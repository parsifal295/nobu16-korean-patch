#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 1."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
WORKSPACE_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
from build_literal_overlay import (  # noqa: E402
    OVERLAY_SCHEMA,
    apply_overlay_blob,
    text_hash,
)
from build_structure_inventory import SOURCE_PINS  # noqa: E402
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    is_visible_translation_candidate,
    iter_literals,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_raw_msggame,
    sha256,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


BATCH_ID = "msggame_pk_system_messages_b01r0003_b02r0086_0197.v0.1"
OVERLAY_NAME = (
    "msggame_ko_system_messages_b01r0003_b02r0086_0197.v0.1.json"
)
EVIDENCE_NAME = "translation_alignment_evidence.v0.1.json"
REVIEW_NAME = "translation_review_index.v0.1.json"
VALIDATION_NAME = "translation_validation.v0.1.json"
RESOURCE = "MSG_PK/SC/msggame.bin"
LANGUAGES = ("SC", "JP", "EN", "TC")
SOURCE_PATHS = {language: f"MSG_PK/{language}/msggame.bin" for language in LANGUAGES}
NEXT_COORDINATE = (2, 198, 0)
DEFERRED_DYNAMIC_FRAGMENT_COUNT = 93


# The values below are project-authored Korean only. Commercial source text is
# read from a user's pinned installation while building and is represented in
# published artifacts solely by UTF-16LE SHA-256 hashes.
TRANSLATIONS: dict[tuple[int, int], tuple[str, ...]] = {
    (1, 3): ("그야말로 청천벽력입니다.\n",),
    (2, 86): ("성인식을 마친 공주가 있군.\n공주의 앞날도 생각해 봐야겠어……",),
    (2, 87): (
        "성인식을 마친 공주가 있는 모양이군요.\n공주의 앞날도 생각해 봐야겠습니다……",
    ),
    (2, 88): ("성인식을 마친 공주가 있습니다.\n공주의 앞날도 헤아려 주십시오……",),
    (2, 89): ("성인식을 마친 공주가 있습니다.\n공주의 앞날도 헤아려 주십시오……",),
    (2, 90): ("이름과 읽는 법을 입력해 주십시오.",),
    (2, 91): ("이름에 사용할 수 없는 문자가 포함되어 있습니다.",),
    (2, 92): ("내용을 확인한 뒤 확인을 눌러 주십시오.",),
    (2, 93): ("무장으로 키울지 공주로 키울지 선택한 뒤 확인을 눌러 주십시오.",),
    (2, 94): ("부인:", "이(가) 무장으로 원복했습니다."),
    (2, 95): ("딸:", "이(가) 무장으로 원복했습니다."),
    (2, 96): ("부인:", "이(가) 성인식을 마치고 성인이 되었습니다."),
    (2, 97): ("딸:", "이(가) 성인식을 마치고 성인이 되었습니다."),
    (2, 98): ("가신의 딸:", "이(가) 성인이 되었습니다."),
    (2, 103): (
        "성인식을 마쳐 저도 어엿한 성인이 되었습니다.\n"
        "무가의 아내로서 맡은 바를 다하도록,\n앞으로도 정진하겠습니다.",
    ),
    (2, 104): (
        "마침내 어엿한 성인이 되었으니,\n앞으로 주군을 훌륭히 보필하고,\n"
        "본가의 번영에 조금이나마 힘이 되겠습니다.",
    ),
    (2, 109): (
        "님, 찾아뵈었습니다.\n성인식도 마쳤으니 이제부터\n충성을 바칠 대상:",
        "입니다.",
    ),
    (2, 110): (
        "성인식을 마친 무가의 딸로서,\n충성을 바칠 대상:",
        "에게 힘을 보탤 날을 맞아,\n오랫동안 기다려 온 보람을 느낍니다.",
    ),
    (2, 111): ("원복 완료 인원:", "명.\n어엿한 무장으로 성장했습니다."),
    (2, 112): ("휘하 합류 인원:", "명.\n원복을 마치고 휘하의 무장이 되었습니다."),
    (2, 113): ("의 적대 목표를 갱신했습니다.",),
    (2, 114): ("의 수입이 부족하여 금전 공납량이 감소했습니다.",),
    (2, 115): ("의 수입이 부족하여 군량 공납량이 감소했습니다.",),
    (2, 116): ("의 수입이 부족하여 군마 공납량이 감소했습니다.",),
    (2, 117): ("의 수입이 부족하여 철포 공납량이 감소했습니다.",),
    (2, 118): ("플레이어 세력이 멸망했습니다.\n게임을 종료합니다.",),
    (2, 119): ("혼인 동맹 파기 대상:", "입니다.\n실행하시겠습니까?"),
    (2, 120): ("혼인 동맹 파기 대상:", "등입니다.\n실행하시겠습니까?"),
    (2, 121): (
        "혈연관계가 없는 대상:",
        ".\n이로 인해 출가하려는 공주가 있습니다. 허락하시겠습니까?",
    ),
    (2, 126): (
        "나머지는 제게 맡겨주십시오.\n후임 당주:",
        "이(가) 본가를 패자로 만들겠습니다.",
    ),
    (2, 127): (
        "라는 이름은 무겁지만 자랑스럽기도 하여,\n마음이 절로 다잡아집니다.\n"
        "앞으로는 제게 맡겨주십시오.",
    ),
    (2, 128): ("제게 맡겨주십시오.\n본가는 제가 지켜내겠습니다.",),
    (2, 129): (
        "안심하십시오. 전 당주:",
        "가 지켜 온 본가:",
        "입니다.\n제 지략과 무용으로 가문을 이어가겠습니다……\n"
        "아니, 더욱 번영시키겠다고 맹세합니다.",
    ),
    (2, 130): ("전 당주:", "\n그 뒤를 이어 이 가문을 다시 일으키겠습니다."),
    (2, 131): (
        "님, 지금까지 본가의 주인으로서\n정말 수고 많으셨습니다.\n후임 당주:",
        "에게 맡겨주십시오.",
    ),
    (2, 138): ("편히 쉬십시오.\n본가는…… 제가 반드시 지켜내겠습니다.",),
    (2, 143): ("이(가) 당주가 된 가문:", "입니다."),
    (2, 144): ("에서 출가한 인물:", "입니다."),
    (2, 145): ("변경 전 세력명:", ", 변경 후 세력명:", "가문", "."),
    (2, 146): ("의 멸망 원인 세력:", "입니다."),
    (2, 147): ("의 멸망 원인 세력:", "입니다."),
    (2, 148): ("이(가) 병에 걸렸습니다.",),
    (2, 149): ("등 발병 인원:", "명이 병에 걸렸습니다."),
    (2, 150): ("이(가) 회복했습니다.",),
    (2, 151): ("등 회복 인원:", "명이 회복했습니다."),
    (2, 152): ("공략 대상 세력:", "을(를) 공략하여 공략 방침을 달성했습니다."),
    (2, 153): ("공략 대상 세력:", "이(가) 멸망하여 공략 방침이 해제되었습니다."),
    (2, 154): ("공략 대상 세력:", "이(가) 아군이 되어 공략 방침이 해제되었습니다."),
    (2, 155): (
        "공략 대상 세력:",
        "으로 향하는 행군로가 사라져 공략 방침이 해제되었습니다.",
    ),
    (2, 156): ("공략 대상 세력:", "과(와) 휴전하여 공략 방침이 해제되었습니다."),
    (2, 157): ("공략 대상 성:", "을(를) 공략했습니다."),
    (2, 158): ("의 소속 세력이 바뀌어 공략 대상 성에서 해제되었습니다.",),
    (2, 159): ("의 소속 세력이 아군이 되어 공략 대상 성에서 해제되었습니다.",),
    (2, 160): (
        "행군로 소실 대상:",
        "으로 향하는 길이 사라져 공략 대상 성에서 해제되었습니다.",
    ),
    (2, 161): (
        "휴전 대상 성:",
        "의 소속 세력과 휴전하여 공략 대상 성에서 해제되었습니다.",
    ),
    (2, 162): ("지배 중인 성하에 막부의 권위를 나타내는 시설이 없습니다.",),
    (2, 163): ("지배 중인 성하에 막부의 권위를 나타내는 시설이 있습니다.",),
    (2, 164): ("당주는 정이대장군으로서 무사의 영수입니다.",),
    (2, 165): ("당주가 막부의 직책에 취임하지 않았습니다.",),
    (2, 166): ("당주의 막부 직책:", "입니다."),
    (2, 167): ("막부 창시자의 혈통을 잇는 가문:", "의 당주입니다."),
    (2, 168): ("막부와 인연이 있는 가문:", "의 당주입니다."),
    (2, 169): ("지배 중인 성하에 조정의 권위를 나타내는 시설이 없습니다.",),
    (2, 170): ("지배 중인 성하에 조정의 권위를 나타내는 시설이 있습니다.",),
    (2, 171): ("당주가 관직에 취임하지 않았습니다.",),
    (2, 172): ("당주의 조정 관직:", "입니다."),
    (2, 173): ("조정과 인연이 있는 가문:", "의 당주입니다."),
    (2, 174): ("지배 중인 성하에 종교·문화적 가치가 있는 시설이 없습니다.",),
    (2, 175): ("지배 중인 성하에 종교·문화적 권위를 나타내는 시설이 있습니다.",),
    (2, 176): ("일향종을 통솔하는 세력:", "의 종주입니다."),
    (2, 177): ("권위 있는 가문:", "의 당주입니다."),
    (2, 178): ("막부의 정당성을 드러내는 정책을 채택하지 않았습니다.",),
    (2, 179): ("막부의 정당성을 드러내는 정책을 채택했습니다.",),
    (2, 180): ("조정의 위광을 드러내는 정책을 채택하지 않았습니다.",),
    (2, 181): ("조정의 위광을 드러내는 정책을 채택했습니다.",),
    (2, 182): ("종교·문화 등 천하에 존재감을 드러내는 정책을 채택하지 않았습니다.",),
    (2, 183): ("종교·문화 등 천하에 존재감을 드러내는 정책을 채택했습니다.",),
    (2, 184): ("지배 중인 군에 종교·문화적 가치가 있는 취락이 없습니다.",),
    (2, 185): ("지배 중인 군에 종교·문화적 권위를 나타내는 취락이 있습니다.",),
    (2, 186): ("본가가 지배하는 성:", "개입니다."),
    (2, 187): ("이(가) 지배하는 지역:", "의 모든 성을 지배하고 있습니다."),
    (2, 188): (
        "옛 본거지:",
        "에서 이전하려는 목적지는\n",
        "입니다. 옮길 수 없는 시설이 있습니다.\n그래도 이전하시겠습니까?",
    ),
    (2, 189): (
        "본거지 이전 대상:",
        "에서 재이전할 목적지는\n",
        "입니다. 옮길 수 없는 시설이 있습니다.\n그래도 이전하시겠습니까?",
    ),
    (2, 190): (
        "시설 이전 출발지:",
        ", 목적지:",
        "입니다.\n건설 칸이 부족합니다.\n이전을 포기할 시설을 선택하십시오.",
    ),
    (2, 191): ("본거지 이전:", "→", "(으)로\n이전이 완료되었습니다."),
    (2, 192): (
        "옛 본거지:",
        "이(가) 함락되어 본거지를\n",
        "(으)로 옮겼습니다.",
    ),
    (2, 193): ("「", "」 등 정책 수:", "개. 해당 정책을 철회했습니다."),
    (2, 194): ("정책 「", "」을 철회했습니다."),
    (2, 195): ("위신이 하락하여 정책 「", "」을 철회했습니다."),
    (2, 196): ("다이묘의 방침과 맞지 않아 정책 「", "」을 철회했습니다."),
    (2, 197): ("정책 「", "」을 철회했습니다."),
}


# Parentheses are ordinary Korean prose punctuation here (for particle choices
# such as ``이(가)``).  Preserve only bracket/quote forms that can delimit
# placeholders or injected names in the source records.
BRACKET_CHARS = frozenset("[]{}<>［］｛｝〈〉《》「」『』【】〔〕")
CJK_UNIFIED_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.relative_to(path.parents[1]).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": len(CJK_UNIFIED_RE.findall(text)),
        "kana_count": len(KANA_RE.findall(text)),
    }


def bracket_sequence(text: str) -> list[str]:
    return [character for character in text if character in BRACKET_CHARS]


def source_structure(text: str) -> dict[str, Any]:
    invariant = common.message_invariants(text)
    return {
        "utf16_code_units": len(text.encode("utf-16-le")) // 2,
        "printf_tokens": invariant["printf"],
        "unknown_percent_count": invariant["unknown_percent_count"],
        "escape_sequences": invariant["esc"],
        "control_codepoints": invariant["controls"],
        "line_breaks": invariant["line_breaks"],
        "private_use_codepoints": invariant["pua"],
        "bracket_sequence": bracket_sequence(text),
        "leading_whitespace_utf16le_sha256": text_hash(invariant["leading_whitespace"]),
        "trailing_whitespace_utf16le_sha256": text_hash(invariant["trailing_whitespace"]),
    }


def record_reference(record: Any) -> dict[str, Any]:
    literals = parse_record_literals(record)
    hashes = [text_hash(literal.text) for literal in literals]
    chain = hashlib.sha256("\n".join(hashes).encode("ascii")).hexdigest().upper()
    return {
        "record_data_sha256": sha256(record.data),
        "literal_count": len(literals),
        "visible_literal_count": sum(
            is_visible_translation_candidate(literal.text) for literal in literals
        ),
        "literal_hash_chain_sha256": chain,
        "literals": [
            {
                "literal_id": literal.literal_id,
                "utf16le_sha256": text_hash(literal.text),
                "structure": source_structure(literal.text),
            }
            for literal in literals
        ],
    }


def record_skeleton(record: Any) -> bytes:
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        output.extend(record.data[cursor : literal.marker_offset])
        output.extend(LITERAL_START)
        output.extend(LITERAL_END)
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


def selected_record_keys() -> list[tuple[int, int]]:
    return sorted(TRANSLATIONS)


def selected_coordinates() -> list[tuple[int, int, int]]:
    return [
        (block_id, record_id, literal_id)
        for block_id, record_id in selected_record_keys()
        for literal_id in range(len(TRANSLATIONS[(block_id, record_id)]))
    ]


def validate_static_scope() -> None:
    keys = selected_record_keys()
    if keys[0] != (1, 3) or keys[-1] != (2, 197):
        raise ValueError("translation batch boundaries changed")
    if any(block_id not in (1, 2) for block_id, _record_id in keys):
        raise ValueError("translation batch contains an unexpected block")
    if any(not (86 <= record_id <= 197) for block_id, record_id in keys if block_id == 2):
        raise ValueError("block 2 translation scope changed")
    if len(selected_coordinates()) != 150:
        raise ValueError("translation batch must contain exactly 150 literals")


def load_sources(paths: dict[str, Path]) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for language in LANGUAGES:
        logical_path = SOURCE_PATHS[language]
        pin = SOURCE_PINS[logical_path]
        packed = paths[language].read_bytes()
        if len(packed) != pin["packed_size"] or sha256(packed) != pin["packed_sha256"]:
            raise ValueError(f"{language} packed msggame source pin mismatch")
        _header, raw = decompress_wrapper(packed)
        if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
            raise ValueError(f"{language} raw msggame source pin mismatch")
        parsed = parse_packed_msggame(packed)
        if parsed.archive.record_count != pin["record_count"]:
            raise ValueError(f"{language} record count mismatch")
        if rebuild_raw_msggame(parsed.archive) != raw:
            raise ValueError(f"{language} raw parse/rebuild is not byte-identical")
        loaded[language] = {"packed": packed, "raw": raw, "parsed": parsed}
    return loaded


def _record_map(archive: Any) -> dict[tuple[int, int], Any]:
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def _literal_map(archive: Any) -> dict[tuple[int, int, int], Any]:
    return {
        (literal.block_id, literal.record_id, literal.literal_id): literal
        for literal in iter_literals(archive)
    }


def _uncertainty_flags(
    coordinate: tuple[int, int, int],
    record_counts: dict[str, int],
) -> list[str]:
    block_id, record_id, _literal_id = coordinate
    flags = ["runtime_line_wrap_review"]
    if len(set(record_counts.values())) != 1:
        flags.append("cross_language_literal_shape_diff")
    if len(TRANSLATIONS[(block_id, record_id)]) > 1 or record_id in {
        109,
        113,
        114,
        115,
        116,
        117,
        127,
        138,
        148,
        150,
        158,
        159,
        185,
        187,
    }:
        flags.append("runtime_dynamic_join_review")
    if coordinate == (1, 3, 0):
        flags.append("jp_reference_absent_en_reference_empty_tc_used")
    if coordinate == (2, 185, 0):
        flags.append("sc_semantic_conflict_resolved_from_jp_en_tc")
    return flags


def _assert_public_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    scans: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = script_counts(path.read_text(encoding="utf-8"))
        scans[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise ValueError(f"source-script text leaked into {path}")
    return scans


def build(args: argparse.Namespace) -> dict[str, Any]:
    validate_static_scope()
    paths = {
        language: Path(getattr(args, f"stock_{language.lower()}")).resolve()
        for language in LANGUAGES
    }
    installed_before = {language: sha256(path.read_bytes()) for language, path in paths.items()}
    loaded = load_sources(paths)
    archives = {language: loaded[language]["parsed"].archive for language in LANGUAGES}
    records = {language: _record_map(archive) for language, archive in archives.items()}
    sc_literals = _literal_map(archives["SC"])

    overlay_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    invariant_failures: list[dict[str, Any]] = []
    record_evidence: list[dict[str, Any]] = []
    replacement_map: dict[tuple[int, int, int], str] = {}

    for block_id, record_id in selected_record_keys():
        key = (block_id, record_id)
        source_record_literals = parse_record_literals(records["SC"][key])
        replacements = TRANSLATIONS[key]
        if len(source_record_literals) != len(replacements):
            raise ValueError(
                f"translation literal count mismatch at {key}: "
                f"source={len(source_record_literals)}, ko={len(replacements)}"
            )
        if not all(is_visible_translation_candidate(item.text) for item in source_record_literals):
            raise ValueError(f"selected record contains an invisible SC literal: {key}")

        language_references = {
            language: record_reference(records[language][key]) for language in LANGUAGES
        }
        literal_counts = {
            language: language_references[language]["literal_count"]
            for language in LANGUAGES
        }
        record_evidence.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "selected_sc_literal_ids": list(range(len(replacements))),
                "references": language_references,
                "literal_shape_aligned_across_languages": len(set(literal_counts.values())) == 1,
                "cross_language_literal_id_alignment_used": False,
                "manual_same_record_semantic_crosscheck": True,
            }
        )

        for literal, replacement in zip(source_record_literals, replacements, strict=True):
            coordinate = (block_id, record_id, literal.literal_id)
            problems = common.invariant_mismatches(literal.text, replacement)
            if bracket_sequence(literal.text) != bracket_sequence(replacement):
                problems.append(
                    "bracket_sequence: "
                    f"source={bracket_sequence(literal.text)!r}, "
                    f"ko={bracket_sequence(replacement)!r}"
                )
            if problems:
                invariant_failures.append(
                    {"coordinate": list(coordinate), "problems": problems}
                )
            replacement_map[coordinate] = replacement
            overlay_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "source_sc_utf16le_sha256": text_hash(literal.text),
                    "ko": replacement,
                }
            )
            review_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "status": "translated",
                    "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en_tc_record_context",
                    "automated_draft": True,
                    "human_review_required": True,
                    "runtime_reviewed": False,
                    "uncertainty_flags": _uncertainty_flags(coordinate, literal_counts),
                }
            )
    if invariant_failures:
        raise ValueError(f"replacement invariants failed: {invariant_failures}")

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "packed_size": len(sc_packed),
            "packed_sha256": sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": sha256(sc_raw),
            "record_count": archives["SC"].record_count,
            "literal_slot_count": len(sc_literals),
        },
        "entries": overlay_entries,
    }

    rebuilt, binary_manifest = apply_overlay_blob(sc_packed, overlay)
    _target_header, target_raw = decompress_wrapper(rebuilt)
    target = parse_packed_msggame(rebuilt)
    target_literals = _literal_map(target.archive)
    target_records = _record_map(target.archive)

    if set(target_literals) != set(sc_literals):
        raise ValueError("literal coordinates changed after rebuild")
    for coordinate, source_literal in sc_literals.items():
        expected = replacement_map.get(coordinate, source_literal.text)
        if target_literals[coordinate].text != expected:
            raise ValueError(f"rebuilt literal mismatch at {coordinate}")
    if set(target_records) != set(records["SC"]):
        raise ValueError("record coordinates changed after rebuild")
    if any(
        record_skeleton(records["SC"][key]) != record_skeleton(target_records[key])
        for key in target_records
    ):
        raise ValueError("opaque record bytecode changed outside literal text")
    if rebuild_raw_msggame(target.archive) != target_raw:
        raise ValueError("rebuilt target raw parse/rebuild is not byte-identical")

    source_block_counts = [len(block.records) for block in archives["SC"].blocks]
    target_block_counts = [len(block.records) for block in target.archive.blocks]
    if source_block_counts != target_block_counts:
        raise ValueError("top-level block record counts changed")
    if any(block.offset % 4 for block in target.archive.blocks):
        raise ValueError("rebuilt top-level block offset is not four-byte aligned")

    selected = selected_coordinates()
    if [tuple(entry[key] for key in ("block_id", "record_id", "literal_id")) for entry in overlay_entries] != selected:
        raise ValueError("overlay coordinate order is not deterministic")
    if selected[-1] != (2, 197, 1) or NEXT_COORDINATE not in sc_literals:
        raise ValueError("batch continuation boundary changed")

    record_keys = selected_record_keys()
    evidence = {
        "schema": "nobu16.kr.msggame-translation-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "deferred_dynamic_fragment_count": DEFERRED_DYNAMIC_FRAGMENT_COUNT,
            "deferred_scope": "block_0_visible_pronoun_honorific_grammar_fragments",
        },
        "alignment_basis": [
            "same_pk_resource_role",
            "same_18_block_shape",
            "same_block_and_record_coordinates",
            "manual_same_record_semantic_crosscheck",
            "language_literal_shapes_may_differ",
            "cross_language_literal_id_alignment_not_used",
        ],
        "source_files": {
            language: {
                "logical_path": SOURCE_PATHS[language],
                **SOURCE_PINS[SOURCE_PATHS[language]],
            }
            for language in LANGUAGES
        },
        "record_count": len(record_evidence),
        "records": record_evidence,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msggame-translation-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(review_entries),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts["overlay"] = write_json(overlay_path, overlay)
    artifacts["alignment_evidence"] = write_json(evidence_path, evidence)
    artifacts["review_index"] = write_json(review_path, review)
    source_free_scan = _assert_public_source_free(
        (overlay_path, evidence_path, review_path)
    )

    installed_after = {language: sha256(path.read_bytes()) for language, path in paths.items()}
    if installed_before != installed_after:
        raise ValueError("installed game source changed during read-only batch build")

    validation = {
        "schema": "nobu16.kr.msggame-translation-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "selected_coordinates_sha256": sha256(
                json.dumps(selected, separators=(",", ":")).encode("utf-8")
            ),
        },
        "selection": {
            "stable_sc_coordinate_order": True,
            "natural_record_boundaries": True,
            "included_complete_display_records": True,
            "deferred_dynamic_fragment_count": DEFERRED_DYNAMIC_FRAGMENT_COUNT,
            "deferred_reason": "context_sensitive_pronoun_honorific_grammar_fragments",
            "internal_code_key_exclusions": 0,
        },
        "source_alignment": {
            "languages": list(LANGUAGES),
            "record_coordinates_aligned": True,
            "literal_shapes_assumed_aligned": False,
            "manual_same_record_semantic_crosschecks": len(record_keys),
            "record_reference_count": len(record_keys) * len(LANGUAGES),
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "escape_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_sequence_in_order",
            ],
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": sha256(rebuilt),
            "target_raw_size": len(target_raw),
            "target_raw_sha256": sha256(target_raw),
            "literal_coordinates_preserved": True,
            "record_coordinates_preserved": True,
            "opaque_record_bytecode_preserved": True,
            "top_level_offsets_recomputed_and_aligned": True,
            "raw_parse_rebuild_byte_exact": True,
            "installed_game_file_written": False,
        },
        "translation_status": {
            "translated_draft": len(selected),
            "human_review_required": len(selected),
            "runtime_reviewed": 0,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "byte_identical_offline_binary_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_modified": False,
            "progress_manifest_modified": False,
            "other_workstreams_modified": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    artifacts["generation_validation"] = write_json(validation_path, validation)
    if script_counts(validation_path.read_text(encoding="utf-8")) != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError("source-script text leaked into validation artifact")
    return {
        "out_root": out_root,
        "entry_count": len(selected),
        "record_count": len(record_keys),
        "next_coordinate": NEXT_COORDINATE,
        "target_packed_sha256": sha256(rebuilt),
        "artifacts": artifacts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for language in LANGUAGES:
        parser.add_argument(
            f"--stock-{language.lower()}",
            type=Path,
            default=WORKSPACE_ROOT / Path(SOURCE_PATHS[language]),
        )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"records={result['record_count']}")
    print(f"entries={result['entry_count']}")
    print("next_coordinate=" + ",".join(map(str, result["next_coordinate"])))
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
