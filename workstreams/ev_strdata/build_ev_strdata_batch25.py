#!/usr/bin/env python3
"""Build source-free ev_strdata historical event batch v0.25 artifacts."""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402
import build_ev_strdata_batch24 as prior  # noqa: E402


BATCH_ID = "ev-strdata-historical-events-4751-4838-v0.25"
OVERLAY_NAME = "ev_strdata_ko_historical_events_4751_4838.v0.25.json"
EVIDENCE_NAME = "alignment_evidence.v0.25.json"
REVIEW_NAME = "review_index.v0.25.json"
VALIDATION_NAME = "validation.v0.25.json"

SCOPE_START = 4751
SCOPE_END = 4838
NEXT_DISPLAY_ID = 4839
TRANSLATED_COUNT = 88
INSPECTED_COUNT = 88
DEFERRED_COUNT = 0

TRANSLATED_IDS_SHA256 = "C4A924FC41D5205CEE875157290F3A399155108A83E44B0370C9B27FD3142345"
TRANSLATION_MAP_SHA256 = "DA2B3FCA728B44F06F942631799BC9B058580D1DB7802F4C4E1964428AE8355A"
SOURCE_SC_HASHES_SHA256 = "A8DA4F3F0452D1E2D8A772B48914F23C28B98B11E3C7E7D8C89B533AA4ADA95A"
ALL_REFERENCE_HASHES_SHA256 = "40D03C1546FBD8ED9274531025B946C6BABBE7649918FDF75B12395B228DE646"
DEFERRED_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "E3DBF673999314B4C458F1998EEE30C0E94E4FDC5380C1488CEA87EA27AA4DEB",
    "JP": "3B4E02307B30FBEA9416CD76E901D4438B6D224C9FF494F08B24B172FC0B6161",
    "TC": "E8B4304D09D95F801EC5DBA52E68B2AD747D3971B3E0624FCBE451EC3DD0AEF6",
}


# Project-authored Korean only.  The corresponding source-free dialogue draft
# was reviewed against the pinned ev_strdata SC/JP/TC records and is embedded
# here so this workstream has no runtime dependency on another workstream.
TRANSLATIONS = {
    4751: "늘 \x1bCB호조씨\x1bCZ의 압력에 시달리던 간토 제장들은\n\x1bCB호조\x1bCZ 영지 깊숙이 진격한 \x1bCA가게토라\x1bCZ를\n잇달아 지지하고 나섰다.",
    4752: "이제 \x1bCA가게토라\x1bCZ는 \x1bCC간토\x1bCZ의 구세주가 되었다.",
    4753: "이 상황에서 간토 간레이 \x1bCA우에스기 노리마사\x1bCZ는\n무력한 자신에게 자격이 없다고 판단하고,\n간레이직을 \x1bCA가게토라\x1bCZ에게 넘기기로 했다.",
    4754: "이를 예상이라도 했는지,\n\x1bCA가게토라\x1bCZ는 순순히 받아들여,\n간토 간레이직을 계승했다.",
    4755: "\x1bCA가게토라\x1bCZ의 간토 간레이 취임식은\n\x1bCC가마쿠라\x1bCZ의 \x1bCC쓰루가오카 하치만구\x1bCZ에서 열렸다.\n이는 \x1bCB호조 가문\x1bCZ을 도발하는 동시에,",
    4756: "가마쿠라 막부 이래 무문의 신을 숭배해 온 곳에서\n취임식을 열어, \x1bCA가게토라\x1bCZ의 간레이 계승에\n정당성을 더하려는 뜻도 있었다.",
    4757: "\x1bCA가게토라\x1bCZ 님,\n간토 간레이 취임을 축하드립니다.",
    4758: "\x1bCA가게이에\x1bCZ, 나는 이를 계기로 이름을 바꾸겠다.",
    4759: "과연, ‘\x1bCB우에스기\x1bCZ’ 성을 이으시는군요.",
    4760: "그뿐만이 아니다.",
    4761: "\x1bCA노리마사\x1bCZ 공의 이름 한 글자를 받아,\n‘\x1bCA마사토라\x1bCZ’라 하겠다.\n이제부터 나는 \x1bCA우에스기 마사토라\x1bCZ다.",
    4762: "……알겠습니다.",
    4763: "\x1bCA노리마사\x1bCZ 공에게 한 글자를 받는 것이\n쓸데없다고 생각하는구나.",
    4764: "아, 아닙니다……\n당치도 않습니다.",
    4765: "이름을 바꿔도 내 무용은 달라지지 않는다.\n일단 따라 주면 그만이지.",
    4766: "그렇습니다.\n이제 \x1bCC간토\x1bCZ에서 벌이는 모든 싸움은\n대의를 위한 싸움이 됩니다.",
    4767: "바로 코앞에서 이런 의식을 치렀으니,\n\x1bCB호조\x1bCZ도 체면을 구겼겠지요.",
    4768: "이렇게 되리라 예상했다.\n사욕으로 \x1bCC간토\x1bCZ를 짓누르는 \x1bCB호조\x1bCZ를……\n간토 간레이의 이름으로 멸하겠다.",
    4769: "\x1bCC히다\x1bCZ는 남북조 시대 공가인 \x1bCB아네가코지 가문\x1bCZ이\n고쿠시를 맡고, 막부가 슈고로 임명한 \x1bCB교고쿠 가문\x1bCZ과\n공존하며 분할 통치하고 있었다.",
    4770: "전국시대에 들어서자 \x1bCB교고쿠씨\x1bCZ의 지류로,\n\x1bCC히다\x1bCZ를 맡던 \x1bCB미키 가문\x1bCZ은\n\x1bCB아네가코지 가문\x1bCZ의 이름을 빼앗으려 획책했다.",
    4771: "그리고 \x1bCB미키 가문\x1bCZ의 적자 \x1bCA미키 요리쓰나\x1bCZ가\n‘\x1bCA아네가코지 요리쓰나\x1bCZ’로 개명한 뒤,\n삼 년의 세월이 흘렀다.",
    4772: "\x1bCB미키 가문\x1bCZ 당주 \x1bCA미키 요시요리\x1bCZ가 바라던\n주나곤 임명은 아직 이루어지지 않았다.",
    4773: "어째서냐……\n\x1bCA요리쓰나\x1bCZ, 너는 어째서라고 생각하느냐?",
    4774: "무엇이 어째서란 말씀이십니까?",
    4775: "어째서 주나곤이 되지 못하는 것 같으냐?\n이제 한 걸음만 남았다고 생각하는데.",
    4776: "주나곤은 구교, 곧 종3위에 해당하는\n의정관입니다…… 지방 무사가\n그리 쉽게 임명될 자리가 아닙니다.",
    4777: "그렇다면,\n나도 \x1bCB아네가코지\x1bCZ를 칭할 수밖에 없겠군.",
    4778: "아버님…… 제 말을 듣고 계십니까?",
    4779: "좋다, 이제부터 나는 \x1bCA아네가코지 요시요리\x1bCZ다!\n이러면 주나곤이 될 수 있겠지!",
    4780: "아버님……",
    4781: "본래 \x1bCC교토\x1bCZ의 \x1bCB아네가코지 가문\x1bCZ은 공가의 격으로 따지면\n‘\x1bCB우린케\x1bCZ’에 해당한다. 극관, 곧 최고 관직을\n다이나곤으로 삼는 가문이다.",
    4782: "물론 참칭에 불과해 실효는 없지만,\n다이나곤 아래인 주나곤직을 원한 \x1bCA요시요리\x1bCZ가\n\x1bCB아네가코지\x1bCZ 성을 칭한 것도 근거 없지는 않았다……",
    4783: "……하아.\n성을 바꿔도 임명되지는 않는가……",
    4784: "아버님, 몸이 불편하십니까?",
    4785: "흥, 그런 게 아니다……!\n이름을 바꾼 지도 오래되었거늘……\n하아…… 주나곤……",
    4786: "아버님!",
    4787: "왜, 왜 그리 큰소리를 내느냐.",
    4788: "저는 이렇게 생각합니다.\n지금은 힘이 곧 말을 하는 난세입니다.",
    4789: "원하는 것은 자기 손으로 움켜쥔다.\n그렇지 않습니까?",
    4790: "으, 으음……\n그렇지.",
    4791: "그렇다면 아버님도 원하시는 것은\n스스로 손에 넣으시면 됩니다.",
    4792: "……그랬지.\n좋아!\n이제부터 나는 \x1bCA아네가코지 주나곤 요시요리\x1bCZ다!",
    4793: "음, 음……\n……예?",
    4794: "지금은 힘이 곧 말을 하는 난세……\n다이묘들은 제멋대로 관위를 자칭하지.",
    4795: "예, 예.\n그렇기는 합니다만.",
    4796: "그러니 나도 우선 자칭하겠다!\n그리고 언젠가 그 관위에 걸맞은\n다이묘가 되어 보이마!",
    4797: "……\n어떠냐, \x1bCA요리쓰나\x1bCZ.\n내 생각이 틀렸느냐?",
    4798: "……아닙니다. 훌륭한 결심입니다.",
    4799: "그리하여,\n‘\x1bCA아네가코지 요시요리\x1bCZ’로 이름을 바꾼 \x1bCA미키 요시요리\x1bCZ는,\n세력 확장에 매진했다.",
    4800: "\x1bCB오다 가문\x1bCZ 본거――",
    4801: "\x1bCA[b754]\x1bCZ는 당시로서는 보기 드문 연애결혼으로\n\x1bCA네네\x1bCZ를 아내로 맞았다.",
    4802: "하지만 \x1bCA[bm754]\x1bCZ는 바람기가 있어,\n사랑하는 아내 말고도 여러 여인과 염문을 뿌렸다.",
    4803: "\x1bCA[bm754]\x1bCZ와 \x1bCA네네\x1bCZ 사이에 아이가 없어,\n어떻게든 후계자를 얻으려 다른 여인들에게\n손을 댔다는 이야기도 있지만……",
    4804: "\x1bCA네네\x1bCZ…… 네가 주군께 고자질했느냐?\n내가 바람을 피웠다고 말이야.\n주군께 호되게 꾸중을 들었다.",
    4805: "당신! 혼례 때 하신 말씀을\n잊으신 건 아니겠지요?\n내게 여인은 너 하나뿐이라고……",
    4806: "으음……\n내가 그런 말을 했던가?",
    4807: "하·셨·습·니·다!\n그때 바람을 피우면 주군께 이르겠다고\n저도 분명 말씀드렸지요?",
    4808: "이런, \x1bCA네네\x1bCZ에게는 당해 낼 수가 없군……",
    4809: "주군 \x1bCA오다 노부나가\x1bCZ가 보낸 편지에는,\n\x1bCA네네\x1bCZ가 \x1bCA[bm754]\x1bCZ의 바람기로 고민하는 것을 위로한\n내용이 남아 있다……",
    4810: "‘너는 대머리 쥐에게 과분한 여인이다’――\n편지는 \x1bCA[bm754]\x1bCZ를 그렇게 표현하고,\n\x1bCA네네\x1bCZ를 격려하는 말로 채워져 있었다.",
    4811: "‘무에 기대지 않고 지혜로 일어선다.’\n그 뜻을 가슴에 품고, 이제 이 사내는\n전란의 시대로 나아가려 했다――",
    4812: "\x1bCA구로다 모토타카\x1bCZ의 적자 \x1bCA고데라 간베에 요시타카\x1bCZ는 원복을\n치르며 \x1bCA고데라 마사모토\x1bCZ의 성을 받았지만, 주군을\n꺼려 본래의 \x1bCB구로다\x1bCZ 성도 함께 사용했다……",
    4813: "훗날 재능을 알아본 \x1bCA하시바 히데요시\x1bCZ를 만나,\n희대의 군사로 날개를 펼치게 되는――\n\x1bCA구로다 조스이\x1bCZ, 바로 그 사람이다……",
    4814: "\x1bCA이마가와 요시모토\x1bCZ가 오케하자마에서 전사한 일은,\n오랜 굴종을 강요당한 \x1bCB[bs1871] 가문\x1bCZ에\n천재일우의 기회였다.",
    4815: "그 기회를 놓치지 않고,\n\x1bCA[b1871]\x1bCZ는 선조 대대로 이어 온 땅\n\x1bCC미카와 오카자키성\x1bCZ에서 독립했다.",
    4816: "그러나 \x1bCB이마가와 가문\x1bCZ은 \x1bCC도토미\x1bCZ와 \x1bCC스루가\x1bCZ에 건재했고,\n한편 \x1bCA요시모토\x1bCZ를 꺾은 \x1bCC오와리\x1bCZ의 \x1bCB오다 가문\x1bCZ은 기세를 올렸다.\n\x1bCB[bs1871] 가문\x1bCZ에는 양쪽을 함께 상대할 힘이 없었다.",
    4817: "\x1bCC오와리\x1bCZ·\x1bCC기요스성\x1bCZ――",
    4818: "기다리고 있었다, \x1bCA다케치요\x1bCZ.\n……아니, 이제는 \x1bCA[bm1871]\x1bCZ인가.",
    4819: "\x1bCA노부나가\x1bCZ 님, 참으로 오랜만입니다.\n늦게 찾아뵌 점을 사과드립니다.",
    4820: "그러게 말이다. \x1bCB이마가와\x1bCZ에게서 독립한 건 좋다만,\n왜 곧바로 내게 오지 않았지?",
    4821: "듣자 하니 \x1bCA요시모토\x1bCZ의 전사 소식을 들었을 때,\n할복하려 했다면서?",
    4822: "그, 그것은……",
    4823: "뭐, 됐다.\n오늘 이곳에 왔다는 것은,\n\x1bCB이마가와\x1bCZ와 완전히 결별하겠다는 뜻이겠지?",
    4824: "역시 \x1bCA노부나가\x1bCZ 님은 모두 꿰뚫어 보시는군요.\n이제 \x1bCB[bs1871]\x1bCZ이 살아갈 길은\n\x1bCB오다 가문\x1bCZ과 협력하는 것뿐입니다.",
    4825: "나와 손을 잡으면 아비의 원수라 여기는 \x1bCA이마가와 우지자네\x1bCZ가\n당장 쳐들어올지도 모른다.",
    4826: "가신 중에도 아직 \x1bCB이마가와\x1bCZ의 은혜를 잊지 못한 자가\n많겠지…… 나와 손잡는 방침으로 가문을\n하나로 모을 수 있겠느냐?",
    4827: "걱정하지 않으셔도 됩니다.\n저희는 이미 \x1bCB이마가와\x1bCZ와 싸울 각오를 마쳤습니다.\n\x1bCB오다 가문\x1bCZ의 도움만 있다면……",
    4828: "현명한 판단이다. 때도 제대로 읽었군.\n네 그런 점을 높이 사는 것이다,\n\x1bCA다케치요\x1bCZ.",
    4829: "나는 반드시 천하를 얻는다!\n하지만 내 다음 천하인은……\n어쩌면 네가 될지도 모르겠군.",
    4830: "예…… 처, 천하 말씀이십니까?",
    4831: "그래, 천하다. 천하포무다!\n삼베처럼 어지러운 세상의 전쟁을 끝내려면,\n내가 천하를 얻는 수밖에 없다!",
    4832: "그토록 멀리 내다보고 계셨습니까……\n황송합니다. 하지만 제가 다음 천하인이라니,\n저를 너무 높이 평가하셨습니다.",
    4833: "아니, 나는 네 그릇을 그만큼 높이 산다.\n내가 천하인이 되는 그날까지,\n네가 내 등을 지켜 줘야겠다.",
    4834: "예, 맡겨 주십시오!\n반드시 기대에 보답하겠습니다.",
    4835: "(어디까지나 정직한 사내로군……\n\u3000하지만 바로 그 ‘성실함’이\n\u3000네 무서운 재능이다……)",
    4836: "이때 맺은 \x1bCA오다 노부나가\x1bCZ와 \x1bCA[b1871]\x1bCZ의 맹약은,\n훗날 기요스 동맹이라 불리는 혼인 동맹으로 발전했다.",
    4837: "동시에 \x1bCA모토야스\x1bCZ는 \x1bCA이에야스\x1bCZ로 이름을 바꾸었다.\n옛 주군 \x1bCA이마가와 요시모토\x1bCZ에게 받은 이름과 결별하고,\n\x1bCA노부나가\x1bCZ와 함께할 미래를 택했음을 드러냈다.",
    4838: "\x1bCA[bm1871]\x1bCZ는 그 성실함으로\n한결같이 \x1bCA노부나가\x1bCZ에게 협력을 아끼지 않았고,\n\x1bCA노부나가\x1bCZ도 계속 그에 보답했다.",
}


CURRENT_EXCLUDED_IDS = frozenset()
PREVIOUS_DEFERRED_BATCHES = prior.PREVIOUS_DEFERRED_BATCHES + (
    {
        "version": "v0.24",
        "batch_id": prior.BATCH_ID,
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": DEFERRED_IDS_SHA256,
    },
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PREVIOUS_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
PREVIOUS_DEFERRED_UNION_COUNT = 549
PREVIOUS_DEFERRED_UNION_SHA256 = prior.PREVIOUS_DEFERRED_UNION_SHA256

CLASS_COUNTS = {
    "hashiba_nene_marriage_event": 11,
    "kuroda_kanbee_coming_of_age_event": 2,
    "matsudaira_independence_kiyosu_alliance_event": 25,
    "miki_anegakoji_junaigon_event": 32,
    "uesugi_masatora_kanto_kanrei_inauguration_event": 18,
}
TERMINOLOGY_REVIEW_IDS = frozenset(
    {
        4753,
        4755,
        4761,
        4769,
        4776,
        4781,
        4782,
        4792,
        4801,
        4810,
        4812,
        4813,
        4814,
        4817,
        4824,
        4829,
        4831,
        4836,
    }
)
CROSS_REFERENCE_STRUCTURE_DIFFERENCE_IDS = frozenset(
    {4761, 4765, 4768, 4770, 4772, 4801, 4802, 4815, 4816, 4828, 4836}
)
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 88
REPEATED_SOURCE_ID_GROUPS: tuple[tuple[int, ...], ...] = ()
EXCLUDED_CANDIDATE_COUNTS = {
    "actor_reference": 0,
    "dummy_placeholder": 0,
    "empty_slot": 0,
    "internal_event_key": 0,
}


def classify(entry_id: int) -> str:
    if entry_id <= 4768:
        return "uesugi_masatora_kanto_kanrei_inauguration_event"
    if entry_id <= 4800:
        return "miki_anegakoji_junaigon_event"
    if entry_id <= 4811:
        return "hashiba_nene_marriage_event"
    if entry_id <= 4813:
        return "kuroda_kanbee_coming_of_age_event"
    return "matsudaira_independence_kiyosu_alliance_event"


def non_display_kind(text: str) -> str | None:
    if text == "":
        return "empty_slot"
    if text.isascii() and all(character.isalnum() or character == "_" for character in text):
        return "internal_event_key"
    if text.startswith("[b") and text.endswith("]") and text.count("[") == 1:
        return "actor_reference"
    if not text.strip() or text.count("?") >= 2 and text.isascii():
        return "dummy_placeholder"
    return None


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def previous_deferred_overlap_metadata() -> dict[str, Any]:
    overlap_ids = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    return {
        "previous_batches": [
            {
                "version": batch["version"],
                "batch_id": batch["batch_id"],
                "deferred_entry_count": batch["count"],
                "deferred_ids_sha256": batch["ids_sha256"],
            }
            for batch in PREVIOUS_DEFERRED_BATCHES
        ],
        "previous_deferred_union_entry_count": PREVIOUS_DEFERRED_UNION_COUNT,
        "previous_deferred_union_ids_sha256": PREVIOUS_DEFERRED_UNION_SHA256,
        "current_deferred_entry_count": DEFERRED_COUNT,
        "current_deferred_ids_sha256": DEFERRED_IDS_SHA256,
        "overlap_entry_count": len(overlap_ids),
        "overlap_ids_sha256": shared.hash_json(overlap_ids),
        "overlap_detected": bool(overlap_ids),
    }


def related_msgev_review_metadata() -> dict[str, Any]:
    return {
        "related_batches": ["msgev_historical_events_4691_4838.v0.14"],
        "same_numeric_id_semantic_reviewed_entry_count": TRANSLATED_COUNT,
        "terminology_cross_checked": True,
        "direct_translation_reuse": True,
        "source_free_reused_entry_count": TRANSLATED_COUNT,
        "ev_strdata_sc_structure_is_authoritative": True,
        "cross_reference_structure_difference_ids": sorted(
            CROSS_REFERENCE_STRUCTURE_DIFFERENCE_IDS
        ),
        "commercial_source_text_included": False,
    }


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = sorted(TRANSLATIONS)
    inspected_ids = list(range(SCOPE_START, SCOPE_END + 1))
    if len(ids) != TRANSLATED_COUNT or ids != inspected_ids:
        raise shared.EvStrDataError("v0.25 translated scope changed")
    if len(inspected_ids) != INSPECTED_COUNT:
        raise shared.EvStrDataError("v0.25 inspected count changed")
    if CURRENT_EXCLUDED_IDS or DEFERRED_COUNT != 0:
        raise shared.EvStrDataError("v0.25 current exclusion set changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.25 translated id digest changed")
    if shared.hash_json(inspected_ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.25 inspected id digest changed")
    if shared.hash_json(sorted(CURRENT_EXCLUDED_IDS)) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.25 excluded id digest changed")
    if (
        shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids])
        != TRANSLATION_MAP_SHA256
    ):
        raise shared.EvStrDataError("v0.25 Korean translation map changed")

    for batch in PREVIOUS_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(
                f"{batch['version']} deferred exclusion pin changed"
            )
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.24 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.24 deferred union digest changed")
    overlap = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.25 exclusions overlap previous batches")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.25 event classification counts changed")

    source_sc_hashes: list[str] = []
    all_reference_hashes: list[str] = []
    ids_by_source_hash: dict[str, list[int]] = defaultdict(list)
    detected_counts = Counter()
    for entry_id in ids:
        references = [
            loaded[language]["table"].texts[entry_id] for language in shared.LANGUAGES
        ]
        for text in references:
            kind = non_display_kind(text)
            if kind is not None:
                detected_counts[kind] += 1
        if any(not text.strip() for text in references):
            raise shared.EvStrDataError(f"id {entry_id}: empty aligned display text")
        source_sc = references[0]
        source_hash = common.text_hash(source_sc)
        source_sc_hashes.append(source_hash)
        all_reference_hashes.extend(common.text_hash(text) for text in references)
        ids_by_source_hash[source_hash].append(entry_id)
        failures = shared.replacement_failures(source_sc, TRANSLATIONS[entry_id])
        if failures:
            raise shared.EvStrDataError(
                f"id {entry_id}: invariant mismatch: {failures}"
            )
    if detected_counts:
        raise shared.EvStrDataError(
            f"v0.25 non-display candidate found: {dict(detected_counts)}"
        )
    repeated_groups = tuple(
        tuple(group) for group in ids_by_source_hash.values() if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.25 repeated-source groups changed")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.25 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.25 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.25 ordered SC/JP/TC source hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if non_display_kind(next_text) is not None:
            raise shared.EvStrDataError(
                f"v0.25 next candidate is not display text for {language}"
            )
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError("v0.25 next display anchor changed")
    return ids


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    ids = validate_batch_sources(loaded)
    overlap = previous_deferred_overlap_metadata()
    related_review = related_msgev_review_metadata()

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = loaded["SC"]["table"].texts[entry_id]
        reference_structures = {
            language: shared.text_structure(loaded[language]["table"].texts[entry_id])
            for language in shared.LANGUAGES
        }
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": TRANSLATIONS[entry_id],
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "classification": classify(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            loaded[language]["table"].texts[entry_id]
                        ),
                        "structure": reference_structures[language],
                    }
                    for language in shared.LANGUAGES
                },
                "cross_reference_structure_differs_from_sc": entry_id
                in CROSS_REFERENCE_STRUCTURE_DIFFERENCE_IDS,
                "translation_origin": "source_free_related_msgev_korean_reuse_with_sc_jp_tc_revalidation",
            }
        )

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": shared.RESOURCE,
        "base_language": "SC",
        "entry_count": TRANSLATED_COUNT,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": shared.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": shared.sha256(sc_raw),
            "string_count": shared.STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
    try:
        common.validate_overlay_shape(overlay)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist

    source_files = {
        language: {
            **shared.SOURCE_PINS[language],
            "relative_path": loaded[language]["relative"],
            "string_count": shared.STRING_COUNT,
        }
        for language in shared.LANGUAGES
    }
    boundary_ids = (SCOPE_START - 1, SCOPE_START, 4768, 4769, 4800, 4801, 4813, 4814, SCOPE_END, NEXT_DISPLAY_ID)
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v25",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "inspected_entry_count": INSPECTED_COUNT,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "next_display_id": NEXT_DISPLAY_ID,
            "functional_section": "historical_event_dialogue_and_narration",
            "functional_class_counts": CLASS_COUNTS,
            "excluded_candidate_counts": EXCLUDED_CANDIDATE_COUNTS,
        },
        "translation_mapping": {
            "sha256": TRANSLATION_MAP_SHA256,
            "entry_count": TRANSLATED_COUNT,
            "embedded_in_generator": True,
            "commercial_source_text_included": False,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "sc_jp_tc_semantic_review",
            "exact_sc_hash_for_every_overlay_entry",
            "ordered_sc_jp_tc_hash_set_pin",
            "standalone_internal_placeholder_actor_and_empty_detection",
            "v013_through_v024_deferred_union_overlap_check",
            "source_free_related_msgev_korean_reuse_and_revalidation",
            "sc_structure_authoritative_when_references_differ",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata resource; TC is the third "
            "reference alongside SC and JP. Official strings are represented only by hashes."
        ),
        "source_files": source_files,
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(loaded[language]["table"].texts[entry_id])
                    for language in shared.LANGUAGES
                },
            }
            for entry_id in boundary_ids
        ],
        "entry_count": TRANSLATED_COUNT,
        "entries": evidence_entries,
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v25",
        "batch_id": BATCH_ID,
        "quality_state": "historical_event_translation_draft_pending_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "terminology_review_count": len(TERMINOLOGY_REVIEW_IDS),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": classify(entry_id),
                "translation_origin": "source_free_related_msgev_korean_reuse_with_sc_jp_tc_revalidation",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": ["event_text_runtime_layout"]
                + (
                    ["historical_term_or_reading_review"]
                    if entry_id in TERMINOLOGY_REVIEW_IDS
                    else []
                )
                + (
                    ["cross_language_structure_difference_review"]
                    if entry_id in CROSS_REFERENCE_STRUCTURE_DIFFERENCE_IDS
                    else []
                ),
            }
            for entry_id in ids
        ],
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in ((overlay_path, overlay), (evidence_path, evidence), (review_path, review)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(shared.encode_json(value))
    source_free_scan = {
        path.relative_to(out_root).as_posix(): shared.source_free_counts(path.read_bytes())
        for path in (overlay_path, evidence_path, review_path)
    }
    if any(counts != {"han_or_kana_count": 0, "embedded_nul_count": 0} for counts in source_free_scan.values()):
        raise shared.EvStrDataError("v0.25 public artifact contains source script text or an embedded NUL")

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {relative: shared.sha256((game_root / Path(relative)).read_bytes()) for relative in before}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.25 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {"size": path.stat().st_size, "sha256": shared.sha256(path.read_bytes())}
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v25",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "translated_ids_sha256": TRANSLATED_IDS_SHA256,
            "inspected_entry_count": INSPECTED_COUNT,
            "inspected_ids_sha256": TRANSLATED_IDS_SHA256,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "deferred_ids_sha256": DEFERRED_IDS_SHA256,
            "next_display_id": NEXT_DISPLAY_ID,
            "total_string_slots": shared.STRING_COUNT,
            "sc_display_translation_target_count": shared.DISPLAY_TARGET_COUNT_SC,
            "functional_class_counts": CLASS_COUNTS,
            "excluded_candidate_counts": EXCLUDED_CANDIDATE_COUNTS,
        },
        "source_alignment": {
            "languages": list(shared.LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": shared.STRING_COUNT,
            "translated_reference_hash_count": TRANSLATED_COUNT * len(shared.LANGUAGES),
            "translated_ids_nonempty_in_all_references": TRANSLATED_COUNT,
            "ordered_sc_source_hashes_sha256": SOURCE_SC_HASHES_SHA256,
            "ordered_all_reference_hashes_sha256": ALL_REFERENCE_HASHES_SHA256,
            "source_files": source_files,
        },
        "translation": {
            "translation_map_sha256": TRANSLATION_MAP_SHA256,
            "translation_map_entry_count": TRANSLATED_COUNT,
            "exact_sc_hashes_emitted": TRANSLATED_COUNT,
            "runtime_layout_review_flag_count": TRANSLATED_COUNT,
            "historical_term_or_reading_review_flag_count": len(TERMINOLOGY_REVIEW_IDS),
            "cross_language_structure_difference_review_flag_count": len(CROSS_REFERENCE_STRUCTURE_DIFFERENCE_IDS),
            "source_text_embedded": False,
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": TRANSLATED_UNIQUE_SOURCE_HASH_COUNT,
            "translated_repeated_source_group_count": len(REPEATED_SOURCE_ID_GROUPS),
            "repeated_source_id_groups": [],
            "failures": 0,
        },
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "replacement_invariants": {
            "checked": TRANSLATED_COUNT,
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholders_in_order",
            ],
        },
        "raw_format": {
            "lz4_wrapper_decompression": "OK",
            "message_table_parser": "tools/nobu16_msg_table.py",
            "raw_parse_rebuild_byte_exact_languages": list(shared.LANGUAGES),
            "binary_builder_state": "enabled_offline_output_only",
        },
        "offline_binary_build": {**binary, "installed_target_written": False},
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": shared.sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {"required_runs": ["isolated_a", "isolated_b", "final"], "byte_identical_artifacts_required": True},
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "existing_v01_through_v024_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {"han_or_kana_count": 0, "embedded_nul_count": 0}:
        raise shared.EvStrDataError("v0.25 validation is not source-free")
    return {
        "entry_count": TRANSLATED_COUNT,
        "inspected_count": INSPECTED_COUNT,
        "deferred_count": DEFERRED_COUNT,
        "next_display_id": NEXT_DISPLAY_ID,
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [game_root / "MSG" / language / "ev_strdata.bin" for language in shared.LANGUAGES]
    before = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr25-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr25-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError("isolated A/B v0.25 public artifacts are not byte-identical")
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError("final v0.25 public artifacts differ from isolated A/B output")
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.25 build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"translated={result['entry_count']}")
    print(f"inspected={result['inspected_count']}")
    print(f"deferred_internal={result['deferred_count']}")
    print(f"next_display_id={result['next_display_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
