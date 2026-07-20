#!/usr/bin/env python3
"""Build the W85 Honnouji-successors event candidate from strict on-disk W84."""

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

MSGEV = "MSG_PK/JP/msgev.bin"
W84_WORKSTREAM_NAME = "pc_event_koshu_campaign_quality_wave84_v1"
W84_BUILDER = REPO / "workstreams" / W84_WORKSTREAM_NAME / "build_pc_event_koshu_campaign_quality_wave84_v1.py"
EXPECTED_W84_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "5D4A4C7CA96421E7BEE761A241A5B3252A48DEC720BE1993477BA7D2EC05C586",
    "raw_size": 994_296,
    "sha256": "7CA04F8EAE44EC27202268896F3D1CAA4BB4C90CEC6591C037ECCEC2A62D122B",
    "size": 998_221,
}

SCENE_IDS = tuple(range(7_793, 7_816))
CHANGED_IDS = (
    7_794, 7_796, 7_797, 7_800, 7_801, 7_802, 7_803, 7_806, 7_808, 7_810,
    7_811, 7_812, 7_813, 7_814,
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

# Pinned after the one read-only profile pass and before the only candidate write.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "C5AD43F00B08B8F1D52DC041EC1D00C628C528A889C2A924BB895F4316A1BC87",
    "raw_size": 994_628,
    "sha256": "6E42E3394EE77C4DA440092FB67175CD31DDDF0263F50D284581934631312BFC",
    "size": 998_554,
}
# This scene has no runtime substitution tokens; keep that assertion explicit.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    7794: (
        f"{E}CA노부나가{E}CZ를 죽인 {E}CA미쓰히데{E}CZ가\n"
        "쉽사리 천하인이 될 리는 없었다.\n"
        "주군의 원수를 갚으려는 가신들도 있었다…"
    ),
    7796: (
        f"{E}CA오다{E}CZ의 가독을 이을 {E}CA노부타다{E}CZ마저\n"
        f"{E}CC교{E}CZ의 불길 속에서 목숨을 잃었으니,\n"
        f"앞으로 {E}CB오다 가문{E}CZ에 파란은 불가피했다."
    ),
    7797: (
        f"간신히 {E}CA노부타다{E}CZ 다음의 계승권을\n"
        f"주장할 수 있는 차남 {E}CA노부카쓰{E}CZ는,\n"
        f"그 기량으로 {E}CB오다 가문{E}CZ을 이어도\n"
        "천하인의 자리를 잇기는 어려울 것이다…"
    ),
    7800: (
        f"{E}CB오다가{E}CZ에서 출세가로 이름나,\n"
        f"주군의 두터운 신임 아래 {E}CC기나이{E}CZ를 맡고도\n"
        "끝내 주군을 친 「계략과 책모의 사내」."
    ),
    7801: "한편 「자신을 위장하는 데 빈틈이 없다」,\n「배신과 비밀 회합을 즐긴다」는\n평도 있었다.",
    7802: "또한 「잠든 늑대 같은 용모」라며\n그 위험성을 지적받기도 한,\n난세가 낳은 효웅이기도 했다.",
    7803: (
        "그 결단이…\n"
        "틀렸다고는 생각하고 싶지 않다.\n"
        f"하지만 {E}CA노부나가{E}CZ 님의 패업은\n"
        "누군가가 아니라 내가 이어야 한다!"
    ),
    7806: (
        "주군을 친 것만으로 끝나지는 않는다.\n"
        f"{E}CA미쓰히데{E}CZ의 다음 도전이 지금\n"
        "막 시작되려 하고 있었다―"
    ),
    7808: (
        f"일찍부터 {E}CA노부나가{E}CZ를 따라\n"
        f"수많은 무공을 세워 「돌격 {E}CA시바타{E}CZ」\n"
        f"「귀신 {E}CA시바타{E}CZ」라 불렸다."
    ),
    7810: (
        "한편 축성의 재능도 있어,\n"
        f"잇코잇키가 날뛰던 {E}CC에치젠{E}CZ을 평정하고\n"
        f"{E}CC기타노쇼성{E}CZ을 쌓는 등 자신을 신뢰한\n"
        f"{E}CA노부나가{E}CZ의 기대에 부응했다."
    ),
    7811: (
        f"주군이… {E}CA노부나가{E}CZ 님이\n"
        "살해당하셨다고!? 말도 안 된다!\n"
        f"…이놈 {E}CA미쓰히데{E}CZ!\n"
        "결코 용서치 않겠다!"
    ),
    7812: (
        "하지만 먼저 생각할 것은\n"
        f"{E}CB오다 가문{E}CZ의 앞날이다.\n"
        f"내가 {E}CB오다 가문{E}CZ을 떠받쳐야 한다.\n"
        "하지만 나는 싸움밖에 모르는 서투른 사내…"
    ),
    7813: (
        "아니… 그래도 내가 할 수 있는 일은 있다!\n"
        "돌아가신 주군의 뜻을 이을 자는 나뿐이다!\n"
        "천하의 평온으로 가는 길을\n"
        "끊어서는 안 된다!"
    ),
    7814: (
        "어쩌면 수라의 길이 될지도 모른다…\n"
        "하지만… 모두 부디 따라와 다오!\n"
        f"이 {E}CA가쓰이에{E}CZ가 벌이는 싸움은\n"
        "필사의 싸움이다. 모두, 쳐라!"
    ),
}

RATIONALES: Mapping[int, str] = {
    7794: "미쓰히데가 천하인이 되기 어려운 이유와 주군의 원수를 갚으려는 가신들의 존재를 복원",
    7796: "노부타다의 죽음과 오다 가문의 장래에 파란이 불가피하다는 인과를 자연스럽게 재배치",
    7797: "노부타다 다음 계승권·차남 노부카쓰·그의 기량이라는 누락된 판단 근거를 복원",
    7800: "오다 가문 출세가, 두터운 신임 아래 기나이 위임, 주군 시해와 책략가 평을 모두 복원",
    7801: "자기 위장과 배신·비밀 회합을 즐긴다는 평을 자연스러운 한국어로 바로잡음",
    7802: "잠든 늑대 같은 용모와 위험성, 난세가 낳은 효웅이라는 묘사를 복원",
    7803: "결단에 대한 자문과 노부나가의 패업을 자신이 이어야 한다는 결의를 복원",
    7806: "주군 시해가 끝이 아니라 다음 도전의 시작이라는 시제를 자연스럽게 복원",
    7808: "돌격 시바타·귀신 시바타라는 두 별칭을 의미 단위로 보존",
    7810: "잇코잇키가 날뛰던 에치젠 평정, 기타노쇼성 축성, 노부나가의 신임을 모두 복원",
    7811: "주군 피살 소식의 충격과 미쓰히데를 용서하지 않겠다는 분노를 자연스럽게 복원",
    7812: "오다 가문의 앞날·자신의 책임·싸움밖에 모르는 서투름을 원문 흐름대로 복원",
    7813: "天下静謐을 천하의 평온으로 바로잡고 그 길을 끊지 않겠다는 결의를 복원",
    7814: "수라의 길·부하들의 동행 요청·가쓰이에의 필사전·돌격 명령을 비문 없이 복원",
}


class Wave85Error(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave85Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave85Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W84_BUILDER.is_file(), f"W84 builder missing: {W84_BUILDER}")
w84 = load_module("pc_event_wave84_for_wave85", W84_BUILDER)
parse_table = w84.parse_table
core = w84.core
control_signature = w84.control_signature
is_full_width_visible = w84.is_full_width_visible


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
        raise Wave85Error(f"candidate escapes tmp root: {resolved}") from exc
    return resolved


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {"sha256": sha256(event), "size": len(event), "raw_sha256": sha256(raw), "raw_size": len(raw)}


def runtime_tokens(value: str) -> tuple[str, ...]:
    return tuple(RUNTIME_RE.findall(value))


def assert_no_break_inside_tag(value: str) -> None:
    opened = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            if token == "\x1bCZ":
                require(opened, "unpaired ESC close")
                opened = False
            else:
                require(not opened, "nested ESC colour span")
                opened = True
            cursor += 3
            continue
        require(not (opened and value[cursor] in "\r\n"), "line break inside colour tag")
        cursor += 1
    require(not opened, "unterminated ESC colour span")


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
        require(runtime is None, f"unexpected W85 runtime token: {runtime.group(0) if runtime else ''}")
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
    root = w84.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W84 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W84 Honnouji-successors predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W84_PROFILE, "W84 on-disk event profile drift")
    require(w84.EXPECTED_OUTPUT_PROFILE == EXPECTED_W84_PROFILE, "W84 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W84_PROFILE, "W84 audit output profile drift")
    require(manifest["output"] == EXPECTED_W84_PROFILE, "W84 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_jp() -> Any:
    return w84.w82.w81.w80.load_direct_jp()


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W85 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W85 retained scope drift")
    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty W85 row: {entry_id}")
        current_signature = control_signature(current)
        require(current_signature == control_signature(source_jp), f"W84/direct-JP control drift: {entry_id}")
        require(control_signature(target) == current_signature, f"W85 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        tokens = runtime_tokens(target)
        require(not tokens, f"unexpected W85 runtime token: {entry_id}: {tokens}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W85 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W85 raw width exceeds 960px: {entry_id}")
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w84_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w84_current_ko_utf16le_sha256": text_hash(current),
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
                "control_signature": control_signature(target),
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W85 changed ID scope drift")
    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W84 Honnouji-successors predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W85 Honnouji-successors event", event)
    require(after_raw == rebuilt_raw, "W85 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W85 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W85 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W85 output profile drift")
    audit = {
        "schema": "nobu16.kr.pc-event-honnouji-successors-quality-wave85-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W84 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
        "input_w84_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-honnouji-successors-quality-wave85-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w84.WORKSTREAM.name,
            "candidate_relative": (w84.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W85 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W85 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W85 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W85 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W85 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W85 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W85 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_honnouji_successors_quality_wave85_v1.py",
        WORKSTREAM / "test_pc_event_honnouji_successors_quality_wave85_v1.py",
    ):
        require(path.is_file(), f"W85 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W85 trailing whitespace: {path.name}:{number}")


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
