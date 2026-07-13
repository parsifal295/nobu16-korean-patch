#!/usr/bin/env python3
"""Audit a locally rebuilt, private wide-glyph candidate without exposing its payload."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "KR_PATCH_WORK" / "tools"
sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402
import nobu16_msg_table as msgtable  # noqa: E402
import validate_g1n_surgical as g1ncheck  # noqa: E402


PROBE = ROOT / "KR_PATCH_WORK" / "workstreams" / "castle_wide_glyph"
WRAPPED = PROBE / "private" / "wrapper_candidate"
STOCK_MESSAGE = ROOT / "MSG_PK" / "SC" / "msgdata.bin"
STOCK_FONT = ROOT / "RES_SC" / "res_lang.bin"
TARGET_MESSAGE = WRAPPED / "MSG_PK" / "SC" / "msgdata.bin"
TARGET_FONT = WRAPPED / "RES_SC" / "res_lang.bin"
RAW_MESSAGE = PROBE / "private" / "candidate" / "msgdata.probe-9168-wide.name-only.raw"
RAW_FONTS = {
    6: PROBE / "private" / "candidate" / "SC_6.probe-9168-wide.g1n",
    7: PROBE / "private" / "candidate" / "SC_7.probe-9168-wide.g1n",
}
HARNESS = PROBE / "Invoke-WideCastleNameOnlyProbe.ps1"
OUTPUT = PROBE / "audit" / "private_candidate_audit.json"

EXPECTED = {
    "stock_message": "0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E",
    "target_message": "165353713703A2A1D72C24D6C9A7D5709F21FA3D2B641993BE786BA14B2B17CC",
    "raw_stock_message": "1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF",
    "raw_target_message": "2F83D99CAFD4E0291A2C33DFAFC9AB79B4DB2FE37CD5FD8DD6C101B4D724C48E",
    "stock_font": "916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99",
    "target_font": "AFBB287B5418FBCB44B083F7D77E5F53426AE7E1AB23C6B69F17EC98E0EB7258",
    "raw_font_6": "22E253653364A0F1F4FC6F597D2EBFA0B5B1B8A12B84F0380046C2C8106570A1",
    "raw_font_7": "E239E92F7F4E2AC866B9918D553EBE8FB657633B5875DA9B3664787EBD22C795",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def hash_gate(path: Path, expected: str, label: str) -> dict[str, object]:
    actual = sha256_file(path)
    require(actual == expected, f"{label} hash mismatch: expected={expected} actual={actual}")
    return {"path": relative(path), "size": path.stat().st_size, "sha256": actual}


def audit_message() -> dict[str, object]:
    stock_blob = STOCK_MESSAGE.read_bytes()
    target_blob = TARGET_MESSAGE.read_bytes()
    stock_header, stock_raw = lz4.decompress_wrapper(stock_blob)
    target_header, target_raw = lz4.decompress_wrapper(target_blob)
    require(stock_header.prefix == target_header.prefix, "message wrapper prefix changed")
    require(sha256_bytes(stock_raw) == EXPECTED["raw_stock_message"], "stock raw message hash mismatch")
    require(sha256_bytes(target_raw) == EXPECTED["raw_target_message"], "target raw message hash mismatch")
    require(target_raw == RAW_MESSAGE.read_bytes(), "wrapped message does not contain pinned raw candidate")

    stock_table = msgtable.parse_message_table(stock_raw)
    target_table = msgtable.parse_message_table(target_raw)
    require(stock_table.string_count == target_table.string_count == 29210, "message count changed")
    changed = [
        index
        for index, (before, after) in enumerate(zip(stock_table.texts, target_table.texts))
        if before != after
    ]
    require(changed == [9168], f"message changes are not exactly id 9168: {changed[:20]}")
    require(target_table.texts[9168] == "\ud792", "target id 9168 is not U+D792")
    require(target_table.texts[9936] == stock_table.texts[9936], "shared Castle suffix changed")
    require(
        msgtable.rebuild_message_table(target_table, target_table.texts) == target_raw,
        "target raw message is not byte-identical on parse/rebuild",
    )
    return {
        "stock_wrapper": hash_gate(STOCK_MESSAGE, EXPECTED["stock_message"], "stock message wrapper"),
        "target_wrapper": hash_gate(TARGET_MESSAGE, EXPECTED["target_message"], "target message wrapper"),
        "wrapper_prefix_hex": target_header.prefix.hex(" ").upper(),
        "target_uncompressed_size": target_header.uncompressed_size,
        "target_compressed_size": target_header.compressed_size,
        "string_count": target_table.string_count,
        "changed_ids": changed,
        "id_9168_after_codepoint": "U+D792",
        "id_9936_shared_suffix_unchanged": True,
        "raw_parse_rebuild_byte_identical": True,
    }


def audit_g1n(entry: int, stock_raw: bytes, extracted: bytes) -> dict[str, object]:
    target_path = RAW_FONTS[entry]
    require(extracted == target_path.read_bytes(), f"entry {entry} raw data differs from pinned candidate")
    with tempfile.TemporaryDirectory(prefix="nobu16-wide-glyph-audit-") as temporary:
        stock_path = Path(temporary) / f"SC_{entry}.stock.g1n"
        stock_path.write_bytes(stock_raw)
        result = g1ncheck.compare_g1n(
            g1ncheck.parse_g1n(stock_path),
            g1ncheck.parse_g1n(target_path),
            "append",
        )
    require(result.ok, f"entry {entry} G1N append audit failed: {result.errors}")
    require(result.added_records == [1, 1], f"entry {entry} appended record counts changed")
    require(
        result.changed_codepoints == {0: [0xD792], 1: [0xD792]},
        f"entry {entry} changed codepoints are not exactly U+D792 in both tables",
    )
    parsed = g1ncheck.parse_g1n(target_path)
    new_records = [
        parsed.tables[table].records[-1]
        for table in range(parsed.table_count)
    ]
    return {
        "entry": entry,
        "raw_path": relative(target_path),
        "raw_size": target_path.stat().st_size,
        "raw_sha256": sha256_file(target_path),
        "appended_records_by_table": result.added_records,
        "changed_codepoints_by_table": {
            str(table): [f"U+{cp:04X}" for cp in values]
            for table, values in result.changed_codepoints.items()
        },
        "new_record_metrics": [
            {
                "table": table,
                "width": record.width,
                "height": record.height,
                "advance": record.advance,
                "row_stride": record.row_stride,
                "pixel_size": record.pixel_size,
                "atlas_pointer": record.pointer,
            }
            for table, record in enumerate(new_records)
        ],
        "old_maps_except_proxy_exact": True,
        "old_records_exact": True,
        "complete_stock_atlas_exact_prefix": True,
    }


def audit_font_archive() -> dict[str, object]:
    stock_blob = STOCK_FONT.read_bytes()
    target_blob = TARGET_FONT.read_bytes()
    stock = lz4.parse_link(stock_blob)
    target = lz4.parse_link(target_blob)
    require(lz4.rebuild_link(stock) == stock_blob, "stock LINK parse/rebuild changed bytes")
    require(lz4.rebuild_link(target) == target_blob, "target LINK parse/rebuild changed bytes")
    require(len(stock.entries) == len(target.entries), "LINK entry count changed")
    require(stock.version == target.version and stock.reserved == target.reserved, "LINK version fields changed")
    require(stock.fixed_header == target.fixed_header, "LINK fixed header changed")
    require(stock.pre_data_padding == target.pre_data_padding, "LINK pre-data padding changed")

    changed_entries: list[int] = []
    g1n_results: list[dict[str, object]] = []
    for before, after in zip(stock.entries, target.entries):
        require(before.index == after.index, "LINK entry order changed")
        require(before.gap_after == after.gap_after, f"LINK entry {before.index} trailer/gap changed")
        if before.data != after.data:
            changed_entries.append(before.index)
        if before.index in (6, 7):
            before_header, stock_raw = lz4.decompress_wrapper(before.data)
            after_header, raw = lz4.decompress_wrapper(after.data)
            require(before_header.prefix == after_header.prefix, f"entry {before.index} wrapper prefix changed")
            g1n_results.append(audit_g1n(before.index, stock_raw, raw))
        else:
            require(before.data == after.data, f"non-target LINK entry {before.index} changed")

    require(changed_entries == [6, 7], f"LINK changed entries are not exactly [6, 7]: {changed_entries}")
    return {
        "stock_archive": hash_gate(STOCK_FONT, EXPECTED["stock_font"], "stock font archive"),
        "target_archive": hash_gate(TARGET_FONT, EXPECTED["target_font"], "target font archive"),
        "link_entry_count": len(target.entries),
        "link_version": target.version,
        "link_reserved": target.reserved,
        "link_parse_rebuild_byte_identical": True,
        "changed_entries": changed_entries,
        "unchanged_entry_payload_count": len(target.entries) - len(changed_entries),
        "all_entry_trailers_and_gaps_exact": True,
        "g1n": g1n_results,
    }


def audit_harness_text() -> dict[str, object]:
    text = HARNESS.read_text(encoding="utf-8")
    required = [
        EXPECTED["stock_message"],
        EXPECTED["target_message"],
        EXPECTED["stock_font"],
        EXPECTED["target_font"],
        "Assert-NoGameProcess",
        "Invoke-AtomicReplace",
        "automatic-rollback",
        "operation.lock",
        "journal.json",
    ]
    missing = [token for token in required if token not in text]
    require(not missing, f"harness is missing required tokens: {missing}")
    forbidden = [
        "WriteProcessMemory",
        "OpenProcess",
        "VirtualProtect",
        "Start-Process",
        "NOBU16PK.exe",
        "NOBU16PK_EN.exe",
        "HKCU:",
        "HKLM:",
        "Set-ItemProperty",
        "New-ItemProperty",
        "Remove-ItemProperty",
    ]
    found = [token for token in forbidden if token.lower() in text.lower()]
    require(not found, f"harness contains forbidden process/launch/registry tokens: {found}")
    return {
        "path": relative(HARNESS),
        "size": HARNESS.stat().st_size,
        "sha256": sha256_file(HARNESS),
        "required_safety_tokens_present": True,
        "forbidden_process_launch_registry_tokens_found": [],
        "executed_by_this_audit": False,
    }


def main() -> int:
    result = {
        "schema": "nobu16.kr.wide-castle-wrapped-candidate-audit.v1",
        "status": "PASS",
        "candidate_kind": "private-noninstalled-runtime-probe",
        "message": audit_message(),
        "font_archive": audit_font_archive(),
        "harness": audit_harness_text(),
        "scope": {
            "installed_game_files_modified": False,
            "game_launched": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_access": False,
            "canonical_or_release_directory_modified": False,
        },
        "exact_change_claim": {
            "message_ids_changed": [9168],
            "shared_castle_suffix_changed": False,
            "font_link_entries_changed": [6, 7],
            "font_codepoints_changed_per_entry_table": ["U+D792"],
            "font_records_appended_per_entry_table": 1,
            "all_other_link_entry_payloads_exact": True,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"audit={OUTPUT}")
    print(f"audit_sha256={sha256_file(OUTPUT)}")
    print("status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
