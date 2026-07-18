#!/usr/bin/env python3
"""Audit and repair Issue #61 policy-effect percent literals offline.

The historical Steam JP fullwidth-normalization pass converted literal
U+FF05 percent signs to ASCII U+0025.  In a policy value such as ``%+d％``,
the first three characters are a printf token and the trailing ASCII percent
is an invalid formatter directive, so the unit is not rendered in game.

This workstream is deliberately a narrow, final-stage repair overlay.  It
does not rewrite the historical normalizer artifact or repack a stale release
baseline.  Instead it reads the exact current Steam 11-file JP text-audit
profile, restores only the 49 PK and 39 shared policy cells that are proven by
the v0.9 source and the historical hash-gated operation ledger, then writes a
private candidate below ``KR_PATCH_WORK/tmp``.  The installed game is never
opened for writing by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

FULLWIDTH_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_fullwidth_normalization_v1"
    / "build_steam_jp_fullwidth_normalization_v1.py"
)
FULLWIDTH_METADATA_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_fullwidth_normalization_v1"
    / "public"
    / "steam_jp_fullwidth_normalization.v1.json"
)
FULLWIDTH_BUILDER_PIN = {
    "size": 77_931,
    "sha256": "F9EBD80B94B890E93ACE6CD8F84E7C3592DD51D29FE97B8DAA9D0448C88D91A0",
}
FULLWIDTH_METADATA_PIN = {
    "size": 7_914_503,
    "sha256": "E902FB90D19B37168C9512A5337CE0A0CB18E1D4EEE77284667BFB7CA7B73329",
}

SCHEMA = "nobu16.kr.issue-61-policy-percent.v1"
AUDIT_SCHEMA = "nobu16.kr.issue-61-policy-percent-audit.v1"
BUILD_MANIFEST_SCHEMA = "nobu16.kr.issue-61-policy-percent-build.v1"

PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
SHARED_STRDATA = "MSG/JP/strdata.bin"
PK_MSGDATA = "MSG_PK/JP/msgdata.bin"
CHANGED_PATHS = (SHARED_STRDATA, PK_MSGDATA)

# The exact live text profile after ``pc-text-quality-wave15-16-v1``.  Its
# three dialogue resources are retain-only here: Issue 61 must preserve that
# independently applied transaction rather than restore the older Wave14
# predecessor vector.
INPUT_SPECS = {
    "MSG/JP/ev_strdata.bin": {
        "size": 928_123,
        "sha256": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    },
    "MSG/JP/msggame.bin": {
        "size": 1_504_655,
        "sha256": "EEA622999F38C72F2088467E04D4A885B684D3FD3CF99FB72879A72079CF9351",
    },
    SHARED_STRDATA: {
        "size": 957_204,
        "sha256": "5F308F416378976C1AB0B50D4A91C9DA38C637A0A842BAB04FB48256B2103E28",
    },
    "MSG_PK/JP/msgbre.bin": {
        "size": 484_068,
        "sha256": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    },
    PK_MSGDATA: {
        "size": 496_995,
        "sha256": "69090EC9EEE1DF9EAFB64BB35CEFD285A5089FDE78E9A4A855EAA0AE5991C168",
    },
    "MSG_PK/JP/msgev.bin": {
        "size": 994_711,
        "sha256": "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3",
    },
    "MSG_PK/JP/msggame.bin": {
        "size": 1_806_759,
        "sha256": "9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC",
    },
    "MSG_PK/JP/msgire.bin": {
        "size": 23_128,
        "sha256": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    },
    "MSG_PK/JP/msgstf.bin": {
        "size": 17_341,
        "sha256": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    },
    "MSG_PK/JP/msgstf_ce.bin": {
        "size": 18_767,
        "sha256": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    },
    "MSG_PK/JP/msgui.bin": {
        "size": 122_733,
        "sha256": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
    },
}

# Derived by a clean, hash-gated local ``hash`` run.  Retained paths are
# byte-identical to INPUT_SPECS; only the two audited policy resources differ.
TARGET_SPECS: dict[str, dict[str, Any]] | None = {
    **INPUT_SPECS,
    SHARED_STRDATA: {
        "size": 957_204,
        "sha256": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    },
    PK_MSGDATA: {
        "size": 496_995,
        "sha256": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    },
}

PK_POLICY_FIRST_ID = 22_506
PK_POLICY_LAST_ID = 22_701
SHARED_POLICY_BLOCK = 0
SHARED_POLICY_FIRST_SLOT = 22_254
SHARED_POLICY_LAST_SLOT = 22_387

PK_PERCENT_IDS = frozenset(
    (
        22_506, 22_507, 22_509, 22_510, 22_512, 22_514, 22_515,
        22_526, 22_527, 22_531, 22_532, 22_533, 22_534, 22_535,
        22_536, 22_537, 22_540, 22_541, 22_543, 22_548, 22_553,
        22_554, 22_555, 22_556, 22_558, 22_560, 22_563, 22_564,
        22_581, 22_585, 22_599, 22_605, 22_606, 22_614, 22_624,
        22_628, 22_629, 22_630, 22_631, 22_632, 22_635, 22_644,
        22_647, 22_648, 22_653, 22_656, 22_662, 22_664, 22_666,
    )
)
SHARED_PERCENT_SLOTS = frozenset(
    (
        22_254, 22_255, 22_257, 22_258, 22_260, 22_262, 22_263,
        22_274, 22_275, 22_279, 22_280, 22_281, 22_283, 22_284,
        22_285, 22_288, 22_289, 22_291, 22_296, 22_303, 22_304,
        22_306, 22_308, 22_312, 22_329, 22_333, 22_347, 22_353,
        22_354, 22_362, 22_372, 22_376, 22_377, 22_378, 22_379,
        22_380, 22_381, 22_382, 22_383,
    )
)
PK_PERCENT_IDS_SHA256 = "75AE1A00C7ABAA5F23064A8629BC25CC361BB0D4059EDEA909C8450EDA5D197B"
SHARED_PERCENT_SLOTS_SHA256 = "BC06F61F733A48298A1E8FB4F14AF1E247E9BFCDA763C73F59AA693ACE4BA814"

FULLWIDTH_PERCENT = "\uFF05"
ASCII_PERCENT = "%"
SOURCE_FREE_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF\u3400-\u9FFF\uF900-\uFAFF]")


class Issue61Error(RuntimeError):
    """A pinned input, policy scope, or private-output gate changed."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise Issue61Error(f"required file is absent: {path}")
    return {"size": path.stat().st_size, "sha256": sha256_path(path)}


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise Issue61Error(f"{label} differs: expected={expected!r}, actual={actual!r}")


def canonical_hash(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def source_free(value: Any) -> bool:
    return SOURCE_FREE_RE.search(json.dumps(value, ensure_ascii=False, sort_keys=True)) is None


def load_fullwidth_support() -> Any:
    require(file_spec(FULLWIDTH_BUILDER_PATH), FULLWIDTH_BUILDER_PIN, "fullwidth builder pin")
    require(file_spec(FULLWIDTH_METADATA_PATH), FULLWIDTH_METADATA_PIN, "fullwidth metadata pin")
    spec = importlib.util.spec_from_file_location("issue_61_fullwidth_support", FULLWIDTH_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise Issue61Error("cannot load fullwidth support")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    metadata = module.read_metadata()
    module.validate_metadata(metadata)
    return module


def require_under_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    target = path.resolve(strict=False)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise Issue61Error(f"{label} must remain below {TMP_ROOT}") from exc
    if target == root:
        raise Issue61Error(f"{label} cannot be the tmp root")
    return target


def live_path(steam_root: Path, relative: str) -> Path:
    root = steam_root.resolve(strict=True)
    path = (root / Path(relative)).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise Issue61Error(f"Steam resource escapes root: {relative}") from exc
    if not path.is_file():
        raise Issue61Error(f"Steam resource is absent: {relative}")
    return path


def profile_specs(root: Path) -> dict[str, dict[str, Any]]:
    return {relative: file_spec(live_path(root, relative)) for relative in PROFILE_PATHS}


def assert_profile(root: Path, expected: Mapping[str, Mapping[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    actual = profile_specs(root)
    require(actual, dict(expected), label)
    return actual


def policy_coordinates(resource: str) -> tuple[tuple[int, ...], ...]:
    if resource == PK_MSGDATA:
        return tuple((entry_id,) for entry_id in range(PK_POLICY_FIRST_ID, PK_POLICY_LAST_ID + 1))
    if resource == SHARED_STRDATA:
        return tuple(
            (SHARED_POLICY_BLOCK, slot_id)
            for slot_id in range(SHARED_POLICY_FIRST_SLOT, SHARED_POLICY_LAST_SLOT + 1)
        )
    raise Issue61Error(f"resource is outside the Issue 61 policy scope: {resource}")


def expected_percent_coordinates(resource: str) -> frozenset[tuple[int, ...]]:
    if resource == PK_MSGDATA:
        return frozenset((entry_id,) for entry_id in PK_PERCENT_IDS)
    if resource == SHARED_STRDATA:
        return frozenset((SHARED_POLICY_BLOCK, slot_id) for slot_id in SHARED_PERCENT_SLOTS)
    raise Issue61Error(f"resource is outside the Issue 61 policy scope: {resource}")


def assert_scope_constants() -> None:
    require(len(PK_PERCENT_IDS), 49, "PK percent ID count")
    require(len(SHARED_PERCENT_SLOTS), 39, "shared percent slot count")
    require(canonical_hash(sorted(PK_PERCENT_IDS)), PK_PERCENT_IDS_SHA256, "PK percent ID vector")
    require(
        canonical_hash(sorted(SHARED_PERCENT_SLOTS)),
        SHARED_PERCENT_SLOTS_SHA256,
        "shared percent slot vector",
    )
    if not PK_PERCENT_IDS.issubset(set(range(PK_POLICY_FIRST_ID, PK_POLICY_LAST_ID + 1))):
        raise Issue61Error("PK percent IDs escape the complete policy scope")
    if not SHARED_PERCENT_SLOTS.issubset(set(range(SHARED_POLICY_FIRST_SLOT, SHARED_POLICY_LAST_SLOT + 1))):
        raise Issue61Error("shared percent slots escape the complete policy scope")


def printf_tokens(text: str, fullwidth: Any) -> tuple[str, ...]:
    return tuple(match.group(0) for match in fullwidth.PRINTF_RE.finditer(text))


def unsafe_ascii_percent_indexes(text: str, fullwidth: Any) -> tuple[int, ...]:
    token_indexes = {
        index
        for match in fullwidth.PRINTF_RE.finditer(text)
        for index in range(match.start(), match.end())
    }
    return tuple(
        index
        for index, character in enumerate(text)
        if character == ASCII_PERCENT and index not in token_indexes
    )


def policy_audit(document: Any, resource: str, fullwidth: Any) -> dict[str, Any]:
    cells = fullwidth.cell_map(document)
    rows: list[dict[str, Any]] = []
    for coordinate in policy_coordinates(resource):
        text = cells.get(coordinate)
        if text is None:
            raise Issue61Error(f"policy coordinate is absent: {resource} {coordinate}")
        unsafe = unsafe_ascii_percent_indexes(text, fullwidth)
        rows.append(
            {
                "coordinate": fullwidth.coord_json(coordinate, document.kind),
                "unsafe_ascii_percent_indexes": list(unsafe),
                "fullwidth_percent_count": text.count(FULLWIDTH_PERCENT),
                "printf_token_count": len(printf_tokens(text, fullwidth)),
            }
        )
    raw_rows = [row for row in rows if row["unsafe_ascii_percent_indexes"]]
    fullwidth_rows = [row for row in rows if row["fullwidth_percent_count"]]
    return {
        "resource": resource,
        "scope_coordinate_count": len(rows),
        "unsafe_ascii_percent_coordinate_count": len(raw_rows),
        "unsafe_ascii_percent_character_count": sum(
            len(row["unsafe_ascii_percent_indexes"]) for row in raw_rows
        ),
        "unsafe_ascii_percent_coordinates": [row["coordinate"] for row in raw_rows],
        "fullwidth_percent_coordinate_count": len(fullwidth_rows),
        "fullwidth_percent_character_count": sum(
            row["fullwidth_percent_count"] for row in fullwidth_rows
        ),
        "fullwidth_percent_coordinates": [row["coordinate"] for row in fullwidth_rows],
        "printf_token_count": sum(row["printf_token_count"] for row in rows),
    }


def document_unsafe_percent_signature(document: Any, fullwidth: Any) -> dict[tuple[int, ...], tuple[int, ...]]:
    return {
        cell.coordinate: indexes
        for cell in document.cells
        if (indexes := unsafe_ascii_percent_indexes(cell.text, fullwidth))
    }


def load_v09_policy_documents(fullwidth: Any) -> dict[str, Any]:
    v09_path = fullwidth.V09_ZIP
    expected_zip = {"size": fullwidth.V09_ZIP_PIN["size"], "sha256": fullwidth.V09_ZIP_PIN["sha256"]}
    require(file_spec(v09_path), expected_zip, "v0.9 source ZIP pin")
    try:
        with zipfile.ZipFile(v09_path, "r") as archive:
            require(archive.namelist(), list(fullwidth.TARGETS), "v0.9 source ZIP member vector")
            return {
                resource: fullwidth.parse_document(resource, archive.read(resource))
                for resource in CHANGED_PATHS
            }
    except zipfile.BadZipFile as exc:
        raise Issue61Error("v0.9 source ZIP is invalid") from exc


def percent_operation(entry: Mapping[str, Any]) -> Mapping[str, Any]:
    operations = entry.get("character_operations")
    if not isinstance(operations, list) or len(operations) != 1:
        raise Issue61Error("Issue 61 coordinate must have exactly one historical character operation")
    operation = operations[0]
    if not isinstance(operation, dict) or operation.get("from") != "U+FF05" or operation.get("to") != "U+0025":
        raise Issue61Error("Issue 61 coordinate is not an exact U+FF05-to-U+0025 operation")
    if operation.get("operation_type") != "fullwidth_ascii":
        raise Issue61Error("Issue 61 percent operation has an unexpected type")
    index = operation.get("char_index")
    if type(index) is not int or index < 0:
        raise Issue61Error("Issue 61 percent operation has an invalid character index")
    return operation


def select_recovery_entries(metadata: Mapping[str, Any], documents: Mapping[str, Any], fullwidth: Any) -> dict[str, dict[tuple[int, ...], Mapping[str, Any]]]:
    selected: dict[str, dict[tuple[int, ...], Mapping[str, Any]]] = {resource: {} for resource in CHANGED_PATHS}
    for entry in metadata.get("operations", []):
        if not isinstance(entry, dict):
            raise Issue61Error("fullwidth metadata has an invalid operation entry")
        resource = entry.get("resource")
        if resource not in selected:
            continue
        document = documents[resource]
        if entry.get("kind") != document.kind:
            raise Issue61Error(f"fullwidth metadata kind differs for {resource}")
        coordinate = fullwidth.coord_from_json(entry.get("coordinate"), document.kind)
        if coordinate not in expected_percent_coordinates(resource):
            continue
        percent_operation(entry)
        if coordinate in selected[resource]:
            raise Issue61Error(f"duplicate Issue 61 metadata coordinate: {resource} {coordinate}")
        selected[resource][coordinate] = entry
    for resource in CHANGED_PATHS:
        require(
            frozenset(selected[resource]),
            expected_percent_coordinates(resource),
            f"Issue 61 metadata coordinate set {resource}",
        )
    return selected


def restore_literal_percent(text: str, entry: Mapping[str, Any], fullwidth: Any) -> str:
    operation = percent_operation(entry)
    index = int(operation["char_index"])
    if fullwidth.text_hash(text) != entry.get("after_utf16le_sha256"):
        raise Issue61Error("current policy text does not match its historical normalized hash")
    if not 0 <= index < len(text) or text[index] != ASCII_PERCENT:
        raise Issue61Error("current policy text does not have the pinned ASCII percent literal")
    replacement = text[:index] + FULLWIDTH_PERCENT + text[index + 1 :]
    if printf_tokens(replacement, fullwidth) != printf_tokens(text, fullwidth):
        raise Issue61Error("percent recovery altered the printf token vector")
    if unsafe_ascii_percent_indexes(replacement, fullwidth):
        raise Issue61Error("percent recovery did not remove all unsafe ASCII percent literals")
    if fullwidth.text_hash(replacement) != entry.get("before_utf16le_sha256"):
        raise Issue61Error("percent recovery does not restore the historical pre-normalization hash")
    return replacement


def verify_changed_documents(
    source_documents: Mapping[str, Any],
    candidate_documents: Mapping[str, Any],
    v09_documents: Mapping[str, Any],
    selected: Mapping[str, Mapping[tuple[int, ...], Mapping[str, Any]]],
    fullwidth: Any,
) -> None:
    for resource in CHANGED_PATHS:
        source = fullwidth.cell_map(source_documents[resource])
        candidate = fullwidth.cell_map(candidate_documents[resource])
        oracle = fullwidth.cell_map(v09_documents[resource])
        require(set(candidate), set(source), f"candidate coordinate vector {resource}")
        for coordinate, before in source.items():
            after = candidate[coordinate]
            if coordinate not in selected[resource]:
                require(after, before, f"non-target text preservation {resource} {coordinate}")
                continue
            require(after, oracle.get(coordinate), f"v0.9 source restoration {resource} {coordinate}")
            require(
                unsafe_ascii_percent_indexes(after, fullwidth),
                (),
                f"restored target unsafe-percent signature {resource} {coordinate}",
            )
        before_unsafe = document_unsafe_percent_signature(source_documents[resource], fullwidth)
        after_unsafe = document_unsafe_percent_signature(candidate_documents[resource], fullwidth)
        for coordinate in set(before_unsafe) | set(after_unsafe):
            if coordinate in selected[resource]:
                require(after_unsafe.get(coordinate, ()), (), f"target unsafe-percent removal {resource} {coordinate}")
            else:
                require(
                    after_unsafe.get(coordinate, ()),
                    before_unsafe.get(coordinate, ()),
                    f"non-target unsafe-percent preservation {resource} {coordinate}",
                )


def assert_policy_audits(
    predecessor: Mapping[str, Any],
    candidate: Mapping[str, Any],
    source: Mapping[str, Any],
    fullwidth: Any,
) -> dict[str, Any]:
    predecessor_audit = {
        resource: policy_audit(predecessor[resource], resource, fullwidth)
        for resource in CHANGED_PATHS
    }
    candidate_audit = {
        resource: policy_audit(candidate[resource], resource, fullwidth)
        for resource in CHANGED_PATHS
    }
    source_audit = {
        resource: policy_audit(source[resource], resource, fullwidth)
        for resource in CHANGED_PATHS
    }
    expected_coordinate_objects = {
        resource: [
            fullwidth.coord_json(coordinate, predecessor[resource].kind)
            for coordinate in sorted(expected_percent_coordinates(resource))
        ]
        for resource in CHANGED_PATHS
    }
    for resource, expected_count in ((PK_MSGDATA, 49), (SHARED_STRDATA, 39)):
        expected_coordinates = expected_coordinate_objects[resource]
        require(
            predecessor_audit[resource]["unsafe_ascii_percent_coordinates"],
            expected_coordinates,
            f"predecessor Issue 61 unsafe-percent coordinate vector {resource}",
        )
        require(
            predecessor_audit[resource]["unsafe_ascii_percent_character_count"],
            expected_count,
            f"predecessor Issue 61 unsafe-percent character count {resource}",
        )
        require(
            candidate_audit[resource]["unsafe_ascii_percent_character_count"],
            0,
            f"candidate policy unsafe-percent character count {resource}",
        )
        require(
            source_audit[resource]["unsafe_ascii_percent_character_count"],
            0,
            f"v0.9 policy unsafe-percent character count {resource}",
        )
        require(
            candidate_audit[resource]["fullwidth_percent_coordinate_count"],
            source_audit[resource]["fullwidth_percent_coordinate_count"],
            f"candidate/v0.9 fullwidth percent coordinate count {resource}",
        )
        require(
            candidate_audit[resource]["fullwidth_percent_character_count"],
            source_audit[resource]["fullwidth_percent_character_count"],
            f"candidate/v0.9 fullwidth percent character count {resource}",
        )
    return {
        "predecessor": predecessor_audit,
        "candidate": candidate_audit,
        "v0_9_source": source_audit,
        "expected_recovery_coordinates": expected_coordinate_objects,
    }


def prepare_candidate(
    steam_root: Path,
    *,
    require_pinned_targets: bool,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    assert_scope_constants()
    fullwidth = load_fullwidth_support()
    steam_root = steam_root.resolve(strict=True)
    before_profile = assert_profile(steam_root, INPUT_SPECS, "current Steam predecessor profile")
    packed = {resource: live_path(steam_root, resource).read_bytes() for resource in CHANGED_PATHS}
    documents = {resource: fullwidth.parse_document(resource, packed[resource]) for resource in CHANGED_PATHS}
    v09_documents = load_v09_policy_documents(fullwidth)
    metadata = fullwidth.read_metadata()
    selected = select_recovery_entries(metadata, documents, fullwidth)

    candidate_payloads: dict[str, bytes] = {}
    changes: list[dict[str, Any]] = []
    candidate_documents: dict[str, Any] = {}
    for resource in CHANGED_PATHS:
        source_cells = fullwidth.cell_map(documents[resource])
        replacements: dict[tuple[int, ...], str] = {}
        for coordinate, entry in sorted(selected[resource].items()):
            before = source_cells.get(coordinate)
            if before is None:
                raise Issue61Error(f"current policy coordinate is absent: {resource} {coordinate}")
            after = restore_literal_percent(before, entry, fullwidth)
            replacements[coordinate] = after
            changes.append(
                {
                    "resource": resource,
                    "coordinate": fullwidth.coord_json(coordinate, documents[resource].kind),
                    "character_index": percent_operation(entry)["char_index"],
                    "predecessor_utf16le_sha256": fullwidth.text_hash(before),
                    "candidate_utf16le_sha256": fullwidth.text_hash(after),
                    "v0_9_source_utf16le_sha256": fullwidth.text_hash(
                        fullwidth.cell_map(v09_documents[resource])[coordinate]
                    ),
                    "printf_token_count": len(printf_tokens(before, fullwidth)),
                    "operation": "restore_fullwidth_percent_literal",
                }
            )
        candidate_payload = documents[resource].rebuild(replacements)
        candidate_document = fullwidth.parse_document(resource, candidate_payload)
        candidate_payloads[resource] = candidate_payload
        candidate_documents[resource] = candidate_document

    require(len(changes), 88, "Issue 61 total changed coordinate count")
    verify_changed_documents(documents, candidate_documents, v09_documents, selected, fullwidth)
    policy = assert_policy_audits(documents, candidate_documents, v09_documents, fullwidth)
    target_profile = {**before_profile, **{resource: fullwidth.spec(value) for resource, value in candidate_payloads.items()}}
    if require_pinned_targets:
        if TARGET_SPECS is None:
            raise Issue61Error("target profile is not pinned; run the read-only hash command first")
        require(target_profile, TARGET_SPECS, "Issue 61 target profile")
    after_profile = assert_profile(steam_root, before_profile, "Steam predecessor unchanged after candidate preparation")
    audit = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "runtime": {
            "distribution": "Steam",
            "pk_version": "1.1.7",
            "steam_build_id": 18_823_764,
            "language_route": "JP",
        },
        "profile_paths": list(PROFILE_PATHS),
        "changed_paths": list(CHANGED_PATHS),
        "predecessor_profile": before_profile,
        "candidate_profile": target_profile,
        "predecessor_unchanged_after_prepare": after_profile == before_profile,
        "provenance": {
            "fullwidth_builder": {"path": str(FULLWIDTH_BUILDER_PATH.relative_to(REPO)).replace("\\", "/"), **FULLWIDTH_BUILDER_PIN},
            "fullwidth_metadata": {"path": str(FULLWIDTH_METADATA_PATH.relative_to(REPO)).replace("\\", "/"), **FULLWIDTH_METADATA_PIN},
            "v0_9_source_zip": {"path": str(fullwidth.V09_ZIP.relative_to(REPO)).replace("\\", "/"), **{"size": fullwidth.V09_ZIP_PIN["size"], "sha256": fullwidth.V09_ZIP_PIN["sha256"]}},
        },
        "policy": policy,
        "changes": changes,
        "safety": {
            "installed_game_file_written": False,
            "candidate_output_private_tmp_only": True,
            "only_hash_gated_policy_percent_literals_changed": True,
            "non_target_text_cells_byte_semantic_preserved": True,
            "fonts_images_executables_registry_memory_network_unchanged": True,
            "source_text_free": True,
        },
    }
    if not source_free(audit):
        raise Issue61Error("audit must remain source-text-free")
    return candidate_payloads, audit


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise Issue61Error(f"refusing to overwrite output: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def assert_candidate_tree(root: Path, expected: Mapping[str, Mapping[str, Any]], label: str) -> None:
    if not root.is_dir():
        raise Issue61Error(f"{label} candidate root is absent")
    actual_files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }
    require(actual_files, set(PROFILE_PATHS), f"{label} candidate file vector")
    actual = {
        relative: file_spec(root / Path(relative))
        for relative in PROFILE_PATHS
    }
    require(actual, dict(expected), f"{label} candidate profile")


def build_candidate(steam_root: Path, output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    output_root = require_under_tmp(output_root, "candidate output")
    audit_path = require_under_tmp(audit_path, "audit output")
    manifest_path = require_under_tmp(manifest_path, "manifest output")
    if output_root in (audit_path, manifest_path) or audit_path == manifest_path:
        raise Issue61Error("candidate, audit, and manifest outputs must be distinct")
    for path, label in ((audit_path, "audit"), (manifest_path, "manifest")):
        try:
            path.relative_to(output_root)
        except ValueError:
            pass
        else:
            raise Issue61Error(f"{label} must not be stored inside the candidate root")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Issue61Error("candidate output, audit, or manifest already exists")

    payloads, audit = prepare_candidate(steam_root, require_pinned_targets=True)
    target_profile = audit["candidate_profile"]
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.stage-", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            destination = stage / Path(relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative in payloads:
                destination.write_bytes(payloads[relative])
            else:
                shutil.copyfile(live_path(steam_root, relative), destination)
        assert_candidate_tree(stage, target_profile, "staged")
        before_promote = assert_profile(steam_root, INPUT_SPECS, "Steam predecessor before candidate promotion")
        os.replace(stage, output_root)
        assert_candidate_tree(output_root, target_profile, "promoted")
        after_promote = assert_profile(steam_root, before_promote, "Steam predecessor after candidate promotion")
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise

    audit_bytes = canonical_json(audit)
    atomic_write(audit_path, audit_bytes)
    manifest = {
        "schema": BUILD_MANIFEST_SCHEMA,
        "audit_sha256": sha256_bytes(audit_bytes),
        "profile_paths": list(PROFILE_PATHS),
        "changed_paths": list(CHANGED_PATHS),
        "predecessor_profile": INPUT_SPECS,
        "candidate_profile": target_profile,
        "promoted_candidate_verified": True,
        "steam_predecessor_unchanged_after_build": after_promote == before_promote,
        "safety": audit["safety"],
    }
    if not source_free(manifest):
        raise Issue61Error("build manifest must remain source-text-free")
    atomic_write(manifest_path, canonical_json(manifest))
    return manifest


def verify_candidate(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output_root = require_under_tmp(output_root, "candidate output")
    payloads, audit = prepare_candidate(steam_root, require_pinned_targets=True)
    expected = audit["candidate_profile"]
    assert_candidate_tree(output_root, expected, "existing")
    for resource, payload in payloads.items():
        require((output_root / Path(resource)).read_bytes(), payload, f"candidate payload {resource}")
    assert_profile(steam_root, INPUT_SPECS, "Steam predecessor unchanged after candidate verification")
    return {
        "schema": BUILD_MANIFEST_SCHEMA,
        "status": "PASS",
        "candidate_profile": expected,
        "changed_coordinate_count": len(audit["changes"]),
        "steam_files_written": False,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    for command_name in ("audit", "hash", "build", "verify"):
        command = sub.add_parser(command_name)
        command.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
        if command_name in {"build", "verify"}:
            command.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
        if command_name == "build":
            command.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
            command.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command in {"audit", "hash"}:
            _payloads, audit = prepare_candidate(args.steam_root, require_pinned_targets=False)
            print(canonical_json(audit).decode("utf-8"), end="")
            return 0
        if args.command == "build":
            manifest = build_candidate(args.steam_root, args.output_root, args.audit_path, args.manifest_path)
            print(canonical_json({"status": "PASS", "manifest": manifest, "steam_files_written": False}).decode("utf-8"), end="")
            return 0
        report = verify_candidate(args.steam_root, args.output_root)
        print(canonical_json(report).decode("utf-8"), end="")
        return 0
    except (Issue61Error, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(canonical_json({"status": "FAIL", "error": str(exc), "steam_files_written": False}).decode("utf-8"), end="", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
