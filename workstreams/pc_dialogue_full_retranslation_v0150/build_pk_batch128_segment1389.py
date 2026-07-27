#!/usr/bin/env python3
"""Build source-redacted PK B128 segment 1389 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2034:1",
    "15:2039:0",
    "15:2039:1",
    "15:2053:1",
    "15:2054:1",
    "15:2062:1",
    "15:2065:1",
)
TRANSLATIONS = {
    "15:2034:1": "을(를) 건의",
    "15:2039:0": "공략 준비를 위해\n",
    "15:2039:1": "의 실행을 건의",
    "15:2053:1": "을(를) 건의",
    "15:2054:1": "의 실행을 허락해 주시옵소서\n",
    "15:2062:1": "의 실행을 허락해 주시오",
    "15:2065:1": "을(를) 추진하고자 하오",
}
TARGET_RECORD_IDS = (
    2034,
    2039,
    2053,
    2054,
    2062,
    2065,
)
EXPECTED_ARITY = {
    2034: 2,
    2039: 2,
    2053: 2,
    2054: 3,
    2062: 2,
    2065: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2034:0",
    "15:2053:0",
    "15:2054:2",
    "15:2062:0",
    "15:2065:0",
)
PREFILL_COMPANION_DONOR = {
    "15:2034:0": "15:2004:0",
    "15:2053:0": "15:2023:0",
    "15:2054:2": "15:2024:2",
    "15:2062:0": "15:2032:0",
    "15:2065:0": "15:2035:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2054:0",
)
EXACT_BASE_DONOR = {
    2034: (15, 2004),
    2039: (15, 2009),
    2053: (15, 2023),
    2062: (15, 2032),
    2065: (15, 2035),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in EXACT_BASE_DONOR
    },
    2054: ("15:2024:1", "15:2024:2"),
}
EXPECTED_BASE_RAW_MATCHES = {
    2034: ((15, 2004), (15, 2088)),
    2039: (),
    2053: (),
    2054: ((15, 2024), (15, 2108)),
    2062: ((15, 2032), (15, 2116)),
    2065: ((15, 2035), (15, 2119)),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    2034: ((15, 2004), (15, 2088)),
    2039: (
        (15, 1999),
        (15, 2009),
        (15, 2083),
        (15, 2093),
    ),
    2053: ((15, 2023), (15, 2107)),
    2054: ((15, 2024), (15, 2108)),
    2062: ((15, 2032), (15, 2116)),
    2065: ((15, 2035), (15, 2119)),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2034: ((142,), ("026432",)),
    2039: ((466,), ("026432",)),
    2053: ((466,), ("025032",)),
    2054: ((), ("025032",)),
    2062: ((), ()),
    2065: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1389,
    queue_start=67,
    queue_stop=134,
    slice_first="15:2033:1",
    slice_last="15:2066:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(
        HIDDEN_CURRENT_COMPANION_COORDINATES
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(142, 466),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1985, 2105)
    ),
    speaker_style=(
        (2034, "formal_siege_preparation_recommendation"),
        (2039, "formal_siege_preparation_execution_recommendation"),
        (2053, "formal_war_preparation_recommendation"),
        (2054, "formal_war_support_authorization_request"),
        (2062, "formal_unavoidable_war_measure_authorization"),
        (2065, "formal_off_policy_measure_proposal"),
    ),
    terminology_policy=(
        ("siege", "공략"),
        ("preparation", "대비, 준비"),
        ("recommendation", "건의"),
        ("execution", "실행"),
        ("fight", "싸움"),
        ("authorization", "허락"),
        ("our clan", "우리 가문"),
        ("guideline", "지침"),
        ("advance measure", "추진"),
        ("dynamic object particle", "을(를)"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B128 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; five complete "
        "records reuse approved completed Base Korean assemblies selected "
        "by raw, literal and operand-masked source identity with explicit "
        "exact donors; the source-identical authorization record uses its "
        "two populated completed Base rows as semantic context because its "
        "leading empty literal has no translatable Base decision row, while "
        "that hidden empty literal remains source-identical and participates "
        "in complete-record assembly; Base runtime and VM state are never "
        "inherited; sieges, preparation, recommendations, execution, fights, "
        "authorization, our clan, guidelines and advancing measures retain "
        "established historical project wording and formal advisory "
        "registers; calls, inline measure and force tokens, protected outer "
        "whitespace, line breaks, particles, terminators, complete record "
        "arity, all sixty slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=5,
    pins={
        "expected_queue_universe_sha256": (
            "354A482D4069DE0E482F6258A08E16B37D2368C0DA8D1ADA17C9CC39FEC679B9"
        ),
        "expected_queue_slice_sha256": (
            "6136996DD39B7B720AA3F336A0CEDE1F722EE692A10FB8B87D78956DBD801010"
        ),
        "expected_prefilled_coordinate_sha256": (
            "3923DAF72535B13F94867A79BF75D7B807B23BBA4A51C181928ACE027C35DCFF"
        ),
        "expected_prefill_slice_context_sha256": (
            "EAE90A158E604A295D38FB9D7E8A0D6A72A77436BD031B4F54C2BD9FBB8261F4"
        ),
        "expected_target_coordinate_sha256": (
            "041719EDED0982330E54382BC98E573F874CFA76BB5993E17426C1B953307943"
        ),
        "expected_source_target_sha256": (
            "8EAE5FCFEBE3C6A3314F2D8606E9D67789CED9B98AFD99F2B2D4E9541415BA97"
        ),
        "expected_current_target_sha256": (
            "AF656FE6F2B7B3DA3595BE6E6C1F3453C08919D39FCFB5E96345EDBB8ABD6579"
        ),
        "expected_context_corpus_sha256": (
            "4E20716A3F245BABD767D962C2E7918428FC6142F0379F24CAC0F8815B0D9851"
        ),
        "expected_gap_contract_sha256": (
            "F076F399F0632D98EC393D7EE74584F5C92C0E2FF0DCC9D95610A14F4F6DC42C"
        ),
        "expected_boundary_sha256": (
            "45DCB4F3C603F46EC2A7FC20A7F8BDECD9A82465DE103BED762D62EDAB536F79"
        ),
        "expected_runtime_control_sha256": (
            "BFFB5C59D19FF4D71D7A082FA1718A9A100ECA02E74A8B80A85342C6C0C7AC64"
        ),
        "expected_base_search_sha256": (
            "3E4D8BC8B90D08B61DE573920A4C11C48E955E2D2A29518F0132BB8BA57D387A"
        ),
        "expected_complete_assembly_sha256": (
            "218A3FEB4CF647D610A5721C7CD725D38645CEB3BBD436CD251FEC04478026CC"
        ),
        "expected_call_graph_sha256": (
            "BFDD8CF2FF75AF3B0C9430835EE7F2CF62B779D06D9EF2B59380F89519A2B46C"
        ),
        "expected_speaker_style_sha256": (
            "79AC248902E188941E8AD6D680CA797E499D106806F7DCD9D1631C68CC3C4F08"
        ),
        "expected_terminology_policy_sha256": (
            "D5BE656571D222BAB5CA02C3EF0A9718C176DB4B9B4AC9A1063262FDA28FC853"
        ),
        "expected_translation_policy_sha256": (
            "B0A8057738C1FFB86B48EB8AFB407BDE098BCA91D743C570301CB87D3B64E3D7"
        ),
        "expected_candidate_sha256": (
            "9ACA62FBB44CEC0E185B37384A44B493C50068C91D9FF83D45148963B98B58F6"
        ),
        "expected_combined_slice_candidate_sha256": (
            "C6312C25F78DABADFC0E25DFC47D1CA029AF518A3761C0B4B1107B22ACCAB95E"
        ),
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B128_S1389",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1389.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1388.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1390.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B128",
    "queue_row_count": 96,
    "queue_visible_count": 199,
    "queue_first": "15:1999:0",
    "queue_last": "15:2094:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
