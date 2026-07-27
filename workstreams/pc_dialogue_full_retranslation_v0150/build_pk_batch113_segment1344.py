#!/usr/bin/env python3
"""Build source-redacted PK B113 segment 1344 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = tuple(range(526, 556))
TARGET_COORDINATES = tuple(
    f"15:{record_id}:0"
    for record_id in TARGET_RECORD_IDS
)
TRANSLATIONS = {
    coordinate: "의"
    for coordinate in TARGET_COORDINATES
}
EXPECTED_ARITY = {
    record_id: 3 if record_id in {528, 535, 538} else 2
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = tuple(
    f"15:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(1, EXPECTED_ARITY[record_id])
)
PREFILL_COMPANION_DONOR = {
    f"15:{record_id}:{literal_id}":
    f"15:{record_id - 7}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(1, EXPECTED_ARITY[record_id])
}
EXACT_BASE_DONOR = {
    record_id: (15, record_id - 7)
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES = {
    record_id: ((15, record_id - 7),)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: (
        (7,) if record_id in {528, 535, 538} else (),
        ("029632", "028C32"),
    )
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1344,
    queue_start=67,
    queue_stop=134,
    slice_first="15:522:0",
    slice_last="15:555:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(7,),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(510, 601)
    ),
    speaker_style=tuple(
        (record_id, "exact_base_kunishu_placation_register")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("kunishu", "국인중"),
        ("placate", "회유"),
        ("reinforcements", "원군"),
        ("clan", "우리 가문"),
        ("enter service", "가신단에 편입"),
        ("incorporate", "편입"),
        ("benevolence", "인덕"),
        ("win favor", "환심을 사다"),
        ("dynamic possessive particle", "의"),
        ("dynamic subject particle", "께서"),
        ("dynamic object particle", "을(를)"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; all "
        "thirty complete PK records are byte-identical to approved completed "
        "Base donor records at the uniform minus-seven offset and therefore "
        "reuse the full Korean assemblies while retaining each speaker's "
        "completed Base register; Base runtime and VM state are never "
        "inherited; dynamic kunishu, clan and speaker calls retain their "
        "source ordering, possessive, subject and object particles remain "
        "explicit, and kunishu, placation, reinforcements, service, "
        "incorporation, benevolence and favor terminology follows the "
        "historical project glossary; calls, inline tokens, whitespace, "
        "line breaks, terminators, complete record arity, all thirty-seven "
        "slice prefills, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=0,
    pins={
        "expected_queue_universe_sha256": (
            "6C349A528565248A1F4B3505C88EFF2FE9319565E988090698E9D8361AE92F89"
        ),
        "expected_queue_slice_sha256": (
            "9B0326BC53F07AE22FD7508F926ED72AB5A55B81A02C8B1FD37B2385BA8C133F"
        ),
        "expected_prefilled_coordinate_sha256": (
            "AF0E486D6098974181AF930DE924ECDB39CDEB6E522A9588C8CB52AC2FFEF18C"
        ),
        "expected_prefill_slice_context_sha256": (
            "1A6918EE7C6E75FC6DF1A5753DA1DB1E0EFFA69F2E559E4EA236DCAD139D3C1F"
        ),
        "expected_target_coordinate_sha256": (
            "11AB61422485BAA20948D18556D755D88F1301C6DB31CEAACFCDBBE341E1CA57"
        ),
        "expected_source_target_sha256": (
            "33F9113F0395448A1633676B2AE8819EB61DDD92DE9ACDD3FC1BE2CE7FBDD1B9"
        ),
        "expected_current_target_sha256": (
            "A4CFA106A3CB586FF66ECDB8249D3B0A5E372479C7F0ED563F44DC1F5FD6313F"
        ),
        "expected_context_corpus_sha256": (
            "288366D1942DFD99B7108EB5E47075BFE8EFECEC2B67DDEDB512C81668CC7712"
        ),
        "expected_gap_contract_sha256": (
            "8BC4C6B4A1D3FC35324869B54E01B571CCAD7CCD24D384D36C4ABE159A7F6090"
        ),
        "expected_boundary_sha256": (
            "E08E271BAF03AE3F427B64323842269E6BDCE4B211A09776587F3E5FE3278D3C"
        ),
        "expected_runtime_control_sha256": (
            "5FA403B8F363F32226D9A1BA2E78BE02169B4C273F5F96A6C4BF44DE0D2652D0"
        ),
        "expected_base_search_sha256": (
            "ACCE41652C82081195B45267CF1D65CCB02C14F915321309BF63D6FB7B560432"
        ),
        "expected_complete_assembly_sha256": (
            "833890390AB0633A15287F19EE83DC7101B29FC397C3FA53EDBF6B5A7A74EC27"
        ),
        "expected_call_graph_sha256": (
            "C4765167CD1096FA6654A9D18EF4F56583E4BB661E40C8DAB0A0BA1840632DB4"
        ),
        "expected_speaker_style_sha256": (
            "413141DFFCB471FC8567C9B0541E104000ED479154245653130D7DBD4860AF54"
        ),
        "expected_terminology_policy_sha256": (
            "DBB6220E199CD8E0882082AD2000647484DF6F1187E5DE8A2E212CB1C3555171"
        ),
        "expected_translation_policy_sha256": (
            "A4CFA106A3CB586FF66ECDB8249D3B0A5E372479C7F0ED563F44DC1F5FD6313F"
        ),
        "expected_candidate_sha256": (
            "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
        ),
        "expected_combined_slice_candidate_sha256": (
            "6E33301E39625FC454D732FB3E51425BF34805E44AEBD9B5268369064409005C"
        ),
        "expected_combined_changed_literal_count": 37,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B113_S1344",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1344.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1343.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1345.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B113",
    "queue_row_count": 107,
    "queue_visible_count": 200,
    "queue_first": "15:484:0",
    "queue_last": "15:590:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
