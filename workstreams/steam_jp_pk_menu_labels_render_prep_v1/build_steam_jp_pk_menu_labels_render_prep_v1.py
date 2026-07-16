#!/usr/bin/env python3
"""Prepare, but never build, PC-native Korean render inputs for PK labels.

Only ``RES_JP_PK/res_lang_pk.bin /18`` is in scope: 43 transparent, non-logo
UI/editor labels.  `/3` and `/24` plus every logo/title/brand family are
permanently excluded.  This tool emits source-free wording and evidence
templates; its candidate-build command is intentionally hard-disabled until
per-slot runtime traces and BC3-aligned text rectangles exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPOSITORY = SCRIPT.parents[2]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import build_common_message_overlay as common  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-pk-menu-label-render-prep.v1"
RESOURCE = "RES_JP_PK/res_lang_pk.bin"
TARGET_OUTER = 18
EXCLUDED_OUTERS = (3, 24)
AUDIT_ROOT = REPOSITORY / "workstreams" / "steam_jp_pk_menu_labels_audit_v1"
AUDIT_MANIFEST = AUDIT_ROOT / "manifest.v1.json"
AUDIT_CATALOG = AUDIT_ROOT / "catalog.v1.json"
AUDIT_REPORT = REPOSITORY / "tmp" / "steam_jp_pk_menu_labels_audit_v1" / "run_b" / "audit_report.v1.json"
DEFAULT_PLAN = WORKSTREAM / "public" / "render_prep.v1.json"
DEFAULT_TRACE_TEMPLATE = WORKSTREAM / "public" / "runtime_trace_template.v1.json"
DEFAULT_RECT_TEMPLATE = WORKSTREAM / "public" / "text_rectangle_qa_template.v1.json"
TMP_ROOT = REPOSITORY / "tmp" / "steam_jp_pk_menu_labels_render_prep_v1"
DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

AUDIT_PINS = {
    "manifest": "3B3C8E6B74B4A77803E413F938A25C79FB5C35CC8C7B7DBA4CB43EC7B838CB61",
    "catalog": "515E6EDDC98479E2ADA3F20FC6458C20F3520837875E13F757DCCF476D9E046E",
    "report": "2C6A7500EB4BE0D086BAB0461399F84C7D1B3B80C5E323450D064424E6D63FA9",
}
CATALOG_SCHEMA = "nobu16.kr.steam-jp-pk-menu-labels.catalog.v2"
CATALOG_SLOT_KEYS = {"slot", "input_payload_sha256", "dimensions", "ko_output_utf16le_sha256"}
JP_INPUT_PIN = {"size": 141_746_742, "sha256": "EC758BC9B87F98B42E01CA6F841D963811BB944D113E2C65A1E9F5AE19F1DF08"}
JP_OUTER18_SHA256 = "BCECE33A8EEFFCA19EB2C11DB5C289E89472B85682AD1F8281D100966189F515"
NONLOGO_SLOT_COUNT = 43
REVIEW_SLOTS = frozenset({1, 2, 19})


class RenderPrepError(ValueError):
    pass


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789ABCDEF" for character in value)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        document, blob = common.load_json_strict(path)
    except Exception as exc:
        raise RenderPrepError(f"invalid JSON {path}: {exc}") from exc
    return document, blob


def under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def require_workspace(path: Path) -> None:
    if not under(path, WORKSTREAM):
        raise RenderPrepError(f"metadata output must remain below workstream: {path}")


def require_tmp(path: Path) -> None:
    if not under(path, TMP_ROOT):
        raise RenderPrepError(f"temporary report must remain below {TMP_ROOT}: {path}")


def write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def load_audit_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    paths = {"manifest": AUDIT_MANIFEST, "catalog": AUDIT_CATALOG, "report": AUDIT_REPORT}
    documents: dict[str, dict[str, Any]] = {}
    for name, path in paths.items():
        document, blob = read_json(path)
        if sha256(blob) != AUDIT_PINS[name]:
            raise RenderPrepError(f"audit {name} hash drifted")
        documents[name] = document
    manifest, catalog, report = documents["manifest"], documents["catalog"], documents["report"]
    scope = manifest.get("scope", {})
    if scope.get("target_resource") != RESOURCE or scope.get("target_outer_entry") != TARGET_OUTER:
        raise RenderPrepError("audit target drifted")
    if not set(EXCLUDED_OUTERS).issubset(scope.get("excluded_outer_entries", [])):
        raise RenderPrepError("permanent logo/title exclusions missing")
    if manifest.get("switch_v2_reference", {}).get("pixel_copy_allowed") is not False:
        raise RenderPrepError("Switch pixel copy must remain prohibited")
    outcome = manifest.get("audit_outcome", {})
    if outcome.get("all_43_slots_are_logo_free_ui_or_editor_labels") is not True:
        raise RenderPrepError("non-logo slot audit missing")
    if outcome.get("active_korean_glyph_donor", {}).get("required_catalog_codepoints_covered") is not True:
        raise RenderPrepError("active PC Korean glyph coverage proof missing")
    if (
        catalog.get("schema") != CATALOG_SCHEMA
        or catalog.get("target_resource") != RESOURCE
        or catalog.get("target_outer_entry") != TARGET_OUTER
        or catalog.get("source_free") is not True
    ):
        raise RenderPrepError("catalog target/source-free contract drifted")
    if catalog.get("review_required_slots") != sorted(REVIEW_SLOTS):
        raise RenderPrepError("catalog wording review set drifted")
    entries = catalog.get("slots")
    if not isinstance(entries, list) or [entry.get("slot") for entry in entries] != list(range(NONLOGO_SLOT_COUNT)):
        raise RenderPrepError("catalog slot order/count drifted")
    for entry in entries:
        slot = entry["slot"]
        if set(entry) != CATALOG_SLOT_KEYS or entry.get("dimensions") != [512, 128]:
            raise RenderPrepError(f"catalog source-free row drifted at slot {slot}")
        if not valid_sha256(entry.get("input_payload_sha256")) or not valid_sha256(entry.get("ko_output_utf16le_sha256")):
            raise RenderPrepError(f"catalog hash invalid at slot {slot}")
        report_payload = report.get("slots", [])[slot].get("language_payloads", {}).get("jp", {}).get("payload_sha256")
        if entry["input_payload_sha256"] != report_payload:
            raise RenderPrepError(f"catalog input payload pin drifted at slot {slot}")
    if report.get("target", {}).get("outer_entry") != TARGET_OUTER or report.get("target", {}).get("logo_or_title_art_touched") is not False:
        raise RenderPrepError("audit report exclusion evidence drifted")
    if report.get("inputs", {}).get("jp", {}).get("before") != JP_INPUT_PIN or report["inputs"]["jp"].get("outer_18_sha256") != JP_OUTER18_SHA256:
        raise RenderPrepError("audit report JP pin drifted")
    return manifest, catalog, report


def derive_plan(plan_path: Path, trace_path: Path, rectangle_path: Path) -> dict[str, Any]:
    for path in (plan_path, trace_path, rectangle_path):
        require_workspace(path)
    manifest, catalog, _ = load_audit_inputs()
    slots: list[dict[str, Any]] = []
    trace_slots: list[dict[str, Any]] = []
    rect_slots: list[dict[str, Any]] = []
    for entry in catalog["slots"]:
        slot = entry["slot"]
        korean_hash = entry.get("ko_output_utf16le_sha256")
        if not valid_sha256(korean_hash):
            raise RenderPrepError(f"catalog Korean output hash absent at slot {slot}")
        expected_review = slot in REVIEW_SLOTS
        status = "term_review_needed" if expected_review else "confirmed_term"
        blockers = ["runtime_screen_trace_missing", "text_rectangle_qa_missing"]
        if expected_review:
            blockers.insert(0, "korean_wording_review_required")
        slots.append(
            {
                "slot": slot,
                "input_payload_sha256": entry["input_payload_sha256"],
                "dimensions": entry["dimensions"],
                "proposed_ko_utf16le_sha256": korean_hash,
                "wording_status": status,
                "runtime_trace_status": "missing",
                "text_rectangle_qa_status": "missing",
                "candidate_eligible": False,
                "candidate_blockers": blockers,
            }
        )
        trace_slots.append({"slot": slot, "runtime_screen_id": None, "observed_state": None, "trace_status": "missing"})
        rect_slots.append({"slot": slot, "text_rectangle": None, "bc3_block_aligned": False, "background_preservation_verified": False, "qa_status": "missing"})
    plan = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "target_outer_entry": TARGET_OUTER,
            "selected_slots": list(range(NONLOGO_SLOT_COUNT)),
            "excluded_outer_entries": list(EXCLUDED_OUTERS),
            "excluded_families": ["product_logo", "title_screen_art", "brand_art", "historical_title_cards"],
            "switch_pixel_copy_allowed": False,
            "game_install_write_allowed": False,
            "git_release_github_write_allowed": False,
            "candidate_generation_enabled": False,
        },
        "baseline": {"steam_game_version": "1.1.7", "jp_resource": JP_INPUT_PIN, "jp_outer_18_sha256": JP_OUTER18_SHA256},
        "pc_native_renderer": {
            "font_resource": RESOURCE,
            "font_outer_entry": 16,
            "font_table": 0,
            "font_cell_pixels": 48,
            "glyph_coverage_verified": True,
            "pixel_source": "PC-native rendered Korean only; Switch pixels prohibited",
        },
        "audit_pins": AUDIT_PINS,
        "slot_count": len(slots),
        "confirmed_wording_count": len(slots) - len(REVIEW_SLOTS),
        "wording_review_required_slots": sorted(REVIEW_SLOTS),
        "slots": slots,
        "source_free_guarantees": {"contains_commercial_source_text": False, "contains_plaintext_korean_output": False, "contains_complete_game_resource": False, "contains_switch_pixels": False},
    }
    trace_template = {"schema": "nobu16.kr.steam-jp-pk-menu-runtime-trace-template.v1", "resource": RESOURCE, "outer_entry": TARGET_OUTER, "slots": trace_slots, "all_slots_traced": False}
    rect_template = {"schema": "nobu16.kr.steam-jp-pk-menu-text-rectangle-template.v1", "resource": RESOURCE, "outer_entry": TARGET_OUTER, "slots": rect_slots, "all_slots_qa_complete": False}
    write(plan_path, json_bytes(plan))
    write(trace_path, json_bytes(trace_template))
    write(rectangle_path, json_bytes(rect_template))
    validate_plan(plan_path)
    return {"action": "prepare", "plan": str(plan_path), "plan_sha256": sha256(plan_path.read_bytes()), "slot_count": len(slots), "candidate_generation_enabled": False, "game_install_modified": False, "release_modified": False, "github_modified": False}


def validate_plan(path: Path) -> dict[str, Any]:
    plan, blob = read_json(path)
    if plan.get("schema") != SCHEMA or plan.get("scope", {}).get("resource") != RESOURCE or plan["scope"].get("target_outer_entry") != TARGET_OUTER:
        raise RenderPrepError("plan identity/target mismatch")
    scope = plan["scope"]
    if not set(EXCLUDED_OUTERS).issubset(scope.get("excluded_outer_entries", [])) or scope.get("candidate_generation_enabled") is not False or scope.get("switch_pixel_copy_allowed") is not False:
        raise RenderPrepError("plan safety gate drift")
    if plan.get("baseline", {}).get("jp_resource") != JP_INPUT_PIN or plan["baseline"].get("jp_outer_18_sha256") != JP_OUTER18_SHA256:
        raise RenderPrepError("plan JP baseline drift")
    if plan.get("slot_count") != NONLOGO_SLOT_COUNT or plan.get("wording_review_required_slots") != sorted(REVIEW_SLOTS):
        raise RenderPrepError("plan slot/review count drift")
    slots = plan.get("slots")
    if not isinstance(slots, list) or [entry.get("slot") for entry in slots] != list(range(NONLOGO_SLOT_COUNT)):
        raise RenderPrepError("plan slots invalid")
    _, catalog, _ = load_audit_inputs()
    catalog_slots = catalog["slots"]
    for entry in slots:
        slot = entry.get("slot")
        expected = catalog_slots[slot]
        if "proposed_ko" in entry or entry.get("proposed_ko_utf16le_sha256") != expected["ko_output_utf16le_sha256"]:
            raise RenderPrepError(f"plan Korean output hash invalid at slot {slot}")
        if entry.get("input_payload_sha256") != expected["input_payload_sha256"] or entry.get("dimensions") != expected["dimensions"]:
            raise RenderPrepError(f"plan source metadata invalid at slot {slot}")
        if entry.get("candidate_eligible") is not False or entry.get("runtime_trace_status") != "missing" or entry.get("text_rectangle_qa_status") != "missing":
            raise RenderPrepError(f"plan candidate gate unexpectedly open at slot {slot}")
    if plan.get("source_free_guarantees") != {"contains_commercial_source_text": False, "contains_plaintext_korean_output": False, "contains_complete_game_resource": False, "contains_switch_pixels": False}:
        raise RenderPrepError("source-free guarantee drift")
    if not blob.isascii():
        raise RenderPrepError("plan must remain hash-only ASCII metadata")
    return plan


def preflight(game_root: Path, plan_path: Path, output: Path) -> dict[str, Any]:
    require_tmp(output)
    plan = validate_plan(plan_path)
    target = game_root / RESOURCE
    if not target.is_file():
        raise RenderPrepError(f"missing Steam JP target: {target}")
    blob = target.read_bytes()
    actual = {"size": len(blob), "sha256": sha256(blob)}
    if actual != JP_INPUT_PIN:
        raise RenderPrepError(f"Steam JP input hash drift: {actual}")
    outer = lz4.parse_link(blob)
    if len(outer.entries) != 27 or TARGET_OUTER >= len(outer.entries):
        raise RenderPrepError("Steam JP LINK structure drift")
    if sha256(outer.entries[TARGET_OUTER].data) != JP_OUTER18_SHA256:
        raise RenderPrepError("Steam JP /18 payload drift")
    blockers = {blocker for slot in plan["slots"] for blocker in slot["candidate_blockers"]}
    report = {"schema": "nobu16.kr.steam-jp-pk-menu-label-render-preflight.v1", "target": {"resource": RESOURCE, "outer_entry": TARGET_OUTER, "excluded_outer_entries": list(EXCLUDED_OUTERS)}, "input": actual, "candidate_generation_enabled": False, "candidate_created": False, "global_blockers": sorted(blockers), "all_slots_runtime_traced": False, "all_slots_text_rectangle_qa_complete": False, "switch_pixels_used": False, "game_install_modified": False, "release_modified": False, "github_modified": False}
    write(output, json_bytes(report))
    return report


def build_disabled(_: argparse.Namespace) -> int:
    raise RenderPrepError("candidate build is hard-disabled: runtime traces, approved wording, and BC3 text rectangles are absent; no image resource may be produced")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    prepare.add_argument("--trace-template", type=Path, default=DEFAULT_TRACE_TEMPLATE)
    prepare.add_argument("--rectangle-template", type=Path, default=DEFAULT_RECT_TEMPLATE)
    status = commands.add_parser("preflight")
    status.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    status.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    status.add_argument("--output", type=Path, required=True)
    commands.add_parser("build")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "prepare":
            result = derive_plan(args.plan, args.trace_template, args.rectangle_template)
        elif args.command == "preflight":
            result = preflight(args.game_root, args.plan, args.output)
        else:
            return build_disabled(args)
    except (OSError, RenderPrepError, ValueError, lz4.LZ4Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
