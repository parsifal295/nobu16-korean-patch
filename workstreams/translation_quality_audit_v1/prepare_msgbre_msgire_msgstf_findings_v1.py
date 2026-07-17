#!/usr/bin/env python3
"""Prepare high-confidence semantic corrections for PC message resources.

Evidence policy
---------------
* Japanese source: the single declared pristine PC Japanese backup.
* Korean target: the current live PC Steam Korean resource.
* Context only: current live PC EN/SC/TC resources, manually reviewed before
  the fixes below were entered.

This helper never reads Switch Korean data or historic Korean backups.  It
writes only ASCII-escaped JSONL below ``tmp`` and source-gates every row using
the current UTF-16LE hash and the pristine-PC format profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_ROOT = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
OUTPUT_ROOT = REPO / "tmp" / "translation_quality_audit_v1" / "semantic"
sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


# Each value is a full, coordinate-specific Korean replacement.  The 747--833
# block was independently checked row by row because the live text repeatedly
# omitted source clauses or changed actors, relationships, and outcomes.
MSGBRE_FIXES: dict[int, tuple[str, str]] = {
    587: (
        "다케다 가신. 군장을 붉은색으로 통일한 부대를 이끌어 ‘가이산의 맹호’라 불렸다. 신겐의 장남 요시노부의 후견을 맡았으나, 요시노부 모반 미수 사건의 책임을 지고 자결했다.",
        "self_harm_terminology_correction",
    ),
    599: (
        "아자이 가신. 화가 가이호 유쇼의 아버지다. 도요토미 히데요시가 ‘내 군법의 스승’이라 칭한 용장이다. 무사 봉행을 맡아 각지에서 활약했다. 주가가 멸망할 때 전사했으며 ‘가이·아카오·아메노모리 삼장’의 한 사람이다.",
        "office_title_and_wording_correction",
    ),
    702: (
        "아마고 가신. 쓰네히사 때부터 활약했다. 하야시노성대로서 미마사카 방면군을 지휘했다. 아마고 가문 멸망 후 다치하라 히사쓰나와 아마고 가문 재흥군을 결성했다. 갓산토다성 공략 중 병으로 쓰러졌다.",
        "source_outcome_correction",
    ),
    721: (
        "호소카와 가신. 시기산성주. 주군 하루모토를 따라 옛 주군 하타케야마 요시노부를 자결하게 하고 미요시 모토나가를 토벌했다. 뒤에 하루모토와 대립해 가와치 다이헤이지 전투에서 호소카와군과 싸웠으나 패사했다.",
        "self_harm_terminology_correction",
    ),
    747: (
        "모리 가신. 모리 가문이 이와미를 평정한 뒤 모노이와즈성을 쌓아 거성으로 삼았다. 뒤에 영지 문제로 주가를 배반한 후쿠야 다카카네의 공격을 받았으나 아들 쓰네이에와 함께 격퇴했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    748: (
        "모리 가신. 쓰네야스의 아들이다. 야마나 도요쿠니에게 추방당해 이나바 돗토리성에 들어가 하시바 히데요시군과 싸웠다. 그러나 히데요시의 ‘굶겨 죽이기’ 전법에 패해 성병들의 목숨을 살리는 것을 조건으로 자결했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    749: (
        "깃카와 가신. 구니쓰네의 둘째 아들이다. 조카 오키쓰네의 측근인 오시오 가문이 가혹한 정치를 폈기에 모리와키 스케아리와 함께 오시오 가문을 토벌하고 오키쓰네를 은거시킨 뒤 모리 모토나리의 아들 모토하루를 맞아들였다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    750: (
        "모토하루의 장남. 아버지에 뒤지지 않는 무용을 자랑했으며, 도요토미 히데요시의 규슈 정벌에 종군했을 때도 늘 승리를 거두었다고 한다. 아버지가 은거한 뒤 가독을 이었으나, 아버지가 죽은 지 얼마 지나지 않아 병사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    751: (
        "모토하루의 셋째 아들. 세키가하라 전투에서 서군의 패배를 예견하고 외교 교섭으로 모리 가문의 존속을 꾀했다. 그러나 종가는 스오·나가토 두 나라로 감봉되었고, 가문 안에서 배신자라는 비난을 받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    752: (
        "벳쇼 가신. 기누가사성주. 기누가사 가문은 아카마쓰 가문의 서류다. 한때 미요시 나가요시에게 속해 각지에서 전전했다. 하시바 히데요시의 주고쿠 침공군과 싸우다 패했으며, 낙향했다는 설과 전사했다는 설이 있다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    753: (
        "도요토미 가신. 이에사다의 둘째 아들이다. 히메지성대를 맡아 세키가하라 전투에서 서군 소속인 동생 고바야카와 히데아키의 입성을 거부했다. 『게이초 일기』는 1613년의 1년간을 기록한 사료다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    754: (
        "전국시대 제일의 입신출세가. 오다 노부나가를 섬기며 뛰어난 인망과 지략을 무기로 활약해 두각을 나타냈다. 혼노지의 변 뒤 아케치 미쓰히데와 시바타 가쓰이에 등을 차례로 물리치고 천하의 패권을 떨쳤다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    755: (
        "도요토미 가신. 기노시타 이에사다의 아들. 도요토미 히데요시의 명으로 고바야카와 다카카게의 양자가 되었다. 세키가하라 전투에서 동군으로 돌아서 동군의 승리에 크게 공헌했으나 2년 뒤 급사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    756: (
        "히데요시의 이복동생. 형의 오른팔로서 패업에 공헌했다. 온화하고 인망이 높아 히데요시와 다른 다이묘 사이의 교섭을 맡았다. 히데요시보다 먼저 죽어 여러 장수들이 그 죽음을 애석해했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    757: (
        "히데요시의 둘째 아들. 세키가하라 전투 뒤 셋쓰·가와치·이즈미 65만 석의 일개 다이묘로 전락했다. 오사카 전투에서는 어머니 요도도노 등의 과보호를 받아 한 번도 출진하지 못한 채 자결했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    758: (
        "아라키 가신. 주군 무라시게의 소성을 지냈다. 주가 몰락 뒤 도요토미 히데요시를 섬겼고, 뒤에 기노시타 성을 하사받아 이나바 와카사 2만 석을 받았다. 세키가하라 전투에서는 서군에 속했으며 전후 자결했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    759: (
        "도요토미 가신. 이에사다의 장남. 와카사 오바마성주. 세키가하라 전투에서 동군에 속해 후시미성을 지켰으나 임무 포기죄로 개역되어 교토에 은거했다. 근세 와카의 시조라 불린다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    760: (
        "류조지 가신. 류조지 사천왕의 한 사람으로 일컬어진다. 오키타나와테 전투에서 주군 다카노부의 전사 소식을 듣자 나베시마 나오시게를 빠져나가게 한 뒤 적진으로 돌입했다. 생사는 여러 설이 있어 분명하지 않다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    761: (
        "도요토미 가신. 사다미쓰의 아들이라고 한다. 주군 히데요리의 유형제로서 소성을 지냈다. 도쿠가와 가문과 화친할 때는 도요토미 가문의 사자를 맡았다. 오사카 여름 전투에서 이이 나오타카군과 싸우다 전사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    762: (
        "도요토미 가신. 히타치노스케라 칭했다. 시즈가타케 전투 등에 종군해 에치젠 후추 10만 석을 다스렸다. 데와의 검지 봉행 등을 맡았다. 뒤에 도요토미 히데쓰구 사건에 연좌되어 자결을 강요받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    763: (
        "가토 기요마사 가신. 가토 십육장의 한 사람. 처음에는 롯카쿠 요시카타에게 속해 ‘겁쟁이 마타조’라는 별명이 있었으나 하치만신의 가호로 무적의 용사가 되었다. 기요마사의 명으로 오사카 전투에서 도요토미 편에 섰다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    764: (
        "오스미 기모쓰키 가문의 서류. 가네모리의 아버지다. 본가가 시마즈 가문에 맞서는 가운데 시마즈 다다요시와 내통해 가지키성주가 되었다. 뒤에 다다요시·다카히사와 대립했으나 패해 항복하고 다시 신하가 되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    765: (
        "오스미의 센고쿠 다이묘. 다카야마성주. 가네쓰구의 아들이다. 형 가네스케가 추방된 뒤 가독을 이었으나 시마즈군의 공격에 패해 영지를 내주고 항복했다. 세키가하라 전투에서 전사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    766: (
        "시마즈 가신. 기모쓰키 가문의 서류. 아버지 가네히로에게서 가지키성주 자리를 이었다. 시마즈 다카히사·요시히사의 가로를 지냈다. 가모 가문과 이토 가문을 공격하는 전투에서 특히 군공을 세웠다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    767: (
        "오스미의 센고쿠 다이묘. 다카야마성주. 기모쓰키 가문 최대의 판도를 구축했다. 시마즈 다다요시의 딸과 혼인했으나 뒤에 다다요시의 아들 다카히사와 대립했다. 거성이 시마즈군에게 빼앗겼다는 소식을 듣고 자결했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    770: (
        "오스미의 센고쿠 다이묘. 다카야마성주. 가네쓰구의 아들이다. 형 요시가네가 죽은 뒤 가독을 이었다. 이토 가문 등과 손잡고 시마즈 가문에 맞섰으나 어머니인 시마즈 다다요시의 딸과 가신들에게 추방당했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    771: (
        "오스미의 센고쿠 다이묘. 다카야마성주. 가네쓰구의 아들이다. 이토 가문과 손잡고 휴가 오비성을 공격해 성주 시마즈 다다치카를 쫓아냈다. 또한 이지치 시게오키를 도우며 평생 시마즈 가문과 항쟁했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    772: (
        "아시카가 가신. 주군 요시테루의 근습을 지냈다. 요시테루 사후에는 오미로 달아난 그의 동생 요시아키를 위해 분주히 뛰었다. 요시아키가 쇼군이 된 뒤 오다 노부나가와 대립해 조헤이지에 은거했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    773: (
        "오미 북부 절반의 수호. 다카키요의 장남. 아버지가 양자 다카요시에게 가독을 물려주려 하자 아자이 료세이 등의 옹립을 받아 다카키요와 다카요시를 쫓아냈다. 가독을 이었으나 실권은 료세이에게 빼앗겼다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    774: (
        "도요토미 가신. 다카요시의 아들. 아내와 여동생의 인연으로 도요토미 히데요시를 섬겨 오미 오쓰 6만 석을 다스렸다. 세키가하라 전투에서 동군에 속해 거성에 농성하며 서군 일부를 오쓰에 발이 묶이게 했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    775: (
        "도요토미 가신. 다카요시의 둘째 아들. 시나노 이이다 10만 석을 다스리며 조카마치 정비에 힘썼다. 세키가하라 전투에서 동군에 속했고, 전후 고야산으로 달아난 형에게 도쿠가와 가문에 출사하라고 설득했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    776: (
        "다카쓰구의 아들. 오사카 겨울 전투의 화의는 이를 중재한 의모 하쓰의 인연으로 다다타카의 진영에서 맺어졌다. 도쿠가와 히데타다의 딸을 아내로 맞고 모리 가문을 견제할 목적으로 이즈모·오키를 받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    777: (
        "무라카미 가신. 주가를 배반한 가신을 토벌하고 사나다 유키타카와 싸우는 등 주가의 세력 유지를 위해 힘썼다. 주군 요시키요가 시나노를 떠날 때 따랐고, 뒤에 요시키요의 아들 구니키요의 교육을 맡았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    778: (
        "우에스기 가신. 아시나 사천왕 히라타 기요노리의 아들. 인질로 우에스기 가문에 들어가 우에스기 가게카쓰에게 재능을 인정받아 측근이 되었다. 가게카쓰와 사다카쓰의 두터운 신임을 받아 요네자와 봉행에 임명되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    779: (
        "미카와 기라 가문 제13대 당주. 요시타카의 아들이다. 형 요시사토가 일찍 죽자 가독을 이었다. 뒤에 이마가와 가문에 패해 스루가 후추로 끌려갔다. 마쓰다이라 모토야스의 성인식 때는 이발을 맡았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    780: (
        "미카와 기라 가문 제11대 당주. 요시모토의 아들. 도토미 하마마쓰 장원까지 세력을 넓히고 오코치 사다쓰나를 대관으로 파견했으나 이마가와 가문의 침공으로 사다쓰나가 전사해 하마마쓰 장원을 잃었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    781: (
        "조소카베 가신. 지카사다의 적장자. 종가의 가독 계승 때 넷째 아들 모리치카를 옹립하려는 백부 모토치카를 간했으나, 대립 세력인 히사타케 지카나오의 참소로 모토치카에게 자결을 강요받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    782: (
        "조소카베 구니치카의 둘째 아들. 강인하고 지략이 풍부한 무장으로 형 모토치카의 오른팔이 되어 도사 통일에 공헌했다. 도사 이치조 가문이 멸망한 뒤 도사 나카무라성대가 되었으나 곧 병사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    783: (
        "이토 가신. 오니가성주. 시마즈군을 기습으로 격파하는 등 활약해 집사가 되었다. 주가의 분고 퇴거를 따르지 못해 구시마에 숨었으나 시마즈군에게 발각되어 동생과 함께 자결을 강요받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    784: (
        "오다 가신. 시마 해적 중 한 사람. 기즈가와구치 전투에서의 대패를 계기로 ‘철갑선’을 건조해 모리 수군을 격파했다. 그 공으로 다이묘로 출세해 ‘해적 다이묘’라는 별명을 얻었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    785: (
        "오다 가신. 어머니의 오빠인 구키 요시타카에게 길러져 구키 성을 칭했다. 처음 오다 노부타카를 섬겼고, 뒤에 가토 기요마사의 가신이 되었다가 출분했다. 그 뒤 구로다 가문, 고바야카와 가문, 도도 가문을 차례로 섬겼다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    786: (
        "시마 도바번주. 요시타카의 아들. 세키가하라 전투에서 동군에 속해 서군의 아버지와 싸웠다. 전후 자신의 논공행상과 맞바꾸어 아버지의 목숨을 살려 달라고 청했으나, 아버지는 이미 자결한 뒤였다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    787: (
        "소마 가신. 아키타네를 섬기며 나카무라성대를 지냈다. 나카무라성은 801년에 사카노우에노 다무라마로가 스가와라 사네타카에게 명해 쌓게 했다고 한다. 그 뒤 나카무라 가문이 대대로 거성으로 삼았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    788: (
        "아카마쓰 가신. 시카타성주. 구로다 간베이가 16세 때 그 재능을 알아보고 붉은 합자형 투구와 갑옷을 보냈으며, 뒤에 딸 미쓰를 시집보냈다. 덴쇼 연간에 오다군과의 농성전에서 세상을 떠났다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    789: (
        "구로다 간베이의 정실. 구로다 나가마사의 생모. 원호는 쇼후쿠인이다. 열다섯 살에 간베이에게 시집가 재주와 덕으로 남편을 뒷받침했다. 정토종을 깊이 신앙했다고 전해진다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    790: (
        "호조 가신. 구시마 마사시게의 아들. 아버지 사후 호조 우지쓰나에게 의지해 우지쓰나의 딸과 혼인하고 일문이 되었다. 가와고에 합전 등에서 활약했으며, 깃발 문양 때문에 ‘지키하치만’이라 불리며 두려움의 대상이 되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    791: (
        "호조 가신. 우지시게의 아들. 아버지 사후 다마나와성주가 되었다. 도요토미 히데요시의 오다와라 정벌 때 야마나카성을 지켰으나 함락되었고, 이후 거성에 농성하다 항복했다. 전후 도쿠가와 가문을 섬겼다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    792: (
        "호조 가신. 쓰나시게의 아들. 가문 제일의 맹장으로 두려움의 대상이던 아버지에 뒤지지 않는 무용을 지녔다. 다마나와성주를 지내며 우에스기 겐신의 간토 침공군을 격퇴하는 등 전공을 세웠다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    793: (
        "이마가와 가신. 다카텐진성주. 가문 제일의 맹장으로 일컬어졌다. 다케다 노부토라와의 이이다가와라 전투에서 패해 전사했다는 설과, 하나쿠라의 난 패배 뒤 도망치다 노부토라에게 죽었다는 설이 있다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    794: (
        "아시카가 가신. 당대 제일의 서예가. 구스노키 마사시게의 후예를 자처했다. 주군 요시테루가 죽자 마쓰나가 히사히데를 섬겼다. 뒤에 오다 노부나가와 도요토미 히데요시의 우필을 차례로 지냈다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    795: (
        "모리 가신. 시지 히로요시의 둘째 아들. 깃카와 모토하루를 보좌하여 산인 방면을 경략했다. 주군 모토나리 사후 사인중의 한 사람이 되어 당주 데루모토를 보좌하고 주가의 국정에 참여했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    796: (
        "오미의 호족. 하루쓰나의 아들. 오다 노부나가가 에치젠에서 철수할 때 길안내를 맡고 이후 오다 가문에 속했다. 혼노지의 변 뒤 도요토미 히데요시를 섬겼으며 세키가하라 전투에서는 동군으로 돌아섰다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    797: (
        "오미의 호족. 다네쓰나의 적장자. 구나이쇼유라 칭했다. 처음에는 사다쓰나라 했으나 쇼군 아시카가 요시하루의 편휘를 받아 하루쓰나로 개명했다. 다카시마군에서 다카시마 엣추노카미와 싸우다 전사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    798: (
        "도쿠가와 가신. 모토쓰나의 장남. 신분은 하타모토였으나 오미 겐지의 명문 출신이어서 교대기합에 속해 다이묘와 같은 대우를 받았다. 간분 대지진으로 죽었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    799: (
        "오미의 호족. 미요시 모토나가에게 교토에서 쫓겨난 쇼군 아시카가 요시하루를 거관에 숨겨 주었다. 그 공으로 신지칠인중의 한 사람이 되었다. 이후에도 여러 차례 아시카가 쇼군가를 숨겨 주었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    801: (
        "모리 가신. 고리야마 전투에서 적장 34명을 쓰러뜨린 용장. 뒤에 오봉행의 한 사람이 되었다. 주군 다카모토의 대리로 교토에 갔을 때 쇼군 아시카가 요시테루에게 ‘창의 방울’을 하사받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    802: (
        "이마가와 가신. 구노성주. 주가가 멸망하기 직전 도쿠가와 가신 고리키 기요나가의 중개로 도쿠가와 이에야스에게 속했다. 이에야스가 간토에 입국할 때 사쿠라성주가 되었고, 뒤에 구노성으로 돌아왔다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    803: (
        "난부 가신. 구노헤 노부나카의 아들. 처음에는 고스이지성주 시바 아키자네의 사위가 되었으나, 뒤에 시바 가문을 출분해 시바 가문 토벌군의 선봉을 맡았다. 사촌에게 베여 죽었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    804: (
        "난부 가신. 노부나카의 아들. 난부 하루마사의 둘째 딸과 혼인해 후계자 후보가 되었다. 주가에 반기를 든 형 마사자네와 함께 구노헤성에 농성해 도요토미군과 싸웠으나 패해 참수되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    805: (
        "난부 가신. 노부자네의 장남. 구노헤성주. 우쿄라 칭했다. 구노헤 가문은 난부 가문의 서류로, 난부 가문의 시조 미쓰유키의 여섯째 아들 난부 유키쓰라를 조상으로 한다고 전해진다. 하치노헤 노부나가의 딸과 혼인했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    806: (
        "난부 가신. 노부나카의 아들. 난부 하루마사 사후 동생 사네치카를 후계자로 세우려 했으나 실패해 반란을 일으켰다. 난부 노부나오의 요청으로 출진한 도요토미군과 맞서 선전했으나 패해 참수되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    807: (
        "도사 이치조 가신. 구시야마성주. 다카오카군 구보카와향을 본거지로 삼아 야마노우치에서 구보카와로 성을 바꾸었다. 뒤에 조소카베 모토치카에게 속했다. 히사타케 지카나오를 따라 남부 이요 지방을 공략하다 전사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    808: (
        "가가의 호족. 야스키치성주. 오이노스케라 칭했다. 처음 야스키치 이에나가를 섬겼으나 1550년 이에나가에게 야스키치성을 물려받아 성주가 되었다. 가가 잇코잇키군의 두령을 지냈다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    809: (
        "모리 가신. 노부나오의 손자. 각지의 전투에 종군해 활약했다. 구로다 요시타카의 영향으로 기리시탄이 되었다. 뒤에 주군 데루모토의 개종 명령을 거부해 일족 전원이 사형을 받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    810: (
        "아키 다케다 가신. 뒤에 주가와 대립해 모리 가문에 속했다. 딸이 모토나리의 둘째 아들 깃카와 모토하루에게 시집간 뒤에는 일문중으로 중용되어 깃카와군의 선봉을 맡아 각지에서 분전했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    811: (
        "쇼니 가신. 히젠 미쓰세성주. ‘북산을 베고 남해에 발을 담근다’는 꿈을 사들여 무운이 따랐다고 한다. 류조지 가신 오다 마사미쓰를 토벌하는 등 평생 류조지 가문에 맞섰다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    812: (
        "쇼니 가신. 가쓰토시의 적장자. 아버지가 은거하면서 가독을 이었다. 아버지 사후 류조지 가문과 화친해 그 가신이 되었다. 뒤에 오가와 노부토시(나베시마 나오시게의 동생)의 아들 이에요시를 양자로 삼았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    813: (
        "기쿠치 가신. 히고 나가노성주. 주가 몰락 후 류조지 가문에 속했다. 도요토미 히데요시의 규슈 정벌군에 항복했으나 사사 나리마사의 검지에 저항해 히고 국인잇키를 일으켰고, 패해 살해되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    814: (
        "벳쇼 가신. 미키 전투 때 미키성에 농성했다. 패색이 짙어지자 적군에 섞여 하시바 히데요시의 진영에 잠입했다. 히데요시에게 칼을 겨누었으나 제압당해 전사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    815: (
        "도사의 호족. 도쿠젠성주. 처음 조소카베 구니치카와 싸웠으나 뒤에 가신이 되어 각지 전투에서 활약했다. 용장이었지만 가난하여 정월 떡을 찧지 못했다는 이야기가 전한다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    816: (
        "구로다 가신. 구로다 팔호의 한 사람. 이름은 도시야스. 간베이를 섬긴 심복 가신이었다. 세키가하라 전투 때에는 의동생 모리 다헤에와 함께 간베이를 따라 분고의 오토모군과 싸웠다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    817: (
        "구로다 가문의 수석 가로. 도시야스의 아들. 이름은 도시야키라다. 시대를 거스르는 군비 확장을 한 주군 다다유키와 대립했다. 막부에 다다유키의 모반을 고발해 구로다 소동을 일으켰으나 소송에서 패해 유배되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    818: (
        "구루시마 미치후사의 손자. 그의 대에 성을 구루시마로 고쳤다. 오사카성과 에도성 공사에 참여하는 한편 가신단의 인재를 쇄신하고 오사카에 구라야시키를 설치해 재정 건전화에 성공했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    819: (
        "도요토미 가신. 미치야스의 넷째 아들. 처음 고노 가문에 속했다. 주군 히데요시의 시코쿠 정벌 때 형 도쿠이 미치토시와 함께 선봉을 맡았다. 조선 출병에는 수군을 이끌고 종군했으며 전사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    820: (
        "사타케 가신. 와다 아키타메를 주군 요시시게에게 참소해 추방하고 요시시게의 측근이 되었다. 세키가하라 전투 때는 우에스기 가문에 속했다. 주가 전봉 후 미토성 탈환을 꾀했으나 패해 살해되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    821: (
        "아키 가신. 아버지 에치젠은 주가 멸망 때 주군 구니토라의 부인을 친정인 도사 이치조 가문에 데려다준 뒤 구니토라의 무덤 앞에서 순사했다. 그는 조소카베 가문을 섬기다 나카토미가와 전투에서 전사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    822: (
        "오사키 가신. 쓰루다테성주. 구로카와 가문은 오사키 가문의 서류로, 오에이 연간부터 다테 가문에 속했다. 1588년 다테 가문이 오사키 영지에 침입했을 때 오사키 가문 편에 서서 다테군을 격파했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    823: (
        "우에스기 가신. 간바라군 오쿠야마쇼 호조(구로카와)를 영유했다. 가미조 사다노리의 난 때 처음에는 나가오 다메카게에게 속했다가 뒤에 가미조 측으로 돌아섰다. 난 뒤에 귀참해 군사불입의 특권을 인정받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    824: (
        "오노데라 가신. 구로사와성주. 아리야토게 전투 등에서 활약했다. 주가 개역 후 사타케 가문을 섬겨 잇키 진압과 새 논 개발에 힘썼다. 오사카 전투에서는 부대장으로 종군해 활약했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    825: (
        "구로다 팔호의 한 사람. 아버지가 아라키 무라시게에게 붙잡힌 구로다 간베이를 구했다. 세키가하라 전투에서 이시다 미쓰나리의 중신을 죽였고, 뒤에 나가마사의 명으로 『오사카 여름 전투도 병풍』도 제작했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    826: (
        "도요토미 가신. 주군 히데요시의 참모를 맡아 천하 통일에 크게 공헌했다. 그러나 뛰어난 전략적 수완을 두려워한 탓에 녹고는 부젠 나카쓰 12만 석으로 억제되었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    827: (
        "우에스기 가신. 구로타키성주. 주군 하루카게에게 모반을 일으켰으나 패해 살려 달라고 탄원하여 용서받았다. 그러나 뒤에 다시 반역해 에치고 수호 우에스기 사다자네의 명으로 자결을 강요받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    828: (
        "하리마의 호족. 비젠 후쿠오카에서 하리마 히메지로 이주했다. ‘레이주고’라 이름 붙인 안약을 팔아 재력을 모으고 아들 모토타카를 고데라 가문에 출사시키는 등 구로다 가문의 기반을 만들었다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    829: (
        "고데라 가신. 히메지성주. 하리마의 호족 가구야마 시게미치를 토벌한 공으로 주군 마사모토의 양녀와 혼인하고 가로에 취임했다. 뒤에 ‘고데라’ 성과 ‘모토’ 한 글자를 하사받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    830: (
        "나가마사의 적장자. 나가마사는 다다유키의 역량에 의문을 품어 폐적을 꾀했다는 말이 있다. 뒤에 가로 구리야마 다이젠과 대립해 구로다 소동을 일으켰으나 개역은 면했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    831: (
        "도요토미 가신. 간베이 요시타카의 적장자. 규슈 정벌 등에서 활약했다. 세키가하라 전투에서는 동군에 속해 전후 지쿠젠 후쿠오카 52만 석을 다스렸다. 이후 도쿠가와 막부에 공손히 복종하는 태도를 지켰다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    832: (
        "조소카베 가신. 도사 나카무라성대를 지냈다. 헤쓰기가와 전투와 우라토 잇키 진압 등에서 활약했다. 주가가 개역된 뒤에는 도도 가문에 속했다. 오사카 여름 전투 때 옛 주군 모리치카와 싸우다 전사했다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    833: (
        "도요토미 가신. 조부 시게하루에게서 가독을 이었다. 세키가하라 전투가 일어나자 서군에 붙은 구마노 수군 호리노우치 우지요시를 공격해 성을 빼앗고 동군에 가세했다. 야마토에 새 영지를 더 받았다.",
        "coordinate_semantic_omission_or_mistranslation",
    ),
    893: (
        "도요토미 가신. 유키나가의 동생. 기독교에 귀의했다. 세키가하라 전투에서는 유키나가의 거성인 히고 우토성을 수비하며 가토 기요마사군과 싸웠으나 서군의 패전 소식을 듣고 성문을 열고 자결했다.",
        "self_harm_terminology_correction",
    ),
    1146: (
        "사나다 가신. 나구루미성대. 호조 가신 이노마타 구니노리의 기습을 받아 패해 자결했다. 이 사건은 사전 금령에 반한다 하여 도요토미 히데요시에게 오다와라 정벌의 구실을 주었다.",
        "self_harm_terminology_correction",
    ),
    1199: (
        "데와의 호족. 요시마스의 아들. 형 요시우지의 사후 가독을 이었다. 우에스기 가신 혼조 시게나가의 차남을 양자로 맞아 우에스기 가문과의 관계 강화를 꾀했으나, 모가미 요시아키에게 공격받아 자결했다.",
        "self_harm_terminology_correction",
    ),
    1200: (
        "데와의 호족. 오우라성주. 요시마스의 아들. 전투에만 몰두해 영지 정치를 소홀히 하여 영민에게 ‘악야가타’라며 미움받았다. 모가미 요시아키와 내통한 가신 마에모리 구란도에게 모반당해 자결했다.",
        "self_harm_terminology_correction",
    ),
    1333: (
        "아가타 쓰치모치 가문 16대 당주. 지카스케의 아들. 마쓰오성주. 역대 당주 가운데서도 보기 드물게 문무양도에 뛰어난 명장으로 평가되었다. 시마즈 가문과 손잡았으나 오토모군의 공격에 패해 자결했다.",
        "self_harm_terminology_correction",
    ),
    1341: (
        "도요토미 가신. 쓰쓰이 준히로의 차남. 숙부 준케이의 양자가 되었다. 사촌 사다쓰구의 개역 후 가독을 이었다. 오사카 여름 전투에서 오사카성 측에게 거성을 함락당해 도망쳤고, 뒤에 자결했다.",
        "self_harm_terminology_correction",
    ),
    1645: (
        "도요토미 가신. 근습조두로서 고마키 나가쿠테 전투와 오다와라 정벌에 종군했다. 히데요시 사후에는 히데요리를 섬겨 칠수조두의 한 사람이 되었다. 여름 전투 때 히데요리를 따라 순절해 자결했다.",
        "self_harm_terminology_correction",
    ),
    1838: (
        "도요토미 가신. 하치스카 마사카쓰와 함께 스노마타 일야성 축성에 협력했고 이후 히데요시의 오른팔로 활약해 다지마 이즈시 5만 석을 영유했다. 후에 도요토미 히데쓰구 사건에 연좌되어 자결했다.",
        "self_harm_terminology_correction",
    ),
    1878: (
        "도쿠가와 이에야스의 장남. 오다 노부나가의 딸 고토쿠를 아내로 맞았다. 강용하고 영매한 인물됨으로 장래가 촉망받았으나, 훗날 노부나가로부터 다케다 가문과 내통했다는 의심을 받아 아버지의 명으로 자결했다.",
        "self_harm_terminology_correction",
    ),
    2019: (
        "도요토미 가신. 세키가하라 전투에서 서군에 속해 도사에 유배되었으나 탈주해 오사카성에 들어갔다. 사나다 유키무라에 버금가는 인망을 얻어 오사카 여름 전투에서 활약했으나, 성이 함락되자 자결했다.",
        "self_harm_terminology_correction",
    ),
}


MSGIRE_FIXES: dict[int, tuple[str, str]] = {
    17: (
        "중국제 가지 모양 차통. 천하삼가지 가운데 하나다. 이세 국사 기타바타케 가문이 소장해 이런 이름이 붙었다. 뒤에 다인 쇼카도 쇼조가 손에 넣어 야와타 명물의 으뜸으로 아꼈다.",
        "han_made_terminology_correction",
    ),
    20: (
        "중국제 어깨가 도드라진 차통. 천하삼견충 가운데 하나다. 하카타 상인 시마이 소시쓰에게서 아키즈키 다네자네에게 전해졌다. 규슈 정벌 때 항복의 표시로 도요토미 히데요시에게 바쳐진 뒤 행방이 묘연해졌다.",
        "han_made_terminology_correction",
    ),
    22: (
        "중국제 어깨가 도드라진 차통. 표면 전체에 균열이 난 아름다운 차통이다. 사카이의 거상 스미요시야 소무가 소장해 이런 이름이 붙었다. 뒤에 사타케 가문을 거쳐 도쿠가와 쇼군가에 전해졌다.",
        "han_made_terminology_correction",
    ),
    23: (
        "중국제 어깨가 도드라진 차통. 작고 밤색과 팥색을 띠는 운치 높은 일품이다. 다케나카 한베이가 도요토미 히데요시에게 하사받아 이런 이름이 붙었다고 한다.",
        "han_made_terminology_correction",
    ),
    24: (
        "중국제 차통. 감빛 바탕에 떠오른 검은 무늬가 흐린 구름처럼 보여 아시카가 요시마사가 이름을 붙였다. 도요토미 히데요시와 교고쿠 가문 등을 거쳐 도쿠가와 쇼군가가 소장했다.",
        "han_made_terminology_correction",
    ),
    37: (
        "미요시 마사나가가 다케다 노부토라에게 선물한 칼. 뒤에 이마가와 요시모토의 패도가 되어 요시모토 사몬지라고도 불렸다. 오케하자마 전투에서 오다 노부나가가 얻어 자신의 패도로 삼았다.",
        "natural_weapon_term_correction",
    ),
    79: (
        "알을 움직여 계산하는 간편한 계산기. 기원에는 여러 설이 있다. 일본에는 무로마치 시대 말기에 전해졌으며 마에다 도시이에가 정산할 때 애용했다고 한다.",
        "financial_term_correction",
    ),
    104: (
        "요시다 겐코가 쓴 수필집. 가마쿠라 시대 말기에 성립한 것으로 여겨진다. 본래 귀족을 위한 교양 입문서였으나 후대에는 승려와 도시민 등 폭넓은 계층이 즐겨 읽었다.",
        "social_class_term_correction",
    ),
    111: (
        "중국 후난성에서 소수와 상수가 합쳐져 둥팅호로 흘러드는 주변 풍경 가운데 여덟 곳을 그림 소재로 삼은 것. 무계와 옥간 등 많은 화가의 그림이 있어 다인들에게 귀하게 여겨졌다.",
        "art_subject_term_correction",
    ),
}


FIXES_BY_RESOURCE: dict[str, dict[int, tuple[str, str]]] = {
    "msgbre": MSGBRE_FIXES,
    "msgire": MSGIRE_FIXES,
}


# The private findings deliberately retain enough before/after evidence for a
# later freeze step to reject stale coordinates.  The wording below is kept
# generic where a contiguous biography block has the same failure mode; the
# actual coordinate, current hash, and proposed text remain row-specific.
ISSUE_RATIONALES: dict[str, str] = {
    "coordinate_semantic_omission_or_mistranslation": (
        "Coordinate-specific comparison with pristine PC Japanese found lost or "
        "altered source facts (clauses, actor, relationship, event, or outcome); "
        "the proposal restores the source meaning."
    ),
    "self_harm_terminology_correction": (
        "The pristine PC Japanese uses self-inflicted death terminology; the "
        "current Korean wording \"self-harm\" is inaccurate here, so the "
        "proposal uses the death-specific Korean term."
    ),
    "office_title_and_wording_correction": (
        "The current Korean office title/wording does not faithfully convey the "
        "pristine PC Japanese coordinate; the proposal restores the source title "
        "and meaning."
    ),
    "source_outcome_correction": (
        "The current Korean changes the source outcome by adding death; the "
        "pristine PC Japanese states only that the person fell ill."
    ),
    "han_made_terminology_correction": (
        "The source term denotes an item made in China, not a Han-dynasty style; "
        "the proposal uses the accurate Korean sense."
    ),
    "natural_weapon_term_correction": (
        "The current Korean weapon term is not the source meaning; the proposal "
        "restores the coordinate-specific weapon description."
    ),
    "financial_term_correction": (
        "The current Korean financial term is inaccurate for the pristine PC "
        "Japanese coordinate; the proposal restores the source sense."
    ),
    "social_class_term_correction": (
        "The current Korean social-class term is inaccurate for the pristine PC "
        "Japanese coordinate; the proposal restores the source sense."
    ),
    "art_subject_term_correction": (
        "The current Korean art term is inaccurate for the pristine PC Japanese "
        "coordinate; the proposal restores the source sense."
    ),
}

RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


def load(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def format_profile(text: str) -> dict[str, object]:
    return {
        "runtime": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "esc": ESC_RE.findall(text),
        "linebreaks": re.findall(r"\r\n|\n|\r", text),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "private_use": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "fullwidth_percent_count": text.count("％"),
    }


def format_validation(source: str, proposed: str) -> dict[str, object]:
    """Return explicit, machine-readable evidence for every format guard."""
    source_profile = format_profile(source)
    proposed_profile = format_profile(proposed)
    checks = {
        "escape_tags_match": source_profile["esc"] == proposed_profile["esc"],
        "runtime_tokens_match": source_profile["runtime"] == proposed_profile["runtime"],
        "printf_tokens_match": source_profile["printf"] == proposed_profile["printf"],
        "linebreaks_match": source_profile["linebreaks"] == proposed_profile["linebreaks"],
        "leading_whitespace_match": source_profile["leading_whitespace"] == proposed_profile["leading_whitespace"],
        "trailing_whitespace_match": source_profile["trailing_whitespace"] == proposed_profile["trailing_whitespace"],
        "private_use_match": source_profile["private_use"] == proposed_profile["private_use"],
        "fullwidth_percent_count_match": source_profile["fullwidth_percent_count"] == proposed_profile["fullwidth_percent_count"],
        "hangul_present": bool(HANGUL_RE.search(proposed)),
        "no_unintended_question_mark": "?" not in proposed,
        "no_replacement_glyph": "\ufffd" not in proposed,
        "no_japanese_or_cjk_residue": not bool(KANA_OR_HAN_RE.search(proposed)),
    }
    return {
        "source_profile": source_profile,
        "proposed_profile": proposed_profile,
        "checks": checks,
        "all_required_checks_pass": all(checks.values()),
    }


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def resource_rows(resource: str) -> tuple[list[str], list[str]]:
    name = resource + ".bin"
    jp_path = PRISTINE_ROOT / "MSG_PK" / "JP" / name
    ko_path = STEAM / "MSG_PK" / "JP" / name
    jp = load(jp_path)
    ko = load(ko_path)
    if len(jp) != len(ko):
        raise SystemExit(f"{resource}: pristine JP/live KO coordinate count mismatch")
    return jp, ko


def make_rows(resource: str, fixes: dict[int, tuple[str, str]]) -> list[dict[str, object]]:
    jp, current_ko = resource_rows(resource)
    rows: list[dict[str, object]] = []
    for identifier, (proposed, issue) in sorted(fixes.items()):
        if not 0 <= identifier < len(jp):
            raise SystemExit(f"{resource}:{identifier}: coordinate outside table")
        current = current_ko[identifier]
        validation = format_validation(jp[identifier], proposed)
        source_profile = validation["source_profile"]
        if not validation["all_required_checks_pass"]:
            raise SystemExit(f"{resource}:{identifier}: source format profile mismatch")
        if KANA_OR_HAN_RE.search(proposed):
            raise SystemExit(f"{resource}:{identifier}: Japanese/CJK residue in Korean proposal")
        if not HANGUL_RE.search(proposed):
            raise SystemExit(f"{resource}:{identifier}: Korean proposal has no Hangul")
        if "?" in proposed or "\ufffd" in proposed:
            raise SystemExit(f"{resource}:{identifier}: unintended question/replacement glyph")
        if proposed == current:
            raise SystemExit(f"{resource}:{identifier}: proposal is not an effective correction")
        rationale = ISSUE_RATIONALES.get(issue)
        if rationale is None:
            raise SystemExit(f"{resource}:{identifier}: rationale is absent for {issue}")
        rows.append(
            {
                "id": identifier,
                # ``ko`` remains the live current value for the existing
                # freeze builder; ``proposed_ko`` is the replacement.
                "ko": current,
                "current_ko": current,
                "proposed_ko": proposed,
                "current_hash": text_hash(current),
                "issue": issue,
                "issue_type": issue,
                "rationale": rationale,
                "format": source_profile,
                "format_validation": validation,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", choices=tuple(FIXES_BY_RESOURCE), action="append")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()

    selected = args.resource or list(FIXES_BY_RESOURCE)
    output_root = args.output_root.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if output_root == tmp_root or tmp_root not in output_root.parents:
        raise SystemExit("output root must remain below tmp")

    summary: dict[str, object] = {
        "resources": {},
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    for resource in selected:
        rows = make_rows(resource, FIXES_BY_RESOURCE[resource])
        output = output_root / f"{resource}_findings.v1.jsonl"
        atomic_write(
            output,
            "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        )
        if any(char for char in output.read_text(encoding="ascii")):
            # Empty files are valid zero-row JSONL.  Non-empty files must be
            # ASCII too, otherwise PowerShell code-page corruption is possible.
            output.read_text(encoding="ascii")
        summary["resources"][resource] = {
            "entry_count": len(rows),
            "output": str(output),
            "unique_ids": len({int(row["id"]) for row in rows}),
        }
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
