#!/usr/bin/env python3
"""Build the W72 Okehazama source-faithful event correction candidate."""

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
W71_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_anegawa_raw960_wave71_v1"
    / "build_pc_event_anegawa_raw960_wave71_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(4_494, 4_511))
CHANGED_IDS = (4_494, 4_495, 4_496, 4_498, 4_502, 4_503, 4_504, 4_506, 4_507, 4_508, 4_509)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# This display is scene-specific evidence from the 1560 Okehazama context.
# It must not be reused as a global b1448 reservation.
SCENE_RUNTIME_RESERVATIONS = {(4_509, "[b1448]"): "나가오 가게토라"}

TARGETS: Mapping[int, str] = {
    4494: "오케하자마 전투에서\n「\x1bCA요시모토\x1bCZ의 목을 반드시 베겠다」는\n\x1bCB오다군\x1bCZ의 집념은 실로 대단하여…",
    4495: "\x1bCA노부나가\x1bCZ도 말에서 내려\n측근 무사들을 이끌고,\n병졸들 틈에 섞여 몸소 칼을 휘두르며,",
    4496: "몇 번이나 밀려났지만,\n\x1bCB이마가와군\x1bCZ의 중추를\n끝까지 몰아붙였다고 전한다.",
    4498: "아뢰옵니다!\n\x1bCA모리 신스케\x1bCZ 님께서 적장 \x1bCA요시모토\x1bCZ를\n베셨습니다!",
    4502: "（이자가 가이도 제일의 무사,\n\x1bCA이마가와 지부타이후\x1bCZ인가.\n이자가 오랫동안 나를 괴롭힌 자……）",
    4503: "（무거운 수급이로군……\n하지만 사람의 목은\n살아 있을 때 가벼운 법.）",
    4504: "음?\n이건?",
    4506: "\x1bCA노부나가\x1bCZ는 \x1bCA요시모토\x1bCZ가 지니던\n「소자 사몬지」라는 칼에\n다음과 같이 새기고,\n자신의 애검으로 삼았다고 전한다.",
    4507: "\u3000에이로쿠 3년 5월 19일\n\u3000요시모토를 베었을 때\n\u3000그가 지니던 칼\n\u3000\u3000\u3000오다 오와리노카미 노부나가",
    4508: "가이도 제일의 무사,\n\x1bCA이마가와 요시모토\x1bCZ의 죽음은 일개 다이묘\n\x1bCA오다 노부나가\x1bCZ를 전국 시대의 중심 무대로\n끌어올렸을 뿐 아니라…",
    4509: "가이·사가미·스루가 삼국 동맹의\n동요와, 그로 인한 \x1bCA[b1448]\x1bCZ의\n간토 출병, \x1bCB미카와 마쓰다이라 가문\x1bCZ의\n독립 등,",
}

RATIONALES: Mapping[int, str] = {
    4494: "위협의 인용과 오다군 집념의 강조를 자연스럽게 복원",
    4495: "馬廻衆을 측근 무사로 풀고 노부나가의 직접 전투를 보존",
    4496: "반복된 격퇴와 이마가와군 중추 압박을 원문 순서로 복원",
    4498: "보고체와 적장 요시모토 토벌 사실을 명확화",
    4502: "海道一の弓取り·今川治部大輔의 별칭·관직 호칭을 보존",
    4503: "살아 있는 사람의 목이라는 대조를 축약 없이 복원",
    4504: "짧은 반응을 자연스러운 한국어 의문으로 정리",
    4506: "종삼좌문이라는 칼과 비문·애검 관계를 온전히 복원",
    4507: "비문의 독법을 ‘요시모토를 베었을 때 / 그가 지니던 칼’로 교정",
    4508: "일개 다이묘 오다 노부나가를 전국 시대의 중심 무대로 끌어올린 관계를 복원",
    4509: "甲相駿을 가이·사가미·스루가로 바로잡고 원문에 없는 접속을 제거",
}

EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "EF31CE39405A20B81DD824437A7DF4770741D8C660434A3F7D512A36CE9D587E",
    "raw_size": 991_420,
    "sha256": "AB491AEA7B1C6499027797979563BCA0966AF488CCD306FED6D12D0E4F9C55F2",
    "size": 995_333,
}


class Wave72Error(RuntimeError):
    """Raised when W72 source, structure, or output contracts drift."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave72Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave72Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w71 = load_module("pc_event_wave71_for_wave72", W71_BUILDER)


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
        raise Wave72Error(f"candidate escapes tmp root: {resolved}") from exc
    return resolved


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
    require(not in_colour_span, "unterminated ESC colour tag")


def is_full_width_visible(character: str) -> bool:
    return w71.is_full_width_visible(character)


def rendered_display_line(entry_id: int, value: str) -> str:
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
            display = SCENE_RUNTIME_RESERVATIONS.get((entry_id, token))
            require(display is not None, f"no Okehazama runtime reservation for {entry_id}:{token}")
            rendered.append(display)
            cursor = runtime.end()
            continue
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(entry_id: int, value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(entry_id, line)
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


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(event),
        "size": len(event),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def prepare(*, require_output_profile: bool) -> Bundle:
    base = w71.prepare(require_output_profiles=True)
    before_event = base.outputs[MSGEV]
    _header, _raw, before = w71.w66.w60.parse_table("W71 Korean event", before_event)
    jp_blob, _jp_profile = w71.w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w71.w66.w60.parse_table("direct PC Japanese event", jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W72 target scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Okehazama row: {entry_id}")
        current_signature = w71.w70.control_signature(current)
        jp_signature = w71.w70.control_signature(source_jp)
        target_signature = w71.w70.control_signature(target)
        require(current_signature == jp_signature, f"current/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W72 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        metrics = line_metrics(entry_id, target)
        require(1 <= len(metrics) <= MAX_LINES, f"W72 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W72 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w71_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w71_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "rationale": RATIONALES.get(entry_id, "JP·KO 문맥 및 제어 구조를 재확인해 현행 유지"),
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W72 changed ID scope drift")
    rebuilt_raw = w71.w66.w60.core.rebuild_message_table(before, tuple(texts))
    header, _before_raw, _before_table = w71.w66.w60.parse_table("W71 Korean event", before_event)
    event = w71.w66.w60.core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = w71.w66.w60.parse_table("W72 Okehazama event", event)
    require(after_raw == rebuilt_raw, "W72 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W72 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W72 output profile drift")
    audit = {
        "schema": "nobu16.kr.pc-event-okehazama-quality-wave72-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "Steam PC W71 Korean plus direct PC JP/EN/SC/TC review",
            "switch_korean_used": False,
            "japanese_source_linebreaks_used": False,
            "korean_text_shortened": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "live_raw_line_limit_px": RAW_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "runtime_reservations": {"4509:[b1448]": "나가오 가게토라"},
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": [entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS],
        },
        "input_w71_event_profile": profile(before_event, _raw),
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-okehazama-quality-wave72-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "changed_row_ids": list(CHANGED_IDS),
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, changed, tuple(rows), audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W72 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W72 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W72 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W72 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W72 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W72 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W72 candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_okehazama_quality_wave72_v1.py",
        WORKSTREAM / "test_pc_event_okehazama_quality_wave72_v1.py",
    ):
        require(path.is_file(), f"W72 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W72 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        bundle = prepare(require_output_profile=False)
        print(json.dumps({"changed_row_ids": list(CHANGED_IDS), "event_profile": bundle.profile}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "build":
        bundle = prepare(require_output_profile=False)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    source_whitespace_check()
    print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
