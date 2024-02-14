/*
    Run BGC screening tools
*/

include { UNTAR as UNTAR_CSS                       } from '../../modules/nf-core/untar/main'
include { UNTAR as UNTAR_DETECTION                 } from '../../modules/nf-core/untar/main'
include { UNTAR as UNTAR_MODULES                   } from '../../modules/nf-core/untar/main'
include { ANTISMASH_ANTISMASHLITEDOWNLOADDATABASES } from '../../modules/nf-core/antismash/antismashlitedownloaddatabases/main'
include { ANTISMASH_ANTISMASHLITE as ANTISMASH_GBK } from '../../modules/nf-core/antismash/antismashlite/main'
include { ANTISMASH_ANTISMASHLITE as ANTISMASH_GFF } from '../../modules/nf-core/antismash/antismashlite/main'
include { GECCO_RUN                                } from '../../modules/nf-core/gecco/run/main'
include { HMMER_HMMSEARCH as BGC_HMMER_HMMSEARCH   } from '../../modules/nf-core/hmmer/hmmsearch/main'
include { DEEPBGC_DOWNLOAD                         } from '../../modules/nf-core/deepbgc/download/main'
include { DEEPBGC_PIPELINE                         } from '../../modules/nf-core/deepbgc/pipeline/main'
include { COMBGC                                   } from '../../modules/local/combgc'

workflow BGC {

    take:
    fastas       // tuple val(meta), path(PREPPED_INPUT.out.fna)
    faas         // tuple val(meta), path(<ANNO_TOOL>.out.faa)
    gffs         // tuple val(meta), path(<ANNO_TOOL>.out.gff)
    gbks         // tuple val(meta), path(<ANNO_TOOL>.out.gbk)

    main:
    ch_versions              = Channel.empty()
    ch_bgcresults_for_combgc = Channel.empty()

    // When adding new tool that requires FAA, make sure to update conditions
    // in funcscan.nf around annotation and AMP subworkflow execution
    // to ensure annotation is executed!
    ch_faa_for_bgc_hmmsearch = faas

    // ANTISMASH
    if ( !params.bgc_skip_antismash ) {
        // Check whether user supplies database and/or antismash directory. If not, obtain them via the module antismashlite/antismashlitedownloaddatabases.
        // Important for future maintenance: For CI tests, only the "else" option below is used. Both options should be tested locally whenever the antiSMASH module gets updated.
        if ( params.bgc_antismash_databases && params.bgc_antismash_installationdirectory ) {

            ch_antismash_databases = Channel
                .fromPath( params.bgc_antismash_databases )
                .first()

            ch_antismash_directory = Channel
                .fromPath( params.bgc_antismash_installationdirectory )
                .first()

        } else {

            // May need to update on each new version of antismash-lite due to changes to scripts inside these tars
            ch_css_for_antismash = "https://github.com/nf-core/test-datasets/raw/91bb8781c576967e23d2c5315dd4d43213575033/data/delete_me/antismash/css.tar.gz"
            ch_detection_for_antismash = "https://github.com/nf-core/test-datasets/raw/91bb8781c576967e23d2c5315dd4d43213575033/data/delete_me/antismash/detection.tar.gz"
            ch_modules_for_antismash = "https://github.com/nf-core/test-datasets/raw/91bb8781c576967e23d2c5315dd4d43213575033/data/delete_me/antismash/modules.tar.gz"

            UNTAR_CSS ( [ [], ch_css_for_antismash ] )
            ch_versions = ch_versions.mix(UNTAR_CSS.out.versions)

            UNTAR_DETECTION ( [ [], ch_detection_for_antismash ] )
            ch_versions = ch_versions.mix(UNTAR_DETECTION.out.versions)

            UNTAR_MODULES ( [ [], ch_modules_for_antismash ] )
            ch_versions = ch_versions.mix(UNTAR_MODULES.out.versions)

            ANTISMASH_ANTISMASHLITEDOWNLOADDATABASES ( UNTAR_CSS.out.untar.map{ it[1] }, UNTAR_DETECTION.out.untar.map{ it[1] }, UNTAR_MODULES.out.untar.map{ it[1] } )
            ch_versions = ch_versions.mix(ANTISMASH_ANTISMASHLITEDOWNLOADDATABASES.out.versions)
            ch_antismash_databases = ANTISMASH_ANTISMASHLITEDOWNLOADDATABASES.out.database

            ch_antismash_directory = ANTISMASH_ANTISMASHLITEDOWNLOADDATABASES.out.antismash_dir

        }

        // Exact input combination to antismash depends on whether gff (requires fna) or gbk (just gbk) necessary

            ch_antismash_gff_input = fastas.join(gffs, by: 0)
                                    .filter {
                                        meta, fastas, gff ->
                                            if ( meta.longest_contig < params.bgc_antismash_sampleminlength ) log.warn "[nf-core/funcscan] Sample does not have any contig reaching min. length threshold of --bgc_antismash_sampleminlength ${params.bgc_antismash_sampleminlength}. Antismash will not be run for sample: ${meta.id}."
                                            meta.longest_contig >= params.bgc_antismash_sampleminlength
                                    }
                                    .multiMap {
                                        meta, fastas, gff ->
                                        fastas: [ meta, fastas ]
                                        gffs: [ gff ]
                                    }

            ANTISMASH_GFF ( ch_antismash_gff_input.fastas, ch_antismash_databases, ch_antismash_directory, ch_antismash_gff_input.gffs )
            ch_versions = ch_versions.mix(ANTISMASH_GFF.out.versions)

            ch_antismash_gbk_input = gbks.filter {
                                        meta, files ->
                                            if ( meta.longest_contig < params.bgc_antismash_sampleminlength ) log.warn "[nf-core/funcscan] Sample does not have any contig reaching min. length threshold of --bgc_antismash_sampleminlength ${params.bgc_antismash_sampleminlength}. Antismash will not be run for sample: ${meta.id}."
                                            meta.longest_contig >= params.bgc_antismash_sampleminlength
                                    }

            ANTISMASH_GBK ( ch_antismash_gbk_input, ch_antismash_databases, ch_antismash_directory, [] )
            ch_versions = ch_versions.mix(ANTISMASH_GBK.out.versions)

        ch_antismashresults_for_combgc = ANTISMASH_GFF.out.knownclusterblast_dir.dump(tag: 'gff_cluster')
                                            .dump(tag: 'antismash_gff_knownclusterblast_dir')
                                            .mix(ANTISMASH_GFF.out.gbk_input.dump(tag: 'gff_input'))
                                            .dump(tag: 'antismash_gff_gbk_input')
                                            .mix(ANTISMASH_GBK.out.knownclusterblast_dir.dump(tag: 'gbk_cluster'))
                                            .dump(tag: 'antismash_gbk_knownclusterblast_dir')
                                            .mix(ANTISMASH_GBK.out.gbk_input.dump(tag: 'gbk_input'))
                                            .dump(tag: 'antismash_gbk_gbk_input')
                                            .groupTuple()
                                            .map{
                                                meta, files ->
                                                [meta, files.flatten()]
                                            }
        ch_bgcresults_for_combgc = ch_bgcresults_for_combgc.mix(ch_antismashresults_for_combgc)
    }

    // DEEPBGC
    if ( !params.bgc_skip_deepbgc ) {
        if ( params.bgc_deepbgc_database ) {

            ch_deepbgc_database = Channel
                .fromPath( params.bgc_deepbgc_database )
                .first()
        } else {
            DEEPBGC_DOWNLOAD()
            ch_deepbgc_database = DEEPBGC_DOWNLOAD.out.db
            ch_versions = ch_versions.mix(DEEPBGC_DOWNLOAD.out.versions)
        }

        DEEPBGC_PIPELINE ( fastas, ch_deepbgc_database)
        ch_versions = ch_versions.mix(DEEPBGC_PIPELINE.out.versions)
        ch_bgcresults_for_combgc = ch_bgcresults_for_combgc.mix(DEEPBGC_PIPELINE.out.bgc_tsv)
    }

    // GECCO
    if ( !params.bgc_skip_gecco ) {
        ch_gecco_input = fastas.groupTuple()
                            .multiMap {
                                fna: [ it[0], it[1], [] ]
                            }

        GECCO_RUN ( ch_gecco_input, [] )
        ch_versions = ch_versions.mix(GECCO_RUN.out.versions)
        ch_geccoresults_for_combgc = GECCO_RUN.out.gbk
            .mix(GECCO_RUN.out.clusters)
            .groupTuple()
            .map{
                meta, files ->
                [meta, files.flatten()]
            }
        ch_bgcresults_for_combgc = ch_bgcresults_for_combgc.mix(ch_geccoresults_for_combgc)
    }

    // HMMSEARCH
    if ( !params.bgc_skip_hmmsearch ) {
        if ( params.bgc_hmmsearch_models ) { ch_bgc_hmm_models = Channel.fromPath( params.bgc_hmmsearch_models, checkIfExists: true ) } else { error('[nf-core/funcscan] error: hmm model files not found for --bgc_hmmsearch_models! Please check input.') }

        ch_bgc_hmm_models_meta = ch_bgc_hmm_models
            .map {
                file ->
                    def meta  = [:]
                    meta['id'] = file.extension == 'gz' ? file.name - '.hmm.gz' :  file.name - '.hmm'

                [ meta, file ]
            }

        ch_in_for_bgc_hmmsearch = ch_faa_for_bgc_hmmsearch.combine(ch_bgc_hmm_models_meta)
            .map {
                meta_faa, faa, meta_hmm, hmm ->
                    def meta_new = [:]
                    meta_new['id']     = meta_faa['id']
                    meta_new['hmm_id'] = meta_hmm['id']
                [ meta_new, hmm, faa, params.bgc_hmmsearch_savealignments, params.bgc_hmmsearch_savetargets, params.bgc_hmmsearch_savedomains ]
            }

        BGC_HMMER_HMMSEARCH ( ch_in_for_bgc_hmmsearch )
        ch_versions = ch_versions.mix(BGC_HMMER_HMMSEARCH.out.versions)
    }

    // COMBGC
    COMBGC ( ch_bgcresults_for_combgc )

    ch_combgc_summaries = COMBGC.out.tsv.map{ it[1] }.collectFile(name: 'combgc_complete_summary.tsv', storeDir: "${params.outdir}/reports/combgc", keepHeader:true)

    emit:
    versions = ch_versions
}
