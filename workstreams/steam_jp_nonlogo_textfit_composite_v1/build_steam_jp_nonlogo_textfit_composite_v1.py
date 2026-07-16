#!/usr/bin/env python3
"""Compose the private Steam JP non-logo image/text-fit candidate.

This is a deliberately narrow, offline-only integrator.  It starts from the
pinned Steam JP v0.9 package for text, composes the independently gated
fullwidth and v2.3 line-break operations for ``MSG/JP/ev_strdata.bin``, and
uses the existing private image-composite ``RES_JP/res_lang.bin`` as the image
base.  The only image-base replacement is G1N font outer entries 6 and 7.

Outer entries 3 and 24 are protected title/logo entries.  They are never
inputs to a replacement operation and must be byte-identical (data and LINK
padding) in the result.  In fact every image-base entry other than 6 and 7 is
required to be byte-identical in the result, which keeps all current non-font
image work intact as well.

The output is a private candidate directory below ``KR_PATCH_WORK/tmp``.  It
never writes a game installation, creates a release archive, or performs a
Git/GitHub operation.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TMP_ROOT = REPO / "tmp"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import LinkArchive, parse_link, rebuild_link  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-nonlogo-textfit-composite.private.v1"
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

FONT_ROUTES: dict[str, tuple[int, ...]] = {
    "RES_JP/res_lang.bin": (6, 7),
    "RES_JP_PK/res_lang_pk.bin": (16, 17),
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": (1,),
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": (0, 1),
}
IMAGE_FONT_OUTERS = FONT_ROUTES["RES_JP/res_lang.bin"]
PROTECTED_LOGO_TITLE_OUTERS = (3, 24)
CURRENT_IMAGE_OUTERS = (3, 8, 12, 13, 16, 24)

DEFAULT_V09_ZIP = (
    TMP_ROOT
    / "steam_jp_117_image_candidate_v1_inputs"
    / "v0.9.0"
    / "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip"
)
DEFAULT_IMAGE_BASE = (
    TMP_ROOT / "steam_jp_image_composite_v1" / "run_c" / "candidate" / "RES_JP" / "res_lang.bin"
)
DEFAULT_FONT_CANDIDATE_ROOT = (
    TMP_ROOT / "steam_jp_font_advance_candidate_v1_run7" / "private" / "candidate"
)
DEFAULT_FULLWIDTH_METADATA = (
    REPO
    / "workstreams"
    / "steam_jp_fullwidth_normalization_v1"
    / "public"
    / "steam_jp_fullwidth_normalization.v1.json"
)
DEFAULT_SWITCH_V13_ZIP = TMP_ROOT / "third_party_switch_v13" / "NobunagaShinsei_KoreanPatch_v1.3.zip"
DEFAULT_SWITCH_V22_ZIP = TMP_ROOT / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.2.zip"
DEFAULT_SWITCH_V23_ZIP = TMP_ROOT / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.3.zip"
DEFAULT_SWITCH_V24_ZIP = TMP_ROOT / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.4.zip"
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "steam_jp_nonlogo_textfit_composite_v1" / "candidate_v1"

# These pins intentionally describe only private predecessor candidates.  A
# successor needs a new workstream instead of silently mixing a newer image or
# font base into this exact composition contract.
IMAGE_BASE_PIN = {
    "size": 160_095_868,
    "sha256": "2F8048EC34B8B86CED54C0DC9A0879522D2717953805A4E4CC5EFF05407A4A45",
}
FONT_CANDIDATE_PINS = {
    "RES_JP/res_lang.bin": {
        "size": 155_757_652,
        "sha256": "64CCD9068D7EBCFA670091B8A8FB367F1E577C1BCAC05847F4F3C77D7219A64D",
    },
    "RES_JP_PK/res_lang_pk.bin": {
        "size": 143_288_371,
        "sha256": "C0C8509FC91C244A813D4BC20C46E515F6396D03BEAC71B80F89A39245125189",
    },
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": {
        "size": 80_697_755,
        "sha256": "B5BF46E90C444DE1931BCF455447168C01B77967D3143B72916636157F59DE00",
    },
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": {
        "size": 71_294_187,
        "sha256": "13504CB00D09D9A43B9EA5D9AD9FADEF8F58EC12CD290872EAC3FF31335DDA60",
    },
}


class CompositeError(ValueError):
    """Raised when an input or preservation contract is violated."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def file_spec(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            digest.update(chunk)
    return {"size": size, "sha256": digest.hexdigest().upper()}


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise CompositeError(f"{label} differs from its required contract")


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def _require_under(path: Path, root: Path, label: str, *, directory: bool = False) -> Path:
    resolved = _resolved(path)
    allowed = _resolved(root)
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise CompositeError(f"{label} must stay under {allowed}") from exc
    if directory:
        if not resolved.is_dir():
            raise CompositeError(f"{label} is not an existing directory: {resolved}")
    elif not resolved.is_file():
        raise CompositeError(f"{label} is not an existing regular file: {resolved}")
    return resolved


def _private_file(path: Path, label: str) -> Path:
    return _require_under(path, TMP_ROOT, label)


def _private_directory(path: Path, label: str) -> Path:
    return _require_under(path, TMP_ROOT, label, directory=True)


def _repo_file(path: Path, label: str) -> Path:
    return _require_under(path, REPO, label)


def _relative_to_repo(path: Path) -> str:
    try:
        return _resolved(path).relative_to(_resolved(REPO)).as_posix()
    except ValueError as exc:
        raise CompositeError("input path unexpectedly escaped KR_PATCH_WORK") from exc


def _entry_pair(archive: LinkArchive, index: int) -> tuple[bytes, bytes]:
    if index < 0 or index >= len(archive.entries):
        raise CompositeError(f"LINK outer entry /{index} is missing")
    entry = archive.entries[index]
    return entry.data, entry.gap_after


def _changed_entries(before: LinkArchive, after: LinkArchive) -> set[int]:
    if len(before.entries) != len(after.entries):
        raise CompositeError("LINK outer-entry count changed")
    return {
        index
        for index in range(len(before.entries))
        if _entry_pair(before, index) != _entry_pair(after, index)
    }


def _assert_link_shell_equal(before: LinkArchive, after: LinkArchive, label: str) -> None:
    require_equal(after.fixed_header, before.fixed_header, f"{label} fixed LINK header")
    require_equal(after.pre_data_padding, before.pre_data_padding, f"{label} LINK pre-data padding")
    require_equal(len(after.entries), len(before.entries), f"{label} LINK entry count")


def assert_font_candidate_route(
    baseline_blob: bytes,
    candidate_blob: bytes,
    target_outers: Sequence[int],
    label: str,
) -> dict[str, Any]:
    """Prove a font candidate changes exactly its allowed G1N outer entries."""

    baseline = parse_link(baseline_blob)
    candidate = parse_link(candidate_blob)
    _assert_link_shell_equal(baseline, candidate, label)
    targets = set(target_outers)
    if targets & set(PROTECTED_LOGO_TITLE_OUTERS):
        raise CompositeError(f"{label} illegally includes a protected logo/title outer entry")
    actual = _changed_entries(baseline, candidate)
    require_equal(actual, targets, f"{label} changed outer-entry domain")
    for outer in sorted(targets):
        base_data, base_gap = _entry_pair(baseline, outer)
        candidate_data, candidate_gap = _entry_pair(candidate, outer)
        if candidate_data == base_data:
            raise CompositeError(f"{label} /{outer} did not change G1N data")
        require_equal(candidate_gap, base_gap, f"{label} /{outer} LINK gap")
    return {"changed_outer_entries": sorted(actual), "candidate": spec(candidate_blob)}


def compose_res_jp_font(
    image_base_blob: bytes,
    v09_baseline_blob: bytes,
    font_candidate_blob: bytes,
) -> tuple[bytes, dict[str, Any]]:
    """Graft only /6 and /7 from the pinned font candidate onto the image base.

    The function uses LINK data/gap pairs as its preservation unit because
    rebuilding a LINK table can move offsets while still preserving a payload.
    It therefore detects both visible image changes and trailing LINK padding
    changes at every protected outer entry.
    """

    if set(IMAGE_FONT_OUTERS) & set(PROTECTED_LOGO_TITLE_OUTERS):
        raise CompositeError("internal font-target contract overlaps logo/title protection")
    image = parse_link(image_base_blob)
    baseline = parse_link(v09_baseline_blob)
    font = parse_link(font_candidate_blob)
    _assert_link_shell_equal(baseline, image, "image base versus v0.9")
    _assert_link_shell_equal(baseline, font, "font candidate versus v0.9")

    for outer in IMAGE_FONT_OUTERS:
        require_equal(
            _entry_pair(image, outer),
            _entry_pair(baseline, outer),
            f"image base /{outer} v0.9 preimage",
        )
    font_report = assert_font_candidate_route(
        v09_baseline_blob,
        font_candidate_blob,
        IMAGE_FONT_OUTERS,
        "RES_JP font candidate",
    )
    for outer in (*CURRENT_IMAGE_OUTERS, *PROTECTED_LOGO_TITLE_OUTERS):
        _entry_pair(image, outer)

    replacements = {outer: _entry_pair(font, outer)[0] for outer in IMAGE_FONT_OUTERS}
    candidate_blob = rebuild_link(image, replacements)
    candidate = parse_link(candidate_blob)
    _assert_link_shell_equal(image, candidate, "composed image/font candidate")

    changed = _changed_entries(image, candidate)
    require_equal(changed, set(IMAGE_FONT_OUTERS), "composed image/font changed outer-entry domain")
    for outer in range(len(image.entries)):
        expected_data, expected_gap = (
            (_entry_pair(font, outer)[0], _entry_pair(image, outer)[1])
            if outer in IMAGE_FONT_OUTERS
            else _entry_pair(image, outer)
        )
        require_equal(_entry_pair(candidate, outer), (expected_data, expected_gap), f"composed /{outer}")
    for outer in PROTECTED_LOGO_TITLE_OUTERS:
        require_equal(
            _entry_pair(candidate, outer),
            _entry_pair(image, outer),
            f"protected logo/title /{outer}",
        )

    protected = {
        str(outer): {
            "data_sha256": sha256(_entry_pair(image, outer)[0]),
            "gap_sha256": sha256(_entry_pair(image, outer)[1]),
        }
        for outer in PROTECTED_LOGO_TITLE_OUTERS
    }
    return candidate_blob, {
        "image_base_font_preimages_equal_v09": True,
        "font_candidate": font_report,
        "changed_outer_entries": sorted(changed),
        "all_non_font_outer_entries_preserved_from_image_base": True,
        "protected_logo_title_outer_entries": protected,
        "current_image_outer_entries_preserved_from_image_base": list(CURRENT_IMAGE_OUTERS),
    }


def _load_module(module_name: str, path: Path) -> Any:
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    module_spec = importlib.util.spec_from_file_location(module_name, path)
    if module_spec is None or module_spec.loader is None:
        raise CompositeError(f"cannot load dependency: {path.name}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    return module


def source_modules() -> tuple[Any, Any]:
    fullwidth = _load_module(
        "steam_jp_nonlogo_textfit_fullwidth_v1",
        REPO
        / "workstreams"
        / "steam_jp_fullwidth_normalization_v1"
        / "build_steam_jp_fullwidth_normalization_v1.py",
    )
    linebreak = _load_module(
        "steam_jp_nonlogo_textfit_linebreak_v1",
        REPO
        / "workstreams"
        / "steam_jp_switch_v23_linebreak_v1"
        / "build_steam_jp_switch_v23_linebreak_v1.py",
    )
    return fullwidth, linebreak


def _read_pinned_file(path: Path, expected: Mapping[str, Any], label: str) -> bytes:
    actual = file_spec(path)
    require_equal(actual, dict(expected), f"{label} file pin")
    return path.read_bytes()


def _font_candidate_payloads(font_root: Path) -> dict[str, bytes]:
    root = _private_directory(font_root, "font candidate root")
    result: dict[str, bytes] = {}
    for resource, expected in FONT_CANDIDATE_PINS.items():
        path = _private_file(root / Path(resource), f"font candidate {resource}")
        result[resource] = _read_pinned_file(path, expected, f"font candidate {resource}")
    return result


def _validate_paths(
    v09_zip: Path,
    image_base: Path,
    font_root: Path,
    fullwidth_metadata: Path,
    switch_v13_zip: Path,
    switch_v22_zip: Path,
    switch_v23_zip: Path,
    switch_v24_zip: Path,
) -> tuple[Path, Path, Path, Path, Path, Path, Path, Path]:
    return (
        _private_file(v09_zip, "v0.9 baseline package"),
        _private_file(image_base, "current image-composite base"),
        _private_directory(font_root, "font candidate root"),
        _repo_file(fullwidth_metadata, "fullwidth metadata"),
        _private_file(switch_v13_zip, "Switch v1.3 evidence package"),
        _private_file(switch_v22_zip, "Switch v2.2 evidence package"),
        _private_file(switch_v23_zip, "Switch v2.3 evidence package"),
        _private_file(switch_v24_zip, "Switch v2.4 evidence package"),
    )


def build_in_memory(
    *,
    v09_zip: Path = DEFAULT_V09_ZIP,
    image_base: Path = DEFAULT_IMAGE_BASE,
    font_candidate_root: Path = DEFAULT_FONT_CANDIDATE_ROOT,
    fullwidth_metadata: Path = DEFAULT_FULLWIDTH_METADATA,
    switch_v13_zip: Path = DEFAULT_SWITCH_V13_ZIP,
    switch_v22_zip: Path = DEFAULT_SWITCH_V22_ZIP,
    switch_v23_zip: Path = DEFAULT_SWITCH_V23_ZIP,
    switch_v24_zip: Path = DEFAULT_SWITCH_V24_ZIP,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Build all fourteen private payloads without writing them anywhere."""

    (
        v09_zip,
        image_base,
        font_candidate_root,
        fullwidth_metadata,
        switch_v13_zip,
        switch_v22_zip,
        switch_v23_zip,
        switch_v24_zip,
    ) = _validate_paths(
        v09_zip,
        image_base,
        font_candidate_root,
        fullwidth_metadata,
        switch_v13_zip,
        switch_v22_zip,
        switch_v23_zip,
        switch_v24_zip,
    )
    fullwidth, linebreak = source_modules()
    metadata = fullwidth.read_metadata(fullwidth_metadata)
    linebreak_metadata = linebreak.read_fullwidth_metadata(fullwidth_metadata)
    require_equal(linebreak_metadata, metadata, "fullwidth metadata parsers")
    baseline_payloads, documents = fullwidth.load_v09_documents(v09_zip)
    require_equal(tuple(baseline_payloads), TARGETS, "v0.9 target vector")
    fullwidth_payloads = fullwidth.materialize_candidate(baseline_payloads, documents, metadata)
    require_equal(tuple(fullwidth_payloads), TARGETS, "fullwidth target vector")

    overlay, _review, linebreak_validation, _linebreak_only = linebreak.expected_artifacts(
        v09_zip,
        switch_v13_zip,
        switch_v22_zip,
        switch_v23_zip,
        switch_v24_zip,
        fullwidth_metadata,
    )
    composed_ev, composed_ev_report = linebreak.apply_composed_fullwidth_and_linebreak_to_baseline(
        baseline_payloads["MSG/JP/ev_strdata.bin"], overlay, metadata
    )
    payloads = dict(fullwidth_payloads)
    payloads["MSG/JP/ev_strdata.bin"] = composed_ev

    image_blob = _read_pinned_file(image_base, IMAGE_BASE_PIN, "current image-composite base")
    font_payloads = _font_candidate_payloads(font_candidate_root)
    composed_res_jp, image_font_report = compose_res_jp_font(
        image_blob,
        baseline_payloads["RES_JP/res_lang.bin"],
        font_payloads["RES_JP/res_lang.bin"],
    )
    payloads["RES_JP/res_lang.bin"] = composed_res_jp
    for resource, targets in FONT_ROUTES.items():
        if resource == "RES_JP/res_lang.bin":
            continue
        assert_font_candidate_route(
            baseline_payloads[resource],
            font_payloads[resource],
            targets,
            f"{resource} font candidate",
        )
        payloads[resource] = font_payloads[resource]
    require_equal(tuple(payloads), TARGETS, "final target vector")

    # Fullwidth intentionally has no font replacement.  Font work is added
    # here only after every text candidate has completed from the v0.9 base.
    for resource in FONT_ROUTES:
        if resource == "RES_JP/res_lang.bin":
            continue
        if fullwidth_payloads[resource] != baseline_payloads[resource]:
            raise CompositeError(f"fullwidth unexpectedly changed font resource: {resource}")

    manifest = {
        "schema": SCHEMA,
        "candidate_kind": "private_offline_directory",
        "inputs": {
            "v09_package": {"path": _relative_to_repo(v09_zip), **file_spec(v09_zip)},
            "image_composite_base": {"path": _relative_to_repo(image_base), **IMAGE_BASE_PIN},
            "font_candidate_root": _relative_to_repo(font_candidate_root),
            "fullwidth_metadata": {
                "path": _relative_to_repo(fullwidth_metadata),
                **file_spec(fullwidth_metadata),
            },
        },
        "composition": {
            "text_base": "Steam JP v0.9 exact fourteen-file vector",
            "fullwidth_operation_model_external_and_hash_gated": True,
            "linebreak_operation_model_external_and_hash_gated": True,
            "fullwidth_linebreak_composed_from_common_v09_preimage": True,
            "linebreak_only_candidate_not_used_for_overlap": True,
            "linebreak": {
                "entry_count": linebreak_validation["operations"]["entry_count"],
                "linebreak_tokens_replaced": composed_ev_report["linebreak_tokens_replaced"],
                "fullwidth_linebreak_intersection_count": composed_ev_report[
                    "fullwidth_linebreak_composition"
                ]["intersection_entry_count"],
            },
            "image_font": image_font_report,
            "font_routes": {resource: list(targets) for resource, targets in FONT_ROUTES.items()},
        },
        "outputs": {resource: spec(payloads[resource]) for resource in TARGETS},
        "safety": {
            "protected_logo_title_outer_entries": list(PROTECTED_LOGO_TITLE_OUTERS),
            "protected_logo_title_entries_replaced": [],
            "all_res_jp_non_font_outer_entries_preserved_from_image_base": True,
            "game_install_modified": False,
            "release_archive_created": False,
            "git_or_github_action": False,
            "switch_binary_written": False,
        },
    }
    return payloads, manifest


def _safe_output_root(path: Path) -> Path:
    output = _resolved(path)
    tmp = _resolved(TMP_ROOT)
    try:
        output.relative_to(tmp)
    except ValueError as exc:
        raise CompositeError("private output must stay below KR_PATCH_WORK/tmp") from exc
    if output == tmp:
        raise CompositeError("KR_PATCH_WORK/tmp itself is not an output directory")
    if output.exists() and not output.is_dir():
        raise CompositeError("private output root exists but is not a directory")
    return output


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _expected_output_files() -> set[Path]:
    return {Path("manifest.json"), *(Path("candidate") / Path(resource) for resource in TARGETS)}


def _assert_output_tree_is_safe(output_root: Path) -> None:
    if not output_root.exists():
        return
    expected = _expected_output_files()
    found = {path.relative_to(output_root) for path in output_root.rglob("*") if path.is_file()}
    unexpected = found - expected
    if unexpected:
        rendered = ", ".join(sorted(path.as_posix() for path in unexpected))
        raise CompositeError(f"private output contains unexpected files: {rendered}")


def write_private_candidate(payloads: Mapping[str, bytes], manifest: Mapping[str, Any], output_root: Path) -> Path:
    """Write only the exact fourteen-file vector and a source-free manifest."""

    output = _safe_output_root(output_root)
    require_equal(tuple(payloads), TARGETS, "private output target vector")
    _assert_output_tree_is_safe(output)
    for resource in TARGETS:
        _atomic_write(output / "candidate" / Path(resource), payloads[resource])
    _atomic_write(output / "manifest.json", _canonical_json(dict(manifest)))
    _assert_output_tree_is_safe(output)
    for resource in TARGETS:
        actual = (output / "candidate" / Path(resource)).read_bytes()
        require_equal(actual, payloads[resource], f"private output {resource}")
    persisted_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    require_equal(persisted_manifest, dict(manifest), "private output manifest")
    return output


def verify_private_candidate(output_root: Path, expected_manifest: Mapping[str, Any]) -> None:
    output = _safe_output_root(output_root)
    _assert_output_tree_is_safe(output)
    if not output.exists():
        raise CompositeError("private output does not exist")
    actual_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    require_equal(actual_manifest, dict(expected_manifest), "persisted composite manifest")
    outputs = actual_manifest.get("outputs")
    if not isinstance(outputs, dict):
        raise CompositeError("persisted composite manifest has no output spec map")
    for resource in TARGETS:
        actual = file_spec(output / "candidate" / Path(resource))
        require_equal(actual, outputs.get(resource), f"persisted composite output {resource}")


def verify_in_memory(**kwargs: Any) -> dict[str, Any]:
    """Rebuild once with every source gate; this function never writes output."""

    payloads, manifest = build_in_memory(**kwargs)
    require_equal(tuple(payloads), TARGETS, "verification target vector")
    for resource in TARGETS:
        require_equal(spec(payloads[resource]), manifest["outputs"][resource], f"verification {resource}")
    del payloads
    gc.collect()
    return manifest | {"verification": {"in_memory_build_validated": True, "output_written": False}}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("command", choices=("build", "verify"))
    result.add_argument("--v09-zip", type=Path, default=DEFAULT_V09_ZIP)
    result.add_argument("--image-base", type=Path, default=DEFAULT_IMAGE_BASE)
    result.add_argument("--font-candidate-root", type=Path, default=DEFAULT_FONT_CANDIDATE_ROOT)
    result.add_argument("--fullwidth-metadata", type=Path, default=DEFAULT_FULLWIDTH_METADATA)
    result.add_argument("--switch-v13-zip", type=Path, default=DEFAULT_SWITCH_V13_ZIP)
    result.add_argument("--switch-v22-zip", type=Path, default=DEFAULT_SWITCH_V22_ZIP)
    result.add_argument("--switch-v23-zip", type=Path, default=DEFAULT_SWITCH_V23_ZIP)
    result.add_argument("--switch-v24-zip", type=Path, default=DEFAULT_SWITCH_V24_ZIP)
    result.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    result.add_argument(
        "--check-output-root",
        type=Path,
        default=None,
        help="verify an already-written private candidate against the rebuilt manifest",
    )
    return result


def _build_kwargs(args: argparse.Namespace) -> dict[str, Path]:
    return {
        "v09_zip": args.v09_zip,
        "image_base": args.image_base,
        "font_candidate_root": args.font_candidate_root,
        "fullwidth_metadata": args.fullwidth_metadata,
        "switch_v13_zip": args.switch_v13_zip,
        "switch_v22_zip": args.switch_v22_zip,
        "switch_v23_zip": args.switch_v23_zip,
        "switch_v24_zip": args.switch_v24_zip,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "build":
            payloads, manifest = build_in_memory(**_build_kwargs(args))
            output = write_private_candidate(payloads, manifest, args.output_root)
            verify_private_candidate(output, manifest)
            print("status=PASS")
            print(f"private_output={_relative_to_repo(output)}")
            print(f"res_jp_sha256={manifest['outputs']['RES_JP/res_lang.bin']['sha256']}")
            print("game_install_modified=False")
            print("release_archive_created=False")
            return 0
        manifest = verify_in_memory(**_build_kwargs(args))
        if args.check_output_root is not None:
            verify_private_candidate(args.check_output_root, manifest)
        print("status=PASS")
        print("in_memory_only=True")
        print("game_install_modified=False")
        print("release_archive_created=False")
        return 0
    # The imported fullwidth verifier deliberately uses RuntimeError for a
    # failed hash/coordinate gate.  Convert that expected dependency failure
    # to the same concise CLI error as the compositor's own contract errors.
    except (CompositeError, OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
