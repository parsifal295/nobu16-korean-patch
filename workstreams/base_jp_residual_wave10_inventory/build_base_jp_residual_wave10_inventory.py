#!/usr/bin/env python3
"""Inventory the source-script residuals left by the base JP Switch-v1.3 transfer.

This module reads the pinned local Steam and Switch inputs only to derive
source-free planning artifacts.  It never writes a game resource, a current
candidate, or a release archive.  The generated public files contain stable
coordinates, source hashes, Korean-target hashes, classifications, and future
transform contracts; they deliberately contain no commercial source prose.
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
from typing import Any, Iterable


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MSGGAME_BUILDER = (
    REPO
    / "workstreams"
    / "tutorial_dialogue_trace_msggame_v1"
    / "build_base_msggame_switch_v13_overlay.py"
)
EV_BUILDER = (
    REPO
    / "workstreams"
    / "base_ev_strdata_jp_switch_v13_transfer_v1"
    / "build_base_ev_strdata_jp_switch_v13_transfer_v1.py"
)

PUBLIC = HERE / "public"
INVENTORY_PATH = PUBLIC / "base_jp_residual_wave10_inventory.v1.json"
CONTRACTS_PATH = PUBLIC / "base_jp_residual_wave10_contracts.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"

INVENTORY_SCHEMA = "nobu16.kr.base-jp-residual-wave10-inventory.v1"
CONTRACT_SCHEMA = "nobu16.kr.base-jp-residual-wave10-contracts.v1"
VALIDATION_SCHEMA = "nobu16.kr.base-jp-residual-wave10-validation.v1"

EXPECTED = {
    "base_msggame_residual": 332,
    "base_ev_strdata_residual": 45,
    "safe_punctuation_msggame": 207,
    "safe_edge_whitespace_msggame": 62,
    "safe_percent_msggame": 1,
    "manual_hanja_msggame": 3,
    "format_token_msggame": 59,
    "safe_punctuation_ev_strdata": 40,
    "manual_hanja_ev_strdata": 5,
    "safe_contract": 310,
    "manual_term_review": 8,
    "format_token": 59,
    "visible": 318,
    "total": 377,
}

# Narrow lexical-script checks intentionally exclude U+30FB.  The earlier
# strict transfer used a broader range that treated the middle-dot separator
# as source script, which is why already-Korean visible rows remained out.
HAN_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_LETTER_RE = re.compile(r"[\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FD-\u30FF\u31F0-\u31FF]")
PUBLIC_FORBIDDEN_RE = re.compile(
    r"[\u3040-\u30FF\u31F0-\u31FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]"
)
MIDDLE_DOT = "・"


class InventoryError(ValueError):
    """Raised when the pinned residual partition or public model differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InventoryError(f"invalid UTF-8 JSON: {path}") from exc
    if not isinstance(value, dict):
        raise InventoryError(f"JSON root is not an object: {path}")
    return value, blob


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise InventoryError(f"cannot import builder: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def has_lexical_source_script(text: str) -> bool:
    return HAN_RE.search(text) is not None or KANA_LETTER_RE.search(text) is not None


def has_only_middle_dot_source_script(text: str) -> bool:
    return bool(PUBLIC_FORBIDDEN_RE.search(text)) and set(PUBLIC_FORBIDDEN_RE.findall(text)) == {MIDDLE_DOT}


def edge_normalized(source: str, korean: str) -> str:
    """Match only edge whitespace to the source while retaining Korean text."""
    leading = source[: len(source) - len(source.lstrip())]
    trailing = source[len(source.rstrip()) :]
    return leading + korean.strip() + trailing


def coordinate_sha256(coordinates: Iterable[tuple[int, int, int]]) -> str:
    return sha256(
        "".join(
            f"{block}:{record}:{literal}\n"
            for block, record, literal in sorted(coordinates)
        ).encode("ascii")
    )


def id_sha256(ids: Iterable[int]) -> str:
    return sha256("".join(f"{entry_id}\n" for entry_id in sorted(ids)).encode("ascii"))


def rows_sha256(rows: Iterable[dict[str, Any]]) -> str:
    return sha256(canonical_json_bytes(list(rows)))


def msggame_role(block_id: int) -> str:
    roles = {
        4: "settings_help",
        6: "map_event_or_system_fragment",
        7: "effect_or_battle_notification",
        8: "battle_status_notification",
        9: "battlefield_dialogue",
        10: "rule_text",
        12: "format_token",
        13: "strategy_and_battle_tutorial",
        14: "map_help_tutorial",
        15: "advisor_or_event_fragment",
    }
    try:
        return roles[block_id]
    except KeyError as exc:
        raise InventoryError(f"unexpected base msggame residual block: {block_id}") from exc


def visible_priority(role: str) -> str:
    return "p0" if role != "format_token" else "none"


def make_msggame_rows(builder: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base = builder.load_base(builder.DEFAULT_GAME_ROOT)
    switch = builder.load_switch(builder.DEFAULT_SWITCH_ZIP)
    eligible = set(builder.eligible_coordinates(base, switch))
    source_coordinates = {
        coordinate
        for coordinate, literal in base["literals"].items()
        if builder.has_japanese_script(literal.text)
    }
    residual = sorted(source_coordinates - eligible)
    if len(residual) != EXPECTED["base_msggame_residual"]:
        raise InventoryError(f"base msggame residual count differs: {len(residual)}")
    if source_coordinates & eligible != eligible:
        raise InventoryError("base msggame eligibility is not a source-script subset")

    inventory: list[dict[str, Any]] = []
    contracts: list[dict[str, Any]] = []
    for coordinate in residual:
        source = base["literals"][coordinate].text
        korean = switch["literals"][coordinate].text
        block_id, record_id, literal_id = coordinate
        role = msggame_role(block_id)
        mismatch = builder.common.invariant_mismatches(source, korean)
        source_hash = builder.text_hash(source)
        switch_hash = builder.text_hash(korean)
        row: dict[str, Any] = {
            "resource": builder.RESOURCE,
            "block_id": block_id,
            "record_id": record_id,
            "literal_id": literal_id,
            "source_jp_utf16le_sha256": source_hash,
            "switch_ko_utf16le_sha256": switch_hash,
            "role": role,
        }

        if not builder.HANGUL_RE.search(korean):
            if has_lexical_source_script(korean):
                raise InventoryError(f"non-Korean lexical text at base msggame {coordinate}")
            row |= {
                "role": "format_token",
                "classification": "format_token",
                "priority": "none",
                "action": "retain_as_nonsemantic_token",
            }
        elif has_lexical_source_script(korean):
            if KANA_LETTER_RE.search(korean):
                raise InventoryError(f"kana remains in Korean target at base msggame {coordinate}")
            row |= {
                "classification": "manual_hanja_gloss",
                "priority": "p1",
                "action": "manual_terminology_review",
            }
        elif mismatch:
            edge_only = all(
                item.startswith("leading_whitespace:") or item.startswith("trailing_whitespace:")
                for item in mismatch
            )
            if edge_only:
                planned = edge_normalized(source, korean)
                if builder.common.invariant_mismatches(source, planned):
                    raise InventoryError(f"edge normalization does not close {coordinate}")
                row |= {
                    "classification": "safe_edge_whitespace_normalized",
                    "priority": visible_priority(role),
                    "action": "contract_ready",
                    "transform": "switch_v13_match_source_edge_whitespace",
                    "planned_ko_utf16le_sha256": builder.text_hash(planned),
                }
            elif coordinate == (10, 3, 0):
                planned = korean.replace("%", "％")
                if planned == korean or builder.common.invariant_mismatches(source, planned):
                    raise InventoryError("percent normalization does not close the pinned rule row")
                row |= {
                    "classification": "safe_percent_format_normalized",
                    "priority": visible_priority(role),
                    "action": "contract_ready",
                    "transform": "switch_v13_ascii_percent_to_fullwidth",
                    "planned_ko_utf16le_sha256": builder.text_hash(planned),
                }
            else:
                raise InventoryError(f"unexpected base msggame invariant mismatch at {coordinate}: {mismatch!r}")
        else:
            if (
                not builder.has_japanese_script(korean)
                or has_lexical_source_script(korean)
                or not has_only_middle_dot_source_script(korean)
            ):
                raise InventoryError(f"unexpected punctuation partition at base msggame {coordinate}")
            row |= {
                "classification": "safe_punctuation_only_gate",
                "priority": visible_priority(role),
                "action": "contract_ready",
                "transform": "switch_v13_exact",
                "planned_ko_utf16le_sha256": switch_hash,
            }

        inventory.append(row)
        if row["action"] == "contract_ready":
            contracts.append(
                {
                    "resource": row["resource"],
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal_id,
                    "source_jp_utf16le_sha256": source_hash,
                    "planned_ko_utf16le_sha256": row["planned_ko_utf16le_sha256"],
                    "transform": row["transform"],
                }
            )

    if len(inventory) != EXPECTED["base_msggame_residual"]:
        raise InventoryError("base msggame inventory size changed")
    return inventory, contracts


def make_ev_strdata_rows(builder: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    _packed, _wrapper, _raw, steam = builder.load_steam_jp(builder.DEFAULT_GAME_ROOT)
    _switch_packed, _switch_wrapper, _switch_raw, switch = builder.load_switch_v13(
        builder.DEFAULT_SWITCH_ZIP
    )
    selected, residual, _hangul = builder.select_transfer_entries(steam, switch)
    selected_ids = {int(row["id"]) for row in selected}
    residual_ids = [int(row["id"]) for row in residual]
    if len(residual_ids) != EXPECTED["base_ev_strdata_residual"]:
        raise InventoryError(f"base ev_strdata residual count differs: {len(residual_ids)}")
    if set(selected_ids) & set(residual_ids):
        raise InventoryError("base ev_strdata strict and residual rows overlap")

    inventory: list[dict[str, Any]] = []
    contracts: list[dict[str, Any]] = []
    for entry_id in residual_ids:
        source = steam.texts[entry_id]
        korean = switch.texts[entry_id]
        source_hash = builder.text_hash(source)
        switch_hash = builder.text_hash(korean)
        if not builder.HANGUL_RE.search(korean) or not builder.SOURCE_SCRIPT_RE.search(korean):
            raise InventoryError(f"ev_strdata residual predicate changed at {entry_id}")
        if source_hash != next(row["source_jp_utf16le_sha256"] for row in residual if row["id"] == entry_id):
            raise InventoryError(f"ev_strdata residual source hash differs at {entry_id}")
        row: dict[str, Any] = {
            "resource": builder.RESOURCE,
            "id": entry_id,
            "source_jp_utf16le_sha256": source_hash,
            "switch_ko_utf16le_sha256": switch_hash,
            "role": "historical_event_narration_or_scene_label",
        }
        if has_lexical_source_script(korean):
            if KANA_LETTER_RE.search(korean):
                raise InventoryError(f"kana remains in Korean target at ev_strdata {entry_id}")
            row |= {
                "classification": "manual_hanja_gloss",
                "priority": "p1",
                "action": "manual_terminology_review",
            }
        else:
            if not has_only_middle_dot_source_script(korean):
                raise InventoryError(f"ev_strdata punctuation partition differs at {entry_id}")
            if builder.invariant_mismatches(source, korean):
                raise InventoryError(f"ev_strdata punctuation row invariant differs at {entry_id}")
            row |= {
                "classification": "safe_punctuation_only_gate",
                "priority": "p0",
                "action": "contract_ready",
                "transform": "switch_v13_exact",
                "planned_ko_utf16le_sha256": switch_hash,
            }
            contracts.append(
                {
                    "resource": row["resource"],
                    "id": entry_id,
                    "source_jp_utf16le_sha256": source_hash,
                    "planned_ko_utf16le_sha256": switch_hash,
                    "transform": "switch_v13_exact",
                }
            )
        inventory.append(row)
    return inventory, contracts


def count_rows(rows: Iterable[dict[str, Any]], key: str, value: str) -> int:
    return sum(1 for row in rows if row[key] == value)


def expected_models() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    msggame = load_module("base_jp_residual_wave10_msggame", MSGGAME_BUILDER)
    ev_strdata = load_module("base_jp_residual_wave10_ev_strdata", EV_BUILDER)
    msg_inventory, msg_contracts = make_msggame_rows(msggame)
    ev_inventory, ev_contracts = make_ev_strdata_rows(ev_strdata)
    inventory_rows = msg_inventory + ev_inventory
    contracts = msg_contracts + ev_contracts

    if len(inventory_rows) != EXPECTED["total"]:
        raise InventoryError(f"inventory total differs: {len(inventory_rows)}")
    if len(contracts) != EXPECTED["safe_contract"]:
        raise InventoryError(f"safe contract total differs: {len(contracts)}")
    if count_rows(msg_inventory, "classification", "safe_punctuation_only_gate") != EXPECTED["safe_punctuation_msggame"]:
        raise InventoryError("base msggame punctuation partition differs")
    if count_rows(msg_inventory, "classification", "safe_edge_whitespace_normalized") != EXPECTED["safe_edge_whitespace_msggame"]:
        raise InventoryError("base msggame edge-whitespace partition differs")
    if count_rows(msg_inventory, "classification", "safe_percent_format_normalized") != EXPECTED["safe_percent_msggame"]:
        raise InventoryError("base msggame percent partition differs")
    if count_rows(msg_inventory, "classification", "manual_hanja_gloss") != EXPECTED["manual_hanja_msggame"]:
        raise InventoryError("base msggame hanja partition differs")
    if count_rows(msg_inventory, "classification", "format_token") != EXPECTED["format_token_msggame"]:
        raise InventoryError("base msggame token partition differs")
    if count_rows(ev_inventory, "classification", "safe_punctuation_only_gate") != EXPECTED["safe_punctuation_ev_strdata"]:
        raise InventoryError("base ev_strdata punctuation partition differs")
    if count_rows(ev_inventory, "classification", "manual_hanja_gloss") != EXPECTED["manual_hanja_ev_strdata"]:
        raise InventoryError("base ev_strdata hanja partition differs")
    if count_rows(inventory_rows, "action", "manual_terminology_review") != EXPECTED["manual_term_review"]:
        raise InventoryError("manual terminology partition differs")
    if count_rows(inventory_rows, "classification", "format_token") != EXPECTED["format_token"]:
        raise InventoryError("format-token partition differs")
    if sum(1 for row in inventory_rows if row["priority"] == "p0") != EXPECTED["visible"] - EXPECTED["manual_term_review"]:
        raise InventoryError("p0 visible partition differs")

    msg_coordinates = [
        (int(row["block_id"]), int(row["record_id"]), int(row["literal_id"]))
        for row in msg_inventory
    ]
    msg_contract_coordinates = [
        (int(row["block_id"]), int(row["record_id"]), int(row["literal_id"]))
        for row in msg_contracts
    ]
    ev_ids = [int(row["id"]) for row in ev_inventory]
    ev_contract_ids = [int(row["id"]) for row in ev_contracts]
    contract_role_counts = Counter(
        row["role"] for row in inventory_rows if row["action"] == "contract_ready"
    )

    inventory = {
        "schema": INVENTORY_SCHEMA,
        "scope": {
            "base_language": "JP",
            "runtime": {"distribution": "Steam", "version": "1.1.7"},
            "current_candidate_modified": False,
            "installed_game_file_written": False,
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_switch_binary": False,
        },
        "summary": {
            "total_residual": EXPECTED["total"],
            "visible_rows": EXPECTED["visible"],
            "contract_ready_rows": EXPECTED["safe_contract"],
            "manual_terminology_review_rows": EXPECTED["manual_term_review"],
            "nonsemantic_format_token_rows": EXPECTED["format_token"],
        },
        "classification_findings": {
            "middle_dot_false_positive_rows": (
                EXPECTED["safe_punctuation_msggame"] + EXPECTED["safe_punctuation_ev_strdata"]
            ),
            "format_normalization_contract_rows": (
                EXPECTED["safe_edge_whitespace_msggame"] + EXPECTED["safe_percent_msggame"]
            ),
            "switch_target_kana_rows": 0,
            "pure_name_only_rows": 0,
            "hanja_gloss_rows": EXPECTED["manual_term_review"],
        },
        "priority_plan": {
            "p0_contract_ready": [
                {"role": "map_help_tutorial", "count": contract_role_counts["map_help_tutorial"]},
                {
                    "role": "strategy_and_battle_tutorial",
                    "count": contract_role_counts["strategy_and_battle_tutorial"],
                },
                {
                    "role": "historical_event_narration_or_scene_label",
                    "count": contract_role_counts["historical_event_narration_or_scene_label"],
                },
                {
                    "role": "advisor_or_event_fragment",
                    "count": contract_role_counts["advisor_or_event_fragment"],
                },
                {
                    "role": "map_event_or_system_fragment",
                    "count": contract_role_counts["map_event_or_system_fragment"],
                },
                {
                    "role": "battlefield_dialogue",
                    "count": contract_role_counts["battlefield_dialogue"],
                },
            ],
            "p1_manual_terminology_review": EXPECTED["manual_term_review"],
            "out_of_scope_nonsemantic_format_tokens": EXPECTED["format_token"],
        },
        "resources": {
            msggame.RESOURCE: {
                "residual_count": len(msg_inventory),
                "coordinate_sha256": coordinate_sha256(msg_coordinates),
                "contract_ready_count": len(msg_contracts),
                "contract_coordinate_sha256": coordinate_sha256(msg_contract_coordinates),
                "stock_jp": dict(msggame.BASE_PIN),
                "switch_v13_asset_sha256": msggame.SWITCH_ZIP_PIN["sha256"],
            },
            ev_strdata.RESOURCE: {
                "residual_count": len(ev_inventory),
                "ids_sha256": id_sha256(ev_ids),
                "contract_ready_count": len(ev_contracts),
                "contract_ids_sha256": id_sha256(ev_contract_ids),
                "stock_jp": dict(ev_strdata.STEAM_JP_PIN),
                "switch_v13_asset_sha256": ev_strdata.SWITCH_V13_PIN["archive_sha256"],
            },
        },
        "entries": inventory_rows,
    }
    contract_rows = sorted(
        contracts,
        key=lambda row: (
            row["resource"],
            row.get("block_id", -1),
            row.get("record_id", -1),
            row.get("literal_id", -1),
            row.get("id", -1),
        ),
    )
    contract = {
        "schema": CONTRACT_SCHEMA,
        "purpose": "future_disjoint_overlay_input_contracts",
        "distribution_policy": dict(inventory["distribution_policy"]),
        "entry_count": len(contract_rows),
        "entry_sha256": rows_sha256(contract_rows),
        "entries": contract_rows,
    }
    validation = {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "scope": dict(inventory["scope"]),
        "counts": dict(inventory["summary"]),
        "partition": {
            "base_msggame_residual": EXPECTED["base_msggame_residual"],
            "base_ev_strdata_residual": EXPECTED["base_ev_strdata_residual"],
            "safe_punctuation_msggame": EXPECTED["safe_punctuation_msggame"],
            "safe_edge_whitespace_msggame": EXPECTED["safe_edge_whitespace_msggame"],
            "safe_percent_msggame": EXPECTED["safe_percent_msggame"],
            "manual_hanja_msggame": EXPECTED["manual_hanja_msggame"],
            "format_token_msggame": EXPECTED["format_token_msggame"],
            "safe_punctuation_ev_strdata": EXPECTED["safe_punctuation_ev_strdata"],
            "manual_hanja_ev_strdata": EXPECTED["manual_hanja_ev_strdata"],
        },
        "artifacts": {
            INVENTORY_PATH.relative_to(HERE).as_posix(): {
                "sha256": sha256(canonical_json_bytes(inventory)),
                "size": len(canonical_json_bytes(inventory)),
            },
            CONTRACTS_PATH.relative_to(HERE).as_posix(): {
                "sha256": sha256(canonical_json_bytes(contract)),
                "size": len(canonical_json_bytes(contract)),
            },
        },
        "proofs": {
            "strict_transfer_domains_remain_disjoint": True,
            "all_contract_rows_are_visible_and_format_valid": True,
            "all_manual_rows_have_no_kana_in_switch_target": True,
            "all_token_rows_are_nonsemantic": True,
            "current_v5_or_later_candidate_untouched": True,
        },
        "safety": {
            "complete_candidate_binary_written": False,
            "installed_game_files_modified": False,
            "release_asset_written": False,
            "source_text_embedded": False,
        },
    }
    ensure_source_free(inventory, "inventory model")
    ensure_source_free(contract, "contract model")
    ensure_source_free(validation, "validation model")
    return inventory, contract, validation


def ensure_source_free(value: Any, label: str) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if PUBLIC_FORBIDDEN_RE.search(serialized):
        raise InventoryError(f"{label} contains source script")


def write_exact(path: Path, value: dict[str, Any]) -> None:
    blob = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    if path.read_bytes() != blob:
        raise InventoryError(f"write verification failed: {path}")


def generate() -> dict[str, Any]:
    inventory, contracts, validation = expected_models()
    write_exact(INVENTORY_PATH, inventory)
    write_exact(CONTRACTS_PATH, contracts)
    write_exact(VALIDATION_PATH, validation)
    return validation


def verify() -> dict[str, Any]:
    expected_inventory, expected_contracts, expected_validation = expected_models()
    for path, expected in (
        (INVENTORY_PATH, expected_inventory),
        (CONTRACTS_PATH, expected_contracts),
        (VALIDATION_PATH, expected_validation),
    ):
        actual, blob = load_json(path)
        if actual != expected:
            raise InventoryError(f"tracked artifact differs from model: {path}")
        if blob != canonical_json_bytes(actual):
            raise InventoryError(f"tracked artifact is not canonical: {path}")
        ensure_source_free(actual, str(path))
    return expected_validation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "verify"))
    args = parser.parse_args()
    result = generate() if args.command == "generate" else verify()
    print(f"status={result['status']}")
    print(f"residual_total={result['counts']['total_residual']}")
    print(f"contract_ready={result['counts']['contract_ready_rows']}")
    print("installed_game_file_written=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
