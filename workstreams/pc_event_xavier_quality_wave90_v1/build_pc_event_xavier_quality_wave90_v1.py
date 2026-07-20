#!/usr/bin/env python3
"""Build the private W90 Xavier-arrival event-quality candidate from W89.

The W90 candidate is intentionally private.  It reads exactly the verified
W89 candidate, uses direct PC JP/EN/SC/TC tables only as read-only review
context, and writes only beneath its own ``tmp`` root.  It never writes the
Steam installation, performs a Git operation, or publishes a release.
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

# W89 contributes only stable table/control helpers.  The content input is
# pinned below and is never inferred from the helper itself.
W89_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_mikatagahara_quality_wave89_v1"
    / "build_pc_event_mikatagahara_quality_wave89_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_mikatagahara_quality_wave89_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W89_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "3213B87A6DF68E4F61180A2A3C9AF0439195D691AE2C588B96E8A240E721DB1A",
    "raw_size": 995_072,
    "sha256": "DAF480D36AE9651D6BE15074085B6FF704EAFC1288FA08AA8BD35A269B0B93AE",
    "size": 999_000,
}

# Direct PC JP is the pinned pre-localization copy.  EN/SC/TC are direct PC
# context witnesses and are read only; they are not translation inputs.
DIRECT_CONTEXT_PATHS: Mapping[str, Path] = {
    "jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
        r"\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
    ),
    "en": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin"),
    "sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin"),
    "tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin"),
}
EXPECTED_CONTEXT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    "jp": {
        "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        "raw_size": 894_800,
        "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "size": 562_226,
    },
    "en": {
        "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
        "raw_size": 1_878_836,
        "sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
        "size": 762_196,
    },
    "sc": {
        "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
        "raw_size": 754_708,
        "sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
        "size": 522_177,
    },
    "tc": {
        "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
        "raw_size": 744_212,
        "sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
        "size": 524_909,
    },
}
EXPECTED_CONTEXT_ROW_COUNT = 17_916

# This is the complete Xavier-arrival scene.  ID 3277 is its location card;
# ID 3286 closes the narration.  ID 3287 begins a separate Nobunaga scene.
SCENE_IDS = tuple(range(3_277, 3_287))
CHANGED_IDS = (3_280, 3_282, 3_285, 3_286)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

# Static patch 007 runtime: four semantic lines at most.  Raw G1N widths use
# 48px full-width and 24px half-width advances; the displayed 30px effective
# value is recorded, not used as a second pass/fail gate.
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    # Source: ``私は道である``.  The quote and prayer are restored without
    # splitting the Korean auxiliary ``나아가야 / 할`` across lines.
    3280: (
        "그리고…… “나는 길이다”라고\n"
        "말씀하신 주여, 저희가 나아갈 길을\n"
        "보여 주소서."
    ),
    # The current wording obscures the meeting with Yajiro and uses an
    # unnatural ``전해 듣고`` construction.  All source content remains.
    3282: (
        "말라카에서 선교하던 중,\n"
        f"일본인 {E}CA야지로{E}CZ를 만나 일본의 존재를\n"
        "알게 되었고, 그곳으로 건너가기를\n"
        "간절히 바랐다."
    ),
    # ``2년여의 체류 기간`` and preaching to both daimyō and commoners are
    # explicit in the direct PC source.
    3285: (
        f"{E}CA하비에르{E}CZ는 {E}CC가고시마{E}CZ에 상륙한 뒤,\n"
        "2년 남짓 머무는 동안 일본 각지를 돌며\n"
        "많은 다이묘와 백성에게 교리를 전했다."
    ),
    3286: "이후 기독교는 더디게나마\n일본 전역으로 퍼져 나갔다……",
}

RATIONALES: Mapping[int, str] = {
    3277: "직접 PC JP/EN/SC/TC 대조 후 지명 카드의 표기와 태그를 유지",
    3278: "직접 PC JP/EN/SC/TC 대조 후 짧은 감탄사의 어조를 유지",
    3279: "직접 PC JP/EN/SC/TC 대조 후 기도의 호칭과 감사 의미를 유지",
    3280: "‘나는 길이다’라는 인용을 복원하고 보조용언이 갈라진 기존 개행을 문맥 단위로 재배치",
    3281: "직접 PC JP/EN/SC/TC 대조 후 예수회 선교사·하비에르 표기를 유지",
    3282: "야지로와의 만남, 일본의 존재 인지, 도항 열망의 인과를 자연스럽게 복원",
    3283: "직접 PC JP/EN/SC/TC 대조 후 동행한 선교사들과 첫 상륙의 의미를 유지",
    3284: "직접 PC JP/EN/SC/TC 대조 후 구원을 전하려는 결의를 유지",
    3285: "2년 남짓의 체류 기간과 다이묘·백성에게 교리를 전한 행적을 명시적으로 복원",
    3286: "점진적 보급의 뜻을 ‘더디게나마’로 자연스럽게 정리",
}

CHANGED_TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    3280: (624, 792, 288),
    3282: (552, 816, 768, 336),
    3285: (768, 888, 888),
    3286: (576, 648),
}

# Pinned from the read-only W90 profile pass against strict W89.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "CF7AAF9F961DB855C52BFD7863EAA6482B830088B5E8A23759191DBC03F21DF8",
    "raw_size": 995_092,
    "sha256": "3D579EA37A68FE18379D961327EBB21BF2AB23E2130C96449539B1970EFC0CB5",
    "size": 999_020,
}


class Wave90Error(RuntimeError):
    """Raised when the strict W89 predecessor or W90 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave90Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave90Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W89_BUILDER.is_file(), f"W89 helper builder missing: {W89_BUILDER}")
w89 = load_module("pc_event_wave89_base_for_wave90", W89_BUILDER)
parse_table = w89.parse_table
core = w89.core
control_signature = w89.control_signature
is_full_width_visible = w89.is_full_width_visible


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
        raise Wave90Error(f"candidate escapes tmp root: {resolved}") from exc
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
        require(runtime is None, f"unexpected W90 runtime token: {runtime.group(0) if runtime else ''}")
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
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W89 candidate file scope drift: {sorted(actual_files)}")

    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W89 Xavier predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W89_PROFILE, "W89 on-disk event profile drift")
    require(w89.EXPECTED_OUTPUT_PROFILE == EXPECTED_W89_PROFILE, "W89 pinned output profile drift")

    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W89_PROFILE, "W89 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W89_PROFILE, "W89 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Any] = {}
    profiles: dict[str, Mapping[str, Any]] = {}
    for language, path in DIRECT_CONTEXT_PATHS.items():
        resolved = path.resolve(strict=True)
        parts = {part.casefold() for part in resolved.parts}
        require("switch" not in parts, f"non-PC context source forbidden: {resolved}")
        event = resolved.read_bytes()
        _header, raw, table = parse_table(f"direct PC {language.upper()} W90 context", event)
        source_profile = profile(event, raw)
        require(source_profile == EXPECTED_CONTEXT_PROFILES[language], f"direct PC {language.upper()} profile drift")
        require(len(table.texts) == EXPECTED_CONTEXT_ROW_COUNT, f"direct PC {language.upper()} row count drift")
        tables[language] = table
        profiles[language] = source_profile
    return tables, profiles


def validate_static_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "W90 target scope drift")
    require(
        tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS,
        "W90 retained scope drift",
    )
    require(set(CHANGED_TARGET_RAW_WIDTHS) == set(CHANGED_IDS), "W90 target metric scope drift")
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"unexpected W90 runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W90 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W90 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            tuple(metric["raw_g1n_width_px"] for metric in metrics) == CHANGED_TARGET_RAW_WIDTHS[entry_id],
            f"W90 pinned target widths drift: {entry_id}",
        )


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
        require(all((current, source_jp, source_en, source_sc, source_tc)), f"empty W90 row: {entry_id}")

        current_signature = control_signature(current)
        source_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == source_signature, f"W89/direct-PC-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W90 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"unexpected W90 runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W90 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W90 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
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
                "w89_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "direct_pc_en_utf16le_sha256": text_hash(source_en),
                "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
                "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
                "w89_current_ko_utf16le_sha256": text_hash(current),
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

    require(tuple(sorted(changed)) == CHANGED_IDS, "W90 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W89 Xavier predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W90 Xavier event", event)
    require(after_raw == rebuilt_raw, "W90 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W90 actual event diff scope drift",
    )

    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W90 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W90 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-xavier-quality-wave90-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W89 PC Korean candidate plus direct PC JP/EN/SC/TC context",
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
        "input_w89_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-xavier-quality-wave90-manifest.v1",
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
    require(not output.exists(), f"W90 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W90 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W90 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W90 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W90 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W90 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W90 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_xavier_quality_wave90_v1.py",
        WORKSTREAM / "test_pc_event_xavier_quality_wave90_v1.py",
    ):
        require(path.is_file(), f"W90 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W90 trailing whitespace: {path.name}:{number}")


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
