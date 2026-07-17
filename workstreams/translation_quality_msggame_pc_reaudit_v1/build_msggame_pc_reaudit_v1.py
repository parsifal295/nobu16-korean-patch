#!/usr/bin/env python3
"""Freeze the PC-only residual ``pk_msggame`` semantic repairs.

The source authority is the pristine PC Japanese archive.  PC EN/SC/TC are
same-record corroboration only; current PC Korean is an exact before-text
gate.  This builder never opens the contaminated ``F:\\Games\\NOBU16\\MSG_PK\\SC``
file, a Switch resource, a historic Korean backup, a Steam-writing route, or
the generic overlay's Korean payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "translation_quality_msggame_pc_reaudit_v1"
OUTPUT = TMP / "pk_msggame_pc_reaudit_candidates.v1.jsonl"
VALIDATION = WORKSTREAM / "validation.v1.json"

TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(MSGGAME_TOOLS))

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    iter_literals,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
)


STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE = STEAM / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals"
RESOURCE = Path("MSG_PK") / "JP" / "msggame.bin"
SOURCE_PATHS = {
    "pristine_pc_jp": PRISTINE / RESOURCE,
    "current_pc_ko": STEAM / RESOURCE,
    "pc_en": STEAM / "MSG_PK" / "EN" / "msggame.bin",
    "pc_sc": STEAM / "MSG_PK" / "SC" / "msggame.bin",
    "pc_tc": STEAM / "MSG_PK" / "TC" / "msggame.bin",
}
EXPECTED_FILE_SHA256 = {
    "pristine_pc_jp": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "current_pc_ko": "DE606E50C9A6241BD0B85D17A000394007952093984F75DB56E296E0CCDE6B01",
    "pc_en": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "pc_sc": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "pc_tc": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}

SCHEMA = "nobu16.kr.pk-msggame-pc-reaudit.v1"
CANDIDATE_SCHEMA = "nobu16.kr.pk-msggame-pc-reaudit-candidate.v1"
VALIDATION_SCHEMA = "nobu16.kr.pk-msggame-pc-reaudit-validation.v1"
EXPECTED_CANDIDATE_COUNT = 30

RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")
SPACE_BRIDGE_COORDINATES = {"6:3846:1", "6:3847:1"}


class AuditError(ValueError):
    """A pinned PC-only audit invariant changed."""


@dataclass(frozen=True)
class Candidate:
    coordinate: str
    current: str
    proposed: str
    evidence_key: str

    @property
    def block_id(self) -> int:
        return int(self.coordinate.split(":")[0])

    @property
    def record_id(self) -> int:
        return int(self.coordinate.split(":")[1])

    @property
    def literal_id(self) -> int:
        return int(self.coordinate.split(":")[2])


# These are exact, record-context repairs.  Korean labels in this resource
# intentionally condense dynamic JP sentences into a state label; the source
# evidence is therefore checked at record level rather than by literal order.
CANDIDATES = (
    Candidate("6:1475:0", "이", ": 종속시킨 세력:", "subjugation_state"),
    Candidate("6:1476:0", "이", ": 신종 대상:", "submission_state"),
    Candidate("6:1477:0", ": 단교 상대:", ": 혼인 동맹 상대:", "marriage_alliance_state"),
    Candidate("6:1478:0", ": 단교 상대:", ": 혼인 동맹 상대:", "marriage_alliance_state"),
    Candidate("6:1480:0", "와", ": 단교 상대:", "severed_relations_state"),
    Candidate("6:1481:0", ": 정전 상대:", ": 단교 상대:", "severed_relations_state"),
    Candidate("6:1482:0", "이", ": 종속시킨 세력:", "subjugation_state"),
    Candidate("6:1487:0", ": 칙명에 따른 강화 상대:", ": 무기한 정전 상대:", "unlimited_truce_state"),
    Candidate("6:1488:0", ": 칙명에 따른 강화 상대:", ": 무기한 정전 상대:", "unlimited_truce_state"),
    Candidate("6:1489:0", ": 동맹 상대:", ": 칙명에 따른 강화 상대:", "imperial_peace_state"),
    Candidate("6:1490:0", ": 동맹 상대:", ": 칙명에 따른 강화 상대:", "imperial_peace_state"),
    Candidate("6:2125:2", ".", "의 원군에는 감사", "reinforcement_thanks"),
    Candidate("6:2126:2", ".", "의 원군에는 감사", "reinforcement_thanks"),
    Candidate("6:2127:2", ".", "의 원군에는 감사", "reinforcement_thanks"),
    Candidate("6:2131:2", ".", "의 원군에는 감사", "reinforcement_thanks"),
    Candidate("6:2137:2", ".", "의 원군에는 감사", "reinforcement_thanks"),
    Candidate("6:2138:2", ".", "의 원군에는 감사", "reinforcement_thanks"),
    Candidate("6:2139:2", ".", "의 원군에는 감사", "reinforcement_thanks"),
    Candidate("6:2143:2", ".", "의 원군에는 감사", "reinforcement_thanks"),
    Candidate("6:2733:1", ".", "의 뜻에 따를 이유는 없습니다.", "submission_has_limit"),
    Candidate("6:3108:1", ".", "에 입성했습니다.", "entered_castle"),
    Candidate("6:3109:2", ".", "에 입성했습니다.", "entered_castle"),
    Candidate("7:606:1", ".", "에 입성했습니다.", "entered_castle"),
    Candidate("7:607:2", ".", "에 입성했습니다.", "entered_castle"),
    Candidate("6:3733:0", "와", "에 대한 정전 기한이 만료됐습니다.", "truce_expired"),
    Candidate("6:3846:1", "의", "의 ", "construction_cancelled_space_bridge"),
    Candidate("6:3846:2", ".", "건설을 중단했습니다.", "construction_cancelled"),
    Candidate("6:3847:1", "의", "의 ", "construction_cancelled_space_bridge"),
    Candidate("6:3847:2", ".", "건설을 중단했습니다.", "construction_cancelled"),
    Candidate("15:1129:2", ".", "의 관계가 단절되었습니다.", "relations_severed_by_intrigue"),
)

# Exact pristine JP source checks.  EN/SC/TC are pinned, parsed, and checked
# for same record availability; JP remains the lexical authority.
JP_RECORD_MARKERS = {
    "6:1475": "を従属させる",
    "6:1476": "に臣従",
    "6:1477": "が婚姻同盟",
    "6:1478": "が婚姻同盟",
    "6:1480": "が手切",
    "6:1481": "が手切",
    "6:1482": "を従属させる",
    "6:1487": "無期限の停戦",
    "6:1488": "無期限の停戦",
    "6:1489": "勅命により講和",
    "6:1490": "勅命により講和",
    "6:2125": "の援軍には感謝",
    "6:2126": "の援軍には感謝",
    "6:2127": "の援軍には感謝",
    "6:2131": "の援軍には感謝",
    "6:2137": "の援軍には感謝",
    "6:2138": "の援軍には感謝",
    "6:2139": "の援軍には感謝",
    "6:2143": "の援軍には感謝",
    "6:2733": "に従う謂れはありません",
    "6:3108": "に入城",
    "6:3109": "に入城",
    "7:606": "に入城",
    "7:607": "に入城",
    "6:3733": "停戦は期限切れ",
    "6:3846": "を建設中止",
    "6:3847": "を建設中止",
    "15:1129": "が手切",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def coordinate_sort_key(coordinate: str) -> tuple[int, int, int]:
    pieces = coordinate.split(":")
    if len(pieces) != 3 or any(not piece.isdecimal() for piece in pieces):
        raise AuditError(f"invalid literal coordinate: {coordinate!r}")
    return tuple(int(piece) for piece in pieces)  # type: ignore[return-value]


def format_profile(value: str) -> dict[str, Any]:
    esc_offsets = {offset for match in ESC_RE.finditer(value) for offset in range(match.start(), match.end())}
    return {
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "escape_tags": ESC_RE.findall(value),
        "line_breaks": LINEBREAK_RE.findall(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "controls": [
            f"U+{ord(character):04X}"
            for index, character in enumerate(value)
            if ord(character) < 0x20 and character not in "\r\n" and index not in esc_offsets
        ],
    }


def format_delta(before: str, after: str) -> list[str]:
    before_profile = format_profile(before)
    after_profile = format_profile(after)
    return [key for key in before_profile if before_profile[key] != after_profile[key]]


def archive_records(archive: Any) -> dict[tuple[int, int], MsgGameRecord]:
    return {(record.block_id, record.record_id): record for block in archive.blocks for record in block.records}


def literal_texts(archive: Any) -> dict[str, str]:
    return {
        f"{literal.block_id}:{literal.record_id}:{literal.literal_id}": literal.text
        for literal in iter_literals(archive)
    }


def record_skeleton(record: MsgGameRecord) -> str:
    """Hash every marker/nonliteral byte while excluding UTF-16 literal payloads."""
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        output.extend(record.data[cursor : literal.marker_offset + 3])
        output.extend(b"<literal-text>")
        output.extend(record.data[literal.marker_end - 3 : literal.marker_end])
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return sha256_bytes(bytes(output))


def record_text(record: MsgGameRecord) -> str:
    return "".join(literal.text for literal in parse_record_literals(record))


def load_sources() -> tuple[dict[str, bytes], dict[str, Any]]:
    packed: dict[str, bytes] = {}
    archives: dict[str, Any] = {}
    for name, path in SOURCE_PATHS.items():
        if not path.is_file():
            raise AuditError(f"required PC source is absent: {path}")
        actual = sha256_file(path)
        if actual != EXPECTED_FILE_SHA256[name]:
            raise AuditError(f"PC source hash changed for {name}: {actual}")
        packed[name] = path.read_bytes()
        archives[name] = parse_packed_msggame(packed[name]).archive
    return packed, archives


def validate_source_context(archives: Mapping[str, Any]) -> None:
    source_records = {name: archive_records(archive) for name, archive in archives.items()}
    for candidate in CANDIDATES:
        record_key = (candidate.block_id, candidate.record_id)
        marker_key = f"{candidate.block_id}:{candidate.record_id}"
        marker = JP_RECORD_MARKERS.get(marker_key)
        if marker is None:
            raise AuditError(f"missing JP evidence marker for {candidate.coordinate}")
        for name, records in source_records.items():
            if record_key not in records:
                raise AuditError(f"same-record PC context is absent for {candidate.coordinate} in {name}")
        if marker not in record_text(source_records["pristine_pc_jp"][record_key]):
            raise AuditError(f"pristine JP evidence changed for {candidate.coordinate}")


def candidate_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    packed, archives = load_sources()
    validate_source_context(archives)
    current_archive = archives["current_pc_ko"]
    current = literal_texts(current_archive)
    records_before = archive_records(current_archive)

    coordinates = [candidate.coordinate for candidate in CANDIDATES]
    if len(CANDIDATES) != EXPECTED_CANDIDATE_COUNT or len(coordinates) != len(set(coordinates)):
        raise AuditError("candidate coordinate count or uniqueness changed")

    replacements: dict[tuple[int, int, int], str] = {}
    rows: list[dict[str, Any]] = []
    for candidate in sorted(CANDIDATES, key=lambda value: coordinate_sort_key(value.coordinate)):
        live = current.get(candidate.coordinate)
        if live != candidate.current:
            raise AuditError(f"current Korean literal differs at {candidate.coordinate}: {live!r}")
        delta = format_delta(live, candidate.proposed)
        expected_delta = ["trailing_whitespace"] if candidate.coordinate in SPACE_BRIDGE_COORDINATES else []
        if delta != expected_delta:
            raise AuditError(f"literal format contract changed at {candidate.coordinate}")
        replacements[(candidate.block_id, candidate.record_id, candidate.literal_id)] = candidate.proposed
        rows.append(
            {
                "schema": CANDIDATE_SCHEMA,
                "resource": "pk_msggame",
                "block_id": candidate.block_id,
                "record_id": candidate.record_id,
                "literal_id": candidate.literal_id,
                "coordinate": candidate.coordinate,
                "current_korean": candidate.current,
                "proposed_korean": candidate.proposed,
                "current_text_utf16le_sha256": sha256_text(candidate.current),
                "proposed_text_utf16le_sha256": sha256_text(candidate.proposed),
                "evidence_key": candidate.evidence_key,
                "allowed_format_delta": expected_delta,
                "format_contract": (
                    "paired_record_trailing_space_only" if expected_delta else
                    "literal_runtime_printf_esc_newline_edge_whitespace_unchanged"
                ),
            }
        )

    rebuilt = rebuild_packed_with_literals(packed["current_pc_ko"], replacements)
    rebuilt_archive = parse_packed_msggame(rebuilt).archive
    records_after = archive_records(rebuilt_archive)
    for record_key in {(candidate.block_id, candidate.record_id) for candidate in CANDIDATES}:
        if record_skeleton(records_before[record_key]) != record_skeleton(records_after[record_key]):
            raise AuditError(f"nonliteral bytecode changed at record {record_key}")

    source_free = {
        "schema": VALIDATION_SCHEMA,
        "candidate_count": len(rows),
        "coordinate_sha256": sha256_bytes("".join(f"{coordinate}\n" for coordinate in coordinates).encode("ascii")),
        "source_file_sha256": dict(EXPECTED_FILE_SHA256),
        "candidate_current_hashes": {row["coordinate"]: row["current_text_utf16le_sha256"] for row in rows},
        "candidate_proposed_hashes": {row["coordinate"]: row["proposed_text_utf16le_sha256"] for row in rows},
        "same_record_context": ["pristine_pc_jp", "pc_en", "pc_sc", "pc_tc", "current_pc_ko"],
        "contaminated_f_games_pk_sc_opened": False,
        "switch_korean_translation_used": False,
        "steam_game_resource_written": False,
        "nonliteral_bytecode_skeleton": "unchanged_for_each_edited_record",
        "literal_format_contract": "runtime_printf_esc_linebreak_edge_whitespace_unchanged_except_two_paired_trailing_spaces",
    }
    return rows, source_free


def write_outputs(rows: Iterable[Mapping[str, Any]], validation: Mapping[str, Any]) -> None:
    serialized_rows = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows).encode("utf-8")
    atomic_write(OUTPUT, serialized_rows)
    atomic_write(VALIDATION, canonical_json(validation))


def validate_outputs(rows: list[dict[str, Any]], validation: dict[str, Any]) -> None:
    if not OUTPUT.is_file() or not VALIDATION.is_file():
        raise AuditError("private candidate or source-free validation output is absent")
    expected_rows = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows).encode("utf-8")
    if OUTPUT.read_bytes() != expected_rows:
        raise AuditError("private candidate JSONL differs from regenerated PC-only audit")
    if VALIDATION.read_bytes() != canonical_json(validation):
        raise AuditError("source-free validation differs from regenerated PC-only audit")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write only tmp JSONL and source-free validation")
    parser.add_argument("--validate", action="store_true", help="verify regenerated outputs")
    args = parser.parse_args()
    if not args.write and not args.validate:
        parser.error("choose --write and/or --validate")
    rows, validation = candidate_rows()
    if args.write:
        write_outputs(rows, validation)
    if args.validate:
        validate_outputs(rows, validation)
    print(json.dumps({"candidate_count": len(rows), "steam_game_resource_written": False, "switch_korean_translation_used": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
