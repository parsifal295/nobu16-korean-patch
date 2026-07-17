#!/usr/bin/env python3
"""Prepare exact-PC-source static-name reading corrections for ``msgdata``.

The audit compares only pristine PC Japanese labels with current PC Korean
tables.  A candidate is admitted solely when replacing every Korean syllable
for Japanese ``tsu`` with the established Korean ``ssu`` spelling makes the
complete static ``msgdata`` label exactly equal to a current PC ``strdata``
label with the *same pristine Japanese source text*.  PC EN/SC/TC files are
recorded as same-coordinate context only.  Switch resources are never opened.

The output remains a private review artifact.  This script never writes a
game resource.
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
from collections import defaultdict
from pathlib import Path
from typing import Any

from build_semantic_review_inventory_v1 import (
    DEFAULT_ORIGINAL_ROOT,
    DEFAULT_STEAM_ROOT,
    PRISTINE_JP_SHA256,
    language_path,
    parse_common,
    parse_strdata,
)


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
SEMANTIC = REPO / "tmp" / "translation_quality_audit_v1" / "semantic"
OUTPUT = SEMANTIC / "msgdata_tsu_reading_consistency_candidates.v1.jsonl"

MSGDATA_RELATIVE = "MSG_PK/JP/msgdata.bin"
STRDATA_RELATIVE = "MSG/JP/strdata.bin"
EXPECTED_MSGDATA_KO_SHA256 = "7EAA33BC80C021A028660DF1A7934886591A1DA36DB7BC53146749C3A4AEF040"
EXPECTED_STRDATA_KO_SHA256 = "D518A91E36B9A59EAD0B5ED1FDD067941E4BF72E43AFCB19C296C8AD77C8C128"

# Keep the spelling rule codepoint-defined so it cannot be affected by the
# terminal code page.  The proposed reading differs only at these syllables.
TSU = chr(0xCE20)
SSU = chr(0xC4F0)

RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
# Every candidate is a compact static proper-name label.  U+00B7 covers the
# single dot-separated name without permitting arbitrary punctuation or text.
STATIC_KOREAN_NAME_RE = re.compile(r"^[\uac00-\ud7a3\u00b7]+$")
STATIC_JAPANESE_NAME_RE = re.compile(r"^[\u3041-\u30ff\u3400-\u9fff\u3005\uf900-\ufaff]+$")

EXPECTED_CANDIDATE_COUNT = 410
EXPECTED_SOURCE_GROUP_COUNT = 250


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def profile(value: str) -> dict[str, Any]:
    escape_offsets = {
        offset
        for match in ESC_RE.finditer(value)
        for offset in range(match.start(), match.end())
    }
    return {
        "escape_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf": PRINTF_RE.findall(value),
        "linebreaks": LINEBREAK_RE.findall(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip(" \t\r\n"))],
        "trailing_whitespace": value[len(value.rstrip(" \t\r\n")) :],
        "non_escape_controls": [
            f"U+{ord(char):04X}"
            for index, char in enumerate(value)
            if ord(char) < 0x20
            and char not in ("\r", "\n")
            and index not in escape_offsets
        ],
    }


def pc_path(relative: str, language: str, *, pristine_jp: bool = False) -> Path:
    if pristine_jp:
        return DEFAULT_ORIGINAL_ROOT / Path(relative)
    return DEFAULT_STEAM_ROOT / language_path(relative, language)


def atomic_write(path: Path, text: str) -> None:
    tmp_root = (REPO / "tmp").resolve()
    resolved = path.resolve(strict=False)
    if resolved != tmp_root and tmp_root not in resolved.parents:
        raise ValueError(f"output must remain below tmp: {resolved}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_active_msgdata_ids() -> tuple[set[int], list[str]]:
    """Read active outer IDs only, solely to prevent duplicate proposals.

    The generic correction builder owns the list of active artifacts.  Its
    Korean strings are never used as linguistic evidence here; only an outer
    coordinate ID is retained.  ``OUTPUT`` is ignored so this generator is
    idempotent after it is wired into that builder.
    """

    builder_path = REPO / "workstreams" / "translation_quality_corrections_v1" / "build_translation_quality_corrections_v1.py"
    module_spec = importlib.util.spec_from_file_location("quality_correction_builder", builder_path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load active correction builder: {builder_path}")
    builder = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = builder
    module_spec.loader.exec_module(builder)
    spec = next((item for item in builder.SPECS if item.name == "msgdata"), None)
    if spec is None:
        raise RuntimeError("msgdata resource spec is absent from correction builder")

    active_ids: set[int] = set()
    artifact_names: list[str] = []
    for path in spec.proposal_paths:
        path = Path(path)
        if path.resolve() == OUTPUT.resolve():
            continue
        if path == builder.AUTONOMOUS_WORDING_OVERLAY:
            continue
        if not path.is_file():
            raise ValueError(f"active msgdata artifact is absent: {path}")
        artifact_names.append(path.name)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"active artifact row is not an object: {path}:{line_number}")
            declared_resource = row.get("resource")
            if declared_resource is not None and declared_resource != "msgdata":
                continue
            identifier = row.get("id")
            if isinstance(identifier, bool) or not isinstance(identifier, int) or identifier < 0:
                raise ValueError(f"active msgdata artifact has invalid id: {path}:{line_number}")
            active_ids.add(identifier)
    return active_ids, artifact_names


def load_inputs() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    paths = {
        "msgdata_jp": pc_path(MSGDATA_RELATIVE, "JP", pristine_jp=True),
        "msgdata_ko": pc_path(MSGDATA_RELATIVE, "JP"),
        "msgdata_en": pc_path(MSGDATA_RELATIVE, "EN"),
        "msgdata_sc": pc_path(MSGDATA_RELATIVE, "SC"),
        "msgdata_tc": pc_path(MSGDATA_RELATIVE, "TC"),
        "strdata_jp": pc_path(STRDATA_RELATIVE, "JP", pristine_jp=True),
        "strdata_ko": pc_path(STRDATA_RELATIVE, "JP"),
    }
    hashes = {name: sha256_file(path) for name, path in paths.items()}
    if hashes["msgdata_jp"] != PRISTINE_JP_SHA256[MSGDATA_RELATIVE]:
        raise ValueError("pristine PC Japanese msgdata hash differs")
    if hashes["strdata_jp"] != PRISTINE_JP_SHA256[STRDATA_RELATIVE]:
        raise ValueError("pristine PC Japanese strdata hash differs")
    if hashes["msgdata_ko"] != EXPECTED_MSGDATA_KO_SHA256:
        raise ValueError("live PC Korean msgdata baseline differs")
    if hashes["strdata_ko"] != EXPECTED_STRDATA_KO_SHA256:
        raise ValueError("live PC Korean strdata baseline differs")

    tables = {
        "msgdata_jp": parse_common(paths["msgdata_jp"]),
        "msgdata_ko": parse_common(paths["msgdata_ko"]),
        "msgdata_en": parse_common(paths["msgdata_en"]),
        "msgdata_sc": parse_common(paths["msgdata_sc"]),
        "msgdata_tc": parse_common(paths["msgdata_tc"]),
        "strdata_jp": parse_strdata(paths["strdata_jp"]),
        "strdata_ko": parse_strdata(paths["strdata_ko"]),
    }
    if len(tables["msgdata_jp"]) != len(tables["msgdata_ko"]):
        raise ValueError("PC msgdata Japanese/Korean coordinate counts differ")
    if set(tables["strdata_jp"]) != set(tables["strdata_ko"]):
        raise ValueError("PC strdata Japanese/Korean coordinate sets differ")
    return tables, hashes


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tables, hashes = load_inputs()
    active_ids, active_artifacts = load_active_msgdata_ids()

    anchors_by_source: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for coordinate, source in tables["strdata_jp"].items():
        anchors_by_source[source].append((coordinate, tables["strdata_ko"][coordinate]))

    candidates: list[dict[str, Any]] = []
    candidate_ids: set[int] = set()
    source_groups: set[str] = set()
    for coordinate in sorted(tables["msgdata_jp"], key=int):
        source = tables["msgdata_jp"][coordinate]
        current = tables["msgdata_ko"][coordinate]
        if TSU not in current:
            continue
        proposed = current.replace(TSU, SSU)
        matching_anchors = [
            (anchor_coordinate, anchor_ko)
            for anchor_coordinate, anchor_ko in anchors_by_source.get(source, [])
            if anchor_ko == proposed
        ]
        if not matching_anchors:
            continue
        if not STATIC_JAPANESE_NAME_RE.fullmatch(source):
            raise ValueError(f"{coordinate}: exact PC source is not a static Japanese name label")
        if not STATIC_KOREAN_NAME_RE.fullmatch(current) or not STATIC_KOREAN_NAME_RE.fullmatch(proposed):
            raise ValueError(f"{coordinate}: Korean label is not a static name spelling")
        if KANA_OR_HAN_RE.search(proposed):
            raise ValueError(f"{coordinate}: Korean proposal retains Japanese/CJK residue")
        if profile(current) != profile(proposed):
            raise ValueError(f"{coordinate}: format profile differs")
        identifier = int(coordinate)
        if identifier in candidate_ids:
            raise ValueError(f"duplicate msgdata candidate id: {identifier}")
        candidate_ids.add(identifier)
        source_groups.add(source)
        anchor_hashes = {
            anchor_coordinate: text_hash(anchor_ko)
            for anchor_coordinate, anchor_ko in sorted(
                matching_anchors,
                key=lambda item: tuple(int(part) for part in item[0].split(":")),
            )
        }
        candidates.append(
            {
                "allowed_format_delta": [],
                "confidence": "high",
                "current_hash": text_hash(current),
                "format_validation": {
                    "escape_tags": "match",
                    "runtime_tokens": "match",
                    "printf": "match",
                    "linebreaks": "match",
                    "outer_whitespace": "match",
                    "static_name_shape": "match",
                },
                "id": identifier,
                "issue_type": "pc_same_source_tsu_reading_inconsistency",
                "jp_source_hash": text_hash(source),
                "ko": current,
                "pc_language_context_hashes": {
                    language: text_hash(tables[f"msgdata_{language}"][coordinate])
                    for language in ("en", "sc", "tc")
                },
                "pc_same_source_anchor_coordinates": anchor_hashes,
                "pc_same_source_anchor_resource": "strdata",
                "pc_same_source_anchor_count": len(anchor_hashes),
                "private_source_text": source,
                "proposed_ko": proposed,
                "rationale": (
                    "The exact pristine PC Japanese static name is already rendered by "
                    "the same Korean spelling in current PC strdata anchors.  The change "
                    "is limited to the established tsu-to-ssu reading within the full label."
                ),
                "reference_file_sha256": {
                    "msgdata_en": hashes["msgdata_en"],
                    "msgdata_sc": hashes["msgdata_sc"],
                    "msgdata_tc": hashes["msgdata_tc"],
                    "strdata_ko": hashes["strdata_ko"],
                },
                "resource": "msgdata",
                "source_file_sha256": hashes["msgdata_jp"],
                "steam_ko_file_sha256": hashes["msgdata_ko"],
                "switch_korean_translation_used": False,
            }
        )

    overlap = sorted(candidate_ids.intersection(active_ids))
    if overlap:
        raise ValueError(f"candidate IDs overlap active msgdata proposals: {overlap[:10]}")
    if len(candidates) != EXPECTED_CANDIDATE_COUNT:
        raise ValueError(f"candidate count drift: {len(candidates)}")
    if len(source_groups) != EXPECTED_SOURCE_GROUP_COUNT:
        raise ValueError(f"source-group count drift: {len(source_groups)}")
    return candidates, {
        "active_artifacts_checked_for_outer_id_overlap": active_artifacts,
        "candidate_count": len(candidates),
        "exact_pc_source_group_count": len(source_groups),
        "game_files_written": False,
        "output": str(OUTPUT),
        "source_policy": "pristine_pc_japanese_plus_current_pc_same_source_anchors_and_pc_en_sc_tc_context_only",
        "switch_korean_translation_used": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the private JSONL artifact")
    args = parser.parse_args()
    rows, summary = build()
    if args.write:
        payload = "".join(
            json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
            for row in rows
        )
        atomic_write(OUTPUT, payload)
        summary["output_sha256"] = sha256_file(OUTPUT)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
