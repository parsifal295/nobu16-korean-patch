#!/usr/bin/env python3
"""Build the private W93 Mōri Motonari event-quality candidate from W92.

The workstream consumes exactly the verified W92 candidate and uses direct PC
JP/EN/SC/TC resources only as read-only translation witnesses.  Its output is
private to this workstream's ``tmp`` root; it never writes Steam files, makes
Git changes, or publishes a release.
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

# W92 supplies parsing, packing, control-signature, and direct-PC context
# helpers.  The actual content predecessor is pinned independently below.
W92_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_honnouji_aftermath_quality_wave92_v1"
    / "build_pc_event_honnouji_aftermath_quality_wave92_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_honnouji_aftermath_quality_wave92_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W92_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "31E3CA37B1FBD7C30B3D0C403BBDFB1EB32AB6EE29E20D1D47C909DB830A9FFB",
    "raw_size": 995_712,
    "sha256": "E00438466EA21B3E23D5E690EE9820A943214B40B9846AFEDFABA0E34443F8B5",
    "size": 999_642,
}

# The complete Motonari flower-viewing scene.  5976 closes the previous
# scene, while 6000 begins the separate Sakamoto/Akechi scene.
SCENE_IDS = tuple(range(5_977, 6_000))
CHANGED_IDS = (
    5_978,
    5_979,
    5_982,
    5_983,
    5_984,
    5_985,
    5_986,
    5_987,
    5_988,
    5_989,
    5_992,
    5_995,
    5_996,
    5_997,
    5_999,
)
RETAINED_IDS = (5_977, 5_980, 5_981, 5_990, 5_991, 5_993, 5_994, 5_998)

# Static patch 007 baseline: four semantic lines, original-G1N 48/24
# advances, and a live raw line gate of 960px.  The 30px calculation is
# evidence only and is deliberately not a second layout gate.
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# There are no dynamic name/runtime tokens in this scene.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {}
ROW_RUNTIME_TOKENS: Mapping[int, tuple[str, ...]] = {}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    5978: (
        "예년처럼 꽃놀이 연회가 열리고 있었다.\n"
        "산정의 성에서는 온갖 꽃이 피고\n"
        "또 지는 모습을 한눈에 바라볼 수 있었다."
    ),
    5979: (
        f"연회에는 당주 {E}CA모토나리{E}CZ를 비롯해,\n"
        f"‘모리의 두 강’이라 불린 {E}CA깃카와 모토하루{E}CZ,\n"
        f"{E}CA고바야카와 다카카게{E}CZ도\n"
        "자리했다."
    ),
    5982: "아버님……\n기분이 좋아 보이십니다.",
    5983: f"기분이 좋을 리가 없지, {E}CA다카카게{E}CZ.",
    5984: "잘 들어라, 너희 둘.\n내 목숨도 이제 오래 남지 않은 듯하다……",
    5985: "갑작스러운 말씀이십니다만,\n아버님께서 그렇게 말씀하신다면……",
    5986: "무언가 짐작 가는 일이\n있으시다는 말씀이겠군요……",
    5987: (
        "내 수명조차 헤아리지 못하고서야,\n"
        "어찌 적을 꾀로 이길 수 있겠느냐.\n"
        "그래서 남겨 둘 말이 있다."
    ),
    5988: (
        "너희 둘은 목숨을 걸고\n"
        f"{E}CA데루모토{E}CZ와 {E}CB모리 본가{E}CZ를 받들어\n"
        "지키겠다고 맹세하겠지?"
    ),
    5989: "몇 번이나 맹세했는지도 모르겠습니다만……\n반드시 그렇게 하겠습니다!",
    5992: (
        "자, 연회 자리에서 더 잔소리를 하는 건\n"
        "멋을 모르는 짓이겠지.\n"
        "너희도 마음껏 마셔라……"
    ),
    5995: "올해도 즐거운 꽃놀이를\n맞이할 수 있었구나.",
    5996: "만족스러웠다고는 할 수 없지만……\n그래도 좋은 삶이었다.",
    5997: "‘벗을 얻으니 더욱 기쁜 벚꽃이여,\n어제와는 다른 오늘의 빛깔과 향기여.’\n어떠냐?",
    5999: (
        "온갖 모략을 다하고 전쟁에\n"
        f"날을 보낸 삶이었을지라도, {E}CA모토나리{E}CZ는\n"
        "끝까지 사람 사이의 인연을 소중히 여겼다."
    ),
}

RATIONALES: Mapping[int, str] = {
    5977: "direct PC JP/EN/SC/TC context revalidated; retained",
    5978: "꽃이 피고 또 지는 장면을 보존하고 한국어 의미 단위로 재구성",
    5979: "모리의 두 강이라는 별칭과 두 인물의 병렬 관계를 명확히 복원",
    5980: "direct PC JP/EN/SC/TC context revalidated; retained",
    5981: "direct PC JP/EN/SC/TC context revalidated; retained",
    5982: "ご機嫌麗しゅう의 기분이 좋아 보인다는 뜻을 자연스럽게 복원",
    5983: "아들의 인사에 대한 모토나리의 부정적 응답을 보존",
    5984: "임종을 앞둔 고백의 의미와 호소 어조를 복원",
    5985: "갑작스러운 말이라는 공손한 반응을 보존",
    5986: "무언가 짐작하는 일이 있다는 추측을 자연스럽게 복원",
    5987: "수명을 헤아리는 비유와 후계자에게 남길 말을 보존",
    5988: "데루모토와 모리 본가를 받들겠다는 맹세를 명확히 복원",
    5989: "반복된 맹세와 확고한 답변을 보존",
    5990: "direct PC JP/EN/SC/TC context revalidated; retained",
    5991: "direct PC JP/EN/SC/TC context revalidated; retained",
    5992: "연회에서 잔소리를 멈추고 마음껏 마시라는 전환을 복원",
    5993: "direct PC JP/EN/SC/TC context revalidated; retained",
    5994: "direct PC JP/EN/SC/TC context revalidated; retained",
    5995: "꽃놀이를 맞이할 수 있었던 기쁨을 보존",
    5996: "만족과 좋은 삶이라는 양가적 회고를 보존",
    5997: "色香을 빛깔과 향기로 복원; PC EN의 blossoms aroma도 대조",
    5998: "direct PC JP/EN/SC/TC context revalidated; retained",
    5999: "人の絆을 사람 사이의 인연으로 복원",
}

TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    5978: (888, 720, 936),
    5979: (768, 960, 504, 216),
    5982: (192, 552),
    5983: (768,),
    5984: (456, 912),
    5985: (624, 768),
    5986: (504, 600),
    5987: (768, 768, 600),
    5988: (504, 696, 528),
    5989: (936, 600),
    5992: (888, 504, 528),
    5995: (528, 456),
    5996: (744, 504),
    5997: (768, 864, 168),
    5999: (600, 864, 960),
}

# Pinned from the one-time read-only W93 profile pass against strict W92.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "F308D190B7C8522407F9423AB312C8683F92D52E0E4A411B3F160B8ABF901069",
    "raw_size": 995_832,
    "sha256": "07661E9AF84CB5D67CB7025B8813806525083796578BBE2358046426355C81EC",
    "size": 999_763,
}


class Wave93Error(RuntimeError):
    """Raised when a source, layout, or private candidate drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave93Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave93Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W92_BUILDER.is_file(), f"W92 helper builder missing: {W92_BUILDER}")
w92 = load_module("pc_event_wave92_base_for_wave93", W92_BUILDER)
parse_table = w92.parse_table
core = w92.core
control_signature = w92.control_signature
is_full_width_visible = w92.is_full_width_visible


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
        raise Wave93Error(f"candidate escapes tmp root: {resolved}") from exc
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


def raw_width(display: str) -> int:
    full = sum(1 for character in display if is_full_width_visible(character))
    return full * RAW_FULL_WIDTH_PX + (len(display) - full) * RAW_HALF_WIDTH_PX


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
        require(runtime is None, f"unexpected runtime token in W93 scene: {runtime.group(0) if runtime else ''}")
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
    require(tuple(TARGETS) == CHANGED_IDS, "W93 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W93 retained scope drift")
    require(set(TARGET_RAW_WIDTHS) == set(CHANGED_IDS), "W93 target metrics scope drift")
    require(not SCENE_RUNTIME_RESERVATIONS, "W93 must not define runtime reservations")
    require(not ROW_RUNTIME_TOKENS, "W93 must not define runtime-token rows")
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"unexpected W93 runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W93 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W93 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W93 pinned target widths drift: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W92 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W92 Motonari predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W92_PROFILE, "W92 on-disk event profile drift")
    require(w92.EXPECTED_OUTPUT_PROFILE == EXPECTED_W92_PROFILE, "W92 pinned output profile drift")

    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W92_PROFILE, "W92 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W92_PROFILE, "W92 manifest output profile drift")
    prior_changed = set(audit.get("coverage", {}).get("changed_row_ids", []))
    require(not prior_changed.intersection(SCENE_IDS), "W92 unexpectedly overlaps the W93 scene")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Any] = {}
    profiles: dict[str, Mapping[str, Any]] = {}
    for language, path in w92.DIRECT_CONTEXT_PATHS.items():
        resolved = path.resolve(strict=True)
        parts = {part.casefold() for part in resolved.parts}
        require("switch" not in parts, f"non-PC context source forbidden: {resolved}")
        event = resolved.read_bytes()
        _header, raw, table = parse_table(f"direct PC {language.upper()} W93 context", event)
        source_profile = profile(event, raw)
        require(source_profile == w92.EXPECTED_CONTEXT_PROFILES[language], f"direct PC {language.upper()} profile drift")
        require(len(table.texts) == w92.EXPECTED_CONTEXT_ROW_COUNT, f"direct PC {language.upper()} row count drift")
        tables[language] = table
        profiles[language] = source_profile
    return tables, profiles


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_static_targets()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    contexts, context_profiles = load_direct_contexts()
    require(all(len(before.texts) == len(table.texts) for table in contexts.values()), "event table topology drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = contexts["jp"].texts[entry_id]
        source_en = contexts["en"].texts[entry_id]
        source_sc = contexts["sc"].texts[entry_id]
        source_tc = contexts["tc"].texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(all((current, source_jp, source_en, source_sc, source_tc)), f"empty W93 row: {entry_id}")
        current_signature = control_signature(current)
        source_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == source_signature, f"W92/direct-PC-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W93 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"unexpected W93 runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W93 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W93 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")

        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "direct_pc_en": source_en,
                "direct_pc_sc": source_sc,
                "direct_pc_tc": source_tc,
                "w92_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "direct_pc_en_utf16le_sha256": text_hash(source_en),
                "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
                "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
                "w92_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES[entry_id],
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": [],
                "runtime_reservations": [],
                "runtime_proven": False,
                "control_signature": target_signature,
            }
        )

    require(tuple(sorted(changed)) == CHANGED_IDS, "W93 changed ID scope drift")
    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W92 Motonari predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W93 Motonari event", event)
    require(after_raw == rebuilt_raw, "W93 raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS), "W93 actual event diff scope drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W93 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W93 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-mori-motonari-quality-wave93-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W92 PC Korean candidate plus direct PC JP/EN/SC/TC context",
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
        "input_w92_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-mori-motonari-quality-wave93-manifest.v1",
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
    require(not output.exists(), f"W93 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W93 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W93 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W93 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W93 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W93 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W93 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_mori_motonari_quality_wave93_v1.py",
        WORKSTREAM / "test_pc_event_mori_motonari_quality_wave93_v1.py",
    ):
        require(path.is_file(), f"W93 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W93 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "W93 output profile is not pinned")
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
