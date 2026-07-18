#!/usr/bin/env python3
"""Build a pinned three-record PC dialogue/tutorial cleanup without touching Steam.

Wave 6 deliberately layers on the installed Wave 5 profile.  It does not
reopen Wave 5's broad runtime holds: each edit here pins its current Korean
record, its pristine PC Japanese counterpart, all opaque spans, literal-only
layout measurements, and the whole post-build profile.
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
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
WAVE5_SCRIPT = REPO / "workstreams" / "pc_dialogue_quality_wave5_v1" / "build_pc_dialogue_quality_wave5_v1.py"
AUDIT_PATH = WORKSTREAM / "audit_pc_direct_static_cleanup.v1.json"
RESOURCE = "MSG_PK/JP/msggame.bin"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"
SCHEMA = "nobu16.kr.pc-dialogue-quality-wave6.v1"


class Wave6Error(ValueError):
    """A source, layout, or byte-preservation contract failed."""


def load_wave5():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave5_for_wave6", WAVE5_SCRIPT)
    if spec is None or spec.loader is None:
        raise Wave6Error(f"cannot load Wave 5 builder: {WAVE5_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE5 = load_wave5()
WAVE4 = WAVE5.WAVE4
PROFILE_PATHS = tuple(WAVE5.PROFILE_PATHS)
CHANGED_PATHS = (RESOURCE,)
INPUT_SHA256 = dict(WAVE5.TARGET_SHA256)
TARGET_SHA256 = {**INPUT_SHA256, RESOURCE: "CE56A3C6577929513FFEEDFB71637316AA41822DC6F7B26749A6276D572CDF0A"}
EXPECTED_COORDINATES = ((2, 314), (2, 315), (13, 583))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_audit() -> dict[str, Any]:
    try:
        document = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Wave6Error(f"cannot read Wave 6 audit: {exc}") from exc
    if not isinstance(document, dict):
        raise Wave6Error("Wave 6 audit must be an object")
    return document


def parse_coordinate(value: object) -> tuple[int, int]:
    if not isinstance(value, str):
        raise Wave6Error(f"invalid coordinate: {value!r}")
    try:
        block, record = value.split(":", 1)
        return int(block), int(record)
    except ValueError as exc:
        raise Wave6Error(f"invalid coordinate: {value!r}") from exc


def literal_tuple(record: Any) -> tuple[str, ...]:
    return tuple(item.text for item in WAVE4.parse_record_literals(record))


def opaque_schema(record: Any) -> tuple[str, ...]:
    return tuple(WAVE5.opaque_schema(record))


def literal_layout(literals: tuple[str, ...], advance: Any) -> dict[str, object]:
    text = "".join(literals)
    widths = [sum(advance(character) for character in line) for line in text.split("\n")]
    return {"line_count": len(widths), "widths_px": widths}


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave6Error(f"{label} escapes allowed root: {resolved_path}") from exc
    return resolved_path


def require_tmp_path(path: Path, label: str) -> Path:
    return require_under(REPO / "tmp" / WORKSTREAM.name, path, label)


def profile_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = require_under(root, root / relative, f"profile resource {relative}")
        if not path.is_file():
            raise Wave6Error(f"profile resource is absent: {relative}")
        hashes[relative] = sha256_path(path)
    return hashes


def assert_profile(root: Path, expected: dict[str, str], label: str) -> None:
    actual = profile_hashes(root)
    if actual != expected:
        mismatches = {
            path: {"actual": actual.get(path), "expected": expected.get(path)}
            for path in PROFILE_PATHS
            if actual.get(path) != expected.get(path)
        }
        raise Wave6Error(f"{label} profile differs: {json.dumps(mismatches, sort_keys=True)}")


def validate_contracts(steam_root: Path) -> tuple[dict[str, Any], tuple[Any, ...]]:
    audit = read_audit()
    if audit.get("schema") != "nobu16.kr.pc-dialogue-quality-wave6.direct-static-cleanup.v1":
        raise Wave6Error("Wave 6 audit schema differs")
    scope = audit.get("scope")
    inputs = audit.get("input")
    output = audit.get("output")
    rows = audit.get("records")
    if not isinstance(scope, dict) or scope.get("resource") != RESOURCE:
        raise Wave6Error("Wave 6 audit resource differs")
    if not isinstance(inputs, dict) or not isinstance(output, dict) or not isinstance(rows, list):
        raise Wave6Error("Wave 6 audit sections are malformed")
    if inputs.get("steam_file_sha256") != INPUT_SHA256[RESOURCE]:
        raise Wave6Error("Wave 6 audit Steam input hash differs")
    if output.get("steam_file_sha256") != TARGET_SHA256[RESOURCE]:
        raise Wave6Error("Wave 6 audit target hash differs")
    source_path, source_file_hash = WAVE4.WAVE3.PRISTINE_SOURCES[RESOURCE]
    if inputs.get("pristine_pc_jp_file_sha256") != source_file_hash:
        raise Wave6Error("Wave 6 audit PC Japanese source hash differs")
    if sha256_path(source_path) != source_file_hash:
        raise Wave6Error("pristine PC Japanese file hash differs")

    source_records = WAVE4.records_by_coordinate(source_path.read_bytes())
    target_path = require_under(steam_root, steam_root / RESOURCE, "Steam target")
    target_records = WAVE4.records_by_coordinate(target_path.read_bytes())
    advance = WAVE5.validate_event_pk_font_support(steam_root)
    plans: list[Any] = []
    coordinates: list[tuple[int, int]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise Wave6Error("Wave 6 audit record is not an object")
        coordinate = parse_coordinate(row.get("coordinate"))
        coordinates.append(coordinate)
        current = target_records.get(coordinate)
        source = source_records.get(coordinate)
        if current is None or source is None:
            raise Wave6Error(f"missing current or PC Japanese record at {coordinate}")
        expected_current_hash = row.get("current_record_sha256")
        expected_output_hash = row.get("output_record_sha256")
        if not isinstance(expected_current_hash, str) or not isinstance(expected_output_hash, str):
            raise Wave6Error(f"record hash contract is absent at {coordinate}")
        if sha256_bytes(current.data) != expected_current_hash:
            raise Wave6Error(f"current record hash differs at {coordinate}")
        current_literals = tuple(row.get("current_literals", ()))
        output_literals = tuple(row.get("output_literals", ()))
        if literal_tuple(current) != current_literals:
            raise Wave6Error(f"current literal tuple differs at {coordinate}")
        if len(current_literals) != len(output_literals):
            raise Wave6Error(f"literal tuple length differs at {coordinate}")
        expected_schema = tuple(row.get("current_opaque_schema", ()))
        if opaque_schema(current) != expected_schema:
            raise Wave6Error(f"current opaque schema differs at {coordinate}")
        if WAVE4.opaque_commands(current):
            raise Wave6Error(f"unexpected 0143 command at {coordinate}")
        if row.get("current_0143_commands") != []:
            raise Wave6Error(f"audit 0143 contract differs at {coordinate}")
        expected_source_hash = row.get("pristine_pc_jp_record_sha256")
        if sha256_bytes(source.data) != expected_source_hash:
            raise Wave6Error(f"PC Japanese record hash differs at {coordinate}")
        if literal_tuple(source) != tuple(row.get("pristine_pc_jp_literals", ())):
            raise Wave6Error(f"PC Japanese literals differ at {coordinate}")
        if opaque_schema(source) != tuple(row.get("pristine_pc_jp_opaque_schema", ())):
            raise Wave6Error(f"PC Japanese opaque schema differs at {coordinate}")

        changes_data = row.get("literal_changes")
        if not isinstance(changes_data, list) or not changes_data:
            raise Wave6Error(f"literal-change contract is absent at {coordinate}")
        changes: list[Any] = []
        seen_literal_ids: set[int] = set()
        for change in changes_data:
            if not isinstance(change, dict) or not isinstance(change.get("literal_id"), int):
                raise Wave6Error(f"literal-change contract is malformed at {coordinate}")
            literal_id = change["literal_id"]
            if literal_id in seen_literal_ids or literal_id < 0 or literal_id >= len(current_literals):
                raise Wave6Error(f"literal-change ID differs at {coordinate}")
            seen_literal_ids.add(literal_id)
            before = change.get("current")
            replacement = change.get("replacement")
            if current_literals[literal_id] != before or output_literals[literal_id] != replacement:
                raise Wave6Error(f"literal-change text differs at {coordinate}/{literal_id}")
            changes.append(WAVE4.change(literal_id, before, replacement))
        if not any(before != after for before, after in zip(current_literals, output_literals)):
            raise Wave6Error(f"no literal change at {coordinate}")
        if {change.literal_id for change in changes} != {
            index for index, (before, after) in enumerate(zip(current_literals, output_literals)) if before != after
        }:
            raise Wave6Error(f"audit does not account for every changed literal at {coordinate}")
        layout = row.get("literal_only_layout")
        if not isinstance(layout, dict) or not isinstance(layout.get("before"), dict) or not isinstance(layout.get("after"), dict):
            raise Wave6Error(f"literal layout contract is absent at {coordinate}")
        if literal_layout(current_literals, advance) != layout["before"]:
            raise Wave6Error(f"current literal layout differs at {coordinate}")
        if literal_layout(output_literals, advance) != layout["after"]:
            raise Wave6Error(f"output literal layout differs at {coordinate}")
        if layout["before"]["line_count"] != layout["after"]["line_count"]:
            raise Wave6Error(f"manual line count changes at {coordinate}")
        plans.append(WAVE4.plan(coordinate[0], coordinate[1], expected_current_hash, tuple(changes)))
        if expected_output_hash != row.get("output_record_sha256"):
            raise Wave6Error(f"output record hash contract differs at {coordinate}")
    if tuple(coordinates) != EXPECTED_COORDINATES:
        raise Wave6Error(f"Wave 6 coordinate set differs: {coordinates}")
    return audit, tuple(plans)


def rebuild_resource(packed: bytes, audit: dict[str, Any], plans: tuple[Any, ...]) -> bytes:
    before = WAVE4.records_by_coordinate(packed)
    replacements: dict[tuple[int, int], bytes] = {}
    expected_opaque: dict[tuple[int, int], bytes] = {}
    rows_by_coordinate = {parse_coordinate(row["coordinate"]): row for row in audit["records"]}
    for plan in plans:
        record = before.get(plan.coordinate)
        if record is None:
            raise Wave6Error(f"missing input record {plan.coordinate}")
        literals = {item.literal_id: item.text for item in WAVE4.parse_record_literals(record)}
        literal_replacements = {change.literal_id: change.replacement for change in plan.changes}
        for change in plan.changes:
            if literals.get(change.literal_id) != change.expected_text:
                raise Wave6Error(f"input literal differs at {plan.coordinate}/{change.literal_id}")
        expected_opaque[plan.coordinate] = WAVE4.opaque_bytes(record)
        replacements[plan.coordinate] = WAVE4.rebuild_quality_record(record, plan, literal_replacements)
    rebuilt = WAVE4.rebuild_packed_msggame(packed, replacements)
    after = WAVE4.records_by_coordinate(rebuilt)
    if set(before) != set(after):
        raise Wave6Error("record topology changed")
    changed: set[tuple[int, int]] = set()
    for coordinate, record in before.items():
        current = after[coordinate]
        if current.data != record.data:
            changed.add(coordinate)
        expected = replacements.get(coordinate, record.data)
        if current.data != expected:
            raise Wave6Error(f"unexpected record bytes at {coordinate}")
    if changed != set(EXPECTED_COORDINATES):
        raise Wave6Error(f"changed record set differs: {sorted(changed)}")
    for plan in plans:
        row = rows_by_coordinate[plan.coordinate]
        output_record = after[plan.coordinate]
        if sha256_bytes(output_record.data) != row["output_record_sha256"]:
            raise Wave6Error(f"output record hash differs at {plan.coordinate}")
        if opaque_schema(output_record) != tuple(row["current_opaque_schema"]):
            raise Wave6Error(f"output opaque schema differs at {plan.coordinate}")
        if WAVE4.opaque_bytes(output_record) != expected_opaque[plan.coordinate]:
            raise Wave6Error(f"opaque bytes changed at {plan.coordinate}")
        if WAVE4.opaque_commands(output_record):
            raise Wave6Error(f"output contains 0143 command at {plan.coordinate}")
        if literal_tuple(output_record) != tuple(row["output_literals"]):
            raise Wave6Error(f"output literals differ at {plan.coordinate}")
    return rebuilt


def build_candidate(steam_root: Path, output_root: Path, manifest_path: Path) -> dict[str, Any]:
    steam_root = steam_root.resolve(strict=True)
    output_root = require_tmp_path(output_root, "candidate output")
    manifest_path = require_tmp_path(manifest_path, "manifest output")
    if output_root.exists():
        raise Wave6Error(f"candidate output already exists: {output_root}")
    assert_profile(steam_root, INPUT_SHA256, "Steam input")
    audit, plans = validate_contracts(steam_root)
    source = (steam_root / RESOURCE).read_bytes()
    rebuilt = rebuild_resource(source, audit, plans)
    if sha256_bytes(rebuilt) != TARGET_SHA256[RESOURCE]:
        raise Wave6Error("target resource SHA-256 differs")

    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(require_under(steam_root, steam_root / relative, relative), target)
        (stage / RESOURCE).write_bytes(rebuilt)
        output_hashes = profile_hashes(stage)
        if output_hashes != TARGET_SHA256:
            raise Wave6Error("candidate output profile differs")
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave6-v1",
            "changed_paths": list(CHANGED_PATHS),
            "input_sha256": INPUT_SHA256,
            "output_sha256": output_hashes,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_path": str(AUDIT_PATH.relative_to(REPO)).replace("\\", "/"),
            "audit_sha256": sha256_path(AUDIT_PATH),
            "records": [
                {
                    "coordinate": row["coordinate"],
                    "kind": row["kind"],
                    "output_record_sha256": row["output_record_sha256"],
                    "visual_qa_required": bool(row.get("visual_qa_required", False)),
                }
                for row in audit["records"]
            ],
        }
        os.replace(stage, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build a pinned candidate without writing Steam")
    build.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    try:
        output = build_candidate(args.steam_root, args.output_root, args.manifest)
    except (OSError, ValueError, Wave6Error, WAVE4.QualityError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps({"status": "PASS", **output}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
