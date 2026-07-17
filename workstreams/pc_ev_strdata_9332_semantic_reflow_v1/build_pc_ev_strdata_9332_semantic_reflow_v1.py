#!/usr/bin/env python3
"""Build a fail-closed PC Steam candidate for the visible base-event overflow.

The Korean base event at ``MSG/JP/ev_strdata.bin`` ID 9332 cannot fit the
three-line renderer by merely moving its Japanese line breaks.  This builder
uses one reviewed Korean compaction with deliberate clause boundaries.  It
never writes the Steam installation: it emits the normal eleven-file text
transaction profile below ``KR_PATCH_WORK/tmp``.

The other ten files are copied byte-for-byte.  This makes the resulting
candidate safe to apply with ``tools/pk_file_only_transaction.py`` while
keeping the actual patch scope to the one confirmed base-event cell.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGEV_V1 = REPO / "workstreams" / "steam_jp_msgev_full_layout_v1"
sys.path[:0] = [str(TOOLS), str(MSGEV_V1)]

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
import build_steam_jp_msgev_full_layout_v1 as layout_base  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"

PROFILE_TARGETS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
RESOURCE = "MSG/JP/ev_strdata.bin"
EVENT_ID = 9332
MAX_LINES = 3
# This is deliberately stricter than the unproven base-event container width.
# It matches the measured 912px PK event box and leaves a safety margin if the
# base event box is wider (as the in-game screenshot indicates).
MAX_LINE_PX = 912

# Current Steam preimage as of the visible-event investigation.  A mismatch
# must stop the build rather than silently overwriting later wording work.
SOURCE_SHA256 = "03B6D8EF42519F1D5E084B100BBBE23F8C754539C04064937566AB86EA306074"
SOURCE_SIZE = 928_520
SOURCE_TEXT_SHA256 = "FAE15611D07772348A1FEC74CCF1CC02A0A75E381CF10FC7262FAB753184BA9F"

ESC = "\x1bC"
END_COLOR = f"{ESC}Z"
TARGET_TEXT = (
    f"{ESC}B오우치가{END_COLOR}를 대신한 {ESC}C주고쿠{END_COLOR}의 패자,\n"
    f"{ESC}A모리 모토나리{END_COLOR}는 {ESC}C규슈 북부{END_COLOR}를 노리며\n"
    f"{ESC}B오토모{END_COLOR}와 {ESC}B아마고{END_COLOR} 두 가문과 맞섰다."
)
TARGET_TEXT_SHA256 = "2714908068DA84CD14A55A856FB4899C9656C6275EB60FB4F85F927079BE2281"

LINEBREAK_RE = re.compile(r"\r\n|\r|\n")
CONTROL_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)


class ReflowError(ValueError):
    """Raised when a pinned Steam source or the candidate contract differs."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def spec(value: bytes) -> dict[str, Any]:
    return {"size": len(value), "sha256": sha256_bytes(value)}


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ReflowError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def require_under(root: Path, path: Path, label: str, *, exists: bool = True) -> Path:
    root = root.resolve(strict=True)
    resolved = path.resolve(strict=exists)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ReflowError(f"{label} escapes its root: {path}") from exc
    return resolved


def protected_signature(value: str) -> dict[str, Any]:
    """Keep runtime and formatting controls intact through semantic compaction."""

    return {
        "printf": PRINTF_RE.findall(value),
        "runtime": RUNTIME_RE.findall(value),
        "controls": [char for char in value if ord(char) < 0x20 and char not in "\r\n\t\x1b"],
    }


def color_signature(value: str) -> list[str]:
    return CONTROL_RE.findall(value)


def visible_text(value: str) -> str:
    return CONTROL_RE.sub("", value)


def validate_colors(value: str) -> None:
    """Validate only the game's ESC-C colour token grammar and balancing."""

    cursor = 0
    opened = 0
    while cursor < len(value):
        if value.startswith(ESC, cursor):
            if cursor + 3 > len(value):
                raise ReflowError("truncated ESC-C colour token")
            token = value[cursor + 2]
            if token == "Z":
                if opened == 0:
                    raise ReflowError("unmatched ESC-CZ colour reset")
                opened -= 1
            else:
                opened += 1
            cursor += 3
            continue
        cursor += 1
    if opened:
        raise ReflowError("unclosed ESC-C colour token")


def target_line_widths(steam_root: Path, value: str) -> list[int]:
    advance, _font = layout_base.font_advance_function(steam_root)
    return [
        layout_base.visual_line_width(line, advance)
        for line in LINEBREAK_RE.sub("\n", value).split("\n")
    ]


def validate_target(steam_root: Path, source: str, target: str) -> list[int]:
    require(text_hash(source), SOURCE_TEXT_SHA256, "ID 9332 source text hash")
    require(text_hash(target), TARGET_TEXT_SHA256, "reviewed target text hash")
    require(protected_signature(target), protected_signature(source), "runtime/printf/control signature")
    validate_colors(target)
    if target.count("\n") != MAX_LINES - 1:
        raise ReflowError("target must contain exactly two deliberate line breaks")
    lines = target.split("\n")
    if any(not visible_text(line).strip() for line in lines):
        raise ReflowError("target has a blank visual line")
    widths = target_line_widths(steam_root, target)
    if len(widths) != MAX_LINES or max(widths) > MAX_LINE_PX:
        raise ReflowError(f"target violates conservative line budget: {widths!r}")
    if "?" in visible_text(target):
        raise ReflowError("target unexpectedly contains a fallback question mark")
    return widths


def read_event_table(steam_root: Path) -> tuple[bytes, Any, bytes]:
    source_path = require_under(steam_root, steam_root / RESOURCE, "Steam event source")
    packed = source_path.read_bytes()
    require(spec(packed), {"size": SOURCE_SIZE, "sha256": SOURCE_SHA256}, "Steam event source")
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if EVENT_ID >= table.string_count:
        raise ReflowError(f"event ID outside table: {EVENT_ID}")
    if rebuild_message_table(table, table.texts) != raw:
        raise ReflowError("source event table fails parse/rebuild round trip")
    return packed, header, raw


def candidate_event(steam_root: Path) -> tuple[bytes, dict[str, Any]]:
    packed, header, raw = read_event_table(steam_root)
    table = parse_message_table(raw)
    source = table.texts[EVENT_ID]
    widths = validate_target(steam_root, source, TARGET_TEXT)
    texts = list(table.texts)
    texts[EVENT_ID] = TARGET_TEXT
    candidate_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(candidate_raw, header)
    roundtrip_header, roundtrip_raw = decompress_wrapper(candidate)
    require(roundtrip_header.prefix, header.prefix, "candidate wrapper prefix")
    require(roundtrip_raw, candidate_raw, "candidate wrapper round trip")
    roundtrip = parse_message_table(roundtrip_raw)
    require(roundtrip.texts[EVENT_ID], TARGET_TEXT, "candidate ID 9332 text")
    changed = [
        index
        for index, (before, after) in enumerate(zip(table.texts, roundtrip.texts, strict=True))
        if before != after
    ]
    require(changed, [EVENT_ID], "candidate changed coordinate domain")
    if rebuild_message_table(roundtrip, roundtrip.texts) != candidate_raw:
        raise ReflowError("candidate event table fails parse/rebuild round trip")
    return candidate, {
        "source": spec(packed),
        "candidate": spec(candidate),
        "raw_source_sha256": sha256_bytes(raw),
        "raw_candidate_sha256": sha256_bytes(candidate_raw),
        "changed_ids": changed,
        "target_line_widths_px": widths,
        "target_visible_lines": [visible_text(line) for line in TARGET_TEXT.split("\n")],
        "font": {"resource": "RES_JP/res_lang.bin", "outer_entry": 6, "table": 0},
    }


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def output_paths(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }


def build(steam_root: Path, output_root: Path, manifest_path: Path) -> dict[str, Any]:
    steam_root = steam_root.resolve(strict=True)
    allowed_tmp = (REPO / "tmp").resolve(strict=True)
    output_root = output_root.resolve(strict=False)
    try:
        output_root.relative_to(allowed_tmp)
    except ValueError as exc:
        raise ReflowError("candidate output must remain below KR_PATCH_WORK/tmp") from exc
    if output_root == allowed_tmp:
        raise ReflowError("KR_PATCH_WORK/tmp cannot itself be a candidate root")

    candidate_event_blob, event_report = candidate_event(steam_root)
    expected_paths = set(PROFILE_TARGETS)
    if output_root.exists() and output_paths(output_root) - expected_paths:
        raise ReflowError("candidate output contains unexpected pre-existing files")

    rows: list[dict[str, Any]] = []
    for relative in PROFILE_TARGETS:
        source_path = require_under(steam_root, steam_root / relative, f"Steam source {relative}")
        target_path = output_root / relative
        payload = candidate_event_blob if relative == RESOURCE else source_path.read_bytes()
        atomic_write(target_path, payload)
        require(target_path.read_bytes(), payload, f"written candidate {relative}")
        rows.append(
            {
                "path": relative,
                "source": spec(source_path.read_bytes()),
                "candidate": spec(payload),
                "changed": relative == RESOURCE,
            }
        )
    actual_paths = output_paths(output_root)
    require(actual_paths, expected_paths, "candidate exact eleven-file profile")
    manifest = {
        "schema": "nobu16.kr.pc-ev-strdata-9332-semantic-reflow-build.v1",
        "scope": {
            "candidate_private_only": True,
            "steam_game_resource_written": False,
            "font_resources_touched": False,
            "other_resources_touched": False,
        },
        "resource": RESOURCE,
        "event_id": EVENT_ID,
        "event": event_report,
        "profile": rows,
    }
    manifest_path = manifest_path.resolve(strict=False)
    try:
        manifest_path.relative_to(allowed_tmp)
    except ValueError as exc:
        raise ReflowError("manifest must remain below KR_PATCH_WORK/tmp") from exc
    atomic_write(manifest_path, canonical_json(manifest))
    return manifest


def verify(steam_root: Path, output_root: Path) -> dict[str, Any]:
    steam_root = steam_root.resolve(strict=True)
    output_root = output_root.resolve(strict=True)
    _blob, event_report = candidate_event(steam_root)
    require(output_paths(output_root), set(PROFILE_TARGETS), "candidate exact eleven-file profile")
    changed: list[str] = []
    for relative in PROFILE_TARGETS:
        source = require_under(steam_root, steam_root / relative, f"Steam source {relative}").read_bytes()
        candidate = require_under(output_root, output_root / relative, f"candidate {relative}").read_bytes()
        if relative == RESOURCE:
            if candidate == source:
                raise ReflowError("candidate did not change the confirmed event resource")
            changed.append(relative)
        elif candidate != source:
            raise ReflowError(f"candidate unexpectedly changed {relative}")
    require(changed, [RESOURCE], "candidate changed path domain")
    return {"status": "PASS", "changed_paths": changed, "event": event_report}


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = (
            build(args.steam_root, args.output_root, args.manifest)
            if args.command == "build"
            else verify(args.steam_root, args.output_root)
        )
    except (OSError, ValueError, ReflowError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
