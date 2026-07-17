#!/usr/bin/env python3
"""Build a source-gated, high-confidence msgdata semantic review addendum.

This script is deliberately read-only unless ``--write`` is supplied.  It
reads only the pristine PC Japanese resource and the current Steam PC Korean
resource, plus PC EN/SC/TC resources for context.  It never uses the Switch
repository or a historic Korean backup, and it never writes a game resource.

The emitted JSONL is ASCII-only and every row is guarded by both its current
Korean text/hash and its pristine Japanese source text/hash.  A later applier
can therefore reject a row if either resource has changed underneath it.
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
    / "msgdata.bin"
)
LIVE_KO = STEAM / "MSG_PK" / "JP" / "msgdata.bin"
REFERENCE_FILES = {
    language: STEAM / "MSG_PK" / language / "msgdata.bin"
    for language in ("EN", "SC", "TC")
}
TMP_ROOT = REPO / "tmp"
DIRECT_EXISTING = TMP_ROOT / "translation_quality_audit_v1" / "proposals" / "msgdata_ko.jsonl"
SEMANTIC_EXISTING = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_findings.v1.jsonl"
DEFAULT_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_semantic_addendum.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
JAPANESE_OR_CJK_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


@dataclass(frozen=True)
class Candidate:
    source_text: str
    expected_ko: str
    proposed_ko: str
    issue_type: str
    rationale: str
    evidence_ids: tuple[int, ...] = ()


# These are source-gated review definitions.  ``EMIT_IDS`` deliberately keeps
# the first artifact to the 14 unambiguous semantic corrections: one direct
# source conflation and thirteen visible Japanese readings in battle UI.
# Status/terminology consistency rows stay deferred until the broader
# duplicate-rendering review is complete.  Unicode escapes keep the source
# robust on Windows terminals while the emitted JSONL remains ensure_ascii=True.
ALL_REVIEW_CANDIDATES: dict[int, Candidate] = {
    20700: Candidate(
        "\u9000\u304d\u53e3\u307e\u3067\u300c\u507d\u5831\u300d",
        "\ud1f4\ub85c\uae4c\uc9c0 \u300c\uc704\ubcf4\u300d",
        "\ud1f4\ub85c\uae4c\uc9c0 \u300c\ud5c8\ubcf4\u300d",
        "status_term_consistency",
        "\uac19\uc740 \ud45c\uc2dc \uc0c1\ud0dc \ud1a0\ud070 \u300c\u507d\u5831\u300d\uc740 \uae30\uc874 \ud45c\uc2dc \ud56d\ubaa9\uc5d0\uc11c \u300c\ud5c8\ubcf4\u300d\ub85c \uc0ac\uc6a9\ub418\uc5b4 \uc788\uc73c\ubbc0\ub85c \uc6a9\uc5b4\ub97c \uc77c\uce58\uc2dc\ud0a8\ub2e4.",
        (15928, 20696),
    ),
    20721: Candidate(
        "\u9006\u843d\u3068\u3057",
        "\uc0ac\uce74\uc624\ud1a0\uc2dc",
        "\uc808\ubcbd \ub3cc\uaca9",
        "visible_japanese_reading",
        "\uc804\uc7a5 \ud2b9\uc218 \ud589\ub3d9\uba85\uc5d0 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc774 \ub0a8\uc544 \uc788\ub2e4. PC EN\uc758 Downhill Surge\uc640 \uc911\uad6d\uc5b4 \ubc88\uc5ed\uc758 \uc808\ubcbd \ub3cc\uaca9 \uc758\ubbf8\ub97c \ubcf4\uc874\ud55c\ub2e4.",
        (20861,),
    ),
    20789: Candidate(
        "\u68ee",
        "\ubaa8\ub9ac",
        "\uc232",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u68ee\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Forest\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4 \uc9c0\ud615\uba85\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20790: Candidate(
        "\u6d45\u702c",
        "\uc544\uc0ac\uc138",
        "\uc595\uc740 \ubb3c",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u6d45\u702c\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Shallow\uc640 \uae4a\uc740 \ubb3c \ud56d\ubaa9\uacfc \uc9dd\uc744 \uc774\ub8e8\ub294 \ud55c\uad6d\uc5b4\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20791: Candidate(
        "\u6df1\u9593",
        "\ud6c4\uce74\ub9c8",
        "\uae4a\uc740 \ubb3c",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u6df1\u9593\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Deep Water\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20792: Candidate(
        "\u6a4b",
        "\ud558\uc2dc",
        "\ub2e4\ub9ac",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u6a4b\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Bridge\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20794: Candidate(
        "\u9ad8\u5c71",
        "\ub2e4\uce74\uc57c\ub9c8",
        "\uace0\uc0b0",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u9ad8\u5c71\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \ud55c\uad6d\uc5b4 \uc9c0\ud615\uba85\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20821: Candidate(
        "\u6a39\u6797",
        "\uc8fc\ub9b0",
        "\uc218\ub9bc",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u6a39\u6797\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \ud55c\uad6d\uc5b4 \uc9c0\ud615\uc6a9\uc5b4 \uc218\ub9bc\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20822: Candidate(
        "\u6cb3\u53e3",
        "\uac00\uc640\uad6c\uce58",
        "\ud558\uad6c",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u6cb3\u53e3\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \ud55c\uad6d\uc5b4 \uc9c0\ud615\uc6a9\uc5b4 \ud558\uad6c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20824: Candidate(
        "\u65e9\u702c",
        "\ud558\uc57c\uc138",
        "\uc5ec\uc6b8",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u65e9\u702c\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \ubb3c\uc0b4\uc774 \ube60\ub974\uace0 \uc587\uc740 \ud558\ucc9c\uc744 \ub73b\ud558\ub294 \ud55c\uad6d\uc5b4 \uc9c0\ud615\uba85 \uc5ec\uc6b8\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20825: Candidate(
        "\u6bb5\u4e18",
        "\ub2e8\ud050",
        "\ub2e8\uad6c",
        "visible_japanese_reading",
        "\uc804\uc7a5 \uc9c0\ud615\uba85 \u6bb5\u4e18\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \ud55c\uad6d\uc5b4 \uc9c0\ud615\uc6a9\uc5b4 \ub2e8\uad6c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20844: Candidate(
        "\u843d\u77f3",
        "\uc624\uce58\uc774\uc2dc",
        "\ub099\uc11d",
        "visible_japanese_reading",
        "\uc804\uc7a5 \ud2b9\uc218 \uc9c0\ud615 \u843d\u77f3\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Falling Rocks\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    20861: Candidate(
        "\u9006\u843d\u3068\u3057",
        "\uc0ac\uce74\uc624\ud1a0\uc2dc",
        "\uc808\ubcbd \ub3cc\uaca9",
        "visible_japanese_reading",
        "\uc804\uc7a5 \ud2b9\uc218 \ud589\ub3d9\uba85\uc5d0 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc774 \ub0a8\uc544 \uc788\ub2e4. \ub3d9\uc77c \uc6d0\ubb38\uc758 20721\ubc88\uacfc PC EN Downhill Surge\uc758 \uc758\ubbf8\ub97c \ubcf4\uc874\ud55c\ub2e4.",
        (20721,),
    ),
    20865: Candidate(
        "\u9244\u7832\u6c34",
        "\ub383\ud3ec\ubbf8\uc988",
        "\ub3cc\ubc1c \ud64d\uc218",
        "visible_japanese_reading",
        "\uc804\uc7a5 \ud2b9\uc218 \ud589\ub3d9\uba85\uc5d0 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc774 \ub0a8\uc544 \uc788\ub2e4. PC EN Flash Flood\uc640 TC \uc0b0\ud64d\ubc1c\ubc1c\uc758 \uc758\ubbf8\ub97c \ubcf4\uc874\ud55c\ub2e4.",
    ),
    22658: Candidate(
        "\u5177\u7533\u5931\u6557\u6642\u306b\u3082\u52f2\u529f\u7372\u5f97",
        "\uac74\uc758 \uc2e4\ud328 \uc2dc\uc5d0\ub3c4 \uacf5\ud6c8 \ud68d\ub4dd",
        "\uac74\uc758 \uc2e4\ud328 \uc2dc\uc5d0\ub3c4 \ud6c8\uacf5 \ud68d\ub4dd",
        "system_term_consistency",
        "\uac8c\uc784 \uacf5\ud1b5 \uc2a4\ud0ef \u52f2\u529f\uc758 \uae30\uc900 \ud45c\uc2dc\uba85\uc740 26244\ubc88\uc758 \ud6c8\uacf5\uc774\uba70, \ub3d9\uc77c \uc6d0\ubb38\uc774 \ud6c8\uacf5\uc73c\ub85c \ub2e4\uc218 \ud45c\uae30\ub418\uc5b4 \uc788\ub2e4.",
        (26244, 23158),
    ),
    23006: Candidate(
        "\u7372\u5f97\u52f2\u529f\u5897\u52a0",
        "\ud68d\ub4dd \uacf5\ud6c8 \uc99d\uac00",
        "\ud68d\ub4dd \ud6c8\uacf5 \uc99d\uac00",
        "system_term_consistency",
        "\uac8c\uc784 \uacf5\ud1b5 \uc2a4\ud0ef \u52f2\u529f\uc758 \uae30\uc900 \ud45c\uc2dc\uba85\uc740 26244\ubc88\uc758 \ud6c8\uacf5\uc774\uba70, \ub3d9\uc77c \uc6d0\ubb38\uc774 \ud6c8\uacf5\uc73c\ub85c \ub2e4\uc218 \ud45c\uae30\ub418\uc5b4 \uc788\ub2e4.",
        (26244,),
    ),
    23014: Candidate(
        "\u4ee3\u5b98\u306e\u7372\u5f97\u52f2\u529f\u5897\u52a0",
        "\ub300\uad00\uc758 \ud68d\ub4dd \uacf5\ud6c8 \uc99d\uac00",
        "\ub300\uad00\uc758 \ud68d\ub4dd \ud6c8\uacf5 \uc99d\uac00",
        "system_term_consistency",
        "\uac8c\uc784 \uacf5\ud1b5 \uc2a4\ud0ef \u52f2\u529f\uc758 \uae30\uc900 \ud45c\uc2dc\uba85\uc740 26244\ubc88\uc758 \ud6c8\uacf5\uc774\uba70, \ub3d9\uc77c \uc6d0\ubb38\uc774 \ud6c8\uacf5\uc73c\ub85c \ub2e4\uc218 \ud45c\uae30\ub418\uc5b4 \uc788\ub2e4.",
        (26244,),
    ),
    23082: Candidate(
        "\u7d44\u982d\u304c\u6bce\u6708\u52f2\u529f\u3092\u7372\u5f97",
        "\uc870\uc7a5\uc774 \ub9e4\uc6d4 \uacf5\ud6c8 \ud68d\ub4dd",
        "\uc870\uc7a5\uc774 \ub9e4\uc6d4 \ud6c8\uacf5 \ud68d\ub4dd",
        "system_term_consistency",
        "\uac8c\uc784 \uacf5\ud1b5 \uc2a4\ud0ef \u52f2\u529f\uc758 \uae30\uc900 \ud45c\uc2dc\uba85\uc740 26244\ubc88\uc758 \ud6c8\uacf5\uc774\uba70, \ub3d9\uc77c \uc6d0\ubb38\uc774 \ud6c8\uacf5\uc73c\ub85c \ub2e4\uc218 \ud45c\uae30\ub418\uc5b4 \uc788\ub2e4.",
        (26244,),
    ),
    23158: Candidate(
        "\u5177\u7533\u5931\u6557\u6642\u306b\u3082\u52f2\u529f\u7372\u5f97",
        "\uac74\uc758 \uc2e4\ud328 \uc2dc\uc5d0\ub3c4 \uacf5\ud6c8 \ud68d\ub4dd",
        "\uac74\uc758 \uc2e4\ud328 \uc2dc\uc5d0\ub3c4 \ud6c8\uacf5 \ud68d\ub4dd",
        "system_term_consistency",
        "\uac8c\uc784 \uacf5\ud1b5 \uc2a4\ud0ef \u52f2\u529f\uc758 \uae30\uc900 \ud45c\uc2dc\uba85\uc740 26244\ubc88\uc758 \ud6c8\uacf5\uc774\uba70, \ub3d9\uc77c \uc6d0\ubb38\uc774 \ud6c8\uacf5\uc73c\ub85c \ub2e4\uc218 \ud45c\uae30\ub418\uc5b4 \uc788\ub2e4.",
        (26244, 22658),
    ),
    25189: Candidate(
        "\u4f53\u529b\u56de\u5fa9",
        "\ub0b4\uad6c \ud68c\ubcf5",
        "\uccb4\ub825 \ud68c\ubcf5",
        "incorrect_semantic_mapping",
        "\uc6d0\ubb38\uc740 \uccb4\ub825 \ud68c\ubcf5\uc774\uba70 PC EN\u00b7TC\uc640 \ub3d9\uc77c \uc6d0\ubb38\uc758 25306\ubc88 \ud55c\uad6d\uc5b4\uac00 \ubaa8\ub450 \uccb4\ub825 \ud68c\ubcf5\uc73c\ub85c \uc77c\uce58\ud55c\ub2e4. \ub0b4\uad6c \ud68c\ubcf5\uc740 \ub2e4\ub978 \uc6d0\ubb38 \u8010\u4e45\u56de\u5fa9\uc758 \ud45c\uae30\uc640 \ucda9\ub3cc\ud55c\ub2e4.",
        (25184, 25306),
    ),
}

EMIT_IDS = frozenset(
    {
        20721,
        20789,
        20790,
        20791,
        20792,
        20794,
        20821,
        20822,
        20824,
        20825,
        20844,
        20861,
        20865,
        25189,
    }
)
DEFERRED_REVIEW_IDS = frozenset(ALL_REVIEW_CANDIDATES).difference(EMIT_IDS)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load_texts(path: Path) -> list[str]:
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


def critical_profile_match(left: dict[str, object], right: dict[str, object]) -> dict[str, bool]:
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


def read_existing_ids(path: Path) -> set[int]:
    if not path.is_file():
        raise ValueError(f"existing candidate file is absent: {path}")
    result: set[int] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        identifier = row.get("id")
        if not isinstance(identifier, int):
            raise ValueError(f"{path.name}:{line_number} has no integer id")
        if identifier in result:
            raise ValueError(f"{path.name}:{line_number} duplicates ID {identifier}")
        result.add(identifier)
    return result


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


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    jp = load_texts(PRISTINE_JP)
    ko = load_texts(LIVE_KO)
    references = {language: load_texts(path) for language, path in REFERENCE_FILES.items()}
    if len(jp) != len(ko) or any(len(table) != len(jp) for table in references.values()):
        raise ValueError("PC msgdata table cardinalities differ")

    existing_direct = read_existing_ids(DIRECT_EXISTING)
    existing_semantic = read_existing_ids(SEMANTIC_EXISTING)
    existing = existing_direct | existing_semantic
    if not EMIT_IDS.issubset(ALL_REVIEW_CANDIDATES):
        raise ValueError("emit ID is missing its candidate definition")
    overlapping = sorted(existing.intersection(EMIT_IDS))
    if overlapping:
        raise ValueError(f"new semantic candidates overlap existing msgdata candidates: {overlapping}")
    if 26383 in EMIT_IDS:
        raise ValueError("ID 26383 belongs to the existing placeholder candidate, not this semantic addendum")

    file_hashes = {
        "live_steam_ko": sha256_file(LIVE_KO),
        "pristine_pc_jp": sha256_file(PRISTINE_JP),
        **{language.lower(): sha256_file(path) for language, path in REFERENCE_FILES.items()},
    }
    rows: list[dict[str, object]] = []
    for identifier in sorted(EMIT_IDS):
        candidate = ALL_REVIEW_CANDIDATES[identifier]
        if not 0 <= identifier < len(jp):
            raise ValueError(f"coordinate outside msgdata table: {identifier}")
        source = jp[identifier]
        current = ko[identifier]
        if source != candidate.source_text:
            raise ValueError(f"{identifier}: pristine JP source gate failed")
        if current != candidate.expected_ko:
            raise ValueError(f"{identifier}: current Steam Korean gate failed")
        if candidate.proposed_ko == current:
            raise ValueError(f"{identifier}: proposed text is unchanged")

        current_profile = profile(current)
        proposed_profile = profile(candidate.proposed_ko)
        source_profile = profile(source)
        current_to_proposed = critical_profile_match(current_profile, proposed_profile)
        source_to_proposed = critical_profile_match(source_profile, proposed_profile)
        integrity = {
            "hangul_present": bool(HANGUL_RE.search(candidate.proposed_ko)),
            "no_japanese_or_cjk_residue": not bool(JAPANESE_OR_CJK_RE.search(candidate.proposed_ko)),
            "no_replacement_glyph": "\ufffd" not in candidate.proposed_ko,
            "no_repeated_question_marks": "??" not in candidate.proposed_ko,
        }
        if not all(current_to_proposed.values()):
            raise ValueError(f"{identifier}: current/proposed format preservation failed")
        if not all(source_to_proposed.values()):
            raise ValueError(f"{identifier}: pristine-JP/proposed token preservation failed")
        if not all(integrity.values()):
            raise ValueError(f"{identifier}: proposed-text integrity validation failed")

        evidence_context: dict[str, dict[str, str]] = {}
        for evidence_id in candidate.evidence_ids:
            if not 0 <= evidence_id < len(jp):
                raise ValueError(f"{identifier}: evidence coordinate outside msgdata: {evidence_id}")
            evidence_context[str(evidence_id)] = {
                "jp": jp[evidence_id],
                "ko": ko[evidence_id],
                "en": references["EN"][evidence_id],
            }
        rows.append(
            {
                "id": identifier,
                "ko": current,
                "proposed_ko": candidate.proposed_ko,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "source_file_sha256": file_hashes["live_steam_ko"],
                "pristine_jp_file_sha256": file_hashes["pristine_pc_jp"],
                "reference_file_sha256": {language.lower(): file_hashes[language.lower()] for language in REFERENCE_FILES},
                "issue_type": candidate.issue_type,
                "rationale": candidate.rationale,
                "source_gate_validation": "exact_match",
                "current_ko_gate_validation": "exact_match",
                "pc_target_contexts": {
                    "en": references["EN"][identifier],
                    "sc": references["SC"][identifier],
                    "tc": references["TC"][identifier],
                },
                "evidence_context": evidence_context,
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
            }
        )

    identifiers = [row["id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("candidate list has duplicate IDs")
    payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
    if any(byte > 0x7F for byte in payload.encode("utf-8")):
        raise ValueError("JSONL payload is not ASCII-only")
    summary = {
        "row_count": len(rows),
        "unique_id_count": len(set(identifiers)),
        "deferred_review_id_count": len(DEFERRED_REVIEW_IDS),
        "existing_direct_candidate_id_count": len(existing_direct),
        "existing_semantic_candidate_id_count": len(existing_semantic),
        "overlap_with_existing_candidate_ids": [],
        "live_steam_ko_sha256": file_hashes["live_steam_ko"],
        "pristine_pc_jp_sha256": file_hashes["pristine_pc_jp"],
        "source_gates": "all_exact_match",
        "current_ko_gates": "all_exact_match",
        "format_validation": "all_runtime_printf_esc_newline_and_whitespace_profiles_match",
        "json_encoding": "ensure_ascii_true_utf8",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
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
