#!/usr/bin/env python3
"""Verify castle-name draft determinism and the source-free release tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_ROOT = SCRIPT_DIR.parents[1]
TMP_ROOT = PATCH_ROOT / "tmp"
FIRST_ID = 9151
LAST_ID = 9542
COUNT = 392
STATUS = "automatic_draft_review_needed"
OVERLAY_RELATIVE = "public/castle_names_ko_9151_9542.v0.1.json"
EXPECTED_RELEASE_ARTIFACTS = {
    OVERLAY_RELATIVE,
    "evidence/resource_id_map.v0.1.json",
    "manifest.json",
    "validation.json",
}
EXPECTED_RELEASE_FILES = EXPECTED_RELEASE_ARTIFACTS | {
    "README_KO.md",
    "generate_castle_name_draft.py",
    "verification.json",
    "verify_castle_name_draft.py",
}
EXPECTED_RELEASE_DIRECTORIES = {"evidence", "public"}
EXPECTED_BLOCK_HASHES = {
    "SC": "4273E1330085453DDD5EBE6020FD09A68654B97CEF72770B0FA26CAB885932A2",
    "EN": "EC24783D0FB87BAD6A58D2785B9A2EF24DDEF11DB596775EB2B83268A326C46E",
    "JP": "580197B9AFC62FDB4A44E727AF6C1279721F498ED1051988668A7D2BA28C45F5",
}
EXPECTED_UNIQUE_COUNTS = {"SC": 389, "EN": 385, "JP": 389}
EXPECTED_READING_BLOCK_HASHES = {
    "SC": "B0B889078CCDA618AC865A7DFC93A486A5F08913FCF6A8A3FAEBA1F357C20951",
    "EN": "BBDDB244D47EC79A1F0BA56BB05C6F077BA428B4338D26D7CFC0FB15BB0141CB",
    "JP": "D26AD0EE8145292BA403DAA2C8645150636D333C3A14E770AEB958BD2670E4D6",
}
EXPECTED_READING_NONEMPTY_COUNTS = {"SC": 392, "EN": 0, "JP": 392}
EXPECTED_BOUNDARY_CORRECTIONS = {9201: "덴진야마", 9478: "다몬야마"}
EXPECTED_RESOURCE_PINS = {
    "SC": {
        "logical_path": "MSG_PK/SC/msgdata.bin",
        "wrapper_size": 267385,
        "wrapper_sha256": "0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E",
        "raw_size": 499760,
        "raw_sha256": "1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF",
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgdata.bin",
        "wrapper_size": 267550,
        "wrapper_sha256": "15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1",
        "raw_size": 744236,
        "raw_sha256": "DA913D870DA3C13F108E8E6727C9A8881B9E13A83F8EB7F02DD3C55D1D444B32",
    },
    "JP": {
        "logical_path": "MSG_PK/JP/msgdata.bin",
        "wrapper_size": 273734,
        "wrapper_sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
        "raw_size": 431044,
        "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
    },
}
FORBIDDEN_SUFFIXES = {".bin", ".raw", ".jsonl", ".csv", ".bak", ".orig", ".pyc"}
FORBIDDEN_PUBLIC_KEYS = {"sc", "en", "jp", "source", "text", "translation"}


class VerificationError(ValueError):
    """Raised when a deterministic or source-free gate fails."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{path}: expected a JSON object")
    return value


def atomic_write_json(path: Path, value: Any) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def relative_inventory(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise VerificationError(f"missing directory: {root}")
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(
            (item for item in root.rglob("*") if item.is_file()),
            key=lambda item: item.as_posix(),
        )
    ]


def require_tmp_castle_build(path: Path, label: str) -> None:
    try:
        relative = path.resolve().relative_to(TMP_ROOT.resolve())
    except ValueError as exc:
        raise VerificationError(f"{label} is outside KR_PATCH_WORK/tmp") from exc
    if not relative.parts or not relative.parts[0].startswith("castle_names"):
        raise VerificationError(f"{label} is outside a tmp/castle_names* root")


def contains_cjk_unified(text: str) -> bool:
    return any(
        0x3400 <= ord(character) <= 0x4DBF
        or 0x4E00 <= ord(character) <= 0x9FFF
        or 0xF900 <= ord(character) <= 0xFAFF
        for character in text
    )


def walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def verify_overlay(path: Path) -> dict[str, Any]:
    value = read_json(path)
    if set(value) != {"entries", "schema", "source_text_free", "target", "translation_policy"}:
        raise VerificationError("public overlay root properties changed")
    if value.get("schema") != "nobu16.kr.castle-name-overlay.v0.1" or value.get("source_text_free") is not True:
        raise VerificationError("public overlay schema/source-free flag is invalid")
    if any(key.lower() in FORBIDDEN_PUBLIC_KEYS for key in walk_keys(value)):
        raise VerificationError("public overlay contains a commercial source-text field")
    target = value.get("target")
    if (
        not isinstance(target, dict)
        or set(target) != {"entry_count", "first_id", "last_id", "resource", "shared_suffix_id_range_not_modified"}
        or target.get("resource") != "MSG_PK/SC/msgdata.bin"
        or target.get("first_id") != FIRST_ID
        or target.get("last_id") != LAST_ID
        or target.get("entry_count") != COUNT
        or target.get("shared_suffix_id_range_not_modified")
        != {"first_id": 9936, "last_id": 9940, "count": 5}
    ):
        raise VerificationError("public overlay target contract changed")
    policy = value.get("translation_policy")
    if (
        not isinstance(policy, dict)
        or set(policy) != {"base", "castle_type_suffix_included", "jp_reading_use", "reason", "review_required"}
        or policy.get("review_required") is not True
        or policy.get("castle_type_suffix_included") is not False
        or policy.get("jp_reading_use") != "resolve ambiguous syllabic n followed by y"
    ):
        raise VerificationError("public overlay draft policy changed")

    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) != COUNT:
        raise VerificationError("public overlay entry count changed")
    methods: dict[str, int] = {}
    names: list[str] = []
    boundary_corrections: dict[int, str] = {}
    for index, row in enumerate(entries):
        entry_id = FIRST_ID + index
        if not isinstance(row, dict) or set(row) != {"id", "ko", "method", "status"}:
            raise VerificationError(f"public overlay row shape changed at id {entry_id}")
        korean = row.get("ko")
        method = row.get("method")
        if row.get("id") != entry_id or row.get("status") != STATUS:
            raise VerificationError(f"public overlay id/status changed at id {entry_id}")
        if method not in {"en_romaji", "en_romaji_words", "en_romaji_jp_n_y_boundary"}:
            raise VerificationError(f"public overlay method changed at id {entry_id}")
        if (
            not isinstance(korean, str)
            or not korean
            or korean.startswith(" ")
            or korean.endswith(" ")
            or "  " in korean
            or unicodedata.normalize("NFC", korean) != korean
            or any(character != " " and not (0xAC00 <= ord(character) <= 0xD7A3) for character in korean)
        ):
            raise VerificationError(f"public Korean name is invalid at id {entry_id}")
        methods[method] = methods.get(method, 0) + 1
        names.append(korean)
        if method == "en_romaji_jp_n_y_boundary":
            boundary_corrections[entry_id] = korean
    if methods != {"en_romaji": 370, "en_romaji_jp_n_y_boundary": 2, "en_romaji_words": 20}:
        raise VerificationError("automatic transliteration method counts changed")
    if boundary_corrections != EXPECTED_BOUNDARY_CORRECTIONS:
        raise VerificationError("Japanese syllabic n+y boundary corrections changed")
    raw_text = path.read_text(encoding="utf-8")
    if contains_cjk_unified(raw_text):
        raise VerificationError("public overlay contains a CJK unified source ideograph")
    return {
        "entry_count": len(entries),
        "automatic_review_needed_count": len(entries),
        "unique_korean_name_count": len(set(names)),
        "max_korean_character_count_including_spaces": max(map(len, names)),
        "method_counts": methods,
        "jp_syllabic_n_y_boundary_corrections": boundary_corrections,
        "only_precomposed_hangul_and_ascii_space": True,
        "source_text_field_count": 0,
        "cjk_unified_source_ideograph_count": 0,
    }


def verify_evidence(path: Path) -> dict[str, Any]:
    value = read_json(path)
    if value.get("schema") != "nobu16.kr.castle-name-resource-map.v0.1" or value.get("source_text_free") is not True:
        raise VerificationError("resource evidence schema/source-free flag is invalid")
    if set(value) != {
        "aligned_primary_block",
        "excluded_adjacent_ranges",
        "name_blocks",
        "reading_blocks",
        "resources",
        "schema",
        "source_text_free",
        "suffix_contract",
    }:
        raise VerificationError("resource evidence root properties changed")
    aligned = value.get("aligned_primary_block")
    if (
        not isinstance(aligned, dict)
        or set(aligned) != {"all_nonempty", "entry_count", "first_id", "last_id", "resource", "same_ids_in_languages"}
        or aligned.get("resource") != "msgdata.bin"
        or aligned.get("first_id") != FIRST_ID
        or aligned.get("last_id") != LAST_ID
        or aligned.get("entry_count") != COUNT
        or aligned.get("same_ids_in_languages") != ["SC", "EN", "JP"]
        or aligned.get("all_nonempty") is not True
    ):
        raise VerificationError("resource evidence aligned block changed")
    resources = value.get("resources")
    if not isinstance(resources, list) or len(resources) != 3:
        raise VerificationError("resource evidence pin set changed")
    by_language = {
        row.get("language"): row
        for row in resources
        if isinstance(row, dict) and isinstance(row.get("language"), str)
    }
    if set(by_language) != {"SC", "EN", "JP"}:
        raise VerificationError("resource evidence language pin set changed")
    for language, expected in EXPECTED_RESOURCE_PINS.items():
        row = by_language[language]
        if (
            set(row) != {
                "language",
                "logical_path",
                "raw_sha256",
                "raw_size",
                "string_count",
                "unchanged_parse_rebuild_byte_exact",
                "wrapper_sha256",
                "wrapper_size",
            }
            or any(row.get(key) != value for key, value in expected.items())
            or row.get("string_count") != 29210
            or row.get("unchanged_parse_rebuild_byte_exact") is not True
        ):
            raise VerificationError(f"resource evidence {language} wrapper/raw pin changed")
    blocks = value.get("name_blocks")
    if not isinstance(blocks, dict) or set(blocks) != {"SC", "EN", "JP"}:
        raise VerificationError("resource evidence language block set changed")
    for language in ("SC", "EN", "JP"):
        row = blocks[language]
        if (
            not isinstance(row, dict)
            or set(row) != {"count", "first_id", "last_id", "nonempty_count", "text_block_sha256", "unique_text_count"}
            or row.get("first_id") != FIRST_ID
            or row.get("last_id") != LAST_ID
            or row.get("count") != COUNT
            or row.get("nonempty_count") != COUNT
            or row.get("unique_text_count") != EXPECTED_UNIQUE_COUNTS[language]
            or row.get("text_block_sha256") != EXPECTED_BLOCK_HASHES[language]
        ):
            raise VerificationError(f"resource evidence {language} block changed")
    reading_blocks = value.get("reading_blocks")
    if not isinstance(reading_blocks, dict) or set(reading_blocks) != {"SC", "EN", "JP"}:
        raise VerificationError("resource evidence reading block set changed")
    for language in ("SC", "EN", "JP"):
        row = reading_blocks[language]
        if (
            not isinstance(row, dict)
            or set(row) != {"count", "first_id", "last_id", "nonempty_count", "text_block_sha256"}
            or row.get("first_id") != 9543
            or row.get("last_id") != 9934
            or row.get("count") != COUNT
            or row.get("nonempty_count") != EXPECTED_READING_NONEMPTY_COUNTS[language]
            or row.get("text_block_sha256") != EXPECTED_READING_BLOCK_HASHES[language]
        ):
            raise VerificationError(f"resource evidence {language} reading block changed")
    if value.get("suffix_contract") != {
        "name_ids": [9936, 9940],
        "reading_ids": [9942, 9946],
        "separator_id_9941_empty_all_languages": True,
        "suffix_count": 5,
    }:
        raise VerificationError("resource evidence suffix contract changed")
    if value.get("excluded_adjacent_ranges") != [
        {
            "first_id": 9947,
            "last_id": 13974,
            "count": 4028,
            "classification": "unclassified_geographic_and_special_labels",
            "reason_excluded": "not proven to be canonical castle-name ids",
        },
        {
            "first_id": 13975,
            "last_id": 14046,
            "count": 72,
            "classification": "province_names",
            "reason_excluded": "separate province-name block",
        },
        {
            "first_id": 14047,
            "last_id": 14118,
            "count": 72,
            "classification": "province_readings_sc_jp_only",
            "reason_excluded": "separate province-reading block",
        },
    ]:
        raise VerificationError("adjacent excluded range evidence changed")
    if contains_cjk_unified(path.read_text(encoding="utf-8")):
        raise VerificationError("resource evidence contains a CJK unified source ideograph")
    return {
        "resource": "MSG_PK/{SC,EN,JP}/msgdata.bin",
        "first_id": FIRST_ID,
        "last_id": LAST_ID,
        "entry_count": COUNT,
        "all_languages_nonempty_and_id_aligned": True,
        "wrapper_and_raw_resource_pins_exact": True,
        "block_hashes_exact": True,
        "adjacent_unclassified_ranges_excluded": True,
    }


def verify_release_tree(release_root: Path, build_a: Path) -> dict[str, Any]:
    actual_files = {
        path.relative_to(release_root).as_posix()
        for path in release_root.rglob("*")
        if path.is_file()
    }
    if actual_files != EXPECTED_RELEASE_FILES:
        raise VerificationError(
            "release file inventory changed: "
            f"missing={sorted(EXPECTED_RELEASE_FILES - actual_files)}, "
            f"extra={sorted(actual_files - EXPECTED_RELEASE_FILES)}"
        )
    actual_directories = {
        path.relative_to(release_root).as_posix()
        for path in release_root.rglob("*")
        if path.is_dir()
    }
    if actual_directories != EXPECTED_RELEASE_DIRECTORIES:
        raise VerificationError(
            "release directory inventory changed: "
            f"missing={sorted(EXPECTED_RELEASE_DIRECTORIES - actual_directories)}, "
            f"extra={sorted(actual_directories - EXPECTED_RELEASE_DIRECTORIES)}"
        )
    for relative in EXPECTED_RELEASE_ARTIFACTS:
        release_path = release_root / relative
        build_path = build_a / relative
        if not release_path.is_file() or sha256_file(release_path) != sha256_file(build_path):
            raise VerificationError(f"release artifact differs from build A: {relative}")
    private = release_root / "private"
    if private.exists():
        raise VerificationError("release tree contains a private directory")
    forbidden = [
        path.relative_to(release_root).as_posix()
        for path in release_root.rglob("*")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES
    ]
    if forbidden:
        raise VerificationError(f"release tree contains forbidden artifacts: {forbidden}")
    for relative in EXPECTED_RELEASE_FILES:
        text = (release_root / relative).read_text(encoding="utf-8")
        if contains_cjk_unified(text):
            raise VerificationError(f"release artifact contains CJK source ideographs: {relative}")
    return {
        "required_artifact_count": len(EXPECTED_RELEASE_ARTIFACTS),
        "required_artifacts_match_build_a": True,
        "exact_file_inventory": True,
        "exact_directory_inventory": True,
        "public_text_file_count_scanned": len(EXPECTED_RELEASE_FILES),
        "private_directory_count": 0,
        "forbidden_artifact_count": 0,
        "commercial_source_text_present": False,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    build_a = args.build_a.resolve()
    build_b = args.build_b.resolve()
    release_root = args.release_root.resolve()
    require_tmp_castle_build(build_a, "build A")
    require_tmp_castle_build(build_b, "build B")
    inventory_a = relative_inventory(build_a)
    inventory_b = relative_inventory(build_b)
    if inventory_a != inventory_b:
        raise VerificationError("independent castle-name builds are not byte-identical")

    overlay = verify_overlay(build_a / OVERLAY_RELATIVE)
    evidence = verify_evidence(build_a / "evidence" / "resource_id_map.v0.1.json")
    validation = read_json(build_a / "validation.json")
    if validation.get("passed") is not True or validation.get("automatic_review_needed_count") != COUNT:
        raise VerificationError("build validation did not pass")
    private = read_json(build_a / "private" / "castle_names_alignment.v0.1.json")
    if private.get("distribution_forbidden") is not True or len(private.get("entries", [])) != COUNT:
        raise VerificationError("private alignment contract changed")
    release = verify_release_tree(release_root, build_a)
    return {
        "schema": "nobu16.kr.castle-name-draft-verification.v0.1",
        "passed": True,
        "determinism": {
            "independent_builds_byte_identical": True,
            "file_count": len(inventory_a),
            "inventory_sha256": sha256_bytes(
                "".join(
                    f"{row['path']}\t{row['size']}\t{row['sha256']}\n" for row in inventory_a
                ).encode("utf-8")
            ),
        },
        "resource_identification": evidence,
        "public_overlay": {
            **overlay,
            "sha256": sha256_file(build_a / OVERLAY_RELATIVE),
        },
        "release_tree": release,
        "safety": {
            "installed_game_files_modified": False,
            "process_memory_access": False,
            "registry_access": False,
            "private_alignment_distribution_forbidden": True,
        },
        "review_complete": False,
        "patch_recipe_built": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-a", type=Path, required=True)
    parser.add_argument("--build-b", type=Path, required=True)
    parser.add_argument("--release-root", type=Path, default=SCRIPT_DIR)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = verify(args)
        atomic_write_json(args.output.resolve(), result)
    except (OSError, VerificationError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"output={args.output.resolve()}")
    print(f"entries={result['public_overlay']['entry_count']}")
    print("independent_builds_byte_identical=True")
    print("source_text_free=True")
    print("automatic_review_needed=392")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
