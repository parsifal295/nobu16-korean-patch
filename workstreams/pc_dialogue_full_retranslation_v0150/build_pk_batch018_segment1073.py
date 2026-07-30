#!/usr/bin/env python3
"""Build source-redacted PK B018 segment 1073 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B018_S1073.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)

SEGMENT = 1073
QUEUE_BATCH_ID = "pk_msggame-B018"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:1126:0",
    "6:1131:1",
    "6:1136:1",
    "6:1139:1",
    "6:1153:1",
    "6:1154:1",
    "6:1156:1",
    "6:1157:1",
    "6:1160:1",
    "6:1161:0",
    "6:1161:2",
    "6:1162:0",
    "6:1162:1",
    "6:1162:3",
)
TRANSLATIONS = {
    "6:1126:0": "돌아가도 되는가?",
    "6:1131:1": "도…!",
    "6:1136:1": "까닭에",
    "6:1139:1": "인가",
    "6:1153:1": "을 받아 주십시오",
    "6:1154:1": "를 받아 주십시오",
    "6:1156:1": "을(를) 받아 주십시오",
    "6:1157:1": ", 총",
    "6:1160:1": "을 받아 주십시오",
    "6:1161:0": "매입 대상:",
    "6:1161:2": "을 받아 주십시오",
    "6:1162:0": "매입 내역:",
    "6:1162:1": ", 총",
    "6:1162:3": "을 받아 주십시오",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - {"6:1126:0"}
STATIC_COORDINATES = {"6:1126:0"}
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
    (6, 1131): (6, 1129),
    (6, 1136): (6, 1134),
    (6, 1139): (6, 1137),
    (6, 1153): (6, 1151),
    (6, 1154): (6, 1152),
    (6, 1156): (6, 1154),
    (6, 1157): (6, 1155),
    (6, 1160): (6, 1158),
    (6, 1161): (6, 1159),
    (6, 1162): (6, 1160),
}
MASKED_DONOR_TARGETS = {(6, 1136), (6, 1139)}
EXACT_DONOR_TARGETS = set(BASE_DONORS) - MASKED_DONOR_TARGETS
PREFILL_COMPANIONS = {
    "6:1131:1": ("6:1131:0",),
    "6:1136:1": ("6:1136:0",),
    "6:1139:1": ("6:1139:0",),
    "6:1153:1": ("6:1153:0",),
    "6:1154:1": ("6:1154:0",),
    "6:1156:1": ("6:1156:0",),
    "6:1157:1": ("6:1157:0", "6:1157:2"),
    "6:1160:1": ("6:1160:0",),
    "6:1161:0": ("6:1161:1",),
    "6:1161:2": ("6:1161:1",),
    "6:1162:0": ("6:1162:2",),
    "6:1162:1": ("6:1162:2",),
    "6:1162:3": ("6:1162:2",),
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
    "AD3D566DED80C1A61A510C8759B2AAA161046C182D0A5BF58CCE2EDE7B441BB5"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "43BE1C3513D3423145692AFDD510F7F0A56DDF3C433950B20A20D30ACC0A9820"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "9FD63D1CA06686A55DA76E74834431414B471FE3EE6DE2396A35A246DCF7F06F"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "736D1E40DCDEEEF179974D885DE44A51047AEE14D1A5AFED0771C1870A4B8121"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "03D14D71180D296D38C0AB266C912EC302D12E238DC22842D4581376F3EB8FF3"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "CED00AF23FF3063507BC3BB83379933A96B3B003D5D8D49ED72DF705C171BFE1"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "A471FC080B256C0AFC1A0036243B04E745B31A5EA649A657DD3BE19669510E40"
)
EXPECTED_BOUNDARY_SHA256 = (
    "B81751F66E1AA59A2BA5AE3E51D83628B6C77B4B8DA3CAA231BE8B76B0730260"
)
EXPECTED_DYNAMIC_CONTROL_SHA256 = (
    "FD323AD0E124F5802E379F26004FD8D850EE02A0C5A7CE379BA9E98C3BC7CFED"
)
EXPECTED_BASE_DONOR_SHA256 = (
    "60FFB1132F687EA70866FB61B0060D4A72F4E922FFF260E809CC08EDD041943E"
)
EXPECTED_COMPANION_SHA256 = (
    "9981225D7C8D6C70513C7CB227DE83DEAF2C78086F390AB603AFA375247F9DB0"
)
EXPECTED_ASSEMBLY_SHA256 = (
    "19E02989C7406C1EB286C865479B0BE1198E10EFF105A271DACFA937FDAAFD15"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "87E8CDF7B10ED07543C1F8363051AA2FDF1C64571733C95B9969726E260A1771"
)
EXPECTED_CANDIDATE_SHA256 = (
    "D55A6506E44D9FB52C9C938912DE785FC73E2E434A81D3D2D58EE6AF17B4BDD9"
)
EXPECTED_CHANGED_LITERAL_COUNT = 9

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; completed Base donors, current "
    "Korean, and complete PC EN SC TC records are context only; exact "
    "prefill and every available predecessor are validated and excluded; "
    "complete multi-literal runtime assemblies, dynamic item/count/money "
    "ordering, adjacent records, merchant register, historical resource "
    "terms, outer whitespace constraints, particles, protected signatures, "
    "line counts, bytecode gaps, outside-scope records, reverse overlay, "
    "two-run reproduction, tamper rejection and read-only inputs are "
    "guarded; Base runtime state is not inherited and dynamic rows remain "
    "pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1073_common",
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


def control_summary(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    direct = tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in CONTROL_0143_RE.finditer(gap)
    )
    inline_values: list[str] = []
    for gap in gaps:
        without_direct = CONTROL_0143_RE.sub(b"", gap)
        if (
            without_direct.startswith(b"\x02")
            and len(without_direct) in (2, 3)
        ):
            inline_values.append(
                without_direct[1:].hex().upper()
            )
    inline = tuple(inline_values)
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
        len(queue_rows) != 182
        or len(visible) != 200
        or visible[0] != "6:985:0"
        or visible[-1] != "6:1166:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B018 queue universe drifted"
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
    if len(prefilled) != 52:
        raise RuntimeError(
            f"segment {SEGMENT} prefill count drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )

    existing = all_predecessor_rows(prepared)
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {residual}"
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
        if key != (6, 1126)
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
        control_summary(records_by_label["jp"][(6, 1126)])
        != ((), ())
        or any(not match for _, _, _, match in controls)
        or any(
            not any(control_summary(records_by_label["jp"][key]))
            for key in TARGET_RECORD_KEYS
            if key != (6, 1126)
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
                mask_direct_operands(base_pristine[donor_key].data)
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
        base_pristine[BASE_DONORS[key]].data
        != records_by_label["jp"][key].data
        for key in EXACT_DONOR_TARGETS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} exact Base donor drifted"
        )
    if any(
        mask_direct_operands(
            base_pristine[BASE_DONORS[key]].data
        )
        != mask_direct_operands(
            records_by_label["jp"][key].data
        )
        for key in MASKED_DONOR_TARGETS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} masked Base donor drifted"
        )


def reviewed_assemblies(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    predecessors: dict[str, dict[str, Any]],
) -> tuple[tuple[int, tuple[str, ...], tuple[str, ...]], ...]:
    assemblies: list[
        tuple[int, tuple[str, ...], tuple[str, ...]]
    ] = []
    for key in TARGET_RECORD_KEYS:
        current_literals = literal_texts(
            records_by_label["current"],
            key,
        )
        final_literals: list[str] = []
        sources: list[str] = []
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in TRANSLATIONS:
                final_literals.append(TRANSLATIONS[coordinate])
                sources.append("segment")
            elif coordinate in predecessors:
                final_literals.append(
                    str(predecessors[coordinate]["translation"])
                )
                sources.append("prefill_or_predecessor")
            else:
                final_literals.append(current_text)
                sources.append("current_context")
        assemblies.append(
            (key[1], tuple(final_literals), tuple(sources))
        )
    result = tuple(assemblies)
    guarded_digest(
        "assembly",
        result,
        EXPECTED_ASSEMBLY_SHA256,
    )
    return result


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
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
        or len(DYNAMIC_COORDINATES) != 13
        or len(STATIC_COORDINATES) != 1
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
        dynamic = coordinate in DYNAMIC_COORDINATES
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending" if dynamic else "unchanged_from_current",
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
        TRANSLATIONS["6:1126:0"] != "돌아가도 되는가?"
        or TRANSLATIONS["6:1131:1"] != "도…!"
        or TRANSLATIONS["6:1136:1"] != "까닭에"
        or TRANSLATIONS["6:1139:1"] != "인가"
        or TRANSLATIONS["6:1153:1"] != "을 받아 주십시오"
        or TRANSLATIONS["6:1154:1"] != "를 받아 주십시오"
        or TRANSLATIONS["6:1156:1"]
        != "을(를) 받아 주십시오"
        or TRANSLATIONS["6:1157:1"] != ", 총"
        or TRANSLATIONS["6:1160:1"] != "을 받아 주십시오"
        or TRANSLATIONS["6:1161:0"] != "매입 대상:"
        or TRANSLATIONS["6:1161:2"] != "을 받아 주십시오"
        or TRANSLATIONS["6:1162:0"] != "매입 내역:"
        or TRANSLATIONS["6:1162:1"] != ", 총"
        or TRANSLATIONS["6:1162:3"] != "을 받아 주십시오"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reviewed Korean policy drifted"
        )

    companion_contract: list[tuple[str, str, str]] = []
    for target_coordinate, companions in PREFILL_COMPANIONS.items():
        target_key = coordinate_key(target_coordinate)
        target = prepared.visible_targets[
            ("pk_msggame", *target_key)
        ]
        for companion_coordinate in companions:
            row = predecessors.get(companion_coordinate)
            if row is None:
                raise RuntimeError(
                    f"segment {SEGMENT} missing companion: "
                    f"{companion_coordinate}"
                )
            if (
                row.get("source_record_raw_sha256")
                != target["source_record_raw_sha256"]
                or row.get("runtime_review") != "pending"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} companion drifted: "
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
    assemblies = reviewed_assemblies(
        records_by_label,
        predecessors,
    )
    assembly_map = {
        record_id: literals
        for record_id, literals, _ in assemblies
    }
    if (
        not assembly_map[1153][0].endswith("병량")
        or assembly_map[1153][1] != "을 받아 주십시오"
        or assembly_map[1157][1] != ", 총"
        or assembly_map[1157][2] != "점을 받아 주십시오"
        or assembly_map[1161][0] != "매입 대상:"
        or assembly_map[1161][1]
        != "을(를) 매입했습니다\n금"
        or assembly_map[1161][2] != "을 받아 주십시오"
        or assembly_map[1162][0] != "매입 내역:"
        or assembly_map[1162][1] != ", 총"
        or assembly_map[1162][2]
        != "점을 매입했습니다\n금"
        or assembly_map[1162][3] != "을 받아 주십시오"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} final merchant assembly drifted"
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
    if key in {(6, 1136), (6, 1139)}:
        evidence[
            "base_operand_diff_requires_pk_runtime_review"
        ] = True
    if key in {(6, 1153), (6, 1154), (6, 1160)}:
        evidence[
            "resource_amount_particle_requires_runtime_review"
        ] = True
    if key == (6, 1157):
        evidence["runtime_order"] = (
            "representative_item",
            "comma_total_label",
            "count",
            "point_unit_and_receipt",
        )
        evidence[
            "outer_spacing_limited_by_protected_shape"
        ] = True
    if key == (6, 1161):
        evidence["runtime_order"] = (
            "purchase_label",
            "item",
            "purchase_and_money_label",
            "money",
            "receipt",
        )
        evidence[
            "parenthetical_object_particle_in_prefill_companion"
        ] = True
    if key == (6, 1162):
        evidence["runtime_order"] = (
            "purchase_history_label",
            "representative_item",
            "comma_total_label",
            "count",
            "point_unit_purchase_and_money_label",
            "money",
            "receipt",
        )
        evidence[
            "count_unit_not_duplicated"
        ] = True
        evidence[
            "outer_spacing_limited_by_protected_shape"
        ] = True
    return evidence


def build_rows() -> tuple[Any, list[dict[str, Any]], bytes, str, int]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    predecessors = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_semantics(prepared, records_by_label, predecessors)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )

    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        dynamic = coordinate in DYNAMIC_COORDINATES
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        companions = PREFILL_COMPANIONS.get(coordinate, ())
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
            "scope_classification": (
                "runtime_fragment_pending" if dynamic else "retranslated"
            ),
            "layout_review": (
                "runtime_pending"
                if dynamic
                else "unchanged_from_current"
            ),
            "runtime_review": "pending" if dynamic else "not_required",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "base_donor_reviewed": record_id != 1126,
            "base_runtime_state_inherited": False,
            "all_available_predecessors_validated": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "same_record_prefill_companion_review": bool(companions),
            "historical_term_review": True,
            "public_resource_term_review": True,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
        }
        if dynamic:
            row["runtime_assembly_evidence"] = (
                runtime_control_evidence(
                    records_by_label,
                    (block_id, record_id),
                    companions,
                )
            )
        rows.append(row)
    return prepared, rows, candidate, candidate_sha256, changed


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1073-tamper-",
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
        len(rows) != 14
        or len(validated) != 14
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 13,
                "retranslated": 1,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            or row["runtime_assembly_evidence"][
                "base_runtime_state_inherited"
            ]
            is not False
            for row in rows
            if row["scope_classification"]
            == "runtime_fragment_pending"
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
            if row["scope_classification"] == "retranslated"
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
                "segment": "pk_msggame_B018_S1073",
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
                "exact_reuse_prefill_count": 52,
                "residual_count": 14,
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
                "base_donors_reviewed": True,
                "base_runtime_state_inherited": False,
                "same_record_prefill_companions_reviewed": sorted(
                    {
                        companion
                        for companions in PREFILL_COMPANIONS.values()
                        for companion in companions
                    }
                ),
                "merchant_runtime_order_reviewed": [
                    "6:1153",
                    "6:1154",
                    "6:1156",
                    "6:1157",
                    "6:1160",
                    "6:1161",
                    "6:1162",
                ],
                "resource_term_policy": {
                    "provisions": "병량",
                    "horses": "군마",
                    "money": "금",
                },
                "outer_spacing_followup_records": [
                    "6:1153",
                    "6:1154",
                    "6:1157",
                    "6:1160",
                    "6:1161",
                    "6:1162",
                ],
                "outside_scope_records_exact": True,
                "current_runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_terms_reviewed": [
                    "provisions",
                    "military_horses",
                    "money",
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
