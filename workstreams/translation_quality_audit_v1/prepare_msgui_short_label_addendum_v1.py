#!/usr/bin/env python3
"""Emit narrowly-scoped, source-gated msgui short-label repairs.

This audit reads only pristine PC Japanese, the installed Steam PC Korean
target, and the installed PC EN/SC/TC references.  It never reads Switch
Korean or historic Korean backups, and --write writes a review JSONL below
tmp only; it does not modify any game resource.
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


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BACKUP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
TMP_ROOT = REPO / "tmp"
OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgui_short_label_addendum.v1.jsonl"
)

PRISTINE_JP = BACKUP / "MSG_PK" / "JP" / "msgui.bin"
LIVE_KO = STEAM / "MSG_PK" / "JP" / "msgui.bin"
REFERENCES = {
    language.lower(): STEAM / "MSG_PK" / language / "msgui.bin"
    for language in ("EN", "SC", "TC")
}

# Both IDs are Japanese ``\u4e88\u5099`` (reserve), while their Korean text has
# been displaced from later map-confirmation strings.  ID 3749 is the adjacent
# same-source anchor and already renders the intended Korean label.
TARGETS = {
    3747: "\uc18c\ub839 \uc548\ub3c4\ud560 \uc601\uc9c0\ub97c \uc9c0\ub3c4\uc5d0\uc11c \ud655\uc778\ud569\ub2c8\ub2e4.",
    3748: "\uc18c\uc18d\ub418\uae30\ub97c \ud76c\ub9dd\ud558\ub294 \uc131\uc744 \uc9c0\ub3c4\uc5d0\uc11c \ud655\uc778\ud569\ub2c8\ub2e4.",
}
SOURCE_TEXT = "\u4e88\u5099"
PROPOSED_KO = "\uc608\ube44"
ANCHOR_ID = 3749

sys.path.insert(0, str(REPO / "tools"))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
JAPANESE_OR_CJK_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff"
    r"\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load_msgui(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def format_profile(text: str) -> dict[str, object]:
    return {
        "escape_tags": ESC_RE.findall(text),
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "newlines": re.findall(r"\r\n|\n|\r", text),
        "outer_ascii_whitespace": [
            text[: len(text) - len(text.lstrip(" \t"))],
            text[len(text.rstrip(" \t")) :],
        ],
        "private_use": PRIVATE_USE_RE.findall(text),
        "fullwidth_percent_count": text.count("\uff05"),
        "question_mark_count": text.count("?"),
    }


def candidate_files() -> list[Path]:
    audit = TMP_ROOT / "translation_quality_audit_v1"
    paths = list((audit / "semantic").glob("msgui*.jsonl"))
    paths += list((audit / "proposals").glob("msgui*.jsonl"))
    return sorted({path.resolve() for path in paths if path.resolve() != OUTPUT.resolve()})


def assert_not_already_proposed(ids: set[int]) -> None:
    duplicate_locations: list[str] = []
    for path in candidate_files():
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            values = (row.get("id"), row.get("coordinate"))
            for target_id in ids:
                if target_id in values or str(target_id) in values:
                    duplicate_locations.append(f"{path}:{line_number}")
    if duplicate_locations:
        raise ValueError("target ID already exists in msgui candidate files: " + ", ".join(duplicate_locations))


def safe_output(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output must stay under {root}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    jp = load_msgui(PRISTINE_JP)
    ko = load_msgui(LIVE_KO)
    references = {language: load_msgui(path) for language, path in REFERENCES.items()}
    if len(jp) != len(ko) or any(len(table) != len(jp) for table in references.values()):
        raise ValueError("PC msgui table cardinalities differ")
    if not all(0 <= target_id < len(jp) for target_id in TARGETS):
        raise ValueError("target ID is outside the msgui table")
    assert_not_already_proposed(set(TARGETS))

    if jp[ANCHOR_ID] != SOURCE_TEXT or ko[ANCHOR_ID] != PROPOSED_KO:
        raise ValueError("same-source Korean anchor at ID 3749 changed")

    pristine_hash = sha256_file(PRISTINE_JP)
    live_hash = sha256_file(LIVE_KO)
    reference_hashes = {language: sha256_file(path) for language, path in REFERENCES.items()}
    rows: list[dict[str, object]] = []
    for target_id, expected_current in TARGETS.items():
        source = jp[target_id]
        current = ko[target_id]
        if source != SOURCE_TEXT:
            raise ValueError(f"{target_id}: pristine Japanese source gate failed: {source!r}")
        if current != expected_current:
            raise ValueError(f"{target_id}: current Korean target gate failed: {current!r}")
        source_profile = format_profile(source)
        current_profile = format_profile(current)
        proposed_profile = format_profile(PROPOSED_KO)
        if current_profile != proposed_profile or source_profile != proposed_profile:
            raise ValueError(f"{target_id}: source/current/proposed format profiles differ")
        if not HANGUL_RE.search(PROPOSED_KO) or JAPANESE_OR_CJK_RE.search(PROPOSED_KO):
            raise ValueError(f"{target_id}: invalid proposed Korean label")
        if "\ufffd" in PROPOSED_KO or "??" in PROPOSED_KO:
            raise ValueError(f"{target_id}: corruption marker in proposed label")
        rows.append(
            {
                "resource": "msgui",
                "coordinate": str(target_id),
                "id": target_id,
                "ko": current,
                "proposed_ko": PROPOSED_KO,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "live_ko_file_sha256": live_hash,
                "pristine_jp_file_sha256": pristine_hash,
                "reference_file_sha256": reference_hashes,
                "issue_type": "short_label_coordinate_drift",
                "rationale": (
                    "\uc77c\ubcf8\uc5b4 \uc6d0\ubb38\uc774 \ub3d9\uc77c\ud55c \ub2e8\ubb38 \ub77c\ubca8 \u2018\uc608\ube44\u2019\uc778\ub370, "
                    "\ud604\uc7ac \ud55c\uad6d\uc5b4\ub294 \ub4a4 \uc88c\ud45c\uc758 \uc9c0\ub3c4 \ud655\uc778 \uc548\ub0b4\ubb38\uc774 \uc798\ubabb \ubc30\uce58\ub41c "
                    "\uc88c\ud45c \ubc00\ub9bc\uc774\ub2e4. \uc778\uc811\ud55c ID 3749\ub3c4 \ub3d9\uc77c \uc6d0\ubb38\uc744 \u2018\uc608\ube44\u2019\ub85c \ubc88\uc5ed\ud558\uba70, "
                    "PC EN/SC/TC\uc5d0\uc11c\ub294 \ud574\ub2f9 \uc88c\ud45c\uac00 \ubbf8\uc0ac\uc6a9 \ud50c\ub808\uc774\uc2a4\ud640\ub354\ub85c \ub0a8\uc544 \uc788\ub2e4."
                ),
                "source_gate_validation": "exact_match",
                "current_ko_gate_validation": "exact_match",
                "pc_target_contexts": {language: table[target_id] for language, table in references.items()},
                "evidence_context": {
                    "same_source_korean_anchor": {
                        "id": ANCHOR_ID,
                        "source_text": jp[ANCHOR_ID],
                        "ko": ko[ANCHOR_ID],
                    },
                    "coordinate_drift_context": {
                        "current_ko_is_displaced_map_confirmation": True,
                        "no_switch_korean_translation_used": True,
                        "no_historic_korean_backup_used": True,
                    },
                },
                "format_profile": {
                    "current_ko": current_profile,
                    "proposed_ko": proposed_profile,
                    "pristine_jp": source_profile,
                },
                "format_validation": {
                    "current_to_proposed": "all_match",
                    "pristine_jp_to_proposed": "all_match",
                    "hangul_present": True,
                    "no_japanese_or_cjk_residue": True,
                    "no_replacement_glyph": True,
                },
                "game_files_written": False,
            }
        )
    if len(rows) != len(TARGETS) or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("candidate cardinality or uniqueness validation failed")
    summary = {
        "row_count": len(rows),
        "resource": "msgui",
        "ids": [row["id"] for row in rows],
        "source_gate_validation": "all_exact_match",
        "current_ko_gate_validation": "all_exact_match",
        "format_profiles": "all_match",
        "existing_msgui_candidate_overlap": "none",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="validate only; write no files")
    parser.add_argument("--write", action="store_true", help="write review JSONL below tmp")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.validate and args.write:
        parser.error("choose either --validate or --write")
    rows, summary = build_rows()
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        output = safe_output(args.output)
        payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
        if any(byte > 0x7F for byte in payload.encode("utf-8")):
            raise ValueError("review JSONL must be ASCII-only")
        atomic_write(output, payload)
        print(json.dumps({**summary, "output": str(output), "output_bytes": output.stat().st_size}, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
