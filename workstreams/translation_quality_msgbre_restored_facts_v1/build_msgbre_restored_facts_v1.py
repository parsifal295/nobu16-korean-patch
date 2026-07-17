#!/usr/bin/env python3
"""Prepare one PC-only biography-fact restoration candidate.

The source authority is the pristine PC Japanese ``msgbre`` table.  PC
English, Simplified Chinese, and Traditional Chinese are corroborating
same-coordinate context.  Current PC Korean is only an exact before-text
gate.  No Switch Korean, historical Korean, or game-writing path is opened.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP = REPO / "tmp" / "translation_quality_msgbre_restored_facts_v1"
OUTPUT = TMP / "msgbre_restored_facts_candidates.v1.jsonl"
VALIDATION = WORKSTREAM / "validation.v1.json"

STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
ORIGINAL_ROOT = STEAM / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals"
RESOURCE = "MSG_PK/JP/msgbre.bin"

PC_PATHS = {
    "jp": ORIGINAL_ROOT / RESOURCE,
    "ko": STEAM / RESOURCE,
    "en": STEAM / RESOURCE.replace("/JP/", "/EN/"),
    "sc": STEAM / RESOURCE.replace("/JP/", "/SC/"),
    "tc": STEAM / RESOURCE.replace("/JP/", "/TC/"),
}
EXPECTED_FILE_SHA256 = {
    "jp": "945A0E9157E2DBD12781FFA5A986D93681325F40B6486348B1AB311D3BEE1D6D",
    "ko": "C545CD2251E61AEB0A68E10A08ADFFCD3B150C32B5D15236D90727A305B03BAE",
    "en": "97AF6A9CCB7D49C1325A92F6C83B88AA26511B7AE2CB0ABB7C6E0B38AB368945",
    "sc": "D0DDE32C6BE9C81BA91D210BC62BC3E552121A9D7E493D53B461641FABAA499E",
    "tc": "F4A39E2FFD0DB4FBDE416E20B387DA629D87905E127C4421166751E3650D4A11",
}
CANDIDATE_SPECS: dict[int, dict[str, Any]] = {
    720: {
        "expected_current_sha256": "E762C24A462492A254D2D09FCE85B641711839578F699EA254F507523B282D94",
        "expected_proposed_sha256": "874174835485184173CC0F66220A5407AAA09594E6C102466FAFA6937AE39DA4",
        "proposed": (
            "오토모 요시나가의 둘째 아들. 명문 히고 기쿠치 가문을 이었다. "
            "오우치 가문과 함께 형 요시아키에게 맞섰으나 패했고, 뒤에 오토모 가문의 "
            "가독을 이은 조카 소린의 모략으로 살해되었다."
        ),
        "required_markers": {
            "jp": ("大友家の家督を継いだ甥・宗麟", "宗麟の謀略", "討たれた"),
            "en": ("his nephew, Sªrin, heir of the ¥tomo", "killed"),
            "sc": ("侄子宗麟继承大友家家督之位", "宗麟的设计", "被杀害"),
            "tc": ("繼承大友家家督", "宗麟", "計策", "被討伐"),
        },
        "rationale": (
            "Pristine PC JP explicitly says that the nephew Sōrin inherited the Ōtomo headship "
            "and had the subject killed by stratagem. PC SC/TC retain both facts and PC EN retains "
            "the nephew-heir fact; current Korean compresses them to a bare killing."
        ),
        "evidence_key": "succession_and_stratagem",
    },
    768: {
        "expected_current_sha256": "927F1B3A2F2B47B4D9AE5F6D37DB1C0C33BA9EDF6F5598DE6F65FD98E0BB547A",
        "expected_proposed_sha256": "F4A90C84600EC113D30BBD840399C13A465386FB30A7C2E8FBEB600BC09D97B7",
        "proposed": (
            "시마즈 가신. 기모쓰키 가네모리의 아들이다. 이주인 다다무네가 죽은 뒤 "
            "주가의 허락을 받아 기모쓰키 가문의 명적을 다시 이었다. 뒤에 쇼나이의 난 "
            "진압에 공을 세우고, 말년에는 류큐 출병에도 참여했다."
        ),
        "required_markers": {
            "jp": ("主家の許しを得て", "肝付家の名跡に返り咲く", "庄内の乱鎮圧に功績", "晩年", "琉球への出兵にも参加"),
            "en": ("let him revitalize the Kimotsuki name", "put down the Shªnai uprising", "fought in Ry¨ky¨"),
            "sc": ("取得主家允许", "恢复肝付家之名", "庄内镇压内乱立功", "晚年", "出兵琉球"),
            "tc": ("取得主家的允許", "恢復肝付家的名聲", "庄內鎮壓內亂", "晚年", "參與出兵琉球"),
        },
        "rationale": (
            "Pristine PC JP distinguishes permission to resume the Kimotsuki family name, merit in "
            "suppressing the Shōnai Rebellion, and participation in the later Ryūkyū expedition. "
            "PC SC/TC retain all four facts, while current Korean changes or compresses them."
        ),
        "evidence_key": "permission_lineage_merit_and_ryukyu_expedition",
    },
}

RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)


class AuditError(ValueError):
    """A PC-only evidence or format gate changed."""


sys.path.insert(0, str(TOOLS))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


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


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def format_profile(value: str) -> dict[str, Any]:
    return {
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "escape_tokens": ESC_RE.findall(value),
        "line_breaks": re.findall(r"\r\n|\n|\r", value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
    }


def parse_table(label: str) -> tuple[tuple[str, ...], str]:
    path = PC_PATHS[label]
    if not path.is_file():
        raise AuditError(f"missing PC {label} resource: {path}")
    packed_hash = sha256_file(path)
    if packed_hash != EXPECTED_FILE_SHA256[label]:
        raise AuditError(f"PC {label} resource hash differs")
    _header, raw = decompress_wrapper(path.read_bytes())
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise AuditError(f"PC {label} unchanged table rebuild differs")
    if len(table.texts) != 3000:
        raise AuditError(f"PC {label} table count differs")
    return table.texts, packed_hash


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tables: dict[str, tuple[str, ...]] = {}
    hashes: dict[str, str] = {}
    for label in ("jp", "ko", "en", "sc", "tc"):
        tables[label], hashes[label] = parse_table(label)
    rows: list[dict[str, Any]] = []
    for entry_id, spec in sorted(CANDIDATE_SPECS.items()):
        source = tables["jp"][entry_id]
        current = tables["ko"][entry_id]
        english = tables["en"][entry_id]
        simplified = tables["sc"][entry_id]
        traditional = tables["tc"][entry_id]
        proposed = spec["proposed"]
        if not isinstance(proposed, str):
            raise AuditError(f"candidate proposal is invalid: {entry_id}")
        current_hash = sha256_text(current)
        proposed_hash = sha256_text(proposed)
        expected_current = spec["expected_current_sha256"]
        expected_proposed = spec["expected_proposed_sha256"]
        if not isinstance(expected_current, str) or (expected_current and current_hash != expected_current):
            raise AuditError(f"current PC Korean text hash differs: {entry_id}")
        if not isinstance(expected_proposed, str) or (expected_proposed and proposed_hash != expected_proposed):
            raise AuditError(f"reviewed proposed Korean text hash differs: {entry_id}")
        if format_profile(current) != format_profile(proposed):
            raise AuditError(f"candidate changes a protected format field: {entry_id}")
        references = {"jp": source, "en": english, "sc": simplified, "tc": traditional}
        required_markers = spec["required_markers"]
        if not isinstance(required_markers, dict):
            raise AuditError(f"candidate marker contract is invalid: {entry_id}")
        for label, markers in required_markers.items():
            if not isinstance(markers, tuple) or not all(marker in references[label] for marker in markers):
                raise AuditError(f"PC {label} corroborating source marker differs: {entry_id}")
        evidence_key = spec["evidence_key"]
        if not isinstance(evidence_key, str) or not evidence_key:
            raise AuditError(f"candidate evidence key is invalid: {entry_id}")
        rationale = spec["rationale"]
        if not isinstance(rationale, str) or not rationale:
            raise AuditError(f"candidate rationale is invalid: {entry_id}")
        rows.append(
            {
                "schema": "nobu16.kr.msgbre-restored-facts.pc-only.v1",
                "review_batch": "msgbre_restored_facts_v1",
                "record_type": "candidate",
                "resource": RESOURCE,
                "id": entry_id,
                "source_japanese": source,
                "source_japanese_utf16le_sha256": sha256_text(source),
                "current_korean": current,
                "current_korean_utf16le_sha256": current_hash,
                "proposed_korean": proposed,
                "proposed_korean_utf16le_sha256": proposed_hash,
                "format_profile": format_profile(current),
                "pc_references": {"en": english, "sc": simplified, "tc": traditional},
                "pc_file_sha256": hashes,
                "pc_evidence_key": evidence_key,
                "rationale": rationale,
                "switch_korean_translation_used": False,
                "historic_korean_translation_used": False,
                "steam_game_resource_written": False,
                "generic_builder_changed": False,
                "release_or_commit_created": False,
            }
        )
    coordinates = [row["id"] for row in rows]
    source_free = {
        "schema": "nobu16.kr.msgbre-restored-facts.validation.v1",
        "resource": RESOURCE,
        "candidate_count": len(rows),
        "candidate_coordinates": coordinates,
        "candidate_private_jsonl": str(OUTPUT.relative_to(REPO)).replace("\\", "/"),
        "candidate_private_jsonl_sha256": sha256_bytes(private_payload(rows)),
        "pc_file_sha256": hashes,
        "format_profile_preserved": True,
        "pc_jp_en_sc_tc_marker_contracts_verified": True,
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "steam_game_resource_written": False,
        "generic_builder_changed": False,
        "release_or_commit_created": False,
    }
    return rows, source_free


def private_payload(rows: list[dict[str, Any]]) -> bytes:
    return ("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)).encode("utf-8")


def validate_written(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    expected_private = private_payload(rows)
    expected_summary = canonical_json(summary)
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected_private:
        raise AuditError("private candidate output differs from deterministic rebuild")
    if not VALIDATION.is_file() or VALIDATION.read_bytes() != expected_summary:
        raise AuditError("source-free validation differs from deterministic rebuild")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    try:
        rows, summary = build()
        if args.write:
            atomic_write(OUTPUT, private_payload(rows))
            atomic_write(VALIDATION, canonical_json(summary))
        if args.validate:
            validate_written(rows, summary)
        print(
            json.dumps(
                {
                    "candidate_count": len(rows),
                    "candidate_coordinates": [row["id"] for row in rows],
                    "steam_game_resource_written": False,
                    "switch_korean_translation_used": False,
                },
                ensure_ascii=False,
            )
        )
        return 0
    except (AuditError, OSError, ValueError, KeyError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
