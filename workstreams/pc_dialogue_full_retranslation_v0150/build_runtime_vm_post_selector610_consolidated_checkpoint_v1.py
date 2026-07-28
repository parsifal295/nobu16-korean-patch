#!/usr/bin/env python3
"""Apply the selector-610 closure as a targeted immutable ledger delta.

This builder intentionally does not invoke the 52,803-row integration engine.
It byte-copies every unaffected FC157A predecessor row and patches the exact
314-row selector-610 decision union once.  The standalone closure owns runtime
assembly and candidate-archive proof; this checkpoint only binds that proof to
the integrated dialogue ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PK_AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
DIALOGUE_TMP = REPO / "tmp" / WORKSTREAM.name

PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector568_1096_1174_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector568_1096_1174_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector610_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector610_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "pk_selector610_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT
    / "public"
    / "pk_selector610_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT
    / "public"
    / "pk_selector610_consolidated_closure_promotion.v1.json"
)

DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector610_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector610_consolidated_checkpoint.source_free.v1.json"
)

LIVE_BASE_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"
)
LIVE_PK_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SCHEMA = (
    "nobu16.kr.pc-dialogue-runtime-vm-selector610-delta-checkpoint."
    "source-free.v1"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector610-consolidated-closure-decision.private.v1"
)
METHOD = (
    "fc157a_selector610_consolidated_union_once_targeted_ledger_delta"
)
RESOURCE = "pk_msggame"
UPDATE_ACTION_FIELD = "selector610_consolidated_update_action"
EXACT_OVERRIDE_FIELD = "selector610_consolidated_exact_override_evidence"

EXPECTED_ROWS = 52_803
EXPECTED_UNAFFECTED_ROWS = 52_489
EXPECTED_DECISIONS = 314
EXPECTED_PROMOTIONS = 167
EXPECTED_RENEWALS = 147
EXPECTED_OVERRIDES = 193
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 120,
    "translation_override_and_runtime_promotion": 47,
    "translation_override_and_verification_renewal": 146,
    "verification_renewal": 1,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 104, 1: 70, 2: 140}

EXPECTED_PREDECESSOR_PENDING = 7_268
EXPECTED_FINAL_PENDING = 7_101
EXPECTED_PREDECESSOR_ELIGIBLE = 45_535
EXPECTED_FINAL_ELIGIBLE = 45_702
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 13_415
EXPECTED_FINAL_PK_PROMOTIONS = 13_582
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_066
EXPECTED_FINAL_PROMOTED_TOTAL = 29_233

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "1FCF033F1F75FC43473152CFB7115D170657519952C19D563C36C3F9BAB4CBD1"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_BASELINE_PRIVATE_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_BASELINE_PUBLIC_SHA256 = (
    "46270F70A019484EFB1F99851D436467C8FD2DE32EB222BDC048DA1B5BC080FA"
)
BASELINE_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector538_family_checkpoint.private.v1.jsonl"
)
BASELINE_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector538_family_checkpoint.source_free.v1.json"
)
EXPECTED_LIVE_BASE_SHA256 = (
    "2E42421F3E96B4B45FA5DC6283666B8810BE03CB237E9CD4F0DC9CEF48D146CB"
)
EXPECTED_LIVE_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)

# Frozen standalone closure inputs.  Output hashes remain unset until the
# first deterministic checkpoint bootstrap is explicitly requested.
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "3AD24E14E63526AA550B4CCCF3E35F0F8D1C3DFF6388D042A4AB258A54DF1588"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "CFEF7B6B8410397DED1FA10AF9C5AAF94D0C1B9C0D0CF1B593527A3A06D15357"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "74FF921D2D6AC801E695F1A3162E65C3F159BC801BD5C394ED34ED9F3815F802"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "0BCD9B8B510381906E555366CB4017F1DC1F70DF749B73029445A026B936E040"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "9ECF66A8FDAF68EC4D04F4EC551A2FF97A62074036644DF330D2063D6E309C95"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "C619DD5D1A3D5CE5EF7DCBD536A5C6D676502A5500E097C7E4877A1D5954C7BE"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "EC800F8EB648829EFE463CDC811D406643DEEDBBA7FDD73B2543C2DCDA831D3F"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "DA0757A25AD524067EC4E76CF66E6DCF567712340ACB98A74EAB0C868FB0F975"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "6CF738A06857042698AE771F81CCDEF998C4CC54828E5900C22A717724542BA8"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "FF7F860EDD682815AEEEC30D61CA6B787BE4038F4FF0BEA0DC8399AAC667F150"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "13849017022482E0E115529572418A27B56D83A2923237A604F09733649EDFCF"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807"
)

EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "0218C3D198C9930C8920ED8DAEB2DDD85987878035AC59DD5ECC8179D38DE12B"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "42BB33CD2F7553EE3E251DDD78933F85D181F140AA133C5843F6DBDF379B53D3"
)


class DeltaCheckpointError(ValueError):
    """Raised when the targeted selector-610 checkpoint contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DeltaCheckpointError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    require(path.is_file(), f"required file is absent: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def coordinate_key(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts  # type: ignore[return-value]


def coordinate_digest(values: Iterable[str]) -> str:
    ordered = sorted(set(values), key=coordinate_key)
    return sha256_bytes(
        "".join(f"{value}\n" for value in ordered).encode("ascii")
    )


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def is_placeholder(value: str | None) -> bool:
    return value is None or value.startswith("__PENDING_")


def input_placeholders() -> list[str]:
    values = {
        "closure_builder": EXPECTED_CLOSURE_BUILDER_SHA256,
        "closure_decisions": EXPECTED_CLOSURE_DECISIONS_SHA256,
        "closure_evidence": EXPECTED_CLOSURE_EVIDENCE_SHA256,
        "closure_coverage": EXPECTED_CLOSURE_COVERAGE_SHA256,
        "closure_promotion": EXPECTED_CLOSURE_PROMOTION_SHA256,
        "decision_coordinates": EXPECTED_DECISION_COORDINATE_SHA256,
        "promotion_coordinates": EXPECTED_PROMOTION_COORDINATE_SHA256,
        "renewal_coordinates": EXPECTED_RENEWAL_COORDINATE_SHA256,
        "override_coordinates": EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "reviewed_sites": EXPECTED_REVIEWED_SITE_SHA256,
        "source_only_sites": EXPECTED_SOURCE_ONLY_SITE_SHA256,
        "final_candidate": EXPECTED_FINAL_CANDIDATE_SHA256,
    }
    return [name for name, value in values.items() if is_placeholder(value)]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"object expected: {path}")
    return value


def nested_named_values(value: Any, name: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == name:
                found.append(child)
            found.extend(nested_named_values(child, name))
    elif isinstance(value, list):
        for child in value:
            found.extend(nested_named_values(child, name))
    return found


def report_contains(report: Mapping[str, Any], name: str, value: Any) -> bool:
    return value in nested_named_values(report, name)


def validate_output_paths(
    private_output: Path,
    public_output: Path,
) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    resolved_private = private_output.resolve(strict=False)
    require(
        resolved_private == DEFAULT_PRIVATE_OUTPUT.resolve(strict=False),
        "private output must use the selector-610 immutable checkpoint path",
    )
    require(
        private_root in resolved_private.parents,
        "private output must remain below tmp",
    )
    require(
        public_output.resolve(strict=False)
        == DEFAULT_PUBLIC_OUTPUT.resolve(strict=False),
        "public output must use the selector-610 source-free checkpoint path",
    )
    require(
        resolved_private != public_output.resolve(strict=False),
        "private and public outputs must be distinct",
    )


def validate_frozen_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    pending = input_placeholders()
    require(
        not pending,
        "selector-610 closure pins are not frozen: " + ", ".join(pending),
    )
    expected = {
        PREDECESSOR_PRIVATE_PATH: EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        PREDECESSOR_PUBLIC_PATH: EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        BASELINE_PRIVATE_PATH: EXPECTED_BASELINE_PRIVATE_SHA256,
        BASELINE_PUBLIC_PATH: EXPECTED_BASELINE_PUBLIC_SHA256,
        CLOSURE_BUILDER_PATH: EXPECTED_CLOSURE_BUILDER_SHA256,
        CLOSURE_DECISIONS_PATH: EXPECTED_CLOSURE_DECISIONS_SHA256,
        CLOSURE_EVIDENCE_PATH: EXPECTED_CLOSURE_EVIDENCE_SHA256,
        CLOSURE_COVERAGE_PATH: EXPECTED_CLOSURE_COVERAGE_SHA256,
        CLOSURE_PROMOTION_PATH: EXPECTED_CLOSURE_PROMOTION_SHA256,
    }
    for path, digest in expected.items():
        require(sha256_file(path) == digest, f"frozen input drifted: {path}")
    if LIVE_BASE_PATH.is_file():
        require(
            sha256_file(LIVE_BASE_PATH) == EXPECTED_LIVE_BASE_SHA256,
            "live Steam Base archive drifted",
        )
    if LIVE_PK_PATH.is_file():
        require(
            sha256_file(LIVE_PK_PATH) == EXPECTED_LIVE_PK_SHA256,
            "live Steam PK archive drifted",
        )
    coverage = load_json(CLOSURE_COVERAGE_PATH)
    promotion = load_json(CLOSURE_PROMOTION_PATH)
    validate_closure_reports(coverage, promotion)
    return coverage, promotion


def validate_closure_reports(
    coverage: Mapping[str, Any],
    promotion: Mapping[str, Any],
) -> None:
    reports = [coverage, promotion]
    require(
        all(report.get("status") == "PASS" for report in reports),
        "selector-610 closure report is not PASS",
    )
    require(
        all(report.get("steam_write_performed") is False for report in reports),
        "selector-610 closure report permits a Steam write",
    )
    coverage_result = coverage.get("result", {})
    promotion_result = promotion.get("result", {})
    coverage_guards = coverage.get("guards", {})
    promotion_guards = promotion.get("guards", {})
    coverage_candidate = coverage.get("candidate", {})
    promotion_candidate = promotion.get("candidate", {})
    coverage_inputs = coverage.get("inputs", {})
    promotion_inputs = promotion.get("inputs", {})
    require(
        coverage_result.get("decision_rows") == EXPECTED_DECISIONS
        and coverage_result.get("reviewed_sites") == 230
        and coverage_result.get("source_only_sites") == 13
        and coverage_result.get("source_only_actions") == 0
        and promotion_result.get("decision_rows") == EXPECTED_DECISIONS
        and promotion_result.get("promotions") == EXPECTED_PROMOTIONS
        and promotion_result.get("renewals") == EXPECTED_RENEWALS
        and promotion_result.get("overrides") == EXPECTED_OVERRIDES
        and promotion_result.get("action_counts") == EXPECTED_ACTION_COUNTS
        and promotion_result.get("pending_before")
        == EXPECTED_PREDECESSOR_PENDING
        and promotion_result.get("pending_after") == EXPECTED_FINAL_PENDING,
        "selector-610 closure counts drifted",
    )
    expected_guards = {
        "decision_coordinate_sha256":
            EXPECTED_DECISION_COORDINATE_SHA256,
        "promotion_coordinate_sha256":
            EXPECTED_PROMOTION_COORDINATE_SHA256,
        "renewal_coordinate_sha256":
            EXPECTED_RENEWAL_COORDINATE_SHA256,
        "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "candidate_call_site_sha256":
            EXPECTED_REVIEWED_SITE_SHA256,
        "source_only_site_sha256":
            EXPECTED_SOURCE_ONLY_SITE_SHA256,
        "decision_file_sha256":
            EXPECTED_CLOSURE_DECISIONS_SHA256,
        "private_evidence_sha256":
            EXPECTED_CLOSURE_EVIDENCE_SHA256,
    }
    require(
        all(
            coverage_guards.get(key) == value
            and promotion_guards.get(key) == value
            for key, value in expected_guards.items()
        ),
        "selector-610 closure guard digest drifted",
    )
    require(
        coverage_inputs.get("official_ledger_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and promotion_inputs.get("official_ledger_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and coverage_inputs.get("official_public_checkpoint_sha256")
        == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and promotion_inputs.get("official_public_checkpoint_sha256")
        == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and coverage_candidate.get("official_predecessor_sha256")
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
        and promotion_candidate.get("official_predecessor_sha256")
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
        and coverage_candidate.get("reviewed_sha256")
        == EXPECTED_FINAL_CANDIDATE_SHA256
        and promotion_candidate.get("reviewed_sha256")
        == EXPECTED_FINAL_CANDIDATE_SHA256
        and coverage_candidate.get("reverse_overlay_sha256")
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
        and promotion_candidate.get("reverse_overlay_sha256")
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
        "selector-610 closure lineage/candidate drifted",
    )


def load_closure_decisions() -> dict[str, dict[str, Any]]:
    decisions: dict[str, dict[str, Any]] = {}
    actions: Counter[str] = Counter()
    owners: Counter[int] = Counter()
    promotions: list[str] = []
    renewals: list[str] = []
    overrides: list[str] = []
    for line in CLOSURE_DECISIONS_PATH.read_text(
        encoding="utf-8"
    ).splitlines():
        if not line:
            continue
        row = json.loads(line)
        require(isinstance(row, dict), "closure decision must be an object")
        coordinate = str(row.get("coordinate"))
        coordinate_key(coordinate)
        action = str(row.get(UPDATE_ACTION_FIELD))
        translation = row.get("translation")
        owner = row.get("owner_chunk")
        require(
            row.get("schema") == PRIVATE_DECISION_SCHEMA
            and row.get("resource") == RESOURCE
            and coordinate not in decisions
            and action in EXPECTED_ACTION_COUNTS
            and isinstance(translation, str)
            and row.get("translation_utf16le_sha256")
            == utf16le_sha256(translation)
            and isinstance(owner, int)
            and owner in EXPECTED_OWNER_CHUNK_COUNTS
            and row.get("fresh_semantic_review") == "approved"
            and row.get("historical_factuality_review") == "approved"
            and row.get("speaker_tone_review") == "approved"
            and row.get("runtime_review") == "verified"
            and row.get("layout_review")
            == "current_relative_raw_g1n_nonexpanding",
            f"invalid closure decision: {coordinate}",
        )
        decisions[coordinate] = row
        actions[action] += 1
        owners[owner] += 1
        if "runtime_promotion" in action:
            promotions.append(coordinate)
        else:
            renewals.append(coordinate)
        if action.startswith("translation_override"):
            overrides.append(coordinate)
    require(
        len(decisions) == EXPECTED_DECISIONS
        and dict(sorted(actions.items())) == EXPECTED_ACTION_COUNTS
        and dict(sorted(owners.items())) == EXPECTED_OWNER_CHUNK_COUNTS
        and len(promotions) == EXPECTED_PROMOTIONS
        and len(renewals) == EXPECTED_RENEWALS
        and len(overrides) == EXPECTED_OVERRIDES
        and coordinate_digest(decisions) == EXPECTED_DECISION_COORDINATE_SHA256
        and coordinate_digest(promotions)
        == EXPECTED_PROMOTION_COORDINATE_SHA256
        and coordinate_digest(renewals)
        == EXPECTED_RENEWAL_COORDINATE_SHA256
        and coordinate_digest(overrides)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "selector-610 decision union drifted",
    )
    return decisions


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    coordinate = str(decision["coordinate"])
    action = str(decision[UPDATE_ACTION_FIELD])
    translation = str(decision["translation"])
    expected_status = (
        "pending" if "runtime_promotion" in action else "verified"
    )
    require(
        predecessor.get("resource") == RESOURCE
        and predecessor.get("coordinate") == coordinate
        and predecessor.get("semantic_review") == "approved"
        and predecessor.get("runtime_review") == expected_status
        and isinstance(predecessor.get("translation"), str)
        and utf16le_sha256(str(predecessor["translation"]))
        == decision.get("official_predecessor_utf16le_sha256"),
        f"FC157A predecessor decision drifted: {coordinate}",
    )
    changed = dict(predecessor)
    changed["translation"] = translation
    changed["runtime_review"] = "verified"
    changed["scope_classification"] = "retranslated"
    changed["layout_review"] = "current_relative_raw_g1n_nonexpanding"
    changed[UPDATE_ACTION_FIELD] = action
    changed["runtime_vm_verification"] = {
        "schema":
            "nobu16.kr.pk-selector610-consolidated-row-verification.v1",
        "method":
            "reversed_vm_pk_selector610_consolidated_closure",
        "result": "verified",
        "per_row_game_playback_required": False,
        "closure_decision_file_sha256":
            EXPECTED_CLOSURE_DECISIONS_SHA256,
        "closure_evidence_file_sha256":
            EXPECTED_CLOSURE_EVIDENCE_SHA256,
        "owner_chunk": decision["owner_chunk"],
        "jp_source_utf16le_sha256":
            decision["jp_source_utf16le_sha256"],
        "translation_utf16le_sha256":
            decision["translation_utf16le_sha256"],
    }
    if action.startswith("translation_override"):
        changed[EXACT_OVERRIDE_FIELD] = {
            "official_predecessor_utf16le_sha256":
                decision["official_predecessor_utf16le_sha256"],
            "translation_utf16le_sha256":
                decision["translation_utf16le_sha256"],
        }
    return changed


def serialized_private_row(row: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def generate_private_checkpoint(
    decisions: Mapping[str, Mapping[str, Any]],
    output_path: Path | None,
) -> tuple[str, dict[str, Any]]:
    digest = hashlib.sha256()
    row_count = 0
    affected = 0
    unaffected = 0
    seen: set[str] = set()
    output_stream: Any = None
    temporary_name: str | None = None
    try:
        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=output_path.name + ".",
                suffix=".tmp",
                dir=output_path.parent,
                delete=False,
            )
            output_stream = temporary
            temporary_name = temporary.name
        with PREDECESSOR_PRIVATE_PATH.open("rb") as predecessor:
            for raw_line in predecessor:
                row_count += 1
                row = json.loads(raw_line.decode("utf-8"))
                coordinate = str(row.get("coordinate"))
                if row.get("resource") == RESOURCE and coordinate in decisions:
                    require(
                        coordinate not in seen,
                        f"duplicate predecessor coordinate: {coordinate}",
                    )
                    output_line = serialized_private_row(
                        patch_predecessor_row(row, decisions[coordinate])
                    )
                    seen.add(coordinate)
                    affected += 1
                else:
                    output_line = raw_line
                    unaffected += 1
                digest.update(output_line)
                if output_stream is not None:
                    output_stream.write(output_line)
        require(
            row_count == EXPECTED_ROWS
            and affected == EXPECTED_DECISIONS
            and unaffected == EXPECTED_UNAFFECTED_ROWS
            and seen == set(decisions),
            "targeted predecessor stream coverage drifted",
        )
        if output_stream is not None:
            output_stream.flush()
            os.fsync(output_stream.fileno())
            output_stream.close()
            os.replace(temporary_name, output_path)
            temporary_name = None
    finally:
        if output_stream is not None and not output_stream.closed:
            output_stream.close()
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
    return digest.hexdigest().upper(), {
        "row_count": row_count,
        "affected_row_count": affected,
        "unaffected_raw_line_copy_count": unaffected,
    }


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "method": METHOD,
        "release_target": "0.15.0",
        "inputs": {
            "predecessor_private_sha256":
                EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "predecessor_public_sha256":
                EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            "predecessor_candidate_sha256":
                EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "closure_builder_sha256":
                EXPECTED_CLOSURE_BUILDER_SHA256,
            "closure_decisions_sha256":
                EXPECTED_CLOSURE_DECISIONS_SHA256,
            "closure_evidence_sha256":
                EXPECTED_CLOSURE_EVIDENCE_SHA256,
            "closure_coverage_sha256":
                EXPECTED_CLOSURE_COVERAGE_SHA256,
            "closure_promotion_sha256":
                EXPECTED_CLOSURE_PROMOTION_SHA256,
        },
        "selector610_consolidated": {
            "updated_row_count": EXPECTED_DECISIONS,
            "promotion_count": EXPECTED_PROMOTIONS,
            "verification_renewal_count": EXPECTED_RENEWALS,
            "semantic_override_count": EXPECTED_OVERRIDES,
            "action_counts": EXPECTED_ACTION_COUNTS,
            "decision_coordinate_sha256":
                EXPECTED_DECISION_COORDINATE_SHA256,
            "promotion_coordinate_sha256":
                EXPECTED_PROMOTION_COORDINATE_SHA256,
            "renewal_coordinate_sha256":
                EXPECTED_RENEWAL_COORDINATE_SHA256,
            "override_coordinate_sha256":
                EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "reviewed_site_count": 230,
            "reviewed_site_sha256": EXPECTED_REVIEWED_SITE_SHA256,
            "source_only_repair_site_count": 13,
            "source_only_site_sha256":
                EXPECTED_SOURCE_ONLY_SITE_SHA256,
            "source_only_action_count": 0,
            "predecessor_candidate_sha256":
                EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "final_candidate_sha256":
                EXPECTED_FINAL_CANDIDATE_SHA256,
            "reverse_overlay_sha256":
                EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "single_coordinate_union_used": True,
            "sequential_chunk_overlays_used": False,
            "steam_write_performed": False,
        },
        "result": {
            "semantic_review_approved": EXPECTED_ROWS,
            "runtime_review_pending": EXPECTED_FINAL_PENDING,
            "fully_candidate_eligible": EXPECTED_FINAL_ELIGIBLE,
            "promoted_total": EXPECTED_FINAL_PROMOTED_TOTAL,
            "pk_msggame_promotion_count": EXPECTED_FINAL_PK_PROMOTIONS,
            "private_integrated_decision_sha256": private_sha256,
            **stream_result,
        },
        "validation": {
            "full_integration_engine_invoked": False,
            "targeted_affected_rows_rechecked": EXPECTED_DECISIONS,
            "unaffected_rows_byte_copied": EXPECTED_UNAFFECTED_ROWS,
            "candidate_call_sites_rechecked": 230,
            "source_only_sites_rechecked": 13,
            "event_dialogue_912px_rule_applied": False,
            "current_relative_raw_g1n_nonexpansion_used": True,
            "steam_archives_read_only": True,
        },
        "distribution_policy": {
            "private_integrated_decision_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }


def serialized_public_report(report: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            report,
            ensure_ascii=True,
            indent=2,
        )
        + "\n"
    ).encode("ascii")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb",
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
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
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--bootstrap-output-pins",
        action="store_true",
        help="permit the first deterministic write before output hashes are pinned",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    validate_output_paths(args.private_output, args.public_output)
    validate_frozen_inputs()
    decisions = load_closure_decisions()
    output_is_unpinned = (
        EXPECTED_PRIVATE_OUTPUT_SHA256 is None
        or EXPECTED_PUBLIC_OUTPUT_SHA256 is None
    )
    require(
        not output_is_unpinned or args.bootstrap_output_pins,
        "output hashes are not pinned; use --bootstrap-output-pins once",
    )
    require(
        not args.check or not output_is_unpinned,
        "--check requires frozen output hashes",
    )
    private_sha256, stream_result = generate_private_checkpoint(
        decisions,
        args.private_output if args.write else None,
    )
    report = build_public_report(private_sha256, stream_result)
    public_content = serialized_public_report(report)
    public_sha256 = sha256_bytes(public_content)
    if EXPECTED_PRIVATE_OUTPUT_SHA256 is not None:
        require(
            private_sha256 == EXPECTED_PRIVATE_OUTPUT_SHA256,
            "private selector-610 checkpoint digest drifted",
        )
    if EXPECTED_PUBLIC_OUTPUT_SHA256 is not None:
        require(
            public_sha256 == EXPECTED_PUBLIC_OUTPUT_SHA256,
            "public selector-610 checkpoint digest drifted",
        )
    if args.write:
        atomic_write(args.public_output, public_content)
    if args.check:
        require(
            sha256_file(args.private_output)
            == EXPECTED_PRIVATE_OUTPUT_SHA256,
            "written private selector-610 checkpoint drifted",
        )
        require(
            sha256_file(args.public_output)
            == EXPECTED_PUBLIC_OUTPUT_SHA256,
            "written public selector-610 checkpoint drifted",
        )
    print(
        "PASS "
        f"private_sha256={private_sha256} "
        f"public_sha256={public_sha256} "
        f"promoted={EXPECTED_PROMOTIONS} "
        f"pending={EXPECTED_FINAL_PENDING} "
        "full_integration_rebuild=false steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DeltaCheckpointError as error:
        raise SystemExit(f"ERROR: {error}") from error
