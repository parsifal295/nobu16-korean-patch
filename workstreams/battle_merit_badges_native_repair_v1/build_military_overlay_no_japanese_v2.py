#!/usr/bin/env python3
"""Build tmp-only military-overlay candidates with no Japanese UI remnants.

The high candidate is the previously verified native-badge repair.  The low
candidate starts from the stock Japanese 2048x512 atlas, clears all seven
inventoried Japanese UI-image regions, and pastes only independently
downsampled Korean elements from the verified high atlas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_battle_merit_badges_native_repair_v1 as v1  # noqa: E402


SCHEMA = "nobu16.kr.military-overlay-no-japanese.v2"
EXPECTED_INPUTS: Mapping[str, Mapping[str, Any]] = {
    "current_low": {
        "size": 154714237,
        "sha256": "952B97FAE48F5D077E4663EFBE7B2975ADDBC0A521E63F9EDE373D7A77D55600",
    },
    "current_high": {
        "size": 82905500,
        "sha256": "E2B22DFD399E87DF109947F0F98FC58D1BF360B1B54299A6BB4D2051CE53EEA5",
    },
    "stock_high": {
        "size": 79243911,
        "sha256": "00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7",
    },
    "stock_low": {
        "size": 154216023,
        "sha256": "0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0",
    },
    "repaired_high": {
        "size": 82910041,
        "sha256": "BC4C87DD1D93BF944929E6341517828365C59203913E98302DF1A843571623D2",
    },
}

ELEMENTS: tuple[Mapping[str, Any], ...] = (
    {
        "id": "military_assessment_heading",
        "label": "군평정",
        "high_korean_source": (56, 317, 1145, 720),
        "high_japanese_bbox": (46, 288, 1215, 765),
        "high_clear_provenance": (0, 288, 1264, 944),
        "low_japanese_bbox": (5, 121, 629, 410),
        "low_clear_rect": (4, 120, 632, 412),
        "low_korean_target": (44, 163, 589, 365),
    },
    {
        "id": "victory_result",
        "label": "승리",
        "high_korean_source": (2603, 399, 2946, 578),
        "high_japanese_bbox": (2559, 409, 2938, 618),
        "high_clear_provenance": (2080, 350, 2968, 620),
        "low_japanese_bbox": (645, 400, 835, 503),
        "low_clear_rect": (640, 396, 840, 508),
        "low_korean_target": (654, 406, 826, 496),
    },
    {
        "id": "defeat_result",
        "label": "패배",
        "high_korean_source": (2147, 404, 2492, 576),
        "high_japanese_bbox": (2151, 412, 2520, 612),
        "high_clear_provenance": (2080, 350, 2968, 620),
        "low_japanese_bbox": (1843, 332, 2038, 434),
        "low_clear_rect": (1840, 328, 2040, 436),
        "low_korean_target": (1855, 339, 2028, 425),
    },
    {
        "id": "button_prompt",
        "label": "아무 버튼이나 누르십시오.",
        "high_korean_source": (1385, 774, 2127, 826),
        "high_japanese_bbox": (1275, 771, 2166, 829),
        "high_clear_provenance": (1264, 760, 2600, 900),
        "low_japanese_bbox": (1081, 209, 1530, 242),
        "low_clear_rect": (1080, 208, 1532, 244),
        "low_korean_target": (1121, 213, 1492, 239),
    },
    {
        "id": "merit_rank_1",
        "label": "전공 1위",
        "high_korean_source": (2960, 400, 3344, 480),
        "high_japanese_bbox": (2960, 400, 3344, 480),
        "high_clear_provenance": (2960, 383, 3364, 480),
        "low_japanese_bbox": (1082, 254, 1274, 294),
        "low_clear_rect": (1082, 254, 1274, 294),
        "low_korean_target": (1082, 254, 1274, 294),
    },
    {
        "id": "merit_rank_2",
        "label": "전공 2위",
        "high_korean_source": (2982, 500, 3322, 572),
        "high_japanese_bbox": (2982, 500, 3322, 572),
        "high_clear_provenance": (2982, 485, 3346, 572),
        "low_japanese_bbox": (1297, 256, 1467, 292),
        "low_clear_rect": (1297, 256, 1467, 292),
        "low_korean_target": (1297, 256, 1467, 292),
    },
    {
        "id": "merit_rank_3",
        "label": "전공 3위",
        "high_korean_source": (3686, 644, 4026, 716),
        "high_japanese_bbox": (3686, 644, 4026, 716),
        "high_clear_provenance": (3686, 625, 4029, 716),
        "low_japanese_bbox": (1501, 256, 1671, 292),
        "low_clear_rect": (1501, 256, 1671, 292),
        "low_korean_target": (1501, 256, 1671, 292),
    },
)


class NoJapaneseError(ValueError):
    """Raised when complete Japanese-remnant removal cannot be proven."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise NoJapaneseError(message)


def alpha_pixel_count(
    rgba: bytes,
    width: int,
    height: int,
    rect: Sequence[int],
    *,
    threshold: int = 1,
) -> int:
    require(len(rgba) == width * height * 4, "alpha count RGBA geometry differs")
    left, top, right, bottom = (int(value) for value in rect)
    require(0 <= left < right <= width and 0 <= top < bottom <= height, "alpha count rectangle escapes canvas")
    return sum(
        rgba[(y * width + x) * 4 + 3] >= threshold
        for y in range(top, bottom)
        for x in range(left, right)
    )


def validate_contract() -> None:
    safe_ids = [str(row["id"]) for row in v1.military.SAFE_MAPPINGS]
    audit_ids = [str(row["id"]) for row in v1.military.AUDIT_ONLY_MAPPINGS]
    inventory_ids = [str(row["id"]) for row in ELEMENTS]
    require(len(ELEMENTS) == 7, "Japanese-image inventory is not seven groups")
    require(set(inventory_ids) == set(safe_ids + audit_ids), "Japanese-image inventory differs from the audited seven mappings")
    clears: list[tuple[int, int, int, int]] = []
    targets: list[tuple[int, int, int, int]] = []
    for row in ELEMENTS:
        source = tuple(row["high_korean_source"])
        japanese = tuple(row["low_japanese_bbox"])
        clear = tuple(row["low_clear_rect"])
        target = tuple(row["low_korean_target"])
        source_width, source_height = v1.rect_dimensions(source)
        target_width, target_height = v1.rect_dimensions(target)
        require(
            (target_width, target_height)
            == ((source_width + 1) // 2, (source_height + 1) // 2),
            f"high-to-low scale is not rounded 2:1: {row['id']}",
        )
        require(v1.rect_contains(clear, japanese), f"Japanese bbox escapes clear rectangle: {row['id']}")
        require(v1.rect_contains(clear, target), f"Korean target escapes clear rectangle: {row['id']}")
        require(
            v1.rect_contains(row["high_clear_provenance"], row["high_japanese_bbox"]),
            f"high Japanese bbox escapes its clear provenance: {row['id']}",
        )
        clears.append(clear)
        targets.append(target)
    for index, left in enumerate(clears):
        for right in clears[index + 1 :]:
            require(not v1.rectangles_overlap(left, right), "low clear rectangles overlap")
    for index, left in enumerate(targets):
        for right in targets[index + 1 :]:
            require(not v1.rectangles_overlap(left, right), "low Korean targets overlap")


def write_png(
    path: Path,
    rgba: bytes,
    width: int,
    height: int,
    *,
    forbidden: Iterable[Path],
) -> dict[str, Any]:
    return v1.write_png(path, rgba, width, height, forbidden=forbidden)


def build_detail_contact(
    stock_rgba: bytes,
    candidate_rgba: bytes,
    output_root: Path,
    *,
    forbidden: Iterable[Path],
) -> dict[str, Any]:
    gutter = 8
    max_width = max(v1.rect_dimensions(row["low_clear_rect"])[0] for row in ELEMENTS)
    max_height = max(v1.rect_dimensions(row["low_clear_rect"])[1] for row in ELEMENTS)
    canvas_width = gutter + 2 * (max_width + gutter)
    canvas_height = gutter + len(ELEMENTS) * (max_height + gutter)
    canvas = bytearray(canvas_width * canvas_height * 4)
    rows: list[dict[str, Any]] = []
    for row_index, row in enumerate(ELEMENTS):
        clear = tuple(row["low_clear_rect"])
        width, height = v1.rect_dimensions(clear)
        before = bytearray(v1.crop_rgba(stock_rgba, *v1.LOW_GEOMETRY, clear))
        after = bytearray(v1.crop_rgba(candidate_rgba, *v1.LOW_GEOMETRY, clear))
        v1.add_border(before, width, height, (232, 72, 72, 255))
        v1.add_border(after, width, height, (72, 216, 112, 255))
        y = gutter + row_index * (max_height + gutter)
        v1.military.paste_rgba(canvas, canvas_width, gutter, y, bytes(before), width, height)
        v1.military.paste_rgba(canvas, canvas_width, gutter + max_width + gutter, y, bytes(after), width, height)
        rows.append(
            {
                "id": row["id"],
                "label": row["label"],
                "clear_rect": list(clear),
                "panels_left_to_right": ["stock_japanese", "candidate_korean"],
                "panel_dimensions": [width, height],
            }
        )
    path = output_root / "private" / "all_seven_japanese_to_korean_contact.png"
    record = write_png(path, bytes(canvas), canvas_width, canvas_height, forbidden=forbidden)
    record["rows"] = rows
    record["legend"] = {"red": "stock Japanese group", "green": "candidate Korean group"}
    return record


def build_full_contact(
    stock_rgba: bytes,
    candidate_rgba: bytes,
    output_root: Path,
    *,
    forbidden: Iterable[Path],
) -> dict[str, Any]:
    width, height = v1.LOW_GEOMETRY
    canvas = bytearray(width * 2 * height * 4)
    v1.military.paste_rgba(canvas, width * 2, 0, 0, stock_rgba, width, height)
    v1.military.paste_rgba(canvas, width * 2, width, 0, candidate_rgba, width, height)
    path = output_root / "private" / "low_stock_japanese_vs_all_korean_candidate.png"
    record = write_png(path, bytes(canvas), width * 2, height, forbidden=forbidden)
    record["panels_left_to_right"] = ["stock_japanese_atlas", "candidate_korean_atlas"]
    return record


def build(args: argparse.Namespace) -> dict[str, Any]:
    validate_contract()
    paths = {
        "current_low": args.current_low.resolve(),
        "current_high": args.current_high.resolve(),
        "stock_high": args.stock_high.resolve(),
        "stock_low": args.stock_low.resolve(),
        "repaired_high": args.repaired_high.resolve(),
    }
    inputs = {
        name: v1.require_spec(path, EXPECTED_INPUTS[name], name.replace("_", " "))
        for name, path in paths.items()
    }
    forbidden = tuple(paths.values())
    output_root = v1.military.create_fresh_output_root(args.output_root.resolve())

    print("stage=parse_inputs", flush=True)
    current_low = v1.parse_route(paths["current_low"], v1.LOW_OUTER, v1.LOW_GEOMETRY, "current low")
    current_high = v1.parse_route(paths["current_high"], v1.HIGH_OUTER, v1.HIGH_GEOMETRY, "current high")
    stock_high = v1.parse_route(paths["stock_high"], v1.HIGH_OUTER, v1.HIGH_GEOMETRY, "stock high")
    stock_low = v1.parse_route(paths["stock_low"], v1.LOW_OUTER, v1.LOW_GEOMETRY, "stock low")
    repaired_high = v1.parse_route(paths["repaired_high"], v1.HIGH_OUTER, v1.HIGH_GEOMETRY, "repaired high")

    high_before_outer = v1.outer_hashes(current_high.outer)
    high_after_outer = v1.outer_hashes(repaired_high.outer)
    high_changed_outers = [
        index
        for index in range(len(current_high.outer.entries))
        if high_before_outer[str(index)] != high_after_outer[str(index)]
    ]
    require(high_changed_outers == [v1.HIGH_OUTER], f"repaired high outer scope differs: {high_changed_outers}")
    require(
        all(
            current_high.outer.entries[index].data == repaired_high.outer.entries[index].data
            for index in range(len(current_high.outer.entries))
            if index != v1.HIGH_OUTER
        ),
        "repaired high changed an unrelated outer",
    )

    print("stage=audit_high_japanese_inventory", flush=True)
    high_audit_rows: list[dict[str, Any]] = []
    for row in ELEMENTS:
        source = tuple(row["high_korean_source"])
        source_width, source_height = v1.rect_dimensions(source)
        source_rgba = v1.crop_rgba(repaired_high.rgba, *v1.HIGH_GEOMETRY, source)
        require(
            v1.alpha_bbox(source_rgba, source_width, source_height) == (0, 0, source_width, source_height),
            f"high Korean source bbox is not exact: {row['id']}",
        )
        japanese_alpha = alpha_pixel_count(
            stock_high.rgba,
            *v1.HIGH_GEOMETRY,
            row["high_japanese_bbox"],
        )
        require(japanese_alpha > 0, f"stock high Japanese proof is empty: {row['id']}")
        require(
            v1.rect_contains(row["high_clear_provenance"], row["high_japanese_bbox"]),
            f"stock high Japanese bbox escaped clear provenance: {row['id']}",
        )
        high_audit_rows.append(
            {
                "id": row["id"],
                "label": row["label"],
                "stock_high_japanese_bbox": list(row["high_japanese_bbox"]),
                "stock_high_japanese_alpha_pixels": japanese_alpha,
                "full_clear_provenance": list(row["high_clear_provenance"]),
                "korean_source_bbox": list(source),
                "korean_source_rgba_sha256": v1.sha256_bytes(source_rgba),
                "japanese_bbox_fully_inside_clear_provenance": True,
            }
        )

    print("stage=clear_all_low_japanese_groups", flush=True)
    requested = bytearray(stock_low.rgba)
    allowed: set[tuple[int, int]] = set()
    low_rows: list[dict[str, Any]] = []
    for row in ELEMENTS:
        japanese_alpha = alpha_pixel_count(
            stock_low.rgba,
            *v1.LOW_GEOMETRY,
            row["low_japanese_bbox"],
        )
        require(japanese_alpha > 0, f"stock low Japanese proof is empty: {row['id']}")
        v1.clear_rect(requested, *v1.LOW_GEOMETRY, row["low_clear_rect"])
        blocks = v1.rect_blocks(row["low_clear_rect"], *v1.LOW_GEOMETRY)
        require(not allowed.intersection(blocks), f"low clear block sets overlap: {row['id']}")
        allowed.update(blocks)
        low_rows.append(
            {
                "id": row["id"],
                "label": row["label"],
                "stock_japanese_bbox": list(row["low_japanese_bbox"]),
                "stock_japanese_alpha_pixels_cleared": japanese_alpha,
                "clear_rect": list(row["low_clear_rect"]),
                "korean_target": list(row["low_korean_target"]),
            }
        )
    for row in ELEMENTS:
        require(
            alpha_pixel_count(bytes(requested), *v1.LOW_GEOMETRY, row["low_clear_rect"]) == 0,
            f"clear rectangle still contains alpha before Korean paste: {row['id']}",
        )

    print("stage=paste_all_korean_groups", flush=True)
    for report_row, row in zip(low_rows, ELEMENTS):
        source_rect = tuple(row["high_korean_source"])
        target_rect = tuple(row["low_korean_target"])
        source_width, source_height = v1.rect_dimensions(source_rect)
        target_width, target_height = v1.rect_dimensions(target_rect)
        source = v1.crop_rgba(repaired_high.rgba, *v1.HIGH_GEOMETRY, source_rect)
        korean = v1.resize_rgba(source, source_width, source_height, target_width, target_height)
        require(
            v1.alpha_bbox(korean, target_width, target_height) == (0, 0, target_width, target_height),
            f"downsampled Korean bbox is not exact: {row['id']}",
        )
        v1.paste_rect(requested, v1.LOW_GEOMETRY[0], target_rect, korean)
        require(
            v1.alpha_pixels_outside(
                bytes(requested),
                *v1.LOW_GEOMETRY,
                row["low_clear_rect"],
                target_rect,
                threshold=1,
            )
            == 0,
            f"alpha remains outside Korean target inside clear rectangle: {row['id']}",
        )
        report_row.update(
            {
                "high_korean_source": list(source_rect),
                "high_korean_source_rgba_sha256": v1.sha256_bytes(source),
                "low_korean_rgba_sha256": v1.sha256_bytes(korean),
                "high_source_dimensions": [source_width, source_height],
                "low_target_dimensions": [target_width, target_height],
                "resampler": "deterministic premultiplied-alpha Lanczos3, rounded exact 1/2 dimensions",
                "alpha_outside_korean_target_inside_clear": 0,
            }
        )

    low_payload, encoded = v1.encode_selected_blocks(
        bytes(requested),
        *v1.LOW_GEOMETRY,
        stock_low.texture.payload,
        allowed,
    )
    changed_from_stock = v1.changed_blocks(
        stock_low.texture.payload,
        low_payload,
        *v1.LOW_GEOMETRY,
    )
    require(changed_from_stock and changed_from_stock <= allowed, "low payload changed outside the seven clear regions")
    low_candidate_blob = v1.replace_route_payload(current_low, low_payload)

    print("stage=write_candidates", flush=True)
    high_candidate_path = output_root / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port1.bin"
    low_candidate_path = output_root / "candidate" / "RES_JP" / "res_lang.bin"
    v1.military.atomic_write(high_candidate_path, repaired_high.blob, forbidden=forbidden)
    v1.military.atomic_write(low_candidate_path, low_candidate_blob, forbidden=forbidden)
    high_candidate = v1.parse_route(high_candidate_path, v1.HIGH_OUTER, v1.HIGH_GEOMETRY, "v2 high candidate")
    low_candidate = v1.parse_route(low_candidate_path, v1.LOW_OUTER, v1.LOW_GEOMETRY, "v2 low candidate")
    require(high_candidate.blob == repaired_high.blob, "v2 high candidate is not byte-identical to repaired high")
    require(low_candidate.texture.payload == low_payload, "v2 low candidate payload differs")

    print("stage=verify_zero_japanese_provenance", flush=True)
    for report_row, row in zip(low_rows, ELEMENTS):
        clear = tuple(row["low_clear_rect"])
        target = tuple(row["low_korean_target"])
        target_width, target_height = v1.rect_dimensions(target)
        target_crop = v1.crop_rgba(low_candidate.rgba, *v1.LOW_GEOMETRY, target)
        candidate_bbox = v1.alpha_bbox(target_crop, target_width, target_height, threshold=1)
        require(candidate_bbox is not None, f"candidate Korean target is empty: {row['id']}")
        require(
            candidate_bbox[2] - candidate_bbox[0] >= target_width - 4
            and candidate_bbox[3] - candidate_bbox[1] >= target_height - 4,
            f"candidate Korean target shrank excessively: {row['id']} {candidate_bbox}",
        )
        outside = v1.alpha_pixels_outside(
            low_candidate.rgba,
            *v1.LOW_GEOMETRY,
            clear,
            target,
            threshold=1,
        )
        require(outside == 0, f"candidate contains alpha outside Korean target in cleared Japanese region: {row['id']}")
        report_row["candidate_alpha_bbox"] = [
            candidate_bbox[0] + target[0],
            candidate_bbox[1] + target[1],
            candidate_bbox[2] + target[0],
            candidate_bbox[3] + target[1],
        ]
        report_row["candidate_alpha_outside_target_inside_clear"] = outside
        report_row["remaining_original_japanese_groups"] = 0

    low_before_outer = v1.outer_hashes(current_low.outer)
    low_after_outer = v1.outer_hashes(low_candidate.outer)
    low_changed_outers = [
        index
        for index in range(len(current_low.outer.entries))
        if low_before_outer[str(index)] != low_after_outer[str(index)]
    ]
    require(low_changed_outers == [v1.LOW_OUTER], f"low changed outer scope differs: {low_changed_outers}")
    require(
        all(
            current_low.outer.entries[index].data == low_candidate.outer.entries[index].data
            for index in range(len(current_low.outer.entries))
            if index != v1.LOW_OUTER
        ),
        "low candidate changed an unrelated outer",
    )
    blocks_wide = v1.LOW_GEOMETRY[0] // 4
    require(
        all(
            stock_low.texture.payload[(y * blocks_wide + x) * 16 : (y * blocks_wide + x) * 16 + 16]
            == low_candidate.texture.payload[(y * blocks_wide + x) * 16 : (y * blocks_wide + x) * 16 + 16]
            for y in range(v1.LOW_GEOMETRY[1] // 4)
            for x in range(blocks_wide)
            if (x, y) not in allowed
        ),
        "low non-target BC3 block differs from stock",
    )

    print("stage=write_visual_qa", flush=True)
    private_root = v1.military.ensure_tmp(output_root / "private", mkdir=True)
    high_full = write_png(
        private_root / "high_all_korean_atlas.png",
        high_candidate.rgba,
        *v1.HIGH_GEOMETRY,
        forbidden=forbidden + (high_candidate_path, low_candidate_path),
    )
    low_full = write_png(
        private_root / "low_all_korean_atlas.png",
        low_candidate.rgba,
        *v1.LOW_GEOMETRY,
        forbidden=forbidden + (high_candidate_path, low_candidate_path),
    )
    detail_contact = build_detail_contact(
        stock_low.rgba,
        low_candidate.rgba,
        output_root,
        forbidden=forbidden + (high_candidate_path, low_candidate_path),
    )
    full_contact = build_full_contact(
        stock_low.rgba,
        low_candidate.rgba,
        output_root,
        forbidden=forbidden + (high_candidate_path, low_candidate_path),
    )

    inputs_after = {name: v1.file_spec(path) for name, path in paths.items()}
    require(inputs_after == inputs, "an input changed during v2 build")
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "result": "PASS",
        "plan_review": "PASS",
        "file_only": True,
        "game_install_modified": False,
        "release_modified": False,
        "git_commit_or_push_performed": False,
        "runtime_qa": {
            "performed": False,
            "reported_resolution": "1920x1080",
            "full_process_restart_completed": None,
            "reason": "Steam deployment is forbidden for in-progress candidates",
        },
        "inputs": {
            name: {"path": str(paths[name]), **inputs[name]}
            for name in paths
        },
        "inventory": {
            "audited_japanese_image_groups": 7,
            "cleared_japanese_image_groups": 7,
            "remaining_original_japanese_groups": 0,
            "alpha_threshold_for_zero_remnant_proof": 1,
            "ids": [row["id"] for row in ELEMENTS],
            "matches_safe_plus_audit_only_inventory": True,
        },
        "high": {
            "candidate": {"path": str(high_candidate_path), **v1.file_spec(high_candidate_path)},
            "byte_identical_to_native_badge_repair_build_002": True,
            "changed_outer_entries_from_current": high_changed_outers,
            "all_non_17_outer_entries_byte_preserved": True,
            "japanese_clearance_audit": high_audit_rows,
            "full_atlas_png": high_full,
        },
        "low": {
            "candidate": {"path": str(low_candidate_path), **v1.file_spec(low_candidate_path)},
            "stock_payload_sha256": v1.sha256_bytes(stock_low.texture.payload),
            "candidate_payload_sha256": v1.sha256_bytes(low_candidate.texture.payload),
            "allowed_seven_group_bc3_blocks": len(allowed),
            "encoded_bc3_blocks": encoded,
            "changed_bc3_blocks_from_stock": len(changed_from_stock),
            "changed_block_bbox": v1.changed_block_bbox(changed_from_stock),
            "changed_outer_entries_from_current": low_changed_outers,
            "all_non_12_outer_entries_byte_preserved_from_current": True,
            "all_non_target_blocks_byte_preserved_from_stock": True,
            "all_seven_clear_rects_zero_alpha_before_korean_paste": True,
            "all_seven_groups_replaced_from_verified_high_korean_sources": True,
            "zero_remnant_alpha_threshold": 1,
            "remaining_original_japanese_groups": 0,
            "groups": low_rows,
            "full_atlas_png": low_full,
        },
        "visual_qa": {
            "seven_group_contact": detail_contact,
            "full_low_atlas_contact": full_contact,
        },
        "private_output_policy": {
            "under_ignored_tmp": True,
            "steam_apply_allowed": False,
            "release_upload_allowed": False,
            "git_publish_game_payload_allowed": False,
        },
    }
    report_path = output_root / "build_report.json"
    v1.military.write_json(
        report_path,
        report,
        forbidden=forbidden + (high_candidate_path, low_candidate_path),
    )
    print(
        json.dumps(
            {
                "result": "PASS",
                "remaining_original_japanese_groups": 0,
                "high_candidate": report["high"]["candidate"],
                "low_candidate": report["low"]["candidate"],
                "report": str(report_path),
                "seven_group_contact": detail_contact["path"],
                "full_low_contact": full_contact["path"],
                "game_install_modified": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )
    return report


def verify(output_root: Path) -> dict[str, Any]:
    output_root = v1.military.ensure_tmp(output_root.resolve())
    report_path = v1.military.ensure_tmp(output_root / "build_report.json")
    require(report_path.is_file(), f"missing v2 build report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA and report.get("result") == "PASS", "v2 report schema/result differs")
    require(report.get("game_install_modified") is False and report.get("release_modified") is False, "v2 write scope changed")
    inventory = report.get("inventory")
    require(
        isinstance(inventory, Mapping)
        and inventory.get("audited_japanese_image_groups") == 7
        and inventory.get("cleared_japanese_image_groups") == 7
        and inventory.get("remaining_original_japanese_groups") == 0,
        "v2 Japanese inventory proof differs",
    )
    require(inventory.get("alpha_threshold_for_zero_remnant_proof") == 1, "zero-remnant alpha threshold differs")
    for route_name, outer, geometry in (
        ("high", v1.HIGH_OUTER, v1.HIGH_GEOMETRY),
        ("low", v1.LOW_OUTER, v1.LOW_GEOMETRY),
    ):
        candidate = report[route_name]["candidate"]
        path = v1.military.ensure_tmp(Path(candidate["path"]))
        require(path.is_file() and v1.file_spec(path) == {"size": candidate["size"], "sha256": candidate["sha256"]}, f"{route_name} candidate hash differs")
        v1.parse_route(path, outer, geometry, f"verified v2 {route_name}")
    require(report["high"]["byte_identical_to_native_badge_repair_build_002"] is True, "high identity gate lost")
    require(report["low"]["all_non_target_blocks_byte_preserved_from_stock"] is True, "low stock preservation gate lost")
    require(report["low"]["all_seven_clear_rects_zero_alpha_before_korean_paste"] is True, "seven-group clear gate lost")
    require(report["low"]["zero_remnant_alpha_threshold"] == 1, "low zero-remnant threshold differs")
    require(report["low"]["remaining_original_japanese_groups"] == 0, "Japanese groups remain")
    for row in report["low"]["groups"]:
        require(row["remaining_original_japanese_groups"] == 0, f"Japanese group remains: {row['id']}")
        require(row["candidate_alpha_outside_target_inside_clear"] == 0, f"residual alpha outside Korean target: {row['id']}")
    visual_paths = [
        report["high"]["full_atlas_png"],
        report["low"]["full_atlas_png"],
        report["visual_qa"]["seven_group_contact"],
        report["visual_qa"]["full_low_atlas_contact"],
    ]
    for record in visual_paths:
        path = v1.military.ensure_tmp(Path(record["path"]))
        require(path.is_file() and v1.sha256_file(path) == record["sha256"], f"visual QA hash differs: {path}")
    result = {
        "result": "PASS",
        "schema": SCHEMA,
        "remaining_original_japanese_groups": 0,
        "high_candidate": report["high"]["candidate"],
        "low_candidate": report["low"]["candidate"],
        "game_install_modified": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build", help="build no-Japanese high/low candidates and visual QA")
    build_parser.add_argument("--current-low", type=Path, required=True)
    build_parser.add_argument("--current-high", type=Path, required=True)
    build_parser.add_argument("--stock-high", type=Path, required=True)
    build_parser.add_argument("--stock-low", type=Path, required=True)
    build_parser.add_argument("--repaired-high", type=Path, required=True)
    build_parser.add_argument("--output-root", type=Path, required=True)
    verify_parser = commands.add_parser("verify", help="verify an existing v2 output")
    verify_parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        build(args)
    else:
        verify(args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
