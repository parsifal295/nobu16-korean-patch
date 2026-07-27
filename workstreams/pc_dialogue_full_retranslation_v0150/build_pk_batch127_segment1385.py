#!/usr/bin/env python3
"""Build source-redacted PK B127 segment 1385 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1928:2",
    "15:1929:0",
    "15:1932:0",
    "15:1943:2",
    "15:1943:3",
    "15:1943:4",
    "15:1944:2",
    "15:1944:3",
    "15:1944:4",
    "15:1944:5",
    "15:1945:2",
    "15:1945:3",
    "15:1945:4",
    "15:1946:2",
    "15:1946:3",
    "15:1946:4",
    "15:1947:2",
    "15:1947:3",
    "15:1947:4",
    "15:1947:5",
    "15:1948:2",
    "15:1948:3",
    "15:1948:4",
    "15:1949:4",
    "15:1950:2",
    "15:1950:5",
)
TRANSLATIONS = {
    "15:1928:2": "일 정도",
    "15:1929:0": "앞으로:",
    "15:1932:0": "앞으로:",
    "15:1943:2": "개월 안에 목표:",
    "15:1943:3": "성\n현재:",
    "15:1943:4": "성",
    "15:1944:2": "년",
    "15:1944:3": "개월 안에 목표:",
    "15:1944:4": "성\n현재:",
    "15:1944:5": "성",
    "15:1945:2": "일 안에 목표:",
    "15:1945:3": "성\n현재:",
    "15:1945:4": "성",
    "15:1946:2": "개월 안에 목표:",
    "15:1946:3": "명\n현재:",
    "15:1946:4": "명",
    "15:1947:2": "년",
    "15:1947:3": "개월 안에 목표:",
    "15:1947:4": "명\n현재:",
    "15:1947:5": "명",
    "15:1948:2": "일 안에 목표:",
    "15:1948:3": "명\n현재:",
    "15:1948:4": "명",
    "15:1949:4": "(LV)",
    "15:1950:2": "년",
    "15:1950:5": "(LV)",
}
TARGET_RECORD_IDS = (
    1928,
    1929,
    1932,
    1943,
    1944,
    1945,
    1946,
    1947,
    1948,
    1949,
    1950,
)
EXPECTED_ARITY = {
    1928: 3,
    1929: 3,
    1932: 2,
    1943: 5,
    1944: 6,
    1945: 5,
    1946: 5,
    1947: 6,
    1948: 5,
    1949: 5,
    1950: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1928:0",
    "15:1928:1",
    "15:1929:1",
    "15:1929:2",
    "15:1932:1",
    "15:1943:0",
    "15:1944:0",
    "15:1945:0",
    "15:1946:0",
    "15:1947:0",
    "15:1948:0",
    "15:1949:0",
    "15:1949:2",
    "15:1949:3",
    "15:1950:0",
    "15:1950:3",
    "15:1950:4",
)
PREFILL_COMPANION_DONOR = {
    "15:1928:0": "15:1898:0",
    "15:1928:1": "15:1898:1",
    "15:1929:1": "15:1899:1",
    "15:1929:2": "15:1899:2",
    "15:1932:1": "15:1902:1",
    "15:1943:0": "15:1913:0",
    "15:1944:0": "15:1914:0",
    "15:1945:0": "15:1915:0",
    "15:1946:0": "15:1916:0",
    "15:1947:0": "15:1917:0",
    "15:1948:0": "15:1918:0",
    "15:1949:0": "15:1919:0",
    "15:1949:2": "15:1919:2",
    "15:1949:3": "15:1919:3",
    "15:1950:0": "15:1920:0",
    "15:1950:3": "15:1920:3",
    "15:1950:4": "15:1920:4",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:1943:1",
    "15:1944:1",
    "15:1945:1",
    "15:1946:1",
    "15:1947:1",
    "15:1948:1",
    "15:1949:1",
    "15:1950:1",
)
EXACT_BASE_DONOR = {
    1928: (15, 1898),
    1929: (15, 1899),
    1932: (15, 1902),
}
SEMANTIC_BASE_CONTEXT = {
    1928: (),
    1929: (),
    1932: (),
    1943: (
        "15:1913:0",
        "15:1913:2",
        "15:1913:3",
        "15:1913:4",
    ),
    1944: (
        "15:1914:0",
        "15:1914:2",
        "15:1914:3",
        "15:1914:4",
        "15:1914:5",
    ),
    1945: (
        "15:1915:0",
        "15:1915:2",
        "15:1915:3",
        "15:1915:4",
    ),
    1946: (
        "15:1916:0",
        "15:1916:2",
        "15:1916:3",
        "15:1916:4",
    ),
    1947: (
        "15:1917:0",
        "15:1917:2",
        "15:1917:3",
        "15:1917:4",
        "15:1917:5",
    ),
    1948: (
        "15:1918:0",
        "15:1918:2",
        "15:1918:3",
        "15:1918:4",
    ),
    1949: (
        "15:1919:0",
        "15:1919:2",
        "15:1919:3",
        "15:1919:4",
    ),
    1950: (
        "15:1920:0",
        "15:1920:2",
        "15:1920:3",
        "15:1920:4",
        "15:1920:5",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    1928: (),
    1929: (),
    1932: ((15, 1902),),
    1943: (),
    1944: (),
    1945: (),
    1946: (),
    1947: (),
    1948: (),
    1949: (),
    1950: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    1928: ((15, 1898),),
    1929: ((15, 1899),),
    1932: ((15, 1902),),
    1943: ((15, 1913),),
    1944: ((15, 1914),),
    1945: ((15, 1915),),
    1946: ((15, 1916),),
    1947: ((15, 1917),),
    1948: ((15, 1918),),
    1949: ((15, 1919),),
    1950: ((15, 1920),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1928: ((910, 568), ("0232",)),
    1929: ((1174, 1066), ("0232",)),
    1932: ((), ("0232",)),
    1943: ((1162, 550), ("0235", "0232", "0233")),
    1944: ((1162, 550), ("0234", "0235", "0232", "0233")),
    1945: ((1162, 550), ("0236", "0232", "0233")),
    1946: ((1162, 550), ("0235", "0232", "0233")),
    1947: ((1162, 550), ("0234", "0235", "0232", "0233")),
    1948: ((1162, 550), ("0236", "0232", "0233")),
    1949: ((1066, 550), ("0235", "0232", "0233")),
    1950: ((1066, 550), ("0234", "0235", "0232", "0233")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1385,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1928:0",
    slice_last="15:1950:5",
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
        550,
        568,
        910,
        1066,
        1162,
        1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1898, 1999)
    ),
    speaker_style=(
        (1928, "neutral_result_wait_duration_estimate"),
        (1929, "formal_result_report_duration_estimate"),
        (1932, "neutral_work_completion_duration_estimate"),
        (1943, "formal_castle_expansion_month_target"),
        (1944, "formal_castle_expansion_year_month_target"),
        (1945, "formal_castle_expansion_day_target"),
        (1946, "formal_retainer_expansion_month_target"),
        (1947, "formal_retainer_expansion_year_month_target"),
        (1948, "formal_retainer_expansion_day_target"),
        (1949, "formal_policy_level_month_target"),
        (1950, "formal_policy_level_year_month_target"),
    ),
    terminology_policy=(
        ("result", "결과"),
        ("work", "작업"),
        ("completion", "완료"),
        ("controlled castle", "지배하는 성"),
        ("retainer", "가신"),
        ("policy issue level", "정책 발령 수준"),
        ("raise level", "제고"),
        ("goal", "목표"),
        ("current value", "현재"),
        ("person counter", "명"),
        ("level notation", "(LV)"),
        ("dynamic count token delimiter", ":"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B127 queue ordinals zero through "
        "sixty-six and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; the first three "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity with "
        "explicit exact donors, while the eight castle, retainer and policy "
        "target records reuse the matching Base visible assembly through "
        "explicit semantic references because each newline-only fragment "
        "has no promoted decision row; Base runtime and VM state are never "
        "inherited; results, work, completion, controlled castles, "
        "retainers, policy issue levels, goals, current values, counters "
        "and level notation retain established project and historical "
        "wording; direct calls, inline duration, goal and current-value "
        "tokens, protected outer whitespace, newlines, gaps, literal arity, "
        "terminators, all seventeen same-record prefills, eight hidden "
        "newlines, all forty-one slice prefills, complete assemblies, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, reciprocal S1386 and S1387 decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256": (
            "E1A8B7C31AFD7CD33800E1FE68E170AEA554354C2299B03ED08B73C6FD95E060"
        ),
        "expected_queue_slice_sha256": (
            "DBC7D9D9F46C40449FB82FEC99899C505CEA0DD5D99383011FB62DFE48D5EE25"
        ),
        "expected_prefilled_coordinate_sha256": (
            "C68BB9242A9E044C002D408CEDD22E6F4948401DE04D616CFC9EBDE125FAE39F"
        ),
        "expected_prefill_slice_context_sha256": (
            "7C09BB38B6A28B8957F4ECF2F05675B331304CF73BD88128A5F90FDEB202B53C"
        ),
        "expected_target_coordinate_sha256": (
            "E08FA573A8B3D7FD50137DB28C0EB79D060C6DB081C218468AF181DF409CB496"
        ),
        "expected_source_target_sha256": (
            "1C35EB8A42B6353EAF0DD3D239C434AA10C31A717E2D2E7438FC66C9C1738C67"
        ),
        "expected_current_target_sha256": (
            "6BDEFF32E2F581B0C409F480B7E1B47945180582DC6ADE0BB69F7FE00A9978D8"
        ),
        "expected_context_corpus_sha256": (
            "0E0A0B7D02FDF30847036712F1F4A5AE2366187E8C63CD48F3DA5300D602E45E"
        ),
        "expected_gap_contract_sha256": (
            "DA194E533923DA379259734164C504E90E77D4B06B0A86A8D33EA61418D09BA0"
        ),
        "expected_boundary_sha256": (
            "8C2D74E17AF2B06C02177A59BC92B804C2AC9393F2C9DF1CB31B3B67C9713074"
        ),
        "expected_runtime_control_sha256": (
            "C1530748CEC031760EBEF8D1A8B7F61600F2E71761F6ACA5F3445E8DC2788654"
        ),
        "expected_base_search_sha256": (
            "6867F4623D4876FBD85BBB8DB5C0FCE9C97347044013CF65416018BF17A9B930"
        ),
        "expected_complete_assembly_sha256": (
            "9AB413BCC04D7EC13AB7DB512C235329FADB13DEDA2F500B57B0B9E972C4181E"
        ),
        "expected_call_graph_sha256": (
            "296D3C82804E52F4DBD41E4DCD73ECA92FDE94EEDB9B987394E2ECA1DE847B1E"
        ),
        "expected_speaker_style_sha256": (
            "44A2B7991087DE6CDF9553FDC63927942B706F1588DD6086E11029887941F51C"
        ),
        "expected_terminology_policy_sha256": (
            "1F811AC835CE787B8AD9B4FD1C54D8030309D81F7613C494A967D89C5959AB8F"
        ),
        "expected_translation_policy_sha256": (
            "290555BFDB7C7B3668530AF411F765B2DC473EEAAFBC2467606C7A959F79CF7E"
        ),
        "expected_candidate_sha256": (
            "57A12EC0D7D985B526A0599AA86BA48EEF89212707935EC4369CBD4D37DCF462"
        ),
        "expected_combined_slice_candidate_sha256": (
            "1614A1EDED83F32D0B0E43353A25FFA03462CC8B64D874A018AF477E16FFE86A"
        ),
        "expected_combined_changed_literal_count": 47,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B127_S1385",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1385.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1386.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1387.private.v1.jsonl",
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
