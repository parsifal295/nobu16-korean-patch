#!/usr/bin/env python3
"""Build the deterministic private review assignment for PK selector 1174.

The assignment is planning-only.  Exact call sites, roots, and pending
coordinates remain below ``tmp``; the tracked report contains only counts and
cryptographic digests.  The official 81B4 ledger is the semantic predecessor,
while the committed 568/1096 cross-family closure is used to partition the
242-row ceiling into 18 already-owned and 224 disjoint rows.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
RANKING_BUILDER_PATH = (
    WORKSTREAM / "build_pk_next_selector_family_ranking_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP / "pk_next_selector_family_ranking.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking.source_free.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
)
CROSS_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_selector568_1096_cross_family_consolidated_closure_v1.py"
)
CROSS_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_1096_cross_family_consolidated_closure_decisions.private.v1.jsonl"
)
CROSS_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector568_1096_cross_family_consolidated_closure_coverage.v1.json"
)
CROSS_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector568_1096_cross_family_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector1174_assignment.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1174_assignment_coverage.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector1174-assignment.private.v1"
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-selector1174-assignment-coverage.v1"
)
METHOD = (
    "official81b4_selector1174_fixed7way_cross_family_partitioned_assignment"
)
SELECTOR = 1174
TERMINALS = tuple(range(2644, 2651))
CHUNK_COUNT = 2
MIN_CHUNK_SITES = 45
MAX_CHUNK_SITES = 70

EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_RANKING_BUILDER_SHA256 = (
    "19D8F10FC3995AD05A39AD12CD554292A47BF4A1AB572D28359130326FA69391"
)
EXPECTED_RANKING_PRIVATE_SHA256 = (
    "DBEAF9685FAF9F2987DF0267DA40139FF6520F20A02CD1748CCD4280FC591DDE"
)
EXPECTED_RANKING_PUBLIC_SHA256 = (
    "395BEC89F4D37D1F2272145DA8E250B4FF973DBE49818A133242C493A0354541"
)
EXPECTED_CROSS_COMMIT = "d2a89f11e9c0bb75e03e9ccc19ce0ca548fa45e8"
EXPECTED_CROSS_BUILDER_SHA256 = (
    "C9976A86F7ABA023A5F575BBFCCDA20BF2C9A7E8329C0EAFFC59633A2DD422EE"
)
EXPECTED_CROSS_DECISIONS_SHA256 = (
    "E3C97823C70FBD441D420722AE306E2DEBE62CB8919FBA5426A91BC00DCBA5ED"
)
EXPECTED_CROSS_COVERAGE_SHA256 = (
    "2F3D7A91874B373568AE38BDB0C8202A7AF46ACFB36BE8236BD4D61BA3018F36"
)
EXPECTED_CROSS_PROMOTION_REPORT_SHA256 = (
    "FC08FCA8A03B2D5BC10C113AED16D76E1A0463165F20047E80BBF554DCCF7CF3"
)
EXPECTED_PK_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PK_PRISTINE_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_CONTEXT_SHA256 = {
    "en": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "sc": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "tc": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}
EXPECTED_OFFICIAL_PENDING_ROWS = 7_896
EXPECTED_CROSS_PROMOTIONS = 431
EXPECTED_CROSS_PROMOTION_SHA256 = (
    "71C1D381242BE1492BD6B7E75E7EB589690B07A0F022B02ECCC29B21B1CE0419"
)
EXPECTED_SITE_COUNT = 115
EXPECTED_SITE_SHA256 = (
    "C84EE28B01FF367CF261E73EAB77C4ACCB260A655EEBB75AF18E5BDC00F7C1C4"
)
EXPECTED_ROOT_COUNT: int | None = 113
EXPECTED_ROOT_SHA256: str | None = (
    "BBF4B9D8EEDB8789818A72ABAA8E5B1D1A9F87344133BB1654B81B7E0D7A7243"
)
EXPECTED_SOURCE_SITE_COUNT = 121
EXPECTED_SOURCE_SITE_SHA256: str | None = (
    "5ECADA7EE96C59F32FC5F83D0D70668595F3699ADD029D1D6F4A841C032AA264"
)
EXPECTED_SOURCE_ROOT_COUNT: int | None = 119
EXPECTED_SOURCE_ROOT_SHA256: str | None = (
    "0CD552CB8BD669F3C341714BA653BC0BAE5A30151D0DD11D9119D2E3551A27A9"
)
EXPECTED_SOURCE_ONLY_SITES = 6
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "658C87A219EB3A578F1CB67DE4DF4D9EDB57607BCBEF367C23BC7A48E8C1FC0B"
)
EXPECTED_DIRECT_PENDING_SITES = 82
EXPECTED_DIRECT_PENDING_SITE_SHA256: str | None = (
    "C992546899732969A08325C0D34C444F6E7D0279B2EBB8970BBFFEE749206F01"
)
EXPECTED_DIRECT_PENDING_ROOTS = 80
EXPECTED_DIRECT_PENDING_ROOT_SHA256: str | None = (
    "13AE30B601D25AD3CAB61E79559B9DD38F130E96B5E32E18785B28F76FCB7AE2"
)
EXPECTED_POTENTIAL_ROWS = 242
EXPECTED_POTENTIAL_SHA256 = (
    "A8B84921C8E687CB4BF6B5A89520434CAB807D45978C5FC4AE1F6A930CCB0AD5"
)
EXPECTED_OVERLAP_ROWS = 18
EXPECTED_OVERLAP_SHA256 = (
    "306D31747A885B3F335763574AF16F9A56CC6E9B0A83061664AAB7653064DFC6"
)
EXPECTED_DISJOINT_ROWS = 224
EXPECTED_DISJOINT_SHA256 = (
    "03FB8767A2410C66C5A8F586BF92E052B8D89BA446E531834B3ADCAE42C90FBA"
)
EXPECTED_DISPATCH_NODE_SHA256 = (
    "CA8D458D99F2C752EE61A837838E0DB53025C29A02B18DFD19EDD34A9C15171E"
)
EXPECTED_DISPATCH_EDGE_SHA256 = (
    "186BC73587CC0BECB41813CC1F4246DB6CA04832D3A1209864CBC2244FA79ABD"
)
EXPECTED_TERMINAL_SHA256 = (
    "286E027448B602D287D0542B42129453C1BBD00F21C918D470A4A24DA412775A"
)
EXPECTED_CUTS: tuple[int, ...] | None = (55, 115)
EXPECTED_CHUNK_COUNTS: tuple[tuple[int, int, int, int, int], ...] | None = (
    (55, 54, 107, 5, 1376),
    (60, 59, 135, 13, 1396),
)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "C28EAD54791ED8D2315DA967F7A2DB9F92B7ECB5DA7347B71C079FF2E260ED11"
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "07B892C55CAB031BDE414726FD301F03441E181C228D970003A834612ACABC10"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "6979EE31FB6AE4C046892E0785A61CC1D57F58415EB3B3D55601944F148A2CB2"
)


class AssignmentError(ValueError):
    """Raised when selector-1174 assignment evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RANKING = load_module(
    RANKING_BUILDER_PATH, "pk_selector1174_assignment_ranking_v1"
)
ENGINE = RANKING.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def serialized_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    )


def coordinate_digest(values: Iterable[str]) -> str:
    return RANKING.coordinate_digest(values)


def root_digest(values: Iterable[tuple[int, int]]) -> str:
    return RANKING.root_digest(values)


def site_digest(values: Iterable[str]) -> str:
    return RANKING.site_digest(values)


def adjacent_literals(
    records: Mapping[tuple[int, int], Any], site: str
) -> tuple[str, str]:
    block_id, record_id, gap_id, _offset = RANKING.site_key(site)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    return (
        (
            literals[gap_id - 1].text
            if gap_id and gap_id - 1 < len(literals)
            else ""
        ),
        literals[gap_id].text if gap_id < len(literals) else "",
    )


def character_width(character: str) -> int:
    if unicodedata.category(character) == "Cc":
        return 0
    return (
        48
        if unicodedata.east_asian_width(character) in {"W", "F", "A"}
        else 24
    )


def line_widths(value: str) -> tuple[int, ...]:
    return tuple(
        sum(character_width(character) for character in line)
        for line in value.split("\n")
    )


def parse_cross_promotions(
    pending_coordinates: set[str],
) -> set[str]:
    result: set[str] = set()
    row_count = 0
    for line in CROSS_DECISIONS_PATH.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row_count += 1
        row = json.loads(line)
        action = str(
            row.get("selector568_1096_cross_family_update_action", "")
        )
        coordinate = str(row["coordinate"])
        if "runtime_promotion" in action and coordinate in pending_coordinates:
            result.add(coordinate)
    require(row_count == 920, f"cross-family decision row drifted: {row_count}")
    require(
        len(result) == EXPECTED_CROSS_PROMOTIONS
        and coordinate_digest(result) == EXPECTED_CROSS_PROMOTION_SHA256,
        "cross-family current-pending promotion union drifted",
    )
    return result


def load_records() -> tuple[
    dict[tuple[int, int], Any],
    dict[tuple[int, int], Any],
    dict[tuple[int, int], Any],
    dict[str, dict[tuple[int, int], Any]],
    dict[tuple[int, int], set[str]],
]:
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
    context_paths = {
        language: steam_root / "MSG_PK" / language.upper() / "msggame.bin"
        for language in ("en", "sc", "tc")
    }
    require(
        sha256_file(current_path) == EXPECTED_PK_CURRENT_SHA256
        and sha256_file(pristine_path) == EXPECTED_PK_PRISTINE_SHA256,
        "PK current/pristine input drifted",
    )
    require(
        {
            language: sha256_file(path)
            for language, path in context_paths.items()
        }
        == EXPECTED_CONTEXT_SHA256,
        "PK multilingual context input drifted",
    )
    replacements, pending_by_root, _rows = RANKING.load_official_ledger(
        OFFICIAL_LEDGER_PATH
    )
    current_blob = current_path.read_bytes()
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_PK_CANDIDATE_SHA256,
        "official candidate reconstruction drifted",
    )
    candidate = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate_blob).archive
    )
    current = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(current_blob).archive
    )
    source = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(pristine_path.read_bytes()).archive
    )
    contexts = {
        language: ENGINE.archive_records(
            ENGINE.parse_packed_msggame(path.read_bytes()).archive
        )
        for language, path in context_paths.items()
    }
    require(
        set(candidate)
        == set(current)
        == set(source)
        == set(contexts["en"])
        == set(contexts["sc"])
        == set(contexts["tc"]),
        "PK multilingual record universe drifted",
    )
    return candidate, current, source, contexts, pending_by_root


def build_site_rows(
    *,
    sites: Sequence[str],
    candidate: Mapping[tuple[int, int], Any],
    current: Mapping[tuple[int, int], Any],
    source: Mapping[tuple[int, int], Any],
    contexts: Mapping[str, Mapping[tuple[int, int], Any]],
) -> list[dict[str, Any]]:
    terminal_candidate: dict[int, str] = {}
    terminal_current: dict[int, str] = {}
    for terminal in TERMINALS:
        candidate_literals = ENGINE.parse_record_literals(
            candidate[(0, terminal)]
        )
        current_literals = ENGINE.parse_record_literals(current[(0, terminal)])
        require(
            len(candidate_literals) == len(current_literals) == 1,
            f"terminal literal shape drifted: {terminal}",
        )
        terminal_candidate[terminal] = candidate_literals[0].text
        terminal_current[terminal] = current_literals[0].text

    result: list[dict[str, Any]] = []
    language_records = {"jp": source, **contexts}
    for ordinal, site in enumerate(sites):
        block_id, record_id, gap_id, _offset = RANKING.site_key(site)
        left, right = adjacent_literals(candidate, site)
        current_left, current_right = adjacent_literals(current, site)
        language_available = {
            language: any(adjacent_literals(records, site))
            for language, records in language_records.items()
        }
        gap = ENGINE.record_gap_bytes(candidate[(block_id, record_id)])[gap_id]
        control_count = sum(1 for _ in RANKING.CONTROL_RE.finditer(gap))
        layout_risk = False
        maximum_delta = 0
        for terminal in TERMINALS:
            candidate_widths = line_widths(
                left + terminal_candidate[terminal] + right
            )
            current_widths = line_widths(
                current_left + terminal_current[terminal] + current_right
            )
            if len(candidate_widths) != len(current_widths):
                layout_risk = True
            deltas = [
                candidate_width - current_width
                for candidate_width, current_width in zip(
                    candidate_widths, current_widths
                )
            ]
            maximum_delta = max(maximum_delta, max(deltas, default=0))
            layout_risk = layout_risk or any(delta > 0 for delta in deltas)
        flags = {
            "grammar_right_boundary": bool(right),
            "layout_relative_expansion": layout_risk,
            "multi_control_gap": control_count > 1,
            "protected_outer_space": (
                (bool(left) and left.endswith(" "))
                or (bool(right) and right.startswith(" "))
            ),
        }
        missing_auxiliary = sum(
            not language_available[language] for language in ("en", "sc", "tc")
        )
        workload_weight = (
            10
            + 4 * int(flags["grammar_right_boundary"])
            + 7 * int(flags["layout_relative_expansion"])
            + 6 * int(flags["multi_control_gap"])
            + 8 * int(flags["protected_outer_space"])
            + 3 * missing_auxiliary
        )
        result.append(
            {
                "flags": flags,
                "language_available": language_available,
                "left_coordinate": (
                    f"{block_id}:{record_id}:{gap_id - 1}"
                    if gap_id
                    else None
                ),
                "maximum_positive_raw_g1n_delta_px": maximum_delta,
                "ordinal": ordinal,
                "root": f"{block_id}:{record_id}",
                "site": site,
                "workload_weight": workload_weight,
            }
        )
    return result


def balanced_cuts(rows: Sequence[Mapping[str, Any]]) -> tuple[int, ...]:
    boundaries = [
        index
        for index in range(1, len(rows))
        if rows[index - 1]["root"] != rows[index]["root"]
    ]
    total_weight = sum(int(row["workload_weight"]) for row in rows)
    target_weight = total_weight / CHUNK_COUNT
    target_count = len(rows) / CHUNK_COUNT
    candidates: list[tuple[float, int]] = []
    for cut in boundaries:
        if not (
            MIN_CHUNK_SITES <= cut <= MAX_CHUNK_SITES
            and MIN_CHUNK_SITES <= len(rows) - cut <= MAX_CHUNK_SITES
        ):
            continue
        left_weight = sum(
            int(row["workload_weight"]) for row in rows[:cut]
        )
        right_weight = total_weight - left_weight
        cost = (
            (left_weight - target_weight) ** 2
            + (right_weight - target_weight) ** 2
            + 2 * (cut - target_count) ** 2
            + 2 * (len(rows) - cut - target_count) ** 2
        )
        candidates.append((cost, cut))
    require(bool(candidates), "no valid root-preserving balanced cut")
    cut = min(candidates)[1]
    cuts = (cut, len(rows))
    if EXPECTED_CUTS is not None:
        require(cuts == EXPECTED_CUTS, f"assignment cuts drifted: {cuts}")
    return cuts


def assert_source_free(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "public assignment contains CJK dialogue text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public assignment contains an exact coordinate",
    )
    require(
        '"translation"' not in serialized,
        "public assignment contains a translation field",
    )


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    immutable = {
        OFFICIAL_LEDGER_PATH: EXPECTED_OFFICIAL_LEDGER_SHA256,
        RANKING_BUILDER_PATH: EXPECTED_RANKING_BUILDER_SHA256,
        RANKING_PRIVATE_PATH: EXPECTED_RANKING_PRIVATE_SHA256,
        RANKING_PUBLIC_PATH: EXPECTED_RANKING_PUBLIC_SHA256,
        CROSS_BUILDER_PATH: EXPECTED_CROSS_BUILDER_SHA256,
        CROSS_DECISIONS_PATH: EXPECTED_CROSS_DECISIONS_SHA256,
        CROSS_COVERAGE_PATH: EXPECTED_CROSS_COVERAGE_SHA256,
        CROSS_PROMOTION_PATH: EXPECTED_CROSS_PROMOTION_REPORT_SHA256,
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable assignment input drifted: {path}",
        )
    steam_path = RANKING.DEFAULT_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
    steam_before = sha256_file(steam_path)

    ranking_private = json.loads(
        RANKING_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    ranking_public = json.loads(
        RANKING_PUBLIC_PATH.read_text(encoding="utf-8")
    )
    target = next(
        row
        for row in ranking_private["direct_targets"]
        if row["target_coordinate"] == f"0:{SELECTOR}"
    )
    ranked = next(
        row
        for row in ranking_public["ranking"]
        if row["selector_coordinate"] == f"0:{SELECTOR}"
    )
    require(
        ranking_public["recommendation"]["selector_coordinate"]
        == f"0:{SELECTOR}"
        and target["classification"]
        == "eligible_fixed_seven_way_selector",
        "selector-1174 is no longer the ranked eligible recommendation",
    )

    candidate, current, source, contexts, pending_by_root = load_records()
    candidate_edges = RANKING.graph_edges(candidate)
    source_edges = RANKING.graph_edges(source)
    candidate_site_map = RANKING.candidate_call_sites(candidate_edges)
    source_site_map = RANKING.candidate_call_sites(source_edges)
    sites = candidate_site_map[(0, SELECTOR)]
    source_sites = source_site_map[(0, SELECTOR)]
    candidate_roots = {
        RANKING.site_key(site)[:2] for site in sites
    }
    source_roots = {
        RANKING.site_key(site)[:2] for site in source_sites
    }
    source_only = set(source_sites) - set(sites)
    candidate_only = set(sites) - set(source_sites)
    direct_pending_sites = [
        site
        for site in sites
        if RANKING.site_key(site)[:2] in pending_by_root
    ]
    direct_pending_roots = {
        RANKING.site_key(site)[:2] for site in direct_pending_sites
    }
    reachable_pending_roots = {
        RANKING.parse_root(root)
        for root in target["reachable_pending_roots"]
    }
    potential = {
        coordinate
        for root in reachable_pending_roots
        for coordinate in pending_by_root[root]
    }
    all_pending = {
        coordinate
        for coordinates in pending_by_root.values()
        for coordinate in coordinates
    }
    cross_promotions = parse_cross_promotions(all_pending)
    overlap = potential & cross_promotions
    disjoint = potential - cross_promotions
    shape = RANKING.family_shape(
        candidate_edges, source_edges, (0, SELECTOR)
    )

    optional_guards = (
        (EXPECTED_ROOT_COUNT, len(candidate_roots), "candidate root count"),
        (EXPECTED_ROOT_SHA256, root_digest(candidate_roots), "candidate root"),
        (
            EXPECTED_SOURCE_SITE_SHA256,
            site_digest(source_sites),
            "source site",
        ),
        (
            EXPECTED_SOURCE_ROOT_COUNT,
            len(source_roots),
            "source root count",
        ),
        (
            EXPECTED_SOURCE_ROOT_SHA256,
            root_digest(source_roots),
            "source root",
        ),
        (
            EXPECTED_DIRECT_PENDING_SITE_SHA256,
            site_digest(direct_pending_sites),
            "direct pending site",
        ),
        (
            EXPECTED_DIRECT_PENDING_ROOT_SHA256,
            root_digest(direct_pending_roots),
            "direct pending root",
        ),
    )
    for expected, actual, label in optional_guards:
        if expected is not None:
            require(actual == expected, f"{label} digest/count drifted")
    require(
        len(sites) == EXPECTED_SITE_COUNT
        and site_digest(sites) == EXPECTED_SITE_SHA256
        and len(source_sites) == EXPECTED_SOURCE_SITE_COUNT
        and len(source_only) == EXPECTED_SOURCE_ONLY_SITES
        and site_digest(source_only) == EXPECTED_SOURCE_ONLY_SITE_SHA256
        and not candidate_only
        and len(direct_pending_sites) == EXPECTED_DIRECT_PENDING_SITES
        and len(direct_pending_roots) == EXPECTED_DIRECT_PENDING_ROOTS
        and len(potential) == EXPECTED_POTENTIAL_ROWS
        and coordinate_digest(potential) == EXPECTED_POTENTIAL_SHA256
        and len(overlap) == EXPECTED_OVERLAP_ROWS
        and coordinate_digest(overlap) == EXPECTED_OVERLAP_SHA256
        and len(disjoint) == EXPECTED_DISJOINT_ROWS
        and coordinate_digest(disjoint) == EXPECTED_DISJOINT_SHA256
        and potential == overlap | disjoint
        and not overlap & disjoint,
        "selector-1174 site/root/pending partition drifted",
    )
    require(
        shape["seven_way"]
        and root_digest(shape["candidate_nodes"])
        == EXPECTED_DISPATCH_NODE_SHA256
        and RANKING.edge_digest(shape["candidate_dispatch"])
        == EXPECTED_DISPATCH_EDGE_SHA256
        and root_digest(shape["candidate_leaves"])
        == EXPECTED_TERMINAL_SHA256,
        "selector-1174 fixed seven-way dispatch drifted",
    )
    require(
        target["candidate_call_sites"] == sites
        and target["source_call_sites"] == source_sites
        and set(target["potential_current_pending_coordinates"]) == potential
        and set(target["overlap_selector1096_coordinates"]) == overlap
        and not target["overlap_selector568_coordinates"]
        and ranked["disjoint_current_pending_rows"] == len(disjoint),
        "ranking-to-assignment handoff drifted",
    )

    site_rows = build_site_rows(
        sites=sites,
        candidate=candidate,
        current=current,
        source=source,
        contexts=contexts,
    )
    site_row_sha256 = canonical_sha256(site_rows)
    if EXPECTED_SITE_ROW_SHA256 is not None:
        require(
            site_row_sha256 == EXPECTED_SITE_ROW_SHA256,
            "site risk/language matrix drifted",
        )
    cuts = balanced_cuts(site_rows)
    starts = (0,) + cuts[:-1]
    chunks: list[dict[str, Any]] = []
    for chunk_id, (start, end) in enumerate(zip(starts, cuts)):
        members = site_rows[start:end]
        roots = sorted(
            {
                RANKING.parse_root(str(row["root"]))
                for row in members
            }
        )
        chunk_pending = {
            coordinate
            for root in roots
            for coordinate in pending_by_root.get(root, set())
        }
        chunk_overlap = chunk_pending & overlap
        chunk_disjoint = chunk_pending & disjoint
        flag_counts: Counter[str] = Counter(
            {
                "grammar_right_boundary": 0,
                "layout_relative_expansion": 0,
                "multi_control_gap": 0,
                "protected_outer_space": 0,
            }
        )
        language_counts: Counter[str] = Counter(
            {"en": 0, "jp": 0, "sc": 0, "tc": 0}
        )
        for row in members:
            flag_counts.update(
                key for key, value in row["flags"].items() if value
            )
            language_counts.update(
                key
                for key, value in row["language_available"].items()
                if value
            )
        chunks.append(
            {
                "chunk_id": chunk_id,
                "cross_family_overlap_coordinates": sorted(
                    chunk_overlap, key=RANKING.parse_coordinate
                ),
                "cross_family_overlap_row_count": len(chunk_overlap),
                "cross_family_overlap_sha256": coordinate_digest(
                    chunk_overlap
                ),
                "disjoint_pending_coordinates": sorted(
                    chunk_disjoint, key=RANKING.parse_coordinate
                ),
                "disjoint_pending_row_count": len(chunk_disjoint),
                "disjoint_pending_sha256": coordinate_digest(
                    chunk_disjoint
                ),
                "flag_counts": dict(sorted(flag_counts.items())),
                "language_available_counts": dict(
                    sorted(language_counts.items())
                ),
                "ordinal_end": end - 1,
                "ordinal_start": start,
                "pending_coordinates": sorted(
                    chunk_pending, key=RANKING.parse_coordinate
                ),
                "pending_row_upper_bound": len(chunk_pending),
                "pending_sha256": coordinate_digest(chunk_pending),
                "root_count": len(roots),
                "root_sha256": root_digest(roots),
                "roots": [RANKING.root_string(root) for root in roots],
                "site_count": len(members),
                "site_sha256": site_digest(
                    str(row["site"]) for row in members
                ),
                "sites": [str(row["site"]) for row in members],
                "workload_weight": sum(
                    int(row["workload_weight"]) for row in members
                ),
            }
        )
    observed_chunk_counts = tuple(
        (
            int(chunk["site_count"]),
            int(chunk["root_count"]),
            int(chunk["pending_row_upper_bound"]),
            int(chunk["cross_family_overlap_row_count"]),
            int(chunk["workload_weight"]),
        )
        for chunk in chunks
    )
    if EXPECTED_CHUNK_COUNTS is not None:
        require(
            observed_chunk_counts == EXPECTED_CHUNK_COUNTS,
            f"chunk metrics drifted: {observed_chunk_counts}",
        )
    require(
        sum(chunk["site_count"] for chunk in chunks) == len(sites)
        and sum(chunk["root_count"] for chunk in chunks)
        == len(candidate_roots)
        and set().union(
            *(set(chunk["pending_coordinates"]) for chunk in chunks)
        )
        == potential,
        "chunk assignment is not an exact root-preserving partition",
    )

    common_inputs = {
        "cross_family_builder_sha256": EXPECTED_CROSS_BUILDER_SHA256,
        "cross_family_commit": EXPECTED_CROSS_COMMIT,
        "cross_family_coverage_sha256": EXPECTED_CROSS_COVERAGE_SHA256,
        "cross_family_decisions_sha256": EXPECTED_CROSS_DECISIONS_SHA256,
        "cross_family_promotion_report_sha256":
            EXPECTED_CROSS_PROMOTION_REPORT_SHA256,
        "official_integrated_ledger_sha256":
            EXPECTED_OFFICIAL_LEDGER_SHA256,
        "pk_context_sha256": EXPECTED_CONTEXT_SHA256,
        "pk_current_sha256": EXPECTED_PK_CURRENT_SHA256,
        "pk_pristine_sha256": EXPECTED_PK_PRISTINE_SHA256,
        "pk_rebuilt_candidate_sha256": EXPECTED_PK_CANDIDATE_SHA256,
        "ranking_builder_sha256": EXPECTED_RANKING_BUILDER_SHA256,
        "ranking_private_sha256": EXPECTED_RANKING_PRIVATE_SHA256,
        "ranking_public_sha256": EXPECTED_RANKING_PUBLIC_SHA256,
    }
    private: dict[str, Any] = {
        "schema": PRIVATE_SCHEMA,
        "method": METHOD,
        "inputs": common_inputs,
        "assignment_method": {
            "chunk_count": CHUNK_COUNT,
            "contiguous_ordinals": True,
            "root_split_permitted": False,
            "site_count_bounds": [MIN_CHUNK_SITES, MAX_CHUNK_SITES],
            "weights": {
                "base": 10,
                "grammar_right_boundary": 4,
                "layout_relative_expansion": 7,
                "missing_auxiliary_language_each": 3,
                "multi_control_gap": 6,
                "protected_outer_space": 8,
            },
        },
        "scope": {
            "selector_coordinate": f"0:{SELECTOR}:0",
            "terminal_coordinates": [
                f"0:{terminal}:0" for terminal in TERMINALS
            ],
            "candidate_call_sites": sites,
            "candidate_call_roots": [
                RANKING.root_string(root) for root in sorted(candidate_roots)
            ],
            "source_call_sites": source_sites,
            "source_only_call_sites": sorted(
                source_only, key=RANKING.site_key
            ),
            "direct_pending_call_sites": direct_pending_sites,
            "direct_pending_roots": [
                RANKING.root_string(root)
                for root in sorted(direct_pending_roots)
            ],
            "reachable_pending_roots": [
                RANKING.root_string(root)
                for root in sorted(reachable_pending_roots)
            ],
            "potential_current_pending_coordinates": sorted(
                potential, key=RANKING.parse_coordinate
            ),
            "cross_family_overlap_coordinates": sorted(
                overlap, key=RANKING.parse_coordinate
            ),
            "disjoint_current_pending_coordinates": sorted(
                disjoint, key=RANKING.parse_coordinate
            ),
        },
        "site_assignments": site_rows,
        "chunks": chunks,
        "privacy": {
            "classification": "private_coordinate_assignment",
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
    }
    private["guards"] = {
        "chunks_canonical_sha256": canonical_sha256(chunks),
        "payload_without_guards_canonical_sha256": canonical_sha256(private),
        "site_assignment_canonical_sha256": site_row_sha256,
    }
    private_content = serialized_json(private)

    public_chunks = [
        {
            key: chunk[key]
            for key in (
                "chunk_id",
                "cross_family_overlap_row_count",
                "cross_family_overlap_sha256",
                "disjoint_pending_row_count",
                "disjoint_pending_sha256",
                "flag_counts",
                "language_available_counts",
                "ordinal_end",
                "ordinal_start",
                "pending_row_upper_bound",
                "pending_sha256",
                "root_count",
                "root_sha256",
                "site_count",
                "site_sha256",
                "workload_weight",
            )
        }
        for chunk in chunks
    ]
    public: dict[str, Any] = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "inputs": common_inputs,
        "scope": {
            "resource": "MSG_PK/JP/msggame.bin",
            "selector": SELECTOR,
            "terminal_count": len(TERMINALS),
            "terminal_coordinate_sha256": EXPECTED_TERMINAL_SHA256,
            "official_pending_rows": EXPECTED_OFFICIAL_PENDING_ROWS,
        },
        "dispatch_contract": {
            "source_candidate_identical": True,
            "node_count": 13,
            "node_sha256": EXPECTED_DISPATCH_NODE_SHA256,
            "edge_count": 13,
            "edge_sha256": EXPECTED_DISPATCH_EDGE_SHA256,
            "terminal_count": 7,
            "terminal_coordinate_sha256": EXPECTED_TERMINAL_SHA256,
        },
        "coverage": {
            "candidate_call_site_count": len(sites),
            "candidate_call_site_sha256": site_digest(sites),
            "candidate_call_root_count": len(candidate_roots),
            "candidate_call_root_sha256": root_digest(candidate_roots),
            "source_call_site_count": len(source_sites),
            "source_call_site_sha256": site_digest(source_sites),
            "source_call_root_count": len(source_roots),
            "source_call_root_sha256": root_digest(source_roots),
            "source_only_call_site_count": len(source_only),
            "source_only_call_site_sha256": site_digest(source_only),
            "candidate_only_call_site_count": 0,
            "candidate_only_call_site_sha256": site_digest(()),
            "direct_pending_call_site_count": len(direct_pending_sites),
            "direct_pending_call_site_sha256":
                site_digest(direct_pending_sites),
            "direct_pending_root_count": len(direct_pending_roots),
            "direct_pending_root_sha256": root_digest(direct_pending_roots),
            "reachable_pending_root_count":
                len(reachable_pending_roots),
            "reachable_pending_root_sha256":
                root_digest(reachable_pending_roots),
            "potential_current_pending_rows": len(potential),
            "potential_current_pending_sha256":
                coordinate_digest(potential),
            "cross_family_overlap_rows": len(overlap),
            "cross_family_overlap_sha256": coordinate_digest(overlap),
            "disjoint_current_pending_rows": len(disjoint),
            "disjoint_current_pending_sha256":
                coordinate_digest(disjoint),
        },
        "assignment": {
            "chunk_count": CHUNK_COUNT,
            "cuts": list(cuts),
            "deterministic_balancing": True,
            "root_split_permitted": False,
            "site_risk_matrix_sha256": site_row_sha256,
            "chunks": public_chunks,
        },
        "privacy": {
            "contains_commercial_source_text": False,
            "contains_dialogue_bodies": False,
            "contains_exact_coordinates": False,
            "contains_translations": False,
            "private_assignment_stays_below_tmp": True,
            "shared_integration_mutated": False,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    public["guards"] = {
        "private_assignment_sha256": sha256_bytes(
            private_content.encode("utf-8")
        ),
        "report_payload_sha256": canonical_sha256(public),
    }
    public_content = serialized_json(public)
    assert_source_free(public)
    require(
        steam_before
        == sha256_file(steam_path)
        == EXPECTED_PK_CURRENT_SHA256,
        "shadow Steam PK archive changed during assignment",
    )
    return private_content, public_content, private, public


def validate_outputs(
    private_content: str,
    public_content: str,
    *,
    require_frozen_hashes: bool,
) -> None:
    if not require_frozen_hashes:
        return
    actual = (
        sha256_bytes(private_content.encode("utf-8")),
        sha256_bytes(public_content.encode("utf-8")),
    )
    expected = (
        EXPECTED_PRIVATE_FILE_SHA256,
        EXPECTED_PUBLIC_FILE_SHA256,
    )
    require(
        all(expected) and actual == expected,
        f"selector-1174 frozen outputs drifted: {actual}",
    )


def validate_paths(args: argparse.Namespace) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    require(
        private_root in args.private_output.resolve(strict=False).parents,
        "private assignment must remain below tmp",
    )
    require(
        args.public_output.resolve(strict=False)
        == DEFAULT_PUBLIC_OUTPUT.resolve(strict=False),
        "public assignment must use its fixed tracked path",
    )
    shadow_paths = {
        (
            RANKING.DEFAULT_STEAM_ROOT / "MSG_PK" / language / "msggame.bin"
        ).resolve(strict=False)
        for language in ("JP", "EN", "SC", "TC")
    }
    require(
        args.private_output.resolve(strict=False) not in shadow_paths
        and args.public_output.resolve(strict=False) not in shadow_paths,
        "assignment output may not target Steam data",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--private-output", type=Path, default=DEFAULT_PRIVATE_OUTPUT
    )
    parser.add_argument(
        "--public-output", type=Path, default=DEFAULT_PUBLIC_OUTPUT
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate_paths(args)
    private_content, public_content, _private, public = build_outputs()
    validate_outputs(
        private_content,
        public_content,
        require_frozen_hashes=bool(
            EXPECTED_PRIVATE_FILE_SHA256 and EXPECTED_PUBLIC_FILE_SHA256
        ),
    )
    outputs = {
        args.private_output: private_content,
        args.public_output: public_content,
    }
    if args.check:
        for path, content in outputs.items():
            require(path.is_file(), f"assignment output missing: {path}")
            require(
                path.read_text(encoding="utf-8") == content,
                f"assignment output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "chunks": [
                    {
                        "overlap": row["cross_family_overlap_row_count"],
                        "pending": row["pending_row_upper_bound"],
                        "roots": row["root_count"],
                        "sites": row["site_count"],
                        "weight": row["workload_weight"],
                    }
                    for row in public["assignment"]["chunks"]
                ],
                "disjoint_current_pending_rows": EXPECTED_DISJOINT_ROWS,
                "selector": SELECTOR,
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
