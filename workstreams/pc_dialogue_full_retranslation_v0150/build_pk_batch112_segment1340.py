#!/usr/bin/env python3
"""Build source-redacted PK B112 segment 1340 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    395,
    396,
    435,
    437,
    438,
)
TARGET_COORDINATES = (
    "15:395:1",
    "15:396:0",
    "15:435:0",
    "15:437:0",
    "15:438:0",
)
TRANSLATIONS = {
    "15:395:1": "안에서\n",
    "15:396:0": "의",
    "15:435:0": "은(는)",
    "15:437:0": "이",
    "15:438:0": "이",
}
EXPECTED_ARITY = {
    395: 3,
    396: 2,
    435: 3,
    437: 3,
    438: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:395:0",
    "15:395:2",
    "15:396:1",
    "15:435:1",
    "15:435:2",
    "15:437:1",
    "15:437:2",
    "15:438:1",
    "15:438:2",
)
PREFILL_COMPANION_DONOR = {
    "15:395:0": "15:388:0",
    "15:395:2": "15:388:2",
    "15:396:1": "15:389:1",
    "15:435:1": "15:428:1",
    "15:435:2": "15:428:2",
    "15:437:1": "15:430:1",
    "15:437:2": "15:430:2",
    "15:438:1": "15:431:1",
    "15:438:2": "15:431:2",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ()
EXACT_BASE_DONOR = {
    395: (15, 388),
    396: (15, 389),
    435: (15, 428),
    437: (15, 430),
    438: (15, 431),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, donor in EXACT_BASE_DONOR.items()
}
EXPECTED_BASE_MATCHES = {
    record_id: (donor,)
    for record_id, donor in EXACT_BASE_DONOR.items()
}
EXPECTED_CONTROLS_BY_RECORD = {
    395: ((21,), ("02483E",)),
    396: ((21,), ("02483E",)),
    435: ((17, 1), ("024633",)),
    437: ((17,), ("024633",)),
    438: ((17,), ("024633",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1340,
    queue_start=0,
    queue_stop=67,
    slice_first="15:395:0",
    slice_last="15:440:1",
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
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        1,
        17,
        21,
    ),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(385, 447)
    ),
    speaker_style=(
        (395, "courtly_compassionate_observer"),
        (396, "formal_retainer_intelligence_report"),
        (435, "rough_loyalist_gratitude_pledge"),
        (437, "formal_recruit_service_pledge"),
        (438, "formal_recruit_service_pledge"),
    ),
    terminology_policy=(
        ("clan-house contextual locative", "안에서"),
        ("standing within a house", "입지"),
        ("submission", "귀순"),
        ("retainer band", "막하"),
        ("former lord", "옛 주군"),
        ("formal service pledge", "힘이 되고자 하옵니다"),
        ("rough gratitude pledge", "입은 은혜는 절대 잊지 않아"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record entry was reviewed as auxiliary context; all five "
        "residual literals complete byte-identical approved Base Korean "
        "records, so the full assemblies from Base records 388, 389, 428, "
        "430 and 431 are reused exactly while Base runtime and VM state are "
        "never inherited; the house-internal locative is corrected to the "
        "natural contextual form, and submission, retainer-band, former-"
        "lord, formal service-pledge and rough gratitude registers retain "
        "their established project wording; direct calls, inline name and "
        "house tokens, gaps, line counts, protected outer whitespace, "
        "literal arity, terminators, all nine same-record companions, all "
        "sixty-two slice prefills, complete record assemblies, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=1,
    pins={
        "expected_queue_universe_sha256": (
            "00816F7C9CDC6EEFA665DCA237BA363079B38464F390EAA2965D45F824A7B70F"
        ),
        "expected_queue_slice_sha256": (
            "0A1357FFBA8E191369B3E487CD82C18264F99B374808F82507B662C2159F7A34"
        ),
        "expected_prefilled_coordinate_sha256": (
            "12CAE73611D4F6CA273917B6137E8CDC24438A32F37C572C575818D68FE3AD3C"
        ),
        "expected_prefill_slice_context_sha256": (
            "EF164CCAFC0662032AAC4F3AD5AD56C1EC094E17AFEE596979069B83BE14B066"
        ),
        "expected_target_coordinate_sha256": (
            "CCC88C7D23BB655BCC944AB37341CAECDF2A18AE4303B5DCFC3BAE04CFEF2D23"
        ),
        "expected_source_target_sha256": (
            "9080320A86939DE6A7A5B799109EAE2F41F19E1A922F9EFEDEA7E04A30A71F87"
        ),
        "expected_current_target_sha256": (
            "25ECE6F365CCD33DF7A1D8CCFBF8EDB5A645F08D6E4300FF6FFDBB32918E02F7"
        ),
        "expected_context_corpus_sha256": (
            "832A97B189A998FB791066F3824D741370CF822E6BF32123E42917B9ED92B763"
        ),
        "expected_gap_contract_sha256": (
            "ED1A2F8EC0A05EDCC4B806BBCE09E0696F36E157FB8E82328E20297A4DCD9E85"
        ),
        "expected_boundary_sha256": (
            "97BD66B8090D8AEE686E66C931B148633609F0F9BD9A395185C8B1D2FB894E0E"
        ),
        "expected_runtime_control_sha256": (
            "0424EB3705CF9DC58F15792387EBD76FD0C11D001D4C2C4120C6B54DFFEED066"
        ),
        "expected_base_search_sha256": (
            "498C062E8040AA9B94AD51D614E14877E1EB27D6611A40037CC4705D83417E53"
        ),
        "expected_complete_assembly_sha256": (
            "5C49B4A3D874765DF45FF26A374F0B9F7F66A9E74D7A64EBC7EA8ED9C71085B0"
        ),
        "expected_call_graph_sha256": (
            "215863E1FE2A0A310727F40564F8037429FEE644910F305E1AE7D930DA48FA6A"
        ),
        "expected_speaker_style_sha256": (
            "E24D72BD5664CDCA3749CBB1716257435D306DDC67D33A7F77E439A79F318A34"
        ),
        "expected_terminology_policy_sha256": (
            "E8B6B9001C6BEADD7CA0A23C88F8584DC5F4DA3F0F4FEE206D482F197AD2368C"
        ),
        "expected_translation_policy_sha256": (
            "497469208710702013194CD718616AC572915F96D3442AF9A36E95E7CE8ADE91"
        ),
        "expected_candidate_sha256": (
            "8AA79BBCC1EB98D118818A6F7B417D6724A0D7DC9723EF883E0D4464E1223E9C"
        ),
        "expected_combined_slice_candidate_sha256": (
            "DCC27E8D2BD128E16F7CFEA0576C67B6B82E4A68AD3B5BC57B63A1DB8D6D300F"
        ),
        "expected_combined_changed_literal_count": 60,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B112_S1340",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1340.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1341.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1342.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B112",
    "queue_row_count": 89,
    "queue_visible_count": 199,
    "queue_first": "15:395:0",
    "queue_last": "15:483:5",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
