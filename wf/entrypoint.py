from dataclasses import dataclass
from enum import Enum
import os
import subprocess
import requests
import shutil
from pathlib import Path
import typing
import typing_extensions

from latch.resources.workflow import workflow
from latch.resources.tasks import nextflow_runtime_task, custom_task
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir
from latch.ldata.path import LPath
from latch_cli.nextflow.workflow import get_flag
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.utils import urljoins
from latch.types import metadata
from flytekit.core.annotation import FlyteAnnotation

from latch_cli.services.register.utils import import_module_by_path

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)
import latch_metadata

@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize() -> str:
    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage",
        headers=headers,
        json={
            "storage_gib": 100,
        }
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]






@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(pvc_name: str, input: LatchFile, outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], run_amp_screening: typing.Optional[bool], run_arg_screening: typing.Optional[bool], run_bgc_screening: typing.Optional[bool], save_annotations: typing.Optional[bool], annotation_bakta_db_localpath: typing.Optional[str], annotation_bakta_db_downloadtype: typing.Optional[str], annotation_bakta_complete: typing.Optional[bool], annotation_bakta_renamecontigheaders: typing.Optional[bool], annotation_bakta_compliant: typing.Optional[bool], annotation_bakta_trna: typing.Optional[bool], annotation_bakta_tmrna: typing.Optional[bool], annotation_bakta_rrna: typing.Optional[bool], annotation_bakta_ncrna: typing.Optional[bool], annotation_bakta_ncrnaregion: typing.Optional[bool], annotation_bakta_crispr: typing.Optional[bool], annotation_bakta_skipcds: typing.Optional[bool], annotation_bakta_pseudo: typing.Optional[bool], annotation_bakta_skipsorf: typing.Optional[bool], annotation_bakta_gap: typing.Optional[bool], annotation_bakta_ori: typing.Optional[bool], annotation_bakta_activate_plot: typing.Optional[bool], annotation_prokka_singlemode: typing.Optional[bool], annotation_prokka_rawproduct: typing.Optional[bool], annotation_prokka_cdsrnaolap: typing.Optional[bool], annotation_prokka_rnammer: typing.Optional[bool], annotation_prokka_compliant: typing.Optional[bool], annotation_prokka_addgenes: typing.Optional[bool], annotation_prokka_retaincontigheaders: typing.Optional[bool], annotation_prodigal_singlemode: typing.Optional[bool], annotation_prodigal_closed: typing.Optional[bool], annotation_prodigal_forcenonsd: typing.Optional[bool], annotation_pyrodigal_singlemode: typing.Optional[bool], annotation_pyrodigal_closed: typing.Optional[bool], annotation_pyrodigal_forcenonsd: typing.Optional[bool], save_databases: typing.Optional[bool], amp_skip_amplify: typing.Optional[bool], amp_skip_ampir: typing.Optional[bool], amp_skip_hmmsearch: typing.Optional[bool], amp_hmmsearch_models: typing.Optional[str], amp_hmmsearch_savealignments: typing.Optional[bool], amp_hmmsearch_savetargets: typing.Optional[bool], amp_hmmsearch_savedomains: typing.Optional[bool], amp_skip_macrel: typing.Optional[bool], amp_ampcombi_db: typing.Optional[str], arg_skip_amrfinderplus: typing.Optional[bool], arg_amrfinderplus_db: typing.Optional[str], arg_amrfinderplus_plus: typing.Optional[bool], arg_amrfinderplus_name: typing.Optional[bool], arg_skip_deeparg: typing.Optional[bool], arg_deeparg_data: typing.Optional[str], arg_skip_fargene: typing.Optional[bool], arg_fargene_savetmpfiles: typing.Optional[bool], arg_fargene_score: typing.Optional[float], arg_fargene_orffinder: typing.Optional[bool], arg_skip_rgi: typing.Optional[bool], arg_rgi_savejson: typing.Optional[bool], arg_rgi_savetmpfiles: typing.Optional[bool], arg_rgi_lowquality: typing.Optional[bool], arg_skip_abricate: typing.Optional[bool], bgc_skip_antismash: typing.Optional[bool], bgc_antismash_databases: typing.Optional[str], bgc_antismash_installationdirectory: typing.Optional[str], bgc_antismash_cbgeneral: typing.Optional[bool], bgc_antismash_cbknownclusters: typing.Optional[bool], bgc_antismash_cbsubclusters: typing.Optional[bool], bgc_antismash_ccmibig: typing.Optional[bool], bgc_antismash_smcogtrees: typing.Optional[bool], bgc_skip_deepbgc: typing.Optional[bool], bgc_deepbgc_database: typing.Optional[str], bgc_deepbgc_prodigalsinglemode: typing.Optional[bool], bgc_skip_gecco: typing.Optional[bool], bgc_gecco_mask: typing.Optional[bool], bgc_skip_hmmsearch: typing.Optional[bool], bgc_hmmsearch_models: typing.Optional[str], bgc_hmmsearch_savealignments: typing.Optional[bool], bgc_hmmsearch_savetargets: typing.Optional[bool], bgc_hmmsearch_savedomains: typing.Optional[bool], multiqc_methods_description: typing.Optional[str], annotation_tool: typing.Optional[str], annotation_bakta_mincontiglen: typing.Optional[int], annotation_bakta_translationtable: typing.Optional[int], annotation_bakta_gram: typing.Optional[str], annotation_prokka_kingdom: typing.Optional[str], annotation_prokka_gcode: typing.Optional[int], annotation_prokka_mincontiglen: typing.Optional[int], annotation_prokka_evalue: typing.Optional[float], annotation_prokka_coverage: typing.Optional[int], annotation_prodigal_transtable: typing.Optional[int], annotation_pyrodigal_transtable: typing.Optional[int], amp_ampir_model: typing.Optional[str], amp_ampir_minlength: typing.Optional[int], amp_ampcombi_cutoff: typing.Optional[float], arg_amrfinderplus_identmin: typing.Optional[float], arg_amrfinderplus_coveragemin: typing.Optional[float], arg_amrfinderplus_translationtable: typing.Optional[int], arg_deeparg_data_version: typing.Optional[int], arg_deeparg_model: typing.Optional[str], arg_deeparg_minprob: typing.Optional[float], arg_deeparg_alignmentevalue: typing.Optional[float], arg_deeparg_alignmentidentity: typing.Optional[int], arg_deeparg_alignmentoverlap: typing.Optional[float], arg_deeparg_numalignmentsperentry: typing.Optional[int], arg_fargene_hmmmodel: typing.Optional[str], arg_fargene_minorflength: typing.Optional[int], arg_fargene_translationformat: typing.Optional[str], arg_rgi_alignmenttool: typing.Optional[str], arg_rgi_includeloose: typing.Optional[bool], arg_rgi_excludenudge: typing.Optional[bool], arg_rgi_data: typing.Optional[str], arg_abricate_db: typing.Optional[str], arg_abricate_minid: typing.Optional[int], arg_abricate_mincov: typing.Optional[int], bgc_antismash_sampleminlength: typing.Optional[int], bgc_antismash_contigminlength: typing.Optional[int], bgc_antismash_hmmdetectionstrictness: typing.Optional[str], bgc_antismash_taxon: typing.Optional[str], bgc_deepbgc_score: typing.Optional[float], bgc_deepbgc_mergemaxproteingap: typing.Optional[int], bgc_deepbgc_mergemaxnuclgap: typing.Optional[int], bgc_deepbgc_minnucl: typing.Optional[int], bgc_deepbgc_minproteins: typing.Optional[int], bgc_deepbgc_mindomains: typing.Optional[int], bgc_deepbgc_minbiodomains: typing.Optional[int], bgc_deepbgc_classifierscore: typing.Optional[float], bgc_gecco_cds: typing.Optional[int], bgc_gecco_pfilter: typing.Optional[float], bgc_gecco_threshold: typing.Optional[float], bgc_gecco_edgedistance: typing.Optional[int], arg_hamronization_summarizeformat: typing.Optional[str]) -> None:
    try:
        shared_dir = Path("/nf-workdir")



        ignore_list = [
            "latch",
            ".latch",
            "nextflow",
            ".nextflow",
            "work",
            "results",
            "miniconda",
            "anaconda3",
            "mambaforge",
        ]

        shutil.copytree(
            Path("/root"),
            shared_dir,
            ignore=lambda src, names: ignore_list,
            ignore_dangling_symlinks=True,
            dirs_exist_ok=True,
        )

        cmd = [
            "/root/nextflow",
            "run",
            str(shared_dir / "main.nf"),
            "-work-dir",
            str(shared_dir),
            "-profile",
            "docker",
            "-c",
            "latch.config",
                *get_flag('input', input),
                *get_flag('outdir', outdir),
                *get_flag('email', email),
                *get_flag('multiqc_title', multiqc_title),
                *get_flag('run_amp_screening', run_amp_screening),
                *get_flag('run_arg_screening', run_arg_screening),
                *get_flag('run_bgc_screening', run_bgc_screening),
                *get_flag('annotation_tool', annotation_tool),
                *get_flag('save_annotations', save_annotations),
                *get_flag('annotation_bakta_db_localpath', annotation_bakta_db_localpath),
                *get_flag('annotation_bakta_db_downloadtype', annotation_bakta_db_downloadtype),
                *get_flag('annotation_bakta_mincontiglen', annotation_bakta_mincontiglen),
                *get_flag('annotation_bakta_translationtable', annotation_bakta_translationtable),
                *get_flag('annotation_bakta_gram', annotation_bakta_gram),
                *get_flag('annotation_bakta_complete', annotation_bakta_complete),
                *get_flag('annotation_bakta_renamecontigheaders', annotation_bakta_renamecontigheaders),
                *get_flag('annotation_bakta_compliant', annotation_bakta_compliant),
                *get_flag('annotation_bakta_trna', annotation_bakta_trna),
                *get_flag('annotation_bakta_tmrna', annotation_bakta_tmrna),
                *get_flag('annotation_bakta_rrna', annotation_bakta_rrna),
                *get_flag('annotation_bakta_ncrna', annotation_bakta_ncrna),
                *get_flag('annotation_bakta_ncrnaregion', annotation_bakta_ncrnaregion),
                *get_flag('annotation_bakta_crispr', annotation_bakta_crispr),
                *get_flag('annotation_bakta_skipcds', annotation_bakta_skipcds),
                *get_flag('annotation_bakta_pseudo', annotation_bakta_pseudo),
                *get_flag('annotation_bakta_skipsorf', annotation_bakta_skipsorf),
                *get_flag('annotation_bakta_gap', annotation_bakta_gap),
                *get_flag('annotation_bakta_ori', annotation_bakta_ori),
                *get_flag('annotation_bakta_activate_plot', annotation_bakta_activate_plot),
                *get_flag('annotation_prokka_singlemode', annotation_prokka_singlemode),
                *get_flag('annotation_prokka_rawproduct', annotation_prokka_rawproduct),
                *get_flag('annotation_prokka_kingdom', annotation_prokka_kingdom),
                *get_flag('annotation_prokka_gcode', annotation_prokka_gcode),
                *get_flag('annotation_prokka_mincontiglen', annotation_prokka_mincontiglen),
                *get_flag('annotation_prokka_evalue', annotation_prokka_evalue),
                *get_flag('annotation_prokka_coverage', annotation_prokka_coverage),
                *get_flag('annotation_prokka_cdsrnaolap', annotation_prokka_cdsrnaolap),
                *get_flag('annotation_prokka_rnammer', annotation_prokka_rnammer),
                *get_flag('annotation_prokka_compliant', annotation_prokka_compliant),
                *get_flag('annotation_prokka_addgenes', annotation_prokka_addgenes),
                *get_flag('annotation_prokka_retaincontigheaders', annotation_prokka_retaincontigheaders),
                *get_flag('annotation_prodigal_singlemode', annotation_prodigal_singlemode),
                *get_flag('annotation_prodigal_closed', annotation_prodigal_closed),
                *get_flag('annotation_prodigal_transtable', annotation_prodigal_transtable),
                *get_flag('annotation_prodigal_forcenonsd', annotation_prodigal_forcenonsd),
                *get_flag('annotation_pyrodigal_singlemode', annotation_pyrodigal_singlemode),
                *get_flag('annotation_pyrodigal_closed', annotation_pyrodigal_closed),
                *get_flag('annotation_pyrodigal_transtable', annotation_pyrodigal_transtable),
                *get_flag('annotation_pyrodigal_forcenonsd', annotation_pyrodigal_forcenonsd),
                *get_flag('save_databases', save_databases),
                *get_flag('amp_skip_amplify', amp_skip_amplify),
                *get_flag('amp_skip_ampir', amp_skip_ampir),
                *get_flag('amp_ampir_model', amp_ampir_model),
                *get_flag('amp_ampir_minlength', amp_ampir_minlength),
                *get_flag('amp_skip_hmmsearch', amp_skip_hmmsearch),
                *get_flag('amp_hmmsearch_models', amp_hmmsearch_models),
                *get_flag('amp_hmmsearch_savealignments', amp_hmmsearch_savealignments),
                *get_flag('amp_hmmsearch_savetargets', amp_hmmsearch_savetargets),
                *get_flag('amp_hmmsearch_savedomains', amp_hmmsearch_savedomains),
                *get_flag('amp_skip_macrel', amp_skip_macrel),
                *get_flag('amp_ampcombi_db', amp_ampcombi_db),
                *get_flag('amp_ampcombi_cutoff', amp_ampcombi_cutoff),
                *get_flag('arg_skip_amrfinderplus', arg_skip_amrfinderplus),
                *get_flag('arg_amrfinderplus_db', arg_amrfinderplus_db),
                *get_flag('arg_amrfinderplus_identmin', arg_amrfinderplus_identmin),
                *get_flag('arg_amrfinderplus_coveragemin', arg_amrfinderplus_coveragemin),
                *get_flag('arg_amrfinderplus_translationtable', arg_amrfinderplus_translationtable),
                *get_flag('arg_amrfinderplus_plus', arg_amrfinderplus_plus),
                *get_flag('arg_amrfinderplus_name', arg_amrfinderplus_name),
                *get_flag('arg_skip_deeparg', arg_skip_deeparg),
                *get_flag('arg_deeparg_data', arg_deeparg_data),
                *get_flag('arg_deeparg_data_version', arg_deeparg_data_version),
                *get_flag('arg_deeparg_model', arg_deeparg_model),
                *get_flag('arg_deeparg_minprob', arg_deeparg_minprob),
                *get_flag('arg_deeparg_alignmentevalue', arg_deeparg_alignmentevalue),
                *get_flag('arg_deeparg_alignmentidentity', arg_deeparg_alignmentidentity),
                *get_flag('arg_deeparg_alignmentoverlap', arg_deeparg_alignmentoverlap),
                *get_flag('arg_deeparg_numalignmentsperentry', arg_deeparg_numalignmentsperentry),
                *get_flag('arg_skip_fargene', arg_skip_fargene),
                *get_flag('arg_fargene_hmmmodel', arg_fargene_hmmmodel),
                *get_flag('arg_fargene_savetmpfiles', arg_fargene_savetmpfiles),
                *get_flag('arg_fargene_score', arg_fargene_score),
                *get_flag('arg_fargene_minorflength', arg_fargene_minorflength),
                *get_flag('arg_fargene_orffinder', arg_fargene_orffinder),
                *get_flag('arg_fargene_translationformat', arg_fargene_translationformat),
                *get_flag('arg_skip_rgi', arg_skip_rgi),
                *get_flag('arg_rgi_savejson', arg_rgi_savejson),
                *get_flag('arg_rgi_savetmpfiles', arg_rgi_savetmpfiles),
                *get_flag('arg_rgi_alignmenttool', arg_rgi_alignmenttool),
                *get_flag('arg_rgi_includeloose', arg_rgi_includeloose),
                *get_flag('arg_rgi_excludenudge', arg_rgi_excludenudge),
                *get_flag('arg_rgi_lowquality', arg_rgi_lowquality),
                *get_flag('arg_rgi_data', arg_rgi_data),
                *get_flag('arg_skip_abricate', arg_skip_abricate),
                *get_flag('arg_abricate_db', arg_abricate_db),
                *get_flag('arg_abricate_minid', arg_abricate_minid),
                *get_flag('arg_abricate_mincov', arg_abricate_mincov),
                *get_flag('bgc_skip_antismash', bgc_skip_antismash),
                *get_flag('bgc_antismash_databases', bgc_antismash_databases),
                *get_flag('bgc_antismash_installationdirectory', bgc_antismash_installationdirectory),
                *get_flag('bgc_antismash_sampleminlength', bgc_antismash_sampleminlength),
                *get_flag('bgc_antismash_contigminlength', bgc_antismash_contigminlength),
                *get_flag('bgc_antismash_cbgeneral', bgc_antismash_cbgeneral),
                *get_flag('bgc_antismash_cbknownclusters', bgc_antismash_cbknownclusters),
                *get_flag('bgc_antismash_cbsubclusters', bgc_antismash_cbsubclusters),
                *get_flag('bgc_antismash_ccmibig', bgc_antismash_ccmibig),
                *get_flag('bgc_antismash_smcogtrees', bgc_antismash_smcogtrees),
                *get_flag('bgc_antismash_hmmdetectionstrictness', bgc_antismash_hmmdetectionstrictness),
                *get_flag('bgc_antismash_taxon', bgc_antismash_taxon),
                *get_flag('bgc_skip_deepbgc', bgc_skip_deepbgc),
                *get_flag('bgc_deepbgc_database', bgc_deepbgc_database),
                *get_flag('bgc_deepbgc_score', bgc_deepbgc_score),
                *get_flag('bgc_deepbgc_prodigalsinglemode', bgc_deepbgc_prodigalsinglemode),
                *get_flag('bgc_deepbgc_mergemaxproteingap', bgc_deepbgc_mergemaxproteingap),
                *get_flag('bgc_deepbgc_mergemaxnuclgap', bgc_deepbgc_mergemaxnuclgap),
                *get_flag('bgc_deepbgc_minnucl', bgc_deepbgc_minnucl),
                *get_flag('bgc_deepbgc_minproteins', bgc_deepbgc_minproteins),
                *get_flag('bgc_deepbgc_mindomains', bgc_deepbgc_mindomains),
                *get_flag('bgc_deepbgc_minbiodomains', bgc_deepbgc_minbiodomains),
                *get_flag('bgc_deepbgc_classifierscore', bgc_deepbgc_classifierscore),
                *get_flag('bgc_skip_gecco', bgc_skip_gecco),
                *get_flag('bgc_gecco_mask', bgc_gecco_mask),
                *get_flag('bgc_gecco_cds', bgc_gecco_cds),
                *get_flag('bgc_gecco_pfilter', bgc_gecco_pfilter),
                *get_flag('bgc_gecco_threshold', bgc_gecco_threshold),
                *get_flag('bgc_gecco_edgedistance', bgc_gecco_edgedistance),
                *get_flag('bgc_skip_hmmsearch', bgc_skip_hmmsearch),
                *get_flag('bgc_hmmsearch_models', bgc_hmmsearch_models),
                *get_flag('bgc_hmmsearch_savealignments', bgc_hmmsearch_savealignments),
                *get_flag('bgc_hmmsearch_savetargets', bgc_hmmsearch_savetargets),
                *get_flag('bgc_hmmsearch_savedomains', bgc_hmmsearch_savedomains),
                *get_flag('arg_hamronization_summarizeformat', arg_hamronization_summarizeformat),
                *get_flag('multiqc_methods_description', multiqc_methods_description)
        ]

        print("Launching Nextflow Runtime")
        print(' '.join(cmd))
        print(flush=True)

        env = {
            **os.environ,
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms2048M -Xmx8G -XX:ActiveProcessorCount=4",
            "K8S_STORAGE_CLAIM_NAME": pvc_name,
            "NXF_DISABLE_CHECK_LATEST": "true",
        }
        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            name = _get_execution_name()
            if name is None:
                print("Skipping logs upload, failed to get execution name")
            else:
                remote = LPath(urljoins("latch:///your_log_dir/nf_nf_core_funcscan", name, "nextflow.log"))
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)



@workflow(metadata._nextflow_metadata)
def nf_nf_core_funcscan(input: LatchFile, outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], run_amp_screening: typing.Optional[bool], run_arg_screening: typing.Optional[bool], run_bgc_screening: typing.Optional[bool], save_annotations: typing.Optional[bool], annotation_bakta_db_localpath: typing.Optional[str], annotation_bakta_db_downloadtype: typing.Optional[str], annotation_bakta_complete: typing.Optional[bool], annotation_bakta_renamecontigheaders: typing.Optional[bool], annotation_bakta_compliant: typing.Optional[bool], annotation_bakta_trna: typing.Optional[bool], annotation_bakta_tmrna: typing.Optional[bool], annotation_bakta_rrna: typing.Optional[bool], annotation_bakta_ncrna: typing.Optional[bool], annotation_bakta_ncrnaregion: typing.Optional[bool], annotation_bakta_crispr: typing.Optional[bool], annotation_bakta_skipcds: typing.Optional[bool], annotation_bakta_pseudo: typing.Optional[bool], annotation_bakta_skipsorf: typing.Optional[bool], annotation_bakta_gap: typing.Optional[bool], annotation_bakta_ori: typing.Optional[bool], annotation_bakta_activate_plot: typing.Optional[bool], annotation_prokka_singlemode: typing.Optional[bool], annotation_prokka_rawproduct: typing.Optional[bool], annotation_prokka_cdsrnaolap: typing.Optional[bool], annotation_prokka_rnammer: typing.Optional[bool], annotation_prokka_compliant: typing.Optional[bool], annotation_prokka_addgenes: typing.Optional[bool], annotation_prokka_retaincontigheaders: typing.Optional[bool], annotation_prodigal_singlemode: typing.Optional[bool], annotation_prodigal_closed: typing.Optional[bool], annotation_prodigal_forcenonsd: typing.Optional[bool], annotation_pyrodigal_singlemode: typing.Optional[bool], annotation_pyrodigal_closed: typing.Optional[bool], annotation_pyrodigal_forcenonsd: typing.Optional[bool], save_databases: typing.Optional[bool], amp_skip_amplify: typing.Optional[bool], amp_skip_ampir: typing.Optional[bool], amp_skip_hmmsearch: typing.Optional[bool], amp_hmmsearch_models: typing.Optional[str], amp_hmmsearch_savealignments: typing.Optional[bool], amp_hmmsearch_savetargets: typing.Optional[bool], amp_hmmsearch_savedomains: typing.Optional[bool], amp_skip_macrel: typing.Optional[bool], amp_ampcombi_db: typing.Optional[str], arg_skip_amrfinderplus: typing.Optional[bool], arg_amrfinderplus_db: typing.Optional[str], arg_amrfinderplus_plus: typing.Optional[bool], arg_amrfinderplus_name: typing.Optional[bool], arg_skip_deeparg: typing.Optional[bool], arg_deeparg_data: typing.Optional[str], arg_skip_fargene: typing.Optional[bool], arg_fargene_savetmpfiles: typing.Optional[bool], arg_fargene_score: typing.Optional[float], arg_fargene_orffinder: typing.Optional[bool], arg_skip_rgi: typing.Optional[bool], arg_rgi_savejson: typing.Optional[bool], arg_rgi_savetmpfiles: typing.Optional[bool], arg_rgi_lowquality: typing.Optional[bool], arg_skip_abricate: typing.Optional[bool], bgc_skip_antismash: typing.Optional[bool], bgc_antismash_databases: typing.Optional[str], bgc_antismash_installationdirectory: typing.Optional[str], bgc_antismash_cbgeneral: typing.Optional[bool], bgc_antismash_cbknownclusters: typing.Optional[bool], bgc_antismash_cbsubclusters: typing.Optional[bool], bgc_antismash_ccmibig: typing.Optional[bool], bgc_antismash_smcogtrees: typing.Optional[bool], bgc_skip_deepbgc: typing.Optional[bool], bgc_deepbgc_database: typing.Optional[str], bgc_deepbgc_prodigalsinglemode: typing.Optional[bool], bgc_skip_gecco: typing.Optional[bool], bgc_gecco_mask: typing.Optional[bool], bgc_skip_hmmsearch: typing.Optional[bool], bgc_hmmsearch_models: typing.Optional[str], bgc_hmmsearch_savealignments: typing.Optional[bool], bgc_hmmsearch_savetargets: typing.Optional[bool], bgc_hmmsearch_savedomains: typing.Optional[bool], multiqc_methods_description: typing.Optional[str], annotation_tool: typing.Optional[str] = 'pyrodigal', annotation_bakta_mincontiglen: typing.Optional[int] = 1, annotation_bakta_translationtable: typing.Optional[int] = 11, annotation_bakta_gram: typing.Optional[str] = '?', annotation_prokka_kingdom: typing.Optional[str] = 'Bacteria', annotation_prokka_gcode: typing.Optional[int] = 11, annotation_prokka_mincontiglen: typing.Optional[int] = 1, annotation_prokka_evalue: typing.Optional[float] = 1e-06, annotation_prokka_coverage: typing.Optional[int] = 80, annotation_prodigal_transtable: typing.Optional[int] = 11, annotation_pyrodigal_transtable: typing.Optional[int] = 11, amp_ampir_model: typing.Optional[str] = 'precursor', amp_ampir_minlength: typing.Optional[int] = 10, amp_ampcombi_cutoff: typing.Optional[float] = 0.4, arg_amrfinderplus_identmin: typing.Optional[float] = -1, arg_amrfinderplus_coveragemin: typing.Optional[float] = 0.5, arg_amrfinderplus_translationtable: typing.Optional[int] = 11, arg_deeparg_data_version: typing.Optional[int] = 2, arg_deeparg_model: typing.Optional[str] = 'LS', arg_deeparg_minprob: typing.Optional[float] = 0.8, arg_deeparg_alignmentevalue: typing.Optional[float] = 1e-10, arg_deeparg_alignmentidentity: typing.Optional[int] = 50, arg_deeparg_alignmentoverlap: typing.Optional[float] = 0.8, arg_deeparg_numalignmentsperentry: typing.Optional[int] = 1000, arg_fargene_hmmmodel: typing.Optional[str] = 'class_a,class_b_1_2,class_b_3,class_c,class_d_1,class_d_2,qnr,tet_efflux,tet_rpg,tet_enzyme', arg_fargene_minorflength: typing.Optional[int] = 90, arg_fargene_translationformat: typing.Optional[str] = 'pearson', arg_rgi_alignmenttool: typing.Optional[str] = 'BLAST', arg_rgi_includeloose: typing.Optional[bool] = True, arg_rgi_excludenudge: typing.Optional[bool] = True, arg_rgi_data: typing.Optional[str] = 'NA', arg_abricate_db: typing.Optional[str] = 'ncbi', arg_abricate_minid: typing.Optional[int] = 80, arg_abricate_mincov: typing.Optional[int] = 80, bgc_antismash_sampleminlength: typing.Optional[int] = 1000, bgc_antismash_contigminlength: typing.Optional[int] = 1000, bgc_antismash_hmmdetectionstrictness: typing.Optional[str] = 'relaxed', bgc_antismash_taxon: typing.Optional[str] = 'bacteria', bgc_deepbgc_score: typing.Optional[float] = 0.5, bgc_deepbgc_mergemaxproteingap: typing.Optional[int] = 0, bgc_deepbgc_mergemaxnuclgap: typing.Optional[int] = 0, bgc_deepbgc_minnucl: typing.Optional[int] = 1, bgc_deepbgc_minproteins: typing.Optional[int] = 1, bgc_deepbgc_mindomains: typing.Optional[int] = 1, bgc_deepbgc_minbiodomains: typing.Optional[int] = 0, bgc_deepbgc_classifierscore: typing.Optional[float] = 0.5, bgc_gecco_cds: typing.Optional[int] = 3, bgc_gecco_pfilter: typing.Optional[float] = 1e-09, bgc_gecco_threshold: typing.Optional[float] = 0.8, bgc_gecco_edgedistance: typing.Optional[int] = 0, arg_hamronization_summarizeformat: typing.Optional[str] = 'tsv') -> None:
    """
    nf-core/funcscan

    Sample Description
    """

    pvc_name: str = initialize()
    nextflow_runtime(pvc_name=pvc_name, input=input, outdir=outdir, email=email, multiqc_title=multiqc_title, run_amp_screening=run_amp_screening, run_arg_screening=run_arg_screening, run_bgc_screening=run_bgc_screening, annotation_tool=annotation_tool, save_annotations=save_annotations, annotation_bakta_db_localpath=annotation_bakta_db_localpath, annotation_bakta_db_downloadtype=annotation_bakta_db_downloadtype, annotation_bakta_mincontiglen=annotation_bakta_mincontiglen, annotation_bakta_translationtable=annotation_bakta_translationtable, annotation_bakta_gram=annotation_bakta_gram, annotation_bakta_complete=annotation_bakta_complete, annotation_bakta_renamecontigheaders=annotation_bakta_renamecontigheaders, annotation_bakta_compliant=annotation_bakta_compliant, annotation_bakta_trna=annotation_bakta_trna, annotation_bakta_tmrna=annotation_bakta_tmrna, annotation_bakta_rrna=annotation_bakta_rrna, annotation_bakta_ncrna=annotation_bakta_ncrna, annotation_bakta_ncrnaregion=annotation_bakta_ncrnaregion, annotation_bakta_crispr=annotation_bakta_crispr, annotation_bakta_skipcds=annotation_bakta_skipcds, annotation_bakta_pseudo=annotation_bakta_pseudo, annotation_bakta_skipsorf=annotation_bakta_skipsorf, annotation_bakta_gap=annotation_bakta_gap, annotation_bakta_ori=annotation_bakta_ori, annotation_bakta_activate_plot=annotation_bakta_activate_plot, annotation_prokka_singlemode=annotation_prokka_singlemode, annotation_prokka_rawproduct=annotation_prokka_rawproduct, annotation_prokka_kingdom=annotation_prokka_kingdom, annotation_prokka_gcode=annotation_prokka_gcode, annotation_prokka_mincontiglen=annotation_prokka_mincontiglen, annotation_prokka_evalue=annotation_prokka_evalue, annotation_prokka_coverage=annotation_prokka_coverage, annotation_prokka_cdsrnaolap=annotation_prokka_cdsrnaolap, annotation_prokka_rnammer=annotation_prokka_rnammer, annotation_prokka_compliant=annotation_prokka_compliant, annotation_prokka_addgenes=annotation_prokka_addgenes, annotation_prokka_retaincontigheaders=annotation_prokka_retaincontigheaders, annotation_prodigal_singlemode=annotation_prodigal_singlemode, annotation_prodigal_closed=annotation_prodigal_closed, annotation_prodigal_transtable=annotation_prodigal_transtable, annotation_prodigal_forcenonsd=annotation_prodigal_forcenonsd, annotation_pyrodigal_singlemode=annotation_pyrodigal_singlemode, annotation_pyrodigal_closed=annotation_pyrodigal_closed, annotation_pyrodigal_transtable=annotation_pyrodigal_transtable, annotation_pyrodigal_forcenonsd=annotation_pyrodigal_forcenonsd, save_databases=save_databases, amp_skip_amplify=amp_skip_amplify, amp_skip_ampir=amp_skip_ampir, amp_ampir_model=amp_ampir_model, amp_ampir_minlength=amp_ampir_minlength, amp_skip_hmmsearch=amp_skip_hmmsearch, amp_hmmsearch_models=amp_hmmsearch_models, amp_hmmsearch_savealignments=amp_hmmsearch_savealignments, amp_hmmsearch_savetargets=amp_hmmsearch_savetargets, amp_hmmsearch_savedomains=amp_hmmsearch_savedomains, amp_skip_macrel=amp_skip_macrel, amp_ampcombi_db=amp_ampcombi_db, amp_ampcombi_cutoff=amp_ampcombi_cutoff, arg_skip_amrfinderplus=arg_skip_amrfinderplus, arg_amrfinderplus_db=arg_amrfinderplus_db, arg_amrfinderplus_identmin=arg_amrfinderplus_identmin, arg_amrfinderplus_coveragemin=arg_amrfinderplus_coveragemin, arg_amrfinderplus_translationtable=arg_amrfinderplus_translationtable, arg_amrfinderplus_plus=arg_amrfinderplus_plus, arg_amrfinderplus_name=arg_amrfinderplus_name, arg_skip_deeparg=arg_skip_deeparg, arg_deeparg_data=arg_deeparg_data, arg_deeparg_data_version=arg_deeparg_data_version, arg_deeparg_model=arg_deeparg_model, arg_deeparg_minprob=arg_deeparg_minprob, arg_deeparg_alignmentevalue=arg_deeparg_alignmentevalue, arg_deeparg_alignmentidentity=arg_deeparg_alignmentidentity, arg_deeparg_alignmentoverlap=arg_deeparg_alignmentoverlap, arg_deeparg_numalignmentsperentry=arg_deeparg_numalignmentsperentry, arg_skip_fargene=arg_skip_fargene, arg_fargene_hmmmodel=arg_fargene_hmmmodel, arg_fargene_savetmpfiles=arg_fargene_savetmpfiles, arg_fargene_score=arg_fargene_score, arg_fargene_minorflength=arg_fargene_minorflength, arg_fargene_orffinder=arg_fargene_orffinder, arg_fargene_translationformat=arg_fargene_translationformat, arg_skip_rgi=arg_skip_rgi, arg_rgi_savejson=arg_rgi_savejson, arg_rgi_savetmpfiles=arg_rgi_savetmpfiles, arg_rgi_alignmenttool=arg_rgi_alignmenttool, arg_rgi_includeloose=arg_rgi_includeloose, arg_rgi_excludenudge=arg_rgi_excludenudge, arg_rgi_lowquality=arg_rgi_lowquality, arg_rgi_data=arg_rgi_data, arg_skip_abricate=arg_skip_abricate, arg_abricate_db=arg_abricate_db, arg_abricate_minid=arg_abricate_minid, arg_abricate_mincov=arg_abricate_mincov, bgc_skip_antismash=bgc_skip_antismash, bgc_antismash_databases=bgc_antismash_databases, bgc_antismash_installationdirectory=bgc_antismash_installationdirectory, bgc_antismash_sampleminlength=bgc_antismash_sampleminlength, bgc_antismash_contigminlength=bgc_antismash_contigminlength, bgc_antismash_cbgeneral=bgc_antismash_cbgeneral, bgc_antismash_cbknownclusters=bgc_antismash_cbknownclusters, bgc_antismash_cbsubclusters=bgc_antismash_cbsubclusters, bgc_antismash_ccmibig=bgc_antismash_ccmibig, bgc_antismash_smcogtrees=bgc_antismash_smcogtrees, bgc_antismash_hmmdetectionstrictness=bgc_antismash_hmmdetectionstrictness, bgc_antismash_taxon=bgc_antismash_taxon, bgc_skip_deepbgc=bgc_skip_deepbgc, bgc_deepbgc_database=bgc_deepbgc_database, bgc_deepbgc_score=bgc_deepbgc_score, bgc_deepbgc_prodigalsinglemode=bgc_deepbgc_prodigalsinglemode, bgc_deepbgc_mergemaxproteingap=bgc_deepbgc_mergemaxproteingap, bgc_deepbgc_mergemaxnuclgap=bgc_deepbgc_mergemaxnuclgap, bgc_deepbgc_minnucl=bgc_deepbgc_minnucl, bgc_deepbgc_minproteins=bgc_deepbgc_minproteins, bgc_deepbgc_mindomains=bgc_deepbgc_mindomains, bgc_deepbgc_minbiodomains=bgc_deepbgc_minbiodomains, bgc_deepbgc_classifierscore=bgc_deepbgc_classifierscore, bgc_skip_gecco=bgc_skip_gecco, bgc_gecco_mask=bgc_gecco_mask, bgc_gecco_cds=bgc_gecco_cds, bgc_gecco_pfilter=bgc_gecco_pfilter, bgc_gecco_threshold=bgc_gecco_threshold, bgc_gecco_edgedistance=bgc_gecco_edgedistance, bgc_skip_hmmsearch=bgc_skip_hmmsearch, bgc_hmmsearch_models=bgc_hmmsearch_models, bgc_hmmsearch_savealignments=bgc_hmmsearch_savealignments, bgc_hmmsearch_savetargets=bgc_hmmsearch_savetargets, bgc_hmmsearch_savedomains=bgc_hmmsearch_savedomains, arg_hamronization_summarizeformat=arg_hamronization_summarizeformat, multiqc_methods_description=multiqc_methods_description)

