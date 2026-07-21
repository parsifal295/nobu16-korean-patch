#!/usr/bin/env python3
"""Build a current-Steam B17 spacing and grammar repair candidate.

This is a narrow, evidence-backed repair for visible Korean text in MSGGAME
block 17.  It fixes missing spaces at literal boundaries and two clear Korean
case-particle errors.  It preserves message bytecode, runtime tokens, manual
line feeds, and all unselected literals.  ``build`` writes candidates only
under this workstream's ignored ``private`` directory; it never writes Steam.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BASE_JP = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
PK_JP = (
    Path(r"F:\Games\NOBU16\KR_PATCH_BACKUP")
    / "file_only_transaction"
    / "jp-runtime-wave05-20260715-v1"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
FORMAT_PATH = REPO / "workstreams" / "msggame" / "msggame_format.py"

PUBLIC_PATH = WORKSTREAM / "public" / "pc_dialogue_b17_spacing_grammar.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
REPORT_PATH = WORKSTREAM / "REPORT_KO.md"
PRIVATE_REVIEW_PATH = WORKSTREAM / "private" / "pc_dialogue_b17_spacing_grammar.review.v1.json"
PRIVATE_CANDIDATE_ROOT = WORKSTREAM / "private" / "candidate"

BLOCK_ID = 17
RESOURCE_SPECS = {
    "MSG/JP/msggame.bin": {
        "source": STEAM_ROOT / "MSG" / "JP" / "msggame.bin",
        "source_sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "jp": BASE_JP,
        "jp_sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    },
    "MSG_PK/JP/msggame.bin": {
        "source": STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        "source_sha256": "37782D6E96CC6E9C1D60AF50FA5A68AD7C7CC8BE724CEF85EE2E38F2D074B0A7",
        "jp": PK_JP,
        "jp_sha256": "0FB9EA3B4817D208C65F587AF1F57A5BB82106367314801A13C9A534ECC47CD8",
    },
}


@dataclass(frozen=True)
class LiteralFix:
    resource: str
    record_id: int
    literal_id: int
    before: str
    after: str
    rationale: str


# Every source literal below is pinned against the current Steam W102 profile.
# Changes are deliberately local to the literal that owns the Korean spacing or
# case particle; runtime opcode fields and color/name-token topology stay put.
FIXES: tuple[LiteralFix, ...] = (
    LiteralFix("MSG/JP/msggame.bin", 13, 0, "알겠소! 소인도", "알겠소! 소인도 ", "name-boundary space"),
    LiteralFix("MSG/JP/msggame.bin", 13, 2, "일문의 말석으로서\n대임, 훌륭히 완수해 보이겠소이다", " 일문의 말석으로서\n대임을 훌륭히 완수해 보이겠소이다", "name boundary and object particle"),
    LiteralFix("MSG_PK/JP/msggame.bin", 13, 0, "알겠소! 소인도", "알겠소! 소인도 ", "name-boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 13, 2, "일문의 말석으로서\n대임, 훌륭히 완수해 보이겠소이다", " 일문의 말석으로서\n대임을 훌륭히 완수해 보이겠소이다", "name boundary and object particle"),
    LiteralFix("MSG_PK/JP/msggame.bin", 43, 0, "총대장", "총대장 ", "title-name boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 44, 0, "총대장", "총대장 ", "title-name boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 48, 0, "남은 것은", "남은 것은 ", "name-boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 80, 0, "다케다", "다케다 ", "compound-name boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 80, 1, "기마대… 무시무시한 기세로군!\n우리", "기마대… 무시무시한 기세로군!\n우리 ", "name-boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 92, 0, "더는 유인할 상황이 아닌가…\n하지만 우세한 것은 변함없다!", "더는 유인할 상황이 아닌가…\n하지만 우세한 것은 변함없다! ", "name-boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 109, 0, "됐다,", "됐다, ", "name-boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 109, 2, "군을 격파하는 데 성공했다\n이제는", "군을 격파하는 데 성공했다\n이제는 ", "name-boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 115, 0, "나의", "우리 ", "natural possessive construction"),
    LiteralFix("MSG_PK/JP/msggame.bin", 115, 2, "의 상경을\n", "의 상경이\n", "subject particle for passive construction"),
    LiteralFix("MSG_PK/JP/msggame.bin", 115, 3, "도쿠가와", "도쿠가와 ", "dependent-noun boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 118, 1, "군은", "군은 ", "place-name boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 118, 3, "앞에서 진군을 멈췄습니다\n", " 앞에서 진군을 멈췄습니다\n", "place-name boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 119, 0, "하지만,", "하지만, ", "name-boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 939, 2, "을 빼앗았다!\n이제 주군을 구할 수 있겠군!", "를 빼앗았다!\n이제 주군을 구할 수 있겠군!", "Korean object particle"),
    LiteralFix("MSG_PK/JP/msggame.bin", 943, 0, "이것으로", "이것으로 ", "place-name boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 944, 0, "이것으로", "이것으로 ", "place-name boundary space"),
    LiteralFix("MSG_PK/JP/msggame.bin", 965, 0, "역시", "역시 ", "name-boundary space before runtime record"),
    LiteralFix("MSG_PK/JP/msggame.bin", 981, 3, "을 사수하라!", "를 사수하라!", "Korean object particle"),
    LiteralFix("MSG_PK/JP/msggame.bin", 1024, 0, "이 병력으로 질 리 없다\n오늘이야말로", "이 병력으로 질 리 없다\n오늘이야말로 ", "castle-name boundary space"),
)


class RepairError(RuntimeError):
    """Raised when an input or structure no longer matches this repair."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RepairError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any, *, source_free: bool = False) -> bytes:
    return (
        json.dumps(value, ensure_ascii=source_free, indent=2, sort_keys=True) + "\n"
    ).encode("ascii" if source_free else "utf-8")


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


def load_format() -> Any:
    spec = importlib.util.spec_from_file_location("b17_spacing_msggame_format", FORMAT_PATH)
    require(spec is not None and spec.loader is not None, "cannot load MSGGAME format helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


FORMAT = load_format()


def opaque_skeleton(record: Any) -> bytes:
    cursor = 0
    output: list[bytes] = []
    for literal in FORMAT.parse_record_literals(record):
        output.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    output.append(record.data[cursor:])
    return b"".join(output)


def by_resource() -> Mapping[str, tuple[LiteralFix, ...]]:
    grouped: dict[str, list[LiteralFix]] = {relative: [] for relative in RESOURCE_SPECS}
    for fix in FIXES:
        grouped[fix.resource].append(fix)
    require(all(grouped.values()), "a resource has no fixes")
    for relative, rows in grouped.items():
        coordinates = [(item.record_id, item.literal_id) for item in rows]
        require(len(coordinates) == len(set(coordinates)), f"duplicate fix coordinate: {relative}")
    return {relative: tuple(rows) for relative, rows in grouped.items()}


def load_source(relative: str) -> tuple[bytes, Any, Any]:
    spec = RESOURCE_SPECS[relative]
    packed = Path(spec["source"]).read_bytes()
    require(sha256_bytes(packed) == spec["source_sha256"], f"current Steam source SHA differs: {relative}")
    parsed = FORMAT.parse_packed_msggame(packed)
    raw = FORMAT.rebuild_raw_msggame(parsed.archive)
    _header, original_raw = FORMAT.decompress_wrapper(packed)
    require(raw == original_raw, f"source parse/rebuild differs: {relative}")
    jp = Path(spec["jp"]).read_bytes()
    require(sha256_bytes(jp) == spec["jp_sha256"], f"direct JP source SHA differs: {relative}")
    jp_archive = FORMAT.parse_packed_msggame(jp).archive
    return packed, parsed.archive, jp_archive


def build_resource(relative: str, rows: tuple[LiteralFix, ...]) -> tuple[bytes, list[dict[str, Any]]]:
    packed, archive, jp_archive = load_source(relative)
    replacements: dict[tuple[int, int, int], str] = {}
    private_rows: list[dict[str, Any]] = []
    for fix in rows:
        record = archive.blocks[BLOCK_ID].records[fix.record_id]
        jp_record = jp_archive.blocks[BLOCK_ID].records[fix.record_id]
        literals = FORMAT.parse_record_literals(record)
        jp_literals = FORMAT.parse_record_literals(jp_record)
        require(len(literals) == len(jp_literals), f"JP/Korean literal topology differs: {relative}@{fix.record_id}")
        require(opaque_skeleton(record) == opaque_skeleton(jp_record), f"JP/Korean bytecode differs: {relative}@{fix.record_id}")
        require(fix.literal_id < len(literals), f"missing literal: {relative}@{fix.record_id}:{fix.literal_id}")
        require(literals[fix.literal_id].text == fix.before, f"current text differs: {relative}@{fix.record_id}:{fix.literal_id}")
        require(fix.before != fix.after, f"no-op fix: {relative}@{fix.record_id}:{fix.literal_id}")
        require(fix.before.count("\n") == fix.after.count("\n"), f"line-break topology differs: {relative}@{fix.record_id}:{fix.literal_id}")
        replacements[(BLOCK_ID, fix.record_id, fix.literal_id)] = fix.after
        private_rows.append(
            {
                "resource": relative,
                "block_id": BLOCK_ID,
                "record_id": fix.record_id,
                "literal_id": fix.literal_id,
                "before": fix.before,
                "after": fix.after,
                "direct_jp_utf16le_sha256": text_sha256(jp_literals[fix.literal_id].text),
                "rationale": fix.rationale,
            }
        )
    candidate = FORMAT.rebuild_packed_with_literals(packed, replacements)
    parsed_candidate = FORMAT.parse_packed_msggame(candidate).archive
    changed_records = {(BLOCK_ID, fix.record_id) for fix in rows}
    selected = {(BLOCK_ID, fix.record_id, fix.literal_id) for fix in rows}
    for before_block, after_block in zip(archive.blocks, parsed_candidate.blocks, strict=True):
        require(len(before_block.records) == len(after_block.records), f"record count differs: {relative}@{before_block.block_id}")
        for before_record, after_record in zip(before_block.records, after_block.records, strict=True):
            coordinate = (before_record.block_id, before_record.record_id)
            if coordinate not in changed_records:
                require(before_record.data == after_record.data, f"unselected record changed: {relative}@{coordinate}")
                continue
            require(opaque_skeleton(before_record) == opaque_skeleton(after_record), f"bytecode changed: {relative}@{coordinate}")
            before_literals = FORMAT.parse_record_literals(before_record)
            after_literals = FORMAT.parse_record_literals(after_record)
            require(len(before_literals) == len(after_literals), f"literal topology changed: {relative}@{coordinate}")
            for before_literal, after_literal in zip(before_literals, after_literals, strict=True):
                key = (BLOCK_ID, before_record.record_id, before_literal.literal_id)
                if key in selected:
                    expected = replacements[key]
                    require(after_literal.text == expected, f"selected literal differs: {relative}@{key}")
                else:
                    require(before_literal.text == after_literal.text, f"unselected literal changed: {relative}@{key}")
    return candidate, private_rows


def build_model() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, bytes]]:
    grouped = by_resource()
    candidates: dict[str, bytes] = {}
    private_rows: list[dict[str, Any]] = []
    resources: dict[str, Any] = {}
    for relative, rows in grouped.items():
        candidate, review = build_resource(relative, rows)
        source = Path(RESOURCE_SPECS[relative]["source"]).read_bytes()
        candidates[relative] = candidate
        private_rows.extend(review)
        resources[relative] = {
            "source": {"sha256": sha256_bytes(source), "size": len(source)},
            "target": {"sha256": sha256_bytes(candidate), "size": len(candidate)},
            "operation_count": len(rows),
            "operations": [
                {
                    "block_id": BLOCK_ID,
                    "record_id": fix.record_id,
                    "literal_id": fix.literal_id,
                    "before_utf16le_sha256": text_sha256(fix.before),
                    "after_utf16le_sha256": text_sha256(fix.after),
                    "line_break_count_preserved": fix.before.count("\n") == fix.after.count("\n"),
                }
                for fix in rows
            ],
        }
    require(len(private_rows) == len(FIXES) == 24, "repair scope count differs")
    public = {
        "schema": "nobu16.kr.pc-dialogue-b17-spacing-grammar.v1",
        "source_free": True,
        "scope": {
            "block_id": BLOCK_ID,
            "record_count": len({(fix.resource, fix.record_id) for fix in FIXES}),
            "literal_count": len(FIXES),
            "runtime_bytecode_changed": False,
            "manual_linebreaks_changed": False,
            "steam_game_resource_written": False,
        },
        "resources": resources,
    }
    require(canonical_json(public, source_free=True).isascii(), "public artifact contains source text")
    private = {"schema": "nobu16.kr.pc-dialogue-b17-spacing-grammar-private.v1", "rows": private_rows}
    validation = {
        "schema": "nobu16.kr.pc-dialogue-b17-spacing-grammar-validation.v1",
        "status": "PASS",
        "literal_count": len(FIXES),
        "record_count": len({(fix.resource, fix.record_id) for fix in FIXES}),
        "proofs": {
            "current_steam_source_hashes_pinned": True,
            "direct_pc_jp_structure_matched": True,
            "opaque_bytecode_preserved": True,
            "linebreak_topology_preserved": True,
            "unselected_records_preserved": True,
            "steam_game_resource_written": False,
        },
    }
    return public, private, validation, candidates


def report(validation: Mapping[str, Any]) -> bytes:
    return (
        "# B17 인물 대사 공백·조사 보정\n\n"
        "현재 Steam PC B17의 실제 리터럴 경계를 원문 구조와 대조해, 이름 앞뒤 공백 누락과 "
        "`퇴로을` 같은 조사 오류만 고쳤다. 문장 축약·수동 개행 재배치·런타임 바이트코드 변경은 하지 않는다.\n\n"
        f"- 수정 리터럴: {validation['literal_count']}개\n"
        f"- 수정 레코드: {validation['record_count']}개\n"
        "- Base와 PK MSGGAME만 후보로 생성하며 Steam 설치 파일은 쓰지 않는다.\n"
    ).encode("utf-8")


def payloads(public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any]) -> Mapping[Path, bytes]:
    return {
        PUBLIC_PATH: canonical_json(public, source_free=True),
        PRIVATE_REVIEW_PATH: canonical_json(private),
        VALIDATION_PATH: canonical_json(validation, source_free=True),
        REPORT_PATH: report(validation),
    }


def write_outputs(public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any], candidates: Mapping[str, bytes]) -> None:
    for path, payload in payloads(public, private, validation).items():
        atomic_write(path, payload)
    for relative, blob in candidates.items():
        atomic_write(PRIVATE_CANDIDATE_ROOT / relative, blob)


def verify_outputs(public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any], candidates: Mapping[str, bytes]) -> None:
    for path, payload in payloads(public, private, validation).items():
        require(path.is_file() and path.read_bytes() == payload, f"generated output differs: {path}")
    for relative, blob in candidates.items():
        path = PRIVATE_CANDIDATE_ROOT / relative
        require(path.is_file() and path.read_bytes() == blob, f"candidate differs: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify"))
    args = parser.parse_args()
    try:
        public, private, validation, candidates = build_model()
        if args.command == "build":
            write_outputs(public, private, validation, candidates)
        elif args.command == "verify":
            verify_outputs(public, private, validation, candidates)
    except (OSError, ValueError, RepairError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "PASS", "literal_count": validation["literal_count"], "steam_game_resource_written": False}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
