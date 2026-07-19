#!/usr/bin/env python3
"""Build a private, static-only PC battle-dialogue quality candidate.

Wave 47 repairs only literal Korean quality defects in PK block 17: missing
spaces across styled literal boundaries, wrong particles, a few honorific /
meaning errors, and one source-confirmed castle-subject reversal.  Every row
is anchored to pristine Steam-PC Japanese.  The builder rejects any runtime
``02xx`` slot or ``0143`` command, preserves literal markers and opaque bytes
exactly, and can write only its private ``tmp`` candidate directory.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_PATH = STEAM_ROOT / RESOURCE
PC_JP_SOURCE = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / RESOURCE
)
W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-battle-dialogue-static-quality-wave47.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-battle-dialogue-static-quality-wave47-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-battle-dialogue-static-quality-wave47-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912

# This is the currently installed W45 static-safe Steam baseline.  The exact
# profile makes this candidate refuse a drifted game installation.
INPUT_PROFILE = {
    "size": 1_806_538,
    "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
}

# Filled from ``derive-pins`` before ``build`` or ``verify-private`` are
# allowed.  The deliberate two-step process prevents unpinned output from
# being mistaken for an installable candidate.
TARGET_PROFILE: dict[str, Any] = {
    "size": 1_806_594,
    "sha256": "C5BAD79A8CD261864E80238A1AA558594A1BA9451CA6253B92047C952E47459D",
    "raw_size": 1_799_512,
    "raw_sha256": "7F3C13F86CC7F038E52A05C5F75CE9B24790339FE074871B21ED85CFE31A1EB7",
}


class Wave47Error(RuntimeError):
    """Raised when a source, record contract, or private output differs."""


@dataclass(frozen=True)
class Change:
    coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    reason: str

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


# A pin supplies both current Steam and pristine-PC-Japanese anchors, plus
# deterministic output record identity and line layout.  It is intentionally
# not inferred at build time.
@dataclass(frozen=True)
class RecordPin:
    current_sha256: str
    current_size: int
    pc_jp_sha256: str
    target_sha256: str
    target_size: int
    target_line_widths_px: tuple[int, ...]


REVIEWED_CHANGES = (
    Change((17, 42), ("총대장 ", "오토모 요시시게", "를 격파하라!"), "직책과 총대장 이름 사이 공백"),
    Change((17, 43), ("총대장 ", "오토모 요시시게", "를 격파하라!", " 성공"), "직책과 총대장 이름 사이 공백"),
    Change((17, 44), ("총대장 ", "오토모 요시시게", "를 격파하라!", " 실패"), "직책과 총대장 이름 사이 공백"),
    Change((17, 53), ("오토모", "의 부대를 발견했나!\n전군 전진! ", "오토모", "의 목을 베어라!"), "문장 경계 공백"),
    Change((17, 108), ("면목이 없습니다\n수많은 ", "도쿠가와", " 가신이 대신 희생되어…"), "수식어·가문·가신 공백"),
    Change((17, 109), ("됐다, ", "도쿠가와", "군을 격파하는 데 성공했다\n이제는 ", "미카와 무사들", "의 충의를 칭찬할 뿐이다"), "문장 경계 공백"),
    Change((17, 118), ("쓰쓰이", "군은 ", "야마자키", " 앞에서 진군을 멈췄습니다\n", "아케치", "의 열세가 분명하다고 본 것이겠지요"), "군세·지명 경계 공백"),
    Change((17, 120), ("…이렇게 된 이상 어쩔 수 없다!\n기책에 ", "아케치 가문", "의 앞날을 걸겠다!"), "조사 앞 공백"),
    Change((17, 133), ("이제 산꼭대기로 예비 군기를 옮기겠다…\n준비가 끝날 때까지, ", "덴노잔", "을 적에게 넘기지 마라!"), "쉼표 뒤 공백"),
    Change((17, 165), ("강행군을 한 보람이 있어\n", "아케치", "와의 싸움은 ", "하시바 가문", "이 주도하게 됐습니다\n자, 역적을 토벌한 공을 차지하러 갑시다"), "가문 주어 경계 공백"),
    Change((17, 168), ("모반을 일으킨 ", "아케치", "군은 지면 끝이다…\n죽기를 각오하고 정면 돌파를 노리겠지"), "수식어와 군세 공백"),
    Change((17, 169), ("이곳에서는,", "덴노잔", "과 ", "숲가의 요충지", "를 제압해\n양쪽 측면에서 적진을 공격해야 할 듯합니다"), "접속 조사와 지명 경계"),
    Change((17, 182), ("무사히 ", "덴노잔", "을 제압했군!\n이대로 나머지 요충지도 빼앗자!"), "부사와 지명 공백"),
    Change((17, 196), ("아군 진지의 ", "요충지", "를 지켜라"), "소유격과 명사 공백"),
    Change((17, 197), ("아군 진지의 ", "요충지", "를 지켜라", " 성공"), "소유격과 명사 공백"),
    Change((17, 198), ("아군 진지의 ", "요충지", "를 지켜라!", " 실패"), "소유격과 명사 공백"),
    Change((17, 216), ("생각대로, ", "이시다", " 일파를\n", "세키가하라", "로 끌어내는 데 성공했다\n이제 단숨에 놈들을 도륙할 뿐이다"), "가문·일파 경계 공백"),
    Change((17, 217), ("역시 ", "이시다", " 측은 맞서 나왔군\n고사에 따라 결전지는", "세키가하라", "인가"), "중복 부사 제거와 측 표기"),
    Change((17, 218), ("이시다", " 일당은 산들을 이용해\n우리를 에워싸듯 진을 치고 있습니다"), "집단 명사 경계 공백"),
    Change((17, 221), ("우리의 배후를 잡아야 할 ", "모리", "군…\n그들과는 불전의 약정을 맺어 두었다"), "관형절과 군세 공백"),
    Change((17, 233), ("도쿠가와", " 측의 기세가 이 정도일 줄이야…!"), "측 표기 공백"),
    Change((17, 244), ("주군께서 ", "서군", "에 원군으로 오셨다고!\n어쩔 수 없군, 진군한다!"), "주어와 군세 공백"),
    Change((17, 245), ("주군께서 오시자 ", "히로이에", "도 움직였나! 우리도 움직인다!"), "부사절과 이름 공백"),
    Change((17, 248), ("주군! ", "히데요리", "님께서 찾아오셨습니다!"), "호격 뒤 공백"),
    Change((17, 255), ("이번 싸움은, ", "도쿠가와", "의 승리로 결판났군…\n아니, 아직 모르는가…?"), "쉼표 뒤 공백"),
    Change((17, 259), ("군사님께서 말씀하셨다!\n기합을 넣어 ", "요충지", "를 탈환하자!"), "어절 경계 공백"),
    Change((17, 292), ("요시히로", "님을 무사히 모시는 것이다\n기합을 넣어라!"), "殿을 주군으로 오역한 호칭 교정"),
    Change((17, 328), ("요시쓰구", "님을 위해 목숨을 버리는 것이 아깝지 않았다…"), "殿을 주군으로 오역한 호칭 교정"),
    Change((17, 348), ("이에야스", " 녀석… 도요토미의 세상은 앞으로도 이어진다!\n도쿠가와의 세상 따위 평생 오지 못하게 하겠다!"), "이름과 호칭 공백"),
    Change((17, 357), ("나이후", "님… 아니, 역적 ", "이에야스", "를 이곳에서 쓰러뜨리겠다!\n반드시 승리해, ", "도요토미 가문", "의 천하를 지켜 내겠다!"), "역적 호칭·쉼표 경계 공백"),
    Change((17, 362), ("놈이 ", "도쿠가와", " 측과도 내통하고 있다는 것은\n의심할 여지가 없다"), "주어·측 표기 공백"),
    Change((17, 366), ("우세를 유지하며 적군을 계속 압도하라고?\n그런, ", "태합", "전하의 싸움과 같은 일을…"), "쉼표 뒤 공백"),
    Change((17, 368), ("배신에 대한 대비는 내 부대가 맡겠다\n… ", "도쿠가와", " 측이 움직인다, 그대는 앞을 보아라"), "말줄임표·측 표기 공백"),
    Change((17, 378), ("오타니", " 부대와 ", "오사카", "의 원군은 제때 오지 못했군\n그래도 우리가 우세하기는 하지만…"), "부대·지명 경계 공백"),
    Change((17, 393), ("이 ", "시마즈", "에게 말에서도 내리지 않고 명령하다니…?\n가신의 가신 주제에 무례하구나!"), "この島津의 지시어 공백"),
    Change((17, 398), ("나를 비롯해,", "모리 가문", " 중신은 모두\n", "도쿠가와", "와 불전의 약정을 맺었기 때문입니다"), "가문과 중신 공백"),
    Change((17, 402), ("좋아, 늦지 않았군!\n", "모리", " 본군을 데려왔다, ", "지부", "！"), "본군·호칭 경계 공백"),
    Change((17, 403), ("나도 각오를 굳혔다!\n", "모리", " 가문이 너희를 이기게 해 주겠다!"), "가문 명사 공백"),
    Change((17, 405), ("주, 주군께서 직접 참전하신다고!?\n이래서는 ", "나이후", "님과 맺은 약정이…!"), "접속어와 이름 공백"),
    Change((17, 406), ("모리", " 종가가 참전하는 것이다!\n약정이 무슨 소용이냐! 어서 산을 내려가라!"), "종가 명사 공백"),
    Change((17, 435), ("이번 싸움은 ", "미쓰나리", "님에게 승산이 있다고 보았다!\n내 적은 ", "이에야스", "이다, 진군을 시작한다!"), "이름 앞 어절 공백"),
    Change((17, 436), ("고바야카와", "가 드디어 움직였나!\n우리도 ", "이에야스", "를 향해 진군한다!"), "우리도와 이름 공백"),
    Change((17, 437), ("설마 이번 싸움에서 ", "미쓰나리", "가 이기는가!?\n이대로는 ", "모리", " 가문이… 서둘러 진군한다!"), "이름·가문 경계 공백"),
    Change((17, 444), ("전황이 ", "동군", " 쪽으로 기울기 시작했나…\n우리의 적은 ", "미쓰나리", "이다! 진군하라!"), "측·이름 경계 공백"),
    Change((17, 446), ("고바야카와", " 녀석, ", "동군", "의 편에 서다니…\n우리 힘만으로 ", "이에야스", "를 쓰러뜨릴 수밖에 없다…"), "호칭·군세·이름 경계 공백"),
    Change((17, 457), ("모두, 승전 함성을 올려라!\n이제 ", "도요토미 가문", "의 천하는 지켜질 것이다!"), "부사와 가문 공백"),
    Change((17, 462), ("이에야스", "의 부대를 발견했나!\n전군 전진! ", "이에야스", "의 목을 베어라!"), "문장 경계 공백"),
    Change((17, 526), ("앞선 보고대로군\n적은 날이 개기를 기다려 ", "나루미", "로 진군할 생각인 듯합니다"), "동사와 지명 공백"),
    Change((17, 558), ("으… 여기서 쓰러지면…\n", "이마가와", " 가문이…　", "우지", "…", "자네", "…！"), "가문 명사 공백"),
    Change((17, 576), ("도요토미", " 가문을 지키기 위해…\n여러분, 부디 힘을 빌려주시오!"), "가문 명사 공백"),
    Change((17, 617), ("남쪽의 3개 부대", "를 격파하고 ", "사나다마루", "를 지켜라"), "연결 어미와 시설명 공백"),
    Change((17, 618), ("남쪽의 3개 부대", "를 격파하고 ", "사나다마루", "를 지켜라", " 성공"), "연결 어미와 시설명 공백"),
    Change((17, 619), ("남쪽의 3개 부대", "를 격파하고 ", "사나다마루", "를 지켜라", " 실패"), "연결 어미와 시설명 공백"),
    Change((17, 623), ("역시 ", "오사카성", "은 남쪽이 약했군!\n이대로 계속 공격하라!"), "부사와 성 이름 공백"),
    Change((17, 643), ("이런 곳까지 ", "도쿠가와", "군이…!?\n이제 항복할 수밖에 없겠군…"), "지시어와 군세 공백"),
    Change((17, 680), ("주군, 큰일입니다!\n적의 ", "사나다", " 부대와 ", "오타니", " 부대가 보이지 않습니다"), "적군·부대 경계 공백"),
    Change((17, 691), ("좋아, ", "덴노지", "를 확보했군\n이제 적은 뜻대로 움직이지 못하겠지"), "쉼표 뒤 공백"),
    Change((17, 710), ("주군, 아무래도 ", "도요토미", " 측이 무너지기 시작한 듯합니다\n저희는 어찌할까요?"), "부사와 측 표기 공백"),
    Change((17, 939), ("적의 ", "퇴각 지점", "을 빼앗았다!\n이제 주군을 구할 수 있겠군!"), "소유격과 명사 공백"),
    Change((17, 943), ("이것으로 ", "북부 시나노", "를 장악했다고 할 수 있겠군.\n하지만 이토록 큰 희생을 치르다니……"), "지시어와 지역명 공백"),
    Change((17, 1035), ("우리의 존망이 이 싸움에 달렸다!\n", "호조", " 정예병들이여, 돌격하라!!"), "가문과 정예병 공백"),
    Change((17, 1047), ("잘했다, ", "호조", " 장병들이여!\n이대로 끝까지 성을 지켜라!"), "쉼표·가문·장병 공백"),
    Change((17, 1064), ("가와고에성", "이…\n이번 싸움은 우리가 졌군……"), "河越城が를 성에 패했다로 오역한 의미 교정"),
    Change((17, 1125), ("주군, 이대로는 승산이 없습니다!\n일단 ", "가이", "까지 물러나시지요."), "부사와 지역명 공백"),
    Change((17, 1150), ("저 ", "다케다", "군이 이토록 간단히…\n이것이 철포의 힘인가"), "지시어와 군세 공백"),
)

# These records are genuine quality fixes, but their target line is already
# wider than the conservative 912px dialogue bound (many source lines are
# wider as well).  Do not treat that as permission to write them: they stay in
# the review list for UI-specific reflow / real-game QA, outside this static
# bundle.
DISPLAY_QA_HOLDS = {
    (17, 43), (17, 44), (17, 109), (17, 118), (17, 133), (17, 165),
    (17, 169), (17, 233), (17, 245), (17, 255), (17, 328), (17, 348),
    (17, 357), (17, 362), (17, 366), (17, 368), (17, 378), (17, 393),
    (17, 398), (17, 406), (17, 435), (17, 437), (17, 446), (17, 457),
    (17, 526), (17, 617), (17, 618), (17, 619), (17, 680), (17, 710),
    (17, 943),
}
CHANGES = tuple(change for change in REVIEWED_CHANGES if change.coordinate not in DISPLAY_QA_HOLDS)

# Derived once from the exact W45 Steam baseline, then reviewed and pinned.
RECORD_PINS: Mapping[tuple[int, int], RecordPin] = {
    (17, 42): RecordPin("319645E4EB91D8ECF95BCCCD4B98FF66D5F38767AE68AA909C03ECA61003FBBB", 69, "67426AD3DA2CEF18800113B7E29EEBE50D3AB725D479F0944A75289C465B63A7", "6AC58711C85DF1CC7704A35DFB56DCA992CC37F2A0200E0C195B750631BE239E", 71, (816,)),
    (17, 53): RecordPin("B64F9D3F488E7123FD90C02272E217969287C6D58DD831AD518EFBF025AD12B0", 105, "979DDC2DFE503F9ABDBA4B462A3CD296413DC44A838D9BA52B0C18D2A6EA7828", "11165297139C4FDB9B4B1EC37335DC7A2A4E640AA2EDAAD57DC00C845655CB16", 107, (600, 768)),
    (17, 108): RecordPin("A4A8AC75FAE2DB105F903BC34E1DCF5B9968CE3228B8B194AB2A569791BD61B2", 83, "AFEDA5575DA9A85E00B51AC022AD4617105CDC1329A6A80703D61A73F2701D5F", "832132871592F57AB2B2CDCE3156DF61795F83C0875592240FD5FA959F44177F", 87, (360, 912)),
    (17, 120): RecordPin("14362D010FD2614E6E5AC925F2FE207D75860F9395AB365D603F0E2D4C1CA26D", 103, "54BF8F94463572826AD568141E1E3DDD81CA55ED3D8881F6BDE57FB02D08FCF2", "5E37B0D7A74325428D57275241ABF47CD044DEEC07138CA4187EB84E312DF49D", 105, (720, 840)),
    (17, 168): RecordPin("F62A217FC414986687FA95EAAAAF4FA694293CCC32B91242ABE6E6D18D932CA0", 109, "8B28884DC8CE3F09EC990ED854EC99B7DE1FA1B81C40641F41CE743F39A1566E", "5E9C4CE56231533E3DF75E51D3816AD978863A4E0732EC8647322AC2E529D44F", 111, (912, 864)),
    (17, 182): RecordPin("1CEBF45A60F2A329EA3FA9C4748F13ECC96D4ABC7A487D72F6CD0CA3C35B5F86", 89, "1E8BE9F2007A38CAF6A47E1FAC4338295D1F85887649726F8FEE21BF50B1C17A", "39CA34D6B1B6CF35917783AF5D451856ADA003A70C5E402C9C263B8C00386D2D", 91, (600, 720)),
    (17, 196): RecordPin("E855F64CF60971F2AD513D8175EC6EEC6374C4117731472F2C4B8A55A21DD43E", 55, "7D73B3C05B7C83191553E88B16ACDF12B48E0465618B0EE4DFD7B49508A199FE", "4A3361C9DC75C6B75C34C8E3458B79BB954135C613DED9A1DF21B2C7D153F6E9", 57, (648,)),
    (17, 197): RecordPin("7A4C960031384E57BDEC51542276B2F34A9BA3D09D7B5BE18FD28BDF4A9EF336", 73, "17FAFB0669A707DD70B14B534C77F368191D6C13EFBF80CA7BC850EBBEBE1BE1", "7FC3255E4583EFFEDBBAE454D735E67A3877134FBD1D36198C48B296526C1B8C", 75, (768,)),
    (17, 198): RecordPin("C0B303FE81DC53619CCFCEFBBAF02B3162EBC8C15CFE6862EA4A723995166679", 75, "1BAA5C23AF496CF92F783D85703B39768CEDC15E4FEC943E8543D85B2106C5C9", "A30E45A389028A3E1762EB8304693219BD14E90E50D807CEC2D34300DDF9194F", 77, (792,)),
    (17, 216): RecordPin("F4875D3B1EBA7D79D2A3C32FECB3FCF174F3BF52968FB522EB5015D660CAFA14", 143, "79CFA2D140AD186DBC6F59BC3F754648B7F0728BDA8E718E804C96932BF3984B", "36D8966A999BC56AABE0FC390F1B7611956C6D19E637104DE9E16778308780BA", 147, (552, 792, 768)),
    (17, 217): RecordPin("FE85A77971D3AA1DF838C2EB2BAACB3597C00273D56F7DB34602AD9A7794DDC5", 117, "7B9D6B6DF7E28C131F0EF1559EDA5B6E89313DBF4FEAC5E7E11261E4B18FF146", "278A80A6C041BF562A26E6C1559EF1BCFB9A656E4C4967761F858F38FB7EC9BB", 115, (672, 816)),
    (17, 218): RecordPin("2461F550812091719D211A051C9FCDB7C7FADC7CACE0D1EBB46213970878F8DD", 89, "BE3F2F811C01D865C50F592C79F300B1AB9A85EE8207928FB37DB5BC3842CCCC", "6A53BA645712EC3A71AB8134B7CCE95973C43A5A23B46655A8A6D8EB7636E5A2", 91, (648, 816)),
    (17, 221): RecordPin("45832AE20CFA53CA604D8B10A63B214FBD02CE8B5C636A8999E31B958812CE9D", 101, "84D21B0F0128FB9E52F7ADDCF268E6EE5310F0E344227FD5814DEE643473308C", "AC9BD94B97858CBA839138DEEE19AFF1F7049204960DBDBD54E90AFAF9A4562F", 103, (768, 816)),
    (17, 244): RecordPin("D8D98C374AF7C415282903340674FA4A7D362889BAC431117735ED015C9ED3ED", 93, "6D05DDF71E56520C0191D0D84F5DA8341D6E52F16090E9FB7392EA1C068CBB9C", "FAC4955BFAC4EE83D7AB52343FDDFDEEDC259C0766117294C01810C151E35EB3", 95, (816, 552)),
    (17, 248): RecordPin("C0B89DD5F3A1E88354A5D28981F89361B64B63C67B3045970D236F217CF167EA", 65, "E41DC232FD7F89375BE4E66138422916CED08F1313D58063AF4504A5072BCC93", "6BF435BB9C236C0283C5D107654D3064016A2EC3C0A7DA87166E003941CEFCA6", 67, (864,)),
    (17, 259): RecordPin("20EDDF8FAEF5E237011760AC4C11A6731A22D26F4AFAA5EE6B4FFD20251C6C39", 85, "D21E135D186884F00B6C9FA7340DE15683D6CFF970D128F4DDBC39FE3DEF650B", "280E486476B49024FDE1CB78061D2AF45E7668D920FA86D8F6C0C4C19DB6AF3F", 87, (528, 720)),
    (17, 292): RecordPin("01C61CF1739E8F1CE5C1B4491BB98A8E9709CD118C62E1A487159044E4071BC6", 77, "5ED6D5ABA4DB7713F341447F961C921FCE2C987BABC477956674E9A5A1290DD4", "979FABE936159AE3ECEF01AD4C8E598631C125BC25EACA02DBC2D665970CC226", 75, (792, 336)),
    (17, 402): RecordPin("DC742ADE8C1B715F0EB185098EBEC713A23EE2E4C3F3E74D4803B26A8CD1CF5A", 97, "973C966998F98BF41B5D66F6A6F736195ED3328DD8B37FC4E2F8AB5D1F3544A3", "3C1E7ED26BA1E7D42F868683C4DB2C65447ED3EBADB800DD8A22EF814B3BAC1B", 101, (432, 672)),
    (17, 403): RecordPin("5749456D951C6E0CDBB77B323B8B5539825A33D49ED35FB2AC418CE274813B9F", 91, "8ECB02C9854406CEF4ACD7C1383A909B53D7E4BB094FDB6A05112C9B76144D1A", "05BA436F00909D26DA4A16FF2C14F66E9E64EEEBE1AFCE47464D127EB13B9267", 93, (456, 864)),
    (17, 405): RecordPin("80B1AD677D0C252FC6F9F0CE98E5598231BF6422ECB544630B9045F8479F3EB1", 103, "F12AABA560E62E50CEA04071FD46A42E2D556AEDB613C5FB52A0A9B92888EAB8", "471EE7E22D7D3FA597689673B552438354652089CDD8F70C2AA85BFEAB441EA8", 105, (768, 816)),
    (17, 436): RecordPin("3C4AB6EA22DE0EAA8A61484909CFB038917F7E1CE4081BA203D664C17C7B1250", 107, "9C5016DE645E1EBCEF9C396B19D6CBEB474E7663B3A9B83BBEA5E6E5A953286D", "BF63C32902153AC98464D7D515444136CB01659E1BD3022157BBC1D68931CB0F", 109, (696, 768)),
    (17, 444): RecordPin("7D9C32E62C872B3D19CF3B97D71DA1ACFDA52A25B68723A52CE29917FB34B307", 121, "6D3D16853312D1C5FB4F5D2398012BD661DCEF320CEA51E995D63433B3CFAFDC", "727C0D8CB8B251A34E046BCF45A63109F033104AD06B106D8F389372A3D2E058", 127, (864, 840)),
    (17, 462): RecordPin("725F97C984E32E693B65642E67F81166FB7D72F0CF172414F22ED3513D6482EE", 109, "A68F0E703787EC45FCAC1AB5CB527F3B76A99BAFB034142F10301581227C8471", "E0C2148BC6A84C36DF22A56A9EE8E357107B6B06C37A790A74C90F2631B36F07", 111, (648, 816)),
    (17, 558): RecordPin("E0C42C6F24593A05DF548931155B2598C4F66561471F6303350A83E20BA33D59", 121, "59B6F11C63BBBF5E64A9472C06FE8C94A0357C9E21E174C4D3D5BF31425CD8F1", "CAA30AC9D26C4DDE247055930715D0CE54A9F0F3EB8C599B70D77B040070FC1B", 123, (528, 792)),
    (17, 576): RecordPin("536B11A945BC2954AF6708744EDCD6AB94765445DB5D157783A84A1DD1BF9603", 87, "13072874CBF4535EE21BA38A978D10BFEDF670E55769B655B26C2EC88E421007", "6C59C13FA480ABF4A250A8B0A008A5C73E0DB4BBB1758F37C624A9D94650DC00", 89, (696, 696)),
    (17, 623): RecordPin("671CC52C8BBC260DFD2C79C896C6B9CB1073E4C3CCDB2C680ABC3CA60F4D73BB", 85, "402A2B429986EAF0A1791DB855BA80076CE51942E5918B0D5F3EE7B809095013", "D2AE4240D901E6AD3B394789C19F3D48FB77FD589EEB74252D60DA5FE2B3763E", 87, (720, 504)),
    (17, 643): RecordPin("65BDFBC6229AACCB326693EB18ABD444789570B14919742E2FD0FBD028591508", 89, "6D05EAE240833D6FA26E4B1E75912CFD8A209A3602F9B572A20E9E1E0632C46B", "881F11AF37B000A9A19B080143810D1714867A62A2070F0A1112389B82CB874D", 91, (672, 648)),
    (17, 691): RecordPin("317B3E89870245567266364959E355D1C97B1E9FF3E459F69A40EE47D4F98A42", 91, "1D15E36011DF8C731F566AB3FE57CE1E4A6B8F6529B4B979D89FCEE578658D8E", "6FB5C928BE9F9C88C8B16AFE210868460E2DE2E467B5ACD99B7E02959D4CF5CE", 93, (552, 816)),
    (17, 939): RecordPin("54F3E4CF2E243A13F14EE50E083488BD6CBC252954805AC8C65F9BE1446A9ABE", 89, "414BB5B6FDF9FC1EDFB3DECCD188329E7B7E59D432645C824D145AC6B9B59D4C", "D531314D3FFB5F5639DFBAC9E4087B11A34E7C7E6FE5150B5BB06183AE29CD69", 91, (624, 648)),
    (17, 1035): RecordPin("68E428693658A2405DF83A66F1FAB80645940196774091A96A5D5E5CBF1C3622", 97, "16D33738457ED25A29CEE3AED5C0A02D2CDA3AC16645456278A2A6931713A315", "BF97996616EE6D0A5F86E77DAD1208D3E54E19C63904E76F18A27245E7D0105D", 99, (744, 696)),
    (17, 1047): RecordPin("F859A791BDB3CF3108A5D1101F142FC76D2E0C00C0741D267BCA21B61C6F0E40", 83, "102EE94EE0F49707D436766F876A3E09FA73F764171EE02335F555C8DF68289A", "993737AA2CC61C170FD9F5562D17D674D4402063041E608354C532A92FAE7B9E", 87, (576, 624)),
    (17, 1064): RecordPin("DF83A2F6C210DDF0A488E5B0BE1C5BEB97A7C5D5C18C30A6AC26A2E365409B02", 79, "29700BA9BB04072FDA50735321585CAF25BDCEB197641A0CEE3F9EB7A6063161", "E03E2B38F17A331A6064848F25BB09BCBE998D5BF28C107BD4B02CAC879D2A84", 67, (336, 648)),
    (17, 1125): RecordPin("277A8FA192B1D80F0358991C0425487F9031423B4E0E17C74F9096F0581E4852", 93, "8A30FC433E7ABD34744518F5BA5866222AE7732CFDE0462C99D744B2FBA2EA63", "C238BDCA299051FFB88FBE0D31D57AE2E881BA58C6A324AB9D53FC10346C5F98", 95, (744, 648)),
    (17, 1150): RecordPin("EBD20EC908ED53D7025B52EF36C821709E717323F7B3EF65C16F7AEFF39661F9", 81, "631D25B7617C4900251CA6C2DC7E2104CE4BE0AF7848647EE3665B7B0189EBAB", "58B0B544BE6BB66DD99A3003590B231EF0A17CC3E0D94DFE598B20E4D2F542AE", 83, (696, 480)),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave47Error(message)


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
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave47Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave47Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 format helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 format helper differs")
    spec = importlib.util.spec_from_file_location("wave47_pinned_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave47Error("cannot load Wave 27 format helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def records_by_coordinate(packed: bytes) -> Mapping[tuple[int, int], Any]:
    return W27.records_by_coordinate(packed)


def opaque_hexes(record: Any) -> tuple[str, ...]:
    return tuple(span.hex().upper() for span in W27.opaque_spans(record))


def runtime_opcodes(record: Any) -> tuple[str, ...]:
    values: list[str] = []
    for span in W27.opaque_spans(record):
        for index, value in enumerate(span[:-1]):
            if value == 0x02:
                values.append(span[index : index + 2].hex().upper())
    return tuple(values)


def validate_target_literal(value: str, label: str) -> None:
    require(value != "", f"empty target literal: {label}")
    encoded = value.encode("utf-16le")
    require(W27.LITERAL_START not in encoded and W27.LITERAL_END not in encoded, f"reserved marker in target: {label}")
    require(all(ord(char) >= 0x20 or char in "\n\r" for char in value), f"control character in target: {label}")


def load_inputs() -> tuple[bytes, Mapping[tuple[int, int], Any], Mapping[tuple[int, int], Any]]:
    path = reject_switch(RESOURCE_PATH, "current Steam PC PK dialogue")
    source_path = reject_switch(PC_JP_SOURCE, "pristine Steam PC Japanese dialogue")
    packed = path.read_bytes()
    require(len(packed) == INPUT_PROFILE["size"] and sha256_bytes(packed) == INPUT_PROFILE["sha256"], "current Steam PK dialogue profile differs")
    W27.validate_raw_roundtrip(packed, "Wave 47 current Steam PK dialogue")
    source = source_path.read_bytes()
    W27.validate_raw_roundtrip(source, "Wave 47 pristine Steam PC Japanese dialogue")
    return packed, records_by_coordinate(packed), records_by_coordinate(source)


def validate_change(change: Change, before: Any, pc_jp: Any, advance: Any, *, enforce_pins: bool) -> tuple[bytes, dict[str, Any]]:
    require(change.coordinate == (before.block_id, before.record_id), f"current coordinate differs: {change.coordinate_text}")
    require(change.coordinate == (pc_jp.block_id, pc_jp.record_id), f"PC Japanese coordinate differs: {change.coordinate_text}")
    current_literals = W27.literal_texts(before)
    require(len(current_literals) == len(change.target_literals), f"literal slot count differs: {change.coordinate_text}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"terminator differs: {change.coordinate_text}")
    require(not runtime_opcodes(before), f"runtime 02xx token forbidden: {change.coordinate_text}")
    require(not W27.complete_0143_commands(W27.opaque_spans(before)), f"0143 command forbidden: {change.coordinate_text}")
    require("".join(current_literals).count("\n") == "".join(change.target_literals).count("\n"), f"manual LF count differs: {change.coordinate_text}")
    for target in change.target_literals:
        validate_target_literal(target, change.coordinate_text)

    layout = W27.line_layout(change.target_literals, advance)
    require(layout["line_count"] <= MAX_LINES, f"more than {MAX_LINES} lines: {change.coordinate_text}")
    require(layout["max_width_px"] <= MAX_LINE_PX, f"line width exceeds {MAX_LINE_PX}px: {change.coordinate_text}")
    require(not layout["wide_fallback_codepoints"], f"fallback glyph in target: {change.coordinate_text}")

    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == change.target_literals, f"target literal differs: {change.coordinate_text}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"marker topology differs: {change.coordinate_text}")
    require(W27.opaque_spans(after) == W27.opaque_spans(before), f"opaque bytes differ: {change.coordinate_text}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {change.coordinate_text}")

    if enforce_pins:
        pin = RECORD_PINS.get(change.coordinate)
        require(pin is not None, f"record pin is absent: {change.coordinate_text}")
        require(sha256_bytes(before.data) == pin.current_sha256 and len(before.data) == pin.current_size, f"current record pin differs: {change.coordinate_text}")
        require(sha256_bytes(pc_jp.data) == pin.pc_jp_sha256, f"PC Japanese source pin differs: {change.coordinate_text}")
        require(sha256_bytes(after.data) == pin.target_sha256 and len(after.data) == pin.target_size, f"target record pin differs: {change.coordinate_text}")
        require(tuple(layout["line_widths_px"]) == pin.target_line_widths_px, f"line-width pin differs: {change.coordinate_text}")

    return rebuilt, {
        "coordinate": change.coordinate_text,
        "reason": change.reason,
        "current_record_sha256": sha256_bytes(before.data),
        "current_record_size": len(before.data),
        "pc_jp_record_sha256": sha256_bytes(pc_jp.data),
        "target_record_sha256": sha256_bytes(after.data),
        "target_record_size": len(after.data),
        "literal_slot_count": len(change.target_literals),
        "input_manual_lf_count": "".join(current_literals).count("\n"),
        "target_manual_lf_count": "".join(change.target_literals).count("\n"),
        "input_opaque_spans_hex": list(opaque_hexes(before)),
        "target_opaque_spans_hex": list(opaque_hexes(after)),
        "runtime_02xx_opcodes": list(runtime_opcodes(before)),
        "target_line_widths_px": list(layout["line_widths_px"]),
        "target_max_line_px": layout["max_width_px"],
        "target_literals": list(change.target_literals),
    }


def build_unpinned() -> tuple[bytes, bytes, list[dict[str, Any]], Mapping[tuple[int, int], Any]]:
    packed, current, pc_jp = load_inputs()
    advance, _font = W27.load_font_advance()
    replacements: dict[tuple[int, int], bytes] = {}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current.get(change.coordinate)
        source = pc_jp.get(change.coordinate)
        require(before is not None and source is not None, f"record absent: {change.coordinate_text}")
        require(change.coordinate not in replacements, f"duplicate coordinate: {change.coordinate_text}")
        replacement, row = validate_change(change, before, source, advance, enforce_pins=False)
        replacements[change.coordinate] = replacement
        rows.append(row)
    candidate = W27.rebuild_packed_msggame(packed, replacements)
    W27.validate_raw_roundtrip(candidate, "Wave 47 private candidate")
    _header, raw = W27.decompress_wrapper(candidate)
    after = records_by_coordinate(candidate)
    changed = {coordinate for coordinate, record in current.items() if record.data != after[coordinate].data}
    expected = {change.coordinate for change in CHANGES}
    require(changed == expected and set(current) == set(after), "changed record scope differs")
    return candidate, raw, rows, current


def derive_pins() -> dict[str, Any]:
    packed, raw, rows, _current = build_unpinned()
    return {
        "target_profile": {
            "size": len(packed),
            "sha256": sha256_bytes(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256_bytes(raw),
        },
        "record_pins": {
            row["coordinate"]: {
                "current_sha256": row["current_record_sha256"],
                "current_size": row["current_record_size"],
                "pc_jp_sha256": row["pc_jp_record_sha256"],
                "target_sha256": row["target_record_sha256"],
                "target_size": row["target_record_size"],
                "target_line_widths_px": row["target_line_widths_px"],
            }
            for row in rows
        },
    }


def require_pins() -> None:
    require(len(RECORD_PINS) == len(CHANGES), "record pins are incomplete")
    require(set(RECORD_PINS) == {change.coordinate for change in CHANGES}, "record pin coordinates differ")
    require({"size", "sha256", "raw_size", "raw_sha256"} <= set(TARGET_PROFILE), "target profile pin is absent")


def prepare_candidate() -> tuple[bytes, bytes, dict[str, Any], dict[str, Any]]:
    require_pins()
    packed, raw, _rows_unpinned, current = build_unpinned()
    profile = TARGET_PROFILE
    require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], "target packed profile differs")
    require(len(raw) == profile["raw_size"] and sha256_bytes(raw) == profile["raw_sha256"], "target raw profile differs")

    source_packed = reject_switch(PC_JP_SOURCE, "pristine Steam PC Japanese dialogue").read_bytes()
    pc_jp = records_by_coordinate(source_packed)
    advance, font = W27.load_font_advance()
    after = records_by_coordinate(packed)
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current[change.coordinate]
        replacement, row = validate_change(change, before, pc_jp[change.coordinate], advance, enforce_pins=True)
        require(after[change.coordinate].data == replacement, f"rebuilt record differs: {change.coordinate_text}")
        rows.append(row)

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pc_jp_primary": True,
            "pc_en_sc_tc_context_read": True,
            "switch_korean_read": False,
            "runtime_02xx_records": "forbidden",
            "0143_command_records": "forbidden",
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "pinned_format_helper_sha256": W27_HELPER_SHA256,
        "input": INPUT_PROFILE,
        "target": TARGET_PROFILE,
        "font": font,
        "max_lines": MAX_LINES,
        "max_line_px": MAX_LINE_PX,
        "changed_record_count": len(CHANGES),
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": RESOURCE,
        "input": INPUT_PROFILE,
        "output": TARGET_PROFILE,
        "changed_coordinates": [change.coordinate_text for change in CHANGES],
        "changed_record_count": len(CHANGES),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
        "audit_sha256": sha256_bytes(canonical_json(audit)),
    }
    return packed, raw, audit, manifest


def write_candidate(bundle: tuple[bytes, bytes, dict[str, Any], dict[str, Any]]) -> Path:
    packed, _raw, audit, manifest = bundle
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        resource_path = stage / RESOURCE
        resource_path.parent.mkdir(parents=True, exist_ok=True)
        resource_path.write_bytes(packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    packed, _raw, audit, manifest = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require((output / RESOURCE).read_bytes() == packed, "private candidate resource differs")
    require((output / "audit.v1.json").read_bytes() == canonical_json(audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("derive-pins", "build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result = derive_pins()
    elif args.command == "build":
        output = write_candidate(prepare_candidate())
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": len(CHANGES),
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
