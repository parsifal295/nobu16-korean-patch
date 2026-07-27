#!/usr/bin/env python3
"""Prepare and validate the v0.15.0 full PC character-dialogue retranslation.

This program deliberately separates source-bearing review material from the
repository.  It reads the Steam installation but never writes it.  The only
writable location is a deterministic directory below ``tmp/``:

* a private record-context queue contains the JP source, current KO target,
  and available PC EN/SC/TC context;
* source-free ledgers track every current literal and its review batch;
* a complete, approved private decision set can produce a *candidate* under
  that same temporary directory, never a Steam deployment.

The queue does not treat previous coverage, an absence of Japanese glyphs, or
an old correction as a semantic verdict.  Every visible current literal starts
as unreviewed.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp"
DEFAULT_OUTPUT_ROOT = TMP / WORKSTREAM.name
DEFAULT_STEAM_ROOT = Path(
    os.environ.get(
        "NOBU16_DIALOGUE_STEAM_ROOT",
        r"F:\SteamLibrary\steamapps\common\NOBU16",
    )
)
DEFAULT_BASE_PRISTINE = Path(
    r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root\MSG\JP\msggame.bin"
)
DEFAULT_PK_PRISTINE = (
    DEFAULT_STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
CONTRACT_PATH = WORKSTREAM / "review_contract.v1.json"
RUNTIME_VM_COVERAGE_PATH = (
    REPO
    / "workstreams"
    / "base_msggame_runtime_vm_audit_v1"
    / "public"
    / "base_msggame_runtime_vm_coverage.v1.json"
)
PK_RUNTIME_VM_OVERLAY_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_exact_reuse_runtime_vm_verified.private.v1.jsonl"
)
PK_RUNTIME_VM_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_runtime_vm_promotion.v1.json"
)
PK_FULL_CANDIDATE_RUNTIME_VM_OVERLAY_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_full_candidate_runtime_vm_verified.private.v1.jsonl"
)
PK_FULL_CANDIDATE_RUNTIME_VM_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_full_candidate_runtime_vm_promotion.v1.json"
)
PK_RESIDUAL_RUNTIME_VM_OVERLAY_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_residual_runtime_vm_verified.private.v1.jsonl"
)
PK_RESIDUAL_RUNTIME_VM_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_residual_runtime_vm_promotion.v1.json"
)
PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_OVERLAY_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_exact_blocked_pk_only_closure_verified.private.v1.jsonl"
)
PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_exact_blocked_pk_only_closure_promotion.v1.json"
)
PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_OVERLAY_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_pending_cross_resource_exact_closure_verified.private.v1.jsonl"
)
PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_pending_cross_resource_exact_closure_promotion.v1.json"
)
BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_OVERLAY_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "base_msggame_dynamic_honorific_spacing_delta_verified.private.v1.jsonl"
)
BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_REPORT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "base_msggame_dynamic_honorific_spacing_delta.v1.json"
)
PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_OVERLAY_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_dynamic_honorific_spacing_closure_verified.private.v1.jsonl"
)
PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_REPORT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_dynamic_honorific_spacing_closure_promotion.v1.json"
)
PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_EVIDENCE_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_bound_terminal_family_exact_closure_evidence.private.v1.jsonl"
)
PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_REPORT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_bound_terminal_family_exact_closure_promotion.v1.json"
)
PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_EVIDENCE_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_thought_predicate_family_exact_closure_evidence.private.v1.jsonl"
)
PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_REPORT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_thought_predicate_family_exact_closure_promotion.v1.json"
)
PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_EVIDENCE_PATH = (
    DEFAULT_OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_bound_terminal_caller_full_closure_evidence.private.v1.jsonl"
)
PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_REPORT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_bound_terminal_caller_full_closure_promotion.v1.json"
)

sys.path[:0] = [str(REPO / "tools"), str(REPO / "workstreams" / "msggame")]

from msggame_format import (  # noqa: E402
    MsgGameArchive,
    MsgGameRecord,
    iter_literals,
    is_visible_translation_candidate,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
)


SCHEMA = "nobu16.kr.pc-dialogue-full-retranslation.v1"
QUEUE_SCHEMA = f"{SCHEMA}.private-review-queue"
LEDGER_SCHEMA = f"{SCHEMA}.source-free-target-ledger"
BATCH_SCHEMA = f"{SCHEMA}.source-free-batches"
SUMMARY_SCHEMA = f"{SCHEMA}.source-free-summary"
DECISION_SCHEMA = f"{SCHEMA}.private-decision"
MANIFEST_SCHEMA = f"{SCHEMA}.candidate-manifest"
RUNTIME_VM_COVERAGE_SCHEMA = "nobu16.kr.base-msggame-runtime-vm-coverage.v1"
RUNTIME_VM_ROW_VERIFICATION_SCHEMA = (
    "nobu16.kr.base-msggame-runtime-vm-row-verification.v1"
)
PK_RUNTIME_VM_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-exact-reuse-runtime-vm-verification-overlay-row.v1"
)
PK_FULL_CANDIDATE_RUNTIME_VM_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-full-candidate-runtime-vm-verification-overlay-row.v1"
)
PK_RESIDUAL_RUNTIME_VM_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-residual-runtime-vm-verification-overlay-row.v1"
)
PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-exact-blocked-pk-only-closure-overlay-row.v1"
)
PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-pending-cross-resource-exact-closure-overlay-row.v1"
)
BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.base-msggame-dynamic-honorific-spacing-delta-row.v1"
)
PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-dynamic-honorific-spacing-closure-row.v1"
)
PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_EVIDENCE_ROW_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-family-exact-closure-evidence-row.v1"
)
PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_EVIDENCE_ROW_SCHEMA = (
    "nobu16.kr.pk-thought-predicate-family-exact-closure-evidence-row.v1"
)
PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_EVIDENCE_ROW_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-caller-full-closure-evidence-row.v1"
)
RUNTIME_VM_VERIFICATION_METHOD = "reversed_vm_static_analysis"
PK_FULL_CANDIDATE_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_full_candidate_static_analysis"
)
PK_RESIDUAL_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_residual_full_closure_nonexpansion_analysis"
)
PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_pk_only_exact_blocked_closure_nonexpansion_analysis"
)
PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_cross_resource_exact_closure_analysis"
)
BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_dynamic_honorific_spacing_delta_analysis"
)
PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_dynamic_honorific_spacing_closure_analysis"
)
PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_pk_bound_terminal_family_exact_closure_analysis"
)
PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_pk_thought_predicate_family_exact_closure_analysis"
)
PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD = (
    "reversed_vm_pk_bound_terminal_caller_full_closure_analysis"
)
PK_RUNTIME_VM_VERIFICATION_METHODS = frozenset(
    {
        RUNTIME_VM_VERIFICATION_METHOD,
        PK_FULL_CANDIDATE_RUNTIME_VM_VERIFICATION_METHOD,
        PK_RESIDUAL_RUNTIME_VM_VERIFICATION_METHOD,
        PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_VERIFICATION_METHOD,
        PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_VERIFICATION_METHOD,
        BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
        PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
        PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD,
        PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD,
        PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD,
    }
)
RUNTIME_BOUNDARY_LEADING_SPACE_COORDINATES = frozenset(
    {
        ("base_msggame", "0:1271:0"),
        ("base_msggame", "0:1275:0"),
        ("pk_msggame", "0:1325:0"),
        ("pk_msggame", "0:1329:0"),
    }
)
THOUGHT_PREDICATE_SUPERSEDED_TERMINAL_ACTION_COORDINATES = frozenset(
    {
        ("pk_msggame", "6:3551:1"),
        ("pk_msggame", "6:4398:0"),
        ("pk_msggame", "6:4437:0"),
        ("pk_msggame", "15:1430:1"),
        ("pk_msggame", "15:1698:1"),
    }
)
CALLER_SUPERSEDED_TERMINAL_ACTION_COORDINATES = frozenset(
    {
        ("pk_msggame", "6:3863:0"),
        ("pk_msggame", "6:3863:2"),
        ("pk_msggame", "6:3863:3"),
        ("pk_msggame", "6:3941:0"),
        ("pk_msggame", "6:3941:1"),
        ("pk_msggame", "6:3941:2"),
        ("pk_msggame", "15:277:1"),
        ("pk_msggame", "15:278:1"),
        ("pk_msggame", "15:703:0"),
        ("pk_msggame", "15:703:1"),
        ("pk_msggame", "15:703:2"),
    }
)
CALLER_SUPERSEDED_THOUGHT_ACTION_COORDINATE = (
    "pk_msggame",
    "15:1068:0",
)
CALLER_RUNTIME_ASSEMBLY_BOUNDARY_REFLOW_COORDINATES = frozenset(
    {
        ("pk_msggame", "6:4707:0"),
        ("pk_msggame", "15:756:3"),
    }
)
CALLER_COMBINED_CANDIDATE_SHA256 = (
    "498A9A19FA33B57789C6FBF3732DA61967FEDE8055F034F68E43E628C16ED74F"
)
CALLER_COMBINED_OVERLAP_RECORD_SHA256 = (
    "564F81EBB9353750EAFAB190D1A5E3F1050783E0B4D5D526DD7A60DC2F8AC109"
)
CALLER_COMBINED_OVERLAP_ROOT_PROOF_SHA256 = (
    "4121CA04E8DBED2824744D668A0E7DA699A84FCE76DD6C1CE0F37C70904F2994"
)
CALLER_COMBINED_TARGET_DELTA_SHA256 = (
    "3F719E9F54EB226ABE19ADFCCBA9BF2A1926BDC133E1FBD33A567E3DF0994E3F"
)
CALLER_COMBINED_ASSEMBLY_MANIFEST_SHA256 = (
    "0B0A9FD6DB8FC102D6871D7E5A520A7F1AB0A623EC504BCA369928D9DDC7850A"
)
CALLER_COMBINED_OVERLAP_EVIDENCE_SHA256 = (
    "BD82EF31C36A7E32FA6E0A3D59A27A54E0528369CD661D9603E42B49109FB998"
)
CALLER_COMBINED_RENEWAL_REFERENCE_SHA256 = (
    "56766E27D4B786BE1ED3AFEDDC61F1743E3C2CEF2A72111EF7F70AE920C680DA"
)
DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHODS = frozenset(
    {
        BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
        PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
    }
)
SOURCE_OUTER_WHITESPACE_REPAIR_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-msggame-runtime-gap-repair.v1.private-evidence"
)
SOURCE_OUTER_WHITESPACE_REPAIR_CANDIDATE_RECORD_SHA256 = (
    "290E5692BD4B6DBD047F83745D07E4AEFDB3C194C98E0A351CB93822BE4E058D"
)
BATCH_VISIBLE_TARGET_SIZE = 200
SCOPE_CLASSIFICATIONS = {
    "retranslated",
    "runtime_fragment_pending",
    "confirmed_non_display",
}

KANA_OR_HAN_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
ESC_TAG_RE = re.compile(r"\x1bC.")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
BRACKET_TOKEN_RE = re.compile(r"\[[A-Za-z]+\d+\]")
EMPTY_RUNTIME_MORPHEME_SOURCE_BY_KIND = {
    "japanese_sentence_final_particle": frozenset({"\u308f", "\u305e"}),
    "japanese_honorific_prefix": frozenset({"\u304a", "\u3054"}),
}


class RetranslationError(ValueError):
    """Raised when a baseline, decision, or invariant is not safe to use."""


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative_path: Path
    pristine_path: Path
    contexts: tuple[str, ...]
    expected_pristine_sha256: str


@dataclass(frozen=True)
class ResourceInput:
    spec: ResourceSpec
    current_path: Path
    current_blob: bytes
    current_archive: MsgGameArchive
    pristine_blob: bytes
    pristine_archive: MsgGameArchive
    context_archives: Mapping[str, MsgGameArchive]
    file_hashes: Mapping[str, str]


@dataclass(frozen=True)
class PreparedArtifacts:
    queue: str
    ledger: str
    batches: str
    summary: str
    resources: Mapping[str, ResourceInput]
    visible_targets: Mapping[tuple[str, int, int, int], Mapping[str, Any]]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def canonical_ascii_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) for row in rows)


def atomic_write(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        mode = "wb" if isinstance(content, bytes) else "w"
        kwargs: dict[str, Any] = {} if isinstance(content, bytes) else {"encoding": "utf-8", "newline": "\n"}
        with os.fdopen(descriptor, mode, **kwargs) as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def safe_output_root(path: Path) -> Path:
    root = TMP.resolve()
    resolved = path.resolve(strict=False)
    if resolved == root or root not in resolved.parents:
        raise RetranslationError(f"output must stay below {root}: {resolved}")
    return resolved


def coordinate(block_id: int, record_id: int, literal_id: int) -> str:
    return f"{block_id}:{record_id}:{literal_id}"


def record_coordinate(record: MsgGameRecord) -> str:
    return f"{record.block_id}:{record.record_id}"


def archive_records(archive: MsgGameArchive) -> dict[tuple[int, int], MsgGameRecord]:
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def protected_signature(text: str) -> dict[str, Any]:
    """Extract language-independent markup that a new Korean line must keep."""
    return {
        "escape_tags": ESC_TAG_RE.findall(text),
        "printf_tokens": PRINTF_RE.findall(text),
        "bracket_tokens": BRACKET_TOKEN_RE.findall(text),
        "non_layout_controls": [
            f"U+{ord(character):04X}"
            for character in text
            if ord(character) < 32 and character not in "\t\n\r"
        ],
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
    }


def record_gap_bytes(record: MsgGameRecord) -> tuple[bytes, ...]:
    literals = parse_record_literals(record)
    if not literals:
        return (record.data,)
    gaps: list[bytes] = [record.data[: literals[0].marker_offset]]
    for left, right in zip(literals, literals[1:]):
        gaps.append(record.data[left.marker_end : right.marker_offset])
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def direct_call_operands(record: MsgGameRecord) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(match.group(1), "little")
        for gap in record_gap_bytes(record)
        for match in re.finditer(b"\x01\x43(.{4})", gap, re.DOTALL)
    )


def resource_specs(steam_root: Path, base_pristine: Path, pk_pristine: Path) -> tuple[ResourceSpec, ...]:
    return (
        ResourceSpec(
            "base_msggame",
            Path("MSG/JP/msggame.bin"),
            base_pristine,
            ("SC", "TC"),
            "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        ),
        ResourceSpec(
            "pk_msggame",
            Path("MSG_PK/JP/msggame.bin"),
            pk_pristine,
            ("EN", "SC", "TC"),
            "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        ),
    )


def context_path(steam_root: Path, relative_path: Path, language: str) -> Path:
    parts = list(relative_path.parts)
    if len(parts) != 3 or parts[1] != "JP":
        raise RetranslationError(f"unexpected JP resource layout: {relative_path}")
    parts[1] = language
    return steam_root.joinpath(*parts)


def load_resource_inputs(steam_root: Path, base_pristine: Path, pk_pristine: Path) -> dict[str, ResourceInput]:
    result: dict[str, ResourceInput] = {}
    for spec in resource_specs(steam_root, base_pristine, pk_pristine):
        current_path = steam_root / spec.relative_path
        required_paths = {"current_ko": current_path, "pristine_jp": spec.pristine_path}
        required_paths.update({language: context_path(steam_root, spec.relative_path, language) for language in spec.contexts})
        for label, path in required_paths.items():
            if not path.is_file():
                raise RetranslationError(f"missing {spec.name} {label} input: {path}")

        blobs = {label: path.read_bytes() for label, path in required_paths.items()}
        hashes = {label: sha256_bytes(blob) for label, blob in blobs.items()}
        if hashes["pristine_jp"] != spec.expected_pristine_sha256:
            raise RetranslationError(
                f"{spec.name} pristine JP hash drift: expected {spec.expected_pristine_sha256}, "
                f"got {hashes['pristine_jp']}"
            )
        current_archive = parse_packed_msggame(blobs["current_ko"]).archive
        pristine_archive = parse_packed_msggame(blobs["pristine_jp"]).archive
        context_archives = {language: parse_packed_msggame(blobs[language]).archive for language in spec.contexts}
        pristine_records = archive_records(pristine_archive)
        current_records = archive_records(current_archive)
        if set(pristine_records) != set(current_records):
            raise RetranslationError(f"{spec.name} current KO record coordinates drift from pristine JP")
        for language, archive in context_archives.items():
            if set(archive_records(archive)) != set(pristine_records):
                raise RetranslationError(f"{spec.name} PC {language} record coordinates drift from pristine JP")
        result[spec.name] = ResourceInput(
            spec=spec,
            current_path=current_path,
            current_blob=blobs["current_ko"],
            current_archive=current_archive,
            pristine_blob=blobs["pristine_jp"],
            pristine_archive=pristine_archive,
            context_archives=context_archives,
            file_hashes=hashes,
        )
    return result


def iter_record_contexts(resource: ResourceInput) -> Iterable[dict[str, Any]]:
    pristine_records = archive_records(resource.pristine_archive)
    current_records = archive_records(resource.current_archive)
    context_records = {language: archive_records(archive) for language, archive in resource.context_archives.items()}
    for key in sorted(pristine_records):
        source_record = pristine_records[key]
        target_record = current_records[key]
        source_literals = list(parse_record_literals(source_record))
        target_literals = list(parse_record_literals(target_record))
        if len(target_literals) > len(source_literals):
            raise RetranslationError(
                f"{resource.spec.name} {record_coordinate(source_record)} has more current KO literals "
                "than pristine JP literals; rebase the record mapping before review"
            )
        if not source_literals and target_literals:
            raise RetranslationError(f"{resource.spec.name} target literals have no pristine JP record context")
        if not source_literals and not target_literals:
            continue
        context_literals = {
            language: [literal.text for literal in parse_record_literals(context_records[language][key])]
            for language in resource.spec.contexts
        }
        yield {
            "resource": resource.spec.name,
            "record_coordinate": record_coordinate(source_record),
            "source_record_raw_sha256": sha256_bytes(source_record.data),
            "current_record_raw_sha256": sha256_bytes(target_record.data),
            "source_jp_literals": [literal.text for literal in source_literals],
            "current_ko_literals": [literal.text for literal in target_literals],
            "pc_context_literals": context_literals,
            "source_literal_count": len(source_literals),
            "current_literal_count": len(target_literals),
            "target_literals": [
                {
                    "coordinate": coordinate(literal.block_id, literal.record_id, literal.literal_id),
                    "current_ko_utf16le_sha256": sha256_text(literal.text),
                    "visible": is_visible_translation_candidate(literal.text),
                    "current_line_count": literal.text.count("\n") + 1 if literal.text else 0,
                    "protected_signature": protected_signature(literal.text),
                }
                for literal in target_literals
            ],
        }


def make_batches(rows: Sequence[Mapping[str, Any]]) -> tuple[dict[tuple[str, str], str], list[dict[str, Any]]]:
    assignments: dict[tuple[str, str], str] = {}
    batches: list[dict[str, Any]] = []
    current_rows: list[Mapping[str, Any]] = []
    current_resource: str | None = None
    current_visible_count = 0
    serials: Counter[str] = Counter()

    def finish() -> None:
        nonlocal current_rows, current_resource, current_visible_count
        if not current_rows or current_resource is None:
            return
        serials[current_resource] += 1
        batch_id = f"{current_resource}-B{serials[current_resource]:03d}"
        source_count = sum(int(row["source_literal_count"]) for row in current_rows)
        target_count = sum(int(row["current_literal_count"]) for row in current_rows)
        for row in current_rows:
            assignments[(current_resource, str(row["record_coordinate"]))] = batch_id
        batches.append(
            {
                "batch_id": batch_id,
                "resource": current_resource,
                "record_count": len(current_rows),
                "source_literal_count": source_count,
                "current_literal_count": target_count,
                "visible_current_literal_count": current_visible_count,
                "first_record_coordinate": current_rows[0]["record_coordinate"],
                "last_record_coordinate": current_rows[-1]["record_coordinate"],
                "review_status": "unreviewed",
            }
        )
        current_rows = []
        current_resource = None
        current_visible_count = 0

    for row in rows:
        resource = str(row["resource"])
        visible_count = sum(1 for item in row["target_literals"] if item["visible"])
        if current_resource is not None and current_resource != resource:
            finish()
        if current_rows and current_visible_count + visible_count > BATCH_VISIBLE_TARGET_SIZE:
            finish()
        if current_resource is None:
            current_resource = resource
        current_rows.append(row)
        current_visible_count += visible_count
    finish()
    return assignments, batches


def prepare_artifacts(steam_root: Path, base_pristine: Path, pk_pristine: Path) -> PreparedArtifacts:
    resources = load_resource_inputs(steam_root, base_pristine, pk_pristine)
    raw_rows: list[dict[str, Any]] = []
    for resource in resources.values():
        raw_rows.extend(iter_record_contexts(resource))
    assignments, batches = make_batches(raw_rows)
    queue_rows: list[dict[str, Any]] = []
    ledger_rows: list[dict[str, Any]] = []
    visible_targets: dict[tuple[str, int, int, int], Mapping[str, Any]] = {}
    resource_counts: dict[str, Counter[str]] = {name: Counter() for name in resources}

    for row in raw_rows:
        resource_name = str(row["resource"])
        record_key = str(row["record_coordinate"])
        batch_id = assignments[(resource_name, record_key)]
        queue_row = {"schema": QUEUE_SCHEMA, "batch_id": batch_id, **row}
        queue_rows.append(queue_row)
        resource_counts[resource_name]["source_records"] += 1
        resource_counts[resource_name]["source_literals"] += int(row["source_literal_count"])
        resource_counts[resource_name]["current_literals"] += int(row["current_literal_count"])
        for target in row["target_literals"]:
            coordinate_parts = tuple(int(value) for value in str(target["coordinate"]).split(":"))
            target_key = (resource_name, *coordinate_parts)
            if target_key in visible_targets:
                raise RetranslationError(f"duplicate current target coordinate: {target_key}")
            source_free = {
                "schema": LEDGER_SCHEMA,
                "resource": resource_name,
                "coordinate": target["coordinate"],
                "record_coordinate": record_key,
                "batch_id": batch_id,
                "source_record_raw_sha256": row["source_record_raw_sha256"],
                "current_record_raw_sha256": row["current_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "current_line_count": target["current_line_count"],
                "visible": target["visible"],
                "review_status": "unreviewed" if target["visible"] else "not_translatable_blank",
                "semantic_completion": False,
            }
            ledger_rows.append(source_free)
            if target["visible"]:
                visible_targets[target_key] = source_free
                resource_counts[resource_name]["visible_current_literals"] += 1
            else:
                resource_counts[resource_name]["blank_current_literals"] += 1

    if len(ledger_rows) != sum(item["current_literals"] for item in resource_counts.values()):
        raise RetranslationError("source-free target ledger count does not match current target universe")
    summary = {
        "schema": SUMMARY_SCHEMA,
        "release_target": "0.15.0",
        "semantic_completion": False,
        "translation_status": "not_started",
        "source_text_in_summary": False,
        "switch_korean_used": False,
        "historic_korean_used": False,
        "steam_write_performed": False,
        "candidate_deployed_to_steam": False,
        "batch_visible_target_size": BATCH_VISIBLE_TARGET_SIZE,
        "resource_summaries": {
            name: {
                "relative_path": str(resource.spec.relative_path).replace("\\", "/"),
                "file_sha256": dict(resource.file_hashes),
                **dict(resource_counts[name]),
            }
            for name, resource in resources.items()
        },
        "total_source_record_count": sum(item["source_records"] for item in resource_counts.values()),
        "total_source_literal_count": sum(item["source_literals"] for item in resource_counts.values()),
        "total_current_literal_count": len(ledger_rows),
        "total_visible_current_literal_count": len(visible_targets),
        "total_blank_current_literal_count": sum(item["blank_current_literals"] for item in resource_counts.values()),
        "batch_count": len(batches),
        "artifacts": {
            "review_queue_private_sha256": sha256_bytes(jsonl(queue_rows).encode("utf-8")),
            "target_ledger_source_free_sha256": sha256_bytes(jsonl(ledger_rows).encode("utf-8")),
            "review_batches_source_free_sha256": sha256_bytes(canonical_json({"schema": BATCH_SCHEMA, "batches": batches}).encode("utf-8")),
        },
    }
    return PreparedArtifacts(
        queue=jsonl(queue_rows),
        ledger=jsonl(ledger_rows),
        batches=canonical_json({"schema": BATCH_SCHEMA, "batches": batches}),
        summary=canonical_json(summary),
        resources=resources,
        visible_targets=visible_targets,
    )


def artifact_paths(output_root: Path) -> dict[str, Path]:
    return {
        "queue": output_root / "review_queue.private.v1.jsonl",
        "ledger": output_root / "target_ledger.source_free.v1.jsonl",
        "batches": output_root / "review_batches.source_free.v1.json",
        "summary": output_root / "summary.source_free.v1.json",
        "decisions": output_root / "review_decisions.private.v1.jsonl",
    }


def write_prepared(output_root: Path, prepared: PreparedArtifacts) -> None:
    paths = artifact_paths(output_root)
    atomic_write(paths["queue"], prepared.queue)
    atomic_write(paths["ledger"], prepared.ledger)
    atomic_write(paths["batches"], prepared.batches)
    atomic_write(paths["summary"], prepared.summary)


def validate_written(output_root: Path, prepared: PreparedArtifacts) -> None:
    paths = artifact_paths(output_root)
    expected = {
        "queue": prepared.queue,
        "ledger": prepared.ledger,
        "batches": prepared.batches,
        "summary": prepared.summary,
    }
    for name, content in expected.items():
        path = paths[name]
        if not path.is_file():
            raise RetranslationError(f"required generated artifact is absent: {path}")
        if path.read_text(encoding="utf-8") != content:
            raise RetranslationError(f"generated artifact drift: {path}")


def load_decisions(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RetranslationError(f"private decision file is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RetranslationError(f"invalid decision JSON at line {line_number}") from exc
        if not isinstance(row, dict):
            raise RetranslationError(f"decision at line {line_number} is not an object")
        rows.append(row)
    return rows


def parse_coordinate(value: object, label: str) -> tuple[int, int, int]:
    if not isinstance(value, str):
        raise RetranslationError(f"{label} must be a coordinate string")
    parts = value.split(":")
    if len(parts) != 3:
        raise RetranslationError(f"{label} must contain block:record:literal")
    try:
        result = tuple(int(part) for part in parts)
    except ValueError as exc:
        raise RetranslationError(f"{label} has a non-numeric component") from exc
    if any(part < 0 for part in result):
        raise RetranslationError(f"{label} has a negative component")
    return result  # type: ignore[return-value]


def load_runtime_vm_coverage() -> tuple[dict[str, Any], str]:
    if not RUNTIME_VM_COVERAGE_PATH.is_file():
        raise RetranslationError(
            f"tracked runtime VM coverage report is absent: {RUNTIME_VM_COVERAGE_PATH}"
        )
    raw = RUNTIME_VM_COVERAGE_PATH.read_bytes()
    try:
        report = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetranslationError(
            f"tracked runtime VM coverage report is invalid: {RUNTIME_VM_COVERAGE_PATH}"
        ) from exc
    if not isinstance(report, dict):
        raise RetranslationError("tracked runtime VM coverage report is not an object")
    if report.get("schema") != RUNTIME_VM_COVERAGE_SCHEMA:
        raise RetranslationError(
            "tracked runtime VM coverage report has an unexpected schema"
        )
    if report.get("status") != "PASS":
        raise RetranslationError("tracked runtime VM coverage report is not PASS")
    guards = report.get("guards")
    if not isinstance(guards, dict):
        raise RetranslationError("tracked runtime VM coverage report has no guards object")
    if not isinstance(guards.get("row_verification_guards"), dict):
        raise RetranslationError(
            "tracked runtime VM coverage report has no row verification guards"
        )
    if not isinstance(guards.get("record_template_guards"), dict):
        raise RetranslationError(
            "tracked runtime VM coverage report has no record template guards"
        )
    return report, sha256_bytes(raw)


def load_pk_runtime_vm_overlays() -> dict[
    tuple[str, str],
    dict[str, Any],
]:
    specs = (
        (
            PK_RUNTIME_VM_OVERLAY_PATH,
            PK_RUNTIME_VM_PROMOTION_PATH,
            PK_RUNTIME_VM_OVERLAY_ROW_SCHEMA,
            RUNTIME_VM_VERIFICATION_METHOD,
            "nobu16.kr.pk-msggame-runtime-vm-promotion.v1",
            "pk_msggame",
        ),
        (
            PK_FULL_CANDIDATE_RUNTIME_VM_OVERLAY_PATH,
            PK_FULL_CANDIDATE_RUNTIME_VM_PROMOTION_PATH,
            PK_FULL_CANDIDATE_RUNTIME_VM_OVERLAY_ROW_SCHEMA,
            PK_FULL_CANDIDATE_RUNTIME_VM_VERIFICATION_METHOD,
            "nobu16.kr.pk-msggame-full-candidate-runtime-vm-promotion.v1",
            "pk_msggame",
        ),
        (
            PK_RESIDUAL_RUNTIME_VM_OVERLAY_PATH,
            PK_RESIDUAL_RUNTIME_VM_PROMOTION_PATH,
            PK_RESIDUAL_RUNTIME_VM_OVERLAY_ROW_SCHEMA,
            PK_RESIDUAL_RUNTIME_VM_VERIFICATION_METHOD,
            "nobu16.kr.pk-msggame-residual-runtime-vm-promotion.v1",
            "pk_msggame",
        ),
        (
            PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_OVERLAY_PATH,
            PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_PROMOTION_PATH,
            PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_OVERLAY_ROW_SCHEMA,
            PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_VERIFICATION_METHOD,
            (
                "nobu16.kr.pk-msggame-exact-blocked-pk-only-closure-"
                "promotion.v1"
            ),
            "pk_msggame",
        ),
        (
            PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_OVERLAY_PATH,
            PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_PROMOTION_PATH,
            PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_OVERLAY_ROW_SCHEMA,
            PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_VERIFICATION_METHOD,
            (
                "nobu16.kr.pk-msggame-pending-cross-resource-exact-"
                "closure-promotion.v1"
            ),
            "pk_msggame",
        ),
        (
            BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_OVERLAY_PATH,
            BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_REPORT_PATH,
            BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_OVERLAY_ROW_SCHEMA,
            BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
            "nobu16.kr.base-msggame-dynamic-honorific-spacing-delta.v1",
            "base_msggame",
        ),
        (
            PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_OVERLAY_PATH,
            PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_REPORT_PATH,
            PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_OVERLAY_ROW_SCHEMA,
            PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
            (
                "nobu16.kr.pk-msggame-dynamic-honorific-spacing-closure-"
                "promotion.v1"
            ),
            "pk_msggame",
        ),
        (
            PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_EVIDENCE_PATH,
            PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_REPORT_PATH,
            PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_EVIDENCE_ROW_SCHEMA,
            PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD,
            (
                "nobu16.kr.pk-bound-terminal-family-exact-closure-"
                "promotion.v1"
            ),
            "pk_msggame",
        ),
        (
            PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_EVIDENCE_PATH,
            PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_REPORT_PATH,
            PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_EVIDENCE_ROW_SCHEMA,
            PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD,
            (
                "nobu16.kr.pk-thought-predicate-family-exact-closure-"
                "promotion.v1"
            ),
            "pk_msggame",
        ),
        (
            PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_EVIDENCE_PATH,
            PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_REPORT_PATH,
            PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_EVIDENCE_ROW_SCHEMA,
            PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD,
            (
                "nobu16.kr.pk-bound-terminal-caller-full-closure-"
                "promotion.v1"
            ),
            "pk_msggame",
        ),
    )
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for (
        overlay_path,
        promotion_path,
        row_schema,
        method,
        promotion_schema,
        expected_resource,
    ) in specs:
        if not overlay_path.is_file() or not promotion_path.is_file():
            continue
        try:
            promotion = json.loads(
                promotion_path.read_text(encoding="utf-8")
            )
            raw_overlay = overlay_path.read_bytes()
            overlay_lines = raw_overlay.decode("utf-8").splitlines()
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            OSError,
        ) as exc:
            raise RetranslationError(
                f"tracked PK runtime VM overlay is invalid: {overlay_path}"
            ) from exc
        terminal_family = (
            method
            == PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
        )
        thought_predicate_family = (
            method
            == PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
        )
        caller_family = (
            method
            == PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
        )
        evidence_family = (
            terminal_family or thought_predicate_family or caller_family
        )
        private_hash_field = (
            "private_evidence_sha256"
            if evidence_family
            else "private_overlay_sha256"
        )
        if (
            not isinstance(promotion, dict)
            or promotion.get("schema") != promotion_schema
            or promotion.get("status") != "PASS"
            or promotion.get("steam_write_performed") is not False
            or (
                method
                in DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHODS
                and (
                    promotion.get("resource") != expected_resource
                    or promotion.get("method") != method
                )
            )
            or (
                evidence_family
                and (
                    promotion.get("resource") != "MSG_PK/JP/msggame.bin"
                    or promotion.get("method") != method
                )
            )
            or promotion.get("result", {}).get(private_hash_field)
            != sha256_bytes(raw_overlay)
        ):
            raise RetranslationError(
                "tracked PK runtime VM promotion report or overlay hash "
                f"drifted: {overlay_path}"
            )
        source_count = 0
        for line_number, line in enumerate(overlay_lines, start=1):
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RetranslationError(
                    f"invalid PK runtime VM overlay JSON at "
                    f"{overlay_path}:{line_number}"
                ) from exc
            if not isinstance(row, dict):
                raise RetranslationError(
                    f"PK runtime VM overlay row is not an object: "
                    f"{overlay_path}:{line_number}"
                )
            coordinate = row.get("coordinate")
            parse_coordinate(
                coordinate,
                f"PK runtime VM overlay row {line_number}.coordinate",
            )
            key = (row_schema, str(coordinate))
            if not isinstance(coordinate, str) or key in rows:
                raise RetranslationError(
                    f"duplicate PK runtime VM overlay coordinate: {key}"
                )
            dynamic_honorific = (
                method
                in DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHODS
            )
            base_row_valid = (
                row.get("schema") == row_schema
                and row.get("resource") == expected_resource
                and (
                    row.get("status") in {"verified", "pending"}
                    if terminal_family or caller_family
                    else row.get("status") == "verified"
                )
                and row.get("method") == method
                and row.get("per_row_game_playback_required") is False
            )
            if caller_family:
                action = row.get("action")
                delta_binding = row.get("caller_delta_binding")
                predecessor_binding = row.get("predecessor_binding")
                promoted_binding = row.get("actual_promotion_binding")
                dynamic_transition_valid = (
                    action
                    in {
                        "translation_override_pending",
                        "translation_override_and_verification_renewal",
                        "verification_renewal",
                        "translation_override_and_runtime_promotion",
                        "runtime_promotion",
                    }
                    and isinstance(delta_binding, dict)
                    and isinstance(delta_binding.get("root"), list)
                    and isinstance(
                        delta_binding.get("reachable_repaired_targets"),
                        list,
                    )
                    and all(
                        isinstance(delta_binding.get(field), str)
                        for field in (
                            "root_delta_proof_sha256",
                            "target_delta_manifest_sha256",
                            "pk_candidate_packed_sha256",
                            "assembly_hash_manifest_sha256",
                            "audit_report_file_sha256",
                            "audit_report_payload_sha256",
                        )
                    )
                    and isinstance(predecessor_binding, dict)
                    and isinstance(predecessor_binding.get("row_sha256"), str)
                    and (
                        (
                            action
                            in {
                                "runtime_promotion",
                                (
                                    "translation_override_and_runtime_"
                                    "promotion"
                                ),
                            }
                            and row.get("status") == "verified"
                            and isinstance(promoted_binding, dict)
                            and promoted_binding.get(
                                "manual_full_assembly_verified"
                            )
                            is True
                            and promoted_binding.get(
                                "hard_grammar_risk_absent"
                            )
                            is True
                            and promoted_binding.get(
                                "relative_full_closure_line_envelope_"
                                "nonexpanding"
                            )
                            is True
                        )
                        or (
                            action == "translation_override_pending"
                            and row.get("status") == "pending"
                            and promoted_binding is None
                        )
                        or (
                            action
                            in {
                                (
                                    "translation_override_and_verification_"
                                    "renewal"
                                ),
                                "verification_renewal",
                            }
                            and row.get("status") == "verified"
                            and promoted_binding is None
                            and row.get(
                                "preexisting_verified_evidence_renewed"
                            )
                            is True
                        )
                    )
                )
            elif thought_predicate_family:
                action = row.get("action")
                dynamic_transition_valid = (
                    action
                    in {
                        "runtime_promotion",
                        "translation_override_and_runtime_promotion",
                        (
                            "translation_override_and_verification_"
                            "renewal"
                        ),
                    }
                    and row.get("result") == "verified"
                    and isinstance(
                        row.get("predecessor_runtime_review"),
                        str,
                    )
                    and all(
                        isinstance(row.get(field), str)
                        for field in (
                            "candidate_record_raw_sha256",
                            "predecessor_record_raw_sha256",
                            "current_record_raw_sha256",
                            "predecessor_literal_utf16le_sha256",
                            "candidate_literal_utf16le_sha256",
                            "updated_translation_utf16le_sha256",
                            "coverage_report_file_sha256",
                            "coverage_report_payload_sha256",
                            "assembly_manifest_sha256",
                            "pk_candidate_packed_sha256",
                            "row_verification_sha256",
                        )
                    )
                    and all(
                        row.get(field) is True
                        for field in (
                            "full_incoming_closure_verified",
                            "grammar_complete_for_all_registers",
                            "actual_current_relative_nonexpanding",
                            "control_components_preserved",
                            "protected_signature_preserved",
                        )
                    )
                    and (
                        (
                            action
                            in {
                                "runtime_promotion",
                                (
                                    "translation_override_and_runtime_"
                                    "promotion"
                                ),
                            }
                            and row.get("predecessor_runtime_review")
                            == "pending"
                        )
                        or (
                            action
                            == (
                                "translation_override_and_verification_"
                                "renewal"
                            )
                            and row.get("predecessor_runtime_review")
                            == "verified"
                        )
                    )
                )
            elif terminal_family:
                action = row.get("action")
                delta_binding = row.get("terminal_family_delta_binding")
                predecessor_binding = row.get(
                    "predecessor_integrated_binding"
                )
                promoted_binding = row.get("actual_promotion_binding")
                dynamic_transition_valid = (
                    action
                    in {
                        "translation_override",
                        "verification_renewal",
                        "runtime_promotion",
                        "translation_override_and_runtime_promotion",
                        "translation_override_pending",
                    }
                    and isinstance(delta_binding, dict)
                    and isinstance(delta_binding.get("root"), list)
                    and isinstance(
                        delta_binding.get("reachable_repaired_targets"),
                        list,
                    )
                    and all(
                        isinstance(delta_binding.get(field), str)
                        for field in (
                            "root_delta_proof_sha256",
                            "target_delta_manifest_sha256",
                            "pk_candidate_packed_sha256",
                            "ghidra_vm_contract_file_sha256",
                            "ghidra_layout_contract_file_sha256",
                            "audit_report_file_sha256",
                            "audit_report_payload_sha256",
                        )
                    )
                    and isinstance(predecessor_binding, dict)
                    and all(
                        isinstance(predecessor_binding.get(field), str)
                        for field in (
                            "row_sha256",
                            "checkpoint_private_sha256",
                            "checkpoint_report_file_sha256",
                            "checkpoint_builder_sha256",
                        )
                    )
                    and (
                        (
                            action
                            in {
                                "runtime_promotion",
                                (
                                    "translation_override_and_runtime_"
                                    "promotion"
                                ),
                            }
                            and row.get("status") == "verified"
                            and isinstance(promoted_binding, dict)
                            and promoted_binding.get(
                                "manual_full_assembly_verified"
                            )
                            is True
                            and promoted_binding.get(
                                "hard_grammar_risk_absent"
                            )
                            is True
                            and promoted_binding.get(
                                "relative_full_closure_line_envelope_"
                                "nonexpanding"
                            )
                            is True
                        )
                        or (
                            action == "translation_override_pending"
                            and row.get("status") == "pending"
                            and promoted_binding is None
                        )
                        or (
                            action
                            in {
                                "translation_override",
                                "verification_renewal",
                            }
                            and row.get("status") == "verified"
                            and promoted_binding is None
                        )
                    )
                )
            elif dynamic_honorific:
                action = row.get("action")
                scope_transition = row.get("scope_transition")
                layout_transition = row.get("layout_transition")
                dynamic_transition_valid = (
                    action
                    in {
                        "translation_override",
                        "verification_renewal",
                        "runtime_promotion",
                    }
                    and isinstance(scope_transition, dict)
                    and isinstance(layout_transition, dict)
                    and (
                        (
                            action == "runtime_promotion"
                            and expected_resource == "pk_msggame"
                            and scope_transition
                            == {
                                "from": "runtime_fragment_pending",
                                "to": "retranslated",
                            }
                            and layout_transition.get("from")
                            in {
                                "runtime_pending",
                                "unchanged_from_current",
                            }
                            and layout_transition.get("to")
                            == "runtime_verified"
                        )
                        or (
                            action
                            in {
                                "translation_override",
                                "verification_renewal",
                            }
                            and scope_transition.get("from")
                            == scope_transition.get("to")
                            == "retranslated"
                            and layout_transition.get("from")
                            == layout_transition.get("to")
                        )
                    )
                )
            else:
                dynamic_transition_valid = (
                    row.get("scope_transition")
                    == {
                        "from": "runtime_fragment_pending",
                        "to": "retranslated",
                    }
                )
            if not base_row_valid or not dynamic_transition_valid:
                raise RetranslationError(
                    "PK runtime VM overlay evidence is incomplete: "
                    f"{coordinate}"
                )
            if (
                method
                in {
                    PK_RESIDUAL_RUNTIME_VM_VERIFICATION_METHOD,
                    PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_VERIFICATION_METHOD,
                }
                and (
                    not isinstance(row.get("layout_transition"), dict)
                    or row["layout_transition"].get("from")
                    not in {"runtime_pending", "unchanged_from_current"}
                    or row["layout_transition"].get("to")
                    != "runtime_verified"
                )
            ):
                raise RetranslationError(
                    "PK runtime VM overlay lacks its layout proof: "
                    f"{coordinate}"
                )
            if (
                method
                == PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_VERIFICATION_METHOD
            ):
                binding = row.get("cross_resource_closure_binding")
                layout_guard = (
                    binding.get("relative_layout_guard")
                    if isinstance(binding, dict)
                    else None
                )
                if (
                    not isinstance(layout_guard, dict)
                    or layout_guard.get("status") != "verified"
                    or layout_guard.get("reason_codes") != []
                    or layout_guard.get(
                        "relative_full_closure_line_envelope_nonexpanding"
                    )
                    is not True
                ):
                    raise RetranslationError(
                        "PK cross-resource runtime VM overlay lacks its "
                        f"raw-G1N full-closure width proof: {coordinate}"
                    )
            rows[key] = row
            source_count += 1
        if (
            not source_count
            or promotion.get("result", {}).get(
                (
                    "private_evidence_rows"
                    if evidence_family
                    else "private_overlay_rows"
                )
            )
            != source_count
        ):
            raise RetranslationError(
                f"tracked PK runtime VM promotion row count drifted: "
                f"{overlay_path}"
            )
    if not rows:
        raise RetranslationError(
            "no private PK runtime VM verification overlay is available"
        )
    return rows


def validate_pk_runtime_vm_verification(
    *,
    evidence: Mapping[str, Any],
    overlay_rows: Mapping[tuple[str, str], dict[str, Any]],
    coordinate_value: str,
    translation: str,
    layout_review: str,
    resource: str,
    scope_classification: str,
    label: str,
) -> None:
    evidence_schema = str(evidence.get("schema"))
    expected = overlay_rows.get((evidence_schema, coordinate_value))
    if expected is None:
        raise RetranslationError(
            f"{label}.runtime_vm_verification has no tracked PK overlay row"
        )
    method = evidence.get("method")
    combined_caller_overlap = (
        method == PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
        and (resource, coordinate_value)
        == CALLER_SUPERSEDED_THOUGHT_ACTION_COORDINATE
        and isinstance(evidence.get("combined_final_binding"), dict)
    )
    if combined_caller_overlap:
        combined_binding = evidence["combined_final_binding"]
        if (
            canonical_sha256(evidence)
            != CALLER_COMBINED_OVERLAP_EVIDENCE_SHA256
            or
            evidence.get("source_caller_evidence_sha256")
            != canonical_sha256(expected)
            or evidence.get("action") != "verification_renewal"
            or evidence.get("status") != "verified"
            or combined_binding.get("pk_candidate_packed_sha256")
            != CALLER_COMBINED_CANDIDATE_SHA256
            or combined_binding.get("candidate_record_raw_sha256")
            != CALLER_COMBINED_OVERLAP_RECORD_SHA256
            or combined_binding.get("root_delta_proof_sha256")
            != CALLER_COMBINED_OVERLAP_ROOT_PROOF_SHA256
            or combined_binding.get("target_delta_manifest_sha256")
            != CALLER_COMBINED_TARGET_DELTA_SHA256
            or combined_binding.get("assembly_hash_manifest_sha256")
            != CALLER_COMBINED_ASSEMBLY_MANIFEST_SHA256
            or combined_binding.get("renewal_payload_reference_sha256")
            != CALLER_COMBINED_RENEWAL_REFERENCE_SHA256
            or any(
                not isinstance(combined_binding.get(field), str)
                for field in (
                    "thought_predecessor_row_sha256",
                    "thought_predecessor_runtime_vm_verification_sha256",
                    "predecessor_record_raw_sha256",
                    "target_delta_manifest_sha256",
                    "assembly_hash_manifest_sha256",
                    "root_delta_proof_sha256",
                )
            )
            or combined_binding.get("thought_translation_preserved") is not True
            or combined_binding.get("control_signature_preserved") is not True
            or combined_binding.get("grammar_complete") is not True
        ):
            raise RetranslationError(
                f"{label}.runtime_vm_verification combined caller proof drifted"
            )
    elif dict(evidence) != expected:
        raise RetranslationError(
            f"{label}.runtime_vm_verification differs from the tracked PK overlay"
        )
    translation_hash_field = (
        "updated_translation_utf16le_sha256"
        if evidence.get("method")
        == PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
        else "translation_utf16le_sha256"
    )
    if evidence.get(translation_hash_field) != sha256_text(translation):
        raise RetranslationError(
            f"{label}.runtime_vm_verification translation hash does not match"
        )
    if method == PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD:
        action = evidence.get("action")
        delta_binding = evidence.get("caller_delta_binding")
        predecessor_binding = evidence.get("predecessor_binding")
        promoted_binding = evidence.get("actual_promotion_binding")
        if (
            resource != "pk_msggame"
            or evidence.get("resource") != resource
            or evidence.get("status") != "verified"
            or not isinstance(delta_binding, dict)
            or not isinstance(delta_binding.get("root"), list)
            or not isinstance(
                delta_binding.get("reachable_repaired_targets"),
                list,
            )
            or not isinstance(predecessor_binding, dict)
            or any(
                not isinstance(delta_binding.get(field), str)
                for field in (
                    "root_delta_proof_sha256",
                    "target_delta_manifest_sha256",
                    "pk_candidate_packed_sha256",
                    "assembly_hash_manifest_sha256",
                    "audit_report_file_sha256",
                    "audit_report_payload_sha256",
                )
            )
        ):
            raise RetranslationError(
                f"{label}.runtime_vm_verification caller binding is incomplete"
            )
        if action in {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }:
            if (
                scope_classification != "retranslated"
                or layout_review != "runtime_verified"
                or not isinstance(promoted_binding, dict)
                or promoted_binding.get("manual_full_assembly_verified")
                is not True
                or promoted_binding.get("hard_grammar_risk_absent") is not True
                or promoted_binding.get(
                    "relative_full_closure_line_envelope_nonexpanding"
                )
                is not True
            ):
                raise RetranslationError(
                    f"{label}.runtime_vm_verification caller promotion "
                    "proof is incomplete"
                )
        elif action in {
            "translation_override_and_verification_renewal",
            "verification_renewal",
        }:
            if (
                promoted_binding is not None
                or evidence.get("preexisting_verified_evidence_renewed")
                is not True
            ):
                raise RetranslationError(
                    f"{label}.runtime_vm_verification caller renewal "
                    "binding drifted"
                )
        else:
            raise RetranslationError(
                f"{label}.runtime_vm_verification has an invalid caller action"
            )
    elif method == PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD:
        action = evidence.get("action")
        promotion_actions = {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }
        if (
            resource != "pk_msggame"
            or evidence.get("resource") != resource
            or evidence.get("result") != "verified"
            or evidence.get("status") != "verified"
            or evidence.get("per_row_game_playback_required") is not False
            or any(
                not isinstance(evidence.get(field), str)
                for field in (
                    "candidate_record_raw_sha256",
                    "predecessor_record_raw_sha256",
                    "current_record_raw_sha256",
                    "predecessor_literal_utf16le_sha256",
                    "candidate_literal_utf16le_sha256",
                    "coverage_report_file_sha256",
                    "coverage_report_payload_sha256",
                    "assembly_manifest_sha256",
                    "pk_candidate_packed_sha256",
                    "row_verification_sha256",
                )
            )
            or any(
                evidence.get(field) is not True
                for field in (
                    "full_incoming_closure_verified",
                    "grammar_complete_for_all_registers",
                    "actual_current_relative_nonexpanding",
                    "control_components_preserved",
                    "protected_signature_preserved",
                )
            )
        ):
            raise RetranslationError(
                f"{label}.runtime_vm_verification thought-predicate proof "
                "is incomplete"
            )
        if action in promotion_actions:
            if (
                evidence.get("predecessor_runtime_review") != "pending"
                or scope_classification != "retranslated"
                or layout_review != "runtime_verified"
            ):
                raise RetranslationError(
                    f"{label}.runtime_vm_verification thought-predicate "
                    "promotion transition drifted"
                )
        elif action == "translation_override_and_verification_renewal":
            if evidence.get("predecessor_runtime_review") != "verified":
                raise RetranslationError(
                    f"{label}.runtime_vm_verification thought-predicate "
                    "renewal transition drifted"
                )
        else:
            raise RetranslationError(
                f"{label}.runtime_vm_verification has an invalid "
                "thought-predicate action"
            )
    elif method == PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD:
        action = evidence.get("action")
        delta_binding = evidence.get("terminal_family_delta_binding")
        predecessor_binding = evidence.get("predecessor_integrated_binding")
        promoted_binding = evidence.get("actual_promotion_binding")
        if (
            resource != "pk_msggame"
            or evidence.get("resource") != resource
            or evidence.get("status") != "verified"
            or not isinstance(delta_binding, dict)
            or not isinstance(delta_binding.get("root"), list)
            or not isinstance(
                delta_binding.get("reachable_repaired_targets"),
                list,
            )
            or not isinstance(predecessor_binding, dict)
            or any(
                not isinstance(delta_binding.get(field), str)
                for field in (
                    "root_delta_proof_sha256",
                    "target_delta_manifest_sha256",
                    "pk_candidate_packed_sha256",
                    "ghidra_vm_contract_file_sha256",
                    "ghidra_layout_contract_file_sha256",
                    "audit_report_file_sha256",
                    "audit_report_payload_sha256",
                )
            )
        ):
            raise RetranslationError(
                f"{label}.runtime_vm_verification terminal binding is incomplete"
            )
        if action in {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }:
            if (
                scope_classification != "retranslated"
                or layout_review != "runtime_verified"
                or not isinstance(promoted_binding, dict)
                or promoted_binding.get("manual_full_assembly_verified")
                is not True
                or promoted_binding.get("hard_grammar_risk_absent")
                is not True
                or promoted_binding.get(
                    "relative_full_closure_line_envelope_nonexpanding"
                )
                is not True
            ):
                raise RetranslationError(
                    f"{label}.runtime_vm_verification terminal promotion "
                    "proof is incomplete"
                )
        elif action in {"translation_override", "verification_renewal"}:
            if (
                promoted_binding is not None
                or evidence.get("preexisting_verified_evidence_renewed")
                is not True
            ):
                raise RetranslationError(
                    f"{label}.runtime_vm_verification terminal renewal "
                    "binding drifted"
                )
        else:
            raise RetranslationError(
                f"{label}.runtime_vm_verification has an invalid terminal action"
            )
    elif method in DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHODS:
        expected_method = (
            BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD
            if resource == "base_msggame"
            else PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD
        )
        action = evidence.get("action")
        scope_transition = evidence.get("scope_transition")
        layout_transition = evidence.get("layout_transition")
        delta_binding = evidence.get("honorific_spacing_delta_binding")
        predecessor_binding = evidence.get("predecessor_integrated_binding")
        promoted_binding = evidence.get("pk_promoted_root_binding")
        if (
            method != expected_method
            or evidence.get("resource") != resource
            or not isinstance(scope_transition, dict)
            or scope_transition.get("to") != scope_classification
            or not isinstance(layout_transition, dict)
            or layout_transition.get("to") != layout_review
            or not isinstance(delta_binding, dict)
            or not isinstance(delta_binding.get("root"), list)
            or not isinstance(
                delta_binding.get("reachable_repaired_targets"),
                list,
            )
            or any(
                not isinstance(delta_binding.get(field), str)
                for field in (
                    "root_delta_proof_sha256",
                    "target_delta_manifest_sha256",
                    "candidate_packed_sha256",
                    "ghidra_vm_contract_file_sha256",
                    "ghidra_layout_contract_file_sha256",
                    "audit_report_file_sha256",
                    "audit_report_payload_sha256",
                )
            )
            or not isinstance(predecessor_binding, dict)
            or any(
                not isinstance(predecessor_binding.get(field), str)
                for field in (
                    "row_sha256",
                    "private_integrated_decision_sha256",
                    "source_free_report_file_sha256",
                    "integrated_builder_sha256",
                )
            )
        ):
            raise RetranslationError(
                f"{label}.runtime_vm_verification honorific binding is incomplete"
            )
        if action == "runtime_promotion":
            if (
                resource != "pk_msggame"
                or scope_transition
                != {
                    "from": "runtime_fragment_pending",
                    "to": "retranslated",
                }
                or layout_transition.get("to") != "runtime_verified"
                or not isinstance(promoted_binding, dict)
                or promoted_binding.get("hard_grammar_risk_absent")
                is not True
                or promoted_binding.get(
                    "relative_full_closure_line_envelope_nonexpanding"
                )
                is not True
            ):
                raise RetranslationError(
                    f"{label}.runtime_vm_verification promotion proof is incomplete"
                )
        elif action in {"translation_override", "verification_renewal"}:
            if (
                scope_transition.get("from") != scope_transition.get("to")
                or layout_transition.get("from") != layout_transition.get("to")
                or promoted_binding is not None
            ):
                raise RetranslationError(
                    f"{label}.runtime_vm_verification renewal transition drifted"
                )
        else:
            raise RetranslationError(
                f"{label}.runtime_vm_verification has an invalid honorific action"
            )
    if (
        method == PK_ONLY_EXACT_BLOCKED_RUNTIME_VM_VERIFICATION_METHOD
        and evidence.get("layout_review_binding") != {"status": layout_review}
    ):
        raise RetranslationError(
            f"{label}.runtime_vm_verification layout binding does not match"
        )
    if (
        method == PK_CROSS_RESOURCE_EXACT_CLOSURE_RUNTIME_VM_VERIFICATION_METHOD
        and (
            not isinstance(evidence.get("layout_review_binding"), dict)
            or evidence.get("layout_transition")
            != {
                "from": evidence["layout_review_binding"].get("status"),
                "to": layout_review,
            }
            or layout_review != "runtime_verified"
            or not isinstance(
                evidence.get("cross_resource_closure_binding"), dict
            )
            or not isinstance(
                evidence["cross_resource_closure_binding"].get(
                    "relative_layout_guard"
                ),
                dict,
            )
            or evidence["cross_resource_closure_binding"][
                "relative_layout_guard"
            ].get("status")
            != "verified"
            or evidence["cross_resource_closure_binding"][
                "relative_layout_guard"
            ].get("reason_codes")
            != []
            or evidence["cross_resource_closure_binding"][
                "relative_layout_guard"
            ].get(
                "relative_full_closure_line_envelope_nonexpanding"
            )
            is not True
        )
    ):
        raise RetranslationError(
            f"{label}.runtime_vm_verification layout transition does not match"
        )


def validate_runtime_vm_verification(
    *,
    evidence: Mapping[str, Any],
    coverage: Mapping[str, Any],
    coverage_sha256: str,
    coordinate_value: str,
    record_coordinate_value: str,
    source_record_raw_sha256: str,
    current_ko_utf16le_sha256: str,
    translation: str,
    label: str,
) -> None:
    if evidence.get("schema") != RUNTIME_VM_ROW_VERIFICATION_SCHEMA:
        raise RetranslationError(
            f"{label}.runtime_vm_verification has an unexpected schema"
        )
    if evidence.get("method") != RUNTIME_VM_VERIFICATION_METHOD:
        raise RetranslationError(
            f"{label}.runtime_vm_verification has an unexpected method"
        )
    if evidence.get("result") != "verified":
        raise RetranslationError(
            f"{label}.runtime_vm_verification result is not verified"
        )
    if evidence.get("coverage_report_sha256") != coverage_sha256:
        raise RetranslationError(
            f"{label}.runtime_vm_verification coverage report hash does not match"
        )

    guards = coverage["guards"]
    assert isinstance(guards, dict)
    universe_digest = guards.get("pending_universe_digest_sha256")
    legacy_universe_digest = guards.get(
        "pending_coordinate_and_translation_digest_sha256"
    )
    if universe_digest is None:
        universe_digest = legacy_universe_digest
    elif (
        legacy_universe_digest is not None
        and legacy_universe_digest != universe_digest
    ):
        raise RetranslationError(
            "tracked runtime VM coverage report has conflicting universe digests"
        )
    if not isinstance(universe_digest, str):
        raise RetranslationError(
            "tracked runtime VM coverage report has no pending universe digest"
        )
    if evidence.get("pending_universe_digest_sha256") != universe_digest:
        raise RetranslationError(
            f"{label}.runtime_vm_verification pending universe digest does not match"
        )

    record_guards = guards["record_template_guards"]
    row_guards = guards["row_verification_guards"]
    assert isinstance(record_guards, dict)
    assert isinstance(row_guards, dict)
    record_guard = record_guards.get(record_coordinate_value)
    if not isinstance(record_guard, dict):
        raise RetranslationError(
            f"{label}.runtime_vm_verification has no audited record template guard"
        )
    record_template_sha256 = record_guard.get("template_sha256")
    candidate_record_raw_sha256 = record_guard.get(
        "candidate_record_raw_sha256"
    )
    if not isinstance(record_template_sha256, str) or not isinstance(
        candidate_record_raw_sha256, str
    ):
        raise RetranslationError(
            f"{label}.runtime_vm_verification record template guard is incomplete"
        )
    if evidence.get("record_template_sha256") != record_template_sha256:
        raise RetranslationError(
            f"{label}.runtime_vm_verification record template hash does not match"
        )
    if (
        evidence.get("candidate_record_raw_sha256")
        != candidate_record_raw_sha256
    ):
        raise RetranslationError(
            f"{label}.runtime_vm_verification candidate record hash does not match"
        )

    proof_payload = {
        "candidate_record_raw_sha256": candidate_record_raw_sha256,
        "coordinate": coordinate_value,
        "current_ko_utf16le_sha256": current_ko_utf16le_sha256,
        "record_template_sha256": record_template_sha256,
        "source_record_raw_sha256": source_record_raw_sha256,
        "translation_utf16le_sha256": sha256_text(translation),
    }
    computed_proof = sha256_bytes(canonical_ascii_json(proof_payload))
    tracked_proof = row_guards.get(coordinate_value)
    if not isinstance(tracked_proof, str):
        raise RetranslationError(
            f"{label}.runtime_vm_verification has no audited row guard"
        )
    if evidence.get("row_verification_sha256") != tracked_proof:
        raise RetranslationError(
            f"{label}.runtime_vm_verification row guard does not match"
        )
    if computed_proof != tracked_proof:
        raise RetranslationError(
            f"{label}.runtime_vm_verification row proof recomputation failed"
        )


def validate_translation_shape(
    current_text: str,
    translation: str,
    layout_review: object,
    label: str,
    *,
    allow_empty_runtime_morpheme: bool = False,
    allow_runtime_boundary_leading_space: bool = False,
    allow_runtime_assembly_boundary_reflow: bool = False,
) -> None:
    if allow_empty_runtime_morpheme and allow_runtime_boundary_leading_space:
        raise RetranslationError(
            f"{label} cannot combine empty-morpheme and boundary-space exceptions"
        )
    if not translation.strip() and not allow_empty_runtime_morpheme:
        raise RetranslationError(f"{label} replacement is blank")
    if allow_empty_runtime_morpheme and translation != "":
        raise RetranslationError(
            f"{label} empty runtime morpheme replacement must be exactly empty"
        )
    if allow_runtime_boundary_leading_space:
        shape_translation = translation[1:]
        if (
            not translation.startswith(" ")
            or translation.startswith("  ")
            or translation != " 공"
        ):
            raise RetranslationError(
                f"{label} runtime boundary repair must add exactly one ASCII "
                "space before 공"
            )
    else:
        shape_translation = translation
    current_signature = protected_signature(current_text)
    translation_signature = protected_signature(shape_translation)
    if allow_runtime_assembly_boundary_reflow:
        current_signature = {
            key: value
            for key, value in current_signature.items()
            if key not in {"leading_whitespace", "trailing_whitespace"}
        }
        translation_signature = {
            key: value
            for key, value in translation_signature.items()
            if key not in {"leading_whitespace", "trailing_whitespace"}
        }
    if translation_signature != current_signature:
        raise RetranslationError(f"{label} changes protected runtime tokens or outer whitespace")
    if KANA_OR_HAN_RE.search(translation):
        raise RetranslationError(f"{label} replacement retains kana or CJK Han text")
    if (
        translation.count("\n") != current_text.count("\n")
        and layout_review not in {"runtime_verified", "runtime_pending"}
    ):
        raise RetranslationError(
            f"{label} changes line count without runtime layout review"
        )
    if layout_review not in {
        "unchanged_from_current",
        "runtime_verified",
        "runtime_pending",
        "not_needed",
    }:
        raise RetranslationError(f"{label} has an invalid layout_review status")
    if layout_review == "not_needed" and current_text.count("\n"):
        raise RetranslationError(f"{label} has line breaks and cannot use not_needed layout review")


def validate_decisions(
    prepared: PreparedArtifacts,
    decision_path: Path,
    *,
    require_complete: bool = True,
) -> dict[tuple[str, int, int, int], str]:
    decisions = load_decisions(decision_path)
    expected_keys = set(prepared.visible_targets)
    replacements: dict[tuple[str, int, int, int], str] = {}
    current_records_by_resource = {
        name: archive_records(resource.current_archive)
        for name, resource in prepared.resources.items()
    }
    pristine_records_by_resource = {
        name: archive_records(resource.pristine_archive)
        for name, resource in prepared.resources.items()
    }
    runtime_vm_coverage: tuple[dict[str, Any], str] | None = None
    pk_runtime_vm_overlays: dict[
        tuple[str, str],
        dict[str, Any],
    ] | None = None
    runtime_vm_verified_record_hashes: dict[tuple[int, int], str] = {}
    for ordinal, row in enumerate(decisions, start=1):
        label = f"decision[{ordinal}]"
        if row.get("schema") != DECISION_SCHEMA:
            raise RetranslationError(f"{label}.schema must be {DECISION_SCHEMA}")
        resource = row.get("resource")
        if resource not in prepared.resources:
            raise RetranslationError(f"{label}.resource is not in scope")
        block_id, record_id, literal_id = parse_coordinate(row.get("coordinate"), f"{label}.coordinate")
        key = (str(resource), block_id, record_id, literal_id)
        if key not in expected_keys:
            raise RetranslationError(f"{label} is not a visible current target: {key}")
        if key in replacements:
            raise RetranslationError(f"duplicate decision coordinate: {key}")
        target = prepared.visible_targets[key]
        if row.get("source_record_raw_sha256") != target["source_record_raw_sha256"]:
            raise RetranslationError(f"{label} pristine source record guard does not match")
        if row.get("current_ko_utf16le_sha256") != target["current_ko_utf16le_sha256"]:
            raise RetranslationError(f"{label} current Korean target guard does not match")
        if row.get("semantic_review") != "approved":
            raise RetranslationError(f"{label} is not semantically approved")
        scope_classification = row.get("scope_classification")
        if scope_classification not in SCOPE_CLASSIFICATIONS:
            raise RetranslationError(f"{label} has an invalid scope_classification")
        runtime_review = row.get("runtime_review")
        if runtime_review not in {"not_required", "pending", "verified"}:
            raise RetranslationError(f"{label} has an invalid runtime_review status")
        if scope_classification == "runtime_fragment_pending" and runtime_review != "pending":
            raise RetranslationError(f"{label} runtime_fragment_pending must have runtime_review=pending")
        if scope_classification == "retranslated" and runtime_review == "pending":
            raise RetranslationError(f"{label} retranslated cannot still have runtime_review=pending")
        if scope_classification == "confirmed_non_display" and runtime_review != "not_required":
            raise RetranslationError(f"{label} confirmed_non_display must have runtime_review=not_required")
        if row.get("layout_review") == "runtime_pending" and runtime_review != "pending":
            raise RetranslationError(
                f"{label} layout_review=runtime_pending requires runtime_review=pending"
            )
        if (
            "source_outer_whitespace_restored" in row
            and row.get("source_outer_whitespace_restored") is not True
        ):
            raise RetranslationError(
                f"{label}.source_outer_whitespace_restored must be true when present"
            )
        source_outer_whitespace_restored = (
            row.get("source_outer_whitespace_restored") is True
        )
        runtime_vm_evidence = row.get("runtime_vm_verification")
        if runtime_vm_evidence is not None and not isinstance(
            runtime_vm_evidence, dict
        ):
            raise RetranslationError(
                f"{label}.runtime_vm_verification must be an object when present"
            )
        runtime_vm_method = (
            runtime_vm_evidence.get("method")
            if isinstance(runtime_vm_evidence, dict)
            else None
        )
        terminal_pending_evidence = row.get(
            "terminal_family_runtime_evidence"
        )
        if terminal_pending_evidence is not None:
            if (
                resource != "pk_msggame"
                or runtime_review != "pending"
                or runtime_vm_evidence is not None
                or not isinstance(terminal_pending_evidence, dict)
                or terminal_pending_evidence.get("schema")
                != PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_EVIDENCE_ROW_SCHEMA
                or terminal_pending_evidence.get("method")
                != PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                or terminal_pending_evidence.get("status") != "pending"
                or terminal_pending_evidence.get("action")
                != "translation_override_pending"
                or terminal_pending_evidence.get("coordinate")
                != f"{block_id}:{record_id}:{literal_id}"
                or terminal_pending_evidence.get(
                    "translation_utf16le_sha256"
                )
                != sha256_text(str(row.get("translation")))
            ):
                raise RetranslationError(
                    f"{label}.terminal_family_runtime_evidence is invalid"
                )
            if pk_runtime_vm_overlays is None:
                pk_runtime_vm_overlays = load_pk_runtime_vm_overlays()
            expected_terminal_pending = pk_runtime_vm_overlays.get(
                (
                    PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_EVIDENCE_ROW_SCHEMA,
                    f"{block_id}:{record_id}:{literal_id}",
                )
            )
            if (
                expected_terminal_pending is None
                or dict(terminal_pending_evidence)
                != expected_terminal_pending
            ):
                raise RetranslationError(
                    f"{label}.terminal_family_runtime_evidence differs "
                    "from the tracked overlay"
                )
        caller_pending_evidence = row.get(
            "bound_terminal_caller_runtime_evidence"
        )
        if caller_pending_evidence is not None:
            if (
                resource != "pk_msggame"
                or runtime_review != "pending"
                or runtime_vm_evidence is not None
                or not isinstance(caller_pending_evidence, dict)
                or caller_pending_evidence.get("schema")
                != PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_EVIDENCE_ROW_SCHEMA
                or caller_pending_evidence.get("method")
                != PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                or caller_pending_evidence.get("status") != "pending"
                or caller_pending_evidence.get("action")
                != "translation_override_pending"
                or caller_pending_evidence.get("coordinate")
                != f"{block_id}:{record_id}:{literal_id}"
                or caller_pending_evidence.get(
                    "translation_utf16le_sha256"
                )
                != sha256_text(str(row.get("translation")))
            ):
                raise RetranslationError(
                    f"{label}.bound_terminal_caller_runtime_evidence is invalid"
                )
            if pk_runtime_vm_overlays is None:
                pk_runtime_vm_overlays = load_pk_runtime_vm_overlays()
            expected_caller_pending = pk_runtime_vm_overlays.get(
                (
                    PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_EVIDENCE_ROW_SCHEMA,
                    f"{block_id}:{record_id}:{literal_id}",
                )
            )
            if (
                expected_caller_pending is None
                or dict(caller_pending_evidence)
                != expected_caller_pending
            ):
                raise RetranslationError(
                    f"{label}.bound_terminal_caller_runtime_evidence differs "
                    "from the tracked overlay"
                )
        terminal_action = row.get("terminal_family_update_action")
        if terminal_action is not None:
            bound_evidence = (
                runtime_vm_evidence
                if runtime_vm_method
                == PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                else terminal_pending_evidence
            )
            superseded_terminal_renewal = (
                runtime_vm_method
                == PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                and (
                    str(resource),
                    f"{block_id}:{record_id}:{literal_id}",
                )
                in THOUGHT_PREDICATE_SUPERSEDED_TERMINAL_ACTION_COORDINATES
                and terminal_action == "verification_renewal"
                and isinstance(runtime_vm_evidence, dict)
                and runtime_vm_evidence.get("action")
                == "translation_override_and_verification_renewal"
                and runtime_vm_evidence.get("predecessor_runtime_review")
                == "verified"
            )
            caller_superseded_terminal_renewal = (
                runtime_vm_method
                == PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                and (
                    str(resource),
                    f"{block_id}:{record_id}:{literal_id}",
                )
                in CALLER_SUPERSEDED_TERMINAL_ACTION_COORDINATES
                and terminal_action == "verification_renewal"
                and isinstance(runtime_vm_evidence, dict)
                and runtime_vm_evidence.get("action")
                in {
                    "verification_renewal",
                    "translation_override_and_verification_renewal",
                }
            )
            if (
                not isinstance(bound_evidence, dict)
                or terminal_action != bound_evidence.get("action")
            ) and not (
                superseded_terminal_renewal
                or caller_superseded_terminal_renewal
            ):
                raise RetranslationError(
                    f"{label}.terminal_family_update_action is unbound"
                )
        thought_predicate_action = row.get(
            "thought_predicate_family_update_action"
        )
        if (
            thought_predicate_action is not None
            or runtime_vm_method
            == PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
        ):
            caller_superseded_thought = (
                runtime_vm_method
                == PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                and (
                    str(resource),
                    f"{block_id}:{record_id}:{literal_id}",
                )
                == CALLER_SUPERSEDED_THOUGHT_ACTION_COORDINATE
                and thought_predicate_action
                == "translation_override_and_verification_renewal"
                and isinstance(runtime_vm_evidence, dict)
                and runtime_vm_evidence.get("action")
                == "verification_renewal"
            )
            if (
                runtime_vm_method
                != PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                or not isinstance(runtime_vm_evidence, dict)
                or thought_predicate_action
                != runtime_vm_evidence.get("action")
            ) and not caller_superseded_thought:
                raise RetranslationError(
                    f"{label}.thought_predicate_family_update_action is "
                    "unbound"
                )
        caller_action = row.get("bound_terminal_caller_update_action")
        if (
            caller_action is not None
            or runtime_vm_method
            == PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
            or caller_pending_evidence is not None
        ):
            caller_evidence = (
                runtime_vm_evidence
                if runtime_vm_method
                == PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                else caller_pending_evidence
            )
            if (
                not isinstance(caller_evidence, dict)
                or caller_action != caller_evidence.get("action")
            ):
                raise RetranslationError(
                    f"{label}.bound_terminal_caller_update_action is unbound"
                )
        if (
            "runtime_boundary_leading_space_inserted" in row
            and row.get("runtime_boundary_leading_space_inserted") is not True
        ):
            raise RetranslationError(
                f"{label}.runtime_boundary_leading_space_inserted must be true "
                "when present"
            )
        runtime_boundary_leading_space_inserted = (
            row.get("runtime_boundary_leading_space_inserted") is True
        )
        expected_honorific_method = (
            BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD
            if resource == "base_msggame"
            else PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD
        )
        if runtime_boundary_leading_space_inserted and (
            (str(resource), f"{block_id}:{record_id}:{literal_id}")
            not in RUNTIME_BOUNDARY_LEADING_SPACE_COORDINATES
            or runtime_vm_method != expected_honorific_method
        ):
            raise RetranslationError(
                f"{label} has an unauthorized runtime-boundary leading space"
            )
        if runtime_vm_evidence is not None and (
            runtime_vm_method not in PK_RUNTIME_VM_VERIFICATION_METHODS
        ):
            raise RetranslationError(
                f"{label}.runtime_vm_verification has an unsupported method"
            )
        if (
            runtime_vm_method in PK_RUNTIME_VM_VERIFICATION_METHODS
            and runtime_review != "verified"
        ):
            raise RetranslationError(
                f"{label} reversed VM evidence requires runtime_review=verified"
            )
        if (
            resource == "pk_msggame"
            and runtime_review == "verified"
            and runtime_vm_method not in PK_RUNTIME_VM_VERIFICATION_METHODS
        ):
            raise RetranslationError(
                f"{label} verified PK runtime row requires reversed VM evidence"
            )
        if "empty_runtime_morpheme" in row and row.get("empty_runtime_morpheme") is not True:
            raise RetranslationError(
                f"{label}.empty_runtime_morpheme must be true when present"
            )
        empty_runtime_morpheme = row.get("empty_runtime_morpheme") is True
        if "empty_runtime_morpheme_kind" in row and not empty_runtime_morpheme:
            raise RetranslationError(
                f"{label}.empty_runtime_morpheme_kind requires empty_runtime_morpheme=true"
            )
        if empty_runtime_morpheme:
            if scope_classification not in {"runtime_fragment_pending", "retranslated"}:
                raise RetranslationError(
                    f"{label} empty_runtime_morpheme requires runtime_fragment_pending "
                    "or a runtime-verified retranslated decision"
                )
            if (
                scope_classification == "retranslated"
                and runtime_review != "verified"
            ):
                raise RetranslationError(
                    f"{label} retranslated empty_runtime_morpheme requires "
                    "runtime_review=verified"
                )
            morpheme_kind = row.get("empty_runtime_morpheme_kind")
            allowed_sources = (
                EMPTY_RUNTIME_MORPHEME_SOURCE_BY_KIND.get(morpheme_kind)
                if isinstance(morpheme_kind, str)
                else None
            )
            if allowed_sources is None:
                raise RetranslationError(
                    f"{label} has an invalid empty_runtime_morpheme_kind"
                )
            pristine_records = pristine_records_by_resource[str(resource)]
            source_text = parse_record_literals(
                pristine_records[(block_id, record_id)]
            )[literal_id].text
            if source_text not in allowed_sources:
                raise RetranslationError(
                    f"{label} pristine source is not valid for "
                    f"empty_runtime_morpheme_kind={morpheme_kind}"
                )
            assembly_evidence = row.get("runtime_assembly_evidence")
            if not isinstance(assembly_evidence, dict):
                raise RetranslationError(
                    f"{label} empty_runtime_morpheme requires "
                    "runtime_assembly_evidence"
                )
            if (
                assembly_evidence.get("empty_runtime_morpheme_source_jp")
                != source_text
                or assembly_evidence.get("korean_zero_morpheme_caller_review")
                != "approved"
                or assembly_evidence.get("runtime_integration_required") is not True
                or assembly_evidence.get("automatic_space_inserted") is not False
            ):
                raise RetranslationError(
                    f"{label} empty runtime morpheme evidence is incomplete"
                )
        if require_complete and runtime_review == "pending":
            raise RetranslationError(f"{label} still requires runtime context review")
        records = current_records_by_resource[str(resource)]
        current_record = records[(block_id, record_id)]
        current_text = parse_record_literals(current_record)[literal_id].text
        if scope_classification == "confirmed_non_display":
            if row.get("translation") is not None:
                raise RetranslationError(f"{label} confirmed_non_display must not carry a translation")
            translation = current_text
        else:
            translation = row.get("translation")
            if not isinstance(translation, str):
                raise RetranslationError(f"{label}.translation must be a string")
            shape_baseline = current_text
            if source_outer_whitespace_restored:
                pristine_record = pristine_records_by_resource[
                    str(resource)
                ][(block_id, record_id)]
                source_text = parse_record_literals(pristine_record)[
                    literal_id
                ].text
                assembly_evidence = row.get("runtime_assembly_evidence")
                source_calls = direct_call_operands(pristine_record)
                current_calls = direct_call_operands(current_record)
                missing_current_calls = tuple(
                    call
                    for call in source_calls
                    if call not in current_calls
                )
                if (
                    resource != "pk_msggame"
                    or (block_id, record_id, literal_id)
                    != (6, 3887, 0)
                    or scope_classification
                    != "runtime_fragment_pending"
                    or runtime_review != "pending"
                    or row.get("layout_review") != "runtime_pending"
                    or record_gap_bytes(pristine_record)
                    == record_gap_bytes(current_record)
                    or not source_calls
                    or current_calls
                    or missing_current_calls != source_calls
                    or not isinstance(assembly_evidence, dict)
                    or assembly_evidence.get(
                        "current_runtime_gap_anomaly"
                    )
                    is not True
                    or assembly_evidence.get(
                        "source_runtime_gap_repair_required"
                    )
                    is not True
                    or assembly_evidence.get(
                        "source_runtime_gap_repair_integrated_for_evidence_only"
                    )
                    is not True
                    or assembly_evidence.get(
                        "source_outer_whitespace_restored"
                    )
                    is not True
                    or assembly_evidence.get(
                        "runtime_promotion_authorized"
                    )
                    is not False
                    or assembly_evidence.get(
                        "missing_current_call_operands"
                    )
                    not in (source_calls, list(source_calls))
                    or assembly_evidence.get(
                        "source_runtime_gap_repair_evidence_schema"
                    )
                    != SOURCE_OUTER_WHITESPACE_REPAIR_EVIDENCE_SCHEMA
                    or assembly_evidence.get(
                        "source_runtime_gap_repair_builder"
                    )
                    != "build_pk_runtime_gap_repair_3887.py"
                    or assembly_evidence.get(
                        "source_runtime_gap_repair_record_coordinate"
                    )
                    != f"{block_id}:{record_id}"
                    or assembly_evidence.get(
                        "source_runtime_gap_repair_source_record_sha256"
                    )
                    != sha256_bytes(pristine_record.data)
                    or assembly_evidence.get(
                        "source_runtime_gap_repair_current_record_sha256"
                    )
                    != sha256_bytes(current_record.data)
                    or assembly_evidence.get(
                        "source_runtime_gap_repair_candidate_record_sha256"
                    )
                    != SOURCE_OUTER_WHITESPACE_REPAIR_CANDIDATE_RECORD_SHA256
                    or protected_signature(source_text)
                    == protected_signature(current_text)
                    or protected_signature(translation)
                    != protected_signature(source_text)
                ):
                    raise RetranslationError(
                        f"{label} has invalid source outer-whitespace "
                        "restoration evidence"
                    )
                shape_baseline = source_text
            validate_translation_shape(
                shape_baseline,
                translation,
                row.get("layout_review"),
                label,
                allow_empty_runtime_morpheme=empty_runtime_morpheme,
                allow_runtime_boundary_leading_space=(
                    runtime_boundary_leading_space_inserted
                ),
                allow_runtime_assembly_boundary_reflow=(
                    (
                        str(resource),
                        f"{block_id}:{record_id}:{literal_id}",
                    )
                    in CALLER_RUNTIME_ASSEMBLY_BOUNDARY_REFLOW_COORDINATES
                    and caller_action == "translation_override_pending"
                    and isinstance(caller_pending_evidence, dict)
                    and caller_pending_evidence.get("method")
                    == PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                    and row.get("bound_terminal_caller_override_evidence", {}).get(
                        "control_bytes_preserved"
                    )
                    is True
                    and row.get("runtime_assembly_evidence", {}).get(
                        "protected_outer_whitespace_preserved"
                    )
                    is True
                ),
            )
        audited_base_coordinate = False
        if resource == "base_msggame" and runtime_review == "verified":
            if runtime_vm_coverage is None:
                runtime_vm_coverage = load_runtime_vm_coverage()
            audited_base_coordinate = (
                f"{block_id}:{record_id}:{literal_id}"
                in runtime_vm_coverage[0]["guards"]["row_verification_guards"]
            )
            if (
                audited_base_coordinate
                and runtime_vm_method
                not in {
                    RUNTIME_VM_VERIFICATION_METHOD,
                    BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
                }
            ):
                raise RetranslationError(
                    f"{label} is in the reversed-VM audited Base universe and "
                    "requires its bound row evidence"
                )
        runtime_vm_bound = False
        if (
            runtime_review == "verified"
            and runtime_vm_method in PK_RUNTIME_VM_VERIFICATION_METHODS
        ):
            assert isinstance(runtime_vm_evidence, dict)
            if resource == "base_msggame":
                if runtime_vm_method == RUNTIME_VM_VERIFICATION_METHOD:
                    if runtime_vm_coverage is None:
                        runtime_vm_coverage = load_runtime_vm_coverage()
                    coverage, coverage_sha256 = runtime_vm_coverage
                    validate_runtime_vm_verification(
                        evidence=runtime_vm_evidence,
                        coverage=coverage,
                        coverage_sha256=coverage_sha256,
                        coordinate_value=f"{block_id}:{record_id}:{literal_id}",
                        record_coordinate_value=f"{block_id}:{record_id}",
                        source_record_raw_sha256=str(
                            target["source_record_raw_sha256"]
                        ),
                        current_ko_utf16le_sha256=str(
                            target["current_ko_utf16le_sha256"]
                        ),
                        translation=translation,
                        label=label,
                    )
                    record_key = (block_id, record_id)
                    candidate_record_hash = str(
                        runtime_vm_evidence["candidate_record_raw_sha256"]
                    )
                    previous_hash = runtime_vm_verified_record_hashes.setdefault(
                        record_key,
                        candidate_record_hash,
                    )
                    if previous_hash != candidate_record_hash:
                        raise RetranslationError(
                            f"{label} conflicts with another row's candidate "
                            "record hash"
                        )
                elif (
                    runtime_vm_method
                    == BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD
                ):
                    if pk_runtime_vm_overlays is None:
                        pk_runtime_vm_overlays = load_pk_runtime_vm_overlays()
                    validate_pk_runtime_vm_verification(
                        evidence=runtime_vm_evidence,
                        overlay_rows=pk_runtime_vm_overlays,
                        coordinate_value=(
                            f"{block_id}:{record_id}:{literal_id}"
                        ),
                        translation=translation,
                        layout_review=str(row.get("layout_review")),
                        resource=str(resource),
                        scope_classification=str(scope_classification),
                        label=label,
                    )
                else:
                    raise RetranslationError(
                        f"{label} Base reversed VM evidence uses the wrong method"
                    )
            elif resource == "pk_msggame":
                if pk_runtime_vm_overlays is None:
                    pk_runtime_vm_overlays = load_pk_runtime_vm_overlays()
                validate_pk_runtime_vm_verification(
                    evidence=runtime_vm_evidence,
                    overlay_rows=pk_runtime_vm_overlays,
                    coordinate_value=f"{block_id}:{record_id}:{literal_id}",
                    translation=translation,
                    layout_review=str(row.get("layout_review")),
                    resource=str(resource),
                    scope_classification=str(scope_classification),
                    label=label,
                )
            else:
                raise RetranslationError(
                    f"{label} reversed VM evidence has an unsupported resource"
                )
            runtime_vm_bound = True
        if (
            empty_runtime_morpheme
            and scope_classification == "retranslated"
            and not runtime_vm_bound
        ):
            raise RetranslationError(
                f"{label} retranslated empty_runtime_morpheme requires "
                "evidence bound to the tracked reversed VM coverage"
            )
        replacements[key] = translation
    if runtime_vm_verified_record_hashes:
        expected_base_keys = {
            key
            for key in expected_keys
            if key[0] == "base_msggame"
        }
        actual_base_keys = {
            key
            for key in replacements
            if key[0] == "base_msggame"
        }
        if actual_base_keys != expected_base_keys:
            raise RetranslationError(
                "runtime-verified Base decisions require the complete Base decision universe"
            )
        base_replacements = {
            (block_id, record_id, literal_id): translation
            for (resource_name, block_id, record_id, literal_id), translation
            in replacements.items()
            if resource_name == "base_msggame"
        }
        candidate_blob = rebuild_packed_with_literals(
            prepared.resources["base_msggame"].current_blob,
            base_replacements,
        )
        candidate_records = archive_records(
            parse_packed_msggame(candidate_blob).archive
        )
        for record_key, expected_hash in sorted(
            runtime_vm_verified_record_hashes.items()
        ):
            actual_hash = sha256_bytes(candidate_records[record_key].data)
            if actual_hash != expected_hash:
                raise RetranslationError(
                    "assembled Base candidate record differs from its audited "
                    f"runtime VM guard: {record_key[0]}:{record_key[1]}"
                )
    missing = expected_keys.difference(replacements)
    extra = set(replacements).difference(expected_keys)
    if extra or (require_complete and missing):
        raise RetranslationError(
            f"decision set must cover every visible target exactly once; missing={len(missing)}, extra={len(extra)}"
        )
    return replacements


def build_candidate(output_root: Path, prepared: PreparedArtifacts, decision_path: Path) -> None:
    replacements = validate_decisions(prepared, decision_path)
    candidate_root = output_root / "candidate"
    manifest_resources: list[dict[str, Any]] = []
    for resource_name, resource in prepared.resources.items():
        literal_replacements = {
            (block_id, record_id, literal_id): text
            for (name, block_id, record_id, literal_id), text in replacements.items()
            if name == resource_name
        }
        rebuilt = rebuild_packed_with_literals(resource.current_blob, literal_replacements)
        rebuilt_archive = parse_packed_msggame(rebuilt).archive
        rebuilt_records = archive_records(rebuilt_archive)
        for (block_id, record_id, literal_id), text in literal_replacements.items():
            actual = parse_record_literals(rebuilt_records[(block_id, record_id)])[literal_id].text
            if actual != text:
                raise RetranslationError(f"candidate literal did not round-trip: {resource_name}:{block_id}:{record_id}:{literal_id}")
        output_path = candidate_root / resource.spec.relative_path
        atomic_write(output_path, rebuilt)
        manifest_resources.append(
            {
                "resource": resource_name,
                "relative_path": str(resource.spec.relative_path).replace("\\", "/"),
                "input_current_ko_sha256": resource.file_hashes["current_ko"],
                "output_candidate_sha256": sha256_bytes(rebuilt),
                "visible_replacement_count": len(literal_replacements),
            }
        )
    decision_digest = sha256_bytes(decision_path.read_bytes())
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "release_target": "0.15.0",
        "steam_write_performed": False,
        "candidate_deployed_to_steam": False,
        "semantic_completion": True,
        "validated_visible_current_literal_count": len(replacements),
        "private_decision_file_sha256": decision_digest,
        "resources": manifest_resources,
    }
    atomic_write(candidate_root / "candidate_manifest.source_free.v1.json", canonical_json(manifest))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--base-pristine", type=Path, default=DEFAULT_BASE_PRISTINE)
    parser.add_argument("--pk-pristine", type=Path, default=DEFAULT_PK_PRISTINE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--write", action="store_true", help="write deterministic queue and source-free ledgers below tmp")
    parser.add_argument("--validate", action="store_true", help="require written queue and ledgers to be byte-identical")
    parser.add_argument("--validate-decisions", action="store_true", help="require a complete approved private decision set")
    parser.add_argument(
        "--validate-partial-decisions",
        action="store_true",
        help="validate submitted decisions without requiring the full target universe",
    )
    parser.add_argument("--build-candidate", action="store_true", help="build a complete isolated candidate below tmp")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not any(
        (
            args.write,
            args.validate,
            args.validate_decisions,
            args.validate_partial_decisions,
            args.build_candidate,
        )
    ):
        raise RetranslationError("choose at least one action")
    output_root = safe_output_root(args.output_root)
    prepared = prepare_artifacts(args.steam_root, args.base_pristine, args.pk_pristine)
    paths = artifact_paths(output_root)
    if args.write:
        write_prepared(output_root, prepared)
    if args.validate:
        validate_written(output_root, prepared)
    if args.validate_partial_decisions:
        decision_path = args.decisions or paths["decisions"]
        validate_decisions(prepared, decision_path, require_complete=False)
    if args.validate_decisions or args.build_candidate:
        decision_path = args.decisions or paths["decisions"]
        validate_decisions(prepared, decision_path, require_complete=True)
    if args.build_candidate:
        build_candidate(output_root, prepared, args.decisions or paths["decisions"])
    summary = json.loads(prepared.summary)
    print(
        json.dumps(
            {
                "status": "ok",
                "total_current_literal_count": summary["total_current_literal_count"],
                "total_visible_current_literal_count": summary["total_visible_current_literal_count"],
                "batch_count": summary["batch_count"],
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RetranslationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
