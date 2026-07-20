#!/usr/bin/env python3
"""Build the W79 Otate event-quality candidate from strict on-disk W78."""

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
W78_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_echigo_quality_wave78_v1"
    / "build_pc_event_echigo_quality_wave78_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(7_214, 7_239))
CHANGED_IDS = (
    7_214,
    7_215,
    7_216,
    7_217,
    7_219,
    7_221,
    7_222,
    7_226,
    7_228,
    7_234,
    7_236,
    7_237,
    7_238,
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

# This is the exact W78 candidate already present on disk.  W79 never falls
# back to a Steam installation, a live game resource, or any earlier wave.
EXPECTED_W78_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "9FA155B0CFFA17CC9BD3DCAC376779CB212A4DB9E2928AF0800181BE6257AD2B",
    "raw_size": 993_244,
    "sha256": "4C1C40CFB55F4DA111D7D33471EB6AB8CB84134006E7F5F8E659FFDEA302B357",
    "size": 997_165,
}

# Pinned after the single in-memory W79 profile pass and before candidate build.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "6A04C331F21F01D29402153D2DDD30F26678049DA9B25E804A6EA9FFE96A27DE",
    "raw_size": 993_488,
    "sha256": "0740190230C2C2771CB4FAEEB9231E4DC0FE1A4127784A3FA84C511D1153804A",
    "size": 997_409,
}

# These table values are scene-bounded layout reservations only.  They are
# deliberately not claimed as observations of a running-game substitution.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[b1448]": {
        "display": "나가오 가게토라",
        "source_slot_id": 1448,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W78 event slot 1448; conservative historical-name reservation",
    },
    "[b1672]": {
        "display": "히구치 가네쓰구",
        "source_slot_id": 1672,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W78 event slot 1672; scene-bounded full-name reservation",
    },
    "[bs1672]": {
        "display": "히구치",
        "source_slot_id": 1672,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W78 event slot 1672; scene-bounded surname reservation",
    },
}

TARGETS: Mapping[int, str] = {
    7214: (
        "\x1bCA[b1448]\x1bCZ의 죽음으로\n"
        "\x1bCB우에스기가\x1bCZ에서 후계자 다툼인\n"
        "「오타테의 난」이 일어났다."
    ),
    7215: (
        "서로 다투는 이는 두 사람―\n"
        "\x1bCA나가오 마사카게\x1bCZ의 아들\n"
        "\x1bCA우에스기 가게카쓰\x1bCZ와 \x1bCA호조 우지야스\x1bCZ의 아들\n"
        "\x1bCA우에스기 가게토라\x1bCZ였다."
    ),
    7216: (
        "\x1bCB나가오가\x1bCZ 시절부터 \x1bCB우에스기\x1bCZ를\n"
        "대대로 섬겨 온 가신들과\n"
        "\x1bCC에치고\x1bCZ 국내 유력자 다수는\n"
        "\x1bCA우에스기 가게카쓰\x1bCZ를 지지했다…"
    ),
    7217: (
        "\x1bCC간토\x1bCZ에 연고가 깊은 이들과\n"
        "친가인 \x1bCB호조가\x1bCZ 및 동맹국 다수는\n"
        "\x1bCA우에스기 가게토라\x1bCZ를 지지했다."
    ),
    7219: (
        "아뢰옵니다!\n"
        "\x1bCC에치고\x1bCZ의 \x1bCA[b1672]\x1bCZ 님께서 보낸\n"
        "사자가 와 있사옵니다."
    ),
    7221: (
        "그것이… \x1bCB우에스기\x1bCZ 가문의 일에\n"
        "간섭하지 말라고 합니다."
    ),
    7222: (
        "흥, 무슨 말을 하나 했더니…\n"
        "내 아내는 \x1bCB호조\x1bCZ 출신이고,\n"
        "\x1bCB호조\x1bCZ는 내 동맹이다. \x1bCA우지마사\x1bCZ 공에게\n"
        "\x1bCA가게토라\x1bCZ를 도와 달라는 부탁을 받았다."
    ),
    7226: (
        "(아니, 기다려… 침착히 생각해야 해!\n"
        "이만한 거금을 내놓을 수 있다는 건,\n"
        "적어도 금고는 \x1bCA가게카쓰\x1bCZ가\n"
        "장악했다는 뜻인가…)"
    ),
    7228: (
        "(하지만 \x1bCA가게토라\x1bCZ를 이기게 해서야\n"
        "무슨 소용인가?\n"
        "\x1bCB다케다\x1bCZ 주변이 모두 \x1bCB호조\x1bCZ의 세력이 되고,\n"
        "우리도 \x1bCB호조\x1bCZ에 굴복하게 될지 모른다…)"
    ),
    7234: (
        "여기서는 \x1bCA가게카쓰\x1bCZ와 \x1bCA가게토라\x1bCZ 사이를\n"
        "중재해, \x1bCB호조\x1bCZ와 \x1bCB우에스기\x1bCZ 양쪽 모두에게\n"
        "은혜를 베풀어 신세를 지워 두는 것이다."
    ),
    7236: (
        "하지만 \x1bCA가쓰요리\x1bCZ의 계획은\n"
        "보기 좋게 빗나갔다.\n"
        "\x1bCB다케다 가문\x1bCZ의 애매한 태도에 불신을 품은\n"
        "\x1bCB호조 가문\x1bCZ은 \x1bCB다케다\x1bCZ와의 절연을 선언했다…"
    ),
    7237: (
        "당황한 \x1bCA가쓰요리\x1bCZ는\n"
        "\x1bCB호조가\x1bCZ의 공격에 대비하려\n"
        "여동생 \x1bCA기쿠히메\x1bCZ를 \x1bCA가게카쓰\x1bCZ의 정실로 삼아\n"
        "\x1bCB우에스기가\x1bCZ와 혼인 동맹을 맺었다."
    ),
    7238: (
        "하지만 내란으로 황폐해진 \x1bCB우에스기가\x1bCZ는\n"
        "예전의 힘을 잃어, \x1bCB다케다가\x1bCZ는 거의\n"
        "단독으로 \x1bCB호조가\x1bCZ를 맞아 싸우게 되었다."
    ),
}

RATIONALES: Mapping[int, str] = {
    7214: "후계자 다툼의 문장 완결과 조사를 교정한다.",
    7215: "서로 다투는 두 사람과 두 번째 부자 관계를 복원한다.",
    7216: "譜代의 대대로 섬긴 가신과 에치고 유력자 다수를 복원한다.",
    7217: "남성에게 잘못 쓴 친정을 친가로, 동맹 제국을 동맹국으로 교정한다.",
    7219: "사절의 발신 주체를 자연스러운 한국어로 복원한다.",
    7221: "口出し無用를 간섭하지 말라는 뜻으로 명확히 한다.",
    7222: "내 벗 오역을 동맹으로 고치고 우지마사의 요청 관계를 복원한다.",
    7226: "거금을 낼 수 있다는 사실에서 금고 장악을 추론하는 의문형을 복원한다.",
    7228: "가게토라 승리의 무용함과 호조 세력권 위험을 복원한다.",
    7234: "恩を売る의 정치적 의미를 은혜를 베풀어 신세를 지우는 말로 복원한다.",
    7236: "호조가 다케다의 애매한 태도를 불신해 절연을 선언한 주체와 인과를 복원한다.",
    7237: "호조의 공격에 대비한 이유와 가게카쓰의 정실이라는 관계를 복원한다.",
    7238: "우에스기 쇠퇴와 다케다의 사실상 단독 항전을 자연스럽게 정리한다.",
}


class Wave79Error(RuntimeError):
    """Raised when the strict W78 predecessor or W79 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave79Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave79Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w78 = load_module("pc_event_wave78_for_wave79", W78_BUILDER)
parse_table = w78.parse_table
core = w78.core
control_signature = w78.control_signature
is_full_width_visible = w78.is_full_width_visible


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
        raise Wave79Error(f"candidate escapes tmp root: {resolved}") from exc
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
            require(reservation is not None, f"missing W79 scene reservation: {token}")
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
    root = w78.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W78 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W78 Otate predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W78_PROFILE, "W78 on-disk event profile drift")
    require(w78.EXPECTED_OUTPUT_PROFILE == EXPECTED_W78_PROFILE, "W78 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W78_PROFILE, "W78 audit output profile drift")
    require(manifest["output"] == EXPECTED_W78_PROFILE, "W78 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_jp() -> Any:
    return w78.load_direct_jp()


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W79 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W79 retained scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Otate row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W78/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W79 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W79 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W79 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            not any(metric["over_static_patch_912px"] for metric in metrics),
            f"W79 effective width exceeds {STATIC_EFFECTIVE_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        tokens = runtime_tokens(target)
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w78_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w78_current_ko_utf16le_sha256": text_hash(current),
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
    require(tuple(sorted(changed)) == CHANGED_IDS, "W79 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W78 Otate predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W79 Otate event", event)
    require(after_raw == rebuilt_raw, "W79 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W79 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W79 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W79 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-otate-quality-wave79-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W78 Steam-PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
        "input_w78_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-otate-quality-wave79-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w78.WORKSTREAM.name,
            "candidate_relative": (w78.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W79 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W79 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W79 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W79 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W79 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W79 candidate audit differs")
    require(
        (root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "W79 candidate manifest differs",
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
        WORKSTREAM / "build_pc_event_otate_quality_wave79_v1.py",
        WORKSTREAM / "test_pc_event_otate_quality_wave79_v1.py",
    ):
        require(path.is_file(), f"W79 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W79 trailing whitespace: {path.name}:{number}")


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
