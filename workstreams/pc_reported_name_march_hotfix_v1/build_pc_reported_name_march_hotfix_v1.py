#!/usr/bin/env python3
"""Build the source-free v0.90.1 surname hotfix and pin the march notice.

The v0.90.1 resource target accidentally carries ``부족`` in dynamic surname
slot 757. The same slot is used by Base ``strdata`` and PK ``msgdata``.
This builder restores the canonical Korean surname fragment ``초 `` in both
tables and keeps the already-correct Base march notification byte-identical.

Only an isolated ten-file candidate below this worktree's ``tmp`` directory
can be written. There is no Steam-install, release, or publishing operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
WORKSPACE = REPO.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
DEFAULT_INPUT_ROOT = (
    WORKSPACE
    / "scratch"
    / "release-v0901-20260731"
    / "isolated-four-profile"
)
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "candidate"
DEFAULT_MANIFEST_PATH = TMP_ROOT / "build_manifest.v1.json"

TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "strdata"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
RUNTIME_QA = REPO / "workstreams" / "pc_dialogue_runtime_surface_qa_v1"
for root in (TOOLS, STRDATA_TOOLS, MSGGAME_TOOLS, RUNTIME_QA):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import (  # noqa: E402
    MessageTable,
    parse_message_table,
    rebuild_message_table,
)
from strdata_format import (  # noqa: E402
    StrdataArchive,
    parse_raw_strdata,
    rebuild_raw_strdata,
)
from msggame_format import parse_packed_msggame, parse_record_literals  # noqa: E402
import audit_runtime_surface_v1 as QA  # noqa: E402


SCHEMA = "nobu16.kr.pc-reported-name-march-hotfix-build.v1"
OVERLAY_SCHEMA = "nobu16.kr.pc-reported-name-march-hotfix-overlay.v1"
BASE_STRDATA = "MSG/JP/strdata.bin"
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGDATA = "MSG_PK/JP/msgdata.bin"
TARGET_ID = 757
BEFORE = "부족"
AFTER = "초 "
MARCH_COORDINATE = (6, 4137)
MARCH_LITERALS = (
    "우리 군단의 부대가\n",
    "의 ",
    "으로\n진군 중",
)
MARCH_RECORD_RAW_HEX = (
    "070701B0C6ACB9200070ADE8B258C7200080BD00B300AC0A00070702025032"
    "07070158C720000707020264320707013CC75CB80A00C4C970AD200011C907"
    "070201432C020000050505"
)
MARCH_FORMAL_RENDER = (
    "우리 군단의 부대가\n"
    "오노데라 가문의 요코테성으로\n"
    "진군 중입니다"
)
OVERLAY_PATH = WORKSTREAM / "public" / "reported_name_march_hotfix.v1.json"

PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    BASE_MSGGAME,
    BASE_STRDATA,
    "MSG_PK/JP/msgbre.bin",
    PK_MSGDATA,
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgui.bin",
)
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "17A61E7F9B6BBFE4FC6C944D0C9A51D6B45DE201A30130AB4FF445DFE99B5172",
    BASE_MSGGAME: "ADB73561AAA10A66364B3C09B2184BB29698186C808E0FE264C64B1DD2A5A4FE",
    BASE_STRDATA: "C1B28E6EDF5E6602FC909403BF3BA7F79366DC6D6861960D4F75B2F8F92EB438",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    PK_MSGDATA: "3C8185F1A038D7AE1D5D0A5FF12BE45B701F685F26B743E99C9DC272EDA1345A",
    "MSG_PK/JP/msgev.bin": "3461C647D113CF424E791D2D694AADFADEA45F38873A110810558DE0E09C50C8",
    "MSG_PK/JP/msggame.bin": "1D7F1FB2086419BD1FC928012F3E0E3D0BA2C600809513188A3FFBA455F63EFF",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    "MSG/JP/ev_strdata.bin": 928_123,
    BASE_MSGGAME: 1_557_915,
    BASE_STRDATA: 942_246,
    "MSG_PK/JP/msgbre.bin": 484_068,
    PK_MSGDATA: 482_097,
    "MSG_PK/JP/msgev.bin": 1_048_312,
    "MSG_PK/JP/msggame.bin": 1_815_549,
    "MSG_PK/JP/msgire.bin": 23_128,
    "MSG_PK/JP/msgstf.bin": 17_341,
    "MSG_PK/JP/msgui.bin": 122_733,
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_STRDATA: "52391FD804294BCD648B36130018CB971070C7CE91E4C642C6899AB1145D0356",
    PK_MSGDATA: "DE38A271DD8E2C995A5C2CD1E00B2C36EB17D0416625B4F8418AA4176B1E4176",
}
TARGET_SIZES = dict(INPUT_SIZES)


class ReportedTextHotfixError(RuntimeError):
    """An input, structure, output, or policy contract differed."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_sha256(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve(strict=False)
    resolved_path = path.resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ReportedTextHotfixError(
            f"{label} escapes its allowed root: {resolved_path}"
        ) from exc
    return resolved_path


def require_private_output(path: Path, label: str) -> Path:
    checked = require_under(TMP_ROOT, path, label)
    if checked == TMP_ROOT.resolve(strict=False):
        raise ReportedTextHotfixError(f"{label} cannot be the private tmp root")
    return checked


def profile(root: Path) -> tuple[dict[str, str], dict[str, int]]:
    root = root.resolve(strict=True)
    hashes: dict[str, str] = {}
    sizes: dict[str, int] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise ReportedTextHotfixError(f"missing profile resource: {relative}")
        hashes[relative] = sha256_path(path)
        sizes[relative] = path.stat().st_size
    return hashes, sizes


def assert_profile(
    root: Path,
    hashes: Mapping[str, str],
    sizes: Mapping[str, int],
    label: str,
) -> None:
    actual_hashes, actual_sizes = profile(root)
    if actual_hashes != dict(hashes) or actual_sizes != dict(sizes):
        mismatch = {
            relative: {
                "expected_hash": hashes[relative],
                "actual_hash": actual_hashes[relative],
                "expected_size": sizes[relative],
                "actual_size": actual_sizes[relative],
            }
            for relative in PROFILE_PATHS
            if actual_hashes[relative] != hashes[relative]
            or actual_sizes[relative] != sizes[relative]
        }
        raise ReportedTextHotfixError(f"{label} profile differs: {mismatch}")


def unpack_message(source: bytes, label: str) -> tuple[object, MessageTable]:
    wrapper, raw = decompress_wrapper(source)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise ReportedTextHotfixError(f"{label} failed byte round-trip")
    return wrapper, table


def unpack_strdata(source: bytes) -> tuple[object, StrdataArchive]:
    wrapper, raw = decompress_wrapper(source)
    archive = parse_raw_strdata(raw)
    if rebuild_raw_strdata(archive) != raw:
        raise ReportedTextHotfixError("Base strdata failed byte round-trip")
    return wrapper, archive


def slot_bytes(table: MessageTable, entry_id: int) -> bytes:
    start = table.table_offset + table.string_offsets[entry_id]
    end = (
        table.table_offset + table.string_offsets[entry_id + 1]
        if entry_id + 1 < table.string_count
        else table.logical_end
    )
    return table.blob[start:end]


def patch_base_strdata(source: bytes) -> bytes:
    wrapper, archive = unpack_strdata(source)
    texts = list(archive.blocks[0].texts)
    if texts[TARGET_ID] != BEFORE:
        raise ReportedTextHotfixError(
            f"unexpected Base surname preimage: {texts[TARGET_ID]!r}"
        )
    texts[TARGET_ID] = AFTER
    rebuilt = rebuild_raw_strdata(archive, {0: texts})
    checked = parse_raw_strdata(rebuilt)
    if checked.blocks[0].texts[TARGET_ID] != AFTER:
        raise ReportedTextHotfixError("Base surname replacement did not persist")
    return recompress_wrapper(rebuilt, wrapper)


def patch_pk_msgdata(source: bytes) -> bytes:
    wrapper, table = unpack_message(source, PK_MSGDATA)
    texts = list(table.texts)
    if texts[TARGET_ID] != BEFORE:
        raise ReportedTextHotfixError(
            f"unexpected PK surname preimage: {texts[TARGET_ID]!r}"
        )
    texts[TARGET_ID] = AFTER
    rebuilt = rebuild_message_table(table, texts)
    checked = parse_message_table(rebuilt)
    if checked.texts[TARGET_ID] != AFTER:
        raise ReportedTextHotfixError("PK surname replacement did not persist")
    return recompress_wrapper(rebuilt, wrapper)


def assert_non_target_slots_unchanged(
    before: MessageTable,
    after: MessageTable,
    label: str,
) -> None:
    if before.string_count != after.string_count:
        raise ReportedTextHotfixError(f"{label} string count changed")
    changed = tuple(
        entry_id
        for entry_id, (old, new) in enumerate(
            zip(before.texts, after.texts, strict=True)
        )
        if old != new
    )
    if changed != (TARGET_ID,):
        raise ReportedTextHotfixError(
            f"{label} changed unexpected string IDs: {changed}"
        )
    for entry_id in range(before.string_count):
        if entry_id != TARGET_ID and slot_bytes(before, entry_id) != slot_bytes(
            after, entry_id
        ):
            raise ReportedTextHotfixError(
                f"{label} changed non-target slot bytes at {entry_id}"
            )


def verify_component_delta(
    base_before: bytes,
    base_after: bytes,
    pk_before: bytes,
    pk_after: bytes,
) -> None:
    _, base_before_archive = unpack_strdata(base_before)
    _, base_after_archive = unpack_strdata(base_after)
    assert_non_target_slots_unchanged(
        base_before_archive.blocks[0].table,
        base_after_archive.blocks[0].table,
        "Base strdata block 0",
    )
    for old, new in zip(
        base_before_archive.blocks[1:],
        base_after_archive.blocks[1:],
        strict=True,
    ):
        if old.table.blob != new.table.blob:
            raise ReportedTextHotfixError(
                f"Base strdata retain block changed: {old.block_id}"
            )
    _, pk_before_table = unpack_message(pk_before, PK_MSGDATA)
    _, pk_after_table = unpack_message(pk_after, PK_MSGDATA)
    assert_non_target_slots_unchanged(
        pk_before_table,
        pk_after_table,
        "PK msgdata",
    )
    if (
        base_after_archive.blocks[0].texts[TARGET_ID] != AFTER
        or pk_after_table.texts[TARGET_ID] != AFTER
    ):
        raise ReportedTextHotfixError("surname target differs after rebuild")
    if not AFTER.endswith(" "):
        raise ReportedTextHotfixError("surname composition space is absent")


def verify_march_notification(packed: bytes) -> dict[str, Any]:
    archive = parse_packed_msggame(packed).archive
    record = archive.blocks[MARCH_COORDINATE[0]].records[MARCH_COORDINATE[1]]
    literals = tuple(item.text for item in parse_record_literals(record))
    if literals != MARCH_LITERALS:
        raise ReportedTextHotfixError(
            f"march literals differ: expected={MARCH_LITERALS!r}, actual={literals!r}"
        )
    if record.data.hex().upper() != MARCH_RECORD_RAW_HEX:
        raise ReportedTextHotfixError("march record selector/call topology differs")
    components = QA.tolerant_decode_record(record)
    selectors = tuple(
        (
            int(component["group"]),
            int(component["slot"]),
            int(component["property"]),
        )
        for component in components
        if component["kind"] == "selector"
    )
    calls = tuple(
        tuple(int(value) for value in component["target"])
        for component in components
        if component["kind"] == "call"
    )
    if selectors != ((4, 0, 50), (3, 0, 50)) or calls != ((0, 556),):
        raise ReportedTextHotfixError("march selector or terminal call differs")
    records = {
        (item.block_id, item.record_id): item
        for block in archive.blocks
        for item in block.records
    }
    endings = tuple(QA.TerminalRenderer(records).render((0, 556)))
    if endings != ("입니다", "다", "이오"):
        raise ReportedTextHotfixError(f"march terminal family differs: {endings}")
    formal = (
        literals[0]
        + "오노데라 가문"
        + literals[1]
        + "요코테성"
        + literals[2]
        + endings[0]
    )
    if formal != MARCH_FORMAL_RENDER:
        raise ReportedTextHotfixError(f"march formal rendering differs: {formal!r}")
    for forbidden in ("성행", "진군대입니다"):
        if forbidden in formal:
            raise ReportedTextHotfixError(
                f"reported malformed march fragment survived: {forbidden}"
            )
    return {
        "coordinate": "6:4137",
        "literals": list(literals),
        "selectors": [list(item) for item in selectors],
        "terminal_call": "0:556",
        "formal_render": formal,
        "source_resource_byte_identical": True,
    }


def expected_overlay() -> dict[str, Any]:
    return {
        "schema": OVERLAY_SCHEMA,
        "entries": [
            {
                "resource": BASE_STRDATA,
                "block_id": 0,
                "id": TARGET_ID,
                "baseline_utf16le_sha256": text_sha256(BEFORE),
                "ko": AFTER,
                "allow_trailing_space": True,
            },
            {
                "resource": PK_MSGDATA,
                "id": TARGET_ID,
                "baseline_utf16le_sha256": text_sha256(BEFORE),
                "ko": AFTER,
                "allow_trailing_space": True,
            },
        ],
        "march_regression": {
            "resource": BASE_MSGGAME,
            "coordinate": "6:4137",
            "literal_utf16le_sha256": [
                text_sha256(value) for value in MARCH_LITERALS
            ],
            "formal_render_utf16le_sha256": text_sha256(MARCH_FORMAL_RENDER),
            "resource_changed": False,
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_binary": False,
            "steam_write_supported": False,
        },
    }


def validate_overlay() -> None:
    actual = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    if actual != expected_overlay():
        raise ReportedTextHotfixError("tracked source-free overlay differs")


def prepare_candidate(
    input_root: Path = DEFAULT_INPUT_ROOT,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    if tuple(INPUT_SHA256) != PROFILE_PATHS or tuple(INPUT_SIZES) != PROFILE_PATHS:
        raise ReportedTextHotfixError("input profile order differs")
    if tuple(TARGET_SHA256) != PROFILE_PATHS or tuple(TARGET_SIZES) != PROFILE_PATHS:
        raise ReportedTextHotfixError("target profile order differs")
    validate_overlay()
    input_root = input_root.resolve(strict=True)
    assert_profile(input_root, INPUT_SHA256, INPUT_SIZES, "v0.90.1 input")
    source = {
        relative: (input_root / relative).read_bytes()
        for relative in PROFILE_PATHS
    }
    march = verify_march_notification(source[BASE_MSGGAME])
    output = dict(source)
    output[BASE_STRDATA] = patch_base_strdata(source[BASE_STRDATA])
    output[PK_MSGDATA] = patch_pk_msgdata(source[PK_MSGDATA])
    verify_component_delta(
        source[BASE_STRDATA],
        output[BASE_STRDATA],
        source[PK_MSGDATA],
        output[PK_MSGDATA],
    )
    actual_hashes = {
        relative: sha256_bytes(output[relative]) for relative in PROFILE_PATHS
    }
    actual_sizes = {
        relative: len(output[relative]) for relative in PROFILE_PATHS
    }
    if actual_hashes != TARGET_SHA256 or actual_sizes != TARGET_SIZES:
        raise ReportedTextHotfixError("v0.90.1 hotfix target profile differs")
    for relative in PROFILE_PATHS:
        if relative not in {BASE_STRDATA, PK_MSGDATA} and (
            output[relative] != source[relative]
        ):
            raise ReportedTextHotfixError(
                f"retain-only resource changed: {relative}"
            )
    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "candidate_only": True,
        "steam_write_performed": False,
        "input_root": str(input_root),
        "input_sha256": INPUT_SHA256,
        "target_sha256": TARGET_SHA256,
        "target_sizes": TARGET_SIZES,
        "changed_resources": [BASE_STRDATA, PK_MSGDATA],
        "changed_ids": {
            BASE_STRDATA: [TARGET_ID],
            PK_MSGDATA: [TARGET_ID],
        },
        "surname": {
            "id": TARGET_ID,
            "after": AFTER,
            "trailing_composition_space_preserved": True,
            "non_target_slot_bytes_identical": True,
        },
        "march_regression": march,
    }
    return output, report


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def output_files(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }


def verify_private_candidate(
    input_root: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    output_root = require_private_output(output_root, "candidate root")
    if not output_root.is_dir():
        raise ReportedTextHotfixError(
            f"private candidate is absent: {output_root}"
        )
    if output_files(output_root) != set(PROFILE_PATHS):
        raise ReportedTextHotfixError(
            "private candidate must contain exactly the ten-file profile"
        )
    assert_profile(
        output_root,
        TARGET_SHA256,
        TARGET_SIZES,
        "private candidate",
    )
    expected, report = prepare_candidate(input_root)
    for relative in PROFILE_PATHS:
        if (output_root / relative).read_bytes() != expected[relative]:
            raise ReportedTextHotfixError(
                f"private candidate bytes differ: {relative}"
            )
    return report


def build_candidate(
    input_root: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> dict[str, Any]:
    output_root = require_private_output(output_root, "candidate output")
    manifest_path = require_under(TMP_ROOT, manifest_path, "manifest path")
    payloads, report = prepare_candidate(input_root)
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".reported-hotfix-", dir=TMP_ROOT) as temp:
        stage = Path(temp) / "candidate"
        for relative, payload in payloads.items():
            atomic_write(stage / relative, payload)
        assert_profile(stage, TARGET_SHA256, TARGET_SIZES, "staging candidate")
        if output_root.exists():
            require_private_output(output_root, "existing candidate")
            shutil.rmtree(output_root)
        output_root.parent.mkdir(parents=True, exist_ok=True)
        os.replace(stage, output_root)
    verified = verify_private_candidate(input_root, output_root)
    if verified != report:
        raise ReportedTextHotfixError("build and verification reports differ")
    atomic_write(manifest_path, canonical_json(report))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("build", "verify-private", "verify-input"),
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    args = parser.parse_args()
    if args.command == "build":
        report = build_candidate(
            args.input_root,
            args.output_root,
            args.manifest,
        )
    elif args.command == "verify-private":
        report = verify_private_candidate(args.input_root, args.output_root)
    else:
        _payloads, report = prepare_candidate(args.input_root)
    print(canonical_json(report).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
