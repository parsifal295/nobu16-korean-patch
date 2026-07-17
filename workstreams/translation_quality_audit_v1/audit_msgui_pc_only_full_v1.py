#!/usr/bin/env python3
"""Audit every PC ``MSG_PK/JP/msgui.bin`` string without Switch Korean.

The sole translation authority is the pristine PC Japanese resource.  The
currently installed PC Korean resource is the target under review; PC EN, SC,
and TC strings are recorded only as context.  Existing entries in the separate
``translation_quality_msgui_realign_v1`` builder are deliberately retained as
an already-pending partition, never duplicated or rewritten here.

The output is private source-paired audit evidence plus a small, deterministic
high-confidence addendum for the msgui realignment builder.  It never writes a
Steam game file, a release asset, or GitHub state.
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
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_ROOT = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
BUILDER = REPO / "workstreams" / "translation_quality_msgui_realign_v1" / "build_msgui_realign_v1.py"
DEFAULT_AUDIT_OUTPUT = AUDIT_ROOT / "semantic" / "msgui_pc_only_full_audit.v1.jsonl"
DEFAULT_CANDIDATE_OUTPUT = AUDIT_ROOT / "semantic" / "msgui_pc_only_quality_addendum.v1.jsonl"
DEFAULT_HOLD_OUTPUT = AUDIT_ROOT / "semantic" / "msgui_pc_only_ambiguous_holds.v1.jsonl"

PATHS = {
    "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgui.bin",
    # The live JP route is the Korean target route in this file-only patch.
    "ko": STEAM / "MSG_PK" / "JP" / "msgui.bin",
    "en": STEAM / "MSG_PK" / "EN" / "msgui.bin",
    "sc": STEAM / "MSG_PK" / "SC" / "msgui.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msgui.bin",
}
EXPECTED_FILE_SHA256 = {
    "jp": "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A",
    "ko": "470FAD81852C6D80D2E1A0390F89A5590529ACE0BE5192DC1C1C58F70178D0DB",
    "en": "B993412D73889B58B68C8998446AF65E1C7CD02066FEAF483E3F44E3EB0602D5",
    "sc": "B21196467A5A2E08A4019D4CEC4A474A64C6F0CD577FA3D068F2130F95CF2C0C",
    "tc": "FA4351F8303DFDAA240441C5BDF8B42DD4F7603E56E6DBAB8CB4DC0594C007D5",
}
ENTRY_COUNT = 5100

# Each replacement is an actual semantic, terminology, or orthographic defect
# demonstrated by the pristine PC Japanese text.  They are intentionally not
# blanket wording rewrites.  ID 4806 additionally has two exact same-source
# Korean anchors in this PC table (2840 and 2846).
CANDIDATES: dict[int, dict[str, str]] = {
    1149: {
        "proposed_ko": "칙명 화의 실행 횟수",
        "issue_type": "conciliation_term_mistranslated_as_strengthening",
        "rationale": "勅命講和 is conciliation/imperial-order peace, not strengthening; msgui:623 already establishes the PC Korean term ‘칙명 화의’ for the exact core term.",
    },
    2856: {
        "proposed_ko": "공주 이름의 독음을 변경할 수 있습니다.",
        "issue_type": "name_pronunciation_label_uses_ungrammatical_reading_noun",
        "rationale": "The UI’s established Korean label for Japanese 読み is ‘독음’; ‘이름의 읽기’ is an unnatural literal noun phrase.",
    },
    2858: {
        "proposed_ko": "독음이 입력되지 않았습니다.",
        "issue_type": "name_pronunciation_label_terminology_consistency",
        "rationale": "PC JP/EN/SC/TC identify an unentered name pronunciation, while the same PC UI consistently labels name readings as ‘독음’.",
    },
    2867: {
        "proposed_ko": "독음에 금지 문자가 포함되어 있습니다.",
        "issue_type": "name_pronunciation_label_terminology_consistency",
        "rationale": "PC JP/EN/SC/TC identify prohibited characters in the name pronunciation; ‘독음’ is the established Korean UI term.",
    },
    3311: {
        "proposed_ko": "설정한 성명의 독음을 정할 수 있습니다.\n※성명은 합계 %s자까지 입력할 수 있습니다.",
        "issue_type": "full_name_pronunciation_label_terminology_consistency",
        "rationale": "The first line is a full-name pronunciation setting. Replacing the literal ‘읽기’ with the established UI term ‘독음’ fixes the Korean noun phrase without changing line structure or the printf token.",
    },
    4075: {
        "proposed_ko": "설정한 휘하 무장 수(%d명)까지만 고정 무장으로 선택할 수 있습니다.",
        "issue_type": "retainer_term_orthography",
        "rationale": "配下武将数 is a retainer count. PC EN/SC/TC and same-table Korean ‘휘하’ anchors support ‘휘하’, not the isolated ‘배하’ rendering.",
    },
    4806: {
        "proposed_ko": "출진 목적지를 선택하십시오",
        "issue_type": "march_destination_term_consistency",
        "rationale": "出陣先 is the marching destination. The exact pristine source is already rendered as ‘출진 목적지’ at PC msgui:2840 and msgui:2846; EN also says marching destination.",
    },
}

# These strings were examined but do not authorize an isolated automatic
# rewrite.  They remain explicit holds instead of being silently counted as
# normal retained translation, so later review can revisit them safely.
HOLD_REASONS: dict[int, str] = {
    597: "Historical-name display label: ‘사료 표기’ is somewhat editorial, but PC-only references do not establish a uniquely safer replacement.",
    1684: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1685: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1686: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1687: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1688: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1689: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1690: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1691: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1692: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1693: "Kana-index bucket is a sort/runtime component; PC localizations use incompatible alphabet/stroke bucket systems.",
    1694: "Kana-index bucket is a sort/runtime component; the Korean last bucket may be an input/search contract rather than ordinary prose.",
    1913: "Private-use-like compact glyph used by a UI component; PC language variants map it to different symbols and do not establish a Korean prose replacement.",
    1921: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    1923: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    1924: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    1927: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    1928: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    1929: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    1930: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    1931: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    1932: "Japanese IME component/status label; PC EN/SC/TC do not establish a Korean runtime-safe replacement.",
    2297: "Compact glyph used by a UI component; PC language variants map it to different symbols and do not establish a Korean prose replacement.",
    2307: "Compact glyph-prefixed command label; PC language variants disagree on the rendered control component.",
    2308: "Compact glyph-prefixed battle label; PC language variants disagree on the rendered control component.",
    2729: "Pristine JP says stamina recovery but PC EN says soldier recovery; current Korean follows EN, so a source-conflict correction is unsafe.",
    2730: "Pristine JP says stamina recovery but PC EN says soldier recovery; current Korean follows EN, so a source-conflict correction is unsafe.",
    3461: "Pristine JP and EN say file while PC SC/TC say folder; current Korean follows the latter, so the runtime object cannot be settled from PC text alone.",
    4920: "Compact glyph-prefixed command label; PC language variants disagree on the rendered control component.",
}

RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")

sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def load_table(path: Path) -> tuple[str, ...]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def format_profile(value: str) -> dict[str, Any]:
    """Match the separate msgui builder's protected format fields exactly."""
    esc_ranges = {index for match in ESC_RE.finditer(value) for index in range(match.start(), match.end())}
    return {
        "runtime": RUNTIME_RE.findall(value),
        "printf": PRINTF_RE.findall(value),
        "escape": ESC_RE.findall(value),
        "linebreaks": re.findall(r"\r\n|\n|\r", value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "private_use": [f"U+{ord(char):04X}" for char in value if 0xE000 <= ord(char) <= 0xF8FF],
        "controls": [
            f"U+{ord(char):04X}"
            for index, char in enumerate(value)
            if unicodedata.category(char) == "Cc" and char not in ("\r", "\n") and index not in esc_ranges
        ],
        "fullwidth_percent_count": value.count("％"),
        "marker_334d_count": value.count("㍍"),
        "box_drawing": [char for char in value if 0x2500 <= ord(char) <= 0x257F],
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


def deterministic_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def active_builder_proposals() -> dict[int, str]:
    """Read the existing msgui builder inputs without building or writing."""
    if not BUILDER.is_file():
        raise ValueError(f"msgui realignment builder is absent: {BUILDER}")
    module_name = "_msgui_pc_only_full_audit_builder"
    module_spec = importlib.util.spec_from_file_location(module_name, BUILDER)
    if module_spec is None or module_spec.loader is None:
        raise ValueError("cannot load msgui realignment builder")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    try:
        rows = module.read_proposals()
    finally:
        sys.modules.pop(module_name, None)
    result: dict[int, str] = {}
    for identifier, (ko, _row, _label) in rows.items():
        if identifier in result:
            raise ValueError(f"duplicate active msgui coordinate: {identifier}")
        result[identifier] = ko
    return result


def build_candidate(
    identifier: int,
    source: str,
    current: str,
    contexts: Mapping[str, str],
    file_hashes: Mapping[str, str],
) -> dict[str, Any]:
    definition = CANDIDATES[identifier]
    proposed = definition["proposed_ko"]
    current_profile = format_profile(current)
    source_profile = format_profile(source)
    proposed_profile = format_profile(proposed)
    if current_profile != proposed_profile or source_profile != proposed_profile:
        raise ValueError(f"msgui:{identifier} changes a protected format field")
    if not HANGUL_RE.search(proposed) or KANA_OR_HAN_RE.search(proposed) or "\0" in proposed or "\ufffd" in proposed:
        raise ValueError(f"msgui:{identifier} proposal is not safe Korean UI text")
    if proposed == current:
        raise ValueError(f"msgui:{identifier} proposal is not an effective correction")
    return {
        "resource": "msgui",
        "id": identifier,
        "ko": current,
        "proposed_ko": proposed,
        "current_hash": text_hash(current),
        "pristine_jp_hash": text_hash(source),
        "source_jp": source,
        "reference_contexts": dict(contexts),
        "source_file_sha256": file_hashes["jp"],
        "current_file_sha256": file_hashes["ko"],
        "reference_file_sha256": {language.upper(): file_hashes[language] for language in ("en", "sc", "tc")},
        "issue_type": definition["issue_type"],
        "rationale": definition["rationale"],
        "format_profile": proposed_profile,
        "format_validation": {
            "current_to_proposed": "all_msgui_builder_protected_fields_match",
            "pristine_jp_to_proposed": "all_msgui_builder_protected_fields_match",
            "all_required_checks_pass": True,
        },
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    file_hashes = {language: file_hash(path) for language, path in PATHS.items()}
    if file_hashes != EXPECTED_FILE_SHA256:
        raise ValueError("PC msgui file baseline changed; rebase the PC-only audit before reuse")
    tables = {language: load_table(path) for language, path in PATHS.items()}
    if any(len(table) != ENTRY_COUNT for table in tables.values()):
        raise ValueError("PC msgui table cardinality differs from 5100")

    active = active_builder_proposals()
    candidates = {
        identifier: build_candidate(
            identifier,
            tables["jp"][identifier],
            tables["ko"][identifier],
            {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")},
            file_hashes,
        )
        for identifier in sorted(CANDIDATES)
    }
    for identifier, row in candidates.items():
        active_value = active.get(identifier)
        if active_value is not None and active_value != row["proposed_ko"]:
            raise ValueError(f"msgui:{identifier} conflicts with an existing realignment proposal")
    if set(CANDIDATES).intersection(HOLD_REASONS):
        raise ValueError("candidate/hold partitions overlap")

    audit_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    for identifier in range(ENTRY_COUNT):
        source = tables["jp"][identifier]
        current = tables["ko"][identifier]
        contexts = {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")}
        if identifier in CANDIDATES:
            disposition = "active_new_candidate" if identifier in active else "candidate_high_confidence"
            detail = CANDIDATES[identifier]["issue_type"]
        elif identifier in active:
            disposition = "active_existing_msgui_realign_candidate"
            detail = "already present in the separate msgui realignment builder; excluded from duplicate proposal"
        elif identifier in HOLD_REASONS:
            disposition = "hold_ambiguous_runtime_or_cross_language_context"
            detail = HOLD_REASONS[identifier]
        else:
            disposition = "retained_after_pc_only_comparison"
            detail = "no high-confidence semantic, grammatical, proper-name, quantity, or UI-effect correction justified by PC-only evidence"
        row = {
            "schema": "nobu16.kr.msgui-pc-only-full-audit.v1",
            "resource": "msgui",
            "id": identifier,
            "disposition": disposition,
            "disposition_detail": detail,
            "source_jp": source,
            "source_jp_utf16le_sha256": text_hash(source),
            "current_ko": current,
            "current_ko_utf16le_sha256": text_hash(current),
            "reference_contexts": contexts,
            "source_file_sha256": file_hashes["jp"],
            "current_file_sha256": file_hashes["ko"],
            "reference_file_sha256": {language.upper(): file_hashes[language] for language in ("en", "sc", "tc")},
            "audit_scope": {
                "pristine_pc_japanese": True,
                "current_pc_korean": True,
                "pc_en_sc_tc_context_only": True,
                "switch_korean_read": False,
                "historic_korean_read": False,
                "steam_game_resource_written": False,
            },
        }
        audit_rows.append(row)
        if disposition == "hold_ambiguous_runtime_or_cross_language_context":
            hold_rows.append(row)

    summary = {
        "schema": "nobu16.kr.msgui-pc-only-full-audit-summary.v1",
        "entry_count": len(audit_rows),
        "active_existing_msgui_realign_candidate_count": len(set(active) - set(CANDIDATES)),
        "new_high_confidence_candidate_count": len(candidates),
        "new_candidate_already_active_count": len(set(active).intersection(CANDIDATES)),
        "ambiguous_hold_count": len(hold_rows),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in audit_rows).items())),
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }
    return audit_rows, [candidates[identifier] for identifier in sorted(candidates)], hold_rows, summary


def validate_rows(
    audit_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    if len(audit_rows) != ENTRY_COUNT or {row["id"] for row in audit_rows} != set(range(ENTRY_COUNT)):
        raise ValueError("full msgui audit does not cover every 0..5099 coordinate exactly once")
    if {row["id"] for row in candidate_rows} != set(CANDIDATES):
        raise ValueError("msgui candidate IDs differ from the reviewed high-confidence set")
    if {row["id"] for row in hold_rows} != set(HOLD_REASONS):
        raise ValueError("msgui hold IDs differ from the reviewed ambiguous set")
    for row in candidate_rows:
        if row["ko"] == row["proposed_ko"] or text_hash(row["ko"]) != row["current_hash"]:
            raise ValueError(f"msgui:{row['id']} current-text hash gate differs")
        if text_hash(row["source_jp"]) != row["pristine_jp_hash"]:
            raise ValueError(f"msgui:{row['id']} pristine-JP hash gate differs")
        if format_profile(row["ko"]) != row["format_profile"] or format_profile(row["source_jp"]) != row["format_profile"]:
            raise ValueError(f"msgui:{row['id']} candidate format profile differs")
        if KANA_OR_HAN_RE.search(row["proposed_ko"]) or not HANGUL_RE.search(row["proposed_ko"]):
            raise ValueError(f"msgui:{row['id']} candidate Korean safety differs")
    for row in audit_rows:
        scope = row["audit_scope"]
        if scope["switch_korean_read"] or scope["historic_korean_read"] or scope["steam_game_resource_written"]:
            raise ValueError("audit scope must remain PC-only and read-only")
    if summary.get("entry_count") != ENTRY_COUNT or summary.get("new_high_confidence_candidate_count") != len(CANDIDATES):
        raise ValueError("msgui audit summary is inconsistent")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE_OUTPUT)
    parser.add_argument("--hold-output", type=Path, default=DEFAULT_HOLD_OUTPUT)
    parser.add_argument("--write", action="store_true", help="write deterministic private PC-only evidence")
    parser.add_argument("--validate", action="store_true", help="validate generated data and existing deterministic outputs")
    args = parser.parse_args()

    outputs = {
        "audit": safe_under(args.audit_output, AUDIT_ROOT),
        "candidate": safe_under(args.candidate_output, AUDIT_ROOT),
        "hold": safe_under(args.hold_output, AUDIT_ROOT),
    }
    audit_rows, candidate_rows, hold_rows, summary = build_rows()
    validate_rows(audit_rows, candidate_rows, hold_rows, summary)
    payloads = {
        "audit": deterministic_jsonl(audit_rows),
        "candidate": deterministic_jsonl(candidate_rows),
        "hold": deterministic_jsonl(hold_rows),
    }
    if args.write:
        for key in ("audit", "candidate", "hold"):
            atomic_write(outputs[key], payloads[key])
    if args.validate:
        for key in ("audit", "candidate", "hold"):
            if outputs[key].exists() and outputs[key].read_text(encoding="utf-8") != payloads[key]:
                raise ValueError(f"existing {key} output differs from deterministic PC-only evidence")
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
