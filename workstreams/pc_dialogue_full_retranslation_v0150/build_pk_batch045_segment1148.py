#!/usr/bin/env python3
"""Build source-redacted PK B045 segment 1148 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch044_segment1145.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B045_S1148.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B045_S1146.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B045_S1147.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1148
QUEUE_BATCH_ID = "pk_msggame-B045"
QUEUE_START = 134
QUEUE_STOP = 199
QUEUE_FIRST_RECORD = 4370
QUEUE_LAST_RECORD = 4467
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4438:1",
    "6:4438:3",
    "6:4442:0",
    "6:4442:4",
    "6:4443:1",
    "6:4443:4",
    "6:4446:1",
    "6:4448:0",
    "6:4449:0",
    "6:4450:0",
    "6:4451:0",
    "6:4452:0",
    "6:4453:0",
    "6:4454:0",
    "6:4458:0",
    "6:4459:0",
    "6:4461:0",
    "6:4461:1",
    "6:4462:1",
    "6:4463:1",
)
TRANSLATIONS = {
    "6:4438:1": "지만\n현재 「",
    "6:4438:3": "…",
    "6:4442:0": "정책「",
    "6:4442:4": "까닭에",
    "6:4443:1": "」이(가)",
    "6:4443:4": "지만…",
    "6:4446:1": "지만…",
    "6:4448:0": ", 「",
    "6:4449:0": "방침, 받들",
    "6:4450:0": "명을 받들겠습니다",
    "6:4451:0": "명을 받들겠습니다",
    "6:4452:0": "명을 받들겠습니다",
    "6:4453:0": "명을 받들겠습니다",
    "6:4454:0": "성주 「",
    "6:4458:0": "미사용",
    "6:4459:0": "을(를) 배속해",
    "6:4461:0": "이 「",
    "6:4461:1": "」은(는), 부디 「",
    "6:4462:1": ", 팔이 근질거리",
    "6:4463:1": " 원하시는 것이군요",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4438, 4442, 4443, 4446, 4448, 4449, 4450, 4451,
    4452, 4453, 4454, 4458, 4459, 4461, 4462, 4463,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4438: 4,
    4442: 5,
    4443: 5,
    4446: 2,
    4448: 2,
    4449: 2,
    4450: 1,
    4451: 2,
    4452: 2,
    4453: 2,
    4454: 3,
    4458: 1,
    4459: 2,
    4461: 3,
    4462: 4,
    4463: 3,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 59 for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (4454, 4458, 4461)
OPERAND_MASKED_BASE_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in RAW_EXACT_BASE_RECORD_IDS
)
INVISIBLE_CURRENT_COORDINATES = ("6:4462:2",)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if (
        f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
        and f"6:{record_id}:{literal_id}"
        not in INVISIBLE_CURRENT_COORDINATES
    )
)
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    (f"6:{base_record_id}:{literal_id}",)
    for record_id, base_record_id in BASE_RECORD_MAPPING.items()
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in INVISIBLE_CURRENT_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = (
    4369, 4370, 4414, 4437, 4438, 4463, 4467, 4468,
)
SOURCE_CALL_ROOTS = (
    1, 82, 178, 190, 226, 268, 322, 466, 538, 550,
    628, 856, 862, 1066, 1090, 1096, 1126, 1138, 1174,
)
CURRENT_CALL_ROOTS = (
    1, 82, 178, 226, 268, 322, 550, 628, 856, 862,
    1066, 1090, 1096, 1126, 1138,
)

SPEAKER_STYLE = (
    (4438, "policy_suitability_objection"),
    (4442, "policy_facility_construction_proposal"),
    (4443, "castle_town_facility_chain_proposal"),
    (4446, "ideal_facility_proposal"),
    (4448, "collective_policy_acceptance"),
    (4449, "policy_direction_acceptance"),
    (4450, "formal_order_acceptance"),
    (4451, "deferred_order_acceptance_mission_and_battle"),
    (4452, "deferred_order_acceptance_battle"),
    (4453, "deferred_order_acceptance_mission"),
    (4454, "castle_lord_attachment_objection"),
    (4458, "unused_label"),
    (4459, "counterintelligence_assignment_request"),
    (4461, "frontier_assignment_request"),
    (4462, "frontier_defense_assignment_proposal"),
    (4463, "spear_assignment_reconsideration"),
)
TERMINOLOGY_POLICY = (
    ("policy", "정책"),
    ("plan", "방침"),
    ("order_acceptance", "명을 받들겠습니다"),
    ("castle_town", "성하"),
    ("construction", "건설"),
    ("castle_lord", "성주"),
    ("unused", "미사용"),
    ("assignment", "배속"),
    ("covert_action", "조략"),
    ("front_line", "전선"),
    ("unit_defense", "부대의 방비"),
    ("spear_skill", "창 솜씨"),
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
    "C2E43D4245A1C88BB84F972EB43680819976424FDA72B577ED74AD27F15B8B31"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "6253C1999BB861220BDF4DEB2A830C91DBB32BA34CB012C7BC2945B92AC1B45A"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "D514B3DB781BF06944E653E7E88D3814DFE972AE79AB6B58F1EB4D4DE29CF7FA"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "CFB09F532CA300ECE1B557BBD131035CB623018A079AA7AE443B8B55789F64E2"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "360B85CC57887AE9EE1243CBE782386DA498FFBC9FDA6EB0566A1EE4CCAF0572"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "35B4C1F2C694DE3DAE1A869BD4BCDE4EAEC5DE0C912E0403E417DF5CF6CBCED6"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "40455EDB2D67CA516BCB18D25EA227E4F4DAF176220F3F5483B4AB8DB33C8871"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A0F6485949AB6525C8418A3B52E4390E47B3748A0C8249CBDC89E102EE468ACC"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "2F798D7CC62E94DC226E421E8161798978BADF26102895C136D03813C3954833"
)
EXPECTED_BOUNDARY_SHA256 = (
    "E3F9E15EC44478C97FB62702F3C96F8C3BF5F5217BD85B12A4888871D85D4146"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8386566D826902C5C47C8E8DE34F04681C14365D4F05AB5133FEF28D02E15A15"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "7E0A0680BEDFEDB99A98F0B1AC0F8872A86F27EF2145695FF1A01396AFB2D13D"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "CADFC78C89FCADF801A3308D85A90D43CF7808104F54A1411965DC02B4CB4349"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "0468F9C0A2AFFEBC5ACB3A25886045F2D29A62F26766EEEECAF09862C4F7FBE5"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "CB2571C144CA0166A0E9FC3BDC033F13C749700675EFC144A0C16DB7AA01290F"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "D9B7F077A0AB24C578E4E5FA491263A07180D64E1D2A247AB352B7C929B56C89"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "149E06BE59729EE0C188E683A0D8C195A1D6867E710154457EA8A68AD622113F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "39392C700A76519F8689976DEB2F95DCE1876EAC2A4003A884CF4F49A56B9AF9"
)
EXPECTED_CHANGED_LITERAL_COUNT = 16

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete PC "
    "EN SC TC records across the full B045 queue are context only; three "
    "complete target records are raw-exact completed Base matches and "
    "thirteen preserve identical source literals with operand-masked "
    "PK-specific calls; all twenty target fragments, twenty-two same-record "
    "prefill companions and one invisible newline companion form sixteen "
    "complete records; sixteen corrected target fragments and four reviewed "
    "unchanged fragments equal their "
    "verified completed Base semantic donor; policy, construction, castle "
    "town, formal order acceptance, castle-lord attachment, unused-label, "
    "counterintelligence, frontier defense and spear-skill terminology and "
    "speaker register are reviewed; dynamic names, particles, punctuation, "
    "protected outer whitespace, line counts, pristine and current call "
    "graphs, inline runtime tokens, source-current runtime gap differences, "
    "reverse-order overlay, reverse restoration, two-run reproduction, "
    "tamper rejection, outside-scope identity and Steam read-only state are "
    "guarded; Base runtime verification is not inherited and every PK "
    "fragment remains runtime pending"
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1148_template",
        TEMPLATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {TEMPLATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_template()
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
runtime_controls = TEMPLATE.runtime_controls
mask_call_operands = TEMPLATE.mask_call_operands


def patch_template_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
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
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
]:
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 98
        or len(visible) != 199
        or visible[0] != "6:4370:0"
        or visible[-1] != "6:4467:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B045 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "6:4438:0"
        or queue_slice[-1] != "6:4467:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if len(prefilled) != 45:
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
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
        )
        for coordinate in prefilled
    )
    return visible, queue_slice, prefilled, prefill_context


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice, prefilled, prefill_context = queue_evidence(prepared)
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def context_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    patch_template_globals()
    return TEMPLATE.context_evidence(records_by_label)


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = context_evidence(records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if any(
        ("pk_msggame", *coordinate_key(coordinate))
        not in prepared.visible_targets
        for coordinate in TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} target visibility drifted")


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    raise RuntimeError(f"segment {SEGMENT} missing Base match kind")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_invisible: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        base_record = base_source[(BLOCK_ID, base_record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source,
            (BLOCK_ID, base_record_id),
        )
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or pk_literals != base_literals
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base literal match drifted: "
                f"{record_id}"
            )
        kind = base_match_kind(record_id)
        raw_exact = pk_record.data == base_record.data
        masked_equal = (
            mask_call_operands(pk_record)
            == mask_call_operands(base_record)
        )
        if (
            (kind == "raw_exact" and not raw_exact)
            or (kind == "operand_masked" and (raw_exact or not masked_equal))
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source match drifted: "
                f"{record_id}"
            )
        literal_evidence: list[tuple[Any, ...]] = []
        owners: list[str] = []
        translations: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in INVISIBLE_CURRENT_COORDINATES:
                actual = current_literals[literal_id]
                if actual != pk_literals[literal_id]:
                    raise RuntimeError(
                        f"segment {SEGMENT} invisible companion drifted"
                    )
                literal_evidence.append(
                    (coordinate, (), (), actual, "invisible_current")
                )
                owners.append("invisible_current")
                translations.append(actual)
                seen_invisible.add(coordinate)
                continue
            reference = BASE_DONOR_COORDINATES[coordinate][0]
            base_row = base_rows.get(reference)
            if (
                base_row is None
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing completed Base row: "
                    f"{reference}"
                )
            donor = str(base_row["translation"])
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            else:
                prefill_row = prefill_rows.get(coordinate)
                if prefill_row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                actual = str(prefill_row["translation"])
                owner = "prefill"
                seen_prefill.add(coordinate)
            if actual != donor:
                raise RuntimeError(
                    f"segment {SEGMENT} Base donor drifted: {coordinate}"
                )
            literal_evidence.append(
                (
                    coordinate,
                    (reference,),
                    (
                        (
                            reference,
                            donor,
                            str(base_row["semantic_review"]),
                            str(base_row["runtime_review"]),
                        ),
                    ),
                    actual,
                    owner,
                )
            )
            owners.append(owner)
            translations.append(actual)
        base_evidence.append(
            (
                record_id,
                base_record_id,
                kind,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                pk_literals,
                literal_texts(
                    base_current,
                    (BLOCK_ID, base_record_id),
                ),
                tuple(
                    value.hex().upper() for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper() for value in gap_bytes(base_record)
                ),
                mask_call_operands(pk_record),
                mask_call_operands(base_record),
                tuple(literal_evidence),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                runtime_controls(pk_record),
                runtime_controls(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                ),
                kind,
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
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
    guarded_digest("Base context", base, EXPECTED_BASE_CONTEXT_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def call_graph_evidence(prepared: Any) -> tuple[Any, ...]:
    patch_template_globals()
    return TEMPLATE.call_graph_evidence(prepared)


def assert_call_graphs(prepared: Any) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(prepared),
        EXPECTED_CALL_GRAPH_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            key[:2],
        )[key[2]]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def unchecked_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    pk = prepared.resources["pk_msggame"]
    current = records_by_label["current"]
    replacements = {
        coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        pk.current_blob,
        replacements,
    )
    reverse_order_candidate = ENGINE.rebuild_packed_with_literals(
        pk.current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if candidate != reverse_order_candidate:
        raise RuntimeError(
            f"segment {SEGMENT} reverse-order overlay drifted"
        )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    target_record_keys = {
        (BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS
    }
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
        or set(replacements) != {
            coordinate_key(coordinate)
            for coordinate in TARGET_COORDINATES
        }
    ):
        raise RuntimeError(f"segment {SEGMENT} candidate universe drifted")
    for key, current_record in current.items():
        if (
            key not in target_record_keys
            and candidate_records[key].data != current_record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        expected = list(literal_texts(current, key))
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                expected[literal_id] = TRANSLATIONS[coordinate]
        if (
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            or literal_texts(candidate_records, key) != tuple(expected)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target record drifted: {key}"
            )
    reversed_blob = ENGINE.rebuild_packed_with_literals(candidate, reverse)
    if reversed_blob != pk.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    changed = sum(
        translation
        != literal_texts(current, coordinate_key(coordinate)[:2])[
            coordinate_key(coordinate)[2]
        ]
        for coordinate, translation in TRANSLATIONS.items()
    )
    return candidate, sha256_bytes(candidate), changed


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_match_kind": base_match_kind(record_id),
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "invisible_current_companion_reviewed": record_id == 4462,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(prepared, records)
    assert_base_and_complete_assembly(prepared, records)
    assert_call_graphs(prepared)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        references = BASE_DONOR_COORDINATES[coordinate]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate": references[0],
                "base_context_reference_coordinates": references,
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "speaker_style": style_map[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records, record_id),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
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
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 20
        or len(validated) != 20
        or counts != Counter({"runtime_fragment_pending": 20})
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
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B045_S1148",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 65,
                "exact_reuse_prefill_count": 45,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "all_forty_five_prefills_guarded": True,
                "same_record_prefill_companions_guarded": True,
                "invisible_current_companion_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "source_and_current_call_graphs_guarded": True,
                "source_current_runtime_gap_differences_guarded": True,
                "inline_runtime_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "current_runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
