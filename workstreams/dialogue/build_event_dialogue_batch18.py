#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch18 (5238-5358)."""

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
TOOLS_DIR = SCRIPT_PATH.parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch2 as source_shared  # noqa: E402
import build_event_dialogue_batch17 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_5238_5358.v0.18"
OVERLAY_NAME = "msgev_ko_historical_events_5238_5358.v0.18.json"
EVIDENCE_NAME = "alignment_evidence.v0.18.json"
REVIEW_NAME = "review_index.v0.18.json"
VALIDATION_NAME = "validation.v0.18.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 5238
SCOPE_END = 5358
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "imagawas_decline_and_takeda_policy_shift",
        "title_ko": "이마가와의 몰락과 다케다의 방침 전환",
        "start_id": 5238,
        "end_id": 5255,
        "selected_count": 18,
    },
    {
        "event_id": "eiroku_incident_and_yoshiaki_rescue",
        "title_ko": "에이로쿠의 변과 요시아키 구출",
        "start_id": 5256,
        "end_id": 5293,
        "selected_count": 38,
    },
    {
        "event_id": "nanbu_nobunao_adopted_as_heir",
        "title_ko": "난부 노부나오의 후계자 입양",
        "start_id": 5294,
        "end_id": 5299,
        "selected_count": 6,
    },
    {
        "event_id": "yoshiaki_asks_nobunaga_to_enter_kyoto",
        "title_ko": "요시아키의 상경 요청과 아케치 미쓰히데",
        "start_id": 5300,
        "end_id": 5337,
        "selected_count": 38,
    },
    {
        "event_id": "ukita_naoie_assassinates_mimura_iechika",
        "title_ko": "우키타 나오이에의 미무라 이에치카 암살",
        "start_id": 5338,
        "end_id": 5349,
        "selected_count": 12,
    },
    {
        "event_id": "matsudaira_ieyasu_becomes_tokugawa",
        "title_ko": "마쓰다이라 이에야스의 도쿠가와 개성",
        "start_id": 5350,
        "end_id": 5358,
        "selected_count": 9,
    },
)

TRANSLATIONS: dict[int, str] = {
    5238: "\x1bCA이마가와 요시모토\x1bCZ의 죽음은 \x1bCC도카이\x1bCZ의\n큰 다이묘 하나의 몰락을 넘어, \x1bCC간토\x1bCZ와 \x1bCC고신\x1bCZ에도\n커다란 파문을 일으켰다.",
    5239: "그 까닭은 \x1bCB이마가와 가문\x1bCZ과 고소슨 삼국 동맹을 맺은\n\x1bCB다케다 가문\x1bCZ과 \x1bCB호조 가문\x1bCZ도\n방침을 바꾸어야 했기 때문이다.",
    5240: "이제 \x1bCA요시모토\x1bCZ도 죽었고 \x1bCB이마가와 가문\x1bCZ은 믿을 수 없다.\n이 기회에 쳐서 \x1bCC스루가\x1bCZ를 빼앗아야 한다.",
    5241: "가신 대부분이 그렇게 간하고 있다.\n\x1bCA겐시로\x1bCZ, 너는 어찌 생각하느냐?",
    5242: "저도 같은 생각입니다.",
    5243: "그 일에 관해 할 말이 있어 온 것이겠지?",
    5244: "……예, 말씀하신 대로입니다.\n실은――",
    5245: "네 형 \x1bCA도라마사\x1bCZ가 모반을 꾀한다는\n그 일을 말하려는 것이겠지?",
    5246: "알고 계셨습니까……",
    5247: "\x1bCA도라마사\x1bCZ도 그저 휘말렸을 뿐이다.\n정말로 나를 죽이려는 자는……",
    5248: "\x1bCA다로 요시노부\x1bCZ, 내 아들이겠지……\n그 아이의 아내는 \x1bCB이마가와 가문\x1bCZ 출신이니,\n끝내 \x1bCB이마가와\x1bCZ와 연을 끊지 못할 게야.",
    5249: "……그렇습니다.",
    5250: "허, 죽은 \x1bCA다이겐 셋사이\x1bCZ가 참으로\n성가신 족쇄를 남겼구나.",
    5251: "\x1bCA요시노부\x1bCZ 편에 선 가신이 네 형뿐일 리는\n없을 터――\n언젠가는 결판을 내야겠구나……",
    5252: "예! 주군,\n제 형이 베임을 당한다 해도 각오했습니다.\n이 몸을 \x1bCB다케다\x1bCZ에 바치겠습니다.",
    5253: "네 충절을 의심한 적은 없다.\n하지만…… 너희 형제가 다투게 하는 일은\n내게도 괴로운 일이구나……",
    5254: "전국시대에는 흔한 일입니다.\n주군께서도 부자간의 연을 끊으시는데,\n제 일쯤이야……",
    5255: "생각해 보면 나도 아버지와 맞서,\n이 손으로 아버지를 \x1bCC스루가\x1bCZ로 내쫓았지.\n아들과 다투는 것도 그 업보인가……",
    5256: "제13대 쇼군 \x1bCA[b75]\x1bCZ은 막부 재건을 위해 힘썼다.",
    5257: "반면 당주 \x1bCA나가요시\x1bCZ를 잃은 \x1bCB미요시 가문\x1bCZ은,\n\x1bCC기나이\x1bCZ에서 세력이 급속히 약해져 큰 위기감을 느꼈다.",
    5258: "\x1bCA나가요시\x1bCZ 님이 돌아가신 뒤 공방은\n우리를 무시하고 제멋대로 정사를 펼친다.\n우리 힘 없이는 홀로 설 수도 없으면서……",
    5259: "우리는 쇼군의 권위를 가마에 태워\n\x1bCC기나이\x1bCZ에 세력을 세웠다.\n말을 듣지 않는 가마라면…… 끌어내리지.",
    5260: "하지만 그 공방은 여간 성가신 자가 아니다.\n은거시키거나 가두어도 다시 일어날 터……\n차라리 죽여 버리자.",
    5261: "미요시 삼인중과 \x1bCA마쓰나가 히사미치\x1bCZ 등이\n쇼군 \x1bCA아시카가 요시테루\x1bCZ를 죽이려 한다는 소문은,\n\x1bCB미요시\x1bCZ 가신들 사이에 공공연히 퍼져 있었다.",
    5262: "쯧쯧…… 구제할 길 없는 자들이군.\n한때 \x1bCC기나이\x1bCZ에 군림한 \x1bCB미요시 가문\x1bCZ이\n\x1bCA나가요시\x1bCZ 님 한 분의 죽음에 이리 헤매다니……",
    5263: "공방 따위 적당히 가두어 두면 될 것을,\n굳이 제 손을 더럽힐 필요가 있나.",
    5264: "쇼군을 시해했다는 오명까지 뒤집어쓸 텐데……\n내 아들 \x1bCA히사미치\x1bCZ마저 삼인중에게 동조하다니,\n참으로 부끄러운 노릇이군.",
    5265: "그러나 \x1bCA히사히데\x1bCZ의 우려를 비웃듯,\n사태는 급격히 흘러갔다.",
    5266: "며칠 뒤, 미요시 삼인중과 \x1bCA마쓰나가 히사미치\x1bCZ는\n쇼군에게 아뢸 일이 있다는 구실로 군사를 이끌고,\n\x1bCC교토\x1bCZ의 \x1bCA요시테루\x1bCZ 거처로 몰려갔다.",
    5267: "격한 상소는 이내 작은 충돌로 번졌고,\n마침내 뜻밖의 전투로 커지고 말았다.",
    5268: "이 \x1bCB미요시 가문\x1bCZ의 역적놈들……",
    5269: "무가의 동량을 무엇으로 아느냐!\n한 발짝이라도 다가오면 베어 버리겠다!",
    5270: "쇼군, 각오하라!",
    5271: "흥……",
    5272: "크윽!",
    5273: "일설엔 \x1bCA[bm75]\x1bCZ이 \x1bCA쓰카하라 보쿠덴\x1bCZ의 검을 익혔다.\n그 검 앞에서 \x1bCB미요시\x1bCZ 병사들은 속수무책이었다.\n하지만 그것도 시간문제일 뿐이었다……",
    5274: "수가 너무 적었다.\n무로마치 공방의 저택에 구원군을 보낸 자도 없었고,\n\x1bCA[bm75]\x1bCZ은 잡병을 베어 내다 지쳐 갔다……",
    5275: "후, 후후후……\n막부가 다시 일어서는 모습을 보지 못하고\n쓰러지는 것은 참으로 원통하나……",
    5276: "이 검을 적에게 마음껏 휘두를 기회를 얻었으니,\n그것만은 다행이로다.",
    5277: "자, 덤벼라!\n공방을 해치려는 역적들아!\n내 이치노타치를 맛보아라!",
    5278: "\x1bCC교토\x1bCZ·\x1bCA호소카와 후지타카\x1bCZ 저택――",
    5279: "뭐라고? 어소에 변고가 생겼다고!?\n……이 \x1bCB미요시\x1bCZ와 \x1bCB마쓰나가\x1bCZ의 역적들!",
    5280: "안타깝지만 공방을 도울 수 없겠네……\n\x1bCB미요시\x1bCZ 군이 이미 어소를 에워쌌어.",
    5281: "구원군도 소용없겠군…… 공방께는 죄송하지만,\n우리 가신들은 그다음을 생각해야 하네!\n\x1bCB아시카가 쇼군가\x1bCZ의 앞날을……",
    5282: "\x1bCC난토\x1bCZ…… \x1bCC고후쿠지\x1bCZ로 가세!\n그곳에 공방의 아우 \x1bCA이치조인 가쿠케이\x1bCZ 님이 계시네.\n쇼군가의 혈통을 여기서 끊을 수는 없어!",
    5283: "\x1bCC난토\x1bCZ를 포함한 \x1bCC야마토\x1bCZ는 \x1bCA마쓰나가 히사히데\x1bCZ의 세력권……\n내버려 두면 \x1bCA가쿠케이\x1bCZ 님이 \x1bCA히사히데\x1bCZ에게 죽는다.\n우리가 가서 막아야 하네!",
    5284: "이 일련의 사건은 ‘에이로쿠의 변’이라 불린다.\n제13대 쇼군 \x1bCA[b75]\x1bCZ은 목숨을 잃고,\n막부의 기능은 멈추었다.",
    5285: "결국 저질렀나…… 어리석은 놈들!\n쇼군을 죽였다는 오명을 뒤집어쓸 줄 알면서도,\n어찌 그리 어리석단 말이냐!",
    5286: "\x1bCA히사미치\x1bCZ마저 삼인중의 꾐에 넘어가,\n공방 암살에 가담하다니…… 이제 \x1bCB미요시 가문\x1bCZ도\n물러설 곳이 없겠구나.",
    5287: "그러나 세상일은 제멋대로인 법――",
    5288: "\x1bCA히사미치\x1bCZ가 암살에 가담했다는 이유로,\n‘쇼군 살해의 배후는 \x1bCA마쓰나가 히사히데\x1bCZ’라는 소문이\n\x1bCC기나이\x1bCZ를 넘어 온 나라에 퍼졌다.",
    5289: "하지만 이는 \x1bCA히사히데\x1bCZ의 계략이며,\n그 오명을 거꾸로 이용해 주군 \x1bCA나가요시\x1bCZ의\n여러 아우를 제거했다는 소문도 돌았다.",
    5290: "그러나 그 악명 때문에 그는\n시해의 주모자로 지목되었고,\n여러 다이묘의 증오를 받게 되었다.",
    5291: "한편 미요시 삼인중은 공방이 죽은 뒤,\n\x1bCC교토\x1bCZ를 장악했으나 공동의 적을 잃자\n곧 \x1bCA히사미치\x1bCZ와 맞서기 시작했다……",
    5292: "미요시 삼인중과 \x1bCB마쓰나가 가문\x1bCZ의 대립은\n갈수록 선명해져 갔다……",
    5293: "막부의 옛 신하들은 \x1bCA호소카와 후지타카\x1bCZ를 중심으로\n\x1bCA요시테루\x1bCZ의 아우 \x1bCA가쿠케이\x1bCZ를 구출해 환속시키고,\n\x1bCA아시카가 요시아키\x1bCZ라 이름 붙였다.",
    5294: "에이로쿠 8년(1565),\n아들이 없던 \x1bCB난부 가문\x1bCZ의 당주 \x1bCA난부 하루마사\x1bCZ는\n\x1bCA이시카와 다카노부\x1bCZ의 아들 \x1bCA노부나오\x1bCZ를 데릴사위로 맞았다.",
    5295: "\x1bCA노부나오\x1bCZ.\n이제부터 네가 \x1bCB난부 가문\x1bCZ의 후계자다.\n네 아버지 못지않게 활약하기를 기대하마.",
    5296: "예.\n\x1bCB난부 가문\x1bCZ을 위해,\n목숨을 걸고 힘쓰겠습니다.",
    5297: "\x1bCA하루마사\x1bCZ의 숙부인 \x1bCA이시카와 다카노부\x1bCZ는 용장이었고,\n\x1bCB난부 가문\x1bCZ의 발전에 크게 이바지했다.",
    5298: "\x1bCA다카노부\x1bCZ의 아들을\n후계자로 맞으면 \x1bCB난부 가문\x1bCZ도 태평할 것이라고,\n그때는 모두가 생각했다.",
    5299: "후계자가 없는 다이묘가 양자를 들인다.\n그것이 비극의 시작이 되기도 했다……\n전국시대에는 흔한 광경이었다.",
    5300: "무로마치 막부 제13대 쇼군 \x1bCA[b75]\x1bCZ이\n암살된 뒤, 승려였던 아우 \x1bCA아시카가 요시아키\x1bCZ는\n환속하여 막부 재건을 뜻했다.",
    5301: "\x1bCA요시아키\x1bCZ는 각지 다이묘에게 상경을 재촉했다.\n그중에는 \x1bCA오다 노부나가\x1bCZ도 있었으며,\n막부의 중재로 \x1bCB사이토 가문\x1bCZ과 화친한 상태였다.",
    5302: "그러나 \x1bCB오다 가문\x1bCZ과 \x1bCB사이토 가문\x1bCZ의 화친이 깨져,\n\x1bCA노부나가\x1bCZ의 상경은 이루어지지 못했다.",
    5303: "그동안 \x1bCA요시아키\x1bCZ는 \x1bCC오미\x1bCZ, \x1bCC와카사\x1bCZ, \x1bCC에치젠\x1bCZ을 떠돌았다.\n마침내 \x1bCB아사쿠라 가문\x1bCZ의 보호를 받았으나,\n상경할 길은 전혀 보이지 않았다……",
    5304: "하지만 \x1bCA오다 노부나가\x1bCZ가 \x1bCB미노 사이토 가문\x1bCZ을 무너뜨리고,\n\x1bCC기후\x1bCZ로 거처를 옮기자 다시 상경을 청하고자,\n\x1bCA요시아키\x1bCZ는 \x1bCA호소카와 후지타카\x1bCZ를 사자로 보냈다.",
    5305: "우선 이번 승전을\n축하드립니다.",
    5306: "승전……\n아, 이 \x1bCC미노\x1bCZ를 말씀하시는군.",
    5307: "\x1bCA노부나가\x1bCZ 님이 \x1bCC미노\x1bCZ를 거쳐 상경하시길 바라,\n그 뜻으로 \x1bCB사이토\x1bCZ와의 사이를\n중재했던 것입니다만.",
    5308: "그러나 \x1bCB사이토\x1bCZ의 무도함으로 화의가 깨져,\n기대에 부응하지 못했습니다. 송구합니다.",
    5309: "그 일은 됐습니다.\n그보다 이제 \x1bCC교토\x1bCZ로 들어가,\n\x1bCA요시아키\x1bCZ 님을 도와주시겠습니까?",
    5310: "그것은 본디 이 \x1bCA노부나가\x1bCZ의 뜻이었소.\n\x1bCA요시아키\x1bCZ 님께도 그리 전해 주시오.",
    5311: "고맙습니다.\n이제 저도 체면이 서는군요.",
    5312: "참, 앞으로 우리 사이의 연락은\n이 사람을 통하게 하십시오.\n말솜씨도 무예도 뛰어난 사내입니다.",
    5313: "처음 뵙겠습니다…… 저는 \x1bCA요시아키\x1bCZ 님을 모시는\n\x1bCA아케치 주베에\x1bCZ라 합니다.\n무슨 일이든 제게 맡겨 주십시오.",
    5314: "그러면 나는 이만.\n\x1bCA주베에\x1bCZ 공, 뒤를 부탁하네.",
    5315: "후…… \x1bCA[b\x1bCB1773]\x1bCZ, \x1bCA[bm1773]\x1bCZ였던가.\n제법 유능한 듯하나,\n\x1bCC교토\x1bCZ에서 자란 이 특유의 비꼬는 말투는 여전하군.",
    5316: "이제 협력을 구할 상대 앞에서\n\x1bCA[b929]\x1bCZ 같은 자의 이야기를 꺼내다니……\n뭐, 됐다.",
    5317: "\x1bCA주베에\x1bCZ라 했지. 이제 편히 이야기하자.\n너도 격식을 차리지 마라.",
    5318: "고맙습니다.",
    5319: "그러고 보니…… \x1bCA[bm1773]\x1bCZ이 네 솜씨를 칭찬하더군.\n그자도 쓰카하라 보쿠덴류의 검객이라 들었다.\n그가 칭찬한 네 실력은 어느 정도냐?",
    5320: "말씀드릴 만큼 대단하지는 않습니다.\n검은 그저 막대기를 휘두르는 정도일\n뿐입니다만……",
    5321: "하지만…… 뭐냐?",
    5322: "여러 나라를 떠돌 때 인연이 닿아,\n조총 솜씨를 조금 익혔습니다.",
    5323: "오! 조총인가!\n우리 가문에도 다룰 줄 아는 자가 많다!",
    5324: "좋아, 네 솜씨를 보고 싶군.\n밖으로 나가 보여 주겠느냐?",
    5325: "상경 이야기는 어찌하시겠습니까?",
    5326: "상관없다. \x1bCC교토\x1bCZ야 언제든 갈 수 있지.\n그보다…… \x1bCA주베에\x1bCZ, \x1bCC교토\x1bCZ에 들어가면\n공방께서 내게 무엇을 줄 수 있느냐?",
    5327: "온 일본에 떨칠 무위라고 말씀드리고 싶으나……\n지금 \x1bCB아시카가 가문\x1bCZ의 위세는\n기껏해야 \x1bCC기나이\x1bCZ에나 미칠 정도입니다.",
    5328: "하지만 그 \x1bCC기나이\x1bCZ야말로 중요합니다.\n사람과 장사, 사찰과 권문세가가 모인,\n곧 ‘천하’라 불리는 땅이지요……",
    5329: "즉 \x1bCC기나이\x1bCZ를 장악하는 것이 천하포무다.\n옛 권위를 이용해 새로운 세상을 만든다.\n그렇게 말하고 싶은 게로군?",
    5330: "명찰하셨습니다……",
    5331: "마음에 들었다, \x1bCA주베에\x1bCZ.\n\x1bCC교토\x1bCZ 사람들의 에두르는 말에는 질렸는데……\n너는 말이 빠르구나.",
    5332: "자, \x1bCC교토\x1bCZ 이야기는 여기까지다.\n뜰로 나가 나와 조총 솜씨를 실컷 겨루자!\n하하하!",
    5333: "후후……\n오와리의 멍청이, 소문대로의 사내로군.\n평범한 멍청이가 아니야. 파격 그 자체다.",
    5334: "\x1bCA아케치 미쓰히데\x1bCZ의 전반생은 수수께끼에 싸여 있다.",
    5335: "\x1bCC미노\x1bCZ 출신으로 \x1bCB사이토 가문\x1bCZ을 섬겼다거나,\n\x1bCA노히메\x1bCZ의 친척이었다거나, \x1bCB아사쿠라 가문\x1bCZ의 가신이었다거나……\n여러 설이 있으나 어느 것도 확실하지 않다.",
    5336: "\x1bCA노부나가\x1bCZ가 천하포무를 내걸고 \x1bCC교토\x1bCZ로 향할 무렵,\n기록에 이름을 드러낸 그는 마침내 \x1bCB오다 가문\x1bCZ의\n손꼽히는 실력자로 성장한다.",
    5337: "\x1bCA노부나가\x1bCZ와 \x1bCA미쓰히데\x1bCZ,\n운명적인 두 사람의 길이 이렇게 교차하기 시작했다.",
    5338: "용맹으로 이름난\n\x1bCC빗추\x1bCZ의 \x1bCB미무라 가문\x1bCZ 당주 \x1bCA미무라 이에치카\x1bCZ에게\n고전하던 \x1bCA우키타 나오이에\x1bCZ는 한 가지 계책을 냈다.",
    5339: "옛 지인인 낭인 \x1bCA엔도\x1bCZ 형제에게\n조총으로 \x1bCA이에치카\x1bCZ를 암살하라고 의뢰했다.",
    5340: "당시 조총을 이용한 저격은 드물었고,\n신뢰성도 낮아 \x1bCA엔도\x1bCZ 형제는 난색을 보였으나,\n실패를 각오하고 의뢰를 받아들였다.",
    5341: "그리고 며칠 뒤――",
    5342: "보고드립니다!\n\x1bCB미무라\x1bCZ 군이 철수를 시작했습니다!",
    5343: "그런가……\n역시 \x1bCA이에치카\x1bCZ는 죽었군.\n화승총, 의외로 쓸 만하구나.",
    5344: "\x1bCA엔도\x1bCZ 형제는 밤의 어둠에 숨어 \x1bCA이에치카\x1bCZ를 저격했다.\n그러나 어둠이 너무 깊어\n성공 여부를 확인할 수 없었다.",
    5345: "\x1bCA나오이에\x1bCZ는 \x1bCB미무라군\x1bCZ이 철수하는 것을 보고서야,\n저격의 성공을 확신했다.",
    5346: "많은 병사는 필요 없다.\n이 총 한 자루면 사람을 죽일 수 있다.",
    5347: "비겁하다는 말을 들어도,\n암살은 헛되이 죽는 자가 없게 한다.\n결코 꺼릴 일이 아니지……",
    5348: "몇 년 뒤,\n그 유명한 \x1bCA스기타니 젠주보\x1bCZ의\n\x1bCA오다 노부나가\x1bCZ 저격 미수 사건이 일어난다.",
    5349: "현대에는 드물지 않은 저격 암살.\n일본에서는 \x1bCA나오이에\x1bCZ가 꾸민 이 사건이\n최초였다고 전해진다.",
    5350: "\x1bCA마쓰다이라 이에야스\x1bCZ는 \x1bCC미카와\x1bCZ를 다스려 다이묘로 자립하고,\n한 세력의 주인으로 인정받았다――",
    5351: "그의 약진에는 미카와 무사들의 강인함과\n동족 의식에서 나온 결속이 크게 이바지했다.",
    5352: "\x1bCB미카와슈\x1bCZ는 확실히 강하다……\n나를 받치는 충의 또한 강하지.",
    5353: "그 힘을 최대한 끌어내려면,\n내가 \x1bCB미카와슈\x1bCZ의 우두머리임을\n세상에 보여야 한다.",
    5354: "미카와노카미를 칭하는 것은 물론,\n그에 걸맞은 가문 격식도 갖춰야겠군.",
    5355: "이렇게 \x1bCA이에야스\x1bCZ는 이름을\n‘\x1bCA도쿠가와 이에야스\x1bCZ’로 고쳤다.",
    5356: "\x1bCB도쿠가와\x1bCZ는 세이와 겐지 \x1bCB닛타 가문\x1bCZ의 한 갈래로,\n헤이안 말기에 \x1bCB사토미\x1bCZ와 \x1bCB야마나\x1bCZ 가문과 함께 갈라진\n미나모토씨 유래의 성이었다.",
    5357: "쇼군 \x1bCB아시카가 가문\x1bCZ과 맞서는 \x1bCB닛타계\x1bCZ 미나모토 성씨를\n택한 것은 먼 훗날 쇼군 자리를\n바라본 일이라고도 할 수 있다.",
    5358: "\x1bCA노부나가\x1bCZ의 천하포무를 받치는 인물로서,\n그때부터 이런 생각까지 품었는지는\n이름을 바꾼 \x1bCA이에야스\x1bCZ만이 알 일이다――",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    5239: ["ko_so_sun_alliance_term_requires_glossary_review"],
    5248: ["taro_yoshinobu_name_form_requires_glossary_review"],
    5273: ["bokuden_sword_training_account_requires_historical_review"],
    5277: ["ichi_no_tachi_term_requires_glossary_review"],
    5282: ["nanto_and_ichijoin_kakukei_names_require_glossary_review"],
    5284: ["eiroku_incident_name_and_sc_typo_crosschecked_against_jp"],
    5294: ["nanbu_adoption_relationship_requires_historical_review"],
    5315: ["malformed_dynamic_placeholder_preserved_from_sc"],
    5319: ["bokuden_school_wording_requires_glossary_review"],
    5349: ["first_firearm_assassination_claim_requires_historical_review"],
    5352: ["mikawashu_term_requires_glossary_review"],
    5354: ["mikawa_no_kami_title_requires_glossary_review"],
    5356: ["tokugawa_genealogy_requires_historical_review"],
    5357: ["future_shogunate_inference_requires_historical_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.17.json": (
        "544640CB547BE5AA8A8DE00286A0D365E79EB2BD842561C245F8720F086AE725"
    ),
    "public/msgev_ko_historical_events_5109_5237.v0.17.json": (
        "3DDBDFDE91384B344A6E93946E3216C1444DD05689E6D92E5CF4E3D2F51A9406"
    ),
    "review/review_index.v0.17.json": (
        "97E31C05E632B34C9C308EF0DC4B850DE02A20018CA155DE18CE42F27F30E3BA"
    ),
    "validation.v0.17.json": (
        "1F674B7E31A0ED067B714DB5D9BB7A2AB6592F86E04799E33D0163C0865192EA"
    ),
}
INSTALLED_RESOURCE_PINS = shared.INSTALLED_RESOURCE_PINS


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any, relative_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": relative_path, "size": len(blob), "sha256": sha256(blob)}


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if len(ids) != 121 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch18 ids are not the exact 121 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch18 event group")
    return str(matches[0])


def source_structure(text: str) -> dict[str, Any]:
    return shared.source_structure(text)


def public_script_counts(text: str) -> dict[str, int]:
    return shared.public_script_counts(text)


def previous_artifact_snapshot() -> dict[str, Any]:
    mismatches: list[dict[str, str | None]] = []
    rows: list[dict[str, str]] = []
    for relative, expected in sorted(PREVIOUS_ARTIFACT_PINS.items()):
        path = WORKSTREAM_DIR / relative
        actual = sha256(path.read_bytes()) if path.is_file() else None
        if actual != expected:
            mismatches.append({"path": relative, "expected": expected, "actual": actual})
        rows.append({"path": relative, "sha256": expected})
    if mismatches:
        raise ValueError(f"previous dialogue artifacts changed: {mismatches}")
    return {
        "file_count": len(rows),
        "manifest_sha256": sha256(
            json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ),
        "all_hashes_match": True,
    }


def installed_resource_snapshot() -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    mismatches: list[dict[str, Any]] = []
    for relative, expected in sorted(INSTALLED_RESOURCE_PINS.items()):
        path = WORKSPACE_ROOT / relative
        blob = path.read_bytes()
        actual = {"size": len(blob), "sha256": sha256(blob)}
        if actual != expected:
            mismatches.append({"path": relative, "expected": expected, "actual": actual})
        snapshot[relative] = actual
    if mismatches:
        raise ValueError(f"installed msgev baseline changed: {mismatches}")
    return snapshot


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=common.strict_object
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    replacements: dict[str, Any] = {
        "SCRIPT_PATH": SCRIPT_PATH,
        "BATCH_ID": BATCH_ID,
        "OVERLAY_NAME": OVERLAY_NAME,
        "EVIDENCE_NAME": EVIDENCE_NAME,
        "REVIEW_NAME": REVIEW_NAME,
        "VALIDATION_NAME": VALIDATION_NAME,
        "SCOPE_START": SCOPE_START,
        "SCOPE_END": SCOPE_END,
        "EXCLUDED_INTERNAL_IDS": EXCLUDED_INTERNAL_IDS,
        "EVENTS": EVENTS,
        "TRANSLATIONS": TRANSLATIONS,
        "UNCERTAINTY_FLAGS": UNCERTAINTY_FLAGS,
        "PREVIOUS_ARTIFACT_PINS": PREVIOUS_ARTIFACT_PINS,
        "INSTALLED_RESOURCE_PINS": INSTALLED_RESOURCE_PINS,
        "selected_ids": selected_ids,
    }
    originals = {name: getattr(shared, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(shared, name, value)
        result = shared.build(args)
    finally:
        for name, value in originals.items():
            setattr(shared, name, value)

    out_root = args.out_root.resolve()
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    validation_path = out_root / VALIDATION_NAME
    evidence = _load_json(evidence_path)
    review = _load_json(review_path)
    validation = _load_json(validation_path)

    loaded = {
        language: source_shared.load_source(path, language)
        for language, path in {
            "SC": args.stock_sc,
            "JP": args.stock_jp,
            "EN": args.stock_en,
        }.items()
    }
    tables = {language: value[2] for language, value in loaded.items()}
    boundary_ids = (
        5237,
        5238,
        5255,
        5256,
        5293,
        5294,
        5299,
        5300,
        5337,
        5338,
        5349,
        5350,
        5358,
        5359,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v18"
    evidence["boundary_anchors"] = [
        {
            "id": entry_id,
            "reference_hashes": {
                language: common.text_hash(tables[language].texts[entry_id])
                for language in ("SC", "JP", "EN")
            },
        }
        for entry_id in boundary_ids
    ]
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v18"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v18"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch17", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch18"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v17_artifacts_before"] = integrity.pop(
        "dialogue_v01_v16_artifacts_before"
    )
    integrity["dialogue_v01_v17_artifacts_after"] = integrity.pop(
        "dialogue_v01_v16_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_artifacts_modified"
    ] = False

    overlay_path = out_root / "public" / OVERLAY_NAME
    overlay_meta = {
        "path": f"public/{OVERLAY_NAME}",
        "size": overlay_path.stat().st_size,
        "sha256": sha256(overlay_path.read_bytes()),
    }
    evidence_meta = write_json(evidence_path, evidence, f"evidence/{EVIDENCE_NAME}")
    review_meta = write_json(review_path, review, f"review/{REVIEW_NAME}")
    validation["artifacts"] = {
        "overlay": overlay_meta,
        "alignment_evidence": evidence_meta,
        "review_index": review_meta,
    }
    validation_meta = write_json(validation_path, validation, VALIDATION_NAME)
    return {
        "out_root": out_root,
        "entry_count": len(selected_ids()),
        "artifacts": {
            "overlay": overlay_meta,
            "alignment_evidence": evidence_meta,
            "review_index": review_meta,
            "generation_validation": validation_meta,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stock-sc",
        type=Path,
        default=WORKSPACE_ROOT
        / "KR_PATCH_WORK"
        / "backups"
        / "officer_name_probe_v0_1"
        / "msgev.SC.stock.bin",
    )
    parser.add_argument(
        "--stock-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgev.bin"
    )
    parser.add_argument(
        "--stock-en", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgev.bin"
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
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
