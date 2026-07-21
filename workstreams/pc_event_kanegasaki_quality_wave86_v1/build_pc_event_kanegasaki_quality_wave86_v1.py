#!/usr/bin/env python3
"""Build the W86 Kanegasaki event-quality candidate from strict on-disk W85.

The W85 predecessor path and file profile are intentionally left unconfigured
until its candidate has been produced and independently profiled.  This module
can run ``authoring-check`` before then, but cannot read a predecessor, build a
candidate, or write any game resource.
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

# Reuse only stable message-table and control-signature helpers from W80.  The
# actual input is never W80: it is the W85 candidate configured below.
W80_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_naomasa_quality_wave80_v1"
    / "build_pc_event_naomasa_quality_wave80_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(3_230, 3_245))
CHANGED_IDS = (3_231, 3_234, 3_238)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# These values must be filled together only after root supplies the exact W85
# on-disk candidate directory and the packed/raw profile.  Keeping the values
# absent prevents accidental construction from an intermediate predecessor.
PREDECESSOR_WORKSTREAM = "pc_event_honnouji_successors_quality_wave85_v1"
PREDECESSOR_CANDIDATE_ROOT: Path | None = (
    REPO / "tmp" / "pc_event_honnouji_successors_quality_wave85_v1" / "candidate-final"
)
EXPECTED_W85_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "C5AD43F00B08B8F1D52DC041EC1D00C628C528A889C2A924BB895F4316A1BC87",
    "raw_size": 994_628,
    "sha256": "6E42E3394EE77C4DA440092FB67175CD31DDDF0263F50D284581934631312BFC",
    "size": 998_554,
}

# Pinned from the one no-write ``profile`` pass against the strict W85 input.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "9CA0764A3DB51F63F972883D6AC3DE0DBC557074C231F3C70DB3ED787ECF97BC",
    "raw_size": 994_676,
    "sha256": "AAFD78AF7299FC0CB64985BECA7E938C69EBC45779E2541AC12358FFB9CFD0F6",
    "size": 998_602,
}

# The reviewed scene contains no dynamic name tokens.  An empty reservation
# table is deliberate: it is not an assertion that names elsewhere are static.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    3231: (
        "하지만 그것은 구실에 불과했고,\n"
        f"진의는 이웃 {E}CC에치젠{E}CZ에 웅거해\n"
        f"{E}CA요시아키{E}CZ·{E}CA노부나가{E}CZ에 반항하는\n"
        f"{E}CA아사쿠라 요시카게{E}CZ를 견제하는 데 있었다."
    ),
    3234: (
        "이 자루는 무엇을 뜻할까?\n"
        "가신들은 답을 찾느라 고심했다.\n"
        "수수께끼를 푼 이는\n"
        f"{E}CA기노시타 히데요시{E}CZ였다."
    ),
    3238: (
        f"{E}CA노부나가{E}CZ는 그 동맹에 끼어들어\n"
        "아끼는 누이를 시집보냈다."
    ),
}

RATIONALES: Mapping[int, str] = {
    3231: "구실·진의·견제 대상의 관계를 원문과 PC EN/SC/TC 문맥대로 복원",
    3234: "수수께끼를 푼 주체를 가리키는 조사와 서술 연결을 복원",
    3238: "노부나가가 아끼는 누이를 혼인시켜 동맹에 개입한 의미를 복원",
}

TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    3231: (720, 648, 672, 936),
    3234: (576, 720, 432, 528),
    3238: (696, 600),
}


class Wave86Error(RuntimeError):
    """Raised when the W85 predecessor or W86 candidate contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave86Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave86Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_module("pc_event_wave80_base_for_wave86", W80_BUILDER)
parse_table = base.parse_table
core = base.core
control_signature = base.control_signature
is_full_width_visible = base.is_full_width_visible


@dataclass(frozen=True)
class Bundle:
    event: bytes
    changed: Mapping[int, str]
    rows: tuple[Mapping[str, Any], ...]
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
        raise Wave86Error(f"candidate escapes tmp root: {resolved}") from exc
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
            reservation = SCENE_RUNTIME_RESERVATIONS.get(token)
            require(reservation is not None, f"missing W86 scene reservation: {token}")
            rendered.append(str(reservation["display"]))
            cursor = runtime.end()
            continue
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if is_full_width_visible(character))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        rows.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_live_raw_960px": raw > RAW_LINE_LIMIT_PX,
            }
        )
    return tuple(rows)


def predecessor_configured() -> bool:
    return PREDECESSOR_CANDIDATE_ROOT is not None and EXPECTED_W85_PROFILE is not None


def require_predecessor_configuration() -> tuple[Path, Mapping[str, Any]]:
    require(
        predecessor_configured(),
        "W85 predecessor path/profile is not configured; do not build from an intermediate input",
    )
    assert PREDECESSOR_CANDIDATE_ROOT is not None
    assert EXPECTED_W85_PROFILE is not None
    return PREDECESSOR_CANDIDATE_ROOT, EXPECTED_W85_PROFILE


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    configured_root, expected_profile = require_predecessor_configuration()
    root = configured_root.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W85 candidate file scope drift: {sorted(actual_files)}")

    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W85 Kanegasaki predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == expected_profile, "W85 on-disk event profile drift")

    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == expected_profile, "W85 audit output profile drift")
    require(manifest.get("output") == expected_profile, "W85 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_jp() -> Any:
    return base.load_direct_jp()


def validate_static_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "W86 target scope drift")
    require(
        tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS,
        "W86 retained scope drift",
    )
    require(set(TARGET_RAW_WIDTHS) == set(CHANGED_IDS), "W86 target metrics scope drift")
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"unexpected W86 runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W86 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W86 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id],
            f"W86 pinned target widths drift: {entry_id}",
        )


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_static_targets()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Kanegasaki row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W85/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W86 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W86 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W86 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w85_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w85_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES.get(entry_id, "직접 PC JP 및 PC EN/SC/TC 문맥 대조 후 유지"),
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(runtime_tokens(target)),
                "runtime_proven": False,
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W86 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W85 Kanegasaki predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W86 Kanegasaki event", event)
    require(after_raw == rebuilt_raw, "W86 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W86 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W86 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W86 output profile drift")

    configured_root, _expected_predecessor = require_predecessor_configuration()
    audit = {
        "schema": "nobu16.kr.pc-event-kanegasaki-quality-wave86-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W85 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_text_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
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
            "runtime_reservations": SCENE_RUNTIME_RESERVATIONS,
            "runtime_reservations_scene_limited": True,
            "runtime_proven": False,
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": list(RETAINED_IDS),
            "unchanged_after_review_count": len(RETAINED_IDS),
        },
        "input_w85_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-kanegasaki-quality-wave86-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (configured_root / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
        },
        "changed_row_ids": list(CHANGED_IDS),
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, changed, tuple(rows), audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W86 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W86 candidate staging exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True, exist_ok=True)
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
    require(root.is_dir(), f"W86 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W86 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W86 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W86 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W86 candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "runtime_proven": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_kanegasaki_quality_wave86_v1.py",
        WORKSTREAM / "test_pc_event_kanegasaki_quality_wave86_v1.py",
    ):
        require(path.is_file(), f"W86 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W86 trailing whitespace: {path.name}:{number}")


def authoring_check() -> Mapping[str, Any]:
    validate_static_targets()
    return {
        "status": "PASS",
        "w85_predecessor_configured": predecessor_configured(),
        "changed_row_ids": list(CHANGED_IDS),
        "retained_row_ids": list(RETAINED_IDS),
        "target_raw_widths": {str(entry_id): list(widths) for entry_id, widths in TARGET_RAW_WIDTHS.items()},
        "candidate_written": False,
        "steam_game_resource_written": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("authoring-check", "profile", "build", "verify-private", "diff-check"),
    )
    command = parser.parse_args().command
    if command == "authoring-check":
        print(json.dumps(authoring_check(), ensure_ascii=False, sort_keys=True))
        return 0
    if command == "profile":
        bundle = prepare(require_output_profile=False)
        print(json.dumps(bundle.profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        bundle = prepare(require_output_profile=True)
        print(write_candidate(bundle))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": list(bundle.changed), "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
