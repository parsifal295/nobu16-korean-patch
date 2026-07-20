#!/usr/bin/env python3
"""Build the W84 Koshu-campaign event candidate from strict on-disk W83."""

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
W82_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_tenmokuzan_quality_wave82_v1"
    / "build_pc_event_tenmokuzan_quality_wave82_v1.py"
)

# Strict on-disk predecessor, reported from the independently completed W83
# candidate.  W84 may only build from this exact candidate/profile.
W83_WORKSTREAM_NAME = "pc_event_takamatsu_quality_wave83_v1"
W83_BUILDER = (
    REPO
    / "workstreams"
    / W83_WORKSTREAM_NAME
    / "build_pc_event_takamatsu_quality_wave83_v1.py"
)
EXPECTED_W83_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "2EA33030A96FBAD95AC36236682FD45E750F7F035AAD52A5EECC90862F4C81B8",
    "raw_size": 994_192,
    "sha256": "90A9314C575703326A0374B58A1C2E5E0D7BF9250B81C8EC2D553E7E8F36846E",
    "size": 998_116,
}

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(7_779, 7_793))
CHANGED_IDS = (7_779, 7_780, 7_781, 7_782, 7_791, 7_792)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# Pinned from the one read-only W84 profile pass against strict W83.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "5D4A4C7CA96421E7BEE761A241A5B3252A48DEC720BE1993477BA7D2EC05C586",
    "raw_size": 994_296,
    "sha256": "7CA04F8EAE44EC27202268896F3D1CAA4BB4C90CEC6591C037ECCEC2A62D122B",
    "size": 998_221,
}

# Scene-limited conservative reservations, never a claim of live observation.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[bm1251]": {
        "display": "다케다 하루노부",
        "source_slot_id": 1251,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W84 scene-local conservative historical full-name reservation",
    },
    "[bs1871]": {
        "display": "마쓰다이라",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W84 scene-local conservative surname reservation",
    },
    "[bm1871]": {
        "display": "마쓰다이라 모토야스",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W84 scene-local conservative historical full-name reservation",
    },
    "[b1871]": {
        "display": "마쓰다이라 모토야스",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W84 scene-local conservative historical full-name reservation",
    },
}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    7779: (
        f"{E}CC나가시노{E}CZ 전투에서 대패한 뒤,\n"
        f"{E}CA다케다 가쓰요리{E}CZ는 가문의 개혁을\n"
        "서둘렀다."
    ),
    7780: (
        f"{E}CA신겐{E}CZ 시대의 상징인\n"
        f"{E}CC쓰쓰지가사키관{E}CZ을 떠나, {E}CC니라사키{E}CZ에 새로\n"
        f"{E}CC신푸성{E}CZ을 쌓아 본거지로 삼고\n"
        "중앙집권화를 추진하려 했다."
    ),
    7781: (
        "‘사람이 성, 사람이 석벽’이라는\n"
        "신념으로 성곽에 집착하지 않았던\n"
        f"{E}CA[bm1251]{E}CZ를 아는 가신들에게\n"
        f"{E}CC신푸{E}CZ 축성은 평이 좋지 않았다."
    ),
    7782: (
        f"{E}CA가쓰요리{E}CZ의 매제 {E}CA기소 요시마사{E}CZ마저\n"
        "축성과 관련된 부역에 불만이 쌓였는지,\n"
        f"{E}CB다케다가{E}CZ를 떠나 {E}CB오다가{E}CZ로 돌아선 것이다…"
    ),
    7791: (
        f"{E}CA오다 노부나가{E}CZ는 적자 {E}CA노부타다{E}CZ를\n"
        f"총대장에 임명하고, {E}CA다키가와 가즈마스{E}CZ를\n"
        f"보좌로 삼아 {E}CC고슈{E}CZ 정벌을 개시했다."
    ),
    7792: (
        f"{E}CC스루가{E}CZ에서는 {E}CA[b1871]{E}CZ가,\n"
        f"{E}CC간토{E}CZ에서는 {E}CA호조 우지마사{E}CZ가\n"
        f"각각 전선에 합류해, {E}CB다케다가{E}CZ는\n"
        "사방의 적을 맞게 되었다…"
    ),
}

RATIONALES: Mapping[int, str] = {
    7779: "대패한 뒤의 결합을 보존하고 가문 개혁을 서둘렀다는 흐름을 재배치",
    7780: "신겐 시대의 상징·새 신푸성 축성·중앙집권화 추진 의도를 모두 복원",
    7781: "사람이 성이라는 신념, 성곽 비집착, 복수 가신의 신푸 축성 불평을 복원",
    7782: "축성과 관련된 부역의 불만, 다케다 이탈과 오다 배반의 인과를 복원",
    7791: "노부타다 총대장 임명·가즈마스 보좌·고슈 정벌 개시의 종결을 완성",
    7792: "스루가·간토에서 각각 참전한 사실과 사방의 적을 맞게 된 결과를 복원",
}


class Wave84Error(RuntimeError):
    """Raised when W83 is unpinned or its strict predecessor contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave84Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave84Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w82 = load_module("pc_event_wave82_for_wave84", W82_BUILDER)
parse_table = w82.parse_table
core = w82.core
control_signature = w82.control_signature
is_full_width_visible = w82.is_full_width_visible


def load_w83() -> Any:
    require(W83_WORKSTREAM_NAME is not None, "W83 workstream is not pinned")
    require(W83_BUILDER is not None, "W83 builder path is not pinned")
    require(EXPECTED_W83_PROFILE is not None, "W83 output profile is not pinned")
    require(W83_BUILDER.is_file(), f"W83 builder is missing: {W83_BUILDER}")
    return load_module("pc_event_wave83_for_wave84", W83_BUILDER)


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
        raise Wave84Error(f"candidate escapes tmp root: {resolved}") from exc
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
            require(reservation is not None, f"missing W84 scene reservation: {token}")
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


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any], Any]:
    w83 = load_w83()
    root = w83.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W83 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W83 Koshu predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W83_PROFILE, "W83 on-disk event profile drift")
    require(w83.EXPECTED_OUTPUT_PROFILE == EXPECTED_W83_PROFILE, "W83 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W83_PROFILE, "W83 audit output profile drift")
    require(manifest["output"] == EXPECTED_W83_PROFILE, "W83 manifest output profile drift")
    return event, table, raw, predecessor_profile, w83


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile, w83 = load_predecessor()
    direct_jp = w82.w81.w80.load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W84 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W84 retained scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Koshu row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W83/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W84 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        tokens = runtime_tokens(target)
        for token in tokens:
            require(token in SCENE_RUNTIME_RESERVATIONS, f"unexpected W84 runtime token: {entry_id}: {token}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W84 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W84 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w83_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w83_current_ko_utf16le_sha256": text_hash(current),
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
    require(tuple(sorted(changed)) == CHANGED_IDS, "W84 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W83 Koshu predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W84 Koshu event", event)
    require(after_raw == rebuilt_raw, "W84 raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS), "W84 actual event diff scope drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W84 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W84 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-koshu-campaign-quality-wave84-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W83 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
        "input_w83_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-koshu-campaign-quality-wave84-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w83.WORKSTREAM.name,
            "candidate_relative": (w83.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W84 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W84 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W84 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W84 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W84 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W84 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W84 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_koshu_campaign_quality_wave84_v1.py",
        WORKSTREAM / "test_pc_event_koshu_campaign_quality_wave84_v1.py",
    ):
        require(path.is_file(), f"W84 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W84 trailing whitespace: {path.name}:{number}")


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
