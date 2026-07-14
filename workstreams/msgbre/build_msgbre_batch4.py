#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 4 (IDs 351-457)."""

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


BATCH_ID = "msgbre_biographies_0351_0457.v0.4"
OVERLAY_NAME = "msgbre_ko_biographies_0351_0457.v0.4.json"
EVIDENCE_NAME = "alignment_evidence.v0.4.json"
REVIEW_NAME = "review_index.v0.4.json"
VALIDATION_NAME = "validation.v0.4.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 351
SCOPE_END = 457
NEXT_START_ID = 458

TRANSLATIONS: dict[int, str] = {
    351: "아마고 가신. 가로를 맡았다. 요시다 고리야마성 공격 등에 종군했다. 갓산토다성 농성전에서는 함락 직전까지 성 안에 남아 싸웠고, 뒤에 적장자 히사노부 등과 함께 항복했다.",
    352: "오토모 가신. 분고 삼로의 한 사람. 외교를 담당하는 한편 히젠 방면 담당으로 국정에 참여했다. 지쿠젠 평정군 총대장을 맡는 등 여러 분야에서 활약했다.",
    353: "오토모 가신. 지쿠젠 고시다케성의 성독을 맡아 지쿠젠 경략을 담당했다. 또한 주가의 외교를 관장하며 오우치 가문과의 화친, 주군 소린의 동생 하루히데가 오우치 가문을 잇는 일 등을 주선했다.",
    354: "히다의 호족. 가에리쿠모성주. 우지토시의 아버지. 풍부한 광산 자원을 수입원으로 영지 경영을 안정시켰다. 열성적인 잇코슈 신도로 혼간지 가문과 협력해 나가오 다메카게와 싸웠으나 패했다.",
    355: "히다의 호족. 가에리쿠모성주. 도요토미 가신 가나모리 나가치카의 히다 침공군에 항복했으나, 대지진으로 거성이 매몰되고 산사태로 홍수가 일어나 멸망했다. 오늘날까지 매장금 전설이 남아 있다.",
    356: "아키즈키 가신. 오토모 가문에 패해 달아난 당주 다네자네를 숨겨 주었고, 야스미마쓰 전투에서 오토모군을 격퇴해 다네자네의 옛 영지 회복에 기여했다. 은거 뒤에는 황폐한 다카성을 재건하는 데 힘썼다.",
    357: "우쓰노미야 가문 제21대 당주. 나오쓰나의 적장자. 사타케 요시아키의 딸을 아내로 맞아 동맹을 맺었다. 하가 다카사다와 함께 호조 가문과 손잡은 영내의 반우쓰노미야 세력과 싸웠다. 병약했다고 한다.",
    358: "우쓰노미야 가문 제22대 당주. 히로쓰나의 적장자. 도요토미 히데요시의 오다와라 정벌에 참진해 영지를 인정받았다. 그러나 뒤에 도요토미 가문 내부의 권력 다툼에 휘말려 개역되었다.",
    359: "우쓰노미야 가문 제20대 당주. 오키쓰나의 적장자. 나스 마사스케와 다카스케 부자가 다툴 때 마사스케를 지지했다. 뒤에 다카스케의 지성 기쓰레가와성을 공격했으나 나스군의 기습을 받아 패사했다.",
    360: "이요의 호족. 1532년 무렵 셋째 아들 후사쓰나와 함께 하기모리성을 쌓아 거성으로 삼았다. 이요 우쓰노미야 가문은 시모쓰케 우쓰노미야 가문 제8대 당주 사다쓰나의 조카 다케시게 가게야스를 시조로 한다고 한다.",
    361: "우쓰노미야 히로쓰나의 둘째 아들. 유키 하루토모의 양자가 되었으나, 뒤에 도쿠가와 이에야스의 둘째 아들 히데야스가 유키 가문에 입적하자 우쓰노미야 가문으로 돌아왔다. 이후 반도쿠가와·반유키의 태도를 고수했다.",
    362: "이요의 호족. 지조가타케성주. 도사 이치조 가문과 손잡았다. 아스카성 전투에서 사이온지 긴타카를 죽이는 등 위세를 떨쳤으나, 도리사카 고개 전투에서 고노·모리 연합군에 패한 뒤 쇠퇴했다.",
    363: "사이온지 가신. 하기모리성주. 이요 우쓰노미야 가문의 일족이라고 한다. 이웃한 모토성주 셋쓰 지카노부와 영지 문제로 여러 차례 다퉜다. 사이온지 15장의 한 사람으로 꼽혀 ‘하기모리님’이라 불렸다.",
    364: "이마가와 가신. 나가테루의 아들. 아버지가 전사했을 때 도쿠가와 이에야스에게 붙잡혀 이에야스의 처자와 교환되는 인질로 슨푸성에 갔다. 주가 멸망 뒤 도쿠가와 가문에 속해 나가시노 전투 등에 종군했다.",
    365: "이마가와 가신. 가미노고성주. 이마가와 요시모토의 누이를 아내로 맞았다. 우도노 가문은 후지와라노 사네카타의 후예로, 가마쿠라 시대 기이 신구 별당의 아들이 발탁되어 니시노고리(가마고리)를 다스렸다고 한다.",
    366: "이마가와 가신. 나가모치의 아들. 오케하자마 전투 뒤 미카와 무장들이 잇달아 도쿠가와 가문에 속할 때 홀로 이마가와 편에 남았다. 그 때문에 미카와 평정을 노린 도쿠가와군의 공격을 받아 패사했다.",
    367: "아카마쓰 가신. 조즈이성주. 우노 가문은 아카마쓰 가문과 같은 무라카미 겐지 계통이다. 아마고 하루히사의 하리마 침공군에 항복해 영지를 인정받았다. 뒤에 하시바 히데요시의 주고쿠 침공군에 패해 자결했다.",
    368: "아카마쓰 가신. 조즈이성주. 마사요리의 아들. 우노 가문은 아카마쓰 가문 아래에서 슈고다이를 맡았다. 뒤에 모리 가문에 속해 오다 가문에 맞섰으나 하시바 히데요시의 주고쿠 침공군에 패해 자결했다.",
    369: "이요 우쓰노미야 가신. 성을 쌓을 때 물이 나오지 않아 이전하려 했으나, 나타난 노파가 물이 나는 곳을 알려 주어 그대로 머물렀다. 뒤에 샘과 성에 ‘우바가이’라는 이름을 붙였다고 한다.",
    370: "이요 우쓰노미야 가신. 우바가이성주. 오노 나오모리의 야습으로 거성을 잃자 애마의 목을 벤 뒤 자결했다. 이후 유키테루의 기일마다 그의 혼을 태운 목 없는 말이 달린다고 한다.",
    371: "사타케 가신. 오사카 전투에서 중상을 입고도 분전해 ‘사타케의 황귀’라는 별명을 얻었다. 뒤에 가로가 되었으며, 공명정대하고 과단성 있는 인품으로 주군 요시노부의 절대적인 신뢰를 받았다.",
    372: "사타케 가신. 간조부교와 가로를 역임하며 형 노리타다와 함께 주군 요시노부의 두터운 신뢰를 받았다. 당시 번정을 기록한 《우메즈 마사카게 일기》는 역사학상 귀중한 사료다.",
    373: "아마고 가신. 수석 가로를 맡았다. 갓산토다성 농성전에서 사재를 털어 군량을 사 성병들에게 나누어 주었다. 뒤에 모리 모토나리의 이간책에 넘어간 주군 요시히사에게 살해되었다.",
    374: "우라가미 가신. 다이모쓰쿠즈레에서 당주 무라무네가 전사하고 어린 마사무네가 가독을 잇자 후견인으로 가문을 관리했다. 가문이 분열한 뒤 실각해 하리마를 떠났다고 한다.",
    375: "비젠의 센고쿠 다이묘. 무로쓰성주인 형 마사무네와 다투는 한편 비젠에서 세력을 넓혔다. 그러나 뒤에 대두한 가신 우키타 나오이에의 공격을 받아 거성에서 쫓겨났다.",
    376: "아카마쓰 가신. 무로쓰성주. 아들 기요무네에게 구로다 모토타카의 딸을 맞혀 모토타카의 주군 고데라 마사모토와 연계를 강화하려 했다. 그러나 혼례 당일 아카마쓰 마사히데의 습격을 받아 기요무네와 함께 전사했다.",
    377: "시마즈 가신. 주로 휴가 방면에서 활약했다. 로주를 맡아 주군 요시히사의 영국 경영을 보좌했다. 문예에도 조예가 깊어 《이세노카미 심득서》와 《우와이 가쿠켄 일기》를 지었다.",
    378: "시나노의 호족. 무네쓰나의 적장자. 시게노 일족의 종가로 세력을 유지했으나 운노다이라 전투에서 다케다 노부토라와 손잡은 이웃 호족 무라카미 요시키요·스와 요리시게 등에게 패해 전사했다.",
    379: "시나노의 호족. 운노 가문은 예로부터 시나노국 지사가타군 운노를 근거지로 삼은 호족이며, 네즈·모치즈키 가문은 그 방계라고 한다. 딸은 사나다 요리마사에게 시집가 유키타카를 낳았다.",
    380: "시마즈 가신. 미미가와 전투, 히고 미나마타성 공격, 오키타나와테 전투 등에 종군해 각지에서 공을 세웠다. 주군 요시히로는 ‘호히 전쟁의 승리는 모두 히사토라 덕분’이라고 말했다고 한다.",
    381: "류조지 가신. 류조지 다카노부의 둘째 아들로 에가미 가문의 가독을 이었다. ‘당대에 견줄 이 없는 괴력’을 지닌 용장으로 평가받아 각지의 전투에서 활약했다. 조선 출병에 종군했다가 부산에서 죽었다.",
    382: "쇼니 가신. 히젠 세이후쿠지성주. 류조지 다카노부의 가독 계승에 반대한 히가시히젠 19장의 한 사람. 류조지 가신 오다 마사미쓰를 죽이는 등 활약했으나 뒤에는 류조지 가신이 되었다.",
    383: "모가미 가신. 요시아키의 중신. 게이초 데와 전투에서 최전선의 하타야성에 적은 병력으로 농성해 우에스기군의 맹공을 막았다. 나오에 가네쓰구의 항복 권고를 단호히 거절하고 장렬한 최후를 맞았다.",
    384: "니와 가신. 도요토미 히데요시가 니와 가문의 영지를 줄여 많은 중신이 떠날 때도 계속 섬겼다. 세키가하라 전투의 아사이나와테 전투에서 마에다군을 야습해 큰 전과를 올렸다.",
    385: "히타치의 호족. 미토성주. 미치마사의 아들. 우에스기 가문과 손잡아 호조 가문에 맞섰다. 오다와라 정벌 뒤 미토성 인도를 거부하다 사타케 요시노부에게 쫓겨 유키령으로 달아났다.",
    386: "히타치의 호족. 미토성주. 미치야스의 아들. 처음에는 사타케 요시아쓰를 따랐으나, 요시아키가 가독을 잇자 적대하며 거듭 싸웠다. 뒤에 화해하고 다시 사타케 가문에 종속되었다.",
    387: "히타치의 호족. 미토성주. 다다미치의 아들. 타고난 병약함 때문에 곧 아들 시게미치에게 가독을 넘기고 미토성 밖 다케쿠마성에 칩거하다 병사했다. 가신에게 내린 관직 임명장의 사본이 남아 있다.",
    388: "소마 가신. 아키타네·모리타네·요시타네 3대를 섬기며 내정과 외교에서 활약했다. 요시타네를 따라 다무라 가문을 방문했을 때 다테 가문과 내통한 다무라 가신 다무라 겟사이의 저격을 받아 죽었다.",
    389: "히다의 호족. 도키모리의 적장자. 의견이 다른 아버지를 죽이고 동생 노부모리를 추방해 에마 가문을 장악했다. 혼노지의 변을 틈타 아네코지 요리쓰나를 쓰러뜨리려 했으나 도리어 살해되었다.",
    390: "히다의 호족. 스와성주. 미키 가문과 싸웠다. 다케다 가문과 우호를 맺으려 했으나 우에스기 가문과 관계를 맺자고 주장한 적장자 데루모리와 대립했고, 데루모리가 보낸 자객에게 살해되었다.",
    391: "히다의 호족. 도키모리의 아들. 우마노조라 칭했다. 처음에는 승려였으나 다케다 가문에 인질로 보내질 때 환속해 이후 다케다 가문을 섬겼다. 다카텐진성 공방전에서 전사했다.",
    392: "조소카베 가신. 요시다 시게토시의 둘째 아들로 에무라 지카마사의 사위가 되었다. 아버지처럼 빈고노카미라 칭해 ‘고빈고’라 불렸다. 많은 전투에 참가해 이웃 나라까지 용맹을 떨쳤다.",
    393: "조소카베 가신. 지카이에의 아들. 쓰노 지카타다가 도요토미 히데요시의 인질이 되었을 때 그를 따라 후시미로 갔다. 조선 출병 때도 바다를 건너 진주성 공격에 참가해 공을 세웠다.",
    394: "스에 가신. 주군 하루카타의 심복으로 활약했다. 오시키바타 전투 뒤 모리 모토나리의 권유를 받았으나 조건에 불만을 드러냈고, 모토나리가 내응 사실을 폭로해 하루카타에게 살해되었다.",
    395: "아키즈키 가신. 도요토미 히데요시의 규슈 정벌 때 거짓 항복 사절로 히데요시를 찾아갔다. 그 자리에서 항전이 불리함을 깨닫고 주군 다네자네에게 항복을 권했으나 도리어 노여움을 사 자결했다.",
    396: "류조지 가신. 류조지 사천왕의 한 사람. 오키타나와테 전투에서 주군 다카노부의 전사 소식을 듣자 홀로 시마즈 이에히사군 본진으로 돌입해 전사했다. 이에히사는 그를 ‘비할 데 없는 용사’라 칭찬했다.",
    397: "류조지 가신. 류조지 사천왕의 한 사람이라고 한다. 오키타나와테 전투에서 주군 다카노부의 전사 소식을 듣자 다카노부와 비슷한 차림을 하고 적진에 뛰어들어 싸우다 전사했다.",
    398: "다테 가신. 나카노 무네토키가 실각한 뒤 데루무네의 두터운 신임을 받아 숙로가 되었다. 정무를 맡고 오다 노부나가 등과 서신을 주고받았다. 데루무네가 죽은 뒤 그의 묘 앞에서 순사했다.",
    399: "미노의 호족. 구조하치만성주. 도요토미 히데요시를 섬겼다. 고마키·나가쿠테 전투 때 오다 가문과 내통했다는 의심을 받아 감봉되었다. 세키가하라 전투에서는 동군에 속해 전후 옛 영지를 되찾았다.",
    400: "우키타 가신. 주군 나오이에의 밀명을 받아 빗추에서 미마사카로 진출한 미무라 이에치카를 암살했다. 형과 함께 적지에 잠입해 화승총으로 이에치카를 저격하는 데 성공했다.",
    401: "니카이도 가신. 다지마라 칭했다. 주가 멸망 때 붙잡힌 뒤 다테 가문에 속했다. 무용이 뛰어나 세키가하라 전투에서 마쓰카와비시 깃발을 등에 지고 분전해 적과 아군 모두의 찬사를 받았다.",
    402: "아자이 가신. 가문 제일의 맹장으로 이름났다. 주군 나가마사에게 오다 노부나가 암살을 건의했으나 받아들여지지 않았다. 아네가와 전투에서 홀로 노부나가의 본진에 돌입해 전사했다.",
    403: "오고·스겐인이라고도 한다. 아자이 나가마사와 이치 사이에서 태어난 세 자매의 막내딸이다. 뒤에 도쿠가와 히데타다의 아내가 되어 에도 막부 제3대 쇼군 도쿠가와 이에미쓰를 낳았다.",
    404: "오다 노부나가의 누이. 아자이 나가마사에게 시집갔으나 나가마사가 자결한 뒤 친정으로 돌아왔다. 혼노지의 변 뒤 시바타 가쓰이에와 혼인해 에치젠 기타노쇼성에서 함께 자결했다. 절세의 미녀였다고 한다.",
    405: "조코인이라고도 한다. 아자이 나가마사와 이치 사이에서 태어난 세 자매의 둘째 딸이다. 오다니성 전투와 시즈가타케 전투에서 살아남아 교고쿠 다카쓰구의 아내가 되었다. 기독교에 귀의했다고 한다.",
    406: "나오에 가네쓰구의 정실. 도요토미의 천하가 이루어지자 우에스기 가게카쓰의 정실 기쿠히메를 따라 교토로 옮겼고, 뒤에 가네쓰구의 영지 요네자와로 갔다. 병사한 기쿠히메를 대신해 가게카쓰의 아들 사다카쓰를 길렀다.",
    407: "사나다 유키무라의 딸. 어머니는 다카나시 나이키의 딸이다. 오사카 전투에서 아버지를 따라 오사카성에 농성했다. 유키무라가 가타쿠라 시게나가에게 맡겨 성을 빠져나온 뒤 시게나가의 계실이 되었다.",
    408: "가사이 가신. 가시와기성주. 오키타 오이카와당의 우두머리였다. 1559년 지바 사부로 노부치카와 다툰 일을 계기로 가시와기성 사건이 일어났고, 오이카와당은 오하라 가문에 토벌되었다.",
    409: "벳쇼 가신. 오고성주. 하시바 히데요시군을 상대로 거성에 농성해 저항했다. 뒤에 미키성으로 들어가 주군 나가하루를 보좌했다. 하시바 가신 다니 모리토모를 죽인 전투에서 다친 뒤 자결했다.",
    410: "호조 우지마사의 정실. 다케다 신겐의 딸. 고소슨 삼국 동맹을 맺을 때 호조 가문에 시집갔다. 부부 금슬은 좋았으나 동맹 붕괴로 이혼해 가이로 돌아가 출가했고, 젊은 나이에 죽었다.",
    411: "다케다 가신. 본래 시나노의 호족으로 다케다 가문의 거듭된 공격 끝에 항복했다. 무라카미 요시키요·우에스기 노리마사와 내통했다가 다시 다케다 가문에 항복했다. 나가시노 전투에 출진해 전사했다.",
    412: "시나노의 호족. 이와무라다성주. 다케다 신겐의 시나노 침공군에 패해 거성을 잃고 나가쿠보성으로 물러났다. 그러나 그 성도 공격받아 생포되었으며 뒤에 살해되었다고 한다.",
    413: "야마노우치 우에스기 가신. 주가 멸망 뒤 우에스기 가게카쓰를 섬겼다. 가게카쓰의 아이즈 전봉을 따라 호바라 조다이가 되었다. 야스다 요시모토·이와이 노부요시와 함께 아이즈 삼봉행의 한 사람으로 꼽혔다.",
    414: "소 가신. 통칭 아라카와노스케. 가문 제일의 용장으로, 동생과 함께 맨손으로 호랑이와 싸워 퇴치했다는 전설도 남아 있다. 쓰시마 사고 군다이에 임명되었다.",
    415: "야마노우치 우에스기 가신. 오이시 가문은 기소 요시나카의 아들 요시무네를 시조로 한다. 무사시 슈고다이를 지냈다. 주가 멸망 뒤 호조 가문에 항복하고 호조 우지야스의 둘째 아들 우지테루에게 가독을 넘긴 뒤 은거했다.",
    416: "우에스기 가신. 나가오 후사나가의 둘째 아들. 오이다 우지카게의 데릴양자가 되었다. 우에스기 겐신 아래서 간토 출병 등에 활약했고 가게카쓰의 측근으로도 섬겼으나, 돌연 할복 명령을 받고 자결했다.",
    417: "스오 오우치 가문의 일문. 사촌 요시타카와 대립해 분고 오토모 가문으로 달아나 보호받았다. 뒤에 소린의 지원을 받아 오우치 가문 재흥을 위해 옛 영지 스오에서 거병했으나 모리 가문에 패해 자결했다.",
    418: "오우치 가문 제30대 당주. 달아온 전 쇼군 아시카가 요시타네를 옹립하고 호소카와 다카쿠니와 손잡아 상경했다. 간레이 대리로 10년 동안 막부 정치를 맡았다. 귀국 뒤 아마고·아키 다케다 가문과 싸웠다.",
    419: "다무라 가신. 오바마성주. 사다쓰나의 아버지. 이시바시 사천왕의 한 사람으로 이시바시 가문을 섬겼으나 다무라 가문과 내통해 주군 히사요시를 추방하고 시오마쓰 지방의 실권을 장악했다.",
    420: "오우치 가문 제32대 당주. 오토모 요시아키의 아들. 오우치 요시타카가 죽은 뒤 스에 하루카타의 옹립을 받아 오우치 가문을 이었다. 이쓰쿠시마 전투에서 하루카타가 전사한 뒤 모리군의 계속된 침공을 받다가 자결했다.",
    421: "오우치 가문 제31대 당주. 7개 구니의 슈고를 맡아 주고쿠와 규슈에 패권을 떨쳤다. 양사자 하루모치가 죽은 뒤 문예에 몰두해 독자적인 문화를 이뤘으나 가신 스에 하루카타의 모반을 받아 자결했다.",
    422: "아시나 가신. 오우치 사다쓰나의 동생. 1589년 형의 주선으로 다테 가문에 귀속되어 500석을 받았다. 스리아게하라 전투에서 형과 함께 좌우를 굳게 지켜 공을 세웠고 전후 가증되었다.",
    423: "무쓰의 호족. 시오마쓰성주. 다테 마사무네가 당주가 되자 귀속했으나 곧 적대했다. 마사무네의 공격을 받아 패한 뒤에는 다테 가문을 섬겼다. 창술에 뛰어났다.",
    424: "히로사키번 초대 번주. 오우라 다메노리의 딸을 아내로 맞았다. 주가 난부 가문에서 독립해 17년에 걸쳐 쓰가루를 통일했다. 도요토미 히데요시의 오다와라 정벌에 참진해 정식으로 쓰가루 영주가 되었다.",
    425: "난부 가신. 마사노부의 적장자. 오우라성주. 아버지가 죽은 뒤 가독을 이었다. 타고난 병약함 때문에 뒤에 딸 이누의 사위로 오우라(쓰가루) 다메노부를 맞아 후계자로 삼았다.",
    426: "쓰가루의 무장. 마사노부의 아들. 당주인 형 다메노리가 병약해 대신 정무를 맡았다고 한다. 쓰가루 다메노부의 친아버지로 전해진다.",
    427: "쓰가루 가신. 쓰가루 다메노부의 적장자. 쓰가루 가문은 다메노부의 활약으로 난부 가문에서 독립했고 세키가하라 전투의 공으로 지위를 굳혔으나, 노부타케는 아버지보다 먼저 병사했다.",
    428: "히로사키번 제2대 번주. 다메노부의 셋째 아들. 어린 시절 아버지의 권유로 세례를 받았다. 두 형이 일찍 죽어 아버지 사후 가독을 이었다. 히로사키성을 쌓는 등 번의 기반을 다졌다.",
    429: "난부 가신. 오우라성주. 제멋대로여서 가신들의 신망을 얻지 못했다. 와토쿠성 공격에서 전사했으나 아군은 이를 모른 채 퇴각했고, 성에 돌아온 뒤에야 주군이 없다는 사실을 알았다고 한다.",
    430: "난부 가신. 미쓰노부의 적장자. 1502년 아버지의 명으로 새로 쌓은 오우라성의 성주가 되었다. 1528년 아버지의 명복을 빌기 위해 다네사토성 아래에 조쇼지를 세웠다.",
    431: "가마치 가신. 류조지 가문에서 시마즈 가문으로 돌아서려던 주군 시게나미가 류조지 다카노부의 초청을 받자 방문을 만류했다. 그러나 시게나미는 다카노부를 찾아갔다가 살해되었다.",
    432: "도쿠가와 가신. 형 다다토시와 함께 주군 히로타다가 오카자키성으로 돌아오는 데 힘썼고 가니에성 공격에서도 활약했다. 미카와 잇코잇키 때 일족과 가미와다 요새에 농성해 봉기군과 싸웠다.",
    433: "도쿠가와 가신. 다다카즈의 아들. 통칭 히코자에몬. 다카텐진성 공격에서 오카베 모토노부를 죽였다. 많은 로닌을 보호해 의협심 있는 무사로 흠모받았다. 말년에 《미카와 이야기》를 지었다.",
    434: "도쿠가와 가신. 다다카즈의 둘째 아들. 형 다다요와 함께 각지에서 전공을 세웠다. 그 용맹함은 오다 노부나가도 감탄할 정도였다. 세키가하라 전투 뒤 스루가 누마즈 2만 석을 받았다.",
    435: "도쿠가와 가신. 주군 히로타다가 오카자키성으로 돌아오는 데 힘썼다. 미카와 잇코잇키가 일어나자 주군 이에야스를 도와 봉기군을 격파하는 등 주가의 고난기를 줄곧 떠받친 충신이다.",
    436: "도쿠가와 가신. 다다카즈의 맏아들. 미카타가하라·나가시노 전투 등 많은 전투에 종군해 호방한 성격으로 뛰어난 공을 세웠고, 오다 노부나가와 도요토미 히데요시에게도 높은 평가를 받았다.",
    437: "도쿠가와 가신. 다다요의 적장자. 도쿠가와 히데타다의 쓰케가로를 맡았다. 히데타다와 직참 하타모토들의 절대적인 신뢰를 받았으나, 뒤에 정적 혼다 마사노부의 실각 공작으로 개역되었다.",
    438: "도쿠가와 가신. 막부 직할령 통괄, 신기술을 이용한 금은 채굴, 이정표와 역참 설치 등 막부의 민정과 재정에 크게 기여해 ‘천하의 총대관’이라 불렸다.",
    439: "나가오 가신. 미카부리성주. 주군 가게토라의 측근으로 정무에 참여했다. 가게토라의 출가 소동을 틈타 모반했으나 실패했다. 이후 다케다 가문을 섬겼고 가이 덴모쿠산에서 전사했다.",
    440: "오사키 가문 제11대 당주. 다테 다네무네의 아들. 오사키 다카카네의 딸 우메카를 아내로 맞아 가독을 이었다. 덴분의 난 때 다네무네 편에 서서 오사키 요시나오와 싸웠고, 전후 가사이령으로 달아나다 살해되었다.",
    441: "오사키 가문 제12대 당주. 다테 다네무네의 도움으로 가신의 모반을 진압하는 등 점차 세력을 잃었다. 덴분의 난 때 다테 하루무네를 도와 다네무네 편의 오사키 요시노부와 싸웠다.",
    442: "오사키 가문 제13대 당주. 요시나오의 아들. 다테 마사무네의 대군을 한 차례 물리쳤으나 뒤에 그 휘하로 들어갔다. 도요토미 히데요시의 오다와라 정벌에 늦게 참진해 개역되었고 우에스기 가게카쓰를 섬겼다.",
    443: "도쿠가와 가신. 야스타카의 양사자. 친아버지는 사카키바라 야스마사다. 이에야스의 간토 전봉을 따라 가즈사 구루리 3만 석을 받았다. 세키가하라 전투 뒤 도토미 요코스카로 옮겨 번정의 기반을 다졌다.",
    444: "나스 7당의 한 사람. 오타와라 스케키요의 아들. 오제키·오타와라·후쿠하라 가문을 이끌고 이오노·아시노 가문과 손잡았으며, 큰할아버지뻘로서 주군 스케하루를 후견하는 등 가문 내 최대 세력을 구축했다.",
    445: "나스 7기의 한 사람. 다카마스의 셋째 아들. 형 하루마스가 죽은 뒤 시모쓰케 구로바네 1만 3천 석을 이었다. 세키가하라 전투에서 동군에 속해 본령을 인정받았고, 뒤에 형의 아들 마사마스에게 가독을 넘겼다.",
    446: "나스 가신. 후쿠하라 스케야스와 함께 오타와라 스케키요를 주군 스케후사에게 참소해 쫓아냈다. 뒤에 돌아온 스케키요에게 아들 마스쓰구를 잃고, 스케키요의 아들 다카마스에게 오제키 가문을 빼앗겼다.",
    447: "니와 가신. 주가 몰락 뒤 도요토미 히데요시를 섬겼다. 세키가하라 전투에서 서군에 속해 거성 분고 우스키성에 농성했으나 주력군의 패배로 성을 열었다. 이후 교토에 은거했다.",
    448: "오다 가신. 시바타 가쓰이에를 섬겼으나 활 솜씨를 인정받아 노부나가의 직신이 되었다. 문재도 뛰어났으며 노부나가의 생애를 기록한 《신초코키》로 특히 유명하다.",
    449: "호조 가신. 스케타카의 아들. 뒤에 사토미 가문에 속해 제2차 고노다이 전투에 종군했다. 다케다·우에스기 가문에 사자를 보내는 등 외교에서도 활약했다. 30명 몫의 힘을 지닌 호걸이었다고 한다.",
    450: "호조 가신. 이와쓰키성주. 스케마사의 적장자. 아버지의 미움을 사 아버지와 동생을 쫓아내고 이와쓰키성주가 되었다. 미후네야마 전투에서 호조군 후군을 맡아 사토미군과 싸우다 전사했다.",
    451: "오기가야쓰 우에스기 가신. 이와쓰키성주. 스케요리의 적장자. 1535년 아버지가 은거하자 가독을 이었다. 가와고에 야전에서 주군 도모사다가 호조군에 패사한 뒤 호조 가문에 속했다.",
    452: "오기가야쓰 우에스기 가신. 호조 가문과 내통해 에도성을 점거하고 주군 도모오키를 가와고에성으로 몰아냈다. 뒤에 호조 가신 도야마·도미나가 두 가문과 함께 에도성을 지켰으며 고즈키테이에 살았다고 한다.",
    453: "오기가야쓰 우에스기 가신. 이와쓰키성주. 스케요리의 둘째 아들. 주가 멸망 뒤 우에스기·사타케 가문에 속해 평생 호조 가문과 싸웠다. 도요토미 히데요시의 오다와라 정벌 때 히데요시의 본진을 방문했다.",
    454: "기이의 호족. 오타성주. 사콘이라 칭했다. 도요토미 히데요시의 기슈 정벌에서 대군을 상대로 선전했으나 거성이 수공을 받아 한 달간 농성한 끝에 항복하고 자결했다.",
    455: "도쿠가와 가신. 야스스케의 아들. 처음에는 아버지와 함께 사토미 가문에 속했다. 아버지가 죽은 뒤 사타케 가문에 속한 오타 스케마사를 의지했다. 뒤에 도쿠가와 이에야스를 섬겼고 누이는 이에야스의 측실이 되었다.",
    456: "사타케 가신. 오타 스케마사의 둘째 아들. 데바이자카 전투에서 오다 우지하루를 격파해 오다성주가 되었다. 주가의 아키타 전봉을 따랐으나 뒤에 에치젠 후쿠이번주 유키 히데야스를 섬겼다.",
    457: "기이의 호족. 오타성주. 사이카당과 거듭 싸웠다. 고마키·나가쿠테 전투 때 도쿠가와 이에야스의 요청에 응해 싸웠다. 도요토미 히데요시의 기슈 정벌에서는 거성이 수공을 받아 패했다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    353: ["koshidake_castle_and_jotoku_office_terms_require_glossary_review"],
    354: ["kaerikumo_castle_reading_requires_castle_catalog_review"],
    356: ["taka_castle_reading_requires_castle_catalog_review"],
    360: ["takeshige_kageyasu_reading_requires_officer_catalog_review"],
    362: ["jizogatake_and_torisaka_place_readings_require_catalog_review"],
    363: ["moto_castle_and_hagimori_epithet_require_context_review"],
    377: ["book_title_renderings_require_glossary_review"],
    380: ["hohi_war_term_requires_glossary_review"],
    382: ["seifukuji_castle_reading_requires_castle_catalog_review"],
    392: ["kobingo_epithet_rendering_requires_glossary_review"],
    401: ["matsukawabishi_banner_term_requires_glossary_review"],
    403: ["ogo_and_sugenin_name_forms_require_glossary_review"],
    408: ["okita_oikawa_faction_term_requires_context_review"],
    413: ["aizu_three_magistrates_name_readings_require_catalog_review"],
    439: ["mikaburi_castle_reading_crosschecked_but_requires_catalog_review"],
    440: ["umeka_name_reading_requires_officer_catalog_review"],
    452: ["kozukitei_residence_reading_requires_glossary_review"],
    456: ["tebaizaka_battle_reading_crosschecked_but_requires_glossary_review"],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def write_json(path: Path, value: Any) -> dict[str, Any]:
    return shared.write_json(path, value)


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != 107:
        raise ValueError("batch4 translations must exactly cover IDs 351-457")
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
        raise ValueError("next-start boundary ID 458 must be non-empty in all languages")

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
        "schema": "nobu16.kr.msgbre-alignment-evidence.v4",
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
            "officer_name_overlay_id_crosscheck",
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
        "schema": "nobu16.kr.msgbre-review-index.v4",
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
        "schema": "nobu16.kr.msgbre-generation-validation.v4",
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
            "natural_boundary": {
                "last_completed_family": "ota",
                "next_family": "otaka",
                "officer_name_ids_crosschecked": len(ids) + 1,
            },
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
            "existing_v01_v02_v03_artifacts_modified": False,
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
