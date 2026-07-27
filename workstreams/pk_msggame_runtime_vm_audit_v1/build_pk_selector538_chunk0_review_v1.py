#!/usr/bin/env python3
"""Validate selector 538 chunk 0 and build its source-free proposal report.

Dialogue bodies and exact translation maps are read only from the private
handoff below ``tmp``.  This builder does not mutate a shared decision ledger
or the Steam installation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
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
ASSIGNMENT_BUILDER = WORKSTREAM / "build_pk_selector538_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "family538_assignment.private.v1.json"
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk0_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk0_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector538-chunk0-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector538-chunk0-review-proposal.v1"
METHOD = "reversed_vm_pk_selector538_chunk0_full_caller_review"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))
ORDINAL_START = 0
ORDINAL_END = 64
EXPECTED_SITE_COUNT = 65
EXPECTED_ASSEMBLY_COUNT = 455
EXPECTED_ACCEPTED = 35
EXPECTED_REWRITE = 33
EXPECTED_KEEP = 2
EXPECTED_REJECT = 30
EXPECTED_ACCEPTED_ASSEMBLIES = 245
EXPECTED_REJECTED_ASSEMBLIES = 210

EXPECTED_ASSIGNMENT_SHA256 = (
    "57FBEE8EEC3551DAD8A7F1BB77CD7B2E2CF08109CB3A912452BE8244BB0FAACF"
)
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_LEDGER_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "6A8C1B51CD2A0AA4DD76E8C937710D3EC575F8E47F5D752879FC670E500870DD"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "9801E563C8F53B2C98D05289B16974B0CC90B6FAD8A3EBBEE357DB220403584E"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "F3369B3FD77F9CA08F5C418FFC21CC7999D5F0AEA954E1B5E980E0DF5964E382"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 144

# Frozen after the private handoff and public proposal are independently
# reproduced.
EXPECTED_PRIVATE_HANDOFF_SHA256: str | None = (
    "9A8CE09CCA100FCA9C5F9C148EDA38C043D8737218F2B4A11F3CDF2B7A7A92BF"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256: str | None = (
    "583E53881F3099163F4E43E955C9363EDD597F82CA5B280BA96231A02A7673B4"
)
EXPECTED_REWRITE_COORDINATE_SHA256: str | None = (
    "7010E3B363FD8786E9B92D5F74C023DE47F96F0F9F4771F67E216D9A7E78E1A0"
)
EXPECTED_KEEP_COORDINATE_SHA256: str | None = (
    "BDB7269F1EA20733F0195703646D92E025B8B59C6E92FF53B2A775895F1F03D2"
)
EXPECTED_REJECT_COORDINATE_SHA256: str | None = (
    "4AB2A1BB0AB1371F509193D1BB57227412BBD1E2090DED9B0E528AFEAE83FF00"
)
EXPECTED_ACCEPTED_SITE_SHA256: str | None = (
    "4A51986D3BE5FA499C62825052DD49AF39D350062E6B1685C85A6FF878583B4B"
)
EXPECTED_REJECTED_SITE_SHA256: str | None = (
    "CB2B58B7D51FBB6B94025E47BC83F587B7549F0235BAE61D747264E152C29FE1"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "83E9AAF749B93BCF6B41BCA719CEB24EC2EF2FB0BFC3CF9883B67A7679762EA3"
)
EXPECTED_ACCEPTED_ROOT_SHA256: str | None = (
    "6ABC8E35F2FD16D90DBECC7BA9A75E97B6DEDB862F4320488A50269F9ADB18F6"
)
EXPECTED_REJECTED_ROOT_SHA256: str | None = (
    "EF0B0A6AA45372F626DC4BF042231FB84A17664153164D8092E03D2ED44448CB"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256: str | None = (
    "FCF5CAD181AA01E190336B0CD206E7D0F518AA5227BBB8693F05E4284A5E66BF"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256: str | None = (
    "42343A8FB2DCE2967AE8D3CB6373D5F3DFA8FD10C47D9387E01001DEA5AA7706"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "55D558207B2C26E9292BF1D204E81F29E124D72EFB8A029870B051EF1A953041"
)


class ReviewError(ValueError):
    """Raised when a frozen selector 538 chunk-0 contract drifts."""


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


ASSIGN = load_module(ASSIGNMENT_BUILDER, "pk_selector538_chunk0_assignment_v1")
CALLER = ASSIGN.CALLER
BASE_AUDIT = CALLER.BASE_AUDIT
ENGINE = CALLER.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def coordinate_digest(values: Iterable[str]) -> str:
    return CALLER.coordinate_digest(values)


def site_digest(values: Iterable[str]) -> str:
    return ASSIGN.site_digest(values)


def root_digest(values: Iterable[tuple[int, int]]) -> str:
    return ASSIGN.root_digest(values)


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return CALLER.parse_coordinate(value)


def site_root(site: str) -> tuple[int, int]:
    block_id, record_id, _gap_id, _offset = map(int, site.split(":"))
    return block_id, record_id


def line_metric(value: str) -> dict[str, Any]:
    full_width_count = 0
    half_width_count = 0
    visible: list[str] = []
    for character in value:
        if unicodedata.category(character) == "Cc":
            continue
        visible.append(character)
        if unicodedata.east_asian_width(character) in {"W", "F", "A"}:
            full_width_count += 1
        else:
            half_width_count += 1
    return {
        "full_width_count": full_width_count,
        "half_width_count": half_width_count,
        "raw_g1n_width_px": (
            48 * full_width_count + 24 * half_width_count
        ),
        "visible": "".join(visible),
    }


def line_metrics(value: str) -> list[dict[str, Any]]:
    return [line_metric(line) for line in value.split("\n")]


def current_relative_nonexpanding(
    reviewed: Sequence[Mapping[str, Any]],
    current: Sequence[Mapping[str, Any]],
) -> bool:
    return len(reviewed) == len(current) and all(
        int(reviewed_line["raw_g1n_width_px"])
        <= int(current_line["raw_g1n_width_px"])
        for reviewed_line, current_line in zip(reviewed, current)
    )


def outer_whitespace_signature(value: str) -> dict[str, str]:
    prefix_length = len(value) - len(value.lstrip())
    suffix_length = len(value) - len(value.rstrip())
    return {
        "leading": value[:prefix_length],
        "trailing": value[len(value) - suffix_length :] if suffix_length else "",
    }


def record_gap_sha256(record: Any) -> str:
    framed = b"".join(
        len(gap).to_bytes(4, "little") + gap
        for gap in BASE_AUDIT.literal_gaps(record)
    )
    return sha256_bytes(framed)


def adjacent_literals(
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> tuple[str, str]:
    return ASSIGN.adjacent_literals(records, site)


def terminal_literals(
    records: Mapping[tuple[int, int], Any],
) -> dict[int, str]:
    return {
        terminal: BASE_AUDIT.parse_record_literals(
            records[(0, terminal)]
        )[0].text
        for terminal in TERMINALS
    }


def load_json_exact(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM rejected: {path}")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewError(f"invalid strict UTF-8 JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector 538 assignment hash drifted",
    )
    assignment = load_json_exact(ASSIGNMENT_PATH)
    require(
        assignment.get("schema") == ASSIGN.SCHEMA,
        "selector 538 assignment schema drifted",
    )
    chunk = assignment["chunks"][0]
    require(
        chunk.get("chunk_id") == 0
        and chunk.get("ordinal_start") == ORDINAL_START
        and chunk.get("ordinal_end") == ORDINAL_END
        and chunk.get("site_count") == EXPECTED_SITE_COUNT
        and chunk.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and chunk.get("root_sha256") == EXPECTED_CHUNK_ROOT_SHA256
        and chunk.get("pending_coordinate_sha256")
        == EXPECTED_PENDING_COORDINATE_SHA256
        and chunk.get("pending_row_upper_bound")
        == EXPECTED_PENDING_ROW_UPPER_BOUND,
        "selector 538 chunk-0 assignment drifted",
    )
    return assignment, chunk


def load_world() -> dict[str, Any]:
    *_unused, bundle = ASSIGN.FINAL.build_outputs()
    analysis = bundle["analysis"]
    candidate_blob = analysis["candidate_blob"]
    require(
        sha256_bytes(candidate_blob) == EXPECTED_BASELINE_CANDIDATE_SHA256,
        "baseline candidate drifted",
    )
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    resource = prepared.resources["pk_msggame"]
    current_records = ENGINE.archive_records(resource.current_archive)
    language_records = {
        "jp": ENGINE.archive_records(resource.pristine_archive),
        "sc": ENGINE.archive_records(resource.context_archives["SC"]),
        "tc": ENGINE.archive_records(resource.context_archives["TC"]),
        "en": ENGINE.archive_records(resource.context_archives["EN"]),
    }
    return {
        "candidate_blob": candidate_blob,
        "candidate_records": analysis["candidate_records"],
        "current_records": current_records,
        "language_records": language_records,
    }


def validate_context(
    recorded: Mapping[str, Any],
    *,
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> None:
    left, right = adjacent_literals(records, site)
    require(
        recorded.get("left") == left
        and recorded.get("right") == right
        and recorded.get("joined_utf8_sha256")
        == sha256_bytes((left + right).encode("utf-8")),
        f"private multilingual context drifted at {site}",
    )


def validate_private_handoff(
    handoff: Mapping[str, Any],
    *,
    assignment: Mapping[str, Any],
    chunk: Mapping[str, Any],
    world: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        handoff.get("schema") == PRIVATE_SCHEMA,
        "private handoff schema drifted",
    )
    privacy = handoff.get("privacy", {})
    scope = handoff.get("scope", {})
    counts = handoff.get("counts", {})
    require(
        privacy.get("classification") == "private"
        and privacy.get("contains_dialogue_bodies") is True
        and privacy.get("public") is False
        and privacy.get("shared_integration_mutated") is False
        and privacy.get("steam_write_performed") is False,
        "private handoff privacy contract drifted",
    )
    require(
        scope.get("assignment_sha256") == EXPECTED_ASSIGNMENT_SHA256
        and scope.get("baseline_candidate_sha256")
        == EXPECTED_BASELINE_CANDIDATE_SHA256
        and scope.get("integrated_ledger_sha256") == EXPECTED_LEDGER_SHA256
        and scope.get("selector_coordinate") == f"0:{SELECTOR}:0"
        and scope.get("ordinal_start") == ORDINAL_START
        and scope.get("ordinal_end") == ORDINAL_END
        and scope.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and tuple(scope.get("terminal_coordinates", ()))
        == tuple(f"0:{terminal}:0" for terminal in TERMINALS),
        "private handoff scope drifted",
    )
    require(
        counts
        == {
            "accepted": EXPECTED_ACCEPTED,
            "accepted_assemblies": EXPECTED_ACCEPTED_ASSEMBLIES,
            "assemblies": EXPECTED_ASSEMBLY_COUNT,
            "keep": EXPECTED_KEEP,
            "reject": EXPECTED_REJECT,
            "rejected_assemblies": EXPECTED_REJECTED_ASSEMBLIES,
            "rewrite": EXPECTED_REWRITE,
            "sites": EXPECTED_SITE_COUNT,
        },
        "private handoff counts drifted",
    )

    site_rows = handoff.get("site_reviews")
    require(
        isinstance(site_rows, list) and len(site_rows) == EXPECTED_SITE_COUNT,
        "private site review cardinality drifted",
    )
    assignment_rows = assignment["site_assignments"][
        ORDINAL_START : ORDINAL_END + 1
    ]
    exact_maps = handoff.get("exact_maps", {})
    rewrite_map = exact_maps.get("rewrite")
    keep_map = exact_maps.get("keep")
    reject_map = exact_maps.get("reject")
    reviewed_map = exact_maps.get("reviewed")
    require(
        all(
            isinstance(value, dict)
            for value in (rewrite_map, keep_map, reject_map, reviewed_map)
        ),
        "private exact maps are absent",
    )

    decisions: Counter[str] = Counter()
    rewrite_coordinates: set[str] = set()
    keep_coordinates: set[str] = set()
    reject_coordinates: set[str] = set()
    accepted_sites: list[str] = []
    rejected_sites: list[str] = []
    assembly_manifest: list[list[Any]] = []
    candidate_records = world["candidate_records"]
    current_records = world["current_records"]
    terminal_candidate = terminal_literals(candidate_records)
    terminal_current = terminal_literals(current_records)

    for assignment_row, row in zip(assignment_rows, site_rows):
        ordinal = int(assignment_row["ordinal"])
        site = str(assignment_row["site"])
        coordinate = str(assignment_row["left_coordinate"])
        decision = str(row.get("decision"))
        reviewed_left = row.get("reviewed_left_translation")
        require(
            row.get("ordinal") == ordinal
            and row.get("site") == site
            and row.get("left_coordinate") == coordinate
            and decision in {"rewrite", "keep", "reject"}
            and isinstance(reviewed_left, str),
            f"private site identity/decision drifted at ordinal {ordinal}",
        )
        decisions[decision] += 1
        if decision == "rewrite":
            rewrite_coordinates.add(coordinate)
            accepted_sites.append(site)
        elif decision == "keep":
            keep_coordinates.add(coordinate)
            accepted_sites.append(site)
        else:
            reject_coordinates.add(coordinate)
            rejected_sites.append(site)

        baseline_left, baseline_right = adjacent_literals(
            candidate_records, site
        )
        current_left, current_right = adjacent_literals(current_records, site)
        require(
            row.get("baseline_candidate_left") == baseline_left
            and row.get("baseline_candidate_right") == baseline_right
            and row.get("current_left") == current_left
            and row.get("current_right") == current_right,
            f"private Korean context drifted at {site}",
        )
        require(
            reviewed_map.get(coordinate) == reviewed_left,
            f"private reviewed map drifted at {coordinate}",
        )
        if decision == "rewrite":
            require(
                rewrite_map.get(coordinate) == reviewed_left
                and reviewed_left != baseline_left,
                f"private rewrite map drifted at {coordinate}",
            )
        elif decision == "keep":
            require(
                keep_map.get(coordinate) == reviewed_left
                and reviewed_left == baseline_left,
                f"private keep map drifted at {coordinate}",
            )
        else:
            require(
                isinstance(reject_map.get(coordinate), str)
                and reject_map.get(coordinate) == row.get("reject_reason"),
                f"private reject map drifted at {coordinate}",
            )

        authority = row.get("multilingual_authority", {})
        require(
            authority.get("jp_is_semantic_authority") is True
            and authority.get("fresh_review_completed") is True
            and authority.get("speaker_tone_reviewed") is True
            and authority.get("historical_terms_reviewed") is True,
            f"private semantic proof drifted at {site}",
        )
        for language in ("jp", "sc", "tc", "en"):
            language_context = authority.get(language)
            require(
                isinstance(language_context, dict),
                f"private {language} context absent at {site}",
            )
            validate_context(
                language_context,
                records=world["language_records"][language],
                site=site,
            )
            require(
                language_context.get("available")
                is bool(assignment_row["language_available"][language]),
                f"private {language} availability drifted at {site}",
            )

        control = row.get("control_and_protected_proof", {})
        root = site_root(site)
        require(
            control.get("baseline_record_gap_sha256")
            == record_gap_sha256(candidate_records[root])
            and control.get("reviewed_outer_whitespace_signature")
            == outer_whitespace_signature(reviewed_left)
            and control.get("baseline_outer_whitespace_signature")
            == outer_whitespace_signature(baseline_left)
            and control.get("outer_whitespace_preserved") is True
            and control.get("literal_linebreak_count_preserved") is True,
            f"private control/protected proof drifted at {site}",
        )

        branches = row.get("assemblies")
        require(
            isinstance(branches, list) and len(branches) == len(TERMINALS),
            f"private assembly branch count drifted at {site}",
        )
        all_width = True
        all_register = True
        for terminal, branch in zip(TERMINALS, branches):
            reviewed_assembly = (
                reviewed_left
                + terminal_candidate[terminal]
                + baseline_right
            )
            current_assembly = (
                current_left + terminal_current[terminal] + current_right
            )
            reviewed_lines = line_metrics(reviewed_assembly)
            current_lines = line_metrics(current_assembly)
            nonexpanding = current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            grammar_compatible = bool(row.get("grammar_compatible"))
            register_proven = decision != "reject" and grammar_compatible
            require(
                branch.get("terminal_coordinate") == f"0:{terminal}:0"
                and branch.get("register")
                == ("plain" if terminal in {1917, 1922} else "polite")
                and branch.get("reviewed_terminal") == terminal_candidate[terminal]
                and branch.get("current_terminal") == terminal_current[terminal]
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
                f"private assembly proof drifted at {site}/0:{terminal}:0",
            )
            all_width = all_width and nonexpanding
            all_register = all_register and register_proven
            assembly_manifest.append(
                [
                    ordinal,
                    site,
                    terminal,
                    decision,
                    sha256_bytes(reviewed_assembly.encode("utf-8")),
                    sha256_bytes(current_assembly.encode("utf-8")),
                    nonexpanding,
                    register_proven,
                ]
            )
        require(
            row.get("all_seven_width_branches_nonexpanding") is all_width
            and row.get("all_seven_register_branches_proven") is all_register,
            f"private seven-branch summary drifted at {site}",
        )
        if decision != "reject":
            require(
                all_width and all_register,
                f"accepted site lacks seven-branch proof: {site}",
            )
        else:
            require(
                not (all_width and all_register),
                f"rejected site has no blocker: {site}",
            )

    require(
        decisions
        == Counter(
            {
                "rewrite": EXPECTED_REWRITE,
                "keep": EXPECTED_KEEP,
                "reject": EXPECTED_REJECT,
            }
        )
        and set(rewrite_map) == rewrite_coordinates
        and set(keep_map) == keep_coordinates
        and set(reject_map) == reject_coordinates
        and set(reviewed_map)
        == rewrite_coordinates | keep_coordinates | reject_coordinates,
        "private decision/exact-map coverage drifted",
    )

    replacements = {
        parse_coordinate(coordinate): str(text)
        for coordinate, text in rewrite_map.items()
    }
    proposal_blob = BASE_AUDIT.rebuild_packed_with_literals(
        world["candidate_blob"],
        replacements,
    )
    proposal_records = BASE_AUDIT.records_from_blob(proposal_blob)
    changed_roots = {
        root
        for root in candidate_records
        if candidate_records[root].data != proposal_records[root].data
    }
    expected_changed_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in rewrite_map
    }
    require(
        changed_roots == expected_changed_roots,
        "proposal changed-record universe drifted",
    )
    for root in changed_roots:
        require(
            record_gap_sha256(candidate_records[root])
            == record_gap_sha256(proposal_records[root]),
            f"proposal control gaps changed at {root}",
        )
    for row in site_rows:
        root = site_root(str(row["site"]))
        control = row["control_and_protected_proof"]
        baseline_gap_sha256 = record_gap_sha256(candidate_records[root])
        proposal_gap_sha256 = record_gap_sha256(proposal_records[root])
        require(
            control.get("proposal_record_gap_sha256")
            == proposal_gap_sha256
            and control.get("record_control_gaps_preserved") is True
            and baseline_gap_sha256 == proposal_gap_sha256,
            f"private proposal control proof drifted at {row['site']}",
        )
    proposal_candidate_sha256 = sha256_bytes(proposal_blob)
    require(
        handoff.get("digests", {}).get("proposal_candidate_sha256")
        == proposal_candidate_sha256
        and handoff.get("digests", {}).get("assembly_canonical_sha256")
        == canonical_sha256(assembly_manifest),
        "private proposal/assembly digest drifted",
    )
    return {
        "accepted_sites": accepted_sites,
        "assembly_manifest": assembly_manifest,
        "keep_map": keep_map,
        "proposal_candidate_sha256": proposal_candidate_sha256,
        "reject_map": reject_map,
        "rejected_sites": rejected_sites,
        "rewrite_map": rewrite_map,
        "site_rows": site_rows,
    }


def build_report() -> tuple[dict[str, Any], dict[str, Any]]:
    assignment, chunk = load_assignment()
    live_steam_path = Path(CALLER.LIVE_STEAM_PK)
    require(live_steam_path.is_file(), "live Steam PK msggame is absent")
    steam_before = sha256_file(live_steam_path)
    world = load_world()
    handoff = load_json_exact(PRIVATE_HANDOFF_PATH)
    private_sha256 = sha256_file(PRIVATE_HANDOFF_PATH)
    if EXPECTED_PRIVATE_HANDOFF_SHA256 is not None:
        require(
            private_sha256 == EXPECTED_PRIVATE_HANDOFF_SHA256,
            "private handoff hash drifted",
        )
    validated = validate_private_handoff(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    steam_after = sha256_file(live_steam_path)
    require(steam_before == steam_after, "Steam archive changed during review")

    rewrite_coordinates = sorted(
        validated["rewrite_map"], key=parse_coordinate
    )
    keep_coordinates = sorted(validated["keep_map"], key=parse_coordinate)
    reject_coordinates = sorted(validated["reject_map"], key=parse_coordinate)
    accepted_sites = sorted(validated["accepted_sites"])
    rejected_sites = sorted(validated["rejected_sites"])
    accepted_roots = {site_root(site) for site in accepted_sites}
    rejected_roots = {site_root(site) for site in rejected_sites}
    pending_coordinates = list(chunk["pending_coordinates"])
    potential_promotion_coordinates = [
        coordinate
        for coordinate in pending_coordinates
        if parse_coordinate(coordinate)[:2] in accepted_roots
    ]
    blocked_pending_coordinates = [
        coordinate
        for coordinate in pending_coordinates
        if parse_coordinate(coordinate)[:2] in rejected_roots
    ]
    require(
        len(accepted_roots) == EXPECTED_ACCEPTED
        and len(rejected_roots) == EXPECTED_REJECT
        and len(potential_promotion_coordinates) == 65
        and len(blocked_pending_coordinates) == 79
        and len(potential_promotion_coordinates)
        + len(blocked_pending_coordinates)
        == EXPECTED_PENDING_ROW_UPPER_BOUND,
        "chunk-0 pending-root partition drifted",
    )
    site_rows = validated["site_rows"]
    language_counts = {
        language: sum(
            bool(
                row["multilingual_authority"][language]["available"]
            )
            for row in site_rows
        )
        for language in ("jp", "sc", "tc", "en")
    }
    blocker_counts = Counter(
        str(row["reject_reason"]) for row in site_rows
        if row["decision"] == "reject"
    )

    report: dict[str, Any] = {
        "distribution_policy": {
            "private_handoff_contains_dialogue_bodies": True,
            "private_handoff_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "inputs": {
            "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "baseline_candidate_sha256": EXPECTED_BASELINE_CANDIDATE_SHA256,
            "integrated_ledger_sha256": EXPECTED_LEDGER_SHA256,
        },
        "method": METHOD,
        "proof": {
            "accepted_assembly_branches": EXPECTED_ACCEPTED_ASSEMBLIES,
            "all_65_sites_classified": True,
            "all_accepted_current_relative_raw_g1n_nonexpanding": True,
            "all_accepted_register_branches_proven": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "all_outer_whitespace_signatures_preserved": True,
            "assembly_branches_recorded": EXPECTED_ASSEMBLY_COUNT,
            "assembly_canonical_sha256": canonical_sha256(
                validated["assembly_manifest"]
            ),
            "auxiliary_language_available_counts": language_counts,
            "blocker_reason_counts": dict(sorted(blocker_counts.items())),
            "fresh_semantic_review_sites": EXPECTED_SITE_COUNT,
            "historical_term_review_sites": EXPECTED_SITE_COUNT,
            "jp_authority_sites": EXPECTED_SITE_COUNT,
            "rejected_assembly_branches": EXPECTED_REJECTED_ASSEMBLIES,
            "speaker_tone_review_sites": EXPECTED_SITE_COUNT,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": {
            "accepted_root_count": len(accepted_roots),
            "accepted_root_sha256": root_digest(accepted_roots),
            "accepted_site_count": EXPECTED_ACCEPTED,
            "accepted_site_sha256": site_digest(accepted_sites),
            "blocked_pending_coordinate_count":
                len(blocked_pending_coordinates),
            "blocked_pending_coordinate_sha256": coordinate_digest(
                blocked_pending_coordinates
            ),
            "keep_coordinate_count": EXPECTED_KEEP,
            "keep_coordinate_sha256": coordinate_digest(keep_coordinates),
            "potential_promotion_coordinate_count":
                len(potential_promotion_coordinates),
            "potential_promotion_coordinate_sha256": coordinate_digest(
                potential_promotion_coordinates
            ),
            "proposal_candidate_sha256":
                validated["proposal_candidate_sha256"],
            "reject_coordinate_count": EXPECTED_REJECT,
            "reject_coordinate_sha256": coordinate_digest(reject_coordinates),
            "rejected_root_count": len(rejected_roots),
            "rejected_root_sha256": root_digest(rejected_roots),
            "rejected_site_count": EXPECTED_REJECT,
            "rejected_site_sha256": site_digest(rejected_sites),
            "rewrite_coordinate_count": EXPECTED_REWRITE,
            "rewrite_coordinate_sha256": coordinate_digest(
                rewrite_coordinates
            ),
        },
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": 0,
            "ordinal_end": ORDINAL_END,
            "ordinal_start": ORDINAL_START,
            "pending_coordinate_sha256":
                EXPECTED_PENDING_COORDINATE_SHA256,
            "pending_row_upper_bound": EXPECTED_PENDING_ROW_UPPER_BOUND,
            "root_count": chunk["root_count"],
            "root_sha256": EXPECTED_CHUNK_ROOT_SHA256,
            "selector": SELECTOR,
            "site_count": EXPECTED_SITE_COUNT,
            "site_sha256": EXPECTED_CHUNK_SITE_SHA256,
            "terminal_count": len(TERMINALS),
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    report["guards"] = {
        "private_handoff_sha256": private_sha256,
        "report_payload_sha256": canonical_sha256(report),
        "steam_archive_sha256_before": steam_before,
        "steam_archive_sha256_after": steam_after,
    }

    frozen = {
        "accepted_root_sha256": report["result"]["accepted_root_sha256"],
        "accepted_site_sha256": report["result"]["accepted_site_sha256"],
        "assembly_sha256": report["proof"]["assembly_canonical_sha256"],
        "blocked_pending_coordinate_sha256": report["result"][
            "blocked_pending_coordinate_sha256"
        ],
        "keep_coordinate_sha256": report["result"][
            "keep_coordinate_sha256"
        ],
        "private_handoff_sha256": private_sha256,
        "proposal_candidate_sha256": report["result"][
            "proposal_candidate_sha256"
        ],
        "potential_promotion_coordinate_sha256": report["result"][
            "potential_promotion_coordinate_sha256"
        ],
        "reject_coordinate_sha256": report["result"][
            "reject_coordinate_sha256"
        ],
        "rejected_root_sha256": report["result"]["rejected_root_sha256"],
        "rejected_site_sha256": report["result"]["rejected_site_sha256"],
        "rewrite_coordinate_sha256": report["result"][
            "rewrite_coordinate_sha256"
        ],
    }
    return report, frozen


def validate_frozen(frozen: Mapping[str, str]) -> None:
    expected = {
        "accepted_root_sha256": EXPECTED_ACCEPTED_ROOT_SHA256,
        "accepted_site_sha256": EXPECTED_ACCEPTED_SITE_SHA256,
        "assembly_sha256": EXPECTED_ASSEMBLY_SHA256,
        "blocked_pending_coordinate_sha256":
            EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256,
        "keep_coordinate_sha256": EXPECTED_KEEP_COORDINATE_SHA256,
        "private_handoff_sha256": EXPECTED_PRIVATE_HANDOFF_SHA256,
        "proposal_candidate_sha256": EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        "potential_promotion_coordinate_sha256":
            EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256,
        "reject_coordinate_sha256": EXPECTED_REJECT_COORDINATE_SHA256,
        "rejected_root_sha256": EXPECTED_REJECTED_ROOT_SHA256,
        "rejected_site_sha256": EXPECTED_REJECTED_SITE_SHA256,
        "rewrite_coordinate_sha256": EXPECTED_REWRITE_COORDINATE_SHA256,
    }
    for key, value in expected.items():
        if value is not None:
            require(frozen[key] == value, f"frozen {key} drifted")


def serialized_report() -> tuple[bytes, dict[str, str]]:
    report, frozen = build_report()
    validate_frozen(frozen)
    return canonical_bytes(report) + b"\n", frozen


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    content, frozen = serialized_report()
    file_sha256 = sha256_bytes(content)
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        require(
            file_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            "public proposal file hash drifted",
        )
    if args.check:
        require(args.output.is_file(), f"proposal is absent: {args.output}")
        require(
            args.output.read_bytes() == content,
            "public proposal content drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "file_sha256": file_sha256,
                "frozen": frozen,
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
