#!/usr/bin/env python3
"""Build source-redacted PK B080 segment 1244 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch080_segment1245.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B080_S1244.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B079_S1243.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B080_S1245.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1244
QUEUE_BATCH_ID = "pk_msggame-B080"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_SLICE_FIRST = "9:487:0"
QUEUE_SLICE_LAST = "9:542:0"
QUEUE_SLICE_VISIBLE_COUNT = 67
QUEUE_SLICE_PREFILL_COUNT = 51
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:487:0",
    "9:488:0",
    "9:489:0",
    "9:491:0",
    "9:495:0",
    "9:497:0",
    "9:499:0",
    "9:501:0",
    "9:506:0",
    "9:523:0",
    "9:526:1",
    "9:529:0",
    "9:530:0",
    "9:535:0",
    "9:535:1",
    "9:540:1",
)
TRANSLATIONS = {
    "9:487:0": "을(를) 포함한 총",
    "9:488:0": "이(가)\n저지당함",
    "9:489:0": "을(를) 포함한 총",
    "9:491:0": "을(를) 포함한 총",
    "9:495:0": "설비를 제압해 아군 총사기 상승",
    "9:497:0": "설비가 제압되어 아군 총사기 하락",
    "9:499:0": "본성을 파괴해 아군 총사기 상승",
    "9:501:0": "본성이 파괴되어 아군 총사기 하락",
    "9:506:0": "의 무장",
    "9:523:0": "호오……",
    "9:526:1": "……",
    "9:529:0": "그렇군요……",
    "9:530:0": "뭐라고!\n",
    "9:535:0": "!\n쓰러뜨릴 자는―",
    "9:535:1": "이다!",
    "9:540:1": ", 각오하라!",
}
TARGET_RECORD_IDS = (
    487, 488, 489, 491, 495, 497, 499, 501,
    506, 523, 526, 529, 530, 535, 540,
)
STATIC_RECORD_IDS = (495, 497, 499, 501)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
STATIC_COORDINATES = {
    "9:495:0", "9:497:0", "9:499:0", "9:501:0",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    487: 2, 488: 1, 489: 2, 491: 2,
    495: 1, 497: 1, 499: 1, 501: 1,
    506: 2, 523: 2, 526: 2, 529: 2,
    530: 2, 535: 2, 540: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:487:1",
    "9:489:1",
    "9:491:1",
    "9:506:1",
    "9:523:1",
    "9:526:0",
    "9:529:1",
    "9:530:1",
    "9:540:0",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    487: (9, 437),
    488: (9, 438),
    489: (9, 439),
    491: (9, 441),
    495: (9, 444),
    497: (9, 445),
    499: (9, 446),
    501: (9, 447),
    506: (9, 452),
    523: (9, 469),
    526: (9, 472),
    529: (9, 475),
    530: (9, 476),
    535: (9, 481),
    540: (9, 486),
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    487: ("9:437:0", "9:437:1"),
    488: ("9:438:0",),
    489: ("9:439:0", "9:439:1"),
    491: ("9:424:0", "9:424:1", "9:441:0", "9:441:1"),
    495: ("9:444:0",),
    497: ("9:445:0",),
    499: ("9:446:0",),
    501: ("9:447:0",),
    506: ("9:452:0", "9:452:1"),
    523: ("9:469:0", "9:469:1"),
    526: ("9:472:0", "9:472:1"),
    529: ("9:475:0", "9:475:1"),
    530: ("9:476:0", "9:476:1"),
    535: ("9:481:0", "9:481:1"),
    540: ("9:486:0", "9:486:1"),
}
PREFILL_COMPANION_DONOR = {
    "9:487:1": "9:437:1",
    "9:489:1": "9:439:1",
    "9:491:1": "9:424:1",
    "9:506:1": "9:452:1",
    "9:523:1": "9:469:1",
    "9:526:0": "9:472:0",
    "9:529:1": "9:475:1",
    "9:530:1": "9:476:1",
    "9:540:0": "9:486:0",
}
EXPECTED_BASE_RAW_MATCHES = {
    487: ((9, 437),),
    488: ((9, 438),),
    489: ((9, 439),),
    491: ((9, 424), (9, 441)),
    495: (),
    497: (),
    499: (),
    501: (),
    506: ((9, 452),),
    523: ((9, 469),),
    526: ((9, 472),),
    529: ((9, 475),),
    530: ((9, 476),),
    535: ((9, 481),),
    540: ((9, 486),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id)
    for record_id in (
        423, 424, 425, 436, 437, 438, 439, 440, 441, 442,
        443, 444, 445, 446, 447, 448, 451, 452, 453,
        468, 469, 470, 471, 472, 473, 474, 475, 476, 477,
        480, 481, 482, 485, 486, 487, 488, 489, 490, 491,
        492, 494, 495, 496, 497, 498, 499, 500, 501, 502,
        505, 506, 507, 522, 523, 524, 525, 526, 527, 528,
        529, 530, 531, 534, 535, 536, 539, 540, 541, 542, 543,
    )
)
SOURCE_CALL_ROOTS = (17,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    487: ((), ("02AC32", "0232")),
    488: ((), ("02AC32",)),
    489: ((), ("02AC32", "0232")),
    491: ((), ("02AC32", "0232")),
    495: ((), ()),
    497: ((), ()),
    499: ((), ()),
    501: ((), ()),
    506: ((), ("02AA32", "0232")),
    523: ((17,), ()),
    526: ((17,), ()),
    529: ((17,), ()),
    530: ((17,), ()),
    535: ((17,), ("024635",)),
    540: ((17,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (487, "battlefield_decoy_retreat_summary"),
    (488, "battlefield_movement_blocked_summary"),
    (489, "battlefield_movement_blocked_summary"),
    (491, "battlefield_local_warrior_reinforcement_summary"),
    (495, "allied_morale_gain_notice"),
    (497, "allied_morale_loss_notice"),
    (499, "citadel_destroyed_morale_gain_notice"),
    (501, "citadel_destroyed_morale_loss_notice"),
    (506, "battlefield_officer_casualty_summary"),
    (523, "confident_single_combat_challenge"),
    (526, "elder_single_combat_challenge"),
    (529, "polite_single_combat_challenge"),
    (530, "surprised_single_combat_challenge"),
    (535, "bold_single_combat_challenge"),
    (540, "vengeful_single_combat_challenge"),
)
TERMINOLOGY_POLICY = (
    ("decoy tactic", "위병계"),
    ("local warrior", "토착 무사"),
    ("battle facility", "설비"),
    ("citadel", "본성"),
    ("overall morale", "총사기"),
    ("officer", "무장"),
    ("killed in battle", "전사"),
    ("captured", "포박"),
    ("project em dash", "―"),
    ("ellipsis", "……"),
    ("ASCII exclamation", "!"),
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "E797F5045EF74D1A9675A9AC5541647B60BC4D6A6E9D15478D77B4EB17727800"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4D8D0DAEB32228C23F87E42F3508E3F32B6780CCDDAB96286BF39DEA1F4F582B"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "13C33796DBEC19F836053540D028027B0A0C5093E17BAE6CFB115FCEEBD27EF5"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "41443F608C8263B3E208A0253649C5D1E95D1B202EE964E8C2E39C237BD6EB5E"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "040FA578076C3196DE15B1915781BACA382CF2D9362D9DE8C7F93F1BC10C0C96"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "66DBCB32533CBB9FE4138E08451921C1F3356C24C3926527EF6A275CF2633D16"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "9750D21738C126039BF189357E28A32E8A9101035BF424DA8237FFC3DB6C7ECD"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "F9F8B7AB0AB216707519CE4BA6AD504D42321E7D7D60D47E39661FAEEC9E1026"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "4B5E4951ECDCB30DE3ED9C637D7EF229AAF40396DF5FB7A8D9B3A8B17A6E4BE0"
)
EXPECTED_BOUNDARY_SHA256 = (
    "4B700E7AD6DC7988EF81574D1B90EAB36A107871BEABF47CE96C0250C4088562"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "D354566317EC65E45363B41034A6D3D7C8CDCDB2A28BC3287D9AF827B46A8CA1"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "F65744DDA45B8D69A485A2D1990536C76CDBDF27E3EDF1D7D2E489342217C046"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "403A3198C0AFE3923D75029D432B55520F24E1751C068EE4C06A3F7E956B1319"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "C0DC65720E94CB09CCC9E093592FF6991FE7F40F88AD6B36DC48B57AD4C90F4B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "BA610A5AE7229B64791919A15EC7126F07C7FFCF384DEB2B189E8E38D28F65B1"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "5E0A3D8F8B119C88DCD5D2F09BC7C2AD495CB5F16B2E3CBAC677D81D3332E85C"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "C8DF34A7D5B9F5A22C94DB47FC97F778BCFB1A9E0C13F087080AE63F60A866C1"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F238F23366BE3555FD1EFD3028ABF26DFB6EC31192B66EE7571D84183ADB2D95"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "883B4D266EE6B016BE70D7560B9D41E19B9C32D6BF5487A3C0BD444C6F24E61D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 14
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 63

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; PC English, Simplified "
    "Chinese and Traditional Chinese auxiliaries were reviewed; completed "
    "Base records were used only as semantic, terminology and speaker-"
    "register context without inheriting Base runtime or VM state; battle "
    "status notices use the established project terms for decoy tactics, "
    "local warriors, facilities, the citadel, overall morale, officers, "
    "battle deaths and captures; challenge lines preserve distinct bold, "
    "elderly, polite, surprised and vengeful registers, dynamic calls, "
    "tokens, ellipses and the project em dash; sixteen residual translations "
    "plus nine approved prefill companions assemble all fifteen complete "
    "records; all fifty-one prefills in the sixty-seven-row opening slice, "
    "source/current gaps, controls, protected whitespace and complete "
    "assemblies are guarded; both overlay orders, byte-exact reversal, "
    "two-run reproduction, tamper rejection, outside-scope identity and "
    "Steam read-only state are verified; discovered pins are immutable and "
    "Base runtime state is never inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1244_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ENGINE = PARENT.ENGINE
CORE = PARENT.CORE
sha256_bytes = PARENT.sha256_bytes


def install_globals() -> None:
    names = (
        "SCRIPT", "OUTPUT", "PREFILL", "BASE_PROMOTED",
        "OPTIONAL_NEIGHBORS", "STEAM_PK", "SEGMENT", "QUEUE_BATCH_ID",
        "QUEUE_START", "QUEUE_STOP", "QUEUE_SLICE_FIRST",
        "QUEUE_SLICE_LAST", "QUEUE_SLICE_VISIBLE_COUNT",
        "QUEUE_SLICE_PREFILL_COUNT", "BLOCK_ID", "PK_RECORD_COUNT",
        "TARGET_COORDINATES", "TRANSLATIONS", "TARGET_RECORD_IDS",
        "STATIC_RECORD_IDS", "DYNAMIC_RECORD_IDS", "STATIC_COORDINATES",
        "DYNAMIC_COORDINATES", "EXPECTED_ARITY",
        "PREFILL_COMPANION_COORDINATES",
        "HIDDEN_CURRENT_COMPANION_COORDINATES", "SEMANTIC_BASE_RECORD",
        "PREFILL_COMPANION_DONOR", "EXACT_BASE_DONOR",
        "SEMANTIC_BASE_CONTEXT", "EXPECTED_BASE_RAW_MATCHES",
        "EXPECTED_BASE_LITERAL_MATCHES", "EXPECTED_BASE_MASKED_MATCHES",
        "BOUNDARY_RECORD_KEYS", "SOURCE_CALL_ROOTS", "CURRENT_CALL_ROOTS",
        "EXPECTED_CONTROLS_BY_RECORD",
        "EXPECTED_SOURCE_CONTROLS_BY_RECORD",
        "EXPECTED_CURRENT_CONTROLS_BY_RECORD",
        "SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS", "SPEAKER_STYLE",
        "TERMINOLOGY_POLICY", "EXPECTED_STEAM_PK_SHA256",
        "EXPECTED_PRISTINE_PK_SHA256", "EXPECTED_PREFILL_SHA256",
        "EXPECTED_BASE_PROMOTED_SHA256", "EXPECTED_QUEUE_UNIVERSE_SHA256",
        "EXPECTED_QUEUE_SLICE_SHA256",
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
        "EXPECTED_TARGET_COORDINATE_SHA256", "EXPECTED_SOURCE_TARGET_SHA256",
        "EXPECTED_CURRENT_TARGET_SHA256", "EXPECTED_CONTEXT_CORPUS_SHA256",
        "EXPECTED_GAP_CONTRACT_SHA256", "EXPECTED_BOUNDARY_SHA256",
        "EXPECTED_RUNTIME_CONTROL_SHA256", "EXPECTED_BASE_SEARCH_SHA256",
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256", "EXPECTED_CALL_GRAPH_SHA256",
        "EXPECTED_SPEAKER_STYLE_SHA256",
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        "EXPECTED_TRANSLATION_POLICY_SHA256", "EXPECTED_CANDIDATE_SHA256",
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256",
        "EXPECTED_CHANGED_LITERAL_COUNT",
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT", "DISCOVERED_PINS", "BASIS",
    )
    namespace = globals()
    for name in names:
        setattr(PARENT, name, namespace[name])


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, str, int, tuple[str, ...],
]:
    install_globals()
    return PARENT.build_rows()


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared, rows, candidate, candidate_sha256, changed,
        combined_sha256, combined_changed, optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    if DISCOVERED_PINS:
        print(json.dumps(
            DISCOVERED_PINS, sort_keys=True, separators=(",", ":"),
        ))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 16
        or len(validated) != 16
        or counts != Counter({"runtime_fragment_pending": 16})
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    install_globals()
    PARENT.propagate_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    if DISCOVERED_PINS:
        raise RuntimeError(f"segment {SEGMENT} pins remained mutable")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B080_S1244",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": QUEUE_SLICE_VISIBLE_COUNT,
        "exact_reuse_prefill_count": QUEUE_SLICE_PREFILL_COUNT,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count": 0,
        "masked_complete_base_donor_record_count": 0,
        "semantic_base_context_record_count": len(SEMANTIC_BASE_RECORD),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
        "candidate_sha256": candidate_sha256,
        "combined_slice_candidate_sha256": combined_sha256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "steam_sha256_before": steam_before,
        "steam_sha256_after": steam_after,
        "base_runtime_state_inherited": False,
        "source_current_gap_contract_guarded": True,
        "inline_token_controls_guarded": True,
        "direct_call_graphs_guarded": True,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "discovered_pins_empty": True,
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
