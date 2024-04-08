/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { paramsSummaryMultiqc   } from '../subworkflows/nf-core/utils_nfcore_pipeline'
include { softwareVersionsToYAML } from '../subworkflows/nf-core/utils_nfcore_pipeline'
include { methodsDescriptionText } from '../subworkflows/local/utils_nfcore_funcscan_pipeline'
include { paramsSummaryMap; validateParameters; paramsHelp; paramsSummaryLog; fromSamplesheet } from 'plugin/nf-validation'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CONFIG FILES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

ch_multiqc_config                     = Channel.fromPath( "$projectDir/assets/multiqc_config.yml", checkIfExists: true )
ch_multiqc_custom_config              = params.multiqc_config ? Channel.fromPath( params.multiqc_config, checkIfExists: true ) : Channel.empty()
ch_multiqc_logo                       = params.multiqc_logo   ? Channel.fromPath( params.multiqc_logo, checkIfExists: true ) : Channel.empty()
ch_multiqc_custom_methods_description = params.multiqc_methods_description ? file(params.multiqc_methods_description, checkIfExists: true) : file("$projectDir/assets/methods_description_template.yml", checkIfExists: true)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT LOCAL MODULES/SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// SUBWORKFLOW: Consisting of a mix of local and nf-core/modules
//
include { ANNOTATION } from '../subworkflows/local/annotation'
include { AMP        } from '../subworkflows/local/amp'
include { ARG        } from '../subworkflows/local/arg'
include { BGC        } from '../subworkflows/local/bgc'
include { TAXA_CLASS } from '../subworkflows/local/taxa_class'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT NF-CORE MODULES/SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// MODULE: Installed directly from nf-core/modules
//

include { BIOAWK                      } from '../modules/nf-core/bioawk/main'
include { GUNZIP as GUNZIP_INPUT_PREP } from '../modules/nf-core/gunzip/main'
include { MULTIQC                     } from '../modules/nf-core/multiqc/main'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow FUNCSCAN {

    take:
    ch_samplesheet // channel: samplesheet read in from --input

    main:

    ch_versions = Channel.empty()
    ch_multiqc_files = Channel.empty()

    ch_input = Channel.fromSamplesheet("input")

    ///////////////////////
    // INPUT PREPARATION //
    ///////////////////////

    // Some tools require uncompressed input
    ch_input_prep = ch_input
                        .map{meta, fasta, faa, feature -> [meta, [fasta, faa, feature]]}
                        .transpose()
                        .branch {
                            compressed: it[1].toString().endsWith('.gz')
                            uncompressed: it[1]
                        }

    GUNZIP_INPUT_PREP ( ch_input_prep.compressed )
    ch_versions = ch_versions.mix( GUNZIP_INPUT_PREP.out.versions )

    // Merge all the already uncompressed and newly compressed FASTAs here into
    // a single input channel for downstream
    ch_intermediate_input = GUNZIP_INPUT_PREP.out.gunzip
                            .mix( ch_input_prep.uncompressed )
                            .groupTuple()
                            .map{
                                meta, files ->
                                    def fasta_found   = files.find{it.toString().tokenize('.').last().matches('fasta|fas|fna|fa')}
                                    def faa_found     = files.find{it.toString().endsWith('.faa')}
                                    def feature_found = files.find{it.toString().tokenize('.').last().matches('gbk')}
                                    def fasta         = fasta_found   != null ? fasta_found   : []
                                    def faa           = faa_found     != null ? faa_found     : []
                                    def feature       = feature_found != null ? feature_found : []

                                    [meta, fasta, faa, feature]
                            }
                            .multiMap {
                                meta, fasta, faa, feature ->
                                    fastas: [ meta, fasta ]
                                    annotations : [ meta, faa, feature ]
                            }

    // Add to meta the length of longest contig for downstream filtering
    ch_intermediate_input.fastas
    ch_intermediate_input.annotations

    BIOAWK ( ch_intermediate_input.fastas )
    ch_versions = ch_versions.mix( BIOAWK.out.versions )

    ch_intermediate_input = ch_intermediate_input.fastas
                                .join( BIOAWK.out.longest )
                                .join( ch_intermediate_input.annotations )
                                .map{
                                    meta, fasta, length, faa, feature ->
                                        def meta_new = [:]
                                        meta_new['longest_contig'] = Integer.parseInt(length)
                                    [ meta + meta_new, fasta, faa, feature ]
                                }

    // Separate pre-annotated FASTAs from those that need annotation
    ch_input_for_annotation = ch_intermediate_input
                                .branch {
                                    meta, fasta, protein, feature ->
                                        preannotated: protein != []
                                        unannotated: true
                                }

    /*
        ANNOTATION
    */

    // Some tools require annotated FASTAs
    if ( ( params.run_arg_screening && !params.arg_skip_deeparg ) || ( params.run_amp_screening && ( !params.amp_skip_hmmsearch || !params.amp_skip_amplify || !params.amp_skip_ampir ) ) || ( params.run_bgc_screening && ( !params.bgc_skip_hmmsearch || !params.bgc_skip_antismash ) ) ) {

        ch_unannotated_for_annotation = ch_input_for_annotation.unannotated
                                            .map{
                                                meta, fasta, protein, feature ->
                                                [meta, fasta]
                                            }

        ANNOTATION( ch_unannotated_for_annotation )
        ch_versions = ch_versions.mix( ANNOTATION.out.versions )
        ch_multiqc_files = ch_multiqc_files.mix( ANNOTATION.out.multiqc_files )

        ch_new_annotation = ch_unannotated_for_annotation
                                .join( ANNOTATION.out.faa )
                                .join( ANNOTATION.out.gbk )

    } else {
        ch_new_annotation = Channel.empty()
    }

    ch_prepped_input = ch_input_for_annotation.preannotated
                        .map{
                            meta, fasta, protein, feature ->
                                def gbk = feature.extension == 'gbk' ? feature : []
                            [meta, fasta, protein, gbk]
                        }
                        .mix( ch_new_annotation )
                        .multiMap {
                            meta, fasta, protein, gbk ->
                            fastas: [meta, fasta]
                            faas: [meta, protein]
                            gbks: [meta, gbk]
                        }


    /*
        TAXONOMIC CLASSIFICATION
    */

    // The final subworkflow reports need taxonomic classification.
    // This can be either on NT or AA level depending on annotation.
    // TODO: Only NT at the moment. AA tax. classification will be added only when its PR is merged.
    if ( params.run_taxa_classification ) {
            TAXA_CLASS ( ch_prepped_input.fastas )
            ch_versions     = ch_versions.mix( TAXA_CLASS.out.versions )
            ch_taxonomy_tsv = TAXA_CLASS.out.sample_taxonomy

    } else {
            ch_mmseqs_db              = Channel.empty()
            ch_taxonomy_querydb       = Channel.empty()
            ch_taxonomy_querydb_taxdb = Channel.empty()
            ch_taxonomy_tsv           = Channel.empty()
    }

    ///////////////
    // SCREENING //
    ///////////////

    /*
        AMPs
    */
    if ( params.run_amp_screening && !params.run_taxa_classification ) {
        AMP (
            ch_prepped_input.fastas,
            ch_prepped_input.faas
                .filter {
                    meta, file ->
                        if ( file != [] && file.isEmpty() ) log.warn("[nf-core/funcscan] Annotation of following sample produced produced an empty FAA file. AMP screening tools requiring this file will not be executed: ${meta.id}")
                        !file.isEmpty()

                },
            ch_taxonomy_tsv
        )
        ch_versions = ch_versions.mix(AMP.out.versions)
    } else if ( params.run_amp_screening && params.run_taxa_classification ) {
        AMP (
            ch_prepped_input.fastas,
            ch_prepped_input.faas
                .filter {
                    meta, file ->
                        if ( file != [] && file.isEmpty() ) log.warn("[nf-core/funcscan] Annotation of following sample produced produced an empty FAA file. AMP screening tools requiring this file will not be executed: ${meta.id}")
                        !file.isEmpty()
                    },
            ch_taxonomy_tsv
                .filter {
                        meta, file ->
                        if ( file != [] && file.isEmpty() ) log.warn("[nf-core/funcscan] Taxonomy classification of the following sample produced an empty TSV file. Taxonomy merging will not be executed: ${meta.id}")
                        !file.isEmpty()
                    }
        )
        ch_versions = ch_versions.mix( AMP.out.versions )
    }

    /*
        ARGs
    */
    if ( params.run_arg_screening && !params.run_taxa_classification ) {
        if ( params.arg_skip_deeparg ) {
            ARG (
                ch_prepped_input.fastas,
                [],
                ch_taxonomy_tsv
                )
        } else {
            ARG (
                ch_prepped_input.fastas,
                ch_prepped_input.faas
                    .filter {
                        meta, file ->
                        if ( file != [] && file.isEmpty() ) log.warn("[nf-core/funcscan] Annotation of following sample produced produced an empty FAA file. ARG screening tools requiring this file will not be executed: ${meta.id}")
                            !file.isEmpty()
                    },
                ch_taxonomy_tsv
            )
        }
        ch_versions = ch_versions.mix( ARG.out.versions )
    } else if ( params.run_arg_screening && params.run_taxa_classification ) {
        if ( params.arg_skip_deeparg ) {
            ARG (
                ch_prepped_input.fastas,
                [],
                ch_taxonomy_tsv
                    .filter {
                        meta, file ->
                        if ( file.isEmpty() ) log.warn("[nf-core/funcscan] Taxonomy classification of the following sample produced an empty TSV file. Taxonomy merging will not be executed: ${meta.id}")
                        !file.isEmpty()
                    }
                )
        } else {
            ARG (
                ch_prepped_input.fastas,
                ch_prepped_input.faas
                    .filter {
                        meta, file ->
                        if ( file.isEmpty() ) log.warn("[nf-core/funcscan] Annotation of following sample produced produced an empty FAA file. ARG screening tools requiring this file will not be executed: ${meta.id}")
                            !file.isEmpty()
                    },
                ch_taxonomy_tsv
                    .filter {
                        meta, file ->
                        if ( file.isEmpty() ) log.warn("[nf-core/funcscan] Taxonomy classification of the following sample produced an empty TSV file. Taxonomy merging will not be executed: ${meta.id}")
                        !file.isEmpty()
                }
            )
        }
        ch_versions = ch_versions.mix( ARG.out.versions )
    }

    /*
        BGCs
    */
    if ( params.run_bgc_screening && !params.run_taxa_classification ) {
        BGC (
            ch_prepped_input.fastas,
            ch_prepped_input.faas
                .filter {
                    meta, file ->
                        if ( file.isEmpty() ) log.warn("[nf-core/funcscan] Annotation of following sample produced produced an empty FAA file. BGC screening tools requiring this file will not be executed: ${meta.id}")
                        !file.isEmpty()
                },
            ch_prepped_input.gbks
                .filter {
                    meta, file ->
                        if ( file.isEmpty() ) log.warn("[nf-core/funcscan] Annotation of following sample produced produced an empty GBK file. BGC screening tools requiring this file will not be executed: ${meta.id}")
                        !file.isEmpty()
                },
            ch_taxonomy_tsv
        )
        ch_versions = ch_versions.mix( BGC.out.versions )
    } else if ( params.run_bgc_screening && params.run_taxa_classification ) {
        BGC (
            ch_prepped_input.fastas,
            ch_prepped_input.faas
                .filter {
                    meta, file ->
                        if ( file != [] && file.isEmpty() ) log.warn("[nf-core/funcscan] Annotation of following sample produced produced an empty FAA file. BGC screening tools requiring this file will not be executed: ${meta.id}")
                        !file.isEmpty()
                },
            ch_prepped_input.gbks
                .filter {
                    meta, file ->
                        if ( file != [] && file.isEmpty() ) log.warn("[nf-core/funcscan] Annotation of following sample produced an empty GBK file. BGC screening tools requiring this file will not be executed: ${meta.id}")
                        !file.isEmpty()
                },
            ch_taxonomy_tsv
                    .filter {
                        meta, file ->
                        if ( file.isEmpty() ) log.warn("[nf-core/funcscan] Taxonomy classification of the following sample produced an empty TSV file. Taxonomy merging will not be executed: ${meta.id}")
                        !file.isEmpty()
                }
        )
        ch_versions = ch_versions.mix( BGC.out.versions )
    }

    //
    // Collate and save software versions
    //
    softwareVersionsToYAML( ch_versions )
        .collectFile( storeDir: "${params.outdir}/pipeline_info", name: 'nf_core_pipeline_software_mqc_versions.yml', sort: true, newLine: true )
        .set { ch_collated_versions }

    //
    // MODULE: MultiQC
    //

    ch_multiqc_config                     = Channel.fromPath( "$projectDir/assets/multiqc_config.yml", checkIfExists: true )
    ch_multiqc_custom_config              = params.multiqc_config ? Channel.fromPath( params.multiqc_config, checkIfExists: true ) : Channel.empty()
    ch_multiqc_logo                       = params.multiqc_logo ? Channel.fromPath( params.multiqc_logo, checkIfExists: true ) : Channel.empty()
    summary_params                        = paramsSummaryMap( workflow, parameters_schema: "nextflow_schema.json" )
    ch_workflow_summary                   = Channel.value( paramsSummaryMultiqc( summary_params ) )
    ch_multiqc_custom_methods_description = params.multiqc_methods_description ? file(params.multiqc_methods_description, checkIfExists: true) : file("$projectDir/assets/methods_description_template.yml", checkIfExists: true)
    ch_methods_description                = Channel.value( methodsDescriptionText( ch_multiqc_custom_methods_description ))
    ch_multiqc_files                      = ch_multiqc_files.mix( ch_workflow_summary.collectFile(name: 'workflow_summary_mqc.yaml') )
    ch_multiqc_files                      = ch_multiqc_files.mix( ch_collated_versions )
    ch_multiqc_files                      = ch_multiqc_files.mix( ch_methods_description.collectFile(name: 'methods_description_mqc.yaml') )

    MULTIQC (
        ch_multiqc_files.collect(),
        ch_multiqc_config.toList(),
        ch_multiqc_custom_config.toList(),
        ch_multiqc_logo.toList()
    )

    emit:
    multiqc_report = MULTIQC.out.report.toList() // channel: /path/to/multiqc_report.html
    versions       = ch_versions                 // channel: [ path(versions.yml) ]
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
