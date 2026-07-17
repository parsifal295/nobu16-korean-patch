#!/usr/bin/env python3
"""Build PC-only direct-UI-anchor corrections for four ``strdata`` labels.

The source-gated targets are duplicated UI labels whose exact PC ``msgui``
counterparts already use the clear Korean terms.  This helper reads pristine
PC Japanese, current Steam PC Korean, and current PC EN/SC/TC only.  It never
reads Switch Korean or a historic Korean backup, and it never writes a game
resource.
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
DEFAULT_OUTPUT = AUDIT_ROOT / "semantic" / "strdata_cross_resource_labels_addendum.v1.jsonl"

STRDATA_JP = PRISTINE_ROOT / "MSG" / "JP" / "strdata.bin"
STRDATA_KO = STEAM / "MSG" / "JP" / "strdata.bin"
STRDATA_REFERENCES = {
    language.lower(): STEAM / "MSG" / language / "strdata.bin"
    for language in ("SC", "TC")
}
MSGUI_JP = PRISTINE_ROOT / "MSG_PK" / "JP" / "msgui.bin"
MSGUI_KO = STEAM / "MSG_PK" / "JP" / "msgui.bin"
MSGUI_REFERENCES = {
    language.lower(): STEAM / "MSG_PK" / language / "msgui.bin"
    for language in ("EN", "SC", "TC")
}

MSGDATA_CANDIDATE_PATHS = {
    "construction": AUDIT_ROOT / "semantic" / "msgdata_semantic_ui_term_addendum.v1.jsonl",
    "labor": AUDIT_ROOT / "semantic" / "msgdata_labor_terminology_addendum.v1.jsonl",
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
    block: int
    identifier: int
    source_text: str
    current_ko: str
    proposed_ko: str
    anchor_kind: str
    slot_kind: str


# These are all bare display labels.  The two source terms and their nearby
# source groups exactly match their current PC msgui anchors below.
TARGETS = (
    Target(0, 23641, "\u4f5c\u4e8b", "\uc791\uc0ac", "\uac74\ucd95", "construction", "trait_label"),
    Target(1, 1824, "\u4f5c\u4e8b", "\uc791\uc0ac", "\uac74\ucd95", "construction", "visible_ui_label"),
    Target(0, 24936, "\u52b4\u529b", "\ub178\ub825", "\ub178\ub3d9\ub825", "labor", "system_glossary_label"),
    Target(1, 1362, "\u52b4\u529b", "\ub178\ub825", "\ub178\ub3d9\ub825", "labor", "construction_requirement_label"),
)

MSGUI_ANCHORS = {
    "construction": {
        "id": 1824,
        "source_text": "\u4f5c\u4e8b",
        "current_ko": "\uac74\ucd95",
        "proposed_ko": "\uac74\ucd95",
        "slot_kind": "direct_same_source_ui_anchor",
    },
    "labor": {
        "id": 1362,
        "source_text": "\u52b4\u529b",
        "current_ko": "\ub178\ub3d9\ub825",
        "proposed_ko": "\ub178\ub3d9\ub825",
        "slot_kind": "direct_same_source_construction_resource_anchor",
    },
}

EXPECTED_MSGDATA_CANDIDATES = {
    "construction": {
        "id": 24443,
        "ko": "\uc791\uc0ac",
        "proposed_ko": "\uac74\ucd95",
    },
    "labor": {
        "id": 26228,
        "ko": "\ub178\ub825",
        "proposed_ko": "\ub178\ub3d9\ub825",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load_strdata(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


def load_common(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


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


def existing_strdata_overlaps() -> list[str]:
    target_keys = {(target.block, target.identifier) for target in TARGETS}
    found: list[str] = []
    for directory in (AUDIT_ROOT / "semantic", AUDIT_ROOT / "proposals"):
        for path in sorted(directory.glob("strdata*.jsonl")):
            if path.resolve() == DEFAULT_OUTPUT.resolve():
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                block, identifier = row.get("block"), row.get("id")
                if isinstance(block, int) and isinstance(identifier, int) and (block, identifier) in target_keys:
                    found.append(f"{path.name}:{line_number}")
    return found


def read_expected_msgdata_candidate(kind: str) -> dict[str, object]:
    path = MSGDATA_CANDIDATE_PATHS[kind]
    expected = EXPECTED_MSGDATA_CANDIDATES[kind]
    if not path.is_file():
        raise ValueError(f"missing existing PC msgdata candidate: {path}")
    matches = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("id") == expected["id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one msgdata candidate for {kind}, got {len(matches)}")
    row = matches[0]
    if row.get("ko") != expected["ko"] or row.get("proposed_ko") != expected["proposed_ko"]:
        raise ValueError(f"existing msgdata candidate drifted for {kind}")
    return {
        "id": expected["id"],
        "ko": row["ko"],
        "proposed_ko": row["proposed_ko"],
        "current_hash": row.get("current_hash"),
        "source_text": row.get("source_text"),
        "source_text_hash": row.get("source_text_hash"),
        "artifact": path.name,
    }


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    overlaps = existing_strdata_overlaps()
    if overlaps:
        raise ValueError(f"cross-resource strdata labels overlap existing candidates: {overlaps}")

    strdata = {
        "jp": load_strdata(STRDATA_JP),
        "ko": load_strdata(STRDATA_KO),
        **{language: load_strdata(path) for language, path in STRDATA_REFERENCES.items()},
    }
    msgui = {
        "jp": load_common(MSGUI_JP),
        "ko": load_common(MSGUI_KO),
        **{language: load_common(path) for language, path in MSGUI_REFERENCES.items()},
    }
    if not (set(strdata["jp"]) == set(strdata["ko"]) == set(strdata["sc"]) == set(strdata["tc"])):
        raise ValueError("PC strdata coordinate sets differ")
    if any(len(msgui[language]) != len(msgui["jp"]) for language in msgui):
        raise ValueError("PC msgui cardinalities differ")

    anchors: dict[str, dict[str, Any]] = {}
    for kind, expected in MSGUI_ANCHORS.items():
        identifier = expected["id"]
        if msgui["jp"][identifier] != expected["source_text"] or msgui["ko"][identifier] != expected["current_ko"]:
            raise ValueError(f"msgui direct anchor changed for {kind}:{identifier}")
        anchors[kind] = {
            "resource": "msgui",
            "id": identifier,
            "source_text": msgui["jp"][identifier],
            "ko": msgui["ko"][identifier],
            "pc_target_contexts": {language: msgui[language][identifier] for language in MSGUI_REFERENCES},
            "slot_kind": expected["slot_kind"],
            "source_gate_validation": "exact_match",
            "current_ko_gate_validation": "exact_match",
        }

    file_hashes = {
        "strdata": {
            "pristine_pc_jp": sha256_file(STRDATA_JP),
            "live_steam_ko": sha256_file(STRDATA_KO),
            **{language: sha256_file(path) for language, path in STRDATA_REFERENCES.items()},
        },
        "msgui": {
            "pristine_pc_jp": sha256_file(MSGUI_JP),
            "live_steam_ko": sha256_file(MSGUI_KO),
            **{language: sha256_file(path) for language, path in MSGUI_REFERENCES.items()},
        },
    }
    msgdata_candidates = {kind: read_expected_msgdata_candidate(kind) for kind in MSGUI_ANCHORS}

    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        coordinate = (target.block, target.identifier)
        source = strdata["jp"].get(coordinate)
        current = strdata["ko"].get(coordinate)
        if source != target.source_text:
            raise ValueError(f"strdata:{target.block}:{target.identifier}: pristine JP source gate failed")
        if current != target.current_ko:
            raise ValueError(f"strdata:{target.block}:{target.identifier}: current KO gate failed")
        anchor = anchors[target.anchor_kind]
        if anchor["source_text"] != source or anchor["ko"] != target.proposed_ko:
            raise ValueError(f"strdata:{target.block}:{target.identifier}: direct msgui anchor mismatch")
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
            raise ValueError(f"strdata:{target.block}:{target.identifier}: format or integrity validation failed")
        rows.append(
            {
                "resource": "strdata",
                "coordinate": f"{target.block}:{target.identifier}",
                "block": target.block,
                "id": target.identifier,
                "ko": current,
                "proposed_ko": target.proposed_ko,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "source_file_sha256": file_hashes["strdata"]["live_steam_ko"],
                "pristine_jp_file_sha256": file_hashes["strdata"]["pristine_pc_jp"],
                "reference_file_sha256": {language: file_hashes["strdata"][language] for language in STRDATA_REFERENCES},
                "issue_type": "direct_cross_resource_ui_term_consistency",
                "slot_kind": target.slot_kind,
                "rationale": "The exact same pristine-PC-JP label and adjacent UI group are already localized by the live PC msgui anchor. This replaces a Japanese phonetic rendering or personal-effort sense with the direct Korean UI term.",
                "source_gate_validation": "exact_match",
                "current_ko_gate_validation": "exact_match",
                "pc_target_contexts": {language: strdata[language][coordinate] for language in STRDATA_REFERENCES},
                "direct_msgui_anchor": anchors[target.anchor_kind],
                "existing_msgdata_counterpart_candidate": msgdata_candidates[target.anchor_kind],
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
    keys = [(row["block"], row["id"]) for row in rows]
    if len(rows) != len(TARGETS) or len(keys) != len(set(keys)):
        raise ValueError("candidate cardinality or coordinate uniqueness check failed")
    payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
    if any(byte > 0x7F for byte in payload.encode("utf-8")):
        raise ValueError("candidate JSONL must be ASCII-only")
    summary = {
        "row_count": len(rows),
        "target_coordinates": [row["coordinate"] for row in rows],
        "term_counts": {
            "construction": sum(row["proposed_ko"] == "\uac74\ucd95" for row in rows),
            "labor": sum(row["proposed_ko"] == "\ub178\ub3d9\ub825" for row in rows),
        },
        "existing_strdata_candidate_overlap": [],
        "source_gates": "all_exact_match",
        "current_ko_gates": "all_exact_match",
        "format_validation": "all_runtime_printf_esc_newline_whitespace_profiles_match",
        "direct_msgui_anchor_ids": sorted(anchor["id"] for anchor in anchors.values()),
        "existing_msgdata_counterpart_ids": sorted(candidate["id"] for candidate in msgdata_candidates.values()),
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="validate only; write no files")
    parser.add_argument("--write", action="store_true", help="write the ASCII JSONL below tmp")
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
