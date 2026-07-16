#!/usr/bin/env python3
"""Rebase text-fit improvements onto the *current* Steam JP installation.

This is deliberately not a v0.9 package rebuild.  It starts from each live
Steam JP resource, verifies that source against a frozen current-state
contract, and makes only these narrow changes:

* the source-free, per-coordinate fullwidth-ASCII operations;
* the source-free, linebreak-only operations in ``ev_strdata``;
* the approved font candidate's G1N outer entries only.

The historical v0.9 full-text archive and the earlier non-logo image composite
are not inputs.  In particular, ``RES_JP/res_lang.bin`` outer entries ``/3``
and ``/24`` are never replacement sources.  They are read only after building
to prove that their payload and following gap remain byte-identical to the
current Steam base.  The builder never writes a game installation, a release,
GitHub, an EXE, the registry, memory, or a DLL.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, parse_link, rebuild_link, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load support module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FULLWIDTH = _load_module(
    "steam_jp_current_state_fullwidth_support",
    REPO / "workstreams" / "steam_jp_fullwidth_normalization_v1" / "build_steam_jp_fullwidth_normalization_v1.py",
)
LINEBREAK = _load_module(
    "steam_jp_current_state_linebreak_support",
    REPO / "workstreams" / "steam_jp_switch_v23_linebreak_v1" / "build_steam_jp_switch_v23_linebreak_v1.py",
)


SCHEMA = "nobu16.kr.steam-jp-current-state-textfit-rebase.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-current-state-textfit-rebase-validation.v1"
BUILD_MANIFEST_SCHEMA = "nobu16.kr.steam-jp-current-state-textfit-rebase-build.v1"
CONTRACT_PATH = WORKSTREAM / "current_state_contract.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "steam_jp_current_state_textfit_rebase_v1" / "candidate"

FULLWIDTH_METADATA = (
    REPO
    / "workstreams"
    / "steam_jp_fullwidth_normalization_v1"
    / "public"
    / "steam_jp_fullwidth_normalization.v1.json"
)
LINEBREAK_OVERLAY = (
    REPO
    / "workstreams"
    / "steam_jp_switch_v23_linebreak_v1"
    / "public"
    / "ev_strdata_ko_switch_v23_linebreak_640.v1.json"
)
FONT_RUN_ROOT = TMP_ROOT / "steam_jp_font_advance_candidate_v1_run7" / "private"
FONT_MANIFEST = FONT_RUN_ROOT / "manifest.json"
FONT_CANDIDATE_ROOT = FONT_RUN_ROOT / "candidate"

TARGETS = tuple(FULLWIDTH.TARGETS)
TEXT_RESOURCES = tuple(FULLWIDTH.TEXT_KINDS)
FONT_RESOURCES = tuple(FULLWIDTH.FONT_G1N_ROUTES)
EV_RESOURCE = "MSG/JP/ev_strdata.bin"
RES_JP = "RES_JP/res_lang.bin"
SPECIAL_RES_JP_ENTRIES = (3, 24)
PURE_LINEBREAK_OPERATIONS = {
    "switch_v23_coordinate_exact_linebreak_to_ascii_space",
    "switch_v23_rebased_linebreak_to_ascii_space",
}
MANUAL_LINEBREAK_OPERATION = "manual_korean_residual_translation_and_linebreak_repair"
SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30FF\u31F0-\u31FF\u3400-\u9FFF\uF900-\uFAFF]"
)

# These pins name the reviewed upstream inputs, not a v0.9 full-text payload.
# They keep a later ``freeze`` from silently accepting a different operation
# model or a different private font candidate.
STATIC_INPUT_PINS: dict[str, Any] = {
    "fullwidth_metadata": {
        "path": "workstreams/steam_jp_fullwidth_normalization_v1/public/steam_jp_fullwidth_normalization.v1.json",
        "size": 7_914_503,
        "sha256": "E902FB90D19B37168C9512A5337CE0A0CB18E1D4EEE77284667BFB7CA7B73329",
    },
    "linebreak_overlay": {
        "path": "workstreams/steam_jp_switch_v23_linebreak_v1/public/ev_strdata_ko_switch_v23_linebreak_640.v1.json",
        "size": 936_927,
        "sha256": "231833C0110D3C5792DDBB3781A2927419A0E162F18AD68126074462248A36E9",
    },
    "font_manifest": {
        "path": "tmp/steam_jp_font_advance_candidate_v1_run7/private/manifest.json",
        "size": 116_367,
        "sha256": "8C88E124E5F9C18FF931A5DE87144C8FEBD4D42145C44F0AFD965105A1710D13",
    },
    "font_candidates": {
        "RES_JP/res_lang.bin": {
            "path": "tmp/steam_jp_font_advance_candidate_v1_run7/private/candidate/RES_JP/res_lang.bin",
            "size": 155_757_652,
            "sha256": "64CCD9068D7EBCFA670091B8A8FB367F1E577C1BCAC05847F4F3C77D7219A64D",
        },
        "RES_JP_PK/res_lang_pk.bin": {
            "path": "tmp/steam_jp_font_advance_candidate_v1_run7/private/candidate/RES_JP_PK/res_lang_pk.bin",
            "size": 143_288_371,
            "sha256": "C0C8509FC91C244A813D4BC20C46E515F6396D03BEAC71B80F89A39245125189",
        },
        "RES_JP_PK_PORT/res_lang_pk_port1.bin": {
            "path": "tmp/steam_jp_font_advance_candidate_v1_run7/private/candidate/RES_JP_PK_PORT/res_lang_pk_port1.bin",
            "size": 80_697_755,
            "sha256": "B5BF46E90C444DE1931BCF455447168C01B77967D3143B72916636157F59DE00",
        },
        "RES_JP_PK_PORT/res_lang_pk_port2.bin": {
            "path": "tmp/steam_jp_font_advance_candidate_v1_run7/private/candidate/RES_JP_PK_PORT/res_lang_pk_port2.bin",
            "size": 71_294_187,
            "sha256": "13504CB00D09D9A43B9EA5D9AD9FADEF8F58EC12CD290872EAC3FF31335DDA60",
        },
    },
}


class RebaseError(RuntimeError):
    """The current-base, source-free, or preservation contract differed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RebaseError(f"required file is missing: {path}")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return {"size": size, "sha256": digest.hexdigest().upper()}


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def id_hash(values: Sequence[int]) -> str:
    return sha256(",".join(str(value) for value in sorted(values)).encode("ascii"))


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise RebaseError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def require_true(actual: Any, label: str) -> None:
    if actual is not True:
        raise RebaseError(f"{label} must be true")


def source_free(value: Any) -> bool:
    """Public contract/validation contain hashes and coordinates, never source prose."""

    return SOURCE_TEXT_RE.search(json.dumps(value, ensure_ascii=False, sort_keys=True)) is None


def require_source_free(value: Any, label: str) -> None:
    require_true(source_free(value), f"{label} source-free scan")


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RebaseError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise RebaseError(f"{label} root is not an object")
    return value


def check_static_input(path: Path, pin: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = file_spec(path)
    expected = {"size": pin["size"], "sha256": pin["sha256"]}
    require(actual, expected, f"{label} static pin")
    return {"path": pin["path"], **actual}


def safe_steam_path(steam_root: Path, relative: str) -> Path:
    root = steam_root.resolve(strict=True)
    candidate = (root / Path(relative)).resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise RebaseError(f"Steam resource escapes root: {relative}") from exc
    if not candidate.is_file():
        raise RebaseError(f"Steam resource is not a regular file: {relative}")
    return candidate


def safe_tmp_root(path: Path) -> Path:
    root = TMP_ROOT.resolve(strict=True)
    absolute = path.resolve(strict=False)
    try:
        absolute.relative_to(root)
    except ValueError as exc:
        raise RebaseError("private output must stay below KR_PATCH_WORK/tmp") from exc
    if absolute == root:
        raise RebaseError("private output must not be the tmp root")
    return absolute


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def unpack_spec(packed: bytes, label: str) -> dict[str, Any]:
    _header, raw = decompress_wrapper(packed)
    return {"packed": spec(packed), "raw": spec(raw)}


def load_external_inputs() -> dict[str, Any]:
    pins = {
        "fullwidth_metadata": check_static_input(
            FULLWIDTH_METADATA, STATIC_INPUT_PINS["fullwidth_metadata"], "fullwidth metadata"
        ),
        "linebreak_overlay": check_static_input(
            LINEBREAK_OVERLAY, STATIC_INPUT_PINS["linebreak_overlay"], "linebreak overlay"
        ),
        "font_manifest": check_static_input(
            FONT_MANIFEST, STATIC_INPUT_PINS["font_manifest"], "font manifest"
        ),
        "font_candidates": {},
    }
    for resource in FONT_RESOURCES:
        pin = STATIC_INPUT_PINS["font_candidates"][resource]
        candidate_path = FONT_CANDIDATE_ROOT / Path(resource)
        pins["font_candidates"][resource] = check_static_input(
            candidate_path, pin, f"font candidate {resource}"
        )

    metadata = FULLWIDTH.read_metadata(FULLWIDTH_METADATA)
    require_source_free(metadata, "fullwidth metadata")
    scope = metadata.get("scope")
    if not isinstance(scope, dict):
        raise RebaseError("fullwidth scope is absent")
    require(scope.get("active_text_resource_count"), 10, "fullwidth active resource count")
    require(scope.get("automatic_normalization_coordinate_count"), 3460, "fullwidth coordinate count")
    require(len(metadata.get("operations", [])), 3460, "fullwidth operation vector")

    overlay = read_json(LINEBREAK_OVERLAY, "linebreak overlay")
    require(overlay.get("schema"), "nobu16.kr.steam-jp-switch-v23-linebreak-overlay.v1", "linebreak schema")
    require(overlay.get("resource"), EV_RESOURCE, "linebreak resource")
    require(overlay.get("entry_count"), 640, "linebreak entry count")
    # The historical overlay is an input model, not a public output from this
    # workstream.  Its four explicitly manual rows can retain review context;
    # this builder never reads ``ko`` as a replacement string and emits only
    # hashes, coordinates, and operation counts into its own artifacts.

    manifest = read_json(FONT_MANIFEST, "font manifest")
    require(manifest.get("schema"), "nobu16.kr.steam-jp-font-advance-candidate.v1", "font manifest schema")
    routes = manifest.get("routes")
    if not isinstance(routes, list):
        raise RebaseError("font manifest route list is absent")
    route_map: dict[str, dict[str, Any]] = {}
    for route in routes:
        if not isinstance(route, dict):
            raise RebaseError("font manifest route is invalid")
        resource = route.get("logical_path")
        if resource not in FONT_RESOURCES or resource in route_map:
            raise RebaseError("font manifest route domain differs")
        pin = STATIC_INPUT_PINS["font_candidates"][resource]
        require(route.get("candidate_size"), pin["size"], f"font manifest candidate size {resource}")
        require(route.get("candidate_sha256"), pin["sha256"], f"font manifest candidate hash {resource}")
        target_rows = route.get("targets")
        verification = route.get("verification")
        if not isinstance(target_rows, list) or not isinstance(verification, dict):
            raise RebaseError(f"font manifest target model is absent: {resource}")
        verification_targets = verification.get("targets")
        if not isinstance(verification_targets, list):
            raise RebaseError(f"font manifest verification targets are absent: {resource}")
        final_by_outer = {
            item.get("outer_entry"): item
            for item in verification_targets
            if isinstance(item, dict) and isinstance(item.get("outer_entry"), int)
        }
        expected_outers = tuple(FULLWIDTH.FONT_G1N_ROUTES[resource])
        target_by_outer: dict[int, dict[str, Any]] = {}
        for item in target_rows:
            if not isinstance(item, dict):
                raise RebaseError(f"font manifest target is invalid: {resource}")
            outer = item.get("outer_entry")
            preimage = item.get("preimage_g1n_sha256")
            final = final_by_outer.get(outer)
            if outer not in expected_outers or not isinstance(preimage, str) or not isinstance(final, dict):
                raise RebaseError(f"font manifest target route differs: {resource}")
            final_hash = final.get("g1n_sha256")
            final_size = final.get("g1n_size")
            if not isinstance(final_hash, str) or not isinstance(final_size, int):
                raise RebaseError(f"font manifest output target differs: {resource}")
            target_by_outer[outer] = {
                "preimage_g1n_sha256": preimage,
                "candidate_g1n_sha256": final_hash,
                "candidate_g1n_size": final_size,
            }
        require(tuple(sorted(target_by_outer)), tuple(sorted(expected_outers)), f"font target vector {resource}")
        route_map[resource] = target_by_outer
    require(tuple(route_map), FONT_RESOURCES, "font manifest resource vector")

    return {
        "pins": pins,
        "fullwidth_metadata": metadata,
        "linebreak_overlay": overlay,
        "font_targets": route_map,
    }


def load_current_texts(steam_root: Path) -> tuple[dict[str, bytes], dict[str, Any], dict[str, dict[str, Any]]]:
    payloads: dict[str, bytes] = {}
    documents: dict[str, Any] = {}
    baseline: dict[str, dict[str, Any]] = {}
    for resource in TEXT_RESOURCES:
        payload = safe_steam_path(steam_root, resource).read_bytes()
        document = FULLWIDTH.parse_document(resource, payload)
        packed_raw = unpack_spec(payload, resource)
        baseline[resource] = {
            **packed_raw,
            "text_coordinate_count": len(document.cells),
            "kind": document.kind,
        }
        payloads[resource] = payload
        documents[resource] = document
    return payloads, documents, baseline


def current_font_baseline(steam_root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for resource in FONT_RESOURCES:
        result[resource] = {"packed": file_spec(safe_steam_path(steam_root, resource))}
    return result


def apply_fullwidth_to_current(
    payloads: Mapping[str, bytes], documents: Mapping[str, Any], metadata: Mapping[str, Any]
) -> tuple[dict[str, bytes], dict[str, dict[tuple[int, ...], str]], dict[str, Any]]:
    """Apply only hash-gated operations to live current text, never old payloads.

    Newer translations can legitimately replace an old fullwidth-model cell.
    A changed coordinate is not an error and is never normalized heuristically:
    it is recorded as deferred and left byte-for-byte/current-text unchanged.
    All other coordinates still have to satisfy the original source hash,
    protected-token vector, character-operation vector, and target hash.
    """

    raw_operations = metadata.get("operations")
    if not isinstance(raw_operations, list) or len(raw_operations) != 3460:
        raise RebaseError("fullwidth metadata operation vector differs")
    automatic_map = FULLWIDTH.map_from_metadata(metadata)
    operation_types = FULLWIDTH.operation_types_from_map(automatic_map)
    cell_maps = {resource: FULLWIDTH.cell_map(document) for resource, document in documents.items()}
    replacements: dict[str, dict[tuple[int, ...], str]] = {resource: {} for resource in TEXT_RESOURCES}
    deferred: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[int, ...]]] = set()
    for entry in raw_operations:
        if not isinstance(entry, dict):
            raise RebaseError("fullwidth metadata operation is invalid")
        resource = entry.get("resource")
        if resource not in documents or entry.get("kind") != documents[resource].kind:
            raise RebaseError("fullwidth metadata resource/kind differs")
        coordinate = FULLWIDTH.coord_from_json(entry.get("coordinate"), documents[resource].kind)
        key = (resource, coordinate)
        if key in seen:
            raise RebaseError("duplicate fullwidth metadata coordinate")
        seen.add(key)
        source = cell_maps[resource].get(coordinate)
        if source is None:
            raise RebaseError("fullwidth metadata coordinate is absent from current resource")
        if FULLWIDTH.text_hash(source) != entry.get("before_utf16le_sha256"):
            deferred.append(
                {
                    "resource": resource,
                    "kind": documents[resource].kind,
                    "coordinate": FULLWIDTH.coord_json(coordinate, documents[resource].kind),
                    "reason": "current_preimage_hash_mismatch",
                }
            )
            continue
        character_operations = entry.get("character_operations")
        if not isinstance(character_operations, list):
            raise RebaseError("fullwidth character-operation vector is absent")
        try:
            target, observed = FULLWIDTH.normalization_operations(source, automatic_map, operation_types)
        except FULLWIDTH.NormalizationError as exc:
            raise RebaseError("fullwidth operation generation failed") from exc
        require(observed, character_operations, "fullwidth character-operation replay")
        require(FULLWIDTH.text_hash(target), entry.get("after_utf16le_sha256"), "fullwidth target hash")
        require(FULLWIDTH.protected_signature(source), entry.get("protected_invariants"), "fullwidth protected source")
        replacements[resource][coordinate] = target
    require(len(seen), 3460, "fullwidth unique coordinate count")
    output = dict(payloads)
    for resource in TEXT_RESOURCES:
        values = replacements[resource]
        if not values:
            continue
        candidate = documents[resource].rebuild(values)
        reparsed = FULLWIDTH.parse_document(resource, candidate)
        expected = FULLWIDTH.cell_map(documents[resource])
        expected.update(values)
        require(FULLWIDTH.cell_map(reparsed), expected, f"fullwidth reparse {resource}")
        output[resource] = candidate
    deferred_by_resource = {
        resource: sum(item["resource"] == resource for item in deferred) for resource in TEXT_RESOURCES
    }
    report = {
        "metadata_coordinate_count": len(seen),
        "applied_coordinate_count": sum(len(rows) for rows in replacements.values()),
        "deferred_coordinate_count": len(deferred),
        "deferred_coordinate_vector_sha256": sha256(canonical_json(deferred)),
        "deferred_reason_counts": {
            reason: sum(item["reason"] == reason for item in deferred)
            for reason in sorted({item["reason"] for item in deferred})
        },
        "resource_applied_counts": {resource: len(replacements[resource]) for resource in TEXT_RESOURCES},
        "resource_deferred_counts": deferred_by_resource,
        "mode": "current_preimage_hash_gated_fullwidth_ascii_only__mismatches_deferred_unchanged",
        "deferred_coordinates_are_not_replacement_sources": True,
    }
    return output, replacements, report


def linebreak_entries(overlay: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    values = overlay.get("entries")
    if not isinstance(values, list) or len(values) != 640:
        raise RebaseError("linebreak entry vector differs")
    result: dict[int, dict[str, Any]] = {}
    counts = {operation: 0 for operation in (*PURE_LINEBREAK_OPERATIONS, MANUAL_LINEBREAK_OPERATION)}
    for value in values:
        if not isinstance(value, dict):
            raise RebaseError("linebreak entry is invalid")
        entry_id = value.get("id")
        operation = value.get("operation")
        if not isinstance(entry_id, int) or entry_id < 0 or entry_id in result or operation not in counts:
            raise RebaseError("linebreak coordinate/operation differs")
        if not isinstance(value.get("preimage_utf16le_sha256"), str):
            raise RebaseError("linebreak preimage hash is absent")
        if not isinstance(value.get("preimage_linebreak_vector"), list):
            raise RebaseError("linebreak vector is absent")
        if not isinstance(value.get("preimage_protected_signature"), dict):
            raise RebaseError("linebreak protected preimage is absent")
        if not isinstance(value.get("target_protected_signature"), dict):
            raise RebaseError("linebreak protected target is absent")
        result[entry_id] = value
        counts[operation] += 1
    require(counts["switch_v23_coordinate_exact_linebreak_to_ascii_space"], 625, "exact linebreak count")
    require(counts["switch_v23_rebased_linebreak_to_ascii_space"], 11, "rebased linebreak count")
    require(counts[MANUAL_LINEBREAK_OPERATION], 4, "manual linebreak count")
    return result


def apply_linebreak_after_fullwidth(
    source_packed: bytes,
    fullwidth_packed: bytes,
    source_document: Any,
    fullwidth_replacements: Mapping[tuple[int, ...], str],
    overlay: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    """Compose current -> fullwidth -> linebreak once, without copying overlay prose."""

    _source_header, source_raw = decompress_wrapper(source_packed)
    source_table = parse_message_table(source_raw)
    header, raw = decompress_wrapper(fullwidth_packed)
    table = parse_message_table(raw)
    require(source_table.string_count, table.string_count, "ev string count after fullwidth")
    require(rebuild_message_table(table, table.texts), raw, "ev fullwidth raw round-trip")
    entries = linebreak_entries(overlay)
    source_cells = FULLWIDTH.cell_map(source_document)
    fullwidth_ids = {coordinate[0] for coordinate in fullwidth_replacements}
    require(all(0 <= value < table.string_count for value in entries), True, "linebreak ids in range")

    manual_ids = sorted(
        entry_id
        for entry_id, entry in entries.items()
        if entry["operation"] == MANUAL_LINEBREAK_OPERATION
    )
    overlap_ids = sorted(set(entries) & fullwidth_ids)
    manual_overlap = sorted(set(manual_ids) & fullwidth_ids)
    require(manual_overlap, [], "manual residual/fullwidth overlap")

    replacements: dict[int, str] = {}
    deferred: dict[int, str] = {}
    applied: list[int] = []
    replaced_tokens = 0
    for entry_id, entry in entries.items():
        before_current = source_cells[(entry_id,)]
        before_fullwidth = table.texts[entry_id]
        operation = entry["operation"]
        if operation == MANUAL_LINEBREAK_OPERATION:
            # These four are authored Korean residual translations in the old
            # overlay.  A layout rebase must not inject them into a newer text.
            require(before_fullwidth, before_current, f"manual residual unchanged {entry_id}")
            deferred[entry_id] = "manual_translation_not_rebased"
            continue
        if LINEBREAK.text_hash(before_current) != entry["preimage_utf16le_sha256"]:
            deferred[entry_id] = "current_preimage_hash_mismatch"
            continue
        expected_breaks = tuple(entry["preimage_linebreak_vector"])
        if LINEBREAK.linebreaks(before_fullwidth) != expected_breaks:
            deferred[entry_id] = "current_linebreak_vector_mismatch"
            continue
        if LINEBREAK.protected_signature(before_fullwidth) != entry["preimage_protected_signature"]:
            deferred[entry_id] = "current_protected_signature_mismatch"
            continue
        after = LINEBREAK.replace_hard_breaks_with_ascii_space(before_fullwidth)
        try:
            LINEBREAK.assert_linebreak_only_transition(
                before_fullwidth, after, expected_breaks, f"current rebase {entry_id}"
            )
        except LINEBREAK.LinebreakError as exc:
            raise RebaseError(f"linebreak transition failed at {entry_id}") from exc
        require(
            LINEBREAK.protected_signature(after),
            entry["target_protected_signature"],
            f"linebreak protected target {entry_id}",
        )
        replacements[entry_id] = after
        applied.append(entry_id)
        replaced_tokens += len(expected_breaks)

    final_texts = [replacements.get(index, text) for index, text in enumerate(table.texts)]
    candidate_raw = rebuild_message_table(table, final_texts)
    candidate = recompress_wrapper(candidate_raw, header)
    _candidate_header, roundtrip = decompress_wrapper(candidate)
    require(roundtrip, candidate_raw, "ev combined wrapper round-trip")
    candidate_table = parse_message_table(candidate_raw)
    require(candidate_table.string_count, table.string_count, "ev combined string count")
    for entry_id, after in replacements.items():
        require(candidate_table.texts[entry_id], after, f"ev combined target {entry_id}")
    for entry_id in manual_ids:
        require(candidate_table.texts[entry_id], table.texts[entry_id], f"manual residual remains unchanged {entry_id}")
    changed = {
        entry_id
        for entry_id, (before, after) in enumerate(zip(table.texts, candidate_table.texts, strict=True))
        if before != after
    }
    require(changed, set(replacements), "ev linebreak changed domain")
    return candidate, {
        "resource": EV_RESOURCE,
        "linebreak_entry_count": len(entries),
        "linebreak_only_available_count": 636,
        "linebreak_applied_count": len(applied),
        "linebreak_applied_ids_sha256": id_hash(applied),
        "linebreak_deferred_count": len(deferred),
        "linebreak_deferred_ids_sha256": id_hash(list(deferred)),
        "linebreak_deferred_reason_counts": {
            reason: sum(value == reason for value in deferred.values())
            for reason in sorted(set(deferred.values()))
        },
        "linebreak_tokens_replaced": replaced_tokens,
        "manual_residual_count": len(manual_ids),
        "manual_residual_ids_sha256": id_hash(manual_ids),
        "manual_residual_changed": False,
        "fullwidth_linebreak_overlap_count": len(overlap_ids),
        "fullwidth_linebreak_overlap_ids_sha256": id_hash(overlap_ids),
        "manual_residual_fullwidth_overlap_count": 0,
        "composition_order": "current_steam_jp -> fullwidth_ascii_hash_gated -> CRLF_CR_LF_to_ascii_space",
        "fullwidth_applied_once_before_linebreak": True,
        "raw_parse_rebuild_valid": rebuild_message_table(candidate_table, candidate_table.texts) == candidate_raw,
        "packed": spec(candidate),
        "raw": spec(candidate_raw),
    }


def g1n_spec(entry_data: bytes, label: str) -> tuple[dict[str, Any], bytes]:
    _header, raw = decompress_wrapper(entry_data)
    if raw[:8] != b"_N1G0000":
        raise RebaseError(f"{label} is not a G1N wrapper")
    return spec(raw), raw


def rebase_one_font(
    steam_root: Path,
    resource: str,
    external: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    """Graft only approved outer G1Ns into the live resource, preserving gaps."""

    source_path = safe_steam_path(steam_root, resource)
    source_blob = source_path.read_bytes()
    candidate_path = FONT_CANDIDATE_ROOT / Path(resource)
    candidate_blob = candidate_path.read_bytes()
    source_archive = parse_link(source_blob)
    candidate_archive = parse_link(candidate_blob)
    targets = tuple(FULLWIDTH.FONT_G1N_ROUTES[resource])
    expected_targets = external["font_targets"][resource]
    if max(targets, default=-1) >= len(source_archive.entries) or max(targets, default=-1) >= len(candidate_archive.entries):
        raise RebaseError(f"font target outer entry is absent: {resource}")

    replacements: dict[int, bytes] = {}
    target_report: list[dict[str, Any]] = []
    for outer in targets:
        source_entry = source_archive.entries[outer]
        candidate_entry = candidate_archive.entries[outer]
        source_g1n, _source_raw = g1n_spec(source_entry.data, f"{resource}/{outer} current")
        candidate_g1n, _candidate_raw = g1n_spec(candidate_entry.data, f"{resource}/{outer} candidate")
        expected = expected_targets[outer]
        require(source_g1n["sha256"], expected["preimage_g1n_sha256"], f"font current preimage G1N {resource}/{outer}")
        require(candidate_g1n["sha256"], expected["candidate_g1n_sha256"], f"font candidate G1N {resource}/{outer}")
        require(candidate_g1n["size"], expected["candidate_g1n_size"], f"font candidate G1N size {resource}/{outer}")
        source_header, _ = decompress_wrapper(source_entry.data)
        candidate_header, _ = decompress_wrapper(candidate_entry.data)
        require(source_header.prefix, candidate_header.prefix, f"font wrapper prefix {resource}/{outer}")
        replacements[outer] = candidate_entry.data
        target_report.append(
            {
                "outer_entry": outer,
                "current_g1n": source_g1n,
                "candidate_g1n": candidate_g1n,
                "wrapper_prefix_sha256": sha256(source_header.prefix),
                "current_gap_after": spec(source_entry.gap_after),
                "candidate_data_from_approved_font_outer_entry_only": True,
            }
        )

    result = rebuild_link(source_archive, replacements)
    rebuilt = parse_link(result)
    require(rebuilt.fixed_header, source_archive.fixed_header, f"font fixed header {resource}")
    require(rebuilt.pre_data_padding, source_archive.pre_data_padding, f"font pre-data padding {resource}")
    require(len(rebuilt.entries), len(source_archive.entries), f"font entry count {resource}")
    for index, source_entry in enumerate(source_archive.entries):
        result_entry = rebuilt.entries[index]
        if index in replacements:
            require(result_entry.data, replacements[index], f"font target replacement {resource}/{index}")
            require(result_entry.gap_after, source_entry.gap_after, f"font target gap preservation {resource}/{index}")
        else:
            require(result_entry.data, source_entry.data, f"font non-target payload preservation {resource}/{index}")
            require(result_entry.gap_after, source_entry.gap_after, f"font non-target gap preservation {resource}/{index}")

    special_report: list[dict[str, Any]] = []
    if resource == RES_JP:
        for outer in SPECIAL_RES_JP_ENTRIES:
            if outer >= len(source_archive.entries):
                raise RebaseError(f"protected RES_JP outer entry missing: /{outer}")
            source_entry = source_archive.entries[outer]
            result_entry = rebuilt.entries[outer]
            # This is verification only.  No candidate entry /3 or /24 is
            # selected or copied anywhere in this function.
            require(result_entry.data, source_entry.data, f"RES_JP /{outer} payload byte identity")
            require(result_entry.gap_after, source_entry.gap_after, f"RES_JP /{outer} gap byte identity")
            special_report.append(
                {
                    "outer_entry": outer,
                    "payload": spec(source_entry.data),
                    "gap_after": spec(source_entry.gap_after),
                    "byte_identical_to_current_base": True,
                    "replacement_source_used": False,
                }
            )

    return result, {
        "resource": resource,
        "source": spec(source_blob),
        "candidate": spec(result),
        "link_entry_count": len(source_archive.entries),
        "target_outer_entries": list(targets),
        "target_entries": target_report,
        "non_target_payloads_byte_identical_to_current_base": True,
        "non_target_gaps_byte_identical_to_current_base": True,
        "target_gaps_byte_identical_to_current_base": True,
        "res_jp_protected_entries": special_report,
        "res_jp_3_24_replacement_sources_used": False,
    }


def build_current_candidate(
    steam_root: Path, external: Mapping[str, Any]
) -> tuple[
    dict[str, bytes],
    dict[str, Any],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, Any],
]:
    """Return only current-base candidates plus hash-only reports."""

    text_payloads, documents, text_baseline = load_current_texts(steam_root)
    fullwidth_payloads, fullwidth_replacements, fullwidth_report = apply_fullwidth_to_current(
        text_payloads, documents, external["fullwidth_metadata"]
    )
    ev_candidate, linebreak_report = apply_linebreak_after_fullwidth(
        text_payloads[EV_RESOURCE],
        fullwidth_payloads[EV_RESOURCE],
        documents[EV_RESOURCE],
        fullwidth_replacements[EV_RESOURCE],
        external["linebreak_overlay"],
    )
    fullwidth_payloads[EV_RESOURCE] = ev_candidate

    text_report = {
        resource: {
            "source": text_baseline[resource],
            "candidate": unpack_spec(fullwidth_payloads[resource], resource),
            "fullwidth_coordinate_count": len(fullwidth_replacements[resource]),
        }
        for resource in TEXT_RESOURCES
    }
    font_baseline = current_font_baseline(steam_root)
    return fullwidth_payloads, linebreak_report, text_report, font_baseline, fullwidth_report


def make_contract(steam_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    external = load_external_inputs()
    text_payloads, linebreak_report, text_report, font_baseline, fullwidth_report = build_current_candidate(steam_root, external)

    font_reports: dict[str, dict[str, Any]] = {}
    expected_candidates: dict[str, dict[str, Any]] = {
        resource: text_report[resource]["candidate"] for resource in TEXT_RESOURCES
    }
    for resource in FONT_RESOURCES:
        font_candidate, report = rebase_one_font(steam_root, resource, external)
        font_reports[resource] = report
        expected_candidates[resource] = {"packed": spec(font_candidate)}
        del font_candidate

    baseline: dict[str, Any] = {}
    for resource in TEXT_RESOURCES:
        baseline[resource] = text_report[resource]["source"]
    baseline.update(font_baseline)
    contract: dict[str, Any] = {
        "schema": SCHEMA,
        "runtime": {"distribution": "Steam", "language_route": "JP", "pk_version": "1.1.7"},
        "safety": {
            "current_steam_jp_is_the_only_resource_baseline": True,
            "v09_full_text_archive_read": False,
            "v09_full_text_archive_used_as_replacement": False,
            "existing_nonlogo_composite_read": False,
            "existing_nonlogo_composite_applied": False,
            "res_jp_outer_3_or_24_used_as_replacement_source": False,
            "res_jp_outer_3_or_24_verified_byte_identical_only": True,
            "linebreak_manual_residual_translation_rebased": False,
            "logo_or_logo_like_images_touched": False,
            "installed_game_file_written": False,
            "release_written": False,
            "github_written": False,
            "source_text_free": True,
        },
        "baseline": {"resources": baseline},
        "inputs": external["pins"],
        "operations": {
            "fullwidth": fullwidth_report,
            "linebreak": linebreak_report,
            "font": font_reports,
        },
        "expected_candidates": expected_candidates,
        "candidate_resource_vector": list(TARGETS),
        "staging": {
            "ev_strdata": EV_RESOURCE,
            "res_lang": RES_JP,
            "transaction_ready": True,
            "private_tmp_output_only": True,
        },
    }
    validate_contract(contract)
    validation = validation_projection(contract)
    require_source_free(validation, "validation")
    return contract, validation


def validation_projection(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "runtime": contract["runtime"],
        "candidate_resource_vector": contract["candidate_resource_vector"],
        "baseline_resources": contract["baseline"]["resources"],
        "expected_candidates": contract["expected_candidates"],
        "operations": contract["operations"],
        "safety": contract["safety"],
    }


def validate_contract(contract: Mapping[str, Any]) -> None:
    require(contract.get("schema"), SCHEMA, "contract schema")
    require_source_free(contract, "contract")
    safety = contract.get("safety")
    if not isinstance(safety, dict):
        raise RebaseError("contract safety is absent")
    for key in (
        "current_steam_jp_is_the_only_resource_baseline",
        "v09_full_text_archive_read",
        "v09_full_text_archive_used_as_replacement",
        "existing_nonlogo_composite_read",
        "existing_nonlogo_composite_applied",
        "res_jp_outer_3_or_24_used_as_replacement_source",
        "res_jp_outer_3_or_24_verified_byte_identical_only",
        "linebreak_manual_residual_translation_rebased",
        "logo_or_logo_like_images_touched",
        "installed_game_file_written",
        "release_written",
        "github_written",
        "source_text_free",
    ):
        if key not in safety:
            raise RebaseError(f"contract safety flag is absent: {key}")
    for key in (
        "current_steam_jp_is_the_only_resource_baseline",
        "res_jp_outer_3_or_24_verified_byte_identical_only",
        "source_text_free",
    ):
        require_true(safety[key], f"contract safety {key}")
    for key in (
        "v09_full_text_archive_read",
        "v09_full_text_archive_used_as_replacement",
        "existing_nonlogo_composite_read",
        "existing_nonlogo_composite_applied",
        "res_jp_outer_3_or_24_used_as_replacement_source",
        "linebreak_manual_residual_translation_rebased",
        "logo_or_logo_like_images_touched",
        "installed_game_file_written",
        "release_written",
        "github_written",
    ):
        require(safety[key], False, f"contract safety {key}")
    require(contract.get("candidate_resource_vector"), list(TARGETS), "candidate resource vector")
    baseline = contract.get("baseline")
    if not isinstance(baseline, dict) or not isinstance(baseline.get("resources"), dict):
        raise RebaseError("baseline resource contract is absent")
    require(tuple(baseline["resources"]), TARGETS, "baseline resource vector")
    expected = contract.get("expected_candidates")
    if not isinstance(expected, dict):
        raise RebaseError("candidate contract is absent")
    require(tuple(expected), TARGETS, "candidate resource vector in contract")


def load_frozen_contract() -> tuple[dict[str, Any], dict[str, Any]]:
    contract = read_json(CONTRACT_PATH, "frozen current-state contract")
    validation = read_json(VALIDATION_PATH, "frozen validation")
    validate_contract(contract)
    require(validation, validation_projection(contract), "frozen validation projection")
    return contract, validation


def verify_live_baseline(steam_root: Path, contract: Mapping[str, Any]) -> None:
    resources = contract["baseline"]["resources"]
    for resource in TEXT_RESOURCES:
        payload = safe_steam_path(steam_root, resource).read_bytes()
        document = FULLWIDTH.parse_document(resource, payload)
        actual = {**unpack_spec(payload, resource), "text_coordinate_count": len(document.cells), "kind": document.kind}
        require(actual, resources[resource], f"frozen current text baseline {resource}")
    for resource in FONT_RESOURCES:
        actual = {"packed": file_spec(safe_steam_path(steam_root, resource))}
        require(actual, resources[resource], f"frozen current font baseline {resource}")


def verify_external_pins(contract: Mapping[str, Any], external: Mapping[str, Any]) -> None:
    require(external["pins"], contract.get("inputs"), "frozen input pins")


def assert_expected_text_candidates(
    payloads: Mapping[str, bytes], contract: Mapping[str, Any]
) -> None:
    expected = contract["expected_candidates"]
    for resource in TEXT_RESOURCES:
        require(unpack_spec(payloads[resource], resource), expected[resource], f"expected text candidate {resource}")


def build_fonts_against_contract(
    steam_root: Path, external: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    font_contract = contract["operations"]["font"]
    for resource in FONT_RESOURCES:
        candidate, report = rebase_one_font(steam_root, resource, external)
        require(report, font_contract[resource], f"frozen font rebase report {resource}")
        require({"packed": spec(candidate)}, contract["expected_candidates"][resource], f"expected font candidate {resource}")
        result[resource] = candidate
    return result


def compute_frozen_candidate(
    steam_root: Path, contract: Mapping[str, Any]
) -> tuple[dict[str, bytes], dict[str, bytes], dict[str, Any]]:
    external = load_external_inputs()
    verify_external_pins(contract, external)
    verify_live_baseline(steam_root, contract)
    text_payloads, linebreak_report, text_report, _font_baseline, fullwidth_report = build_current_candidate(steam_root, external)
    expected_operation = contract["operations"]
    require(fullwidth_report, expected_operation["fullwidth"], "frozen fullwidth operation report")
    require(linebreak_report, expected_operation["linebreak"], "frozen linebreak operation report")
    assert_expected_text_candidates(text_payloads, contract)
    font_payloads = build_fonts_against_contract(steam_root, external, contract)
    return text_payloads, font_payloads, {"linebreak": linebreak_report}


def source_specs_now(steam_root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for resource in TARGETS:
        result[resource] = file_spec(safe_steam_path(steam_root, resource))
    return result


def command_freeze(args: argparse.Namespace) -> int:
    contract, validation = make_contract(args.steam_root)
    atomic_write(CONTRACT_PATH, canonical_json(contract))
    atomic_write(VALIDATION_PATH, canonical_json(validation))
    print("status=PASS")
    print("baseline=current_steam_jp_only")
    print(f"fullwidth_applied={contract['operations']['fullwidth']['applied_coordinate_count']}")
    print(f"fullwidth_deferred={contract['operations']['fullwidth']['deferred_coordinate_count']}")
    print(f"linebreak_applied={contract['operations']['linebreak']['linebreak_applied_count']}")
    print("manual_linebreak_residual_rebased=False")
    print("steam_files_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    contract, _validation = load_frozen_contract()
    before = source_specs_now(args.steam_root)
    text_a, fonts_a, _report_a = compute_frozen_candidate(args.steam_root, contract)
    # ``freeze`` already independently produced the pinned font hashes.  One
    # fresh font rebuild compared to those hashes proves deterministic output
    # without keeping two 400+ MiB font candidate sets resident at once.  Text
    # resources are small enough to recompute twice in this invocation.
    external = load_external_inputs()
    text_b, linebreak_b, _text_report_b, _font_baseline_b, fullwidth_b = build_current_candidate(
        args.steam_root, external
    )
    require(fullwidth_b, contract["operations"]["fullwidth"], "second fullwidth report")
    require(linebreak_b, contract["operations"]["linebreak"], "second linebreak report")
    assert_expected_text_candidates(text_b, contract)
    for resource in TEXT_RESOURCES:
        require(text_a[resource], text_b[resource], f"deterministic text candidate {resource}")
    for resource in FONT_RESOURCES:
        require(
            {"packed": spec(fonts_a[resource])},
            contract["expected_candidates"][resource],
            f"deterministic font candidate {resource}",
        )
    after = source_specs_now(args.steam_root)
    require(after, before, "Steam source unchanged after verification")
    print("status=PASS")
    print("deterministic=True")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    contract, _validation = load_frozen_contract()
    before = source_specs_now(args.steam_root)
    text_payloads, font_payloads, report = compute_frozen_candidate(args.steam_root, contract)
    output_root = safe_tmp_root(args.output_root)
    for resource in TEXT_RESOURCES:
        atomic_write(output_root / Path(resource), text_payloads[resource])
    for resource in FONT_RESOURCES:
        atomic_write(output_root / Path(resource), font_payloads[resource])
    manifest = {
        "schema": BUILD_MANIFEST_SCHEMA,
        "contract_sha256": sha256(CONTRACT_PATH.read_bytes()),
        "candidate_resource_vector": list(TARGETS),
        "expected_candidates": contract["expected_candidates"],
        "linebreak": report["linebreak"],
        "safety": {
            "private_tmp_output_only": True,
            "installed_game_file_written": False,
            "release_written": False,
            "github_written": False,
            "logo_or_logo_like_images_touched": False,
        },
    }
    require_source_free(manifest, "private build manifest")
    atomic_write(output_root / "build_manifest.v1.json", canonical_json(manifest))
    for resource in TARGETS:
        actual = file_spec(output_root / Path(resource))
        expected = contract["expected_candidates"][resource]["packed"]
        require(actual, expected, f"written private staging file {resource}")
    after = source_specs_now(args.steam_root)
    require(after, before, "Steam source unchanged after build")
    print("status=PASS")
    print(f"output_root={output_root}")
    print("steam_files_written=False")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("freeze", "verify", "build"):
        command = commands.add_parser(name)
        command.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
        if name == "build":
            command.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "freeze":
            return command_freeze(args)
        if args.command == "verify":
            return command_verify(args)
        return command_build(args)
    except (RebaseError, OSError, ValueError, FULLWIDTH.NormalizationError, LINEBREAK.LinebreakError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
