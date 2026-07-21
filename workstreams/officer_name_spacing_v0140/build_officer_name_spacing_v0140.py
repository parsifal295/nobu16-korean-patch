#!/usr/bin/env python3
"""Repair missing Korean separators in dynamically composed officer names.

The game formatter concatenates a surname component and a given-name component
without inserting a separator for Hangul.  The ordinary Korean name-component
overlay therefore stores a trailing ASCII space on surname components.  This
workstream first finds matching, space-separated Korean full names for exact
pristine-JP component pairs, then limits the repair to an isolated surname-only
alias block. Pair evidence alone is not sufficient: shared components can serve
as either a surname or a given name.

It never writes an installed game file.  ``build`` writes candidates only to
the ignored ``private/candidate`` directory; public artifacts contain hashes,
coordinates, and counts but no game text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "switch_msgbre_v11"
for path in (TOOLS, STRDATA_TOOLS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.officer-name-spacing.v1"
VALIDATION_SCHEMA = "nobu16.kr.officer-name-spacing-validation.v1"
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
ORIGINAL_ROOT = (
    Path(r"F:\Games\NOBU16\KR_PATCH_BACKUP")
    / "file_only_transaction"
    / "jp-runtime-wave05-20260715-v1"
    / "originals"
)

PK_RESOURCE = "MSG_PK/JP/msgdata.bin"
EVENT_RESOURCE = "MSG_PK/JP/msgev.bin"

PK_CURRENT_SHA256 = "F9ACF8E013EBF942C7E39D73A927D591591BF5448AAC66519CEB3FE713A03EF6"
EVENT_CURRENT_SHA256 = "D20E1CC9E1014473DCFCE7C247721FFA912955B0CB6EEA71BB00BD055977FB4E"
PK_JP_SHA256 = "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38"
EVENT_JP_SHA256 = "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002"

DISPLAY_GROUPS: tuple[tuple[str, int, int], ...] = (
    ("primary", 0, 3_332),
    ("fictional_princess", 6_664, 100),
    ("secondary_name_dictionary", 6_864, 1_137),
)
# Exact-pair evidence finds 57 missing-space display components. Most are
# shared message strings and cannot be safely changed globally: a component
# which is a surname in one officer name may be a given name in another.
EVIDENCE_IDS_SHA256 = "804BC2CDEBDC4F086161EFC6E9F2572531B9CD2006729FEC6CDBAB69FDB3358E"
EVIDENCE_COUNT = 57

# 939..943 are the dedicated alias-surname block immediately before the given
# name block (944 onward). Each has direct pristine-JP/current-Korean full-name
# evidence and no shared-given-name role in the audited component catalog.
SAFE_SURNAME_ONLY_IDS = (939, 940, 941, 942, 943)
EXPECTED_CANDIDATE_COUNT = len(SAFE_SURNAME_ONLY_IDS)
EXPECTED_IDS_SHA256 = "BC9431128CC89AE0F6403F4B61C5A8D1782B15D81341744B833F3B34737DA72A"

PUBLIC_PATH = WORKSTREAM / "public" / "officer_name_spacing.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
REPORT_PATH = WORKSTREAM / "REPORT_KO.md"
PRIVATE_REVIEW_PATH = WORKSTREAM / "private" / "officer_name_spacing.review.v1.json"
PRIVATE_CANDIDATE_ROOT = WORKSTREAM / "private" / "candidate"
# An early draft created a Base candidate before the distinct Base display route
# was identified.  This generator now owns a PK-only candidate set, so remove
# that stale private output whenever it rebuilds.
STALE_PRIVATE_CANDIDATE_PATHS = (
    PRIVATE_CANDIDATE_ROOT / "MSG" / "JP" / "strdata.bin",
)


class SpacingError(RuntimeError):
    """Raised when an input, mapping, or candidate invariant changes."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SpacingError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any, *, source_free: bool = False) -> bytes:
    return (
        json.dumps(value, ensure_ascii=source_free, indent=2, sort_keys=True) + "\n"
    ).encode("ascii" if source_free else "utf-8")


def canonical_id_hash(ids: Sequence[int]) -> str:
    return sha256_bytes(json.dumps(list(ids), separators=(",", ":")).encode("ascii"))


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def checked_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    require(root_resolved == path or root_resolved in path.parents, f"path escapes root: {relative}")
    return path


def load_common(path: Path, expected_sha256: str, label: str) -> tuple[bytes, bytes, MessageTable]:
    packed = path.read_bytes()
    require(sha256_bytes(packed) == expected_sha256, f"{label} packed SHA-256 differs")
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, f"{label} parse/rebuild differs")
    return packed, raw, table


def has_control(text: str) -> bool:
    return any(character in text for character in ("\x1b", "\r", "\n", "\x00"))


def display_ids() -> tuple[int, ...]:
    values: list[int] = []
    for _name, start, count in DISPLAY_GROUPS:
        values.extend(range(start, start + count))
    return tuple(values)


def derive_candidates(
    source_components: Sequence[str],
    current_components: Sequence[str],
    source_events: Sequence[str],
    current_events: Sequence[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return source-free operations and text-bearing private evidence.

    Exact full-name evidence first identifies possible omissions. It then
    admits only the audited alias-surname block; arbitrary shared components
    are excluded because the same display entry can also be a given name.
    """

    require(len(source_events) <= len(current_events), "event table count shrank")
    by_source: dict[str, list[int]] = defaultdict(list)
    for entry_id in display_ids():
        source = source_components[entry_id]
        if source and not has_control(source):
            by_source[source].append(entry_id)

    evidence: dict[int, list[dict[str, Any]]] = defaultdict(list)
    # The current Korean table has six appended rows; original coordinates are
    # otherwise prefix-aligned, which is the same compatibility rule used by
    # the existing message audit chain.
    for event_id, (source_full, current_full) in enumerate(
        zip(source_events, current_events[: len(source_events)], strict=True)
    ):
        if not source_full or has_control(source_full) or has_control(current_full):
            continue
        for split in range(1, len(source_full)):
            for surname_id in by_source.get(source_full[:split], ()):
                surname = current_components[surname_id]
                if surname.endswith(" ") or not surname or surname.rstrip(" ") != surname:
                    continue
                for given_id in by_source.get(source_full[split:], ()):
                    given = current_components[given_id]
                    if not given or given != given.rstrip(" "):
                        continue
                    if surname + " " + given != current_full:
                        continue
                    evidence[surname_id].append(
                        {
                            "event_id": event_id,
                            "given_id": given_id,
                            "source_full": source_full,
                            "current_full": current_full,
                            "source_surname": source_components[surname_id],
                            "current_surname": surname,
                            "source_given": source_components[given_id],
                            "current_given": given,
                        }
                    )

    evidence_ids = sorted(evidence)
    require(len(evidence_ids) == EVIDENCE_COUNT, "pair-evidence count differs")
    require(canonical_id_hash(evidence_ids) == EVIDENCE_IDS_SHA256, "pair-evidence ID set differs")
    candidate_ids = list(SAFE_SURNAME_ONLY_IDS)
    require(set(candidate_ids).issubset(evidence), "a safe surname-only component lost its full-name evidence")
    require(len(candidate_ids) == EXPECTED_CANDIDATE_COUNT, "candidate count differs")
    require(canonical_id_hash(candidate_ids) == EXPECTED_IDS_SHA256, "candidate ID set differs")
    operations: list[dict[str, Any]] = []
    private_rows: list[dict[str, Any]] = []
    for entry_id in candidate_ids:
        before = current_components[entry_id]
        after = before + " "
        rows = evidence[entry_id]
        require(before and before == before.rstrip(" "), f"candidate {entry_id} is not a bare display component")
        require(all(row["current_surname"] == before for row in rows), f"candidate {entry_id} evidence differs")
        operations.append(
            {
                "display_id": entry_id,
                "source_display_utf16le_sha256": text_hash(source_components[entry_id]),
                "current_display_utf16le_sha256": text_hash(before),
                "replacement_utf16le_sha256": text_hash(after),
                "adds_ascii_space": True,
                "event_full_name_evidence_count": len(rows),
            }
        )
        private_rows.append(
            {
                "display_id": entry_id,
                "source_display": source_components[entry_id],
                "current_display": before,
                "replacement": after,
                "evidence": rows,
            }
        )
    return operations, private_rows


def rebuild_pk(table: MessageTable, operations: Sequence[Mapping[str, Any]]) -> bytes:
    texts = list(table.texts)
    changed: set[int] = set()
    for operation in operations:
        entry_id = int(operation["display_id"])
        before = texts[entry_id]
        require(text_hash(before) == operation["current_display_utf16le_sha256"], f"PK source text differs at {entry_id}")
        texts[entry_id] = before + " "
        changed.add(entry_id)
    rebuilt = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt)
    require(reparsed.texts == tuple(texts), "PK candidate parse differs")
    for entry_id, (before, after) in enumerate(zip(table.texts, reparsed.texts, strict=True)):
        if entry_id not in changed:
            require(before == after, f"PK non-target field changed at {entry_id}")
    return rebuilt


def build_model() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, bytes]]:
    original_pk_path = checked_path(ORIGINAL_ROOT, PK_RESOURCE)
    original_event_path = checked_path(ORIGINAL_ROOT, EVENT_RESOURCE)
    current_pk_path = checked_path(STEAM_ROOT, PK_RESOURCE)
    current_event_path = checked_path(STEAM_ROOT, EVENT_RESOURCE)

    original_pk_packed, _original_pk_raw, original_pk = load_common(original_pk_path, PK_JP_SHA256, "pristine PK msgdata")
    original_event_packed, _original_event_raw, original_event = load_common(original_event_path, EVENT_JP_SHA256, "pristine PK msgev")
    current_pk_packed, _current_pk_raw, current_pk = load_common(current_pk_path, PK_CURRENT_SHA256, "current Steam PK msgdata")
    _current_event_packed, _current_event_raw, current_event = load_common(current_event_path, EVENT_CURRENT_SHA256, "current Steam PK msgev")
    # Current Korean resources retain a few later-added strings, but the
    # complete name-component and event-name ranges used below are aligned.
    require(len(original_pk.texts) == 29_210 and len(current_pk.texts) == 29_218, "PK msgdata string count differs")
    require(len(original_event.texts) == 17_910 and len(current_event.texts) == 17_916, "PK msgev string count differs")

    pk_operations, private_rows = derive_candidates(
        original_pk.texts,
        current_pk.texts,
        original_event.texts,
        current_event.texts,
    )
    pk_raw = rebuild_pk(current_pk, pk_operations)
    pk_candidate = recompress_wrapper(pk_raw, current_pk_packed)
    require(decompress_wrapper(pk_candidate)[1] == pk_raw, "PK wrapper round-trip differs")

    ids = [int(operation["display_id"]) for operation in pk_operations]
    public = {
        "schema": SCHEMA,
        "source_free": True,
        "source_text_emitted": False,
        "scope": {
            "name_component_display_fields_only": True,
            "furigana_reading_fields_changed": False,
            "event_body_text_changed": False,
            "base_strdata_changed": False,
            "steam_game_resource_written": False,
            "derivation": "pristine-PC-JP component pair plus current-Steam-PK spaced full-name evidence, restricted to the audited surname-only alias block",
        },
        "candidate_ids_sha256": canonical_id_hash(ids),
        "candidate_count": len(ids),
        "resources": {
            "MSG_PK/JP/msgdata.bin": {
                "source": {"sha256": PK_CURRENT_SHA256, "size": len(current_pk_packed)},
                "target": {"sha256": sha256_bytes(pk_candidate), "size": len(pk_candidate)},
                "operations": pk_operations,
            },
        },
    }
    require(canonical_json(public, source_free=True).isascii(), "public artifact is not source-free")
    private = {
        "schema": "nobu16.kr.officer-name-spacing-private-review.v1",
        "rows": private_rows,
    }
    validation = {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "candidate_count": len(ids),
        "candidate_ids_sha256": canonical_id_hash(ids),
        "input_file_sha256": {
            PK_RESOURCE: PK_CURRENT_SHA256,
            EVENT_RESOURCE: EVENT_CURRENT_SHA256,
        },
        "proofs": {
            "pristine_jp_pair_derivation": True,
            "current_korean_full_name_space_evidence": True,
            "shared_or_ambiguous_component_evidence_excluded": True,
            "surname_only_alias_block_verified": True,
            "pk_parse_rebuild_verified": True,
            "non_target_fields_preserved": True,
            "reading_fields_preserved": True,
            "event_body_preserved": True,
            "steam_game_resource_written": False,
        },
    }
    candidates = {PK_RESOURCE: pk_candidate}
    return public, private, validation, candidates


def report_payload(validation: Mapping[str, Any]) -> bytes:
    return (
        "# 동적 무장 성명 공백 복구\n\n"
        "한글 성명 조합기는 성·이름 사이에 자동 공백을 넣지 않는다. 따라서 현재 Steam "
        "PK `msgev.bin`의 공백 포함 성명과 원본 PC JP 조합을 함께 대조했다. 다만 성과 "
        "이름 양쪽으로 재사용되는 조각은 제외하고, 전용 별칭 성 블록에서 확인된 "
        f"{validation['candidate_count']}개에만 끝 공백 하나를 복구했다.\n\n"
        "- 후리가나 독음 칸은 바꾸지 않는다.\n"
        "- 이벤트 본문과 정적 전체 성명은 바꾸지 않는다.\n"
        "- 성·이름 겸용 조각 52개는 다른 무장명을 깨뜨릴 수 있어 보류한다.\n"
        "- Base `strdata.bin`은 이식하지 않는다. 그 표시 경로는 별도 실게임 검증이 필요하다.\n"
        "- 후보는 작업 디렉터리에만 생성하며 Steam 설치 파일은 쓰지 않는다.\n"
    ).encode("utf-8")


def payloads(
    public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any]
) -> dict[Path, bytes]:
    return {
        PUBLIC_PATH: canonical_json(public, source_free=True),
        PRIVATE_REVIEW_PATH: canonical_json(private),
        VALIDATION_PATH: canonical_json(validation, source_free=True),
        REPORT_PATH: report_payload(validation),
    }


def write_outputs(
    public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any], candidates: Mapping[str, bytes]
) -> None:
    for path, payload in payloads(public, private, validation).items():
        atomic_write(path, payload)
    for path in STALE_PRIVATE_CANDIDATE_PATHS:
        path.unlink(missing_ok=True)
    for resource, blob in candidates.items():
        atomic_write(PRIVATE_CANDIDATE_ROOT / resource, blob)


def verify_outputs(
    public: Mapping[str, Any], private: Mapping[str, Any], validation: Mapping[str, Any], candidates: Mapping[str, bytes]
) -> None:
    for path, payload in payloads(public, private, validation).items():
        require(path.is_file() and path.read_bytes() == payload, f"generated output differs: {path}")
    for resource, blob in candidates.items():
        path = PRIVATE_CANDIDATE_ROOT / resource
        require(path.is_file() and path.read_bytes() == blob, f"candidate differs: {resource}")
    for path in STALE_PRIVATE_CANDIDATE_PATHS:
        require(not path.exists(), f"stale private candidate remains: {path}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify"))
    args = parser.parse_args(argv)
    try:
        public, private, validation, candidates = build_model()
        if args.command == "build":
            write_outputs(public, private, validation, candidates)
        elif args.command == "verify":
            verify_outputs(public, private, validation, candidates)
    except (OSError, ValueError, SpacingError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "PASS", "candidate_count": validation["candidate_count"], "steam_game_resource_written": False}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
