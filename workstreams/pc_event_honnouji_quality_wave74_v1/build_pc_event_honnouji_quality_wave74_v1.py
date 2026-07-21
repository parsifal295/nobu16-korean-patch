#!/usr/bin/env python3
"""Build the W74 Honnouji event-quality candidate from the W73 predecessor."""

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
W73_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_imayama_quality_wave73_v1"
    / "build_pc_event_imayama_quality_wave73_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(10_990, 11_010))
CHANGED_IDS = (10_990, 10_995, 10_996, 10_998, 10_999, 11_000, 11_003, 11_004, 11_006, 11_008, 11_009)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
STATIC_EFFECTIVE_LINE_LIMIT_PX = 912
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W73_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "CDDCD9F37B76F93B06A1D62AA3C1483C0F915FF214E8DBCC62D17B3787799929",
    "raw_size": 991_568,
    "sha256": "1F578E167642BDA264AE57F700A3E3EAD886107CC98970C7AE653F2319202996",
    "size": 995_482,
}
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "9940CD998E31B83B67AC8FB012B60625B34CC44BCDED8A3952DF49D11C0B8F03",
    "raw_size": 991_668,
    "sha256": "A31DAB5EF47BCCC0D41653C38F30E1D83E91860A4D3D9D314EE85695D9C56DC2",
    "size": 995_582,
}

TARGETS: Mapping[int, str] = {
    10990: "주군, 들어주십시오!\n이 \x1bCC혼노지\x1bCZ 지하에는 숨은 길이 있습니다…\n운이 좋으면 밖으로 빠져나갈 수\n있을지도 모릅니다.",
    10995: "그러게 말입니다…\n전란이 끊이지 않는 \x1bCC교토\x1bCZ의 거리이기에\n만일의 탈출구를 마련해 둔\n것이겠지요만…",
    10996: "다행히 숨은 길은 막다른 곳에\n이르지 않고, 구불구불 굽이치며\n앞으로 이어지고 있었다.\n이윽고…",
    10998: "하하, 정말 포위 밖으로\n나올 수 있었다니!\n이제 일단 죽을 고비는 벗어난 듯하구나…\n\x1bCA야스케\x1bCZ, 잘했다!",
    10999: "\x1bCA야스케\x1bCZ의 기지 덕에 살아난 \x1bCA노부나가\x1bCZ 일행.\n그들은 반역자 \x1bCA아케치 미쓰히데\x1bCZ에\n맞서기 위해 \x1bCC교토\x1bCZ를 빠져나와\n본거지 \x1bCC아즈치성\x1bCZ으로 향했다…",
    11000: "\x1bCA아케치 미쓰히데\x1bCZ의 배신으로부터\n며칠 뒤, \x1bCC아즈치성\x1bCZ―",
    11003: "\x1bCA아케치\x1bCZ 님의 모반이 있은 지\n며칠이 지나, \x1bCA오다 노부나가\x1bCZ가 죽었다는\n풍문이 영지 전역을 뒤덮고 있습니다.",
    11004: "\x1bCA하시바\x1bCZ 님, \x1bCA시바타\x1bCZ 님을 비롯한\n중신들께서도 주군을 수색하기보다는\n다음 천하를 차지하려는 듯한\n기색입니다…",
    11006: "이제 이 땅은 사방이 모두 적이다!\n…\x1bCA야스케\x1bCZ, \x1bCA란마루\x1bCZ, \x1bCA야스히데\x1bCZ!\n여기서 다시 천하를 차지해 보이겠다!",
    11008: "\x1bCC아즈치성\x1bCZ으로 돌아온 \x1bCA노부나가\x1bCZ는\n\x1bCA하시바\x1bCZ, \x1bCA시바타\x1bCZ 등 \x1bCB오다\x1bCZ의 옛 신하들과\n결별하고, \x1bCA야스케\x1bCZ 등 소수의 가신만으로\n독립을 선언했다.",
    11009: "\x1bCA하시바\x1bCZ, \x1bCA시바타\x1bCZ, \x1bCA아케치\x1bCZ 등 옛 중신을\n물리치고, 마땅히 있어야 할\n천하를 되찾기 위한 싸움이\n지금 막을 올렸다…",
}

RATIONALES: Mapping[int, str] = {
    10990: "숨은 길의 존재와 탈출 가능성을 모두 보존하고, 청원과 설명을 문맥 단위로 분리했다.",
    10995: "전란이 끊이지 않는 교토라는 이유와 만일의 탈출구라는 인과를 복원했다.",
    10996: "막다른 곳이 아님, 굽이침, 계속 전진, 이윽고라는 원문 진행을 모두 보존했다.",
    10998: "포위 탈출, 죽을 고비 회피, 야스케를 향한 칭찬을 각각 자연스러운 호흡으로 배치했다.",
    10999: "야스케의 기지, 반역자 미쓰히데에 맞섬, 교토 이탈, 아즈치성 귀환 목적을 보존했다.",
    11000: "배신 뒤 며칠과 아즈치성이라는 장면 전환 정보를 삭제 없이 분리했다.",
    11003: "모반 이후 경과, 노부나가 사망 풍문, 영지 전역 확산이라는 세 정보를 보존했다.",
    11004: "중신들의 명시, 주군 수색보다 다음 천하를 노리는 태도를 모두 보존했다.",
    11006: "사방의 적, 세 인물 호명, 재기 선언을 원문 순서대로 유지했다.",
    11008: "아즈치성 귀환, 옛 신하와 결별, 소수 가신으로 독립 선언을 문장으로 복원했다.",
    11009: "옛 중신 격파, 마땅히 있어야 할 천하 회복, 싸움의 개막을 모두 보존했다.",
}


class Wave74Error(RuntimeError):
    """Raised when the W73 predecessor or W74 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave74Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave74Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w73 = load_module("pc_event_wave73_for_wave74", W73_BUILDER)


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
        raise Wave74Error(f"candidate escapes tmp root: {resolved}") from exc
    return resolved


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(event),
        "size": len(event),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def rendered_display_line(value: str) -> str:
    rendered: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        require(runtime is None, f"unexpected runtime token in Honnouji scope: {runtime.group(0) if runtime else ''}")
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if w73.w72.is_full_width_visible(character))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        effective = (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX
        rows.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": effective,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_live_raw_960px": raw > RAW_LINE_LIMIT_PX,
                "over_static_patch_912px": effective > STATIC_EFFECTIVE_LINE_LIMIT_PX,
            }
        )
    return tuple(rows)


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    reconstructed = w73.prepare(require_output_profile=True)
    require(reconstructed.profile == EXPECTED_W73_PROFILE, "W73 reconstruction profile drift")
    path = w73.CANDIDATE_ROOT / MSGEV
    require(path.is_file(), f"W73 candidate missing: {path}")
    event = path.read_bytes()
    require(event == reconstructed.event, "W73 private candidate differs from its pinned reconstruction")
    _header, raw, table = w73.w72.w71.w66.w60.parse_table("W73 Honnouji predecessor", event)
    require(profile(event, raw) == EXPECTED_W73_PROFILE, "W73 candidate on-disk profile drift")
    return event, table, raw, reconstructed.profile


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    jp_blob, _jp_profile = w73.w72.w71.w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w73.w72.w71.w66.w60.parse_table("direct PC Japanese event", jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W74 target scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Honnouji row: {entry_id}")
        current_signature = w73.w72.w71.w70.control_signature(current)
        jp_signature = w73.w72.w71.w70.control_signature(source_jp)
        target_signature = w73.w72.w71.w70.control_signature(target)
        require(current_signature == jp_signature, f"W73/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W74 control/token drift: {entry_id}")
        w73.w72.assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W74 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W74 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            not any(metric["over_static_patch_912px"] for metric in metrics),
            f"W74 static-patch effective width exceeds {STATIC_EFFECTIVE_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w73_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w73_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "rationale": RATIONALES.get(entry_id, "W73 문구는 직접 JP와 제어 구조 대조 후 그대로 유지했다."),
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W74 changed ID scope drift")

    header, _parsed_raw, _parsed_table = w73.w72.w71.w66.w60.parse_table("W73 Honnouji predecessor", before_event)
    rebuilt_raw = w73.w72.w71.w66.w60.core.rebuild_message_table(before, tuple(texts))
    event = w73.w72.w71.w66.w60.core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = w73.w72.w71.w66.w60.parse_table("W74 Honnouji event", event)
    require(after_raw == rebuilt_raw, "W74 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W74 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W74 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W74 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-honnouji-quality-wave74-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "W73 Steam-PC Korean candidate plus direct PC JP review",
            "switch_korean_used": False,
            "japanese_source_linebreaks_used": False,
            "korean_text_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "strict_live_raw_line_limit_px": RAW_LINE_LIMIT_PX,
            "static_patch_effective_line_limit_px": STATIC_EFFECTIVE_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "runtime_reservations": {},
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": [entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS],
        },
        "input_w73_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-honnouji-quality-wave74-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w73.WORKSTREAM.name,
            "candidate_relative": (w73.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
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
    require(not output.exists(), f"W74 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W74 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W74 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W74 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W74 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W74 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W74 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_honnouji_quality_wave74_v1.py",
        WORKSTREAM / "test_pc_event_honnouji_quality_wave74_v1.py",
    ):
        require(path.is_file(), f"W74 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W74 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        bundle = prepare(require_output_profile=False)
        print(json.dumps(bundle.profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        bundle = prepare(require_output_profile=True)
        output = write_candidate(bundle)
        print(output)
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
