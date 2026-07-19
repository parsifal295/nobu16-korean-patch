#!/usr/bin/env python3
"""Build the private W66 PC-source semantic correction overlay from W65.

W66 is a bounded PC-only correction pass: 46 static MSGGAME literals and 15
static event rows.  It keeps W64's approved event reflows and W65's four
``내대신`` title fixes intact.  Six fully static dialogue targets receive
safe three-line reflow; their widths are pinned at or below 912 px.  No font,
Steam resource, Git state, network state, or public release is touched by
this builder.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
# Keep the earlier discarded private build intact for audit; the final W66
# bundle is deliberately emitted to a distinct private candidate directory.
CANDIDATE_ROOT = TMP_ROOT / "candidate-final2"
W65_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave65_v1"
    / "build_pc_private_union_composite_wave65_v1.py"
)


class Wave66Error(RuntimeError):
    """Raised when a pinned W65 input or W66 output contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave66Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave66Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w65 = load_module("pc_private_union_wave65_for_wave66", W65_BUILDER)
w64 = w65.w64
w63 = w65.w63
w62 = w65.w62
w61 = w65.w61
w60 = w65.w60

BASE = w65.BASE
PK = w65.PK
MSGDATA = w65.MSGDATA
MSGEV = w65.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class DialogueTarget:
    resource: str
    coordinate: tuple[int, int, int]
    current_ko: str
    target_ko: str
    direct_pc_jp: str
    rationale: str
    allow_lf_change: bool = False
    target_line_widths_px: tuple[int, ...] | None = None

    @property
    def coordinate_text(self) -> str:
        return ":".join(str(value) for value in self.coordinate)


@dataclass(frozen=True)
class EventTarget:
    entry_id: int
    current_ko: str
    target_ko: str
    direct_pc_jp: str
    target_line_widths_px: tuple[int, ...]
    rationale: str


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    dialogue_effective: Mapping[tuple[str, int, int, int], str]
    dialogue_classifications: Mapping[str, tuple[tuple[str, int, int, int], ...]]
    dialogue_rows: tuple[Mapping[str, Any], ...]
    event_effective: Mapping[int, str]
    event_classifications: Mapping[str, tuple[int, ...]]
    event_rows: tuple[Mapping[str, Any], ...]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


DIALOGUE_TARGETS = (
    DialogueTarget(
        BASE, (2, 105, 0),
        "원복를 맞이해\n어엿한 한 사람 몫이 된 무장이",
        "원복을 맞이해\n어엿한 한 사람 몫이 된 무장이",
        "元服を迎え\n一人前となった武将が",
        "원복 뒤의 목적격 조사를 바로잡는다.",
    ),
    DialogueTarget(
        BASE, (2, 106, 0),
        "원복를 치르고\n휘하에 가담하는 무장이",
        "원복을 치르고\n휘하에 가담하는 무장이",
        "元服して\n幕下に加わる武将が",
        "원복 뒤의 목적격 조사를 바로잡는다.",
    ),
    DialogueTarget(
        BASE, (2, 242, 0),
        "작사라면 특기라",
        "공사라면 특기라",
        "作事であれば得手に",
        "作事는 글쓰기(작사)가 아니라 공사·건축이다.",
    ),
    DialogueTarget(
        BASE, (2, 619, 2),
        "다\n놈들에게 신의 위광을 보여주는 것이다",
        "여\n놈들에게 신의 위광을 보여주는 것이다",
        "よ\n奴らに神の威光を示すのだ",
        "호격 よ를 문맥에 맞는 여로 바로잡는다.",
    ),
    DialogueTarget(
        BASE, (4, 4, 0),
        "게임을 종료합니다.\n계속하시겠습니까?",
        "게임을 종료합니다.\n정말 종료하시겠습니까?",
        "ゲームを終了します。\nよろしいですか？",
        "게임 종료 확인문을 자연스러운 한국어 확인문으로 바로잡는다.",
    ),
    DialogueTarget(
        BASE, (6, 1143, 0),
        "매번 감사드립니다\n지금은 가보도 취급하고 있습죠",
        "매번 감사드립니다\n지금은 가보도 취급하고 있습니다",
        "毎度ありがとうございます\n今は家宝も扱っておりますぞ",
        "상인 대사의 비문 습죠를 표준 종결형 있습니다로 바로잡는다.",
        False,
        (408, 744),
    ),
    DialogueTarget(
        BASE, (6, 1144, 0),
        "매번 감사드립니다\n단골손님을 위해 상등품 가보를 준비해 두었습죠",
        "매번 감사드립니다\n단골손님을 위해\n상등품 가보를 준비해 두었습니다",
        "毎度ありがとうございます\nお得意様のため上物の家宝を用意しましたぞ",
        "상인 대사의 비문을 바로잡고 긴 문장을 세 줄에 안전하게 재배치한다.",
        True,
        (408, 360, 744),
    ),
    DialogueTarget(
        BASE, (6, 1145, 0),
        "매번 감사드립니다, 덕분에\n구입 가격이 싸졌습죠",
        "매번 감사드립니다, 덕분에\n구입 가격이 싸졌습니다",
        "毎度ありがとうございます、おかげさまで\n購入価格が安くなっておりますぞ",
        "상인 대사의 비문 습죠를 표준 종결형 있습니다로 바로잡는다.",
        False,
        (600, 528),
    ),
    DialogueTarget(
        BASE, (6, 1146, 0),
        "매번 감사드립니다, 덕분에\n거래할 수 있는 양이 많아졌습죠",
        "매번 감사드립니다, 덕분에\n거래할 수 있는 양이 많아졌습니다",
        "毎度ありがとうございます、おかげさまで\n取引できる量が多くなっておりますぞ",
        "상인 대사의 비문 습죠를 표준 종결형 있습니다로 바로잡는다.",
        False,
        (600, 768),
    ),
    DialogueTarget(
        BASE, (6, 1541, 1),
        "의 심증은\n최악이라 해도 좋을 것입니다.\n전쟁이 나도 이상하지 않사옵니다",
        "의 인상은\n최악이라 해도 좋을 것입니다.\n전쟁이 나도 이상하지 않사옵니다",
        "の心証は\n最悪と言ってよろしいかと。\n戦となるも不思議ではありませぬぞ",
        "心証은 법적 심증이 아니라 상대의 인상·호감도다.",
    ),
    DialogueTarget(
        BASE, (6, 1560, 0),
        "이(가) 단교 운운하였다 하옵니다。\n이를 방치하면 다른 가문에게도\n얕보일 수 있사옵니다",
        "이(가) 단교 운운하였다 하옵니다.\n이를 방치하면 다른 가문에게도\n얕보일 수 있사옵니다",
        "が手切れなどと申したとか。\nこれを捨て置いては他家にも\n軽く見られかねませぬぞ",
        "일본식 마침표를 한국어 마침표로 바로잡는다.",
        False,
        (768, 696, 480),
    ),
    DialogueTarget(
        BASE, (6, 1596, 0),
        "이(가) 당가에 종속하였사오나\n놈들은 우리의 힘을 이용하려는 것\n뿐일지도 모르옵니다, 조심하시오소서",
        "이(가) 당가에 종속하였사오나\n놈들은 우리의 힘을 이용하려는 것\n뿐일지도 모르옵니다, 조심하십시오",
        "が当家に従属しましたが\n奴らは我らの力を利用したい\nだけやもしれません、お気をつけを",
        "중복된 존대 어미 하시오소서를 표준 종결형 하십시오로 바로잡는다.",
        False,
        (672, 768, 792),
    ),
    DialogueTarget(
        BASE, (6, 2169, 2),
        "의 원군은 여기까지…\n이후로는、무운을 빌겠",
        "의 원군은 여기까지…\n이후로는, 무운을 빌겠",
        "が援軍はこれまで…\nあとは、ご武運を祈",
        "일본식 쉼표와 누락된 공백을 한국어 표기로 바로잡는다.",
        False,
        (480, 504),
    ),
    DialogueTarget(
        BASE, (6, 2634, 0),
        "눈앞의 싸움에만 눈을 두는 것은\n다이묘 된 자가 할 일이 아니다, 인가",
        "눈앞의 싸움에만 눈을 두는 것은\n다이묘 된 자가 할 일이 아닌가",
        "目前の戦に目を向け続けるのみは\n大名たる者のする事にあらじ、か",
        "부정 의문문의 조사와 띄어쓰기를 바로잡는다.",
    ),
    DialogueTarget(
        BASE, (6, 2777, 0),
        "적이라 여길 자가 없다면 나라를 부유하게 한다.n외교도 정치의 한 축을 맡고 있느니",
        "적이라 여길 자가 없다면\n나라를 부유하게 한다.\n외교도 정치의 한 축을 맡고 있느니",
        "敵と見据える者無きなら、国を富ませる。n外交も政の一端を担っておろうて",
        "표시되는 ASCII n 오타를 제거하고 의미 단위로 세 줄을 나눈다.",
        True,
        (552, 504, 792),
    ),
    DialogueTarget(
        BASE, (6, 4181, 0),
        "적성 공략의 뜻을 각 성주에게 전했더니\n다음 성에서 구체안이 나왔습니다.",
        "적성 조략의 뜻을 각 성주에게 전했더니\n다음 성에서 구체안이 나왔습니다.",
        "敵城調略の意向を各城主に伝えたところ\n次の城にて具体案が出され",
        "敵城調略은 공격(공략)이 아니라 공작·조략이다.",
    ),
    DialogueTarget(
        BASE, (7, 1504, 0),
        "는 상당한 수비\n독력으로는 다소 벅찰 듯\n원군과 협력하여 공격하시오소서",
        "는 상당한 수비\n독력으로는 다소 벅찰 듯\n원군과 협력하여 공격하십시오",
        "はなかなかの守り\n独力ではいささか骨かと\n援軍と協力して攻められませ",
        "중복된 존대 어미 하시오소서를 표준 종결형 하십시오로 바로잡는다.",
        False,
        (336, 552, 672),
    ),
    DialogueTarget(
        BASE, (7, 2428, 1),
        "을(를) 지키기는\n상당한 난사가 될 것이다",
        "을(를) 지키기는\n상당한 난제가 될 것이다",
        "を守るは\n相当の難事となる",
        "難事는 난사가 아니라 난제다.",
    ),
    DialogueTarget(
        BASE, (7, 2429, 1),
        "을(를) 지키기는\n상당한 난사가 될 것이다",
        "을(를) 지키기는\n상당한 난제가 될 것이다",
        "を守るは\n相当の難事となる",
        "難事는 난사가 아니라 난제다.",
    ),
    DialogueTarget(
        BASE, (8, 1065, 1),
        "\n더 이상의 피해는 나오지 않는다",
        "\n더 이상의 피해는 없을 것이다",
        "\nこれ以上の被害は出ない",
        "피해가 나온다는 직역을 자연스러운 부정문으로 바로잡는다.",
    ),
    DialogueTarget(
        BASE, (8, 1168, 0),
        "수험도의 총본산인 긴푸센지에 기진하여\n승려들의 심증이 좋아지면\n그들도 나서서 절을 세울 것입니다",
        "수험도의 총본산인 긴푸센지에 기진하여\n승려들의 호감이 높아지면\n그들도 나서서 절을 세울 것입니다",
        "修験道の総本山の金峯山寺に寄進し\n僧たちの心証が良くなれば\n彼らも進んで寺を建てましょう",
        "心証が良い는 심증이 아니라 호감·인상이 좋다는 뜻이다.",
    ),
    DialogueTarget(
        BASE, (8, 1172, 0),
        "동국 최고 학부인 아시카가 학교를 지원하면\n가신들도 학문으로 성장함을 막을 수 없사옵니다",
        "동국 최고 학부인 아시카가 학교를\n지원하면 가신들도 학문으로\n성장할 수밖에 없사옵니다",
        "東国の最高学府である足利学校を援助し\n家臣達も勉学で成長するやまれません",
        "成長するやまれません은 성장할 수밖에 없다는 뜻이며, 세 줄에 안전하게 재배치한다.",
        True,
        (768, 624, 576),
    ),
    DialogueTarget(
        BASE, (8, 1173, 0),
        "동국 최대의 영지에 있는 만간지에 시주하면\n우리 통치의 좋은 선전이 되고\n병사에 대한 통솔력도 높아질 것입니다",
        "동국 최대의 성지에 있는 만간지에\n시주하면 우리 통치의 좋은 선전이 되고\n병사에 대한 통솔력도 높아질 것입니다",
        "東国最大の霊場にある満願寺に寄進すれば\n我らの統治の良い宣伝になり\n兵への統率力も高まるでしょう",
        "霊場은 영지가 아니라 영험한 성지이며, 세 줄에 안전하게 재배치한다.",
        False,
        (768, 888, 864),
    ),
    DialogueTarget(
        BASE, (8, 1176, 0),
        "아소 신사는 예로부터 천하의 흉조를\n점치는 영지라 전해지고 있으니\n재건하면 반드시 우리에게 도움이 되오리다",
        "아소 신사는 예로부터 천하의 흉조를\n점치는 성지라 전해지고 있으니 재건하면\n반드시 우리에게 도움이 되오리다",
        "阿蘇神社は古くか天下の凶兆\nを占う霊場と言われるている\n再興すれば必ず我らの助かりなるでしょう",
        "霊場은 영지가 아니라 영험한 성지이며, 세 줄에 안전하게 재배치한다.",
        False,
        (816, 912, 744),
    ),
    DialogueTarget(
        BASE, (13, 309, 0),
        "【설정상의 주의】\n ・공략 목표를 설정한 후, 가신은 내정을 중단하고\n  군비나 조략에 관한 행동만 수행한다\n ・임전 상태는 출진해 귀환한 후, 또는 일정 시간이 지난 후에 해제된다\n ・성대/군대는 군비를 할 수 없다",
        "【설정상의 주의】\n ・공략 목표를 설정한 후, 가신은 내정을 중단하고\n  군비나 조략에 관한 행동만 수행한다\n ・임전 상태는 출진해 귀환한 후, 또는 일정 시간이 지난 후에 해제된다\n ・성대/군다이는 군비를 할 수 없다",
        "【設定上の注意】\n　・攻略目標を設定後、家臣は内政をとりやめ\n　　軍備や調略に関する行動のみを行う\n　・臨戦状態は、出陣して帰還後、または一定時間経過後に解除される\n　・城代／郡代は軍備ができない",
        "郡代 직함을 군대가 아닌 군다이로 바로잡되 튜토리얼 개행 구조는 보존한다.",
    ),
    DialogueTarget(
        BASE, (13, 418, 0),
        "준비 성에는 임전 상태인 군의 수가 표시되며\n모든 군이 임전 상태가 되면 아이콘 색이 바뀝니다.\n※성대·군대의 군은 임전 상태가 되지 않습니다\n\n임전 상태인 군이 많을수록 부대가 강화되어 더 오래 출진할 수 있으나\n모든 군이 임전 상태가 되기 전에 출진할 수도 있습니다.",
        "준비 성에는 임전 상태인 군의 수가 표시되며\n모든 군이 임전 상태가 되면 아이콘 색이 바뀝니다.\n※성대·군다이의 군은 임전 상태가 되지 않습니다\n\n임전 상태인 군이 많을수록 부대가 강화되어 더 오래 출진할 수 있으나\n모든 군이 임전 상태가 되기 전에 출진할 수도 있습니다.",
        "準備城には臨戦状態の郡の数が表示され\n全郡が臨戦状態になるとアイコンの色が変わります。\n※城代・郡代の郡は臨戦状態になりません\n\n臨戦状態の郡が多いほど部隊が強化され、より長く出陣できますが\n全郡が臨戦状態になる前に出陣することも可能です。",
        "郡代 직함을 군대가 아닌 군다이로 바로잡되 튜토리얼 개행 구조는 보존한다.",
    ),
    DialogueTarget(
        PK, (2, 111, 0),
        "원복를 맞이해\n어엿한 한 사람 몫이 된 무장이",
        "원복을 맞이해\n어엿한 한 사람 몫이 된 무장이",
        "元服を迎え\n一人前となった武将が",
        "원복 뒤의 목적격 조사를 바로잡는다.",
    ),
    DialogueTarget(
        PK, (2, 112, 0),
        "원복를 치르고\n휘하에 가담하는 무장이",
        "원복을 치르고\n휘하에 가담하는 무장이",
        "元服して\n幕下に加わる武将が",
        "원복 뒤의 목적격 조사를 바로잡는다.",
    ),
    DialogueTarget(
        PK, (2, 248, 0),
        "작사라면 특기라",
        "공사라면 특기라",
        "作事であれば得手に",
        "作事는 글쓰기(작사)가 아니라 공사·건축이다.",
        False,
        (360,),
    ),
    DialogueTarget(
        PK, (2, 670, 0),
        "군대는 설비를 건설할 수 없습니다",
        "군다이는 설비를 건설할 수 없습니다",
        "郡代は設備建設不可",
        "郡代 직함을 군대가 아닌 군다이로 바로잡는다.",
    ),
    DialogueTarget(
        PK, (2, 671, 0),
        "“군사제”에 따라 군대가 건설합니다",
        "“군사제”에 따라 군다이가 건설합니다",
        "「郡司制」により郡代が建設します",
        "郡代 직함을 군대가 아닌 군다이로 바로잡는다.",
    ),
    DialogueTarget(
        PK, (6, 1547, 1),
        "의 심증은\n최악이라 해도 좋을 것입니다.\n전쟁이 나도 이상하지 않사옵니다",
        "의 인상은\n최악이라 해도 좋을 것입니다.\n전쟁이 나도 이상하지 않사옵니다",
        "の心証は\n最悪と言ってよろしいかと。\n戦となるも不思議ではありませぬぞ",
        "心証은 법적 심증이 아니라 상대의 인상·호감도다.",
    ),
    DialogueTarget(
        PK, (6, 1566, 0),
        "이(가) 단교 운운하였다 하옵니다。\n이를 방치하면 다른 가문에게도\n얕보일 수 있사옵니다",
        "이(가) 단교 운운하였다 하옵니다.\n이를 방치하면 다른 가문에게도\n얕보일 수 있사옵니다",
        "が手切れなどと申したとか。\nこれを捨て置いては他家にも\n軽く見られかねませぬぞ",
        "일본식 마침표를 한국어 마침표로 바로잡는다.",
        False,
        (768, 696, 480),
    ),
    DialogueTarget(
        PK, (6, 1602, 0),
        "이(가) 당가에 종속하였사오나\n놈들은 우리의 힘을 이용하려는 것\n뿐일지도 모르옵니다, 조심하시오소서",
        "이(가) 당가에 종속하였사오나\n놈들은 우리의 힘을 이용하려는 것\n뿐일지도 모르옵니다, 조심하십시오",
        "が当家に従属しましたが\n奴らは我らの力を利用したい\nだけやもしれません、お気をつけを",
        "중복된 존대 어미 하시오소서를 표준 종결형 하십시오로 바로잡는다.",
        False,
        (672, 768, 792),
    ),
    DialogueTarget(
        PK, (6, 2175, 2),
        "의 원군은 여기까지…\n이후로는、무운을 빌겠",
        "의 원군은 여기까지…\n이후로는, 무운을 빌겠",
        "が援軍はこれまで…\nあとは、ご武運を祈",
        "일본식 쉼표와 누락된 공백을 한국어 표기로 바로잡는다.",
        False,
        (480, 504),
    ),
    DialogueTarget(
        PK, (6, 2640, 0),
        "눈앞의 싸움에만 눈을 두는 것은\n다이묘 된 자가 할 일이 아니다, 인가",
        "눈앞의 싸움에만 눈을 두는 것은\n다이묘 된 자가 할 일이 아닌가",
        "目前の戦に目を向け続けるのみは\n大名たる者のする事にあらじ、か",
        "부정 의문문의 조사와 띄어쓰기를 바로잡는다.",
        False,
        (720, 696),
    ),
    DialogueTarget(
        PK, (6, 2783, 0),
        "적이라 여길 자가 없다면 나라를 부유하게 한다.n외교도 정치의 한 축을 맡고 있느니",
        "적이라 여길 자가 없다면\n나라를 부유하게 한다.\n외교도 정치의 한 축을 맡고 있느니",
        "敵と見据える者無きなら、国を富ませる。n外交も政の一端を担っておろうて",
        "표시되는 ASCII n 오타를 제거하고 의미 단위로 세 줄을 나눈다.",
        allow_lf_change=True,
        target_line_widths_px=(552, 504, 792),
    ),
    DialogueTarget(
        PK, (6, 4211, 0),
        "적성 공략의 뜻을 각 성주에게 전했더니\n다음 성에서 구체안이 나왔습니다.",
        "적성 조략의 뜻을 각 성주에게 전했더니\n다음 성에서 구체안이 나왔습니다.",
        "敵城調略の意向を各城主に伝えたところ\n次の城にて具体案が出され",
        "敵城調略은 공격(공략)이 아니라 공작·조략이다.",
    ),
    DialogueTarget(
        PK, (7, 1544, 0),
        "는 상당한 수비\n독력으로는 다소 벅찰 듯\n원군과 협력하여 공격하시오소서",
        "는 상당한 수비\n독력으로는 다소 벅찰 듯\n원군과 협력하여 공격하십시오",
        "はなかなかの守り\n独力ではいささか骨かと\n援軍と協力して攻められませ",
        "중복된 존대 어미 하시오소서를 표준 종결형 하십시오로 바로잡는다.",
        False,
        (336, 552, 672),
    ),
    DialogueTarget(
        PK, (7, 2474, 1),
        "을(를) 지키기는\n상당한 난사가 될 것이다",
        "을(를) 지키기는\n상당한 난제가 될 것이다",
        "を守るは\n相当の難事となる",
        "難事는 난사가 아니라 난제다.",
        False,
        (360, 552),
    ),
    DialogueTarget(
        PK, (7, 2475, 1),
        "을(를) 지키기는\n상당한 난사가 될 것이다",
        "을(를) 지키기는\n상당한 난제가 될 것이다",
        "を守るは\n相当の難事となる",
        "難事는 난사가 아니라 난제다.",
        False,
        (360, 552),
    ),
    DialogueTarget(
        PK, (8, 1077, 1),
        "\n더 이상의 피해는 나오지 않는다",
        "\n더 이상의 피해는 없을 것이다",
        "\nこれ以上の被害は出ない",
        "피해가 나온다는 직역을 자연스러운 부정문으로 바로잡는다.",
        False,
        (0, 672),
    ),
    DialogueTarget(
        PK, (8, 1246, 0),
        "아직 영토는 없지만 지위가 높은 가신들에게는\n이대로 처벌받을 수 있나요?",
        "아직 영지가 없는 고위 가신에게\n이러한 조치를 하는 건 어떻겠습니까?",
        "まだ領地を持たない身分の高い家臣に対して\nこのような仕置を行うのがいかがでしょうか",
        "대상·행위가 뒤집힌 문장과 仕置의 처벌 오역을 바로잡는다.",
    ),
    DialogueTarget(
        PK, (13, 331, 0),
        "【설정상의 주의】\n ·공략 목표를 설정한 후, 가신은 내정을 중단하고\n  군비나 조략에 관한 행동만 수행한다\n ·임전 상태는 출진해 귀환한 후, 또는 일정 시간이 지난 후에 해제된다\n ·성대/군대는 군비를 할 수 없다",
        "【설정상의 주의】\n ·공략 목표를 설정한 후, 가신은 내정을 중단하고\n  군비나 조략에 관한 행동만 수행한다\n ·임전 상태는 출진해 귀환한 후, 또는 일정 시간이 지난 후에 해제된다\n ·성대/군다이는 군비를 할 수 없다",
        "【設定上の注意】\n　・攻略目標を設定後、家臣は内政をとりやめ\n　　軍備や調略に関する行動のみを行う\n　・臨戦状態は、出陣して帰還後、または一定時間経過後に解除される\n　・城代／郡代は軍備ができない",
        "郡代 직함을 군대가 아닌 군다이로 바로잡되 튜토리얼 개행 구조는 보존한다.",
    ),
    DialogueTarget(
        PK, (13, 454, 0),
        "군비 거점에는 임전 상태가 된 군의 수가 표시되며,\n모든 군이 임전 상태가 되면 아이콘 색이 바뀝니다.\n※성대와 군대가 맡은 군은 임전 상태가 되지 않습니다.\n\n임전 상태인 군이 많을수록 부대가 강화되고 더 오래 출진할 수 있지만,\n모든 군이 임전 상태가 되기 전에도 출진할 수 있습니다.",
        "군비 거점에는 임전 상태가 된 군의 수가 표시되며,\n모든 군이 임전 상태가 되면 아이콘 색이 바뀝니다.\n※성대와 군다이가 맡은 군은 임전 상태가 되지 않습니다.\n\n임전 상태인 군이 많을수록 부대가 강화되고 더 오래 출진할 수 있지만,\n모든 군이 임전 상태가 되기 전에도 출진할 수 있습니다.",
        "軍備拠点には臨戦状態の郡の数が表示され\n全郡が臨戦状態になるとアイコンの色が変わります。\n※城代・郡代の郡は臨戦状態になりません\n\n臨戦状態の郡が多いほど部隊が強化され、より長く出陣できますが\n全郡が臨戦状態になる前に出陣することも可能です。",
        "郡代 직함을 군대가 아닌 군다이로 바로잡되 튜토리얼 개행 구조는 보존한다.",
    ),
    DialogueTarget(
        PK, (13, 578, 0),
        "방위 담당 무장은 담당 구획에 중요 설비나 방책을 건설해 공성전에 대비합니다.\n공성전을 유리하게 이끌도록 무장과 설비 배치를 궁리하십시오.\n\n【담당 구획을 정할 때의 요점】\n ·적에게 피해를 주는 설비는 전선에 배치\n ·아군을 회복·강화하는 설비는 성 주변에 배치\n ·적 세력과 마주한 구획에는 뛰어난 무장을 배치\n ※군대는 설비를 건설할 수 없으니 주의",
        "방위 담당 무장은 담당 구획에 중요 설비나 방책을 건설해 공성전에 대비합니다.\n공성전을 유리하게 이끌도록 무장과 설비 배치를 궁리하십시오.\n\n【담당 구획을 정할 때의 요점】\n ·적에게 피해를 주는 설비는 전선에 배치\n ·아군을 회복·강화하는 설비는 성 주변에 배치\n ·적 세력과 마주한 구획에는 뛰어난 무장을 배치\n ※군다이는 설비를 건설할 수 없으니 주의",
        "防衛担当の武将は、攻城戦に備えて担当区画に重要設備や防柵を建設します。\n攻城戦を有利に運ぶため、武将や設備の配置を工夫しましょう。\n\n【担当区画決めのポイント】\n　・敵に被害を与える設備は前線に配置する\n　・味方の回復や強化を行う設備は城周辺に配置する\n　・敵勢力に面している区画に優秀な武将を配置する\n　※郡代は設備を建設できないので注意",
        "郡代 직함을 군대가 아닌 군다이로 바로잡되 튜토리얼 개행 구조는 보존한다.",
    ),
)

EVENT_TARGETS = (
    EventTarget(
        9885,
        "\x1bCC이시다 미쓰나리\x1bCZ는 실전의 지휘관이 된\n지부노쇼로, \x1bCA오미 사와야마\x1bCZ 성주였다.\n과거 \x1bCB도요토미\x1bCZ 공의에서 부교를 지냈다.",
        "실전 지휘관이 된 지부노쇼라 불린\n\x1bCC오미 사와야마\x1bCZ 성주 \x1bCA이시다 미쓰나리\x1bCZ.\n과거 \x1bCB도요토미\x1bCZ 정권에서 봉행을 지냈다.",
        "実戦における指揮官となった治部少輔こと\n\x1bCC近江佐和山\x1bCZ城主・\x1bCA石田三成\x1bCZ。\nかつて\x1bCB豊臣\x1bCZ公儀で奉行を務めた。",
        (768, 840, 888),
        "인물·지명 태그와 治部少輔こと의 호칭 의미를 원문 순서로 복원한다.",
    ),
    EventTarget(
        9916,
        "어떻게든 \x1bCC데루모토\x1bCZ 님께서\n\x1bCA오사카\x1bCZ에서 출진하게 할 수 없겠나?",
        "어떻게든 \x1bCC오사카\x1bCZ에서 \x1bCA데루모토\x1bCZ 님께서\n출진하시도록 할 수 없겠나?",
        "どうにか\x1bCC大坂\x1bCZより\x1bCA輝元\x1bCZ殿に\nご出馬いただくことはできないだろうか？",
        (840, 624),
        "오사카 지명과 데루모토 인물 태그를 바로잡고 자연스러운 청유문으로 다듬는다.",
    ),
    EventTarget(
        9975,
        "충신 \x1bCC도리이 모토타다\x1bCZ는 적은\n병력으로 \x1bCA후시미성\x1bCZ을 끝까지 지켰으나\n일기토 끝에 전사했다.",
        "적은 병력으로 \x1bCC후시미성\x1bCZ을\n끝까지 지킨 충신 \x1bCA도리이 모토타다\x1bCZ는\n일기토 끝에 전사했다.",
        "寡兵にてよく\x1bCC伏見城\x1bCZを守り抜くも\n忠臣・\x1bCA鳥居元忠\x1bCZ、一騎討ちの末に討死。",
        (576, 816, 504),
        "후시미성과 도리이 모토타다의 지명·인물 태그를 바로잡는다.",
    ),
    EventTarget(
        9998,
        "\x1bCA오타니 요시쓰구\x1bCZ 계략과 \x1bCA니와 나가시게\x1bCZ\n분전으로 \x1bCC서군\x1bCZ은 \x1bCB호쿠리쿠\x1bCZ서 우세했다.\n\x1bCA요시쓰구\x1bCZ는 \x1bCC미노\x1bCZ·\x1bCC오가키성\x1bCZ으로 향했다.",
        "\x1bCA오타니 요시쓰구\x1bCZ 계략과 \x1bCA니와 나가시게\x1bCZ\n분전으로 \x1bCC호쿠리쿠\x1bCZ에서 \x1bCB서군\x1bCZ이 우세했다.\n\x1bCA요시쓰구\x1bCZ는 \x1bCC미노\x1bCZ·\x1bCC오가키성\x1bCZ으로 향했다.",
        "\x1bCA大谷吉継\x1bCZの機略、\x1bCA丹羽長重\x1bCZの奮闘により、\n\x1bCC北陸\x1bCZにおける\x1bCB西軍\x1bCZ優位は明らかとなった。\n\x1bCA吉継\x1bCZは次なる戦場、\x1bCC美濃\x1bCZ・\x1bCC大垣城\x1bCZへと向かう。",
        (864, 912, 888),
        "호쿠리쿠 지명과 서군 세력 태그를 바로잡는다.",
    ),
    EventTarget(
        10272,
        "\x1bCA도요토미\x1bCZ가 나아갈 길을 밝혀 온 충신\n\x1bCB이시다 미쓰나리\x1bCZ라는\n횃불도 여기서 꺼졌다.",
        "\x1bCA이시다 미쓰나리\x1bCZ는 주군 가문의\n앞길을 밝혀 온 충신. \x1bCB도요토미\x1bCZ의 횃불도\n여기서 꺼졌다.",
        "主家の行く道を照らしてきた\x1bCA石田三成\x1bCZ。\n\x1bCB豊臣\x1bCZのかがり火たる忠臣もここに消えゆく。",
        (696, 912, 336),
        "미쓰나리 인물과 도요토미 세력 태그를 바로잡고 문장을 복원한다.",
    ),
    EventTarget(
        10274,
        "\x1bCC서군\x1bCZ이 \x1bCB세키가하라\x1bCZ에서 패하면서\n\x1bCA사나다 마사유키\x1bCZ는 궁지에 몰렸다.",
        "\x1bCC세키가하라\x1bCZ에서 \x1bCB서군\x1bCZ이 패하면서\n\x1bCA사나다 마사유키\x1bCZ는 궁지에 몰렸다.",
        "\x1bCC関ヶ原\x1bCZにおける\x1bCB西軍\x1bCZの敗北により\n\x1bCA真田昌幸\x1bCZは窮地に立たされた。",
        (720, 768),
        "세키가하라 지명과 서군 세력 태그를 바로잡는다.",
    ),
    EventTarget(
        10288,
        "하지만 우리는 유배되어 이 땅을\n떠나게 될 것이다. \x1bCB노부유키\x1bCZ를 당주로\n삼은 \x1bCA사나다\x1bCZ가 앞날을 이어 가겠지.",
        "하지만 우리는 유배되어 이 땅을\n떠나게 될 것이다. \x1bCB사나다\x1bCZ는 \x1bCA노부유키\x1bCZ를\n당주로 삼아 앞날을 이어 가겠지.",
        "しかし、我らは流罪となり、\nこの地を去ることになろう。\n\x1bCB真田\x1bCZは\x1bCA信之\x1bCZを当主として歩んでゆくのだ。",
        (720, 888, 744),
        "사나다 세력과 노부유키 인물 태그를 바로잡는다.",
    ),
    EventTarget(
        10334,
        "\x1bCA미쓰나리\x1bCZ는 \x1bCA도요토미\x1bCZ 은고지만\n\x1bCB이에야스\x1bCZ 편 든 다이묘를 벌하고,\n\x1bCB동군\x1bCZ 장수의 당주를 교체·감봉했다.",
        "\x1bCA미쓰나리\x1bCZ는 \x1bCA이에야스\x1bCZ 편을 든\n\x1bCB도요토미\x1bCZ 은고 다이묘를 벌하고,\n\x1bCB동군\x1bCZ 장수들의 당주를 교체·감봉했다.",
        "\x1bCA三成\x1bCZは\x1bCA家康\x1bCZに与した\x1bCB豊臣\x1bCZ恩顧大名を処罰。\n\x1bCB東軍\x1bCZ諸将の当主交替と減封を行った。",
        (648, 720, 864),
        "이에야스 인물과 도요토미 세력 태그를 바로잡고 동군 제장 복수를 반영한다.",
    ),
    EventTarget(
        10450,
        "천하의 주인 \x1bCA이에야스\x1bCZ에게 남은 걱정은\n태합 \x1bCC히데요시\x1bCZ가 \x1bCA오사카\x1bCZ에 남긴 유복자\n\x1bCA도요토미 히데요리\x1bCZ뿐이었다.",
        "천하의 주인 \x1bCA이에야스\x1bCZ에게 남은 걱정은\n아직 \x1bCC오사카\x1bCZ에 남은 태합 \x1bCA히데요시\x1bCZ의\n남겨진 아들 \x1bCA도요토미 히데요리\x1bCZ뿐이었다.",
        "天下の主・\x1bCA家康\x1bCZの心残りとなったのは\n未だ\x1bCC大坂\x1bCZに座す太閤・\x1bCA秀吉\x1bCZの忘れ形見\n\x1bCA豊臣秀頼\x1bCZのみ。",
        (864, 816, 912),
        "오사카 지명과 히데요시 인물 태그를 바로잡고 忘れ形見을 사실에 맞는 남겨진 아들로 옮긴다.",
    ),
    EventTarget(
        10513,
        "또한 \x1bCC마사무네\x1bCZ와의 합의에 따라\n\x1bCA에도\x1bCZ 총공격은 결전에서\n\x1bCB미쓰나리 측\x1bCZ이 승리한 뒤로 정했다.",
        "또한 \x1bCC에도\x1bCZ 총공격은\n\x1bCA마사무네\x1bCZ와의 합의에 따라 결전에서\n\x1bCB미쓰나리 측\x1bCZ이 승리한 뒤로 정했다.",
        "また\x1bCC江戸\x1bCZへの総攻撃は\n\x1bCA政宗\x1bCZとの取り決めにより\n決戦で\x1bCB三成方\x1bCZの勝った後と定めた。",
        (432, 792, 792),
        "에도 지명과 마사무네 인물 태그를 바로잡고 결전이라는 조건을 복원한다.",
    ),
    EventTarget(
        10566,
        "\x1bCA도쿠가와\x1bCZ는 \x1bCB가쓰모토\x1bCZ 구원\n명분으로 제후에게 호령해,\n\x1bCA히데요리\x1bCZ 토벌에 나설 셈이었다.",
        "\x1bCA가쓰모토\x1bCZ 구원 명분을 얻은 \x1bCB도쿠가와\x1bCZ는\n마침내 각국 다이묘에게 호령해,\n\x1bCA히데요리\x1bCZ 토벌에 나설 셈이었다.",
        "これにより\x1bCA且元\x1bCZ救援の大義名分を得た\x1bCB徳川\x1bCZは\nついに各国の諸大名に号令をかける。ここで\n\x1bCA秀頼\x1bCZ討伐に動き出すという算段であった。",
        (864, 720, 720),
        "가쓰모토 인물과 도쿠가와 세력 태그를 바로잡는다.",
    ),
    EventTarget(
        10630,
        "\x1bCC히데요시\x1bCZ가 \x1bCA노부나가\x1bCZ 뜻을 이은 성,\n\x1bCA오사카성\x1bCZ을 무대로\n전국 최후의 전쟁이 다가왔다…",
        "\x1bCC오사카성\x1bCZ― \x1bCA노부나가\x1bCZ의 뜻을 잇고자\n\x1bCA히데요시\x1bCZ가 지은 성을 무대로\n전국 최후의 전쟁이 다가왔다…",
        "\x1bCC大坂城\x1bCZ―\n\x1bCA信長\x1bCZの志を継がんと\x1bCA秀吉\x1bCZが築きし城を舞台に\n戦国最後の戦は刻一刻と近づいていた…",
        (792, 648, 696),
        "오사카성 지명과 노부나가·히데요시 인물 태그를 바로잡는다.",
    ),
    EventTarget(
        10815,
        "먼저 병력을 본대와 별동대로 나누고\n별동대를 \x1bCB사이조산\x1bCZ에 틀어박힌\n\x1bCC우에스기군\x1bCZ의 뒤로 보내 기습을 가한다.",
        "먼저 병력을 본대와 별동대로 나누고\n별동대를 \x1bCB우에스기군\x1bCZ이 농성한\n\x1bCC사이조산\x1bCZ으로 보내 뒤에서 기습한다.",
        "兵を本隊と別働隊の二手に分けて\n別働隊を\x1bCB上杉勢\x1bCZの籠る\x1bCC妻女山\x1bCZへ派遣し\n背後より急襲を仕掛ける。",
        (816, 672, 816),
        "우에스기군 세력과 사이조산 지명 태그를 바로잡는다.",
    ),
    EventTarget(
        10866,
        "\x1bCC도쿠가와 이에야스\x1bCZ 구원을 청한\n\x1bCA나가시노성\x1bCZ. \x1bCA오다 노부나가\x1bCZ는 \x1bCA신겐\x1bCZ과의\n악연을 끝내려 흔쾌히 응했다.",
        "\x1bCC나가시노성\x1bCZ 구원을 청한\n\x1bCA도쿠가와 이에야스\x1bCZ. \x1bCA오다 노부나가\x1bCZ는\n\x1bCA신겐\x1bCZ 때의 악연을 끝내려 흔쾌히 응했다.",
        "\x1bCC長篠城\x1bCZ救助のため来援を乞う\x1bCA徳川家康\x1bCZ。\n\x1bCA織田信長\x1bCZは\x1bCA信玄\x1bCZ以来の因縁に決着を付けんと\nこれを快諾した。",
        (528, 816, 912),
        "나가시노성 지명과 이에야스 인물 태그를 바로잡고 信玄以来의 시간적 의미를 복원한다.",
    ),
    EventTarget(
        10940,
        "\x1bCC신겐\x1bCZ이 불길처럼 \x1bCA도토미\x1bCZ를 침공하자,\n\x1bCA노부나가\x1bCZ 동맹 \x1bCA도쿠가와 이에야스\x1bCZ는\n최대 시련에 맞섰다.",
        "\x1bCC도토미\x1bCZ를 불길처럼 유린한 \x1bCA신겐\x1bCZ―\n\x1bCA노부나가\x1bCZ의 맹우, \x1bCA도쿠가와 이에야스\x1bCZ는\n일생 최대의 시련에 맞서려 했다.",
        "\x1bCC遠江\x1bCZを火のごとく侵し掠める\x1bCA信玄\x1bCZ―\n\x1bCA信長\x1bCZの盟友・\x1bCA徳川家康\x1bCZは\n生涯最大の試練に挑まんとしていた。",
        (744, 864, 744),
        "도토미 지명과 신겐 인물 태그를 바로잡고 유린·맹우·맞서려 했다는 원문 의미를 복원한다.",
    ),
)

EXPECTED_DIALOGUE_TARGETS = {
    BASE: tuple(target.coordinate for target in DIALOGUE_TARGETS if target.resource == BASE),
    PK: tuple(target.coordinate for target in DIALOGUE_TARGETS if target.resource == PK),
}
EXPECTED_EVENT_IDS = tuple(target.entry_id for target in EVENT_TARGETS)
EXPECTED_DIALOGUE_CLASSES = {BASE: {"fresh": 26, "already": 0, "override": 0}, PK: {"fresh": 20, "already": 0, "override": 0}}
EXPECTED_EVENT_CLASSES = {"fresh": 15, "already": 0, "override": 0}
# These two W63-era strings already differed from W45, but still retained the
# typo "원복를".  W66 intentionally refines that prior correction from the
# current W65 text, rather than silently treating it as unrelated history.
EXPECTED_BASE_HISTORY_REVISIONS = ((2, 105, 0), (2, 106, 0))
EXPECTED_PK_HISTORY_REVISIONS = ((2, 111, 0), (2, 112, 0))
EXPECTED_HISTORY_REVISION_TEXTS = {
    BASE: {
        (2, 105, 0): (
            "겐푸쿠를 맞이해\n어엿한 한 사람 몫이 된 무장이",
            "원복를 맞이해\n어엿한 한 사람 몫이 된 무장이",
            "원복을 맞이해\n어엿한 한 사람 몫이 된 무장이",
        ),
        (2, 106, 0): (
            "겐푸쿠를 치르고\n휘하에 가담하는 무장이",
            "원복를 치르고\n휘하에 가담하는 무장이",
            "원복을 치르고\n휘하에 가담하는 무장이",
        ),
    },
    PK: {
        (2, 111, 0): (
            "겐푸쿠를 맞이해\n어엿한 한 사람 몫이 된 무장이",
            "원복를 맞이해\n어엿한 한 사람 몫이 된 무장이",
            "원복을 맞이해\n어엿한 한 사람 몫이 된 무장이",
        ),
        (2, 112, 0): (
            "겐푸쿠를 치르고\n휘하에 가담하는 무장이",
            "원복를 치르고\n휘하에 가담하는 무장이",
            "원복을 치르고\n휘하에 가담하는 무장이",
        ),
    },
}
EXPECTED_FINAL_PROFILE_DICTS = {
    BASE: {
        "raw_sha256": "6B3777F916CBBC1138856B95BC26C21B9B746F7A6C579F47FB7083037FE13ED6",
        "raw_size": 1498552,
        "sha256": "F7E3705E421556DCF0BBF1F99562762471FA8E7563E5DFDC0F53BDDC0E24E969",
        "size": 1504454,
    },
    MSGDATA: {
        "raw_sha256": "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
        "raw_size": 495032,
        "sha256": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        "size": 496999,
    },
    MSGEV: {
        "raw_sha256": "15DF5383686AA62426F0F378265FE9E80095A61D48705240DA8904471BCF0863",
        "raw_size": 990904,
        "sha256": "7E89011B17D9B92D7CE4F956D266DB46B157A8F2AD008DE40EA36C4F7E2914DA",
        "size": 994815,
    },
    PK: {
        "raw_sha256": "7CB535FE3499A81F086191FE73AB98C9C81A728F70D4BD4515C2A0E6EBBBDFF5",
        "raw_size": 1799448,
        "sha256": "4AE4C91A71E049D44500CAE899D4BED18F452598DC08FD01BF7BA5EC986DD589",
        "size": 1806530,
    },
}
EXPECTED_FINAL_RECORD_COUNTS = {BASE: 133, PK: 303, MSGDATA: 4, MSGEV: 211}
EXPECTED_FINAL_TOTAL_RECORDS = 651


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w62.profile_dict(value)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave66Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def parse_msggame(blob: bytes, label: str) -> Any:
    return w65.parse_msggame(blob, label)


def literal_at(archive: Any, coordinate: tuple[int, int, int], label: str) -> str:
    return w61.literal_at(archive, coordinate, label)


def dialogue_target_map(resource: str) -> dict[tuple[int, int, int], DialogueTarget]:
    selected = tuple(target for target in DIALOGUE_TARGETS if target.resource == resource)
    mapped = {target.coordinate: target for target in selected}
    require(len(mapped) == len(selected), f"duplicate W66 dialogue target: {resource}")
    require(tuple(mapped) == EXPECTED_DIALOGUE_TARGETS[resource], f"W66 dialogue scope drift: {resource}")
    return mapped


def event_target_map() -> dict[int, EventTarget]:
    mapped = {target.entry_id: target for target in EVENT_TARGETS}
    require(len(mapped) == len(EVENT_TARGETS), "duplicate W66 event target")
    require(tuple(mapped) == EXPECTED_EVENT_IDS, "W66 event target order or scope drift")
    return mapped


def literal_controls(value: str) -> tuple[int, ...]:
    return tuple(ord(character) for character in value if ord(character) < 32 and character not in ("\n", "\r"))


def assert_msggame_structure(
    before: Any,
    after: Any,
    effective: Mapping[tuple[int, int, int], str],
    lf_changing: set[tuple[int, int, int]],
    label: str,
) -> None:
    before_records = w63.w59.archive_records(before)
    after_records = w63.w59.archive_records(after)
    require(set(before_records) == set(after_records), f"{label}: record topology drift")
    before_literals = w63.w59.literal_texts(before)
    after_literals = w63.w59.literal_texts(after)
    require(
        {coordinate for coordinate in before_literals if before_literals[coordinate] != after_literals[coordinate]} == set(effective),
        f"{label}: literal scope drift",
    )
    require(
        {coordinate for coordinate in before_records if before_records[coordinate].data != after_records[coordinate].data}
        == {(block, record) for block, record, _literal in effective},
        f"{label}: record scope drift",
    )
    for coordinate in sorted(before_records):
        before_record = before_records[coordinate]
        after_record = after_records[coordinate]
        require(
            w63.w59.record_skeleton(before_record) == w63.w59.record_skeleton(after_record),
            f"{label}: opaque record bytes drift at {coordinate}",
        )
    for coordinate, source in before_literals.items():
        result = after_literals[coordinate]
        require(literal_controls(source) == literal_controls(result), f"{label}: control drift at {coordinate}")
        if coordinate not in lf_changing:
            require(source.count("\n") == result.count("\n"), f"{label}: unexpected LF drift at {coordinate}")


def overlay_dialogue(
    resource: str,
    w65_blob: bytes,
) -> tuple[
    bytes,
    dict[tuple[int, int, int], str],
    dict[str, tuple[tuple[int, int, int], ...]],
    tuple[Mapping[str, Any], ...],
]:
    before = parse_msggame(w65_blob, f"W65 {resource}")
    direct_jp = w61.load_direct_jp(resource)
    font = w64.layout.load_font()
    effective: dict[tuple[int, int, int], str] = {}
    classes: dict[str, list[tuple[int, int, int]]] = {"fresh": [], "already": [], "override": []}
    rows: list[Mapping[str, Any]] = []
    for coordinate, target in dialogue_target_map(resource).items():
        current = literal_at(before, coordinate, f"W65 {resource}")
        source_jp = literal_at(direct_jp, coordinate, f"pristine PC JP {resource}")
        require(source_jp == target.direct_pc_jp, f"direct PC JP dialogue witness drift: {resource}:{coordinate}")
        require(literal_controls(current) == literal_controls(target.target_ko), f"dialogue control drift: {resource}:{coordinate}")
        if not target.allow_lf_change:
            require(current.count("\n") == target.target_ko.count("\n"), f"dialogue LF drift: {resource}:{coordinate}")
        target_widths = w64.layout.line_widths(target.target_ko, font)
        if target.target_line_widths_px is not None:
            require(target_widths == target.target_line_widths_px, f"dialogue target width drift: {resource}:{coordinate}")
            require(max(target_widths) <= w64.layout.PK_MAX_LINE_PX, f"dialogue reflow over width: {resource}:{coordinate}")
        if current == target.target_ko:
            classes["already"].append(coordinate)
        elif current == target.current_ko:
            classes["fresh"].append(coordinate)
            effective[coordinate] = target.target_ko
        else:
            classes["override"].append(coordinate)
        rows.append({
            "resource": resource,
            "coordinate": target.coordinate_text,
            "w65_current_ko": current,
            "target_ko": target.target_ko,
            "direct_pc_jp": source_jp,
            "w65_current_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target.target_ko),
            "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
            "source_manual_lf_count": current.count("\n"),
            "target_manual_lf_count": target.target_ko.count("\n"),
            "source_line_widths_px": list(w64.layout.line_widths(current, font)),
            "target_line_widths_px": list(target_widths),
            "rationale": target.rationale,
        })
    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_DIALOGUE_CLASSES[resource],
        f"W66 dialogue classification drift: {resource}: {frozen}",
    )
    output = w63.w59.rebuild_packed_with_literals(w65_blob, effective)
    after = parse_msggame(output, f"W66 {resource}")
    assert_msggame_structure(
        before,
        after,
        effective,
        {coordinate for coordinate, target in dialogue_target_map(resource).items() if target.allow_lf_change},
        f"W65-to-W66 {resource}",
    )
    return output, effective, frozen, tuple(rows)


def static_event_signature(value: str, entry_id: int, label: str) -> Mapping[str, Any]:
    signature = dict(w64.layout.control_signature(value))
    require(signature["runtime_tokens"] == [], f"{entry_id} {label} contains runtime tokens")
    require(signature["printf_tokens"] == [], f"{entry_id} {label} contains printf tokens")
    require(signature["unknown_percent_count"] == 0, f"{entry_id} {label} contains unknown percent")
    require(signature["other_controls"] == [], f"{entry_id} {label} contains another control")
    return signature


def overlay_event(
    w65_blob: bytes,
) -> tuple[bytes, dict[int, str], dict[str, tuple[int, ...]], tuple[Mapping[str, Any], ...]]:
    header, _raw, before = w60.parse_table("W65 event", w65_blob)
    direct_jp_blob, _direct_jp_profile = w62.load_direct_jp_event()
    _jp_header, _jp_raw, jp = w60.parse_table("pristine PC JP event", direct_jp_blob)
    require(len(before.texts) == len(jp.texts), "W65/direct-PC-JP event table length drift")
    font = w64.layout.load_font()
    effective: dict[int, str] = {}
    classes: dict[str, list[int]] = {"fresh": [], "already": [], "override": []}
    rows: list[Mapping[str, Any]] = []
    for entry_id, target in event_target_map().items():
        current = before.texts[entry_id]
        source_jp = jp.texts[entry_id]
        require(current == target.current_ko, f"W65 event KO preimage drift: {entry_id}")
        require(source_jp == target.direct_pc_jp, f"direct PC JP event witness drift: {entry_id}")
        source_signature = static_event_signature(source_jp, entry_id, "direct PC JP")
        require(static_event_signature(current, entry_id, "W65 KO") == source_signature, f"W65 event tag drift: {entry_id}")
        require(static_event_signature(target.target_ko, entry_id, "target KO") == source_signature, f"W66 event tag drift: {entry_id}")
        require(current.count("\n") == target.target_ko.count("\n"), f"W66 event LF drift: {entry_id}")
        widths = w64.layout.line_widths(target.target_ko, font)
        require(widths == target.target_line_widths_px, f"W66 event width drift: {entry_id}: {widths}")
        require(max(widths) <= w64.layout.PK_MAX_LINE_PX, f"W66 event over width: {entry_id}")
        if current == target.target_ko:
            classes["already"].append(entry_id)
        elif current == target.current_ko:
            classes["fresh"].append(entry_id)
            effective[entry_id] = target.target_ko
        else:  # pragma: no cover - protected by the preimage check above
            classes["override"].append(entry_id)
        rows.append({
            "entry_id": entry_id,
            "w65_current_ko": current,
            "target_ko": target.target_ko,
            "direct_pc_jp": source_jp,
            "w65_current_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target.target_ko),
            "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
            "source_manual_lf_count": current.count("\n"),
            "target_manual_lf_count": target.target_ko.count("\n"),
            "source_line_widths_px": list(w64.layout.line_widths(current, font)),
            "target_line_widths_px": list(widths),
            "control_signature": source_signature,
            "rationale": target.rationale,
        })
    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_EVENT_CLASSES,
        f"W66 event classification drift: {frozen}",
    )
    texts = list(before.texts)
    for entry_id, value in effective.items():
        texts[entry_id] = value
    raw = w60.core.rebuild_message_table(before, tuple(texts))
    output = w60.core.recompress_wrapper(raw, header)
    _header, output_raw, after = w60.parse_table("W66 event", output)
    require(output_raw == raw, "W66 event raw mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(effective),
        "W66 event scope drift",
    )
    return output, effective, frozen, tuple(rows)


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w65.prepare(require_output_profiles=True)
    w65.verify_private_candidate(base)
    base_output, base_effective, base_classes, base_rows = overlay_dialogue(BASE, base.outputs[BASE])
    pk_output, pk_effective, pk_classes, pk_rows = overlay_dialogue(PK, base.outputs[PK])
    event_output, event_effective, event_classes, event_rows = overlay_event(base.outputs[MSGEV])
    outputs = {
        BASE: base_output,
        PK: pk_output,
        MSGDATA: base.outputs[MSGDATA],
        MSGEV: event_output,
    }
    profiles = {resource: w61.profile(blob) for resource, blob in outputs.items()}
    dialogue_effective = {
        (resource, *coordinate): value
        for resource, values in ((BASE, base_effective), (PK, pk_effective))
        for coordinate, value in values.items()
    }
    dialogue_classifications = {
        name: tuple(
            (resource, *coordinate)
            for resource, classes in ((BASE, base_classes), (PK, pk_classes))
            for coordinate in classes[name]
        )
        for name in ("fresh", "already", "override")
    }
    w45 = w62.load_w45_backups()
    w45_base = parse_msggame(w45[BASE], "W45 Base")
    w45_pk = parse_msggame(w45[PK], "W45 PK")
    w65_base = parse_msggame(base.outputs[BASE], "W65 Base")
    w65_pk = parse_msggame(base.outputs[PK], "W65 PK")
    w66_base = parse_msggame(base_output, "W66 Base")
    w66_pk = parse_msggame(pk_output, "W66 PK")
    w45_base_literals = w63.w59.literal_texts(w45_base)
    w45_pk_literals = w63.w59.literal_texts(w45_pk)
    w65_base_literals = w63.w59.literal_texts(w65_base)
    w65_pk_literals = w63.w59.literal_texts(w65_pk)
    w66_base_literals = w63.w59.literal_texts(w66_base)
    w66_pk_literals = w63.w59.literal_texts(w66_pk)
    w65_base_changed = {coordinate for coordinate in w45_base_literals if w45_base_literals[coordinate] != w65_base_literals[coordinate]}
    w65_pk_changed = {coordinate for coordinate in w45_pk_literals if w45_pk_literals[coordinate] != w65_pk_literals[coordinate]}
    w66_base_changed = {coordinate for coordinate in w45_base_literals if w45_base_literals[coordinate] != w66_base_literals[coordinate]}
    w66_pk_changed = {coordinate for coordinate in w45_pk_literals if w45_pk_literals[coordinate] != w66_pk_literals[coordinate]}
    base_history_revisions = w65_base_changed & set(base_effective)
    pk_history_revisions = w65_pk_changed & set(pk_effective)
    require(
        base_history_revisions == set(EXPECTED_BASE_HISTORY_REVISIONS),
        f"W66 Base history-revision scope drift: {sorted(base_history_revisions)}",
    )
    require(
        pk_history_revisions == set(EXPECTED_PK_HISTORY_REVISIONS),
        f"W66 PK history-revision scope drift: {sorted(pk_history_revisions)}",
    )
    for resource, before_literals, w65_literals, w66_literals in (
        (BASE, w45_base_literals, w65_base_literals, w66_base_literals),
        (PK, w45_pk_literals, w65_pk_literals, w66_pk_literals),
    ):
        expected_history_texts = EXPECTED_HISTORY_REVISION_TEXTS[resource]
        expected_history_coordinates = (
            set(EXPECTED_BASE_HISTORY_REVISIONS)
            if resource == BASE
            else set(EXPECTED_PK_HISTORY_REVISIONS)
        )
        require(
            set(expected_history_texts) == expected_history_coordinates,
            f"W66 {resource} history-revision text contract drift",
        )
        for coordinate, (w45_text, w65_text, w66_text) in expected_history_texts.items():
            require(before_literals[coordinate] == w45_text, f"W66 {resource} W45 history text drift: {coordinate}")
            require(w65_literals[coordinate] == w65_text, f"W66 {resource} W65 history text drift: {coordinate}")
            require(w66_literals[coordinate] == w66_text, f"W66 {resource} W66 history text drift: {coordinate}")
    require(w66_base_changed == w65_base_changed | set(base_effective), "W66 Base W45 retention drift")
    require(w66_pk_changed == w65_pk_changed | set(pk_effective), "W66 PK W45 retention drift")
    _header, _raw, w45_events = w60.parse_table("W45 event", w45[MSGEV])
    _header, _raw, w65_events = w60.parse_table("W65 event", base.outputs[MSGEV])
    _header, _raw, w66_events = w60.parse_table("W66 event", event_output)
    w65_event_changed = {index for index, value in enumerate(w45_events.texts) if value != w65_events.texts[index]}
    w66_event_changed = {index for index, value in enumerate(w45_events.texts) if value != w66_events.texts[index]}
    require(w65_event_changed.isdisjoint(event_effective), "W66 events overlap W65 history")
    require(w66_event_changed == w65_event_changed | set(event_effective), "W66 event W45 retention drift")
    base_records, _ = w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _ = w60.msggame_counts(w45[PK], outputs[PK])
    final_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require(EXPECTED_FINAL_PROFILE_DICTS is not None, "W66 output profile constants are not pinned")
        require(EXPECTED_FINAL_RECORD_COUNTS is not None, "W66 record count constants are not pinned")
        require(EXPECTED_FINAL_TOTAL_RECORDS is not None, "W66 total record constant is not pinned")
        require(
            {resource: profile_dict(profile) for resource, profile in profiles.items()} == EXPECTED_FINAL_PROFILE_DICTS,
            "W66 output profile drift",
        )
        require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, "W66 final record count drift")
        require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS, "W66 final total drift")
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave66-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W65 Steam-PC Korean candidate and pristine PC Japanese only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "base_w65": {resource: profile_dict(w61.profile(base.outputs[resource])) for resource in ALL_RESOURCES},
        "direct_pc_jp_resources": [BASE, PK, MSGEV],
        "dialogue_classifications": {
            name: [":".join((resource, *(str(value) for value in coordinate))) for resource, *coordinate in values]
            for name, values in dialogue_classifications.items()
        },
        "dialogue_rows": list(base_rows) + list(pk_rows),
        "base_history_revision_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(base_history_revisions)],
        "pk_history_revision_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(pk_history_revisions)],
        "event_classifications": {name: list(values) for name, values in event_classes.items()},
        "event_rows": list(event_rows),
        "w45_to_w65_changed_base_literal_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(w65_base_changed)],
        "w45_to_w66_changed_base_literal_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(w66_base_changed)],
        "w45_to_w65_changed_pk_literal_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(w65_pk_changed)],
        "w45_to_w66_changed_pk_literal_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(w66_pk_changed)],
        "w45_to_w65_changed_event_ids": sorted(w65_event_changed),
        "w45_to_w66_changed_event_ids": sorted(w66_event_changed),
        "final_record_counts": final_counts,
        "final_total_records": sum(final_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave66-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(
        outputs,
        profiles,
        dialogue_effective,
        dialogue_classifications,
        tuple(list(base_rows) + list(pk_rows)),
        event_effective,
        event_classes,
        event_rows,
        final_counts,
        audit,
        manifest,
    )


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W66 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W66 candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    bundle = bundle or prepare(require_output_profiles=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W66 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W66 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W66 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W66 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W66 manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave66_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave66_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W66 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W66 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
        "dialogue_classifications": {
            name: [":".join((resource, *(str(value) for value in coordinate))) for resource, *coordinate in values]
            for name, values in bundle.dialogue_classifications.items()
        },
        "event_classifications": {name: list(values) for name, values in bundle.event_classifications.items()},
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=True)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_private_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
