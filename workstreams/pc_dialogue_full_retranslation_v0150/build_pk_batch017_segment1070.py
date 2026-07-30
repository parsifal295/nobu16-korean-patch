#!/usr/bin/env python3
"""Build source-redacted PK B017 segment 1070 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B017_S1070.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)

SEGMENT = 1070
QUEUE_BATCH_ID = "pk_msggame-B017"
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:819:0",
    "6:822:0",
    "6:826:0",
    "6:826:1",
    "6:830:0",
    "6:834:0",
    "6:835:0",
    "6:839:0",
    "6:844:0",
)
TRANSLATIONS = {
    "6:819:0": "흥,",
    "6:822:0": "…",
    "6:826:0": "우리 가문에 ",
    "6:826:1": " 따위는\n필요 없다고 생각하오만…",
    "6:830:0": "이",
    "6:834:0": "하아…",
    "6:835:0": "…",
    "6:839:0": "하아…\n",
    "6:844:0": "설마",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
TARGET_RECORD_KEYS = tuple(
    sorted(
        {
            (BLOCK_ID, int(coordinate.split(":")[1]))
            for coordinate in TARGET_COORDINATES
        }
    )
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
    (6, 819): (6, 817),
    (6, 822): (6, 820),
    (6, 826): (6, 824),
    (6, 830): (6, 828),
    (6, 834): (6, 832),
    (6, 835): (6, 833),
    (6, 839): (6, 837),
    (6, 844): (6, 842),
}
PREFILL_COMPANIONS = {
    "6:819:0": "6:819:1",
    "6:822:0": "6:822:1",
    "6:830:0": "6:830:1",
    "6:834:0": "6:834:1",
    "6:835:0": "6:835:1",
    "6:839:0": "6:839:1",
    "6:844:0": "6:844:1",
}

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
    "122A750F11C637314F8E873145433AA46A43DE4D95B374FA58E0FC82990547D2"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "8B7F3368DE710470ED23DDB87288DE5C31539DF2A7B81CA2A56BE9CF76903B8B"
)
EXPECTED_FIRST_SLICE_SHA256 = (
    "3BE49B231B883E7B38066ACD91F4D8F654F1E15819214904E3CC6B0E436B222F"
)
EXPECTED_FIRST_PREFILLED_SHA256 = (
    "C6DF52D21671D286ADA04573B5CA60B4CE6BFEA99037212FCFC720204B1B51DC"
)
EXPECTED_SECOND_SLICE_SHA256 = (
    "44B5B59ADBF1FCBD710600813AAE5666004907B291D80EA9BA85D703C9ED5D08"
)
EXPECTED_THIRD_SLICE_SHA256 = (
    "36B8C4369F7FE6D43BF7AC029CD65F4865547A00166297360B2962D71D8E9C92"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3A140BFE27A786C84DABAF18447EC5806F043A977F7736D483DAA9F088D1BEF2"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "20A126AE0F14CEDBC6E1349DC6DF62ECDB882BF42548894A2FCF1F21CD632DC9"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "EC3114305566B74CCF9C67E792C2DF21575F232DB76EF73A5DB18FE5D02420A9"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "06D8615FC168EFC4EDB8C26C9B2F917EFDA1B67BFA8E18A9FA1B73C1549DEDBC"
)
EXPECTED_BOUNDARY_SHA256 = (
    "BE5F3E5A70DC68CF82C8AC92E88DC077DB982EA496244EA6218972243CCB1F33"
)
EXPECTED_DYNAMIC_CONTROL_SHA256 = (
    "24546E291B819EA0070419C4CF2FBBDFB8A829EE24C63831E0A4B40E482699AA"
)
EXPECTED_BASE_DONOR_SHA256 = (
    "4EB80C5689F00C76D46BAF681197F6AF64592110930175B1B179A1A300612A37"
)
EXPECTED_COMPANION_SHA256 = (
    "89957127F872F55881922085182DC6994C3186517C3BBE6022471F4C905DD6B1"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "6955A8E748BD1941FF9B36C90F2CBBE5879B4532A0D3073E0C8D816E4716AC64"
)
EXPECTED_CANDIDATE_SHA256 = (
    "23808B86EA562A7DA9D7C2DF2ECEA8B52FD8F7FF8D8EFFAD7BB7F4E613111991"
)
EXPECTED_CHANGED_LITERAL_COUNT = 1

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; completed Base exact-record "
    "donors, current Korean, and complete PC EN SC TC records are context "
    "only; the Base prefill and every available predecessor are validated "
    "and excluded; all 200 B017 visible coordinates are closed by 191 "
    "exact-prefill rows and nine reviewed residual rows; complete runtime "
    "assemblies, adjacent records, policy register, historical terminology, "
    "protected signatures, line counts, bytecode gaps, outside-scope "
    "records, reverse overlay, two-run reproduction, tamper rejection and "
    "read-only inputs are guarded; Base runtime state is not inherited and "
    "all dynamic fragments remain pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1070_common",
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
        len(queue_rows) != 192
        or len(visible) != 200
        or visible[0] != "6:793:0"
        or visible[-1] != "6:984:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B017 queue universe drifted"
        )
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    return visible


def all_predecessor_rows(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    owners: dict[str, str] = {}
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
            previous = owners.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
            existing[coordinate] = row
    return existing


def assert_queue_and_residual_contract(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
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
    first = visible[0:67]
    second = visible[67:134]
    third = visible[134:200]
    guarded_digest(
        "first queue slice",
        first,
        EXPECTED_FIRST_SLICE_SHA256,
    )
    guarded_digest(
        "second queue slice",
        second,
        EXPECTED_SECOND_SLICE_SHA256,
    )
    guarded_digest(
        "third queue slice",
        third,
        EXPECTED_THIRD_SLICE_SHA256,
    )

    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    first_prefilled = tuple(
        coordinate
        for coordinate in first
        if coordinate in prefill_coordinates
    )
    second_prefilled = tuple(
        coordinate
        for coordinate in second
        if coordinate in prefill_coordinates
    )
    third_prefilled = tuple(
        coordinate
        for coordinate in third
        if coordinate in prefill_coordinates
    )
    if (
        len(first_prefilled) != 58
        or len(second_prefilled) != 67
        or second_prefilled != second
        or len(third_prefilled) != 66
        or third_prefilled != third
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B017 prefill coverage drifted"
        )
    guarded_digest(
        "first prefilled coordinate",
        first_prefilled,
        EXPECTED_FIRST_PREFILLED_SHA256,
    )

    existing = all_predecessor_rows(prepared)
    residual = tuple(
        coordinate
        for coordinate in visible
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {residual}"
        )
    if (
        len(prefill_coordinates.intersection(visible)) != 191
        or len(residual) != 9
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B017 closure count drifted"
        )
    return existing


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
    if (
        any(not match for _, _, _, match in controls)
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
            control_summary(base_pristine[donor_key]),
        )
        for target_key, donor_key in BASE_DONORS.items()
    )
    guarded_digest(
        "base donor",
        donor_contract,
        EXPECTED_BASE_DONOR_SHA256,
    )
    if any(
        base_pristine[donor_key].data
        != records_by_label["jp"][target_key].data
        for target_key, donor_key in BASE_DONORS.items()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} exact Base record donor drifted"
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
        TRANSLATIONS["6:819:0"] != "흥,"
        or TRANSLATIONS["6:822:0"] != "…"
        or TRANSLATIONS["6:826:0"] != "우리 가문에 "
        or TRANSLATIONS["6:826:1"]
        != " 따위는\n필요 없다고 생각하오만…"
        or TRANSLATIONS["6:830:0"] != "이"
        or TRANSLATIONS["6:834:0"] != "하아…"
        or TRANSLATIONS["6:835:0"] != "…"
        or TRANSLATIONS["6:839:0"] != "하아…\n"
        or TRANSLATIONS["6:844:0"] != "설마"
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
        "base_runtime_state_inherited": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }
    if key == (6, 826):
        evidence["dynamic_name_outer_spacing_preserved"] = True
        evidence["base_donor_spacing_not_copied"] = True
    if key == (6, 830):
        evidence[
            "two_name_particle_spacing_requires_runtime_audit"
        ] = True
    if key == (6, 844):
        evidence[
            "name_particle_spacing_requires_runtime_audit"
        ] = True
    return evidence


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    predecessors = assert_queue_and_residual_contract(prepared)
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
            "base_exact_record_donor_reviewed": True,
            "base_runtime_state_inherited": False,
            "all_available_predecessors_validated": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "same_record_prefill_companion_review":
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
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1070-tamper-",
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
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
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
        len(rows) != 9
        or len(validated) != 9
        or counts != Counter({"runtime_fragment_pending": 9})
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
            or row["runtime_assembly_evidence"][
                "base_runtime_state_inherited"
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
                "segment": "pk_msggame_B017_S1070",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [0, 199],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "target_record_count": len(TARGET_RECORD_KEYS),
                "block_ids": [BLOCK_ID],
                "exact_reuse_prefill_count": 191,
                "first_slice_prefill_count": 58,
                "second_slice_prefill_count": 67,
                "third_slice_prefill_count": 66,
                "residual_count": 9,
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
                "base_exact_record_donors_reviewed": True,
                "base_runtime_state_inherited": False,
                "same_record_prefill_companions_reviewed": sorted(
                    PREFILL_COMPANIONS.values()
                ),
                "particle_spacing_followup_records": [
                    "6:830",
                    "6:844",
                ],
                "outside_scope_records_exact": True,
                "source_current_runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_terms_reviewed": [
                    "slander",
                    "clan_register",
                ],
                "public_resource_terms_reviewed": [
                    "council",
                    "cooperation",
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
