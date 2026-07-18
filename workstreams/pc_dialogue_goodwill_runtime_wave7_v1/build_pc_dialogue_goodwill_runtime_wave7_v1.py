#!/usr/bin/env python3
"""Build the pinned Wave 7 PC dialogue repair candidate without touching Steam.

Wave 7 is deliberately narrow: it repairs only twelve records independently
proven against the installed PC Japanese source and the current Steam profile.
It never uses a Switch Korean asset.  Runtime faction/facility tokens remain
opaque; a small, pinned subset removes only Japanese ``0143`` inflection
commands that the PC SC/TC (and where present EN) records do not carry.
"""

from __future__ import annotations

import argparse
from collections import Counter
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
WAVE6_SCRIPT = REPO / "workstreams" / "pc_dialogue_quality_wave6_v1" / "build_pc_dialogue_quality_wave6_v1.py"
AUDIT_PATH = WORKSTREAM / "audit_pc_current_static_repairs_wave7.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"
SCHEMA = "nobu16.kr.pc-dialogue-current-static-repairs-wave7.v1"
TRANSACTION_ID = "pc-dialogue-current-static-repairs-wave7-v1"
CHANGED_PATHS = ("MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin")
EXPECTED_COORDINATES = {
    "MSG/JP/msggame.bin": ((6, 1518), (6, 1519), (6, 1520)),
    "MSG_PK/JP/msggame.bin": (
        (6, 1524),
        (6, 1525),
        (6, 1526),
        (6, 3887),
        (8, 1095),
        (8, 1104),
        (8, 1111),
        (8, 1178),
        (8, 1180),
    ),
}


class Wave7Error(ValueError):
    """A source, profile, layout, or opaque-byte contract failed."""


def load_wave6():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave6_for_wave7", WAVE6_SCRIPT)
    if spec is None or spec.loader is None:
        raise Wave7Error(f"cannot load Wave 6 builder: {WAVE6_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE6 = load_wave6()
WAVE5 = WAVE6.WAVE5
WAVE4 = WAVE6.WAVE4
PROFILE_PATHS = tuple(WAVE6.PROFILE_PATHS)
INPUT_SHA256 = dict(WAVE6.TARGET_SHA256)
TARGET_SHA256 = {
    **INPUT_SHA256,
    "MSG/JP/msggame.bin": "83C4DF9326DB1487707FDABE9CF2A00380144D14D3AC4A4FCD02513C8E3C279E",
    "MSG_PK/JP/msggame.bin": "31950B8213AC80C9BCB866163EE7B4B655440ADF863DED21186273E3F8A34BDB",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave7Error(f"{label} escapes allowed root: {resolved_path}") from exc
    return resolved_path


def require_tmp_path(path: Path, label: str) -> Path:
    return require_under(REPO / "tmp" / WORKSTREAM.name, path, label)


def profile_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = require_under(root, root / relative, f"profile resource {relative}")
        if not path.is_file():
            raise Wave7Error(f"profile resource is absent: {relative}")
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
        raise Wave7Error(f"{label} profile differs: {json.dumps(mismatches, sort_keys=True)}")


def parse_coordinate(value: object) -> tuple[int, int]:
    if not isinstance(value, str):
        raise Wave7Error(f"invalid coordinate: {value!r}")
    try:
        block, record = value.split(":", 1)
        return int(block), int(record)
    except ValueError as exc:
        raise Wave7Error(f"invalid coordinate: {value!r}") from exc


def literal_tuple(record: Any) -> tuple[str, ...]:
    return tuple(item.text for item in WAVE4.parse_record_literals(record))


def opaque_schema(record: Any) -> tuple[str, ...]:
    return tuple(WAVE5.opaque_schema(record))


def literal_layout(literals: tuple[str, ...], advance: Any) -> dict[str, object]:
    merged = "".join(literals)
    widths = [sum(advance(character) for character in line) for line in merged.split("\n")]
    return {"line_count": len(widths), "widths_px": widths}


def read_audit() -> dict[str, Any]:
    try:
        document = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Wave7Error(f"cannot read Wave 7 audit: {exc}") from exc
    if not isinstance(document, dict):
        raise Wave7Error("Wave 7 audit must be an object")
    if document.get("schema") != "nobu16.kr.pc-dialogue-current-static-repairs-wave7.audit.v1":
        raise Wave7Error("Wave 7 audit schema differs")
    scope = document.get("scope")
    if not isinstance(scope, dict) or scope.get("platform") != "Steam PC":
        raise Wave7Error("Wave 7 audit scope differs")
    if "Switch Korean" not in scope.get("excluded_sources", []):
        raise Wave7Error("Wave 7 audit must explicitly exclude Switch Korean")
    if document.get("input_profile_sha256") != INPUT_SHA256:
        raise Wave7Error("Wave 7 audit input profile differs")
    if document.get("output_profile_sha256") != TARGET_SHA256:
        raise Wave7Error("Wave 7 audit output profile differs")
    rows = document.get("records")
    if not isinstance(rows, list):
        raise Wave7Error("Wave 7 audit records are malformed")
    return document


def expected_remove_commands(row: dict[str, Any]) -> tuple[Any, ...]:
    raw = row.get("remove_0143_commands")
    if not isinstance(raw, list):
        raise Wave7Error(f"missing removal list at {row.get('coordinate')!r}")
    commands: list[Any] = []
    offsets: set[int] = set()
    for item in raw:
        if not isinstance(item, list) or len(item) != 2 or not isinstance(item[0], int) or not isinstance(item[1], str):
            raise Wave7Error(f"invalid removal contract at {row.get('coordinate')!r}")
        if item[0] in offsets:
            raise Wave7Error(f"duplicate removal offset at {row.get('coordinate')!r}")
        offsets.add(item[0])
        commands.append(WAVE4.remove_command(item[0], item[1]))
    return tuple(commands)


def verify_non_japanese_structure(steam_root: Path, resource: str, coordinate: tuple[int, int]) -> None:
    """Prove removal candidates are JP-only inflection, never the runtime token."""
    family = resource.split("/", 1)[0]
    languages = ("SC", "TC") if family == "MSG" else ("EN", "SC", "TC")
    for language in languages:
        path = steam_root / family / language / "msggame.bin"
        if not path.is_file():
            raise Wave7Error(f"missing required PC {language} reference: {path}")
        record = WAVE4.records_by_coordinate(path.read_bytes()).get(coordinate)
        if record is None:
            raise Wave7Error(f"missing PC {language} reference at {resource} {coordinate}")
        if WAVE4.opaque_commands(record):
            raise Wave7Error(f"PC {language} reference retains 0143 at {resource} {coordinate}")


def validate_contracts(steam_root: Path) -> tuple[dict[str, Any], dict[str, tuple[tuple[Any, dict[str, Any]], ...]]]:
    audit = read_audit()
    rows = audit["records"]
    advance = WAVE5.validate_event_pk_font_support(steam_root)
    current_by_resource: dict[str, dict[tuple[int, int], Any]] = {}
    source_by_resource: dict[str, dict[tuple[int, int], Any]] = {}
    grouped: dict[str, list[tuple[Any, dict[str, Any]]]] = {relative: [] for relative in CHANGED_PATHS}
    seen: set[tuple[str, tuple[int, int]]] = set()

    for row in rows:
        if not isinstance(row, dict):
            raise Wave7Error("Wave 7 audit contains a non-object record")
        resource = row.get("resource")
        if resource not in CHANGED_PATHS:
            raise Wave7Error(f"unexpected Wave 7 resource: {resource!r}")
        coordinate = parse_coordinate(row.get("coordinate"))
        key = (resource, coordinate)
        if key in seen:
            raise Wave7Error(f"duplicate Wave 7 coordinate: {resource} {coordinate}")
        seen.add(key)

        if resource not in current_by_resource:
            current_by_resource[resource] = WAVE4.records_by_coordinate((steam_root / resource).read_bytes())
            source_path, source_hash = WAVE4.WAVE3.PRISTINE_SOURCES[resource]
            if sha256_path(source_path) != source_hash:
                raise Wave7Error(f"pristine PC Japanese resource hash differs: {resource}")
            source_by_resource[resource] = WAVE4.records_by_coordinate(source_path.read_bytes())
        current = current_by_resource[resource].get(coordinate)
        source = source_by_resource[resource].get(coordinate)
        if current is None or source is None:
            raise Wave7Error(f"missing current or pristine PC Japanese record at {resource} {coordinate}")

        current_literals = literal_tuple(current)
        output_literals = tuple(row.get("output_literals", ()))
        if not output_literals or len(current_literals) != len(output_literals):
            raise Wave7Error(f"literal topology differs at {resource} {coordinate}")
        if sha256_bytes(current.data) != row.get("current_record_sha256"):
            raise Wave7Error(f"current record hash differs at {resource} {coordinate}")
        if current_literals != tuple(row.get("current_literals", ())):
            raise Wave7Error(f"current literals differ at {resource} {coordinate}")
        if opaque_schema(current) != tuple(row.get("current_opaque_schema", ())):
            raise Wave7Error(f"current opaque schema differs at {resource} {coordinate}")
        if sha256_bytes(source.data) != row.get("pristine_pc_jp_record_sha256"):
            raise Wave7Error(f"pristine PC Japanese record hash differs at {resource} {coordinate}")
        if literal_tuple(source) != tuple(row.get("pristine_pc_jp_literals", ())):
            raise Wave7Error(f"pristine PC Japanese literals differ at {resource} {coordinate}")
        if opaque_schema(source) != tuple(row.get("pristine_pc_jp_opaque_schema", ())):
            raise Wave7Error(f"pristine PC Japanese opaque schema differs at {resource} {coordinate}")

        removals = expected_remove_commands(row)
        actual_commands = WAVE4.opaque_commands(current)
        if removals:
            if tuple(actual_commands) != tuple((item.offset, item.value) for item in removals):
                raise Wave7Error(f"removable 0143 commands differ at {resource} {coordinate}")
            verify_non_japanese_structure(steam_root, resource, coordinate)
        changes = tuple(
            WAVE4.change(index, before, after)
            for index, (before, after) in enumerate(zip(current_literals, output_literals))
            if before != after
        )
        if not changes:
            raise Wave7Error(f"no literal change at {resource} {coordinate}")
        if sum(text.count("\n") for text in current_literals) != sum(text.count("\n") for text in output_literals):
            raise Wave7Error(f"manual line-break count differs at {resource} {coordinate}")
        if literal_layout(output_literals, advance) != row.get("literal_only_layout"):
            raise Wave7Error(f"literal layout differs at {resource} {coordinate}")
        plan = WAVE4.plan(coordinate[0], coordinate[1], row["current_record_sha256"], changes, remove_commands=removals)
        grouped[resource].append((plan, row))

    for resource, expected in EXPECTED_COORDINATES.items():
        actual = tuple(plan.coordinate for plan, _row in grouped[resource])
        if actual != expected:
            raise Wave7Error(f"Wave 7 coordinate set differs for {resource}: {actual}")
    return audit, {resource: tuple(values) for resource, values in grouped.items()}


def rebuild_resource(packed: bytes, plans_and_rows: tuple[tuple[Any, dict[str, Any]], ...], resource: str) -> bytes:
    before = WAVE4.records_by_coordinate(packed)
    replacements: dict[tuple[int, int], bytes] = {}
    for plan, row in plans_and_rows:
        record = before.get(plan.coordinate)
        if record is None:
            raise Wave7Error(f"missing input record {resource} {plan.coordinate}")
        literals = literal_tuple(record)
        literal_replacements = {change.literal_id: change.replacement for change in plan.changes}
        for change in plan.changes:
            if literals[change.literal_id] != change.expected_text:
                raise Wave7Error(f"input literal differs at {resource} {plan.coordinate}/{change.literal_id}")
        replacements[plan.coordinate] = WAVE4.rebuild_quality_record(record, plan, literal_replacements)

    rebuilt = WAVE4.rebuild_packed_msggame(packed, replacements)
    after = WAVE4.records_by_coordinate(rebuilt)
    if set(before) != set(after):
        raise Wave7Error(f"record topology changed in {resource}")
    changed = {coordinate for coordinate, record in before.items() if record.data != after[coordinate].data}
    if changed != set(EXPECTED_COORDINATES[resource]):
        raise Wave7Error(f"changed record set differs in {resource}: {sorted(changed)}")

    for plan, row in plans_and_rows:
        output = after[plan.coordinate]
        if sha256_bytes(output.data) != row["output_record_sha256"]:
            raise Wave7Error(f"output record hash differs at {resource} {plan.coordinate}")
        if literal_tuple(output) != tuple(row["output_literals"]):
            raise Wave7Error(f"output literals differ at {resource} {plan.coordinate}")
        if opaque_schema(output) != tuple(row["output_opaque_schema"]):
            raise Wave7Error(f"output opaque schema differs at {resource} {plan.coordinate}")
        input_record = before[plan.coordinate]
        expected_opaque = WAVE4.expected_opaque_after_removals(input_record, plan)
        if WAVE4.opaque_bytes(output) != expected_opaque:
            raise Wave7Error(f"output opaque bytes differ at {resource} {plan.coordinate}")
        expected_remaining = Counter(value for _offset, value in WAVE4.opaque_commands(input_record))
        for removed in plan.remove_commands:
            expected_remaining[removed.value] -= 1
        if any(count < 0 for count in expected_remaining.values()):
            raise Wave7Error(f"removed command count differs at {resource} {plan.coordinate}")
        actual_remaining = Counter(value for _offset, value in WAVE4.opaque_commands(output))
        if actual_remaining != Counter({value: count for value, count in expected_remaining.items() if count}):
            raise Wave7Error(f"unplanned 0143 command change at {resource} {plan.coordinate}")
    return rebuilt


def build_candidate(steam_root: Path, output_root: Path, manifest_path: Path) -> dict[str, Any]:
    steam_root = steam_root.resolve(strict=True)
    output_root = require_tmp_path(output_root, "candidate output")
    manifest_path = require_tmp_path(manifest_path, "manifest output")
    if output_root.exists():
        raise Wave7Error(f"candidate output already exists: {output_root}")
    assert_profile(steam_root, INPUT_SHA256, "Steam input")
    audit, plans_by_resource = validate_contracts(steam_root)
    rebuilt = {
        resource: rebuild_resource((steam_root / resource).read_bytes(), plans, resource)
        for resource, plans in plans_by_resource.items()
    }
    for resource, value in rebuilt.items():
        if sha256_bytes(value) != TARGET_SHA256[resource]:
            raise Wave7Error(f"target resource SHA-256 differs for {resource}")

    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(require_under(steam_root, steam_root / relative, relative), target)
        for resource, value in rebuilt.items():
            (stage / resource).write_bytes(value)
        output_hashes = profile_hashes(stage)
        if output_hashes != TARGET_SHA256:
            raise Wave7Error("candidate output profile differs")
        manifest = {
            "schema": SCHEMA,
            "transaction_id": TRANSACTION_ID,
            "changed_paths": list(CHANGED_PATHS),
            "input_sha256": INPUT_SHA256,
            "output_sha256": output_hashes,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_path": str(AUDIT_PATH.relative_to(REPO)).replace("\\", "/"),
            "audit_sha256": sha256_path(AUDIT_PATH),
            "records": [
                {
                    "resource": row["resource"],
                    "coordinate": row["coordinate"],
                    "kind": row["kind"],
                    "output_record_sha256": row["output_record_sha256"],
                    "runtime_visual_qa_required": bool(row.get("runtime_visual_qa_required", False)),
                }
                for row in audit["records"]
            ],
        }
        os.replace(stage, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
        manifest = build_candidate(args.steam_root, args.output_root, args.manifest)
    except (OSError, ValueError, Wave7Error, WAVE4.QualityError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps({"status": "PASS", **manifest}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
