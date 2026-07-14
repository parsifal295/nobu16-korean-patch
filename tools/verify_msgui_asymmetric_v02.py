#!/usr/bin/env python3
"""Verify the source-free MSGUI v0.2 asymmetric-slot candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

import msgui_catalog_v2 as catalog


V01_SHA256 = "65994E73624B90951D64369D20097CE46ACAFCDBD0C2EFA18B40975126F3F8C6"
V02_SHA256 = "5DC3C0E14E2131FC2BB4252DF3B25E1F10E462205EAB715E2923298A714B8C14"
RECIPE_SHA256 = "88094B17FC90E892020B8301476D1F7899B60389C9E805929C618DFC5EA517BF"
DEMAND_SHA256 = "7DBF97C2AC889F2FB33856A1A8096A1DB091C4D25DB411E73E95E5D0FB7E0D16"
TARGET_SHA256 = "C683AE9355A43F9A2104E49A6179363727CE0A550682F906C224A44F506826AC"

TRANSLATED_IDS = (
    set(range(2329, 2349))
    | {2408, 2409, 2419, 2420, 2457, 2459, 2558, 2650, 2657, 2661}
    | set(range(2691, 2747))
)
PRESERVED_IDS = {
    513,
    689,
    691,
    1302,
    1350,
    1352,
    1694,
    *range(1921, 1933),
    2570,
    2571,
    2572,
}
STRUCTURAL_EMPTY_IDS = {733, 734, 1607}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(
                (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            )
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def require_exact_keys(value: Any, keys: set[str], label: str) -> None:
    require(isinstance(value, dict), f"{label} must be an object")
    actual = set(value)
    require(
        actual == keys,
        f"{label} keys mismatch: missing={sorted(keys - actual)!r}, "
        f"unknown={sorted(actual - keys)!r}",
    )


def has_cjk_or_kana(text: str) -> bool:
    return any(
        0x3040 <= ord(char) <= 0x30FF
        or 0x31F0 <= ord(char) <= 0x31FF
        or 0x3400 <= ord(char) <= 0x4DBF
        or 0x4E00 <= ord(char) <= 0x9FFF
        or 0xF900 <= ord(char) <= 0xFAFF
        for char in text
    )


def verify(project_root: Path) -> dict[str, Any]:
    workstream = project_root / "workstreams" / "msgui_full" / "asymmetric_v02"
    validation_path = workstream / "validation.json"
    overlay_v01_path = project_root / "data" / "public" / "msgui_ko_0000_5099.v0.1.json"
    overlay_v02_path = project_root / "data" / "public" / "msgui_ko_0000_5099.v0.2.json"
    recipe_path = workstream / "public" / "msgui_sc.recipe.json"
    demand_path = workstream / "public" / "glyph_demand.json"
    officer_demand_path = (
        project_root
        / "workstreams"
        / "officer_names"
        / "font_v5"
        / "corpus"
        / "msgui_0000_5099"
        / "glyph_demand.json"
    )

    validation = catalog.load_json_strict(validation_path)
    require(
        validation.get("schema") == "nobu16.kr.msgui-asymmetric-candidate-validation.v1",
        "validation schema mismatch",
    )
    require(validation.get("release_eligible") is False, "candidate must not be release eligible")
    require(
        validation.get("runtime_validation", {}).get("status") == "pending",
        "runtime status must remain pending",
    )

    expected_files = {
        overlay_v01_path: V01_SHA256,
        overlay_v02_path: V02_SHA256,
        recipe_path: RECIPE_SHA256,
        demand_path: DEMAND_SHA256,
        officer_demand_path: DEMAND_SHA256,
    }
    for path, expected_hash in expected_files.items():
        require(path.is_file(), f"missing required file: {path}")
        require(sha256_file(path) == expected_hash, f"hash mismatch: {path}")

    overlay_v01 = catalog.load_json_strict(overlay_v01_path)
    overlay_v02 = catalog.load_json_strict(overlay_v02_path)
    catalog.validate_translation_overlay_shape(overlay_v01)
    catalog.validate_translation_overlay_shape(overlay_v02)
    require(overlay_v01["entry_count"] == 3951, "v0.1 entry count mismatch")
    require(overlay_v02["entry_count"] == 4037, "v0.2 entry count mismatch")
    by_id_v01 = {int(item["id"]): item for item in overlay_v01["entries"]}
    by_id_v02 = {int(item["id"]): item for item in overlay_v02["entries"]}
    require(set(by_id_v02) - set(by_id_v01) == TRANSLATED_IDS, "v0.2 added ID set mismatch")
    require(not (set(by_id_v01) - set(by_id_v02)), "v0.2 removed a v0.1 entry")
    require(
        all(by_id_v01[entry_id] == by_id_v02[entry_id] for entry_id in by_id_v01),
        "v0.2 changed a pre-existing v0.1 entry",
    )
    require(PRESERVED_IDS.isdisjoint(by_id_v02), "language-specific blank was activated")
    require(STRUCTURAL_EMPTY_IDS.isdisjoint(by_id_v02), "structural blank was activated")
    require(
        not any(has_cjk_or_kana(item["ko"]) for item in overlay_v02["entries"]),
        "public overlay contains CJK ideographs or kana",
    )
    statuses = Counter(
        item.get("status", overlay_v02["defaults"]["status"])
        for item in overlay_v02["entries"]
    )
    require(statuses == Counter({"translated": 4019, "reviewed": 18}), "status counts mismatch")
    provenance = overlay_v02["development_batch_provenance"]
    provenance_skipped_total = sum(
        int(item["skipped_whitespace_entries"]) for item in provenance
    )
    require(len(provenance) == 47, "provenance batch count mismatch")
    require(provenance_skipped_total == 136, "provenance skipped total mismatch")

    recipe = catalog.load_json_strict(recipe_path)
    require_exact_keys(
        recipe,
        {
            "schema",
            "scope",
            "version",
            "language",
            "file_only",
            "source",
            "target",
            "operations",
            "operation_index",
            "payload_policy",
            "export_verification",
        },
        "message recipe root",
    )
    require(recipe["schema"] == "nobu16.file-only-msg-recipe.v1", "recipe schema mismatch")
    require(recipe["scope"] == "msgui_catalog_v2", "recipe scope mismatch")
    require(recipe["version"] == "0.2-dev", "recipe version mismatch")
    require(recipe["language"] == "SC", "recipe language mismatch")
    require(recipe["file_only"] is True, "recipe is not file-only")
    require_exact_keys(
        recipe["source"],
        {"relative_path", "size", "sha256", "raw_size", "raw_sha256", "string_count"},
        "message recipe source",
    )
    require_exact_keys(
        recipe["target"], {"size", "sha256", "raw_size", "raw_sha256"}, "message recipe target"
    )
    require(recipe["source"]["relative_path"] == "MSG_PK/SC/msgui.bin", "source path mismatch")
    require(
        recipe["source"]["sha256"]
        == "C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82",
        "stock hash mismatch",
    )
    require(recipe["target"]["sha256"] == TARGET_SHA256, "target hash mismatch")
    operations = recipe["operations"]
    require(isinstance(operations, list) and len(operations) == 3922, "operation count mismatch")
    operation_ids: list[int] = []
    for index, operation in enumerate(operations):
        require_exact_keys(
            operation,
            {"id", "source_utf16le_sha256", "replacement"},
            f"message recipe operation[{index}]",
        )
        entry_id = operation["id"]
        require(isinstance(entry_id, int) and not isinstance(entry_id, bool), "invalid operation ID")
        operation_ids.append(entry_id)
        overlay_entry = by_id_v02.get(entry_id)
        require(overlay_entry is not None, f"operation {entry_id} missing from overlay")
        require(
            operation["source_utf16le_sha256"]
            == overlay_entry["source_sc_utf16le_sha256"],
            f"operation {entry_id} source hash mismatch",
        )
        require(
            operation["replacement"] == overlay_entry["ko"],
            f"operation {entry_id} replacement mismatch",
        )
    require(operation_ids == sorted(set(operation_ids)), "operation IDs are not sorted unique")
    expected_operation_ids = [
        entry_id
        for entry_id, entry in sorted(by_id_v02.items())
        if entry["source_sc_utf16le_sha256"] != catalog.text_hash(entry["ko"])
    ]
    require(
        operation_ids == expected_operation_ids,
        "recipe does not cover exactly every effective overlay replacement",
    )
    operation_ids_hash = hashlib.sha256(
        json.dumps(operation_ids, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()
    require(
        operation_ids_hash == "EDABA5D0BDB939265288CC22E15379CD1C4C774DF3F798EA5B181F9F02638CAD",
        "operation ID hash mismatch",
    )
    require_exact_keys(
        recipe["operation_index"],
        {"count", "id_encoding", "ids_sha256", "sorted_unique"},
        "message recipe operation_index",
    )
    require(recipe["operation_index"] == {
        "count": len(operation_ids),
        "id_encoding": "UTF-8 compact JSON integer array",
        "ids_sha256": operation_ids_hash,
        "sorted_unique": True,
    }, "message recipe operation index mismatch")
    require(
        set(recipe["payload_policy"].values()) == {False, True},
        "recipe payload policy is malformed",
    )
    require(recipe["payload_policy"] == {
        "contains_complete_source": False,
        "contains_complete_target": False,
        "contains_executable_bytes": False,
        "source_text_is_stored_as_hash_only": True,
        "stock_file_is_required_at_apply_time": True,
        "development_catalog_included": False,
    }, "recipe payload policy mismatch")
    require_exact_keys(
        recipe["export_verification"],
        {
            "byte_identical_to_pinned_target",
            "table_parse_roundtrip",
            "wrapper_decompress_roundtrip",
            "build_manifest_sha256",
        },
        "message recipe export_verification",
    )
    require(
        recipe["export_verification"]["byte_identical_to_pinned_target"] is True
        and recipe["export_verification"]["table_parse_roundtrip"] is True
        and recipe["export_verification"]["wrapper_decompress_roundtrip"] is True,
        "message recipe export verification flags mismatch",
    )

    demand = catalog.load_json_strict(demand_path)
    officer_demand = catalog.load_json_strict(officer_demand_path)
    require(demand == officer_demand, "MSGUI demand differs from officer Font-v5 corpus")
    require(demand.get("character_count") == 625, "glyph count mismatch")
    require(demand.get("hangul_syllable_count") == 524, "Hangul syllable count mismatch")

    expected_validation = {
        "schema": "nobu16.kr.msgui-asymmetric-candidate-validation.v1",
        "candidate_id": "msgui_ko_0000_5099.v0.2",
        "date": "2026-07-14",
        "file_only": True,
        "installed_game_files_modified": False,
        "process_memory_access": False,
        "dll_injection_or_hooking": False,
        "executable_modified": False,
        "registry_modified": False,
        "classification": {
            "total_ids": 5100,
            "translated_or_reviewed": len(by_id_v02),
            "canonical_empty": 1041,
            "preserved_language_specific_blank": len(PRESERVED_IDS),
            "ordinary_sc_nonblank_untranslated": 0,
            "new_translations": {
                "count": len(TRANSLATED_IDS),
                "id_ranges": [
                    "2329-2348",
                    "2408-2409",
                    "2419-2420",
                    "2457",
                    "2459",
                    "2558",
                    "2650",
                    "2657",
                    "2661",
                    "2691-2746",
                ],
            },
            "preserved_language_specific_ids": sorted(PRESERVED_IDS),
            "structural_empty_ids": sorted(STRUCTURAL_EMPTY_IDS),
        },
        "catalog_validation": {
            "valid": True,
            "errors": 0,
            "warnings": 0,
            "status_counts": {
                "empty": 1041,
                "untranslated": len(PRESERVED_IDS),
                "translated": statuses["translated"],
                "reviewed": statuses["reviewed"],
            },
            "buildable_count": len(by_id_v02),
            "private_complete_catalog_sha256": (
                "B8BD5E53A630AAC14300342851F89C84F1CA50E8B4FAFBD9FEF5662D1A51A816"
            ),
        },
        "private_inputs": {
            "included_in_public_patch": False,
            "asymmetric_batch_sha256": (
                "80744EEFD24FBB79943C5EB1723A07D01EACCA199B5FB1BE0D3E11082D90D851"
            ),
            "structural_empty_batch_sha256": (
                "3D19016712120C6B04661A3AB173467B0AAA431DBCC141C4D7D5ACFA27E71AB4"
            ),
        },
        "public_overlay": {
            "path": "../../../data/public/msgui_ko_0000_5099.v0.2.json",
            "size": overlay_v02_path.stat().st_size,
            "sha256": sha256_file(overlay_v02_path),
            "entry_count": len(by_id_v02),
            "translated_count": statuses["translated"],
            "reviewed_count": statuses["reviewed"],
            "provenance_batch_count": len(provenance),
            "skipped_whitespace_entry_count": overlay_v02[
                "skipped_whitespace_entry_count"
            ],
            "provenance_skipped_whitespace_total": provenance_skipped_total,
            "contains_commercial_source_text": overlay_v02["distribution_policy"][
                "contains_commercial_source_text"
            ],
            "contains_complete_game_resource": overlay_v02["distribution_policy"][
                "contains_complete_game_resource"
            ],
            "strict_schema_valid": True,
            "deterministic_two_builds": True,
        },
        "message_recipe": {
            "path": "public/msgui_sc.recipe.json",
            "size": recipe_path.stat().st_size,
            "sha256": sha256_file(recipe_path),
            "operation_count": len(operation_ids),
            "operation_ids_sha256": operation_ids_hash,
            "source_sha256": recipe["source"]["sha256"],
            "target_size": recipe["target"]["size"],
            "target_sha256": recipe["target"]["sha256"],
            "target_raw_size": recipe["target"]["raw_size"],
            "target_raw_sha256": recipe["target"]["raw_sha256"],
            "deterministic_two_builds": True,
            "stock_replay_target_exact": True,
        },
        "glyph_demand": {
            "path": "public/glyph_demand.json",
            "sha256": sha256_file(demand_path),
            "character_count": demand["character_count"],
            "hangul_syllable_count": demand["hangul_syllable_count"],
            "byte_exact_with_officer_font_v5_msgui_demand": demand == officer_demand,
        },
        "runtime_validation": {
            "status": "pending",
            "all_86_sc_blank_slots_require_context_qa": True,
            "specific_semantic_conflict_ids": [2729, 2730],
        },
        "release_eligible": False,
    }
    require(
        validation == expected_validation,
        "validation.json does not exactly match recomputed candidate evidence",
    )

    return {
        "schema": "nobu16.kr.msgui-asymmetric-source-free-verification.v1",
        "valid": True,
        "overlay_entries": len(by_id_v02),
        "new_translations": len(TRANSLATED_IDS),
        "preserved_language_specific": len(PRESERVED_IDS),
        "structural_empty": len(STRUCTURAL_EMPTY_IDS),
        "message_operations": len(operations),
        "overlay_sha256": V02_SHA256,
        "recipe_sha256": RECIPE_SHA256,
        "target_sha256": TARGET_SHA256,
        "glyph_demand_sha256": DEMAND_SHA256,
        "release_eligible": False,
        "runtime_validation": "pending",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--report", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = verify(args.project_root.resolve())
    if args.report:
        atomic_json(args.report.resolve(), report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
