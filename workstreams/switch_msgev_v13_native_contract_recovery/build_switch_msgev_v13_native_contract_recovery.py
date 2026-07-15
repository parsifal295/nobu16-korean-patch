#!/usr/bin/env python3
"""Build thirteen manually reconstructed PK ``msgev`` Korean rows.

The preceding Switch v1.3 invariant-recovery pass deliberately excludes these
rows because their PK/SC escape-token counts or custom bracket-token order do
not match the Switch Korean draft.  This builder uses the pinned official PK
SC, JP, EN, and TC rows plus the exact Switch Japanese mapping as read-only
context.  The Korean results are rewritten against the PK/SC runtime contract;
commercial source strings and complete game resources are never emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
STRICT_ROOT = REPO_ROOT / "workstreams" / "switch_msgev_v13_jp_hash_recovery"
sys.path[:0] = [str(TOOLS_ROOT), str(STRICT_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgev_v13_jp_hash_recovery as strict  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "switch-v13-pk-msgev-native-contract-recovery-13.v1"
RESOURCE = "MSG_PK/SC/msgev.bin"
SELECTED_IDS = [
    6_829,
    6_833,
    7_027,
    7_633,
    7_823,
    7_953,
    8_094,
    8_642,
    8_959,
    9_331,
    9_336,
    9_340,
    10_888,
]
EXPECTED_SELECTED_IDS_SHA256 = (
    "FBEB52131D74798885BD0BC311399EB1F054EFB0CB716BE8DFE0AD1133897C72"
)

OVERLAY_NAME = "msgev_ko_switch_v13_native_contract_recovery_13.v1.json"
EVIDENCE_NAME = "switch_v13_msgev_native_contract_recovery_alignment.v1.json"
REVIEW_NAME = "switch_v13_msgev_native_contract_recovery_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = (
    "workstreams/switch_msgev_v13_native_contract_recovery/public/" + OVERLAY_NAME
)
PREDECESSOR_OVERLAY_PATH = (
    "workstreams/switch_msgev_v13_invariant_recovery/public/"
    "msgev_ko_switch_v13_invariant_recovery_248.v1.json"
)

TARGET_CATALOG_RELATIVE = Path("data/public/translation_target_keys.v0.1.json")
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")
PREDECESSOR_REVIEW_RELATIVE = Path(
    "workstreams/switch_msgev_v13_invariant_recovery/review/"
    "switch_v13_msgev_invariant_recovery_review.v1.json"
)
PREDECESSOR_REVIEW_SHA256 = (
    "46F86345A82D8172EA8F00DBBE662BA76EA1726EC2319BEF6957209B9071DE75"
)

EXPECTED_TARGET_COUNT = 12_906
EXPECTED_TARGET_IDS_SHA256 = (
    "00D725442F097A6F369FC3AC662C753976EAA07C714FDF6F436A7EF8B62E7C89"
)
EXPECTED_PRIOR_PATH_COUNT = 32
EXPECTED_PRIOR_PATHS_SHA256 = (
    "D8C9647E087E8B1822DF215D2BB7F44BB8DCB36F02C5CCFA1A2C7DCBF8D7A78D"
)
EXPECTED_PRIOR_CLAIM_COUNT = 13_007
EXPECTED_PRIOR_CLAIM_IDS_SHA256 = (
    "833726800A984AC94C62BA07E5DC11A9015651B0F691724EA27807B3CF753CFE"
)
EXPECTED_PRIOR_TARGET_COUNT = 11_409
EXPECTED_PRIOR_TARGET_IDS_SHA256 = (
    "B328F053C31C5E43230FE7FA31DA8306D730AB8D06116083A7D0D5AA55FFCD84"
)
EXPECTED_PRIOR_OUTSIDE_TARGET_COUNT = 1_598
EXPECTED_PRIOR_OUTSIDE_TARGET_IDS_SHA256 = (
    "5C050980004350E17D6B4E5BFC0151075CFDEBF1D41006A7E7FBE5BBC2B0E313"
)

# Pinned after the first deterministic generation.  It is checked only when
# the exact self path is already present in the progress catalog.
EXPECTED_OVERLAY_SHA256 = (
    "92767CB6E1C0BB890F185F611B3055A2E75370D544370A0AEDF08B8AAC6FDE07"
)

SOURCE_PINS: dict[str, dict[str, Any]] = {
    "SC": dict(strict.upstream.SOURCE_PINS["pk_sc_stock"]),
    "JP": dict(strict.upstream.SOURCE_PINS["pk_jp"]),
    "EN": {
        "logical_path": "MSG_PK/EN/msgev.bin",
        "size": 758_160,
        "packed_sha256": "95CDB15F1AED529C95ADDE784A750059E90060A44DF1EA208EB4A56E2F685640",
        "raw_size": 1_868_232,
        "raw_sha256": "806A34770ABA15550033E0B2D51CFA849E3C9367B61BC0BA05C37B87F13475EF",
        "string_count": 17_910,
    },
    "TC": {
        "logical_path": "MSG_PK/TC/msgev.bin",
        "size": 523_304,
        "packed_sha256": "CB4A3E57AF2091124669E28BF1DD6B8C664BFA8A1EF800F8BB6FD79C82E1DE47",
        "raw_size": 740_444,
        "raw_sha256": "39F661510E2A4D53E07B3D93DE34A315BAD4231A1BB8B96E8E79674908A4B5D3",
        "string_count": 17_910,
    },
}

# Reviewed Korean results only.  Official source text remains in the pinned
# local resources and is represented in public evidence solely by hashes.
TRANSLATIONS: dict[int, str] = {
    6_829: (
        "그런 말씀은 마시옵소서……\n"
        "선사께서는 반드시\n"
        "건강히 오래 사셔야 하옵니다!"
    ),
    6_833: (
        "내 마지막 제자는 앞날을 스스로 선택할 만큼\n"
        "충분히 뛰어난 재능을 지니고 있으니 말이다.\n"
        "물론, 네가 \x1bCB이마가와 가문\x1bCZ을 도와주기를 기도하마……"
    ),
    7_027: (
        "\x1bCA다케나카 한베에\x1bCZ는 \x1bCA[b826]\x1bCZ의 결백을 끝까지 믿었기에,\n"
        "\x1bCA쇼주마루\x1bCZ를 처형했다는 거짓 보고를 \x1bCA노부나가\x1bCZ에게 올렸다.\n"
        "실제로는 그를 숨겨 주었다."
    ),
    7_633: (
        "곧 비가 많이 내리는 시기가 옵니다……\n"
        "튼튼한 제방을 쌓아 아시모리강의 물을 끌어들이면,\n"
        "\x1bCC다카마쓰성\x1bCZ을 외딴섬으로 만들 수 있을 것입니다."
    ),
    7_823: (
        "교토를 탈환한다!\n"
        "\x1bCA미쓰히데\x1bCZ를 베어 \x1bCA노부나가\x1bCZ 님의 원수를 갚고,\n"
        "후계자로서 천하의 인정을 받겠다!"
    ),
    7_953: (
        "그 일은 우리 중신들이 보필하면 문제될 것 없소.\n"
        "아무리 어리시다 해도 엄연히 후계자가 계신 이상,\n"
        "\x1bCA노부타카\x1bCZ 님을 후사로 세우는 데 반대하오!"
    ),
    8_094: (
        "이것이 덴분의 난이오.\n"
        "\x1bCB다테 가문\x1bCZ의 가세를 크게 쇠퇴시킨 쓰라린 교훈이었소."
    ),
    8_642: (
        "그때 후방의 \x1bCC다치바나야마성\x1bCZ에서\n"
        "\x1bCA[b1222]\x1bCZ가 \x1bCA[bm1221]\x1bCZ를 찾아왔다."
    ),
    8_959: (
        "모토나리가 세 아들에게 모리 가문의 미래를 맡기며\n"
        "친필로 쓴 《삼자교훈장》은 오늘날까지 남아,\n"
        "힘을 합치는 일의 중요성을 지금도 전하고 있다……"
    ),
    9_331: (
        "에이로쿠 3년(1560년), 두 번째 \x1bCC귀경\x1bCZ으로부터 1년여,\n"
        "구보 \x1bCA[b75]\x1bCZ는 실력자 \x1bCA미요시 나가요시\x1bCZ의 전횡을 마주하고\n"
        "의욕을 잃고 있었다……"
    ),
    9_336: (
        "그 의기양양한 모습을 못마땅하게 여긴 다이묘도 많았다.\n"
        "그동안 기나이를 제 것인 양 장악해 온 \x1bCB미요시\x1bCZ 일파,\n"
        "\x1bCC오사카\x1bCZ에 거대한 기반을 둔 \x1bCB혼간지\x1bCZ……"
    ),
    9_340: (
        "\x1bCA노부나가\x1bCZ는 제장에게 천하 통일을 서두르라 명했다.\n"
        "\x1bCA시바타 가쓰이에\x1bCZ를 보내 \x1bCC호쿠리쿠\x1bCZ의 "
        "\x1bCA우에스기 가게카쓰\x1bCZ를 상대하게 하고,\n"
        "\x1bCA다키가와 가즈마스\x1bCZ와 \x1bCA도쿠가와 이에야스\x1bCZ 등을 보내 "
        "\x1bCC간토\x1bCZ를 견제하게 했다……"
    ),
    10_888: (
        "\x1bCC야마자키\x1bCZ와 \x1bCC덴노잔\x1bCZ에서 맞선 두 진영이\n"
        "이제 막 전투를 시작하려 한다."
    ),
}

DECISIONS: dict[int, dict[str, Any]] = {
    6_829: {"repair": "remove_non_contract_escape_pair", "basis": "pk_sc_with_multilingual_context"},
    6_833: {"repair": "add_pk_sc_clan_escape_pair", "basis": "pk_sc_with_multilingual_context"},
    7_027: {"repair": "reorder_entities_and_remove_duplicate_escape_pair", "basis": "pk_sc_jp_tc_alignment"},
    7_633: {"repair": "remove_non_contract_location_escape_pair", "basis": "pk_sc_jp_tc_alignment"},
    7_823: {"repair": "remove_non_contract_capital_escape_pair", "basis": "pk_sc_jp_tc_alignment"},
    7_953: {"repair": "add_pk_sc_officer_escape_pair", "basis": "pk_sc_with_multilingual_context"},
    8_094: {"repair": "add_pk_sc_clan_escape_pair", "basis": "pk_sc_with_multilingual_context"},
    8_642: {"repair": "reorder_dynamic_bracket_entities", "basis": "pk_sc_tc_coordinate_order"},
    8_959: {"repair": "remove_non_contract_person_and_clan_escape_pairs", "basis": "pk_sc_with_multilingual_context"},
    9_331: {"repair": "add_pk_sc_capital_escape_pair", "basis": "pk_sc_tc_coordinate_contract"},
    9_336: {"repair": "remove_non_contract_region_escape_pair", "basis": "pk_sc_tc_coordinate_contract"},
    9_340: {"repair": "reorder_entities_and_expand_pc_literal_officer", "basis": "pk_sc_tc_coordinate_contract"},
    10_888: {
        "repair": "replace_incompatible_switch_dynamic_person_fragment",
        "basis": "pk_sc_tc_locale_rewrite",
        "jp_en_switch_semantic_conflict": True,
    },
}

HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
BRACKET_TOKEN_RE = strict.upstream.BRACKET_TOKEN_RE


class NativeRecoveryError(ValueError):
    """Raised when an input pin, translation, or safety contract changes."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def artifact_metadata(relative: str, blob: bytes) -> dict[str, Any]:
    return {"path": relative, "size": len(blob), "sha256": sha256(blob)}


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name


def _safe_out_root(path: Path, repo_root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise NativeRecoveryError("output must remain inside the patch workspace") from exc
    return resolved


def load_pinned_table(path: Path, language: str) -> dict[str, Any]:
    pin = SOURCE_PINS[language]
    packed = path.read_bytes()
    if len(packed) != int(pin["size"]) or sha256(packed) != pin["packed_sha256"]:
        raise NativeRecoveryError(f"{language} packed msgev differs from its pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != int(pin["raw_size"]) or sha256(raw) != pin["raw_sha256"]:
        raise NativeRecoveryError(f"{language} raw msgev differs from its pin")
    table = parse_message_table(raw)
    if table.string_count != int(pin["string_count"]):
        raise NativeRecoveryError(f"{language} msgev string count differs from its pin")
    if rebuild_message_table(table, table.texts) != raw:
        raise NativeRecoveryError(f"{language} unchanged rebuild is not exact")
    return {
        "packed": packed,
        "raw": raw,
        "table": table,
        "public_pin": {
            "logical_path": pin["logical_path"],
            "size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
            "string_count": table.string_count,
        },
    }


def load_sources(game_root: Path, repo_root: Path, archive_path: Path) -> dict[str, Any]:
    strict_sources = strict.load_sources(game_root, repo_root, archive_path)
    sc = strict_sources["pk_sc_stock"]
    jp = strict_sources["pk_jp"]
    return {
        "SC": {
            **sc,
            "public_pin": {
                key: SOURCE_PINS["SC"][key]
                for key in (
                    "logical_path",
                    "size",
                    "packed_sha256",
                    "raw_size",
                    "raw_sha256",
                    "string_count",
                )
            },
        },
        "JP": {
            **jp,
            "public_pin": {
                key: SOURCE_PINS["JP"][key]
                for key in (
                    "logical_path",
                    "size",
                    "packed_sha256",
                    "raw_size",
                    "raw_sha256",
                    "string_count",
                )
            },
        },
        "EN": load_pinned_table(game_root / "MSG_PK" / "EN" / "msgev.bin", "EN"),
        "TC": load_pinned_table(game_root / "MSG_PK" / "TC" / "msgev.bin", "TC"),
        "switch_ko": strict_sources["switch_ko"],
        "base_jp": strict_sources["base_jp"],
    }


def load_target_catalog(path: Path) -> dict[str, Any]:
    catalog, blob = common.load_json_strict(path)
    if catalog.get("schema") != "nobu16.kr.translation-target-keys.v0.1":
        raise NativeRecoveryError("translation target catalog schema changed")
    if catalog.get("source_free") is not True or catalog.get("contains_source_text") is not False:
        raise NativeRecoveryError("translation target catalog is not source-free")
    resources = catalog.get("resources")
    rows = (
        [row for row in resources if row.get("path") == RESOURCE]
        if isinstance(resources, list)
        else []
    )
    if len(rows) != 1:
        raise NativeRecoveryError("translation target catalog has no unique msgev row")
    row = rows[0]
    ids = row.get("target_ids")
    if not isinstance(ids, list) or any(type(value) is not int for value in ids):
        raise NativeRecoveryError("msgev target IDs are invalid")
    typed = [int(value) for value in ids]
    if typed != sorted(set(typed)):
        raise NativeRecoveryError("msgev target IDs are not sorted and unique")
    if (
        len(typed) != EXPECTED_TARGET_COUNT
        or hash_json(typed) != EXPECTED_TARGET_IDS_SHA256
        or row.get("target_count") != EXPECTED_TARGET_COUNT
        or row.get("target_keys_sha256") != EXPECTED_TARGET_IDS_SHA256
    ):
        raise NativeRecoveryError("msgev exact target set differs from its pin")
    return {
        "path": _repo_relative(path, REPO_ROOT),
        "entry_count": len(typed),
        "ids_sha256": hash_json(typed),
        "ids": set(typed),
        "catalog_sha256": sha256(blob),
    }


def _load_overlay(path: Path) -> tuple[dict[str, Any], bytes, list[int]]:
    overlay, blob = common.load_json_strict(path)
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE:
        raise NativeRecoveryError(f"overlay targets another resource: {path}")
    ids = [int(entry["id"]) for entry in entries]
    return overlay, blob, ids


def audit_progress_registration(
    progress_path: Path, repo_root: Path, target_ids: set[int]
) -> dict[str, Any]:
    """Pin the historical predecessor set and validate later disjoint successors."""
    progress, _progress_blob = common.load_json_strict(progress_path)
    resources = progress.get("resources")
    rows = (
        [row for row in resources if row.get("path") == RESOURCE]
        if isinstance(resources, list)
        else []
    )
    if len(rows) != 1:
        raise NativeRecoveryError("progress catalog has no unique msgev row")
    patterns = rows[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise NativeRecoveryError("msgev progress overlay paths are invalid")

    prior_paths: list[str] = []
    prior_ids: list[int] = []
    successor_ids: set[int] = set()
    self_count = 0
    predecessor_boundary_seen = False
    for pattern in patterns:
        paths = sorted(repo_root.glob(pattern))
        if len(paths) != 1:
            raise NativeRecoveryError(
                f"progress overlay pattern {pattern!r} resolved to {len(paths)} files"
            )
        path = paths[0]
        logical = _repo_relative(path, repo_root)
        overlay, blob, ids = _load_overlay(path)
        if logical == SELF_OVERLAY_PATH:
            if pattern != SELF_OVERLAY_PATH:
                raise NativeRecoveryError("self overlay must use its exact logical path")
            if overlay.get("overlay_id") != BATCH_ID:
                raise NativeRecoveryError("self registration overlay_id changed")
            if ids != SELECTED_IDS or hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
                raise NativeRecoveryError("self registration ID set changed")
            if (
                EXPECTED_OVERLAY_SHA256 != "__PIN_AFTER_GENERATION__"
                and sha256(blob) != EXPECTED_OVERLAY_SHA256
            ):
                raise NativeRecoveryError("self registration overlay hash changed")
            self_count += 1
            continue
        if predecessor_boundary_seen:
            if pattern != logical:
                raise NativeRecoveryError("successor overlays must use exact logical paths")
            policy = overlay.get("distribution_policy")
            if not isinstance(policy, dict) or policy.get(
                "contains_commercial_source_text"
            ) is not False or policy.get("contains_complete_game_resource") is not False:
                raise NativeRecoveryError(f"successor overlay is not source-free: {logical}")
            overlap = set(ids) & set(SELECTED_IDS)
            if overlap:
                raise NativeRecoveryError(
                    f"successor overlaps native recovery at {min(overlap)}: {logical}"
                )
            duplicate = set(ids) & successor_ids
            if duplicate:
                raise NativeRecoveryError(
                    f"successor overlays overlap at {min(duplicate)}: {logical}"
                )
            successor_ids.update(ids)
            continue
        prior_paths.append(logical)
        prior_ids.extend(ids)
        if logical == PREDECESSOR_OVERLAY_PATH:
            predecessor_boundary_seen = True

    if self_count > 1:
        raise NativeRecoveryError("self overlay is registered more than once")
    if not predecessor_boundary_seen:
        raise NativeRecoveryError("invariant-recovery predecessor boundary is absent")
    if len(prior_paths) != EXPECTED_PRIOR_PATH_COUNT:
        raise NativeRecoveryError("prior msgev progress path count changed")
    if hash_json(prior_paths) != EXPECTED_PRIOR_PATHS_SHA256:
        raise NativeRecoveryError("prior msgev progress path set/order changed")
    if len(prior_ids) != len(set(prior_ids)):
        raise NativeRecoveryError("prior msgev overlay IDs overlap")
    claims = set(prior_ids)
    if len(claims) != EXPECTED_PRIOR_CLAIM_COUNT:
        raise NativeRecoveryError("prior msgev claim count changed")
    if hash_json(sorted(claims)) != EXPECTED_PRIOR_CLAIM_IDS_SHA256:
        raise NativeRecoveryError("prior msgev claim ID set changed")
    target_claims = claims & target_ids
    outside_claims = claims - target_ids
    if (
        len(target_claims) != EXPECTED_PRIOR_TARGET_COUNT
        or hash_json(sorted(target_claims)) != EXPECTED_PRIOR_TARGET_IDS_SHA256
    ):
        raise NativeRecoveryError("prior msgev target-intersection claims changed")
    if (
        len(outside_claims) != EXPECTED_PRIOR_OUTSIDE_TARGET_COUNT
        or hash_json(sorted(outside_claims)) != EXPECTED_PRIOR_OUTSIDE_TARGET_IDS_SHA256
    ):
        raise NativeRecoveryError("prior msgev outside-target claims changed")
    if claims.intersection(SELECTED_IDS):
        raise NativeRecoveryError("native recovery overlaps a prior overlay")
    successor_prior_overlap = successor_ids & claims
    if successor_prior_overlap:
        raise NativeRecoveryError(
            f"successor overlaps a pinned predecessor at {min(successor_prior_overlap)}"
        )
    if not set(SELECTED_IDS).issubset(target_ids):
        raise NativeRecoveryError("native recovery contains an outside-target ID")

    # Deliberately exclude the current self-registration state.  The snapshot
    # and generated artifacts are byte-identical before and after one exact
    # registration.
    return {
        "prior_overlay_path_count": len(prior_paths),
        "prior_overlay_paths_sha256": hash_json(prior_paths),
        "prior_claim_count": len(claims),
        "prior_claim_ids_sha256": hash_json(sorted(claims)),
        "prior_target_intersection_count": len(target_claims),
        "prior_target_intersection_ids_sha256": hash_json(sorted(target_claims)),
        "prior_outside_target_count": len(outside_claims),
        "prior_outside_target_ids_sha256": hash_json(sorted(outside_claims)),
        "candidate_count": len(SELECTED_IDS),
        "candidate_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "candidate_prior_overlap_count": 0,
        "candidate_target_intersection_count": len(SELECTED_IDS),
        "candidate_outside_target_count": 0,
        "target_coverage_after_registration": len(target_claims) + len(SELECTED_IDS),
        "self_registration_states_allowed": ["absent", "one_exact_path"],
        "self_excluded_from_prior_claims": True,
        "registration_order_independent": True,
        "ids": claims,
    }


def validate_predecessor_exclusions(repo_root: Path) -> dict[str, Any]:
    path = repo_root / PREDECESSOR_REVIEW_RELATIVE
    review, blob = common.load_json_strict(path)
    if sha256(blob) != PREDECESSOR_REVIEW_SHA256:
        raise NativeRecoveryError("predecessor invariant-recovery review changed")
    exclusions = review.get("exclusions")
    ids = (
        [entry.get("id") for entry in exclusions]
        if isinstance(exclusions, list)
        else []
    )
    if ids != SELECTED_IDS or hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
        raise NativeRecoveryError("predecessor exclusion partition changed")
    return {
        "path": PREDECESSOR_REVIEW_RELATIVE.as_posix(),
        "sha256": sha256(blob),
        "excluded_count": len(ids),
        "excluded_ids_sha256": hash_json(ids),
        "exact_partition_consumed": True,
    }


def switch_mapping_for_id(
    sources: dict[str, Any], entry_id: int
) -> tuple[str, list[int], str]:
    pk_jp = sources["JP"]["table"].texts[entry_id]
    buckets = strict.exact_jp_buckets(
        {
            "pk_jp": sources["JP"],
            "base_jp": sources["base_jp"],
            "switch_ko": sources["switch_ko"],
        }
    )
    jp_hash = common.text_hash(pk_jp)
    hash_rows = buckets.get(jp_hash, [])
    exact_rows = [row for row in hash_rows if row["jp"] == pk_jp]
    if not exact_rows or len(exact_rows) != len(hash_rows):
        raise NativeRecoveryError(f"ID {entry_id} has no unique exact Switch JP bucket")
    switch_ko = strict.resolve_unique_meaningful_ko(exact_rows, pk_jp)
    if switch_ko is None:
        raise NativeRecoveryError(f"ID {entry_id} has no unique meaningful Switch Korean")
    coordinates = sorted(int(row["coordinate"]) for row in exact_rows)
    return switch_ko, coordinates, jp_hash


def validate_translation(source_sc: str, translation: str, entry_id: int) -> dict[str, Any]:
    if not common.has_semantic_text(source_sc):
        raise NativeRecoveryError(f"ID {entry_id} is not a visible PK SC target")
    if not common.has_semantic_text(translation) or HANGUL_RE.search(translation) is None:
        raise NativeRecoveryError(f"ID {entry_id} lacks meaningful Hangul")
    if strict.upstream.contains_cjk_or_kana(translation):
        raise NativeRecoveryError(f"ID {entry_id} contains CJK or Kana")
    problems = common.invariant_mismatches(source_sc, translation)
    if problems:
        raise NativeRecoveryError(f"ID {entry_id} PK SC invariants differ: {problems}")
    source_brackets = BRACKET_TOKEN_RE.findall(source_sc)
    target_brackets = BRACKET_TOKEN_RE.findall(translation)
    if source_brackets != target_brackets:
        raise NativeRecoveryError(f"ID {entry_id} custom bracket sequence differs")
    return {
        "pk_sc_invariants_preserved": True,
        "custom_bracket_tokens_preserved": True,
        "custom_bracket_token_count": len(source_brackets),
        "source_script_free": True,
    }


def derive_entries(
    sources: dict[str, Any], target_ids: set[int], prior_ids: set[int]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if sorted(TRANSLATIONS) != SELECTED_IDS or sorted(DECISIONS) != SELECTED_IDS:
        raise NativeRecoveryError("translation or decision table does not cover exact IDs")
    if hash_json(SELECTED_IDS) != EXPECTED_SELECTED_IDS_SHA256:
        raise NativeRecoveryError("selected ID set differs from its pin")
    entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in SELECTED_IDS:
        if entry_id not in target_ids or entry_id in prior_ids:
            raise NativeRecoveryError(f"ID {entry_id} is not an unclaimed exact target")
        source_sc = sources["SC"]["table"].texts[entry_id]
        translation = TRANSLATIONS[entry_id]
        checks = validate_translation(source_sc, translation, entry_id)
        switch_ko, coordinates, jp_hash = switch_mapping_for_id(sources, entry_id)
        if common.text_hash(translation) == common.text_hash(switch_ko):
            raise NativeRecoveryError(f"ID {entry_id} blindly preserves the Switch value")
        language_hashes = {
            language: common.text_hash(sources[language]["table"].texts[entry_id])
            for language in ("SC", "JP", "EN", "TC")
        }
        if language_hashes["JP"] != jp_hash:
            raise NativeRecoveryError(f"ID {entry_id} JP mapping hash changed")
        entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": language_hashes["SC"],
                "ko": translation,
            }
        )
        decision = DECISIONS[entry_id]
        evidence_entries.append(
            {
                "id": entry_id,
                "official_pk_utf16le_sha256": language_hashes,
                "switch_ko_before_utf16le_sha256": common.text_hash(switch_ko),
                "ko_utf16le_sha256": common.text_hash(translation),
                "base_jp_coordinate_count": len(coordinates),
                "base_jp_coordinate_ids_sha256": hash_json(coordinates),
                "exact_switch_japanese_mapping": True,
                "unique_meaningful_switch_korean_draft": True,
                "switch_text_blindly_preserved": False,
                "native_reconstruction_completed": True,
                "semantic_basis": decision["basis"],
                "control_repair": decision["repair"],
                "jp_en_switch_semantic_conflict": bool(
                    decision.get("jp_en_switch_semantic_conflict", False)
                ),
                "official_multilingual_context_reviewed": True,
                "selected_within_exact_target_key": True,
                "selected_within_stock_visible_target": True,
                "disjoint_from_prior_overlays": True,
                **checks,
            }
        )
    return entries, evidence_entries


def reconstruct_target(sources: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
    packed = sources["SC"]["packed"]
    raw = sources["SC"]["raw"]
    table = sources["SC"]["table"]
    texts = list(table.texts)
    for entry in entries:
        texts[int(entry["id"])] = str(entry["ko"])
    rebuilt_raw = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise NativeRecoveryError("in-memory target parse check failed")
    rebuilt_packed = recompress_wrapper(rebuilt_raw, packed)
    if decompress_wrapper(rebuilt_packed)[1] != rebuilt_raw:
        raise NativeRecoveryError("in-memory target wrapper check failed")
    if rebuild_message_table(table, table.texts) != raw:
        raise NativeRecoveryError("pristine SC unchanged rebuild is not exact")
    return {
        "resource": RESOURCE,
        "changed_entry_count": len(entries),
        "raw_size": len(rebuilt_raw),
        "raw_sha256": sha256(rebuilt_raw),
        "packed_size": len(rebuilt_packed),
        "packed_sha256": sha256(rebuilt_packed),
        "parse_rebuild_round_trip": True,
        "wrapper_round_trip": True,
        "complete_target_included": False,
    }


def actual_input_snapshot(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
) -> dict[str, str]:
    paths = {
        "switch_archive": archive_path,
        "pk_sc": repo_root / SOURCE_PINS["SC"]["logical_path"],
        "pk_jp": game_root / SOURCE_PINS["JP"]["logical_path"],
        "pk_en": game_root / SOURCE_PINS["EN"]["logical_path"],
        "pk_tc": game_root / SOURCE_PINS["TC"]["logical_path"],
        "target_catalog": target_path,
        "progress_catalog": progress_path,
        "predecessor_review": repo_root / PREDECESSOR_REVIEW_RELATIVE,
    }
    return {name: sha256(path.read_bytes()) for name, path in paths.items()}


def build_once(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    out_root = _safe_out_root(out_root, repo_root)
    before = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    target = load_target_catalog(target_path)
    progress = audit_progress_registration(progress_path, repo_root, target["ids"])
    predecessor = validate_predecessor_exclusions(repo_root)
    sources = load_sources(game_root, repo_root, archive_path)
    entries, evidence_entries = derive_entries(
        sources, target["ids"], progress["ids"]
    )
    rebuilt_a = reconstruct_target(sources, entries)
    rebuilt_b = reconstruct_target(sources, entries)
    if rebuilt_a != rebuilt_b:
        raise NativeRecoveryError("in-memory target reconstruction is not deterministic")

    source_public = {
        language: sources[language]["public_pin"]
        for language in ("SC", "JP", "EN", "TC")
    }
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
            key: source_public["SC"][key]
            for key in (
                "size",
                "packed_sha256",
                "raw_size",
                "raw_sha256",
                "string_count",
            )
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    common.validate_overlay_shape(overlay)

    canonical_progress = {key: value for key, value in progress.items() if key != "ids"}
    target_public = {key: value for key, value in target.items() if key != "ids"}
    evidence = {
        "schema": "nobu16.kr.switch-msgev-v13-native-contract-recovery-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "selected_entry_count": len(entries),
            "selected_ids": SELECTED_IDS,
            "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
            "exact_predecessor_exclusion_partition": True,
        },
        "source_release": strict.SWITCH_RELEASE,
        "official_source_files": source_public,
        "target_catalog": target_public,
        "progress_registration_audit": canonical_progress,
        "predecessor_exclusion_partition": predecessor,
        "translation_policy": {
            "method": "manual_native_korean_reconstruction_from_multilingual_context",
            "switch_text_role": "draft_and_alignment_evidence_only",
            "runtime_contract_authority": "pk_sc",
            "semantic_context_languages": ["SC", "JP", "EN", "TC"],
            "switch_text_blindly_preserved": False,
            "published_source_material": "hashes_only",
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "esc_sequences_in_order",
                "other_controls",
                "line_break_sequence",
                "private_use_codepoints",
                "leading_whitespace",
                "trailing_whitespace",
                "custom_bracket_tokens_in_order",
            ],
        },
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msgev-v13-native-contract-recovery-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "quality_state": "native_semantic_review_complete_runtime_review_pending",
        "entry_count": len(entries),
        "entries": [
            {
                "id": row["id"],
                "status": "translated",
                "translation_origin": "official_multilingual_context_native_korean",
                "semantic_basis": row["semantic_basis"],
                "control_repair": row["control_repair"],
                "jp_en_switch_semantic_conflict": row[
                    "jp_en_switch_semantic_conflict"
                ],
                "semantic_review_completed": True,
                "pk_sc_invariants_preserved": True,
                "custom_bracket_tokens_preserved": True,
                "source_script_free": True,
                "exact_target": True,
                "prior_overlay_disjoint": True,
                "runtime_reviewed": False,
            }
            for row in evidence_entries
        ],
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }

    values = {
        f"public/{OVERLAY_NAME}": overlay,
        f"evidence/{EVIDENCE_NAME}": evidence,
        f"review/{REVIEW_NAME}": review,
    }
    files = {relative: encode_json(value) for relative, value in values.items()}
    expected_scan = {"han_or_kana_count": 0, "embedded_nul_count": 0}
    scans = {relative: strict.source_free_counts(blob) for relative, blob in files.items()}
    if any(scan != expected_scan for scan in scans.values()):
        raise NativeRecoveryError("a generated public artifact contains source script")
    artifacts = {
        relative: artifact_metadata(relative, blob) for relative, blob in files.items()
    }
    validation = {
        "schema": "nobu16.kr.switch-msgev-v13-native-contract-recovery-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "entry_count": len(entries),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "target_catalog": target_public,
        "progress_registration_audit": canonical_progress,
        "predecessor_exclusion_partition": predecessor,
        "replacement_invariants": {
            "checked": len(entries),
            "failures": 0,
            "pk_sc_contract_preserved_count": len(entries),
            "custom_bracket_contract_preserved_count": len(entries),
            "manual_native_reconstruction_count": len(entries),
            "switch_text_blindly_preserved_count": 0,
        },
        "target_reconstruction": rebuilt_a,
        "source_free_scan": scans,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "pre_and_post_self_registration_must_be_byte_identical": True,
            "in_memory_target_a_b_equal": True,
        },
        "safety": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "base_msg_sc_modified": False,
            "root_progress_modified": False,
            "root_readme_modified": False,
            "font_modified": False,
            "commit_or_push_performed": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_blob = encode_json(validation)
    if strict.source_free_counts(validation_blob) != expected_scan:
        raise NativeRecoveryError("generated validation contains source script")
    files[VALIDATION_NAME] = validation_blob

    for relative, blob in files.items():
        path = out_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    after = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    if before != after:
        raise NativeRecoveryError("a read-only input changed during generation")
    return {
        "entry_count": len(entries),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "target": rebuilt_a,
        "files": files,
        "artifacts": {
            **artifacts,
            VALIDATION_NAME: artifact_metadata(VALIDATION_NAME, validation_blob),
        },
    }


def build_reproducibly(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    out_root = _safe_out_root(out_root, repo_root)
    before = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    tmp_root = repo_root / "tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="nobu16-msgev-native-a-", dir=tmp_root
    ) as first_dir, tempfile.TemporaryDirectory(
        prefix="nobu16-msgev-native-b-", dir=tmp_root
    ) as second_dir:
        first = build_once(
            game_root,
            repo_root,
            archive_path,
            target_path,
            progress_path,
            Path(first_dir),
        )
        second = build_once(
            game_root,
            repo_root,
            archive_path,
            target_path,
            progress_path,
            Path(second_dir),
        )
        if first["files"] != second["files"] or first["target"] != second["target"]:
            raise NativeRecoveryError("isolated builds are not byte-identical")
    final = build_once(
        game_root, repo_root, archive_path, target_path, progress_path, out_root
    )
    if final["files"] != first["files"] or final["target"] != first["target"]:
        raise NativeRecoveryError("final build differs from isolated builds")
    if (
        actual_input_snapshot(game_root, repo_root, archive_path, target_path, progress_path)
        != before
    ):
        raise NativeRecoveryError("a read-only input changed across the reproducible build")
    return final


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--archive", type=Path, default=REPO_ROOT / strict.SWITCH_ARCHIVE_RELATIVE
    )
    parser.add_argument(
        "--target-catalog", type=Path, default=REPO_ROOT / TARGET_CATALOG_RELATIVE
    )
    parser.add_argument(
        "--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE
    )
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(
            args.game_root,
            args.repo_root,
            args.archive,
            args.target_catalog,
            args.progress,
            args.out_root,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"entries={result['entry_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['packed_sha256']}")
    for relative, artifact in sorted(result["artifacts"].items()):
        print(f"{relative}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
