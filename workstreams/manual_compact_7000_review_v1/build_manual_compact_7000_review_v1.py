#!/usr/bin/env python3
"""Human semantic review plan for 7xxx manual Korean event compactions.

This workstream is evidence-only. It reads a frozen strict Korean candidate,
the pre-compaction Korean backup, and direct PC JP/EN/SC/TC witnesses. Its
sole output is a JSON review artifact; it never creates a game candidate,
writes Steam files, changes Git state, or contacts a network service.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402
import nobu16_msg_table as message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-manual-compact-7000-human-review.v1"
OUTPUT_PATH = WORKSTREAM / "public" / "manual_compact_7000_review.v1.json"
HISTORICAL_MANIFEST = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "msgev_ko_steam_jp_full_layout.v2.json"
)
RESERVATION_MANIFEST = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "runtime_token_reservations.v1.json"
)
PREVIOUS_REFLOW_REVIEW = (
    REPO / "workstreams" / "manual_compact_reflow_6000_8000" / "review.v1.json"
)

CURRENT_KO_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_batch06_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
PREVIOUS_BATCH05_KO_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_batch05_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
DIRECT_JP_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msgev.bin"
)
DIRECT_EN_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin")
DIRECT_SC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin")
DIRECT_TC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin")
LEGACY_PRECOMPACTION_KO_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-v0.10.0-original-font-rollback-v1"
    r"\originals\MSG_PK\JP\msgev.bin"
)

EXPECTED_CURRENT_PROFILE = {
    "packed_sha256": "600B6F1C8BE432A5987E1A05F19DCA30AF00DB9BFBFEAC702CCB60605B19B313",
    "raw_sha256": "2EEF242A9F5183061F866C854DF51139CF0FEC3E69C004F04C665B69C91AAF5B",
}
EXPECTED_PREVIOUS_BATCH05_PROFILE = {
    "packed_sha256": "8B7B9BF8F104C56F3EED0B3B5E1871E416466CD443020D6306135CCA56E7FE42",
    "raw_sha256": "D49A221732551E6DA673657A577828640E438D02B23AF3B529130A2B9689CC7F",
}
EXPECTED_DIRECT_JP_PROFILE = {
    "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
}

MIN_ID = 7000
MAX_ID = 7999
EXPECTED_TARGET_COUNT = 201
EXPECTED_CURRENT_DIFF_COUNT = 61
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
MAX_EFFECTIVE_LINE_PX = 912
MAX_RAW_LINE_PX = 1440
MAX_LINES = 4

E = "\x1b"
ESC_RE = re.compile(r"\x1b(?:CA|CB|CC|CZ)")
RUNTIME_RE = re.compile(r"\[([a-z]+)(\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*(?:\d+)?(?:\.\d+)?[A-Za-z]")


# The 61 rows below differ from the historical compact record in the strict
# batch05 baseline. Every row has an explicit human decision: retain a
# source-complete later revision, or reconcile it with clauses/terms missing
# from that revision. This prevents a bulk legacy restore from erasing later
# quality work.
CURRENT_RECONCILIATIONS: dict[int, tuple[str, str]] = {
    7033: (
        (
            f"그 {E}CB시마즈가{E}CZ를 중흥시킨 시조가\n"
            f"{E}CA시마즈 짓신사이{E}CZ라 불린 {E}CA시마즈 다다요시{E}CZ이며,\n"
            f"그 {E}CA짓신사이{E}CZ와 함께 {E}CC사쓰마{E}CZ 통일을 이룬 이는…"
        ),
        "현재문에 남은 짓신사이 표기는 유지하되, 그 시마즈가, 별칭 관계, 함께, 통일을 이룬 주체를 원문처럼 다시 명시했다.",
    ),
    7290: (
        (
            f"하지만 {E}CA노부나가{E}CZ를 양부 {E}CA이마가와 요시모토{E}CZ의 원수로\n"
            f"여겨 원망하던 시어머니 {E}CA세나히메{E}CZ, 곧 {E}CA쓰키야마도노{E}CZ는\n"
            f"며느리 {E}CA도쿠히메{E}CZ와 사이가 나빴다……"
        ),
        "현재문의 호칭 정정은 유지하되, 하지만, 양부, 원망하던 시어머니라는 관계와 감정을 복원했다.",
    ),
    7310: (
        (
            f"포위군에 소속되어 있던 {E}CA구리야마 젠스케{E}CZ는\n"
            "곧장 성 안으로 들어가,\n"
            f"유폐된 주군 {E}CA[b826]{E}CZ의 감옥으로\n"
            "향했다."
        ),
        "포위군 소속과 즉시 입성이라는 원문의 두 정보를 복원하고, 현재문의 안전한 동적 인명 소유격은 유지했다.",
    ),
    7477: (
        (
            f"{E}CA긴치요{E}CZ 또한 아버지의 기대를 받아,\n"
            "어릴 적부터 영주의 긍지를 지니고,\n"
            "사내 무장에게도 지지 않을 기개와 무예를\n"
            "익히고 있었다."
        ),
        "긴치요 표기는 유지하되, 아버지의 기대, 어린 시절, 사내 무장에게도 뒤지지 않는다는 원문 정보를 복원했다.",
    ),
    7562: (
        (
            f"{E}CA가네쓰구{E}CZ의 어머니는 {E}CA나오에 가게쓰나{E}CZ의 여동생,\n"
            f"즉 {E}CA오후네{E}CZ는 {E}CA가네쓰구{E}CZ보다 세 살 위 사촌 누이로,\n"
            "어릴 시절에는 얼굴을 마주할 기회도 많았다."
        ),
        "오센 오기를 오후네로 바로잡고, 여동생, 사촌 누이, 어린 시절 자주 만난 관계를 원문대로 복원했다.",
    ),
    7940: (
        (
            f"옛 {E}CB오다 가문{E}CZ 필두 중신을 자임한 {E}CA시바타 가쓰이에{E}CZ와\n"
            f"주군의 원수를 갚은 {E}CA[bs754]히데요시{E}CZ.\n"
            "두 사람의 속셈은 전혀 달랐기 때문이다…"
        ),
        "시바타가 옛 오다가 필두 중신을 자임했다는 원문 관점을 복원하고, 두 사람의 상반된 계산이라는 결론을 보존했다.",
    ),
    7985: (
        (
            "삼천 명에 이르는 장례 행렬은,\n"
            f"{E}CA노부나가{E}CZ의 뒤를 이을 천하인이\n"
            f"{E}CA[bs754]히데요시{E}CZ임을\n"
            "도읍 사람들의 눈에 강렬하게 각인시킨 한편…"
        ),
        "인원 수, 후계 천하인이라는 의미, 도읍 사람들의 눈에 강렬히 각인됐다는 원문 정보를 모두 복원했다.",
    ),
}

CURRENT_PRESERVATION_NOTES: dict[int, str] = {
    7200: "가쓰히사 사후 아마고 재흥 불가, 모토하루의 두 차례 주가 멸망, 용서 불가라는 세 절이 현재문에 모두 남아 있다.",
    7203: "데루모토 알현을 위한 호송, 다카하시강 나루, 모토하루 휘하 무사의 습격이라는 사건 순서가 완결돼 있다.",
    7207: "사관을 권한 뒤 목숨을 빼앗아 비열하다는 비난을 감수한다는 독백의 원인과 평가가 모두 남아 있다.",
    7211: "달에 숙원 성취를 빌고 불요불굴로 싸운 용장의 씁쓸한 결말을 현재문이 빠짐없이 전달한다.",
    7212: "아마고 재흥과 모리 복수 모두 미완으로 남기고 죽었다는 결과와 감정이 현재문에 완결돼 있다.",
    7213: "불굴의 정신이 후세에 감동을 주고 충절이 지금도 칭송받는다는 두 결과가 모두 남아 있다.",
    7215: "두 경쟁자의 부계와 이름이 현재문에 모두 명시돼 있다.",
    7216: "나가오가 시절부터의 세습 가신과 에치고 유력자의 가게카쓰 지지가 모두 유지돼 있다.",
    7222: "아내의 호조 출신, 호조와의 동맹, 우지마사의 가게토라 지원 의뢰가 모두 유지돼 있다.",
    7226: "거금을 낼 수 있다는 사실에서 가게카쓰의 금고 장악을 추론하는 독백이 완결돼 있다.",
    7228: "가게토라 승리 뒤 다케다 포위와 호조 굴복 가능성이라는 우려가 모두 유지돼 있다.",
    7236: "가쓰요리의 계획 실패, 호조의 불신, 다케다와의 절연 선언이 모두 유지돼 있다.",
    7237: "호조 공격 대비, 기쿠히메의 정실 혼인, 우에스기와의 혼인 동맹이라는 인과가 유지돼 있다.",
    7301: "오다와의 동맹 자체, 양부 요시모토를 죽인 원수, 그와 손잡은 어리석음이라는 비난이 완결돼 있다.",
    7475: "긴치요라는 이름과 긴 자의 겸손히 경청한다는 뜻, 그 바람을 담은 작명이라는 의미가 유지돼 있다.",
    7652: "사이토가 가신, 노히메 연고자, 아사쿠라가 가신이라는 세 설과 모두 불확실하다는 결론이 유지돼 있다.",
    7675: "지용을 겸비한 명장이라는 평가와 격한 성격이 화를 불렀다는 전환이 유지돼 있다.",
    7677: "옛 다케다 가신들의 공포와 [bm1871]에게 해결을 호소한 행동이 모두 유지돼 있다.",
    7684: "다케다 측의 전언, [bm1251]의 [b1448] 평가, 훌륭한 적수라는 판단이 완결돼 있다.",
    7685: "[bm1448]에게 뒤지지 않으려 정진했고 중요한 전투에서 대패하지 않았다는 인과가 유지돼 있다.",
    7690: "나아가든 물러서든 천하에 적수가 없는 다다카쓰라는 고금무쌍 평이 유지돼 있다.",
    7695: "가이와 시나노 편입 뒤 정예 다케다군을 지탱한 인재 확보에 나섰다는 사건이 유지돼 있다.",
    7696: "옛 다케다 가신 통솔자로 [bm1871]가 성장한 젊은 이이 나오마사를 선택했다는 내용이 유지돼 있다.",
    7699: "야마가타에게 쫓긴 공포와 어쩔 수 없었다는 변명이 완결돼 있다.",
    7706: "옛 적의 반감, [bm1251]을 받든 기술과 지혜, 우리에게 도움이 된다는 결론이 모두 유지돼 있다.",
    7711: "급격한 출세로 미카와 기반이 없던 나오마사에게 옛 다케다 가신 처우를 맡긴 이유가 유지돼 있다.",
    7712: "엄한 훈련으로 정평 난 나오마사가 기개 있는 고슈 병사를 다룰 적임자라는 판단이 유지돼 있다.",
    7733: "일문중과 후다이중의 배반, 가족을 이끈 도주, 결단을 내려야 한 상황이 모두 유지돼 있다.",
    7739: "적이 오야마다군이고 노부시게가 오다로 돌아섰다는 긴급 전언이 완결돼 있다.",
    7753: "병량 보급 단절과 모리 원군의 접근 불가라는 두 문제가 모두 유지돼 있다.",
    7754: "노부나가 원군 소문과 모리가의 강화 분위기 고조가 모두 유지돼 있다.",
    7761: "노부나가의 다카마쓰 접근, 장기전의 정면충돌, 모리 멸망이라는 경고가 유지돼 있다.",
    7762: "강화의 대가가 무네하루의 목과 약간의 영토라는 조건이 유지돼 있다.",
    7772: "양군 앞의 할복과 예법에 따른 듯한 훌륭한 모습으로 히데요시를 감복시킨 결과가 유지돼 있다.",
    7780: "쓰쓰지가사키관 이탈, 니라사키 신푸성 축성, 중앙집권 추진이라는 세 정보가 유지돼 있다.",
    7781: "사람이 성, 사람이 석벽이라는 신념과 성곽에 집착하지 않던 [bm1251], 신푸 축성의 불평이 모두 유지돼 있다.",
    7792: "스루가의 [b1871]와 간토의 호조 우지마사가 전선에 합류해 사방의 적을 맞았다는 내용이 유지돼 있다.",
    7794: "노부나가를 죽인 미쓰히데의 천하인 등극 난항과 주군 복수를 노린 가신들이 모두 유지돼 있다.",
    7796: "가독 계승자 노부타다의 교토 화재 사망과 오다가의 파란 불가피라는 인과가 유지돼 있다.",
    7797: "노부타다 다음 계승권의 차남 노부카쓰와 그의 한계 때문에 천하인 지위 계승이 어렵다는 내용이 유지돼 있다.",
    7800: "오다가의 출세가, 기나이 위임, 결국 주군을 친 계략과 책모의 인물이라는 평가가 유지돼 있다.",
    7803: "결단을 부정하고 싶지 않음, 노부나가 패업 계승의 필요, 그 주체가 자신이라는 선언이 유지돼 있다.",
    7810: "축성 재능, 에치젠 평정과 기타노쇼성 축성, 노부나가의 기대 부응이라는 내용이 유지돼 있다.",
    7812: "오다가의 앞날 우선, 자신이 떠받칠 책임, 싸움만 아는 서투름이라는 독백이 유지돼 있다.",
    7813: "죽은 주군의 뜻을 이을 자신, 천하의 평온으로 가는 길을 끊지 않겠다는 결의가 유지돼 있다.",
    7814: "수라의 길 가능성, 추종 요청, 가쓰이에의 필사전 명령이 모두 유지돼 있다.",
    7817: "미천한 출신에서 제 실력으로 올라선 사람을 끄는 재주와 전국시대가 아니면 빛나지 못했을 인재라는 평가가 유지돼 있다.",
    7818: "무명 도키치 별명, 부탁을 싫은 내색 없이 완벽히 해내는 솜씨와 붙임성이 유지돼 있다.",
    7819: "노부나가의 신임, 중신으로의 성장, 강대한 모리가를 홀로 압도할 정도라는 결과가 유지돼 있다.",
    7827: "가문보다 실력을 중시한 노부나가와 그가 가장 의지한 미쓰히데와 [b754]의 쌍벽이 유지돼 있다.",
    7828: "혼노지의 변으로 옛 주군을 멸한 새 천하인 미쓰히데와 그 앞을 가로막은 히데요시의 필연성이 유지돼 있다.",
    7834: "야마자키와 덴노잔 결전, 기세 오른 히데요시군의 아케치군 압박이 유지돼 있다.",
    7841: "[bs754]군의 압승, 미쓰히데의 교토 탈출, 생존만이 유일한 길이라는 믿음이 유지돼 있다.",
    7847: "미쓰히데가 삼일천하로 불린 이유가 권력 정점의 짧은 기간이라는 점을 현재문이 명확히 한다.",
}

# Four legacy rows have a true source or terminology issue independent of the
# historical three-line compaction. They retain all source content while
# correcting only the identified Korean term or name.
LEGACY_QUALITY_OVERRIDES: dict[int, tuple[str, str]] = {
    7146: (
        "하도 여러 번 꾸중을 들어서,\n"
        "「인내」 두 글자를 벽에 걸어 두었습니다만\n"
        "그것도 지금은 「숙고」 두 글자로 바뀌었습니다.",
        "思案은 이 문맥에서 사안이 아니라 숙고와 궁리이므로 숙고로 바로잡았다.",
    ),
    7158: (
        f"「에치고의 용」, 「군신」이라고도 불린\n"
        f"전국시대가 낳은 총아 {E}CA[bm1448]{E}CZ의 삶에\n"
        "돌연 종막의 때가 찾아왔다.",
        "戦国の世の申し子를 직역한 전국 시대가 낳은 아이를 자연스러운 전국시대가 낳은 총아로 바로잡았다.",
    ),
    7633: (
        f"머지않아 비가 잦아지는 시기…\n"
        f"튼튼한 제방을 쌓아 {E}CC아시모리강{E}CZ의 물을\n"
        f"끌어들이면 {E}CC다카마쓰성{E}CZ은 외딴섬이 될 것입니다.",
        "동일 수계의 기존 한국어 표기 아시모리강에 맞춰 일본어 접미사 가와를 제거했다.",
    ),
    7867: (
        f"세상에서 {E}CC미시마{E}CZ의 {E}CB무라카미 수군{E}CZ이라 불린 해적 무리――\n"
        f"각각 {E}CC노시마{E}CZ·{E}CC구루시마{E}CZ·{E}CC인노시마{E}CZ에 의거하여 주변\n"
        "세력과 때로는 손잡고, 때로는 다투었다.",
        "三島는 이 문맥에서 세 섬을 가리키는 고유 지명 Mishima이므로 산토가 아니라 미시마로 표기했다.",
    ),
}

# Legacy full Korean is retained verbatim except for Korean semantic line
# breaks. Four reuse prior focused reflows; three additionally fail only when
# their dynamic-name reservations are included in the Static Patch 007 width.
SEMANTIC_REFLOW_OVERRIDES: dict[int, str] = {
    7308: (
        f"{E}CA노부야스{E}CZ가 {E}CA다케다 가쓰요리{E}CZ와 결탁해\n"
        f"아버지와 그 맹우 {E}CA노부나가{E}CZ에게 모반을 일으키려 한다…\n"
        f"그런 소문이 {E}CA이에야스{E}CZ의 귀에 들어간 것이다."
    ),
    7610: (
        f"그 누구보다 힘으로 밀어붙이는 어리석음을 아는 {E}CA히데요시{E}CZ는,\n"
        f"{E}CC빗추빈고{E}CZ 두 지방을 주는 조건으로\n"
        f"{E}CA무네하루{E}CZ를 회유하려 했으나\n"
        f"{E}CA무네하루{E}CZ는 거들떠보지도 않았다."
    ),
    7611: (
        f"{E}CB모리가{E}CZ 또한 {E}CB오다가{E}CZ에 대한 열세 속에서\n"
        f"최전선을 사수하는 {E}CA무네하루{E}CZ에게\n"
        "무슨 일이 생기면 큰일이라 여겨\n"
        "여러 차례 중신을 보내 격려하고 있었다."
    ),
    7734: (
        f"그것은 {E}CA오야마다 노부시게{E}CZ의 {E}CC이와도노성{E}CZ과\n"
        f"{E}CA사나다 마사유키{E}CZ의 {E}CC이와비쓰성{E}CZ\n"
        "어느 쪽으로 도망칠 것인가 하는 결단이었다."
    ),
    7522: (
        f"{E}CA[bm1448]{E}CZ는 후계자를 명확히 정하지 않았기에,\n"
        f"{E}CA[bm1454]{E}CZ와 {E}CA[bm321]{E}CZ는\n"
        "차기 당주 자리를 둘러싸고\n"
        "물밑에서 다투기 시작하고 있었다."
    ),
    7635: (
        f"{E}CA[bs754]{E}CZ 군이 쌓은 대제방은\n"
        f"장맛비와 {E}CC아시모리강{E}CZ의 물을 받아내어,\n"
        f"{E}CC다카마쓰성{E}CZ 일대는 며칠 만에\n"
        "거대한 늪지와 같은 모습을 드러냈다…"
    ),
    7926: (
        f"자아, 이제 남은 일은 쳐들어올 {E}CB호조{E}CZ를\n"
        "막는 것뿐.\n"
        f"{E}CA[bs1871]{E}CZ 님도 따르게 된 {E}CB사나다{E}CZ를\n"
        "내버려 두지는 못할 터."
    ),
}
PREVIOUS_FOCUSED_REFLOW_IDS = {7308, 7610, 7611, 7734}


class ReviewError(RuntimeError):
    """Raised when a frozen review input or invariant drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_digest(value: str) -> str:
    return digest(value.encode("utf-16-le"))


def profile(path: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    require(path.is_file(), f"read-only source missing: {path}")
    packed = path.read_bytes()
    _header, raw = lz4.decompress_wrapper(packed)
    table = message_table.parse_message_table(raw)
    require(
        message_table.rebuild_message_table(table, table.texts) == raw,
        f"message table round-trip differs: {path}",
    )
    return (
        {
            "path": str(path),
            "packed_size": len(packed),
            "packed_sha256": digest(packed),
            "raw_size": len(raw),
            "raw_sha256": digest(raw),
            "string_count": len(table.texts),
        },
        table.texts,
    )


def normalize_linebreaks(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def normalize_legacy_layout(value: str) -> str:
    """Remove inherited indent only; words, clauses, and semantic LFs remain."""
    return "\n".join(
        line.lstrip(" \u3000") for line in normalize_linebreaks(value).split("\n")
    )


def is_full_width_visible(character: str) -> bool:
    return (
        "가" <= character <= "힣"
        or "ㄱ" <= character <= "ㆎ"
        or "一" <= character <= "鿿"
        or "㐀" <= character <= "䶿"
        or "ぁ" <= character <= "ヿ"
    )


def control_signature(value: str) -> dict[str, Any]:
    return {
        "esc": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "nul_count": value.count("\x00"),
    }


def assert_colour_tags(value: str, entry_id: int) -> None:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == E:
            token = value[cursor : cursor + 3]
            require(
                ESC_RE.fullmatch(token) is not None,
                f"{entry_id}: malformed ESC token {token!r}",
            )
            if token == f"{E}CZ":
                require(in_span, f"{entry_id}: unpaired ESC close")
                in_span = False
            else:
                require(not in_span, f"{entry_id}: nested ESC colour span")
                in_span = True
            cursor += 3
            continue
        require(
            not (in_span and value[cursor] in "\r\n"),
            f"{entry_id}: line break inside colour tag",
        )
        cursor += 1
    require(not in_span, f"{entry_id}: unterminated ESC colour span")


def visible_units(value: str) -> list[str]:
    return re.findall(
        r"\[[a-z]+\d+\]|[가-힣A-Za-z0-9]+|[^\s]",
        ESC_RE.sub("", value),
    )


def reintroduced_surface_units(before: str, after: str) -> list[str]:
    prior = visible_units(before)
    target = visible_units(after)
    result: list[str] = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(
        a=prior, b=target
    ).get_opcodes():
        if tag in {"insert", "replace"}:
            for unit in target[j1:j2]:
                if unit not in result:
                    result.append(unit)
    return result[:64]


def layout_lines(
    entry_id: int,
    target: str,
    current_names: tuple[str, ...],
    reservations: dict[str, Any],
) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    encoded_lines = normalize_linebreaks(target).split("\n")
    for number, encoded_line in enumerate(encoded_lines, 1):
        visible_template = ESC_RE.sub("", encoded_line)
        dynamic: list[dict[str, Any]] = []

        def render_token(match: re.Match[str]) -> str:
            token = match.group(0)
            name_id = int(match.group(2))
            require(
                0 <= name_id < len(current_names),
                f"{entry_id}: runtime name outside table: {token}",
            )
            reservation = reservations.get(token)
            require(reservation is not None, f"{entry_id}: unknown runtime token: {token}")
            display = ESC_RE.sub(
                "", normalize_linebreaks(current_names[name_id])
            ).replace("\n", " ")
            dynamic.append(
                {
                    "token": token,
                    "source_name_id": name_id,
                    "display_string": display,
                    "reserved_raw_g1n_width_px": reservation[
                        "reserved_full_name_width_px"
                    ],
                    "reserved_effective_width_px": (
                        reservation["reserved_full_name_width_px"] * DRAW_FONT_PX
                        + RAW_FULL_WIDTH_PX
                        - 1
                    )
                    // RAW_FULL_WIDTH_PX,
                    "runtime_proven": False,
                    "reservation_policy": (
                        "reviewed manifest reservation; scaled by the same 30/48 "
                        "Static Patch 007 ratio and not inferred from an unrelated route"
                    ),
                }
            )
            return display

        display = RUNTIME_RE.sub(render_token, visible_template)
        literal_without_runtime = RUNTIME_RE.sub("", visible_template)
        literal_full = sum(
            1 for character in literal_without_runtime if is_full_width_visible(character)
        )
        literal_half = len(literal_without_runtime) - literal_full
        reserved_raw = sum(item["reserved_raw_g1n_width_px"] for item in dynamic)
        raw = (
            literal_full * RAW_FULL_WIDTH_PX
            + literal_half * RAW_HALF_WIDTH_PX
            + reserved_raw
        )
        effective = (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX
        display_full = sum(1 for character in display if is_full_width_visible(character))
        display_half = len(display) - display_full
        lines.append(
            {
                "line_number": number,
                "line_count": len(encoded_lines),
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": effective,
                "full_width_character_count": display_full,
                "half_width_character_count": display_half,
                "runtime_reservations": dynamic,
                "exceeds_912px": effective > MAX_EFFECTIVE_LINE_PX,
            }
        )
    return lines


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def load_prior_reflow_targets() -> dict[int, str]:
    payload = read_json(PREVIOUS_REFLOW_REVIEW)
    rows = payload.get("rows")
    require(isinstance(rows, list), "previous reflow rows missing")
    result: dict[int, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        entry_id = row.get("entry_id")
        proposed = row.get("proposed_ko")
        if isinstance(entry_id, int) and isinstance(proposed, str):
            result[entry_id] = proposed
    for entry_id in PREVIOUS_FOCUSED_REFLOW_IDS:
        target = SEMANTIC_REFLOW_OVERRIDES[entry_id]
        require(
            result.get(entry_id) == target,
            f"{entry_id}: prior reflow target drift",
        )
    return result


def build() -> dict[str, Any]:
    current_profile, current = profile(CURRENT_KO_PATH)
    require(
        current_profile["packed_sha256"] == EXPECTED_CURRENT_PROFILE["packed_sha256"],
        "batch06 strict current packed profile drift",
    )
    require(
        current_profile["raw_sha256"] == EXPECTED_CURRENT_PROFILE["raw_sha256"],
        "batch06 strict current raw profile drift",
    )
    jp_profile, jp = profile(DIRECT_JP_PATH)
    require(
        jp_profile["packed_sha256"] == EXPECTED_DIRECT_JP_PROFILE["packed_sha256"],
        "direct PC JP packed profile drift",
    )
    require(
        jp_profile["raw_sha256"] == EXPECTED_DIRECT_JP_PROFILE["raw_sha256"],
        "direct PC JP raw profile drift",
    )
    en_profile, en = profile(DIRECT_EN_PATH)
    sc_profile, sc = profile(DIRECT_SC_PATH)
    tc_profile, tc = profile(DIRECT_TC_PATH)
    legacy_profile, legacy = profile(LEGACY_PRECOMPACTION_KO_PATH)
    for label, texts in (
        ("jp", jp),
        ("en", en),
        ("sc", sc),
        ("tc", tc),
        ("legacy", legacy),
    ):
        require(len(texts) == len(current), f"{label}/current string-count drift")

    historical = read_json(HISTORICAL_MANIFEST)
    all_entries = historical.get("entries")
    require(isinstance(all_entries, list), "historical entry list missing")
    selected = [
        entry
        for entry in all_entries
        if isinstance(entry, dict)
        and MIN_ID <= entry.get("id", -1) <= MAX_ID
        and (
            entry.get("operation") == "manual_compact_korean_layout"
            or "manual_compact_korean_layout" in entry.get("newline_operations", [])
        )
    ]
    selected.sort(key=lambda entry: entry["id"])
    require(
        len(selected) == EXPECTED_TARGET_COUNT,
        f"manual compact 7xxx count drift: {len(selected)}",
    )
    previous_batch05_profile, previous_batch05 = profile(PREVIOUS_BATCH05_KO_PATH)
    require(
        previous_batch05_profile["packed_sha256"]
        == EXPECTED_PREVIOUS_BATCH05_PROFILE["packed_sha256"],
        "batch05 scope predecessor packed profile drift",
    )
    require(
        previous_batch05_profile["raw_sha256"]
        == EXPECTED_PREVIOUS_BATCH05_PROFILE["raw_sha256"],
        "batch05 scope predecessor raw profile drift",
    )
    unchanged_scope_ids = [
        entry["id"]
        for entry in selected
        if current[entry["id"]] == previous_batch05[entry["id"]]
    ]
    require(
        len(unchanged_scope_ids) == EXPECTED_TARGET_COUNT,
        "batch06 changed a reviewed 7xxx manual compact row",
    )

    reservation_payload = read_json(RESERVATION_MANIFEST)
    reservations = reservation_payload.get("reservations")
    require(isinstance(reservations, dict), "runtime reservation map missing")
    prior_reflows = load_prior_reflow_targets()

    current_diff_ids = {
        entry["id"] for entry in selected if current[entry["id"]] != entry["ko"]
    }
    require(
        len(current_diff_ids) == EXPECTED_CURRENT_DIFF_COUNT,
        f"current historical compact diff count drift: {len(current_diff_ids)}",
    )
    decision_ids = set(CURRENT_RECONCILIATIONS) | set(CURRENT_PRESERVATION_NOTES)
    require(
        current_diff_ids == decision_ids,
        "every current-diff row must have exactly one explicit individual decision",
    )
    require(
        not (set(CURRENT_RECONCILIATIONS) & set(CURRENT_PRESERVATION_NOTES)),
        "current-diff decision categories overlap",
    )

    rows: list[dict[str, Any]] = []
    counts = {
        "simple_legacy_full_text_restoration": 0,
        "legacy_full_text_with_source_term_correction": 0,
        "legacy_full_text_with_semantic_reflow": 0,
        "source_complete_current_quality_preserved": 0,
        "current_quality_reconciled_with_source_complete_clauses": 0,
    }
    for historical_row in selected:
        entry_id = historical_row["id"]
        compact = historical_row.get("ko")
        require(isinstance(compact, str), f"{entry_id}: historical compact text missing")
        current_ko = current[entry_id]
        current_diff = entry_id in current_diff_ids
        reflow_record: dict[str, Any] | None = None
        legacy_quality_record: dict[str, Any] | None = None

        if entry_id in CURRENT_RECONCILIATIONS:
            target, review_note = CURRENT_RECONCILIATIONS[entry_id]
            strategy = "reconcile_current_quality_revision_with_source_complete_clauses"
            semantic_status = "reconciled_source_omission_or_term"
            counts["current_quality_reconciled_with_source_complete_clauses"] += 1
        elif entry_id in CURRENT_PRESERVATION_NOTES:
            target = normalize_linebreaks(current_ko)
            review_note = CURRENT_PRESERVATION_NOTES[entry_id]
            strategy = "preserve_post_compaction_current_quality_revision"
            semantic_status = "source_complete_current_revision_preserved"
            counts["source_complete_current_quality_preserved"] += 1
        elif entry_id in LEGACY_QUALITY_OVERRIDES:
            target, review_note = LEGACY_QUALITY_OVERRIDES[entry_id]
            strategy = "restore_precompaction_full_text_with_source_term_correction"
            semantic_status = "legacy_full_text_restored_with_source_term_correction"
            legacy_quality_record = {
                "legacy_ko_before_term_correction": normalize_legacy_layout(legacy[entry_id]),
                "correction_note": review_note,
            }
            counts["legacy_full_text_with_source_term_correction"] += 1
        elif entry_id in SEMANTIC_REFLOW_OVERRIDES:
            legacy_unreflowed = normalize_legacy_layout(legacy[entry_id])
            legacy_metrics = layout_lines(
                entry_id, legacy_unreflowed, current, reservations
            )
            target = SEMANTIC_REFLOW_OVERRIDES[entry_id]
            if entry_id in PREVIOUS_FOCUSED_REFLOW_IDS:
                require(
                    target == prior_reflows[entry_id],
                    f"{entry_id}: focused reflow target no longer matches",
                )
            strategy = "restore_precompaction_full_text_with_semantic_reflow"
            semantic_status = "legacy_full_text_restored_with_revalidated_semantic_reflow"
            review_note = (
                "압축 전 완전한 한국어 문장을 유지하되, 이전 focused review의 "
                "Static Patch 007 통과 개행을 그대로 재검증했다."
            )
            reflow_record = {
                "prior_review_path": (
                    str(PREVIOUS_REFLOW_REVIEW)
                    if entry_id in PREVIOUS_FOCUSED_REFLOW_IDS
                    else None
                ),
                "prior_review_target_reused_verbatim": (
                    entry_id in PREVIOUS_FOCUSED_REFLOW_IDS
                ),
                "new_dynamic_reservation_reflow": (
                    entry_id not in PREVIOUS_FOCUSED_REFLOW_IDS
                ),
                "legacy_ko_before_reflow": legacy_unreflowed,
                "legacy_line_count": len(legacy_metrics),
                "legacy_lines": legacy_metrics,
                "legacy_any_line_exceeds_912px": any(
                    line["exceeds_912px"] for line in legacy_metrics
                ),
            }
            counts["legacy_full_text_with_semantic_reflow"] += 1
        else:
            target = normalize_legacy_layout(legacy[entry_id])
            strategy = "restore_precompaction_full_korean_text"
            semantic_status = "legacy_full_text_restoration"
            review_note = (
                "직접 PC JP/EN/SC/TC 대조에서 압축 전 한국어가 사건의 "
                "주체, 행위, 결과를 보존한다는 것을 확인했다. 단어와 절은 줄이지 않고, "
                "상속된 들여쓰기만 제거한다."
            )
            counts["simple_legacy_full_text_restoration"] += 1

        require(target, f"{entry_id}: empty target")
        assert_colour_tags(target, entry_id)
        target_signature = control_signature(target)
        current_signature = control_signature(current_ko)
        jp_signature = control_signature(jp[entry_id])
        require(
            target_signature == current_signature,
            f"{entry_id}: target/current control signature drift",
        )
        require(
            target_signature == jp_signature,
            f"{entry_id}: target/direct JP control signature drift",
        )
        metrics = layout_lines(entry_id, target, current, reservations)
        require(1 <= len(metrics) <= MAX_LINES, f"{entry_id}: target line count fails")
        require(
            not any(line["exceeds_912px"] for line in metrics),
            f"{entry_id}: target exceeds Static Patch 007 912px width",
        )

        rows.append(
            {
                "id": entry_id,
                "historical_operation": historical_row.get("operation"),
                "historical_newline_operations": historical_row.get(
                    "newline_operations", []
                ),
                "review_status": "ready_for_semantic-restoration_candidate",
                "restoration_strategy": strategy,
                "semantic_status": semantic_status,
                "human_semantic_review_note": review_note,
                "current_diff_from_historical_manual_compact": current_diff,
                "current_diff_individually_reviewed": current_diff,
                "historical_manual_compact_ko": compact,
                "current_ko_at_batch05_strict_baseline": current_ko,
                "legacy_precompaction_ko": legacy[entry_id],
                "legacy_quality_correction": legacy_quality_record,
                "legacy_layout_before_semantic_reflow": reflow_record,
                "proposed_ko": target,
                "historical_compact_to_proposed_surface_units": reintroduced_surface_units(
                    compact, target
                ),
                "current_to_proposed_surface_units": reintroduced_surface_units(
                    current_ko, target
                ),
                "direct_pc_source_evidence": {
                    "jp": jp[entry_id],
                    "en": en[entry_id],
                    "sc": sc[entry_id],
                    "tc": tc[entry_id],
                },
                "current_ko_utf16le_sha256": text_digest(current_ko),
                "legacy_precompaction_ko_utf16le_sha256": text_digest(legacy[entry_id]),
                "proposed_ko_utf16le_sha256": text_digest(target),
                "control_signature": target_signature,
                "control_signature_matches_current": target_signature == current_signature,
                "control_signature_matches_direct_jp": target_signature == jp_signature,
                "target_line_count": len(metrics),
                "target_lines": metrics,
                "any_line_exceeds_912px": any(
                    line["exceeds_912px"] for line in metrics
                ),
                "japanese_source_line_breaks_used_for_korean_layout": False,
            }
        )

    require(
        sum(counts.values()) == EXPECTED_TARGET_COUNT,
        "review count accounting drift",
    )
    require(
        counts["source_complete_current_quality_preserved"]
        + counts["current_quality_reconciled_with_source_complete_clauses"]
        == EXPECTED_CURRENT_DIFF_COUNT,
        "current-diff decision count drift",
    )

    return {
        "schema": SCHEMA,
        "review_kind": "proposal_only_no_candidate",
        "scope": {
            "resource": "MSG_PK/JP/msgev.bin",
            "event_id_range": [MIN_ID, MAX_ID],
            "manual_compact_target_count": len(rows),
            "current_diff_individual_review_count": EXPECTED_CURRENT_DIFF_COUNT,
            "review_counts": counts,
            "candidate_binary_created": False,
            "steam_files_written": False,
            "git_or_release_actions_performed": False,
        },
        "layout_baseline": {
            "name": "Static Patch 007 verified PK event dialogue",
            "runtime_font_px": DRAW_FONT_PX,
            "runtime_line_spacing_setting": 8,
            "runtime_usable_line_width_px": MAX_EFFECTIVE_LINE_PX,
            "maximum_lines": MAX_LINES,
            "raw_g1n_full_width_advance_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_advance_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_g1n_pass_limit_px": MAX_RAW_LINE_PX,
            "effective_width_pass_limit_px": MAX_EFFECTIVE_LINE_PX,
            "japanese_source_line_break_policy": (
                "direct JP line breaks are semantic evidence only; Korean breaks "
                "are placed independently at Korean semantic boundaries"
            ),
            "runtime_token_policy": (
                "manifest reservation only; same 30/48 scale; every dynamic "
                "reservation record has runtime_proven=false"
            ),
        },
        "sources": {
            "strict_current_korean_batch06": current_profile,
            "batch05_scope_stability_predecessor": {
                **previous_batch05_profile,
                "all_201_manual_compact_scope_rows_unchanged_in_batch06": True,
                "unchanged_entry_count": len(unchanged_scope_ids),
            },
            "direct_pc_jp_pristine": jp_profile,
            "direct_pc_en": en_profile,
            "direct_pc_sc": sc_profile,
            "direct_pc_tc": tc_profile,
            "legacy_precompaction_korean_backup": legacy_profile,
            "historical_manual_compact_manifest": {
                "path": str(HISTORICAL_MANIFEST),
                "sha256": digest(HISTORICAL_MANIFEST.read_bytes()),
            },
            "runtime_token_reservation_manifest": {
                "path": str(RESERVATION_MANIFEST),
                "sha256": digest(RESERVATION_MANIFEST.read_bytes()),
            },
            "prior_focused_reflow_review": {
                "path": str(PREVIOUS_REFLOW_REVIEW),
                "sha256": digest(PREVIOUS_REFLOW_REVIEW.read_bytes()),
                "revalidated_entry_ids": sorted(PREVIOUS_FOCUSED_REFLOW_IDS),
            },
        },
        "entries": rows,
    }


def verify(payload: dict[str, Any]) -> None:
    scope = payload.get("scope", {})
    require(
        scope.get("manual_compact_target_count") == EXPECTED_TARGET_COUNT,
        "output target count incorrect",
    )
    rows = payload.get("entries")
    require(isinstance(rows, list) and len(rows) == EXPECTED_TARGET_COUNT, "row count")
    reviewed = [
        row
        for row in rows
        if row.get("current_diff_from_historical_manual_compact")
        and row.get("current_diff_individually_reviewed")
    ]
    require(
        len(reviewed) == EXPECTED_CURRENT_DIFF_COUNT,
        "current-diff individual review evidence missing",
    )
    for row in rows:
        require(
            row.get("target_line_count", 0) <= MAX_LINES,
            f"{row.get('id')}: too many target lines",
        )
        require(
            not row.get("any_line_exceeds_912px"),
            f"{row.get('id')}: line width failure",
        )
        for line in row.get("target_lines", []):
            require(
                line.get("effective_width_px", MAX_EFFECTIVE_LINE_PX + 1)
                <= MAX_EFFECTIVE_LINE_PX,
                f"{row.get('id')}: effective width failure",
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.command == "build":
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "output": str(OUTPUT_PATH),
                    "manual_compact_target_count": len(payload["entries"]),
                    "review_counts": payload["scope"]["review_counts"],
                    "candidate_binary_created": False,
                    "steam_files_written": False,
                },
                ensure_ascii=False,
            )
        )
    else:
        require(OUTPUT_PATH.is_file(), f"missing built artifact: {OUTPUT_PATH}")
        on_disk = read_json(OUTPUT_PATH)
        verify(on_disk)
        print(
            json.dumps(
                {
                    "verified": str(OUTPUT_PATH),
                    "manual_compact_target_count": len(on_disk["entries"]),
                    "candidate_binary_created": False,
                    "steam_files_written": False,
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
