#!/usr/bin/env python3
"""Build the W88 Honganji uprising event-quality candidate from strict W87.

This candidate is deliberately private.  It reads only the already verified
W87 candidate and the pinned direct PC Japanese table, then emits a rebuilt
``MSG_PK/JP/msgev.bin`` below ``tmp``.  It never writes the Steam game,
performs a Git operation, or publishes a release.
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

# Reuse only the stable message-table/control helpers.  The actual content
# predecessor is W87, fixed below; it is never the helper's own predecessor.
W80_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_naomasa_quality_wave80_v1"
    / "build_pc_event_naomasa_quality_wave80_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_hieizan_quality_wave87_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W87_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "1056F2EDB6661D9815F807D32FC743FD254390961E9114C5C86031EB76D03C59",
    "raw_size": 994_764,
    "sha256": "76E176F3917A6D549CE8B8748D1172C145FF6D6F2E119A89B72FBB3887CCF293",
    "size": 998_690,
}

SCENE_IDS = tuple(range(5_938, 5_956))
CHANGED_IDS = (5_939, 5_944, 5_946, 5_947, 5_952)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

# The static-patch-007 baseline used by this workstream is a four-line,
# raw-G1N safety gate.  ``effective_width_px`` is recorded for the 30px
# renderer but remains report-only here.
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# This is a conservative scene-local reservation, not a claim about the
# runtime prefix semantics.  Slot 75 currently contains the 408px full name
# below, whose raw width is used solely to reserve [bm75]'s rendered space.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[bm75]": {
        "display": "아시카가 요시테루",
        "source_slot_id": 75,
        "reserved_raw_g1n_width_px": 408,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W87 slot 75 conservative full-name reservation; prefix semantics not assumed",
    },
}
ROW_RUNTIME_TOKENS: Mapping[int, tuple[str, ...]] = {5_944: ("[bm75]",)}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    5939: (
        f"그 고민의 원인은, 쇼군이 된 {E}CA요시아키{E}CZ를\n"
        "돕는… 아니, 뒤에서 조종하는 실력자\n"
        f"{E}CA노부나가{E}CZ의 존재였다."
    ),
    5944: (
        f"{E}CA[bm75]{E}CZ 공·{E}CA미요시 나가요시{E}CZ와는\n"
        "관계가 나쁘지 않았다.\n"
        f"하지만 지금 구보님 뒤의 {E}CA노부나가{E}CZ란 자는,\n"
        "아무래도 위험해 보인다……"
    ),
    5946: (
        f"만약 {E}CA노부나가{E}CZ가 우리 교단을 적대한다면,\n"
        "탄압받기 전에 선수를 쳐\n"
        "우리가 먼저 봉기하는 편이\n"
        "나을지도 모른다……"
    ),
    5947: (
        f"아네가와 패전에도 {E}CA노부나가{E}CZ를 적대하는\n"
        f"{E}CB아사쿠라{E}CZ·{E}CB아자이{E}CZ는 아직 건재하다.\n"
        f"그들과 손잡으면 {E}CA노부나가{E}CZ의 위협을\n"
        "미연에 막을 수 있을지도 모른다."
    ),
    5952: (
        f"({E}CB아사쿠라{E}CZ·{E}CB아자이{E}CZ에 이어 {E}CB혼간지{E}CZ까지\n"
        "반기를 들다니.\n"
        "쇼군으로서 내 권위가 낮은가,\n"
        f"아니면 {E}CA노부나가{E}CZ의 인망이 없는 탓인가……)"
    ),
}

RATIONALES: Mapping[int, str] = {
    5939: "고민의 원인, 요시아키의 쇼군 취임, 보좌를 가장한 배후 조종과 노부나가의 존재를 복원",
    5944: "미요시 성, 구보님 호칭, 현재 시점 및 노부나가의 위험성 판단을 원문 문맥대로 복원",
    5946: "우리 교단을 적대할 경우의 피탄압 전 선제 봉기와 더 나은 방책이라는 판단을 복원",
    5947: "아네가와 패전 뒤에도 건재한 아사쿠라·아자이와 미연 방지의 인과를 복원",
    5952: "반기를 든 주체, 쇼군으로서의 권위, 노부나가의 인망 부재를 복원",
}

TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    5939: (912, 816, 480),
    5944: (960, 504, 960, 576),
    5946: (936, 552, 600, 408),
    5947: (888, 768, 792, 744),
    5952: (816, 336, 672, 936),
}

# Pinned from the one read-only profile pass against the strict W87 input.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "1E7CDDD56016993624C7C18E80E754067D56B5DBA06075F7794198A1902586EB",
    "raw_size": 994_920,
    "sha256": "230953A3F700F86E6207EA4B77F4BC364765FCF5FC87CCC285CBA4AA27E3E054",
    "size": 998_847,
}


class Wave88Error(RuntimeError):
    """Raised when the strict predecessor or candidate contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave88Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave88Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W80_BUILDER.is_file(), f"W80 helper builder missing: {W80_BUILDER}")
base = load_module("pc_event_wave80_base_for_wave88", W80_BUILDER)
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
        raise Wave88Error(f"candidate escapes tmp root: {resolved}") from exc
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


def raw_width(display: str) -> int:
    full = sum(1 for character in display if is_full_width_visible(character))
    half = len(display) - full
    return full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX


def validate_runtime_reservations() -> None:
    require(set(SCENE_RUNTIME_RESERVATIONS) == {"[bm75]"}, "W88 reservation scope drift")
    for token, reservation in SCENE_RUNTIME_RESERVATIONS.items():
        display = reservation.get("display")
        configured_raw = reservation.get("reserved_raw_g1n_width_px")
        require(isinstance(display, str) and display, f"invalid W88 reservation display: {token}")
        require(type(configured_raw) is int and configured_raw > 0, f"invalid W88 reservation raw width: {token}")
        require(raw_width(display) == configured_raw, f"W88 reservation raw width drift: {token}")
        require(reservation.get("scene_limited") is True, f"W88 reservation not scene-limited: {token}")
        require(reservation.get("runtime_proven") is False, f"W88 runtime proof unexpectedly asserted: {token}")


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
            require(reservation is not None, f"missing W88 scene reservation: {token}")
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


def reservation_details(value: str) -> list[Mapping[str, Any]]:
    return [
        {"token": token, **SCENE_RUNTIME_RESERVATIONS[token]}
        for token in runtime_tokens(value)
    ]


def validate_static_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "W88 target scope drift")
    require(
        tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS,
        "W88 retained scope drift",
    )
    require(set(TARGET_RAW_WIDTHS) == set(CHANGED_IDS), "W88 target metrics scope drift")
    validate_runtime_reservations()
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(
            runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()),
            f"W88 runtime token scope drift: {entry_id}",
        )
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W88 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W88 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id],
            f"W88 pinned target widths drift: {entry_id}",
        )


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W87 candidate file scope drift: {sorted(actual_files)}")

    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W87 Honganji predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W87_PROFILE, "W87 on-disk event profile drift")

    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W87_PROFILE, "W87 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W87_PROFILE, "W87 manifest output profile drift")
    return event, table, raw, predecessor_profile


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_static_targets()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = base.load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty W88 row: {entry_id}")

        current_signature = control_signature(current)
        require(current_signature == control_signature(source_jp), f"W87/direct-JP control drift: {entry_id}")
        require(control_signature(target) == current_signature, f"W88 control/token drift: {entry_id}")
        require(
            runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()),
            f"W88 runtime token differs in row: {entry_id}",
        )
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W88 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W88 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )

        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w87_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w87_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES.get(entry_id, "direct PC JP and PC EN/SC/TC context revalidated; retained"),
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(runtime_tokens(target)),
                "runtime_reservations": reservation_details(target),
                "runtime_proven": False,
                "control_signature": control_signature(target),
            }
        )

    require(tuple(sorted(changed)) == CHANGED_IDS, "W88 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W87 Honganji predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W88 Honganji event", event)
    require(after_raw == rebuilt_raw, "W88 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W88 actual event diff scope drift",
    )

    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W88 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W88 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-honganji-quality-wave88-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W87 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
        "input_w87_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-honganji-quality-wave88-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W88 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W88 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W88 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W88 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W88 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W88 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W88 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_honganji_quality_wave88_v1.py",
        WORKSTREAM / "test_pc_event_honganji_quality_wave88_v1.py",
    ):
        require(path.is_file(), f"W88 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W88 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        print(write_candidate(prepare(require_output_profile=True)))
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
