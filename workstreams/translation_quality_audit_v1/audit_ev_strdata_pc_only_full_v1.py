#!/usr/bin/env python3
"""Create a read-only PC-only coverage audit for base event text.

This generator reads pristine PC Japanese plus current PC Korean, Simplified
Chinese, and Traditional Chinese event tables.  It never opens a Switch Korean
file.  Existing generic-builder candidates are excluded by coordinate, and
only manually adjudicated, high-confidence corrections are emitted.

The audit artifact covers every remaining base-event coordinate.  Manual
line-break concerns and terminology/runtime-sensitive rows are HOLD records,
not automatic changes.  All writes stay under tmp.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_JP = Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root\MSG\JP\ev_strdata.bin")
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
SEMANTIC = AUDIT_ROOT / "semantic"
BUILDER = REPO / "workstreams" / "translation_quality_corrections_v1" / "build_translation_quality_corrections_v1.py"

DEFAULT_AUDIT_OUTPUT = SEMANTIC / "ev_strdata_pc_only_full_audit.v1.jsonl"
DEFAULT_CANDIDATE_OUTPUT = SEMANTIC / "ev_strdata_pc_only_quality_addendum.v1.jsonl"
DEFAULT_HOLD_OUTPUT = SEMANTIC / "ev_strdata_pc_only_ambiguous_holds.v1.jsonl"
DEFAULT_SUMMARY_OUTPUT = SEMANTIC / "ev_strdata_pc_only_full_audit_summary.v1.json"

PATHS = {
    "JP": PRISTINE_JP,
    "KO": STEAM / "MSG" / "JP" / "ev_strdata.bin",
    "SC": STEAM / "MSG" / "SC" / "ev_strdata.bin",
    "TC": STEAM / "MSG" / "TC" / "ev_strdata.bin",
}
EXPECTED_PRISTINE_JP_SHA256 = "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB"

RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)

# Terms whose source-side semantics are unusually easy to invert or flatten.
# They are triage cues only.  No candidate is generated from this list unless
# it is listed separately in CANDIDATES and passes its own PC-reference gates.
RISK_MARKERS: Mapping[str, tuple[str, ...]] = {
    "administration": ("知行", "所領", "当主", "本拠", "官位", "仲介"),
    "vassal_relation": ("陪臣", "家臣", "家来", "宿老", "小姓"),
    "inheritance": ("家督", "相続", "婿養子", "養子", "廃嫡", "隠居"),
    "war_outcome": ("討死", "戦死", "自害", "落城", "降伏", "滅亡", "攻落"),
    "intrigue": ("密談", "調略", "内応", "寝返り", "謀反", "離反", "出奔"),
    "religion": ("切腹", "出家", "寺社", "法名"),
    "confinement": ("幽閉", "追放", "投獄", "拘束"),
    "geography": ("国衆", "領国", "城下", "街道", "郡"),
    "captivity": ("捕縛", "捕虜", "人質", "監視"),
    "clarity_homonym": ("反徒", "忍従", "示し"),
}
CONVENTION_HOLD_MARKERS = ("調略", "知行", "所領", "宿老", "婿養子", "養子")

# These were observed as source-visible manual line breaks immediately before
# a Korean particle or connective.  They remain isolated HOLD records because
# fixing layout requires the separate event reflow and real-game QA workflow.
MANUAL_LINEBREAK_HOLDS: Mapping[int, tuple[str, str]] = {
    4558: ("실력\n과", "manual break before connective particle 과"),
    4769: ("교고쿠가\x1bCZ\n와", "manual break before topic/coordination particle 와"),
    5155: ("한베에\x1bCZ\n를", "manual break before object particle 를"),
    5403: ("배반\n으로", "manual break before connective 으로"),
    5492: ("있다\n는", "manual break before quoted topic suffix 는"),
    6365: ("차\n 를", "manual break before object particle 를"),
    6401: ("이치조가\x1bCZ\n가", "manual break before subject particle 가"),
    9580: ("원한다\n는", "manual break before quoted topic suffix 는"),
    9585: ("위해\n가", "manual break before subject particle 가"),
}


@dataclass(frozen=True)
class Candidate:
    identifier: int
    old: str
    new: str
    source_markers: tuple[str, ...]
    sc_markers: tuple[str, ...]
    tc_markers: tuple[str, ...]
    issue_type: str
    rationale: str


CANDIDATES = (
    Candidate(
        3765,
        "반도의 진압은",
        "반란 진압은",
        ("反徒",),
        ("叛乱分子",),
        ("平叛",),
        "rebel_term_clarity_not_geographic_peninsula",
        "The source says suppression of rebels. 반도 is a historical reading but commonly reads as peninsula; 반란 진압 states the source meaning plainly and shortens the sentence.",
    ),
    Candidate(
        3986,
        "\x1bCZ 는",
        "\x1bCZ는",
        (),
        (),
        (),
        "korean_subject_particle_spacing",
        "A visible Korean subject particle is detached from the preceding tagged name. The source meaning and runtime tag remain unchanged.",
    ),
    Candidate(
        4166,
        "본이 서지 않사옵니다",
        "본이 되지 않사옵니다",
        ("示し",),
        ("表率",),
        (),
        "cannot_set_an_example_korean_idiom",
        "The Japanese means that one cannot set an example for the household. 본이 되지 않다 is the ordinary Korean construction for that meaning.",
    ),
    Candidate(
        4298,
        "반도를 안고",
        "반란군을 안고",
        ("反徒",),
        ("叛徒",),
        ("叛徒",),
        "rebel_group_clarity_not_geographic_peninsula",
        "The internal threat is a group of rebels, not a peninsula. 반란군 removes the Korean homonym while preserving the surrounding event layout.",
    ),
    Candidate(
        4317,
        "바람직하다 는",
        "바람직하다는",
        (),
        (),
        (),
        "korean_quoted_clause_spacing",
        "The visible Korean quoted-clause suffix is incorrectly separated by a space. Only that spacing is repaired.",
    ),
    Candidate(
        4814,
        "인종의 나날",
        "굴종의 나날",
        ("忍従",),
        ("隐忍",),
        ("隱忍",),
        "forced_endurance_clarity_not_race_homonym",
        "The sentence says the clan was forced into prolonged 忍従. 굴종의 나날 expresses compelled subordination without the ordinary Korean race reading of 인종.",
    ),
    Candidate(
        5140,
        "본보기도 서지 않는다",
        "본이 되지 않는다",
        ("示し",),
        ("表率",),
        ("表率",),
        "cannot_set_an_example_korean_idiom",
        "The source says he cannot serve as an example to the Mino local lords. 본이 되지 않는다 is the natural Korean expression.",
    ),
    Candidate(
        5160,
        "소동 은",
        "소동은",
        (),
        (),
        (),
        "korean_topic_particle_spacing",
        "The visible Korean topic particle is detached by a space. The correction changes no source meaning or event formatting.",
    ),
    Candidate(
        5200,
        "수라의 땅이 된다, 인가 귀공의 말은 지당하다만…",
        "수라의 땅이 되는가? 귀공의 말은 지당하나…",
        ("修羅の地",),
        ("修罗之地",),
        ("修羅之地",),
        "question_and_concession_sentence_repaired",
        "The source asks whether Echigo will again become a land of endless war, then concedes the point. The current Korean has a broken question and connective; this restores both relations.",
    ),
    Candidate(
        5319,
        "사내 가",
        "사내가",
        (),
        (),
        (),
        "korean_subject_particle_spacing",
        "The visible Korean subject particle is incorrectly separated. Only that local spacing is repaired.",
    ),
    Candidate(
        5574,
        "따라온다, 는",
        "따라온다는",
        (),
        (),
        (),
        "korean_quoted_clause_spacing",
        "The Korean quoted-clause suffix is detached after the report punctuation. The correction joins the suffix without changing line breaks.",
    ),
    Candidate(
        9529,
        "이으라 는",
        "이으라는",
        (),
        (),
        (),
        "korean_quoted_directive_spacing",
        "The Korean quotative suffix after the inheritance directive is visibly detached. The correction joins it and preserves every non-text field.",
    ),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


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


def deterministic_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def parse_common(path: Path) -> dict[int, str]:
    tools = REPO / "tools"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table

    _header, raw = decompress_wrapper(path.read_bytes())
    return {index: text for index, text in enumerate(parse_message_table(raw).texts)}


def format_profile(value: str) -> dict[str, Any]:
    escaped_offsets = {index for match in ESC_RE.finditer(value) for index in range(match.start(), match.end())}
    return {
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "escape_tags": ESC_RE.findall(value),
        "line_breaks": LINEBREAK_RE.findall(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "private_use": [f"U+{ord(character):04X}" for character in PRIVATE_USE_RE.findall(value)],
        "controls": [
            f"U+{ord(character):04X}"
            for index, character in enumerate(value)
            if ord(character) < 32 and character not in ("\r", "\n") and index not in escaped_offsets
        ],
        "fullwidth_percent_count": value.count("％"),
        "marker_334d_count": value.count("㌍"),
    }


def visible_text(value: str) -> str:
    return RUNTIME_RE.sub("", ESC_RE.sub("", value))


def visible_line_lengths(value: str) -> list[int]:
    return [len(line) for line in LINEBREAK_RE.split(visible_text(value))]


def risk_categories(source: str) -> list[str]:
    return sorted(category for category, markers in RISK_MARKERS.items() if any(marker in source for marker in markers))


def load_builder_module() -> Any:
    if not BUILDER.is_file():
        raise ValueError(f"generic correction builder is absent: {BUILDER}")
    for dependency in (REPO / "tools", REPO / "workstreams" / "strdata", REPO / "workstreams" / "msggame"):
        if str(dependency) not in sys.path:
            sys.path.insert(0, str(dependency))
    module_name = "_ev_strdata_pc_only_audit_builder"
    module_spec = importlib.util.spec_from_file_location(module_name, BUILDER)
    if module_spec is None or module_spec.loader is None:
        raise ValueError(f"unable to import generic correction builder: {BUILDER}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    return module


def active_builder_ids(candidate_output: Path) -> set[int]:
    module = load_builder_module()
    try:
        original = next(spec for spec in module.SPECS if spec.name == "ev_strdata")
        paths = tuple(
            path
            for path in original.proposal_paths
            if path.resolve(strict=False) != candidate_output.resolve(strict=False)
        )
        rows = module.read_proposals(replace(original, proposal_paths=paths))
    finally:
        sys.modules.pop("_ev_strdata_pc_only_audit_builder", None)
    identifiers: set[int] = set()
    for row in rows:
        coordinate = row.get("coordinate")
        try:
            identifier = int(coordinate)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"ev_strdata builder coordinate is not numeric: {coordinate!r}") from exc
        if identifier in identifiers:
            raise ValueError(f"duplicate active ev_strdata builder coordinate: {identifier}")
        identifiers.add(identifier)
    return identifiers


def candidate_row(
    change: Candidate,
    source: str,
    current: str,
    references: Mapping[str, str],
    file_hashes: Mapping[str, str],
) -> dict[str, Any]:
    if current.count(change.old) != 1:
        raise ValueError(f"candidate source fragment differs at ev_strdata:{change.identifier}")
    if not all(marker in source for marker in change.source_markers):
        raise ValueError(f"JP source marker differs at ev_strdata:{change.identifier}")
    if not all(marker in references["SC"] for marker in change.sc_markers):
        raise ValueError(f"PC SC marker differs at ev_strdata:{change.identifier}")
    if not all(marker in references["TC"] for marker in change.tc_markers):
        raise ValueError(f"PC TC marker differs at ev_strdata:{change.identifier}")
    proposed = current.replace(change.old, change.new)
    before_profile = format_profile(current)
    after_profile = format_profile(proposed)
    if before_profile != after_profile:
        raise ValueError(f"protected format profile differs at ev_strdata:{change.identifier}")
    before_lengths = visible_line_lengths(current)
    after_lengths = visible_line_lengths(proposed)
    if len(before_lengths) != len(after_lengths):
        raise ValueError(f"manual event line count differs at ev_strdata:{change.identifier}")
    if any(after > before + 1 for before, after in zip(before_lengths, after_lengths)):
        raise ValueError(f"candidate grows a visible event line by more than one cell at ev_strdata:{change.identifier}")
    if KANA_OR_HAN_RE.search(proposed) or "\0" in proposed or "\ufffd" in proposed:
        raise ValueError(f"unsafe Korean candidate at ev_strdata:{change.identifier}")
    return {
        "allowed_format_delta": [],
        "confidence": "high",
        "current_hash": text_hash(current),
        "format_validation": {
            "all_nontext_format_fields": "match",
            "candidate_visible_line_lengths": after_lengths,
            "current_visible_line_lengths": before_lengths,
            "manual_line_count": len(after_lengths),
            "manual_line_count_matches_current": True,
            "max_visible_line_growth_cells": max((after - before for before, after in zip(before_lengths, after_lengths)), default=0),
        },
        "id": change.identifier,
        "issue_type": change.issue_type,
        "jp_source_hash": text_hash(source),
        "ko": current,
        "pc_semantic_evidence": {
            "jp_terms": list(change.source_markers),
            "pc_sc_terms": list(change.sc_markers),
            "pc_tc_terms": list(change.tc_markers),
        },
        "proposed_ko": proposed,
        "rationale": change.rationale,
        "reference_basis": ["pristine_pc_jp", "pc_sc", "pc_tc"],
        "reference_file_sha256": dict(file_hashes),
        "resource": "ev_strdata",
        "source_file_sha256": file_hashes["JP"],
        "steam_ko_file_sha256": file_hashes["KO"],
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }


def hold_reasons(identifier: int, source: str, current: str, risks: list[str]) -> list[str]:
    reasons: list[str] = []
    manual = MANUAL_LINEBREAK_HOLDS.get(identifier)
    if manual is not None:
        fragment, description = manual
        if fragment not in current:
            raise ValueError(f"manual line-break hold predicate differs at ev_strdata:{identifier}")
        reasons.append(description)
    convention_terms = [marker for marker in CONVENTION_HOLD_MARKERS if marker in source]
    if convention_terms:
        reasons.append("historical terminology needs a resource-wide Korean convention: " + ", ".join(convention_terms))
    if (RUNTIME_RE.search(source) or RUNTIME_RE.search(current)) and risks:
        reasons.append("runtime name token occurs with a high-risk semantic category; retain for contextual review")
    if "clarity_homonym" in risks:
        reasons.append("source term has a Korean homonym or idiom choice; retain unless individually adjudicated")
    return reasons


def build_rows(candidate_output: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    for language, path in PATHS.items():
        if not path.is_file():
            raise ValueError(f"required PC {language} event resource is absent: {path}")
    file_hashes = {language: sha256_file(path) for language, path in PATHS.items()}
    if file_hashes["JP"] != EXPECTED_PRISTINE_JP_SHA256:
        raise ValueError("pristine PC Japanese ev_strdata hash differs; rebase the audit before use")
    tables = {language: parse_common(path) for language, path in PATHS.items()}
    coordinate_set = set(tables["JP"])
    if not coordinate_set:
        raise ValueError("pristine PC Japanese ev_strdata is empty")
    if any(set(table) != coordinate_set for table in tables.values()):
        raise ValueError("PC ev_strdata language coordinate sets differ")

    active_ids = active_builder_ids(candidate_output)
    if not active_ids.issubset(coordinate_set):
        raise ValueError("active generic-builder coordinate is outside ev_strdata inventory")
    candidates_by_id = {candidate.identifier: candidate for candidate in CANDIDATES}
    if len(candidates_by_id) != len(CANDIDATES):
        raise ValueError("reviewed candidate ids are not unique")
    if set(candidates_by_id).intersection(active_ids):
        overlap = sorted(set(candidates_by_id).intersection(active_ids))
        raise ValueError(f"new PC-only candidates overlap active generic-builder coordinates: {overlap}")
    if set(candidates_by_id).intersection(MANUAL_LINEBREAK_HOLDS):
        raise ValueError("manual line-break HOLD id overlaps a candidate")
    if not set(MANUAL_LINEBREAK_HOLDS).issubset(coordinate_set - active_ids):
        raise ValueError("manual line-break HOLD id is excluded or absent")

    candidate_rows: list[dict[str, Any]] = []
    for identifier in sorted(candidates_by_id):
        candidate = candidates_by_id[identifier]
        candidate_rows.append(
            candidate_row(
                candidate,
                tables["JP"][identifier],
                tables["KO"][identifier],
                {"SC": tables["SC"][identifier], "TC": tables["TC"][identifier]},
                file_hashes,
            )
        )

    audit_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    residual_cjk_ids: list[int] = []
    short_ratio_ids: list[int] = []
    source_to_korean: defaultdict[str, set[str]] = defaultdict(set)
    audited_ids = sorted(coordinate_set - active_ids)
    for identifier in audited_ids:
        source = tables["JP"][identifier]
        current = tables["KO"][identifier]
        source_to_korean[source].add(current)
        risks = risk_categories(source)
        source_visible = visible_text(source).replace("\r", "").replace("\n", "")
        korean_visible = visible_text(current).replace("\r", "").replace("\n", "")
        short_ratio = len(korean_visible) / len(source_visible) if source_visible else None
        flags: list[str] = []
        if short_ratio is not None and len(source_visible) >= 30 and short_ratio < 0.43:
            flags.append("short_korean_vs_japanese_visible_length")
            short_ratio_ids.append(identifier)
        if KANA_OR_HAN_RE.search(current):
            flags.append("cjk_or_kana_residual_in_korean")
            residual_cjk_ids.append(identifier)
        if identifier in candidates_by_id:
            disposition = "candidate_high_confidence"
            detail = candidates_by_id[identifier].issue_type
            reasons: list[str] = []
        else:
            reasons = hold_reasons(identifier, source, current, risks)
            if reasons:
                disposition = "hold_manual_linebreak_layout" if identifier in MANUAL_LINEBREAK_HOLDS else "hold_ambiguous_or_runtime"
                detail = "; ".join(reasons)
            else:
                disposition = "retained_after_pc_only_triage"
                detail = "no manually verified high-confidence meaning, grammar, proper-name, quantity, or effect correction"
        row = {
            "schema": "nobu16.kr.ev-strdata-pc-only-full-audit.v1",
            "resource": "ev_strdata",
            "id": identifier,
            "disposition": disposition,
            "disposition_detail": detail,
            "risk_categories": risks,
            "heuristic_flags": flags,
            "source_jp": source,
            "source_jp_utf16le_sha256": text_hash(source),
            "current_ko": current,
            "current_ko_utf16le_sha256": text_hash(current),
            "reference_contexts": {"SC": tables["SC"][identifier], "TC": tables["TC"][identifier]},
            "source_file_sha256": file_hashes["JP"],
            "current_file_sha256": file_hashes["KO"],
            "reference_file_sha256": {"SC": file_hashes["SC"], "TC": file_hashes["TC"]},
            "audit_scope": {
                "pristine_pc_japanese": True,
                "current_pc_korean": True,
                "pc_sc_tc_references": True,
                "switch_korean_read": False,
                "historic_korean_read": False,
                "steam_game_resource_written": False,
            },
        }
        audit_rows.append(row)
        if reasons:
            hold_rows.append(
                {
                    "schema": "nobu16.kr.ev-strdata-pc-only-hold.v1",
                    "resource": "ev_strdata",
                    "id": identifier,
                    "hold_kind": "manual_linebreak_layout" if identifier in MANUAL_LINEBREAK_HOLDS else "ambiguous_or_runtime",
                    "hold_reasons": reasons,
                    "risk_categories": risks,
                    "source_jp": source,
                    "current_ko": current,
                    "reference_contexts": {"SC": tables["SC"][identifier], "TC": tables["TC"][identifier]},
                    "source_jp_utf16le_sha256": text_hash(source),
                    "current_ko_utf16le_sha256": text_hash(current),
                    "switch_korean_translation_used": False,
                    "historic_korean_translation_used": False,
                    "game_files_written": False,
                }
            )

    inconsistent_source_ids = sorted(
        identifier
        for identifier in audited_ids
        if len(source_to_korean[tables["JP"][identifier]]) > 1 and tables["JP"][identifier]
    )
    summary = {
        "schema": "nobu16.kr.ev-strdata-pc-only-full-audit-summary.v1",
        "audit_method": "full coordinate coverage with PC-only lexical-risk triage and manually adjudicated candidate/hold partitions",
        "inventory_coordinate_count": len(coordinate_set),
        "excluded_active_generic_builder_coordinate_count": len(active_ids),
        "audited_coordinate_count": len(audit_rows),
        "audited_nonempty_source_or_korean_count": sum(
            1 for row in audit_rows if row["source_jp"] or row["current_ko"]
        ),
        "new_high_confidence_candidate_count": len(candidate_rows),
        "candidate_ids": [row["id"] for row in candidate_rows],
        "hold_count": len(hold_rows),
        "manual_linebreak_hold_count": sum(1 for row in hold_rows if row["hold_kind"] == "manual_linebreak_layout"),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in audit_rows).items())),
        "risk_category_counts": dict(
            sorted(
                Counter(
                    category
                    for row in audit_rows
                    for category in row["risk_categories"]
                ).items()
            )
        ),
        "diagnostics": {
            "cjk_or_kana_residual_in_audited_current_korean_count": len(residual_cjk_ids),
            "short_korean_visible_length_flag_count": len(short_ratio_ids),
            "same_japanese_source_with_multiple_current_korean_targets_count": len(set(inconsistent_source_ids)),
        },
        "pc_file_sha256": file_hashes,
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
        "candidate_output_intended_generic_builder_path": str(candidate_output),
    }
    return audit_rows, candidate_rows, hold_rows, summary


def validate_rows(
    audit_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    audit_ids = [row["id"] for row in audit_rows]
    if len(audit_ids) != len(set(audit_ids)):
        raise ValueError("audit contains duplicate coordinates")
    if audit_ids != sorted(audit_ids):
        raise ValueError("audit coordinate order is not deterministic")
    candidate_ids = {candidate.identifier for candidate in CANDIDATES}
    if {row["id"] for row in candidate_rows} != candidate_ids:
        raise ValueError("candidate output differs from the manually reviewed set")
    if len(hold_rows) != len({row["id"] for row in hold_rows}):
        raise ValueError("hold output contains duplicate coordinates")
    if candidate_ids.intersection(row["id"] for row in hold_rows):
        raise ValueError("candidate is incorrectly present in a HOLD output")
    if not set(MANUAL_LINEBREAK_HOLDS).issubset({row["id"] for row in hold_rows}):
        raise ValueError("manual line-break HOLD partition is incomplete")
    for candidate in candidate_rows:
        if candidate["ko"] == candidate["proposed_ko"] or text_hash(candidate["ko"]) != candidate["current_hash"]:
            raise ValueError(f"candidate hash/current gate differs at ev_strdata:{candidate['id']}")
        if format_profile(candidate["ko"]) != format_profile(candidate["proposed_ko"]):
            raise ValueError(f"candidate format profile differs at ev_strdata:{candidate['id']}")
        if KANA_OR_HAN_RE.search(candidate["proposed_ko"]):
            raise ValueError(f"candidate retains CJK/Kana at ev_strdata:{candidate['id']}")
        if candidate["switch_korean_translation_used"] or candidate["historic_korean_translation_used"]:
            raise ValueError(f"candidate scope is not PC-only at ev_strdata:{candidate['id']}")
    for row in audit_rows:
        scope = row["audit_scope"]
        if scope["switch_korean_read"] or scope["historic_korean_read"] or scope["steam_game_resource_written"]:
            raise ValueError(f"audit scope is not PC-only at ev_strdata:{row['id']}")
    if summary["audited_coordinate_count"] != len(audit_rows):
        raise ValueError("audit summary count differs")
    if summary["new_high_confidence_candidate_count"] != len(candidate_rows):
        raise ValueError("candidate summary count differs")
    if summary["hold_count"] != len(hold_rows):
        raise ValueError("hold summary count differs")
    if summary["inventory_coordinate_count"] != (
        summary["excluded_active_generic_builder_coordinate_count"] + summary["audited_coordinate_count"]
    ):
        raise ValueError("inventory partition is incomplete")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE_OUTPUT)
    parser.add_argument("--hold-output", type=Path, default=DEFAULT_HOLD_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY_OUTPUT)
    parser.add_argument("--write", action="store_true", help="write private deterministic audit artifacts")
    parser.add_argument("--validate", action="store_true", help="compare existing outputs with generated deterministic content")
    args = parser.parse_args()

    outputs = {
        "audit": safe_under(args.audit_output, AUDIT_ROOT),
        "candidate": safe_under(args.candidate_output, AUDIT_ROOT),
        "hold": safe_under(args.hold_output, AUDIT_ROOT),
        "summary": safe_under(args.summary_output, AUDIT_ROOT),
    }
    audit_rows, candidate_rows, hold_rows, summary = build_rows(outputs["candidate"])
    validate_rows(audit_rows, candidate_rows, hold_rows, summary)
    payloads = {
        "audit": deterministic_jsonl(audit_rows),
        "candidate": deterministic_jsonl(candidate_rows),
        "hold": deterministic_jsonl(hold_rows),
        "summary": json.dumps(summary, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
    }
    if args.write:
        for key in ("audit", "candidate", "hold", "summary"):
            atomic_write(outputs[key], payloads[key])
    if args.validate:
        for key in ("audit", "candidate", "hold", "summary"):
            if outputs[key].is_file() and outputs[key].read_text(encoding="utf-8") != payloads[key]:
                raise ValueError(f"existing {key} output differs from deterministic PC-only evidence")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
