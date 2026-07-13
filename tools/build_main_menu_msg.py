#!/usr/bin/env python3
"""Build the Korean main-menu msgui resource without touching installed files.

The compact translation catalog carries both the expected stock SHA-256 and
the exact source string for every changed id.  A build is refused if either
check fails.  The output is a normal on-disk resource file; this tool performs
no process-memory access, injection, hooking, or executable modification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from nobu16_lz4 import decompress_wrapper, recompress_wrapper
from nobu16_msg_table import parse_message_table, rebuild_message_table


LANGUAGES = ("EN", "JP", "SC", "TC")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--language", choices=LANGUAGES, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    if catalog.get("schema") != "nobu16.kr.translation.v1":
        raise ValueError("unsupported translation catalog schema")
    language = args.language
    source_spec = catalog["source_files"][language]
    source_path = args.game_root / Path(source_spec["path"])
    source_blob = source_path.read_bytes()
    source_hash = sha256(source_blob)
    expected_hash = str(source_spec["sha256"]).upper()
    if source_hash != expected_hash:
        raise ValueError(
            f"stock hash mismatch for {source_path}: {source_hash}, expected {expected_hash}"
        )

    _, raw = decompress_wrapper(source_blob)
    table = parse_message_table(raw)
    texts = list(table.texts)
    changed: list[dict[str, object]] = []
    seen_ids: set[int] = set()
    for entry in catalog["entries"]:
        entry_id = int(entry["id"])
        if entry_id in seen_ids:
            raise ValueError(f"duplicate translation id {entry_id}")
        seen_ids.add(entry_id)
        if not 0 <= entry_id < table.string_count:
            raise ValueError(f"translation id {entry_id} is outside msgui")
        expected_source = entry["source"][language]
        actual_source = texts[entry_id]
        if actual_source != expected_source:
            raise ValueError(
                f"id {entry_id} source mismatch: {actual_source!r}, expected {expected_source!r}"
            )
        korean = entry["ko"]
        if not isinstance(korean, str) or not korean or "\x00" in korean:
            raise ValueError(f"id {entry_id} has an invalid Korean translation")
        texts[entry_id] = korean
        changed.append({"id": entry_id, "source": actual_source, "ko": korean})

    rebuilt_raw = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if tuple(texts) != reparsed.texts:
        raise RuntimeError("rebuilt msgui parse verification failed")
    output_blob = recompress_wrapper(rebuilt_raw, source_blob)
    _, output_raw_check = decompress_wrapper(output_blob)
    if output_raw_check != rebuilt_raw:
        raise RuntimeError("wrapped msgui decompression verification failed")

    relative = Path(source_spec["path"])
    output_path = args.out_dir / relative
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(output_blob)

    glyphs = sorted({char for item in changed for char in item["ko"] if not char.isspace()})
    manifest = {
        "schema": "nobu16.kr.build-manifest.v1",
        "scope": catalog["scope"],
        "version": catalog["version"],
        "language": language,
        "memory_patch": False,
        "source": {
            "path": str(relative).replace("\\", "/"),
            "size": len(source_blob),
            "sha256": source_hash,
        },
        "output": {
            "path": str(relative).replace("\\", "/"),
            "size": len(output_blob),
            "sha256": sha256(output_blob),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256(rebuilt_raw),
        },
        "changed": changed,
        "hangul_glyphs": glyphs,
        "hangul_codepoints": [f"U+{ord(char):04X}" for char in glyphs],
        "verification": {
            "stock_sha256": "OK",
            "source_strings": "OK",
            "table_parse_roundtrip": "OK",
            "wrapper_decompress": "OK",
        },
    }
    manifest_path = args.out_dir / "main_menu_msg_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"language={language}")
    print(f"source={source_path}")
    print(f"source_sha256={source_hash}")
    print(f"output={output_path}")
    print(f"output_sha256={manifest['output']['sha256']}")
    print(f"changed={len(changed)}")
    print(f"hangul_glyphs={len(glyphs)}")
    print("memory_patch=false")
    print("verification=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
