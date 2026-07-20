#!/usr/bin/env python3
"""Build the W75 Toyotomi-event quality candidate from on-disk W74."""

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
W74_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_honnouji_quality_wave74_v1"
    / "build_pc_event_honnouji_quality_wave74_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(8_484, 8_521))
CHANGED_IDS = (
    8_491,
    8_496,
    8_498,
    8_499,
    8_503,
    8_506,
    8_508,
    8_510,
    8_512,
    8_513,
    8_514,
    8_515,
    8_516,
    8_519,
    8_520,
)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
STATIC_EFFECTIVE_LINE_LIMIT_PX = 912
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W74_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "9940CD998E31B83B67AC8FB012B60625B34CC44BCDED8A3952DF49D11C0B8F03",
    "raw_size": 991_668,
    "sha256": "A31DAB5EF47BCCC0D41653C38F30E1D83E91860A4D3D9D314EE85695D9C56DC2",
    "size": 995_582,
}
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "11A0266615A38366EAE3DAC6845F334D62BF19C31D34622DCB9286A804F05408",
    "raw_size": 991_928,
    "sha256": "E0531856273B55AAA8E53AC2899372307E83595F4BE645237E05A680E305EF50",
    "size": 995_843,
}

# These are conservative capacity bounds only, not a global assertion that a
# token always renders to this particular historical alias.  They are at least
# as long as the aliases needed for this scene's name-bearing tokens.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, str] = {
    "[bs754]": "기노시타",
    "[b1871]": "마쓰다이라 모토야스",
    "[bm1871]": "마쓰다이라 모토야스",
    "[bs1871]": "마쓰다이라",
}

TARGETS: Mapping[int, str] = {
    8491: (
        "\x1bCA가즈마사\x1bCZ는 \x1bCB[bs754]가\x1bCZ로 옮긴 뒤,\n"
        "눈에 띄는 활약은 거의 없었으나\n"
        "\x1bCB[bs754]\x1bCZ와 \x1bCB[bs1871]\x1bCZ 사이의 화합에\n"
        "마음을 쏟았다고 한다."
    ),
    8496: "오히려 늘 무리한 말을 꺼내,\n뒤처리에는 \x1bCA히데나가\x1bCZ만\n불려 나가곤 했다.",
    8498: "어째서 간파쿠입니까?\n불과 얼마 전 쇼군 임관을 거절하신\n것 아니었습니까?",
    8499: "나는 무가 출신이 아니니 말이다.\n쇼군이 된다 한들 무가의 흉내를 내는 데\n지나지 않으리라 여겼다.",
    8503: "뭐, 다음 간파쿠가 나올 때까지의\n임시방편이라는 것이지.",
    8506: (
        "이리하여 간파쿠 자리에 오른\n"
        "\x1bCA히데요시\x1bCZ는, 다음으로 천황께\n"
        "새 성씨, \x1bCA도요토미\x1bCZ를 하사받는다."
    ),
    8508: (
        "간파쿠 지위가 세습제가 되고,\n"
        "이리하여 \x1bCB도요토미가\x1bCZ는 천하를 다스리는\n"
        "가문이 되는 것이다."
    ),
    8510: (
        "겐페이토키쓰의 명가 위에\n"
        "\x1bCB도요토미 가문\x1bCZ이 군림하는,\n"
        "\x1bCA히데요시\x1bCZ가 만든 새 시대의 시작이었다."
    ),
    8512: (
        "\x1bCA[b1871]\x1bCZ도 이에 어쩔 수 없이\n"
        "따랐으나, 응한 것은 정전에 불과했고,\n"
        "\x1bCB[bs754]\x1bCZ와 \x1bCB[bs1871]\x1bCZ 양가의 긴장은\n"
        "아직도 계속되고 있었다."
    ),
    8513: (
        "천하인을 목표로 한 \x1bCA히데요시\x1bCZ는\n"
        "거대한 존재감을 유지하는 \x1bCB[bs1871]가\x1bCZ를\n"
        "그대로 둘 수 없었다. 수단을 가리지 않고\n"
        "\x1bCB[bm1871]\x1bCZ 포섭을 꾀했다."
    ),
    8514: "주군, \x1bCA히데요시\x1bCZ가 또\n보통이 아닌 분을 보내왔습니다…",
    8515: (
        "뭐냐, 나 원…\n"
        "필요 없다는데도 자기 누이를\n"
        "내 아내로 삼으라며 보낸 지\n"
        "얼마 되지도 않았잖나. 이번엔 누구냐?"
    ),
    8516: "\x1bCA히데요시\x1bCZ 공의 모친이옵니다.\n인질로 보내신 듯하옵니다…",
    8519: (
        "어쩔 수 없군…\n"
        "원숭이 님과의 참을성 겨루기도\n"
        "이쯤에서 끝낼 때인가.\n"
        "이렇게 되어서는 도망쳐 숨을 수도 없겠지."
    ),
    8520: (
        "친족을 거듭 보낸 \x1bCA히데요시\x1bCZ에게 질렸는지,\n"
        "\x1bCA히데요시\x1bCZ의 성의에 꺾인 것인지,\n"
        "\x1bCA[bm1871]\x1bCZ는 마침내\n"
        "\x1bCA히데요시\x1bCZ에게 신종하기로 결심했다."
    ),
}

RATIONALES: Mapping[int, str] = {
    8491: "이적 뒤 거의 눈에 띄는 활약은 없었지만 양가의 화합에 마음을 쏟았다는 원문을 복원",
    8496: "무리한 일을 벌였다는 뜻이 아닌 무리한 말을 꺼냈다는 원문으로 교정",
    8498: "막 쇼군 임관을 거절한 직후라는 의문문 구조를 복원",
    8499: "무가 출신이 아니라 쇼군이 되어도 무가를 흉내 내는 데 그친다는 뜻을 자연스럽게 복원",
    8503: "다음 간파쿠 전까지의 임시방편이라는 繋ぎ의 뜻을 복원",
    8506: "새 성씨라는 의미 단위를 보존하도록 수동 개행을 재배치",
    8508: "간파쿠 지위 자체가 세습제가 되는 문법적 주체를 명확히 함",
    8510: "도요토미가가 군림하는 히데요시의 새 시대라는 수식 관계를 명확히 함",
    8512: "정전에만 응했으며 양가의 긴장이 계속됐다는 원문 정보를 복원",
    8513: "천하인 목표·도쿠가와가의 존재감·수단을 가리지 않은 포섭을 축약 없이 복원",
    8514: "とんでもないお人을 비하하는 자가 아닌 보통이 아닌 인물로 교정",
    8515: "누이를 아내로 삼으라며 보낸 직후라는 문장 구조와 문맥 개행을 교정",
    8516: "히데요시의 모친이라는 직접적인 존칭 서술로 정리",
    8519: "이쯤이 끝일 때라는 문법 오류를 이쯤에서 끝낼 때로 교정",
    8520: "친족을 거듭 보낸 행위와 성의라는 두 원인 및 신종 결심을 완문으로 복원",
}


class Wave75Error(RuntimeError):
    """Raised when a W74 predecessor or W75 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave75Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave75Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w74 = load_module("pc_event_wave74_for_wave75", W74_BUILDER)


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
        raise Wave75Error(f"candidate escapes tmp root: {resolved}") from exc
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
        if runtime is not None:
            token = runtime.group(0)
            reservation = SCENE_RUNTIME_RESERVATIONS.get(token)
            require(reservation is not None, f"no conservative W75 reservation for {token}")
            rendered.append(reservation)
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
        full = sum(1 for character in display if w74.w73.w72.is_full_width_visible(character))
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
    reconstructed = w74.prepare(require_output_profile=True)
    require(reconstructed.profile == EXPECTED_W74_PROFILE, "W74 reconstruction profile drift")
    path = w74.CANDIDATE_ROOT / MSGEV
    require(path.is_file(), f"W74 candidate missing: {path}")
    event = path.read_bytes()
    require(event == reconstructed.event, "W74 private candidate differs from its pinned reconstruction")
    _header, raw, table = w74.w73.w72.w71.w66.w60.parse_table("W74 Toyotomi predecessor", event)
    require(profile(event, raw) == EXPECTED_W74_PROFILE, "W74 candidate on-disk profile drift")
    return event, table, raw, reconstructed.profile


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    jp_blob, _jp_profile = w74.w73.w72.w71.w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w74.w73.w72.w71.w66.w60.parse_table("direct PC Japanese event", jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W75 target scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Toyotomi row: {entry_id}")
        current_signature = w74.w73.w72.w71.w70.control_signature(current)
        jp_signature = w74.w73.w72.w71.w70.control_signature(source_jp)
        target_signature = w74.w73.w72.w71.w70.control_signature(target)
        require(current_signature == jp_signature, f"W74/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W75 control/token drift: {entry_id}")
        w74.w73.w72.assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W75 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W75 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w74_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w74_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "rationale": RATIONALES.get(entry_id, "W74 문자열을 직접 PC 일본어와 제어 구조에 대조해 유지"),
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W75 changed ID scope drift")

    header, _parsed_raw, _parsed_table = w74.w73.w72.w71.w66.w60.parse_table("W74 Toyotomi predecessor", before_event)
    rebuilt_raw = w74.w73.w72.w71.w66.w60.core.rebuild_message_table(before, tuple(texts))
    event = w74.w73.w72.w71.w66.w60.core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = w74.w73.w72.w71.w66.w60.parse_table("W75 Toyotomi event", event)
    require(after_raw == rebuilt_raw, "W75 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W75 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W75 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W75 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-toyotomi-quality-wave75-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "on-disk W74 Steam-PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
            "runtime_reservations_kind": "conservative capacity bounds, not global display assertions",
            "runtime_reservations": dict(SCENE_RUNTIME_RESERVATIONS),
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": [entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS],
        },
        "input_w74_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-toyotomi-quality-wave75-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w74.WORKSTREAM.name,
            "candidate_relative": (w74.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W75 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W75 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W75 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W75 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W75 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W75 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W75 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_toyotomi_quality_wave75_v1.py",
        WORKSTREAM / "test_pc_event_toyotomi_quality_wave75_v1.py",
    ):
        require(path.is_file(), f"W75 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W75 trailing whitespace: {path.name}:{number}")


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
