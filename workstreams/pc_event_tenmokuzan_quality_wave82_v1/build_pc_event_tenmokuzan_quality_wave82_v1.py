#!/usr/bin/env python3
"""Build the W82 Takeda fall / Tenmokuzan event candidate from strict W81."""

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
W81_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_mitsuhide_quality_wave81_v1"
    / "build_pc_event_mitsuhide_quality_wave81_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(7_732, 7_752))
CHANGED_IDS = (7_733, 7_735, 7_739, 7_741, 7_744, 7_746, 7_749, 7_750)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W81_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "E9D196E3DF6A086C9A2E9704CE89A8BD1701EB088D9AF795D65A4055CA729522",
    "raw_size": 994_000,
    "sha256": "0B18991E5B9DA4BF7D94A5583C2F868DB69292AD12CFD6B48AF86318AEAFB516",
    "size": 997_923,
}

# Pinned from the single read-only W82 profile pass before the only candidate write.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "844FC26539B16C076A597E77EC872FFD6270F19F65DC069D6F8A8BA79FB2FE51",
    "raw_size": 994_028,
    "sha256": "0CB2A885FB3316D8009DEBDCB619AC4540FF30D07F6EA8CFB43F67586104FEC5",
    "size": 997_952,
}

# Scene-limited conservative reservation, not a live runtime observation.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[bs1871]": {
        "display": "마쓰다이라",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W81 slot 1871; conservative surname reservation for the Takeda fall scene",
    },
}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    7733: (
        "일문중·후다이중마저 잇달아 배반하자,\n"
        f"{E}CB다케다가{E}CZ 당주 {E}CA가쓰요리{E}CZ는 가족을 이끌고\n"
        "도주하면서도 어떤 결단을 내려야 했다…"
    ),
    7735: (
        f"거리도 가깝고, 아내의 친정 {E}CB호조 가{E}CZ와도\n"
        f"가까웠기에, {E}CA가쓰요리{E}CZ는\n"
        f"{E}CC이와도노성{E}CZ을 택한다…"
    ),
    7739: (
        "안 됩니다, 기다리십시오!\n"
        f"적은 {E}CB오야마다{E}CZ군입니다!\n"
        f"{E}CA오야마다 노부시게{E}CZ 님이 {E}CB오다{E}CZ로\n"
        "돌아선 듯합니다!"
    ),
    7741: (
        "모두, 나를… 인정하지 않겠다는 것인가.\n"
        f"나는 {E}CB다케다{E}CZ의 당주가 아니다…\n"
        f"{E}CB다케다{E}CZ의 사내조차 아니란 말인가…"
    ),
    7744: (
        f"알겠다. {E}CB다케다{E}CZ의 당주로서\n"
        "부끄럽지 않도록, 깨끗이 할복하겠다.\n"
        "모두, 뒤를 부탁한다!"
    ),
    7746: (
        "목숨을 건 가신들의 방어로\n"
        f"잠시 시간을 번 {E}CA가쓰요리{E}CZ는 처자와 함께\n"
        "자결할 최후의 땅을 찾았다."
    ),
    7749: (
        "부인의 사세구에 이르길…\n"
        "「검은 머리칼처럼 어지러운 세상은\n"
        "　끝이 없고, 그리움에 스러지는\n"
        "　이슬 같은 목숨이여」"
    ),
    7750: (
        "모두, 미안하다…!\n"
        f"{E}CB다케다{E}CZ의 이름은…\n"
        f"이 {E}CC덴모쿠산{E}CZ에서 스러지는구나…\n"
        "아버님… 용서해 주시오…"
    ),
}

RATIONALES: Mapping[int, str] = {
    7733: "일문중·후다이중의 연쇄 배반, 가족 동반 도주, 결단 강요를 모두 복원",
    7735: "거리와 아내 친정 호조 가문에 대한 근접성이라는 두 선택 근거를 명료화",
    7739: "오야마다 군의 습격과 노부시게의 오다 배반을 어절·의미 단위로 재배치",
    7741: "가쓰요리의 당주·다케다 일원 자격 부정이라는 자문을 자연스러운 한국어로 복원",
    7744: "깨끗이 할복하다의 결합을 보존하고 당주로서의 결의를 재배치",
    7746: "防戦을 방어로 바로잡고 처자와 함께 자결할 최후의 땅을 찾는 흐름을 복원",
    7749: "검은 머리칼·어지러운 세상·끝없는 그리움·이슬 같은 목숨의 사세구 이미지를 복원",
    7750: "이 덴모쿠산에서 다케다의 이름이 끝난다는 문장을 의미 단위로 재배치",
}


class Wave82Error(RuntimeError):
    """Raised when the strict W81 predecessor or W82 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave82Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave82Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w81 = load_module("pc_event_wave81_for_wave82", W81_BUILDER)
parse_table = w81.parse_table
core = w81.core
control_signature = w81.control_signature
is_full_width_visible = w81.is_full_width_visible


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
        raise Wave82Error(f"candidate escapes tmp root: {resolved}") from exc
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
            require(reservation is not None, f"missing W82 scene reservation: {token}")
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


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = w81.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W81 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W81 Tenmokuzan predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W81_PROFILE, "W81 on-disk event profile drift")
    require(w81.EXPECTED_OUTPUT_PROFILE == EXPECTED_W81_PROFILE, "W81 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W81_PROFILE, "W81 audit output profile drift")
    require(manifest["output"] == EXPECTED_W81_PROFILE, "W81 manifest output profile drift")
    return event, table, raw, predecessor_profile


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = w81.w80.load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W82 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W82 retained scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Tenmokuzan row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W81/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W82 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        tokens = runtime_tokens(target)
        for token in tokens:
            require(token in SCENE_RUNTIME_RESERVATIONS, f"unexpected W82 runtime token: {entry_id}: {token}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W82 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W82 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w81_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w81_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES.get(entry_id, "직접 PC JP 및 PC EN/SC/TC 문맥 대조 후 유지"),
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(tokens),
                "runtime_proven": False,
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W82 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W81 Tenmokuzan predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W82 Tenmokuzan event", event)
    require(after_raw == rebuilt_raw, "W82 raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS), "W82 actual event diff scope drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W82 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W82 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-tenmokuzan-quality-wave82-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W81 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
        "input_w81_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-tenmokuzan-quality-wave82-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w81.WORKSTREAM.name,
            "candidate_relative": (w81.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W82 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W82 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W82 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W82 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W82 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W82 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W82 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_tenmokuzan_quality_wave82_v1.py",
        WORKSTREAM / "test_pc_event_tenmokuzan_quality_wave82_v1.py",
    ):
        require(path.is_file(), f"W82 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W82 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
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
