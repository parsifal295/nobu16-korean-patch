#!/usr/bin/env python3
"""Generate pinned, source-free glyph demand from public Korean overlays.

This tool intentionally accepts only the two tracked overlay revisions named in
``SPECS``.  Updating either public overlay requires an explicit review and pin
update here before its font corpus can change.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_ROOT = SCRIPT_DIR.parent
GAME_ROOT = PATCH_ROOT.parent

DEMAND_SCHEMA = "nobu16.kr.glyph-demand.v1"
COMMON_OVERLAY_SCHEMA = "nobu16.kr.common-message-overlay.v1"
CASTLE_OVERLAY_SCHEMA = "nobu16.kr.castle-name-overlay.v0.1"
HASH_RE = re.compile(r"[0-9A-F]{64}\Z")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
CASTLE_NAME_RE = re.compile(r"[\uac00-\ud7a3]+(?: [\uac00-\ud7a3]+)*\Z")

DIALOGUE_ROOT_KEYS = frozenset(
    {
        "base_language",
        "defaults",
        "distribution_policy",
        "entries",
        "entry_count",
        "overlay_id",
        "resource",
        "schema",
        "stock_sc",
    }
)
DIALOGUE_ENTRY_KEYS = frozenset({"id", "ko", "source_sc_utf16le_sha256"})
CASTLE_ROOT_KEYS = frozenset(
    {"entries", "schema", "source_text_free", "target", "translation_policy"}
)
CASTLE_ENTRY_KEYS = frozenset({"id", "ko", "method", "status"})


class DemandError(ValueError):
    """Raised when a public overlay or demand artifact is not canonical."""


@dataclass(frozen=True)
class OverlaySpec:
    kind: str
    overlay_path: Path
    output_path: Path
    overlay_sha256: str
    schema: str
    resource: str
    first_id: int
    last_id: int
    source_description: str

    @property
    def ids(self) -> tuple[int, ...]:
        return tuple(range(self.first_id, self.last_id + 1))


SPECS: Mapping[str, OverlaySpec] = {
    "dialogue": OverlaySpec(
        kind="dialogue",
        overlay_path=(
            PATCH_ROOT
            / "workstreams"
            / "dialogue"
            / "public"
            / "msgev_ko_event_opening_3202_3229.v0.1.json"
        ),
        output_path=(
            PATCH_ROOT
            / "workstreams"
            / "font_v6"
            / "corpus"
            / "msgev_dialogue_3202_3229"
            / "glyph_demand.json"
        ),
        overlay_sha256="98C77E79256EE7B5A5CAAFAF95FDC1467F20A90F8E508E3EE975629B4EFD1C7F",
        schema=COMMON_OVERLAY_SCHEMA,
        resource="MSG_PK/SC/msgev.bin",
        first_id=3202,
        last_id=3229,
        source_description="Korean text in the source-free public msgev dialogue overlay",
    ),
    "castle": OverlaySpec(
        kind="castle",
        overlay_path=(
            PATCH_ROOT
            / "workstreams"
            / "castle_names"
            / "public"
            / "castle_names_ko_9151_9542.v0.1.json"
        ),
        output_path=(
            PATCH_ROOT
            / "workstreams"
            / "font_v6"
            / "corpus"
            / "msgdata_castle_names_9151_9542"
            / "glyph_demand.json"
        ),
        overlay_sha256="465F0CA873E310C20FAF9DF7D247B4A5025991774E1C4F8F320BC4125A93AE13",
        schema=CASTLE_OVERLAY_SCHEMA,
        resource="MSG_PK/SC/msgdata.bin",
        first_id=9151,
        last_id=9542,
        source_description="Korean names in the source-free public msgdata castle-name overlay",
    ),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def reject_duplicate_or_case_colliding_keys(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    spellings: dict[str, str] = {}
    for key, value in pairs:
        folded = key.casefold()
        if key in result:
            raise DemandError(f"duplicate JSON key: {key!r}")
        if folded in spellings:
            raise DemandError(
                "case-colliding JSON keys: "
                f"{spellings[folded]!r} and {key!r}"
            )
        result[key] = value
        spellings[folded] = key
    return result


def loads_json_strict(raw: bytes, label: str = "JSON") -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicate_or_case_colliding_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DemandError(f"invalid UTF-8 JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise DemandError(f"{label}: top-level JSON value must be an object")
    return value


def require_exact_keys(
    value: object, expected: frozenset[str], label: str
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DemandError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise DemandError(
            f"{label} keys are not exact; missing={missing!r}, "
            f"unexpected={unexpected!r}"
        )
    return value


def require_bool(value: object, expected: bool, label: str) -> None:
    if type(value) is not bool or value is not expected:
        raise DemandError(f"{label} must be {expected!r}")


def require_int(value: object, expected: int, label: str) -> None:
    if type(value) is not int or value != expected:
        raise DemandError(f"{label} must be integer {expected}")


def require_string(value: object, expected: str, label: str) -> None:
    if not isinstance(value, str) or value != expected:
        raise DemandError(f"{label} must be {expected!r}")


def require_canonical_hash(value: object, label: str) -> str:
    if not isinstance(value, str) or HASH_RE.fullmatch(value) is None:
        raise DemandError(f"{label} must be an uppercase SHA-256 digest")
    return value


def validate_ko_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise DemandError(f"{label} must be non-empty text without NUL")
    if not unicodedata.is_normalized("NFC", value):
        raise DemandError(f"{label} must be NFC-normalized")
    return value


def contains_commercial_script(text: str) -> bool:
    """Return true for CJK ideographs or kana, which are not Korean output."""

    return any(
        0x3040 <= ord(char) <= 0x30FF
        or 0x31F0 <= ord(char) <= 0x31FF
        or 0x3400 <= ord(char) <= 0x4DBF
        or 0x4E00 <= ord(char) <= 0x9FFF
        or 0xF900 <= ord(char) <= 0xFAFF
        or 0xFF66 <= ord(char) <= 0xFF9F
        or 0x20000 <= ord(char) <= 0x323AF
        or 0x2F800 <= ord(char) <= 0x2FA1F
        for char in text
    )


def validate_dialogue_overlay(
    overlay: dict[str, Any], spec: OverlaySpec
) -> tuple[list[int], list[str]]:
    require_exact_keys(overlay, DIALOGUE_ROOT_KEYS, "dialogue root")
    require_string(overlay["schema"], spec.schema, "dialogue schema")
    require_string(overlay["resource"], spec.resource, "dialogue resource")
    require_string(overlay["base_language"], "SC", "dialogue base_language")
    require_string(
        overlay["overlay_id"],
        "msgev_event_opening_3202_3229.v0.1",
        "dialogue overlay_id",
    )

    defaults = require_exact_keys(
        overlay["defaults"], frozenset({"status"}), "dialogue defaults"
    )
    require_string(defaults["status"], "translated", "dialogue defaults.status")
    policy = require_exact_keys(
        overlay["distribution_policy"],
        frozenset(
            {"contains_commercial_source_text", "contains_complete_game_resource"}
        ),
        "dialogue distribution_policy",
    )
    require_bool(
        policy["contains_commercial_source_text"],
        False,
        "dialogue contains_commercial_source_text",
    )
    require_bool(
        policy["contains_complete_game_resource"],
        False,
        "dialogue contains_complete_game_resource",
    )
    stock = require_exact_keys(
        overlay["stock_sc"],
        frozenset(
            {"packed_sha256", "raw_sha256", "raw_size", "size", "string_count"}
        ),
        "dialogue stock_sc",
    )
    require_canonical_hash(stock["packed_sha256"], "dialogue stock packed hash")
    require_canonical_hash(stock["raw_sha256"], "dialogue stock raw hash")
    for field in ("raw_size", "size", "string_count"):
        if type(stock[field]) is not int or stock[field] <= 0:
            raise DemandError(f"dialogue stock_sc.{field} must be a positive integer")

    entries = overlay["entries"]
    if not isinstance(entries, list):
        raise DemandError("dialogue entries must be an array")
    require_int(overlay["entry_count"], len(spec.ids), "dialogue entry_count")
    if len(entries) != len(spec.ids):
        raise DemandError(
            f"dialogue entries must contain exactly {len(spec.ids)} items"
        )

    ids: list[int] = []
    texts: list[str] = []
    for index, raw_entry in enumerate(entries):
        entry = require_exact_keys(
            raw_entry, DIALOGUE_ENTRY_KEYS, f"dialogue entries[{index}]"
        )
        entry_id = entry["id"]
        if type(entry_id) is not int:
            raise DemandError(f"dialogue entries[{index}].id must be an integer")
        text = validate_ko_text(entry["ko"], f"dialogue entries[{index}].ko")
        require_canonical_hash(
            entry["source_sc_utf16le_sha256"],
            f"dialogue entries[{index}].source_sc_utf16le_sha256",
        )
        if contains_commercial_script(text):
            raise DemandError(
                f"dialogue entries[{index}].ko contains CJK source script or kana"
            )
        consumed = {
            position
            for match in ESC_RE.finditer(text)
            for position in range(match.start(), match.end())
        }
        malformed_esc = [
            position
            for position, character in enumerate(text)
            if character == "\x1b" and position not in consumed
        ]
        if malformed_esc:
            raise DemandError(
                f"dialogue entries[{index}].ko has malformed ESC command(s)"
            )
        ids.append(entry_id)
        texts.append(text)

    if tuple(ids) != spec.ids:
        raise DemandError(
            f"dialogue ids must be the exact ordered range "
            f"{spec.first_id}..{spec.last_id}"
        )
    return ids, texts


def validate_castle_overlay(
    overlay: dict[str, Any], spec: OverlaySpec
) -> tuple[list[int], list[str]]:
    require_exact_keys(overlay, CASTLE_ROOT_KEYS, "castle root")
    require_string(overlay["schema"], spec.schema, "castle schema")
    require_bool(overlay["source_text_free"], True, "castle source_text_free")

    target = require_exact_keys(
        overlay["target"],
        frozenset(
            {
                "entry_count",
                "first_id",
                "last_id",
                "resource",
                "shared_suffix_id_range_not_modified",
            }
        ),
        "castle target",
    )
    require_int(target["entry_count"], len(spec.ids), "castle target.entry_count")
    require_int(target["first_id"], spec.first_id, "castle target.first_id")
    require_int(target["last_id"], spec.last_id, "castle target.last_id")
    require_string(target["resource"], spec.resource, "castle target.resource")
    suffix = require_exact_keys(
        target["shared_suffix_id_range_not_modified"],
        frozenset({"count", "first_id", "last_id"}),
        "castle target.shared_suffix_id_range_not_modified",
    )
    require_int(suffix["count"], 5, "castle shared suffix count")
    require_int(suffix["first_id"], 9936, "castle shared suffix first_id")
    require_int(suffix["last_id"], 9940, "castle shared suffix last_id")

    policy = require_exact_keys(
        overlay["translation_policy"],
        frozenset(
            {
                "base",
                "castle_type_suffix_included",
                "jp_reading_use",
                "reason",
                "review_required",
            }
        ),
        "castle translation_policy",
    )
    require_bool(
        policy["castle_type_suffix_included"],
        False,
        "castle castle_type_suffix_included",
    )
    require_bool(policy["review_required"], True, "castle review_required")
    for field in ("base", "jp_reading_use", "reason"):
        if not isinstance(policy[field], str) or not policy[field]:
            raise DemandError(f"castle translation_policy.{field} must be text")

    entries = overlay["entries"]
    if not isinstance(entries, list) or len(entries) != len(spec.ids):
        raise DemandError(
            f"castle entries must contain exactly {len(spec.ids)} items"
        )
    ids: list[int] = []
    texts: list[str] = []
    allowed_methods = {
        "en_romaji",
        "en_romaji_words",
        "en_romaji_jp_n_y_boundary",
    }
    for index, raw_entry in enumerate(entries):
        entry = require_exact_keys(
            raw_entry, CASTLE_ENTRY_KEYS, f"castle entries[{index}]"
        )
        entry_id = entry["id"]
        if type(entry_id) is not int:
            raise DemandError(f"castle entries[{index}].id must be an integer")
        text = validate_ko_text(entry["ko"], f"castle entries[{index}].ko")
        if CASTLE_NAME_RE.fullmatch(text) is None:
            raise DemandError(
                f"castle entries[{index}].ko must contain only precomposed "
                "Hangul syllables separated by single ASCII spaces"
            )
        if entry["method"] not in allowed_methods:
            raise DemandError(f"castle entries[{index}].method is unsupported")
        require_string(
            entry["status"],
            "automatic_draft_review_needed",
            f"castle entries[{index}].status",
        )
        ids.append(entry_id)
        texts.append(text)

    if tuple(ids) != spec.ids:
        raise DemandError(
            f"castle ids must be the exact ordered range "
            f"{spec.first_id}..{spec.last_id}"
        )
    return ids, texts


def validate_overlay_bytes(
    raw: bytes, spec: OverlaySpec, label: str
) -> tuple[dict[str, Any], list[int], list[str]]:
    overlay = loads_json_strict(raw, label)
    if spec.kind == "dialogue":
        ids, texts = validate_dialogue_overlay(overlay, spec)
    elif spec.kind == "castle":
        ids, texts = validate_castle_overlay(overlay, spec)
    else:  # pragma: no cover - SPECS is fixed, but fail closed if extended badly.
        raise DemandError(f"unsupported overlay kind: {spec.kind!r}")
    actual_hash = sha256_bytes(raw)
    if actual_hash != spec.overlay_sha256:
        raise DemandError(
            f"{label}: overlay SHA-256 {actual_hash} does not match pinned "
            f"{spec.overlay_sha256}"
        )
    return overlay, ids, texts


def renderable_characters(text: str) -> list[str]:
    """Match msgui_catalog_v2 font filtering exactly."""

    consumed_esc = {
        index
        for match in ESC_RE.finditer(text)
        for index in range(match.start(), match.end())
    }
    return [
        char
        for index, char in enumerate(text)
        if index not in consumed_esc
        and not char.isspace()
        and not (ord(char) < 0x20 or 0x7F <= ord(char) <= 0x9F)
        and not (0xE000 <= ord(char) <= 0xF8FF)
    ]


def font_exclusion_reason(char: str) -> str:
    codepoint = ord(char)
    if 0xE000 <= codepoint <= 0xF8FF:
        return "game_private_icon"
    if codepoint < 0x20 or 0x7F <= codepoint <= 0x9F:
        return "ui_control"
    return "ui_escape_sequence_component"


def font_exclusion_inventory(
    raw_characters: set[str], font_characters: set[str]
) -> list[dict[str, str]]:
    return [
        {
            "codepoint": f"U+{ord(char):04X}",
            "reason": font_exclusion_reason(char),
        }
        for char in sorted(raw_characters - font_characters, key=ord)
    ]


def project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(GAME_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise DemandError(f"overlay must stay inside the game workspace: {path}") from exc


def id_inventory_hash(ids: Sequence[int]) -> str:
    data = json.dumps(list(ids), separators=(",", ":")).encode("utf-8")
    return sha256_bytes(data)


def build_demand(
    overlay_path: Path, spec: OverlaySpec
) -> dict[str, Any]:
    try:
        raw = overlay_path.read_bytes()
    except OSError as exc:
        raise DemandError(f"cannot read {overlay_path}: {exc}") from exc
    overlay, ids, texts = validate_overlay_bytes(raw, spec, str(overlay_path))

    raw_chars = {
        character
        for text in texts
        for character in text
        if not character.isspace()
    }
    font_chars = {
        character for text in texts for character in renderable_characters(text)
    }
    characters = sorted(font_chars, key=ord)
    exclusions = font_exclusion_inventory(raw_chars, font_chars)
    exclusion_blob = json.dumps(
        exclusions, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    source_codepoint_lines = "".join(
        f"U+{ord(character):04X}\n"
        for character in sorted(raw_chars, key=ord)
    ).encode("ascii")
    hangul_syllables = [
        character for character in characters if 0xAC00 <= ord(character) <= 0xD7A3
    ]
    hangul_jamo = [
        character
        for character in characters
        if 0x1100 <= ord(character) <= 0x11FF
        or 0x3130 <= ord(character) <= 0x318F
        or 0xA960 <= ord(character) <= 0xA97F
        or 0xD7B0 <= ord(character) <= 0xD7FF
    ]
    codepoints = [f"U+{ord(character):04X}" for character in characters]
    return {
        "schema": DEMAND_SCHEMA,
        "source": spec.source_description,
        "source_overlay": {
            "kind": spec.kind,
            "path": project_relative(overlay_path),
            "sha256": sha256_bytes(raw),
            "schema": overlay["schema"],
            "resource": spec.resource,
            "entry_count": len(ids),
            "first_id": ids[0],
            "last_id": ids[-1],
            "ordered_ids_sha256": id_inventory_hash(ids),
        },
        "source_non_whitespace_character_count": len(raw_chars),
        "source_non_whitespace_codepoints_sha256": sha256_bytes(
            source_codepoint_lines
        ),
        "font_exclusion_policy": (
            "exclude ESC command components, C0/C1 controls, and game PUA "
            "icons from G1N raster demand"
        ),
        "excluded_font_token_count": len(exclusions),
        "excluded_font_tokens": exclusions,
        "excluded_font_tokens_sha256": sha256_bytes(exclusion_blob),
        "character_count": len(characters),
        "characters": characters,
        "codepoints": codepoints,
        "hangul_syllable_count": len(hangul_syllables),
        "hangul_syllables": hangul_syllables,
        "hangul_syllable_codepoints": [
            f"U+{ord(character):04X}" for character in hangul_syllables
        ],
        "hangul_jamo_count": len(hangul_jamo),
        "hangul_jamo": hangul_jamo,
        "hangul_jamo_codepoints": [
            f"U+{ord(character):04X}" for character in hangul_jamo
        ],
    }


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


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


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=sorted(SPECS))
    parser.add_argument("--overlay", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify byte-identical output without writing it.",
    )
    args = parser.parse_args(argv)
    spec = SPECS[args.kind]
    overlay_path = (args.overlay or spec.overlay_path).resolve()
    output_path = (args.output or spec.output_path).resolve()
    try:
        expected = encode_json(build_demand(overlay_path, spec))
        if args.check:
            try:
                actual = output_path.read_bytes()
            except OSError as exc:
                raise DemandError(f"cannot read {output_path}: {exc}") from exc
            if actual != expected:
                raise DemandError(f"stale glyph demand: {output_path}")
        else:
            atomic_write(output_path, expected)
    except DemandError as exc:
        parser.exit(2, f"error: {exc}\n")

    value = loads_json_strict(expected, "generated demand")
    print(f"kind={spec.kind}")
    print(f"output={output_path}")
    print(f"overlay_sha256={value['source_overlay']['sha256']}")
    print(f"entries={value['source_overlay']['entry_count']}")
    print(f"characters={value['character_count']}")
    print(f"hangul_syllables={value['hangul_syllable_count']}")
    print(f"excluded_tokens={value['excluded_font_token_count']}")
    print(f"sha256={sha256_bytes(expected)}")
    print(f"check_only={args.check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
