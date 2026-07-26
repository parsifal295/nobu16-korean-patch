#!/usr/bin/env python3
"""Build source-redacted PK B039 segment 1129 residual decisions."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch038_segment1125.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B039_S1129.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B039_S1128.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B039_S1130.private.v1.jsonl",
)

SEGMENT = 1129
QUEUE_BATCH_ID = "pk_msggame-B039"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 3752
QUEUE_LAST_RECORD = 3866

TARGET_COORDINATES = tuple(
    f"6:{record_id}:2" for record_id in range(3794, 3804)
)
TRANSLATIONS = {
    coordinate: "의" for coordinate in TARGET_COORDINATES
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = tuple(range(3794, 3804))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BASE_RECORD_MAPPING = {
    record_id: record_id - 7 for record_id in TARGET_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    f"6:{record_id}:2": f"6:{base_record_id}:2"
    for record_id, base_record_id in BASE_RECORD_MAPPING.items()
}
PREFILL_COMPANION_COORDINATES = tuple(
    coordinate
    for record_id in TARGET_RECORD_IDS
    for coordinate in (
        f"6:{record_id}:0",
        f"6:{record_id}:3",
    )
)
INVISIBLE_CURRENT_COORDINATES = tuple(
    f"6:{record_id}:1" for record_id in TARGET_RECORD_IDS
)
BOUNDARY_RECORD_IDS = tuple(range(3791, 3807))

EXPECTED_GAPS = (
    "",
    "014374020000",
    "026432",
    "023C",
    "01432A040000050505",
)
EXPECTED_PK_CONTROLS = ((628, 1066), ("026432", "023C"))
EXPECTED_BASE_GAPS = (
    "",
    "014368020000",
    "026432",
    "023C",
    "01431E040000050505",
)
EXPECTED_BASE_CONTROLS = ((616, 1054), ("026432", "023C"))
EXPECTED_MASKED_GAPS = (
    "",
    "0143FFFFFFFF",
    "026432",
    "023C",
    "0143FFFFFFFF050505",
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
EXPECTED_QUEUE_SLICE_SHA256 = (
    "D985C35B6D1A3DDB6F50D39FD816EF4AD972B68B71350086F4A0D146A39F2159"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "552CB409C9E407633B2B8AFDB8E4521C06B125CE5DC867F74B3C470D730E8309"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "BB49CD650B9C1A3FBEA71193939E77027835E1FBA6DE3A6DBB4FCF12A51B2DD4"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3C9209E9CDBEC3E627E343A0E06FEE4162FFBC65CFC319A882F1969C7CD763C7"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "6182E3BC625778DB92D470566D5482DA12EA4A4AD409B30CBDA2A1A2DDAAD1C0"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "25333175F7B0E7DBE13A75EACF79488F0104DB6F3AC8364236687F58F7636758"
)
EXPECTED_BOUNDARY_SHA256 = (
    "952CD0D331433B645429F53C5D3F8E68BAF9D58B742049F02F6FE3A616EA79D9"
)
EXPECTED_RUNTIME_CONTRACT_SHA256 = (
    "5768A1AB12364E62D97AB1C022D022847AD970B75DADBF0681022264E967A76E"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "5F3AAD9FE668C6F1997686C3B957ED9FE3074E32B2A941A4391BA32B58E645C9"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "1F79B3B7B2D3E1C5BEC68CC0773851A080F11E5EFD462E59551046CA72AD4A2E"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "05372997D3A3015A66E8EDF4C492B6FECD4E807EE37FF90020399A26714E958F"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "914C69E2923D1CAB6FB93CD938F41221A9659A3A288A2FBD57090D693D191F7C"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "F02B02529110E4A773B18697EBE3AC121C8E2B9117EAD94D54088677487F7F56"
)
EXPECTED_REGISTER_POLICY_SHA256 = (
    "F26BA2FFD983DC1E76B3256C0C0B888A9877D966C6B55364B27A7313A8102C45"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "6182E3BC625778DB92D470566D5482DA12EA4A4AD409B30CBDA2A1A2DDAAD1C0"
)
EXPECTED_CANDIDATE_SHA256 = EXPECTED_STEAM_PK_SHA256
EXPECTED_CHANGED_LITERAL_COUNT = 0

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; fifty-seven Base exact-reuse "
    "prefill rows and ten residual rows cover the assigned sixty-seven "
    "visible literals; ten identical four-literal runtime templates are "
    "assembled with twenty prefill companions and ten invisible newline "
    "companions; the matching Base record-minus-seven sequence pins the "
    "wording while PK call operands 628 and 1066 remain authoritative "
    "and Base operands 616 and 1054 are reference only; the neutral "
    "possessive particle is retained because its dynamic neighbors "
    "supply the request and target names; acceptance, undertaking and "
    "formal assurance terminology and ten surrounding speaker-register "
    "variants are reviewed; inline tokens, direct calls, protected outer "
    "whitespace, line counts, complete-record assembly, multilingual "
    "context, boundaries, reverse overlay, zero-change candidate "
    "identity, two-run reproduction, tamper rejection, outside-scope "
    "records and read-only inputs are guarded; all ten dynamic fragments "
    "remain runtime pending"
)
DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1129_common",
        COMMON_PATH,
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


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def guarded_raw_digest(label: str, value: bytes, expected: str) -> str:
    actual = sha256_bytes(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,)
        if resource == "base_msggame"
        else tuple(
            sorted(
                DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
            )
        )
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


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
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
        len(queue_rows) != 114
        or len(visible) != 198
        or visible[0] != f"6:{QUEUE_FIRST_RECORD}:0"
        or visible[-1] != f"6:{QUEUE_LAST_RECORD}:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B039 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3794:0"
        or queue_slice[-1] != "6:3838:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "EXPECTED_QUEUE_SLICE_SHA256",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 57:
        raise RuntimeError(f"segment {SEGMENT} prefill count drifted")
    guarded_digest(
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
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


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    calls = tuple(
        int.from_bytes(match.group(1), "little")
        for value in gaps
        for match in DIRECT_CALL_RE.finditer(value)
    )
    inline = tuple(
        value.hex().upper() for value in gaps if value.startswith(b"\x02")
    )
    return calls, inline


def masked_gaps(record: Any) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01\x43.{4}",
            b"\x01\x43\xFF\xFF\xFF\xFF",
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gap_bytes(record)
    )


def assert_expected_pk_runtime_record(record: Any) -> None:
    if (
        tuple(value.hex().upper() for value in gap_bytes(record))
        != EXPECTED_GAPS
        or runtime_controls(record) != EXPECTED_PK_CONTROLS
        or masked_gaps(record) != EXPECTED_MASKED_GAPS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK runtime record validation failed"
        )


def assert_context_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"], coordinate_key(coordinate)[:2]
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"], coordinate_key(coordinate)[:2]
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
                records_by_label[label], (BLOCK_ID, record_id)
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    runtime_contract = tuple(
        (
            label,
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
            masked_gaps(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        (
            "EXPECTED_SOURCE_TARGET_SHA256",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "EXPECTED_CURRENT_TARGET_SHA256",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "EXPECTED_CONTEXT_CORPUS_SHA256",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "EXPECTED_BOUNDARY_SHA256",
            boundary,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "EXPECTED_RUNTIME_CONTRACT_SHA256",
            runtime_contract,
            EXPECTED_RUNTIME_CONTRACT_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    for label, record_id, gaps, controls, masked in runtime_contract:
        if (
            gaps != EXPECTED_GAPS
            or controls != EXPECTED_PK_CONTROLS
            or masked != EXPECTED_MASKED_GAPS
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK runtime drifted: {record_id}"
            )
        assert_expected_pk_runtime_record(
            records_by_label[label][(BLOCK_ID, record_id)]
        )


def assert_base_companions_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[tuple[int, int, int], str]:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = decision_map("base_msggame")
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
    companion_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    complete_replacements: dict[tuple[int, int, int], str] = {}
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_invisible: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_literals = literal_texts(
            records_by_label["jp"], (BLOCK_ID, record_id)
        )
        base_literals = literal_texts(
            base_source, (BLOCK_ID, base_record_id)
        )
        base_current_literals = literal_texts(
            base_current, (BLOCK_ID, base_record_id)
        )
        base_record = base_source[(BLOCK_ID, base_record_id)]
        if (
            pk_literals != base_literals
            or tuple(
                value.hex().upper() for value in gap_bytes(base_record)
            )
            != EXPECTED_BASE_GAPS
            or runtime_controls(base_record) != EXPECTED_BASE_CONTROLS
            or masked_gaps(base_record) != EXPECTED_MASKED_GAPS
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
            )
        base_translations: list[str] = []
        for literal_id in range(len(base_literals)):
            base_coordinate = f"6:{base_record_id}:{literal_id}"
            base_row = base_rows.get(base_coordinate)
            if base_row is None:
                if literal_id != 1 or base_current_literals[literal_id] != "\n":
                    raise RuntimeError(
                        f"segment {SEGMENT} missing Base decision: "
                        f"{base_coordinate}"
                    )
                base_translations.append(base_current_literals[literal_id])
            else:
                base_translations.append(str(base_row["translation"]))
        base_evidence.append(
            (
                record_id,
                base_record_id,
                sha256_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)].data
                ),
                sha256_bytes(base_record.data),
                pk_literals,
                tuple(base_translations),
                EXPECTED_PK_CONTROLS,
                EXPECTED_BASE_CONTROLS,
            )
        )

        owners: list[str] = []
        completed: list[str] = []
        for literal_id in range(len(pk_literals)):
            coordinate = f"6:{record_id}:{literal_id}"
            key = (BLOCK_ID, record_id, literal_id)
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                translation = str(row["translation"])
                owner = "prefill"
                seen_prefill.add(coordinate)
                companion_evidence.append(
                    (
                        coordinate,
                        translation,
                        str(row["source_record_raw_sha256"]),
                        str(row["current_ko_utf16le_sha256"]),
                    )
                )
            elif coordinate in INVISIBLE_CURRENT_COORDINATES:
                translation = literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )[literal_id]
                owner = "invisible_current"
                seen_invisible.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: {coordinate}"
                )
            owners.append(owner)
            completed.append(translation)
            complete_replacements[key] = translation
        if tuple(completed) != tuple(base_translations):
            raise RuntimeError(
                f"segment {SEGMENT} complete Base wording drifted: "
                f"{record_id}"
            )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(completed),
                runtime_controls(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                ),
                runtime_controls(base_record),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "EXPECTED_BASE_CONTEXT_SHA256",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "EXPECTED_PREFILL_COMPANION_SHA256",
        tuple(companion_evidence),
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    guarded_digest(
        "EXPECTED_ASSEMBLY_POLICY_SHA256",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )
    return complete_replacements


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "EXPECTED_TARGET_COORDINATE_SHA256",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TRANSLATION_POLICY_SHA256",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    terminology = (
        ("request_acceptance", "이야기는 알겠다"),
        ("possessive_particle", "의"),
        ("object_particle", "을(를)"),
        ("formal_assurance", "확실히 맡다"),
    )
    guarded_digest(
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        terminology,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    register_policy = tuple(
        (
            record_id,
            f"request_acceptance_speaker_variant_{ordinal:02d}",
            "neutral_dynamic_possessive_particle",
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
            False,
        )
        for ordinal, record_id in enumerate(TARGET_RECORD_IDS)
    )
    guarded_digest(
        "EXPECTED_REGISTER_POLICY_SHA256",
        register_policy,
        EXPECTED_REGISTER_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"], (block_id, record_id)
        )[literal_id]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation != current_text
            or translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} neutral fragment drifted: {coordinate}"
            )


def assert_candidate_records(
    current_records: dict[tuple[int, int], Any],
    candidate_records: dict[tuple[int, int], Any],
) -> None:
    target_keys = {
        (BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS
    }
    if (
        len(current_records) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(f"segment {SEGMENT} candidate universe drifted")
    for key, record in current_records.items():
        if (
            key not in target_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed outside scope: {key}"
            )
    for key in target_keys:
        if gap_bytes(candidate_records[key]) != gap_bytes(
            current_records[key]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed runtime gaps: {key}"
            )


def build_candidates(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    complete_replacements: dict[tuple[int, int, int], str],
) -> tuple[bytes, str, int, bytes]:
    resource = prepared.resources["pk_msggame"]
    current_records = records_by_label["current"]
    replacements = {
        coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current_records, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob, replacements
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    assert_candidate_records(current_records, candidate_records)
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        if (
            literal_texts(candidate_records, key[:2])[key[2]]
            != translation
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate literal drifted: {coordinate}"
            )
    if (
        ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} reverse overlay drifted")
    changed = sum(
        translation != reverse[key]
        for key, translation in replacements.items()
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed literal count drifted: {changed}"
        )
    candidate_sha256 = guarded_raw_digest(
        "EXPECTED_CANDIDATE_SHA256",
        candidate,
        EXPECTED_CANDIDATE_SHA256,
    )
    if candidate != resource.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} zero-change candidate identity drifted"
        )

    complete_reverse = {
        key: literal_texts(current_records, key[:2])[key[2]]
        for key in complete_replacements
    }
    complete_candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob, complete_replacements
    )
    complete_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(complete_candidate).archive
    )
    assert_candidate_records(current_records, complete_records)
    for key, translation in complete_replacements.items():
        if literal_texts(complete_records, key[:2])[key[2]] != translation:
            raise RuntimeError(
                f"segment {SEGMENT} complete assembly drifted: {key}"
            )
    if (
        ENGINE.rebuild_packed_with_literals(
            complete_candidate, complete_reverse
        )
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete assembly reverse drifted"
        )
    guarded_raw_digest(
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256",
        complete_candidate,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )
    return candidate, candidate_sha256, changed, complete_candidate


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    if (
        tuple(value.hex().upper() for value in gap_bytes(source))
        != EXPECTED_GAPS
        or gap_bytes(current) != gap_bytes(source)
        or runtime_controls(source) != EXPECTED_PK_CONTROLS
        or runtime_controls(current) != EXPECTED_PK_CONTROLS
        or masked_gaps(source) != EXPECTED_MASKED_GAPS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: {record_id}"
        )
    return {
        "runtime_category":
        "request_acceptance_dynamic_possessive_fragment",
        "speaker_register_variant":
        f"request_acceptance_speaker_variant_{record_id - 3794:02d}",
        "source_record_gap_sha256": canonical_sha256(EXPECTED_GAPS),
        "current_record_gap_sha256": canonical_sha256(EXPECTED_GAPS),
        "source_direct_call_operands": EXPECTED_PK_CONTROLS[0],
        "current_direct_call_operands": EXPECTED_PK_CONTROLS[0],
        "base_reference_direct_call_operands":
        EXPECTED_BASE_CONTROLS[0],
        "source_inline_token_hex": EXPECTED_PK_CONTROLS[1],
        "current_inline_token_hex": EXPECTED_PK_CONTROLS[1],
        "source_current_runtime_gap_equal": True,
        "pk_call_operands_authoritative": True,
        "base_call_operands_reference_only": True,
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companions_reviewed": True,
        "invisible_newline_companion_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "base_wording_contextually_adapted": False,
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
    bytes,
    tuple[str, ...],
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    complete_replacements = assert_base_companions_and_assembly(
        prepared, records_by_label
    )
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed, complete_candidate = (
        build_candidates(
            prepared, records_by_label, complete_replacements
        )
    )
    if DISCOVERED_PINS:
        return (
            prepared,
            [],
            candidate,
            candidate_sha256,
            changed,
            complete_candidate,
            optional_present,
        )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"], (block_id, record_id)
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
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
                "all_record_literals_reviewed": True,
                "prefill_companions_reviewed": True,
                "invisible_newline_companion_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(records_by_label, record_id),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        complete_candidate,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1129-tamper-", dir=DECISIONS_ROOT
    ) as directory:
        tampered_path = (
            Path(directory) / "tampered.private.v1.jsonl"
        )
        ENGINE.atomic_write(tampered_path, ENGINE.jsonl(tampered_rows))
        try:
            ENGINE.validate_decisions(
                prepared, tampered_path, require_complete=False
            )
        except ENGINE.RetranslationError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} source tamper was accepted"
            )
    tampered_policy = dict(TRANSLATIONS)
    tampered_policy[TARGET_COORDINATES[0]] += "X"
    if (
        canonical_sha256(tuple(tampered_policy.items()))
        == EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} policy tamper was accepted"
        )
    tampered_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        {
            coordinate_key(coordinate): translation
            for coordinate, translation in tampered_policy.items()
        },
    )
    if (
        tampered_candidate == candidate
        or sha256_bytes(tampered_candidate)
        == EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate tamper was accepted"
        )
    original_record = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )[(BLOCK_ID, TARGET_RECORD_IDS[0])]
    for pk_operand, base_operand in (
        ("014374020000", "014368020000"),
        ("01432A040000", "01431E040000"),
    ):
        tampered_data = bytearray(original_record.data)
        source = bytes.fromhex(pk_operand)
        offset = tampered_data.find(source)
        if offset < 0:
            raise RuntimeError(f"segment {SEGMENT} PK operand is absent")
        tampered_data[offset : offset + len(source)] = bytes.fromhex(
            base_operand
        )
        tampered_record = type(original_record)(
            block_id=original_record.block_id,
            record_id=original_record.record_id,
            relative_offset=original_record.relative_offset,
            data=bytes(tampered_data),
        )
        try:
            assert_expected_pk_runtime_record(tampered_record)
        except RuntimeError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} Base operand tamper was accepted"
            )


def main() -> int:
    first = build_rows()
    if DISCOVERED_PINS:
        print(
            json.dumps(
                DISCOVERED_PINS,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        complete_candidate,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or complete_candidate != second[5]
        or optional_present != second[6]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
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
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 10
        or len(validated) != 10
        or counts != Counter({"runtime_fragment_pending": 10})
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
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B039_S1129",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 57,
                "base_semantic_reference_count": len(rows),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_newline_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "zero_change_candidate_identity": True,
                "candidate_sha256": candidate_sha256,
                "complete_assembly_sha256":
                EXPECTED_COMPLETE_ASSEMBLY_SHA256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "base_semantics_pinned": True,
                "pk_call_operands_authoritative": True,
                "base_call_operands_reference_only": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "prefill_companions_guarded": True,
                "invisible_newline_companions_guarded": True,
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
                "complete_assembly_reverse_exact": True,
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
