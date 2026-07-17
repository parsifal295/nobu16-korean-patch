#!/usr/bin/env python3
"""Build the first PC-only Korean dialogue quality repair wave.

This deliberately small, source-gated wave repairs only issues whose Korean
replacement is confirmed against the pristine PC Japanese resource.  It keeps
all dynamic-name bytecode, ESC colour tags, literal boundaries, and unrelated
files byte-for-byte intact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME = REPO / "workstreams" / "msggame"
STRDATA = REPO / "workstreams" / "strdata"
sys.path[:0] = [str(TOOLS), str(MSGGAME), str(STRDATA)]

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_record_literals,
)
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_format import parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"

# The installed PC-only state after the ID 9332 event reflow.  The script
# refuses any other baseline, so a later manual/local change cannot be
# silently replaced.
BASELINE_SHA256 = {
    "MSG/JP/ev_strdata.bin": "AEB9FAEFDA9CFF9B8048394C0EE79653F1FCC18B3F9B97BA058EEF86354F3CFC",
    "MSG/JP/msggame.bin": "8C9D7CBD9E614932A515A8B00A3CFA079818C4A929CF50080E940568CC9E57F4",
    "MSG/JP/strdata.bin": "580AF0520CA0211BF1B12A76F2FB011FD195364B23485CB29479211328961BC7",
    "MSG_PK/JP/msgbre.bin": "92C9AFF3B8238E5925CC5A3508BBBD4F699A33182F373CA0FDF71457742A235B",
    "MSG_PK/JP/msgdata.bin": "973AEE65A7E247B7E053BBE493DA92C4E0458A5E300CC032116D4FB7CBBF5E8D",
    "MSG_PK/JP/msgev.bin": "3E606351730F24A87C218E582BB80E14959FE3AC9DE00C5AA9A5BF1E35A51BC5",
    "MSG_PK/JP/msggame.bin": "07E96591A44C0BB5FBA0E2506010AE2E235E917F2AEC866758EC190A6850731F",
    "MSG_PK/JP/msgire.bin": "3D3B30E8341781089CA96AD147F0ADDD4417DCF57F0EF2998726E2EC0F64E2FE",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
# The exact installed PC-only target produced from BASELINE_SHA256 by this
# wave.  Retained resources deliberately keep their baseline hash.
TARGET_SHA256 = {
    "MSG/JP/ev_strdata.bin": "25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834",
    "MSG/JP/msggame.bin": "04C9C6C63894ED2525B1107C2D251F55B081C5AB246C021CC262378F6028C938",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "9572873D2BBFF3C62581F09BE2CD54225CCDD2C400D3ACC895675E2C0A2780DD",
    "MSG_PK/JP/msggame.bin": "6A3B84E4664809062E5105640F26F3CEABA69DA3675051939497590E5EFB99DE",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
PROFILE_TARGETS = tuple(BASELINE_SHA256)
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave1.v1"


@dataclass(frozen=True)
class CommonFix:
    relative: str
    entry_id: int
    before: str
    after: str


@dataclass(frozen=True)
class StrdataFix:
    block_id: int
    entry_id: int
    before: str
    after: str


@dataclass(frozen=True)
class LiteralFix:
    relative: str
    block_id: int
    record_id: int
    literal_id: int
    before: str
    after: str

    @property
    def coordinate(self) -> str:
        return f"{self.block_id}:{self.record_id}:{self.literal_id}"


class QualityWaveError(ValueError):
    """Raised when a source, format, or candidate gate does not match."""


# Generic NPC/title labels.  Proper nouns such as 御所 are not included: only
# source 小姓 / 小姓頭 contexts reached through the listed resource IDs change.
COMMON_FIXES = (
    CommonFix("MSG/JP/ev_strdata.bin", 2792, "고쇼", "시동"),
    CommonFix("MSG_PK/JP/msgev.bin", 2792, "고쇼", "시동"),
    CommonFix(
        "MSG_PK/JP/msgdata.bin",
        18031,
        "총성에 잠에서 깬 노부나가에게\n고쇼가 모반의 뜻을 전했다.",
        "총성에 잠에서 깬 노부나가에게\n시동이 모반의 뜻을 전했다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        580,
        "도쿠가와 가신. 고슈류 병학자이며 마사모리의 아들이다. 주군 히데타다의 고쇼가 되었으나 뒤에 출분했고, 오사카 전투 뒤 귀참했다. 고슈류 병학을 집대성해 많은 제자를 가르쳤다.",
        "도쿠가와 가신. 고슈류 병학자이며 마사모리의 아들이다. 주군 히데타다의 시동이 되었으나 뒤에 출분했고, 오사카 전투 뒤 귀참했다. 고슈류 병학을 집대성해 많은 제자를 가르쳤다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        758,
        "아라키 가신. 주군 무라시게의 소성을 지냈다. 주가 몰락 뒤 도요토미 히데요시를 섬겼고, 뒤에 기노시타 성을 하사받아 이나바 와카사 2만 석을 받았다. 세키가하라 전투에서는 서군에 속했으며 전후 자결했다.",
        "아라키 가신. 주군 무라시게의 시동을 지냈다. 주가 몰락 뒤 도요토미 히데요시를 섬겼고, 뒤에 기노시타 성을 하사받아 이나바 와카사 2만 석을 받았다. 세키가하라 전투에서는 서군에 속했으며 전후 자결했다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        761,
        "도요토미 가신. 사다미쓰의 아들이라고 한다. 주군 히데요리의 유형제로서 소성을 지냈다. 도쿠가와 가문과 화친할 때는 도요토미 가문의 사자를 맡았다. 오사카 여름 전투에서 이이 나오타카군과 싸우다 전사했다.",
        "도요토미 가신. 사다미쓰의 아들이라고 한다. 주군 히데요리의 유형제로서 시동을 지냈다. 도쿠가와 가문과 화친할 때는 도요토미 가문의 사자를 맡았다. 오사카 여름 전투에서 이이 나오타카군과 싸우다 전사했다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        934,
        "마쓰마에 가신. 아버지 대에 에조로 이주하여 마쓰마에 긴히로를 고쇼로서 섬겼다. 이후 마치부교가 되었다. 후쿠야마관의 화재에서 긴히로를 구출하였으나, 그때의 화상이 원인이 되어 사망하였다.",
        "마쓰마에 가신. 아버지 대에 에조로 이주하여 마쓰마에 긴히로를 시동으로서 섬겼다. 이후 마치부교가 되었다. 후쿠야마관의 화재에서 긴히로를 구출하였으나, 그때의 화상이 원인이 되어 사망하였다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        1440,
        "도쿠가와 가신. 주군 이에야스의 고쇼를 맡았다. 이에야스의 신뢰를 받아 히데타다의 사부역과 간토소부교 등을 역임했다. 그러나 훗날 이에야스의 노여움을 사 은거의 몸이 되었다.",
        "도쿠가와 가신. 주군 이에야스의 시동을 맡았다. 이에야스의 신뢰를 받아 히데타다의 사부역과 간토소부교 등을 역임했다. 그러나 훗날 이에야스의 노여움을 사 은거의 몸이 되었다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        1542,
        "오사키 가신. 니이다성주. 요시타카의 소성을 맡았다. 가중 굴지의 미소년으로, 같은 소성인 이바노 소하치로와 총애를 다투었고, 이것이 계기가 되어 오사키 가문의 내란이 일어났다.",
        "오사키 가신. 니이다성주. 요시타카의 시동을 맡았다. 가중 굴지의 미소년으로, 같은 시동인 이바노 소하치로와 총애를 다투었고, 이것이 계기가 되어 오사키 가문의 내란이 일어났다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        1879,
        "오코치 히사쓰나의 장남. 도쿠가와 이에미쓰를 섬겨 소성에서 노중까지 출세해 '지혜 이즈'라는 별명을 얻었다. 시마바라의 난에서는 총대장을 맡아 진압에 성공했다.",
        "오코치 히사쓰나의 장남. 도쿠가와 이에미쓰를 섬겨 시동에서 노중까지 출세해 '지혜 이즈'라는 별명을 얻었다. 시마바라의 난에서는 총대장을 맡아 진압에 성공했다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        2009,
        "시바타 가신. 주군 가쓰이에의 고쇼가시라로서 1만 석을 다스렸다. 시즈가타케 합전에서 시바타군이 무너져 달아났을 때 하시바군의 추격을 막으며 분전하였다. 가쓰이에를 에치젠으로 퇴각시킨 뒤 전사하였다.",
        "시바타 가신. 주군 가쓰이에의 시동장으로서 1만 석을 다스렸다. 시즈가타케 합전에서 시바타군이 무너져 달아났을 때 하시바군의 추격을 막으며 분전하였다. 가쓰이에를 에치젠으로 퇴각시킨 뒤 전사하였다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgbre.bin",
        2041,
        "오다 가신. 요시나리의 삼남. 주군 노부나가의 고쇼를 맡는다. 영리하고 용모가 아름다워 노부나가에게 총애받았다. 장래가 촉망되었으나 혼노지의 변에서 노부나가를 따라 분전하다 전사했다.",
        "오다 가신. 요시나리의 삼남. 주군 노부나가의 시동을 맡는다. 영리하고 용모가 아름다워 노부나가에게 총애받았다. 장래가 촉망되었으나 혼노지의 변에서 노부나가를 따라 분전하다 전사했다.",
    ),
    CommonFix(
        "MSG_PK/JP/msgire.bin",
        121,
        "가마쿠라 시대 도공 도사부로 유키미쓰가 만든 단도로 오다 노부나가가 아낀 칼이다. 노부나가가 고쇼 모리 란마루의 성실함을 칭찬하며 이 칼을 주었다는 설이 있다.",
        "가마쿠라 시대 도공 도사부로 유키미쓰가 만든 단도로 오다 노부나가가 아낀 칼이다. 노부나가가 시동 모리 란마루의 성실함을 칭찬하며 이 칼을 주었다는 설이 있다.",
    ),
)

STRDATA_FIXES = (
    StrdataFix(0, 17929, "총성에 잠에서 깬 노부나가에게\n고쇼가 모반의 뜻을 전했다.", "총성에 잠에서 깬 노부나가에게\n시동이 모반의 뜻을 전했다."),
    StrdataFix(2, 580, "도쿠가와 가신. 고슈류 병학자. 마사모리의 아들. 주군 히데타다의 고쇼가 되었으나 훗날 출분했다. 오사카 전투 후 귀참을 이루었다. 고슈류 병학을 집대성하여 많은 문하생을 가르쳤다.", "도쿠가와 가신. 고슈류 병학자. 마사모리의 아들. 주군 히데타다의 시동이 되었으나 훗날 출분했다. 오사카 전투 후 귀참을 이루었다. 고슈류 병학을 집대성하여 많은 문하생을 가르쳤다."),
    StrdataFix(2, 934, "마쓰마에 가신. 아버지 대에 에조로 이주하여 마쓰마에 긴히로를 고쇼로서 섬겼다. 이후 마치부교가 되었다. 후쿠야마관의 화재에서 긴히로를 구출하였으나, 그때의 화상이 원인이 되어 사망하였다.", "마쓰마에 가신. 아버지 대에 에조로 이주하여 마쓰마에 긴히로를 시동으로서 섬겼다. 이후 마치부교가 되었다. 후쿠야마관의 화재에서 긴히로를 구출하였으나, 그때의 화상이 원인이 되어 사망하였다."),
    StrdataFix(2, 1440, "도쿠가와 가신. 주군 이에야스의 고쇼를 맡았다. 이에야스의 신뢰를 받아 히데타다의 사부역과 간토소부교 등을 역임했다. 그러나 훗날 이에야스의 노여움을 사 은거의 몸이 되었다.", "도쿠가와 가신. 주군 이에야스의 시동을 맡았다. 이에야스의 신뢰를 받아 히데타다의 사부역과 간토소부교 등을 역임했다. 그러나 훗날 이에야스의 노여움을 사 은거의 몸이 되었다."),
    StrdataFix(2, 1542, "오사키 가신. 니이다성주. 요시타카의 소성을 맡았다. 가중 굴지의 미소년으로, 같은 소성인 이바노 소하치로와 총애를 다투었고, 이것이 계기가 되어 오사키 가문의 내란이 일어났다.", "오사키 가신. 니이다성주. 요시타카의 시동을 맡았다. 가중 굴지의 미소년으로, 같은 시동인 이바노 소하치로와 총애를 다투었고, 이것이 계기가 되어 오사키 가문의 내란이 일어났다."),
    StrdataFix(2, 1879, "오코치 히사쓰나의 장남. 도쿠가와 이에미쓰를 섬겨 소성에서 노중까지 출세해 '지혜 이즈'라는 별명을 얻었다. 시마바라의 난에서는 총대장을 맡아 진압에 성공했다.", "오코치 히사쓰나의 장남. 도쿠가와 이에미쓰를 섬겨 시동에서 노중까지 출세해 '지혜 이즈'라는 별명을 얻었다. 시마바라의 난에서는 총대장을 맡아 진압에 성공했다."),
    StrdataFix(2, 2009, "시바타 가신. 주군 가쓰이에의 고쇼가시라로서 1만 석을 다스렸다. 시즈가타케 합전에서 시바타군이 무너져 달아났을 때 하시바군의 추격을 막으며 분전하였다. 가쓰이에를 에치젠으로 퇴각시킨 뒤 전사하였다.", "시바타 가신. 주군 가쓰이에의 시동장으로서 1만 석을 다스렸다. 시즈가타케 합전에서 시바타군이 무너져 달아났을 때 하시바군의 추격을 막으며 분전하였다. 가쓰이에를 에치젠으로 퇴각시킨 뒤 전사하였다."),
    StrdataFix(2, 2041, "오다 가신. 요시나리의 삼남. 주군 노부나가의 고쇼를 맡는다. 영리하고 용모가 아름다워 노부나가에게 총애받았다. 장래가 촉망되었으나 혼노지의 변에서 노부나가를 따라 분전하다 전사했다.", "오다 가신. 요시나리의 삼남. 주군 노부나가의 시동을 맡는다. 영리하고 용모가 아름다워 노부나가에게 총애받았다. 장래가 촉망되었으나 혼노지의 변에서 노부나가를 따라 분전하다 전사했다."),
    StrdataFix(3, 121, "가마쿠라 시대의 도공 도자부로 유키미쓰가 만든 단도, 오다 노부나가의 애도. 일설에는 고쇼 모리 란마루가 그 성실함을 칭찬받아 노부나가로부터 하사받았다고 한다.", "가마쿠라 시대의 도공 도자부로 유키미쓰가 만든 단도, 오다 노부나가의 애도. 일설에는 시동 모리 란마루가 그 성실함을 칭찬받아 노부나가로부터 하사받았다고 한다."),
)

CORE_LITERAL_FIXES = (
    LiteralFix("MSG/JP/msggame.bin", 13, 99, 1, "의 자질은\n당가에서도 일이를 다투는 재능이니\n주군의 패업을 지탱해 줄 것이옵니다", "의 자질은\n당가에서도 손꼽히는 재능이니\n주군의 패업을 지탱해 줄 것이옵니다"),
    LiteralFix("MSG_PK/JP/msggame.bin", 13, 99, 1, "의 자질은\n당가에서도 일이를 다투는 재능이니\n주군의 패업을 지탱해 줄 것이옵니다", "의 자질은\n당가에서도 손꼽히는 재능이니\n주군의 패업을 지탱해 줄 것이옵니다"),
    LiteralFix("MSG/JP/msggame.bin", 13, 143, 0, "당가는 아직 힘이 부족하오\n천하를 노리려면 영토를 넓혀 힘을 기르고\n전국의 다이묘에게 힘을 인정받아야 합니다", "당가는 아직 세력이 미약하오.\n천하를 노리려면 영토를 넓혀 국력을 기르고,\n전국의 다이묘에게 그 힘을 인정받아야 하오."),
    LiteralFix("MSG_PK/JP/msggame.bin", 13, 143, 0, "당가는 아직 힘이 부족하오\n천하를 노리려면 영토를 넓혀 힘을 기르고\n전국의 다이묘에게 힘을 인정받아야 합니다", "당가는 아직 세력이 미약하오.\n천하를 노리려면 영토를 넓혀 국력을 기르고,\n전국의 다이묘에게 그 힘을 인정받아야 하오."),
    LiteralFix("MSG/JP/msggame.bin", 17, 5, 3, "이(가) 앞질러 나섰다고…!?\n강화를、오토모를 무너뜨릴 셈인가…!", "이(가) 앞질러 나섰다고…!?\n강화를 깨고 오토모를 무너뜨릴 셈인가…!"),
    LiteralFix("MSG/JP/msggame.bin", 17, 26, 0, "복병이 있었다!혼란한 틈에 쳐부수자!", "복병이 있었다! 혼란한 틈에 쳐부수자!"),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 162, 1, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 211, 1, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 226, 0, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 582, 0, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 582, 1, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 613, 1, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 613, 2, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 925, 1, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 937, 0, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 946, 1, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 967, 1, "、", ", "),
    LiteralFix("MSG_PK/JP/msggame.bin", 17, 978, 0, "、", ", "),
    LiteralFix("MSG/JP/msggame.bin", 16, 42, 0, "자금을 너무 쌓아 두는 건 악수\n정책이야말로 난세의 요체", "금전을 지나치게 쌓아 두는 것은 악수.\n정책이야말로 난세의 요체다."),
    LiteralFix("MSG/JP/msggame.bin", 16, 45, 0, "군다이로는 역시…\n부하 배속만 있다면", "군다이로서는 역시…\n부하가 배속되기만 한다면"),
)

# Block 12 is deliberately absent: every reviewed row has a 01 43 generated
# ending.  Literal-only replacement would risk joining a Korean ending to
# opaque Japanese grammar at runtime.
LITERAL_FIXES = CORE_LITERAL_FIXES


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def require_under(root: Path, candidate: Path, label: str) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise QualityWaveError(f"{label} escapes its allowed root: {candidate}") from exc
    return candidate


def output_paths(output_root: Path) -> set[str]:
    return {path.relative_to(output_root).as_posix() for path in output_root.rglob("*") if path.is_file()}


def assert_profile_sha256(steam_root: Path, expected: dict[str, str], label: str) -> None:
    current = {relative: sha256_path(require_under(steam_root, steam_root / relative, "Steam source")) for relative in PROFILE_TARGETS}
    if current != expected:
        mismatches = {key: {"expected": expected[key], "actual": current[key]} for key in PROFILE_TARGETS if current[key] != expected[key]}
        raise QualityWaveError(f"Steam {label} differs from approved wave-1 state: {mismatches}")


def assert_baseline(steam_root: Path) -> None:
    assert_profile_sha256(steam_root, BASELINE_SHA256, "baseline")


def fixes_for_common(relative: str) -> tuple[CommonFix, ...]:
    return tuple(fix for fix in COMMON_FIXES if fix.relative == relative)


def fixes_for_msggame(relative: str) -> tuple[LiteralFix, ...]:
    return tuple(fix for fix in LITERAL_FIXES if fix.relative == relative)


def patch_common(source: bytes, fixes: Iterable[CommonFix]) -> bytes:
    fixes = tuple(fixes)
    if not fixes:
        return source
    header, raw = decompress_wrapper(source)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise QualityWaveError("common source table does not byte-round-trip")
    texts = list(table.texts)
    for fix in fixes:
        if fix.entry_id >= len(texts) or texts[fix.entry_id] != fix.before:
            actual = None if fix.entry_id >= len(texts) else texts[fix.entry_id]
            raise QualityWaveError(f"unexpected common preimage {fix.relative}#{fix.entry_id}: {actual!r}")
        texts[fix.entry_id] = fix.after
    rebuilt_raw = rebuild_message_table(table, texts)
    checked = parse_message_table(rebuilt_raw)
    if checked.texts != tuple(texts):
        raise QualityWaveError("common table parse verification failed")
    return recompress_wrapper(rebuilt_raw, header)


def patch_strdata(source: bytes) -> bytes:
    header, raw = decompress_wrapper(source)
    archive = parse_raw_strdata(raw)
    if rebuild_raw_strdata(archive) != raw:
        raise QualityWaveError("strdata source container does not byte-round-trip")
    replacements: dict[int, list[str]] = {}
    for fix in STRDATA_FIXES:
        texts = replacements.setdefault(fix.block_id, list(archive.blocks[fix.block_id].texts))
        if fix.entry_id >= len(texts) or texts[fix.entry_id] != fix.before:
            actual = None if fix.entry_id >= len(texts) else texts[fix.entry_id]
            raise QualityWaveError(f"unexpected strdata preimage {fix.block_id}:{fix.entry_id}: {actual!r}")
        texts[fix.entry_id] = fix.after
    rebuilt_raw = rebuild_raw_strdata(archive, replacements)
    checked = parse_raw_strdata(rebuilt_raw)
    for fix in STRDATA_FIXES:
        if checked.blocks[fix.block_id].texts[fix.entry_id] != fix.after:
            raise QualityWaveError(f"strdata output differs at {fix.block_id}:{fix.entry_id}")
    return recompress_wrapper(rebuilt_raw, header)


def record_at(source: bytes, block_id: int, record_id: int) -> MsgGameRecord:
    archive = parse_packed_msggame(source).archive
    try:
        return archive.blocks[block_id].records[record_id]
    except IndexError as exc:
        raise QualityWaveError(f"missing msggame record {block_id}:{record_id}") from exc


def patch_msggame(source: bytes, fixes: Iterable[LiteralFix]) -> bytes:
    fixes = tuple(fixes)
    if not fixes:
        return source
    parsed = parse_packed_msggame(source)
    grouped: dict[tuple[int, int], dict[int, str]] = {}
    for fix in fixes:
        record = parsed.archive.blocks[fix.block_id].records[fix.record_id]
        literals = parse_record_literals(record)
        if fix.literal_id >= len(literals) or literals[fix.literal_id].text != fix.before:
            actual = None if fix.literal_id >= len(literals) else literals[fix.literal_id].text
            raise QualityWaveError(f"unexpected msggame preimage {fix.relative}@{fix.coordinate}: {actual!r}")
        record_fixes = grouped.setdefault((fix.block_id, fix.record_id), {})
        if fix.literal_id in record_fixes:
            raise QualityWaveError(f"duplicate msggame literal fix {fix.relative}@{fix.coordinate}")
        record_fixes[fix.literal_id] = fix.after
    replacements = {
        coordinate: rebuild_record_literals(parsed.archive.blocks[coordinate[0]].records[coordinate[1]], values)
        for coordinate, values in grouped.items()
    }
    rebuilt = rebuild_packed_msggame(source, replacements)
    checked = parse_packed_msggame(rebuilt).archive
    for fix in fixes:
        literal = parse_record_literals(checked.blocks[fix.block_id].records[fix.record_id])[fix.literal_id]
        if literal.text != fix.after:
            raise QualityWaveError(f"msggame output differs at {fix.relative}@{fix.coordinate}")
    return rebuilt


def opaque_segments(record: MsgGameRecord) -> tuple[bytes, ...]:
    """Return every non-literal byte span, excluding only UTF-16 payloads."""
    cursor = 0
    spans: list[bytes] = []
    for literal in parse_record_literals(record):
        spans.append(record.data[cursor:literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


def patch_target(relative: str, source: bytes) -> bytes:
    if relative == "MSG/JP/strdata.bin":
        return patch_strdata(source)
    if relative in {"MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin"}:
        return patch_msggame(source, fixes_for_msggame(relative))
    return patch_common(source, fixes_for_common(relative))


def expected_changed_paths() -> set[str]:
    common = {fix.relative for fix in COMMON_FIXES}
    msggame = {fix.relative for fix in LITERAL_FIXES}
    return common | msggame | {"MSG/JP/strdata.bin"}


def verify_installed(steam_root: Path) -> dict[str, object]:
    """Verify the exact Steam target after this wave has been applied."""
    steam_root = steam_root.resolve(strict=True)
    assert_profile_sha256(steam_root, TARGET_SHA256, "installed target")
    for relative in {fix.relative for fix in COMMON_FIXES}:
        _, raw = decompress_wrapper((steam_root / relative).read_bytes())
        table = parse_message_table(raw)
        for fix in fixes_for_common(relative):
            if table.texts[fix.entry_id] != fix.after:
                raise QualityWaveError(f"installed common fix differs at {relative}#{fix.entry_id}")
    _, strdata_raw = decompress_wrapper((steam_root / "MSG/JP/strdata.bin").read_bytes())
    strdata = parse_raw_strdata(strdata_raw)
    for fix in STRDATA_FIXES:
        if strdata.blocks[fix.block_id].texts[fix.entry_id] != fix.after:
            raise QualityWaveError(f"installed strdata fix differs at {fix.block_id}:{fix.entry_id}")
    for relative in {fix.relative for fix in LITERAL_FIXES}:
        archive = parse_packed_msggame((steam_root / relative).read_bytes()).archive
        for fix in fixes_for_msggame(relative):
            literals = parse_record_literals(archive.blocks[fix.block_id].records[fix.record_id])
            if fix.literal_id >= len(literals) or literals[fix.literal_id].text != fix.after:
                raise QualityWaveError(f"installed msggame fix differs at {relative}@{fix.coordinate}")
    return {
        "schema": MANIFEST_SCHEMA,
        "status": "PASS",
        "installed_profile": "target",
        "changed_paths": sorted(expected_changed_paths()),
        "common_fix_count": len(COMMON_FIXES),
        "strdata_fix_count": len(STRDATA_FIXES),
        "msggame_literal_fix_count": len(LITERAL_FIXES),
    }


def verify_candidate(steam_root: Path, output_root: Path) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    output_root = output_root.resolve(strict=True)
    assert_baseline(steam_root)
    if output_paths(output_root) != set(PROFILE_TARGETS):
        raise QualityWaveError("candidate tree does not contain the exact eleven-file text profile")
    changed_expected = expected_changed_paths()
    changed: list[str] = []
    entries: list[dict[str, object]] = []
    for relative in PROFILE_TARGETS:
        source = require_under(steam_root, steam_root / relative, "Steam source").read_bytes()
        candidate = require_under(output_root, output_root / relative, "candidate").read_bytes()
        if relative in changed_expected:
            if candidate == source:
                raise QualityWaveError(f"candidate did not change expected resource: {relative}")
            changed.append(relative)
        elif candidate != source:
            raise QualityWaveError(f"candidate changed retain-only resource: {relative}")
        entries.append({"path": relative, "source_sha256": sha256_bytes(source), "candidate_sha256": sha256_bytes(candidate), "source_size": len(source), "candidate_size": len(candidate)})
    if set(changed) != changed_expected:
        raise QualityWaveError(f"unexpected changed resource set: {changed!r}")
    for relative in {fix.relative for fix in COMMON_FIXES}:
        _, raw = decompress_wrapper((output_root / relative).read_bytes())
        table = parse_message_table(raw)
        for fix in fixes_for_common(relative):
            if table.texts[fix.entry_id] != fix.after:
                raise QualityWaveError(f"candidate common fix differs at {relative}#{fix.entry_id}")
    _, strdata_raw = decompress_wrapper((output_root / "MSG/JP/strdata.bin").read_bytes())
    strdata = parse_raw_strdata(strdata_raw)
    for fix in STRDATA_FIXES:
        if strdata.blocks[fix.block_id].texts[fix.entry_id] != fix.after:
            raise QualityWaveError(f"candidate strdata fix differs at {fix.block_id}:{fix.entry_id}")
    for relative in {fix.relative for fix in LITERAL_FIXES}:
        source_archive = parse_packed_msggame((steam_root / relative).read_bytes()).archive
        parsed = parse_packed_msggame((output_root / relative).read_bytes()).archive
        relative_fixes = fixes_for_msggame(relative)
        grouped: dict[tuple[int, int], set[int]] = {}
        for item in relative_fixes:
            grouped.setdefault((item.block_id, item.record_id), set()).add(item.literal_id)
        if len(source_archive.blocks) != len(parsed.blocks):
            raise QualityWaveError(f"candidate msggame block count differs at {relative}")
        for before_block, after_block in zip(source_archive.blocks, parsed.blocks, strict=True):
            if len(before_block.records) != len(after_block.records):
                raise QualityWaveError(f"candidate msggame record count differs at {relative} block {before_block.block_id}")
            for before_record, after_record in zip(before_block.records, after_block.records, strict=True):
                coordinate = (before_record.block_id, before_record.record_id)
                if coordinate not in grouped and before_record.data != after_record.data:
                    raise QualityWaveError(f"candidate changed untouched msggame record at {relative}@{before_record.block_id}:{before_record.record_id}")
        for fix in relative_fixes:
            before_record = source_archive.blocks[fix.block_id].records[fix.record_id]
            after_record = parsed.blocks[fix.block_id].records[fix.record_id]
            before_literals = parse_record_literals(before_record)
            after_literals = parse_record_literals(after_record)
            if len(before_literals) != len(after_literals):
                raise QualityWaveError(f"candidate literal count differs at {relative}@{fix.block_id}:{fix.record_id}")
            if opaque_segments(before_record) != opaque_segments(after_record):
                raise QualityWaveError(f"candidate opaque bytes differ at {relative}@{fix.block_id}:{fix.record_id}")
            if after_literals[fix.literal_id].text != fix.after:
                raise QualityWaveError(f"candidate msggame fix differs at {relative}@{fix.coordinate}")
            selected = grouped[(fix.block_id, fix.record_id)]
            for literal_id, (before_literal, after_literal) in enumerate(zip(before_literals, after_literals, strict=True)):
                if literal_id not in selected and before_literal.text != after_literal.text:
                    raise QualityWaveError(f"candidate changed unlisted literal at {relative}@{fix.block_id}:{fix.record_id}:{literal_id}")
    return {"schema": MANIFEST_SCHEMA, "status": "PASS", "changed_paths": sorted(changed), "entries": entries, "common_fix_count": len(COMMON_FIXES), "strdata_fix_count": len(STRDATA_FIXES), "msggame_literal_fix_count": len(LITERAL_FIXES)}


def build(steam_root: Path, output_root: Path, manifest_path: Path) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    assert_baseline(steam_root)
    output_root = output_root.resolve()
    expected_root = DEFAULT_OUTPUT_ROOT.resolve()
    if output_root != expected_root:
        raise QualityWaveError(f"output root must be the dedicated build directory: {expected_root}")
    temporary_parent = output_root.parent
    temporary_parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="candidate-", dir=temporary_parent))
    try:
        for relative in PROFILE_TARGETS:
            source_path = require_under(steam_root, steam_root / relative, "Steam source")
            if not source_path.is_file():
                raise QualityWaveError(f"Steam source is absent: {source_path}")
            destination = temporary / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(patch_target(relative, source_path.read_bytes()))
        if output_root.exists():
            require_under(REPO / "tmp" / WORKSTREAM.name, output_root, "candidate output")
            shutil.rmtree(output_root)
        os.replace(temporary, output_root)
        report = verify_candidate(steam_root, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(canonical_json(report))
        return report
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true", help="verify the pre-apply baseline candidate")
    mode.add_argument("--verify-installed", action="store_true", help="verify the exact post-apply Steam target")
    args = parser.parse_args(argv)
    try:
        if args.verify_installed:
            report = verify_installed(args.steam_root)
        elif args.verify_only:
            report = verify_candidate(args.steam_root, args.output_root)
        else:
            report = build(args.steam_root, args.output_root, args.manifest)
    except (OSError, ValueError, QualityWaveError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
