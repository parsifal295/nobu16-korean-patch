#!/usr/bin/env python3
"""Build source-redacted PK B134 segment 1408 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE = (
    COMMON.BASE.base_and_assembly_evidence
)
_ORIGINAL_RUNTIME_EVIDENCE = COMMON.CORE.runtime_evidence

MAIN_RECORD_IDS = tuple(range(2588, 2600))
SUPPLEMENT_RECORD_KEYS = ((16, 3), (16, 7))
TARGET_RECORD_IDS = MAIN_RECORD_IDS + (3, 7)
TARGET_RECORD_KEYS = (
    *((15, record_id) for record_id in MAIN_RECORD_IDS),
    *SUPPLEMENT_RECORD_KEYS,
)
TARGET_COORDINATES = (
    "15:2588:0",
    "15:2588:1",
    "15:2588:3",
    "15:2589:0",
    "15:2589:1",
    "15:2589:2",
    "15:2589:3",
    "15:2590:0",
    "15:2590:1",
    "15:2590:2",
    "15:2590:3",
    "15:2591:0",
    "15:2591:1",
    "15:2591:2",
    "15:2591:3",
    "15:2592:0",
    "15:2592:1",
    "15:2592:2",
    "15:2592:4",
    "15:2593:0",
    "15:2593:1",
    "15:2593:2",
    "15:2593:3",
    "15:2593:4",
    "15:2594:0",
    "15:2594:1",
    "15:2594:2",
    "15:2594:3",
    "15:2595:0",
    "15:2595:1",
    "15:2595:2",
    "15:2596:0",
    "15:2596:1",
    "15:2596:2",
    "15:2596:3",
    "15:2596:4",
    "15:2597:0",
    "15:2597:1",
    "15:2597:3",
    "15:2597:4",
    "15:2598:0",
    "15:2598:1",
    "15:2598:2",
    "15:2598:3",
    "15:2598:4",
    "15:2599:0",
    "16:3:0",
    "16:7:1",
)
MAIN_TARGET_COORDINATES = tuple(
    coordinate
    for coordinate in TARGET_COORDINATES
    if coordinate.startswith("15:")
)
TRANSLATIONS = {
    "15:2588:0": ", 저희는 여기까지인가 봅니다",
    "15:2588:1": "……\n역시 적은 만만한 상대가 아닙니다",
    "15:2588:3": ", 부디 무운을 빕니다……!",
    "15:2589:0": "의 군세가 쳐들어왔습니다",
    "15:2589:1": "\n적의 기세를 살려 줄 수는 없습니다",
    "15:2589:2": "\n이 성에서 반드시 막아 내겠습니다",
    "15:2589:3": "!",
    "15:2590:0": "우리를 붙잡아 둘 셈입니까",
    "15:2590:1": "\n적의 뜻대로 되게 둘 수는 없습니다",
    "15:2590:2": "\n서둘러 제압하고 본대에 합류하겠습니다",
    "15:2590:3": "!",
    "15:2591:0": "을(를) 지켜 냈습니다",
    "15:2591:1": "!\n이제 우리 군의 승리를 빌 뿐입니다",
    "15:2591:2": "\n모두 이대로 성의 방비를 굳혀라",
    "15:2591:3": "!",
    "15:2592:0": "큭, 발을 묶지는 못한 것",
    "15:2592:1": "인가……\n",
    "15:2592:2": "적병도 충분히 소모되었을 것입니다",
    "15:2592:4": ", 부디 우리 군에 승리를……!",
    "15:2593:0": "……마침내 자웅을 가릴 때가 온 것",
    "15:2593:1": "인가\n",
    "15:2593:2": "의 운명도 여기까지입니다",
    "15:2593:3": "\n이번 싸움으로 끝장을 내 주십시오",
    "15:2593:4": "!",
    "15:2594:0": "모두, 이제 결전의 때입니다",
    "15:2594:1": (
        "!\n우리의 천하 통일 야망을 이루기 위해\n여기서"
    ),
    "15:2594:2": "과(와) 결판을 냅시다",
    "15:2594:3": "!",
    "15:2595:0": (
        "에게 패하다니……\n이렇게 된 이상 항복할 수밖에"
    ),
    "15:2595:1": "없습니다\n우리의 숙원도 여기까지군요,",
    "15:2595:2": "……",
    "15:2596:0": "모두, 수고 많았다",
    "15:2596:1": "!\n마침내",
    "15:2596:2": "을(를) 굴복시켰다",
    "15:2596:3": "\n자, 승리의 함성을 올려라",
    "15:2596:4": "!",
    "15:2597:0": ",",
    "15:2597:1": "을(를) 제압하고\n그 여세를 몰아 왔습니다",
    "15:2597:3": "도 함께 싸웁시다",
    "15:2597:4": "!",
    "15:2598:0": ", 잘",
    "15:2598:1": "와 주었습니다",
    "15:2598:2": "!\n",
    "15:2598:3": (
        "이(가) 와 주었으니 든든합니다\n"
        "이번 싸움은 반드시 승리하겠습니다"
    ),
    "15:2598:4": "!",
    "15:2599:0": (
        "거부하면 다시 제안될 때까지 실행할 수 없습니다\n"
        "정말 거부하시겠습니까?"
    ),
    "16:3:0": "성하 건설이야말로\n노동력을 알맞게 쓸 곳이로군",
    "16:7:1": "에 필요하군",
}
EXPECTED_ARITY = {
    2588: 4,
    2589: 4,
    2590: 4,
    2591: 4,
    2592: 5,
    2593: 5,
    2594: 4,
    2595: 3,
    2596: 5,
    2597: 5,
    2598: 5,
    2599: 1,
    3: 1,
    7: 2,
}
PREFILL_COMPANION_COORDINATES = ("16:7:0",)
PREFILL_COMPANION_DONOR = {"16:7:0": "16:7:0"}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2588:2",
    "15:2592:3",
    "15:2597:2",
)
EXACT_BASE_DONOR = {7: (16, 7)}
SEMANTIC_BASE_CONTEXT = {
    2588: ("6:2167:0", "6:2168:0", "6:2169:2", "9:3232:1"),
    2589: ("9:2750:0", "9:2953:0"),
    2590: ("7:135:0", "9:1383:0"),
    2591: ("6:599:0", "9:2750:0"),
    2592: ("6:2169:2", "9:2914:0"),
    2593: ("2:555:0", "7:861:0"),
    2594: ("2:555:0", "8:364:0"),
    2595: ("7:2770:2", "8:364:0"),
    2596: ("7:748:0", "7:748:1"),
    2597: ("7:135:0", "7:2581:0"),
    2598: ("6:597:0", "9:3232:1"),
    2599: ("6:1193:0",),
    3: ("16:3:0",),
    7: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in MAIN_RECORD_IDS},
    3: (),
    7: ((16, 7),),
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_KEY = {
    (15, 2588): ((838, 268, 298, 730, 29), ()),
    (15, 2589): ((184, 736, 1078, 1132), ("025032",)),
    (15, 2590): ((604, 748, 1132), ()),
    (15, 2591): ((1132, 568, 1204), ("026432",)),
    (15, 2592): ((748, 574, 568, 29), ()),
    (15, 2593): ((538, 568, 1096), ("025032",)),
    (15, 2594): ((568, 1132), ("025032",)),
    (15, 2595): ((1090, 250), ("025032",)),
    (15, 2596): ((586, 538, 1132, 1204), ("025032",)),
    (15, 2597): ((8, 628, 7, 190, 514), ("026432",)),
    (15, 2598): ((214, 514, 538, 8, 1132), ()),
    (15, 2599): ((), ()),
    (16, 3): ((), ()),
    (16, 7): ((), ("023C", "02463F")),
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: EXPECTED_CONTROLS_BY_KEY[(15, record_id)]
    for record_id in MAIN_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD.update({
    3: EXPECTED_CONTROLS_BY_KEY[(16, 3)],
    7: EXPECTED_CONTROLS_BY_KEY[(16, 7)],
})
BOUNDARY_RECORD_KEYS = (
    *((15, record_id) for record_id in range(2548, 2600)),
    *((16, record_id) for record_id in range(0, 20)),
)

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1408,
    queue_start=134,
    queue_stop=200,
    slice_first="15:2588:0",
    slice_last="16:19:0",
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
        7, 8, 29, 184, 190, 214, 250, 268, 298, 514, 538, 568,
        574, 586, 604, 628, 730, 736, 748, 838, 1078, 1090, 1096,
        1132, 1204,
    ),
    boundary_record_keys=BOUNDARY_RECORD_KEYS,
    speaker_style=(
        (2588, "formal_withdrawal_and_good_fortune"),
        (2589, "formal_castle_defense_resolve"),
        (2590, "formal_rapid_capture_resolve"),
        (2591, "commanding_successful_defense"),
        (2592, "formal_failed_delay_and_victory_prayer"),
        (2593, "formal_decisive_battle_challenge"),
        (2594, "commanding_unification_decisive_battle"),
        (2595, "formal_defeat_and_surrender"),
        (2596, "commanding_victory_celebration"),
        (2597, "formal_reinforcement_arrival"),
        (2598, "formal_ally_welcome"),
        (2599, "system_rejection_confirmation"),
        (3, "reflective_castle_town_construction"),
        (7, "reflective_policy_necessity"),
    ),
    terminology_policy=(
        ("good fortune in battle", "무운"),
        ("main force", "본대"),
        ("decisive contest", "자웅"),
        ("decisive battle", "결전"),
        ("unification of the realm", "천하 통일"),
        ("surrender", "항복"),
        ("victory cheer", "승리의 함성"),
        ("castle-town construction", "성하 건설"),
        ("labor", "노동력"),
        ("dynamic particles", "을(를), 이(가), 과(와)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B134 queue coordinates one hundred thirty-four "
        "through one hundred ninety-nine and the approved Base prefill; "
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was manually reviewed as auxiliary "
        "context, with the two records lacking auxiliary translations "
        "reviewed from full JP assembly and call context; this mixed slice "
        "contains block fifteen narrative records and block sixteen "
        "reflective lines, so source, current, multilingual, gap, control, "
        "Base-search, complete-assembly and runtime evidence are guarded by "
        "their full block and record coordinates; the source-identical "
        "block sixteen policy record reuses its approved completed Base "
        "Korean assembly, while all other records use completed Base rows "
        "only as semantic and glossary context and never inherit Base "
        "runtime or VM state; good fortune, main force, decisive contests, "
        "decisive battles, unification of the realm, surrender, victory "
        "cheers, castle-town construction and labor retain established "
        "historical project wording and formal, commanding, reflective or "
        "system register; calls, inline person, force, castle, policy and "
        "count tokens, three hidden newline fragments, protected outer "
        "whitespace, line breaks, dynamic particles, punctuation, "
        "terminators, complete record arity, all eighteen slice prefills, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=32,
    pins={
        "expected_queue_universe_sha256": "BDF36DC6AA15A71B145A66EE3EE96918E276D9863BDDAEB4B914B07C158854B1",
        "expected_queue_slice_sha256": "9B12D6AC9FA600160B179F45BB0F066372A784071A3BC2465168B4D84EE11774",
        "expected_prefilled_coordinate_sha256": "9123FCEDB7A9FD4770FA09C91887F4EC8C36228B9482120C0C318D599F768449",
        "expected_prefill_slice_context_sha256": "9359D5A0ABC13C1C0CE6B51B32E729EA04C1EAB73BFAB09D00867F09BE936B67",
        "expected_target_coordinate_sha256": "B4A35CD1B8E26BF3A610F6C30854CAF67EAB6210F47F45CE1A74969A5C73B7E8",
        "expected_source_target_sha256": "59E43BE4C3360DFBC5439E6FDD254B39F16C656456DC9FBDB246BC8C000C4057",
        "expected_current_target_sha256": "853FCAD2EA0F0E23F33D4E9C2443BF6F28AAC7387EDD52B66D8F829110540692",
        "expected_context_corpus_sha256": "B7B9D81CF50637BE6BAE84055CD49869C9178D900D93BB4A6970C10B3599C5B1",
        "expected_gap_contract_sha256": "09E12DC36678ED81D8878E90FB18F09F21B55F68FACBD47FD5D567C7D25B63E4",
        "expected_boundary_sha256": "64A7A73600AAF570BA55718F362B24D6777E707A737AA01B4DC01A87238B35AF",
        "expected_runtime_control_sha256": "09D74F339B3EAABC64774BDA7CE994E2637AC441693BB51A24272374761C8C8B",
        "expected_base_search_sha256": "8EB26240394A97C9487DA402E8F2419EA54C8E117167107032DE882958AF5315",
        "expected_complete_assembly_sha256": "938A5CB5420B323116E67CB61C88D5DE2C53EC61548D3432E5993EDA77896172",
        "expected_call_graph_sha256": "A539428A854C18ADEDE6B2F423849874E33EB12FCB60ACC35947E877D7556C43",
        "expected_speaker_style_sha256": "1BC23B8A77C926C561EE60BDF28FAEC57E7C33C267B85991B6DE4358EBC9B1E7",
        "expected_terminology_policy_sha256": "58E5E7DF4E156101F210057B6B7E937DDCFA2DE2A10C38B0449A9D2FF09DEB26",
        "expected_translation_policy_sha256": "58F3D34C075D20068AA2B726B7789218B7CFEBCEB6319C8343B949B9D7FA5BB6",
        "expected_candidate_sha256": "03E805338ACE9AD5C73329F09BA0A647B212532867703E286E58253C75D52E92",
        "expected_combined_slice_candidate_sha256": "2B10C0C4D00B184B070929411D23A9C4FC851FCAC026F4DEC4AAF8D3E2A0A2E5",
        "expected_combined_changed_literal_count": 49,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B134_S1408",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B134_S1408.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B134_S1406.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B134_S1407.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B134",
    "queue_row_count": 73,
    "queue_visible_count": 200,
    "queue_first": "15:2548:0",
    "queue_last": "16:19:0",
})


def mixed_context_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    """Build coordinate-aware evidence for the mixed block slice."""
    _, _, _, _, record_keys = COMMON.queue_evidence(prepared)
    source_target = tuple(
        (
            coordinate,
            COMMON.literal_texts(
                records_by_label["jp"],
                COMMON.coordinate_key(coordinate)[:2],
            )[COMMON.coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            COMMON.literal_texts(
                records_by_label["current"],
                COMMON.coordinate_key(coordinate)[:2],
            )[COMMON.coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            key,
            COMMON.sha256_bytes(records[key].data),
            COMMON.literal_texts(records, key),
        )
        for label, records in records_by_label.items()
        for key in record_keys
    )
    gaps = tuple(
        (
            key,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(records_by_label["jp"][key])
            ),
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(
                    records_by_label["current"][key]
                )
            ),
        )
        for key in TARGET_RECORD_KEYS
    )
    boundary = tuple(
        (
            label,
            key,
            COMMON.sha256_bytes(records_by_label[label][key].data),
            COMMON.literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for key in BOUNDARY_RECORD_KEYS
    )
    controls = tuple(
        (
            label,
            key,
            COMMON.CORE.runtime_controls(records_by_label[label][key]),
        )
        for label in ("jp", "current")
        for key in TARGET_RECORD_KEYS
    )
    return {
        "source_target": source_target,
        "current_target": current_target,
        "corpus": corpus,
        "gaps": gaps,
        "boundary": boundary,
        "controls": controls,
    }


def assert_context_contracts_mixed(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = mixed_context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"],
         CONFIG["expected_source_target_sha256"]),
        ("current target", values["current_target"],
         CONFIG["expected_current_target_sha256"]),
        ("multilingual context", values["corpus"],
         CONFIG["expected_context_corpus_sha256"]),
        ("gap contract", values["gaps"],
         CONFIG["expected_gap_contract_sha256"]),
        ("boundary", values["boundary"],
         CONFIG["expected_boundary_sha256"]),
        ("runtime control", values["controls"],
         CONFIG["expected_runtime_control_sha256"]),
    ):
        COMMON.CORE.guarded_digest(label, value, expected)
    expected_controls = tuple(
        (label, key, EXPECTED_CONTROLS_BY_KEY[key])
        for label in ("jp", "current")
        for key in TARGET_RECORD_KEYS
    )
    if (
        any(source != current for _, source, current in values["gaps"])
        or values["controls"] != expected_controls
        or any(
            ("pk_msggame", *COMMON.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError("segment 1408 mixed runtime layout drifted")


def base_and_assembly_evidence_mixed(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard block fifteen normally and append block sixteen evidence."""
    original_globals = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved_record_ids = original_globals["TARGET_RECORD_IDS"]
    saved_coordinates = original_globals["TARGET_COORDINATES"]
    saved_prefill = original_globals["PREFILL_COMPANION_COORDINATES"]
    saved_prefill_donor = original_globals["PREFILL_COMPANION_DONOR"]
    original_globals["TARGET_RECORD_IDS"] = MAIN_RECORD_IDS
    original_globals["TARGET_COORDINATES"] = MAIN_TARGET_COORDINATES
    original_globals["PREFILL_COMPANION_COORDINATES"] = ()
    original_globals["PREFILL_COMPANION_DONOR"] = {}
    try:
        base_evidence, assembly_evidence = (
            _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(
                prepared,
                records_by_label,
            )
        )
    finally:
        original_globals["TARGET_RECORD_IDS"] = saved_record_ids
        original_globals["TARGET_COORDINATES"] = saved_coordinates
        original_globals["PREFILL_COMPANION_COORDINATES"] = saved_prefill
        original_globals["PREFILL_COMPANION_DONOR"] = saved_prefill_donor

    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    base_tail: list[tuple[Any, ...]] = []
    assembly_tail: list[tuple[Any, ...]] = []
    for key in SUPPLEMENT_RECORD_KEYS:
        block_id, record_id = key
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(
            records_by_label["jp"], key
        )
        current_literals = COMMON.literal_texts(
            records_by_label["current"], key
        )
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if COMMON.literal_texts(base_source, coordinate)
            == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
                and COMMON.CORE.mask_call_operands(record)
                == COMMON.CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1408 Base search drifted: {key}"
            )
        exact = record_id in EXACT_BASE_DONOR
        donor_coordinates = (
            tuple(
                f"{EXACT_BASE_DONOR[record_id][0]}:"
                f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
            if exact
            else SEMANTIC_BASE_CONTEXT[record_id]
        )
        donor_rows: list[dict[str, Any]] = []
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1408 Base context drifted: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(donor)
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{block_id}:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual")
                continue
            prefill = prefill_rows.get(coordinate)
            donor_coordinate = donor_coordinates[literal_id]
            if (
                not exact
                or prefill is None
                or coordinate not in PREFILL_COMPANION_COORDINATES
                or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                != donor_coordinate
                or prefill.get("semantic_review") != "approved"
                or prefill.get("runtime_review") != "pending"
            ):
                raise RuntimeError(
                    f"segment 1408 companion drifted: {coordinate}"
                )
            assembled.append(str(prefill["translation"]))
            owners.append("base_exact_prefill_runtime_pending")
        donor_translations = tuple(
            str(row["translation"]) for row in donor_rows
        )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1408 exact donor assembly drifted: {key}"
            )
        base_tail.append((
            key,
            COMMON.sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(source)
            ),
            raw_matches,
            literal_matches,
            masked_matches,
            donor_coordinates,
            tuple(
                (
                    coordinate,
                    str(row["translation"]),
                    str(row["runtime_review"]),
                )
                for coordinate, row in zip(
                    donor_coordinates, donor_rows
                )
            ),
            "complete_exact" if exact else "semantic_context_only",
        ))
        assembly_tail.append((
            key,
            tuple(owners),
            tuple(assembled),
            donor_translations,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            (
                "complete_translation_equals_completed_base_donor"
                if exact
                else "manual_pk_semantic_adaptation"
            ),
            "base_runtime_state_not_inherited",
        ))
    return (
        tuple(base_evidence) + tuple(base_tail),
        tuple(assembly_evidence) + tuple(assembly_tail),
    )


def runtime_evidence_mixed(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    if record_id not in {3, 7}:
        return _ORIGINAL_RUNTIME_EVIDENCE(records_by_label, record_id)
    key = (16, record_id)
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_controls = COMMON.CORE.runtime_controls(source)
    current_controls = COMMON.CORE.runtime_controls(current)
    exact = record_id in EXACT_BASE_DONOR
    references = (
        tuple(
            f"{EXACT_BASE_DONOR[record_id][0]}:"
            f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        if exact
        else SEMANTIC_BASE_CONTEXT[record_id]
    )
    return {
        "runtime_category": dict(CONFIG["speaker_style"])[record_id],
        "source_record_gap_sha256": COMMON.CORE.canonical_sha256(
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(source)
            )
        ),
        "current_record_gap_sha256": COMMON.CORE.canonical_sha256(
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(current)
            )
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        COMMON.gap_bytes(source) == COMMON.gap_bytes(current),
        "base_complete_record_match_kind": (
            "raw_literal_and_operand_exact"
            if exact
            else "semantic_context_only"
        ),
        "base_complete_record_coordinate": (
            f"{EXACT_BASE_DONOR[record_id][0]}:"
            f"{EXACT_BASE_DONOR[record_id][1]}"
            if exact
            else None
        ),
        "base_complete_record_match_coordinates": tuple(
            f"{match[0]}:{match[1]}"
            for match in EXPECTED_BASE_LITERAL_MATCHES[record_id]
        ),
        "base_semantic_context_coordinates": references,
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed":
        record_id == 7,
        "manual_multilingual_context_reviewed": True,
        "completed_base_donor_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_candidate_mixed(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    """Build and scope-check a candidate across both target blocks."""
    replacements = {
        COMMON.coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    current = records_by_label["current"]
    reverse = {
        key: COMMON.literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = COMMON.ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    reverse_order = COMMON.ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or COMMON.ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError("segment 1408 mixed candidate overlay drifted")
    candidate_records = COMMON.ENGINE.archive_records(
        COMMON.ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != len(TARGET_COORDINATES)
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            COMMON.gap_bytes(candidate_records[key])
            != COMMON.gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError("segment 1408 mixed candidate scope drifted")
    changed = sum(
        translation
        != COMMON.literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = COMMON.sha256_bytes(candidate)
    expected = CONFIG["expected_candidate_sha256"]
    if expected != "TO_PIN" and candidate_sha256 != expected:
        raise RuntimeError(
            "segment 1408 mixed candidate drifted: "
            f"{candidate_sha256}"
        )
    if changed != CONFIG["expected_changed_literal_count"]:
        raise RuntimeError(
            f"segment 1408 mixed changed count drifted: {changed}"
        )
    if expected == "TO_PIN":
        COMMON.DISCOVERED_PINS["candidate"] = candidate_sha256
    return candidate, candidate_sha256, changed


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.assert_context_contracts = assert_context_contracts_mixed
    exact_module.base_and_assembly_evidence = (
        base_and_assembly_evidence_mixed
    )
    exact_module.runtime_evidence = runtime_evidence_mixed
    exact_module.build_candidate = build_candidate_mixed
    COMMON.CORE.assert_context_contracts = assert_context_contracts_mixed
    COMMON.CORE.base_and_assembly_evidence = (
        base_and_assembly_evidence_mixed
    )
    COMMON.CORE.runtime_evidence = runtime_evidence_mixed
    COMMON.CORE.build_candidate = build_candidate_mixed


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
