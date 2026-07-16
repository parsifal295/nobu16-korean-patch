#!/usr/bin/env python3
"""Freeze a safe, source-free JP-v0.9 ``msgev`` P1-03 Korean overlay.

The audit bundle has 183 coordinates.  Three dynamic bracket-substitution
rows remain byte-preserved.  For the other 180 rows, this builder reads only
committed Korean catalogs and their source-hash alignment evidence.  It emits
the 157 rows that are either literal JP-contract reuse or can be safely
rebased by replacing an equal-length ESC lexeme stream.  Rows requiring a
line-break, bracket, or ESC-pair-count judgement are published only as
source-free manual-review holds.

``freeze`` writes metadata/catalog files in this workstream.  ``build`` writes
the complete binary candidate only under ``KR_PATCH_WORK/tmp`` and never
writes a Steam installation, a release asset, or an SC container.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
sys.path[:0] = [str(TOOLS)]

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402


RESOURCE = "MSG_PK/JP/msgev.bin"
BUNDLE_ID = "p1-MSG_PK_JP_msgev-03"
AUDIT_PATH = REPO / "workstreams" / "jp_active_message_residual_audit_v1" / "public" / "active_jp_remaining_coordinates.v1.json"
DEFAULT_STOCK_ROOT = REPO / "tmp" / "steam_jp_msgev_p1_residual_03_v1" / "stock_v090"
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_msgev_p1_residual_03_v1" / "candidate"
PUBLIC_OVERLAY = WORKSTREAM / "public" / "msgev_ko_steam_jp_p1_residual_03_safe_157.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
CONTRACT = WORKSTREAM / "source_free_contract.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-03-safe-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-03-safe-validation.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-03-safe-contract.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-03-safe-build-manifest.v1"

STOCK = {
    "packed_size": 1_040_799,
    "packed_sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
    "raw_size": 1_036_708,
    "raw_sha256": "6D87086EA6B533EAB3F3745DB7564E8D7842E7DD603AD765B2D6D900644E00FB",
    "string_count": 17_916,
}
AUDIT_PIN = {
    "size": 1_188_084,
    "sha256": "AECC6969E8AD7AA00A8CC69B1DD8F6013922ABB085EE4E8397CA4D2368141E97",
}
EXPECTED_AUDIT_COUNT = 183
EXPECTED_AUDIT_SHA256 = "0245195E033DAA4F5E74D8A73CAE3624D16A751AC4D87B11CE7A1DD4F7FEE204"
EXPECTED_LITERAL_COUNT = 115
EXPECTED_ESC_REBASED_COUNT = 42
EXPECTED_APPLIED_COUNT = 157
EXPECTED_MANUAL_REVIEW_HOLD_COUNT = 23
EXPECTED_RUNTIME_PRESERVATION_COUNT = 3

DIRECT_CATALOGS = (
    {
        "relative_path": "workstreams/base_ev_strdata_jp_residual_wave11/public/ev_strdata_ko_base_jp_residual_wave11_40.v1.json",
        "size": 24_810,
        "sha256": "5F8207E5D5E0ECDA39D39C8B15EE2F1707E7A68E1FADAF70FBFF5595F552108D",
    },
    {
        "relative_path": "workstreams/base_ev_strdata_jp_switch_v13_transfer_v1/public/ev_strdata_ko_base_jp_switch_v13_transfer_13045.v1.json",
        "size": 2_939_878,
        "sha256": "1A79E514616C284C140FB8A6618BA48AD648BA88EBE4D81F618B4C551C038B2A",
    },
    {
        "relative_path": "workstreams/steam_jp_msgev_p1_residual_02_v1/public/msgev_ko_steam_jp_p1_residual_02_185.v1.json",
        "size": 142_419,
        "sha256": "BBBCB3F55D7D109B11A98195355F25D7233270158F40BE1FD2B14C9B9D162200",
    },
)
NATIVE_CATALOGS = (
    {
        "name": "native_02",
        "catalog": "workstreams/msgev_pk_native_batch02/public/msgev_ko_pk_native_batch02_150.v1.json",
        "catalog_size": 44_261,
        "catalog_sha256": "642E5B0B7503B5CCA6472CE10E4066296C6D8F6DA8DD8BC2B16EDA7BEC554367",
        "evidence": "workstreams/msgev_pk_native_batch02/evidence/msgev_pk_native_batch02_alignment.v1.json",
        "evidence_size": 256_131,
        "evidence_sha256": "1EC3875BE00EF41B5EDE9E9E0C68A68B32CF1FD42BDB7DDEB6B80E85FB0BF0E7",
    },
    {
        "name": "native_03",
        "catalog": "workstreams/msgev_pk_native_batch03/public/msgev_ko_pk_native_batch03_350.v1.json",
        "catalog_size": 98_344,
        "catalog_sha256": "B66294BB02F553591F9AA5F123AD2EBC4E937692DA0364F0FB17090F25C1DD07",
        "evidence": "workstreams/msgev_pk_native_batch03/evidence/msgev_pk_native_batch03_alignment.v1.json",
        "evidence_size": 473_507,
        "evidence_sha256": "17206EFA3AA87B3A1916A88DC969DBA81A806B45A5FFE8B4379327F85613724B",
    },
    {
        "name": "native_04",
        "catalog": "workstreams/msgev_pk_native_batch04/public/msgev_ko_pk_native_batch04_175.v1.json",
        "catalog_size": 50_889,
        "catalog_sha256": "90C1220FC4D40F218C70A01813B0A993AA61C365DC49A2649592528F0AD2F4BA",
        "evidence": "workstreams/msgev_pk_native_batch04/evidence/msgev_pk_native_batch04_alignment.v1.json",
        "evidence_size": 285_699,
        "evidence_sha256": "DED74F23A56C9D430295038C3C2D9828A9F93B84A539A865B7E9611F0D630505",
    },
    {
        "name": "native_05",
        "catalog": "workstreams/msgev_pk_native_batch05/public/msgev_ko_pk_native_batch05_300.v1.json",
        "catalog_size": 84_002,
        "catalog_sha256": "CED113C16D01202BEB63B7F66B62BDFA8478149313C2A20A539FB2B4EF599EC2",
        "evidence": "workstreams/msgev_pk_native_batch05/evidence/msgev_pk_native_batch05_alignment.v1.json",
        "evidence_size": 424_514,
        "evidence_sha256": "8EB47E12E552A4DDD669E3670ACD7E10A9165017A9C1EC10CBD98F4AAA656FF5",
    },
    {
        "name": "native_06",
        "catalog": "workstreams/msgev_pk_native_batch06/public/msgev_ko_pk_native_batch06_260.v1.json",
        "catalog_size": 60_342,
        "catalog_sha256": "94DAF36792E1BCAC12DDB5658DA91785B487D825939E2D7C94D381751C2D0BFF",
        "evidence": "workstreams/msgev_pk_native_batch06/evidence/msgev_pk_native_batch06_alignment.v1.json",
        "evidence_size": 454_128,
        "evidence_sha256": "DE9CCA0F5045B5F64D5F2206394097C8B3628FA6FA71E78C856707FE1F065E02",
    },
)
# These fixed donors resolve repeated JP source hashes by the exact catalog
# entry that carries the reviewed target control and line-break contract.
SPECIAL_DIRECT_DONORS = {
    10888: ("workstreams/base_ev_strdata_jp_switch_v13_transfer_v1/public/ev_strdata_ko_base_jp_switch_v13_transfer_13045.v1.json", 7827),
    10889: ("workstreams/steam_jp_msgev_p1_residual_02_v1/public/msgev_ko_steam_jp_p1_residual_02_185.v1.json", 7828),
    10890: ("workstreams/steam_jp_msgev_p1_residual_02_v1/public/msgev_ko_steam_jp_p1_residual_02_185.v1.json", 7829),
    15420: ("workstreams/base_ev_strdata_jp_switch_v13_transfer_v1/public/ev_strdata_ko_base_jp_switch_v13_transfer_13045.v1.json", 15190),
    16219: ("workstreams/base_ev_strdata_jp_switch_v13_transfer_v1/public/ev_strdata_ko_base_jp_switch_v13_transfer_13045.v1.json", 15989),
}
SPECIAL_NATIVE_DONORS = {9826: 9858}
SPECIAL_DONOR_REASONS = {
    9826: "native_9858_exact_source_hash_with_target_ca_cb_escape_contract",
    10888: "direct_7827_exact_target_source_hash_and_token_profile",
    10889: "p1_02_direct_7828_exact_target_source_hash_and_token_profile",
    10890: "p1_02_direct_7829_exact_target_source_hash_and_token_profile",
    15420: "ordered_equal_hash_block_suffix_4241_exact_direct_donor",
    16219: "ordered_equal_hash_block_suffix_4241_exact_direct_donor",
}
RUNTIME_STRUCTURAL_KEYS = {
    10837: "375C69E2654F0F4C131C1C7077D245A60D37CE716F3576929F6F43863A7BDA4D",
    10840: "F8CB9D48AA46C1689FFF61D08B1E86A2D1171E661D5816569A37FF9F9E4A4A84",
    10905: "25197A58676345AD961A7F1469524DF19FC53C302278B390C1B14970494AE4CE",
}

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(r"[\u3040-\u30ff\uff66-\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
PRINTF_RE = re.compile(r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
RUNTIME_BRACKET_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PROFILE_KEYS = (
    "printf", "unknown_percent_count", "leading_whitespace", "trailing_whitespace",
    "esc", "esc_pair_family", "controls", "line_breaks", "pua", "runtime_brackets",
)


class MsgevP1Residual03Error(ValueError):
    """Raised when an immutable input or source-free conversion contract differs."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def pretty_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise MsgevP1Residual03Error(f"{label} differs from its exact contract")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        previous = folded.get(key.casefold())
        if previous is not None:
            raise MsgevP1Residual03Error(f"duplicate/case-colliding JSON key: {previous!r}/{key!r}")
        folded[key.casefold()] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MsgevP1Residual03Error(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise MsgevP1Residual03Error(f"JSON root is not an object: {path}")
    return value, blob


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise MsgevP1Residual03Error(f"required file is missing: {path}")
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def path_from_repo(relative: str) -> Path:
    value = Path(relative)
    if not relative or value.is_absolute() or ".." in value.parts or "\\" in relative:
        raise MsgevP1Residual03Error("repository-relative path is unsafe")
    path = (REPO / value).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError as exc:
        raise MsgevP1Residual03Error("repository-relative path escaped workspace") from exc
    return path


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
    finally:
        temporary.unlink(missing_ok=True)


def message_profile(text: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(text))
    printf_percent_offsets = {
        offset
        for match in printf_matches
        for offset in range(match.start(), match.end())
        if text[offset] == "%"
    }
    esc = [match.group(0) for match in ESC_RE.finditer(text)]
    esc_offsets = {
        offset for match in ESC_RE.finditer(text) for offset in range(match.start(), match.end())
    }
    return {
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, char in enumerate(text) if char == "%" and offset not in printf_percent_offsets
        ),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "esc": esc,
        "esc_pair_family": ["close" if value == "\x1bCZ" else "open" for value in esc],
        "controls": [
            f"U+{ord(char):04X}"
            for offset, char in enumerate(text)
            if unicodedata.category(char) == "Cc" and char not in ("\r", "\n") and offset not in esc_offsets
        ],
        "line_breaks": LINE_BREAK_RE.findall(text),
        "pua": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "runtime_brackets": RUNTIME_BRACKET_RE.findall(text),
    }


def profile_hash(profile: Mapping[str, Any]) -> str:
    return canonical_hash({key: profile[key] for key in PROFILE_KEYS})


def profile_mismatches(source: str, replacement: str) -> list[str]:
    before = message_profile(source)
    after = message_profile(replacement)
    return [key for key in PROFILE_KEYS if before[key] != after[key]]


def payload_without_skeleton(text: str) -> str:
    """Return Korean semantic payload for provenance hashing, not display."""

    value = ESC_RE.sub("", text)
    value = PRINTF_RE.sub("", value)
    value = RUNTIME_BRACKET_RE.sub("", value)
    value = LINE_BREAK_RE.sub("", value)
    return "".join(
        char
        for char in value
        if unicodedata.category(char) != "Cc" and not 0xE000 <= ord(char) <= 0xF8FF
    )


def payload_hash(text: str) -> str:
    return text_hash(payload_without_skeleton(text))


def validate_korean(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\0" in value or "\ufffd" in value:
        raise MsgevP1Residual03Error(f"unsafe Korean text: {label}")
    if CJK_OR_KANA_RE.search(value) or not HANGUL_RE.search(value):
        raise MsgevP1Residual03Error(f"Korean script contract differs: {label}")
    return value


def load_stock(stock_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    source_path = (stock_root.resolve() / Path(RESOURCE)).resolve()
    if not source_path.is_file():
        raise MsgevP1Residual03Error(f"v0.9 JP source is missing: {source_path}")
    packed = source_path.read_bytes()
    require_equal(
        {"packed_size": len(packed), "packed_sha256": sha256_bytes(packed)},
        {"packed_size": STOCK["packed_size"], "packed_sha256": STOCK["packed_sha256"]},
        "active v0.9 JP packed baseline",
    )
    _header, raw = decompress_wrapper(packed)
    require_equal(
        {"raw_size": len(raw), "raw_sha256": sha256_bytes(raw)},
        {"raw_size": STOCK["raw_size"], "raw_sha256": STOCK["raw_sha256"]},
        "active v0.9 JP raw baseline",
    )
    table = parse_message_table(raw)
    require_equal(table.string_count, STOCK["string_count"], "active v0.9 JP string count")
    if rebuild_message_table(table, table.texts) != raw:
        raise MsgevP1Residual03Error("unchanged v0.9 JP table cannot round-trip byte-identically")
    return source_path, packed, raw, table


def load_audit() -> tuple[list[int], dict[int, str]]:
    require_equal(file_spec(AUDIT_PATH), AUDIT_PIN, "active residual audit pin")
    document, _blob = read_json(AUDIT_PATH)
    bundles = document.get("recommended_parallel_bundles")
    if not isinstance(bundles, list):
        raise MsgevP1Residual03Error("audit bundle vector is missing")
    selected = [row for row in bundles if isinstance(row, dict) and row.get("bundle_id") == BUNDLE_ID]
    if len(selected) != 1:
        raise MsgevP1Residual03Error("P1-03 audit bundle is missing or duplicated")
    bundle = selected[0]
    if (
        bundle.get("resource") != RESOURCE
        or bundle.get("format") != "common"
        or bundle.get("classification") != "japanese_kana_no_hangul"
        or bundle.get("priority") != "P1"
    ):
        raise MsgevP1Residual03Error("P1-03 audit route differs")
    coordinates = bundle.get("coordinates")
    if not isinstance(coordinates, list):
        raise MsgevP1Residual03Error("P1-03 audit coordinates are missing")
    ids: list[int] = []
    for coordinate in coordinates:
        if not isinstance(coordinate, dict) or set(coordinate) != {"id"} or type(coordinate["id"]) is not int:
            raise MsgevP1Residual03Error("P1-03 audit coordinate schema differs")
        ids.append(coordinate["id"])
    if ids != sorted(set(ids)):
        raise MsgevP1Residual03Error("P1-03 audit coordinates are not sorted and unique")
    require_equal(len(ids), EXPECTED_AUDIT_COUNT, "P1-03 audit coordinate count")
    require_equal(canonical_hash([{ "id": entry_id } for entry_id in ids]), EXPECTED_AUDIT_SHA256, "P1-03 audit digest")
    require_equal(bundle.get("coordinate_count"), EXPECTED_AUDIT_COUNT, "P1-03 audit bundle count")
    require_equal(bundle.get("coordinate_sha256"), EXPECTED_AUDIT_SHA256, "P1-03 audit bundle digest")
    resource_rows = document.get("entries_by_resource", {}).get(RESOURCE)
    if not isinstance(resource_rows, list):
        raise MsgevP1Residual03Error("P1-03 audit resource rows are missing")
    source_hashes: dict[int, str] = {}
    for row in resource_rows:
        if not isinstance(row, dict):
            continue
        coordinate = row.get("coordinate")
        source_hash = row.get("active_utf16le_sha256")
        if isinstance(coordinate, dict) and type(coordinate.get("id")) is int and coordinate["id"] in ids:
            if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash):
                raise MsgevP1Residual03Error("audit source hash is malformed")
            source_hashes[coordinate["id"]] = source_hash
    require_equal(sorted(source_hashes), ids, "P1-03 audit source-hash coordinate coverage")
    for entry_id, expected_hash in RUNTIME_STRUCTURAL_KEYS.items():
        require_equal(source_hashes.get(entry_id), expected_hash, f"runtime structural source hash at {entry_id}")
    return ids, source_hashes


def checked_reference_inputs() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in DIRECT_CATALOGS:
        path = path_from_repo(str(item["relative_path"]))
        actual = file_spec(path)
        require_equal(actual, {"size": item["size"], "sha256": item["sha256"]}, f"direct catalog {item['relative_path']}")
        result.append({"role": "direct_jp_hash_catalog", "relative_path": item["relative_path"], **actual})
    for item in NATIVE_CATALOGS:
        for role in ("catalog", "evidence"):
            path = path_from_repo(str(item[role]))
            actual = file_spec(path)
            require_equal(
                actual,
                {"size": item[f"{role}_size"], "sha256": item[f"{role}_sha256"]},
                f"{item['name']} {role}",
            )
            result.append({"role": f"{item['name']}_{role}", "relative_path": item[role], **actual})
    return result


def _catalog_entries(document: Mapping[str, Any], label: str) -> dict[int, str]:
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise MsgevP1Residual03Error(f"catalog entries missing: {label}")
    result: dict[int, str] = {}
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get("id")) is not int:
            raise MsgevP1Residual03Error(f"catalog entry id is invalid: {label}")
        entry_id = entry["id"]
        korean = validate_korean(entry.get("ko"), f"{label}:{entry_id}")
        if entry_id in result and result[entry_id] != korean:
            raise MsgevP1Residual03Error(f"catalog id has conflicting Korean: {label}:{entry_id}")
        result[entry_id] = korean
    return result


def load_reference_indexes() -> tuple[dict[str, list[dict[str, Any]]], dict[tuple[str, int], dict[str, Any]], list[dict[str, Any]]]:
    """Load only pinned, committed Korean provenance into source-free indexes."""

    inputs = checked_reference_inputs()
    direct: dict[str, list[dict[str, Any]]] = {}
    for item in DIRECT_CATALOGS:
        relative = str(item["relative_path"])
        document, _blob = read_json(path_from_repo(relative))
        if document.get("resource") not in {"MSG/JP/ev_strdata.bin", RESOURCE}:
            raise MsgevP1Residual03Error("direct reuse catalog route differs")
        entries = document.get("entries")
        if not isinstance(entries, list):
            raise MsgevP1Residual03Error("direct reuse catalog entries are missing")
        for entry in entries:
            if not isinstance(entry, dict):
                raise MsgevP1Residual03Error("direct reuse catalog entry is invalid")
            source_hash = entry.get("source_jp_utf16le_sha256")
            korean = validate_korean(entry.get("ko"), f"{relative}:{entry.get('id', '?')}")
            if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash):
                raise MsgevP1Residual03Error("direct reuse source hash is invalid")
            direct.setdefault(source_hash, []).append(
                {
                    "kind": "committed_direct_jp_exact_source_hash_reuse",
                    "catalog": relative,
                    "catalog_entry_id": entry.get("id"),
                    "ko": korean,
                    "ko_utf16le_sha256": text_hash(korean),
                }
            )

    def load_aligned(item: Mapping[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
        catalog_path = str(item["catalog"])
        evidence_path = str(item["evidence"])
        catalog, _catalog_blob = read_json(path_from_repo(catalog_path))
        evidence, _evidence_blob = read_json(path_from_repo(evidence_path))
        korean_by_id = _catalog_entries(catalog, catalog_path)
        rows = evidence.get("entries")
        if not isinstance(rows, list):
            raise MsgevP1Residual03Error(f"alignment entries missing: {evidence_path}")
        result: dict[tuple[str, int], dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict) or type(row.get("id")) is not int:
                continue
            entry_id = row["id"]
            hashes = row.get("official_pk_utf16le_sha256")
            source_hash = hashes.get("JP") if isinstance(hashes, dict) else None
            if entry_id not in korean_by_id or not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash):
                continue
            key = (source_hash, entry_id)
            donor = {
                "kind": "committed_native_korean_semantic_payload",
                "catalog": catalog_path,
                "evidence": evidence_path,
                "catalog_entry_id": entry_id,
                "ko": korean_by_id[entry_id],
                "ko_utf16le_sha256": text_hash(korean_by_id[entry_id]),
            }
            previous = result.get(key)
            if previous is not None and previous != donor:
                raise MsgevP1Residual03Error(f"aligned provenance collision: {item['name']}:{entry_id}")
            result[key] = donor
        return result

    native: dict[tuple[str, int], dict[str, Any]] = {}
    for item in NATIVE_CATALOGS:
        for key, donor in load_aligned(item).items():
            previous = native.get(key)
            if previous is not None and previous != donor:
                raise MsgevP1Residual03Error(f"native provenance collision at {key[1]}")
            native[key] = donor
    return direct, native, inputs


def _single_direct_donor(direct: Mapping[str, Sequence[Mapping[str, Any]]], source_hash: str, entry_id: int) -> dict[str, Any] | None:
    choices = direct.get(source_hash, ())
    variants = {str(value["ko"]): value for value in choices}
    if not variants:
        return None
    if len(variants) != 1:
        raise MsgevP1Residual03Error(f"ambiguous direct Korean provenance at {entry_id}")
    return dict(next(iter(variants.values())))


def _special_direct_donor(direct: Mapping[str, Sequence[Mapping[str, Any]]], source_hash: str, entry_id: int) -> dict[str, Any]:
    catalog, catalog_entry_id = SPECIAL_DIRECT_DONORS[entry_id]
    matches = [
        value
        for value in direct.get(source_hash, ())
        if value.get("catalog") == catalog and value.get("catalog_entry_id") == catalog_entry_id
    ]
    if len(matches) != 1:
        raise MsgevP1Residual03Error(f"special direct donor is missing or ambiguous at {entry_id}")
    return dict(matches[0])


def select_donors(table: MessageTable) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    ids, audit_hashes = load_audit()
    direct, native, _inputs = load_reference_indexes()
    donors: list[dict[str, Any]] = []
    runtime_holds: list[dict[str, Any]] = []
    for entry_id in ids:
        if not 0 <= entry_id < table.string_count:
            raise MsgevP1Residual03Error(f"audit coordinate lies outside message table: {entry_id}")
        source = table.texts[entry_id]
        source_hash = text_hash(source)
        require_equal(source_hash, audit_hashes[entry_id], f"active v0.9 source hash at {entry_id}")
        source_profile = message_profile(source)
        if entry_id in RUNTIME_STRUCTURAL_KEYS:
            runtime_holds.append(
                {
                    "id": entry_id,
                    "source_jp_utf16le_sha256": source_hash,
                    "classification": "runtime_custom_bracket_substitution_preserved",
                    "reason_codes": ["runtime_custom_bracket_substitution", "preserve_active_utf16le_payload"],
                    "source_token_profile": source_profile,
                    "source_token_profile_sha256": profile_hash(source_profile),
                }
            )
            continue
        if entry_id in SPECIAL_DIRECT_DONORS:
            donor = _special_direct_donor(direct, source_hash, entry_id)
        elif entry_id in SPECIAL_NATIVE_DONORS:
            donor_id = SPECIAL_NATIVE_DONORS[entry_id]
            donor = native.get((source_hash, donor_id))
            if donor is None:
                raise MsgevP1Residual03Error(f"special exact native donor is missing at {entry_id}")
            donor = {**donor, "kind": "native_exact_source_hash_format_resolved_payload", "target_id": entry_id}
        else:
            donor = _single_direct_donor(direct, source_hash, entry_id)
            if donor is None:
                donor = native.get((source_hash, entry_id))
                if donor is None:
                    raise MsgevP1Residual03Error(f"no committed Korean provenance at {entry_id}")
        korean = validate_korean(donor["ko"], f"selected donor:{entry_id}")
        donors.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": source_hash,
                "source": source,
                "source_profile": source_profile,
                "ko": korean,
                "input_profile": message_profile(korean),
                "provenance": {key: value for key, value in donor.items() if key != "ko"},
            }
        )
    require_equal(len(donors), 180, "Korean donor count")
    require_equal(len(runtime_holds), EXPECTED_RUNTIME_PRESERVATION_COUNT, "runtime preservation count")
    return donors, runtime_holds, [
        {"id": entry_id, "source_jp_utf16le_sha256": audit_hashes[entry_id]} for entry_id in ids
    ]


def can_rebase_esc(source_profile: Mapping[str, Any], input_profile: Mapping[str, Any]) -> bool:
    mismatches = [key for key in PROFILE_KEYS if source_profile[key] != input_profile[key]]
    return (
        mismatches == ["esc"]
        and len(source_profile["esc"]) == len(input_profile["esc"])
        and source_profile["esc_pair_family"] == input_profile["esc_pair_family"]
        and source_profile["runtime_brackets"] == input_profile["runtime_brackets"]
    )


def rebase_esc_lexemes(korean: str, source_profile: Mapping[str, Any]) -> str:
    expected = iter(source_profile["esc"])
    count = 0

    def replace(_: re.Match[str]) -> str:
        nonlocal count
        count += 1
        try:
            return next(expected)
        except StopIteration as exc:
            raise MsgevP1Residual03Error("ESC rebase had too many donor lexemes") from exc

    converted = ESC_RE.sub(replace, korean)
    try:
        next(expected)
    except StopIteration:
        pass
    else:
        raise MsgevP1Residual03Error("ESC rebase had too few donor lexemes")
    require_equal(count, len(source_profile["esc"]), "ESC rebase lexeme count")
    return converted


def hold_reasons(source_profile: Mapping[str, Any], input_profile: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if source_profile["line_breaks"] != input_profile["line_breaks"]:
        reasons.append("linebreak_contract_requires_manual_placement_review")
    if len(source_profile["esc"]) != len(input_profile["esc"]):
        reasons.append("esc_lexeme_count_requires_manual_entity_review")
    elif source_profile["esc_pair_family"] != input_profile["esc_pair_family"]:
        reasons.append("esc_pair_order_requires_manual_entity_review")
    if source_profile["runtime_brackets"] != input_profile["runtime_brackets"]:
        reasons.append("runtime_bracket_contract_requires_manual_entity_review")
    for key in ("printf", "unknown_percent_count", "leading_whitespace", "trailing_whitespace", "controls", "pua"):
        if source_profile[key] != input_profile[key]:
            reasons.append(f"{key}_contract_requires_manual_review")
    if not reasons:
        reasons.append("semantic_context_requires_manual_review")
    return reasons


def resolve_safe_entries(table: MessageTable) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    donors, runtime_holds, _audit_rows = select_donors(table)
    entries: list[dict[str, Any]] = []
    manual_holds: list[dict[str, Any]] = []
    literal = 0
    rebased = 0
    for donor in donors:
        entry_id = int(donor["id"])
        source = str(donor["source"])
        input_ko = str(donor["ko"])
        source_profile = donor["source_profile"]
        input_profile = donor["input_profile"]
        mismatches = profile_mismatches(source, input_ko)
        output_ko: str | None = None
        operation: str | None = None
        if not mismatches:
            output_ko = input_ko
            literal += 1
            operation = "literal_committed_korean_reuse"
        elif can_rebase_esc(source_profile, input_profile):
            output_ko = rebase_esc_lexemes(input_ko, source_profile)
            require_equal(payload_hash(output_ko), payload_hash(input_ko), f"ESC rebase semantic payload at {entry_id}")
            require_equal(message_profile(output_ko), source_profile, f"ESC rebase source profile at {entry_id}")
            rebased += 1
            operation = "replace_equal_length_esc_lexemes_in_target_order"
        if output_ko is None:
            manual_holds.append(
                {
                    "id": entry_id,
                    "source_jp_utf16le_sha256": donor["source_jp_utf16le_sha256"],
                    "classification": "manual_review_hold",
                    "reason_codes": hold_reasons(source_profile, input_profile),
                    "source_token_profile": source_profile,
                    "source_token_profile_sha256": profile_hash(source_profile),
                    "provenance": {
                        **donor["provenance"],
                        "input_ko_utf16le_sha256": text_hash(input_ko),
                        "input_semantic_payload_utf16le_sha256": payload_hash(input_ko),
                        "input_token_profile_sha256": profile_hash(input_profile),
                    },
                }
            )
            continue
        output_profile = message_profile(output_ko)
        require_equal(output_profile, source_profile, f"selected source profile at {entry_id}")
        provenance = {
            **donor["provenance"],
            "operation": operation,
            "input_ko_utf16le_sha256": text_hash(input_ko),
            "input_semantic_payload_utf16le_sha256": payload_hash(input_ko),
            "input_token_profile_sha256": profile_hash(input_profile),
        }
        entries.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": donor["source_jp_utf16le_sha256"],
                "ko": output_ko,
                "ko_utf16le_sha256": text_hash(output_ko),
                "source_token_profile_sha256": profile_hash(source_profile),
                "provenance": provenance,
            }
        )
    require_equal(literal, EXPECTED_LITERAL_COUNT, "literal reuse count")
    require_equal(rebased, EXPECTED_ESC_REBASED_COUNT, "ESC rebase count")
    require_equal(len(entries), EXPECTED_APPLIED_COUNT, "safe overlay entry count")
    require_equal(len(manual_holds), EXPECTED_MANUAL_REVIEW_HOLD_COUNT, "manual review hold count")
    if [entry["id"] for entry in entries] != sorted(entry["id"] for entry in entries):
        raise MsgevP1Residual03Error("safe overlay entries are not sorted")
    return entries, manual_holds, runtime_holds


def validate_entries(table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    required = {
        "id", "source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256", "source_token_profile_sha256", "provenance",
    }
    expected, _manual_holds, _runtime_holds = resolve_safe_entries(table)
    if len(entries) != len(expected):
        raise MsgevP1Residual03Error("safe overlay entry count differs")
    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping) or set(entry) != required:
            raise MsgevP1Residual03Error(f"safe overlay entry schema differs at index {index}")
        entry_id = entry["id"]
        if type(entry_id) is not int or not 0 <= entry_id < table.string_count:
            raise MsgevP1Residual03Error(f"safe overlay id is invalid at index {index}")
        source = table.texts[entry_id]
        korean = validate_korean(entry["ko"], f"safe overlay:{entry_id}")
        if not all(isinstance(entry[key], str) and HEX64_RE.fullmatch(entry[key]) for key in (
            "source_jp_utf16le_sha256", "ko_utf16le_sha256", "source_token_profile_sha256"
        )):
            raise MsgevP1Residual03Error(f"safe overlay hash is invalid at {entry_id}")
        require_equal(text_hash(source), entry["source_jp_utf16le_sha256"], f"safe overlay source hash at {entry_id}")
        require_equal(text_hash(korean), entry["ko_utf16le_sha256"], f"safe overlay Korean hash at {entry_id}")
        require_equal(profile_hash(message_profile(source)), entry["source_token_profile_sha256"], f"safe overlay profile hash at {entry_id}")
        require_equal(message_profile(korean), message_profile(source), f"safe overlay profile at {entry_id}")
        if not isinstance(entry["provenance"], Mapping):
            raise MsgevP1Residual03Error(f"safe overlay provenance is invalid at {entry_id}")
        normalized.append(dict(entry))
    require_equal(normalized, expected, "safe overlay exact pinned donor resolution")
    return normalized


def make_overlay(entries: Sequence[Mapping[str, Any]], manual_holds: Sequence[Mapping[str, Any]], runtime_holds: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    _ids, _hashes = load_audit()
    inputs = checked_reference_inputs()
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msgev_ko_steam_jp_p1_residual_03_safe_157.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "sc_container_used": False,
        },
        "active_v090_baseline": dict(STOCK),
        "audit_bundle": {
            "bundle_id": BUNDLE_ID,
            "audit_sha256": AUDIT_PIN["sha256"],
            "coordinate_count": EXPECTED_AUDIT_COUNT,
            "coordinate_sha256": EXPECTED_AUDIT_SHA256,
        },
        "selection": {
            "korean_donor_count": 180,
            "literal_reuse_count": EXPECTED_LITERAL_COUNT,
            "esc_rebased_count": EXPECTED_ESC_REBASED_COUNT,
            "applied_entry_count": len(entries),
            "manual_review_hold_count": len(manual_holds),
            "runtime_preservation_count": len(runtime_holds),
            "applied_coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
        },
        "reference_inputs": inputs,
        "entry_count": len(entries),
        "coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
        "entries": [dict(entry) for entry in entries],
    }


def validate_public_overlay(value: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    required = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy", "active_v090_baseline",
        "audit_bundle", "selection", "reference_inputs", "entry_count", "coordinate_sha256", "entries",
    }
    if set(value) != required or value.get("schema") != OVERLAY_SCHEMA:
        raise MsgevP1Residual03Error("public overlay schema differs")
    if value.get("overlay_id") != "msgev_ko_steam_jp_p1_residual_03_safe_157.v1" or value.get("resource") != RESOURCE:
        raise MsgevP1Residual03Error("public overlay route differs")
    if value.get("base_language") != "JP" or value.get("active_v090_baseline") != STOCK:
        raise MsgevP1Residual03Error("public overlay baseline differs")
    if value.get("distribution_policy") != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "sc_container_used": False,
    }:
        raise MsgevP1Residual03Error("public overlay distribution policy differs")
    if value.get("audit_bundle") != {
        "bundle_id": BUNDLE_ID,
        "audit_sha256": AUDIT_PIN["sha256"],
        "coordinate_count": EXPECTED_AUDIT_COUNT,
        "coordinate_sha256": EXPECTED_AUDIT_SHA256,
    }:
        raise MsgevP1Residual03Error("public overlay audit contract differs")
    require_equal(value.get("reference_inputs"), checked_reference_inputs(), "public overlay reference inputs")
    raw_entries = value.get("entries")
    if not isinstance(raw_entries, list) or value.get("entry_count") != len(raw_entries):
        raise MsgevP1Residual03Error("public overlay entry vector differs")
    entries = validate_entries(table, raw_entries)
    selection = value.get("selection")
    if selection != {
        "korean_donor_count": 180,
        "literal_reuse_count": EXPECTED_LITERAL_COUNT,
        "esc_rebased_count": EXPECTED_ESC_REBASED_COUNT,
        "applied_entry_count": EXPECTED_APPLIED_COUNT,
        "manual_review_hold_count": EXPECTED_MANUAL_REVIEW_HOLD_COUNT,
        "runtime_preservation_count": EXPECTED_RUNTIME_PRESERVATION_COUNT,
        "applied_coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
    }:
        raise MsgevP1Residual03Error("public overlay selection contract differs")
    require_equal(value.get("coordinate_sha256"), canonical_hash([{ "id": entry["id"] } for entry in entries]), "public overlay coordinate digest")
    return entries


def candidate_from_entries(packed: bytes, raw: bytes, table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> tuple[bytes, bytes, list[int]]:
    selected = validate_entries(table, entries)
    selected_ids = {int(entry["id"]) for entry in selected}
    texts = list(table.texts)
    changed: list[int] = []
    for entry in selected:
        entry_id = int(entry["id"])
        korean = str(entry["ko"])
        if texts[entry_id] != korean:
            changed.append(entry_id)
        texts[entry_id] = korean
    raw_a = rebuild_message_table(table, texts)
    raw_b = rebuild_message_table(table, texts)
    require_equal(raw_a, raw_b, "deterministic raw rebuild")
    packed_a = recompress_wrapper(raw_a, packed)
    packed_b = recompress_wrapper(raw_b, packed)
    require_equal(packed_a, packed_b, "deterministic packed rebuild")
    _header, checked_raw = decompress_wrapper(packed_a)
    checked = parse_message_table(checked_raw)
    require_equal(checked_raw, raw_a, "candidate decompression")
    require_equal(checked.texts, tuple(texts), "candidate parser text round-trip")
    if rebuild_message_table(checked, checked.texts) != checked_raw:
        raise MsgevP1Residual03Error("candidate parse/rebuild differs")
    for entry_id, source in enumerate(table.texts):
        if checked.texts[entry_id] != texts[entry_id]:
            raise MsgevP1Residual03Error(f"candidate text differs at {entry_id}")
        if entry_id not in selected_ids:
            if source.encode("utf-16le") + b"\0\0" != checked.texts[entry_id].encode("utf-16le") + b"\0\0":
                raise MsgevP1Residual03Error(f"nonselected UTF-16LE payload differs at {entry_id}")
    for entry_id in RUNTIME_STRUCTURAL_KEYS:
        require_equal(checked.texts[entry_id], table.texts[entry_id], f"runtime structural payload at {entry_id}")
    if (
        checked.string_count != table.string_count
        or checked.block_offset != table.block_offset
        or checked.table_offset != table.table_offset
        or checked.table_size != table.table_size
        or checked.string_start != table.string_start
    ):
        raise MsgevP1Residual03Error("candidate message table structure differs")
    stock_prefix = bytearray(raw[: table.table_offset])
    candidate_prefix = bytearray(checked_raw[: checked.table_offset])
    struct.pack_into("<I", stock_prefix, 8, 0)
    struct.pack_into("<I", candidate_prefix, 8, 0)
    require_equal(stock_prefix, candidate_prefix, "opaque prefix except logical size")
    require_equal(changed, [entry["id"] for entry in selected], "effective changed coordinate vector")
    return packed_a, raw_a, changed


def transformed_validation_rows(table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in entries:
        provenance = entry["provenance"]
        if provenance.get("operation") != "replace_equal_length_esc_lexemes_in_target_order":
            continue
        entry_id = int(entry["id"])
        source_profile = message_profile(table.texts[entry_id])
        input_profile_hash = provenance["input_token_profile_sha256"]
        rows.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": entry["source_jp_utf16le_sha256"],
                "provenance": {
                    "kind": provenance["kind"],
                    "catalog": provenance["catalog"],
                    "evidence": provenance.get("evidence"),
                    "catalog_entry_id": provenance["catalog_entry_id"],
                },
                "operation": provenance["operation"],
                "source_token_profile": source_profile,
                "source_token_profile_sha256": profile_hash(source_profile),
                "input_token_profile_sha256": input_profile_hash,
                "input_ko_utf16le_sha256": provenance["input_ko_utf16le_sha256"],
                "input_semantic_payload_utf16le_sha256": provenance["input_semantic_payload_utf16le_sha256"],
                "output_ko_utf16le_sha256": entry["ko_utf16le_sha256"],
                "output_semantic_payload_utf16le_sha256": payload_hash(entry["ko"]),
                "output_token_profile": message_profile(entry["ko"]),
                "output_token_profile_sha256": profile_hash(message_profile(entry["ko"])),
            }
        )
    require_equal(len(rows), EXPECTED_ESC_REBASED_COUNT, "transformed validation row count")
    return rows


def special_donor_validation_rows(table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_id = {int(entry["id"]): entry for entry in entries}
    required_ids = tuple(sorted(SPECIAL_DONOR_REASONS))
    if set(required_ids) != set(SPECIAL_DIRECT_DONORS) | set(SPECIAL_NATIVE_DONORS):
        raise MsgevP1Residual03Error("special donor policy IDs differ")
    rows: list[dict[str, Any]] = []
    for entry_id in required_ids:
        entry = by_id.get(entry_id)
        if entry is None:
            raise MsgevP1Residual03Error(f"special donor was not applied: {entry_id}")
        provenance = entry["provenance"]
        rows.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": entry["source_jp_utf16le_sha256"],
                "ko_utf16le_sha256": entry["ko_utf16le_sha256"],
                "source_token_profile_sha256": profile_hash(message_profile(table.texts[entry_id])),
                "review_basis": SPECIAL_DONOR_REASONS[entry_id],
                "provenance": {
                    "kind": provenance["kind"],
                    "catalog": provenance["catalog"],
                    "evidence": provenance.get("evidence"),
                    "catalog_entry_id": provenance["catalog_entry_id"],
                },
            }
        )
    return rows


def make_validation(table: MessageTable, entries: Sequence[Mapping[str, Any]], manual_holds: Sequence[Mapping[str, Any]], runtime_holds: Sequence[Mapping[str, Any]], candidate: bytes, candidate_raw: bytes, changed: Sequence[int]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v090_baseline": dict(STOCK),
        "audit_bundle": {
            "bundle_id": BUNDLE_ID,
            "coordinate_count": EXPECTED_AUDIT_COUNT,
            "coordinate_sha256": EXPECTED_AUDIT_SHA256,
        },
        "counts": {
            "korean_donor_count": 180,
            "literal_reuse_count": EXPECTED_LITERAL_COUNT,
            "esc_rebased_count": EXPECTED_ESC_REBASED_COUNT,
            "applied_entry_count": len(entries),
            "manual_review_hold_count": len(manual_holds),
            "runtime_preservation_count": len(runtime_holds),
        },
        "expected_candidate": {
            "packed_size": len(candidate),
            "packed_sha256": sha256_bytes(candidate),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256_bytes(candidate_raw),
            "string_count": STOCK["string_count"],
        },
        "effective_change_count": len(changed),
        "effective_change_coordinate_sha256": canonical_hash([{ "id": entry_id } for entry_id in changed]),
        "transformed_entries": transformed_validation_rows(table, entries),
        "special_exact_donor_evidence": special_donor_validation_rows(table, entries),
        "manual_review_holds": [dict(value) for value in manual_holds] + [dict(value) for value in runtime_holds],
        "checks": {
            "active_v090_baseline_pinned": True,
            "audit_coordinate_scope_exact": True,
            "per_entry_jp_source_hash_gated": True,
            "committed_korean_provenance_pinned": True,
            "literal_reuse_and_esc_rebase_partitioned": True,
            "equal_length_esc_pair_family_only": True,
            "linebreak_or_bracket_ambiguity_held": True,
            "runtime_custom_bracket_substitution_preserved": True,
            "source_token_profiles_preserved": True,
            "nonselected_utf16le_payloads_preserved": True,
            "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True,
            "steam_installation_written": False,
            "sc_container_used": False,
            "release_asset_written": False,
            "github_written": False,
        },
    }


def make_contract(overlay_blob: bytes, validation_blob: bytes, validation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "runtime_route": {"language": "JP", "sc_container_used": False, "installed_game_file_written": False},
        "active_v090_baseline": dict(STOCK),
        "audit_bundle": {"bundle_id": BUNDLE_ID, "coordinate_sha256": EXPECTED_AUDIT_SHA256},
        "overlay": {
            "relative_path": "workstreams/steam_jp_msgev_p1_residual_03_v1/public/msgev_ko_steam_jp_p1_residual_03_safe_157.v1.json",
            "sha256": sha256_bytes(overlay_blob),
            "entry_count": EXPECTED_APPLIED_COUNT,
        },
        "validation": {
            "relative_path": "workstreams/steam_jp_msgev_p1_residual_03_v1/validation.v1.json",
            "sha256": sha256_bytes(validation_blob),
        },
        "expected_candidate": dict(validation["expected_candidate"]),
        "safe_partition": {
            "literal_reuse_count": EXPECTED_LITERAL_COUNT,
            "esc_rebased_count": EXPECTED_ESC_REBASED_COUNT,
            "manual_review_hold_count": EXPECTED_MANUAL_REVIEW_HOLD_COUNT,
            "runtime_preservation_count": EXPECTED_RUNTIME_PRESERVATION_COUNT,
        },
        "output_policy": {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE},
        "proofs": {
            "active_v090_baseline_pinned": True,
            "committed_korean_provenance_source_hash_gated": True,
            "literal_and_safe_esc_rebase_only": True,
            "unsafe_structural_rows_held": True,
            "runtime_custom_bracket_rows_preserved": True,
            "source_token_profiles_preserved": True,
            "nonselected_utf16le_payloads_preserved": True,
            "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True,
            "steam_installation_read_only": True,
        },
    }


def assert_source_free(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise MsgevP1Residual03Error(f"artifact is not JP-route source-free: {path}")


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO / "tmp").resolve()
    try:
        resolved.relative_to(private_root)
    except ValueError as exc:
        raise MsgevP1Residual03Error("candidate output must stay below KR_PATCH_WORK/tmp") from exc
    if resolved == private_root:
        raise MsgevP1Residual03Error("KR_PATCH_WORK/tmp itself cannot be a candidate root")
    return resolved


def freeze(stock_root: Path) -> dict[str, Any]:
    _source_path, packed, raw, table = load_stock(stock_root)
    entries, manual_holds, runtime_holds = resolve_safe_entries(table)
    entries = validate_entries(table, entries)
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries)
    overlay_blob = pretty_bytes(make_overlay(entries, manual_holds, runtime_holds))
    validation = make_validation(table, entries, manual_holds, runtime_holds, candidate, candidate_raw, changed)
    validation_blob = pretty_bytes(validation)
    contract = make_contract(overlay_blob, validation_blob, validation)
    atomic_write(PUBLIC_OVERLAY, overlay_blob)
    atomic_write(VALIDATION, validation_blob)
    atomic_write(CONTRACT, pretty_bytes(contract))
    for path in (PUBLIC_OVERLAY, VALIDATION, CONTRACT):
        assert_source_free(path)
    return {
        "applied_entry_count": len(entries),
        "literal_reuse_count": EXPECTED_LITERAL_COUNT,
        "esc_rebased_count": EXPECTED_ESC_REBASED_COUNT,
        "manual_review_hold_count": len(manual_holds),
        "runtime_preservation_count": len(runtime_holds),
        "candidate_sha256": sha256_bytes(candidate),
        "candidate_raw_sha256": sha256_bytes(candidate_raw),
        "installed_game_file_modified": False,
    }


def load_frozen_inputs(stock_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], bytes, bytes, MessageTable]:
    source_path, packed, raw, table = load_stock(stock_root)
    contract, _contract_blob = read_json(CONTRACT)
    required = {
        "schema", "source_free", "contains_commercial_source_text", "contains_complete_game_resource", "resource",
        "runtime_route", "active_v090_baseline", "audit_bundle", "overlay", "validation", "expected_candidate",
        "safe_partition", "output_policy", "proofs",
    }
    if set(contract) != required or contract.get("schema") != CONTRACT_SCHEMA or contract.get("resource") != RESOURCE:
        raise MsgevP1Residual03Error("frozen contract schema/route differs")
    require_equal(contract.get("runtime_route"), {"language": "JP", "sc_container_used": False, "installed_game_file_written": False}, "frozen runtime route")
    require_equal(contract.get("active_v090_baseline"), STOCK, "frozen baseline")
    require_equal(contract.get("audit_bundle"), {"bundle_id": BUNDLE_ID, "coordinate_sha256": EXPECTED_AUDIT_SHA256}, "frozen audit")
    require_equal(contract.get("safe_partition"), {
        "literal_reuse_count": EXPECTED_LITERAL_COUNT,
        "esc_rebased_count": EXPECTED_ESC_REBASED_COUNT,
        "manual_review_hold_count": EXPECTED_MANUAL_REVIEW_HOLD_COUNT,
        "runtime_preservation_count": EXPECTED_RUNTIME_PRESERVATION_COUNT,
    }, "frozen safe partition")
    require_equal(contract.get("output_policy"), {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE}, "frozen output policy")
    if not isinstance(contract.get("proofs"), dict) or any(value is not True for value in contract["proofs"].values()):
        raise MsgevP1Residual03Error("frozen proof set differs")
    overlay_path = path_from_repo(str(contract["overlay"].get("relative_path", "")))
    overlay, overlay_blob = read_json(overlay_path)
    require_equal(sha256_bytes(overlay_blob), contract["overlay"].get("sha256"), "frozen public overlay hash")
    entries = validate_public_overlay(overlay, table)
    validation_path = path_from_repo(str(contract["validation"].get("relative_path", "")))
    validation, validation_blob = read_json(validation_path)
    require_equal(sha256_bytes(validation_blob), contract["validation"].get("sha256"), "frozen validation hash")
    require_equal(validation.get("expected_candidate"), contract.get("expected_candidate"), "frozen validation candidate")
    holds = validation.get("manual_review_holds")
    if not isinstance(holds, list) or len(holds) != EXPECTED_MANUAL_REVIEW_HOLD_COUNT + EXPECTED_RUNTIME_PRESERVATION_COUNT:
        raise MsgevP1Residual03Error("frozen manual-review hold vector differs")
    for path in (overlay_path, validation_path, CONTRACT):
        assert_source_free(path)
    if source_path != (stock_root.resolve() / Path(RESOURCE)).resolve():
        raise MsgevP1Residual03Error("unexpected v0.9 source path")
    return contract, entries, packed, raw, table


def build_staging_candidate(stock_root: Path, output_root: Path) -> dict[str, Any]:
    output = require_private_output_root(output_root)
    source_path, stock_before, _raw_before, _table_before = load_stock(stock_root)
    contract, entries, packed, raw, table = load_frozen_inputs(stock_root)
    require_equal(packed, stock_before, "v0.9 JP source while loading frozen inputs")
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries)
    observed = {
        "packed_size": len(candidate),
        "packed_sha256": sha256_bytes(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256_bytes(candidate_raw),
        "string_count": table.string_count,
    }
    require_equal(observed, contract["expected_candidate"], "candidate versus frozen contract")
    target = (output / Path(RESOURCE)).resolve()
    try:
        target.relative_to(output)
    except ValueError as exc:
        raise MsgevP1Residual03Error("candidate target escaped private output root") from exc
    if target == source_path:
        raise MsgevP1Residual03Error("refusing to target source baseline")
    atomic_write(target, candidate)
    require_equal(target.read_bytes(), candidate, "written private candidate")
    require_equal(source_path.read_bytes(), stock_before, "v0.9 JP source after private build")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v090_baseline": dict(STOCK),
        "target": observed,
        "applied_entry_count": len(entries),
        "effective_change_count": len(changed),
        "coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
        "effective_change_coordinate_sha256": canonical_hash([{ "id": entry_id } for entry_id in changed]),
        "output": {"relative_path": RESOURCE, "complete_candidate_private_only": True, "installed_game_file_modified": False},
        "checks": {"contract_hash": "OK", "source_hash_gates": "OK", "token_profiles": "OK", "source_unchanged": "OK"},
    }
    atomic_write(output / "build_manifest.v1.json", pretty_bytes(manifest))
    return {"candidate_path": str(target), "manifest_path": str(output / "build_manifest.v1.json"), **observed, "installed_game_file_modified": False}


def verify(stock_root: Path) -> dict[str, Any]:
    contract, entries, packed, raw, table = load_frozen_inputs(stock_root)
    first, first_raw, changed = candidate_from_entries(packed, raw, table, entries)
    second, second_raw, changed_second = candidate_from_entries(packed, raw, table, entries)
    require_equal(first, second, "deterministic candidate A/B")
    require_equal(first_raw, second_raw, "deterministic raw A/B")
    require_equal(changed, changed_second, "deterministic changed IDs A/B")
    require_equal({
        "packed_size": len(first), "packed_sha256": sha256_bytes(first),
        "raw_size": len(first_raw), "raw_sha256": sha256_bytes(first_raw), "string_count": table.string_count,
    }, contract["expected_candidate"], "verified candidate versus frozen contract")
    return {"status": "PASS", "applied_entry_count": len(entries), "candidate_sha256": sha256_bytes(first), "output_written": False}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (("freeze", "write source-free overlay, validation, and contract"), ("build", "write only a private staging candidate"), ("verify", "recompute the frozen candidate without writing a resource")):
        item = commands.add_parser(command, help=help_text)
        item.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if command == "build":
            item.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "freeze":
            result = freeze(args.stock_root)
        elif args.command == "build":
            result = build_staging_candidate(args.stock_root, args.output_root)
        else:
            result = verify(args.stock_root)
    except (MsgevP1Residual03Error, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
