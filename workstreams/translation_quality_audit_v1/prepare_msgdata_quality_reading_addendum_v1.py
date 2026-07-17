#!/usr/bin/env python3
"""Build a second, source-gated msgdata quality addendum for visible readings.

The first addendum is intentionally limited to the battle-terrain cluster.
This companion artifact covers only independently cross-checked, visible UI
labels and traits where a Japanese reading was left in the Korean text.  It
does not write a game resource and it uses no Switch or historic Korean data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prepare_msgdata_quality_semantic_findings_v1 import (
    Candidate,
    DIRECT_EXISTING,
    HANGUL_RE,
    JAPANESE_OR_CJK_RE,
    LIVE_KO,
    PRISTINE_JP,
    REFERENCE_FILES,
    SEMANTIC_EXISTING,
    TMP_ROOT,
    atomic_write,
    critical_profile_match,
    load_texts,
    profile,
    read_existing_ids,
    safe_under,
    sha256_file,
    text_hash,
)


CORE_EXISTING = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_semantic_addendum.v1.jsonl"
)
DEFAULT_OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_reading_addendum.v1.jsonl"
)


# All twelve entries are visible label/trait fields, not ruby-reading fields.
# The PC EN/SC/TC resources are evidence only; pristine PC Japanese and current
# Steam Korean are the two source gates.  Ambiguous historical proper nouns and
# facility terms are intentionally left out.
CANDIDATES: dict[int, Candidate] = {
    24078: Candidate(
        "\u66ff\u92ad\u5c4b",
        "\uac00\uc5d0\uc81c\ub2c8\uc57c",
        "\ud658\uc804\uc0c1",
        "visible_japanese_reading",
        "\uc131\ud558 \ub9c8\uc744 \uc2dc\uc124\uba85 \u66ff\u92ad\u5c4b\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Exchange\uc640 \ud658\uc804 \uc5c5\uc790\ub97c \ub73b\ud558\ub294 \ud55c\uad6d\uc5b4 \uc6a9\uc5b4\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24097: Candidate(
        "\u5927\u793e",
        "\ub2e4\uc774\uc0e4",
        "\ub300\uc0ac",
        "visible_japanese_reading",
        "\uc2e0\uc0ac \uc2dc\uc124\uba85 \u5927\u793e\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744, \uae30\uc874 \uc9c0\uba85\uc758 \uc774\uc988\ubaa8 \ub300\uc0ac\u00b7\uc2a4\uc640 \ub300\uc0ac\uc640 \uc77c\uce58\ud558\ub294 \ud55c\uad6d\uc5b4 \uc6a9\uc5b4\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (26365, 26370),
    ),
    24101: Candidate(
        "\u672c\u5c71",
        "\ubaa8\ud1a0\uc57c\ub9c8",
        "\ubcf8\uc0b0",
        "visible_japanese_reading",
        "\uc0ac\ucc30 \uc2dc\uc124\uba85 \u672c\u5c71\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Head Temple\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4 \uc6a9\uc5b4 \ubcf8\uc0b0\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24106: Candidate(
        "\u80fd\u697d\u5802",
        "\ub178\uac00\ucfe0\ub3c4",
        "\ub178\uac00\ucfe0\ub2f9",
        "visible_japanese_reading",
        "\uacf5\uc5f0 \uc2dc\uc124\uba85 \u80fd\u697d\u5802\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Noh Theater\uc640 \ud55c\uad6d\uc5b4 \ud45c\uae30\uc5d0 \ub9de\ucd98 \ub178\uac00\ucfe0\ub2f9\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24417: Candidate(
        "\u4e00\u6240\u61f8\u547d",
        "\uc787\uc1fc\ucf04\uba54\uc774",
        "\uc804\uc2ec\uc804\ub825",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u4e00\u6240\u61f8\u547d\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Utmost Devotion\uacfc SC\u00b7TC\uc758 \u76e1\u5fc3\u76e1\u529b \uc758\ubbf8\uc5d0 \ub9de\ucd98 \uc804\uc2ec\uc804\ub825\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24419: Candidate(
        "\u76db\u540d",
        "\ubaa8\ub9ac\ub098",
        "\uba85\uc131",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u76db\u540d\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Reputation\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4 \uc6a9\uc5b4 \uba85\uc131\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24425: Candidate(
        "\u57ce\u4e57",
        "\uc870\ub178\ub9ac",
        "\uacf5\uc131",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u57ce\u4e57\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Castle Raid\uc640 SC\u00b7TC\uc758 \u653b\u57ce \uc758\ubbf8\uc5d0 \ub9de\ucd98 \uacf5\uc131\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24440: Candidate(
        "\u6d77\u795e",
        "\uac00\uc774\uc9c4",
        "\ud574\uc2e0",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u6d77\u795e\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Sea God\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4 \uc6a9\uc5b4 \ud574\uc2e0\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24446: Candidate(
        "\u6570\u5bc4",
        "\uc2a4\ud0a4",
        "\ud48d\ub958",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u6570\u5bc4\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Refined Taste\uc640 SC\u00b7TC\uc758 \u98a8\u96c5 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \ud48d\ub958\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24484: Candidate(
        "\u7a32\u5149",
        "\uc774\ub098\ubbf8\uc4f0",
        "\ubc88\uac1c",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u7a32\u5149\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Lightning Flash\uacfc SC\u00b7TC\uc758 \u95ea\u96fb \uc758\ubbf8\uc5d0 \ub9de\ucd98 \ubc88\uac1c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24486: Candidate(
        "\u9b3c\u7f8e\u6fc3",
        "\uc624\ub2c8\ubbf8\ub178",
        "\ubbf8\ub178\uc758 \uadc0\uc2e0",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u9b3c\u7f8e\u6fc3\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Mino Ogre\uc5d0 \ub9de\ucd98 \ubbf8\ub178\uc758 \uadc0\uc2e0\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4. \uae30\uc874 \uac00\uc774\uc758 \ud638\ub791\uc774\u00b7\uc5d0\uce58\uace0\uc758 \uc6a9\uacfc \uac19\uc740 \ubcc4\uce6d \ud45c\uae30 \ubc29\uc2dd\uc744 \ub530\ub978\ub2e4.",
        (24456, 24458),
    ),
    24487: Candidate(
        "\u59eb\u6b66\u8005",
        "\ud788\uba54\ubb34\uc0e4",
        "\uc5ec\uc804\uc0ac",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u59eb\u6b66\u8005\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Female Warriors\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4 \uc5ec\uc804\uc0ac\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
}


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    jp = load_texts(PRISTINE_JP)
    ko = load_texts(LIVE_KO)
    references = {language: load_texts(path) for language, path in REFERENCE_FILES.items()}
    if len(jp) != len(ko) or any(len(table) != len(jp) for table in references.values()):
        raise ValueError("PC msgdata table cardinalities differ")

    existing_sources = (DIRECT_EXISTING, SEMANTIC_EXISTING, CORE_EXISTING)
    existing_by_file = {path.name: read_existing_ids(path) for path in existing_sources}
    existing = set().union(*existing_by_file.values())
    overlap = sorted(existing.intersection(CANDIDATES))
    if overlap:
        raise ValueError(f"reading addendum overlaps existing msgdata candidates: {overlap}")

    file_hashes = {
        "live_steam_ko": sha256_file(LIVE_KO),
        "pristine_pc_jp": sha256_file(PRISTINE_JP),
        **{language.lower(): sha256_file(path) for language, path in REFERENCE_FILES.items()},
    }
    rows: list[dict[str, object]] = []
    for identifier, candidate in sorted(CANDIDATES.items()):
        if not 0 <= identifier < len(jp):
            raise ValueError(f"coordinate outside msgdata table: {identifier}")
        source = jp[identifier]
        current = ko[identifier]
        if source != candidate.source_text:
            raise ValueError(f"{identifier}: pristine JP source gate failed")
        if current != candidate.expected_ko:
            raise ValueError(f"{identifier}: current Steam Korean gate failed")
        if current == candidate.proposed_ko:
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
        "existing_direct_candidate_id_count": len(existing_by_file[DIRECT_EXISTING.name]),
        "existing_semantic_candidate_id_count": len(existing_by_file[SEMANTIC_EXISTING.name]),
        "existing_core_addendum_id_count": len(existing_by_file[CORE_EXISTING.name]),
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
