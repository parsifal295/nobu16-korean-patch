#!/usr/bin/env python3
"""Build source-redacted PK B074 segment 1227 residual decisions."""

from pathlib import Path

from build_pk_batch074_common import make_config, run


SCRIPT = Path(__file__).resolve()
CONFIG = make_config(
    script=SCRIPT,
    segment=1227,
    queue_start=67,
    queue_stop=134,
    slice_first="8:623:0",
    slice_last="8:682:0",
    target_coordinates=(
        "8:636:0",
        "8:662:0",
    ),
    translations={
        "8:636:0": "께서는 「",
        "8:662:0": "오오, 「",
    },
    target_record_ids=(636, 662),
    expected_arity={
        636: 2,
        662: 2,
    },
    prefill_companion_coordinates=(
        "8:636:1",
        "8:662:1",
    ),
    prefill_companion_donor={
        "8:636:1": "8:624:1",
        "8:662:1": "8:650:1",
    },
    semantic_base_context={
        636: ("8:624:0", "8:624:1"),
        662: ("8:650:0", "8:650:1"),
    },
    expected_base_raw_matches={
        636: ((8, 624),),
        662: ((8, 650),),
    },
    expected_controls_by_record={
        636: ((8, 8), ()),
        662: ((1,), ()),
    },
    source_call_roots=(1, 8),
    boundary_record_keys=tuple(
        (8, record_id)
        for record_id in (
            622, 623, 624, 625, 635, 636, 637,
            649, 650, 651, 661, 662, 663, 681, 682, 683,
        )
    ),
    speaker_style=(
        (636, "deferential_chigyo_relinquishment"),
        (662, "shocked_chigyo_reduction_lament"),
    ),
    terminology_policy=(
        ("chigyo stipend land", "지행"),
        ("relinquish", "내놓다"),
        ("deferential lord reference", "께서는"),
        ("dynamic person or lord", "「」"),
    ),
    basis=(
        "pristine PK Japanese is authoritative and the blank PK English, "
        "Simplified Chinese and Traditional Chinese slots were explicitly "
        "reviewed; two raw-identical completed Base records supply manually "
        "selected semantic wording only, while PK runtime and VM state are "
        "never inherited; two residuals and two exact-prefill companions form "
        "two complete records; historically specific chigyo terminology, "
        "deferential and distressed registers, dynamic persons, calls, "
        "protected whitespace, gaps, boundaries, two-run reproduction, "
        "tamper rejection, reverse overlays, outside-scope identity and Steam "
        "read-only state are guarded"
    ),
    pins={
        "expected_queue_universe_sha256":
        "AD7463BFB5BF319B21F2E4B813FD175CEF956C86397E29689D48156AD1726FC7",
        "expected_queue_slice_sha256":
        "884C62E29B0C550C2225514F89816B51A20BF5808B2714EA0E4E4BAAE9B1B2A8",
        "expected_prefilled_coordinate_sha256":
        "9A7AE3D022B322BE1A208A36E2F79425BA6081BE8703B8F3F8CB1C2414BE2879",
        "expected_prefill_slice_context_sha256":
        "049D8B4F788E55DAFDA6D346CCC0FEE647620310A0259DFCA30417011A2E1FA6",
        "expected_target_coordinate_sha256":
        "CD56FB8750F9358469430B0A45A959460260A9630C2CE2E0CA6255759221A8B3",
        "expected_source_target_sha256":
        "115C852F78D149F868940182BFB68430C5260EF4707CA93296AF40EDB19ADAC7",
        "expected_current_target_sha256":
        "1BADA45998CD4A6E54B36672D9210DCF78227FC73593BF8B73929E830934421C",
        "expected_context_corpus_sha256":
        "E7F745C4E880B90BF50A1B66340CFB2DF04CCF441ECDDDB6EB033BD08BC4147F",
        "expected_gap_contract_sha256":
        "A4AF7F4991767EF1A170D1176E8538D09133E57AF8E1886A9B50BA304FA6967E",
        "expected_boundary_sha256":
        "2B3A211D7E253245F1D79829CB4D7B73341E0704604B687E2610ABCC8E8D636D",
        "expected_runtime_control_sha256":
        "AFE96EE1C81440865FBC4A0CD683358C10C91D1A927255F68F6A5E8DC7F841E9",
        "expected_base_search_sha256":
        "0433EB18BEFC54B7A7AC7650B6A2E56F19DF3ED27AA3EC7E48F4ED7869E76E2E",
        "expected_complete_assembly_sha256":
        "F81DD1563980B2F653F347BEA564D8A2644A5B3DDC68CCF553094AC5C1A227C3",
        "expected_call_graph_sha256":
        "B7FEFC0E69503FD7AC6DCB557D7714DA2EC745739A13C3E806D541BE9BF5BC14",
        "expected_speaker_style_sha256":
        "ACC72D27B4DDA174EB937273C7C2C742A8A35B781884797D37EB8563E1D4693F",
        "expected_terminology_policy_sha256":
        "21B4C9649542566130D27F5B8BC403CF3B294BE572495BAFA43C7D8D682721F0",
        "expected_translation_policy_sha256":
        "4B77448993DB0F91B44FCB8192E88FD22C0D91385C52BAF6AC8445CC0FFFB8A2",
        "expected_candidate_sha256":
        "45B7F0576B4CC8ED7F228EC44A4B2893C7F8544DBEA8741D511FD596CB93C83C",
        "expected_combined_slice_candidate_sha256":
        "E525584F46C9DA5FD020C7EFDC4326B05CFD8A8F794F41D279DF71C6C4CEA711",
        "expected_combined_changed_literal_count": 61,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
