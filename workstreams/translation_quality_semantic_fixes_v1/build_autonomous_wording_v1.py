#!/usr/bin/env python3
"""Freeze/build the verified ``자주적으로`` -> ``자율적으로`` wording fix.

The 24 selected tutorial literals were first paired privately with pristine PC
Japanese originals.  This public builder contains no Japanese source text and
uses source hashes to ensure it only touches the reviewed current Steam text.
It never writes to the Steam installation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "msggame"))

from msggame_format import iter_literals, parse_packed_msggame, rebuild_packed_with_literals  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "translation_quality_semantic_fixes_v1" / "autonomous_wording_candidate"
PUBLIC_OVERLAY = WORKSTREAM / "public" / "autonomous_wording.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.semantic-autonomous-wording-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.semantic-autonomous-wording-validation.v1"
MANIFEST_SCHEMA = "nobu16.kr.semantic-autonomous-wording-build-manifest.v1"
OLD_WORDING = "자주적으로"
NEW_WORDING = "자율적으로"
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")


@dataclass(frozen=True)
class Resource:
    name: str
    relative: str
    coordinates: tuple[tuple[int, int, int], ...]


RESOURCES = (
    Resource(
        "base_msggame",
        "MSG/JP/msggame.bin",
        (
            (13, 275, 0), (13, 360, 0), (13, 483, 0), (13, 505, 0),
            (14, 34, 1), (14, 35, 1), (14, 37, 1), (14, 49, 1),
            (14, 50, 5), (14, 150, 1), (14, 153, 1),
        ),
    ),
    Resource(
        "pk_msggame",
        "MSG_PK/JP/msggame.bin",
        (
            (13, 294, 0), (13, 392, 0), (13, 527, 0), (13, 549, 0),
            (14, 52, 1), (14, 53, 1), (14, 54, 1), (14, 55, 1),
            (14, 57, 1), (14, 72, 1), (14, 73, 5), (14, 209, 1),
            (14, 216, 1),
        ),
    ),
)


class WordingFixError(ValueError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def pretty_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def private_path(path: Path) -> Path:
    value = path.resolve()
    root = (REPO / "tmp").resolve()
    if value == root or root not in value.parents:
        raise WordingFixError(f"output must remain under {root}")
    return value


def profile(text: str) -> dict[str, Any]:
    return {
        "runtime": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "escape": ESC_RE.findall(text),
        "linebreaks": re.findall(r"\r\n|\n|\r", text),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "private_use": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
    }


def resource_data(steam_root: Path, resource: Resource) -> tuple[Path, bytes, dict[tuple[int, int, int], str], dict[str, Any]]:
    path = (steam_root.resolve() / Path(resource.relative)).resolve()
    if not path.is_file():
        raise WordingFixError(f"missing Steam resource: {path}")
    packed = path.read_bytes()
    parsed = parse_packed_msggame(packed)
    _header, raw = decompress_wrapper(packed)
    literals = {(item.block_id, item.record_id, item.literal_id): item.text for item in iter_literals(parsed.archive)}
    expected = set(resource.coordinates)
    if set(resource.coordinates) != expected or len(expected) != len(resource.coordinates):
        raise WordingFixError(f"coordinate contract is duplicated: {resource.name}")
    if not expected.issubset(literals):
        raise WordingFixError(f"reviewed literal is absent: {resource.name}")
    return path, packed, literals, {
        "relative_path": resource.relative,
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "record_count": parsed.archive.record_count,
        "literal_count": len(literals),
    }


def format_coordinate(coordinate: tuple[int, int, int]) -> str:
    return ":".join(str(value) for value in coordinate)


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = value.split(":")
    if len(parts) != 3 or any(not part.isdecimal() for part in parts):
        raise WordingFixError(f"invalid literal coordinate: {value!r}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def assert_public_safe(blob: bytes, label: str) -> None:
    text = blob.decode("utf-8")
    if KANA_OR_HAN_RE.search(text):
        raise WordingFixError(f"{label} retains Japanese/CJK source text")


def freeze(steam_root: Path) -> dict[str, Any]:
    resource_values: list[dict[str, Any]] = []
    for resource in RESOURCES:
        _path, _packed, literals, baseline = resource_data(steam_root, resource)
        entries: list[dict[str, Any]] = []
        for coordinate in resource.coordinates:
            source = literals[coordinate]
            if source.count(OLD_WORDING) < 1:
                raise WordingFixError(f"reviewed wording source changed at {resource.name}:{coordinate}")
            replacement = source.replace(OLD_WORDING, NEW_WORDING)
            if profile(source) != profile(replacement):
                raise WordingFixError(f"format profile differs at {resource.name}:{coordinate}")
            entries.append({
                "coordinate": format_coordinate(coordinate),
                "source_current_utf16le_sha256": text_hash(source),
                "ko": replacement,
                "ko_utf16le_sha256": text_hash(replacement),
                "format_profile_sha256": canonical_hash(profile(source)),
            })
        resource_values.append({"name": resource.name, "baseline": baseline, "entry_count": len(entries), "entries": entries})
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "autonomous_wording.v1",
        "scope": "reviewed PC Korean tutorial wording repair; no Switch Korean translation used",
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "switch_korean_translation_used": False},
        "entry_count": sum(value["entry_count"] for value in resource_values),
        "resources": resource_values,
    }
    blob = pretty_json(overlay)
    assert_public_safe(blob, "overlay")
    atomic_write(PUBLIC_OVERLAY, blob)
    validation = validate_overlay(steam_root, overlay)
    validation_blob = pretty_json(validation)
    assert_public_safe(validation_blob, "validation")
    atomic_write(VALIDATION, validation_blob)
    return {"entry_count": overlay["entry_count"], "overlay_sha256": sha256_bytes(blob), "validation_sha256": sha256_bytes(validation_blob), "steam_installation_written": False}


def load_overlay() -> dict[str, Any]:
    try:
        value = json.loads(PUBLIC_OVERLAY.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WordingFixError("invalid public overlay") from exc
    if not isinstance(value, dict):
        raise WordingFixError("public overlay root is invalid")
    return value


def validate_overlay(steam_root: Path, overlay: Mapping[str, Any] | None = None) -> dict[str, Any]:
    value = overlay if overlay is not None else load_overlay()
    required = {"schema", "overlay_id", "scope", "distribution_policy", "entry_count", "resources"}
    if set(value) != required or value["schema"] != OVERLAY_SCHEMA or value["overlay_id"] != "autonomous_wording.v1":
        raise WordingFixError("overlay header differs")
    policy = {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "switch_korean_translation_used": False}
    if value["distribution_policy"] != policy or not isinstance(value["resources"], list) or len(value["resources"]) != len(RESOURCES):
        raise WordingFixError("overlay policy/resources differ")
    total = 0
    reports: list[dict[str, Any]] = []
    for resource, item in zip(RESOURCES, value["resources"], strict=True):
        if not isinstance(item, dict) or set(item) != {"name", "baseline", "entry_count", "entries"} or item["name"] != resource.name:
            raise WordingFixError(f"resource header differs: {resource.name}")
        _path, _packed, literals, baseline = resource_data(steam_root, resource)
        if item["baseline"] != baseline or not isinstance(item["entries"], list) or item["entry_count"] != len(item["entries"]) or item["entry_count"] != len(resource.coordinates):
            raise WordingFixError(f"resource baseline/entry count differs: {resource.name}")
        expected_coordinates = list(resource.coordinates)
        changes = 0
        for expected, entry in zip(expected_coordinates, item["entries"], strict=True):
            required_entry = {"coordinate", "source_current_utf16le_sha256", "ko", "ko_utf16le_sha256", "format_profile_sha256"}
            if not isinstance(entry, dict) or set(entry) != required_entry or parse_coordinate(entry["coordinate"]) != expected:
                raise WordingFixError(f"entry coordinates differ: {resource.name}")
            source = literals[expected]
            replacement = entry["ko"]
            if not isinstance(replacement, str) or any(not isinstance(entry[key], str) or not HEX64_RE.fullmatch(entry[key]) for key in ("source_current_utf16le_sha256", "ko_utf16le_sha256", "format_profile_sha256")):
                raise WordingFixError(f"entry types differ: {resource.name}:{expected}")
            if text_hash(source) != entry["source_current_utf16le_sha256"] or text_hash(replacement) != entry["ko_utf16le_sha256"] or canonical_hash(profile(source)) != entry["format_profile_sha256"]:
                raise WordingFixError(f"source/hash/profile differs: {resource.name}:{expected}")
            if OLD_WORDING not in source or replacement != source.replace(OLD_WORDING, NEW_WORDING) or profile(source) != profile(replacement):
                raise WordingFixError(f"wording correction differs: {resource.name}:{expected}")
            if KANA_OR_HAN_RE.search(replacement):
                raise WordingFixError(f"replacement has Japanese/CJK source text: {resource.name}:{expected}")
            changes += source != replacement
        total += len(item["entries"])
        reports.append({"name": resource.name, "entry_count": len(item["entries"]), "effective_change_count": changes, "checks": {"baseline": "OK", "source_hashes": "OK", "format_profiles": "OK", "wording_rule": "OK"}})
    if total != value["entry_count"]:
        raise WordingFixError("total entry count differs")
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "switch_korean_translation_used": False,
        "entry_count": total,
        "resources": reports,
        "checks": {"Steam_installation_written": False, "source_hash_gates": "OK", "format_profiles": "OK", "pristine_source_review_recorded_privately": "OK"},
    }


def build(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output_root = private_path(output_root)
    overlay = load_overlay()
    validation = validate_overlay(steam_root, overlay)
    outputs: list[dict[str, Any]] = []
    for resource, item in zip(RESOURCES, overlay["resources"], strict=True):
        source_path, packed, literals, _baseline = resource_data(steam_root, resource)
        replacements = {parse_coordinate(entry["coordinate"]): entry["ko"] for entry in item["entries"]}
        candidate_a = rebuild_packed_with_literals(packed, replacements)
        candidate_b = rebuild_packed_with_literals(packed, replacements)
        if candidate_a != candidate_b:
            raise WordingFixError(f"candidate is not deterministic: {resource.name}")
        verified = {(item.block_id, item.record_id, item.literal_id): item.text for item in iter_literals(parse_packed_msggame(candidate_a).archive)}
        if any(verified.get(coordinate) != replacement for coordinate, replacement in replacements.items()):
            raise WordingFixError(f"candidate text differs: {resource.name}")
        target = (output_root / Path(resource.relative)).resolve()
        if output_root not in target.parents:
            raise WordingFixError("candidate path escapes private output")
        atomic_write(target, candidate_a)
        if source_path.read_bytes() != packed or target.read_bytes() != candidate_a:
            raise WordingFixError(f"unexpected file mutation: {resource.name}")
        _header, raw = decompress_wrapper(candidate_a)
        outputs.append({"name": resource.name, "relative_path": resource.relative, "packed_size": len(candidate_a), "packed_sha256": sha256_bytes(candidate_a), "raw_size": len(raw), "raw_sha256": sha256_bytes(raw), "effective_change_count": len(replacements)})
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "switch_korean_translation_used": False,
        "entry_count": validation["entry_count"],
        "output_policy": {"private_root": "tmp", "steam_installation_written": False, "release_asset_written": False, "github_written": False},
        "resources": outputs,
    }
    blob = pretty_json(manifest)
    assert_public_safe(blob, "manifest")
    atomic_write(output_root / "build_manifest.v1.json", blob)
    return {"entry_count": validation["entry_count"], "resource_count": len(outputs), "output_root": str(output_root), "steam_installation_written": False}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    freeze_parser = sub.add_parser("freeze")
    freeze_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)
    try:
        result = freeze(args.steam_root) if args.command == "freeze" else build(args.steam_root, args.output_root)
    except (WordingFixError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
