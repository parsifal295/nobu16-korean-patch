#!/usr/bin/env python3
"""Build a private PC-only Block 15 literal-repair candidate.

This workstream deliberately has no Steam write, transaction, Git, network,
or release operation.  It reads the pinned current Steam-PC Korean resources
and pristine PC-Japanese references, then writes only below this workstream's
private ``tmp`` root.

``derive-pins`` is a read-only maintenance command.  ``build`` and
``verify-private`` refuse to run until every input, record, and output pin is
present and matches.  ``diff-check`` validates a built private candidate
against the pinned W45 input without touching the game installation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

BASE_PC_JP_SOURCE = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
PK_PC_JP_SOURCE = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / PK_RESOURCE
)

W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-block15-runtime-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-block15-runtime-candidate-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-block15-runtime-candidate-manifest.v1"

# The active PC font represents a 38 EAW-unit / 912-pixel conservative ceiling
# for this audit.  An applying row may neither increase the record's maximum
# line width nor exceed this ceiling.  This is intentionally stricter than a
# visual judgement and keeps unmeasured runtime substitutions conservative.
CONSERVATIVE_MAX_LINE_PX = 912
CONSERVATIVE_MAX_EAW_UNITS = 38


class CandidateError(RuntimeError):
    """Raised when an input, semantic pin, or private-output guard drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    require(
        not any("switch" in part.casefold() for part in resolved.parts),
        f"Nintendo Switch path is forbidden: {label}",
    )
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CandidateError(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 format helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 format helper differs")
    spec = importlib.util.spec_from_file_location("block15_pinned_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise CandidateError("cannot load Wave 27 format helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()
Coordinate = tuple[int, int]


@dataclass(frozen=True)
class ResourceSpec:
    resource: str
    current_path: Path
    pc_jp_source: Path
    current_profile: Mapping[str, Any]
    pc_jp_profile: Mapping[str, Any]


@dataclass(frozen=True)
class Proposal:
    family: str
    resource: str
    coordinate: Coordinate
    literal_index: int
    old: str
    new: str
    pc_jp_anchor: str
    reason: str
    disposition: str

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"

    @property
    def slot_text(self) -> str:
        return f"{self.coordinate_text}:{self.literal_index}"


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    rows: tuple[Mapping[str, Any], ...]
    preimage_pins: Mapping[str, Mapping[str, Mapping[str, Any]]]


# Exact installed W45 Korean resources and the two allowed pristine PC-JP
# references.  The builder rejects a drift before it parses a record.
RESOURCE_SPECS: Mapping[str, ResourceSpec] = {
    BASE_RESOURCE: ResourceSpec(
        resource=BASE_RESOURCE,
        current_path=STEAM_ROOT / BASE_RESOURCE,
        pc_jp_source=BASE_PC_JP_SOURCE,
        current_profile={
            "size": 1_504_410,
            "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        },
        pc_jp_profile={
            "size": 610_163,
            "sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        },
    ),
    PK_RESOURCE: ResourceSpec(
        resource=PK_RESOURCE,
        current_path=STEAM_ROOT / PK_RESOURCE,
        pc_jp_source=PK_PC_JP_SOURCE,
        current_profile={
            "size": 1_806_538,
            "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        },
        pc_jp_profile={
            "size": 721_304,
            "sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        },
    ),
}


# Applying rows: literal-only replacements.  The source-language anchor is
# evidence only; Japanese data never supplies bytes to the Korean candidate.
# 15:1206 / 15:1214 preserve the existing manual LF inside their literal.
APPLY_PROPOSALS: tuple[Proposal, ...] = (
    Proposal("riding_training", BASE_RESOURCE, (15, 1875), 1, "마술 훈련", "승마 훈련", "馬術の訓練", "馬術 training, not magic", "apply"),
    Proposal("riding_training", BASE_RESOURCE, (15, 1890), 1, "마술 훈련", "승마 훈련", "馬術の訓練", "馬術 training, not magic", "apply"),
    Proposal("report_possible", BASE_RESOURCE, (15, 1899), 2, "보고할 수 없", "보고할 수 있", "報告でき", "report is possible", "apply"),
    Proposal("impression_worsens", BASE_RESOURCE, (15, 1096), 3, "심증이 악화", "인상이 악화", "心証が悪化", "心証 is an impression here", "apply"),
    Proposal("impression_improves", BASE_RESOURCE, (15, 1206), 2, "심증이\n이전보다 좋아졌다", "인상이\n이전보다 좋아졌다", "心証が\n以前より良くなった", "preserve LF while replacing 心証", "apply"),
    Proposal("favorable_opinion", BASE_RESOURCE, (15, 1657), 0, "심증은 충분하니", "호감은 충분하니", "心証は十分", "alliance advice uses favorable opinion", "apply"),
    Proposal("favorable_opinion", BASE_RESOURCE, (15, 1659), 0, "심증은 충분하니", "호감은 충분하니", "心証は十分", "alliance-extension advice uses favorable opinion", "apply"),
    Proposal("favorable_opinion", BASE_RESOURCE, (15, 1661), 0, "심증은 충분하니", "호감은 충분하니", "心証は十分", "marriage-alliance advice uses favorable opinion", "apply"),
    Proposal("report_possible", PK_RESOURCE, (15, 1929), 2, "보고할 수 없", "보고할 수 있", "報告でき", "report is possible", "apply"),
    Proposal("capture_command", PK_RESOURCE, (15, 2257), 1, "다음 성을 함락했습니다:", "를 함락시켜라", "を落とせ", "Japanese is an imperative capture command", "apply"),
    Proposal("capture_command", PK_RESOURCE, (15, 2258), 1, "다음 성을 함락했습니다:", "를 함락시켜라", "を落とせ", "Japanese is an imperative capture command", "apply"),
    Proposal("cannot_invade", PK_RESOURCE, (15, 2279), 0, "침공할 수 있어", "침공할 수 없어", "侵攻することができ", "context is diplomatic inability to invade", "apply"),
    Proposal("impression_worsens", PK_RESOURCE, (15, 1104), 3, "심증이 악화", "인상이 악화", "心証が悪化", "心証 is an impression here", "apply"),
    Proposal("impression_improves", PK_RESOURCE, (15, 1214), 2, "심증이\n이전보다 좋아졌다", "인상이\n이전보다 좋아졌다", "心証が\n以前より良くなった", "preserve LF while replacing 心証", "apply"),
    Proposal("favorable_opinion", PK_RESOURCE, (15, 1687), 0, "심증은 충분하니", "호감은 충분하니", "心証は十分", "alliance advice uses favorable opinion", "apply"),
    Proposal("favorable_opinion", PK_RESOURCE, (15, 1689), 0, "심증은 충분하니", "호감은 충분하니", "心証は十分", "alliance-extension advice uses favorable opinion", "apply"),
    Proposal("favorable_opinion", PK_RESOURCE, (15, 1691), 0, "심증은 충분하니", "호감은 충분하니", "心証は十分", "marriage-alliance advice uses favorable opinion", "apply"),
)


# This semantic correction is intentionally held.  Literal-only replacement
# makes its sole line 1152px / 48 EAW units (from 720px / 30), exceeding both
# the source width and the conservative cap.  Adding a line break is forbidden
# by this workstream's manual-LF invariant.
HOLD_PROPOSALS: tuple[Proposal, ...] = (
    Proposal("severed_relation", BASE_RESOURCE, (15, 1121), 2, "이 절연", "의 관계가 단절되었습니다.", "手切", "relationship severed by estrangement scheme", "hold_width_excess"),
)


# These other private candidates are immutable exclusions.  W46 has Block 15
# entries, so it is represented exactly.  W48/W50/W51/static-composite are
# represented by conservative block guards: a broader failure is intentional,
# and guarantees that any coordinate from their known scopes fails immediately
# without reading another workstream during build.
EXACT_REUSED_COORDINATES: Mapping[str, Mapping[str, frozenset[Coordinate]]] = {
    "W46": {
        BASE_RESOURCE: frozenset({(6, 4410), (15, 220), (15, 270)}),
        PK_RESOURCE: frozenset({(6, 4469), (15, 223), (15, 273)}),
    },
}
CONSERVATIVE_REUSED_BLOCKS: Mapping[str, Mapping[str, frozenset[int]]] = {
    "W48": {BASE_RESOURCE: frozenset({6}), PK_RESOURCE: frozenset({6})},
    "W50": {BASE_RESOURCE: frozenset({9, 12}), PK_RESOURCE: frozenset({9, 12})},
    "W51": {BASE_RESOURCE: frozenset({13, 14}), PK_RESOURCE: frozenset({13, 14})},
    "static_composite": {
        BASE_RESOURCE: frozenset({6, 7, 8, 9, 12, 13, 14}),
        PK_RESOURCE: frozenset({2, 6, 7, 8, 9, 12, 13, 14, 17}),
    },
}


# These pins are filled by the read-only derive-pins command before build is
# allowed.  Each record pin includes whole-record and per-literal preimages;
# TARGET_OUTPUT_PROFILES additionally pins the exact packed/raw result.
RECORD_PREIMAGE_PINS: Mapping[str, Mapping[str, Mapping[str, Any]]] = {'MSG/JP/msggame.bin': {'15:1096': {'current': {'literal_count': 4,
                                                'literal_utf16le_sha256': ['CE20CAB51C0AF6186BF449B8DF0278A041550602A0F0066F100046E66337E592',
                                                                           'E8896624F93641B7A06CFAD7508E413D48A4830EC4F79CB822CD572BDC73E2F1',
                                                                           'CAB57DDE07EE63BBF59BA2D9B6DB45C1A74600332EF271EBF47EB29ABF54FC04',
                                                                           '26FDD3D605D0B835F415B0D08B0FE74500A6CC0FDD47D13122A03589264929C7'],
                                                'record_sha256': '0E830F623B677EF23F621676ADEA6AA2B083509D6785D5B5E438F4FFB72709BF',
                                                'record_size': 111},
                                    'pc_jp': {'literal_count': 4,
                                              'literal_utf16le_sha256': ['DDEBDAB4768B502DD0192BA273002B4CB49825B6B3730F492B4238A3751596E5',
                                                                         '68C92EC1F0BA0C6FDECBE8F16E022F78DD7C2D5A7AE2E2409E164B2F414F1EE3',
                                                                         'FA433C89E61178902327DA13AF7DC0B09AEDE94A362DE11626C21700A658C353',
                                                                         '7D3C86D5FC73B1F41D9ADBC93F2E8EAD36B80C9A80624E412D7C0B46E6F9F9AC'],
                                              'record_sha256': '3F56E8166838178D23153D7C8F57099CDCE421DF1C9AA393E17F005BFDFAEBD9',
                                              'record_size': 103}},
                        '15:1121': {'current': {'literal_count': 3,
                                                'literal_utf16le_sha256': ['DD32BF8B0B888C7745C660E235FDCAFC15D0FDC4952A8CE751E456113993E907',
                                                                           '618A5E7A3D787F90C48AD70A5D753297287C64E58387339492DDDEE2E66D7FA2',
                                                                           '51F3243BF4C94F35ACF0BBBA6338B3CC7F427077496AE2B21951978F87951DDA'],
                                                'record_sha256': '7C16024E0BA320F82B3CC3D6324B13889B8E069E4E9998A26DFB65AB61033CDD',
                                                'record_size': 61},
                                    'pc_jp': {'literal_count': 3,
                                              'literal_utf16le_sha256': ['8266F48392AC445251AB860B5F3A227BA0FA2C716F17503ECE8D43DBFE90CBDD',
                                                                         'DB87CEE52504CA5732BAD49DDB1D5B8551C011C1891996D58AACAE47F66585ED',
                                                                         '349CCBD921EE5DB989D459AD48FADBD79A86690E509AD136C6949798B892CF9E'],
                                              'record_sha256': '910C454EF470856A6BF6F4D81F9E0FEA073FED2280ACA3D8463F2DA042F3F0C5',
                                              'record_size': 53}},
                        '15:1206': {'current': {'literal_count': 3,
                                                'literal_utf16le_sha256': ['C83D8AA5B9BFE835F54C8D73AEF3FD47B1036E90BC9C50ED2D9B626664743758',
                                                                           'AE3D3A894925CC5F90E39525E1CED6D2C20579ADF8F11A9C5829D91DAE625AA8',
                                                                           'D4397B2C06EEDBD825389BA80B6E238B883DED656655072B07045CBF2ABFC235'],
                                                'record_sha256': '38404B00DF7C696A833564EBAD325D05C2BF55C81A2C6E8A4DA6C04E76A7DE24',
                                                'record_size': 104},
                                    'pc_jp': {'literal_count': 3,
                                              'literal_utf16le_sha256': ['7D25F09A731001A34A06F6D054104397D2BD073469D690ACD6075DB6963790CC',
                                                                         '039BE30C84FE744A10D3A012AC820337C6D966B1C85C84D593CCE7D0FC7F3EAE',
                                                                         '2A0A5A9B79C9B22DAF3CB53D47365A8E494AB9FA0A4DCB8959AC39A0D3F8E7CF'],
                                              'record_sha256': '6AED2C455E0CB5EC6102F6A8A5CC3CB9578515CC43CC56C5BAF2E9F7432839F5',
                                              'record_size': 86}},
                        '15:1657': {'current': {'literal_count': 1,
                                                'literal_utf16le_sha256': ['97E7A1505F9D0C95F3DCF8A7AC22ECB22E6A3198E0A6378C11E63F84B82F7A61'],
                                                'record_sha256': 'FBAFE4EB6F16377935CBA36D926B21604B33BDBF231D4CD40D95A1E2D763F316',
                                                'record_size': 82},
                                    'pc_jp': {'literal_count': 1,
                                              'literal_utf16le_sha256': ['9FF7C51F5E91F8E26AA4692C3ACBAE1774C87992F078BF5A3CD7D961E9B7788A'],
                                              'record_sha256': '79042359D16DB2F7515C6FDFDAEE38A2D331CD589B5D256772DF6B207CE2A58B',
                                              'record_size': 64}},
                        '15:1659': {'current': {'literal_count': 1,
                                                'literal_utf16le_sha256': ['CD971054E0B150F29082A447B77672D67C94E803A576A71D16E78718639F34E7'],
                                                'record_sha256': 'E53AE1C2C69F875C0A1170D7DBD269FB813F71293C6FA5EDDA115BA01F3DAC43',
                                                'record_size': 82},
                                    'pc_jp': {'literal_count': 1,
                                              'literal_utf16le_sha256': ['A6A1929F01CB23E8F48098DC536227A4BCD93C52FB941FA35C0827D14AD00636'],
                                              'record_sha256': '36A0469B12893D325A2B1A2FCFA20DABE245EF96C9684E1E09CEFA524B0A142F',
                                              'record_size': 64}},
                        '15:1661': {'current': {'literal_count': 1,
                                                'literal_utf16le_sha256': ['534BB226EC238004EAA0E14E94A275DE407A87576B1C4DD2DE1F56C3CE6D0037'],
                                                'record_sha256': 'A5A82502AEF382AF5BF6207C8EDB574081F19C0A57613B22FDECEC6C90F31A30',
                                                'record_size': 88},
                                    'pc_jp': {'literal_count': 1,
                                              'literal_utf16le_sha256': ['CAAB97D48585158D4285F84E7BE8C65B88C07E128D8519274C1A27642A59F889'],
                                              'record_sha256': '0877EE29C3F8E9C77B50A3EA6F7E4941C440AECA6FB9208D7BDADE47DD50574C',
                                              'record_size': 68}},
                        '15:1875': {'current': {'literal_count': 2,
                                                'literal_utf16le_sha256': ['42E30C561A36448D580BE54278AAE18E3EDF070A8CB5F34F4001609FDC47E1FA',
                                                                           'C873B612317188F07678645F740EDDCF0290845F32FF2CD01EDF3BA717B685FE'],
                                                'record_sha256': '49CE2A9CB2923B80078E1530B71D5AD7EB76A83725B45CA59B3D0434A7A71DAB',
                                                'record_size': 91},
                                    'pc_jp': {'literal_count': 2,
                                              'literal_utf16le_sha256': ['24D3D0252794F6550EAE498A136FE4B9135E59D00110F15A422164E4FC20AB0E',
                                                                         '8FC907129C0DCE36E86A01B1BF5FBFB9F4E4BB06B6CDE7EBE7CF296C63BF5807'],
                                              'record_sha256': '0CB0F1893E8E6CB03EF30186AA15705D1A7D4E7A5C74C1D22B6A69924F3CD635',
                                              'record_size': 79}},
                        '15:1890': {'current': {'literal_count': 2,
                                                'literal_utf16le_sha256': ['CB1E902196295CD17FAA6DA16E6E7D4F5701DF19CB6C7300E547D442EE1E009E',
                                                                           'C873B612317188F07678645F740EDDCF0290845F32FF2CD01EDF3BA717B685FE'],
                                                'record_sha256': '3C6922639C05E2D00990DC4D9343A046462E89F03B728B15FDA66B57EE0D7A09',
                                                'record_size': 91},
                                    'pc_jp': {'literal_count': 2,
                                              'literal_utf16le_sha256': ['C9C0882720D56A60C4C2580007D41CDA5BFA38076BD8C91772672064C5651C27',
                                                                         '8FC907129C0DCE36E86A01B1BF5FBFB9F4E4BB06B6CDE7EBE7CF296C63BF5807'],
                                              'record_sha256': 'CCFE4919C0B1EEB723957A655630210F50FEC63A5775D3082F367DBA09921595',
                                              'record_size': 79}},
                        '15:1899': {'current': {'literal_count': 3,
                                                'literal_utf16le_sha256': ['A1A72076831E29EF6B42DF806A89FE106268A2091CC13EF1A1AE8718077B464C',
                                                                           'A3020FE388FAC6828084005686BFB468B48C8540918B04250FBECC4A2616CFA0',
                                                                           '8F43738D4F2DC07D742CF8784D22AF4FD834D9F8170886BB9BCF7432E209BB80'],
                                                'record_sha256': '1917BEA7D2DFF193FE90996467D6B91BC0E40FDBF99729BC49C8ADA78FDBF944',
                                                'record_size': 69},
                                    'pc_jp': {'literal_count': 3,
                                              'literal_utf16le_sha256': ['DB75DB0585C09DF55E791199908AA0209EB5F401496AE69D065E5B7EF803A52B',
                                                                         'AECB395709AFD3E1ED7BF701AC1F9B32FF0C0763D9BB49EB80AA257CF088C189',
                                                                         '71BCEE3D1F30453BB10F883FD9E3423BA081DCDBA5E73B639976569DA7533C04'],
                                              'record_sha256': '32D02A3BCDA4D7F97A5D277E6BA1F3A1FBE4000810A0EF9498F276756BD498AA',
                                              'record_size': 65}}},
 'MSG_PK/JP/msggame.bin': {'15:1104': {'current': {'literal_count': 4,
                                                   'literal_utf16le_sha256': ['CE20CAB51C0AF6186BF449B8DF0278A041550602A0F0066F100046E66337E592',
                                                                              'E8896624F93641B7A06CFAD7508E413D48A4830EC4F79CB822CD572BDC73E2F1',
                                                                              'CAB57DDE07EE63BBF59BA2D9B6DB45C1A74600332EF271EBF47EB29ABF54FC04',
                                                                              '26FDD3D605D0B835F415B0D08B0FE74500A6CC0FDD47D13122A03589264929C7'],
                                                   'record_sha256': '0B59499FF1B35F4F50C7AF8EB99849D8C79B47477A1B8F86F3554CEBCE1C4134',
                                                   'record_size': 111},
                                       'pc_jp': {'literal_count': 4,
                                                 'literal_utf16le_sha256': ['DDEBDAB4768B502DD0192BA273002B4CB49825B6B3730F492B4238A3751596E5',
                                                                            '68C92EC1F0BA0C6FDECBE8F16E022F78DD7C2D5A7AE2E2409E164B2F414F1EE3',
                                                                            'FA433C89E61178902327DA13AF7DC0B09AEDE94A362DE11626C21700A658C353',
                                                                            '7D3C86D5FC73B1F41D9ADBC93F2E8EAD36B80C9A80624E412D7C0B46E6F9F9AC'],
                                                 'record_sha256': '7346C29D8762FA506AB6B4BE3CC125F89DA67EF0EE10EEB03CA2480D1153C1D8',
                                                 'record_size': 103}},
                           '15:1214': {'current': {'literal_count': 3,
                                                   'literal_utf16le_sha256': ['C83D8AA5B9BFE835F54C8D73AEF3FD47B1036E90BC9C50ED2D9B626664743758',
                                                                              'AE3D3A894925CC5F90E39525E1CED6D2C20579ADF8F11A9C5829D91DAE625AA8',
                                                                              'D4397B2C06EEDBD825389BA80B6E238B883DED656655072B07045CBF2ABFC235'],
                                                   'record_sha256': '38404B00DF7C696A833564EBAD325D05C2BF55C81A2C6E8A4DA6C04E76A7DE24',
                                                   'record_size': 104},
                                       'pc_jp': {'literal_count': 3,
                                                 'literal_utf16le_sha256': ['7D25F09A731001A34A06F6D054104397D2BD073469D690ACD6075DB6963790CC',
                                                                            '039BE30C84FE744A10D3A012AC820337C6D966B1C85C84D593CCE7D0FC7F3EAE',
                                                                            '2A0A5A9B79C9B22DAF3CB53D47365A8E494AB9FA0A4DCB8959AC39A0D3F8E7CF'],
                                                 'record_sha256': '6AED2C455E0CB5EC6102F6A8A5CC3CB9578515CC43CC56C5BAF2E9F7432839F5',
                                                 'record_size': 86}},
                           '15:1687': {'current': {'literal_count': 1,
                                                   'literal_utf16le_sha256': ['97E7A1505F9D0C95F3DCF8A7AC22ECB22E6A3198E0A6378C11E63F84B82F7A61'],
                                                   'record_sha256': 'C7C032E751ED632E7D84862A9037D5E291E523CC5F5E295D647789636A486FB9',
                                                   'record_size': 82},
                                       'pc_jp': {'literal_count': 1,
                                                 'literal_utf16le_sha256': ['9FF7C51F5E91F8E26AA4692C3ACBAE1774C87992F078BF5A3CD7D961E9B7788A'],
                                                 'record_sha256': 'BDD2CC7D50DDB4FDEAAE55A6E9A265BC6D33F92F3400E631598AD3600D455544',
                                                 'record_size': 64}},
                           '15:1689': {'current': {'literal_count': 1,
                                                   'literal_utf16le_sha256': ['CD971054E0B150F29082A447B77672D67C94E803A576A71D16E78718639F34E7'],
                                                   'record_sha256': '8A9640503C7A1262E7E90034701F0D449ECE382F9A91E24A4D7E6A5258508C37',
                                                   'record_size': 82},
                                       'pc_jp': {'literal_count': 1,
                                                 'literal_utf16le_sha256': ['A6A1929F01CB23E8F48098DC536227A4BCD93C52FB941FA35C0827D14AD00636'],
                                                 'record_sha256': '22D852801A8464F03313DB0A9FCA117B428FC60848B0DC9F9022F362457026EC',
                                                 'record_size': 64}},
                           '15:1691': {'current': {'literal_count': 1,
                                                   'literal_utf16le_sha256': ['534BB226EC238004EAA0E14E94A275DE407A87576B1C4DD2DE1F56C3CE6D0037'],
                                                   'record_sha256': 'C0467C6B6E0412638C283C5B7EC6CDEF62247E41774686F8D924A50844776892',
                                                   'record_size': 88},
                                       'pc_jp': {'literal_count': 1,
                                                 'literal_utf16le_sha256': ['CAAB97D48585158D4285F84E7BE8C65B88C07E128D8519274C1A27642A59F889'],
                                                 'record_sha256': '2A2C0FD106169F9E9D49792C4A5DA875193C7240D085B00D1D11594EAD859DBF',
                                                 'record_size': 68}},
                           '15:1929': {'current': {'literal_count': 3,
                                                   'literal_utf16le_sha256': ['A1A72076831E29EF6B42DF806A89FE106268A2091CC13EF1A1AE8718077B464C',
                                                                              'A3020FE388FAC6828084005686BFB468B48C8540918B04250FBECC4A2616CFA0',
                                                                              '8F43738D4F2DC07D742CF8784D22AF4FD834D9F8170886BB9BCF7432E209BB80'],
                                                   'record_sha256': '20C2096B8768044D60ACCEC24DFDC2BF00284D2E68C6F1291BD1EBDB7F6105E7',
                                                   'record_size': 69},
                                       'pc_jp': {'literal_count': 3,
                                                 'literal_utf16le_sha256': ['DB75DB0585C09DF55E791199908AA0209EB5F401496AE69D065E5B7EF803A52B',
                                                                            'AECB395709AFD3E1ED7BF701AC1F9B32FF0C0763D9BB49EB80AA257CF088C189',
                                                                            '71BCEE3D1F30453BB10F883FD9E3423BA081DCDBA5E73B639976569DA7533C04'],
                                                 'record_sha256': '7D9A73432FEBF755692B235EE2A4F059A5711B5AB32E9B5D8A1D628976563BA3',
                                                 'record_size': 65}},
                           '15:2257': {'current': {'literal_count': 3,
                                                   'literal_utf16le_sha256': ['626E878D0490F2FAB1088B0619BB509666324F13E3745FF13CADA40D20DDED1A',
                                                                              '4059A27597006565FC66948DC05009B800D0FD3D2516FBB52F8418065469174B',
                                                                              '6B5761C5A72BA0AD66C6C40045F314CCA75A02B0C8F9EBA2BFA5FEB51A10B7D4'],
                                                   'record_sha256': '8D13B2EF989CADCB6B4A6FF29B1A922F4AEE51B764201E933425A1776C32D6C2',
                                                   'record_size': 106},
                                       'pc_jp': {'literal_count': 3,
                                                 'literal_utf16le_sha256': ['A2C674D82C7B508E4B6BE265BD050A2853E6FD1F6B3578B24BD3B45D629DB3B8',
                                                                            'D25D1746B34D7324734AB84E2BB17FB1EFB7AC1880F721CE9213393D3086ED61',
                                                                            '9A6126D32744C35FAF9494E0F0D5ECDAD6A91D7CAAD09D9B1186918369373451'],
                                                 'record_sha256': 'A38CD6602FBB3D5660F1DFC87B453D5E6342CD2110AA035449D0136CA28CA29E',
                                                 'record_size': 68}},
                           '15:2258': {'current': {'literal_count': 3,
                                                   'literal_utf16le_sha256': ['626E878D0490F2FAB1088B0619BB509666324F13E3745FF13CADA40D20DDED1A',
                                                                              '4059A27597006565FC66948DC05009B800D0FD3D2516FBB52F8418065469174B',
                                                                              '6B5761C5A72BA0AD66C6C40045F314CCA75A02B0C8F9EBA2BFA5FEB51A10B7D4'],
                                                   'record_sha256': '8D13B2EF989CADCB6B4A6FF29B1A922F4AEE51B764201E933425A1776C32D6C2',
                                                   'record_size': 106},
                                       'pc_jp': {'literal_count': 3,
                                                 'literal_utf16le_sha256': ['A2C674D82C7B508E4B6BE265BD050A2853E6FD1F6B3578B24BD3B45D629DB3B8',
                                                                            'D25D1746B34D7324734AB84E2BB17FB1EFB7AC1880F721CE9213393D3086ED61',
                                                                            '9A6126D32744C35FAF9494E0F0D5ECDAD6A91D7CAAD09D9B1186918369373451'],
                                                 'record_sha256': 'A38CD6602FBB3D5660F1DFC87B453D5E6342CD2110AA035449D0136CA28CA29E',
                                                 'record_size': 68}},
                           '15:2279': {'current': {'literal_count': 1,
                                                   'literal_utf16le_sha256': ['FA971FA9716C3AD615142FC783E16DDA2655E5B95B19A5BFBB87F22958ABC2ED'],
                                                   'record_sha256': 'AF56A4373BEC7CD2008AB5C555FD97CA9F4B2674BCE8F904EB57390DA680C0FB',
                                                   'record_size': 77},
                                       'pc_jp': {'literal_count': 1,
                                                 'literal_utf16le_sha256': ['D1CFCAA823504C0C085AA06495A15793A1DA7DC0B3B88AA6ADBA53440C80BED9'],
                                                 'record_sha256': 'DE33DAFF1F30997F7E36CFB1FE61B6234CAEC5D426F7F01E121DDDF84CA945D4',
                                                 'record_size': 73}}}}
TARGET_OUTPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {'MSG/JP/msggame.bin': {'raw_sha256': '0AE069E9FF45C783A9107D84D82F501C2FFA06B0D7AFAA1B218116D3786AF734',
                        'raw_size': 1498508,
                        'sha256': '94125746E07A8235ECF0636CDC803BADD3D3552C0617347CC7762AB742DB4C3B',
                        'size': 1504410},
 'MSG_PK/JP/msggame.bin': {'raw_sha256': '5797EC4CDDF523766FBF12585D6DD86E4C39DA79F55648D12AE0C45EF023C844',
                           'raw_size': 1799432,
                           'sha256': '68AAB9E828B574E5E805BC7D054284E16328D4BDF5FA41A44CAE4F29E953A667',
                           'size': 1806514}}
RECORD_EVIDENCE_SHA256 = "1F1D4D3B6B8B7D489B3E01245E19AA927CD57D0FFD68764EB119A3F6154C9807"
RECORD_EVIDENCE_COUNT = 18


def proposal_sort_key(proposal: Proposal) -> tuple[int, int, int, int]:
    return (
        RESOURCE_ORDER.index(proposal.resource),
        proposal.coordinate[0],
        proposal.coordinate[1],
        proposal.literal_index,
    )


def collect_proposals() -> tuple[Proposal, ...]:
    all_proposals = tuple(sorted(APPLY_PROPOSALS + HOLD_PROPOSALS, key=proposal_sort_key))
    require(len(APPLY_PROPOSALS) == 17, "apply scope count differs")
    require(len(HOLD_PROPOSALS) == 1, "hold scope count differs")
    require(len(all_proposals) == RECORD_EVIDENCE_COUNT, "proposal scope count differs")
    identities = {(item.resource, item.coordinate, item.literal_index) for item in all_proposals}
    require(len(identities) == len(all_proposals), "duplicate candidate literal slot")
    require(all(item.resource in RESOURCE_ORDER for item in all_proposals), "unknown proposal resource")
    require(all(item.disposition in {"apply", "hold_width_excess"} for item in all_proposals), "unknown disposition")
    assert_no_scope_overlap(all_proposals)
    return all_proposals


def assert_no_scope_overlap(proposals: Sequence[Proposal]) -> None:
    for proposal in proposals:
        for workstream, by_resource in EXACT_REUSED_COORDINATES.items():
            if proposal.coordinate in by_resource.get(proposal.resource, frozenset()):
                raise CandidateError(f"candidate coordinate overlaps {workstream}: {proposal.resource}:{proposal.coordinate_text}")
        for workstream, by_resource in CONSERVATIVE_REUSED_BLOCKS.items():
            if proposal.coordinate[0] in by_resource.get(proposal.resource, frozenset()):
                raise CandidateError(
                    f"candidate coordinate is inside {workstream} conservative exclusion: "
                    f"{proposal.resource}:{proposal.coordinate_text}"
                )


PROPOSALS = collect_proposals()


def literal_hashes(record: Any) -> list[str]:
    return [sha256_bytes(value.encode("utf-16-le")) for value in W27.literal_texts(record)]


def opaque_hexes(record: Any) -> list[str]:
    return [span.hex().upper() for span in W27.opaque_spans(record)]


def marker_topology_hex(record: Any) -> list[list[str]]:
    return [[start.hex().upper(), end.hex().upper()] for start, end in W27.marker_topology(record)]


def runtime_02xx_tokens(record: Any) -> list[str]:
    tokens: list[str] = []
    for span in W27.opaque_spans(record):
        for index, byte in enumerate(span[:-1]):
            if byte == 0x02:
                tokens.append(span[index : index + 2].hex().upper())
    return tokens


def complete_0143_commands(record: Any) -> list[str]:
    return list(W27.complete_0143_commands(W27.opaque_spans(record)))


def eaw_units(value: str) -> int:
    # Ambiguous-width characters are counted wide; this is deliberately
    # conservative for a CJK game UI.
    return sum(2 if unicodedata.east_asian_width(char) in {"F", "W", "A"} else 1 for char in value)


def layout_evidence(values: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]) -> dict[str, Any]:
    layout = W27.line_layout(values, advance)
    text = "".join(values)
    eaw_line_units = [eaw_units(line) for line in text.split("\n")]
    return {
        "line_count": layout["line_count"],
        "line_widths_px": list(layout["line_widths_px"]),
        "max_width_px": layout["max_width_px"],
        "eaw_line_units": eaw_line_units,
        "max_eaw_units": max(eaw_line_units, default=0),
        "wide_fallback_codepoints": list(layout["wide_fallback_codepoints"]),
    }


def record_fingerprint(record: Any) -> dict[str, Any]:
    literals = W27.literal_texts(record)
    return {
        "record_sha256": sha256_bytes(record.data),
        "record_size": len(record.data),
        "literal_count": len(literals),
        "literal_utf16le_sha256": literal_hashes(record),
        "marker_topology_hex": marker_topology_hex(record),
        "opaque_spans_hex": opaque_hexes(record),
        "terminator_hex": W27.RECORD_TERMINATOR.hex().upper(),
        "has_record_terminator": record.data.endswith(W27.RECORD_TERMINATOR),
        "manual_lf_count": "".join(literals).count("\n"),
        "manual_lf_count_by_literal": [value.count("\n") for value in literals],
        "runtime_02xx_tokens": runtime_02xx_tokens(record),
        "complete_0143_commands": complete_0143_commands(record),
    }


def minimal_preimage_pin(record: Any) -> dict[str, Any]:
    fingerprint = record_fingerprint(record)
    return {
        "record_sha256": fingerprint["record_sha256"],
        "record_size": fingerprint["record_size"],
        "literal_count": fingerprint["literal_count"],
        "literal_utf16le_sha256": fingerprint["literal_utf16le_sha256"],
    }


def validate_target_literal(value: str, label: str) -> None:
    require(value != "", f"empty target literal: {label}")
    encoded = value.encode("utf-16-le")
    require(W27.LITERAL_START not in encoded and W27.LITERAL_END not in encoded, f"reserved marker in target: {label}")
    require(all(unicodedata.category(char) != "Cc" or char in "\n\r" for char in value), f"control in target: {label}")


def rebuild_literal_only_record(source: Any, target_literals: tuple[str, ...]) -> bytes:
    """Rebuild text while copying every opaque byte unchanged.

    Wave 27's static helper intentionally strips ``01 43`` morphology commands;
    that behavior is forbidden here.  This local function is therefore the only
    record rewriter used by this candidate.
    """

    spans = W27.opaque_spans(source)
    require(len(spans) == len(target_literals) + 1, "literal/opaque topology differs")
    payload = bytearray()
    for span, literal in zip(spans, target_literals):
        payload.extend(span)
        payload.extend(W27.LITERAL_START)
        payload.extend(literal.encode("utf-16-le"))
        payload.extend(W27.LITERAL_END)
    payload.extend(spans[-1])
    return bytes(payload)


def load_inputs() -> tuple[
    Mapping[str, bytes],
    Mapping[str, Mapping[Coordinate, Any]],
    Mapping[str, Mapping[Coordinate, Any]],
]:
    packed: dict[str, bytes] = {}
    current_records: dict[str, Mapping[Coordinate, Any]] = {}
    pc_jp_records: dict[str, Mapping[Coordinate, Any]] = {}
    for resource in RESOURCE_ORDER:
        spec = RESOURCE_SPECS[resource]
        current_path = reject_switch(spec.current_path, f"W45 Steam PC {resource}")
        jp_path = reject_switch(spec.pc_jp_source, f"pristine PC Japanese {resource}")
        current = current_path.read_bytes()
        jp = jp_path.read_bytes()
        require(
            len(current) == spec.current_profile["size"] and sha256_bytes(current) == spec.current_profile["sha256"],
            f"W45 current profile differs: {resource}",
        )
        require(
            len(jp) == spec.pc_jp_profile["size"] and sha256_bytes(jp) == spec.pc_jp_profile["sha256"],
            f"PC-Japanese profile differs: {resource}",
        )
        W27.validate_raw_roundtrip(current, f"Block 15 W45 input {resource}")
        W27.validate_raw_roundtrip(jp, f"Block 15 PC-Japanese source {resource}")
        packed[resource] = current
        current_records[resource] = W27.records_by_coordinate(current)
        pc_jp_records[resource] = W27.records_by_coordinate(jp)
    return packed, current_records, pc_jp_records


def expected_pin_for(resource: str, coordinate: Coordinate) -> Mapping[str, Any]:
    resource_pins = RECORD_PREIMAGE_PINS.get(resource)
    require(resource_pins is not None, f"preimage pins absent for {resource}")
    pin = resource_pins.get(f"{coordinate[0]}:{coordinate[1]}")
    require(pin is not None, f"preimage pin absent for {resource}:{coordinate}")
    return pin


def validate_preimage_pin(proposal: Proposal, current: Any, pc_jp: Any, enforce: bool) -> Mapping[str, Any]:
    observed = {"current": minimal_preimage_pin(current), "pc_jp": minimal_preimage_pin(pc_jp)}
    if enforce:
        require(observed == expected_pin_for(proposal.resource, proposal.coordinate), f"record/literal preimage differs: {proposal.resource}:{proposal.slot_text}")
    return observed


def validate_immutable_structure(before: Any, after: Any, label: str) -> None:
    before_literals = W27.literal_texts(before)
    after_literals = W27.literal_texts(after)
    require(len(after_literals) == len(before_literals), f"literal count differs: {label}")
    require(
        [value.count("\n") for value in after_literals] == [value.count("\n") for value in before_literals],
        f"manual LF per literal differs: {label}",
    )
    require("".join(after_literals).count("\n") == "".join(before_literals).count("\n"), f"manual LF count differs: {label}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"marker topology differs: {label}")
    require(W27.opaque_spans(after) == W27.opaque_spans(before), f"opaque bytes differ: {label}")
    require(after.data.endswith(W27.RECORD_TERMINATOR) and before.data.endswith(W27.RECORD_TERMINATOR), f"record terminator differs: {label}")
    require(runtime_02xx_tokens(after) == runtime_02xx_tokens(before), f"02xx runtime tokens differ: {label}")
    require(complete_0143_commands(after) == complete_0143_commands(before), f"0143 morphology commands differ: {label}")


def validate_proposal(
    proposal: Proposal,
    current: Any,
    pc_jp: Any,
    advance: Callable[[str], tuple[int, bool]],
    enforce_pins: bool,
) -> tuple[bytes, Mapping[str, Any], Mapping[str, Any]]:
    label = f"{proposal.resource}:{proposal.slot_text}"
    require(proposal.coordinate == (current.block_id, current.record_id), f"current coordinate differs: {label}")
    require(proposal.coordinate == (pc_jp.block_id, pc_jp.record_id), f"PC-Japanese coordinate differs: {label}")
    preimage_pin = validate_preimage_pin(proposal, current, pc_jp, enforce_pins)

    current_literals = W27.literal_texts(current)
    source_literals = W27.literal_texts(pc_jp)
    require(0 <= proposal.literal_index < len(current_literals), f"literal slot is absent: {label}")
    require(len(current_literals) == len(source_literals), f"current/PC-Japanese literal count differs: {label}")
    require(current.data.endswith(W27.RECORD_TERMINATOR), f"current terminator is absent: {label}")
    require(pc_jp.data.endswith(W27.RECORD_TERMINATOR), f"PC-Japanese terminator is absent: {label}")
    require("".join(source_literals).count(proposal.pc_jp_anchor) >= 1, f"PC-Japanese semantic anchor differs: {label}")

    current_slot = current_literals[proposal.literal_index]
    require(current_slot.count(proposal.old) == 1, f"literal preimage occurrence differs: {label}")
    require(sum(value.count(proposal.old) for value in current_literals) == 1, f"record preimage occurrence differs: {label}")
    target_literals = list(current_literals)
    target_literals[proposal.literal_index] = current_slot.replace(proposal.old, proposal.new)
    target_literals_tuple = tuple(target_literals)
    require(target_literals_tuple != current_literals, f"target is unchanged: {label}")
    require(len(target_literals_tuple) == len(current_literals), f"literal count differs before rebuild: {label}")
    for value in target_literals_tuple:
        validate_target_literal(value, label)

    current_layout = layout_evidence(current_literals, advance)
    target_layout = layout_evidence(target_literals_tuple, advance)
    width_ok = (
        target_layout["line_count"] == current_layout["line_count"]
        and target_layout["max_width_px"] <= current_layout["max_width_px"]
        and target_layout["max_eaw_units"] <= current_layout["max_eaw_units"]
        and target_layout["max_width_px"] <= CONSERVATIVE_MAX_LINE_PX
        and target_layout["max_eaw_units"] <= CONSERVATIVE_MAX_EAW_UNITS
        and not target_layout["wide_fallback_codepoints"]
    )
    if proposal.disposition == "apply":
        require(width_ok, f"conservative width/EAW guard differs: {label}")
    else:
        require(proposal.disposition == "hold_width_excess" and not width_ok, f"hold disposition differs: {label}")

    rebuilt = rebuild_literal_only_record(current, target_literals_tuple)
    target = W27.MsgGameRecord(current.block_id, current.record_id, current.relative_offset, rebuilt)
    require(W27.literal_texts(target) == target_literals_tuple, f"rebuilt literals differ: {label}")
    validate_immutable_structure(current, target, label)

    row = {
        "family": proposal.family,
        "resource": proposal.resource,
        "coordinate": proposal.coordinate_text,
        "literal_index": proposal.literal_index,
        "slot": proposal.slot_text,
        "disposition": proposal.disposition,
        "reason": proposal.reason,
        "semantic_anchor_pc_jp": proposal.pc_jp_anchor,
        "replacement": {"old": proposal.old, "new": proposal.new, "current_slot_occurrences": current_slot.count(proposal.old)},
        "preimage_pin": preimage_pin,
        "current_record": record_fingerprint(current),
        "pc_jp_record": record_fingerprint(pc_jp),
        "proposed_target_record": record_fingerprint(target),
        "width_eaw": {
            "current": current_layout,
            "proposed": target_layout,
            "conservative_max_line_px": CONSERVATIVE_MAX_LINE_PX,
            "conservative_max_eaw_units": CONSERVATIVE_MAX_EAW_UNITS,
            "eligible_for_apply": width_ok,
        },
        "runtime_real_game_qa_required": True,
    }
    return rebuilt, row, preimage_pin


def observed_profile(packed: bytes, raw: bytes) -> dict[str, Any]:
    return {
        "size": len(packed),
        "sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
    }


def build_unpinned(enforce_pins: bool) -> CandidateBundle:
    current_packed, current_records, pc_jp_records = load_inputs()
    advance, font = W27.load_font_advance()
    replacements: dict[str, dict[Coordinate, bytes]] = {resource: {} for resource in RESOURCE_ORDER}
    rows: list[Mapping[str, Any]] = []
    preimage_pins: dict[str, dict[str, Mapping[str, Any]]] = {resource: {} for resource in RESOURCE_ORDER}

    for proposal in PROPOSALS:
        current = current_records[proposal.resource].get(proposal.coordinate)
        pc_jp = pc_jp_records[proposal.resource].get(proposal.coordinate)
        require(current is not None and pc_jp is not None, f"candidate record is absent: {proposal.resource}:{proposal.slot_text}")
        target, row, pin = validate_proposal(proposal, current, pc_jp, advance, enforce_pins)
        key = proposal.coordinate_text
        require(key not in preimage_pins[proposal.resource], f"duplicate preimage coordinate: {proposal.resource}:{key}")
        preimage_pins[proposal.resource][key] = pin
        rows.append(row)
        if proposal.disposition == "apply":
            require(proposal.coordinate not in replacements[proposal.resource], f"duplicate output coordinate: {proposal.resource}:{key}")
            replacements[proposal.resource][proposal.coordinate] = target

    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource in RESOURCE_ORDER:
        candidate = W27.rebuild_packed_msggame(current_packed[resource], replacements[resource])
        W27.validate_raw_roundtrip(candidate, f"Block 15 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        after_records = W27.records_by_coordinate(candidate)
        changed = {
            coordinate
            for coordinate, before in current_records[resource].items()
            if after_records[coordinate].data != before.data
        }
        expected = {proposal.coordinate for proposal in APPLY_PROPOSALS if proposal.resource == resource}
        require(changed == expected and set(after_records) == set(current_records[resource]), f"changed record scope differs: {resource}")
        for hold in HOLD_PROPOSALS:
            if hold.resource == resource:
                require(after_records[hold.coordinate].data == current_records[resource][hold.coordinate].data, f"held record changed: {resource}:{hold.slot_text}")
        packed_output[resource] = candidate
        raw_output[resource] = raw

    output_profiles = {resource: observed_profile(packed_output[resource], raw_output[resource]) for resource in RESOURCE_ORDER}
    evidence_sha256 = sha256_bytes(canonical_json(rows))
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC only",
            "pc_jp_primary": True,
            "pc_en_sc_tc_context_only": True,
            "switch_paths_or_translations_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "pinned_format_helper_sha256": W27_HELPER_SHA256,
        "font": font,
        "w45_inputs": {resource: RESOURCE_SPECS[resource].current_profile for resource in RESOURCE_ORDER},
        "pc_jp_sources": {resource: RESOURCE_SPECS[resource].pc_jp_profile for resource in RESOURCE_ORDER},
        "width_eaw_policy": {
            "target_line_count_equals_current": True,
            "target_max_width_must_not_expand": True,
            "target_max_eaw_must_not_expand": True,
            "max_line_px": CONSERVATIVE_MAX_LINE_PX,
            "max_eaw_units": CONSERVATIVE_MAX_EAW_UNITS,
            "wide_fallback_glyphs_forbidden": True,
        },
        "conflict_guard": {
            "W46_exact_coordinate_exclusion": {resource: [f"{block}:{record}" for block, record in sorted(coords)] for resource, coords in EXACT_REUSED_COORDINATES["W46"].items()},
            "conservative_excluded_blocks": {workstream: {resource: sorted(blocks) for resource, blocks in by_resource.items()} for workstream, by_resource in CONSERVATIVE_REUSED_BLOCKS.items()},
        },
        "outputs": output_profiles,
        "proposal_count": len(PROPOSALS),
        "apply_record_count": len(APPLY_PROPOSALS),
        "hold_record_count": len(HOLD_PROPOSALS),
        "apply_record_count_by_resource": {resource: sum(item.resource == resource for item in APPLY_PROPOSALS) for resource in RESOURCE_ORDER},
        "record_evidence_sha256": evidence_sha256,
        "records": rows,
        "runtime_real_game_qa_required_before_application": True,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": list(RESOURCE_ORDER),
        "w45_inputs": {resource: RESOURCE_SPECS[resource].current_profile for resource in RESOURCE_ORDER},
        "outputs": output_profiles,
        "apply_coordinates": {resource: [item.slot_text for item in APPLY_PROPOSALS if item.resource == resource] for resource in RESOURCE_ORDER},
        "hold_coordinates": {resource: [item.slot_text for item in HOLD_PROPOSALS if item.resource == resource] for resource in RESOURCE_ORDER},
        "apply_record_count": len(APPLY_PROPOSALS),
        "hold_record_count": len(HOLD_PROPOSALS),
        "record_evidence_sha256": evidence_sha256,
        "runtime_real_game_qa_required_before_application": True,
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_output, raw_output, audit, manifest, tuple(rows), preimage_pins)


def require_final_pins() -> None:
    require(set(RECORD_PREIMAGE_PINS) == set(RESOURCE_ORDER), "preimage pin resources differ")
    for resource in RESOURCE_ORDER:
        expected_coordinates = {proposal.coordinate_text for proposal in PROPOSALS if proposal.resource == resource}
        require(set(RECORD_PREIMAGE_PINS[resource]) == expected_coordinates, f"preimage pin coordinate scope differs: {resource}")
    require(set(TARGET_OUTPUT_PROFILES) == set(RESOURCE_ORDER), "target output profile resources differ")
    for resource in RESOURCE_ORDER:
        require({"size", "sha256", "raw_size", "raw_sha256"} <= set(TARGET_OUTPUT_PROFILES[resource]), f"target output profile absent: {resource}")
    require(len(RECORD_EVIDENCE_SHA256) == 64, "record evidence hash pin is absent")


def derive_pins() -> Mapping[str, Any]:
    bundle = build_unpinned(enforce_pins=False)
    return {
        "preimage_pins": bundle.preimage_pins,
        "target_output_profiles": {resource: observed_profile(bundle.packed[resource], bundle.raw[resource]) for resource in RESOURCE_ORDER},
        "record_evidence_count": len(bundle.rows),
        "record_evidence_sha256": sha256_bytes(canonical_json(bundle.rows)),
    }


def prepare_candidate() -> CandidateBundle:
    require_final_pins()
    bundle = build_unpinned(enforce_pins=True)
    for resource in RESOURCE_ORDER:
        actual = observed_profile(bundle.packed[resource], bundle.raw[resource])
        require(actual == TARGET_OUTPUT_PROFILES[resource], f"target output profile differs: {resource}")
    require(len(bundle.rows) == RECORD_EVIDENCE_COUNT, "record evidence count differs")
    require(sha256_bytes(canonical_json(bundle.rows)) == RECORD_EVIDENCE_SHA256, "record evidence differs")
    return bundle


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource in RESOURCE_ORDER:
            destination = stage / resource
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(bundle.packed[resource])
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            require_private(output, "existing candidate output")
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> Mapping[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require(output.is_dir(), f"private candidate is absent: {output}")
    for resource in RESOURCE_ORDER:
        path = output / resource
        require(path.is_file() and path.read_bytes() == bundle.packed[resource], f"private candidate resource differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "apply_record_count": len(APPLY_PROPOSALS),
        "hold_record_count": len(HOLD_PROPOSALS),
        "steam_game_resource_written": False,
    }


def diff_check() -> Mapping[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require(output.is_dir(), "private candidate is absent; build first")
    current_packed, current_records, _pc_jp_records = load_inputs()
    changed_coordinates: dict[str, list[str]] = {}
    for resource in RESOURCE_ORDER:
        candidate_path = output / resource
        candidate = candidate_path.read_bytes()
        require(candidate == bundle.packed[resource], f"private candidate drift: {resource}")
        candidate_records = W27.records_by_coordinate(candidate)
        changed = sorted(
            coordinate
            for coordinate, before in current_records[resource].items()
            if candidate_records[coordinate].data != before.data
        )
        expected = sorted(item.coordinate for item in APPLY_PROPOSALS if item.resource == resource)
        require(changed == expected, f"diff scope differs: {resource}")
        for hold in HOLD_PROPOSALS:
            if hold.resource == resource:
                require(candidate_records[hold.coordinate].data == current_records[resource][hold.coordinate].data, f"held record changed in diff: {resource}:{hold.slot_text}")
        changed_coordinates[resource] = [f"{block}:{record}" for block, record in changed]
        require(candidate != current_packed[resource], f"candidate has no packed diff: {resource}")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_coordinates": changed_coordinates,
        "apply_record_count": len(APPLY_PROPOSALS),
        "hold_record_count": len(HOLD_PROPOSALS),
        "opaque_runtime_markers_verified_immutable": True,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("derive-pins", "build", "verify-private", "diff-check"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result = derive_pins()
    elif args.command == "build":
        output = write_candidate(prepare_candidate())
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "apply_record_count": len(APPLY_PROPOSALS),
            "hold_record_count": len(HOLD_PROPOSALS),
            "steam_game_resource_written": False,
        }
    elif args.command == "verify-private":
        result = verify_private()
    else:
        result = diff_check()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
