#!/usr/bin/env python3
"""Freeze and build the first verified fixes from the PC text-quality audit.

The input is the *current Steam PC JP route*.  Candidate wording is supplied
through private review JSONL files; the published overlay keeps
only Korean replacements and source hashes.  In particular, this builder does
not read a Switch Korean resource or use one as a translation authority.

``freeze`` produces a source-free public overlay plus its validation record.
``build`` recreates private candidates from that frozen overlay without
writing to the Steam installation.
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
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))
sys.path.insert(0, str(REPO / "workstreams" / "msggame"))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
from msggame_format import iter_literals, parse_packed_msggame, rebuild_packed_with_literals  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "translation_quality_corrections_v1" / "candidate"
PRIVATE_PROPOSALS = REPO / "tmp" / "translation_quality_audit_v1" / "proposals"
PRIVATE_SEMANTIC = REPO / "tmp" / "translation_quality_audit_v1" / "semantic"
MSGDATA_TSU_OUTER_WHITESPACE = (
    REPO
    / "tmp"
    / "translation_quality_msgdata_tsu_outer_whitespace_v1"
    / "msgdata_tsu_outer_whitespace_candidates.v1.jsonl"
)
RESIDUAL_THREE_PC_ONLY = (
    REPO
    / "tmp"
    / "translation_quality_residual_three_pc_only_v1"
    / "private_candidates.v1.jsonl"
)
MSGBRE_RESTORED_FACTS = (
    REPO
    / "tmp"
    / "translation_quality_msgbre_restored_facts_v1"
    / "msgbre_restored_facts_candidates.v1.jsonl"
)
PC_ANCHOR_REAUDIT = (
    REPO
    / "tmp"
    / "translation_quality_strdata_msgdata_pc_anchor_reaudit_v1"
    / "private_candidates.v1.jsonl"
)
EV_STRDATA_PC_REAUDIT = (
    REPO
    / "tmp"
    / "translation_quality_ev_strdata_pc_reaudit_v1"
    / "ev_strdata_pc_reaudit_candidates.v1.jsonl"
)
PK_MSGGAME_PC_REAUDIT = (
    REPO
    / "tmp"
    / "translation_quality_msggame_pc_reaudit_v1"
    / "pk_msggame_pc_reaudit_candidates.v1.jsonl"
)
BASE_MSGGAME_PC_REAUDIT = (
    REPO
    / "tmp"
    / "translation_quality_base_msggame_pc_reaudit_v1"
    / "base_msggame_pc_reaudit_candidates.v1.jsonl"
)
MSGEV_PC_CANONICAL_TITLE_REPAIR = (
    REPO
    / "workstreams"
    / "translation_quality_msgev_pc_canonical_title_repair_v1"
    / "private_candidates.v1.jsonl"
)
EVENT_SEMANTIC_RESIDUALS_PC_ONLY = (
    REPO
    / "tmp"
    / "translation_quality_event_semantic_residuals_pc_only_v1"
    / "private_candidates.v1.jsonl"
)
PC_TRANSLATION_RESIDUALS_ANCHORS = (
    REPO
    / "tmp"
    / "pc_translation_residuals_pc_only_v1"
    / "pc_exact_anchor_candidates.v1.jsonl"
)
PC_MSGGAME_RESIDUALS = (
    REPO
    / "tmp"
    / "translation_quality_pc_msggame_residuals_v1"
    / "pk_msggame_candidates.v1.jsonl"
)
# These two batches were re-reviewed directly against the pristine PC Japanese
# resource and the PC EN/SC/TC variants.  They deliberately supersede an
# earlier generic correction at the same coordinate when the two Korean
# renderings disagree.  Pinning the private batch bytes prevents an unrelated
# edit under ``tmp`` from silently gaining that precedence.
PC_ONLY_OVERRIDE_INPUT_SHA256 = {
    EVENT_SEMANTIC_RESIDUALS_PC_ONLY: "C0DF8E6DE69DF7DEDD07D27FA84E1F6337E5296C631CDBB99F5F7411EAC81CFC",
    PC_TRANSLATION_RESIDUALS_ANCHORS: "218BE3E2534798C9EB0EDD33A08A481E4670FE017B9C2B9FB2E532D880592A49",
    PC_MSGGAME_RESIDUALS: "0FBF1825F47463F00382B05F955CDE13A0816A3E7A552B852270ED457CB8A6FB",
}
PUBLIC_OVERLAY = WORKSTREAM / "public" / "translation_quality_corrections.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
AUTONOMOUS_WORDING_OVERLAY = REPO / "workstreams" / "translation_quality_semantic_fixes_v1" / "public" / "autonomous_wording.v1.json"
EVENT_LAYOUT_RUNTIME = REPO / "workstreams" / "steam_jp_msgev_full_layout_v2" / "build_steam_jp_msgev_full_layout_v2.py"

OVERLAY_SCHEMA = "nobu16.kr.translation-quality-corrections-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.translation-quality-corrections-validation.v1"
MANIFEST_SCHEMA = "nobu16.kr.translation-quality-corrections-build-manifest.v1"

# The patch intentionally uses U+30FB (・) as a Korean list separator.  It is
# punctuation, not a Japanese-language residue, and must remain legal in a
# Korean replacement.
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
# Keep the brackets in the profile.  Review proposals and the runtime syntax
# both refer to the complete token (for example ``[bm1251]``); retaining that
# representation avoids silently comparing a different notation.
RUNTIME_TOKEN_RE = re.compile(r"\[[a-z]+\d+\]")
MALFORMED_RUNTIME_OPEN_RE = re.compile(r"\[\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
EVENT_MAX_LINES = 3
EVENT_MAX_LINE_PX = 912
# A packed msggame record may concatenate multiple literal slots at runtime.
# This is deliberately a one-record contract, not a general permission to
# alter outer whitespace: slot 0 needs one ASCII separator before the
# unchanged fortress-name slot, and slot 2 completes the sentence.
PK_MSGGAME_JOIN_CONTRACT = "pk_msggame_17_1078_adjacency.v1"
PK_MSGGAME_JOIN_COORDINATES = ("17:1078:0", "17:1078:1", "17:1078:2")
PK_MSGGAME_JOIN_EDIT_COORDINATES = ("17:1078:0", "17:1078:2")
PK_MSGGAME_JOIN_WHITESPACE_COORDINATE = "17:1078:0"
PK_MSGGAME_CONSTRUCTION_SPACE_CONTRACT = "pk_msggame_construction_space_bridge.v1"
PK_MSGGAME_CONSTRUCTION_SPACE_PAIRS = (
    ("6:3846:1", "6:3846:2"),
    ("6:3847:1", "6:3847:2"),
)
PK_MSGGAME_CONSTRUCTION_SPACE_COORDINATES = tuple(
    coordinate for pair in PK_MSGGAME_CONSTRUCTION_SPACE_PAIRS for coordinate in pair
)
PK_MSGGAME_CONSTRUCTION_SPACE_WHITESPACE_COORDINATES = tuple(pair[0] for pair in PK_MSGGAME_CONSTRUCTION_SPACE_PAIRS)
# Five base-game battle prompts split ``enemy headquarters`` and the next
# literal without an ASCII separator.  These are deliberately enumerated:
# this is a record-join contract, not a general permission to change outer
# whitespace in base msggame literals.
BASE_MSGGAME_BOUNDARY_CONTRACT = "base_msggame_enemy_headquarters_boundary.v1"
BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES = (
    "7:756:0",
    "7:766:0",
    "7:770:0",
    "7:781:0",
    "7:784:0",
)


class CorrectionError(ValueError):
    """Raised when a correction would lose a text-format invariant."""


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative: str
    parser: str
    proposal_paths: tuple[Path, ...]
    pc_only_override_paths: tuple[Path, ...] = ()


SPECS = (
    # msgui includes confirmed coordinate realignments.  Those replacements
    # must be checked against the same-coordinate pristine PC Japanese text,
    # rather than merely against the current Korean formatting profile, so it
    # is intentionally frozen by translation_quality_msgui_realign_v1.
    ResourceSpec(
        "msgbre",
        "MSG_PK/JP/msgbre.bin",
        "common",
        (
            PRIVATE_SEMANTIC / "msgbre_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "msgbre_quality_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "msgbre_pc_only_quality_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "horse_riding_clarity_addendum.v1.jsonl",
            MSGBRE_RESTORED_FACTS,
        ),
    ),
    ResourceSpec(
        "msgdata",
        "MSG_PK/JP/msgdata.bin",
        "common",
        (
            PRIVATE_PROPOSALS / "msgdata_ko.jsonl",
            PRIVATE_SEMANTIC / "msgdata_quality_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_quality_semantic_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_quality_reading_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_quality_terminology_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_quality_facility_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_quality_trait_semantic_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_quality_industry_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_quality_ui_labels_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_literal_placeholder_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_labor_terminology_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_semantic_ui_term_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_shuu_suffix_consistency_candidates.v1.jsonl",
            PRIVATE_SEMANTIC / "msgdata_tsu_reading_consistency_candidates.v1.jsonl",
            MSGDATA_TSU_OUTER_WHITESPACE,
            PC_ANCHOR_REAUDIT,
            PRIVATE_SEMANTIC / "msgdata_battle_key_site_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "utsunomiya_reading_consistency_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "territorial_measures_term_consistency_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "horse_riding_clarity_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "static_name_special_glyph_addendum.v1.jsonl",
        ),
        pc_only_override_paths=(PC_TRANSLATION_RESIDUALS_ANCHORS,),
    ),
    ResourceSpec(
        "strdata",
        "MSG/JP/strdata.bin",
        "strdata",
        (
            PRIVATE_PROPOSALS / "strdata_ko.jsonl",
            PRIVATE_SEMANTIC / "strdata_quality_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "strdata_residual_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "territorial_measures_term_consistency_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "strdata_cross_resource_labels_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "strdata_battle_key_site_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "utsunomiya_reading_consistency_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "horse_riding_clarity_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "static_name_special_glyph_addendum.v1.jsonl",
        ),
        pc_only_override_paths=(PC_TRANSLATION_RESIDUALS_ANCHORS,),
    ),
    ResourceSpec(
        "msgev",
        "MSG_PK/JP/msgev.bin",
        "common",
        (
            PRIVATE_SEMANTIC / "msgev_ko_rebased_v2r.v1.jsonl",
            PRIVATE_PROPOSALS / "msgev_semantic_quality_v1.jsonl",
            PRIVATE_PROPOSALS / "msgev_cjk_residual_candidates_v1.jsonl",
            PRIVATE_SEMANTIC / "msgev_ginchiyo_glyph_fix_v1.jsonl",
            PRIVATE_SEMANTIC / "msgev_semantic_quality_v2r_novel.v1.jsonl",
            PRIVATE_SEMANTIC / "msgev_semantic_quality_v2r2_addendum.jsonl",
            PRIVATE_SEMANTIC / "msgev_tsu_to_sseu_static_consistency_candidates.v1.jsonl",
            PRIVATE_SEMANTIC / "msgev_highrisk_semantic_propername_v1.jsonl",
            PRIVATE_SEMANTIC / "yousho_location_clarity_candidates.v1.jsonl",
            RESIDUAL_THREE_PC_ONLY,
            MSGEV_PC_CANONICAL_TITLE_REPAIR,
        ),
        pc_only_override_paths=(EVENT_SEMANTIC_RESIDUALS_PC_ONLY,),
    ),
    # This is a semantic-quality pass over the base PC event strings.  Its
    # private review rows use ``proposed_ko`` and per-coordinate current
    # hashes, both accepted below before a source-free overlay is frozen.
    ResourceSpec(
        "ev_strdata",
        "MSG/JP/ev_strdata.bin",
        "common",
        (
            PRIVATE_SEMANTIC / "ev_strdata_findings_rebased_v8.v1.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_quality_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_semantic_quality_v2.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_semantic_relationship_addendum_v1.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_semantic_quality_v3.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_semantic_quality_v4.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_proper_name_quality_v5.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_semantic_quality_v6r.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_battle_death_clarity_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "yousho_location_clarity_candidates.v1.jsonl",
            PRIVATE_SEMANTIC / "ev_strdata_pc_only_quality_addendum.v1.jsonl",
            EV_STRDATA_PC_REAUDIT,
        ),
    ),
    ResourceSpec(
        "msgire",
        "MSG_PK/JP/msgire.bin",
        "common",
        (
            PRIVATE_SEMANTIC / "msgire_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "msgire_proper_name_reference_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "msgire_pc_only_quality_addendum.v1.jsonl",
        ),
    ),
    ResourceSpec(
        "msgstf",
        "MSG_PK/JP/msgstf.bin",
        "common",
        (
            PRIVATE_SEMANTIC / "msgstf_pc_only_quality_addendum.v1.jsonl",
        ),
    ),
    ResourceSpec(
        "msgstf_ce",
        "MSG_PK/JP/msgstf_ce.bin",
        "common",
        (
            PRIVATE_SEMANTIC / "msgstf_ce_pc_only_quality_addendum.v1.jsonl",
        ),
    ),
    ResourceSpec(
        "base_msggame",
        "MSG/JP/msggame.bin",
        "msggame",
        (
            PRIVATE_SEMANTIC / "base_msggame_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "base_msggame_additional_findings.v1.jsonl",
            PRIVATE_SEMANTIC / "base_msggame_castle_capture_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "base_msggame_japanese_punctuation_candidates.v1.jsonl",
            PRIVATE_SEMANTIC / "base_msggame_quality_candidates.v2.jsonl",
            PRIVATE_SEMANTIC / "base_msggame_quality_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "base_msggame_quality_addendum.v2.jsonl",
            PRIVATE_SEMANTIC / "base_msggame_quality_addendum.v3.jsonl",
            PRIVATE_SEMANTIC / "base_msggame_quality_addendum.v4.jsonl",
            RESIDUAL_THREE_PC_ONLY,
            AUTONOMOUS_WORDING_OVERLAY,
            BASE_MSGGAME_PC_REAUDIT,
        ),
    ),
    ResourceSpec(
        "pk_msggame",
        "MSG_PK/JP/msggame.bin",
        "msggame",
        (
            PRIVATE_SEMANTIC / "pk_msggame_quality_findings_rebased_v2.v1.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_broad_candidates.v1.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_broad_candidates.v2.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_broad_candidates.v3.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_block17_candidates.v1.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_block17_candidates.v2.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_block17_candidates.v3.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_block17_candidates.v4.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_crossblock_candidates.v1.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_crossblock_candidates.v2.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_crossblock_candidates.v3r.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_crossblock_candidates.v4.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_crossblock_candidates.v5r.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_japanese_punctuation_candidates.v2r.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_dynamic_child_candidates.v1.jsonl",
            PRIVATE_SEMANTIC / "pk_msggame_key_site_addendum.v1.jsonl",
            PRIVATE_SEMANTIC / "horse_riding_clarity_addendum.v1.jsonl",
            RESIDUAL_THREE_PC_ONLY,
            AUTONOMOUS_WORDING_OVERLAY,
            PK_MSGGAME_PC_REAUDIT,
        ),
        pc_only_override_paths=(PC_MSGGAME_RESIDUALS,),
    ),
)
SPEC_BY_NAME = {spec.name: spec for spec in SPECS}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def pretty_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def safe_private_output(path: Path) -> Path:
    output = path.resolve()
    root = (REPO / "tmp").resolve()
    if output == root or root not in output.parents:
        raise CorrectionError(f"candidate output must stay below {root}: {output}")
    return output


def coordinate_key(spec: ResourceSpec, row: Mapping[str, Any]) -> str:
    if spec.parser == "common":
        value = row.get("id")
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise CorrectionError(f"{spec.name} proposal has an invalid id: {value!r}")
        return str(value)
    if spec.parser == "msggame":
        value = row.get("coordinate")
        if not isinstance(value, str) or len(value.split(":")) != 3 or any(not part.isdecimal() for part in value.split(":")):
            raise CorrectionError(f"{spec.name} proposal has an invalid literal coordinate: {value!r}")
        return value
    block = row.get("block")
    entry_id = row.get("id")
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in (block, entry_id)):
        raise CorrectionError(f"{spec.name} proposal has an invalid block/id")
    return f"{block}:{entry_id}"


def coordinate_sort_key(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split(":"))


def read_autonomous_wording_overlay(path: Path, spec: ResourceSpec) -> list[dict[str, Any]]:
    """Adapt the separately frozen, source-free wording overlay.

    The wording pass has the same two ``msggame`` resources as this builder.
    Reading its public overlay here lets one private candidate contain both
    sets of non-overlapping corrections, while retaining the original
    current-text hash gate for every coordinate.  The overlay contains no
    Japanese source text and declares that Switch Korean was not used.
    """
    overlay = strict_json(path)
    policy = overlay.get("distribution_policy")
    expected_policy = {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "switch_korean_translation_used": False,
    }
    if overlay.get("overlay_id") != "autonomous_wording.v1" or policy != expected_policy:
        raise CorrectionError(f"unexpected autonomous wording overlay: {path}")
    resources = overlay.get("resources")
    if not isinstance(resources, list):
        raise CorrectionError(f"autonomous wording resources are invalid: {path}")
    matches = [resource for resource in resources if isinstance(resource, Mapping) and resource.get("name") == spec.name]
    if len(matches) != 1:
        raise CorrectionError(f"autonomous wording resource is absent/ambiguous for {spec.name}")
    resource = matches[0]
    baseline = resource.get("baseline")
    entries = resource.get("entries")
    if not isinstance(baseline, Mapping) or baseline.get("relative_path") != spec.relative or not isinstance(entries, list):
        raise CorrectionError(f"autonomous wording resource is malformed for {spec.name}")
    if resource.get("entry_count") != len(entries):
        raise CorrectionError(f"autonomous wording entry count differs for {spec.name}")
    rows: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise CorrectionError(f"autonomous wording entry is invalid for {spec.name}")
        coordinate = coordinate_key(spec, entry)
        ko = entry.get("ko")
        source_hash = entry.get("source_current_utf16le_sha256")
        ko_hash = entry.get("ko_utf16le_sha256")
        if (
            not isinstance(ko, str)
            or not ko
            or not isinstance(source_hash, str)
            or not HEX64_RE.fullmatch(source_hash.upper())
            or not isinstance(ko_hash, str)
            or ko_hash.upper() != sha256_text(ko)
        ):
            raise CorrectionError(f"autonomous wording entry fails its hash gate at {spec.name}:{coordinate}")
        # Use the original current-text hash as a normal proposal gate.  This
        # still rejects a live Steam file that was edited after the wording
        # overlay was frozen.
        rows.append({"coordinate": coordinate, "ko": ko, "proposal": {"current_hash": source_hash}})
    return rows


def format_profile(text: str) -> dict[str, Any]:
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
        "fullwidth_percent_count": text.count("％"),
        "marker_334d_count": text.count("㌍"),
    }


def profile_delta(before: Mapping[str, Any], after: Mapping[str, Any]) -> list[str]:
    return [key for key in before if before[key] != after[key]]


def proposal_replacement(proposal: Mapping[str, Any]) -> tuple[str, str | None]:
    """Return the reviewed replacement and its private current-text field.

    The early audit generators wrote ``proposed_ko``/``ko`` while the
    PC-only full-audit generators use ``proposed_korean``/``current_korean``.
    Both schemas carry an exact current-text hash and are accepted here only
    as an explicit before/after pair; plain ``ko`` rows remain replacements.
    The canonical-title repair has a deliberately separate, hash-bound
    ``translation`` schema so arbitrary similarly named private fields are
    never accepted as Korean replacements.
    """

    has_short = "proposed_ko" in proposal
    has_long = "proposed_korean" in proposal
    has_canonical_title = "translation" in proposal
    if has_canonical_title:
        required_canonical_title_fields = {
            "id",
            "canonical_anchor_id",
            "candidate_jp_utf16le_sha256",
            "current_ko_utf16le_sha256",
            "canonical_jp_utf16le_sha256",
            "translation",
            "translation_utf16le_sha256",
            "proof",
        }
        if (
            has_short
            or has_long
            or "ko" in proposal
            or set(proposal) != required_canonical_title_fields
            or proposal.get("proof") != "full_canonical_pc_title_anchor"
            or isinstance(proposal.get("canonical_anchor_id"), bool)
            or not isinstance(proposal.get("canonical_anchor_id"), int)
            or proposal["canonical_anchor_id"] < 0
        ):
            raise CorrectionError("ambiguous canonical-title Korean replacement schema")
        value = proposal["translation"]
        current_key = None
    elif has_short and has_long:
        if proposal["proposed_ko"] != proposal["proposed_korean"]:
            raise CorrectionError("conflicting private Korean replacements")
        raise CorrectionError("ambiguous private Korean replacement schema")
    elif has_short:
        value = proposal["proposed_ko"]
        # Recent PC-only reaudits call the before-value ``current_ko`` while
        # older semantic batches call it ``ko``.  Both are explicit private
        # before/after pairs and must be hash-bound during freeze.
        current_key = "ko" if "ko" in proposal else "current_ko"
    elif has_long:
        value = proposal["proposed_korean"]
        current_key = "current_korean"
    else:
        value = proposal.get("ko")
        current_key = None
    if not isinstance(value, str) or not value:
        raise CorrectionError("proposal lacks a Korean replacement")
    return value, current_key


def read_proposals(spec: ResourceSpec, proposal_paths: Sequence[Path] | None = None) -> list[dict[str, Any]]:
    paths = spec.proposal_paths if proposal_paths is None else proposal_paths
    rows: list[dict[str, Any]] = []
    for path in paths:
        if path == AUTONOMOUS_WORDING_OVERLAY:
            rows.extend(read_autonomous_wording_overlay(path, spec))
            continue
        if not path.is_file():
            raise CorrectionError(f"private reviewed proposal is absent: {path}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CorrectionError(f"invalid JSONL at {path}:{line_number}") from exc
            if not isinstance(row, dict):
                raise CorrectionError(f"proposal row is not an object at {path}:{line_number}")
            # A small cross-resource addendum can declare its destination
            # explicitly.  Older PC-only review generators used the stable
            # packed-resource path while this builder uses a short resource
            # name.  Both exact identifiers are accepted for the matching
            # resource only; all other destinations remain ignored.
            declared_resource = row.get("resource")
            if declared_resource is not None:
                if not isinstance(declared_resource, str):
                    raise CorrectionError(f"proposal resource is invalid at {path}:{line_number}")
                if declared_resource not in {spec.name, spec.relative}:
                    continue
            coordinate = coordinate_key(spec, row)
            try:
                ko, current_key = proposal_replacement(row)
            except CorrectionError as exc:
                raise CorrectionError(f"{exc} at {spec.name}:{coordinate}") from exc
            # Keep the private current-field name with the normalized entry
            # so freeze can bind the before/after pair to the live PC table.
            if current_key is not None:
                row = dict(row)
                row["_private_current_key"] = current_key
            rows.append({"coordinate": coordinate, "ko": ko, "proposal": row})
    if not rows:
        raise CorrectionError(f"proposal file has no rows for {spec.name}")
    rows.sort(key=lambda row: coordinate_sort_key(row["coordinate"]))
    duplicates = [row["coordinate"] for index, row in enumerate(rows[1:], start=1) if row["coordinate"] == rows[index - 1]["coordinate"]]
    if duplicates:
        raise CorrectionError(f"duplicate proposal coordinate(s) for {spec.name}: {duplicates[:5]!r}")
    return rows


def read_pc_only_override_proposals(spec: ResourceSpec) -> list[dict[str, Any]]:
    """Read a fixed, direct-PC review batch that may supersede older wording.

    Normal proposal inputs are intentionally duplicate-free.  A PC-only
    full-audit batch is different: its evidence is newer and was reviewed from
    the pristine PC Japanese and PC EN/SC/TC resources, so it may replace a
    legacy rendering at the same coordinate.  Only the two byte-pinned paths
    declared above receive this authority; all usual inputs still reject
    duplicates before anything is frozen.
    """

    if not spec.pc_only_override_paths:
        return []
    for path in spec.pc_only_override_paths:
        expected = PC_ONLY_OVERRIDE_INPUT_SHA256.get(path)
        if expected is None:
            raise CorrectionError(f"unapproved PC-only override input for {spec.name}: {path}")
        if not path.is_file():
            raise CorrectionError(f"PC-only override input is absent for {spec.name}: {path}")
        if sha256_bytes(path.read_bytes()) != expected:
            raise CorrectionError(f"PC-only override input hash differs for {spec.name}: {path}")
    return read_proposals(spec, spec.pc_only_override_paths)


def load_common(path: Path) -> tuple[bytes, bytes, MessageTable, dict[str, str]]:
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise CorrectionError(f"unchanged common-table rebuild differs: {path}")
    return packed, raw, table, {str(index): text for index, text in enumerate(table.texts)}


def load_strdata(path: Path) -> tuple[bytes, bytes, Any, dict[str, str]]:
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    archive = parse_raw_strdata(raw)
    if rebuild_raw_strdata(archive) != raw:
        raise CorrectionError(f"unchanged strdata rebuild differs: {path}")
    return packed, raw, archive, {f"{block}:{slot}": text for (block, slot), text in coordinate_texts(archive).items()}


def load_msggame(path: Path) -> tuple[bytes, bytes, Any, dict[str, str]]:
    packed = path.read_bytes()
    parsed = parse_packed_msggame(packed)
    _header, raw = decompress_wrapper(packed)
    # A no-op literal rebuild is expected to be byte-identical.  This guards
    # the opaque bytecode around literals before any semantic replacement is
    # considered.
    if rebuild_packed_with_literals(packed, {}) != packed:
        raise CorrectionError(f"unchanged msggame rebuild differs: {path}")
    texts = {
        f"{literal.block_id}:{literal.record_id}:{literal.literal_id}": literal.text
        for literal in iter_literals(parsed.archive)
    }
    return packed, raw, parsed, texts


def load_resource(steam_root: Path, spec: ResourceSpec) -> tuple[Path, bytes, bytes, Any, dict[str, str]]:
    path = (steam_root.resolve() / Path(spec.relative)).resolve()
    if not path.is_file():
        raise CorrectionError(f"live resource is absent: {path}")
    if spec.parser == "common":
        packed, raw, parsed, texts = load_common(path)
    elif spec.parser == "strdata":
        packed, raw, parsed, texts = load_strdata(path)
    elif spec.parser == "msggame":
        packed, raw, parsed, texts = load_msggame(path)
    else:
        raise CorrectionError(f"unsupported parser: {spec.parser}")
    return path, packed, raw, parsed, texts


def private_pk_msggame_join_proof(proposal: Mapping[str, Any], coordinate: str) -> Mapping[str, Any]:
    """Read the private three-literal proof for the sole whitespace exception.

    The review material stays under ``tmp`` because it includes the live
    before/after joined text.  The public overlay retains only the checked
    joined-text hash and the fixed coordinate contract.
    """
    if coordinate not in PK_MSGGAME_JOIN_EDIT_COORDINATES:
        raise CorrectionError(f"unexpected msggame join coordinate: {coordinate}")
    proof = proposal.get("adjacent_literal_validation")
    required = {"status", "record_coordinates", "current_join", "proposed_join", "proposed_join_utf16le_sha256"}
    if (
        not isinstance(proof, Mapping)
        or set(proof) != required
        or proof.get("status") != "three_literal_join_verified"
        or proof.get("record_coordinates") != list(PK_MSGGAME_JOIN_COORDINATES)
        or not isinstance(proof.get("current_join"), str)
        or not isinstance(proof.get("proposed_join"), str)
        or not isinstance(proof.get("proposed_join_utf16le_sha256"), str)
        or not HEX64_RE.fullmatch(proof["proposed_join_utf16le_sha256"].upper())
    ):
        raise CorrectionError(f"invalid private msggame join proof at {coordinate}")
    return proof


def freeze_pk_msggame_join_proof(texts: Mapping[str, str], entries: Sequence[dict[str, Any]], rows: Sequence[Mapping[str, Any]]) -> None:
    """Bind the 17:1078 literal join to live text before freezing it.

    This does not make whitespace changes generally acceptable.  It permits
    exactly one trailing ASCII space in the first literal, verifies that the
    middle fortress-name literal remains untouched, and hashes the final
    three-literal Korean sentence.
    """
    row_by_coordinate = {row["coordinate"]: row["proposal"] for row in rows}
    relevant_rows = set(row_by_coordinate).intersection(PK_MSGGAME_JOIN_COORDINATES)
    if not relevant_rows:
        return
    if relevant_rows != set(PK_MSGGAME_JOIN_EDIT_COORDINATES):
        raise CorrectionError("incomplete or unexpected private msggame join rows")
    if any(coordinate not in texts for coordinate in PK_MSGGAME_JOIN_COORDINATES):
        raise CorrectionError("msggame join coordinate is absent from live text")

    entry_by_coordinate = {entry["coordinate"]: entry for entry in entries}
    if (
        set(PK_MSGGAME_JOIN_EDIT_COORDINATES) - set(entry_by_coordinate)
        or PK_MSGGAME_JOIN_COORDINATES[1] in entry_by_coordinate
    ):
        raise CorrectionError("msggame join must edit only its first and third literals")

    proofs = [
        private_pk_msggame_join_proof(row_by_coordinate[coordinate], coordinate)
        for coordinate in PK_MSGGAME_JOIN_EDIT_COORDINATES
    ]
    if proofs[0] != proofs[1]:
        raise CorrectionError("msggame join proof differs between edited literals")
    proof = proofs[0]
    current_join = "".join(texts[coordinate] for coordinate in PK_MSGGAME_JOIN_COORDINATES)
    proposed_join = "".join(
        entry_by_coordinate.get(coordinate, {"ko": texts[coordinate]})["ko"]
        for coordinate in PK_MSGGAME_JOIN_COORDINATES
    )
    if (
        proof["current_join"] != current_join
        or proof["proposed_join"] != proposed_join
        or sha256_text(proposed_join) != proof["proposed_join_utf16le_sha256"].upper()
    ):
        raise CorrectionError("msggame joined text differs from the private review proof")

    first = entry_by_coordinate[PK_MSGGAME_JOIN_WHITESPACE_COORDINATE]
    third = entry_by_coordinate[PK_MSGGAME_JOIN_EDIT_COORDINATES[1]]
    before_first_profile = format_profile(texts[PK_MSGGAME_JOIN_WHITESPACE_COORDINATE])
    after_first_profile = format_profile(first["ko"])
    if (
        first["allowed_format_delta"] != ["trailing_whitespace"]
        or third["allowed_format_delta"] != []
        or before_first_profile["trailing_whitespace"] != ""
        or after_first_profile["trailing_whitespace"] != " "
        or first["ko"][-1:] != " "
        or first["ko"].endswith("  ")
        or profile_delta(before_first_profile, after_first_profile) != ["trailing_whitespace"]
        or profile_delta(format_profile(texts[PK_MSGGAME_JOIN_EDIT_COORDINATES[1]]), format_profile(third["ko"])) != []
    ):
        raise CorrectionError("msggame join whitespace exception differs from its narrow contract")

    public_proof = {
        "contract": PK_MSGGAME_JOIN_CONTRACT,
        "coordinates": list(PK_MSGGAME_JOIN_COORDINATES),
        "proposed_join_utf16le_sha256": proof["proposed_join_utf16le_sha256"].upper(),
    }
    for coordinate in PK_MSGGAME_JOIN_EDIT_COORDINATES:
        entry_by_coordinate[coordinate]["adjacent_join"] = dict(public_proof)


def validate_frozen_pk_msggame_join(texts: Mapping[str, str], entries: Sequence[Mapping[str, Any]]) -> None:
    """Recheck the source-free join proof against the live Korean baseline."""
    entry_by_coordinate = {entry.get("coordinate"): entry for entry in entries if isinstance(entry, Mapping)}
    entries_with_proof = {
        coordinate
        for coordinate, entry in entry_by_coordinate.items()
        if isinstance(entry, Mapping) and "adjacent_join" in entry
    }
    if not entries_with_proof:
        return
    if (
        entries_with_proof != set(PK_MSGGAME_JOIN_EDIT_COORDINATES)
        or PK_MSGGAME_JOIN_COORDINATES[1] in entry_by_coordinate
        or any(coordinate not in texts for coordinate in PK_MSGGAME_JOIN_COORDINATES)
    ):
        raise CorrectionError("frozen msggame join coordinates differ")

    proofs = [entry_by_coordinate[coordinate]["adjacent_join"] for coordinate in PK_MSGGAME_JOIN_EDIT_COORDINATES]
    required = {"contract", "coordinates", "proposed_join_utf16le_sha256"}
    proof = proofs[0]
    if (
        not all(isinstance(value, Mapping) and value == proof for value in proofs)
        or not isinstance(proof, Mapping)
        or set(proof) != required
        or proof.get("contract") != PK_MSGGAME_JOIN_CONTRACT
        or proof.get("coordinates") != list(PK_MSGGAME_JOIN_COORDINATES)
        or not isinstance(proof.get("proposed_join_utf16le_sha256"), str)
        or not HEX64_RE.fullmatch(proof["proposed_join_utf16le_sha256"].upper())
    ):
        raise CorrectionError("frozen msggame join proof differs")

    first = entry_by_coordinate[PK_MSGGAME_JOIN_WHITESPACE_COORDINATE]
    third = entry_by_coordinate[PK_MSGGAME_JOIN_EDIT_COORDINATES[1]]
    before_first_profile = format_profile(texts[PK_MSGGAME_JOIN_WHITESPACE_COORDINATE])
    after_first_profile = format_profile(first["ko"])
    if (
        first.get("allowed_format_delta") != ["trailing_whitespace"]
        or third.get("allowed_format_delta") != []
        or before_first_profile["trailing_whitespace"] != ""
        or after_first_profile["trailing_whitespace"] != " "
        or first.get("ko", "")[-1:] != " "
        or first.get("ko", "").endswith("  ")
        or profile_delta(before_first_profile, after_first_profile) != ["trailing_whitespace"]
        or profile_delta(format_profile(texts[PK_MSGGAME_JOIN_EDIT_COORDINATES[1]]), format_profile(third["ko"])) != []
    ):
        raise CorrectionError("frozen msggame whitespace exception differs")
    proposed_join = "".join(
        entry_by_coordinate.get(coordinate, {"ko": texts[coordinate]})["ko"]
        for coordinate in PK_MSGGAME_JOIN_COORDINATES
    )
    if sha256_text(proposed_join) != proof["proposed_join_utf16le_sha256"].upper():
        raise CorrectionError("frozen msggame joined text hash differs")


def freeze_pk_msggame_construction_space_proofs(
    texts: Mapping[str, str], entries: Sequence[dict[str, Any]], rows: Sequence[Mapping[str, Any]]
) -> None:
    """Permit exactly two paired literal-space bridges in construction notices.

    The Korean record splits ``<castle>의 <facility> 건설 ...`` across slots
    1 and 2.  A missing final clause needs a single separator, but that space
    is preserved by appending it to slot 1 rather than changing slot 2's
    leading-whitespace contract.  No other ``pk_msggame`` whitespace change
    is accepted by this proof.
    """
    row_by_coordinate = {row["coordinate"]: row["proposal"] for row in rows}
    expected = set(PK_MSGGAME_CONSTRUCTION_SPACE_COORDINATES)
    relevant = set(row_by_coordinate).intersection(expected)
    if not relevant:
        return
    if relevant != expected:
        raise CorrectionError("incomplete or unexpected construction-space review rows")

    entry_by_coordinate = {entry["coordinate"]: entry for entry in entries}
    if expected - set(entry_by_coordinate):
        raise CorrectionError("construction-space coordinates are absent from frozen entries")

    for whitespace_coordinate, clause_coordinate in PK_MSGGAME_CONSTRUCTION_SPACE_PAIRS:
        if whitespace_coordinate not in texts or clause_coordinate not in texts:
            raise CorrectionError("construction-space coordinate is absent from live text")
        whitespace_entry = entry_by_coordinate[whitespace_coordinate]
        clause_entry = entry_by_coordinate[clause_coordinate]
        before_profile = format_profile(texts[whitespace_coordinate])
        after_profile = format_profile(whitespace_entry["ko"])
        if (
            whitespace_entry["allowed_format_delta"] != ["trailing_whitespace"]
            or clause_entry["allowed_format_delta"] != []
            or before_profile["trailing_whitespace"] != ""
            or after_profile["trailing_whitespace"] != " "
            or whitespace_entry["ko"].endswith("  ")
            or whitespace_entry["ko"][-1:] != " "
            or clause_entry["ko"][:1].isspace()
            or profile_delta(before_profile, after_profile) != ["trailing_whitespace"]
            or profile_delta(format_profile(texts[clause_coordinate]), format_profile(clause_entry["ko"])) != []
        ):
            raise CorrectionError("construction-space literal contract differs")
        proposed_join = whitespace_entry["ko"] + clause_entry["ko"]
        proof = {
            "contract": PK_MSGGAME_CONSTRUCTION_SPACE_CONTRACT,
            "coordinates": [whitespace_coordinate, clause_coordinate],
            "proposed_join_utf16le_sha256": sha256_text(proposed_join),
        }
        whitespace_entry["construction_space_join"] = dict(proof)
        clause_entry["construction_space_join"] = dict(proof)


def validate_frozen_pk_msggame_construction_space_proofs(
    texts: Mapping[str, str], entries: Sequence[Mapping[str, Any]]
) -> None:
    """Recheck both source-free construction-space contracts after freeze."""
    entry_by_coordinate = {entry.get("coordinate"): entry for entry in entries if isinstance(entry, Mapping)}
    expected = set(PK_MSGGAME_CONSTRUCTION_SPACE_COORDINATES)
    entries_with_proof = {
        coordinate
        for coordinate, entry in entry_by_coordinate.items()
        if isinstance(entry, Mapping) and "construction_space_join" in entry
    }
    if not entries_with_proof:
        return
    if entries_with_proof != expected:
        raise CorrectionError("frozen construction-space coordinates differ")

    required = {"contract", "coordinates", "proposed_join_utf16le_sha256"}
    for whitespace_coordinate, clause_coordinate in PK_MSGGAME_CONSTRUCTION_SPACE_PAIRS:
        if whitespace_coordinate not in texts or clause_coordinate not in texts:
            raise CorrectionError("frozen construction-space coordinate is absent")
        whitespace_entry = entry_by_coordinate[whitespace_coordinate]
        clause_entry = entry_by_coordinate[clause_coordinate]
        proof = whitespace_entry["construction_space_join"]
        if (
            not isinstance(proof, Mapping)
            or clause_entry.get("construction_space_join") != proof
            or set(proof) != required
            or proof.get("contract") != PK_MSGGAME_CONSTRUCTION_SPACE_CONTRACT
            or proof.get("coordinates") != [whitespace_coordinate, clause_coordinate]
            or not isinstance(proof.get("proposed_join_utf16le_sha256"), str)
            or not HEX64_RE.fullmatch(proof["proposed_join_utf16le_sha256"].upper())
        ):
            raise CorrectionError("frozen construction-space proof differs")
        before_profile = format_profile(texts[whitespace_coordinate])
        after_profile = format_profile(whitespace_entry["ko"])
        if (
            whitespace_entry.get("allowed_format_delta") != ["trailing_whitespace"]
            or clause_entry.get("allowed_format_delta") != []
            or before_profile["trailing_whitespace"] != ""
            or after_profile["trailing_whitespace"] != " "
            or whitespace_entry.get("ko", "").endswith("  ")
            or whitespace_entry.get("ko", "")[-1:] != " "
            or clause_entry.get("ko", "")[:1].isspace()
            or profile_delta(before_profile, after_profile) != ["trailing_whitespace"]
            or profile_delta(format_profile(texts[clause_coordinate]), format_profile(clause_entry["ko"])) != []
        ):
            raise CorrectionError("frozen construction-space literal contract differs")
        proposed_join = whitespace_entry["ko"] + clause_entry["ko"]
        if sha256_text(proposed_join) != proof["proposed_join_utf16le_sha256"].upper():
            raise CorrectionError("frozen construction-space joined text hash differs")


def base_msggame_record_coordinates(texts: Mapping[str, str], coordinate: str) -> list[str]:
    """Return the complete literal sequence for one base msggame record."""

    parts = coordinate.split(":")
    if len(parts) != 3 or any(not value.isdecimal() for value in parts):
        raise CorrectionError(f"invalid base msggame coordinate: {coordinate!r}")
    prefix = ":".join(parts[:2]) + ":"
    result = sorted(
        (value for value in texts if value.startswith(prefix)),
        key=coordinate_sort_key,
    )
    if not result or coordinate not in result:
        raise CorrectionError(f"base msggame record is absent for {coordinate}")
    return result


def private_base_msggame_boundary_proof(proposal: Mapping[str, Any], coordinate: str) -> Mapping[str, Any]:
    """Validate the private full-record evidence for one boundary-space edit."""

    if coordinate not in BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES:
        raise CorrectionError(f"unexpected base msggame boundary coordinate: {coordinate}")
    proof = proposal.get("linked_record_contract")
    required = {
        "status",
        "literal_layouts",
        "target_literal_id",
        "current_ko_literal_texts",
        "proposed_ko_literal_texts",
        "current_ko_literal_concatenation",
        "proposed_ko_literal_concatenation",
        "whole_record_format",
        "nonliteral_bytecode",
    }
    expected_record_format = {
        "newlines": "match",
        "outer_ascii_whitespace": "match",
        "question_marks": "unchanged",
    }
    if (
        not isinstance(proof, Mapping)
        or set(proof) != required
        or proof.get("status") != "whole_literal_sequence_newline_runtime_slots_and_nonliteral_bytecode_validated"
        or proof.get("target_literal_id") != 0
        or not isinstance(proof.get("literal_layouts"), Mapping)
        or set(proof["literal_layouts"]) != {"jp", "ko", "sc", "tc"}
        or not all(
            isinstance(value, list) and all(isinstance(item, int) and item >= 0 for item in value)
            for value in proof["literal_layouts"].values()
        )
        or not all(
            isinstance(proof.get(key), list) and all(isinstance(value, str) for value in proof[key])
            for key in ("current_ko_literal_texts", "proposed_ko_literal_texts")
        )
        or not all(
            isinstance(proof.get(key), str)
            for key in ("current_ko_literal_concatenation", "proposed_ko_literal_concatenation")
        )
        or proof.get("whole_record_format") != expected_record_format
        or not isinstance(proof.get("nonliteral_bytecode"), Mapping)
        or set(proof["nonliteral_bytecode"]) != {"status", "before_skeleton_sha256", "after_skeleton_sha256"}
        or proof["nonliteral_bytecode"].get("status") != "unchanged_after_rebuild"
        or not all(
            isinstance(proof["nonliteral_bytecode"].get(key), str)
            and HEX64_RE.fullmatch(proof["nonliteral_bytecode"][key].upper())
            for key in ("before_skeleton_sha256", "after_skeleton_sha256")
        )
    ):
        raise CorrectionError(f"invalid private base msggame boundary proof at {coordinate}")
    return proof


def freeze_base_msggame_boundary_proofs(
    texts: Mapping[str, str],
    entries: Sequence[dict[str, Any]],
    rows: Sequence[Mapping[str, Any]],
) -> None:
    """Freeze the five explicitly reviewed base-message literal joins."""

    row_by_coordinate = {row["coordinate"]: row["proposal"] for row in rows}
    relevant_rows = set(row_by_coordinate).intersection(BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES)
    if not relevant_rows:
        return
    expected = set(BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES)
    if relevant_rows != expected:
        raise CorrectionError("incomplete base msggame boundary-space review set")
    entry_by_coordinate = {entry["coordinate"]: entry for entry in entries}
    if expected - set(entry_by_coordinate):
        raise CorrectionError("base msggame boundary entry is absent from frozen overlay")

    for coordinate in BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES:
        proof = private_base_msggame_boundary_proof(row_by_coordinate[coordinate], coordinate)
        coordinates = base_msggame_record_coordinates(texts, coordinate)
        current_literals = [texts[value] for value in coordinates]
        record_entries = {value for value in coordinates if value in entry_by_coordinate}
        if record_entries != {coordinate}:
            raise CorrectionError("base msggame boundary record has an unexpected second edit")
        proposed_literals = [
            entry_by_coordinate.get(value, {"ko": texts[value]})["ko"]
            for value in coordinates
        ]
        current_join = "".join(current_literals)
        proposed_join = "".join(proposed_literals)
        if (
            proof["literal_layouts"]["ko"] != list(range(len(coordinates)))
            or proof["current_ko_literal_texts"] != current_literals
            or proof["proposed_ko_literal_texts"] != proposed_literals
            or proof["current_ko_literal_concatenation"] != current_join
            or proof["proposed_ko_literal_concatenation"] != proposed_join
        ):
            raise CorrectionError("base msggame boundary private record proof differs from live text")
        entry = entry_by_coordinate[coordinate]
        before_profile = format_profile(texts[coordinate])
        after_profile = format_profile(entry["ko"])
        if (
            entry["allowed_format_delta"] != ["trailing_whitespace"]
            or before_profile["trailing_whitespace"] != ""
            or after_profile["trailing_whitespace"] != " "
            or entry["ko"][-1:] != " "
            or entry["ko"].endswith("  ")
            or profile_delta(before_profile, after_profile) != ["trailing_whitespace"]
        ):
            raise CorrectionError("base msggame boundary whitespace exception differs from its narrow contract")
        entry["adjacent_join"] = {
            "contract": BASE_MSGGAME_BOUNDARY_CONTRACT,
            "coordinates": coordinates,
            "proposed_join_utf16le_sha256": sha256_text(proposed_join),
        }


def validate_frozen_base_msggame_boundary_proofs(
    texts: Mapping[str, str], entries: Sequence[Mapping[str, Any]]
) -> None:
    """Recheck the source-free base-message literal-join contracts."""

    entry_by_coordinate = {
        entry.get("coordinate"): entry for entry in entries if isinstance(entry, Mapping)
    }
    entries_with_proof = {
        coordinate
        for coordinate, entry in entry_by_coordinate.items()
        if isinstance(entry, Mapping) and "adjacent_join" in entry
    }
    expected = set(BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES)
    if not entries_with_proof:
        return
    if entries_with_proof != expected:
        raise CorrectionError("frozen base msggame boundary coordinates differ")
    required = {"contract", "coordinates", "proposed_join_utf16le_sha256"}
    for coordinate in BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES:
        entry = entry_by_coordinate[coordinate]
        proof = entry["adjacent_join"]
        coordinates = base_msggame_record_coordinates(texts, coordinate)
        record_entries = {value for value in coordinates if value in entry_by_coordinate}
        if (
            not isinstance(proof, Mapping)
            or set(proof) != required
            or proof.get("contract") != BASE_MSGGAME_BOUNDARY_CONTRACT
            or proof.get("coordinates") != coordinates
            or not isinstance(proof.get("proposed_join_utf16le_sha256"), str)
            or not HEX64_RE.fullmatch(proof["proposed_join_utf16le_sha256"].upper())
            or record_entries != {coordinate}
        ):
            raise CorrectionError("frozen base msggame boundary proof differs")
        before_profile = format_profile(texts[coordinate])
        after_profile = format_profile(entry["ko"])
        if (
            entry.get("allowed_format_delta") != ["trailing_whitespace"]
            or before_profile["trailing_whitespace"] != ""
            or after_profile["trailing_whitespace"] != " "
            or entry.get("ko", "")[-1:] != " "
            or entry.get("ko", "").endswith("  ")
            or profile_delta(before_profile, after_profile) != ["trailing_whitespace"]
        ):
            raise CorrectionError("frozen base msggame boundary whitespace exception differs")
        proposed_join = "".join(
            entry_by_coordinate.get(value, {"ko": texts[value]})["ko"]
            for value in coordinates
        )
        if sha256_text(proposed_join) != proof["proposed_join_utf16le_sha256"].upper():
            raise CorrectionError("frozen base msggame joined text hash differs")


def validate_replacement(before: str, after: str, spec: ResourceSpec, coordinate: str, proposal: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    if "\0" in after or "\ufffd" in after:
        raise CorrectionError(f"unsafe NUL/replacement glyph at {spec.name}:{coordinate}")
    if KANA_OR_HAN_RE.search(after):
        raise CorrectionError(f"replacement retains Japanese/CJK text at {spec.name}:{coordinate}")
    # A PowerShell code-page failure can turn an entire Korean proposal into
    # repeated literal question marks.  A normal Korean question may contain
    # one or two ``?`` characters, but a multi-mark string with no Hangul is
    # never a usable correction in this package.
    if after.count("?") >= 3 and not HANGUL_RE.search(after):
        raise CorrectionError(f"suspicious question-mark-only replacement at {spec.name}:{coordinate}")
    if spec.name == "msgev" and len(re.split(r"\r\n|\n|\r", after)) > EVENT_MAX_LINES:
        raise CorrectionError(f"event dialogue exceeds the three-line limit at {spec.name}:{coordinate}")
    if MALFORMED_RUNTIME_OPEN_RE.search(after):
        raise CorrectionError(f"replacement retains malformed double runtime opener at {spec.name}:{coordinate}")
    before_profile = format_profile(before)
    after_profile = format_profile(after)
    delta = profile_delta(before_profile, after_profile)
    requested = proposal.get("allowed_format_delta")
    if requested is None:
        # Normal translation repairs must preserve every non-text invariant.
        # Event token repairs explicitly identify themselves through this field.
        if delta:
            raise CorrectionError(f"unapproved format delta at {spec.name}:{coordinate}: {delta!r}")
    else:
        if not isinstance(requested, list) or any(not isinstance(value, str) for value in requested):
            raise CorrectionError(f"invalid allowed_format_delta at {spec.name}:{coordinate}")
        # The review file may list permitted profile keys in a human-friendly
        # order; compare the set while still rejecting duplicated entries.
        if len(set(requested)) != len(requested) or set(requested) != set(delta):
            raise CorrectionError(f"format delta differs from proposal at {spec.name}:{coordinate}: expected={requested!r}, actual={delta!r}")
        # Event dialogue sometimes needs a deliberate, reviewer-recorded
        # reflow after a runtime token is restored.  It remains constrained to
        # the three-line/width check performed by the private review, and is
        # never accepted unless that delta is explicitly recorded per row.
        # An explicitly recorded empty list is equivalent to the default
        # no-delta policy and is safe for every resource.  Only a *real*
        # profile change needs the narrower event-dialogue exception below.
        if delta:
            safe_event_deltas = {"runtime_tokens", "malformed_runtime_open_count", "line_breaks"}
            safe_event = spec.name == "msgev" and set(delta).issubset(safe_event_deltas)
            safe_msggame_join = (
                spec.name == "pk_msggame"
                and coordinate == PK_MSGGAME_JOIN_WHITESPACE_COORDINATE
                and delta == ["trailing_whitespace"]
            )
            safe_pk_msggame_construction_space = (
                spec.name == "pk_msggame"
                and coordinate in PK_MSGGAME_CONSTRUCTION_SPACE_WHITESPACE_COORDINATES
                and delta == ["trailing_whitespace"]
            )
            safe_base_msggame_boundary = (
                spec.name == "base_msggame"
                and coordinate in BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES
                and delta == ["trailing_whitespace"]
            )
            if safe_msggame_join:
                private_pk_msggame_join_proof(proposal, coordinate)
            if not safe_event and not safe_msggame_join and not safe_pk_msggame_construction_space and not safe_base_msggame_boundary:
                raise CorrectionError(f"unsafe permitted format delta at {spec.name}:{coordinate}: {delta!r}")
    expected_runtime = proposal.get("expected_runtime_tokens")
    if expected_runtime is not None:
        if not isinstance(expected_runtime, list) or not all(isinstance(value, str) for value in expected_runtime):
            raise CorrectionError(f"invalid expected_runtime_tokens at {spec.name}:{coordinate}")
        if after_profile["runtime_tokens"] != expected_runtime:
            raise CorrectionError(f"runtime tokens differ from approved target at {spec.name}:{coordinate}")
    return before_profile, after_profile, delta


@lru_cache(maxsize=2)
def event_layout_runtime(steam_root_key: str) -> tuple[Any, Any, Mapping[str, int]]:
    """Load the local PC font/reservation verifier for frozen event metrics.

    This is layout-only evidence: it reads the current PC font and the
    checked-in runtime-token reservation table, never a Switch text table or
    a Korean translation reference.
    """

    spec = importlib.util.spec_from_file_location(
        "translation_quality_corrections_event_layout", EVENT_LAYOUT_RUNTIME
    )
    if spec is None or spec.loader is None:
        raise CorrectionError("cannot load the PC event layout verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    try:
        advance, _font = module.current_font(Path(steam_root_key))
        reservations, _excluded, _document = module.load_reservations()
    except Exception as exc:  # pragma: no cover - external layout verifier
        raise CorrectionError("cannot load PC event layout metrics") from exc
    return module, advance, reservations


def measured_event_layout(after: str, steam_root: Path, coordinate: str) -> tuple[list[int], list[int]]:
    module, advance, reservations = event_layout_runtime(str(steam_root.resolve()))
    try:
        actual, reserved = module.target_width_pairs(after, advance, reservations)
    except Exception as exc:  # pragma: no cover - external layout verifier
        raise CorrectionError(f"cannot measure event layout at msgev:{coordinate}") from exc
    if (
        not actual
        or len(actual) != len(reserved)
        or len(actual) > EVENT_MAX_LINES
        or any(not isinstance(value, int) or value < 0 or value > EVENT_MAX_LINE_PX for value in actual)
        or any(not isinstance(value, int) or value < 0 or value > EVENT_MAX_LINE_PX for value in reserved)
    ):
        raise CorrectionError(f"event layout exceeds the PC three-line budget at msgev:{coordinate}")
    return actual, reserved


def event_layout_proof(
    before: str,
    after: str,
    proposal: Mapping[str, Any],
    coordinate: str,
    steam_root: Path,
) -> dict[str, Any]:
    """Validate and preserve the reviewer-calculated event layout evidence.

    The event font has fixed 48px wide-script cells, but dynamic name tokens
    consume a coordinate-specific reserved width.  The private reviewer has
    that reservation data; this function makes its resulting line metrics a
    required, source-free part of the frozen overlay rather than a comment
    that can be lost between review and build.
    """
    validation = proposal.get("validation")
    linebreak = validation.get("linebreak") if isinstance(validation, Mapping) else None
    if linebreak is None:
        # Older PC-only name/semantic audit batches predate the event-layout
        # field.  They are admissible only when all format markers (including
        # manual breaks) stay unchanged, after which the local PC font
        # verifier independently measures the proposed text.
        if format_profile(before) != format_profile(after):
            raise CorrectionError(f"unreviewed format change at msgev:{coordinate}")
        actual, reserved = measured_event_layout(after, steam_root, coordinate)
        return {
            "line_count": len(actual),
            "line_widths_px": actual,
            "reserved_line_widths_px": reserved,
            "max_line_px": EVENT_MAX_LINE_PX,
        }
    if not isinstance(linebreak, Mapping):
        raise CorrectionError(f"event linebreak validation is invalid at msgev:{coordinate}")
    lines = re.split(r"\r\n|\n|\r", after)
    actual = linebreak.get("actual_widths_px")
    reserved = linebreak.get("reserved_widths_px")
    candidate_count = linebreak.get("candidate_line_count")
    if (
        not isinstance(candidate_count, int)
        or candidate_count != len(lines)
        or candidate_count > EVENT_MAX_LINES
        or linebreak.get("max_line_px") != EVENT_MAX_LINE_PX
        or linebreak.get("within_three_line_budget") is not True
        or not isinstance(actual, list)
        or not isinstance(reserved, list)
        or len(actual) != candidate_count
        or len(reserved) != candidate_count
        or not all(isinstance(value, int) and 0 <= value <= EVENT_MAX_LINE_PX for value in actual)
        or not all(isinstance(value, int) and 0 <= value <= EVENT_MAX_LINE_PX for value in reserved)
    ):
        raise CorrectionError(f"invalid event layout proof at msgev:{coordinate}")
    return {
        "line_count": candidate_count,
        "line_widths_px": actual,
        "reserved_line_widths_px": reserved,
        "max_line_px": EVENT_MAX_LINE_PX,
    }


def validate_frozen_event_layout(after: str, proof: Any, coordinate: str) -> None:
    if not isinstance(proof, Mapping):
        raise CorrectionError(f"frozen event layout proof is absent at msgev:{coordinate}")
    lines = re.split(r"\r\n|\n|\r", after)
    actual = proof.get("line_widths_px")
    reserved = proof.get("reserved_line_widths_px")
    if (
        set(proof) != {"line_count", "line_widths_px", "reserved_line_widths_px", "max_line_px"}
        or proof.get("line_count") != len(lines)
        or proof.get("line_count") > EVENT_MAX_LINES
        or proof.get("max_line_px") != EVENT_MAX_LINE_PX
        or not isinstance(actual, list)
        or not isinstance(reserved, list)
        or len(actual) != len(lines)
        or len(reserved) != len(lines)
        or not all(isinstance(value, int) and 0 <= value <= EVENT_MAX_LINE_PX for value in actual)
        or not all(isinstance(value, int) and 0 <= value <= EVENT_MAX_LINE_PX for value in reserved)
    ):
        raise CorrectionError(f"frozen event layout proof is invalid at msgev:{coordinate}")


def resource_baseline(packed: bytes, raw: bytes, texts: Mapping[str, str], spec: ResourceSpec) -> dict[str, Any]:
    return {
        "relative_path": spec.relative,
        "parser": spec.parser,
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "coordinate_count": len(texts),
    }


def freeze(steam_root: Path) -> dict[str, Any]:
    resources: list[dict[str, Any]] = []
    total_entries = 0
    for spec in SPECS:
        _path, packed, raw, _parsed, texts = load_resource(steam_root, spec)
        entries: list[dict[str, Any]] = []
        review_rows = read_proposals(spec)
        pc_only_override_rows = read_pc_only_override_proposals(spec)
        if pc_only_override_rows:
            # The normal input set remains duplicate-free.  For the handful
            # of coordinates subjected to the newer direct-PC review, use the
            # hash-pinned PC-only result instead of treating an older Korean
            # rendering as semantic authority.
            review_by_coordinate = {row["coordinate"]: row for row in review_rows}
            review_by_coordinate.update({row["coordinate"]: row for row in pc_only_override_rows})
            review_rows = [review_by_coordinate[coordinate] for coordinate in sorted(review_by_coordinate, key=coordinate_sort_key)]
        for row in review_rows:
            coordinate = row["coordinate"]
            if coordinate not in texts:
                raise CorrectionError(f"proposal coordinate is absent from live {spec.name}: {coordinate}")
            before = texts[coordinate]
            private_current_key = row["proposal"].get("_private_current_key")
            if private_current_key is not None:
                private_current = row["proposal"].get(private_current_key)
                if not isinstance(private_current, str) or private_current != before:
                    raise CorrectionError(f"private semantic current text differs at {spec.name}:{coordinate}")
            supplied_hashes = [
                row["proposal"][key]
                for key in (
                    "source_hash",
                    "current_hash",
                    "current_text_sha256",
                    "current_ko_sha256",
                    "current_ko_utf16le_sha256",
                    "current_korean_utf16le_sha256",
                    "current_text_utf16le_sha256",
                )
                if key in row["proposal"]
            ]
            nested_source_hashes = row["proposal"].get("source_hashes")
            if nested_source_hashes is not None:
                if not isinstance(nested_source_hashes, Mapping):
                    raise CorrectionError(f"private proposal source-hash mapping is invalid at {spec.name}:{coordinate}")
                nested_current = nested_source_hashes.get("current_ko_utf16le_sha256")
                if nested_current is None:
                    nested_current = nested_source_hashes.get("current_pc_ko_utf16le_sha256")
                if nested_current is not None:
                    supplied_hashes.append(nested_current)
            if supplied_hashes:
                if (
                    not all(isinstance(value, str) and HEX64_RE.fullmatch(value.upper()) for value in supplied_hashes)
                    or len({value.upper() for value in supplied_hashes}) != 1
                    or supplied_hashes[0].upper() != sha256_text(before)
                ):
                    raise CorrectionError(f"private proposal source hash differs at {spec.name}:{coordinate}")
            after = row["ko"]
            proposed_hashes = [
                row["proposal"][key]
                for key in (
                    "proposed_text_sha256",
                    "proposed_ko_sha256",
                    "proposed_ko_utf16le_sha256",
                    "proposed_korean_utf16le_sha256",
                    "proposed_text_utf16le_sha256",
                    "translation_utf16le_sha256",
                )
                if key in row["proposal"]
            ]
            if nested_source_hashes is not None:
                nested_proposed = nested_source_hashes.get("proposed_ko_utf16le_sha256")
                if nested_proposed is not None:
                    proposed_hashes.append(nested_proposed)
            if proposed_hashes and (
                not all(isinstance(value, str) and HEX64_RE.fullmatch(value.upper()) for value in proposed_hashes)
                or len({value.upper() for value in proposed_hashes}) != 1
                or proposed_hashes[0].upper() != sha256_text(after)
            ):
                raise CorrectionError(f"private proposal target hash differs at {spec.name}:{coordinate}")
            before_profile, after_profile, delta = validate_replacement(before, after, spec, coordinate, row["proposal"])
            entry = {
                "coordinate": coordinate,
                "source_current_utf16le_sha256": sha256_text(before),
                "ko": after,
                "ko_utf16le_sha256": sha256_text(after),
                "source_format_profile_sha256": canonical_hash(before_profile),
                "ko_format_profile_sha256": canonical_hash(after_profile),
                "allowed_format_delta": delta,
            }
            if spec.name == "msgev":
                entry["event_layout"] = event_layout_proof(before, after, row["proposal"], coordinate, steam_root)
            entries.append(entry)
        if spec.name == "pk_msggame":
            freeze_pk_msggame_join_proof(texts, entries, review_rows)
            freeze_pk_msggame_construction_space_proofs(texts, entries, review_rows)
        if spec.name == "base_msggame":
            freeze_base_msggame_boundary_proofs(texts, entries, review_rows)
        if not entries:
            raise CorrectionError(f"no corrections loaded for {spec.name}")
        resources.append({"name": spec.name, "baseline": resource_baseline(packed, raw, texts, spec), "entry_count": len(entries), "entries": entries})
        total_entries += len(entries)
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "translation_quality_corrections.v1",
        "scope": "verified PC Steam Korean quality fixes; Switch Korean translation excluded from review authority",
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "switch_korean_translation_used": False},
        "resource_count": len(resources),
        "entry_count": total_entries,
        "resources": resources,
    }
    overlay_blob = pretty_json(overlay)
    assert_source_free_blob(overlay_blob, "overlay")
    atomic_write(PUBLIC_OVERLAY, overlay_blob)

    validation = validate_overlay(steam_root, overlay)
    validation_blob = pretty_json(validation)
    assert_source_free_blob(validation_blob, "validation")
    atomic_write(VALIDATION, validation_blob)
    return {
        "resource_count": len(resources),
        "entry_count": total_entries,
        "overlay_sha256": sha256_bytes(overlay_blob),
        "validation_sha256": sha256_bytes(validation_blob),
        "steam_installation_written": False,
    }


def assert_source_free_blob(blob: bytes, label: str) -> None:
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CorrectionError(f"{label} is not UTF-8") from exc
    if KANA_OR_HAN_RE.search(text):
        raise CorrectionError(f"{label} unexpectedly contains Japanese/CJK source text")


def strict_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CorrectionError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CorrectionError(f"JSON root is not an object: {path}")
    return value


def validate_overlay(steam_root: Path, overlay: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if overlay is None:
        overlay = strict_json(PUBLIC_OVERLAY)
    required = {"schema", "overlay_id", "scope", "distribution_policy", "resource_count", "entry_count", "resources"}
    if set(overlay) != required or overlay["schema"] != OVERLAY_SCHEMA or overlay["overlay_id"] != "translation_quality_corrections.v1":
        raise CorrectionError("public overlay header differs")
    expected_policy = {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "switch_korean_translation_used": False}
    if overlay["distribution_policy"] != expected_policy:
        raise CorrectionError("public overlay policy differs")
    resources_value = overlay["resources"]
    if not isinstance(resources_value, list) or overlay["resource_count"] != len(resources_value) or len(resources_value) != len(SPECS):
        raise CorrectionError("public overlay resource count differs")
    total_entries = 0
    validations: list[dict[str, Any]] = []
    for index, resource in enumerate(resources_value):
        spec = SPECS[index]
        if not isinstance(resource, dict) or set(resource) != {"name", "baseline", "entry_count", "entries"} or resource["name"] != spec.name:
            raise CorrectionError(f"public overlay resource differs at index {index}")
        _path, packed, raw, _parsed, texts = load_resource(steam_root, spec)
        if resource["baseline"] != resource_baseline(packed, raw, texts, spec):
            raise CorrectionError(f"Steam baseline differs for {spec.name}")
        entries = resource["entries"]
        if not isinstance(entries, list) or resource["entry_count"] != len(entries) or not entries:
            raise CorrectionError(f"public overlay entries differ for {spec.name}")
        last_coordinate: tuple[int, ...] | None = None
        changes = 0
        for entry in entries:
            if not isinstance(entry, dict):
                raise CorrectionError(f"unexpected entry schema in {spec.name}")
            required_entry = {"coordinate", "source_current_utf16le_sha256", "ko", "ko_utf16le_sha256", "source_format_profile_sha256", "ko_format_profile_sha256", "allowed_format_delta"}
            if spec.name == "msgev":
                required_entry = required_entry | {"event_layout"}
            if spec.name == "pk_msggame" and entry.get("coordinate") in PK_MSGGAME_JOIN_EDIT_COORDINATES:
                required_entry = required_entry | {"adjacent_join"}
            if spec.name == "pk_msggame" and entry.get("coordinate") in PK_MSGGAME_CONSTRUCTION_SPACE_COORDINATES:
                required_entry = required_entry | {"construction_space_join"}
            if spec.name == "base_msggame" and entry.get("coordinate") in BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES:
                required_entry = required_entry | {"adjacent_join"}
            if set(entry) != required_entry:
                raise CorrectionError(f"unexpected entry schema in {spec.name}")
            coordinate = entry["coordinate"]
            if not isinstance(coordinate, str) or coordinate not in texts:
                raise CorrectionError(f"entry coordinate is absent in {spec.name}: {coordinate!r}")
            sort_key = coordinate_sort_key(coordinate)
            if last_coordinate is not None and sort_key <= last_coordinate:
                raise CorrectionError(f"entries are not strictly sorted in {spec.name}")
            last_coordinate = sort_key
            before = texts[coordinate]
            after = entry["ko"]
            if not isinstance(after, str) or not all(isinstance(entry[key], str) and HEX64_RE.fullmatch(entry[key]) for key in ("source_current_utf16le_sha256", "ko_utf16le_sha256", "source_format_profile_sha256", "ko_format_profile_sha256")):
                raise CorrectionError(f"invalid hash/string field in {spec.name}:{coordinate}")
            before_profile = format_profile(before)
            after_profile = format_profile(after)
            delta = profile_delta(before_profile, after_profile)
            if sha256_text(before) != entry["source_current_utf16le_sha256"] or sha256_text(after) != entry["ko_utf16le_sha256"]:
                raise CorrectionError(f"source or Korean hash differs at {spec.name}:{coordinate}")
            if canonical_hash(before_profile) != entry["source_format_profile_sha256"] or canonical_hash(after_profile) != entry["ko_format_profile_sha256"]:
                raise CorrectionError(f"format profile hash differs at {spec.name}:{coordinate}")
            if entry["allowed_format_delta"] != delta:
                raise CorrectionError(f"format delta differs at {spec.name}:{coordinate}")
            if KANA_OR_HAN_RE.search(after) or MALFORMED_RUNTIME_OPEN_RE.search(after):
                raise CorrectionError(f"unsafe published replacement at {spec.name}:{coordinate}")
            if after.count("?") >= 3 and not HANGUL_RE.search(after):
                raise CorrectionError(f"suspicious published question-mark-only replacement at {spec.name}:{coordinate}")
            if spec.name == "msgev" and len(re.split(r"\r\n|\n|\r", after)) > 3:
                raise CorrectionError(f"published event dialogue exceeds the three-line limit at {spec.name}:{coordinate}")
            if spec.name == "msgev":
                validate_frozen_event_layout(after, entry["event_layout"], coordinate)
            if delta:
                safe_event = spec.name == "msgev" and set(delta).issubset({"runtime_tokens", "malformed_runtime_open_count", "line_breaks"})
                safe_msggame_join = (
                    spec.name == "pk_msggame"
                    and coordinate == PK_MSGGAME_JOIN_WHITESPACE_COORDINATE
                    and delta == ["trailing_whitespace"]
                )
                safe_pk_msggame_construction_space = (
                    spec.name == "pk_msggame"
                    and coordinate in PK_MSGGAME_CONSTRUCTION_SPACE_WHITESPACE_COORDINATES
                    and delta == ["trailing_whitespace"]
                )
                safe_base_msggame_boundary = (
                    spec.name == "base_msggame"
                    and coordinate in BASE_MSGGAME_BOUNDARY_WHITESPACE_COORDINATES
                    and delta == ["trailing_whitespace"]
                )
                if not safe_event and not safe_msggame_join and not safe_pk_msggame_construction_space and not safe_base_msggame_boundary:
                    raise CorrectionError(f"unapproved frozen delta at {spec.name}:{coordinate}")
            if before != after:
                changes += 1
        if spec.name == "pk_msggame":
            validate_frozen_pk_msggame_join(texts, entries)
            validate_frozen_pk_msggame_construction_space_proofs(texts, entries)
        if spec.name == "base_msggame":
            validate_frozen_base_msggame_boundary_proofs(texts, entries)
        total_entries += len(entries)
        validations.append({"name": spec.name, "entry_count": len(entries), "effective_change_count": changes, "checks": {"baseline": "OK", "source_hashes": "OK", "format_profiles": "OK", "replacement_safety": "OK"}})
    if overlay["entry_count"] != total_entries:
        raise CorrectionError("public overlay total entry count differs")
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "switch_korean_translation_used": False,
        "overlay": {"relative_path": "workstreams/translation_quality_corrections_v1/public/translation_quality_corrections.v1.json", "sha256": sha256_bytes(PUBLIC_OVERLAY.read_bytes()) if PUBLIC_OVERLAY.is_file() else None},
        "resource_count": len(validations),
        "entry_count": total_entries,
        "resources": validations,
        "checks": {"source_hash_gates": "OK", "format_profiles": "OK", "Steam_installation_written": False},
    }


def replacement_maps(overlay: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for resource in overlay["resources"]:
        result[resource["name"]] = {entry["coordinate"]: entry["ko"] for entry in resource["entries"]}
    return result


def build_common_candidate(raw: bytes, table: MessageTable, replacements: Mapping[str, str]) -> bytes:
    texts = list(table.texts)
    for coordinate, value in replacements.items():
        texts[int(coordinate)] = value
    first = rebuild_message_table(table, texts)
    second = rebuild_message_table(table, texts)
    if first != second:
        raise CorrectionError("common-table rebuild is not deterministic")
    parsed = parse_message_table(first)
    if parsed.texts != tuple(texts) or rebuild_message_table(parsed, parsed.texts) != first:
        raise CorrectionError("common candidate parser roundtrip differs")
    for index, before in enumerate(table.texts):
        expected = replacements.get(str(index), before)
        if parsed.texts[index] != expected:
            raise CorrectionError(f"common candidate text differs at {index}")
    return first


def build_strdata_candidate(raw: bytes, archive: Any, replacements: Mapping[str, str]) -> bytes:
    by_block: dict[int, list[str]] = {block.block_id: list(block.texts) for block in archive.blocks}
    for coordinate, value in replacements.items():
        block, slot = (int(part) for part in coordinate.split(":"))
        by_block[block][slot] = value
    first = rebuild_raw_strdata(archive, by_block)
    second = rebuild_raw_strdata(archive, by_block)
    if first != second:
        raise CorrectionError("strdata rebuild is not deterministic")
    parsed = parse_raw_strdata(first)
    texts = coordinate_texts(parsed)
    before_texts = coordinate_texts(archive)
    for (block, slot), before in before_texts.items():
        expected = replacements.get(f"{block}:{slot}", before)
        if texts[(block, slot)] != expected:
            raise CorrectionError(f"strdata candidate text differs at {block}:{slot}")
    if rebuild_raw_strdata(parsed) != first:
        raise CorrectionError("strdata candidate parser roundtrip differs")
    return first


def build_msggame_candidate(packed: bytes, parsed: Any, replacements: Mapping[str, str]) -> bytes:
    """Rebuild selected embedded literals without changing surrounding bytecode.

    ``msggame`` has a distinct nested-record format: changing a literal can
    shift later record and block offsets, so the packed-resource rebuilder is
    the single authority here.  We still compare every parsed literal after
    rebuilding, which catches an accidental coordinate conversion or a
    mutation outside the requested review rows.
    """
    literal_replacements: dict[tuple[int, int, int], str] = {}
    for coordinate, value in replacements.items():
        block_id, record_id, literal_id = (int(part) for part in coordinate.split(":"))
        literal_replacements[(block_id, record_id, literal_id)] = value

    first = rebuild_packed_with_literals(packed, literal_replacements)
    second = rebuild_packed_with_literals(packed, literal_replacements)
    if first != second:
        raise CorrectionError("msggame literal rebuild is not deterministic")

    candidate = parse_packed_msggame(first)
    before_texts = {
        f"{literal.block_id}:{literal.record_id}:{literal.literal_id}": literal.text
        for literal in iter_literals(parsed.archive)
    }
    candidate_texts = {
        f"{literal.block_id}:{literal.record_id}:{literal.literal_id}": literal.text
        for literal in iter_literals(candidate.archive)
    }
    if set(candidate_texts) != set(before_texts):
        raise CorrectionError("msggame candidate literal coordinates differ")
    for coordinate, before in before_texts.items():
        expected = replacements.get(coordinate, before)
        if candidate_texts[coordinate] != expected:
            raise CorrectionError(f"msggame candidate text differs at {coordinate}")
    if rebuild_packed_with_literals(first, {}) != first:
        raise CorrectionError("msggame candidate no-op rebuild differs")
    return first


def build(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output_root = safe_private_output(output_root)
    overlay = strict_json(PUBLIC_OVERLAY)
    validation = validate_overlay(steam_root, overlay)
    maps = replacement_maps(overlay)
    outputs: list[dict[str, Any]] = []
    for spec in SPECS:
        source_path, packed, raw, parsed, _texts = load_resource(steam_root, spec)
        replacements = maps[spec.name]
        if spec.parser == "common":
            candidate_raw = build_common_candidate(raw, parsed, replacements)
            candidate_a = recompress_wrapper(candidate_raw, packed)
            candidate_b = recompress_wrapper(candidate_raw, packed)
        elif spec.parser == "strdata":
            candidate_raw = build_strdata_candidate(raw, parsed, replacements)
            candidate_a = recompress_wrapper(candidate_raw, packed)
            candidate_b = recompress_wrapper(candidate_raw, packed)
        elif spec.parser == "msggame":
            candidate_a = build_msggame_candidate(packed, parsed, replacements)
            candidate_b = build_msggame_candidate(packed, parsed, replacements)
            _candidate_header, candidate_raw = decompress_wrapper(candidate_a)
        else:
            raise CorrectionError(f"unsupported parser: {spec.parser}")
        if candidate_a != candidate_b:
            raise CorrectionError(f"packed candidate is not deterministic: {spec.name}")
        _header, checked_raw = decompress_wrapper(candidate_a)
        if checked_raw != candidate_raw:
            raise CorrectionError(f"packed candidate roundtrip differs: {spec.name}")
        target = (output_root / Path(spec.relative)).resolve()
        if output_root not in target.parents:
            raise CorrectionError(f"candidate path escapes private output: {target}")
        atomic_write(target, candidate_a)
        if source_path.read_bytes() != packed or target.read_bytes() != candidate_a:
            raise CorrectionError(f"unexpected source or candidate mutation: {spec.name}")
        outputs.append({"name": spec.name, "relative_path": spec.relative, "packed_size": len(candidate_a), "packed_sha256": sha256_bytes(candidate_a), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "effective_change_count": sum(1 for coordinate, value in replacements.items() if _texts[coordinate] != value)})
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "switch_korean_translation_used": False,
        "validation": {"schema": validation["schema"], "entry_count": validation["entry_count"]},
        "output_policy": {"private_root": "tmp", "steam_installation_written": False, "release_asset_written": False, "github_written": False},
        "resources": outputs,
    }
    manifest_blob = pretty_json(manifest)
    assert_source_free_blob(manifest_blob, "candidate manifest")
    atomic_write(output_root / "build_manifest.v1.json", manifest_blob)
    return {"resource_count": len(outputs), "entry_count": validation["entry_count"], "output_root": str(output_root), "steam_installation_written": False}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    freeze_parser = subparsers.add_parser("freeze", help="freeze source-gated public corrections from private review proposals")
    freeze_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser = subparsers.add_parser("build", help="build private verified candidates from a frozen overlay")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)
    try:
        result = freeze(args.steam_root) if args.command == "freeze" else build(args.steam_root, args.output_root)
    except (CorrectionError, OSError, ValueError, KeyError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
