#!/usr/bin/env python3
"""Assemble the full Steam JP event-layout successor from reviewed inputs.

This is a v0.10/current-Steam successor to ``full_layout_v1``.  It consumes
three frozen kinds of input:

* source-free per-LF Korean boundary decisions;
* source-free runtime-name width reservations; and
* private, reviewed Korean semantic-compaction batches.

The installed game is always read-only.  The resulting overlay is hash-gated
to the current ``msgev`` source and the currently installed event-font metric;
only a candidate below ``tmp`` can be written.
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
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp"
V1_WORKSTREAM = REPO / "workstreams" / "steam_jp_msgev_full_layout_v1"
V1_SCRIPT = V1_WORKSTREAM / "build_steam_jp_msgev_full_layout_v1.py"
RESOURCE = "MSG_PK/JP/msgev.bin"
OVERLAY_PATH = WORKSTREAM / "public" / "msgev_ko_steam_jp_full_layout.v2.json"
AUDIT_PATH = WORKSTREAM / "public" / "msgev_full_layout_audit.v2.json"
VERIFICATION_PATH = WORKSTREAM / "verification.v2.json"
DECISIONS_PATH = WORKSTREAM / "public" / "manual_boundary_decisions.v1.json"
RESERVATIONS_PATH = WORKSTREAM / "public" / "runtime_token_reservations.v1.json"
TRANSLATION_ROOT = TMP_ROOT / "steam_jp_msgev_full_layout_v2" / "compaction_review" / "translations"
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "steam_jp_msgev_full_layout_v2" / "candidate"

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgev-full-layout-overlay.v2"
AUDIT_SCHEMA = "nobu16.kr.steam-jp-msgev-full-layout-audit.v2"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-msgev-full-layout-verification.v2"
BUILD_SCHEMA = "nobu16.kr.steam-jp-msgev-full-layout-build.v2"
DECISION_SCHEMA = "nobu16.kr.steam-jp-msgev-manual-boundary-decisions.v1"
RESERVATION_SCHEMA = "nobu16.kr.steam-jp-msgev-runtime-token-reservations.v1"
MAX_LINE_PX = 912
MAX_LINES = 3
FULL_MANUAL_REVIEW_COUNT = 4003
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")


def _load_v1() -> Any:
    spec = importlib.util.spec_from_file_location("nobu16_msgev_full_layout_v1", V1_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load v1 support: {V1_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = _load_v1()


class FullLayoutV2Error(ValueError):
    """The reviewed input or current Steam baseline no longer matches."""


@dataclass(frozen=True)
class Layout:
    ranges: tuple[tuple[int, int], ...]
    actual_widths: tuple[int, ...]
    reserved_widths: tuple[int, ...]
    score: tuple[int, ...]


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise FullLayoutV2Error(f"{label} differs: expected={expected!r}, actual={actual!r}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FullLayoutV2Error(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise FullLayoutV2Error(f"{label} root is not an object")
    return value


def file_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def source_table(steam_root: Path) -> tuple[Path, bytes, bytes, Any]:
    return base.source_table(steam_root)


def current_font(steam_root: Path) -> tuple[Any, dict[str, Any]]:
    return base.font_advance_function(steam_root)


def protected_signature(value: str) -> dict[str, Any]:
    return base.protected_signature(value)


def layout_skeleton(value: str) -> str:
    return base.layout_skeleton(value)


def linebreak_vector(value: str) -> list[str]:
    return base.linebreak_vector(value)


def require_tmp_output_root(path: Path) -> Path:
    return base.safe_output_root(path)


def load_v1_audit() -> tuple[dict[int, dict[str, Any]], dict[int, dict[str, Any]]]:
    audit = read_json(V1_WORKSTREAM / "public" / "msgev_full_layout_audit.v1.json", "v1 audit")
    overlay = read_json(V1_WORKSTREAM / "public" / "msgev_ko_steam_jp_full_layout.v1.json", "v1 overlay")
    rows = audit.get("rows")
    entries = overlay.get("entries")
    if not isinstance(rows, list) or not isinstance(entries, list):
        raise FullLayoutV2Error("v1 artifact lists are absent")
    row_map: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or type(row.get("id")) is not int or row["id"] in row_map:
            raise FullLayoutV2Error("v1 audit row is malformed")
        row_map[row["id"]] = row
    entry_map: dict[int, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get("id")) is not int or entry["id"] in entry_map:
            raise FullLayoutV2Error("v1 overlay entry is malformed")
        entry_map[entry["id"]] = entry
    return row_map, entry_map


def load_decisions() -> dict[tuple[int, int], dict[str, str]]:
    document = read_json(DECISIONS_PATH, "manual boundary decisions")
    require(document.get("schema"), DECISION_SCHEMA, "manual boundary decision schema")
    require(document.get("resource"), RESOURCE, "manual boundary decision resource")
    decisions = document.get("decisions")
    if not isinstance(decisions, list):
        raise FullLayoutV2Error("manual boundary decision vector is absent")
    result: dict[tuple[int, int], dict[str, str]] = {}
    for row in decisions:
        if not isinstance(row, dict):
            raise FullLayoutV2Error("manual boundary decision is invalid")
        entry_id = row.get("id")
        ordinal = row.get("lf_ordinal")
        operation = row.get("operation")
        preimage = row.get("preimage_utf16le_sha256")
        reason = row.get("reason")
        if (
            type(entry_id) is not int
            or type(ordinal) is not int
            or operation not in {"space", "concat"}
            or not isinstance(preimage, str)
            or not isinstance(reason, str)
        ):
            raise FullLayoutV2Error("manual boundary decision shape differs")
        key = (entry_id, ordinal)
        if key in result:
            raise FullLayoutV2Error("manual boundary decision is duplicated")
        result[key] = {"operation": operation, "preimage": preimage, "reason": reason}
    return result


def load_reservations() -> tuple[dict[str, int], set[int], dict[str, Any]]:
    document = read_json(RESERVATIONS_PATH, "runtime token reservations")
    require(document.get("schema"), RESERVATION_SCHEMA, "runtime reservation schema")
    require(document.get("resource"), RESOURCE, "runtime reservation resource")
    rows = document.get("reservations")
    excluded = document.get("excluded_protected_rows")
    if not isinstance(rows, dict) or not isinstance(excluded, list):
        raise FullLayoutV2Error("runtime reservation schema differs")
    result: dict[str, int] = {}
    for token, row in rows.items():
        if not isinstance(token, str) or RUNTIME_RE.fullmatch(token) is None or not isinstance(row, dict):
            raise FullLayoutV2Error("runtime reservation row differs")
        width = row.get("reserved_full_name_width_px")
        if type(width) is not int or width <= 0:
            raise FullLayoutV2Error("runtime reservation width differs")
        result[token] = width
    excluded_ids: set[int] = set()
    for row in excluded:
        if not isinstance(row, dict) or type(row.get("id")) is not int:
            raise FullLayoutV2Error("runtime exclusion differs")
        excluded_ids.add(row["id"])
    return result, excluded_ids, document


def source_operations(
    entry_id: int,
    source: str,
    v1_row: Mapping[str, Any],
    decisions: Mapping[tuple[int, int], Mapping[str, str]],
) -> tuple[list[str], list[str]]:
    source_hash = text_hash(source)
    require(source_hash, v1_row.get("preimage_utf16le_sha256"), f"v1 row preimage {entry_id}")
    original = v1_row.get("newline_operations")
    if not isinstance(original, list):
        raise FullLayoutV2Error(f"v1 row newline operation vector absent: {entry_id}")
    matches = list(LINEBREAK_RE.finditer(source))
    require(len(original), len(matches), f"v1 row LF count {entry_id}")
    operations: list[str] = []
    reasons: list[str] = []
    for ordinal, operation in enumerate(original):
        if operation in {"space", "concat"}:
            operations.append(str(operation))
            reasons.append("v1_structural")
            continue
        if operation != "manual":
            raise FullLayoutV2Error(f"unknown v1 LF operation {entry_id}/{ordinal}")
        decision = decisions.get((entry_id, ordinal))
        if decision is None:
            raise FullLayoutV2Error(f"manual LF decision is missing: {entry_id}/{ordinal}")
        require(decision["preimage"], source_hash, f"manual LF decision preimage {entry_id}/{ordinal}")
        operations.append(decision["operation"])
        reasons.append(decision["reason"])
    return operations, reasons


def marked_stream(value: str, operations: Sequence[str]) -> str:
    """Turn only approved source LFs into preferred spaces or concatenation."""

    matches = list(LINEBREAK_RE.finditer(value))
    require(len(matches), len(operations), "approved LF operation count")
    parts: list[str] = []
    last_separator = False

    def append_plain(chunk: str) -> None:
        nonlocal last_separator
        for char in chunk:
            if char == " ":
                if not last_separator:
                    parts.append(" ")
                    last_separator = True
            else:
                parts.append(char)
                last_separator = False

    def append_preferred_space() -> None:
        nonlocal last_separator
        if last_separator:
            parts[-1] = base.INTERNAL_PREFERRED_BREAK
        else:
            parts.append(base.INTERNAL_PREFERRED_BREAK)
            last_separator = True

    cursor = 0
    for match, operation in zip(matches, operations, strict=True):
        append_plain(value[cursor : match.start()])
        if operation == "space":
            append_preferred_space()
        elif operation != "concat":
            raise FullLayoutV2Error(f"invalid approved LF operation: {operation}")
        cursor = match.end()
    append_plain(value[cursor:])
    result = "".join(parts)
    if not result or result[0] in (" ", base.INTERNAL_PREFERRED_BREAK) or result[-1] in (" ", base.INTERNAL_PREFERRED_BREAK):
        raise FullLayoutV2Error("approved LF stream has external whitespace")
    return result


def _color_span_end(value: str, start: int) -> int | None:
    if not value.startswith("\x1bC", start) or start + 3 > len(value) or value[start + 2] == "Z":
        return None
    close = value.find("\x1bCZ", start + 3)
    return None if close < 0 else close + 3


def words_from_marked(value: str) -> tuple[list[str], set[int]]:
    """Split only on spaces outside colored name spans, retaining name spaces."""

    words: list[str] = []
    preferred_after: set[int] = set()
    current: list[str] = []
    cursor = 0
    pending_preferred = False
    while cursor < len(value):
        span_end = _color_span_end(value, cursor)
        if span_end is not None:
            current.append(value[cursor:span_end])
            cursor = span_end
            continue
        char = value[cursor]
        if char in (" ", base.INTERNAL_PREFERRED_BREAK):
            if current:
                words.append("".join(current))
                current = []
                if char == base.INTERNAL_PREFERRED_BREAK:
                    preferred_after.add(len(words) - 1)
            elif char == base.INTERNAL_PREFERRED_BREAK and words:
                preferred_after.add(len(words) - 1)
            pending_preferred = char == base.INTERNAL_PREFERRED_BREAK
            cursor += 1
            continue
        current.append(char)
        cursor += 1
    if current:
        words.append("".join(current))
    if not words:
        raise FullLayoutV2Error("layout contains no visible words")
    if pending_preferred and not current:
        raise FullLayoutV2Error("layout has trailing preferred break")
    return words, preferred_after


def word_widths(
    words: Sequence[str],
    advance: Any,
    reservations: Mapping[str, int],
) -> tuple[list[int], list[int]]:
    actual: list[int] = []
    reserved: list[int] = []
    for word in words:
        visible = base.visual_line_width(word, advance)
        projected = visible
        for token in RUNTIME_RE.findall(word):
            width = reservations.get(token)
            if width is None:
                raise FullLayoutV2Error(f"runtime reservation is absent: {token}")
            projected += max(0, width - base.visual_line_width(token, advance))
        actual.append(visible)
        reserved.append(projected)
    return actual, reserved


def target_width_pairs(
    target: str,
    advance: Any,
    reservations: Mapping[str, int],
) -> tuple[list[int], list[int]]:
    """Measure visible and worst-case runtime-name widths for every line."""

    lines = LINEBREAK_RE.sub("\n", target).split("\n")
    actual: list[int] = []
    reserved: list[int] = []
    for line in lines:
        visible = base.visual_line_width(line, advance)
        projected = visible
        for token in RUNTIME_RE.findall(line):
            width = reservations.get(token)
            if width is None:
                raise FullLayoutV2Error(f"runtime reservation missing in target: {token}")
            projected += max(0, width - base.visual_line_width(token, advance))
        actual.append(visible)
        reserved.append(projected)
    return actual, reserved


def solve_layout(
    words: Sequence[str],
    preferred_after: set[int],
    advance: Any,
    reservations: Mapping[str, int],
    minimum_lines: int,
) -> Layout | None:
    actual_words, reserved_words = word_widths(words, advance, reservations)
    space = advance(" ")
    count = len(words)

    def range_width(values: Sequence[int], start: int, end: int) -> int:
        return sum(values[start:end]) + space * max(0, end - start - 1)

    def exact(line_count: int) -> Layout | None:
        @lru_cache(maxsize=None)
        def visit(start: int, remaining: int) -> Layout | None:
            if remaining == 0:
                return Layout((), (), (), ()) if start == count else None
            maximum_end = count - (remaining - 1)
            best: Layout | None = None
            for end in range(start + 1, maximum_end + 1):
                actual = range_width(actual_words, start, end)
                reserved = range_width(reserved_words, start, end)
                if reserved > MAX_LINE_PX:
                    break
                tail = visit(end, remaining - 1)
                if tail is None:
                    continue
                actual_widths = (actual, *tail.actual_widths)
                reserved_widths = (reserved, *tail.reserved_widths)
                nonpreferred = 0 if end == count or (end - 1) in preferred_after else 1
                score = (
                    nonpreferred + (tail.score[0] if tail.score else 0),
                    sum((MAX_LINE_PX - width) ** 2 for width in reserved_widths),
                    max(reserved_widths),
                )
                candidate = Layout(((start, end), *tail.ranges), actual_widths, reserved_widths, score)
                if best is None or candidate.score < best.score:
                    best = candidate
            return best

        return visit(0, line_count)

    for line_count in range(minimum_lines, MAX_LINES + 1):
        result = exact(line_count)
        if result is not None:
            return result
    return None


def render(words: Sequence[str], layout: Layout) -> str:
    return "\n".join(" ".join(words[start:end]) for start, end in layout.ranges)


def preferred_after_punctuation(words: Sequence[str]) -> set[int]:
    result: set[int] = set()
    for index, word in enumerate(words[:-1]):
        visible = base.visible_text(word)
        if visible and visible[-1] in base.TERMINAL_PUNCTUATION:
            result.add(index)
    return result


def reflow_source(
    source: str,
    operations: Sequence[str],
    advance: Any,
    reservations: Mapping[str, int],
) -> tuple[str, Layout] | None:
    marked = marked_stream(source, operations)
    words, preferred = words_from_marked(marked)
    source_line_count = len(base.visual_line_widths(source, advance))
    layout = solve_layout(words, preferred, advance, reservations, min(MAX_LINES, max(2, source_line_count)))
    return None if layout is None else (render(words, layout), layout)


def reflow_manual_text(
    target: str,
    source_line_count: int,
    advance: Any,
    reservations: Mapping[str, int],
) -> tuple[str, Layout] | None:
    if not target or target != target.strip(" \r\n"):
        return None
    # A reviewed translation's LFs represent deliberate Korean clause
    # boundaries.  Retain them as preferred breaks; the solver may move one
    # only when preserving it would exceed the real three-line budget.
    marked = marked_stream(target, ["space"] * len(linebreak_vector(target)))
    words, preferred = words_from_marked(marked)
    preferred.update(preferred_after_punctuation(words))
    layout = solve_layout(
        words,
        preferred,
        advance,
        reservations,
        min(MAX_LINES, max(2, source_line_count)),
    )
    return None if layout is None else (render(words, layout), layout)


def load_private_translations() -> dict[int, str]:
    if not TRANSLATION_ROOT.is_dir():
        return {}
    result: dict[int, str] = {}
    for path in sorted(TRANSLATION_ROOT.glob("*.jsonl")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise FullLayoutV2Error(f"invalid private translation JSON: {path.name}:{number}") from exc
            if not isinstance(row, dict) or type(row.get("id")) is not int or not isinstance(row.get("ko"), str):
                raise FullLayoutV2Error(f"invalid private translation row: {path.name}:{number}")
            entry_id = row["id"]
            if entry_id in result:
                raise FullLayoutV2Error(f"duplicate private translation ID: {entry_id}")
            result[entry_id] = row["ko"]
    return result


def make_reflow_entry(
    entry_id: int,
    source: str,
    target: str,
    layout: Layout,
    operations: Sequence[str],
    reasons: Sequence[str],
) -> dict[str, Any]:
    return {
        "id": entry_id,
        "operation": "conservative_whitespace_reflow",
        "preimage_utf16le_sha256": text_hash(source),
        "target_utf16le_sha256": text_hash(target),
        "ko": target,
        "source_line_breaks": linebreak_vector(source),
        "target_line_widths_px": list(layout.actual_widths),
        "target_reserved_line_widths_px": list(layout.reserved_widths),
        "protected_signature": protected_signature(source),
        "newline_operations": list(operations),
        "boundary_reasons": list(reasons),
    }


def make_compaction_entry(
    entry_id: int,
    source: str,
    target: str,
    layout: Layout,
) -> dict[str, Any]:
    require(protected_signature(target), protected_signature(source), f"manual compaction tokens {entry_id}")
    return {
        "id": entry_id,
        "operation": "manual_compact_korean_layout",
        "preimage_utf16le_sha256": text_hash(source),
        "target_utf16le_sha256": text_hash(target),
        "ko": target,
        "source_line_breaks": linebreak_vector(source),
        "target_line_widths_px": list(layout.actual_widths),
        "target_reserved_line_widths_px": list(layout.reserved_widths),
        "protected_signature": protected_signature(source),
        "newline_operations": ["reviewed_semantic_compaction"],
    }


def hydrate_v1_entries(
    table: Any,
    v1_entries: Mapping[int, Mapping[str, Any]],
    advance: Any,
    reservations: Mapping[str, int],
) -> dict[int, dict[str, Any]]:
    """Carry v1's already-reviewed edits into the current-font v2 overlay.

    The current Steam font binary is hash-pinned independently of v1.  Its
    relevant advances are remeasured here, so every inherited target receives
    current actual and reserved widths instead of inheriting stale metadata.
    """

    result: dict[int, dict[str, Any]] = {}
    for entry_id, original in v1_entries.items():
        if not 0 <= entry_id < table.string_count:
            raise FullLayoutV2Error(f"v1 overlay ID is outside the message table: {entry_id}")
        source = table.texts[entry_id]
        entry = dict(original)
        require(text_hash(source), entry.get("preimage_utf16le_sha256"), f"v1 overlay preimage {entry_id}")
        target = entry.get("ko")
        if not isinstance(target, str):
            raise FullLayoutV2Error(f"v1 overlay target is absent: {entry_id}")
        actual, reserved = target_width_pairs(target, advance, reservations)
        entry["target_line_widths_px"] = actual
        entry["target_reserved_line_widths_px"] = reserved
        result[entry_id] = entry
    return result


def row_for(
    entry_id: int,
    source: str,
    source_widths: Sequence[int],
    classification: str,
    layout: Layout | None,
    note: str,
) -> dict[str, Any]:
    return {
        "id": entry_id,
        "preimage_utf16le_sha256": text_hash(source),
        "source_line_widths_px": list(source_widths),
        "classification": classification,
        "target_line_widths_px": list(layout.actual_widths) if layout else None,
        "target_reserved_line_widths_px": list(layout.reserved_widths) if layout else None,
        "note": note,
    }


def build_entries(
    table: Any,
    advance: Any,
    decisions: Mapping[tuple[int, int], Mapping[str, str]],
    reservations: Mapping[str, int],
    excluded_ids: set[int],
    translations: Mapping[int, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int]]:
    v1_rows, v1_entries = load_v1_audit()
    entries = hydrate_v1_entries(table, v1_entries, advance, reservations)
    rows: list[dict[str, Any]] = []
    required_compactions: list[int] = []
    for entry_id, source in enumerate(table.texts):
        if entry_id not in v1_rows:
            continue
        v1_row = v1_rows[entry_id]
        source_widths = base.visual_line_widths(source, advance)
        prior_class = str(v1_row.get("classification"))
        if entry_id == 10564:
            if entry_id in entries:
                rows.append(row_for(entry_id, source, source_widths, "v1_reused", None, "v1 reviewed entry"))
            continue

        # The 1,383 rows whose original Korean cannot fit within three lines
        # never had a mechanically safe LF operation vector.  They must start
        # from a reviewed semantic compact translation, not a guessed join.
        if prior_class == "manual_compaction_required":
            reviewed = translations.get(entry_id)
            if reviewed is None:
                required_compactions.append(entry_id)
                rows.append(
                    row_for(
                        entry_id,
                        source,
                        source_widths,
                        "missing_reviewed_semantic_compaction",
                        None,
                        "private translation absent",
                    )
                )
                continue
            compact = reflow_manual_text(reviewed, len(source_widths), advance, reservations)
            if compact is None:
                raise FullLayoutV2Error(f"reviewed semantic compaction still exceeds budget: {entry_id}")
            target, layout = compact
            entries[entry_id] = make_compaction_entry(entry_id, source, target, layout)
            rows.append(
                row_for(
                    entry_id,
                    source,
                    source_widths,
                    "reviewed_semantic_compaction",
                    layout,
                    "private reviewed translation",
                )
            )
            continue

        # A printf row has no bounded runtime replacement width.  Its existing
        # game layout is deliberately retained rather than pretending it was
        # proven safe for an unknown substitution.
        if prior_class == "manual_protected_token_review" and entry_id in excluded_ids:
            rows.append(
                row_for(
                    entry_id,
                    source,
                    source_widths,
                    "protected_runtime_width_unknown_preserved",
                    None,
                    "printf runtime width is unbounded; source layout retained",
                )
            )
            continue

        if prior_class not in {"manual_korean_boundary_review", "manual_protected_token_review"}:
            if entry_id in entries:
                rows.append(row_for(entry_id, source, source_widths, "v1_reused", None, "v1 reviewed entry"))
            else:
                rows.append(
                    row_for(
                        entry_id,
                        source,
                        source_widths,
                        "v1_existing_layout_retained",
                        None,
                        "v1 already fit without a text change",
                    )
                )
            continue

        operations, reasons = source_operations(entry_id, source, v1_row, decisions)
        reflow = reflow_source(source, operations, advance, reservations)
        if reflow is not None:
            target, layout = reflow
            require(layout_skeleton(target), layout_skeleton(source), f"reflow content {entry_id}")
            require(protected_signature(target), protected_signature(source), f"reflow tokens {entry_id}")
            if target != source:
                entries[entry_id] = make_reflow_entry(entry_id, source, target, layout, operations, reasons)
                rows.append(row_for(entry_id, source, source_widths, "reviewed_boundary_reflow", layout, "static boundary decision"))
            else:
                rows.append(row_for(entry_id, source, source_widths, "already_fit_after_review", layout, "no byte change required"))
            continue
        reviewed = translations.get(entry_id)
        if reviewed is None:
            required_compactions.append(entry_id)
            rows.append(row_for(entry_id, source, source_widths, "missing_reviewed_semantic_compaction", None, "private translation absent"))
            continue
        compact = reflow_manual_text(reviewed, len(source_widths), advance, reservations)
        if compact is None:
            raise FullLayoutV2Error(f"reviewed semantic compaction still exceeds budget: {entry_id}")
        target, layout = compact
        entries[entry_id] = make_compaction_entry(entry_id, source, target, layout)
        rows.append(row_for(entry_id, source, source_widths, "reviewed_semantic_compaction", layout, "private reviewed translation"))
    return [entries[entry_id] for entry_id in sorted(entries)], rows, required_compactions


def coordinate_hash(ids: Iterable[int]) -> str:
    return sha256_bytes(json.dumps([{"id": item} for item in sorted(ids)], separators=(",", ":")).encode("ascii"))


def validate_reserved_entries(entries: Sequence[Mapping[str, Any]], advance: Any, reservations: Mapping[str, int]) -> None:
    for entry in entries:
        target = entry.get("ko")
        if not isinstance(target, str):
            raise FullLayoutV2Error("overlay target is not text")
        actual, reserved = target_width_pairs(target, advance, reservations)
        require(actual, entry.get("target_line_widths_px"), f"target actual widths {entry.get('id')}")
        require(reserved, entry.get("target_reserved_line_widths_px", actual), f"target reserved widths {entry.get('id')}")
        if len(actual) > MAX_LINES or max(reserved) > MAX_LINE_PX:
            raise FullLayoutV2Error(f"target layout exceeds actual/reserved budget: {entry.get('id')}")


def make_documents(
    source_path: Path,
    packed: bytes,
    raw: bytes,
    table: Any,
    font: Mapping[str, Any],
    entries: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
    required_compactions: Sequence[int],
    candidate: bytes,
    candidate_raw: bytes,
    changed: Sequence[int],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    classifications = Counter(str(row["classification"]) for row in rows)
    reviewed_boundary_count = classifications.get("reviewed_boundary_reflow", 0)
    already_fit_count = classifications.get("already_fit_after_review", 0)
    semantic_count = classifications.get("reviewed_semantic_compaction", 0)
    unknown_runtime_count = classifications.get("protected_runtime_width_unknown_preserved", 0)
    manual_review_coverage = reviewed_boundary_count + already_fit_count + semantic_count + unknown_runtime_count
    source = {
        "packed": file_spec(source_path),
        "raw_sha256": sha256_bytes(raw),
        "string_count": table.string_count,
    }
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "resource": RESOURCE,
        "source": source,
        "font": {
            "resource": "RES_JP/res_lang.bin",
            "outer_entry": 6,
            "table": 0,
            "packed": dict(font),
            "max_line_px": MAX_LINE_PX,
            "max_lines": MAX_LINES,
            "runtime_name_reservations_applied": True,
        },
        "selection": {
            "effective_change_coordinate_sha256": coordinate_hash(int(entry["id"]) for entry in entries),
            "entry_count": len(entries),
            "missing_private_semantic_compaction_count": len(required_compactions),
            "reviewed_semantic_compaction_count": semantic_count,
        },
        "entries": list(entries),
    }
    audit = {
        "schema": AUDIT_SCHEMA,
        "resource": RESOURCE,
        "source": source,
        "font": overlay["font"],
        "classifications": dict(sorted(classifications.items())),
        "required_compaction_ids": list(required_compactions),
        "review_coverage": {
            "expected_manual_review_row_count": FULL_MANUAL_REVIEW_COUNT,
            "manual_review_row_count": manual_review_coverage,
            "reviewed_boundary_reflow_count": reviewed_boundary_count,
            "already_fit_after_review_count": already_fit_count,
            "reviewed_semantic_compaction_count": semantic_count,
            "runtime_width_unknown_source_preserved_count": unknown_runtime_count,
        },
        "rows": list(rows),
        "policy": {
            "font_widths_modified": False,
            "manual_boundary_decisions_frozen": True,
            "runtime_name_width_reservations_applied": True,
            "semantic_compactions_require_private_review_translation": True,
            "steam_files_written": False,
        },
    }
    verification = {
        "schema": VERIFICATION_SCHEMA,
        "resource": RESOURCE,
        "source": source,
        "font": overlay["font"],
        "counts": {
            "overlay_entry_count": len(entries),
            "effective_change_count": len(changed),
            "missing_reviewed_compaction_count": len(required_compactions),
            "manual_review_coverage_count": manual_review_coverage,
            "reviewed_semantic_compaction_count": semantic_count,
            **dict(sorted(classifications.items())),
        },
        "overlay": {
            "relative_path": "workstreams/steam_jp_msgev_full_layout_v2/public/msgev_ko_steam_jp_full_layout.v2.json",
            "entry_count": len(entries),
            "effective_change_coordinate_sha256": coordinate_hash(int(entry["id"]) for entry in entries),
        },
        "audit": {
            "relative_path": "workstreams/steam_jp_msgev_full_layout_v2/public/msgev_full_layout_audit.v2.json",
            "missing_private_semantic_compaction_count": len(required_compactions),
            "manual_review_coverage_count": manual_review_coverage,
        },
        "expected_candidate": {
            "packed": {"size": len(candidate), "sha256": sha256_bytes(candidate)},
            "raw": {"size": len(candidate_raw), "sha256": sha256_bytes(candidate_raw)},
            "string_count": table.string_count,
            "effective_change_count": len(changed),
        },
        "safety": {
            "font_widths_modified": False,
            "steam_files_written": False,
            "release_written": False,
            "github_written": False,
            "nonselected_utf16le_payloads_preserved": True,
            "dynamic_name_widths_reserved": True,
        },
    }
    return overlay, audit, verification


def command_status(args: argparse.Namespace) -> int:
    _source_path, _packed, _raw, table = source_table(args.steam_root)
    advance, _font = current_font(args.steam_root)
    decisions = load_decisions()
    reservations, excluded, _reservation_doc = load_reservations()
    translations = load_private_translations()
    _entries, _rows, required = build_entries(table, advance, decisions, reservations, excluded, translations)
    print(json.dumps({"status": "INCOMPLETE" if required else "READY", "missing_compaction_count": len(required), "missing_compaction_ids": required}, ensure_ascii=False))
    return 0 if not required else 3


def command_freeze(args: argparse.Namespace) -> int:
    source_path, packed, raw, table = source_table(args.steam_root)
    advance, font = current_font(args.steam_root)
    decisions = load_decisions()
    reservations, excluded, reservation_document = load_reservations()
    translations = load_private_translations()
    entries, rows, required = build_entries(table, advance, decisions, reservations, excluded, translations)
    if required:
        raise FullLayoutV2Error(f"semantic compaction coverage is incomplete: {len(required)} rows")
    validate_reserved_entries(entries, advance, reservations)
    candidate, candidate_raw, changed = base.candidate_from_entries(packed, raw, table, entries, advance)
    overlay, audit, verification = make_documents(
        source_path, packed, raw, table, font, entries, rows, required, candidate, candidate_raw, changed
    )
    require(
        audit["review_coverage"]["manual_review_row_count"],
        FULL_MANUAL_REVIEW_COUNT,
        "full manual review coverage",
    )
    overlay["inputs"] = {
        "manual_boundary_decisions": {"sha256": sha256_bytes(DECISIONS_PATH.read_bytes())},
        "runtime_token_reservations": {"sha256": sha256_bytes(RESERVATIONS_PATH.read_bytes())},
        "runtime_reservation_font": reservation_document.get("font"),
    }
    audit["inputs"] = overlay["inputs"]
    verification["inputs"] = overlay["inputs"]
    atomic_write(OVERLAY_PATH, canonical_json(overlay))
    atomic_write(AUDIT_PATH, canonical_json(audit))
    verification["overlay"]["sha256"] = sha256_bytes(OVERLAY_PATH.read_bytes())
    verification["audit"]["sha256"] = sha256_bytes(AUDIT_PATH.read_bytes())
    atomic_write(VERIFICATION_PATH, canonical_json(verification))
    print("status=PASS")
    print(f"effective_changes={len(changed)}")
    print("steam_files_written=False")
    return 0


def load_frozen(steam_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], bytes, bytes, Any, Any, dict[str, int]]:
    overlay = read_json(OVERLAY_PATH, "v2 overlay")
    audit = read_json(AUDIT_PATH, "v2 audit")
    verification = read_json(VERIFICATION_PATH, "v2 verification")
    require(overlay.get("schema"), OVERLAY_SCHEMA, "v2 overlay schema")
    require(audit.get("schema"), AUDIT_SCHEMA, "v2 audit schema")
    require(verification.get("schema"), VERIFICATION_SCHEMA, "v2 verification schema")
    require(verification.get("overlay", {}).get("sha256"), sha256_bytes(OVERLAY_PATH.read_bytes()), "v2 overlay pin")
    require(verification.get("audit", {}).get("sha256"), sha256_bytes(AUDIT_PATH.read_bytes()), "v2 audit pin")
    source_path, packed, raw, table = source_table(steam_root)
    source = {"packed": file_spec(source_path), "raw_sha256": sha256_bytes(raw), "string_count": table.string_count}
    require(source, verification.get("source"), "v2 Steam source")
    advance, font = current_font(steam_root)
    require(overlay.get("font", {}).get("packed"), font, "v2 event font")
    reservations, _excluded, _doc = load_reservations()
    return overlay, audit, verification, packed, raw, table, advance, reservations


def compute_frozen_candidate(steam_root: Path) -> tuple[bytes, bytes, dict[str, Any]]:
    overlay, _audit, verification, packed, raw, table, advance, reservations = load_frozen(steam_root)
    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise FullLayoutV2Error("v2 overlay entries are absent")
    validate_reserved_entries(entries, advance, reservations)
    candidate, candidate_raw, changed = base.candidate_from_entries(packed, raw, table, entries, advance)
    expected = {
        "packed": {"size": len(candidate), "sha256": sha256_bytes(candidate)},
        "raw": {"size": len(candidate_raw), "sha256": sha256_bytes(candidate_raw)},
        "string_count": table.string_count,
        "effective_change_count": len(changed),
    }
    require(expected, verification.get("expected_candidate"), "v2 frozen candidate")
    return candidate, candidate_raw, {"expected": expected, "changed": changed, "source": verification["source"]}


def command_verify(args: argparse.Namespace) -> int:
    _candidate, _raw, report = compute_frozen_candidate(args.steam_root)
    print("status=PASS")
    print(f"effective_changes={len(report['changed'])}")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    candidate, _raw, report = compute_frozen_candidate(args.steam_root)
    root = require_tmp_output_root(args.output_root)
    target = root / Path(RESOURCE)
    atomic_write(target, candidate)
    manifest = {
        "schema": BUILD_SCHEMA,
        "resource": RESOURCE,
        "source": report["source"],
        "candidate": report["expected"],
        "effective_change_coordinate_sha256": coordinate_hash(report["changed"]),
        "safety": {"private_tmp_output_only": True, "steam_files_written": False, "font_widths_modified": False},
    }
    atomic_write(root / "manifest.v2.json", canonical_json(manifest))
    require(file_spec(target), report["expected"]["packed"], "v2 written candidate")
    print("status=PASS")
    print(f"output={target}")
    print(f"effective_changes={len(report['changed'])}")
    print("steam_files_written=False")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("status", "freeze", "verify", "build"):
        command = commands.add_parser(name)
        command.add_argument("--steam-root", type=Path, default=base.DEFAULT_STEAM_ROOT)
        if name == "build":
            command.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "status":
            return command_status(args)
        if args.command == "freeze":
            return command_freeze(args)
        if args.command == "verify":
            return command_verify(args)
        return command_build(args)
    except (FullLayoutV2Error, base.LayoutError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
