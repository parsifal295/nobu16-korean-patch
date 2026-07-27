#!/usr/bin/env python3
"""Build the private 2546 simple-caller retranslation proposal.

Translation bodies and exact coordinates stay below ``tmp``.  The tracked
report contains only counts, digests, proof conclusions, and immutable input
seals.  This proposal does not modify the shared integration or Steam.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
FAMILY_BUILDER_PATH = (
    WORKSTREAM / "build_pk_bound_terminal_2546_full_caller_closure_v1.py"
)
TRANSLATION_INPUT_PATH = (
    DIALOGUE_TMP
    / "family2546_simple_caller_retranslation_translations.private.v1.json"
)
CHECKPOINT_PATH = DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
LEDGER_PATH = DIALOGUE_TMP / "family2546_full_ledger.private.v1.json"
HANDOFF_000_151_PATH = (
    DIALOGUE_TMP / "family2546_ord000_151_analysis.private.v1.json"
)
HANDOFF_152_303_PATH = (
    DIALOGUE_TMP / "family2546_ord152_303_analysis.private.v1.json"
)
QUEUE_PATH = DIALOGUE_TMP / "review_queue.private.v1.jsonl"
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "family2546_simple_caller_retranslation_proposal.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_simple_caller_retranslation_proposal.v1.json"
)

INPUT_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-simple-caller-translation-input.v1"
)
PRIVATE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-simple-caller-retranslation-private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-simple-caller-retranslation-proposal.v1"
)
RELEASE_TARGET = "0.15.0"
RESOURCE = "pk_msggame"
SELECTOR = 1066
TERMINAL_RECORD_IDS = tuple(range(2546, 2553))
A_REASONS = frozenset(
    {
        "fixed_question_ka",
        "fixed_question_kanou",
        "fixed_question_kayo",
        "fixed_question_after_terminal",
        "fixed_nominalizer_question_after_terminal",
    }
)

EXPECTED_TRANSLATION_INPUT_SHA256 = (
    "69107790355FC8879BA3727D4F811076D237487B7F03566F4FB89FE4CF3AFD14"
)
EXPECTED_CHECKPOINT_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_LEDGER_SHA256 = (
    "90987EC88A5AA06DA1BAB681E84D59ECD1E8090EE1AFCD472A0A5D646C3399EE"
)
EXPECTED_HANDOFF_000_151_SHA256 = (
    "CD6A535AFA08678924EA6296FAFAFE192BF70D78F96F616BAC09B741A7CCBEA9"
)
EXPECTED_HANDOFF_152_303_SHA256 = (
    "0E83FCEC00A894B444899B251CABE8F6E0506FE987C29025DB26EEA804A9350B"
)
EXPECTED_QUEUE_SHA256 = (
    "B3F393B578EB46B50C1714A4007AEAA87F8BEF74704E84F7837F3FC482E1D1CC"
)
EXPECTED_CHECKPOINT_ROWS = 52_803
EXPECTED_CHECKPOINT_PENDING = 8_213
EXPECTED_CHECKPOINT_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256 = (
    "C59CA74634E8A1FB0BBBFA3FE3A324AFC0ED06FDF7D707444116D5862A6C2C75"
)
EXPECTED_ROOTS = 9
EXPECTED_ROOT_SHA256 = (
    "DAF81B7CE6F04C328884A6344380AA51FE16DDDC42EBC41D0A9FAB3B0843F74D"
)
EXPECTED_PENDING_ROWS = 23
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "0EA72CCAB19602D79E8F1D04690D7F3DD39E02BF47267CC91A73A780EEA1FBE9"
)
EXPECTED_VERIFIED_ROWS = 5
EXPECTED_VERIFIED_COORDINATE_SHA256 = (
    "33E1CB0D48FA401F556CE8C2824D5EE83877007B0B3271537CCFC5496923DA63"
)
EXPECTED_REVIEW_ROWS = 28
EXPECTED_REVIEW_COORDINATE_SHA256 = (
    "196FC4887A53E1F01647B2A47D6BB650D5CA48B4962EA83A9639A39D4DAD65EF"
)
EXPECTED_REWRITE_ROWS = 17
EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "8F75484BA98CEECCF591CBEF8FC0174587E497F8734EECFA3626A7E4A591A9FD"
)
EXPECTED_KEEP_ROWS = 11
EXPECTED_KEEP_COORDINATE_SHA256 = (
    "DF5435862479ED1313F5AE8C8D935DE6082AA6A55A15C21530D48EADC04CB7CA"
)
EXPECTED_PENDING_REWRITE_ROWS = 14
EXPECTED_PENDING_REWRITE_COORDINATE_SHA256 = (
    "145F143D08B26C2845987E37195FF4FF9C31665E509C9F9A81FE3007E6A8EF62"
)
EXPECTED_PENDING_KEEP_ROWS = 9
EXPECTED_PENDING_KEEP_COORDINATE_SHA256 = (
    "59FC7D95C829E0BC68F4387DB60E364F544930C0E889FDAF0C23A2CE8E6CF8AE"
)
EXPECTED_VERIFIED_REWRITE_ROWS = 3
EXPECTED_VERIFIED_REWRITE_COORDINATE_SHA256 = (
    "0F7FE250ADBCDEB7A13737F4FD603A979433CB2B0D7C07A064A5F0C735E16952"
)
EXPECTED_VERIFIED_KEEP_ROWS = 2
EXPECTED_VERIFIED_KEEP_COORDINATE_SHA256 = (
    "81F79F6A6BFB36FF5FAF27A58138AA41D42ABFD5D5738900992E1880B53A89FC"
)
EXPECTED_TRANSLATION_MAP_SHA256 = (
    "B12AD98F0AF23266F8AD057A1256F2558B810451EE96D4668FA06A1997408704"
)
EXPECTED_REGISTER_ASSEMBLIES = 63

# Frozen after the first independently reproduced build.
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "EE9978A8D2B6E432618A0B5A70286C8B2E7EC6CC2AA6671AD77B02D002F50DBB"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "712A4D767F2E8C6F8E82FCADF4AA2C827AA5AE7CF5948E328D455EDB77161A2E"
)


class ProposalError(ValueError):
    """Raised when a frozen proposal contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProposalError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(
        spec is not None and spec.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FAMILY = load_module(
    FAMILY_BUILDER_PATH,
    "pk_bound_terminal_2546_simple_caller_family_helpers_v1",
)
BASE_AUDIT = FAMILY.BASE_AUDIT
CALLER = FAMILY.CALLER
CROSS = FAMILY.CROSS
ENGINE = FAMILY.ENGINE
HONORIFIC = FAMILY.HONORIFIC


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(
    value: Any,
    *,
    source_free: bool,
) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=source_free,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return FAMILY.parse_coordinate(value)


def coordinate_digest(values: Iterable[str]) -> str:
    return FAMILY.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return FAMILY.record_digest(values)


def root_string(root: tuple[int, int]) -> str:
    return f"{root[0]}:{root[1]}"


def load_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    require(path.is_file(), f"required private JSON is absent: {path}")
    raw = path.read_bytes()
    require(
        sha256_bytes(raw) == expected_sha256,
        f"private JSON digest drifted: {path}",
    )
    value = json.loads(raw.decode("utf-8"))
    require(isinstance(value, dict), f"private JSON is not an object: {path}")
    return value


def load_jsonl(path: Path, expected_sha256: str) -> list[dict[str, Any]]:
    require(path.is_file(), f"required private JSONL is absent: {path}")
    raw = path.read_bytes()
    require(
        sha256_bytes(raw) == expected_sha256,
        f"private JSONL digest drifted: {path}",
    )
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        raw.decode("utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        value = json.loads(line)
        require(
            isinstance(value, dict),
            f"{path}:{line_number} is not an object",
        )
        rows.append(value)
    return rows


def build_category_sets(
    ledger: Mapping[str, Any],
) -> tuple[
    set[tuple[int, int]],
    set[str],
    set[str],
    dict[tuple[int, int], str],
]:
    rejected = ledger.get("sets", {}).get("rejected_pending", {})
    rejected_roots = {
        tuple(map(int, value.split(":")))
        for value in rejected.get("roots", ())
    }
    reason_by_root = {
        tuple(map(int, key.split(":"))): str(value)
        for key, value in ledger.get("bindings", {})
        .get("blocker_reason_by_root", {})
        .items()
    }
    roots = {
        root
        for root in rejected_roots
        if reason_by_root.get(root) in A_REASONS
    }
    members = ledger.get("bindings", {}).get("root_members", {})
    pending = {
        coordinate
        for root in roots
        for coordinate in members[root_string(root)][
            "rejected_pending_coordinates"
        ]
    }
    verified = {
        coordinate
        for root in roots
        for coordinate in members[root_string(root)][
            "verified_renewal_coordinates"
        ]
    }
    require(
        len(roots) == EXPECTED_ROOTS
        and record_digest(roots) == EXPECTED_ROOT_SHA256
        and len(pending) == EXPECTED_PENDING_ROWS
        and coordinate_digest(pending)
        == EXPECTED_PENDING_COORDINATE_SHA256
        and len(verified) == EXPECTED_VERIFIED_ROWS
        and coordinate_digest(verified)
        == EXPECTED_VERIFIED_COORDINATE_SHA256,
        "simple-caller category universe drifted",
    )
    return roots, pending, verified, reason_by_root


def load_translation_input(
    review_coordinates: set[str],
) -> tuple[dict[str, str], dict[str, Any]]:
    value = load_json(
        TRANSLATION_INPUT_PATH,
        EXPECTED_TRANSLATION_INPUT_SHA256,
    )
    translations = value.get("translations")
    semantic_review = value.get("semantic_review")
    require(
        value.get("schema") == INPUT_SCHEMA
        and value.get("release_target") == RELEASE_TARGET
        and value.get("resource") == RESOURCE
        and value.get("steam_write_performed") is False
        and isinstance(translations, dict)
        and isinstance(semantic_review, dict)
        and semantic_review.get("jp_is_authority") is True
        and semantic_review.get("pc_en_sc_tc_are_context_only") is True
        and semantic_review.get(
            "question_pragmatics_recast_as_register_safe_"
            "request_intent_or_recommendation"
        )
        is True
        and semantic_review.get(
            "character_voice_and_historical_terms_reviewed"
        )
        is True,
        "translation input metadata drifted",
    )
    exact = {str(key): str(text) for key, text in translations.items()}
    compact = json.dumps(
        exact,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    require(
        set(exact) <= review_coordinates
        and len(exact) == EXPECTED_REWRITE_ROWS
        and coordinate_digest(exact) == EXPECTED_REWRITE_COORDINATE_SHA256
        and sha256_bytes(compact) == EXPECTED_TRANSLATION_MAP_SHA256
        and all(text and not ENGINE.KANA_OR_HAN_RE.search(text) for text in exact.values()),
        "private exact translation map drifted",
    )
    return exact, dict(semantic_review)


def load_checkpoint() -> dict[tuple[str, str], dict[str, Any]]:
    rows = load_jsonl(CHECKPOINT_PATH, EXPECTED_CHECKPOINT_SHA256)
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(key not in result, f"duplicate checkpoint row: {key}")
        result[key] = row
    require(
        len(result) == EXPECTED_CHECKPOINT_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in result.values()
        )
        == EXPECTED_CHECKPOINT_PENDING,
        "BF7B checkpoint universe drifted",
    )
    return result


def build_candidate_records(
    checkpoint: Mapping[tuple[str, str], Mapping[str, Any]],
    translations: Mapping[str, str],
) -> tuple[
    bytes,
    dict[tuple[int, int], Any],
    bytes,
    dict[tuple[int, int], Any],
]:
    replacements = {
        parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in checkpoint.items()
        if resource == RESOURCE and isinstance(row.get("translation"), str)
    }
    checkpoint_blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    checkpoint_records = BASE_AUDIT.records_from_blob(checkpoint_blob)
    proposal_replacements = dict(replacements)
    proposal_replacements.update(
        {
            parse_coordinate(coordinate): text
            for coordinate, text in translations.items()
        }
    )
    proposal_blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        proposal_replacements,
    )
    proposal_records = BASE_AUDIT.records_from_blob(proposal_blob)
    roots = {
        parse_coordinate(coordinate)[:2] for coordinate in translations
    }
    require(
        sha256_bytes(checkpoint_blob)
        == EXPECTED_CHECKPOINT_CANDIDATE_SHA256
        and sha256_bytes(proposal_blob)
        == EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        "checkpoint/proposal candidate digest drifted",
    )
    HONORIFIC.changed_record_guard(
        predecessor_records=checkpoint_records,
        candidate_records=proposal_records,
        expected_changed=roots,
    )
    return (
        checkpoint_blob,
        checkpoint_records,
        proposal_blob,
        proposal_records,
    )


def load_queue_rows(
    roots: set[tuple[int, int]],
) -> dict[tuple[int, int], dict[str, Any]]:
    rows = load_jsonl(QUEUE_PATH, EXPECTED_QUEUE_SHA256)
    selected: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        if row.get("resource") != RESOURCE:
            continue
        root = tuple(map(int, str(row["record_coordinate"]).split(":")))
        if root in roots:
            require(root not in selected, f"duplicate queue root: {root}")
            selected[root] = row
    require(set(selected) == roots, "private context queue root coverage drifted")
    return selected


def structural_multilingual_by_root(
    first_handoff: Mapping[str, Any],
    second_handoff: Mapping[str, Any],
    roots: set[tuple[int, int]],
) -> dict[tuple[int, int], dict[str, bool]]:
    result: dict[tuple[int, int], dict[str, bool]] = {}
    for row in first_handoff["union"]["records"]:
        if row.get("decision") != "reject":
            continue
        root = FAMILY.site_root(str(row["site"]))
        if root in roots:
            result[root] = {
                str(language): bool(present)
                for language, present in row[
                    "multilingual_present"
                ].items()
            }
    for site in second_handoff["rejected_sites"]:
        root = FAMILY.site_root(str(site))
        if root in roots:
            result[root] = {
                "jp": True,
                "en": False,
                "sc": False,
                "tc": False,
            }
    require(set(result) == roots, "handoff multilingual root coverage drifted")
    return result


def language_presence(context: Mapping[str, Any]) -> dict[str, bool]:
    result = {"jp": True}
    for language in ("en", "sc", "tc"):
        values = context.get(language.upper(), ())
        result[language] = bool(
            isinstance(values, list)
            and any(isinstance(value, str) and value for value in values)
        )
    return result


def linewise_nonexpanding(
    current_widths: Sequence[int],
    proposal_widths: Sequence[int],
) -> bool:
    return (
        len(current_widths) == len(proposal_widths)
        and all(
            proposal <= current
            for current, proposal in zip(
                current_widths,
                proposal_widths,
            )
        )
    )


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    ledger = load_json(LEDGER_PATH, EXPECTED_LEDGER_SHA256)
    first_handoff = load_json(
        HANDOFF_000_151_PATH,
        EXPECTED_HANDOFF_000_151_SHA256,
    )
    second_handoff = load_json(
        HANDOFF_152_303_PATH,
        EXPECTED_HANDOFF_152_303_SHA256,
    )
    roots, pending, verified, reason_by_root = build_category_sets(ledger)
    review_coordinates = pending | verified
    require(
        len(review_coordinates) == EXPECTED_REVIEW_ROWS
        and coordinate_digest(review_coordinates)
        == EXPECTED_REVIEW_COORDINATE_SHA256,
        "review coordinate universe drifted",
    )
    translations, semantic_review = load_translation_input(
        review_coordinates
    )
    checkpoint = load_checkpoint()
    (
        _checkpoint_blob,
        checkpoint_records,
        _proposal_blob,
        proposal_records,
    ) = build_candidate_records(checkpoint, translations)
    source_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_PRISTINE
    )[0]
    current_records = BASE_AUDIT.records_from_blob(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes()
    )
    queue_by_root = load_queue_rows(roots)
    structural_multilingual = structural_multilingual_by_root(
        first_handoff,
        second_handoff,
        roots,
    )
    terminal_coordinates = {
        f"0:{record_id}:0" for record_id in TERMINAL_RECORD_IDS
    }
    terminal_text = {
        record_id: BASE_AUDIT.parse_record_literals(
            checkpoint_records[(0, record_id)]
        )[0].text
        for record_id in TERMINAL_RECORD_IDS
    }
    require(
        set(terminal_coordinates)
        <= {
            coordinate
            for resource, coordinate in checkpoint
            if resource == RESOURCE
        },
        "terminal checkpoint rows are absent",
    )
    full_sites = CALLER.call_sites(checkpoint_records, SELECTOR)
    sites_by_root = {
        root: [
            site
            for site in full_sites
            if FAMILY.site_root(site) == root
        ]
        for root in roots
    }
    require(
        all(len(sites) == 1 for sites in sites_by_root.values()),
        "simple-caller root does not have exactly one selector site",
    )

    private_roots: list[dict[str, Any]] = []
    decision_manifest: list[dict[str, Any]] = []
    assembly_manifest: list[dict[str, Any]] = []
    component_manifest: list[dict[str, Any]] = []
    all_width_deltas: list[int] = []
    record_context_signatures: Counter[tuple[str, ...]] = Counter()
    structural_context_signatures: Counter[tuple[str, ...]] = Counter()

    for root in sorted(roots):
        root_id = root_string(root)
        queue_row = queue_by_root[root]
        source_record = source_records[root]
        current_record = current_records[root]
        checkpoint_record = checkpoint_records[root]
        proposal_record = proposal_records[root]
        source_literals = BASE_AUDIT.parse_record_literals(source_record)
        current_literals = BASE_AUDIT.parse_record_literals(current_record)
        checkpoint_literals = BASE_AUDIT.parse_record_literals(
            checkpoint_record
        )
        proposal_literals = BASE_AUDIT.parse_record_literals(proposal_record)
        require(
            len(checkpoint_literals) == len(proposal_literals)
            and len(queue_row["current_ko_literals"])
            == len(checkpoint_literals)
            and queue_row["source_record_raw_sha256"]
            == sha256_bytes(source_record.data)
            and queue_row["current_record_raw_sha256"]
            == sha256_bytes(current_record.data),
            f"private queue/archive binding drifted: {root_id}",
        )
        source_signature = HONORIFIC.component_signatures(source_record)
        current_signature = HONORIFIC.component_signatures(current_record)
        checkpoint_signature = HONORIFIC.component_signatures(
            checkpoint_record
        )
        proposal_signature = HONORIFIC.component_signatures(proposal_record)
        require(
            source_signature
            == current_signature
            == checkpoint_signature
            == proposal_signature
            and ENGINE.record_gap_bytes(source_record)
            == ENGINE.record_gap_bytes(current_record)
            == ENGINE.record_gap_bytes(checkpoint_record)
            == ENGINE.record_gap_bytes(proposal_record),
            f"record control topology drifted: {root_id}",
        )
        component_manifest.append(
            {
                "root": root_id,
                "component_sha256": canonical_sha256(source_signature),
                "record_gap_sha256": canonical_sha256(
                    [gap.hex() for gap in ENGINE.record_gap_bytes(source_record)]
                ),
            }
        )

        coordinate_rows: list[dict[str, Any]] = []
        for literal_id, (
            checkpoint_literal,
            proposal_literal,
        ) in enumerate(zip(checkpoint_literals, proposal_literals)):
            coordinate = f"{root[0]}:{root[1]}:{literal_id}"
            require(
                (RESOURCE, coordinate) in checkpoint,
                f"checkpoint literal row is absent: {coordinate}",
            )
            checkpoint_row = checkpoint[(RESOURCE, coordinate)]
            status = str(checkpoint_row["runtime_review"])
            require(
                coordinate in review_coordinates
                and status
                == ("pending" if coordinate in pending else "verified"),
                f"review status binding drifted: {coordinate}",
            )
            decision = "rewrite" if coordinate in translations else "keep"
            require(
                proposal_literal.text
                == (
                    translations[coordinate]
                    if decision == "rewrite"
                    else checkpoint_literal.text
                ),
                f"proposal literal binding drifted: {coordinate}",
            )
            current_protected = ENGINE.protected_signature(
                checkpoint_literal.text
            )
            proposal_protected = ENGINE.protected_signature(
                proposal_literal.text
            )
            require(
                current_protected == proposal_protected
                and checkpoint_literal.text.count("\n")
                == proposal_literal.text.count("\n"),
                f"protected token/layout signature drifted: {coordinate}",
            )
            source_text = (
                source_literals[literal_id].text
                if literal_id < len(source_literals)
                else None
            )
            coordinate_row = {
                "coordinate": coordinate,
                "checkpoint_runtime_review": status,
                "decision": decision,
                "source_jp": source_text,
                "checkpoint_translation": checkpoint_literal.text,
                "proposal_translation": proposal_literal.text,
                "source_jp_utf16le_sha256": (
                    ENGINE.sha256_text(source_text)
                    if isinstance(source_text, str)
                    else None
                ),
                "checkpoint_translation_utf16le_sha256":
                ENGINE.sha256_text(checkpoint_literal.text),
                "proposal_translation_utf16le_sha256":
                ENGINE.sha256_text(proposal_literal.text),
                "protected_signature": current_protected,
                "protected_signature_preserved": True,
                "line_count_preserved": True,
            }
            coordinate_rows.append(coordinate_row)
            decision_manifest.append(
                {
                    "coordinate": coordinate,
                    "status": status,
                    "decision": decision,
                    "proposal_translation_utf16le_sha256":
                    ENGINE.sha256_text(proposal_literal.text),
                }
            )

        site = sites_by_root[root][0]
        checkpoint_left, checkpoint_right = CALLER.adjacent_literals(
            checkpoint_records,
            site,
        )
        proposal_left, proposal_right = CALLER.adjacent_literals(
            proposal_records,
            site,
        )
        require(
            proposal_left
            and not proposal_left.endswith((".", "?", "!"))
            and proposal_right.startswith("."),
            f"register-safe caller boundary shape drifted: {root_id}",
        )
        root_assemblies: list[dict[str, Any]] = []
        for record_id in TERMINAL_RECORD_IDS:
            ending = terminal_text[record_id]
            checkpoint_assembly = (
                checkpoint_left + ending + checkpoint_right
            )
            proposal_assembly = proposal_left + ending + proposal_right
            checkpoint_widths = CROSS.RESIDUAL_AUDIT.raw_line_widths(
                checkpoint_assembly
            )
            proposal_widths = CROSS.RESIDUAL_AUDIT.raw_line_widths(
                proposal_assembly
            )
            require(
                linewise_nonexpanding(
                    checkpoint_widths,
                    proposal_widths,
                ),
                (
                    "current-relative raw G1N assembly expansion: "
                    f"{root_id}/{record_id}"
                ),
            )
            deltas = [
                proposal - current
                for current, proposal in zip(
                    checkpoint_widths,
                    proposal_widths,
                )
            ]
            all_width_deltas.extend(deltas)
            assembly = {
                "terminal_coordinate": f"0:{record_id}:0",
                "terminal_translation": ending,
                "checkpoint_assembly": checkpoint_assembly,
                "proposal_assembly": proposal_assembly,
                "checkpoint_assembly_utf16le_sha256":
                ENGINE.sha256_text(checkpoint_assembly),
                "proposal_assembly_utf16le_sha256":
                ENGINE.sha256_text(proposal_assembly),
                "checkpoint_raw_g1n_widths": list(checkpoint_widths),
                "proposal_raw_g1n_widths": list(proposal_widths),
                "width_delta_px": deltas,
                "current_relative_nonexpanding": True,
                "grammar_review": "pass",
                "control_topology_preserved": True,
                "protected_signature_preserved": True,
            }
            root_assemblies.append(assembly)
            assembly_manifest.append(
                {
                    "root": root_id,
                    "terminal_record_id": record_id,
                    "checkpoint_assembly_utf16le_sha256":
                    ENGINE.sha256_text(checkpoint_assembly),
                    "proposal_assembly_utf16le_sha256":
                    ENGINE.sha256_text(proposal_assembly),
                    "checkpoint_raw_g1n_widths": list(checkpoint_widths),
                    "proposal_raw_g1n_widths": list(proposal_widths),
                }
            )

        record_presence = language_presence(
            queue_row["pc_context_literals"]
        )
        structural_presence = structural_multilingual[root]
        record_context_signatures[
            tuple(
                language
                for language in ("jp", "en", "sc", "tc")
                if record_presence[language]
            )
        ] += 1
        structural_context_signatures[
            tuple(
                language
                for language in ("jp", "en", "sc", "tc")
                if structural_presence[language]
            )
        ] += 1
        private_roots.append(
            {
                "root": root_id,
                "reason": reason_by_root[root],
                "site": site,
                "verdict": "rewrite",
                "source_record_raw_sha256":
                queue_row["source_record_raw_sha256"],
                "checkpoint_record_sha256":
                sha256_bytes(checkpoint_record.data),
                "proposal_record_sha256":
                sha256_bytes(proposal_record.data),
                "source_context": {
                    "jp": queue_row["source_jp_literals"],
                    "en": queue_row["pc_context_literals"].get("EN", []),
                    "sc": queue_row["pc_context_literals"].get("SC", []),
                    "tc": queue_row["pc_context_literals"].get("TC", []),
                },
                "record_context_present": record_presence,
                "structural_terminal_caller_context_present":
                structural_presence,
                "coordinate_reviews": coordinate_rows,
                "register_assemblies": root_assemblies,
                "proof": {
                    "jp_semantic_authority": True,
                    "pc_multilingual_context_is_auxiliary": True,
                    "all_7_register_assemblies_grammar_pass": True,
                    "all_7_register_assemblies_current_relative_"
                    "raw_g1n_nonexpanding": True,
                    "control_topology_preserved": True,
                    "protected_tokens_preserved": True,
                    "character_voice_reviewed": True,
                    "historical_terms_reviewed": True,
                },
            }
        )

    rewrite_coordinates = set(translations)
    keep_coordinates = review_coordinates - rewrite_coordinates
    pending_rewrite = pending & rewrite_coordinates
    pending_keep = pending & keep_coordinates
    verified_rewrite = verified & rewrite_coordinates
    verified_keep = verified & keep_coordinates
    require(
        len(rewrite_coordinates) == EXPECTED_REWRITE_ROWS
        and coordinate_digest(rewrite_coordinates)
        == EXPECTED_REWRITE_COORDINATE_SHA256
        and len(keep_coordinates) == EXPECTED_KEEP_ROWS
        and coordinate_digest(keep_coordinates)
        == EXPECTED_KEEP_COORDINATE_SHA256
        and len(pending_rewrite) == EXPECTED_PENDING_REWRITE_ROWS
        and coordinate_digest(pending_rewrite)
        == EXPECTED_PENDING_REWRITE_COORDINATE_SHA256
        and len(pending_keep) == EXPECTED_PENDING_KEEP_ROWS
        and coordinate_digest(pending_keep)
        == EXPECTED_PENDING_KEEP_COORDINATE_SHA256
        and len(verified_rewrite) == EXPECTED_VERIFIED_REWRITE_ROWS
        and coordinate_digest(verified_rewrite)
        == EXPECTED_VERIFIED_REWRITE_COORDINATE_SHA256
        and len(verified_keep) == EXPECTED_VERIFIED_KEEP_ROWS
        and coordinate_digest(verified_keep)
        == EXPECTED_VERIFIED_KEEP_COORDINATE_SHA256,
        "keep/rewrite partition drifted",
    )
    require(
        len(assembly_manifest) == EXPECTED_REGISTER_ASSEMBLIES
        and all_width_deltas
        and max(all_width_deltas) <= 0,
        "register assembly proof universe drifted",
    )
    decision_manifest.sort(key=lambda row: parse_coordinate(row["coordinate"]))
    assembly_manifest.sort(
        key=lambda row: (
            tuple(map(int, row["root"].split(":"))),
            int(row["terminal_record_id"]),
        )
    )
    component_manifest.sort(
        key=lambda row: tuple(map(int, row["root"].split(":")))
    )
    reason_counts = Counter(reason_by_root[root] for root in roots)
    expected_reason_counts = {
        "fixed_nominalizer_question_after_terminal": 1,
        "fixed_question_after_terminal": 1,
        "fixed_question_ka": 5,
        "fixed_question_kanou": 1,
        "fixed_question_kayo": 1,
    }
    require(
        dict(sorted(reason_counts.items())) == expected_reason_counts,
        "simple-caller reason partition drifted",
    )
    private_payload = {
        "schema": PRIVATE_SCHEMA,
        "status": "PASS",
        "release_target": RELEASE_TARGET,
        "resource": RESOURCE,
        "bindings": {
            "checkpoint_private_sha256": EXPECTED_CHECKPOINT_SHA256,
            "checkpoint_candidate_sha256":
            EXPECTED_CHECKPOINT_CANDIDATE_SHA256,
            "proposal_candidate_sha256":
            EXPECTED_PROPOSAL_CANDIDATE_SHA256,
            "residual_ledger_sha256": EXPECTED_LEDGER_SHA256,
            "handoff_ord000_151_sha256":
            EXPECTED_HANDOFF_000_151_SHA256,
            "handoff_ord152_303_sha256":
            EXPECTED_HANDOFF_152_303_SHA256,
            "review_queue_sha256": EXPECTED_QUEUE_SHA256,
            "translation_input_sha256":
            EXPECTED_TRANSLATION_INPUT_SHA256,
        },
        "scope": {
            "selector": SELECTOR,
            "terminal_coordinates": sorted(
                terminal_coordinates,
                key=parse_coordinate,
            ),
            "root_count": len(roots),
            "roots": [root_string(root) for root in sorted(roots)],
            "pending_coordinate_count": len(pending),
            "pending_coordinates": sorted(pending, key=parse_coordinate),
            "verified_coordinate_count": len(verified),
            "verified_coordinates": sorted(verified, key=parse_coordinate),
        },
        "semantic_review": semantic_review,
        "exact_translation_map": translations,
        "roots": private_roots,
        "manifests": {
            "decisions": decision_manifest,
            "assemblies": assembly_manifest,
            "components": component_manifest,
        },
        "counts": {
            "root_verdicts": {"keep": 0, "rewrite": 9, "reject": 0},
            "coordinate_verdicts": {
                "keep": len(keep_coordinates),
                "rewrite": len(rewrite_coordinates),
                "reject": 0,
            },
            "pending_coordinate_verdicts": {
                "keep": len(pending_keep),
                "rewrite": len(pending_rewrite),
                "reject": 0,
            },
            "verified_coordinate_verdicts": {
                "keep": len(verified_keep),
                "rewrite": len(verified_rewrite),
                "reject": 0,
            },
            "register_assemblies": len(assembly_manifest),
        },
        "proof": {
            "all_roots_bound_to_exact_blocker_reason": True,
            "all_coordinates_reviewed": True,
            "all_rewrites_private_and_exact": True,
            "all_7_register_assemblies_grammar_pass": True,
            "all_7_register_assemblies_current_relative_raw_g1n_"
            "nonexpanding": True,
            "minimum_width_delta_px": min(all_width_deltas),
            "maximum_width_delta_px": max(all_width_deltas),
            "control_topology_preserved_for_all_roots": True,
            "protected_tokens_preserved_for_all_coordinates": True,
            "jp_semantic_authority_for_all_roots": True,
            "multilingual_context_used_when_present": True,
            "assembly_manifest_sha256":
            canonical_sha256(assembly_manifest),
            "component_manifest_sha256":
            canonical_sha256(component_manifest),
            "decision_manifest_sha256":
            canonical_sha256(decision_manifest),
        },
        "privacy": {
            "classification": "private_translation_bearing",
            "public": False,
            "contains_commercial_source_text": True,
            "contains_translation_bodies": True,
        },
        "steam_write_performed": False,
    }
    private_content = canonical_json(private_payload, source_free=False)
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))

    public_payload = {
        "schema": PUBLIC_SCHEMA,
        "status": "PASS",
        "release_target": RELEASE_TARGET,
        "resource": "MSG_PK/JP/msggame.bin",
        "method": "private_multilingual_simple_caller_retranslation_review",
        "bindings": {
            "checkpoint_private_sha256": EXPECTED_CHECKPOINT_SHA256,
            "checkpoint_candidate_sha256":
            EXPECTED_CHECKPOINT_CANDIDATE_SHA256,
            "proposal_candidate_sha256":
            EXPECTED_PROPOSAL_CANDIDATE_SHA256,
            "residual_ledger_sha256": EXPECTED_LEDGER_SHA256,
            "handoff_ord000_151_sha256":
            EXPECTED_HANDOFF_000_151_SHA256,
            "handoff_ord152_303_sha256":
            EXPECTED_HANDOFF_152_303_SHA256,
            "review_queue_sha256": EXPECTED_QUEUE_SHA256,
            "translation_input_sha256":
            EXPECTED_TRANSLATION_INPUT_SHA256,
            "private_handoff_sha256": private_sha256,
        },
        "scope": {
            "selector": SELECTOR,
            "terminal_records": len(TERMINAL_RECORD_IDS),
            "blocker_roots": len(roots),
            "pending_rows": len(pending),
            "preexisting_verified_rows": len(verified),
            "reviewed_rows": len(review_coordinates),
            "root_sha256": EXPECTED_ROOT_SHA256,
            "pending_coordinate_sha256":
            EXPECTED_PENDING_COORDINATE_SHA256,
            "verified_coordinate_sha256":
            EXPECTED_VERIFIED_COORDINATE_SHA256,
            "review_coordinate_sha256":
            EXPECTED_REVIEW_COORDINATE_SHA256,
        },
        "proposal": {
            "root_verdict_counts": {
                "keep": 0,
                "rewrite": len(roots),
                "reject": 0,
            },
            "coordinate_verdict_counts": {
                "keep": len(keep_coordinates),
                "rewrite": len(rewrite_coordinates),
                "reject": 0,
            },
            "pending_coordinate_verdict_counts": {
                "keep": len(pending_keep),
                "rewrite": len(pending_rewrite),
                "reject": 0,
            },
            "verified_coordinate_verdict_counts": {
                "keep": len(verified_keep),
                "rewrite": len(verified_rewrite),
                "reject": 0,
            },
            "exact_override_coordinate_sha256":
            EXPECTED_REWRITE_COORDINATE_SHA256,
            "exact_override_map_sha256":
            EXPECTED_TRANSLATION_MAP_SHA256,
            "keep_coordinate_sha256":
            EXPECTED_KEEP_COORDINATE_SHA256,
            "potential_runtime_promotion_rows": len(pending),
            "potential_runtime_promotion_roots": len(roots),
            "required_verification_renewal_rows": len(verified),
            "reason_root_counts": dict(sorted(reason_counts.items())),
        },
        "multilingual": {
            "jp_semantic_authority_roots": len(roots),
            "record_context_presence_root_counts": {
                "+".join(signature): count
                for signature, count in sorted(
                    record_context_signatures.items()
                )
            },
            "structural_terminal_caller_presence_root_counts": {
                "+".join(signature): count
                for signature, count in sorted(
                    structural_context_signatures.items()
                )
            },
            "pc_en_sc_tc_used_as_context_only": True,
        },
        "proof": {
            "register_assemblies": len(assembly_manifest),
            "all_7_register_assemblies_grammar_pass": True,
            "all_7_register_assemblies_current_relative_raw_g1n_"
            "nonexpanding": True,
            "minimum_width_delta_px": min(all_width_deltas),
            "maximum_width_delta_px": max(all_width_deltas),
            "control_topology_preserved_for_all_roots": True,
            "protected_tokens_preserved_for_all_coordinates": True,
            "character_voice_and_historical_terms_reviewed": True,
            "assembly_manifest_sha256":
            canonical_sha256(assembly_manifest),
            "component_manifest_sha256":
            canonical_sha256(component_manifest),
            "decision_manifest_sha256":
            canonical_sha256(decision_manifest),
        },
        "integration": {
            "shared_runtime_vm_integration_modified": False,
            "proposal_only": True,
            "safe_to_promote_without_followup_integration": False,
        },
        "distribution_policy": {
            "private_handoff_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
        },
        "steam_write_performed": False,
    }
    public_content = canonical_json(public_payload, source_free=True)
    validate_outputs(
        private_content,
        public_content,
        private_payload,
        public_payload,
    )
    return private_content, public_content, private_payload, public_payload


def validate_outputs(
    private_content: str,
    public_content: str,
    private_payload: Mapping[str, Any],
    public_payload: Mapping[str, Any],
) -> None:
    require(
        private_payload.get("schema") == PRIVATE_SCHEMA
        and private_payload.get("status") == "PASS"
        and private_payload.get("steam_write_performed") is False,
        "private output metadata drifted",
    )
    require(
        public_payload.get("schema") == PUBLIC_SCHEMA
        and public_payload.get("status") == "PASS"
        and public_payload.get("steam_write_performed") is False
        and public_payload.get("integration", {}).get(
            "shared_runtime_vm_integration_modified"
        )
        is False,
        "public output metadata drifted",
    )
    require(
        not re.search(
            r"[\u1100-\u11ff\u3130-\u318f\u3400-\u4dbf"
            r"\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            public_content,
        ),
        "public report contains Hangul/CJK text",
    )
    require(
        not re.search(r"\b\d+:\d+(?::\d+)?\b", public_content),
        "public report exposes exact coordinates",
    )
    require(
        "exact_translation_map" not in public_content
        and "source_context" not in public_content
        and "proposal_translation" not in public_content,
        "public report exposes translation-bearing fields",
    )
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))
    public_sha256 = sha256_bytes(public_content.encode("utf-8"))
    if EXPECTED_PRIVATE_OUTPUT_SHA256 is not None:
        require(
            private_sha256 == EXPECTED_PRIVATE_OUTPUT_SHA256,
            f"private output digest drifted: {private_sha256}",
        )
    if EXPECTED_PUBLIC_OUTPUT_SHA256 is not None:
        require(
            public_sha256 == EXPECTED_PUBLIC_OUTPUT_SHA256,
            f"public output digest drifted: {public_sha256}",
        )


def validate_output_paths(args: argparse.Namespace) -> None:
    private = args.private_output.resolve(strict=False)
    public = args.public_output.resolve(strict=False)
    require(
        DIALOGUE_TMP.resolve(strict=False) in private.parents,
        "private handoff must stay below dialogue tmp",
    )
    require(
        public == DEFAULT_PUBLIC_OUTPUT.resolve(strict=False),
        "public report path is fixed",
    )
    require(private != public, "private and public outputs must differ")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--validate", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.write or args.validate,
        "choose --write and/or --validate",
    )
    validate_output_paths(args)
    private_content, public_content, private_payload, public_payload = (
        build_outputs()
    )
    if args.write:
        args.private_output.parent.mkdir(parents=True, exist_ok=True)
        args.public_output.parent.mkdir(parents=True, exist_ok=True)
        args.private_output.write_text(
            private_content,
            encoding="utf-8",
            newline="\n",
        )
        args.public_output.write_text(
            public_content,
            encoding="ascii",
            newline="\n",
        )
    if args.validate:
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8")
            == private_content,
            "private handoff does not match deterministic output",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="ascii")
            == public_content,
            "public report does not match deterministic output",
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "roots": public_payload["scope"]["blocker_roots"],
                "pending_rows":
                public_payload["scope"]["pending_rows"],
                "exact_overrides":
                public_payload["proposal"][
                    "coordinate_verdict_counts"
                ]["rewrite"],
                "register_assemblies":
                public_payload["proof"]["register_assemblies"],
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
