#!/usr/bin/env python3
"""Build the private W64 static-event reflow overlay from W63.

W64 changes exactly 57 standard PC event narration/dialogue rows.  Each change
replaces one existing tag-external ASCII space with one LF; it never changes a
word, markup, colour tag, runtime token, font, Steam file, Git state, network
state, or public release.  The W63 composite is the only Korean base, while
the pristine direct-PC Japanese event table is used as the source witness.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate"
W63_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave63_v1"
    / "build_pc_private_union_composite_wave63_v1.py"
)
EVENT_LAYOUT_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_reflow_static_batch_d_candidate_v1"
    / "build_pc_event_reflow_static_batch_d_candidate_v1.py"
)


class Wave64Error(RuntimeError):
    """Raised when a pinned W63 source or W64 output contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave64Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave64Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w63 = load_module("pc_private_union_wave63_for_wave64", W63_BUILDER)
layout = load_module("pc_event_layout_for_wave64", EVENT_LAYOUT_BUILDER)
w62 = w63.w62
w61 = w62.w61
w60 = w62.w60

BASE = w63.BASE
PK = w63.PK
MSGDATA = w63.MSGDATA
MSGEV = w63.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class ReflowTarget:
    entry_id: int
    source_width_px: int
    target_line_widths_px: tuple[int, int]


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    event_effective: Mapping[int, str]
    event_classifications: Mapping[str, tuple[int, ...]]
    event_rows: tuple[Mapping[str, Any], ...]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Every pair below is a context-reviewed two-line layout, not an auto-selected
# balance.  The source width and pair uniquely pin the approved original-space
# location inside the W63 preimage.
REFLOW_TARGETS = (
    ReflowTarget(5571, 960, (360, 576)),
    ReflowTarget(5820, 1008, (312, 672)),
    ReflowTarget(5910, 1272, (504, 744)),
    ReflowTarget(5918, 960, (552, 384)),
    ReflowTarget(6114, 936, (432, 480)),
    ReflowTarget(6176, 1008, (432, 552)),
    ReflowTarget(6188, 960, (576, 360)),
    ReflowTarget(6462, 1080, (576, 480)),
    ReflowTarget(6523, 936, (456, 456)),
    ReflowTarget(6665, 1392, (672, 696)),
    ReflowTarget(6677, 1032, (216, 792)),
    ReflowTarget(6695, 936, (624, 288)),
    ReflowTarget(6824, 936, (216, 696)),
    ReflowTarget(6841, 1152, (696, 432)),
    ReflowTarget(6868, 936, (312, 600)),
    ReflowTarget(7021, 936, (696, 216)),
    ReflowTarget(7091, 1032, (264, 744)),
    ReflowTarget(7153, 984, (576, 384)),
    ReflowTarget(7492, 1008, (648, 336)),
    ReflowTarget(7697, 1032, (384, 624)),
    ReflowTarget(8072, 1128, (528, 576)),
    ReflowTarget(8121, 1104, (408, 672)),
    ReflowTarget(8151, 1176, (264, 888)),
    ReflowTarget(8182, 936, (288, 624)),
    ReflowTarget(8346, 1176, (408, 744)),
    ReflowTarget(8414, 1032, (792, 216)),
    ReflowTarget(8601, 1008, (408, 576)),
    ReflowTarget(9102, 984, (288, 672)),
    ReflowTarget(9144, 1248, (624, 600)),
    ReflowTarget(9164, 1272, (768, 480)),
    ReflowTarget(9590, 1032, (480, 528)),
    ReflowTarget(9636, 1248, (528, 696)),
    ReflowTarget(9789, 960, (408, 528)),
    ReflowTarget(9794, 1224, (624, 576)),
    ReflowTarget(9829, 1200, (384, 792)),
    ReflowTarget(9880, 1104, (312, 768)),
    ReflowTarget(9944, 1008, (264, 720)),
    ReflowTarget(9952, 984, (288, 672)),
    ReflowTarget(9954, 936, (576, 336)),
    ReflowTarget(10058, 1248, (576, 648)),
    ReflowTarget(10156, 1080, (288, 768)),
    ReflowTarget(10158, 984, (264, 696)),
    ReflowTarget(10165, 984, (552, 408)),
    ReflowTarget(10166, 1056, (456, 576)),
    ReflowTarget(10191, 984, (312, 648)),
    ReflowTarget(10346, 960, (528, 408)),
    ReflowTarget(10415, 1008, (312, 672)),
    ReflowTarget(10504, 1080, (576, 480)),
    ReflowTarget(10569, 960, (336, 600)),
    ReflowTarget(10591, 936, (480, 432)),
    ReflowTarget(10685, 1224, (432, 768)),
    ReflowTarget(10714, 1224, (600, 600)),
    ReflowTarget(10757, 960, (480, 456)),
    ReflowTarget(10801, 1128, (576, 528)),
    ReflowTarget(10898, 1104, (384, 696)),
    ReflowTarget(10915, 1368, (672, 672)),
    ReflowTarget(10956, 936, (504, 408)),
)

EXPECTED_TARGET_IDS = tuple(target.entry_id for target in REFLOW_TARGETS)
EXPECTED_EVENT_CLASSES = {"fresh": 57, "already": 0, "override": 0}
EXPECTED_FINAL_RECORD_COUNTS = {BASE: 109, PK: 282, MSGDATA: 4, MSGEV: 196}
EXPECTED_FINAL_TOTAL_RECORDS = 591
EXPECTED_FINAL_PROFILE_DICTS: dict[str, dict[str, Any]] | None = {
    BASE: {
        "raw_sha256": "7DA010184830AC83600F6DC301BBF134D6F8CAC9A5CE3818BDB4A3246E2F4A63",
        "raw_size": 1498548,
        "sha256": "02C8B0F0A175B85BDE223355620124DF5DC07B20FE804D26212E10C307D7C099",
        "size": 1504450,
    },
    PK: {
        "raw_sha256": "EBE0BB1F7440963300B225DC18B31281382A6A988B1A65875EC14A5F177D4056",
        "raw_size": 1799448,
        "sha256": "FC28D8394D40C5EF45D3BFCEF7161E05B6536B1874AAE90BA8ED14C99F28B351",
        "size": 1806530,
    },
    MSGDATA: {
        "raw_sha256": "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
        "raw_size": 495032,
        "sha256": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        "size": 496999,
    },
    MSGEV: {
        "raw_sha256": "27A3D7FFFF43E3E805B5F5AF90F708E35710C6284EC4DFBA9D465C998C9BE94F",
        "raw_size": 990844,
        "sha256": "48E06CF0CA5CA39D261E376D35B9A96B4A91BB7EE52A188D5F1400354A6FFEA4",
        "size": 994755,
    },
}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w62.profile_dict(value)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave64Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def event_target_map() -> dict[int, ReflowTarget]:
    mapped = {target.entry_id: target for target in REFLOW_TARGETS}
    require(len(mapped) == len(REFLOW_TARGETS), "duplicate W64 reflow ID")
    require(tuple(sorted(mapped)) == EXPECTED_TARGET_IDS, "W64 reflow target order or scope drift")
    return mapped


def manual_lf_count(value: str) -> int:
    require("\r" not in value, "CR is not allowed in a W64 static reflow")
    return value.count("\n")


def active_colour_before(value: str, offset: int) -> str | None:
    """Return the active ESC-C colour span immediately before ``offset``."""
    active: str | None = None
    cursor = 0
    while cursor < offset:
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(len(token) == 3 and token[:2] == "\x1bC", "malformed ESC-C token")
            code = token[2]
            if code in "ABC":
                require(active is None, "nested colour span")
                active = code
            elif code == "Z":
                require(active is not None, "orphan colour reset")
                active = None
            else:
                raise Wave64Error(f"unsupported ESC-C code: {code!r}")
            cursor += 3
            continue
        cursor += 1
    return active


def static_signature(value: str, entry_id: int, label: str) -> Mapping[str, Any]:
    signature = dict(layout.control_signature(value))
    require(signature["runtime_tokens"] == [], f"{entry_id} {label} contains a runtime token")
    require(signature["printf_tokens"] == [], f"{entry_id} {label} contains a printf token")
    require(signature["unknown_percent_count"] == 0, f"{entry_id} {label} contains an unknown percent")
    require(signature["other_controls"] == [], f"{entry_id} {label} contains another control")
    return signature


def choose_reflow(
    before: str,
    target: ReflowTarget,
    font: Any,
) -> tuple[str, int, tuple[int, int], Mapping[str, Any]]:
    entry_id = target.entry_id
    require(manual_lf_count(before) == 0, f"{entry_id} source already has manual LF")
    source_signature = static_signature(before, entry_id, "source")
    source_widths = layout.line_widths(before, font)
    require(source_widths == (target.source_width_px,), f"{entry_id} source width drift: {source_widths}")
    require(target.source_width_px > layout.PK_MAX_LINE_PX, f"{entry_id} source is not over width")
    candidates: list[tuple[str, int, tuple[int, int]]] = []
    for offset, character in enumerate(before):
        if character != " ":
            continue
        if active_colour_before(before, offset) is not None:
            continue
        after = before[:offset] + "\n" + before[offset + 1 :]
        widths = layout.line_widths(after, font)
        if widths == target.target_line_widths_px:
            candidates.append((after, offset, widths))
    require(len(candidates) == 1, f"{entry_id} must have one approved context reflow: {len(candidates)}")
    after, offset, widths = candidates[0]
    require(manual_lf_count(after) == 1, f"{entry_id} target must have exactly one LF")
    require(layout.layout_equivalent(before, after), f"{entry_id} wording or markup changed")
    require(static_signature(after, entry_id, "target") == source_signature, f"{entry_id} control signature drift")
    require(1 <= len(widths) <= layout.MAX_LINES, f"{entry_id} line count drift")
    require(max(widths) <= layout.PK_MAX_LINE_PX, f"{entry_id} line width drift")
    return after, offset, widths, source_signature


def overlay_event(
    w63_blob: bytes,
) -> tuple[bytes, dict[int, str], dict[str, tuple[int, ...]], tuple[Mapping[str, Any], ...]]:
    header, _raw, before = w60.parse_table("W63 event", w63_blob)
    direct_jp_blob, direct_jp_profile = w62.load_direct_jp_event()
    _jp_header, _jp_raw, jp = w60.parse_table("pristine PC JP event", direct_jp_blob)
    require(len(before.texts) == len(jp.texts), "W63/direct-PC-JP event table length drift")
    font = layout.load_font()
    effective: dict[int, str] = {}
    classes: dict[str, list[int]] = {"fresh": [], "already": [], "override": []}
    rows: list[Mapping[str, Any]] = []
    for entry_id, target in sorted(event_target_map().items()):
        current = before.texts[entry_id]
        direct_jp = jp.texts[entry_id]
        target_ko, split_offset, widths, signature = choose_reflow(current, target, font)
        require(
            static_signature(direct_jp, entry_id, "direct PC JP") == signature,
            f"{entry_id} direct PC JP tag/control evidence drift",
        )
        if current == target_ko:
            classes["already"].append(entry_id)
        elif current == before.texts[entry_id]:
            classes["fresh"].append(entry_id)
            effective[entry_id] = target_ko
        else:  # pragma: no cover - current comes directly from ``before``
            classes["override"].append(entry_id)
        rows.append({
            "entry_id": entry_id,
            "w63_current_ko": current,
            "target_ko": target_ko,
            "direct_pc_jp": direct_jp,
            "w63_current_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target_ko),
            "direct_pc_jp_utf16le_sha256": text_hash(direct_jp),
            "split_offset": split_offset,
            "source_manual_lf_count": manual_lf_count(current),
            "target_manual_lf_count": manual_lf_count(target_ko),
            "source_line_widths_px": [target.source_width_px],
            "target_line_widths_px": list(widths),
            "control_signature": signature,
            "rationale": "문맥 단위의 태그 밖 기존 공백 하나만 수동 줄바꿈으로 교체",
        })
    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_EVENT_CLASSES,
        f"W64 event classification drift: {frozen}",
    )
    texts = list(before.texts)
    for entry_id, value in effective.items():
        texts[entry_id] = value
    raw = w60.core.rebuild_message_table(before, tuple(texts))
    output = w60.core.recompress_wrapper(raw, header)
    _output_header, output_raw, after = w60.parse_table("W64 event", output)
    require(output_raw == raw, "W64 event raw mismatch")
    changed = {index for index, value in enumerate(before.texts) if value != after.texts[index]}
    require(changed == set(effective), f"W64 event scope drift: {sorted(changed)}")
    require(direct_jp_profile == w62.load_direct_jp_event()[1], "direct PC JP profile drift")
    return output, effective, frozen, tuple(rows)


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w63.prepare(require_output_profiles=True)
    w63.verify_private_candidate(base)
    event_output, event_effective, event_classifications, event_rows = overlay_event(base.outputs[MSGEV])
    outputs = {
        BASE: base.outputs[BASE],
        PK: base.outputs[PK],
        MSGDATA: base.outputs[MSGDATA],
        MSGEV: event_output,
    }
    profiles = {resource: w61.profile(blob) for resource, blob in outputs.items()}
    w45 = w62.load_w45_backups()
    _w45_header, _w45_raw, w45_events = w60.parse_table("W45 event", w45[MSGEV])
    _w63_header, _w63_raw, w63_events = w60.parse_table("W63 event", base.outputs[MSGEV])
    _w64_header, _w64_raw, w64_events = w60.parse_table("W64 event", event_output)
    w63_changed = {index for index, value in enumerate(w45_events.texts) if value != w63_events.texts[index]}
    w64_changed = {index for index, value in enumerate(w45_events.texts) if value != w64_events.texts[index]}
    require(w63_changed.isdisjoint(event_effective), "W64 reflow overlaps a W63 event correction")
    require(w64_changed == w63_changed | set(event_effective), "W64 W45 event retention drift")
    base_records, _base_literals = w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _pk_literals = w60.msggame_counts(w45[PK], outputs[PK])
    final_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require(EXPECTED_FINAL_PROFILE_DICTS is not None, "W64 output profile constants are not pinned")
        require(
            {resource: profile_dict(profile) for resource, profile in profiles.items()} == EXPECTED_FINAL_PROFILE_DICTS,
            "W64 output profile drift",
        )
        require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, "W64 final record count drift")
        require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS, "W64 final total drift")
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave64-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W63 Steam-PC Korean candidate and pristine PC Japanese only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "base_w63": {resource: profile_dict(w61.profile(base.outputs[resource])) for resource in ALL_RESOURCES},
        "direct_pc_jp_event": w62.load_direct_jp_event()[1],
        "font": dict(layout.FONT_PROFILE),
        "approved_reflow_ids": list(EXPECTED_TARGET_IDS),
        "event_classifications": {name: list(value) for name, value in event_classifications.items()},
        "event_rows": list(event_rows),
        "w45_to_w63_changed_event_ids": sorted(w63_changed),
        "w63_to_w64_changed_event_ids": sorted(event_effective),
        "w45_to_w64_changed_event_ids": sorted(w64_changed),
        "w63_w64_event_overlap_ids": sorted(w63_changed & set(event_effective)),
        "final_record_counts": final_counts,
        "final_total_records": sum(final_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave64-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(
        outputs,
        profiles,
        event_effective,
        event_classifications,
        event_rows,
        final_counts,
        audit,
        manifest,
    )


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W64 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W64 candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    bundle = bundle or prepare(require_output_profiles=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W64 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W64 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W64 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W64 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W64 manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave64_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave64_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W64 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W64 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
        "event_classifications": {name: list(value) for name, value in bundle.event_classifications.items()},
        "approved_reflow_ids": list(EXPECTED_TARGET_IDS),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=True)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_private_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
