#!/usr/bin/env python3
"""Build source-free MSG/SC/ev_strdata officer-name batch10 artifacts."""

from __future__ import annotations

import argparse
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import build_ev_strdata_batch4 as engine


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
shared = engine.shared
common = engine.common

BATCH_ID = "ev-strdata-officer-names-1750-1949-v0.10"
OVERLAY_NAME = "ev_strdata_ko_officer_names_1750_1949.v0.10.json"
EVIDENCE_NAME = "alignment_evidence.v0.10.json"
REVIEW_NAME = "review_index.v0.10.json"
VALIDATION_NAME = "validation.v0.10.json"
SCOPE_START = 1750
SCOPE_END = 1949
NEXT_START_ID = 1950
SELECTED_COUNT = SCOPE_END - SCOPE_START + 1

# Every entry in this batch matches the pinned officer-name seed by its exact
# SC UTF-16LE hash. This mapping remains explicit so a future source mismatch
# cannot silently inherit an unrelated translation.
MANUAL_TRANSLATIONS: dict[int, dict[str, str]] = {}

_ENGINE_CONFIGURATION = {
    "SCRIPT_PATH": SCRIPT_PATH,
    "WORKSTREAM_ROOT": WORKSTREAM_ROOT,
    "BATCH_ID": BATCH_ID,
    "OVERLAY_NAME": OVERLAY_NAME,
    "EVIDENCE_NAME": EVIDENCE_NAME,
    "REVIEW_NAME": REVIEW_NAME,
    "VALIDATION_NAME": VALIDATION_NAME,
    "SCOPE_START": SCOPE_START,
    "SCOPE_END": SCOPE_END,
    "NEXT_START_ID": NEXT_START_ID,
    "SELECTED_COUNT": SELECTED_COUNT,
}


def load_translations(sc_table: Any) -> dict[int, str]:
    """Reuse names only on exact SC hashes; require independent pins otherwise."""

    seed_path = REPO_ROOT / shared.SEED_RELATIVE
    seed_blob = seed_path.read_bytes()
    if shared.sha256(seed_blob) != shared.SEED_SHA256:
        raise shared.EvStrDataError("pinned officer-name seed overlay changed")
    seed = shared.load_json(seed_path)
    entries = seed.get("entries")
    if not isinstance(entries, list):
        raise shared.EvStrDataError("seed entries must be an array")
    by_id = {
        int(entry["id"]): entry
        for entry in entries
        if isinstance(entry, dict) and "id" in entry
    }

    translations: dict[int, str] = {}
    manual_used: set[int] = set()
    for entry_id in range(SCOPE_START, SCOPE_END + 1):
        source = sc_table.texts[entry_id]
        if not source.strip():
            raise shared.EvStrDataError(f"selected SC id {entry_id} is not display text")
        source_hash = common.text_hash(source)
        seed_entry = by_id.get(entry_id)
        if (
            seed_entry is not None
            and seed_entry.get("source_sc_utf16le_sha256") == source_hash
        ):
            replacement = seed_entry.get("ko")
        else:
            manual = MANUAL_TRANSLATIONS.get(entry_id)
            if manual is None or manual["source_sc_utf16le_sha256"] != source_hash:
                raise shared.EvStrDataError(
                    f"id {entry_id}: neither exact seed hash nor pinned manual translation matches"
                )
            replacement = manual["ko"]
            manual_used.add(entry_id)
        if not isinstance(replacement, str) or not replacement.strip():
            raise shared.EvStrDataError(f"id {entry_id}: Korean name is empty")
        failures = shared.replacement_failures(source, replacement)
        if failures:
            raise shared.EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
        translations[entry_id] = replacement

    if manual_used != set(MANUAL_TRANSLATIONS):
        raise shared.EvStrDataError(
            f"manual translation coverage mismatch: used={sorted(manual_used)}"
        )
    return translations


_ENGINE_CONFIGURATION["load_translations"] = load_translations


@contextmanager
def configured_engine() -> Iterator[None]:
    """Run the reviewed v0.4 mechanics with only v0.10 batch values changed."""

    original = {name: getattr(engine, name) for name in _ENGINE_CONFIGURATION}
    try:
        for name, value in _ENGINE_CONFIGURATION.items():
            setattr(engine, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(engine, name, value)


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def upgrade_v010_metadata(out_root: Path) -> None:
    """Replace inherited version labels and refresh dependent artifact hashes."""

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    validation_path = out_root / VALIDATION_NAME

    evidence = shared.load_json(evidence_path)
    evidence["schema"] = "nobu16.kr.ev-strdata-alignment-evidence.v10"
    evidence["manual_translation_policy"] = {
        "count": len(MANUAL_TRANSLATIONS),
        "ids_sha256": shared.hash_json(sorted(MANUAL_TRANSLATIONS)),
        "official_source_text_included": False,
        "basis": "SC_JP_TC_aligned_name_review_with_exact_SC_hash_pins",
    }
    for entry in evidence["entries"]:
        entry_id = int(entry["id"])
        is_manual = entry_id in MANUAL_TRANSLATIONS
        entry["translation_reuse_exact_sc_hash_match"] = not is_manual
        if is_manual:
            entry["manual_translation_hash_pinned"] = True
    evidence_path.write_bytes(shared.encode_json(evidence))

    review = shared.load_json(review_path)
    review["schema"] = "nobu16.kr.ev-strdata-review-index.v10"
    for entry in review["entries"]:
        if int(entry["id"]) in MANUAL_TRANSLATIONS:
            entry["translation_origin"] = "manual_sc_jp_tc_alignment_exact_sc_hash_pin"
    review_path.write_bytes(shared.encode_json(review))

    validation = shared.load_json(validation_path)
    validation["schema"] = "nobu16.kr.ev-strdata-generation-validation.v10"
    safety = validation["safety"]
    safety.pop("existing_v01_v02_v03_artifacts_modified", None)
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_artifacts_modified"
    ] = False
    validation["translation_reuse"]["exact_sc_hash_matches"] = (
        SELECTED_COUNT - len(MANUAL_TRANSLATIONS)
    )
    validation["translation_reuse"]["mismatches"] = len(MANUAL_TRANSLATIONS)
    validation["manual_translation"] = {
        "count": len(MANUAL_TRANSLATIONS),
        "ids_sha256": shared.hash_json(sorted(MANUAL_TRANSLATIONS)),
        "source_text_embedded": False,
        "sc_hash_pins_checked": len(MANUAL_TRANSLATIONS),
        "sc_jp_tc_alignment_reviewed": len(MANUAL_TRANSLATIONS),
    }
    validation["artifacts"] = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation_path.write_bytes(shared.encode_json(validation))

    public_paths = (overlay_path, evidence_path, review_path, validation_path)
    if any(
        shared.source_free_counts(path.read_bytes())
        != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for path in public_paths
    ):
        raise shared.EvStrDataError(
            "v0.10 public artifact contains source script text or an embedded NUL"
        )


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    with configured_engine():
        result = engine.build_once(game_root, out_root)
    upgrade_v010_metadata(out_root)
    return {
        "entry_count": result["entry_count"],
        "next_start_id": result["next_start_id"],
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [
        game_root / "MSG" / language / "ev_strdata.bin"
        for language in shared.LANGUAGES
    ]
    before = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr10-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr10-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError("final public artifacts differ from isolated A/B output")
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError(
            "installed game resource changed across reproducible build"
        )
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"entries={result['entry_count']}")
    print(f"next_start_id={result['next_start_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
