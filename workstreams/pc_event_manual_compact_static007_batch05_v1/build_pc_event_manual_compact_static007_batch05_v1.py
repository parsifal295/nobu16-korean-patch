#!/usr/bin/env python3
"""Build the private multi-scene Static Patch 007 manual_compact batch 05.

Only the on-disk batch04 candidate provides Korean build text. Direct PC
JP/EN/SC/TC resources are read-only semantic evidence. This batch reuses the
committed batch03 codec/audit engine with a separately pinned broad scope,
per-scene audit, and an exact multi-row diff. It has no Steam, Git, release,
or network path.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
MSGEV = "MSG_PK/JP/msgev.bin"

BATCH03_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_static007_batch03_v1"
    / "build_pc_event_manual_compact_static007_batch03_v1.py"
)
PREDECESSOR_WORKSTREAM = "pc_event_manual_compact_4000_5000_restore_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_PREDECESSOR_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "9F15BE13C0CFE09D82A9BAE616B57FCE8B4C92187624EB3686E2F850B504F146",
    "raw_size": 1_006_792,
    "sha256": "E95A773B7B6448542CF8236868CBEEE7BA49382DD0450DB75DB6CD66CF43FF60",
    "size": 1_010_766,
}
# The strict bulk predecessor is pinned above; candidate generation is now enabled.
PREPARATION_ONLY = False
# Deterministic output from the pinned 4000–5000 bulk strict predecessor.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "D49A221732551E6DA673657A577828640E438D02B23AF3B529130A2B9689CC7F",
    "raw_size": 1_007_432,
    "sha256": "8B7B9BF8F104C56F3EED0B3B5E1871E416466CD443020D6306135CCA56E7FE42",
    "size": 1_011_408,
}

SCENE_GROUPS: tuple[tuple[str, int, int], ...] = (
    ("gifu_naming_and_tenka_fubu", 3_287, 3_308),
    ("regional_ending_sequences", 3_309, 3_353),
    ("imperial_titles_choice", 3_354, 3_384),
    ("unification_aftermath_alt_histories", 3_385, 3_440),
    ("ashikaga_miyoshi_reconciliation", 3_441, 3_460),
    ("nobukatsu_second_rebellion", 3_461, 3_484),
    ("imagawa_hojo_ujitsuna", 3_485, 3_500),
)
SCENE_NAME = "multi_scene_3287_3500"
SCENE_IDS = tuple(range(3_287, 3_501))
CHANGED_IDS = (
    3_297,
    3_307,
    3_311,
    3_316,
    3_327,
    3_336,
    3_346,
    3_358,
    3_360,
    3_386,
    3_394,
    3_396,
    3_398,
    3_402,
    3_411,
    3_421,
    3_429,
    3_438,
    3_439,
    3_445,
    3_452,
    3_468,
    3_469,
    3_475,
    3_482,
    3_483,
    3_484,
    3_485,
    3_486,
    3_489,
    3_495,
    3_496,
    3_498,
)
RUNTIME_HOLD_IDS = (3_442, 3_443, 3_444, 3_448, 3_455, 3_456, 3_459, 3_499)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)
ENGINE_REVIEW_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in RUNTIME_HOLD_IDS)
ENGINE_RETAINED_IDS = tuple(entry_id for entry_id in ENGINE_REVIEW_IDS if entry_id not in CHANGED_IDS)
E = "\x1b"

TARGETS: Mapping[int, str] = {
    3_297: (
        f"주나라 {E}CA문왕{E}CZ은 {E}CC기산{E}CZ에서 천하를 정했고,\n"
        f"{E}CA공자{E}CZ는 {E}CC곡부{E}CZ에서 태어나 학문을 닦았습니다.\n"
        "반드시 좋은 땅이 될 것입니다……"
    ),
    3_307: (
        f"이름 유래에는 여러 설이 있으나, {E}CC이노쿠치{E}CZ 마을은\n"
        f"‘{E}CC기후{E}CZ’가 되고 {E}CC이나바야마성{E}CZ은\n"
        f"‘{E}CC기후성{E}CZ’으로 다시 지어졌다."
    ),
    3_311: (
        f"수도에서 멀리 떨어진 {E}CC오우{E}CZ에서는\n"
        "무로마치 막부 개창 이래 다이묘들의\n"
        "다툼과 전쟁이 끊이지 않았지만……"
    ),
    3_316: (
        "무로마치 막부 개창 이래 여러 세력의\n"
        f"이해관계가 얽혀, {E}CC간토{E}CZ에서는 늘\n"
        "전쟁이 벌어지는 것이 당연시됐으나……"
    ),
    3_327: (
        "하지만 세력 확대를 꾸준히 추진한\n"
        f"{E}CB[bus] 가문{E}CZ의 노력이 결실을 맺어,\n"
        f"마침내 {E}CC고신{E}CZ 지방은 통일을 맞았다."
    ),
    3_336: (
        f"오닌의 난으로 황폐해진 {E}CC교토{E}CZ를 포함한\n"
        f"{E}CC긴키{E}CZ 일대는 여러 다이묘가 막부 주도권을 놓고\n"
        "끊임없이 싸워 온 땅이었다."
    ),
    3_346: (
        "전국시대 내내 강력한 중심 다이묘가 없어\n"
        f"{E}CC긴키{E}CZ와 {E}CC주고쿠{E}CZ 다이묘들의 다툼에 휘말린\n"
        f"{E}CC시코쿠{E}CZ에는 강한 권력이 생기지 못했다……"
    ),
    3_358: (
        "주상께서 특별히 분부하셨소.\n"
        "귀공을 관백·정이대장군·태정대신 가운데\n"
        "하나에 임명하고자 하신답니다."
    ),
    3_360: (
        "모두 천하인에게 걸맞은 조정의 요직입니다.\n"
        "마음대로 고르라는 분부이니,\n"
        "어느 자리를 택하시겠습니까……?"
    ),
    3_386: (
        f"{E}CA[bu]{E}CZ 공은 천하의 평안을 드높이 외치고,\n"
        "전국에 소부지령을 선포했다. 이유를 불문하고,\n"
        "다이묘 사이의 사적인 영토 분쟁은 금지되었다."
    ),
    3_394: (
        "“창업은 쉽지만 수성은 어렵다.”\n"
        f"하루빨리 {E}CB[bus] 가문{E}CZ의 지배를 굳혀\n"
        "이 태평한 세상을 하루라도 더 오래 지켜야 한다……!"
    ),
    3_396: (
        f"이렇게 {E}CA[bu]{E}CZ 공은 관백에 취임해\n"
        f"{E}CC[cuh]{E}CZ에 정무청을 두고, 무가 관백이\n"
        "각지 다이묘를 다스릴 새 정권을 세웠다."
    ),
    3_398: (
        f"{E}CA[bu]{E}CZ의 천하통일 뒤, 조정은 {E}CB아시카가 가문{E}CZ을\n"
        "대신할 무가의 수장으로 그를 인정해 정이대장군에\n"
        "임명하고 막부 개설을 허가했다."
    ),
    3_402: (
        f"{E}CA[bu]{E}CZ의 위세는 {E}CB아시카가 본가{E}CZ를 넘어\n"
        "진정한 무가의 동량으로 인정받았고,\n"
        "정이대장군이 되어 무로마치 막부를 재흥했다."
    ),
    3_411: (
        "이질 세력을 허용하지 않는 강고한\n"
        "봉건적 지배는 200년 동안 이어져\n"
        f"{E}CA[bus]{E}CZ 시대라 불리는 세상을 만들었다."
    ),
    3_421: (
        "다시 각지에서 다이묘들이 다투는 시대가\n"
        f"찾아왔지만, 100년간 일본의 평화를 지킨\n"
        f"{E}CA[bus]{E}CZ 시대는 사람들의 기억에 오래 남았다."
    ),
    3_429: (
        f"잇키가 빈발하자 {E}CB[bis] 가문{E}CZ 등\n"
        f"유력 다이묘들은 {E}CA[bus]{E}CZ의 지배를 버리고\n"
        "동란을 오히려 자기 세력을 다지는 데 이용했다."
    ),
    3_438: (
        f"이 움직임에 조정은 당황했지만, {E}CA[bus]{E}CZ 정권은\n"
        "섭관과 대신 중심의 공가 사회와 거리를 두면서도\n"
        "조정 자체는 그대로 보존했다."
    ),
    3_439: (
        f"정치 권력은 {E}CB[bus] 가문{E}CZ이 맡고,\n"
        "의례적 권위는 조정이 맡는 특수한 이중 국가로\n"
        "안정되어, 그것이 상시 체제가 됐다."
    ),
    3_445: (
        f"{E}CB아시카가 가문{E}CZ 내부에서도 {E}CB미요시 세력{E}CZ을 원망한\n"
        f"{E}CA호소카와 하루모토{E}CZ 등이 화친에 계속 반대해,\n"
        f"{E}CC교토{E}CZ 귀환은 끝내 이루어지지 못했다."
    ),
    3_452: (
        f"반{E}CB미요시{E}CZ의 선봉이 된 {E}CA호소카와 하루모토{E}CZ 일파는\n"
        f"각지에서 {E}CB미요시 가문{E}CZ 거점을 집요하게 공격해,\n"
        f"새 {E}CB아시카가{E}CZ·{E}CB미요시{E}CZ 협력 체제를 흔들었다."
    ),
    3_468: (
        "급병으로 숨도 가쁘시고,\n"
        "내일조차 장담할 수 없는 상태라\n"
        f"마지막으로 {E}CA노부카쓰{E}CZ 님을 뵙고 싶답니다…"
    ),
    3_469: (
        "그 형이 그토록 앓다니, 믿기지 않는군……\n"
        "마지막에 그토록 미워한 나를 보고 싶다니,\n"
        "그래도 사람의 정은 남아 있었던가."
    ),
    3_475: (
        "뻔한 꾀병에 걸려들다니.\n"
        "순진하다고는 할 수 있어도 전국시대에는\n"
        "말 그대로 목숨을 잃게 만드는 약점이다……"
    ),
    3_482: (
        f"생모 {E}CA도타고젠{E}CZ이 비탄에 잠긴 것은 말할 것도 없다.\n"
        f"하지만 {E}CA노부카쓰{E}CZ의 죽음은 뜻밖에도\n"
        "가문 안에 거의 동요를 일으키지 않았다."
    ),
    3_483: (
        f"{E}CA노부카쓰{E}CZ의 모반이 두 번째였고,\n"
        f"이전부터 {E}CA노부나가{E}CZ의 지배가 깊이 뿌리내린 것이\n"
        "배경이었을지도 모른다."
    ),
    3_484: (
        f"어쨌든 {E}CA노부카쓰{E}CZ의 죽음은 {E}CB오다{E}CZ 가문을 결속시켜\n"
        f"{E}CC오와리{E}CZ 통일을 향한 {E}CA노부나가{E}CZ 중심 체제를\n"
        "더욱 굳건하게 만들었다."
    ),
    3_485: (
        f"{E}CB이마가와가{E}CZ의 군사였던 {E}CA호조소운{E}CZ({E}CA이세소즈이{E}CZ)은\n"
        f"{E}CC이즈{E}CZ와 {E}CC사가미{E}CZ를 차지해 독립하고, 적자 {E}CA우지쓰나{E}CZ는\n"
        f"{E}CC무사시{E}CZ·{E}CC시모사{E}CZ·{E}CC스루가{E}CZ로 진출했다."
    ),
    3_486: (
        f"그 {E}CC스루가{E}CZ에서 {E}CA우지쓰나{E}CZ에게 농락당한 이는,\n"
        "훗날 ‘가이도 제일의 무사’라 불린\n"
        f"{E}CB이마가와가{E}CZ 당주 {E}CA이마가와 요시모토{E}CZ였다."
    ),
    3_489: (
        "허허, 승려답지 않은 험한 말이군……\n"
        "하지만 스승이여, 나는 마음 깊은 곳에서\n"
        f"{E}CA우지쓰나{E}CZ와 다시 한번 싸우고 싶었소."
    ),
    3_495: (
        f"그럼 이제 {E}CA요시모토{E}CZ 님이 스승이 되어\n"
        f"{E}CA우지쓰나{E}CZ의 아들 {E}CA우지야스{E}CZ에게\n"
        "난세의 법도를 가르쳐 보시는 건 어떻습니까?"
    ),
    3_496: (
        "죽는 이가 남기고, 산 이가 이어받습니다……\n"
        "그 사람이 죽을 때면 이어받을 이가 나타나,\n"
        "그렇게 사람이 만들어져 가는 것입니다."
    ),
    3_498: (
        f"{E}CA이마가와 요시모토{E}CZ는 {E}CA우지쓰나{E}CZ의 죽음을 틈타\n"
        f"{E}CC스루가{E}CZ에 출병해 {E}CC간바라성{E}CZ 등 {E}CC스루가 동부{E}CZ를 점령했다.\n"
        "이를 ‘가토의 난’이라 한다……"
    ),
}
TARGET_LAYOUTS: Mapping[int, tuple[tuple[int, ...], tuple[int, ...]]] = {
    3_297: ((888, 984, 720), (555, 615, 450)),
    3_307: ((1_128, 672, 648), (705, 420, 405)),
    3_311: ((744, 816, 744), (465, 510, 465)),
    3_316: ((840, 720, 840), (525, 450, 525)),
    3_327: ((768, 768, 792), (480, 480, 495)),
    3_336: ((864, 1_056, 624), (540, 660, 390)),
    3_346: ((936, 912, 912), (585, 570, 570)),
    3_358: ((648, 912, 696), (405, 570, 435)),
    3_360: ((984, 648, 696), (615, 405, 435)),
    3_386: ((912, 1_056, 1_056), (570, 660, 660)),
    3_394: ((720, 792, 1_152), (450, 495, 720)),
    3_396: ((720, 816, 912), (450, 510, 570)),
    3_398: ((1_008, 1_128, 720), (630, 705, 450)),
    3_402: ((816, 816, 1_032), (510, 510, 645)),
    3_411: ((768, 744, 864), (480, 465, 540)),
    3_421: ((912, 912, 984), (570, 570, 615)),
    3_429: ((696, 888, 1_080), (435, 555, 675)),
    3_438: ((1_032, 1_104, 672), (645, 690, 420)),
    3_439: ((720, 1_056, 816), (450, 660, 510)),
    3_445: ((1_080, 1_008, 840), (675, 630, 525)),
    3_452: ((1_080, 1_056, 960), (675, 660, 600)),
    3_468: ((552, 720, 936), (345, 450, 585)),
    3_469: ((912, 960, 792), (570, 600, 495)),
    3_475: ((552, 912, 936), (345, 570, 585)),
    3_482: ((1_152, 792, 912), (720, 495, 570)),
    3_483: ((720, 1_080, 528), (450, 675, 330)),
    3_484: ((1_080, 936, 552), (675, 585, 345)),
    3_485: ((1_056, 1_152, 768), (660, 720, 480)),
    3_486: ((984, 768, 912), (615, 480, 570)),
    3_489: ((792, 912, 840), (495, 570, 525)),
    3_495: ((840, 672, 1_008), (525, 420, 630)),
    3_496: ((960, 984, 888), (600, 615, 555)),
    3_498: ((1_008, 1_224, 648), (630, 765, 405)),
}
RATIONALES: Mapping[int, str] = {
    3_297: "공자의 곡부 출생과 학문 수양이 빠졌던 문법 오류를 복원하고, 문왕·공자·길지의 세 의미 단위로 나눴다.",
    3_307: "명명 유래의 여러 설, 이노쿠치에서 기후로의 개칭, 이나바야마성의 기후성 재건을 보존했다.",
    3_311: "수도와의 거리, 무로마치 이래의 다이묘 분쟁, 전쟁 지속이라는 인과를 보존했다.",
    3_316: "여러 세력의 이해관계와 간토의 상시 전쟁이라는 원문 인과를 문장 단위로 복원했다.",
    3_327: "세력 확대 노력의 결실과 고신 지방 통일이라는 현재 의미를 유지했다.",
    3_336: "오닌의 난으로 황폐해진 교토를 포함한 긴키의 막부 주도권 분쟁을 보존했다.",
    3_346: "중심 다이묘 부재, 긴키·주고쿠 분쟁의 파급, 시코쿠 권력 부재를 모두 유지했다.",
    3_358: "관백·정이대장군·태정대신 중 하나를 제수한다는 칙명을 손대지 않고 재배치했다.",
    3_360: "천하인에 걸맞은 조정 요직을 자유롭게 고르게 한다는 제안을 보존했다.",
    3_386: "천하의 평안 선포, 소부지령, 이유를 불문한 사적 영토 분쟁 금지를 모두 보존했다.",
    3_394: "창업과 수성의 대비, 가문 지배 공고화, 태평 지속의 세 의미를 보존했다.",
    3_396: "관백 취임, 정무청 설치, 무가 관백 정권 수립의 순서를 보존했다.",
    3_398: "무가 수장 인정, 정이대장군 임명, 막부 개설 허가라는 원문 요소를 복원했다.",
    3_402: "아시카가 본가를 넘는 위세, 무가 동량 인정, 무로마치 재흥을 모두 보존했다.",
    3_411: "이질 세력을 허용하지 않는 봉건 지배와 200년 지속이라는 원문 의미를 보존했다.",
    3_421: "다이묘 난립의 재개와 백 년 평화의 기억이라는 대비를 보존했다.",
    3_429: "잇키 빈발, 유력 다이묘의 이탈, 동란을 자기 기반 강화에 이용한 인과를 보존했다.",
    3_438: "조정의 당황, 공가 사회와의 거리, 조정 자체 보존을 원문 순서대로 재배치했다.",
    3_439: "정치 권력과 의례 권위의 분담, 이중 국가의 안정·상시화를 보존했다.",
    3_445: "아시카가 내부의 미요시 원한, 하루모토 등의 반대, 교토 귀환 실패를 보존했다.",
    3_452: "하루모토 일파의 집요한 거점 공격과 아시카가·미요시 협력 체제의 동요를 보존했다.",
    3_468: "급병·위독 상태와 노부카쓰를 마지막으로 만나고 싶다는 요청을 보존했다.",
    3_469: "형의 위독함에 대한 놀람, 마지막 만남, 남은 인정의 추측을 보존했다.",
    3_475: "명백한 꾀병, 전국시대에서 순진함이 치명적이라는 평가를 보존했다.",
    3_482: "생모의 비탄과 노부카쓰 사망이 가문에 거의 동요를 일으키지 않은 대비를 보존했다.",
    3_483: "두 번째 모반과 이미 깊이 뿌리내린 노부나가 지배라는 배경을 보존했다.",
    3_484: "노부카쓰 사망 뒤 오다 가문의 결속과 오와리 통일 체제의 공고화를 보존했다.",
    3_485: "소운의 이즈·사가미 독립과 적자 우지쓰나의 세 지역 진출을 보존했다.",
    3_486: "스루가에서의 우지쓰나와 요시모토의 관계, 훗날의 칭호와 당주 지위를 보존했다.",
    3_489: "승려답지 않은 말이라는 반응과 우지쓰나와 다시 싸우고 싶었던 속마음을 보존했다.",
    3_495: "요시모토가 우지야스에게 난세의 법도를 가르치라는 권유를 보존했다.",
    3_496: "죽는 이의 유산, 산 이의 계승, 계승자를 통해 사람이 형성된다는 비유를 보존했다.",
    3_498: "우지쓰나 사망을 틈탄 출병, 스루가 동부 점령, 가토의 난 명칭을 보존했다.",
}
CURRENT_QUALITY_PRESERVED: Mapping[int, tuple[str, ...]] = {
    3_297: ("주나라", "문왕", "기산", "공자", "곡부", "좋은 땅"),
    3_307: ("이노쿠치", "기후", "이나바야마성", "기후성"),
    3_311: ("무로마치 막부", "오우", "다이묘", "전쟁"),
    3_316: ("무로마치 막부", "간토", "이해관계", "전쟁"),
    3_327: ("세력 확대", "가문", "고신", "통일"),
    3_336: ("오닌의 난", "교토", "긴키", "막부 주도권"),
    3_346: ("긴키", "주고쿠", "시코쿠", "강한 권력"),
    3_358: ("관백", "정이대장군", "태정대신"),
    3_360: ("천하인", "조정 요직", "택하시겠습니까"),
    3_386: ("천하태평", "소부지", "영토 다툼"),
    3_394: ("창업", "수성", "가문 지배", "태평성대"),
    3_396: ("관백", "정무청", "무가 관백", "새 정권"),
    3_398: ("천하통일", "아시카가 가문", "막부"),
    3_402: ("아시카가 본가", "무가의 동량", "무로마치 재흥"),
    3_411: ("이질 세력", "봉건 지배", "200년", "시대"),
    3_421: ("다이묘 난립", "100년", "일본 평화", "시대"),
    3_429: ("잇키", "유력 다이묘", "동란", "기반"),
    3_438: ("조정", "섭관·대신", "공가", "보존"),
    3_439: ("정치", "의례 권위", "이중국가", "상시 체제"),
    3_445: ("아시카가 가문", "미요시 세력", "하루모토", "교토 귀환"),
    3_452: ("미요시", "하루모토", "아시카가", "연합"),
    3_468: ("급병", "내일", "노부카쓰", "마지막"),
    3_469: ("형", "마지막", "미워한 나", "정"),
    3_475: ("꾀병", "전국시대", "목숨"),
    3_482: ("도타고젠", "노부카쓰", "가문", "동요"),
    3_483: ("노부카쓰", "모반", "노부나가", "지배"),
    3_484: ("노부카쓰", "오다", "오와리", "노부나가"),
    3_485: ("이마가와가", "호조소운", "이세소즈이", "우지쓰나", "이즈", "사가미", "무사시", "시모사", "스루가"),
    3_486: ("스루가", "우지쓰나", "가이도 제일의 무사", "이마가와 요시모토"),
    3_489: ("승려", "스승", "우지쓰나", "다시 싸우고 싶었소"),
    3_495: ("요시모토", "우지쓰나", "우지야스", "난세의 법도"),
    3_496: ("죽은 이", "산 이", "이어", "사람"),
    3_498: ("이마가와 요시모토", "우지쓰나", "스루가", "간바라성", "가토의 난"),
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if not BATCH03_BUILDER.is_file():
    raise RuntimeError(f"batch03 helper missing: {BATCH03_BUILDER}")
engine = load_module("manual_compact_static007_batch03_engine_for_batch05", BATCH03_BUILDER)


class ManualCompactStatic007Batch05Error(RuntimeError):
    """Raised when strict input, evidence, layout, or output drifts."""


@dataclass(frozen=True)
class Bundle:
    event: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManualCompactStatic007Batch05Error(message)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ManualCompactStatic007Batch05Error(f"candidate path escapes tmp: {resolved}") from exc
    return resolved


def build_scene_index() -> Mapping[int, str]:
    scene_index: dict[int, str] = {}
    for scene, first_id, last_id in SCENE_GROUPS:
        require(first_id <= last_id, f"invalid scene range: {scene}")
        for entry_id in range(first_id, last_id + 1):
            require(entry_id not in scene_index, f"scene overlap: {entry_id}")
            scene_index[entry_id] = scene
    require(tuple(sorted(scene_index)) == SCENE_IDS, "scene range coverage drift")
    return scene_index


SCENE_INDEX = build_scene_index()


def validate_authored_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "target ID order/scope drift")
    require(set(CHANGED_IDS).isdisjoint(RETAINED_IDS), "changed/retained scope overlap")
    require(SCENE_IDS == tuple(range(3287, 3501)), "broad range drift")
    require(not (set(CHANGED_IDS) & set(RUNTIME_HOLD_IDS)), "runtime-hold row selected without route evidence")
    require(20 <= len(CHANGED_IDS) <= 40, "multi-scene batch target count outside policy")
    for entry_id, target in TARGETS.items():
        require("\x00" not in target, f"embedded terminator: {entry_id}")
        engine.base.base.assert_no_break_inside_tag(target)
        signature = engine.base.base.control_signature(target)
        require(signature["runtime_tokens"] == [], f"runtime token in changed target: {entry_id}")
        require(signature["printf_tokens"] == [], f"printf token in target: {entry_id}")
        require(signature["unknown_percent_count"] == 0, f"unknown percent in target: {entry_id}")
        require(signature["other_controls"] == [], f"other control in target: {entry_id}")
        metrics = engine.base.base.line_metrics(target)
        require(1 <= len(metrics) <= 4, f"target line count exceeds max: {entry_id}")
        require(all(line["passes_static_patch_007"] for line in metrics), f"target fails Static Patch 007: {entry_id}")
        if TARGET_LAYOUTS:
            expected_raw, expected_effective = TARGET_LAYOUTS[entry_id]
            require(tuple(line["raw_g1n_width_px"] for line in metrics) == expected_raw, f"target raw drift: {entry_id}")
            require(
                tuple(line["effective_width_px"] for line in metrics) == expected_effective,
                f"target effective drift: {entry_id}",
            )


def configure_engine() -> None:
    """Bind the committed codec/audit engine to this batch's strict scope."""
    engine.WORKSTREAM = WORKSTREAM
    engine.TMP_ROOT = TMP_ROOT
    engine.CANDIDATE_ROOT = CANDIDATE_ROOT
    engine.PREDECESSOR_WORKSTREAM = PREDECESSOR_WORKSTREAM
    engine.PREDECESSOR_CANDIDATE_ROOT = PREDECESSOR_CANDIDATE_ROOT
    engine.EXPECTED_PREDECESSOR_PROFILE = EXPECTED_PREDECESSOR_PROFILE
    engine.EXPECTED_OUTPUT_PROFILE = EXPECTED_OUTPUT_PROFILE
    engine.SCENE_NAME = SCENE_NAME
    # The shared codec's static line metric intentionally rejects unresolved
    # runtime name tokens. Those rows remain immutable and are audited below.
    engine.SCENE_IDS = ENGINE_REVIEW_IDS
    engine.CHANGED_IDS = CHANGED_IDS
    engine.RETAINED_IDS = ENGINE_RETAINED_IDS
    engine.TARGETS = TARGETS
    engine.TARGET_LAYOUTS = TARGET_LAYOUTS
    engine.RATIONALES = RATIONALES
    engine.CURRENT_QUALITY_PRESERVED = CURRENT_QUALITY_PRESERVED
    engine.validate_authored_targets = validate_authored_targets


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any], Mapping[str, Any]]:
    configure_engine()
    return engine.load_predecessor()


def scene_coverage(rows: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    by_id = {int(row["entry_id"]): row for row in rows}
    coverage: list[Mapping[str, Any]] = []
    for scene, first_id, last_id in SCENE_GROUPS:
        ids = list(range(first_id, last_id + 1))
        changed = [entry_id for entry_id in ids if by_id[entry_id]["changed"]]
        holds = [entry_id for entry_id in ids if entry_id in RUNTIME_HOLD_IDS]
        coverage.append(
            {
                "scene": scene,
                "reviewed_row_ids": ids,
                "reviewed_row_count": len(ids),
                "changed_manual_compact_ids": changed,
                "changed_manual_compact_count": len(changed),
                "runtime_hold_excluded_ids": holds,
                "runtime_hold_excluded_count": len(holds),
            }
        )
    return coverage


def runtime_hold_rows(before: Any, contexts: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Record unresolved runtime-token rows without static-width guessing."""
    rows: list[Mapping[str, Any]] = []
    for entry_id in RUNTIME_HOLD_IDS:
        current = before.texts[entry_id]
        direct = {language: contexts[language].texts[entry_id] for language in ("jp", "en", "sc", "tc")}
        signature = engine.base.base.control_signature(current)
        require(signature["runtime_tokens"], f"declared runtime hold has no runtime token: {entry_id}")
        require(signature == engine.base.base.control_signature(direct["jp"]), f"runtime hold KO/JP control drift: {entry_id}")
        engine.base.base.assert_no_break_inside_tag(current)
        rows.append(
            {
                "entry_id": entry_id,
                "scene": SCENE_INDEX[entry_id],
                "changed": False,
                "strict_predecessor_ko": current,
                "target_ko": current,
                "strict_predecessor_ko_utf16le_sha256": engine.text_hash(current),
                "target_ko_utf16le_sha256": engine.text_hash(current),
                "direct_pc_jp": direct["jp"],
                "direct_pc_en": direct["en"],
                "direct_pc_sc": direct["sc"],
                "direct_pc_tc": direct["tc"],
                "direct_pc_jp_utf16le_sha256": engine.text_hash(direct["jp"]),
                "direct_pc_en_utf16le_sha256": engine.text_hash(direct["en"]),
                "direct_pc_sc_utf16le_sha256": engine.text_hash(direct["sc"]),
                "direct_pc_tc_utf16le_sha256": engine.text_hash(direct["tc"]),
                "direct_control_signatures": {
                    "jp": engine.base.base.control_signature(direct["jp"]),
                    "en": engine.base.base.control_signature(direct["en"]),
                    "sc": engine.base.base.control_signature(direct["sc"]),
                    "tc": engine.base.base.control_signature(direct["tc"]),
                },
                "target_control_signature": signature,
                "strict_ko_matches_direct_jp_protected_signature": True,
                "japanese_source_line_breaks_used": False,
                "jp_lf_policy": "ignored",
                "runtime_tokens": signature["runtime_tokens"],
                "runtime_reservations": [],
                "runtime_proven": False,
                "current_manual_line_count": current.count("\n") + 1,
                "target_manual_line_count": current.count("\n") + 1,
                "current_lines": [],
                "target_lines": [],
                "current_static_patch_007_passes": None,
                "target_static_patch_007_passes": None,
                "layout_status": "NOT_EVALUATED_RUNTIME_HOLD",
                "runtime_hold_excluded": True,
                "runtime_hold_exclusion_reason": "런타임 이름 토큰의 행별 렌더링 경로·예약 폭 근거가 없어 자동 재배치하지 않았다.",
                "rationale": "장면 문맥과 direct PC 4언어를 기록하되, 런타임 토큰의 폭을 추측하지 않고 원문을 보존했다.",
                "historical_vs_current": None,
                "current_quality_conflict_check": {
                    "status": "NOT_APPLICABLE",
                    "reason": "런타임 이름 토큰의 행별 예약 폭 근거가 없으므로 변경하지 않았다.",
                },
                "terminator_policy": "UTF-16LE NUL terminator is serialized by rebuild_message_table",
            }
        )
    return rows


def prepare(*, require_output_profile: bool) -> Bundle:
    require(not PREPARATION_ONLY, "batch05 is preparation-only until the bulk strict predecessor is pinned")
    configure_engine()
    engine_bundle = engine.prepare(require_output_profile=require_output_profile)
    audit = copy.deepcopy(engine_bundle.audit)
    manifest = copy.deepcopy(engine_bundle.manifest)
    rows = list(audit["rows"])
    require(tuple(row["entry_id"] for row in rows) == ENGINE_REVIEW_IDS, "engine row coverage drift")
    _event, before, _raw, _profile, _predecessor_audit = load_predecessor()
    contexts, _context_profiles = engine.base.base.load_direct_contexts()
    rows.extend(runtime_hold_rows(before, contexts))
    rows.sort(key=lambda row: int(row["entry_id"]))
    require(tuple(row["entry_id"] for row in rows) == SCENE_IDS, "combined row coverage drift")
    for row in rows:
        entry_id = int(row["entry_id"])
        row["scene"] = SCENE_INDEX[entry_id]
        if entry_id in RUNTIME_HOLD_IDS:
            require(row["runtime_tokens"], f"declared runtime hold has no runtime token: {entry_id}")
            require(not row["changed"], f"runtime hold unexpectedly changed: {entry_id}")
        else:
            row["runtime_hold_excluded"] = False
    changed_rows = [row for row in rows if row["changed"]]
    require([row["entry_id"] for row in changed_rows] == list(CHANGED_IDS), "exact multi-row audit drift")

    audit["schema"] = "nobu16.kr.pc-event-manual-compact-static007-batch05-audit.v1"
    profiles = audit["source_profiles"]
    require("strict_predecessor_batch02" in profiles, "engine predecessor profile key drift")
    profiles["strict_predecessor_batch04"] = profiles.pop("strict_predecessor_batch02")
    audit["coverage"]["reviewed_scene"] = SCENE_NAME
    audit["coverage"]["reviewed_row_ids"] = list(SCENE_IDS)
    audit["coverage"]["reviewed_row_count"] = len(SCENE_IDS)
    audit["coverage"]["retained_context_ids"] = list(RETAINED_IDS)
    audit["coverage"]["retained_context_count"] = len(RETAINED_IDS)
    audit["coverage"]["scene_groups"] = scene_coverage(rows)
    audit["coverage"]["runtime_hold_excluded_ids"] = list(RUNTIME_HOLD_IDS)
    audit["coverage"]["runtime_hold_excluded_count"] = len(RUNTIME_HOLD_IDS)
    audit["exact_multi_row_diff"] = changed_rows
    audit.pop("exact_two_row_diff", None)
    audit["exact_multi_row_diff_count"] = len(changed_rows)
    audit["rows"] = rows

    manifest["schema"] = "nobu16.kr.pc-event-manual-compact-static007-batch05-manifest.v1"
    manifest["exact_multi_row_diff"] = True
    manifest.pop("exact_two_row_diff", None)
    manifest["scene_groups"] = scene_coverage(rows)
    manifest["runtime_hold_excluded_ids"] = list(RUNTIME_HOLD_IDS)
    return Bundle(engine_bundle.event, audit, manifest, engine_bundle.profile)


def write_candidate(bundle: Bundle) -> Path:
    configure_engine()
    return engine.write_candidate(bundle)


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "candidate event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "runtime_hold_excluded_ids": list(RUNTIME_HOLD_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_manual_compact_static007_batch05_v1.py",
        WORKSTREAM / "test_pc_event_manual_compact_static007_batch05_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("authoring-check", "profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "authoring-check":
        validate_authored_targets()
        print(json.dumps({entry_id: list(engine.base.base.line_metrics(text)) for entry_id, text in TARGETS.items()}, ensure_ascii=False))
        return 0
    if command == "profile":
        require(not PREPARATION_ONLY, "batch05 is preparation-only until the bulk strict predecessor is pinned")
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(
        json.dumps(
            {
                "changed_row_ids": bundle.audit["actual_changed_row_ids"],
                "runtime_hold_excluded_ids": list(RUNTIME_HOLD_IDS),
                "event_profile": bundle.profile,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
