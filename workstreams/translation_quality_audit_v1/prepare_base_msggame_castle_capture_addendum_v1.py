#!/usr/bin/env python3
"""Prepare a source-gated base-PC battle-dialogue terminology addendum.

This review pass fixes only a narrow, repeatable issue: battlefield
``capture/take`` wording was translated as a literal physical ``drop``.  It
uses the pristine PC Japanese message file as the authority and treats PC
Simplified/Traditional Chinese as supplemental context when a matching
literal exists.  It neither reads nor uses a Switch Korean resource.

The generated review JSONL stays below ``tmp`` and may contain private source
context.  The generic correction builder later emits a source-free overlay
and never writes to the Steam installation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(REPO / "workstreams" / "msggame"))

from msggame_format import iter_literals, parse_packed_msggame  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
LIVE_KO = DEFAULT_STEAM_ROOT / "MSG" / "JP" / "msggame.bin"
PRISTINE_JP = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
REFERENCE_FILES = {
    "sc": DEFAULT_STEAM_ROOT / "MSG" / "SC" / "msggame.bin",
    "tc": DEFAULT_STEAM_ROOT / "MSG" / "TC" / "msggame.bin",
}
EXPECTED_PRISTINE_JP_FILE_SHA256 = "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"
TMP_ROOT = REPO / "tmp"
DEFAULT_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "base_msggame_castle_capture_addendum.v1.jsonl"
EXISTING_PROPOSALS = (
    TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "base_msggame_findings.v1.jsonl",
    TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "base_msggame_additional_findings.v1.jsonl",
)

KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
RUNTIME_TOKEN_RE = re.compile(r"\[[a-z]+\d+\]")
MALFORMED_RUNTIME_OPEN_RE = re.compile(r"\[\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)


@dataclass(frozen=True)
class Candidate:
    """A source-free, hash-gated proposal definition."""

    source_text_hash: str
    current_hash: str
    proposed_ko: str
    issue_type: str
    rationale: str


# These expected hashes pin the exact pristine Japanese source and the exact
# current Steam Korean text without embedding either text in a tracked file.
# Every proposed value is independently checked against both profiles below.
CANDIDATES: dict[str, Candidate] = {
    "7:1456:0": Candidate("C882C066F9CBE594886D329F8487E88202DE4444E7A58BB789011A7F417F5B6C", "91750DFF7E7CBC4AC457E631DA7254B534CE644E8D7E9D659DCBF05A2D4163AB", "\uc744\u0028\ub97c\u0029\u0020\ud568\ub77d\ud558\uc9c0\u0020\uc54a\uaca0\uc2b5\ub2c8\uae4c\u000a\uc218\ube44\uac00\u0020\uc81c\ubc95\u0020\uacac\uace0\ud558\uc624\ub098\u000a\ubb50\u002c\u0020\uc131\ud558\uc758\u0020\uad70\ubd80\ud130\u0020\uc81c\uc555\ud558\uba74\u0021", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; only the affected verb is corrected."),
    "7:1470:0": Candidate("9352143A89A146CADE3FEF25CA2AC4C8BA7BBEA68BD5DD4E86F4DB3256FDE946", "EAF74F4D240FB2B8698303BFBBBCF51CF80BD71A99EA37E9386B88C9C1A54C25", "\uc758\u0020\uc218\ube44\ub294\u0020\uc131\uac00\uc2dc\uad70\u000a\uc8fc\ubcc0\ubd80\ud130\u0020\ubb34\ub108\ub728\ub824\u000a\uc131\uc744\u0020\ud568\ub77d\ud558\ub294\u0020\uc218\ub85c\u0020\uac00\uc9c0", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; only the affected verb is corrected."),
    "7:1536:0": Candidate("C882C066F9CBE594886D329F8487E88202DE4444E7A58BB789011A7F417F5B6C", "91750DFF7E7CBC4AC457E631DA7254B534CE644E8D7E9D659DCBF05A2D4163AB", "\uc744\u0028\ub97c\u0029\u0020\ud568\ub77d\ud558\uc9c0\u0020\uc54a\uaca0\uc2b5\ub2c8\uae4c\u000a\uc218\ube44\uac00\u0020\uc81c\ubc95\u0020\uacac\uace0\ud558\uc624\ub098\u000a\ubb50\u002c\u0020\uc131\ud558\uc758\u0020\uad70\ubd80\ud130\u0020\uc81c\uc555\ud558\uba74\u0021", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; only the affected verb is corrected."),
    "7:1550:0": Candidate("9352143A89A146CADE3FEF25CA2AC4C8BA7BBEA68BD5DD4E86F4DB3256FDE946", "EAF74F4D240FB2B8698303BFBBBCF51CF80BD71A99EA37E9386B88C9C1A54C25", "\uc758\u0020\uc218\ube44\ub294\u0020\uc131\uac00\uc2dc\uad70\u000a\uc8fc\ubcc0\ubd80\ud130\u0020\ubb34\ub108\ub728\ub824\u000a\uc131\uc744\u0020\ud568\ub77d\ud558\ub294\u0020\uc218\ub85c\u0020\uac00\uc9c0", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; only the affected verb is corrected."),
    "7:2135:0": Candidate("84CD76CF421281D2A102E14A6AA23E9B20B2A652028A72FBB8B5AD4A4826FF13", "20812EC97A5F23AA2B55E29336104FE61914FCC35ECA8E8104B5680CE5800B4A", "\ud6c4\uc6d0\uad70\uc774\u0020\ub2ff\uae30\u0020\uc804\uc5d0\u000a\ud568\ub77d\ud574\u0020\ubc84\ub9ac\ub294\u0020\uac8c\ub2e4", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "7:2140:0": Candidate("1F566E373F5B180DA494613238FE15154051855A3DF95311321C1AFBA675E626", "57A8F28B42CC7A75F5876F93BD1B8D3FBC8462E79440C12CCE3560298DEE53DB", "\uc801\uc774\u0020\ub2e4\uac00\uc624\uae30\u0020\uc804\uc5d0\u000a\uc131\uc744\u0020\ud568\ub77d\ud558\uba74\u0020\ub41c\ub2e4\u0021", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "7:2144:0": Candidate("E7E3BD5183C9808A520AF5629C8AB549D93C4900CB3DFCC4592E5E5F24C8D0A5", "49DBAC817FE43FAC6DC2145495A8F19FEBB306B3A3081013975D1A6AE567B934", "\ud6c4\uc6d0\uad70\uc774\ub77c\ub2c8\u0020\uc131\uac00\uc2dc\ub2e4\u000a\uc131\uc744\u0020\uc11c\ub458\ub7ec\u0020\ud568\ub77d\ud574\uc57c\u0020\ud55c\ub2e4", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "7:2151:0": Candidate("7DF0FECA0B24C73F046481868FEB52FF57E3BB87113DEF549472C7DE0DCD9B8F", "5AE69E3F4D26B32D591D5B612FBB58E03837968B36D98E5F874C8A1880CB17F4", "\ud6c4\uc6d0\uad70\uc774\ub77c\uace0\u003f\u000a\ub3c4\ucc29\u0020\uc804\uc5d0\u0020\ud568\ub77d\ud558\uc790\u0021", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "7:2170:0": Candidate("FD62FEA55AC6C014C4BFBFCC880E54278DF39D04295CC77A1D024F3B6F59205D", "13B5D524219A56522633D321959ACAC0172FB646A468BEB4322D277BA7AE04A9", "\uc774\ub7f0\u0020\uc791\uc740\u0020\uc131\ucbe4\uc740\u000a\uae08\ubc29\u0020\ud568\ub77d\ud574\u0020\ubcf4\uc774\uaca0\uc2b5\ub2c8\ub2e4", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "7:2181:0": Candidate("D5A60A530CDD9A434259157065010FC699E561DC6C36609AF243A3532283EEFF", "F3ECE2C0A2DA19BD416F0F063647E0418F4A0803A0CC0392173C98CB3383F519", "\ud3ec\uc704\ubcf4\ub2e4\u0020\uac15\uacf5\uc774\u000a\ub354\u0020\ube68\ub9ac\u0020\ud568\ub77d\ud558\ub9ac\ub77c", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "7:2193:0": Candidate("630FB0488136C57A4ADA8C6EE6AAC2604CC34289F0222F3ADFEF610A888C9A63", "0385B5D62E4C51CD89F79FBB653FD0752D0F8A0556E7A828B7E40213C59B86E8", "\uc774\u0020\uc131\u002c\u0020\ud798\uc73c\ub85c\u0020\ubc00\uc5b4\ubd99\uc774\ub294\u0020\ud3b8\uc774\u000a\ube68\ub9ac\u0020\ud568\ub77d\ud560\u0020\uc218\u0020\uc788\ub2e4\uace0\u0020\ubd24\ub2e4", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "7:2203:0": Candidate("6D71593CF4BA6B652394A35C8C66564A683E7A96790168269E5DE20C9E7CADC0", "AE826764E707D6DB4E0046A2B17161875F28EA16BF6E7EB7E63FDC5D3B8246D5", "\ud6c4\uc6d0\uad70\u0020\ubcd1\ub825\ub3c4\u0020\ub300\uae30\ud558\uace0\u0020\uc788\ub2e4\u000a\uac15\uacf5\uc73c\ub85c\u0020\ud568\ub77d\ud574\uc57c\u0020\ud55c\ub2e4\u0021", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "7:2277:0": Candidate("08435D9A20E24F00E9F818539EB7BA3A72CFB4FB4216ADEB2CD4DAF4E10A031E", "37EF0A1CA3D01B98E695BE2B3C6B89E0C4C0C46EF84BD2176CC5144E4F6CBB9B", "\ud3ec\uc704\ub294\u0020\uc644\ub8cc\ub418\uc5c8\ub2e4\u000a\uc131\uc744\u0020\ud568\ub77d\ud558\uba74\u0020\ub05d\uc774\ub2e4", "castle_capture_terminology", "Military capture wording was rendered as a literal physical drop; the original line structure is retained."),
    "9:3662:0": Candidate("B9D7F5D60DD70BC4FB371F50C5483E9D9FD68F3016DDDB8CD8153513213BC634", "466931966D78FD766753565F4A19DBA7D5B4D4D39ACA82E2F72357D291CD8B44", "\uc804\ub825\uc740\u0020\ud638\uac01\uc774\ub77c\u0020\ud560\u0020\uc218\u0020\uc788\uaca0\uc2b5\ub2c8\ub2e4\u000a\uc694\uc9c0\ub97c\u0020\uc81c\uc555\ud574\u0020\uc801\uc758\u0020\uc0ac\uae30\ub97c\u0020\ub5a8\uc5b4\ub728\ub9ac\uba74\u000a\uc2b9\ub9ac\uac00\u0020\ubcf4\uc77c\u0020\uac83\uc785\ub2c8\ub2e4", "strategic_point_terminology", "A strategic point was treated as a fortress; the correction keeps the distinct morale verb unchanged."),
    "9:3666:0": Candidate("D6B2289872B223D83BBE628B0B82FF498650CCC71F9CA81F5049427A536668DE", "6EDE5DA7643F31CB1FCDBB1B40B570532ABD0A3DE6A89F7C8AC47D537F452E9B", "\uc804\ub825\uc740\u0020\ud638\uac01\uc774\uad70\uc694\u000a\uc694\uc9c0\ub97c\u0020\uc81c\uc555\ud574\u0020\uc801\uc758\u0020\uc0ac\uae30\ub97c\u0020\ub5a8\uc5b4\ub728\ub9ac\ub294\u0020\uac83\uc774\u000a\uad00\uac74\uc774\u0020\ub418\uaca0\uc9c0\uc694\u0021", "strategic_point_terminology", "A strategic point was treated as a fortress; the correction also restores the intended strategic-point label."),
    "9:3667:0": Candidate("DC528BEE41EA1AACEE5F0C3D18FDC6BE3C2C83E6637C660EB20B6F4EE46A92C4", "5A8161B0232AF55888EF1C7DCDD8BAA083A5EAE644525858DFAA73451131FC40", "\uc804\ub825\uc740\u0020\ubc31\uc911\uc9c0\uc138\uc785\ub2c8\ub2e4\u000a\uacf5\ub7b5\ud560\u0020\uc218\u0020\uc788\ub294\u0020\uc694\uc9c0\ubd80\ud130\u0020\uc81c\uc555\ud574\u0020\ub098\uac00\uba70\u000a\uc801\uc758\u0020\uc0ac\uae30\ub97c\u0020\ub5a8\uc5b4\ub728\ub9ac\uba74\u0020\uc2b9\uae30\uac00\u0020\ubcf4\uc77c\u0020\uac83\uc785\ub2c8\ub2e4", "strategic_point_terminology", "A strategic point was treated as a fortress; the correction retains the staged suppression meaning."),
    "15:910:2": Candidate("2FD500D82A7BEDFFDE546E42C4C20FBAE75D7D6F8E9A03EAF81459BA9460F116", "F8889CBDF7C4B9BFE5B0E19A55C8BDD1A61877337FC848EC8865019FE34CC999", "\uc740\u0028\ub294\u0029\u000a\uc815\uba74\uc73c\ub85c\u0020\uacf5\uaca9\ud574\uc11c\ub294\u0020\ud568\ub77d\ud558\uae30\u0020\uc5b4\ub835\ub2e4", "castle_capture_terminology", "A fortress-capture verb was rendered as a physical drop; the dynamic-name slot and line break are preserved."),
    "15:1215:0": Candidate("C5F50C9E94BCFE3D9344D04F4DAF7E601F1449A895CF170690A0570B4D0B82EB", "16305FA44BFBA934DA29C6590616092D079D304F8517E8AE34134DAAD7D108E1", "\uc774\ubc88\u0020\uc131\u0020\uacf5\uaca9\uc740\u000a\ub545\uad74\u0020\uacf5\uaca9\uc73c\ub85c\u0020\ud558\uaca0\uc18c\u000a\uc798\u0020\ud480\ub9ac\uba74\u0020\uae08\uc138\u0020\uc131\uc744\u0020\ud568\ub77d\ud560\u0020\uc218\u0020\uc788\uc744\u0020\uac83\uc774\uc624", "castle_capture_terminology", "A fortress-capture verb was rendered as a physical drop; the original three-line structure is preserved."),
}

# One line carries an unchanged preceding literal plus a dynamic-name literal.
# Only its final literal is altered, and the exact three-slot shape is checked
# on both the live Korean and pristine PC Japanese resource.
RECORD_CONTRACTS = {
    "15:910:2": ("15:910:0", "15:910:1", "15:910:2"),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def coordinate_sort_key(coordinate: str) -> tuple[int, int, int]:
    try:
        values = tuple(int(part) for part in coordinate.split(":"))
    except ValueError as exc:
        raise ValueError(f"invalid msggame coordinate: {coordinate}") from exc
    if len(values) != 3 or any(value < 0 for value in values):
        raise ValueError(f"invalid msggame coordinate: {coordinate}")
    return values


def record_key(coordinate: str) -> str:
    block, record, _literal = coordinate_sort_key(coordinate)
    return f"{block}:{record}"


def parse_literals(path: Path) -> tuple[dict[str, str], dict[str, list[str]]]:
    archive = parse_packed_msggame(path.read_bytes()).archive
    texts: dict[str, str] = {}
    records: dict[str, list[str]] = defaultdict(list)
    for literal in iter_literals(archive):
        coordinate = f"{literal.block_id}:{literal.record_id}:{literal.literal_id}"
        if coordinate in texts:
            raise ValueError(f"duplicate literal coordinate in {path}: {coordinate}")
        texts[coordinate] = literal.text
        records[f"{literal.block_id}:{literal.record_id}"].append(coordinate)
    for coordinates in records.values():
        coordinates.sort(key=coordinate_sort_key)
    return texts, dict(records)


def profile(text: str) -> dict[str, Any]:
    esc_offsets = {offset for match in ESC_RE.finditer(text) for offset in range(match.start(), match.end())}
    return {
        "runtime_tokens": RUNTIME_TOKEN_RE.findall(text),
        "malformed_runtime_open_count": len(MALFORMED_RUNTIME_OPEN_RE.findall(text)),
        "printf_tokens": PRINTF_RE.findall(text),
        "escape_tags": ESC_RE.findall(text),
        "line_breaks": re.findall(r"\r\n|\n|\r", text),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "private_use": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "controls": [
            f"U+{ord(char):04X}"
            for index, char in enumerate(text)
            if unicodedata.category(char) == "Cc" and char not in ("\r", "\n") and index not in esc_offsets
        ],
        "fullwidth_percent_count": text.count("\uff05"),
        "marker_334d_count": text.count("\u334d"),
    }


def read_existing_coordinates() -> set[str]:
    existing: set[str] = set()
    for path in EXISTING_PROPOSALS:
        if not path.is_file():
            raise ValueError(f"existing reviewed proposal is absent: {path}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            coordinate = row.get("coordinate")
            if not isinstance(coordinate, str):
                raise ValueError(f"existing proposal coordinate is invalid: {path}:{line_number}")
            existing.add(coordinate)
    return existing


def safe_under(path: Path, root: Path) -> Path:
    value = path.resolve()
    checked_root = root.resolve()
    if value == checked_root or checked_root not in value.parents:
        raise ValueError(f"output must remain below {checked_root}")
    return value


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
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if sha256_file(PRISTINE_JP) != EXPECTED_PRISTINE_JP_FILE_SHA256:
        raise ValueError("pristine PC Japanese base msggame hash differs")
    live, live_records = parse_literals(LIVE_KO)
    pristine, pristine_records = parse_literals(PRISTINE_JP)
    references = {language: parse_literals(path)[0] for language, path in REFERENCE_FILES.items()}
    existing = read_existing_coordinates()
    overlap = sorted(existing.intersection(CANDIDATES), key=coordinate_sort_key)
    if overlap:
        raise ValueError(f"castle-capture addendum overlaps an existing candidate: {overlap}")

    file_hashes = {
        "live_steam_ko": sha256_file(LIVE_KO),
        "pristine_pc_jp": sha256_file(PRISTINE_JP),
        **{language: sha256_file(path) for language, path in REFERENCE_FILES.items()},
    }
    rows: list[dict[str, Any]] = []
    for coordinate, candidate in sorted(CANDIDATES.items(), key=lambda pair: coordinate_sort_key(pair[0])):
        if coordinate not in live or coordinate not in pristine:
            raise ValueError(f"{coordinate}: absent from live Korean or pristine PC Japanese")
        source = pristine[coordinate]
        current = live[coordinate]
        if text_hash(source) != candidate.source_text_hash:
            raise ValueError(f"{coordinate}: pristine PC Japanese source hash gate failed")
        if text_hash(current) != candidate.current_hash:
            raise ValueError(f"{coordinate}: current Steam Korean hash gate failed")
        if current == candidate.proposed_ko:
            raise ValueError(f"{coordinate}: proposal is unchanged")
        expected_record = list(RECORD_CONTRACTS.get(coordinate, (coordinate,)))
        if live_records.get(record_key(coordinate)) != expected_record or pristine_records.get(record_key(coordinate)) != expected_record:
            raise ValueError(f"{coordinate}: adjacent-literal layout differs from the reviewed record contract")

        source_profile = profile(source)
        current_profile = profile(current)
        proposed_profile = profile(candidate.proposed_ko)
        format_checks = {
            "current_to_proposed": current_profile == proposed_profile,
            "pristine_jp_to_proposed": source_profile == proposed_profile,
            "hangul_present": bool(HANGUL_RE.search(candidate.proposed_ko)),
            "no_japanese_or_cjk_residue": not bool(KANA_OR_HAN_RE.search(candidate.proposed_ko)),
            "no_replacement_glyph": "\ufffd" not in candidate.proposed_ko,
        }
        if not all(format_checks.values()):
            raise ValueError(f"{coordinate}: format or replacement integrity validation failed")
        coverage = {language: ("present" if coordinate in texts else "absent") for language, texts in references.items()}
        rows.append(
            {
                "resource": "base_msggame",
                "coordinate": coordinate,
                "ko": current,
                "proposed_ko": candidate.proposed_ko,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "live_ko_file_sha256": file_hashes["live_steam_ko"],
                "pristine_jp_file_sha256": file_hashes["pristine_pc_jp"],
                "reference_file_sha256": {language: file_hashes[language] for language in REFERENCE_FILES},
                "issue_type": candidate.issue_type,
                "rationale": candidate.rationale,
                "source_gate_validation": "exact_utf16le_hash_match",
                "current_ko_gate_validation": "exact_utf16le_hash_match",
                "pc_target_contexts": {language: references[language].get(coordinate) for language in REFERENCE_FILES},
                "pc_target_context_coverage": coverage,
                "adjacent_literal_validation": {
                    "status": "record_layout_exact_in_live_and_pristine",
                    "record_literals": expected_record,
                    "edited_literal": coordinate,
                },
                "format_profile": {
                    "current_ko": current_profile,
                    "proposed_ko": proposed_profile,
                    "pristine_jp": source_profile,
                },
                "format_validation": {**format_checks, "all_required_checks_pass": True},
                "evidence_context": {
                    "switch_korean_translation_used": False,
                    "historic_korean_backup_used": False,
                    "authority": "pristine_PC_Japanese",
                },
                "game_files_written": False,
            }
        )

    coordinates = [row["coordinate"] for row in rows]
    if len(coordinates) != len(set(coordinates)):
        raise ValueError("candidate coordinates are not unique")
    summary = {
        "row_count": len(rows),
        "unique_coordinate_count": len(set(coordinates)),
        "overlap_with_existing_candidates": [],
        "live_steam_ko_sha256": file_hashes["live_steam_ko"],
        "pristine_pc_jp_sha256": file_hashes["pristine_pc_jp"],
        "source_gates": "all_exact_utf16le_hash_match",
        "current_ko_gates": "all_exact_utf16le_hash_match",
        "adjacent_literal_contract": "all_exact_match",
        "format_validation": "all_profiles_match",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="validate only; write no review file")
    parser.add_argument("--write", action="store_true", help="write the private review JSONL below tmp")
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
        payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")
        if any(byte > 0x7F for byte in payload):
            raise ValueError("private review JSONL is not ASCII-only")
        atomic_write(output, payload)
        print(json.dumps({**summary, "output": str(output), "output_bytes": output.stat().st_size}, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
