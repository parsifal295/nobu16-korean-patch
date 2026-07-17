#!/usr/bin/env python3
"""Prepare a PC-only ``msgui`` rebase and audit same-source divergences.

``msgui_ko.jsonl`` is retained unchanged as the original private review
input.  This script emits a full replacement input with the same 70 IDs, but
replaces only ID 191 from a generic ``new`` label to the PC-evidenced
``unread/unviewed`` Korean label.  The realign builder must use the rebase
path *instead of*, never alongside, the original input.

It also records every other coordinate from the 36 same-pristine-Japanese
divergence rows and the one non-empty localization-identifier row.  These are
held when PC JP/EN/SC/TC shows a contextual distinction, an existing active
candidate already resolves the drift, or only non-semantic punctuation varies.
No Switch Korean, historic Korean backup, or game-resource write is used.
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
AUDIT = REPO / "tmp" / "translation_quality_audit_v1"
QUEUE = AUDIT / "semantic_inventory_v6" / "private_review_queue.jsonl"
ORIGINAL = AUDIT / "proposals" / "msgui_ko.jsonl"
EXTERNAL_ARTIFACTS = {
    "msgui_findings.v1.jsonl": AUDIT / "semantic" / "msgui_findings.v1.jsonl",
    "msgui_realign_3625_3670.v1.jsonl": AUDIT / "semantic" / "msgui_realign_3625_3670.v1.jsonl",
    "msgui_short_label_addendum.v1.jsonl": AUDIT / "semantic" / "msgui_short_label_addendum.v1.jsonl",
}
DEFAULT_REBASE = AUDIT / "proposals" / "msgui_ko_pc_only_rebase.v1.jsonl"
DEFAULT_HOLDS = AUDIT / "semantic" / "msgui_same_source_divergence_holds.v1.jsonl"

PATHS = {
    "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgui.bin",
    "ko": STEAM / "MSG_PK" / "JP" / "msgui.bin",
    "en": STEAM / "MSG_PK" / "EN" / "msgui.bin",
    "sc": STEAM / "MSG_PK" / "SC" / "msgui.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msgui.bin",
}
EXPECTED_FILES = {
    "jp": "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A",
    "ko": "470FAD81852C6D80D2E1A0390F89A5590529ACE0BE5192DC1C1C58F70178D0DB",
    "en": "B993412D73889B58B68C8998446AF65E1C7CD02066FEAF483E3F44E3EB0602D5",
    "sc": "B21196467A5A2E08A4019D4CEC4A474A64C6F0CD577FA3D068F2130F95CF2C0C",
    "tc": "FA4351F8303DFDAA240441C5BDF8B42DD4F7603E56E6DBAB8CB4DC0594C007D5",
}
EXPECTED_ORIGINAL_SHA256 = "E21CA23A3F83E1AE0303264450AEC5B4A28049BDDB2C984B5A5C283D52A2E75A"
EXPECTED_EXTERNAL_SHA256 = {
    "msgui_findings.v1.jsonl": "9DC3FAC2BDF42306569557AE9A41E148999D4841DFD1D0B952601A86EF535E7B",
    "msgui_realign_3625_3670.v1.jsonl": "4F8586958140611F4229848D191D3465719ED9E88E1DAA6AA625D63E7B926C6A",
    "msgui_short_label_addendum.v1.jsonl": "0EA077FD6DC16295B402CE87BA7429EDE349AECA6FF4E525B96D42521FC7AE12",
}

# The 70 Han-residual candidates have already passed a separate full PC-only
# review.  This rebase retains their exact ID set and changes just 191.
REBASE_IDS = {
    191, 192, 193, 194, 196, 197, 198, 199, 200, 201, 203, 206, 207, 208, 209,
    2665, 2666, 2667, 2668, 2669, 2670, 2671, 2672, 2673, 2674, 2675, 2676,
    2677, 2678, 2679, 2680, 2681, 2683, 2685, 2686,
    2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2757, 2758, 2761, 2764,
    2765, 2767, 2768, 2772, 2773, 2775, 2778, 2779, 2780, 2782, 2784, 2785,
    2786, 2787, 2788, 2789, 2790, 2791, 2792, 2793, 2794, 2796, 2797,
}
REBASE_ID = 191
ANCHOR_ID = 2267
EXPECTED_191_SOURCE_CURRENT = "6D2171BB845CF7C2F595752DE1AC17ABD5FF9915EF08955A2BD3DCC41A42232E"
EXPECTED_191_ORIGINAL_KO_HASH = "402F28C93C4D2E9F3B48481EA46C11F13653938B84688E0CA5A1DA69AED64359"
EXPECTED_191_REBASED_KO = "\ubbf8\uc5f4\ub78c"
EXPECTED_191_REBASED_KO_HASH = "91B0ABC9477ED3C4EB3E6298956831D59C5875030AAD1BB11BD9D30EF99FE1E9"

DIVERGENCE_IDS = {
    10, 27, 548, 937, 1157, 1710, 191, 2267, 2536,
    2662, 2663, 2664, 2666, 2667, 2722, 2723, 2729, 2730,
    2788, 2793, 3514, 3542, 3641, 3651, 3738, 3747, 3748, 3749,
    4054, 4855, 4856, 4875, 4903, 4904, 4913, 4923, 4930,
}
LOCALIZATION_IDENTIFIER_ID = 3738

# Each group covers every non-191 row.  The reason is deliberately derived
# from PC JP/EN/SC/TC and existing active-PC candidate status, never Switch.
HOLD_GROUPS: tuple[tuple[set[int], str, str], ...] = (
    ({10, 27, 548}, "contextual_part_of_speech", "PC EN distinguishes command-like 'Organize' from noun-like 'Organization'; the Korean forms are contextual rather than an unsafe global normalization."),
    ({937, 2536}, "contextual_state_distinction", "PC EN distinguishes OFF from Nullified, so the two Korean state labels must remain contextual."),
    ({ANCHOR_ID}, "same_source_korean_anchor", "This already-correct Korean anchor establishes the PC-only rebase wording at ID 191; no change is needed here."),
    ({1157, 2793}, "already_aligned_with_rebase_candidate", "The existing/rebased Korean value is the same at both PC coordinates; no second candidate is needed."),
    ({1710, 2788}, "already_aligned_with_rebase_candidate", "The existing/rebased Korean value is the same at both PC coordinates; no second candidate is needed."),
    ({2662, 2663, 2664, 2666, 2667}, "already_aligned_with_rebase_candidate", "The existing/rebased Korean value is consistent across the PC group; no second candidate is needed."),
    ({2722, 2723, 2729, 2730}, "pc_language_semantic_branch", "Pristine JP is identical, but PC EN intentionally distinguishes stamina restoration from soldiers restoration. The current Korean mirrors that distinction, so source-text normalization would erase PC-supported meaning."),
    ({3514, 4054}, "punctuation_only", "PC JP/EN/SC/TC semantic content agrees; only Korean terminal punctuation differs, below the high-confidence semantic-correction threshold."),
    ({3542, 4875}, "existing_active_coordinate_realign", "The incorrect coordinate is already corrected by an active PC-only realign candidate, with the other coordinate serving as a same-source anchor."),
    ({3641, 4923}, "existing_active_coordinate_realign", "The incorrect coordinate is already corrected by an active PC-only realign candidate, with the other coordinate serving as a same-source anchor."),
    ({3651, 4913, 4930}, "existing_active_coordinate_realign", "The incorrect coordinate is already corrected by an active PC-only realign candidate, with the other coordinates serving as same-source anchors."),
    ({LOCALIZATION_IDENTIFIER_ID}, "existing_active_localization_identifier_repair", "The non-empty localization identifier is already corrected by an active PC-only candidate; do not add a conflicting duplicate."),
    ({3747, 3748, 3749}, "existing_active_short_label_realign", "Two displaced coordinates are already corrected by active PC-only short-label candidates, and the third is the direct Korean anchor."),
    ({4855, 4856, 4903, 4904}, "punctuation_only", "PC semantic content agrees; the remaining variation is terminal punctuation only, below the high-confidence semantic-correction threshold."),
)

EXTERNAL_EXPECTED = {
    3542: ("msgui_findings.v1.jsonl", "\ud0c0 \uc138\ub825\uc758 \uc131\uc785\ub2c8\ub2e4"),
    3738: ("msgui_findings.v1.jsonl", "\ud56d\ubcf5\ud558\uace0 \uc131\uc8fc \uc774\uc678\ub294 \uc11d\ubc29"),
    3641: ("msgui_realign_3625_3670.v1.jsonl", "\uc131\ud558 \ubc29\uce68\uc744 \uc124\uc815\ud560 \uc131\uc744 \uc120\ud0dd\ud558\uc2ed\uc2dc\uc624."),
    3651: ("msgui_realign_3625_3670.v1.jsonl", "\uc601\uc9c0\ub85c \uc904 \uad70\uc744 \uc120\ud0dd\ud558\uc2ed\uc2dc\uc624."),
    3747: ("msgui_short_label_addendum.v1.jsonl", "\uc608\ube44"),
    3748: ("msgui_short_label_addendum.v1.jsonl", "\uc608\ube44"),
}

sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff"
    r"\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


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


def profile(value: str) -> dict[str, object]:
    return {
        "escape_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf": PRINTF_RE.findall(value),
        "newlines": re.findall(r"\r\n|\n|\r", value),
        "outer_ascii_whitespace": (
            value[: len(value) - len(value.lstrip(" \t"))],
            value[len(value.rstrip(" \t")) :],
        ),
        "private_use": [f"U+{ord(character):04X}" for character in PRIVATE_USE_RE.findall(value)],
        "fullwidth_percent_count": value.count("\uff05"),
        "question_mark_count": value.count("?"),
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


def korean_integrity(value: str) -> dict[str, bool]:
    return {
        "hangul_present": bool(HANGUL_RE.search(value)),
        "no_japanese_or_cjk_residue": not bool(CJK_OR_KANA_RE.search(value)),
        "no_replacement_glyph": "\ufffd" not in value,
        "no_repeated_question_marks": "??" not in value,
    }


def jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"required artifact is absent: {path}")
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"row is not an object: {path}:{line_number}")
        result.append(value)
    return result


def candidate_map(path: Path, rows: list[dict[str, Any]]) -> dict[int, str]:
    result: dict[int, str] = {}
    for line_number, row in enumerate(rows, start=1):
        identifier = row.get("id")
        value = row.get("proposed_ko") if "proposed_ko" in row else row.get("ko")
        if isinstance(identifier, bool) or not isinstance(identifier, int) or not isinstance(value, str) or not value:
            raise ValueError(f"invalid candidate row: {path}:{line_number}")
        if identifier in result:
            raise ValueError(f"duplicate candidate id: {path}:{identifier}")
        result[identifier] = value
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


def encode_rows(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)


def queue_map() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for line_number, row in enumerate(jsonl_rows(QUEUE), start=1):
        if row.get("resource") != "msgui":
            continue
        flags = row.get("flags", [])
        if not (
            "same_pristine_jp_has_multiple_korean_renderings" in flags
            or "target_localization_identifier_for_nonempty_jp" in flags
        ):
            continue
        try:
            identifier = int(row.get("coordinate"))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid queue coordinate: {QUEUE}:{line_number}") from exc
        if identifier in rows:
            raise ValueError(f"duplicate queue coordinate: {identifier}")
        rows[identifier] = row
    if set(rows) != DIVERGENCE_IDS or LOCALIZATION_IDENTIFIER_ID not in rows:
        raise ValueError("same-source/identifier queue differs from reviewed 37-coordinate set")
    return rows


def hold_policy() -> dict[int, tuple[str, str]]:
    policy: dict[int, tuple[str, str]] = {}
    for identifiers, classification, reason in HOLD_GROUPS:
        for identifier in identifiers:
            if identifier in policy:
                raise ValueError(f"duplicate hold policy id: {identifier}")
            policy[identifier] = (classification, reason)
    expected = DIVERGENCE_IDS - {REBASE_ID}
    if set(policy) != expected:
        raise ValueError("hold policy does not cover every non-rebased divergence row")
    return policy


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    hashes = {language: file_hash(path) for language, path in PATHS.items()}
    if hashes != EXPECTED_FILES:
        raise ValueError("PC msgui baseline hash differs; rebase review before reuse")
    tables = {language: load_table(path) for language, path in PATHS.items()}
    if any(len(table) != len(tables["jp"]) for table in tables.values()):
        raise ValueError("PC msgui table cardinalities differ")

    if file_hash(ORIGINAL) != EXPECTED_ORIGINAL_SHA256:
        raise ValueError("original msgui_ko artifact changed; re-review before rebase")
    original = candidate_map(ORIGINAL, jsonl_rows(ORIGINAL))
    if set(original) != REBASE_IDS:
        raise ValueError("original msgui_ko ID set differs from reviewed 70-coordinate set")
    if text_hash(original[REBASE_ID]) != EXPECTED_191_ORIGINAL_KO_HASH:
        raise ValueError("original msgui_ko ID 191 differs from reviewed candidate")

    external_maps: dict[str, dict[int, str]] = {}
    for name, path in EXTERNAL_ARTIFACTS.items():
        if file_hash(path) != EXPECTED_EXTERNAL_SHA256[name]:
            raise ValueError(f"external candidate changed; re-review before reuse: {name}")
        external_maps[name] = candidate_map(path, jsonl_rows(path))
    for identifier, (name, expected) in EXTERNAL_EXPECTED.items():
        if external_maps[name].get(identifier) != expected:
            raise ValueError(f"external active candidate differs at msgui:{identifier}")

    queue = queue_map()
    source = tables["jp"][REBASE_ID]
    current = tables["ko"][REBASE_ID]
    anchor_source = tables["jp"][ANCHOR_ID]
    anchor_current = tables["ko"][ANCHOR_ID]
    if (
        source != current
        or source != anchor_source
        or text_hash(source) != EXPECTED_191_SOURCE_CURRENT
        or text_hash(current) != EXPECTED_191_SOURCE_CURRENT
        or anchor_current != EXPECTED_191_REBASED_KO
        or text_hash(anchor_current) != EXPECTED_191_REBASED_KO_HASH
    ):
        raise ValueError("ID 191 PC source/current or same-source Korean anchor differs")

    rebase_rows: list[dict[str, Any]] = []
    for identifier in sorted(REBASE_IDS):
        pristine = tables["jp"][identifier]
        live = tables["ko"][identifier]
        replacement = EXPECTED_191_REBASED_KO if identifier == REBASE_ID else original[identifier]
        source_profile = profile(pristine)
        current_profile = profile(live)
        replacement_profile = profile(replacement)
        source_format = profile_match(source_profile, replacement_profile)
        current_format = profile_match(current_profile, replacement_profile)
        integrity = korean_integrity(replacement)
        if not all(source_format.values()) or not all(current_format.values()) or not all(integrity.values()):
            raise ValueError(f"rebase format or Korean-integrity validation failed at msgui:{identifier}")
        evidence: dict[str, Any] = {
            "resource": "msgui",
            "id": identifier,
            "ko": replacement,
            "current_ko": live,
            "current_hash": text_hash(live),
            "source_current_hash": text_hash(live),
            "source_text": pristine,
            "source_text_hash": text_hash(pristine),
            "pristine_jp_hash": text_hash(pristine),
            "source_file_sha256": hashes["ko"],
            "pristine_jp_file_sha256": hashes["jp"],
            "reference_file_sha256": {language: hashes[language] for language in ("en", "sc", "tc")},
            "pc_target_contexts": {language: tables[language][identifier] for language in ("en", "sc", "tc")},
            "original_private_artifact": ORIGINAL.name,
            "original_candidate_ko": original[identifier],
            "original_candidate_hash": text_hash(original[identifier]),
            "rebase_action": "replace_existing_candidate" if identifier == REBASE_ID else "retain_existing_candidate",
            "source_gate_validation": "exact_utf16le_hash_match",
            "current_ko_gate_validation": "exact_utf16le_hash_match",
            "format_profile": {
                "pristine_jp": source_profile,
                "current_ko": current_profile,
                "replacement_ko": replacement_profile,
            },
            "format_validation": {
                "replacement_to_pristine_jp": source_format,
                "replacement_to_current": current_format,
                "replacement_integrity": integrity,
                "all_required_checks_pass": True,
            },
            "switch_korean_translation_used": False,
            "historic_korean_backup_used": False,
            "game_files_written": False,
        }
        if identifier == REBASE_ID:
            evidence["issue_type"] = "pc_only_same_source_semantic_precision_rebase"
            evidence["rationale"] = "Pristine PC JP is unread/unviewed; PC EN uses the NEW UI shorthand, PC SC/TC retain unread/unviewed wording, and same-source PC msgui ID 2267 already renders the label as Korean unread/unviewed."
            evidence["same_source_msgui_anchor"] = {
                "id": ANCHOR_ID,
                "source_text_hash": text_hash(anchor_source),
                "current_ko": anchor_current,
                "current_hash": text_hash(anchor_current),
            }
            evidence["builder_reordering_policy"] = {
                "replace_input_path": "tmp/translation_quality_audit_v1/proposals/msgui_ko.jsonl",
                "with_rebase_path": "tmp/translation_quality_audit_v1/proposals/msgui_ko_pc_only_rebase.v1.jsonl",
                "include_both": False,
                "reason": "Both contain the same 70 coordinates, but ID 191 differs by the PC-only precision correction.",
            }
        rebase_rows.append(evidence)

    policies = hold_policy()
    holds: list[dict[str, Any]] = []
    for identifier in sorted(DIVERGENCE_IDS - {REBASE_ID}):
        row = queue[identifier]
        pristine = tables["jp"][identifier]
        live = tables["ko"][identifier]
        queue_contexts = {"EN": tables["en"][identifier], "SC": tables["sc"][identifier], "TC": tables["tc"][identifier]}
        if row.get("jp") != pristine or row.get("ko") != live or row.get("contexts") != queue_contexts:
            raise ValueError(f"review queue differs from PC tables at msgui:{identifier}")
        if row.get("jp_utf16le_sha256") != text_hash(pristine) or row.get("ko_utf16le_sha256") != text_hash(live):
            raise ValueError(f"review queue hash differs from PC tables at msgui:{identifier}")
        classification, reason = policies[identifier]
        active: dict[str, Any] | None = None
        if identifier in original:
            active = {"artifact": DEFAULT_REBASE.name, "value": EXPECTED_191_REBASED_KO if identifier == REBASE_ID else original[identifier], "rebase_path_replaces_original": True}
        elif identifier in EXTERNAL_EXPECTED:
            name, value = EXTERNAL_EXPECTED[identifier]
            active = {"artifact": name, "value": value, "rebase_path_replaces_original": False}
        holds.append(
            {
                "resource": "msgui",
                "coordinate": str(identifier),
                "id": identifier,
                "current_ko": live,
                "current_hash": text_hash(live),
                "source_text": pristine,
                "source_text_hash": text_hash(pristine),
                "source_file_sha256": hashes["ko"],
                "pristine_jp_file_sha256": hashes["jp"],
                "reference_file_sha256": {language: hashes[language] for language in ("en", "sc", "tc")},
                "pc_target_contexts": {language: tables[language][identifier] for language in ("en", "sc", "tc")},
                "review_status": "hold_no_new_addendum_candidate",
                "classification": classification,
                "reason": reason,
                "existing_active_candidate": active,
                "source_gate_validation": "exact_utf16le_hash_match",
                "current_ko_gate_validation": "exact_utf16le_hash_match",
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
                "game_files_written": False,
            }
        )
    if len(rebase_rows) != 70 or {row["id"] for row in rebase_rows} != REBASE_IDS:
        raise ValueError("rebase row set differs")
    if len(holds) != 36 or {row["id"] for row in holds}.union({REBASE_ID}) != DIVERGENCE_IDS:
        raise ValueError("hold row set differs")
    summary = {
        "rebase_candidate_count": len(rebase_rows),
        "changed_coordinate_count": 1,
        "changed_coordinate": REBASE_ID,
        "replaced_original_value_hash": EXPECTED_191_ORIGINAL_KO_HASH,
        "rebased_value_hash": EXPECTED_191_REBASED_KO_HASH,
        "same_source_divergence_hold_count": len(holds),
        "identifier_hold_count": 1,
        "source_current_hash_gates": "all_exact_utf16le_hash_match",
        "format_validation": "all_rebase_rows_match_pristine_current_runtime_printf_escape_newline_whitespace_profiles",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    return rebase_rows, holds, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebase-output", type=Path, default=DEFAULT_REBASE)
    parser.add_argument("--hold-output", type=Path, default=DEFAULT_HOLDS)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.validate and not args.write:
        parser.error("choose --validate and/or --write")
    try:
        rebase_output = safe_under(args.rebase_output, AUDIT)
        hold_output = safe_under(args.hold_output, AUDIT)
        rebase_rows, holds, summary = build_rows()
        if args.write:
            atomic_write(rebase_output, encode_rows(rebase_rows))
            atomic_write(hold_output, encode_rows(holds))
            summary = {
                **summary,
                "rebase_output": str(rebase_output),
                "rebase_output_bytes": rebase_output.stat().st_size,
                "hold_output": str(hold_output),
                "hold_output_bytes": hold_output.stat().st_size,
                "json_encoding": "ensure_ascii_true_utf8",
            }
    except (OSError, ValueError, IndexError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
