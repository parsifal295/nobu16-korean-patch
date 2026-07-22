#!/usr/bin/env python3
"""Build and apply the v0.15.1 Steam JP direct resource patch.

The public patch ledger rebuilds all text resources from pristine Steam JP
1.1.7 inputs and applies bounded BSDIFF40 deltas for the image archives and
translated DLC records. It never distributes a complete game resource, verifies every
source and target hash, writes verified backups, and rolls back on failure.

The static EXE installer is intentionally out of scope.  This tool performs
no process-memory work and does not unpack, alter, or distribute the game EXE.
"""

from __future__ import annotations

import argparse
import base64
import bz2
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
import zipfile
import struct
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[1]
for _path in (
    REPO / "tools",
    REPO / "workstreams" / "switch_msgbre_v11",
    REPO / "workstreams" / "msggame",
):
    if _path.is_dir() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_container import parse_strdata, rebuild_strdata  # noqa: E402
import msggame_format as MSGGAME  # noqa: E402


SCHEMA = "nobu16.resource-upgrade-patcher.v1"
STATE_SCHEMA = "nobu16.resource-upgrade-patcher.state.v1"
VERSION = "v0.15.1"
BASELINE_RELEASES = ("v0.13.0", "v0.13.1")
LEDGER_FILENAME = "v0.14.0-resource-patch.json"
RESOURCE_PATHS = (
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
)
RESOURCE_KINDS: Mapping[str, str] = {
    "MSG/JP/msggame.bin": "msggame_records",
    "MSG/JP/strdata.bin": "strdata_container",
    "MSG_PK/JP/msgdata.bin": "common_message_table",
    "MSG_PK/JP/msgev.bin": "common_message_table",
    "MSG_PK/JP/msggame.bin": "msggame_records",
}
EXPECTED_OPERATION_COUNTS: Mapping[str, int] = {
    "MSG/JP/msggame.bin": 161,
    "MSG/JP/strdata.bin": 4_529,
    "MSG_PK/JP/msgdata.bin": 4_551,
    "MSG_PK/JP/msgev.bin": 2_008,
    "MSG_PK/JP/msggame.bin": 349,
}
# A v0.14.0 opaque-record fallback needs 93 small records (6,237 bytes in
# total).  Fixed limits make an accidental full-resource blob fail closed.
MAX_OPAQUE_RECORD_BYTES = 1_024
MAX_OPAQUE_RECORD_PAYLOAD_BYTES = 64 * 1_024

# v0.13.0 and v0.13.1 carry the same game-resource vector.  v0.13.1 changed
# only the static installer, so one predecessor profile safely covers both.
PREDECESSORS: Mapping[str, tuple[int, str]] = {
    "MSG/JP/msggame.bin": (
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
    ),
    "MSG/JP/strdata.bin": (
        957_200,
        "37A1F6280B2663A7FF055C6A2105B5658CA62065582A66213C6D4D4AE2A79E0A",
    ),
    "MSG_PK/JP/msgdata.bin": (
        496_991,
        "8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A",
    ),
    "MSG_PK/JP/msgev.bin": (
        994_739,
        "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    ),
    "MSG_PK/JP/msggame.bin": (
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
    ),
}
TARGETS: Mapping[str, tuple[int, str]] = {
    "MSG/JP/msggame.bin": (
        1_504_462,
        "3886D081E26AC2DEE75D8799CF839FEF2EFC6D27433FCD04C5FD43B4D23FD23A",
    ),
    "MSG/JP/strdata.bin": (
        942_246,
        "C1B28E6EDF5E6602FC909403BF3BA7F79366DC6D6861960D4F75B2F8F92EB438",
    ),
    "MSG_PK/JP/msgdata.bin": (
        481_948,
        "6E2B883004545B2DD7D28360AFEED7D3BFDFEF2BF45E8333FD95CD0A49E95C70",
    ),
    "MSG_PK/JP/msgev.bin": (
        1_048_316,
        "D8BFACEB7422BEB3460EFC6B9509882759E6D5374A8B0AC41E920514FACC5BA4",
    ),
    "MSG_PK/JP/msggame.bin": (
        1_806_586,
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
    ),
}
# The upgrade is deliberately fail-closed over the full published v0.13.x
# resource vector.  These ten resources are retained byte-for-byte in v0.14.0
# but still prove that a mixed or unrelated installation is not upgraded.
RETAINED_RESOURCES: Mapping[str, tuple[int, str]] = {
    "MSG/JP/ev_strdata.bin": (
        928_131,
        "85CC7B26E2D9A159AABD71610A9694AD803CFADE8CCD12F1A082AE2A35E3FF45",
    ),
    "MSG_PK/JP/msgbre.bin": (
        484_068,
        "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    ),
    "MSG_PK/JP/msgire.bin": (
        23_128,
        "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    ),
    "MSG_PK/JP/msgstf.bin": (
        17_341,
        "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    ),
    "MSG_PK/JP/msgui.bin": (
        122_733,
        "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
    ),
    "RES_JP/res_lang.bin": (
        161_428_458,
        "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7",
    ),
    "RES_JP/res_lang_exp.bin": (
        13_796_051,
        "AC55622FC5C78ECA4ECFE37D1D890D5B26F6200ED7BAF1506B784541E158B7B7",
    ),
    "RES_JP_PK/res_lang_pk.bin": (
        141_893_576,
        "9019582ABBF88B08562B366E7D5A4283C6507455F86A801946AC32CCC25C2C2F",
    ),
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": (
        83_878_438,
        "F65383C72291D08B71EBA7E2EF504A8C674E7C4678445045868D98FCA5B0730D",
    ),
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": (
        67_623_137,
        "09531F21FA3BD56E2554C47942E47B5ACB61A7F279EFBF4AF85E4CAB963E4FAA",
    ),
}

# Direct-release contract.  The legacy declarations above describe the
# unpublished v0.13.x upgrader and are intentionally shadowed here.  Keeping
# the compatible parsing/rebuild helpers below lets this patcher use one
# fail-closed transaction for a pristine Steam JP 1.1.7 installation.
SCHEMA = "nobu16.resource-direct-patcher.v1"
STATE_SCHEMA = "nobu16.resource-direct-patcher.state.v1"
LEDGER_FILENAME = "v0.15.1-direct-resource-patch.json.gz"
BASELINE_RELEASES: tuple[str, ...] = ()
TEXT_RESOURCE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgui.bin",
)
BINARY_RESOURCE_PATHS = (
    "RES_JP/res_lang.bin",
    "RES_JP/res_lang_exp.bin",
    "RES_JP_PK/res_lang_pk.bin",
    "RES_JP_PK_PORT/res_lang_pk_port1.bin",
    "RES_JP_PK_PORT/res_lang_pk_port2.bin",
)
RESOURCE_PATHS = TEXT_RESOURCE_PATHS + BINARY_RESOURCE_PATHS
RESOURCE_KINDS = {
    "MSG/JP/ev_strdata.bin": "common_message_table",
    "MSG/JP/msggame.bin": "msggame_records",
    "MSG/JP/strdata.bin": "strdata_container",
    "MSG_PK/JP/msgbre.bin": "common_message_table",
    "MSG_PK/JP/msgdata.bin": "common_message_table",
    "MSG_PK/JP/msgev.bin": "common_message_table",
    "MSG_PK/JP/msggame.bin": "msggame_records",
    "MSG_PK/JP/msgire.bin": "common_message_table",
    "MSG_PK/JP/msgstf.bin": "common_message_table",
    "MSG_PK/JP/msgui.bin": "common_message_table",
    **{relative: "binary_bsdiff40" for relative in BINARY_RESOURCE_PATHS},
}
EXPECTED_OPERATION_COUNTS = {
    "MSG/JP/ev_strdata.bin": 13_090,
    "MSG/JP/msggame.bin": 16_473,
    "MSG/JP/strdata.bin": 25_954,
    "MSG_PK/JP/msgbre.bin": 2_217,
    "MSG_PK/JP/msgdata.bin": 24_786,
    "MSG_PK/JP/msgev.bin": 14_483,
    "MSG_PK/JP/msggame.bin": 19_026,
    "MSG_PK/JP/msgire.bin": 122,
    "MSG_PK/JP/msgstf.bin": 8,
    "MSG_PK/JP/msgui.bin": 4_150,
}
MAX_OPAQUE_RECORD_BYTES = 1_024
MAX_OPAQUE_RECORD_PAYLOAD_BYTES = 64 * 1_024
PREDECESSORS = {
    "MSG/JP/ev_strdata.bin": (496_819, "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB"),
    "MSG/JP/msggame.bin": (610_163, "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"),
    "MSG/JP/strdata.bin": (507_054, "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0"),
    "MSG_PK/JP/msgbre.bin": (221_127, "945A0E9157E2DBD12781FFA5A986D93681325F40B6486348B1AB311D3BEE1D6D"),
    "MSG_PK/JP/msgdata.bin": (272_453, "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E"),
    "MSG_PK/JP/msgev.bin": (562_226, "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84"),
    "MSG_PK/JP/msggame.bin": (721_304, "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"),
    "MSG_PK/JP/msgire.bin": (12_376, "0AFBFE11A380A9C98FB3B368092A05B39ABB6F80C4B0723AD3B6DB55C2559C5D"),
    "MSG_PK/JP/msgstf.bin": (6_841, "01EEB0B1B4879B6C70E9D7564F9D2FBD93E7B537CF8C614A58EEA82A83785A29"),
    "MSG_PK/JP/msgui.bin": (64_976, "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A"),
    "RES_JP/res_lang.bin": (153_198_542, "D32898C186CBDC7534692269C062E888ACE3B7A58F5DB4FEC8B0C745DADAAE53"),
    "RES_JP/res_lang_exp.bin": (13_226_270, "09DDC867E0B6F5A8210332C12F180A24A52C0B94D0AEE5E00E622CEA25A06D74"),
    "RES_JP_PK/res_lang_pk.bin": (140_729_547, "67CC064ED9D138B85255F8AA6AC5B5E47D7239E06E15A4E5AD68922274300EF5"),
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": (77_468_728, "1B44436B542F73B8B155A43F74D897F8D32C1C274D8C64B3CA9F4478BDB86022"),
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": (61_609_467, "52A8DE4BA1480E86218AC0CDE50DA946B4BCDFD7053ED85B94B04E663C00B380"),
}
TARGETS = {
    "MSG/JP/ev_strdata.bin": (928_131, "85CC7B26E2D9A159AABD71610A9694AD803CFADE8CCD12F1A082AE2A35E3FF45"),
    "MSG/JP/msggame.bin": (1_504_462, "3886D081E26AC2DEE75D8799CF839FEF2EFC6D27433FCD04C5FD43B4D23FD23A"),
    "MSG/JP/strdata.bin": (942_246, "C1B28E6EDF5E6602FC909403BF3BA7F79366DC6D6861960D4F75B2F8F92EB438"),
    "MSG_PK/JP/msgbre.bin": (484_068, "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939"),
    "MSG_PK/JP/msgdata.bin": (481_948, "6E2B883004545B2DD7D28360AFEED7D3BFDFEF2BF45E8333FD95CD0A49E95C70"),
    "MSG_PK/JP/msgev.bin": (1_048_316, "D8BFACEB7422BEB3460EFC6B9509882759E6D5374A8B0AC41E920514FACC5BA4"),
    "MSG_PK/JP/msggame.bin": (1_806_586, "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"),
    "MSG_PK/JP/msgire.bin": (23_128, "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB"),
    "MSG_PK/JP/msgstf.bin": (17_341, "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B"),
    "MSG_PK/JP/msgui.bin": (122_733, "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7"),
    "RES_JP/res_lang.bin": (161_428_458, "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"),
    "RES_JP/res_lang_exp.bin": (13_796_051, "AC55622FC5C78ECA4ECFE37D1D890D5B26F6200ED7BAF1506B784541E158B7B7"),
    "RES_JP_PK/res_lang_pk.bin": (141_893_576, "9019582ABBF88B08562B366E7D5A4283C6507455F86A801946AC32CCC25C2C2F"),
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": (83_878_438, "F65383C72291D08B71EBA7E2EF504A8C674E7C4678445045868D98FCA5B0730D"),
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": (67_623_137, "09531F21FA3BD56E2554C47942E47B5ACB61A7F279EFBF4AF85E4CAB963E4FAA"),
}
RETAINED_RESOURCES: Mapping[str, tuple[int, str]] = {}
BINARY_PATCH_FORMAT = "bsdiff40-bzip2"
MAX_BINARY_PATCH_BYTES = 40 * 1024 * 1024
MAX_BINARY_PATCH_FRACTION_NUMERATOR = 1
MAX_BINARY_PATCH_FRACTION_DENOMINATOR = 2
MAX_SMALL_BINARY_PATCH_BYTES = 16 * 1024


PROFILE_FILENAME = "v0.15.1-resource-profile.json"


def _release_profile_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / PROFILE_FILENAME
    return REPO / "release_payload" / VERSION / PROFILE_FILENAME


def _load_release_profile() -> Mapping[str, Any]:
    path = _release_profile_path()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot load the v0.15.1 resource profile: {path}") from exc
    if not isinstance(value, Mapping):
        raise RuntimeError("v0.15.1 resource profile is not an object")
    expected_keys = {
        "schema",
        "version",
        "text_resource_paths",
        "binary_resource_paths",
        "optional_resource_paths",
        "resource_kinds",
        "expected_operation_counts",
        "predecessors",
        "targets",
    }
    if set(value) != expected_keys:
        raise RuntimeError("v0.15.1 resource profile keys differ")
    if value.get("schema") != "nobu16.kr.resource-profile.v0.15.1" or value.get("version") != VERSION:
        raise RuntimeError("v0.15.1 resource profile identity differs")
    return value


def _profile_pin_map(value: object, paths: Sequence[str], label: str) -> dict[str, tuple[int, str]]:
    if not isinstance(value, Mapping) or set(value) != set(paths):
        raise RuntimeError(f"v0.15.1 {label} profile paths differ")
    result: dict[str, tuple[int, str]] = {}
    for relative in paths:
        spec = value[relative]
        if not isinstance(spec, Mapping) or set(spec) != {"size", "sha256"}:
            raise RuntimeError(f"v0.15.1 {label} profile is malformed: {relative}")
        size = spec.get("size")
        digest = spec.get("sha256")
        if (
            isinstance(size, bool)
            or not isinstance(size, int)
            or size < 0
            or not isinstance(digest, str)
            or len(digest) != 64
        ):
            raise RuntimeError(f"v0.15.1 {label} profile is malformed: {relative}")
        try:
            int(digest, 16)
        except ValueError as exc:
            raise RuntimeError(f"v0.15.1 {label} profile hash is malformed: {relative}") from exc
        result[relative] = (size, digest.upper())
    return result


_PROFILE = _load_release_profile()
TEXT_RESOURCE_PATHS = tuple(str(path) for path in _PROFILE["text_resource_paths"])
BINARY_RESOURCE_PATHS = tuple(str(path) for path in _PROFILE["binary_resource_paths"])
RESOURCE_PATHS = TEXT_RESOURCE_PATHS + BINARY_RESOURCE_PATHS
if len(set(RESOURCE_PATHS)) != len(RESOURCE_PATHS):
    raise RuntimeError("v0.15.1 resource profile contains duplicate paths")
OPTIONAL_RESOURCE_PATHS = frozenset(str(path) for path in _PROFILE["optional_resource_paths"])
if not OPTIONAL_RESOURCE_PATHS.issubset(BINARY_RESOURCE_PATHS):
    raise RuntimeError("v0.15.1 optional-resource paths differ")
MANDATORY_RESOURCE_PATHS = tuple(path for path in RESOURCE_PATHS if path not in OPTIONAL_RESOURCE_PATHS)
RESOURCE_KINDS = {str(path): str(kind) for path, kind in _PROFILE["resource_kinds"].items()}
if set(RESOURCE_KINDS) != set(RESOURCE_PATHS):
    raise RuntimeError("v0.15.1 resource-kind paths differ")
EXPECTED_OPERATION_COUNTS = {
    str(path): int(count) for path, count in _PROFILE["expected_operation_counts"].items()
}
if set(EXPECTED_OPERATION_COUNTS) != set(TEXT_RESOURCE_PATHS):
    raise RuntimeError("v0.15.1 text operation-count paths differ")
PREDECESSORS = _profile_pin_map(_PROFILE["predecessors"], RESOURCE_PATHS, "predecessor")
TARGETS = _profile_pin_map(_PROFILE["targets"], RESOURCE_PATHS, "target")

ATTRIBUTION_BANNER = r"""
================================================================
 ____   ____ ___ _   _ ____ ___ ____  _____
|  _ \ / ___|_ _| \ | / ___|_ _|  _ \| ____|
| | | | |    | ||  \| \___ \| || | | |  _|
| |_| | |___ | || |\  |___) | || |_| | |___
|____/ \____|___|_| \_|____/___|____/|_____|
================================================================
제작: 디시인사이드 신장의야망 갤러리
      parsifal
GitHub: https://github.com/parsifal295/nobu16-korean-patch
================================================================
""".strip("\n")

class PatcherError(RuntimeError):
    """Raised for a fail-closed resource-patcher condition."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def file_spec(blob: bytes) -> dict[str, object]:
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def require_spec(blob: bytes, expected: Mapping[str, object], label: str) -> None:
    actual = file_spec(blob)
    if actual != {"size": int(expected["size"]), "sha256": str(expected["sha256"]).upper()}:
        raise PatcherError(
            f"{label} differs: size={actual['size']} sha256={actual['sha256']}"
        )


def pin_spec(pin: tuple[int, str]) -> dict[str, object]:
    return {"size": pin[0], "sha256": pin[1]}


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def ordinary_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        not value
        or value != path.as_posix()
        or path.is_absolute()
        or ".." in path.parts
        or any(":" in part for part in path.parts)
        # Top-level resource archives such as RES_JP/res_lang.bin have two
        # components.  All accepted paths are still pinned by the ledger, so
        # do not reject those legitimate retained-resource paths here.
        or len(path.parts) < 2
    ):
        raise PatcherError(f"non-canonical resource path: {value!r}")
    return path


def game_path(root: Path, relative: str) -> Path:
    relative_path = ordinary_relative_path(relative)
    root = root.resolve(strict=True)
    candidate = (root / Path(relative_path)).resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PatcherError(f"resource path escapes game root: {relative}") from exc
    if not candidate.is_file():
        raise PatcherError(f"missing resource: {relative}")
    return candidate


def ensure_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PatcherError(f"{label} is not an object")
    return value


def ensure_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise PatcherError(f"{label} is not an array")
    return value


def ensure_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PatcherError(f"{label} is not a non-negative integer")
    return value


def ensure_hash(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise PatcherError(f"{label} is not a SHA-256")
    value = value.upper()
    try:
        int(value, 16)
    except ValueError as exc:
        raise PatcherError(f"{label} is not a SHA-256") from exc
    return value


def make_common_resource(relative: str, predecessor: bytes, target: bytes) -> dict[str, object]:
    _pre_header, predecessor_raw = decompress_wrapper(predecessor)
    _target_header, target_raw = decompress_wrapper(target)
    predecessor_table = parse_message_table(predecessor_raw)
    target_table = parse_message_table(target_raw)
    if predecessor_table.string_count != target_table.string_count:
        raise PatcherError(f"{relative} string count differs across the upgrade")
    operations: list[dict[str, object]] = []
    for entry_id, (before, after) in enumerate(
        zip(predecessor_table.texts, target_table.texts, strict=True)
    ):
        if before != after:
            operations.append(
                {
                    "id": entry_id,
                    "source_utf16le_sha256": text_hash(before),
                    "replacement": after,
                    "replacement_utf16le_sha256": text_hash(after),
                }
            )
    resource = {
        "path": relative,
        "kind": "common_message_table",
        "predecessor": {
            **file_spec(predecessor),
            "raw_size": len(predecessor_raw),
            "raw_sha256": sha256_bytes(predecessor_raw),
            "string_count": predecessor_table.string_count,
        },
        "target": {
            **file_spec(target),
            "raw_size": len(target_raw),
            "raw_sha256": sha256_bytes(target_raw),
            "string_count": target_table.string_count,
        },
        "operation_count": len(operations),
        "operations": operations,
    }
    rebuilt = apply_common_resource(predecessor, resource)
    if rebuilt != target:
        raise PatcherError(f"{relative} operation ledger does not rebuild its target")
    return resource


def make_strdata_resource(relative: str, predecessor: bytes, target: bytes) -> dict[str, object]:
    _pre_header, predecessor_raw = decompress_wrapper(predecessor)
    _target_header, target_raw = decompress_wrapper(target)
    predecessor_table = parse_strdata(predecessor_raw)
    target_table = parse_strdata(target_raw)
    if len(predecessor_table.blocks) != len(target_table.blocks):
        raise PatcherError(f"{relative} block count differs across the upgrade")
    operations: list[dict[str, object]] = []
    for before_block, after_block in zip(
        predecessor_table.blocks, target_table.blocks, strict=True
    ):
        if before_block.slot_count != after_block.slot_count:
            raise PatcherError(f"{relative} block {before_block.block_id} slot count differs")
        for slot_id, (before, after) in enumerate(
            zip(before_block.texts, after_block.texts, strict=True)
        ):
            if before != after:
                operations.append(
                    {
                        "block_id": before_block.block_id,
                        "slot_id": slot_id,
                        "source_utf16le_sha256": text_hash(before),
                        "replacement": after,
                        "replacement_utf16le_sha256": text_hash(after),
                    }
                )
    resource = {
        "path": relative,
        "kind": "strdata_container",
        "predecessor": {
            **file_spec(predecessor),
            "raw_size": len(predecessor_raw),
            "raw_sha256": sha256_bytes(predecessor_raw),
            "block_slot_counts": [block.slot_count for block in predecessor_table.blocks],
        },
        "target": {
            **file_spec(target),
            "raw_size": len(target_raw),
            "raw_sha256": sha256_bytes(target_raw),
            "block_slot_counts": [block.slot_count for block in target_table.blocks],
        },
        "operation_count": len(operations),
        "operations": operations,
    }
    rebuilt = apply_strdata_resource(predecessor, resource)
    if rebuilt != target:
        raise PatcherError(f"{relative} operation ledger does not rebuild its target")
    return resource


def opaque_skeleton(record: Any) -> bytes:
    cursor = 0
    result: list[bytes] = []
    for literal in MSGGAME.parse_record_literals(record):
        result.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    result.append(record.data[cursor:])
    return b"".join(result)


def make_msggame_resource(relative: str, predecessor: bytes, target: bytes) -> dict[str, object]:
    predecessor_archive = MSGGAME.parse_packed_msggame(predecessor).archive
    target_archive = MSGGAME.parse_packed_msggame(target).archive
    predecessor_blocks = [(block.block_id, len(block.records)) for block in predecessor_archive.blocks]
    target_blocks = [(block.block_id, len(block.records)) for block in target_archive.blocks]
    if predecessor_blocks != target_blocks:
        raise PatcherError(f"{relative} block/record topology differs across the upgrade")
    operations: list[dict[str, object]] = []
    for predecessor_block, target_block in zip(
        predecessor_archive.blocks, target_archive.blocks, strict=True
    ):
        for predecessor_record, target_record in zip(
            predecessor_block.records, target_block.records, strict=True
        ):
            if predecessor_record.data == target_record.data:
                continue
            predecessor_literals = MSGGAME.parse_record_literals(predecessor_record)
            target_literals = MSGGAME.parse_record_literals(target_record)
            literal_mode = (
                len(predecessor_literals) == len(target_literals)
                and opaque_skeleton(predecessor_record) == opaque_skeleton(target_record)
            )
            operation: dict[str, object] = {
                "block_id": predecessor_block.block_id,
                "record_id": predecessor_record.record_id,
                "source_record_sha256": sha256_bytes(predecessor_record.data),
                "target_record_sha256": sha256_bytes(target_record.data),
            }
            if literal_mode:
                literals: list[dict[str, object]] = []
                for before, after in zip(predecessor_literals, target_literals, strict=True):
                    if before.text != after.text:
                        literals.append(
                            {
                                "literal_id": before.literal_id,
                                "source_utf16le_sha256": text_hash(before.text),
                                "replacement": after.text,
                                "replacement_utf16le_sha256": text_hash(after.text),
                            }
                        )
                if not literals:
                    raise PatcherError(
                        f"{relative} record {predecessor_block.block_id}:{predecessor_record.record_id} has no literal delta"
                    )
                operation["mode"] = "literals"
                operation["literals"] = literals
            else:
                operation["mode"] = "record_bytes"
                operation["target_record_base64"] = base64.b64encode(
                    target_record.data
                ).decode("ascii")
            operations.append(operation)
    _pre_header, predecessor_raw = decompress_wrapper(predecessor)
    _target_header, target_raw = decompress_wrapper(target)
    resource = {
        "path": relative,
        "kind": "msggame_records",
        "predecessor": {
            **file_spec(predecessor),
            "raw_size": len(predecessor_raw),
            "raw_sha256": sha256_bytes(predecessor_raw),
            "block_record_counts": [list(item) for item in predecessor_blocks],
        },
        "target": {
            **file_spec(target),
            "raw_size": len(target_raw),
            "raw_sha256": sha256_bytes(target_raw),
            "block_record_counts": [list(item) for item in target_blocks],
        },
        "operation_count": len(operations),
        "operations": operations,
    }
    rebuilt = apply_msggame_resource(predecessor, resource)
    if rebuilt != target:
        raise PatcherError(f"{relative} operation ledger does not rebuild its target")
    return resource


def read_baseline_zip(path: Path, relative: str) -> bytes:
    with zipfile.ZipFile(path, "r") as archive:
        try:
            return archive.read(relative)
        except KeyError as exc:
            raise PatcherError(f"baseline ZIP is missing {relative}") from exc


def build_ledger(baseline_zip: Path, game_root: Path) -> dict[str, object]:
    baseline_zip = baseline_zip.resolve(strict=True)
    game_root = game_root.resolve(strict=True)
    if not zipfile.is_zipfile(baseline_zip):
        raise PatcherError(f"baseline is not a ZIP: {baseline_zip}")
    for relative, pin in RETAINED_RESOURCES.items():
        require_spec(
            game_path(game_root, relative).read_bytes(),
            pin_spec(pin),
            f"target retained {relative}",
        )
    resources: list[dict[str, object]] = []
    for relative in RESOURCE_PATHS:
        predecessor = read_baseline_zip(baseline_zip, relative)
        target_path = game_path(game_root, relative)
        target = target_path.read_bytes()
        require_spec(predecessor, pin_spec(PREDECESSORS[relative]), f"baseline {relative}")
        require_spec(target, pin_spec(TARGETS[relative]), f"target {relative}")
        if relative.endswith("strdata.bin"):
            resources.append(make_strdata_resource(relative, predecessor, target))
        elif relative.endswith("msggame.bin"):
            resources.append(make_msggame_resource(relative, predecessor, target))
        else:
            resources.append(make_common_resource(relative, predecessor, target))
    operation_counts = {resource["path"]: resource["operation_count"] for resource in resources}
    ledger: dict[str, object] = {
        "schema": SCHEMA,
        "release": VERSION,
        "baseline_releases": list(BASELINE_RELEASES),
        "resource_count": len(resources),
        "resources": resources,
        "retained_resource_count": len(RETAINED_RESOURCES),
        "retained_resources": [
            {"path": relative, "spec": pin_spec(pin)}
            for relative, pin in sorted(RETAINED_RESOURCES.items())
        ],
        "operation_counts": operation_counts,
        "payload_policy": {
            "contains_complete_game_resources": False,
            "contains_game_executable": False,
            "process_memory_access": False,
            "requires_installed_predecessor_resources": True,
            "predecessor_full_resources_stored": False,
            "opaque_target_records_may_include_context": True,
        },
    }
    verify_ledger(ledger)
    return ledger


def write_ledger(path: Path, ledger: Mapping[str, object]) -> None:
    verify_ledger(ledger)
    atomic_write(path, canonical_json(ledger))


def parse_file_spec(value: object, label: str) -> dict[str, object]:
    mapping = ensure_mapping(value, label)
    if not {"size", "sha256"}.issubset(mapping):
        raise PatcherError(f"{label} is missing file-size metadata")
    return {
        "size": ensure_int(mapping.get("size"), f"{label} size"),
        "sha256": ensure_hash(mapping.get("sha256"), f"{label} SHA-256"),
    }


def ensure_exact_keys(
    value: Mapping[str, Any], expected: set[str], label: str
) -> None:
    actual = set(value)
    if actual != expected:
        unexpected = sorted(str(key) for key in actual - expected)
        missing = sorted(expected - actual)
        details: list[str] = []
        if unexpected:
            details.append(f"unknown={unexpected}")
        if missing:
            details.append(f"missing={missing}")
        raise PatcherError(f"{label} schema differs ({', '.join(details)})")


def verify_raw_metadata(
    value: object, label: str, *, metadata_key: str
) -> Mapping[str, Any]:
    mapping = ensure_mapping(value, label)
    ensure_exact_keys(
        mapping,
        {"size", "sha256", "raw_size", "raw_sha256", metadata_key},
        label,
    )
    parse_file_spec(mapping, label)
    ensure_int(mapping.get("raw_size"), f"{label} raw size")
    ensure_hash(mapping.get("raw_sha256"), f"{label} raw SHA-256")
    metadata = mapping.get(metadata_key)
    if metadata_key == "string_count":
        ensure_int(metadata, f"{label} string count")
    else:
        values = ensure_list(metadata, f"{label} {metadata_key}")
        for index, item in enumerate(values):
            if metadata_key == "block_record_counts":
                pair = ensure_list(item, f"{label} {metadata_key}[{index}]")
                if len(pair) != 2:
                    raise PatcherError(f"{label} {metadata_key}[{index}] differs")
                ensure_int(pair[0], f"{label} block id")
                ensure_int(pair[1], f"{label} record count")
            else:
                ensure_int(item, f"{label} {metadata_key}[{index}]")
    return mapping


def parse_resource_specs(resource: Mapping[str, Any]) -> tuple[str, dict[str, object], dict[str, object]]:
    relative = resource.get("path")
    if not isinstance(relative, str) or relative not in RESOURCE_PATHS:
        raise PatcherError(f"invalid resource path: {relative!r}")
    predecessor = parse_file_spec(resource.get("predecessor"), f"{relative} predecessor")
    target = parse_file_spec(resource.get("target"), f"{relative} target")
    if predecessor != pin_spec(PREDECESSORS[relative]):
        raise PatcherError(f"{relative} predecessor profile differs")
    if target != pin_spec(TARGETS[relative]):
        raise PatcherError(f"{relative} target profile differs")
    return relative, predecessor, target


def verify_text_operation(
    operation: Mapping[str, Any], label: str, *, coordinate_keys: set[str]
) -> None:
    expected = coordinate_keys | {
        "source_utf16le_sha256",
        "replacement",
        "replacement_utf16le_sha256",
    }
    ensure_exact_keys(operation, expected, label)
    for key in coordinate_keys:
        ensure_int(operation.get(key), f"{label} {key}")
    ensure_hash(operation.get("source_utf16le_sha256"), f"{label} source hash")
    replacement = operation.get("replacement")
    if not isinstance(replacement, str) or "\x00" in replacement:
        raise PatcherError(f"{label} replacement is invalid")
    replacement_hash = ensure_hash(
        operation.get("replacement_utf16le_sha256"), f"{label} replacement hash"
    )
    if text_hash(replacement) != replacement_hash:
        raise PatcherError(f"{label} replacement hash differs")


def verify_operations(resource: Mapping[str, Any], relative: str, kind: str) -> int:
    operations = ensure_list(resource.get("operations"), f"{relative} operations")
    count = ensure_int(resource.get("operation_count"), f"{relative} operation count")
    if count != len(operations) or count != EXPECTED_OPERATION_COUNTS[relative]:
        raise PatcherError(f"{relative} operation count differs")
    seen: set[object] = set()
    opaque_payload_bytes = 0
    for index, raw in enumerate(operations):
        operation = ensure_mapping(raw, f"{relative} operation {index}")
        label = f"{relative} operation {index}"
        if kind == "common_message_table":
            verify_text_operation(operation, label, coordinate_keys={"id"})
            coordinate: object = operation["id"]
        elif kind == "strdata_container":
            verify_text_operation(operation, label, coordinate_keys={"block_id", "slot_id"})
            coordinate = (operation["block_id"], operation["slot_id"])
        else:
            base_keys = {
                "block_id",
                "record_id",
                "source_record_sha256",
                "target_record_sha256",
                "mode",
            }
            mode = operation.get("mode")
            if mode == "record_bytes":
                ensure_exact_keys(operation, base_keys | {"target_record_base64"}, label)
            elif mode == "literals":
                ensure_exact_keys(operation, base_keys | {"literals"}, label)
            else:
                raise PatcherError(f"{label} mode is invalid")
            ensure_int(operation.get("block_id"), f"{label} block id")
            ensure_int(operation.get("record_id"), f"{label} record id")
            ensure_hash(operation.get("source_record_sha256"), f"{label} source record hash")
            target_record_hash = ensure_hash(
                operation.get("target_record_sha256"), f"{label} target record hash"
            )
            coordinate = (operation["block_id"], operation["record_id"])
            if mode == "record_bytes":
                encoded = operation.get("target_record_base64")
                if not isinstance(encoded, str):
                    raise PatcherError(f"{label} record payload is invalid")
                try:
                    decoded = base64.b64decode(encoded.encode("ascii"), validate=True)
                except (UnicodeEncodeError, ValueError) as exc:
                    raise PatcherError(f"{label} record payload is malformed") from exc
                if not decoded or len(decoded) > MAX_OPAQUE_RECORD_BYTES:
                    raise PatcherError(f"{label} record payload size differs")
                if sha256_bytes(decoded) != target_record_hash:
                    raise PatcherError(f"{label} record payload hash differs")
                opaque_payload_bytes += len(decoded)
            else:
                literals = ensure_list(operation.get("literals"), f"{label} literals")
                if not literals:
                    raise PatcherError(f"{label} literals are empty")
                literal_seen: set[int] = set()
                for literal_index, raw_literal in enumerate(literals):
                    literal = ensure_mapping(raw_literal, f"{label} literal {literal_index}")
                    verify_text_operation(
                        literal,
                        f"{label} literal {literal_index}",
                        coordinate_keys={"literal_id"},
                    )
                    literal_id = literal["literal_id"]
                    if literal_id in literal_seen:
                        raise PatcherError(f"{label} duplicate literal id")
                    literal_seen.add(literal_id)
        if coordinate in seen:
            raise PatcherError(f"{label} duplicate coordinate")
        seen.add(coordinate)
    if opaque_payload_bytes > MAX_OPAQUE_RECORD_PAYLOAD_BYTES:
        raise PatcherError(f"{relative} opaque payload budget differs")
    return opaque_payload_bytes


def verify_ledger(value: object) -> dict[str, Any]:
    ledger = dict(ensure_mapping(value, "ledger"))
    ensure_exact_keys(
        ledger,
        {
            "schema",
            "release",
            "baseline_releases",
            "resource_count",
            "resources",
            "retained_resource_count",
            "retained_resources",
            "operation_counts",
            "payload_policy",
        },
        "ledger",
    )
    if ledger.get("schema") != SCHEMA or ledger.get("release") != VERSION:
        raise PatcherError("unsupported resource-patcher ledger")
    baseline_releases = ensure_list(ledger.get("baseline_releases"), "baseline releases")
    if tuple(baseline_releases) != BASELINE_RELEASES:
        raise PatcherError("baseline release contract differs")
    resources = ensure_list(ledger.get("resources"), "resources")
    if len(resources) != len(RESOURCE_PATHS) or ledger.get("resource_count") != len(resources):
        raise PatcherError("resource count differs")
    by_path: dict[str, Mapping[str, Any]] = {}
    opaque_payload_bytes = 0
    for raw in resources:
        resource = ensure_mapping(raw, "resource")
        ensure_exact_keys(
            resource,
            {"path", "kind", "predecessor", "target", "operation_count", "operations"},
            "resource",
        )
        relative, _predecessor, _target = parse_resource_specs(resource)
        if relative in by_path:
            raise PatcherError(f"duplicate resource in ledger: {relative}")
        kind = resource.get("kind")
        if kind != RESOURCE_KINDS[relative]:
            raise PatcherError(f"{relative} resource kind differs")
        metadata_key = {
            "common_message_table": "string_count",
            "strdata_container": "block_slot_counts",
            "msggame_records": "block_record_counts",
        }[kind]
        verify_raw_metadata(resource["predecessor"], f"{relative} predecessor", metadata_key=metadata_key)
        verify_raw_metadata(resource["target"], f"{relative} target", metadata_key=metadata_key)
        opaque_payload_bytes += verify_operations(resource, relative, kind)
        by_path[relative] = resource
    if tuple(sorted(by_path)) != tuple(sorted(RESOURCE_PATHS)):
        raise PatcherError("resource vector differs")
    if opaque_payload_bytes > MAX_OPAQUE_RECORD_PAYLOAD_BYTES:
        raise PatcherError("opaque payload budget differs")
    retained = ensure_list(ledger.get("retained_resources"), "retained resources")
    if ledger.get("retained_resource_count") != len(retained) or len(retained) != len(RETAINED_RESOURCES):
        raise PatcherError("retained resource count differs")
    retained_by_path: dict[str, dict[str, object]] = {}
    for raw in retained:
        item = ensure_mapping(raw, "retained resource")
        ensure_exact_keys(item, {"path", "spec"}, "retained resource")
        relative = item.get("path")
        if not isinstance(relative, str) or relative not in RETAINED_RESOURCES or relative in retained_by_path:
            raise PatcherError(f"invalid retained resource: {relative!r}")
        spec_value = ensure_mapping(item.get("spec"), f"retained {relative}")
        ensure_exact_keys(spec_value, {"size", "sha256"}, f"retained {relative}")
        spec = parse_file_spec(spec_value, f"retained {relative}")
        if spec != pin_spec(RETAINED_RESOURCES[relative]):
            raise PatcherError(f"retained resource pin differs: {relative}")
        retained_by_path[relative] = spec
    if tuple(sorted(retained_by_path)) != tuple(sorted(RETAINED_RESOURCES)):
        raise PatcherError("retained resource vector differs")
    operation_counts = ensure_mapping(ledger.get("operation_counts"), "operation counts")
    ensure_exact_keys(operation_counts, set(RESOURCE_PATHS), "operation counts")
    for relative in RESOURCE_PATHS:
        if ensure_int(operation_counts.get(relative), f"{relative} operation count") != EXPECTED_OPERATION_COUNTS[relative]:
            raise PatcherError(f"{relative} operation count map differs")
    if dict(operation_counts) != {path: by_path[path]["operation_count"] for path in RESOURCE_PATHS}:
        raise PatcherError("operation count map differs")
    policy = ensure_mapping(ledger.get("payload_policy"), "payload policy")
    expected_policy = {
        "contains_complete_game_resources": False,
        "contains_game_executable": False,
        "process_memory_access": False,
        "requires_installed_predecessor_resources": True,
        "predecessor_full_resources_stored": False,
        "opaque_target_records_may_include_context": True,
    }
    if dict(policy) != expected_policy:
        raise PatcherError("payload policy differs")
    return ledger


def apply_common_resource(source: bytes, resource: Mapping[str, Any]) -> bytes:
    relative, predecessor, target = parse_resource_specs(resource)
    require_spec(source, predecessor, f"installed {relative}")
    _header, raw = decompress_wrapper(source)
    if len(raw) != ensure_int(resource["predecessor"].get("raw_size"), f"{relative} predecessor raw size"):
        raise PatcherError(f"{relative} predecessor raw size differs")
    if sha256_bytes(raw) != ensure_hash(resource["predecessor"].get("raw_sha256"), f"{relative} predecessor raw SHA-256"):
        raise PatcherError(f"{relative} predecessor raw hash differs")
    table = parse_message_table(raw)
    count = ensure_int(resource["predecessor"].get("string_count"), f"{relative} string count")
    if table.string_count != count:
        raise PatcherError(f"{relative} string count differs")
    texts = list(table.texts)
    seen: set[int] = set()
    for raw_operation in ensure_list(resource.get("operations"), f"{relative} operations"):
        operation = ensure_mapping(raw_operation, f"{relative} operation")
        entry_id = ensure_int(operation.get("id"), f"{relative} operation id")
        if entry_id >= len(texts) or entry_id in seen:
            raise PatcherError(f"{relative} operation id is invalid: {entry_id}")
        seen.add(entry_id)
        before = texts[entry_id]
        if text_hash(before) != ensure_hash(
            operation.get("source_utf16le_sha256"), f"{relative} operation {entry_id} source hash"
        ):
            raise PatcherError(f"{relative} source text differs at {entry_id}")
        replacement = operation.get("replacement")
        if not isinstance(replacement, str) or "\x00" in replacement:
            raise PatcherError(f"{relative} replacement is invalid at {entry_id}")
        if text_hash(replacement) != ensure_hash(
            operation.get("replacement_utf16le_sha256"), f"{relative} operation {entry_id} replacement hash"
        ):
            raise PatcherError(f"{relative} replacement hash differs at {entry_id}")
        texts[entry_id] = replacement
    rebuilt_raw = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise PatcherError(f"{relative} rebuilt message table differs")
    target_mapping = ensure_mapping(resource["target"], f"{relative} target")
    if len(rebuilt_raw) != ensure_int(target_mapping.get("raw_size"), f"{relative} target raw size"):
        raise PatcherError(f"{relative} target raw size differs")
    if sha256_bytes(rebuilt_raw) != ensure_hash(target_mapping.get("raw_sha256"), f"{relative} target raw SHA-256"):
        raise PatcherError(f"{relative} target raw hash differs")
    candidate = recompress_wrapper(rebuilt_raw, source)
    require_spec(candidate, target, f"rebuilt {relative}")
    return candidate


def apply_strdata_resource(source: bytes, resource: Mapping[str, Any]) -> bytes:
    relative, predecessor, target = parse_resource_specs(resource)
    require_spec(source, predecessor, f"installed {relative}")
    _header, raw = decompress_wrapper(source)
    predecessor_mapping = ensure_mapping(resource["predecessor"], f"{relative} predecessor")
    if len(raw) != ensure_int(predecessor_mapping.get("raw_size"), f"{relative} predecessor raw size"):
        raise PatcherError(f"{relative} predecessor raw size differs")
    if sha256_bytes(raw) != ensure_hash(predecessor_mapping.get("raw_sha256"), f"{relative} predecessor raw SHA-256"):
        raise PatcherError(f"{relative} predecessor raw hash differs")
    container = parse_strdata(raw)
    expected_counts = predecessor_mapping.get("block_slot_counts")
    if expected_counts != [block.slot_count for block in container.blocks]:
        raise PatcherError(f"{relative} predecessor block counts differ")
    replacements: dict[int, list[str]] = {}
    seen: set[tuple[int, int]] = set()
    for raw_operation in ensure_list(resource.get("operations"), f"{relative} operations"):
        operation = ensure_mapping(raw_operation, f"{relative} operation")
        block_id = ensure_int(operation.get("block_id"), f"{relative} block id")
        slot_id = ensure_int(operation.get("slot_id"), f"{relative} slot id")
        coordinate = (block_id, slot_id)
        if coordinate in seen or block_id >= len(container.blocks) or slot_id >= container.blocks[block_id].slot_count:
            raise PatcherError(f"{relative} operation coordinate is invalid: {coordinate}")
        seen.add(coordinate)
        values = replacements.setdefault(block_id, list(container.blocks[block_id].texts))
        before = values[slot_id]
        if text_hash(before) != ensure_hash(
            operation.get("source_utf16le_sha256"), f"{relative} operation {coordinate} source hash"
        ):
            raise PatcherError(f"{relative} source text differs at {coordinate}")
        replacement = operation.get("replacement")
        if not isinstance(replacement, str) or "\x00" in replacement:
            raise PatcherError(f"{relative} replacement is invalid at {coordinate}")
        if text_hash(replacement) != ensure_hash(
            operation.get("replacement_utf16le_sha256"), f"{relative} operation {coordinate} replacement hash"
        ):
            raise PatcherError(f"{relative} replacement hash differs at {coordinate}")
        values[slot_id] = replacement
    rebuilt_raw = rebuild_strdata(container, replacements)
    target_mapping = ensure_mapping(resource["target"], f"{relative} target")
    if len(rebuilt_raw) != ensure_int(target_mapping.get("raw_size"), f"{relative} target raw size"):
        raise PatcherError(f"{relative} target raw size differs")
    if sha256_bytes(rebuilt_raw) != ensure_hash(target_mapping.get("raw_sha256"), f"{relative} target raw SHA-256"):
        raise PatcherError(f"{relative} target raw hash differs")
    candidate = recompress_wrapper(rebuilt_raw, source)
    require_spec(candidate, target, f"rebuilt {relative}")
    return candidate


def apply_msggame_resource(source: bytes, resource: Mapping[str, Any]) -> bytes:
    relative, predecessor, target = parse_resource_specs(resource)
    require_spec(source, predecessor, f"installed {relative}")
    _header, raw = decompress_wrapper(source)
    predecessor_mapping = ensure_mapping(resource["predecessor"], f"{relative} predecessor")
    if len(raw) != ensure_int(predecessor_mapping.get("raw_size"), f"{relative} predecessor raw size"):
        raise PatcherError(f"{relative} predecessor raw size differs")
    if sha256_bytes(raw) != ensure_hash(predecessor_mapping.get("raw_sha256"), f"{relative} predecessor raw SHA-256"):
        raise PatcherError(f"{relative} predecessor raw hash differs")
    archive = MSGGAME.parse_packed_msggame(source).archive
    block_counts = [(block.block_id, len(block.records)) for block in archive.blocks]
    if predecessor_mapping.get("block_record_counts") != [list(item) for item in block_counts]:
        # JSON turns tuples into lists; this explicit check avoids accepting a
        # similar-looking archive with a different block identity.
        raise PatcherError(f"{relative} predecessor block/record topology differs")
    records = {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }
    replacements: dict[tuple[int, int], bytes] = {}
    seen: set[tuple[int, int]] = set()
    for raw_operation in ensure_list(resource.get("operations"), f"{relative} operations"):
        operation = ensure_mapping(raw_operation, f"{relative} operation")
        coordinate = (
            ensure_int(operation.get("block_id"), f"{relative} block id"),
            ensure_int(operation.get("record_id"), f"{relative} record id"),
        )
        if coordinate in seen or coordinate not in records:
            raise PatcherError(f"{relative} record coordinate is invalid: {coordinate}")
        seen.add(coordinate)
        record = records[coordinate]
        if sha256_bytes(record.data) != ensure_hash(
            operation.get("source_record_sha256"), f"{relative} record {coordinate} source hash"
        ):
            raise PatcherError(f"{relative} source record differs at {coordinate}")
        mode = operation.get("mode")
        if mode == "record_bytes":
            encoded = operation.get("target_record_base64")
            if not isinstance(encoded, str):
                raise PatcherError(f"{relative} target record is absent at {coordinate}")
            try:
                replacement = base64.b64decode(encoded.encode("ascii"), validate=True)
            except (UnicodeEncodeError, ValueError) as exc:
                raise PatcherError(f"{relative} target record is malformed at {coordinate}") from exc
        elif mode == "literals":
            literals = MSGGAME.parse_record_literals(record)
            literal_replacements: dict[int, str] = {}
            literal_seen: set[int] = set()
            for raw_literal in ensure_list(operation.get("literals"), f"{relative} literals"):
                literal = ensure_mapping(raw_literal, f"{relative} literal")
                literal_id = ensure_int(literal.get("literal_id"), f"{relative} literal id")
                if literal_id in literal_seen or literal_id >= len(literals):
                    raise PatcherError(f"{relative} literal id is invalid at {coordinate}:{literal_id}")
                literal_seen.add(literal_id)
                before = literals[literal_id].text
                if text_hash(before) != ensure_hash(
                    literal.get("source_utf16le_sha256"), f"{relative} literal source hash"
                ):
                    raise PatcherError(f"{relative} source literal differs at {coordinate}:{literal_id}")
                replacement_text = literal.get("replacement")
                if not isinstance(replacement_text, str) or "\x00" in replacement_text:
                    raise PatcherError(f"{relative} literal replacement is invalid at {coordinate}:{literal_id}")
                if text_hash(replacement_text) != ensure_hash(
                    literal.get("replacement_utf16le_sha256"), f"{relative} literal replacement hash"
                ):
                    raise PatcherError(f"{relative} literal replacement hash differs at {coordinate}:{literal_id}")
                literal_replacements[literal_id] = replacement_text
            if not literal_replacements:
                raise PatcherError(f"{relative} literal operation is empty at {coordinate}")
            replacement = MSGGAME.rebuild_record_literals(record, literal_replacements)
        else:
            raise PatcherError(f"{relative} operation mode is invalid at {coordinate}")
        if sha256_bytes(replacement) != ensure_hash(
            operation.get("target_record_sha256"), f"{relative} record {coordinate} target hash"
        ):
            raise PatcherError(f"{relative} rebuilt record differs at {coordinate}")
        replacements[coordinate] = replacement
    rebuilt_raw = MSGGAME.rebuild_raw_msggame(archive, replacements)
    target_mapping = ensure_mapping(resource["target"], f"{relative} target")
    if len(rebuilt_raw) != ensure_int(target_mapping.get("raw_size"), f"{relative} target raw size"):
        raise PatcherError(f"{relative} target raw size differs")
    if sha256_bytes(rebuilt_raw) != ensure_hash(target_mapping.get("raw_sha256"), f"{relative} target raw SHA-256"):
        raise PatcherError(f"{relative} target raw hash differs")
    candidate = recompress_wrapper(rebuilt_raw, source)
    require_spec(candidate, target, f"rebuilt {relative}")
    return candidate


def build_candidates(game_root: Path, ledger: Mapping[str, Any]) -> dict[str, bytes]:
    candidates: dict[str, bytes] = {}
    for resource in ensure_list(ledger.get("resources"), "resources"):
        item = ensure_mapping(resource, "resource")
        relative, predecessor, _target = parse_resource_specs(item)
        source = game_path(game_root, relative).read_bytes()
        require_spec(source, predecessor, f"installed {relative}")
        kind = item.get("kind")
        if kind == "common_message_table":
            candidates[relative] = apply_common_resource(source, item)
        elif kind == "strdata_container":
            candidates[relative] = apply_strdata_resource(source, item)
        elif kind == "msggame_records":
            candidates[relative] = apply_msggame_resource(source, item)
        else:
            raise PatcherError(f"unsupported resource kind: {kind!r}")
    return candidates


def installed_state(game_root: Path, ledger: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for resource in ensure_list(ledger.get("resources"), "resources"):
        item = ensure_mapping(resource, "resource")
        relative, predecessor, target = parse_resource_specs(item)
        blob = game_path(game_root, relative).read_bytes()
        actual = file_spec(blob)
        if actual == predecessor:
            result[relative] = "predecessor"
        elif actual == target:
            result[relative] = "target"
        else:
            result[relative] = "unknown"
    return result


def assert_retained_resources(game_root: Path, ledger: Mapping[str, Any]) -> None:
    retained = ensure_list(ledger.get("retained_resources"), "retained resources")
    for raw in retained:
        item = ensure_mapping(raw, "retained resource")
        relative = item.get("path")
        if not isinstance(relative, str):
            raise PatcherError("retained resource path is invalid")
        expected = parse_file_spec(item.get("spec"), f"retained {relative}")
        require_spec(game_path(game_root, relative).read_bytes(), expected, f"retained {relative}")


def require_stopped_game() -> None:
    if os.name != "nt":
        return
    completed = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq NOBU16PK.exe", "/NH", "/FO", "CSV"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise PatcherError("cannot determine whether NOBU16PK.exe is running")
    if "nobu16pk.exe" in (completed.stdout or "").casefold():
        raise PatcherError("close NOBU16PK.exe before modifying resources")


def backup_root(game_root: Path) -> Path:
    return game_root / "KR_PATCH_BACKUP" / "v0.14.0-resource-patcher"


def contained_backup_path(game_root: Path, relative: Path) -> Path:
    root = game_root.resolve(strict=True)
    candidate = backup_root(root) / relative
    try:
        candidate.resolve(strict=False).relative_to(root)
    except (OSError, ValueError) as exc:
        raise PatcherError(f"backup path escapes game root: {relative.as_posix()}") from exc
    return candidate


def state_path(game_root: Path) -> Path:
    return contained_backup_path(game_root, Path("state.json"))


def backup_path(game_root: Path, relative: str) -> Path:
    return contained_backup_path(game_root, Path(ordinary_relative_path(relative)))


def write_state(game_root: Path, ledger_hash: str, status: str, paths: Sequence[str]) -> None:
    value = {
        "schema": STATE_SCHEMA,
        "release": VERSION,
        "ledger_sha256": ledger_hash,
        "status": status,
        "paths": list(paths),
    }
    atomic_write(state_path(game_root), canonical_json(value))


def ensure_backups(
    game_root: Path,
    ledger: Mapping[str, Any],
    paths: Iterable[str] | None = None,
) -> None:
    selected = None if paths is None else set(paths)
    for resource in ensure_list(ledger.get("resources"), "resources"):
        item = ensure_mapping(resource, "resource")
        relative, predecessor, _target = parse_resource_specs(item)
        if selected is not None and relative not in selected:
            continue
        backup = backup_path(game_root, relative)
        if backup.exists():
            if not backup.is_file():
                raise PatcherError(f"backup is not a file: {relative}")
            require_spec(backup.read_bytes(), predecessor, f"existing backup {relative}")
            continue
        source = game_path(game_root, relative).read_bytes()
        require_spec(source, predecessor, f"installed predecessor {relative}")
        atomic_write(backup, source)
        require_spec(backup.read_bytes(), predecessor, f"written backup {relative}")


def apply_patch(
    game_root: Path,
    ledger: Mapping[str, Any],
    *,
    ledger_hash: str,
    retained_prechecked: bool = False,
) -> dict[str, object]:
    if not retained_prechecked:
        assert_retained_resources(game_root, ledger)
    state = installed_state(game_root, ledger)
    values = set(state.values())
    if values == {"target"}:
        return {"result": "already_target", "writes_performed": False, "state": state}
    if values != {"predecessor"}:
        raise PatcherError(f"apply requires a complete predecessor vector: {state}")
    require_stopped_game()
    candidates = build_candidates(game_root, ledger)
    ensure_backups(game_root, ledger)
    paths = sorted(candidates)
    write_state(game_root, ledger_hash, "applying", paths)
    replaced: list[str] = []
    try:
        for relative in paths:
            require_stopped_game()
            target_path = game_path(game_root, relative)
            require_spec(target_path.read_bytes(), pin_spec(PREDECESSORS[relative]), f"pre-replace {relative}")
            atomic_write(target_path, candidates[relative])
            # Once os.replace succeeds this path must be included in rollback,
            # even if the following verification detects a disk or AV issue.
            replaced.append(relative)
            require_spec(target_path.read_bytes(), pin_spec(TARGETS[relative]), f"applied {relative}")
        final = installed_state(game_root, ledger)
        if set(final.values()) != {"target"}:
            raise PatcherError(f"apply did not reach target vector: {final}")
        write_state(game_root, ledger_hash, "applied", paths)
        return {"result": "applied", "writes_performed": True, "state": final}
    except Exception as original:
        rollback_errors: list[str] = []
        for relative in reversed(replaced):
            try:
                require_stopped_game()
                source = backup_path(game_root, relative).read_bytes()
                require_spec(source, pin_spec(PREDECESSORS[relative]), f"backup {relative}")
                target_path = game_path(game_root, relative)
                atomic_write(target_path, source)
                require_spec(target_path.read_bytes(), pin_spec(PREDECESSORS[relative]), f"rollback {relative}")
            except Exception as rollback_error:
                rollback_errors.append(f"{relative}: {rollback_error}")
        final = installed_state(game_root, ledger)
        write_state(game_root, ledger_hash, "rollback_failed" if rollback_errors else "restored", paths)
        if rollback_errors or set(final.values()) != {"predecessor"}:
            raise PatcherError(
                f"apply failed ({original}); rollback was not proven: {' | '.join(rollback_errors)}"
            ) from original
        raise PatcherError(f"apply failed and was rolled back: {original}") from original


def restore_patch(
    game_root: Path,
    ledger: Mapping[str, Any],
    *,
    ledger_hash: str,
    retained_prechecked: bool = False,
) -> dict[str, object]:
    if not retained_prechecked:
        assert_retained_resources(game_root, ledger)
    state = installed_state(game_root, ledger)
    if "unknown" in state.values():
        raise PatcherError(f"restore found an unsupported installed resource: {state}")
    paths = sorted(relative for relative, value in state.items() if value == "target")
    if not paths:
        return {"result": "already_predecessor", "writes_performed": False, "state": state}
    require_stopped_game()
    target_bytes: dict[str, bytes] = {}
    predecessor_bytes: dict[str, bytes] = {}
    for relative in paths:
        installed = game_path(game_root, relative).read_bytes()
        require_spec(installed, pin_spec(TARGETS[relative]), f"installed target {relative}")
        target_bytes[relative] = installed
        backup = backup_path(game_root, relative)
        if not backup.is_file():
            raise PatcherError(f"backup is missing: {relative}")
        source = backup.read_bytes()
        require_spec(source, pin_spec(PREDECESSORS[relative]), f"backup {relative}")
        predecessor_bytes[relative] = source
    write_state(game_root, ledger_hash, "restoring", paths)
    replaced: list[str] = []
    try:
        for relative in paths:
            require_stopped_game()
            target_path = game_path(game_root, relative)
            atomic_write(target_path, predecessor_bytes[relative])
            # Include the file in rollback before validating the new bytes.
            replaced.append(relative)
            require_spec(target_path.read_bytes(), pin_spec(PREDECESSORS[relative]), f"restored {relative}")
        final = installed_state(game_root, ledger)
        if any(value not in {"predecessor", "missing_optional"} for value in final.values()):
            raise PatcherError(f"restore did not reach predecessor vector: {final}")
        write_state(game_root, ledger_hash, "restored", paths)
        return {"result": "restored", "writes_performed": True, "state": final}
    except Exception as original:
        rollback_errors: list[str] = []
        for relative in reversed(replaced):
            try:
                require_stopped_game()
                target_path = game_path(game_root, relative)
                atomic_write(target_path, target_bytes[relative])
                require_spec(target_path.read_bytes(), pin_spec(TARGETS[relative]), f"restore rollback {relative}")
            except Exception as rollback_error:
                rollback_errors.append(f"{relative}: {rollback_error}")
        final = installed_state(game_root, ledger)
        write_state(game_root, ledger_hash, "rollback_failed" if rollback_errors else "applied", paths)
        if rollback_errors or final != state:
            raise PatcherError(
                f"restore failed ({original}); rollback was not proven: {' | '.join(rollback_errors)}"
            ) from original
        raise PatcherError(f"restore failed and was rolled back: {original}") from original


def load_ledger(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PatcherError(f"cannot read patch ledger: {path}") from exc
    return verify_ledger(value), sha256_bytes(raw)


# ---------------------------------------------------------------------------
# Direct Steam JP 1.1.7 implementation


def binary_patch_member(relative: str) -> str:
    """Return the canonical package member for a BSDIFF40 resource delta."""
    ordinary_relative_path(relative)
    return "binary/" + relative.replace("/", "__") + ".bsdiff"


def parse_resource_specs(resource: Mapping[str, Any]) -> tuple[str, dict[str, object], dict[str, object]]:
    relative = resource.get("path")
    if not isinstance(relative, str) or relative not in RESOURCE_PATHS:
        raise PatcherError(f"invalid resource path: {relative!r}")
    predecessor = parse_file_spec(resource.get("predecessor"), f"{relative} predecessor")
    target = parse_file_spec(resource.get("target"), f"{relative} target")
    if predecessor != pin_spec(PREDECESSORS[relative]):
        raise PatcherError(f"{relative} pristine source profile differs")
    if target != pin_spec(TARGETS[relative]):
        raise PatcherError(f"{relative} target profile differs")
    return relative, predecessor, target


def parse_binary_patch_descriptor(value: object, relative: str) -> dict[str, object]:
    descriptor = ensure_mapping(value, f"{relative} binary patch")
    ensure_exact_keys(
        descriptor,
        {"format", "member", "size", "sha256"},
        f"{relative} binary patch",
    )
    if descriptor.get("format") != BINARY_PATCH_FORMAT:
        raise PatcherError(f"{relative} binary patch format differs")
    member = descriptor.get("member")
    if not isinstance(member, str) or member != binary_patch_member(relative):
        raise PatcherError(f"{relative} binary patch member differs")
    spec = parse_file_spec(descriptor, f"{relative} binary patch")
    target_size = TARGETS[relative][0]
    if (
        spec["size"] <= 0
        or spec["size"] > MAX_BINARY_PATCH_BYTES
        or (
            target_size >= MAX_SMALL_BINARY_PATCH_BYTES * 2
            and int(spec["size"]) * MAX_BINARY_PATCH_FRACTION_DENOMINATOR
            >= target_size * MAX_BINARY_PATCH_FRACTION_NUMERATOR
        )
        or (
            target_size < MAX_SMALL_BINARY_PATCH_BYTES * 2
            and int(spec["size"]) > MAX_SMALL_BINARY_PATCH_BYTES
        )
    ):
        raise PatcherError(f"{relative} binary patch exceeds its bounded delta policy")
    return {
        "format": BINARY_PATCH_FORMAT,
        "member": member,
        **spec,
    }


def bsdiff_offtin(raw: bytes, label: str) -> int:
    if len(raw) != 8:
        raise PatcherError(f"{label} has an invalid BSDIFF integer")
    value = int.from_bytes(raw, "little", signed=False)
    magnitude = value & ((1 << 63) - 1)
    return -magnitude if value & (1 << 63) else magnitude


def apply_bsdiff40(source: bytes, patch: bytes, *, relative: str) -> bytes:
    """Apply one bounded BSDIFF40 patch using only the Python standard library."""
    if len(patch) < 32 or patch[:8] != b"BSDIFF40":
        raise PatcherError(f"{relative} binary patch is not BSDIFF40")
    control_size = bsdiff_offtin(patch[8:16], f"{relative} control length")
    diff_size = bsdiff_offtin(patch[16:24], f"{relative} diff length")
    target_size = bsdiff_offtin(patch[24:32], f"{relative} target length")
    if control_size < 0 or diff_size < 0 or target_size < 0:
        raise PatcherError(f"{relative} binary patch has a negative section")
    control_end = 32 + control_size
    diff_end = control_end + diff_size
    if control_end > len(patch) or diff_end > len(patch):
        raise PatcherError(f"{relative} binary patch sections escape payload")
    try:
        control = bz2.decompress(patch[32:control_end])
        diff = bz2.decompress(patch[control_end:diff_end])
        extra = bz2.decompress(patch[diff_end:])
    except OSError as exc:
        raise PatcherError(f"{relative} binary patch bzip2 stream is invalid") from exc
    if len(control) % 24:
        raise PatcherError(f"{relative} binary patch control stream is malformed")

    candidate = bytearray(target_size)
    old_position = 0
    new_position = 0
    control_position = 0
    diff_position = 0
    extra_position = 0
    while new_position < target_size:
        if control_position + 24 > len(control):
            raise PatcherError(f"{relative} binary patch control stream ended early")
        add_length = bsdiff_offtin(
            control[control_position : control_position + 8],
            f"{relative} add length",
        )
        extra_length = bsdiff_offtin(
            control[control_position + 8 : control_position + 16],
            f"{relative} extra length",
        )
        seek_length = bsdiff_offtin(
            control[control_position + 16 : control_position + 24],
            f"{relative} seek length",
        )
        control_position += 24
        if add_length < 0 or extra_length < 0:
            raise PatcherError(f"{relative} binary patch has a negative copy length")
        if (
            new_position + add_length > target_size
            or diff_position + add_length > len(diff)
            or old_position < 0
            or old_position + add_length > len(source)
        ):
            raise PatcherError(f"{relative} binary patch add range escapes input")
        for offset in range(add_length):
            candidate[new_position + offset] = (
                diff[diff_position + offset] + source[old_position + offset]
            ) & 0xFF
        new_position += add_length
        old_position += add_length
        diff_position += add_length
        if (
            new_position + extra_length > target_size
            or extra_position + extra_length > len(extra)
        ):
            raise PatcherError(f"{relative} binary patch extra range escapes payload")
        candidate[new_position : new_position + extra_length] = extra[
            extra_position : extra_position + extra_length
        ]
        new_position += extra_length
        extra_position += extra_length
        old_position += seek_length
        if old_position < 0 or old_position > len(source):
            raise PatcherError(f"{relative} binary patch seek escapes input")
    if (
        control_position != len(control)
        or diff_position != len(diff)
        or extra_position != len(extra)
    ):
        raise PatcherError(f"{relative} binary patch has unconsumed payload")
    return bytes(candidate)


def patch_member_path(patch_root: Path, member: str) -> Path:
    relative = ordinary_relative_path(member)
    root = patch_root.resolve(strict=True)
    candidate = (root / Path(relative)).resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PatcherError(f"binary patch member escapes patch root: {member}") from exc
    if not candidate.is_file():
        raise PatcherError(f"binary patch member is missing: {member}")
    return candidate


def load_binary_patch(
    patch_root: Path, resource: Mapping[str, Any], relative: str
) -> bytes:
    descriptor = parse_binary_patch_descriptor(resource.get("binary_patch"), relative)
    patch_path = patch_member_path(patch_root, str(descriptor["member"]))
    patch = patch_path.read_bytes()
    require_spec(patch, descriptor, f"{relative} packaged binary patch")
    return patch


def make_binary_resource(
    relative: str, predecessor: bytes, target: bytes, patch_root: Path
) -> dict[str, object]:
    require_spec(predecessor, pin_spec(PREDECESSORS[relative]), f"pristine {relative}")
    require_spec(target, pin_spec(TARGETS[relative]), f"target {relative}")
    member = binary_patch_member(relative)
    patch_path = patch_member_path(patch_root, member)
    patch = patch_path.read_bytes()
    descriptor = {
        "format": BINARY_PATCH_FORMAT,
        "member": member,
        **file_spec(patch),
    }
    parse_binary_patch_descriptor(descriptor, relative)
    rebuilt = apply_bsdiff40(predecessor, patch, relative=relative)
    if rebuilt != target:
        raise PatcherError(f"{relative} binary delta does not rebuild its target")
    return {
        "path": relative,
        "kind": "binary_bsdiff40",
        "predecessor": file_spec(predecessor),
        "target": file_spec(target),
        "binary_patch": descriptor,
    }


def build_ledger(
    pristine_root: Path, game_root: Path, binary_patch_root: Path
) -> dict[str, object]:
    """Create the frozen direct ledger from pristine inputs and v0.15 targets."""
    pristine_root = pristine_root.resolve(strict=True)
    game_root = game_root.resolve(strict=True)
    binary_patch_root = binary_patch_root.resolve(strict=True)
    resources: list[dict[str, object]] = []
    for relative in TEXT_RESOURCE_PATHS:
        predecessor = game_path(pristine_root, relative).read_bytes()
        target = game_path(game_root, relative).read_bytes()
        require_spec(predecessor, pin_spec(PREDECESSORS[relative]), f"pristine {relative}")
        require_spec(target, pin_spec(TARGETS[relative]), f"target {relative}")
        kind = RESOURCE_KINDS[relative]
        if kind == "common_message_table":
            resources.append(make_common_resource(relative, predecessor, target))
        elif kind == "strdata_container":
            resources.append(make_strdata_resource(relative, predecessor, target))
        elif kind == "msggame_records":
            resources.append(make_msggame_resource(relative, predecessor, target))
        else:  # pragma: no cover - fixed map is validated below
            raise PatcherError(f"unsupported text resource kind: {kind}")
    for relative in BINARY_RESOURCE_PATHS:
        resources.append(
            make_binary_resource(
                relative,
                game_path(pristine_root, relative).read_bytes(),
                game_path(game_root, relative).read_bytes(),
                binary_patch_root,
            )
        )
    operation_counts = {
        resource["path"]: resource["operation_count"]
        for resource in resources
        if resource["path"] in TEXT_RESOURCE_PATHS
    }
    ledger: dict[str, object] = {
        "schema": SCHEMA,
        "release": VERSION,
        "source_profile": {
            "kind": "steam-jp-1.1.7-pristine",
            "resource_count": len(RESOURCE_PATHS),
        },
        "resource_count": len(resources),
        "resources": resources,
        "operation_counts": operation_counts,
        "payload_policy": {
            "contains_complete_game_resources": False,
            "contains_game_executable": False,
            "process_memory_access": False,
            "requires_installed_pristine_resources": True,
            "pristine_full_resources_stored": False,
            "opaque_target_records_may_include_context": True,
            "binary_delta_format": BINARY_PATCH_FORMAT,
            "binary_delta_resource_count": len(BINARY_RESOURCE_PATHS),
        },
    }
    verify_ledger(ledger)
    return ledger


def verify_ledger(value: object) -> dict[str, Any]:
    ledger = dict(ensure_mapping(value, "ledger"))
    ensure_exact_keys(
        ledger,
        {
            "schema",
            "release",
            "source_profile",
            "resource_count",
            "resources",
            "operation_counts",
            "payload_policy",
        },
        "ledger",
    )
    if ledger.get("schema") != SCHEMA or ledger.get("release") != VERSION:
        raise PatcherError("unsupported direct resource-patcher ledger")
    source_profile = ensure_mapping(ledger.get("source_profile"), "source profile")
    ensure_exact_keys(source_profile, {"kind", "resource_count"}, "source profile")
    if (
        source_profile.get("kind") != "steam-jp-1.1.7-pristine"
        or source_profile.get("resource_count") != len(RESOURCE_PATHS)
    ):
        raise PatcherError("source profile differs")
    resources = ensure_list(ledger.get("resources"), "resources")
    if len(resources) != len(RESOURCE_PATHS) or ledger.get("resource_count") != len(resources):
        raise PatcherError("resource count differs")
    by_path: dict[str, Mapping[str, Any]] = {}
    opaque_payload_bytes = 0
    for raw in resources:
        resource = ensure_mapping(raw, "resource")
        relative = resource.get("path")
        if not isinstance(relative, str) or relative in by_path:
            raise PatcherError(f"duplicate or invalid resource path: {relative!r}")
        kind = resource.get("kind")
        if relative not in RESOURCE_KINDS or kind != RESOURCE_KINDS[relative]:
            raise PatcherError(f"{relative} resource kind differs")
        if kind == "binary_bsdiff40":
            ensure_exact_keys(
                resource,
                {"path", "kind", "predecessor", "target", "binary_patch"},
                f"{relative} resource",
            )
            parse_resource_specs(resource)
            parse_binary_patch_descriptor(resource.get("binary_patch"), relative)
        else:
            ensure_exact_keys(
                resource,
                {"path", "kind", "predecessor", "target", "operation_count", "operations"},
                f"{relative} resource",
            )
            parse_resource_specs(resource)
            metadata_key = {
                "common_message_table": "string_count",
                "strdata_container": "block_slot_counts",
                "msggame_records": "block_record_counts",
            }[kind]
            verify_raw_metadata(
                resource["predecessor"], f"{relative} predecessor", metadata_key=metadata_key
            )
            verify_raw_metadata(
                resource["target"], f"{relative} target", metadata_key=metadata_key
            )
            opaque_payload_bytes += verify_operations(resource, relative, str(kind))
        by_path[relative] = resource
    if tuple(sorted(by_path)) != tuple(sorted(RESOURCE_PATHS)):
        raise PatcherError("resource vector differs")
    if opaque_payload_bytes > MAX_OPAQUE_RECORD_PAYLOAD_BYTES:
        raise PatcherError("opaque payload budget differs")
    operation_counts = ensure_mapping(ledger.get("operation_counts"), "operation counts")
    ensure_exact_keys(operation_counts, set(TEXT_RESOURCE_PATHS), "operation counts")
    for relative in TEXT_RESOURCE_PATHS:
        if ensure_int(operation_counts.get(relative), f"{relative} operation count") != EXPECTED_OPERATION_COUNTS[relative]:
            raise PatcherError(f"{relative} operation count map differs")
        if operation_counts[relative] != by_path[relative]["operation_count"]:
            raise PatcherError(f"{relative} operation count/resource differs")
    policy = ensure_mapping(ledger.get("payload_policy"), "payload policy")
    expected_policy = {
        "contains_complete_game_resources": False,
        "contains_game_executable": False,
        "process_memory_access": False,
        "requires_installed_pristine_resources": True,
        "pristine_full_resources_stored": False,
        "opaque_target_records_may_include_context": True,
        "binary_delta_format": BINARY_PATCH_FORMAT,
        "binary_delta_resource_count": len(BINARY_RESOURCE_PATHS),
    }
    if dict(policy) != expected_policy:
        raise PatcherError("payload policy differs")
    return ledger


def default_patch_root() -> Path:
    return runtime_directory() / "patches"


def build_candidates(
    game_root: Path,
    ledger: Mapping[str, Any],
    *,
    patch_root: Path | None = None,
    paths: Iterable[str] | None = None,
) -> dict[str, bytes]:
    patch_root = (default_patch_root() if patch_root is None else patch_root).resolve(strict=True)
    selected = None if paths is None else set(paths)
    candidates: dict[str, bytes] = {}
    for resource in ensure_list(ledger.get("resources"), "resources"):
        item = ensure_mapping(resource, "resource")
        relative, predecessor, _target = parse_resource_specs(item)
        if selected is not None and relative not in selected:
            continue
        source = game_path(game_root, relative).read_bytes()
        require_spec(source, predecessor, f"installed {relative}")
        kind = item.get("kind")
        if kind == "common_message_table":
            candidate = apply_common_resource(source, item)
        elif kind == "strdata_container":
            candidate = apply_strdata_resource(source, item)
        elif kind == "msggame_records":
            candidate = apply_msggame_resource(source, item)
        elif kind == "binary_bsdiff40":
            candidate = apply_bsdiff40(
                source,
                load_binary_patch(patch_root, item, relative),
                relative=relative,
            )
            require_spec(candidate, pin_spec(TARGETS[relative]), f"rebuilt {relative}")
        else:  # pragma: no cover - ledger is validated before use
            raise PatcherError(f"unsupported resource kind: {kind!r}")
        candidates[relative] = candidate
    return candidates


def installed_state(game_root: Path, ledger: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for resource in ensure_list(ledger.get("resources"), "resources"):
        item = ensure_mapping(resource, "resource")
        relative, predecessor, target = parse_resource_specs(item)
        unresolved = game_root / Path(ordinary_relative_path(relative))
        if relative in OPTIONAL_RESOURCE_PATHS and not unresolved.exists():
            result[relative] = "missing_optional"
            continue
        actual = file_spec(game_path(game_root, relative).read_bytes())
        if actual == predecessor:
            result[relative] = "predecessor"
        elif actual == target:
            result[relative] = "target"
        else:
            result[relative] = "unknown"
    return result


def pending_apply_paths(state: Mapping[str, str]) -> tuple[str, ...]:
    if any(value == "unknown" for value in state.values()):
        raise PatcherError(f"apply found an unsupported installed resource: {dict(state)}")
    mandatory_values = {state[path] for path in MANDATORY_RESOURCE_PATHS}
    if mandatory_values not in ({"predecessor"}, {"target"}):
        raise PatcherError(f"apply requires a uniform mandatory resource vector: {dict(state)}")
    if any(
        state[path] not in {"predecessor", "target", "missing_optional"}
        for path in OPTIONAL_RESOURCE_PATHS
    ):
        raise PatcherError(f"apply found an unsupported optional resource state: {dict(state)}")
    return tuple(sorted(path for path, value in state.items() if value == "predecessor"))


def assert_retained_resources(game_root: Path, ledger: Mapping[str, Any]) -> None:
    # Direct mode preflights the full source vector; it has no retained vector.
    del game_root, ledger


def backup_root(game_root: Path) -> Path:
    return game_root / "KR_PATCH_BACKUP" / "v0.15.1-direct-patcher"


def apply_patch(
    game_root: Path,
    ledger: Mapping[str, Any],
    *,
    ledger_hash: str,
    patch_root: Path | None = None,
    retained_prechecked: bool = False,
) -> dict[str, object]:
    del retained_prechecked
    state = installed_state(game_root, ledger)
    paths = pending_apply_paths(state)
    if not paths:
        return {"result": "already_target", "writes_performed": False, "state": state}
    require_stopped_game()
    candidates = build_candidates(game_root, ledger, patch_root=patch_root, paths=paths)
    ensure_backups(game_root, ledger, paths)
    write_state(game_root, ledger_hash, "applying", paths)
    replaced: list[str] = []
    try:
        for relative in paths:
            require_stopped_game()
            target_path = game_path(game_root, relative)
            require_spec(target_path.read_bytes(), pin_spec(PREDECESSORS[relative]), f"pre-replace {relative}")
            atomic_write(target_path, candidates[relative])
            replaced.append(relative)
            require_spec(target_path.read_bytes(), pin_spec(TARGETS[relative]), f"applied {relative}")
        final = installed_state(game_root, ledger)
        if any(value not in {"target", "missing_optional"} for value in final.values()):
            raise PatcherError(f"apply did not reach target vector: {final}")
        write_state(game_root, ledger_hash, "applied", paths)
        return {"result": "applied", "writes_performed": True, "state": final}
    except Exception as original:
        rollback_errors: list[str] = []
        for relative in reversed(replaced):
            try:
                require_stopped_game()
                source = backup_path(game_root, relative).read_bytes()
                require_spec(source, pin_spec(PREDECESSORS[relative]), f"backup {relative}")
                target_path = game_path(game_root, relative)
                atomic_write(target_path, source)
                require_spec(target_path.read_bytes(), pin_spec(PREDECESSORS[relative]), f"rollback {relative}")
            except Exception as rollback_error:
                rollback_errors.append(f"{relative}: {rollback_error}")
        final = installed_state(game_root, ledger)
        write_state(game_root, ledger_hash, "rollback_failed" if rollback_errors else "restored", paths)
        if rollback_errors or final != state:
            raise PatcherError(
                f"apply failed ({original}); rollback was not proven: {' | '.join(rollback_errors)}"
            ) from original
        raise PatcherError(f"apply failed and was rolled back: {original}") from original


def canonical_ledger_bytes(ledger: Mapping[str, object]) -> bytes:
    verify_ledger(ledger)
    return gzip.compress(canonical_json(ledger), compresslevel=9, mtime=0)


def write_ledger(path: Path, ledger: Mapping[str, object]) -> None:
    atomic_write(path, canonical_ledger_bytes(ledger))


def load_ledger(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        if not raw.startswith(b"\x1f\x8b"):
            raise PatcherError("direct patch ledger must be gzip-compressed")
        value = json.loads(gzip.decompress(raw).decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PatcherError(f"cannot read direct patch ledger: {path}") from exc
    return verify_ledger(value), sha256_bytes(raw)


def runtime_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return SCRIPT.parent


def default_ledger_path() -> Path:
    return runtime_directory() / "patches" / LEDGER_FILENAME


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


def print_json(value: Mapping[str, object]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=runtime_directory())
    parser.add_argument("--ledger", type=Path, default=default_ledger_path())
    parser.add_argument("--patch-root", type=Path, default=None)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true")
    action.add_argument("--restore", action="store_true")
    action.add_argument(
        "--preflight",
        action="store_true",
        help="verify the complete direct-patch input vector without writing files",
    )
    parser.add_argument("--yes", action="store_true", help="do not request interactive confirmation")
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="suppress the success banner for a parent unified installer",
    )
    parser.add_argument("--show-banner", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    configure_console()
    args = build_parser().parse_args(argv)
    if args.show_banner:
        print(ATTRIBUTION_BANNER)
        return 0
    try:
        game_root = args.game_root.resolve(strict=True)
        ledger, ledger_hash = load_ledger(args.ledger.resolve(strict=True))
        patch_root = (
            args.ledger.resolve(strict=True).parent
            if args.patch_root is None
            else args.patch_root.resolve(strict=True)
        )
        report: dict[str, object] = {
            "release": VERSION,
            "game_root": str(game_root),
            "ledger_sha256": ledger_hash,
            "installed_state": installed_state(game_root, ledger),
        }
        if not args.apply and not args.restore and not args.preflight:
            assert_retained_resources(game_root, ledger)
            report.update({"action": "dry_run", "writes_performed": False})
            print_json(report)
            return 0
        if args.preflight:
            state = report["installed_state"]
            if not isinstance(state, dict):  # pragma: no cover - fixed by installed_state()
                raise PatcherError("installed state has an invalid shape")
            pending = pending_apply_paths(state)
            if not pending:
                result = "already_target"
            else:
                require_stopped_game()
                # The source vector and ledger are already hash-pinned above.
                # Also prove that every externally stored BSDIFF payload exists
                # and matches its ledger descriptor before a unified installer
                # allows the EXE stage to write anything.
                for resource in ensure_list(ledger.get("resources"), "resources"):
                    item = ensure_mapping(resource, "resource")
                    relative, _predecessor, _target = parse_resource_specs(item)
                    if relative in pending and item.get("kind") == "binary_bsdiff40":
                        load_binary_patch(patch_root, item, relative)
                result = "ready"
            print_json(
                {
                    **report,
                    "action": "preflight",
                    "result": result,
                    "writes_performed": False,
                }
            )
            return 0
        action_name = "apply" if args.apply else "restore"
        if not args.yes:
            print_json({**report, "action": action_name, "writes_performed": False})
            if input(f"Type {action_name.upper()} to continue: ").strip() != action_name.upper():
                print("Cancelled.")
                return 2
        # Keep the sole 10-resource retained-vector preflight immediately
        # adjacent to the write operation.  This avoids both a second large
        # read and a stale preflight if the user pauses at confirmation.
        assert_retained_resources(game_root, ledger)
        result = (
            apply_patch(
                game_root,
                ledger,
                ledger_hash=ledger_hash,
                patch_root=patch_root,
                retained_prechecked=True,
            )
            if args.apply
            else restore_patch(
                game_root,
                ledger,
                ledger_hash=ledger_hash,
                retained_prechecked=True,
            )
        )
        print_json({**report, "action": action_name, **result})
        if (
            args.apply
            and not args.no_banner
            and result["result"] in {"applied", "already_target"}
        ):
            print(ATTRIBUTION_BANNER)
        return 0
    except (PatcherError, OSError, RuntimeError) as exc:
        print_json({"release": VERSION, "status": "FAIL", "error": str(exc), "writes_performed": False})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
