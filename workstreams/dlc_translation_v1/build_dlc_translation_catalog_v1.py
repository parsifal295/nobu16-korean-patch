#!/usr/bin/env python3
"""Build the source-aligned DLC translation catalogue without touching Steam.

Full JP/SC/TC/EN source text is commercial input and is therefore written only
below this workstream's ignored ``private`` directory.  The committed manifest
contains counts, coordinates, and hashes, but no source script.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
AUDIT_SCRIPT = (
    REPO
    / "workstreams"
    / "dlc_translation_inventory_v1"
    / "audit_dlc_translation_inventory_v1.py"
)

PRIVATE_CATALOG = WORKSTREAM / "private" / "catalog.private.v1.json"
PUBLIC_MANIFEST = WORKSTREAM / "catalog.manifest.v1.json"

DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_LEGACY_ROOT = Path(
    r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root"
)

LANGUAGES = ("JP", "SC", "TC", "EN")
AREAS = ("DLC", "DLC_PK")
SCHEMA = "nobu16.kr.dlc-translation-catalog-private.v1"
MANIFEST_SCHEMA = "nobu16.kr.dlc-translation-catalog-manifest.v1"

# The English resources use Koei's font-code characters in place of a few
# Latin punctuation/romanisation glyphs.  ``source`` always retains the exact
# code units; ``display`` is only a translator-facing reading aid.
EN_DISPLAY_MAP = str.maketrans(
    {
        "\u00a5": "Ō",
        "\u00a8": "ū",
        "\u00aa": "ō",
        "\u00c6": "“",
        "\u00c8": "—",
        "\u00d6": "'",
        "\u00f6": "'",
    }
)

ESC_RE = re.compile(r"\x1bC[A-Z]")
RUNTIME_TOKEN_RE = re.compile(r"\[(?:bm?|[A-Za-z]+)\d+\]")
PRINTF_RE = re.compile(
    r"%(?:\d+\$)?[-+#0 ']*\d*(?:\.\d+)?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)


class CatalogError(ValueError):
    """Raised when catalogue alignment or a pinned format invariant fails."""


def load_audit_module() -> Any:
    spec = importlib.util.spec_from_file_location("dlc_inventory_v1", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise CatalogError(f"cannot import inventory helper: {AUDIT_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def utf16le(text: str) -> bytes:
    return text.encode("utf-16le", errors="strict")


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_xl_shape(raw: bytes) -> dict[str, Any]:
    if len(raw) < 20 or raw[:4] != b"XL\x13\0":
        raise CatalogError("decoded resource is not XL13")
    _, _, file_size, type_count, sets, width, table_offset, _ = struct.unpack_from(
        "<HHHHHhhh", raw, 0
    )
    types = tuple(raw[16 : 16 + type_count])
    string_fields = sum(value == 0 for value in types)
    if file_size != len(raw):
        raise CatalogError(f"XL13 size field mismatch: {file_size} != {len(raw)}")
    if string_fields != 1:
        raise CatalogError(f"expected one string field per row, found {string_fields}")
    return {
        "sets": sets,
        "width": width,
        "table_offset": table_offset,
        "types": list(types),
        "string_fields": string_fields,
    }


def source_text(code_units: Sequence[int]) -> str:
    blob = b"".join(struct.pack("<H", value) for value in code_units)
    return blob.decode("utf-16le", errors="strict")


def protected_tokens(text: str) -> list[str]:
    found: list[tuple[int, str]] = []
    for pattern in (ESC_RE, RUNTIME_TOKEN_RE, PRINTF_RE):
        found.extend((match.start(), match.group(0)) for match in pattern.finditer(text))
    return [value for _, value in sorted(found)]


def control_signature(text: str) -> dict[str, Any]:
    pua = [f"U+{ord(value):04X}" for value in text if 0xE000 <= ord(value) <= 0xF8FF]
    controls = [
        f"U+{ord(value):04X}"
        for value in text
        if ord(value) < 0x20 and value not in {"\n", "\t"}
    ]
    return {
        "protected_tokens": protected_tokens(text),
        "private_use_codepoints": pua,
        "nonlayout_control_codepoints": controls,
        "line_count": text.count("\n") + 1,
    }


def is_new_path(relative: Path, legacy_root: Path) -> bool:
    return not (legacy_root / relative).is_file()


def aligned_language_path(game_root: Path, area: str, language: str, name: str) -> Path:
    direct = game_root / area / language / name
    if direct.is_file():
        return direct
    # Base DLC ships JP/SC/TC only.  Its eight displayed JP sources are exact
    # duplicates of the same-named PK containers, so the official PK EN row is
    # the only valid English semantic donor for this alignment.
    if area == "DLC" and language == "EN":
        donor = game_root / "DLC_PK" / "EN" / name
        if donor.is_file():
            return donor
    raise CatalogError(f"missing aligned {language} resource: {direct}")


def catalogue_inputs(
    game_root: Path, legacy_root: Path, executable: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    audit = load_audit_module()
    decoder = audit.DlcDecoder(executable)
    placements: list[dict[str, Any]] = []
    sources: dict[str, dict[str, Any]] = {}
    family_counts: Counter[str] = Counter()
    area_counts: Counter[str] = Counter()
    new_counts: Counter[str] = Counter()
    excluded_counts: Counter[str] = Counter()
    file_counts: Counter[str] = Counter()
    placement_ids: set[str] = set()
    full_language_hashes: dict[str, dict[str, str]] = defaultdict(dict)

    for area in AREAS:
        jp_root = game_root / area / "JP"
        if not jp_root.is_dir():
            raise CatalogError(f"missing JP DLC directory: {jp_root}")
        for jp_path in sorted(jp_root.glob("*.n16")):
            if not audit.is_translation_container(jp_path):
                continue
            relative = Path(area) / "JP" / jp_path.name
            spec = audit.file_spec(jp_path)
            language_records: dict[str, tuple[Any, ...]] = {}
            shapes: dict[str, dict[str, Any]] = {}
            for language in LANGUAGES:
                path = aligned_language_path(game_root, area, language, jp_path.name)
                try:
                    input_label = path.relative_to(game_root).as_posix()
                except ValueError as exc:
                    raise CatalogError(f"aligned source escaped game root: {path}") from exc
                full_language_hashes[area][f"{language}:{input_label}"] = audit.sha256_file(path)
                raw = decoder.decode_xl(path, audit.file_spec(path))
                shapes[language] = read_xl_shape(raw)
                _, records = audit.parse_xl_records(raw)
                language_records[language] = records
            record_counts = {language: len(rows) for language, rows in language_records.items()}
            if len(set(record_counts.values())) != 1:
                raise CatalogError(
                    f"row topology differs at {area}/{jp_path.name}: {record_counts}"
                )
            set_counts = {language: shape["sets"] for language, shape in shapes.items()}
            if len(set(set_counts.values())) != 1:
                raise CatalogError(
                    f"XL set count differs at {area}/{jp_path.name}: {set_counts}"
                )

            file_counts[area] += 1
            path_is_new = is_new_path(relative, legacy_root)
            for index, jp_record in enumerate(language_records["JP"]):
                if not jp_record.code_units:
                    continue
                if not audit.is_visible_record(spec.family, jp_record):
                    excluded_counts[spec.family] += 1
                    continue
                aligned = {
                    language: language_records[language][index]
                    for language in LANGUAGES
                }
                if any(record.row != jp_record.row for record in aligned.values()):
                    raise CatalogError(
                        f"row identity differs at {area}/{jp_path.name} index {index}"
                    )
                texts = {
                    language: source_text(record.code_units)
                    for language, record in aligned.items()
                }
                jp_blob = utf16le(texts["JP"])
                source_id = f"jp-{sha256(jp_blob)[:20]}"
                placement_id = f"{area}/JP/{jp_path.name}#row{jp_record.row}"
                if placement_id in placement_ids:
                    raise CatalogError(f"duplicate placement id: {placement_id}")
                placement_ids.add(placement_id)
                source = sources.setdefault(
                    source_id,
                    {
                        "source_id": source_id,
                        "jp_utf16le_sha256": sha256(jp_blob),
                        "jp": texts["JP"],
                        "contexts": [],
                        "placements": [],
                    },
                )
                if source["jp"] != texts["JP"]:
                    raise CatalogError(f"source id collision: {source_id}")
                context = {
                    "placement_id": placement_id,
                    "family": spec.family,
                    "jp": texts["JP"],
                    "sc": texts["SC"],
                    "tc": texts["TC"],
                    "en": texts["EN"],
                    "en_display": texts["EN"].translate(EN_DISPLAY_MAP),
                }
                source["contexts"].append(context)
                source["placements"].append(placement_id)
                placement = {
                    "placement_id": placement_id,
                    "area": area,
                    "path": f"{area}/JP/{jp_path.name}",
                    "family": spec.family,
                    "row": jp_record.row,
                    "source_id": source_id,
                    "is_new_path": path_is_new,
                    "jp_utf16le_sha256": sha256(jp_blob),
                    "jp_control_signature": control_signature(texts["JP"]),
                    "aligned_utf16le_sha256": {
                        language: sha256(utf16le(text))
                        for language, text in texts.items()
                    },
                }
                placements.append(placement)
                family_counts[spec.family] += 1
                area_counts[area] += 1
                if path_is_new:
                    new_counts[spec.family] += 1

    ordered_sources = sorted(sources.values(), key=lambda value: value["source_id"])
    ordered_placements = sorted(placements, key=lambda value: value["placement_id"])
    new_source_ids = {
        placement["source_id"] for placement in placements if placement["is_new_path"]
    }
    existing_source_ids = set(sources) - new_source_ids
    new_only_source_ids = {
        source_id
        for source_id in new_source_ids
        if all(
            placement["is_new_path"]
            for placement in placements
            if placement["source_id"] == source_id
        )
    }

    private = {
        "schema": SCHEMA,
        "inputs": {
            "game_root": str(game_root),
            "legacy_root": str(legacy_root),
            "executable": str(executable),
            "executable_sha256": audit.sha256_file(executable),
            "localized_file_sha256": {
                area: dict(sorted(values.items()))
                for area, values in sorted(full_language_hashes.items())
            },
        },
        "policy": {
            "source_text_private_only": True,
            "translation_base_language": "JP",
            "crosscheck_languages": ["SC", "TC", "EN"],
            "base_dlc_english_context_uses_same_named_dlc_pk_donor": True,
            "empty_slots_excluded": True,
            "event_rows_257_267_excluded": True,
            "tom_sort_row_1_excluded": True,
            "exact_jp_source_dedup_with_coordinate_override_supported": True,
        },
        "summary": {
            "files": sum(file_counts.values()),
            "files_by_area": dict(sorted(file_counts.items())),
            "placements": len(placements),
            "unique_jp_sources": len(sources),
            "new_path_placements": sum(new_counts.values()),
            "new_path_unique_sources": len(new_source_ids),
            "new_only_unique_sources": len(new_only_source_ids),
            "existing_only_unique_sources": len(existing_source_ids),
            "placements_by_area": dict(sorted(area_counts.items())),
            "placements_by_family": dict(sorted(family_counts.items())),
            "new_path_placements_by_family": dict(sorted(new_counts.items())),
            "excluded_internal_records_by_family": dict(sorted(excluded_counts.items())),
        },
        "sources": ordered_sources,
        "placements": ordered_placements,
    }
    private_blob = canonical_json(private)

    public_placements = [
        {
            "placement_id": value["placement_id"],
            "family": value["family"],
            "source_id": value["source_id"],
            "is_new_path": value["is_new_path"],
            "jp_utf16le_sha256": value["jp_utf16le_sha256"],
            "jp_control_signature": value["jp_control_signature"],
            "aligned_utf16le_sha256": value["aligned_utf16le_sha256"],
        }
        for value in ordered_placements
    ]
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "private_catalog_sha256": sha256(private_blob),
        "summary": private["summary"],
        "policy": private["policy"],
        "source_ids": sorted(sources),
        "new_path_source_ids": sorted(new_source_ids),
        "placements": public_placements,
        "validation": {
            "all_four_languages_present": True,
            "one_string_field_per_xl_row": True,
            "row_topology_aligned": True,
            "source_script_absent_from_public_manifest": True,
            "steam_writes": 0,
        },
    }
    return private, manifest


def write_or_validate(path: Path, blob: bytes, *, write: bool) -> None:
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
        return
    if not path.is_file():
        raise CatalogError(f"missing generated artifact: {path}")
    if path.read_bytes() != blob:
        raise CatalogError(f"generated artifact drifted: {path}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--legacy-root", type=Path, default=DEFAULT_LEGACY_ROOT)
    parser.add_argument("--executable", type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)

    game_root = args.game_root.resolve()
    legacy_root = args.legacy_root.resolve()
    executable = (args.executable or game_root / "NOBU16PK.exe").resolve()
    private, manifest = catalogue_inputs(game_root, legacy_root, executable)
    private_blob = canonical_json(private)
    manifest_blob = canonical_json(manifest)
    write_or_validate(PRIVATE_CATALOG, private_blob, write=args.write)
    write_or_validate(PUBLIC_MANIFEST, manifest_blob, write=args.write)
    print(
        json.dumps(
            {
                "private_catalog_sha256": sha256(private_blob),
                "public_manifest_sha256": sha256(manifest_blob),
                "summary": manifest["summary"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
