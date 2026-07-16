#!/usr/bin/env python3
"""Assemble the immutable Steam PK 1.1.7 JP-route v0.8.0 exact-12 candidate.

The v0.7.0 workstream is imported read-only and remains immutable.  This
wrapper preserves its strdata, msgui, msggame, and four high-resolution Seoul
Hangang font candidates byte-for-byte, while replacing only the five common
message candidates with the reviewed wave08 integration and its 980-entry
Steam-JP officer-surname recovery.

No command writes to the Steam installation.  ``bootstrap`` and ``verify``
stage candidates below the repository ``tmp`` directory and delete the stage;
``build`` retains an exact-12 candidate only after matching the tracked pin.
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
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
V2_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_117_candidate_v2"
    / "build_steam_jp_117_candidate_v2.py"
)
WAVE08_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_common_messages_wave08"
    / "build_wave08_integration.py"
)
V07_VERIFICATION_PATH = (
    REPO / "workstreams" / "steam_jp_117_candidate_v2" / "verification.v2.json"
)
V07_VERIFICATION_SHA256 = (
    "C98F6CDD5A7E1FDAD1F93DE4BCA2C95A47A9DF4D1371EC90A2523F8EFD4F52DD"
)

DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_117_candidate_v3"
DEFAULT_ZIP_NAME = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip"
SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-manifest.v3"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-verification.v3"
VERIFICATION_PATH = WORKSTREAM / "verification.v3.json"

EXPECTED_COMMON_APPLIED = 40_581
EXPECTED_WAVE08_SEMANTIC_DELTA = 94
EXPECTED_SURNAME_RECOVERY_DELTA = 980
EXPECTED_WAVE08_REVIEWED_SEMANTIC_GAP_REMAINING = 0
EXPECTED_RETAINED_INTERNAL_DUMMIES = 2
EXPECTED_EXCLUDED_SOURCE_EQUAL_CONTRACT = 1_796
EXPECTED_FORMAT_CONTRACT_BLOCKED = 730
EXPECTED_ALIGNMENT_GAP = 62
EXPECTED_REVIEW_BACKLOG = 792
EXPECTED_SOURCE_UNION_EFFECTIVE = 43_169
OFFICER_SURNAME_ID = 84
OFFICER_GIVEN_NAME_ID = 1_266
OFFICER_SURNAME_KO = "오다 "
OFFICER_GIVEN_NAME_KO = "노부나가"
OFFICER_FULL_NAME_KO = "오다 노부나가"


class CandidateV3Error(RuntimeError):
    """A v0.8.0 dependency, invariant, or immutable pin failed closed."""


def load_module(name: str, path: Path) -> Any:
    if not path.is_file():
        raise CandidateV3Error(f"required integration is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateV3Error(f"cannot import component: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V2 = load_module("nobu16_steam_jp_117_candidate_v3_base", V2_PATH)

STOCK_ROOT = V2.STOCK_ROOT
# The old v0.7 staging directory is not a durable input.  The installed JP
# files are read-only inputs here and must still match the immutable v0.7
# candidate hashes before they can be reused.
DEFAULT_FONT_ROOT = V2.STEAM_ROOT
PORT_TARGETS = V2.PORT_TARGETS
FONT_RESOURCES = V2.FONT_RESOURCES
TARGETS = V2.TARGETS
EXPECTED_TARGETS = V2.EXPECTED_TARGETS
COMMON_FILES = tuple(V2.BASE.COMMON.FILES)
EXPECTED_COMMON_FILES = (
    "msgev.bin",
    "msgdata.bin",
    "msgbre.bin",
    "msgire.bin",
    "msgstf.bin",
)
if COMMON_FILES != EXPECTED_COMMON_FILES:
    raise RuntimeError("v3 common-message resource vector changed")
if TARGETS != EXPECTED_TARGETS or len(TARGETS) != 12:
    raise RuntimeError("v3 exact-twelve target vector changed")

IMMUTABLE_V07_TARGETS = (
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgui.bin",
    "RES_JP/res_lang.bin",
    "RES_JP_PK/res_lang_pk.bin",
    "RES_JP_PK_PORT/res_lang_pk_port1.bin",
    "RES_JP_PK_PORT/res_lang_pk_port2.bin",
)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def load_v07_verification() -> dict[str, Any]:
    value, blob = V2.read_object(V07_VERIFICATION_PATH)
    if sha256(blob) != V07_VERIFICATION_SHA256:
        raise CandidateV3Error("immutable v0.7.0 verification pin changed")
    if value.get("schema") != V2.VERIFICATION_SCHEMA:
        raise CandidateV3Error("immutable v0.7.0 verification schema changed")
    candidates = value.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != set(TARGETS):
        raise CandidateV3Error("immutable v0.7.0 candidate vector changed")
    return value


def load_wave08_integration() -> Any:
    integration = load_module("nobu16_steam_jp_common_wave08_v3", WAVE08_PATH)
    if not callable(getattr(integration, "build_all", None)):
        raise CandidateV3Error("wave08 integration has no build_all(stock_root) interface")
    return integration


def require_int(value: Any, expected: int, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value != expected:
        raise CandidateV3Error(f"{label} changed: {value!r} != {expected}")
    return value


def _observed_candidates(candidates: Mapping[str, bytes]) -> dict[str, dict[str, Any]]:
    if tuple(candidates) != COMMON_FILES:
        raise CandidateV3Error(
            f"wave08 candidate order/vector changed: {tuple(candidates)!r}"
        )
    result: dict[str, dict[str, Any]] = {}
    for name in COMMON_FILES:
        blob = candidates[name]
        if not isinstance(blob, bytes):
            raise CandidateV3Error(f"wave08 candidate is not bytes: {name}")
        result[name] = {"size": len(blob), "sha256": sha256(blob)}
    return result


def _validate_reported_candidate_pins(
    reported: Any, observed: Mapping[str, dict[str, Any]]
) -> None:
    if not isinstance(reported, dict) or set(reported) != set(COMMON_FILES):
        raise CandidateV3Error("wave08 reported candidate vector changed")
    for name in COMMON_FILES:
        row = reported[name]
        if not isinstance(row, dict):
            raise CandidateV3Error(f"wave08 candidate metadata is malformed: {name}")
        if {
            "size": row.get("size"),
            "sha256": row.get("sha256"),
        } != observed[name]:
            raise CandidateV3Error(f"wave08 candidate pin mismatch: {name}")


def build_common(stock_root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Build common messages and prove the representative surname composition."""

    integration = load_wave08_integration()
    result = integration.build_all(stock_root)
    if not isinstance(result, tuple) or len(result) != 2:
        raise CandidateV3Error("wave08 build_all must return (candidates, metadata)")
    candidates, metadata = result
    if not isinstance(candidates, dict) or not isinstance(metadata, dict):
        raise CandidateV3Error("wave08 build_all returned malformed values")
    observed = _observed_candidates(candidates)
    require_int(
        metadata.get("applied_entries"),
        EXPECTED_COMMON_APPLIED,
        "wave08 applied_entries",
    )
    require_int(
        metadata.get("wave08_semantic_delta_entries"),
        EXPECTED_WAVE08_SEMANTIC_DELTA,
        "wave08 semantic delta entries",
    )
    require_int(
        metadata.get("surname_recovery_delta_entries"),
        EXPECTED_SURNAME_RECOVERY_DELTA,
        "officer surname recovery delta entries",
    )
    require_int(
        metadata.get("wave08_reviewed_semantic_gap_remaining"),
        EXPECTED_WAVE08_REVIEWED_SEMANTIC_GAP_REMAINING,
        "wave08 reviewed semantic gap remaining",
    )
    require_int(
        metadata.get("retained_internal_dummy_entries"),
        EXPECTED_RETAINED_INTERNAL_DUMMIES,
        "wave08 retained_internal_dummy_entries",
    )
    require_int(
        metadata.get("excluded_source_equal_contract_entries"),
        EXPECTED_EXCLUDED_SOURCE_EQUAL_CONTRACT,
        "wave08 excluded_source_equal_contract_entries",
    )
    require_int(
        metadata.get("format_contract_blocked_entries"),
        EXPECTED_FORMAT_CONTRACT_BLOCKED,
        "common-message format-contract blocked entries",
    )
    require_int(
        metadata.get("alignment_gap_entries"),
        EXPECTED_ALIGNMENT_GAP,
        "common-message alignment-gap entries",
    )
    require_int(
        metadata.get("review_backlog_entries"),
        EXPECTED_REVIEW_BACKLOG,
        "common-message review backlog entries",
    )
    require_int(
        metadata.get("source_union_effective_entries"),
        EXPECTED_SOURCE_UNION_EFFECTIVE,
        "common-message source-union effective entries",
    )
    accounted = (
        metadata["applied_entries"]
        + metadata["excluded_source_equal_contract_entries"]
        + metadata["format_contract_blocked_entries"]
        + metadata["alignment_gap_entries"]
    )
    if accounted != metadata["source_union_effective_entries"]:
        raise CandidateV3Error(
            "common-message accounting identity changed: "
            f"{accounted} != {metadata['source_union_effective_entries']}"
        )
    _validate_reported_candidate_pins(metadata.get("candidates"), observed)
    common = getattr(integration, "COMMON", None)
    if common is None:
        raise CandidateV3Error("wave08 integration has no common-message parser")
    _wrapper, msgdata_raw = common.decompress_wrapper(candidates["msgdata.bin"])
    msgdata = common.parse_message_table(msgdata_raw)
    surname = msgdata.texts[OFFICER_SURNAME_ID]
    given_name = msgdata.texts[OFFICER_GIVEN_NAME_ID]
    if (
        surname != OFFICER_SURNAME_KO
        or given_name != OFFICER_GIVEN_NAME_KO
        or surname + given_name != OFFICER_FULL_NAME_KO
    ):
        raise CandidateV3Error(
            "Steam-JP officer-name composition probe differs: "
            f"{surname!r} + {given_name!r}"
        )
    normalized = dict(metadata)
    normalized["builder"] = (
        "steam_jp_common_messages_v1+wave08_integration+officer_surnames_v1"
    )
    normalized["officer_name_probe"] = {
        "surname_id": OFFICER_SURNAME_ID,
        "given_name_id": OFFICER_GIVEN_NAME_ID,
        "surname_ko": surname,
        "given_name_ko": given_name,
        "composed_ko": surname + given_name,
        "status": "PASS",
    }
    normalized["candidates"] = {
        name: dict(metadata["candidates"][name]) for name in COMMON_FILES
    }
    return {name: candidates[name] for name in COMMON_FILES}, normalized


def immutable_v07_candidate_pins() -> dict[str, dict[str, Any]]:
    previous = load_v07_verification()["candidates"]
    return {name: dict(previous[name]) for name in IMMUTABLE_V07_TARGETS}


def assert_immutable_v07_candidates(
    candidates: Mapping[str, dict[str, Any]]
) -> None:
    expected = immutable_v07_candidate_pins()
    observed = {name: candidates.get(name) for name in IMMUTABLE_V07_TARGETS}
    if observed != expected:
        changed = [name for name in IMMUTABLE_V07_TARGETS if observed[name] != expected[name]]
        raise CandidateV3Error(
            "v0.7.0 non-common candidate changed: " + ", ".join(changed)
        )


def verification_projection(manifest: dict[str, Any]) -> dict[str, Any]:
    msgui = manifest["components"]["msgui"]
    msggame = manifest["components"]["msggame"]
    common = manifest["components"]["common_messages"]
    strdata = manifest["components"]["strdata"]
    fonts = manifest["components"]["fonts"]
    common_provenance = {
        key: value
        for key, value in common.items()
        if key
        not in {
            "builder",
            "applied_entries",
            "unresolved_entries",
            "wave08_semantic_delta_entries",
            "surname_recovery_delta_entries",
            "wave08_reviewed_semantic_gap_remaining",
            "retained_internal_dummy_entries",
            "excluded_source_equal_contract_entries",
            "format_contract_blocked_entries",
            "alignment_gap_entries",
            "review_backlog_entries",
            "source_union_effective_entries",
            "candidates",
        }
    }
    return {
        "schema": VERIFICATION_SCHEMA,
        "runtime": manifest["runtime"],
        "candidate_file_count": manifest["candidate_file_count"],
        "candidate_paths": manifest["candidate_paths"],
        "predecessors": manifest["predecessors"],
        "candidates": manifest["candidates"],
        "translation": {
            "strdata_applied": strdata["applied_entries"],
            "msgui_mapped": msgui["mapped_entries"],
            "msgui_effective_changes": msgui["effective_changes"],
            "msgui_unmapped": msgui["unmapped_entries"],
            "common_messages_applied": common["applied_entries"],
            "common_messages_wave08_semantic_delta_entries": common[
                "wave08_semantic_delta_entries"
            ],
            "common_messages_surname_recovery_delta_entries": common[
                "surname_recovery_delta_entries"
            ],
            "common_messages_wave08_reviewed_semantic_gap_remaining": common[
                "wave08_reviewed_semantic_gap_remaining"
            ],
            "common_messages_retained_internal_dummy_entries": common[
                "retained_internal_dummy_entries"
            ],
            "common_messages_excluded_source_equal_contract_entries": common[
                "excluded_source_equal_contract_entries"
            ],
            "common_messages_format_contract_blocked_entries": common[
                "format_contract_blocked_entries"
            ],
            "common_messages_alignment_gap_entries": common[
                "alignment_gap_entries"
            ],
            "common_messages_review_backlog_entries": common[
                "review_backlog_entries"
            ],
            "common_messages_source_union_effective_entries": common[
                "source_union_effective_entries"
            ],
            "msggame_applied": msggame["applied_entries"],
            "msggame_remaining_jp_semantic": msggame["remaining_jp_semantic"],
        },
        "provenance": {
            "v0_7_0_verification_sha256": V07_VERIFICATION_SHA256,
            "common_messages_wave08": common_provenance,
            "msgui": {
                key: msgui[key]
                for key in (
                    "foundation_sha256",
                    "supplement_sha256",
                    "supplement_coordinate_sha256",
                    "withheld_audit_sha256",
                    "excluded_id",
                    "excluded_source_jp_utf16le_sha256",
                )
            },
            "msggame": {
                key: msggame[key]
                for key in (
                    "wave07_entries",
                    "wave07_coordinates_sha256",
                    "wave07_unique_source_hash_count",
                    "wave07_contextual_variant_source_count",
                    "wave07_overlays",
                )
            },
            "fonts": fonts["evidence"],
        },
        "zip": manifest["zip"],
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "component_candidate_pins_exact": True,
            "v0_7_0_non_common_candidates_exact": True,
            "high_resolution_seoul_hangang_four_routes_exact": True,
            "wave08_common_messages_integrated": True,
            "officer_surnames_980_integrated": True,
            "officer_name_id84_id1266_composition_verified": True,
            "exact_twelve_files": True,
            "zip_payloads_equal_candidates": True,
            "staged_before_promote": True,
            "sc_container_used": False,
            "steam_files_written": False,
        },
    }


def validate_destination(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise CandidateV3Error(f"output must be below repository tmp: {resolved}")
    if resolved.exists():
        raise CandidateV3Error(f"output already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def build_staged(
    stock_root: Path, port_stock_root: Path, font_root: Path, staging: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    before = V2.predecessor_vector(stock_root, port_stock_root)
    font_evidence = V2.configure_font_candidates(font_root)
    strdata, strdata_meta = V2.BASE.build_strdata(stock_root)
    msgui, msgui_meta = V2.build_msgui(stock_root)
    common, common_meta = build_common(stock_root)
    msggame, msggame_meta = V2.build_msggame(stock_root)

    candidate_root = staging / "candidate"
    candidates: dict[str, dict[str, Any]] = {}
    candidates["MSG/JP/strdata.bin"] = V2.BASE.write_candidate_file(
        candidate_root, "MSG/JP/strdata.bin", strdata
    )
    candidates["MSG_PK/JP/msgui.bin"] = V2.BASE.write_candidate_file(
        candidate_root, "MSG_PK/JP/msgui.bin", msgui
    )
    for name, blob in common.items():
        relative = f"MSG_PK/JP/{name}"
        candidates[relative] = V2.BASE.write_candidate_file(
            candidate_root, relative, blob
        )
    candidates["MSG_PK/JP/msggame.bin"] = V2.BASE.write_candidate_file(
        candidate_root, "MSG_PK/JP/msggame.bin", msggame
    )
    for relative, route in font_evidence["routes"].items():
        source = font_root / Path(relative)
        observed = V2.BASE.copy_candidate_file(candidate_root, relative, source)
        if observed != route:
            raise CandidateV3Error(f"font candidate pin mismatch: {relative}")
        candidates[relative] = observed

    if V2.BASE.candidate_files(candidate_root) != list(TARGETS):
        raise CandidateV3Error("candidate root is not the exact twelve-file vector")
    if set(candidates) != set(TARGETS):
        raise CandidateV3Error("candidate manifest does not cover exact target vector")
    assert_immutable_v07_candidates(candidates)
    if V2.predecessor_vector(stock_root, port_stock_root) != before:
        raise CandidateV3Error("Steam stock vector changed during offline build")

    zip_path = staging / DEFAULT_ZIP_NAME
    if zip_path.parent != staging or zip_path.exists():
        raise CandidateV3Error("unsafe fixed ZIP destination")
    zip_spec = V2.make_zip(candidate_root, zip_path)
    manifest = {
        "schema": SCHEMA,
        "runtime": {
            "distribution": "Steam",
            "pk_version": "1.1.7",
            "steam_build_id": 18_823_764,
            "language_route": "JP",
        },
        "candidate_root": "candidate",
        "candidate_file_count": len(candidates),
        "candidate_paths": list(TARGETS),
        "predecessors": before,
        "candidates": {key: candidates[key] for key in TARGETS},
        "components": {
            "strdata": strdata_meta,
            "msgui": msgui_meta,
            "common_messages": common_meta,
            "msggame": msggame_meta,
            "fonts": {
                "builder": "font_jp_seoulhangang_v1",
                "evidence": font_evidence,
                "routes": {
                    relative: candidates[relative] for relative in FONT_RESOURCES
                },
            },
        },
        "zip": {
            "name": DEFAULT_ZIP_NAME,
            **zip_spec,
            "member_count": len(TARGETS),
        },
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "jp_route_exact": True,
            "exact_twelve_files": True,
            "component_candidate_pins_exact": True,
            "v0_7_0_non_common_candidates_exact": True,
            "high_resolution_seoul_hangang_four_routes_exact": True,
            "wave08_common_messages_integrated": True,
            "officer_surnames_980_integrated": True,
            "officer_name_id84_id1266_composition_verified": True,
            "zip_payloads_equal_candidates": True,
            "staged_before_promote": True,
            "sc_container_used": False,
            "memory_patch": False,
            "dll_injection": False,
            "hooking": False,
            "exe_or_registry_modified": False,
            "steam_files_written": False,
        },
    }
    projection = verification_projection(manifest)
    (staging / "candidate_manifest.v3.json").write_bytes(V2.BASE.json_bytes(manifest))
    return manifest, projection


def staged_build(
    stock_root: Path,
    port_stock_root: Path,
    font_root: Path,
    destination_parent: Path,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    staging = Path(
        tempfile.mkdtemp(prefix=".steam-jp-117-v3-", dir=destination_parent)
    )
    try:
        manifest, projection = build_staged(
            stock_root, port_stock_root, font_root, staging
        )
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return staging, manifest, projection


def load_tracked_verification() -> dict[str, Any]:
    value, _blob = V2.read_object(VERIFICATION_PATH)
    if value.get("schema") != VERIFICATION_SCHEMA:
        raise CandidateV3Error("tracked v3 verification schema changed")
    return value


def command_bootstrap(args: argparse.Namespace) -> int:
    proposal = validate_destination(args.proposal)
    staging, _manifest, projection = staged_build(
        args.stock_root.resolve(),
        args.port_stock_root.resolve(),
        args.font_candidate_root.resolve(),
        proposal.parent,
    )
    try:
        V2.atomic_write(proposal, V2.BASE.json_bytes(projection))
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    print(f"proposal={proposal}")
    print(f"proposal_sha256={V2.BASE.sha256_path(proposal)}")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    parent = validate_destination(args.scratch_root)
    parent.mkdir(parents=False)
    try:
        staging, _manifest, projection = staged_build(
            args.stock_root.resolve(),
            args.port_stock_root.resolve(),
            args.font_candidate_root.resolve(),
            parent,
        )
        try:
            if projection != expected:
                raise CandidateV3Error(
                    "integrated candidate differs from tracked verification pin"
                )
        finally:
            shutil.rmtree(staging, ignore_errors=True)
    finally:
        shutil.rmtree(parent, ignore_errors=True)
    print("status=PASS")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    output = validate_destination(args.output_root)
    staging, manifest, projection = staged_build(
        args.stock_root.resolve(),
        args.port_stock_root.resolve(),
        args.font_candidate_root.resolve(),
        output.parent,
    )
    try:
        if projection != expected:
            raise CandidateV3Error(
                "integrated candidate differs from tracked verification pin"
            )
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    print("status=PASS")
    print(f"steam_pk_version={manifest['runtime']['pk_version']}")
    print(f"steam_build_id={manifest['runtime']['steam_build_id']}")
    print(f"candidate_files={manifest['candidate_file_count']}")
    print(f"zip_name={manifest['zip']['name']}")
    print(f"zip_sha256={manifest['zip']['sha256']}")
    print("steam_files_written=False")
    return 0


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--stock-root", type=Path, default=STOCK_ROOT)
    parser.add_argument(
        "--port-stock-root",
        type=Path,
        required=True,
        help=(
            "directory containing pristine Steam 1.1.7 "
            "res_lang_pk_port1.bin and res_lang_pk_port2.bin"
        ),
    )
    parser.add_argument("--font-candidate-root", type=Path, default=DEFAULT_FONT_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    bootstrap = commands.add_parser(
        "bootstrap", help="emit only a source-free proposed verification pin"
    )
    add_common_arguments(bootstrap)
    bootstrap.add_argument(
        "--proposal",
        type=Path,
        default=REPO / "tmp" / "steam_jp_117_candidate_v3.proposed.json",
    )
    bootstrap.set_defaults(handler=command_bootstrap)

    verify = commands.add_parser(
        "verify", help="rebuild privately and compare with the tracked pin"
    )
    add_common_arguments(verify)
    verify.add_argument(
        "--scratch-root",
        type=Path,
        default=REPO / "tmp" / "steam_jp_117_candidate_v3_verify",
    )
    verify.set_defaults(handler=command_verify)

    build = commands.add_parser(
        "build", help="stage, verify, and retain the exact-twelve candidate"
    )
    add_common_arguments(build)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.set_defaults(handler=command_build)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (
        CandidateV3Error,
        V2.CandidateV2Error,
        V2.BASE.CandidateError,
        OSError,
        ValueError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
