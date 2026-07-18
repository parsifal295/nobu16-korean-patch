#!/usr/bin/env python3
"""Build a source-gated Steam-PC Korean repair candidate for NPC name components.

The game has two independent presentation paths for ordinary NPC titles:
dynamic name fragments in Base ``strdata`` / PK ``msgdata`` and complete labels
in Base ``ev_strdata`` / PK ``msgev``.  This builder changes both paths from the
same checked Korean targets, validates every listed composition in both
fragment tables, and never reads a Switch resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "strdata"
sys.path[:0] = [str(TOOLS), str(STRDATA_TOOLS)]

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
from strdata_format import StrdataArchive, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


SCHEMA = "nobu16.kr.npc-name-component-quality.v1"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BUILD_ROOT = REPO / "tmp" / WORKSTREAM.name
DEFAULT_OUTPUT_ROOT = BUILD_ROOT / "candidate-v2"
DEFAULT_MANIFEST = BUILD_ROOT / "candidate_manifest.v2.json"

PROFILE_PATHS = (
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG/JP/ev_strdata.bin",
    "MSG_PK/JP/msgev.bin",
)

# Steam PC state at the start of this audit.  The builder refuses a drifted
# baseline instead of overwriting a newer text wave.
BASELINE_SHA256 = {
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG/JP/ev_strdata.bin": "3A7BE17B7DA97B89BD82DFFF44EBC28DA2D3AA91D2E970A0F6C26DE22C657A22",
    "MSG_PK/JP/msgev.bin": "73DEC80A85B5441AFFFA725DAB72CF02D334D29B297AD08050BC496D532CB8F3",
}

# Exact candidate output from the pinned Steam PC baseline.  Keeping this table
# non-empty makes later rebuilds target-gated as well as source-gated.
TARGET_SHA256 = {
    "MSG/JP/strdata.bin": "5F308F416378976C1AB0B50D4A91C9DA38C637A0A842BAB04FB48256B2103E28",
    "MSG_PK/JP/msgdata.bin": "69090EC9EEE1DF9EAFB64BB35CEFD285A5089FDE78E9A4A855EAA0AE5991C168",
    "MSG/JP/ev_strdata.bin": "CC77EE4B0587B371A901069FB3F39C2187886C3A3335D9748D275FA2881EB426",
    "MSG_PK/JP/msgev.bin": "3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5",
}


@dataclass(frozen=True)
class ComponentFix:
    entry_id: int
    base_before: str
    pk_before: str
    after: str


@dataclass(frozen=True)
class StaticFix:
    entry_id: int
    before: str
    after: str


@dataclass(frozen=True)
class Composition:
    key: str
    entry_ids: tuple[int, ...]
    expected: str


class NpcNameQualityError(ValueError):
    """Raised when the pinned source, table structure, or candidate differs."""


# These are the dynamic routes with either a user-reported runtime failure or a
# PC EN component pair that forms a normal word/phrase.  All values are
# Korean-only.  Component IDs are distinct source slots even where JP shares a
# character, because each one is tied to a different ordinary-NPC route.
COMPONENT_FIXES = (
    ComponentFix(263, "나가", "나가", "장"),
    ComponentFix(329, "마쓰다이라", "마쓰다이라 ", "마쓰다이라 "),
    ComponentFix(444, "가문", "가문", "가"),
    ComponentFix(514, "공", "공", "구"),
    ComponentFix(602, "소", "소", "시"),
    ComponentFix(776, "덴", "덴", "전"),
    ComponentFix(938, "범용", "범용", "범용 "),
    ComponentFix(2157, "사람", "사람", "인"),
    ComponentFix(2158, "백성", "백성", "민"),
    ComponentFix(2161, "가문", "가문", "게"),
    ComponentFix(2163, "성씨", "성씨", "동"),
    ComponentFix(2170, "사람", "사람", "인"),
    ComponentFix(2172, "도모", "도모", ""),
    ComponentFix(2183, "노", "노", "로"),
    ComponentFix(2938, "수수께끼의", "수수께끼의", "수수께끼의 "),
    ComponentFix(2943, "사람", "사람", "인"),
    ComponentFix(2944, "미", "미", "감"),
    ComponentFix(2945, "장력", "장력", "시"),
    ComponentFix(3318, "모로", "모로", "사"),
)

# These have a JP complete-label anchor but their PC EN fragments are ordered
# or segmented differently from the complete label.  They stay audited but are
# intentionally not written until a real-game route proves the component use.
HELD_DYNAMIC_COMPONENT_IDS = frozenset(
    {
        87, 89, 93, 147, 174, 182, 185, 194, 195, 209, 327, 349, 445, 710,
        757, 774, 2164, 2168, 2175, 2177, 2178, 2179, 2180, 2181, 2182,
        2184, 2185, 2186, 2187, 2188,
    }
)
AUDITED_COMPOSITION_ROUTE_COUNT = 39

# Complete NPC labels do not automatically inherit the fragment table.  These
# are coordinate-only corrections and are applied identically to Base and PK.
STATIC_FIXES = (
    StaticFix(2780, "쓰다 소큐", "쓰다 소규"),
    StaticFix(2783, "도시타카보", "슌소보"),
    StaticFix(2784, "후로이스", "프로이스"),
    StaticFix(2804, "자비에르", "하비에르"),
    StaticFix(2810, "오이와 스케무", "다이간 유무"),
    StaticFix(2812, "마을 처녀", "성읍 처녀"),
    StaticFix(2814, "상인사", "상인 대표"),
    StaticFix(2818, "조자", "부족장"),
    StaticFix(3009, "오이와 스케무", "다이간 유무"),
    StaticFix(3074, "가인", "가신"),
)

# The complete-label anchors are the semantic oracle for the applied dynamic
# routes.  The broader 39-route audit is deliberately counted separately above.
COMPOSITIONS = (
    Composition("old_man", (925, 2157), "노인"),
    Composition("farmer", (829, 2158), "농민"),
    Composition("courtier", (514, 2161), "구게"),
    Composition("page", (602, 2163), "시동"),
    Composition("retainer", (444, 2165), "가신"),
    Composition("common_ninja", (938, 2166), "범용 닌자"),
    Composition("relay", (776, 2169), "전령"),
    Composition("merchant", (191, 2170), "상인"),
    Composition("child", (146, 2172), "아이"),
    Composition("matsudaira_takechiyo", (329, 2176), "마쓰다이라 다케치요"),
    Composition("elder", (263, 2183), "장로"),
    Composition("mysterious_dancer", (2938, 2939), "수수께끼의 무희"),
    Composition("foreigner", (2942, 2943), "남만인"),
    Composition("relay_second_anchor", (776, 2169), "전령"),
    Composition("guard", (2944, 2945), "감시"),
    Composition("missionary", (3317, 3318), "선교사"),
)


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def require_under(root: Path, candidate: Path, label: str) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise NpcNameQualityError(f"{label} escapes its allowed root: {candidate}") from exc
    return candidate


def assert_unique_ids() -> None:
    component_ids = [item.entry_id for item in COMPONENT_FIXES]
    static_ids = [item.entry_id for item in STATIC_FIXES]
    if len(component_ids) != len(set(component_ids)):
        raise NpcNameQualityError("duplicate component fix ID")
    if len(static_ids) != len(set(static_ids)):
        raise NpcNameQualityError("duplicate static fix ID")
    if len({item.key for item in COMPOSITIONS}) != len(COMPOSITIONS):
        raise NpcNameQualityError("duplicate composition key")


def assert_baseline(steam_root: Path) -> None:
    steam_root = steam_root.resolve(strict=True)
    actual = {
        relative: sha256_path(require_under(steam_root, steam_root / relative, "Steam source"))
        for relative in PROFILE_PATHS
    }
    if actual != BASELINE_SHA256:
        mismatch = {
            path: {"expected": BASELINE_SHA256[path], "actual": actual[path]}
            for path in PROFILE_PATHS
            if actual[path] != BASELINE_SHA256[path]
        }
        raise NpcNameQualityError(f"Steam baseline drifted: {mismatch}")


def _checked_common_source(source: bytes, label: str) -> tuple[object, MessageTable]:
    wrapper, raw = decompress_wrapper(source)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise NpcNameQualityError(f"{label} common table does not byte-round-trip")
    return wrapper, table


def _patched_common(
    source: bytes,
    fixes: Iterable[StaticFix],
    label: str,
) -> bytes:
    wrapper, table = _checked_common_source(source, label)
    texts = list(table.texts)
    for fix in fixes:
        if fix.entry_id >= len(texts) or texts[fix.entry_id] != fix.before:
            actual = None if fix.entry_id >= len(texts) else texts[fix.entry_id]
            raise NpcNameQualityError(
                f"unexpected static preimage {label}#{fix.entry_id}: {actual!r}"
            )
        texts[fix.entry_id] = fix.after
    rebuilt_raw = rebuild_message_table(table, texts)
    checked = parse_message_table(rebuilt_raw)
    if checked.texts != tuple(texts):
        raise NpcNameQualityError(f"{label} rebuilt table failed parse verification")
    return recompress_wrapper(rebuilt_raw, wrapper)


def _patch_pk_msgdata(source: bytes) -> bytes:
    wrapper, table = _checked_common_source(source, "MSG_PK/JP/msgdata.bin")
    texts = list(table.texts)
    for fix in COMPONENT_FIXES:
        if texts[fix.entry_id] != fix.pk_before:
            raise NpcNameQualityError(
                f"unexpected PK component preimage #{fix.entry_id}: {texts[fix.entry_id]!r}"
            )
        texts[fix.entry_id] = fix.after
    rebuilt_raw = rebuild_message_table(table, texts)
    checked = parse_message_table(rebuilt_raw)
    if checked.texts != tuple(texts):
        raise NpcNameQualityError("PK msgdata rebuilt table failed parse verification")
    return recompress_wrapper(rebuilt_raw, wrapper)


def _patch_base_strdata(source: bytes) -> bytes:
    wrapper, raw = decompress_wrapper(source)
    archive = parse_raw_strdata(raw)
    if rebuild_raw_strdata(archive) != raw:
        raise NpcNameQualityError("Base strdata does not byte-round-trip")
    texts = list(archive.blocks[0].texts)
    for fix in COMPONENT_FIXES:
        if texts[fix.entry_id] != fix.base_before:
            raise NpcNameQualityError(
                f"unexpected Base component preimage #0:{fix.entry_id}: {texts[fix.entry_id]!r}"
            )
        texts[fix.entry_id] = fix.after
    rebuilt_raw = rebuild_raw_strdata(archive, {0: texts})
    checked = parse_raw_strdata(rebuilt_raw)
    if checked.blocks[0].texts != tuple(texts):
        raise NpcNameQualityError("Base strdata rebuilt table failed parse verification")
    return recompress_wrapper(rebuilt_raw, wrapper)


def patch_target(relative: str, source: bytes) -> bytes:
    if relative == "MSG/JP/strdata.bin":
        return _patch_base_strdata(source)
    if relative == "MSG_PK/JP/msgdata.bin":
        return _patch_pk_msgdata(source)
    if relative in {"MSG/JP/ev_strdata.bin", "MSG_PK/JP/msgev.bin"}:
        return _patched_common(source, STATIC_FIXES, relative)
    raise NpcNameQualityError(f"unsupported target path: {relative}")


def _assert_untouched_texts(
    before: Sequence[str],
    after: Sequence[str],
    changed_ids: set[int],
    label: str,
) -> None:
    if len(before) != len(after):
        raise NpcNameQualityError(f"{label} slot count changed")
    for entry_id, (old, new) in enumerate(zip(before, after, strict=True)):
        if entry_id not in changed_ids and old != new:
            raise NpcNameQualityError(f"{label} changed unlisted text slot #{entry_id}")


def _assert_components(
    base: Sequence[str],
    pk: Sequence[str],
) -> None:
    for fix in COMPONENT_FIXES:
        if base[fix.entry_id] != fix.after:
            raise NpcNameQualityError(f"Base component differs at #0:{fix.entry_id}")
        if pk[fix.entry_id] != fix.after:
            raise NpcNameQualityError(f"PK component differs at #{fix.entry_id}")
    for composition in COMPOSITIONS:
        base_text = "".join(base[entry_id] for entry_id in composition.entry_ids)
        pk_text = "".join(pk[entry_id] for entry_id in composition.entry_ids)
        if base_text != composition.expected or pk_text != composition.expected:
            raise NpcNameQualityError(
                f"composition {composition.key} differs: Base={base_text!r}, PK={pk_text!r}, "
                f"expected={composition.expected!r}"
            )


def _assert_static(table: Sequence[str], label: str) -> None:
    for fix in STATIC_FIXES:
        if table[fix.entry_id] != fix.after:
            raise NpcNameQualityError(f"{label} static label differs at #{fix.entry_id}")


def _candidate_files(output_root: Path) -> set[str]:
    return {
        path.relative_to(output_root).as_posix()
        for path in output_root.rglob("*")
        if path.is_file()
    }


def _verify_parsed_changes(steam_root: Path, output_root: Path) -> None:
    source_base = (steam_root / "MSG/JP/strdata.bin").read_bytes()
    candidate_base = (output_root / "MSG/JP/strdata.bin").read_bytes()
    _source_wrapper, source_raw = decompress_wrapper(source_base)
    _candidate_wrapper, candidate_raw = decompress_wrapper(candidate_base)
    source_archive = parse_raw_strdata(source_raw)
    candidate_archive = parse_raw_strdata(candidate_raw)
    if len(source_archive.blocks) != len(candidate_archive.blocks):
        raise NpcNameQualityError("Base strdata block count changed")
    for source_block, candidate_block in zip(source_archive.blocks[1:], candidate_archive.blocks[1:], strict=True):
        if source_block.table.blob != candidate_block.table.blob:
            raise NpcNameQualityError(f"Base strdata changed retain-only block {source_block.block_id}")
    component_ids = {fix.entry_id for fix in COMPONENT_FIXES}
    _assert_untouched_texts(
        source_archive.blocks[0].texts,
        candidate_archive.blocks[0].texts,
        component_ids,
        "Base strdata block 0",
    )

    source_pk = (steam_root / "MSG_PK/JP/msgdata.bin").read_bytes()
    candidate_pk = (output_root / "MSG_PK/JP/msgdata.bin").read_bytes()
    _source_wrapper, source_raw = decompress_wrapper(source_pk)
    _candidate_wrapper, candidate_raw = decompress_wrapper(candidate_pk)
    source_table = parse_message_table(source_raw)
    candidate_table = parse_message_table(candidate_raw)
    _assert_untouched_texts(source_table.texts, candidate_table.texts, component_ids, "PK msgdata")
    _assert_components(candidate_archive.blocks[0].texts, candidate_table.texts)

    static_ids = {fix.entry_id for fix in STATIC_FIXES}
    for relative in ("MSG/JP/ev_strdata.bin", "MSG_PK/JP/msgev.bin"):
        source = (steam_root / relative).read_bytes()
        candidate = (output_root / relative).read_bytes()
        _source_wrapper, source_raw = decompress_wrapper(source)
        _candidate_wrapper, candidate_raw = decompress_wrapper(candidate)
        source_table = parse_message_table(source_raw)
        candidate_table = parse_message_table(candidate_raw)
        _assert_untouched_texts(source_table.texts, candidate_table.texts, static_ids, relative)
        _assert_static(candidate_table.texts, relative)


def verify_candidate(steam_root: Path, output_root: Path) -> dict[str, object]:
    assert_unique_ids()
    steam_root = steam_root.resolve(strict=True)
    output_root = output_root.resolve(strict=True)
    assert_baseline(steam_root)
    if _candidate_files(output_root) != set(PROFILE_PATHS):
        raise NpcNameQualityError("candidate tree does not contain the exact four-file profile")
    entries: list[dict[str, object]] = []
    for relative in PROFILE_PATHS:
        source = require_under(steam_root, steam_root / relative, "Steam source").read_bytes()
        candidate = require_under(output_root, output_root / relative, "candidate").read_bytes()
        if candidate == source:
            raise NpcNameQualityError(f"candidate did not change expected resource: {relative}")
        target_hash = sha256_bytes(candidate)
        if TARGET_SHA256 and target_hash != TARGET_SHA256[relative]:
            raise NpcNameQualityError(
                f"candidate target hash differs at {relative}: {target_hash}"
            )
        entries.append(
            {
                "path": relative,
                "source_sha256": sha256_bytes(source),
                "candidate_sha256": target_hash,
                "source_size": len(source),
                "candidate_size": len(candidate),
            }
        )
    _verify_parsed_changes(steam_root, output_root)
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "changed_paths": list(PROFILE_PATHS),
        "component_fix_count": len(COMPONENT_FIXES),
        "static_fix_count": len(STATIC_FIXES),
        "composition_route_count": len(COMPOSITIONS),
        "audited_composition_route_count": AUDITED_COMPOSITION_ROUTE_COUNT,
        "held_dynamic_component_id_count": len(HELD_DYNAMIC_COMPONENT_IDS),
        "entries": entries,
    }


def build(steam_root: Path, output_root: Path, manifest_path: Path) -> dict[str, object]:
    assert_unique_ids()
    steam_root = steam_root.resolve(strict=True)
    assert_baseline(steam_root)
    output_root = require_under(BUILD_ROOT, output_root, "candidate output")
    manifest_path = require_under(BUILD_ROOT, manifest_path, "candidate manifest")
    if output_root.exists():
        raise NpcNameQualityError(f"candidate output already exists: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="candidate-", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            source_path = require_under(steam_root, steam_root / relative, "Steam source")
            target_path = temporary / relative
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(patch_target(relative, source_path.read_bytes()))
        os.replace(temporary, output_root)
        report = verify_candidate(steam_root, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(canonical_json(report))
        return report
    except Exception:
        if temporary.exists():
            require_under(output_root.parent, temporary, "temporary candidate")
            shutil.rmtree(temporary)
        raise


def verify_installed(steam_root: Path) -> dict[str, object]:
    """Verify that all four installed resources equal this candidate's target."""
    if not TARGET_SHA256:
        raise NpcNameQualityError("target SHA-256 pins have not been recorded")
    steam_root = steam_root.resolve(strict=True)
    actual = {
        relative: sha256_path(require_under(steam_root, steam_root / relative, "Steam target"))
        for relative in PROFILE_PATHS
    }
    if actual != TARGET_SHA256:
        mismatch = {
            path: {"expected": TARGET_SHA256[path], "actual": actual[path]}
            for path in PROFILE_PATHS
            if actual[path] != TARGET_SHA256[path]
        }
        raise NpcNameQualityError(f"Steam target differs: {mismatch}")
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "installed_profile": "npc-name-component-quality-v1",
        "changed_paths": list(PROFILE_PATHS),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true")
    mode.add_argument("--verify-installed", action="store_true")
    args = parser.parse_args(argv)
    if args.verify_installed:
        report = verify_installed(args.steam_root)
    elif args.verify_only:
        report = verify_candidate(args.steam_root, args.output_root)
    else:
        report = build(args.steam_root, args.output_root, args.manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
