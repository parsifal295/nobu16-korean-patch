#!/usr/bin/env python3
"""Build the root-disjoint two-chunk assignment for PK selector 1090."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER_PATH = WORKSTREAM / "build_pk_selector1198_assignment_v1.py"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector178_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector178_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector178_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = DIALOGUE_TMP / "pk_selector1090_assignment.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1090_assignment_coverage.v1.json"
)

SELECTOR = 1090
TERMINALS = tuple(range(2574, 2581))
PRIVATE_SCHEMA = "nobu16.kr.pk-selector1090-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1090-assignment-coverage.v1"
METHOD = (
    "selector178_checkpoint_selector1090_root_disjoint_two_chunk_"
    "template_atom_assignment"
)
EXPECTED_INPUT_SHA256 = {
    "ledger": "A11DC8F5F0BAA9532DCB7737AFAFC8732506AC2F4E4B6479B44056CF9958015D",
    "checkpoint_public":
        "8850CDFFDEF13076DF8402F68AA4F72528C9ACEE8145F4A65B4FAF64C7A27742",
    "ranking_builder":
        "678387EB0A7FE13AF9FDD5C19D8757A4220FE523BFB1C7BD806C5482FC8A2479",
    "ranking_private":
        "992EBD7FAC8ABCF99268E2B0C3139837FCB4CE87502B9A24DB8EF9414D465D4E",
    "ranking_public":
        "747608515DA8ADA09A2C990ABC148F041E19E138FCA8CC4C93D6641EE04208FA",
    "base_assignment":
        "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF",
    "helper":
        "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5",
}
EXPECTED_PK_CANDIDATE_SHA256 = (
    "D89D47866F7FA9D34F68814219A00840921C130E062EA5DE80F95063B9E96E7F"
)
EXPECTED_COVERAGE = (96, 92, 104, 8, 0, 41, 41, 80)
EXPECTED_SITE_ROW_SHA256: str | None = (
    "2593EE342C150FFDDDD8944FC3EB3E6A6F912B6BF6C5C275328678E778E1877D"
)
EXPECTED_TEMPLATE_SIZES: tuple[int, ...] | None = (2, 5, 5)
EXPECTED_CHUNK_METRICS: tuple[tuple[int, ...], ...] | None = (
    (47, 45, 19, 41, 7, 936),
    (49, 47, 22, 39, 3, 938),
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "B256F67F1A584D8895BA7BDCCA764338A9F9A08B12C78F00579703035AC090FA"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "917E3C6087EE4593EEEA0529A2FE88E6D68FE16A69CBC61A0476113EE719EE9B"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGNMENT = load_module(BASE_BUILDER_PATH, "pk_selector1090_assignment_base_v1")
RANKING_WRAPPER = load_module(
    RANKING_BUILDER_PATH,
    "pk_selector1090_ranking_v1",
)
RANKING = RANKING_WRAPPER.RANKING
ENGINE = RANKING.ENGINE
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE

for _name in (
    "RANKING_BUILDER_PATH",
    "RANKING_PRIVATE_PATH",
    "RANKING_PUBLIC_PATH",
    "DEFAULT_PRIVATE_OUTPUT",
    "DEFAULT_PUBLIC_OUTPUT",
    "SELECTOR",
    "TERMINALS",
    "PRIVATE_SCHEMA",
    "PUBLIC_SCHEMA",
    "METHOD",
    "EXPECTED_INPUT_SHA256",
    "EXPECTED_PK_CANDIDATE_SHA256",
    "EXPECTED_COVERAGE",
    "EXPECTED_SITE_ROW_SHA256",
    "EXPECTED_TEMPLATE_SIZES",
    "EXPECTED_CHUNK_METRICS",
    "EXPECTED_PRIVATE_FILE_SHA256",
    "EXPECTED_PUBLIC_FILE_SHA256",
):
    setattr(ASSIGNMENT, _name, globals()[_name])

ASSIGNMENT.RANKING_WRAPPER = RANKING_WRAPPER
ASSIGNMENT.RANKING = RANKING
ASSIGNMENT.ENGINE = ENGINE
for _module in (ASSIGNMENT.BASE, ASSIGNMENT.RECORDS):
    _module.RANKING_WRAPPER = RANKING_WRAPPER
    _module.RANKING = RANKING
    _module.ENGINE = ENGINE
    _module.SELECTOR = SELECTOR
    _module.TERMINALS = TERMINALS
    _module.EXPECTED_PK_CANDIDATE_SHA256 = EXPECTED_PK_CANDIDATE_SHA256
ASSIGNMENT.RECORDS.OFFICIAL_LEDGER_PATH = RANKING_WRAPPER.DEFAULT_LEDGER
ASSIGNMENT.HELPER.RANKING = RANKING
ASSIGNMENT.HELPER.ENGINE = ENGINE
ASSIGNMENT.HELPER.LEGACY.RANKING = RANKING
ASSIGNMENT.HELPER.LEGACY.ENGINE = ENGINE
ASSIGNMENT.HELPER.LEGACY.SELECTOR = SELECTOR
ASSIGNMENT.HELPER.LEGACY.TERMINALS = TERMINALS

AssignmentError = ASSIGNMENT.AssignmentError
require = ASSIGNMENT.require
sha256_file = ASSIGNMENT.sha256_file
assert_source_free = ASSIGNMENT.assert_source_free


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    """Run the frozen generic builder with its legacy handoff label adapted."""
    original_loads = ASSIGNMENT.json.loads

    def adapted_loads(value: str, *args: Any, **kwargs: Any) -> Any:
        result = original_loads(value, *args, **kwargs)
        if not isinstance(result, dict):
            return result
        if "direct_targets" in result:
            for row in result["direct_targets"]:
                if row.get("target_coordinate") == "0:1090":
                    row["target_coordinate"] = "0:1198"
                    break
        recommendation = result.get("recommendation")
        if (
            isinstance(recommendation, dict)
            and recommendation.get("selector_coordinate") == "0:1090"
        ):
            recommendation["selector_coordinate"] = "0:1198"
        return result

    ASSIGNMENT.json.loads = adapted_loads
    try:
        _private_content, _public_content, private, public = (
            ASSIGNMENT.build_outputs()
        )
    finally:
        ASSIGNMENT.json.loads = original_loads
    private["scope"]["selector_coordinate"] = "0:1090:0"
    public["scope"]["official_pending_rows"] = 6432
    private_content = ASSIGNMENT.serialized_json(private)
    public["guards"] = {
        "private_assignment_sha256":
            ASSIGNMENT.sha256_bytes(private_content.encode("utf-8")),
        "payload_without_guards_canonical_sha256":
            ASSIGNMENT.canonical_sha256(
                {key: value for key, value in public.items() if key != "guards"}
            ),
    }
    assert_source_free(public)
    return (
        private_content,
        ASSIGNMENT.serialized_json(public),
        private,
        public,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    private_content, public_content, _private, public = build_outputs()
    private_sha = ASSIGNMENT.sha256_bytes(private_content.encode("utf-8"))
    public_sha = ASSIGNMENT.sha256_bytes(public_content.encode("utf-8"))
    if EXPECTED_PRIVATE_FILE_SHA256:
        require(private_sha == EXPECTED_PRIVATE_FILE_SHA256, "private drift")
    if EXPECTED_PUBLIC_FILE_SHA256:
        require(public_sha == EXPECTED_PUBLIC_FILE_SHA256, "public drift")
    if args.check:
        require(
            DEFAULT_PRIVATE_OUTPUT.read_text(encoding="utf-8")
            == private_content,
            "private artifact drift",
        )
        require(
            DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
            == public_content,
            "public artifact drift",
        )
    else:
        DEFAULT_PRIVATE_OUTPUT.write_text(
            private_content, encoding="utf-8", newline=""
        )
        DEFAULT_PUBLIC_OUTPUT.write_text(
            public_content, encoding="ascii", newline=""
        )
    print(json.dumps({
        "chunks": [
            [
                row["site_count"],
                row["pending_row_upper_bound"],
                row["workload_weight"],
            ]
            for row in public["assignment"]["chunks"]
        ],
        "private_sha256": private_sha,
        "public_sha256": public_sha,
        "source_only_repair_sites":
            public["coverage"]["source_only_repair_site_count"],
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
