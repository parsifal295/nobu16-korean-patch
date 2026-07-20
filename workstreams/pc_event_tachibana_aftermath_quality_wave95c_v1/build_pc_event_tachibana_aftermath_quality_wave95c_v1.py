#!/usr/bin/env python3
"""Build the private W95c Tachibana-aftermath correction from strict W95b.

This tool accepts only the pinned on-disk W95b candidate as its Korean input.
It rechecks all ten corrected entries against the direct PC JP/EN/SC/TC tables,
and only writes a three-file candidate beneath this workstream's private tmp
directory.  It has no Steam, Git, network, or release operation.
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

W95B_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_tachibana_aftermath_linebreak_wave95b_v1"
    / "build_pc_event_tachibana_aftermath_linebreak_wave95b_v1.py"
)
MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_tachibana_aftermath_linebreak_wave95b_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W95B_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "FABEE3442CE0B74C55BD58B4E2338C701B8B8A47B6132FC94284E96C811D211C",
    "raw_size": 995_848,
    "sha256": "C2E266BC6589DC730D39DB74839AE7DD37E0ACCC953238E4B090E154486C44B3",
    "size": 999_779,
}

CHANGED_IDS = (8400, 8405, 8411, 8417, 8419, 8421, 8422, 8432, 8435, 8438)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# The colour wrappers already present in the strict W95b predecessor remain
# around their names.  Only the Korean wording and/or manual LF allocation is
# changed here; no sentence is shortened or deleted.
TARGETS: Mapping[int, str] = {
    8400: (
        "하지만 두 사람은 자식 복이 없어\n"
        "자연히 사이도 소원해져,\n"
        "\x1bCA[bm1730]\x1bCZ의 사후 얼마 지나지 않아\n"
        "별거하고 있었다."
    ),
    8405: "아버님 일은 미안하네.\n내가 간병을 제대로 못 한 탓이지.",
    8411: "그런 일은\n아무도 알려 주지 않았습니다.",
    8417: (
        "그런 말씀이 아닙니다.\n"
        "아버님…… 아버님과 당신께서\n"
        "나누신 이야기를 묻는 것입니다."
    ),
    8419: (
        "당신께서 오신 뒤로,\n"
        "아버님은 당신하고만 나가시고……\n"
        "저 같은 이는 안중에도 없으셨으니까요."
    ),
    8421: (
        "아버님 이야기인가, 어디 보자…\n"
        "은어 먹는 법이 무사답지 않다고\n"
        "꾸중을 들었다든가.\n"
        "이런 이야기면 되겠는가?"
    ),
    8422: "무사답지 않다고요?",
    8432: (
        "아버님이 안 계셔도 이 \x1bCA무네시게\x1bCZ가 있다.\n"
        "외로우면 언제든 찾아와도 좋다."
    ),
    8435: "아버님께 뒤지지 않는 무사가 되도록\n나는 힘쓸 생각이다.\n그대도 건강하거라.",
    8438: (
        "무사로서의 그릇은 아버님을 넘는다…\n"
        "당신은 아버님께서 말씀하신\n"
        "그런 분이셨습니다."
    ),
}
LF_ONLY_IDS = (8400,)
ROW_RUNTIME_TOKENS: Mapping[int, tuple[str, ...]] = {8400: ("[bm1730]",)}
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[bm1730]": {
        "source_slot_id": 1730,
        "display": "벳키 아키츠라",
        "reserved_raw_g1n_width_px": 312,
        "scene_limited": True,
        "runtime_proven": False,
    }
}
RATIONALES: Mapping[int, str] = {
    8400: "문장 삭제 없이 내레이션의 인과와 수동 개행을 정리했다.",
    8405: "간병을 충분히 하지 못했다는 화자의 자책을 명확히 했다.",
    8411: "정보를 전혀 듣지 못했다는 대사의 주어와 부정을 자연스럽게 했다.",
    8417: "아버지와 상대가 나눈 대화를 묻는 의도를 분명히 했다.",
    8419: "아버지에게 소외되었다는 화자의 원망을 원문 의미대로 복원했다.",
    8421: "은어 먹는 법으로 꾸중 들은 일화를 자연스러운 구어체로 정리했다.",
    8422: "무사답지 않다는 평가를 의문문으로 정확히 옮겼다.",
    8432: "무네시게가 곁에 있다는 위로와 방문 권유를 원문 의미대로 정리했다.",
    8435: "아버지에게 뒤지지 않는 무사가 되겠다는 결의와 작별을 바로잡았다.",
    8438: "무사로서의 그릇과 아버지의 평을 원문의 의미대로 복원했다.",
}

# Pinned after the deterministic profile pass.  Keeping these gates in the
# source makes a later input/library drift fail closed.
TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] | None = {
    8400: (744, 552, 888, 384),
    8405: (504, 768),
    8411: (216, 672),
    8417: (504, 624, 720),
    8419: (456, 720, 888),
    8421: (696, 720, 432, 552),
    8422: (432,),
    8432: (912, 720),
    8435: (816, 456, 432),
    8438: (816, 624, 432),
}
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "C511A82E26762C6D5FC2573BE2E5B8B375A88C3B3C27E25FBECF5C51F2C48CA3",
    "raw_size": 995_864,
    "sha256": "2C22342032D494979D3BDE904648BCFD1BE5864169CB6F735B069C8025460BA2",
    "size": 999_795,
}


class Wave95cError(RuntimeError):
    """Raised when the strict predecessor, direct context, or output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave95cError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave95cError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W95B_BUILDER.is_file(), f"W95b helper builder missing: {W95B_BUILDER}")
w95b = load_module("pc_event_wave95b_base_for_wave95c", W95B_BUILDER)
parse_table = w95b.parse_table
core = w95b.core
control_signature = w95b.control_signature
is_full_width_visible = w95b.is_full_width_visible


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
        raise Wave95cError(f"candidate escapes tmp root: {resolved}") from exc
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


def validate_runtime_reservations() -> None:
    reservation = SCENE_RUNTIME_RESERVATIONS.get("[bm1730]")
    require(reservation is not None, "8400 runtime reservation missing")
    require(reservation["source_slot_id"] == 1730, "8400 reservation slot drift")
    require(reservation["display"] == "벳키 아키츠라", "8400 reservation display drift")
    require(reservation["reserved_raw_g1n_width_px"] == 312, "8400 reservation raw width drift")
    require(reservation["scene_limited"] is True, "8400 reservation must be scene-limited")
    require(reservation["runtime_proven"] is False, "8400 runtime proof must remain false")
    display = str(reservation["display"])
    measured = sum(1 for character in display if is_full_width_visible(character)) * RAW_FULL_WIDTH_PX
    measured += (len(display) - sum(1 for character in display if is_full_width_visible(character))) * RAW_HALF_WIDTH_PX
    require(measured == reservation["reserved_raw_g1n_width_px"], "8400 reservation measurement drift")


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
            token = runtime.group(0)
            reservation = SCENE_RUNTIME_RESERVATIONS.get(token)
            require(reservation is not None, f"missing scene reservation: {token}")
            rendered.append(str(reservation["display"]))
            cursor = runtime.end()
            continue
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


def reservation_details(value: str) -> list[Mapping[str, Any]]:
    return [{"token": token, **SCENE_RUNTIME_RESERVATIONS[token]} for token in runtime_tokens(value)]


def validate_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "W95c target scope drift")
    require(tuple(RATIONALES) == CHANGED_IDS, "W95c rationale scope drift")
    require(LF_ONLY_IDS == (8400,), "W95c LF-only scope drift")
    require(set(ROW_RUNTIME_TOKENS) == {8400}, "W95c runtime-token scope drift")
    validate_runtime_reservations()
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W95c target runtime-token drift: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W95c target line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W95c target raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if TARGET_RAW_WIDTHS is not None:
            require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W95c target widths drift: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W95b candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W95b predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W95B_PROFILE, "W95b on-disk event profile drift")
    require(w95b.EXPECTED_OUTPUT_PROFILE == EXPECTED_W95B_PROFILE, "W95b pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W95B_PROFILE, "W95b audit output profile drift")
    require(manifest.get("output") == EXPECTED_W95B_PROFILE, "W95b manifest output profile drift")
    require(audit.get("coverage", {}).get("changed_row_ids") == [8438], "W95b one-row scope drift")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    loader = getattr(w95b.w95, "load_direct_contexts", None)
    require(callable(loader), "W95 direct-PC context loader missing")
    tables, profiles = loader()
    require(tuple(sorted(tables)) == ("en", "jp", "sc", "tc"), "direct PC context language scope drift")
    require(tuple(sorted(profiles)) == ("en", "jp", "sc", "tc"), "direct PC context profile scope drift")
    return tables, profiles


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_targets()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    contexts, context_profiles = load_direct_contexts()
    require(all(len(before.texts) == len(table.texts) for table in contexts.values()), "event table topology drift")

    texts = list(before.texts)
    rows: list[Mapping[str, Any]] = []
    for entry_id in CHANGED_IDS:
        current = before.texts[entry_id]
        source_jp = contexts["jp"].texts[entry_id]
        source_en = contexts["en"].texts[entry_id]
        source_sc = contexts["sc"].texts[entry_id]
        source_tc = contexts["tc"].texts[entry_id]
        target = TARGETS[entry_id]
        require(all((current, source_jp, source_en, source_sc, source_tc, target)), f"empty W95c row: {entry_id}")
        current_signature = control_signature(current)
        require(current_signature == control_signature(source_jp), f"W95b/direct-PC-JP control drift: {entry_id}")
        require(control_signature(target) == current_signature, f"W95c control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W95c runtime-token differs: {entry_id}")
        if entry_id in LF_ONLY_IDS:
            require(LINEBREAK_RE.sub(" ", target) == LINEBREAK_RE.sub(" ", current), f"W95c LF-only visible text drift: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W95c line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W95c raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if TARGET_RAW_WIDTHS is not None:
            require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W95c measured widths drift: {entry_id}")
        require(target != current, f"W95c target unexpectedly equals predecessor: {entry_id}")
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
                "w95b_current_ko": current,
                "target_ko": target,
                "w95b_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": True,
                "review_disposition": "semantic_correction" if entry_id not in LF_ONLY_IDS else "lf_only_reflow",
                "rationale": RATIONALES[entry_id],
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "lf_only_reflow": entry_id in LF_ONLY_IDS,
                "normalized_visible_text_equal": (
                    LINEBREAK_RE.sub(" ", target) == LINEBREAK_RE.sub(" ", current)
                    if entry_id in LF_ONLY_IDS
                    else False
                ),
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(runtime_tokens(target)),
                "runtime_reservations": reservation_details(target),
                "runtime_proven": False,
                "control_signature": control_signature(target),
            }
        )

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W95b predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W95c Tachibana-aftermath event", event)
    require(after_raw == rebuilt_raw, "W95c raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W95c actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W95c output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W95c output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-tachibana-aftermath-quality-wave95c-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W95b PC Korean candidate plus direct PC JP/EN/SC/TC context",
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
            "runtime_reservations": SCENE_RUNTIME_RESERVATIONS,
            "runtime_reservations_scene_limited": True,
            "runtime_proven": False,
        },
        "coverage": {
            "reviewed_scene_ids": list(CHANGED_IDS),
            "reviewed_scene_row_count": len(CHANGED_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": [],
            "unchanged_after_review_count": 0,
        },
        "input_w95b_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-tachibana-aftermath-quality-wave95c-manifest.v1",
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
    require(not output.exists(), f"W95c candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W95c candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W95c candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W95c candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W95c candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W95c candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W95c candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_tachibana_aftermath_quality_wave95c_v1.py",
        WORKSTREAM / "test_pc_event_tachibana_aftermath_quality_wave95c_v1.py",
    ):
        require(path.is_file(), f"W95c authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W95c trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "W95c output profile is not pinned")
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
