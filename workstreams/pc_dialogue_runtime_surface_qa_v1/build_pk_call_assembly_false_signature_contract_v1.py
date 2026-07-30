#!/usr/bin/env python3
"""Build the source-free PK call-assembly reviewed-false contract.

The private review report contains rendered Korean text.  This builder selects
only the findings that were exhaustively reviewed as false positives and emits
the same source-free structural fields already used by the public audit.  The
runtime audit consumes only the resulting exact finding signatures; it does
not trust a candidate-file hash or a broad coordinate/rule exception.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
DEFAULT_INPUT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "call-assembly-pk-43c2-base-326b.private.v1.json"
)
DEFAULT_OUTPUT = (
    SCRIPT.parent
    / "pk_call_assembly_false_signature_contract.source_free.v1.json"
)
SCHEMA = (
    "nobu16.kr.pk-call-assembly-reviewed-false-signature-contract."
    "source-free.v1"
)
EXPECTED_PRIVATE_REPORT_SHA256 = (
    "9EFD6BDA4CC5E1DC818B57788E038ED00D8735CDE5237EDD1A458BEE1CB81448"
)
EXPECTED_BASE_INPUT_SHA256 = (
    "44828B27368FB74EF906DC167DCAF1BA54129A4313F7EDA3C0668777BB86E276"
)
EXPECTED_PK_INPUT_SHA256 = (
    "43C2E6539D547F3D3273D9B683BDF3490EEC38B628D64A80EDF18D9E5BB8B9CE"
)
EXPECTED_PRIVATE_ISSUE_COUNT = 8290
EXPECTED_SELECTOR_SIDE_COUNT = 98
EXPECTED_NON_SIDE_COUNT = 33
EXPECTED_ENTRY_COUNT = (
    EXPECTED_SELECTOR_SIDE_COUNT + EXPECTED_NON_SIDE_COUNT
)

SOURCE_FREE_FINDING_FIELDS = (
    "resource",
    "category",
    "block_id",
    "record_id",
    "component_index",
    "literal_id",
    "call_target",
    "rule",
    "previous_literal_sha256",
    "call_variant_sha256",
    "next_literal_sha256",
    "assembled_sha256",
)


def parse_coordinates(specification: str) -> set[tuple[int, int]]:
    coordinates: set[tuple[int, int]] = set()
    for item in specification.split(","):
        item = item.strip()
        if not item:
            continue
        block_text, record_text = item.split(":", 1)
        block_id = int(block_text)
        if "-" in record_text:
            first_text, last_text = record_text.split("-", 1)
            first = int(first_text)
            last = int(last_text)
            coordinates.update(
                (block_id, record_id)
                for record_id in range(first, last + 1)
            )
        else:
            coordinates.add((block_id, int(record_text)))
    return coordinates


SELECTOR_SIDE_COORDINATES = parse_coordinates(
    """
    7:2846, 7:2855,
    8:103, 8:997,
    13:73, 13:75, 13:77,
    15:22, 15:24-28, 15:30-32, 15:34-37,
    15:491-492, 15:494, 15:496-497, 15:501, 15:514-517, 15:519,
    15:527-528, 15:531-532, 15:535-536, 15:544, 15:556-561,
    15:568-573, 15:586-592, 15:594-597, 15:599, 15:602-604,
    15:606, 15:608, 15:615-616, 15:645-647, 15:653, 15:656-657,
    15:659-661, 15:663, 15:665, 15:667, 15:670-671, 15:673,
    15:677, 15:679, 15:682-683, 15:685, 15:689-690, 15:703-704,
    15:1893-1895,
    17:858, 17:869
    """
)

NON_SIDE_FALSE_COORDINATES: Mapping[str, set[tuple[int, int]]] = {
    "finite_suffix_before_same_sentence_hangul": parse_coordinates(
        """
        6:4457, 6:4510, 6:4663-4665, 6:4672, 6:4916,
        15:257, 15:275-276, 15:282-283, 15:1830, 15:1839,
        15:1844, 15:1849, 15:2009
        """
    ),
    "deut_bare_copula": parse_coordinates(
        """
        6:270, 6:4517,
        8:31, 8:38, 8:274-278, 8:293,
        15:129-130, 15:2199, 15:2385-2386
        """
    ),
    "rendered_missing_exist_stem_before_bare_formal": parse_coordinates(
        "9:162"
    ),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_line(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"


def source_free_finding(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    return {field: value.get(field) for field in SOURCE_FREE_FINDING_FIELDS}


def finding_signature_sha256(value: Mapping[str, Any]) -> str:
    return sha256_bytes(
        canonical_line(source_free_finding(value)).encode("ascii")
    )


def reviewed_coordinate_rules() -> dict[
    tuple[tuple[int, int], str],
    str,
]:
    selected = {
        (
            coordinate,
            "rendered_selector_side_role_smell",
        ): "selector_side_legitimate"
        for coordinate in SELECTOR_SIDE_COORDINATES
    }
    for rule, coordinates in NON_SIDE_FALSE_COORDINATES.items():
        for coordinate in coordinates:
            key = (coordinate, rule)
            if key in selected:
                raise ValueError(f"duplicate reviewed key: {key}")
            selected[key] = "non_side_false_positive"
    return selected


def contract_entry(
    value: Mapping[str, Any],
    review_class: str,
) -> dict[str, Any]:
    finding = source_free_finding(value)
    return {
        **finding,
        "finding_signature_sha256": finding_signature_sha256(finding),
        "review_class": review_class,
    }


def entry_digest(entries: Iterable[Mapping[str, Any]]) -> str:
    body = "\n".join(
        canonical_line(entry)
        for entry in sorted(
            entries,
            key=lambda row: (
                str(row["review_class"]),
                str(row["rule"]),
                int(row["block_id"]),
                int(row["record_id"]),
                str(row["finding_signature_sha256"]),
            ),
        )
    )
    return sha256_bytes(body.encode("ascii"))


def build(input_path: Path) -> dict[str, Any]:
    report_blob = input_path.read_bytes()
    report_sha256 = sha256_bytes(report_blob)
    if report_sha256 != EXPECTED_PRIVATE_REPORT_SHA256:
        raise ValueError(
            "unexpected private review report: "
            f"{report_sha256}"
        )
    report = json.loads(report_blob.decode("utf-8"))
    if int(report.get("issue_count", -1)) != EXPECTED_PRIVATE_ISSUE_COUNT:
        raise ValueError("unexpected private review issue count")
    resources = report.get("resources", {})
    if (
        resources.get("base_msggame", {}).get("sha256")
        != EXPECTED_BASE_INPUT_SHA256
        or resources.get("pk_msggame", {}).get("sha256")
        != EXPECTED_PK_INPUT_SHA256
    ):
        raise ValueError("unexpected reviewed input resource hashes")

    reviewed = reviewed_coordinate_rules()
    if len(SELECTOR_SIDE_COORDINATES) != EXPECTED_SELECTOR_SIDE_COUNT:
        raise ValueError("unexpected selector-side review cardinality")
    if (
        sum(len(values) for values in NON_SIDE_FALSE_COORDINATES.values())
        != EXPECTED_NON_SIDE_COUNT
    ):
        raise ValueError("unexpected non-side review cardinality")
    if len(reviewed) != EXPECTED_ENTRY_COUNT:
        raise ValueError("unexpected reviewed coordinate/rule cardinality")

    selected: list[dict[str, Any]] = []
    matched: Counter[tuple[tuple[int, int], str]] = Counter()
    for finding in report.get("issues", ()):
        if finding.get("resource") != "pk_msggame":
            continue
        key = (
            (
                int(finding["block_id"]),
                int(finding["record_id"]),
            ),
            str(finding["rule"]),
        )
        review_class = reviewed.get(key)
        if review_class is None:
            continue
        selected.append(contract_entry(finding, review_class))
        matched[key] += 1

    missing = sorted(set(reviewed) - set(matched))
    repeated = sorted(key for key, count in matched.items() if count != 1)
    if missing or repeated:
        raise ValueError(
            "review selection mismatch: "
            f"missing={missing}, repeated={repeated}"
        )
    if len(selected) != EXPECTED_ENTRY_COUNT:
        raise ValueError("unexpected selected finding count")

    selected.sort(
        key=lambda row: (
            str(row["review_class"]),
            str(row["rule"]),
            int(row["block_id"]),
            int(row["record_id"]),
            str(row["finding_signature_sha256"]),
        )
    )
    rule_counts = Counter(str(row["rule"]) for row in selected)
    review_class_counts = Counter(
        str(row["review_class"]) for row in selected
    )
    coordinate_rule_body = "\n".join(
        f"{row['block_id']}:{row['record_id']}:{row['rule']}"
        for row in selected
    )
    return {
        "schema": SCHEMA,
        "source_free": True,
        "private_text_included": False,
        "application_contract": {
            "candidate_file_hash_required": False,
            "exact_finding_signature_required": True,
            "rule_only_suppression_forbidden": True,
            "coordinate_rule_only_suppression_forbidden": True,
        },
        "review_provenance": {
            "private_report_sha256": report_sha256,
            "base_input_sha256": EXPECTED_BASE_INPUT_SHA256,
            "pk_input_sha256": EXPECTED_PK_INPUT_SHA256,
            "private_issue_count": EXPECTED_PRIVATE_ISSUE_COUNT,
        },
        "review_class_counts": dict(sorted(review_class_counts.items())),
        "rule_counts": dict(sorted(rule_counts.items())),
        "coordinate_rule_sha256": sha256_bytes(
            coordinate_rule_body.encode("ascii")
        ),
        "entry_count": len(selected),
        "entry_sha256": entry_digest(selected),
        "entries": selected,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = canonical_json(build(args.input))
    if args.check:
        if not args.output.exists():
            raise ValueError(f"contract is absent: {args.output}")
        if args.output.read_text(encoding="utf-8") != payload:
            raise ValueError("tracked contract differs from reviewed rebuild")
        return 0
    args.output.write_text(payload, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
