#!/usr/bin/env python3
"""Build the private W94 Ōtomo/Tachibana event-quality candidate from W93.

Only the self-contained succession-and-father's-remains scene is changed.
The builder consumes the exact W93 candidate, audits every displayed line with
scene-local dynamic-name reservations, and writes only under this workstream's
private ``tmp`` root.
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

W93_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_mori_motonari_quality_wave93_v1"
    / "build_pc_event_mori_motonari_quality_wave93_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_mori_motonari_quality_wave93_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W93_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "F308D190B7C8522407F9423AB312C8683F92D52E0E4A411B3F160B8ABF901069",
    "raw_size": 995_832,
    "sha256": "07661E9AF84CB5D67CB7025B8813806525083796578BBE2358046426355C81EC",
    "size": 999_763,
}

# 8382 is the preceding address; 8383–8391 is the complete exchange between
# Takahashi Munetora and Takahashi Jōun about Bekki Akitsura's remains.
SCENE_IDS = tuple(range(8_383, 8_392))
CHANGED_IDS = (8_384, 8_385, 8_387, 8_388, 8_389, 8_390, 8_391)
RETAINED_IDS = (8_383, 8_386)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# These reservations are deliberately scene-local and conservative.  They
# document no runtime observation: they simply reserve the verified Korean
# full-name display width when the event renders the dynamic name tokens.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[bm1222]": {
        "display": "다카하시 무네토라",
        "source_slot_id": 1222,
        "reserved_raw_g1n_width_px": 408,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 1222; conservative full-name reservation for this scene only",
    },
    "[bm1730]": {
        "display": "벳키 아키츠라",
        "source_slot_id": 1730,
        "reserved_raw_g1n_width_px": 312,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 1730; conservative full-name reservation for this scene only",
    },
}
ROW_RUNTIME_TOKENS: Mapping[int, tuple[str, ...]] = {
    8383: ("[bm1222]",),
    8385: ("[bm1730]",),
    8387: ("[bm1222]",),
    8391: ("[bm1222]",),
}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    8384: f"저는 아버님의 유해를\n{E}CC다치바나산{E}CZ으로 옮길 생각이옵니다.",
    8385: f"{E}CA[bm1730]{E}CZ 공은 이 땅에 묻으라\n유언하셨을 터인데…?",
    8387: (
        "아버님께서 돌아가신 뒤에는\n"
        f"이 {E}CA[bm1222]{E}CZ가 {E}CB오토모{E}CZ를\n"
        "지키겠사옵니다."
    ),
    8388: (
        "그렇다면 아버님께서는\n"
        f"{E}CC다치바나산{E}CZ에서 편히\n"
        "잠드시게 할 생각입니다."
    ),
    8389: "훗…\n좋을 대로 하거라.",
    8390: "그러면 준비할 일이 있사온지라,\n이만 실례하겠습니다.",
    8391: f"(훌륭한 장수이자 훌륭한 사내가\n되었구나, {E}CA[bm1222]{E}CZ)",
}

RATIONALES: Mapping[int, str] = {
    8383: "direct PC JP/EN/SC/TC context revalidated; retained with [bm1222] reservation",
    8384: "고립된 첫 줄을 제거하고 유해를 옮길 의도를 한국어 의미 단위로 재구성",
    8385: "주어만 남은 줄을 해소하면서 유언의 의미를 보존",
    8386: "direct PC JP/EN/SC/TC context revalidated; retained",
    8387: "[bm1222] 보수 예약을 포함한 초과를 해소하고 오토모를 지키겠다는 맹세 보존",
    8388: "같은 立花山 표기를 다치바나산으로 통일하고 의미 단위로 재구성",
    8389: "好きにするがよかろう의 허락하는 연장자 어조를 자연스럽게 복원",
    8390: "支度와 御免의 준비·작별 의미를 복원",
    8391: "좋은 장수와 좋은 사내라는 병렬 칭찬을 보존하고 [bm1222] 예약 초과 해소",
}

# Every number below includes a substituted reservation where a runtime token
# appears.  This guards all nine scene rows against token-stripped auditing.
SCENE_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    8383: (744,),
    8384: (480, 792),
    8385: (792, 456),
    8386: (744, 816, 840),
    8387: (624, 744, 360),
    8388: (504, 456, 552),
    8389: (72, 408),
    8390: (720, 480),
    8391: (720, 672),
}

# Pinned from the one-time read-only W94 profile pass against strict W93.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "E323F774A74064DD00C8AD3670D76A03DCAE0C1100D1707DBA662EC999370358",
    "raw_size": 995_840,
    "sha256": "BC51F8954CA078D2BC96FCC8E82F7343F5DE5FB7892CE1954C1E987E8FAED7EE",
    "size": 999_771,
}


class Wave94Error(RuntimeError):
    """Raised when a source, reservation, layout, or candidate drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave94Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave94Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W93_BUILDER.is_file(), f"W93 helper builder missing: {W93_BUILDER}")
w93 = load_module("pc_event_wave93_base_for_wave94", W93_BUILDER)
parse_table = w93.parse_table
core = w93.core
control_signature = w93.control_signature
is_full_width_visible = w93.is_full_width_visible


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
        raise Wave94Error(f"candidate escapes tmp root: {resolved}") from exc
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


def validate_runtime_reservations() -> None:
    require(set(SCENE_RUNTIME_RESERVATIONS) == {"[bm1222]", "[bm1730]"}, "W94 reservation scope drift")
    expected = {"[bm1222]": (1222, "다카하시 무네토라", 408), "[bm1730]": (1730, "벳키 아키츠라", 312)}
    for token, (slot_id, display, raw) in expected.items():
        reservation = SCENE_RUNTIME_RESERVATIONS[token]
        require(reservation.get("source_slot_id") == slot_id, f"W94 reservation slot drift: {token}")
        require(reservation.get("display") == display, f"W94 reservation display drift: {token}")
        require(reservation.get("reserved_raw_g1n_width_px") == raw, f"W94 reservation raw width drift: {token}")
        require(raw_width(display) == raw, f"W94 reservation measured width drift: {token}")
        require(reservation.get("scene_limited") is True, f"W94 reservation not scene-limited: {token}")
        require(reservation.get("runtime_proven") is False, f"W94 runtime proof unexpectedly asserted: {token}")


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
            require(reservation is not None, f"missing W94 scene reservation: {token}")
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


def reservation_details(value: str) -> list[Mapping[str, Any]]:
    return [{"token": token, **SCENE_RUNTIME_RESERVATIONS[token]} for token in runtime_tokens(value)]


def validate_static_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "W94 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W94 retained scope drift")
    require(set(SCENE_RAW_WIDTHS) == set(SCENE_IDS), "W94 all-row metrics scope drift")
    validate_runtime_reservations()
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W94 runtime token scope drift: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W94 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W94 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == SCENE_RAW_WIDTHS[entry_id], f"W94 pinned target widths drift: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W93 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W93 Ōtomo predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W93_PROFILE, "W93 on-disk event profile drift")
    require(w93.EXPECTED_OUTPUT_PROFILE == EXPECTED_W93_PROFILE, "W93 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W93_PROFILE, "W93 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W93_PROFILE, "W93 manifest output profile drift")
    prior_changed = set(audit.get("coverage", {}).get("changed_row_ids", []))
    require(not prior_changed.intersection(SCENE_IDS), "W93 unexpectedly overlaps the W94 scene")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Any] = {}
    profiles: dict[str, Mapping[str, Any]] = {}
    for language, path in w93.w92.DIRECT_CONTEXT_PATHS.items():
        resolved = path.resolve(strict=True)
        parts = {part.casefold() for part in resolved.parts}
        require("switch" not in parts, f"non-PC context source forbidden: {resolved}")
        event = resolved.read_bytes()
        _header, raw, table = parse_table(f"direct PC {language.upper()} W94 context", event)
        source_profile = profile(event, raw)
        require(source_profile == w93.w92.EXPECTED_CONTEXT_PROFILES[language], f"direct PC {language.upper()} profile drift")
        require(len(table.texts) == w93.w92.EXPECTED_CONTEXT_ROW_COUNT, f"direct PC {language.upper()} row count drift")
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
        require(all((current, source_jp, source_en, source_sc, source_tc)), f"empty W94 row: {entry_id}")
        current_signature = control_signature(current)
        source_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == source_signature, f"W93/direct-PC-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W94 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W94 runtime token differs in row: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W94 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W94 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == SCENE_RAW_WIDTHS[entry_id], f"W94 all-row measured widths drift: {entry_id}")

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
                "w93_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "direct_pc_en_utf16le_sha256": text_hash(source_en),
                "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
                "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
                "w93_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES[entry_id],
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(runtime_tokens(target)),
                "runtime_reservations": reservation_details(target),
                "runtime_proven": False,
                "control_signature": target_signature,
            }
        )

    require(tuple(sorted(changed)) == CHANGED_IDS, "W94 changed ID scope drift")
    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W93 Ōtomo predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W94 Ōtomo event", event)
    require(after_raw == rebuilt_raw, "W94 raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS), "W94 actual event diff scope drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W94 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W94 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-otomo-tachibana-quality-wave94-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W93 PC Korean candidate plus direct PC JP/EN/SC/TC context",
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
        "input_w93_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-otomo-tachibana-quality-wave94-manifest.v1",
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
    require(not output.exists(), f"W94 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W94 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W94 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W94 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W94 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W94 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W94 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_otomo_tachibana_quality_wave94_v1.py",
        WORKSTREAM / "test_pc_event_otomo_tachibana_quality_wave94_v1.py",
    ):
        require(path.is_file(), f"W94 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W94 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "W94 output profile is not pinned")
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
