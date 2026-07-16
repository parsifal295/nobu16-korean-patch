#!/usr/bin/env python3
"""Assemble the Steam PK 1.1.7 JP-route v0.9.0 exact-14 candidate.

This candidate is intentionally a narrow, verified successor to the released
v0.8.0 exact-14 package.  It validates that package byte-for-byte against the
tracked v5 verification record, then replaces only the two independently
pinned base-language resources with the Wave 11 residual candidates:

* ``MSG/JP/msggame.bin``: 270 safe residual rows (23,194 total); and
* ``MSG/JP/ev_strdata.bin``: 40 safe residual rows (13,085 total).

The baseline package is a public release input rather than the currently
installed Steam directory.  Both replacements are rebuilt from the immutable
pre-application Steam 1.1.7 backup.  No command in this workstream writes an
installed game file, modifies an executable, or touches the SC route.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
V5_VERIFICATION_PATH = (
    REPO / "workstreams" / "steam_jp_117_candidate_v5" / "verification.v5.json"
)
V5_VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-verification.v5"
MSGGAME_WAVE11_PATH = (
    REPO
    / "workstreams"
    / "base_msggame_wave11"
    / "build_base_msggame_wave11.py"
)
EV_STRDATA_WAVE11_PATH = (
    REPO
    / "workstreams"
    / "base_ev_strdata_jp_residual_wave11"
    / "build_base_ev_strdata_jp_residual_wave11.py"
)

DEFAULT_BASELINE_ZIP = (
    REPO
    / "tmp"
    / "steam_jp_117_candidate_v5_14file_final"
    / "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip"
)
DEFAULT_STOCK_ROOT = Path(
    r"F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/"
    r"file_only_transaction/steam-jp-1.1.7-v0.8.0/originals"
)
DEFAULT_LIVE_GAME_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_117_candidate_v6"
DEFAULT_ZIP_NAME = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip"
SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-manifest.v6"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-verification.v6"
VERIFICATION_PATH = WORKSTREAM / "verification.v6.json"

BASE_MSGGAME_RESOURCE = "MSG/JP/msggame.bin"
BASE_EV_STRDATA_RESOURCE = "MSG/JP/ev_strdata.bin"
REPLACED_RESOURCES = (BASE_EV_STRDATA_RESOURCE, BASE_MSGGAME_RESOURCE)
V5_VERIFICATION_SHA256 = (
    "BF0CC287FC2E2FBADB0A3CB29055C2BF7F6BAC10CDF9C686514CB64B5A4BC2E3"
)
WAVE11_BUILDER_SHA256 = {
    BASE_MSGGAME_RESOURCE: "793FF773E55B9268FA793F02EF6529BB0C6DFBB3B2A9E974F902469C9B3D5C64",
    BASE_EV_STRDATA_RESOURCE: "2E4EA524DD63162BF7CAD0EFFABCE55D0E31F4D8731A23AF70BFAACD00A36B90",
}
BASELINE_RELEASE_PIN = {
    "name": "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip",
    "size": 356_954_358,
    "sha256": "8167B09DE5DC56C1F195AF0A913336F552D189B0DB320C2A4F5EC863BBC58D08",
}


class CandidateV6Error(RuntimeError):
    """Raised when an immutable input, scope, or candidate invariant differs."""


def load_module(name: str, path: Path) -> Any:
    if not path.is_file():
        raise CandidateV6Error(f"required component is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateV6Error(f"cannot import component: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXPECTED_TARGETS = (
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
TARGETS = EXPECTED_TARGETS
LIVE_GUARD_PATHS = (*TARGETS, "NOBU16.exe", "NOBU16PK.exe")
if tuple(sorted(REPLACED_RESOURCES)) != REPLACED_RESOURCES:
    raise RuntimeError("v6 exact-fourteen JP target vector changed")


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def blob_spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def path_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CandidateV6Error(f"missing required file: {path}")
    return blob_spec(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise CandidateV6Error(f"{label} differs: expected={expected!r}, actual={actual!r}")


def require_module_pin(pin: Any, blob: bytes, label: str) -> dict[str, Any]:
    if not isinstance(pin, Mapping):
        raise CandidateV6Error(f"{label} pin is not an object")
    expected_sizes = {
        value
        for key in ("size", "packed_size")
        if isinstance((value := pin.get(key)), int) and not isinstance(value, bool)
    }
    expected_hashes = {
        value
        for key in ("sha256", "packed_sha256")
        if isinstance((value := pin.get(key)), str)
    }
    actual = blob_spec(blob)
    if expected_sizes != {actual["size"]} or expected_hashes != {actual["sha256"]}:
        raise CandidateV6Error(f"{label} candidate pin differs")
    return actual


def candidate_paths(candidate_root: Path) -> list[str]:
    if not candidate_root.is_dir():
        raise CandidateV6Error(f"candidate root is missing: {candidate_root}")
    result = sorted(
        path.relative_to(candidate_root).as_posix()
        for path in candidate_root.rglob("*")
        if path.is_file()
    )
    if result != list(TARGETS):
        raise CandidateV6Error("candidate root is not the exact fourteen-file JP vector")
    return result


def candidate_specs(candidate_root: Path) -> dict[str, dict[str, Any]]:
    candidate_paths(candidate_root)
    return {relative: path_spec(candidate_root / Path(relative)) for relative in TARGETS}


def load_v5_verification() -> dict[str, Any]:
    path = V5_VERIFICATION_PATH
    blob = path.read_bytes()
    if sha256(blob) != V5_VERIFICATION_SHA256:
        raise CandidateV6Error("immutable v0.8 verification pin changed")
    try:
        value = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateV6Error("invalid v0.8 verification JSON") from exc
    if not isinstance(value, dict) or value.get("schema") != V5_VERIFICATION_SCHEMA:
        raise CandidateV6Error("immutable v0.8 verification schema changed")
    if value.get("candidate_paths") != list(TARGETS):
        raise CandidateV6Error("immutable v0.8 candidate vector changed")
    candidates = value.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != set(TARGETS):
        raise CandidateV6Error("immutable v0.8 candidate pins changed")
    return value


def validate_baseline_zip(baseline_zip: Path, v5_verification: Mapping[str, Any]) -> None:
    if baseline_zip.name != BASELINE_RELEASE_PIN["name"]:
        raise CandidateV6Error("baseline release asset name differs")
    require_equal(path_spec(baseline_zip), {
        "size": BASELINE_RELEASE_PIN["size"],
        "sha256": BASELINE_RELEASE_PIN["sha256"],
    }, "baseline v0.8 release asset")
    require_equal(v5_verification.get("zip"), {
        "member_count": len(TARGETS),
        **BASELINE_RELEASE_PIN,
    }, "tracked v0.8 release pin")
    with zipfile.ZipFile(baseline_zip, "r") as archive:
        names = archive.namelist()
        if names != list(TARGETS):
            raise CandidateV6Error("baseline ZIP member vector is not exact fourteen")
        for relative in TARGETS:
            actual = blob_spec(archive.read(relative))
            require_equal(
                actual,
                v5_verification["candidates"][relative],
                f"baseline ZIP payload pin {relative}",
            )


def materialize_baseline(
    baseline_zip: Path, staging: Path, v5_verification: Mapping[str, Any]
) -> Path:
    """Copy the pinned public v0.8 baseline into isolated candidate staging."""

    validate_baseline_zip(baseline_zip, v5_verification)
    candidate_root = staging / "candidate"
    candidate_root.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(baseline_zip, "r") as archive:
        for relative in TARGETS:
            destination = candidate_root / Path(relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            payload = archive.read(relative)
            destination.write_bytes(payload)
            require_equal(
                path_spec(destination),
                v5_verification["candidates"][relative],
                f"materialized baseline payload pin {relative}",
            )
    candidate_paths(candidate_root)
    return candidate_root


def load_wave_module(name: str, path: Path, resource: str) -> Any:
    expected_source_sha = WAVE11_BUILDER_SHA256.get(resource)
    if expected_source_sha is None:
        raise CandidateV6Error(f"Wave 11 source pin is absent: {resource}")
    if path_spec(path)["sha256"] != expected_source_sha:
        raise CandidateV6Error(f"Wave 11 builder source pin differs: {resource}")
    module = load_module(name, path)
    if getattr(module, "RESOURCE", None) != resource:
        raise CandidateV6Error(f"Wave 11 resource differs: {resource}")
    if not callable(getattr(module, "build_blob", None)):
        raise CandidateV6Error(f"Wave 11 build_blob is missing: {resource}")
    if not callable(getattr(module, "verify", None)):
        raise CandidateV6Error(f"Wave 11 verifier is missing: {resource}")
    if not isinstance(getattr(module, "EXPECTED_CANDIDATE", None), Mapping):
        raise CandidateV6Error(f"Wave 11 candidate pin is missing: {resource}")
    if not isinstance(getattr(module, "DEFAULT_SWITCH_ZIP", None), Path):
        raise CandidateV6Error(f"Wave 11 Switch input is missing: {resource}")
    validation_path = getattr(module, "VALIDATION_PATH", None)
    if not isinstance(validation_path, Path) or not validation_path.is_file():
        raise CandidateV6Error(f"Wave 11 validation artifact is missing: {resource}")
    return module


def require_transfer_count(metrics: Mapping[str, Any], resource: str) -> int:
    values: set[int] = set()
    direct = metrics.get("entry_count")
    if isinstance(direct, int) and not isinstance(direct, bool) and direct >= 0:
        values.add(direct)
    candidate = metrics.get("candidate")
    if isinstance(candidate, Mapping):
        changed = candidate.get("changed_entry_count")
        if isinstance(changed, int) and not isinstance(changed, bool) and changed >= 0:
            values.add(changed)
    if len(values) != 1:
        raise CandidateV6Error(f"Wave 11 transfer count is ambiguous: {resource}")
    return next(iter(values))


def source_free_json_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    try:
        parsed = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateV6Error(f"invalid public validation JSON: {path}") from exc
    if not isinstance(parsed, dict):
        raise CandidateV6Error(f"validation JSON root is not an object: {path}")
    return {"path": path.relative_to(REPO).as_posix(), **blob_spec(blob)}


def build_wave_component(
    module: Any,
    stock_root: Path,
    expected_predecessor: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    resource = str(module.RESOURCE)
    source = stock_root / Path(resource)
    source_before = path_spec(source)
    require_equal(source_before, dict(expected_predecessor), f"Steam stock pin {resource}")
    switch_zip = module.DEFAULT_SWITCH_ZIP
    switch_before = path_spec(switch_zip)
    candidate, metrics = module.build_blob(stock_root, switch_zip)
    if not isinstance(candidate, bytes) or not isinstance(metrics, Mapping):
        raise CandidateV6Error(f"Wave 11 build result is malformed: {resource}")
    if metrics.get("resource") != resource:
        raise CandidateV6Error(f"Wave 11 reported a different resource: {resource}")
    candidate_spec = require_module_pin(
        module.EXPECTED_CANDIDATE, candidate, f"Wave 11 candidate {resource}"
    )
    reported = metrics.get("candidate")
    if not isinstance(reported, Mapping):
        raise CandidateV6Error(f"Wave 11 candidate metadata is absent: {resource}")
    require_module_pin(reported, candidate, f"Wave 11 reported candidate {resource}")
    verified = module.verify(stock_root, switch_zip)
    if not isinstance(verified, Mapping) or verified.get("status") != "PASS":
        raise CandidateV6Error(f"Wave 11 validation did not pass: {resource}")
    require_equal(path_spec(source), source_before, f"Steam stock unchanged {resource}")
    require_equal(path_spec(switch_zip), switch_before, f"Switch input unchanged {resource}")
    wave_delta = metrics.get("wave11_safe_entries")
    if not isinstance(wave_delta, int) or isinstance(wave_delta, bool) or wave_delta < 0:
        wave_delta = metrics.get("wave11", {}).get("safe_entry_count") if isinstance(metrics.get("wave11"), Mapping) else None
    if not isinstance(wave_delta, int) or isinstance(wave_delta, bool) or wave_delta < 0:
        raise CandidateV6Error(f"Wave 11 delta count is absent: {resource}")
    return candidate, {
        "workstream": module.__name__,
        "resource": resource,
        "validation": source_free_json_spec(module.VALIDATION_PATH),
        "builder_source_sha256": WAVE11_BUILDER_SHA256[resource],
        "stock_predecessor": source_before,
        "candidate": candidate_spec,
        "module_expected_candidate_pin": dict(module.EXPECTED_CANDIDATE),
        "switch_v13_zip": switch_before,
        "transferred_entry_count": require_transfer_count(metrics, resource),
        "wave11_delta_entry_count": wave_delta,
        "metrics": dict(metrics),
    }


def replace_candidate(candidate_root: Path, relative: str, replacement: bytes) -> None:
    destination = candidate_root / Path(relative)
    if not destination.is_file():
        raise CandidateV6Error(f"baseline candidate target is missing: {relative}")
    temporary = destination.with_name(destination.name + ".v6.tmp")
    if temporary.exists():
        raise CandidateV6Error(f"unsafe pre-existing temporary path: {temporary}")
    temporary.write_bytes(replacement)
    try:
        require_equal(path_spec(temporary), blob_spec(replacement), f"replacement pin {relative}")
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def assert_unchanged_v08_targets(
    candidates: Mapping[str, Mapping[str, Any]], v5_verification: Mapping[str, Any]
) -> None:
    for relative in TARGETS:
        if relative not in REPLACED_RESOURCES:
            require_equal(
                candidates[relative],
                v5_verification["candidates"][relative],
                f"v0.8 retained candidate pin {relative}",
            )


def snapshot_live_resources(live_game_root: Path | None) -> dict[str, dict[str, Any]] | None:
    """Record every file this flow must never change, including both EXEs."""

    if live_game_root is None:
        return None
    root = live_game_root.resolve(strict=True)
    if not root.is_dir():
        raise CandidateV6Error(f"live game root is not a directory: {root}")
    return {relative: path_spec(root / Path(relative)) for relative in LIVE_GUARD_PATHS}


def assert_live_resources_unchanged(
    live_game_root: Path | None, before: Mapping[str, Mapping[str, Any]] | None
) -> None:
    if live_game_root is None:
        if before is not None:
            raise CandidateV6Error("unexpected live-resource guard state")
        return
    if before is None:
        raise CandidateV6Error("live-resource guard snapshot is absent")
    root = live_game_root.resolve(strict=True)
    after = {relative: path_spec(root / Path(relative)) for relative in LIVE_GUARD_PATHS}
    require_equal(after, dict(before), "live Steam resource/EXE pre-post guard")


def assert_zip_matches(candidate_root: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as archive:
        if archive.namelist() != list(TARGETS):
            raise CandidateV6Error("ZIP member vector is not exact fourteen-file JP order")
        for relative in TARGETS:
            if archive.read(relative) != (candidate_root / Path(relative)).read_bytes():
                raise CandidateV6Error(f"ZIP payload differs from candidate: {relative}")


def make_zip(candidate_root: Path, destination: Path) -> dict[str, Any]:
    """Write and re-read the exact-fourteen JP vector without importing v5 code."""

    candidate_paths(candidate_root)
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        for relative in TARGETS:
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (candidate_root / Path(relative)).read_bytes())
    assert_zip_matches(candidate_root, destination)
    return path_spec(destination)


def verification_projection(manifest: Mapping[str, Any]) -> dict[str, Any]:
    components = manifest["components"]
    msggame = components["base_msggame_wave11"]
    ev_strdata = components["base_ev_strdata_wave11"]
    translation = dict(manifest["v0_8_translation"])
    translation.update(
        {
            "base_msggame_switch_v13_transferred_entries": msggame["transferred_entry_count"],
            "base_msggame_wave11_safe_delta_entries": msggame["wave11_delta_entry_count"],
            "base_ev_strdata_switch_v13_transferred_entries": ev_strdata["transferred_entry_count"],
            "base_ev_strdata_wave11_safe_delta_entries": ev_strdata["wave11_delta_entry_count"],
        }
    )
    return {
        "schema": VERIFICATION_SCHEMA,
        "runtime": manifest["runtime"],
        "candidate_file_count": manifest["candidate_file_count"],
        "candidate_paths": manifest["candidate_paths"],
        "predecessors": manifest["predecessors"],
        "candidates": manifest["candidates"],
        "translation": translation,
        "provenance": {
            "v0_8_baseline": components["v0_8_baseline"],
            "base_msggame_wave11": msggame,
            "base_ev_strdata_wave11": ev_strdata,
            "fonts": components["fonts"],
        },
        "zip": manifest["zip"],
        "checks": dict(manifest["checks"]),
    }


def _build_staged(
    baseline_zip: Path,
    stock_root: Path,
    staging: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    v5_verification = load_v5_verification()
    candidate_root = materialize_baseline(baseline_zip, staging, v5_verification)
    msggame_module = load_wave_module(
        "nobu16_base_msggame_wave11_v6", MSGGAME_WAVE11_PATH, BASE_MSGGAME_RESOURCE
    )
    ev_strdata_module = load_wave_module(
        "nobu16_base_ev_strdata_wave11_v6", EV_STRDATA_WAVE11_PATH, BASE_EV_STRDATA_RESOURCE
    )
    msggame_blob, msggame_meta = build_wave_component(
        msggame_module, stock_root, v5_verification["predecessors"][BASE_MSGGAME_RESOURCE]
    )
    ev_strdata_blob, ev_strdata_meta = build_wave_component(
        ev_strdata_module, stock_root, v5_verification["predecessors"][BASE_EV_STRDATA_RESOURCE]
    )
    replace_candidate(candidate_root, BASE_MSGGAME_RESOURCE, msggame_blob)
    replace_candidate(candidate_root, BASE_EV_STRDATA_RESOURCE, ev_strdata_blob)
    candidates = candidate_specs(candidate_root)
    assert_unchanged_v08_targets(candidates, v5_verification)
    require_equal(
        candidates[BASE_MSGGAME_RESOURCE], msggame_meta["candidate"], "Wave 11 msggame candidate pin"
    )
    require_equal(
        candidates[BASE_EV_STRDATA_RESOURCE], ev_strdata_meta["candidate"], "Wave 11 ev_strdata candidate pin"
    )
    zip_path = staging / DEFAULT_ZIP_NAME
    zip_spec = make_zip(candidate_root, zip_path)
    manifest = {
        "schema": SCHEMA,
        "runtime": dict(v5_verification["runtime"]),
        "candidate_root": "candidate",
        "candidate_file_count": len(TARGETS),
        "candidate_paths": list(TARGETS),
        "predecessors": {
            relative: dict(v5_verification["predecessors"][relative]) for relative in TARGETS
        },
        "candidates": {relative: candidates[relative] for relative in TARGETS},
        "v0_8_translation": dict(v5_verification["translation"]),
        "components": {
            "v0_8_baseline": {
                "release_asset": dict(BASELINE_RELEASE_PIN),
                "verification": {
                    "path": V5_VERIFICATION_PATH.relative_to(REPO).as_posix(),
                    "sha256": V5_VERIFICATION_SHA256,
                },
                "replaced_resources": list(REPLACED_RESOURCES),
                "retained_v0_8_target_count": len(TARGETS) - len(REPLACED_RESOURCES),
                "candidate_payloads_verified_exact": True,
            },
            "base_msggame_wave11": msggame_meta,
            "base_ev_strdata_wave11": ev_strdata_meta,
            "fonts": dict(v5_verification["provenance"]["fonts"]),
        },
        "zip": {"name": DEFAULT_ZIP_NAME, **zip_spec, "member_count": len(TARGETS)},
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "jp_route_exact": True,
            "exact_fourteen_files": True,
            "v0_8_release_baseline_exact": True,
            "twelve_v0_8_targets_retained_exact": True,
            "base_msggame_wave11_270_integrated": True,
            "base_ev_strdata_wave11_40_integrated": True,
            "msgstf_ce_credits_not_modified": True,
            "high_resolution_seoul_hangang_four_routes_exact": True,
            "zip_payloads_equal_candidates": True,
            "staged_before_promote": True,
            "sc_container_used": False,
            "memory_patch": False,
            "dll_injection": False,
            "hooking": False,
            "exe_or_registry_modified": False,
            "steam_files_written": False,
            "live_game_resource_pre_post_guard": True,
        },
    }
    projection = verification_projection(manifest)
    (staging / "candidate_manifest.v6.json").write_bytes(canonical_json_bytes(manifest))
    return manifest, projection


def build_staged(
    baseline_zip: Path,
    stock_root: Path,
    staging: Path,
    live_game_root: Path | None = DEFAULT_LIVE_GAME_ROOT,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build offline while proving the live Steam resource and EXE vector stayed fixed."""

    before = snapshot_live_resources(live_game_root)
    try:
        return _build_staged(baseline_zip, stock_root, staging)
    finally:
        assert_live_resources_unchanged(live_game_root, before)


def validate_destination(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise CandidateV6Error(f"output must be below repository tmp: {resolved}")
    if resolved.exists():
        raise CandidateV6Error(f"output already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def staged_build(
    baseline_zip: Path,
    stock_root: Path,
    destination_parent: Path,
    live_game_root: Path | None,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    staging = Path(tempfile.mkdtemp(prefix=".steam-jp-117-v6-", dir=destination_parent))
    try:
        manifest, projection = build_staged(
            baseline_zip, stock_root, staging, live_game_root
        )
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return staging, manifest, projection


def load_tracked_verification() -> dict[str, Any]:
    if not VERIFICATION_PATH.is_file():
        raise CandidateV6Error("tracked v6 verification is missing")
    blob = VERIFICATION_PATH.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateV6Error("invalid tracked v6 verification JSON") from exc
    if not isinstance(value, dict) or value.get("schema") != VERIFICATION_SCHEMA:
        raise CandidateV6Error("tracked v6 verification schema changed")
    if blob != canonical_json_bytes(value):
        raise CandidateV6Error("tracked v6 verification formatting changed")
    return value


def atomic_write(path: Path, blob: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise CandidateV6Error(f"unsafe pre-existing temporary path: {temporary}")
    temporary.write_bytes(blob)
    try:
        require_equal(path_spec(temporary), blob_spec(blob), "temporary output pin")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def command_bootstrap(args: argparse.Namespace) -> int:
    proposal = validate_destination(args.proposal)
    staging, _manifest, projection = staged_build(
        args.baseline_zip.resolve(), args.stock_root.resolve(), proposal.parent,
        args.live_game_root.resolve(),
    )
    try:
        atomic_write(proposal, canonical_json_bytes(projection))
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    print(f"proposal={proposal}")
    print(f"proposal_sha256={path_spec(proposal)['sha256']}")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    scratch = validate_destination(args.scratch_root)
    scratch.mkdir(parents=False)
    try:
        staging, _manifest, projection = staged_build(
            args.baseline_zip.resolve(), args.stock_root.resolve(), scratch,
            args.live_game_root.resolve(),
        )
        try:
            require_equal(projection, expected, "integrated v6 verification")
        finally:
            shutil.rmtree(staging, ignore_errors=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("status=PASS")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    output = validate_destination(args.output_root)
    staging, manifest, projection = staged_build(
        args.baseline_zip.resolve(), args.stock_root.resolve(), output.parent,
        args.live_game_root.resolve(),
    )
    try:
        require_equal(projection, expected, "integrated v6 verification")
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
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
    parser.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
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
    except (CandidateV6Error, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
