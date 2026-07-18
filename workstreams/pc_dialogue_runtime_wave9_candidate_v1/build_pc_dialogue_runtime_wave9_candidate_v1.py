#!/usr/bin/env python3
"""Build a private PC-only Wave 9 runtime-dialogue candidate.

This workstream accepts only the pinned Wave 8 private candidate as text
input, writes only below its own tmp directory, and has no Steam-apply command.
The generated audit is source-free: it carries hashes, topology, glyph, and
width evidence, but no source or candidate literal text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
PRIVATE_TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
WAVE8_INPUT_ROOT = (
    REPO
    / "tmp"
    / "pc_dialogue_quality_wave8_candidate_v1"
    / "candidate-build-1"
)
DEFAULT_FONT_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
RESOURCE = "MSG_PK/JP/msggame.bin"
SCHEMA = "nobu16.kr.pc-dialogue-runtime-wave9.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-runtime-wave9.audit.v1"
RECORD_TERMINATOR = b"\x05\x05\x05"
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"
WIDE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]"
)
GROUP_RUNTIME_LAYOUT = "runtime_linebreak_and_phrase_repair"
GROUP_GUSIN_TERMINOLOGY = "high_confidence_gusin_to_geonui"
EXCLUDED_HOMOGRAPH = "누구신"

for module_root in (TOOLS, MSGGAME_TOOLS):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from nobu16_lz4 import decompress_wrapper, parse_link  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402
from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_record_literals,
)


class Wave9Error(RuntimeError):
    """A candidate contract was violated."""


PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)

# Exact Wave 8 private-candidate inputs. These are intentionally not current
# Steam hashes, so a different installation cannot become an implicit input.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834",
    "MSG/JP/msggame.bin": "7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "1880A8052C916FAC7F262CCC8638477F5AA124F248A6468E0533A8E252AB55C5",
    "MSG_PK/JP/msggame.bin": "454A18B0F0ED5E39A3AC823AD0A30086C25226BF6E48D4580962DFEE84E24A32",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}

# Pinned deterministic private output profile. Only the PK msggame entry
# changes; every other target hash remains exactly equal to Wave 8.
TARGET_SHA256 = {
    "MSG/JP/ev_strdata.bin": "25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834",
    "MSG/JP/msggame.bin": "7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "1880A8052C916FAC7F262CCC8638477F5AA124F248A6468E0533A8E252AB55C5",
    "MSG_PK/JP/msggame.bin": "209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}

LONG_RUNTIME_VALUE_ROWS = frozenset(
    {
        (2, 96),
        (2, 97),
        (2, 126),
        (6, 2328),
        (6, 2750),
    }
)

# The terminology subgroup is validated against PC-only reference resources.
PRISTINE_PC_JP_MSGGAME = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msggame.bin"
)
PC_REFERENCE_MSGGAME = {
    "pc_jp_pristine": PRISTINE_PC_JP_MSGGAME,
    "pc_en": REPO.parent / "MSG_PK" / "EN" / "msggame.bin",
    "pc_sc": REPO.parent / "MSG_PK" / "SC" / "msggame.bin",
    "pc_tc": REPO.parent / "MSG_PK" / "TC" / "msggame.bin",
}
PC_REFERENCE_SHA256 = {
    "pc_jp_pristine": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "pc_en": "14D9A20ECB35F35C91D14947921CF09F5EAF960F8FA4D70F703F2366DB1D13AF",
    "pc_sc": "8D4417737975203A4CFF7EB0185DB1959F09D56B5F394CFD8136A58B3E7783C3",
    "pc_tc": "73278A4CF06F007E729C37FC6E6409FD77A5A246DB0408CF2879082E88FB0B5D",
}
TERMINOLOGY_GRAMMAR_EXCEPTIONS = {
    (6, 1195): ("구신을", "건의를"),
    (6, 1396): ("구신이", "건의가"),
    (6, 1472): ("구신을", "건의를"),
}


@dataclass(frozen=True)
class RuntimeRow:
    coordinate: tuple[int, int]
    current_literals: tuple[str, ...]
    output_literals: tuple[str, ...]
    input_record_sha256: str
    opaque_spans_hex: tuple[str, ...]
    group: str = GROUP_RUNTIME_LAYOUT

    @property
    def key(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


def row(
    block_id: int,
    record_id: int,
    current_literals: tuple[str, ...],
    output_literals: tuple[str, ...],
    input_record_sha256: str,
    opaque_spans_hex: tuple[str, ...],
    group: str = GROUP_RUNTIME_LAYOUT,
) -> RuntimeRow:
    return RuntimeRow(
        coordinate=(block_id, record_id),
        current_literals=current_literals,
        output_literals=output_literals,
        input_record_sha256=input_record_sha256,
        opaque_spans_hex=opaque_spans_hex,
        group=group,
    )


RUNTIME_LAYOUT_ROWS = (
    row(2, 94, ("부인:", "이(가) 무장으로 원복했습니다."), ("부인 ", ", 무장으로서 원복했습니다."), "3C2E2E35E64C7802A70C2FAD24203847C3B827E693D143436BFBF345FF40E035", ("", "024633", "050505")),
    row(2, 95, ("딸:", "이(가) 무장으로 원복했습니다."), ("따님 ", ", 무장으로서 원복했습니다."), "AD14C3CAED2D5CFDB69982942AEE17EE908D90E8791DF8BA930135DD7F510106", ("", "024633", "050505")),
    row(2, 96, ("부인:", "이(가) 성인식을 마치고 성인이 되었습니다."), ("부인 ", ", 머리 올림 의식을 마쳐 성인이 되었습니다."), "532921CE205B8EECB8FA13072D3D4E923434A2BEF0472DEF29F50BE49F959003", ("", "024633", "050505")),
    row(2, 97, ("딸:", "이(가) 성인식을 마치고 성인이 되었습니다."), ("따님 ", ", 머리 올림 의식을 마쳐 성인이 되었습니다."), "4FD61ABA55A075629E80A90DF59994359F22CBD89A11F0111EB7C56196DBF323", ("", "024633", "050505")),
    row(2, 98, ("가신의 딸:", "이(가) 성인이 되었습니다."), ("가신의 딸 ", ", 성인이 되었습니다."), "E57F0306A1492CB15273902D320AC83690CF29EBE390CF02226CE83D10D6ACFE", ("", "024633", "050505")),
    row(2, 126, ("나머지는 제게 맡겨주십시오.\n후임 당주:", "이(가) 본가를 패자로 만들겠습니다."), ("나머지는 제게 맡겨 주십시오.\n후임 당주인 ", ", 본가를 천하의 강자로 만들겠습니다."), "4581EDD6FB164E0DE71DF1E0C3B6477657BF9A6C45047968C3C63EF640D7711C", ("", "024635", "050505")),
    row(2, 152, ("공략 대상 세력:", "을(를) 공략하여 공략 방침을 달성했습니다."), ("공략 대상 세력: ", "\n공략에 성공해 방침을 달성했습니다."), "FA17508FF0D32A3A2755DDC4762A462177D9720DD0045EBBE314E93E3D0B89A5", ("", "023C", "050505")),
    row(2, 153, ("공략 대상 세력:", "이(가) 멸망하여 공략 방침이 해제되었습니다."), ("공략 대상 세력: ", "\n세력이 멸망해 방침이 해제되었습니다."), "ACCDDF2365AB79E5F54BF42F42ABF8F07357275495E9EA8BB35240807F62CD30", ("", "023C", "050505")),
    row(2, 154, ("공략 대상 세력:", "이(가) 아군이 되어 공략 방침이 해제되었습니다."), ("공략 대상 세력: ", "\n아군이 되어 방침이 해제되었습니다."), "804B08F5C9FEB9674D1370CCCC7B3318181F00F269DCDD367D79221EC61805E5", ("", "023C", "050505")),
    row(2, 155, ("공략 대상 세력:", "으로 향하는 행군로가 사라져 공략 방침이 해제되었습니다."), ("공략 대상 세력: ", "\n행군로가 끊겨 방침이 해제되었습니다."), "419A12E9303112034EC9A671FE46CB9D34B2E78158C550643D3C977BFCE53551", ("", "023C", "050505")),
    row(2, 156, ("공략 대상 세력:", "과(와) 휴전하여 공략 방침이 해제되었습니다."), ("공략 대상 세력: ", "\n휴전으로 방침이 해제되었습니다."), "51F485975E7C1B2219F2E885DC7D33B07CA1A9EE0FFE26B6F0B61A97FC5FAE36", ("", "023C", "050505")),
    row(2, 157, ("공략 대상 성:", "을(를) 공략했습니다."), ("공략 대상 성: ", "\n공략을 완료했습니다."), "4D0533CEAA4BE6556C01DBA3065B3DB1D3F43AF34B43D109BE57A93011C8ECAD", ("", "026432", "050505")),
    row(2, 192, ("옛 본거지:", "이(가) 함락되어 본거지를\n", "(으)로 옮겼습니다."), ("기존 본거지 ", "의 함락으로\n본거지를 ", "에 옮겼습니다."), "7AE2F81C66B488E9169629866DBE5DEB7E3F2CDDA14E4D80EA2C57F59F4CE58D", ("", "026432", "026532", "050505")),
    row(2, 300, ("적의 모략을 막을 자:", "한조", "이(가)\n막을 터이니 걱정은 무용…"), ("적의 모략은 모두", "한조", "가\n막을 테니 걱정은 무용…"), "21AB705B6E3921D378E6BC1517C45085D80B86A7A2FDF557BEDBD2BCD3C33D16", ("", "1B4341", "1B435A", "050505")),
    row(2, 320, ("담당자:", "은(는) 농사에 제법 일가견이 있다!\n내 지식으로 이 영지를 풍요롭게 하겠다."), ("나 ", ", 농사에는 제법 일가견이 있다!\n내 지식으로 이 영지를 풍요롭게 하겠다."), "8587B0BD1E80E99045A1E951F01D54D22859DEF11C24FEDE448F0731638E9A59", ("", "024635", "050505")),
    row(2, 331, ("정찰 담당:", "이(가) 협공을\n눈치채지 못할 줄 알았나?"), ("나 ", ", 협공을\n눈치채지 못할 줄 알았나?"), "B4590D1E648CBA83821FDAB39B2FDEFEA459FCAA01257B51A816CED465D07B7D", ("", "024635", "050505")),
    row(2, 341, ("모든 일을 내게 맡겨 주십시오.\n오른눈이 될 자:", "이(가) 주군의 오른눈이 되겠습니다!"), ("모든 일을 제게 맡겨 주십시오.\n저 ", ", 주군의 오른팔이 되겠습니다!"), "F40E2D73CCDF981F62D8717D6F90CAE3E115074526DB6BC2AEB2C3C1EDCDDE02", ("", "024635", "050505")),
    row(2, 434, ("내 야망의 막이 이제 오른다.\n전국에 새바람을 일으킬 자:", "이(가) 바로 나다!"), ("내 야망의 막이 이제 오른다.\n이 ", ", 전국에 새바람을 일으키겠다!"), "FC563D3CA7DC7053032D83F5FC45EB3AA4169FC18F5DA8DCD31F5334D50A60B3", ("", "024635", "050505")),
    row(2, 563, ("이 정도는 열세도 아니다.\n십문자창으로 뒤집을 자:", "이(가) 전세를 뒤집는다!"), ("이 정도는 열세도 아니다.\n여기서는 ", ", 십문자창으로 만회하겠다!"), "2FBB91EA4A61E2D7D3C1F3260E998E613A1FF261D80F6235439B3A880A041EB9", ("", "024634", "050505")),
    row(6, 2328, ("이 대가의 수락 여부를 정할 상대:", "이(가), 수락할지는\n부딪쳐 봐야겠군…"), ("이 정도 보상으로 ", "의 수락을\n얻을 수 있을지는 두고 봐야겠군…"), "3FA0FE4E8D3C1D29E6771636A2CD1F760766B47CC39A136117CACAA9F2B72DD3", ("", "024735", "050505")),
    row(6, 2750, ("무력으로 쓰러뜨리는 것이 최선이지만:", "은(는)\n그것만으로는 쓰러지지 않으리, 어쩔 수 없다"), ("무력으로 굴복시키는 것이 최선이나,\n", "의 경우 그것만으로는 어려운 듯하군…"), "F2167E0D75D52C35EF6D174CFE59CEB4BD401F85C903297B9D6A4010058D373C", ("", "025032", "050505")),
    row(6, 2910, (": 맹약을 파기하다니!?\n배후 세력:", "이(가) 뒤에서 조종하고 있음이\n틀림없군요"), (" 측이 맹약을 저버리다니…!?\n큭, 배후에는 ", " 측이\n관여한 것이 틀림없군요."), "6A326557808E5CB1076608472BF85AC4520ED84EE73DA714EFE0BE6599FC37DD", ("025032", "025132", "050505")),
    row(15, 643, ("본가와 유대를 이어 갈 세력:", "은(는) 이제\n운명 공동체라 할 수 있사옵니다\n속히 산하에 거두어야 할 줄로 아옵니다"), ("우리와 ", " 측은 이제\n운명 공동체라 할 수 있사옵니다\n속히 산하에 거두어야 할 줄로 아옵니다"), "38B55D4DED7408EA864370CF9EF8D5EE1B012E69516AD085CB066EBF18D32042", ("", "028C32", "050505")),
    row(15, 667, ("본가와 유대를 이어 갈 세력:", "은(는)\n이제 한배를 탄 사이\n속히 산하에 거두어야 할 줄로 아옵니다"), ("우리와 ", " 측은\n이제 한배를 탄 사이\n속히 산하에 거두어야 할 줄로 아옵니다"), "5A9E97114FF61516139602E412F4F8FD22C7FA0E26636504DB626A814AC3BC2D", ("", "028C32", "050505")),
    row(15, 679, ("본가와 유대를 이어 갈 세력:", "은(는)\n이제 한배를 탄 사이\n속히 산하에 거두어야 할 줄로 아옵니다"), ("우리와 ", " 측은\n이제 한배를 탄 사이\n속히 산하에 거두어야 할 줄로 아옵니다"), "5A9E97114FF61516139602E412F4F8FD22C7FA0E26636504DB626A814AC3BC2D", ("", "028C32", "050505")),
)

# These eight rows are intentionally a separate, high-confidence terminology
# group. Their output is mechanically restricted to one term substitution.
GUSIN_TERMINOLOGY_ROWS = (
    row(6, 563, ("구신에 아무 소식이 없군……",), ("건의에 아무 소식이 없군……",), "1688E18F22CF55EA0F3C696227E3992945AB00C7B0335835A21752A8F3F616C7", ("", "050505"), GROUP_GUSIN_TERMINOLOGY),
    row(6, 572, ("그렇게 자신 있게 구신했건만\n내버려 두다니……",), ("그렇게 자신 있게 건의했건만\n내버려 두다니……",), "A492F6F957A68D6E30CF54ACDECCEEEEB81C79A946E0B53C1B5DE14BDF402160", ("", "050505"), GROUP_GUSIN_TERMINOLOGY),
    row(6, 1195, ("방침을 바꾸면 제안 중인 구신을 철회하고\n새 방침에 따라 가신에게 새 제안을 요청합니다\n계속하시겠습니까?",), ("방침을 바꾸면 제안 중인 건의를 철회하고\n새 방침에 따라 가신에게 새 제안을 요청합니다\n계속하시겠습니까?",), "CE900CE8D44A3E73CBC546C7A9E13161817C8579053A3F84DD641D1EB85B2C3F", ("", "050505"), GROUP_GUSIN_TERMINOLOGY),
    row(6, 1396, ("이 군단의 모든 구신이 발생합니다.",), ("이 군단의 모든 건의가 발생합니다.",), "78CE396414AC0203C3B8580B66D15CC92A7C55F1A1D511D97D500DD5A9A9F05C", ("", "050505"), GROUP_GUSIN_TERMINOLOGY),
    row(6, 1397, ("이 군단에서는 물자 관련 구신만 발생합니다.",), ("이 군단에서는 물자 관련 건의만 발생합니다.",), "95437D860BE50631E2405FCA1D27E8EFC1A9CF1D7173F5BB326448EE4942A501", ("", "050505"), GROUP_GUSIN_TERMINOLOGY),
    row(6, 1398, ("이 군단에서는 무장 관련 구신만 발생합니다.",), ("이 군단에서는 무장 관련 건의만 발생합니다.",), "BD0CBFAB10FE7BBB27309BCD2E5AF1DF0B6F061982201AAD4A86825470EB5103", ("", "050505"), GROUP_GUSIN_TERMINOLOGY),
    row(6, 1399, ("이 군단에서는 어떤 구신도 발생하지 않습니다.",), ("이 군단에서는 어떤 건의도 발생하지 않습니다.",), "42315738EC75E1ADF17AC9F9AB2781E2B0B5F02A43CF2CEB04A00B5F3C65D2EB", ("", "050505"), GROUP_GUSIN_TERMINOLOGY),
    row(6, 1472, ("편성한 무장이나 성이 임무 또는 구신을\n실행 중이라면 중지됩니다\n계속하시겠습니까?",), ("편성한 무장이나 성이 임무 또는 건의를\n실행 중이라면 중지됩니다\n계속하시겠습니까?",), "1F1D373F63284ECAB99A14997B2DFD306B7A358DA0F617FD08DBD27FC2890A0D", ("", "050505"), GROUP_GUSIN_TERMINOLOGY),
)

ALL_ROWS = (*RUNTIME_LAYOUT_ROWS, *GUSIN_TERMINOLOGY_ROWS)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def ensure_under(path: Path, root: Path, label: str) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave9Error(f"{label} must remain under {resolved_root}: {resolved_path}") from exc
    return resolved_path


def require_private_output(path: Path, label: str) -> Path:
    return ensure_under(path, PRIVATE_TMP_ROOT, label)


def profile_hashes(root: Path) -> dict[str, str]:
    return {relative: sha256_path(root / Path(relative)) for relative in PROFILE_PATHS}


def require_wave8_input_root(input_root: Path) -> dict[str, str]:
    resolved = input_root.resolve()
    if not resolved.is_dir():
        raise Wave9Error(f"Wave 8 private candidate is missing: {resolved}")
    if "switch" in "/".join(part.lower() for part in resolved.parts):
        raise Wave9Error("Nintendo Switch Korean input is explicitly excluded")
    missing = [relative for relative in PROFILE_PATHS if not (resolved / relative).is_file()]
    if missing:
        raise Wave9Error(f"Wave 8 private candidate is incomplete: {missing}")
    actual = profile_hashes(resolved)
    if actual != INPUT_SHA256:
        mismatch = {
            relative: {"expected": INPUT_SHA256[relative], "actual": actual[relative]}
            for relative in PROFILE_PATHS
            if actual[relative] != INPUT_SHA256[relative]
        }
        raise Wave9Error(f"Wave 8 profile hash mismatch: {mismatch}")
    return actual


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    parsed = parse_packed_msggame(packed)
    return {
        (record.block_id, record.record_id): record
        for block in parsed.archive.blocks
        for record in block.records
    }


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    cursor = 0
    values: list[bytes] = []
    for literal in parse_record_literals(record):
        values.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    values.append(record.data[cursor:])
    return tuple(values)


def literal_marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return tuple(
        (
            record.data[literal.marker_offset : literal.marker_offset + len(LITERAL_START)],
            record.data[literal.marker_end - len(LITERAL_END) : literal.marker_end],
        )
        for literal in parse_record_literals(record)
    )


def flatten_static_lines(literals: Iterable[str]) -> tuple[str, ...]:
    lines: list[str] = []
    for value in literals:
        lines.extend(value.split("\n"))
    return tuple(lines)


def load_font_advance(font_root: Path) -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    font_path = (font_root / "RES_JP" / "res_lang.bin").resolve()
    if not font_path.is_file():
        raise Wave9Error(f"current PC font resource is missing: {font_path}")
    try:
        archive = parse_link(font_path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[6].data)
    except (IndexError, ValueError) as exc:
        raise Wave9Error("current PC font entry 6 cannot be unpacked") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_wave9_font_") as directory:
        g1n_path = Path(directory) / "font.g1n"
        g1n_path.write_bytes(raw)
        parsed = g1n.parse_g1n(g1n_path)
    if parsed.structural_errors or not parsed.tables:
        raise Wave9Error("current PC font entry 6 has an invalid G1N structure")
    table = parsed.tables[0]

    def advance(character: str) -> tuple[int, bool]:
        if len(character) != 1:
            raise Wave9Error("font width request must be one Unicode character")
        codepoint = ord(character)
        ordinal = table.mapping[codepoint] if codepoint < len(table.mapping) else 0
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character):
                return 48, True
            raise Wave9Error(f"current PC font lacks static glyph U+{codepoint:04X}")
        if ordinal >= len(table.records):
            raise Wave9Error(
                f"current PC font glyph ordinal is invalid for U+{codepoint:04X}"
            )
        glyph = table.records[ordinal]
        if glyph.width != glyph.advance or glyph.advance not in (24, 48):
            raise Wave9Error(
                f"current PC font metric is invalid for U+{codepoint:04X}"
            )
        return glyph.advance, False

    return advance, {
        "resource": "RES_JP/res_lang.bin",
        "entry": 6,
        "packed_sha256": sha256_path(font_path),
        "table_count": len(parsed.tables),
    }


def static_line_widths(
    literals: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    widths: list[int] = []
    fallback_codepoints: set[str] = set()
    for line in flatten_static_lines(literals):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                raise Wave9Error(f"candidate static text contains control U+{ord(character):04X}")
            character_width, used_wide_fallback = advance(character)
            width += character_width
            if used_wide_fallback:
                fallback_codepoints.add(f"U+{ord(character):04X}")
        widths.append(width)
    return tuple(widths), tuple(sorted(fallback_codepoints))


def validate_terminology_references() -> dict[str, str]:
    reference_records: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    for label, path in PC_REFERENCE_MSGGAME.items():
        if not path.is_file():
            raise Wave9Error(f"PC terminology reference is missing: {label}")
        actual_hash = sha256_path(path)
        if actual_hash != PC_REFERENCE_SHA256[label]:
            raise Wave9Error(f"PC terminology reference hash changed: {label}")
        reference_records[label] = records_by_coordinate(path.read_bytes())
    for row_value in GUSIN_TERMINOLOGY_ROWS:
        jp_record = reference_records["pc_jp_pristine"].get(row_value.coordinate)
        if jp_record is None or "具申" not in "".join(literal_texts(jp_record)):
            raise Wave9Error(f"{row_value.key} is not a pristine PC Japanese 具申 row")
        for label in ("pc_en", "pc_sc", "pc_tc"):
            reference_record = reference_records[label].get(row_value.coordinate)
            if reference_record is None or not literal_texts(reference_record):
                raise Wave9Error(f"{row_value.key} lacks PC {label} context")
    return dict(PC_REFERENCE_SHA256)


def validate_row_definitions() -> None:
    coordinates = [item.coordinate for item in ALL_ROWS]
    if len(RUNTIME_LAYOUT_ROWS) != 25:
        raise Wave9Error("runtime linebreak group must contain exactly 25 records")
    if len(GUSIN_TERMINOLOGY_ROWS) != 8:
        raise Wave9Error("high-confidence terminology group must contain exactly 8 records")
    if len(coordinates) != 33 or len(set(coordinates)) != len(coordinates):
        raise Wave9Error("Wave 9 must contain exactly 33 unique physical records")
    if not LONG_RUNTIME_VALUE_ROWS.issubset(set(coordinates)):
        raise Wave9Error("long-runtime QA coordinate contract is incomplete")
    for item in ALL_ROWS:
        if len(item.current_literals) != len(item.output_literals):
            raise Wave9Error(f"{item.key} changed literal-slot topology")
        if len(item.opaque_spans_hex) != len(item.current_literals) + 1:
            raise Wave9Error(f"{item.key} opaque-span topology is invalid")
        if len(item.input_record_sha256) != 64:
            raise Wave9Error(f"{item.key} input record hash is invalid")
        if EXCLUDED_HOMOGRAPH in "".join(item.current_literals + item.output_literals):
            raise Wave9Error(f"{item.key} contains the explicitly excluded homograph")
        if not any(before != after for before, after in zip(item.current_literals, item.output_literals)):
            raise Wave9Error(f"{item.key} has no actual text change")
    for item in GUSIN_TERMINOLOGY_ROWS:
        exception = TERMINOLOGY_GRAMMAR_EXCEPTIONS.get(item.coordinate)
        if exception is None:
            expected_output = tuple(
                value.replace("구신", "건의") for value in item.current_literals
            )
        else:
            source_fragment, replacement_fragment = exception
            expected_output = tuple(
                value.replace(source_fragment, replacement_fragment)
                for value in item.current_literals
            )
        if item.output_literals != expected_output:
            raise Wave9Error(
                f"{item.key} terminology group changed beyond its allowed term grammar"
            )
        if "구신" not in "".join(item.current_literals):
            raise Wave9Error(f"{item.key} terminology group lacks its source term")


def validate_row_input(row_value: RuntimeRow, input_record: MsgGameRecord) -> None:
    if sha256_bytes(input_record.data) != row_value.input_record_sha256:
        raise Wave9Error(f"{row_value.key} Wave 8 preimage record hash mismatch")
    if literal_texts(input_record) != row_value.current_literals:
        raise Wave9Error(f"{row_value.key} Wave 8 literal tuple mismatch")
    actual_opaque = tuple(value.hex().upper() for value in opaque_spans(input_record))
    if actual_opaque != row_value.opaque_spans_hex:
        raise Wave9Error(f"{row_value.key} opaque-token schema mismatch")
    topology = literal_marker_topology(input_record)
    if topology != tuple((LITERAL_START, LITERAL_END) for _ in row_value.current_literals):
        raise Wave9Error(f"{row_value.key} literal-marker topology mismatch")
    if not input_record.data.endswith(RECORD_TERMINATOR):
        raise Wave9Error(f"{row_value.key} lacks the required record terminator")


def rebuild_row(row_value: RuntimeRow, input_record: MsgGameRecord) -> MsgGameRecord:
    replacement_map = {
        literal_id: replacement
        for literal_id, replacement in enumerate(row_value.output_literals)
    }
    rebuilt = MsgGameRecord(
        block_id=input_record.block_id,
        record_id=input_record.record_id,
        relative_offset=input_record.relative_offset,
        data=rebuild_record_literals(input_record, replacement_map),
    )
    if literal_texts(rebuilt) != row_value.output_literals:
        raise Wave9Error(f"{row_value.key} rebuilt literal tuple mismatch")
    if opaque_spans(rebuilt) != opaque_spans(input_record):
        raise Wave9Error(f"{row_value.key} altered opaque bytes or runtime tokens")
    if literal_marker_topology(rebuilt) != literal_marker_topology(input_record):
        raise Wave9Error(f"{row_value.key} altered literal-marker topology")
    if not rebuilt.data.endswith(RECORD_TERMINATOR):
        raise Wave9Error(f"{row_value.key} altered the record terminator")
    return rebuilt


def source_free_row_audit(
    row_value: RuntimeRow,
    input_record: MsgGameRecord,
    output_record: MsgGameRecord,
    advance: Callable[[str], tuple[int, bool]],
) -> dict[str, Any]:
    input_widths, input_fallbacks = static_line_widths(row_value.current_literals, advance)
    output_widths, output_fallbacks = static_line_widths(row_value.output_literals, advance)
    opaque = opaque_spans(input_record)
    if opaque != opaque_spans(output_record):
        raise Wave9Error(f"{row_value.key} audit saw an opaque-byte change")
    return {
        "coordinate": row_value.key,
        "group": row_value.group,
        "input_record_sha256": sha256_bytes(input_record.data),
        "output_record_sha256": sha256_bytes(output_record.data),
        "literal_slot_count": len(row_value.current_literals),
        "input_literal_utf16le_sha256": [text_hash(value) for value in row_value.current_literals],
        "output_literal_utf16le_sha256": [text_hash(value) for value in row_value.output_literals],
        "input_literal_characters": [len(value) for value in row_value.current_literals],
        "output_literal_characters": [len(value) for value in row_value.output_literals],
        "opaque_span_sha256": [sha256_bytes(value) for value in opaque],
        "opaque_span_bytes": [len(value) for value in opaque],
        "literal_marker_topology": [
            {"start": start.hex().upper(), "end": end.hex().upper()}
            for start, end in literal_marker_topology(input_record)
        ],
        "terminator_hex": RECORD_TERMINATOR.hex().upper(),
        "input_static_line_widths": list(input_widths),
        "output_static_line_widths": list(output_widths),
        "input_static_max_width": max(input_widths, default=0),
        "output_static_max_width": max(output_widths, default=0),
        "missing_static_glyphs": [],
        "input_wide_fallback_codepoints": list(input_fallbacks),
        "output_wide_fallback_codepoints": list(output_fallbacks),
        "real_game_qa_required_before_release": True,
        "requires_long_runtime_value_qa": row_value.coordinate in LONG_RUNTIME_VALUE_ROWS,
    }


def validate_full_output(
    input_packed: bytes,
    output_packed: bytes,
    expected_records: Mapping[tuple[int, int], MsgGameRecord],
) -> None:
    before = records_by_coordinate(input_packed)
    after = records_by_coordinate(output_packed)
    if before.keys() != after.keys():
        raise Wave9Error("candidate changed msggame record topology")
    changed = {
        coordinate
        for coordinate in before
        if before[coordinate].data != after[coordinate].data
    }
    if changed != set(expected_records):
        raise Wave9Error(
            "candidate changed records outside the 33-row contract: "
            f"expected={sorted(expected_records)} actual={sorted(changed)}"
        )
    for coordinate, expected in expected_records.items():
        if after[coordinate].data != expected.data:
            raise Wave9Error(f"{coordinate[0]}:{coordinate[1]} output record mismatch")


@dataclass(frozen=True)
class CandidateBundle:
    packed_msggame: bytes
    input_profile_sha256: dict[str, str]
    output_profile_sha256: dict[str, str]
    audit: dict[str, Any]


def prepare_candidate(input_root: Path, font_root: Path) -> CandidateBundle:
    validate_row_definitions()
    terminology_reference_hashes = validate_terminology_references()
    input_profile = require_wave8_input_root(input_root)
    packed_path = input_root.resolve() / Path(RESOURCE)
    input_packed = packed_path.read_bytes()
    if sha256_bytes(input_packed) != INPUT_SHA256[RESOURCE]:
        raise Wave9Error("Wave 8 msggame profile hash changed while reading")
    advance, font_evidence = load_font_advance(font_root)
    input_records = records_by_coordinate(input_packed)
    replacements: dict[tuple[int, int], bytes] = {}
    expected_output_records: dict[tuple[int, int], MsgGameRecord] = {}
    audit_rows: list[dict[str, Any]] = []

    for row_value in ALL_ROWS:
        input_record = input_records.get(row_value.coordinate)
        if input_record is None:
            raise Wave9Error(f"{row_value.key} is absent from the Wave 8 msggame")
        validate_row_input(row_value, input_record)
        output_record = rebuild_row(row_value, input_record)
        replacements[row_value.coordinate] = output_record.data
        expected_output_records[row_value.coordinate] = output_record
        audit_rows.append(source_free_row_audit(row_value, input_record, output_record, advance))

    output_packed = rebuild_packed_msggame(input_packed, replacements)
    validate_full_output(input_packed, output_packed, expected_output_records)
    output_profile = dict(input_profile)
    output_profile[RESOURCE] = sha256_bytes(output_packed)
    if TARGET_SHA256[RESOURCE]:
        if output_profile != TARGET_SHA256:
            mismatch = {
                relative: {"expected": TARGET_SHA256[relative], "actual": output_profile[relative]}
                for relative in PROFILE_PATHS
                if output_profile[relative] != TARGET_SHA256[relative]
            }
            raise Wave9Error(f"Wave 9 target profile hash mismatch: {mismatch}")

    changed_payload_hashes = {sha256_bytes(item.data) for item in expected_output_records.values()}
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_free": True,
        "literal_source_text_embedded": False,
        "source_policy": {
            "platform": "Steam PC",
            "allowed_reference_sets": ["PC JP", "PC EN", "PC SC", "PC TC"],
            "input_text_profile": "Wave 8 private PC candidate",
            "excluded": ["Nintendo Switch Korean"],
            "switch_korean_used": False,
        },
        "steam_write_capability": "absent",
        "input_profile_sha256": input_profile,
        "output_profile_sha256": output_profile,
        "font_evidence": font_evidence,
        "terminology_reference_evidence": {
            "group": GROUP_GUSIN_TERMINOLOGY,
            "pc_reference_sha256": terminology_reference_hashes,
            "pristine_jp_required_codepoints": ["U+5177", "U+7533"],
            "explicit_homograph_exclusion_enforced": True,
            "necessary_case_particle_adjustment_rows": [
                f"{block_id}:{record_id}"
                for block_id, record_id in sorted(TERMINOLOGY_GRAMMAR_EXCEPTIONS)
            ],
        },
        "summary": {
            "physical_records": len(ALL_ROWS),
            "runtime_linebreak_and_phrase_records": len(RUNTIME_LAYOUT_ROWS),
            "high_confidence_terminology_records": len(GUSIN_TERMINOLOGY_ROWS),
            "unique_output_record_payloads": len(changed_payload_hashes),
            "changed_resource": RESOURCE,
            "real_game_qa_required_before_release": True,
            "long_runtime_value_rows": [
                f"{block_id}:{record_id}"
                for block_id, record_id in sorted(LONG_RUNTIME_VALUE_ROWS)
            ],
        },
        "records": audit_rows,
    }
    return CandidateBundle(
        packed_msggame=output_packed,
        input_profile_sha256=input_profile,
        output_profile_sha256=output_profile,
        audit=audit,
    )


def atomic_write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(value)
    os.replace(temporary, path)


def write_json(path: Path, value: Mapping[str, Any]) -> str:
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    atomic_write_bytes(path, payload)
    return sha256_bytes(payload)


def write_candidate(bundle: CandidateBundle, input_root: Path, output_root: Path) -> None:
    output_root = require_private_output(output_root, "candidate output")
    if output_root.exists():
        raise Wave9Error(f"refusing to overwrite an existing candidate directory: {output_root}")
    output_root.mkdir(parents=True)
    for relative in PROFILE_PATHS:
        destination = output_root / Path(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative == RESOURCE:
            atomic_write_bytes(destination, bundle.packed_msggame)
        else:
            shutil.copy2(input_root / Path(relative), destination)
    actual = profile_hashes(output_root)
    if actual != bundle.output_profile_sha256:
        raise Wave9Error("written candidate profile hash mismatch")


def build_manifest(bundle: CandidateBundle, audit_sha256: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source_free_audit": True,
        "source_free_audit_sha256": audit_sha256,
        "steam_write_capability": "absent",
        "steam_apply_command": None,
        "input_profile_sha256": bundle.input_profile_sha256,
        "output_profile_sha256": bundle.output_profile_sha256,
        "changed_paths": [RESOURCE],
        "subgroups": {
            GROUP_RUNTIME_LAYOUT: [row_value.key for row_value in RUNTIME_LAYOUT_ROWS],
            GROUP_GUSIN_TERMINOLOGY: [row_value.key for row_value in GUSIN_TERMINOLOGY_ROWS],
        },
        "real_game_qa_required_before_release": True,
        "long_runtime_value_rows": [
            f"{block_id}:{record_id}"
            for block_id, record_id in sorted(LONG_RUNTIME_VALUE_ROWS)
        ],
    }


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def command_audit(args: argparse.Namespace) -> int:
    audit_path = require_private_output(args.audit_path, "audit output")
    bundle = prepare_candidate(args.input_root, args.font_root)
    audit_sha256 = write_json(audit_path, bundle.audit)
    print_json(
        {
            "status": "ok",
            "audit": audit_path.relative_to(REPO).as_posix(),
            "audit_sha256": audit_sha256,
            "output_profile_sha256": bundle.output_profile_sha256,
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_build(args: argparse.Namespace) -> int:
    output_root = require_private_output(args.output_root, "candidate output")
    audit_path = require_private_output(args.audit_path, "audit output")
    manifest_path = require_private_output(args.manifest, "manifest output")
    bundle = prepare_candidate(args.input_root, args.font_root)
    write_candidate(bundle, args.input_root.resolve(), output_root)
    audit_sha256 = write_json(audit_path, bundle.audit)
    manifest = build_manifest(bundle, audit_sha256)
    manifest_sha256 = write_json(manifest_path, manifest)
    print_json(
        {
            "status": "ok",
            "candidate": output_root.relative_to(REPO).as_posix(),
            "audit": audit_path.relative_to(REPO).as_posix(),
            "manifest": manifest_path.relative_to(REPO).as_posix(),
            "audit_sha256": audit_sha256,
            "manifest_sha256": manifest_sha256,
            "output_profile_sha256": bundle.output_profile_sha256,
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_hash(args: argparse.Namespace) -> int:
    bundle = prepare_candidate(args.input_root, args.font_root)
    print_json(
        {
            "status": "ok",
            "output_profile_sha256": bundle.output_profile_sha256,
            "candidate_records": len(ALL_ROWS),
            "steam_write_capability": "absent",
        }
    )
    return 0


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input-root", type=Path, default=WAVE8_INPUT_ROOT)
    parser.add_argument("--font-root", type=Path, default=DEFAULT_FONT_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    hash_parser = subparsers.add_parser("hash", help="validate and print private output hashes")
    add_input_arguments(hash_parser)
    hash_parser.set_defaults(func=command_hash)
    audit_parser = subparsers.add_parser("audit", help="write a source-free private audit")
    add_input_arguments(audit_parser)
    audit_parser.add_argument(
        "--audit-path",
        type=Path,
        default=PRIVATE_TMP_ROOT / "audit_pc_dialogue_runtime_wave9.v1.json",
    )
    audit_parser.set_defaults(func=command_audit)
    build_parser_value = subparsers.add_parser(
        "build", help="write a private candidate, source-free audit, and manifest"
    )
    add_input_arguments(build_parser_value)
    build_parser_value.add_argument(
        "--output-root", type=Path, default=PRIVATE_TMP_ROOT / "candidate-build-1"
    )
    build_parser_value.add_argument(
        "--audit-path",
        type=Path,
        default=PRIVATE_TMP_ROOT / "audit_pc_dialogue_runtime_wave9.v1.json",
    )
    build_parser_value.add_argument(
        "--manifest", type=Path, default=PRIVATE_TMP_ROOT / "build_manifest.v1.json"
    )
    build_parser_value.set_defaults(func=command_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Wave9Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
