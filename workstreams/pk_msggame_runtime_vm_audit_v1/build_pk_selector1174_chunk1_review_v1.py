#!/usr/bin/env python3
"""Validate PK selector-1174 chunk-1 and emit a source-free review report."""

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
ASSIGNMENT_BUILDER = WORKSTREAM / "build_pk_selector1174_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector1174_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1174_assignment_coverage.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector538_family_checkpoint.private.v1.jsonl"
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
PRIVATE_REVIEW_PATH = (
    DIALOGUE_TMP / "pk_selector1174_chunk1_review.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1174_chunk1_review_proposal.v1.json"
)
LIVE_STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector1174-chunk1-review.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1174-chunk1-review-proposal.v1"
METHOD = "reversed_vm_pk_selector1174_chunk1_fresh_semantic_review"
SELECTOR = 1174
TERMINALS = tuple(range(2644, 2651))
CHUNK_ID = 1
ORDINAL_START = 55
ORDINAL_END = 114

EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "FFAB60E333B547158CBE349D60708BB8D26B1EBF2DE0F56AC7EF512EDD6EEC9E"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "07B892C55CAB031BDE414726FD301F03441E181C228D970003A834612ACABC10"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "6979EE31FB6AE4C046892E0785A61CC1D57F58415EB3B3D55601944F148A2CB2"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_CROSS_BUILDER_SHA256 = (
    "C9976A86F7ABA023A5F575BBFCCDA20BF2C9A7E8329C0EAFFC59633A2DD422EE"
)
EXPECTED_CROSS_DECISIONS_SHA256 = (
    "E3C97823C70FBD441D420722AE306E2DEBE62CB8919FBA5426A91BC00DCBA5ED"
)
EXPECTED_PRIVATE_REVIEW_SHA256 = (
    "7FEACBC29E0C4F9F46670B0A7781620AE7F54639FF58CED00D3C0453166C86EF"
)
EXPECTED_PRE_CROSS_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_CROSS_CANDIDATE_SHA256 = (
    "FF424B8C66BECD398E7617EA95904BFBEBFADEA581870CE5A142CD9BF3CA4845"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256 = (
    "8A982B3FE79CA7EC16899AF7E58339C81EEA9179675AE788C89CC65457614BCE"
)
EXPECTED_FOUR_REPAIR_ONLY_CANDIDATE_SHA256 = (
    "9681A11B89FAA93E18F4C100537D0B29DF18974CF75085099024D876D6A43784"
)
EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_SITE_COUNT = 60
EXPECTED_ROOT_COUNT = 59
EXPECTED_ASSEMBLY_COUNT = 420
EXPECTED_ACCEPTED_SITES = 44
EXPECTED_ACCEPTED_ROOTS = 43
EXPECTED_REJECTED_SITES = 16
EXPECTED_REJECTED_ROOTS = 16
EXPECTED_REWRITES = 39
EXPECTED_KEEPS = 7
EXPECTED_PENDING = 135
EXPECTED_ACCEPTED_PENDING = 108
EXPECTED_BLOCKED_PENDING = 27
EXPECTED_CROSS_RENEWALS = 13
EXPECTED_CROSS_BLOCKED = 0
EXPECTED_DISJOINT_PROMOTIONS = 95
EXPECTED_NONPENDING_OVERRIDES = 16
EXPECTED_PENDING_OVERRIDES = 23
EXPECTED_BOUNDARY_WHITESPACE_CHANGES = 32
EXPECTED_DEPENDENCY_ASSEMBLIES = 7
EXPECTED_CROSS_REQUIRED_OVERRIDES = 7
EXPECTED_SITE_SHA256 = (
    "FEC5A84EB99E4937789C883D67A40C33F5EB2EB83DD5293E55FF9823081F59D6"
)
EXPECTED_ROOT_SHA256 = (
    "C2391049C1ACE5C6C2ABAA98CD8A34DC98E9B50859920431E4175871A26A9E17"
)
EXPECTED_PENDING_SHA256 = (
    "3EAEAB40484EFA552AB546C27CAAD8026E6D79895315DE83B10FB865AD43EF1D"
)
EXPECTED_OVERLAP_SHA256 = (
    "5DD9365211CEB69D9A1069EA19F8929250A2E71207E0DE4D226D031EDE9A4E27"
)
EXPECTED_DISJOINT_SHA256 = (
    "4330F9F977AC63A2CBDBDF66A5091939BDD0AF8D9BD7DDBEB106513C31173147"
)
EXPECTED_ACCEPTED_PENDING_SHA256 = (
    "5F9C87CCD58EAA5B5D98A857C73468AF0FB35B6C6B205F6D39523E0655823F64"
)
EXPECTED_BLOCKED_PENDING_SHA256 = (
    "5F07D4B36AB87B6E68576E7981AAF4DA248A3A1F1CFA7635078139212023916C"
)
EXPECTED_CROSS_RENEWAL_SHA256 = (
    "5DD9365211CEB69D9A1069EA19F8929250A2E71207E0DE4D226D031EDE9A4E27"
)
EXPECTED_CROSS_BLOCKED_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_DISJOINT_PROMOTION_SHA256 = (
    "B428311B38312FABA6EE224EA19A9E1798C8DE4BD661D2EDC8AF7CF4BECC8039"
)
EXPECTED_OVERRIDE_SHA256 = (
    "CE35B7388E6DDCBDEE7EF33AE918672A999F5EF7A437C7EF72593E6AD0073D40"
)
EXPECTED_KEEP_SHA256 = (
    "E4C4135DBDADC06C8F065E3F9186CA8EF15C7D34FDBC8BA9481493A3AD7D1F03"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "D81A76F7C8B8CE0146879FD9DB2F5EFFC62C5077608064BAECFBA5FA4963C56B"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "CF7D60CC393CED8B44F705D14EE8391392C157065F258533A0A770E961835763"
)
EXPECTED_ASSEMBLY_SHA256 = (
    "8BEB5BCFA5CC36BAB14A421BD0459C5F575753F190CB87CD71F67E7FE8221DBE"
)
EXPECTED_DEPENDENCY_ASSEMBLY_SHA256 = (
    "9F3D7E45118D3759A7B10E5F1D45D9089177ADFE88F46B66F472B0400FB2A9AE"
)
EXPECTED_CROSS_REQUIRED_OVERRIDE_SHA256 = (
    "5FA76FD488FEA55E62E970D941D8F57F4EAEBC4F8B176F090AE63DC03D9DE3BF"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "00BCA825E39953B1E0A6DD86842F78BAD32CF7EC0166BFC8F41F594EC50B82CC"
)


class ReviewError(ValueError):
    """Raised when selector-1174 chunk-1 review evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGN = load_module(ASSIGNMENT_BUILDER, "selector1174_chunk1_review_assignment")
ENGINE = ASSIGN.ENGINE
ASSIGN.OFFICIAL_LEDGER_PATH = OFFICIAL_LEDGER_PATH


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


def coordinate_digest(values: Iterable[str]) -> str:
    return ASSIGN.coordinate_digest(values)


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return tuple(map(int, value.split(":")))  # type: ignore[return-value]


def site_root(site: str) -> tuple[int, int]:
    block_id, record_id, _gap_id, _offset = ASSIGN.RANKING.site_key(site)
    return block_id, record_id


def line_metrics(value: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line in value.split("\n"):
        full = 0
        half = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                continue
            if unicodedata.east_asian_width(character) in {"W", "F", "A"}:
                full += 1
            else:
                half += 1
        result.append(
            {
                "full_width_count": full,
                "half_width_count": half,
                "raw_g1n_width_px": 48 * full + 24 * half,
                "visible": line,
            }
        )
    return result


def current_relative_nonexpanding(
    reviewed: Sequence[Mapping[str, Any]],
    current: Sequence[Mapping[str, Any]],
) -> bool:
    return len(reviewed) == len(current) and all(
        int(candidate["raw_g1n_width_px"]) <= int(baseline["raw_g1n_width_px"])
        for candidate, baseline in zip(reviewed, current)
    )


def record_gap_sha256(record: Any) -> str:
    framed = b"".join(
        len(gap).to_bytes(4, "little") + gap
        for gap in ENGINE.record_gap_bytes(record)
    )
    return sha256_bytes(framed)


def load_json_exact(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM rejected: {path}")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewError(f"invalid strict UTF-8 JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def load_cross_map() -> dict[tuple[int, int, int], str]:
    result: dict[tuple[int, int, int], str] = {}
    rows = 0
    for line in CROSS_DECISIONS_PATH.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        rows += 1
        row = json.loads(line)
        translation = row.get("translation")
        require(isinstance(translation, str), "cross translation body absent")
        result[parse_coordinate(str(row["coordinate"]))] = translation
    require(rows == 920 and len(result) == 920, "cross row universe drifted")
    return result


def load_world() -> dict[str, Any]:
    candidate, current, source, contexts, _pending = ASSIGN.load_records()
    current_path = ASSIGN.RANKING.DEFAULT_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
    official, _pending_by_root, _rows = ASSIGN.RANKING.load_official_ledger(
        OFFICIAL_LEDGER_PATH
    )
    pre_cross_blob = ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), official
    )
    require(
        sha256_bytes(pre_cross_blob) == EXPECTED_PRE_CROSS_CANDIDATE_SHA256,
        "pre-cross candidate drifted",
    )
    cross_blob = ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), {**official, **load_cross_map()}
    )
    require(
        sha256_bytes(cross_blob) == EXPECTED_CROSS_CANDIDATE_SHA256,
        "corrected cross predecessor drifted",
    )
    return {
        "candidate_blob": cross_blob,
        "candidate_records": ENGINE.archive_records(
            ENGINE.parse_packed_msggame(cross_blob).archive
        ),
        "current_records": current,
        "language_records": {"jp": source, **contexts},
        "pre_cross_records": candidate,
    }


def validate_context(
    recorded: Mapping[str, Any],
    *,
    records: Mapping[tuple[int, int], Any],
    site: str,
    available: bool,
) -> None:
    left, right = ASSIGN.adjacent_literals(records, site)
    require(
        recorded.get("available") is available
        and recorded.get("left") == left
        and recorded.get("right") == right
        and recorded.get("joined_utf8_sha256")
        == sha256_bytes((left + right).encode("utf-8")),
        f"multilingual context drifted at {site}",
    )


def validate_private(
    handoff: Mapping[str, Any],
    *,
    assignment: Mapping[str, Any],
    chunk: Mapping[str, Any],
    world: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        handoff.get("schema") == PRIVATE_SCHEMA
        and handoff.get("method") == METHOD,
        "private review schema/method drifted",
    )
    privacy = handoff.get("privacy", {})
    scope = handoff.get("scope", {})
    counts = handoff.get("counts", {})
    require(
        privacy
        == {
            "classification": "private",
            "contains_dialogue_bodies": True,
            "public": False,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
        "private review privacy contract drifted",
    )
    require(
        scope.get("chunk_id") == CHUNK_ID
        and scope.get("ordinal_start") == ORDINAL_START
        and scope.get("ordinal_end") == ORDINAL_END
        and scope.get("selector_coordinate") == f"0:{SELECTOR}:0"
        and scope.get("site_sha256") == EXPECTED_SITE_SHA256
        and scope.get("root_sha256") == EXPECTED_ROOT_SHA256
        and scope.get("pending_sha256") == EXPECTED_PENDING_SHA256
        and scope.get("cross_family_overlap_sha256") == EXPECTED_OVERLAP_SHA256
        and scope.get("disjoint_pending_sha256") == EXPECTED_DISJOINT_SHA256
        and tuple(scope.get("terminal_coordinates", ()))
        == tuple(f"0:{terminal}:0" for terminal in TERMINALS),
        "private review scope drifted",
    )
    require(
        counts
        == {
            "accepted_pending_coordinates": EXPECTED_ACCEPTED_PENDING,
            "accepted_roots": EXPECTED_ACCEPTED_ROOTS,
            "accepted_sites": EXPECTED_ACCEPTED_SITES,
            "assemblies": EXPECTED_ASSEMBLY_COUNT,
            "blocked_pending_coordinates": EXPECTED_BLOCKED_PENDING,
            "blocked_roots": EXPECTED_REJECTED_ROOTS,
            "cross_overlap_blocked": EXPECTED_CROSS_BLOCKED,
            "cross_overlap_renewals": EXPECTED_CROSS_RENEWALS,
            "cross_renewal_required_overrides":
                EXPECTED_CROSS_REQUIRED_OVERRIDES,
            "dependency_assemblies": EXPECTED_DEPENDENCY_ASSEMBLIES,
            "disjoint_potential_promotions": EXPECTED_DISJOINT_PROMOTIONS,
            "keep": EXPECTED_KEEPS,
            "reject": EXPECTED_REJECTED_SITES,
            "rewrite": EXPECTED_REWRITES,
            "sites": EXPECTED_SITE_COUNT,
        },
        "private review count contract drifted",
    )

    exact = handoff.get("exact_maps", {})
    overrides = exact.get("translation_overrides")
    keep_coordinates = exact.get("keep_coordinates")
    required_cross_overrides = exact.get(
        "cross_renewal_required_override_coordinates"
    )
    require(
        isinstance(overrides, dict)
        and isinstance(keep_coordinates, list)
        and isinstance(required_cross_overrides, list)
        and len(overrides) == EXPECTED_REWRITES
        and len(keep_coordinates) == EXPECTED_KEEPS,
        "private exact maps drifted",
    )
    pending = set(chunk["pending_coordinates"])
    overlap = set(chunk["cross_family_overlap_coordinates"])
    require(
        len(set(overrides) & pending) == EXPECTED_PENDING_OVERRIDES
        and len(set(overrides) - pending) == EXPECTED_NONPENDING_OVERRIDES,
        "pending/nonpending override partition drifted",
    )
    site_rows = handoff.get("site_reviews")
    require(
        isinstance(site_rows, list) and len(site_rows) == EXPECTED_SITE_COUNT,
        "private site rows drifted",
    )
    assignment_rows = assignment["site_assignments"][
        ORDINAL_START : ORDINAL_END + 1
    ]
    candidate_records = world["candidate_records"]
    current_records = world["current_records"]
    pre_cross_records = world["pre_cross_records"]
    language_records = world["language_records"]
    terminal_candidate = {
        terminal: ENGINE.parse_record_literals(
            candidate_records[(0, terminal)]
        )[0].text
        for terminal in TERMINALS
    }
    terminal_current = {
        terminal: ENGINE.parse_record_literals(
            current_records[(0, terminal)]
        )[0].text
        for terminal in TERMINALS
    }
    terminal_jp = {
        terminal: ENGINE.parse_record_literals(
            language_records["jp"][(0, terminal)]
        )[0].text
        for terminal in TERMINALS
    }
    require(
        set(terminal_candidate.values()) == {""}
        and set(terminal_current.values()) == {"", "\uace0"}
        and set(terminal_jp.values()) == {"", "\u3054"},
        "selector terminal semantic universe drifted",
    )

    accepted_sites: list[str] = []
    rejected_sites: list[str] = []
    blocker_counts: Counter[str] = Counter()
    language_counts: Counter[str] = Counter()
    assembly_manifest: list[list[Any]] = []
    dependency_assembly_manifest: list[list[Any]] = []
    whitespace_changes = 0
    seen_override_coordinates: set[str] = set()
    seen_keep_coordinates: set[str] = set()
    repair_only_override_coordinates: set[str] = set()
    for assignment_row, row in zip(assignment_rows, site_rows):
        ordinal = int(assignment_row["ordinal"])
        site = str(assignment_row["site"])
        coordinate_value = assignment_row["left_coordinate"]
        coordinate = (
            str(coordinate_value) if coordinate_value is not None else None
        )
        root = site_root(site)
        decision = row.get("decision")
        reviewed_left = row.get("reviewed_left_translation")
        reviewed_right = row.get("reviewed_right_translation")
        require(
            row.get("ordinal") == ordinal
            and row.get("site") == site
            and row.get("coordinate") == coordinate
            and decision in {"rewrite", "keep", "reject"}
            and isinstance(reviewed_left, str)
            and isinstance(reviewed_right, str),
            f"site identity/decision drifted at ordinal {ordinal}",
        )
        baseline_left, baseline_right = ASSIGN.adjacent_literals(
            candidate_records, site
        )
        current_left, current_right = ASSIGN.adjacent_literals(
            current_records, site
        )
        pre_cross_left, pre_cross_right = ASSIGN.adjacent_literals(
            pre_cross_records, site
        )
        require(
            row.get("baseline_candidate_left") == baseline_left
            and row.get("baseline_candidate_right") == baseline_right
            and row.get("current_left") == current_left
            and row.get("current_right") == current_right
            and row.get("pre_cross_left") == pre_cross_left
            and row.get("pre_cross_right") == pre_cross_right,
            f"Korean predecessor context drifted at {site}",
        )
        require(
            reviewed_right == baseline_right
            or decision == "rewrite",
            f"right-fragment override lacks rewrite decision at {site}",
        )
        if decision == "rewrite":
            require(
                coordinate is not None
                and overrides.get(coordinate) == reviewed_left
                and reviewed_left != baseline_left,
                f"rewrite map drifted at {site}",
            )
            seen_override_coordinates.add(coordinate)
            if ordinal in {57, 76}:
                repair_only_override_coordinates.add(coordinate)
            if reviewed_right != baseline_right:
                block_id, record_id, gap_id, _offset = (
                    ASSIGN.RANKING.site_key(site)
                )
                right_coordinate = f"{block_id}:{record_id}:{gap_id}"
                require(
                    overrides.get(right_coordinate) == reviewed_right,
                    f"right-fragment override map drifted at {site}",
                )
                seen_override_coordinates.add(right_coordinate)
                if ordinal in {57, 76}:
                    repair_only_override_coordinates.add(right_coordinate)
            accepted_sites.append(site)
        elif decision == "keep":
            require(
                coordinate is not None
                and coordinate in keep_coordinates
                and reviewed_left == baseline_left,
                f"keep map drifted at {site}",
            )
            seen_keep_coordinates.add(coordinate)
            accepted_sites.append(site)
        else:
            require(
                isinstance(row.get("reject_reason"), str)
                and bool(row["reject_reason"]),
                f"reject reason absent at {site}",
            )
            rejected_sites.append(site)
            blocker_counts[str(row["reject_reason"])] += 1

        authority = row.get("multilingual_authority", {})
        require(
            authority.get("fresh_review_completed") is True
            and authority.get("jp_is_semantic_authority") is True
            and authority.get("speaker_tone_reviewed") is True
            and authority.get("historical_terms_reviewed") is True
            and authority.get("review_passes") == 2,
            f"semantic review proof drifted at {site}",
        )
        for language in ("jp", "en", "sc", "tc"):
            available = bool(assignment_row["language_available"][language])
            validate_context(
                authority[language],
                records=language_records[language],
                site=site,
                available=available,
            )
            language_counts[language] += int(available)

        control = row.get("control_and_boundary_proof", {})
        require(
            control.get("baseline_record_gap_sha256")
            == record_gap_sha256(candidate_records[root])
            and control.get("record_control_gaps_preserved") is True
            and control.get("literal_linebreak_count_preserved") is True
            and control.get("existing_leading_whitespace_preserved") is True
            and control.get("existing_trailing_whitespace_preserved") is True,
            f"control/boundary proof drifted at {site}",
        )
        whitespace_changes += int(
            bool(control.get("intentional_boundary_whitespace_changed"))
        )
        branches = row.get("assemblies")
        require(
            isinstance(branches, list) and len(branches) == len(TERMINALS),
            f"seven-branch assembly absent at {site}",
        )
        all_width = True
        all_register = True
        for branch_index, (terminal, branch) in enumerate(
            zip(TERMINALS, branches)
        ):
            reviewed_assembly = (
                reviewed_left + terminal_candidate[terminal] + reviewed_right
            )
            current_assembly = (
                current_left + terminal_current[terminal] + current_right
            )
            reviewed_lines = line_metrics(reviewed_assembly)
            current_lines = line_metrics(current_assembly)
            nonexpanding = current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            register_proven = decision != "reject"
            expected_register = (
                "plain_empty"
                if terminal in {2645, 2650}
                else "contextual_honorific_elided"
            )
            require(
                branch.get("branch_index") == branch_index
                and branch.get("terminal_coordinate") == f"0:{terminal}:0"
                and branch.get("candidate_terminal")
                == terminal_candidate[terminal]
                and branch.get("current_terminal") == terminal_current[terminal]
                and branch.get("jp_terminal") == terminal_jp[terminal]
                and branch.get("register_semantic") == expected_register
                and branch.get("reviewed_assembly") == reviewed_assembly
                and branch.get("current_assembly") == current_assembly
                and branch.get("reviewed_lines") == reviewed_lines
                and branch.get("current_lines") == current_lines
                and branch.get("line_count_match")
                is (len(reviewed_lines) == len(current_lines))
                and branch.get("current_relative_raw_g1n_nonexpanding")
                is nonexpanding
                and branch.get("register_and_grammar_proven")
                is register_proven,
                f"assembly proof drifted at {site}/{terminal}",
            )
            all_width = all_width and nonexpanding
            all_register = all_register and register_proven
            assembly_manifest.append(
                [
                    ordinal,
                    site,
                    terminal,
                    sha256_bytes(reviewed_assembly.encode("utf-8")),
                    sha256_bytes(current_assembly.encode("utf-8")),
                    nonexpanding,
                    register_proven,
                ]
            )
        dependency_branches = row.get("dependency_assemblies")
        require(
            isinstance(dependency_branches, list)
            and len(dependency_branches)
            == (EXPECTED_DEPENDENCY_ASSEMBLIES if ordinal == 76 else 0),
            f"selector1096 dependency branch count drifted at {site}",
        )
        if ordinal == 76:
            candidate_literals = [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    candidate_records[root]
                )
            ]
            current_literals = [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    current_records[root]
                )
            ]
            for branch_index, (terminal, dependency) in enumerate(
                zip(range(2581, 2588), dependency_branches)
            ):
                candidate_terminal = ENGINE.parse_record_literals(
                    candidate_records[(0, terminal)]
                )[0].text
                current_terminal = ENGINE.parse_record_literals(
                    current_records[(0, terminal)]
                )[0].text
                reviewed_dependency = (
                    candidate_literals[3]
                    + candidate_terminal
                    + reviewed_left
                )
                current_dependency = (
                    current_literals[3]
                    + current_terminal
                    + current_left
                )
                reviewed_dependency_lines = line_metrics(
                    reviewed_dependency
                )
                current_dependency_lines = line_metrics(current_dependency)
                dependency_nonexpanding = current_relative_nonexpanding(
                    reviewed_dependency_lines,
                    current_dependency_lines,
                )
                require(
                    dependency.get("branch_index") == branch_index
                    and dependency.get("selector") == 1096
                    and dependency.get("terminal_coordinate")
                    == f"0:{terminal}:0"
                    and dependency.get("reviewed_assembly")
                    == reviewed_dependency
                    and dependency.get("current_assembly")
                    == current_dependency
                    and dependency.get("reviewed_lines")
                    == reviewed_dependency_lines
                    and dependency.get("current_lines")
                    == current_dependency_lines
                    and dependency.get(
                        "current_relative_raw_g1n_nonexpanding"
                    )
                    is dependency_nonexpanding
                    and dependency_nonexpanding,
                    f"selector1096 dependency proof drifted at {site}/{terminal}",
                )
                dependency_assembly_manifest.append(
                    [
                        site,
                        terminal,
                        sha256_bytes(reviewed_dependency.encode("utf-8")),
                        sha256_bytes(current_dependency.encode("utf-8")),
                        dependency_nonexpanding,
                    ]
                )
        require(
            row.get("all_seven_width_branches_nonexpanding") is all_width
            and row.get("all_seven_register_branches_proven") is all_register,
            f"seven-branch summary drifted at {site}",
        )
        if decision != "reject":
            require(
                all_width and all_register,
                f"accepted site lacks width/register proof: {site}",
            )
        else:
            require(
                not all_register,
                f"rejected site lacks semantic blocker: {site}",
            )

    require(
        seen_override_coordinates == set(overrides)
        and seen_keep_coordinates == set(keep_coordinates)
        and len(accepted_sites) == EXPECTED_ACCEPTED_SITES
        and len(rejected_sites) == EXPECTED_REJECTED_SITES
        and whitespace_changes == EXPECTED_BOUNDARY_WHITESPACE_CHANGES,
        "review decision coverage drifted",
    )
    accepted_roots = {site_root(site) for site in accepted_sites}
    rejected_roots = {site_root(site) for site in rejected_sites}
    require(
        len(accepted_roots) == EXPECTED_ACCEPTED_ROOTS
        and len(rejected_roots) == EXPECTED_REJECTED_ROOTS
        and accepted_roots.isdisjoint(rejected_roots),
        "accepted/rejected root partition drifted",
    )
    pending_coordinates = list(chunk["pending_coordinates"])
    accepted_pending = [
        coordinate
        for coordinate in pending_coordinates
        if parse_coordinate(coordinate)[:2] in accepted_roots
    ]
    blocked_pending = [
        coordinate
        for coordinate in pending_coordinates
        if parse_coordinate(coordinate)[:2] in rejected_roots
    ]
    accepted_overlap = sorted(set(accepted_pending) & overlap)
    blocked_overlap = sorted(set(blocked_pending) & overlap)
    accepted_disjoint = sorted(set(accepted_pending) - overlap)
    require(
        len(accepted_pending) == EXPECTED_ACCEPTED_PENDING
        and len(blocked_pending) == EXPECTED_BLOCKED_PENDING
        and len(accepted_overlap) == EXPECTED_CROSS_RENEWALS
        and len(blocked_overlap) == EXPECTED_CROSS_BLOCKED
        and len(accepted_disjoint) == EXPECTED_DISJOINT_PROMOTIONS
        and coordinate_digest(accepted_pending)
        == EXPECTED_ACCEPTED_PENDING_SHA256
        and coordinate_digest(blocked_pending)
        == EXPECTED_BLOCKED_PENDING_SHA256
        and coordinate_digest(accepted_overlap)
        == EXPECTED_CROSS_RENEWAL_SHA256
        and coordinate_digest(blocked_overlap)
        == EXPECTED_CROSS_BLOCKED_SHA256
        and coordinate_digest(accepted_disjoint)
        == EXPECTED_DISJOINT_PROMOTION_SHA256,
        "pending/cross disposition drifted",
    )
    require(
        coordinate_digest(overrides) == EXPECTED_OVERRIDE_SHA256
        and coordinate_digest(keep_coordinates) == EXPECTED_KEEP_SHA256
        and ASSIGN.site_digest(accepted_sites) == EXPECTED_ACCEPTED_SITE_SHA256
        and ASSIGN.site_digest(rejected_sites) == EXPECTED_REJECTED_SITE_SHA256
        and canonical_sha256(assembly_manifest) == EXPECTED_ASSEMBLY_SHA256
        and len(dependency_assembly_manifest)
        == EXPECTED_DEPENDENCY_ASSEMBLIES
        and canonical_sha256(dependency_assembly_manifest)
        == EXPECTED_DEPENDENCY_ASSEMBLY_SHA256
        and len(required_cross_overrides)
        == EXPECTED_CROSS_REQUIRED_OVERRIDES
        and set(required_cross_overrides).issubset(overrides)
        and coordinate_digest(required_cross_overrides)
        == EXPECTED_CROSS_REQUIRED_OVERRIDE_SHA256
        and len(repair_only_override_coordinates) == 4,
        "review digest contract drifted",
    )
    private_digests = handoff.get("digests", {})
    require(
        private_digests.get("accepted_pending_coordinate_sha256")
        == EXPECTED_ACCEPTED_PENDING_SHA256
        and private_digests.get("blocked_pending_coordinate_sha256")
        == EXPECTED_BLOCKED_PENDING_SHA256
        and private_digests.get("cross_overlap_renewal_sha256")
        == EXPECTED_CROSS_RENEWAL_SHA256
        and private_digests.get("cross_overlap_blocked_sha256")
        == EXPECTED_CROSS_BLOCKED_SHA256
        and private_digests.get("disjoint_potential_promotion_sha256")
        == EXPECTED_DISJOINT_PROMOTION_SHA256
        and private_digests.get("translation_override_coordinate_sha256")
        == EXPECTED_OVERRIDE_SHA256
        and private_digests.get("keep_coordinate_sha256")
        == EXPECTED_KEEP_SHA256
        and private_digests.get("accepted_site_sha256")
        == EXPECTED_ACCEPTED_SITE_SHA256
        and private_digests.get("rejected_site_sha256")
        == EXPECTED_REJECTED_SITE_SHA256
        and private_digests.get("assembly_canonical_sha256")
        == EXPECTED_ASSEMBLY_SHA256
        and private_digests.get("dependency_assembly_canonical_sha256")
        == EXPECTED_DEPENDENCY_ASSEMBLY_SHA256
        and private_digests.get("cross_renewal_required_override_sha256")
        == EXPECTED_CROSS_REQUIRED_OVERRIDE_SHA256,
        "private digest self-binding drifted",
    )

    four_repair_blob = ENGINE.rebuild_packed_with_literals(
        world["candidate_blob"],
        {
            parse_coordinate(coordinate): str(overrides[coordinate])
            for coordinate in repair_only_override_coordinates
        },
    )
    require(
        sha256_bytes(four_repair_blob)
        == EXPECTED_FOUR_REPAIR_ONLY_CANDIDATE_SHA256,
        "four-repair-only candidate drifted",
    )
    proposal_blob = ENGINE.rebuild_packed_with_literals(
        world["candidate_blob"],
        {
            parse_coordinate(coordinate): str(translation)
            for coordinate, translation in overrides.items()
        },
    )
    require(
        sha256_bytes(proposal_blob) == EXPECTED_PROPOSAL_CANDIDATE_SHA256
        and private_digests.get("proposal_candidate_sha256")
        == EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        "review proposal candidate drifted",
    )
    proposal_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(proposal_blob).archive
    )
    changed_roots = {
        root
        for root in candidate_records
        if candidate_records[root].data != proposal_records[root].data
    }
    require(
        changed_roots
        == {parse_coordinate(coordinate)[:2] for coordinate in overrides},
        "proposal changed-root universe drifted",
    )
    for root in changed_roots:
        require(
            record_gap_sha256(candidate_records[root])
            == record_gap_sha256(proposal_records[root]),
            f"proposal control gap changed at {root}",
        )
    return {
        "accepted_roots": accepted_roots,
        "accepted_sites": accepted_sites,
        "assembly_manifest": assembly_manifest,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "dependency_assembly_manifest": dependency_assembly_manifest,
        "four_repair_candidate_sha256":
            sha256_bytes(four_repair_blob),
        "language_counts": dict(language_counts),
        "proposal_blob": proposal_blob,
        "rejected_roots": rejected_roots,
        "rejected_sites": rejected_sites,
        "whitespace_changes": whitespace_changes,
    }


def assert_source_free(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "public review contains CJK dialogue text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public review contains an exact coordinate",
    )
    require(
        '"translation"' not in serialized
        and '"exact_maps"' not in serialized
        and '"site_reviews"' not in serialized,
        "public review leaks private translation structure",
    )


def build_report() -> dict[str, Any]:
    immutable = {
        ASSIGNMENT_BUILDER: EXPECTED_ASSIGNMENT_BUILDER_SHA256,
        ASSIGNMENT_PATH: EXPECTED_ASSIGNMENT_SHA256,
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        OFFICIAL_LEDGER_PATH: EXPECTED_OFFICIAL_LEDGER_SHA256,
        CROSS_BUILDER_PATH: EXPECTED_CROSS_BUILDER_SHA256,
        CROSS_DECISIONS_PATH: EXPECTED_CROSS_DECISIONS_SHA256,
        PRIVATE_REVIEW_PATH: EXPECTED_PRIVATE_REVIEW_SHA256,
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable review input drifted: {path}",
        )
    assignment = load_json_exact(ASSIGNMENT_PATH)
    chunk = assignment["chunks"][CHUNK_ID]
    require(
        chunk.get("chunk_id") == CHUNK_ID
        and chunk.get("ordinal_start") == ORDINAL_START
        and chunk.get("ordinal_end") == ORDINAL_END
        and chunk.get("site_count") == EXPECTED_SITE_COUNT
        and chunk.get("root_count") == EXPECTED_ROOT_COUNT
        and chunk.get("pending_row_upper_bound") == EXPECTED_PENDING
        and chunk.get("site_sha256") == EXPECTED_SITE_SHA256
        and chunk.get("root_sha256") == EXPECTED_ROOT_SHA256
        and chunk.get("pending_sha256") == EXPECTED_PENDING_SHA256
        and chunk.get("cross_family_overlap_sha256") == EXPECTED_OVERLAP_SHA256
        and chunk.get("disjoint_pending_sha256") == EXPECTED_DISJOINT_SHA256,
        "chunk assignment contract drifted",
    )
    require(
        LIVE_STEAM_PK.is_file()
        and sha256_file(LIVE_STEAM_PK) == EXPECTED_STEAM_PK_SHA256,
        "live Steam PK msggame drifted before review",
    )
    steam_before = sha256_file(LIVE_STEAM_PK)
    world = load_world()
    handoff = load_json_exact(PRIVATE_REVIEW_PATH)
    validated = validate_private(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    steam_after = sha256_file(LIVE_STEAM_PK)
    require(steam_before == steam_after, "live Steam changed during review")

    report: dict[str, Any] = {
        "distribution_policy": {
            "private_review_contains_dialogue_bodies": True,
            "private_review_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
        },
        "inputs": {
            "assignment_private_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "assignment_public_sha256": EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
            "corrected_cross_commit_bound": True,
            "corrected_cross_decisions_sha256":
                EXPECTED_CROSS_DECISIONS_SHA256,
            "cross_predecessor_candidate_sha256":
                EXPECTED_CROSS_CANDIDATE_SHA256,
            "official_integrated_ledger_sha256":
                EXPECTED_OFFICIAL_LEDGER_SHA256,
            "private_review_sha256": EXPECTED_PRIVATE_REVIEW_SHA256,
        },
        "method": METHOD,
        "proof": {
            "all_60_sites_freshly_reviewed": True,
            "all_accepted_current_relative_raw_g1n_nonexpanding": True,
            "all_accepted_register_branches_proven": True,
            "all_changed_record_control_gaps_preserved": True,
            "assembly_branches_recorded": EXPECTED_ASSEMBLY_COUNT,
            "assembly_canonical_sha256": EXPECTED_ASSEMBLY_SHA256,
            "auxiliary_language_available_counts":
                validated["language_counts"],
            "blocker_reason_counts": validated["blocker_counts"],
            "historical_term_review_sites": EXPECTED_SITE_COUNT,
            "intentional_literal_boundary_whitespace_changes":
                validated["whitespace_changes"],
            "jp_authority_sites": EXPECTED_SITE_COUNT,
            "msggame_event_912px_rule_applied": False,
            "repaired_cross_dependency_selector1096_branches":
                EXPECTED_DEPENDENCY_ASSEMBLIES,
            "repaired_cross_dependency_selector1096_sha256":
                EXPECTED_DEPENDENCY_ASSEMBLY_SHA256,
            "repaired_cross_selector1174_branches": 14,
            "speaker_tone_review_sites": EXPECTED_SITE_COUNT,
            "terminal_branch_count_per_site": len(TERMINALS),
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": {
            "accepted_pending_coordinate_count": EXPECTED_ACCEPTED_PENDING,
            "accepted_pending_coordinate_sha256":
                EXPECTED_ACCEPTED_PENDING_SHA256,
            "accepted_root_count": EXPECTED_ACCEPTED_ROOTS,
            "accepted_site_count": EXPECTED_ACCEPTED_SITES,
            "accepted_site_sha256": EXPECTED_ACCEPTED_SITE_SHA256,
            "blocked_cross_overlap_count": EXPECTED_CROSS_BLOCKED,
            "blocked_cross_overlap_sha256": EXPECTED_CROSS_BLOCKED_SHA256,
            "blocked_pending_coordinate_count": EXPECTED_BLOCKED_PENDING,
            "blocked_pending_coordinate_sha256":
                EXPECTED_BLOCKED_PENDING_SHA256,
            "cross_verification_renewal_count": EXPECTED_CROSS_RENEWALS,
            "cross_verification_renewal_sha256":
                EXPECTED_CROSS_RENEWAL_SHA256,
            "cross_renewal_required_override_count":
                EXPECTED_CROSS_REQUIRED_OVERRIDES,
            "cross_renewal_required_override_sha256":
                EXPECTED_CROSS_REQUIRED_OVERRIDE_SHA256,
            "disjoint_potential_promotion_count":
                EXPECTED_DISJOINT_PROMOTIONS,
            "disjoint_potential_promotion_sha256":
                EXPECTED_DISJOINT_PROMOTION_SHA256,
            "keep_coordinate_count": EXPECTED_KEEPS,
            "keep_coordinate_sha256": EXPECTED_KEEP_SHA256,
            "nonpending_translation_override_count":
                EXPECTED_NONPENDING_OVERRIDES,
            "pending_translation_override_count":
                EXPECTED_PENDING_OVERRIDES,
            "four_repair_only_candidate_sha256":
                EXPECTED_FOUR_REPAIR_ONLY_CANDIDATE_SHA256,
            "full_chunk_proposal_candidate_sha256":
                EXPECTED_PROPOSAL_CANDIDATE_SHA256,
            "rejected_root_count": EXPECTED_REJECTED_ROOTS,
            "rejected_site_count": EXPECTED_REJECTED_SITES,
            "rejected_site_sha256": EXPECTED_REJECTED_SITE_SHA256,
            "translation_override_count": EXPECTED_REWRITES,
            "translation_override_coordinate_sha256":
                EXPECTED_OVERRIDE_SHA256,
        },
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "cross_family_overlap_row_count": 13,
            "disjoint_pending_row_count": 122,
            "ordinal_end": ORDINAL_END,
            "ordinal_start": ORDINAL_START,
            "pending_row_upper_bound": EXPECTED_PENDING,
            "root_count": EXPECTED_ROOT_COUNT,
            "selector": SELECTOR,
            "site_count": EXPECTED_SITE_COUNT,
            "terminal_count": len(TERMINALS),
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    report["guards"] = {
        "payload_without_guards_canonical_sha256": canonical_sha256(report),
        "steam_archive_sha256_after": steam_after,
        "steam_archive_sha256_before": steam_before,
    }
    assert_source_free(report)
    return report


def serialized_report() -> bytes:
    return canonical_bytes(build_report()) + b"\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.output.resolve(strict=False) == DEFAULT_OUTPUT.resolve(strict=False),
        "selector-1174 public report must use its fixed tracked path",
    )
    content = serialized_report()
    file_sha256 = sha256_bytes(content)
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        require(
            file_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            "selector-1174 public report hash drifted",
        )
    if args.check:
        require(args.output.is_file(), f"review report is absent: {args.output}")
        require(
            args.output.read_bytes() == content,
            "selector-1174 public report content drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "accepted_pending": EXPECTED_ACCEPTED_PENDING,
                "cross_renewals": EXPECTED_CROSS_RENEWALS,
                "disjoint_potential_promotions":
                    EXPECTED_DISJOINT_PROMOTIONS,
                "file_sha256": file_sha256,
                "output": str(args.output),
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
