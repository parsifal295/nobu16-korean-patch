#!/usr/bin/env python3
"""Build source-gated static-name repairs for unsupported glyph loss.

This narrow audit only covers the duplicated static name slot for Tachibana
Ginchiyo.  It reads the pristine PC Japanese sources, the current Steam PC
Korean targets, and installed PC EN/SC/TC references.  It neither reads a
Switch Korean resource nor writes a game resource.  ``--write`` only emits a
review JSONL under ``tmp``.
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
    / "static_name_special_glyph_addendum.v1.jsonl"
)

STR_PRISTINE_JP = BACKUP / "MSG" / "JP" / "strdata.bin"
STR_LIVE_KO = STEAM / "MSG" / "JP" / "strdata.bin"
STR_REFERENCES = {
    language.lower(): STEAM / "MSG" / language / "strdata.bin"
    for language in ("SC", "TC")
}
MSG_PRISTINE_JP = BACKUP / "MSG_PK" / "JP" / "msgdata.bin"
MSG_LIVE_KO = STEAM / "MSG_PK" / "JP" / "msgdata.bin"
MSG_REFERENCES = {
    language.lower(): STEAM / "MSG_PK" / language / "msgdata.bin"
    for language in ("EN", "SC", "TC")
}

# The source glyph is U+250C, not a decorative game icon.  PC SC preserves
# the underlying name character as 訚 and PC EN provides the reading.
SOURCE_TEXT = "\u250c\u5343\u4ee3"
CURRENT_KO = "\u250c\uc9c0\uc694"
PROPOSED_KO = "\uae34\uce58\uc694"
STR_COORDINATE = (0, 2046)
MSG_ID = 2046

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata  # noqa: E402


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


def load_msgdata(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def load_strdata(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


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


def assert_candidate_integrity(
    *, resource: str, source: str, current: str, proposed: str
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    if source != SOURCE_TEXT:
        raise ValueError(f"{resource}: pristine source gate failed: {source!r}")
    if current != CURRENT_KO:
        raise ValueError(f"{resource}: current Korean gate failed: {current!r}")
    if proposed != PROPOSED_KO:
        raise ValueError(f"{resource}: unexpected proposed text")
    source_profile = format_profile(source)
    current_profile = format_profile(current)
    proposed_profile = format_profile(proposed)
    if current_profile != proposed_profile:
        raise ValueError(f"{resource}: current/proposed format profile mismatch")
    if source_profile != proposed_profile:
        raise ValueError(f"{resource}: source/proposed format profile mismatch")
    if not HANGUL_RE.search(proposed):
        raise ValueError(f"{resource}: proposed text has no Hangul")
    if JAPANESE_OR_CJK_RE.search(proposed) or "\u250c" in proposed:
        raise ValueError(f"{resource}: proposed text retains source glyph or CJK")
    if "\ufffd" in proposed or "??" in proposed:
        raise ValueError(f"{resource}: proposed text contains a corruption marker")
    return source_profile, current_profile, proposed_profile


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


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    str_jp = load_strdata(STR_PRISTINE_JP)
    str_ko = load_strdata(STR_LIVE_KO)
    str_refs = {language: load_strdata(path) for language, path in STR_REFERENCES.items()}
    if set(str_jp) != set(str_ko) or any(set(table) != set(str_jp) for table in str_refs.values()):
        raise ValueError("strdata PC table coordinates differ")
    if STR_COORDINATE not in str_jp:
        raise ValueError("strdata target coordinate is absent")

    msg_jp = load_msgdata(MSG_PRISTINE_JP)
    msg_ko = load_msgdata(MSG_LIVE_KO)
    msg_refs = {language: load_msgdata(path) for language, path in MSG_REFERENCES.items()}
    if len(msg_jp) != len(msg_ko) or any(len(table) != len(msg_jp) for table in msg_refs.values()):
        raise ValueError("msgdata PC table cardinalities differ")
    if not 0 <= MSG_ID < len(msg_jp):
        raise ValueError("msgdata target coordinate is outside the table")

    str_source = str_jp[STR_COORDINATE]
    str_current = str_ko[STR_COORDINATE]
    str_source_profile, str_current_profile, str_proposed_profile = assert_candidate_integrity(
        resource="strdata", source=str_source, current=str_current, proposed=PROPOSED_KO
    )
    msg_source = msg_jp[MSG_ID]
    msg_current = msg_ko[MSG_ID]
    msg_source_profile, msg_current_profile, msg_proposed_profile = assert_candidate_integrity(
        resource="msgdata", source=msg_source, current=msg_current, proposed=PROPOSED_KO
    )

    if msg_refs["en"][MSG_ID] != "Ginchiyo":
        raise ValueError("msgdata EN Ginchiyo evidence changed")
    if str_refs["sc"][STR_COORDINATE] != "\u8a1a\u5343\u4ee3":
        raise ValueError("strdata SC name-character evidence changed")
    if msg_refs["sc"][MSG_ID] != "\u8a1a\u5343\u4ee3":
        raise ValueError("msgdata SC name-character evidence changed")

    issue_type = "static_name_special_glyph_loss"
    rationale = (
        "PC SC\uc758 \u8a1a\u5343\u4ee3\uc640 PC EN\uc758 Ginchiyo, \ub3d9\uc77c \uc778\uba85\uc744 "
        "\uae34\uce58\uc694\ub85c \ubcf5\uc6d0\ud55c ev_strdata V4\uc758 \uc0c1\ud638 \uadfc\uac70\ub85c, "
        "\uc9c0\uc6d0\ub418\uc9c0 \uc54a\ub294 U+250C \uae00\ub9ac\ud504\uc640 \uc798\ubabb\ub41c \ub3c5\uc74c\uc744 "
        "\uae34\uce58\uc694\ub85c \ubcf5\uc6d0\ud55c\ub2e4."
    )
    common_evidence = {
        "pc_cross_resource_msgdata": {
            "id": MSG_ID,
            "en": msg_refs["en"][MSG_ID],
            "sc": msg_refs["sc"][MSG_ID],
            "tc": msg_refs["tc"][MSG_ID],
        },
        "ev_strdata_v4_consistency_ids": [1729, 3014, 3073, 7470, 7475, 7477, 8399],
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
    }
    rows = [
        {
            "resource": "strdata",
            "coordinate": "0:2046",
            "block": STR_COORDINATE[0],
            "id": STR_COORDINATE[1],
            "ko": str_current,
            "proposed_ko": PROPOSED_KO,
            "current_hash": text_hash(str_current),
            "source_text": str_source,
            "source_text_hash": text_hash(str_source),
            "live_ko_file_sha256": sha256_file(STR_LIVE_KO),
            "pristine_jp_file_sha256": sha256_file(STR_PRISTINE_JP),
            "reference_file_sha256": {
                language: sha256_file(path) for language, path in STR_REFERENCES.items()
            },
            "issue_type": issue_type,
            "rationale": rationale,
            "source_gate_validation": "exact_match",
            "current_ko_gate_validation": "exact_match",
            "pc_target_contexts": {
                "sc": str_refs["sc"][STR_COORDINATE],
                "tc": str_refs["tc"][STR_COORDINATE],
            },
            "evidence_context": common_evidence,
            "format_profile": {
                "current_ko": str_current_profile,
                "proposed_ko": str_proposed_profile,
                "pristine_jp": str_source_profile,
            },
            "format_validation": {
                "current_to_proposed": "all_match",
                "pristine_jp_to_proposed": "all_match",
                "hangul_present": True,
                "no_japanese_or_cjk_residue": True,
                "no_source_box_drawing_residue": True,
                "no_replacement_glyph": True,
            },
        },
        {
            "resource": "msgdata",
            "coordinate": str(MSG_ID),
            "id": MSG_ID,
            "ko": msg_current,
            "proposed_ko": PROPOSED_KO,
            "current_hash": text_hash(msg_current),
            "source_text": msg_source,
            "source_text_hash": text_hash(msg_source),
            "live_ko_file_sha256": sha256_file(MSG_LIVE_KO),
            "pristine_jp_file_sha256": sha256_file(MSG_PRISTINE_JP),
            "reference_file_sha256": {
                language: sha256_file(path) for language, path in MSG_REFERENCES.items()
            },
            "issue_type": issue_type,
            "rationale": rationale,
            "source_gate_validation": "exact_match",
            "current_ko_gate_validation": "exact_match",
            "pc_target_contexts": {
                language: table[MSG_ID] for language, table in msg_refs.items()
            },
            "evidence_context": common_evidence,
            "format_profile": {
                "current_ko": msg_current_profile,
                "proposed_ko": msg_proposed_profile,
                "pristine_jp": msg_source_profile,
            },
            "format_validation": {
                "current_to_proposed": "all_match",
                "pristine_jp_to_proposed": "all_match",
                "hangul_present": True,
                "no_japanese_or_cjk_residue": True,
                "no_source_box_drawing_residue": True,
                "no_replacement_glyph": True,
            },
        },
    ]
    if len({(str(row["resource"]), str(row["coordinate"])) for row in rows}) != len(rows):
        raise ValueError("duplicate static-name candidate coordinate")
    summary = {
        "row_count": len(rows),
        "resources": [row["resource"] for row in rows],
        "source_gate_validation": "all_exact_match",
        "current_ko_gate_validation": "all_exact_match",
        "format_profiles": "all_match",
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
        print(
            json.dumps(
                {**summary, "output": str(output), "output_bytes": output.stat().st_size},
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
