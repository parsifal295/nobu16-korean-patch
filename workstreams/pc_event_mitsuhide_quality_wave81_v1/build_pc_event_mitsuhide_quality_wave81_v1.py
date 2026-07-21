#!/usr/bin/env python3
"""Build the W81 Mitsuhide early-life event candidate from strict on-disk W80."""

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
W80_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_naomasa_quality_wave80_v1"
    / "build_pc_event_naomasa_quality_wave80_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(7_651, 7_675))
CHANGED_IDS = (7_652, 7_661, 7_664, 7_665, 7_667, 7_668, 7_669, 7_671, 7_672, 7_673)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W80_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "1F70E64756B4EF214734245D85A93328753EAA8B47DA247F915F6707C0EE5EA5",
    "raw_size": 993_952,
    "sha256": "0553580CE8F5A0274D6DD792A23F9D3BBD48960820F0931C920962B6E039B08C",
    "size": 997_875,
}

# Pinned from the single read-only W81 profile pass before the only candidate write.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "E9D196E3DF6A086C9A2E9704CE89A8BD1701EB088D9AF795D65A4055CA729522",
    "raw_size": 994_000,
    "sha256": "0B18991E5B9DA4BF7D94A5583C2F868DB69292AD12CFD6B48AF86318AEAFB516",
    "size": 997_923,
}

# This scene has no runtime substitution tokens.  Keep the empty mapping
# explicit so a later token cannot be silently measured as literal text.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    7652: (
        f"{E}CC미노{E}CZ 출신으로 {E}CB사이토 가문{E}CZ을 섬겼다는 설,\n"
        f"{E}CA노히메{E}CZ의 연고자였다는 설,\n"
        f"{E}CB아사쿠라 가문{E}CZ의 가신이었다는 설…\n"
        "어느 것도 확실하지 않다."
    ),
    7661: "흥… 너도 나와 함께 지내다 보니\n빈정거림을 배우――",
    7664: (
        "나무를 깎아 만든 상이로군, 불상인가?\n"
        f"{E}CA히데미쓰{E}CZ, 보아라. 나는 유감스럽게도\n"
        "신불에는 어두워서 말이다."
    ),
    7665: "이것은 대흑천상이옵니다.",
    7667: "천 명… 겨우 그뿐인가.\n그렇다면 필요 없구나.",
    7668: "앗…! 아무것도 버리지 않아도\n되지 않사옵니까.",
    7669: (
        "천 명의 우두머리 따위,\n"
        "범부라도 될 수 있다.\n"
        "우리 무사가 출세를 빌어야 할\n"
        "신은 아니리라."
    ),
    7671: "큰 뜻을 품은 자는 신불에 기대지 않는다.\n그런 말씀이시지요?",
    7672: "흥… 뭐, 그런 셈이다.\n우선은 주군을 찾아야 하지만 말이다.",
    7673: f"{E}CA아케치 미쓰히데{E}CZ는\n늘 마음속에 높은 이상을 품고 있었다.",
}

RATIONALES: Mapping[int, str] = {
    7652: "미노·사이토, 노히메, 아사쿠라의 세 가설과 미확정이라는 결론을 모두 복원",
    7661: "조건형을 함께 지낸 결과라는 원문의 인과로 바로잡고 의미 단위로 재개행",
    7664: "生憎의 뜻과 다른 공교롭게도를 유감스럽게도로 바로잡음",
    7665: "大黒像의 신격을 한국어 불교 용어 대흑천상으로 명확화",
    7667: "말줄임표 뒤 띄어쓰기를 바로잡음",
    7668: "버리지/않아도의 어절 분리를 제거",
    7669: "범부라도/될의 어절 분리를 제거하고 네 의미 단위로 재배치",
    7671: "확인 질문을 자연스러운 존대 표현으로 바로잡음",
    7672: "감탄사와 이어지는 발화를 하나의 의미 단위로 결합",
    7673: "직역투 자신 안에를 자연스러운 마음속에로 바로잡음",
}


class Wave81Error(RuntimeError):
    """Raised when the strict W80 predecessor or W81 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave81Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave81Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w80 = load_module("pc_event_wave80_for_wave81", W80_BUILDER)
parse_table = w80.parse_table
core = w80.core
control_signature = w80.control_signature
is_full_width_visible = w80.is_full_width_visible


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
        raise Wave81Error(f"candidate escapes tmp root: {resolved}") from exc
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
            require(reservation is not None, f"unexpected W81 runtime token: {token}")
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
    root = w80.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W80 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W80 Mitsuhide predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W80_PROFILE, "W80 on-disk event profile drift")
    require(w80.EXPECTED_OUTPUT_PROFILE == EXPECTED_W80_PROFILE, "W80 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W80_PROFILE, "W80 audit output profile drift")
    require(manifest["output"] == EXPECTED_W80_PROFILE, "W80 manifest output profile drift")
    return event, table, raw, predecessor_profile


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = w80.load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W81 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W81 retained scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Mitsuhide row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W80/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W81 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        tokens = runtime_tokens(target)
        require(not tokens, f"unexpected W81 runtime token(s): {entry_id}: {tokens}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W81 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W81 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w80_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w80_current_ko_utf16le_sha256": text_hash(current),
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
    require(tuple(sorted(changed)) == CHANGED_IDS, "W81 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W80 Mitsuhide predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W81 Mitsuhide event", event)
    require(after_raw == rebuilt_raw, "W81 raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS), "W81 actual event diff scope drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W81 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W81 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-mitsuhide-quality-wave81-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W80 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
        "input_w80_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-mitsuhide-quality-wave81-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w80.WORKSTREAM.name,
            "candidate_relative": (w80.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W81 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W81 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W81 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W81 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W81 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W81 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W81 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_mitsuhide_quality_wave81_v1.py",
        WORKSTREAM / "test_pc_event_mitsuhide_quality_wave81_v1.py",
    ):
        require(path.is_file(), f"W81 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W81 trailing whitespace: {path.name}:{number}")


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
