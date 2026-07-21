#!/usr/bin/env python3
"""Build a private Static Patch 007 restoration candidate for reviewed rows.

This combines the completed 3900, 8000, 9000, and 10000--11008
``manual_compact_korean_layout`` review artifacts.  The only Korean binary
input is the strict batch07 candidate.  Review artifacts contribute their
already source-audited Korean text and per-line measurements; direct game
resources are not copied or written here.  The builder writes only below its
own ``tmp`` root and has no Steam, Git, release, or network path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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


SCHEMA = "nobu16.kr.pc-event-manual-compact-static007-3900-11008-restore.v1"
STRICT_WORKSTREAM = "pc_event_manual_compact_static007_batch07_v1"
STRICT_ROOT = REPO / "tmp" / STRICT_WORKSTREAM / "candidate-final"
STRICT_EVENT = STRICT_ROOT / RESOURCE
STRICT_AUDIT = STRICT_ROOT / "audit.v1.json"
STRICT_MANIFEST = STRICT_ROOT / "candidate_manifest.v1.json"
EXPECTED_STRICT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "85C48E864CC06831EB8F31C713703E0E3715848EE049A36B4F53CEB757F186E3",
    "raw_size": 1_020_156,
    "sha256": "5B84334A51829A8D981F4BE5E161D73803894D29F7FA1D91AC40090671CB347D",
    "size": 1_024_182,
}

# Deterministic result from the pinned batch07 input and the four immutable
# review artifacts.  ``build`` and ``verify-private`` fail on any drift.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "2DFE8833BC6153E3EF76701EC8A823CA21AAAFF561090BD06957A0426CC07871",
    "raw_size": 1_042_232,
    "sha256": "A5F09D0E36A044D895C41BEA56ADC6809A9768BF2D3AFE79B1793E8BCC4B1867",
    "size": 1_046_345,
}

RAW_G1N_LIMIT = 1440
EFFECTIVE_LIMIT = 912
MAX_LINES = 4
EXPECTED_REVIEWED_COUNT = 640
EXPECTED_CHANGED_COUNT = 607
EXPECTED_PRESERVED_COUNT = 33

ESC_RE = re.compile(r"\x1bC[ABCZ]")
BRACKET_RE = re.compile(r"\[[^\[\]\r\n]+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")


@dataclass(frozen=True)
class ReviewSpec:
    name: str
    path: Path
    sha256: str
    schema: str
    count: int
    current_key: str
    min_id: int
    max_id: int


@dataclass(frozen=True)
class ReviewRow:
    entry_id: int
    artifact: str
    artifact_relative: str
    artifact_sha256: str
    current_ko: str
    proposed_ko: str
    layout: Mapping[str, Any]
    review_judgement: Any
    restoration_strategy: Any


@dataclass(frozen=True)
class Bundle:
    event: bytes
    profile: Mapping[str, Any]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


REVIEW_SPECS = (
    ReviewSpec(
        "manual_compact_3900_review_v1",
        REPO
        / "workstreams"
        / "manual_compact_3900_review_v1"
        / "public"
        / "manual_compact_3900_review.v1.json",
        "8EAD4E514AEFEEC648579BF17F092E9C9FA915685F5A2D10B306B60C49DD657C",
        "nobu16.kr.manual-compact-3900-review.v1",
        32,
        "current_ko_at_strict_6000_7999_baseline",
        3900,
        3999,
    ),
    ReviewSpec(
        "manual_compact_8000_review_v1",
        REPO
        / "workstreams"
        / "manual_compact_8000_review_v1"
        / "public"
        / "manual_compact_8000_review.v1.json",
        "92A87F636593D0F25CD1417BDD3F4BBBB7A2D5D876E1F911E1EF65F4580110FF",
        "nobu16.kr.manual-compact-8000-review.v1",
        177,
        "current_ko_at_batch06_strict_baseline",
        8000,
        8999,
    ),
    ReviewSpec(
        "manual_compact_9000_review_v1",
        REPO
        / "workstreams"
        / "manual_compact_9000_review_v1"
        / "public"
        / "manual_compact_9000_review.v1.json",
        "86B7326A1461A8B2B62E636B1F1D6FFA8438D2E02C203C291E9997325FE807F0",
        "nobu16.kr.manual-compact-9000-review.v1",
        283,
        "current_ko_at_final_strict_baseline",
        9000,
        9999,
    ),
    ReviewSpec(
        "manual_compact_10000_review_v1",
        REPO
        / "workstreams"
        / "manual_compact_10000_review_v1"
        / "public"
        / "manual_compact_10000_11008_review.v1.json",
        "7F30CBDA90BF281441896F14021F33ABDD23ADFA31894834B9AD970B9997BCE7",
        "nobu16.kr.pc-event-manual-compact-static007-10000-review.v1",
        148,
        "current_ko_at_strict_predecessor",
        10000,
        11008,
    ),
)


class CandidateError(RuntimeError):
    """Raised when a source, review, layout, or output invariant drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def file_record(path: Path) -> Mapping[str, Any]:
    return {
        "relative_path": relative(path),
        "sha256": sha256(path.read_bytes()),
        "size": path.stat().st_size,
    }


def profile(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
        "sha256": sha256(packed),
        "size": len(packed),
    }


def normalized_breaks(value: str) -> str:
    return LINEBREAK_RE.sub("\n", value)


def protected_signature(value: str) -> Mapping[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf_matches}
    other_controls: list[str] = []
    pua: list[str] = []
    for offset, character in enumerate(value):
        if character in "\r\n\x1b":
            continue
        if unicodedata.category(character) == "Cc":
            other_controls.append(f"U+{ord(character):04X}")
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
        "other_c0_controls": other_controls,
        "pua_codepoints": pua,
        "nul_count": value.count("\x00"),
    }


def validate_tags(value: str, entry_id: int) -> None:
    in_colour_span = False
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            tag = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(tag) is not None, f"{entry_id}: malformed tag {tag!r}")
            if tag == "\x1bCZ":
                require(in_colour_span, f"{entry_id}: unmatched colour close")
                in_colour_span = False
            else:
                require(not in_colour_span, f"{entry_id}: nested colour tag")
                in_colour_span = True
            cursor += 3
            continue
        require(not (in_colour_span and character in "\r\n"), f"{entry_id}: LF inside colour tag")
        cursor += 1
    require(not in_colour_span, f"{entry_id}: unterminated colour tag")


def load_json(path: Path) -> Mapping[str, Any]:
    require(path.is_file(), f"missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def load_strict() -> tuple[bytes, Any, tuple[str, ...], Mapping[str, Any], Mapping[str, Any]]:
    root = STRICT_ROOT.resolve(strict=True)
    require(root.is_relative_to((REPO / "tmp").resolve()), "strict candidate escapes tmp")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"strict candidate file scope drift: {sorted(actual_files)}")
    event = STRICT_EVENT.read_bytes()
    header, raw = decompress_wrapper(event)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, "strict table round-trip drift")
    actual_profile = profile(event, raw)
    require(actual_profile == EXPECTED_STRICT_PROFILE, "strict batch07 packed/raw profile drift")
    manifest = load_json(STRICT_MANIFEST)
    audit = load_json(STRICT_AUDIT)
    require(manifest.get("candidate_only") is True, "strict candidate must remain private")
    require(manifest.get("output") == actual_profile, "strict manifest output profile drift")
    require(audit.get("candidate_only") is True, "strict audit must remain candidate-only")
    require(len(table.texts) == 17_916, "strict string count drift")
    return event, header, tuple(table.texts), actual_profile, {
        "workstream": STRICT_WORKSTREAM,
        "candidate_relative": relative(STRICT_ROOT),
        "event_relative": relative(STRICT_EVENT),
        "candidate_manifest": file_record(STRICT_MANIFEST),
        "audit": file_record(STRICT_AUDIT),
        "profile": actual_profile,
    }


def assert_layout(entry_id: int, proposed: str, layout: Mapping[str, Any]) -> None:
    require(layout.get("line_count") == len(normalized_breaks(proposed).split("\n")), f"{entry_id}: layout line count drift")
    require(int(layout.get("line_count", 0)) <= MAX_LINES, f"{entry_id}: more than four lines")
    require(layout.get("all_lines_pass_static_patch_007") is True, f"{entry_id}: artifact layout is not Static Patch 007-safe")
    lines = layout.get("lines")
    require(isinstance(lines, list) and lines, f"{entry_id}: artifact layout lines missing")
    proposed_lines = normalized_breaks(proposed).split("\n")
    require(len(lines) == len(proposed_lines), f"{entry_id}: artifact line list count drift")
    for number, (line, encoded) in enumerate(zip(lines, proposed_lines), 1):
        require(isinstance(line, dict), f"{entry_id}: malformed artifact line")
        require(line.get("line_number") == number, f"{entry_id}: artifact line ordering drift")
        require(line.get("encoded_string") == encoded, f"{entry_id}: artifact encoded line drift")
        require(int(line.get("raw_g1n_width_px", RAW_G1N_LIMIT + 1)) <= RAW_G1N_LIMIT, f"{entry_id}: raw width exceeds 1440")
        require(int(line.get("effective_width_px", EFFECTIVE_LIMIT + 1)) <= EFFECTIVE_LIMIT, f"{entry_id}: effective width exceeds 912")
        require(line.get("exceeds_912px") is False, f"{entry_id}: artifact marks 912 overflow")


def load_reviews(strict_texts: Sequence[str]) -> tuple[tuple[ReviewRow, ...], Mapping[str, Any]]:
    rows: list[ReviewRow] = []
    records: dict[str, Any] = {}
    seen: set[int] = set()
    for spec in REVIEW_SPECS:
        payload = load_json(spec.path)
        require(sha256(spec.path.read_bytes()) == spec.sha256, f"{spec.name}: artifact hash drift")
        require(payload.get("schema") == spec.schema, f"{spec.name}: schema drift")
        entries = payload.get("entries")
        require(isinstance(entries, list) and len(entries) == spec.count, f"{spec.name}: entry count drift")
        artifact_ids: list[int] = []
        for entry in entries:
            require(isinstance(entry, dict), f"{spec.name}: non-object entry")
            entry_id = entry.get("entry_id")
            require(isinstance(entry_id, int), f"{spec.name}: entry id missing")
            require(spec.min_id <= entry_id <= spec.max_id, f"{spec.name}: entry {entry_id} outside declared range")
            require(entry_id not in seen, f"duplicate review entry {entry_id}")
            seen.add(entry_id)
            artifact_ids.append(entry_id)
            current = entry.get(spec.current_key)
            proposed = entry.get("proposed_ko")
            layout = entry.get("layout")
            require(isinstance(current, str), f"{spec.name}:{entry_id}: current text missing")
            require(isinstance(proposed, str), f"{spec.name}:{entry_id}: proposed text missing")
            require(isinstance(layout, dict), f"{spec.name}:{entry_id}: layout missing")
            require(strict_texts[entry_id] == current, f"{spec.name}:{entry_id}: strict baseline text drift")
            validate_tags(current, entry_id)
            validate_tags(proposed, entry_id)
            require(protected_signature(current) == protected_signature(proposed), f"{spec.name}:{entry_id}: control/token signature drift")
            assert_layout(entry_id, proposed, layout)
            rows.append(
                ReviewRow(
                    entry_id=entry_id,
                    artifact=spec.name,
                    artifact_relative=relative(spec.path),
                    artifact_sha256=spec.sha256,
                    current_ko=current,
                    proposed_ko=proposed,
                    layout=layout,
                    review_judgement=entry.get("review_judgement"),
                    restoration_strategy=entry.get("restoration_strategy"),
                )
            )
        records[spec.name] = {
            "artifact": file_record(spec.path),
            "schema": spec.schema,
            "entry_count": len(artifact_ids),
            "entry_ids_sha256": sha256(",".join(str(value) for value in sorted(artifact_ids)).encode("ascii")),
            "strict_baseline_key": spec.current_key,
        }
    rows.sort(key=lambda row: row.entry_id)
    require(len(rows) == EXPECTED_REVIEWED_COUNT, "combined reviewed row count drift")
    return tuple(rows), records


def ids_sha256(ids: Sequence[int]) -> str:
    return sha256(",".join(str(entry_id) for entry_id in ids).encode("ascii"))


def build_bundle(require_output_profile: bool) -> Bundle:
    _event, header, strict_texts, strict_profile, strict_record = load_strict()
    review_rows, artifacts = load_reviews(strict_texts)
    target_texts = list(strict_texts)
    for row in review_rows:
        target_texts[row.entry_id] = row.proposed_ko
    raw = rebuild_message_table(parse_message_table(decompress_wrapper(STRICT_EVENT.read_bytes())[1]), target_texts)
    event = recompress_wrapper(raw, header)
    output_profile = profile(event, raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        require(output_profile == EXPECTED_OUTPUT_PROFILE, "candidate output profile drift")
    after = parse_message_table(decompress_wrapper(event)[1]).texts
    require(tuple(after) == tuple(target_texts), "rebuilt table text drift")
    changed_ids = [row.entry_id for row in review_rows if row.current_ko != row.proposed_ko]
    preserved_ids = [row.entry_id for row in review_rows if row.current_ko == row.proposed_ko]
    require(len(changed_ids) == EXPECTED_CHANGED_COUNT, "changed review row count drift")
    require(len(preserved_ids) == EXPECTED_PRESERVED_COUNT, "preserved review row count drift")
    actual_changed = [index for index, (before, after_text) in enumerate(zip(strict_texts, target_texts)) if before != after_text]
    require(actual_changed == changed_ids, "candidate changed-id scope drift")
    audit_rows = []
    for row in review_rows:
        audit_rows.append(
            {
                "entry_id": row.entry_id,
                "artifact": row.artifact,
                "artifact_relative": row.artifact_relative,
                "artifact_sha256": row.artifact_sha256,
                "changed": row.entry_id in changed_ids,
                "strict_predecessor_ko": row.current_ko,
                "proposed_ko": row.proposed_ko,
                "strict_predecessor_utf16le_sha256": text_sha256(row.current_ko),
                "proposed_utf16le_sha256": text_sha256(row.proposed_ko),
                "control_signature": protected_signature(row.proposed_ko),
                "layout": row.layout,
                "review_judgement": row.review_judgement,
                "restoration_strategy": row.restoration_strategy,
            }
        )
    audit: Mapping[str, Any] = {
        "schema": SCHEMA + ".audit",
        "candidate_only": True,
        "resource": RESOURCE.as_posix(),
        "predecessor": strict_record,
        "review_artifacts": artifacts,
        "static_patch_007_layout": {
            "runtime_font_px": 30,
            "runtime_usable_line_width_px": EFFECTIVE_LIMIT,
            "max_lines": MAX_LINES,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_g1n_pass_limit_px": RAW_G1N_LIMIT,
            "japanese_source_lf_authoritative": False,
        },
        "coverage": {
            "reviewed_row_count": len(review_rows),
            "reviewed_row_ids_sha256": ids_sha256([row.entry_id for row in review_rows]),
            "changed_row_count": len(changed_ids),
            "changed_row_ids": changed_ids,
            "changed_row_ids_sha256": ids_sha256(changed_ids),
            "preserved_row_count": len(preserved_ids),
            "preserved_row_ids": preserved_ids,
            "preserved_row_ids_sha256": ids_sha256(preserved_ids),
            "all_rows_static_patch_007_pass": True,
            "all_rows_four_or_fewer_lines": True,
        },
        "output_event_profile": output_profile,
        "rows": audit_rows,
        "source_policy": {
            "only_korean_binary_input_is_strict_batch07": True,
            "review_artifacts_are_source_audited": True,
            "japanese_source_line_breaks_not_reused": True,
            "sentence_shortening_or_deletion_allowed": False,
            "candidate_binary_written_to_steam": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
    }
    manifest: Mapping[str, Any] = {
        "schema": SCHEMA + ".manifest",
        "candidate_only": True,
        "candidate_output_must_be_under": relative(TMP_ROOT),
        "resource": RESOURCE.as_posix(),
        "predecessor": strict_record,
        "review_artifacts": artifacts,
        "reviewed_row_ids": [row.entry_id for row in review_rows],
        "changed_row_ids": changed_ids,
        "preserved_row_ids": preserved_ids,
        "output": output_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }
    return Bundle(event=event, profile=output_profile, audit=audit, manifest=manifest)


def require_private(path: Path) -> Path:
    resolved = path.resolve()
    root = TMP_ROOT.resolve()
    require(resolved.is_relative_to(root), f"candidate path escapes private tmp root: {resolved}")
    return resolved


def write_candidate(bundle: Bundle) -> Path:
    root = require_private(CANDIDATE_ROOT)
    if root.exists():
        shutil.rmtree(root)
    (root / RESOURCE).parent.mkdir(parents=True, exist_ok=True)
    (root / RESOURCE).write_bytes(bundle.event)
    (root / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
    (root / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
    return root


def verify_private_candidate() -> Mapping[str, Any]:
    bundle = build_bundle(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"candidate missing: {root}")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"candidate file scope drift: {sorted(actual_files)}")
    require((root / RESOURCE).read_bytes() == bundle.event, "candidate event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": relative(root),
        "event_profile": bundle.profile,
        "reviewed_row_count": bundle.audit["coverage"]["reviewed_row_count"],
        "changed_row_count": bundle.audit["coverage"]["changed_row_count"],
        "preserved_row_count": bundle.audit["coverage"]["preserved_row_count"],
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_manual_compact_static007_3900_11008_restore_v1.py",
        WORKSTREAM / "test_pc_event_manual_compact_static007_3900_11008_restore_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    args = parser.parse_args()
    if args.command == "profile":
        print(json.dumps(build_bundle(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        print(relative(write_candidate(build_bundle(require_output_profile=True))))
        return 0
    if args.command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = build_bundle(require_output_profile=True)
    print(
        json.dumps(
            {
                "changed_row_ids": bundle.audit["coverage"]["changed_row_ids"],
                "event_profile": bundle.profile,
                "preserved_row_ids": bundle.audit["coverage"]["preserved_row_ids"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
