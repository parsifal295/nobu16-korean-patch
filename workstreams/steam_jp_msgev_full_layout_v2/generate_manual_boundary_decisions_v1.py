#!/usr/bin/env python3
"""Freeze the v2 manual-event-boundary provenance table without writing Steam.

This is a development-time classifier only.  It reads the v1 audit and the
installed Steam JP message table, records one decision for every previously
``manual`` LF boundary in both Korean-boundary and dynamic-name review rows,
and writes a source-free JSON artifact.  The later overlay builder consumes
the frozen decisions and must not require Kiwi.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
V1_AUDIT = REPO / "workstreams" / "steam_jp_msgev_full_layout_v1" / "public" / "msgev_full_layout_audit.v1.json"
OUTPUT = WORKSTREAM / "public" / "manual_boundary_decisions.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
ENGINE_ROOT = REPO / "tmp" / "korean_spacing_engine"

sys.path[:0] = [str(TOOLS)]

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-msgev-manual-boundary-decisions.v1"
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
COLOR_SPAN_RE = re.compile(r"\x1bC.(.*?)\x1bCZ", re.DOTALL)
DASHES = frozenset(chr(value) for value in (0x2013, 0x2014, 0x2015))

# These are the corpus-specific places where a hard LF is demonstrably inside
# a Korean construction or a tightly joined typographic construction.  Keeping
# them explicit avoids treating a merely plausible Kiwi parse as authority.
FORCE_CONCAT: dict[tuple[int, int], str] = {
    (4965, 0): "parenthetical_reading_join",
    (4975, 0): "parenthetical_reading_join",
    (6909, 0): "ellipsis_join",
    (6931, 0): "quote_parenthetical_join",
    (7047, 0): "closing_quote_quotative_suffix_join",
    (7070, 1): "closing_quote_quotative_suffix_join",
    (7087, 0): "closing_quote_quotative_suffix_join",
    (7579, 0): "adjacent_quote_join",
    (7620, 1): "ellipsis_join",
    (7801, 0): "adjacent_quote_join",
    (8135, 0): "copula_honorific_ending_join",
    (8503, 0): "copula_adnominal_join",
    (8686, 1): "closing_quote_quotative_suffix_join",
    (8776, 0): "conditional_ending_join",
    (9512, 0): "derivational_verb_join",
    (9580, 1): "adnominal_ending_join",
    (16397, 1): "closing_quote_object_particle_join",
}


class DecisionError(ValueError):
    """Raised when source provenance or decision coverage differs."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def file_spec(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"size": len(data), "sha256": sha256(data)}


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise DecisionError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_kiwi() -> tuple[Any, str]:
    if not ENGINE_ROOT.is_dir():
        raise DecisionError(f"Kiwi engine root is absent: {ENGINE_ROOT}")
    sys.path.insert(0, str(ENGINE_ROOT))
    try:
        import kiwipiepy  # type: ignore[import-not-found]
        from kiwipiepy import Kiwi  # type: ignore[import-not-found]
    except ImportError as exc:
        raise DecisionError("the local Kiwi spacing engine cannot be imported") from exc
    return Kiwi(), str(kiwipiepy.__version__)


def color_names(texts: Iterable[str]) -> set[str]:
    result: set[str] = set()
    for value in texts:
        for match in COLOR_SPAN_RE.finditer(value):
            name = match.group(1).replace("\r", "").replace("\n", "").strip()
            if len(name) >= 2 and "[" not in name and "]" not in name:
                result.add(name)
    return result


def visible_text(value: str) -> str:
    return ESC_RE.sub("", value)


def flat_visible_and_manual_offsets(value: str, operations: list[str]) -> tuple[str, list[int]]:
    visible = visible_text(value)
    matches = list(LINEBREAK_RE.finditer(visible))
    require(len(matches), len(operations), "manual row LF count")
    pieces: list[str] = []
    offsets: list[int] = []
    cursor = 0
    length = 0
    for match, operation in zip(matches, operations):
        piece = visible[cursor : match.start()]
        pieces.append(piece)
        length += len(piece)
        if operation == "manual":
            offsets.append(length)
        cursor = match.end()
    pieces.append(visible[cursor:])
    return "".join(pieces), offsets


def kiwi_relation(flat: str, spaced: str, offset: int) -> str:
    before = [(index, char) for index, char in enumerate(flat) if not char.isspace()]
    after = [(index, char) for index, char in enumerate(spaced) if not char.isspace()]
    if [char for _index, char in before] != [char for _index, char in after]:
        raise DecisionError("Kiwi altered the non-whitespace skeleton")
    mapped = {input_index: output_index for (input_index, _), (output_index, _) in zip(before, after)}
    left = offset - 1
    while left >= 0 and flat[left].isspace():
        left -= 1
    right = offset
    while right < len(flat) and flat[right].isspace():
        right += 1
    if left < 0 or right >= len(flat):
        raise DecisionError("manual LF does not have visible neighbors")
    return "space" if any(char.isspace() for char in spaced[mapped[left] + 1 : mapped[right]]) else "concat"


def dynamic_token_adjacent(flat: str, offset: int) -> bool:
    return flat[:offset].endswith("]") or flat[offset:].startswith("[")


def previous_visible_char(flat: str, offset: int) -> str:
    index = offset - 1
    while index >= 0 and flat[index].isspace():
        index -= 1
    return flat[index] if index >= 0 else ""


def resolve_operation(
    entry_id: int,
    lf_ordinal: int,
    flat: str,
    offset: int,
    relation: str,
) -> tuple[str, str]:
    forced_reason = FORCE_CONCAT.get((entry_id, lf_ordinal))
    if forced_reason is not None:
        return "concat", forced_reason
    if dynamic_token_adjacent(flat, offset):
        return "space", "dynamic_token_boundary_default_space"
    if previous_visible_char(flat, offset) in DASHES:
        return "concat", "typographic_dash_join"
    if relation == "space":
        return "space", "kiwi_space_color_name_dictionary"
    return "space", "kiwi_concat_rejected_as_independent_eojeol"


def load_source_table(steam_root: Path) -> tuple[Path, Any, dict[str, Any]]:
    path = (steam_root / RESOURCE).resolve(strict=True)
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    return path, table, {"packed": file_spec(path), "raw_sha256": sha256(raw), "string_count": table.string_count}


def generate(steam_root: Path) -> dict[str, Any]:
    audit = json.loads(V1_AUDIT.read_text(encoding="utf-8"))
    if audit.get("schema") != "nobu16.kr.steam-jp-msgev-full-layout-audit.v1":
        raise DecisionError("v1 audit schema differs")
    source_path, table, source = load_source_table(steam_root)
    require(audit.get("source"), source, "v1 audit source profile")
    kiwi, kiwi_version = load_kiwi()
    names = color_names(table.texts)
    for name in names:
        kiwi.add_user_word(name, "NNP", 10.0)

    korean_rows = [
        row for row in audit.get("rows", []) if row.get("classification") == "manual_korean_boundary_review"
    ]
    protected_rows = [
        row for row in audit.get("rows", []) if row.get("classification") == "manual_protected_token_review"
    ]
    rows = [*korean_rows, *protected_rows]
    decisions: list[dict[str, Any]] = []
    found_force: set[tuple[int, int]] = set()
    for row in rows:
        entry_id = row.get("id")
        operations = row.get("newline_operations")
        if type(entry_id) is not int or not isinstance(operations, list):
            raise DecisionError("v1 manual row shape is invalid")
        source_text = table.texts[entry_id]
        require(text_hash(source_text), row.get("preimage_utf16le_sha256"), f"manual row {entry_id} preimage")
        flat, manual_offsets = flat_visible_and_manual_offsets(source_text, operations)
        spaced = kiwi.space(flat)
        manual_index = 0
        for lf_ordinal, previous_operation in enumerate(operations):
            if previous_operation != "manual":
                continue
            offset = manual_offsets[manual_index]
            manual_index += 1
            relation = kiwi_relation(flat, spaced, offset)
            operation, reason = resolve_operation(entry_id, lf_ordinal, flat, offset, relation)
            if (entry_id, lf_ordinal) in FORCE_CONCAT:
                found_force.add((entry_id, lf_ordinal))
            decisions.append(
                {
                    "id": entry_id,
                    "lf_ordinal": lf_ordinal,
                    "operation": operation,
                    "preimage_utf16le_sha256": row["preimage_utf16le_sha256"],
                    "reason": reason,
                    "kiwi_relation": relation,
                    "kiwi_version": kiwi_version,
                }
            )
        require(manual_index, len(manual_offsets), f"manual offset coverage {entry_id}")
    require(found_force, set(FORCE_CONCAT), "forced-concat corpus coverage")
    decisions.sort(key=lambda item: (int(item["id"]), int(item["lf_ordinal"])))
    counts = Counter(item["operation"] for item in decisions)
    reason_counts = Counter(item["reason"] for item in decisions)
    return {
        "schema": SCHEMA,
        "resource": RESOURCE.as_posix(),
        "source": source,
        "selection": {
            "v1_audit_relative_path": "workstreams/steam_jp_msgev_full_layout_v1/public/msgev_full_layout_audit.v1.json",
            "manual_korean_boundary_review_row_count": len(korean_rows),
            "manual_protected_token_review_row_count": len(protected_rows),
            "reviewed_row_count": len(rows),
            "manual_linebreak_decision_count": len(decisions),
        },
        "decision_engine": {
            "name": "kiwipiepy",
            "version": kiwi_version,
            "color_name_user_dictionary_count": len(names),
            "source_text_stored": False,
            "steam_files_written": False,
        },
        "counts": {"operations": dict(sorted(counts.items())), "reasons": dict(sorted(reason_counts.items()))},
        "decisions": decisions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        document = generate(args.steam_root)
        output = args.output.resolve(strict=False)
        expected = OUTPUT.resolve(strict=False)
        if output != expected:
            raise DecisionError("output must be the v2 public provenance artifact")
        atomic_write(output, canonical_json(document))
        print("status=PASS")
        print(f"output={output}")
        print(f"decisions={document['selection']['manual_linebreak_decision_count']}")
        print("steam_files_written=False")
        return 0
    except (DecisionError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
