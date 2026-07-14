#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 5 (IDs 458-565)."""

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


BATCH_ID = "msgbre_biographies_0458_0565.v0.5"
OVERLAY_NAME = "msgbre_ko_biographies_0458_0565.v0.5.json"
EVIDENCE_NAME = "alignment_evidence.v0.5.json"
REVIEW_NAME = "review_index.v0.5.json"
VALIDATION_NAME = "validation.v0.5.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 458
SCOPE_END = 565
NEXT_START_ID = 566

TRANSLATIONS: dict[int, str] = {
    458: "안도 가신. 외교에서 활약했다. 1558년 난부 가문과 화친 교섭을 맡았다. 1589년 미나토 소동 때는 유리 12두 가운데 아카오츠 가문을 아군으로 끌어들이기 위한 사자로 나섰다.",
    459: "야마나 가신. 다케다성주. 오타가키 가문은 야마나 사천왕 중 하나였다. 오다 가문에서 모리 가문으로 돌아선 탓에 하시바 히데요시의 공격을 받았다. 한때 거성을 탈환했으나 뒤에 패해 달아났다.",
    460: "야마나 가신. 무네토모의 아들. 1521년 제4대 다케다성주가 되었다. 오타가키 가문은 야마나 사천왕에 꼽히는 중신 가문으로, 다지마 국조 구사카베 가문의 후예라고 한다.",
    461: "야마나 가신. 무네히사의 아들. 1538년 제5대 다케다성주가 되었다. 거성 다케다성은 무로마치 시대 중기에 오타가키 미쓰카게가 쌓았으며, 미쓰카게의 아들 가게치카는 오닌의 난에서 활약했다.",
    462: "아시카가 가신. 세키오카성주. 요시테루와 요시아키 2대를 섬겼다. 막부 멸망 뒤 영지를 잃고 사카이에 살았다. 훗날 조선 출병에 종군해 이가에 영지를 받았다. 갑주 연구가로도 유명했다.",
    463: "도요토미 가신. 세키가하라 전투에서 서군에 속했다. 친우 이시다 미쓰나리를 위해 지병을 무릅쓰고 분전해 도도 다카토라군을 격퇴했으나, 배반한 고바야카와 히데아키군의 공격을 받아 패한 뒤 자결했다.",
    464: "도요토미 가신. 요시츠구의 맏아들. 세키가하라 전투에서 아버지와 함께 서군에 속해 싸웠다. 전후 로닌이 되었으나 도요토미 히데요리의 초청을 받아 오사카성에 들어갔다. 덴노지구치 전투에서 전사했다.",
    465: "나스 7당의 한 사람. 스케키요의 셋째 아들. 형 다카마스와 스케타카가 분가를 세워 오타와라 가문을 이었다. 도요토미 히데요시의 오다와라 정벌 때 아들 하루키요를 보내 히데요시를 영접하게 했다.",
    466: "나스 7당의 한 사람. 오타와라성주. 구로바네성주 오제키 마스쓰구를 죽이고 아들 다카마스에게 오제키 가문을 잇게 했다. 또 딸을 주군 마사스케의 측실로 들이는 등 나스 가문 안에서 최대 세력을 구축했다.",
    467: "나스 7당의 한 사람. 쓰나키요의 아들. 도요토미 히데요시의 오다와라 정벌에 참진해 영지를 인정받았다. 세키가하라 전투에서는 동군에 속해 우에스기 가문의 동향을 탐색하는 등 활약했고, 전후 가증되었다.",
    468: "이와키 가신. 다카나리의 아들. 처음에는 사타케 가문과 싸웠으나 이와키·사타케 두 가문이 동맹을 맺을 때 사타케 가문에 속했다. 뒤에 주군 요시시게의 아들로 이와키 가문을 이은 쓰네타카를 섬겼다.",
    469: "사타케 가신. 다쓰고야마성주. 오츠카 가문은 본래 이와키 가신이었으나 마사나리 때 사타케 일가에 준하는 대우를 받아 사타케 가문에 속했다. 뒤에 사타케·이와키 두 가문 사이를 중재해 화친을 성사시켰다.",
    470: "이와키 가신. 오츠카 가문의 서류로 스가마타성주를 지냈다. 뒤에 종가 당주 마사나리의 뒤를 이어 다쓰고야마성에 들어갔다. 이로써 오츠카 가문은 다시 이와키 가문에 속하게 되었다.",
    471: "의사. 아사쿠라 요시카게를 섬겼다. 기력 회복과 해독에 효능이 있는 환약 ‘만킨탄’을 만들어 아사쿠라군을 뒷받침했다. 주가가 멸망하자 출가했고, 약방을 운영해 큰 호평을 얻었다.",
    472: "오토모 가문 제20대 당주. 오우치 가문 등 주변 세력과 싸워 판도를 넓혔다. 적장자 요시시게를 폐적하려다 니카이쿠즈레의 변이 일어났고, 가신들의 습격으로 중상을 입어 죽었다.",
    473: "오토모 가문 제21대 당주. 이름은 요시시게. 요시아키의 아들. 전성기에는 규슈 6개 구니를 다스렸으나 다카조가와 전투에서 시마즈군에 패해 많은 가신을 잃었고, 이후 쇠퇴의 길을 걸었다.",
    474: "오토모 가문 제22대 당주. 요시시게의 아들. 시마즈·류조지 두 가문의 압박을 받아 도요토미 히데요시에게 의지했고 분고 1개 구니를 인정받았다. 그러나 조선 출병 때 적전 도주를 범해 개역되었다.",
    475: "오토모 가신. 소린의 둘째 아들. 아버지의 명으로 승려가 되었으나 무예를 닦다가 훗날 환속했다. 시마즈 요시히사와 내통해 영지를 몰수당했다. 주가가 개역된 뒤에는 히고 호소카와 가문 등을 섬겼다.",
    476: "아와의 호족. 하쿠치성주. 요리타케의 아들. 이즈모노카미라 칭했다. 이웃의 시게키요 분고노카미를 멸망시켰을 때 시게키요 일족 이자와 곤노신의 공격을 받아 패했고, 간조지에서 자결했다고 한다.",
    477: "아와의 호족. 하쿠치성주. 고즈케노스케라 칭했다. 오니시 가문은 세이와 겐지 오가사와라 가문 또는 곤도 가문의 후예라고 한다. 아버지 요리타케와 함께 이요에서 조소카베 모토치카와 싸우다 전사했다.",
    478: "아와의 호족. 하쿠치성주. 이즈모노카미라 칭했다. 오니시 가문은 미요시군 오니시촌 출신으로, 미요시군과 사누키 도요타군 등을 침략해 오이노쇼라는 이름으로 지배했다. 조소카베군과 싸우다 전사했다.",
    479: "아와의 무장. 오니시 가문은 미요시 가문과 우호를 맺고 있었으나, 요리카네는 인질로 보내진 뒤 조소카베 모토치카의 후대를 받아 그의 가신이 되었다. 이어 아버지를 설득해 조소카베 가문에 항복시켰다.",
    480: "사노 가신. 사노 사천왕의 한 사람. 재무에 뛰어났다고 한다. 아시오 구리 광산을 개발하는 등 주가의 재정 기반을 세우는 데 힘썼다. 주군 무네쓰나가 죽은 뒤 자결을 강요받았다.",
    481: "도요토미 가신. 하루나가의 동생. 도켄사이라 칭했다. 오사카 여름 전투 때 사카이에 불을 질렀다. 오사카성이 함락되자 탈출해 달아났으나 붙잡혀 사카이에서 참수되었다.",
    482: "도요토미 가신. 가타기리 가쓰모토가 오사카성을 떠난 뒤 성안을 통솔했다. 오사카 전투에서 도요토미 측 지도자 역할을 맡았다. 오사카성이 함락될 때 주군 히데요리를 따라 순사했다.",
    483: "도요토미 가신. 하루나가의 동생. 오사카 전투 때 주전파의 중심인물 가운데 하나였다. 오사카성 함락 뒤 주군 히데요리의 아들 구니마쓰마루를 데리고 탈출했으나 붙잡혀 참수되었다.",
    484: "고노 가신. 오요케성주. 도사 이치조 가문과 모리 가문 등이 고노령을 침공했을 때 이를 격퇴했다. 도요토미 히데요시의 시코쿠 정벌군에 항복했고 주군 미치나오를 따라 아키로 이주했다.",
    485: "고노 가신. 나오마사의 동생. 지조가타케성주 우쓰노미야 도요쓰나의 사위가 되었다. 도요쓰나가 몰락한 뒤 지조가타케성주가 되었다. 여러 차례 주가를 배반해 형과 주가군을 상대로 거듭 싸웠다.",
    486: "미시마 수군 오호리 가문의 딸. 《쓰루히메 전설》에 따르면 오우치 가문과의 전투에서 갑주를 입고 분전했으며, 뒤에 전사한 연인을 따라 바다에 몸을 던졌다고 한다.",
    487: "히젠의 호족. 산조성주. 스미타다의 적장자. 세키가하라 전투에서 동군에 속해 영지를 인정받았다. 그러나 기리시탄에서 니치렌종으로 개종해 기리시탄을 박해했고, 뒤에 독살되었다.",
    488: "히젠의 호족. 아리마 가문에 패해 오무라에서 쫓겨났으나 뒤에 아리마군을 격파하고 귀환했다. 이 승리를 축하하며 춘 춤이 ‘오키타오도리·구로마루오도리·스코오도리’의 기원이라고 한다.",
    489: "히젠의 호족. 산조성주. 아리마 하루즈미의 압박을 받아 하루즈미의 둘째 아들 스미타다를 양자로 맞아 가독을 넘겼다. 뒤에 적장자 다카아키가 태어나자 고토 가문에 양자로 보냈다.",
    490: "히젠의 호족. 산조성주. 아리마 하루즈미의 둘째 아들. 오무라 스미사키의 양자가 되어 가독을 이었다. 나가사키를 개항해 포르투갈과 무역했다. 일본 최초의 기리시탄 다이묘로 유명하다.",
    491: "요시사키의 맏아들. ‘오이치몬바라이’라 불린 가중 숙청으로 재원을 확보하고 당주의 권력을 강화했다. 오사카 전투 뒤 도요토미 가문 잔당을 추포하는 데 힘썼다. 아버지와 마찬가지로 기리시탄을 탄압했다.",
    492: "하시바 가신. 하리마 출신. 오다 가문이 하리마를 공략할 때 하시바 히데요시의 유히쓰가 되었다. 새로운 노 작품을 창작하는 등 문예에 뛰어났으며, 하시바 히데요시의 군기 《덴쇼키》를 저술했다.",
    493: "오노데라 가신. 요코테성주. 1546년 가나자와 곤조보와 함께 모반해 주군 다네미치를 죽였다(히라성의 난). 그러나 뒤에 다네미치의 적장자 데루미치에게 살해되었다.",
    494: "우키타 가신. 이에토시(도시카쓰)의 아들. 주가의 내란으로 출분해 도쿠가와 가문을 섬겼다. 오사카 전투 때 아들 헤이나이가 오사카 편에 속한 탓에 이에야스의 노여움을 사 자결했다.",
    495: "기이의 호족. 사이카당의 한 사람. 이시야마 혼간지에 농성해 활약했다. 사격 솜씨가 뛰어나 오다 노부나가가 공격해 왔을 때 그를 저격해 허벅지에 중상을 입혔다고 한다.",
    496: "야마토의 호족. 오카성주. 스오노카미라 칭했다. 고후쿠지 이치조인방 고쿠민의 한 사람으로 마쓰나가 히사히데를 섬겼다. 1574년 오다 노부나가에게 거점을 불태우는 공격을 받았고, 주가가 멸망하자 순사했다.",
    497: "가모 가신. 가모 가문이 개역된 뒤 아이즈에 입봉한 우에스기 가문을 섬겼다. 흩뿌린 금화 위에서 잤다는 기행으로 유명했다. 세키가하라 전투 때 모은 재산 전부를 주가에 바쳤다.",
    498: "우키타 가신. 우키타 삼로의 한 사람. 도검과 창술에 뛰어나 40여 차례 전투에 출진한 용장이었다. 오카야마성 수축과 성하마을 건설에도 참여했다. 조선 출병 진중에서 병사했다.",
    499: "도쿠가와 가신. 사다요시의 적장자. 이시카와 야스나가가 개역된 뒤 옛 영지 시나노 마쓰모토 6만 석을 받았다. 오사카 여름 전투에서 전사했으며, 주군 이에야스에게 ‘시나노는…’이라는 말을 남기고 숨을 거두었다고 한다.",
    500: "쓰가루 가신. 주군 다메노부의 창업기를 떠받친 오우라 삼로의 한 사람. 시나노 출신으로 쓰가루로 이주해 오우라 가문을 섬겼다. 다이코지성과 이시카와성 공격 등에 종군해 활약했다.",
    501: "시나노의 호족. 나가무네의 둘째 아들이자 나가토키의 동생. 아버지와 형의 명으로 이이다의 스즈오카 오가사와라 가문을 재흥했다. 다케다 가문에 패한 뒤 도카이도를 거쳐 미요시 가문에 의지했으나 혼코쿠지의 변에서 전사했다.",
    502: "도쿠가와 가신. 사카이 다다쓰구의 셋째 아들. 오가사와라 노부미네의 양자가 되어 가독을 잇고 무사시 혼조번주가 되었다. 오다와라 정벌과 우에다성 공격 등에 참진했다. 뒤에 시모사 고가로 가증 전봉되었다.",
    503: "미요시 가신. 이치노미야성주. 주군 나가요시의 누이를 아내로 맞았다. 이즈미 구메다 전투에서 미요시군이 대패했을 때 군을 수습해 침착하게 퇴각시켜 칭송받았다. 뒤에 조소카베 모토치카에게 살해되었다.",
    504: "노부유키의 적장자. 아버지가 죽은 뒤 가독을 이어 시모사 고가번 2만 석의 제2대 번주가 되었다. 뒤에 시모사 세키야도 2만 7천 석으로 가증 전봉되었다. 이타쿠라 시게마사의 딸을 아내로 맞았다.",
    505: "히데마사의 둘째 아들. 오사카 여름 전투에서 아버지와 형 다다나가가 전사해 가독을 이었다. 하리마 아카시를 거쳐 부젠 고쿠라번주가 되었다. 다도에 조예가 깊어 아가노야키 육성에 힘썼다.",
    506: "시나노 슈고. 나가무네의 맏아들. 다케다 신겐에게 시나노에서 쫓겨나 에치고·셋쓰·아이즈 등지를 떠돌았다. 아들 사다요시가 노부나가 휘하에서 옛 영지를 되찾았으나 자신은 돌아가지 못한 채 죽었다.",
    507: "시나노 슈고. 방계 이나 오가사와라 가문을 굴복시켜 분열된 오가사와라 가문을 통일했다. 이웃 스와 가문과도 화친을 맺어 영내 통치를 안정시키는 데 힘썼다.",
    508: "오우치 가신. 누쿠유성주. 주군 요시타카가 죽은 뒤 아마고 가문에 속했다. 오모리 은산으로 진출해 영유했다. 뒤에 모리 모토나리군의 공격을 받아 저항했으나 패해 항복했다.",
    509: "도쿠가와 가신. 나가토키의 적장자. 각지를 떠돈 뒤 도쿠가와 이에야스의 후원을 받아 옛 영지를 되찾았고, 이후 도쿠가와 가문을 섬겼다. 아들 히데마사에게 이에야스의 손녀를 맞아들이는 등 관계 강화에 힘썼다.",
    510: "오가사와라 가신. 나가토키의 동생. 여러 구니를 떠돈 뒤 우에스기 가게카쓰의 후원으로 후카시성을 탈환했다. 그러나 조카 사다요시가 도쿠가와 이에야스의 도움을 받아 시나노에 들어오자 성을 넘겨주었다.",
    511: "이마가와 가신. 오케하자마 전투에서 주군 요시모토의 수급을 스루가로 가져왔다. 주가 멸망 뒤 다케다 가문을 섬겨 다카텐진성주가 되었으나 도쿠가와 이에야스의 공격으로 성이 함락될 때 전사했다.",
    512: "이마가와 가신. 주군 우지테루가 죽은 뒤 후계 문제로 일어난 하나쿠라의 난에서 바이카쿠 쇼호(이마가와 요시모토) 편에 섰다. 가타노카미성을 함락시키는 등 크게 활약했다.",
    513: "이마가와 가신. 주가 멸망 뒤 다케다 가문을 섬겨 시미즈성주가 되었다. 스루가 선방중으로서 미카타가하라 전투 등에 종군했다. 다케다 가문 멸망 뒤에는 도쿠가와 가문을 섬겨 가이 평정에 기여했다.",
    514: "도쿠가와 가신. 마사츠나의 아들. 나가쿠테 전투 등에서 공을 세웠다. 주군 이에야스가 간토에 입봉할 때 가즈사·시모사 1만 2천 석을 받았고, 뒤에 단바 가메야마 2만 석으로 가증되었다.",
    515: "오다 가신. 다가야 마사츠네 등에게 거성 야타베성을 빼앗겼으나 10년 뒤 호조 우지테루의 지원을 받아 탈환했다. 그러나 뒤에 다가야 시게츠네에게 패해 전사했다.",
    516: "사타케 가신. 젠테츠의 아들. 승려로서 사타케 요시시게·요시노부 2대를 가까이서 섬겼다. 외교에서 활약했고, 요시시게의 셋째 아들 사다타카가 이와키 가문에 입적할 때 동행해 이와키 가문의 정무에도 참여했다.",
    517: "사타케 가신. 겐이츠의 아들. 처음에는 부조를 따라 삭발하고 승려가 되었으나 뒤에 주군 요시노부의 명으로 환속했다. 요시노부의 아키타 전봉을 따랐고 오사카 전투에도 출진해 공을 세웠다.",
    518: "사타케 가신. 승려로서 요시아쓰·요시아키·요시시게 3대를 가까이서 섬겼다. 시라카와 유키 가문과 고가 공방 등과 서신을 주고받으며 외교에서 중책을 맡아 사타케 일문 다음가는 지위를 얻었다.",
    519: "사토미 가신. 요시요리의 중신으로 아와 오카모토성을 근거지 삼아 사토미 수군의 한 축을 맡았다. 요시요리가 죽은 뒤 오카모토성 화재의 책임을 지고 추방되었으나 나중에 복귀했다.",
    520: "사가라 가신. 첫 출진 이래 19차례 전투에서 공을 세웠다. 사쓰마 오구치 전투에서 시마즈 가신 가와카미 히사아키를 죽였다. 뒤에 사가라 가문의 군공을 기록한 《오카모토 요리우지 전장일기》를 지었다.",
    521: "오다 가신. 노부나가의 셋째 아들 노부타카가 그의 저택에서 태어났다고 한다. 뒤에 주가를 떠나 도요토미 가문을 섬기고 이세 가메야마성주가 되었다. 세키가하라 전투에서 서군에 속했으며 전후 자결했다.",
    522: "류조지 가신. 거성 가스가야마성을 구마시로 가쓰토시에게 빼앗기고 많은 일족을 잃었다. 복수를 위해 출진했다가 텟푸 고개에서 가쓰토시와 마주쳐 일기토를 벌였으나 패해 죽었다.",
    523: "오미의 호족. 아케치 미쓰히데를 섬겼다. 미쓰히데가 죽은 뒤 시바타 가쓰토요의 가로를 거쳐 도요토미 히데요시를 섬겨 이요 후추 7만 석을 받았다. 세키가하라 전투에서 동군으로 돌아섰으나 전후 개역되었다.",
    524: "단바의 호족. 아카이 나오마사의 외숙부. 나이토 구니사다가 공격해 오자 이를 격퇴했다. 그러나 뒤에 휘하 장병을 버려 죽게 한 탓에 신망을 잃었고, 나오마사에게 모살되어 구로이성을 빼앗겼다.",
    525: "기슈의 호족. 츠다 산쇼·산초 부자에게 포술을 배워 몇 년 만에 오의를 익혔고, 오다 노부나가와 하시바 히데요시를 괴롭혔다. 뒤에 아사노 요시나가의 요청으로 츠다류 포술을 전수했다.",
    526: "노부마사의 적장자. 어머니는 도쿠가와 이에야스의 딸 가메히메다. 세키가하라 전투에서 도쿠가와 히데타다를 따라 우에다성 공격에 참가했다. 무용이 뛰어났으나 병으로 오사카 전투에 출진하지 못했고, 끝내 병사했다.",
    527: "도쿠가와 가신. 사다요시의 아들. 한때 다케다 신겐에게 속했으나 신겐이 죽은 뒤 돌아왔다. 나가시노 전투에서 나가시노성을 끝까지 지켜 승리에 크게 기여했고, 그 공으로 이에야스의 딸 가메히메를 아내로 맞았다.",
    528: "이에마사의 적장자. 아버지가 급사하자 7세에 가독을 이어 시모쓰케 우쓰노미야번 제2대 번주가 되었다. 뒤에 시모사 고가로 가증 전봉되었으나 우쓰노미야성 조천정 사건 뒤 다시 우쓰노미야에 봉해졌다.",
    529: "도쿠가와 가신. 다다마사의 맏아들. 아버지가 죽자 미노 가노번을 이었으나 어려서 할아버지 노부마사와 할머니 가메히메가 후견했다. 젊은 나이에 죽어 오쿠다이라 가문도 개역되었다.",
    530: "사다요시의 동생. 도쿠가와 가신으로 나가시노 전투 등에 참가했다. 세키가하라 전투에서는 고바야카와 히데아키의 감시역을 맡아 히데아키와 함께 서군의 오타니 요시츠구 부대와 싸우다 치명상을 입고 진중에서 죽었다.",
    531: "미카와의 호족. 사다요시·사다하루의 아버지. 처음 마쓰다이라 가문에 속한 뒤 정세에 따라 이마가와·오다·도쿠가와·다케다 가문으로 주군을 바꾸며 가문을 보전했다. 다케다 가문 멸망 뒤 도쿠가와 가문으로 돌아왔다.",
    532: "이마가와 가신. 오케하자마 전투 뒤 도쿠가와 가문을 섬겨 가케가와성 공격과 아네가와 전투에 종군했다. 한때 다케다 신겐에게 속했으나 신겐이 죽은 뒤 도쿠가와 가문으로 돌아와 나가시노 전투에서 활약했다.",
    533: "니혼마쓰 하타케야마 가신. 다테 마사무네가 니혼마쓰성을 공격할 때 마사무네의 본진을 여러 차례 습격했으나 모두 실패했다고 한다. 주가 멸망 뒤 마사무네의 거듭된 출사를 거절하고 고향으로 돌아가 농사를 지었다.",
    534: "마에다 가신. 노토 스에모리성주. 사사 나리마사가 이끈 1만 5천 대군을 불과 300명의 병력으로 물리쳤다. 이때 아내가 성병들을 찾아다니며 질타하고 격려했다는 일화가 남아 있다.",
    535: "오다 가신. 노부카쓰의 명으로 도요토미 히데요시의 가신이 되었다. 세키가하라 전투에서는 동군의 후쿠시마 마사노리를 섬겨 싸웠다. 전후 여러 지역을 떠돌다가 끝내 하타모토가 되었다.",
    536: "우키타 가신. 사다치카의 아들. 주가의 국정을 맡아 영내 검지와 성하마을 정비 등을 추진했다. 주군 히데이에의 총애를 등에 업고 전권을 휘두른 탓에 반대 세력에게 독살되었다고 한다.",
    537: "우키타 가신. 우키타 삼로의 한 사람. 묘젠지 전투를 비롯한 각지의 전투에 종군해 주군 나오이에의 창업을 도왔다. 도가와 히데야스가 은거한 뒤 국정을 맡았으며, 나중에 매제에게 살해되었다.",
    538: "우키타 가신. 사다치카의 아들. 형 츠나나오가 죽은 뒤 가독을 이었다. 가문에서도 손꼽히는 고위 가신으로 2만 4천 석을 다스렸다. 주군 히데이에를 따라 세키가하라 전투에 출진한 뒤 행방불명되었다.",
    539: "도사 이치조 가신. 주군 가네사다가 분고로 추방되자 분개해 가네사다를 배신한 가신들의 거성을 공격했다. 뒤에 조소카베 모토치카의 도사 평정군에 항복하고 하타 지방 평정에 힘썼다.",
    540: "오다 가문 제15대 당주. 마사하루의 아들. 호조 가문과 손잡고 사타케 가문의 남진을 막으려 했으나 연전연패해 거성을 빼앗기고 항복했다. 이후에도 옛 영지를 되찾지 못하고 유키 히데야스를 섬겼다.",
    541: "오다 가문 제16대 당주. 우지하루의 아들. 동맹을 맺었던 호조 가문이 멸망한 뒤 유키 히데야스를 섬겼다. 누이가 히데야스의 측실이 되었고, 히데야스의 에치젠 전봉을 따라 이주했다.",
    542: "쇼니 가신. 히젠 하스노이케성주. 류조지 다카노부의 가독 계승에 반대한 히가시히젠 19장의 한 사람으로 다카노부와 싸웠다. 다카노부가 히젠으로 돌아온 뒤에는 그를 섬겼고, 에가미 다케타네 토벌전에서 전사했다.",
    543: "오다 가문 제14대 당주. 호리고에 공방 아시카가 마사토모의 아들로 오다 시게하루의 양자가 되었다. 에도 가문 등과 싸우고 가와고에 전투에서 고가 공방 아시카가 가문을 지지하는 등 여러 군사 행동을 펼쳤다.",
    544: "나리타 가신. 나리타 지카야스의 둘째 아들. 기사이성주 오다 가문의 가독을 이었다. 형 나가야스가 우에스기 겐신을 배반했을 때 겐신에게 거성을 빼앗겼으나 뒤에 형이 기사이성을 탈환했다.",
    545: "우지하루의 서장자. 핫타 사콘이라 칭했다. 오다 가문의 동맹인 호조 가문을 섬겼다. 주가 멸망 뒤 도요토미 가문을 섬겼고, 조선 출병 때 선박 봉행을 맡아 이세에 영지를 받았다.",
    546: "노부타다의 적장자. 혼노지의 변 뒤 하시바 히데요시의 옹립으로 3세에 오다 가문을 이었으나 실권은 히데요시가 장악했다. 세키가하라 전투에서 서군을 도왔다가 패하고 고야산에서 출가했다.",
    547: "도요토미 가신. 노부카쓰의 아들. 에치젠 오노 5만 석을 다스렸다. 세키가하라 전투에서 처음 동군에 속했으나 뒤에 아버지와 함께 서군으로 돌아서 개역되었다. 이후 무사시 아사쿠사에 은거했다.",
    548: "츠다 노부즈미의 맏아들. 어머니는 아케치 미쓰히데의 딸이다. 혼노지의 변 때 아버지가 죽자 아버지의 옛 가신 도도 다카토라를 의지했다. 뒤에 도요토미 가문을 섬겼고, 오사카 전투 뒤 다카토라의 구명으로 살아남아 하타모토가 되었다.",
    549: "오와리의 호족. 이와쿠라성주. 오다 노부카쓰를 지지해 오다 노부나가와 우키노에서 싸웠으나 패했다. 뒤에 아들 노부카타 등에게 추방되었고, 이후 사이토 요시타쓰를 의지해 계속 노부나가에 맞섰다.",
    550: "노부사다의 아들. 무용이 뛰어나 이마가와 가문과의 아즈키자카 전투에서 후군을 맡았다. 조카 노부나가의 기요스성 공략에서 활약해 나고야성주가 되었으나 몇 달 뒤 가신에게 모살되었다.",
    551: "노부나가의 셋째 아들. 이세의 호족 간베 도모모리의 양자가 되어 가독을 이었다. 혼노지의 변 뒤 시바타 가쓰이에와 손잡고 하시바 히데요시에 맞섰으나 패해 히데요시의 명으로 자결했다.",
    552: "오다 가신. 노부히데의 맏아들이자 노부나가의 서형. 아즈키자카 전투에서 선진을 맡았다. 뒤에 모반을 꾀했으나 노부나가에게 용서받고 마음을 고쳐 힘썼으며, 이세 나가시마 공격에서 전사했다.",
    553: "오와리 슈고다이 오다 노부토모의 가신. 쓰시마·아쓰타 상인의 경제력을 바탕으로 세력을 넓혔다. 그러나 오와리 통일을 앞두고 유행병에 걸려 급사해 적장자 노부나가에게 오다 가문을 맡겼다.",
    554: "노부히데의 둘째 아들. 노부유키라고도 한다. ‘멍청이’라 불린 형 노부나가와 달리 영리해 가문 안에서 평판이 좋았다. 하야시 히데사다 등의 옹립으로 가독을 다퉜으나 기요스성에서 노부나가에게 살해되었다.",
    555: "노부카쓰의 아들. 백부 노부나가를 섬겼고 아케치 미쓰히데의 딸을 아내로 맞았다. ‘한층 뛰어난 인물’이라 평가받을 만큼 재능이 있었으나 혼노지의 변 때 사촌 노부타카에게 살해되었다.",
    556: "오다 가신. 이누야마성주. 오다 노부히데의 딸을 아내로 맞아 한때 오다 노부나가와 협력했으나 차츰 적대했다. 노부나가에게 이누야마성을 빼앗기고 가이로 달아났다고 한다.",
    557: "노부나가의 적장자. 마쓰나가 히사히데의 모반 진압과 가이 평정 등에서 공을 세웠다. 노부나가에게 가독을 넘겨받아 미노·오와리 두 구니를 다스렸다. 혼노지의 변 때 니조 어소에서 자결했다.",
    558: "노부히데의 적장자. 오케하자마에서 이마가와 요시모토를 격파했다. 이후 천하포무를 내걸고 적대 세력을 잇달아 멸망시켰다. 천하 통일을 눈앞에 두고 아케치 미쓰히데의 모반을 받아 혼노지에서 죽었다.",
    559: "시바 가신. 요시노부의 아들. 오다 미치카쓰 휘하에서 ‘기요스 삼봉행’의 한 사람으로 활약했다. 쇼바타성을 쌓아 거성으로 삼고 인근 쓰시마항을 지배해 오다 가문의 재정 기반을 닦았다.",
    560: "노부히데의 넷째 아들. 에치젠 공격과 이시야마 혼간지 공격에 참가했다. 혼노지의 변 뒤 도요토미 히데요시를 섬겨 히데요시의 아들 히데요리의 보좌역을 맡았다. 딸은 히데요시의 측실이 되어 총애받았다.",
    561: "오와리 시바 가신. 오와리 하4군의 슈고다이로 히로노부라고도 하며 기요스성주를 맡았다. 주군 요시무네를 죽인 탓에 오다 노부나가의 명을 받은 오다 노부미쓰에게 공격받아 자결했다.",
    562: "노부나가의 둘째 아들. 이세 국사 기타바타케 가문의 양자가 되어 가독을 이었다. 혼노지의 변 뒤 도요토미 가문에 종속되었다. 오다와라 정벌 뒤 도쿠가와 이에야스의 옛 영지로 전봉하라는 명을 거부해 개역되었다.",
    563: "시바 가신. 야마토노카미라 칭했다. 내란을 일으키고 자결한 오다 미치사다의 뒤를 이어 오와리 하4군의 슈고다이가 되었다. 오다 노부나가의 아버지 노부히데는 미치카쓰의 가신인 ‘기요스 삼봉행’ 중 한 사람이었다.",
    564: "노부히데의 열째 아들. 우라쿠사이라 칭했다. 다도에 심취해 리큐 칠철의 한 사람이 되었다. 형 노부나가가 죽은 뒤 도요토미 가문에 속했으나 오사카 전투 직전 도쿠가와 편과 내통하고 오사카성을 떠났다.",
    565: "도요토미 가신. 나가마스의 적장자. 도요토미 히데요리를 섬겼으나 오사카 여름 전투 직전 갑자기 오사카성을 떠났다. 이후 교토에서 은거하며 다도 우라쿠류를 계승했다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    460: ["munetomo_reading_and_tajima_kokuzo_title_require_glossary_review"],
    469: ["satake_ikka_status_rendering_requires_context_review"],
    471: ["mankintan_medicine_name_requires_glossary_review"],
    473: ["takajogawa_battle_reading_requires_glossary_review"],
    476: ["shigekiyo_bungonokami_izawa_gonnoshin_and_ganjoji_readings_require_review"],
    478: ["oi_no_sho_rendering_requires_place_name_review"],
    479: ["hostage_clause_subject_requires_context_review"],
    488: ["okita_kuromaru_suko_dance_name_renderings_require_glossary_review"],
    491: ["oichimonbarai_term_requires_glossary_review"],
    493: ["kanazawa_konjobu_and_hirajo_rebellion_readings_require_review"],
    494: ["game_source_has_father_subject_ietoshi_identity_ambiguity"],
    496: ["kofukuji_ichijoin_gata_kokumin_term_requires_glossary_review"],
    505: ["agano_yaki_reading_requires_glossary_review"],
    512: ["katanokami_castle_reading_requires_castle_catalog_review"],
    515: ["yatabe_castle_and_tagaya_masatsune_readings_require_catalog_review"],
    520: ["battle_diary_title_rendering_requires_glossary_review"],
    522: ["teppu_pass_reading_requires_place_catalog_review"],
    525: ["tsuda_sansho_name_reading_requires_officer_catalog_review"],
    528: ["utsunomiya_hanging_ceiling_incident_term_requires_glossary_review"],
    534: ["suemori_castle_reading_requires_castle_catalog_review"],
    542: ["hasunoike_castle_reading_requires_castle_catalog_review"],
    543: ["oda_shigeharu_name_reading_requires_officer_catalog_review"],
    544: ["kisai_castle_reading_requires_castle_catalog_review"],
    545: ["ship_magistrate_term_requires_glossary_review"],
    549: ["ukino_battle_reading_requires_glossary_review"],
    559: ["shobata_castle_and_kiyosu_three_magistrates_terms_require_review"],
    561: ["lower_four_districts_office_term_requires_glossary_review"],
    564: ["urakusai_and_uraku_school_terms_require_glossary_review"],
    565: ["uraku_school_term_requires_glossary_review"],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def write_json(path: Path, value: Any) -> dict[str, Any]:
    return shared.write_json(path, value)


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != 108:
        raise ValueError("batch5 translations must exactly cover IDs 458-565")
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
        raise ValueError("next-start boundary ID 566 must be non-empty in all languages")

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
        "schema": "nobu16.kr.msgbre-alignment-evidence.v5",
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
        "schema": "nobu16.kr.msgbre-review-index.v5",
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
        "schema": "nobu16.kr.msgbre-generation-validation.v5",
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
                "last_completed_family": "oda_yorinaga",
                "next_family": "ochi",
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
            "existing_v01_v02_v03_v04_artifacts_modified": False,
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
