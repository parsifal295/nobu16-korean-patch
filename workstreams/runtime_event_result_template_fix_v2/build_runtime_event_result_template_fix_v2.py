#!/usr/bin/env python3
"""Build the source-free Base/PK event-result template correction."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

from build_common_message_overlay import invariant_mismatches  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


OVERLAY_PATH = WORKSTREAM_ROOT / "public" / "runtime_event_result_template_fix.v2.json"
EVIDENCE_PATH = WORKSTREAM_ROOT / "evidence" / "screenshot_mapping.source-free.v2.json"
DEFAULT_INPUT_ROOT = REPO_ROOT / "tmp" / "v090_dialogue_runtime_final_integration_v6" / "target"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tmp" / "runtime_event_result_template_fix_v2" / "candidate"

BASE_CHANGED_IDS = [
    17302, 17303, 17308, 17316, 17319, 17321, 17339, 17340,
    17344, 17345, 17346, 17347, 17350, 17351, 17378, 17410,
    17464, 17478, 17482, 17626, 17627, 17645, 17663, 17664,
    17668, 17670, 17671, 17674,
]
PK_CHANGED_IDS = [
    17344, 17345, 17350, 17358, 17361, 17363, 17381, 17382,
    17386, 17387, 17388, 17389, 17392, 17393, 17420, 17452,
    17508, 17522, 17526, 17672, 17673, 17691, 17709, 17710,
    17714, 17716, 17717, 17720,
]

RESOURCE_PINS: dict[str, dict[str, Any]] = {
    "MSG/JP/ev_strdata.bin": {
        "input": {
            "packed_size": 928135,
            "packed_sha256": "B8A50B3933FBC0A6A51D0B85AB8D3B4A77EC234CAA65C0FA3DB4B1EEC1604DC1",
            "raw_size": 924484,
            "raw_sha256": "0B14B96140BE4FC390A609EEBD2BDA9F2749B848311D292DBFD031527CE56E06",
            "string_count": 17868,
        },
        "output": {
            "packed_size": 928123,
            "packed_sha256": "17A61E7F9B6BBFE4FC6C944D0C9A51D6B45DE201A30130AB4FF445DFE99B5172",
            "raw_size": 924472,
            "raw_sha256": "5DEFBC2A7B4B34F36989DEEE7C40B49CC34E9421CF46F0AEB8986E9507FBB3E2",
            "string_count": 17868,
        },
        "changed_ids": BASE_CHANGED_IDS,
    },
    "MSG_PK/JP/msgev.bin": {
        "input": {
            "packed_size": 1048324,
            "packed_sha256": "27E2EB977A4D11C82B4A096DE1F8D6F4C1D4F0FF0DEF323DBDCADFE35FE07197",
            "raw_size": 1044204,
            "raw_sha256": "0854F8656247460BC9236BB414AE615978901E5DB51026500436D1615DCDEC05",
            "string_count": 17916,
        },
        "output": {
            "packed_size": 1048312,
            "packed_sha256": "3461C647D113CF424E791D2D694AADFADEA45F38873A110810558DE0E09C50C8",
            "raw_size": 1044192,
            "raw_sha256": "010880E1E1CC58645224469A28CE0557205B0670A9A3D426B04F5A90B65DBCF2",
            "string_count": 17916,
        },
        "changed_ids": PK_CHANGED_IDS,
    },
}


class BuildError(RuntimeError):
    """Raised when a pinned resource or overlay contract is violated."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def file_state(packed: bytes, raw: bytes, string_count: int) -> dict[str, Any]:
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "string_count": string_count,
    }


def validate_overlay(overlay: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    expected_root_keys = {"schema", "overlay_id", "distribution_policy", "entries"}
    if set(overlay) != expected_root_keys:
        raise BuildError("overlay root keys changed")
    if overlay["schema"] != "nobu16.kr.runtime-event-result-template-overlay.v2":
        raise BuildError("unsupported overlay schema")
    if overlay["overlay_id"] != "runtime_event_result_template_fix_v2":
        raise BuildError("overlay id changed")
    if any(overlay["distribution_policy"].values()):
        raise BuildError("overlay distribution policy must remain source-free")

    grouped = {resource: [] for resource in RESOURCE_PINS}
    seen: set[tuple[str, int]] = set()
    for entry in overlay["entries"]:
        if set(entry) != {
            "resource",
            "id",
            "source_utf16le_sha256",
            "ko",
            "allow_edge_whitespace_change",
        }:
            raise BuildError("overlay entry keys changed")
        resource = entry["resource"]
        key = (resource, entry["id"])
        if resource not in grouped or key in seen:
            raise BuildError(f"invalid or duplicate overlay entry: {key}")
        if not isinstance(entry["ko"], str) or not entry["ko"] or "\x00" in entry["ko"]:
            raise BuildError(f"invalid replacement text: {key}")
        seen.add(key)
        grouped[resource].append(entry)

    expected = {
        (resource, entry_id)
        for resource, pins in RESOURCE_PINS.items()
        for entry_id in pins["changed_ids"]
    }
    if seen != expected:
        raise BuildError(f"overlay scope changed: expected={sorted(expected)}, actual={sorted(seen)}")
    for entries in grouped.values():
        entries.sort(key=lambda entry: entry["id"])
    return grouped


def build_resource(
    source: Path,
    destination: Path,
    resource: str,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    packed = source.read_bytes()
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    pins = RESOURCE_PINS[resource]
    before_state = file_state(packed, raw, table.string_count)
    if before_state != pins["input"]:
        raise BuildError(f"{resource}: input pin mismatch: {before_state}")
    if recompress_wrapper(raw, header) != packed:
        raise BuildError(f"{resource}: input is not the pinned literal-only wrapper form")

    texts = list(table.texts)
    row_audit: list[dict[str, Any]] = []
    for entry in entries:
        entry_id = entry["id"]
        source_text = table.texts[entry_id]
        if text_hash(source_text) != entry["source_utf16le_sha256"]:
            raise BuildError(f"{resource} id {entry_id}: source row hash mismatch")
        mismatches = invariant_mismatches(
            source_text,
            entry["ko"],
            allow_edge_whitespace_change=entry["allow_edge_whitespace_change"],
        )
        if mismatches:
            raise BuildError(f"{resource} id {entry_id}: invariant mismatch: {mismatches}")
        texts[entry_id] = entry["ko"]
        row_audit.append(
            {
                "id": entry_id,
                "source_utf16le_sha256": entry["source_utf16le_sha256"],
                "output_utf16le_sha256": text_hash(entry["ko"]),
                "allow_edge_whitespace_change": entry["allow_edge_whitespace_change"],
            }
        )

    rebuilt_raw = rebuild_message_table(table, texts)
    rebuilt_table = parse_message_table(rebuilt_raw)
    changed_ids = [
        entry_id
        for entry_id, (before, after) in enumerate(zip(table.texts, rebuilt_table.texts))
        if before != after
    ]
    if changed_ids != pins["changed_ids"]:
        raise BuildError(f"{resource}: changed ID set mismatch: {changed_ids}")

    rebuilt_packed = recompress_wrapper(rebuilt_raw, header)
    after_state = file_state(rebuilt_packed, rebuilt_raw, rebuilt_table.string_count)
    if after_state != pins["output"]:
        raise BuildError(f"{resource}: output pin mismatch: {after_state}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(rebuilt_packed)
    return {
        "resource": resource,
        "input": before_state,
        "output": after_state,
        "changed_ids": changed_ids,
        "rows": row_audit,
    }


def build(input_root: Path, output_root: Path) -> dict[str, Any]:
    input_root = input_root.resolve()
    output_root = output_root.resolve()
    if input_root == output_root:
        raise BuildError("output root must differ from input root")
    if output_root.exists():
        raise BuildError(f"refusing to replace existing output root: {output_root}")
    for resource in RESOURCE_PINS:
        source = (input_root / resource).resolve()
        if not source.is_file() or input_root not in source.parents:
            raise BuildError(f"missing or escaped input resource: {resource}")

    overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    grouped = validate_overlay(overlay)
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    if evidence["distribution_policy"]["contains_commercial_source_text"]:
        raise BuildError("screenshot mapping must remain source-free")

    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage_parent = Path(tempfile.mkdtemp(prefix="runtime-event-result-", dir=output_root.parent))
    stage_root = stage_parent / "candidate"
    stage_root.mkdir()
    try:
        resources = [
            build_resource(input_root / resource, stage_root / resource, resource, grouped[resource])
            for resource in RESOURCE_PINS
        ]
        manifest = {
            "schema": "nobu16.kr.runtime-event-result-template-build.v2",
            "overlay_sha256": sha256_bytes(OVERLAY_PATH.read_bytes()),
            "evidence_sha256": sha256_bytes(EVIDENCE_PATH.read_bytes()),
            "resources": resources,
            "expected_runtime_examples": evidence["expected_runtime_examples"],
            "steam_write_performed": False,
            "passed": True,
        }
        (stage_root / "validation.v2.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        stage_root.replace(output_root)
        return manifest
    finally:
        if stage_parent.exists():
            shutil.rmtree(stage_parent)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build(args.input_root, args.output_root)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
