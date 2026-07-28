#!/usr/bin/env python3
"""Build the single-union selector-610 runtime closure on frozen FC157A."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
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
SEMANTIC_TMP = DIALOGUE_TMP / "semantic_overrides"
PUBLIC_DIR = WORKSTREAM / "public"

ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector610_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector610_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector610_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / (
        "runtime_vm_integrated.post_selector568_1096_1174_consolidated_"
        "checkpoint.private.v1.jsonl"
    )
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP
    / (
        "pk_selector568_1096_1174_consolidated_closure_"
        "decisions.private.v1.jsonl"
    )
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector610_chunk{chunk}_review_v1.py"
    for chunk in range(3)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector610_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(3)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP
    / f"pk_selector610_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(3)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector610_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(3)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP
    / "pk_selector610_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector610_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector610_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector610_consolidated_closure_promotion.v1.json"
)

METHOD = (
    "fc157a_selector610_three_chunk_single_union_with_targeted_"
    "source_only_runtime_delta_proof"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector610-consolidated-closure-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector610-consolidated-closure-evidence.private.v1"
)
PUBLIC_COVERAGE_SCHEMA = (
    "nobu16.kr.pk-selector610-consolidated-closure-coverage.v1"
)
PUBLIC_PROMOTION_SCHEMA = (
    "nobu16.kr.pk-selector610-consolidated-closure-promotion.v1"
)
UPDATE_ACTION_FIELD = "selector610_consolidated_update_action"
ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector610-assignment.private.v1"
RECOGNIZED_ACTIONS = frozenset(
    {
        "runtime_promotion",
        "translation_override_and_runtime_promotion",
        "translation_override_and_verification_renewal",
        "verification_renewal",
    }
)

EXPECTED_INPUT_SHA256 = {
    "assignment_builder":
        "C0BC64F37C288E23F0C8E7437775BA4534A44F05C500A8B4E70E5965BCF9D5EA",
    "assignment_private":
        "50A4234CC7207FFF4BCC3049532EC78502E1E8F14565CF1FBFC5399A88D4D036",
    "assignment_public":
        "FD98F9289C6F1D429BF03B53252E9C1846262A29419E97ECDCE26695D91E9C2F",
    "official_ledger":
        "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA",
    "predecessor_decisions":
        "3260FCF12561EE116228907E1619FDB368DBDF9D0BA8565C03CD014440669B38",
    "chunk0_builder":
        "6660C56EDC296FC542B8DF28F4AAB15822E9E8D8AB99D1B6446F676AE766BA45",
    "chunk0_public":
        "F8826430F6B48D985A93021E44F655430A0F1CF830B0BF0B38CE910F5249BAD2",
    "chunk0_decisions":
        "EF6679D24898A4EB87FEBDF2AFBF2AC47FB6EBEC2253D9C52091C22751F3012C",
    "chunk0_evidence":
        "35947BFF399DC9B1263B8D10EE54C1D71F9A034D0AE62F4796608D0BFE6D2785",
    "chunk1_builder":
        "DF39B5719F5DC0232892FEE6A867A1CF0DF1F0BD831C89619917D29563513EF6",
    "chunk1_public":
        "2EAF65919343C560D4289715FB1D5792B07D6616B64498855FAB95D985346143",
    "chunk1_decisions":
        "940D7082F3289252C8C5EDEC134B4E70E540B951DFBCFBA081860CA248239B34",
    "chunk1_evidence":
        "02FA41E288D8B302B87DB83142F216B5D3A7BF26449AA533471282C39B436224",
    "chunk2_builder":
        "85E18A21E83C0ACA78394F4560AA9BA3136283E242DE6DA778D2A45B6654BEA9",
    "chunk2_public":
        "FBFEB8A18D1CD65EE20E06CF68A7EEB321F984D43BE21C1D2373E4BF688755EC",
    "chunk2_decisions":
        "56C31683AF3CB6FBABA3127453A9B17C9F7487A7E28667F4B454199E78E93720",
    "chunk2_evidence":
        "13CE2F94A82D40ADE6B25F15D612028854D0727DD784F76614FCCEFF74D41FA9",
}
EXPECTED_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "1FCF033F1F75FC43473152CFB7115D170657519952C19D563C36C3F9BAB4CBD1"
)
EXPECTED_CHUNK_ROWS = (104, 70, 140)
EXPECTED_CHUNK_SITES = (77, 77, 76)
EXPECTED_DECISION_ROWS = 314
EXPECTED_DECISION_ROOTS = 125
EXPECTED_PROMOTIONS = 167
EXPECTED_RENEWALS = 147
EXPECTED_OVERRIDES = 193
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 120,
    "translation_override_and_runtime_promotion": 47,
    "translation_override_and_verification_renewal": 146,
    "verification_renewal": 1,
}
EXPECTED_PENDING_BEFORE = 7_268
EXPECTED_PENDING_AFTER = 7_101
EXPECTED_REVIEWED_SITES = 230
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "FF7F860EDD682815AEEEC30D61CA6B787BE4038F4FF0BEA0DC8399AAC667F150"
)
EXPECTED_SOURCE_SITES = 243
EXPECTED_SOURCE_SITE_SHA256 = (
    "4927B74B595BEBD13968E16056C13FEF757437A211EBF2F777F7EC4313DBD015"
)
EXPECTED_SOURCE_ONLY_SITES = 13
EXPECTED_SOURCE_ONLY_SHA256 = (
    "13849017022482E0E115529572418A27B56D83A2923237A604F09733649EDFCF"
)
EXPECTED_PREDECESSOR_OVERLAPS = 4
EXPECTED_PREDECESSOR_SUPERSESSIONS = 3

# Filled after the first deterministic write, then frozen for --check.
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "CFEF7B6B8410397DED1FA10AF9C5AAF94D0C1B9C0D0CF1B593527A3A06D15357",
    "private_evidence":
        "74FF921D2D6AC801E695F1A3162E65C3F159BC801BD5C394ED34ED9F3815F802",
    "public_coverage":
        "0BCD9B8B510381906E555366CB4017F1DC1F70DF749B73029445A026B936E040",
    "public_promotion":
        "9ECF66A8FDAF68EC4D04F4EC551A2FF97A62074036644DF330D2063D6E309C95",
    "final_candidate":
        "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807",
    "decision_coordinates":
        "C619DD5D1A3D5CE5EF7DCBD536A5C6D676502A5500E097C7E4877A1D5954C7BE",
    "promotion_coordinates":
        "EC800F8EB648829EFE463CDC811D406643DEEDBBA7FDD73B2543C2DCDA831D3F",
    "renewal_coordinates":
        "DA0757A25AD524067EC4E76CF66E6DCF567712340ACB98A74EAB0C868FB0F975",
    "override_coordinates":
        "6CF738A06857042698AE771F81CCDEF998C4CC54828E5900C22A717724542BA8",
    "predecessor_overlap_coordinates":
        "92D944D30CB2E68C0ABAD8067A2E3F0455F443F5E1D806A75E681A06CEC720B3",
    "predecessor_supersession_coordinates":
        "BC50B1F37B501B4CD0A2AE3867F29B869393A072C1177F6B38BF53861D63639C",
    "source_only_proof":
        "9AFC5BA029B0EC0661A24D9F0E807D5B83347C2507A5594241B0721BCA9C6FE8",
}


class ClosureError(ValueError):
    """Raised when a frozen selector-610 closure invariant drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector610_consolidated_input")
ENGINE = ASSIGNMENT.ENGINE
RANKING = ASSIGNMENT.RANKING


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def coordinate_digest(values: Iterable[str]) -> str:
    return ASSIGNMENT.coordinate_digest(values)


def root_digest(values: Iterable[str]) -> str:
    payload = "\n".join(
        sorted(set(values), key=lambda item: tuple(map(int, item.split(":"))))
    )
    return sha256_bytes(payload.encode("ascii"))


def site_digest(values: Iterable[str]) -> str:
    return ASSIGNMENT.site_digest(values)


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts  # type: ignore[return-value]


def coordinate_root(value: str) -> str:
    return ":".join(value.split(":")[:2])


def utf16_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le", errors="strict"))


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"BOM rejected: {path}")
    value = json.loads(raw.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_bytes().splitlines(), start=1):
        if not line:
            continue
        value = json.loads(line.decode("utf-8", errors="strict"))
        require(
            isinstance(value, dict),
            f"JSONL object required: {path}:{line_number}",
        )
        result.append(value)
    return result


def literal_text(
    records: Mapping[tuple[int, int], Any], coordinate: str
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), f"literal absent: {coordinate}")
    return str(literals[literal_id].text)


def without_outer_whitespace(signature: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in signature.items()
        if key not in {"leading_whitespace", "trailing_whitespace"}
    }


def reviewed_translation(row: Mapping[str, Any]) -> str:
    value = row.get("reviewed_translation", row.get("translation"))
    require(isinstance(value, str), "reviewed translation absent")
    return value


def reviewed_translation_sha256(row: Mapping[str, Any]) -> str:
    value = row.get("reviewed_utf16le_sha256", row.get("translation_utf16le_sha256"))
    require(isinstance(value, str), "reviewed translation hash absent")
    return value


def serialized_json(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def serialized_jsonl(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return b"".join(serialized_json(row) for row in rows)


def assert_source_free(value: Any) -> None:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            content,
        )
        is None,
        "public artifact contains CJK text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", content) is None,
        "public artifact contains an exact coordinate",
    )
    require(
        '"translation"' not in content and '"reviewed_translation"' not in content,
        "public artifact contains a translation field",
    )


def validate_immutable_inputs() -> None:
    paths = {
        "assignment_builder": ASSIGNMENT_BUILDER_PATH,
        "assignment_private": ASSIGNMENT_PRIVATE_PATH,
        "assignment_public": ASSIGNMENT_PUBLIC_PATH,
        "official_ledger": OFFICIAL_LEDGER_PATH,
        "predecessor_decisions": PREDECESSOR_DECISIONS_PATH,
    }
    for chunk in range(len(CHUNK_BUILDERS)):
        paths[f"chunk{chunk}_builder"] = CHUNK_BUILDERS[chunk]
        paths[f"chunk{chunk}_public"] = CHUNK_PUBLIC[chunk]
        paths[f"chunk{chunk}_decisions"] = CHUNK_DECISIONS[chunk]
        paths[f"chunk{chunk}_evidence"] = CHUNK_EVIDENCE[chunk]
    for label, path in paths.items():
        require(
            path.is_file() and sha256_file(path) == EXPECTED_INPUT_SHA256[label],
            f"immutable input drifted: {label}",
        )


def load_official_rows() -> tuple[
    list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]
]:
    rows = load_jsonl(OFFICIAL_LEDGER_PATH)
    by_key = {
        (str(row["resource"]), str(row["coordinate"])): row for row in rows
    }
    require(len(by_key) == len(rows), "official ledger keys are not unique")
    pending = sum(row.get("runtime_review") == "pending" for row in rows)
    require(pending == EXPECTED_PENDING_BEFORE, "official pending count drifted")
    return rows, by_key


def validate_chunk_evidence(
    assignment: Mapping[str, Any],
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    evidence = [load_json(path) for path in CHUNK_EVIDENCE]
    assigned_chunks = assignment["chunks"]
    all_sites: set[str] = set()
    for chunk_id in range(len(CHUNK_BUILDERS)):
        rows = chunk_rows[chunk_id]
        chunk_evidence = evidence[chunk_id]
        assigned = assigned_chunks[chunk_id]
        sites = {str(row["site"]) for row in chunk_evidence["site_reviews"]}
        assigned_sites = set(map(str, assigned["sites"]))
        coordinates = {str(row["coordinate"]) for row in rows}
        assigned_roots = set(map(str, assigned["roots"]))
        require(
            len(rows) == EXPECTED_CHUNK_ROWS[chunk_id]
            and len(coordinates) == len(rows),
            f"chunk{chunk_id} decision count drifted",
        )
        require(
            sites == assigned_sites and len(sites) == EXPECTED_CHUNK_SITES[chunk_id],
            f"chunk{chunk_id} site coverage drifted",
        )
        escaped = {
            str(row["coordinate"])
            for row in rows
            if coordinate_root(str(row["coordinate"])) not in assigned_roots
            and not str(row.get("overlap_owner") or "")
        }
        require(not escaped, f"chunk{chunk_id} decision escaped its assignment")
        require(not all_sites & sites, "assignment sites overlap across chunks")
        all_sites.update(sites)
    require(
        len(all_sites) == EXPECTED_REVIEWED_SITES
        and site_digest(all_sites) == EXPECTED_CANDIDATE_SITE_SHA256,
        "reviewed selector-610 site union drifted",
    )
    return evidence


def validate_site_call(
    records: Mapping[tuple[int, int], Any],
    site: str,
    *,
    expected: bool,
) -> None:
    block_id, record_id, gap_id, offset = map(int, site.split(":"))
    rows = [
        row
        for row in RANKING.LEGACY.record_edges(records[(block_id, record_id)])
        if row["kind"] == "C"
        and tuple(row["target"]) == (0, 610)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    require(bool(rows) is expected, f"selector-610 site state drifted: {site}")


def source_only_runtime_delta_proof(
    assignment: Mapping[str, Any],
    current_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
    source_records: Mapping[tuple[int, int], Any],
) -> dict[str, Any]:
    candidate_sites = set(map(str, assignment["scope"]["candidate_call_sites"]))
    source_only = set(
        map(str, assignment["scope"]["source_only_repair_sites"])
    )
    source_sites = set(
        map(
            str,
            assignment["scope"].get(
                "source_call_sites", candidate_sites | source_only
            ),
        )
    )
    require(
        len(candidate_sites) == EXPECTED_REVIEWED_SITES
        and site_digest(candidate_sites) == EXPECTED_CANDIDATE_SITE_SHA256,
        "candidate site register drifted",
    )
    require(
        len(source_sites) == EXPECTED_SOURCE_SITES
        and site_digest(source_sites) == EXPECTED_SOURCE_SITE_SHA256,
        "source site register drifted",
    )
    require(
        source_sites - candidate_sites == source_only
        and not candidate_sites - source_sites
        and len(source_only) == EXPECTED_SOURCE_ONLY_SITES
        and site_digest(source_only) == EXPECTED_SOURCE_ONLY_SHA256,
        "source-only register drifted",
    )
    for site in sorted(candidate_sites, key=RANKING.site_key):
        validate_site_call(current_records, site, expected=True)
        validate_site_call(candidate_records, site, expected=True)
        validate_site_call(source_records, site, expected=True)
    proof_rows = []
    for site in sorted(source_only, key=RANKING.site_key):
        validate_site_call(source_records, site, expected=True)
        validate_site_call(current_records, site, expected=False)
        validate_site_call(candidate_records, site, expected=False)
        root = tuple(map(int, site.split(":")[:2]))
        for records, label in (
            (current_records, "current"),
            (candidate_records, "candidate"),
        ):
            calls = [
                row
                for row in RANKING.LEGACY.record_edges(records[root])
                if row["kind"] == "C" and tuple(row["target"]) == (0, 610)
            ]
            require(not calls, f"source-only root has a {label} selector call")
        proof_rows.append(
            {
                "site": site,
                "source_call_present": True,
                "current_call_absent": True,
                "candidate_call_absent": True,
                "action": "none",
            }
        )
    return {
        "actions": 0,
        "classification": "pristine_only_control_delta_absent_from_runtime",
        "proof_rows": proof_rows,
        "proof_sha256": canonical_sha256(proof_rows),
        "site_count": len(source_only),
        "site_sha256": site_digest(source_only),
    }


def resolve_union(
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    predecessor_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    owner_maps = [
        {str(row["coordinate"]): reviewed_translation(row) for row in rows}
        for rows in chunk_rows
    ]
    owner_coordinates = [set(mapping) for mapping in owner_maps]
    owner_roots = [
        {coordinate_root(value) for value in coordinates}
        for coordinates in owner_coordinates
    ]
    for left in range(len(CHUNK_BUILDERS)):
        for right in range(left + 1, len(CHUNK_BUILDERS)):
            require(
                not owner_coordinates[left] & owner_coordinates[right],
                "chunk decision coordinates overlap",
            )
            require(
                not owner_roots[left] & owner_roots[right],
                "chunk decision roots overlap",
            )
    reference_union: dict[str, str] | None = None
    for order in itertools.permutations(range(len(CHUNK_BUILDERS))):
        resolved: dict[str, str] = {}
        for owner in order:
            resolved.update(owner_maps[owner])
        if reference_union is None:
            reference_union = resolved
        require(resolved == reference_union, "owner permutation changed the union")
    require(reference_union is not None, "empty owner union")
    union = reference_union
    require(
        len(union) == EXPECTED_DECISION_ROWS
        and len({coordinate_root(value) for value in union})
        == EXPECTED_DECISION_ROOTS,
        "decision union count drifted",
    )

    source_rows = {
        str(row["coordinate"]): row
        for rows in chunk_rows
        for row in rows
    }
    promotions: set[str] = set()
    renewals: set[str] = set()
    overrides: set[str] = set()
    actions: dict[str, str] = {}
    for coordinate, body in union.items():
        row = source_rows[coordinate]
        predecessor = official[("pk_msggame", coordinate)]
        pending = predecessor.get("runtime_review") == "pending"
        changed = body != predecessor.get("translation")
        if pending:
            promotions.add(coordinate)
        else:
            require(
                predecessor.get("runtime_review") == "verified",
                "decision predecessor state is neither pending nor verified",
            )
            renewals.add(coordinate)
        if changed:
            overrides.add(coordinate)
        if pending:
            action = (
                "translation_override_and_runtime_promotion"
                if changed else "runtime_promotion"
            )
        else:
            action = (
                "translation_override_and_verification_renewal"
                if changed else "verification_renewal"
            )
        require(action == row["action"], "chunk action disagrees with FC157A")
        actions[coordinate] = action
    action_counts = dict(sorted(Counter(actions.values()).items()))
    require(
        len(promotions) == EXPECTED_PROMOTIONS
        and len(renewals) == EXPECTED_RENEWALS
        and len(overrides) == EXPECTED_OVERRIDES
        and action_counts == EXPECTED_ACTION_COUNTS,
        "consolidated disposition drifted",
    )

    predecessor = {
        str(row["coordinate"]): str(row["translation"])
        for row in predecessor_rows
    }
    overlap = set(union) & set(predecessor)
    supersession = {
        coordinate
        for coordinate in overlap
        if union[coordinate] != predecessor[coordinate]
    }
    require(
        len(overlap) == EXPECTED_PREDECESSOR_OVERLAPS
        and len(supersession) == EXPECTED_PREDECESSOR_SUPERSESSIONS,
        "predecessor overlap topology drifted",
    )
    return {
        "action_by_coordinate": actions,
        "action_counts": action_counts,
        "final_translation": union,
        "overrides": overrides,
        "owner_maps": owner_maps,
        "predecessor_overlap": overlap,
        "predecessor_supersession": supersession,
        "promotions": promotions,
        "renewals": renewals,
        "source_rows": source_rows,
        "union": set(union),
    }


def validate_rows_and_rebuild(
    official_rows: Sequence[Mapping[str, Any]],
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    union: Mapping[str, Any],
) -> dict[str, Any]:
    steam_root = RANKING.DEFAULT_STEAM_ROOT
    current_path = steam_root / "MSG_PK" / "JP" / "msggame.bin"
    pristine_path = (
        steam_root
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    )
    live_path = Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
    )
    require(
        current_path.is_file()
        and pristine_path.is_file()
        and current_path.resolve() != live_path.resolve(),
        "development archive is absent or resolves to live Steam",
    )
    require(
        sha256_file(current_path) == EXPECTED_CURRENT_SHA256
        and sha256_file(pristine_path) == EXPECTED_PRISTINE_SHA256,
        "current/pristine archive drifted",
    )
    current_blob = current_path.read_bytes()
    pristine_blob = pristine_path.read_bytes()
    replacements = {
        parse_coordinate(str(row["coordinate"])): str(row["translation"])
        for row in official_rows
        if row.get("resource") == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    official_blob = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    require(
        sha256_bytes(official_blob) == EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "official candidate reconstruction drifted",
    )

    def records(blob: bytes) -> dict[tuple[int, int], Any]:
        return ENGINE.archive_records(ENGINE.parse_packed_msggame(blob).archive)

    current_records = records(current_blob)
    source_records = records(pristine_blob)
    official_records = records(official_blob)
    for coordinate, action in union["action_by_coordinate"].items():
        row = union["source_rows"][coordinate]
        body = union["final_translation"][coordinate]
        predecessor = official[("pk_msggame", coordinate)]
        require(
            str(row["resource"]) == "pk_msggame"
            and str(row["fresh_semantic_review"]) == "approved"
            and str(row["historical_factuality_review"]) == "approved"
            and str(row["speaker_tone_review"]) == "approved"
            and str(row["runtime_review"]) == "verified"
            and str(row["layout_review"])
            == "current_relative_raw_g1n_nonexpanding",
            "review approval field drifted",
        )
        require(
            action in RECOGNIZED_ACTIONS
            and utf16_sha256(body) == reviewed_translation_sha256(row),
            "reviewed translation hash drifted",
        )
        require(
            utf16_sha256(literal_text(current_records, coordinate))
            == row["current_ko_utf16le_sha256"],
            "current literal hash drifted",
        )
        require(
            utf16_sha256(literal_text(source_records, coordinate))
            == row["jp_source_utf16le_sha256"],
            "JP source literal hash drifted",
        )
        predecessor_body = str(predecessor["translation"])
        require(
            body.count("\n") == predecessor_body.count("\n"),
            "literal linebreak count changed",
        )
        require(
            without_outer_whitespace(ENGINE.protected_signature(body))
            == without_outer_whitespace(
                ENGINE.protected_signature(predecessor_body)
            ),
            "protected runtime token signature changed",
        )

    final_blob = ENGINE.rebuild_packed_with_literals(
        official_blob,
        {
            parse_coordinate(coordinate): body
            for coordinate, body in union["final_translation"].items()
        },
    )
    final_sha256 = sha256_bytes(final_blob)
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        final_blob,
        {
            parse_coordinate(coordinate):
                str(official[("pk_msggame", coordinate)]["translation"])
            for coordinate in union["union"]
        },
    )
    require(reverse_blob == official_blob, "reverse overlay is not exact")
    final_records = records(final_blob)
    override_roots = {
        tuple(map(int, coordinate_root(value).split(":")))
        for value in union["overrides"]
    }
    actual_changed_roots = {
        root
        for root in official_records
        if official_records[root].data != final_records[root].data
    }
    require(
        actual_changed_roots == override_roots,
        "candidate changed-root universe drifted",
    )
    for root in override_roots:
        require(
            ENGINE.record_gap_bytes(official_records[root])
            == ENGINE.record_gap_bytes(final_records[root]),
            f"record control gaps changed: {root}",
        )
    return {
        "candidate_records": official_records,
        "changed_root_count": len(override_roots),
        "current_records": current_records,
        "final_candidate_sha256": final_sha256,
        "reverse_candidate_sha256": sha256_bytes(reverse_blob),
        "source_records": source_records,
    }


def build_outputs() -> dict[Path, bytes]:
    validate_immutable_inputs()
    assignment = load_json(ASSIGNMENT_PRIVATE_PATH)
    assignment_public = load_json(ASSIGNMENT_PUBLIC_PATH)
    require(
        assignment.get("schema") == ASSIGNMENT_PRIVATE_SCHEMA
        and assignment_public.get("status") == "PASS",
        "assignment contract drifted",
    )
    chunk_rows = [load_jsonl(path) for path in CHUNK_DECISIONS]
    evidence = validate_chunk_evidence(assignment, chunk_rows)
    official_rows, official = load_official_rows()
    predecessor_rows = load_jsonl(PREDECESSOR_DECISIONS_PATH)
    union = resolve_union(chunk_rows, official, predecessor_rows)
    candidate = validate_rows_and_rebuild(official_rows, official, union)
    source_only = source_only_runtime_delta_proof(
        assignment,
        candidate["current_records"],
        candidate["candidate_records"],
        candidate["source_records"],
    )

    normalized_rows = []
    for coordinate in sorted(union["union"], key=parse_coordinate):
        source_row = union["source_rows"][coordinate]
        body = union["final_translation"][coordinate]
        chunk_id = next(
            chunk
            for chunk, owner in enumerate(union["owner_maps"])
            if coordinate in owner
        )
        normalized_rows.append(
            {
                UPDATE_ACTION_FIELD: union["action_by_coordinate"][coordinate],
                "coordinate": coordinate,
                "fresh_semantic_review": "approved",
                "historical_factuality_review": "approved",
                "jp_source_utf16le_sha256":
                    source_row["jp_source_utf16le_sha256"],
                "layout_review": "current_relative_raw_g1n_nonexpanding",
                "method": METHOD,
                "official_predecessor_utf16le_sha256": utf16_sha256(
                    str(official[("pk_msggame", coordinate)]["translation"])
                ),
                "owner_chunk": chunk_id,
                "resource": "pk_msggame",
                "runtime_review": "verified",
                "schema": PRIVATE_DECISION_SCHEMA,
                "speaker_tone_review": "approved",
                "translation": body,
                "translation_utf16le_sha256": utf16_sha256(body),
            }
        )
    decisions_content = serialized_jsonl(normalized_rows)
    decisions_sha256 = sha256_bytes(decisions_content)

    digests = {
        "decision_coordinate_sha256": coordinate_digest(union["union"]),
        "override_coordinate_sha256": coordinate_digest(union["overrides"]),
        "predecessor_overlap_coordinate_sha256": coordinate_digest(
            union["predecessor_overlap"]
        ),
        "predecessor_supersession_coordinate_sha256": coordinate_digest(
            union["predecessor_supersession"]
        ),
        "promotion_coordinate_sha256": coordinate_digest(union["promotions"]),
        "renewal_coordinate_sha256": coordinate_digest(union["renewals"]),
        "source_only_proof_sha256": source_only["proof_sha256"],
    }
    frozen = {
        "private_decisions": decisions_sha256,
        "final_candidate": candidate["final_candidate_sha256"],
        "decision_coordinates": digests["decision_coordinate_sha256"],
        "promotion_coordinates": digests["promotion_coordinate_sha256"],
        "renewal_coordinates": digests["renewal_coordinate_sha256"],
        "override_coordinates": digests["override_coordinate_sha256"],
        "predecessor_overlap_coordinates":
            digests["predecessor_overlap_coordinate_sha256"],
        "predecessor_supersession_coordinates":
            digests["predecessor_supersession_coordinate_sha256"],
        "source_only_proof": digests["source_only_proof_sha256"],
    }
    for label, actual in frozen.items():
        expected = EXPECTED_OUTPUT_SHA256[label]
        if expected is not None:
            require(expected == actual, f"frozen output drifted: {label}")

    evidence_payload = {
        "counts": {
            "action_counts": union["action_counts"],
            "changed_roots": candidate["changed_root_count"],
            "decision_roots": EXPECTED_DECISION_ROOTS,
            "decision_rows": len(union["union"]),
            "overrides": len(union["overrides"]),
            "predecessor_overlaps": len(union["predecessor_overlap"]),
            "predecessor_supersessions":
                len(union["predecessor_supersession"]),
            "promotions": len(union["promotions"]),
            "renewals": len(union["renewals"]),
            "reviewed_sites": EXPECTED_REVIEWED_SITES,
            "source_only_actions": source_only["actions"],
            "source_only_sites": source_only["site_count"],
        },
        "digests": digests,
        "exact_maps": {
            "overrides": sorted(union["overrides"], key=parse_coordinate),
            "predecessor_overlaps": sorted(
                union["predecessor_overlap"], key=parse_coordinate
            ),
            "predecessor_supersessions": sorted(
                union["predecessor_supersession"], key=parse_coordinate
            ),
            "promotions": sorted(union["promotions"], key=parse_coordinate),
            "renewals": sorted(union["renewals"], key=parse_coordinate),
            "source_only_sites": source_only["proof_rows"],
        },
        "guards": {
            "candidate_sha256": candidate["final_candidate_sha256"],
            "decision_file_sha256": decisions_sha256,
            "reverse_candidate_sha256": candidate["reverse_candidate_sha256"],
        },
        "inputs": {
            "assignment_sha256":
                EXPECTED_INPUT_SHA256["assignment_private"],
            "chunk_decision_sha256": [
                EXPECTED_INPUT_SHA256[f"chunk{chunk}_decisions"]
                for chunk in range(len(CHUNK_BUILDERS))
            ],
            "chunk_evidence_sha256": [
                EXPECTED_INPUT_SHA256[f"chunk{chunk}_evidence"]
                for chunk in range(len(CHUNK_BUILDERS))
            ],
            "official_ledger_sha256":
                EXPECTED_INPUT_SHA256["official_ledger"],
            "predecessor_decisions_sha256":
                EXPECTED_INPUT_SHA256["predecessor_decisions"],
        },
        "method": METHOD,
        "proof": {
            "all_owner_permutations_identical": True,
            "all_reviewed_lines_current_relative_nonexpanding": True,
            "all_reviewed_sites_covered": True,
            "chunk_coordinate_and_root_sets_disjoint": True,
            "literal_linebreak_counts_preserved": True,
            "predecessor_supersessions_explicit": True,
            "protected_runtime_tokens_preserved": True,
            "record_control_gaps_preserved": True,
            "reverse_overlay_exact": True,
            "source_only_runtime_delta_actions_zero": True,
        },
        "privacy": {
            "classification": "private_source_bearing",
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
        "schema": PRIVATE_EVIDENCE_SCHEMA,
        "source_only_runtime_delta_proof": source_only,
        "upstream_evidence_summary": [
            {
                "chunk_id": chunk,
                "decision_rows": EXPECTED_CHUNK_ROWS[chunk],
                "evidence_sha256":
                    EXPECTED_INPUT_SHA256[f"chunk{chunk}_evidence"],
                "site_count": EXPECTED_CHUNK_SITES[chunk],
            }
            for chunk in range(len(CHUNK_BUILDERS))
        ],
    }
    evidence_content = serialized_json(evidence_payload)
    evidence_sha256 = sha256_bytes(evidence_content)
    if EXPECTED_OUTPUT_SHA256["private_evidence"] is not None:
        require(
            evidence_sha256 == EXPECTED_OUTPUT_SHA256["private_evidence"],
            "frozen private evidence drifted",
        )

    common_public = {
        "artifacts": {
            "private_decisions_basename": PRIVATE_DECISIONS_OUTPUT.name,
            "private_decisions_schema": PRIVATE_DECISION_SCHEMA,
            "private_evidence_basename": PRIVATE_EVIDENCE_OUTPUT.name,
        },
        "candidate": {
            "official_predecessor_sha256": EXPECTED_OFFICIAL_CANDIDATE_SHA256,
            "reviewed_sha256": candidate["final_candidate_sha256"],
            "reverse_overlay_sha256": candidate["reverse_candidate_sha256"],
        },
        "guards": {
            "candidate_call_site_sha256": EXPECTED_CANDIDATE_SITE_SHA256,
            "decision_file_sha256": decisions_sha256,
            "decision_coordinate_sha256":
                digests["decision_coordinate_sha256"],
            "override_coordinate_sha256":
                digests["override_coordinate_sha256"],
            "promotion_coordinate_sha256":
                digests["promotion_coordinate_sha256"],
            "private_evidence_sha256": evidence_sha256,
            "renewal_coordinate_sha256":
                digests["renewal_coordinate_sha256"],
            "source_only_proof_sha256":
                digests["source_only_proof_sha256"],
            "source_only_site_sha256": EXPECTED_SOURCE_ONLY_SHA256,
        },
        "inputs": {
            "assignment_sha256":
                EXPECTED_INPUT_SHA256["assignment_private"],
            "chunk_decision_sha256": [
                EXPECTED_INPUT_SHA256[f"chunk{chunk}_decisions"]
                for chunk in range(len(CHUNK_BUILDERS))
            ],
            "chunk_evidence_sha256": [
                EXPECTED_INPUT_SHA256[f"chunk{chunk}_evidence"]
                for chunk in range(len(CHUNK_BUILDERS))
            ],
            "official_ledger_sha256":
                EXPECTED_INPUT_SHA256["official_ledger"],
            "official_public_checkpoint_sha256":
                EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256,
            "predecessor_candidate_sha256":
                EXPECTED_OFFICIAL_CANDIDATE_SHA256,
            "predecessor_decisions_sha256":
                EXPECTED_INPUT_SHA256["predecessor_decisions"],
        },
        "method": METHOD,
        "privacy": {
            "contains_commercial_source_text": False,
            "contains_dialogue_bodies": False,
            "contains_exact_coordinates": False,
            "contains_translations": False,
            "private_artifacts_stay_below_tmp": True,
            "shared_integration_mutated": False,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "status": "PASS",
        "steam_write_performed": False,
    }
    coverage = {
        **json.loads(json.dumps(common_public)),
        "proof": {
            "all_230_candidate_sites_reviewed": True,
            "all_owner_permutations_identical": True,
            "chunk_coordinate_and_root_sets_disjoint": True,
            "current_relative_raw_g1n_nonexpanding": True,
            "literal_linebreak_counts_preserved": True,
            "predecessor_supersessions_explicit": True,
            "protected_runtime_tokens_preserved": True,
            "record_control_gaps_preserved": True,
            "reverse_overlay_exact": True,
            "source_only_13_absent_from_current_and_candidate": True,
            "source_only_runtime_delta_actions_zero": True,
        },
        "result": {
            "candidate_call_site_sha256": EXPECTED_CANDIDATE_SITE_SHA256,
            "changed_roots": candidate["changed_root_count"],
            "decision_roots": EXPECTED_DECISION_ROOTS,
            "decision_rows": EXPECTED_DECISION_ROWS,
            "predecessor_overlaps": EXPECTED_PREDECESSOR_OVERLAPS,
            "predecessor_supersessions": EXPECTED_PREDECESSOR_SUPERSESSIONS,
            "reviewed_sites": EXPECTED_REVIEWED_SITES,
            "source_only_actions": 0,
            "source_only_disposition":
                "pristine_only_control_delta_excluded_no_action",
            "source_only_sites": EXPECTED_SOURCE_ONLY_SITES,
            "source_only_site_sha256": EXPECTED_SOURCE_ONLY_SHA256,
            "source_call_sites": EXPECTED_SOURCE_SITES,
            "source_call_site_sha256": EXPECTED_SOURCE_SITE_SHA256,
        },
        "schema": PUBLIC_COVERAGE_SCHEMA,
    }
    coverage["guards"]["payload_without_guard_sha256"] = canonical_sha256(
        coverage
    )
    promotion = {
        **json.loads(json.dumps(common_public)),
        "result": {
            "action_counts": union["action_counts"],
            "decision_rows": EXPECTED_DECISION_ROWS,
            "overrides": EXPECTED_OVERRIDES,
            "pending_after": EXPECTED_PENDING_AFTER,
            "pending_before": EXPECTED_PENDING_BEFORE,
            "promotions": EXPECTED_PROMOTIONS,
            "renewals": EXPECTED_RENEWALS,
            "source_only_actions": 0,
        },
        "schema": PUBLIC_PROMOTION_SCHEMA,
    }
    promotion["guards"]["payload_without_guard_sha256"] = canonical_sha256(
        promotion
    )
    assert_source_free(coverage)
    assert_source_free(promotion)
    coverage_content = serialized_json(coverage)
    promotion_content = serialized_json(promotion)
    for label, content in (
        ("public_coverage", coverage_content),
        ("public_promotion", promotion_content),
    ):
        expected = EXPECTED_OUTPUT_SHA256[label]
        if expected is not None:
            require(sha256_bytes(content) == expected, f"{label} drifted")
    return {
        PRIVATE_DECISIONS_OUTPUT: decisions_content,
        PRIVATE_EVIDENCE_OUTPUT: evidence_content,
        PUBLIC_COVERAGE_OUTPUT: coverage_content,
        PUBLIC_PROMOTION_OUTPUT: promotion_content,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    outputs = build_outputs()
    if args.check:
        for path, content in outputs.items():
            require(
                path.is_file() and path.read_bytes() == content,
                f"consolidated output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        json.dumps(
            {
                "candidate_sha256":
                    load_json(PUBLIC_PROMOTION_OUTPUT)["candidate"][
                        "reviewed_sha256"
                    ] if args.check else "written",
                "decision_rows": EXPECTED_DECISION_ROWS,
                "pending_after": EXPECTED_PENDING_AFTER,
                "promotions": EXPECTED_PROMOTIONS,
                "source_only_actions": 0,
                "status": "PASS",
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
