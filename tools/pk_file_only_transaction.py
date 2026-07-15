#!/usr/bin/env python3
"""Fail-closed local transaction helper for PK Korean-patch candidates.

This helper intentionally does *not* build a public release archive.  It is
for a locally generated, already verified candidate set: it records the exact
installed predecessor hashes, verifies the candidate hashes, and can then
apply or restore the files as one small transaction.  The manifest contains
only paths, sizes, and hashes--never candidate bytes or absolute local paths.

Only the exact Simplified-Chinese or Japanese PC PK runtime paths enumerated
in ``ALLOWED_TARGETS`` are accepted.  A transaction is always confined to one
runtime-language profile.  The base-game tree remains blocked except for that
profile's shared ``MSG/<LANG>/strdata.bin`` and base font archive.  Japanese
transactions support both the legacy exact ten-file profile and the exact
twelve-file profile that adds the two JP PK port font archives.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterator


SC_MESSAGE_FILES = (
    "msgui.bin",
    "msgev.bin",
    "msgdata.bin",
    "msgbre.bin",
    "msgire.bin",
    "msgstf.bin",
    "msggame.bin",
)
JP_MESSAGE_FILES = SC_MESSAGE_FILES
SC_ALLOWED_TARGETS = frozenset(
    {f"MSG_PK/SC/{name}" for name in SC_MESSAGE_FILES}
    | {"MSG/SC/strdata.bin", "RES_SC/res_lang.bin", "RES_SC/res_lang_exp.bin"}
)
JP_LEGACY_ALLOWED_TARGETS = frozenset(
    {f"MSG_PK/JP/{name}" for name in JP_MESSAGE_FILES}
    | {
        "MSG/JP/strdata.bin",
        "RES_JP/res_lang.bin",
        "RES_JP_PK/res_lang_pk.bin",
    }
)
JP_PORT_FONT_TARGETS = frozenset(
    {
        "RES_JP_PK_PORT/res_lang_pk_port1.bin",
        "RES_JP_PK_PORT/res_lang_pk_port2.bin",
    }
)
JP_ALLOWED_TARGETS = JP_LEGACY_ALLOWED_TARGETS | JP_PORT_FONT_TARGETS
ALLOWED_TARGETS = SC_ALLOWED_TARGETS | JP_ALLOWED_TARGETS
LEGACY_TARGET_SCOPE = ["MSG_PK/SC", "RES_SC"]
TARGET_SCOPE = ["MSG/SC/strdata.bin", "MSG_PK/SC", "RES_SC"]
JP_TARGET_SCOPE = ["MSG/JP/strdata.bin", "MSG_PK/JP", "RES_JP", "RES_JP_PK"]
JP_PORT_TARGET_SCOPE = [
    "MSG/JP/strdata.bin",
    "MSG_PK/JP",
    "RES_JP",
    "RES_JP_PK",
    "RES_JP_PK_PORT",
]
LIVE_RESOURCE_ROOTS = (
    ("MSG", "SC"),
    ("MSG_PK", "SC"),
    ("RES_SC",),
    ("MSG", "JP"),
    ("MSG_PK", "JP"),
    ("RES_JP",),
    ("RES_JP_PK",),
    ("RES_JP_PK_PORT",),
)
MANIFEST_SCHEMA = "nobu16.pk-file-only-transaction.v1"
STATE_SCHEMA = "nobu16.pk-file-only-transaction-state.v1"
SHA256_RE = re.compile(r"\A[0-9A-F]{64}\Z")
RELEASE_ID_RE = re.compile(r"\A[a-z0-9][a-z0-9._-]{0,79}\Z")


class TransactionError(RuntimeError):
    """A safety gate rejected an operation before a resource is replaced."""


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, object]:
    assert_ordinary_file(path, "file")
    return {"size": path.stat().st_size, "sha256": sha256_path(path)}


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    normalized: set[str] = set()
    for key, value in pairs:
        if not isinstance(key, str):
            raise TransactionError("JSON object key is not a string")
        folded = key.casefold()
        if folded in normalized:
            raise TransactionError(f"duplicate or case-colliding JSON key: {key!r}")
        normalized.add(folded)
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise TransactionError(f"invalid JSON numeric constant: {value}")


def read_strict_json(path: Path) -> dict[str, Any]:
    assert_ordinary_file(path, "JSON manifest")
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            value = json.load(
                stream,
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_json_constant,
            )
    except TransactionError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TransactionError(f"cannot read strict UTF-8 JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TransactionError(f"JSON root must be an object: {path}")
    return value


def safe_relative_path(value: str) -> str:
    if not isinstance(value, str):
        raise TransactionError("manifest path must be a string")
    pure = PurePosixPath(value.replace("\\", "/"))
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise TransactionError(f"unsafe relative path: {value!r}")
    for part in pure.parts:
        if ":" in part or part.endswith((" ", ".")):
            raise TransactionError(f"unsafe Windows path segment: {value!r}")
    return "/".join(pure.parts)


def is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = path.stat(follow_symlinks=False).st_file_attributes
    except (AttributeError, FileNotFoundError):
        return False
    return bool(attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT


def assert_ordinary_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise TransactionError(f"{label} is missing or not a regular file: {path}")
    if is_reparse_point(path):
        raise TransactionError(f"{label} must not be a symlink/reparse point: {path}")


def assert_ordinary_directory(path: Path, label: str, *, must_exist: bool = True) -> None:
    if must_exist and not path.is_dir():
        raise TransactionError(f"{label} is missing or not a directory: {path}")
    if path.exists() and is_reparse_point(path):
        raise TransactionError(f"{label} must not be a symlink/reparse point: {path}")


def assert_no_links_between(root: Path, leaf: Path, label: str) -> None:
    root = root.resolve(strict=True)
    try:
        relative = leaf.relative_to(root)
    except ValueError as exc:
        raise TransactionError(f"{label} escapes expected root: {leaf}") from exc
    current = root
    if is_reparse_point(current):
        raise TransactionError(f"{label} root is a symlink/reparse point: {current}")
    for part in relative.parts:
        current /= part
        if is_reparse_point(current):
            raise TransactionError(f"{label} path contains a symlink/reparse point: {current}")


def lexical_absolute(path: Path) -> Path:
    """Return an absolute path without resolving symlinks or reparse points."""
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def assert_no_reparse_components(path: Path, label: str) -> Path:
    """Reject every existing link/reparse component before canonical resolution."""
    absolute = lexical_absolute(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if is_reparse_point(current):
            raise TransactionError(
                f"{label} path contains a symlink/reparse point: {current}"
            )
    return absolute


def resolve_under(root: Path, relative: str, label: str, *, root_must_exist: bool = True) -> Path:
    relative = safe_relative_path(relative)
    root = root.resolve(strict=root_must_exist)
    target = root.joinpath(*PurePosixPath(relative).parts)
    try:
        target.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise TransactionError(f"{label} escapes its root: {relative}") from exc
    return target


def validate_spec(value: Any, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"size", "sha256"}:
        raise TransactionError(f"{label} must contain exactly size and sha256")
    size = value["size"]
    digest = value["sha256"]
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise TransactionError(f"{label}.size must be a positive integer")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise TransactionError(f"{label}.sha256 must be uppercase SHA-256")
    return {"size": size, "sha256": digest}


def runtime_profile_for_paths(paths: set[str] | frozenset[str], label: str) -> str:
    """Infer exactly one supported runtime-language profile from target paths."""
    if not paths:
        raise TransactionError(f"{label} must contain at least one target path")
    unknown = paths - ALLOWED_TARGETS
    if unknown:
        raise TransactionError(f"{label} contains a target outside PK scope: {sorted(unknown)[0]}")
    profiles: set[str] = set()
    if paths & SC_ALLOWED_TARGETS:
        profiles.add("SC")
    if paths & JP_ALLOWED_TARGETS:
        profiles.add("JP")
    if len(profiles) != 1:
        raise TransactionError(f"{label} must not mix SC and JP runtime profiles")
    profile = profiles.pop()
    if profile == "JP" and paths not in (
        JP_LEGACY_ALLOWED_TARGETS,
        JP_ALLOWED_TARGETS,
    ):
        expected = (
            JP_ALLOWED_TARGETS
            if paths & JP_PORT_FONT_TARGETS
            else JP_LEGACY_ALLOWED_TARGETS
        )
        missing = sorted(expected - paths)
        raise TransactionError(
            f"{label} must contain the exact JP 10-file profile or exact "
            "JP+JP_PK_PORT 12-file profile"
            + (f" (missing={','.join(missing)})" if missing else "")
        )
    return profile


def runtime_profile_for_scope(target_scope: Any) -> str:
    if target_scope in (LEGACY_TARGET_SCOPE, TARGET_SCOPE):
        return "SC"
    if target_scope in (JP_TARGET_SCOPE, JP_PORT_TARGET_SCOPE):
        return "JP"
    raise TransactionError(
        "manifest target_scope must be the legacy SC scope, exact SC scope, "
        "exact JP 10-file scope, or exact JP+JP_PK_PORT 12-file scope"
    )


def assert_matches_spec(path: Path, spec: dict[str, object], label: str) -> None:
    assert_ordinary_file(path, label)
    actual_size = path.stat().st_size
    expected_size = int(spec["size"])
    if actual_size != expected_size:
        raise TransactionError(f"{label} size mismatch: {actual_size}, expected {expected_size}")
    actual_hash = sha256_path(path)
    expected_hash = str(spec["sha256"])
    if actual_hash != expected_hash:
        raise TransactionError(f"{label} SHA-256 mismatch: {actual_hash}, expected {expected_hash}")


def parse_candidate_args(values: list[str] | None) -> dict[str, Path]:
    candidates: dict[str, Path] = {}
    for value in values or []:
        if value.count("=") != 1:
            raise TransactionError("--candidate must be TARGET=LOCAL_CANDIDATE_FILE")
        target, local = value.split("=", 1)
        target = safe_relative_path(target)
        if target not in ALLOWED_TARGETS:
            raise TransactionError(f"candidate target is outside PK scope: {target}")
        if not local:
            raise TransactionError(f"candidate path is empty for {target}")
        if target in candidates:
            raise TransactionError(f"duplicate candidate target: {target}")
        candidates[target] = assert_no_reparse_components(
            Path(local), f"candidate {target}"
        )
    if not candidates:
        raise TransactionError("at least one --candidate is required")
    runtime_profile_for_paths(set(candidates), "candidate set")
    return candidates


def collect_candidate_root(root: Path) -> dict[str, Path]:
    """Collect only known PK targets from a local composite output tree."""
    root = assert_no_reparse_components(root, "candidate root")
    assert_ordinary_directory(root, "candidate root")
    root = root.resolve(strict=True)
    candidates: dict[str, Path] = {}
    for relative in sorted(ALLOWED_TARGETS):
        candidate = resolve_under(root, relative, f"candidate-root {relative}")
        if not candidate.exists():
            continue
        assert_no_links_between(root, candidate, f"candidate-root {relative}")
        assert_ordinary_file(candidate, f"candidate-root {relative}")
        candidates[relative] = candidate
    if not candidates:
        raise TransactionError("candidate root contains no accepted PK target files")
    profile = runtime_profile_for_paths(set(candidates), "candidate root")
    if profile == "JP":
        extras: list[str] = []
        for current, directory_names, file_names in os.walk(
            root, topdown=True, followlinks=False
        ):
            current_path = Path(current)
            for directory_name in directory_names:
                child = current_path / directory_name
                if is_reparse_point(child):
                    raise TransactionError(
                        "JP candidate root contains a symlink/reparse point: "
                        + str(child)
                    )
            for file_name in file_names:
                child = current_path / file_name
                if is_reparse_point(child):
                    raise TransactionError(
                        "JP candidate root contains a symlink/reparse point: "
                        + str(child)
                    )
                relative = child.relative_to(root).as_posix()
                if relative not in JP_ALLOWED_TARGETS:
                    extras.append(relative)
        if extras:
            raise TransactionError(
                "JP candidate root contains an unexpected file: " + sorted(extras)[0]
            )
    return candidates


def candidates_from_namespace(args: argparse.Namespace) -> dict[str, Path]:
    candidate_root = getattr(args, "candidate_root", None)
    direct = getattr(args, "candidate", None)
    if candidate_root is not None:
        if direct:
            raise TransactionError("use either --candidate or --candidate-root, not both")
        return collect_candidate_root(candidate_root)
    return parse_candidate_args(direct)


def candidate_must_not_be_live_resource(game_root: Path, candidate: Path, label: str) -> None:
    candidate = assert_no_reparse_components(candidate, label)
    assert_ordinary_file(candidate, label)
    game_root = game_root.resolve(strict=True)
    resolved = candidate.resolve(strict=True)
    for parts in LIVE_RESOURCE_ROOTS:
        scoped_root = game_root.joinpath(*parts)
        try:
            resolved.relative_to(scoped_root.resolve(strict=False))
        except ValueError:
            continue
        raise TransactionError(f"{label} must not point into a live PK resource tree: {candidate}")


def validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    expected_keys = {
        "schema",
        "release_id",
        "file_only",
        "process_memory_access",
        "dll_injection",
        "hooking",
        "executable_modified",
        "registry_modified",
        "target_scope",
        "entries",
    }
    if set(value) != expected_keys:
        raise TransactionError("manifest has an unexpected or missing top-level field")
    if value["schema"] != MANIFEST_SCHEMA:
        raise TransactionError("unsupported transaction manifest schema")
    release_id = value["release_id"]
    if not isinstance(release_id, str) or not RELEASE_ID_RE.fullmatch(release_id):
        raise TransactionError("release_id must be lowercase ASCII [a-z0-9._-]")
    for name in (
        "file_only",
        "process_memory_access",
        "dll_injection",
        "hooking",
        "executable_modified",
        "registry_modified",
    ):
        expected = name == "file_only"
        if value[name] is not expected:
            raise TransactionError(f"manifest {name} must be {expected!r}")
    target_scope = value["target_scope"]
    scope_profile = runtime_profile_for_scope(target_scope)
    raw_entries = value["entries"]
    if not isinstance(raw_entries, list) or not raw_entries:
        raise TransactionError("manifest entries must be a non-empty array")
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_entries):
        if not isinstance(raw, dict) or set(raw) != {"path", "mode", "predecessor", "target"}:
            raise TransactionError(f"manifest entry {index} has an unexpected field")
        path = safe_relative_path(raw["path"])
        if path not in ALLOWED_TARGETS:
            raise TransactionError(f"manifest entry {index} is outside PK scope: {path}")
        folded = path.casefold()
        if folded in seen:
            raise TransactionError(f"manifest has duplicate target path: {path}")
        seen.add(folded)
        predecessor = validate_spec(raw["predecessor"], f"entry {path} predecessor")
        target = validate_spec(raw["target"], f"entry {path} target")
        mode = raw["mode"]
        if mode not in {"replace", "retain"}:
            raise TransactionError(f"entry {path} mode must be replace or retain")
        if mode == "replace" and predecessor == target:
            raise TransactionError(f"replace entry {path} target cannot equal predecessor")
        if mode == "retain" and predecessor != target:
            raise TransactionError(f"retain entry {path} must pin an identical predecessor and target")
        entries.append({"path": path, "mode": mode, "predecessor": predecessor, "target": target})
    if not any(entry["mode"] == "replace" for entry in entries):
        raise TransactionError(
            "candidate set is already installed; refusing an all-retain no-op transaction"
        )
    entry_paths = {entry["path"] for entry in entries}
    entry_profile = runtime_profile_for_paths(entry_paths, "manifest entries")
    if entry_profile != scope_profile:
        raise TransactionError("manifest target_scope and entries must use the same runtime profile")
    if target_scope == JP_TARGET_SCOPE and entry_paths != JP_LEGACY_ALLOWED_TARGETS:
        raise TransactionError(
            "manifest JP 10-file target_scope requires the exact legacy JP 10-file profile"
        )
    if target_scope == JP_PORT_TARGET_SCOPE and entry_paths != JP_ALLOWED_TARGETS:
        raise TransactionError(
            "manifest JP+JP_PK_PORT target_scope requires the exact JP 12-file profile"
        )
    if target_scope == LEGACY_TARGET_SCOPE and not entry_paths <= (
        SC_ALLOWED_TARGETS - {"MSG/SC/strdata.bin"}
    ):
        raise TransactionError("legacy SC target_scope cannot contain shared MSG/SC/strdata.bin")
    entries.sort(key=lambda entry: entry["path"])
    return {**value, "entries": entries}


def read_manifest(path: Path) -> tuple[dict[str, Any], str]:
    raw = read_strict_json(path)
    manifest = validate_manifest(raw)
    return manifest, hashlib.sha256(canonical_json(manifest)).hexdigest().upper()


def scope_report(manifest: dict[str, Any]) -> dict[str, Any]:
    paths = [entry["path"] for entry in manifest["entries"]]
    path_set = set(paths)
    runtime_language = runtime_profile_for_paths(path_set, "manifest entries")
    if runtime_language != runtime_profile_for_scope(manifest["target_scope"]):
        raise TransactionError("manifest target_scope and entries must use the same runtime profile")
    sc_message_paths = [path for path in paths if path.startswith("MSG_PK/SC/")]
    sc_resource_paths = [path for path in paths if path.startswith("RES_SC/")]
    sc_base_paths = [path for path in paths if path == "MSG/SC/strdata.bin"]
    jp_message_paths = [path for path in paths if path.startswith("MSG_PK/JP/")]
    jp_base_resource_paths = [path for path in paths if path.startswith("RES_JP/")]
    jp_pk_resource_paths = [path for path in paths if path.startswith("RES_JP_PK/")]
    jp_pk_port_resource_paths = [
        path for path in paths if path.startswith("RES_JP_PK_PORT/")
    ]
    jp_base_paths = [path for path in paths if path == "MSG/JP/strdata.bin"]
    return {
        "target_paths": paths,
        "runtime_language": runtime_language,
        "msg_pk_sc_count": len(sc_message_paths),
        "res_sc_count": len(sc_resource_paths),
        "base_msg_sc_count": len(sc_base_paths),
        "all_seven_msg_pk_sc_included": set(sc_message_paths) == {
            f"MSG_PK/SC/{name}" for name in SC_MESSAGE_FILES
        },
        "msg_pk_jp_count": len(jp_message_paths),
        "res_jp_count": len(jp_base_resource_paths),
        "res_jp_pk_count": len(jp_pk_resource_paths),
        "res_jp_pk_port_count": len(jp_pk_port_resource_paths),
        "base_msg_jp_count": len(jp_base_paths),
        "all_seven_msg_pk_jp_included": set(jp_message_paths) == {
            f"MSG_PK/JP/{name}" for name in JP_MESSAGE_FILES
        },
        "jp_10_file_count": len(path_set & JP_LEGACY_ALLOWED_TARGETS),
        "jp_10_file_complete": path_set == JP_LEGACY_ALLOWED_TARGETS,
        "jp_12_file_count": len(path_set & JP_ALLOWED_TARGETS),
        "jp_12_file_complete": path_set == JP_ALLOWED_TARGETS,
    }


def make_manifest(game_root: Path, release_id: str, candidates: dict[str, Path]) -> dict[str, Any]:
    if not RELEASE_ID_RE.fullmatch(release_id):
        raise TransactionError("release_id must be lowercase ASCII [a-z0-9._-]")
    assert_ordinary_directory(game_root, "game root")
    root = game_root.resolve(strict=True)
    candidate_targets = {safe_relative_path(target) for target in candidates}
    candidate_profile = runtime_profile_for_paths(candidate_targets, "candidate set")
    entries: list[dict[str, Any]] = []
    for target, candidate in sorted(candidates.items()):
        target = safe_relative_path(target)
        if target not in ALLOWED_TARGETS:
            raise TransactionError(f"candidate target is outside PK scope: {target}")
        installed = resolve_under(root, target, f"installed {target}")
        assert_no_links_between(root, installed, f"installed {target}")
        assert_ordinary_file(installed, f"installed {target}")
        candidate_must_not_be_live_resource(root, candidate, f"candidate {target}")
        predecessor = file_spec(installed)
        target_spec = file_spec(candidate)
        mode = "retain" if predecessor == target_spec else "replace"
        entries.append({"path": target, "mode": mode, "predecessor": predecessor, "target": target_spec})
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "release_id": release_id,
        "file_only": True,
        "process_memory_access": False,
        "dll_injection": False,
        "hooking": False,
        "executable_modified": False,
        "registry_modified": False,
        "target_scope": (
            JP_PORT_TARGET_SCOPE
            if candidate_profile == "JP" and candidate_targets == JP_ALLOWED_TARGETS
            else JP_TARGET_SCOPE
            if candidate_profile == "JP"
            else TARGET_SCOPE
        ),
        "entries": entries,
    }
    return validate_manifest(manifest)


def write_atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    assert_ordinary_directory(path.parent, "JSON parent directory")
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    try:
        with temporary.open("xb") as stream:
            stream.write(canonical_json(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def default_backup_root(game_root: Path, release_id: str) -> Path:
    return game_root / "KR_PATCH_BACKUP" / "file_only_transaction" / release_id


def validate_backup_root(game_root: Path, backup_root: Path) -> Path:
    root = game_root.resolve(strict=True)
    backup = lexical_absolute(backup_root)
    for parts in LIVE_RESOURCE_ROOTS:
        forbidden = root.joinpath(*parts)
        try:
            backup.relative_to(forbidden)
        except ValueError:
            continue
        raise TransactionError("backup root must not be inside a PK resource tree")
    allowed_parent = root / "KR_PATCH_BACKUP"
    try:
        backup.relative_to(allowed_parent)
    except ValueError as exc:
        raise TransactionError("backup root must stay under <game-root>/KR_PATCH_BACKUP") from exc
    backup = assert_no_reparse_components(backup, "backup root").resolve(strict=False)
    try:
        backup.relative_to(allowed_parent)
    except ValueError as exc:
        raise TransactionError("backup root must stay under <game-root>/KR_PATCH_BACKUP") from exc
    if backup.exists():
        assert_ordinary_directory(backup, "backup root")
    return backup


def resource_paths(game_root: Path, manifest: dict[str, Any]) -> dict[str, Path]:
    root = game_root.resolve(strict=True)
    paths: dict[str, Path] = {}
    for entry in manifest["entries"]:
        path = resolve_under(root, entry["path"], f"installed {entry['path']}")
        assert_no_links_between(root, path, f"installed {entry['path']}")
        paths[entry["path"]] = path
    return paths


def installed_status(game_root: Path, manifest: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    paths = resource_paths(game_root, manifest)
    rows: list[dict[str, Any]] = []
    states: list[str] = []
    for entry in manifest["entries"]:
        relative = entry["path"]
        path = paths[relative]
        if not path.is_file() or is_reparse_point(path):
            state = "missing"
            actual: dict[str, object] | None = None
        else:
            actual = file_spec(path)
            if entry["mode"] == "retain" and actual == entry["predecessor"]:
                state = "retained"
            elif actual == entry["predecessor"]:
                state = "predecessor"
            elif actual == entry["target"]:
                state = "target"
            else:
                state = "unknown"
        states.append(state)
        rows.append({"path": relative, "state": state, "actual": actual})
    replace_states = [
        row["state"] for entry, row in zip(manifest["entries"], rows, strict=True)
        if entry["mode"] == "replace"
    ]
    distinct = set(replace_states)
    if not replace_states or distinct == {"predecessor"}:
        overall = "predecessor"
    elif distinct == {"target"}:
        overall = "target"
    elif "unknown" in distinct or "missing" in distinct:
        overall = "unsafe"
    else:
        overall = "mixed"
    return overall, rows


def candidate_status(
    game_root: Path, manifest: dict[str, Any], candidates: dict[str, Path]
) -> list[dict[str, Any]]:
    expected = {entry["path"]: entry["target"] for entry in manifest["entries"]}
    if set(candidates) != set(expected):
        missing = sorted(set(expected) - set(candidates))
        extra = sorted(set(candidates) - set(expected))
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("unexpected=" + ",".join(extra))
        raise TransactionError("candidate set must exactly match manifest entries (" + "; ".join(details) + ")")
    rows: list[dict[str, Any]] = []
    for relative, candidate in sorted(candidates.items()):
        candidate_must_not_be_live_resource(game_root, candidate, f"candidate {relative}")
        assert_matches_spec(candidate, expected[relative], f"candidate {relative}")
        rows.append({"path": relative, "candidate": str(candidate), "verified": True})
    return rows


def backup_path(backup_root: Path, relative: str) -> Path:
    path = resolve_under(
        backup_root,
        "originals/" + relative,
        f"backup {relative}",
        root_must_exist=False,
    )
    return assert_no_reparse_components(path, f"backup {relative}")


def state_path(backup_root: Path) -> Path:
    return backup_root / "transaction_state.json"


def lock_path(backup_root: Path) -> Path:
    return backup_root / "operation.lock"


@contextlib.contextmanager
def exclusive_lock(backup_root: Path) -> Iterator[None]:
    backup_root = assert_no_reparse_components(backup_root, "backup root")
    backup_root.mkdir(parents=True, exist_ok=True)
    assert_no_reparse_components(backup_root, "backup root")
    assert_ordinary_directory(backup_root, "backup root")
    lock = lock_path(backup_root)
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise TransactionError(f"operation lock already exists; do not override it: {lock}") from exc
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.fsync(descriptor)
        yield
    finally:
        os.close(descriptor)
        lock.unlink(missing_ok=True)


def copy_atomic(
    source: Path,
    destination: Path,
    expected: dict[str, object],
    label: str,
    *,
    before_replace: Callable[[], None] | None = None,
) -> None:
    assert_ordinary_file(source, label + " source")
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert_ordinary_directory(destination.parent, label + " parent")
    temporary = destination.parent / f".{destination.name}.n16kr.{uuid.uuid4().hex}.tmp"
    try:
        with source.open("rb") as incoming, temporary.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing, length=1024 * 1024)
            outgoing.flush()
            os.fsync(outgoing.fileno())
        assert_matches_spec(temporary, expected, label + " staging")
        if before_replace is not None:
            before_replace()
        os.replace(temporary, destination)
        assert_matches_spec(destination, expected, label + " replacement")
    finally:
        temporary.unlink(missing_ok=True)


def backup_all(game_root: Path, backup_root: Path, manifest: dict[str, Any]) -> None:
    paths = resource_paths(game_root, manifest)
    for entry in manifest["entries"]:
        relative = entry["path"]
        source = paths[relative]
        assert_matches_spec(source, entry["predecessor"], f"installed predecessor {relative}")
        backup = backup_path(backup_root, relative)
        if backup.exists():
            assert_matches_spec(backup, entry["predecessor"], f"existing backup {relative}")
        else:
            copy_atomic(source, backup, entry["predecessor"], f"backup {relative}")


def assert_backup_all(backup_root: Path, manifest: dict[str, Any]) -> None:
    for entry in manifest["entries"]:
        assert_matches_spec(
            backup_path(backup_root, entry["path"]),
            entry["predecessor"],
            f"backup {entry['path']}",
        )


def running_game_processes() -> list[str]:
    expected = {
        "nobu16.exe",
        "nobu16pk.exe",
        "nobu16pk_en.exe",
        "nobu16_launcher.exe",
    }
    if os.name == "nt":
        found: list[str] = []
        for image in sorted(expected):
            completed = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {image}", "/NH", "/FO", "CSV"],
                capture_output=True,
                text=True,
                check=False,
            )
            text = (completed.stdout or "").lower()
            if image in text:
                found.append(image)
        return found
    completed = subprocess.run(["ps", "-A", "-o", "comm="], capture_output=True, text=True, check=False)
    return sorted(
        line.strip()
        for line in completed.stdout.splitlines()
        if Path(line.strip()).name.lower() in expected
    )


def assert_game_stopped() -> None:
    running = running_game_processes()
    if running:
        raise TransactionError("close the game and official launcher before modifying files: " + ", ".join(running))


def dry_run(game_root: Path, backup_root: Path, manifest: dict[str, Any], candidates: dict[str, Path]) -> dict[str, Any]:
    candidates_report = candidate_status(game_root, manifest, candidates)
    status, installed = installed_status(game_root, manifest)
    backups: list[dict[str, Any]] = []
    for entry in manifest["entries"]:
        backup = backup_path(backup_root, entry["path"])
        if backup.exists():
            try:
                assert_matches_spec(backup, entry["predecessor"], f"backup {entry['path']}")
                backup_state = "valid"
            except TransactionError as exc:
                backup_state = "invalid: " + str(exc)
        else:
            backup_state = "absent"
        backups.append({"path": entry["path"], "state": backup_state})
    return {
        "schema": MANIFEST_SCHEMA,
        "action": "dry-run",
        "release_id": manifest["release_id"],
        "status": "PASS" if status in {"predecessor", "target"} else "FAIL",
        "installed_state": status,
        "would_apply": status == "predecessor",
        "would_restore": status == "target",
        "installed": installed,
        "candidates": candidates_report,
        "backups": backups,
        "scope": scope_report(manifest),
        "writes_performed": False,
    }


def make_state(
    manifest: dict[str, Any], manifest_hash: str, status: str, *, applied: list[str] | None = None
) -> dict[str, Any]:
    return {
        "schema": STATE_SCHEMA,
        "release_id": manifest["release_id"],
        "manifest_sha256": manifest_hash,
        "status": status,
        "paths": [entry["path"] for entry in manifest["entries"]],
        "applied_paths": sorted(applied or []),
    }


def assert_state(backup_root: Path, manifest: dict[str, Any], manifest_hash: str) -> dict[str, Any]:
    path = state_path(backup_root)
    value = read_strict_json(path)
    expected_keys = {"schema", "release_id", "manifest_sha256", "status", "paths", "applied_paths"}
    if set(value) != expected_keys:
        raise TransactionError("transaction state has an unexpected field")
    if (
        value["schema"] != STATE_SCHEMA
        or value["release_id"] != manifest["release_id"]
        or value["manifest_sha256"] != manifest_hash
        or value["paths"] != [entry["path"] for entry in manifest["entries"]]
        or not isinstance(value["applied_paths"], list)
        or any(item not in value["paths"] for item in value["applied_paths"])
        or value["status"] not in {"backup_complete", "applying", "applied", "restoring", "restored", "rollback_failed"}
    ):
        raise TransactionError("transaction state does not match this manifest")
    return value


def apply_transaction(
    game_root: Path,
    backup_root: Path,
    manifest: dict[str, Any],
    manifest_hash: str,
    candidates: dict[str, Path],
) -> dict[str, Any]:
    candidate_status(game_root, manifest, candidates)
    status, _ = installed_status(game_root, manifest)
    if status == "target":
        return {
            "schema": MANIFEST_SCHEMA,
            "action": "apply",
            "release_id": manifest["release_id"],
            "status": "PASS",
            "result": "already_target",
            "scope": scope_report(manifest),
            "writes_performed": False,
        }
    if status != "predecessor":
        raise TransactionError(f"apply requires a complete predecessor vector; found {status}")
    assert_game_stopped()
    with exclusive_lock(backup_root):
        status, _ = installed_status(game_root, manifest)
        if status != "predecessor":
            raise TransactionError("installed files changed after dry-run; apply aborted")
        backup_all(game_root, backup_root, manifest)
        write_atomic_json(state_path(backup_root), make_state(manifest, manifest_hash, "backup_complete"))
        changed: list[str] = []
        try:
            write_atomic_json(state_path(backup_root), make_state(manifest, manifest_hash, "applying", applied=changed))
            paths = resource_paths(game_root, manifest)
            for entry in manifest["entries"]:
                relative = entry["path"]
                if entry["mode"] == "retain":
                    continue
                # A user could launch the game after the initial gate while a
                # large font candidate is staging.  Recheck immediately
                # before every live-resource replacement.
                assert_game_stopped()
                assert_matches_spec(paths[relative], entry["predecessor"], f"pre-replace {relative}")
                copy_atomic(
                    candidates[relative],
                    paths[relative],
                    entry["target"],
                    f"apply {relative}",
                    before_replace=assert_game_stopped,
                )
                changed.append(relative)
                write_atomic_json(
                    state_path(backup_root),
                    make_state(manifest, manifest_hash, "applying", applied=changed),
                )
            final_status, _ = installed_status(game_root, manifest)
            if final_status != "target":
                raise TransactionError("apply did not reach the complete target vector")
            write_atomic_json(state_path(backup_root), make_state(manifest, manifest_hash, "applied", applied=changed))
        except Exception as original:
            rollback_errors: list[str] = []
            for entry in reversed(manifest["entries"]):
                relative = entry["path"]
                if entry["mode"] != "replace":
                    continue
                try:
                    path = resource_paths(game_root, manifest)[relative]
                    actual = file_spec(path)
                    if actual == entry["predecessor"]:
                        continue
                    if actual != entry["target"]:
                        raise TransactionError(
                            f"rollback source {relative} is neither predecessor nor target"
                        )
                    assert_game_stopped()
                    copy_atomic(
                        backup_path(backup_root, relative),
                        path,
                        entry["predecessor"],
                        f"rollback {relative}",
                        before_replace=assert_game_stopped,
                    )
                except Exception as rollback_error:  # preserve the primary cause too
                    rollback_errors.append(str(rollback_error))
            final_status, _ = installed_status(game_root, manifest)
            if rollback_errors or final_status != "predecessor":
                write_atomic_json(
                    state_path(backup_root),
                    make_state(manifest, manifest_hash, "rollback_failed", applied=changed),
                )
                raise TransactionError(
                    f"apply failed ({original}); rollback was not proven: " + " | ".join(rollback_errors)
                ) from original
            write_atomic_json(state_path(backup_root), make_state(manifest, manifest_hash, "restored"))
            raise TransactionError(f"apply failed and was rolled back: {original}") from original
    return {
        "schema": MANIFEST_SCHEMA,
        "action": "apply",
        "release_id": manifest["release_id"],
        "status": "PASS",
        "result": "applied",
        "scope": scope_report(manifest),
        "writes_performed": True,
    }


def restore_transaction(
    game_root: Path,
    backup_root: Path,
    manifest: dict[str, Any],
    manifest_hash: str,
) -> dict[str, Any]:
    assert_game_stopped()
    with exclusive_lock(backup_root):
        state = assert_state(backup_root, manifest, manifest_hash)
        if state["status"] == "rollback_failed":
            raise TransactionError("previous rollback failed; inspect backups before retrying")
        assert_backup_all(backup_root, manifest)
        status, rows = installed_status(game_root, manifest)
        if status == "unsafe":
            raise TransactionError("restore refuses an unknown or missing installed resource")
        if status == "predecessor":
            write_atomic_json(state_path(backup_root), make_state(manifest, manifest_hash, "restored"))
            return {
                "schema": MANIFEST_SCHEMA,
                "action": "restore",
                "release_id": manifest["release_id"],
                "status": "PASS",
                "result": "already_predecessor",
                "scope": scope_report(manifest),
                "writes_performed": False,
            }
        write_atomic_json(state_path(backup_root), make_state(manifest, manifest_hash, "restoring"))
        paths = resource_paths(game_root, manifest)
        changed: list[str] = []
        try:
            for entry, row in zip(manifest["entries"], rows, strict=True):
                relative = entry["path"]
                if entry["mode"] == "retain":
                    if row["state"] != "retained":
                        raise TransactionError(f"restore refuses changed retained resource: {relative}")
                    continue
                if row["state"] == "predecessor":
                    continue
                if row["state"] != "target":
                    raise TransactionError(f"restore refuses non-target resource: {relative}")
                assert_game_stopped()
                copy_atomic(
                    backup_path(backup_root, relative),
                    paths[relative],
                    entry["predecessor"],
                    f"restore {relative}",
                    before_replace=assert_game_stopped,
                )
                changed.append(relative)
            final_status, _ = installed_status(game_root, manifest)
            if final_status != "predecessor":
                raise TransactionError("restore did not reach the complete predecessor vector")
            write_atomic_json(state_path(backup_root), make_state(manifest, manifest_hash, "restored"))
        except Exception as exc:
            # A partial restore is safe to retry: every changed path is now the
            # verified predecessor, while untouched paths remain the target.
            write_atomic_json(
                state_path(backup_root),
                make_state(manifest, manifest_hash, "restoring", applied=changed),
            )
            raise TransactionError(f"restore failed; rerun only after inspecting the journal: {exc}") from exc
    return {
        "schema": MANIFEST_SCHEMA,
        "action": "restore",
        "release_id": manifest["release_id"],
        "status": "PASS",
        "result": "restored",
        "scope": scope_report(manifest),
        "writes_performed": bool(changed),
    }


def print_report(report: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="write a hash-only local transaction manifest")
    plan.add_argument("--game-root", type=Path, required=True)
    plan.add_argument("--release-id", required=True)
    plan.add_argument("--manifest", type=Path, required=True)
    plan_candidates = plan.add_mutually_exclusive_group(required=True)
    plan_candidates.add_argument("--candidate", action="append", metavar="TARGET=FILE")
    plan_candidates.add_argument("--candidate-root", type=Path)

    for command in ("dry-run", "apply"):
        action = subparsers.add_parser(command, help=f"{command} a local candidate transaction")
        action.add_argument("--game-root", type=Path, required=True)
        action.add_argument("--manifest", type=Path, required=True)
        action.add_argument("--backup-root", type=Path)
        action_candidates = action.add_mutually_exclusive_group(required=True)
        action_candidates.add_argument("--candidate", action="append", metavar="TARGET=FILE")
        action_candidates.add_argument("--candidate-root", type=Path)
        if command == "apply":
            action.add_argument("--confirm", choices=["APPLY"], help="required explicit write confirmation")

    restore = subparsers.add_parser("restore", help="restore the exact predecessor vector from verified backups")
    restore.add_argument("--game-root", type=Path, required=True)
    restore.add_argument("--manifest", type=Path, required=True)
    restore.add_argument("--backup-root", type=Path)
    restore.add_argument("--confirm", choices=["RESTORE"], help="required explicit write confirmation")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        game_root = args.game_root.expanduser().resolve(strict=True)
        assert_ordinary_directory(game_root, "game root")
        if args.command == "plan":
            candidates = candidates_from_namespace(args)
            manifest = make_manifest(game_root, args.release_id, candidates)
            destination = args.manifest.expanduser().resolve(strict=False)
            if destination.exists():
                raise TransactionError(f"refusing to overwrite existing manifest: {destination}")
            write_atomic_json(destination, manifest)
            print_report(
                {
                    "schema": MANIFEST_SCHEMA,
                    "action": "plan",
                    "release_id": manifest["release_id"],
                    "status": "PASS",
                    "manifest": str(destination),
                    "entries": manifest["entries"],
                    "scope": scope_report(manifest),
                    "writes_performed": False,
                }
            )
            return 0

        manifest, manifest_hash = read_manifest(args.manifest.expanduser().resolve(strict=True))
        backup_root = validate_backup_root(
            game_root,
            (args.backup_root if args.backup_root else default_backup_root(game_root, manifest["release_id"])),
        )
        if args.command == "dry-run":
            report = dry_run(game_root, backup_root, manifest, candidates_from_namespace(args))
            print_report(report)
            return 0 if report["status"] == "PASS" else 2
        if args.command == "apply":
            if args.confirm != "APPLY":
                raise TransactionError("apply requires --confirm APPLY")
            print_report(
                apply_transaction(
                    game_root,
                    backup_root,
                    manifest,
                    manifest_hash,
                    candidates_from_namespace(args),
                )
            )
            return 0
        if args.confirm != "RESTORE":
            raise TransactionError("restore requires --confirm RESTORE")
        print_report(restore_transaction(game_root, backup_root, manifest, manifest_hash))
        return 0
    except TransactionError as exc:
        print_report({"status": "FAIL", "error": str(exc), "writes_performed": False})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
