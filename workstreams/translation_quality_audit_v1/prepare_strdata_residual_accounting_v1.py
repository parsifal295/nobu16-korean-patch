#!/usr/bin/env python3
"""Account for every CJK/Kana residual in live strdata Korean text.

The script writes two review-only ASCII JSONL artifacts below ``tmp``:

* a source-free 45-coordinate accounting ledger; and
* seven source-gated, high-confidence Korean replacements.

The other 38 coordinates are not silently ignored: 23 already have direct
proposal rows, nine are Japanese-IME-only strings unused by SC/TC, and six
are official credits retained verbatim to preserve names and attribution.
No game resource is written and no Switch/historic Korean data is read.
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
    / "MSG"
    / "JP"
    / "strdata.bin"
)
LIVE_ROOT = STEAM / "MSG"
TMP_ROOT = REPO / "tmp"
DIRECT_PROPOSALS = TMP_ROOT / "translation_quality_audit_v1" / "proposals" / "strdata_ko.jsonl"
SEMANTIC_PROPOSALS = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "strdata_quality_findings.v1.jsonl"
ACCOUNTING_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "strdata_japanese_residual_accounting.v1.jsonl"
FINDINGS_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "strdata_residual_findings.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata  # noqa: E402


KANA_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")


@dataclass(frozen=True)
class Candidate:
    before: str
    after: str
    source_marker: str
    rationale: str


# These are the only seven uncovered residuals safe to change without a style
# policy or credit-holder authorization.  The five numeric values sit in a
# one-to-ten Korean number sequence; the two 月 glyphs are month units in live
# Korean UI strings while their special icons remain untouched.
HIGH_CONFIDENCE: dict[tuple[int, int], Candidate] = {
    (1, 461): Candidate("二", "이", "二", "일·사·육·팔 등과 같은 한글 숫자열에서 남은 ‘이’ 표기다."),
    (1, 462): Candidate("三", "삼", "三", "일·사·육·팔 등과 같은 한글 숫자열에서 남은 ‘삼’ 표기다."),
    (1, 464): Candidate("五", "오", "五", "일·사·육·팔 등과 같은 한글 숫자열에서 남은 ‘오’ 표기다."),
    (1, 466): Candidate("七", "칠", "七", "일·사·육·팔 등과 같은 한글 숫자열에서 남은 ‘칠’ 표기다."),
    (1, 468): Candidate("九", "구", "九", "일·사·육·팔 등과 같은 한글 숫자열에서 남은 ‘구’ 표기다."),
    (1, 3477): Candidate("/月", "/월", "月", "군단 수치의 月은 한국어 월 단위로 표기해야 한다."),
    (1, 3478): Candidate("/月", "/월", "月", "군단 수치의 月은 한국어 월 단위로 표기해야 한다."),
}


# SC/TC parallel strings are blank for these Japanese IME keyboard labels, so
# they are not ordinary localized UI.  Preserve them until a Korean input-mode
# rendering policy and runtime test exist.
IME_ONLY_HOLD = {
    (1, 1921),
    (1, 1923),
    (1, 1924),
    (1, 1927),
    (1, 1928),
    (1, 1929),
    (1, 1930),
    (1, 1931),
    (1, 1932),
}


# These six strings are the official end-credit blocks.  They include staff
# names, legal company names, and licensed attributions; translating them
# would change proper names/credit wording rather than localize game text.
OFFICIAL_CREDIT_HOLD = {(4, identifier) for identifier in range(0, 6)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


def direct_proposal_rows() -> dict[tuple[int, int], dict[str, object]]:
    if not DIRECT_PROPOSALS.is_file():
        raise ValueError(f"direct proposal file is absent: {DIRECT_PROPOSALS}")
    rows: dict[tuple[int, int], dict[str, object]] = {}
    for number, line in enumerate(DIRECT_PROPOSALS.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        try:
            coordinate = (int(row["block"]), int(row["id"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"direct proposal row {number}: coordinate is absent") from exc
        if coordinate in rows:
            raise ValueError(f"direct proposal row {number}: duplicate coordinate {coordinate}")
        rows[coordinate] = row
    return rows


def semantic_coordinates() -> set[tuple[int, int]]:
    if not SEMANTIC_PROPOSALS.is_file():
        raise ValueError(f"semantic proposal file is absent: {SEMANTIC_PROPOSALS}")
    coordinates: set[tuple[int, int]] = set()
    for number, line in enumerate(SEMANTIC_PROPOSALS.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        coordinate = (int(row["block"]), int(row["id"]))
        if coordinate in coordinates:
            raise ValueError(f"semantic proposal row {number}: duplicate coordinate {coordinate}")
        coordinates.add(coordinate)
    return coordinates


def residual_counts(text: str) -> tuple[int, int]:
    return len(HAN_RE.findall(text)), len(KANA_RE.findall(text))


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
        "private_use": [f"U+{ord(character):04X}" for character in text if 0xE000 <= ord(character) <= 0xF8FF],
        "fullwidth_percent_count": text.count("％"),
        "question_marks": text.count("?"),
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


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    jp = load(PRISTINE_JP)
    ko = load(LIVE_ROOT / "JP" / "strdata.bin")
    sc = load(LIVE_ROOT / "SC" / "strdata.bin")
    tc = load(LIVE_ROOT / "TC" / "strdata.bin")
    if not (set(jp) == set(ko) == set(sc) == set(tc)):
        raise ValueError("strdata coordinates differ across PC resources")
    direct = direct_proposal_rows()
    semantic = semantic_coordinates()

    residual_coordinates = {
        coordinate for coordinate, text in ko.items() if HAN_RE.search(text) or KANA_RE.search(text)
    }
    direct_residual = set(direct).intersection(residual_coordinates)
    high_coordinates = set(HIGH_CONFIDENCE)
    hold_coordinates = IME_ONLY_HOLD | OFFICIAL_CREDIT_HOLD
    if high_coordinates.intersection(direct) or high_coordinates.intersection(semantic):
        raise ValueError("high-confidence residual candidates overlap existing proposals")
    if hold_coordinates.intersection(high_coordinates):
        raise ValueError("hold and candidate residual sets overlap")
    expected = direct_residual | high_coordinates | hold_coordinates
    if expected != residual_coordinates:
        unaccounted = sorted(residual_coordinates - expected)
        nonresidual = sorted(expected - residual_coordinates)
        raise ValueError(f"residual accounting mismatch; unaccounted={unaccounted}, nonresidual={nonresidual}")
    if len(direct_residual) != 23 or len(high_coordinates) != 7 or len(IME_ONLY_HOLD) != 9 or len(OFFICIAL_CREDIT_HOLD) != 6:
        raise ValueError("unexpected residual group cardinality")
    for coordinate in IME_ONLY_HOLD:
        if sc[coordinate].strip() or tc[coordinate].strip():
            raise ValueError(f"{coordinate}: expected blank SC/TC IME-only parallel strings")
    for coordinate in OFFICIAL_CREDIT_HOLD:
        if ko[coordinate] != jp[coordinate]:
            raise ValueError(f"{coordinate}: official credit target no longer matches pristine credit block")
    for coordinate, row in direct.items():
        if coordinate in direct_residual:
            if str(row.get("source_hash", "")) != text_hash(ko[coordinate]):
                raise ValueError(f"{coordinate}: existing direct proposal source hash is stale")

    ko_file_sha = sha256_file(LIVE_ROOT / "JP" / "strdata.bin")
    jp_file_sha = sha256_file(PRISTINE_JP)
    findings: list[dict[str, object]] = []
    accounting: list[dict[str, object]] = []
    for coordinate in sorted(residual_coordinates):
        current = ko[coordinate]
        han_count, kana_count = residual_counts(current)
        base = {
            "block": coordinate[0],
            "id": coordinate[1],
            "current_hash": text_hash(current),
            "han_glyph_count": han_count,
            "kana_glyph_count": kana_count,
        }
        if coordinate in direct_residual:
            accounting.append(
                {
                    **base,
                    "disposition": "covered_by_existing_direct_proposal",
                    "reason": "Existing strdata direct-proposal JSONL already contains a source-hash-gated Korean replacement.",
                }
            )
            continue
        if coordinate in IME_ONLY_HOLD:
            accounting.append(
                {
                    **base,
                    "disposition": "hold_japanese_ime_only",
                    "reason": "Current SC/TC parallel strings are blank, indicating a Japanese IME-only label rather than ordinary localized UI; hold pending Korean input-mode runtime policy.",
                }
            )
            continue
        if coordinate in OFFICIAL_CREDIT_HOLD:
            accounting.append(
                {
                    **base,
                    "disposition": "hold_official_credits",
                    "reason": "Official end-credit block with proper names/legal attributions; preserve verbatim pending explicit credit-localization authorization.",
                }
            )
            continue

        candidate = HIGH_CONFIDENCE[coordinate]
        if candidate.source_marker not in jp[coordinate]:
            raise ValueError(f"{coordinate}: expected pristine JP source marker is absent")
        if current.count(candidate.before) != 1:
            raise ValueError(f"{coordinate}: expected one current fragment, found {current.count(candidate.before)}")
        proposed = current.replace(candidate.before, candidate.after, 1)
        current_profile = profile(current)
        proposed_profile = profile(proposed)
        source_profile = profile(jp[coordinate])
        checks = {
            "escape_tags_match": current_profile["escape_tags"] == proposed_profile["escape_tags"],
            "runtime_tokens_match": current_profile["runtime_tokens"] == proposed_profile["runtime_tokens"],
            "printf_tokens_match": current_profile["printf"] == proposed_profile["printf"],
            "newlines_match": current_profile["newlines"] == proposed_profile["newlines"],
            "outer_ascii_whitespace_match": current_profile["outer_ascii_whitespace"] == proposed_profile["outer_ascii_whitespace"],
            "private_use_match": current_profile["private_use"] == proposed_profile["private_use"],
            "fullwidth_percent_count_match": current_profile["fullwidth_percent_count"] == proposed_profile["fullwidth_percent_count"],
            "question_marks_unchanged": current_profile["question_marks"] == proposed_profile["question_marks"],
            "hangul_present": bool(HANGUL_RE.search(proposed)),
            "no_han_or_kana_residual": not bool(HAN_RE.search(proposed) or KANA_RE.search(proposed)),
            "no_replacement_glyph": "\ufffd" not in proposed,
            "no_repeated_question_marks": "??" not in proposed,
        }
        if not all(checks.values()):
            raise ValueError(f"{coordinate}: high-confidence proposal validation failed")
        findings.append(
            {
                "block": coordinate[0],
                "id": coordinate[1],
                "ko": current,
                "proposed_ko": proposed,
                "current_hash": text_hash(current),
                "source_file_sha256": ko_file_sha,
                "pristine_jp_file_sha256": jp_file_sha,
                "issue_type": "잔존 일본어 표기",
                "rationale": candidate.rationale,
                "source_marker_validation": "match",
                "format_profile": {
                    "current": current_profile,
                    "proposed": proposed_profile,
                    "pristine_jp": source_profile,
                },
                "format_validation": {**checks, "all_required_checks_pass": True},
            }
        )
        accounting.append(
            {
                **base,
                "disposition": "high_confidence_candidate",
                "reason": candidate.rationale,
            }
        )

    if len(accounting) != len(residual_coordinates) or len(findings) != len(HIGH_CONFIDENCE):
        raise ValueError("ledger or findings count mismatch")
    disposition_counts: dict[str, int] = {}
    for row in accounting:
        status = str(row["disposition"])
        disposition_counts[status] = disposition_counts.get(status, 0) + 1
    summary = {
        "residual_coordinate_count": len(residual_coordinates),
        "han_flag_coordinate_count": sum(bool(HAN_RE.search(ko[coordinate])) for coordinate in residual_coordinates),
        "kana_flag_coordinate_count": sum(bool(KANA_RE.search(ko[coordinate])) for coordinate in residual_coordinates),
        "accounting_row_count": len(accounting),
        "high_confidence_candidate_count": len(findings),
        "disposition_counts": disposition_counts,
        "direct_proposal_hashes": "all_match",
        "pristine_jp_pc_sha256": jp_file_sha,
        "live_steam_ko_sha256": ko_file_sha,
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return accounting, findings, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    accounting, findings, summary = build()
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        accounting_path = safe_under(ACCOUNTING_OUTPUT, TMP_ROOT)
        findings_path = safe_under(FINDINGS_OUTPUT, TMP_ROOT)
        atomic_write(accounting_path, "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in accounting))
        atomic_write(findings_path, "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in findings))
        print(
            json.dumps(
                {
                    **summary,
                    "accounting_output": str(accounting_path),
                    "accounting_output_bytes": accounting_path.stat().st_size,
                    "findings_output": str(findings_path),
                    "findings_output_bytes": findings_path.stat().st_size,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    for row in findings:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
