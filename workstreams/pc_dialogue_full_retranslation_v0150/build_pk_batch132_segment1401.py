#!/usr/bin/env python3
"""Build source-redacted PK B132 segment 1401 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2423:1",
    "15:2424:0",
    "15:2425:1",
    "15:2427:1",
    "15:2427:2",
    "15:2429:1",
    "15:2432:1",
    "15:2438:0",
    "15:2444:1",
    "15:2445:0",
    "15:2445:2",
    "15:2445:3",
    "15:2446:0",
    "15:2446:1",
    "15:2446:5",
    "15:2449:1",
    "15:2449:2",
    "15:2449:3",
)
TRANSLATIONS = {
    "15:2423:1": "……",
    "15:2424:0": "특히",
    "15:2425:1": "지만\n",
    "15:2427:1": "을(를) 목표로",
    "15:2427:2": "?",
    "15:2429:1": "개를 초과",
    "15:2432:1": "개를 초과",
    "15:2438:0": "세력 목표를 제안한 무장",
    "15:2444:1": "의 소속자",
    "15:2445:0": "을(를) 겨냥한",
    "15:2445:2": "이(가) 간파",
    "15:2445:3": "!",
    "15:2446:0": "이번",
    "15:2446:1": ",",
    "15:2446:5": "주의해",
    "15:2449:1": "에서는",
    "15:2449:2": "이(가)\n",
    "15:2449:3": "에게 의심을 품은 듯……",
}
TARGET_RECORD_IDS = (
    2423, 2424, 2425, 2427, 2429, 2432,
    2438, 2444, 2445, 2446, 2449,
)
EXPECTED_ARITY = {
    2423: 2,
    2424: 2,
    2425: 3,
    2427: 3,
    2429: 3,
    2432: 3,
    2438: 3,
    2444: 4,
    2445: 4,
    2446: 6,
    2449: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2423:0",
    "15:2424:1",
    "15:2425:0",
    "15:2425:2",
    "15:2427:0",
    "15:2429:0",
    "15:2429:2",
    "15:2432:0",
    "15:2432:2",
    "15:2438:1",
    "15:2438:2",
    "15:2444:0",
    "15:2444:2",
    "15:2444:3",
    "15:2445:1",
    "15:2446:2",
    "15:2446:4",
    "15:2449:0",
)
PREFILL_COMPANION_DONOR = {
    "15:2423:0": "15:2392:0",
    "15:2424:1": "15:2393:1",
    "15:2425:0": "15:2394:0",
    "15:2425:2": "15:2394:2",
    "15:2427:0": "15:2396:0",
    "15:2429:0": "15:2398:0",
    "15:2429:2": "15:2398:2",
    "15:2432:0": "15:2401:0",
    "15:2432:2": "15:2398:2",
    "15:2438:1": "15:2407:1",
    "15:2438:2": "15:2407:2",
    "15:2444:0": "15:2413:0",
    "15:2444:2": "15:2413:2",
    "15:2444:3": "15:2413:3",
    "15:2445:1": "15:2414:1",
    "15:2446:2": "15:2415:2",
    "15:2446:4": "15:2415:4",
    "15:2449:0": "15:2418:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2446:3",
)
EXACT_BASE_DONOR = {
    record_id: (15, record_id - 31)
    for record_id in (2423, 2424, 2425, 2427, 2429, 2432, 2444, 2449)
}
SEMANTIC_BASE_CONTEXT = {
    **{record_id: () for record_id in EXACT_BASE_DONOR},
    2438: ("15:2407:0", "15:2407:1", "15:2407:2"),
    2445: ("15:2414:0", "15:2414:1", "15:2414:2", "15:2414:3"),
    2446: (
        "15:2415:0",
        "15:2415:1",
        "15:2415:2",
        "15:2415:4",
        "15:2415:5",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{
        record_id: (EXACT_BASE_DONOR[record_id],)
        for record_id in EXACT_BASE_DONOR
    },
    2438: (),
    2445: (),
    2446: ((15, 2415),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2423: ((562,), ()),
    2424: ((1066,), ("024933",)),
    2425: ((160, 1114), ("024933",)),
    2427: ((466,), ("025032",)),
    2429: ((628, 466), ("0233",)),
    2432: ((628, 466), ("0233",)),
    2438: ((), ("0233", "0232")),
    2444: ((712, 21, 1066), ("02483E",)),
    2445: ((539, 508), ("026432", "023C", "024635")),
    2446: ((628, 1174, 412), ("023C", "024833", "026432")),
    2449: ((34, 8), ("025032", "026432")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1401,
    queue_start=67,
    queue_stop=134,
    slice_first="15:2423:0",
    slice_last="15:2449:3",
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
        562, 1066, 160, 1114, 466, 628, 712, 21,
        539, 508, 1174, 412, 34, 8,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2380, 2485)
    ),
    speaker_style=(
        (2423, "formal_strong_force_caution"),
        (2424, "formal_famous_commander_warning"),
        (2425, "formal_commander_vigilance_advice"),
        (2427, "formal_target_force_recommendation"),
        (2429, "system_castle_target_reward"),
        (2432, "system_facility_target_reward"),
        (2438, "system_merit_award_notice"),
        (2444, "formal_captured_spy_counterplot"),
        (2445, "confident_scheme_detection"),
        (2446, "formal_failed_scheme_warning"),
        (2449, "formal_scheme_aftereffect_report"),
    ),
    terminology_policy=(
        ("force", "세력"),
        ("renowned commander", "명장"),
        ("target", "목표"),
        ("castle", "성"),
        ("castle-town facility", "성하 시설"),
        ("merit", "훈공"),
        ("spy", "간자"),
        ("scheme", "공작, 조략"),
        ("allies", "아군"),
        ("suspicion", "의심"),
        ("dynamic particles", "을(를), 이(가), 은(는)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B132 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; eight complete "
        "records reuse approved completed Base Korean assemblies selected "
        "by literal and operand-masked source identity, while three "
        "PK-specific merit and scheme records use completed adjacent Base "
        "rows as semantic context; one source-identical hidden newline "
        "remains non-translatable while participating in complete assembly; "
        "Base runtime and VM state are never inherited; forces, renowned "
        "commanders, targets, castles, castle-town facilities, merit, spies, "
        "schemes, allies and suspicion retain established historical project "
        "wording and formal, system or confident registers; calls, inline "
        "person, force, castle, count and merit tokens, protected outer "
        "whitespace, line breaks, particles, punctuation, ellipses, "
        "terminators, complete record arity, all forty-nine slice prefills, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256": "4B81A2B81F0E8C254EBA4771F9E0DCDF4F57F82DF74DE0B5E0E61D99D11263A4",
        "expected_queue_slice_sha256": "813281F75C93BD20908E2C0D798AA05A19CAD9AD82E772C1E88E1D2103383F32",
        "expected_prefilled_coordinate_sha256": "DA9F42C01011B5BF7CA746A8735439CCD40E92D4EF5BC1AB0B9D56F29A087F5B",
        "expected_prefill_slice_context_sha256": "725D3530E0FBFFF4C242B571F730400C1F10539812B65341007608375DE74BA9",
        "expected_target_coordinate_sha256": "1F16BB7C5409AFAAC32DD57D974F782B1891DFC1E4D349E745C688A0860D8033",
        "expected_source_target_sha256": "8C6D0A1624418015B1FAA39606B76C61D0766084387C976C158CAB4DB5D64F04",
        "expected_current_target_sha256": "480C434BA4DE09959CD8DE980047088DDE761DC0E23C4D96B60B7B787B790473",
        "expected_context_corpus_sha256": "8D8785D2CB13D6EEC821599ACD953FE03E89249059B0051AEA785D3BD2C6F60B",
        "expected_gap_contract_sha256": "CF88956D2661D2E2C0064D0E6AE363A2F6437508581B2863B7C77ADB7F7E2F14",
        "expected_boundary_sha256": "51A327A1E410BE04C406C0C3E51A71B5F8B8952D79E7D603B94A6FBEF45612D3",
        "expected_runtime_control_sha256": "82F3025A723B1D738FDD45DC1EA0F77CF713451F6A74308D181EC25D717D7D0A",
        "expected_base_search_sha256": "43DBE8AF85A6DA4836B7505405E71A9F85A8AF08DCBD07B88DDEB4F6CA7038C1",
        "expected_complete_assembly_sha256": "6B27B2982115D3E18CAFB9A2C51C2E8021BC6DDE95C116A3FD9B2D17D2099C19",
        "expected_call_graph_sha256": "ABA734D7DD46F9AB8BCBB37DBE839D595C8FB0D8241AC8E48B2F6F665B7BCDFF",
        "expected_speaker_style_sha256": "2B3AFDFE7324DC0C9A5E277FDAF2B45621C174514800DA8ADE2A7414FAB6C49F",
        "expected_terminology_policy_sha256": "EBD23B11A4306B0E88891A34393A506354039DE9CA0C35CD7802FD4C64859BB2",
        "expected_translation_policy_sha256": "93084C1C8B15634D9855B636A30E6E87414D6F8DBD49FFE916ED61BFAE783E99",
        "expected_candidate_sha256": "40C9116A6CF4753487CD6EC4EA0D2E3E4FF2159A6F47F5C5E3472CE0B7854B12",
        "expected_combined_slice_candidate_sha256": "21D14A10481B71468862B43D9BC620F4C5C11CB3C3269B9D3674205170DA82E3",
        "expected_combined_changed_literal_count": 62,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B132_S1401",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1401.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1400.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1402.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B132",
    "queue_row_count": 78,
    "queue_visible_count": 200,
    "queue_first": "15:2396:0",
    "queue_last": "15:2474:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
