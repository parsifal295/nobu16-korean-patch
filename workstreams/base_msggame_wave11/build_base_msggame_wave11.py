#!/usr/bin/env python3
"""Build and verify the safe Wave 11 residual overlay for base JP msggame.

The prior Switch-v1.3 transfer deliberately stopped before rows whose Korean
target contained a middle-dot punctuation mark, source-edge whitespace, or a
format-percent difference.  This workstream consumes only the source-free
contracts from the Wave 10 inventory and re-derives the Korean target from the
pinned Switch v1.3 asset.  Three Hanja-gloss rows and 59 nonsemantic format
tokens remain explicitly deferred.

No command here writes a Steam resource, the v5 candidate, a release archive,
or a complete game binary.  ``generate`` writes only source-free JSON metadata
and Korean overlay text beneath this workstream; ``verify`` is read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PRIOR_BUILDER = (
    REPO
    / "workstreams"
    / "tutorial_dialogue_trace_msggame_v1"
    / "build_base_msggame_switch_v13_overlay.py"
)
INVENTORY_PATH = (
    REPO
    / "workstreams"
    / "base_jp_residual_wave10_inventory"
    / "public"
    / "base_jp_residual_wave10_inventory.v1.json"
)
CONTRACTS_PATH = (
    REPO
    / "workstreams"
    / "base_jp_residual_wave10_inventory"
    / "public"
    / "base_jp_residual_wave10_contracts.v1.json"
)

PUBLIC = HERE / "public"
OVERLAY_PATH = PUBLIC / "msggame_ko_base_jp_wave11_safe_270.v1.json"
DEFERRED_PATH = PUBLIC / "msggame_ko_base_jp_wave11_deferred_62.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"

# The live Steam root is intentionally not the default: it currently contains
# the v0.8.0 test candidate.  This transaction backup is the pinned stock JP
# input that was captured before that application.  Callers may supply another
# known-stock root with --stock-root.
DEFAULT_STOCK_ROOT = Path(
    r"F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/"
    r"file_only_transaction/steam-jp-1.1.7-v0.8.0/originals"
)
DEFAULT_SWITCH_ZIP = (
    REPO / "tmp" / "third_party_switch_v13" / "NobunagaShinsei_KoreanPatch_v1.3.zip"
)

RESOURCE = "MSG/JP/msggame.bin"
OVERLAY_SCHEMA = "nobu16.kr.base-msggame-jp-wave11-safe-overlay.v1"
DEFERRED_SCHEMA = "nobu16.kr.base-msggame-jp-wave11-deferred.v1"
VALIDATION_SCHEMA = "nobu16.kr.base-msggame-jp-wave11-validation.v1"

EXPECTED = {
    "residual_rows": 332,
    "prior_switch_v13_entries": 22_924,
    "safe_contract_entries": 270,
    "manual_hanja_gloss_entries": 3,
    "nonsemantic_format_token_entries": 59,
    "combined_changed_entries": 23_194,
}
EXPECTED_CANDIDATE = {
    "packed_size": 649_347,
    "packed_sha256": "E54D7AB55CB981B7973FBF8657A276520EBFA881D3439BE94A2D14086B293177",
    "raw_size": 1_498_276,
    "raw_sha256": "183F7867817FBDAAE8E8B1DE547AEAC9B80C6A818604DD26FBF57BABD2FC10E2",
}

SAFE_TRANSFORMS = {
    "switch_v13_exact",
    "switch_v13_match_source_edge_whitespace",
    "switch_v13_ascii_percent_to_fullwidth",
}

# U+30FB (middle dot) is punctuation rather than a lexical Japanese source
# character for this contract.  It is deliberately allowed in public Korean
# text and checked separately by the Wave 10 inventory.
CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_LETTER_RE = re.compile(
    r"[\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FD-\u30FF\u31F0-\u31FF]"
)


class Wave11Error(ValueError):
    """Raised when a pinned input, contract, or source-free artifact diverges."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def strict_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Wave11Error(f"invalid UTF-8 JSON: {path}") from exc
    if not isinstance(value, dict):
        raise Wave11Error(f"JSON root is not an object: {path}")
    return value, blob


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave11Error(f"cannot import prerequisite builder: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def coordinates(entries: Iterable[dict[str, Any]]) -> list[tuple[int, int, int]]:
    result = [
        (int(row["block_id"]), int(row["record_id"]), int(row["literal_id"]))
        for row in entries
    ]
    if len(result) != len(set(result)):
        raise Wave11Error("duplicate literal coordinate")
    return sorted(result)


def coordinate_sha256(values: Iterable[tuple[int, int, int]]) -> str:
    return sha256(
        "".join(f"{block}:{record}:{literal}\n" for block, record, literal in sorted(values)).encode(
            "ascii"
        )
    )


def has_lexical_source_script(text: str) -> bool:
    return CJK_RE.search(text) is not None or KANA_LETTER_RE.search(text) is not None


def assert_source_free(value: Any, label: str) -> None:
    """Reject commercial JP script while allowing Korean and neutral punctuation."""
    encoded = canonical_json_bytes(value).decode("utf-8")
    if has_lexical_source_script(encoded):
        raise Wave11Error(f"source script leaked into public artifact: {label}")


def edge_normalized(source: str, korean: str) -> str:
    leading = source[: len(source) - len(source.lstrip())]
    trailing = source[len(source.rstrip()) :]
    return leading + korean.strip() + trailing


def load_inventory_partition() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return safe, manual, and nonsemantic base-msggame residual rows."""
    inventory, _blob = strict_json(INVENTORY_PATH)
    rows = inventory.get("entries")
    if not isinstance(rows, list):
        raise Wave11Error("Wave 10 inventory entries are missing")
    selected = [row for row in rows if row.get("resource") == RESOURCE]
    if len(selected) != EXPECTED["residual_rows"]:
        raise Wave11Error(f"base msggame residual count differs: {len(selected)}")

    safe = [row for row in selected if row.get("action") == "contract_ready"]
    manual = [row for row in selected if row.get("action") == "manual_terminology_review"]
    tokens = [row for row in selected if row.get("action") == "retain_as_nonsemantic_token"]
    if (
        len(safe) != EXPECTED["safe_contract_entries"]
        or len(manual) != EXPECTED["manual_hanja_gloss_entries"]
        or len(tokens) != EXPECTED["nonsemantic_format_token_entries"]
        or len(safe) + len(manual) + len(tokens) != len(selected)
    ):
        raise Wave11Error("Wave 10 base-msggame residual partition differs")
    for row in safe:
        if row.get("transform") not in SAFE_TRANSFORMS:
            raise Wave11Error("unexpected safe transform")
        if not isinstance(row.get("planned_ko_utf16le_sha256"), str):
            raise Wave11Error("safe row has no planned Korean hash")
    return (
        sorted(safe, key=lambda row: (row["block_id"], row["record_id"], row["literal_id"])),
        sorted(manual, key=lambda row: (row["block_id"], row["record_id"], row["literal_id"])),
        sorted(tokens, key=lambda row: (row["block_id"], row["record_id"], row["literal_id"])),
    )


def load_safe_contracts(safe_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contracts, _blob = strict_json(CONTRACTS_PATH)
    entries = contracts.get("entries")
    if not isinstance(entries, list):
        raise Wave11Error("Wave 10 contracts are missing")
    selected = [row for row in entries if row.get("resource") == RESOURCE]
    if len(selected) != EXPECTED["safe_contract_entries"]:
        raise Wave11Error(f"base msggame contract count differs: {len(selected)}")
    result = sorted(
        selected,
        key=lambda row: (row["block_id"], row["record_id"], row["literal_id"]),
    )
    if coordinates(result) != coordinates(safe_rows):
        raise Wave11Error("Wave 10 contract and inventory coordinate domains differ")
    for contract, row in zip(result, safe_rows, strict=True):
        if (
            contract.get("source_jp_utf16le_sha256") != row.get("source_jp_utf16le_sha256")
            or contract.get("planned_ko_utf16le_sha256")
            != row.get("planned_ko_utf16le_sha256")
            or contract.get("transform") != row.get("transform")
        ):
            raise Wave11Error("Wave 10 contract content differs from inventory")
    return result


def target_for_contract(base_module: Any, source: str, switch_target: str, transform: str) -> str:
    if transform == "switch_v13_exact":
        return switch_target
    if transform == "switch_v13_match_source_edge_whitespace":
        return edge_normalized(source, switch_target)
    if transform == "switch_v13_ascii_percent_to_fullwidth":
        result = switch_target.replace("%", "％")
        if result == switch_target:
            raise Wave11Error("percent-normalization contract no longer changes the target")
        return result
    raise Wave11Error(f"unsupported transform: {transform}")


def expected_overlay(
    base_module: Any,
    base: dict[str, Any],
    switch: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    safe_rows, manual_rows, token_rows = load_inventory_partition()
    contracts = load_safe_contracts(safe_rows)
    entries: list[dict[str, Any]] = []
    for contract in contracts:
        coordinate = (
            int(contract["block_id"]),
            int(contract["record_id"]),
            int(contract["literal_id"]),
        )
        if coordinate not in base["literals"] or coordinate not in switch["literals"]:
            raise Wave11Error(f"contract coordinate is absent from a pinned table: {coordinate}")
        source = base["literals"][coordinate].text
        switch_target = switch["literals"][coordinate].text
        target = target_for_contract(base_module, source, switch_target, str(contract["transform"]))
        if base_module.text_hash(source) != contract["source_jp_utf16le_sha256"]:
            raise Wave11Error(f"source pin differs at {coordinate}")
        if base_module.text_hash(target) != contract["planned_ko_utf16le_sha256"]:
            raise Wave11Error(f"Korean contract pin differs at {coordinate}")
        if base_module.HANGUL_RE.search(target) is None:
            raise Wave11Error(f"Korean target is absent at {coordinate}")
        if has_lexical_source_script(target):
            raise Wave11Error(f"lexical source script remains at {coordinate}")
        if base_module.common.invariant_mismatches(source, target):
            raise Wave11Error(f"format invariant differs at {coordinate}")
        entries.append(
            {
                "block_id": coordinate[0],
                "record_id": coordinate[1],
                "literal_id": coordinate[2],
                "source_jp_utf16le_sha256": contract["source_jp_utf16le_sha256"],
                "ko": target,
                "ko_utf16le_sha256": contract["planned_ko_utf16le_sha256"],
                "transform": contract["transform"],
            }
        )

    if len(entries) != EXPECTED["safe_contract_entries"]:
        raise Wave11Error("safe overlay size differs")
    if coordinates(entries) != coordinates(contracts):
        raise Wave11Error("safe overlay coordinate domain differs")
    contract_sha = sha256(canonical_json_bytes(contracts))
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msggame_ko_base_jp_wave11_safe_270.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "runtime": {"distribution": "Steam", "version": "1.1.7"},
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "source_free": True,
        },
        "predecessor": {
            "workstream": "tutorial_dialogue_trace_msggame_v1",
            "switch_v13_exact_entries": EXPECTED["prior_switch_v13_entries"],
        },
        "contract_source": {
            "workstream": "base_jp_residual_wave10_inventory",
            "safe_contract_entries": len(contracts),
            "entries_canonical_sha256": contract_sha,
        },
        "selection": {
            "coordinate_exact": True,
            "requires_hangul": True,
            "lexical_cjk_or_kana_rejected": True,
            "format_invariants_required": True,
            "allowed_transforms": sorted(SAFE_TRANSFORMS),
        },
        "entry_count": len(entries),
        "entry_coordinate_sha256": coordinate_sha256(coordinates(entries)),
        "entries": entries,
    }
    assert_source_free(overlay, "safe overlay")
    return overlay, manual_rows, token_rows


def expected_deferred(
    manual_rows: list[dict[str, Any]], token_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    manual_entries = [
        {
            "block_id": int(row["block_id"]),
            "record_id": int(row["record_id"]),
            "literal_id": int(row["literal_id"]),
            "source_jp_utf16le_sha256": row["source_jp_utf16le_sha256"],
            "switch_ko_utf16le_sha256": row["switch_ko_utf16le_sha256"],
            "status": "pending_manual_korean_term_review",
            "reason": "switch_target_contains_hanja_gloss",
            "required_policy": "retain_korean_term_without_hanja_parenthetical",
        }
        for row in manual_rows
    ]
    token_entries = [
        {
            "block_id": int(row["block_id"]),
            "record_id": int(row["record_id"]),
            "literal_id": int(row["literal_id"]),
            "source_jp_utf16le_sha256": row["source_jp_utf16le_sha256"],
            "status": "retain_nonsemantic_format_token",
        }
        for row in token_rows
    ]
    if (
        len(manual_entries) != EXPECTED["manual_hanja_gloss_entries"]
        or len(token_entries) != EXPECTED["nonsemantic_format_token_entries"]
    ):
        raise Wave11Error("deferred partition size differs")
    value = {
        "schema": DEFERRED_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "source_free": True,
        },
        "summary": {
            "safe_overlay_entries": EXPECTED["safe_contract_entries"],
            "manual_hanja_gloss_entries": len(manual_entries),
            "nonsemantic_format_token_entries": len(token_entries),
            "deferred_total": len(manual_entries) + len(token_entries),
        },
        "manual_hanja_gloss_entries": manual_entries,
        "nonsemantic_format_token_entries": token_entries,
    }
    assert_source_free(value, "deferred report")
    return value


def load_overlay(
    base_module: Any, base: dict[str, Any], switch: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], bytes]:
    expected, manual_rows, token_rows = expected_overlay(base_module, base, switch)
    value, blob = strict_json(OVERLAY_PATH)
    if value != expected:
        raise Wave11Error("tracked Wave 11 overlay differs from pinned model")
    assert_source_free(value, "tracked safe overlay")
    return value, manual_rows, token_rows, blob


def load_deferred(
    manual_rows: list[dict[str, Any]], token_rows: list[dict[str, Any]]
) -> tuple[dict[str, Any], bytes]:
    expected = expected_deferred(manual_rows, token_rows)
    value, blob = strict_json(DEFERRED_PATH)
    if value != expected:
        raise Wave11Error("tracked Wave 11 deferred report differs from pinned model")
    assert_source_free(value, "tracked deferred report")
    return value, blob


def prior_replacements(base_module: Any, base: dict[str, Any], switch: dict[str, Any]) -> dict[tuple[int, int, int], str]:
    prior, _blob = base_module.load_overlay(base, switch)
    replacements: dict[tuple[int, int, int], str] = {}
    for row in prior["entries"]:
        coordinate = (int(row["block_id"]), int(row["record_id"]), int(row["literal_id"]))
        if coordinate in replacements or coordinate not in base["literals"]:
            raise Wave11Error(f"invalid prior coordinate: {coordinate}")
        source = base["literals"][coordinate].text
        target = str(row["ko"])
        if (
            base_module.text_hash(source) != row["source_jp_utf16le_sha256"]
            or base_module.text_hash(target) != row["ko_utf16le_sha256"]
            or base_module.common.invariant_mismatches(source, target)
        ):
            raise Wave11Error(f"prior transfer invariant differs at {coordinate}")
        replacements[coordinate] = target
    if len(replacements) != EXPECTED["prior_switch_v13_entries"]:
        raise Wave11Error("prior transfer entry count differs")
    return replacements


def build_blob(
    stock_root: Path = DEFAULT_STOCK_ROOT,
    switch_zip: Path | None = None,
) -> tuple[bytes, dict[str, Any]]:
    """Build the combined 22,924 + 270 candidate in memory only."""
    base_module = load_module("base_msggame_wave11_prior", PRIOR_BUILDER)
    if switch_zip is None:
        switch_zip = base_module.DEFAULT_SWITCH_ZIP
    base = base_module.load_base(stock_root)
    switch = base_module.load_switch(switch_zip)
    overlay, manual_rows, token_rows, overlay_blob = load_overlay(base_module, base, switch)
    deferred, deferred_blob = load_deferred(manual_rows, token_rows)
    replacements = prior_replacements(base_module, base, switch)
    prior_coordinates = set(replacements)

    for row in overlay["entries"]:
        coordinate = (int(row["block_id"]), int(row["record_id"]), int(row["literal_id"]))
        if coordinate in replacements or coordinate not in base["literals"]:
            raise Wave11Error(f"wave overlay collision or absent coordinate: {coordinate}")
        source = base["literals"][coordinate].text
        target = str(row["ko"])
        if (
            base_module.text_hash(source) != row["source_jp_utf16le_sha256"]
            or base_module.text_hash(target) != row["ko_utf16le_sha256"]
            or base_module.common.invariant_mismatches(source, target)
            or has_lexical_source_script(target)
        ):
            raise Wave11Error(f"wave transfer invariant differs at {coordinate}")
        replacements[coordinate] = target

    wave_coordinates = coordinates(overlay["entries"])
    if len(prior_coordinates & set(wave_coordinates)):
        raise Wave11Error("Wave 11 overlaps the prior exact transfer")
    if len(replacements) != EXPECTED["combined_changed_entries"]:
        raise Wave11Error("combined transfer entry count differs")

    raw = base_module.msggame.rebuild_raw_with_literals(base["archive"], replacements)
    candidate = base_module.recompress_wrapper_greedy(raw, base["header"])
    _header, roundtrip = base_module.decompress_wrapper(candidate)
    if roundtrip != raw or candidate[:8] != base["packed"][:8]:
        raise Wave11Error("candidate wrapper round-trip differs")
    parsed = base_module.msggame.parse_packed_msggame(candidate)
    candidate_literals = base_module.literal_map(parsed.archive)
    if set(candidate_literals) != set(base["literals"]):
        raise Wave11Error("candidate literal coordinate set differs")
    changed = {
        coordinate
        for coordinate in base["literals"]
        if base["literals"][coordinate].text != candidate_literals[coordinate].text
    }
    if changed != set(replacements):
        raise Wave11Error("candidate changed a non-selected literal")
    if any(candidate_literals[key].text != value for key, value in replacements.items()):
        raise Wave11Error("candidate literal differs from an overlay")
    normalized_base = base_module.normalized_structure_raw(base["archive"])
    normalized_candidate = base_module.normalized_structure_raw(parsed.archive)
    if normalized_base != normalized_candidate:
        raise Wave11Error("candidate changed opaque bytecode or structure")

    candidate_spec = {
        "packed_size": len(candidate),
        "packed_sha256": sha256(candidate),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
    }
    metrics = {
        "resource": RESOURCE,
        "stock": dict(base_module.BASE_PIN),
        "candidate": candidate_spec,
        # Candidate assemblers consume an explicit, unambiguous transfer
        # count.  Keep it alongside the detailed Wave 11 breakdown so this
        # module can be composed without re-deriving or guessing its scope.
        "entry_count": len(replacements),
        "prior_switch_v13_entries": len(prior_coordinates),
        "wave11_safe_entries": len(wave_coordinates),
        "manual_hanja_gloss_deferred": len(deferred["manual_hanja_gloss_entries"]),
        "nonsemantic_format_token_retained": len(deferred["nonsemantic_format_token_entries"]),
        "combined_changed_entries": len(replacements),
        "wave11_entry_coordinate_sha256": overlay["entry_coordinate_sha256"],
        "wave11_overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "deferred_report": {"size": len(deferred_blob), "sha256": sha256(deferred_blob)},
        "normalized_structure_sha256": sha256(normalized_base),
        "non_selected_literals_preserved": True,
        "wrapper_header_preserved": True,
        "candidate_written": False,
        "steam_file_written": False,
    }
    return candidate, metrics


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "resource": RESOURCE,
        "runtime": {"distribution": "Steam", "version": "1.1.7"},
        "translation": {
            "prior_switch_v13_exact_entries": metrics["prior_switch_v13_entries"],
            "wave11_safe_contract_entries": metrics["wave11_safe_entries"],
            "manual_hanja_gloss_deferred": metrics["manual_hanja_gloss_deferred"],
            "nonsemantic_format_token_retained": metrics["nonsemantic_format_token_retained"],
            "combined_changed_entries": metrics["combined_changed_entries"],
        },
        "expected": {"stock": metrics["stock"], "candidate": metrics["candidate"]},
        "proofs": {
            "wave11_entry_coordinate_sha256": metrics["wave11_entry_coordinate_sha256"],
            "wave11_overlay": metrics["wave11_overlay"],
            "deferred_report": metrics["deferred_report"],
            "normalized_structure_sha256": metrics["normalized_structure_sha256"],
            "non_selected_literals_preserved": metrics["non_selected_literals_preserved"],
            "wrapper_header_preserved": metrics["wrapper_header_preserved"],
            "deterministic_ab_equal": True,
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "candidate_written": metrics["candidate_written"],
            "installed_game_files_modified": metrics["steam_file_written"],
            "sc_binary_used": False,
            "source_text_embedded": False,
        },
    }


def generate(stock_root: Path = DEFAULT_STOCK_ROOT, switch_zip: Path | None = None) -> dict[str, Any]:
    """Generate only source-free workstream artifacts from pinned local inputs."""
    base_module = load_module("base_msggame_wave11_generate_prior", PRIOR_BUILDER)
    if switch_zip is None:
        switch_zip = base_module.DEFAULT_SWITCH_ZIP
    base = base_module.load_base(stock_root)
    switch = base_module.load_switch(switch_zip)
    overlay, manual_rows, token_rows = expected_overlay(base_module, base, switch)
    deferred = expected_deferred(manual_rows, token_rows)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    OVERLAY_PATH.write_bytes(canonical_json_bytes(overlay))
    DEFERRED_PATH.write_bytes(canonical_json_bytes(deferred))
    first, metrics = build_blob(stock_root, switch_zip)
    second, second_metrics = build_blob(stock_root, switch_zip)
    if first != second or metrics != second_metrics:
        raise Wave11Error("deterministic A/B candidate differs")
    VALIDATION_PATH.write_bytes(canonical_json_bytes(validation_model(metrics)))
    return {"status": "GENERATED", **metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path = DEFAULT_STOCK_ROOT, switch_zip: Path | None = None) -> dict[str, Any]:
    """Read-only verification of the tracked Wave 11 source-free artifacts."""
    first, metrics = build_blob(stock_root, switch_zip)
    second, second_metrics = build_blob(stock_root, switch_zip)
    if first != second or metrics != second_metrics:
        raise Wave11Error("deterministic A/B candidate differs")
    validation, _blob = strict_json(VALIDATION_PATH)
    if validation != validation_model(metrics):
        raise Wave11Error("tracked validation differs from pinned model")
    assert_source_free(validation, "validation")
    return {"status": "PASS", **metrics, "deterministic_ab_equal": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "verify"))
    parser.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
    parser.add_argument("--switch-zip", type=Path, default=None)
    args = parser.parse_args()
    result = (
        generate(args.stock_root, args.switch_zip)
        if args.command == "generate"
        else verify(args.stock_root, args.switch_zip)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
