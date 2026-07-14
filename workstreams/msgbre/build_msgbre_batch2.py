#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 2 (IDs 129-250)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_msgbre_batch1 as shared  # noqa: E402


BATCH_ID = "msgbre_biographies_0129_0250.v0.2"
OVERLAY_NAME = "msgbre_ko_biographies_0129_0250.v0.2.json"
EVIDENCE_NAME = "alignment_evidence.v0.2.json"
REVIEW_NAME = "review_index.v0.2.json"
VALIDATION_NAME = "validation.v0.2.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 129
SCOPE_END = 250
NEXT_START_ID = 251

TRANSLATIONS: dict[int, str] = {
    129: "아키의 호족. 오우치 가문에서 이반해 아마고 가문과 손잡았다. 뒤에 오우치 요시오키의 명을 받은 스에 오키후사의 공격을 받고 모리 모토나리의 중재로 항복했다. 이후 오우치·모리 가문 편에 섰다.",
    130: "이마가와 가신. 이누이성주. 다하라 혼슈쿠 전투에서 공을 세웠다. 주가 멸망 뒤 다케다 가문을 섬겨 도쿠가와 가문과 싸웠다. 다케다 가문 멸망 뒤에는 호조 가문에 속해 사타케 가문과의 전투에서 공을 세웠다.",
    131: "아키의 호족. 오우치 가문에 속했다. 어린 시절 모리 다카모토와 함께 오우치 가문의 인질이 되어 친교를 맺었다. 뒤에 모리 가문이 오우치 가문에서 이반하자 행동을 함께했다.",
    132: "오우치 가신. 주가 멸망 뒤 모리 가문에 속했다. 아마고 가문 멸망 뒤 이즈모 갓산토다성의 성주 대리가 되어 야마나카 유키모리군을 격퇴했다. 뒤에 모토나리의 다섯째 아들 모토아키를 보좌해 이즈모를 다스렸다.",
    133: "다케다 가신. 주군 노부토라 추방에 관여했다. 이후 노부토라의 아들 신겐을 섬겨 이타가키 노부카타와 함께 숙로를 맡았다. 우에다하라 전투에서 무라카미 요시키요군과 격전을 벌이다 전사했다.",
    134: "아자이 가신. 아메노모리성주. 이름은 기요사다. 가이호 쓰나치카·아카오 기요쓰나와 함께 ‘가이·아카오·아메노모리 삼장’이라 불렸다. 아자이 가문 멸망 뒤 아메노모리 일족은 각지로 흩어졌다.",
    135: "아라키 무라시게의 친족으로 사촌이라는 설도 있다. 무라시게를 따라 오다 노부나가에게 모반해 거성 하나쿠마성에서 쫓겨났다. 뒤에 용서받아 도요토미 가신이 되었으나 히데쓰구 사건에 연좌되어 유배되었다.",
    136: "단바의 호족. 사이쿠조성주. 호방하고 용맹한 것으로 이름났다. 하타노 가문 멸망 뒤 아케치 미쓰히데의 출사 요청을 거절하고 대신 아들 우지키요를 보냈다. 우지키요는 야마자키 전투에서 전사했다.",
    137: "무라시게의 맏아들. 아버지가 노부나가에게 모반하자 아마가사키성에서 오다군과 싸웠으나 패했다. 뒤에 하시바 히데요시를 따라 시즈가타케 전투에 참가했으며, 부상한 뒤로는 다시 전장에 나가지 못했다고 한다.",
    138: "이케다 가신. 아리오카성주. 뒤에 오다 가문을 섬겨 셋쓰 경략을 맡았으나 혼간지·모리 가문과 손잡아 모반했다가 패해 달아났다. 이후 다인이 되어 리큐 칠철의 한 사람으로 꼽혔다.",
    139: "이토 가문의 근시. 1549년 이토·시마즈 양군이 대치하던 중 절기 행사가 열렸다. 이때 시마즈 측 주마 무사시와 벌인 스모에서 이긴 뒤 무사시의 목을 베었다고 한다.",
    140: "히젠의 호족. 히노에성주. 하루즈미의 적장자. 쇼군 아시카가 요시하루의 소반슈가 되었다. 류조지 다카노부와 항쟁했으나 거듭 패해 영지를 잃었다. 시가에 심취했다고 한다.",
    141: "하리마의 호족. 처음에는 셋쓰 아리마군에 살다가 뒤에 하리마로 옮겼다. 아리마 가문은 아리마군의 지토로 임명된 아카마쓰 요시스케를 시조로 하는 아카마쓰 가문의 방계다.",
    142: "히젠의 호족. 히노에성주. 시마바라반도를 중심으로 세력을 넓혀 아리마 가문의 최대 판도를 세웠다. 또 둘째 아들 스미타다를 오무라 가문에 입양시켜 화해하고 안정된 지배 체제를 확립했다.",
    143: "히젠의 호족. 히노에성주. 요시사다의 둘째 아들. 형 요시즈미가 죽은 뒤 가독을 이었다. 시마즈 가문과 손잡아 세력 회복을 꾀했으나 훗날 오카모토 다이하치 사건을 일으켜 가이에서 참수되었다.",
    144: "하리마의 호족. 시게노리의 아들. 도요토미 히데요시를 섬겨 주고쿠 공격과 규슈 정벌 등에 종군했다. 히데요시가 죽은 뒤 도쿠가와 이에야스를 섬겨 세키가하라 전투에 참가했고, 전후 셋쓰 산다 2만 석을 받았다.",
    145: "히젠 아리마번주. 하루노부의 아들. 오카모토 다이하치 사건으로 아버지가 처형되었으나 도쿠가와 이에야스의 양녀를 아내로 맞았기에 용서받고 가독을 이었다. 뒤에 휴가 노베오카 5만 석으로 전봉되었다.",
    146: "도요토미 가신. 노리요리의 적장자. 히데요시가 죽은 뒤 도쿠가와 이에야스에게 속해 세키가하라 전투와 오사카 전투에서 공을 세우고 지쿠고 구루메 21만 석을 받았다. 시마바라의 난 진압에도 공을 세웠다.",
    147: "모리 가신. 모토나리를 섬겨 수많은 전투에서 공을 세웠다. 다카모토의 신임을 얻어 측근이 되었고 오봉행의 한 사람으로 내정을 보좌했다. 모리 18장에도 꼽힌다.",
    148: "와카사 다케다 가신. 야마우치성주. 이에나가의 아들. 부교를 맡았고 노부토요·요시즈미 두 대를 사무라이 대장으로 섬겼다. 에이로쿠 연간인 1558~1570년에 각지를 전전하며 활약했다.",
    149: "와카사 다케다 가신. 구니요시성주. 뒤에 오다 노부나가에게 속해 각지를 전전했다. 옛 주군 모토아키가 칩거를 명받자 노부나가에게 사면을 탄원했다. 혼노지의 변 뒤 도요토미 히데요시에게 속했다.",
    150: "모리 가신. 다케다 노부시게의 아들. 다케다 가문 멸망 때 달아나 출가한 뒤 외교승으로 활동했다. 오다 노부나가와 도요토미 히데요시의 앞날을 예언한 일로 유명하다. 세키가하라 전투에서 서군에 속해 전후 참수되었다.",
    151: "히야마 안도 가문 제8대 당주. 기요스에의 적장자. 미나토·히야마 두 안도 가문을 통일하고 능숙한 전략으로 가문 최대 판도를 세웠다. ‘북두성이 북천에 자리한 듯하다’라는 평을 들을 만큼 두려움을 샀다.",
    152: "히야마 안도 가문 제9대 당주. 지카스에의 적장자. 아버지가 죽은 뒤 가독을 이었다. 난부·도자와 가문과 항쟁하며 영지를 지켰으나 세키가하라 전투에서의 실책으로 아키타 영지에서 쫓겨났다.",
    153: "히야마 안도 가문 제7대 당주. 1550년 가키자키 스에히로와 아이누인의 화친 협정을 중재하려 에조치로 건너갔다. 이를 계기로 히야마 안도 가문의 에조 지배 체제가 확립되었다.",
    154: "히야마 안도 가문 제6대 당주. 다다스에의 아들. 1514년 가키자키 미쓰히로의 마쓰마에 슈고직을 추인했다. 동시에 ‘도카이 쇼군’ 등의 칭호를 쓰기 시작해 에조 지배권을 대내외에 내세웠다.",
    155: "미나토 안도 가문 제10대 당주. 시게스에의 적장자. 아버지가 죽은 뒤 숙부 지카스에에게 미나토성에서 쫓겨나 도시마성으로 옮겨졌다. 지카스에가 죽은 뒤 도자와 가문과 손잡아 모반했으나 실패했다.",
    156: "미나토 안도 가문 제9대 당주. 기요스에의 셋째 아들. 안도 다카스에의 양자였던 형 도모스에가 죽자 자신이 다카스에의 양자가 되어 가독을 이었다. 가키자키 스에히로의 여섯째 딸을 아내로 맞았다.",
    157: "미나토 안도 가문 제7대 당주. 노부스에의 아들. 아버지가 죽은 뒤 가독을 이었고 간레이 호소카와 가문의 집사에게 ‘긴조쇼슈’로 대우받았다. 아들이 없어 사위 기요스에의 셋째 아들 시게스에를 양자로 삼았다.",
    158: "사이토 가신. 미노 삼인중의 한 사람. 주가 멸망 뒤 오다 노부나가에게 속했으나 훗날 추방되었다. 혼노지의 변을 틈타 옛 영지를 되찾으려 거병했지만 이나바 잇테쓰와 싸우다 패사했다.",
    159: "도쿠가와 가신. 고마키 나가쿠테 전투에서 이케다 쓰네오키와 모리 나가요시를 죽이는 전공을 세웠다. 도쿠가와 이에야스의 측근이 되었고, 이에야스의 열째 아들 요리노부의 쓰케가로로 오사카 전투에 출진해 여러 군을 통제했다.",
    160: "호조 가신. 출납 관련 부교 등을 맡아 가문의 정무를 이끈 핵심 인물이 되었다. 호조 가문 영지의 공정 도량형인 ‘안도마스’를 고안하는 등 주가의 발전에 크게 공헌했다.",
    161: "야마노우치 우에스기 가신. 고즈케 우스이군을 다스린 고쿠진. 안나카성과 마쓰이다성을 거성으로 삼았으나 다케다 신겐의 고즈케 침공군에 항복했다. 뒤에 적장자 가게시게에게 가독을 넘기고 은거했다.",
    162: "아자이 가신이자 오미의 호족. 아자이 나가마사와 오다 노부나가의 누이 이치의 혼인을 중개했다. 아네가와 전투에서 오다 가문의 포로가 되었으나 아자이군을 추격하는 잘못을 진언해 풀려났다.",
    163: "기모쓰키 가신. 오스미 이루후네성주. 시마즈 요시히사군이 공격하자 거성에 농성해 맞섰다. 그러나 주가의 원군이 오지 않아 1년 3개월에 걸친 농성 끝에 시마즈군에 항복했다.",
    164: "이마가와 가신. 나오모리의 딸. 이이 가문의 당주가 잇달아 죽어 뒤를 이을 남자가 끊기자 당주가 되었다. 평생 남편을 맞지 않았고, 뒤에 이이 나오마사를 양자로 삼아 가문을 잇게 했다.",
    165: "도쿠가와 가신. 나오마사의 둘째 아들. 병약한 형 나오카쓰를 대신해 가독을 잇고 오미 히코네 번주가 되었다. 오사카 여름 전투에 참가해 조소카베 모리치카군과 기무라 시게나리군을 격파했다.",
    166: "도쿠가와 가신. 나오마사의 맏아들. 이에야스의 명으로 히코네성을 쌓아 본거지로 삼았다. 병약했기에 본가 가독은 동생 나오타카에게 넘겼고, 자신은 분가를 세워 고즈케 안나카를 다스렸다.",
    167: "이마가와 가신. 이이노야성주. 나오모리의 양자. 나오모리가 죽자 가독을 이었으나 주군 우지자네에게 모반 혐의를 받아 살해되었다. 아들 나오마사는 뒤를 이은 이이 나오토라가 길렀다.",
    168: "도쿠가와 가신. 도쿠가와 사천왕의 한 사람. 군장을 붉은색으로 통일한 부대는 ‘붉은 귀신’이라 두려움을 샀고 늘 선봉을 다퉜다. 세키가하라 전투에서는 시마즈군을 추격해 시마즈 도요히사를 죽였다.",
    169: "이마가와 가신. 이이노야성주. 시바 가신 오코치 사다쓰나에게 호응해 미타케성에 농성했으나 아사히나 야스모치군의 공격으로 함락되었다. 이후 이마가와 가문에 속했고 오케하자마 전투에서 전사했다.",
    170: "이마가와 가신. 가타쓰라의 아들. 부젠노카미라 칭했다. 하시바 히데요시의 첫 주군으로 알려진 마쓰시타 가헤에 등을 요리키로 거느렸다고 한다. 오케하자마 전투에 종군해 전사했다.",
    171: "이마가와 가신. 히쿠마성주. 오케하자마 전투 뒤 도쿠가와 가문으로 돌아서 주군 우지자네의 공격을 받고 패한 뒤 화해했다. 훗날 우지자네의 부름으로 슨푸성에 갔다가 그곳에서 모살되었다.",
    172: "이이자카 무네야스의 딸이자 다테 히데무네의 어머니. 다테 마사무네의 눈에 들어 측실이 되었다. 부채로 쥐를 쫓는 모습이 고양이 같아 ‘네코 고젠’이라 불렸다.",
    173: "도요토미 가신. 이름은 나오카게. 가토 기요마사 휘하의 사무라이 대장이었다. 가토 가문 삼걸의 한 사람이자 일본 7창에도 꼽혔다. 토목과 축성 기술에 정통해 구마모토성 축조에도 참여했다.",
    174: "오우치 가신. 부교를 맡아 주로 규슈 방면에 주둔했다. 스에 하루카타의 모반에 동조했고 주군 요시타카가 죽은 뒤 주가를 이은 요시나가를 섬겼다. 기마 궁술의 예법에 정통했다.",
    175: "비젠의 호족. 고쿠라성주. 우키타 나오이에에게 신종해 두각을 나타냈고, 나오이에가 오다 편에 서자 모리군을 맞아 크게 이겼다. 그러나 히사타카의 세력을 경계한 누군가에게 모살되었다.",
    176: "가토 기요마사 가신. 처음에는 우에스기 겐신을 섬겼으나 쇼바야시 가즈타다에게 무용을 인정받아 기요마사를 섬겼다. 선봉 공 한 번에 500석을 받기로 하고 일곱 번 선봉에 서서 3천 석을 받았다.",
    177: "하타케야마 가신. 도시요리슈를 맡았다. 주군 요시쓰나가 노토에서 추방되자 따랐다. 요시쓰나의 노토 귀환 작전을 이끌며 군세를 지휘해 선전했으나 실패로 끝났다.",
    178: "쓰네오키의 맏딸. 모리 나가요시에게 시집갔다. 시즈가타케 전투의 기후성 공격에서 철포대를 이끌고 공성전에 참가했다고 한다. 나가요시가 전사한 뒤 유언에 따라 친정으로 돌아가 나카무라 가즈우지와 재혼했다.",
    179: "데루마사의 넷째 아들. 어머니는 도쿠가와 이에야스의 딸 도쿠히메다. 조카마치와 교통망을 정비했다. 6만 8천 석을 다스리고 시종까지 올랐으나 가문에서 이케다 소동이 일어나 영지를 몰수당했다.",
    180: "오다 가신. 쓰네오키의 둘째 아들. 혼노지의 변 뒤 도요토미 가문에 속해 각지에서 활약했다. 세키가하라 전투에서는 동군에 속했고, 전후 하리마 히메지 52만 석을 받아 ‘히메지 재상’이라 불렸다.",
    181: "도시타카의 적장자. 도쿠가와 이에미쓰에게 이름 한 글자를 받았다. 비젠 오카야마 31만 석의 번주로, 유학을 장려해 학교를 세우고 영민의 생활 향상에 힘써 오카야마번의 기틀을 다진 명군이다.",
    182: "오다 가신. 노부나가의 젖형제. 아네가와 전투 등에서 활약했다. 혼노지의 변 뒤 오다 가문 네 숙로의 한 사람이 되었다. 하시바 히데요시 편에 서서 고마키 나가쿠테 전투에 출진했다가 전사했다.",
    183: "시모쓰마 라이류의 맏아들. 어머니 시치조는 이케다 쓰네오키의 양녀다. 처음에는 혼간지 교뇨를 섬겼으나 출분해 숙부 이케다 데루마사를 섬기면서 이름을 이케다 시게토시로 바꿨다. 오사카 전투에서 공을 세웠다.",
    184: "셋쓰의 호족. 이케다성주. 나가마사의 아들. 오다 노부나가의 긴키 평정군에 항복해 이타미·와다 가문과 함께 ‘셋쓰 삼수호’라 불렸으나 미요시 가문과 내통한 일족에게 추방되었다.",
    185: "셋쓰의 호족. 호소카와 하루모토에게 중용되고 쇼군가에서도 후대받았다. 미요시 나가요시가 호소카와 우지쓰나를 옹립해 하루모토와 대립하자 우지쓰나 편에 섰으나 패해 하루모토의 명으로 자결했다.",
    186: "데루마사의 다섯째 아들. 어머니는 도쿠가와 이에야스의 딸 도쿠히메다. 형 다다쓰구가 죽을 때 3만 5천 석을 나눠 받아 하리마 아코번을 세웠다. 번정의 기틀을 다졌으나 젊어서 죽었다.",
    187: "다이호지 가신. 데와 아사히야마성주. 다이코 검지에 반대한 농민 봉기에 가담해 천하에 맞서는 악당을 자처하며 ‘아쿠지로’라 칭했다. 치수와 개간에 힘써 백성들의 사랑을 받았다.",
    188: "셋쓰의 호족. 이케다성주. 나가마사의 아들. 형 가쓰마사를 추방하고 가독을 이었다. 미요시 삼인중과 손잡아 오다 노부나가와 적대했으나 뒤에 항복했고 셋쓰를 지배한 아라키 무라시게에게 속했다.",
    189: "데루마사의 셋째 아들. 어머니는 도쿠가와 이에야스의 딸 도쿠히메다. 형 다다쓰구가 죽자 가독을 이어 비젠 오카야마번 제2대 번주가 되었다. 오카야마성을 개수해 방비를 굳히고 조카마치를 정비했다.",
    190: "쓰네오키의 셋째 아들이자 데루마사의 동생. 히데요시의 양자로서 도요토미 가문의 천하 통일 사업에 힘을 보탰다. 세키가하라 전투에서는 동군에 속해 공을 세웠고 이에야스에게 영지를 더 받아 이나바 돗토리 번주가 되었다.",
    191: "나가요시의 맏아들. 어릴 때부터 노신 미즈노 젠에몬의 가르침을 받았다. 가독을 이어 이나바 돗토리 번주가 되었고 뒤에 빗추 마쓰야마로 전봉되었다. 신전 개발에 힘썼다.",
    192: "셋쓰의 호족. 이케다성주. 노부마사의 아들. 아버지가 호소카와 하루모토의 명으로 자결한 뒤 가독을 이었다. 미요시 나가요시에게 속해 하타노·가와치 하타케야마 가문과의 전투에서 공을 세웠다.",
    193: "도쿠가와 가신. 데루마사의 적장자. 아버지가 죽은 뒤 하리마 히메지 52만 석을 이었으나 다스린 지 불과 3년 만에 급사했다. 계모 도쿠히메가 친아들 다다쓰구를 후계자로 세우려고 독살했다는 설이 있다.",
    194: "도요토미 가신. 다카마쓰번 제2대 번주. 지카마사의 아들. 처음에는 오다 노부나가를 섬겨 사이카 공격에서 공을 세웠다. 세키가하라 전투 때 아버지는 서군, 자신은 동군에 속해 이코마 가문의 존속을 꾀했다.",
    195: "도요토미 가신. 사누키 다카마쓰 17만 석을 다스렸다. 주군 히데요시가 죽은 뒤 삼중로의 한 사람이 되었다. 세키가하라 전투에서 서군에 속했으나 아들 가즈마사가 동군에 속해 영지 몰수를 면했다.",
    196: "가즈마사의 맏아들. 아버지가 죽은 뒤 가독을 이어 사누키 다카마쓰번 17만 1천 석의 제2대 번주가 되었다. 오사카 전투에는 유격군으로 참가했다. 정실은 도도 다카토라의 양녀다.",
    197: "도요토미 가신. 이에나가의 아들. 어려서부터 히데쓰구를 가까이 모셨고 히데쓰구가 죽은 뒤에는 히데요시를 섬겼다. 세키가하라 전투에서 동군에 속해 후쿠시마 마사노리 휘하로 싸웠고, 뒤에 마쓰다이라 다다요시의 가신이 되었다.",
    198: "오슈 시바 가신. 아키타카의 셋째 아들. 아버지가 시즈쿠이시 지방을 공략할 때 이사리관주가 되어 이사리 고쇼라 칭했다. 시바 가문이 멸망할 때 이사리관은 난부 노부나오에게 함락되었다.",
    199: "아와의 호족. 하시바 히데요시의 시코쿠 정벌 뒤 아와에 들어온 하치스카 이에마사에 반대하는 봉기 등을 진압했다. 그 공을 인정받아 요가시라 쇼야에 임명되었다.",
    200: "난부 가문 제22대 당주 난부 마사야스의 넷째 아들. 형 난부 야스노부에게 이시가메 땅을 받아 이시가메 성씨를 썼다. 고즈카타성주를 맡아 남쪽의 시바 가문에 대비했다.",
    201: "도쿠가와 가신. 가즈마사의 숙부. 미카와 잇코잇키 평정전에서 공을 세웠다. 이마가와 가문 멸망 뒤 가케가와성주가 되었고 만년에는 미노 오가키 5만 석을 다스렸다. 이에야스를 향한 충성이 둘도 없다는 평을 받았다.",
    202: "빗추의 호족. 다카야마성주. 히사토모의 아들. 아버지가 죽은 뒤 가독을 이었다. 매형 미무라 모토치카를 도와 모리군과 싸웠으나 패했다. 재흥을 꾀하다 모리군의 공격을 받고 자결했다.",
    203: "빗추의 호족. 다카야마성주. 미무라 모토치카를 따라 묘젠지 전투에 참가했으나 우키타 나오이에군에 패해 부상한 뒤 죽었다. 이시카와 가문은 기비쓰 신사의 사무다이를 기반으로 성장한 호족이다.",
    204: "이가 닌자. 모모치 산다유의 부장이었다고 한다. 도요토미 히데요시를 암살하려 오사카성에 침입했으나 명물 ‘지도리 향로’가 울어 실패했다. 가마솥에 삶는 형벌을 받았다고 한다.",
    205: "도요토미 가신. 가즈마사의 둘째 아들. 오사카 전투에서 오사카성에 농성했다. 사나다마루 전투에서 실수로 화약을 터뜨렸고, 이를 신호로 착각해 몰려든 도쿠가와군은 사나다 유키무라에게 격퇴되었다.",
    206: "도쿠가와 가신. 가즈마사의 아들. 아버지를 따라 주가에서 출분해 도요토미 가문에 속했다. 아버지가 죽은 뒤 시나노 마쓰모토 6만 석을 이었다. 세키가하라 전투에서 동군에 속했으나 뒤에 영지 은닉죄로 영지를 몰수당했다.",
    207: "난부 가신. 난부 마사야스의 둘째 아들. 쓰가루 군다이로서 조카 하루마사를 보좌해 난부 가문의 세력 확대에 크게 공헌했다. 뒤에 가신 오우라, 곧 쓰가루 다메노부의 모반으로 자결했다.",
    208: "난부 가문 제26대 당주. 이시카와 다카노부의 아들. 하루쓰구가 죽은 뒤 벌어진 가문 소동에서 승리해 가독을 이었다. 구노헤 마사자네의 난 등으로 고전했으나 도요토미 히데요시에게 접근해 영내를 통일했다.",
    209: "도쿠가와 가신. 가로를 맡아 니시미카와슈를 이끌고 활약했다. 고마키 나가쿠테 전투 뒤 도요토미 가문으로 출분했다. 그 때문에 도쿠가와 가문은 미카와 이래의 군제를 다케다류로 바꾸게 되었다.",
    210: "도쿠가와 가신. 오쿠보 다다치카의 둘째 아들. 외조부 이시카와 이에나리의 양자가 되어 이시카와 가문을 이었다. 아버지 다다치카의 실각에 연좌되었으나 오사카 전투 때 용서받아 출진해 분전했다.",
    211: "잇시키 가신. 가야성주. 주군 요시키요의 권력이 약해졌을 때 실권을 쥔 삼봉행의 한 사람이다. 잇시키 구로를 옹립해 내란을 일으킨 노베나가 하루노부에게 한때 패했으나 반격해 격퇴했다.",
    212: "고노 가신. 다카토게성주. 빗추노카미라 칭했다. 한때 미요시 가문에 속해 선봉을 맡았으나 고노 가문의 공격에 패해 항복했다. 뒤에는 조소카베 모토치카의 이요 침공군에 항복했다.",
    213: "도요토미 가신. 세키가하라 전투에서 동군으로 싸워 첫 수급을 얻는 등 분전했다. 이후 히데요리를 섬겼으나 오사카 겨울 전투 직전 고야산에 들어갔다. 주가 멸망 뒤 도쿠가와 가문을 섬겼다.",
    214: "도요토미 가신. 오와리 이누야마성주를 맡았다. 세키가하라 전투에서 서군에 속해 용감히 싸웠다. 전후 영지를 잃었으나 죽음은 면했다. 뒤에 삭발해 소린이라 칭하고 교토에서 금융업을 했다.",
    215: "난부 가문 제27대 당주. 노부나오의 아들. 아버지가 죽은 뒤 가독을 이었다. 세키가하라 전투에서 동군에 속해 모가미 가문을 구원했다. 영내 봉기를 진압하는 등 난부번의 기초를 세웠다.",
    216: "도요토미 가신. 오봉행의 한 사람으로 국정에 참여했다. 주군 히데요시가 죽은 뒤 서군을 지휘해 세키가하라에서 도쿠가와 이에야스와 싸웠으나 여러 장수를 통제하지 못해 패했고 교토에서 참수되었다.",
    217: "미쓰나리의 아들. 세키가하라 전투 때 인질로 오사카성에 머물렀다. 전후 교토 주쇼인에 들어가 삭발했고, 주쇼인 주지의 구명 탄원으로 용서받았다. 뒤에 주쇼인 제3대 주지가 되었다.",
    218: "미쓰나리의 둘째 아들. 세키가하라 전투 뒤 쓰가루 노부타케의 도움으로 쓰가루에 달아나 스기야마 겐고로 이름을 바꾸고 칩거했다. 쓰가루 가문을 섬겼다는 설도 있으며 자손은 그 가문의 중신으로 이어졌다.",
    219: "미쓰나리의 아버지. 문무에 뛰어나고 일본과 중국 학문에 정통한 재인으로 전해진다. 사와야마성 성주 대리를 맡아 미쓰나리를 보좌했으나 세키가하라 전투 뒤 동군의 공격으로 성이 함락되자 자결했다.",
    220: "도요토미 가신. 세키가하라 전투 때 아버지 마사쓰구와 함께 동생 미쓰나리의 거성 사와야마성을 지켰다. 서군 패배 뒤 고바야카와 히데아키 등의 공격을 받아 성이 함락되자 일족과 함께 자결했다.",
    221: "오스미의 호족. 오바마성주. 기모쓰키 가문과 손잡아 시마즈 가문에 맞섰으나 시마즈군에 거성을 빼앗겨 항복했다. 이후 시마즈 가문에 속해 오토모 가문 공격 등에 종군했다.",
    222: "벳쇼 가신. 주군 나가하루와 함께 미키성에 농성해 하시바 히데요시와 싸우며 하시바 가신 후루타 시게노리를 죽이는 등 활약했다. 나가하루가 죽은 뒤 히데요시에게 속했고, 훗날 마에다 도시이에를 섬겼다.",
    223: "호조 가신. 오우마와리슈의 한 사람이자 효조슈를 맡았다. 주군 우지나오가 상락 약속을 어겼을 때 변명하려 도요토미 히데요시를 찾아갔다. 주가 멸망 뒤 도쿠가와 이에야스를 섬겼다.",
    224: "시마즈 가신. 다다아키의 아들. 아버지와 함께 오스미 가지키성주 기모쓰키 가네히로를 공격해 항복시키고 그 영지의 처리를 맡았다. 뒤에 로주가 되어 주가의 세력 확대에 공헌했다.",
    225: "시마즈 가신. 다다쿠라의 아들. 로주를 맡았다. 도요토미 히데요시의 규슈 정벌군에 패해 인질이 되었다. 히데요시에게 주가와 동격의 대우를 받은 탓에 주군 다다쓰네와 대립해 살해되었다.",
    226: "시마즈 가신. 지략과 무용이 뛰어나 주가의 사쓰마 통일에 공헌했다. 오스미 가지키성 공격에서 일본 최초로 철포를 실전에 사용했다. 뒤에 로주가 되어 국정에 참여했다.",
    227: "도쿠가와 가신. 무가제법도 등의 법령 제정을 맡았다. 호코지 종명 사건을 일으켜 오사카 전투의 구실을 만드는 등 책략에서도 활약해 ‘검은 옷의 재상’이라 불렸다.",
    228: "소마 가신. 이즈미다성주. 1588년 수비하던 오고에성에 쳐들어온 다테 마사무네군을 격퇴하는 등 주군 요시타네를 따라 다테 가문과 공방을 거듭했다.",
    229: "난부 가신. 이시가메 노부후사의 아들 마사아키의 아들. 숙부 이즈미야마 야스마사의 양자가 되어 산노헤향 이즈미야마촌을 다스리고 이즈미야마 성씨를 썼다. 딸 지쇼인은 뒤에 주군 노부나오의 후실이 되었다.",
    230: "난부 가신. 후루야스의 적장자. 누이는 주군 노부나오의 후실 지쇼인이다. 뒤에 이시가메 가문이 끊기자 이시가메 성씨를 썼다. 노부나오의 처남으로 난부번 중신 20명에 들었다.",
    231: "센고쿠 시대의 여성으로 가부키 춤의 시조다. 이즈모타이샤의 무녀를 자처하며 교토에서 염불춤을 공연해 인기를 끌었다. 만년에는 이즈모국에서 비구니가 되었다고 하나 수수께끼가 많다.",
    232: "시마즈 가신. 유소쿠 고지쓰를 전수받았다. 시마즈 요시히로 휘하에서 많은 공을 세웠고 세키가하라 전투에서는 이나즈 시게마사와의 싸움에서 활약했다. 수석 가로를 맡아 시마즈 다다쓰네가 참근할 때마다 반드시 수행했다.",
    233: "아자이 가신. 사와야마성주. 아네가와 전투에서 선봉을 맡아 분전했다. 뒤에 오다 노부나가에게 항복해 신조성주가 되었으나 노부나가의 노여움을 사 영지를 몰수당하고 고야산으로 출분했다.",
    234: "안도 가신. 지카스에의 직신. 안도 가문에 반기를 든 오다테성주 아사리 가쓰요리가 싸움에 패해 거성을 넘긴 뒤 오다테성에 들어가 히나이 대관이 되었다.",
    235: "아키즈키 가신. 지카유키의 아들. 젊어서부터 무용이 높다는 평을 받았다. 오토모 가문과의 전투에서 총대장으로 임명되어 용감히 출진했으나 적을 깊이 추격하다 복병의 습격을 받아 전사했다.",
    236: "아키즈키 가신. 사마노스케라 칭했다. 아들 지카우지가 오토모군에 죽자 불단 기둥에 와카 한 수를 적어 아들의 영혼에 바쳤다. 뒤에 어느 전투에서 선진을 맡아 전사했다.",
    237: "다케다 가신. 주군 노부토라 추방에 관여했다. 이후 노부토라의 아들 신겐을 섬겨 각지의 전투에서 활약했다. 우에다하라 전투에서 선봉을 맡아 무라카미 요시키요군과 격전을 벌이다 전사했다.",
    238: "도쿠가와 가신. 처음에는 승려였으나 아버지와 동생이 죽자 환속해 가독을 이었다. 슨푸와 에도의 마치부교를 맡은 뒤 교토 쇼시다이가 되어 서국의 여러 다이묘를 감시했다.",
    239: "호조 가신. 유히쓰와 효조슈를 맡았다. 도쿠가와 이에야스와의 화평 교섭, 도요토미 히데요시와의 절충 등 대외 교섭에서 수완을 발휘했다. 주가 멸망 뒤 히데요시의 오토기슈로 섬겼다.",
    240: "이마가와 가신. 이타미성주 마사오키의 아들. 어린 시절 스루가로 달아나 이마가와 가문을 섬겼다. 우지자네 시대에는 해적부교를 맡았다. 주가 멸망 뒤에는 다케다·도쿠가와 가문에서 선박부교를 맡았다.",
    241: "깃카와 가신. 아버지 깃카와 쓰네요와 함께 모리 모토나리의 둘째 아들 모토하루가 깃카와 가문을 잇도록 힘썼다. 뒤에 모리 가문에 속했고, 오우치 가문 멸망 뒤 야마구치 부교로 보초 두 구니의 여러 정무를 맡았다.",
    242: "오사키 가신. 이치쿠리성주. 가사이·오사키 봉기 때 거성에 농성해 끝까지 분전했다. 봉기 진압 뒤 모가미 가문을 섬겨 쓰루오카성 수비대장을 맡았으나 모반을 일으켜 죽임을 당했다.",
    243: "오사키 가신. 이치쿠리성주. 이치쿠리 다카하루의 조부라고 한다. 1591년 가사이·오사키 봉기 때 92세의 고령에도 거성에 농성해 싸웠으나 패해 전사했다.",
    244: "도사 이치조 가문 제5대 당주. 후사모토의 아들. 밤낮으로 주색에 빠져 살다가 가신들에게 추방되었다. 뒤에 오토모 소린의 후원을 받아 옛 영지를 되찾으려 했으나 실패했다.",
    245: "다케다 신겐의 이복동생. 가이 우에노성주. 가이 겐지의 흐름을 잇는 이치조 가문의 명적을 이었다. 신겐의 유언에 따라 가쓰요리의 후견인을 맡아 쇠퇴하는 다케다 가문에 끝까지 충성을 다했다.",
    246: "도사 이치조 가문 제6대 당주. 가네사다의 적장자. 아버지를 추방한 조소카베 모토치카에게 옹립되어 꼭두각시 당주가 되었다. 조소카베 가신 나미카와 기요무네의 모반에 가담해 이요국으로 추방되었다.",
    247: "도사 이치조 가문 제2대 당주. 간파쿠 이치조 노리후사의 둘째 아들. 고쿠진슈의 탄원으로 원복을 치르고 다이묘가 되었다. 모토야마 가문에 쫓긴 조소카베 구니치카를 보호하고 그 재흥에 힘썼다.",
    248: "도사 이치조 가문 제4대 당주. 후사후유의 아들. 히메노노성주 쓰노 모토타카를 죽이고 오히라 가문의 거성 도사 하스이케성을 빼앗는 등 세력을 넓혔으나 돌연 자결했다. 광기 때문이었다고 한다.",
    249: "후사이에의 둘째 아들이자 이치조 가네사다의 양부. 간파쿠에 취임했다. 후사모토와 가네사다가 어린 나이에 도사 이치조 가문을 이었기에 도사로 내려가 직접 정무를 맡았다.",
    250: "도사 이치조 가문 제3대 당주. 후사이에의 아들. 가신의 참소를 믿고 후견인 시키지 후지야스에게 자결을 명했다. 후지야스의 결백을 알고 사면 사자를 보냈으나 이미 자결한 뒤였다고 한다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    130: ["tahara_honshuku_battle_reading_requires_glossary_review"],
    134: ["collective_epithet_rendering_requires_glossary_review"],
    136: ["saikujo_castle_reading_requires_glossary_review"],
    148: ["yamanouchi_castle_reading_requires_glossary_review"],
    151: ["historical_epithet_rendering_requires_glossary_review"],
    157: ["kinjoshoshu_office_term_requires_glossary_review"],
    160: ["ando_masu_term_requires_glossary_review"],
    170: ["katatsura_given_name_reading_requires_glossary_review"],
    170: ["yoriki_relationship_requires_context_review"],
    175: ["kokura_castle_reading_requires_glossary_review"],
    198: ["isari_residence_reading_requires_glossary_review"],
    199: ["yogashira_shoya_office_term_requires_glossary_review"],
    211: ["nobenaga_harunobu_name_reading_requires_glossary_review"],
    212: ["takato_castle_reading_requires_glossary_review"],
    224: ["tadaaki_given_name_reading_requires_glossary_review"],
    228: ["ogoe_castle_reading_requires_glossary_review"],
    232: ["yusoku_kojitsu_term_requires_glossary_review"],
    250: ["shikiji_fujiyasu_name_reading_requires_glossary_review"],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def write_json(path: Path, value: Any) -> dict[str, Any]:
    return shared.write_json(path, value)


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != 122:
        raise ValueError("batch2 translations must exactly cover IDs 129-250")
    return ids


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    paths = {"SC": args.stock_sc, "JP": args.stock_jp, "EN": args.stock_en}
    loaded = {
        language: shared.load_source(path, language)
        for language, path in paths.items()
    }
    tables = {language: value[2] for language, value in loaded.items()}

    empty_ids = [
        entry_id
        for entry_id in ids
        if any(not tables[language].texts[entry_id] for language in ("SC", "JP", "EN"))
    ]
    if empty_ids:
        raise ValueError(f"selected aligned range contains empty entries: {empty_ids}")
    if not all(tables[language].texts[NEXT_START_ID] for language in ("SC", "JP", "EN")):
        raise ValueError("next-start boundary ID 251 must be non-empty in all languages")

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = tables["SC"].texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        problems = shared.common.invariant_mismatches(source_sc, replacement)
        source_placeholders = shared.BRACKET_TOKEN_RE.findall(source_sc)
        replacement_placeholders = shared.BRACKET_TOKEN_RE.findall(replacement)
        if source_placeholders != replacement_placeholders:
            problems.append(
                "custom_bracket_placeholders: "
                f"source={source_placeholders!r}, ko={replacement_placeholders!r}"
            )
        if problems:
            failures.append({"id": entry_id, "problems": problems})
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": shared.common.text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "references": {
                    language: {
                        "utf16le_sha256": shared.common.text_hash(
                            tables[language].texts[entry_id]
                        ),
                        "structure": shared.source_structure(
                            tables[language].texts[entry_id]
                        ),
                    }
                    for language in ("SC", "JP", "EN")
                },
                "manual_semantic_crosscheck": True,
            }
        )
    if failures:
        raise ValueError(f"replacement invariants failed: {failures}")

    sc_packed, sc_raw, _ = loaded["SC"]
    overlay = {
        "schema": shared.common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": "MSG_PK/SC/msgbre.bin",
        "base_language": "SC",
        "entry_count": len(ids),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": sha256(sc_raw),
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    shared.validate_overlay(overlay, ids)

    anchor_ids = (SCOPE_START - 1, SCOPE_START, SCOPE_END, NEXT_START_ID)
    evidence = {
        "schema": "nobu16.kr.msgbre-alignment-evidence.v2",
        "batch_id": BATCH_ID,
        "resource": "msgbre",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_nonempty_entry_count": len(ids),
            "next_start_id": NEXT_START_ID,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_3000_entry_count",
            "same_numeric_string_ids",
            "all_selected_entries_nonempty_in_sc_jp_en",
            "manual_semantic_crosscheck_of_selected_entries",
        ],
        "source_files": {
            language: {**SOURCE_PINS[language], "string_count": STRING_COUNT}
            for language in ("SC", "JP", "EN")
        },
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: shared.common.text_hash(
                        tables[language].texts[entry_id]
                    )
                    for language in ("SC", "JP", "EN")
                },
            }
            for entry_id in anchor_ids
        ],
        "entry_count": len(ids),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msgbre-review-index.v2",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(ids),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en",
                "automated_draft": True,
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": UNCERTAINTY_FLAGS.get(entry_id, []),
            }
            for entry_id in ids
        ],
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["overlay"] = write_json(out_root / "public" / OVERLAY_NAME, overlay)
    artifacts["alignment_evidence"] = write_json(
        out_root / "evidence" / EVIDENCE_NAME, evidence
    )
    artifacts["review_index"] = write_json(
        out_root / "review" / REVIEW_NAME, review
    )

    public_paths = {
        "overlay": out_root / "public" / OVERLAY_NAME,
        "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME,
        "review_index": out_root / "review" / REVIEW_NAME,
    }
    source_free_scan = {
        name: shared.script_counts(path.read_text(encoding="utf-8"))
        for name, path in public_paths.items()
    }
    if any(
        counts != {"cjk_unified_count": 0, "kana_count": 0}
        for counts in source_free_scan.values()
    ):
        raise ValueError("public artifact contains source-script text")

    validation = {
        "schema": "nobu16.kr.msgbre-generation-validation.v2",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_nonempty_entry_count": len(ids),
            "next_start_id": NEXT_START_ID,
            "selected_ids_sha256": sha256(
                json.dumps(ids, separators=(",", ":")).encode("utf-8")
            ),
        },
        "source_alignment": {
            "languages": ["SC", "JP", "EN"],
            "string_count_each": STRING_COUNT,
            "selected_reference_hash_count": len(ids) * 3,
            "manual_semantic_crosschecks": len(ids),
            "selected_nonempty_in_all_languages": len(ids),
        },
        "replacement_invariants": {
            "checked": len(ids),
            "failures": 0,
            "custom_bracket_placeholder_checks": len(ids),
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "custom_bracket_placeholders_in_order",
            ],
        },
        "translation_status": {
            "translated_draft": len(ids),
            "human_review_required": len(ids),
            "runtime_reviewed": 0,
            "specific_uncertainty_entries": len(UNCERTAINTY_FLAGS),
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_modified": False,
            "common_builder_modified": False,
            "other_workstreams_modified": False,
            "existing_v01_artifacts_modified": False,
        },
    }
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation
    )
    return {"out_root": out_root, "entry_count": len(ids), "artifacts": artifacts}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stock-sc", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "SC" / "msgbre.bin"
    )
    parser.add_argument(
        "--stock-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgbre.bin"
    )
    parser.add_argument(
        "--stock-en", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgbre.bin"
    )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"entries={result['entry_count']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print(f"next_start_id={NEXT_START_ID}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
