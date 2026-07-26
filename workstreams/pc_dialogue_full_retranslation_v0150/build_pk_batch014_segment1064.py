#!/usr/bin/env python3
"""Build source-redacted PK B014 segment 1064 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B014_S1064.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
OPTIONAL_PREDECESSOR = (
    DECISIONS_ROOT / "pk_msggame_B014_S1063.private.v1.jsonl"
)

SEGMENT = 1064
QUEUE_BATCH_ID = "pk_msggame-B014"
QUEUE_START = 134
QUEUE_STOP = 200
MIDDLE_START = 67
MIDDLE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("6:374:1",)
TARGET_RECORD_KEY = (6, 374)
BOUNDARY_RECORD_KEYS = ((6, 373), (6, 375))
BASE_DONOR_KEY = (6, 372)
TRANSLATIONS = {"6:374:1": "의 일…"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)

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
    "BAE97C559F23A9B6FC39351665BA9516CE7E4E2E79B27C3E33547F5D7DC37F0A"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "191330925F504EDE907B669FE86BA5F7C9AD05108C3ABEDE4AA0575B917FB730"
)
EXPECTED_MIDDLE_SLICE_SHA256 = (
    "9673E8F486AD0CAC3C882DB7226E5256EE32B116516AD7EA5018FE39DD478E89"
)
EXPECTED_MIDDLE_PREFILLED_SHA256 = (
    "9673E8F486AD0CAC3C882DB7226E5256EE32B116516AD7EA5018FE39DD478E89"
)
EXPECTED_LAST_PREFILLED_SHA256 = (
    "209ABA4C155DA26B55D95A6FE92CA5DAFBB40CF89279EA5410FC1335F9A6E1AF"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "6CF8DB1AE91A34D70FAE1836B3EDE923A4DAC4F5AF2DD19AF6004EF1A875EC99"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "FE620F06F1AA3AE2A24215D761CCABC5AC8A8F88A055F42ABEAD2B87F0B84578"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "06BA485DD37FBD75F7A57B412BD50BEEB0B9245E3864CAC8A485FB69F03B3DC8"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "7A7EA9DE0EA448335DF925334392B921F0AC62A07E864217365602BFD9745296"
)
EXPECTED_BOUNDARY_SHA256 = (
    "954AA689FE398D6AD92480B7A9A9B2CC1DB31B82B67A38A67EAE9F9438941935"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "FE1A45461C5AF1DA827DADCA7BD3FEE722AE1D0A3073586A634601E5FA452F7A"
)
EXPECTED_BASE_DONOR_SHA256 = (
    "7A851F4FB4ACF7E8DC0CEF275C39CBEA146D91603BA9C7BF5F1FF3C7B37A0C69"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "FE620F06F1AA3AE2A24215D761CCABC5AC8A8F88A055F42ABEAD2B87F0B84578"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_CHANGED_LITERAL_COUNT = 0

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; completed Base exact full-record "
    "donor, current Korean, and complete PC EN SC TC records are context "
    "only; the same-record prefill companion and adjacent records were "
    "reviewed; B014 middle slice is fully covered by exact reuse; all "
    "available predecessors, protected signatures, line counts, bytecode "
    "gaps, outside-scope records, reverse overlay, two-run reproduction, "
    "tamper rejection and read-only inputs are guarded; this dynamic name "
    "fragment remains runtime pending without automatic promotion"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1064_common",
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
        len(queue_rows) != 202
        or len(visible) != 200
        or visible[0] != "4:94:0"
        or visible[-1] != "6:416:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B014 queue universe drifted"
        )
    return visible


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
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
    middle_slice = visible[MIDDLE_START:MIDDLE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    guarded_digest(
        "middle queue slice",
        middle_slice,
        EXPECTED_MIDDLE_SLICE_SHA256,
    )

    prefill_rows = read_jsonl(PREFILL)
    prefill_coordinates = {
        str(row["coordinate"]) for row in prefill_rows
    }
    middle_prefilled = tuple(
        coordinate
        for coordinate in middle_slice
        if coordinate in prefill_coordinates
    )
    if (
        len(middle_slice) != 67
        or len(middle_prefilled) != 67
        or middle_prefilled != middle_slice
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B014 middle slice is not 67/67 prefill"
        )
    guarded_digest(
        "middle prefilled coordinate",
        middle_prefilled,
        EXPECTED_MIDDLE_PREFILLED_SHA256,
    )

    last_prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(last_prefilled) != 65:
        raise RuntimeError(
            f"segment {SEGMENT} final slice prefill count drifted"
        )
    guarded_digest(
        "last prefilled coordinate",
        last_prefilled,
        EXPECTED_LAST_PREFILLED_SHA256,
    )

    existing: dict[str, str] = {}
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
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )

    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {residual}"
        )

    optional_present: list[str] = []
    if OPTIONAL_PREDECESSOR.is_file():
        ENGINE.validate_decisions(
            prepared,
            OPTIONAL_PREDECESSOR,
            require_complete=False,
        )
        optional_present.append(OPTIONAL_PREDECESSOR.name)
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
    corpus_keys = (
        BOUNDARY_RECORD_KEYS[0],
        TARGET_RECORD_KEY,
        BOUNDARY_RECORD_KEYS[1],
    )
    corpus = tuple(
        (
            label,
            key,
            sha256_bytes(records[key].data),
            literal_texts(records, key),
        )
        for label, records in records_by_label.items()
        for key in corpus_keys
    )
    gaps = tuple(
        (
            label,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][TARGET_RECORD_KEY]
                )
            ),
        )
        for label in ("jp", "current")
    )
    boundary = tuple(
        (
            label,
            key,
            sha256_bytes(records_by_label[label][key].data),
            literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][key]
                )
            ),
        )
        for label in ("jp", "current")
        for key in BOUNDARY_RECORD_KEYS
    )
    source_gaps = gap_bytes(
        records_by_label["jp"][TARGET_RECORD_KEY]
    )
    direct_calls = tuple(
        int.from_bytes(match.group(1), "little")
        for gap in source_gaps
        for match in CONTROL_0143_RE.finditer(gap)
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
        "dynamic record",
        (TARGET_RECORD_KEY, direct_calls),
        EXPECTED_DYNAMIC_RECORD_SHA256,
    )
    if direct_calls != (1,):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic call operand drifted"
        )

    base_pristine = archive_records(
        prepared.resources["base_msggame"].pristine_blob
    )
    base_current = archive_records(
        prepared.resources["base_msggame"].current_blob
    )
    donor = (
        sha256_bytes(base_pristine[BASE_DONOR_KEY].data),
        sha256_bytes(base_current[BASE_DONOR_KEY].data),
        literal_texts(base_pristine, BASE_DONOR_KEY),
        literal_texts(base_current, BASE_DONOR_KEY),
        tuple(
            value.hex().upper()
            for value in gap_bytes(base_pristine[BASE_DONOR_KEY])
        ),
    )
    guarded_digest(
        "base donor",
        donor,
        EXPECTED_BASE_DONOR_SHA256,
    )
    if (
        base_pristine[BASE_DONOR_KEY].data
        != records_by_label["jp"][TARGET_RECORD_KEY].data
        or literal_texts(base_current, BASE_DONOR_KEY)
        != literal_texts(
            records_by_label["current"],
            TARGET_RECORD_KEY,
        )
        or gap_bytes(base_current[BASE_DONOR_KEY])
        != gap_bytes(
            records_by_label["current"][TARGET_RECORD_KEY]
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} exact Base full-record donor drifted"
        )


def assert_semantics(
    prepared: Any,
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

    current_literals = literal_texts(
        records_by_label["current"],
        TARGET_RECORD_KEY,
    )
    if (
        len(current_literals) != 2
        or current_literals[1] != TRANSLATIONS["6:374:1"]
        or current_literals[0] != "백성의 이해를 얻는 것이\n"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reviewed Korean assembly drifted"
        )
    current_text = current_literals[1]
    translation = TRANSLATIONS["6:374:1"]
    ENGINE.validate_translation_shape(
        current_text,
        translation,
        "runtime_pending",
        "6:374:1",
    )
    if (
        translation.count("\n") != current_text.count("\n")
        or ENGINE.protected_signature(translation)
        != ENGINE.protected_signature(current_text)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target shape drifted"
        )

    prefill_row = next(
        (
            row
            for row in read_jsonl(PREFILL)
            if row.get("coordinate") == "6:374:0"
        ),
        None,
    )
    source_target = prepared.visible_targets[
        ("pk_msggame", 6, 374, 1)
    ]
    if (
        prefill_row is None
        or prefill_row.get("translation") != current_literals[0]
        or prefill_row.get("runtime_review") != "pending"
        or prefill_row.get("source_record_raw_sha256")
        != source_target["source_record_raw_sha256"]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} same-record prefill companion drifted"
        )


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
        current_record_literals = literal_texts(current, key)
        candidate_literals = literal_texts(candidate_records, key)
        for literal_id, current_text in enumerate(
            current_record_literals
        ):
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
) -> dict[str, Any]:
    gaps = gap_bytes(
        records_by_label["current"][TARGET_RECORD_KEY]
    )
    direct_calls = tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in CONTROL_0143_RE.finditer(gap)
    )
    if direct_calls != (1,):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted"
        )
    return {
        "record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gaps)
        ),
        "direct_call_operands": direct_calls,
        "inline_runtime_tokens": (),
        "literal_order": (
            "prefill_companion",
            "direct_call_1",
            "reviewed_suffix",
        ),
        "prefill_companion_coordinate": "6:374:0",
        "prefill_companion_reviewed": True,
        "complete_record_assembly_reviewed": True,
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
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_semantics(prepared, records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )

    coordinate = TARGET_COORDINATES[0]
    target = prepared.visible_targets[
        ("pk_msggame", 6, 374, 1)
    ]
    current_text = literal_texts(
        records_by_label["current"],
        TARGET_RECORD_KEY,
    )[1]
    rows = [
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
            "base_exact_full_record_donor_reviewed": True,
            "all_available_predecessors_validated": True,
            "optional_s1063_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "same_record_prefill_companion_review": True,
            "historical_term_review": True,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "runtime_assembly_evidence":
            runtime_control_evidence(records_by_label),
        }
    ]
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
        prefix="pk-s1064-tamper-",
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
        len(rows) != 1
        or len(validated) != 1
        or counts != Counter({"runtime_fragment_pending": 1})
        or rows[0]["semantic_review"] != "approved"
        or rows[0]["runtime_review"] != "pending"
        or rows[0]["layout_review"] != "runtime_pending"
        or rows[0]["historic_korean_used"] is not False
        or rows[0]["switch_korean_used"] is not False
        or rows[0]["line_count_preserved"] is not True
        or rows[0]["runtime_assembly_evidence"][
            "runtime_promotion_authorized"
        ]
        is not False
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
                "segment": "pk_msggame_B014_S1064",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "target_record_count": 1,
                "block_ids": [BLOCK_ID],
                "middle_slice_exact_reuse_prefill_count": 67,
                "middle_slice_residual_count": 0,
                "final_slice_exact_reuse_prefill_count": 65,
                "final_slice_residual_count": 1,
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
                "optional_s1063_validated_if_present": True,
                "base_exact_full_record_donor_reviewed": True,
                "same_record_prefill_companions_reviewed": [
                    "6:374:0",
                ],
                "adjacent_records_reviewed": [
                    "6:373",
                    "6:375",
                ],
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
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
