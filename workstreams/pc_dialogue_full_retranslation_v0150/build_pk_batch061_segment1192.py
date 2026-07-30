#!/usr/bin/env python3
"""Build source-redacted PK B061 segment 1192 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch060_segment1189.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B061_S1192.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B061_S1191.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B061_S1193.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1192
QUEUE_BATCH_ID = "pk_msggame-B061"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:1664:0",
    "7:1666:0",
    "7:1667:0",
    "7:1668:0",
    "7:1676:0",
    "7:1678:1",
    "7:1680:1",
    "7:1681:0",
    "7:1682:0",
    "7:1684:0",
    "7:1686:0",
    "7:1688:0",
    "7:1690:0",
)
TRANSLATIONS = {
    "7:1664:0": "의 성—",
    "7:1666:0": "의 성—",
    "7:1667:0": "노린다면—",
    "7:1668:0": "의 성—",
    "7:1676:0": "의 성—",
    "7:1678:1": "의 성—",
    "7:1680:1": "의 성—",
    "7:1681:0": "노릴 곳은—",
    "7:1682:0": "의 성—",
    "7:1684:0": "공격한다면—",
    "7:1686:0": "의 성—",
    "7:1688:0": "의 성—",
    "7:1690:0": "이제는—",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    1664,
    1666,
    1667,
    1668,
    1676,
    1678,
    1680,
    1681,
    1682,
    1684,
    1686,
    1688,
    1690,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    1664: 2,
    1666: 2,
    1667: 3,
    1668: 2,
    1676: 2,
    1678: 3,
    1680: 3,
    1681: 3,
    1682: 2,
    1684: 3,
    1686: 2,
    1688: 2,
    1690: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "7:1664:1",
    "7:1666:1",
    "7:1667:2",
    "7:1668:1",
    "7:1676:1",
    "7:1678:0",
    "7:1678:2",
    "7:1680:0",
    "7:1680:2",
    "7:1681:2",
    "7:1682:1",
    "7:1684:2",
    "7:1686:1",
    "7:1688:1",
    "7:1690:1",
    "7:1690:2",
)
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "7:1667:1",
    "7:1681:1",
    "7:1684:1",
)
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
PRIMARY_BASE_MATCH = {
    1664: (7, 1624),
    1666: (7, 1626),
    1667: (7, 1627),
    1668: (7, 1628),
    1676: (7, 1636),
    1678: (7, 1638),
    1680: (7, 1640),
    1681: (7, 1641),
    1682: (7, 1642),
    1684: (7, 1644),
    1686: (7, 1646),
    1688: (7, 1648),
    1690: (7, 1650),
}
EXPECTED_BASE_MATCHES = {
    record_id: (base_coordinate,)
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
EXPECTED_RAW_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_BASE_DONOR_COORDINATES = {
    record_id: tuple(
        f"{base_coordinate[0]}:{base_coordinate[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
        if f"7:{record_id}:{literal_id}"
        not in HIDDEN_CURRENT_COMPANION_COORDINATES
    )
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
BOUNDARY_RECORD_KEYS = (
    (7, 1662),
    (7, 1663),
    *tuple((7, record_id) for record_id in TARGET_RECORD_IDS),
    (7, 1665),
    (7, 1669),
    (7, 1675),
    (7, 1677),
    (7, 1679),
    (7, 1683),
    (7, 1685),
    (7, 1687),
    (7, 1689),
    (7, 1691),
    (7, 1693),
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1664: ((), ("025032", "026432")),
    1666: ((), ("025032", "026432")),
    1667: ((), ("026432", "025032")),
    1668: ((), ("025032", "026432")),
    1676: ((), ("025032", "026432")),
    1678: ((), ("025032", "026432")),
    1680: ((), ("025032", "026432")),
    1681: ((), ("026432", "025032")),
    1682: ((), ("025032", "026432")),
    1684: ((), ("026432", "025032")),
    1686: ((), ("025032", "026432")),
    1688: ((), ("025032", "026432")),
    1690: ((), ("025032", "026432")),
}
SPEAKER_STYLE = (
    (1664, "elder_allied_castle_opportunity"),
    (1666, "formal_allied_castle_realism"),
    (1667, "formal_alliance_obsolescence"),
    (1668, "measured_allied_castle_realism"),
    (1676, "reluctant_allied_castle_desire"),
    (1678, "decisive_break_relations"),
    (1680, "cynical_break_relations"),
    (1681, "formal_relations_settlement"),
    (1682, "worldly_attack_opportunity"),
    (1684, "formal_break_relations_opportunity"),
    (1686, "measured_enemy_complacency"),
    (1688, "urgent_castle_attack"),
    (1690, "formal_no_need_for_restraint"),
)
TERMINOLOGY_POLICY = (
    ("castle", "성"),
    ("friendly relations", "우호"),
    ("break relations", "단교"),
    ("practical gain", "실리"),
    ("attack", "공격"),
    ("capture", "함락"),
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
    "84B05B910EFFBD07D2C16C76B26C6207F5469076F75A7CA85F1A93DD18089D88"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "C8F21AD497B2D529E29E13F0B92DD490821DE6A3D34BE17DF793B23A48657130"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5BCCB4AF74D532C4EB36CED6EE538D72C5FC2A2BAA5CEF6CCFBB8A197283D5AB"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "BA78703610BD296121BA53B846EB3199CBB8D4D93464B33D517E407C35B78AAA"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "76BEC669F0563E6A6E25F6D27BCAFA0B1B098E22150A099391367C36E02DB966"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "2650A3FA44CF3C36085A65260CDEBD4470A51F9BB11C28ACBDB9AA95F7E901DD"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "C15C44A3487D2D050FCA372B641241A78753C0C1257FCEFC06749878F31F31D2"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "DF887CF2AA562EF7CD7931F63C6E989B19E45D597EDD3E72F686F51B207D67F8"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "E0C4ACB5198E34A8AE46134E2BEF663B3EA8BE64E347BE123400DAAE5393FCC7"
)
EXPECTED_BOUNDARY_SHA256 = (
    "4E9FF1D6DD074BC9D7910143B10936AC33433944B75A563C6621C09AB83EFE94"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "DB113BA18C0BD7065483021A8BF58F3610203EA203AC643F43C518130529D6E7"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "F82E6C564A2F60AAAE099D5CAC8261ED94BC07941829B24A86CDBCE4B8825220"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "A032A80309B82546F750D32FBCC0774F6D8924FD8861F98D6EE05DBA474999D2"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "79AFC94FCCCD70D0E64EEE8C262A577E0590FA0540FB66C69068FBE707B4B98A"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "C7C5DDD954700F9F58DAD4A53FC78CC4AFF2FACA25B375BEC025DE785AED38F5"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "7B3A851BA879F70DC64CC7783A8C23417CDAE6ABB214AB6DF2A11DFCD5B7E3D6"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "50DFD05D6C3893776368CDD3019E854F80F3C675802DC81B39EFB0308FF07BC9"
)
EXPECTED_CANDIDATE_SHA256 = (
    "B472A15E0944DD2BD6B8F0523DA6715C8AF4C19C11B4B157A21234DA3301A2AC"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "EB8B79A5F6CFFAE193BE0C0425255F8CBC084B4916E53645D90D50C22E44AF44"
)
EXPECTED_CHANGED_LITERAL_COUNT = 13

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC context "
    "reviewed where present; all thirteen complete PK source records have "
    "one byte-exact completed Base source donor whose final Korean is "
    "selected only after manual semantic, terminology and register review; "
    "sixteen approved Base-prefilled companions and three source-empty "
    "newline companions are reviewed as complete record assemblies; all "
    "fifty-three Base prefills in the queue slice are validated; force and "
    "castle tokens, particles, newlines, protected outer whitespace, full "
    "records, boundaries, two-run reproduction, tamper rejection, reverse "
    "overlays, outside-scope identity and Steam read-only state are "
    "guarded; Base runtime and VM state are not inherited and every "
    "residual remains runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1192_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
PARENT = BASE.PARENT
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = PARENT.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
runtime_controls = PARENT.runtime_controls
mask_call_operands = PARENT.mask_call_operands


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = queue_rows(prepared)
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 143
        or len(visible) != 200
        or visible[0] != "7:1551:0"
        or visible[-1] != "7:1693:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B061 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "7:1663:0"
        or queue_slice[-1] != "7:1693:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != 53
        or len(residual) != 13
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} queue residual drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and mask_call_operands(record) == mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_RAW_BASE_MATCHES[record_id]
            or literal_matches != EXPECTED_LITERAL_BASE_MATCHES[record_id]
            or masked_matches != EXPECTED_MASKED_BASE_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        assembled: list[str] = []
        donor_assembled: list[str] = []
        donor_rows: list[dict[str, Any]] = []
        base_key = PRIMARY_BASE_MATCH[record_id]
        base_literals = literal_texts(base_source, base_key)
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            donor_coordinate = (
                f"{base_key[0]}:{base_key[1]}:{literal_id}"
            )
            if coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                    or base_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden newline drifted: "
                        f"{coordinate}"
                    )
                seen_hidden.add(coordinate)
                assembled.append("\n")
                donor_assembled.append("\n")
                continue
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing donor: {donor_coordinate}"
                )
            donor_translation = str(donor["translation"])
            if coordinate in target_set:
                if TRANSLATIONS[coordinate] != donor_translation:
                    raise RuntimeError(
                        f"segment {SEGMENT} target donor drifted: "
                        f"{coordinate}"
                    )
                seen_target.add(coordinate)
                assembled.append(TRANSLATIONS[coordinate])
            elif coordinate in companion_set:
                companion = prefill_rows.get(coordinate)
                if (
                    companion is None
                    or companion.get("runtime_review") != "pending"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or str(companion["translation"]) != donor_translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill companion drifted: "
                        f"{coordinate}"
                    )
                seen_companion.add(coordinate)
                assembled.append(str(companion["translation"]))
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned literal: {coordinate}"
                )
            donor_assembled.append(donor_translation)
            donor_rows.append(donor)
        if tuple(assembled) != tuple(donor_assembled):
            raise RuntimeError(
                f"segment {SEGMENT} complete donor assembly drifted: "
                f"{record_id}"
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
                tuple(
                    coordinate
                    for coordinate in HIDDEN_CURRENT_COMPANION_COORDINATES
                    if coordinate.startswith(f"7:{record_id}:")
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(assembled),
                tuple(donor_assembled),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "exact_complete_record_reviewed",
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 66
        or len(prefilled) != 53
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def install_base_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "FUTURE_COMPANION_COORDINATES": FUTURE_COMPANION_COORDINATES,
        "PRIMARY_BASE_MATCH": PRIMARY_BASE_MATCH,
        "EXPECTED_BASE_MATCHES": EXPECTED_BASE_MATCHES,
        "EXPECTED_RAW_BASE_MATCHES": EXPECTED_RAW_BASE_MATCHES,
        "EXPECTED_LITERAL_BASE_MATCHES": EXPECTED_LITERAL_BASE_MATCHES,
        "EXPECTED_MASKED_BASE_MATCHES": EXPECTED_MASKED_BASE_MATCHES,
        "EXPECTED_BASE_DONOR_COORDINATES":
        EXPECTED_BASE_DONOR_COORDINATES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256": EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
        "queue_evidence": queue_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    PARENT.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    result = list(BASE.build_rows())
    rows = result[1]
    for row in rows:
        row["manual_complete_base_donor_translation_selected"] = True
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = False
        row["hidden_source_newline_companion_reviewed"] = (
            coordinate_key(str(row["coordinate"]))[1] in {1667, 1681, 1684}
        )
        row["next_slice_companion_reviewed"] = False
    return tuple(result)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
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
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 13
        or len(validated) != 13
        or counts != Counter({"runtime_fragment_pending": 13})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        PARENT.engine_builder().assert_tamper_rejection(
            prepared,
            rows,
            candidate,
        )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B061_S1192",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 53,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_current_companion_count":
                len(HIDDEN_CURRENT_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                len(EXPECTED_BASE_MATCHES),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduced": True,
                "outside_scope_identity_guarded": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
