#!/usr/bin/env python3
"""Freeze a source-free manual-layout overlay for Steam JP v0.9 msgev.

This workstream resolves the 23 P1-03 rows intentionally held by the
safe-157 overlay. The public artifacts contain only Korean payloads, hashes,
token profiles, and provenance. A complete resource is reconstructed only
below KR_PATCH_WORK/tmp.

The 21 line-layout rows preserve the Korean donor semantic payload exactly;
only the line-break layout and the source ESC lexeme stream are rebuilt. The
two entity-layout rows use explicit Korean-only templates and are checked
against the exact source token skeleton. No Switch same-index payload is
loaded by this builder.
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
from collections import Counter
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
AUDIT_PATH = (
    REPO
    / "workstreams"
    / "jp_active_message_residual_audit_v1"
    / "public"
    / "active_jp_remaining_coordinates.v1.json"
)
DEFAULT_STOCK_ROOT = REPO / "tmp" / "steam_jp_msgev_p1_residual_03_v1" / "stock_v090"
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_msgev_p1_residual_03_manual_layout_v1" / "candidate"
PUBLIC_OVERLAY = WORKSTREAM / "public" / "msgev_ko_steam_jp_p1_residual_03_manual_layout_23.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
CONTRACT = WORKSTREAM / "source_free_contract.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-03-manual-layout-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-03-manual-layout-validation.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-03-manual-layout-contract.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-03-manual-layout-build-manifest.v1"

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
BUNDLE_COORDINATE_SHA256 = "0245195E033DAA4F5E74D8A73CAE3624D16A751AC4D87B11CE7A1DD4F7FEE204"

MANUAL_IDS = (
    8466,
    9796,
    9820,
    9822,
    9823,
    9825,
    9857,
    9890,
    9948,
    9980,
    10008,
    10101,
    10114,
    10181,
    10186,
    10421,
    10475,
    10574,
    10689,
    10810,
    10820,
    10876,
    10887,
)
SPECIAL_ENTITY_IDS = (10421, 10475)
LINE_LAYOUT_IDS = tuple(entry_id for entry_id in MANUAL_IDS if entry_id not in SPECIAL_ENTITY_IDS)
RUNTIME_PRESERVATION_IDS = (10837, 10840, 10905)

DONOR_GROUPS: tuple[dict[str, Any], ...] = (
    {
        "name": "native_02",
        "catalog": "workstreams/msgev_pk_native_batch02/public/msgev_ko_pk_native_batch02_150.v1.json",
        "catalog_size": 44_261,
        "catalog_sha256": "642E5B0B7503B5CCA6472CE10E4066296C6D8F6DA8DD8BC2B16EDA7BEC554367",
        "evidence": "workstreams/msgev_pk_native_batch02/evidence/msgev_pk_native_batch02_alignment.v1.json",
        "evidence_size": 256_131,
        "evidence_sha256": "1EC3875BE00EF41B5EDE9E9E0C68A68B32CF1FD42BDB7DDEB6B80E85FB0BF0E7",
        "ids": (8466, 9796, 9820, 9822, 9823, 9825, 9857, 9890),
    },
    {
        "name": "native_03",
        "catalog": "workstreams/msgev_pk_native_batch03/public/msgev_ko_pk_native_batch03_350.v1.json",
        "catalog_size": 98_344,
        "catalog_sha256": "B66294BB02F553591F9AA5F123AD2EBC4E937692DA0364F0FB17090F25C1DD07",
        "evidence": "workstreams/msgev_pk_native_batch03/evidence/msgev_pk_native_batch03_alignment.v1.json",
        "evidence_size": 473_507,
        "evidence_sha256": "17206EFA3AA87B3A1916A88DC969DBA81A806B45A5FFE8B4379327F85613724B",
        "ids": (9948, 9980, 10008, 10101, 10114, 10181, 10186),
    },
    {
        "name": "native_04",
        "catalog": "workstreams/msgev_pk_native_batch04/public/msgev_ko_pk_native_batch04_175.v1.json",
        "catalog_size": 50_889,
        "catalog_sha256": "90C1220FC4D40F218C70A01813B0A993AA61C365DC49A2649592528F0AD2F4BA",
        "evidence": "workstreams/msgev_pk_native_batch04/evidence/msgev_pk_native_batch04_alignment.v1.json",
        "evidence_size": 285_699,
        "evidence_sha256": "DED74F23A56C9D430295038C3C2D9828A9F93B84A539A865B7E9611F0D630505",
        "ids": (10421,),
    },
    {
        "name": "native_05",
        "catalog": "workstreams/msgev_pk_native_batch05/public/msgev_ko_pk_native_batch05_300.v1.json",
        "catalog_size": 84_002,
        "catalog_sha256": "CED113C16D01202BEB63B7F66B62BDFA8478149313C2A20A539FB2B4EF599EC2",
        "evidence": "workstreams/msgev_pk_native_batch05/evidence/msgev_pk_native_batch05_alignment.v1.json",
        "evidence_size": 424_514,
        "evidence_sha256": "8EB47E12E552A4DDD669E3670ACD7E10A9165017A9C1EC10CBD98F4AAA656FF5",
        "ids": (10475, 10574, 10689),
    },
    {
        "name": "native_06",
        "catalog": "workstreams/msgev_pk_native_batch06/public/msgev_ko_pk_native_batch06_260.v1.json",
        "catalog_size": 60_342,
        "catalog_sha256": "94DAF36792E1BCAC12DDB5658DA91785B487D825939E2D7C94D381751C2D0BFF",
        "evidence": "workstreams/msgev_pk_native_batch06/evidence/msgev_pk_native_batch06_alignment.v1.json",
        "evidence_size": 454_128,
        "evidence_sha256": "DE9CCA0F5045B5F64D5F2206394097C8B3628FA6FA71E78C856707FE1F065E02",
        "ids": (10810, 10820, 10876, 10887),
    },
)

# Each anchor is a unique Korean-only substring in the donor after line breaks
# are removed and source ESC lexemes are rebased. A break is inserted after
# each anchor, in order. This keeps all non-layout donor text byte-for-byte
# intact after skeleton removal.
LINE_LAYOUT_ANCHORS: dict[int, tuple[str, ...]] = {
    8466: ("\x1bCB우에스기\x1bCZ는",),
    9796: ("줄었고,", "\x1bCA히데요시\x1bCZ에게"),
    9820: ("자들!", "내가"),
    9822: ("대답인가…", "운명을"),
    9823: ("일단락되었으나", "여전히"),
    9825: ("제거 기회를", "\x1bCA이에야스\x1bCZ와의"),
    9857: ("제거 기회를", "\x1bCA이에야스\x1bCZ와의"),
    9890: ("\x1bCA지부\x1bCZ.", "\x1bCA우키타\x1bCZ 님의 역할일"),
    9948: ("사람입니다.", "일은"),
    9980: ("돌아가", "\x1bCB서군\x1bCZ으로"),
    10008: ("각오입니다.", "증서를"),
    10101: ("움직이다니!", "생기면"),
    10114: ("결단은", "앞날에"),
    10181: ("계기로",),
    10186: ("우리에게", "있다면……"),
    10574: ("무르익었다.", "내 손으로"),
    10689: ("그는", "싸움에"),
    10810: ("과연",),
    10820: ("청했으니", "수밖에"),
    10876: ("저질렀습니다!", "대신해"),
    10887: ("\x1bCA오다 노부나가\x1bCZ.", "봉화가"),
}

# @@ESC<n>@@ is replaced at freeze time with the source table's exact ESC
# lexeme at the same ordinal position. These Korean-only templates are
# deliberately explicit because the original donor ESC pair counts are not
# compatible with the target skeleton.
SPECIAL_ENTITY_LAYOUTS: dict[int, dict[str, Any]] = {
    10421: {
        "template": (
            "@@ESC0@@모가미 가문@@ESC1@@의 거성 @@ESC2@@야마가타성@@ESC3@@을 지키는 마지막 요새\n"
            "@@ESC4@@하세도성@@ESC5@@을 @@ESC6@@우에스기군은@@ESC7@@ 보름 동안 포위했고\n"
            "그때 놀라운 소식이 날아들었다."
        ),
        "entity_order": ("모가미 가문", "야마가타성", "하세도성", "우에스기군은"),
        "semantic_preservation": "whitespace_normalized_word_multiset_reordered",
    },
    10475: {
        "template": (
            "@@ESC0@@이시다 미쓰나리@@ESC1@@에게 요청을 받은 우에스기는\n"
            "@@ESC2@@오우의 여러 장수@@ESC3@@를 규합해 @@ESC4@@에도@@ESC5@@를 공격하기 위한\n"
            "발판으로 이 @@ESC6@@우에스기@@ESC7@@의 @@ESC8@@모가미@@ESC9@@ 공략을 택했다."
        ),
        "entity_order": ("이시다 미쓰나리", "오우의 여러 장수", "에도", "우에스기", "모가미"),
        "semantic_preservation": "exact_payload_after_skeleton_removal",
    },
}

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(r"[\u3040-\u30ff\uff66-\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
PRINTF_RE = re.compile(r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
RUNTIME_BRACKET_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
ESC_MARKER_RE = re.compile(r"@@ESC(\d+)@@")
PROFILE_KEYS = (
    "printf",
    "unknown_percent_count",
    "leading_whitespace",
    "trailing_whitespace",
    "esc",
    "esc_pair_family",
    "controls",
    "line_breaks",
    "pua",
    "runtime_brackets",
)


class ManualLayoutError(ValueError):
    """Raised when a source-free manual-layout contract does not hold."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def pretty_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ManualLayoutError(f"{label} differs from its exact contract")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        previous = folded.get(key.casefold())
        if previous is not None:
            raise ManualLayoutError(f"duplicate/case-colliding JSON key: {previous!r}/{key!r}")
        folded[key.casefold()] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManualLayoutError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ManualLayoutError(f"JSON root is not an object: {path}")
    return value, blob


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ManualLayoutError(f"required file is missing: {path}")
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def path_from_repo(relative: str) -> Path:
    value = Path(relative)
    if not relative or value.is_absolute() or ".." in value.parts or "\\" in relative:
        raise ManualLayoutError("repository-relative path is unsafe")
    path = (REPO / value).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError as exc:
        raise ManualLayoutError("repository-relative path escaped workspace") from exc
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


def semantic_word_counter(text: str) -> Counter[str]:
    value = ESC_RE.sub("", text)
    value = PRINTF_RE.sub("", value)
    value = RUNTIME_BRACKET_RE.sub("", value)
    value = LINE_BREAK_RE.sub(" ", value)
    value = "".join(
        char
        for char in value
        if unicodedata.category(char) != "Cc" and not 0xE000 <= ord(char) <= 0xF8FF
    )
    return Counter(value.split())


def validate_korean(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\0" in value or "\ufffd" in value:
        raise ManualLayoutError(f"unsafe Korean text: {label}")
    if CJK_OR_KANA_RE.search(value) or not HANGUL_RE.search(value):
        raise ManualLayoutError(f"Korean script contract differs: {label}")
    return value


def load_stock(stock_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    source_path = (stock_root.resolve() / Path(RESOURCE)).resolve()
    if not source_path.is_file():
        raise ManualLayoutError(f"v0.9 JP source is missing: {source_path}")
    packed = source_path.read_bytes()
    require_equal(
        {"packed_size": len(packed), "packed_sha256": sha256_bytes(packed)},
        {"packed_size": STOCK["packed_size"], "packed_sha256": STOCK["packed_sha256"]},
        "v0.9 JP packed baseline",
    )
    _header, raw = decompress_wrapper(packed)
    require_equal(
        {"raw_size": len(raw), "raw_sha256": sha256_bytes(raw)},
        {"raw_size": STOCK["raw_size"], "raw_sha256": STOCK["raw_sha256"]},
        "v0.9 JP raw baseline",
    )
    table = parse_message_table(raw)
    require_equal(table.string_count, STOCK["string_count"], "v0.9 JP string count")
    if rebuild_message_table(table, table.texts) != raw:
        raise ManualLayoutError("unchanged v0.9 JP table cannot round-trip byte-identically")
    return source_path, packed, raw, table


def load_audit() -> dict[int, str]:
    require_equal(file_spec(AUDIT_PATH), AUDIT_PIN, "active residual audit pin")
    document, _blob = read_json(AUDIT_PATH)
    bundles = document.get("recommended_parallel_bundles")
    if not isinstance(bundles, list):
        raise ManualLayoutError("audit bundle vector is missing")
    selected = [row for row in bundles if isinstance(row, dict) and row.get("bundle_id") == BUNDLE_ID]
    if len(selected) != 1:
        raise ManualLayoutError("P1-03 audit bundle is missing or duplicated")
    bundle = selected[0]
    if (
        bundle.get("resource") != RESOURCE
        or bundle.get("format") != "common"
        or bundle.get("classification") != "japanese_kana_no_hangul"
        or bundle.get("priority") != "P1"
    ):
        raise ManualLayoutError("P1-03 audit route differs")
    coordinates = bundle.get("coordinates")
    if not isinstance(coordinates, list):
        raise ManualLayoutError("P1-03 audit coordinates are missing")
    ids: list[int] = []
    for coordinate in coordinates:
        if not isinstance(coordinate, dict) or set(coordinate) != {"id"} or type(coordinate.get("id")) is not int:
            raise ManualLayoutError("P1-03 audit coordinate schema differs")
        ids.append(coordinate["id"])
    if ids != sorted(set(ids)):
        raise ManualLayoutError("P1-03 audit coordinates are not sorted and unique")
    require_equal(len(ids), 183, "P1-03 audit coordinate count")
    require_equal(
        canonical_hash([{"id": entry_id} for entry_id in ids]),
        BUNDLE_COORDINATE_SHA256,
        "P1-03 audit coordinate digest",
    )
    require_equal(bundle.get("coordinate_count"), len(ids), "P1-03 audit bundle count")
    require_equal(bundle.get("coordinate_sha256"), BUNDLE_COORDINATE_SHA256, "P1-03 audit bundle digest")
    if not set(MANUAL_IDS).issubset(ids):
        raise ManualLayoutError("manual layout IDs are outside the P1-03 audit bundle")

    resource_rows = document.get("entries_by_resource", {}).get(RESOURCE)
    if not isinstance(resource_rows, list):
        raise ManualLayoutError("P1-03 audit resource rows are missing")
    result: dict[int, str] = {}
    for row in resource_rows:
        if not isinstance(row, dict):
            continue
        coordinate = row.get("coordinate")
        source_hash = row.get("active_utf16le_sha256")
        if isinstance(coordinate, dict) and type(coordinate.get("id")) is int and coordinate["id"] in MANUAL_IDS:
            if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash):
                raise ManualLayoutError("manual audit source hash is malformed")
            result[coordinate["id"]] = source_hash
    require_equal(tuple(sorted(result)), MANUAL_IDS, "manual audit source-hash coordinate coverage")
    return result


def checked_reference_inputs() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for group in DONOR_GROUPS:
        for role in ("catalog", "evidence"):
            relative = str(group[role])
            actual = file_spec(path_from_repo(relative))
            expected = {"size": group[f"{role}_size"], "sha256": group[f"{role}_sha256"]}
            require_equal(actual, expected, f"{group['name']} {role}")
            result.append({"role": f"{group['name']}_{role}", "relative_path": relative, **actual})
    return result


def _catalog_korean_entries(document: Mapping[str, Any], label: str) -> dict[int, str]:
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise ManualLayoutError(f"catalog entries missing: {label}")
    result: dict[int, str] = {}
    for row in entries:
        if not isinstance(row, dict) or type(row.get("id")) is not int:
            raise ManualLayoutError(f"catalog entry id is invalid: {label}")
        entry_id = row["id"]
        korean = validate_korean(row.get("ko"), f"{label}:{entry_id}")
        previous = result.get(entry_id)
        if previous is not None and previous != korean:
            raise ManualLayoutError(f"catalog Korean collision: {label}:{entry_id}")
        result[entry_id] = korean
    return result


def _evidence_hashes(document: Mapping[str, Any], label: str) -> dict[int, str]:
    rows = document.get("entries")
    if not isinstance(rows, list):
        raise ManualLayoutError(f"alignment rows missing: {label}")
    result: dict[int, str] = {}
    for row in rows:
        if not isinstance(row, dict) or type(row.get("id")) is not int:
            continue
        hashes = row.get("official_pk_utf16le_sha256")
        source_hash = hashes.get("JP") if isinstance(hashes, dict) else None
        if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash):
            continue
        previous = result.get(row["id"])
        if previous is not None and previous != source_hash:
            raise ManualLayoutError(f"alignment source-hash collision: {label}:{row['id']}")
        result[row["id"]] = source_hash
    return result


def load_donors(audit_hashes: Mapping[int, str]) -> tuple[dict[int, dict[str, Any]], list[dict[str, Any]]]:
    inputs = checked_reference_inputs()
    donors: dict[int, dict[str, Any]] = {}
    for group in DONOR_GROUPS:
        catalog_path = path_from_repo(str(group["catalog"]))
        evidence_path = path_from_repo(str(group["evidence"]))
        catalog, _catalog_blob = read_json(catalog_path)
        evidence, _evidence_blob = read_json(evidence_path)
        korean_by_id = _catalog_korean_entries(catalog, str(group["catalog"]))
        source_by_id = _evidence_hashes(evidence, str(group["evidence"]))
        for entry_id in group["ids"]:
            korean = korean_by_id.get(entry_id)
            source_hash = source_by_id.get(entry_id)
            if korean is None or source_hash is None:
                raise ManualLayoutError(f"pinned Korean provenance is incomplete at {entry_id}")
            require_equal(source_hash, audit_hashes[entry_id], f"donor alignment source hash at {entry_id}")
            donor = {
                "kind": "committed_native_korean_semantic_payload",
                "catalog": str(group["catalog"]),
                "evidence": str(group["evidence"]),
                "catalog_entry_id": entry_id,
                "ko": korean,
                "ko_utf16le_sha256": text_hash(korean),
            }
            if entry_id in donors:
                raise ManualLayoutError(f"manual Korean donor is duplicated: {entry_id}")
            donors[entry_id] = donor
    require_equal(tuple(sorted(donors)), MANUAL_IDS, "manual Korean donor coverage")
    return donors, inputs


def rebase_esc_lexemes(korean: str, source_profile: Mapping[str, Any]) -> str:
    expected = iter(source_profile["esc"])
    count = 0

    def replace(_: re.Match[str]) -> str:
        nonlocal count
        count += 1
        try:
            return next(expected)
        except StopIteration as exc:
            raise ManualLayoutError("ESC rebase had too many donor lexemes") from exc

    converted = ESC_RE.sub(replace, korean)
    try:
        next(expected)
    except StopIteration:
        pass
    else:
        raise ManualLayoutError("ESC rebase had too few donor lexemes")
    require_equal(count, len(source_profile["esc"]), "ESC rebase lexeme count")
    return converted


def line_layout_output(entry_id: int, source: str, donor: str) -> tuple[str, dict[str, Any]]:
    source_profile = message_profile(source)
    donor_profile = message_profile(donor)
    require_equal(
        profile_mismatches(source, donor),
        ["line_breaks"],
        f"line-layout donor contract at {entry_id}",
    )
    require_equal(
        source_profile["esc_pair_family"],
        donor_profile["esc_pair_family"],
        f"line-layout ESC pair family at {entry_id}",
    )
    require_equal(
        len(source_profile["esc"]),
        len(donor_profile["esc"]),
        f"line-layout ESC lexeme count at {entry_id}",
    )
    anchors = LINE_LAYOUT_ANCHORS[entry_id]
    require_equal(
        tuple(source_profile["line_breaks"]),
        tuple("\n" for _ in anchors),
        f"manual line-break type/count at {entry_id}",
    )
    body = LINE_BREAK_RE.sub("", rebase_esc_lexemes(donor, source_profile))
    positions: list[int] = []
    previous = -1
    for anchor in anchors:
        if body.count(anchor) != 1:
            raise ManualLayoutError(f"manual line-break anchor is not unique at {entry_id}: {anchor!r}")
        position = body.index(anchor) + len(anchor)
        if position <= previous:
            raise ManualLayoutError(f"manual line-break anchors are not ordered at {entry_id}")
        positions.append(position)
        previous = position
    for position in reversed(positions):
        body = body[:position] + "\n" + body[position:]
    require_equal(payload_hash(body), payload_hash(donor), f"line-layout semantic payload at {entry_id}")
    require_equal(message_profile(body), source_profile, f"line-layout source profile at {entry_id}")
    return body, {
        "operation": "manual_linebreak_layout_with_source_esc_stream",
        "manual_line_break_anchor_count": len(anchors),
        "semantic_preservation": "exact_payload_after_skeleton_removal",
    }


def entity_layout_output(entry_id: int, source: str, donor: str) -> tuple[str, dict[str, Any]]:
    source_profile = message_profile(source)
    require_equal(
        profile_mismatches(source, donor),
        ["esc", "esc_pair_family"],
        f"entity-layout donor contract at {entry_id}",
    )
    spec = SPECIAL_ENTITY_LAYOUTS[entry_id]
    template = str(spec["template"])
    esc = list(source_profile["esc"])
    expected_markers = tuple(range(len(esc)))
    observed_markers = tuple(int(value) for value in ESC_MARKER_RE.findall(template))
    require_equal(observed_markers, expected_markers, f"entity-layout marker order at {entry_id}")
    result = template
    for index, lexeme in enumerate(esc):
        marker = f"@@ESC{index}@@"
        require_equal(result.count(marker), 1, f"entity-layout marker multiplicity at {entry_id}:{index}")
        result = result.replace(marker, lexeme)
    if ESC_MARKER_RE.search(result):
        raise ManualLayoutError(f"unresolved entity-layout ESC marker at {entry_id}")
    require_equal(message_profile(result), source_profile, f"entity-layout source profile at {entry_id}")
    if entry_id == 10421:
        require_equal(
            semantic_word_counter(result),
            semantic_word_counter(donor),
            "10421 manually reordered Korean semantic word multiset",
        )
    elif entry_id == 10475:
        require_equal(payload_hash(result), payload_hash(donor), "10475 Korean semantic payload")
    else:
        raise ManualLayoutError(f"unknown entity layout ID: {entry_id}")
    return result, {
        "operation": "manual_entity_layout_with_exact_source_esc_stream",
        "source_esc_lexeme_count": len(esc),
        "reassembled_entity_order": list(spec["entity_order"]),
        "semantic_preservation": str(spec["semantic_preservation"]),
    }


def resolve_entries(table: MessageTable) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    audit_hashes = load_audit()
    donors, reference_inputs = load_donors(audit_hashes)
    entries: list[dict[str, Any]] = []
    for entry_id in MANUAL_IDS:
        if not 0 <= entry_id < table.string_count:
            raise ManualLayoutError(f"manual coordinate lies outside the message table: {entry_id}")
        source = table.texts[entry_id]
        source_hash = text_hash(source)
        require_equal(source_hash, audit_hashes[entry_id], f"v0.9 JP source hash at {entry_id}")
        source_profile = message_profile(source)
        donor = donors[entry_id]
        korean_input = validate_korean(donor["ko"], f"manual donor:{entry_id}")
        if entry_id in LINE_LAYOUT_IDS:
            korean, layout = line_layout_output(entry_id, source, korean_input)
        else:
            korean, layout = entity_layout_output(entry_id, source, korean_input)
        validate_korean(korean, f"manual output:{entry_id}")
        require_equal(message_profile(korean), source_profile, f"manual full token profile at {entry_id}")
        provenance = {
            **{key: value for key, value in donor.items() if key != "ko"},
            "input_semantic_payload_utf16le_sha256": payload_hash(korean_input),
            "input_token_profile_sha256": profile_hash(message_profile(korean_input)),
            **layout,
        }
        entries.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": source_hash,
                "ko": korean,
                "ko_utf16le_sha256": text_hash(korean),
                "source_token_profile_sha256": profile_hash(source_profile),
                "provenance": provenance,
            }
        )
    require_equal(tuple(entry["id"] for entry in entries), MANUAL_IDS, "manual entry order")
    return entries, reference_inputs


def manual_coordinate_hash(entries: Sequence[Mapping[str, Any]]) -> str:
    return canonical_hash([{"id": int(entry["id"])} for entry in entries])


def make_overlay(entries: Sequence[Mapping[str, Any]], reference_inputs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msgev_ko_steam_jp_p1_residual_03_manual_layout_23.v1",
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "base_language": "JP",
        "active_v090_baseline": dict(STOCK),
        "audit_bundle": {
            "bundle_id": BUNDLE_ID,
            "audit_sha256": AUDIT_PIN["sha256"],
            "coordinate_count": 183,
            "coordinate_sha256": BUNDLE_COORDINATE_SHA256,
        },
        "selection": {
            "manual_layout_entry_count": len(entries),
            "line_layout_entry_count": len(LINE_LAYOUT_IDS),
            "entity_layout_entry_count": len(SPECIAL_ENTITY_IDS),
            "coordinate_sha256": manual_coordinate_hash(entries),
        },
        "distribution_policy": {
            "sc_container_used": False,
            "complete_candidate_private_only": True,
            "installed_game_file_written": False,
        },
        "reference_inputs": [dict(value) for value in reference_inputs],
        "entry_count": len(entries),
        "entries": [dict(entry) for entry in entries],
    }


def validate_entries(table: MessageTable, raw_entries: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_entries, list):
        raise ManualLayoutError("manual overlay entries are missing")
    expected, _inputs = resolve_entries(table)
    required = {
        "id",
        "source_jp_utf16le_sha256",
        "ko",
        "ko_utf16le_sha256",
        "source_token_profile_sha256",
        "provenance",
    }
    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, Mapping) or set(entry) != required:
            raise ManualLayoutError(f"manual overlay entry schema differs at index {index}")
        entry_id = entry["id"]
        if type(entry_id) is not int or entry_id not in MANUAL_IDS:
            raise ManualLayoutError(f"manual overlay ID is invalid at index {index}")
        source = table.texts[entry_id]
        korean = validate_korean(entry["ko"], f"manual overlay:{entry_id}")
        if not all(
            isinstance(entry[key], str) and HEX64_RE.fullmatch(entry[key])
            for key in ("source_jp_utf16le_sha256", "ko_utf16le_sha256", "source_token_profile_sha256")
        ):
            raise ManualLayoutError(f"manual overlay hash is invalid at {entry_id}")
        require_equal(text_hash(source), entry["source_jp_utf16le_sha256"], f"manual source hash at {entry_id}")
        require_equal(text_hash(korean), entry["ko_utf16le_sha256"], f"manual Korean hash at {entry_id}")
        require_equal(
            profile_hash(message_profile(source)),
            entry["source_token_profile_sha256"],
            f"manual source profile hash at {entry_id}",
        )
        require_equal(message_profile(korean), message_profile(source), f"manual token profile at {entry_id}")
        if not isinstance(entry["provenance"], Mapping):
            raise ManualLayoutError(f"manual provenance is invalid at {entry_id}")
        normalized.append(dict(entry))
    require_equal(normalized, expected, "manual overlay exact donor/layout resolution")
    return normalized


def validate_public_overlay(value: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    required = {
        "schema",
        "overlay_id",
        "source_free",
        "contains_commercial_source_text",
        "contains_complete_game_resource",
        "resource",
        "base_language",
        "active_v090_baseline",
        "audit_bundle",
        "selection",
        "distribution_policy",
        "reference_inputs",
        "entry_count",
        "entries",
    }
    if set(value) != required or value.get("schema") != OVERLAY_SCHEMA:
        raise ManualLayoutError("public overlay schema differs")
    require_equal(
        value.get("overlay_id"),
        "msgev_ko_steam_jp_p1_residual_03_manual_layout_23.v1",
        "public overlay ID",
    )
    require_equal(value.get("resource"), RESOURCE, "public overlay resource")
    require_equal(value.get("base_language"), "JP", "public overlay language")
    require_equal(value.get("active_v090_baseline"), STOCK, "public overlay baseline")
    require_equal(value.get("source_free"), True, "public overlay source-free flag")
    require_equal(value.get("contains_commercial_source_text"), False, "public overlay commercial source flag")
    require_equal(value.get("contains_complete_game_resource"), False, "public overlay complete resource flag")
    require_equal(
        value.get("audit_bundle"),
        {
            "bundle_id": BUNDLE_ID,
            "audit_sha256": AUDIT_PIN["sha256"],
            "coordinate_count": 183,
            "coordinate_sha256": BUNDLE_COORDINATE_SHA256,
        },
        "public overlay audit bundle",
    )
    require_equal(
        value.get("distribution_policy"),
        {
            "sc_container_used": False,
            "complete_candidate_private_only": True,
            "installed_game_file_written": False,
        },
        "public overlay distribution policy",
    )
    expected_entries, expected_inputs = resolve_entries(table)
    require_equal(value.get("reference_inputs"), expected_inputs, "public overlay reference inputs")
    entries = validate_entries(table, value.get("entries"))
    require_equal(value.get("entry_count"), len(entries), "public overlay entry count")
    require_equal(
        value.get("selection"),
        {
            "manual_layout_entry_count": len(MANUAL_IDS),
            "line_layout_entry_count": len(LINE_LAYOUT_IDS),
            "entity_layout_entry_count": len(SPECIAL_ENTITY_IDS),
            "coordinate_sha256": manual_coordinate_hash(entries),
        },
        "public overlay selection",
    )
    require_equal(entries, expected_entries, "public overlay expected entries")
    return entries


def candidate_from_entries(
    packed: bytes, raw: bytes, table: MessageTable, entries: Sequence[Mapping[str, Any]]
) -> tuple[bytes, bytes, list[int]]:
    selected = validate_entries(table, list(entries))
    selected_ids = {int(entry["id"]) for entry in selected}
    texts = list(table.texts)
    changed: list[int] = []
    for entry in selected:
        entry_id = int(entry["id"])
        korean = str(entry["ko"])
        if texts[entry_id] != korean:
            changed.append(entry_id)
        texts[entry_id] = korean
    require_equal(changed, list(MANUAL_IDS), "manual effective change vector")

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
    require_equal(rebuild_message_table(checked, checked.texts), checked_raw, "candidate parse/rebuild")
    for entry_id, source in enumerate(table.texts):
        if checked.texts[entry_id] != texts[entry_id]:
            raise ManualLayoutError(f"candidate text differs at {entry_id}")
        if entry_id not in selected_ids:
            if source.encode("utf-16le") + b"\0\0" != checked.texts[entry_id].encode("utf-16le") + b"\0\0":
                raise ManualLayoutError(f"nonselected UTF-16LE payload differs at {entry_id}")
    for entry_id in RUNTIME_PRESERVATION_IDS:
        require_equal(
            checked.texts[entry_id],
            table.texts[entry_id],
            f"runtime custom bracket payload at {entry_id}",
        )
    if (
        checked.string_count != table.string_count
        or checked.block_offset != table.block_offset
        or checked.table_offset != table.table_offset
        or checked.table_size != table.table_size
        or checked.string_start != table.string_start
    ):
        raise ManualLayoutError("candidate message table structure differs")
    stock_prefix = bytearray(raw[: table.table_offset])
    candidate_prefix = bytearray(checked_raw[: checked.table_offset])
    struct.pack_into("<I", stock_prefix, 8, 0)
    struct.pack_into("<I", candidate_prefix, 8, 0)
    require_equal(stock_prefix, candidate_prefix, "opaque prefix except logical size")
    return packed_a, raw_a, changed


def runtime_preservation_rows(table: MessageTable) -> list[dict[str, Any]]:
    return [
        {
            "id": entry_id,
            "classification": "runtime_custom_bracket_substitution_preserved",
            "reason_codes": ["runtime_custom_bracket_substitution", "preserve_active_utf16le_payload"],
            "source_jp_utf16le_sha256": text_hash(table.texts[entry_id]),
            "source_token_profile": message_profile(table.texts[entry_id]),
            "source_token_profile_sha256": profile_hash(message_profile(table.texts[entry_id])),
        }
        for entry_id in RUNTIME_PRESERVATION_IDS
    ]


def make_validation(
    table: MessageTable,
    entries: Sequence[Mapping[str, Any]],
    candidate: bytes,
    candidate_raw: bytes,
    changed: Sequence[int],
) -> dict[str, Any]:
    preserved = runtime_preservation_rows(table)
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v090_baseline": dict(STOCK),
        "audit_bundle": {
            "bundle_id": BUNDLE_ID,
            "coordinate_count": 183,
            "coordinate_sha256": BUNDLE_COORDINATE_SHA256,
        },
        "counts": {
            "applied_entry_count": len(entries),
            "manual_review_hold_count": 0,
            "runtime_preservation_count": len(RUNTIME_PRESERVATION_IDS),
            "manual_layout_entry_count": len(entries),
            "line_layout_entry_count": len(LINE_LAYOUT_IDS),
            "entity_layout_entry_count": len(SPECIAL_ENTITY_IDS),
            "runtime_custom_bracket_preservation_count": len(RUNTIME_PRESERVATION_IDS),
        },
        "expected_candidate": {
            "packed_size": len(candidate),
            "packed_sha256": sha256_bytes(candidate),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256_bytes(candidate_raw),
            "string_count": table.string_count,
        },
        "effective_change_count": len(changed),
        "effective_change_coordinate_sha256": canonical_hash([{"id": entry_id} for entry_id in changed]),
        "transformed_entries": [
            {
                "id": entry["id"],
                "source_jp_utf16le_sha256": entry["source_jp_utf16le_sha256"],
                "ko_utf16le_sha256": entry["ko_utf16le_sha256"],
                "source_token_profile": message_profile(table.texts[int(entry["id"])]),
                "source_token_profile_sha256": entry["source_token_profile_sha256"],
                "provenance": dict(entry["provenance"]),
            }
            for entry in entries
        ],
        "manual_review_holds": preserved,
        "checks": {
            "active_v090_baseline_pinned": True,
            "audit_coordinate_scope_exact": True,
            "per_entry_jp_source_hash_gated": True,
            "committed_korean_provenance_pinned": True,
            "switch_same_index_payload_used": False,
            "full_token_profile_preserved": True,
            "manual_line_layout_semantic_payload_preserved": True,
            "manual_entity_layout_source_esc_stream_exact": True,
            "parser_roundtrip_valid": True,
            "nonselected_utf16le_payloads_preserved": True,
            "runtime_custom_bracket_rows_preserved": True,
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
        "runtime_route": {
            "language": "JP",
            "sc_container_used": False,
            "installed_game_file_written": False,
        },
        "active_v090_baseline": dict(STOCK),
        "audit_bundle": {
            "bundle_id": BUNDLE_ID,
            "coordinate_sha256": BUNDLE_COORDINATE_SHA256,
        },
        "overlay": {
            "relative_path": (
                "workstreams/steam_jp_msgev_p1_residual_03_manual_layout_v1/public/"
                "msgev_ko_steam_jp_p1_residual_03_manual_layout_23.v1.json"
            ),
            "sha256": sha256_bytes(overlay_blob),
            "entry_count": len(MANUAL_IDS),
        },
        "validation": {
            "relative_path": "workstreams/steam_jp_msgev_p1_residual_03_manual_layout_v1/validation.v1.json",
            "sha256": sha256_bytes(validation_blob),
        },
        "expected_candidate": dict(validation["expected_candidate"]),
        "output_policy": {
            "complete_candidate_private_only": True,
            "allowed_root": "tmp",
            "relative_path": RESOURCE,
        },
        "proofs": {
            "active_v090_baseline_pinned": True,
            "committed_korean_provenance_source_hash_gated": True,
            "switch_same_index_payload_not_used": True,
            "full_token_profiles_preserved": True,
            "manual_line_layout_semantic_payload_preserved": True,
            "manual_entity_layout_source_esc_stream_exact": True,
            "nonselected_utf16le_payloads_preserved": True,
            "runtime_custom_bracket_rows_preserved": True,
            "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True,
            "steam_installation_read_only": True,
        },
    }


def assert_source_free(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise ManualLayoutError(f"artifact is not JP-route source-free: {path}")


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO / "tmp").resolve()
    try:
        resolved.relative_to(private_root)
    except ValueError as exc:
        raise ManualLayoutError("candidate output must stay below KR_PATCH_WORK/tmp") from exc
    if resolved == private_root:
        raise ManualLayoutError("KR_PATCH_WORK/tmp itself cannot be a candidate root")
    return resolved


def freeze(stock_root: Path) -> dict[str, Any]:
    _source_path, packed, raw, table = load_stock(stock_root)
    entries, reference_inputs = resolve_entries(table)
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries)
    overlay_blob = pretty_bytes(make_overlay(entries, reference_inputs))
    validation = make_validation(table, entries, candidate, candidate_raw, changed)
    validation_blob = pretty_bytes(validation)
    contract = make_contract(overlay_blob, validation_blob, validation)
    atomic_write(PUBLIC_OVERLAY, overlay_blob)
    atomic_write(VALIDATION, validation_blob)
    atomic_write(CONTRACT, pretty_bytes(contract))
    for path in (PUBLIC_OVERLAY, VALIDATION, CONTRACT):
        assert_source_free(path)
    return {
        "status": "PASS",
        "manual_layout_entry_count": len(entries),
        "line_layout_entry_count": len(LINE_LAYOUT_IDS),
        "entity_layout_entry_count": len(SPECIAL_ENTITY_IDS),
        "candidate_sha256": sha256_bytes(candidate),
        "candidate_raw_sha256": sha256_bytes(candidate_raw),
        "installed_game_file_modified": False,
    }


def load_frozen_inputs(
    stock_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], bytes, bytes, MessageTable]:
    source_path, packed, raw, table = load_stock(stock_root)
    contract, _contract_blob = read_json(CONTRACT)
    required = {
        "schema",
        "source_free",
        "contains_commercial_source_text",
        "contains_complete_game_resource",
        "resource",
        "runtime_route",
        "active_v090_baseline",
        "audit_bundle",
        "overlay",
        "validation",
        "expected_candidate",
        "output_policy",
        "proofs",
    }
    if set(contract) != required or contract.get("schema") != CONTRACT_SCHEMA:
        raise ManualLayoutError("frozen contract schema differs")
    require_equal(contract.get("resource"), RESOURCE, "frozen contract resource")
    require_equal(contract.get("source_free"), True, "frozen contract source-free flag")
    require_equal(contract.get("contains_commercial_source_text"), False, "frozen contract commercial source flag")
    require_equal(contract.get("contains_complete_game_resource"), False, "frozen contract complete resource flag")
    require_equal(
        contract.get("runtime_route"),
        {"language": "JP", "sc_container_used": False, "installed_game_file_written": False},
        "frozen runtime route",
    )
    require_equal(contract.get("active_v090_baseline"), STOCK, "frozen baseline")
    require_equal(
        contract.get("audit_bundle"),
        {"bundle_id": BUNDLE_ID, "coordinate_sha256": BUNDLE_COORDINATE_SHA256},
        "frozen audit bundle",
    )
    require_equal(
        contract.get("output_policy"),
        {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE},
        "frozen output policy",
    )
    if not isinstance(contract.get("proofs"), dict) or any(value is not True for value in contract["proofs"].values()):
        raise ManualLayoutError("frozen proof set differs")
    overlay_path = path_from_repo(str(contract.get("overlay", {}).get("relative_path", "")))
    overlay, overlay_blob = read_json(overlay_path)
    require_equal(sha256_bytes(overlay_blob), contract.get("overlay", {}).get("sha256"), "frozen overlay hash")
    require_equal(contract.get("overlay", {}).get("entry_count"), len(MANUAL_IDS), "frozen overlay count")
    entries = validate_public_overlay(overlay, table)
    validation_path = path_from_repo(str(contract.get("validation", {}).get("relative_path", "")))
    validation, validation_blob = read_json(validation_path)
    require_equal(sha256_bytes(validation_blob), contract.get("validation", {}).get("sha256"), "frozen validation hash")
    require_equal(validation.get("schema"), VALIDATION_SCHEMA, "frozen validation schema")
    require_equal(validation.get("expected_candidate"), contract.get("expected_candidate"), "frozen validation candidate")
    require_equal(
        validation.get("counts"),
        {
            "applied_entry_count": len(MANUAL_IDS),
            "manual_review_hold_count": 0,
            "runtime_preservation_count": len(RUNTIME_PRESERVATION_IDS),
            "manual_layout_entry_count": len(MANUAL_IDS),
            "line_layout_entry_count": len(LINE_LAYOUT_IDS),
            "entity_layout_entry_count": len(SPECIAL_ENTITY_IDS),
            "runtime_custom_bracket_preservation_count": len(RUNTIME_PRESERVATION_IDS),
        },
        "frozen validation counts",
    )
    require_equal(
        validation.get("manual_review_holds"),
        runtime_preservation_rows(table),
        "frozen runtime-preservation holds",
    )
    for path in (overlay_path, validation_path, CONTRACT):
        assert_source_free(path)
    require_equal(source_path, (stock_root.resolve() / Path(RESOURCE)).resolve(), "frozen stock source path")
    return contract, entries, packed, raw, table


def build_staging_candidate(stock_root: Path, output_root: Path) -> dict[str, Any]:
    output = require_private_output_root(output_root)
    source_path, stock_before, _raw_before, _table_before = load_stock(stock_root)
    contract, entries, packed, raw, table = load_frozen_inputs(stock_root)
    require_equal(packed, stock_before, "v0.9 source while loading frozen inputs")
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries)
    observed = {
        "packed_size": len(candidate),
        "packed_sha256": sha256_bytes(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256_bytes(candidate_raw),
        "string_count": table.string_count,
    }
    require_equal(observed, contract.get("expected_candidate"), "candidate versus frozen contract")
    target = (output / Path(RESOURCE)).resolve()
    try:
        target.relative_to(output)
    except ValueError as exc:
        raise ManualLayoutError("candidate target escaped private output root") from exc
    if target == source_path:
        raise ManualLayoutError("refusing to target source baseline")
    atomic_write(target, candidate)
    require_equal(target.read_bytes(), candidate, "written private candidate")
    require_equal(source_path.read_bytes(), stock_before, "v0.9 source after private build")
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
        "coordinate_sha256": manual_coordinate_hash(entries),
        "effective_change_coordinate_sha256": canonical_hash([{"id": entry_id} for entry_id in changed]),
        "output": {
            "relative_path": RESOURCE,
            "complete_candidate_private_only": True,
            "installed_game_file_modified": False,
        },
        "checks": {
            "contract_hash": "OK",
            "source_hash_gates": "OK",
            "full_token_profiles": "OK",
            "source_unchanged": "OK",
        },
    }
    atomic_write(output / "build_manifest.v1.json", pretty_bytes(manifest))
    return {
        "candidate_path": str(target),
        "manifest_path": str(output / "build_manifest.v1.json"),
        **observed,
        "installed_game_file_modified": False,
    }


def verify(stock_root: Path) -> dict[str, Any]:
    contract, entries, packed, raw, table = load_frozen_inputs(stock_root)
    first, first_raw, changed = candidate_from_entries(packed, raw, table, entries)
    second, second_raw, changed_second = candidate_from_entries(packed, raw, table, entries)
    require_equal(first, second, "deterministic candidate A/B")
    require_equal(first_raw, second_raw, "deterministic raw A/B")
    require_equal(changed, changed_second, "deterministic changed IDs A/B")
    require_equal(
        {
            "packed_size": len(first),
            "packed_sha256": sha256_bytes(first),
            "raw_size": len(first_raw),
            "raw_sha256": sha256_bytes(first_raw),
            "string_count": table.string_count,
        },
        contract.get("expected_candidate"),
        "verified candidate versus frozen contract",
    )
    return {
        "status": "PASS",
        "manual_layout_entry_count": len(entries),
        "candidate_sha256": sha256_bytes(first),
        "output_written": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("freeze", "write source-free overlay, validation, and contract"),
        ("build", "write only a private staging candidate"),
        ("verify", "recompute the frozen candidate without writing a resource"),
    ):
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
    except (ManualLayoutError, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
