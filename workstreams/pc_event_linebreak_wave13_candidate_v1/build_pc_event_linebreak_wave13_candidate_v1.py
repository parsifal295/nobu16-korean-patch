#!/usr/bin/env python3
"""Build a private PC-only Wave 13 Base-event dialogue candidate.

Wave 13 is intentionally narrow: it starts from the currently installed
NPC-component-quality Base-event profile and changes seven reviewed static
event cells.  The builder has no Steam-apply, overlay, release, or Git operation.
``--write`` can create only a private candidate, audit, and manifest below
``KR_PATCH_WORK/tmp/pc_event_linebreak_wave13_candidate_v1``.

The semantic anchor is pristine Steam-PC Japanese.  Nintendo Switch Korean
assets are neither read nor used as a source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

RESOURCE = "MSG/JP/ev_strdata.bin"
FONT_RESOURCE = "RES_JP/res_lang.bin"
PRISTINE_PC_JP_PATH = REPO.parent / "MSG" / "JP" / "ev_strdata.bin"

EXPECTED_INPUT_PACKED_SHA256 = "CC77EE4B0587B371A901069FB3F39C2187886C3A3335D9748D275FA2881EB426"
EXPECTED_INPUT_PACKED_SIZE = 928199
EXPECTED_INPUT_RAW_SHA256 = "8419E5B1FCBD0719F5598C5165C0880016C48D014F05AEB086FBB3A98A0A72A5"
EXPECTED_INPUT_RAW_SIZE = 924548
EXPECTED_OUTPUT_PACKED_SHA256 = "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80"
EXPECTED_OUTPUT_PACKED_SIZE = 928123
EXPECTED_OUTPUT_RAW_SHA256 = "87BF185203CA776787F74208B7505BCB21E53DB227FA9C8A15DD28388A68C1F4"
EXPECTED_OUTPUT_RAW_SIZE = 924472
EXPECTED_STRING_COUNT = 17868

EXPECTED_PRISTINE_PC_JP_SHA256 = "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB"
EXPECTED_PRISTINE_PC_JP_RAW_SHA256 = "5FBD960A4870FA4850BD725C58E67BE3A7F191960737C36E4505151FE4B7C528"
EXPECTED_FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"

# This is an empirical Base-event ceiling: among the selected records that
# already retain their contextual manual breaks, the largest current line is
# 4066's 1,104 px line.  Every target line must stay within that known-safe
# envelope and every target must have at most three contextual lines.
MAX_LINES = 3
EMPIRICAL_BASE_EVENT_MAX_LINE_PX = 1104
FONT_OUTER_ENTRY = 6
FONT_TABLE = 0
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u9fff\uf900-\ufaff]")


class CandidateError(RuntimeError):
    """A source pin, formatting guard, or private-output guard failed."""


@dataclass(frozen=True)
class Candidate:
    identifier: int
    current_utf16le_sha256: str
    target_utf16le_sha256: str
    pristine_pc_jp_utf16le_sha256: str
    target: str
    semantic_rationale: str
    linebreak_policy: str
    linebreak_rationale: str
    expected_target_widths_px: tuple[int, ...]


# The only seven logical Base-event cells this workstream can change.  The
# strings are candidate text, not a copied source translation.  7380 and 8350
# are the only entries where the Korean text intentionally regains two manual
# context breaks; the other five preserve their existing break count/vector.
CANDIDATES: tuple[Candidate, ...] = (
    Candidate(
        3280,
        "4C4AFF3BD49E15BE68F7BED8DF0B2DACDE8788E2CC95834651BC50D4B72DB9FD",
        "2A3EE816651247BF2F48D1094CF681B66F889334A2C9276AC635746BCCCB978B",
        "50F3DAAEB6DA9B973D8A4254E0DE6C299E314B3EFE621DACEC0436B3A8E3ADA6",
        "그리고…\n'내가 곧 길이다'라고 말씀하신 주여.\n저희에게 나아갈 길을 보여 주소서.",
        "말하는 이의 직접 인용과 기도체를 PC 일본어 원문의 의미에 맞춰 바로잡는다.",
        "preserve_existing_breaks",
        "호소의 도입 / 직접 인용 / 청원이라는 기존 3행 문맥을 유지한다.",
        (192, 840, 792),
    ),
    Candidate(
        4066,
        "36915F876283CDFBB38D31AB838AC8EA31982AC7837A9BBDEB17C00C33462449",
        "D4667A67953622542D2CAAD9DCA84AB20AD54F0B92F496A79559DBBD6172840E",
        "859D2A77D54DBEBBB5737D32A7DDAD06ED0470F38E39E37712E9F34023915F1B",
        "싸우지 않고 이기는 것이 병법의 요체입니다.\n공성은 하책, 마음을 얻는 것이 상책입니다.\n책략이 통하면 전쟁은 팔 할 이긴 셈입니다.",
        "병법의 대비(공성/마음)와 조략의 결과를 자연스러운 한국어로 정리한다.",
        "preserve_existing_breaks",
        "원문의 격언 / 대비 / 결론 구조인 기존 3행을 유지한다.",
        (1008, 984, 984),
    ),
    Candidate(
        5299,
        "B1A021362E5DA54395FD593028BAAE98FC2DD66B8E8815E780FF75C25A6E2988",
        "4E96BE9F34F32EF3C50822C58469E15D2A14AB4C97300FF6DB8D59D1453AB99F",
        "95FE836FEA7D5A7286520DC96A9CE1CE2F5E97852EDE1B52B6BD1D533B7E7EC5",
        "후사 없는 다이묘가 양자를 후계자로 들인다.\n그것이 비극으로 이어져 간다…\n전국 시대에는 흔한 광경이었다.",
        "양자를 '후계자로 들인다'는 관계와 시대 서술을 원문 의미에 맞춘다.",
        "preserve_existing_breaks",
        "사건 / 비극의 연결 / 시대적 총평이라는 기존 3행을 유지한다.",
        (1008, 696, 720),
    ),
    Candidate(
        6960,
        "9280E9C19ED95AEDFB3773A3ACEBF2493BF0007F93FAA4F29F30A7DD52E71044",
        "F6AC898549D6EC051313E0588772D19A4F86D6979DBFDE9F1C42A3673EBA91CA",
        "20B0450995F048304F3E3DC0121B623C265F6A8DD9851BB048424C7BC07C1573",
        "제 책략이 안이했던 모양입니다.\n일을 서두르다 그르친 듯합니다…",
        "조략 실패에 대한 자책의 어조를 간결하고 자연스럽게 바로잡는다.",
        "preserve_existing_breaks",
        "판단 / 후회의 두 호흡인 기존 2행을 유지한다.",
        (720, 744),
    ),
    Candidate(
        7380,
        "A414CB54DFC1847C527D8ED39AD4FB1AB4BFBD1BFD801480749AD3DB88BCDC22",
        "FF4F1D2F04DB06CFEB9A69A6DB34E3E3E97E22275DC02259F499F8C16F058A63",
        "DBF6E74480A077DE184B71ADFB4DF081C8097F48DE48FC98DC27302E78E59BBF",
        "(불복하는 자에겐 위세로 저항심을 꺾고,\n따르는 자에겐 희망을 줘 분발하게 한다.\n그것이 천하인의 방식이로군.)",
        "불복자와 복종자를 대비하는 천하인의 통치 방식을 의미에 맞춰 정리한다.",
        "restore_contextual_three_lines",
        "원문의 괄호 독백처럼 위세 / 희망 / 천하인의 결론을 각각 한 줄로 나눠, 무너진 수동 3행을 복원한다.",
        (912, 912, 672),
    ),
    Candidate(
        8140,
        "2BD20DC889F8ABAE07A73D8CF31D3CE4CC5C12C561EEF5114D0BB5EB4EC976ED",
        "856764C90E37523EA1155274B6C896AF5FFB9EA7BA7335AD513FB2949807BCD8",
        "BAAA6C4664E7DC68C0A9747D6457412DA55BF88192C19BA463C2B8111DA51790",
        "우리를 배신하면 어떻게 되는지… 본보기로\n엄히 벌하지 않으면 기강이 서지 않는다.\n출진한다!",
        "본보기로 엄벌한다는 명령의 강도와 자연스러운 문장을 바로잡는다.",
        "preserve_existing_breaks",
        "위협 / 징벌의 이유 / 출진 명령이라는 기존 3행을 유지한다.",
        (960, 912, 216),
    ),
    Candidate(
        8350,
        "8593E484228808CBB1766D8BDEF16AEF499D05625FE2AD24FFAC7E68DB879E2B",
        "1F7C0E1DFD8B6F092FF806F8FA89141A125D5A60EB369CD2A888E3C0F2724BF3",
        "40DE6ABADF79F9230EE643AEDD5C0A4ECCF60C7FC87B4967514A9FB121200F07",
        "불복하는 자에겐 위세로 저항심을 꺾고,\n따르는 자에겐 희망을 줘 분발하게 한다.\n그런 천하인의 성을 쌓는 것이다.",
        "불복/복종의 대비와 천하인의 성을 세운다는 결론을 원문 의미에 맞춘다.",
        "restore_contextual_three_lines",
        "위세 / 희망 / 천하인의 성이라는 원문의 세 문장 구조를 수동 3행으로 복원한다.",
        (888, 912, 744),
    ),
)


if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from build_common_message_overlay import message_invariants  # noqa: E402
from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")


def safe_resource(root: Path, relative: str | Path) -> Path:
    resolved_root = root.resolve(strict=True)
    path = (resolved_root / relative).resolve(strict=True)
    try:
        path.relative_to(resolved_root)
    except ValueError as exc:
        raise CandidateError(f"resource escapes configured root: {path}") from exc
    return path


def require_private(path: Path) -> Path:
    resolved = path.resolve()
    private_root = TMP_ROOT.resolve()
    try:
        resolved.relative_to(private_root)
    except ValueError as exc:
        raise CandidateError(f"private output escapes {private_root}: {resolved}") from exc
    return resolved


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise CandidateError(f"Nintendo Switch Korean reference is forbidden: {label}")
    return resolved


def candidate_ids() -> tuple[int, ...]:
    identifiers = tuple(candidate.identifier for candidate in CANDIDATES)
    require(identifiers == (3280, 4066, 5299, 6960, 7380, 8140, 8350), "Wave13 coordinate set differs")
    require(len(set(identifiers)) == len(identifiers), "Wave13 has duplicate coordinates")
    return identifiers


def protected_profile(value: str) -> dict[str, Any]:
    invariant = message_invariants(value)
    return {
        "esc": invariant["esc"],
        "printf": invariant["printf"],
        "unknown_percent_count": invariant["unknown_percent_count"],
        "controls": invariant["controls"],
        "pua": invariant["pua"],
        "leading_whitespace": invariant["leading_whitespace"],
        "trailing_whitespace": invariant["trailing_whitespace"],
        "runtime_tokens": RUNTIME_RE.findall(value),
    }


def linebreak_vector(value: str) -> tuple[str, ...]:
    return tuple(LINEBREAK_RE.findall(value))


def validate_target_text(candidate: Candidate, current: str) -> None:
    target = candidate.target
    require(text_sha256(current) == candidate.current_utf16le_sha256, f"{candidate.identifier}: current literal differs")
    require(text_sha256(target) == candidate.target_utf16le_sha256, f"{candidate.identifier}: target literal differs")
    require("\x00" not in target and "\ufffd" not in target, f"{candidate.identifier}: unsafe target character")
    require(KANA_OR_HAN_RE.search(target) is None, f"{candidate.identifier}: Japanese/CJK residue in target")
    require(protected_profile(current) == protected_profile(target), f"{candidate.identifier}: protected tag/token profile differs")
    require(not protected_profile(target)["esc"], f"{candidate.identifier}: unexpected colour tag")
    require(not protected_profile(target)["runtime_tokens"], f"{candidate.identifier}: unexpected runtime token")
    if candidate.linebreak_policy == "preserve_existing_breaks":
        require(linebreak_vector(current) == linebreak_vector(target), f"{candidate.identifier}: preserved line-break vector differs")
    elif candidate.linebreak_policy == "restore_contextual_three_lines":
        require(candidate.identifier in {7380, 8350}, f"{candidate.identifier}: unapproved new manual break")
        require(linebreak_vector(current) == (), f"{candidate.identifier}: current text is not collapsed")
        require(linebreak_vector(target) == ("\n", "\n"), f"{candidate.identifier}: restored break vector differs")
    else:
        raise CandidateError(f"{candidate.identifier}: unknown line-break policy {candidate.linebreak_policy!r}")


def load_event_font(steam_root: Path) -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    path = safe_resource(steam_root, FONT_RESOURCE)
    packed_sha256 = sha256_path(path)
    require(packed_sha256 == EXPECTED_FONT_SHA256, f"event font profile differs: {packed_sha256}")
    try:
        archive = parse_link(path.read_bytes())
        require(len(archive.entries) > FONT_OUTER_ENTRY, "event font outer entry is absent")
        _header, raw = decompress_wrapper(archive.entries[FONT_OUTER_ENTRY].data)
    except (IndexError, ValueError) as exc:
        raise CandidateError("event font entry cannot be unpacked") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_wave13_event_font_") as directory:
        font_path = Path(directory) / "event_font.g1n"
        font_path.write_bytes(raw)
        parsed = g1n.parse_g1n(font_path)
    require(not parsed.structural_errors, f"event font structure differs: {parsed.structural_errors[:1]}")
    require(len(parsed.tables) > FONT_TABLE, "event font table is absent")
    table = parsed.tables[FONT_TABLE]

    def advance(character: str) -> tuple[int, bool]:
        require(len(character) == 1, "font width requests must contain exactly one character")
        ordinal = table.mapping[ord(character)] if ord(character) < len(table.mapping) else 0
        if ordinal == 0:
            if KANA_OR_HAN_RE.fullmatch(character):
                return 48, True
            raise CandidateError(f"event font lacks glyph U+{ord(character):04X}")
        require(ordinal < len(table.records), f"event font ordinal is invalid for U+{ord(character):04X}")
        glyph = table.records[ordinal]
        require(glyph.width == glyph.advance and glyph.advance in (24, 48), f"event glyph metric differs for U+{ord(character):04X}")
        return glyph.advance, False

    return advance, {
        "resource": FONT_RESOURCE,
        "outer_entry": FONT_OUTER_ENTRY,
        "table": FONT_TABLE,
        "packed_sha256": packed_sha256,
    }


def measure_layout(value: str, advance: Callable[[str], tuple[int, bool]]) -> dict[str, Any]:
    lines = LINEBREAK_RE.sub("\n", value).split("\n")
    widths: list[int] = []
    fallback_codepoints: set[str] = set()
    for line in lines:
        width = 0
        cursor = 0
        while cursor < len(line):
            if line[cursor] == "\x1b":
                token = line[cursor : cursor + 3]
                require(ESC_RE.fullmatch(token) is not None, "malformed colour token")
                cursor += 3
                continue
            character = line[cursor]
            require(unicodedata.category(character) != "Cc", f"unexpected control U+{ord(character):04X}")
            glyph_width, fallback = advance(character)
            width += glyph_width
            if fallback:
                fallback_codepoints.add(f"U+{ord(character):04X}")
            cursor += 1
        widths.append(width)
    return {
        "line_count": len(lines),
        "line_widths_px": widths,
        "max_line_width_px": max(widths, default=0),
        "fallback_codepoints": sorted(fallback_codepoints),
    }


def opaque_header_digest(table: MessageTable) -> str:
    """Hash metadata bytes after masking only the required size/offset fields.

    Common-message rebuilds necessarily adjust the outer logical size and each
    string-offset entry after a text-length change.  Every other header/opaque
    byte before the string pool must remain identical.
    """

    prefix = bytearray(table.blob[: table.string_start])
    prefix[8:12] = b"\x00" * 4
    prefix[table.table_offset : table.string_start] = b"\x00" * (table.string_start - table.table_offset)
    return sha256_bytes(bytes(prefix))


def load_source(steam_root: Path) -> tuple[bytes, Any, bytes, MessageTable]:
    source = safe_resource(steam_root, RESOURCE)
    packed = source.read_bytes()
    require(sha256_bytes(packed) == EXPECTED_INPUT_PACKED_SHA256, "current Base-event packed preimage differs")
    require(len(packed) == EXPECTED_INPUT_PACKED_SIZE, "current Base-event packed size differs")
    header, raw = decompress_wrapper(packed)
    require(sha256_bytes(raw) == EXPECTED_INPUT_RAW_SHA256, "current Base-event raw preimage differs")
    require(len(raw) == EXPECTED_INPUT_RAW_SIZE, "current Base-event raw size differs")
    table = parse_message_table(raw)
    require(table.string_count == EXPECTED_STRING_COUNT, "current Base-event string count differs")
    require(rebuild_message_table(table, table.texts) == raw, "current Base-event source does not round-trip")
    return packed, header, raw, table


def validate_pristine_pc_japanese() -> dict[str, Any]:
    path = reject_switch_path(PRISTINE_PC_JP_PATH, "pristine Steam-PC Japanese")
    packed = path.read_bytes()
    require(sha256_bytes(packed) == EXPECTED_PRISTINE_PC_JP_SHA256, "pristine PC Japanese packed hash differs")
    header, raw = decompress_wrapper(packed)
    del header
    require(sha256_bytes(raw) == EXPECTED_PRISTINE_PC_JP_RAW_SHA256, "pristine PC Japanese raw hash differs")
    table = parse_message_table(raw)
    require(table.string_count == EXPECTED_STRING_COUNT, "pristine PC Japanese coordinate domain differs")
    evidence: dict[str, str] = {}
    for candidate in CANDIDATES:
        value = table.texts[candidate.identifier]
        require(text_sha256(value) == candidate.pristine_pc_jp_utf16le_sha256, f"{candidate.identifier}: pristine PC Japanese anchor differs")
        evidence[str(candidate.identifier)] = text_sha256(value)
    return {
        "platform": "Steam PC",
        "resource": str(path),
        "packed_sha256": sha256_bytes(packed),
        "raw_sha256": sha256_bytes(raw),
        "coordinate_utf16le_sha256": evidence,
        "switch_korean_translation_used": False,
    }


def build(steam_root: Path = DEFAULT_STEAM_ROOT) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    candidate_ids()
    steam_root = steam_root.resolve(strict=True)
    anchor_evidence = validate_pristine_pc_japanese()
    advance, font_evidence = load_event_font(steam_root)
    input_packed, header, input_raw, input_table = load_source(steam_root)
    final_texts = list(input_table.texts)
    rows: list[dict[str, Any]] = []
    preserved_current_maximums: list[int] = []

    for candidate in CANDIDATES:
        current = input_table.texts[candidate.identifier]
        validate_target_text(candidate, current)
        current_layout = measure_layout(current, advance)
        target_layout = measure_layout(candidate.target, advance)
        require(tuple(target_layout["line_widths_px"]) == candidate.expected_target_widths_px, f"{candidate.identifier}: target width contract differs")
        require(target_layout["line_count"] == len(candidate.expected_target_widths_px), f"{candidate.identifier}: target line count differs")
        require(1 <= target_layout["line_count"] <= MAX_LINES, f"{candidate.identifier}: target exceeds {MAX_LINES} lines")
        require(target_layout["max_line_width_px"] <= EMPIRICAL_BASE_EVENT_MAX_LINE_PX, f"{candidate.identifier}: target exceeds empirical Base-event width ceiling")
        require(not target_layout["fallback_codepoints"], f"{candidate.identifier}: target uses fallback glyphs")
        if candidate.linebreak_policy == "preserve_existing_breaks":
            preserved_current_maximums.append(current_layout["max_line_width_px"])

        final_texts[candidate.identifier] = candidate.target
        rows.append(
            {
                "schema": "nobu16.kr.pc-event-linebreak-wave13-audit.v1",
                "resource": RESOURCE,
                "id": candidate.identifier,
                "coordinate": str(candidate.identifier),
                "current_ko": current,
                "proposed_ko": candidate.target,
                "current_utf16le_sha256": text_sha256(current),
                "proposed_utf16le_sha256": text_sha256(candidate.target),
                "pristine_pc_jp_utf16le_sha256": candidate.pristine_pc_jp_utf16le_sha256,
                "semantic_rationale": candidate.semantic_rationale,
                "linebreak": {
                    "policy": candidate.linebreak_policy,
                    "rationale": candidate.linebreak_rationale,
                    "current_vector": list(linebreak_vector(current)),
                    "target_vector": list(linebreak_vector(candidate.target)),
                    "target_manual_line_count": target_layout["line_count"],
                },
                "protected_binary_text_profile": {
                    "current": protected_profile(current),
                    "target": protected_profile(candidate.target),
                    "preserved": protected_profile(current) == protected_profile(candidate.target),
                },
                "layout": {
                    "font": font_evidence,
                    "current": current_layout,
                    "target": target_layout,
                    "max_lines": MAX_LINES,
                    "empirical_base_event_max_line_px": EMPIRICAL_BASE_EVENT_MAX_LINE_PX,
                },
                "provenance": {
                    "pc_only": True,
                    "semantic_anchor": "pristine Steam-PC Japanese",
                    "switch_korean_translation_used": False,
                },
                "qa": {
                    "real_game_qa_required": True,
                    "status": "not_run",
                    "steam_game_resource_written": False,
                },
            }
        )

    require(max(preserved_current_maximums) == EMPIRICAL_BASE_EVENT_MAX_LINE_PX, "empirical Base-event width ceiling source differs")
    raw_a = rebuild_message_table(input_table, final_texts)
    raw_b = rebuild_message_table(input_table, final_texts)
    require(raw_a == raw_b, "Wave13 raw rebuild is not deterministic")
    require(sha256_bytes(raw_a) == EXPECTED_OUTPUT_RAW_SHA256, "Wave13 raw output hash differs")
    require(len(raw_a) == EXPECTED_OUTPUT_RAW_SIZE, "Wave13 raw output size differs")
    packed_a = recompress_wrapper(raw_a, header)
    packed_b = recompress_wrapper(raw_a, header)
    require(packed_a == packed_b, "Wave13 packed rebuild is not deterministic")
    require(sha256_bytes(packed_a) == EXPECTED_OUTPUT_PACKED_SHA256, "Wave13 packed output hash differs")
    require(len(packed_a) == EXPECTED_OUTPUT_PACKED_SIZE, "Wave13 packed output size differs")

    _checked_header, checked_raw = decompress_wrapper(packed_a)
    checked_table = parse_message_table(checked_raw)
    require(checked_raw == raw_a, "Wave13 packed output decompresses differently")
    require(checked_table.texts == tuple(final_texts), "Wave13 candidate parse differs")
    require(rebuild_message_table(checked_table, checked_table.texts) == checked_raw, "Wave13 candidate does not round-trip")
    require(opaque_header_digest(input_table) == opaque_header_digest(checked_table), "Wave13 changed opaque header bytes")
    changed_ids = tuple(
        identifier
        for identifier, (before, after) in enumerate(zip(input_table.texts, checked_table.texts))
        if before != after
    )
    require(changed_ids == candidate_ids(), f"Wave13 changed unexpected text cells: {changed_ids}")

    summary = {
        "schema": "nobu16.kr.pc-event-linebreak-wave13-summary.v1",
        "workstream": WORKSTREAM.name,
        "scope": {
            "resource": RESOURCE,
            "changed_files": 1,
            "changed_logical_records": len(CANDIDATES),
            "changed_ids": list(candidate_ids()),
            "linebreak_restored_ids": [7380, 8350],
        },
        "input": {
            "packed_sha256": sha256_bytes(input_packed),
            "packed_size": len(input_packed),
            "raw_sha256": sha256_bytes(input_raw),
            "raw_size": len(input_raw),
            "string_count": input_table.string_count,
        },
        "output": {
            "packed_sha256": sha256_bytes(packed_a),
            "packed_size": len(packed_a),
            "raw_sha256": sha256_bytes(raw_a),
            "raw_size": len(raw_a),
        },
        "semantic_anchor": anchor_evidence,
        "layout_contract": {
            "font": font_evidence,
            "max_target_lines": MAX_LINES,
            "empirical_base_event_max_line_px": EMPIRICAL_BASE_EVENT_MAX_LINE_PX,
            "preserved_manual_line_current_max_px": max(preserved_current_maximums),
            "target_widths_px": {str(row["id"]): row["layout"]["target"]["line_widths_px"] for row in rows},
        },
        "provenance": {
            "pc_only": True,
            "switch_korean_translation_used": False,
            "switch_korean_assets_read": False,
        },
        "output_policy": {
            "private_tmp_only_when_write_requested": True,
            "steam_game_resource_written": False,
            "steam_apply_capability": "absent",
            "git_stage_or_commit_written": False,
            "release_or_overlay_written": False,
        },
        "real_game_qa": {
            "required": True,
            "status": "not_run",
        },
    }
    return packed_a, summary, {"rows": rows, "input_opaque_header_digest": opaque_header_digest(input_table), "output_opaque_header_digest": opaque_header_digest(checked_table)}


def atomic_write(path: Path, payload: bytes) -> None:
    path = require_private(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def write_private(packed: bytes, summary: Mapping[str, Any], audit_payload: Mapping[str, Any], output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    output_root = require_private(output_root)
    audit_path = require_private(audit_path)
    manifest_path = require_private(manifest_path)
    if output_root.exists():
        raise CandidateError(f"refusing to overwrite private candidate directory: {output_root}")
    candidate_path = require_private(output_root / RESOURCE)
    atomic_write(candidate_path, packed)
    require(sha256_path(candidate_path) == EXPECTED_OUTPUT_PACKED_SHA256, "written private candidate hash differs")
    audit_bytes = canonical_json(audit_payload)
    atomic_write(audit_path, audit_bytes)
    manifest = {
        "schema": "nobu16.kr.pc-event-linebreak-wave13-build-manifest.v1",
        "workstream": WORKSTREAM.name,
        "candidate": {
            "relative_path": str(candidate_path.relative_to(TMP_ROOT)).replace("\\", "/"),
            "resource": RESOURCE,
            "packed_sha256": EXPECTED_OUTPUT_PACKED_SHA256,
            "packed_size": EXPECTED_OUTPUT_PACKED_SIZE,
        },
        "audit": {
            "relative_path": str(audit_path.relative_to(TMP_ROOT)).replace("\\", "/"),
            "sha256": sha256_bytes(audit_bytes),
        },
        "summary": dict(summary),
        "output_policy": dict(summary["output_policy"]),
    }
    manifest_bytes = canonical_json(manifest)
    atomic_write(manifest_path, manifest_bytes)
    return {
        "candidate": str(candidate_path),
        "audit": str(audit_path),
        "manifest": str(manifest_path),
        "audit_sha256": sha256_bytes(audit_bytes),
        "manifest_sha256": sha256_bytes(manifest_bytes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--write", action="store_true", help="write only private artefacts below the workstream tmp root")
    parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate-build-1")
    parser.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    parser.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    args = parser.parse_args()
    try:
        packed, summary, details = build(args.steam_root)
        audit = {
            "schema": "nobu16.kr.pc-event-linebreak-wave13-audit.v1",
            "summary": summary,
            "opaque_header_digest": {
                "input": details["input_opaque_header_digest"],
                "output": details["output_opaque_header_digest"],
                "preserved": details["input_opaque_header_digest"] == details["output_opaque_header_digest"],
            },
            "records": details["rows"],
        }
        written = write_private(packed, summary, audit, args.output_root, args.audit_path, args.manifest_path) if args.write else None
        print(json.dumps({
            "status": "ok",
            "input_sha256": EXPECTED_INPUT_PACKED_SHA256,
            "output_sha256": EXPECTED_OUTPUT_PACKED_SHA256,
            "changed_logical_records": len(CANDIDATES),
            "changed_ids": list(candidate_ids()),
            "steam_game_resource_written": False,
            "git_stage_or_commit_written": False,
            "private_outputs": written,
        }, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (CandidateError, OSError, ValueError, KeyError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
