#!/usr/bin/env python3
"""Build the private multi-scene Static Patch 007 manual-linebreak batch 06.

The strict Korean input is batch05's private candidate. Direct PC JP/EN/SC/TC
resources are read-only semantic evidence; no Steam, Git, release, or network
path exists here. The edit is layout-only: Korean non-whitespace characters,
control codes, colour tags, runtime tokens, and terminators are preserved.
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
PREDECESSOR_WORKSTREAM = "pc_event_manual_compact_static007_batch05_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_PREDECESSOR_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "D49A221732551E6DA673657A577828640E438D02B23AF3B529130A2B9689CC7F",
    "raw_size": 1_007_432,
    "sha256": "8B7B9BF8F104C56F3EED0B3B5E1871E416466CD443020D6306135CCA56E7FE42",
    "size": 1_011_408,
}
# Deterministic output from the pinned batch05 strict predecessor.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "2EEF242A9F5183061F866C854DF51139CF0FEC3E69C004F04C665B69C91AAF5B",
    "raw_size": 1_007_428,
    "sha256": "600B6F1C8BE432A5987E1A05F19DCA30AF00DB9BFBFEAC702CCB60605B19B313",
    "size": 1_011_404,
}
PREPARATION_ONLY = False

SCENE_GROUPS: tuple[tuple[str, int, int], ...] = (
    ("kawagoe_encirclement", 3_501, 3_526),
    ("takeda_nobushige_precepts", 3_527, 3_549),
    ("nabeshima_naoshige_hikotsuru", 3_550, 3_564),
    ("saito_tatsuoki_yoshitatsu", 3_565, 3_594),
    ("hojo_imagawa_and_fox_tale", 3_595, 3_641),
    ("nagao_torachiyo", 3_642, 3_661),
    ("mori_takamoto_education", 3_662, 3_688),
)
SCENE_NAME = "multi_scene_3501_3688"
SCENE_IDS = tuple(range(3_501, 3_689))
CHANGED_IDS = (
    3_502,
    3_505,
    3_508,
    3_517,
    3_542,
    3_550,
    3_551,
    3_561,
    3_563,
    3_564,
    3_566,
    3_570,
    3_575,
    3_577,
    3_590,
    3_595,
    3_596,
    3_597,
    3_599,
    3_605,
    3_613,
    3_615,
    3_619,
    3_638,
    3_640,
    3_641,
    3_643,
    3_644,
    3_645,
    3_647,
    3_648,
    3_653,
    3_656,
    3_659,
    3_669,
)
RUNTIME_HOLD_IDS = (
    3_514,
    3_519,
    3_520,
    3_522,
    3_524,
    3_525,
    3_526,
    3_548,
    3_565,
    3_576,
    3_578,
    3_579,
    3_584,
    3_609,
    3_610,
    3_611,
    3_612,
    3_617,
)
# These were historical manual_compact rows, but their existing breaks already
# form the right semantic units. They are consciously retained rather than
# disturbed merely to force a diff.
STATIC_RETAINED_MANUAL_IDS = (3_634, 3_642)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)
ENGINE_REVIEW_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in RUNTIME_HOLD_IDS)
ENGINE_RETAINED_IDS = tuple(entry_id for entry_id in ENGINE_REVIEW_IDS if entry_id not in CHANGED_IDS)
E = "\x1b"

TARGETS: Mapping[int, str] = {
    3_502: (
        f"간토관령 {E}CA노리마사{E}CZ와 {E}CC오기야쓰{E}CZ {E}CA도모사다{E}CZ,\n"
        f"고가쿠보 {E}CA하루우지{E}CZ까지 합세해 {E}CC가와고에성{E}CZ을 치려\n"
        "진군 중입니다!"
    ),
    3_505: (
        f"설마… {E}CA이마가와 요시모토{E}CZ가\n"
        f"{E}CB다케다{E}CZ뿐 아니라 {E}CB양우에스기{E}CZ와 {E}CB고가쿠보{E}CZ까지\n"
        "모두 조종하는 건가!?"
    ),
    3_508: (
        "8만… 쉽게 모을 수는 없지.\n"
        f"허나 {E}CB양우에스기{E}CZ와 {E}CB고가쿠보{E}CZ가\n"
        "합세하면, 수만을 넘길 수도 있겠군…"
    ),
    3_517: (
        f"그래, {E}CC가와고에{E}CZ는 맡겼다! 남은 건 {E}CC가토{E}CZ.\n"
        f"{E}CA요시모토{E}CZ는 안 물러날 터.\n"
        "하지만 만만한 상대는 아니다…"
    ),
    3_542: (
        f"형님은 {E}CB다케다{E}CZ를 천하로 이끌 분입니다.\n"
        "저는 작은 재주뿐이니, 형님을 믿고 따를 뿐입니다."
    ),
    3_550: (
        f"{E}CB류조지{E}CZ의 책사 {E}CA나베시마 나오시게{E}CZ.\n"
        f"바쁜 나날을 내조로 받친 이는 아내 {E}CA히코쓰루히메{E}CZ였다."
    ),
    3_551: (
        "두 사람의 첫 만남은 전설로 남았다. 개선 길에\n"
        f"{E}CA나오시게{E}CZ는 {E}CC이이모리성{E}CZ에서 {E}CA히코쓰루{E}CZ을 처음 보았다…"
    ),
    3_561: (
        f"{E}CA이시이 쓰네노부{E}CZ의 딸 {E}CA히코쓰루{E}CZ입니다.\n"
        f"전에는 {E}CA노토미 노부즈미{E}CZ에게 시집갔으나, {E}CA노토미{E}CZ 님이\n"
        "전사해 과부가 됐습니다…"
    ),
    3_563: (
        f"시녀를 지휘하고 손수 생선을 굽는 {E}CA히코쓰루{E}CZ의 솜씨에\n"
        f"반한 {E}CA나오시게{E}CZ는 훗날 정식으로 청혼했다."
    ),
    3_564: (
        f"드문 연애결혼으로 아내가 된 {E}CA히코쓰루{E}CZ는\n"
        f"총명함과 포용력으로 냉철한 {E}CA나베시마 나오시게{E}CZ를 보필했다…"
    ),
    3_566: (
        f"하극상의 전형 {E}CC미노{E}CZ {E}CB사이토 가문{E}CZ은\n"
        f"이제 {E}CA오다 노부나가{E}CZ의 공세에 밀려 4대 역사를\n"
        "끝내려 하고 있었다…"
    ),
    3_570: (
        f"아니요, {E}CB사이토 가문{E}CZ에 미련은 없습니다.\n"
        f"이것도 운명이었겠지요. 이제 {E}CC미노{E}CZ의 부흥만 빕니다…"
    ),
    3_575: (
        f"{E}CA사이토 다쓰오키{E}CZ는 {E}CC나가라강{E}CZ을 내려 {E}CC이세 나가시마{E}CZ로\n"
        f"달아났거나, 옛 연을 따라 {E}CC에치젠{E}CZ으로\n"
        "갔다고 한다."
    ),
    3_577: (
        f"쇼군님을 뵙게 되어 영광입니다… 저는 {E}CA사이토 다카마사{E}CZ라\n"
        "합니다. 귀경을 축하드립니다."
    ),
    3_590: (
        f"{E}CA사이토 다카마사{E}CZ는 쇼군 {E}CA요시테루{E}CZ에게\n"
        f"막부 사시키이자 외가와 연 있는 {E}CB잇시키 가문{E}CZ의\n"
        "이름을 받았다."
    ),
    3_595: (
        f"{E}CB호조 가문{E}CZ의 시조 {E}CA소운{E}CZ({E}CA이세 소즈이{E}CZ)은\n"
        f"{E}CA이마가와 우지치카{E}CZ의 숙부이자 군사였고, 훗날 독립해\n"
        f"{E}CC간토{E}CZ에 영지를 넓혔다."
    ),
    3_596: (
        f"{E}CA우지쓰나{E}CZ 때 {E}CB이마가와{E}CZ와 {E}CB호조{E}CZ는 각기 다이묘가 돼\n"
        f"{E}CC스루가{E}CZ 동부, {E}CC후지강{E}CZ 동쪽을 두고 적대했다."
    ),
    3_597: (
        f"{E}CB이마가와 가문{E}CZ은 본래 지배하던 {E}CC가토{E}CZ를\n"
        f"가신 집안이던 {E}CB호조 가문{E}CZ에 빼앗긴 채 언제까지고 둘 수 없었다."
    ),
    3_599: (
        f"{E}CA요시모토{E}CZ 계략으로, {E}CB야마노우치{E}CZ·{E}CB오기야쓰{E}CZ {E}CB양 우에스기{E}CZ에\n"
        f"{E}CA하루우지{E}CZ까지 가세해 {E}CB호조{E}CZ의\n"
        f"{E}CC가와고에성{E}CZ을 공격했다…"
    ),
    3_605: (
        "작은 싸움의 승패에 매달릴 틈은 없다.\n"
        f"{E}CA우지야스{E}CZ는 {E}CA요시모토{E}CZ의 뜻을 꺾을 기사회생의 수를\n"
        "둘 때를 노렸다…"
    ),
    3_613: (
        f"그럼, {E}CC가토{E}CZ 성은 {E}CB호조{E}CZ에서 {E}CB이마가와{E}CZ로 넘기고\n"
        "양가는 화친한다. 이 조건으로 좋겠소?"
    ),
    3_615: (
        f"{E}CC가토{E}CZ는 본래 {E}CB이마가와{E}CZ의 땅. 제자리로 돌아온 셈이지만…\n"
        "넘긴다면 더 싸울 이유는 없다."
    ),
    3_619: (
        f"{E}CB이마가와{E}CZ·{E}CB호조{E}CZ·{E}CB다케다{E}CZ의 미묘한 관계는\n"
        "훗날 고소슨 삼국동맹으로 이어진다."
    ),
    3_638: (
        f"{E}CA호조 우지야스{E}CZ는 무략뿐 아니라 와카에도 능한 문인·독서가였다.\n"
        "역사서 ‘아즈마카가미’도 지녔다 전한다."
    ),
    3_640: (
        f"{E}CA우지야스{E}CZ 사후, {E}CA우지마사{E}CZ는 여우의 저주를 우려해\n"
        f"‘{E}CA호조{E}CZ 이나리’를 세웠다."
    ),
    3_641: (
        f"{E}CA호조{E}CZ 이나리의 개구리 모양 ‘개구리바위’는\n"
        f"{E}CC오다와라{E}CZ에 위기 오면 꼭 운다고 전한다…"
    ),
    3_643: (
        f"그러나 {E}CB우에스기{E}CZ 가신·{E}CC에치고{E}CZ 국인과 잦은 충돌을 빚어,\n"
        "모두의 지지를 얻진 못했다."
    ),
    3_644: (
        f"{E}CA다메카게{E}CZ 사후 장남 {E}CA하루카게{E}CZ가 이은 뒤,\n"
        f"그 모순이 터져 {E}CB나가오{E}CZ 이탈자도 나타나기 시작했다…"
    ),
    3_645: (
        "으음, 다들 왜 내게 이를 드러내나… 난 아무 잘못도 없는데.\n"
        "죽은 아버지만 원망해야 하나…?"
    ),
    3_647: (
        f"그 기대를 받은 이는 {E}CA하루카게{E}CZ의 어린 아우로\n"
        f"{E}CC린센지{E}CZ에서 불도를 닦던 {E}CA도라치요{E}CZ였다."
    ),
    3_648: (
        f"{E}CA도라치요{E}CZ 님은 수행 중 문무에 뛰어난 장수감이라\n"
        f"들었습니다. 부디 {E}CB나가오{E}CZ의 위기를 구해 주십시오!"
    ),
    3_653: (
        f"형 {E}CA하루카게{E}CZ도 국인 반란에 마음 아프신다.\n"
        "피를 나눈 아우인 네가 돕지 않고 어찌하겠느냐!"
    ),
    3_656: (
        f"가신 청으로 {E}CA도라치요{E}CZ는 원복하고, {E}CA가게토라{E}CZ라 하고\n"
        f"형 {E}CA하루카게{E}CZ를 섬겼다. 훗날 {E}CA우에스기{E}CZ 겐신, 바로 그다―"
    ),
    3_659: (
        f"유약한 {E}CA하루카게{E}CZ와 달리 {E}CA가게토라{E}CZ의 용맹은\n"
        f"널리 알려져, 부친 {E}CA다메카게{E}CZ를 떠올린 이도 많았다."
    ),
    3_669: (
        f"오늘부터 {E}CA시지 히로요시{E}CZ가 후견이다. 그의 말을 잘 듣고,\n"
        "당주로 부끄럽지 않은 장수가 되어라!"
    ),
}

TARGET_LAYOUTS: Mapping[int, tuple[tuple[int, ...], tuple[int, ...]]] = {
    3_502: ((912, 1_104, 336), (570, 690, 210)),
    3_505: ((600, 984, 480), (375, 615, 300)),
    3_508: ((600, 672, 816), (375, 420, 510)),
    3_517: ((912, 576, 672), (570, 360, 420)),
    3_542: ((888, 1_152), (555, 720)),
    3_550: ((768, 1_224), (480, 765)),
    3_551: ((1_056, 1_176), (660, 735)),
    3_561: ((864, 1_200, 552), (540, 750, 345)),
    3_563: ((1_200, 936), (750, 585)),
    3_564: ((912, 1_344), (570, 840)),
    3_566: ((768, 1_032, 456), (480, 645, 285)),
    3_570: ((912, 1_176), (570, 735)),
    3_575: ((1_176, 840, 288), (735, 525, 180)),
    3_577: ((1_272, 672), (795, 420)),
    3_590: ((840, 1_056, 336), (525, 660, 210)),
    3_595: ((864, 1_200, 504), (540, 750, 315)),
    3_596: ((1_104, 984), (690, 615)),
    3_597: ((864, 1_440), (540, 900)),
    3_599: ((1_248, 624, 528), (780, 390, 330)),
    3_605: ((864, 1_128, 360), (540, 705, 225)),
    3_613: ((1_008, 864), (630, 540)),
    3_615: ((1_248, 696), (780, 435)),
    3_619: ((864, 816), (540, 510)),
    3_638: ((1_440, 912), (900, 570)),
    3_640: ((1_104, 552), (690, 345)),
    3_641: ((960, 912), (600, 570)),
    3_643: ((1_248, 624), (780, 390)),
    3_644: ((912, 1_176), (570, 735)),
    3_645: ((1_344, 696), (840, 435)),
    3_647: ((1_008, 864), (630, 540)),
    3_648: ((1_104, 1_128), (690, 705)),
    3_653: ((960, 1_080), (600, 675)),
    3_656: ((1_152, 1_248), (720, 780)),
    3_659: ((960, 1_152), (600, 720)),
    3_669: ((1_272, 840), (795, 525)),
}

RATIONALES: Mapping[int, str] = {
    3_502: "가와고에성을 향한 진군의 주체와 행동을 분리해, 합세한 세력의 열거와 출병 목적을 읽기 쉽게 배치했다.",
    3_505: "요시모토의 조종 의혹, 조종 대상 세력, 결론의 순서로 묶어 반문을 보존했다.",
    3_508: "병력 규모의 평가 뒤에 연합 세력과 그 귀결을 이어, 조건과 결과의 관계를 명확히 했다.",
    3_517: "가와고에 위임과 가토 대응을 한 줄에 묶고, 요시모토의 위협 평가를 별도 의미 단위로 두었다.",
    3_542: "형의 천하 경영 능력과 자신이 따르겠다는 결의를 두 문장 단위로 배치했다.",
    3_550: "나오시게의 책사 지위와 히코쓰루의 내조를 두 문장 단위로 연결했다.",
    3_551: "전설적 첫 만남의 서술과 개선길에서의 만남을 자연스러운 시간 흐름으로 묶었다.",
    3_561: "신분 소개, 전혼, 전사로 인한 과부 신세를 각각 읽히는 단위로 재배치했다.",
    3_563: "히코쓰루의 기지와 나오시게의 청혼을 원인과 결과의 두 단위로 나눴다.",
    3_564: "연애결혼과 히코쓰루가 보필한 방식·대상을 두 줄로 정리했다.",
    3_566: "사이토 가문의 하극상 배경, 노부나가의 공세, 사대 역사의 종결을 순서대로 보존했다.",
    3_570: "사이토 가문에 대한 미련 없음과 미노 부흥을 바라는 결말을 두 문장 단위로 묶었다.",
    3_575: "나가라강·이세 나가시마 경로와 에치젠 행의 두 전승을 구분했다.",
    3_577: "알현 인사와 신분 소개·귀경 축하를 자연스러운 말의 호흡으로 재배치했다.",
    3_590: "요시테루에게 받은 잇시키 가문 명적의 성격과 수여 결과를 순서대로 유지했다.",
    3_595: "소운의 신분·이마가와와의 관계·간토 독립 확장의 서술 순서를 보존했다.",
    3_596: "양 가문이 다이묘로 분리된 사실과 스루가 동부를 둘러싼 적대를 두 의미 단위로 나눴다.",
    3_597: "가토의 본래 지배와 호조에게 빼앗긴 상태를 한 원인·결과 문장으로 정리했다.",
    3_599: "요시모토의 계략, 가세한 세력, 가와고에성 공격의 흐름을 끊지 않도록 재배치했다.",
    3_605: "소규모 전투에 얽매일 수 없음과 기사회생의 수를 노린다는 대비를 유지했다.",
    3_613: "가토성 양도 조건과 화친 확인을 두 문장 단위로 분리했다.",
    3_615: "가토의 귀속과 전쟁을 지속할 이유가 없다는 판단을 두 문장으로 연결했다.",
    3_619: "삼 가문의 미묘한 관계와 훗날 삼국동맹으로 이어지는 결과를 두 줄로 묶었다.",
    3_638: "우지야스의 무략·와카 능력과 역사서 소지를 별도 문장 단위로 배치했다.",
    3_640: "우지야스 사후의 여우 저주 우려와 우지마사의 이나리 건립을 인과로 연결했다.",
    3_641: "개구리바위의 정체와 오다와라 위기 때 우는 전승을 두 의미 단위로 정리했다.",
    3_643: "우에스기 가신·에치고 국인과의 충돌과 지지 상실이라는 인과를 유지했다.",
    3_644: "다메카게 사후의 모순 폭발과 나가오 이탈자 출현을 순서대로 배치했다.",
    3_645: "하루카게의 독백에서 원망의 대상이 죽은 아버지로 향하는 흐름을 두 호흡으로 묶었다.",
    3_647: "기대를 받은 도라치요의 혈연 관계와 린센지 수행을 두 의미 단위로 분리했다.",
    3_648: "도라치요의 자질에 대한 설명과 나가오 가문 구원 요청을 두 호흡으로 배치했다.",
    3_653: "하루카게의 고통과 피를 나눈 아우에게 건네는 책무를 두 문장 단위로 묶었다.",
    3_656: "원복·가게토라 개명·하루카게 보좌와 훗날 겐신이라는 귀결을 두 호흡으로 배치했다.",
    3_659: "가게토라의 용맹과 다메카게를 떠올린 사람들의 평가를 두 의미 단위로 나눴다.",
    3_669: "후견인 임명과 당주로서의 성장 명령을 두 문장 단위로 배치했다.",
}

# The layout-only integrity check below proves every non-whitespace character
# of the strict Korean input remains present and ordered. This list gives the
# generic audit a concise explicit preservation marker for each changed row.
CURRENT_QUALITY_PRESERVED: Mapping[int, tuple[str, ...]] = {
    entry_id: ("strict Korean non-whitespace sequence preserved",) for entry_id in CHANGED_IDS
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


engine = load_module("manual_compact_static007_batch06_engine", BATCH03_BUILDER)


class ManualCompactStatic007Batch06Error(RuntimeError):
    """Raised when the candidate-only batch06 contract is violated."""


@dataclass(frozen=True)
class Bundle:
    event: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManualCompactStatic007Batch06Error(message)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ManualCompactStatic007Batch06Error(f"candidate path escapes tmp: {resolved}") from exc
    return resolved


def build_scene_index() -> Mapping[int, str]:
    index: dict[int, str] = {}
    for scene, first_id, last_id in SCENE_GROUPS:
        for entry_id in range(first_id, last_id + 1):
            require(entry_id not in index, f"scene group overlap: {entry_id}")
            index[entry_id] = scene
    require(tuple(index) == SCENE_IDS, "scene group coverage drift")
    return index


SCENE_INDEX = build_scene_index()


def non_whitespace(text: str) -> str:
    return "".join(character for character in text if not character.isspace())


def validate_authored_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "target ID order/scope drift")
    require(SCENE_IDS == tuple(range(3_501, 3_689)), "broad range drift")
    require(set(CHANGED_IDS).isdisjoint(RETAINED_IDS), "changed/retained scope overlap")
    require(not (set(CHANGED_IDS) & set(RUNTIME_HOLD_IDS)), "runtime-hold row selected without route evidence")
    require(set(STATIC_RETAINED_MANUAL_IDS).issubset(ENGINE_RETAINED_IDS), "static retained manual scope drift")
    require(20 <= len(CHANGED_IDS) <= 40, "multi-scene batch target count outside policy")
    require(tuple(TARGET_LAYOUTS) == CHANGED_IDS, "target layout ID order/scope drift")
    require(tuple(RATIONALES) == CHANGED_IDS, "rationale ID order/scope drift")
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
        expected_raw, expected_effective = TARGET_LAYOUTS[entry_id]
        require(
            tuple(line["raw_g1n_width_px"] for line in metrics) == expected_raw,
            f"target raw drift: {entry_id}",
        )
        require(
            tuple(line["effective_width_px"] for line in metrics) == expected_effective,
            f"target effective drift: {entry_id}",
        )


def configure_engine() -> None:
    """Bind the committed codec/audit engine to batch06's strict input and scope."""
    engine.WORKSTREAM = WORKSTREAM
    engine.TMP_ROOT = TMP_ROOT
    engine.CANDIDATE_ROOT = CANDIDATE_ROOT
    engine.PREDECESSOR_WORKSTREAM = PREDECESSOR_WORKSTREAM
    engine.PREDECESSOR_CANDIDATE_ROOT = PREDECESSOR_CANDIDATE_ROOT
    engine.EXPECTED_PREDECESSOR_PROFILE = EXPECTED_PREDECESSOR_PROFILE
    engine.EXPECTED_OUTPUT_PROFILE = EXPECTED_OUTPUT_PROFILE
    engine.SCENE_NAME = SCENE_NAME
    # The shared line metric intentionally rejects unresolved runtime tokens.
    # Those rows remain immutable and are audited separately below.
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
    """Record unresolved runtime-name rows without inventing a reservation width."""
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
                    language: engine.base.base.control_signature(direct[language])
                    for language in ("jp", "en", "sc", "tc")
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
    require(not PREPARATION_ONLY, "batch06 is preparation-only until its strict predecessor is pinned")
    configure_engine()
    engine_bundle = engine.prepare(require_output_profile=require_output_profile)
    audit = copy.deepcopy(engine_bundle.audit)
    manifest = copy.deepcopy(engine_bundle.manifest)
    rows = list(audit["rows"])
    require(tuple(row["entry_id"] for row in rows) == ENGINE_REVIEW_IDS, "engine row coverage drift")
    _event, before, _raw, _profile, _predecessor_audit = load_predecessor()
    contexts, _context_profiles = engine.base.base.load_direct_contexts()
    for entry_id in CHANGED_IDS:
        require(
            non_whitespace(before.texts[entry_id]) == non_whitespace(TARGETS[entry_id]),
            f"layout-only Korean text integrity drift: {entry_id}",
        )
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
        if entry_id == 3_634:
            row["rationale"] = "기존 수동 개행이 말장난 설명·여우 울음의 반환·여우를 물리치는 의도를 이미 문맥 단위로 나누므로 유지했다."
            row["current_quality_conflict_check"] = {
                "status": "PASS_RETAINED",
                "reason": "historical manual_compact 행이지만 새 개행을 강제하지 않고, 현재의 의미 단위를 보존했다.",
            }
        if entry_id == 3_642:
            row["rationale"] = "기존 수동 개행이 다메카게 대의 배경·주가 초월·에치고 제일 세력이라는 세 의미 단위를 이미 보존하므로 유지했다."
            row["current_quality_conflict_check"] = {
                "status": "PASS_RETAINED",
                "reason": "historical manual_compact 행이지만 새 개행을 강제하지 않고, 현재의 의미 단위를 보존했다.",
            }
    changed_rows = [row for row in rows if row["changed"]]
    require([row["entry_id"] for row in changed_rows] == list(CHANGED_IDS), "exact multi-row audit drift")

    audit["schema"] = "nobu16.kr.pc-event-manual-compact-static007-batch06-audit.v1"
    profiles = audit["source_profiles"]
    require("strict_predecessor_batch02" in profiles, "engine predecessor profile key drift")
    profiles["strict_predecessor_batch05"] = profiles.pop("strict_predecessor_batch02")
    audit["source_policy"]["layout_only_non_whitespace_integrity_verified"] = True
    audit["coverage"]["reviewed_scene"] = SCENE_NAME
    audit["coverage"]["reviewed_row_ids"] = list(SCENE_IDS)
    audit["coverage"]["reviewed_row_count"] = len(SCENE_IDS)
    audit["coverage"]["retained_context_ids"] = list(RETAINED_IDS)
    audit["coverage"]["retained_context_count"] = len(RETAINED_IDS)
    audit["coverage"]["scene_groups"] = scene_coverage(rows)
    audit["coverage"]["runtime_hold_excluded_ids"] = list(RUNTIME_HOLD_IDS)
    audit["coverage"]["runtime_hold_excluded_count"] = len(RUNTIME_HOLD_IDS)
    audit["coverage"]["static_retained_manual_ids"] = list(STATIC_RETAINED_MANUAL_IDS)
    audit["coverage"]["static_retained_manual_count"] = len(STATIC_RETAINED_MANUAL_IDS)
    audit["exact_multi_row_diff"] = changed_rows
    audit.pop("exact_two_row_diff", None)
    audit["exact_multi_row_diff_count"] = len(changed_rows)
    audit["rows"] = rows

    manifest["schema"] = "nobu16.kr.pc-event-manual-compact-static007-batch06-manifest.v1"
    manifest["exact_multi_row_diff"] = True
    manifest.pop("exact_two_row_diff", None)
    manifest["scene_groups"] = scene_coverage(rows)
    manifest["runtime_hold_excluded_ids"] = list(RUNTIME_HOLD_IDS)
    manifest["static_retained_manual_ids"] = list(STATIC_RETAINED_MANUAL_IDS)
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
        "static_retained_manual_ids": list(STATIC_RETAINED_MANUAL_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_manual_compact_static007_batch06_v1.py",
        WORKSTREAM / "test_pc_event_manual_compact_static007_batch06_v1.py",
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
                "static_retained_manual_ids": list(STATIC_RETAINED_MANUAL_IDS),
                "event_profile": bundle.profile,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
