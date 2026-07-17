#!/usr/bin/env python3
"""Create a PC-only, source-gated ``領内諸策`` terminology addendum.

The title is already rendered as ``영내 시책`` in the live PC Korean
``msgui`` interface.  This helper audits only the eight remaining repeated
labels in live PC ``strdata`` and ``msgdata`` that still say ``영지 제책``.
It reads pristine PC Japanese, current Steam PC Korean, and current PC
EN/SC/TC context where that resource exists.  It never reads Switch Korean
or an historic Korean backup, and it never writes a game resource.
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
from typing import Any


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_ROOT = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
TMP_ROOT = REPO / "tmp"
AUDIT_ROOT = TMP_ROOT / "translation_quality_audit_v1"
DEFAULT_OUTPUT = AUDIT_ROOT / "semantic" / "territorial_measures_term_consistency_addendum.v1.jsonl"

STRDATA_JP = PRISTINE_ROOT / "MSG" / "JP" / "strdata.bin"
STRDATA_KO = STEAM / "MSG" / "JP" / "strdata.bin"
STRDATA_REFERENCES = {
    language.lower(): STEAM / "MSG" / language / "strdata.bin"
    for language in ("SC", "TC")
}
MSGDATA_JP = PRISTINE_ROOT / "MSG_PK" / "JP" / "msgdata.bin"
MSGDATA_KO = STEAM / "MSG_PK" / "JP" / "msgdata.bin"
MSGDATA_REFERENCES = {
    language.lower(): STEAM / "MSG_PK" / language / "msgdata.bin"
    for language in ("EN", "SC", "TC")
}
MSGUI_JP = PRISTINE_ROOT / "MSG_PK" / "JP" / "msgui.bin"
MSGUI_KO = STEAM / "MSG_PK" / "JP" / "msgui.bin"
MSGUI_REFERENCES = {
    language.lower(): STEAM / "MSG_PK" / language / "msgui.bin"
    for language in ("EN", "SC", "TC")
}

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
CJK_OR_KANA_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff"
    r"\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


@dataclass(frozen=True)
class Target:
    resource: str
    coordinate: tuple[int, int] | int
    source_text: str
    expected_ko: str
    proposed_ko: str
    ui_slot_context: str


SOURCE_TITLE = "\u9818\u5185\u8af8\u7b56"
SOURCE_TITLE_WITH_NAME = "\u9818\u5185\u8af8\u7b56\u300c%s\u300d"
CURRENT_TITLE = "\uc601\uc9c0 \uc81c\ucc45"
CURRENT_TITLE_WITH_NAME = "\uc601\uc9c0 \uc81c\ucc45 \u300c%s\u300d"
PROPOSED_TITLE = "\uc601\ub0b4 \uc2dc\ucc45"
PROPOSED_TITLE_WITH_NAME = "\uc601\ub0b4 \uc2dc\ucc45 \u300c%s\u300d"

# The strdata title slots are repeated live UI labels, not ruby/readings or
# prose.  The msgdata slots are their same-PC-resource counterparts.
TARGETS = (
    Target("strdata", (0, 18757), SOURCE_TITLE, CURRENT_TITLE, PROPOSED_TITLE, "territorial_measures_label"),
    Target("strdata", (0, 19757), SOURCE_TITLE, CURRENT_TITLE, PROPOSED_TITLE, "territorial_measures_label"),
    Target("strdata", (0, 20578), SOURCE_TITLE, CURRENT_TITLE, PROPOSED_TITLE, "territorial_measures_label"),
    Target("strdata", (1, 2194), SOURCE_TITLE_WITH_NAME, CURRENT_TITLE_WITH_NAME, PROPOSED_TITLE_WITH_NAME, "territorial_measures_named_label"),
    Target("strdata", (1, 2212), SOURCE_TITLE, CURRENT_TITLE, PROPOSED_TITLE, "territorial_measures_label"),
    Target("msgdata", 18859, SOURCE_TITLE, CURRENT_TITLE, PROPOSED_TITLE, "territorial_measures_label"),
    Target("msgdata", 19859, SOURCE_TITLE, CURRENT_TITLE, PROPOSED_TITLE, "territorial_measures_label"),
    Target("msgdata", 20680, SOURCE_TITLE, CURRENT_TITLE, PROPOSED_TITLE, "territorial_measures_label"),
)

MSGUI_ANCHORS = {
    2194: (SOURCE_TITLE_WITH_NAME, "\uc601\ub0b4 \uc2dc\ucc45 \u201c%s\u201d"),
    2212: (SOURCE_TITLE, PROPOSED_TITLE),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load_common(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def load_strdata(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


def profile(text: str) -> dict[str, object]:
    return {
        "escape_tags": ESC_RE.findall(text),
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "newlines": re.findall(r"\r\n|\n|\r", text),
        "outer_ascii_whitespace": (
            text[: len(text) - len(text.lstrip(" \t"))],
            text[len(text.rstrip(" \t")) :],
        ),
        "private_use": [f"U+{ord(character):04X}" for character in PRIVATE_USE_RE.findall(text)],
        "fullwidth_percent_count": text.count("\uff05"),
        "question_mark_count": text.count("?"),
    }


def profile_match(left: dict[str, object], right: dict[str, object]) -> dict[str, bool]:
    return {
        "escape_tags_match": left["escape_tags"] == right["escape_tags"],
        "runtime_tokens_match": left["runtime_tokens"] == right["runtime_tokens"],
        "printf_match": left["printf"] == right["printf"],
        "newlines_match": left["newlines"] == right["newlines"],
        "outer_ascii_whitespace_match": left["outer_ascii_whitespace"] == right["outer_ascii_whitespace"],
        "private_use_match": left["private_use"] == right["private_use"],
        "fullwidth_percent_count_match": left["fullwidth_percent_count"] == right["fullwidth_percent_count"],
        "question_mark_count_match": left["question_mark_count"] == right["question_mark_count"],
    }


def candidate_overlaps() -> dict[str, list[str]]:
    """Find target keys already present in the current review candidate sets."""
    targets = {
        "strdata": {str(target.coordinate) for target in TARGETS if target.resource == "strdata"},
        "msgdata": {str(target.coordinate) for target in TARGETS if target.resource == "msgdata"},
    }
    found = {resource: [] for resource in targets}
    paths = [
        *(AUDIT_ROOT / "proposals").glob("strdata*.jsonl"),
        *(AUDIT_ROOT / "semantic").glob("strdata*.jsonl"),
        *(AUDIT_ROOT / "proposals").glob("msgdata*.jsonl"),
        *(AUDIT_ROOT / "semantic").glob("msgdata*.jsonl"),
    ]
    for path in sorted({item.resolve() for item in paths if item.resolve() != DEFAULT_OUTPUT.resolve()}):
        resource = "strdata" if path.name.startswith("strdata") else "msgdata"
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if resource == "strdata":
                if not isinstance(row.get("block"), int) or not isinstance(row.get("id"), int):
                    continue
                key = str((row["block"], row["id"]))
            else:
                if not isinstance(row.get("id"), int):
                    continue
                key = str(row["id"])
            if key in targets[resource]:
                found[resource].append(f"{path.name}:{line_number}")
    return found


def safe_under(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=False)
    allowed = root.resolve(strict=False)
    if resolved != allowed and allowed not in resolved.parents:
        raise ValueError(f"output must remain below {allowed}: {resolved}")
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


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    overlaps = candidate_overlaps()
    if any(overlaps.values()):
        raise ValueError(f"territorial-measures candidates overlap existing rows: {overlaps}")

    strdata = {
        "jp": load_strdata(STRDATA_JP),
        "ko": load_strdata(STRDATA_KO),
        **{language: load_strdata(path) for language, path in STRDATA_REFERENCES.items()},
    }
    msgdata = {
        "jp": load_common(MSGDATA_JP),
        "ko": load_common(MSGDATA_KO),
        **{language: load_common(path) for language, path in MSGDATA_REFERENCES.items()},
    }
    msgui = {
        "jp": load_common(MSGUI_JP),
        "ko": load_common(MSGUI_KO),
        **{language: load_common(path) for language, path in MSGUI_REFERENCES.items()},
    }
    if not (
        set(strdata["jp"]) == set(strdata["ko"]) == set(strdata["sc"]) == set(strdata["tc"])
    ):
        raise ValueError("PC strdata coordinate sets differ")
    if any(len(msgdata[language]) != len(msgdata["jp"]) for language in msgdata):
        raise ValueError("PC msgdata cardinalities differ")
    if any(len(msgui[language]) != len(msgui["jp"]) for language in msgui):
        raise ValueError("PC msgui cardinalities differ")
    for identifier, (source, expected_ko) in MSGUI_ANCHORS.items():
        if msgui["jp"][identifier] != source or msgui["ko"][identifier] != expected_ko:
            raise ValueError(f"msgui anchor {identifier} changed")

    file_hashes = {
        "strdata": {
            "pristine_pc_jp": sha256_file(STRDATA_JP),
            "live_steam_ko": sha256_file(STRDATA_KO),
            **{language: sha256_file(path) for language, path in STRDATA_REFERENCES.items()},
        },
        "msgdata": {
            "pristine_pc_jp": sha256_file(MSGDATA_JP),
            "live_steam_ko": sha256_file(MSGDATA_KO),
            **{language: sha256_file(path) for language, path in MSGDATA_REFERENCES.items()},
        },
        "msgui": {
            "pristine_pc_jp": sha256_file(MSGUI_JP),
            "live_steam_ko": sha256_file(MSGUI_KO),
            **{language: sha256_file(path) for language, path in MSGUI_REFERENCES.items()},
        },
    }
    anchor_context = {
        str(identifier): {
            "source_text": msgui["jp"][identifier],
            "ko": msgui["ko"][identifier],
            "pc_target_contexts": {
                language: msgui[language][identifier] for language in MSGUI_REFERENCES
            },
        }
        for identifier in MSGUI_ANCHORS
    }

    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        table = strdata if target.resource == "strdata" else msgdata
        coordinate = target.coordinate
        if target.resource == "strdata":
            if not isinstance(coordinate, tuple) or coordinate not in table["jp"]:
                raise ValueError(f"invalid strdata coordinate: {coordinate}")
            source = table["jp"][coordinate]
            current = table["ko"][coordinate]
            contexts = {language: table[language][coordinate] for language in STRDATA_REFERENCES}
            coordinate_label = f"{coordinate[0]}:{coordinate[1]}"
            identity: dict[str, Any] = {"block": coordinate[0], "id": coordinate[1]}
        else:
            if not isinstance(coordinate, int) or not 0 <= coordinate < len(table["jp"]):
                raise ValueError(f"invalid msgdata coordinate: {coordinate}")
            source = table["jp"][coordinate]
            current = table["ko"][coordinate]
            contexts = {language: table[language][coordinate] for language in MSGDATA_REFERENCES}
            coordinate_label = str(coordinate)
            identity = {"id": coordinate}
        if source != target.source_text:
            raise ValueError(f"{target.resource}:{coordinate_label}: pristine JP source gate failed")
        if current != target.expected_ko:
            raise ValueError(f"{target.resource}:{coordinate_label}: current KO gate failed")
        current_profile = profile(current)
        source_profile = profile(source)
        proposed_profile = profile(target.proposed_ko)
        current_to_proposed = profile_match(current_profile, proposed_profile)
        source_to_proposed = profile_match(source_profile, proposed_profile)
        integrity = {
            "hangul_present": bool(HANGUL_RE.search(target.proposed_ko)),
            "no_japanese_or_cjk_residue": not bool(CJK_OR_KANA_RE.search(target.proposed_ko)),
            "no_replacement_glyph": "\ufffd" not in target.proposed_ko,
            "no_repeated_question_marks": "??" not in target.proposed_ko,
        }
        if not all(current_to_proposed.values()) or not all(source_to_proposed.values()) or not all(integrity.values()):
            raise ValueError(f"{target.resource}:{coordinate_label}: format or integrity check failed")
        rows.append(
            {
                "resource": target.resource,
                "coordinate": coordinate_label,
                **identity,
                "ko": current,
                "proposed_ko": target.proposed_ko,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "source_file_sha256": file_hashes[target.resource]["live_steam_ko"],
                "pristine_jp_file_sha256": file_hashes[target.resource]["pristine_pc_jp"],
                "reference_file_sha256": {
                    language: file_hashes[target.resource][language]
                    for language in contexts
                },
                "issue_type": "territorial_measures_term_consistency",
                "ui_slot_context": target.ui_slot_context,
                "rationale": "Same-source live PC msgui labels render this title as the Korean UI term 'yeongnae sichaek'; PC EN calls it Territorial Measures.",
                "source_gate_validation": "exact_match",
                "current_ko_gate_validation": "exact_match",
                "pc_target_contexts": contexts,
                "semantic_anchor": anchor_context,
                "format_profile": {
                    "current_ko": current_profile,
                    "proposed_ko": proposed_profile,
                    "pristine_jp": source_profile,
                },
                "format_validation": {
                    "current_to_proposed": current_to_proposed,
                    "pristine_jp_to_proposed": source_to_proposed,
                    "integrity": integrity,
                    "all_required_checks_pass": True,
                },
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
                "game_files_written": False,
            }
        )
    keys = [(row["resource"], row["coordinate"]) for row in rows]
    if len(rows) != len(TARGETS) or len(keys) != len(set(keys)):
        raise ValueError("candidate cardinality or key uniqueness check failed")
    payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
    if any(byte > 0x7F for byte in payload.encode("utf-8")):
        raise ValueError("candidate JSONL must be ASCII-only")
    summary = {
        "row_count": len(rows),
        "resource_counts": {
            "strdata": sum(row["resource"] == "strdata" for row in rows),
            "msgdata": sum(row["resource"] == "msgdata" for row in rows),
        },
        "target_coordinates": [f"{row['resource']}:{row['coordinate']}" for row in rows],
        "existing_candidate_overlap": overlaps,
        "source_gates": "all_exact_match",
        "current_ko_gates": "all_exact_match",
        "format_validation": "all_runtime_printf_esc_newline_whitespace_profiles_match",
        "msgui_same_source_anchors": sorted(MSGUI_ANCHORS),
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="validate only; write no files")
    parser.add_argument("--write", action="store_true", help="write the review JSONL under tmp")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.validate and args.write:
        parser.error("choose either --validate or --write")
    rows, summary = build_rows()
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        output = safe_under(args.output, TMP_ROOT)
        payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
        atomic_write(output, payload)
        print(json.dumps({**summary, "output": str(output), "output_bytes": output.stat().st_size}, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
