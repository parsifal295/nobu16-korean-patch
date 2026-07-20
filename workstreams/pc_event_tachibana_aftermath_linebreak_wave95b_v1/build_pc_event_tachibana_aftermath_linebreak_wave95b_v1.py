#!/usr/bin/env python3
"""Build the private W95b one-row semantic-linebreak correction from W95."""

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

W95_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_tachibana_aftermath_quality_wave95_v1"
    / "build_pc_event_tachibana_aftermath_quality_wave95_v1.py"
)
MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_tachibana_aftermath_quality_wave95_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W95_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "3401B422130D3E183EC249DFE2E243B95DF32CE8C385BB0AAD64756E4C6C492A",
    "raw_size": 995_848,
    "sha256": "93BAACFE32433E3E09555258FACFD44EFE09F0D1860EF6B496FFD38B16F847D4",
    "size": 999_779,
}

ENTRY_ID = 8438
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

TARGET = "무사로서의 기량은 아버님을 넘는다…\n당신은 아버님 말씀 그대로의\n분이셨습니다."
TARGET_RAW_WIDTHS = (816, 648, 312)
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "FABEE3442CE0B74C55BD58B4E2338C701B8B8A47B6132FC94284E96C811D211C",
    "raw_size": 995_848,
    "sha256": "C2E266BC6589DC730D39DB74839AE7DD37E0ACCC953238E4B090E154486C44B3",
    "size": 999_779,
}


class Wave95bError(RuntimeError):
    """Raised when the strict predecessor, LF-only target, or candidate drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave95bError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave95bError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W95_BUILDER.is_file(), f"W95 helper builder missing: {W95_BUILDER}")
w95 = load_module("pc_event_wave95_base_for_wave95b", W95_BUILDER)
parse_table = w95.parse_table
core = w95.core
control_signature = w95.control_signature
is_full_width_visible = w95.is_full_width_visible


@dataclass(frozen=True)
class Bundle:
    event: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave95bError(f"candidate escapes tmp root: {resolved}") from exc
    return resolved


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(event),
        "size": len(event),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def runtime_tokens(value: str) -> tuple[str, ...]:
    return tuple(RUNTIME_RE.findall(value))


def assert_no_break_inside_tag(value: str) -> None:
    in_colour_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            if token == "\x1bCZ":
                require(in_colour_span, "unpaired ESC close")
                in_colour_span = False
            else:
                require(not in_colour_span, "nested ESC colour span")
                in_colour_span = True
            cursor += 3
            continue
        require(not (in_colour_span and value[cursor] in "\r\n"), "line break inside colour tag")
        cursor += 1
    require(not in_colour_span, "unterminated ESC colour span")


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        require(not runtime_tokens(line), "W95b target must not have runtime tokens")
        display: list[str] = []
        cursor = 0
        while cursor < len(line):
            if line[cursor] == "\x1b":
                token = line[cursor : cursor + 3]
                require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token in layout: {token!r}")
                cursor += 3
                continue
            require(unicodedata.category(line[cursor]) != "Cc", f"unexpected visible control U+{ord(line[cursor]):04X}")
            display.append(line[cursor])
            cursor += 1
        display_string = "".join(display)
        full = sum(1 for character in display_string if is_full_width_visible(character))
        half = len(display_string) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        rows.append(
            {
                "line_number": number,
                "display_string": display_string,
                "raw_g1n_width_px": raw,
                "effective_width_px": (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_live_raw_960px": raw > RAW_LINE_LIMIT_PX,
            }
        )
    return tuple(rows)


def validate_target() -> None:
    assert_no_break_inside_tag(TARGET)
    require(not runtime_tokens(TARGET), "W95b target must not have runtime tokens")
    metrics = line_metrics(TARGET)
    require(1 <= len(metrics) <= MAX_LINES, "W95b target line count drift")
    require(not any(metric["over_live_raw_960px"] for metric in metrics), "W95b target raw width exceeds 960px")
    require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS, "W95b target raw widths drift")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W95 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W95 linebreak predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W95_PROFILE, "W95 on-disk event profile drift")
    require(w95.EXPECTED_OUTPUT_PROFILE == EXPECTED_W95_PROFILE, "W95 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W95_PROFILE, "W95 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W95_PROFILE, "W95 manifest output profile drift")
    require(ENTRY_ID in set(audit.get("coverage", {}).get("changed_row_ids", [])), "W95 must contain the original 8438 correction")
    return event, table, raw, predecessor_profile


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_target()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    current = before.texts[ENTRY_ID]
    require(current, "W95b source row is empty")
    require(control_signature(TARGET) == control_signature(current), "W95b control/token drift")
    require(LINEBREAK_RE.sub(" ", TARGET) == LINEBREAK_RE.sub(" ", current), "W95b LF-only visible text drift")
    require(TARGET != current, "W95b target unexpectedly equals predecessor")
    metrics = line_metrics(TARGET)

    texts = list(before.texts)
    texts[ENTRY_ID] = TARGET
    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W95 linebreak predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W95b linebreak correction", event)
    require(after_raw == rebuilt_raw, "W95b raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == {ENTRY_ID}, "W95b actual diff scope drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W95b output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W95b output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-tachibana-aftermath-linebreak-wave95b-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W95 PC Korean candidate",
            "lf_only_reflow": True,
            "visible_text_added_deleted_or_replaced": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "network_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "strict_live_raw_line_limit_px": RAW_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_is_report_only": True,
            "runtime_reservations": {},
            "runtime_proven": False,
        },
        "coverage": {
            "reviewed_scene_ids": [ENTRY_ID],
            "reviewed_scene_row_count": 1,
            "changed_row_ids": [ENTRY_ID],
            "changed_row_count": 1,
            "unchanged_after_review_ids": [],
            "unchanged_after_review_count": 0,
        },
        "input_w95_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "row": {
            "entry_id": ENTRY_ID,
            "w95_current_ko": current,
            "target_ko": TARGET,
            "w95_current_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(TARGET),
            "lf_only_reflow": True,
            "normalized_visible_text_equal": True,
            "control_signature": control_signature(TARGET),
            "runtime_tokens": [],
            "runtime_reservations": [],
            "runtime_proven": False,
            "target_manual_line_count": len(metrics),
            "target_lines": list(metrics),
        },
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-tachibana-aftermath-linebreak-wave95b-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
        },
        "changed_row_ids": [ENTRY_ID],
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W95b candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W95b candidate staging exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True)
        event_path.write_bytes(bundle.event)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W95b candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W95b candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W95b candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W95b candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W95b candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": [ENTRY_ID],
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "runtime_proven": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_tachibana_aftermath_linebreak_wave95b_v1.py",
        WORKSTREAM / "test_pc_event_tachibana_aftermath_linebreak_wave95b_v1.py",
    ):
        require(path.is_file(), f"W95b authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W95b trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "W95b output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": [ENTRY_ID], "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
