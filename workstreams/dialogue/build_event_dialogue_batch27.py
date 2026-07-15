#!/usr/bin/env python3
"""Build source-free Korean historical-event dialogue batch27 (6373-6481)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
TOOLS_DIR = SCRIPT_PATH.parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch26 as shared  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


source_shared = shared.source_shared
BATCH_ID = "msgev_historical_events_6373_6481.v0.27"
OVERLAY_NAME = "msgev_ko_historical_events_6373_6481.v0.27.json"
EVIDENCE_NAME = "alignment_evidence.v0.27.json"
REVIEW_NAME = "review_index.v0.27.json"
VALIDATION_NAME = "validation.v0.27.json"
STRING_COUNT = shared.STRING_COUNT
SCOPE_START = 6373
SCOPE_END = 6481
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

TC_SOURCE_PIN: dict[str, Any] = {
    "logical_path": "MSG_PK/TC/msgev.bin",
    "size": 523_304,
    "packed_sha256": "CB4A3E57AF2091124669E28BF1DD6B8C664BFA8A1EF800F8BB6FD79C82E1DE47",
    "raw_size": 740_444,
    "raw_sha256": "39F661510E2A4D53E07B3D93DE34A315BAD4231A1BB8B96E8E79674908A4B5D3",
}
SOURCE_PINS: dict[str, dict[str, Any]] = {
    language: dict(source_shared.SOURCE_PINS[language])
    for language in ("SC", "JP", "EN")
}
SOURCE_PINS["TC"] = dict(TC_SOURCE_PIN)

EVENTS = (
    {
        "event_id": "chosokabe_subdues_ichijo",
        "title_ko": "조소카베의 이치조 정벌",
        "start_id": 6373,
        "end_id": 6389,
        "selected_count": 17,
    },
    {
        "event_id": "ichijo_kanesada_attempts_tosa_return",
        "title_ko": "이치조 가네사다의 도사 탈환",
        "start_id": 6390,
        "end_id": 6410,
        "selected_count": 21,
    },
    {
        "event_id": "motochika_contacts_oda_for_awa",
        "title_ko": "아와 진출과 오다 교섭",
        "start_id": 6411,
        "end_id": 6427,
        "selected_count": 17,
    },
    {
        "event_id": "motochika_labels_equipment",
        "title_ko": "모토치카의 기명 전술",
        "start_id": 6428,
        "end_id": 6443,
        "selected_count": 16,
    },
    {
        "event_id": "harima_and_kuroda_joins_oda",
        "title_ko": "하리마와 구로다의 오다 합류",
        "start_id": 6444,
        "end_id": 6481,
        "selected_count": 38,
    },
)

TRANSLATIONS: dict[int, str] = {
    6373: "어린 시절 ‘히메와카코’라 불리던\n\x1bCA조소카베 모토치카\x1bCZ는 전장을 거듭하며 크게 성장해,\n이제 ‘오니와카코’라 불리게 되었다.",
    6374: "\x1bCB아키 가문\x1bCZ을 멸한 \x1bCA모토치카\x1bCZ가\n\x1bCC도사\x1bCZ에서 세력을 넓히려 할 때,\n가장 큰 걸림돌은 \x1bCB도사 이치조 가문\x1bCZ이었다.",
    6375: "지금이 절호의 기회입니다!\n\x1bCB아키\x1bCZ를 친 지금, 다음 적은 \x1bCB이치조\x1bCZ뿐!\n형님도 이미 결심하셨겠지요?",
    6376: "\x1bCA모토치카\x1bCZ의 동생 \x1bCA기라 치카사다\x1bCZ는\n\x1bCC도사\x1bCZ의 호족 \x1bCB기라 가문\x1bCZ을 이었으며,\n용맹하고 무예에 밝은 장수였다.",
    6377: "경솔한 말씀은 마십시오.\n\x1bCB이치조\x1bCZ 님은 위기의 \x1bCB조소카베 가문\x1bCZ을 구하고,\n아버님의 \x1bCC오카토요성\x1bCZ 귀환도 도우신 은인입니다.",
    6378: "그런 \x1bCB이치조 가문\x1bCZ에 활을 겨눈다면\n천벌을 받아 우리 운도 다할 것입니다……\n\x1bCB이치조\x1bCZ를 칠 수는 결코 없습니다!",
    6379: "형제의 조부 \x1bCA조소카베 가네츠구\x1bCZ가\n\x1bCB모토야마 가문\x1bCZ에게 멸망했을 때, 유아 \x1bCA쿠니치카\x1bCZ를\n보호한 이는 \x1bCA이치조 후사이에\x1bCZ였습니다.",
    6380: "그 일은 \x1bCB조소카베\x1bCZ의 사람이라면\n누구나 알고 있다.\n내가 묻는 것은 형님의 각오다.",
    6381: "천벌이 내린다면, 형님 대신\n제가 떠안겠습니다!\n그러니 얼버무리지 말아 주십시오.",
    6382: "후, 후후……하하하!\n잘 말했다, \x1bCA치카사다\x1bCZ!\n나도 같은 생각이었다.",
    6383: "（큰 소리로 웃다니. 형님에게는\n\u3000드문 일도 다 있구나……）",
    6384: "아버님을 돌보신 \x1bCA이치조 후사이에\x1bCZ 공은\n현 당주 \x1bCA가네사다\x1bCZ 님에게는 증조부입니다.\n이제 인연은 끊겼다고 해도 되겠지요.",
    6385: "우리는 이제 \x1bCB이치조\x1bCZ를 공격한다.\n\x1bCA치카사다\x1bCZ, 네게 맡기겠다!",
    6386: "맡겨 주십시오!",
    6387: "사실 이런 날이 올지도 모른다 생각해,\n미리 세워 둔 계책이 있습니다.\n들어 보시겠습니까?",
    6388: "（설마 형님은 내가 \x1bCB이치조\x1bCZ 공격을\n\u3000말 꺼내기를 기다리고 계셨던 건가?）",
    6389: "\x1bCB조소카베 가문\x1bCZ은 \x1bCB이치조 가문\x1bCZ 타도를 결심했다.\n옛 은혜를 버리고,\n\x1bCC도사\x1bCZ 통일을 향해 움직이기 시작했다……",
    6390: "\x1bCA이치조 가네사다\x1bCZ는 \x1bCC도사\x1bCZ에서 쫓겨나\n\x1bCC분고\x1bCZ로 달아나 \x1bCA[b473]\x1bCZ의 보호 아래\n기독교에 귀의했다.",
    6391: "세례명은 \x1bCA돈 파울로\x1bCZ.\n하지만 신앙은 바뀌어도\n\x1bCC도사\x1bCZ로 돌아갈 야심은 버리지 않았다.",
    6392: "이놈 \x1bCA모토치카\x1bCZ…… 은혜를 원수로 갚다니!\n비열한 수로 나를 쫓아낸 치욕,\n절대로 용서하지 않겠다!",
    6393: "진정하십시오, \x1bCA가네사다\x1bCZ 님.\n마음을 가라앉히고 자신을 주께 맡기십시오.\n그러면 길이 열릴 것입니다.",
    6394: "\x1bCA가네사다\x1bCZ는 장인 \x1bCA[b473]\x1bCZ에게 병력을 빌려\n\x1bCC도사\x1bCZ 탈환을 위해 \x1bCC분고\x1bCZ에서 출항했다.",
    6395: "\x1bCA가네사다\x1bCZ의 \x1bCC도사\x1bCZ 귀환을 노리는 이가\n\x1bCC분고\x1bCZ에서 병력을 모은다는 소문은\n곧 \x1bCC도사\x1bCZ에도 퍼져 나갔다……",
    6396: "\x1bCA가네사다\x1bCZ의 귀환을 바라는 이들도 나타나,\n\x1bCB조소카베 가문\x1bCZ의 지배는 흔들리고 있었다.",
    6397: "흥, 정신 못 차리고 또 오려는가!\n이제 부를 생각도 없는데.",
    6398: "\x1bCA가네사다\x1bCZ를 돕는 자가 나타나면 곤란합니다.\n즉시 토벌군을 보내시지요.",
    6399: "좋다, 이번에는 나도 출진하겠다.\n\x1bCC시코쿠\x1bCZ를 평정하려는 자가,\n이런 싸움에서 주저앉을 수는 없지!",
    6400: "（형님의 패기가……!）",
    6401: "\x1bCC도사\x1bCZ의 \x1bCB이치조 가문\x1bCZ은 이름 그대로\n오섭가의 \x1bCC이치조 가문\x1bCZ이\n오닌의 난을 계기로 \x1bCC도사\x1bCZ에 뿌리내린 명문이다.",
    6402: "한편 \x1bCB조소카베 가문\x1bCZ은 \x1bCC도사\x1bCZ 칠웅에 드는\n\x1bCC도사\x1bCZ의 국인 다이묘였으나, 멸망의 위기에서\n\x1bCB이치조 가문\x1bCZ에게 도움받은 과거가 있다.",
    6403: "두 영웅은 일본 굴지의 맑은 강 \x1bCC시만토가와\x1bCZ\n물가에서 \x1bCC도사\x1bCZ의 패권을 놓고 결전을 벌였다.",
    6404: "옛 세력을 대표하는 \x1bCB이치조 가문\x1bCZ과\n새로운 힘 \x1bCB조소카베 가문\x1bCZ……\n승리를 거둔 것은 후자였다.",
    6405: "이놈!\n염치없는 놈!\n이놈!",
    6406: "네 시대는 끝났다!\n다시는 \x1bCC도사\x1bCZ에 발을 들이지 마라!",
    6407: "패한 \x1bCA이치조 가네사다\x1bCZ는 다시 \x1bCC분고\x1bCZ로 달아났다.\n그 후 독실한 기독교도로서\n신앙에 힘쓰며 살았다고 한다.",
    6408: "한편 \x1bCC도사\x1bCZ에 남아 \x1bCA모토치카\x1bCZ를 계속 섬긴\n\x1bCA가네사다\x1bCZ의 아들 \x1bCA다다마사\x1bCZ는 제대로 쓰이지 못해,\n다이묘 가문으로서의 체면도 잃었다.",
    6409: "\x1bCC시만토가와\x1bCZ의 승리로,\n\x1bCB조소카베 모토치카\x1bCZ는 이미 사실상\n\x1bCC도사\x1bCZ의 국주로 인정받고 있었다……",
    6410: "\x1bCB이치조 가문\x1bCZ을 멸하고,\n\x1bCC도사\x1bCZ 한 나라를 평정한 \x1bCA조소카베 모토치카\x1bCZ는\n다음 공략 목표를 아와로 정했다.",
    6411: "\x1bCC아와\x1bCZ는 \x1bCC기이국\x1bCZ·\x1bCC이즈미국\x1bCZ과 \x1bCC세토나이카이\x1bCZ를 사이에 두고,\n\x1bCC기나이\x1bCZ 세력의 영향을 피할 수 없는 곳이었다.",
    6412: "\x1bCA모토치카\x1bCZ가 가장 경계한 것은,\n근년 \x1bCC기나이\x1bCZ에서 세력을 넓힌 \x1bCA오다 노부나가\x1bCZ였다.",
    6413: "\x1bCC아와\x1bCZ를 마음대로 손에 넣는데,\n어째서 \x1bCA노부나가\x1bCZ 따위의 허락을 받아야 하지?",
    6414: "\x1bCA노부나가\x1bCZ 따위라 하기는 그렇습니다만……\n현재 \x1bCA노부나가\x1bCZ의 허락이 필요한 것은 아닙니다.",
    6415: "허락을 얻는다는 것은 겉치레일 뿐.\n요지는 방해하지 말라는 경고입니다.",
    6416: "그런가……\n그렇다면 \x1bCA노부나가\x1bCZ를 위해서도 미리 말해 두는 편이 낫군.",
    6417: "확실히,\n바다를 사이에 둔 싸움은 서로에게 이득이 없습니다.\n그런데 \x1bCB오다\x1bCZ에 어떻게 전하시겠습니까?",
    6418: "\x1bCB오다\x1bCZ의 중신 \x1bCA아케치 미쓰히데\x1bCZ는 내 아내의 먼 친척이다.\n그를 통해 이야기를 붙이지.",
    6419: "제 의형도\n\x1bCA미쓰히데\x1bCZ 님의 중신이니까요!",
    6420: "……하, 설마 이 일을 위해\n저를 \x1bCC미노\x1bCZ에서 맞아들인 겁니까!?",
    6421: "하하하.\n그대를 이곳에 맞은 지가 몇 년인데?\n그때는 아직 \x1bCC도사\x1bCZ조차 장악하지 못했다.",
    6422: "그런 옛날에,\n이토록 먼 앞을 내다볼 리가 있겠느냐.",
    6423: "그, 그러시겠지요……",
    6424: "나는 그저 \x1bCC미노\x1bCZ에 아름다운 공주가 있다는 말을 듣고,\n이 \x1bCC도사\x1bCZ로 맞아들이고 싶었을 뿐이다.",
    6425: "그, 그렇겠지요!\n후후후……",
    6426: "（형님이 말이 많아질 때는\n\u3000거짓말을 하고 계실 때지……）",
    6427: "（형님의 깊은 헤아림…… 두렵구나……）",
    6428: "\x1bCC오카토요성\x1bCZ·토조 주변──",
    6429: "……",
    6430: "형님, 어찌하셨습니까?",
    6431: "제법 어질러져 있군.",
    6432: "아, 이것은……\n싸움이 이어져 치울 틈이 없었던 모양입니다.\n쓴 물건은 정리하라 일러 두겠습니다.",
    6433: "그것만으로는 아무것도 달라지지 않는다.\n모든 도구에 이름을 쓰라고 일러라.",
    6434: "이름을 말입니까?",
    6435: "도구에 이름을 써 두면,\n평소에 서로 바꾸어 가져갈 일도 없겠지.",
    6436: "전장에서 도구를 잃어버리면,\n주인의 실수임을 알 수 있다.",
    6437: "그러므로,\n도구를 함부로 다루는 일도 없어지겠지.",
    6438: "……예!\n그리하겠습니다.",
    6439: "여전히 형님은\n무엇을 보고 계신지 알 수 없는 분이군……",
    6440: "아군과 적군을 모두 잘 보고 계신다.\n아군의 강점을 살리고, 적의 약점을 찾는다.\n평범한 장수로는 당해 낼 수 없겠지.",
    6441: "소지품에 이름을 쓰는\n오늘날에도 교육의 기본인 행동을\n\x1bCB조소카베 가문\x1bCZ은 전국 시대에 실천했다.",
    6442: "일령구족과 협력하는 체제 등을 포함한,\n\x1bCA모토치카\x1bCZ의 세심하고 근대적인 감각이",
    6443: "\x1bCB조소카베 가문\x1bCZ이 \x1bCC시코쿠\x1bCZ에서\n급성장한 한 요인이었을 것이다.",
    6444: "\x1bCA[b826]\x1bCZ──\n하리마 슈고 \x1bCB아카마쓰 가문\x1bCZ의 중신,\n\x1bCB고데라 가문\x1bCZ을 섬긴 \x1bCA구로다 모토타카\x1bCZ의 아들이다.",
    6445: "\x1bCB고데라\x1bCZ 가문이 \x1bCB오다\x1bCZ와\n\x1bCB모리\x1bCZ 중 누구와 손잡을지 논의할 때,\n\x1bCA[bm826]\x1bCZ는 \x1bCB오다\x1bCZ와 손잡아야 한다고 강하게 주장했다.",
    6446: "그리고 이 젊은 인재는 지금\n사자로서 \x1bCA오다 노부나가\x1bCZ를 찾아가고 있었다……",
    6447: "\x1bCB모리\x1bCZ를 물리치고 우리와 친교를 맺다니,\n참으로 훌륭한 판단이로다.\n과연 ‘\x1bCC하리마\x1bCZ의 기인’이라 불릴 만하군!",
    6448: "\x1bCB모리\x1bCZ에게 양천이 있어도, 대장 \x1bCA데루모토\x1bCZ는 어리석은 장수……\n\x1bCC오와리 반국\x1bCZ에서 일어나\n\x1bCC기나이\x1bCZ를 장악한 \x1bCA노부나가\x1bCZ 님께는 못 미칩니다.",
    6449: "후후……\n아첨도 잊지 않는다는 말이로군.\n좋다, \x1bCC하리마\x1bCZ 진출은 우리도 바라던 바다.",
    6450: "하지만 만일에 대비해 인질은 받아 두겠다.\n\x1bCA[bm826]\x1bCZ, 네 적자는 원숭이에게 맡겨라.\n원숭이는 \x1bCA[bm826]\x1bCZ를 데리고 \x1bCC하리마\x1bCZ로 들어가라!",
    6451: "명을 받듭니다!",
    6452: "\x1bCA[bm826]\x1bCZ, 이것을 받아라.\n네 재능에 내리는 상이다.",
    6453: "훌륭한 칼입니다……\n과분한 영광입니다!",
    6454: "후후, ‘헤시키리’라 부르는 칼이다.\n너도 그 지략으로\n\x1bCC주고쿠\x1bCZ를 베어 갈라 보아라!",
    6455: "\x1bCB오다 가문\x1bCZ·\x1bCA[b754]\x1bCZ 저택──",
    6456: "\x1bCA노부나가\x1bCZ 님은 어떠했나?",
    6457: "어떻다니요?",
    6458: "‘\x1bCC하리마\x1bCZ의 기인’이라 불리는\n자네의 안목이 궁금할 뿐이네.\n사양 말고 말해 보게.",
    6459: "위엄에 찬 모습이셨습니다……\n천하인에 어울리는 분이라 생각합니다.",
    6460: "호오, 그런가 그런가!\n그럼 나는 어떠하냐?",
    6461: "（이 사내는 천한 출신에서 맨손으로\n\u3000\x1bCB오다 가문\x1bCZ의 중신까지 올랐다고 들었다.\n\u3000어떻게 답해야 하지……）",
    6462: "깊이 생각해도 소용없으니 솔직히 말씀하십시오.",
    6463: "……!\n당신은……\n\x1bCA다케나카 한베에\x1bCZ 님이십니까?",
    6464: "예, 그렇습니다.\n제법 알아보고 오신 모양이군요.",
    6465: "당신의 높은 명성은\n천하에 모르는 이가 없습니다!",
    6466: "후후…… 내 이야기는 그만두지요.\n지금은 \x1bCA히데요시\x1bCZ 님 이야기를 하고 있었는데요?",
    6467: "그렇지!\n\x1bCA[bm826]\x1bCZ가 나를 어떻게 보는지,\n이제 다 알겠구나!",
    6468: "아니, 그건……",
    6469: "하하하!\n농담이니 신경 쓰지 마라.",
    6470: "하지만 한 가지 더 알았다.\n자네는 거짓말을 못 하는 사내로군.\n\x1bCA한베에\x1bCZ와는 아주 다르다!",
    6471: "그렇습니다……\n의심은 많아도 거짓말은 못 하는 분,\n함께 싸우기에 알맞은 분입니다.",
    6472: "무사의 거짓말도 무략이라 들었습니다.\n거짓을 숨기지 못하는 것은 제 무략이 모자라서……",
    6473: "상관없습니다.\n진중에 거짓말쟁이가 둘이나 필요 없으니까요……",
    6474: "그렇지, 거짓말쟁이는 하나면 된다!\n\x1bCA[bm826]\x1bCZ, \x1bCC하리마\x1bCZ에서는 우리를 도와다오!\n부탁하마!",
    6475: "（이것이 \x1bCB오다 가문\x1bCZ의 주종인가.\n\u3000이 밝음과 여유……\n\u3000천하를 노리는 자들이란 이런가……）",
    6476: "（\x1bCB오다 가문\x1bCZ과 이들의 힘이 있다면\n\u3000\x1bCC하리마\x1bCZ도 밝게 새로 태어날지 모르지）",
    6477: "\x1bCB아카마쓰 가문\x1bCZ과 \x1bCB우라가미 가문\x1bCZ이 하극상으로 쇠퇴한\n\x1bCC하리마\x1bCZ에는 소세력이 난립했고,",
    6478: "서쪽에는 \x1bCB모리\x1bCZ, 동쪽에는 \x1bCB오다 가문\x1bCZ이라는\n대립하는 대세력이 조략을 벌인 탓에,\n소세력들은 작은 다툼을 거듭했다.",
    6479: "\x1bCA히데요시\x1bCZ의 \x1bCC하리마\x1bCZ 진출 목적은\n이 상황에 마침표를 찍고,\n\x1bCB모리\x1bCZ 침공의 교두보를 세우는 것이었다.",
    6480: "새로 \x1bCA히데요시\x1bCZ 휘하에 들어온\n젊은 군사 \x1bCA[b826]\x1bCZ의 분주한 활약으로……",
    6481: "\x1bCB벳쇼 가문\x1bCZ을 비롯해 작은 다툼을 거듭하던\n\x1bCC하리마\x1bCZ의 소세력들도 \x1bCB오다 가문\x1bCZ에\n복속하는 길을 택하기 시작했다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    6373: ["himewakako_and_oniwakako_sobriquets_require_glossary_review"],
    6376: ["kira_chikasada_and_tosa_haozoku_term_require_history_review"],
    6379: ["kanetsugu_kunichika_and_fusaie_name_readings_require_review"],
    6390: ["dynamic_b473_patron_identity_requires_runtime_context_review"],
    6391: ["don_paulo_baptismal_name_requires_glossary_review"],
    6401: ["gossekke_explanatory_context_requires_history_review"],
    6408: ["tadamasa_status_and_clan_continuity_require_history_review"],
    6411: ["setonaikai_and_kinai_geopolitical_wording_requires_review"],
    6418: ["mitsuhide_marital_relative_connection_requires_history_review"],
    6428: ["okatoyo_castle_and_tozo_location_reading_requires_review"],
    6441: ["modern_education_comparison_requires_style_review"],
    6442: ["ichiryo_gusoku_institution_requires_glossary_review"],
    6444: ["dynamic_b826_and_kodera_akamatsu_chain_require_review"],
    6447: ["harima_kijin_epithet_requires_style_review"],
    6448: ["ryogawa_reference_and_terumoto_assessment_require_review"],
    6450: ["dynamic_bm826_and_saru_reference_require_runtime_review"],
    6454: ["heshikiri_name_and_chugoku_wordplay_require_glossary_review"],
    6455: ["dynamic_b754_residence_owner_requires_runtime_context_review"],
    6461: ["social_status_wording_requires_style_review"],
    6477: ["gekokujo_causality_requires_history_review"],
    6479: ["bridgehead_military_term_requires_style_review"],
    6480: ["dynamic_b826_advisor_identity_requires_runtime_context_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.26.json": (
        "9ABA4A871D9D53274E185A076FF185961D78CCD3CDF626E703CD1AD605E02BEA"
    ),
    "public/msgev_ko_historical_events_6269_6372.v0.26.json": (
        "2B2DC3E2939685B636603D476FBBF3B851619A5FA7B9E1E26F7CCBB899AD7E9E"
    ),
    "review/review_index.v0.26.json": (
        "698371DB4FB43459E48DD628DDFC035CFC0C7D25F1E9EBCB360386A2D48F0FFF"
    ),
    "validation.v0.26.json": (
        "24B7C8C964FA5C963F9CAFD6AA9FC02C8CED40B2AF0EDB754633AEA17E2FCFE3"
    ),
}
INSTALLED_RESOURCE_PINS = {
    **shared.INSTALLED_RESOURCE_PINS,
    "MSG_PK/TC/msgev.bin": {
        "size": 523_304,
        "sha256": "CB4A3E57AF2091124669E28BF1DD6B8C664BFA8A1EF800F8BB6FD79C82E1DE47",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any, relative_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": relative_path, "size": len(blob), "sha256": sha256(blob)}


def selected_ids() -> list[int]:
    excluded = set(EXCLUDED_INTERNAL_IDS)
    ids = [
        entry_id
        for entry_id in range(SCOPE_START, SCOPE_END + 1)
        if entry_id not in excluded
    ]
    if ids != sorted(TRANSLATIONS):
        raise ValueError("translation ids do not exactly cover the declared scope")
    if sum(int(event["selected_count"]) for event in EVENTS) != len(ids):
        raise ValueError("event group counts do not cover the declared scope")
    return ids


def event_for(entry_id: int) -> str:
    for event in EVENTS:
        if int(event["start_id"]) <= entry_id <= int(event["end_id"]):
            return str(event["event_id"])
    raise ValueError(f"no event group for ID {entry_id}")


def source_structure(text: str) -> dict[str, Any]:
    return shared.source_structure(text)


def public_script_counts(text: str) -> dict[str, int]:
    return shared.public_script_counts(text)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=common.strict_object
    )


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
        blob = (WORKSPACE_ROOT / relative).read_bytes()
        actual = {"size": len(blob), "sha256": sha256(blob)}
        if actual != expected:
            mismatches.append({"path": relative, "expected": expected, "actual": actual})
        snapshot[relative] = actual
    if mismatches:
        raise ValueError(f"installed msgev baseline changed: {mismatches}")
    return snapshot


def existing_dialogue_overlay_snapshot() -> dict[str, Any]:
    selected = set(selected_ids())
    owners: dict[int, str] = {}
    rows: list[dict[str, Any]] = []
    duplicate_ids: set[int] = set()
    for path in sorted((WORKSTREAM_DIR / "public").glob("msgev_ko_*.json")):
        if path.name == OVERLAY_NAME:
            continue
        overlay, blob = common.load_json_strict(path)
        resource, _, entries = common.validate_overlay_shape(overlay)
        if resource != "MSG_PK/SC/msgev.bin":
            continue
        ids = [int(entry["id"]) for entry in entries]
        for entry_id in ids:
            if entry_id in owners:
                duplicate_ids.add(entry_id)
            owners[entry_id] = path.name
        rows.append(
            {
                "path": path.relative_to(WORKSTREAM_DIR).as_posix(),
                "sha256": sha256(blob),
                "entry_count": len(ids),
                "min_id": min(ids),
                "max_id": max(ids),
            }
        )
    if duplicate_ids:
        raise ValueError(
            f"existing dialogue overlays have duplicate coordinates: {sorted(duplicate_ids)}"
        )
    overlap = sorted(selected & set(owners))
    if overlap:
        raise ValueError(f"selected IDs overlap existing dialogue overlays: {overlap}")
    return {
        "overlay_count": len(rows),
        "existing_entry_count": len(owners),
        "effective_unique_id_count": len(owners),
        "cross_overlay_duplicate_id_count": 0,
        "selected_overlap_ids": [],
        "overlays": rows,
    }


def load_tc_source(path: Path) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    pin = SOURCE_PINS["TC"]
    if len(packed) != int(pin["size"]) or sha256(packed) != pin["packed_sha256"]:
        raise ValueError("TC packed source does not match the pinned release")
    _, raw = decompress_wrapper(packed)
    if len(raw) != int(pin["raw_size"]) or sha256(raw) != pin["raw_sha256"]:
        raise ValueError("TC raw source does not match the pinned release")
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT:
        raise ValueError(
            f"TC string count is {table.string_count}, expected {STRING_COUNT}"
        )
    if rebuild_message_table(table, table.texts) != raw:
        raise ValueError("TC parse/rebuild is not byte-identical")
    return packed, raw, table


def load_sources(args: argparse.Namespace) -> dict[str, tuple[bytes, bytes, Any]]:
    loaded = {
        language: source_shared.load_source(path, language)
        for language, path in {
            "SC": args.stock_sc,
            "JP": args.stock_jp,
            "EN": args.stock_en,
        }.items()
    }
    loaded["TC"] = load_tc_source(args.stock_tc)
    return loaded


def reconstruct_sc_target(sc_source: tuple[bytes, bytes, Any]) -> dict[str, Any]:
    stock_packed, _, table = sc_source
    texts = list(table.texts)
    for entry_id, replacement in TRANSLATIONS.items():
        texts[entry_id] = replacement
    rebuilt_raw = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise ValueError("target SC table parse/rebuild verification failed")
    rebuilt_wrapper = recompress_wrapper(rebuilt_raw, stock_packed)
    _, raw_after_wrapper = decompress_wrapper(rebuilt_wrapper)
    if raw_after_wrapper != rebuilt_raw:
        raise ValueError("target SC wrapper decompress verification failed")
    return {
        "wrapper": rebuilt_wrapper,
        "raw": rebuilt_raw,
        "changed_entry_count": len(TRANSLATIONS),
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    previous_before = previous_artifact_snapshot()
    installed_before = installed_resource_snapshot()
    existing_before = existing_dialogue_overlay_snapshot()
    loaded = load_sources(args)
    tables = {language: value[2] for language, value in loaded.items()}

    shared_display_ids = [
        entry_id
        for entry_id in ids
        if len({tables[language].texts[entry_id] for language in ("SC", "JP", "TC", "EN")})
        == 1
    ]
    if shared_display_ids:
        raise ValueError(
            "selected range contains all-language shared internal keys: "
            f"{shared_display_ids}"
        )

    invariant_failures: list[dict[str, Any]] = []
    visible_lengths: dict[int, list[int]] = {}
    for entry_id in ids:
        source_sc = tables["SC"].texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(source_sc, replacement)
        if BRACKET_TOKEN_RE.findall(source_sc) != BRACKET_TOKEN_RE.findall(replacement):
            problems.append("custom bracket placeholders are not preserved in order")
        if problems:
            invariant_failures.append({"id": entry_id, "problems": problems})
        visible_lengths[entry_id] = [
            len(common.ESC_RE.sub("", line)) for line in replacement.splitlines()
        ]
    if invariant_failures:
        raise ValueError(f"replacement invariants failed: {invariant_failures}")
    entries_over_32 = [
        entry_id
        for entry_id, lengths in visible_lengths.items()
        if max(lengths) > 32
    ]
    if entries_over_32:
        details = {entry_id: visible_lengths[entry_id] for entry_id in entries_over_32}
        raise ValueError(f"authored lines exceed 32 codepoints: {details}")

    target_a = reconstruct_sc_target(loaded["SC"])
    target_b = reconstruct_sc_target(loaded["SC"])
    if target_a["wrapper"] != target_b["wrapper"] or target_a["raw"] != target_b["raw"]:
        raise ValueError("SC target reconstruction A/B is not byte-identical")

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
        shared.build(args)
    finally:
        for name, value in originals.items():
            setattr(shared, name, value)

    previous_after = previous_artifact_snapshot()
    installed_after = installed_resource_snapshot()
    existing_after = existing_dialogue_overlay_snapshot()
    if previous_before != previous_after:
        raise ValueError("previous dialogue artifacts changed during build")
    if installed_before != installed_after:
        raise ValueError("installed msgev files changed during build")
    if existing_before != existing_after:
        raise ValueError("existing dialogue overlay coordinates changed during build")

    out_root = args.out_root.resolve()
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    validation_path = out_root / VALIDATION_NAME
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence = _load_json(evidence_path)
    review = _load_json(review_path)
    validation = _load_json(validation_path)

    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v27"
    evidence["alignment_basis"] = [
        "same_resource_role",
        "same_17910_entry_count",
        "same_numeric_string_ids",
        "manual_semantic_crosscheck_of_selected_entries",
        "event_boundaries_crosschecked_in_sc_jp_tc_en",
        "no_all_language_shared_internal_keys_in_selected_range",
    ]
    evidence["source_files"] = {
        language: {**SOURCE_PINS[language], "string_count": STRING_COUNT}
        for language in ("SC", "JP", "TC", "EN")
    }
    evidence["event_groups"] = list(EVENTS)
    boundary_ids = (
        6372,
        6373,
        6389,
        6390,
        6410,
        6411,
        6427,
        6428,
        6443,
        6444,
        6481,
        6482,
    )
    evidence["boundary_anchors"] = [
        {
            "id": entry_id,
            "reference_hashes": {
                language: common.text_hash(tables[language].texts[entry_id])
                for language in ("SC", "JP", "TC", "EN")
            },
        }
        for entry_id in boundary_ids
    ]
    evidence["entry_count"] = len(ids)
    for entry in evidence["entries"]:
        entry_id = int(entry["id"])
        entry["references"]["TC"] = {
            "utf16le_sha256": common.text_hash(tables["TC"].texts[entry_id]),
            "structure": source_structure(tables["TC"].texts[entry_id]),
        }

    review["schema"] = "nobu16.kr.event-dialogue-review-index.v27"
    review["entry_count"] = len(ids)
    for entry in review["entries"]:
        entry["translation_origin"] = (
            "assistant_generated_draft_from_pinned_sc_jp_tc_en"
        )

    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v27"
    validation["scope"] = {
        "start_id": SCOPE_START,
        "end_id": SCOPE_END,
        "selected_entry_count": len(ids),
        "selected_ids_sha256": sha256(
            json.dumps(ids, separators=(",", ":")).encode("utf-8")
        ),
        "excluded_internal_entry_count": len(EXCLUDED_INTERNAL_IDS),
        "excluded_internal_ids_sha256": sha256(
            json.dumps(list(EXCLUDED_INTERNAL_IDS), separators=(",", ":")).encode("utf-8")
        ),
    }
    validation["source_alignment"] = {
        "languages": ["SC", "JP", "TC", "EN"],
        "string_count_each": STRING_COUNT,
        "selected_reference_hash_count": len(ids) * 4,
        "manual_semantic_crosschecks": len(ids),
        "pk_or_base_sources_auto_copied": False,
    }
    validation["replacement_invariants"] = {
        "checked": len(ids),
        "failures": 0,
        "custom_bracket_placeholder_checks": len(ids),
        "preserved": [
            "printf_tokens",
            "unknown_percent_count",
            "edge_whitespace",
            "esc_sequences_in_order",
            "control_characters",
            "line_break_sequence",
            "private_use_codepoints",
            "custom_bracket_placeholders_in_order",
        ],
    }
    validation["translation_status"] = {
        "translated_draft": len(ids),
        "human_review_required": len(ids),
        "runtime_reviewed": 0,
        "specific_uncertainty_entries": len(UNCERTAINTY_FLAGS),
    }
    validation["layout_heuristic"] = {
        "max_authored_line_codepoints_excluding_esc": max(
            length for lengths in visible_lengths.values() for length in lengths
        ),
        "entries_over_32": [],
        "source_fixed_linebreak_exceptions": [],
        "runtime_layout_review_required": True,
    }
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch26", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch27"
    ] = True
    validation["reconstruction"] = {
        "source_parse_rebuild_byte_identical": {
            language: True for language in ("SC", "JP", "TC", "EN")
        },
        "sc_overlay_rebuild_a_b_byte_identical": True,
        "changed_entry_count": target_a["changed_entry_count"],
        "target": {
            "complete_target_included": False,
            "wrapper_size": len(target_a["wrapper"]),
            "wrapper_sha256": sha256(target_a["wrapper"]),
            "raw_size": len(target_a["raw"]),
            "raw_sha256": sha256(target_a["raw"]),
        },
    }
    validation["existing_overlay_exclusion"] = existing_before
    validation["preexisting_integrity"] = {
        "dialogue_v01_v26_artifacts_before": previous_before,
        "dialogue_v01_v26_artifacts_after": previous_after,
        "installed_msgev_before": installed_before,
        "installed_msgev_after": installed_after,
    }
    safety = validation["safety"]
    for key in list(safety):
        if key.startswith("existing_v01_v02_v03_v04_v05_v06_v07_v08_v09"):
            safety.pop(key)
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_v22_v23_v24_v25_v26_artifacts_modified"
    ] = False
    safety["pk_or_base_source_auto_copy_performed"] = False

    overlay_meta = {
        "path": f"public/{OVERLAY_NAME}",
        "size": overlay_path.stat().st_size,
        "sha256": sha256(overlay_path.read_bytes()),
    }
    evidence_meta = write_json(evidence_path, evidence, f"evidence/{EVIDENCE_NAME}")
    review_meta = write_json(review_path, review, f"review/{REVIEW_NAME}")
    public_paths = {
        "overlay": overlay_path,
        "alignment_evidence": evidence_path,
        "review_index": review_path,
    }
    source_free_scan = {
        name: public_script_counts(path.read_text(encoding="utf-8"))
        for name, path in public_paths.items()
    }
    if any(
        counts != {"cjk_unified_count": 0, "kana_count": 0}
        for counts in source_free_scan.values()
    ):
        raise ValueError("a public artifact contains source-script text")
    validation["source_free_scan"] = source_free_scan
    validation["artifacts"] = {
        "overlay": overlay_meta,
        "alignment_evidence": evidence_meta,
        "review_index": review_meta,
    }
    validation["generator"] = {
        "path": SCRIPT_PATH.name,
        "sha256": sha256(SCRIPT_PATH.read_bytes()),
    }
    validation_meta = write_json(validation_path, validation, VALIDATION_NAME)
    if public_script_counts(validation_path.read_text(encoding="utf-8")) != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError("validation contains source-script text")
    return {
        "out_root": out_root,
        "entry_count": len(ids),
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
        "--stock-tc", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "TC" / "msgev.bin"
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
