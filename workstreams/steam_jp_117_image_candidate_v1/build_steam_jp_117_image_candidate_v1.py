#!/usr/bin/env python3
"""Assemble the offline Steam JP 1.1.7 v0.10.0 title-image candidate.

The only payload change from the pinned v0.9.0 exact-fourteen package is
``RES_JP/res_lang.bin``.  Its replacement is the independently verified PC
title-image candidate with 108 rebuilt title slots.  This module intentionally
has no game-install, executable, launcher, rollback, or installation command:
all outputs are created below this repository's ``tmp/`` directory.

The v0.9 ZIP and its manifest are immutable inputs.  They are cross-checked
against each other before the title-image candidate is copied into an isolated
staging tree.  A pre/post read-only guard also hashes all fourteen game
resources plus both game executables whenever a CLI command is run with the
default Steam root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TMP_ROOT = REPO / "tmp"

DEFAULT_V09_INPUT_ROOT = (
    TMP_ROOT / "steam_jp_117_image_candidate_v1_inputs" / "v0.9.0"
)
DEFAULT_BASELINE_ZIP = (
    DEFAULT_V09_INPUT_ROOT / "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip"
)
DEFAULT_BASELINE_MANIFEST = DEFAULT_V09_INPUT_ROOT / "candidate_manifest.v6.json"
DEFAULT_TITLE_CANDIDATE = (
    TMP_ROOT
    / "steam_jp_title_images_v1"
    / "final"
    / "candidate"
    / "RES_JP"
    / "res_lang.bin"
)
DEFAULT_LIVE_GAME_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "steam_jp_117_image_candidate_v1"
DEFAULT_ZIP_NAME = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.0.zip"

SCHEMA = "nobu16.kr.steam-jp-1.1.7-image-candidate-manifest.v1"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-image-candidate-verification.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-image-candidate-validation.v1"
V09_MANIFEST_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-manifest.v6"
TITLE_VALIDATION_SCHEMA = "nobu16.kr.steam-jp-title-images.validation.v1"
VERIFICATION_PATH = WORKSTREAM / "verification.v1.json"
TITLE_VALIDATION_PATH = (
    REPO / "workstreams" / "steam_jp_title_images_v1" / "validation.v1.json"
)
TITLE_BUILDER_PATH = (
    REPO / "workstreams" / "steam_jp_title_images_v1" / "build_steam_jp_title_images_v1.py"
)

TARGETS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgui.bin",
    "RES_JP/res_lang.bin",
    "RES_JP_PK/res_lang_pk.bin",
    "RES_JP_PK_PORT/res_lang_pk_port1.bin",
    "RES_JP_PK_PORT/res_lang_pk_port2.bin",
)
REPLACED_RESOURCE = "RES_JP/res_lang.bin"
LIVE_GUARD_PATHS = (*TARGETS, "NOBU16.exe", "NOBU16PK.exe")
ZIP_FORBIDDEN_PREFIXES = ("exefs/", "romfs/", "switch/", "png/")

EXPECTED_RUNTIME = {
    "distribution": "Steam",
    "language_route": "JP",
    "pk_version": "1.1.7",
    "steam_build_id": 18823764,
}
V09_RELEASE_PIN = {
    "name": "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip",
    "size": 356_951_693,
    "sha256": "1BCC92A3CD7025D307AF9B193BDDD8F1448451024630C8414FC218F0C49FE829",
}
V09_MANIFEST_PIN = {
    "name": "candidate_manifest.v6.json",
    "size": 16_870,
    "sha256": "5D93C83B817E67408A9F8A160B8437E37DE4EF332AB7C76D69855D2F705A8F3B",
}
TITLE_VALIDATION_PIN = {
    "size": 2_413,
    "sha256": "F3968CFC7FEDD816251F301EB09BA70BDA99C7CD2FEA58C793FA1487D8CE7FB4",
}
TITLE_BUILDER_PIN = {
    "size": 33_365,
    "sha256": "DC5F2B43812822B5CE90A593949DF3114690115A4E9B38D4B9F14A799657FB52",
}
TITLE_BUILDER_SHA256 = TITLE_BUILDER_PIN["sha256"]
TITLE_SOURCE_FONT_BASELINE = {
    "size": 154_216_023,
    "sha256": "0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0",
}
TITLE_CANDIDATE_PIN = {
    "size": 160_351_447,
    "sha256": "D045B42BC3D4A4D4C501C5A0E010698AAE95AAE227775306A1272D5259E0888B",
}
STOCK_RES_LANG_PREDECESSOR = {
    "size": 153_198_542,
    "sha256": "D32898C186CBDC7534692269C062E888ACE3B7A58F5DB4FEC8B0C745DADAAE53",
}


class ImageCandidateError(RuntimeError):
    """Raised when a pinned input, scope, or safety invariant differs."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def blob_spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def path_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ImageCandidateError(f"missing required file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return {"size": path.stat().st_size, "sha256": digest.hexdigest().upper()}


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ImageCandidateError(
            f"{label} differs: expected={expected!r}, actual={actual!r}"
        )


def require_spec(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = path_spec(path)
    require_equal(actual, dict(expected), label)
    return actual


def _lexical_absolute(path: Path) -> Path:
    """Return an absolute path without accepting a reparse-point escape."""

    return Path(os.path.abspath(os.fspath(path)))


def _reparse_kind(path: Path) -> str | None:
    """Classify a link/reparse point without following it when possible.

    Windows directory junctions are not reported by ``Path.is_symlink()``.
    Test both the high-level junction API and the ``lstat`` reparse attribute so
    staging never treats a junction as an ordinary directory component.
    """

    try:
        if path.is_symlink():
            return "symlink"
        if path.is_junction():
            return "junction"
        info = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ImageCandidateError(f"cannot inspect path component: {path}") from exc
    if stat.S_ISLNK(info.st_mode):
        return "symlink"
    reparse_attribute = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    if getattr(info, "st_file_attributes", 0) & reparse_attribute:
        return "reparse point"
    return None


def _reject_reparse(path: Path, label: str) -> None:
    kind = _reparse_kind(path)
    if kind is not None:
        raise ImageCandidateError(f"{label} must not be a {kind}: {path}")


def _tmp_roots() -> tuple[Path, Path]:
    """Return lexical and resolved repository ``tmp`` roots after link checks."""

    lexical = _lexical_absolute(TMP_ROOT)
    _reject_reparse(lexical, "repository tmp root")
    if not lexical.is_dir():
        raise ImageCandidateError(f"repository tmp root is not a directory: {lexical}")
    try:
        resolved = lexical.resolve(strict=True)
    except OSError as exc:
        raise ImageCandidateError(f"cannot resolve repository tmp root: {lexical}") from exc
    return lexical, resolved


def assert_safe_tmp_path(
    path: Path,
    label: str,
    *,
    require_exists: bool = False,
) -> Path:
    """Reject every symlink/junction component and prove ``path`` stays in tmp.

    This check is deliberately invoked immediately before every staging/output
    mutation and cleanup.  It handles ordinary symlinks, Windows directory
    junctions, and other reparse points rather than relying on ``resolve()``
    alone, which would otherwise follow an escape before containment is tested.
    """

    tmp_lexical, tmp_resolved = _tmp_roots()
    lexical = _lexical_absolute(path)
    try:
        relative = lexical.relative_to(tmp_lexical)
    except ValueError as exc:
        raise ImageCandidateError(f"{label} must be below repository tmp: {lexical}") from exc
    if not relative.parts:
        raise ImageCandidateError(f"{label} must not be the repository tmp root")

    current = tmp_lexical
    for component in relative.parts:
        current = current / component
        _reject_reparse(current, f"{label} path component")

    try:
        resolved = lexical.resolve(strict=require_exists)
    except FileNotFoundError as exc:
        raise ImageCandidateError(f"{label} is missing: {lexical}") from exc
    except OSError as exc:
        raise ImageCandidateError(f"cannot resolve {label}: {lexical}") from exc
    if resolved == tmp_resolved or tmp_resolved not in resolved.parents:
        raise ImageCandidateError(f"{label} escapes repository tmp after resolve: {resolved}")
    return resolved


def ensure_safe_tmp_directory(path: Path, label: str) -> Path:
    """Create a tmp-relative directory one checked component at a time."""

    lexical_target = _lexical_absolute(path)
    tmp_lexical, _tmp_resolved = _tmp_roots()
    if lexical_target == tmp_lexical:
        return _tmp_resolved
    target = assert_safe_tmp_path(lexical_target, label)
    relative = lexical_target.relative_to(tmp_lexical)
    current = tmp_lexical
    for component in relative.parts:
        current = current / component
        assert_safe_tmp_path(current, f"{label} directory")
        if not current.exists():
            try:
                current.mkdir()
            except FileExistsError:
                # A concurrent creator is safe only if the post-check agrees.
                pass
        checked = assert_safe_tmp_path(
            current, f"{label} directory", require_exists=True
        )
        if not checked.is_dir():
            raise ImageCandidateError(f"{label} component is not a directory: {checked}")
    return assert_safe_tmp_path(target, label, require_exists=True)


def write_new_tmp_file(path: Path, payload: bytes, label: str) -> Path:
    """Create a fresh regular tmp file without truncating a raced-in target."""

    target = assert_safe_tmp_path(path, label)
    ensure_safe_tmp_directory(target.parent, f"{label} parent")
    # ``x`` refuses an existing file/link; this avoids ``wb`` truncating a
    # raced-in hard link or other unexpected target.
    try:
        with target.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise ImageCandidateError(f"unsafe pre-existing output path: {target}") from exc
    checked = assert_safe_tmp_path(target, label, require_exists=True)
    if not checked.is_file():
        raise ImageCandidateError(f"{label} did not become a regular file: {checked}")
    return checked


def _assert_tree_has_no_reparse_points(root: Path, label: str) -> Path:
    """Scan a cleanup tree without descending into links or junctions."""

    checked_root = assert_safe_tmp_path(root, label, require_exists=True)
    if not checked_root.is_dir():
        raise ImageCandidateError(f"{label} is not a directory: {checked_root}")
    pending = [checked_root]
    while pending:
        current = pending.pop()
        assert_safe_tmp_path(current, label, require_exists=True)
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    child = Path(entry.path)
                    _reject_reparse(child, f"{label} cleanup entry")
                    assert_safe_tmp_path(child, f"{label} cleanup entry", require_exists=True)
                    if entry.is_dir(follow_symlinks=False):
                        pending.append(child)
        except OSError as exc:
            raise ImageCandidateError(f"cannot scan {label} cleanup tree: {current}") from exc
    return checked_root


def safe_rmtree(path: Path, label: str, *, ignore_errors: bool = False) -> None:
    """Remove only a reparse-free, tmp-contained staging tree."""

    try:
        # Do not follow a missing/broken link just to decide it is absent.
        if not path.exists() and _reparse_kind(path) is None:
            return
        checked = _assert_tree_has_no_reparse_points(path, label)
        # Re-check immediately before the destructive cleanup call.
        _assert_tree_has_no_reparse_points(checked, label)
        shutil.rmtree(checked)
    except (ImageCandidateError, OSError):
        if ignore_errors:
            return
        raise


def safe_unlink_tmp_file(path: Path, label: str, *, ignore_errors: bool = False) -> None:
    """Unlink a verified regular tmp file without following a reparse point."""

    try:
        if not path.exists() and _reparse_kind(path) is None:
            return
        checked = assert_safe_tmp_path(path, label, require_exists=True)
        if not checked.is_file():
            raise ImageCandidateError(f"{label} is not a regular file: {checked}")
        # Re-check immediately before unlinking the temporary file.
        assert_safe_tmp_path(checked, label, require_exists=True)
        checked.unlink()
    except (ImageCandidateError, OSError):
        if ignore_errors:
            return
        raise


def require_safe_distinct_inputs(
    baseline_zip: Path, baseline_manifest: Path, title_candidate: Path
) -> tuple[Path, Path, Path]:
    """Resolve immutable inputs and reject aliases before any staging write.

    The pinned payload checks remain the authority for byte identity, while this
    guard prevents a caller from making a ZIP, manifest, or replacement path
    alias another input or a symlink.  The default v0.9 inputs intentionally
    live in the normal inherited-ACL ``tmp/.../inputs`` bucket rather than an
    owner-only candidate staging directory, so elevated verification can read
    the same pinned bytes.
    """

    raw_paths = (baseline_zip, baseline_manifest, title_candidate)
    labels = ("v0.9 ZIP", "v0.9 manifest", "title candidate")
    resolved: list[Path] = []
    for path, label in zip(raw_paths, labels, strict=True):
        if path.is_symlink():
            raise ImageCandidateError(f"{label} input must not be a symlink: {path}")
        try:
            value = path.resolve(strict=True)
        except OSError as exc:
            raise ImageCandidateError(f"cannot resolve {label} input: {path}") from exc
        if not value.is_file():
            raise ImageCandidateError(f"{label} input is not a file: {value}")
        resolved.append(value)
    if len(set(resolved)) != len(resolved):
        raise ImageCandidateError("v0.9 ZIP, manifest, and title inputs must be distinct")
    return resolved[0], resolved[1], resolved[2]


def load_canonical_json(
    path: Path, label: str, *, require_canonical: bool = True
) -> dict[str, Any]:
    try:
        blob = path.read_bytes()
        value = json.loads(blob.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ImageCandidateError(f"invalid {label} JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ImageCandidateError(f"{label} JSON root is not an object")
    if require_canonical and blob != canonical_json_bytes(value):
        raise ImageCandidateError(f"{label} JSON formatting is not canonical")
    return value


def require_target_mapping(value: Any, label: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(value, dict) or set(value) != set(TARGETS):
        raise ImageCandidateError(f"{label} target map differs from exact fourteen vector")
    result: dict[str, Mapping[str, Any]] = {}
    for relative in TARGETS:
        spec = value.get(relative)
        if not isinstance(spec, Mapping):
            raise ImageCandidateError(f"{label} has invalid pin for {relative}")
        size = spec.get("size")
        digest = spec.get("sha256")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ImageCandidateError(f"{label} has invalid size for {relative}")
        if not isinstance(digest, str) or len(digest) != 64 or digest != digest.upper():
            raise ImageCandidateError(f"{label} has invalid SHA-256 for {relative}")
        result[relative] = {"size": size, "sha256": digest}
    return result


def load_v09_manifest(manifest_path: Path) -> dict[str, Any]:
    if manifest_path.name != V09_MANIFEST_PIN["name"]:
        raise ImageCandidateError("v0.9 manifest filename differs")
    require_spec(
        manifest_path,
        {"size": V09_MANIFEST_PIN["size"], "sha256": V09_MANIFEST_PIN["sha256"]},
        "v0.9 manifest input pin",
    )
    manifest = load_canonical_json(manifest_path, "v0.9 manifest")
    require_equal(manifest.get("schema"), V09_MANIFEST_SCHEMA, "v0.9 manifest schema")
    require_equal(manifest.get("runtime"), EXPECTED_RUNTIME, "v0.9 runtime")
    require_equal(manifest.get("candidate_file_count"), len(TARGETS), "v0.9 file count")
    require_equal(manifest.get("candidate_paths"), list(TARGETS), "v0.9 target vector")
    candidates = require_target_mapping(manifest.get("candidates"), "v0.9 candidates")
    predecessors = require_target_mapping(manifest.get("predecessors"), "v0.9 predecessors")
    require_equal(
        manifest.get("zip"),
        {"member_count": len(TARGETS), **V09_RELEASE_PIN},
        "v0.9 release ZIP pin in manifest",
    )
    if candidates[REPLACED_RESOURCE] != TITLE_SOURCE_FONT_BASELINE:
        raise ImageCandidateError("v0.9 RES_JP predecessor candidate is not title-font baseline")
    if predecessors[REPLACED_RESOURCE] != STOCK_RES_LANG_PREDECESSOR:
        raise ImageCandidateError("v0.9 RES_JP stock predecessor contract differs")
    checks = manifest.get("checks")
    if not isinstance(checks, Mapping):
        raise ImageCandidateError("v0.9 checks are absent")
    for key in (
        "steam_1_1_7_predecessors_exact",
        "jp_route_exact",
        "exact_fourteen_files",
        "zip_payloads_equal_candidates",
        "memory_patch",
        "dll_injection",
        "hooking",
        "exe_or_registry_modified",
        "steam_files_written",
    ):
        expected = False if key in {
            "memory_patch",
            "dll_injection",
            "hooking",
            "exe_or_registry_modified",
            "steam_files_written",
        } else True
        require_equal(checks.get(key), expected, f"v0.9 check {key}")
    return {
        **manifest,
        "candidates": {key: dict(value) for key, value in candidates.items()},
        "predecessors": {key: dict(value) for key, value in predecessors.items()},
    }


def assert_exact_zip_members(names: list[str], label: str) -> None:
    if names != list(TARGETS):
        raise ImageCandidateError(f"{label} member vector is not exact fourteen-file JP order")
    if len(names) != len(set(names)):
        raise ImageCandidateError(f"{label} has duplicate members")
    if any(
        name.casefold().startswith(prefix)
        for name in names
        for prefix in ZIP_FORBIDDEN_PREFIXES
    ):
        raise ImageCandidateError(f"{label} contains a forbidden platform/image member")


def validate_v09_zip(baseline_zip: Path, manifest: Mapping[str, Any]) -> None:
    if baseline_zip.name != V09_RELEASE_PIN["name"]:
        raise ImageCandidateError("v0.9 baseline ZIP filename differs")
    require_spec(
        baseline_zip,
        {"size": V09_RELEASE_PIN["size"], "sha256": V09_RELEASE_PIN["sha256"]},
        "v0.9 baseline ZIP input pin",
    )
    try:
        with zipfile.ZipFile(baseline_zip, "r") as archive:
            names = archive.namelist()
            assert_exact_zip_members(names, "v0.9 baseline ZIP")
            for relative in TARGETS:
                info = archive.getinfo(relative)
                if info.flag_bits & 0x1:
                    raise ImageCandidateError(f"v0.9 baseline ZIP member is encrypted: {relative}")
                require_equal(
                    blob_spec(archive.read(relative)),
                    manifest["candidates"][relative],
                    f"v0.9 ZIP payload pin {relative}",
                )
    except zipfile.BadZipFile as exc:
        raise ImageCandidateError("v0.9 baseline ZIP is invalid") from exc


def load_title_validation() -> dict[str, Any]:
    require_spec(TITLE_VALIDATION_PATH, TITLE_VALIDATION_PIN, "title validation pin")
    require_spec(TITLE_BUILDER_PATH, TITLE_BUILDER_PIN, "title builder source pin")
    validation = load_canonical_json(
        TITLE_VALIDATION_PATH, "title validation", require_canonical=False
    )
    require_equal(
        validation.get("schema"), TITLE_VALIDATION_SCHEMA, "title validation schema"
    )
    for key in ("source_free", "file_only"):
        require_equal(validation.get(key), True, f"title validation {key}")
    require_equal(
        validation.get("game_install_modified"), False, "title validation game write"
    )
    target = validation.get("target")
    if not isinstance(target, Mapping):
        raise ImageCandidateError("title validation target is absent")
    require_equal(target.get("resource"), REPLACED_RESOURCE, "title validation target")
    slots = target.get("title_slots")
    if not isinstance(slots, Mapping):
        raise ImageCandidateError("title validation slot range is absent")
    require_equal(slots.get("first"), 0, "title slot range first")
    require_equal(slots.get("last"), 107, "title slot range last")
    require_equal(slots.get("count"), 108, "title slot count")
    pins = validation.get("pins")
    if not isinstance(pins, Mapping):
        raise ImageCandidateError("title validation pins are absent")
    require_equal(
        pins.get("steam_jp_font_baseline"),
        TITLE_SOURCE_FONT_BASELINE,
        "title font baseline pin",
    )
    require_equal(
        pins.get("steam_jp_title_candidate"),
        TITLE_CANDIDATE_PIN,
        "title candidate pin",
    )
    candidate_check = validation.get("candidate_verification")
    if not isinstance(candidate_check, Mapping):
        raise ImageCandidateError("title validation candidate checks are absent")
    for key in (
        "unrelated_outer_entries_byte_preserved",
        "tail_slots_108_109_byte_preserved",
        "title_slot_pc_g1t_contract_verified",
        "outer_parse_valid",
        "inner_parse_valid",
    ):
        require_equal(candidate_check.get(key), True, f"title validation {key}")
    return validation


def validate_title_candidate(title_candidate: Path) -> dict[str, Any]:
    load_title_validation()
    return require_spec(title_candidate, TITLE_CANDIDATE_PIN, "title-image candidate")


def candidate_paths(candidate_root: Path) -> list[str]:
    _reject_reparse(candidate_root, "candidate root")
    if not candidate_root.is_dir():
        raise ImageCandidateError(f"candidate root is missing: {candidate_root}")
    result: list[str] = []
    for path in candidate_root.rglob("*"):
        _reject_reparse(path, "candidate tree entry")
        if path.is_file():
            result.append(path.relative_to(candidate_root).as_posix())
    result.sort()
    assert_exact_zip_members(result, "candidate tree")
    return result


def candidate_specs(candidate_root: Path) -> dict[str, dict[str, Any]]:
    candidate_paths(candidate_root)
    return {relative: path_spec(candidate_root / Path(relative)) for relative in TARGETS}


def materialize_v09_baseline(
    baseline_zip: Path, staging: Path, manifest: Mapping[str, Any]
) -> Path:
    validate_v09_zip(baseline_zip, manifest)
    staging = ensure_safe_tmp_directory(staging, "staging root")
    candidate_root = assert_safe_tmp_path(staging / "candidate", "candidate root")
    try:
        candidate_root.mkdir()
    except FileExistsError as exc:
        raise ImageCandidateError(f"unsafe pre-existing candidate root: {candidate_root}") from exc
    candidate_root = ensure_safe_tmp_directory(candidate_root, "candidate root")
    with zipfile.ZipFile(baseline_zip, "r") as archive:
        for relative in TARGETS:
            destination = assert_safe_tmp_path(
                candidate_root / Path(relative), f"candidate target {relative}"
            )
            ensure_safe_tmp_directory(
                destination.parent, f"candidate target parent {relative}"
            )
            payload = archive.read(relative)
            destination = write_new_tmp_file(
                destination, payload, f"candidate target {relative}"
            )
            require_equal(
                path_spec(destination),
                manifest["candidates"][relative],
                f"materialized v0.9 payload pin {relative}",
            )
    candidate_paths(candidate_root)
    return candidate_root


def replace_title_resource(candidate_root: Path, title_payload: Path) -> None:
    candidate_root = ensure_safe_tmp_directory(candidate_root, "candidate root")
    destination = assert_safe_tmp_path(
        candidate_root / Path(REPLACED_RESOURCE), "title resource destination", require_exists=True
    )
    if not destination.is_file():
        raise ImageCandidateError("v0.9 title resource is missing from candidate tree")
    replacement = title_payload.read_bytes()
    temporary = destination.with_name(destination.name + ".image-v1.tmp")
    temporary = write_new_tmp_file(temporary, replacement, "title resource temporary")
    try:
        require_equal(
            path_spec(temporary), TITLE_CANDIDATE_PIN, "temporary title candidate pin"
        )
        assert_safe_tmp_path(temporary, "title resource temporary", require_exists=True)
        assert_safe_tmp_path(destination, "title resource destination", require_exists=True)
        os.replace(temporary, destination)
    finally:
        safe_unlink_tmp_file(temporary, "title resource temporary", ignore_errors=True)


def assert_retained_v09_targets(
    candidates: Mapping[str, Mapping[str, Any]], baseline: Mapping[str, Any]
) -> None:
    for relative in TARGETS:
        if relative != REPLACED_RESOURCE:
            require_equal(
                candidates[relative],
                baseline["candidates"][relative],
                f"retained v0.9 target pin {relative}",
            )


def snapshot_live_resources(
    live_game_root: Path | None,
) -> dict[str, dict[str, Any]] | None:
    """Hash every game resource and executable this offline workflow must not change."""

    if live_game_root is None:
        return None
    root = live_game_root.resolve(strict=True)
    if not root.is_dir():
        raise ImageCandidateError(f"live game root is not a directory: {root}")
    return {relative: path_spec(root / Path(relative)) for relative in LIVE_GUARD_PATHS}


def assert_live_resources_unchanged(
    live_game_root: Path | None, before: Mapping[str, Mapping[str, Any]] | None
) -> None:
    if live_game_root is None:
        if before is not None:
            raise ImageCandidateError("unexpected live-resource guard state")
        return
    if before is None:
        raise ImageCandidateError("live-resource guard snapshot is absent")
    root = live_game_root.resolve(strict=True)
    after = {relative: path_spec(root / Path(relative)) for relative in LIVE_GUARD_PATHS}
    require_equal(after, dict(before), "live Steam resource/EXE pre-post guard")


def assert_zip_matches(candidate_root: Path, zip_path: Path) -> None:
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            names = archive.namelist()
            assert_exact_zip_members(names, "candidate ZIP")
            for relative in TARGETS:
                if archive.read(relative) != (candidate_root / Path(relative)).read_bytes():
                    raise ImageCandidateError(
                        f"candidate ZIP payload differs from candidate: {relative}"
                    )
    except zipfile.BadZipFile as exc:
        raise ImageCandidateError("candidate ZIP is invalid") from exc


def make_zip(candidate_root: Path, destination: Path) -> dict[str, Any]:
    """Write a deterministic exact-fourteen JP ZIP and verify it by re-read."""

    candidate_root = ensure_safe_tmp_directory(candidate_root, "candidate root")
    destination = assert_safe_tmp_path(destination, "candidate ZIP")
    ensure_safe_tmp_directory(destination.parent, "candidate ZIP parent")
    if destination.exists():
        raise ImageCandidateError(f"unsafe pre-existing candidate ZIP: {destination}")
    temporary = destination.with_name(destination.name + ".tmp")
    temporary = assert_safe_tmp_path(temporary, "candidate ZIP temporary")
    candidate_paths(candidate_root)
    temporary_created = False
    try:
        # Exclusive creation refuses a raced-in file/link.  Keep the opened
        # handle while ZIP data is written, then atomically promote it.
        with temporary.open("x+b") as stream:
            temporary_created = True
            with zipfile.ZipFile(
                stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
            ) as archive:
                for relative in TARGETS:
                    info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(
                        info, (candidate_root / Path(relative)).read_bytes()
                    )
            stream.flush()
            os.fsync(stream.fileno())
        temporary = assert_safe_tmp_path(
            temporary, "candidate ZIP temporary", require_exists=True
        )
        assert_zip_matches(candidate_root, temporary)
        assert_safe_tmp_path(destination, "candidate ZIP")
        if destination.exists():
            raise ImageCandidateError(f"unsafe pre-existing candidate ZIP: {destination}")
        os.replace(temporary, destination)
    except FileExistsError as exc:
        raise ImageCandidateError(f"unsafe pre-existing candidate ZIP temporary: {temporary}") from exc
    finally:
        if temporary_created:
            safe_unlink_tmp_file(temporary, "candidate ZIP temporary", ignore_errors=True)
    destination = assert_safe_tmp_path(destination, "candidate ZIP", require_exists=True)
    assert_zip_matches(candidate_root, destination)
    return path_spec(destination)


def verification_projection(manifest: Mapping[str, Any]) -> dict[str, Any]:
    components = manifest["components"]
    return {
        "schema": VERIFICATION_SCHEMA,
        "runtime": manifest["runtime"],
        "candidate_file_count": manifest["candidate_file_count"],
        "candidate_paths": manifest["candidate_paths"],
        "predecessors": manifest["predecessors"],
        "candidates": manifest["candidates"],
        "provenance": {
            "v0_9_baseline": components["v0_9_baseline"],
            "title_images": components["title_images"],
        },
        "zip": manifest["zip"],
        "checks": manifest["checks"],
    }


def _build_staged(
    baseline_zip: Path,
    baseline_manifest: Path,
    title_candidate: Path,
    staging: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    staging = ensure_safe_tmp_directory(staging, "staging root")
    baseline_zip, baseline_manifest, title_candidate = require_safe_distinct_inputs(
        baseline_zip, baseline_manifest, title_candidate
    )
    baseline = load_v09_manifest(baseline_manifest)
    validate_v09_zip(baseline_zip, baseline)
    title_spec = validate_title_candidate(title_candidate)
    candidate_root = materialize_v09_baseline(baseline_zip, staging, baseline)
    replace_title_resource(candidate_root, title_candidate)
    candidates = candidate_specs(candidate_root)
    assert_retained_v09_targets(candidates, baseline)
    require_equal(
        candidates[REPLACED_RESOURCE], title_spec, "integrated title candidate pin"
    )
    zip_path = staging / DEFAULT_ZIP_NAME
    zip_spec = make_zip(candidate_root, zip_path)
    manifest = {
        "schema": SCHEMA,
        "runtime": dict(EXPECTED_RUNTIME),
        "candidate_root": "candidate",
        "candidate_file_count": len(TARGETS),
        "candidate_paths": list(TARGETS),
        "predecessors": {
            relative: dict(baseline["predecessors"][relative]) for relative in TARGETS
        },
        "candidates": {relative: candidates[relative] for relative in TARGETS},
        "components": {
            "v0_9_baseline": {
                "release_asset": dict(V09_RELEASE_PIN),
                "manifest": {
                    "name": V09_MANIFEST_PIN["name"],
                    "size": V09_MANIFEST_PIN["size"],
                    "sha256": V09_MANIFEST_PIN["sha256"],
                    "schema": V09_MANIFEST_SCHEMA,
                },
                "replaced_resource": REPLACED_RESOURCE,
                "retained_v0_9_target_count": len(TARGETS) - 1,
                "candidate_payloads_verified_exact": True,
            },
            "title_images": {
                "validation": {
                    "path": TITLE_VALIDATION_PATH.relative_to(REPO).as_posix(),
                    **TITLE_VALIDATION_PIN,
                },
                "builder_source_sha256": TITLE_BUILDER_SHA256,
                "source_font_baseline": dict(TITLE_SOURCE_FONT_BASELINE),
                "stock_predecessor": dict(STOCK_RES_LANG_PREDECESSOR),
                "candidate": dict(title_spec),
                "rebuilt_title_slot_count": 108,
                "switch_or_exefs_payload_copied": False,
            },
        },
        "zip": {"name": DEFAULT_ZIP_NAME, **zip_spec, "member_count": len(TARGETS)},
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "jp_route_exact": True,
            "exact_fourteen_files": True,
            "v0_9_release_baseline_exact": True,
            "v0_9_manifest_baseline_exact": True,
            "thirteen_v0_9_targets_retained_exact": True,
            "title_res_lang_only_replaced": True,
            "title_image_slots_0_107_integrated": True,
            "zip_payloads_equal_candidates": True,
            "zip_has_no_extra_reports_png_switch_or_exefs": True,
            "staged_before_promote": True,
            "memory_patch": False,
            "dll_injection": False,
            "hooking": False,
            "exe_or_registry_modified": False,
            "steam_files_written": False,
            "live_game_resource_pre_post_guard": True,
        },
    }
    projection = verification_projection(manifest)
    atomic_write(
        staging / "candidate_manifest.v1.json",
        canonical_json_bytes(manifest),
    )
    return manifest, projection


def build_staged(
    baseline_zip: Path,
    baseline_manifest: Path,
    title_candidate: Path,
    staging: Path,
    live_game_root: Path | None = DEFAULT_LIVE_GAME_ROOT,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build offline while proving the live Steam resource and EXE vector stayed fixed."""

    staging = ensure_safe_tmp_directory(staging, "staging root")
    before = snapshot_live_resources(live_game_root)
    try:
        return _build_staged(baseline_zip, baseline_manifest, title_candidate, staging)
    finally:
        assert_live_resources_unchanged(live_game_root, before)


def validate_destination(path: Path) -> Path:
    resolved = assert_safe_tmp_path(path, "output destination")
    if resolved.exists():
        raise ImageCandidateError(f"output already exists: {resolved}")
    ensure_safe_tmp_directory(resolved.parent, "output destination parent")
    # Re-check after parent creation and immediately before the caller uses it.
    return assert_safe_tmp_path(resolved, "output destination")


def staged_build(
    baseline_zip: Path,
    baseline_manifest: Path,
    title_candidate: Path,
    destination_parent: Path,
    live_game_root: Path | None,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    destination_parent = ensure_safe_tmp_directory(
        destination_parent, "staging parent"
    )
    staging = Path(
        tempfile.mkdtemp(prefix=".steam-jp-117-image-v1-", dir=destination_parent)
    )
    staging = ensure_safe_tmp_directory(staging, "staging root")
    try:
        manifest, projection = build_staged(
            baseline_zip, baseline_manifest, title_candidate, staging, live_game_root
        )
    except Exception:
        safe_rmtree(staging, "failed staging cleanup", ignore_errors=True)
        raise
    return staging, manifest, projection


def load_tracked_verification() -> dict[str, Any]:
    if not VERIFICATION_PATH.is_file():
        raise ImageCandidateError("tracked image candidate verification is missing")
    value = load_canonical_json(VERIFICATION_PATH, "tracked image verification")
    require_equal(value.get("schema"), VERIFICATION_SCHEMA, "tracked verification schema")
    return value


def atomic_write(path: Path, blob: bytes) -> None:
    path = assert_safe_tmp_path(path, "atomic output")
    ensure_safe_tmp_directory(path.parent, "atomic output parent")
    if path.exists():
        raise ImageCandidateError(f"unsafe pre-existing output path: {path}")
    temporary = write_new_tmp_file(path.with_name(path.name + ".tmp"), blob, "atomic temporary")
    try:
        require_equal(path_spec(temporary), blob_spec(blob), "temporary output pin")
        assert_safe_tmp_path(temporary, "atomic temporary", require_exists=True)
        assert_safe_tmp_path(path, "atomic output")
        if path.exists():
            raise ImageCandidateError(f"unsafe pre-existing output path: {path}")
        os.replace(temporary, path)
    finally:
        safe_unlink_tmp_file(temporary, "atomic temporary", ignore_errors=True)


def command_bootstrap(args: argparse.Namespace) -> int:
    proposal = validate_destination(args.proposal)
    staging, _manifest, projection = staged_build(
        args.baseline_zip.resolve(),
        args.baseline_manifest.resolve(),
        args.title_candidate.resolve(),
        proposal.parent,
        args.live_game_root.resolve(),
    )
    try:
        atomic_write(proposal, canonical_json_bytes(projection))
    finally:
        safe_rmtree(staging, "bootstrap staging cleanup")
    print(f"proposal={proposal}")
    print(f"proposal_sha256={path_spec(proposal)['sha256']}")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    scratch = validate_destination(args.scratch_root)
    scratch = ensure_safe_tmp_directory(scratch, "verify scratch root")
    try:
        staging, _manifest, projection = staged_build(
            args.baseline_zip.resolve(),
            args.baseline_manifest.resolve(),
            args.title_candidate.resolve(),
            scratch,
            args.live_game_root.resolve(),
        )
        try:
            require_equal(projection, expected, "integrated image candidate verification")
        finally:
            safe_rmtree(staging, "verify staging cleanup")
    finally:
        safe_rmtree(scratch, "verify scratch cleanup")
    print("status=PASS")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    output = validate_destination(args.output_root)
    staging, manifest, projection = staged_build(
        args.baseline_zip.resolve(),
        args.baseline_manifest.resolve(),
        args.title_candidate.resolve(),
        output.parent,
        args.live_game_root.resolve(),
    )
    try:
        require_equal(projection, expected, "integrated image candidate verification")
        assert_safe_tmp_path(staging, "build staging root", require_exists=True)
        assert_safe_tmp_path(output, "build output destination")
        if output.exists():
            raise ImageCandidateError(f"unsafe pre-existing build output: {output}")
        os.replace(staging, output)
    except Exception:
        safe_rmtree(staging, "failed build staging cleanup", ignore_errors=True)
        raise
    print("status=PASS")
    print(f"steam_pk_version={manifest['runtime']['pk_version']}")
    print(f"candidate_files={manifest['candidate_file_count']}")
    print(f"zip_name={manifest['zip']['name']}")
    print(f"zip_sha256={manifest['zip']['sha256']}")
    print("steam_files_written=False")
    return 0


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--baseline-zip", type=Path, default=DEFAULT_BASELINE_ZIP)
    parser.add_argument(
        "--baseline-manifest", type=Path, default=DEFAULT_BASELINE_MANIFEST
    )
    parser.add_argument("--title-candidate", type=Path, default=DEFAULT_TITLE_CANDIDATE)
    parser.add_argument("--live-game-root", type=Path, default=DEFAULT_LIVE_GAME_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    bootstrap = commands.add_parser("bootstrap")
    add_common_arguments(bootstrap)
    bootstrap.add_argument("--proposal", type=Path, required=True)
    verify = commands.add_parser("verify")
    add_common_arguments(verify)
    verify.add_argument("--scratch-root", type=Path, required=True)
    build = commands.add_parser("build")
    add_common_arguments(build)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "bootstrap":
            return command_bootstrap(args)
        if args.command == "verify":
            return command_verify(args)
        return command_build(args)
    except (ImageCandidateError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
