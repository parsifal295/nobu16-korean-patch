#!/usr/bin/env python3
"""Build the private, one-row event-5777 Kanegasaki semantic correction.

The only Korean predecessor is the pinned W97 candidate.  Direct PC JP/EN/SC/TC
resources are read-only semantic witnesses.  This builder never writes Steam,
Git, a release payload, or any path outside its own tmp candidate directory.
"""

from __future__ import annotations

import argparse
import hashlib
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
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


MSGEV = "MSG_PK/JP/msgev.bin"
ENTRY_ID = 5_777
EXPECTED_ROW_COUNT = 17_916
PREDECESSOR_WORKSTREAM = "pc_event_toyotomi_kanpaku_quality_wave97_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_PREDECESSOR_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "E1810DEA757C5179A8C5631251656CDA83C36425C0699BE95650A6CCFBE4C11F",
    "raw_size": 996_240,
    "sha256": "C5451B9BA726C8D06743E86D8F6ED320E052F6B6065A37D550DE4ACCE3CF4810",
    "size": 1_000_172,
}
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "AB0F8AACA67B57B065695ED150C9A401847F89639899BA86B39843E9BE481B01",
    "raw_size": 996_276,
    "sha256": "273045FEE10099A37C78C6836ADE575ABFC2DD3E02EB84C65CAFDC61D7691EC8",
    "size": 1_000_208,
}

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

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[hlL]?[diuoxXfFeEgGaAcspn%]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

E = "\x1b"
EXPECTED_PREDECESSOR_KO = (
    f"{E}CC가네가사키{E}CZ 위기 벗어난 {E}CA노부나가{E}CZ는\n"
    f"{E}CC기후{E}CZ로 돌아와 태세 정비,\n"
    f"{E}CB아자이{E}CZ 토벌 뜻을 드러냈다."
)
EXPECTED_DIRECT_PC_JP = (
    f"{E}CC金ヶ崎{E}CZの窮地を脱した{E}CA織田信長{E}CZは、\n"
    f"{E}CC岐阜{E}CZに戻るとすぐに態勢を整え\n"
    f"{E}CB浅井家{E}CZ討伐の姿勢を明らかにした。"
)
TARGET_KO = (
    f"{E}CC가네가사키{E}CZ의 위기에서 벗어난\n"
    f"{E}CA오다 노부나가{E}CZ는 {E}CC기후{E}CZ로 돌아오자마자\n"
    "태세를 정비해,\n"
    f"{E}CB아자이 가문{E}CZ 토벌 의지를 분명히 밝혔다."
)
TARGET_RAW_WIDTHS = (672, 840, 336, 912)
EXPECTED_ESC_TOKENS = (
    f"{E}CC",
    f"{E}CZ",
    f"{E}CA",
    f"{E}CZ",
    f"{E}CC",
    f"{E}CZ",
    f"{E}CB",
    f"{E}CZ",
)
TERM_DECISION = {
    "requested_term": "방침",
    "selected_term": "의지",
    "reason": (
        "JP 姿勢, EN determined, SC 姿态, and TC 誓言 all indicate a declared "
        "intent/stance. 의지 is therefore more precise than an institutional policy."
    ),
}


class Event5777Error(RuntimeError):
    """Raised when the strict input, source evidence, or output drifts."""


@dataclass(frozen=True)
class Bundle:
    event: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Event5777Error(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(event),
        "size": len(event),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def parse_table(label: str, event: bytes) -> tuple[Any, bytes, Any]:
    header, raw = decompress_wrapper(event)
    table = parse_message_table(raw)
    require(len(table.texts) == EXPECTED_ROW_COUNT, f"{label} row-count drift: {len(table.texts)}")
    return header, raw, table


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Event5777Error(f"candidate escapes private tmp root: {resolved}") from exc
    return resolved


def control_signature(value: str) -> Mapping[str, Any]:
    esc_tokens: list[str] = []
    other_controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == E:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at {cursor}")
            esc_tokens.append(token)
            cursor += 3
            continue
        if character not in "\r\n" and unicodedata.category(character) == "Cc":
            other_controls.append(f"U+{ord(character):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf}
    return {
        "esc_tokens": esc_tokens,
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "other_controls": other_controls,
    }


def assert_no_break_inside_tag(value: str) -> None:
    in_colour_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == E:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            if token == f"{E}CZ":
                require(in_colour_span, "unpaired ESC close")
                in_colour_span = False
            else:
                require(not in_colour_span, "nested ESC colour span")
                in_colour_span = True
            cursor += 3
            continue
        require(not (in_colour_span and value[cursor] in "\r\n"), "line break inside ESC span")
        cursor += 1
    require(not in_colour_span, "unterminated ESC span")


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def rendered_display_line(value: str) -> str:
    rendered: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] == E:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token in layout: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        require(runtime is None, f"unexpected runtime token: {runtime.group(0) if runtime else ''}")
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


def validate_authored_target() -> None:
    require("\x00" not in TARGET_KO, "target contains an embedded UTF-16 terminator")
    require(TARGET_KO.count("\n") == MAX_LINES - 1, "target must use exactly four semantic lines")
    assert_no_break_inside_tag(TARGET_KO)
    signature = control_signature(TARGET_KO)
    require(tuple(signature["esc_tokens"]) == EXPECTED_ESC_TOKENS, "target ESC wrapper order drift")
    require(signature["runtime_tokens"] == [], "target unexpectedly has a runtime token")
    require(signature["printf_tokens"] == [], "target unexpectedly has a printf token")
    require(signature["unknown_percent_count"] == 0, "target has an unknown percent token")
    require(signature["other_controls"] == [], "target has an unexpected control")
    metrics = line_metrics(TARGET_KO)
    require(len(metrics) == MAX_LINES, "target line-count drift")
    require(tuple(line["raw_g1n_width_px"] for line in metrics) == TARGET_RAW_WIDTHS, "target raw widths drift")
    require(not any(line["over_live_raw_960px"] for line in metrics), "target exceeds raw 960px")
    require("방침" not in TARGET_KO and "의지" in TARGET_KO, "term decision drift")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W97 predecessor file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict W97 predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_PREDECESSOR_PROFILE, "W97 packed/raw predecessor profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_PREDECESSOR_PROFILE, "W97 audit profile drift")
    require(manifest.get("output") == EXPECTED_PREDECESSOR_PROFILE, "W97 manifest profile drift")
    require(table.texts[ENTRY_ID] == EXPECTED_PREDECESSOR_KO, "W97 row 5777 compact source drift")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Any] = {}
    profiles: dict[str, Mapping[str, Any]] = {}
    for language, path in DIRECT_CONTEXT_PATHS.items():
        resolved = path.resolve(strict=True)
        require("switch" not in {part.casefold() for part in resolved.parts}, f"non-PC source forbidden: {resolved}")
        event = resolved.read_bytes()
        _header, raw, table = parse_table(f"direct PC {language.upper()}", event)
        source_profile = profile(event, raw)
        require(source_profile == EXPECTED_CONTEXT_PROFILES[language], f"direct PC {language.upper()} profile drift")
        tables[language] = table
        profiles[language] = source_profile
    require(tuple(sorted(tables)) == ("en", "jp", "sc", "tc"), "direct-context language scope drift")
    return tables, profiles


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_authored_target()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    contexts, context_profiles = load_direct_contexts()
    require(all(len(before.texts) == len(table.texts) for table in contexts.values()), "direct-PC topology drift")

    source_jp = contexts["jp"].texts[ENTRY_ID]
    source_en = contexts["en"].texts[ENTRY_ID]
    source_sc = contexts["sc"].texts[ENTRY_ID]
    source_tc = contexts["tc"].texts[ENTRY_ID]
    current = before.texts[ENTRY_ID]
    require(source_jp == EXPECTED_DIRECT_PC_JP, "direct PC JP row 5777 source drift")
    require("determined" in source_en and "姿态" in source_sc and "誓言" in source_tc, "term-evidence drift")
    source_signature = control_signature(source_jp)
    current_signature = control_signature(current)
    target_signature = control_signature(TARGET_KO)
    require(current_signature == source_signature, "predecessor/direct-JP control signature drift")
    require(target_signature == current_signature, "target control signature drift")
    assert_no_break_inside_tag(current)
    assert_no_break_inside_tag(source_jp)
    assert_no_break_inside_tag(TARGET_KO)

    texts = list(before.texts)
    texts[ENTRY_ID] = TARGET_KO
    header, _raw_again, _table_again = parse_table("strict W97 predecessor", before_event)
    rebuilt_raw = rebuild_message_table(before, texts)
    event = recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("event-5777 output", event)
    require(after_raw == rebuilt_raw, "candidate raw reparse mismatch")
    changed_ids = [index for index, (left, right) in enumerate(zip(before.texts, after.texts)) if left != right]
    require(changed_ids == [ENTRY_ID], f"candidate is not an exact one-row diff: {changed_ids[:8]}")
    require(after.texts[ENTRY_ID] == TARGET_KO, "candidate target text drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "candidate packed/raw output profile drift")

    metrics = line_metrics(TARGET_KO)
    row = {
        "entry_id": ENTRY_ID,
        "changed": True,
        "predecessor_ko": current,
        "target_ko": TARGET_KO,
        "predecessor_ko_utf16le_sha256": text_hash(current),
        "target_ko_utf16le_sha256": text_hash(TARGET_KO),
        "direct_pc_jp": source_jp,
        "direct_pc_en": source_en,
        "direct_pc_sc": source_sc,
        "direct_pc_tc": source_tc,
        "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
        "direct_pc_en_utf16le_sha256": text_hash(source_en),
        "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
        "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
        "control_signature": target_signature,
        "japanese_source_line_breaks_used": False,
        "jp_lf_policy": "ignored",
        "runtime_tokens": [],
        "runtime_reservations": [],
        "runtime_proven": False,
        "source_line_count": len(LINEBREAK_RE.sub("\n", current).split("\n")),
        "target_manual_line_count": len(metrics),
        "line_count": len(metrics),
        "lines": list(metrics),
        "target_lines": list(metrics),
        "over_live_raw_960px": any(line["over_live_raw_960px"] for line in metrics),
        "terminator_policy": "UTF-16LE NUL terminator is serialized by rebuild_message_table",
        "semantic_term_choice": TERM_DECISION,
    }
    audit = {
        "schema": "nobu16.kr.pc-event-5777-kanegasaki-decompact-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "strict_input_only": PREDECESSOR_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
            "only_korean_predecessor_input": True,
            "direct_pc_context_read_only": True,
            "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
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
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_is_report_only": True,
            "runtime_reservations": {},
        },
        "source_profiles": {
            "strict_predecessor_w97": predecessor_profile,
            "direct_pc_contexts": context_profiles,
        },
        "output_event_profile": event_profile,
        "actual_changed_row_ids": changed_ids,
        "actual_changed_row_count": len(changed_ids),
        "exact_one_row_diff": row,
        "rows": [row],
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-5777-kanegasaki-decompact-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
            "only_korean_predecessor_input": True,
        },
        "direct_pc_context_profiles": context_profiles,
        "changed_row_ids": [ENTRY_ID],
        "exact_one_row_diff": True,
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"candidate staging already exists: {staging}")
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
    require(root.is_dir(), f"candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "candidate event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": [ENTRY_ID],
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_5777_kanegasaki_decompact_v1.py",
        WORKSTREAM / "test_pc_event_5777_kanegasaki_decompact_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("authoring-check", "profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "authoring-check":
        validate_authored_target()
        print(json.dumps({"entry_id": ENTRY_ID, "target_lines": list(line_metrics(TARGET_KO))}, ensure_ascii=False))
        return 0
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
    print(
        json.dumps(
            {
                "changed_row_ids": bundle.audit["actual_changed_row_ids"],
                "event_profile": bundle.profile,
                "target_ko": TARGET_KO,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
