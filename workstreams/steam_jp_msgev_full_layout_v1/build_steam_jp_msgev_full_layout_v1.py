#!/usr/bin/env python3
"""Build a conservative full-event line-layout overlay for Steam JP ``msgev``.

The Steam v0.10 event renderer uses the original 48 px font and a 912 px
three-line message box.  This builder audits every Korean hard-line-break
entry in ``MSG_PK/JP/msgev.bin`` and changes only entries where whitespace
can be reflowed without guessing a Korean word boundary.  The remaining
entries are written to a hash-only review queue; they are deliberately not
flattened with a blanket LF-to-space conversion.

``freeze`` reads the current Steam JP v0.10 files, writes the public overlay,
audit, and verification contract in this workstream, and never writes Steam.
``build`` later reconstructs exactly the pinned candidate below ``tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp"
TOOLS = REPO / "tools"
GAME_RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
FONT_RESOURCE = Path("RES_JP") / "res_lang.bin"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "steam_jp_msgev_full_layout_v1" / "candidate"
OVERLAY_PATH = WORKSTREAM / "public" / "msgev_ko_steam_jp_full_layout.v1.json"
AUDIT_PATH = WORKSTREAM / "public" / "msgev_full_layout_audit.v1.json"
VERIFICATION_PATH = WORKSTREAM / "verification.v1.json"

sys.path[:0] = [str(TOOLS)]

import validate_g1n_surgical as g1n  # noqa: E402
from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgev-full-layout-overlay.v1"
AUDIT_SCHEMA = "nobu16.kr.steam-jp-msgev-full-layout-audit.v1"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-msgev-full-layout-verification.v1"
BUILD_SCHEMA = "nobu16.kr.steam-jp-msgev-full-layout-build.v1"
MAX_LINE_PX = 912
MAX_LINES = 3
FONT_OUTER_ENTRY = 6
FONT_TABLE = 0
INTERNAL_PREFERRED_BREAK = "\0"

HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
WIDE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
PRINTF_RE = re.compile(r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]")
RUNTIME_BRACKET_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")

OPENING_PUNCTUATION = frozenset("([{\"'「『〈《“‘")
CLOSING_PUNCTUATION = frozenset(")]}'\"」』〉》”’")
TERMINAL_PUNCTUATION = frozenset(".,!?…:;，。！？、")
PARTICLES = tuple(
    sorted(
        (
            "에게서",
            "한테서",
            "으로",
            "에게",
            "한테",
            "께서",
            "부터",
            "까지",
            "처럼",
            "보다",
            "밖에",
            "만큼",
            "은",
            "는",
            "이",
            "가",
            "을",
            "를",
            "의",
            "에",
            "와",
            "과",
            "도",
            "만",
            "로",
            "나",
            "랑",
            "께",
        ),
        key=len,
        reverse=True,
    )
)
SAFE_MULTI_SYLLABLE_ENDINGS = tuple(
    sorted(
        (
            "한다고",
            "라고",
            "하면서",
            "하며",
            "하여",
            "해서",
            "하였다",
            "했다",
            "한다",
            "됩니다",
            "있었다",
            "없었다",
            "되었다",
            "된다",
            "므로",
            "도록",
            "는데",
            "지만",
            "다면",
            "하면",
        ),
        key=len,
        reverse=True,
    )
)

# The screenshot row cannot fit even after a correct word-boundary reflow.
# This is a reviewed Korean rewrite; it is the sole semantic compaction in
# this first full-corpus pass.  Font metrics are unchanged.
MANUAL_COMPACT_OVERRIDES: dict[int, str] = {
    10564: (
        "\x1bCB도쿠가와\x1bCZ에 적의가 없자, \x1bCB도쿠가와\x1bCZ를\n"
        "따르자던 \x1bCA가쓰모토\x1bCZ는 \x1bCB도쿠가와\x1bCZ 앞잡이로\n"
        "몰려 \x1bCB도요토미 가문\x1bCZ에서 고립된다."
    )
}
MANUAL_COMPACT_PREIMAGE_HASHES = {
    10564: "430B77E0B6210204450991E4140CA1C892F475244FEB6E8976BC7DFB3340E6B8"
}


class LayoutError(ValueError):
    """Raised when the frozen layout or its current Steam base diverges."""


@dataclass(frozen=True)
class LayoutSolution:
    ranges: tuple[tuple[int, int], ...]
    widths: tuple[int, ...]
    score: tuple[int, ...]


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise LayoutError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise LayoutError(f"required file is absent: {path}")
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def safe_resource(root: Path, resource: Path) -> Path:
    base = root.resolve(strict=True)
    result = (base / resource).resolve(strict=True)
    try:
        result.relative_to(base)
    except ValueError as exc:
        raise LayoutError(f"resource escaped Steam root: {resource}") from exc
    if not result.is_file():
        raise LayoutError(f"Steam resource is not a regular file: {resource}")
    return result


def safe_output_root(path: Path) -> Path:
    allowed = TMP_ROOT.resolve(strict=True)
    result = path.resolve(strict=False)
    try:
        result.relative_to(allowed)
    except ValueError as exc:
        raise LayoutError("candidate output must remain below KR_PATCH_WORK/tmp") from exc
    if result == allowed:
        raise LayoutError("tmp itself is not a valid candidate root")
    return result


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LayoutError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise LayoutError(f"{label} root is not an object")
    return value


def visible_text(value: str) -> str:
    return ESC_RE.sub("", value)


def is_hangul(value: str) -> bool:
    return len(value) == 1 and HANGUL_RE.fullmatch(value) is not None


def protected_signature(value: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(value))
    printf_percent_offsets = {
        offset
        for match in printf_matches
        for offset in range(match.start(), match.end())
        if value[offset] == "%"
    }
    esc_matches = list(ESC_RE.finditer(value))
    esc_offsets = {
        offset for match in esc_matches for offset in range(match.start(), match.end())
    }
    controls = [
        f"U+{ord(char):04X}"
        for offset, char in enumerate(value)
        if unicodedata.category(char) == "Cc"
        and char not in ("\r", "\n")
        and offset not in esc_offsets
    ]
    return {
        "esc": [match.group(0) for match in esc_matches],
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, char in enumerate(value) if char == "%" and offset not in printf_percent_offsets
        ),
        "controls": controls,
        "pua": [f"U+{ord(char):04X}" for char in value if 0xE000 <= ord(char) <= 0xF8FF],
        "runtime_brackets": RUNTIME_BRACKET_RE.findall(value),
    }


def has_protected_review_token(signature: Mapping[str, Any]) -> bool:
    return any(
        bool(signature[key])
        for key in ("printf", "unknown_percent_count", "controls", "pua", "runtime_brackets")
    )


def layout_skeleton(value: str) -> str:
    """All glyph/control content except layout whitespace, in original order."""

    return value.replace(" ", "").replace("\r", "").replace("\n", "")


def linebreak_vector(value: str) -> list[str]:
    return LINEBREAK_RE.findall(value)


def font_advance_function(steam_root: Path) -> tuple[Callable[[str], int], dict[str, Any]]:
    path = safe_resource(steam_root, FONT_RESOURCE)
    archive = parse_link(path.read_bytes())
    if FONT_OUTER_ENTRY >= len(archive.entries):
        raise LayoutError("event font outer entry is absent")
    try:
        _header, raw = decompress_wrapper(archive.entries[FONT_OUTER_ENTRY].data)
    except Exception as exc:
        raise LayoutError("event font entry is not a readable G1N wrapper") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_msgev_full_layout_") as directory:
        g1n_path = Path(directory) / "event_font.g1n"
        g1n_path.write_bytes(raw)
        parsed = g1n.parse_g1n(g1n_path)
    if parsed.structural_errors:
        raise LayoutError(f"event font structure differs: {parsed.structural_errors[0]}")
    if FONT_TABLE >= len(parsed.tables):
        raise LayoutError("event font table is absent")
    table = parsed.tables[FONT_TABLE]

    def advance(char: str) -> int:
        codepoint = ord(char)
        if codepoint >= len(table.mapping):
            raise LayoutError(f"glyph is outside event font mapping: U+{codepoint:04X}")
        ordinal = table.mapping[codepoint]
        if ordinal == 0:
            # The renderer uses its 48 px wide-script fallback for unmapped
            # table-0 Hangul/CJK glyphs.  The game visibly renders these
            # characters; treating mapping slot zero as a missing 0 px glyph
            # would under-measure the very event rows being audited.
            if WIDE_SCRIPT_RE.fullmatch(char) is not None:
                return 48
            raise LayoutError(f"glyph is absent from event font: U+{codepoint:04X}")
        if ordinal >= len(table.records):
            raise LayoutError(f"glyph is absent from event font: U+{codepoint:04X}")
        record = table.records[ordinal]
        if record.width != record.advance or record.advance not in (24, 48):
            raise LayoutError(f"unexpected event glyph metric: U+{codepoint:04X}")
        return record.advance

    return advance, file_spec(path)


def visual_line_width(value: str, advance: Callable[[str], int]) -> int:
    width = 0
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                raise LayoutError("malformed ESC color token in event text")
            cursor += 3
            continue
        char = value[cursor]
        if unicodedata.category(char) == "Cc":
            raise LayoutError(f"unexpected control in visible event line: U+{ord(char):04X}")
        width += advance(char)
        cursor += 1
    return width


def visual_line_widths(value: str, advance: Callable[[str], int]) -> list[int]:
    canonical = LINEBREAK_RE.sub("\n", value)
    return [visual_line_width(line, advance) for line in canonical.split("\n")]


def visible_neighbors(value: str, match: re.Match[str]) -> tuple[str, str, str, str]:
    left_raw = value[: match.start()]
    right_raw = value[match.end() :]
    left_visible = visible_text(left_raw).rstrip(" ")
    right_visible = visible_text(right_raw).lstrip(" ")
    return left_raw, right_raw, left_visible, right_visible


def starts_complete_particle(value: str) -> bool:
    return any(value.startswith(particle) for particle in PARTICLES)


def particle_is_bounded(value: str) -> bool:
    for particle in PARTICLES:
        if value.startswith(particle):
            tail = value[len(particle) :]
            return not tail or tail[0] in " \r\n" or tail[0] in CLOSING_PUNCTUATION
    return False


def newline_operation(value: str, match: re.Match[str]) -> str:
    """Return a conservative operation for one hard LF, or ``manual``.

    General Hangul-to-Hangul joins are deliberately not guessed.  The small
    exceptions below are structural punctuation, explicit whitespace, a
    colored-name particle boundary, and multi-syllable grammatical endings.
    """

    left_raw, right_raw, left_visible, right_visible = visible_neighbors(value, match)
    if not left_visible or not right_visible:
        return "manual"
    if (left_raw and left_raw[-1] == " ") or (right_raw and right_raw[0] == " "):
        return "space"
    left_char = left_visible[-1]
    right_char = right_visible[0]
    if left_char in OPENING_PUNCTUATION or right_char in CLOSING_PUNCTUATION:
        return "concat"
    if left_char in TERMINAL_PUNCTUATION:
        return "space"
    if left_raw.rstrip(" ").endswith("\x1bCZ") and particle_is_bounded(right_raw.lstrip(" ")):
        return "concat"
    if (
        is_hangul(right_char)
        and not starts_complete_particle(right_visible)
        and any(left_visible.endswith(ending) for ending in SAFE_MULTI_SYLLABLE_ENDINGS)
    ):
        return "space"
    return "manual"


def hangul_to_hangul_break_count(value: str) -> int:
    count = 0
    for match in LINEBREAK_RE.finditer(value):
        _left_raw, _right_raw, left_visible, right_visible = visible_neighbors(value, match)
        if left_visible and right_visible and is_hangul(left_visible[-1]) and is_hangul(right_visible[0]):
            count += 1
    return count


class _MarkedBuilder:
    """Build words with original-LF break preference without retaining LFs."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self._last_separator = False

    def separator(self, preferred: bool) -> None:
        marker = INTERNAL_PREFERRED_BREAK if preferred else " "
        if self.parts and self._last_separator:
            if preferred:
                self.parts[-1] = INTERNAL_PREFERRED_BREAK
            return
        self.parts.append(marker)
        self._last_separator = True

    def plain(self, value: str) -> None:
        for char in value:
            if char == " ":
                self.separator(False)
            elif char in "\t\v\f" or char == INTERNAL_PREFERRED_BREAK:
                raise LayoutError("unsupported horizontal whitespace in automatic layout")
            else:
                self.parts.append(char)
                self._last_separator = False

    def finish(self) -> str:
        return "".join(self.parts)


def marked_word_stream(value: str, operations: Sequence[str]) -> str:
    matches = list(LINEBREAK_RE.finditer(value))
    require(len(operations), len(matches), "newline-operation vector length")
    result = _MarkedBuilder()
    cursor = 0
    for match, operation in zip(matches, operations):
        result.plain(value[cursor : match.start()])
        if operation == "space":
            result.separator(True)
        elif operation != "concat":
            raise LayoutError(f"cannot form automatic word stream from operation: {operation}")
        cursor = match.end()
    result.plain(value[cursor:])
    return result.finish()


def all_lf_space_stream(value: str) -> str:
    return marked_word_stream(value, ["space"] * len(linebreak_vector(value)))


def parse_marked_words(marked: str) -> tuple[list[str], set[int]]:
    if not marked or marked[0] in (" ", INTERNAL_PREFERRED_BREAK) or marked[-1] in (" ", INTERNAL_PREFERRED_BREAK):
        raise LayoutError("automatic layout has leading or trailing whitespace")
    words: list[str] = []
    preferred_after: set[int] = set()
    buffer: list[str] = []
    for char in marked:
        if char in (" ", INTERNAL_PREFERRED_BREAK):
            if not buffer:
                raise LayoutError("automatic layout has repeated whitespace")
            words.append("".join(buffer))
            buffer = []
            if char == INTERNAL_PREFERRED_BREAK:
                preferred_after.add(len(words) - 1)
        else:
            buffer.append(char)
    if not buffer:
        raise LayoutError("automatic layout has empty final word")
    words.append("".join(buffer))
    return words, preferred_after


def solve_layout(
    words: Sequence[str],
    preferred_after: set[int],
    advance: Callable[[str], int],
    line_count: int,
    preserve_preferred: bool,
) -> LayoutSolution | None:
    """Find an exact-line-count layout using only real word boundaries."""

    if not 1 <= line_count <= MAX_LINES or not words:
        return None
    word_widths = [visual_line_width(word, advance) for word in words]
    space_width = advance(" ")
    count = len(words)

    def range_width(start: int, end: int) -> int:
        return sum(word_widths[start:end]) + space_width * max(0, end - start - 1)

    @lru_cache(maxsize=None)
    def solve(start: int, remaining_lines: int) -> LayoutSolution | None:
        if remaining_lines == 0:
            return LayoutSolution((), (), ()) if start == count else None
        max_end = count - (remaining_lines - 1)
        best: LayoutSolution | None = None
        for end in range(start + 1, max_end + 1):
            width = range_width(start, end)
            if width > MAX_LINE_PX:
                break
            tail = solve(end, remaining_lines - 1)
            if tail is None:
                continue
            normal_break = 0
            if end < count and preserve_preferred and (end - 1) not in preferred_after:
                normal_break = 1
            widths = (width, *tail.widths)
            if preserve_preferred:
                score = (
                    normal_break + (tail.score[0] if tail.score else 0),
                    sum((MAX_LINE_PX - item) ** 2 for item in widths),
                    max(widths),
                )
            else:
                score = (max(widths), sum(item * item for item in widths))
            candidate = LayoutSolution(((start, end), *tail.ranges), widths, score)
            if best is None or candidate.score < best.score:
                best = candidate
        return best

    return solve(0, line_count)


def best_layout(
    words: Sequence[str],
    preferred_after: set[int],
    advance: Callable[[str], int],
    minimum_lines: int,
    preserve_preferred: bool,
) -> LayoutSolution | None:
    for line_count in range(minimum_lines, MAX_LINES + 1):
        candidate = solve_layout(words, preferred_after, advance, line_count, preserve_preferred)
        if candidate is not None:
            return candidate
    return None


def minimum_maximum_layout(
    words: Sequence[str], advance: Callable[[str], int]
) -> LayoutSolution | None:
    candidates = [
        solve_layout(words, set(), advance, line_count, False)
        for line_count in range(1, MAX_LINES + 1)
    ]
    present = [candidate for candidate in candidates if candidate is not None]
    if not present:
        return None
    return min(present, key=lambda item: item.score)


def render_layout(words: Sequence[str], solution: LayoutSolution) -> str:
    return "\n".join(" ".join(words[start:end]) for start, end in solution.ranges)


def coordinate_hash(ids: Iterable[int]) -> str:
    return sha256_bytes(
        json.dumps([{"id": item} for item in sorted(ids)], separators=(",", ":")).encode("ascii")
    )


def analyze_entry(entry_id: int, value: str, advance: Callable[[str], int]) -> dict[str, Any]:
    signature = protected_signature(value)
    widths = visual_line_widths(value, advance)
    source_lines = len(widths)
    source_max = max(widths)
    operations = [newline_operation(value, match) for match in LINEBREAK_RE.finditer(value)]
    all_space_solution: LayoutSolution | None = None
    try:
        all_words, _all_preferred = parse_marked_words(all_lf_space_stream(value))
        all_space_solution = minimum_maximum_layout(all_words, advance)
    except LayoutError:
        all_space_solution = None
    minimum_max = max(all_space_solution.widths) if all_space_solution is not None else None
    result: dict[str, Any] = {
        "id": entry_id,
        "preimage_utf16le_sha256": text_hash(value),
        "linebreak_count": len(operations),
        "source_line_widths_px": widths,
        "source_max_line_px": source_max,
        "hangul_to_hangul_break_count": hangul_to_hangul_break_count(value),
        "protected_token_review": has_protected_review_token(signature),
        "minimum_three_line_max_px": minimum_max,
        "newline_operations": operations,
    }
    if all_space_solution is None:
        result["classification"] = "manual_compaction_required"
        return result
    if has_protected_review_token(signature):
        result["classification"] = "manual_protected_token_review"
        return result
    if "manual" in operations:
        result["classification"] = "manual_korean_boundary_review"
        return result
    if source_lines <= MAX_LINES and source_max <= MAX_LINE_PX:
        result["classification"] = "existing_layout_retained"
        return result
    try:
        marked = marked_word_stream(value, operations)
        words, preferred_after = parse_marked_words(marked)
        desired_lines = min(MAX_LINES, max(2, source_lines))
        solution = best_layout(words, preferred_after, advance, desired_lines, True)
    except LayoutError:
        solution = None
    if solution is None:
        result["classification"] = "manual_compaction_required"
        return result
    target = render_layout(words, solution)
    if layout_skeleton(target) != layout_skeleton(value):
        raise LayoutError(f"automatic layout content changed at ID {entry_id}")
    if protected_signature(target) != signature:
        raise LayoutError(f"automatic layout protected tokens changed at ID {entry_id}")
    target_widths = visual_line_widths(target, advance)
    if len(target_widths) > MAX_LINES or max(target_widths) > MAX_LINE_PX:
        raise LayoutError(f"automatic layout overflow at ID {entry_id}")
    result.update(
        {
            "classification": "automatic_conservative_reflow",
            "target": target,
            "target_line_widths_px": target_widths,
        }
    )
    return result


def make_overlay_entry(row: Mapping[str, Any], source: str) -> dict[str, Any]:
    target = row.get("target")
    if not isinstance(target, str):
        raise LayoutError(f"automatic target is absent: ID {row['id']}")
    signature = protected_signature(source)
    return {
        "id": row["id"],
        "operation": "conservative_whitespace_reflow",
        "preimage_utf16le_sha256": row["preimage_utf16le_sha256"],
        "target_utf16le_sha256": text_hash(target),
        "ko": target,
        "source_line_breaks": linebreak_vector(source),
        "target_line_widths_px": row["target_line_widths_px"],
        "protected_signature": signature,
        "newline_operations": row["newline_operations"],
    }


def make_manual_override_entry(entry_id: int, source: str, advance: Callable[[str], int]) -> dict[str, Any]:
    require(text_hash(source), MANUAL_COMPACT_PREIMAGE_HASHES[entry_id], f"manual override {entry_id} preimage")
    target = MANUAL_COMPACT_OVERRIDES[entry_id]
    require(protected_signature(target), protected_signature(source), f"manual override {entry_id} protected tokens")
    widths = visual_line_widths(target, advance)
    if len(widths) > MAX_LINES or max(widths) > MAX_LINE_PX:
        raise LayoutError(f"manual override {entry_id} does not fit event box")
    return {
        "id": entry_id,
        "operation": "manual_compact_korean_layout",
        "preimage_utf16le_sha256": text_hash(source),
        "target_utf16le_sha256": text_hash(target),
        "ko": target,
        "source_line_breaks": linebreak_vector(source),
        "target_line_widths_px": widths,
        "protected_signature": protected_signature(source),
        "newline_operations": ["manual_compaction"],
    }


def candidate_from_entries(
    packed: bytes,
    raw: bytes,
    table: Any,
    entries: Sequence[Mapping[str, Any]],
    advance: Callable[[str], int],
) -> tuple[bytes, bytes, list[int]]:
    texts = list(table.texts)
    selected_ids: list[int] = []
    for entry in entries:
        entry_id = entry.get("id")
        target = entry.get("ko")
        operation = entry.get("operation")
        if type(entry_id) is not int or not isinstance(target, str) or not isinstance(operation, str):
            raise LayoutError("overlay entry shape is invalid")
        if entry_id in selected_ids or not 0 <= entry_id < len(texts):
            raise LayoutError("overlay coordinate is duplicate or outside table")
        source = texts[entry_id]
        require(text_hash(source), entry.get("preimage_utf16le_sha256"), f"overlay preimage {entry_id}")
        require(text_hash(target), entry.get("target_utf16le_sha256"), f"overlay target {entry_id}")
        require(protected_signature(source), entry.get("protected_signature"), f"overlay source tokens {entry_id}")
        require(protected_signature(target), entry.get("protected_signature"), f"overlay target tokens {entry_id}")
        widths = visual_line_widths(target, advance)
        require(widths, entry.get("target_line_widths_px"), f"overlay target widths {entry_id}")
        if len(widths) > MAX_LINES or max(widths) > MAX_LINE_PX:
            raise LayoutError(f"overlay target overflows event box: {entry_id}")
        if operation == "conservative_whitespace_reflow":
            require(layout_skeleton(target), layout_skeleton(source), f"overlay content preservation {entry_id}")
        elif operation != "manual_compact_korean_layout":
            raise LayoutError(f"overlay operation is invalid: {entry_id}")
        selected_ids.append(entry_id)
        texts[entry_id] = target
    raw_candidate = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(raw_candidate, packed)
    _header, roundtrip_raw = decompress_wrapper(candidate)
    require(roundtrip_raw, raw_candidate, "candidate wrapper round-trip")
    candidate_table = parse_message_table(roundtrip_raw)
    require(candidate_table.texts, tuple(texts), "candidate message table round-trip")
    changed = [index for index, (before, after) in enumerate(zip(table.texts, candidate_table.texts)) if before != after]
    require(changed, selected_ids, "candidate changed-coordinate domain")
    for index, before in enumerate(table.texts):
        if index not in selected_ids:
            require(candidate_table.texts[index], before, f"nonselected payload {index}")
    return candidate, raw_candidate, changed


def audit_and_entries(table: Any, advance: Callable[[str], int]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    for entry_id, value in enumerate(table.texts):
        if HANGUL_RE.search(value) is None or LINEBREAK_RE.search(value) is None:
            continue
        row = analyze_entry(entry_id, value, advance)
        if entry_id in MANUAL_COMPACT_OVERRIDES:
            entry = make_manual_override_entry(entry_id, value, advance)
            row["classification"] = "manual_compaction_override_applied"
            row["target_line_widths_px"] = entry["target_line_widths_px"]
            row.pop("target", None)
            entries.append(entry)
        elif row["classification"] == "automatic_conservative_reflow":
            entries.append(make_overlay_entry(row, value))
            row.pop("target", None)
        rows.append(row)
    entries.sort(key=lambda item: int(item["id"]))
    return rows, entries


def make_documents(
    source_path: Path,
    packed: bytes,
    raw: bytes,
    table: Any,
    font: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    entries: Sequence[Mapping[str, Any]],
    candidate: bytes,
    candidate_raw: bytes,
    changed: Sequence[int],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    classifications = Counter(str(row["classification"]) for row in rows)
    automatic_count = sum(entry["operation"] == "conservative_whitespace_reflow" for entry in entries)
    manual_override_count = sum(entry["operation"] == "manual_compact_korean_layout" for entry in entries)
    review_hold_count = sum(count for name, count in classifications.items() if name.startswith("manual_") and name != "manual_compaction_override_applied")
    source = {
        "packed": file_spec(source_path),
        "raw_sha256": sha256_bytes(raw),
        "string_count": table.string_count,
    }
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "resource": GAME_RESOURCE.as_posix(),
        "source": source,
        "font": {
            "resource": FONT_RESOURCE.as_posix(),
            "outer_entry": FONT_OUTER_ENTRY,
            "table": FONT_TABLE,
            "packed": dict(font),
            "max_line_px": MAX_LINE_PX,
            "max_lines": MAX_LINES,
        },
        "selection": {
            "scanned_hangul_hard_linebreak_entry_count": len(rows),
            "automatic_conservative_reflow_count": automatic_count,
            "manual_compact_override_count": manual_override_count,
            "effective_change_coordinate_sha256": coordinate_hash(int(entry["id"]) for entry in entries),
        },
        "entries": list(entries),
    }
    audit = {
        "schema": AUDIT_SCHEMA,
        "resource": GAME_RESOURCE.as_posix(),
        "source": source,
        "font": overlay["font"],
        "entry_count": len(rows),
        "classifications": dict(sorted(classifications.items())),
        "rows": list(rows),
        "policy": {
            "font_widths_modified": False,
            "hard_linebreaks_globally_removed": False,
            "automatic_reflow_requires_unambiguous_boundary": True,
            "automatic_reflow_requires_actual_g1n_width_within_budget": True,
            "manual_review_rows_are_not_written_to_candidate": True,
        },
    }
    verification = {
        "schema": VERIFICATION_SCHEMA,
        "resource": GAME_RESOURCE.as_posix(),
        "source": source,
        "font": overlay["font"],
        "counts": {
            "scanned_hangul_hard_linebreak_entry_count": len(rows),
            "automatic_conservative_reflow_count": automatic_count,
            "manual_compact_override_count": manual_override_count,
            "manual_review_hold_count": review_hold_count,
            **dict(sorted(classifications.items())),
        },
        "overlay": {
            "relative_path": "workstreams/steam_jp_msgev_full_layout_v1/public/msgev_ko_steam_jp_full_layout.v1.json",
            "entry_count": len(entries),
            "effective_change_coordinate_sha256": coordinate_hash(int(entry["id"]) for entry in entries),
        },
        "audit": {
            "relative_path": "workstreams/steam_jp_msgev_full_layout_v1/public/msgev_full_layout_audit.v1.json",
            "entry_count": len(rows),
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
            "automatic_reflow_only_at_unambiguous_boundaries": True,
            "manual_review_rows_left_unchanged": True,
            "nonselected_utf16le_payloads_preserved": True,
        },
    }
    return overlay, audit, verification


def source_table(steam_root: Path) -> tuple[Path, bytes, bytes, Any]:
    source_path = safe_resource(steam_root, GAME_RESOURCE)
    packed = source_path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts), raw, "source table parse/rebuild")
    return source_path, packed, raw, table


def command_freeze(args: argparse.Namespace) -> int:
    source_path, packed, raw, table = source_table(args.steam_root)
    advance, font = font_advance_function(args.steam_root)
    rows, entries = audit_and_entries(table, advance)
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries, advance)
    overlay, audit, verification = make_documents(
        source_path, packed, raw, table, font, rows, entries, candidate, candidate_raw, changed
    )
    atomic_write(OVERLAY_PATH, canonical_json(overlay))
    atomic_write(AUDIT_PATH, canonical_json(audit))
    verification["overlay"]["sha256"] = sha256_bytes(OVERLAY_PATH.read_bytes())
    verification["audit"]["sha256"] = sha256_bytes(AUDIT_PATH.read_bytes())
    atomic_write(VERIFICATION_PATH, canonical_json(verification))
    print("status=PASS")
    print(f"scanned={len(rows)}")
    print(f"automatic_reflow={sum(item['operation'] == 'conservative_whitespace_reflow' for item in entries)}")
    print(f"manual_compact_override={sum(item['operation'] == 'manual_compact_korean_layout' for item in entries)}")
    print(f"candidate_sha256={sha256_bytes(candidate)}")
    print("steam_files_written=False")
    return 0


def load_frozen_inputs(steam_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Path, bytes, bytes, Any, Callable[[str], int]]:
    overlay = read_json(OVERLAY_PATH, "full event overlay")
    audit = read_json(AUDIT_PATH, "full event audit")
    verification = read_json(VERIFICATION_PATH, "full event verification")
    require(overlay.get("schema"), OVERLAY_SCHEMA, "overlay schema")
    require(audit.get("schema"), AUDIT_SCHEMA, "audit schema")
    require(verification.get("schema"), VERIFICATION_SCHEMA, "verification schema")
    require(verification.get("overlay", {}).get("sha256"), sha256_bytes(OVERLAY_PATH.read_bytes()), "overlay pin")
    require(verification.get("audit", {}).get("sha256"), sha256_bytes(AUDIT_PATH.read_bytes()), "audit pin")
    source_path, packed, raw, table = source_table(steam_root)
    require(overlay.get("resource"), GAME_RESOURCE.as_posix(), "overlay resource")
    require(overlay.get("source"), verification.get("source"), "source profile contract")
    require(
        {"packed": file_spec(source_path), "raw_sha256": sha256_bytes(raw), "string_count": table.string_count},
        verification.get("source"),
        "Steam msgev source profile",
    )
    advance, font = font_advance_function(steam_root)
    require(overlay.get("font", {}).get("packed"), font, "event font profile")
    require(verification.get("font"), overlay.get("font"), "font contract")
    return overlay, audit, verification, source_path, packed, raw, table, advance


def compute_frozen_candidate(steam_root: Path) -> tuple[bytes, bytes, dict[str, Any]]:
    overlay, audit, verification, _source_path, packed, raw, table, advance = load_frozen_inputs(steam_root)
    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise LayoutError("overlay entry list is invalid")
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries, advance)
    expected = {
        "packed": {"size": len(candidate), "sha256": sha256_bytes(candidate)},
        "raw": {"size": len(candidate_raw), "sha256": sha256_bytes(candidate_raw)},
        "string_count": table.string_count,
        "effective_change_count": len(changed),
    }
    require(expected, verification.get("expected_candidate"), "frozen candidate")
    require(len(audit.get("rows", [])), verification.get("counts", {}).get("scanned_hangul_hard_linebreak_entry_count"), "audit row count")
    return candidate, candidate_raw, {
        "changed": changed,
        "expected": expected,
        "source": verification["source"],
    }


def command_verify(args: argparse.Namespace) -> int:
    candidate, candidate_raw, report = compute_frozen_candidate(args.steam_root)
    require(sha256_bytes(candidate), report["expected"]["packed"]["sha256"], "verification candidate")
    require(sha256_bytes(candidate_raw), report["expected"]["raw"]["sha256"], "verification raw candidate")
    print("status=PASS")
    print(f"effective_changes={len(report['changed'])}")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    candidate, _candidate_raw, report = compute_frozen_candidate(args.steam_root)
    root = safe_output_root(args.output_root)
    target = root / GAME_RESOURCE
    atomic_write(target, candidate)
    manifest = {
        "schema": BUILD_SCHEMA,
        "resource": GAME_RESOURCE.as_posix(),
        "source": report["source"],
        "candidate": report["expected"],
        "effective_change_coordinate_sha256": coordinate_hash(report["changed"]),
        "safety": {
            "private_tmp_output_only": True,
            "font_widths_modified": False,
            "steam_files_written": False,
            "release_written": False,
            "github_written": False,
        },
    }
    atomic_write(root / "manifest.v1.json", canonical_json(manifest))
    require(file_spec(target), report["expected"]["packed"], "written candidate")
    print("status=PASS")
    print(f"output={target}")
    print(f"effective_changes={len(report['changed'])}")
    print("steam_files_written=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("freeze", "verify", "build"):
        item = commands.add_parser(command)
        item.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
        if command == "build":
            item.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "freeze":
            return command_freeze(args)
        if args.command == "verify":
            return command_verify(args)
        return command_build(args)
    except (LayoutError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
