import sys
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
from latch.executions import report_nextflow_used_storage
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
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage-ofs",
        headers=headers,
        json={
            "storage_expiration_hours": 0,
            "version": 1,
        },
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]


class ampir_model(Enum):
    precursor = 'precursor'
    mature = 'mature'




class annotation_database(Enum):
    bakta = 'bakta'
    prodigal = 'prodigal'
    pyrodigal = 'pyrodigal'
    prokka = 'prokka'




@dataclass
class Samplesheet:
    sample: str
    fasta: LatchFile
    protein: typing.Optional[LatchFile]
    gbk: typing.Optional[LatchFile]




input_construct_samplesheet = metadata._nextflow_metadata.parameters['input'].samplesheet_constructor


@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(pvc_name: str, input: typing.List[Samplesheet], outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], run_amp_screening: bool, run_arg_screening: bool, run_bgc_screening: bool, run_taxa_classification: bool, taxa_classification_mmseqs_db: typing.Optional[LatchDir], taxa_classification_mmseqs_db_savetmp: bool, taxa_classification_mmseqs_taxonomy_savetmp: bool, save_annotations: bool, annotation_bakta_db: typing.Optional[LatchDir], annotation_bakta_singlemode: bool, annotation_bakta_complete: bool, annotation_bakta_renamecontigheaders: bool, annotation_bakta_compliant: bool, annotation_bakta_trna: bool, annotation_bakta_tmrna: bool, annotation_bakta_rrna: bool, annotation_bakta_ncrna: bool, annotation_bakta_ncrnaregion: bool, annotation_bakta_crispr: bool, annotation_bakta_skipcds: bool, annotation_bakta_pseudo: bool, annotation_bakta_skipsorf: bool, annotation_bakta_gap: bool, annotation_bakta_ori: bool, annotation_bakta_activate_plot: bool, annotation_prokka_singlemode: bool, annotation_prokka_rawproduct: bool, annotation_prokka_cdsrnaolap: bool, annotation_prokka_rnammer: bool, annotation_prokka_addgenes: bool, annotation_prokka_retaincontigheaders: bool, annotation_prodigal_singlemode: bool, annotation_prodigal_closed: bool, annotation_prodigal_forcenonsd: bool, annotation_pyrodigal_singlemode: bool, annotation_pyrodigal_closed: bool, annotation_pyrodigal_forcenonsd: bool, save_db: bool, amp_skip_amplify: bool, amp_skip_ampir: bool, amp_run_hmmsearch: bool, amp_hmmsearch_models: typing.Optional[LatchDir], amp_hmmsearch_savealignments: bool, amp_hmmsearch_savetargets: bool, amp_hmmsearch_savedomains: bool, amp_skip_macrel: bool, amp_ampcombi_db: typing.Optional[LatchDir], amp_ampcombi_parsetables_removehitswostopcodons: bool, amp_ampcombi_cluster_removesingletons: bool, arg_skip_amrfinderplus: bool, arg_amrfinderplus_db: typing.Optional[LatchDir], arg_amrfinderplus_plus: bool, arg_amrfinderplus_name: bool, arg_skip_deeparg: bool, arg_deeparg_db: typing.Optional[LatchDir], arg_skip_fargene: bool, arg_fargene_savetmpfiles: bool, arg_fargene_score: typing.Optional[float], arg_fargene_orffinder: bool, arg_skip_rgi: bool, arg_rgi_db: typing.Optional[LatchDir], arg_rgi_savejson: bool, arg_rgi_savetmpfiles: bool, arg_rgi_includeloose: bool, arg_rgi_includenudge: bool, arg_rgi_lowquality: bool, arg_skip_abricate: bool, arg_abricate_db: typing.Optional[LatchDir], arg_skip_argnorm: bool, bgc_savefilteredcontigs: bool, bgc_skip_antismash: bool, bgc_antismash_db: typing.Optional[LatchDir], bgc_antismash_installdir: typing.Optional[LatchDir], bgc_antismash_cbgeneral: bool, bgc_antismash_cbknownclusters: bool, bgc_antismash_cbsubclusters: bool, bgc_antismash_ccmibig: bool, bgc_antismash_smcogtrees: bool, bgc_skip_deepbgc: bool, bgc_deepbgc_db: typing.Optional[LatchDir], multiqc_methods_description: typing.Optional[str], taxa_classification_tool: typing.Optional[str], taxa_classification_mmseqs_db_id: typing.Optional[str], taxa_classification_mmseqs_taxonomy_searchtype: typing.Optional[int], taxa_classification_mmseqs_taxonomy_lcaranks: typing.Optional[str], taxa_classification_mmseqs_taxonomy_taxlineage: typing.Optional[int], taxa_classification_mmseqs_taxonomy_sensitivity: typing.Optional[str], taxa_classification_mmseqs_taxonomy_orffilters: typing.Optional[str], taxa_classification_mmseqs_taxonomy_lcamode: typing.Optional[int], taxa_classification_mmseqs_taxonomy_votemode: typing.Optional[int], annotation_tool: annotation_database, annotation_bakta_db_downloadtype: typing.Optional[str], annotation_bakta_mincontiglen: typing.Optional[int], annotation_bakta_translationtable: typing.Optional[int], annotation_bakta_gram: typing.Optional[str], annotation_prokka_kingdom: typing.Optional[str], annotation_prokka_gcode: typing.Optional[int], annotation_prokka_mincontiglen: typing.Optional[int], annotation_prokka_evalue: typing.Optional[float], annotation_prokka_coverage: typing.Optional[int], annotation_prokka_compliant: bool, annotation_prodigal_transtable: typing.Optional[int], annotation_pyrodigal_transtable: typing.Optional[int], amp_ampir_model: typing.Optional[ampir_model], amp_ampir_minlength: typing.Optional[int], amp_ampcombi_parsetables_cutoff: typing.Optional[float], amp_ampcombi_parsetables_aalength: typing.Optional[int], amp_ampcombi_parsetables_dbevalue: typing.Optional[float], amp_ampcombi_parsetables_hmmevalue: typing.Optional[float], amp_ampcombi_parsetables_windowstopcodon: typing.Optional[int], amp_ampcombi_parsetables_windowtransport: typing.Optional[int], amp_ampcombi_cluster_covmode: typing.Optional[float], amp_ampcombi_cluster_sensitivity: typing.Optional[float], amp_ampcombi_cluster_minmembers: typing.Optional[int], amp_ampcombi_cluster_mode: typing.Optional[float], amp_ampcombi_cluster_coverage: typing.Optional[float], amp_ampcombi_cluster_seqid: typing.Optional[float], arg_amrfinderplus_identmin: typing.Optional[float], arg_amrfinderplus_coveragemin: typing.Optional[float], arg_amrfinderplus_translationtable: typing.Optional[int], arg_deeparg_db_version: typing.Optional[int], arg_deeparg_model: typing.Optional[str], arg_deeparg_minprob: typing.Optional[float], arg_deeparg_alignmentevalue: typing.Optional[float], arg_deeparg_alignmentidentity: typing.Optional[int], arg_deeparg_alignmentoverlap: typing.Optional[float], arg_deeparg_numalignmentsperentry: typing.Optional[int], arg_fargene_hmmmodel: typing.Optional[str], arg_fargene_minorflength: typing.Optional[int], arg_fargene_translationformat: typing.Optional[str], arg_rgi_alignmenttool: typing.Optional[str], arg_rgi_data: typing.Optional[str], arg_rgi_split_prodigal_jobs: bool, arg_abricate_db_id: typing.Optional[str], arg_abricate_minid: typing.Optional[int], arg_abricate_mincov: typing.Optional[int], arg_hamronization_summarizeformat: typing.Optional[str], bgc_mincontiglength: typing.Optional[int], bgc_antismash_contigminlength: typing.Optional[int], bgc_antismash_hmmdetectionstrictness: typing.Optional[str], bgc_antismash_pfam2go: bool, bgc_antismash_rre: bool, bgc_antismash_taxon: typing.Optional[str], bgc_antismash_tfbs: bool, bgc_deepbgc_score: typing.Optional[float], bgc_deepbgc_minnucl: typing.Optional[int], bgc_deepbgc_minproteins: typing.Optional[int]) -> None:
    shared_dir = Path("/nf-workdir")

    exec_name = _get_execution_name()
    if exec_name is None:
        print("Failed to get execution name.")
        exec_name = "unknown"

    latch_log_dir = urljoins("latch:///your_log_dir/nf_nf_core_funcscan", exec_name)
    print(f"Log directory: {latch_log_dir}")


    input_samplesheet = input_construct_samplesheet(input)

    ignore_list = [
        "latch",
        ".latch",
        ".git",
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

    profile_list = ['docker']
    if False:
        profile_list.extend([p.value for p in execution_profiles])

    if len(profile_list) == 0:
        profile_list.append("standard")

    profiles = ','.join(profile_list)

    cmd = [
        "/root/nextflow",
        "run",
        str(shared_dir / "main.nf"),
        "-work-dir",
        str(shared_dir),
        "-profile",
        profiles,
        "-c",
        "latch.config",
        "-resume",
        *get_flag('input', input_samplesheet),
                *get_flag('outdir', outdir),
                *get_flag('email', email),
                *get_flag('multiqc_title', multiqc_title),
                *get_flag('run_amp_screening', run_amp_screening),
                *get_flag('run_arg_screening', run_arg_screening),
                *get_flag('run_bgc_screening', run_bgc_screening),
                *get_flag('run_taxa_classification', run_taxa_classification),
                *get_flag('taxa_classification_tool', taxa_classification_tool),
                *get_flag('taxa_classification_mmseqs_db', taxa_classification_mmseqs_db),
                *get_flag('taxa_classification_mmseqs_db_id', taxa_classification_mmseqs_db_id),
                *get_flag('taxa_classification_mmseqs_db_savetmp', taxa_classification_mmseqs_db_savetmp),
                *get_flag('taxa_classification_mmseqs_taxonomy_savetmp', taxa_classification_mmseqs_taxonomy_savetmp),
                *get_flag('taxa_classification_mmseqs_taxonomy_searchtype', taxa_classification_mmseqs_taxonomy_searchtype),
                *get_flag('taxa_classification_mmseqs_taxonomy_lcaranks', taxa_classification_mmseqs_taxonomy_lcaranks),
                *get_flag('taxa_classification_mmseqs_taxonomy_taxlineage', taxa_classification_mmseqs_taxonomy_taxlineage),
                *get_flag('taxa_classification_mmseqs_taxonomy_sensitivity', taxa_classification_mmseqs_taxonomy_sensitivity),
                *get_flag('taxa_classification_mmseqs_taxonomy_orffilters', taxa_classification_mmseqs_taxonomy_orffilters),
                *get_flag('taxa_classification_mmseqs_taxonomy_lcamode', taxa_classification_mmseqs_taxonomy_lcamode),
                *get_flag('taxa_classification_mmseqs_taxonomy_votemode', taxa_classification_mmseqs_taxonomy_votemode),
                *get_flag('annotation_tool', annotation_tool),
                *get_flag('save_annotations', save_annotations),
                *get_flag('annotation_bakta_db', annotation_bakta_db),
                *get_flag('annotation_bakta_db_downloadtype', annotation_bakta_db_downloadtype),
                *get_flag('annotation_bakta_singlemode', annotation_bakta_singlemode),
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
                *get_flag('save_db', save_db),
                *get_flag('amp_skip_amplify', amp_skip_amplify),
                *get_flag('amp_skip_ampir', amp_skip_ampir),
                *get_flag('amp_ampir_model', amp_ampir_model),
                *get_flag('amp_ampir_minlength', amp_ampir_minlength),
                *get_flag('amp_run_hmmsearch', amp_run_hmmsearch),
                *get_flag('amp_hmmsearch_models', amp_hmmsearch_models),
                *get_flag('amp_hmmsearch_savealignments', amp_hmmsearch_savealignments),
                *get_flag('amp_hmmsearch_savetargets', amp_hmmsearch_savetargets),
                *get_flag('amp_hmmsearch_savedomains', amp_hmmsearch_savedomains),
                *get_flag('amp_skip_macrel', amp_skip_macrel),
                *get_flag('amp_ampcombi_db', amp_ampcombi_db),
                *get_flag('amp_ampcombi_parsetables_cutoff', amp_ampcombi_parsetables_cutoff),
                *get_flag('amp_ampcombi_parsetables_aalength', amp_ampcombi_parsetables_aalength),
                *get_flag('amp_ampcombi_parsetables_dbevalue', amp_ampcombi_parsetables_dbevalue),
                *get_flag('amp_ampcombi_parsetables_hmmevalue', amp_ampcombi_parsetables_hmmevalue),
                *get_flag('amp_ampcombi_parsetables_windowstopcodon', amp_ampcombi_parsetables_windowstopcodon),
                *get_flag('amp_ampcombi_parsetables_windowtransport', amp_ampcombi_parsetables_windowtransport),
                *get_flag('amp_ampcombi_parsetables_removehitswostopcodons', amp_ampcombi_parsetables_removehitswostopcodons),
                *get_flag('amp_ampcombi_cluster_covmode', amp_ampcombi_cluster_covmode),
                *get_flag('amp_ampcombi_cluster_sensitivity', amp_ampcombi_cluster_sensitivity),
                *get_flag('amp_ampcombi_cluster_minmembers', amp_ampcombi_cluster_minmembers),
                *get_flag('amp_ampcombi_cluster_mode', amp_ampcombi_cluster_mode),
                *get_flag('amp_ampcombi_cluster_coverage', amp_ampcombi_cluster_coverage),
                *get_flag('amp_ampcombi_cluster_seqid', amp_ampcombi_cluster_seqid),
                *get_flag('amp_ampcombi_cluster_removesingletons', amp_ampcombi_cluster_removesingletons),
                *get_flag('arg_skip_amrfinderplus', arg_skip_amrfinderplus),
                *get_flag('arg_amrfinderplus_db', arg_amrfinderplus_db),
                *get_flag('arg_amrfinderplus_identmin', arg_amrfinderplus_identmin),
                *get_flag('arg_amrfinderplus_coveragemin', arg_amrfinderplus_coveragemin),
                *get_flag('arg_amrfinderplus_translationtable', arg_amrfinderplus_translationtable),
                *get_flag('arg_amrfinderplus_plus', arg_amrfinderplus_plus),
                *get_flag('arg_amrfinderplus_name', arg_amrfinderplus_name),
                *get_flag('arg_skip_deeparg', arg_skip_deeparg),
                *get_flag('arg_deeparg_db', arg_deeparg_db),
                *get_flag('arg_deeparg_db_version', arg_deeparg_db_version),
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
                *get_flag('arg_rgi_db', arg_rgi_db),
                *get_flag('arg_rgi_savejson', arg_rgi_savejson),
                *get_flag('arg_rgi_savetmpfiles', arg_rgi_savetmpfiles),
                *get_flag('arg_rgi_alignmenttool', arg_rgi_alignmenttool),
                *get_flag('arg_rgi_includeloose', arg_rgi_includeloose),
                *get_flag('arg_rgi_includenudge', arg_rgi_includenudge),
                *get_flag('arg_rgi_lowquality', arg_rgi_lowquality),
                *get_flag('arg_rgi_data', arg_rgi_data),
                *get_flag('arg_rgi_split_prodigal_jobs', arg_rgi_split_prodigal_jobs),
                *get_flag('arg_skip_abricate', arg_skip_abricate),
                *get_flag('arg_abricate_db_id', arg_abricate_db_id),
                *get_flag('arg_abricate_db', arg_abricate_db),
                *get_flag('arg_abricate_minid', arg_abricate_minid),
                *get_flag('arg_abricate_mincov', arg_abricate_mincov),
                *get_flag('arg_hamronization_summarizeformat', arg_hamronization_summarizeformat),
                *get_flag('arg_skip_argnorm', arg_skip_argnorm),
                *get_flag('bgc_mincontiglength', bgc_mincontiglength),
                *get_flag('bgc_savefilteredcontigs', bgc_savefilteredcontigs),
                *get_flag('bgc_skip_antismash', bgc_skip_antismash),
                *get_flag('bgc_antismash_db', bgc_antismash_db),
                *get_flag('bgc_antismash_installdir', bgc_antismash_installdir),
                *get_flag('bgc_antismash_contigminlength', bgc_antismash_contigminlength),
                *get_flag('bgc_antismash_cbgeneral', bgc_antismash_cbgeneral),
                *get_flag('bgc_antismash_cbknownclusters', bgc_antismash_cbknownclusters),
                *get_flag('bgc_antismash_cbsubclusters', bgc_antismash_cbsubclusters),
                *get_flag('bgc_antismash_ccmibig', bgc_antismash_ccmibig),
                *get_flag('bgc_antismash_smcogtrees', bgc_antismash_smcogtrees),
                *get_flag('bgc_antismash_hmmdetectionstrictness', bgc_antismash_hmmdetectionstrictness),
                *get_flag('bgc_antismash_pfam2go', bgc_antismash_pfam2go),
                *get_flag('bgc_antismash_rre', bgc_antismash_rre),
                *get_flag('bgc_antismash_taxon', bgc_antismash_taxon),
                *get_flag('bgc_antismash_tfbs', bgc_antismash_tfbs),
                *get_flag('bgc_skip_deepbgc', bgc_skip_deepbgc),
                *get_flag('bgc_deepbgc_db', bgc_deepbgc_db),
                *get_flag('bgc_deepbgc_score', bgc_deepbgc_score),
                *get_flag('bgc_deepbgc_minnucl', bgc_deepbgc_minnucl),
                *get_flag('bgc_deepbgc_minproteins', bgc_deepbgc_minproteins),
                *get_flag('multiqc_methods_description', multiqc_methods_description)
    ]

    print("Launching Nextflow Runtime")
    print(' '.join(cmd))
    print(flush=True)

    failed = False
    try:
        env = {
            **os.environ,
            "NXF_ANSI_LOG": "false",
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms1536M -Xmx6144M -XX:ActiveProcessorCount=4",
            "NXF_DISABLE_CHECK_LATEST": "true",
            "NXF_ENABLE_VIRTUAL_THREADS": "false",
            "NXF_ENABLE_FS_SYNC": "true",
        }

        if False:
            env["LATCH_LOG_DIR"] = latch_log_dir

        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    except subprocess.CalledProcessError:
        failed = True
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            remote = LPath(urljoins(latch_log_dir, "nextflow.log"))
            print(f"Uploading .nextflow.log to {remote.path}")
            remote.upload_from(nextflow_log)

        print("Computing size of workdir... ", end="")
        try:
            result = subprocess.run(
                ['du', '-sb', str(shared_dir)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5 * 60
            )

            size = int(result.stdout.split()[0])
            report_nextflow_used_storage(size)
            print(f"Done. Workdir size: {size / 1024 / 1024 / 1024: .2f} GiB")
        except subprocess.TimeoutExpired:
            print("Failed to compute storage size: Operation timed out after 5 minutes.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to compute storage size: {e.stderr}")
        except Exception as e:
            print(f"Failed to compute storage size: {e}")

    if failed:
        sys.exit(1)


@workflow(metadata._nextflow_metadata)
def nf_nf_core_funcscan(input: typing.List[Samplesheet], outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], run_amp_screening: bool, run_arg_screening: bool, run_bgc_screening: bool, run_taxa_classification: bool, taxa_classification_mmseqs_db: typing.Optional[LatchDir], taxa_classification_mmseqs_db_savetmp: bool, taxa_classification_mmseqs_taxonomy_savetmp: bool, save_annotations: bool, annotation_bakta_db: typing.Optional[LatchDir], annotation_bakta_singlemode: bool, annotation_bakta_complete: bool, annotation_bakta_renamecontigheaders: bool, annotation_bakta_compliant: bool, annotation_bakta_trna: bool, annotation_bakta_tmrna: bool, annotation_bakta_rrna: bool, annotation_bakta_ncrna: bool, annotation_bakta_ncrnaregion: bool, annotation_bakta_crispr: bool, annotation_bakta_skipcds: bool, annotation_bakta_pseudo: bool, annotation_bakta_skipsorf: bool, annotation_bakta_gap: bool, annotation_bakta_ori: bool, annotation_bakta_activate_plot: bool, annotation_prokka_singlemode: bool, annotation_prokka_rawproduct: bool, annotation_prokka_cdsrnaolap: bool, annotation_prokka_rnammer: bool, annotation_prokka_addgenes: bool, annotation_prokka_retaincontigheaders: bool, annotation_prodigal_singlemode: bool, annotation_prodigal_closed: bool, annotation_prodigal_forcenonsd: bool, annotation_pyrodigal_singlemode: bool, annotation_pyrodigal_closed: bool, annotation_pyrodigal_forcenonsd: bool, save_db: bool, amp_skip_amplify: bool, amp_skip_ampir: bool, amp_run_hmmsearch: bool, amp_hmmsearch_models: typing.Optional[LatchDir], amp_hmmsearch_savealignments: bool, amp_hmmsearch_savetargets: bool, amp_hmmsearch_savedomains: bool, amp_skip_macrel: bool, amp_ampcombi_db: typing.Optional[LatchDir], amp_ampcombi_parsetables_removehitswostopcodons: bool, amp_ampcombi_cluster_removesingletons: bool, arg_skip_amrfinderplus: bool, arg_amrfinderplus_db: typing.Optional[LatchDir], arg_amrfinderplus_plus: bool, arg_amrfinderplus_name: bool, arg_skip_deeparg: bool, arg_deeparg_db: typing.Optional[LatchDir], arg_skip_fargene: bool, arg_fargene_savetmpfiles: bool, arg_fargene_score: typing.Optional[float], arg_fargene_orffinder: bool, arg_skip_rgi: bool, arg_rgi_db: typing.Optional[LatchDir], arg_rgi_savejson: bool, arg_rgi_savetmpfiles: bool, arg_rgi_includeloose: bool, arg_rgi_includenudge: bool, arg_rgi_lowquality: bool, arg_skip_abricate: bool, arg_abricate_db: typing.Optional[LatchDir], arg_skip_argnorm: bool, bgc_savefilteredcontigs: bool, bgc_skip_antismash: bool, bgc_antismash_db: typing.Optional[LatchDir], bgc_antismash_installdir: typing.Optional[LatchDir], bgc_antismash_cbgeneral: bool, bgc_antismash_cbknownclusters: bool, bgc_antismash_cbsubclusters: bool, bgc_antismash_ccmibig: bool, bgc_antismash_smcogtrees: bool, bgc_skip_deepbgc: bool, bgc_deepbgc_db: typing.Optional[LatchDir], multiqc_methods_description: typing.Optional[str], taxa_classification_tool: typing.Optional[str] = 'mmseqs2', taxa_classification_mmseqs_db_id: typing.Optional[str] = 'Kalamari', taxa_classification_mmseqs_taxonomy_searchtype: typing.Optional[int] = 2, taxa_classification_mmseqs_taxonomy_lcaranks: typing.Optional[str] = 'kingdom,phylum,class,order,family,genus,species', taxa_classification_mmseqs_taxonomy_taxlineage: typing.Optional[int] = 1, taxa_classification_mmseqs_taxonomy_sensitivity: typing.Optional[str] = '5.0', taxa_classification_mmseqs_taxonomy_orffilters: typing.Optional[str] = '2.0', taxa_classification_mmseqs_taxonomy_lcamode: typing.Optional[int] = 3, taxa_classification_mmseqs_taxonomy_votemode: typing.Optional[int] = 1, annotation_tool: annotation_database = annotation_database.pyrodigal, annotation_bakta_db_downloadtype: typing.Optional[str] = 'full', annotation_bakta_mincontiglen: typing.Optional[int] = 1, annotation_bakta_translationtable: typing.Optional[int] = 11, annotation_bakta_gram: typing.Optional[str] = '?', annotation_prokka_kingdom: typing.Optional[str] = 'Bacteria', annotation_prokka_gcode: typing.Optional[int] = 11, annotation_prokka_mincontiglen: typing.Optional[int] = 1, annotation_prokka_evalue: typing.Optional[float] = 1e-06, annotation_prokka_coverage: typing.Optional[int] = 80, annotation_prokka_compliant: bool = True, annotation_prodigal_transtable: typing.Optional[int] = 11, annotation_pyrodigal_transtable: typing.Optional[int] = 11, amp_ampir_model: typing.Optional[ampir_model] = ampir_model.precursor, amp_ampir_minlength: typing.Optional[int] = 10, amp_ampcombi_parsetables_cutoff: typing.Optional[float] = 0.6, amp_ampcombi_parsetables_aalength: typing.Optional[int] = 100, amp_ampcombi_parsetables_dbevalue: typing.Optional[float] = 5.0, amp_ampcombi_parsetables_hmmevalue: typing.Optional[float] = 0.06, amp_ampcombi_parsetables_windowstopcodon: typing.Optional[int] = 60, amp_ampcombi_parsetables_windowtransport: typing.Optional[int] = 11, amp_ampcombi_cluster_covmode: typing.Optional[float] = 0.0, amp_ampcombi_cluster_sensitivity: typing.Optional[float] = 4.0, amp_ampcombi_cluster_minmembers: typing.Optional[int] = 0, amp_ampcombi_cluster_mode: typing.Optional[float] = 1.0, amp_ampcombi_cluster_coverage: typing.Optional[float] = 0.8, amp_ampcombi_cluster_seqid: typing.Optional[float] = 0.4, arg_amrfinderplus_identmin: typing.Optional[float] = -1.0, arg_amrfinderplus_coveragemin: typing.Optional[float] = 0.5, arg_amrfinderplus_translationtable: typing.Optional[int] = 11, arg_deeparg_db_version: typing.Optional[int] = 2, arg_deeparg_model: typing.Optional[str] = 'LS', arg_deeparg_minprob: typing.Optional[float] = 0.8, arg_deeparg_alignmentevalue: typing.Optional[float] = 1e-10, arg_deeparg_alignmentidentity: typing.Optional[int] = 50, arg_deeparg_alignmentoverlap: typing.Optional[float] = 0.8, arg_deeparg_numalignmentsperentry: typing.Optional[int] = 1000, arg_fargene_hmmmodel: typing.Optional[str] = 'class_a,class_b_1_2,class_b_3,class_c,class_d_1,class_d_2,qnr,tet_efflux,tet_rpg,tet_enzyme', arg_fargene_minorflength: typing.Optional[int] = 90, arg_fargene_translationformat: typing.Optional[str] = 'pearson', arg_rgi_alignmenttool: typing.Optional[str] = 'BLAST', arg_rgi_data: typing.Optional[str] = 'NA', arg_rgi_split_prodigal_jobs: bool = True, arg_abricate_db_id: typing.Optional[str] = 'ncbi', arg_abricate_minid: typing.Optional[int] = 80, arg_abricate_mincov: typing.Optional[int] = 80, arg_hamronization_summarizeformat: typing.Optional[str] = 'tsv', bgc_mincontiglength: typing.Optional[int] = 3000, bgc_antismash_contigminlength: typing.Optional[int] = 3000, bgc_antismash_hmmdetectionstrictness: typing.Optional[str] = 'relaxed', bgc_antismash_pfam2go: bool = False, bgc_antismash_rre: bool = False, bgc_antismash_taxon: typing.Optional[str] = 'bacteria', bgc_antismash_tfbs: bool = False, bgc_deepbgc_score: typing.Optional[float] = 0.5, bgc_deepbgc_minnucl: typing.Optional[int] = 1, bgc_deepbgc_minproteins: typing.Optional[int] = 1) -> None:
    """
    nf-core/funcscan

    Sample Description
    """

    pvc_name: str = initialize()
    nextflow_runtime(pvc_name=pvc_name, input=input, outdir=outdir, email=email, multiqc_title=multiqc_title, run_amp_screening=run_amp_screening, run_arg_screening=run_arg_screening, run_bgc_screening=run_bgc_screening, run_taxa_classification=run_taxa_classification, taxa_classification_tool=taxa_classification_tool, taxa_classification_mmseqs_db=taxa_classification_mmseqs_db, taxa_classification_mmseqs_db_id=taxa_classification_mmseqs_db_id, taxa_classification_mmseqs_db_savetmp=taxa_classification_mmseqs_db_savetmp, taxa_classification_mmseqs_taxonomy_savetmp=taxa_classification_mmseqs_taxonomy_savetmp, taxa_classification_mmseqs_taxonomy_searchtype=taxa_classification_mmseqs_taxonomy_searchtype, taxa_classification_mmseqs_taxonomy_lcaranks=taxa_classification_mmseqs_taxonomy_lcaranks, taxa_classification_mmseqs_taxonomy_taxlineage=taxa_classification_mmseqs_taxonomy_taxlineage, taxa_classification_mmseqs_taxonomy_sensitivity=taxa_classification_mmseqs_taxonomy_sensitivity, taxa_classification_mmseqs_taxonomy_orffilters=taxa_classification_mmseqs_taxonomy_orffilters, taxa_classification_mmseqs_taxonomy_lcamode=taxa_classification_mmseqs_taxonomy_lcamode, taxa_classification_mmseqs_taxonomy_votemode=taxa_classification_mmseqs_taxonomy_votemode, annotation_tool=annotation_tool, save_annotations=save_annotations, annotation_bakta_db=annotation_bakta_db, annotation_bakta_db_downloadtype=annotation_bakta_db_downloadtype, annotation_bakta_singlemode=annotation_bakta_singlemode, annotation_bakta_mincontiglen=annotation_bakta_mincontiglen, annotation_bakta_translationtable=annotation_bakta_translationtable, annotation_bakta_gram=annotation_bakta_gram, annotation_bakta_complete=annotation_bakta_complete, annotation_bakta_renamecontigheaders=annotation_bakta_renamecontigheaders, annotation_bakta_compliant=annotation_bakta_compliant, annotation_bakta_trna=annotation_bakta_trna, annotation_bakta_tmrna=annotation_bakta_tmrna, annotation_bakta_rrna=annotation_bakta_rrna, annotation_bakta_ncrna=annotation_bakta_ncrna, annotation_bakta_ncrnaregion=annotation_bakta_ncrnaregion, annotation_bakta_crispr=annotation_bakta_crispr, annotation_bakta_skipcds=annotation_bakta_skipcds, annotation_bakta_pseudo=annotation_bakta_pseudo, annotation_bakta_skipsorf=annotation_bakta_skipsorf, annotation_bakta_gap=annotation_bakta_gap, annotation_bakta_ori=annotation_bakta_ori, annotation_bakta_activate_plot=annotation_bakta_activate_plot, annotation_prokka_singlemode=annotation_prokka_singlemode, annotation_prokka_rawproduct=annotation_prokka_rawproduct, annotation_prokka_kingdom=annotation_prokka_kingdom, annotation_prokka_gcode=annotation_prokka_gcode, annotation_prokka_mincontiglen=annotation_prokka_mincontiglen, annotation_prokka_evalue=annotation_prokka_evalue, annotation_prokka_coverage=annotation_prokka_coverage, annotation_prokka_cdsrnaolap=annotation_prokka_cdsrnaolap, annotation_prokka_rnammer=annotation_prokka_rnammer, annotation_prokka_compliant=annotation_prokka_compliant, annotation_prokka_addgenes=annotation_prokka_addgenes, annotation_prokka_retaincontigheaders=annotation_prokka_retaincontigheaders, annotation_prodigal_singlemode=annotation_prodigal_singlemode, annotation_prodigal_closed=annotation_prodigal_closed, annotation_prodigal_transtable=annotation_prodigal_transtable, annotation_prodigal_forcenonsd=annotation_prodigal_forcenonsd, annotation_pyrodigal_singlemode=annotation_pyrodigal_singlemode, annotation_pyrodigal_closed=annotation_pyrodigal_closed, annotation_pyrodigal_transtable=annotation_pyrodigal_transtable, annotation_pyrodigal_forcenonsd=annotation_pyrodigal_forcenonsd, save_db=save_db, amp_skip_amplify=amp_skip_amplify, amp_skip_ampir=amp_skip_ampir, amp_ampir_model=amp_ampir_model, amp_ampir_minlength=amp_ampir_minlength, amp_run_hmmsearch=amp_run_hmmsearch, amp_hmmsearch_models=amp_hmmsearch_models, amp_hmmsearch_savealignments=amp_hmmsearch_savealignments, amp_hmmsearch_savetargets=amp_hmmsearch_savetargets, amp_hmmsearch_savedomains=amp_hmmsearch_savedomains, amp_skip_macrel=amp_skip_macrel, amp_ampcombi_db=amp_ampcombi_db, amp_ampcombi_parsetables_cutoff=amp_ampcombi_parsetables_cutoff, amp_ampcombi_parsetables_aalength=amp_ampcombi_parsetables_aalength, amp_ampcombi_parsetables_dbevalue=amp_ampcombi_parsetables_dbevalue, amp_ampcombi_parsetables_hmmevalue=amp_ampcombi_parsetables_hmmevalue, amp_ampcombi_parsetables_windowstopcodon=amp_ampcombi_parsetables_windowstopcodon, amp_ampcombi_parsetables_windowtransport=amp_ampcombi_parsetables_windowtransport, amp_ampcombi_parsetables_removehitswostopcodons=amp_ampcombi_parsetables_removehitswostopcodons, amp_ampcombi_cluster_covmode=amp_ampcombi_cluster_covmode, amp_ampcombi_cluster_sensitivity=amp_ampcombi_cluster_sensitivity, amp_ampcombi_cluster_minmembers=amp_ampcombi_cluster_minmembers, amp_ampcombi_cluster_mode=amp_ampcombi_cluster_mode, amp_ampcombi_cluster_coverage=amp_ampcombi_cluster_coverage, amp_ampcombi_cluster_seqid=amp_ampcombi_cluster_seqid, amp_ampcombi_cluster_removesingletons=amp_ampcombi_cluster_removesingletons, arg_skip_amrfinderplus=arg_skip_amrfinderplus, arg_amrfinderplus_db=arg_amrfinderplus_db, arg_amrfinderplus_identmin=arg_amrfinderplus_identmin, arg_amrfinderplus_coveragemin=arg_amrfinderplus_coveragemin, arg_amrfinderplus_translationtable=arg_amrfinderplus_translationtable, arg_amrfinderplus_plus=arg_amrfinderplus_plus, arg_amrfinderplus_name=arg_amrfinderplus_name, arg_skip_deeparg=arg_skip_deeparg, arg_deeparg_db=arg_deeparg_db, arg_deeparg_db_version=arg_deeparg_db_version, arg_deeparg_model=arg_deeparg_model, arg_deeparg_minprob=arg_deeparg_minprob, arg_deeparg_alignmentevalue=arg_deeparg_alignmentevalue, arg_deeparg_alignmentidentity=arg_deeparg_alignmentidentity, arg_deeparg_alignmentoverlap=arg_deeparg_alignmentoverlap, arg_deeparg_numalignmentsperentry=arg_deeparg_numalignmentsperentry, arg_skip_fargene=arg_skip_fargene, arg_fargene_hmmmodel=arg_fargene_hmmmodel, arg_fargene_savetmpfiles=arg_fargene_savetmpfiles, arg_fargene_score=arg_fargene_score, arg_fargene_minorflength=arg_fargene_minorflength, arg_fargene_orffinder=arg_fargene_orffinder, arg_fargene_translationformat=arg_fargene_translationformat, arg_skip_rgi=arg_skip_rgi, arg_rgi_db=arg_rgi_db, arg_rgi_savejson=arg_rgi_savejson, arg_rgi_savetmpfiles=arg_rgi_savetmpfiles, arg_rgi_alignmenttool=arg_rgi_alignmenttool, arg_rgi_includeloose=arg_rgi_includeloose, arg_rgi_includenudge=arg_rgi_includenudge, arg_rgi_lowquality=arg_rgi_lowquality, arg_rgi_data=arg_rgi_data, arg_rgi_split_prodigal_jobs=arg_rgi_split_prodigal_jobs, arg_skip_abricate=arg_skip_abricate, arg_abricate_db_id=arg_abricate_db_id, arg_abricate_db=arg_abricate_db, arg_abricate_minid=arg_abricate_minid, arg_abricate_mincov=arg_abricate_mincov, arg_hamronization_summarizeformat=arg_hamronization_summarizeformat, arg_skip_argnorm=arg_skip_argnorm, bgc_mincontiglength=bgc_mincontiglength, bgc_savefilteredcontigs=bgc_savefilteredcontigs, bgc_skip_antismash=bgc_skip_antismash, bgc_antismash_db=bgc_antismash_db, bgc_antismash_installdir=bgc_antismash_installdir, bgc_antismash_contigminlength=bgc_antismash_contigminlength, bgc_antismash_cbgeneral=bgc_antismash_cbgeneral, bgc_antismash_cbknownclusters=bgc_antismash_cbknownclusters, bgc_antismash_cbsubclusters=bgc_antismash_cbsubclusters, bgc_antismash_ccmibig=bgc_antismash_ccmibig, bgc_antismash_smcogtrees=bgc_antismash_smcogtrees, bgc_antismash_hmmdetectionstrictness=bgc_antismash_hmmdetectionstrictness, bgc_antismash_pfam2go=bgc_antismash_pfam2go, bgc_antismash_rre=bgc_antismash_rre, bgc_antismash_taxon=bgc_antismash_taxon, bgc_antismash_tfbs=bgc_antismash_tfbs, bgc_skip_deepbgc=bgc_skip_deepbgc, bgc_deepbgc_db=bgc_deepbgc_db, bgc_deepbgc_score=bgc_deepbgc_score, bgc_deepbgc_minnucl=bgc_deepbgc_minnucl, bgc_deepbgc_minproteins=bgc_deepbgc_minproteins, multiqc_methods_description=multiqc_methods_description)

