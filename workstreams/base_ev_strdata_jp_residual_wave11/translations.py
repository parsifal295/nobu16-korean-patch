"""Source-free Korean targets for the safe base-event residual wave.

The values intentionally contain neither Japanese nor Han script.  Message
control spans are represented with Python escape sequences and are preserved
verbatim by the builder.
"""

from __future__ import annotations


# These 40 rows are the disjoint, contract-ready portion of the 45-row base
# event residual.  The source-free builder proves every value against the
# pinned stock source, the upstream target hash, and its control invariants.
TRANSLATIONS: dict[int, str] = {
    3207: "\x1bCA셋사이\x1bCZ는 양가에 재빨리 손을 써,\n\x1bCA이마가와 요시모토\x1bCZ·\x1bCA다케다 하루노부\x1bCZ·\x1bCA호조 우지야스\x1bCZ\n각각의 적자에게",
    3880: "\x1bCC아키\x1bCZ·\x1bCC이와미\x1bCZ에 세력을 넓힌 \x1bCB깃카와 씨\x1bCZ.\n본래 \x1bCB후지와라 씨\x1bCZ 출신으로, 가마쿠라 시대 중기에\n\x1bCC서국\x1bCZ으로 거점을 옮긴 무사단이었다.",
    4232: "\x1bCC기요스\x1bCZ는 일찍이 오와리 슈고쇼가 설치되어,\n\x1bCC교\x1bCZ·\x1bCC가마쿠라\x1bCZ 왕래로（\x1bCC도카이도\x1bCZ）와 \x1bCC이세 가도\x1bCZ의\n합류점이 되는 교통의 요충지였다.",
    4709: "\x1bCC가와나카지마\x1bCZ·\x1bCB다케다군\x1bCZ 본진――",
    4817: "\x1bCC오와리\x1bCZ·\x1bCC기요스성\x1bCZ――",
    5227: "\x1bCA나가요시\x1bCZ·\x1bCA히사히데\x1bCZ는 젊은 \x1bCA요시쓰구\x1bCZ의 권위를 위협하는 존재가\n되기 전에, \x1bCA후유야스\x1bCZ를 없애버린 것이다…",
    5279: "뭣이, 고쇼가！？\n…이놈, \x1bCB미요시\x1bCZ·\x1bCB마쓰나가\x1bCZ의 어리석은 자들이!",
    5640: "\x1bCC갓산토다성\x1bCZ은 일찍이 \x1bCB오우치\x1bCZ·\x1bCB모리\x1bCZ 등의\n공격을 여러 차례 물리친 견고한 성이었으나\n지금 바야흐로 함락의 위기에 처해 있었다.",
    5741: "\x1bCA우지야스\x1bCZ의 반대를 무릅쓰고,\n\x1bCA우지테루\x1bCZ·\x1bCA우지쿠니\x1bCZ 등은 성을 나와 \x1bCB다케다군\x1bCZ을 추격.\n하지만, 바로 이것이 \x1bCA[bm1251]\x1bCZ의 함정이었다.",
    5744: "\x1bCA우지테루\x1bCZ·\x1bCA우지쿠니\x1bCZ는 패잔병을 모아 \x1bCC오다와라\x1bCZ로\n귀환. 그곳에 \x1bCA우지마사\x1bCZ의 원정대도 도착했다.",
    5778: "\x1bCB오다 가문\x1bCZ·\x1bCA오다 노부나가\x1bCZ거성―",
    5863: "\x1bCB류조지 가문\x1bCZ·\x1bCA류조지 다카노부\x1bCZ거성―",
    5866: "이대로 우리가 영지를 넓히면\n\x1bCC지쿠젠\x1bCZ·\x1bCC지쿠고\x1bCZ을 침범함은 필연.\n결판을 낼 수밖에 없을 것이오!",
    5885: "\x1bCC아네가와\x1bCZ에서 격돌한 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ의 연합군과\n\x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ의 연합군의 싸움은,\n초반부터 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 측이 우세하였다.",
    5895: "\x1bCC아네가와 결전장\x1bCZ·\x1bCB오다군\x1bCZ 본진―",
    5952: "（\x1bCB아사쿠라\x1bCZ·\x1bCB아자이\x1bCZ에 이어, \x1bCB혼간지\x1bCZ까지 등을 돌리다니.\n　장군으로서 나의 권위가 낮은 것인가,\n　아니면 \x1bCA노부나가\x1bCZ의 인망이 없어서인가…）",
    6155: "\x1bCC하마마쓰성\x1bCZ·성 밖―",
    6428: "\x1bCC오코성\x1bCZ·곳간 주변――",
    6455: "\x1bCB오다 가문\x1bCZ·\x1bCA[b754]\x1bCZ거관―",
    6531: "\x1bCB오다 가문\x1bCZ·\x1bCA노부나가\x1bCZ거성――",
    6587: "\x1bCA우지쿠니\x1bCZ는 출가하고,\n\x1bCA우지노리\x1bCZ·\x1bCA우지나오\x1bCZ는 \x1bCC고야산\x1bCZ에서 칩거하게 된다.\n이로써 전국 다이묘·\x1bCB고호조씨\x1bCZ는 멸망했다.",
    6704: "\x1bCA오다 노부나가\x1bCZ로부터 재흥을 인정받아,\n\x1bCB모리\x1bCZ와 접하는 최전선의 \x1bCC고즈키성\x1bCZ을 맡은\n\x1bCA아마고 가쓰히사\x1bCZ·\x1bCA야마나카 시카노스케\x1bCZ 주종…",
    7166: "\x1bCC가스가야마\x1bCZ 성하·\x1bCA[b1672]\x1bCZ 저택―",
    7177: "\x1bCC하리마국\x1bCZ·\x1bCC고즈키성\x1bCZ을 함락시킨 \x1bCB오다가\x1bCZ에서는,\n새로운 성주를 누구로 할지,\n\x1bCA노부나가\x1bCZ와 중신들 사이에 논의가 오가고 있었다.",
    7240: "\x1bCB류조지\x1bCZ·\x1bCB시마즈\x1bCZ의 세력에 밀려 마침내\n본거지인 \x1bCC분고\x1bCZ까지 위협받는 사태에 이르자,\n\x1bCA[bm473]\x1bCZ는 관백 \x1bCA히데요시\x1bCZ에게 구원을 청했다.",
    7340: "\x1bCB오다 가문\x1bCZ·\x1bCA[bs754]\x1bCZ진중―",
    7442: "\x1bCA겐뇨\x1bCZ·\x1bCA뇨슌니\x1bCZ 부부를 비롯해 \x1bCB혼간지\x1bCZ의 주요\n인사들은 \x1bCC이시야마\x1bCZ를 떠나 \x1bCC기슈 사기노모리\x1bCZ로 향했다.\n그러나…",
    7649: "\x1bCA히데요시\x1bCZ·\x1bCA[bm826]\x1bCZ의 계책에 의한 수공으로\n\x1bCC다카마쓰성\x1bCZ은 궁지에 몰렸다. 마치 \x1bCB오다가\x1bCZ와\n\x1bCB모리가\x1bCZ의 관계를 은유하듯이…",
    7732: "\x1bCA오다\x1bCZ·\x1bCA[bs1871]\x1bCZ 연합군의 맹공으로,\n\x1bCB다케다가\x1bCZ는 완전히 붕괴했다.",
    7755: "\x1bCC다카마쓰성\x1bCZ·성 안―",
    7834: "\x1bCC야마자키\x1bCZ·\x1bCC덴노잔\x1bCZ 땅에서 맞선 \x1bCA미쓰히데\x1bCZ와 \x1bCA히데요시\x1bCZ는\n결전에 이르렀다. 기세가 앞선 \x1bCA히데요시\x1bCZ군이\n점차 \x1bCA아케치\x1bCZ의 군세를 압박해 갔다.",
    8249: "\x1bCC고마키야마\x1bCZ에서 대치한 \x1bCA[bs754]히데요시\x1bCZ군과\n\x1bCA오다 노부카쓰\x1bCZ·\x1bCA[b1871]\x1bCZ의 연합군―",
    8283: "\x1bCC고마키야마\x1bCZ 전선 이외에도 각지에서\n\x1bCA히데요시\x1bCZ 측, \x1bCA노부카쓰\x1bCZ·\x1bCA[bm1871]\x1bCZ 측의 군세가 충돌하였으나\n어느 쪽도 결정적인 승패는 나지 않았다.",
    8341: "\x1bCC셋쓰국\x1bCZ·\x1bCC이시야마 고보\x1bCZ.",
    9149: "\x1bCA모리 모토나리\x1bCZ의 아들이라 하면, 적남·\x1bCA다카모토\x1bCZ 외에\n\x1bCA깃카와 모토하루\x1bCZ·\x1bCA고바야카와 다카카게\x1bCZ 형제가 유명하지만\n그 외에도 자식을 두고 있었다.",
    9324: "\x1bCB아시카가 쇼군가\x1bCZ·\x1bCB간레이 호소카와 가문\x1bCZ 각각의 내분이\n오래 이어져 혼돈이 극에 달한 \x1bCC기나이\x1bCZ에서는\n새로이 \x1bCB미요시 가문\x1bCZ이 주가를 능가하는 힘을 지녔다.",
    9330: "\x1bCC동국\x1bCZ으로 눈을 돌리면, 서로 다투어 온\n\x1bCB이마가와\x1bCZ·\x1bCB다케다\x1bCZ·\x1bCB호조\x1bCZ의 유력 세 다이묘가,\n이해를 넘어 손을 잡으려 움직이기 시작하고 있었다…",
    9461: "\x1bCC다쓰노성\x1bCZ주·\x1bCA아카마쓰 마사히데\x1bCZ의 아들인 \x1bCA히로히데\x1bCZ는\n생애에 여러 차례 이름을 바꾼 것으로 알려져 있다.\n\x1bCA히로히데\x1bCZ·\x1bCA히로미치\x1bCZ·\x1bCA마사히로\x1bCZ 등…",
    9473: "\x1bCA다카마사\x1bCZ의 이복동생인 \x1bCA마고시로\x1bCZ와 \x1bCA기헤이지\x1bCZ 등\n다른 자식에게 자연히 애정이 옮겨 갔다.\n\x1bCA도시마사\x1bCZ·\x1bCA다카마사\x1bCZ 부자는 소원해져 갔다.",
    9708: "\x1bCA시바타 가쓰이에\x1bCZ·\x1bCA[b754]\x1bCZ 등 중신들도,\n\x1bCA노부나가\x1bCZ의 생환 소식을 받고,\n잇따라 \x1bCA미쓰히데\x1bCZ 토벌군에 참가했다.",
}


# These five rows are intentionally not written into the candidate.  Their
# rationale is surfaced in the source-free public hold artifact instead.
MANUAL_HOLD_IDS: tuple[int, ...] = (3917, 4835, 7260, 8818, 8904)
