/*
    Run AMP screening tools
*/

include { MACREL_CONTIGS          } from '../../modules/nf-core/modules/macrel/contigs/main'
include { HMMER_HMMSEARCH         } from '../../modules/nf-core/modules/hmmer/hmmsearch/main'
include { AMPLIFY_PREDICT         } from '../../modules/nf-core/modules/amplify/predict/main'

workflow AMP {
    take:
    contigs // tuple val(meta), path(contigs)
    faa     // tuple val(meta), path(PROKKA.out.faa)

    main:
    ch_versions = Channel.empty()
    ch_mqc      = Channel.empty()


    // TODO ampir
    // TODO AMPlify
    if ( !params.amp_skip_amplify_predict ) {
        AMPLIFY_PREDICT ( faa, [] )
        ch_versions = ch_versions.mix(AMPLIFY_PREDICT.out.versions)
    }

    if ( !params.amp_skip_macrel ) {
        MACREL_CONTIGS ( contigs )
        ch_versions = ch_versions.mix(MACREL_CONTIGS.out.versions)
    }

    if ( !params.amp_skip_hmmsearch ) {
        if (params.amp_hmmsearch_models) { ch_amp_hmm_models = Channel.fromPath( params.amp_hmmsearch_models, checkIfExists: true ) } else { exit 1, '[nf-core/funscan] error: hmm model files not found for --amp_hmmsearch_models! Please check input.' }

        ch_amp_hmm_models_meta = ch_amp_hmm_models
            .map {
                file ->
                    def meta  = [:]
                    meta['id'] = file.extension == 'gz' ? file.name - '.hmm.gz' :  file.name - '.hmm'

                [ meta, file ]
            }

        ch_in_for_hmmsearch = faa.combine(ch_amp_hmm_models_meta)
            .map {
                meta_faa, faa, meta_hmm, hmm ->
                    def meta_new = [:]
                    meta_new['id'] = meta_faa['id'] + '_'  + meta_hmm['id']
                // TODO make optional outputs params?
                [ meta_new, hmm, faa, params.amp_hmmsearch_savealignments, params.amp_hmmsearch_savetargets, params.amp_hmmsearch_savedomains ]
            }
            .dump(tag: "input_for_hmmsearch")

        HMMER_HMMSEARCH ( ch_in_for_hmmsearch )


    }

    emit:
    versions = ch_versions
    mqc = ch_mqc

}
