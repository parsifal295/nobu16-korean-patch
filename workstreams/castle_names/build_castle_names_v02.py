#!/usr/bin/env python3
"""Build the source-free, human-reviewed castle-name overlay v0.2.

The builder applies four SHA-pinned review proposal files to the immutable
v0.1 draft.  It does not read any installed game resource or commercial
source string.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import unicodedata
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
FIRST_ID = 9151
LAST_ID = 9542
ENTRY_COUNT = LAST_ID - FIRST_ID + 1
STATUS = "reviewed"
EXPECTED_CHANGE_COUNT = 53
BASE_SHA256 = "465F0CA873E310C20FAF9DF7D247B4A5025991774E1C4F8F320BC4125A93AE13"
PROPOSALS = (
    (
        "castle_names_ko_9151_9249.review-proposal.v0.2.json",
        9151,
        9249,
        "B06F39128C5283951F9A6A9E8DC7FB2CCDAE4CE762967939A6508701EF739A28",
    ),
    (
        "castle_names_ko_9250_9348.review-proposal.v0.2.json",
        9250,
        9348,
        "4A4815356B33612E0F51D9E873AA4D27A9350D681C90AE4CE0C4BD353478750F",
    ),
    (
        "castle_names_ko_9349_9446.review-proposal.v0.2.json",
        9349,
        9446,
        "7335DE8E2386F182492E6079362653C1717F3FA12995663A6010B6A32B5EFB24",
    ),
    (
        "castle_names_ko_9447_9542.review-proposal.v0.2.json",
        9447,
        9542,
        "5F1538D2FFEA914A7287CE3AFC4703CD3891EAD182C89A08DD07ED2EAF634FB0",
    ),
)
SPECIAL_DECISIONS = {
    9256: "시즈",
    9361: "빗추 마쓰야마",
    9447: "니타카야마",
}


class CastleReviewError(ValueError):
    """Raised when a pinned review input or output contract is invalid."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise CastleReviewError(f"cannot read {path}: {exc}") from exc


def read_json_bytes(path: Path) -> tuple[dict[str, Any], bytes]:
    data = read_bytes(path)
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CastleReviewError(f"invalid UTF-8 JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CastleReviewError(f"expected a JSON object: {path}")
    return value, data


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def valid_korean_name(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == unicodedata.normalize("NFC", value)
        and not value.startswith(" ")
        and not value.endswith(" ")
        and "  " not in value
        and all(character == " " or 0xAC00 <= ord(character) <= 0xD7A3 for character in value)
    )


def load_base(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    value, data = read_json_bytes(path)
    if sha256_bytes(data) != BASE_SHA256:
        raise CastleReviewError("v0.1 base overlay SHA-256 does not match the pinned draft")
    if value.get("schema") != "nobu16.kr.castle-name-overlay.v0.1":
        raise CastleReviewError("unexpected v0.1 base schema")
    if value.get("source_text_free") is not True:
        raise CastleReviewError("v0.1 base must be source-text-free")
    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) != ENTRY_COUNT:
        raise CastleReviewError("v0.1 base entry count changed")
    for offset, row in enumerate(entries):
        entry_id = FIRST_ID + offset
        if (
            not isinstance(row, dict)
            or set(row) != {"id", "ko", "method", "status"}
            or row.get("id") != entry_id
            or row.get("status") != "automatic_draft_review_needed"
            or not valid_korean_name(row.get("ko"))
        ):
            raise CastleReviewError(f"invalid v0.1 base row at id {entry_id}")
    return value, entries


def load_review_changes(
    reviews_dir: Path,
    base_entries: list[dict[str, Any]],
) -> tuple[dict[int, str], list[dict[str, Any]]]:
    by_id = {int(row["id"]): row for row in base_entries}
    all_reviewed_ids: set[int] = set()
    changes: dict[int, str] = {}
    proposal_metadata: list[dict[str, Any]] = []

    for filename, first_id, last_id, expected_sha256 in PROPOSALS:
        path = reviews_dir / filename
        proposal, data = read_json_bytes(path)
        actual_sha256 = sha256_bytes(data)
        if actual_sha256 != expected_sha256:
            raise CastleReviewError(f"review proposal SHA-256 changed: {filename}")
        if proposal.get("schema") != "nobu16.kr.castle-name-human-review-proposal.v0.2":
            raise CastleReviewError(f"unexpected review schema: {filename}")
        base_reference = proposal.get("base_overlay")
        if not isinstance(base_reference, dict) or base_reference.get("sha256") != BASE_SHA256:
            raise CastleReviewError(f"review proposal has a different base: {filename}")
        scope = proposal.get("scope")
        scope_ids = set(range(first_id, last_id + 1))
        if (
            not isinstance(scope, dict)
            or scope.get("first_id") != first_id
            or scope.get("last_id") != last_id
            or scope.get("reviewed_count") != len(scope_ids)
            or scope.get("contiguous") is not True
        ):
            raise CastleReviewError(f"review scope changed: {filename}")
        accepted = proposal.get("accepted_as_is_ids")
        proposed_changes = proposal.get("changes")
        if not isinstance(accepted, list) or not isinstance(proposed_changes, list):
            raise CastleReviewError(f"review decision lists missing: {filename}")

        accepted_ids = {int(entry_id) for entry_id in accepted}
        changed_ids: set[int] = set()
        for change in proposed_changes:
            if not isinstance(change, dict):
                raise CastleReviewError(f"invalid change row: {filename}")
            entry_id = change.get("id")
            draft = change.get("draft_ko")
            proposed = change.get("proposed_ko")
            if not isinstance(entry_id, int) or entry_id not in scope_ids or entry_id in changed_ids:
                raise CastleReviewError(f"invalid or duplicate changed id in {filename}: {entry_id}")
            if by_id[entry_id]["ko"] != draft:
                raise CastleReviewError(f"draft value no longer matches v0.1 at id {entry_id}")
            if not valid_korean_name(proposed):
                raise CastleReviewError(f"invalid proposed Korean name at id {entry_id}")
            changed_ids.add(entry_id)
            changes[entry_id] = proposed

        if accepted_ids & changed_ids or accepted_ids | changed_ids != scope_ids:
            raise CastleReviewError(f"review coverage is incomplete or overlapping: {filename}")
        summary = proposal.get("summary")
        if (
            not isinstance(summary, dict)
            or summary.get("accepted_as_is_count") != len(accepted_ids)
            or summary.get("change_proposed_count") != len(changed_ids)
        ):
            raise CastleReviewError(f"review summary count changed: {filename}")
        if all_reviewed_ids & scope_ids:
            raise CastleReviewError(f"review scopes overlap: {filename}")
        all_reviewed_ids.update(scope_ids)
        proposal_metadata.append(
            {
                "change_count": len(changed_ids),
                "first_id": first_id,
                "last_id": last_id,
                "path": f"reviews/{filename}",
                "reviewed_count": len(scope_ids),
                "sha256": actual_sha256,
            }
        )

    if all_reviewed_ids != set(range(FIRST_ID, LAST_ID + 1)):
        raise CastleReviewError("four review proposals do not cover all 392 ids")
    if len(changes) != EXPECTED_CHANGE_COUNT:
        raise CastleReviewError(f"expected 53 approved changes, found {len(changes)}")
    for entry_id, expected_name in SPECIAL_DECISIONS.items():
        if changes.get(entry_id) != expected_name:
            raise CastleReviewError(f"required review decision changed at id {entry_id}")
    return changes, proposal_metadata


def build_release(base_path: Path, reviews_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    base, base_entries = load_base(base_path)
    changes, proposal_metadata = load_review_changes(reviews_dir, base_entries)

    entries = []
    for row in base_entries:
        entry_id = int(row["id"])
        entries.append(
            {
                "id": entry_id,
                "ko": changes.get(entry_id, row["ko"]),
                "method": row["method"],
                "status": STATUS,
            }
        )

    overlay = {
        "entries": entries,
        "review": {
            "approved_change_count": len(changes),
            "base_overlay_path": "public/castle_names_ko_9151_9542.v0.1.json",
            "base_overlay_sha256": BASE_SHA256,
            "proposal_count": len(proposal_metadata),
            "proposals": proposal_metadata,
            "reviewed_count": len(entries),
            "status_meaning": "reviewed means human review complete",
        },
        "schema": "nobu16.kr.castle-name-overlay.v0.2",
        "source_text_free": True,
        "target": base["target"],
        "translation_policy": {
            "castle_type_suffix_included": False,
            "compound_spacing": "human_reviewed_place_name_usage",
            "geographic_tsu": "standard_korean_쓰",
            "long_vowels": "do_not_duplicate_japanese_long_vowels_in_korean",
            "personal_name_style": "out_of_scope",
            "review_required": False,
        },
    }
    overlay_data = json_bytes(overlay)
    changed_by_diff = sum(
        current["ko"] != previous["ko"] for current, previous in zip(entries, base_entries, strict=True)
    )
    remaining_geographic_츠_count = sum(row["ko"].count("츠") for row in entries)
    if changed_by_diff != EXPECTED_CHANGE_COUNT:
        raise CastleReviewError("built v0.2 differs from v0.1 by an unexpected count")
    if any(row["status"] != STATUS for row in entries):
        raise CastleReviewError("not every v0.2 entry has reviewed status")
    if remaining_geographic_츠_count:
        raise CastleReviewError("a geographic 츠 spelling remains after the approved review")

    by_id = {row["id"]: row["ko"] for row in entries}
    validation = {
        "approved_change_count": changed_by_diff,
        "base_overlay_sha256": BASE_SHA256,
        "entry_count": len(entries),
        "geographic_tsu_uses_쓰": remaining_geographic_츠_count == 0,
        "geographic_츠_remaining_count": remaining_geographic_츠_count,
        "id_9361_space_preserved": by_id[9361] == "빗추 마쓰야마",
        "id_range_contiguous": [row["id"] for row in entries] == list(range(FIRST_ID, LAST_ID + 1)),
        "installed_game_files_modified": False,
        "medium_confidence_long_vowel_decisions_applied": (
            by_id[9256] == "시즈" and by_id[9447] == "니타카야마"
        ),
        "passed": True,
        "process_memory_access": False,
        "proposal_count": len(proposal_metadata),
        "public_ko_only_precomposed_hangul_and_ascii_space": all(
            valid_korean_name(row["ko"]) for row in entries
        ),
        "registry_access": False,
        "reviewed_count": sum(row["status"] == STATUS for row in entries),
        "schema": "nobu16.kr.castle-name-review-validation.v0.2",
        "source_text_fields_in_public_overlay": 0,
        "source_text_free": True,
        "status": STATUS,
        "v0_2_overlay_sha256": sha256_bytes(overlay_data),
    }
    return overlay, validation


def check_or_write(path: Path, expected: bytes, check: bool) -> None:
    if check:
        actual = read_bytes(path)
        if actual != expected:
            raise CastleReviewError(f"generated file is stale: {path}")
    else:
        atomic_write(path, expected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        type=Path,
        default=SCRIPT_DIR / "public" / "castle_names_ko_9151_9542.v0.1.json",
    )
    parser.add_argument("--reviews-dir", type=Path, default=SCRIPT_DIR / "reviews")
    parser.add_argument(
        "--output",
        type=Path,
        default=SCRIPT_DIR / "public" / "castle_names_ko_9151_9542.v0.2.json",
    )
    parser.add_argument(
        "--validation-output",
        type=Path,
        default=SCRIPT_DIR / "validation.v0.2.json",
    )
    parser.add_argument("--check", action="store_true", help="verify released files without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    overlay, validation = build_release(args.base, args.reviews_dir)
    overlay_data = json_bytes(overlay)
    validation_data = json_bytes(validation)
    check_or_write(args.output, overlay_data, args.check)
    check_or_write(args.validation_output, validation_data, args.check)
    print(
        json.dumps(
            {
                "approved_change_count": EXPECTED_CHANGE_COUNT,
                "entry_count": ENTRY_COUNT,
                "mode": "check" if args.check else "write",
                "overlay_sha256": sha256_bytes(overlay_data),
                "reviewed_count": ENTRY_COUNT,
                "validation_sha256": sha256_bytes(validation_data),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CastleReviewError as exc:
        print(f"castle-name v0.2 build failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
