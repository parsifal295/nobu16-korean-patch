#!/usr/bin/env python3
"""Build source-redacted PK B043 segment 1142 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch042_segment1139.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B043_S1142.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B043_S1140.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B043_S1141.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1142
QUEUE_BATCH_ID = "pk_msggame-B043"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_FIRST_RECORD = 4156
QUEUE_LAST_RECORD = 4262
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4244:1",
    "6:4250:0",
    "6:4251:0",
    "6:4260:0",
    "6:4260:2",
    "6:4260:3",
    "6:4260:4",
    "6:4261:0",
    "6:4261:2",
    "6:4261:3",
    "6:4261:4",
    "6:4261:5",
    "6:4262:0",
)
TRANSLATIONS = {
    "6:4244:1": "시겠습니까?",
    "6:4250:0": "에서",
    "6:4251:0": "에서",
    "6:4260:0": "을(를)",
    "6:4260:2": ", 무",
    "6:4260:3": ", 지",
    "6:4260:4": ", 정",
    "6:4261:0": "을(를)",
    "6:4261:2": ":",
    "6:4261:3": ",",
    "6:4261:4": ",",
    "6:4261:5": ",",
    "6:4262:0": "통",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (4244, 4250, 4251, 4260, 4261, 4262)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4244: 2,
    4250: 2,
    4251: 2,
    4260: 6,
    4261: 7,
    4262: 1,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 30 for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (4250, 4251, 4260, 4261, 4262)
OPERAND_MASKED_BASE_RECORD_IDS = (4244,)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
)
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    (f"6:{base_record_id}:{literal_id}",)
    for record_id, base_record_id in BASE_RECORD_MAPPING.items()
    for literal_id in range(EXPECTED_ARITY[record_id])
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    4155,
    4156,
    4213,
    4214,
    4243,
    4245,
    4249,
    4252,
    4259,
    4262,
    4263,
)
EXPECTED_CONTROLS_BY_RECORD = {
    4244: ((598, 1066), ("026432014356020000",)),
    4250: ((), ("029632", "023C")),
    4251: ((), ("029632", "023C")),
    4260: (
        (),
        ("024633", "029632", "0232", "0233", "0234", "0235"),
    ),
    4261: (
        (),
        (
            "024633",
            "029632",
            "026432",
            "023C",
            "023D",
            "023E",
            "023F",
        ),
    ),
    4262: ((), ()),
}
EXPECTED_CALL_ROOTS = (598, 1066)

SPEAKER_STYLE = (
    (4244, "instruction_confirmation_prompt"),
    (4250, "control_seizure_cancel_notice"),
    (4251, "construction_cancel_notice"),
    (4260, "castle_lord_appointment_fixed_stats_prompt"),
    (4261, "castle_lord_appointment_dynamic_stats_prompt"),
    (4262, "leadership_stat_abbreviation"),
)
TERMINOLOGY_POLICY = (
    ("instruction", "지시"),
    ("control", "장악"),
    ("construction", "건설"),
    ("cancel", "중단"),
    ("castle_lord", "영주"),
    ("castle_ability", "성 능력"),
    ("leadership", "통"),
    ("valor", "무"),
    ("intelligence", "지"),
    ("politics", "정"),
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
    "A4D37420E8B388B5124EB805FAE2F898AD8315E3ABFA1301096EE76D65DB3413"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "339BB0A35B5D00FD32A9EA63714BABFB3A62ABD31F6F2C225420AA49B796D1E2"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "37F49D8ECD2C142E108FF0D361C6A34B9F03F70B7341C8FFE0070B778AC239B5"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "68F1AD340486018BB43E229E62E818911E8E495FEB438DFAE6064669D9195062"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "FBDA86D8F9E28338A4F04DE972B3EFF99D2259BDF7A7C04AB1464B1AE947FEBA"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "DFC3A54EBEEFE418AF48B63A0430B5AD670C8949E781E94B1E3B432B8CEF4AA8"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "8E961E2A7A28586AE27CB6068D4A66D28BAB90C6588F340B6888FC38640C288D"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "9306A0765FEB55D7B845DAFB25D6A6C5E03A0EE6030A395ECE814A406B6CCF42"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "EF16656986612662BA2A9143100CA66604DBA85E1A696DFCAFDFE390B6E75C0D"
)
EXPECTED_BOUNDARY_SHA256 = (
    "91F1B9BF43835CC1C622B6CDD73918EB24A8C17540FDBA8932112D73C9404D56"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "EBD43A9C0073E25EF0D8194B2D362C1934924C28D09F00166122F1E05B83BCD3"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "B1080CB9FF058F89A7567DDF81A97B6DAE66F637AC4BBDF0CC6C0F4E08E4374B"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "CADF0CD3290BD74658E1E8030F2DA9D37C643B9960E8FF6F3B339FEB110B67BB"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "EFD4184A3507CCC9085485E1F6DD41E9957DE4C1ADB5C2B2DBD3107B16836D99"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "317B3CD21CA08FD3AA5DFAE3B4C72D025D979B5AFB9A2A8EE17B6B16F2A18AC1"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "BA44122309460843E86426D4DED934BDE8DB776796CE6676987ED9513FDE630B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "06FB855589B37A0A597E17B145CA45714FA4BAB3CD95A63156D90ED1568A5C73"
)
EXPECTED_CANDIDATE_SHA256 = (
    "34D67759D0EE671586005C6D7B29152156B34EC9548DEDED30B1E38AC490D5F4"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records across the full B043 queue are context only; "
    "five complete target records are raw-exact completed Base matches "
    "and one preserves identical source literals with operand-masked "
    "PK-specific calls; all thirteen residual fragments and seven same-"
    "record prefill companions form six complete records; every target "
    "translation and companion equals its verified Base semantic donor; "
    "seven confirmation, dynamic-particle and punctuation fragments are "
    "corrected while six approved fragments stay unchanged; instruction, "
    "control, construction, cancellation, castle-lord appointment and "
    "leadership, valor, intelligence and politics abbreviation terminology "
    "and system-prompt register are reviewed; dynamic names, stat values, "
    "particles, punctuation, protected outer whitespace, line counts, live "
    "call graphs, inline runtime tokens, runtime gaps, reverse-order "
    "overlay, reverse restoration, two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are guarded; every "
    "new output is optional, Base runtime verification is not inherited, "
    "and every PK fragment remains runtime pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1142_template",
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


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    calls = tuple(
        int.from_bytes(match.group(1), "little")
        for value in gaps
        for match in DIRECT_CALL_RE.finditer(value)
    )
    tokens = tuple(
        value.hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )
    return calls, tokens


def mask_call_operands(record: Any) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01([\x43\x4A]).{4}",
            lambda match: b"\x01" + match.group(1) + b"\xFF" * 4,
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gap_bytes(record)
    )


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
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
        len(queue_rows) != 107
        or len(visible) != 200
        or visible[0] != "6:4156:0"
        or visible[-1] != "6:4262:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B043 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:4214:0"
        or queue_slice[-1] != "6:4262:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 53:
        raise RuntimeError(f"segment {SEGMENT} prefill slice count drifted")
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
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
                    "pk_source_gap_template_sha256"
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
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
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


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in CONTEXT_RECORD_IDS
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", corpus, EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        ("runtime control", controls, EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(source != current for _, source, current in gaps)
        or any(
            runtime != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, runtime in controls
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    raise RuntimeError(f"segment {SEGMENT} missing Base match kind")


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
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
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        base_record = base_source[(BLOCK_ID, base_record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current,
            (BLOCK_ID, base_record_id),
        )
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or len(base_literals) != EXPECTED_ARITY[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        kind = base_match_kind(record_id)
        raw_exact = pk_record.data == base_record.data
        literals_equal = pk_literals == base_literals
        masked_equal = (
            mask_call_operands(pk_record)
            == mask_call_operands(base_record)
        )
        if (
            (kind == "raw_exact" and not (raw_exact and literals_equal))
            or (
                kind == "operand_masked"
                and (raw_exact or not literals_equal or not masked_equal)
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source match drifted: "
                f"{record_id}"
            )
        donor_rows: list[tuple[Any, ...]] = []
        owners: list[str] = []
        translations: list[str] = []
        references_by_literal: list[tuple[str, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            references = BASE_DONOR_COORDINATES[coordinate]
            reference = references[0]
            base_row = base_rows.get(reference)
            if (
                base_row is None
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing verified Base row: "
                    f"{reference}"
                )
            donor_translation = str(base_row["translation"])
            donor_rows.append(
                (
                    coordinate,
                    references,
                    (
                        (
                            reference,
                            donor_translation,
                            str(base_row["semantic_review"]),
                            str(base_row["runtime_review"]),
                        ),
                    ),
                    donor_translation,
                )
            )
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
            if actual != donor_translation:
                raise RuntimeError(
                    f"segment {SEGMENT} Base translation drifted: "
                    f"{coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            references_by_literal.append(references)
        base_evidence.append(
            (
                record_id,
                base_record_id,
                kind,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                pk_literals,
                base_literals,
                base_current_literals,
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_record)
                ),
                mask_call_operands(pk_record),
                mask_call_operands(base_record),
                tuple(donor_rows),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references_by_literal),
                runtime_controls(pk_record),
                kind,
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        | set(OPERAND_MASKED_BASE_RECORD_IDS)
        != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(OPERAND_MASKED_BASE_RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "complete assembly",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[tuple[Any, ...], tuple[tuple[int, int], ...]]:
    pending: deque[tuple[int, int]] = deque([root])
    visited: set[tuple[int, int]] = set()
    edges: list[tuple[Any, ...]] = []
    terminals: list[tuple[int, int]] = []
    while pending:
        coordinate = pending.popleft()
        if coordinate in visited:
            continue
        if coordinate not in records:
            raise RuntimeError(
                f"segment {SEGMENT} missing call target: {coordinate}"
            )
        visited.add(coordinate)
        joined = b"".join(gap_bytes(records[coordinate]))
        next_coordinates: list[tuple[int, int]] = []
        for opcode in (b"\x01\x43", b"\x01\x4A"):
            for match in re.finditer(
                re.escape(opcode) + b"(.{4})",
                joined,
                re.DOTALL,
            ):
                operand = int.from_bytes(match.group(1), "little")
                target = (operand // 10_000, operand % 10_000)
                edges.append(
                    (
                        coordinate,
                        opcode.hex().upper(),
                        operand,
                        target,
                    )
                )
                next_coordinates.append(target)
                pending.append(target)
        if not next_coordinates:
            terminals.append(coordinate)
    graph = tuple(
        (
            coordinate,
            sha256_bytes(records[coordinate].data),
            literal_texts(records, coordinate),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[coordinate])
            ),
        )
        for coordinate in sorted(visited)
    ) + (("edges", tuple(sorted(edges))),)
    return graph, tuple(sorted(terminals))


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = reachable_call_graph(
            current_records,
            (0, operand),
        )
        terminal_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in terminals
        )
        if (
            not graph
            or not terminals
            or any(len(values) > 1 for values in terminal_literals)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
    guarded_digest(
        "call graph",
        tuple(evidence),
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
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime evidence drifted")
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
        "live_pk_call_graphs_reviewed": record_id == 4244,
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
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
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B043_S1142",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 53,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "live_pk_call_root_count": len(EXPECTED_CALL_ROOTS),
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
                "all_fifty_three_prefills_guarded": True,
                "same_record_prefill_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "direct_calls_and_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
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
