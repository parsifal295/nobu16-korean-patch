#!/usr/bin/env python3
"""Build a source-free contract for reviewed Base Kiwi spacing false positives."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
DEFAULT_INPUT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "kiwi-spacing-high-confidence-base-35170.private.v1.json"
)
DEFAULT_OUTPUT = (
    SCRIPT.parent
    / "base_spacing_false_signature_contract.source_free.v1.json"
)
DEFAULT_POST_INPUT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "kiwi-spacing-high-confidence-base-d4dee.private.v1.json"
)
DEFAULT_SIGNATURE_INPUT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "kiwi-spacing-high-confidence-base-23fad.private.v1.json"
)
SCHEMA = "nobu16.kr.base-spacing-false-signature-contract.source-free.v1"
EXPECTED_PRIVATE_REPORT_SHA256 = (
    "0F4F92579C420CD5AA4ECB5C8880EABDEFE833AD6176CAB5BE85CC5A48CE49E8"
)
EXPECTED_INPUT_SHA256 = (
    "35170AF2008C92FB9D435342C039151994D69B564973F63B6FAF78B4FE18FF19"
)
EXPECTED_POST_REPORT_SHA256 = (
    "12A00F6C491ADC718EA0972A74190F34F08B0B41B95833B52F386CB46CDE1285"
)
EXPECTED_POST_INPUT_SHA256 = (
    "D4DEE16105252F77963B5996E50BB24B35B992503A306C069995E93B19DE0361"
)
EXPECTED_SIGNATURE_REPORT_SHA256 = (
    "493EF6D60CD95A07E01D9C1D749F92F1A5BCA1C5021088D100B415F9B0952799"
)
EXPECTED_SIGNATURE_INPUT_SHA256 = (
    "23FAD4AEF732C777CF1B9A167B78D1500B3D04366FC95C46B63E9709843F4A1F"
)
EXPECTED_COUNTS = {
    "particle_to_lexeme": {
        "coordinate_count": 100,
        "finding_count": 151,
        "signature_count": 20,
    },
    "etm_to_lexeme": {
        "coordinate_count": 96,
        "finding_count": 224,
        "signature_count": 29,
    },
}
EXPECTED_CONTRACT_COUNTS = {
    "particle_to_lexeme": {
        "coordinate_count": 102,
        "finding_count": 153,
        "signature_count": 22,
    },
    "etm_to_lexeme": {
        "coordinate_count": 96,
        "finding_count": 224,
        "signature_count": 29,
    },
    "adverb_to_lexeme": {
        "coordinate_count": 226,
        "finding_count": 701,
        "signature_count": 31,
    },
    "nominal_to_bound_noun": {
        "coordinate_count": 220,
        "finding_count": 406,
        "signature_count": 32,
    },
    "nominal_to_predicate": {
        "coordinate_count": 343,
        "finding_count": 462,
        "signature_count": 59,
    },
}
# The four mixed particle coordinates also contain a real missing-space
# signature.  This digest selects only the independently reviewed compound
# false positive and therefore stores no Korean source or translation text.
MIXED_PARTICLE_COORDINATES = {
    (2, 69),
    (2, 334),
    (6, 3393),
    (6, 3398),
}
MIXED_PARTICLE_FALSE_SIGNATURE_SHA256 = (
    "43EA00DF236696343CA08260FEC169D6CB5E0D0995CA0A8F30BF940740CB50E8"
)
POST_REMEDIATION_FALSE_SIGNATURES = {
    (
        "particle_to_lexeme",
        "43EA00DF236696343CA08260FEC169D6CB5E0D0995CA0A8F30BF940740CB50E8",
        (6, 129),
    ),
    (
        "particle_to_lexeme",
        "262FEF69DC7412ED21C0D0570F89BE6A5C74BE82AF938A14CA18988EFD6D7F3C",
        (9, 264),
    ),
    (
        "particle_to_lexeme",
        "3C104B58EA7B992642BEB87DA6D86704447BA365D676E48B4BEAD9E160206CA8",
        (9, 3274),
    ),
    (
        "particle_to_lexeme",
        "3C104B58EA7B992642BEB87DA6D86704447BA365D676E48B4BEAD9E160206CA8",
        (9, 3275),
    ),
    (
        "particle_to_lexeme",
        "262FEF69DC7412ED21C0D0570F89BE6A5C74BE82AF938A14CA18988EFD6D7F3C",
        (9, 3467),
    ),
}


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


FALSE_COORDINATES = {
    "particle_to_lexeme": parse_coordinates(
        """
        1:5,
        2:18, 2:69, 2:70, 2:127, 2:261, 2:334, 2:335, 2:490, 2:617,
        6:9, 6:113, 6:115, 6:408, 6:1406, 6:2814, 6:2838, 6:3393,
        6:3398, 6:3402, 6:3513, 6:4213, 6:4576,
        7:20, 7:21, 7:28, 7:39, 7:82, 7:87, 7:88, 7:274, 7:564,
        7:573, 7:997, 7:1164, 7:1244, 7:1324, 7:1338, 7:1355,
        7:1443, 7:1445, 7:1472, 7:1513, 7:1552, 7:1635, 7:1659,
        7:1758, 7:2612, 7:2663, 7:2677,
        8:57, 8:59, 8:62, 8:452, 8:485, 8:578, 8:1049, 8:1065,
        8:1100,
        9:28, 9:47, 9:74, 9:137, 9:173, 9:250, 9:576, 9:807,
        9:1132, 9:1895, 9:2330, 9:3295,
        13:246, 13:249, 13:389, 13:390,
        14:12, 14:41, 14:99, 14:105, 14:106, 14:116, 14:117, 14:142,
        15:615, 15:1434, 15:1600, 15:1646, 15:1655, 15:2308-2316,
        15:2326-2327,
        16:48
        """
    ),
    "etm_to_lexeme": parse_coordinates(
        """
        4:42,
        6:20, 6:29, 6:30, 6:135, 6:164, 6:628, 6:858, 6:880,
        6:1696, 6:3482, 6:4033,
        7:59, 7:97, 7:100, 7:103, 7:1449, 7:2162, 7:2454,
        7:2739-2743, 7:2754-2758,
        8:44, 8:72, 8:83, 8:95, 8:317, 8:747, 8:878, 8:971,
        8:1084, 8:1109, 8:1117,
        9:1, 9:21, 9:111, 9:151, 9:199, 9:341, 9:494, 9:1580,
        9:2062, 9:2669,
        12:55,
        13:8, 13:400-401, 13:425,
        14:7, 14:12, 14:47, 14:75, 14:93, 14:123,
        15:23, 15:29, 15:31-32, 15:67, 15:117, 15:141, 15:146,
        15:495, 15:497, 15:500-501, 15:505, 15:515, 15:518,
        15:569, 15:571, 15:593, 15:605, 15:632, 15:634, 15:915,
        15:916, 15:1194, 15:1198, 15:1201, 15:1203, 15:1204,
        15:1670, 15:1832, 15:1850, 15:1861, 15:2265, 15:2330,
        15:2409
        """
    ),
}

ACTUAL_SIGNATURE_COORDINATES = {
    "adverb_to_lexeme": parse_coordinates(
        """
        6:150, 6:3541, 6:3680,
        7:26, 7:72, 7:266, 7:876,
        8:55, 8:73, 8:99, 8:278, 8:397, 8:758, 8:993,
        9:191, 9:2571, 9:3676,
        15:1, 15:5, 15:104, 15:147, 15:149, 15:157, 15:252,
        15:254, 15:267, 15:1540, 15:1628, 15:1896, 15:1898,
        15:2064
        """
    ),
    "nominal_to_bound_noun": parse_coordinates(
        """
        2:113, 2:114,
        6:18, 6:20, 6:28, 6:86, 6:98, 6:99, 6:118, 6:120,
        6:125, 6:126, 6:185, 6:274, 6:596, 6:629, 6:633, 6:639,
        6:824, 6:825, 6:1546, 6:1557, 6:1563, 6:1568, 6:1570,
        6:1577, 6:2451, 6:2722, 6:2736, 6:2910, 6:2915, 6:2917,
        6:2922, 6:2927, 6:2929, 6:3260, 6:3262, 6:3285, 6:3288,
        6:4027, 6:4030,
        7:79, 7:941, 7:949, 7:951, 7:1340, 7:1653, 7:1663,
        7:1670, 7:1678, 7:1684,
        9:47, 9:105, 9:199, 9:808, 9:811, 9:1505, 9:2672,
        15:126, 15:135, 15:145, 15:803, 15:1805, 15:1827,
        15:1829, 15:2264
        """
    ),
    "nominal_to_predicate": parse_coordinates(
        """
        6:44, 6:155, 6:2237, 6:3386, 6:3537,
        7:2438, 7:2764,
        8:34, 8:46, 8:275, 8:327,
        15:5, 15:94, 15:140, 15:203, 15:254, 15:804, 15:1410,
        15:2154, 15:2346, 15:2376
        """
    ),
}
MIXED_FALSE_SIGNATURES = {
    "adverb_to_lexeme": {
        "3D906D58619A7E6537819BAE877ADBD34F383208D3665B636941A8C133CAF4E4",
    },
    "nominal_to_bound_noun": set(),
    "nominal_to_predicate": {
        "9183876D5F212F4373839674376F9E79B4A9FB0797C4E049A0097E1F84AC448B",
    },
}
EXPECTED_SIGNATURE_CLASSIFICATION = {
    "adverb_to_lexeme": {
        "actual_signature_count": 20,
        "false_coordinate_count": 227,
        "false_finding_count": 785,
        "false_signature_count": 32,
    },
    "nominal_to_bound_noun": {
        "actual_signature_count": 44,
        "false_coordinate_count": 220,
        "false_finding_count": 408,
        "false_signature_count": 32,
    },
    "nominal_to_predicate": {
        "actual_signature_count": 32,
        "false_coordinate_count": 341,
        "false_finding_count": 460,
        "false_signature_count": 59,
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def coordinate_digest(values: Iterable[tuple[int, int]]) -> str:
    body = "\n".join(
        f"{block_id}:{record_id}"
        for block_id, record_id in sorted(values)
    )
    return sha256_bytes(body.encode("ascii"))


def signature_digest(row: dict[str, Any]) -> str:
    body = "|".join(
        (
            str(row["category"]),
            str(row["left"]["form"]),
            str(row["left"]["tag"]),
            str(row["right"]["form"]),
            str(row["right"]["tag"]),
        )
    )
    return sha256_bytes(body.encode("utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def build(
    input_path: Path,
    post_input_path: Path,
    signature_input_path: Path = DEFAULT_SIGNATURE_INPUT,
) -> dict[str, Any]:
    private_bytes = input_path.read_bytes()
    require(
        sha256_bytes(private_bytes) == EXPECTED_PRIVATE_REPORT_SHA256,
        "reviewed private spacing report drifted",
    )
    source = json.loads(private_bytes)
    require(
        source.get("input_sha256") == EXPECTED_INPUT_SHA256,
        "reviewed spacing candidate drifted",
    )
    for category, expected in EXPECTED_COUNTS.items():
        require(
            len(FALSE_COORDINATES[category])
            == expected["coordinate_count"],
            f"{category} reviewed coordinate transcription drifted",
        )

    reviewed_false_signatures: dict[str, set[str]] = defaultdict(set)
    discovery_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source["issues"]:
        category = str(row["category"])
        if category not in FALSE_COORDINATES:
            continue
        coordinate = (int(row["block_id"]), int(row["record_id"]))
        if coordinate not in FALSE_COORDINATES[category]:
            continue
        digest = signature_digest(row)
        if (
            category == "particle_to_lexeme"
            and coordinate in MIXED_PARTICLE_COORDINATES
            and digest != MIXED_PARTICLE_FALSE_SIGNATURE_SHA256
        ):
            continue
        reviewed_false_signatures[category].add(digest)
        discovery_rows[category].append(row)

    for category, expected in EXPECTED_COUNTS.items():
        rows = discovery_rows[category]
        require(
            len(rows) == expected["finding_count"],
            f"{category} reviewed false-finding count drifted",
        )
        require(
            len(
                {
                    (int(row["block_id"]), int(row["record_id"]))
                    for row in rows
                }
            )
            == expected["coordinate_count"],
            f"{category} reviewed false-coordinate count drifted",
        )
        require(
            len(reviewed_false_signatures[category])
            == expected["signature_count"],
            f"{category} reviewed false-signature count drifted",
        )

    signature_bytes = signature_input_path.read_bytes()
    require(
        sha256_bytes(signature_bytes) == EXPECTED_SIGNATURE_REPORT_SHA256,
        "reviewed adverb/nominal signature report drifted",
    )
    signature_source = json.loads(signature_bytes)
    require(
        signature_source.get("input_sha256")
        == EXPECTED_SIGNATURE_INPUT_SHA256,
        "reviewed adverb/nominal candidate drifted",
    )
    for category, expected in EXPECTED_SIGNATURE_CLASSIFICATION.items():
        category_rows = [
            row
            for row in signature_source["issues"]
            if row["category"] == category
        ]
        all_signatures = {
            signature_digest(row) for row in category_rows
        }
        actual_signatures = {
            signature_digest(row)
            for row in category_rows
            if (
                int(row["block_id"]),
                int(row["record_id"]),
            )
            in ACTUAL_SIGNATURE_COORDINATES[category]
            and signature_digest(row)
            not in MIXED_FALSE_SIGNATURES[category]
        }
        false_signatures = all_signatures - actual_signatures
        false_rows = [
            row
            for row in category_rows
            if signature_digest(row) in false_signatures
        ]
        false_coordinates = {
            (int(row["block_id"]), int(row["record_id"]))
            for row in false_rows
        }
        require(
            len(actual_signatures)
            == expected["actual_signature_count"],
            f"{category} actual-signature classification drifted",
        )
        require(
            len(false_signatures)
            == expected["false_signature_count"],
            f"{category} false-signature classification drifted",
        )
        require(
            len(false_rows) == expected["false_finding_count"],
            f"{category} false-finding classification drifted",
        )
        require(
            len(false_coordinates)
            == expected["false_coordinate_count"],
            f"{category} false-coordinate classification drifted",
        )
        reviewed_false_signatures[category].update(false_signatures)

    post_bytes = post_input_path.read_bytes()
    require(
        sha256_bytes(post_bytes) == EXPECTED_POST_REPORT_SHA256,
        "post-remediation private spacing report drifted",
    )
    post_source = json.loads(post_bytes)
    require(
        post_source.get("input_sha256") == EXPECTED_POST_INPUT_SHA256,
        "post-remediation spacing candidate drifted",
    )
    reviewed_false_signatures["particle_to_lexeme"].update(
        signature
        for category, signature, _coordinate
        in POST_REMEDIATION_FALSE_SIGNATURES
        if category == "particle_to_lexeme"
    )

    grouped: dict[
        tuple[str, str],
        list[tuple[int, int]],
    ] = defaultdict(list)
    finding_counts: dict[tuple[str, str], int] = defaultdict(int)
    post_found: set[tuple[str, str, tuple[int, int]]] = set()
    for row in post_source["issues"]:
        category = str(row["category"])
        if category not in EXPECTED_CONTRACT_COUNTS:
            continue
        coordinate = (int(row["block_id"]), int(row["record_id"]))
        digest = signature_digest(row)
        key = (category, digest, coordinate)
        require(
            digest in reviewed_false_signatures[category],
            f"unreviewed current spacing signature at "
            f"{coordinate}: {category}:{digest}",
        )
        grouped[(category, digest)].append(coordinate)
        finding_counts[(category, digest)] += 1
        if key in POST_REMEDIATION_FALSE_SIGNATURES:
            post_found.add(key)
    require(
        post_found == POST_REMEDIATION_FALSE_SIGNATURES,
        "post-remediation false-signature extension drifted",
    )

    entries = []
    for (category, digest), coordinates in sorted(grouped.items()):
        unique_coordinates = sorted(set(coordinates))
        entries.append(
            {
                "category": category,
                "coordinate_count": len(unique_coordinates),
                "coordinate_sha256": coordinate_digest(unique_coordinates),
                "coordinates": [
                    [block_id, record_id]
                    for block_id, record_id in unique_coordinates
                ],
                "finding_count": finding_counts[(category, digest)],
                "signature_sha256": digest,
            }
        )

    category_summaries = {}
    for category, expected in EXPECTED_CONTRACT_COUNTS.items():
        category_entries = [
            row for row in entries if row["category"] == category
        ]
        coordinates = {
            tuple(coordinate)
            for row in category_entries
            for coordinate in row["coordinates"]
        }
        finding_count = sum(
            int(row["finding_count"]) for row in category_entries
        )
        require(
            len(category_entries) == expected["signature_count"],
            f"{category} false-signature count drifted",
        )
        require(
            len(coordinates) == expected["coordinate_count"],
            f"{category} current false-coordinate count drifted",
        )
        require(
            finding_count == expected["finding_count"],
            f"{category} false-finding count drifted",
        )
        category_summaries[category] = {
            "coordinate_count": len(coordinates),
            "coordinate_sha256": coordinate_digest(coordinates),
            "finding_count": finding_count,
            "signature_count": len(category_entries),
        }

    entry_body = "\n".join(
        (
            f"{row['category']}:{row['signature_sha256']}:"
            f"{row['coordinate_count']}:{row['coordinate_sha256']}:"
            f"{row['finding_count']}"
        )
        for row in entries
    )
    return {
        "category_summaries": category_summaries,
        "discovery_input_sha256": EXPECTED_INPUT_SHA256,
        "discovery_report_sha256": EXPECTED_PRIVATE_REPORT_SHA256,
        "entries": entries,
        "entry_count": len(entries),
        "entry_sha256": sha256_bytes(entry_body.encode("ascii")),
        "post_remediation_input_sha256": EXPECTED_POST_INPUT_SHA256,
        "post_remediation_report_sha256": EXPECTED_POST_REPORT_SHA256,
        "private_text_included": False,
        "schema": SCHEMA,
        "signature_discovery_input_sha256":
            EXPECTED_SIGNATURE_INPUT_SHA256,
        "signature_discovery_report_sha256":
            EXPECTED_SIGNATURE_REPORT_SHA256,
        "steam_write_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--post-input",
        type=Path,
        default=DEFAULT_POST_INPUT,
    )
    parser.add_argument(
        "--signature-input",
        type=Path,
        default=DEFAULT_SIGNATURE_INPUT,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(
        args.input,
        args.post_input,
        args.signature_input,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(canonical_json(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "entry_count": payload["entry_count"],
                "entry_sha256": payload["entry_sha256"],
                "output": str(args.output.resolve()),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
