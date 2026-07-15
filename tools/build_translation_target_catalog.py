#!/usr/bin/env python3
"""Build the source-free PK-runtime translation target-key catalog from pristine backups.

The catalog contains only integer string IDs, msggame coordinates, or shared
strdata block/slot coordinates plus structural counts and SHA-256 values.  It
never serializes source strings and never reads live game resources.  Inputs
are explicit, pinned backup locations created before file-only transactions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = ROOT.parent
TOOLS_ROOT = ROOT / "tools"
MSGGAME_ROOT = ROOT / "workstreams" / "msggame"
STRDATA_CONTAINER_ROOT = ROOT / "workstreams" / "switch_msgbre_v11"
for import_root in (TOOLS_ROOT, MSGGAME_ROOT, STRDATA_CONTAINER_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import nobu16_lz4 as lz4  # noqa: E402
import nobu16_msg_table as msg_table  # noqa: E402
from msggame_format import (  # noqa: E402
    is_visible_translation_candidate,
    iter_literals,
    parse_packed_msggame,
)
from strdata_container import parse_strdata  # noqa: E402


OUTPUT = ROOT / "data" / "public" / "translation_target_keys.v0.1.json"
DEFAULT_OFFICER_BACKUP_ROOT = (
    GAME_ROOT / "KR_PATCH_BACKUP" / "officer_names_v0_1" / "stock"
)
DEFAULT_TRANSACTION_BACKUP_ROOT = (
    GAME_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "pk-full-messages-seoulhangang-v1"
    / "originals"
    / "MSG_PK"
    / "SC"
)
DEFAULT_SHARED_TRANSACTION_BACKUP_ROOT = (
    GAME_ROOT / "KR_PATCH_BACKUP" / "file_only_transaction"
)

CATALOG_SCHEMA = "nobu16.kr.translation-target-keys.v0.1"
EXPECTED_PK_TOTAL = 61_306
EXPECTED_TOTAL = 87_996
SHARED_STRDATA_PATH = "MSG/SC/strdata.bin"
SHARED_STRDATA_PACKED_SIZE = 516_628
SHARED_STRDATA_PACKED_SHA256 = "93F88D71210B96783749CEB948E0713D7E6552F764F644092B71A5FD0C994B88"
SHARED_STRDATA_RAW_SIZE = 760_388
SHARED_STRDATA_RAW_SHA256 = "17EF622F36BA94009F67519DC79ED543C223B467311E51711A009F9DD0816214"
SHARED_STRDATA_BLOCK_SLOT_COUNTS = (25_069, 4_100, 3_000, 122, 20)
SHARED_STRDATA_TARGET_COUNT = 26_690


class TargetCatalogError(ValueError):
    """Raised when a pristine input or catalog invariant fails."""


@dataclass(frozen=True)
class BaselineSpec:
    logical_path: str
    backup_set: str
    filename: str
    packed_sha256: str
    raw_sha256: str
    total_slots: int
    expected_target_count: int
    record_total: int | None = None


BASELINES: tuple[BaselineSpec, ...] = (
    BaselineSpec(
        "MSG_PK/SC/msgui.bin",
        "officer_names_v0_1/stock",
        "msgui.stock.bak",
        "C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82",
        "D0699841A1F96BBF08420F319A271A2F960F7851164082EA3170BC4CA3A32976",
        5_100,
        4_037,
    ),
    BaselineSpec(
        "MSG_PK/SC/msgev.bin",
        "officer_names_v0_1/stock",
        "msgev.stock.bak",
        "7221A53E6E5CF493A3FAFFFCE35280E8147898120EEC59E460A2429AA265C1F9",
        "99E0338A64FF4140AD6E27503B1BF138AC44F5B68F01973ED61D0C949619DC91",
        17_910,
        12_906,
    ),
    BaselineSpec(
        "MSG_PK/SC/msgdata.bin",
        "officer_names_v0_1/stock",
        "msgdata.stock.bak",
        "0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E",
        "1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF",
        29_210,
        25_534,
    ),
    BaselineSpec(
        "MSG_PK/SC/msgbre.bin",
        "pk-full-messages-seoulhangang-v1/originals",
        "msgbre.bin",
        "AD1FEC313228AADB00581C25AE59D8C6AFF54DD771A4D0F7BC35CD1B44D77B8D",
        "E0343DCDB1BE7C62E515DE52B9045DC54A4D8FE77BF9B6F0836A3478CBD77779",
        3_000,
        2_217,
    ),
    BaselineSpec(
        "MSG_PK/SC/msgire.bin",
        "pk-full-messages-seoulhangang-v1/originals",
        "msgire.bin",
        "F275691D4B583C2A54BB4422F290504D3D27710E1B8CC9E0A4C91E7A49195D96",
        "0FEDF372903B72B32F111CEAE52914E14D4234D6428766A31E4A13CC76DB3F54",
        122,
        122,
    ),
    BaselineSpec(
        "MSG_PK/SC/msgstf.bin",
        "pk-full-messages-seoulhangang-v1/originals",
        "msgstf.bin",
        "956B37C34E28E0DB04ABB5F0602A1111560358BF58A3A39CCB45468CC5BE290A",
        "83AE1BCC142286EAEA73327A7670EB77BFD6E6EB4520BCDE0914CBFA3C529B75",
        20,
        8,
    ),
    BaselineSpec(
        "MSG_PK/SC/msggame.bin",
        "pk-full-messages-seoulhangang-v1/originals",
        "msggame.bin",
        "BD7B33FCC7495B855B0828C7FE4E5F7ADB2DE656A9B12E20259750F94EE665D6",
        "1958B2B801D37186D478284EA0E29CA96D8DA2BC087D6BEB74A4139EF01C11CE",
        25_598,
        16_482,
        record_total=21_581,
    ),
)


# These 97 pristine SC whitespace/empty slots are deliberately activated by
# MSGUI v0.2 and therefore belong to its translation target by policy.
MSGUI_INTENTIONAL_ACTIVATION_IDS: tuple[int, ...] = (
    2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2338,
    2339, 2340, 2341, 2342, 2343, 2344, 2345, 2346, 2347, 2348,
    2408, 2409, 2419, 2420, 2457, 2459, 2498, 2499, 2500, 2558,
    2650, 2657, 2661, 2691, 2692, 2693, 2694, 2695, 2696, 2697,
    2698, 2699, 2700, 2701, 2702, 2703, 2704, 2705, 2706, 2707,
    2708, 2709, 2710, 2711, 2712, 2713, 2714, 2715, 2716, 2717,
    2718, 2719, 2720, 2721, 2722, 2723, 2724, 2725, 2726, 2727,
    2728, 2729, 2730, 2731, 2732, 2733, 2734, 2735, 2736, 2737,
    2738, 2739, 2740, 2741, 2742, 2743, 2744, 2745, 2746, 3688,
    3691, 3784, 3855, 3942, 3988, 3989, 3990,
)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return sha256(encoded)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TargetCatalogError(message)


def resolve_input(
    spec: BaselineSpec,
    *,
    officer_backup_root: Path,
    transaction_backup_root: Path,
) -> Path:
    if spec.backup_set == "officer_names_v0_1/stock":
        root = officer_backup_root
    else:
        root = transaction_backup_root
    path = root / spec.filename
    require(path.is_file(), f"missing pristine backup for {spec.logical_path}: {path}")
    return path


def read_pinned_packed(path: Path, spec: BaselineSpec) -> tuple[bytes, bytes]:
    packed = path.read_bytes()
    require(
        sha256(packed) == spec.packed_sha256,
        f"{spec.logical_path}: pristine packed SHA-256 mismatch",
    )
    _header, raw = lz4.decompress_wrapper(packed)
    require(
        sha256(raw) == spec.raw_sha256,
        f"{spec.logical_path}: pristine raw SHA-256 mismatch",
    )
    return packed, raw


def read_pinned_shared_strdata(
    shared_transaction_backup_root: Path,
) -> tuple[bytes, bytes]:
    """Find the exact pristine shared strdata only in transaction backups."""

    pattern = "*/originals/MSG/SC/strdata.bin"
    matches: list[tuple[Path, bytes]] = []
    for path in sorted(shared_transaction_backup_root.glob(pattern)):
        if not path.is_file():
            continue
        packed = path.read_bytes()
        if (
            len(packed) == SHARED_STRDATA_PACKED_SIZE
            and sha256(packed) == SHARED_STRDATA_PACKED_SHA256
        ):
            matches.append((path, packed))
    require(
        bool(matches),
        "missing exact pristine transaction backup for MSG/SC/strdata.bin",
    )
    _path, packed = matches[0]
    _header, raw = lz4.decompress_wrapper(packed)
    require(
        len(raw) == SHARED_STRDATA_RAW_SIZE,
        "MSG/SC/strdata.bin: pristine raw size mismatch",
    )
    require(
        sha256(raw) == SHARED_STRDATA_RAW_SHA256,
        "MSG/SC/strdata.bin: pristine raw SHA-256 mismatch",
    )
    return packed, raw


def visible_common_ids(texts: Sequence[str]) -> list[int]:
    # This exactly reproduces the project's established stock_visible_nonblank
    # policy: Unicode whitespace-only slots are not translation targets.
    return [entry_id for entry_id, value in enumerate(texts) if value.strip()]


def build_common_resource(
    spec: BaselineSpec,
    *,
    path: Path,
) -> dict[str, Any]:
    packed, raw = read_pinned_packed(path, spec)
    table = msg_table.parse_message_table(raw)
    require(table.string_count == spec.total_slots, f"{spec.logical_path}: slot count mismatch")
    visible_ids = visible_common_ids(table.texts)
    intentional: list[int] = []
    if spec.logical_path.endswith("/msgui.bin"):
        intentional = list(MSGUI_INTENTIONAL_ACTIVATION_IDS)
        require(len(intentional) == 97, "msgui intentional activation count is not 97")
        require(len(set(intentional)) == len(intentional), "duplicate msgui activation ID")
        for entry_id in intentional:
            require(0 <= entry_id < table.string_count, f"msgui activation ID out of range: {entry_id}")
            require(
                not table.texts[entry_id].strip(),
                f"msgui activation ID {entry_id} is not blank in pristine SC",
            )
    targets = sorted(set(visible_ids) | set(intentional))
    require(
        len(targets) == spec.expected_target_count,
        f"{spec.logical_path}: target count={len(targets)}, expected={spec.expected_target_count}",
    )
    return {
        "path": spec.logical_path,
        "key_kind": "id",
        "total_slots": table.string_count,
        "pristine_visible_nonblank": len(visible_ids),
        "intentional_activation_count": len(intentional),
        "intentional_activation_ids": intentional,
        "target_count": len(targets),
        "target_keys_sha256": canonical_hash(targets),
        "target_ids": targets,
        "baseline": {
            "backup_set": spec.backup_set,
            "filename": spec.filename,
            "packed_size": len(packed),
            "packed_sha256": spec.packed_sha256,
            "raw_size": len(raw),
            "raw_sha256": spec.raw_sha256,
        },
    }


def build_msggame_resource(spec: BaselineSpec, *, path: Path) -> dict[str, Any]:
    packed, raw = read_pinned_packed(path, spec)
    parsed = parse_packed_msggame(packed)
    coordinates = sorted(
        [literal.block_id, literal.record_id, literal.literal_id]
        for literal in iter_literals(parsed.archive)
        if is_visible_translation_candidate(literal.text)
    )
    all_literal_count = sum(1 for _ in iter_literals(parsed.archive))
    require(all_literal_count == spec.total_slots, "msggame literal count mismatch")
    require(parsed.archive.record_count == spec.record_total, "msggame record count mismatch")
    require(
        len(coordinates) == spec.expected_target_count,
        f"msggame target count={len(coordinates)}, expected={spec.expected_target_count}",
    )
    require(len({tuple(value) for value in coordinates}) == len(coordinates), "duplicate msggame coordinate")
    return {
        "path": spec.logical_path,
        "key_kind": "msggame_coordinate",
        "record_total": parsed.archive.record_count,
        "total_slots": all_literal_count,
        "pristine_visible_nonblank": len(coordinates),
        "intentional_activation_count": 0,
        "intentional_activation_coordinates": [],
        "target_count": len(coordinates),
        "target_keys_sha256": canonical_hash(coordinates),
        "target_coordinates": coordinates,
        "baseline": {
            "backup_set": spec.backup_set,
            "filename": spec.filename,
            "packed_size": len(packed),
            "packed_sha256": spec.packed_sha256,
            "raw_size": len(raw),
            "raw_sha256": spec.raw_sha256,
        },
    }


def build_shared_strdata_resource(
    *, shared_transaction_backup_root: Path
) -> dict[str, Any]:
    packed, raw = read_pinned_shared_strdata(shared_transaction_backup_root)
    parsed = parse_strdata(raw)
    block_slot_counts = tuple(block.slot_count for block in parsed.blocks)
    require(
        block_slot_counts == SHARED_STRDATA_BLOCK_SLOT_COUNTS,
        "MSG/SC/strdata.bin: block slot counts differ",
    )
    coordinates = sorted(
        [block.block_id, slot_id]
        for block in parsed.blocks
        for slot_id, value in enumerate(block.texts)
        if value.strip()
    )
    require(
        len(coordinates) == SHARED_STRDATA_TARGET_COUNT,
        (
            f"MSG/SC/strdata.bin: target count={len(coordinates)}, "
            f"expected={SHARED_STRDATA_TARGET_COUNT}"
        ),
    )
    require(
        len({tuple(value) for value in coordinates}) == len(coordinates),
        "MSG/SC/strdata.bin: duplicate block/slot coordinate",
    )
    return {
        "path": SHARED_STRDATA_PATH,
        "runtime_scope": "pk_loaded_shared_base",
        "key_kind": "block_slot_coordinate",
        "block_slot_counts": list(block_slot_counts),
        "total_slots": sum(block_slot_counts),
        "pristine_visible_nonblank": len(coordinates),
        "intentional_activation_count": 0,
        "intentional_activation_coordinates": [],
        "target_count": len(coordinates),
        "target_keys_sha256": canonical_hash(coordinates),
        "target_coordinates": coordinates,
        "baseline": {
            "backup_set": "file_only_transaction/*/originals",
            "filename": SHARED_STRDATA_PATH,
            "packed_size": len(packed),
            "packed_sha256": SHARED_STRDATA_PACKED_SHA256,
            "raw_size": len(raw),
            "raw_sha256": SHARED_STRDATA_RAW_SHA256,
        },
    }


def build_catalog(
    *,
    officer_backup_root: Path,
    transaction_backup_root: Path,
    shared_transaction_backup_root: Path,
) -> dict[str, Any]:
    resources: list[dict[str, Any]] = []
    for spec in BASELINES:
        input_path = resolve_input(
            spec,
            officer_backup_root=officer_backup_root,
            transaction_backup_root=transaction_backup_root,
        )
        if spec.logical_path.endswith("/msggame.bin"):
            resource = build_msggame_resource(spec, path=input_path)
        else:
            resource = build_common_resource(spec, path=input_path)
        resources.append(resource)

    pk_total = sum(int(resource["target_count"]) for resource in resources)
    require(
        pk_total == EXPECTED_PK_TOTAL,
        f"PK-private target count={pk_total}, expected={EXPECTED_PK_TOTAL}",
    )
    resources.append(
        build_shared_strdata_resource(
            shared_transaction_backup_root=shared_transaction_backup_root
        )
    )

    total = sum(int(resource["target_count"]) for resource in resources)
    require(total == EXPECTED_TOTAL, f"all target count={total}, expected={EXPECTED_TOTAL}")
    aggregate_keys = {
        resource["path"]: (
            resource["target_ids"]
            if resource["key_kind"] == "id"
            else resource["target_coordinates"]
        )
        for resource in resources
    }
    return {
        "schema": CATALOG_SCHEMA,
        "source_free": True,
        "contains_source_text": False,
        "generated_by": "tools/build_translation_target_catalog.py",
        "policy": {
            "common_tables": "pristine SC value.strip() is non-empty",
            "msgui": "pristine visible IDs plus 97 intentional v0.2 activations",
            "msggame": "pristine SC literals containing a printable non-whitespace character",
            "shared_strdata": "exact PK-loaded MSG/SC/strdata.bin block/slot values whose pristine SC value.strip() is non-empty",
            "progress": "completed and coverage are intersections with these target keys; non-target activations are reported separately",
        },
        "pk_private_resource_count": len(BASELINES),
        "pk_private_target_total": pk_total,
        "shared_runtime_resource_count": 1,
        "shared_runtime_target_total": SHARED_STRDATA_TARGET_COUNT,
        "resource_count": len(resources),
        "target_total": total,
        "all_target_keys_sha256": canonical_hash(aggregate_keys),
        "resources": resources,
    }


def encode_catalog(catalog: dict[str, Any]) -> str:
    return json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--officer-backup-root",
        type=Path,
        default=DEFAULT_OFFICER_BACKUP_ROOT,
        help="Pristine officer_names_v0_1/stock directory; never the live MSG_PK tree.",
    )
    parser.add_argument(
        "--transaction-backup-root",
        type=Path,
        default=DEFAULT_TRANSACTION_BACKUP_ROOT,
        help="Pristine pk-full-messages-seoulhangang-v1 originals/MSG_PK/SC directory.",
    )
    parser.add_argument(
        "--shared-transaction-backup-root",
        type=Path,
        default=DEFAULT_SHARED_TRANSACTION_BACKUP_ROOT,
        help=(
            "Transaction backup root searched only for the exact pinned "
            "originals/MSG/SC/strdata.bin; the live game tree is never read."
        ),
    )
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if the public catalog is stale")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog = build_catalog(
        officer_backup_root=args.officer_backup_root,
        transaction_backup_root=args.transaction_backup_root,
        shared_transaction_backup_root=args.shared_transaction_backup_root,
    )
    encoded = encode_catalog(catalog)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != encoded:
            print("translation target-key catalog is stale")
            return 1
        print("translation target-key catalog is current")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(f"output={args.output}")
    print(f"target_total={catalog['target_total']}")
    for resource in catalog["resources"]:
        print(
            f"{resource['path']}={resource['target_count']} "
            f"keys_sha256={resource['target_keys_sha256']}"
        )
    print(f"all_target_keys_sha256={catalog['all_target_keys_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
