#!/usr/bin/env python3
"""Clean the three source-script residues in the Switch biography transfer.

The pinned Switch v1.3 ``strdata.bin`` is byte-identical to v1.1.  Three PK
biography rows match the Switch Korean text exactly but were excluded from the
strict transfer because one or two CJK code points remained as parenthetical
glosses.  This builder applies three deliberately narrow Hangul rewrites,
checks every PK SC message invariant, and emits source-text-free artifacts.

No complete game resource is written.  Target reconstruction happens only in
memory and every output is constrained to this repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
STRICT_ROOT = REPO_ROOT / "workstreams" / "switch_msgbre_v11"
sys.path[:0] = [str(TOOLS_ROOT), str(STRICT_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgbre_v11 as strict  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from strdata_container import EXPECTED_SLOT_COUNTS, parse_strdata, rebuild_strdata  # noqa: E402


BATCH_ID = "switch_v13_msgbre_cjk_cleanup_3.v0.1"
RESOURCE = "MSG_PK/SC/msgbre.bin"
SELECTED_IDS = [944, 1104, 1238]
EXPECTED_SELECTED_IDS_SHA256 = "C19CF4F02CB33DF4FC72C25443BA4E0FD7D5978B142DA7C2A62536881670BFC3"
EXPECTED_PRIOR_CLAIMED_COUNT = 2_203
EXPECTED_PRIOR_CLAIMED_IDS_SHA256 = "A1F577B7BBE1CDDF8440C0EE7B26434DB676AFBB1326E990999D434722F8FC5B"

OVERLAY_NAME = "msgbre_ko_switch_v13_cjk_cleanup_3.v0.1.json"
EVIDENCE_NAME = "switch_v13_msgbre_cjk_cleanup_evidence.v0.1.json"
REVIEW_NAME = "switch_v13_msgbre_cjk_cleanup_review_index.v0.1.json"
VALIDATION_NAME = "switch_v13_msgbre_cjk_cleanup_validation.v0.1.json"
SELF_OVERLAY_PATH = f"workstreams/switch_msgbre_v13_cjk_cleanup/public/{OVERLAY_NAME}"
EXPECTED_SELF_OVERLAY_SHA256 = "170A49AE210ED546888B33A4A4BD626AA44E66966B64217E4398847B989A4E43"
PREDECESSOR_BOUNDARY_PATH = (
    "workstreams/switch_msgbre_v11/public/msgbre_ko_switch_v11_strict_transfer.v0.1.json"
)
HISTORICAL_PROGRESS_SHA256 = "DB88E04F2DDC206F449263FF0CFE3CAA05EA4CD9E1030D58B5BD2EF1B444DD51"

SWITCH_ARCHIVE_RELATIVE = Path(
    "tmp/third_party_switch_v13/NobunagaShinsei_KoreanPatch_v1.3.zip"
)
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/strdata.bin"
SWITCH_README_MEMBER = "NobunagaShinsei_KR/README.md"
SWITCH_V13_ARCHIVE_PIN = {
    "size": 72_977_145,
    "sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
}
SWITCH_MEMBER_PIN = {
    "size": 404_189,
    "compressed_size": 294_162,
    "crc32": "B17A2EBB",
    "sha256": "5F065B9DBDAE4DC75E2D7186A76C0AC988FB504F018F820C204262BF07D5061B",
    "raw_size": 953_512,
    "raw_sha256": "245538466576E3880B3C53C0CB4929685096DF394C27CCB93B2C893615A46ADE",
}

# Hash pins prove that the cleanup starts from the exact Switch Korean rows and
# ends at the deliberately reviewed Hangul-only forms.  No source text is
# embedded in these records.
CLEANUP_PINS: dict[int, dict[str, Any]] = {
    944: {
        "switch_ko_utf16le_sha256": "5412943D73F702DE2AC7EE438321FF619FE6F83F680446DC99277D93D327C82B",
        "cleaned_ko_utf16le_sha256": "92CD0D2651CEA9309585E64F0F41131403739718B6FB5C71DDF37CE0B5BAE2BD",
        "before_cjk_count": 1,
        "cleanup_kind": "single_character_meaning_gloss_to_hangul",
    },
    1104: {
        "switch_ko_utf16le_sha256": "D60229FC6B4047441422CC1435735B7E9C3DD162854423D74A52B45B263D104A",
        "cleaned_ko_utf16le_sha256": "56A62C9A2504496175D266AEEA9E7824D4DC81CAA1F64099D19321B1DB665CB0",
        "before_cjk_count": 1,
        "cleanup_kind": "single_character_reading_to_hangul",
    },
    1238: {
        "switch_ko_utf16le_sha256": "C96302EFBF10B89361050960D09631E73836A3B923111238A9910C690A63543F",
        "cleaned_ko_utf16le_sha256": "9C36EE342A15A1E1DB46D6020FB4B9509A703A1E6391F7D7569611614515A68E",
        "before_cjk_count": 2,
        "cleanup_kind": "two_character_age_gloss_to_natural_hangul",
    },
}

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")


class MsgbreCleanupError(ValueError):
    """Raised when a pinned cleanup or safety gate fails."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def ids_sha256(ids: list[int]) -> str:
    return sha256(json.dumps(ids, separators=(",", ":")).encode("utf-8"))


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": len(CJK_RE.findall(text)),
        "kana_count": len(KANA_RE.findall(text)),
    }


def source_script_free(text: str) -> bool:
    return script_counts(text) == {"cjk_unified_count": 0, "kana_count": 0}


def write_json(path: Path, value: Any, logical_path: str) -> dict[str, Any]:
    blob = json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": logical_path, "size": len(blob), "sha256": sha256(blob)}


def _relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _safe_out_root(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise MsgbreCleanupError(
            "output must stay inside KR_PATCH_WORK; game files are never outputs"
        ) from exc
    return resolved


def cleanup_switch_korean(entry_id: int, text: str) -> str:
    """Apply the one reviewed, minimal source-script rewrite for ``entry_id``."""
    if entry_id == 944:
        needle = "무(" + chr(0x7121) + ")"
        replacement = "무(없을 무)"
    elif entry_id == 1104:
        needle = "「" + chr(0x4E5F) + "(야)」"
        replacement = "「야」"
    elif entry_id == 1238:
        needle = "일본 최고(" + chr(0x6700) + chr(0x53E4) + ")의"
        replacement = "일본에서 가장 오래된"
    else:
        raise MsgbreCleanupError(f"no reviewed cleanup for ID {entry_id}")
    if text.count(needle) != 1:
        raise MsgbreCleanupError(f"ID {entry_id} cleanup needle count is not one")
    cleaned = text.replace(needle, replacement, 1)
    if cleaned == text:
        raise MsgbreCleanupError(f"ID {entry_id} cleanup did not change the row")
    return cleaned


def load_switch_v13(archive_path: Path) -> tuple[Any, dict[str, Any]]:
    archive_blob = archive_path.read_bytes()
    if (
        len(archive_blob) != SWITCH_V13_ARCHIVE_PIN["size"]
        or sha256(archive_blob) != SWITCH_V13_ARCHIVE_PIN["sha256"]
    ):
        raise MsgbreCleanupError("Switch v1.3 archive does not match its release pin")
    with zipfile.ZipFile(archive_path) as archive:
        info = archive.getinfo(SWITCH_MEMBER)
        if info.flag_bits & 1:
            raise MsgbreCleanupError("Switch strdata member must not be encrypted")
        if (
            info.file_size != SWITCH_MEMBER_PIN["size"]
            or info.compress_size != SWITCH_MEMBER_PIN["compressed_size"]
            or f"{info.CRC:08X}" != SWITCH_MEMBER_PIN["crc32"]
        ):
            raise MsgbreCleanupError("Switch strdata ZIP metadata differs from the pin")
        packed = archive.read(info)
        readme = archive.read(SWITCH_README_MEMBER)
    if len(packed) != SWITCH_MEMBER_PIN["size"] or sha256(packed) != SWITCH_MEMBER_PIN["sha256"]:
        raise MsgbreCleanupError("Switch strdata member differs from the v1.3 pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != SWITCH_MEMBER_PIN["raw_size"] or sha256(raw) != SWITCH_MEMBER_PIN["raw_sha256"]:
        raise MsgbreCleanupError("Switch strdata raw payload differs from the pin")
    parsed = parse_strdata(raw)
    if (
        tuple(block.slot_count for block in parsed.blocks) != EXPECTED_SLOT_COUNTS
        or rebuild_strdata(parsed) != raw
    ):
        raise MsgbreCleanupError("Switch strdata does not strictly parse and rebuild")
    provenance = {
        "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
        "release_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.3",
        "tag": "v1.3",
        "author_attribution": "GitHub user snake7594",
        "archive_member": SWITCH_MEMBER,
        "archive_size": len(archive_blob),
        "archive_sha256": sha256(archive_blob),
        "member_size": len(packed),
        "member_sha256": sha256(packed),
        "member_raw_size": len(raw),
        "member_raw_sha256": sha256(raw),
        "member_readme_size": len(readme),
        "text_member_byte_identical_to_v1_1": (
            sha256(packed) == strict.SWITCH_MEMBER_PIN["sha256"]
        ),
        "v1_1_member_sha256_pin": strict.SWITCH_MEMBER_PIN["sha256"],
        "block_slot_counts": [block.slot_count for block in parsed.blocks],
    }
    if provenance["member_sha256"] != provenance["v1_1_member_sha256_pin"]:
        raise MsgbreCleanupError("Switch v1.3 text member is not byte-identical to v1.1")
    return parsed, provenance


def load_existing_claims(progress_path: Path) -> tuple[set[int], dict[str, Any]]:
    """Validate pinned predecessors and ignore disjoint source-free successors."""

    progress_blob = progress_path.read_bytes()
    progress = json.loads(progress_blob.decode("utf-8"))
    resources = progress.get("resources")
    matches = [
        item for item in resources if item.get("path") == RESOURCE
    ] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise MsgbreCleanupError("translation progress has no unique PK msgbre resource")
    globs = matches[0].get("overlay_globs")
    if not isinstance(globs, list) or not all(isinstance(item, str) for item in globs):
        raise MsgbreCleanupError("PK msgbre overlay configuration is invalid")
    claims: set[int] = set()
    overlays: list[dict[str, Any]] = []
    candidate_registered = False
    predecessor_boundary_seen = False
    successor_ids: set[int] = set()
    successor_overlays: list[dict[str, Any]] = []
    selected_ids = set(SELECTED_IDS)
    for pattern in globs:
        paths = sorted(REPO_ROOT.glob(pattern))
        if len(paths) != 1:
            raise MsgbreCleanupError(
                f"overlay pattern {pattern!r} resolved to {len(paths)} files"
            )
        path = paths[0]
        logical_path = _relative(path)
        blob = path.read_bytes()
        overlay = json.loads(blob.decode("utf-8"))
        if overlay.get("resource") != RESOURCE:
            raise MsgbreCleanupError(f"overlay {logical_path} targets another resource")
        entries = overlay.get("entries")
        if not isinstance(entries, list):
            raise MsgbreCleanupError(f"overlay {logical_path} entries are invalid")
        ids = [entry.get("id") for entry in entries]
        if any(type(entry_id) is not int for entry_id in ids):
            raise MsgbreCleanupError(f"overlay {logical_path} IDs are invalid")
        typed_ids = [int(entry_id) for entry_id in ids]
        if typed_ids != sorted(typed_ids) or len(typed_ids) != len(set(typed_ids)):
            raise MsgbreCleanupError(f"overlay {logical_path} IDs are not sorted and unique")

        if logical_path == SELF_OVERLAY_PATH:
            if pattern != SELF_OVERLAY_PATH:
                raise MsgbreCleanupError("candidate overlay must use its exact logical path")
            if candidate_registered:
                raise MsgbreCleanupError("candidate overlay is registered more than once")
            if not predecessor_boundary_seen:
                raise MsgbreCleanupError("candidate overlay precedes its pinned owner boundary")
            if (
                overlay.get("overlay_id") != BATCH_ID
                or sha256(blob) != EXPECTED_SELF_OVERLAY_SHA256
                or typed_ids != SELECTED_IDS
                or ids_sha256(typed_ids) != EXPECTED_SELECTED_IDS_SHA256
            ):
                raise MsgbreCleanupError("candidate overlay contract changed")
            candidate_registered = True
            continue

        if predecessor_boundary_seen:
            if pattern != logical_path:
                raise MsgbreCleanupError("successor overlays must use exact logical paths")
            policy = overlay.get("distribution_policy")
            if (
                not isinstance(policy, dict)
                or policy.get("contains_commercial_source_text") is not False
                or policy.get("contains_complete_game_resource") is not False
            ):
                raise MsgbreCleanupError(f"successor overlay is not source-free: {logical_path}")
            overlap = selected_ids.intersection(typed_ids)
            if overlap:
                raise MsgbreCleanupError(
                    f"successor overlay overlaps this cleanup at {min(overlap)}: {logical_path}"
                )
            overlap = claims.intersection(typed_ids)
            if overlap:
                raise MsgbreCleanupError(
                    f"successor overlay overlaps a pinned predecessor at {min(overlap)}: {logical_path}"
                )
            overlap = successor_ids.intersection(typed_ids)
            if overlap:
                raise MsgbreCleanupError(
                    f"successor overlays overlap at {min(overlap)}: {logical_path}"
                )
            successor_ids.update(typed_ids)
            successor_overlays.append(
                {
                    "logical_path": logical_path,
                    "sha256": sha256(blob),
                    "entry_count": len(typed_ids),
                    "ids_sha256": ids_sha256(typed_ids),
                    "source_free": True,
                    "excluded_from_prior_claims": True,
                }
            )
            continue

        if claims.intersection(typed_ids):
            raise MsgbreCleanupError(f"prior overlay IDs overlap at {logical_path}")
        claims.update(typed_ids)
        overlays.append(
            {
                "logical_path": logical_path,
                "sha256": sha256(blob),
                "entry_count": len(typed_ids),
                "min_id": min(typed_ids),
                "max_id": max(typed_ids),
            }
        )
        if logical_path == PREDECESSOR_BOUNDARY_PATH:
            predecessor_boundary_seen = True
    if not predecessor_boundary_seen:
        raise MsgbreCleanupError("pinned msgbre predecessor boundary is absent")
    claimed_hash = ids_sha256(sorted(claims))
    if (
        len(claims) != EXPECTED_PRIOR_CLAIMED_COUNT
        or claimed_hash != EXPECTED_PRIOR_CLAIMED_IDS_SHA256
    ):
        raise MsgbreCleanupError("prior PK msgbre coverage differs from the cleanup pin")
    snapshot = {
        "progress_logical_path": _relative(progress_path),
        "progress_sha256": sha256(progress_blob),
        "candidate_overlay_registered": candidate_registered,
        "candidate_overlay_excluded_from_prior_claims": True,
        "prior_overlays": overlays,
        "prior_overlay_count": len(overlays),
        "unique_claimed_count": len(claims),
        "claimed_ids_sha256": claimed_hash,
        "successor_overlays": successor_overlays,
        "successor_overlay_count": len(successor_overlays),
        "successor_effective_id_count": len(successor_ids),
        "successors_excluded_from_prior_claims": True,
    }
    return claims, snapshot


def historical_prior_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable derivation snapshot embedded in historical artifacts."""

    return {
        "progress_logical_path": snapshot["progress_logical_path"],
        "progress_sha256": HISTORICAL_PROGRESS_SHA256,
        "candidate_overlay_registered": True,
        "candidate_overlay_excluded_from_prior_claims": True,
        "prior_overlays": snapshot["prior_overlays"],
        "prior_overlay_count": snapshot["prior_overlay_count"],
        "unique_claimed_count": snapshot["unique_claimed_count"],
        "claimed_ids_sha256": snapshot["claimed_ids_sha256"],
    }


def derive_entries(
    switch_archive: Any,
    base_archive: Any,
    pk_jp: Any,
    pk_sc: Any,
    claimed_ids: set[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reverse_index, _ = strict.build_biography_reverse_index(base_archive, switch_archive)
    entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in SELECTED_IDS:
        if entry_id in claimed_ids:
            raise MsgbreCleanupError(f"ID {entry_id} overlaps a prior msgbre overlay")
        jp = pk_jp.texts[entry_id]
        sc = pk_sc.texts[entry_id]
        record = reverse_index.get(common.text_hash(jp))
        if record is None or record["jp"] != jp or record["candidate_ko"] is None:
            raise MsgbreCleanupError(f"ID {entry_id} has no exact convergent Switch mapping")
        candidate = str(record["candidate_ko"])
        pin = CLEANUP_PINS[entry_id]
        before_counts = script_counts(candidate)
        if (
            common.text_hash(candidate) != pin["switch_ko_utf16le_sha256"]
            or before_counts
            != {"cjk_unified_count": pin["before_cjk_count"], "kana_count": 0}
        ):
            raise MsgbreCleanupError(f"ID {entry_id} Switch candidate differs from its pin")
        cleaned = cleanup_switch_korean(entry_id, candidate)
        if (
            common.text_hash(cleaned) != pin["cleaned_ko_utf16le_sha256"]
            or not source_script_free(cleaned)
            or not HANGUL_RE.search(cleaned)
        ):
            raise MsgbreCleanupError(f"ID {entry_id} cleaned Korean differs from its pin")
        switch_problems = common.invariant_mismatches(sc, candidate)
        cleaned_problems = common.invariant_mismatches(sc, cleaned)
        if switch_problems or cleaned_problems:
            raise MsgbreCleanupError(f"ID {entry_id} does not preserve PK SC invariants")
        if not common.has_semantic_text(sc):
            raise MsgbreCleanupError(f"ID {entry_id} is outside the stock-visible target")
        sc_hash = common.text_hash(sc)
        entries.append(
            {"id": entry_id, "source_sc_utf16le_sha256": sc_hash, "ko": cleaned}
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "pk_jp_utf16le_sha256": common.text_hash(jp),
                "pk_sc_utf16le_sha256": sc_hash,
                "switch_ko_utf16le_sha256": common.text_hash(candidate),
                "cleaned_ko_utf16le_sha256": common.text_hash(cleaned),
                "base_biography_slot_count": record["slot_count"],
                "base_biography_slot_ids_sha256": record["slot_ids_sha256"],
                "cleanup_kind": pin["cleanup_kind"],
                "before_script_counts": before_counts,
                "after_script_counts": script_counts(cleaned),
                "exact_pk_jp_match": True,
                "switch_hash_converged": True,
                "selected_within_stock_visible_target": True,
                "all_pk_sc_message_invariants_preserved": True,
            }
        )
    ids = [entry["id"] for entry in entries]
    if ids != SELECTED_IDS or ids_sha256(ids) != EXPECTED_SELECTED_IDS_SHA256:
        raise MsgbreCleanupError("selected cleanup ID set differs from the pin")
    return entries, evidence_entries


def input_snapshot(args: argparse.Namespace) -> dict[str, str]:
    return {
        "switch_v13_archive": sha256(args.switch_zip.read_bytes()),
        "base_jp_strdata": sha256(args.base_jp_strdata.read_bytes()),
        "pk_jp_msgbre": sha256(args.stock_pk_jp.read_bytes()),
        "pk_sc_msgbre": sha256(args.stock_pk_sc.read_bytes()),
        "translation_progress": sha256(args.progress.read_bytes()),
    }


def build_once(args: argparse.Namespace, out_root: Path) -> dict[str, Any]:
    out_root = _safe_out_root(out_root)
    before = input_snapshot(args)
    claimed, current_prior_snapshot = load_existing_claims(args.progress)
    prior_snapshot = historical_prior_snapshot(current_prior_snapshot)
    switch_archive, provenance = load_switch_v13(args.switch_zip)
    _, _, base_archive = strict._load_pinned_strdata(
        args.base_jp_strdata, strict.BASE_JP_STRDATA_PIN, "PC base JP strdata"
    )
    _, _, pk_jp = strict._load_pinned_message_table(
        args.stock_pk_jp, strict.PK_JP_MSGBRE_PIN, "PK JP msgbre"
    )
    pk_sc_packed, pk_sc_raw, pk_sc = strict._load_pinned_message_table(
        args.stock_pk_sc, strict.PK_SC_MSGBRE_PIN, "PK SC msgbre"
    )
    entries, evidence_entries = derive_entries(
        switch_archive, base_archive, pk_jp, pk_sc, claimed
    )
    target = strict.reconstruct_target(pk_sc_packed, pk_sc, entries)
    if target != strict.reconstruct_target(pk_sc_packed, pk_sc, entries):
        raise MsgbreCleanupError("in-memory target reconstruction is not deterministic")

    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(pk_sc_packed),
            "packed_sha256": sha256(pk_sc_packed),
            "raw_size": len(pk_sc_raw),
            "raw_sha256": sha256(pk_sc_raw),
            "string_count": pk_sc.string_count,
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    strict.validate_msgbre_overlay_shape(overlay)
    evidence = {
        "schema": "nobu16.kr.switch-msgbre-v13-cjk-cleanup-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "msgbre",
        "scope": {
            "selected_entry_count": len(entries),
            "selected_ids": SELECTED_IDS,
            "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
            "selected_within_stock_visible_target_count": len(entries),
        },
        "source_release": provenance,
        "base_jp_strdata": strict.BASE_JP_STRDATA_PIN,
        "pk_source_files": {
            "JP": strict.PK_JP_MSGBRE_PIN,
            "SC": strict.PK_SC_MSGBRE_PIN,
        },
        "matching_policy": {
            "source_alignment": "complete PK JP hash plus exact in-memory equality",
            "switch_selection": "one convergent Korean result for every duplicate base biography slot",
            "cleanup": "three pinned minimal Hangul rewrites only",
            "target_gate": "pristine PK SC semantic nonblank row",
            "invariants": [
                "printf tokens",
                "unknown percent count",
                "escape controls",
                "other controls",
                "line breaks",
                "private-use code points",
                "leading whitespace",
                "trailing whitespace",
            ],
        },
        "prior_overlay_exclusion": prior_snapshot,
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msgbre-v13-cjk-cleanup-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "source_script_cleanup_complete_not_runtime_reviewed",
        "entry_count": len(entries),
        "entries": [
            {
                "id": entry["id"],
                "status": "translated",
                "translation_origin": "switch_v1.3_text_identical_to_v1.1_plus_pinned_hangul_cleanup",
                "cleanup_kind": CLEANUP_PINS[entry["id"]]["cleanup_kind"],
                "source_script_free": True,
                "selected_within_stock_visible_target": True,
                "pk_sc_invariants_preserved": True,
                "human_review_required": True,
                "runtime_reviewed": False,
            }
            for entry in entries
        ],
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    artifacts = {
        "overlay": write_json(
            out_root / "public" / OVERLAY_NAME,
            overlay,
            f"public/{OVERLAY_NAME}",
        ),
        "alignment_evidence": write_json(
            out_root / "evidence" / EVIDENCE_NAME,
            evidence,
            f"evidence/{EVIDENCE_NAME}",
        ),
        "review_index": write_json(
            out_root / "review" / REVIEW_NAME,
            review,
            f"review/{REVIEW_NAME}",
        ),
    }
    artifact_paths = {
        "overlay": out_root / "public" / OVERLAY_NAME,
        "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME,
        "review_index": out_root / "review" / REVIEW_NAME,
    }
    source_free_scan = {
        name: script_counts(path.read_text(encoding="utf-8"))
        for name, path in artifact_paths.items()
    }
    if any(not source_script_free(path.read_text(encoding="utf-8")) for path in artifact_paths.values()):
        raise MsgbreCleanupError("generated public artifact contains CJK or Kana")
    after = input_snapshot(args)
    _, current_prior_after = load_existing_claims(args.progress)
    if before != after or current_prior_snapshot != current_prior_after:
        raise MsgbreCleanupError("an input or prior overlay changed during generation")
    validation = {
        "schema": "nobu16.kr.switch-msgbre-v13-cjk-cleanup-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {
            "selected_entry_count": len(entries),
            "expected_selected_entry_count": len(SELECTED_IDS),
            "selected_ids": SELECTED_IDS,
            "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        },
        "source_release": provenance,
        "prior_overlay_exclusion": prior_snapshot,
        "target_reconstruction": target,
        "source_free_scan": source_free_scan,
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "target_a_b_equal": True,
        },
        "safety": {
            "switch_archive_included": False,
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "commit_or_push_performed": False,
        },
        "input_snapshot_before": before,
        "input_snapshot_after": after,
        "artifacts": artifacts,
    }
    validation["source_free_scan"]["generation_validation"] = script_counts(
        json_bytes(validation).decode("utf-8")
    )
    if validation["source_free_scan"]["generation_validation"] != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise MsgbreCleanupError("generation validation contains source script")
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation, VALIDATION_NAME
    )
    files = {
        name: path.read_bytes()
        for name, path in {
            **artifact_paths,
            "generation_validation": out_root / VALIDATION_NAME,
        }.items()
    }
    return {
        "entry_count": len(entries),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "target": target,
        "artifacts": artifacts,
        "files": files,
    }


def build_reproducibly(args: argparse.Namespace) -> dict[str, Any]:
    out_root = _safe_out_root(args.out_root)
    before = input_snapshot(args)
    with tempfile.TemporaryDirectory(
        prefix="nobu16-msgbre-cleanup-a-", dir=REPO_ROOT / "tmp"
    ) as first_dir, tempfile.TemporaryDirectory(
        prefix="nobu16-msgbre-cleanup-b-", dir=REPO_ROOT / "tmp"
    ) as second_dir:
        first = build_once(args, Path(first_dir))
        second = build_once(args, Path(second_dir))
        if first["files"] != second["files"] or first["target"] != second["target"]:
            raise MsgbreCleanupError("isolated cleanup builds are not byte-identical")
    final = build_once(args, out_root)
    if final["files"] != first["files"] or final["target"] != first["target"]:
        raise MsgbreCleanupError("final cleanup build differs from isolated builds")
    if input_snapshot(args) != before:
        raise MsgbreCleanupError("input resource changed across reproducible build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--switch-zip", type=Path, default=REPO_ROOT / SWITCH_ARCHIVE_RELATIVE
    )
    parser.add_argument(
        "--base-jp-strdata", type=Path, default=GAME_ROOT / "MSG" / "JP" / "strdata.bin"
    )
    parser.add_argument(
        "--stock-pk-jp", type=Path, default=GAME_ROOT / "MSG_PK" / "JP" / "msgbre.bin"
    )
    parser.add_argument(
        "--stock-pk-sc", type=Path, default=strict.LOCAL_STOCK_SC_BACKUP
    )
    parser.add_argument(
        "--progress",
        type=Path,
        default=REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json",
    )
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    try:
        result = build_reproducibly(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"entries={result['entry_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['packed_sha256']}")
    for name, artifact in sorted(result["artifacts"].items()):
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
