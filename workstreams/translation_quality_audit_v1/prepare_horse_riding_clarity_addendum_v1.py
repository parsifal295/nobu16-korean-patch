#!/usr/bin/env python3
"""Build PC-only source-gated clarity repairs for the Japanese term ``馬術``.

The live Korean phonetic rendering ``마술`` is a valid Hanja reading but is
visually indistinguishable from magic.  Every included PC source/reference
context means horsemanship/equestrian skill, so the review-only proposal uses
the unambiguous Korean UI term ``승마`` while preserving every other character.
No Switch Korean or historic Korean backup is read, and no game file is
written.
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
DEFAULT_OUTPUT = AUDIT_ROOT / "semantic" / "horse_riding_clarity_addendum.v1.jsonl"

RESOURCE_PATHS: dict[str, dict[str, Path]] = {
    "strdata": {
        "jp": PRISTINE_ROOT / "MSG" / "JP" / "strdata.bin",
        "ko": STEAM / "MSG" / "JP" / "strdata.bin",
        "sc": STEAM / "MSG" / "SC" / "strdata.bin",
        "tc": STEAM / "MSG" / "TC" / "strdata.bin",
    },
    "msgbre": {
        "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgbre.bin",
        "ko": STEAM / "MSG_PK" / "JP" / "msgbre.bin",
        "en": STEAM / "MSG_PK" / "EN" / "msgbre.bin",
        "sc": STEAM / "MSG_PK" / "SC" / "msgbre.bin",
        "tc": STEAM / "MSG_PK" / "TC" / "msgbre.bin",
    },
    "msgdata": {
        "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
        "ko": STEAM / "MSG_PK" / "JP" / "msgdata.bin",
        "en": STEAM / "MSG_PK" / "EN" / "msgdata.bin",
        "sc": STEAM / "MSG_PK" / "SC" / "msgdata.bin",
        "tc": STEAM / "MSG_PK" / "TC" / "msgdata.bin",
    },
    "pk_msggame": {
        "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        "ko": STEAM / "MSG_PK" / "JP" / "msggame.bin",
        "en": STEAM / "MSG_PK" / "EN" / "msggame.bin",
        "sc": STEAM / "MSG_PK" / "SC" / "msggame.bin",
        "tc": STEAM / "MSG_PK" / "TC" / "msggame.bin",
    },
}

REFERENCE_LANGUAGES = {
    "strdata": ("sc", "tc"),
    "msgbre": ("en", "sc", "tc"),
    "msgdata": ("en", "sc", "tc"),
    "pk_msggame": ("en", "sc", "tc"),
}

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))
sys.path.insert(0, str(REPO / "workstreams" / "msggame"))

from msggame_format import iter_literals, parse_packed_msggame  # noqa: E402
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
SOURCE_MARKER = "\u99ac\u8853"
CURRENT_MARKER = "\ub9c8\uc220"
PROPOSED_MARKER = "\uc2b9\ub9c8"


@dataclass(frozen=True)
class Target:
    resource: str
    coordinate: str
    source_hash: str
    current_hash: str
    slot_kind: str
    rationale: str


# Hashes freeze the complete source/current strings, not merely the term.
# This permits the two biography copies and the newline-bearing msggame
# literals to remain exact source-gated candidates.
TARGETS = (
    Target(
        "strdata",
        "0:21113",
        "94D516D67F4DD4278BF84B63D8D7DDFEBA264058598F30469D10AB2D90463815",
        "0B33686BB9E4D6166A5586584315233873722CA73C4E58FE4AA53C69DD8202C5",
        "visible_skill_instruction_label",
        "PC EN identifies this as Equestrian Instruction; the bare Korean reading is visually ambiguous with magic.",
    ),
    Target(
        "strdata",
        "0:23648",
        "863C93645EE41844AFAA5699A953A581E01B8494F1F08DF9B0F52E9CDA39427E",
        "872555F4E8F96D6E177644E5A0CCD177FF5658761B53D243882E57EBAFB1BE69",
        "visible_equestrian_skill_label",
        "The matching PC EN label is Equestrian, not magic; use the Korean riding term for a readable UI label.",
    ),
    Target(
        "strdata",
        "2:618",
        "D4117347BFBBE93971A9F8B7178DE66581993E5AFF1FF24F590A52CE6429B4F0",
        "976F5E2A0D2C4CB4190B92B1E7B0D2A5045B833A25B6687C063FBB27F250D1B5",
        "biography_horsemanship_sentence",
        "The biography calls the character a master of horsemanship; PC EN says skilled horseman.",
    ),
    Target(
        "strdata",
        "2:1490",
        "AD8DB409A8ABEBEB655B7BBD2027EF42F2094C17BB83214C76A9BA7D0A95C9F7",
        "BD36DD3E5F09DB4EE046665FEDDF7E643C08CE242B03C6DAA710D13CA8584D95",
        "biography_horsemanship_sentence",
        "The biography calls the character an expert in horsemanship; PC EN says skilled rider.",
    ),
    Target(
        "msgbre",
        "618",
        "D4117347BFBBE93971A9F8B7178DE66581993E5AFF1FF24F590A52CE6429B4F0",
        "90DFE48692272E281662925234281BE32C046499D4C7D13D5C1AB059F9FF37B1",
        "biography_horsemanship_sentence",
        "This is the direct PC biography counterpart of strdata 2:618 and must retain the same clarified term.",
    ),
    Target(
        "msgbre",
        "1490",
        "AD8DB409A8ABEBEB655B7BBD2027EF42F2094C17BB83214C76A9BA7D0A95C9F7",
        "BD36DD3E5F09DB4EE046665FEDDF7E643C08CE242B03C6DAA710D13CA8584D95",
        "biography_horsemanship_sentence",
        "This is the direct PC biography counterpart of strdata 2:1490 and must retain the same clarified term.",
    ),
    Target(
        "msgdata",
        "21215",
        "94D516D67F4DD4278BF84B63D8D7DDFEBA264058598F30469D10AB2D90463815",
        "0B33686BB9E4D6166A5586584315233873722CA73C4E58FE4AA53C69DD8202C5",
        "visible_skill_instruction_label",
        "PC EN says Equestrian Instruction and PC SC/TC retain the horsemanship term.",
    ),
    Target(
        "msgdata",
        "24450",
        "863C93645EE41844AFAA5699A953A581E01B8494F1F08DF9B0F52E9CDA39427E",
        "872555F4E8F96D6E177644E5A0CCD177FF5658761B53D243882E57EBAFB1BE69",
        "visible_equestrian_skill_label",
        "PC EN says Equestrian, so the plain Korean label must not read as magic.",
    ),
    Target(
        "msgdata",
        "26550",
        "A9A2F01C1A2D0F72DB5AB2E030B3967FAE9FAF801B45063049E67080A1F39D87",
        "6A1E7927E5D9B82726D342BE84294F0D79BA57A2C1E07A4E99F16A79E8322BD5",
        "visible_equestrian_official_title",
        "PC EN calls this Equestrian Overseer; clarify the title's field as horse riding.",
    ),
    Target(
        "msgdata",
        "27889",
        "B858F54248E8F18D54A9EB23ADD05368CDFF0EE7AE9EDCCFC18AD3BE035D08E7",
        "89EC04EC9B0A67D723AD06457B67ECF03F743D511744A92399970C9EB23F7405",
        "visible_equestrian_effect_description",
        "PC EN selects skilled riders to form cavalry units; this is explicitly a riding skill, not magic.",
    ),
    Target(
        "pk_msggame",
        "6:4795:0",
        "77F37E5125EBDE5C202F34252E008E9988BE7CC02FBF8D9E104A64C34BA9F4A8",
        "0BCC6EF88BD7D3759C876EAE7266450310AE157E8BDFA2EA975114D506A8072A",
        "event_dialogue_fragment",
        "PC EN refers to the speaker's equestrian skills and a fine horse; retain the literal's line layout exactly.",
    ),
    Target(
        "pk_msggame",
        "15:1905:1",
        "8FC907129C0DCE36E86A01B1BF5FBFB9F4E4BB06B6CDE7EBE7CF296C63BF5807",
        "C873B612317188F07678645F740EDDCF0290845F32FF2CD01EDF3BA717B685FE",
        "event_instruction_fragment",
        "PC EN explicitly calls this equestrian training; retain the literal's manual line breaks exactly.",
    ),
    Target(
        "pk_msggame",
        "15:1920:1",
        "8FC907129C0DCE36E86A01B1BF5FBFB9F4E4BB06B6CDE7EBE7CF296C63BF5807",
        "C873B612317188F07678645F740EDDCF0290845F32FF2CD01EDF3BA717B685FE",
        "event_instruction_fragment",
        "PC EN explicitly calls this equestrian training; retain the literal's manual line breaks exactly.",
    ),
)

# Exact duplicate source text can have resource-specific live Korean framing.
# The links are evidence-only and never cause a cross-resource overwrite.
PEERS = {
    ("strdata", "0:21113"): ("msgdata", "21215"),
    ("strdata", "0:23648"): ("msgdata", "24450"),
    ("strdata", "2:618"): ("msgbre", "618"),
    ("strdata", "2:1490"): ("msgbre", "1490"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load_common(path: Path) -> dict[str, str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return {str(index): text for index, text in enumerate(parse_message_table(raw).texts)}


def load_strdata(path: Path) -> dict[str, str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return {
        f"{block}:{identifier}": text
        for (block, identifier), text in coordinate_texts(parse_raw_strdata(raw)).items()
    }


def load_msggame(path: Path) -> dict[str, str]:
    parsed = parse_packed_msggame(path.read_bytes())
    return {
        f"{literal.block_id}:{literal.record_id}:{literal.literal_id}": literal.text
        for literal in iter_literals(parsed.archive)
    }


def load_resource(resource: str, path: Path) -> dict[str, str]:
    if resource == "strdata":
        return load_strdata(path)
    if resource in {"msgbre", "msgdata"}:
        return load_common(path)
    if resource == "pk_msggame":
        return load_msggame(path)
    raise ValueError(f"unknown resource: {resource}")


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


def line_character_counts(text: str) -> list[int]:
    return [len(line) for line in re.split(r"\r\n|\n|\r", text)]


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


def normalized_row_key(resource: str, row: dict[str, Any], path: Path) -> tuple[str, str] | None:
    row_resource = row.get("resource")
    if not isinstance(row_resource, str):
        for candidate in ("strdata", "msgbre", "msgdata", "pk_msggame"):
            if path.name.startswith(candidate):
                row_resource = candidate
                break
    if row_resource != resource:
        return None
    coordinate = row.get("coordinate")
    if not isinstance(coordinate, str):
        if resource == "strdata" and isinstance(row.get("block"), int) and isinstance(row.get("id"), int):
            coordinate = f"{row['block']}:{row['id']}"
        elif resource in {"msgbre", "msgdata"} and isinstance(row.get("id"), int):
            coordinate = str(row["id"])
    if not isinstance(coordinate, str):
        return None
    return row_resource, coordinate


def candidate_overlaps() -> dict[str, list[str]]:
    targets = {(target.resource, target.coordinate) for target in TARGETS}
    found: dict[str, list[str]] = {resource: [] for resource, _coordinate in targets}
    for directory in (AUDIT_ROOT / "semantic", AUDIT_ROOT / "proposals"):
        for path in sorted(directory.glob("*.jsonl")):
            if path.resolve() == DEFAULT_OUTPUT.resolve():
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                for resource, coordinate in targets:
                    key = normalized_row_key(resource, row, path)
                    if key == (resource, coordinate):
                        found[resource].append(f"{path.name}:{line_number}")
    return found


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    overlaps = candidate_overlaps()
    if any(overlaps.values()):
        raise ValueError(f"horse-riding candidates overlap existing candidate rows: {overlaps}")

    tables = {
        resource: {language: load_resource(resource, path) for language, path in paths.items()}
        for resource, paths in RESOURCE_PATHS.items()
    }
    for resource, language_tables in tables.items():
        if set(language_tables["jp"]) != set(language_tables["ko"]):
            raise ValueError(f"pristine JP/current KO coordinate set differs for {resource}")
    file_hashes = {
        resource: {language: sha256_file(path) for language, path in paths.items()}
        for resource, paths in RESOURCE_PATHS.items()
    }

    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        table = tables[target.resource]
        source = table["jp"].get(target.coordinate)
        current = table["ko"].get(target.coordinate)
        if source is None or current is None:
            raise ValueError(f"missing target {target.resource}:{target.coordinate}")
        if text_hash(source) != target.source_hash or SOURCE_MARKER not in source or source.count(SOURCE_MARKER) != 1:
            raise ValueError(f"pristine JP source gate failed for {target.resource}:{target.coordinate}")
        if text_hash(current) != target.current_hash or CURRENT_MARKER not in current or current.count(CURRENT_MARKER) != 1:
            raise ValueError(f"current KO gate failed for {target.resource}:{target.coordinate}")
        proposed = current.replace(CURRENT_MARKER, PROPOSED_MARKER)
        if proposed.count(PROPOSED_MARKER) != 1 or CURRENT_MARKER in proposed:
            raise ValueError(f"term replacement did not remain local for {target.resource}:{target.coordinate}")
        current_profile = profile(current)
        source_profile = profile(source)
        proposed_profile = profile(proposed)
        current_to_proposed = profile_match(current_profile, proposed_profile)
        source_to_proposed = profile_match(source_profile, proposed_profile)
        current_line_counts = line_character_counts(current)
        proposed_line_counts = line_character_counts(proposed)
        integrity = {
            "hangul_present": bool(HANGUL_RE.search(proposed)),
            "no_japanese_or_cjk_residue": not bool(CJK_OR_KANA_RE.search(proposed)),
            "no_replacement_glyph": "\ufffd" not in proposed,
            "no_repeated_question_marks": "??" not in proposed,
            "line_character_counts_unchanged": current_line_counts == proposed_line_counts,
        }
        if not all(current_to_proposed.values()) or not all(source_to_proposed.values()) or not all(integrity.values()):
            raise ValueError(f"format, line-layout, or integrity check failed for {target.resource}:{target.coordinate}")
        peer_context: dict[str, Any] | None = None
        peer = PEERS.get((target.resource, target.coordinate))
        if peer is not None:
            peer_resource, peer_coordinate = peer
            peer_source = tables[peer_resource]["jp"].get(peer_coordinate)
            peer_current = tables[peer_resource]["ko"].get(peer_coordinate)
            if peer_source != source or peer_current is None or CURRENT_MARKER not in peer_current:
                raise ValueError(f"cross-resource peer drifted for {target.resource}:{target.coordinate}")
            peer_context = {
                "resource": peer_resource,
                "coordinate": peer_coordinate,
                "source_text": peer_source,
                "ko": peer_current,
                "proposed_ko": peer_current.replace(CURRENT_MARKER, PROPOSED_MARKER),
            }
        identity: dict[str, Any]
        if target.resource == "strdata":
            block, identifier = (int(part) for part in target.coordinate.split(":"))
            identity = {"block": block, "id": identifier}
        elif target.resource in {"msgbre", "msgdata"}:
            identity = {"id": int(target.coordinate)}
        else:
            identity = {}
        rows.append(
            {
                "resource": target.resource,
                "coordinate": target.coordinate,
                **identity,
                "ko": current,
                "proposed_ko": proposed,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "source_file_sha256": file_hashes[target.resource]["ko"],
                "pristine_jp_file_sha256": file_hashes[target.resource]["jp"],
                "reference_file_sha256": {
                    language: file_hashes[target.resource][language]
                    for language in REFERENCE_LANGUAGES[target.resource]
                },
                "issue_type": "ambiguous_hanja_reading_clarity",
                "slot_kind": target.slot_kind,
                "rationale": target.rationale,
                "term_mapping": {
                    "pristine_jp": SOURCE_MARKER,
                    "current_ko": CURRENT_MARKER,
                    "proposed_ko": PROPOSED_MARKER,
                },
                "source_gate_validation": "exact_utf16le_hash_and_single_marker_match",
                "current_ko_gate_validation": "exact_utf16le_hash_and_single_marker_match",
                "pc_target_contexts": {
                    language: table[language].get(target.coordinate)
                    for language in REFERENCE_LANGUAGES[target.resource]
                },
                "cross_resource_peer": peer_context,
                "format_profile": {
                    "current_ko": current_profile,
                    "proposed_ko": proposed_profile,
                    "pristine_jp": source_profile,
                },
                "line_character_counts": {
                    "current_ko": current_line_counts,
                    "proposed_ko": proposed_line_counts,
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
        raise ValueError("candidate cardinality or coordinate uniqueness check failed")
    payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
    if any(byte > 0x7F for byte in payload.encode("utf-8")):
        raise ValueError("candidate JSONL must be ASCII-only")
    summary = {
        "row_count": len(rows),
        "resource_counts": {
            resource: sum(row["resource"] == resource for row in rows)
            for resource in ("strdata", "msgbre", "msgdata", "pk_msggame")
        },
        "target_coordinates": [f"{row['resource']}:{row['coordinate']}" for row in rows],
        "existing_candidate_overlap": overlaps,
        "source_gates": "all_exact_utf16le_hash_and_marker_match",
        "current_ko_gates": "all_exact_utf16le_hash_and_marker_match",
        "format_validation": "all_runtime_printf_esc_newline_whitespace_profiles_and_line_counts_match",
        "cross_resource_peer_count": sum(row["cross_resource_peer"] is not None for row in rows),
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
