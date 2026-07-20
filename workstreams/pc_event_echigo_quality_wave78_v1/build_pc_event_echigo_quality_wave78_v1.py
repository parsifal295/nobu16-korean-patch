#!/usr/bin/env python3
"""Build the W78 Echigo event-quality candidate from strict on-disk W77."""

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
W77_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_komaki_nagakute_quality_wave77_v1"
    / "build_pc_event_komaki_nagakute_quality_wave77_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(4_280, 4_315))
CHANGED_IDS = (
    4_281,
    4_288,
    4_289,
    4_290,
    4_294,
    4_296,
    4_298,
    4_299,
    4_302,
    4_303,
    4_304,
    4_313,
    4_314,
)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
STATIC_EFFECTIVE_LINE_LIMIT_PX = 912
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# This is the exact profile produced by the already-built, on-disk W77
# candidate.  W78 never falls back to a Steam installation or an older wave.
EXPECTED_W77_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "1F191E28DCFF25D7BC619983782A136D1A6F5FA053C2AC432792256C54B9D3F1",
    "raw_size": 992_912,
    "sha256": "8B85E62DE5611DE14B51BA50B1C4F57F40DB56DFF6ADAC119594196B0FAADB9F",
    "size": 996_831,
}

# Pinned after the in-memory W78 profile pass and before the single candidate
# write.  Keep this non-None for normal build / verification commands.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "9FA155B0CFFA17CC9BD3DCAC376779CB212A4DB9E2928AF0800181BE6257AD2B",
    "raw_size": 993_244,
    "sha256": "4C1C40CFB55F4DA111D7D33471EB6AB8CB84134006E7F5F8E659FFDEA302B357",
    "size": 997_165,
}

# The game has not been observed rendering these dynamic values in this exact
# scene.  Reserving the longest locally relevant historical spelling is a
# conservative layout bound only, so every reservation explicitly remains
# runtime_proven=false.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[b1448]": {
        "display": "나가오 가게토라",
        "source_slot_id": 1448,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W77 scene-local conservative maximum historical-name reservation",
    },
    "[bm1448]": {
        "display": "나가오 가게토라",
        "source_slot_id": 1448,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W77 scene-local conservative maximum historical-name reservation",
    },
    "[bs1448]": {
        "display": "나가오 가게토라",
        "source_slot_id": 1448,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W77 scene-local conservative maximum historical-name reservation",
    },
}

TARGETS: Mapping[int, str] = {
    4281: (
        "그 이유는, 당주 \x1bCA[bm1448]\x1bCZ가\n"
        "모든 정무를 내팽개치고,\n"
        "\x1bCC비샤몬도\x1bCZ에 틀어박힌 채\n"
        "밖으로 나오지 않았기 때문이다……"
    ),
    4288: (
        "\x1bCC비샤몬도\x1bCZ에서 마침내 나온\n"
        "\x1bCA[bm1448]\x1bCZ는 돌연 출가를 선언해\n"
        "가신들을 더 큰 혼란에 빠뜨렸다."
    ),
    4289: (
        "오래도록 \x1bCB[bs1448]\x1bCZ 가문을 섬기며\n"
        "\x1bCA오쿠마 도모히데\x1bCZ도 \x1bCA[bm1448]\x1bCZ 옹립에\n"
        "힘썼으나, 이 혼란을 틈타 \x1bCB다케다\x1bCZ와\n"
        "내통해 반기를 들었다……"
    ),
    4290: (
        "당황한 가신들은 \x1bCA[bm1448]\x1bCZ의 폭주를\n"
        "막을 수 있는 유일한 인물,\n"
        "\x1bCA[bm1448]\x1bCZ의 스승 \x1bCA덴시쓰 고이쿠\x1bCZ에게\n"
        "도움을 청했다."
    ),
    4294: "그대들 스스로 가슴에 손을 얹고\n생각해 보라! 답은 그 안에 있느니라……",
    4296: (
        "선문답이 아니다. \x1bCA[bm1448]\x1bCZ를\n"
        "가장 괴롭히는 근심은……\n"
        "그대들 \x1bCB[bs1448] 가문\x1bCZ 가신과\n"
        "\x1bCB에치고 국인\x1bCZ의 행실이다!"
    ),
    4298: (
        "밖에는 \x1bCB다케다\x1bCZ와 잇코잇키 같은 적이 있고,\n"
        "안에는 \x1bCA오쿠마\x1bCZ 같은 반란자가 있으니,\n"
        "\x1bCC에치고\x1bCZ는 전례 없는 위기에 놓였다."
    ),
    4299: (
        "그런데도 그대들은 \x1bCC에치고\x1bCZ를 이끄는\n"
        "슈고다이 \x1bCA[b1448]\x1bCZ의 명을\n"
        "따르지 않고, 저마다의 이해로\n"
        "대립하며 서로 반목한다!"
    ),
    4302: (
        "\x1bCA[bm1448]\x1bCZ는 지금의\n"
        "\x1bCB[bs1448] 가문\x1bCZ에서 그 유대를\n"
        "느끼지 못하기에 출가하겠다고 한 것이오.\n"
        "소승이 무슨 간언을 해도 소용없을 터……"
    ),
    4303: (
        "우리 탓에 \x1bCA[bm1448]\x1bCZ 님께서\n"
        "출가하신다면, 우리가 하나로 뭉쳐\n"
        "\x1bCA[bm1448]\x1bCZ 님을 받들겠다고\n"
        "맹세할 수밖에 없겠군."
    ),
    4304: (
        "\x1bCA나가오 마사카게\x1bCZ는 가신과 국인을\n"
        "두루 설득했고, 가신들은 연명으로\n"
        "\x1bCA[bm1448]\x1bCZ에게 충절을 맹세하는\n"
        "서장을 작성했다."
    ),
    4313: (
        "\x1bCA[bm1448]\x1bCZ의 결사적인 출가 선언으로\n"
        "단결을 다진 \x1bCC에치고\x1bCZ 무사들은,\n"
        "\x1bCA[bm1448]\x1bCZ의 지휘 아래\n"
        "\x1bCA오쿠마 도모히데\x1bCZ를 꺾어 \x1bCC엣추\x1bCZ로 내쫓았다."
    ),
    4314: (
        "\x1bCA[bm1448]\x1bCZ는 국내를 하나로 모은 뒤,\n"
        "마침내 외적 \x1bCB다케다 가문\x1bCZ과 맞설\n"
        "각오를 새로이 다졌다."
    ),
}

RATIONALES: Mapping[int, str] = {
    4281: "모든 정무 포기와 은거가 혼란의 직접 원인이라는 인과를 복원한다.",
    4288: "마침내 비샤몬도에서 나온 뒤 출가를 선언한 순서를 복원한다.",
    4289: "오쿠마가 혼란을 틈타 다케다와 내통하고 반기를 든 정보를 복원한다.",
    4290: "막을 수 있는 유일한 인물과 그의 스승이라는 수식 관계를 바로잡는다.",
    4294: "생각해/보라로 갈린 수동 개행을 의미 단위로 재배치한다.",
    4296: "가게토라를 가장 괴롭힌 근심과 가신·국인의 행실이라는 책임 소재를 복원한다.",
    4298: "외적과 내란, 전례 없는 위기라는 원문의 병렬 구조를 복원한다.",
    4299: "슈고다이의 명령 불복종, 각자 이익, 상호 반목을 복원한다.",
    4302: "유대 상실, 출가 선언, 간언 무용의 네 의미 단위를 복원한다.",
    4303: "출가의 원인이 자신들에게 있다면 단결해 받들겠다는 맹세를 복원한다.",
    4304: "국인을 두루 설득하고 연명 충성 서장을 작성한 흐름을 복원한다.",
    4313: "결사적 출가 선언, 단결, 도모히데 격퇴와 엣추 추방을 복원한다.",
    4314: "국내 통합 뒤 외적 다케다와 맞설 결의를 복원한다.",
}


class Wave78Error(RuntimeError):
    """Raised when the strict W77 predecessor or W78 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave78Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave78Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w77 = load_module("pc_event_wave77_for_wave78", W77_BUILDER)
parse_table = w77.parse_table
core = w77.core
control_signature = w77.control_signature
is_full_width_visible = w77.is_full_width_visible


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
        raise Wave78Error(f"candidate escapes tmp root: {resolved}") from exc
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
            require(reservation is not None, f"missing W78 scene reservation: {token}")
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
    root = w77.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W77 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W77 Echigo predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W77_PROFILE, "W77 on-disk event profile drift")
    require(w77.EXPECTED_OUTPUT_PROFILE == EXPECTED_W77_PROFILE, "W77 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W77_PROFILE, "W77 audit output profile drift")
    require(manifest["output"] == EXPECTED_W77_PROFILE, "W77 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_jp() -> Any:
    return w77.load_direct_jp()


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W78 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W78 retained scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Echigo row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W77/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W78 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W78 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W78 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            not any(metric["over_static_patch_912px"] for metric in metrics),
            f"W78 effective width exceeds {STATIC_EFFECTIVE_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        tokens = runtime_tokens(target)
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w77_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w77_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES.get(entry_id, "직접 PC JP 및 PC EN/SC/TC 문맥 대조 후 유지한다."),
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(tokens),
                "runtime_proven": False,
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W78 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W77 Echigo predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W78 Echigo event", event)
    require(after_raw == rebuilt_raw, "W78 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W78 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W78 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W78 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-echigo-quality-wave78-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W77 Steam-PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
            "static_patch_effective_line_limit_px": STATIC_EFFECTIVE_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
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
        "input_w77_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-echigo-quality-wave78-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w77.WORKSTREAM.name,
            "candidate_relative": (w77.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W78 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W78 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W78 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W78 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W78 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W78 candidate audit differs")
    require(
        (root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "W78 candidate manifest differs",
    )
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
        WORKSTREAM / "build_pc_event_echigo_quality_wave78_v1.py",
        WORKSTREAM / "test_pc_event_echigo_quality_wave78_v1.py",
    ):
        require(path.is_file(), f"W78 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W78 trailing whitespace: {path.name}:{number}")


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
