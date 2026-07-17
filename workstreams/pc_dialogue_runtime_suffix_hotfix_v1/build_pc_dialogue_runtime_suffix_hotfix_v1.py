#!/usr/bin/env python3
"""Build a PC-only hotfix for Korean dialogue with Japanese suffix bytecode.

Several ``msggame`` records were translated as if every visible character
lived in a UTF-16 literal.  In fact, those records leave a Japanese inflection
suffix in opaque bytecode after a Korean verb stem.  The game therefore joins
the Korean stem to a Japanese-language ending at runtime.

This builder starts only from the already installed PC-only text-audit target,
checks its two affected resource hashes, and creates an isolated eleven-file
candidate tree.  It never writes into the Steam installation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME = REPO / "workstreams" / "msggame"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(MSGGAME))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
)


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_BUILD_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"

# This exact vector is the currently installed result of
# pc-only-text-audit-68c8eb1.  Failing when it differs prevents this hotfix
# from silently overwriting a later user change.
INITIAL_BASELINE_SHA256 = {
    "MSG/JP/msggame.bin": "8F8F702D0DE368319FB1F93E39977AEE6AA02B5FE02E033C2320EE6B92D02019",
    "MSG_PK/JP/msggame.bin": "8EA53D1015D836FCADEAB307AC0095D107B7B874BD58DA3F34CA0528DC6B1BFB",
}
# A second, source-backed defect was found while checking the affected reply:
# PK record 6:2295 had been copied from 6:2294 instead of containing its own
# response.  These are the hashes after the first runtime-suffix application;
# accepting this exact state permits a small follow-up without rebuilding or
# overwriting the completed first correction.
POST_RUNTIME_SUFFIX_BASELINE_SHA256 = {
    "MSG/JP/msggame.bin": "8C9D7CBD9E614932A515A8B00A3CFA079818C4A929CF50080E940568CC9E57F4",
    "MSG_PK/JP/msggame.bin": "3CAD4167131040D0AB141ACADC1750A42F58E46F78F65D024E55F2983548BA0A",
}

# The transaction helper deliberately accepts only this exact profile.  The
# nine unchanged files are copied byte-for-byte so a later transaction records
# them as retain entries rather than broadening the patch scope.
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

TERMINATOR = b"\x05\x05\x05"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-runtime-suffix-hotfix-build.v1"


@dataclass(frozen=True)
class RecordFix:
    block_id: int
    record_id: int
    before_literals: tuple[str, ...]
    after: str
    prefix_hex: str = ""

    @property
    def coordinate(self) -> str:
        return f"{self.block_id}:{self.record_id}"


# These are complete Korean renderings.  Replacing the whole record is
# intentional: it removes only the Japanese grammar bytecode between literal
# slots while retaining any proven pre-literal bytecode declared in prefix_hex.
BASE_RUNTIME_SUFFIX_FIXES = (
    RecordFix(
        6,
        2288,
        ("크게 나오셨군요\n그에 상응하는 것은 갖고 계십니까?",),
        "상당히 큰 요구를 하시는군요.\n그에 걸맞은 대가는 준비하셨습니까?",
    ),
    RecordFix(
        6,
        2289,
        ("훗… 크게 나오는군\n툭 까놓고 말하자면 보답하기 나름이지",),
        "훗… 제법 큰 요구로군.\n까놓고 말해, 대가에 달렸지.",
    ),
    RecordFix(
        13,
        17,
        ("처, 천하를!?\n이건… 크게 나오", "\n허나 그렇기에 보필할 보람도 있는 법"),
        "천, 천하를!?\n이건 정말… 원대한 포부로군.\n허나 그렇기에 보필할 보람도 있는 법이지.",
    ),
    RecordFix(
        13,
        142,
        ("처, 천하를!?\n이건… 크게 나오", "\n허나 그렇기에 보필할 보람도 있는 법"),
        "천, 천하를!?\n이건 정말… 원대한 포부로군.\n허나 그렇기에 보필할 보람도 있는 법이지.",
    ),
)

PK_RUNTIME_SUFFIX_FIXES = (
    RecordFix(
        13,
        17,
        ("처, 천하를!?\n이건… 크게 나오", "\n허나 그렇기에 보필할 보람도 있는 법"),
        "천, 천하를!?\n이건 정말… 원대한 포부로군.\n허나 그렇기에 보필할 보람도 있는 법이지.",
    ),
    RecordFix(
        13,
        142,
        ("처, 천하를!?\n이건… 크게 나오", "\n허나 그렇기에 보필할 보람도 있는 법"),
        "천, 천하를!?\n이건 정말… 원대한 포부로군.\n허나 그렇기에 보필할 보람도 있는 법이지.",
    ),
)

PK_RESPONSE_FIXES = (
    RecordFix(
        6,
        2295,
        ("꽤 큰 부탁이군요.\n그만한 대가를 기대해도 되겠습니까?",),
        "훗… 제법 큰 요구로군.\n까놓고 말해, 대가에 달렸지.",
    ),
)


class HotfixError(ValueError):
    """Raised before a candidate is emitted when a scope gate differs."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def require_under(root: Path, candidate: Path, label: str) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise HotfixError(f"{label} escapes its allowed root: {candidate}") from exc
    return candidate


def record_by_coordinate(packed: bytes, fix: RecordFix) -> MsgGameRecord:
    archive = parse_packed_msggame(packed).archive
    try:
        return archive.blocks[fix.block_id].records[fix.record_id]
    except IndexError as exc:
        raise HotfixError(f"missing msggame record {fix.coordinate}") from exc


def static_record(record: MsgGameRecord, fix: RecordFix) -> bytes:
    literals = parse_record_literals(record)
    before = tuple(literal.text for literal in literals)
    if before != fix.before_literals:
        raise HotfixError(
            f"unexpected Korean baseline at {fix.coordinate}: {before!r}"
        )
    if not literals:
        raise HotfixError(f"record {fix.coordinate} has no literal to replace")
    prefix = record.data[: literals[0].marker_offset]
    expected_prefix = bytes.fromhex(fix.prefix_hex)
    if prefix != expected_prefix:
        raise HotfixError(
            f"unexpected opaque prefix at {fix.coordinate}: {prefix.hex().upper()}"
        )
    encoded = fix.after.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise HotfixError(f"reserved literal marker in replacement at {fix.coordinate}")
    return prefix + LITERAL_START + encoded + LITERAL_END + TERMINATOR


def patch_msggame(packed: bytes, fixes: Iterable[RecordFix]) -> bytes:
    fixes = tuple(fixes)
    replacements = {
        (fix.block_id, fix.record_id): static_record(record_by_coordinate(packed, fix), fix)
        for fix in fixes
    }
    rebuilt = rebuild_packed_msggame(packed, replacements)
    verify_patched_msggame(rebuilt, fixes)
    return rebuilt


def verify_patched_msggame(packed: bytes, fixes: Iterable[RecordFix]) -> None:
    for fix in fixes:
        record = record_by_coordinate(packed, fix)
        literals = parse_record_literals(record)
        if len(literals) != 1 or literals[0].text != fix.after:
            raise HotfixError(f"patched literal differs at {fix.coordinate}")
        expected = bytes.fromhex(fix.prefix_hex) + LITERAL_START + fix.after.encode("utf-16-le") + LITERAL_END + TERMINATOR
        if record.data != expected:
            raise HotfixError(f"Japanese suffix bytecode remains at {fix.coordinate}")


def source_phase(steam_root: Path) -> str:
    current = {
        relative: sha256_path(steam_root / relative)
        for relative in INITIAL_BASELINE_SHA256
    }
    if current == INITIAL_BASELINE_SHA256:
        return "initial"
    if current == POST_RUNTIME_SUFFIX_BASELINE_SHA256:
        return "post_runtime_suffix"
    raise HotfixError("Steam dialogue baseline differs from both approved hotfix states")


def active_fixes(phase: str) -> tuple[tuple[RecordFix, ...], tuple[RecordFix, ...]]:
    if phase == "initial":
        return BASE_RUNTIME_SUFFIX_FIXES, PK_RUNTIME_SUFFIX_FIXES + PK_RESPONSE_FIXES
    if phase == "post_runtime_suffix":
        return (), PK_RESPONSE_FIXES
    raise HotfixError(f"unsupported hotfix phase: {phase}")


def patch_target(
    relative: str,
    source: bytes,
    base_fixes: Iterable[RecordFix],
    pk_fixes: Iterable[RecordFix],
) -> bytes:
    if relative == "MSG/JP/msggame.bin":
        fixes = tuple(base_fixes)
        return patch_msggame(source, fixes) if fixes else source
    if relative == "MSG_PK/JP/msggame.bin":
        fixes = tuple(pk_fixes)
        return patch_msggame(source, fixes) if fixes else source
    return source


def write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def output_paths(output_root: Path) -> set[str]:
    actual: set[str] = set()
    for path in output_root.rglob("*"):
        if path.is_file():
            actual.add(path.relative_to(output_root).as_posix())
    return actual


def verify_candidate(steam_root: Path, output_root: Path) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    output_root = output_root.resolve(strict=True)
    phase = source_phase(steam_root)
    base_active, pk_active = active_fixes(phase)
    changed_expected = {
        "MSG/JP/msggame.bin" if base_active else "",
        "MSG_PK/JP/msggame.bin" if pk_active else "",
    } - {""}
    if output_paths(output_root) != set(PROFILE_TARGETS):
        raise HotfixError("candidate tree does not contain the exact eleven-file text profile")
    changed: list[str] = []
    manifest_entries: list[dict[str, object]] = []
    for relative in PROFILE_TARGETS:
        source_path = require_under(steam_root, steam_root / relative, "Steam source")
        candidate_path = require_under(output_root, output_root / relative, "candidate")
        source = source_path.read_bytes()
        candidate = candidate_path.read_bytes()
        source_hash = sha256_bytes(source)
        candidate_hash = sha256_bytes(candidate)
        if relative in changed_expected:
            if candidate == source:
                raise HotfixError(f"candidate did not change {relative}")
            changed.append(relative)
        elif candidate != source:
            raise HotfixError(f"candidate unexpectedly changed {relative}")
        manifest_entries.append(
            {
                "path": relative,
                "source_sha256": source_hash,
                "candidate_sha256": candidate_hash,
                "source_size": len(source),
                "candidate_size": len(candidate),
            }
        )
    if set(changed) != changed_expected:
        raise HotfixError(f"unexpected changed candidate set: {changed!r}")
    verify_patched_msggame(
        (output_root / "MSG/JP/msggame.bin").read_bytes(),
        BASE_RUNTIME_SUFFIX_FIXES,
    )
    verify_patched_msggame(
        (output_root / "MSG_PK/JP/msggame.bin").read_bytes(),
        PK_RUNTIME_SUFFIX_FIXES + PK_RESPONSE_FIXES,
    )
    return {
        "schema": MANIFEST_SCHEMA,
        "status": "PASS",
        "baseline_phase": phase,
        "changed_paths": changed,
        "entries": manifest_entries,
    }


def build(steam_root: Path, output_root: Path, manifest_path: Path) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    phase = source_phase(steam_root)
    base_active, pk_active = active_fixes(phase)
    expected_output = DEFAULT_OUTPUT_ROOT.resolve()
    output_root = output_root.resolve()
    if output_root != expected_output:
        raise HotfixError(f"output root must be the dedicated build directory: {expected_output}")
    temp_parent = output_root.parent
    temp_parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="candidate-", dir=temp_parent))
    try:
        for relative in PROFILE_TARGETS:
            source_path = require_under(steam_root, steam_root / relative, "Steam source")
            if not source_path.is_file():
                raise HotfixError(f"Steam source is absent: {source_path}")
            source = source_path.read_bytes()
            write_bytes(temporary / relative, patch_target(relative, source, base_active, pk_active))
        if output_root.exists():
            require_under(REPO / "tmp" / WORKSTREAM.name, output_root, "candidate output")
            shutil.rmtree(output_root)
        os.replace(temporary, output_root)
        report = verify_candidate(steam_root, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(canonical_json(report))
        return report
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_BUILD_MANIFEST)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = (
            verify_candidate(args.steam_root, args.output_root)
            if args.verify_only
            else build(args.steam_root, args.output_root, args.manifest)
        )
    except (HotfixError, OSError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
