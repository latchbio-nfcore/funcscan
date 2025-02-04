from latch.types.metadata import (
    NextflowMetadata,
    LatchAuthor,
    NextflowRuntimeResources,
)
from latch.types.directory import (
    LatchDir,
)

from latch.types.metadata import (
    Fork,
    ForkBranch,
    Params,
    Section,
    Spoiler,
    Text,
)

from .parameters import (
    generated_parameters,
)

flow = [
    Section(
        "Input/Output",
        Params("input", "outdir"),
    ),
    Section(
        "Taxonomic Annotations",
        Params(
            "run_taxa_classification",
            "taxa_classification_tool",
        ),
        Spoiler(
            "MMSeqs Options",
            Params(
                "taxa_classification_mmseqs_db",
                "taxa_classification_mmseqs_db_id",
                "taxa_classification_mmseqs_db_savetmp",
                "taxa_classification_mmseqs_taxonomy_savetmp",
                "taxa_classification_mmseqs_taxonomy_searchtype",
                "taxa_classification_mmseqs_taxonomy_lcaranks",
                "taxa_classification_mmseqs_taxonomy_taxlineage",
                "taxa_classification_mmseqs_taxonomy_sensitivity",
                "taxa_classification_mmseqs_taxonomy_orffilters",
                "taxa_classification_mmseqs_taxonomy_lcamode",
                "taxa_classification_mmseqs_taxonomy_votemode",
            ),
        ),
    ),
    Section(
        "Functional Annotation",
        Params(
            "annotation_tool",
            "save_annotations",
            "run_amp_screening",
            "run_arg_screening",
            "run_bgc_screening",
            "save_db",
        ),
        Spoiler(
            "Bakta",
            Params(
                "annotation_bakta_db",
                "annotation_bakta_db_downloadtype",
                "annotation_bakta_singlemode",
                "annotation_bakta_mincontiglen",
                "annotation_bakta_translationtable",
                "annotation_bakta_gram",
                "annotation_bakta_complete",
                "annotation_bakta_renamecontigheaders",
                "annotation_bakta_compliant",
                "annotation_bakta_trna",
                "annotation_bakta_tmrna",
                "annotation_bakta_rrna",
                "annotation_bakta_ncrna",
                "annotation_bakta_ncrnaregion",
                "annotation_bakta_crispr",
                "annotation_bakta_skipcds",
                "annotation_bakta_pseudo",
                "annotation_bakta_skipsorf",
                "annotation_bakta_gap",
                "annotation_bakta_ori",
                "annotation_bakta_activate_plot",
            ),
        ),
        Spoiler(
            "Prokka",
            Params(
                "annotation_prokka_singlemode",
                "annotation_prokka_rawproduct",
                "annotation_prokka_kingdom",
                "annotation_prokka_gcode",
                "annotation_prokka_mincontiglen",
                "annotation_prokka_evalue",
                "annotation_prokka_coverage",
                "annotation_prokka_cdsrnaolap",
                "annotation_prokka_rnammer",
                "annotation_prokka_compliant",
                "annotation_prokka_addgenes",
                "annotation_prokka_retaincontigheaders",
            ),
        ),
        Spoiler(
            "Prodigal",
            Params(
                "annotation_prodigal_singlemode",
                "annotation_prodigal_closed",
                "annotation_prodigal_transtable",
                "annotation_prodigal_forcenonsd",
            ),
        ),
        Spoiler(
            "Pyrodigal",
            Params(
                "annotation_pyrodigal_singlemode",
                "annotation_pyrodigal_closed",
                "annotation_pyrodigal_transtable",
                "annotation_pyrodigal_forcenonsd",
            ),
        ),
        Spoiler(
            "AMP Options",
            Spoiler(
                "AMP: Amplify",
                Params(
                    "amp_skip_amplify"
                ),
            ),
            Spoiler(
                "AMP: ampir",
                Params(
                    "amp_skip_ampir",
                    "amp_ampir_model",
                    "amp_ampir_minlength",
                ),
            ),
            Spoiler(
                "AMP: hmmsearch",
                Params(
                    "amp_run_hmmsearch",
                    "amp_hmmsearch_models",
                    "amp_hmmsearch_savealignments",
                    "amp_hmmsearch_savetargets",
                    "amp_hmmsearch_savedomains",
                ),
            ),
            Spoiler(
                "AMP: Macrel",
                Params(
                    "amp_skip_macrel"
                ),
            ),
            Spoiler(
                "AMP: ampcombi2 parsetables",
                Params(
                    "amp_ampcombi_db",
                    "amp_ampcombi_parsetables_cutoff",
                    "amp_ampcombi_parsetables_aalength",
                    "amp_ampcombi_parsetables_dbevalue",
                    "amp_ampcombi_parsetables_hmmevalue",
                    "amp_ampcombi_parsetables_windowstopcodon",
                    "amp_ampcombi_parsetables_windowtransport",
                    "amp_ampcombi_parsetables_removehitswostopcodons",
                    "amp_ampcombi_parsetables_ampir",
                    "amp_ampcombi_parsetables_amplify",
                    "amp_ampcombi_parsetables_macrel",
                    "amp_ampcombi_parsetables_hmmsearch",
                ),
            ),
            Spoiler(
                "AMP: ampcombi2 cluster",
                Params(
                    "amp_ampcombi_cluster_covmode",
                    "amp_ampcombi_cluster_sensitivity",
                    "amp_ampcombi_cluster_minmembers",
                    "amp_ampcombi_cluster_mode",
                    "amp_ampcombi_cluster_coverage",
                    "amp_ampcombi_cluster_seqid",
                    "amp_ampcombi_cluster_removesingletons",
                ),
            ),
        ),
        Spoiler(
            "ARG Options",
            Text("ARG: AMRFinderPlus"),
            Params(
                "arg_skip_amrfinderplus",
                "arg_amrfinderplus_db",
                "arg_amrfinderplus_identmin",
                "arg_amrfinderplus_coveragemin",
                "arg_amrfinderplus_translationtable",
                "arg_amrfinderplus_plus",
                "arg_amrfinderplus_name",
            ),
            Text("ARG: DeepARG"),
            Params(
                "arg_skip_deeparg",
                "arg_deeparg_db",
                "arg_deeparg_db_version",
                "arg_deeparg_model",
                "arg_deeparg_minprob",
                "arg_deeparg_alignmentevalue",
                "arg_deeparg_alignmentidentity",
                "arg_deeparg_alignmentoverlap",
                "arg_deeparg_numalignmentsperentry",
            ),
            Text("ARG: fARGene"),
            Params(
                "arg_skip_fargene",
                "arg_fargene_hmmmodel",
                "arg_fargene_savetmpfiles",
                "arg_fargene_score",
                "arg_fargene_minorflength",
                "arg_fargene_orffinder",
                "arg_fargene_translationformat",
            ),
            Text("ARG: RGI"),
            Params(
                "arg_skip_rgi",
                "arg_rgi_db",
                "arg_rgi_savejson",
                "arg_rgi_savetmpfiles",
                "arg_rgi_alignmenttool",
                "arg_rgi_includeloose",
                "arg_rgi_includenudge",
                "arg_rgi_lowquality",
                "arg_rgi_data",
                "arg_rgi_split_prodigal_jobs",
            ),
            Text("ARG: ABRicate"),
            Params(
                "arg_skip_abricate",
                "arg_abricate_db_id",
                "arg_abricate_db",
                "arg_abricate_minid",
                "arg_abricate_mincov",
            ),
            Text("ARG: hAMRonization"),
            Params(
                "arg_hamronization_summarizeformat",
            ),
            Text("ARG: argNorm"),
            Params(
                "arg_skip_argnorm",
            ),
        ),
        Spoiler(
            "BGC Options",
            Params(
                "bgc_mincontiglength",
                "bgc_savefilteredcontigs",
            ),
            Spoiler(
                "AntiSmash Options",
                Params(
                    "bgc_skip_antismash",
                    "bgc_antismash_db",
                    "bgc_antismash_installdir",
                    "bgc_antismash_contigminlength",
                    "bgc_antismash_cbgeneral",
                    "bgc_antismash_cbknownclusters",
                    "bgc_antismash_cbsubclusters",
                    "bgc_antismash_ccmibig",
                    "bgc_antismash_smcogtrees",
                    "bgc_antismash_hmmdetectionstrictness",
                    "bgc_antismash_pfam2go",
                    "bgc_antismash_rre",
                    "bgc_antismash_taxon",
                    "bgc_antismash_tfbs",
                ),
            ),
            Spoiler(
                "DeepBGC Options",
                Params(
                    "bgc_skip_deepbgc",
                    "bgc_deepbgc_db",
                    "bgc_deepbgc_score",
                    "bgc_deepbgc_prodigalsinglemode",
                    "bgc_deepbgc_mergemaxproteingap",
                    "bgc_deepbgc_mergemaxnuclgap",
                    "bgc_deepbgc_minnucl",
                    "bgc_deepbgc_minproteins",
                    "bgc_deepbgc_mindomains",
                    "bgc_deepbgc_minbiodomains",
                    "bgc_deepbgc_classifierscore",
                ),
            ),
            Spoiler(
                "Gecco Options",
                Params(
                    "bgc_skip_gecco",
                    "bgc_gecco_mask",
                    "bgc_gecco_cds",
                    "bgc_gecco_pfilter",
                    "bgc_gecco_threshold",
                    "bgc_gecco_edgedistance",
                ),
            ),
            Spoiler(
                "HMMSearch Options",
                Params(
                    "bgc_run_hmmsearch",
                    "bgc_hmmsearch_models",
                    "bgc_hmmsearch_savealignments",
                    "bgc_hmmsearch_savetargets",
                    "bgc_hmmsearch_savedomains",
                ),
            ),
        ),
        Spoiler(
            "MultiQC Options",
            Params(
                "multiqc_title",
                "multiqc_methods_description",
            ),
        ),
    ),
]
NextflowMetadata(
    display_name="nf-core/funcscan",
    author=LatchAuthor(
        name="Your Name",
    ),
    parameters=generated_parameters,
    runtime_resources=NextflowRuntimeResources(
        cpus=4,
        memory=8,
        storage_gib=100,
    ),
    log_dir=LatchDir(
        "latch:///your_log_dir"
    ),
    flow=flow,
)
