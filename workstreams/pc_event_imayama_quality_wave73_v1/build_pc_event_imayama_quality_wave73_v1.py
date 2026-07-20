#!/usr/bin/env python3
"""Build the W73 Imayama event-quality candidate from the W72 predecessor."""

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
W72_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_okehazama_quality_wave72_v1"
    / "build_pc_event_okehazama_quality_wave72_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(5_915, 5_938))
CHANGED_IDS = (5_920, 5_921, 5_923, 5_936, 5_937)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W72_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "EF31CE39405A20B81DD824437A7DF4770741D8C660434A3F7D512A36CE9D587E",
    "raw_size": 991_420,
    "sha256": "AB491AEA7B1C6499027797979563BCA0966AF488CCD306FED6D12D0E4F9C55F2",
    "size": 995_333,
}
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "CDDCD9F37B76F93B06A1D62AA3C1483C0F915FF214E8DBCC62D17B3787799929",
    "raw_size": 991_568,
    "sha256": "1F578E167642BDA264AE57F700A3E3EAD886107CC98970C7AE653F2319202996",
    "size": 995_482,
}

TARGETS: Mapping[int, str] = {
    5920: "\x1bCB류조지\x1bCZ 가문의 당주 \x1bCA다카노부\x1bCZ는\n\x1bCB오토모\x1bCZ와의 전쟁은 결심했지만,\n\x1bCA나오시게\x1bCZ가 제안한 야습에는\n쉽사리 동의하지 못했다.",
    5921: "\x1bCA다카노부\x1bCZ 님, 적군은\n승리를 미리 축하하며\n술을 돌리고 있는 모양입니다.\n지금이야말로 야습의 기회입니다!",
    5923: "급하기에야말로 야습을 해야 합니다!",
    5936: "이마야마 전투에서 승리한 \x1bCB류조지\x1bCZ 가문은\n태세를 정비해 \x1bCB오토모군\x1bCZ에 대한 열세를\n만회했고, 이는 훗날 영토 확장으로\n이어졌다고 전해진다.",
    5937: "\x1bCB류조지\x1bCZ의 비약에는\n냉철하면서도 열정적인 참모\n\x1bCA나베시마 나오시게\x1bCZ의 존재가\n큰 역할을 했음은 두말할 나위 없다.",
}

RATIONALES: Mapping[int, str] = {
    5920: "가문 당주·오토모와의 전쟁·나오시게의 야습 제안 관계를 원문대로 복원",
    5921: "前祝い를 승리를 앞둔 축하로 바로잡고 공손한 보고 어조를 보존",
    5923: "급하기 때문에 야습한다는 인과를 자연스럽게 복원",
    5936: "승리·태세 정비·열세 만회·훗날 영토 확장이라는 원문 정보를 모두 보존",
    5937: "냉철하면서도 열정적인 참모라는 원문 서술을 축약 없이 문장으로 복원",
}


class Wave73Error(RuntimeError):
    """Raised when the W72 predecessor or W73 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave73Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave73Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w72 = load_module("pc_event_wave72_for_wave73", W72_BUILDER)


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
        raise Wave73Error(f"candidate escapes tmp root: {resolved}") from exc
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
        require(runtime is None, f"unexpected runtime token in Imayama scope: {runtime.group(0) if runtime else ''}")
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if w72.is_full_width_visible(character))
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
    reconstructed = w72.prepare(require_output_profile=True)
    require(reconstructed.profile == EXPECTED_W72_PROFILE, "W72 profile drift")
    path = w72.CANDIDATE_ROOT / MSGEV
    require(path.is_file(), f"W72 candidate missing: {path}")
    event = path.read_bytes()
    require(event == reconstructed.event, "W72 private candidate differs from its pinned reconstruction")
    _header, raw, table = w72.w71.w66.w60.parse_table("W72 Imayama predecessor", event)
    require(profile(event, raw) == EXPECTED_W72_PROFILE, "W72 candidate on-disk profile drift")
    return event, table, raw, reconstructed.profile


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, before_raw, predecessor_profile = load_predecessor()
    jp_blob, _jp_profile = w72.w71.w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w72.w71.w66.w60.parse_table("direct PC Japanese event", jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W73 target scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Imayama row: {entry_id}")
        current_signature = w72.w71.w70.control_signature(current)
        jp_signature = w72.w71.w70.control_signature(source_jp)
        target_signature = w72.w71.w70.control_signature(target)
        require(current_signature == jp_signature, f"W72/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W73 control/token drift: {entry_id}")
        w72.assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W73 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W73 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w72_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w72_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "rationale": RATIONALES.get(entry_id, "JP·KO 문맥 및 제어 구조를 재확인해 W72 문자열 유지"),
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W73 changed ID scope drift")

    header, _parsed_raw, _parsed_table = w72.w71.w66.w60.parse_table("W72 Imayama predecessor", before_event)
    rebuilt_raw = w72.w71.w66.w60.core.rebuild_message_table(before, tuple(texts))
    event = w72.w71.w66.w60.core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = w72.w71.w66.w60.parse_table("W73 Imayama event", event)
    require(after_raw == rebuilt_raw, "W73 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W73 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W73 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W73 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-imayama-quality-wave73-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "W72 Steam-PC Korean candidate plus direct PC JP/EN/SC/TC review",
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
            "runtime_reservations": {},
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": [entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS],
        },
        "input_w72_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-imayama-quality-wave73-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w72.WORKSTREAM.name,
            "candidate_relative": (w72.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W73 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W73 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W73 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W73 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W73 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W73 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W73 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_imayama_quality_wave73_v1.py",
        WORKSTREAM / "test_pc_event_imayama_quality_wave73_v1.py",
    ):
        require(path.is_file(), f"W73 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W73 trailing whitespace: {path.name}:{number}")


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
