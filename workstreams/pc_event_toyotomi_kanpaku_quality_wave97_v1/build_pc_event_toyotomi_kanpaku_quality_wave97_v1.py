#!/usr/bin/env python3
"""Build the private W97 Toyotomi-kanpaku scene-quality candidate from W96.

Only the pinned on-disk W96 private candidate supplies Korean input.  Every
row in the independent 8492–8510 scene is rechecked against direct PC
JP/EN/SC/TC text.  This builder writes only its own private candidate and has
no Steam, Git, network, or release operation.
"""

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

W96_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_sanada_ishikawa_quality_wave96_v1"
    / "build_pc_event_sanada_ishikawa_quality_wave96_v1.py"
)
MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_sanada_ishikawa_quality_wave96_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W96_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "293D16C91520E455AA4FEB6539B00A7B1D4F207D66ADDCFF87F6EB9715524A94",
    "raw_size": 996_228,
    "sha256": "0FF01B159898CA5E9C1004CE030FE8B6B42B2618DD85821F6DE7AADA43CCCBD8",
    "size": 1_000_160,
}

SCENE_IDS = tuple(range(8_492, 8_511))
CHANGED_IDS = (8492, 8496, 8497, 8498, 8500, 8501, 8503, 8506, 8508, 8509, 8510)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# These are the prepared, unshortened Korean targets.  Existing colour spans
# remain in their original order and no line break is placed inside a span.
TARGETS: Mapping[int, str] = {
    8492: "\x1bCA히데나가\x1bCZ, 나는 관백이 될 것이다!",
    8496: (
        "오히려 늘 무리한 요구를 하고,\n"
        "그 뒷수습에는 \x1bCA히데나가\x1bCZ만\n"
        "끌려 나가곤 했다."
    ),
    8497: (
        "하지만 이제까지보다 더한 무리한 요구에,\n"
        "\x1bCA히데나가\x1bCZ마저 어이없음을\n"
        "감추지 못했다."
    ),
    8498: "어째서 관백이십니까?\n불과 얼마 전 쇼군 임관을 거절하신\n것 아니었습니까?",
    8500: "그렇다고 관백이라니… 아니,\n그러고 보니 지금 관백 자리는\n비어 있었지요.",
    8501: (
        "음, \x1bCA니조\x1bCZ와 \x1bCA고노에\x1bCZ가 서로 다투고 있네.\n"
        "서로 양보하지 않으니,\n"
        "내게까지 이야기가 온 것이지."
    ),
    8503: "뭐, 다음 관백이 정해질 때까지의\n임시방편이라는 것이지.",
    8506: (
        "이렇게 관백 자리에 오른 \x1bCA히데요시\x1bCZ는,\n"
        "이어 천황에게서 새 성씨,\n"
        "\x1bCA도요토미\x1bCZ를 하사받는다."
    ),
    8508: (
        "관백직은 그대로 세습제가 되었고,\n"
        "이로써 \x1bCB도요토미가\x1bCZ는 천하를\n"
        "다스리는 가문이 되었다."
    ),
    8509: "칠백 년 동안 \x1bCB후지와라씨\x1bCZ가 독점해 온\n섭정·관백 체제는 여기서 막을 내린다.",
    8510: (
        "겐페이토키쓰의 명문가들 위에\n"
        "\x1bCB도요토미 가문\x1bCZ이 군림하는,\n"
        "\x1bCA히데요시\x1bCZ가 만든 새 시대가 시작되었다."
    ),
}
RATIONALES: Mapping[int, str] = {
    8492: "같은 장면 안의 관백 표기를 한국어 역사 용어로 일관되게 정리했다.",
    8496: "무리한 요구와 뒷수습에 끌려 나가는 히데나가의 역할을 명확히 했다.",
    8497: "평소보다 더한 요구에 히데나가마저 어이없어한 뉘앙스를 복원했다.",
    8498: "관백·쇼군 임관을 둘러싼 질문을 자연스러운 한국어로 정리했다.",
    8500: "관백 자리가 비었다는 깨달음과 호흡을 자연스럽게 정리했다.",
    8501: "니조와 고노에의 다툼, 양보하지 않아 제안이 온 인과를 명확히 했다.",
    8503: "다음 관백이 정해질 때까지의 임시 역할이라는 의미를 정확히 옮겼다.",
    8506: "히데요시가 천황에게서 도요토미라는 새 성씨를 받은 관계를 바로잡았다.",
    8508: "관백직 세습과 도요토미가의 천하 지배라는 결과를 명확히 했다.",
    8509: "후지와라씨가 독점한 섭정·관백 체제의 종결을 자연스럽게 옮겼다.",
    8510: "겐페이토키쓰 명문가 위에 도요토미가가 군림하는 새 시대를 문법적으로 정리했다.",
}

# This scene contains no runtime-name token.  It is deliberately recorded as
# an empty scene-local reservation map rather than inheriting any other scene's
# assumptions; runtime proof remains false.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {}

# Pinned after deterministic profile/layout calculation before private build.
TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] | None = {
    8492: (768,),
    8493: (144,),
    8494: (792,),
    8495: (888, 504),
    8496: (696, 576, 408),
    8497: (936, 552, 336),
    8498: (480, 792, 384),
    8499: (744, 912, 552),
    8500: (624, 672, 336),
    8501: (888, 504, 672),
    8502: (768, 792),
    8503: (744, 528),
    8504: (648, 456),
    8505: (408, 528),
    8506: (840, 576, 528),
    8507: (768, 864),
    8508: (768, 624, 552),
    8509: (840, 864),
    8510: (672, 600, 888),
}
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "E1810DEA757C5179A8C5631251656CDA83C36425C0699BE95650A6CCFBE4C11F",
    "raw_size": 996_240,
    "sha256": "C5451B9BA726C8D06743E86D8F6ED320E052F6B6065A37D550DE4ACCE3CF4810",
    "size": 1_000_172,
}


class Wave97Error(RuntimeError):
    """Raised when strict source, direct context, or candidate output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave97Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave97Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W96_BUILDER.is_file(), f"W96 helper builder missing: {W96_BUILDER}")
w96 = load_module("pc_event_wave96_base_for_wave97", W96_BUILDER)
parse_table = w96.parse_table
core = w96.core
control_signature = w96.control_signature
is_full_width_visible = w96.is_full_width_visible


@dataclass(frozen=True)
class Bundle:
    event: bytes
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
        raise Wave97Error(f"candidate escapes tmp root: {resolved}") from exc
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
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token in layout: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        if runtime is not None:
            raise Wave97Error(f"W97 scene unexpectedly contains runtime token: {runtime.group(0)}")
        character = value[cursor]
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if is_full_width_visible(character))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        rows.append(
            {
                "line_number": number,
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
    require(SCENE_IDS == tuple(range(8492, 8511)), "W97 scene scope drift")
    require(len(SCENE_IDS) == 19, "W97 scene length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W97 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W97 retained scope drift")
    require(len(RETAINED_IDS) == 8, "W97 retained count drift")
    require(SCENE_RUNTIME_RESERVATIONS == {}, "W97 must not inherit a runtime reservation")
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"W97 target unexpectedly has runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W97 target line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W97 target raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if TARGET_RAW_WIDTHS is not None:
            require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W97 target widths drift: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W96 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W96 predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W96_PROFILE, "W96 on-disk event profile drift")
    require(w96.EXPECTED_OUTPUT_PROFILE == EXPECTED_W96_PROFILE, "W96 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W96_PROFILE, "W96 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W96_PROFILE, "W96 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    loader = getattr(w96, "load_direct_contexts", None)
    require(callable(loader), "W96 direct-PC context loader missing")
    tables, profiles = loader()
    require(tuple(sorted(tables)) == ("en", "jp", "sc", "tc"), "direct PC context language scope drift")
    require(tuple(sorted(profiles)) == ("en", "jp", "sc", "tc"), "direct PC context profile scope drift")
    return tables, profiles


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_static_targets()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    contexts, context_profiles = load_direct_contexts()
    require(all(len(before.texts) == len(table.texts) for table in contexts.values()), "event table topology drift")

    texts = list(before.texts)
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = contexts["jp"].texts[entry_id]
        source_en = contexts["en"].texts[entry_id]
        source_sc = contexts["sc"].texts[entry_id]
        source_tc = contexts["tc"].texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(all((current, source_jp, source_en, source_sc, source_tc, target)), f"empty W97 row: {entry_id}")
        current_signature = control_signature(current)
        require(current_signature == control_signature(source_jp), f"W96/direct-PC-JP control drift: {entry_id}")
        require(control_signature(target) == current_signature, f"W97 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"W97 runtime token unexpected: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W97 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W97 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if TARGET_RAW_WIDTHS is not None:
            require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W97 measured widths drift: {entry_id}")
        changed = entry_id in CHANGED_IDS
        require((target != current) == changed, f"W97 expected change disposition drift: {entry_id}")
        if changed:
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "direct_pc_en": source_en,
                "direct_pc_sc": source_sc,
                "direct_pc_tc": source_tc,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "direct_pc_en_utf16le_sha256": text_hash(source_en),
                "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
                "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
                "w96_current_ko": current,
                "target_ko": target,
                "w96_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": changed,
                "review_disposition": "semantic_correction" if changed else "retained_after_semantic_lf_audit",
                "rationale": RATIONALES[entry_id] if changed else "직접 PC 4언어 대조와 의미·수동 개행 검사를 통과하여 유지.",
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "lf_only_reflow": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": [],
                "runtime_reservations": [],
                "runtime_proven": False,
                "control_signature": control_signature(target),
            }
        )

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W96 predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W97 Toyotomi-kanpaku event", event)
    require(after_raw == rebuilt_raw, "W97 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W97 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W97 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W97 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-toyotomi-kanpaku-quality-wave97-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W96 PC Korean candidate plus direct PC JP/EN/SC/TC context",
            "strict_input_only": PREDECESSOR_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_sentence_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "network_operation_performed": False,
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
        "input_w96_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-toyotomi-kanpaku-quality-wave97-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
        },
        "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
        "changed_row_ids": list(CHANGED_IDS),
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W97 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W97 candidate staging exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True)
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
    require(root.is_dir(), f"W97 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W97 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W97 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W97 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W97 candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "runtime_proven": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_toyotomi_kanpaku_quality_wave97_v1.py",
        WORKSTREAM / "test_pc_event_toyotomi_kanpaku_quality_wave97_v1.py",
    ):
        require(path.is_file(), f"W97 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W97 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "W97 output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": list(CHANGED_IDS), "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
