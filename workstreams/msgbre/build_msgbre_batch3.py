#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 3 (IDs 251-350)."""

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


BATCH_ID = "msgbre_biographies_0251_0350.v0.3"
OVERLAY_NAME = "msgbre_ko_biographies_0251_0350.v0.3.json"
EVIDENCE_NAME = "alignment_evidence.v0.3.json"
REVIEW_NAME = "review_index.v0.3.json"
VALIDATION_NAME = "validation.v0.3.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 251
SCOPE_END = 350
NEXT_START_ID = 351

TRANSLATIONS: dict[int, str] = {
    251: "오사키 가신. 마사카성주. 이즈노카미라 칭했고 가노 성씨도 썼다. 이치하사마·가노 가문은 오사키 일족의 참모를 맡았다고 한다. 덴쇼 말기 주가의 내분 때 우지이에 요시쓰구 편에 섰다.",
    252: "도요토미 가신. 규슈 정벌과 오다와라 정벌에 참가했다. 세키가하라 전투에서는 동군 편에 섰고 오사카 전투에도 종군했다. 그 공으로 영지가 늘어 에치고 산조 4만 1천여 석을 다스렸다.",
    253: "오토모 가신. 분고 고무레성주. 생애 대부분을 전장에서 보낸 한편 주군 소린을 초대해 벚꽃놀이 모임을 연 풍류인이었다. 일족에서 모반자가 나온 책임을 지고 자결했다.",
    254: "단고의 센고쿠 다이묘. 이웃 와카사의 다케다 가문과 자주 싸웠다. 잇시키 가문은 세이와 겐지 아시카가 가문의 일문으로, 야마나·아카마쓰·교고쿠 가문과 함께 막부의 시시키를 이루며 중용되었다.",
    255: "단고의 센고쿠 다이묘. 조카 미쓰노부가 호소카와 후지타카에게 모살된 뒤 유미키성에 들어가 잇시키 종가를 이었다. 그러나 호소카와 다다오키에게 포위되자 적진에 돌입해 전사했다.",
    256: "단고의 센고쿠 다이묘. 요시유키의 아들. 교토에서 쫓겨난 쇼군 아시카가 요시아키를 보호해 오다군의 공격을 받았다. 선전했으나 가신 누마타 가게유의 내통으로 패해 자결했다.",
    257: "아시카가 가신. 가라하시 아리카즈의 둘째 아들. 주군 요시아키가 교토에서 추방된 뒤 도쿠가와 이에야스를 섬겼다. 훗날 고케에 올랐고 게이초 연간인 1596~1615년에 가라하시 가문을 이었다.",
    258: "아시카가 가신. 오토모슈를 맡았다. 호소카와 후지타카와 함께 유폐된 주군 요시아키의 탈출에 힘썼다. 요시아키가 교토에서 추방된 뒤에는 그를 쇼군직에 복귀시키려 분주히 움직였다.",
    259: "단고의 센고쿠 다이묘. 요시미치의 아들. 아버지가 죽은 뒤 가신 이나토미 스케나오에게 의지해 호소카와 후지타카군과 싸웠다. 아케치 미쓰히데의 주선으로 화친해 후지타카의 딸과 혼인했으나 다시 배반해 살해되었다.",
    260: "다케다 가신. 이데우라성주. 무라카미 요시키요의 일족이다. 고슈 닌자의 두령으로 다케다 가문을 섬겼다. 주가가 멸망한 뒤 사나다 가문을 섬겼으며, 두령이면서도 직접 첩보 활동을 벌였다.",
    261: "쓰쓰이 가신. 이도성주. 훗날 거성을 아들 가쿠히로에게 넘기고 오다 노부나가를 섬겼다. 여러 전투에서 공을 세워 야마시로 마키시마 2만 석을 받았으나 야마자키 전투에서 아케치 미쓰히데 편에 서 영지를 잃었다.",
    262: "이토 요시스케의 손자인 기리시탄. 이름은 스케마스이며 만쇼는 세례명이다. 오토모 소린의 인척으로 덴쇼 견구소년사절의 정사가 되어 교황과 에스파냐 국왕을 알현했고, 귀국한 뒤 사제가 되었다.",
    263: "센고쿠 시대 말기의 검객. 가네마키 지사이에게 검술을 배우고 잇토류 검술을 창시했다. 여러 구니를 여행하며 33차례 승부를 벌였고 한 번도 패하지 않았다고 한다.",
    264: "휴가의 센고쿠 다이묘. 요시스케의 아들. 서자였으나 적자가 요절해 가독을 이었고 아버지의 후견 아래 이토 가문의 전성기를 열었다. 시마즈 가문과 대치하던 중 병사했다.",
    265: "이토 가신. 요시마스의 아들. 할아버지 요시스케와 함께 오토모 소린에게 의지했다. 도요토미 히데요시의 규슈 평정 뒤 숙부 스케타카가 휴가 오비를 되찾자 그를 따랐으며, 훗날 젊은 나이에 병사했다.",
    266: "휴가의 센고쿠 다이묘. 이토 가문의 최대 판도를 세웠으나 기사키바루 전투에서 시마즈군에 패해 쇠퇴했다. 분고의 오토모 소린에게 의지했지만 오토모군이 미미가와 전투에서 대패한 뒤 각지를 떠돌았다.",
    267: "도요토미 가신. 휴가 이토 가문의 먼 일족으로 떠돌던 이토 스케타카를 보호했다. 오사카 전투에서는 나나테구미 조장으로 오사카성에 농성했으나 패전 뒤 용서받아 도쿠가와 가문을 섬겼다.",
    268: "이토 가신. 요시스케의 처남이라고 한다. 지용을 겸비한 장수로 이름났다. 기사키바루 전투에서 총대장을 맡았으나 병력이 적은 시마즈군의 교란 전술과 기습에 패해 전사했다.",
    269: "휴가 오비번주. 스케타카의 아들. 세키가하라 전투에서 아버지와 함께 동군에 속해 다카하시 모토타네군과 시마즈군을 상대했다. 아버지가 죽은 뒤 휴가 오비 3만 6천 석을 잇고 검지와 개간을 시행했다.",
    270: "이토 가신. 요시스케 옹립에 공을 세우고 측근으로 권세를 누려 가신들의 미움을 샀다. 공포탄으로 싸우자고 거짓 약속한 뒤 기모쓰키 가문을 격파하고 난고를 빼앗았다.",
    271: "도요토미 가신. 요시스케의 아들. 도요토미 히데요시의 규슈 정벌군에서 길잡이를 맡아 휴가 오비의 옛 영지를 되찾았다. 조선 파병에도 종군했고 세키가하라 전투에서는 동군에 속했으나 전후 병사했다.",
    272: "도요토미 가신. 아버지 모리카게가 죽은 뒤 가독을 이어 미노 오가키 3만 4천 석을 다스렸다. 세키가하라 전투에서 서군에 속해 전후 영지를 몰수당하고 추방되었으며, 훗날 마에다 도시쓰네를 섬겼다.",
    273: "도쿠가와 가신. 주군 이에야스의 측근으로 민정에 참여했다. 간토 전역에서 검지와 치수 사업을 벌여 에도 막부의 경제 기반 확립에 이바지했으며, 그의 지방 행정법은 이나류라 불렸다.",
    274: "도쿠가와 가신. 후방 지원에서 활약했다. 아버지 다다쓰구와 함께 신전 개발과 치수에 힘썼고 아버지가 죽은 뒤 간토 군다이직을 이었다. 오사카 전투에서는 후신부교로 해자를 메우는 등의 일을 맡았다.",
    275: "도쿠가와 가신. 세키가하라 전투에서 도쿠가와 히데타다를 따라 우에다성 공격에 참가했다. 오사카 전투에서는 사카이 이에쓰구 휘하에서 싸웠다. 훗날 오사카 조다이를 지내고 미카와 가리야번 초대 번주가 되었다.",
    276: "이토 가신. 기요타케성주. 세키가하라 전투 때 서군 측 미야자키성을 함락했다. 전후 막부의 반환 명령과 주군 스케요시의 자결 명령을 모두 거부한 채 거성에 농성하다 패사했다.",
    277: "셋쓰 아리마 가신. 노리요리를 따라 동군으로 세키가하라 전투에 참가했다. 전초전인 구이세가와 전투에서 이시다 미쓰나리의 장수 요코야마 겐모쓰를 죽였고 오사카 전투에서도 활약했으나 시마바라의 난에서 전사했다.",
    278: "잇시키 가신. 단고 오시키성주. 사가미노카미라 칭했다. 사사키 쇼스케지로 요시쿠니에게 포술을 배워 독창적으로 발전시켰다. 훗날 손자 스케나오에게 전수해 이나토미류 포술의 기초를 세웠다.",
    279: "잇시키 가신. 이나토미류 포술의 시조. 주가가 멸망한 뒤 호소카와 다다오키를 섬겨 총포 사범을 맡았다. 훗날 도쿠가와 가문에 출사해 막부 뎃포카타로서 구니토모 대장장이 집단의 조직화에 힘썼다.",
    280: "사이토 가신. 미노 삼인중의 한 사람. 주가가 멸망한 뒤 오다 가문을 섬겼다. 아네가와 전투에서 아자이군의 측면을 공격해 아군을 승리로 이끌었다. 완고한 성격 때문에 잇테쓰라는 말의 어원이 되었다.",
    281: "도쿠가와 가신. 미치토의 아들. 오사카 전투에서 첫 출진했다. 잔혹하고 무도해 사냥에서 짐승을 잡지 못한 화풀이로 영민을 대량 학살했다고 한다. 훗날 모반 혐의를 받아 자결했다.",
    282: "오다 가신. 잇테쓰의 서장자. 혼노지의 변 뒤 도요토미 히데요시를 섬겨 우마마와리를 맡았다. 고마키 나가쿠테 전투와 규슈 정벌 등에 종군했고 아버지가 죽은 뒤 미노 시미즈 1만 2천 석을 받았다.",
    283: "하야시 마사히데의 아들. 이나바 시게미치의 딸과 혼인해 이나바 성씨를 썼다. 고바야카와 가문을 섬기며 세키가하라 전투에서 히데아키를 동군으로 돌아서게 했다. 훗날 도쿠가와 이에미쓰의 유모 가스가노쓰보네를 후처로 맞았다.",
    284: "오다 가신. 잇테쓰의 맏아들. 혼노지의 변 뒤 도요토미 히데요시를 섬겼다. 세키가하라 전투에서는 오다 히데노부를 따라 서군에 속했으나 뒤에 동군에 항복했고, 전후 분고 우스키 5만 석을 받았다.",
    285: "도요토미 가신. 사다미치의 맏아들. 규슈 정벌 때 주군 히데요시의 노여움을 사 칩거했으나 훗날 복귀해 여러 전투에 종군했다. 아버지가 죽은 뒤 가독을 잇고 오사카 겨울 전투에 출진했다.",
    286: "도요토미 가신. 시게미치의 다섯째 아들. 형 마키무라 도시사다가 죽었을 때 유자가 어렸기에 이세 이와데 2만여 석을 이었다. 세키가하라 전투에서는 동군에 속해 구키 요시타카와 싸웠다.",
    287: "아시나 가신. 모리쿠니의 아들. 스리아게하라 전투에서 주가가 패한 뒤 주군 모리시게를 따라 히타치로 달아났다. 훗날 모리시게의 곁을 떠나 고향 이나와시로로 돌아와 여생을 보냈다.",
    288: "아시나 가신. 후처의 참소를 듣고 아들 모리타네를 폐적하려다 발각되어 아들과 다퉜다. 훗날 주가를 배반하고 다테 가문에 속했으며 스리아게하라 전투에서는 선봉으로 아시나군과 싸웠다.",
    289: "오가사와라 가신. 마사노리의 셋째 아들. 히키성·다카토성 공격을 비롯한 여러 전투에 사무라이 대장으로 종군해 활약했다. 훗날 수석 가로가 되어 가문에서 가장 많은 1천 6백 석을 받았다.",
    290: "오가사와라 가신. 주군 나가토키가 다케다 신겐에게 쫓겨난 뒤에도 거성 이누카이성에 농성해 저항했다. 그러나 나가토키의 군세를 맞으러 가던 중 다케다군과 마주쳐 싸우다 패했다.",
    291: "모리 가신. 주군 모토나리의 모리 가문 상속에 힘썼다. 훗날 군역과 축성 등의 의무를 소홀히 하는 등 오만하게 행동해 모토나리의 명으로 이노우에 일족 30명이 살해되었다.",
    292: "이요 우쓰노미야 가신. 나카오성주. 조요지를 세우고 성 아랫마을에 출몰하는 해적을 토벌해 백성의 생활을 안정시키는 정책을 폈다. 훗날 조소카베군에게 거성을 빼앗겼다.",
    293: "구로다 가신. 구로다 팔호의 한 사람. 모토타카 때부터 4대에 걸쳐 섬긴 충신이다. 이시가키바루 전투에서 요시타카를 따라 공을 세웠고, 나가마사가 죽은 뒤 일어난 구로다 소동에서는 번의 존속에 이바지했다.",
    294: "오다 가신. 오다 노부히데의 사촌. 오와리 슈고인 시바 가문의 일족 이노오 가문에 입양되었다. 오케하자마 전투에서 와시즈 요새를 지키다 아사히나 야스토모군의 공격을 받아 전사했다.",
    295: "호조 가신. 호조 우지쿠니를 섬기며 누마타성 성주 대리를 맡았다. 사나다 마사유키의 지성 나구루미성을 독단으로 빼앗아 도요토미 히데요시에게 오다와라 정벌의 구실을 주었고, 전후 책형을 당했다.",
    296: "호소카와 가신. 간레이 호소카와 다카쿠니를 죽이고 미요시 모토나가를 멸했으며 교토의 홋케 봉기를 진압하는 등 각지에서 활약했다. 미요시 마사나가가 셋쓰 에구치 전투에서 패사한 뒤 몰락했다.",
    297: "우쓰노미야 가신. 가미노카와성주. 주군 구니쓰나의 후계자로 아사노 나가마사의 아들 나가시게를 맞아들이자고 주장해 숙로 하가 다카타케와 대립했다. 훗날 다카타케의 공격을 받아 패사했다.",
    298: "스루가의 센고쿠 다이묘. 이복형 겐코 에탄을 쓰러뜨리고 가독을 이었다. 가이·사가미·스루가 삼국 동맹으로 후방의 걱정을 없앤 뒤 상경길에 올랐으나 오케하자마에서 오다 노부나가의 기습을 받아 전사했다.",
    299: "이마가와 가문 제8대 당주. 어린 나이에 당주가 되어 우마마와리 창설, 검지 시행, 유통 활성화 등의 정책을 폈다. 그러나 명장이라는 평판이 퍼지기 시작하자마자 급사했다.",
    300: "스루가의 센고쿠 다이묘. 요시모토의 적장자. 아버지가 죽은 뒤 가독을 이었으나 게마리와 와카에 빠져 무위로 세월을 보냈다. 그 결과 도쿠가와 이에야스와 다케다 신겐에게 영국에서 쫓겨났다.",
    301: "이마가와 우지치카의 아들. 이름은 요시자네라고도 한다. 형 우지테루가 죽은 뒤 벌어진 가독 다툼인 하나쿠라의 난에서 바이카쿠 쇼호, 곧 이마가와 요시모토와 싸웠으나 패해 자결했다.",
    302: "시마즈 가신. 친아버지는 시마즈 히사미치다. 시게토요의 양자가 되어 요시히로 휘하에서 활약했다. 세키가하라 전투 뒤 퇴각하던 요시히로와 흩어져 동군에 붙잡힌 뒤 죽임을 당했다.",
    303: "사쓰마의 호족. 누이는 시마즈 다카히사에게 시집갔다. 시마즈 다다요시와 시마즈 사네히사의 항쟁에서 다다요시를 지지했다. 이치키성 공격에서 사네히사의 동생 다다토키를 죽이는 등 여러 전투에서 활약했다.",
    304: "우에스기 가신. 히라바야시성주. 가쓰나가의 아들. 주군 겐신에게 이름을 하사받았다. 아버지가 죽은 뒤 가독을 이었고 혼조 시게나가의 모반 진압에서 활약해 이후 시게나가보다 윗자리를 받았다.",
    305: "우에스기 가신. 히라바야시성주. 조조 사다노리의 난 때 한동안 조조 편에 섰다. 가와나카지마 전투에서 활약해 감사장을 받았다. 모반한 혼조 시게나가의 거성 무라카미성을 포위하던 중 병사했다.",
    306: "우에스기 가신. 히라바야시성주. 가쓰나가의 아들. 형 아키나가가 죽은 뒤 가독을 이었다. 데와 센보쿠 봉기 진압 등에 활약했으나 도요토미 히데요시의 조선 파병에 종군했을 때 중병에 걸려 죽었다.",
    307: "우에스기 가신. 오타테의 난에서 우에스기 가게카쓰 편에 서 이이야마성주가 되었다. 성 아랫마을을 정비해 근세 이이야마정의 기초를 닦았다. 주가가 아이즈로 전봉된 뒤에는 아이즈 삼봉행의 한 사람으로 꼽혔다.",
    308: "유키 가신. 옛 성씨는 미우라. 주군 하루토모에게 유키 사천왕의 한 사람인 이와카미 성씨를 쓰도록 허락받았다. 사타케 요시시게와 다무라 기요아키에게 문서를 보내는 등 외교에서 활약했다.",
    309: "사타케 가문 제20대 당주. 사타케 요시시게의 셋째 아들 이와키 사다타카의 맏아들이다. 아버지의 유령 시나노 나카무라 1만 석을 다스렸다. 훗날 백부 사타케 요시노부의 양자가 되어 구보타번 제2대 번주가 되었다.",
    310: "무쓰 오다테성주. 다테 가문의 내분인 덴분의 대란에서 딸 구보가 하루무네의 아내였기에 하루무네 편에 섰다. 사타케 요시아쓰와도 여러 차례 싸웠으며 와카에 능했다.",
    311: "무쓰 오다테성주. 지카타카의 아들. 도요토미 히데요시의 오다와라 정벌에 참가해 공을 세우고 영지를 인정받았으나 호조 가문이 항복한 지 얼마 지나지 않아 가마쿠라에서 병사했다.",
    312: "무쓰 오다테성주. 다테 하루무네의 맏아들. 이와키 시게타카의 양자가 되어 가독과 양부가 일군 영국을 이었다. 그러나 사타케 가문의 침공을 받아 종속될 수밖에 없었다.",
    313: "무쓰의 호족. 쓰네타카의 아들. 고가 구보 아시카가 마사우지와 다카모토 부자의 다툼에서 사타케 가문과 함께 마사우지 편에 서 다카모토 편의 우쓰노미야 가문 및 시모사 유키 가문과 거듭 싸웠다.",
    314: "시바 가신. 요시나가의 동생. 우쿄라 칭했다. 주가의 앞날을 불안하게 여겨 난부 가문과 내통했다. 거성 이와시미즈관에서 거병했고 이를 계기로 난부군이 침공해 시바 가문이 멸망했다.",
    315: "시바 가신. 히고라 칭했다. 정무를 외면하고 유흥에 빠진 주군 아키나오를 여러 차례 간했으나 받아들여지지 않았다고 한다. 난부 가문이 시바 가문을 멸망시킬 때 주가를 따라 죽었다.",
    316: "미요시 가신. 미요시 삼인중의 한 사람으로 미요시 일족과 같은 대우를 받았다. 쇼군 아시카가 요시아키의 거병에 호응해 야마시로 요도성에 농성했으나 호소카와 후지타카군의 공격을 받아 패사했다.",
    317: "사가라 가신. 무용이 뛰어나 각지에서 활약했다. 히고 미나마타성 공방전에서는 적장 니이로 다다모토와 렌가를 주고받았다. 주군 요시히가 죽은 뒤 후카미 나가토모와 함께 어린 주군 요리후사를 보좌했다.",
    318: "사가라 가신. 요리야스의 아들. 세키가하라 전투에서 주군 요리후사를 동군에 내응시켜 주가의 존속에 기여했다. 훗날 국가로를 지냈으나 전횡이 심해 쓰가루로 유배되었다.",
    319: "빗추의 호족. 사이다성주. 시모사노카미라 칭했다. 아버지 히데나가처럼 모리·우키타 양가 사이에서 이합집산을 거듭했다. 한때 아마고 가문에 거성을 빼앗겼으나 훗날 되찾았다.",
    320: "빗추의 호족. 사이다성주. 시모사노카미라 칭했다. 아버지 후지스케는 쇼 다메스케의 동생이다. 거성이 우키타 가문과 모리 가문의 국경에 있어 양가 사이에서 이합집산을 거듭했다.",
    321: "호조 우지야스의 일곱째 아들. 에쓰소 동맹이 성립될 때 에치고로 가 훗날 우에스기 겐신의 양자가 되었다. 겐신이 죽은 뒤 오타테의 난에서 의형제 우에스기 가게카쓰와 가독을 다투다 패사했다.",
    322: "야마노우치 우에스기 가문 당주. 가와고에 전투에서 패해 세력을 잃고 호조군에 쫓겨 에치고로 달아났다. 나가오 가게토라에게 우에스기 성씨와 간토 간레이직을 넘겼고 오타테의 난에서 우에스기 가게카쓰에게 살해되었다.",
    323: "오기야쓰 우에스기 가문 당주. 가신 오타 스케타카의 호조 가문 내통으로 거성 에도성을 빼앗겨 가와고에성으로 달아났다. 에도성을 되찾으려 호조 가문과 싸웠으나 세력을 회복하지 못했다.",
    324: "오기야쓰 우에스기 가문 당주. 도모오키의 아들. 호조 가문에 거성 가와고에성을 빼앗겼다. 주변 여러 구니와 화친한 뒤 대군으로 성을 포위했으나 호조군의 기습을 받아 전사했고 오기야쓰 우에스기 가문은 끊겼다.",
    325: "에치고 슈고. 에치고 슈고다이 나가오 다메카게의 옹립을 받아 양부 후사요시를 자결시키고 슈고가 되었다. 훗날 다메카게와 대립해 우사미 후사타다와 함께 그를 제거하려 했으나 실패했다.",
    326: "가게카쓰의 적장자. 데와 요네자와번 30만 석의 제2대 번주. 어머니가 일찍 죽어 나오에 가네쓰구와 오후네의 손에서 자랐다. 셋째 딸은 주신구라로 유명한 기라 고즈케노스케에게 시집갔다.",
    327: "호조 가신. 도모나오의 둘째 아들. 아버지와 형 나가노리처럼 마쓰야마성 아랫마을의 경영에 힘썼다. 도요토미 히데요시의 오다와라 정벌 때 오다와라성에 농성했으며 함락 뒤 행방불명되었다.",
    328: "도요토미 가신. 규슈 정벌과 오다와라 정벌 등에 종군했다. 세키가하라 전투에서 서군에 속해 전후 영지를 잃었다. 훗날 아사노 가문을 섬겨 오사카 전투에 출진했으며 다인으로도 이름났다.",
    329: "오기야쓰 우에스기 가신. 도모나오의 아버지. 마쓰야마성주. 가와고에성 전투에서 패한 우에스기 도모사다가 달아오자 숨겨 주었으나 훗날 호조 가문에 항복했다. 우에스기 겐신과 싸우다 전사했다.",
    330: "오기야쓰 우에스기 가신. 호조 가문의 무사시 침공군에 항복한 뒤 호조 가문을 섬겼다. 다국중으로 마쓰야마성주가 되어 독자적인 주인장을 쓰는 등 호조 가문에서 독립된 지배를 펼쳤다.",
    331: "이가의 호족. 이가 십이인중의 중심인물. 오다 노부카쓰가 이가를 침공했을 때 노부카쓰의 가신 쓰게 사부로자에몬을 죽이고 오다군을 격퇴했다. 훗날 오다군에 패해 미카와로 달아났다.",
    332: "미무라 가신. 쓰네야마성주. 주군 이에치카의 딸과 혼인했다. 처남 모토치카가 죽은 뒤에도 거성에 농성해 모리 가문에 저항했고, 고바야카와 다카카게가 이끄는 모리군의 공격을 받아 전멸했다.",
    333: "사가라 가신. 요리오키의 동생. 요리오키와 주군 요시시게의 제휴를 성사시키고 국정에 참여했다. 가문 안에서 신망이 높았으나 그 세력을 두려워한 형에게 살해되었고, 훗날 원령의 재앙이 있었다고 한다.",
    334: "사가라 가신. 히고 우에무라성주. 아들 하루히로를 후계자로 삼는다는 약속을 받고 주군 요시시게에게 협력했다. 요시시게 정권의 막후 실력자로서 정권의 성립과 존속을 위해 자형과 친동생을 모살했다.",
    335: "사가라 가신. 히고 우에무라성주. 요리오키의 둘째 아들. 아버지가 죽은 뒤 두 동생과 함께 조카 요시히에게 반기를 들었으나 패해 사쓰마로 달아났다. 훗날 계략에 속아 귀국했다가 요시히에게 살해되었다.",
    336: "아사쿠라 가신. 이치조다니 사봉행의 한 사람으로 국정에 참여했다. 오다 노부나가의 에치젠 침공군에 항복해 본령을 인정받고 에치젠 슈고다이가 되었으나 도다 나가시게의 공격을 받아 패사했다.",
    337: "우라가미 가신. 요시이에의 아들. 아버지가 시마무라 모리자네의 습격을 받고 자결한 뒤 비젠 후쿠오카의 거상 아베 요시사다에게 달아났으나 얼마 지나지 않아 병사했다. 어리석고 겁이 많다는 평을 받았다.",
    338: "도요토미 가신. 나오이에의 적장자. 주군 히데요시의 총애를 받아 오대로의 한 사람이 되었으나 내분으로 중신 대부분을 잃었다. 세키가하라 전투에서 서군에 속했고 전후 하치조지마로 유배되었다.",
    339: "우키타 가신. 다다이에의 아들. 주가의 내분으로 출분해 도쿠가와 이에야스를 섬겼다. 세키가하라 전투의 공으로 이와미 하마다 2만 석을 받았고 오사카 전투에서는 이에야스의 손녀 센을 구출했다.",
    340: "우키타 가신. 오키이에의 아들. 형 나오이에의 창업에 크게 이바지했다. 형이 죽은 뒤 조카 히데이에의 후견인이 되었고 조선 파병 때는 도요토미군 총독을 맡은 히데이에를 따라 바다를 건넜다.",
    341: "우라가미 가신. 옷코성주. 온갖 권모술수로 적을 제거해 가문 안에서 최대 세력을 일궜다. 끝내 주군 무네카게를 추방하고 비젠국을 장악한 희대의 모장이다.",
    342: "우라가미 가신. 우키타 요시이에의 이복동생. 사이가 나쁜 형을 모살하고 도이시성을 빼앗았다. 우라가미 가문이 마사무네파와 무네카게파로 갈리자 마사무네 편에 섰고 요시이에의 손자인 무네카게파 나오이에에게 죽었다.",
    343: "우에스기 가신. 에치고류 군학의 시조라고 한다. 조조 사다노리의 난에서 조조 편에 섰으나 사다노리가 죽은 뒤 귀참했다. 국정에 참여하는 등 활약했지만 나가오 마사카게와 뱃놀이하던 중 익사했다.",
    344: "나가노 가신. 나가노 다네후지의 아들. 우지이 가문은 나가노 스케타카, 곧 나가노 구도 가문 초대 당주 스케마사의 둘째 아들을 시조로 한다. 오다 노부카네에게 우지이성에서 쫓겨났으나 훗날 오다 가문을 섬겼다.",
    345: "오사키 가신. 이와데야마성주. 오사키 내란 때 이바노 소하치로와 손잡고 반주류파의 중심인물로 활동했다. 주가가 몰락한 뒤 다테 마사무네를 섬겼으나 얼마 지나지 않아 병사했다.",
    346: "도요토미 가신. 보쿠젠의 아들. 오다와라 정벌에 종군해 이세 구와나 2만 2천 석을 받았다. 세키가하라 전투에서 서군에 속해 전후 유랑했고 오사카성에 들어가 오사카 여름 전투에서 도요토미 히데요리를 따라 죽었다.",
    347: "모가미 가신. 사다나오의 아들. 지략이 뛰어나 덴도 가문과 시라토리 가문의 토벌에 이바지했다. 다테 가문에 사자로 가고 마무로성 공략에서 공을 세우는 등 여러 방면에서 활약했다.",
    348: "모가미 가신. 덴분의 대란에서 주군 요시모리의 대리로 출진했다. 주가의 내분 때는 중병에 걸린 몸으로 요시모리를 설득해 요시아키에게 가독을 넘기도록 했다.",
    349: "사이토 가신. 미노 삼인중의 한 사람. 주가가 멸망한 뒤 오다 가문을 섬겨 이세 평정전에서 공을 세웠다. 나가시마 잇코 봉기군과 싸우다 오다군이 패했을 때 후군을 맡아 전사했다.",
    350: "오사키 가신. 산초메성주. 우지이에 가문의 시조는 시바 이에카네의 집사를 지낸 우지이에 사에몬 시게사다라고 한다. 아들 요시쓰구가 이와데야마성주가 되자 산초메성에 은거했다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    254: ["shishiki_office_term_requires_glossary_review"],
    256: ["numata_kageyu_title_reading_requires_glossary_review"],
    258: ["otomohshu_office_term_requires_glossary_review"],
    262: ["tensho_embassy_title_requires_glossary_review"],
    274: ["fushin_bugyo_office_term_requires_glossary_review"],
    278: ["oshiki_castle_and_gunnery_name_readings_require_glossary_review"],
    279: ["teppokata_office_term_requires_glossary_review"],
    289: ["hiki_castle_reading_requires_glossary_review"],
    294: ["iino_family_reading_requires_officer_catalog_review"],
    303: ["shimazu_tadatoki_given_name_requires_catalog_review"],
    308: ["iwakami_surname_grant_sentence_requires_context_review"],
    317: ["sagara_yoshihi_given_name_requires_catalog_review"],
    325: ["usami_fusatada_given_name_requires_catalog_review"],
    330: ["tokokushu_status_term_requires_glossary_review"],
    341: ["okko_castle_reading_requires_glossary_review"],
    344: ["ujii_family_and_castle_readings_require_glossary_review"],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def write_json(path: Path, value: Any) -> dict[str, Any]:
    return shared.write_json(path, value)


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != 100:
        raise ValueError("batch3 translations must exactly cover IDs 251-350")
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
        raise ValueError("next-start boundary ID 351 must be non-empty in all languages")

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
        "schema": "nobu16.kr.msgbre-alignment-evidence.v3",
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
        "schema": "nobu16.kr.msgbre-review-index.v3",
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
        "schema": "nobu16.kr.msgbre-generation-validation.v3",
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
            "existing_v01_v02_artifacts_modified": False,
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
