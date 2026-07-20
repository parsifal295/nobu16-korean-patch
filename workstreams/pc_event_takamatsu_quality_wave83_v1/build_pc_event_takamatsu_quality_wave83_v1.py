#!/usr/bin/env python3
"""Build the W83 Takamatsu water-siege event candidate from strict W82."""

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

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(7_752, 7_779))
CHANGED_IDS = (7_753, 7_754, 7_761, 7_762, 7_768, 7_770, 7_772, 7_774, 7_776)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W82_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "844FC26539B16C076A597E77EC872FFD6270F19F65DC069D6F8A8BA79FB2FE51",
    "raw_size": 994_028,
    "sha256": "0CB2A885FB3316D8009DEBDCB619AC4540FF30D07F6EA8CFB43F67586104FEC5",
    "size": 997_952,
}

# Pinned from the one read-only W83 profile pass before the only candidate write.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "2EA33030A96FBAD95AC36236682FD45E750F7F035AAD52A5EECC90862F4C81B8",
    "raw_size": 994_192,
    "sha256": "90A9314C575703326A0374B58A1C2E5E0D7BF9250B81C8EC2D553E7E8F36846E",
    "size": 998_116,
}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    7753: (
        "병량 보급이 끊긴 것도 뼈아팠지만,\n"
        f"무엇보다 {E}CB모리 가문{E}CZ의 원군이\n"
        "접근할 수 없게 된 것이 큰 문제였다."
    ),
    7754: (
        f"{E}CA오다 노부나가{E}CZ가 {E}CC교토{E}CZ에서\n"
        "원군으로 달려온다는 소문이 퍼지자,\n"
        f"{E}CB모리 가문{E}CZ에서는 강화 분위기가\n"
        "무르익고 있었다…"
    ),
    7761: (
        f"{E}CA오다 노부나가{E}CZ가 이 {E}CC다카마쓰{E}CZ로\n"
        "향하고 있습니다. 전쟁이 길어지면\n"
        f"{E}CB오다{E}CZ와 {E}CB모리{E}CZ가 정면으로 충돌해,\n"
        f"대합전이 되어 {E}CB모리{E}CZ는 멸망합니다."
    ),
    7762: (
        f"{E}CA히데요시{E}CZ 공께서는 지금 강화에 응한다면,\n"
        f"{E}CA무네하루{E}CZ 공의 목과 약간의 영토를\n"
        "대가로 화친을 맺겠다고 하셨습니다."
    ),
    7768: (
        "헛소리 마라, 땡중 놈.\n"
        f"어서 돌아가 {E}CA히데요시{E}CZ에게\n"
        "내가 할복하겠다고 전해라!"
    ),
    7770: (
        f"{E}CA에케이{E}CZ, {E}CA히데요시{E}CZ… 똑똑히 보아 두어라!\n"
        f"이 {E}CA무네하루{E}CZ의 진정한 무사다운 죽음을!"
    ),
    7772: (
        "양군 장병이 지켜보는 가운데\n"
        f"{E}CA시미즈 무네하루{E}CZ는 당당히 할복했다.\n"
        "예법에 따른 듯한 일련의 모습은\n"
        f"훌륭하여 {E}CA히데요시{E}CZ마저 감복시켰다."
    ),
    7774: (
        "아닙니다, 소승의 공 따위는…\n"
        f"이번 일은 올곧은 {E}CA시미즈 무네하루{E}CZ 님의\n"
        "무사도가 양가의 싸움을\n"
        "멈추었을 뿐이옵니다."
    ),
    7776: (
        "몹시 서두르시는 모양이구려…\n"
        "가미가타에서 무슨 일이라도 생겼소이까?"
    ),
}

RATIONALES: Mapping[int, str] = {
    7753: "後詰를 원군으로 바로잡고 모리 가문의 원군이 접근할 수 없던 핵심을 복원",
    7754: "노부나가의 교토발 원군 도착 소문과 모리 가문의 강화 분위기 고조를 복원",
    7761: "오다·모리 정면충돌이 대합전으로 번져 모리 멸망으로 이어지는 인과를 복원",
    7762: "무네하루의 목과 약간의 영토를 대가로 한 화친 조건의 조사와 연결을 교정",
    7768: "할복의 주체가 무네하루 자신임을 명시해 히데요시에게 할복을 명하는 독해를 제거",
    7770: "真の武士の死に様를 자연스러운 한국어인 진정한 무사다운 죽음으로 복원",
    7772: "작법을 따른 듯한 훌륭한 일련의 모습을 복원해 시미즈 무네하루의 할복 장면을 명료화",
    7774: "문장은 유지하고 소승의 겸양과 무네하루의 사도가 양가 전투를 멈춘 인과를 의미 단위로 재배치",
    7776: "ずいぶんと、お急ぎ를 어지간히가 아닌 몹시 서두르는 뜻으로 교정",
}


class Wave83Error(RuntimeError):
    """Raised when the strict W82 predecessor or W83 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave83Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave83Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w82 = load_module("pc_event_wave82_for_wave83", W82_BUILDER)
parse_table = w82.parse_table
core = w82.core
control_signature = w82.control_signature
is_full_width_visible = w82.is_full_width_visible


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
        raise Wave83Error(f"candidate escapes tmp root: {resolved}") from exc
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
        require(runtime is None, f"W83 must not contain runtime token: {runtime.group(0) if runtime else ''}")
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
    root = w82.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W82 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W82 Takamatsu predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W82_PROFILE, "W82 on-disk event profile drift")
    require(w82.EXPECTED_OUTPUT_PROFILE == EXPECTED_W82_PROFILE, "W82 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W82_PROFILE, "W82 audit output profile drift")
    require(manifest["output"] == EXPECTED_W82_PROFILE, "W82 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_jp() -> Any:
    return w82.w81.w80.load_direct_jp()


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W83 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W83 retained scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Takamatsu row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W82/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W83 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        tokens = runtime_tokens(target)
        require(not tokens, f"unexpected W83 runtime token: {entry_id}: {tokens}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W83 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W83 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w82_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w82_current_ko_utf16le_sha256": text_hash(current),
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
    require(tuple(sorted(changed)) == CHANGED_IDS, "W83 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W82 Takamatsu predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W83 Takamatsu event", event)
    require(after_raw == rebuilt_raw, "W83 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W83 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W83 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W83 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-takamatsu-quality-wave83-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W82 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
            "runtime_reservations": {},
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
        "input_w82_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-takamatsu-quality-wave83-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w82.WORKSTREAM.name,
            "candidate_relative": (w82.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W83 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W83 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W83 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W83 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W83 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W83 candidate audit differs")
    require(
        (root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "W83 candidate manifest differs",
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
        WORKSTREAM / "build_pc_event_takamatsu_quality_wave83_v1.py",
        WORKSTREAM / "test_pc_event_takamatsu_quality_wave83_v1.py",
    ):
        require(path.is_file(), f"W83 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W83 trailing whitespace: {path.name}:{number}")


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
