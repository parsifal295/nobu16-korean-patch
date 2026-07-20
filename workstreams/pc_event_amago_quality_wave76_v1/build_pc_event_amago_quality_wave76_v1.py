#!/usr/bin/env python3
"""Build the W76 Amago/Shikanosuke event-quality candidate from on-disk W75."""

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
W75_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_toyotomi_quality_wave75_v1"
    / "build_pc_event_toyotomi_quality_wave75_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(7_199, 7_214))
CHANGED_IDS = (7_199, 7_200, 7_201, 7_202, 7_203, 7_205, 7_207, 7_211, 7_212, 7_213)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
STATIC_EFFECTIVE_LINE_LIMIT_PX = 912
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W75_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "11A0266615A38366EAE3DAC6845F334D62BF19C31D34622DCB9286A804F05408",
    "raw_size": 991_928,
    "sha256": "E0531856273B55AAA8E53AC2899372307E83595F4BE645237E05A680E305EF50",
    "size": 995_843,
}
# This was pinned from the strict W75 in-memory reconstruction before the one
# permitted candidate write.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "34CEF870EA769ED4D0C89E002A795353AED92C79670FDCF729475A25D82D7949",
    "raw_size": 992_124,
    "sha256": "C4BB65199D1D8FAF7236A12B0BE07A875FE02D6764F8890B69E1423BCAB9F8A6",
    "size": 996_040,
}

TARGETS: Mapping[int, str] = {
    7199: (
        "그러나 \x1bCA시카노스케\x1bCZ의 진의는\n"
        "원수 \x1bCA깃카와 모토하루\x1bCZ에 대한\n"
        "복수에 있었다…"
    ),
    7200: (
        "(\x1bCA가쓰히사\x1bCZ 님이 세상을 떠난 지금,\n"
        "\x1bCB아마고\x1bCZ 가문의 재흥은 불가능하다.\n"
        "하지만 주군의 가문을 두 번이나 멸한\n"
        "\x1bCA모토하루\x1bCZ만은 결코 용서할 수 없다!)"
    ),
    7201: (
        "(사관하겠다며 방심시켜 두고,\n"
        "기회를 보아 \x1bCA모토하루\x1bCZ에게 접근해\n"
        "내 칼로 반드시 베어 죽여 보이겠다…!)"
    ),
    7202: (
        "하지만 \x1bCA시카노스케\x1bCZ는 잊고 있었다.\n"
        "\x1bCB모리\x1bCZ는 어디까지나 모략을 일삼는\n"
        "가문이었다는 것을."
    ),
    7203: (
        "당주 \x1bCA모리 데루모토\x1bCZ를 알현하러 호송되던\n"
        "도중, \x1bCC다카하시강\x1bCZ 나루에 이르렀을 때\n"
        "\x1bCA시카노스케\x1bCZ는 \x1bCA모토하루\x1bCZ 휘하\n"
        "무사들에게 습격당했다."
    ),
    7205: "으, 원통하도다…!",
    7207: (
        "그토록 진지하게 맞서 온 적에게…\n"
        "사관까지 권해 놓고 목숨을 빼앗다니,\n"
        "비열하다는 말을 들어도\n"
        "할 말이 없겠구나…"
    ),
    7211: (
        "칠난팔고 끝에 숙원이 이루어지기를\n"
        "달에 빌며 불요불굴의 싸움을 이어 온\n"
        "용장의 이야기는 씁쓸한 여운을 남긴 채\n"
        "막을 내렸다."
    ),
    7212: (
        "결국 \x1bCB아마고 가문\x1bCZ 재흥도,\n"
        "\x1bCB모리\x1bCZ에 대한 복수도 이루지 못한\n"
        "\x1bCA시카노스케\x1bCZ는 원통한 마음만 남긴 채\n"
        "세상을 떠났다…"
    ),
    7213: (
        "하지만 그의 불굴의 정신은\n"
        "후세 사람들에게 큰 감동을 주었고,\n"
        "그 충절의 마음은 지금도\n"
        "많은 이들에게 칭송받고 있다…"
    ),
}

RATIONALES: Mapping[int, str] = {
    7199: "원수와 인명 사이의 어색한 분절을 절·대상·결말 단위로 재배치했다.",
    7200: "가쓰히사 사후, 아마고 재흥 불가, 주가를 두 번 멸한 모토하루라는 원문의 강조를 복원했다.",
    7201: "仕官する를 벼슬을 사는 일로 오독한 표현을 사관하여 방심시킨 뒤 죽인다는 뜻으로 바로잡았다.",
    7202: "謀略の家를 자연스러운 한국어인 모략을 일삼는 가문으로 옮기고 의미 단위로 줄을 나눴다.",
    7203: "호송 중이라는 원문의 정보를 복원하고 사건의 시간·장소·가해자를 문맥 단위로 분리했다.",
    7205: "일본어의 죽어가는 신음 む、를 사색의 음이 아닌 으,로 교정했다.",
    7207: "진지하게 맞서 온 적을 쫓은 적으로 바꾼 오독과 비열하다 해도 할 말 없다는 수용 의미를 복원했다.",
    7211: "칠난팔고 끝 숙원을 빈다는 조사 누락을 바로잡고 숙원 성취·불요불굴·씁쓸한 결말을 보존했다.",
    7212: "모리에 대한 복수와 무념만 남기고 세상을 떠난 결말을 자연스럽게 복원했다.",
    7213: "후세 사람이라는 수혜자, 충절, 현재까지 이어지는 칭송을 모두 보존했다.",
}


class Wave76Error(RuntimeError):
    """Raised when the W75 predecessor or W76 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave76Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave76Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w75 = load_module("pc_event_wave75_for_wave76", W75_BUILDER)


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
        raise Wave76Error(f"candidate escapes tmp root: {resolved}") from exc
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
        require(runtime is None, f"unexpected runtime token in Amago scene: {runtime.group(0) if runtime else ''}")
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if w75.w74.w73.w72.is_full_width_visible(character))
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
    reconstructed = w75.prepare(require_output_profile=True)
    require(reconstructed.profile == EXPECTED_W75_PROFILE, "W75 reconstruction profile drift")
    path = w75.CANDIDATE_ROOT / MSGEV
    require(path.is_file(), f"W75 candidate missing: {path}")
    event = path.read_bytes()
    require(event == reconstructed.event, "W75 private candidate differs from its pinned reconstruction")
    _header, raw, table = w75.w74.w73.w72.w71.w66.w60.parse_table("W75 Amago predecessor", event)
    require(profile(event, raw) == EXPECTED_W75_PROFILE, "W75 candidate on-disk profile drift")
    return event, table, raw, reconstructed.profile


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    jp_blob, _jp_profile = w75.w74.w73.w72.w71.w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w75.w74.w73.w72.w71.w66.w60.parse_table("direct PC Japanese event", jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W76 target scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Amago row: {entry_id}")
        current_signature = w75.w74.w73.w72.w71.w70.control_signature(current)
        jp_signature = w75.w74.w73.w72.w71.w70.control_signature(source_jp)
        target_signature = w75.w74.w73.w72.w71.w70.control_signature(target)
        require(current_signature == jp_signature, f"W75/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W76 control/token drift: {entry_id}")
        w75.w74.w73.w72.assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W76 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W76 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            not any(metric["over_static_patch_912px"] for metric in metrics),
            f"W76 effective width exceeds {STATIC_EFFECTIVE_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w75_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w75_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "rationale": RATIONALES.get(entry_id, "W75 한국어를 그대로 유지했다."),
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W76 changed ID scope drift")

    header, _parsed_raw, _parsed_table = w75.w74.w73.w72.w71.w66.w60.parse_table("W75 Amago predecessor", before_event)
    rebuilt_raw = w75.w74.w73.w72.w71.w66.w60.core.rebuild_message_table(before, tuple(texts))
    event = w75.w74.w73.w72.w71.w66.w60.core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = w75.w74.w73.w72.w71.w66.w60.parse_table("W76 Amago event", event)
    require(after_raw == rebuilt_raw, "W76 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W76 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W76 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W76 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-amago-quality-wave76-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "on-disk W75 Steam-PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": [entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS],
        },
        "input_w75_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-amago-quality-wave76-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w75.WORKSTREAM.name,
            "candidate_relative": (w75.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W76 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W76 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W76 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W76 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W76 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W76 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W76 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_amago_quality_wave76_v1.py",
        WORKSTREAM / "test_pc_event_amago_quality_wave76_v1.py",
    ):
        require(path.is_file(), f"W76 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W76 trailing whitespace: {path.name}:{number}")


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
