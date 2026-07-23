#!/usr/bin/env python3
"""Prepare PC-only MS GEV name-reading consistency candidates.

This is a review generator, never an applicator.  It identifies only an
especially narrow class of corrections: an MS GEV entry whose complete
Japanese label is identical to a pristine PC ``ev_strdata``/``strdata`` label,
and whose Korean becomes *exactly* the live PC static Korean label after every
``\uce20`` (츠) in that MS GEV entry is changed to ``\uc4f0`` (쓰).  A label
with any other difference is deliberately held rather than inferred.

The generator opens only PC Japanese sources and live PC Korean resources.  It
does not declare or open Switch paths or historical Korean backups, does not
change line breaks, and writes no game resource or review artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PC_BASE_SOURCE_ROOT = Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root")
PC_PK_JP_ORIGINAL = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
PC_STRDATA_JP_ORIGINAL = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG"
    / "JP"
    / "strdata.bin"
)

TMP_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
SEMANTIC_ROOT = TMP_ROOT / "semantic"
PROPOSAL_ROOT = TMP_ROOT / "proposals"
OUTPUT = SEMANTIC_ROOT / "msgev_tsu_to_sseu_static_consistency_candidates.v1.jsonl"
HOLD_OUTPUT = SEMANTIC_ROOT / "msgev_tsu_to_sseu_static_consistency_holds.v1.jsonl"

REVIEW_BATCH = "msgev_tsu_to_sseu_static_consistency_v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
TABLE_COUNT = 17_916
MAX_LOGICAL_COLUMNS = 76
TSU = "\uce20"
SSEU = "\uc4f0"

EXPECTED_HASHES = {
    "msgev_jp": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "msgev_ko": "B8B3B1C5A635419E590DB866C240A1B6609799E0FEA0E69F86D6208F27E5C52B",
    "ev_strdata_jp": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
    "ev_strdata_ko": "6A7D90C1A95AD42DCAE2D3C3719508EDD00588288659A1D192B680CF70EAE6E4",
    "strdata_jp": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "strdata_ko": "D518A91E36B9A59EAD0B5ED1FDD067941E4BF72E43AFCB19C296C8AD77C8C128",
}

# These are emitted by the adjacent semantic audit generator.  Keep this
# reading-consistency batch disjoint even before that private JSONL is added.
SEMANTIC_BATCH_COORDINATES = {
    3986,
    4258,
    5647,
    7310,
    8128,
    8512,
    8739,
    9753,
    9771,
    10817,
    10856,
}

ESC_TOKEN_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ID_RE = re.compile(r'"id"\s*:\s*(\d+)')
HAN_ONLY_RE = re.compile(r"^[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+$")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")


@dataclass(frozen=True)
class StaticSpec:
    resource: str
    pristine_jp_path: Path
    live_ko_path: Path
    parser_name: str
    jp_hash_key: str
    ko_hash_key: str


@dataclass(frozen=True)
class StaticAnchor:
    resource: str
    coordinate: str
    japanese: str
    korean: str


STATIC_SPECS = (
    StaticSpec(
        resource="ev_strdata",
        pristine_jp_path=PC_BASE_SOURCE_ROOT / "MSG" / "JP" / "ev_strdata.bin",
        live_ko_path=STEAM_ROOT / "MSG" / "JP" / "ev_strdata.bin",
        parser_name="common",
        jp_hash_key="ev_strdata_jp",
        ko_hash_key="ev_strdata_ko",
    ),
    StaticSpec(
        resource="strdata",
        pristine_jp_path=PC_STRDATA_JP_ORIGINAL,
        live_ko_path=STEAM_ROOT / "MSG" / "JP" / "strdata.bin",
        parser_name="strdata",
        jp_hash_key="strdata_jp",
        ko_hash_key="strdata_ko",
    ),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def file_hash(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load parser module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_common(path: Path) -> dict[str, str]:
    sys.path.insert(0, str(REPO / "tools"))
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table

    _header, raw = decompress_wrapper(path.read_bytes())
    return {str(index): text for index, text in enumerate(parse_message_table(raw).texts)}


def parse_strdata(path: Path) -> dict[str, str]:
    sys.path.insert(0, str(REPO / "tools"))
    from nobu16_lz4 import decompress_wrapper

    strdata = load_module(
        "msgev_tsu_to_sseu_strdata_format",
        REPO / "workstreams" / "strdata" / "strdata_format.py",
    )
    _header, raw = decompress_wrapper(path.read_bytes())
    archive = strdata.parse_raw_strdata(raw)
    return {
        f"{block}:{slot}": text
        for (block, slot), text in strdata.coordinate_texts(archive).items()
    }


PARSERS: dict[str, Callable[[Path], dict[str, str]]] = {
    "common": parse_common,
    "strdata": parse_strdata,
}


def visible(text: str) -> str:
    return ESC_TOKEN_RE.sub("", text)


def format_signature(text: str) -> dict[str, Any]:
    return {
        "escape_tokens": ESC_TOKEN_RE.findall(text),
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf_tokens": PRINTF_RE.findall(text),
        "linebreaks": re.findall(r"\r\n|\n|\r", text),
        "leading_ascii_whitespace": text[: len(text) - len(text.lstrip(" \t"))],
        "trailing_ascii_whitespace": text[len(text.rstrip(" \t")) :],
    }


def logical_columns(line: str) -> int:
    rendered = ESC_TOKEN_RE.sub("", line)
    rendered = RUNTIME_RE.sub("XXXXXXXX", rendered)
    result = 0
    for char in rendered:
        if unicodedata.combining(char):
            continue
        result += 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
    return result


def layout(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    return {
        "line_count": len(lines),
        "logical_display_columns": [logical_columns(line) for line in lines],
    }


def only_tsu_to_sseu(current: str, proposed: str) -> bool:
    if len(current) != len(proposed):
        return False
    changes = [(before, after) for before, after in zip(current, proposed) if before != after]
    return bool(changes) and all(before == TSU and after == SSEU for before, after in changes)


def existing_msgev_artifact_coordinates() -> tuple[set[int], list[str]]:
    """Read only numeric coordinates from existing private MS GEV artifacts."""

    blocked: set[int] = set(SEMANTIC_BATCH_COORDINATES)
    files: list[str] = []
    skip = {OUTPUT.resolve(), HOLD_OUTPUT.resolve()}
    for root in (SEMANTIC_ROOT, PROPOSAL_ROOT):
        if not root.exists():
            continue
        for path in sorted(root.glob("*msgev*.jsonl")):
            if path.resolve() in skip:
                continue
            files.append(path.relative_to(REPO).as_posix())
            # Existing Korean text is intentionally not interpreted here.
            for match in ID_RE.finditer(path.read_text(encoding="utf-8")):
                blocked.add(int(match.group(1)))
    return blocked, files


def load_msgev() -> tuple[tuple[str, ...], tuple[str, ...], dict[str, str]]:
    jp_hash = file_hash(PC_PK_JP_ORIGINAL)
    ko_path = STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin"
    ko_hash = file_hash(ko_path)
    if jp_hash != EXPECTED_HASHES["msgev_jp"]:
        raise RuntimeError(f"unexpected pristine PC MS GEV JP hash: {jp_hash}")
    if ko_hash != EXPECTED_HASHES["msgev_ko"]:
        raise RuntimeError(f"unexpected live PC MS GEV Korean hash: {ko_hash}")
    jp = tuple(parse_common(PC_PK_JP_ORIGINAL).values())
    ko = tuple(parse_common(ko_path).values())
    if len(jp) != TABLE_COUNT or len(ko) != TABLE_COUNT:
        raise RuntimeError(f"unexpected MS GEV table count: {len(jp)}, {len(ko)}")
    return jp, ko, {"jp": jp_hash, "ko": ko_hash}


def static_anchors() -> tuple[dict[str, tuple[StaticAnchor, ...]], dict[str, str], int]:
    anchors: dict[str, list[StaticAnchor]] = defaultdict(list)
    hashes: dict[str, str] = {}
    considered = 0
    for spec in STATIC_SPECS:
        jp_hash = file_hash(spec.pristine_jp_path)
        ko_hash = file_hash(spec.live_ko_path)
        if jp_hash != EXPECTED_HASHES[spec.jp_hash_key]:
            raise RuntimeError(f"unexpected pristine PC {spec.resource} JP hash: {jp_hash}")
        if ko_hash != EXPECTED_HASHES[spec.ko_hash_key]:
            raise RuntimeError(f"unexpected live PC {spec.resource} Korean hash: {ko_hash}")
        hashes[f"{spec.resource}_jp"] = jp_hash
        hashes[f"{spec.resource}_ko"] = ko_hash
        parser = PARSERS[spec.parser_name]
        jp_table = parser(spec.pristine_jp_path)
        ko_table = parser(spec.live_ko_path)
        if set(jp_table) != set(ko_table):
            raise RuntimeError(f"PC {spec.resource} coordinate mismatch")
        for coordinate, source in jp_table.items():
            target = ko_table[coordinate]
            source_visible = visible(source)
            target_visible = visible(target)
            # Proper-name labels only: no tag, runtime, hard break, kana or
            # punctuation in the PC Japanese static key.  This rejects prose
            # and component-like strings before matching MS GEV.
            if source != source_visible or not HAN_ONLY_RE.fullmatch(source_visible):
                continue
            if (
                target != target_visible
                or "\n" in target_visible
                or "\r" in target_visible
                or RUNTIME_RE.search(target_visible)
                or not HANGUL_RE.search(target_visible)
                or SSEU not in target_visible
            ):
                continue
            considered += 1
            anchors[source_visible].append(
                StaticAnchor(
                    resource=spec.resource,
                    coordinate=coordinate,
                    japanese=source_visible,
                    korean=target_visible,
                )
            )
    return {key: tuple(value) for key, value in anchors.items()}, hashes, considered


def anchor_payload(anchors: list[StaticAnchor]) -> list[dict[str, str]]:
    return [
        {
            "resource": anchor.resource,
            "coordinate": anchor.coordinate,
            "canonical_korean": anchor.korean,
        }
        for anchor in sorted(anchors, key=lambda item: (item.resource, item.coordinate))
    ]


def build() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    jp, ko, msgev_hashes = load_msgev()
    anchors_by_source, static_hashes, static_anchor_count = static_anchors()
    blocked, artifact_files = existing_msgev_artifact_coordinates()

    candidates: list[dict[str, Any]] = []
    blocked_ids: list[int] = []
    not_exact_ids: list[int] = []
    layout_hold_ids: list[int] = []
    static_source_match_ids: list[int] = []
    for index, (source, current) in enumerate(zip(jp, ko)):
        source_visible = visible(source)
        anchors = anchors_by_source.get(source_visible)
        if not anchors:
            continue
        current_visible = visible(current)
        if TSU not in current_visible:
            continue
        static_source_match_ids.append(index)
        proposed = current.replace(TSU, SSEU)
        proposed_visible = visible(proposed)
        matching_anchors = [anchor for anchor in anchors if anchor.korean == proposed_visible]
        if not matching_anchors:
            not_exact_ids.append(index)
            continue
        if not only_tsu_to_sseu(current, proposed):
            raise RuntimeError(f"non-tsu-to-sseu delta at {index}")
        if format_signature(current) != format_signature(proposed):
            raise RuntimeError(f"format contract drift at {index}")
        current_layout = layout(current)
        proposed_layout = layout(proposed)
        if current_layout != proposed_layout:
            raise RuntimeError(f"layout drift at {index}")
        if proposed_layout["line_count"] > 3 or max(
            proposed_layout["logical_display_columns"], default=0
        ) > MAX_LOGICAL_COLUMNS:
            layout_hold_ids.append(index)
            continue
        if index in blocked:
            blocked_ids.append(index)
            continue
        candidates.append(
            {
                "schema_version": REVIEW_BATCH,
                "review_batch": REVIEW_BATCH,
                "record_type": "candidate",
                "confidence": "high",
                "resource": RESOURCE,
                "id": index,
                "issue_type": "proper_name_reading_tsu_to_sseu_inconsistency",
                "source_japanese": source,
                "current_korean": current,
                "proposed_korean": proposed,
                "reference_static_label": source_visible,
                "reference_static_anchors": anchor_payload(matching_anchors),
                "reference_rule": "complete_pristine_pc_jp_label_and_post_tsu_to_sseu_pc_static_ko_are_exact",
                "input_file_sha256": {**msgev_hashes, **static_hashes},
                "current_text_sha256": text_hash(current),
                "proposed_text_sha256": text_hash(proposed),
                "format_contract": format_signature(current),
                "current_layout": current_layout,
                "proposed_layout": proposed_layout,
                "logical_width_budget": MAX_LOGICAL_COLUMNS,
                "active_artifact_coordinate_overlap": False,
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
                "game_files_written": False,
            }
        )

    ids = [row["id"] for row in candidates]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate MS GEV candidate coordinates")
    if set(ids) & blocked:
        raise RuntimeError("candidate coordinate overlaps blocked MS GEV artifact")
    holds = [
        {
            "schema_version": REVIEW_BATCH,
            "review_batch": REVIEW_BATCH,
            "record_type": "hold_group",
            "reason": "shared_static_jp_label_but_non_tsu_to_sseu_difference_remains",
            "ids": not_exact_ids,
            "count": len(not_exact_ids),
            "switch_korean_translation_used": False,
            "historic_korean_backup_used": False,
            "game_files_written": False,
        },
        {
            "schema_version": REVIEW_BATCH,
            "review_batch": REVIEW_BATCH,
            "record_type": "hold_group",
            "reason": "candidate_coordinate_already_in_existing_msgev_review_or_adjacent_semantic_batch",
            "ids": blocked_ids,
            "count": len(blocked_ids),
            "switch_korean_translation_used": False,
            "historic_korean_backup_used": False,
            "game_files_written": False,
        },
        {
            "schema_version": REVIEW_BATCH,
            "review_batch": REVIEW_BATCH,
            "record_type": "hold_group",
            "reason": "three_line_or_logical_width_budget_not_met",
            "ids": layout_hold_ids,
            "count": len(layout_hold_ids),
            "switch_korean_translation_used": False,
            "historic_korean_backup_used": False,
            "game_files_written": False,
        },
    ]
    summary = {
        "review_batch": REVIEW_BATCH,
        "resource": RESOURCE,
        "full_pc_msgev_entries_scanned": TABLE_COUNT,
        "static_name_anchor_count": static_anchor_count,
        "static_name_source_count": len(anchors_by_source),
        "msgev_entries_with_complete_static_jp_label_and_tsu": len(static_source_match_ids),
        "strict_tsu_to_sseu_exact_static_match_count_before_exclusion": len(candidates)
        + len(blocked_ids),
        "candidate_count": len(candidates),
        "candidate_ids": ids,
        "held_non_exact_count": len(not_exact_ids),
        "held_existing_or_semantic_overlap_count": len(blocked_ids),
        "held_layout_count": len(layout_hold_ids),
        "active_artifact_coordinate_union_count_including_adjacent_semantic_batch": len(blocked),
        "active_artifacts_scanned_for_id_exclusion": artifact_files,
        "input_file_sha256": {**msgev_hashes, **static_hashes},
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    return candidates, holds, summary


def canonical_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def atomic_write(path: Path, payload: str) -> None:
    """Write a reproducible private review artifact, never a game resource."""

    allowed_root = TMP_ROOT.resolve()
    resolved = path.resolve(strict=False)
    if resolved != allowed_root and allowed_root not in resolved.parents:
        raise RuntimeError(f"review output must remain below {TMP_ROOT}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("candidates", "holds", "summary"), default="summary")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    candidates, holds, summary = build()
    if args.write:
        atomic_write(OUTPUT, canonical_jsonl(candidates))
        atomic_write(HOLD_OUTPUT, canonical_jsonl(holds))
        summary["candidate_output"] = OUTPUT.relative_to(REPO).as_posix()
        summary["candidate_output_sha256"] = file_hash(OUTPUT)
        summary["hold_output"] = HOLD_OUTPUT.relative_to(REPO).as_posix()
        summary["hold_output_sha256"] = file_hash(HOLD_OUTPUT)
    if args.kind == "candidates":
        print("@@JSONL@@")
        print(canonical_jsonl(candidates), end="")
    elif args.kind == "holds":
        print("@@JSONL@@")
        print(canonical_jsonl(holds), end="")
    else:
        print("@@SUMMARY@@")
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
