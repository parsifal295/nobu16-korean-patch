#!/usr/bin/env python3
"""Read-only audit for Steam JP PK non-logo menu label images.

The sole target is ``RES_JP_PK/res_lang_pk.bin /18``.  It is deliberately an
audit-only tool: private contact sheets can be emitted below ``tmp/``, but no
candidate resource, game-install write, Git operation, or release operation
exists here.  Logo/title/brand art is expressly out of scope.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp"
MANIFEST_PATH = WORKSTREAM / "manifest.v1.json"
CATALOG_PATH = WORKSTREAM / "catalog.v1.json"
DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
SCHEMA = "nobu16.kr.steam-jp-pk-menu-labels-audit.v1"
CATALOG_SCHEMA = "nobu16.kr.steam-jp-pk-menu-labels.catalog.v2"
TARGET_OUTER = 18
LANGUAGE_ORDER = ("jp", "en", "sc", "tc")
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as codec  # noqa: E402


class AuditError(ValueError):
    """Raised when an input or safety contract fails."""


@dataclass(frozen=True)
class SlotImage:
    slot: int
    wrapper_sha256: str
    raw_sha256: str
    payload_sha256: str
    rgba: bytes


@dataclass(frozen=True)
class LanguageImageBundle:
    language: str
    before: Mapping[str, Any]
    after: Mapping[str, Any]
    outer_entry_sha256: str
    slots: tuple[SlotImage, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256_bytes(blob: bytes | bytearray | memoryview) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256_file(path)}


def stable_hash(value: Any) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def load_manifest() -> dict[str, Any]:
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid manifest: {exc}") from exc
    validate_manifest(manifest)
    return manifest


def valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789ABCDEF" for character in value)


def load_catalog() -> dict[str, Any]:
    """Load only an ASCII, hash-only public catalog.

    The wording and all original JP/EN labels are intentionally absent.  This
    catalog can therefore be committed and checked without carrying game text
    or raster source data.
    """

    try:
        blob = CATALOG_PATH.read_bytes()
        require(blob.isascii(), "catalog must remain ASCII source-free metadata")
        catalog = json.loads(blob.decode("ascii"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid source-free catalog: {exc}") from exc
    require(isinstance(catalog, dict), "catalog root must be an object")
    return catalog


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    require(manifest.get("schema") == SCHEMA, "manifest schema mismatch")
    scope = manifest.get("scope")
    require(isinstance(scope, Mapping), "manifest scope missing")
    require(scope.get("target_resource") == "RES_JP_PK/res_lang_pk.bin", "wrong target resource")
    require(scope.get("target_outer_entry") == TARGET_OUTER, "wrong target outer entry")
    require(set(scope.get("excluded_outer_entries", ())) >= {3, 24}, "logo/title exclusions missing")
    require(scope.get("game_install_write_allowed") is False, "game write must stay disabled")
    require(scope.get("git_or_release_write_allowed") is False, "Git/release write must stay disabled")
    require(scope.get("candidate_generation_enabled") is False, "candidate generation must stay disabled")
    inputs = manifest.get("inputs")
    require(isinstance(inputs, Mapping) and tuple(inputs) == LANGUAGE_ORDER, "language input order/scope drifted")
    for language in LANGUAGE_ORDER:
        row = inputs[language]
        require(isinstance(row, Mapping), f"{language}: input missing")
        require(row.get("relative_path") == f"RES_{language.upper()}_PK/res_lang_pk.bin", f"{language}: wrong resource path")
        require(isinstance(row.get("size"), int) and row["size"] > 0, f"{language}: invalid input size")
        require(isinstance(row.get("sha256"), str) and len(row["sha256"]) == 64, f"{language}: invalid input SHA")
    contract = manifest.get("structure_contract")
    require(isinstance(contract, Mapping), "structure contract missing")
    require(contract.get("outer_entry_count") == 27, "outer entry contract drifted")
    require(contract.get("nested_slot_count") == 43, "nested slot contract drifted")
    require(contract.get("g1t_texture_count_per_slot") == 1, "texture count contract drifted")
    require(contract.get("g1t_platform") == 10, "platform contract drifted")
    require(contract.get("format_code") == "0x5B", "format contract drifted")
    require(contract.get("dimensions") == [512, 128], "dimensions contract drifted")
    require(contract.get("mip_count") == 1, "mip contract drifted")
    source_free = manifest.get("source_free_guarantees")
    require(isinstance(source_free, Mapping) and source_free.get("metadata_only") is True, "source-free flag missing")


def validate_catalog(catalog: Mapping[str, Any], manifest: Mapping[str, Any], report: Mapping[str, Any] | None = None) -> None:
    """Validate that the public catalog contains hashes, not source labels."""

    require(catalog.get("schema") == CATALOG_SCHEMA, "catalog schema mismatch")
    require(catalog.get("target_resource") == manifest["scope"]["target_resource"], "catalog target resource drifted")
    require(catalog.get("target_outer_entry") == TARGET_OUTER, "catalog target outer entry drifted")
    require(catalog.get("source_free") is True, "catalog source-free flag missing")
    require(catalog.get("hash_algorithm") == "SHA-256", "catalog hash algorithm drifted")
    require(catalog.get("korean_output_hash_encoding") == "UTF-16LE", "catalog Korean hash encoding drifted")
    require(set(catalog.get("excluded_outer_entries", ())) >= {3, 24}, "catalog logo/title exclusions missing")
    require(catalog.get("review_required_slots") == [1, 2, 19], "catalog review slot set drifted")
    require(catalog.get("candidate_eligible_now") is False, "catalog must not open a candidate gate")
    guarantees = catalog.get("source_free_guarantees")
    require(
        guarantees
        == {
            "contains_japanese_source_text": False,
            "contains_english_reference_text": False,
            "contains_plaintext_korean_output": False,
            "contains_image_bytes": False,
        },
        "catalog source-free guarantee drifted",
    )
    slots = catalog.get("slots")
    require(isinstance(slots, list) and [row.get("slot") for row in slots] == list(range(43)), "catalog slot order/count drifted")
    expected_dimensions = manifest["structure_contract"]["dimensions"]
    expected_keys = {"slot", "input_payload_sha256", "dimensions", "ko_output_utf16le_sha256"}
    for row in slots:
        require(isinstance(row, Mapping) and set(row) == expected_keys, "catalog row must be hash-only metadata")
        require(valid_sha256(row.get("input_payload_sha256")), "catalog input payload SHA invalid")
        require(valid_sha256(row.get("ko_output_utf16le_sha256")), "catalog Korean output SHA invalid")
        require(row.get("dimensions") == expected_dimensions, "catalog slot dimensions drifted")
    serialized = json.dumps(catalog, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    require('"jp"' not in serialized and '"en_reference"' not in serialized and '"ko"' not in serialized, "catalog leaked a source label field")
    if report is not None:
        report_slots = report.get("slots")
        require(isinstance(report_slots, list) and len(report_slots) == 43, "report unavailable for catalog hash check")
        for row in slots:
            slot = row["slot"]
            payload = report_slots[slot].get("language_payloads", {}).get("jp", {}).get("payload_sha256")
            require(payload == row["input_payload_sha256"], f"catalog payload pin drifted at slot {slot}")


def is_reparse(path: Path) -> bool:
    try:
        attrs = path.lstat().st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT) or path.is_symlink() or path.is_junction()
    except OSError:
        return True


def ensure_tmp(path: Path, *, mkdir: bool = False) -> Path:
    """Return a non-reparse output path that lexically and physically stays in tmp."""

    root_lexical = Path(os.path.abspath(TMP_ROOT))
    candidate_lexical = Path(os.path.abspath(path))
    try:
        candidate_lexical.relative_to(root_lexical)
    except ValueError as exc:
        raise AuditError(f"output escapes tmp: {candidate_lexical}") from exc
    require(not is_reparse(root_lexical), f"tmp root is a reparse point: {root_lexical}")
    root = root_lexical.resolve()
    current = root
    for part in candidate_lexical.relative_to(root_lexical).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            require(not is_reparse(current), f"output component is a reparse point: {current}")
            resolved = current.resolve()
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise AuditError(f"output component escapes tmp: {current}") from exc
            current = resolved
        elif mkdir:
            current.mkdir(exist_ok=False)
            require(not is_reparse(current), f"new output component is a reparse point: {current}")
    return current


def create_fresh_output_root(path: Path) -> Path:
    parent = ensure_tmp(path.parent, mkdir=True)
    output = parent / path.name
    require(not output.exists() and not output.is_symlink(), f"refusing to replace output root: {output}")
    output.mkdir(exist_ok=False)
    return ensure_tmp(output)


def atomic_write(path: Path, payload: bytes) -> None:
    target = ensure_tmp(path.parent, mkdir=True) / path.name
    target = ensure_tmp(target)
    require(not target.exists() and not target.is_symlink(), f"refusing to replace output: {target}")
    handle, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_language(game_root: Path, language: str, spec: Mapping[str, Any], contract: Mapping[str, Any]) -> LanguageImageBundle:
    path = game_root / str(spec["relative_path"])
    require(path.is_file(), f"{language}: missing input {path}")
    before = file_spec(path)
    expected = {"size": spec["size"], "sha256": spec["sha256"]}
    require(before == expected, f"{language}: Steam 1.1.7 input fingerprint mismatch: {before}")
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"{language}: outer LINK identity gate failed")
    require(len(outer.entries) == contract["outer_entry_count"], f"{language}: outer entry count drifted")
    require(TARGET_OUTER < len(outer.entries), f"{language}: target outer entry missing")
    inner = codec.parse_inner_link32(outer.entries[TARGET_OUTER].data)
    require(len(inner.entries) == contract["nested_slot_count"], f"{language}: nested slot count drifted")
    slots: list[SlotImage] = []
    for entry in inner.entries:
        header, raw = lz4.decompress_wrapper(entry.data)
        texture = codec.parse_pc_title_g1t(raw)
        require(header.uncompressed_size == len(raw), f"{language}/{entry.index}: wrapper size drifted")
        require(
            (texture.width, texture.height, texture.format_code, texture.mip_count)
            == (512, 128, 0x5B, 1),
            f"{language}/{entry.index}: G1T geometry/format drifted",
        )
        slots.append(
            SlotImage(
                slot=entry.index,
                wrapper_sha256=sha256_bytes(entry.data),
                raw_sha256=sha256_bytes(raw),
                payload_sha256=sha256_bytes(texture.bc3),
                rgba=codec.decode_bc3(texture.bc3, texture.width, texture.height),
            )
        )
    after = file_spec(path)
    require(after == before, f"{language}: input changed during read-only audit")
    return LanguageImageBundle(
        language=language,
        before=before,
        after=after,
        outer_entry_sha256=sha256_bytes(outer.entries[TARGET_OUTER].data),
        slots=tuple(slots),
    )


def difference_metrics(left: bytes, right: bytes, width: int = 512, height: int = 128) -> dict[str, Any]:
    require(len(left) == len(right) == width * height * 4, "RGBA comparison size mismatch")
    min_x, min_y, max_x, max_y = width, height, -1, -1
    changed = 0
    for pixel in range(width * height):
        start = pixel * 4
        if left[start : start + 4] != right[start : start + 4]:
            changed += 1
            x, y = pixel % width, pixel // width
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
    return {
        "changed_pixel_count": changed,
        "difference_bbox_inclusive": None if not changed else [min_x, min_y, max_x, max_y],
    }


def checkerboard(rgba: bytes, width: int = 512, height: int = 128) -> bytes:
    output = bytearray(len(rgba))
    for y in range(height):
        for x in range(width):
            source = (y * width + x) * 4
            alpha = rgba[source + 3]
            background = 40 if ((x // 8) ^ (y // 8)) & 1 else 22
            for channel in range(3):
                output[source + channel] = (rgba[source + channel] * alpha + background * (255 - alpha) + 127) // 255
            output[source + 3] = 255
    return bytes(output)


def nearest_resize(rgba: bytes, width: int, height: int, target_width: int, target_height: int) -> bytes:
    output = bytearray(target_width * target_height * 4)
    for y in range(target_height):
        source_y = min(height - 1, y * height // target_height)
        for x in range(target_width):
            source_x = min(width - 1, x * width // target_width)
            source = (source_y * width + source_x) * 4
            target = (y * target_width + x) * 4
            output[target : target + 4] = rgba[source : source + 4]
    return bytes(output)


def add_border(rgba: bytearray, width: int, height: int, color: tuple[int, int, int, int]) -> None:
    for x in range(width):
        rgba[x * 4 : x * 4 + 4] = bytes(color)
        bottom = ((height - 1) * width + x) * 4
        rgba[bottom : bottom + 4] = bytes(color)
    for y in range(height):
        left = (y * width) * 4
        right = (y * width + width - 1) * 4
        rgba[left : left + 4] = bytes(color)
        rgba[right : right + 4] = bytes(color)


def paste_rgba(canvas: bytearray, canvas_width: int, x: int, y: int, source: bytes, source_width: int, source_height: int) -> None:
    for row in range(source_height):
        source_start = row * source_width * 4
        target_start = ((y + row) * canvas_width + x) * 4
        canvas[target_start : target_start + source_width * 4] = source[source_start : source_start + source_width * 4]


def make_contact_sheet(bundles: Mapping[str, LanguageImageBundle]) -> bytes:
    panel_width, panel_height, gutter = 256, 64, 4
    canvas_width = gutter + len(LANGUAGE_ORDER) * (panel_width + gutter)
    canvas_height = gutter + len(next(iter(bundles.values())).slots) * (panel_height + gutter)
    canvas = bytearray(canvas_width * canvas_height * 4)
    colors = {
        "jp": (235, 196, 56, 255),
        "en": (64, 168, 236, 255),
        "sc": (232, 72, 72, 255),
        "tc": (176, 92, 224, 255),
    }
    for row, slot in enumerate(range(len(next(iter(bundles.values())).slots))):
        y = gutter + row * (panel_height + gutter)
        for column, language in enumerate(LANGUAGE_ORDER):
            image = checkerboard(bundles[language].slots[slot].rgba)
            panel = bytearray(nearest_resize(image, 512, 128, panel_width, panel_height))
            add_border(panel, panel_width, panel_height, colors[language])
            x = gutter + column * (panel_width + gutter)
            paste_rgba(canvas, canvas_width, x, y, panel, panel_width, panel_height)
    return codec.encode_rgba_png(bytes(canvas), canvas_width, canvas_height)


def source_free_slot_rows(bundles: Mapping[str, LanguageImageBundle]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for slot in range(len(bundles["jp"].slots)):
        jp = bundles["jp"].slots[slot]
        language_rows: dict[str, Any] = {}
        comparisons: dict[str, Any] = {}
        for language in LANGUAGE_ORDER:
            current = bundles[language].slots[slot]
            language_rows[language] = {
                "wrapper_sha256": current.wrapper_sha256,
                "raw_sha256": current.raw_sha256,
                "payload_sha256": current.payload_sha256,
            }
            if language != "jp":
                comparisons[f"jp_to_{language}"] = difference_metrics(jp.rgba, current.rgba)
        result.append(
            {
                "slot": slot,
                "classification": "unreviewed_nonlogo_candidate",
                "language_payloads": language_rows,
                "jp_vs_other_languages": comparisons,
                "candidate_eligible": False,
                "candidate_blockers": [
                    "runtime screen mapping missing",
                    "Korean wording missing",
                    "text-only background-preserving rectangle missing",
                ],
            }
        )
    return result


def build_report(game_root: Path, manifest: Mapping[str, Any]) -> tuple[dict[str, Any], Mapping[str, LanguageImageBundle]]:
    contract = manifest["structure_contract"]
    bundles = {
        language: read_language(game_root, language, manifest["inputs"][language], contract)
        for language in LANGUAGE_ORDER
    }
    rows = source_free_slot_rows(bundles)
    report = {
        "schema": SCHEMA,
        "file_only": True,
        "game_install_modified": False,
        "git_or_release_modified": False,
        "target": {
            "resource": manifest["scope"]["target_resource"],
            "outer_entry": TARGET_OUTER,
            "logo_or_title_art_touched": False,
            "excluded_outer_entries": list(manifest["scope"]["excluded_outer_entries"]),
        },
        "candidate_generation": {
            "enabled": False,
            "candidate_created": False,
            "reason": "No Switch PK source, no runtime mapping, and no approved PC-native Korean text rectangles.",
        },
        "inputs": {
            language: {
                "before": dict(bundle.before),
                "after": dict(bundle.after),
                "unchanged_during_read": bundle.before == bundle.after,
                "outer_18_sha256": bundle.outer_entry_sha256,
            }
            for language, bundle in bundles.items()
        },
        "structure": dict(contract),
        "slots": rows,
        "switch_v2_reference": dict(manifest["switch_v2_reference"]),
        "source_free_guarantees": dict(manifest["source_free_guarantees"]),
    }
    report["report_sha256"] = stable_hash(report)
    validate_report(report, manifest)
    return report, bundles


def validate_report(report: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    require(report.get("schema") == SCHEMA, "report schema mismatch")
    expected_hash = stable_hash({key: value for key, value in report.items() if key != "report_sha256"})
    require(report.get("report_sha256") == expected_hash, "report checksum mismatch")
    require(report.get("file_only") is True, "file-only flag missing")
    require(report.get("game_install_modified") is False, "report must not claim game install write")
    require(report.get("git_or_release_modified") is False, "report must not claim Git/release write")
    target = report.get("target")
    require(isinstance(target, Mapping) and target.get("logo_or_title_art_touched") is False, "logo/title exclusion violated")
    require(target.get("outer_entry") == TARGET_OUTER, "target outer entry mismatch")
    candidate = report.get("candidate_generation")
    require(isinstance(candidate, Mapping) and candidate.get("enabled") is False and candidate.get("candidate_created") is False, "candidate gate violated")
    inputs = report.get("inputs")
    require(isinstance(inputs, Mapping) and set(inputs) == set(LANGUAGE_ORDER), "report input scope drifted")
    for language in LANGUAGE_ORDER:
        row = inputs[language]
        require(row.get("before") == row.get("after"), f"{language}: report admits input mutation")
        expected_fingerprint = {
            "size": manifest["inputs"][language]["size"],
            "sha256": manifest["inputs"][language]["sha256"],
        }
        require(row.get("before") == expected_fingerprint, f"{language}: report input fingerprint mismatch")
        require(row.get("unchanged_during_read") is True, f"{language}: read-only flag missing")
    slots = report.get("slots")
    require(isinstance(slots, list) and len(slots) == 43, "report slot count mismatch")
    require([row.get("slot") for row in slots] == list(range(43)), "report slot order drifted")
    for row in slots:
        require(row.get("candidate_eligible") is False, "unreviewed slot cannot be candidate-eligible")
        payloads = row.get("language_payloads")
        require(isinstance(payloads, Mapping) and set(payloads) == set(LANGUAGE_ORDER), "slot language payload metadata drifted")
        for language in LANGUAGE_ORDER:
            payload = payloads[language]
            require(isinstance(payload, Mapping), "slot payload metadata missing")
            require(all(isinstance(payload.get(key), str) and len(payload[key]) == 64 for key in ("wrapper_sha256", "raw_sha256", "payload_sha256")), "invalid slot hash")
    source_free = report.get("source_free_guarantees")
    require(isinstance(source_free, Mapping) and source_free.get("metadata_only") is True, "report source-free flag missing")


def inspect_command(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    catalog = load_catalog()
    game_root = Path(args.game_root).resolve()
    output_root = create_fresh_output_root(Path(args.output_root))
    report, bundles = build_report(game_root, manifest)
    validate_catalog(catalog, manifest, report)
    report_path = ensure_tmp(output_root / "audit_report.v1.json")
    atomic_write(report_path, (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    if args.preview:
        png = make_contact_sheet(bundles)
        preview_path = ensure_tmp(output_root / "private" / "pk_menu_labels_contact_sheet.png")
        atomic_write(preview_path, png)
        preview = {
            "path": str(preview_path),
            "sha256": sha256_bytes(png),
            "private_only": True,
            "dimensions": [1044, 2928],
            "language_order_left_to_right": list(LANGUAGE_ORDER),
            "border_colors": {"jp": "gold", "en": "blue", "sc": "red", "tc": "purple"},
        }
        preview_path_json = ensure_tmp(output_root / "private" / "preview.v1.json")
        atomic_write(preview_path_json, (json.dumps(preview, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(f"report_sha256={report['report_sha256']}")
    print("candidate_created=False")
    print("game_install_modified=False")
    return 0


def verify_command(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    catalog = load_catalog()
    output_root = ensure_tmp(Path(args.output_root))
    report_path = ensure_tmp(output_root / "audit_report.v1.json")
    require(report_path.is_file(), f"missing audit report: {report_path}")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid audit report: {exc}") from exc
    validate_report(report, manifest)
    validate_catalog(catalog, manifest, report)
    print(f"report_sha256={report['report_sha256']}")
    print("verify=PASS")
    print("game_install_modified=False")
    return 0


def build_command(_: argparse.Namespace) -> int:
    raise AuditError(
        "candidate generation is hard-disabled: `/18` needs runtime mapping, approved Korean labels, "
        "and PC-native background-preservation proof before any private candidate can exist"
    )


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect", help="read-only input audit; outputs stay under tmp")
    inspect.add_argument("--game-root", default=str(DEFAULT_GAME_ROOT))
    inspect.add_argument("--output-root", required=True)
    inspect.add_argument("--preview", action="store_true")
    inspect.set_defaults(handler=inspect_command)
    verify = subparsers.add_parser("verify", help="verify a prior tmp-only audit report")
    verify.add_argument("--output-root", required=True)
    verify.set_defaults(handler=verify_command)
    build = subparsers.add_parser("build", help="intentionally disabled candidate gate")
    build.set_defaults(handler=build_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, codec.CodecError, lz4.LZ4Error, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
