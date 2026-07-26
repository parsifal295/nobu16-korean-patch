#!/usr/bin/env python3
"""Build source-redacted PK B037 segment 1122 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch036_segment1121.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B037_S1122.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B036_S1121.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B037_S1123.private.v1.jsonl",
)

SEGMENT = 1122
QUEUE_BATCH_ID = "pk_msggame-B037"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:3540:0", "6:3540:1", "6:3544:0", "6:3547:3",
    "6:3548:0", "6:3548:1", "6:3548:3", "6:3550:0",
    "6:3550:2", "6:3550:4", "6:3551:2", "6:3552:1",
    "6:3553:3", "6:3554:1", "6:3554:3", "6:3555:1",
    "6:3556:0", "6:3556:3",
)
TRANSLATIONS = {
    "6:3540:0": "의",
    "6:3540:1": "이(가) 일등",
    "6:3544:0": "무슨 일이든",
    "6:3547:3": "인데",
    "6:3548:0": "라 하",
    "6:3548:1": "나\n",
    "6:3548:3": "!",
    "6:3550:0": "좋아!",
    "6:3550:2": "요\n…",
    "6:3550:4": "만…",
    "6:3551:2": "!",
    "6:3552:1": "!",
    "6:3553:3": "…",
    "6:3554:1": "이(가) 훈공 1위여도 괜찮을까요\n여러분, 그래서는",
    "6:3554:3": "어요",
    "6:3555:1": "…\n",
    "6:3556:0": "이(가)",
    "6:3556:3": "어서 말이네",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3540, 3544, 3547, 3548, 3550, 3551,
    3552, 3553, 3554, 3555, 3556,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BASE_RECORD_MAPPING = {record_id: record_id - 7 for record_id in TARGET_RECORD_IDS}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
PREFILL_COMPANION_COORDINATES = (
    "6:3540:2", "6:3540:3", "6:3544:1", "6:3544:2",
    "6:3547:0", "6:3547:2", "6:3548:2", "6:3550:1",
    "6:3550:3", "6:3551:0", "6:3551:1", "6:3552:0",
    "6:3553:0", "6:3553:1", "6:3553:2", "6:3554:0",
    "6:3554:2", "6:3555:0", "6:3555:2", "6:3555:3",
    "6:3556:1", "6:3556:2",
)
INVISIBLE_CURRENT_COORDINATES = ("6:3547:1",)
BOUNDARY_RECORD_IDS = (3539, 3540, 3543, 3546, 3557, 3569, 3570, 3571)
EXPECTED_GAPS_BY_RECORD = {
    3540: ("023C", "014301000000", "0143EE000000", "014352000000", "050505"),
    3544: ("", "014311000000", "023C", "0143EC020000050505"),
    3547: ("", "014352000000", "014308000000", "014362020000", "050505"),
    3548: ("023C", "01438C020000", "014301000000", "01435A040000", "050505"),
    3550: ("", "023C", "01431A020000", "023C", "0143EA010000", "050505"),
    3551: ("023C", "01432A040000", "0143E2000000", "050505"),
    3552: ("", "014372040000", "050505"),
    3553: ("", "01431A020000", "014308000000", "0143E6020000", "050505"),
    3554: ("", "023C", "014301000000", "0143EC020000", "050505"),
    3555: (
        "", "014356020000", "014311000000", "014332020000",
        "01438E000000050505",
    ),
    3556: ("014301000000", "023C", "014311000000", "01432A010000", "050505"),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3540: ((1, 238, 82), ("023C",)),
    3544: ((17, 748), ("023C",)),
    3547: ((82, 8, 610), ()),
    3548: ((652, 1, 1114), ("023C",)),
    3550: ((538, 490), ("023C", "023C")),
    3551: ((1066, 226), ("023C",)),
    3552: ((1138,), ()),
    3553: ((538, 8, 742), ()),
    3554: ((1, 748), ("023C",)),
    3555: ((598, 17, 562, 142), ()),
    3556: ((1, 17, 298), ("023C",)),
}

EXPECTED_STEAM_PK_SHA256 = "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
EXPECTED_PRISTINE_PK_SHA256 = "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
EXPECTED_PREFILL_SHA256 = "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
EXPECTED_BASE_PROMOTED_SHA256 = "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
EXPECTED_TARGET_COORDINATE_SHA256 = "7B7A105CC334F10A41381903215BCCD917A5A59F7EACD24537B4303F9B5636A9"
EXPECTED_QUEUE_SLICE_SHA256 = "526DE3BEBB518774A0BDEFCED780BBCCC411E481E296DC818D3ABF676278B7E1"
EXPECTED_PREFILLED_COORDINATE_SHA256 = "F1485D34E164699095C475C58973F4B163B6209D9CF7BD5A66F4B681A3DBCD5E"
EXPECTED_SOURCE_TARGET_SHA256 = "A058795A41A1005FD6874B461014391D057D1FD7EF6C447B660777ABC9AD39AB"
EXPECTED_CURRENT_TARGET_SHA256 = "740914A18A46077AB0489810053D902F408737456E9B0153A0B656476A4B94B7"
EXPECTED_CONTEXT_CORPUS_SHA256 = "6DB0F55F596BCB9DE10F1AB0A8B7DDD6B44FFA5CE4D0FE67C1970FF44AB0D694"
EXPECTED_GAP_CONTRACT_SHA256 = "1EC7F22815421C2929DB0F245990A7DC6961952058D9181BE7FFD5F047151CDE"
EXPECTED_BOUNDARY_SHA256 = "40E13AAA95184FAD836DE103C2B6B25C6FDF1C938833C235164FF7116C7B0864"
EXPECTED_RUNTIME_OPERAND_SHA256 = "6DDAC395CDE3901B87A036AFC1C4522A70174D58B711426F54D637B65BFED1ED"
EXPECTED_DYNAMIC_RECORD_SHA256 = "3D8571A15FC34E199521F8110AC213C01A137AB08A6782D6A03727EE3A20F786"
EXPECTED_BASE_CONTEXT_SHA256 = "CF68B80E09884C52D51CFB001761BE70D9913EB4F8D3E99D920BBC9D022386EF"
EXPECTED_PREFILL_COMPANION_SHA256 = "6370CCAD4C96EE0B1910889C6AF0B340DE77B9802C40710508D382DCD670AA61"
EXPECTED_ASSEMBLY_POLICY_SHA256 = "3335A191DA9686937A35B6CC5E46793BC02EDE1F05317706900B5EB2CA6D49CE"
EXPECTED_TERMINOLOGY_POLICY_SHA256 = "CE86638897DA1E437C11862F30E58980CC95D70389A9DC6C6BF7C46FC38F8DBA"
EXPECTED_RUNTIME_CATEGORY_SHA256 = "97EEA7A1B73EA1457FF972B16611759BEF09E13EDC0F1590BD51FD7049B4EE60"
EXPECTED_TRANSLATION_POLICY_SHA256 = "0BDC68A79CB49F754FBD14C12712224916A34BB482822C2EFC52A677F7E93D0C"
EXPECTED_CANDIDATE_SHA256 = "99559A54A15C8F90C7FD63E823A84C170D885FA4DFCAA78FC73030AB7D051574"
EXPECTED_CHANGED_LITERAL_COUNT = 13

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; eleven completed Base exact "
    "full-record donors pin merit-ranking dialogue, historical register, "
    "house service and speaker voice; all eighteen targets use completed "
    "Base wording; twenty-two prefilled companions and one invisible "
    "layout-only current fragment complete all eleven records; all 49 "
    "prefilled queue rows and concurrent neighbor outputs are optional "
    "validated inputs rather than execution dependencies; direct calls, "
    "person and rank tokens, boundaries, protected outer whitespace, line "
    "counts, bytecode gaps, reverse overlay, two-run reproduction, tamper "
    "rejection and read-only inputs are guarded; Base runtime state is not "
    "inherited and every PK target remains runtime pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})")


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1122_common", COMMON_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {COMMON_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_common()
ENGINE = COMMON.ENGINE
sha256_bytes = COMMON.sha256_bytes
canonical_sha256 = COMMON.canonical_sha256
coordinate_key = COMMON.coordinate_key
literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
read_jsonl = COMMON.read_jsonl
context_records = COMMON.context_records


def patch_common_globals() -> None:
    values = {
        "SCRIPT": SCRIPT, "OUTPUT": OUTPUT, "PREFILL": PREFILL,
        "SEGMENT": SEGMENT, "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START, "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID, "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES, "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256": EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(COMMON, name, value)
    COMMON.patch_common_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,) if resource == "base_msggame"
        else tuple(sorted(DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")))
    )
    result: dict[str, dict[str, Any]] = {}
    for path in paths:
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if row.get("resource") == resource and isinstance(coordinate, str):
                result[coordinate] = row
    return result


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    queue_rows = [
        json.loads(line) for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"]) for row in queue_rows
        for target in row["target_literals"] if target["visible"]
    )
    if (
        len(queue_rows) != 104 or len(visible) != 200
        or visible[0] != "6:3540:0" or visible[-1] != "6:3643:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B037 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67 or queue_slice[0] != "6:3540:0"
        or queue_slice[-1] != "6:3570:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    prefill_coordinates = {str(row["coordinate"]) for row in read_jsonl(PREFILL)}
    prefilled = tuple(c for c in queue_slice if c in prefill_coordinates)
    if len(prefilled) != 49:
        raise RuntimeError(f"segment {SEGMENT} prefill slice count drifted")
    guarded_digest(
        "prefilled coordinate", prefilled, EXPECTED_PREFILLED_COORDINATE_SHA256
    )
    existing: dict[str, str] = {}
    for path in sorted(DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if row.get("resource") != "pk_msggame" or not isinstance(coordinate, str):
                raise RuntimeError(f"segment {SEGMENT} mixed predecessor: {path}")
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(c for c in queue_slice if c not in existing)
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


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    calls = tuple(
        int.from_bytes(match.group(1), "little")
        for value in gaps for match in DIRECT_CALL_RE.finditer(value)
    )
    tokens = tuple(value.hex().upper() for value in gaps if value.startswith(b"\x02"))
    return calls, tokens


def assert_context_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            c, literal_texts(records_by_label["jp"], coordinate_key(c)[:2])[
                coordinate_key(c)[2]
            ],
        )
        for c in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            c, literal_texts(records_by_label["current"], coordinate_key(c)[:2])[
                coordinate_key(c)[2]
            ],
        )
        for c in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label, record_id, sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in TARGET_RECORD_IDS
    )
    gaps = tuple(
        (
            record_id,
            tuple(v.hex().upper() for v in gap_bytes(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )),
            tuple(v.hex().upper() for v in gap_bytes(
                records_by_label["current"][(BLOCK_ID, record_id)]
            )),
        )
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label, record_id,
            sha256_bytes(records_by_label[label][(BLOCK_ID, record_id)].data),
            literal_texts(records_by_label[label], (BLOCK_ID, record_id)),
            tuple(v.hex().upper() for v in gap_bytes(
                records_by_label[label][(BLOCK_ID, record_id)]
            )),
        )
        for label in ("jp", "current") for record_id in BOUNDARY_RECORD_IDS
    )
    operands = tuple(
        (label, record_id, runtime_controls(
            records_by_label[label][(BLOCK_ID, record_id)]
        ))
        for label in ("jp", "current") for record_id in TARGET_RECORD_IDS
    )
    actual_dynamic = tuple(
        record_id for record_id in TARGET_RECORD_IDS
        if any(runtime_controls(records_by_label["jp"][(BLOCK_ID, record_id)]))
    )
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", corpus, EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        ("runtime operand", operands, EXPECTED_RUNTIME_OPERAND_SHA256),
        ("dynamic record", actual_dynamic, EXPECTED_DYNAMIC_RECORD_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(
            source != EXPECTED_GAPS_BY_RECORD[record_id] or current != source
            for record_id, source, current in gaps
        )
        or any(
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in operands
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime operand layout drifted")


def assert_base_companions_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted policy drifted")
    base_rows = decision_map("base_msggame")
    prefill_rows = {str(row["coordinate"]): row for row in read_jsonl(PREFILL)}
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    companion_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_invisible: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        base_record = base_source[(BLOCK_ID, base_record_id)]
        pk_literals = literal_texts(records_by_label["jp"], (BLOCK_ID, record_id))
        base_literals = literal_texts(base_source, (BLOCK_ID, base_record_id))
        base_current_literals = literal_texts(
            base_current, (BLOCK_ID, base_record_id)
        )
        if pk_literals != base_literals:
            raise RuntimeError(
                f"segment {SEGMENT} Base source mapping drifted: {record_id}"
            )
        base_evidence.append(
            (
                record_id, base_record_id, sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data), pk_literals, base_literals,
                base_current_literals,
            )
        )
        owners: list[str] = []
        translations: list[str] = []
        for literal_id in range(len(pk_literals)):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = f"6:{base_record_id}:{literal_id}"
            if coordinate in INVISIBLE_CURRENT_COORDINATES:
                actual = literal_texts(
                    records_by_label["current"], (BLOCK_ID, record_id)
                )[literal_id]
                expected = base_current_literals[literal_id]
                owner = "invisible_current"
                seen_invisible.add(coordinate)
            else:
                base_row = base_rows.get(base_coordinate)
                if base_row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing Base decision: {base_coordinate}"
                    )
                expected = str(base_row["translation"])
                if coordinate in TRANSLATIONS:
                    actual = TRANSLATIONS[coordinate]
                    owner = "segment"
                    seen_target.add(coordinate)
                elif coordinate in PREFILL_COMPANION_COORDINATES:
                    row = prefill_rows.get(coordinate)
                    if row is None:
                        raise RuntimeError(
                            f"segment {SEGMENT} missing companion: {coordinate}"
                        )
                    actual = str(row["translation"])
                    owner = "prefill"
                    seen_prefill.add(coordinate)
                    companion_evidence.append(
                        (
                            coordinate, base_coordinate, actual,
                            str(row["source_record_raw_sha256"]),
                            str(row["current_ko_utf16le_sha256"]),
                        )
                    )
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} incomplete owner: {coordinate}"
                    )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} Base assembly drifted: {coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
        assembly_evidence.append(
            (
                record_id, base_record_id, tuple(owners),
                tuple(translations), runtime_controls(pk_record),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest("Base context", tuple(base_evidence), EXPECTED_BASE_CONTEXT_SHA256)
    guarded_digest(
        "prefill companion", tuple(companion_evidence),
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    guarded_digest(
        "assembly policy", tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def runtime_category(record_id: int) -> str:
    return {
        3540: "merit_top_formal_subordinate",
        3544: "merit_service_duty_formal",
        3547: "merit_modest_elder",
        3548: "merit_young_elder",
        3550: "merit_ranked_veteran",
        3551: "merit_highest_honor",
        3552: "merit_leader_capacity",
        3553: "merit_peak_gratitude",
        3554: "merit_feminine_challenge",
        3555: "merit_lifelong_service",
        3556: "merit_office_support",
    }[record_id]


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate", TARGET_COORDINATES, EXPECTED_TARGET_COORDINATE_SHA256
    )
    guarded_digest(
        "translation policy", tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    terminology = (
        ("merit", "훈공"), ("house_duty", "소임"),
        ("assist", "보필"), ("stipend", "녹봉"),
        ("honor", "영예"), ("office", "자리"),
        ("service", "섬기다"), ("elder_register", "말이네"),
    )
    guarded_digest(
        "terminology policy", terminology, EXPECTED_TERMINOLOGY_POLICY_SHA256
    )
    categories = tuple(
        (
            record_id, runtime_category(record_id),
            "runtime_fragment_pending", "pending", "runtime_pending", False,
        )
        for record_id in TARGET_RECORD_IDS
    )
    guarded_digest(
        "runtime category", categories, EXPECTED_RUNTIME_CATEGORY_SHA256
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
            records_by_label["current"], key[:2]
        )[key[2]]
        ENGINE.validate_translation_shape(
            current_text, translation, "runtime_pending", coordinate
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(f"segment {SEGMENT} shape drifted: {coordinate}")


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]], record_id: int
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(f"segment {SEGMENT} dynamic controls drifted")
    return {
        "runtime_category": runtime_category(record_id),
        "source_record_gap_sha256": canonical_sha256(
            tuple(v.hex().upper() for v in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(v.hex().upper() for v in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal": gap_bytes(source) == gap_bytes(current),
        "complete_record_assembly_reviewed": True,
        "prefill_companions_reviewed": True,
        "invisible_layout_fragment_reviewed": record_id == 3547,
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
    Any, list[dict[str, Any]], bytes, str, int, tuple[str, ...]
]:
    patch_common_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(records)
    assert_base_companions_and_assembly(prepared, records)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(prepared, records)
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"], (block_id, record_id)
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        rows.append({
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
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
            "invisible_layout_fragment_reviewed": record_id == 3547,
            "speaker_register_reviewed": True,
            "historical_terminology_reviewed": True,
            "protected_outer_whitespace_preserved": True,
            "base_wording_contextually_adapted": False,
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_context_is_automatic_reuse": False,
            "base_runtime_state_inherited": False,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after": TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "runtime_assembly_evidence": runtime_control_evidence(
                records, record_id
            ),
        })
    return (
        prepared, rows, candidate, candidate_sha256, changed, optional_present
    )


def assert_tamper_rejection(
    prepared: Any, rows: list[dict[str, Any]], candidate: bytes
) -> None:
    patch_common_globals()
    COMMON.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, rows, candidate, candidate_sha256, changed, optional_present = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2] or candidate_sha256 != second[3]
        or changed != second[4] or optional_present != second[5]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    steam_path = prepared.resources["pk_msggame"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 18 or len(validated) != 18
        or counts != Counter({"runtime_fragment_pending": 18})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"]["runtime_promotion_authorized"]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    assert_tamper_rejection(prepared, rows, candidate)
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B037_S1122",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "decision_count": len(rows),
        "scope_classification_counts": dict(counts),
        "exact_reuse_prefill_count": 49,
        "base_semantic_reference_count": len(rows),
        "prefill_companion_count": len(PREFILL_COMPANION_COORDINATES),
        "invisible_layout_companion_count": len(INVISIBLE_CURRENT_COORDINATES),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "candidate_sha256": candidate_sha256,
        "translation_policy_sha256": EXPECTED_TRANSLATION_POLICY_SHA256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "source_and_current_hashes_guarded": True,
        "all_available_predecessors_validated": True,
        "optional_new_outputs_only": True,
        "base_semantics_pinned": True,
        "base_runtime_state_inherited": False,
        "queue_boundaries_guarded": True,
        "prefill_companions_guarded": True,
        "invisible_layout_fragment_guarded": True,
        "complete_multi_literal_records_guarded": True,
        "direct_calls_and_tokens_guarded": True,
        "protected_outer_whitespace_guarded": True,
        "speaker_register_guarded": True,
        "historical_terminology_guarded": True,
        "outside_scope_records_exact": True,
        "runtime_gaps_exact": True,
        "protected_signatures_exact": True,
        "line_counts_preserved": True,
        "reverse_overlay_exact": True,
        "second_run_reproduction_exact": True,
        "tamper_tests_passed": True,
        "tracked_builder_source_redacted": True,
        "runtime_promotion_authorized": False,
        "steam_read_only": True,
        "steam_write_performed": False,
        "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
        "output": str(OUTPUT),
    }, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
