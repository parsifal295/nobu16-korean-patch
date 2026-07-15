#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 7 (IDs 611-655)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_msgbre_batch6 as engine  # noqa: E402


BATCH_ID = "msgbre_biographies_0611_0655.v0.7"
OVERLAY_NAME = "msgbre_ko_biographies_0611_0655.v0.7.json"
EVIDENCE_NAME = "alignment_evidence.v0.7.json"
REVIEW_NAME = "review_index.v0.7.json"
VALIDATION_NAME = "validation.v0.7.json"
STRING_COUNT = engine.STRING_COUNT
SOURCE_PINS = engine.SOURCE_PINS
SCOPE_START = 611
SCOPE_END = 655
NEXT_START_ID = 656
shared = engine.shared


TRANSLATIONS: dict[int, str] = {
    611: "가키자키 마쓰마에 가문 제6대 당주. 요시히로의 아들이다. 도쿠가와 이에야스가 내대신이 되었을 때 아버지와 함께 이에야스를 배알했다. 1600년 마쓰마에번 제2대 번주가 되었지만 아버지보다 먼저 병사했다.",
    612: "도요토미 가신. 금절렬지물사번을 맡고 분고 도미쿠 2만 석을 다스렸다. 세키가하라 전투에서 서군에 속해 미노 오가키성에 농성했으나, 동군으로 돌아선 사가라 요리후사 등에게 살해되었다.",
    613: "야마나 가신. 쓰구나리의 아들. 아버지를 죽인 다유쇼 고레요시와 싸워 그를 토벌했다. 뒤에 하시바 히데요시의 중국 정벌군에 항복해 이나바 돗토리성 공략 등에 참가했고, 이나바에서 1만 석을 받았다.",
    614: "도요토미 가신. 미쓰나리의 아들. 오다와라 정벌과 조선 출병 등에 종군해 이나바 우라즈미키야마 1만 석을 다스렸다. 세키가하라 전투에서 서군에 속해 오미 오쓰성 공격에 참가했고, 전후 자결했다.",
    615: "야마나 가신. 라쿠라쿠젠성주. 주군 오키토요가 다지마 슈고가 되자 슈고다이가 되어 영국 경영의 실권을 장악했다. 뒤에 다유쇼 고레요시와 대립하다 기습을 받고 자결했다.",
    616: "부젠의 호족. 오하타성주. 오토모 가문에 속해 반오토모 세력 노나카 시게카네와 치열하게 다퉜다. 도요토미 히데요시의 규슈 정벌 뒤 부젠에 들어온 구로다 요시타카와 싸웠으나 패해 멸망했다.",
    617: "다테 가신. 덴분의 대란 때 외삼촌 다네무네 휘하에서 활약했다. 난이 끝난 뒤 거성 가케다성을 폐성한다는 화친 조건에 불만을 품고 모반을 일으켰으나 붙잡혀 참수되었다.",
    618: "다테 가신. 아버지 시게토시는 다네시게의 아들이며, 형 시게노부는 우와지마 다테 가문을 섬겨 우와지마으로 갔다. 마술의 명수로 알려져 교토에서 여러 차례 묘기를 선보였다.",
    619: "가사이 가문 제16대 당주. 하루타네의 적자이자 데라이케성주. 아버지가 죽은 뒤 가독을 이었다. 병약한 탓에 뚜렷한 업적을 남기지 못한 채 불과 5년의 치세 뒤 병사했다.",
    620: "가사이 가문 제15대 당주. 하루시게의 둘째 아들이자 데라이케성주. 형 모리노부와 그 양자 하루키요가 모두 일찍 죽자 가독을 이었다. 쇼군 아시카가 요시하루에게서 편휘를 받았다.",
    621: "가사이 가문 제17대 당주. 하루타네의 둘째 아들이자 데라이케성주. 형 지카노부가 죽은 뒤 가독을 이었다. 다테 가문과 손잡고 오사키 가문과 싸웠으나, 오다와라 정벌에 참진하지 않아 개역되었다.",
    622: "호조 가신. 노토노카미라 칭했다. 가사하라 가문은 아버지 노부타메 때 호조 가문에 속했다고 한다. 1554년 이마가와 가문과의 가시마 전투에서 호조 우지시게 등과 함께 선진을 맡았다.",
    623: "호조 가신. 야스카쓰의 아버지. 소운 때부터 섬긴 고참 중신으로 이즈중의 필두격이었다. 우지쓰나 때 고즈쿠에성 성대에 임명되어 무사시 남부 호족으로 조직된 고즈쿠에중을 이끌었다.",
    624: "호조 가문의 가신. 마쓰다 노리히데의 아들로 가사하라 가문을 이었다. 도요토미의 오다와라 공격 때 아버지와 함께 히데요시에게 내응하려 했으나, 동생 히데하루의 밀고로 드러나 주군 우지마사에게 살해되었다.",
    625: "시나노의 호족. 시가성주. 야마노우치 우에스기 가문에 속했다. 다케다 신겐의 공격에 완강히 저항했으나 원군이 다케다군에 패해 고립되었고, 얼마 뒤 총공격을 받자 자결했다.",
    626: "가사이 가신. 오바야시성주. 가시야마 가문은 오슈 지바 가문의 일족이다. 이사와군의 종령직을 맡아 가문에서도 손꼽히는 군사력을 지녔다. 가사이·오사키 잇키의 총대장을 맡은 가시야마 아키무네의 아버지다.",
    627: "가사이 가신. 가시야마 아키요시의 넷째 아들이자 오리이 다테의 주인. 영내 굴지의 거친 무장으로 불렸고 가시야마 가문의 내란 때 가로 미타 쇼겐을 죽였다. 가사이·오사키 잇키에서는 반란군의 총수가 되었다.",
    628: "가사이 가신. 아키무네의 적자. 주가가 멸망한 뒤 난부 가문을 섬겨 이와사키성 성대를 맡았다. 와가 병란 진압 등에서 활약했으나, 강용함을 두려워한 주군 난부 도시나오에게 독살되었다.",
    629: "가사이 가신. 가시야마 아키요시의 셋째 아들이자 고야마성주. 동생 오리이 아키히사와 함께 영내 굴지의 거친 무장으로 불렸다. 1581년 가시야마 가문의 내란 때 가로 미타 쇼겐을 죽였다.",
    630: "호조 가신. 호조 우지야스가 기이에서 불러 수군을 맡겼다. 사토미 가문과의 전투에서 활약했다. 주가가 멸망한 뒤 옛 주군 우지나오를 따라 고야산으로 갔고, 우지나오가 죽은 뒤 기이로 돌아왔다.",
    631: "정체불명의 술사. 마쓰나가 히사히데 앞에서 죽은 아내로 둔갑하거나 대나무 잎을 물고기로 바꾸는 등 여러 술법을 썼다. 뒤에 도요토미 히데요시에게 책형을 받았으나 쥐로 변해 달아났다고 한다.",
    632: "우에스기 가신. 처음에는 다케다 가문을 섬겼고, 뒤에 나오에 가네쓰구의 측근이 되었다. 가네쓰구의 두터운 신임을 받아 ‘나오에 피관의 동량’이라 불렸다. 군사 면에서도 모가미 가문 공략 등에서 활약했다.",
    633: "도요토미 가신. 하리마 출신으로 시즈가타케 칠본창의 한 사람이다. 세키가하라 전투 때 서군에 속해 후시미성 공격 등에 참가했다. 전후 개역되었으나 뒤에 막신으로 등용되었다.",
    634: "도요토미 가신. 시즈가타케 칠본창의 한 사람이다. 주군 히데요리의 후견으로서 주가 존속을 위해 힘썼으나, 도쿠가와 이에야스와 내통했다는 의혹을 받아 오사카성에서 물러났다. 이후 도쿠가와 가문에 속했다.",
    635: "도요토미 가신. 가쓰모토의 동생. 오다와라 정벌 등에 종군했다. 도요토미 히데요시가 죽은 뒤 히데요리를 섬겼으나, 호코지 종명 사건에서 도쿠가와 가문과 내통했다는 의심을 받아 형과 함께 오사카성을 떠났다.",
    636: "다테 가신 오니니와 요시나오의 딸. 다테 마사무네를 뒷받침한 명장 오니니와 쓰나모토·가타쿠라 가게쓰나 등의 누나다. 마사무네의 유모와 교육계를 맡았고, 가타쿠라 가문의 지물 ‘검은 낚시종’을 고안했다.",
    637: "다테 가신. 가게쓰나의 아들. 오사카 여름 전투에서 고토 모토쓰구 등을 베는 등 활약해 도쿠가와 이에야스에게 ‘귀신’이라는 평을 받았다. 이때 사나다 유키무라의 딸 우메를 보호했고, 뒤에 아내로 맞았다.",
    638: "다테 가신. 19세에 주군 마사무네의 교육계가 되어 지략 면에서 마사무네를 보좌했다. 도요토미 히데요시의 오다와라 정벌에 참진하도록 마사무네를 설득해 다테 가문의 존속에 공헌했다.",
    639: "모리 가신. 처음에는 아와야 성을 칭했으나 주군 데루모토에게서 가타다 성을 받았다. 고바야카와 다카카게가 이요로 전봉된 뒤에는 빈고 미하라성주가 되었다. 세키가하라 전투에는 데루모토의 대리로 출진했다.",
    640: "모리 가신. 아키 사쿠라오성주를 맡아 이쓰쿠시마 신사를 포함한 신령의 관리와 지배를 담당했다. 이쓰쿠시마 전투 때 스에 하루카타에게 거짓 편지를 보내 하루카타를 이쓰쿠시마로 유인하는 데 성공했다.",
    641: "이마가와 가신. 가쓰라야마성주. 가신 저택분의 연공 감면과 영내 사찰 보호 등 영지 안에서 독자적인 정책을 폈다. 주가가 멸망한 뒤 몰락했고 다케다 신겐의 여섯째 아들 우지사다가 뒤를 이었다.",
    642: "도요토미 가신. 시즈가타케 칠본창의 한 사람. ‘침용의 사’라는 평을 받았다. 도요토미 수군의 주력으로 각지 전투에서 활약했고, 세키가하라 전투에서는 동군에 속해 이요 마쓰야마 20만 석을 받았다.",
    643: "사이토 다쓰오키와 도요토미 히데요시를 섬겨 아자이 공략과 하리마 미키성 공략에서 공을 세웠다. 오다와라 정벌 뒤 고후성주가 되었다. 분로쿠의 역 때 조선에 건너갔으나 귀국길에 병사했다.",
    644: "아마고 가신. 아마고 기요히사의 아들. 주가가 멸망한 뒤 아마고 가쓰히사가 이끈 재흥군에 호응했다. 후베야마 전투에 패해 이즈모에서 쫓겨났고, 고즈키성에서 모리의 대군에게 포위되어 자결했다.",
    645: "도요토미 가신. 시즈가타케 칠본창의 한 사람. 조선 출병에서 활약해 ‘호랑이 가토’의 일화를 남겼다. 히데요시가 죽은 뒤 이시다 미쓰나리와 대립했고, 세키가하라 전투에서 동군에 속해 히고 구마모토 52만 석을 받았다.",
    646: "‘나는 가토’라는 별명이 있던 뛰어난 닌자. 우에스기 겐신을 섬겼으나 단조의 능력을 두려워한 겐신에게 에치고에서 쫓겨났다. 이어 섬긴 다케다 신겐에게도 목숨을 노려져 변소에서 암살되었다.",
    647: "기요마사의 둘째 아들. 아버지가 죽은 뒤 도도 다카토라의 후견으로 히고 구마모토번 54만 석을 이었다. 젊은 탓에 가신단을 장악하지 못했고, 뒤에 막법 위반을 이유로 제봉되었다.",
    648: "미쓰야스의 둘째 아들. 도요토미 히데요시를 섬겼다. 세키가하라 전투에서 동군을 도와 시마즈군과 싸웠고, 전후 미나쿠치성을 공략했다. 오사카 전투에서도 공을 세워 이요 오즈성주가 되었다.",
    649: "요시아키의 적자. 아버지가 죽은 뒤 무쓰 아이즈 40만 석을 이었다. 와카마쓰성 천수각을 개수했고, 보병금을 좋아해 잇포도노라 불렸다. 가로와 대립해 아이즈 소동을 일으킨 끝에 개역되었다.",
    650: "시라카와 유키 가신. 가즈사노카미라 칭했다. 무용이 뛰어나고 선정을 베풀어 백성들이 잘 따랐다고 한다. 사타케 가문과의 전투 등에서 활약했으며, 주가가 멸망한 뒤에는 다테 가문을 섬겼다.",
    651: "데와의 호족이자 아사리 가신. 아사리 노리요리의 사위가 되어 아사리 성을 받았다. 뒤에 아사리 가문을 떠나 매사냥꾼으로서 노부나가의 아들 노부타카와 가모 우지사토 등에게 중용되었다.",
    652: "아시나 가신. 주군 모리타카가 죽은 뒤 다테 마사무네의 동생 고지로를 후계자로 세우려는 세력을 누르고, 사타케 요시시게의 둘째 아들 요시히로를 당주로 맞는 데 성공했다. 스리아게하라 전투에서 전사했다.",
    653: "오다 가신. 나가야 가게시게의 아들로 나가치카의 양자가 되었다. 양아버지가 죽은 뒤 가독을 이었다. 오사카 전투에 종군해 공을 세웠고, 양아버지처럼 다도를 좋아해 다회기에 이름을 남겼다.",
    654: "요시시게의 둘째 아들. 형 시게치카가 의절당하자 가독을 이어 히다 다카야마번주가 되었다. 광산과 신전 개발에 힘썼으며, 기근 때 가보인 다기를 팔아 영민 구제에 썼다고 한다.",
    655: "오다 가신. 아카호로슈의 한 사람. 시바타 가쓰이에를 따라 호쿠리쿠 평정에 공헌했다. 가쓰이에가 죽은 뒤 칩거했으나, 뒤에 도요토미 히데요시를 섬겼다. 다도에 뛰어나 리큐 칠철의 한 사람으로 꼽힌다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    612: ["kin_kirizaki_sashimono_tsuban_title_requires_glossary_review"],
    615: ["rakurakuzen_castle_and_tajima_office_readings_require_review"],
    626: ["isawa_soryoshoku_title_requires_glossary_review"],
    631: ["gashin_koji_legendary_magic_terms_require_review"],
    632: ["naoe_hikan_no_toryo_title_requires_glossary_review"],
    636: ["black_fishing_bell_banner_term_requires_review"],
    642: ["chinyu_no_shi_epithet_requires_glossary_review"],
    646: ["tobi_kato_epithet_requires_glossary_review"],
    649: ["ippokin_chess_term_requires_glossary_review"],
}


def _configure_engine() -> None:
    engine.SCRIPT_PATH = SCRIPT_PATH
    engine.BATCH_ID = BATCH_ID
    engine.OVERLAY_NAME = OVERLAY_NAME
    engine.EVIDENCE_NAME = EVIDENCE_NAME
    engine.REVIEW_NAME = REVIEW_NAME
    engine.VALIDATION_NAME = VALIDATION_NAME
    engine.SCOPE_START = SCOPE_START
    engine.SCOPE_END = SCOPE_END
    engine.NEXT_START_ID = NEXT_START_ID
    engine.TRANSLATIONS = TRANSLATIONS
    engine.UNCERTAINTY_FLAGS = UNCERTAINTY_FLAGS


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != len(TRANSLATIONS):
        raise ValueError("batch7 translations must exactly cover IDs 611-655")
    return ids


def build(args: argparse.Namespace) -> dict[str, Any]:
    _configure_engine()
    result = engine.build(args)
    validation_path = result["out_root"] / VALIDATION_NAME
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    validation["schema"] = "nobu16.kr.msgbre-generation-validation.v7"
    validation["scope"]["natural_boundary"] = {
        "selection_policy": "fixed_contiguous_parallel_slice",
        "previous_batch_end_id": 610,
        "next_start_id": NEXT_START_ID,
        "officer_name_ids_crosschecked": len(TRANSLATIONS) + 2,
    }
    validation["generator"] = {
        "path": SCRIPT_PATH.name,
        "sha256": engine.engine.sha256(SCRIPT_PATH.read_bytes()),
    }
    result["artifacts"]["generation_validation"] = engine.engine.write_json(
        validation_path, validation
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-sc", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "SC" / "msgbre.bin")
    parser.add_argument("--stock-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgbre.bin")
    parser.add_argument("--stock-en", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgbre.bin")
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
