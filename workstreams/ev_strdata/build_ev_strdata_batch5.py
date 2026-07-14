#!/usr/bin/env python3
"""Build source-free MSG/SC/ev_strdata officer-name batch5 artifacts."""

from __future__ import annotations

import argparse
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import build_ev_strdata_batch4 as previous


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
shared = previous.shared

BATCH_ID = "ev-strdata-officer-names-0750-0949-v0.5"
OVERLAY_NAME = "ev_strdata_ko_officer_names_0750_0949.v0.5.json"
EVIDENCE_NAME = "alignment_evidence.v0.5.json"
REVIEW_NAME = "review_index.v0.5.json"
VALIDATION_NAME = "validation.v0.5.json"
SCOPE_START = 750
SCOPE_END = 949
NEXT_START_ID = 950
SELECTED_COUNT = SCOPE_END - SCOPE_START + 1

_PREVIOUS_CONFIGURATION = {
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


@contextmanager
def configured_previous_builder() -> Iterator[None]:
    """Run the reviewed v0.4 mechanics with only v0.5 batch constants changed."""

    original = {
        name: getattr(previous, name) for name in _PREVIOUS_CONFIGURATION
    }
    try:
        for name, value in _PREVIOUS_CONFIGURATION.items():
            setattr(previous, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(previous, name, value)


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def upgrade_v05_metadata(out_root: Path) -> None:
    """Replace inherited version labels and refresh dependent artifact hashes."""

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    validation_path = out_root / VALIDATION_NAME

    evidence = shared.load_json(evidence_path)
    evidence["schema"] = "nobu16.kr.ev-strdata-alignment-evidence.v5"
    evidence_path.write_bytes(shared.encode_json(evidence))

    review = shared.load_json(review_path)
    review["schema"] = "nobu16.kr.ev-strdata-review-index.v5"
    review_path.write_bytes(shared.encode_json(review))

    validation = shared.load_json(validation_path)
    validation["schema"] = "nobu16.kr.ev-strdata-generation-validation.v5"
    safety = validation["safety"]
    safety.pop("existing_v01_v02_v03_artifacts_modified", None)
    safety["existing_v01_v02_v03_v04_artifacts_modified"] = False
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
            "v0.5 public artifact contains source script text or an embedded NUL"
        )


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    with configured_previous_builder():
        result = previous.build_once(game_root, out_root)
    upgrade_v05_metadata(out_root)
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
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr5-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr5-b-") as second_tmp:
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
