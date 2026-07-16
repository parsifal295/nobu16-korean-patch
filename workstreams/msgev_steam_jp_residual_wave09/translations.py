"""Project-authored Korean replacements for the bounded Wave09 event delta.

This module intentionally contains no Japanese source text.  The builder pins
each source row with a UTF-16LE SHA-256 digest before the replacement is used.
"""

from __future__ import annotations


# Two already visible residual scene lines plus the contiguous Yasuke alternate
# Honnōji event sequence.  ID 10961 is intentionally absent: it was already
# Korean in the Wave08 baseline.
EVENT_STORY_IDS = (
    10959,
    10960,
    *range(10962, 11010),
)

# Event-list / branch-condition labels that remain Japanese in the same JP
# message resource.  These are deliberately held apart from story prose so
# the review surface remains bounded and auditable.
EVENT_LABEL_IDS = (
    *range(16437, 16449),
    16904,
    16905,
    17456,
    17833,
)


TARGET_TRANSLATIONS = {
    10959: "그렇다면 \x1bCA[bm1251]\x1bCZ이 진을 친 곳은 산 아래 \x1bCC하치만바라\x1bCZ…\n하지만 병력을 둘로 나누었다면\n\x1bCB다케다\x1bCZ의 본대는 빈틈이 많을 듯하옵니다.",
    10960: "여기서는 \x1bCA[bm1251]\x1bCZ의 계책을 역이용해\n우리 일행은 이 산을 내려간다!\n결코 적에게 눈치채게 하지 마라!",
    10962: "이국적인 풍모를 마음에 들어 한\n\x1bCA오다 노부나가\x1bCZ에게 직접 신변 경호의 임무를\n받고 있던 \x1bCA야스케\x1bCZ.",
    10963: "주군이 된 \x1bCA노부나가\x1bCZ의 원정에 수행한 그는,\n\x1bCA노부나가\x1bCZ의 숙소인 \x1bCC교토\x1bCZ·\x1bCC혼노지\x1bCZ에서\n경내를 순찰하고 있었다…",
    10964: "―덜컹!",
    10965: "뭐야, 돌바닥이 어긋나 있지 않은가!\n…고쳐 두자. 다른 사람이\n걸려 넘어져도 곤란하겠지.",
    10966: "돌바닥을 고치려던 \x1bCA야스케\x1bCZ가 판석을 들어내자\n그 판 모양 돌 뒤에는 깊은 굴이 있었다.\n굴은 꽤 깊어 지하로 이어지고 있다.",
    10967: "이런 곳에 굴이 있다니…\n설마…숨은 길?",
    10968: "―\x1bCA야스케\x1bCZ 님! 여기 계셨습니까!\n주군께서 부르십니다, 서둘러 본당으로!",
    10969: "뭐라고!\n즉시 가겠소!",
    10970: "（절에 숨겨진 굴이라니,\n\u3000정체가 궁금하지만…\n\u3000이 입구는 닫아 두도록 하자）",
    10971: "이튿날, 새벽의 \x1bCC혼노지\x1bCZ 문 앞―",
    10972: "새가 지저귀기 시작했군…\n야번도 슬슬 끝날 때가 되었나.",
    10973: "（그러고 보니,\n\u3000그 숨은 길은 어디로 이어져 있었을까…\n\u3000보물창고인가, 아니면 밖으로 빠져나가는 길인가）",
    10974: "불침번 근무가 끝날 무렵,\n생각에 잠긴 \x1bCA야스케\x1bCZ의 귀에 들려온 것은\n규칙적으로 행군하는 부대의 발소리였다.",
    10975: "병력이 \x1bCC교토\x1bCZ를 지날 예정은 없었는데…\n…설마 누군가의 배신인가!?\n한시라도 빨리 알려야 한다!",
    10976: "\x1bCC혼노지\x1bCZ, \x1bCA오다 노부나가\x1bCZ의 침소―",
    10977: "\x1bCA야스케\x1bCZ가 침소로 달려 들어갔을 때는 이미,\n마찬가지로 반란을 눈치챈 이들이\n\x1bCA노부나가\x1bCZ 곁에 모여 있었다.",
    10978: "오오, \x1bCA야스케\x1bCZ! 너도 들었느냐?\n쳐들어온 군의 깃발은 도라지 문양이야…\n…설마 \x1bCA미쓰히데\x1bCZ가 반란을 일으킬 줄이야, 방심했군!",
    10979: "이렇게 된 이상 어쩔 수 없습니다.\n무슨 수를 써서라도 포위를 뚫고\n\x1bCC오미\x1bCZ 방면으로 빠져나가야 합니다…",
    10980: "\x1bCC니조\x1bCZ 방면은 포위가 두터울 것입니다.\n돌파한다면 남문이―",
    10981: "착착 군의가 진행되는 가운데,\n\x1bCA야스케\x1bCZ는 홀로 망설이고 있었다.",
    10982: "（그 숨은 길의 존재를\n\u3000주군과 모두에게 알려야 할까）",
    10983: "（\x1bCA미쓰히데\x1bCZ 님의 주도면밀함은 주군께서 가장 잘 아신다…\n\u3000주군께서는 \x1bCA아케치\x1bCZ군의 포위를 돌파하는 것보다\n\u3000숨은 길로 탈출하는 길을 택하실 것이다. 하지만）",
    10984: "（그 길이 밖으로 이어진다는 증거는 없다.\n\u3000만약 막다른 길이라면, 이 선택은\n\u3000모두의 죽음을 확실하게 만들고 만다）",
    10985: "（완전한 도박이 된다.\n\u3000나는―）",
    10986: "（정체를 알 수 없는 숨은 길에\n\u3000모두의 목숨을 걸 수는 없다.\n\u3000전투 준비에 집중하자）",
    10987: "작전은 정리되었다!\n\x1bCA아케치\x1bCZ군의 포위만 뚫으면 우리가 이긴다…\n\x1bCA야스케\x1bCZ, 함께 가자!",
    10988: "\x1bCA노부나가\x1bCZ를 따라 밖으로 나온 \x1bCA야스케\x1bCZ의 귀에\n조금 전보다 커진 행군 소리가 들려온다.\n사투의 때가 바로 눈앞까지 다가왔다…",
    10989: "（운을 하늘에 맡길 뿐이다.\n\u3000여기서는 도박을 해 보는 수밖에 없다）",
    10990: "주군, 들어 주십시오!\n이 \x1bCC혼노지\x1bCZ 지하에는 숨은 길이 있습니다…\n운이 좋으면 밖으로 빠져나갈 수도 있을지 모릅니다.",
    10991: "뭐라고…?\n운, 운인가…",
    10992: "…좋다!\n네 운에 모든 것을 맡긴다!\n당장 안내하라!",
    10993: "\x1bCC혼노지\x1bCZ, 지하―",
    10994: "설마 절 지하에\n이렇게 긴 길이 있을 줄이야…",
    10995: "그러게 말입니다…\n전란이 끊이지 않는 \x1bCC교토\x1bCZ의 거리이기에\n만일의 탈출구를 마련해 둔 것이겠지요만…",
    10996: "다행히 숨은 길은 막다른 곳에 이르지 않고,\n구불구불하며 앞으로 이어지고 있었다.\n그리고…",
    10997: "주군, 여러분!\n이 굽이를 지나면 빛이 보입니다!",
    10998: "하하, 정말 포위 밖으로 나올 수 있었다니!\n이제 일단 죽을 고비는 벗어난 듯하구나…\n\x1bCA야스케\x1bCZ, 잘했다!",
    10999: "\x1bCA야스케\x1bCZ의 기지로 살아남은 \x1bCA노부나가\x1bCZ 일행.\n그들은 반역자 \x1bCA아케치 미쓰히데\x1bCZ에 맞서기 위해,\n\x1bCC교토\x1bCZ를 벗어나 본거지·\x1bCC아즈치성\x1bCZ으로 향했다…",
    11000: "\x1bCA아케치 미쓰히데\x1bCZ의 배신으로부터 며칠 뒤, \x1bCC아즈치성\x1bCZ―",
    11001: "주군! 무사히 여기까지 돌아오시다니!",
    11002: "하하, 마침내 하늘에게 버림받았다고 생각했지만,\n\x1bCA야스케\x1bCZ의 기지 덕을 봤다!\n…그래서, 정세는?",
    11003: "\x1bCA아케치\x1bCZ 님의 반란에서 며칠이 지나,\n\x1bCA오다 노부나가\x1bCZ가 죽었다는 풍문이\n영지 전역을 뒤덮고 있습니다.",
    11004: "\x1bCA하시바\x1bCZ 님, \x1bCA시바타\x1bCZ 님 같은 중신 여러분도\n주군을 찾기보다는 다음 천하를\n차지하려는 듯한 분위기라서…",
    11005: "됐다…\n그 \x1bCA미쓰히데\x1bCZ마저 배신했다.\n중신 따위 누구도 믿을 수 없다!",
    11006: "이제 이 땅은 사방 모두가 적이다!\n…\x1bCA야스케\x1bCZ, \x1bCA란마루\x1bCZ, \x1bCA야스히데\x1bCZ!\n여기서 다시 천하를 차지해 보이겠다!",
    11007: "하하!",
    11008: "\x1bCC아즈치성\x1bCZ으로 귀환한 \x1bCA노부나가\x1bCZ는,\n\x1bCA하시바\x1bCZ, \x1bCA시바타\x1bCZ 등 \x1bCB오다\x1bCZ의 옛 신하들을 버리고\n\x1bCA야스케\x1bCZ 등 소수의 가신만 거느린 채 독립을 선언했다.",
    11009: "\x1bCA하시바\x1bCZ, \x1bCA시바타\x1bCZ, \x1bCA아케치\x1bCZ 등 옛 중신을 물리치고\n본래의 천하를 되찾기 위한 싸움이,\n지금 막을 올린다…",
    16437: "「세키가하라 전투」에서 승리한 것은",
    16438: "동군",
    16439: "서군",
    16440: "「오사카 여름 전투」에서 승리한 것은",
    16441: "도쿠가와군",
    16442: "도요토미군",
    16443: "야스케는 숨은 길을",
    16444: "알리지 않았다",
    16445: "알렸다",
    16446: "이브라힘은 숨은 길을",
    16447: "알리지 않았다",
    16448: "알렸다",
    16904: "%s이(가) %s을(를) 보유하지 않음",
    16905: "철포가 전래되지 않음",
    17456: "철포 전래(철포 관련 정책과 특성이 해금)",
    17833: "%s과(와) 동맹·혼인 동맹·종속 관계",
}


TARGET_IDS = tuple(TARGET_TRANSLATIONS)

if TARGET_IDS != EVENT_STORY_IDS + EVENT_LABEL_IDS:
    raise RuntimeError("Wave09 translation IDs differ from their declared bounded scope")
