#!/usr/bin/env python3
"""Build the private W71 Anegawa semantic-linebreak correction.

This pass starts from the pinned W70 Korean candidate. It does not shorten,
delete, rename, or otherwise rewrite a Korean sentence. Every source line
break is discarded, then the same Korean text is placed at reviewed Korean
phrase boundaries. The live Steam screenshot establishes that this PK event
widget wraps with raw G1N advances (full-width 48 / half-width 24) at 960px;
the static-007 30px font setting is draw typography, not its wrap metric.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
W70_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_anegawa_static007_wave70_v1"
    / "build_pc_event_anegawa_static007_wave70_v1.py"
)

PK_BODY_START = 3_000
PK_BODY_END = 11_009
EXPECTED_PK_BODY_NONEMPTY_COUNT = 8_006
SCENE_RANGES = (range(5_777, 5_803), range(5_885, 5_915))
MAX_LINES = 4
RAW_WRAP_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
DRAW_LINE_SPACING = 8

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# W70 incorrectly looked up these tokens in the event-message table. These
# are conservative, scene-valid display reservations. bm1871 can render the
# shorter historical name, but the full name is used for a safe bound.
RUNTIME_RESERVATIONS = {
    "[b1871]": "도쿠가와 이에야스",
    "[bm1871]": "도쿠가와 이에야스",
    "[bs1871]": "도쿠가와",
}

# Counts refer to semantic units separated by visible whitespace outside an
# ESC colour span. They were selected manually after discarding all prior JP
# source line breaks. Each tuple covers one entire Korean message.
REFLOW_UNIT_COUNTS: Mapping[int, tuple[int, ...]] = {
    5777: (4, 4, 4),
    5778: (2,),
    5779: (3, 2, 3, 5),
    5780: (6, 5, 2, 4),
    5781: (2, 4, 4),
    5782: (4,),
    5783: (1, 5, 3),
    5784: (4, 2, 2, 3),
    5785: (2, 5, 3, 3),
    5786: (2,),
    5787: (2, 3, 2),
    5788: (1, 3, 2),
    5789: (2, 2, 3),
    5790: (3, 2, 7, 4),
    5791: (2, 3, 3),
    5792: (4, 3, 3, 5),
    5793: (1,),
    5794: (1, 2, 5),
    5795: (3, 3, 3, 5),
    5796: (2,),
    5797: (1, 3, 2),
    5798: (3, 4),
    5799: (3, 4, 5),
    5800: (2,),
    5801: (1, 4),
    5802: (1, 5, 4),
    5885: (2, 2, 3, 4),
    5886: (3, 3, 4, 5),
    5887: (3, 4, 4, 3),
    5888: (4, 6),
    5889: (4,),
    5890: (3, 4, 2),
    5891: (1, 2, 5, 5),
    5892: (1,),
    5893: (1,),
    5894: (3, 5, 3),
    5895: (2,),
    5896: (3,),
    5897: (5, 2, 3, 2),
    5898: (2, 3, 2),
    5899: (2, 5),
    5900: (1,),
    5901: (1, 1),
    5902: (2, 4, 4),
    5903: (1,),
    5904: (5, 3),
    5905: (2, 3),
    5906: (4, 4, 5, 4),
    5907: (3, 2),
    5908: (3, 3),
    5909: (5,),
    5910: (3, 4),
    5911: (3, 5, 4),
    5912: (4, 3, 3, 6),
    5913: (5, 3, 2, 5),
    5914: (2, 4, 3),
}

EXPECTED_EVENT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "0CA883CCAA94672F261640CA416FA5C2C15F2CFE112ED3D2523C156180DBEB15",
    "raw_size": 991_376,
    "sha256": "229A6EB7888BCC9838DC3B96F532F61F431FB3DEF5ED661D3253FF49F5D2991D",
    "size": 995_289,
}
EXPECTED_EVENT_RECORD_COUNT: int | None = 270
EXPECTED_TOTAL_RECORDS: int | None = 729


class Wave71Error(RuntimeError):
    """Raised when the W71 source, layout, or output contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave71Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave71Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w70 = load_module("pc_event_wave70_for_wave71", W70_BUILDER)
w66 = w70.w66
BASE = w70.BASE
PK = w70.PK
MSGDATA = w70.MSGDATA
MSGEV = w70.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    effective: Mapping[int, str]
    rows: tuple[Mapping[str, Any], ...]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w66.profile_dict(value)


def scene_ids() -> tuple[int, ...]:
    values = tuple(identifier for segment in SCENE_RANGES for identifier in segment)
    require(values == tuple(sorted(values)), "Anegawa scene ranges are not ascending")
    require(len(values) == len(set(values)) == 56, "Anegawa scene coverage drift")
    require(tuple(REFLOW_UNIT_COUNTS) == values, "manual semantic-line map scope drift")
    return values


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave71Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def semantic_units(value: str) -> tuple[str, ...]:
    """Split on visible whitespace without ever splitting an ESC colour span."""
    units: list[str] = []
    current: list[str] = []
    cursor = 0
    in_colour_span = False
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at {cursor}")
            if token == "\x1bCZ":
                require(in_colour_span, f"unpaired ESC close at {cursor}")
                in_colour_span = False
            else:
                require(not in_colour_span, f"nested ESC colour span at {cursor}")
                in_colour_span = True
            current.append(token)
            cursor += 3
            continue
        if character.isspace():
            if in_colour_span:
                current.append(" ")
            elif current:
                units.append("".join(current))
                current = []
            cursor += 1
            continue
        current.append(character)
        cursor += 1
    require(not in_colour_span, "unterminated ESC colour span")
    if current:
        units.append("".join(current))
    require(bool(units), "empty event text cannot be reflowed")
    return tuple(units)


def normalized_text(value: str) -> str:
    return " ".join(semantic_units(value))


def reflow_korean(value: str, line_counts: tuple[int, ...]) -> str:
    units = semantic_units(value)
    require(sum(line_counts) == len(units), f"manual line units do not cover text: {value!r}")
    require(1 <= len(line_counts) <= MAX_LINES, "manual line count exceeds live dialogue limit")
    lines: list[str] = []
    cursor = 0
    for count in line_counts:
        require(count > 0, "manual line group must not be empty")
        lines.append(" ".join(units[cursor : cursor + count]))
        cursor += count
    require(cursor == len(units), "manual line grouping left units behind")
    result = "\n".join(lines)
    require(normalized_text(result) == normalized_text(value), "reflow changed Korean text content")
    return result


def assert_no_break_inside_tag(value: str) -> None:
    in_colour_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at {cursor}")
            if token == "\x1bCZ":
                require(in_colour_span, f"unpaired ESC close at {cursor}")
                in_colour_span = False
            else:
                require(not in_colour_span, f"nested ESC colour span at {cursor}")
                in_colour_span = True
            cursor += 3
            continue
        require(not (in_colour_span and value[cursor] in "\r\n"), "line break inside ESC colour span")
        cursor += 1
    require(not in_colour_span, "unterminated ESC colour span")


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def rendered_display_line(value: str) -> str:
    rendered: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token in layout: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        if runtime is not None:
            token = runtime.group(0)
            reservation = RUNTIME_RESERVATIONS.get(token)
            require(reservation is not None, f"no live runtime-name reservation: {token}")
            rendered.append(reservation)
            cursor = runtime.end()
            continue
        require(unicodedata.category(character) != "Cc", f"unexpected visible control: U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    metrics: list[Mapping[str, Any]] = []
    for line in LINEBREAK_RE.sub("\n", value).split("\n"):
        display = rendered_display_line(line)
        full_width = sum(1 for character in display if is_full_width_visible(character))
        half_width = len(display) - full_width
        raw_width = full_width * RAW_FULL_WIDTH_PX + half_width * RAW_HALF_WIDTH_PX
        effective_width = (raw_width * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX
        metrics.append(
            {
                "display_string": display,
                "raw_g1n_width_px": raw_width,
                "effective_width_px": effective_width,
                "full_width_character_count": full_width,
                "half_width_character_count": half_width,
                "over_live_raw_960px": raw_width > RAW_WRAP_LIMIT_PX,
            }
        )
    return tuple(metrics)


def body_universe(before: Any, direct_jp: Any) -> tuple[int, ...]:
    require(len(before.texts) > PK_BODY_END and len(direct_jp.texts) > PK_BODY_END, "PK body domain is absent")
    values = tuple(
        identifier
        for identifier in range(PK_BODY_START, PK_BODY_END + 1)
        if before.texts[identifier] and direct_jp.texts[identifier]
    )
    require(len(values) == EXPECTED_PK_BODY_NONEMPTY_COUNT, "PK event-body coverage drift")
    return values


def expected_final_profile_dicts() -> dict[str, Mapping[str, Any]]:
    require(EXPECTED_EVENT_PROFILE is not None, "W71 event profile is not pinned")
    expected = {resource: dict(value) for resource, value in w70.expected_final_profile_dicts().items()}
    expected[MSGEV] = dict(EXPECTED_EVENT_PROFILE)
    return expected


def expected_final_record_counts() -> dict[str, int]:
    require(EXPECTED_EVENT_RECORD_COUNT is not None, "W71 event record count is not pinned")
    expected = dict(w70.expected_final_record_counts())
    expected[MSGEV] = EXPECTED_EVENT_RECORD_COUNT
    return expected


def overlay_events(w70_blob: bytes) -> tuple[bytes, dict[int, str], tuple[Mapping[str, Any], ...], Mapping[str, Any]]:
    header, _raw, before = w66.w60.parse_table("W70 event", w70_blob)
    direct_jp_blob, _direct_profile = w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w66.w60.parse_table("pristine PC JP event", direct_jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "W70/direct-PC-JP event table length drift")
    full_body = body_universe(before, direct_jp)
    reviewed = scene_ids()
    require(set(reviewed).issubset(full_body), "Anegawa review scope falls outside event body")

    effective: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in reviewed:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = reflow_korean(current, REFLOW_UNIT_COUNTS[entry_id])
        require(
            w70.control_signature(current) == w70.control_signature(source_jp),
            f"W70/direct-PC-JP token or tag drift: {entry_id}",
        )
        require(
            w70.control_signature(current) == w70.control_signature(target),
            f"W71 token or tag drift: {entry_id}",
        )
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W71 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W71 live raw width exceeds {RAW_WRAP_LIMIT_PX}px: {entry_id}",
        )
        if current != target:
            effective[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "w70_current_ko": current,
                "target_ko": target,
                "direct_pc_jp": source_jp,
                "w70_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "source_manual_lf_count": len(LINEBREAK_RE.findall(current)),
                "target_manual_lf_count": len(LINEBREAK_RE.findall(target)),
                "target_line_count": len(metrics),
                "target_lines": list(metrics),
                "control_signature": w70.control_signature(target),
                "korean_visible_text_preserved": normalized_text(current) == normalized_text(target),
                "japanese_source_line_breaks_used": False,
            }
        )

    texts = list(before.texts)
    for entry_id, value in effective.items():
        texts[entry_id] = value
    rebuilt_raw = w66.w60.core.rebuild_message_table(before, tuple(texts))
    output = w66.w60.core.recompress_wrapper(rebuilt_raw, header)
    _output_header, output_raw, after = w66.w60.parse_table("W71 event", output)
    require(output_raw == rebuilt_raw, "W71 event raw mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(effective),
        "W71 event scope drift",
    )
    coverage = {
        "semantic_completion": False,
        "full_pk_event_body_range": [PK_BODY_START, PK_BODY_END],
        "full_pk_event_body_nonempty_rows": len(full_body),
        "reviewed_scene_ranges": [[segment.start, segment.stop - 1] for segment in SCENE_RANGES],
        "reviewed_scene_rows": len(reviewed),
        "manual_linebreak_reviewed_rows": list(reviewed),
        "reflow_changed_rows": sorted(effective),
        "reflow_unchanged_rows": [identifier for identifier in reviewed if identifier not in effective],
        "remaining_full_pk_event_body_rows": len(full_body) - len(reviewed),
    }
    return output, effective, tuple(rows), coverage


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w70.prepare(require_output_profiles=True)
    w70.verify_private_candidate(base)
    event_output, effective, rows, coverage = overlay_events(base.outputs[MSGEV])
    outputs = {
        BASE: base.outputs[BASE],
        PK: base.outputs[PK],
        MSGDATA: base.outputs[MSGDATA],
        MSGEV: event_output,
    }
    profiles = {resource: w66.w61.profile(blob) for resource, blob in outputs.items()}
    w45 = w66.w62.load_w45_backups()
    base_records, _ = w66.w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _ = w66.w60.msggame_counts(w45[PK], outputs[PK])
    final_record_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w66.w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require(
            {resource: profile_dict(value) for resource, value in profiles.items()} == expected_final_profile_dicts(),
            "W71 output profile drift",
        )
        require(final_record_counts == expected_final_record_counts(), "W71 record count drift")
        require(EXPECTED_TOTAL_RECORDS is not None, "W71 total record count is not pinned")
        require(sum(final_record_counts.values()) == EXPECTED_TOTAL_RECORDS, "W71 total record count drift")
    audit = {
        "schema": "nobu16.kr.pc-event-anegawa-raw960-wave71-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W70 Steam-PC Korean candidate and pristine PC Japanese only",
            "switch_read": False,
            "japanese_source_linebreaks_used": False,
            "korean_text_shortened": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "layout_policy": {
            "baseline": "static patch 007 typography plus live Steam screenshot",
            "draw_font_px": DRAW_FONT_PX,
            "line_spacing_setting": DRAW_LINE_SPACING,
            "max_lines": MAX_LINES,
            "word_wrap_metric": "raw G1N advance, not draw-size-scaled advance",
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "live_raw_line_limit_px": RAW_WRAP_LIMIT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "dynamic_runtime_reservations": dict(RUNTIME_RESERVATIONS),
            "manual_break_rule": "Korean semantic units only; Japanese source line breaks are ignored",
            "korean_text_rule": "no shortening, deletion, rename, or content rewrite",
        },
        "coverage": coverage,
        "rows": list(rows),
        "final_record_counts": final_record_counts,
        "final_total_records": sum(final_record_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-anegawa-raw960-wave71-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_record_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(outputs, profiles, effective, rows, final_record_counts, audit, manifest)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W71 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W71 candidate staging already exists: {staging}")
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
    require(root.is_dir(), f"W71 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W71 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W71 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W71 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W71 manifest differs")
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
        WORKSTREAM / "build_pc_event_anegawa_raw960_wave71_v1.py",
        WORKSTREAM / "test_pc_event_anegawa_raw960_wave71_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W71 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W71 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(
        json.dumps(
            {
                "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
                "final_record_counts": bundle.final_record_counts,
                "final_total_records": sum(bundle.final_record_counts.values()),
                "line_metrics": {str(row["entry_id"]): row["target_lines"] for row in bundle.rows},
                "changed_rows": sorted(bundle.effective),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=False)
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
