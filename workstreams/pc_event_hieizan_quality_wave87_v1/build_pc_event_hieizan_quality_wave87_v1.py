#!/usr/bin/env python3
"""Build the W87 Hiei-zan event-quality candidate from strict on-disk W86."""

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

# Use only stable table/control helpers from W80. The actual predecessor is
# fixed below to W86, never W80.
W80_BUILDER = REPO / "workstreams" / "pc_event_naomasa_quality_wave80_v1" / "build_pc_event_naomasa_quality_wave80_v1.py"
MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_kanegasaki_quality_wave86_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W86_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "9CA0764A3DB51F63F972883D6AC3DE0DBC557074C231F3C70DB3ED787ECF97BC",
    "raw_size": 994_676,
    "sha256": "AAFD78AF7299FC0CB64985BECA7E938C69EBC45779E2541AC12358FFB9CFD0F6",
    "size": 998_602,
}

SCENE_IDS = tuple(range(3_245, 3_261))
CHANGED_IDS = (
    3_246, 3_247, 3_248, 3_249, 3_251, 3_252, 3_253, 3_256, 3_257, 3_258,
    3_259, 3_260,
)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# Pinned from the one no-write profile pass against strict W86.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "1056F2EDB6661D9815F807D32FC743FD254390961E9114C5C86031EB76D03C59",
    "raw_size": 994_764,
    "sha256": "76E176F3917A6D549CE8B8748D1172C145FF6D6F2E119A89B72FBB3887CCF293",
    "size": 998_690,
}
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    3246: (
        "누구나 칭송했다.\n"
        f"{E}CA전교대사{E}CZ 이래의 호국을 위한\n"
        "대도량이자, 여러 종파의\n"
        "숭앙을 받는 불문의 중심이라고."
    ),
    3247: (
        "겉으로는 그랬을 것이다.\n"
        "하지만 실제로 엔랴쿠지는 예부터\n"
        "신위를 등에 업고 강소를 거듭하며\n"
        "권익을 넓혀 왔다."
    ),
    3248: "승병의 무력과 전국의 장원을 함께\n거느린 중세 최대급의 권문이었다.",
    3249: (
        f"그 권문이 {E}CA노부나가{E}CZ에게 등을 돌린\n"
        f"{E}CA아자이{E}CZ·{E}CA아사쿠라{E}CZ 무리와 손을 잡았으니,\n"
        "용서할 수 없었다."
    ),
    3251: (
        "무사의 질서를 따르려 하지 않는 그들은\n"
        f"{E}CA노부나가{E}CZ가 그리는 천하의 설계도에\n"
        "필요 없는 존재였다."
    ),
    3252: (
        "하지만…… 여러 나라가 숭앙하는 절을\n"
        f"불태우면, 비난은 {E}CA노부나가{E}CZ에게\n"
        "빗발칠 터였다."
    ),
    3253: "가신들은 주군의 폭거를\n멈추라고 간언했다.",
    3256: (
        "뜻밖에도 주명을 과감히 받든 이는\n"
        "단 한 명이었다.\n"
        "옛 권위를 누구보다 중시하던\n"
        f"{E}CA아케치 미쓰히데{E}CZ였다."
    ),
    3257: (
        "주군을 귀신이라 부르게 하느니,\n"
        "내가 스스로 귀신이 되리라.\n"
        f"각오를 품은 {E}CA미쓰히데{E}CZ는\n"
        "산문에 불을 질렀다."
    ),
    3258: "산 위의 가람은 홍련의 불길에 휩싸이고,\n달아나는 승려와 속인도\n포위군에게 베였다.",
    3259: (
        f"아비규환의 지옥도도 {E}CA노부나가{E}CZ에게는\n"
        "중세라는 유물과의 결별에\n"
        "지나지 않았다."
    ),
    3260: (
        f"아이러니하게도 이 공으로 {E}CA미쓰히데{E}CZ는\n"
        f"{E}CA노부나가{E}CZ 가신 가운데 처음 성주가 되어,\n"
        f"불탄 터인 {E}CC사카모토{E}CZ에\n"
        "성을 쌓도록 허락받았다……"
    ),
}

RATIONALES: Mapping[int, str] = {
    3246: "전교대사 이래의 호국 대도량·여러 종파의 숭앙·불문 중추를 복원",
    3247: "겉모습과 실상, 신위를 배경으로 한 강소와 권익 확대를 복원",
    3248: "僧兵·전국 장원·중세 최대급 권문이라는 역사 용어를 복원",
    3249: "앞 행의 권문과 노부나가에게 등을 돌린 아자이·아사쿠라의 결탁을 복원",
    3251: "무사의 질서와 노부나가가 그리는 천하 설계도라는 현재형 서술을 복원",
    3252: "절 소각의 조건과 노부나가에게 쏟아질 비난을 의미 단위로 재배치",
    3253: "가신들이 폭거 자체가 아니라 폭거를 멈추라고 간언한 목적어 관계를 복원",
    3256: "유일하게 과감히 주명을 받은 아케치 미쓰히데와 표기를 복원",
    3257: "주군을 귀신이라 부르게 하기보다 자신이 귀신이 되겠다는 결의를 복원",
    3258: "홍련의 불길, 달아나는 승려·속인이 포위군에게 베인 사실을 복원",
    3259: "아비규환의 지옥도가 중세와의 결별에 지나지 않았다는 문법과 의미를 복원",
    3260: "아이러니한 공, 최초 성주, 불탄 사카모토 터의 축성 허가를 복원",
}

TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    3246: (384, 648, 552, 720),
    3247: (552, 744, 768, 408),
    3248: (768, 768),
    3249: (768, 888, 408),
    3251: (888, 792, 456),
    3252: (816, 696, 336),
    3253: (528, 432),
    3256: (768, 360, 648, 480),
    3257: (720, 624, 528, 456),
    3258: (912, 528, 432),
    3259: (816, 576, 336),
    3260: (840, 912, 480, 576),
}


class Wave87Error(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave87Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave87Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W80_BUILDER.is_file(), f"W80 builder missing: {W80_BUILDER}")
base = load_module("pc_event_wave80_base_for_wave87", W80_BUILDER)
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
        raise Wave87Error(f"candidate escapes tmp root: {resolved}") from exc
    return resolved


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {"sha256": sha256(event), "size": len(event), "raw_sha256": sha256(raw), "raw_size": len(raw)}


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
        require(runtime is None, f"unexpected W87 runtime token: {runtime.group(0) if runtime else ''}")
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


def validate_static_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "W87 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W87 retained scope drift")
    require(set(TARGET_RAW_WIDTHS) == set(CHANGED_IDS), "W87 target metric scope drift")
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"unexpected W87 runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W87 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W87 raw width exceeds 960px: {entry_id}")
        require(
            tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id],
            f"W87 pinned target widths drift: {entry_id}",
        )


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W86 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W86 Hiei-zan predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W86_PROFILE, "W86 on-disk event profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W86_PROFILE, "W86 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W86_PROFILE, "W86 manifest output profile drift")
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
        require(bool(current) and bool(source_jp), f"empty W87 row: {entry_id}")
        current_signature = control_signature(current)
        require(current_signature == control_signature(source_jp), f"W86/direct-JP control drift: {entry_id}")
        require(control_signature(target) == current_signature, f"W87 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W87 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W87 raw width exceeds 960px: {entry_id}")
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w86_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w86_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES.get(entry_id, "직접 PC JP 및 PC EN/SC/TC 문맥 대조 후 유지"),
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(runtime_tokens(target)),
                "runtime_proven": False,
                "control_signature": control_signature(target),
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W87 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W86 Hiei-zan predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W87 Hiei-zan event", event)
    require(after_raw == rebuilt_raw, "W87 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W87 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W87 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W87 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-hieizan-quality-wave87-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W86 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
        "input_w86_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-hieizan-quality-wave87-manifest.v1",
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
    require(not output.exists(), f"W87 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W87 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W87 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W87 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W87 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W87 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W87 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_hieizan_quality_wave87_v1.py",
        WORKSTREAM / "test_pc_event_hieizan_quality_wave87_v1.py",
    ):
        require(path.is_file(), f"W87 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W87 trailing whitespace: {path.name}:{number}")


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
