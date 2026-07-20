#!/usr/bin/env python3
"""Build a private, fail-closed 6000-7999 event restoration candidate.

The only Korean build input is the strict batch06 candidate.  Every target
comes verbatim from a completed 6000 or 7000 human-review artifact.  Direct
PC JP/EN/SC/TC resources are read-only audit witnesses only.  This builder
has no Steam, Git, release, or network path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-manual-compact-static007-6000-7999-restore.v1"
STRICT_WORKSTREAM = "pc_event_manual_compact_static007_batch06_v1"
STRICT_ROOT = REPO / "tmp" / STRICT_WORKSTREAM / "candidate-final"
STRICT_EVENT = STRICT_ROOT / RESOURCE
STRICT_AUDIT = STRICT_ROOT / "audit.v1.json"
STRICT_MANIFEST = STRICT_ROOT / "candidate_manifest.v1.json"
EXPECTED_STRICT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "2EEF242A9F5183061F866C854DF51139CF0FEC3E69C004F04C665B69C91AAF5B",
    "raw_size": 1_007_428,
    "sha256": "600B6F1C8BE432A5987E1A05F19DCA30AF00DB9BFBFEAC702CCB60605B19B313",
    "size": 1_011_404,
}

ARTIFACT_6000 = (
    REPO
    / "workstreams"
    / "manual_compact_6000_review_v1"
    / "public"
    / "manual_compact_6000_review.v1.json"
)
ARTIFACT_7000 = (
    REPO
    / "workstreams"
    / "manual_compact_7000_review_v1"
    / "public"
    / "manual_compact_7000_review.v1.json"
)
EXPECTED_ARTIFACTS: Mapping[str, Mapping[str, Any]] = {
    "manual_compact_6000_review_v1": {
        "path": ARTIFACT_6000,
        "sha256": "1610EE261AF7F6C9D54B9E1B74A43A94D4F71B0A7808B29EE8627036B7A5DA81",
        "schema": "nobu16.kr.manual-compact-6000-review.v1",
        "expected_count": 192,
        "id_key": "entry_id",
        "current_key": "current_ko_at_batch05_strict_baseline",
        "direct_source_key": "direct_pc_sources",
        "id_range": (6000, 6999),
        "baseline_note": (
            "artifact baseline is batch05; every one of its reviewed current "
            "rows must equal the strict batch06 input before any proposed text "
            "is accepted"
        ),
    },
    "manual_compact_7000_review_v1": {
        "path": ARTIFACT_7000,
        "sha256": "BA42D65863460967B15671BD2BC1FE34BCBE80795E7601CDFC5E38172A320FBE",
        "schema": "nobu16.kr.pc-event-manual-compact-7000-human-review.v1",
        "expected_count": 201,
        "id_key": "id",
        "current_key": "current_ko_at_batch05_strict_baseline",
        "direct_source_key": "direct_pc_source_evidence",
        "id_range": (7000, 7999),
        "baseline_note": (
            "artifact was refreshed against batch06; its historical field label "
            "is retained for schema compatibility, so row-wise batch06 equality "
            "is the authority"
        ),
    },
}

RESERVATION_MANIFEST = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "runtime_token_reservations.v1.json"
)
EXPECTED_RESERVATION_SHA256 = "B981C7C456F2DC285721E7E3DB74D2D11456B49B25D5A97BB320F815DFC0A893"

DIRECT_CONTEXT_PATHS: Mapping[str, Path] = {
    "jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
        r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
    ),
    "en": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin"),
    "sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin"),
    "tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin"),
}
EXPECTED_DIRECT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    "jp": {
        "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        "raw_size": 894_800,
        "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "size": 562_226,
    },
    "en": {
        "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
        "raw_size": 1_878_836,
        "sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
        "size": 762_196,
    },
    "sc": {
        "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
        "raw_size": 754_708,
        "sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
        "size": 522_177,
    },
    "tc": {
        "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
        "raw_size": 744_212,
        "sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
        "size": 524_909,
    },
}

RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
MAX_EFFECTIVE_LINE_PX = 912
MAX_RAW_LINE_PX = 1440
MAX_LINES = 4
EXPECTED_REVIEWED_COUNT = 393
EXPECTED_REVIEWED_IDS_SHA256 = "787D4463B07EC1F57A5FB0993F0C3B93E3C0A5997C792AB43801D71FC218B546"
EXPECTED_CHANGED_COUNT = 338
EXPECTED_CHANGED_IDS_SHA256 = "07E14E2342A395494470D520D36872D167A3B76F14FA97AD84543CC52F6F3ADA"
EXPECTED_PRESERVED_COUNT = 55
EXPECTED_PRESERVED_IDS_SHA256 = "7B3C7141669C7DD975378791DF347C79FA1ED04812248FA6DB9E1D8E3306674C"
PROTECTED_SENTINEL_IDS = (5777, 5999, 7000, 8000, 8510)

# Deterministic profile generated from the pinned strict batch06 predecessor
# and the two completed review artifacts. Build and verify fail closed on any
# packed or raw drift.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "567C8C3C2F371E27CBE6FFEAB9F8F3EE7F6D6F13A2C179682A5A7F7D3F35780F",
    "raw_size": 1_020_112,
    "sha256": "D99390D4F2D7D469C105439A11476B01830F5E96287B278C164045CBC7BA3547",
    "size": 1_024_138,
}

ESC_RE = re.compile(r"\x1bC[ABCZ]")
BRACKET_RE = re.compile(r"\[[^\[\]\r\n]+\]")
NUMERIC_RUNTIME_RE = re.compile(r"\[([A-Za-z]{1,16})(\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")


class CandidateError(RuntimeError):
    """Raised when an input, review, layout, or output invariant fails."""


@dataclass(frozen=True)
class LoadedTable:
    texts: tuple[str, ...]
    profile: Mapping[str, Any]


@dataclass(frozen=True)
class ReviewRow:
    entry_id: int
    artifact_name: str
    artifact_relative: str
    artifact_sha256: str
    artifact_schema: str
    artifact_current: str
    proposed: str
    direct_sources: Mapping[str, str]
    artifact_row: Mapping[str, Any]


@dataclass(frozen=True)
class Bundle:
    event: bytes
    profile: Mapping[str, Any]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def file_record(path: Path) -> Mapping[str, Any]:
    blob = path.read_bytes()
    return {
        "relative_path": relative(path),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def packed_profile(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
        "sha256": sha256(packed),
        "size": len(packed),
    }


def normalized_linebreaks(value: str) -> str:
    return LINEBREAK_RE.sub("\n", value)


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def protected_signature(value: str) -> Mapping[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf_matches}
    controls: list[str] = []
    pua: list[str] = []
    for offset, character in enumerate(value):
        if character in "\r\n\x1b":
            continue
        if unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        if 0xE000 <= ord(character) <= 0xF8FF:
            pua.append(f"U+{ord(character):04X}")
    return {
        "esc_tags": ESC_RE.findall(value),
        "runtime_tokens": BRACKET_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1
            for offset, character in enumerate(value)
            if character == "%" and offset not in printf_offsets
        ),
        "other_c0_controls": controls,
        "pua_codepoints": pua,
        "nul_count": value.count("\x00"),
    }


def assert_colour_layout(value: str, entry_id: int) -> None:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            tag = value[cursor : cursor + 3]
            require(
                ESC_RE.fullmatch(tag) is not None,
                f"{entry_id}: malformed ESC tag {tag!r}",
            )
            if tag == "\x1bCZ":
                require(in_span, f"{entry_id}: unpaired ESC close")
                in_span = False
            else:
                require(not in_span, f"{entry_id}: nested ESC colour tag")
                in_span = True
            cursor += 3
            continue
        require(
            not (in_span and value[cursor] in "\r\n"),
            f"{entry_id}: line break inside colour tag",
        )
        cursor += 1
    require(not in_span, f"{entry_id}: unterminated ESC colour tag")


def load_json(path: Path) -> Mapping[str, Any]:
    require(path.is_file(), f"JSON source missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def load_packed_table(
    path: Path, expected: Mapping[str, Any], label: str
) -> LoadedTable:
    require(path.is_file(), f"{label} missing: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(
        rebuild_message_table(table, table.texts) == raw,
        f"{label} table round trip differs",
    )
    actual = packed_profile(packed, raw)
    require(actual == expected, f"{label} packed/raw profile drift")
    require(len(table.texts) == 17_916, f"{label} string count drift")
    return LoadedTable(tuple(table.texts), actual)


def load_strict_input() -> tuple[bytes, Any, LoadedTable, Mapping[str, Any]]:
    root = STRICT_ROOT.resolve(strict=True)
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    }
    require(
        actual_files == expected_files,
        f"strict batch06 file scope drift: {sorted(actual_files)}",
    )
    event = STRICT_EVENT.read_bytes()
    header, raw = decompress_wrapper(event)
    table = parse_message_table(raw)
    require(
        rebuild_message_table(table, table.texts) == raw,
        "strict batch06 table round trip differs",
    )
    strict_profile = packed_profile(event, raw)
    require(strict_profile == EXPECTED_STRICT_PROFILE, "strict batch06 profile drift")
    audit = load_json(STRICT_AUDIT)
    manifest = load_json(STRICT_MANIFEST)
    require(manifest.get("candidate_only") is True, "strict batch06 must remain candidate-only")
    require(audit.get("candidate_only") is True, "strict batch06 audit must remain candidate-only")
    require(manifest.get("output") == EXPECTED_STRICT_PROFILE, "strict batch06 manifest drift")
    require(
        audit.get("output_event_profile") == EXPECTED_STRICT_PROFILE,
        "strict batch06 audit drift",
    )
    return event, header, LoadedTable(tuple(table.texts), strict_profile), {
        "workstream": STRICT_WORKSTREAM,
        "candidate_relative": relative(STRICT_ROOT),
        "event_relative": relative(STRICT_EVENT),
        "candidate_manifest": file_record(STRICT_MANIFEST),
        "audit": file_record(STRICT_AUDIT),
        "profile": strict_profile,
        "candidate_only": True,
        "strict_predecessor": manifest.get("predecessor"),
    }


def load_direct_contexts() -> tuple[Mapping[str, LoadedTable], Mapping[str, Any]]:
    tables: dict[str, LoadedTable] = {}
    for language, path in DIRECT_CONTEXT_PATHS.items():
        tables[language] = load_packed_table(
            path, EXPECTED_DIRECT_PROFILES[language], f"direct-PC {language}"
        )
    return tables, {language: table.profile for language, table in tables.items()}


def load_reservations(
    strict_names: Sequence[str],
) -> tuple[Mapping[str, Mapping[str, Any]], Mapping[str, Any]]:
    require(
        sha256(RESERVATION_MANIFEST.read_bytes()) == EXPECTED_RESERVATION_SHA256,
        "reservation manifest hash drift",
    )
    payload = load_json(RESERVATION_MANIFEST)
    raw_reservations = payload.get("reservations")
    require(isinstance(raw_reservations, dict), "reservation map missing")
    result: dict[str, Mapping[str, Any]] = {}
    for token, record in raw_reservations.items():
        require(
            isinstance(token, str) and NUMERIC_RUNTIME_RE.fullmatch(token) is not None,
            f"bad reservation token: {token!r}",
        )
        require(isinstance(record, dict), f"bad reservation row: {token}")
        name_id = int(record["source_name_id"])
        require(0 <= name_id < len(strict_names), f"reservation name id range: {token}")
        display = ESC_RE.sub(
            "", normalized_linebreaks(strict_names[name_id])
        ).replace("\n", " ")
        measured_raw = sum(
            RAW_FULL_WIDTH_PX if is_full_width_visible(ch) else RAW_HALF_WIDTH_PX
            for ch in display
        )
        require(
            measured_raw == int(record["reserved_full_name_width_px"]),
            f"reservation width drift: {token}",
        )
        result[token] = record
    return result, {
        "relative_path": relative(RESERVATION_MANIFEST),
        "sha256": EXPECTED_RESERVATION_SHA256,
        "schema": payload.get("schema"),
        "reservation_count": len(result),
        "policy": (
            "Per referenced runtime token only; raw reservation is scaled by 30/48 "
            "and each audit record remains runtime_proven=false."
        ),
    }


def artifact_direct_sources(
    artifact_name: str, entry_id: int, row: Mapping[str, Any], key: str
) -> Mapping[str, str]:
    raw = row.get(key)
    require(isinstance(raw, dict), f"{artifact_name}:{entry_id} direct source map missing")
    result: dict[str, str] = {}
    for language in ("jp", "en", "sc", "tc"):
        value = raw.get(language)
        if isinstance(value, str):
            result[language] = value
        elif isinstance(value, dict) and isinstance(value.get("text"), str):
            result[language] = value["text"]
        else:
            raise CandidateError(
                f"{artifact_name}:{entry_id} direct {language} source missing"
            )
    return result


def artifact_proposed_signature_matches(
    row: Mapping[str, Any], target_signature: Mapping[str, Any], entry_id: int
) -> None:
    """Compare the two completed-review signature encodings semantically.

    The 6000 review stored runtime tokens as their complete ``[b826]``
    literals, whereas the 7000 review used ``re.findall`` capture groups and
    therefore serialized the same token as ``["b", "826"]``.  The candidate
    always uses complete literals internally, so normalize the artifact-only
    representation before making this additional provenance assertion.
    """

    def normalized_runtime_tokens(value: Any) -> list[str]:
        require(isinstance(value, list), f"{entry_id}: artifact runtime signature malformed")
        normalized: list[str] = []
        for item in value:
            if isinstance(item, str):
                token = item
            elif (
                isinstance(item, list)
                and len(item) == 2
                and isinstance(item[0], str)
                and isinstance(item[1], str)
            ):
                token = f"[{item[0]}{item[1]}]"
            else:
                raise CandidateError(
                    f"{entry_id}: artifact runtime signature item malformed: {item!r}"
                )
            require(
                NUMERIC_RUNTIME_RE.fullmatch(token) is not None,
                f"{entry_id}: artifact runtime token malformed: {token!r}",
            )
            normalized.append(token)
        return normalized

    artifact_signature = row.get("control_signature")
    require(isinstance(artifact_signature, dict), f"{entry_id}: review control signature missing")
    proposed = artifact_signature.get("proposed")
    if isinstance(proposed, dict):
        require(
            proposed.get("esc_tokens") == target_signature["esc_tags"],
            f"{entry_id}: artifact proposed ESC signature drift",
        )
        require(
            normalized_runtime_tokens(proposed.get("runtime_tokens"))
            == target_signature["runtime_tokens"],
            f"{entry_id}: artifact proposed runtime signature drift",
        )
        require(
            proposed.get("printf_tokens") == target_signature["printf_tokens"],
            f"{entry_id}: artifact proposed printf signature drift",
        )
        require(
            proposed.get("terminator_nul_count") == target_signature["nul_count"],
            f"{entry_id}: artifact proposed NUL signature drift",
        )
        return
    require(
        artifact_signature.get("esc") == target_signature["esc_tags"],
        f"{entry_id}: artifact proposed ESC signature drift",
    )
    require(
        normalized_runtime_tokens(artifact_signature.get("runtime_tokens"))
        == target_signature["runtime_tokens"],
        f"{entry_id}: artifact proposed runtime signature drift",
    )
    require(
        artifact_signature.get("printf_tokens") == target_signature["printf_tokens"],
        f"{entry_id}: artifact proposed printf signature drift",
    )
    require(
        artifact_signature.get("nul_count") == target_signature["nul_count"],
        f"{entry_id}: artifact proposed NUL signature drift",
    )


def load_review_artifacts(
    strict_texts: Sequence[str],
) -> tuple[tuple[ReviewRow, ...], Mapping[str, Any], Mapping[str, Any]]:
    combined: list[ReviewRow] = []
    artifact_records: dict[str, Any] = {}
    rowwise_baselines: dict[str, Any] = {}
    all_ids: set[int] = set()
    for artifact_name, spec in EXPECTED_ARTIFACTS.items():
        path = Path(spec["path"])
        blob = path.read_bytes()
        require(
            sha256(blob) == spec["sha256"],
            f"{artifact_name} artifact hash drift",
        )
        document = json.loads(blob.decode("utf-8"))
        require(isinstance(document, dict), f"{artifact_name} artifact root is invalid")
        require(
            document.get("schema") == spec["schema"],
            f"{artifact_name} artifact schema drift",
        )
        entries = document.get("entries")
        require(
            isinstance(entries, list) and len(entries) == spec["expected_count"],
            f"{artifact_name} artifact entry count drift",
        )
        id_key = str(spec["id_key"])
        current_key = str(spec["current_key"])
        direct_key = str(spec["direct_source_key"])
        low, high = spec["id_range"]
        seen: set[int] = set()
        strict_equal_count = 0
        for row in entries:
            require(isinstance(row, dict), f"{artifact_name} entry is invalid")
            entry_id = row.get(id_key)
            current = row.get(current_key)
            proposed = row.get("proposed_ko")
            require(
                type(entry_id) is int and low <= entry_id <= high,
                f"{artifact_name} bad entry id: {entry_id!r}",
            )
            require(entry_id not in seen, f"{artifact_name} duplicate id: {entry_id}")
            require(entry_id not in all_ids, f"review artifacts overlap at {entry_id}")
            seen.add(entry_id)
            all_ids.add(entry_id)
            require(
                isinstance(current, str) and current,
                f"{artifact_name}:{entry_id} reviewed current missing",
            )
            require(
                isinstance(proposed, str) and proposed and "\x00" not in proposed,
                f"{artifact_name}:{entry_id} proposed Korean missing or has NUL",
            )
            require(
                current == strict_texts[entry_id],
                f"{artifact_name}:{entry_id} review baseline does not equal strict batch06",
            )
            strict_equal_count += 1
            direct_sources = artifact_direct_sources(
                artifact_name, entry_id, row, direct_key
            )
            combined.append(
                ReviewRow(
                    entry_id=entry_id,
                    artifact_name=artifact_name,
                    artifact_relative=relative(path),
                    artifact_sha256=str(spec["sha256"]),
                    artifact_schema=str(spec["schema"]),
                    artifact_current=current,
                    proposed=proposed,
                    direct_sources=direct_sources,
                    artifact_row=row,
                )
            )
        require(
            len(seen) == spec["expected_count"],
            f"{artifact_name} coverage drift",
        )
        artifact_records[artifact_name] = {
            "relative_path": relative(path),
            "sha256": str(spec["sha256"]),
            "schema": str(spec["schema"]),
            "entry_count": int(spec["expected_count"]),
            "id_range": list(spec["id_range"]),
        }
        rowwise_baselines[artifact_name] = {
            "artifact_current_key": current_key,
            "strict_input": "batch06",
            "strict_equal_row_count": strict_equal_count,
            "expected_row_count": int(spec["expected_count"]),
            "all_rows_equal": strict_equal_count == int(spec["expected_count"]),
            "note": spec["baseline_note"],
        }
    combined.sort(key=lambda row: row.entry_id)
    reviewed_ids = [row.entry_id for row in combined]
    require(len(combined) == EXPECTED_REVIEWED_COUNT, "combined review count drift")
    require(
        changed_ids_hash(reviewed_ids) == EXPECTED_REVIEWED_IDS_SHA256,
        "combined reviewed ID hash drift",
    )
    return tuple(combined), artifact_records, rowwise_baselines


def line_metrics(
    entry_id: int,
    target: str,
    strict_names: Sequence[str],
    reservations: Mapping[str, Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    lines: list[Mapping[str, Any]] = []
    encoded_lines = normalized_linebreaks(target).split("\n")
    for line_number, line in enumerate(encoded_lines, 1):
        cursor = 0
        visible_parts: list[str] = []
        static_parts: list[str] = []
        runtime_details: list[Mapping[str, Any]] = []
        raw_width = 0
        while cursor < len(line):
            if line[cursor] == "\x1b":
                tag = line[cursor : cursor + 3]
                require(
                    ESC_RE.fullmatch(tag) is not None,
                    f"{entry_id}: bad ESC in line metrics",
                )
                cursor += 3
                continue
            token_match = BRACKET_RE.match(line, cursor)
            if token_match is not None:
                token = token_match.group(0)
                numeric = NUMERIC_RUNTIME_RE.fullmatch(token)
                require(
                    numeric is not None,
                    f"{entry_id}: unresolved nonnumeric bracket token {token}",
                )
                reservation = reservations.get(token)
                require(
                    reservation is not None,
                    f"{entry_id}: runtime reservation missing for {token}",
                )
                name_id = int(numeric.group(2))
                require(
                    0 <= name_id < len(strict_names),
                    f"{entry_id}: runtime name id range {token}",
                )
                display = ESC_RE.sub(
                    "", normalized_linebreaks(strict_names[name_id])
                ).replace("\n", " ")
                reserved_raw = int(reservation["reserved_full_name_width_px"])
                raw_width += reserved_raw
                visible_parts.append(display)
                runtime_details.append(
                    {
                        "token": token,
                        "source_name_id": name_id,
                        "display_string": display,
                        "display_full_width_character_count": sum(
                            is_full_width_visible(ch) for ch in display
                        ),
                        "display_half_width_character_count": sum(
                            not is_full_width_visible(ch) for ch in display
                        ),
                        "reserved_raw_g1n_width_px": reserved_raw,
                        "reserved_effective_width_px": math.ceil(
                            reserved_raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX
                        ),
                        "runtime_proven": False,
                        "scene_limited": True,
                        "basis": (
                            "reviewed reservation manifest applied only to the "
                            "runtime token present on this audit line"
                        ),
                    }
                )
                cursor = token_match.end()
                continue
            character = line[cursor]
            static_parts.append(character)
            visible_parts.append(character)
            raw_width += (
                RAW_FULL_WIDTH_PX
                if is_full_width_visible(character)
                else RAW_HALF_WIDTH_PX
            )
            cursor += 1
        display_string = "".join(visible_parts)
        full_count = sum(is_full_width_visible(ch) for ch in display_string)
        half_count = len(display_string) - full_count
        effective = math.ceil(raw_width * DRAW_FONT_PX / RAW_FULL_WIDTH_PX)
        lines.append(
            {
                "line_number": line_number,
                "line_count": len(encoded_lines),
                "source_line_with_tags_and_tokens": line,
                "display_string": display_string,
                "static_visible_string": "".join(static_parts),
                "raw_g1n_width_px": raw_width,
                "effective_width_px": effective,
                "full_width_character_count": full_count,
                "half_width_character_count": half_count,
                "runtime_reservations": runtime_details,
                "exceeds_912px": effective > MAX_EFFECTIVE_LINE_PX,
                "passes_912px": effective <= MAX_EFFECTIVE_LINE_PX,
            }
        )
    return lines


def changed_ids_hash(ids: Sequence[int]) -> str:
    return sha256(",".join(str(entry_id) for entry_id in ids).encode("ascii"))


def review_reference(row: ReviewRow) -> Mapping[str, Any]:
    return {
        "artifact": {
            "name": row.artifact_name,
            "relative_path": row.artifact_relative,
            "sha256": row.artifact_sha256,
            "schema": row.artifact_schema,
            "entry_id": row.entry_id,
        },
        "artifact_current_ko_utf16le_sha256": text_hash(row.artifact_current),
        "artifact_proposed_ko_utf16le_sha256": text_hash(row.proposed),
        "artifact_review_status": row.artifact_row.get("review_status"),
        "artifact_restoration_strategy": row.artifact_row.get(
            "restoration_strategy"
        ),
        "artifact_direct_pc_source_utf16le_sha256": {
            language: text_hash(value) for language, value in row.direct_sources.items()
        },
    }


def sentinel_records(
    before: Sequence[str], after: Sequence[str], reviewed_ids: set[int]
) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    for entry_id in PROTECTED_SENTINEL_IDS:
        require(0 <= entry_id < len(before), f"sentinel outside table: {entry_id}")
        require(entry_id not in reviewed_ids, f"sentinel overlaps review scope: {entry_id}")
        require(before[entry_id] == after[entry_id], f"sentinel changed: {entry_id}")
        records.append(
            {
                "entry_id": entry_id,
                "before_utf16le_sha256": text_hash(before[entry_id]),
                "after_utf16le_sha256": text_hash(after[entry_id]),
                "unchanged": True,
            }
        )
    return records


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, header, strict, strict_info = load_strict_input()
    direct, direct_profiles = load_direct_contexts()
    require(
        all(len(table.texts) == len(strict.texts) for table in direct.values()),
        "direct context topology drift",
    )
    reservations, reservation_info = load_reservations(strict.texts)
    review_rows, artifact_records, baseline_rows = load_review_artifacts(strict.texts)
    reviewed_ids = [row.entry_id for row in review_rows]
    reviewed_set = set(reviewed_ids)
    planned_changed = [
        row.entry_id
        for row in review_rows
        if row.proposed != strict.texts[row.entry_id]
    ]
    preserved = [
        row.entry_id
        for row in review_rows
        if row.proposed == strict.texts[row.entry_id]
    ]
    require(
        len(planned_changed) == EXPECTED_CHANGED_COUNT,
        "planned changed count drift",
    )
    require(
        changed_ids_hash(planned_changed) == EXPECTED_CHANGED_IDS_SHA256,
        "planned changed ID hash drift",
    )
    require(len(preserved) == EXPECTED_PRESERVED_COUNT, "preserved count drift")
    require(
        changed_ids_hash(preserved) == EXPECTED_PRESERVED_IDS_SHA256,
        "preserved ID hash drift",
    )

    texts = list(strict.texts)
    changed_rows: list[Mapping[str, Any]] = []
    for review in review_rows:
        entry_id = review.entry_id
        current = strict.texts[entry_id]
        target = review.proposed
        for language, source in review.direct_sources.items():
            require(
                source == direct[language].texts[entry_id],
                f"{entry_id}: {language} direct source no longer matches review evidence",
            )
        current_signature = protected_signature(current)
        target_signature = protected_signature(target)
        jp_signature = protected_signature(direct["jp"].texts[entry_id])
        require(
            current_signature == jp_signature,
            f"{entry_id}: strict Korean and direct JP control signature drift",
        )
        require(
            target_signature == current_signature,
            f"{entry_id}: proposed control, colour, runtime, or terminator drift",
        )
        artifact_proposed_signature_matches(
            review.artifact_row, target_signature, entry_id
        )
        require(target_signature["nul_count"] == 0, f"{entry_id}: target embedded NUL")
        require(
            target_signature["other_c0_controls"] == [],
            f"{entry_id}: target unknown control",
        )
        assert_colour_layout(current, entry_id)
        assert_colour_layout(target, entry_id)
        target_lines = line_metrics(entry_id, target, strict.texts, reservations)
        require(
            1 <= len(target_lines) <= MAX_LINES,
            f"{entry_id}: target line count outside 1..{MAX_LINES}",
        )
        require(
            not any(line["exceeds_912px"] for line in target_lines),
            f"{entry_id}: target line exceeds 912px",
        )
        if target == current:
            continue
        texts[entry_id] = target
        changed_rows.append(
            {
                "entry_id": entry_id,
                "changed": True,
                "review_source_reference": review_reference(review),
                "strict_batch06_ko": current,
                "target_ko": target,
                "strict_batch06_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "direct_pc_sources": review.direct_sources,
                "direct_pc_source_utf16le_sha256": {
                    language: text_hash(value)
                    for language, value in review.direct_sources.items()
                },
                "strict_batch06_control_signature": current_signature,
                "target_control_signature": target_signature,
                "direct_pc_jp_control_signature": jp_signature,
                "direct_pc_control_signatures": {
                    language: protected_signature(value)
                    for language, value in review.direct_sources.items()
                },
                "strict_ko_matches_direct_jp_protected_signature": True,
                "target_matches_strict_protected_signature": True,
                "target_line_count": len(target_lines),
                "max_four_lines_pass": True,
                "any_line_exceeds_912px": False,
                "target_lines": target_lines,
                "japanese_source_line_breaks_used": False,
                "jp_lf_policy": "ignored",
                "sentence_shortening_or_deletion_allowed": False,
                "terminator_policy": (
                    "UTF-16LE NUL terminator is serialized only by "
                    "rebuild_message_table"
                ),
            }
        )

    raw_before = decompress_wrapper(before_event)[1]
    rebuilt_raw = rebuild_message_table(parse_message_table(raw_before), texts)
    event = recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw = decompress_wrapper(event)
    after = parse_message_table(after_raw)
    require(after_raw == rebuilt_raw, "candidate raw reparse mismatch")
    actual_changed = [
        index
        for index, (before_text, after_text) in enumerate(zip(strict.texts, after.texts))
        if before_text != after_text
    ]
    require(
        actual_changed == planned_changed,
        "candidate changed IDs are not the exact reviewed plan",
    )
    require(
        len(changed_rows) == len(actual_changed) == EXPECTED_CHANGED_COUNT,
        "changed row audit count drift",
    )
    sentinels = sentinel_records(strict.texts, after.texts, reviewed_set)
    output_profile = packed_profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        require(output_profile == EXPECTED_OUTPUT_PROFILE, "candidate output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-manual-compact-static007-6000-7999-restore-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "strict_korean_input_only": relative(STRICT_EVENT),
            "strict_input_profile": strict.profile,
            "allowed_korean_review_proposed_sources": artifact_records,
            "direct_pc_context_read_only": True,
            "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
            "japanese_source_line_breaks_used": False,
            "korean_sentence_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "network_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "authority": "Static Patch 007 PK event dialogue baseline",
            "raw_g1n_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_px": RAW_HALF_WIDTH_PX,
            "raw_g1n_hard_limit_px": MAX_RAW_LINE_PX,
            "runtime_font_px": DRAW_FONT_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_hard_limit_px": MAX_EFFECTIVE_LINE_PX,
            "max_lines": MAX_LINES,
            "runtime_reservation_policy": reservation_info,
        },
        "source_profiles": {
            "strict_batch06": strict_info,
            "direct_pc_contexts": direct_profiles,
            "review_artifacts": artifact_records,
            "review_baseline_rowwise_assertions": baseline_rows,
        },
        "coverage": {
            "reviewed_row_count": len(review_rows),
            "reviewed_id_range_groups": [[6000, 6999], [7000, 7999]],
            "reviewed_row_ids_sha256": changed_ids_hash(reviewed_ids),
            "planned_changed_row_count": len(planned_changed),
            "planned_changed_row_ids": planned_changed,
            "planned_changed_row_ids_sha256": changed_ids_hash(planned_changed),
            "preserved_review_row_count": len(preserved),
            "preserved_review_row_ids": preserved,
            "preserved_review_row_ids_sha256": changed_ids_hash(preserved),
            "protected_nonreviewed_sentinels": sentinels,
        },
        "actual_changed_row_ids": actual_changed,
        "actual_changed_row_ids_sha256": changed_ids_hash(actual_changed),
        "actual_changed_row_count": len(actual_changed),
        "exact_reviewed_diff": True,
        "output_event_profile": output_profile,
        "rows": changed_rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-manual-compact-static007-6000-7999-restore-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": relative(TMP_ROOT),
        "resource": RESOURCE.as_posix(),
        "predecessor": {
            "workstream": STRICT_WORKSTREAM,
            "candidate_relative": relative(STRICT_EVENT),
            "profile": strict.profile,
            "strict_on_disk": True,
            "only_korean_predecessor_input": True,
        },
        "review_artifacts": artifact_records,
        "review_baseline_rowwise_assertions": baseline_rows,
        "direct_pc_context_profiles": direct_profiles,
        "changed_row_ids": actual_changed,
        "changed_row_ids_sha256": changed_ids_hash(actual_changed),
        "changed_row_count": len(actual_changed),
        "preserved_review_row_ids": preserved,
        "preserved_review_row_count": len(preserved),
        "protected_nonreviewed_sentinels": sentinels,
        "exact_reviewed_diff": True,
        "output": output_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event=event, profile=output_profile, audit=audit, manifest=manifest)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CandidateError(f"candidate path leaves tmp root: {resolved}") from exc
    return resolved


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"stale candidate staging path: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / RESOURCE
        event_path.parent.mkdir(parents=True)
        event_path.write_bytes(bundle.event)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(
            canonical_json(bundle.manifest)
        )
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"candidate missing: {root}")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    }
    require(actual_files == expected_files, f"candidate file scope drift: {sorted(actual_files)}")
    require((root / RESOURCE).read_bytes() == bundle.event, "candidate event differs")
    require(
        (root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit),
        "candidate audit differs",
    )
    require(
        (root / "candidate_manifest.v1.json").read_bytes()
        == canonical_json(bundle.manifest),
        "candidate manifest differs",
    )
    return {
        "status": "PASS",
        "candidate_root": relative(root),
        "changed_row_count": bundle.audit["actual_changed_row_count"],
        "changed_row_ids_sha256": bundle.audit["actual_changed_row_ids_sha256"],
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        SCRIPT,
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "test_pc_event_manual_compact_static007_6000_7999_restore_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args(argv).command
    if command == "profile":
        bundle = prepare(require_output_profile=False)
        print(
            json.dumps(
                {
                    "changed_row_count": bundle.audit["actual_changed_row_count"],
                    "changed_row_ids_sha256": bundle.audit[
                        "actual_changed_row_ids_sha256"
                    ],
                    "event_profile": bundle.profile,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    source_whitespace_check()
    if command == "build":
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        print(relative(write_candidate(prepare(require_output_profile=True))))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(
        json.dumps(
            {
                "changed_row_ids": bundle.audit["actual_changed_row_ids"],
                "changed_row_ids_sha256": bundle.audit[
                    "actual_changed_row_ids_sha256"
                ],
                "event_profile": bundle.profile,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CandidateError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
