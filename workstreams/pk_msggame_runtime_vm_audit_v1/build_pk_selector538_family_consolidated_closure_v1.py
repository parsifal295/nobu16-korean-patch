#!/usr/bin/env python3
"""Consolidate selector-538 chunks 0..3 into one exact closure family.

Each independent chunk was proved against the immutable post-selector-1066
checkpoint.  Their 420 renewal coordinates are the same, while promotion and
override sets are pairwise disjoint.  Applying the chunk decision files in
sequence would therefore discard earlier renewal overrides.  This builder
instead validates every frozen input and constructs the exact union once.

Dialogue-bearing decisions stay below ``tmp``.  The tracked coverage and
promotion reports contain only counts, coordinates hashes, and cryptographic
bindings.  Steam and release checkpoints are never written.
"""

from __future__ import annotations

import argparse
import copy
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
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"

CHUNK_BUILDER_PATHS = tuple(
    WORKSTREAM / f"build_pk_selector538_chunk{chunk}_closure_v1.py"
    for chunk in range(4)
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
)
OFFICIAL_PREDECESSOR_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_family_consolidated_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_family_consolidated_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_family_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_family_consolidated_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-selector538-family-consolidated-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-selector538-family-consolidated-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector538-family-consolidated-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = (
    "nobu16.kr.pk-selector538-family-consolidated-exact-override.v1"
)
METHOD = "reversed_vm_pk_selector538_chunks_0_3_consolidated_closure"
UPDATE_ACTION_FIELD = "selector538_family_update_action"
OVERRIDE_FIELD = "selector538_family_exact_override_evidence"
SELECTOR = 538

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_OFFICIAL_PREDECESSOR_PRIVATE_SHA256 = (
    "6945B4CBAD745A808CE306599FCC5BB7C17068414AD7B085E59B02BC20818165"
)
EXPECTED_OFFICIAL_PREDECESSOR_PUBLIC_SHA256 = (
    "B49011D2FA5BB8018D9852106461367439D4E018DF3F3F80D2455FCB0729A77D"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_OFFICIAL_PREDECESSOR_PENDING = 8_113
EXPECTED_STANDALONE_PENDING_AFTER = 7_936
EXPECTED_PENDING_AFTER = 7_901
EXPECTED_DECISION_ROWS = 697
EXPECTED_PROMOTION_ROWS = 277
EXPECTED_ALREADY_PROMOTED_ROWS = 65
EXPECTED_INCREMENTAL_PROMOTION_ROWS = 212
EXPECTED_RENEWAL_ROWS = 420
EXPECTED_OVERRIDE_ROWS = 142
EXPECTED_ACCEPTED_ASSEMBLIES = 1_057
EXPECTED_TRANSLATION_SINGLE_VARIANT_ROWS = 335
EXPECTED_TRANSLATION_TWO_VARIANT_ROWS = 85
EXPECTED_PAIRWISE_DECISION_OVERLAP = 420
EXPECTED_PAIRWISE_PROMOTION_OVERLAP = 0
EXPECTED_PAIRWISE_OVERRIDE_OVERLAP = 0
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 220,
    "translation_override_and_runtime_promotion": 57,
    "translation_override_and_verification_renewal": 85,
    "verification_renewal": 335,
}
EXPECTED_CHUNK_DECISION_ROWS = (485, 499, 464, 509)
EXPECTED_CHUNK_PROMOTION_ROWS = (65, 79, 44, 89)
EXPECTED_CHUNK_OVERRIDE_ROWS = (33, 42, 30, 37)
EXPECTED_CHUNK_ACCEPTED_ASSEMBLIES = (245, 315, 231, 266)
EXPECTED_CHUNK_DECISION_SHA256 = (
    "6B002FF3565B1BAAED58064BA2351232B443A3B43350BD7BE9ADAFD1ED117BBF",
    "1FFA7BF45AA7DE0E53EFE3ED59BDED1E824A39F3E2CC4FD0E8CFFAC6D28A4D70",
    "1AFCCCF416F1EFFB04DAA045139E85E16D96668EB4E8F7A8CE41B6362C573BB2",
    "21F647B8D680DDA3639A95F289AAD8E9B442C00F05378CB213EEC847AE8CFC8C",
)
EXPECTED_CHUNK_EVIDENCE_SHA256 = (
    "AA38C99D83D42733BA8E271D26F9EB711FE0F1B626B9F9C266E8045FFBBF5F54",
    "D20256F303BE835F079883C856E1D3C1A8949C5E775ABB61CBFD421FEC9F9647",
    "C59C7190BF0291B99CF8D4A64AE3276DD36238CAFC90F77F562089927DBC050E",
    "36C8E2C923AB8F94F2E2C2218EC3F09B382FB5A7856533C0378F3668BDC00BD8",
)
EXPECTED_CHUNK_AUDIT_SHA256 = (
    "BD5BCE9A82BCE6D38B5D4175253D8C0D025F464B9D6FA01ACBC0675B0841C43C",
    "CA0ADCF4ADDA5AF0AEEC28DDEDE3ECED87121BD391B428102FB6CAFFD5A73717",
    "5475B552EF7BA70EE1F184263F45BDDC732E1548ED371D6174EC485EA1BAFEBA",
    "91D52FB7ED6CD13DA6E15AFB77494A9D907EC78FDBC6CB399FABB2285C10103F",
)
EXPECTED_CHUNK_PROMOTION_SHA256 = (
    "E08B23BAEB01C6EA3DA61AA9C2C85B6E5CBC981A646ED3DD494F90A7B230771D",
    "EC3BCB3E9246B8B3C837CFC1929F76E278B99B8483450CA57EEE0175CFA388E0",
    "CB4DF5D1307995E5C60D19CF1DD43F95D852901A70E4480B03F22D1B8BD9E871",
    "BE3832142A04A989CEEA7259340089AD8AC18280FEF91AFD7C492E59262AAA47",
)
EXPECTED_CHUNK_DECISION_COORDINATE_SHA256 = (
    "96AC18FD76014A9B6E52EA8CCB435C3FFFB218DB51B49B11BA50290E4DC0CA13",
    "876D5F6B96D0C50D245F7E176E0AE038BBB4BC0D4D4A9EB29F48B76AD89DF829",
    "D7DDC358689AF3B84C63AC37174552F45A7171492F92DD229C1E7C98369D81C4",
    "DDD94F031325CFE8BF6D752CA34F1E9F6F13B4F50B8D47ABBC184FAA4B0192B9",
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "36058C249C73F5B42C0DC7426FA68879F4BDC515F40F9C50B6CFEC07C7FD4D59"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "B6D1D61B1681F9CA92AD6DCD2C43F4913D83916C0DC5BFE05A4C0BFEC3BED5C1"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "8DA1C9C2491E145FD1EBAD2C326F48FDD344E91766758B68644EDDD53131C1A5"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "CE46C3E9524D6FB61DA1B24B58F3EB6EC863BC3860727A4B7BCB2F9D2D23AABF"
)
EXPECTED_OVERRIDE_MAP_SHA256 = (
    "F871C92957276271BD9114F5F8EB7884588B31A11E1F51B79442759CD5ECD262"
)
EXPECTED_ACTION_COORDINATE_SHA256 = {
    "runtime_promotion":
    "F1A2FCACE81519F800E2CBCF2E9A750F31FBF9D6BD1145F2834C58C6CC204921",
    "translation_override_and_runtime_promotion":
    "91E33C570489937A72B869F26285346D7CC3FA7837FF590B4EE9D34661D76485",
    "translation_override_and_verification_renewal":
    "06708518E2A97EC1B3C853821A9829322A42F67B3688C0BA30C6EBF43363F82C",
    "verification_renewal":
    "40DB24CEDF35B1647028E91E4E91571A5E68F94180DB98CD2A622D96050BA1FC",
}
EXPECTED_CHUNK0_PROMOTION_COORDINATE_SHA256 = (
    "FCF5CAD181AA01E190336B0CD206E7D0F518AA5227BBB8693F05E4284A5E66BF"
)
EXPECTED_LATER_PROMOTION_COORDINATE_SHA256 = (
    "C30259266763AF5012B213BB12FFC005A9ED8D4214727E37C69015C68D465F25"
)
EXPECTED_SUPERSEDED_RENEWAL_ROWS = 69
EXPECTED_SUPERSEDED_RENEWAL_COORDINATE_SHA256 = (
    "BE139F9096DAF7F6F47335FFAFD1458DEE95AAC2987E4F5FCC10BA2287267BC1"
)
EXPECTED_RETAINED_CHUNK0_RENEWAL_ROWS = 351
EXPECTED_RETAINED_CHUNK0_RENEWAL_COORDINATE_SHA256 = (
    "114C4D50B59BE0A7B508BA7EAF331F26C1F2FA3BE6E6D117B78B1810D6EA5274"
)
EXPECTED_LATER_EFFECTIVE_DELTA_ROWS = 281
EXPECTED_LATER_EFFECTIVE_DELTA_COORDINATE_SHA256 = (
    "3795E5A2E93AE2F024C350097E52293495EF87529D537B0449156D644834FD9A"
)
EXPECTED_RENEWAL_OVERRIDE_MAP_SHA256 = (
    "A647D4268DE672D738ABF29F46645A60DA9427DCFEE33B70DA87CAE07B35C8B4"
)
EXPECTED_RENEWAL_OVERRIDE_OWNER_MAP_SHA256 = (
    "3889B448DCE7FE0C8DE85880363700900C083D1D4900121B2282096092B8DC87"
)
EXPECTED_RENEWAL_WINNER_MAP_SHA256 = (
    "3248CD35D273E26CAB3F3221C56A6D05A4F4CDC6E5ECD24BA16084355620219B"
)
EXPECTED_EMPTY_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)

# Frozen after the first independent --write reproduction.
EXPECTED_AUDIT_OUTPUT_SHA256: str | None = (
    "39E287858CDF49ABDA329A6C3E8EB1E9497E415CDE25F4348C3E12113A1C07A8"
)
EXPECTED_PROMOTION_OUTPUT_SHA256: str | None = (
    "6F7DDA159299CC9B1923C14A55B5341CFBDB9E9DB3CADA5D7CB77453EAEF3E85"
)
EXPECTED_DECISION_OUTPUT_SHA256: str | None = (
    "5640EB7FB7E4EA9B32309B7FA280637DA9F26F96CA500BCD4FA9847D997456C0"
)
EXPECTED_EVIDENCE_OUTPUT_SHA256: str | None = (
    "910C0A59823C2B6B083F58257D6203053738EFEFC2E49E6271D553FF44CAB940"
)
EXPECTED_FAMILY_CANDIDATE_SHA256: str | None = (
    "24E0E9CCAAD469C0EEFB41EDB032A17F0DAE9BF3EEB471688D452C2FC2A37C56"
)


class ClosureError(ValueError):
    """Raised when the consolidated selector-family contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


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


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    require(path.is_file(), f"required file is absent: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def canonical_json(value: Any) -> str:
    return canonical_bytes(value).decode("ascii") + "\n"


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) for row in rows)


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = value.split(":")
    require(len(parts) == 3, f"invalid coordinate: {value!r}")
    try:
        result = tuple(int(part) for part in parts)
    except ValueError as exc:
        raise ClosureError(f"invalid coordinate: {value!r}") from exc
    require(all(part >= 0 for part in result), f"invalid coordinate: {value!r}")
    return result  # type: ignore[return-value]


def coordinate_digest(values: Iterable[str]) -> str:
    coordinates = sorted(set(values), key=parse_coordinate)
    return sha256_bytes(
        "".join(f"{coordinate}\n" for coordinate in coordinates).encode(
            "ascii"
        )
    )


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    resource_order = {"base_msggame": 0, "pk_msggame": 1}
    coordinate = parse_coordinate(str(row["coordinate"]))
    return (resource_order[str(row["resource"])], *coordinate)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"required JSON is absent: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClosureError(f"invalid JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"required JSONL is absent: {path}")
    rows: list[dict[str, Any]] = []
    try:
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line:
                continue
            row = json.loads(line)
            require(
                isinstance(row, dict),
                f"JSONL row {line_number} is not an object: {path}",
            )
            rows.append(row)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClosureError(f"invalid JSONL: {path}") from exc
    return rows


def index_rows(
    rows: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for source in rows:
        row = copy.deepcopy(dict(source))
        key = (str(row.get("resource")), str(row.get("coordinate")))
        require(
            key[0] in {"base_msggame", "pk_msggame"}
            and len(parse_coordinate(key[1])) == 3,
            f"invalid row key: {key}",
        )
        require(key not in result, f"duplicate row: {key}")
        result[key] = row
    return result


def seal_report(report: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(report))
    guards = result.setdefault("guards", {})
    require(isinstance(guards, dict), "report guards are not an object")
    guards.pop("report_payload_sha256", None)
    guards["report_payload_sha256"] = canonical_sha256(result)
    return result


SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
)
SENSITIVE_BODY_KEYS = {
    "accepted_sites",
    "assembly",
    "candidate_text",
    "current_text",
    "exact_maps",
    "records",
    "rejected_sites",
    "source_text",
    "translation",
}


def assert_source_free_report(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            require(
                key not in SENSITIVE_BODY_KEYS,
                f"tracked report contains private body/map key: {key}",
            )
            assert_source_free_report(child)
    elif isinstance(value, list):
        for child in value:
            assert_source_free_report(child)
    elif isinstance(value, str):
        require(
            SOURCE_TEXT_RE.search(value) is None,
            "tracked report contains source/translation characters",
        )


def chunk_paths(
    module: Any,
) -> tuple[Path, Path, Path, Path]:
    return (
        Path(module.DEFAULT_AUDIT_OUTPUT),
        Path(module.DEFAULT_PROMOTION_OUTPUT),
        Path(module.DEFAULT_DECISION_OUTPUT),
        Path(module.DEFAULT_EVIDENCE_OUTPUT),
    )


def action_memberships(
    rows: Mapping[str, Mapping[str, Any]],
    action_field: str,
) -> tuple[set[str], set[str], set[str]]:
    promotions: set[str] = set()
    renewals: set[str] = set()
    overrides: set[str] = set()
    for coordinate, row in rows.items():
        action = str(row.get(action_field))
        require(
            action in EXPECTED_ACTION_COUNTS,
            f"unknown chunk action at {coordinate}: {action!r}",
        )
        if "runtime_promotion" in action:
            promotions.add(coordinate)
        if "verification_renewal" in action:
            renewals.add(coordinate)
        if "translation_override" in action:
            overrides.add(coordinate)
    require(
        promotions | renewals == set(rows)
        and not promotions & renewals,
        "chunk promotion/renewal partition drifted",
    )
    return promotions, renewals, overrides


def load_frozen_chunks() -> dict[str, Any]:
    chunks: list[dict[str, Any]] = []
    artifact_manifest: list[dict[str, Any]] = []
    for chunk, builder_path in enumerate(CHUNK_BUILDER_PATHS):
        module = load_module(
            builder_path,
            f"pk_selector538_family_chunk{chunk}",
        )
        audit_path, promotion_path, decision_path, evidence_path = (
            chunk_paths(module)
        )
        expected_hashes = (
            EXPECTED_CHUNK_AUDIT_SHA256[chunk],
            EXPECTED_CHUNK_PROMOTION_SHA256[chunk],
            EXPECTED_CHUNK_DECISION_SHA256[chunk],
            EXPECTED_CHUNK_EVIDENCE_SHA256[chunk],
        )
        for name, path, expected in zip(
            ("audit", "promotion", "decision", "evidence"),
            (audit_path, promotion_path, decision_path, evidence_path),
            expected_hashes,
        ):
            actual = sha256_file(path)
            require(
                actual == expected,
                f"selector538 chunk{chunk} {name} artifact drifted: "
                f"{actual}",
            )
            artifact_manifest.append(
                {
                    "chunk": chunk,
                    "kind": name,
                    "sha256": actual,
                }
            )
        audit = load_json(audit_path)
        promotion = load_json(promotion_path)
        assert_source_free_report(audit)
        assert_source_free_report(promotion)
        require(
            audit.get("schema") == module.AUDIT_SCHEMA
            and promotion.get("schema") == module.PROMOTION_SCHEMA
            and audit.get("method") == module.METHOD
            and promotion.get("method") == module.METHOD
            and audit.get("status") == "PASS"
            and promotion.get("status") == "PASS"
            and audit.get("steam_write_performed") is False
            and promotion.get("steam_write_performed") is False,
            f"selector538 chunk{chunk} public contract drifted",
        )
        decision_rows = load_jsonl(decision_path)
        evidence_rows = load_jsonl(evidence_path)
        require(
            len(decision_rows) == EXPECTED_CHUNK_DECISION_ROWS[chunk]
            and len(evidence_rows) == EXPECTED_CHUNK_DECISION_ROWS[chunk],
            f"selector538 chunk{chunk} decision/evidence count drifted",
        )
        decisions = {
            str(row["coordinate"]): row for row in decision_rows
        }
        evidence = {
            str(row["coordinate"]): row for row in evidence_rows
        }
        require(
            len(decisions) == len(decision_rows)
            and set(decisions) == set(evidence)
            and coordinate_digest(decisions)
            == EXPECTED_CHUNK_DECISION_COORDINATE_SHA256[chunk],
            f"selector538 chunk{chunk} coordinate contract drifted",
        )
        action_field = str(module.UPDATE_ACTION_FIELD)
        promotions, renewals, overrides = action_memberships(
            decisions, action_field
        )
        require(
            len(promotions) == EXPECTED_CHUNK_PROMOTION_ROWS[chunk]
            and len(renewals) == EXPECTED_RENEWAL_ROWS
            and len(overrides) == EXPECTED_CHUNK_OVERRIDE_ROWS[chunk],
            f"selector538 chunk{chunk} membership count drifted",
        )
        for coordinate, row in decisions.items():
            vm = row.get("runtime_vm_verification")
            require(
                isinstance(vm, dict)
                and vm == evidence[coordinate]
                and vm.get("coordinate") == coordinate
                and vm.get("method") == module.METHOD
                and vm.get("schema") == module.EVIDENCE_SCHEMA
                and vm.get("action") == row.get(action_field)
                and vm.get("status") == "verified"
                and vm.get("resource") == "pk_msggame",
                f"selector538 chunk{chunk} row evidence drifted: "
                f"{coordinate}",
            )
            if coordinate in overrides:
                override = row.get(
                    f"selector538_chunk{chunk}_exact_override_evidence"
                )
                require(
                    isinstance(override, dict)
                    and override.get("schema") == module.OVERRIDE_SCHEMA
                    and override.get("translation_utf16le_sha256")
                    == sha256_text(str(row["translation"])),
                    f"selector538 chunk{chunk} override drifted: "
                    f"{coordinate}",
                )
        require(
            int(audit["proof"]["accepted_assembly_rows"])
            == EXPECTED_CHUNK_ACCEPTED_ASSEMBLIES[chunk],
            f"selector538 chunk{chunk} assembly count drifted",
        )
        chunks.append(
            {
                "audit": audit,
                "audit_sha256": expected_hashes[0],
                "decision_rows": decisions,
                "evidence_sha256": expected_hashes[3],
                "module": module,
                "overrides": overrides,
                "promotion": promotion,
                "promotion_sha256": expected_hashes[1],
                "promotions": promotions,
                "renewals": renewals,
            }
        )
    return {
        "artifact_manifest": artifact_manifest,
        "chunks": chunks,
    }


def analyze_family(chunks: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    decision_sets = [set(chunk["decision_rows"]) for chunk in chunks]
    promotion_sets = [set(chunk["promotions"]) for chunk in chunks]
    renewal_sets = [set(chunk["renewals"]) for chunk in chunks]
    override_sets = [set(chunk["overrides"]) for chunk in chunks]
    pairwise: list[dict[str, Any]] = []
    for left in range(4):
        for right in range(left + 1, 4):
            decision_overlap = decision_sets[left] & decision_sets[right]
            promotion_overlap = promotion_sets[left] & promotion_sets[right]
            override_overlap = override_sets[left] & override_sets[right]
            require(
                len(decision_overlap) == EXPECTED_PAIRWISE_DECISION_OVERLAP
                and decision_overlap == renewal_sets[left]
                and decision_overlap == renewal_sets[right],
                f"chunk {left}/{right} decision overlap drifted",
            )
            require(
                len(promotion_overlap) == EXPECTED_PAIRWISE_PROMOTION_OVERLAP
                and not promotion_overlap,
                f"chunk {left}/{right} promotion overlap drifted",
            )
            require(
                len(override_overlap) == EXPECTED_PAIRWISE_OVERRIDE_OVERLAP
                and not override_overlap,
                f"chunk {left}/{right} override overlap drifted",
            )
            pairwise.append(
                {
                    "decision_overlap_rows": len(decision_overlap),
                    "decision_overlap_sha256": coordinate_digest(
                        decision_overlap
                    ),
                    "left_chunk": left,
                    "override_overlap_rows": len(override_overlap),
                    "override_overlap_sha256": coordinate_digest(
                        override_overlap
                    ),
                    "promotion_overlap_rows": len(promotion_overlap),
                    "promotion_overlap_sha256": coordinate_digest(
                        promotion_overlap
                    ),
                    "right_chunk": right,
                }
            )
    require(
        all(renewal == renewal_sets[0] for renewal in renewal_sets[1:]),
        "chunk renewal universes are not identical",
    )
    decisions = set().union(*decision_sets)
    promotions = set().union(*promotion_sets)
    renewals = set(renewal_sets[0])
    overrides = set().union(*override_sets)
    require(
        len(decisions) == EXPECTED_DECISION_ROWS
        and len(promotions) == EXPECTED_PROMOTION_ROWS
        and len(renewals) == EXPECTED_RENEWAL_ROWS
        and len(overrides) == EXPECTED_OVERRIDE_ROWS
        and decisions == promotions | renewals
        and not promotions & renewals,
        "selector538 family union counts drifted",
    )
    require(
        coordinate_digest(decisions) == EXPECTED_DECISION_COORDINATE_SHA256
        and coordinate_digest(promotions)
        == EXPECTED_PROMOTION_COORDINATE_SHA256
        and coordinate_digest(renewals)
        == EXPECTED_RENEWAL_COORDINATE_SHA256
        and coordinate_digest(overrides)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "selector538 family union coordinate digest drifted",
    )
    override_owner: dict[str, int] = {}
    override_map: dict[str, str] = {}
    for chunk_id, chunk in enumerate(chunks):
        for coordinate in chunk["overrides"]:
            require(
                coordinate not in override_owner,
                f"duplicate override owner: {coordinate}",
            )
            override_owner[coordinate] = chunk_id
            override_map[coordinate] = str(
                chunk["decision_rows"][coordinate]["translation"]
            )
    require(
        canonical_sha256(
            dict(
                sorted(
                    override_map.items(),
                    key=lambda item: parse_coordinate(item[0]),
                )
            )
        )
        == EXPECTED_OVERRIDE_MAP_SHA256,
        "selector538 family exact override map drifted",
    )
    action_by_coordinate: dict[str, str] = {}
    for coordinate in decisions:
        is_promotion = coordinate in promotions
        is_override = coordinate in overrides
        if is_promotion:
            action = (
                "translation_override_and_runtime_promotion"
                if is_override
                else "runtime_promotion"
            )
        else:
            action = (
                "translation_override_and_verification_renewal"
                if is_override
                else "verification_renewal"
            )
        action_by_coordinate[coordinate] = action
    action_counts = Counter(action_by_coordinate.values())
    require(
        dict(action_counts) == EXPECTED_ACTION_COUNTS,
        "selector538 family action counts drifted",
    )
    for action, expected in EXPECTED_ACTION_COORDINATE_SHA256.items():
        require(
            coordinate_digest(
                coordinate
                for coordinate, value in action_by_coordinate.items()
                if value == action
            )
            == expected,
            f"selector538 family action coordinate drifted: {action}",
        )
    translation_variant_counts: Counter[int] = Counter()
    for coordinate in renewals:
        translations = {
            str(chunk["decision_rows"][coordinate]["translation"])
            for chunk in chunks
        }
        translation_variant_counts[len(translations)] += 1
        assemblies = [
            chunk["decision_rows"][coordinate].get(
                "runtime_assembly_evidence"
            )
            for chunk in chunks
        ]
        require(
            all(assembly == assemblies[0] for assembly in assemblies[1:]),
            f"shared renewal assembly drifted: {coordinate}",
        )
    require(
        dict(translation_variant_counts)
        == {
            1: EXPECTED_TRANSLATION_SINGLE_VARIANT_ROWS,
            2: EXPECTED_TRANSLATION_TWO_VARIANT_ROWS,
        },
        "shared renewal translation-variant contract drifted",
    )
    require(
        len(promotion_sets[0]) == EXPECTED_ALREADY_PROMOTED_ROWS
        and coordinate_digest(promotion_sets[0])
        == EXPECTED_CHUNK0_PROMOTION_COORDINATE_SHA256
        and len(promotions - promotion_sets[0])
        == EXPECTED_INCREMENTAL_PROMOTION_ROWS,
        "chunk0 exact supersession universe drifted",
    )
    later_promotions = promotions - promotion_sets[0]
    renewal_overrides = overrides & renewals
    later_renewal_overrides = renewal_overrides - override_sets[0]
    retained_chunk0_renewals = renewals - later_renewal_overrides
    later_effective_delta = later_promotions | later_renewal_overrides
    renewal_override_map = {
        coordinate: override_map[coordinate]
        for coordinate in sorted(
            renewal_overrides, key=parse_coordinate
        )
    }
    renewal_override_owner_map = {
        coordinate: override_owner[coordinate]
        for coordinate in sorted(
            renewal_overrides, key=parse_coordinate
        )
    }
    renewal_winner_map = {
        coordinate: (
            override_owner[coordinate]
            if coordinate in later_renewal_overrides
            else 0
        )
        for coordinate in sorted(renewals, key=parse_coordinate)
    }
    require(
        coordinate_digest(later_promotions)
        == EXPECTED_LATER_PROMOTION_COORDINATE_SHA256
        and len(later_renewal_overrides)
        == EXPECTED_SUPERSEDED_RENEWAL_ROWS
        and coordinate_digest(later_renewal_overrides)
        == EXPECTED_SUPERSEDED_RENEWAL_COORDINATE_SHA256
        and len(retained_chunk0_renewals)
        == EXPECTED_RETAINED_CHUNK0_RENEWAL_ROWS
        and coordinate_digest(retained_chunk0_renewals)
        == EXPECTED_RETAINED_CHUNK0_RENEWAL_COORDINATE_SHA256
        and len(later_effective_delta)
        == EXPECTED_LATER_EFFECTIVE_DELTA_ROWS
        and coordinate_digest(later_effective_delta)
        == EXPECTED_LATER_EFFECTIVE_DELTA_COORDINATE_SHA256
        and canonical_sha256(renewal_override_map)
        == EXPECTED_RENEWAL_OVERRIDE_MAP_SHA256
        and canonical_sha256(renewal_override_owner_map)
        == EXPECTED_RENEWAL_OVERRIDE_OWNER_MAP_SHA256
        and canonical_sha256(renewal_winner_map)
        == EXPECTED_RENEWAL_WINNER_MAP_SHA256,
        "selector538 chunk0 exact renewal supersession drifted",
    )
    return {
        "action_by_coordinate": action_by_coordinate,
        "decisions": decisions,
        "later_effective_delta": later_effective_delta,
        "later_promotions": later_promotions,
        "later_renewal_overrides": later_renewal_overrides,
        "override_map": override_map,
        "override_owner": override_owner,
        "overrides": overrides,
        "pairwise": pairwise,
        "promotions": promotions,
        "renewal_override_owner_map": renewal_override_owner_map,
        "renewal_winner_map": renewal_winner_map,
        "renewals": renewals,
        "retained_chunk0_renewals": retained_chunk0_renewals,
        "translation_variant_counts": dict(translation_variant_counts),
    }


def build_audit(
    *,
    chunks: Sequence[Mapping[str, Any]],
    artifact_manifest: Sequence[Mapping[str, Any]],
    analysis: Mapping[str, Any],
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "action_counts": dict(sorted(EXPECTED_ACTION_COUNTS.items())),
        "distribution_policy": {
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "guards": {
            "chunk_artifact_manifest_sha256": canonical_sha256(
                list(artifact_manifest)
            ),
            "chunk_audit_file_sha256": list(
                EXPECTED_CHUNK_AUDIT_SHA256
            ),
            "chunk_decision_coordinate_sha256": list(
                EXPECTED_CHUNK_DECISION_COORDINATE_SHA256
            ),
            "chunk_decision_file_sha256": list(
                EXPECTED_CHUNK_DECISION_SHA256
            ),
            "chunk_evidence_file_sha256": list(
                EXPECTED_CHUNK_EVIDENCE_SHA256
            ),
            "chunk_promotion_file_sha256": list(
                EXPECTED_CHUNK_PROMOTION_SHA256
            ),
            "chunk0_exact_supersession_coordinate_sha256":
                EXPECTED_CHUNK_DECISION_COORDINATE_SHA256[0],
            "chunk0_promotion_supersession_coordinate_sha256":
                EXPECTED_CHUNK0_PROMOTION_COORDINATE_SHA256,
            "chunk0_retained_renewal_coordinate_sha256":
                EXPECTED_RETAINED_CHUNK0_RENEWAL_COORDINATE_SHA256,
            "chunk0_superseded_renewal_coordinate_sha256":
                EXPECTED_SUPERSEDED_RENEWAL_COORDINATE_SHA256,
            "decision_union_coordinate_sha256":
                EXPECTED_DECISION_COORDINATE_SHA256,
            "later_effective_delta_coordinate_sha256":
                EXPECTED_LATER_EFFECTIVE_DELTA_COORDINATE_SHA256,
            "later_promotion_coordinate_sha256":
                EXPECTED_LATER_PROMOTION_COORDINATE_SHA256,
            "official_predecessor_private_sha256":
                EXPECTED_OFFICIAL_PREDECESSOR_PRIVATE_SHA256,
            "official_predecessor_public_sha256":
                EXPECTED_OFFICIAL_PREDECESSOR_PUBLIC_SHA256,
            "override_map_canonical_sha256":
                EXPECTED_OVERRIDE_MAP_SHA256,
            "override_union_coordinate_sha256":
                EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "predecessor_checkpoint_sha256":
                EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "promotion_union_coordinate_sha256":
                EXPECTED_PROMOTION_COORDINATE_SHA256,
            "renewal_common_coordinate_sha256":
                EXPECTED_RENEWAL_COORDINATE_SHA256,
            "renewal_override_map_canonical_sha256":
                EXPECTED_RENEWAL_OVERRIDE_MAP_SHA256,
            "renewal_override_owner_map_canonical_sha256":
                EXPECTED_RENEWAL_OVERRIDE_OWNER_MAP_SHA256,
            "renewal_winner_map_canonical_sha256":
                EXPECTED_RENEWAL_WINNER_MAP_SHA256,
        },
        "method": METHOD,
        "proof": {
            "accepted_assembly_rows": EXPECTED_ACCEPTED_ASSEMBLIES,
            "all_chunk_artifacts_frozen_and_reproduced": True,
            "all_exact_overrides_applied_once": True,
            "all_shared_assembly_evidence_identical": True,
            "automatic_space_inserted": False,
            "chunk0_current_layer_exactly_superseded": True,
            "chunk0_retained_renewal_rows":
                EXPECTED_RETAINED_CHUNK0_RENEWAL_ROWS,
            "chunk0_superseded_renewal_rows":
                EXPECTED_SUPERSEDED_RENEWAL_ROWS,
            "family_union_constructed_from_immutable_checkpoint": True,
            "pairwise_decision_overlap": analysis["pairwise"],
            "pairwise_override_overlap_zero": True,
            "pairwise_promotion_overlap_zero": True,
            "renewal_overrides_preserved_by_union": True,
            "sequential_row_replacement_used": False,
            "translation_single_variant_rows":
                EXPECTED_TRANSLATION_SINGLE_VARIANT_ROWS,
            "translation_two_variant_rows":
                EXPECTED_TRANSLATION_TWO_VARIANT_ROWS,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "schema": AUDIT_SCHEMA,
        "scope": {
            "chunk_count": 4,
            "chunk_decision_rows": list(EXPECTED_CHUNK_DECISION_ROWS),
            "decision_union_rows": EXPECTED_DECISION_ROWS,
            "exact_override_union_rows": EXPECTED_OVERRIDE_ROWS,
            "incremental_runtime_promotion_rows":
                EXPECTED_INCREMENTAL_PROMOTION_ROWS,
            "later_effective_delta_rows":
                EXPECTED_LATER_EFFECTIVE_DELTA_ROWS,
            "official_predecessor_pending_rows":
                EXPECTED_OFFICIAL_PREDECESSOR_PENDING,
            "post_family_pending_rows": EXPECTED_PENDING_AFTER,
            "predecessor_pending_rows": EXPECTED_PREDECESSOR_PENDING,
            "predecessor_rows": EXPECTED_PREDECESSOR_ROWS,
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "selector": SELECTOR,
            "superseded_chunk0_promotion_rows":
                EXPECTED_ALREADY_PROMOTED_ROWS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    require(
        sum(EXPECTED_CHUNK_ACCEPTED_ASSEMBLIES)
        == EXPECTED_ACCEPTED_ASSEMBLIES
        and all(
            chunk["audit"].get("steam_write_performed") is False
            and chunk["promotion"].get("steam_write_performed") is False
            for chunk in chunks
        ),
        "selector538 family input distribution contract drifted",
    )
    sealed = seal_report(report)
    assert_source_free_report(sealed)
    return sealed


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    chunks: Sequence[Mapping[str, Any]],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    chunk0_rows = chunks[0]["decision_rows"]
    updates: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    repair_hard_risks = chunks[0]["module"].CALLER.PREDECESSOR.repair_hard_risks
    for coordinate in sorted(
        analysis["decisions"], key=parse_coordinate
    ):
        baseline = predecessor_rows[("pk_msggame", coordinate)]
        chunk0_superseded = coordinate in chunk0_rows
        official_predecessor = (
            chunk0_rows[coordinate] if chunk0_superseded else baseline
        )
        updated = copy.deepcopy(dict(official_predecessor))
        action = str(analysis["action_by_coordinate"][coordinate])
        is_promotion = coordinate in analysis["promotions"]
        is_override = coordinate in analysis["overrides"]
        if is_override:
            updated["translation"] = analysis["override_map"][coordinate]
            repair_hard_risks(updated)
            updated[OVERRIDE_FIELD] = {
                "automatic_space_inserted": False,
                "chunk_owner": int(
                    analysis["override_owner"][coordinate]
                ),
                "control_bytes_preserved": True,
                "exact_union_hash_bound": True,
                "schema": OVERRIDE_SCHEMA,
                "translation_utf16le_sha256": sha256_text(
                    str(updated["translation"])
                ),
            }
        if is_promotion:
            if chunk0_superseded:
                require(
                    baseline.get("runtime_review") == "pending"
                    and official_predecessor.get("runtime_review")
                    == "verified",
                    f"chunk0 promotion supersession drifted: {coordinate}",
                )
            else:
                require(
                    baseline.get("runtime_review") == "pending",
                    f"family promotion baseline drifted: {coordinate}",
                )
                updated["runtime_review"] = "verified"
                updated["scope_classification"] = "retranslated"
                updated["layout_review"] = "runtime_verified"
        else:
            require(
                coordinate in analysis["renewals"]
                and baseline.get("runtime_review") == "verified"
                and official_predecessor.get("runtime_review") == "verified",
                f"family renewal predecessor drifted: {coordinate}",
            )
        evidence = {
            "action": action,
            "closure_binding": {
                "accepted_assembly_rows": EXPECTED_ACCEPTED_ASSEMBLIES,
                "audit_report_file_sha256": audit_file_sha256,
                "audit_report_payload_sha256": audit["guards"][
                    "report_payload_sha256"
                ],
                "decision_union_coordinate_sha256":
                    EXPECTED_DECISION_COORDINATE_SHA256,
                "override_map_canonical_sha256":
                    EXPECTED_OVERRIDE_MAP_SHA256,
                "override_union_coordinate_sha256":
                    EXPECTED_OVERRIDE_COORDINATE_SHA256,
                "promotion_union_coordinate_sha256":
                    EXPECTED_PROMOTION_COORDINATE_SHA256,
                "renewal_common_coordinate_sha256":
                    EXPECTED_RENEWAL_COORDINATE_SHA256,
                "selector": SELECTOR,
            },
            "coordinate": coordinate,
            "method": METHOD,
            "per_row_game_playback_required": False,
            "predecessor_binding": {
                "baseline_checkpoint_sha256":
                    EXPECTED_PREDECESSOR_PRIVATE_SHA256,
                "baseline_row_sha256": canonical_sha256(baseline),
                "chunk0_exactly_superseded": chunk0_superseded,
                "official_checkpoint_sha256":
                    EXPECTED_OFFICIAL_PREDECESSOR_PRIVATE_SHA256,
                "official_row_sha256": canonical_sha256(
                    official_predecessor
                ),
            },
            "preexisting_verified_evidence_renewed": not is_promotion,
            "resource": "pk_msggame",
            "schema": EVIDENCE_SCHEMA,
            "status": "verified",
            "translation_utf16le_sha256": sha256_text(
                str(updated["translation"])
            ),
        }
        updated[UPDATE_ACTION_FIELD] = action
        updated["runtime_vm_verification"] = evidence
        updates.append(updated)
        evidence_rows.append(evidence)
    updates.sort(key=row_sort_key)
    evidence_rows.sort(
        key=lambda row: parse_coordinate(str(row["coordinate"]))
    )
    require(
        Counter(str(row["action"]) for row in evidence_rows)
        == Counter(EXPECTED_ACTION_COUNTS),
        "selector538 family emitted action counts drifted",
    )
    return updates, evidence_rows


def merged_candidate_sha256(
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    updates: Sequence[Mapping[str, Any]],
) -> str:
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in predecessor_rows.items()
    }
    for update in updates:
        key = (str(update["resource"]), str(update["coordinate"]))
        require(key in merged, f"family update row is absent: {key}")
        merged[key] = copy.deepcopy(dict(update))
    rows = sorted(merged.values(), key=row_sort_key)
    require(
        len(rows) == EXPECTED_PREDECESSOR_ROWS
        and sum(row.get("runtime_review") == "pending" for row in rows)
        == EXPECTED_STANDALONE_PENDING_AFTER,
        "selector538 family candidate count drifted",
    )
    return sha256_bytes(canonical_jsonl(rows).encode("utf-8"))


def build_promotion(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    candidate_sha256: str,
    decision_content: str,
    evidence_content: str,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "action_counts": dict(sorted(EXPECTED_ACTION_COUNTS.items())),
        "distribution_policy": {
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "candidate_sha256": candidate_sha256,
            "decision_union_coordinate_sha256":
                EXPECTED_DECISION_COORDINATE_SHA256,
            "official_predecessor_private_sha256":
                EXPECTED_OFFICIAL_PREDECESSOR_PRIVATE_SHA256,
            "override_map_canonical_sha256":
                EXPECTED_OVERRIDE_MAP_SHA256,
            "override_union_coordinate_sha256":
                EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "predecessor_checkpoint_sha256":
                EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "promotion_union_coordinate_sha256":
                EXPECTED_PROMOTION_COORDINATE_SHA256,
            "renewal_common_coordinate_sha256":
                EXPECTED_RENEWAL_COORDINATE_SHA256,
        },
        "method": METHOD,
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": {
            "decision_delta_rows": EXPECTED_DECISION_ROWS,
            "exact_override_rows": EXPECTED_OVERRIDE_ROWS,
            "incremental_runtime_promotion_rows":
                EXPECTED_INCREMENTAL_PROMOTION_ROWS,
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "pending_rows_before":
                EXPECTED_OFFICIAL_PREDECESSOR_PENDING,
            "private_decision_delta_sha256": sha256_bytes(
                decision_content.encode("utf-8")
            ),
            "private_evidence_rows": EXPECTED_DECISION_ROWS,
            "private_evidence_sha256": sha256_bytes(
                evidence_content.encode("utf-8")
            ),
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "superseded_chunk0_promotion_rows":
                EXPECTED_ALREADY_PROMOTED_ROWS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
        },
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "steam_write_performed": False,
    }
    sealed = seal_report(report)
    assert_source_free_report(sealed)
    return sealed


def build_outputs() -> dict[str, Any]:
    require(
        sha256_file(PREDECESSOR_PRIVATE_PATH)
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        "immutable selector538 family predecessor drifted",
    )
    predecessor_list = load_jsonl(PREDECESSOR_PRIVATE_PATH)
    require(
        len(predecessor_list) == EXPECTED_PREDECESSOR_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in predecessor_list
        )
        == EXPECTED_PREDECESSOR_PENDING,
        "immutable selector538 family predecessor counts drifted",
    )
    predecessor_rows = index_rows(predecessor_list)
    frozen = load_frozen_chunks()
    chunks = frozen["chunks"]
    analysis = analyze_family(chunks)
    audit = build_audit(
        chunks=chunks,
        artifact_manifest=frozen["artifact_manifest"],
        analysis=analysis,
    )
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updates, evidence_rows = build_updated_rows(
        predecessor_rows=predecessor_rows,
        chunks=chunks,
        analysis=analysis,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updates)
    evidence_content = canonical_jsonl(evidence_rows)
    candidate_sha256 = merged_candidate_sha256(
        predecessor_rows, updates
    )
    if EXPECTED_FAMILY_CANDIDATE_SHA256 is not None:
        require(
            candidate_sha256 == EXPECTED_FAMILY_CANDIDATE_SHA256,
            "selector538 family candidate SHA-256 drifted",
        )
    promotion = build_promotion(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        candidate_sha256=candidate_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
    )
    promotion_content = canonical_json(promotion)
    return {
        "analysis": analysis,
        "audit": audit,
        "audit_content": audit_content,
        "audit_file_sha256": audit_file_sha256,
        "candidate_sha256": candidate_sha256,
        "decision_content": decision_content,
        "decision_file_sha256": sha256_bytes(
            decision_content.encode("utf-8")
        ),
        "evidence_content": evidence_content,
        "evidence_file_sha256": sha256_bytes(
            evidence_content.encode("utf-8")
        ),
        "promotion": promotion,
        "promotion_content": promotion_content,
        "promotion_file_sha256": sha256_bytes(
            promotion_content.encode("utf-8")
        ),
        "updated_rows": updates,
    }


def write_exact(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def validate_output_hashes(bundle: Mapping[str, Any]) -> None:
    expected = (
        EXPECTED_AUDIT_OUTPUT_SHA256,
        EXPECTED_PROMOTION_OUTPUT_SHA256,
        EXPECTED_DECISION_OUTPUT_SHA256,
        EXPECTED_EVIDENCE_OUTPUT_SHA256,
    )
    actual = (
        bundle["audit_file_sha256"],
        bundle["promotion_file_sha256"],
        bundle["decision_file_sha256"],
        bundle["evidence_file_sha256"],
    )
    for label, expected_hash, actual_hash in zip(
        ("audit", "promotion", "decision", "evidence"),
        expected,
        actual,
    ):
        if expected_hash is not None:
            require(
                actual_hash == expected_hash,
                f"selector538 family {label} output drifted: "
                f"{actual_hash}",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=DEFAULT_AUDIT_OUTPUT,
    )
    parser.add_argument(
        "--promotion-output",
        type=Path,
        default=DEFAULT_PROMOTION_OUTPUT,
    )
    parser.add_argument(
        "--decision-output",
        type=Path,
        default=DEFAULT_DECISION_OUTPUT,
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=DEFAULT_EVIDENCE_OUTPUT,
    )
    args = parser.parse_args()
    bundle = build_outputs()
    validate_output_hashes(bundle)
    outputs = (
        (args.audit_output, bundle["audit_content"]),
        (args.promotion_output, bundle["promotion_content"]),
        (args.decision_output, bundle["decision_content"]),
        (args.evidence_output, bundle["evidence_content"]),
    )
    if args.write:
        for path, content in outputs:
            write_exact(path, str(content))
    else:
        for path, content in outputs:
            require(path.is_file(), f"output is absent: {path}")
            require(
                path.read_bytes() == str(content).encode("utf-8"),
                f"output content drifted: {path}",
            )
    print(
        "selector538-family-consolidated-closure: PASS "
        f"decisions={EXPECTED_DECISION_ROWS} "
        f"promotions={EXPECTED_PROMOTION_ROWS} "
        f"incremental={EXPECTED_INCREMENTAL_PROMOTION_ROWS} "
        f"renewals={EXPECTED_RENEWAL_ROWS} "
        f"overrides={EXPECTED_OVERRIDE_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"candidate={bundle['candidate_sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ClosureError as exc:
        print(f"selector538-family-consolidated-closure: FAIL: {exc}")
        raise SystemExit(1)
