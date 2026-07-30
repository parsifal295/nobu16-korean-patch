#!/usr/bin/env python3
"""Build source-redacted PK B015 segment 1067 residual decisions."""

from __future__ import annotations

import copy
import hashlib
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
COMMON_PATH = WORKSTREAM / "build_pk_batch012_segment1059.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B015_S1067.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B015_S1065.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B015_S1066.private.v1.jsonl",
)

SEGMENT = 1067
QUEUE_BATCH_ID = "pk_msggame-B015"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:547:1",
    "6:554:0",
    "6:556:0",
    "6:562:0",
    "6:579:1",
    "6:589:0",
    "6:597:1",
)
TRANSLATIONS = {
    "6:547:1": "가.",
    "6:554:0": "사전 조율을 게을리해서는\n",
    "6:556:0": "…",
    "6:562:0": "언제",
    "6:579:1": "라면 말이야",
    "6:589:0": "설령",
    "6:597:1": "인가…",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
TARGET_RECORD_KEYS = tuple(
    (BLOCK_ID, int(coordinate.split(":")[1]))
    for coordinate in TARGET_COORDINATES
)
BOUNDARY_RECORD_KEYS = tuple(
    sorted(
        {
            (BLOCK_ID, record_id + delta)
            for _, record_id in TARGET_RECORD_KEYS
            for delta in (-1, 1)
        }
    )
)
BASE_DONORS = {
    (6, 547): (6, 545),
    (6, 554): (6, 552),
    (6, 556): (6, 554),
    (6, 562): (6, 560),
    (6, 579): (6, 577),
    (6, 589): (6, 587),
    (6, 597): (6, 595),
}
MASKED_DONOR_TARGETS = {(6, 547), (6, 554)}
EXACT_DONOR_TARGETS = set(TARGET_RECORD_KEYS) - MASKED_DONOR_TARGETS
PREFILL_COMPANIONS = {
    "6:556:0": "6:556:1",
    "6:562:0": "6:562:1",
    "6:579:1": "6:579:0",
    "6:589:0": "6:589:1",
    "6:597:1": "6:597:0",
}
OPTIONAL_COMPANIONS = {"6:547:1": "6:547:0"}

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7E370C4A1948D758E708E6CF9AFEEC0A35090A8AC1CC6BBB909458F3B3E0C467"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "A60A30C0688367339A8667A4D49DA895FBE25B02B4AEC6CF8813E7D8AAB544D1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F25423F56D11C91BB7647B145D06ADE66B48EB315EC67EE8169C13DB1D48AA32"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "1695FF7BA7512FF74A95E279683F8BBD242DEAF5C952CBC9685FFEAAEA9CE9DB"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "FF02086B0DC5051343F0CF701BC13EDD9998BA31B8A4B0F5E06FEACE12E6C3BA"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "31063C46D8F97AD115AA0A41F29F5C9A689CC2E8D975EA7CAF2D8FC6CDF20221"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "9647A760797E8A2F8FDE5939907E95F5051F30FA207099FE172CB1BB54E5E801"
)
EXPECTED_BOUNDARY_SHA256 = (
    "0EA4294F494DFAFC2D6A9CDC17566315D2C5C6270058D137DE0F7F14D0627723"
)
EXPECTED_DYNAMIC_CONTROL_SHA256 = (
    "CAA1EF154EB9E44FDF5BB7A865A263DB7A419CC1E6EB3C2AA8751334EEC1F355"
)
EXPECTED_BASE_DONOR_SHA256 = (
    "9B3953808573FFE0564B46D750DC7097B31F67AE112078E9C6F6B439E1260681"
)
EXPECTED_COMPANION_SHA256 = (
    "954D6A87B09AFE33F69C5DC03C368B5F5368A2AA8BD2BC7E996E3DFBD364665B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "8155D6962F55C7D8BABCCE61CAFE1D5A22E44E67EBC235F5739664B0A031CB30"
)
EXPECTED_CANDIDATE_SHA256 = (
    "A8C1885EAC48D46967C530D4B21734C080FE1556A21A3C268695C47D6E104488"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; completed Base donors, current "
    "Korean, and complete PC EN SC TC records are context only; Base "
    "exact-reuse prefill and all available predecessors are validated and "
    "excluded; adjacent records, complete runtime assemblies, Korean "
    "spacing, policy vocabulary, protected signatures, line counts, "
    "source/current bytecode gaps, outside-scope records, reverse overlay, "
    "two-run reproduction, tamper rejection and read-only inputs are "
    "guarded; dynamic fragments remain runtime pending without automatic "
    "promotion"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1067_common",
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
CONTROL_0143_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
CONTROL_02_RE = re.compile(b"\x02(.{2})", re.DOTALL)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def coordinate_key(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    if len(parts) != 3:
        raise RuntimeError(f"invalid coordinate: {value}")
    return parts  # type: ignore[return-value]


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def control_summary(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    direct = tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in CONTROL_0143_RE.finditer(gap)
    )
    inline = tuple(
        match.group(1).hex().upper()
        for gap in gaps
        for match in CONTROL_02_RE.finditer(gap)
    )
    return direct, inline


def mask_direct_operands(value: bytes) -> bytes:
    return CONTROL_0143_RE.sub(
        lambda match: match.group(0)[:2] + b"\0\0\0\0",
        value,
    )


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RuntimeError(f"required private decision is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise RuntimeError(
                    f"private decision row is not an object: {path}"
                )
            rows.append(row)
    return rows


def archive_records(blob: bytes) -> dict[tuple[int, int], Any]:
    return ENGINE.archive_records(
        ENGINE.parse_packed_msggame(blob).archive
    )


def context_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    paths = {
        "jp": ENGINE.DEFAULT_PK_PRISTINE,
        "current": prepared.resources["pk_msggame"].current_path,
        "en": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "EN"
        / "msggame.bin",
        "sc": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "SC"
        / "msggame.bin",
        "tc": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "TC"
        / "msggame.bin",
    }
    return {
        label: archive_records(path.read_bytes())
        for label, path in paths.items()
    }


def queue_visible_coordinates(prepared: Any) -> tuple[str, ...]:
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 188
        or len(visible) != 200
        or visible[0] != "6:417:0"
        or visible[-1] != "6:604:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B015 queue universe drifted"
        )
    return visible


def all_predecessor_rows(
    prepared: Any,
) -> tuple[dict[str, dict[str, Any]], tuple[str, ...]]:
    existing: dict[str, dict[str, Any]] = {}
    owners: dict[str, str] = {}
    optional_present: list[str] = []
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        if path in OPTIONAL_PREDECESSORS:
            optional_present.append(path.name)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = owners.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
            existing[coordinate] = row
    return existing, tuple(optional_present)


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[dict[str, dict[str, Any]], tuple[str, ...]]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
    )

    visible = queue_visible_coordinates(prepared)
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
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
    if len(prefilled) != 59:
        raise RuntimeError(
            f"segment {SEGMENT} prefill count drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )

    existing, optional_present = all_predecessor_rows(prepared)
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {residual}"
        )
    return existing, optional_present


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
    context_keys = tuple(
        sorted(set(TARGET_RECORD_KEYS) | set(BOUNDARY_RECORD_KEYS))
    )
    corpus = tuple(
        (
            label,
            key,
            sha256_bytes(records[key].data),
            literal_texts(records, key),
        )
        for label, records in records_by_label.items()
        for key in context_keys
    )
    gaps = tuple(
        (
            label,
            key,
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current")
        for key in TARGET_RECORD_KEYS
    )
    boundary = tuple(
        (
            label,
            key,
            sha256_bytes(records_by_label[label][key].data),
            literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current")
        for key in BOUNDARY_RECORD_KEYS
    )
    controls = tuple(
        (
            key,
            control_summary(records_by_label["jp"][key]),
            control_summary(records_by_label["current"][key]),
            gap_bytes(records_by_label["jp"][key])
            == gap_bytes(records_by_label["current"][key]),
        )
        for key in TARGET_RECORD_KEYS
    )
    guarded_digest(
        "source target",
        source_target,
        EXPECTED_SOURCE_TARGET_SHA256,
    )
    guarded_digest(
        "current target",
        current_target,
        EXPECTED_CURRENT_TARGET_SHA256,
    )
    guarded_digest(
        "multilingual context",
        corpus,
        EXPECTED_CONTEXT_CORPUS_SHA256,
    )
    guarded_digest(
        "gap contract",
        gaps,
        EXPECTED_GAP_CONTRACT_SHA256,
    )
    guarded_digest(
        "boundary",
        boundary,
        EXPECTED_BOUNDARY_SHA256,
    )
    guarded_digest(
        "dynamic control",
        controls,
        EXPECTED_DYNAMIC_CONTROL_SHA256,
    )
    mismatch_keys = tuple(
        key for key, _, _, match in controls if not match
    )
    if (
        mismatch_keys != ((6, 547),)
        or control_summary(
            records_by_label["jp"][(6, 547)]
        )[0]
        != (886, 538)
        or control_summary(
            records_by_label["current"][(6, 547)]
        )[0]
        != (886,)
        or any(
            not any(control_summary(records_by_label["jp"][key]))
            for key in TARGET_RECORD_KEYS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic control classification drifted"
        )

    base_pristine = archive_records(
        prepared.resources["base_msggame"].pristine_blob
    )
    base_current = archive_records(
        prepared.resources["base_msggame"].current_blob
    )
    donor_contract = tuple(
        (
            target_key,
            donor_key,
            sha256_bytes(base_pristine[donor_key].data),
            sha256_bytes(base_current[donor_key].data),
            literal_texts(base_pristine, donor_key),
            literal_texts(base_current, donor_key),
            (
                base_pristine[donor_key].data
                == records_by_label["jp"][target_key].data
            ),
            (
                mask_direct_operands(
                    base_pristine[donor_key].data
                )
                == mask_direct_operands(
                    records_by_label["jp"][target_key].data
                )
            ),
        )
        for target_key, donor_key in BASE_DONORS.items()
    )
    guarded_digest(
        "base donor",
        donor_contract,
        EXPECTED_BASE_DONOR_SHA256,
    )
    if any(
        literal_texts(base_pristine, BASE_DONORS[target_key])
        != literal_texts(records_by_label["jp"], target_key)
        for target_key in TARGET_RECORD_KEYS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base source literal donor drifted"
        )
    if any(
        base_pristine[BASE_DONORS[target_key]].data
        != records_by_label["jp"][target_key].data
        for target_key in EXACT_DONOR_TARGETS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} exact Base record donor drifted"
        )
    if any(
        mask_direct_operands(
            base_pristine[BASE_DONORS[target_key]].data
        )
        != mask_direct_operands(
            records_by_label["jp"][target_key].data
        )
        for target_key in MASKED_DONOR_TARGETS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} masked Base record donor drifted"
        )


def assert_semantics(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    predecessors: dict[str, dict[str, Any]],
) -> tuple[tuple[str, str, str], ...]:
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
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source-redaction policy drifted"
        )

    current = records_by_label["current"]
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
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

    if (
        TRANSLATIONS["6:547:1"] != "가."
        or TRANSLATIONS["6:554:0"]
        != "사전 조율을 게을리해서는\n"
        or TRANSLATIONS["6:556:0"] != "…"
        or TRANSLATIONS["6:562:0"] != "언제"
        or TRANSLATIONS["6:579:1"] != "라면 말이야"
        or TRANSLATIONS["6:589:0"] != "설령"
        or TRANSLATIONS["6:597:1"] != "인가…"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reviewed Korean policy drifted"
        )

    companion_contract: list[tuple[str, str, str]] = []
    for target_coordinate, companion_coordinate in (
        PREFILL_COMPANIONS.items()
    ):
        row = predecessors.get(companion_coordinate)
        if row is None:
            raise RuntimeError(
                f"segment {SEGMENT} missing prefill companion: "
                f"{companion_coordinate}"
            )
        target_key = coordinate_key(target_coordinate)
        companion_key = coordinate_key(companion_coordinate)
        target = prepared.visible_targets[
            ("pk_msggame", *target_key)
        ]
        if (
            row.get("source_record_raw_sha256")
            != target["source_record_raw_sha256"]
            or row.get("runtime_review") != "pending"
        ):
            raise RuntimeError(
                f"segment {SEGMENT} companion guard drifted: "
                f"{companion_coordinate}"
            )
        companion_contract.append(
            (
                target_coordinate,
                companion_coordinate,
                str(row["translation"]),
            )
        )

    for target_coordinate, companion_coordinate in (
        OPTIONAL_COMPANIONS.items()
    ):
        row = predecessors.get(companion_coordinate)
        companion_translation = (
            str(row["translation"])
            if row is not None
            else literal_texts(
                current,
                coordinate_key(companion_coordinate)[:2],
            )[coordinate_key(companion_coordinate)[2]]
        )
        if row is not None:
            target_key = coordinate_key(target_coordinate)
            target = prepared.visible_targets[
                ("pk_msggame", *target_key)
            ]
            if (
                row.get("source_record_raw_sha256")
                != target["source_record_raw_sha256"]
                or row.get("runtime_review") != "pending"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} optional companion drifted"
                )
        companion_contract.append(
            (
                target_coordinate,
                companion_coordinate,
                companion_translation,
            )
        )

    companion_tuple = tuple(companion_contract)
    guarded_digest(
        "companion",
        companion_tuple,
        EXPECTED_COMPANION_SHA256,
    )
    return companion_tuple


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    resource = prepared.resources["pk_msggame"]
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
        resource.current_blob,
        replacements,
    )
    candidate_records = archive_records(candidate)
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )

    target_record_keys = {key[:2] for key in replacements}
    for key, current_record in current.items():
        candidate_record = candidate_records[key]
        if key not in target_record_keys:
            if candidate_record.data != current_record.data:
                raise RuntimeError(
                    f"segment {SEGMENT} changed outside scope: {key}"
                )
            continue
        if gap_bytes(candidate_record) != gap_bytes(current_record):
            raise RuntimeError(
                f"segment {SEGMENT} changed target gaps: {key}"
            )
        current_literals = literal_texts(current, key)
        candidate_literals = literal_texts(candidate_records, key)
        for literal_id, current_text in enumerate(current_literals):
            replacement_key = (key[0], key[1], literal_id)
            expected = replacements.get(replacement_key, current_text)
            if candidate_literals[literal_id] != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} candidate literal drifted: "
                    f"{replacement_key}"
                )

    if (
        ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay drifted"
        )
    changed = sum(
        translation != reverse[key]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if EXPECTED_CHANGED_LITERAL_COUNT == -1:
        DISCOVERED_PINS["changed literal count"] = changed
    elif changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    if EXPECTED_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["candidate"] = candidate_sha256
    elif candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} candidate drifted: "
            f"{candidate_sha256}"
        )
    return candidate, candidate_sha256, changed


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    key: tuple[int, int],
    companion_coordinates: tuple[str, ...],
) -> dict[str, Any]:
    source_record = records_by_label["jp"][key]
    current_record = records_by_label["current"][key]
    source_gaps = gap_bytes(source_record)
    current_gaps = gap_bytes(current_record)
    source_direct, source_inline = control_summary(source_record)
    current_direct, current_inline = control_summary(current_record)
    coordinate_label = f"{key[0]}:{key[1]}"
    evidence: dict[str, Any] = {
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in source_gaps)
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in current_gaps)
        ),
        "source_direct_call_operands": source_direct,
        "current_direct_call_operands": current_direct,
        "source_inline_runtime_tokens": source_inline,
        "current_inline_runtime_tokens": current_inline,
        "source_current_gap_match": source_gaps == current_gaps,
        "companion_coordinates": companion_coordinates,
        "complete_record_assembly_reviewed": True,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }
    if coordinate_label == "6:547":
        evidence[
            "source_only_conjugation_call_operands"
        ] = (538,)
        evidence[
            "current_gap_difference_requires_runtime_audit"
        ] = True
    if coordinate_label == "6:589":
        evidence[
            "parenthetical_particle_in_prefill_companion"
        ] = True
        evidence[
            "particle_cannot_be_safely_moved_into_owned_prefix"
        ] = True
        evidence[
            "followup_runtime_companion_audit_required"
        ] = True
        evidence[
            "outer_whitespace_guard_prevents_prefix_space"
        ] = True
    if coordinate_label == "6:562":
        evidence[
            "spacing_requires_runtime_companion_audit"
        ] = True
        evidence[
            "outer_whitespace_guard_prevents_prefix_space"
        ] = True
    return evidence


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    predecessors, optional_present = (
        assert_queue_and_residual_contract(prepared)
    )
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    companion_contract = assert_semantics(
        prepared,
        records_by_label,
        predecessors,
    )
    companion_by_target = {
        target: companion
        for target, companion, _ in companion_contract
    }
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )

    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        companion = companion_by_target.get(coordinate)
        row: dict[str, Any] = {
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
            "base_donor_reviewed": True,
            "all_available_predecessors_validated": True,
            "optional_s1065_s1066_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "same_record_companion_review":
            companion is not None,
            "historical_term_review": True,
            "public_resource_term_review": True,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "runtime_assembly_evidence":
            runtime_control_evidence(
                records_by_label,
                (block_id, record_id),
                (companion,) if companion is not None else (),
            ),
        }
        rows.append(row)
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
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1067-tamper-",
        dir=DECISIONS_ROOT,
    ) as directory:
        path = Path(directory) / "tampered.private.v1.jsonl"
        ENGINE.atomic_write(path, ENGINE.jsonl(tampered_rows))
        try:
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
        except ENGINE.RetranslationError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} source guard accepted tampering"
            )

    tampered_policy = dict(TRANSLATIONS)
    tampered_policy[TARGET_COORDINATES[0]] += "X"
    if (
        canonical_sha256(tuple(tampered_policy.items()))
        == EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} policy guard accepted tampering"
        )
    tampered_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        {
            coordinate_key(coordinate): translation
            for coordinate, translation in tampered_policy.items()
        },
    )
    if tampered_candidate == candidate:
        raise RuntimeError(
            f"segment {SEGMENT} candidate guard accepted tampering"
        )


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
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
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

    steam_path = prepared.resources["pk_msggame"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
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
        len(rows) != 7
        or len(validated) != 7
        or counts != Counter({"runtime_fragment_pending": 7})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
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
    if ENGINE.KANA_OR_HAN_RE.search(
        OUTPUT.read_text(encoding="utf-8")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private output leaked source text"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B015_S1067",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "target_record_count": len(TARGET_RECORD_KEYS),
                "block_ids": [BLOCK_ID],
                "exact_reuse_prefill_count": 59,
                "residual_count": 7,
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_s1065_s1066_validated_if_present": True,
                "base_donors_reviewed": True,
                "same_record_companions_reviewed": sorted(
                    set(PREFILL_COMPANIONS.values())
                    | set(OPTIONAL_COMPANIONS.values())
                ),
                "source_current_gap_mismatch_records": [
                    "6:547",
                ],
                "parenthetical_particle_followup_records": [
                    "6:589",
                ],
                "runtime_spacing_followup_records": [
                    "6:562",
                    "6:589",
                ],
                "outside_scope_records_exact": True,
                "current_runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_terms_reviewed": True,
                "public_resource_terms_reviewed": [
                    "policy_coordination",
                    "castle_attack",
                ],
                "historic_korean_used": False,
                "switch_korean_used": False,
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
