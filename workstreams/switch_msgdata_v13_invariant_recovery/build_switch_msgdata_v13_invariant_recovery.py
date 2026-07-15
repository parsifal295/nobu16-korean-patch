#!/usr/bin/env python3
"""Recover safe Switch-derived PK msgdata rows rejected by strict formatting gates.

The Switch v1.3 ``strdata.bin`` text member is byte-identical to v1.1.  The
first strict transfer intentionally rejected rows containing source script or
whose formatting contract differed from the stock PC PK/SC row.  This builder
revisits only that 148-row residual pool, excludes the stock-blank row and two
semantically incompatible contracts, and emits a source-free 145-row overlay.

No complete game resource is written.  A rebuilt PK/SC target exists only in
memory long enough to prove deterministic table and wrapper reconstruction.
"""

from __future__ import annotations

import argparse
from collections import Counter
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
STRDATA_ROOT = REPO_ROOT / "workstreams" / "strdata"
UPSTREAM_ROOT = REPO_ROOT / "workstreams" / "switch_msgdata_v11"
sys.path[:0] = [str(TOOLS_ROOT), str(STRDATA_ROOT), str(UPSTREAM_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgdata_v11 as upstream  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from strdata_format import EXPECTED_SLOT_COUNTS, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


BATCH_ID = "switch-v13-pk-msgdata-invariant-recovery-145.v1"
OVERLAY_NAME = "msgdata_ko_switch_v13_invariant_recovery_145.v1.json"
EVIDENCE_NAME = "switch_v13_msgdata_invariant_recovery_alignment.v1.json"
REVIEW_NAME = "switch_v13_msgdata_invariant_recovery_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
RESOURCE = upstream.RESOURCE
STRING_COUNT = upstream.STRING_COUNT
SELF_OVERLAY_LOGICAL_PATH = (
    f"workstreams/switch_msgdata_v13_invariant_recovery/public/{OVERLAY_NAME}"
)
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")

SWITCH_ARCHIVE_RELATIVE = Path(
    "tmp/third_party_switch_v13/NobunagaShinsei_KoreanPatch_v1.3.zip"
)
SWITCH_MEMBER = upstream.SWITCH_ARCHIVE_MEMBER
STOCK_SC_RELATIVE = Path(
    "KR_PATCH_BACKUP/file_only_transaction/pk-full-messages-seoulhangang-v1/"
    "originals/MSG_PK/SC/msgdata.bin"
)

SWITCH_V13 = {
    "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
    "release_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.3",
    "tag": "v1.3",
    "author_attribution": "GitHub user snake7594",
    "archive_relative_path": SWITCH_ARCHIVE_RELATIVE.as_posix(),
    "archive_size": 72_977_145,
    "archive_sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
    "member_path": SWITCH_MEMBER,
    "member_size": 404_189,
    "member_compressed_size": 294_162,
    "member_crc32": "B17A2EBB",
    "member_packed_sha256": "5F065B9DBDAE4DC75E2D7186A76C0AC988FB504F018F820C204262BF07D5061B",
    "member_raw_size": 953_512,
    "member_raw_sha256": "245538466576E3880B3C53C0CB4929685096DF394C27CCB93B2C893615A46ADE",
}

V11_TEXT_IDENTITY = {
    "release_tag": "v1.1",
    "member_packed_sha256": upstream.SWITCH_MEMBER_PIN["sha256"],
    "member_raw_sha256": upstream.SWITCH_MEMBER_PIN["raw_sha256"],
    "member_text_byte_identical": True,
}

OWNER_OVERLAYS = (
    {
        "path": "data/public/msgdata_ko_officer_names_0000_2399.v0.1.json",
        "sha256": "D787EB64BFFC54D1ACA2F23BC9407991FEB4FCF76D102E1EE017EEF416FE4FA3",
        "entry_count": 3_831,
        "ids_sha256": "ADBE4F9A948FD4440D5D997D0D8ADD2088696F1A30147932D9A9948754AD7D6E",
    },
    {
        "path": "workstreams/castle_names/public/castle_names_ko_9151_9542.v0.2.json",
        "sha256": "0CEFDE11008F4503198903E1FA25ACDDB120F6B407405EF9ACE2B01B39577E5E",
        "entry_count": 392,
        "ids_sha256": "474F7B7EA14CA96FF70EBCD63D1FF2CBC0E3CE5BC89ECDD4B9EB8D25E67CE850",
    },
    {
        "path": "workstreams/province_names/public/province_names_ko_13975_14046.v0.2.json",
        "sha256": "2EF65EBDEF21521857477EA180E7FBC7AB92F1626FC69D06BD6262E97BFDBDF5",
        "entry_count": 72,
        "ids_sha256": "92FC19CAC52F04FD5D0DEC3F98F0C929B232DDD41F1D9C2F94059260E9C57A8A",
    },
    {
        "path": "workstreams/msgdata/public/msgdata_ko_faction_labels_3032_3221.v0.1.json",
        "sha256": "A277CC298262A46683CDB81273487BB5EF4AAD25FE361C1977251B52A1BF7244",
        "entry_count": 190,
        "ids_sha256": "BFE9A2B0651D15EB08DA4DD5E1B0C31FDC6BB7E670B1ACF8ED551F7F6C5A44FD",
    },
    {
        "path": "workstreams/msgdata/public/msgdata_ko_name_components_3222_3315.v0.1.json",
        "sha256": "9B887DE854B6ADE847036F1D757925AFFA9BD84FD041ADAB0CE23DA0D3DAC09A",
        "entry_count": 94,
        "ids_sha256": "17FE6A25C8D2A4EBE5FE311C3154576D4811F983014F43CF7FB2034557524F54",
    },
    {
        "path": "workstreams/switch_msgdata_v11/public/msgdata_ko_switch_v11_strict_transfer.v0.1.json",
        "sha256": "1C748373DFF712E52BA11459E032E3611ED5151EF18633E592452D3A2A78392E",
        "entry_count": 16_176,
        "ids_sha256": "B8AC5996A1D9A6231E8A22AC130C077E0F11830F181FF66FA5FB6929C6FB34BB",
    },
)

EXPECTED_OWNER_AUTHORED_COUNT = 20_755
EXPECTED_OWNER_UNION_COUNT = 20_683
EXPECTED_OWNER_DUPLICATE_COUNT = 72
EXPECTED_OWNER_UNION_IDS_SHA256 = "5B08D81DB398BEEA5742197192C86C7E2DF3B0323506B63B30AD7197BEE4F1A0"

EXPECTED_RESIDUAL_COUNT = 148
EXPECTED_RESIDUAL_IDS_SHA256 = "79B18002ED18F45A87A778FCE26BF4874713120EF10C7DEAD8412E7643735BBE"
EXPECTED_VISIBLE_COUNT = 147
EXPECTED_VISIBLE_IDS_SHA256 = "1F61BF27C69FAC3D1B21EB70F3B27E193407C08705C720CB1430B33FD8FA82DA"
EXPECTED_SELECTED_COUNT = 145
EXPECTED_SELECTED_IDS_SHA256 = "8BBA6F1E8AC5867BFB0361D4A58D3DAF023BAB559CFEE5044520810A39E79BD0"
EXPECTED_OVERLAY_SHA256 = "0372E73879BD2E3C927F69375079AA6EE507E2FF2824E9AE8E8525E109CCC982"
EXPECTED_EXCLUDED_IDS = (18_048, 22_594, 25_546)
EXPECTED_EXCLUDED_IDS_SHA256 = "2FD5C2EC8B7EA2F4DB50FAAA179B5B9033688B3C139163D3F5702B936865A00B"

EXPECTED_RESIDUAL_CATEGORY_COUNTS = {
    "esc+printf": 1,
    "leading_whitespace+line_breaks": 2,
    "line_breaks": 41,
    "line_breaks+unknown_percent_count": 1,
    "printf": 7,
    "pua": 85,
    "source_script": 8,
    "unknown_percent_count": 3,
}

CUSTOM_BRACKET_TOKEN_RE = re.compile(r"\[[A-Za-z0-9_]+\]")
CJK_UNIFIED_RE = upstream.CJK_UNIFIED_RE
KANA_RE = upstream.KANA_RE
HANGUL_RE = upstream.HANGUL_RE

PUA_IDS = frozenset(range(17_896, 17_981))
SOURCE_SCRIPT_IDS = frozenset((22_617, 24_378, 24_379, 24_380, 24_381, 24_382, 24_383, 24_384))
PERCENT_IDS = frozenset((22_526, 22_536, 22_546, 22_555))
PRINTF_FULLWIDTH_PERCENT_IDS = frozenset((23_990, 23_992, 23_995))
UI_EFFECT_LINE_IDS = frozenset((20_936, 20_953, 20_957, 21_036, 21_053, 21_057))
FIVE_TO_FOUR_LINE_IDS = frozenset((15_136, 15_139, 15_142, 15_143, 15_144))
UNSAFE_CONTRACT_IDS = frozenset((22_594, 25_546))


class RecoveryError(ValueError):
    """Raised when a pinned input, residual pool, or repair contract changes."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any, logical_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": logical_path, "size": len(blob), "sha256": sha256(blob)}


def source_script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": len(CJK_UNIFIED_RE.findall(text)),
        "kana_count": len(KANA_RE.findall(text)),
    }


def has_meaningful_hangul(text: str) -> bool:
    return bool(HANGUL_RE.search(text)) and common.has_semantic_text(text)


def category_key(source_script: dict[str, int], problems: list[str]) -> str:
    keys = {problem.split(":", 1)[0] for problem in problems}
    if sum(source_script.values()):
        keys.add("source_script")
    return "+".join(sorted(keys))


def load_switch_v13(archive_path: Path) -> tuple[bytes, bytes, Any, dict[str, Any]]:
    archive_blob = archive_path.read_bytes()
    if len(archive_blob) != SWITCH_V13["archive_size"] or sha256(archive_blob) != SWITCH_V13["archive_sha256"]:
        raise RecoveryError("Switch v1.3 archive differs from its size/SHA-256 pin")
    with zipfile.ZipFile(archive_path) as archive:
        info = archive.getinfo(SWITCH_MEMBER)
        if info.flag_bits & 0x1:
            raise RecoveryError("Switch v1.3 strdata member is encrypted")
        if info.file_size != SWITCH_V13["member_size"]:
            raise RecoveryError("Switch v1.3 strdata member size changed")
        if info.compress_size != SWITCH_V13["member_compressed_size"]:
            raise RecoveryError("Switch v1.3 strdata compressed size changed")
        if f"{info.CRC:08X}" != SWITCH_V13["member_crc32"]:
            raise RecoveryError("Switch v1.3 strdata CRC32 changed")
        packed = archive.read(info)
    if sha256(packed) != SWITCH_V13["member_packed_sha256"]:
        raise RecoveryError("Switch v1.3 strdata packed SHA-256 changed")
    _, raw = decompress_wrapper(packed)
    if len(raw) != SWITCH_V13["member_raw_size"] or sha256(raw) != SWITCH_V13["member_raw_sha256"]:
        raise RecoveryError("Switch v1.3 strdata raw payload changed")
    if sha256(packed) != V11_TEXT_IDENTITY["member_packed_sha256"]:
        raise RecoveryError("Switch v1.3 strdata is no longer byte-identical to v1.1")
    if sha256(raw) != V11_TEXT_IDENTITY["member_raw_sha256"]:
        raise RecoveryError("Switch v1.3 raw strdata is no longer byte-identical to v1.1")
    parsed = parse_raw_strdata(raw)
    if tuple(block.slot_count for block in parsed.blocks) != EXPECTED_SLOT_COUNTS:
        raise RecoveryError("Switch v1.3 strdata block layout changed")
    if rebuild_raw_strdata(parsed) != raw:
        raise RecoveryError("Switch v1.3 strdata parse/rebuild is not byte-identical")
    provenance = {
        **SWITCH_V13,
        "v1_1_text_identity": V11_TEXT_IDENTITY,
        "v1_3_text_member_equals_v1_1": True,
        "block_slot_counts": list(EXPECTED_SLOT_COUNTS),
        "parse_rebuild_byte_identical": True,
    }
    return packed, raw, parsed, provenance


def load_owner_catalog(repo_root: Path) -> dict[str, Any]:
    ids_union: set[int] = set()
    authored_count = 0
    rows: list[dict[str, Any]] = []
    for descriptor in OWNER_OVERLAYS:
        path = repo_root / descriptor["path"]
        overlay, blob = common.load_json_strict(path)
        if sha256(blob) != descriptor["sha256"]:
            raise RecoveryError(f"owner overlay SHA-256 changed: {descriptor['path']}")
        resource = overlay.get("resource")
        target = overlay.get("target")
        if resource is None and isinstance(target, dict):
            resource = target.get("resource")
        if resource != RESOURCE:
            raise RecoveryError(f"owner overlay targets another resource: {descriptor['path']}")
        entries = overlay.get("entries")
        if not isinstance(entries, list):
            raise RecoveryError(f"owner overlay has no entries: {descriptor['path']}")
        ids = [entry.get("id") for entry in entries]
        if any(type(entry_id) is not int for entry_id in ids):
            raise RecoveryError(f"owner overlay has a non-integer ID: {descriptor['path']}")
        sorted_ids = sorted(int(entry_id) for entry_id in ids)
        if len(sorted_ids) != descriptor["entry_count"] or len(set(sorted_ids)) != len(sorted_ids):
            raise RecoveryError(f"owner overlay count/uniqueness changed: {descriptor['path']}")
        if hash_json(sorted_ids) != descriptor["ids_sha256"]:
            raise RecoveryError(f"owner overlay ID set changed: {descriptor['path']}")
        authored_count += len(sorted_ids)
        ids_union.update(sorted_ids)
        rows.append(
            {
                "path": descriptor["path"],
                "sha256": sha256(blob),
                "entry_count": len(sorted_ids),
                "ids_sha256": hash_json(sorted_ids),
            }
        )
    snapshot = {
        "overlays": rows,
        "authored_entry_count": authored_count,
        "effective_unique_id_count": len(ids_union),
        "cross_overlay_duplicate_id_count": authored_count - len(ids_union),
        "effective_ids_sha256": hash_json(sorted(ids_union)),
    }
    if authored_count != EXPECTED_OWNER_AUTHORED_COUNT:
        raise RecoveryError("owner authored entry count changed")
    if len(ids_union) != EXPECTED_OWNER_UNION_COUNT:
        raise RecoveryError("owner effective union count changed")
    if authored_count - len(ids_union) != EXPECTED_OWNER_DUPLICATE_COUNT:
        raise RecoveryError("owner duplicate count changed")
    if snapshot["effective_ids_sha256"] != EXPECTED_OWNER_UNION_IDS_SHA256:
        raise RecoveryError("owner effective ID set changed")
    return {"ids": ids_union, "snapshot": snapshot}


def validate_progress_catalog(
    progress_path: Path,
    owner_catalog: dict[str, Any],
) -> dict[str, Any]:
    """Validate pinned owners plus later disjoint registrations.

    The generated overlay is intentionally absent from ``OWNER_OVERLAYS``.  If
    integration later registers it in the global progress catalog, this check
    validates that registration and removes it before comparing the prior-owner
    set.  Therefore a post-integration rebuild derives the same 148-row pool
    and the same 145-row overlay instead of treating its own IDs as claimed.
    Source-free successor batches are likewise validated and excluded from this
    historical derivation, so appending new translations cannot invalidate it.
    """

    progress, _ = common.load_json_strict(progress_path)
    resources = progress.get("resources")
    if not isinstance(resources, list):
        raise RecoveryError("translation progress has no resources array")
    matches = [row for row in resources if row.get("path") == RESOURCE]
    if len(matches) != 1:
        raise RecoveryError("translation progress must contain exactly one PK msgdata resource")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(pattern, str) for pattern in patterns):
        raise RecoveryError("PK msgdata progress overlay_globs are invalid")

    owner_paths = {str(descriptor["path"]) for descriptor in OWNER_OVERLAYS}
    prior_paths: list[str] = []
    self_rows: list[dict[str, Any]] = []
    successor_rows: list[dict[str, Any]] = []
    successor_ids: set[int] = set()

    self_overlay, self_blob = common.load_json_strict(REPO_ROOT / SELF_OVERLAY_LOGICAL_PATH)
    self_entries = self_overlay.get("entries")
    if self_overlay.get("resource") != RESOURCE or not isinstance(self_entries, list):
        raise RecoveryError("checked self overlay shape changed")
    self_ids = [entry.get("id") for entry in self_entries]
    if any(type(entry_id) is not int for entry_id in self_ids):
        raise RecoveryError("checked self overlay has a non-integer ID")
    typed_self_ids = [int(entry_id) for entry_id in self_ids]
    if (
        self_overlay.get("overlay_id") != BATCH_ID
        or sha256(self_blob) != EXPECTED_OVERLAY_SHA256
        or len(typed_self_ids) != EXPECTED_SELECTED_COUNT
        or typed_self_ids != sorted(typed_self_ids)
        or len(typed_self_ids) != len(set(typed_self_ids))
        or hash_json(typed_self_ids) != EXPECTED_SELECTED_IDS_SHA256
    ):
        raise RecoveryError("checked self overlay contract changed")
    selected_ids = set(typed_self_ids)

    for pattern in patterns:
        resolved = sorted(REPO_ROOT.glob(pattern))
        if len(resolved) != 1:
            raise RecoveryError(f"progress overlay glob {pattern!r} resolved to {len(resolved)} files")
        path = resolved[0]
        logical_path = path.relative_to(REPO_ROOT).as_posix()
        if logical_path == SELF_OVERLAY_LOGICAL_PATH:
            if pattern != SELF_OVERLAY_LOGICAL_PATH:
                raise RecoveryError("self overlay must be registered by its exact logical path")
            overlay, blob = common.load_json_strict(path)
            ids = [entry.get("id") for entry in overlay.get("entries", [])]
            if overlay.get("overlay_id") != BATCH_ID:
                raise RecoveryError("self progress registration has an unexpected overlay_id")
            if sha256(blob) != EXPECTED_OVERLAY_SHA256:
                raise RecoveryError("self progress registration overlay SHA-256 changed")
            if len(ids) != EXPECTED_SELECTED_COUNT or hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
                raise RecoveryError("self progress registration ID set changed")
            self_rows.append(
                {
                    "path": logical_path,
                    "entry_count": len(ids),
                    "ids_sha256": hash_json(ids),
                    "excluded_from_prior_claims": True,
                }
            )
            continue
        if logical_path in owner_paths:
            prior_paths.append(logical_path)
            continue

        if pattern != logical_path:
            raise RecoveryError("successor overlays must use exact logical paths")
        overlay, blob = common.load_json_strict(path)
        entries = overlay.get("entries")
        if overlay.get("resource") != RESOURCE or not isinstance(entries, list):
            raise RecoveryError(f"successor overlay shape is invalid: {logical_path}")
        ids = [entry.get("id") for entry in entries]
        if any(type(entry_id) is not int for entry_id in ids):
            raise RecoveryError(f"successor overlay has a non-integer ID: {logical_path}")
        typed_ids = [int(entry_id) for entry_id in ids]
        if typed_ids != sorted(typed_ids) or len(typed_ids) != len(set(typed_ids)):
            raise RecoveryError(f"successor overlay IDs are not sorted and unique: {logical_path}")
        policy = overlay.get("distribution_policy")
        if (
            not isinstance(policy, dict)
            or policy.get("contains_commercial_source_text") is not False
            or policy.get("contains_complete_game_resource") is not False
        ):
            raise RecoveryError(f"successor overlay is not source-free: {logical_path}")
        overlap = selected_ids & set(typed_ids)
        if overlap:
            raise RecoveryError(
                f"successor overlay overlaps this batch at {min(overlap)}: {logical_path}"
            )
        overlap = owner_catalog["ids"] & set(typed_ids)
        if overlap:
            raise RecoveryError(
                f"successor overlay overlaps a pinned owner at {min(overlap)}: {logical_path}"
            )
        overlap = successor_ids & set(typed_ids)
        if overlap:
            raise RecoveryError(
                f"successor overlays overlap at {min(overlap)}: {logical_path}"
            )
        successor_ids.update(typed_ids)
        successor_rows.append(
            {
                "path": logical_path,
                "sha256": sha256(blob),
                "entry_count": len(typed_ids),
                "ids_sha256": hash_json(typed_ids),
                "source_free": True,
                "excluded_from_prior_claims": True,
            }
        )

    if len(self_rows) > 1:
        raise RecoveryError("self overlay is registered more than once")
    if set(prior_paths) != owner_paths or len(prior_paths) != len(owner_paths):
        raise RecoveryError("progress prior-owner paths differ from the pinned owner catalog")
    if owner_catalog["snapshot"]["effective_unique_id_count"] != EXPECTED_OWNER_UNION_COUNT:
        raise RecoveryError("progress prior-owner union changed")
    if owner_catalog["snapshot"]["effective_ids_sha256"] != EXPECTED_OWNER_UNION_IDS_SHA256:
        raise RecoveryError("progress prior-owner ID hash changed")
    return {
        "self_registered": bool(self_rows),
        "self_registration_count": len(self_rows),
        "self_registration": self_rows[0] if self_rows else None,
        "self_excluded_from_prior_claims": True,
        "prior_owner_path_count": len(prior_paths),
        "prior_owner_effective_id_count": EXPECTED_OWNER_UNION_COUNT,
        "prior_owner_effective_ids_sha256": EXPECTED_OWNER_UNION_IDS_SHA256,
        "successor_overlays": successor_rows,
        "successor_overlay_count": len(successor_rows),
        "successor_effective_id_count": len(successor_ids),
        "successors_excluded_from_prior_claims": True,
    }


def derive_residual_pool(
    pk_jp: Any,
    pk_sc: Any,
    reverse_index: dict[str, dict[str, Any]],
    owner_ids: set[int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    histogram: Counter[str] = Counter()
    for entry_id, (jp, sc) in enumerate(zip(pk_jp.texts, pk_sc.texts, strict=True)):
        jp_hash = common.text_hash(jp)
        record = reverse_index.get(jp_hash)
        if record is None or record["jp"] != jp or record["candidate_ko"] is None:
            continue
        if entry_id in owner_ids:
            continue
        ko = str(record["candidate_ko"])
        scripts = source_script_counts(ko)
        problems = common.invariant_mismatches(sc, ko)
        if not sum(scripts.values()) and not problems:
            continue
        category = category_key(scripts, problems)
        histogram[category] += 1
        rows.append(
            {
                "id": entry_id,
                "jp": jp,
                "sc": sc,
                "ko": ko,
                "jp_hash": jp_hash,
                "record": record,
                "source_script_before": scripts,
                "invariant_problems_before": problems,
                "category": category,
                "stock_visible_target": common.has_semantic_text(sc),
            }
        )
    ids = [row["id"] for row in rows]
    visible_ids = [row["id"] for row in rows if row["stock_visible_target"]]
    if len(ids) != EXPECTED_RESIDUAL_COUNT or hash_json(ids) != EXPECTED_RESIDUAL_IDS_SHA256:
        raise RecoveryError("148-row residual pool changed")
    if len(visible_ids) != EXPECTED_VISIBLE_COUNT or hash_json(visible_ids) != EXPECTED_VISIBLE_IDS_SHA256:
        raise RecoveryError("147-row stock-visible residual pool changed")
    if dict(sorted(histogram.items())) != EXPECTED_RESIDUAL_CATEGORY_COUNTS:
        raise RecoveryError("residual category histogram changed")
    return rows, {
        "residual_count": len(ids),
        "residual_ids_sha256": hash_json(ids),
        "stock_visible_count": len(visible_ids),
        "stock_visible_ids_sha256": hash_json(visible_ids),
        "stock_blank_count": len(ids) - len(visible_ids),
        "stock_blank_ids": sorted(set(ids) - set(visible_ids)),
        "category_counts": dict(sorted(histogram.items())),
    }


def _replace_exactly_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RecoveryError(f"{label}: expected exactly one {old!r}")
    return text.replace(old, new, 1)


def repair_korean(row: dict[str, Any], pool: dict[int, dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    entry_id = int(row["id"])
    sc = str(row["sc"])
    ko = str(row["ko"])
    operations: list[str] = []
    adjacent_fragments: list[int] = []

    if entry_id in PUA_IDS:
        source_pua = [character for character in sc if 0xE000 <= ord(character) <= 0xF8FF]
        if source_pua != ["\uE003"]:
            raise RecoveryError(f"id {entry_id}: stock PUA contract changed")
        ko = _replace_exactly_once(ko, "\u00B7", source_pua[0], f"id {entry_id}")
        operations.append("restore_stock_pua_separator")

    if entry_id in SOURCE_SCRIPT_IDS:
        if "\u30FB" not in ko:
            raise RecoveryError(f"id {entry_id}: expected Japanese middle-dot source script")
        ko = ko.replace("\u30FB", "\u00B7")
        operations.append("normalize_japanese_middle_dot_to_korean_safe_separator")

    if entry_id in PERCENT_IDS:
        ko = _replace_exactly_once(ko, "%+d%", "%+d％", f"id {entry_id}")
        operations.append("restore_fullwidth_percent_literal")

    if entry_id == 22_537:
        ko = _replace_exactly_once(ko, "%+d", "+%d", f"id {entry_id}")
        operations.append("restore_literal_plus_and_printf_d")
    elif entry_id == 23_988:
        ko = "특수 영향력+%d " + ko
        operations.append("restore_omitted_first_printf_clause")
    elif entry_id in PRINTF_FULLWIDTH_PERCENT_IDS:
        ko = _replace_exactly_once(ko, "%%", "％", f"id {entry_id}")
        operations.append("restore_fullwidth_percent_without_printf_token")
    elif entry_id == 25_293:
        if "%" in ko:
            raise RecoveryError("id 25293: Switch value unexpectedly already contains printf")
        ko += "+%d"
        operations.append("restore_literal_plus_and_printf_d")

    source_breaks = sc.count("\n")
    ko_breaks = ko.count("\n")
    if entry_id in FIVE_TO_FOUR_LINE_IDS:
        head, separator, tail = ko.rpartition("\n")
        if not separator:
            raise RecoveryError(f"id {entry_id}: expected final line break")
        ko = head + " " + tail
        operations.append("remove_final_switch_wrap")
    elif entry_id == 18_047:
        fragment = str(pool[18_048]["ko"])
        ko = ko + "\n" + fragment
        adjacent_fragments.append(18_048)
        operations.append("join_adjacent_switch_semantic_fragment")
    elif entry_id == 18_051:
        ko = _replace_exactly_once(ko, "남성을 ", "남성을\n", f"id {entry_id}")
        operations.append("restore_stock_line_count_at_clause_boundary")
    elif entry_id == 18_062:
        ko += "\n본보기로 따끔하게 벌해야 한다."
        adjacent_fragments.append(18_063)
        operations.append("restore_clause_from_adjacent_switch_fragment")
    elif entry_id == 18_063:
        if "\n" not in ko:
            raise RecoveryError("id 18063: adjacent Switch clause boundary changed")
        ko = "그렇지 않으면 " + ko.split("\n", 1)[1]
        adjacent_fragments.append(18_062)
        operations.append("retain_target_clause_and_remove_adjacent_prefix")
    elif entry_id == 18_068:
        ko = "설욕을 기하는 이에야스는\n" + ko
        adjacent_fragments.append(18_067)
        operations.append("restore_clause_from_adjacent_switch_fragment")
    elif entry_id in (18_089, 18_102):
        ko = "\n" + ko
        operations.append("restore_stock_leading_line_break")
    elif entry_id == 18_091:
        ko = "…\n" + ko
        operations.append("restore_leading_ellipsis_clause_break")
    elif entry_id == 18_093:
        ko = _replace_exactly_once(ko, "… ", "…\n", f"id {entry_id}")
        operations.append("restore_stock_line_count_at_clause_boundary")
    elif entry_id == 19_660:
        ko = _replace_exactly_once(ko, "무장의 ", "무장의\n", f"id {entry_id}")
        operations.append("restore_stock_line_count_at_phrase_boundary")
    elif entry_id in UI_EFFECT_LINE_IDS:
        ko = _replace_exactly_once(ko, "\n", " / ", f"id {entry_id}")
        operations.append("restore_single_line_effect_separator")
    elif source_breaks == 0 and ko_breaks > 0:
        ko = ko.replace("\n", " ")
        operations.append("remove_switch_soft_wraps")

    problems_after = common.invariant_mismatches(sc, ko)
    if problems_after:
        raise RecoveryError(f"id {entry_id}: repair did not preserve SC invariants: {problems_after}")
    if CUSTOM_BRACKET_TOKEN_RE.findall(sc) != CUSTOM_BRACKET_TOKEN_RE.findall(ko):
        raise RecoveryError(f"id {entry_id}: custom bracket placeholders differ")
    if source_script_counts(ko) != {"cjk_unified_count": 0, "kana_count": 0}:
        raise RecoveryError(f"id {entry_id}: repaired text retains CJK unified or kana")
    if not has_meaningful_hangul(ko):
        raise RecoveryError(f"id {entry_id}: repaired text lacks meaningful Hangul")
    if not operations:
        raise RecoveryError(f"id {entry_id}: residual row had no explicit repair operation")
    return ko, {
        "operations": operations,
        "adjacent_switch_semantic_fragment_ids": adjacent_fragments,
        "pk_sc_invariants_preserved": True,
        "custom_bracket_tokens_preserved": True,
        "source_script_free": True,
    }


def select_entries(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    pool = {int(row["id"]): row for row in rows}
    entries: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for row in rows:
        entry_id = int(row["id"])
        if not row["stock_visible_target"]:
            exclusions.append(
                {
                    "id": entry_id,
                    "reason": "stock_sc_blank_not_translation_target",
                    "eligible_for_progress": False,
                    "automatic_repair_safe": False,
                }
            )
            continue
        if entry_id in UNSAFE_CONTRACT_IDS:
            reason = (
                "switch_semantics_conflict_with_stock_sc_esc_printf_contract"
                if entry_id == 22_594
                else "stock_sc_dummy_has_no_printf_contract"
            )
            exclusions.append(
                {
                    "id": entry_id,
                    "reason": reason,
                    "eligible_for_progress": True,
                    "automatic_repair_safe": False,
                }
            )
            continue
        ko, repair = repair_korean(row, pool)
        sc = str(row["sc"])
        record = row["record"]
        entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(sc),
                "ko": ko,
            }
        )
        evidence.append(
            {
                "id": entry_id,
                "pk_jp_utf16le_sha256": row["jp_hash"],
                "pk_sc_utf16le_sha256": common.text_hash(sc),
                "switch_ko_before_utf16le_sha256": common.text_hash(str(row["ko"])),
                "repaired_ko_utf16le_sha256": common.text_hash(ko),
                "base_jp_coordinate_count": int(record["coordinate_count"]),
                "base_jp_coordinate_ids_sha256": record["coordinate_ids_sha256"],
                "residual_category": row["category"],
                "stock_visible_target": True,
                "exact_japanese_match": True,
                "switch_korean_hash_converged": True,
                **repair,
            }
        )
    ids = [entry["id"] for entry in entries]
    excluded_ids = [entry["id"] for entry in exclusions]
    if len(ids) != EXPECTED_SELECTED_COUNT or hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
        raise RecoveryError("safe selected ID set changed")
    if excluded_ids != list(EXPECTED_EXCLUDED_IDS) or hash_json(excluded_ids) != EXPECTED_EXCLUDED_IDS_SHA256:
        raise RecoveryError("honest exclusion ID set changed")
    return entries, evidence, exclusions


def validate_overlay(overlay: dict[str, Any], stock_table: Any, owner_ids: set[int]) -> None:
    resource, stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE or stock["string_count"] != STRING_COUNT:
        raise RecoveryError("overlay targets the wrong resource or string count")
    selected = [entry["id"] for entry in entries]
    if set(selected) & owner_ids:
        raise RecoveryError("recovery overlay overlaps an existing msgdata owner overlay")
    for entry in entries:
        entry_id = int(entry["id"])
        source = stock_table.texts[entry_id]
        replacement = str(entry["ko"])
        if not common.has_semantic_text(source):
            raise RecoveryError(f"id {entry_id}: selected row is not stock-visible")
        if common.text_hash(source) != entry["source_sc_utf16le_sha256"]:
            raise RecoveryError(f"id {entry_id}: source SC hash changed")
        if common.invariant_mismatches(source, replacement):
            raise RecoveryError(f"id {entry_id}: final overlay violates SC invariants")
        if CUSTOM_BRACKET_TOKEN_RE.findall(source) != CUSTOM_BRACKET_TOKEN_RE.findall(replacement):
            raise RecoveryError(f"id {entry_id}: final bracket placeholders differ")


def input_snapshot(args: argparse.Namespace) -> dict[str, str]:
    values = {
        "switch_v13_archive": sha256(args.switch_zip.read_bytes()),
        "base_jp_strdata": sha256(args.base_jp_strdata.read_bytes()),
        "pk_jp_msgdata": sha256(args.stock_pk_jp.read_bytes()),
        "pristine_pk_sc_msgdata": sha256(args.stock_pk_sc.read_bytes()),
    }
    for index, descriptor in enumerate(OWNER_OVERLAYS):
        values[f"owner_overlay_{index}"] = sha256((REPO_ROOT / descriptor["path"]).read_bytes())
    return values


def build(args: argparse.Namespace) -> dict[str, Any]:
    input_before = input_snapshot(args)
    owners = load_owner_catalog(REPO_ROOT)
    progress_state = validate_progress_catalog(args.progress, owners)
    if not progress_state["self_excluded_from_prior_claims"]:
        raise RecoveryError("self overlay was not excluded from prior claims")
    _, _, switch_archive, provenance = load_switch_v13(args.switch_zip)
    _, _, base_archive = upstream._load_base_jp_strdata(args.base_jp_strdata)
    _, _, pk_jp_table = upstream._load_pk_msgdata(
        args.stock_pk_jp, upstream.PK_JP_MSGDATA_PIN, "PK JP msgdata"
    )
    sc_packed, _, pk_sc_table = upstream._load_pk_msgdata(
        args.stock_pk_sc, upstream.PK_SC_MSGDATA_PIN, "pristine PK SC msgdata"
    )
    reverse_index, reverse_summary = upstream.build_jp_hash_reverse_index(base_archive, switch_archive)
    rows, pool_summary = derive_residual_pool(
        pk_jp_table, pk_sc_table, reverse_index, owners["ids"]
    )
    entries, evidence_entries, exclusions = select_entries(rows)

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
            "size": upstream.PK_SC_MSGDATA_PIN["size"],
            "packed_sha256": upstream.PK_SC_MSGDATA_PIN["sha256"],
            "raw_size": upstream.PK_SC_MSGDATA_PIN["raw_size"],
            "raw_sha256": upstream.PK_SC_MSGDATA_PIN["raw_sha256"],
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    validate_overlay(overlay, pk_sc_table, owners["ids"])
    target_a = upstream.reconstruct_sc_target(sc_packed, pk_sc_table, entries)
    target_b = upstream.reconstruct_sc_target(sc_packed, pk_sc_table, entries)
    if target_a != target_b:
        raise RecoveryError("in-memory target reconstruction is not deterministic")

    evidence = {
        "schema": "nobu16.kr.switch-msgdata-v13-invariant-recovery-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "source_release": provenance,
        "owner_catalog": owners["snapshot"],
        "progress_integration_policy": {
            "pre_integration_unregistered_allowed": True,
            "post_integration_exact_self_registration_allowed": True,
            "self_overlay_logical_path": SELF_OVERLAY_LOGICAL_PATH,
            "self_overlay_excluded_from_prior_claims": True,
        },
        "reverse_index": reverse_summary,
        "residual_pool": pool_summary,
        "selected_entry_count": len(entries),
        "selected_ids_sha256": hash_json([entry["id"] for entry in entries]),
        "entries": evidence_entries,
    }
    review = {
        "schema": "nobu16.kr.switch-msgdata-v13-invariant-recovery-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "summary": {
            "residual_candidate_count": len(rows),
            "stock_visible_candidate_count": pool_summary["stock_visible_count"],
            "translated_count": len(entries),
            "excluded_count": len(exclusions),
            "runtime_reviewed_count": 0,
        },
        "entries": [
            {
                "id": entry["id"],
                "status": "translated",
                "human_review_required": True,
                "runtime_reviewed": False,
                "stock_visible_target": True,
                "source_script_free": True,
                "pk_sc_invariants_preserved": True,
                "translation_origin": "switch_v1.3_text_equals_v1.1_invariant_recovery",
            }
            for entry in entries
        ],
        "exclusions": exclusions,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["overlay"] = write_json(
        out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}"
    )
    artifacts["alignment_evidence"] = write_json(
        out_root / "evidence" / EVIDENCE_NAME, evidence, f"evidence/{EVIDENCE_NAME}"
    )
    artifacts["review_index"] = write_json(
        out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}"
    )

    for name, artifact in artifacts.items():
        public_text = (out_root / artifact["path"]).read_text(encoding="utf-8")
        if source_script_counts(public_text) != {"cjk_unified_count": 0, "kana_count": 0}:
            raise RecoveryError(f"{name} artifact contains CJK unified or kana")

    input_after = input_snapshot(args)
    if input_before != input_after:
        raise RecoveryError("read-only input changed during generation")
    validation = {
        "schema": "nobu16.kr.switch-msgdata-v13-invariant-recovery-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "scope": {
            "resource": RESOURCE,
            "residual_candidate_count": len(rows),
            "stock_visible_candidate_count": pool_summary["stock_visible_count"],
            "selected_entry_count": len(entries),
            "selected_ids_sha256": hash_json([entry["id"] for entry in entries]),
            "excluded_count": len(exclusions),
            "excluded_ids": [entry["id"] for entry in exclusions],
            "excluded_ids_sha256": hash_json([entry["id"] for entry in exclusions]),
        },
        "source_release": provenance,
        "owner_catalog": owners["snapshot"],
        "progress_integration_policy": {
            "pre_integration_unregistered_allowed": True,
            "post_integration_exact_self_registration_allowed": True,
            "self_overlay_logical_path": SELF_OVERLAY_LOGICAL_PATH,
            "self_overlay_excluded_from_prior_claims": True,
        },
        "residual_pool": pool_summary,
        "target_reconstruction": target_a,
        "reproducibility": {
            "in_memory_target_a_b_equal": True,
            "isolated_artifact_a_b_required": True,
        },
        "input_snapshot_before": input_before,
        "input_snapshot_after": input_after,
        "source_free_scan": {
            name: source_script_counts((out_root / artifact["path"]).read_text(encoding="utf-8"))
            for name, artifact in artifacts.items()
        },
        "safety": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "global_progress_modified": False,
            "global_readme_modified": False,
            "font_modified": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "commit_or_push_performed": False,
        },
        "artifacts": artifacts,
    }
    validation["source_free_scan"]["generation_validation"] = source_script_counts(
        encode_json(validation).decode("utf-8")
    )
    if any(sum(counts.values()) for counts in validation["source_free_scan"].values()):
        raise RecoveryError("validation artifact source-free scan failed")
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation, VALIDATION_NAME
    )
    return {
        "out_root": out_root,
        "entry_count": len(entries),
        "excluded_count": len(exclusions),
        "artifacts": artifacts,
        "target_reconstruction": target_a,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--switch-zip", type=Path, default=REPO_ROOT / SWITCH_ARCHIVE_RELATIVE
    )
    parser.add_argument(
        "--base-jp-strdata", type=Path, default=GAME_ROOT / "MSG" / "JP" / "strdata.bin"
    )
    parser.add_argument(
        "--stock-pk-jp", type=Path, default=GAME_ROOT / "MSG_PK" / "JP" / "msgdata.bin"
    )
    parser.add_argument(
        "--stock-pk-sc", type=Path, default=GAME_ROOT / STOCK_SC_RELATIVE
    )
    parser.add_argument(
        "--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE
    )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"entries={result['entry_count']}")
    print(f"excluded={result['excluded_count']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
