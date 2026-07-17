#!/usr/bin/env python3
"""Emit one source-gated ``msgui`` coordinate-drift repair for review.

The audit deliberately uses only the pristine PC Japanese source, the live
Steam PC Korean target, and live PC EN/SC/TC references.  It does not read a
Switch Korean translation or a historical Korean backup.  ``--write`` emits a
review JSONL below ``tmp`` only; it never changes a game resource.
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
PRISTINE_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgui.bin"
)
LIVE_KO = STEAM / "MSG_PK" / "JP" / "msgui.bin"
REFERENCES = {
    language.lower(): STEAM / "MSG_PK" / language / "msgui.bin"
    for language in ("EN", "SC", "TC")
}
TMP_ROOT = REPO / "tmp"
OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgui_game_clear_coordinate_drift_addendum.v1.jsonl"
)

TARGET_ID = 3583
SOURCE_TEXT = "ゲームクリア"
CURRENT_KO = "현재 선택한 성입니다"
PROPOSED_KO = "게임 클리어"
# This is evidence only, rather than a live gate: the independently reviewed
# coordinate-realignment proposal can legitimately repair this location first.
DISPLACED_SOURCE_ID = 3589
DISPLACED_SOURCE_TEXT = "選択中の城です"

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
        "fullwidth_percent_count": text.count("％"),
        "question_mark_count": text.count("?"),
    }


def candidate_files() -> list[Path]:
    audit = TMP_ROOT / "translation_quality_audit_v1"
    paths = list((audit / "semantic").glob("msgui*.jsonl"))
    paths += list((audit / "proposals").glob("msgui*.jsonl"))
    return sorted({path.resolve() for path in paths if path.resolve() != OUTPUT.resolve()})


def assert_not_already_proposed(target_id: int) -> None:
    duplicate_locations: list[str] = []
    for path in candidate_files():
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            values = (row.get("id"), row.get("coordinate"))
            if target_id in values or str(target_id) in values:
                duplicate_locations.append(f"{path}:{line_number}")
    if duplicate_locations:
        raise ValueError(
            "target ID already exists in msgui candidate files: "
            + ", ".join(duplicate_locations)
        )


def safe_output(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output must stay under {root}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_row() -> tuple[dict[str, object], dict[str, object]]:
    jp = load_msgui(PRISTINE_JP)
    ko = load_msgui(LIVE_KO)
    references = {language: load_msgui(path) for language, path in REFERENCES.items()}
    if len(jp) != len(ko) or any(len(table) != len(jp) for table in references.values()):
        raise ValueError("PC msgui table cardinalities differ")
    if not (0 <= TARGET_ID < len(jp) and 0 <= DISPLACED_SOURCE_ID < len(jp)):
        raise ValueError("review coordinate is outside the msgui table")
    assert_not_already_proposed(TARGET_ID)

    source = jp[TARGET_ID]
    current = ko[TARGET_ID]
    if source != SOURCE_TEXT:
        raise ValueError(f"{TARGET_ID}: pristine Japanese source gate failed: {source!r}")
    if current != CURRENT_KO:
        raise ValueError(f"{TARGET_ID}: current Korean target gate failed: {current!r}")
    if jp[DISPLACED_SOURCE_ID] != DISPLACED_SOURCE_TEXT:
        raise ValueError("displaced-text source evidence changed at ID 3589")

    source_profile = format_profile(source)
    current_profile = format_profile(current)
    proposed_profile = format_profile(PROPOSED_KO)
    if source_profile != proposed_profile or current_profile != proposed_profile:
        raise ValueError("source/current/proposed format profiles differ")
    if not HANGUL_RE.search(PROPOSED_KO) or JAPANESE_OR_CJK_RE.search(PROPOSED_KO):
        raise ValueError("proposed Korean text is not Hangul-only")
    if "\ufffd" in PROPOSED_KO or "??" in PROPOSED_KO:
        raise ValueError("proposed Korean text contains a corruption marker")

    reference_texts = {language: table[TARGET_ID] for language, table in references.items()}
    expected_reference_texts = {
        "en": "Game Clear.",
        "sc": "游戏通关。",
        "tc": "遊戲過關",
    }
    if reference_texts != expected_reference_texts:
        raise ValueError(f"PC reference gate changed: {reference_texts!r}")

    row = {
        "resource": "msgui",
        "coordinate": str(TARGET_ID),
        "id": TARGET_ID,
        "ko": current,
        "proposed_ko": PROPOSED_KO,
        "current_hash": text_hash(current),
        "source_text": source,
        "source_text_hash": text_hash(source),
        "live_ko_file_sha256": sha256_file(LIVE_KO),
        "pristine_jp_file_sha256": sha256_file(PRISTINE_JP),
        "reference_file_sha256": {
            language: sha256_file(path) for language, path in REFERENCES.items()
        },
        "issue_type": "short_label_coordinate_drift",
        "rationale": (
            "순정 PC JP ‘ゲームクリア’와 PC EN/SC/TC의 Game Clear/游戏通关/遊戲過關이 "
            "일치한다. 현재 한국어 ‘현재 선택한 성입니다’는 JP ID 3589의 ‘選択中の城です’ "
            "문맥에 해당하는, 인접 구간의 명백한 좌표 밀림 텍스트다."
        ),
        "source_gate_validation": "exact_match",
        "current_ko_gate_validation": "exact_match",
        "pc_target_contexts": reference_texts,
        "evidence_context": {
            "displaced_current_ko_semantic_source": {
                "id": DISPLACED_SOURCE_ID,
                "pristine_jp": jp[DISPLACED_SOURCE_ID],
                "semantic_korean": CURRENT_KO,
                "is_live_gate": False,
            },
            "existing_candidate_overlap": "none",
            "switch_korean_translation_used": False,
            "historic_korean_backup_used": False,
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
    summary = {
        "row_count": 1,
        "resource": "msgui",
        "ids": [TARGET_ID],
        "source_gate_validation": "all_exact_match",
        "current_ko_gate_validation": "all_exact_match",
        "pc_reference_gate_validation": "all_exact_match",
        "format_profiles": "all_match",
        "existing_msgui_candidate_overlap": "none",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return row, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="validate only; write no files")
    parser.add_argument("--write", action="store_true", help="write review JSONL below tmp")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.validate and args.write:
        parser.error("choose either --validate or --write")
    row, summary = build_row()
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        output = safe_output(args.output)
        payload = json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n"
        if any(byte > 0x7F for byte in payload.encode("utf-8")):
            raise ValueError("review JSONL must be ASCII-only")
        atomic_write(output, payload)
        print(
            json.dumps(
                {**summary, "output": str(output), "output_bytes": output.stat().st_size},
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
