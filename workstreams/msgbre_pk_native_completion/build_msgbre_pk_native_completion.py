#!/usr/bin/env python3
"""Build the source-free native Korean overlay that completes PK ``msgbre``.

The eleven rows in this workstream have no safe Switch text match.  They are
translated directly after read-only alignment of the pristine official PK
SC, JP, EN, and TC tables.  Commercial source strings and complete rebuilt
resources never leave memory; published evidence contains hashes only.
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
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "msgbre_pk_native_completion_11.v0.1"
RESOURCE = "MSG_PK/SC/msgbre.bin"
SELECTED_IDS = [1749, *range(2207, 2217)]
EXPECTED_SELECTED_IDS_SHA256 = (
    "31F6AEC16C201CCDE31984F70A477A9673F651ACFE878D956C8CBAAE024BEC47"
)
EXPECTED_TARGET_COUNT = 2_217
EXPECTED_TARGET_KEYS_SHA256 = (
    "FDD3B10B6434607F642C979F804E804D7B3684FD538C92212E38E0EF4C76A5B0"
)
EXPECTED_PRIOR_CLAIMED_COUNT = 2_206
EXPECTED_PRIOR_CLAIMED_IDS_SHA256 = (
    "0027C433843D1F175772DECFDDFCFE7EA62CC42106E7944CD6D3A36628B22643"
)

OVERLAY_NAME = "msgbre_ko_pk_native_completion_11.v0.1.json"
EVIDENCE_NAME = "msgbre_pk_native_completion_evidence.v0.1.json"
REVIEW_NAME = "msgbre_pk_native_completion_review_index.v0.1.json"
VALIDATION_NAME = "msgbre_pk_native_completion_validation.v0.1.json"
SELF_OVERLAY_PATH = f"workstreams/msgbre_pk_native_completion/public/{OVERLAY_NAME}"

LOCAL_STOCK_SC_BACKUP = (
    GAME_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "pk-full-messages-seoulhangang-v1"
    / "originals"
    / "MSG_PK"
    / "SC"
    / "msgbre.bin"
)

SOURCE_PINS: dict[str, dict[str, Any]] = {
    "SC": {
        "logical_path": "MSG_PK/SC/msgbre.bin",
        "size": 226_918,
        "packed_sha256": "AD1FEC313228AADB00581C25AE59D8C6AFF54DD771A4D0F7BC35CD1B44D77B8D",
        "raw_size": 291_256,
        "raw_sha256": "E0343DCDB1BE7C62E515DE52B9045DC54A4D8FE77BF9B6F0836A3478CBD77779",
        "string_count": 3_000,
    },
    "JP": {
        "logical_path": "MSG_PK/JP/msgbre.bin",
        "size": 221_127,
        "packed_sha256": "DA9BE8242CF0A90592D573DF676ECDE26566B11C5707273EEB4AF5BA54132AD5",
        "raw_size": 333_516,
        "raw_sha256": "02237F07362E0E3DFF92C0E999A29B887EBE5971B1C3EF8F26EAA5C969FB9668",
        "string_count": 3_000,
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgbre.bin",
        "size": 295_601,
        "packed_sha256": "6A3F7415187F8D7E4442972C7F6AAA4C3D2C2CD5EE4584B72D130295FEDCBA47",
        "raw_size": 836_320,
        "raw_sha256": "8445078E7691461D791364208A4286A00D73F0FE4DF73569D376FE9E05986F64",
        "string_count": 3_000,
    },
    "TC": {
        "logical_path": "MSG_PK/TC/msgbre.bin",
        "size": 238_570,
        "packed_sha256": "B10E7C7E4BBE3D19DFB9BABBCC254A905AB0EB7BB59643C8845B18A8C4A7BB3A",
        "raw_size": 302_428,
        "raw_sha256": "84825D7E3C93EEDE3D3F38D5B2D69B1B6A6E3F985A7E21484BF21DF91555971C",
        "string_count": 3_000,
    },
}

# The official source strings are deliberately absent.  These are the eleven
# reviewed Korean results, ordered by the exact PK SC target ID.
TRANSLATIONS: dict[int, str] = {
    1749: (
        "호조 가신. 우지야스의 아들이다. 우에스기 가문과 화친을 성사시켰다. "
        "도요토미 히데요시의 오다와라 정벌 때 출격을 주장했으나 받아들여지지 "
        "않았다. 마에다 도시이에에게 거성 하치가타성을 함락당한 뒤 항복했다."
    ),
    2207: (
        "도쿠가와 가신. 미카와 잇코잇키 때 문도 편에 가담했으나 뒤에 귀참을 "
        "허락받았다. 미카타가하라 전투에서는 도쿠가와 이에야스를 하마마쓰성으로 "
        "피신시키고 자신은 그 대역을 맡아 전사했다."
    ),
    2208: (
        "다케다 가신. 마사쓰네의 형이며 다케다 이십사장의 한 사람이다. 다케다 "
        "신겐의 측근으로 중용되었고 쓰치야 가문의 명적을 받았다. 미카타가하라 "
        "전투에서 공을 세웠으나 나가시노 전투에서 전사했다."
    ),
    2209: (
        "아케치 가신. 통칭 덴고로. 아케치 미쓰히데의 아버지 대부터 섬긴 중신이라 "
        "전해진다. 야마자키 전투에서 쓰쓰이 준케이에게 참전을 권했으나 실패했다. "
        "전투 중 입은 부상으로 퇴각한 뒤 자결했다."
    ),
    2210: (
        "아시카가 가신. 쇼군 아시카가 요시테루 아래에서 이세 가문을 대신해 "
        "만도코로 집사에 임명되었다. 에이로쿠의 변 뒤에는 아시카가 요시아키에게 "
        "속했고, 요시아키가 쇼군이 되자 다시 만도코로 집사로 기용되었다."
    ),
    2211: (
        "도쿠가와 가신. 모토타다의 아버지다. 도쿠가와 이에야스가 인질이던 "
        "시절부터 중신이었으며 루스이역으로 오카자키를 다스렸다. 이에야스의 "
        "오카자키 귀환에 대비해 철저히 절약하고 군자금을 모으는 데 힘썼다."
    ),
    2212: (
        "검술가. 이름은 다카모토. 여러 구니를 순회한 끝에 오의 “이치노타치”를 "
        "터득하고 신토류를 창시했다. 평생 치른 19번의 승부에서 한 번도 패하지 "
        "않았다. 문하에는 아시카가 요시테루와 기타바타케 도모노리 등이 있다."
    ),
    2213: (
        "도쿠가와 제2대 쇼군 히데타다의 생모. 오아이노카타 또는 호다이인이라고도 "
        "한다. 미카와국 최동부의 고쿠진 사이고 가문 출신이다. 전남편과 사별한 뒤 "
        "도쿠가와 이에야스의 측실이 되었다. 용모가 단정하고 성실한 인품이었다."
    ),
    2214: (
        "도미타 노부타카의 계실. 우키타 다다이에의 딸이다. 기타노카타라 불렸으며 "
        "본명은 알려지지 않았다. 아노쓰성 전투에서는 무사 차림으로 달려가 위기에 "
        "빠진 남편을 구해 “아름답고 용맹하다”는 칭송을 받았다."
    ),
    2215: (
        "도쿠가와 이에야스의 측실. 운코인 또는 이치이노쓰보네라고도 한다. 뛰어난 "
        "재치로 이에야스의 총애를 받아 진중에도 따라나섰다. 외교 수완이 뛰어나 "
        "오사카 겨울 전투에서는 도요토미 측과의 화친 교섭을 맡았다."
    ),
    2216: (
        "시마즈 요시히사의 딸. 요시히사의 총애를 받았다고 전해진다. 도요토미 "
        "가문의 인질로 교토에 머물렀다. 남편은 시마즈 가문의 후계자로 여겨진 사촌 "
        "히사야스였으며, 그가 죽은 뒤 다다쓰네를 남편으로 맞았다."
    ),
}

REVIEW_FOCUS: dict[int, str] = {
    1749: "hojo_hachigata_odawara_register",
    2207: "tokugawa_mikatagahara_register",
    2208: "takeda_succession_and_battle_register",
    2209: "akechi_yamazaki_register",
    2210: "ashikaga_office_title_register",
    2211: "tokugawa_household_office_register",
    2212: "sword_school_and_personal_name_register",
    2213: "tokugawa_maternal_title_register",
    2214: "anotsu_warrior_title_register",
    2215: "tokugawa_consort_and_diplomacy_register",
    2216: "shimazu_marriage_and_hostage_register",
}

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
CUSTOM_BRACKETS = frozenset(
    "()[]{}<>（）［］｛｝〈〉《》「」『』【】〔〕〖〗〘〙〚〛“”‘’"
)


class NativeCompletionError(ValueError):
    """Raised when an input pin, translation, or safety gate fails."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16le"))


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


def custom_bracket_signature(text: str) -> list[str]:
    return [character for character in text if character in CUSTOM_BRACKETS]


def write_json(path: Path, value: Any, logical_path: str) -> dict[str, Any]:
    blob = json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": logical_path, "size": len(blob), "sha256": sha256(blob)}


def _safe_out_root(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise NativeCompletionError(
            "output must stay inside KR_PATCH_WORK; game files are never outputs"
        ) from exc
    return resolved


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def load_pinned_table(
    path: Path, language: str
) -> tuple[bytes, bytes, Any, dict[str, Any]]:
    pin = SOURCE_PINS[language]
    packed = path.read_bytes()
    if len(packed) != pin["size"] or sha256(packed) != pin["packed_sha256"]:
        raise NativeCompletionError(f"{language} msgbre differs from its packed pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise NativeCompletionError(f"{language} msgbre differs from its raw pin")
    table = parse_message_table(raw)
    if table.string_count != pin["string_count"]:
        raise NativeCompletionError(f"{language} msgbre string count differs from its pin")
    if rebuild_message_table(table, table.texts) != raw:
        raise NativeCompletionError(f"{language} msgbre unchanged rebuild is not exact")
    public_pin = {
        "logical_path": pin["logical_path"],
        "size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": table.string_count,
    }
    return packed, raw, table, public_pin


def load_exact_target_keys(catalog_path: Path) -> tuple[set[int], dict[str, Any]]:
    blob = catalog_path.read_bytes()
    catalog = json.loads(blob.decode("utf-8"))
    resources = catalog.get("resources")
    matches = (
        [item for item in resources if item.get("path") == RESOURCE]
        if isinstance(resources, list)
        else []
    )
    if len(matches) != 1:
        raise NativeCompletionError("target catalog has no unique PK msgbre entry")
    item = matches[0]
    ids = item.get("target_ids")
    if not isinstance(ids, list) or any(type(value) is not int for value in ids):
        raise NativeCompletionError("PK msgbre target keys are invalid")
    typed = [int(value) for value in ids]
    if (
        typed != list(range(EXPECTED_TARGET_COUNT))
        or item.get("target_count") != EXPECTED_TARGET_COUNT
        or item.get("target_keys_sha256") != EXPECTED_TARGET_KEYS_SHA256
        or ids_sha256(typed) != EXPECTED_TARGET_KEYS_SHA256
    ):
        raise NativeCompletionError("PK msgbre exact target keys differ from the pin")
    return set(typed), {
        "logical_path": _repo_relative(catalog_path),
        "sha256": sha256(blob),
        "target_count": len(typed),
        "target_keys_sha256": ids_sha256(typed),
        "contains_source_text": False,
    }


def audit_progress_registration(
    progress_path: Path, target_ids: set[int]
) -> tuple[set[int], dict[str, Any]]:
    progress_blob = progress_path.read_bytes()
    progress = json.loads(progress_blob.decode("utf-8"))
    resources = progress.get("resources")
    matches = (
        [item for item in resources if item.get("path") == RESOURCE]
        if isinstance(resources, list)
        else []
    )
    if len(matches) != 1:
        raise NativeCompletionError("translation progress has no unique PK msgbre entry")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise NativeCompletionError("PK msgbre progress overlay list is invalid")

    claims: set[int] = set()
    overlays: list[dict[str, Any]] = []
    self_registration_count = 0
    for pattern in patterns:
        if pattern == SELF_OVERLAY_PATH:
            self_registration_count += 1
            continue
        paths = sorted(REPO_ROOT.glob(pattern))
        if len(paths) != 1:
            raise NativeCompletionError(
                f"overlay pattern {pattern!r} resolved to {len(paths)} files"
            )
        path = paths[0]
        logical_path = _repo_relative(path)
        if logical_path == SELF_OVERLAY_PATH:
            self_registration_count += 1
            continue
        blob = path.read_bytes()
        overlay = json.loads(blob.decode("utf-8"))
        if overlay.get("resource") != RESOURCE:
            raise NativeCompletionError(f"overlay {logical_path} targets another resource")
        entries = overlay.get("entries")
        if not isinstance(entries, list):
            raise NativeCompletionError(f"overlay {logical_path} entries are invalid")
        ids = [entry.get("id") for entry in entries]
        if any(type(entry_id) is not int for entry_id in ids):
            raise NativeCompletionError(f"overlay {logical_path} IDs are invalid")
        typed = [int(entry_id) for entry_id in ids]
        if len(typed) != len(set(typed)) or claims.intersection(typed):
            raise NativeCompletionError(f"prior overlay IDs overlap at {logical_path}")
        claims.update(typed)
        overlays.append(
            {
                "logical_path": logical_path,
                "sha256": sha256(blob),
                "entry_count": len(typed),
                "min_id": min(typed),
                "max_id": max(typed),
            }
        )
    if self_registration_count > 1:
        raise NativeCompletionError("candidate overlay is registered more than once")

    expected_prior = target_ids.difference(SELECTED_IDS)
    claimed_hash = ids_sha256(sorted(claims))
    if (
        claims != expected_prior
        or len(claims) != EXPECTED_PRIOR_CLAIMED_COUNT
        or claimed_hash != EXPECTED_PRIOR_CLAIMED_IDS_SHA256
    ):
        raise NativeCompletionError("prior PK msgbre claims do not equal the exact 11-row gap")
    if claims.intersection(SELECTED_IDS):
        raise NativeCompletionError("native completion overlaps a prior PK msgbre overlay")

    with_candidate = claims.union(SELECTED_IDS)
    if with_candidate != target_ids:
        raise NativeCompletionError("candidate registration would not complete PK msgbre")
    snapshot = {
        "progress_logical_path": _repo_relative(progress_path),
        "progress_sha256": sha256(progress_blob),
        "candidate_registered_in_current_progress": self_registration_count == 1,
        "candidate_excluded_from_prior_claims": True,
        "registration_order_independent": True,
        "simulated_without_candidate_count": len(claims),
        "simulated_without_candidate_ids_sha256": claimed_hash,
        "simulated_with_candidate_count": len(with_candidate),
        "simulated_with_candidate_ids_sha256": ids_sha256(sorted(with_candidate)),
        "completion_after_registration": True,
        "prior_overlay_count": len(overlays),
        "prior_overlays": overlays,
    }
    return claims, snapshot


def validate_translation(
    entry_id: int, source_sc: str, translation: str
) -> dict[str, Any]:
    if not common.has_semantic_text(source_sc):
        raise NativeCompletionError(f"ID {entry_id} is outside the visible PK SC target")
    if not common.has_semantic_text(translation) or not HANGUL_RE.search(translation):
        raise NativeCompletionError(f"ID {entry_id} has no semantic Hangul translation")
    if not source_script_free(translation):
        raise NativeCompletionError(f"ID {entry_id} translation contains CJK or Kana")
    problems = common.invariant_mismatches(source_sc, translation)
    if problems:
        raise NativeCompletionError(f"ID {entry_id} message invariants differ: {problems}")
    source_brackets = custom_bracket_signature(source_sc)
    target_brackets = custom_bracket_signature(translation)
    if source_brackets != target_brackets:
        raise NativeCompletionError(f"ID {entry_id} custom bracket signature differs")
    return {
        "message_invariants_preserved": True,
        "custom_bracket_signature_preserved": True,
        "custom_bracket_count": len(source_brackets),
        "source_script_free": True,
    }


def validate_overlay_shape(overlay: dict[str, Any]) -> None:
    """Validate the common overlay shape without widening deploy allowlists."""
    expected_root = {
        "schema",
        "overlay_id",
        "resource",
        "base_language",
        "entry_count",
        "distribution_policy",
        "stock_sc",
        "defaults",
        "entries",
    }
    if set(overlay) != expected_root or overlay["schema"] != common.OVERLAY_SCHEMA:
        raise NativeCompletionError("msgbre overlay root schema is invalid")
    if overlay["resource"] != RESOURCE or overlay["base_language"] != "SC":
        raise NativeCompletionError("msgbre overlay target is invalid")
    if overlay["defaults"] != {"status": "translated"}:
        raise NativeCompletionError("msgbre overlay default status is invalid")
    if overlay["entry_count"] != len(overlay["entries"]) or not overlay["entries"]:
        raise NativeCompletionError("msgbre overlay entry count is invalid")
    if overlay["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise NativeCompletionError("msgbre overlay distribution policy is invalid")
    stock = overlay["stock_sc"]
    if set(stock) != {
        "size",
        "packed_sha256",
        "raw_size",
        "raw_sha256",
        "string_count",
    } or stock["string_count"] != 3_000:
        raise NativeCompletionError("msgbre overlay stock specification is invalid")
    ids: list[int] = []
    for entry in overlay["entries"]:
        if set(entry) != {"id", "source_sc_utf16le_sha256", "ko"}:
            raise NativeCompletionError("msgbre overlay entry shape is invalid")
        if type(entry["id"]) is not int:
            raise NativeCompletionError("msgbre overlay entry ID is invalid")
        if re.fullmatch(r"[0-9A-F]{64}", str(entry["source_sc_utf16le_sha256"])) is None:
            raise NativeCompletionError("msgbre overlay source hash is invalid")
        if not isinstance(entry["ko"], str) or "\0" in entry["ko"]:
            raise NativeCompletionError("msgbre overlay Korean text is invalid")
        entry["ko"].encode("utf-16le")
        ids.append(entry["id"])
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise NativeCompletionError("msgbre overlay IDs are not sorted and unique")


def derive_entries(
    tables: dict[str, Any], target_ids: set[int], prior_claims: set[int]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if sorted(TRANSLATIONS) != SELECTED_IDS:
        raise NativeCompletionError("translations do not exactly cover the selected IDs")
    if ids_sha256(SELECTED_IDS) != EXPECTED_SELECTED_IDS_SHA256:
        raise NativeCompletionError("selected ID set differs from its pin")
    entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in SELECTED_IDS:
        if entry_id not in target_ids or entry_id in prior_claims:
            raise NativeCompletionError(f"ID {entry_id} is not an unclaimed exact target")
        source_sc = tables["SC"].texts[entry_id]
        translation = TRANSLATIONS[entry_id]
        checks = validate_translation(entry_id, source_sc, translation)
        language_hashes = {
            language: text_hash(tables[language].texts[entry_id])
            for language in ("SC", "JP", "EN", "TC")
        }
        if len(set(language_hashes.values())) != 4:
            raise NativeCompletionError(f"ID {entry_id} language alignment is ambiguous")
        entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": language_hashes["SC"],
                "ko": translation,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "official_source_utf16le_sha256": language_hashes,
                "ko_utf16le_sha256": text_hash(translation),
                "translation_origin": "native_korean_from_official_multilingual_alignment",
                "review_focus": REVIEW_FOCUS[entry_id],
                "official_language_alignment_complete": True,
                "proper_noun_glossary_consistent": True,
                "selected_within_exact_target_key": True,
                "selected_within_stock_visible_target": True,
                "disjoint_from_prior_overlays": True,
                **checks,
            }
        )
    return entries, evidence_entries


def reconstruct_target(
    sc_packed: bytes, sc_raw: bytes, sc_table: Any, entries: list[dict[str, Any]]
) -> dict[str, Any]:
    texts = list(sc_table.texts)
    for entry in entries:
        texts[int(entry["id"])] = str(entry["ko"])
    rebuilt_raw = rebuild_message_table(sc_table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise NativeCompletionError("in-memory target parse check failed")
    rebuilt_packed = recompress_wrapper(rebuilt_raw, sc_packed)
    if decompress_wrapper(rebuilt_packed)[1] != rebuilt_raw:
        raise NativeCompletionError("in-memory target wrapper check failed")
    unchanged = rebuild_message_table(sc_table, sc_table.texts)
    if unchanged != sc_raw:
        raise NativeCompletionError("pristine target unchanged rebuild is not exact")
    return {
        "resource": RESOURCE,
        "entry_count": len(entries),
        "raw_size": len(rebuilt_raw),
        "raw_sha256": sha256(rebuilt_raw),
        "packed_size": len(rebuilt_packed),
        "packed_sha256": sha256(rebuilt_packed),
        "parse_rebuild_round_trip": True,
        "wrapper_round_trip": True,
        "complete_target_included": False,
    }


def input_snapshot(args: argparse.Namespace) -> dict[str, str]:
    return {
        "pk_sc_msgbre": sha256(args.stock_sc.read_bytes()),
        "pk_jp_msgbre": sha256(args.stock_jp.read_bytes()),
        "pk_en_msgbre": sha256(args.stock_en.read_bytes()),
        "pk_tc_msgbre": sha256(args.stock_tc.read_bytes()),
        "translation_target_keys": sha256(args.target_catalog.read_bytes()),
        "translation_progress": sha256(args.progress.read_bytes()),
    }


def build_once(args: argparse.Namespace, out_root: Path) -> dict[str, Any]:
    out_root = _safe_out_root(out_root)
    before = input_snapshot(args)
    target_ids, target_snapshot = load_exact_target_keys(args.target_catalog)
    prior_claims, progress_snapshot = audit_progress_registration(
        args.progress, target_ids
    )
    sources: dict[str, tuple[bytes, bytes, Any, dict[str, Any]]] = {
        "SC": load_pinned_table(args.stock_sc, "SC"),
        "JP": load_pinned_table(args.stock_jp, "JP"),
        "EN": load_pinned_table(args.stock_en, "EN"),
        "TC": load_pinned_table(args.stock_tc, "TC"),
    }
    tables = {language: value[2] for language, value in sources.items()}
    source_public = {language: value[3] for language, value in sources.items()}
    entries, evidence_entries = derive_entries(tables, target_ids, prior_claims)
    target = reconstruct_target(
        sources["SC"][0], sources["SC"][1], sources["SC"][2], entries
    )
    target_repeat = reconstruct_target(
        sources["SC"][0], sources["SC"][1], sources["SC"][2], entries
    )
    if target != target_repeat:
        raise NativeCompletionError("in-memory target reconstruction is not deterministic")

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
            "size": source_public["SC"]["size"],
            "packed_sha256": source_public["SC"]["packed_sha256"],
            "raw_size": source_public["SC"]["raw_size"],
            "raw_sha256": source_public["SC"]["raw_sha256"],
            "string_count": source_public["SC"]["string_count"],
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    validate_overlay_shape(overlay)
    evidence = {
        "schema": "nobu16.kr.msgbre-pk-native-completion-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "msgbre",
        "scope": {
            "selected_entry_count": len(entries),
            "selected_ids": SELECTED_IDS,
            "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
            "exact_target_count": EXPECTED_TARGET_COUNT,
            "coverage_after_registration": EXPECTED_TARGET_COUNT,
            "completion_after_registration": True,
        },
        "official_source_files": source_public,
        "target_catalog": target_snapshot,
        "progress_registration_audit": progress_snapshot,
        "translation_policy": {
            "origin": "direct Korean translation of the official multilingual PK alignment",
            "switch_text_used": False,
            "source_alignment_languages": ["SC", "JP", "EN", "TC"],
            "published_source_material": "hashes only",
            "invariants": [
                "printf tokens",
                "unknown percent count",
                "escape controls",
                "other controls",
                "line breaks",
                "private-use code points",
                "leading whitespace",
                "trailing whitespace",
                "custom bracket sequence",
            ],
        },
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.msgbre-pk-native-completion-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "native_translation_complete_runtime_review_pending",
        "entry_count": len(entries),
        "entries": [
            {
                "id": entry["id"],
                "status": "translated",
                "translation_origin": "official_pk_multilingual_native_korean",
                "review_focus": REVIEW_FOCUS[int(entry["id"])],
                "official_language_alignment_complete": True,
                "semantic_review_completed": True,
                "proper_noun_glossary_consistent": True,
                "source_script_free": True,
                "selected_within_exact_target_key": True,
                "prior_overlay_disjoint": True,
                "pk_sc_invariants_preserved": True,
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
    if any(counts != {"cjk_unified_count": 0, "kana_count": 0} for counts in source_free_scan.values()):
        raise NativeCompletionError("generated public artifact contains CJK or Kana")

    after = input_snapshot(args)
    target_ids_after, target_snapshot_after = load_exact_target_keys(args.target_catalog)
    _, progress_snapshot_after = audit_progress_registration(args.progress, target_ids_after)
    if (
        before != after
        or target_ids_after != target_ids
        or target_snapshot_after != target_snapshot
        or progress_snapshot_after != progress_snapshot
    ):
        raise NativeCompletionError("an input or progress claim changed during generation")

    validation = {
        "schema": "nobu16.kr.msgbre-pk-native-completion-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {
            "selected_entry_count": len(entries),
            "expected_selected_entry_count": len(SELECTED_IDS),
            "selected_ids": SELECTED_IDS,
            "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
            "prior_claimed_count": len(prior_claims),
            "coverage_after_registration": len(prior_claims.union(SELECTED_IDS)),
            "exact_target_count": len(target_ids),
            "completion_after_registration": True,
        },
        "target_catalog": target_snapshot,
        "progress_registration_audit": progress_snapshot,
        "target_reconstruction": target,
        "source_free_scan": source_free_scan,
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "target_a_b_equal": True,
        },
        "safety": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "root_progress_modified": False,
            "root_readme_modified": False,
            "font_modified": False,
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
        raise NativeCompletionError("generation validation contains CJK or Kana")
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
        "progress_registration_audit": progress_snapshot,
        "artifacts": artifacts,
        "files": files,
    }


def build_reproducibly(args: argparse.Namespace) -> dict[str, Any]:
    out_root = _safe_out_root(args.out_root)
    before = input_snapshot(args)
    tmp_root = REPO_ROOT / "tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="nobu16-msgbre-native-a-", dir=tmp_root
    ) as first_dir, tempfile.TemporaryDirectory(
        prefix="nobu16-msgbre-native-b-", dir=tmp_root
    ) as second_dir:
        first = build_once(args, Path(first_dir))
        second = build_once(args, Path(second_dir))
        if first["files"] != second["files"] or first["target"] != second["target"]:
            raise NativeCompletionError("isolated native builds are not byte-identical")
    final = build_once(args, out_root)
    if final["files"] != first["files"] or final["target"] != first["target"]:
        raise NativeCompletionError("final native build differs from isolated builds")
    if input_snapshot(args) != before:
        raise NativeCompletionError("an input changed across the reproducible build")
    return final


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-sc", type=Path, default=LOCAL_STOCK_SC_BACKUP)
    parser.add_argument(
        "--stock-jp", type=Path, default=GAME_ROOT / "MSG_PK" / "JP" / "msgbre.bin"
    )
    parser.add_argument(
        "--stock-en", type=Path, default=GAME_ROOT / "MSG_PK" / "EN" / "msgbre.bin"
    )
    parser.add_argument(
        "--stock-tc", type=Path, default=GAME_ROOT / "MSG_PK" / "TC" / "msgbre.bin"
    )
    parser.add_argument(
        "--target-catalog",
        type=Path,
        default=REPO_ROOT / "data" / "public" / "translation_target_keys.v0.1.json",
    )
    parser.add_argument(
        "--progress",
        type=Path,
        default=REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json",
    )
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args(argv)


def main() -> int:
    try:
        result = build_reproducibly(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"entries={result['entry_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['packed_sha256']}")
    print(
        "coverage_after_registration="
        f"{result['progress_registration_audit']['simulated_with_candidate_count']}"
    )
    for name, artifact in sorted(result["artifacts"].items()):
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
