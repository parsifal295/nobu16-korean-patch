#!/usr/bin/env python3
"""Build the private Static Patch 007 manual-linebreak batch 07 candidate.

The strict Korean input is the committed 6000--7999 restoration candidate.
Direct PC JP/EN/SC/TC resources are read-only semantic evidence.  This
workstream writes only its private candidate beneath ``tmp``; it contains no
Steam, Git, release, or network path.  The edit is layout-only: Korean
non-whitespace characters, control codes, colour tags, runtime tokens, and
terminators are preserved.  No sentence is shortened or deleted.
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

BATCH06_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_static007_batch06_v1"
    / "build_pc_event_manual_compact_static007_batch06_v1.py"
)
PREDECESSOR_WORKSTREAM = "pc_event_manual_compact_static007_6000_7999_restore_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_PREDECESSOR_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "567C8C3C2F371E27CBE6FFEAB9F8F3EE7F6D6F13A2C179682A5A7F7D3F35780F",
    "raw_size": 1_020_112,
    "sha256": "D99390D4F2D7D469C105439A11476B01830F5E96287B278C164045CBC7BA3547",
    "size": 1_024_138,
}
# Deterministic output from the pinned 6000--7999 strict predecessor.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "85C48E864CC06831EB8F31C713703E0E3715848EE049A36B4F53CEB757F186E3",
    "raw_size": 1_020_156,
    "sha256": "5B84334A51829A8D981F4BE5E161D73803894D29F7FA1D91AC40090671CB347D",
    "size": 1_024_182,
}
COMPLETE_KO_3820_SOURCE = (
    REPO
    / "workstreams"
    / "dialogue"
    / "public"
    / "msgev_ko_historical_events_3819_3929.v0.7.json"
)
EXPECTED_COMPLETE_KO_3820_UTF16LE_SHA256 = "939881EFC8E0CBE750DE47FB6B104BB1900065D0D8299FB717353B326B274697"

SCENE_NAME = "multi_scene_3689_3898"
SCENE_IDS = tuple(range(3_689, 3_899))
SCENE_GROUPS: tuple[tuple[str, int, int], ...] = (
    ("kawagoe_night_battle", 3_689, 3_706),
    ("nobunaga_genpuku", 3_707, 3_709),
    ("ashikaga_yoshiharu_yoshiteru", 3_710, 3_737),
    ("ikoma_kitsuno", 3_738, 3_763),
    ("nagao_kagetora_succession", 3_764, 3_798),
    ("otomo_thunder_god", 3_799, 3_818),
    ("miyoshi_nagayoshi", 3_819, 3_839),
    ("matsudaira_takechiyo", 3_840, 3_854),
    ("nagao_ueda_reconciliation", 3_855, 3_879),
    ("kikkawa_motoharu", 3_880, 3_898),
)
CHANGED_IDS = (
    3_690,
    3_710,
    3_712,
    3_738,
    3_740,
    3_749,
    3_756,
    3_762,
    3_764,
    3_775,
    3_800,
    3_819,
    3_820,
    3_821,
    3_825,
    3_826,
    3_838,
    3_839,
    3_840,
    3_849,
    3_853,
    3_855,
    3_856,
    3_857,
    3_858,
    3_880,
    3_890,
    3_897,
)
RUNTIME_HOLD_IDS = (
    3_691,
    3_692,
    3_694,
    3_703,
    3_713,
    3_715,
    3_716,
    3_717,
    3_720,
    3_729,
    3_730,
    3_734,
    3_736,
    3_765,
    3_766,
    3_767,
    3_770,
    3_777,
    3_778,
    3_781,
    3_782,
    3_783,
    3_789,
    3_790,
    3_793,
    3_795,
    3_797,
    3_798,
    3_799,
    3_801,
    3_806,
    3_810,
    3_811,
    3_815,
    3_817,
    3_818,
    3_859,
    3_860,
    3_861,
    3_862,
    3_864,
    3_865,
    3_867,
    3_869,
    3_873,
    3_875,
    3_876,
    3_877,
)
# These legacy manual_compact rows were read in context and deliberately left
# untouched: rebreaking them would be a cosmetic diff rather than an
# improvement. 3820 additionally needs a later translation-quality pass, not
# a layout-only rewrite.
STATIC_RETAINED_MANUAL_IDS = (3_699, 3_700, 3_704, 3_768, 3_796, 3_830, 3_879)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)
ENGINE_REVIEW_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in RUNTIME_HOLD_IDS)
ENGINE_RETAINED_IDS = tuple(entry_id for entry_id in ENGINE_REVIEW_IDS if entry_id not in CHANGED_IDS)
SOURCE_COMPLETE_RESTORATION_IDS = (3_820,)
LAYOUT_ONLY_CHANGED_IDS = tuple(entry_id for entry_id in CHANGED_IDS if entry_id not in SOURCE_COMPLETE_RESTORATION_IDS)
E = "\x1b"

TARGETS: Mapping[int, str] = {
    3_690: (
        f"{E}CA요시모토{E}CZ 조략에 {E}CB야마노우치{E}CZ·{E}CB오기야쓰{E}CZ·{E}CB고가 아시카가{E}CZ가\n"
        f"일제히 봉기해 {E}CC가와고에성{E}CZ을 포위했다."
    ),
    3_710: (
        "전국시대에 접어들며, 간레이의 쇼군 보좌·정무 체제는 붕괴.\n"
        f"{E}CB아시카가{E}CZ·{E}CB호소카와{E}CZ도 함께 분열했다……"
    ),
    3_712: (
        f"이해 {E}CB호소카와 게이초{E}CZ 가독을 두고\n"
        f"{E}CA하루모토{E}CZ·{E}CA우지쓰나{E}CZ 양 {E}CB호소카와{E}CZ 세력이 격돌,\n"
        f"{E}CA요시하루{E}CZ는 다시 교토를 떠났다."
    ),
    3_738: (
        f"{E}CC오와리{E}CZ에 {E}CB이코마 가문{E}CZ 토호가 있었다. 당주 {E}CA이에무네{E}CZ는\n"
        "무사이면서 장사했고, 그 저택엔\n"
        "사람들이 늘 드나들었다."
    ),
    3_740: (
        f"새것 좋아하고 {E}CC오와리{E}CZ 너머 천하를 본\n"
        f"{E}CB오다 가문{E}CZ 젊은 주군 {E}CA노부나가{E}CZ도 {E}CC이코마 저택{E}CZ에\n"
        "자주 머물렀다."
    ),
    3_749: (
        f"{E}CA이코마 이에무네{E}CZ에겐 딸이 여럿 있었고, 그중 둘째는\n"
        f"이름난 미인이었다. {E}CA노부나가{E}CZ의 저택 방문 이유였다."
    ),
    3_756: (
        "……모른다. 아버지가 정한 혼담이다.\n"
        f"{E}CC미노{E}CZ와 화친하려는 일일 뿐. 내가 따를 의리는 없다."
    ),
    3_762: (
        f"정실 {E}CA노히메{E}CZ보다 앞서 만난 이 여인에게,\n"
        f"{E}CA노부나가{E}CZ가 아명 {E}CA깃포시{E}CZ 한 글자를 주었다는\n"
        "추측도 가능하다."
    ),
    3_764: (
        f"병약한 {E}CA나가오 하루카게{E}CZ가\n"
        f"에치고 슈고다이 {E}CB나가오가{E}CZ 당주가 되자,\n"
        f"유력 무사들은 {E}CA하루카게{E}CZ에게 거듭 반란했다."
    ),
    3_775: (
        f"계속 당주로 일하면 병든 {E}CA하루카게{E}CZ 공의 부담만 커지고,\n"
        "오히려 형님을 괴롭히게 됩니다."
    ),
    3_800: (
        "명민하고 무용도 빼어났으며,\n"
        "인재를 키우고 백성을 아끼는 데 뛰어났다.\n"
        "젊어서부터 수많은 전공을 세웠다."
    ),
    3_819: (
        f"{E}CB오가사와라씨{E}CZ 방계인 {E}CB미요시 가문{E}CZ은 {E}CC아와 미요시군{E}CZ에\n"
        f"터를 잡고 {E}CB아와 호소카와씨{E}CZ를 섬겼다."
    ),
    3_820: (
        f"오닌의 난 뒤, {E}CA미요시 유키나가{E}CZ는\n"
        f"{E}CB아와 호소카와가{E}CZ에서 관령·{E}CB호소카와 게이초가{E}CZ에\n"
        f"양자로 들어간 {E}CA호소카와 스미모토{E}CZ의 가독 다툼을\n"
        "도와 싸워 권세를 얻었다."
    ),
    3_821: (
        f"하지만 {E}CA유키나가{E}CZ 후계자 {E}CA모토나가{E}CZ는\n"
        f"분가 {E}CA미요시 마사나가{E}CZ 모함으로 {E}CA스미모토{E}CZ 아들\n"
        f"{E}CA하루모토{E}CZ와 맞섰다."
    ),
    3_825: (
        f"{E}CB호소카와 가문{E}CZ이 세력을 지키는 것도 우리 공이 있기에\n"
        f"가능한 일! {E}CA하루모토{E}CZ 그릇과는 무관합니다."
    ),
    3_826: (
        f"우리 {E}CB미요시{E}CZ 힘이 없었다면,\n"
        f"{E}CB호소카와{E}CZ 가독을 둔 {E}CA우지쓰나{E}CZ와 싸움도 진작\n"
        "맥없이 패했겠지요?"
    ),
    3_838: (
        f"{E}CA나가요시{E}CZ는 {E}CA호소카와 하루모토{E}CZ를 버리고\n"
        f"대립하던 {E}CA호소카와 우지쓰나{E}CZ 진영을 택했다."
    ),
    3_839: (
        f"{E}CA나가요시{E}CZ 배반에 {E}CB호소카와 게이초가{E}CZ의 가독을 둔\n"
        f"{E}CA하루모토{E}CZ·{E}CA우지쓰나{E}CZ 간 대립은\n"
        f"{E}CC기나이{E}CZ 혼란을 더 깊게 했다."
    ),
    3_840: (
        "그 일은 너무도 갑작스러웠다.\n"
        f"{E}CC미카와 오카자키성{E}CZ 다이묘 {E}CA마쓰다이라 히로타다{E}CZ가\n"
        "돌연 죽었다…"
    ),
    3_849: (
        f"{E}CB마쓰다이라{E}CZ 옛 신하들은 불만일 터…\n"
        f"{E}CA다케치요{E}CZ가 성년 되면 {E}CC오카자키{E}CZ를 {E}CB마쓰다이라가{E}CZ에\n"
        "돌려준다고 하시지요?"
    ),
    3_853: (
        f"몇 해 뒤 {E}CA다케치요{E}CZ가 성년이 되면\n"
        f"{E}CC오카자키{E}CZ성도, {E}CB마쓰다이라{E}CZ 가문도 예전처럼 되살아날 터…"
    ),
    3_855: (
        f"{E}CB나가오{E}CZ는 관령 {E}CB야마노우치 우에스기{E}CZ의 가재를 낸\n"
        f"집안이며, {E}CC에치고{E}CZ {E}CB나가오{E}CZ는 그 분가다."
    ),
    3_856: (
        f"하지만 {E}CB후추 나가오{E}CZ와 {E}CB우에다 나가오{E}CZ는\n"
        f"같은 {E}CB에치고 나가오{E}CZ 일족인데도, 예부터 사이가 험악했다."
    ),
    3_857: (
        f"{E}CB후추 나가오{E}CZ의 {E}CA다메카게{E}CZ가 {E}CC에치고{E}CZ에서 세력을 넓히자,\n"
        f"{E}CB우에다 나가오{E}CZ는 반기를 들었다가 패했다."
    ),
    3_858: (
        f"{E}CA다메카게{E}CZ의 아들 {E}CA하루카게{E}CZ는 {E}CB우에다 나가오{E}CZ를\n"
        "다시 끌어들이려 몇 차례 교섭했지만\n"
        "진척 없었다."
    ),
    3_880: (
        f"{E}CC아키{E}CZ·{E}CC이와미{E}CZ에 세력을 넓힌 {E}CB깃카와씨{E}CZ.\n"
        f"{E}CB후지와라씨{E}CZ 출신으로 가마쿠라 중기 {E}CC사이고쿠{E}CZ로\n"
        "거점을 옮긴 무사단이다."
    ),
    3_890: (
        "무가 혼인은 부모가 정하던 때,\n"
        f"{E}CA모토하루{E}CZ는 스스로 원해 {E}CA구마가이 노부나오{E}CZ의 딸을\n"
        "맞았다."
    ),
    3_897: (
        f"{E}CB깃카와{E}CZ 당주 {E}CA오키츠네{E}CZ를 가신들이\n"
        f"강제로 은거시키고, {E}CA모토하루{E}CZ를\n"
        f"{E}CB깃카와{E}CZ 당주로 세웠다…"
    ),
}

TARGET_LAYOUTS: Mapping[int, tuple[tuple[int, ...], tuple[int, ...]]] = {
    3_690: ((1_224, 864), (765, 540)),
    3_710: ((1_368, 840), (855, 525)),
    3_712: ((768, 1_008, 720), (480, 630, 450)),
    3_738: ((1_224, 720, 552), (765, 450, 345)),
    3_740: ((840, 1_056, 336), (525, 660, 210)),
    3_749: ((1_176, 1_176), (735, 735)),
    3_756: ((792, 1_176), (495, 735)),
    3_762: ((912, 984, 384), (570, 615, 240)),
    3_764: ((576, 888, 984), (360, 555, 615)),
    3_775: ((1_248, 720), (780, 450)),
    3_800: ((648, 960, 768), (405, 600, 480)),
    3_819: ((1_176, 840), (735, 525)),
    3_820: ((744, 1_056, 1_080, 576), (465, 660, 675, 360)),
    3_821: ((792, 1_032, 432), (495, 645, 270)),
    3_825: ((1_224, 960), (765, 600)),
    3_826: ((624, 984, 432), (390, 615, 270)),
    3_838: ((888, 984), (555, 615)),
    3_839: ((1_080, 648, 648), (675, 405, 405)),
    3_840: ((672, 1_104, 288), (420, 690, 180)),
    3_849: ((792, 1_104, 480), (495, 690, 300)),
    3_853: ((744, 1_272), (465, 795)),
    3_855: ((1_080, 864), (675, 540)),
    3_856: ((864, 1_296), (540, 810)),
    3_857: ((1_200, 936), (750, 585)),
    3_858: ((1_008, 816, 288), (630, 510, 180)),
    3_880: ((840, 1_056, 552), (525, 660, 345)),
    3_890: ((696, 1_128, 168), (435, 705, 105)),
    3_897: ((744, 696, 504), (465, 435, 315)),
}

RATIONALES: Mapping[int, str] = {
    3_690: "요시모토의 조략으로 봉기한 세력과 가와고에성 포위라는 결과를 두 의미 단위로 묶었다.",
    3_710: "간레이 중심의 정무 체제 붕괴와 아시카가·호소카와 분열을 문장 단위로 정리했다.",
    3_712: "게이초가 가독 다툼, 양 호소카와 세력의 격돌, 요시하루의 출경을 순서대로 보존했다.",
    3_738: "이코마 토호·이에무네의 신분과 저택의 개방성을 문맥 흐름에 맞게 재배치했다.",
    3_740: "노부나가의 성향과 이코마 저택 체류라는 결론을 분리해 읽기 흐름을 정리했다.",
    3_749: "이에무네의 딸들, 둘째의 미모, 노부나가 방문 이유를 두 문장 단위로 묶었다.",
    3_756: "혼담의 성격과 노부나가가 이를 따를 의리가 없다는 결론을 두 호흡으로 배치했다.",
    3_762: "노히메보다 앞선 만남, 깃포시 한 글자, 그 추측의 순서를 보존했다.",
    3_764: "하루카게의 즉위, 슈고다이 나가오가 당주 취임, 유력 무사의 반복 반란을 차례대로 배치했다.",
    3_775: "계속된 당주 업무가 하루카게에게 주는 부담과 형을 괴롭히게 되는 결과를 분리했다.",
    3_800: "무용·인재 육성·애민·전공의 열거를 세 의미 단위로 정리했다.",
    3_819: "미요시 가문의 오가사와라 방계 정체와 아와 정착·호소카와 섬김을 두 단위로 묶었다.",
    3_821: "모토나가의 지위, 마사나가의 모함, 하루모토와의 대립을 순서대로 배치했다.",
    3_825: "호소카와 세력 유지의 공이 미요시에 있다는 주장과 하루모토 평가를 분리했다.",
    3_826: "미요시의 힘 부재, 우지쓰나와의 가독 다툼, 패배라는 반문을 세 호흡으로 정리했다.",
    3_838: "하루모토를 버린 선택과 우지쓰나 진영 선택을 두 문장 단위로 배치했다.",
    3_839: "나가요시 배반 뒤 가독 다툼의 심화와 기나이 혼란이라는 인과를 보존했다.",
    3_840: "사건의 돌발성과 히로타다의 신분·사망을 세 의미 단위로 정리했다.",
    3_849: "마쓰다이라 옛 신하의 불만과 다케치요 성년 뒤의 반환 약속을 순서대로 배치했다.",
    3_853: "다케치요 성년과 오카자키성·마쓰다이라 가문의 부흥 기대를 두 호흡으로 묶었다.",
    3_855: "나가오의 야마노우치 우에스기 가재 배출과 에치고 나가오 분가 관계를 두 단위로 정리했다.",
    3_856: "후추·우에다 나가오의 같은 일족 관계와 오랜 불화를 두 호흡으로 배치했다.",
    3_857: "다메카게의 세력 확장과 우에다 나가오의 반기·패배를 두 단위로 나눴다.",
    3_858: "하루카게의 재편입 교섭 시도와 진척 부진을 세 의미 단위로 배치했다.",
    3_880: "깃카와의 아키·이와미 세력권과 후지와라 출신·사이고쿠 이주를 순서대로 보존했다.",
    3_890: "무가 혼인의 관습과 모토하루가 스스로 택한 혼인을 분리했다.",
    3_897: "오키츠네 강제 은거와 모토하루의 깃카와 당주 취임을 세 호흡으로 정리했다.",
}

RATIONALES[3_820] = (
    "Complete Korean plus pristine JP, EN, SC, and TC restore every source relation: "
    "Awa Hosokawa origin, Kanrei Keicho adoption, Hosokawa Sumimoto, succession conflict, support, battle, and gained influence."
)


STATIC_RETAINED_NOTES: Mapping[int, str] = {
    3_699: "우지야스 도착의 놀람, 가토 전투라는 의문이 이미 문맥 단위로 분리되어 유지했다.",
    3_700: "야습 성공과 포위군 동요가 이미 완결 문장 단위로 나뉘어 유지했다.",
    3_704: "도모사다 전사와 노리마사·하루우지 패주가 이미 자연스러운 사건 단위로 나뉘어 유지했다.",
    3_768: "거절, 형을 받들려는 이유, 당주 취임 거부가 이미 대사 호흡에 맞아 유지했다.",
    3_796: "하루카게 요양·새 당주 출발·평온하지 않은 결말이 이미 세 의미 단위로 나뉘어 유지했다.",
    3_830: "이케다 노부마사의 일화와 마사나가를 거부하는 결론이 이미 문장 단위로 나뉘어 유지했다.",
    3_879: "상호 경계 속 결속과 한 여인에게 맡겨진 열쇠가 이미 의미 단위로 나뉘어 유지했다.",
}

# The source-only assertion below proves that each Korean non-whitespace
# sequence is unchanged.  This marker lets the generic audit state that fact
# without pretending this is a text-translation rewrite.
CURRENT_QUALITY_PRESERVED: Mapping[int, tuple[str, ...]] = {
    entry_id: (
        (
            "Awa Hosokawa origin",
            "Kanrei Hosokawa Keicho adoption",
            "Hosokawa Sumimoto full name",
            "succession dispute support and battle",
            "gained influence",
        )
        if entry_id in SOURCE_COMPLETE_RESTORATION_IDS
        else ("strict Korean non-whitespace sequence preserved",)
    )
    for entry_id in CHANGED_IDS
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


batch06 = load_module("manual_compact_static007_batch07_context", BATCH06_BUILDER)
# Batch06 in turn imports the committed batch03 codec/audit engine.  We bind
# that generic engine to this strict predecessor below; batch06 itself is not
# used as Korean build input.
engine = batch06.engine
base = engine.base.base


class ManualCompactStatic007Batch07Error(RuntimeError):
    """Raised when strict input, layout, or candidate output drifts."""


@dataclass(frozen=True)
class Bundle:
    event: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManualCompactStatic007Batch07Error(message)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ManualCompactStatic007Batch07Error(f"candidate path escapes tmp: {resolved}") from exc
    return resolved


def non_whitespace(text: str) -> str:
    return "".join(character for character in text if not character.isspace())


def load_complete_korean_3820() -> str:
    """Load the independently preserved complete-Korean source for row 3820."""
    require(COMPLETE_KO_3820_SOURCE.is_file(), f"3820 complete Korean source missing: {COMPLETE_KO_3820_SOURCE}")
    document = json.loads(COMPLETE_KO_3820_SOURCE.read_text(encoding="utf-8"))
    entries = document.get("entries")
    require(isinstance(entries, list), "3820 complete Korean entries absent")
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("id") == 3_820]
    require(len(matches) == 1 and isinstance(matches[0].get("ko"), str), "3820 complete Korean entry drift")
    complete = matches[0]["ko"]
    require(engine.text_hash(complete) == EXPECTED_COMPLETE_KO_3820_UTF16LE_SHA256, "3820 complete Korean hash drift")
    require(base.control_signature(complete) == base.control_signature(TARGETS[3_820]), "3820 complete Korean control drift")
    return complete


def scene_index() -> Mapping[int, str]:
    index: dict[int, str] = {}
    for scene, first_id, last_id in SCENE_GROUPS:
        for entry_id in range(first_id, last_id + 1):
            require(entry_id not in index, f"scene group overlap: {entry_id}")
            index[entry_id] = scene
    require(tuple(index) == SCENE_IDS, "scene group coverage drift")
    return index


SCENE_INDEX = scene_index()


def validate_authored_targets() -> None:
    require(SCENE_IDS == tuple(range(3_689, 3_899)), "broad range drift")
    require(tuple(TARGETS) == CHANGED_IDS, "target ID order/scope drift")
    require(tuple(TARGET_LAYOUTS) == CHANGED_IDS, "target layout ID order/scope drift")
    require(set(RATIONALES) == set(CHANGED_IDS), "rationale ID scope drift")
    require(set(CHANGED_IDS).isdisjoint(RETAINED_IDS), "changed/retained scope overlap")
    require(set(CHANGED_IDS).isdisjoint(RUNTIME_HOLD_IDS), "runtime row selected without reservation evidence")
    require(set(STATIC_RETAINED_MANUAL_IDS).issubset(ENGINE_RETAINED_IDS), "static retained scope drift")
    require(set(SOURCE_COMPLETE_RESTORATION_IDS).issubset(CHANGED_IDS), "source-complete restoration scope drift")
    require(set(SOURCE_COMPLETE_RESTORATION_IDS).isdisjoint(LAYOUT_ONLY_CHANGED_IDS), "restoration/layout-only overlap")
    require(tuple(sorted(SOURCE_COMPLETE_RESTORATION_IDS + LAYOUT_ONLY_CHANGED_IDS)) == CHANGED_IDS, "change mode coverage drift")
    require(20 <= len(CHANGED_IDS) <= 40, "multi-scene target count outside policy")
    for entry_id, target in TARGETS.items():
        require("\x00" not in target, f"embedded terminator: {entry_id}")
        base.assert_no_break_inside_tag(target)
        signature = base.control_signature(target)
        require(signature["runtime_tokens"] == [], f"runtime token in target: {entry_id}")
        require(signature["printf_tokens"] == [], f"printf token in target: {entry_id}")
        require(signature["unknown_percent_count"] == 0, f"unknown percent in target: {entry_id}")
        require(signature["other_controls"] == [], f"other control in target: {entry_id}")
        metrics = base.line_metrics(target)
        require(1 <= len(metrics) <= 4, f"target line count exceeds max: {entry_id}")
        require(all(line["passes_static_patch_007"] for line in metrics), f"target fails Static Patch 007: {entry_id}")
        expected_raw, expected_effective = TARGET_LAYOUTS[entry_id]
        require(
            tuple(line["raw_g1n_width_px"] for line in metrics) == expected_raw,
            f"target raw metric drift: {entry_id}",
        )
        require(
            tuple(line["effective_width_px"] for line in metrics) == expected_effective,
            f"target effective metric drift: {entry_id}",
        )


def configure_engine() -> None:
    """Bind the committed codec/audit engine to batch07's strict input and scope."""
    engine.WORKSTREAM = WORKSTREAM
    engine.TMP_ROOT = TMP_ROOT
    engine.CANDIDATE_ROOT = CANDIDATE_ROOT
    engine.PREDECESSOR_WORKSTREAM = PREDECESSOR_WORKSTREAM
    engine.PREDECESSOR_CANDIDATE_ROOT = PREDECESSOR_CANDIDATE_ROOT
    engine.EXPECTED_PREDECESSOR_PROFILE = EXPECTED_PREDECESSOR_PROFILE
    engine.EXPECTED_OUTPUT_PROFILE = EXPECTED_OUTPUT_PROFILE
    engine.SCENE_NAME = SCENE_NAME
    # The shared metric intentionally rejects unresolved runtime-name tokens.
    # Their strings stay byte-for-byte untouched and are audited separately.
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
        signature = base.control_signature(current)
        require(signature["runtime_tokens"], f"declared runtime hold has no runtime token: {entry_id}")
        require(signature == base.control_signature(direct["jp"]), f"runtime hold KO/JP control drift: {entry_id}")
        base.assert_no_break_inside_tag(current)
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
                    language: base.control_signature(direct[language]) for language in ("jp", "en", "sc", "tc")
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
                "runtime_hold_exclusion_reason": "runtime-name token route/reservation evidence absent; no automatic reflow",
                "rationale": "Retained unchanged pending runtime-token route and reservation proof.",
                "historical_vs_current": None,
                "current_quality_conflict_check": {
                    "status": "NOT_APPLICABLE",
                    "reason": "No runtime-name reservation width has been proven for this row.",
                },
                "terminator_policy": "UTF-16LE NUL terminator is serialized by rebuild_message_table",
            }
        )
    return rows


def prepare(*, require_output_profile: bool) -> Bundle:
    configure_engine()
    complete_korean_3820 = load_complete_korean_3820()
    engine_bundle = engine.prepare(require_output_profile=require_output_profile)
    audit = copy.deepcopy(engine_bundle.audit)
    manifest = copy.deepcopy(engine_bundle.manifest)
    rows = list(audit["rows"])
    require(tuple(row["entry_id"] for row in rows) == ENGINE_REVIEW_IDS, "engine row coverage drift")
    _event, before, _raw, _profile, _predecessor_audit = load_predecessor()
    contexts, _context_profiles = base.load_direct_contexts()
    for entry_id in LAYOUT_ONLY_CHANGED_IDS:
        require(
            non_whitespace(before.texts[entry_id]) == non_whitespace(TARGETS[entry_id]),
            f"layout-only Korean text integrity drift: {entry_id}",
        )
    source_complete = TARGETS[3_820]
    require(base.control_signature(before.texts[3_820]) == base.control_signature(source_complete), "3820 control drift")
    require(base.control_signature(before.texts[3_820]) == base.control_signature(complete_korean_3820), "3820 complete Korean/current control drift")
    for required_term in (
        "미요시 유키나가",
        "아와 호소카와가",
        "관령",
        "호소카와 게이초가",
        "호소카와 스미모토",
        "가독 다툼",
        "도와 싸워",
        "권세를 얻었다",
    ):
        require(required_term in source_complete, f"3820 source-complete term absent: {required_term}")
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
        if entry_id in SOURCE_COMPLETE_RESTORATION_IDS:
            require("호소카와 스미모토" in complete_korean_3820, "3820 full-name evidence drift")
            require("가독 다툼" in complete_korean_3820 and "권세를 얻었다" in complete_korean_3820, "3820 complete-meaning evidence drift")
            row["change_mode"] = "SOURCE_COMPLETE_RESTORATION_WITH_SEMANTIC_REFLOW"
            row["source_complete_restoration_evidence"] = {
                "complete_korean_source": COMPLETE_KO_3820_SOURCE.relative_to(REPO).as_posix(),
                "complete_korean_utf16le_sha256": engine.text_hash(complete_korean_3820),
                "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
                "restored_semantic_units": list(CURRENT_QUALITY_PRESERVED[entry_id]),
                "legacy_non_whitespace_identical": False,
                "sentence_shortened_or_deleted": False,
            }
        elif row["changed"]:
            row["change_mode"] = "LAYOUT_ONLY_SEMANTIC_REFLOW"
        if entry_id in STATIC_RETAINED_MANUAL_IDS:
            row["rationale"] = STATIC_RETAINED_NOTES[entry_id]
            row["current_quality_conflict_check"] = {
                "status": "PASS_RETAINED",
                "reason": "Existing manual line breaks already follow semantic units; no cosmetic rebreak applied.",
            }
    changed_rows = [row for row in rows if row["changed"]]
    require([row["entry_id"] for row in changed_rows] == list(CHANGED_IDS), "exact multi-row audit drift")

    audit["schema"] = "nobu16.kr.pc-event-manual-compact-static007-batch07-audit.v1"
    profiles = audit["source_profiles"]
    require("strict_predecessor_batch02" in profiles, "engine predecessor profile key drift")
    profiles["strict_predecessor_6000_7999_restore"] = profiles.pop("strict_predecessor_batch02")
    profiles["complete_korean_3820"] = {
        "path": COMPLETE_KO_3820_SOURCE.relative_to(REPO).as_posix(),
        "utf16le_sha256": engine.text_hash(complete_korean_3820),
    }
    audit["source_policy"]["layout_only_non_whitespace_integrity_verified"] = False
    audit["source_policy"]["layout_only_non_whitespace_integrity_verified_ids"] = list(LAYOUT_ONLY_CHANGED_IDS)
    audit["source_policy"]["source_complete_restoration_ids"] = list(SOURCE_COMPLETE_RESTORATION_IDS)
    audit["source_policy"]["source_complete_restoration_evidence"] = {
        "complete_korean_legacy": True,
        "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
        "sentence_shortened_or_deleted": False,
    }
    audit["source_policy"]["japanese_source_line_breaks_used"] = False
    audit["source_policy"]["korean_sentence_shortened_or_deleted"] = False
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
    audit["coverage"]["source_complete_restoration_ids"] = list(SOURCE_COMPLETE_RESTORATION_IDS)
    audit["coverage"]["source_complete_restoration_count"] = len(SOURCE_COMPLETE_RESTORATION_IDS)
    audit["exact_multi_row_diff"] = changed_rows
    audit.pop("exact_two_row_diff", None)
    audit["exact_multi_row_diff_count"] = len(changed_rows)
    audit["rows"] = rows

    manifest["schema"] = "nobu16.kr.pc-event-manual-compact-static007-batch07-manifest.v1"
    manifest["exact_multi_row_diff"] = True
    manifest.pop("exact_two_row_diff", None)
    manifest["scene_groups"] = scene_coverage(rows)
    manifest["runtime_hold_excluded_ids"] = list(RUNTIME_HOLD_IDS)
    manifest["static_retained_manual_ids"] = list(STATIC_RETAINED_MANUAL_IDS)
    manifest["source_complete_restoration_ids"] = list(SOURCE_COMPLETE_RESTORATION_IDS)
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
        "source_complete_restoration_ids": list(SOURCE_COMPLETE_RESTORATION_IDS),
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
        WORKSTREAM / "build_pc_event_manual_compact_static007_batch07_v1.py",
        WORKSTREAM / "test_pc_event_manual_compact_static007_batch07_v1.py",
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
        print(json.dumps({entry_id: list(base.line_metrics(text)) for entry_id, text in TARGETS.items()}, ensure_ascii=False))
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
                "source_complete_restoration_ids": list(SOURCE_COMPLETE_RESTORATION_IDS),
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
