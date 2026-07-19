#!/usr/bin/env python3
"""Build a private-only W45-based Steam PC NPC/name spelling candidate.

This builder reads exactly the current W45 Steam Korean MSG_PK tables, the
pristine Steam-PC Japanese backup of those same tables, and current Steam PC
English tables as auxiliary anchors.  It writes a candidate only below its
private ``tmp/`` root; it has no Steam apply, transaction, Git, network, or
release operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_DIRNAME = "candidate"

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_PC_JP_ROOT = Path(
    r"F:\Games\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
    r"\jp-runtime-wave05-20260715-v1\originals"
)
FONT_RESOURCE = STEAM_ROOT / "RES_JP" / "res_lang.bin"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-npc-name-quality-wave50.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-npc-name-quality-wave50-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-npc-name-quality-wave50-manifest.v1"
PK_MAX_LINE_PX = 912
MAX_LINES = 3

LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
WIDE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]")

FONT_SIZE = 161_428_458
FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
FONT_OUTER_ENTRY = 6
FONT_TABLE = 0
FONT_MAP_BYTES = 0x20000
FONT_RECORD_BYTES = 12

# W49 already owns these W45-baseline event IDs.  This candidate must never
# absorb them, even though both candidates repair the Inoue spelling family.
W49_OVERLAP_GUARD_IDS = (3949, 3951, 3953, 3954, 3957)


class Wave50Error(RuntimeError):
    """Raised when a pinned source, static contract, or private output drifts."""


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class TableInput:
    path: Path
    profile: Profile
    record_count: int
    literal_lz4: bool
    label: str


@dataclass(frozen=True)
class ResourceSpec:
    key: str
    relative: str
    current: TableInput
    japanese: TableInput
    english: TableInput
    target: Profile


@dataclass(frozen=True)
class Change:
    resource: str
    entry_id: int
    category: str
    preimage: str
    preimage_utf16le_sha256: str
    old_token: str
    new_token: str
    expected_token_count: int
    target_utf16le_sha256: str
    jp_anchors: tuple[str, ...]
    en_anchors: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class Hold:
    resource: str
    entry_id: int
    preimage: str
    preimage_utf16le_sha256: str
    old_token: str
    new_token: str
    expected_token_count: int
    name_only_target_utf16le_sha256: str
    preimage_line_widths_px: tuple[int, ...]
    name_only_target_line_widths_px: tuple[int, ...]
    jp_anchors: tuple[str, ...]
    en_anchors: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class TableResource:
    input: TableInput
    packed: bytes
    header: Any
    raw: bytes
    table: Any


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    actual_changed_ids: Mapping[str, tuple[int, ...]]


def u(value: str) -> str:
    """Decode ASCII-only escape notation so source literals remain portable."""

    return value.encode("ascii").decode("unicode_escape")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave50Error(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "size": profile.size,
        "sha256": profile.sha256,
        "raw_size": profile.raw_size,
        "raw_sha256": profile.raw_sha256,
    }


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def require_allowed_external_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    forbidden_parts = {"switch", "sc"}
    require(
        not any(part.casefold() in forbidden_parts for part in resolved.parts),
        f"forbidden Switch/SC path: {label}",
    )
    steam_root = STEAM_ROOT.resolve(strict=True)
    jp_root = PRISTINE_PC_JP_ROOT.resolve(strict=True)
    require(
        is_within(resolved, steam_root) or is_within(resolved, jp_root),
        f"external source is outside the approved Steam-PC roots: {label}",
    )
    return resolved


def private_root() -> Path:
    root = TMP_ROOT.resolve(strict=False)
    repo = REPO.resolve(strict=True)
    require(is_within(root, repo), f"private tmp root escapes release workspace: {root}")
    return root


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = private_root()
    require(is_within(resolved, root), f"{label} escapes private tmp root: {resolved}")
    return resolved


def require_profile(packed: bytes, raw: bytes, profile: Profile, label: str) -> None:
    require(len(packed) == profile.size, f"{label} packed size differs")
    require(sha256_bytes(packed) == profile.sha256, f"{label} packed SHA-256 differs")
    require(len(raw) == profile.raw_size, f"{label} raw size differs")
    require(sha256_bytes(raw) == profile.raw_sha256, f"{label} raw SHA-256 differs")


KO_MSGDATA_PROFILE = Profile(
    496_991,
    "8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A",
    495_024,
    "2D38396C29F7548A1C12691877FE9F3D5D4B2C27647D521CFEC975017977C077",
)
KO_MSGDATA_TARGET_PROFILE = Profile(
    496_999,
    "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
    495_032,
    "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
)
JP_MSGDATA_PROFILE = Profile(
    273_734,
    "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
    431_044,
    "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
)
EN_MSGDATA_PROFILE = Profile(
    271_952,
    "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033",
    750_760,
    "756009E6C8EDA82059BE365768B34CF8C030EB9E56C7D836FE567102B163D306",
)

KO_MSGEV_PROFILE = Profile(
    994_739,
    "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    990_828,
    "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
)
KO_MSGEV_TARGET_PROFILE = Profile(
    994_751,
    "F2E5D6F7399CE2B1260984D4CF7AD251FC64D3D9A0279D9E26374BCEAC6EC8AE",
    990_840,
    "04ABDB2305F4B415B6D218370C73E5037C98BEBB0D359FAEBF4D0B91D03AC6FA",
)
JP_MSGEV_PROFILE = Profile(
    555_784,
    "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
    890_428,
    "4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE",
)
EN_MSGEV_PROFILE = Profile(
    762_196,
    "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
    1_878_836,
    "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
)


RESOURCES: Mapping[str, ResourceSpec] = {
    "msgdata": ResourceSpec(
        "msgdata",
        "MSG_PK/JP/msgdata.bin",
        TableInput(
            STEAM_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
            KO_MSGDATA_PROFILE,
            29_218,
            True,
            "W45 Steam Korean msgdata",
        ),
        TableInput(
            PRISTINE_PC_JP_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
            JP_MSGDATA_PROFILE,
            29_210,
            False,
            "pristine Steam-PC Japanese msgdata",
        ),
        TableInput(
            STEAM_ROOT / "MSG_PK" / "EN" / "msgdata.bin",
            EN_MSGDATA_PROFILE,
            29_218,
            False,
            "Steam PC English msgdata auxiliary evidence",
        ),
        KO_MSGDATA_TARGET_PROFILE,
    ),
    "msgev": ResourceSpec(
        "msgev",
        "MSG_PK/JP/msgev.bin",
        TableInput(
            STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin",
            KO_MSGEV_PROFILE,
            17_916,
            True,
            "W45 Steam Korean msgev",
        ),
        TableInput(
            PRISTINE_PC_JP_ROOT / "MSG_PK" / "JP" / "msgev.bin",
            JP_MSGEV_PROFILE,
            17_910,
            False,
            "pristine Steam-PC Japanese msgev",
        ),
        TableInput(
            STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
            EN_MSGEV_PROFILE,
            17_916,
            False,
            "Steam PC English msgev auxiliary evidence",
        ),
        KO_MSGEV_TARGET_PROFILE,
    ),
}


# Every change is fixed to an exact W45 Korean preimage, a token count, a
# resulting UTF-16LE hash, and Japanese/English PC anchors.  The two sources
# are evidence only: the project-authored Korean token replacement is the
# only content mutation.
CHANGES = (
    Change(
        "msgdata", 17197, "npc_name", u(r"\ubc18\uc288"),
        "3582F5CC7EF7A9D519CF4E73E3C529FAFFE4259B35223DDB9C86F1C1897F120E",
        u(r"\ubc18\uc288"), u(r"\ud558\ub098\uc640\uc288"), 1,
        "A472331E3D37B51F6EF498DF6DFF205A7F90D6CE50333BEC35451464E9F7DEB3",
        (u(r"\u72ec\u9237\u8846"),), ("Hanawa Tribe",), "Hanawa Tribe",
    ),
    Change(
        "msgdata", 17235, "npc_name", u(r"\uac00\uc640\uce58\uc288"),
        "66B97B24C92A459A59496B6BE479C47F833743BFB026C6F5AB5FF212B7FA2F7C",
        u(r"\uac00\uc640\uce58\uc288"), u(r"\uac00\uc640\uc6b0\uce58\uc288"), 1,
        "971F6AA018EC205DC37ADA9E19820E4CDCDB423AD6BA336A43E5B516A1932DCA",
        (u(r"\u677e\u5ca1\u8846"),), ("Kawauchi Tribe",), "Kawauchi Tribe",
    ),
    Change(
        "msgdata", 17352, "npc_name", u(r"\ub2e4\uce74\uae30\uc288"),
        "5479ECA37165DA6E3F156492FE62387B884DD0ECCC5F0D024CEB9FE6E40862A5",
        u(r"\ub2e4\uce74\uae30\uc288"), u(r"\ub2e4\uce4c\ub85c\uc288"), 1,
        "8D6B46888572C6799A067BF73D97513E526C5D8A7706196685DC60649FF80581",
        (u(r"\u9db4\u7530\u8846"),), ("Takashiro Tribe",), "Takashiro Tribe",
    ),
    Change(
        "msgdata", 405, "person_name", u(r"\uc774\ub178\uc5d0 "),
        "44089C02C6F48B6D711FC40E89A1BE0F853DEB5BF6FA4B0373180E669632E88F",
        u(r"\uc774\ub178\uc5d0"), u(r"\uc774\ub178\uc6b0\uc5d0"), 1,
        "043D9C5220A42DE558AE6830FAD48D5550553D13B8A2409BE7B2E9ED785BC2B0",
        (u(r"\u4e95\u4e0a"),), (u(r"In\u00aae"),), "Inoue",
    ),
    Change(
        "msgev", 2412, "unarmed_leader", u(r"\ubc18\uc288 \ub450\ub839"),
        "5EC60C692F0F9515A3F6B536F145FD25CF43862DEFF2DFD8C837EC4410115F7E",
        u(r"\ubc18\uc288 \ub450\ub839"), u(r"\ud558\ub098\uc640\uc288 \ub450\ub839"), 1,
        "F4C5105D872725FB75703B69F0184FD9C321620156FE056DF7FBF0A4600B6435",
        (u(r"\u5859\u8846\u982d\u9818"),), ("Hanawa Tribe Boss",), "Hanawa Tribe Boss",
    ),
    Change(
        "msgev", 2421, "unarmed_leader", u(r"\ub370\uc2dc\ub9c8\uc911 \ub450\ub839"),
        "3563B1BDE9345007E1C276F24BF5E5654420A5893FB0D4351E59D0A5AB2A40AC",
        u(r"\ub370\uc2dc\ub9c8\uc911 \ub450\ub839"), u(r"\ub3c4\uc2dc\ub9c8\uc911 \ub450\ub839"), 1,
        "DE6269D2BCC5E7646C11C9E97668B25CE976EC51D7A040FC8E488EA423529574",
        (u(r"\u8c4a\u5cf6\u8846\u982d\u9818"),), ("Toshima Tribe Boss",), "Toshima Tribe Boss",
    ),
    Change(
        "msgev", 2450, "unarmed_leader", u(r"\uac00\uc640\uce58\uc288 \ub450\ub839"),
        "3563295014D098E49B8F71100414BD6E00BD76DAE32D7D59504278D41F6CA95E",
        u(r"\uac00\uc640\uce58\uc288 \ub450\ub839"), u(r"\uac00\uc640\uc6b0\uce58\uc288 \ub450\ub839"), 1,
        "346D8ED63EBA6D178663EB6CAEE445C6E82DBB0CED7750B540437354A476296D",
        (u(r"\u6cb3\u5185\u8846\u982d\u9818"),), ("Kawauchi Tribe Boss",), "Kawauchi Tribe Boss",
    ),
    Change(
        "msgev", 2477, "unarmed_leader", u(r"\uac00\uc988\ub77c\uc57c\ub9c8\uc911 \ub450\ub839"),
        "D469F48938B0EA5A28F834C1B84F986E55DA83482BD518DDF4E8BFA127BF8E10",
        u(r"\uac00\uc988\ub77c\uc57c\ub9c8\uc911 \ub450\ub839"), u(r"\uac00\uc4f0\ub77c\uc57c\ub9c8\uc911 \ub450\ub839"), 1,
        "7D82F656E4E5F1AEE4D976C5F5DB189FAFA98FF211994F0CD01C77694440E80F",
        (u(r"\u845b\u5c71\u8846\u982d\u9818"),), ("Katsurayama Tribe Boss",), "Katsurayama Tribe Boss",
    ),
    Change(
        "msgev", 2521, "unarmed_leader", u(r"\ub3c4\ub77c\ucfe0\ub77c\uc911 \ub450\ub839"),
        "C59D61D459D66A0F1C7FC76B6BF1D3E035FB88BC990AE7F413B36E1CD6462C1C",
        u(r"\ub3c4\ub77c\ucfe0\ub77c\uc911 \ub450\ub839"), u(r"\uace0\ucfe0\ub77c\uc911 \ub450\ub839"), 1,
        "E8C740252F099DDAF92B534F78FBFEDBE51368F622D73C6C7FCF30248EAD549D",
        (u(r"\u864e\u5009\u8846\u982d\u9818"),), ("Kokura Tribe Boss",), "Kokura Tribe Boss",
    ),
    Change(
        "msgev", 2529, "unarmed_leader", u(r"\uc694\ub178\uc288 \ub450\ub839"),
        "7419B9D2FF7C8F8E839492AE39EF552EEA968082A1FD9CF06978929BF17D0D80",
        u(r"\uc694\ub178\uc288 \ub450\ub839"), u(r"\uc138\ub178\uc288 \ub450\ub839"), 1,
        "7E91AF10DC0B3D3460061D10139FA4D7BF6CA6F2F4E81F4340D076C13BBDDE69",
        (u(r"\u4e16\u80fd\u8846\u982d\u9818"),), ("Seno Tribe Boss",), "Seno Tribe Boss",
    ),
    Change(
        "msgev", 2544, "unarmed_leader", u(r"\uc2dc\uc544\ucfe0 \uc218\uad70 \ub450\ub839"),
        "361A619B47A484E5D08289F94FB3CFE12615877FBFC572BB7968B407D19BF7A5",
        u(r"\uc2dc\uc544\ucfe0 \uc218\uad70 \ub450\ub839"), u(r"\uc2dc\uc640\ucfe0 \uc218\uad70 \ub450\ub839"), 1,
        "E62076F84B261F071B4101900E669DD6F16D6D58AA3BCC13B2EF12501DC0C064",
        (u(r"\u5869\u98fd\u6c34\u8ecd\u982d\u9818"),), ("Shiwakusuigun",), "Shiwaku navy leader",
    ),
    Change(
        "msgev", 2567, "unarmed_leader", u(r"\ub2e4\uce74\uae30\uc288 \ub450\ub839"),
        "442BACA1AC1B59386353A522DC29869E8D27DD5ECB3A2252DDA36959809EAB02",
        u(r"\ub2e4\uce74\uae30\uc288 \ub450\ub839"), u(r"\ub2e4\uce4c\ub85c\uc288 \ub450\ub839"), 1,
        "8DE5A114C10699B278C5B2C653FB42DC6A1BACA53BE4F3472CBF107FB25239CE",
        (u(r"\u9ad8\u57ce\u8846\u982d\u9818"),), ("Takashiro Tribe Boss",), "Takashiro Tribe Boss",
    ),
    Change(
        "msgev", 291, "person_name", u(r"\uc774\ub178\uc5d0 \ubaa8\ud1a0\uce74\ub124"),
        "617F8B8EE79CD8A76508540D497C7C840D9A7250727A7BD880D2831033F86C3E",
        u(r"\uc774\ub178\uc5d0"), u(r"\uc774\ub178\uc6b0\uc5d0"), 1,
        "CC376A946B8DF1F3F98CA300E4B6622428606E91F380A3A8B56936A1B16A8BA9",
        (u(r"\u4e95\u4e0a\u5143\u517c"),), (u(r"Motokane In\u00aae"),), "Motokane Inoue",
    ),
    Change(
        "msgev", 292, "person_name", u(r"\uc774\ub178\uc5d0 \uc2dc\uac8c\ud6c4\uc0ac"),
        "6DF7B729DDEBA9540010A59C7B91C6B58034D2517A9BC100C10AA10848457082",
        u(r"\uc774\ub178\uc5d0"), u(r"\uc774\ub178\uc6b0\uc5d0"), 1,
        "D800E86B8D40A91FD9F7D4AFE509E8F2216A4C4FCCB4A067DE8C25139DF63C77",
        (u(r"\u4e95\u4e0a\u91cd\u623f"),), (u(r"Shigefusa In\u00aae"),), "Shigefusa Inoue",
    ),
    Change(
        "msgev", 293, "person_name", u(r"\uc774\ub178\uc5d0 \uc720\ud0a4\ud6c4\uc0ac"),
        "3F31330A65C712A90D8900C44A138F7A80C83DE91C0A0271C418E3D7922E5718",
        u(r"\uc774\ub178\uc5d0"), u(r"\uc774\ub178\uc6b0\uc5d0"), 1,
        "15DD6F4683A36DA6F5F069607B7D7B34F2EBA633995420AF747898BFB8DD9C31",
        (u(r"\u4e95\u4e0a\u4e4b\u623f"),), (u(r"Yukifusa In\u00aae"),), "Yukifusa Inoue",
    ),
    Change(
        "msgev", 3960, "person_name", u(
            r"\uad50\ubb18\ud55c \uc218\uc600\uc9c0\ub9cc, \uc5b4\ub514\uae4c\uc9c0\ub098\n"
            r"\x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\uc758 \ube44\uc815\ud55c \uacb0\ub2e8\uc73c\ub85c, \x1bCB\uc774\ub178\uc5d0\n"
            r"\uc77c\ud30c\x1bCZ\uc758 \uc601\ud5a5\ub825\uc740 \uac00\ubb38\uc5d0\uc11c \uc0ac\ub77c\uc84c\ub2e4."
        ),
        "A4CA9F96D908EB5D9DAA813B441303220C962AB7FB5BB7EF48E2B51AA9049055",
        u(r"\uc774\ub178\uc5d0"), u(r"\uc774\ub178\uc6b0\uc5d0"), 1,
        "740E18BC2F5D873A0F552BC61DBD4BC291A458AE32D63AE5929A5C1D0B37192B",
        (u(r"\u4e95\u4e0a\u515a"),), (u(r"In\u00aae Party"),), "Inoue party only; preserve the existing tag/LF topology",
    ),
)

EXPECTED_CHANGED_IDS: Mapping[str, tuple[int, ...]] = {
    "msgdata": (405, 17197, 17235, 17352),
    "msgev": (291, 292, 293, 2412, 2421, 2450, 2477, 2521, 2529, 2544, 2567, 3960),
}

# The first line grows from 888px to 936px for an Inoue-only replacement,
# while its manual LF/tag topology must remain unchanged.  It is therefore a
# byte-identical hold until a combined name + semantic reflow + real-game QA
# change is reviewed; it is not a width exception for this candidate.
EXPLICIT_HOLDS = (
    Hold(
        "msgev",
        3956,
        u(
            r"\x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294 \uc790\uac1d\uc73c\ub85c \x1bCA\uc774\ub178\uc5d0 \ubaa8\ud1a0\uce74\ub124\x1bCZ\ub97c\n"
            r"\uc554\uc0b4\ud558\uace0, \ub3d9\uc694\ud55c \x1bCB\uc774\ub178\uc5d0 \uc77c\ud30c\x1bCZ \uc800\ud0dd\uc744\n"
            r"\uae09\uc2b5\ud574 \uc77c\uc871 30\uc5ec \uba85\uc744 \ub2e8\uc228\uc5d0 \uc219\uccad\ud588\ub2e4."
        ),
        "EBC680BBA570A02485D3123FD64DB69352ADD7BBFAFEAE66451F8C40C8B8F58C",
        u(r"\uc774\ub178\uc5d0"),
        u(r"\uc774\ub178\uc6b0\uc5d0"),
        2,
        "68918ED1159DCC7709D4123FC17529C7B77FDD2AE805455BF91292BD70FDAFC6",
        (888, 840, 912),
        (936, 888, 912),
        (u(r"\u4e95\u4e0a\u5143\u517c"), u(r"\u4e95\u4e0a\u515a")),
        (u(r"Motokane In\u00aae"), u(r"In\u00aae Party")),
        "name-only correction would exceed 912px; combine with semantic reflow and real-game QA",
    ),
)

# Canonical binding of every changed record's preimage, target, PC JP/EN
# anchors, token/LF signature, and measured width contract.
RECORD_BINDING_SHA256 = "08AF329C8A7D61BCB5E712DD5B7BC999B4549975F5B084049E0788A99E19028A"


def load_table(source: TableInput) -> TableResource:
    path = require_allowed_external_path(source.path, source.label)
    packed = path.read_bytes()
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise Wave50Error(f"{source.label} cannot be parsed as a wrapped message table") from exc
    require_profile(packed, raw, source.profile, source.label)
    require(len(table.texts) == source.record_count, f"{source.label} record count differs")
    require(rebuild_message_table(table, table.texts) == raw, f"{source.label} raw table round-trip differs")
    if source.literal_lz4:
        require(recompress_wrapper(raw, header) == packed, f"{source.label} packed round-trip differs")
    return TableResource(source, packed, header, raw, table)


def _u32(value: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(value):
        raise Wave50Error(f"event font {label} is outside G1N data")
    return struct.unpack_from("<I", value, offset)[0]


def load_event_font_advance() -> tuple[Callable[[str], int], dict[str, Any]]:
    """Read the pinned active Steam PC font solely for 912px QA."""

    path = require_allowed_external_path(FONT_RESOURCE, "active Steam PC event font")
    packed = path.read_bytes()
    require(len(packed) == FONT_SIZE, "active event font size differs")
    require(sha256_bytes(packed) == FONT_SHA256, "active event font SHA-256 differs")
    try:
        archive = parse_link(packed)
        entry = archive.entries[FONT_OUTER_ENTRY]
        _wrapper, raw = decompress_wrapper(entry.data)
    except Exception as exc:
        raise Wave50Error("active event font entry cannot be decoded") from exc

    require(raw[:8] == b"_N1G0000", "event font G1N magic differs")
    require(_u32(raw, 0x08, "declared size") == len(raw), "event font declared size differs")
    table_count = _u32(raw, 0x1C, "table count")
    require(1 <= table_count <= 32, "event font table count is implausible")
    require(FONT_TABLE < table_count, "event font table 0 is absent")
    table_offsets = tuple(_u32(raw, 0x20 + 4 * index, f"table {index} offset") for index in range(table_count))
    atlas_offset = _u32(raw, 0x14, "atlas offset")
    require(
        table_offsets == tuple(sorted(table_offsets)) and len(set(table_offsets)) == table_count,
        "event font table offsets differ",
    )
    table_offset = table_offsets[FONT_TABLE]
    table_end = table_offsets[FONT_TABLE + 1] if FONT_TABLE + 1 < table_count else atlas_offset
    record_start = table_offset + FONT_MAP_BYTES
    require(0 <= table_offset <= record_start <= table_end <= len(raw), "event font table 0 bounds differ")
    record_bytes = table_end - record_start
    require(record_bytes % FONT_RECORD_BYTES == 0, "event font record region alignment differs")
    record_count = record_bytes // FONT_RECORD_BYTES
    require(record_count > 0, "event font has no table 0 records")
    mapping = struct.unpack_from("<65536H", raw, table_offset)

    def advance(character: str) -> int:
        codepoint = ord(character)
        ordinal = mapping[codepoint]
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character) is not None:
                return 48
            raise Wave50Error(f"event font lacks U+{codepoint:04X}")
        if ordinal >= record_count:
            raise Wave50Error(f"event font maps U+{codepoint:04X} outside table 0")
        record_offset = record_start + ordinal * FONT_RECORD_BYTES
        width = raw[record_offset]
        glyph_advance = raw[record_offset + 4]
        if width != glyph_advance or glyph_advance not in (24, 48):
            raise Wave50Error(f"event font metric differs for U+{codepoint:04X}")
        return glyph_advance

    return advance, {
        "resource": "RES_JP/res_lang.bin",
        "size": FONT_SIZE,
        "sha256": FONT_SHA256,
        "outer_entry": FONT_OUTER_ENTRY,
        "g1n_table": FONT_TABLE,
        "g1n_size": len(raw),
        "table0_record_count": record_count,
    }


def protected_signature(value: str) -> dict[str, Any]:
    """Capture all non-content layout/runtime markers that must not change."""

    escapes: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at offset {cursor}")
            escapes.append(token)
            cursor += 3
            continue
        if character not in ("\r", "\n") and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    percent_offsets = {match.start() for match in printf}
    return {
        "line_breaks": LINEBREAK_RE.findall(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "esc_tokens": escapes,
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in percent_offsets
        ),
        "controls": controls,
    }


def line_widths(value: str, advance: Callable[[str], int]) -> tuple[int, ...]:
    widths: list[int] = []
    for line in LINEBREAK_RE.sub("\n", value).split("\n"):
        width = 0
        cursor = 0
        while cursor < len(line):
            character = line[cursor]
            if character == "\x1b":
                token = line[cursor : cursor + 3]
                require(ESC_RE.fullmatch(token) is not None, "malformed event ESC token")
                cursor += 3
                continue
            if unicodedata.category(character) == "Cc":
                raise Wave50Error(f"unexpected event control U+{ord(character):04X}")
            width += advance(character)
            cursor += 1
        widths.append(width)
    return tuple(widths)


def validate_static_contract() -> None:
    by_resource: dict[str, list[int]] = {key: [] for key in RESOURCES}
    for change in CHANGES:
        require(change.resource in RESOURCES, f"unknown resource in change {change.entry_id}")
        by_resource[change.resource].append(change.entry_id)
        require(text_hash(change.preimage) == change.preimage_utf16le_sha256, f"{change.entry_id} preimage hash differs")
        require(change.expected_token_count >= 1, f"{change.entry_id} token count is invalid")
        require(change.old_token != change.new_token, f"{change.entry_id} token mutation is empty")
        require(change.jp_anchors and change.en_anchors, f"{change.entry_id} requires JP and EN anchors")
    require(len(CHANGES) == 16, "static candidate must contain exactly 16 records")
    for resource, expected in EXPECTED_CHANGED_IDS.items():
        require(tuple(sorted(by_resource[resource])) == expected, f"{resource} declared ID scope differs")
        require(len(by_resource[resource]) == len(set(by_resource[resource])), f"{resource} has duplicate IDs")
    event_ids = set(by_resource["msgev"])
    require(event_ids.isdisjoint(W49_OVERLAP_GUARD_IDS), "W49 overlap ID entered this candidate")
    hold_ids = {(hold.resource, hold.entry_id) for hold in EXPLICIT_HOLDS}
    require(len(hold_ids) == len(EXPLICIT_HOLDS), "duplicate explicit hold")
    require(hold_ids == {("msgev", 3956)}, "explicit hold scope differs")
    require(not (hold_ids & {(change.resource, change.entry_id) for change in CHANGES}), "held ID entered candidate")


def evaluate_explicit_holds(
    current: Mapping[str, TableResource],
    japanese: Mapping[str, TableResource],
    english: Mapping[str, TableResource],
    advance: Callable[[str], int],
) -> list[dict[str, Any]]:
    """Audit held rows without allowing them into the candidate mutation set."""

    records: list[dict[str, Any]] = []
    for hold in EXPLICIT_HOLDS:
        before = current[hold.resource].table.texts[hold.entry_id]
        jp_text = japanese[hold.resource].table.texts[hold.entry_id]
        en_text = english[hold.resource].table.texts[hold.entry_id]
        require(before == hold.preimage, f"held {hold.entry_id} W45 preimage differs")
        require(text_hash(before) == hold.preimage_utf16le_sha256, f"held {hold.entry_id} preimage hash differs")
        require(before.count(hold.old_token) == hold.expected_token_count, f"held {hold.entry_id} token count differs")
        name_only_target = before.replace(hold.old_token, hold.new_token)
        require(
            text_hash(name_only_target) == hold.name_only_target_utf16le_sha256,
            f"held {hold.entry_id} name-only target hash differs",
        )
        require(
            protected_signature(before) == protected_signature(name_only_target),
            f"held {hold.entry_id} name-only proposal changes tags, tokens, controls, or manual LF",
        )
        before_widths = line_widths(before, advance)
        proposed_widths = line_widths(name_only_target, advance)
        require(before_widths == hold.preimage_line_widths_px, f"held {hold.entry_id} preimage widths differ")
        require(
            proposed_widths == hold.name_only_target_line_widths_px,
            f"held {hold.entry_id} name-only widths differ",
        )
        require(max(before_widths) <= PK_MAX_LINE_PX, f"held {hold.entry_id} W45 source already exceeds width")
        require(max(proposed_widths) > PK_MAX_LINE_PX, f"held {hold.entry_id} no longer requires a width hold")
        for anchor in hold.jp_anchors:
            require(anchor in jp_text, f"held {hold.entry_id} lacks JP anchor {anchor!r}")
        for anchor in hold.en_anchors:
            require(anchor in en_text, f"held {hold.entry_id} lacks EN anchor {anchor!r}")
        records.append(
            {
                "resource": hold.resource,
                "id": hold.entry_id,
                "preimage_utf16le_sha256": text_hash(before),
                "name_only_target_utf16le_sha256": text_hash(name_only_target),
                "preimage_line_widths_px": list(before_widths),
                "name_only_target_line_widths_px": list(proposed_widths),
                "jp_utf16le_sha256": text_hash(jp_text),
                "en_utf16le_sha256": text_hash(en_text),
                "jp_anchors": list(hold.jp_anchors),
                "jp_anchor_utf16le_sha256": [text_hash(anchor) for anchor in hold.jp_anchors],
                "en_anchors": list(hold.en_anchors),
                "en_anchor_utf16le_sha256": [text_hash(anchor) for anchor in hold.en_anchors],
                "candidate_utf16le_byte_identical": False,
                "reason": hold.reason,
            }
        )
    return records


def record_binding(record: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "resource",
        "id",
        "category",
        "preimage",
        "target",
        "preimage_utf16le_sha256",
        "target_utf16le_sha256",
        "jp_utf16le_sha256",
        "en_utf16le_sha256",
        "jp_anchors",
        "jp_anchor_utf16le_sha256",
        "en_anchors",
        "en_anchor_utf16le_sha256",
        "replacement",
        "protected_signature",
        "target_line_count",
        "target_line_widths_px",
    )
    return {key: record[key] for key in keys}


def prepare_candidate() -> CandidateBundle:
    validate_static_contract()
    advance, font = load_event_font_advance()
    current = {key: load_table(spec.current) for key, spec in RESOURCES.items()}
    japanese = {key: load_table(spec.japanese) for key, spec in RESOURCES.items()}
    english = {key: load_table(spec.english) for key, spec in RESOURCES.items()}
    held_records = evaluate_explicit_holds(current, japanese, english, advance)
    targets = {key: list(table.table.texts) for key, table in current.items()}
    records: list[dict[str, Any]] = []

    for change in CHANGES:
        spec = RESOURCES[change.resource]
        require(change.entry_id < len(current[change.resource].table.texts), f"{change.entry_id} is absent from W45 input")
        require(change.entry_id < len(japanese[change.resource].table.texts), f"{change.entry_id} is absent from JP evidence")
        require(change.entry_id < len(english[change.resource].table.texts), f"{change.entry_id} is absent from EN evidence")
        before = current[change.resource].table.texts[change.entry_id]
        jp_text = japanese[change.resource].table.texts[change.entry_id]
        en_text = english[change.resource].table.texts[change.entry_id]
        require(before == change.preimage, f"{spec.relative} {change.entry_id} W45 preimage differs")
        require(text_hash(before) == change.preimage_utf16le_sha256, f"{change.entry_id} preimage UTF-16LE hash differs")
        for anchor in change.jp_anchors:
            require(anchor in jp_text, f"{change.entry_id} lacks JP anchor {anchor!r}")
        for anchor in change.en_anchors:
            require(anchor in en_text, f"{change.entry_id} lacks EN anchor {anchor!r}")
        require(
            before.count(change.old_token) == change.expected_token_count,
            f"{change.entry_id} expected {change.expected_token_count} source token(s)",
        )
        target = before.replace(change.old_token, change.new_token)
        require(text_hash(target) == change.target_utf16le_sha256, f"{change.entry_id} target UTF-16LE hash differs")
        before_signature = protected_signature(before)
        target_signature = protected_signature(target)
        require(before_signature == target_signature, f"{change.entry_id} changes tags, tokens, controls, or manual LF")
        widths = line_widths(target, advance)
        require(1 <= len(widths) <= MAX_LINES, f"{change.entry_id} line count is outside 1..{MAX_LINES}")
        require(max(widths) <= PK_MAX_LINE_PX, f"{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
        targets[change.resource][change.entry_id] = target
        records.append(
            {
                "resource": change.resource,
                "relative": spec.relative,
                "id": change.entry_id,
                "category": change.category,
                "preimage": before,
                "target": target,
                "preimage_utf16le_sha256": text_hash(before),
                "target_utf16le_sha256": text_hash(target),
                "jp_utf16le_sha256": text_hash(jp_text),
                "en_utf16le_sha256": text_hash(en_text),
                "jp_anchors": list(change.jp_anchors),
                "jp_anchor_utf16le_sha256": [text_hash(anchor) for anchor in change.jp_anchors],
                "en_anchors": list(change.en_anchors),
                "en_anchor_utf16le_sha256": [text_hash(anchor) for anchor in change.en_anchors],
                "replacement": {
                    "old": change.old_token,
                    "new": change.new_token,
                    "expected_count": change.expected_token_count,
                },
                "protected_signature": target_signature,
                "target_line_count": len(widths),
                "target_line_widths_px": list(widths),
                "rationale": change.rationale,
            }
        )

    binding = [record_binding(record) for record in records]
    binding_sha256 = sha256_bytes(canonical_json(binding))
    require(binding_sha256 == RECORD_BINDING_SHA256, "per-record preimage/target/JP/EN binding differs")

    candidate_packed: dict[str, bytes] = {}
    candidate_raw: dict[str, bytes] = {}
    actual_changed_ids: dict[str, tuple[int, ...]] = {}
    candidate_tables: dict[str, Any] = {}
    for key, spec in RESOURCES.items():
        source = current[key]
        raw = rebuild_message_table(source.table, tuple(targets[key]))
        packed = recompress_wrapper(raw, source.header)
        require_profile(packed, raw, spec.target, f"{spec.relative} candidate")
        header, decoded = decompress_wrapper(packed)
        decoded_table = parse_message_table(decoded)
        require(rebuild_message_table(decoded_table, decoded_table.texts) == decoded, f"{spec.relative} candidate raw round-trip differs")
        require(recompress_wrapper(decoded, header) == packed, f"{spec.relative} candidate packed round-trip differs")
        changed_ids = tuple(
            index
            for index, (before, after) in enumerate(zip(source.table.texts, decoded_table.texts))
            if before != after
        )
        require(changed_ids == EXPECTED_CHANGED_IDS[key], f"{spec.relative} actual changed-ID scope differs")
        candidate_packed[key] = packed
        candidate_raw[key] = raw
        actual_changed_ids[key] = changed_ids
        candidate_tables[key] = decoded_table

    require(
        set(actual_changed_ids["msgev"]).isdisjoint(W49_OVERLAP_GUARD_IDS),
        "W49 overlap ID entered actual event output",
    )
    for record in held_records:
        key = record["resource"]
        entry_id = record["id"]
        before_bytes = current[key].table.texts[entry_id].encode("utf-16le")
        after_bytes = candidate_tables[key].texts[entry_id].encode("utf-16le")
        require(before_bytes == after_bytes, f"held {entry_id} is not byte-identical in candidate table")
        record["candidate_utf16le_byte_identical"] = True
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "baseline": "W45",
            "current_korean_inputs": [spec.current.path.as_posix() for spec in RESOURCES.values()],
            "pristine_pc_japanese_evidence": [spec.japanese.path.as_posix() for spec in RESOURCES.values()],
            "pc_english_auxiliary_evidence": [spec.english.path.as_posix() for spec in RESOURCES.values()],
            "font_metric_qa_only": FONT_RESOURCE.as_posix(),
            "switch_or_sc_read": False,
            "workspace_overlay_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "font": font,
        "pk_max_line_px": PK_MAX_LINE_PX,
        "max_lines": MAX_LINES,
        "input": {key: profile_dict(spec.current.profile) for key, spec in RESOURCES.items()},
        "pc_jp_evidence": {key: profile_dict(spec.japanese.profile) for key, spec in RESOURCES.items()},
        "pc_en_auxiliary_evidence": {key: profile_dict(spec.english.profile) for key, spec in RESOURCES.items()},
        "target": {key: profile_dict(spec.target) for key, spec in RESOURCES.items()},
        "changed_record_count": len(CHANGES),
        "held_record_count": len(held_records),
        "actual_changed_ids": {key: list(ids) for key, ids in actual_changed_ids.items()},
        "w49_overlap_guard_ids": list(W49_OVERLAP_GUARD_IDS),
        "w49_overlap_guard_passed": True,
        "explicit_holds": held_records,
        "record_binding_sha256": binding_sha256,
        "records": records,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            spec.relative: {
                "input": profile_dict(spec.current.profile),
                "output": profile_dict(spec.target),
                "actual_changed_ids": list(actual_changed_ids[key]),
            }
            for key, spec in RESOURCES.items()
        },
        "changed_record_count": len(CHANGES),
        "held_record_count": len(held_records),
        "w49_overlap_guard_ids": list(W49_OVERLAP_GUARD_IDS),
        "explicit_holds": [
            {"resource": record["resource"], "id": record["id"], "candidate_utf16le_byte_identical": record["candidate_utf16le_byte_identical"]}
            for record in held_records
        ],
        "record_binding_sha256": binding_sha256,
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(candidate_packed, candidate_raw, audit, manifest, actual_changed_ids)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(not output.exists(), f"candidate output already exists: {output}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    require_private(TMP_ROOT, "private tmp root")
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    require_private(stage, "candidate stage")
    try:
        for key, spec in RESOURCES.items():
            destination = stage / Path(spec.relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(bundle.packed[key])
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(output.is_dir(), "private candidate is absent")
    expected_files = {
        "MSG_PK/JP/msgdata.bin",
        "MSG_PK/JP/msgev.bin",
        "audit.v1.json",
        "candidate_manifest.v1.json",
    }
    actual_files = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    require(actual_files == expected_files, "private candidate file set differs")
    for key, spec in RESOURCES.items():
        path = output / Path(spec.relative)
        require(path.read_bytes() == bundle.packed[key], f"private candidate differs: {spec.relative}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require(
        (output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "private manifest differs",
    )
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "actual_changed_ids": {key: list(ids) for key, ids in bundle.actual_changed_ids.items()},
        "record_binding_sha256": bundle.audit["record_binding_sha256"],
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": len(CHANGES),
            "actual_changed_ids": {key: list(ids) for key, ids in bundle.actual_changed_ids.items()},
            "record_binding_sha256": bundle.audit["record_binding_sha256"],
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
