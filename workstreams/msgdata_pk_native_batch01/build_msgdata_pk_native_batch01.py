#!/usr/bin/env python3
"""Build native PK msgdata batch 01 from 100 exact untranslated targets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = SCRIPT_PATH.parents[3]
TOOLS_ROOT = REPO_ROOT / "tools"
UPSTREAM_ROOT = REPO_ROOT / "workstreams" / "switch_msgdata_v11"
V13_ROOT = REPO_ROOT / "workstreams" / "switch_msgdata_v13_invariant_recovery"
STRDATA_ROOT = REPO_ROOT / "workstreams" / "strdata"
sys.path[:0] = [str(TOOLS_ROOT), str(UPSTREAM_ROOT), str(V13_ROOT), str(STRDATA_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgdata_v11 as upstream  # noqa: E402
import build_switch_msgdata_v13_invariant_recovery as v13  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "pk_msgdata_native_batch01_100.v1"
RESOURCE = "MSG_PK/SC/msgdata.bin"
STRING_COUNT = 29_210
OVERLAY_NAME = "msgdata_ko_pk_native_batch01_100.v1.json"
EVIDENCE_NAME = "msgdata_pk_native_batch01_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_native_batch01_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_LOGICAL_PATH = f"workstreams/msgdata_pk_native_batch01/public/{OVERLAY_NAME}"
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")
TARGET_CATALOG_RELATIVE = Path("data/public/translation_target_keys.v0.1.json")
TARGET_CATALOG_SHA256 = "FF3D15D0792052EB1A4E67BC296B3ED5169662C3510EE8F164F1331EFF07C786"
STOCK_SC_RELATIVE = Path(
    "KR_PATCH_BACKUP/file_only_transaction/pk-full-messages-seoulhangang-v1/"
    "originals/MSG_PK/SC/msgdata.bin"
)

OFFICIAL_PINS = {
    "JP": {"logical_path": "MSG_PK/JP/msgdata.bin", "size": 273_734, "sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38", "raw_size": 431_044, "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0"},
    "SC": {"logical_path": RESOURCE, "size": 516_796, "sha256": "DFFC1FA9E8D175085568C14A407B9CB4BE81CF1416DA4485A64CA330D908ADA5", "raw_size": 514_752, "raw_sha256": "5982D520BF2E66260943DE61D0CB7F1135D1BA81A211E917E3F426C58D9125D6"},
    "EN": {"logical_path": "MSG_PK/EN/msgdata.bin", "size": 267_550, "sha256": "15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1", "raw_size": 744_236, "raw_sha256": "DA913D870DA3C13F108E8E6727C9A8881B9E13A83F8EB7F02DD3C55D1D444B32"},
    "TC": {"logical_path": "MSG_PK/TC/msgdata.bin", "size": 270_032, "sha256": "A3743D318383C5D6E4D16F20B5228337DB0AE9124D144E4FBF3D4AC660FFFC5E", "raw_size": 442_224, "raw_sha256": "4D0CEB95818CC9C17623299B2B104482FED03ACCD27116604F8E29BB4C9D7684"},
}

SELECTED_IDS = tuple(
    list(range(15_063, 15_083))
    + [15_133, 15_134]
    + list(range(15_160, 15_165))
    + [15_271, 15_272, 15_273]
    + list(range(15_275, 15_282))
    + [17_981, 18_002, 18_007, 18_008, 18_009, 18_010, 18_032, 18_033, 18_034, 18_059, 18_061, 18_106]
    + list(range(18_107, 18_158))
)
SELECTED_IDS_SHA256 = "865614726A3D3F6466D084AE5496F0941EEA38F629A36C332BCCFEE4A33ED658"

EXCLUSION_GROUPS = {
    "ambiguous_name_component_proper_reading_or_title": (
        2_086, 2_089, *range(3_319, 3_330), 6_651, *range(6_655, 6_664),
        9_694, 9_894, 9_895, 9_898, 9_902, 9_904, 9_906, 9_907,
        9_910, 9_911, 9_912, 9_914, 9_915, 9_917, 9_918, 9_919,
        9_922, 9_923, 9_924, 9_925, 9_931, 9_934, 11_310, 11_311,
        13_324, 13_325, 14_764, 14_765, 14_766, 15_018, 16_403, 17_432,
    ),
    "symbol_or_rating_marker_without_translation_context": (9_146, 9_147, 9_148),
    "placeholder_dummy_not_a_translatable_display_message": (
        *range(15_350, 15_373), 15_386, *range(15_818, 15_855), 15_868,
    ),
    "romanized_lookup_or_internal_search_key": (
        15_512, 15_513, 15_514, *range(15_516, 15_523), 17_732,
    ),
    "short_fragment_role_is_ambiguous_without_runtime_owner": (
        15_753, 15_754, 15_755, 15_758, 15_759, 15_760, 15_761, 15_762,
    ),
}
EXCLUDED_IDS = tuple(sorted({entry_id for ids in EXCLUSION_GROUPS.values() for entry_id in ids}))
EXCLUDED_IDS_SHA256 = "D31AF7B3E2D358EDFC5AAA49E488C91DFFE2BA46B195E2C614A27568FAF613EC"

TRANSLATIONS = {
    15_063: "미노를 제압하고 기후성을 본거지로 삼은 오다 노부나가. 「천하포무」를 내걸고 상경을 바라보던 노부나가에게 한 남자가 도움을 청해 왔다.",
    15_064: "아마고의 본거지 갓산토다성을 함락시킨 모리 모토나리는 산요와 산인을 제압했다. 서국의 향방은 점차 모리 쪽으로 기울어 갔다.",
    15_065: "이마가와 가문과의 관계는 계속 악화되고 스루가 침공의 기운은 무르익어 갔다. 동맹의 파탄이 다가오는 가운데 가문 안에는 큰 앙금이 생겼다.",
    15_066: "중신들이 기초한 「요시하루 시키모쿠」를 받아들여 구니슈와의 융화를 꾀한 롯카쿠 조테이. 그러나 동쪽에서 거대한 위협이 다가오고 있었다.",
    15_067: "아네가와에서 아자이·아사쿠라를 격파한 지 얼마 되지 않은 오다 가문에 신겐이 일어섰다는 소식이 전해졌다. 노부나가의 싸움은 새로운 국면을 맞으려 했다.",
    15_068: "동서인 겐뇨의 요청에 응해 상경을 결심한 다케다 신겐. 다케다군의 서상 작전은 노부나가 포위망에 큰 순풍이 되었다.",
    15_069: "미카와를 공공연히 침략하는 다케다군을 막으려는 도쿠가와 이에야스. 다케다가 자랑하는 기마 군단의 맹공에도 사나운 미카와 무사들은 과감히 맞서려 했다.",
    15_070: "휴가 기자키바루에서 시마즈 요시히로는 적은 병력으로 이토군을 격파했다. 시마즈는 이를 휴가 공략의 발판으로 삼아 남규슈를 손에 넣어 갔다.",
    15_071: "에도를 본거지로 삼은 도쿠가와 이에야스는 도요토미 가문 오대로의 필두로서 막중한 영향력을 지녔다. 히데요시가 키운 다이묘들까지 아군으로 끌어들여 이시다 미쓰나리와의 결전에 나선다.",
    15_072: "히데요시가 죽은 뒤 휘하에서 자란 장수들마저 도쿠가와로 기울자, 봉행 이시다 미쓰나리가 이에 맞섰다. 우키타·우에스기 등과 손잡고 마침내 이에야스를 타도하려 움직인다.",
    15_073: "도쿠가와에 맞선 우에스기 가문의 가로 나오에 가네쓰구의 행동은 도쿠가와 이에야스를 움직이게 했다. 이시다 미쓰나리 등과 호응해 도호쿠에서 판도를 넓히려 한다.",
    15_074: "다시 찾아온 난세에 결단을 강요받는 당주 마사유키와 두 아들 노부유키·유키무라. 그들의 선택이 사나다와 천하의 앞날을 크게 뒤흔들게 된다.",
    15_075: "세이이타이쇼군으로 무가의 정점에 선 도쿠가와 가문. 이에야스는 자신이 살아 있는 동안 남은 불씨를 없애고 천하의 대업을 마무리하려 했다.",
    15_076: "도요토미 공의의 후계자 히데요리는 죽은 아버지 히데요시가 남긴 천하를 지키고자 도쿠가와와 대치한다. 본거지 오사카에는 역전의 로닌들이 모여든다.",
    15_077: "세키가하라 이후 센다이로 거처를 옮긴 다테 마사무네에게 에도에서 참전 명령이 내려왔다. 그 두 눈에는 아직도 천하를 향한 갈망이 감춰지지 않았다.",
    15_078: "세키가하라 패전으로 한때 개역의 쓰라림을 겪은 다치바나 무네시게는 훗날 다나구라 번주로 복귀했다. 그런 무네시게에게도 에도에서 참전 명령이 도착한다.",
    15_079: "호조 5대의 역사가 자칫 자신의 대에서 끊길 뻔한 호조 우지나오. 하지만 호조 최대의 판도를 넓힌 재능과 뛰어난 일문의 도움으로 재기를 꾀한다.",
    15_080: "천하인의 죽음으로 혼란한 틈을 놓치지 않은 사나다 마사유키는 권력의 공백지가 된 옛 호조 영지 일부를 빼앗아 천하를 향한 포석을 놓았다.",
    15_081: "도요토미 히데쓰구는 봉행 이시다 미쓰나리의 보좌 아래 가까스로 도요토미 가문을 추슬렀다. 죽은 히데요시의 유지를 이어 다시 도요토미 가문의 영화를 되찾으려 한다.",
    15_082: "히데요시의 경계를 받아 부젠에 눌러앉게 된 지장 간베에. 이제 따를 만한 주군이 없는 그는 야망을 드러내 천하를 손에 넣을 계책을 꾸민다.",
    15_133: "미카타가하라 전투",
    15_134: "천하에 평안은 없다",
    15_160: "오다 노부나가가 죽은 뒤, 그 뜻을 이어 천하 통일을\n이룬 도요토미 히데요시마저 세상을 떠났다. 천하의 향방은\n도요토미 정권의 대로로서 중책을 맡은 도쿠가와 이에야스에게\n기울었다. 많은 이가 다음 천하인을 이에야스로 여기는 가운데\n도요토미의 세상을 지키려는 봉행 이시다 미쓰나리는 공공연히\n그와 맞서 천하를 가를 결전을 벌인다.",
    15_161: "천하 평정――한때 오다 노부나가가 내건 이상은\n도쿠가와 이에야스의 손으로 이루어지려 했다. 난세의\n불씨인 도요토미를 진압해 난세에 막을 내리려는 이에야스.\n사나다 유키무라는 죽을 곳을 찾는 무사들과 오사카성에서\n그를 맞아 싸운다. 노리는 것은 오직 이에야스의 수급뿐.",
    15_162: "수많은 전국 다이묘가 영토 확장만 바라보던 때, 오직\n오다 노부나가만이 「천하포무」를 향해 나아갔다.\n쇼군 아시카가 요시아키를 받들어 막부 재흥을 뜻한 노부나가는\n기후에서 상경길에 올랐다. 하지만 그 길에\n수많은 난관이 기다린다는 사실을 아직 알지 못했다……",
    15_163: "아네가와에서 아자이·아사쿠라를 꺾고 포위망을 돌파하던\n노부나가에게 흉보가 닿았다. 가이의 다케다 신겐이 상경한다.\n노부나가의 맹우 도쿠가와 이에야스가 이를 막으려 나섰지만,\n백전노장 지장 신겐의 군략에 거세게 농락당한다……",
    15_164: "도요토미 히데요시는 죽은 주군 오다 노부나가도 이루지 못한\n천하총무사를 눈앞에 두었지만, 오다와라성 함락 직전에\n갑자기 세상을 떠났다. 도요토미 가문을 이은 조카 히데쓰구에게\n천하인의 그릇이 없다고 본 장수들은 잇달아 독립을 결심했고,\n세상은 다시 거센 난세의 소용돌이로 돌아갔다.",
    15_271: "의로운 지휘",
    15_272: "계산의 재능",
    15_273: "불굴의 의지",
    15_275: "구로다 무사",
    15_276: "무쌍의 창",
    15_277: "용사의 뜻",
    15_278: "결사의 각오",
    15_279: "즈이헨류",
    15_280: "천시",
    15_281: "다케다의 아카조나에",
    17_981: "그야말로 청천벽력이었다",
    18_002: "……오와리 원정은 갑작스레 막을 내렸다",
    18_007: "그 이름은――",
    18_008: "오다, 노부나가",
    18_009: "천하포무의 실현을 목표로 나아가는\n전국의 패자, 오다 노부나가",
    18_010: "그 행보에는 한 치의 빈틈도 없었다",
    18_032: "인간 오십 년",
    18_033: "천상의 세월에 견주어 보면",
    18_034: "꿈과 같고 환상과도 같구나",
    18_059: "――사람들은 그녀를 「노히메」라 불렀다.",
    18_061: "다케다 가쓰요리의 대군이 미카와 나가시노성을 포위했다.",
    18_106: "그 뒤에도 용과 호랑이는 싸움을 이어 갔다……",
    18_107: "게이초 5년.",
    18_108: "동틀 녘에 그친 가을비는 이른 아침의 찬 공기 속에서 짙은 안개로 변해,",
    18_109: "전장에 진을 친 20만 대군을 뒤덮고 있었다.",
    18_110: "한 치 앞도 분간할 수 없는 안개를 바라보며,\n이시다 미쓰나리는 지난날을 되돌아보았다……",
    18_111: "다이코 히데요시가 죽은 뒤 천하를 이어야 할 이는 히데요리였다.",
    18_112: "그러나 대로로서 보좌해야 할 도쿠가와 이에야스는\n정무를 독점하고 도요토미 정권 안에 자기 세력을 계속 늘렸다.",
    18_113: "봉행인 미쓰나리는 이에 위기감을 품었다.",
    18_114: "하지만 누구도 미쓰나리의 고충을 이해하지 못했다.",
    18_115: "누구보다 주가를 중시한 까닭에,\n그 독선적인 태도는 사람들의 반감을 샀고,",
    18_116: "많은 이가 미쓰나리를 떠나 오히려 이에야스를 택했다.",
    18_117: "도쿠가와를 쓰러뜨리지 않으면 다이코 전하가 이룬 영화는\n모두 늙은 너구리에게 집어삼켜지고 말리라.",
    18_118: "미쓰나리가 맹우 오타니 요시쓰구에게\n거병을 권한 뜻은 오직 그것뿐이었다.",
    18_119: "오사카성을 장악하고 히데요리를 손에 넣은 뒤,\n미쓰나리는 모든 군세를 이끌고 결전의 땅에 이르렀다.",
    18_120: "생각해 보면 이에야스에게 가담해 저 안개 너머에 진을 친",
    18_121: "후쿠시마·구로다·호소카와 등의 제후도\n미쓰나리와 고락을 함께한 도요토미 은고의 가신들이었다.",
    18_122: "어째서 도요토미 가문의 존망이 걸린 위기를 모르는가……",
    18_123: "「지는 잎 사이 남은 단풍 더욱 애틋하니, 저무는 가을의 마지막 자취로다.」",
    18_124: "홋코쿠 가도와 나카센도가 교차하는 이 분지는\n예전에 후와 관문이 있어 「세키가하라」라 불렸다.",
    18_125: "날이 밝고 아침 안개가 마침내 걷히기 시작할 무렵,",
    18_126: "정적을 가르는 총성과 함께 아카조나에의 인마가 쇄도했다.",
    18_127: "미쓰나리의 생애에서 가장 긴 하루가 시작되려 했다……",
    18_128: "도쿠가와 이에야스는 신슈의 작은 성 우에다에\n그 규모와 어울리지 않는 대군을 보냈다.",
    18_129: "맹약을 깨고 우에스기와 손잡은 사나다에게\n철퇴를 내리기 위해서였다.",
    18_130: "목표인 우에다성은\n한때 도쿠가와 가문이 축성을 도운 성이기도 했다.",
    18_131: "정예병들은 사나다의 소수 병력 따위 두렵지 않다며\n의기양양하게 성문으로 다가갔다.",
    18_132: "바로 그때였다.",
    18_133: "「다카사고여, 이 포구의 배에 돛을 올려라.」",
    18_134: "전장에 갑자기 울려 퍼진 축언의 노랫소리에\n도쿠가와 장병들은 모두 의아해하며 눈살을 찌푸렸다.",
    18_135: "누구……지?",
    18_136: "사람을 놀리는 듯한 웃음을 띠고 성 안에서\n도쿠가와군을 내려다보며 노래하는 그 사내는",
    18_137: "수성장 사나다 아와노카미 마사유키였다.",
    18_138: "싸우기도 전에 승리를 확신한 듯\n공격군을 깔보는 적장의 태도에,",
    18_139: "도발당한 미카와 무사들은 순식간에 살기를 띠고\n오테문을 향해 곧장 공격해 들어갔다.",
    18_140: "기세를 몰아 니노마루까지 들어갔을 무렵,\n그들은 어느새 마사유키의 목소리가 멎었음을 깨달았다.",
    18_141: "그 순간, 어디에 숨어 있었는지\n성의 병사들이 일제히 총격을 퍼부었다.",
    18_142: "좁은 구루와에서 꼼짝하지 못한 도쿠가와 대군은\n줄줄이 탄환의 먹잇감이 되었다.",
    18_143: "「퇴각!」",
    18_144: "마사유키의 계략에 빠졌음을 후회했지만 이미 늦었다.",
    18_145: "엇갈려 세운 울타리에 퇴로가 막혀 도쿠가와 부대는 완전히 무너졌다.",
    18_146: "도쿠가와의 패배는 개전과 함께 결정되었다.",
    18_147: "그러나 지략가의 계략이 이 정도로 끝날 리 없었다.",
    18_148: "추격하는 성의 병사들에게 내몰리듯",
    18_149: "간가와까지 후퇴한 도쿠가와군은\n때마침 내린 비로 불어난 급류를 보고 절망했다.",
    18_150: "하지만 다가오는 사나다군은 그들에게 망설일 틈을 주지 않았다.",
    18_151: "도쿠가와 장병들은 어쩔 수 없이 거센 물살에 몸을 던졌고,\n강은 아비규환의 지옥으로 변했다.",
    18_152: "강을 건너는 대가는 육문전만으로 치를 수 없었다.",
    18_153: "이 한 번의 싸움은 도쿠가와의 체면을 짓밟고\n사나다에 대한 두려움을 깊이 새겼다.",
    18_154: "사나다와 도쿠가와. 두 가문의 오랜 악연은 여기서 시작되었다.",
    18_155: "덴쇼 원년.",
    18_156: "고호쿠의 다이묘 아자이 나가마사의 무운이 여기서 다하려 했다.",
    18_157: "눈앞의 시야는 온통 오다의 모과 문양 깃발로 뒤덮였다.",
}

OFFICIAL_SELECTED_ROWSET_SHA256 = {
    "JP": "DBCE0F178136E3D786AF297014ED571B4B81132D92617B48CE0D95C96CA9877A",
    "SC": "EBE0E2C11FE85B112B23035B84839C6AF29B5EE1562D8457D88F02BE8E312EAC",
    "EN": "B9468AC2C73DEEB8262E9C451A278D5B59E654129C7C35D7AF39A205E5285E23",
    "TC": "2FF44E4040A90139EF6217E335EB95BCAEEC65611AE2CD5E4CFBCB6E3A83E6A6",
}

OWNER_OVERLAYS = (
    ("data/public/msgdata_ko_officer_names_0000_2399.v0.1.json", "D787EB64BFFC54D1ACA2F23BC9407991FEB4FCF76D102E1EE017EEF416FE4FA3", 3_831, "ADBE4F9A948FD4440D5D997D0D8ADD2088696F1A30147932D9A9948754AD7D6E"),
    ("workstreams/castle_names/public/castle_names_ko_9151_9542.v0.2.json", "0CEFDE11008F4503198903E1FA25ACDDB120F6B407405EF9ACE2B01B39577E5E", 392, "474F7B7EA14CA96FF70EBCD63D1FF2CBC0E3CE5BC89ECDD4B9EB8D25E67CE850"),
    ("workstreams/province_names/public/province_names_ko_13975_14046.v0.2.json", "2EF65EBDEF21521857477EA180E7FBC7AB92F1626FC69D06BD6262E97BFDBDF5", 72, "92FC19CAC52F04FD5D0DEC3F98F0C929B232DDD41F1D9C2F94059260E9C57A8A"),
    ("workstreams/msgdata/public/msgdata_ko_faction_labels_3032_3221.v0.1.json", "A277CC298262A46683CDB81273487BB5EF4AAD25FE361C1977251B52A1BF7244", 190, "BFE9A2B0651D15EB08DA4DD5E1B0C31FDC6BB7E670B1ACF8ED551F7F6C5A44FD"),
    ("workstreams/msgdata/public/msgdata_ko_name_components_3222_3315.v0.1.json", "9B887DE854B6ADE847036F1D757925AFFA9BD84FD041ADAB0CE23DA0D3DAC09A", 94, "17FE6A25C8D2A4EBE5FE311C3154576D4811F983014F43CF7FB2034557524F54"),
    ("workstreams/switch_msgdata_v11/public/msgdata_ko_switch_v11_strict_transfer.v0.1.json", "1C748373DFF712E52BA11459E032E3611ED5151EF18633E592452D3A2A78392E", 16_176, "B8AC5996A1D9A6231E8A22AC130C077E0F11830F181FF66FA5FB6929C6FB34BB"),
    ("workstreams/switch_msgdata_v13_invariant_recovery/public/msgdata_ko_switch_v13_invariant_recovery_145.v1.json", "0372E73879BD2E3C927F69375079AA6EE507E2FF2824E9AE8E8525E109CCC982", 145, "8BBA6F1E8AC5867BFB0361D4A58D3DAF023BAB559CFEE5044520810A39E79BD0"),
    ("workstreams/msgdata_pk_native_completion/public/msgdata_ko_pk_native_completion_2.v1.json", "C7D06A9FBE0B11DCA043E7C52DC907898BAF238FD9827913AB04DF47AA494709", 2, "3AF6019509AC61D8A40353E3537EA33EE1D46EA6650732FDE4DBBDD76288C63E"),
)
EXPECTED_OWNER_AUTHORED_COUNT = 20_902
EXPECTED_OWNER_UNION_COUNT = 20_830
EXPECTED_OWNER_DUPLICATE_COUNT = 72
EXPECTED_OWNER_IDS_SHA256 = "9AB8B0CEA93B5567A19B0373F6CF0F20CF0FB6628E427EE4DFB7F167887A858C"

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
CUSTOM_BRACKET_RE = re.compile(r"\[[A-Za-z0-9_]+\]")


class BatchError(ValueError):
    pass


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def script_counts(text: str) -> dict[str, int]:
    return {"cjk_unified_count": len(CJK_RE.findall(text)), "kana_count": len(KANA_RE.findall(text))}


def write_json(path: Path, value: Any, logical_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": logical_path, "size": len(blob), "sha256": sha256(blob)}


def load_pinned_table(path: Path, pin: dict[str, Any], label: str) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    if len(packed) != pin["size"] or sha256(packed) != pin["sha256"]:
        raise BatchError(f"{label} packed resource differs from its pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise BatchError(f"{label} raw resource differs from its pin")
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT or rebuild_message_table(table, table.texts) != raw:
        raise BatchError(f"{label} table layout or round trip changed")
    return packed, raw, table


def make_entries() -> list[dict[str, Any]]:
    if tuple(sorted(TRANSLATIONS)) != SELECTED_IDS:
        raise BatchError("translation dictionary does not match the fixed selected IDs")
    return [
        {"id": entry_id, "source_sc_utf16le_sha256": SOURCE_SC_HASHES[entry_id], "ko": TRANSLATIONS[entry_id]}
        for entry_id in SELECTED_IDS
    ]


SOURCE_SC_HASHES: dict[int, str] = {}


def make_overlay() -> dict[str, Any]:
    if set(SOURCE_SC_HASHES) != set(SELECTED_IDS):
        raise BatchError("SC source hashes have not been initialized from the pinned table")
    pin = OFFICIAL_PINS["SC"]
    return {
        "schema": common.OVERLAY_SCHEMA, "overlay_id": BATCH_ID,
        "resource": RESOURCE, "base_language": "SC", "entry_count": len(SELECTED_IDS),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_sc": {"size": pin["size"], "packed_sha256": pin["sha256"], "raw_size": pin["raw_size"], "raw_sha256": pin["raw_sha256"], "string_count": STRING_COUNT},
        "defaults": {"status": "translated"}, "entries": make_entries(),
    }


def load_owner_catalog() -> dict[str, Any]:
    union: set[int] = set()
    authored = 0
    rows = []
    for logical_path, expected_hash, expected_count, expected_ids_hash in OWNER_OVERLAYS:
        overlay, blob = common.load_json_strict(REPO_ROOT / logical_path)
        ids = [entry.get("id") for entry in overlay.get("entries", [])]
        resource = overlay.get("resource") or (overlay.get("target") or {}).get("resource")
        if resource != RESOURCE or sha256(blob) != expected_hash or len(ids) != expected_count:
            raise BatchError(f"owner overlay changed: {logical_path}")
        if any(type(entry_id) is not int for entry_id in ids) or len(ids) != len(set(ids)) or hash_json(sorted(ids)) != expected_ids_hash:
            raise BatchError(f"owner overlay IDs changed: {logical_path}")
        union.update(ids); authored += len(ids)
        rows.append({"path": logical_path, "sha256": expected_hash, "entry_count": len(ids), "ids_sha256": expected_ids_hash})
    if (authored, len(union), authored - len(union), hash_json(sorted(union))) != (EXPECTED_OWNER_AUTHORED_COUNT, EXPECTED_OWNER_UNION_COUNT, EXPECTED_OWNER_DUPLICATE_COUNT, EXPECTED_OWNER_IDS_SHA256):
        raise BatchError("owner overlay union changed")
    if set(SELECTED_IDS) & union:
        raise BatchError("selected IDs overlap an owner overlay")
    return {"ids": union, "snapshot": {"overlays": rows, "authored_entry_count": authored, "effective_unique_id_count": len(union), "cross_overlay_duplicate_id_count": authored - len(union), "effective_ids_sha256": hash_json(sorted(union))}}


def load_target_catalog(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    if sha256(blob) != TARGET_CATALOG_SHA256:
        raise BatchError("translation target catalog differs from its pin")
    catalog = json.loads(blob.decode("utf-8"))
    rows = [row for row in catalog.get("resources", []) if row.get("path") == RESOURCE]
    if len(rows) != 1:
        raise BatchError("target catalog must contain one PK msgdata row")
    row = rows[0]
    ids = row.get("target_ids")
    if row.get("key_kind") != "id" or row.get("target_count") != 25_534 or row.get("target_keys_sha256") != "B541D484A26F0B6F4306D46A344A29846331CEBC7C6381F18122F0A161C59D3E":
        raise BatchError("PK msgdata target catalog metadata changed")
    if not isinstance(ids, list) or any(type(entry_id) is not int for entry_id in ids) or len(ids) != len(set(ids)):
        raise BatchError("PK msgdata target IDs are invalid")
    return {"ids": set(ids), "snapshot": {"path": TARGET_CATALOG_RELATIVE.as_posix(), "sha256": TARGET_CATALOG_SHA256, "target_count": len(ids), "target_ids_sha256": row["target_keys_sha256"]}}


def validate_selection(target_ids: set[int], owner_ids: set[int]) -> dict[str, Any]:
    if len(SELECTED_IDS) != 100 or tuple(sorted(SELECTED_IDS)) != SELECTED_IDS or hash_json(list(SELECTED_IDS)) != SELECTED_IDS_SHA256:
        raise BatchError("selected ID scope changed")
    if len(EXCLUDED_IDS) != 139 or hash_json(list(EXCLUDED_IDS)) != EXCLUDED_IDS_SHA256:
        raise BatchError("explicit exclusion scope changed")
    if set(SELECTED_IDS) - target_ids or set(EXCLUDED_IDS) - target_ids:
        raise BatchError("selection or exclusion contains a non-target ID")
    remaining_prefix = sorted(entry_id for entry_id in target_ids - owner_ids if entry_id <= SELECTED_IDS[-1])
    if remaining_prefix != sorted((*SELECTED_IDS, *EXCLUDED_IDS)):
        raise BatchError("untranslated target prefix changed")
    eligible = [entry_id for entry_id in remaining_prefix if entry_id not in set(EXCLUDED_IDS)]
    if eligible != list(SELECTED_IDS):
        raise BatchError("selected IDs are not the first 100 eligible ascending targets")
    return {"untranslated_prefix_count": len(remaining_prefix), "explicit_exclusion_count": len(EXCLUDED_IDS), "selected_count": len(SELECTED_IDS), "first_selected_id": SELECTED_IDS[0], "last_selected_id": SELECTED_IDS[-1], "first_100_after_explicit_exclusions": True}


def initialize_and_validate_context(tables: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows_by_language: dict[str, list[dict[str, Any]]] = {}
    for language, table in tables.items():
        rows_by_language[language] = [{"id": entry_id, "utf16le_sha256": common.text_hash(table.texts[entry_id])} for entry_id in SELECTED_IDS]
        if hash_json(rows_by_language[language]) != OFFICIAL_SELECTED_ROWSET_SHA256[language]:
            raise BatchError(f"official selected row set changed for {language}")
    SOURCE_SC_HASHES.clear()
    SOURCE_SC_HASHES.update({row["id"]: row["utf16le_sha256"] for row in rows_by_language["SC"]})
    evidence = []
    review = []
    for entry_id in SELECTED_IDS:
        sc = tables["SC"].texts[entry_id]
        ko = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(sc, ko)
        if not common.has_semantic_text(sc) or problems:
            raise BatchError(f"SC visibility or formatting contract failed at id {entry_id}: {problems}")
        if CUSTOM_BRACKET_RE.findall(sc) != CUSTOM_BRACKET_RE.findall(ko):
            raise BatchError(f"custom bracket tokens changed at id {entry_id}")
        if script_counts(ko) != {"cjk_unified_count": 0, "kana_count": 0} or not HANGUL_RE.search(ko):
            raise BatchError(f"replacement contains source script or no Hangul at id {entry_id}")
        official_hashes = {language: common.text_hash(table.texts[entry_id]) for language, table in tables.items()}
        basis = [language for language in ("JP", "SC", "EN", "TC") if common.has_semantic_text(tables[language].texts[entry_id])]
        evidence.append({"id": entry_id, "official_utf16le_sha256": official_hashes, "pk_sc_format_contract": common.message_invariants(sc), "ko_utf16le_sha256": common.text_hash(ko), "semantic_basis_languages": basis, "stock_visible_exact_target": True, "owner_disjoint": True, "pk_sc_invariants_preserved": True, "custom_bracket_tokens_preserved": True, "source_script_free": True})
        review.append({"id": entry_id, "status": "translated", "human_review_required": True, "runtime_reviewed": False, "semantic_basis_languages": basis, "stock_visible_exact_target": True, "pk_sc_invariants_preserved": True})
    return evidence, review


def load_switch_audit(switch_zip: Path, base_jp: Path, pk_jp_table: Any) -> dict[str, Any]:
    _, _, switch_archive, provenance = v13.load_switch_v13(switch_zip)
    _, _, base_archive = upstream._load_base_jp_strdata(base_jp)
    reverse, summary = upstream.build_jp_hash_reverse_index(base_archive, switch_archive)
    usable = []
    exact_present = []
    for entry_id in SELECTED_IDS:
        source = pk_jp_table.texts[entry_id]
        record = reverse.get(common.text_hash(source))
        if record is not None:
            exact_present.append(entry_id)
        if record is not None and record.get("jp") == source and record.get("candidate_ko") is not None:
            usable.append(entry_id)
    if usable:
        raise BatchError(f"Switch now has usable candidates for manually selected IDs: {usable}")
    return {"source_release": provenance, "reverse_index": summary, "exact_jp_hash_present_count": len(exact_present), "exact_jp_hash_present_ids_sha256": hash_json(exact_present), "usable_korean_candidate_count": 0, "usable_korean_candidate_ids_sha256": hash_json([])}


def validate_progress_catalog(progress_path: Path, owner_ids: set[int]) -> dict[str, Any]:
    progress, _ = common.load_json_strict(progress_path)
    matches = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(matches) != 1 or not isinstance(matches[0].get("overlay_globs"), list):
        raise BatchError("progress must contain one PK msgdata resource")
    expected_owner_paths = {row[0] for row in OWNER_OVERLAYS}
    prior_paths = []
    successor_ids: list[int] = []
    self_count = 0
    for pattern in matches[0]["overlay_globs"]:
        if not isinstance(pattern, str):
            raise BatchError("progress contains a non-string overlay path")
        paths = sorted(REPO_ROOT.glob(pattern))
        if len(paths) != 1:
            raise BatchError(f"progress overlay {pattern!r} resolved to {len(paths)} files")
        logical_path = paths[0].relative_to(REPO_ROOT).as_posix()
        if logical_path != pattern:
            raise BatchError("progress paths must be exact repo-relative paths")
        if logical_path == SELF_OVERLAY_LOGICAL_PATH:
            if paths[0].read_bytes() != encode_json(make_overlay()):
                raise BatchError("self registration is not the exact deterministic overlay")
            self_count += 1
        elif logical_path in expected_owner_paths:
            prior_paths.append(logical_path)
        else:
            overlay, _ = common.load_json_strict(paths[0])
            resource, _stock, entries = common.validate_overlay_shape(overlay)
            if resource != RESOURCE:
                raise BatchError("successor overlay targets another resource")
            successor_ids.extend(int(entry["id"]) for entry in entries)
    if self_count > 1 or set(prior_paths) != expected_owner_paths or len(prior_paths) != len(expected_owner_paths):
        raise BatchError("progress prior-owner set or self-registration count changed")
    if len(successor_ids) != len(set(successor_ids)):
        raise BatchError("successor overlays overlap each other")
    if set(successor_ids) & (owner_ids | set(SELECTED_IDS)):
        raise BatchError("successor overlays overlap this batch or its pinned owners")
    if set(SELECTED_IDS) & owner_ids:
        raise BatchError("selected IDs are already claimed")
    return {"self_registered": self_count == 1, "self_registration_count": self_count, "self_excluded_from_prior_claims": True}


def validate_overlay(overlay: dict[str, Any], stock_table: Any, owner_ids: set[int], target_ids: set[int]) -> None:
    resource, stock, entries = common.validate_overlay_shape(overlay)
    ids = [entry["id"] for entry in entries]
    if resource != RESOURCE or stock["string_count"] != STRING_COUNT or tuple(ids) != SELECTED_IDS:
        raise BatchError("overlay shape or selected scope changed")
    if set(ids) & owner_ids or set(ids) - target_ids:
        raise BatchError("overlay is not owner-disjoint exact-target-only")
    for entry in entries:
        source = stock_table.texts[entry["id"]]
        if common.text_hash(source) != entry["source_sc_utf16le_sha256"] or common.invariant_mismatches(source, entry["ko"]):
            raise BatchError(f"overlay source hash or invariant mismatch at id {entry['id']}")


def exclusion_rows(tables: dict[str, Any]) -> list[dict[str, Any]]:
    reason_by_id = {entry_id: reason for reason, ids in EXCLUSION_GROUPS.items() for entry_id in ids}
    return [{"id": entry_id, "reason": reason_by_id[entry_id], "pk_sc_utf16le_sha256": common.text_hash(tables["SC"].texts[entry_id]), "selected": False} for entry_id in EXCLUDED_IDS]


def input_snapshot(args: argparse.Namespace) -> dict[str, str]:
    paths = {"pk_jp": args.stock_pk_jp, "pk_sc": args.stock_pk_sc, "pk_en": args.stock_pk_en, "pk_tc": args.stock_pk_tc, "target_catalog": args.target_catalog, "switch_v13_archive": args.switch_zip, "base_jp_strdata": args.base_jp_strdata}
    paths.update({f"owner_{index}": REPO_ROOT / row[0] for index, row in enumerate(OWNER_OVERLAYS)})
    return {label: sha256(path.read_bytes()) for label, path in paths.items()}


def build(args: argparse.Namespace) -> dict[str, Any]:
    owners = load_owner_catalog()
    targets = load_target_catalog(args.target_catalog)
    selection = validate_selection(targets["ids"], owners["ids"])
    before = input_snapshot(args)
    packed_sc, _, sc_table = load_pinned_table(args.stock_pk_sc, OFFICIAL_PINS["SC"], "PK SC msgdata")
    tables = {"SC": sc_table}
    for language, path in (("JP", args.stock_pk_jp), ("EN", args.stock_pk_en), ("TC", args.stock_pk_tc)):
        _, _, tables[language] = load_pinned_table(path, OFFICIAL_PINS[language], f"PK {language} msgdata")
    evidence_entries, review_entries = initialize_and_validate_context(tables)
    switch_audit = load_switch_audit(args.switch_zip, args.base_jp_strdata, tables["JP"])
    overlay = make_overlay()
    validate_progress_catalog(args.progress, owners["ids"])
    validate_overlay(overlay, sc_table, owners["ids"], targets["ids"])
    target_a = upstream.reconstruct_sc_target(packed_sc, sc_table, overlay["entries"])
    target_b = upstream.reconstruct_sc_target(packed_sc, sc_table, overlay["entries"])
    if target_a != target_b:
        raise BatchError("in-memory target reconstruction is not deterministic")

    exclusions = exclusion_rows(tables)
    evidence = {"schema": "nobu16.kr.msgdata-pk-native-batch-evidence.v1", "batch_id": BATCH_ID, "resource": RESOURCE, "contains_commercial_source_text": False, "contains_complete_game_resource": False, "method": "manual_pk_jp_sc_en_tc_context_translation_after_switch_v13_reuse_audit", "target_catalog": targets["snapshot"], "selection": selection, "selected_ids_sha256": SELECTED_IDS_SHA256, "excluded_ids_sha256": EXCLUDED_IDS_SHA256, "owner_catalog": owners["snapshot"], "switch_reuse_audit": switch_audit, "entries": evidence_entries, "exclusions": exclusions}
    review = {"schema": "nobu16.kr.msgdata-pk-native-batch-review.v1", "batch_id": BATCH_ID, "resource": RESOURCE, "contains_commercial_source_text": False, "contains_complete_game_resource": False, "summary": {"translated_count": 100, "explicit_exclusion_count": 139, "human_review_required_count": 100, "runtime_reviewed_count": 0}, "entries": review_entries, "exclusions": [{"id": row["id"], "reason": row["reason"]} for row in exclusions]}
    out_root = args.out_root.resolve()
    artifacts = {}
    artifacts["overlay"] = write_json(out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}")
    artifacts["alignment_evidence"] = write_json(out_root / "evidence" / EVIDENCE_NAME, evidence, f"evidence/{EVIDENCE_NAME}")
    artifacts["review_index"] = write_json(out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}")
    for name, artifact in artifacts.items():
        if sum(script_counts((out_root / artifact["path"]).read_text(encoding="utf-8")).values()):
            raise BatchError(f"{name} contains CJK unified or kana")
    after = input_snapshot(args)
    if before != after:
        raise BatchError("read-only input changed during generation")
    validation = {"schema": "nobu16.kr.msgdata-pk-native-batch-validation.v1", "batch_id": BATCH_ID, "passed": True, "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())}, "scope": {"resource": RESOURCE, "selected_entry_count": 100, "selected_ids_sha256": SELECTED_IDS_SHA256, "excluded_count": 139, "excluded_ids_sha256": EXCLUDED_IDS_SHA256, "owner_overlap_count": 0, "non_target_count": 0}, "official_resource_pins": OFFICIAL_PINS, "official_selected_rowset_sha256": OFFICIAL_SELECTED_ROWSET_SHA256, "target_catalog": targets["snapshot"], "selection": selection, "owner_catalog": owners["snapshot"], "switch_reuse_audit": {"release_tag": switch_audit["source_release"]["tag"], "archive_sha256": switch_audit["source_release"]["archive_sha256"], "usable_korean_candidate_count": 0}, "progress_integration_policy": {"pre_integration_unregistered_allowed": True, "post_integration_exact_self_registration_allowed": True, "self_overlay_logical_path": SELF_OVERLAY_LOGICAL_PATH, "self_overlay_excluded_from_prior_claims": True}, "target_reconstruction": target_a, "reproducibility": {"in_memory_target_a_b_equal": True, "isolated_artifact_a_b_required": True}, "input_snapshot_before": before, "input_snapshot_after": after, "source_free_scan": {name: script_counts((out_root / artifact["path"]).read_text(encoding="utf-8")) for name, artifact in artifacts.items()}, "safety": {"commercial_source_text_included": False, "complete_game_resource_included": False, "global_progress_modified": False, "global_readme_modified": False, "font_modified": False, "installed_game_files_modified": False, "deployment_performed": False, "commit_or_push_performed": False}, "artifacts": artifacts}
    validation["source_free_scan"]["generation_validation"] = script_counts(encode_json(validation).decode("utf-8"))
    if any(sum(counts.values()) for counts in validation["source_free_scan"].values()):
        raise BatchError("validation source-free scan failed")
    artifacts["generation_validation"] = write_json(out_root / VALIDATION_NAME, validation, VALIDATION_NAME)
    return {"out_root": out_root, "entry_count": 100, "excluded_count": 139, "artifacts": artifacts, "target_reconstruction": target_a}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-pk-jp", type=Path, default=GAME_ROOT / "MSG_PK/JP/msgdata.bin")
    parser.add_argument("--stock-pk-sc", type=Path, default=GAME_ROOT / STOCK_SC_RELATIVE)
    parser.add_argument("--stock-pk-en", type=Path, default=GAME_ROOT / "MSG_PK/EN/msgdata.bin")
    parser.add_argument("--stock-pk-tc", type=Path, default=GAME_ROOT / "MSG_PK/TC/msgdata.bin")
    parser.add_argument("--switch-zip", type=Path, default=REPO_ROOT / v13.SWITCH_ARCHIVE_RELATIVE)
    parser.add_argument("--base-jp-strdata", type=Path, default=GAME_ROOT / "MSG/JP/strdata.bin")
    parser.add_argument("--target-catalog", type=Path, default=REPO_ROOT / TARGET_CATALOG_RELATIVE)
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE)
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
    print(f"excluded={result['excluded_count']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
