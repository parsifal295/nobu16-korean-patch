#!/usr/bin/env python3
"""Build PC-only dialogue-quality wave four on top of static grammar wave three.

The records in this wave preserve runtime person/faction/month references and
colour spans byte-for-byte.  Most plans replace only pinned UTF-16 literals.
The small runtime-suffix subset also removes only its individually pinned
Japanese ``01 43`` inflection commands; Steam itself is never written.
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
from dataclasses import asdict, dataclass
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
MSGGAME = REPO / "workstreams" / "msggame"
WAVE3_SCRIPT = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_grammar_wave3_static_v1"
    / "build_pc_dialogue_runtime_grammar_wave3_static_v1.py"
)
sys.path.insert(0, str(MSGGAME))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_record_literals,
)


def load_wave3():
    spec = importlib.util.spec_from_file_location("pc_dialogue_wave3_static", WAVE3_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Wave 3 builder: {WAVE3_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE3 = load_wave3()
DEFAULT_STEAM_ROOT = WAVE3.DEFAULT_STEAM_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave4.v1"
BASELINE_SHA256 = WAVE3.BASELINE_SHA256
PROFILE_PATHS = WAVE3.PROFILE_PATHS
CHANGED_PATHS = WAVE3.CHANGED_PATHS

# Generated from the source-gated candidate and pinned for all future builds.
TARGET_SHA256 = {
    **BASELINE_SHA256,
    "MSG/JP/msggame.bin": "2C1211EC2C80356D9213058F669C9E030175235D35441E7C27CD54BDAB258B89",
    "MSG_PK/JP/msggame.bin": "2ADA436B30E50E0574140A9D7900DF6F63BA0F06BA1477644FC8729666179593",
}


class QualityError(ValueError):
    """A direct-PC source, record, or opaque-byte contract failed."""


@dataclass(frozen=True)
class LiteralChange:
    literal_id: int
    expected_text: str
    replacement: str


@dataclass(frozen=True)
class Anchor:
    block_id: int
    record_id: int
    expected_sha256: str


@dataclass(frozen=True)
class RemovedCommand:
    """One exact Japanese inflection command to remove from opaque bytes."""

    offset: int
    expected_hex: str

    @property
    def value(self) -> bytes:
        return bytes.fromhex(self.expected_hex)


@dataclass(frozen=True)
class QualityPlan:
    block_id: int
    record_id: int
    expected_sha256: str
    changes: tuple[LiteralChange, ...]
    base_anchor: Anchor | None = None
    remove_commands: tuple[RemovedCommand, ...] = ()

    @property
    def coordinate(self) -> tuple[int, int]:
        return self.block_id, self.record_id


def change(literal_id: int, expected_text: str, replacement: str) -> LiteralChange:
    if not replacement or "\x00" in replacement:
        raise ValueError("quality replacements must be non-empty visible text")
    return LiteralChange(literal_id, expected_text, replacement)


def anchor(block_id: int, record_id: int, expected_sha256: str) -> Anchor:
    return Anchor(block_id, record_id, expected_sha256)


def remove_command(offset: int, expected_hex: str) -> RemovedCommand:
    value = bytes.fromhex(expected_hex)
    if offset < 0 or len(value) != 6 or value[:2] != b"\x01\x43":
        raise ValueError(f"invalid removable 0143 command: {offset}, {expected_hex}")
    return RemovedCommand(offset, expected_hex.upper())


def plan(
    block_id: int,
    record_id: int,
    expected_sha256: str,
    changes: tuple[LiteralChange, ...],
    base_anchor: Anchor | None = None,
    remove_commands: tuple[RemovedCommand, ...] = (),
) -> QualityPlan:
    if not changes:
        raise ValueError(f"{block_id}:{record_id} has no literal changes")
    offsets = [item.offset for item in remove_commands]
    if len(offsets) != len(set(offsets)):
        raise ValueError(f"duplicate removable 0143 offset for {block_id}:{record_id}")
    return QualityPlan(block_id, record_id, expected_sha256, changes, base_anchor, remove_commands)


def copy_plan(
    block_id: int,
    record_id: int,
    expected_sha256: str,
    current_texts: tuple[str, ...],
    base_texts: tuple[str, ...],
    base_anchor: Anchor,
) -> QualityPlan:
    if len(current_texts) != len(base_texts):
        raise ValueError(f"literal-count mismatch in base-copy plan {block_id}:{record_id}")
    changes = tuple(
        change(index, current, base)
        for index, (current, base) in enumerate(zip(current_texts, base_texts))
        if current != base
    )
    return plan(block_id, record_id, expected_sha256, changes, base_anchor)


def rewrite_plan(
    block_id: int,
    record_id: int,
    expected_sha256: str,
    current_texts: tuple[str, ...],
    replacement_texts: tuple[str, ...],
    base_anchor: Anchor | None = None,
    remove_commands: tuple[RemovedCommand, ...] = (),
) -> QualityPlan:
    """Pin every current literal while replacing only the changed slots."""
    if len(current_texts) != len(replacement_texts):
        raise ValueError(f"literal-count mismatch in re-audited plan {block_id}:{record_id}")
    changes = tuple(
        change(index, current, replacement)
        for index, (current, replacement) in enumerate(zip(current_texts, replacement_texts))
        if current != replacement
    )
    return plan(
        block_id,
        record_id,
        expected_sha256,
        changes,
        base_anchor,
        remove_commands,
    )


# The twelve Base variants share a malformed JP runtime-suffix template.  The
# target and faction placeholders are separate non-0143 commands and remain
# intact; only the two pinned Japanese inflection commands are removed.
BASE_RUNTIME_SUFFIX_IDS = tuple(range(2083, 2095))
BASE_PLANS: tuple[QualityPlan, ...] = tuple(
    plan(
        6,
        record_id,
        "611712BFCC0A9585A147E3DF866F7675E9E1DF89AF8820B04A0A3C60422FDD77",
        (
            change(0, "를 함락시켜라", " 함락은 가능하겠나…"),
            change(1, "인가…\n", "\n"),
            change(2, "의 원군에는 감사", "의 원군에는 감사하겠소."),
        ),
        remove_commands=(
            remove_command(23, "014314020000"),
            remove_command(70, "0143EA010000"),
        ),
    )
    for record_id in BASE_RUNTIME_SUFFIX_IDS
)

# Every item below was compared directly to the pristine PC JP resource.  The
# block-6 items additionally pin the matching current PC-base Korean record;
# this is only a same-PC structural/translation anchor, never a Switch source.
PK_PLANS = (
    plan(
        6, 1543, "9ABB8F41AE2A95D3530CDEC6D49599340E8EDC5FEF238F7C4B8BB101B07D64EE",
        (change(1, ". 여러 나라까지 우리를 버릴지 모릅니다.\n그러니\n철저히 대비해야 합니다", "와 절연하게 되었으니\n여러 나라도 우리를 가만두지 않을 것이옵니다.\n여기는 만전을 기해야 하옵니다"),),
        anchor(6, 1537, "F1F5FBEA83A4CE71CA93B9AA0D91FA4ACFEA07B338C4BF741C54FF94EDFB6860"),
    ),
    plan(
        6, 1558, "EED99D3A71EC44E60742A29AB25313D4B92B07922B9C5D6E00A20EBED7108DCF",
        (change(1, ". 여러 나라가 우리를 노릴 수 있습니다……\n그러니\n철저히 대비해야 합니다", "와 절연한 이상\n여러 나라도 우리를 가만두지 않을 터…\n여기는 만전을 기해야 한다"),),
        anchor(6, 1552, "8C6526FE9478911B4F2D3291077C0A00E71D1841F2F121101A7478758776C4EF"),
    ),
    plan(
        6, 1616, "3D8430BB1321C229E3E4F05192DD0C7B27410A716EC08D2772E59CDB645299F4",
        (change(1, ". 각오는 하되\n우리도 자립해야 합니다", "와 운명을 함께할 각오는 하되\n우리는 우리대로 서야 하옵니다"),),
        anchor(6, 1610, "A8D913DDE69358BE0678F2F89A8AAA25307A94AB0E4E561125BDE0874CD004A5"),
    ),
    plan(
        6, 1637, "FF16E28005A774C4DD83FBA4052CEDDC34A245B517855DB097E90A39CBB3C81E",
        (change(1, ". 두 가문을 잇는 인연의 상징입니다.\n그 이야기는 나중에 하고\n먼저 연회를 열지요", "의 부부는\n당가와 그 가문을 잇는 유대의 상징이지요.\n아니, 그런 얘기는 나중에 하고 우선 연회부터 할까요"),),
        anchor(6, 1631, "43F96750330D53986AFAB991EB7D7DDE82B920388F4B42007DF73CE3012D3C05"),
    ),
    plan(
        6, 1641, "B9D19465D64D93E3E55B2DF69EE21E6F71EA5D15E97C956E2555F9967FCE944E",
        (change(1, ". 이제 두 가문은\n한 식구이자 동맹으로\n함께 나아갑시다", "의 혼약이\n이루어졌으니, 양가는\n앞으로 한집안, 맹우로서 함께 걸어가겠지요"),),
        anchor(6, 1635, "97D99669B91DCBC68180CBF1E94C082C54A0BEB41D4DC0B3E88B032C2FBBE51E"),
    ),
    plan(
        6, 2820, "3F351D9778E0AFE0DA7DA7380703A894A9308088DB432E5D5754D42E27DA5ECD",
        (change(0, "알겠다\n", "잘 알겠소\n"), change(1, ". 인연도 여기까지입니다.", "와의 관계도 여기까지다")),
        anchor(6, 2814, "C9E1285C22E619E5644CEAE89EEFF4DDA14692C5821274F21A6460CDB9F3D6AF"),
    ),
    plan(
        6, 2821, "FB77E6F3C71B2B16B196D05376A7F1175C7A28E62300467EDCAE722287646CA3",
        (change(1, ". 맹약을 해소하겠습니다.", "와의 맹약을 해소합시다"),),
        anchor(6, 2815, "A26BE3AB8655EBF0EB65C632E02A1369CD994C1306F1F4058C940C5F02FEE0B9"),
    ),
    plan(
        6, 2822, "D2B1C9C65DD5701B8FEBA7E76A51D1B8ECCAF745EAEF13BFE219311FC9B98FC2",
        (change(0, "알겠다\n", "잘 알겠소\n"), change(1, ". 이제 동맹은 무효입니다.", "와의 동맹은 파기한다")),
        anchor(6, 2816, "5F3A53FF66FF6D1562FC59ACD3B4428168237C0FDA0E78019A503CFCC406FA62"),
    ),
    plan(
        6, 2844, "3F351D9778E0AFE0DA7DA7380703A894A9308088DB432E5D5754D42E27DA5ECD",
        (change(0, "알겠다\n", "잘 알겠소\n"), change(1, ". 인연도 여기까지입니다.", "와의 관계도 여기까지다")),
        anchor(6, 2838, "C9E1285C22E619E5644CEAE89EEFF4DDA14692C5821274F21A6460CDB9F3D6AF"),
    ),
    plan(
        6, 2845, "FB77E6F3C71B2B16B196D05376A7F1175C7A28E62300467EDCAE722287646CA3",
        (change(1, ". 맹약을 해소하겠습니다.", "와의 맹약을 해소합시다"),),
        anchor(6, 2839, "A26BE3AB8655EBF0EB65C632E02A1369CD994C1306F1F4058C940C5F02FEE0B9"),
    ),
    plan(
        6, 2846, "D2B1C9C65DD5701B8FEBA7E76A51D1B8ECCAF745EAEF13BFE219311FC9B98FC2",
        (change(0, "알겠다\n", "잘 알겠소\n"), change(1, ". 이제 동맹은 무효입니다.", "와의 동맹은 파기한다")),
        anchor(6, 2840, "5F3A53FF66FF6D1562FC59ACD3B4428168237C0FDA0E78019A503CFCC406FA62"),
    ),
    plan(
        6, 3065, "FE0E8373DF2433BD2EF69BF20A092F050B529715EDAC68F114F69858B22435E1",
        (change(1, ". 혼인으로 맺은 동맹도\n앞으로", "와의\n혼인에 의한 동맹도"),),
        anchor(6, 3059, "0C0BCFC4BCC480F31EDB246C7EDBF80228988C31BC9278F19472143A2CC6CE99"),
    ),
    plan(
        6, 3085, "7A5A413AFAE0269C0400BE0764DA445202975312F71905E0B28E95F04DFA753F",
        (change(2, ". 그 취향을 알다니,\n놀라울 따름입니다.", "개월 후에는\n사라져 버리는 것이군요…"),),
        anchor(6, 3079, "CC979F060C5A02B417197CC75CC2CD8C75F68BB310DF197DF2A967278E6090B3"),
    ),
    plan(
        17, 943, "A2B309C2C90D74C9219981BB3465EE1CEC8E41FF85D08FD6FD92D3431856CA90",
        (change(2, ".\n하지만 이토록 큰 희생을 치르다니……", "를 장악했다고 할 수 있겠군.\n하지만 이토록 큰 희생을 치르다니……"),),
    ),
    plan(
        17, 944, "BCB4A3695CF82FD8D472E48664AAAA1E52D0D00960986CB24DA7220DE31F678D",
        (change(2, ".\n이로써 처음 목적은 달성했군.", "를 완전히 장악했소.\n처음 목표는 달성했다고 할 수 있겠소."),),
    ),
    plan(
        17, 1004, "5DAE6F80023ACA35DAD4E45F2BD96F0812ECF2BD227F97B64FFF17B667E5DEBA",
        (change(1, "의 정예 부대군.", "의 정예군이로군."),),
    ),
)

# Further direct-PC anchors discovered by the full PK person-dialogue audit.
# Each pair has the identical pristine PC JP literal tuple; only the PK Korean
# record was substituted with an unrelated sentence or a label fragment.
PK_PLANS += (
    plan(2, 273, "5BF6140C94EDA42A8C0CC96992D05BC976A57CDC7D44206EFA3219A3FF2AAB99", (change(1, ".\n완벽한 성과로 이끌겠다.", "의 보좌를 맡아\n완벽한 성과를 이루리라"),), anchor(2, 267, "8E41B4A64A14A231F3AF38B1C040637E4D96D2C4ACC57945538D153DCD8D1E4D")),
    copy_plan(6, 442, "083BB4247F35D00670F6EB45C68C1F2ADF26A04528E170801B700D8C73DC4204", ("상을 받아도 마냥\n기뻐할 수는 없군……",), ("…이 또한\n주종의 숙명이라면",), anchor(6, 440, "13126DEA7B6AD532E0B87656588899FF8D87800E07B18A8B8BE3AA36EC998C04")),
    copy_plan(6, 800, "6F93BB0A47A151C707E387F506ECD3C9227241FD8055C19D34656164612E6FF7", ("나를 품을 만한\n그릇은 아닌가 보군……",), ("…무슨 일인가?\n돌아가고 싶다만",), anchor(6, 798, "80CA07C6803C7E706B7B7014B9A0B2BC0CDB8D50C18D485403370F30C456029E")),
    copy_plan(6, 802, "FA734188754D0FBAA0D0E1D01877D0D996907801FCCB3DF20D8C9377E539FCC0", ("내 헌책을 바칠 주군은\n따로 있는 듯하군……",), ("…후우, 이 자리조차\n고통스럽게 느껴지는구나",), anchor(6, 800, "9ACE1A2D306B448D1FC61E8645D5D16E3F0844592856ACB230F236180E45A0C1")),
    copy_plan(6, 876, "7EF749C4EF6B0242853557E731795530424EE7E2013802D013184D800209478E", ("평생을 전장에서\n살았건만……",), ("이런 몸 상태로는\n싸움 따위…끄으윽",), anchor(6, 874, "A8B59FC1D8FEEEDAD9F70EA00C3C38EBD9D07F235620B8FDC1826F39CE52E38F")),
    copy_plan(6, 1027, "5EF3F67A9676C7A66971127F139552C2B9B7DD50E360AE864D3741AF8D491C7D", ("누가 혼인하는 거지?",), ("어머… 멋진 일이네",), anchor(6, 1025, "A7440F4868F39B1E1E573236511FA6A4B8D0DC93BF9E1C835924A2215CD08F99")),
    copy_plan(6, 1041, "D3BB837CF7492B65D08B4D933E74466EB054D95A078A1D19BBA06312F0D11669", ("다음 세대로 넘어가는 건가……",), ("서, 설마…",), anchor(6, 1039, "1CD4E325908DAEE88C4D22294CA40B5A8BB80399F985DA6B280A4CC373EF1F11")),
    copy_plan(6, 1051, "D3BB837CF7492B65D08B4D933E74466EB054D95A078A1D19BBA06312F0D11669", ("다음 세대로 넘어가는 건가……",), ("서, 설마…",), anchor(6, 1049, "1CD4E325908DAEE88C4D22294CA40B5A8BB80399F985DA6B280A4CC373EF1F11")),
    copy_plan(6, 1055, "D3BB837CF7492B65D08B4D933E74466EB054D95A078A1D19BBA06312F0D11669", ("다음 세대로 넘어가는 건가……",), ("서, 설마…",), anchor(6, 1053, "1CD4E325908DAEE88C4D22294CA40B5A8BB80399F985DA6B280A4CC373EF1F11")),
    copy_plan(6, 1076, "DE81DE98D81AAD28C64C8BF0349230970588F1B5EF74611B449F38FDC4DEF8AB", ("누군가 추방되었군요",), ("쓸쓸해집니다…",), anchor(6, 1074, "14ACC284931EA72466346066765001E2B37AD388409EDF9D67DC45E9A683229F")),
    copy_plan(6, 1086, "EA79713BEC822891FEDD7827DEC783533C7A874CCF7A1579B1A31FA5E832FEAB", ("내가 나설\n기회가 있으려나?",), ("좋은 군단에\n소속되고 싶구나",), anchor(6, 1084, "1DDBAEC09270D7F24D7199BA00B90E98E90A7EB9F8769927206784FCFBC9D005")),
    copy_plan(6, 1088, "EA79713BEC822891FEDD7827DEC783533C7A874CCF7A1579B1A31FA5E832FEAB", ("내가 나설\n기회가 있으려나?",), ("좋은 군단에\n소속되고 싶구나",), anchor(6, 1086, "1DDBAEC09270D7F24D7199BA00B90E98E90A7EB9F8769927206784FCFBC9D005")),
    copy_plan(6, 2793, "66AA170CDCA7A1AE18B5718A4C5E2B61625860A79CFE2D0E15C3AE6771A55F09", ("이", ". 휘하로 들어갔습니다"), ("이", "의 산하에"), anchor(6, 2787, "07EEDDDBA7789A9A5A1E01304BF4C32648DF721B757C327487640FE2B91B1089")),
    copy_plan(6, 2856, "0FB500CA6BD49B5F164B2633E0756F135F3D3B3CAF658587EF6E5085F9DFC785", ("좋다, 결정했다\n공격할 세력:", ". 출진하자"), ("음, 분명히 받들었소\n우리는", "를 공격하도록 하지"), anchor(6, 2850, "2FE85CB576C76B78B0846670EAD688187C942871EB21974E07DD8C8CBB016D82")),
    copy_plan(6, 2857, "B57A9B96A0ABF7CEFA4297CBFD9C90D51012704009FD16F3177391049DFBDD87", ("알겠습니다\n", ". 공격합시다"), ("알겠습니다\n", "를 공격합시다"), anchor(6, 2851, "9A5B37B4A6CE2F28688A9314C2E623A24983D156488028386BCA3CD3B380CD0F")),
    copy_plan(6, 2858, "460E788AEF700686F934A1218323541D7A544841A224203B519701E654C631EE", ("알겠다\n", ". 공격하겠습니다"), ("잘 알겠소\n", "를 공격하자꾸나"), anchor(6, 2852, "06C9AFE9B921EAD6E0F922E124C17A00ED0BC37CDAD25926F895D3173027F815")),
    copy_plan(6, 2905, "A13D90F7C1CF1077DCBA3E32F3B0D7932E292E6B3396B641B9F5623F63E762CF", (": 단교를 통고해 왔습니까?\n배후 세력:", ". 그 사주가 분명합니다"), ("이(가) 단교를 통고해 왔다고?\n그렇다면…", "의 농간이군요"), anchor(6, 2899, "A8AC98C7856B11B3CC8A7EC7CE8B8A4695DF68DDD317CBF8A7363FFEFFF18F02")),
    copy_plan(6, 2906, "3EF7C8EE5A05565054169467D47021B8581BAA853F1200752AB8B2630993E690", (": 단교한다고……?\n배후 세력:", ". 그 사주인가?"), ("이(가) 관계를 끊겠다…고?\n…", "의 농간인가"), anchor(6, 2900, "02333E110733A44B84E3F8612B5AC1BC7B65FFB2294DC99CB43C308D79619F28")),
    copy_plan(6, 2971, "66B9A56152613707ECD0DE9A68DA5CD9E63DB31EF0264FE5D85B7110068441E7", ("에게서\n", ". 그 휘하에서 전향을 청합니다.\n확인하십시오"), ("에게서\n", "에서 주군을 바꾸기를 청하는 사자가\n와 있습니다. 확인해 주십시오"), anchor(6, 2965, "52B91F7758AB042BB191BD133CE11703CA2A33FAE1231F6C290768C06B7DFF81")),
    copy_plan(6, 3078, "754A6F171B9140FAF073A418810BD80AD0D53C81A73DC4A4B7FDF310D7B54B26", ("참으로 유감이지만", "이(가) 당가를\n떠나셨기에,", ". 해당 동맹은\n앞으로", "개월 남았습니다."), ("참으로 유감이지만", "이(가) 당가를\n떠나셨기에,", "와의 동맹도\n남은", "개월이 되었사옵니다"), anchor(6, 3072, "1B4E6D4ABF10379E178C5EBE3C6E6DEC31D23E4822DAAA0BEB9C5AFEEBB8E911")),
    copy_plan(6, 3166, "8AC93A6C06B080EB65CDCE8F2FD91308403EFFCE9E38EE95A21614D35D76182B", ("종속의 건, 알겠노라\n", ". 그 휘하에서 가명을 지켜라"), ("종속의 건, 알겠노라\n", "의 산하에서 가문의 이름을 지키거라"), anchor(6, 3159, "3D5EF12E9635E85C965A024228E6B96EF3E7036EB9B8D41E8A624738180F1B55")),
    copy_plan(6, 3263, "0F672C54972A37773EEF7E6C990181F3C2433422513DF0B46912D7F4FBE677DB", ("알겠습니다\n", ". 공격하겠습니다"), ("알겠습니다\n", "를 공략해 보이겠습니다"), anchor(6, 3256, "DB82BAC765757F9B48323205E5E7E24C5F8584157F0C98C7620F8525D0F78BE2")),
    copy_plan(6, 3264, "CD3C762CB192932C11EFDC49F644D613E304D58F364908BF69E33920BAD6A5E5", ("알겠다\n", ". 함락시키겠다"), ("잘 알겠소\n", "를 함락시켜 주지"), anchor(6, 3257, "2E80FAA7C60C95F1CAC07520C2D71A279D3919F4FF561005FC9BF73AA7F42ACD")),
    copy_plan(6, 3268, "F48C6A76ECCBB81E73FB8B8D72F6EFD2E298ABBCEFC8465E7F1325631BFDCACE", ("알겠습니다\n", ". 이 정도는 손쉽습니다"), ("알겠습니다\n", "정도는 함락시켜 보이겠습니다"), anchor(6, 3261, "F5FAF589C4C079791025802A1DCA935F072B933D828CF622C0E250ECA9AA8A2A")),
    copy_plan(6, 3275, "089E728FC635355AD7222D3870695BAF93F81F02699E01D6D131516955B965C9", ("알겠습니다\n", ". 방어하겠습니다"), ("알겠습니다\n", ", 우리 가문의 병사로 지키겠소"), anchor(6, 3268, "CDE9793D5F87F394CB24CA9B6B099E6FF43910DDB672995A8CB1ADFF39E81C58")),
    copy_plan(6, 3280, "1366AAC013F1253E8774DA74031AC815049FDC37D334F713021FFFA69BF53392", ("어려울 때일수록 서로 도와야지요…\n", ". 방어에 나서겠습니다"), ("어려울 때일수록 서로 도와야지요…\n", "의 방위로 향합니다"), anchor(6, 3273, "6DF461B09F0411B6C6543949A31C5CB1DC9E0E1C6001523725E9653737D6887D")),
    copy_plan(6, 3286, "8AE4905B56CA48E80CB52293C9C7D78C6EA7CDAD8657139EF9A82A5C47AA90A1", ("무명이 자자한 귀가라면\n", ". 어렵지 않을 것입니다"), ("무명이 자자한 귀가라면\n", "공략쯤은 대수롭지 않으리"), anchor(6, 3279, "0A45F5DF076C8F5EC09DB2835FEAE75DB63E9A7BF67E29F0609CD308AC642AC3")),
)

# The PK variants use the same source dialogue as Base 6:2083–2094, but two
# Korean preimages differ in literal 2.  Preserve 026432/025032 runtime
# references and remove only the two JP inflection commands in each record.
PK_RUNTIME_SUFFIX_GROUPS = (
    (
        (2089, 2090, 2091, 2095),
        "F388F4525E37BC03E46793AA7FB937516AD8438FF7F86C18CA6100C542545CC8",
        ". 감사합니다.",
        (remove_command(35, "01431A020000"), remove_command(80, "0143F0010000")),
    ),
    (
        (2092, 2093, 2094, 2096, 2097, 2098, 2099, 2100),
        "17FBB18B713C38055FD19C83A72E3A2C3E205779B7C56B47B2286D500850DCDA",
        "의 원군에는 감사",
        (remove_command(35, "01431A020000"), remove_command(82, "0143F0010000")),
    ),
)
PK_RUNTIME_SUFFIX_PLANS: tuple[QualityPlan, ...] = tuple(
    plan(
        6,
        record_id,
        expected_sha256,
        (
            change(0, "다음 성을 함락했습니다:", " 함락은 가능하겠나…"),
            change(1, "인가…\n", "\n"),
            change(2, expected_literal_2, "의 원군에는 감사하겠소."),
        ),
        remove_commands=remove_commands,
    )
    for record_ids, expected_sha256, expected_literal_2, remove_commands in PK_RUNTIME_SUFFIX_GROUPS
    for record_id in record_ids
)
PK_PLANS += PK_RUNTIME_SUFFIX_PLANS

# These coordinates were first drafted against the 0FB9 source, whose block
# layout is not the current Steam PC release.  The aligned 31D PC-JP source
# proves that those coordinates point to different dialogue, so fail closed:
# keep them out of the candidate until each one is re-audited from 31D.
DEFERRED_UNALIGNED_0FB9_COORDINATES = frozenset(
    {
        (6, 1543), (6, 1558), (6, 1616), (6, 1637), (6, 1641),
        (6, 2793), (6, 2820), (6, 2821), (6, 2822),
        (6, 2844), (6, 2845), (6, 2846), (6, 2856), (6, 2857),
        (6, 2858), (6, 2905), (6, 2906), (6, 2971), (6, 3065),
        (6, 3078), (6, 3085), (6, 3166), (6, 3263), (6, 3264),
        (6, 3268), (6, 3275), (6, 3280), (6, 3286),
    }
)
PK_PLANS = tuple(
    item for item in PK_PLANS if item.coordinate not in DEFERRED_UNALIGNED_0FB9_COORDINATES
)

# The historical 0FB9-coordinate drafts above remain excluded.  These plans
# were independently re-audited against the aligned 31D PC-JP source and pin
# both the current Korean literals and their whole-record hashes.  Runtime
# names/months stay opaque; only the literal text is replaced, except for the
# one separately proven Japanese inflection command in 6:1558.
PK_REAUDITED_RUNTIME_PLANS: tuple[QualityPlan, ...] = (
    rewrite_plan(
        6, 1543, "9ABB8F41AE2A95D3530CDEC6D49599340E8EDC5FEF238F7C4B8BB101B07D64EE",
        ("당가가", ". 여러 나라까지 우리를 버릴지 모릅니다.\n그러니\n철저히 대비해야 합니다"),
        ("당가가", " 측과 단교하게 되었으니\n여러 나라가 우리를 가만두지 않을 터.\n철저히 대비해야 하옵니다"),
    ),
    rewrite_plan(
        6, 1558, "EED99D3A71EC44E60742A29AB25313D4B92B07922B9C5D6E00A20EBED7108DCF",
        ("당가가", ". 여러 나라가 우리를 노릴 수 있습니다……\n그러니\n철저히 대비해야 합니다"),
        ("당가가", " 측과 단교하게 되었으니\n여러 나라가 우리를 가만두지 않을 터.\n철저히 대비해야 합니다"),
        remove_commands=(remove_command(103, "014336040000"),),
    ),
    rewrite_plan(
        6, 1570, "2FD12521C495BDC9D918B3679B5BA94FC69A1A14E997C1B5DC6F73F43793F210",
        ("이제 벌할 세력:", ".\n우리를 배신한 대가가 무엇인지\n여러 나라에 보여 주자!"),
        ("이렇게 된 이상", " 놈들뿐 아니라,\n우리를 배신하면 어떤 꼴이 되는지\n여러 나라에 똑똑히 보여 줘야 한다!"),
    ),
    rewrite_plan(
        6, 1578, "A2F15BD4EEA6682A39DF1FA2A2FBAFC36C68B02F16D001898BA931CC68C7287E",
        ("본가 휘하의 세력:", ".\n감히 단교하다니,\n내버려 두면 훗날 화근이 될 것입니다"),
        ("당가의 산하에 있던", " 측이 감히 단교를 저지르다니.\n내버려 두면 훗날 화근이 될 것입니다"),
    ),
    rewrite_plan(
        6, 1590, "5E4C882385A77643D6FB8B4DF2EFBB95F1B52008EC028E1EBE804FA9228FBA51",
        ("본가에 속했다 해도 상대:", "은(는)\n나 같은", ".\n대우에 신경 써야 합니다"),
        ("당가에 속했다 해도", " 측은\n나 같은", "의 가신은 아니오.\n대우에는 신경을 써야 하겠지"),
    ),
    rewrite_plan(
        6, 1594, "E6D8FB26A5C32F6FA6E2DEF97E54D0663E09ECB6095BCCB32BF33E351E541610",
        ("호오, 본가에 종속한 세력:", ".\n이제 그들과 나란히 무공을 겨루겠군요.\n생각만 해도 피가 끓습니다"),
        ("흠,", " 측이 당가에 종속했군.\n그렇다면 그들과 어깨를 나란히 하며\n무공을 겨루게 되겠군, 피가 끓는구나"),
    ),
    rewrite_plan(
        6, 1601, "D15202CF653C63871B27AB39C5496182182822FFE5BFD62945487B14DC411CA3",
        ("종속 세력:", ". 앞으로 우리가 그들의 후원자가 되어\n더욱\n강하게 키워야 합니다"),
        ("종속했으니", " 측에는\n이제부터 우리가 후원자가 되어\n더욱 강해지게 해야겠군요"),
    ),
    rewrite_plan(
        6, 1616, "3D8430BB1321C229E3E4F05192DD0C7B27410A716EC08D2772E59CDB645299F4",
        ("종속이란 일방적으로 따르는 것이 아니옵니다.\n", ". 각오는 하되\n우리도 자립해야 합니다"),
        ("종속이란 일방적으로 따르는 것이 아니옵니다.\n", " 측과 운명을 함께할 각오는 하되,\n우리도 우리 힘으로 서야 합니다"),
    ),
    rewrite_plan(
        6, 1637, "FF16E28005A774C4DD83FBA4052CEDDC34A245B517855DB097E90A39CBB3C81E",
        ("와", ". 두 가문을 잇는 인연의 상징입니다.\n그 이야기는 나중에 하고\n먼저 연회를 열지요"),
        (" 및 ", "의 혼인은\n당가와 그 가문을 잇는 유대의 상징이지요.\n그런 얘기는 뒤로 미루고 먼저 연회를 열지요"),
    ),
    rewrite_plan(
        6, 1641, "B9D19465D64D93E3E55B2DF69EE21E6F71EA5D15E97C956E2555F9967FCE944E",
        ("와", ". 이제 두 가문은\n한 식구이자 동맹으로\n함께 나아갑시다"),
        (" 및 ", "의 혼약이 성사되었으니,\n두 가문은 이제 한집안이자 동맹으로\n함께 나아갑시다"),
    ),
    rewrite_plan(
        6, 1726, "CCD95D1112EDC465EF22CD855E40728EEF1E8CDE9E8678F51F156419418969D8",
        ("본가 부대가 머무는 세력:", ". 그 영내에서 단교하면\n악명이 크게 높아집니다.\n계속하시겠습니까?"),
        ("당가 부대가", "의 영내에 있으므로,\n단교하면 악명이 크게 높아집니다.\n정말 진행하시겠습니까?"),
    ),
    rewrite_plan(
        6, 1742, "3E31CB62A46363B2D4014E93DB34887B37E4FA30DDCB29F5CC98F73ACC2D3DCF",
        ("이 세력과 정전할 상대:", ".\n단교를 지시합니다."),
        ("이 세력과", " 측의\n단교를 지시합니다"),
    ),
    rewrite_plan(
        6, 2725, "92D38A524E69B18AA1AF4AA5C12073B086D56A65A4533A81C40008955F63F056",
        ("본가가 약한 탓입니다. 벗어나야 할 세력:", ".\n종속되기 싫다면 강해져야 합니다."),
        ("당가가 약한 탓이지. ", "의 산하로\n들어가기 싫다면 강해질 때까지 기다려라"),
    ),
    rewrite_plan(
        6, 2746, "1684986755E0F7DDA403F493FCECBD4B2DC459B8399CE18BAF3017E86889CDEE",
        ("눈앞을 가로막는 적:", ".\n이 또한 철저히 무너뜨리기 위한 포석입니다."),
        ("눈앞을 가로막는 것이 ", "라면,\n이 또한 그것을 무너뜨리기 위한 포석이다"),
    ),
    rewrite_plan(
        6, 2758, "02EC116884E135F62EAFB1423D193FD1FC678E467BC32E6B5DED03320432A75F",
        ("앞으로 다툴 상대:", ". 경쟁할 때는\n외교로 활로를 찾아야 합니다."),
        ("앞으로", " 측을 상대할 때는\n외교로 활로를 찾아야 합니다"),
    ),
    rewrite_plan(
        6, 2790, "BB4AA21A3A3CF87B803683E93597F2FA1EB0E0CAFBE970FF7C1867DABEB7F16C",
        ("이", ". 이제부터 가신으로\n주군께 평생 충성을 다하겠습니다!\n잘 부탁드립니다."),
        ("이 ", ", 이제부터 주군의 가신으로서\n대대로 섬겨 온 가신들께 뒤지지 않도록 힘쓰겠습니다!\n잘 부탁드립니다"),
    ),
    rewrite_plan(
        6, 2793, "66AA170CDCA7A1AE18B5718A4C5E2B61625860A79CFE2D0E15C3AE6771A55F09",
        ("이", ". 휘하로 들어갔습니다"),
        (" 측이 ", "의 산하로 들어갔습니다"),
    ),
    rewrite_plan(
        6, 2820, "3F351D9778E0AFE0DA7DA7380703A894A9308088DB432E5D5754D42E27DA5ECD",
        ("알겠다\n", ". 인연도 여기까지입니다."),
        ("알겠다.\n", " 측과의 관계도 여기까지다"),
    ),
    rewrite_plan(
        6, 2844, "3F351D9778E0AFE0DA7DA7380703A894A9308088DB432E5D5754D42E27DA5ECD",
        ("알겠다\n", ". 인연도 여기까지입니다."),
        ("알겠다.\n", " 측과의 관계도 여기까지다"),
    ),
    rewrite_plan(
        6, 2821, "FB77E6F3C71B2B16B196D05376A7F1175C7A28E62300467EDCAE722287646CA3",
        ("알겠습니다\n", ". 맹약을 해소하겠습니다."),
        ("알겠습니다.\n", " 측과의 맹약은 해소하겠습니다"),
    ),
    rewrite_plan(
        6, 2845, "FB77E6F3C71B2B16B196D05376A7F1175C7A28E62300467EDCAE722287646CA3",
        ("알겠습니다\n", ". 맹약을 해소하겠습니다."),
        ("알겠습니다.\n", " 측과의 맹약은 해소하겠습니다"),
    ),
    rewrite_plan(
        6, 2822, "D2B1C9C65DD5701B8FEBA7E76A51D1B8ECCAF745EAEF13BFE219311FC9B98FC2",
        ("알겠다\n", ". 이제 동맹은 무효입니다."),
        ("알겠다.\n", " 측과의 동맹은 파기한다"),
    ),
    rewrite_plan(
        6, 2846, "D2B1C9C65DD5701B8FEBA7E76A51D1B8ECCAF745EAEF13BFE219311FC9B98FC2",
        ("알겠다\n", ". 이제 동맹은 무효입니다."),
        ("알겠다.\n", " 측과의 동맹은 파기한다"),
    ),
    rewrite_plan(
        6, 2856, "0FB500CA6BD49B5F164B2633E0756F135F3D3B3CAF658587EF6E5085F9DFC785",
        ("좋다, 결정했다\n공격할 세력:", ". 출진하자"),
        ("좋다, 분명히 알겠다.\n우리는 ", " 측을 공격하겠다"),
    ),
    rewrite_plan(
        6, 2857, "B57A9B96A0ABF7CEFA4297CBFD9C90D51012704009FD16F3177391049DFBDD87",
        ("알겠습니다\n", ". 공격합시다"),
        ("알겠습니다.\n", " 측을 공격하겠습니다"),
    ),
    rewrite_plan(
        6, 2858, "460E788AEF700686F934A1218323541D7A544841A224203B519701E654C631EE",
        ("알겠다\n", ". 공격하겠습니다"),
        ("알겠다.\n", " 측을 공격하자"),
    ),
    rewrite_plan(
        6, 2905, "A13D90F7C1CF1077DCBA3E32F3B0D7932E292E6B3396B641B9F5623F63E762CF",
        (": 단교를 통고해 왔습니까?\n배후 세력:", ". 그 사주가 분명합니다"),
        (" 측이 단교를 통고했다고?\n설마… ", "의 사주로군요"),
    ),
    rewrite_plan(
        6, 2906, "3EF7C8EE5A05565054169467D47021B8581BAA853F1200752AB8B2630993E690",
        (": 단교한다고……?\n배후 세력:", ". 그 사주인가?"),
        (" 측이 관계를 끊겠다고…?\n… ", "의 사주인가?"),
    ),
    rewrite_plan(
        6, 2971, "66B9A56152613707ECD0DE9A68DA5CD9E63DB31EF0264FE5D85B7110068441E7",
        ("에게서\n", ". 그 휘하에서 전향을 청합니다.\n확인하십시오"),
        (" 측에서\n", "의 산하를 떠나겠다는 사신이\n왔습니다. 확인해 주십시오"),
    ),
    rewrite_plan(
        6, 3065, "FE0E8373DF2433BD2EF69BF20A092F050B529715EDAC68F114F69858B22435E1",
        ("인척 관계가 사라졌으므로,", ". 혼인으로 맺은 동맹도\n앞으로", "개월 후에는\n효력이 사라지오, 부디 주의하시오"),
        ("인척 관계가 사라졌으므로,", " 측과의 혼인 동맹도 ", "개월 뒤에는\n효력을 잃습니다. 부디 유의하십시오"),
    ),
    rewrite_plan(
        6, 3078, "754A6F171B9140FAF073A418810BD80AD0D53C81A73DC4A4B7FDF310D7B54B26",
        ("참으로 유감이지만", "이(가) 당가를\n떠나셨기에,", ". 해당 동맹은\n앞으로", "개월 남았습니다."),
        ("참으로 유감스럽게도 ", "께서 당가를 떠나셨으므로,\n", " 측과의 동맹도\n남은 기간은 ", "개월입니다."),
    ),
    rewrite_plan(
        6, 3085, "7A5A413AFAE0269C0400BE0764DA445202975312F71905E0B28E95F04DFA753F",
        ("이(가) 붙들어 두고 있었습니다\n", "와의 혼인 동맹도", ". 그 취향을 알다니,\n놀라울 따름입니다."),
        ("께서 붙잡아 두셨던\n", " 측과의 혼인 동맹도 ", "개월 뒤에는\n사라지고 마는군요…"),
    ),
    rewrite_plan(
        6, 3166, "8AC93A6C06B080EB65CDCE8F2FD91308403EFFCE9E38EE95A21614D35D76182B",
        ("종속의 건, 알겠노라\n", ". 그 휘하에서 가명을 지켜라"),
        ("종속의 의식, 알겠다.\n", "의 산하에서 가문을 지켜라"),
    ),
    rewrite_plan(
        6, 3263, "0F672C54972A37773EEF7E6C990181F3C2433422513DF0B46912D7F4FBE677DB",
        ("알겠습니다\n", ". 공격하겠습니다"),
        ("알겠습니다.\n", " 공략을 해 보이겠습니다"),
    ),
    rewrite_plan(
        6, 3264, "CD3C762CB192932C11EFDC49F644D613E304D58F364908BF69E33920BAD6A5E5",
        ("알겠다\n", ". 함락시키겠다"),
        ("알겠다.\n", " 함락은 내게 맡겨라"),
    ),
    rewrite_plan(
        6, 3268, "F48C6A76ECCBB81E73FB8B8D72F6EFD2E298ABBCEFC8465E7F1325631BFDCACE",
        ("알겠습니다\n", ". 이 정도는 손쉽습니다"),
        ("알겠습니다.\n", " 정도는 함락시켜 보이겠습니다"),
    ),
    rewrite_plan(
        6, 3275, "089E728FC635355AD7222D3870695BAF93F81F02699E01D6D131516955B965C9",
        ("알겠습니다\n", ". 방어하겠습니다"),
        ("알겠습니다.\n", ", 당가의 병력으로 지키겠습니다"),
    ),
    rewrite_plan(
        6, 3280, "1366AAC013F1253E8774DA74031AC815049FDC37D334F713021FFFA69BF53392",
        ("어려울 때일수록 서로 도와야지요…\n", ". 방어에 나서겠습니다"),
        ("어려울 때일수록 서로 도와야지요…\n", "의 방어를 위해 출진하겠습니다"),
    ),
    rewrite_plan(
        6, 3286, "8AE4905B56CA48E80CB52293C9C7D78C6EA7CDAD8657139EF9A82A5C47AA90A1",
        ("무명이 자자한 귀가라면\n", ". 어렵지 않을 것입니다"),
        ("무명이 자자한 귀 가문이라면\n", " 공략쯤은 식은 죽 먹기겠지"),
    ),
)

PK_REAUDITED_DIALOGUE_PLANS: tuple[QualityPlan, ...] = (
    rewrite_plan(
        6, 647, "535D534930192589120808B75623D7ECB731E49C59D1823033D7A1EB7ECF20C2",
        ("누구신가 했더니:", "이(가)\n쳐들어올 것 같습니다"),
        ("아아… ", " 측이\n쳐들어올 듯합니다"),
    ),
    rewrite_plan(
        6, 826, "60D4835A39BB65A401AFB88C9ABF89C767F930834684EC6E2400C4F108BE1C6F",
        ("평정 참여:", "……\n그자를 본가에 둘 필요가 있나"),
        ("당가에 ", " 따위는\n필요 없다고 생각하오만…"),
    ),
    rewrite_plan(
        6, 874, "6875C1F9151E1238C6F19D81E82882934EF23657F1F8EE8A9A0F8A8F0DE04E5B",
        ("이제 죽을 날이\n가까운 모양이군……",),
        ("으으음…\n병 따위에…",),
    ),
    rewrite_plan(
        6, 884, "B63A31C3F9FDEF71A7B402AD510EF2CB859721B952F7561982718AFAD698EF70",
        ("이별할 날이\n가까운지도 모르겠군……",),
        ("하아, 하아…\n아무래도 몸 상태가 좋지 않아…",),
    ),
    rewrite_plan(
        6, 2245, "2E6FCDD3687E47B0A858FEDAE53ADEFC39AE6CA33AC48894A6D527A851198914",
        ("누구신가 했더니:", "님이군요."),
        ("아아… ", "님이셨습니까"),
    ),
    rewrite_plan(
        6, 2270, "40D584F47B0A61996A94991F4F97BC68BC11CBDF90C7538CAFFBEB93FED6F77E",
        ("우리와 친해지고 싶으시다고요……\n그 대가로 무엇을 주시겠습니까?",),
        ("무언가를 주시는 겁니까?\n이거 참 송구스럽군요",),
    ),
    rewrite_plan(
        6, 2271, "40D584F47B0A61996A94991F4F97BC68BC11CBDF90C7538CAFFBEB93FED6F77E",
        ("우리와 친해지고 싶으시다고요……\n그 대가로 무엇을 주시겠습니까?",),
        ("번지르르한 미사여구는 필요 없소.\n무엇으로 우리의 환심을 사시겠소?",),
    ),
    rewrite_plan(
        6, 2307, "535689A99AE9220538952F385B5D99AAD899B4E8D986AF24AED6F52330CDCFBD",
        ("이 요청의 대가는 큽니다.\n상응하는 보답을 준비하셨겠지요?",),
        ("호오… 농담으로 꺼낸 말이 아니라면\n그 진심을 보여 주시오",),
    ),
    rewrite_plan(
        6, 2311, "535689A99AE9220538952F385B5D99AAD899B4E8D986AF24AED6F52330CDCFBD",
        ("이 요청의 대가는 큽니다.\n상응하는 보답을 준비하셨겠지요?",),
        ("그렇군요…\n당신의 각오를 보여 주셨으면 합니다",),
    ),
    rewrite_plan(
        6, 2330, "B90001FEF8203EEEDF56E3A0F5EF82967F1186389ECD920BD42E72C02399350D",
        ("이것으로", "님.\n결과는 운에 맡겨야 합니다."),
        ("이것으로 ", "님께서\n움직여 주시면 좋으련만…"),
    ),
    rewrite_plan(
        6, 2438, "96D380155ECCB1650BA7AFED744F8EF6E1A52FAB6D48BAEB071708780BD1BE3B",
        ("파담이로군…", "님 같은 분과 교섭하다니\n제가 어리석었습니다."),
        ("교섭은 결렬이로군… ", "님을 믿고 찾아왔건만\n그 믿음에는 응해 주지 않은 모양이오"),
    ),
    rewrite_plan(
        6, 2673, "FA63151E064CFB5BE4A9307D23F961CE45BE8D636EDD367FB3FA23CA3DEE2E32",
        ("앞날을 생각해 우호 관계를 맺을 세력:", "와의\n우호 관계를 쌓아야 하는가"),
        ("앞날을 생각하면 ", " 측과\n우호 관계를 맺어야 하는가"),
    ),
    rewrite_plan(
        6, 2676, "18695F536FD731805F6F767691B8EC90A3C31E9481AD28E26F55E2757998ACE9",
        ("관계를 다시 구축할 세력:", "과\n좋은 관계를 맺으면 판세를 바꿀 수 있습니다."),
        ("이 판국, 새로 ", " 측과\n우호 관계를 맺을 수 있다면 판세를 바꿀 수 있겠지"),
    ),
    rewrite_plan(
        6, 2698, "B640687D8EBDEDBBDAC98B9277508A47EA0A3D88B32557DEC38339D15876BFC9",
        ("본가와 유대를 이어 갈 세력:", "과의\n굳은 인연이 오래 이어지기를 바랍니다."),
        ("우리와 ", " 측의 굳은 인연이\n오래도록 이어지기를 바라오"),
    ),
    rewrite_plan(
        6, 2879, "2AB1AACB32E15BF94927852E808014FEA237A76B655F7D8CE255F7D107AC9967",
        ("호오, 본가에 종속한 세력:", "을(를) 버리고 왔다니\n용기 있는 결단을 저버릴 수는 없지\n이후는 당가에 맡기시오"),
        ("흠, ", " 측을 버리고 왔다고?\n용감한 결단을 저버릴 수는 없지.\n이후는 당가에 맡기시오"),
    ),
    rewrite_plan(
        6, 2881, "33784008FB05476429B14511A798291B7ED4947504B11AD1DCAC374207B6075D",
        ("등을 돌린 세력:", "입니까?\n본가를 방패로 택한 것은 현명합니다\n앞으로 활약을 기대하겠습니다"),
        ("과연, ", " 측을 버리시는군요.\n당가를 후견인으로 택한 것은 현명합니다.\n앞으로의 활약을 기대하겠습니다"),
    ),
    rewrite_plan(
        6, 2974, "08142502B19312C94C9CC3B9169A91C4CC608F8068F2944CA7D78E291CF7CA63",
        ("님\n제 부탁을 들어주시겠습니까?",),
        ("당가의 부탁을 들어주시길 바랍니다.\n이것이 마음에 드셨으면 좋겠소만…",),
    ),
    rewrite_plan(
        6, 2975, "08142502B19312C94C9CC3B9169A91C4CC608F8068F2944CA7D78E291CF7CA63",
        ("님\n제 부탁을 들어주시겠습니까?",),
        ("오늘은 상의드릴 일이 있어 찾아왔습니다.\n부디 이것으로 받아주시겠습니까?",),
    ),
    rewrite_plan(
        6, 2976, "3F7FE643EBE4D66F921AAFB23F63420E3D15F226D6F466A5509A9DFB1A5E79E4",
        ("님\n제 부탁을 들어주시겠습니까?",),
        ("의 역량을 믿고 찾아왔소.\n내 부탁을 들어주시오",),
    ),
    rewrite_plan(
        6, 2980, "08142502B19312C94C9CC3B9169A91C4CC608F8068F2944CA7D78E291CF7CA63",
        ("님\n제 부탁을 들어주시겠습니까?",),
        ("부탁을 들어주시겠습니까?\n훗날 양가 모두의 이익이 될 것입니다",),
    ),
    rewrite_plan(
        6, 3402, "962EB2BA19927DC1B9557959BED54E03AFEDA629C4F09EE954A66D162D35D16C",
        ("이 판단이 옳았음을\n증명하기 위해 가문:", "을 평생을 걸고 번영시켜\n증명하겠습니다."),
        ("이 판단이 옳았음을\n이 한몸을 걸고 ", "의\n번영을 이루어 증명하겠습니다"),
    ),
)

PK_REAUDITED_PLANS = PK_REAUDITED_RUNTIME_PLANS + PK_REAUDITED_DIALOGUE_PLANS
PK_PLANS += PK_REAUDITED_PLANS


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise QualityError(f"{label} escapes allowed root: {resolved_path}") from exc
    return resolved_path


def plans_for(relative: str) -> tuple[QualityPlan, ...]:
    if relative == "MSG/JP/msggame.bin":
        return BASE_PLANS
    if relative == "MSG_PK/JP/msggame.bin":
        return PK_PLANS
    raise QualityError(f"unsupported message resource: {relative}")


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(packed).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def opaque_bytes(record: MsgGameRecord) -> bytes:
    literals = parse_record_literals(record)
    if not literals:
        raise QualityError(f"{record.block_id}:{record.record_id} has no literal slots")
    out = bytearray()
    cursor = 0
    for literal in literals:
        out.extend(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    out.extend(record.data[cursor:])
    return bytes(out)


def rendered_literal_line_count(record: MsgGameRecord) -> int:
    """Count manual lines after concatenating literal slots around runtime tokens."""
    literals = parse_record_literals(record)
    if not literals:
        raise QualityError(f"{record.block_id}:{record.record_id} has no literal slots")
    return 1 + sum(literal.text.count("\n") for literal in literals)


def opaque_spans(record: MsgGameRecord) -> tuple[tuple[int, bytes], ...]:
    cursor = 0
    spans: list[tuple[int, bytes]] = []
    for literal in parse_record_literals(record):
        spans.append((cursor, record.data[cursor : literal.marker_offset]))
        cursor = literal.marker_end
    spans.append((cursor, record.data[cursor:]))
    return tuple(spans)


def opaque_commands(record: MsgGameRecord) -> tuple[tuple[int, bytes], ...]:
    commands: list[tuple[int, bytes]] = []
    for span_offset, span in opaque_spans(record):
        for offset in range(len(span) - 5):
            if span[offset : offset + 2] == b"\x01\x43":
                commands.append((span_offset + offset, span[offset : offset + 6]))
    return tuple(commands)


def removal_map(record: MsgGameRecord, item: QualityPlan) -> dict[int, bytes]:
    expected = {command.offset: command.value for command in item.remove_commands}
    if not expected:
        return expected
    actual = dict(opaque_commands(record))
    mismatch = {
        offset: {"expected": value.hex().upper(), "actual": actual.get(offset, b"").hex().upper()}
        for offset, value in expected.items()
        if actual.get(offset) != value
    }
    if mismatch:
        raise QualityError(
            f"{item.coordinate} removable 0143 contract mismatch: "
            f"{json.dumps(mismatch, ensure_ascii=False, sort_keys=True)}"
        )
    return expected


def strip_removed_commands(span_offset: int, span: bytes, removals: dict[int, bytes]) -> bytes:
    output = bytearray()
    index = 0
    while index < len(span):
        absolute = span_offset + index
        command = removals.get(absolute)
        if command is not None:
            if span[index : index + len(command)] != command:
                raise QualityError(f"removable 0143 command shifted at 0x{absolute:X}")
            index += len(command)
            continue
        output.append(span[index])
        index += 1
    return bytes(output)


def expected_opaque_after_removals(record: MsgGameRecord, item: QualityPlan) -> bytes:
    removals = removal_map(record, item)
    return b"".join(
        strip_removed_commands(span_offset, span, removals)
        for span_offset, span in opaque_spans(record)
    )


def encode_literal(text: str, item: QualityPlan) -> bytes:
    encoded = text.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise QualityError(f"reserved literal marker in {item.coordinate}")
    return LITERAL_START + encoded + LITERAL_END


def rebuild_quality_record(
    record: MsgGameRecord,
    item: QualityPlan,
    literal_replacements: dict[int, str],
) -> bytes:
    if not item.remove_commands:
        return rebuild_record_literals(record, literal_replacements)
    removals = removal_map(record, item)
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        output.extend(
            strip_removed_commands(cursor, record.data[cursor : literal.marker_offset], removals)
        )
        output.extend(encode_literal(literal_replacements.get(literal.literal_id, literal.text), item))
        cursor = literal.marker_end
    output.extend(strip_removed_commands(cursor, record.data[cursor:], removals))
    rebuilt = bytes(output)
    rebuilt_record = MsgGameRecord(record.block_id, record.record_id, record.relative_offset, rebuilt)
    if opaque_bytes(rebuilt_record) != expected_opaque_after_removals(record, item):
        raise QualityError(f"{item.coordinate} changed unplanned opaque bytes")
    remaining_commands = {value for _offset, value in opaque_commands(rebuilt_record)}
    leftovers = [
        command.expected_hex
        for command in item.remove_commands
        if command.value in remaining_commands
    ]
    if leftovers:
        raise QualityError(
            f"{item.coordinate} retained planned-to-remove 0143 command(s): {leftovers}"
        )
    return rebuilt


def validate_plan_set(plans: tuple[QualityPlan, ...], relative: str) -> None:
    coordinates = [item.coordinate for item in plans]
    if len(coordinates) != len(set(coordinates)):
        raise QualityError(f"duplicate quality-plan coordinate in {relative}")
    for item in plans:
        literal_ids = [entry.literal_id for entry in item.changes]
        if len(literal_ids) != len(set(literal_ids)):
            raise QualityError(f"duplicate literal slot in {relative} {item.coordinate}")
        removal_offsets = [command.offset for command in item.remove_commands]
        if len(removal_offsets) != len(set(removal_offsets)):
            raise QualityError(f"duplicate removable 0143 offset in {relative} {item.coordinate}")
        for entry in item.changes:
            if entry.expected_text == entry.replacement:
                raise QualityError(f"no-op literal change in {relative} {item.coordinate}")
            if entry.replacement.count("\n") > 2:
                raise QualityError(f"more than three lines in {relative} {item.coordinate}")


def validate_source_coordinates(steam_root: Path) -> dict[str, str]:
    # Wave 3 validates both whole pristine PC JP files; this adds the Wave 4
    # coordinates to that source-gated structural contract.
    source_hashes = WAVE3.assert_pristine_sources()
    WAVE3.assert_pristine_layout_matches_steam(steam_root)
    source_records_by_relative: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    for relative, (source_path, _expected_hash) in WAVE3.PRISTINE_SOURCES.items():
        source_records = records_by_coordinate(source_path.read_bytes())
        source_records_by_relative[relative] = source_records
        for item in plans_for(relative):
            if item.coordinate not in source_records:
                raise QualityError(f"PC JP source lacks {relative} {item.coordinate}")
    base_source = source_records_by_relative["MSG/JP/msggame.bin"]
    for item in PK_PLANS:
        if item.base_anchor is None:
            continue
        base_record = base_source.get((item.base_anchor.block_id, item.base_anchor.record_id))
        if base_record is None:
            raise QualityError(f"PC base JP source lacks anchor for PK {item.coordinate}")
    return source_hashes


def assert_anchor(base_records: dict[tuple[int, int], MsgGameRecord], item: QualityPlan) -> None:
    if item.base_anchor is None:
        return
    target = base_records.get((item.base_anchor.block_id, item.base_anchor.record_id))
    if target is None:
        raise QualityError(f"missing PC base anchor for PK {item.coordinate}")
    actual_hash = sha256_bytes(target.data)
    if actual_hash != item.base_anchor.expected_sha256:
        raise QualityError(
            f"PC base anchor mismatch for PK {item.coordinate}: "
            f"expected {item.base_anchor.expected_sha256}, got {actual_hash}"
        )


def rebuild_quality_resource(
    packed: bytes,
    plans: tuple[QualityPlan, ...],
    relative: str,
    base_records: dict[tuple[int, int], MsgGameRecord],
) -> bytes:
    validate_plan_set(plans, relative)
    before = records_by_coordinate(packed)
    replacements: dict[tuple[int, int], bytes] = {}
    opaque_contracts: dict[tuple[int, int], bytes] = {}
    for item in plans:
        record = before.get(item.coordinate)
        if record is None:
            raise QualityError(f"{relative} missing record {item.coordinate}")
        actual_hash = sha256_bytes(record.data)
        if actual_hash != item.expected_sha256:
            raise QualityError(
                f"{relative} {item.coordinate} SHA-256 mismatch: "
                f"expected {item.expected_sha256}, got {actual_hash}"
            )
        assert_anchor(base_records, item)
        literals = {literal.literal_id: literal.text for literal in parse_record_literals(record)}
        literal_replacements: dict[int, str] = {}
        for entry in item.changes:
            actual = literals.get(entry.literal_id)
            if actual != entry.expected_text:
                raise QualityError(
                    f"{relative} {item.coordinate} literal {entry.literal_id} mismatch: "
                    f"expected {entry.expected_text!r}, got {actual!r}"
                )
            literal_replacements[entry.literal_id] = entry.replacement
        opaque_contracts[item.coordinate] = expected_opaque_after_removals(record, item)
        replacements[item.coordinate] = rebuild_quality_record(record, item, literal_replacements)

    rebuilt = rebuild_packed_msggame(packed, replacements)
    after = records_by_coordinate(rebuilt)
    if set(after) != set(before):
        raise QualityError(f"{relative} record topology changed")
    for coordinate, original in before.items():
        expected = replacements.get(coordinate, original.data)
        if after[coordinate].data != expected:
            raise QualityError(f"{relative} {coordinate} rebuilt record mismatch")
    for item in plans:
        record = after[item.coordinate]
        if opaque_bytes(record) != opaque_contracts[item.coordinate]:
            raise QualityError(f"{relative} {item.coordinate} changed opaque runtime bytes")
        after_literals = {literal.literal_id: literal.text for literal in parse_record_literals(record)}
        for entry in item.changes:
            if after_literals[entry.literal_id] != entry.replacement:
                raise QualityError(f"{relative} {item.coordinate} literal replacement failed")
        if rendered_literal_line_count(record) > 3:
            raise QualityError(f"{relative} {item.coordinate} exceeds three manual lines")
    return rebuilt


def target_is_pinned() -> bool:
    return all(TARGET_SHA256[path] for path in CHANGED_PATHS)


def profile_hashes(root: Path) -> dict[str, str]:
    return WAVE3.profile_hashes(root)


def assert_profile(root: Path, expected: dict[str, str], label: str) -> None:
    try:
        WAVE3.assert_profile(root, expected, label)
    except WAVE3.WaveError as exc:
        raise QualityError(str(exc)) from exc


def render_plan(item: QualityPlan) -> dict[str, object]:
    result = asdict(item)
    result["coordinate"] = f"{item.block_id}:{item.record_id}"
    return result


def build_candidate(
    steam_root: Path,
    output_root: Path,
    manifest_path: Path,
    allow_unpinned_output: bool,
) -> dict[str, object]:
    steam_root = steam_root.resolve()
    output_root = require_under(REPO, output_root, "candidate output")
    manifest_path = require_under(REPO, manifest_path, "manifest output")
    if output_root.exists():
        raise QualityError(f"candidate output already exists: {output_root}")
    assert_profile(steam_root, BASELINE_SHA256, "installed input")
    pristine_hashes = validate_source_coordinates(steam_root)

    source_base = (steam_root / "MSG/JP/msggame.bin").read_bytes()
    source_pk = (steam_root / "MSG_PK/JP/msggame.bin").read_bytes()
    wave3_base = WAVE3.rebuild_static_resource(source_base, WAVE3.BASE_PLANS, "MSG/JP/msggame.bin")
    wave3_pk = WAVE3.rebuild_static_resource(source_pk, WAVE3.PK_PLANS, "MSG_PK/JP/msggame.bin")
    if sha256_bytes(wave3_base) != WAVE3.TARGET_SHA256["MSG/JP/msggame.bin"]:
        raise QualityError("in-memory Wave 3 base output hash mismatch")
    if sha256_bytes(wave3_pk) != WAVE3.TARGET_SHA256["MSG_PK/JP/msggame.bin"]:
        raise QualityError("in-memory Wave 3 PK output hash mismatch")
    base_records = records_by_coordinate(wave3_base)
    final_base = rebuild_quality_resource(wave3_base, BASE_PLANS, "MSG/JP/msggame.bin", base_records)
    final_pk = rebuild_quality_resource(wave3_pk, PK_PLANS, "MSG_PK/JP/msggame.bin", base_records)

    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(require_under(steam_root, steam_root / relative, "Steam input"), target)
        (stage / "MSG/JP/msggame.bin").write_bytes(final_base)
        (stage / "MSG_PK/JP/msggame.bin").write_bytes(final_pk)
        output_hashes = profile_hashes(stage)
        if target_is_pinned():
            if output_hashes != TARGET_SHA256:
                mismatch = {
                    path: {"expected": TARGET_SHA256[path], "actual": output_hashes[path]}
                    for path in PROFILE_PATHS
                    if TARGET_SHA256[path] != output_hashes[path]
                }
                raise QualityError(f"candidate target SHA-256 mismatch: {json.dumps(mismatch)}")
        elif not allow_unpinned_output:
            raise QualityError("target SHA-256 is not pinned; bootstrap only with --allow-unpinned-output")
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave4-v1",
            "input_sha256": BASELINE_SHA256,
            "output_sha256": output_hashes,
            "pinned_output_sha256": TARGET_SHA256 if target_is_pinned() else None,
            "pristine_pc_jp_sha256": pristine_hashes,
            "changed_paths": list(CHANGED_PATHS),
            "base_plan_count": len(BASE_PLANS),
            "pk_plan_count": len(PK_PLANS),
            "base_plans": [render_plan(item) for item in BASE_PLANS],
            "pk_plans": [render_plan(item) for item in PK_PLANS],
        }
        os.replace(stage, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def verify_installed(steam_root: Path) -> None:
    if not target_is_pinned():
        raise QualityError("target SHA-256 is not pinned in this source revision")
    steam_root = steam_root.resolve()
    validate_source_coordinates(steam_root)
    assert_profile(steam_root, TARGET_SHA256, "installed target")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build a candidate without changing Steam")
    build.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    build.add_argument("--allow-unpinned-output", action="store_true")
    build.set_defaults(func=lambda args: build_candidate(
        args.steam_root, args.output_root, args.manifest, args.allow_unpinned_output
    ))
    verify = sub.add_parser("verify-installed", help="require exact final Wave 4 state")
    verify.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    verify.set_defaults(func=lambda args: verify_installed(args.steam_root))
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        result = args.func(args)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        else:
            print("OK")
        return 0
    except (OSError, ValueError, QualityError, WAVE3.WaveError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
