#!/usr/bin/env python3
"""Build source-redacted PK B127 segment 1387 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1970,
    1972,
    1973,
    1983,
    1984,
    1985,
    1986,
    1990,
    1991,
)
TARGET_COORDINATES = (
    "15:1970:1",
    "15:1970:3",
    "15:1972:1",
    "15:1973:1",
    "15:1983:1",
    "15:1984:2",
    "15:1985:1",
    "15:1986:1",
    "15:1986:2",
    "15:1990:1",
    "15:1991:1",
)
TRANSLATIONS = {
    "15:1970:1": ". 순조롭게 보이는 상태",
    "15:1970:3": "\n앞으로:",
    "15:1972:1": "일 정도 걸릴 것으로 사료되옵니다",
    "15:1973:1": "일 정도로 예상합니다",
    "15:1983:1": "일 정도 걸린다고 예상",
    "15:1984:2": "일 정도는 기다려 주시옵소서",
    "15:1985:1": "일 정도는 더 걸린다고 예상",
    "15:1986:1": "\n앞으로:",
    "15:1986:2": "일 정도 걸린다고 예상",
    "15:1990:1": "일 정도 걸릴 것으로 봅니다",
    "15:1991:1": "일 정도 기다려 주시옵소서",
}
EXPECTED_ARITY = {
    1970: 5,
    1972: 2,
    1973: 2,
    1983: 2,
    1984: 3,
    1985: 3,
    1986: 3,
    1990: 2,
    1991: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1970:0",
    "15:1970:2",
    "15:1970:4",
    "15:1972:0",
    "15:1973:0",
    "15:1983:0",
    "15:1984:0",
    "15:1985:0",
    "15:1985:2",
    "15:1986:0",
    "15:1990:0",
    "15:1991:0",
)
PREFILL_COMPANION_DONOR = {
    "15:1970:0": "15:1940:0",
    "15:1970:2": "15:1940:2",
    "15:1970:4": "15:1940:4",
    "15:1972:0": "15:1942:0",
    "15:1973:0": "15:1943:0",
    "15:1983:0": "15:1953:0",
    "15:1984:0": "15:1954:0",
    "15:1985:0": "15:1955:0",
    "15:1985:2": "15:1955:2",
    "15:1986:0": "15:1956:0",
    "15:1990:0": "15:1960:0",
    "15:1991:0": "15:1961:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:1984:1",)
EXACT_BASE_DONOR = {
    1970: (15, 1940),
    1972: (15, 1942),
    1973: (15, 1943),
    1983: (15, 1953),
    1985: (15, 1955),
    1986: (15, 1956),
    1990: (15, 1960),
    1991: (15, 1961),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id != 1984
    },
    1984: (
        "15:1954:0",
        "15:1954:2",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    1970: (),
    1972: ((15, 1942),),
    1973: ((15, 1943),),
    1983: (),
    1984: (),
    1985: (),
    1986: (),
    1990: ((15, 1960),),
    1991: ((15, 1961),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    1970: ((15, 1940),),
    1972: ((15, 1942),),
    1973: ((15, 1943),),
    1983: ((15, 1953),),
    1984: ((15, 1954),),
    1985: ((15, 1955),),
    1986: ((15, 1956),),
    1990: ((15, 1960),),
    1991: ((15, 1961),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1970: ((178, 568, 310, 1126), ("0232",)),
    1972: ((), ("0232",)),
    1973: ((), ("0232",)),
    1983: ((1126,), ("0232",)),
    1984: ((1066,), ("0232",)),
    1985: ((1090, 910), ("0232",)),
    1986: ((310, 1126), ("0232",)),
    1990: ((), ("0232",)),
    1991: ((), ("0232",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1387,
    queue_start=134,
    queue_stop=199,
    slice_first="15:1969:2",
    slice_last="15:1998:1",
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
    source_call_roots=(
        178,
        310,
        568,
        910,
        1066,
        1090,
        1126,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1950, 1999)
    ),
    speaker_style=(
        (1970, "formal_midpoint_progress_report"),
        (1972, "humble_progress_duration_estimate"),
        (1973, "neutral_progress_duration_estimate"),
        (1983, "polite_early_progress_wait_request"),
        (1984, "assured_archaic_completion_request"),
        (1985, "formal_result_wait_request"),
        (1986, "formal_just_started_progress_report"),
        (1990, "deliberative_work_duration_estimate"),
        (1991, "resolute_formal_completion_promise"),
    ),
    terminology_policy=(
        ("mission", "임무"),
        ("work", "작업"),
        ("progress", "진행"),
        ("completion", "완료"),
        ("perform", "수행"),
        ("accomplish", "완수"),
        ("remaining period", "남은 기간"),
        ("result", "결과"),
        ("commence", "착수"),
        ("humble estimate", "사료되옵니다"),
        ("day count token delimiter", ":"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B127 queue ordinals 134 through 198 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; eight complete records reuse "
        "approved completed Base Korean assemblies selected by raw, literal "
        "and operand-masked source identity with explicit exact donors, "
        "while the assured-completion record uses the same Base assembly "
        "through two visible semantic references because its newline-only "
        "fragment has no promoted decision row; Base runtime and VM state "
        "are never inherited; mission, work, progress, completion, "
        "performance, accomplishment, remaining period, result, "
        "commencement, humble estimation, dynamic day-count delimiters and "
        "each speaker register retain established project and historical "
        "terminology; direct calls, the inline day-count token, protected "
        "outer whitespace, newlines, gaps, literal arity, terminators, all "
        "twelve same-record prefills, the hidden newline, all fifty-four "
        "slice prefills, complete assemblies, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "reciprocal S1385 and S1386 decisions and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256": (
            "E1A8B7C31AFD7CD33800E1FE68E170AEA554354C2299B03ED08B73C6FD95E060"
        ),
        "expected_queue_slice_sha256": (
            "E3DB7B645D8627BDB9B530422DEE362F0C458EF971ADFFD63628B1D039A14F4B"
        ),
        "expected_prefilled_coordinate_sha256": (
            "ECA8C2C73C8A85795A2C9A7311765C9F530A755F06699660A26D4706A4F14BAD"
        ),
        "expected_prefill_slice_context_sha256": (
            "9C01669217F20F17A8BEEC7B3E1AABC3AAD3B1B939FBA15DB019C3DEAC6BC7C9"
        ),
        "expected_target_coordinate_sha256": (
            "6DD984F6EA9CF070B5468D2E160A3C03FC24CFE79330874CEBDA4F8248969025"
        ),
        "expected_source_target_sha256": (
            "D6F1340FFB073792F64B0779EA8F230D0A3147199F6C079C8776343A0659080E"
        ),
        "expected_current_target_sha256": (
            "39FED45967F359C80DFE18AF9D42B5F551DD46B7BDF76DD84953BD9A2B98AFCE"
        ),
        "expected_context_corpus_sha256": (
            "0E0A0B7D02FDF30847036712F1F4A5AE2366187E8C63CD48F3DA5300D602E45E"
        ),
        "expected_gap_contract_sha256": (
            "08326C9B4CE930D6BCB801288860ACDEF659E1B870E2F7522C34C8E6303A7CA3"
        ),
        "expected_boundary_sha256": (
            "17F8A1B33487C79F5BBCEBA237F5C939E715D3819F8C128B1CA001C2D5F26F3A"
        ),
        "expected_runtime_control_sha256": (
            "0DFA79BF3BB2ED27D442598170051C73434A1606A8C712F07CC3292776818ED4"
        ),
        "expected_base_search_sha256": (
            "A2B9BBD898351A335267017D492AAC63CE93A8769FC2512C140618CA882A68E8"
        ),
        "expected_complete_assembly_sha256": (
            "C8F0BE94731C80B956E1884C6FE879CBA48BDFE18E30B9166BCC00E12C8BF68F"
        ),
        "expected_call_graph_sha256": (
            "44980759870C20216A28BA192F3A430E86A0C4BBB055F6E0A2ACE52B7203B7FD"
        ),
        "expected_speaker_style_sha256": (
            "C6E9CA7CDA7176EF226B218B7156EE0180977E2C561978F0D6A0DBD3F0880D0F"
        ),
        "expected_terminology_policy_sha256": (
            "07D19A48467594300E5FDA5B7EAE361688F8D8A81F61CD7FF1987566247D3DEE"
        ),
        "expected_translation_policy_sha256": (
            "3E8F5491B1B3F47BCA84693A5C1C778AD07ED74315B97A62D739EBCFFC8EA5C6"
        ),
        "expected_candidate_sha256": (
            "7CF66DB19DDD6ADE10F18F2F7A430FC9129330314411A1DDA392512C4FA263E9"
        ),
        "expected_combined_slice_candidate_sha256": (
            "041881970F4CFC34F35A55BC721FFCA4CD8912031C646751681ECAB2C0BB1769"
        ),
        "expected_combined_changed_literal_count": 63,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B127_S1387",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1387.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1385.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1386.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B127",
    "queue_row_count": 71,
    "queue_visible_count": 199,
    "queue_first": "15:1928:0",
    "queue_last": "15:1998:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
