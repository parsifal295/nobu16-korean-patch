#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 6 (IDs 566-610)."""

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

import build_msgbre_batch5 as engine  # noqa: E402


BATCH_ID = "msgbre_biographies_0566_0610.v0.6"
OVERLAY_NAME = "msgbre_ko_biographies_0566_0610.v0.6.json"
EVIDENCE_NAME = "alignment_evidence.v0.6.json"
REVIEW_NAME = "review_index.v0.6.json"
VALIDATION_NAME = "validation.v0.6.json"
STRING_COUNT = engine.STRING_COUNT
SOURCE_PINS = engine.SOURCE_PINS
SCOPE_START = 566
SCOPE_END = 610
NEXT_START_ID = 611
shared = engine.shared


TRANSLATIONS: dict[int, str] = {
    566: "야마토의 국인. 이에사카의 셋째 아들이자 야마토 국슈였다. 이에히로의 동생이라고 한다. 처음에는 나라하라 성을 칭했다. 이치오 신스케의 명으로 조카 이에타카를 모살하고 오치 가문의 종령이 되었다.",
    567: "오다 노부나가의 숙모. 도야마 가게토의 아내다. 후사 없이 남편이 병사하자 이와무라성주가 되었다. 다케다 신겐의 상락 작전이 시작되자 아키야마 노부토모와 혼인하고 다케다 가문에 귀순했다.",
    568: "다테 가신. 주군 마사무네의 측근이었다. 조선 출병 때 도요토미 히데요시의 애첩 고노마에를 하사받아 마사무네의 노여움을 사고 출분했다. 뒤에 돌아와 국로로서 국정에 관여했다.",
    569: "다테 가신. 다네무네의 아들 모리시게가 고쿠분 가문에 입양될 때 고쿠분 가문으로 가 정무를 맡았다. 뒤에 평정역이 되었다. 히토토리바시 전투 때 고령에도 후군을 맡아 전사했다.",
    570: "사타케 가신. 요시시게와 요시노부 두 대를 측근으로 섬기며 외교에서 중책을 맡았다. 지행 교체 때 와다 아키타메·히토미 후지미치와 함께 요시노부의 삼봉행으로 활약했다.",
    571: "이이 가신. 마사나오의 적자. 당주 나오치카를 참언으로 모살하고 이이 가문의 실권을 장악해 전횡을 일삼았다. 그러나 이에야스의 명을 받은 이이노야 삼인중에게 패해 처형되었다.",
    572: "다치바나 가신. 통칭 이즈미. 유후 고레노부와 함께 다치바나 가문의 양익으로 활약했다. 조선 출병에서 용명을 떨쳤다. 세키가하라 전투로 주가가 개역된 뒤에는 가토 기요마사를 섬겼다.",
    573: "도요토미 가신. 오다와라 정벌 등에 종군해 단바 후쿠치야마 4만 석을 다스렸다. 세키가하라 전투에서 서군에 속해 다나베성을 함락했으나, 서군 주력이 패하자 개성한 뒤 자결했다.",
    574: "히타치의 호족. 누카다성주. 사타케 가문에 속했으나 자립성이 강해 여러 번 주가에 반항했다. 뒤에 모반을 일으켰으나 패해 마쓰다이라 다다테루 등을 섬겼다. 그림에 뛰어났다고 한다.",
    575: "오노데라 가문 제13대 당주. 다네미치의 적자. 아버지가 죽은 뒤 한때 다이호지 가문에 의지했으나, 뒤에 원수 오와다 미쓰모리 등을 멸하고 요코테성으로 돌아왔다. 오노데라 가문의 전성기를 열었다.",
    576: "오노데라 가문 제14대 당주. 데루미치의 둘째 아들. 도요토미 히데요시의 오다와라 정벌에 참진해 영지를 안도받았다. 세키가하라 전투에서 도쿠가와 가문의 출진 요청을 무시해 전후 개역되었다.",
    577: "오노데라 가신. 데루미치의 아들. 모가미 가문과의 전투에서 활약했다. 세키가하라 전투에서는 모가미의 대군과 싸우며 거성 오모리성을 사수했고, 전후 형 요시미치와 함께 쓰와노로 유배되었다.",
    578: "오노데라 가문 제12대 당주. 야스미치의 적자. 처음에는 상경해 쇼군 가문을 섬겼으나 아버지의 죽음으로 귀국해 가독을 이었다. 뒤에 권력 투쟁에 휘말려 가신들에게 살해되었다.",
    579: "사타케 일문 사타케니시 가문의 당주. 사타케 요시아키의 셋째 아들 요시무네의 아들이다. 사타케 가문의 아키타 전봉 뒤 아사리 잔당의 반란을 진압했다. 난부·쓰가루 가문을 견제하는 오다테성을 맡았다.",
    580: "도쿠가와 가신. 고슈류 병학자이며 마사모리의 아들이다. 주군 히데타다의 고쇼가 되었으나 뒤에 출분했고, 오사카 전투 뒤 귀참했다. 고슈류 병학을 집대성해 많은 제자를 가르쳤다.",
    581: "야마노우치 우에스기 가신. 아내는 나가노 나리마사의 여동생이다. 일족의 모반으로 유랑하다 다케다 신겐에게 속했다. 우에노 공략에 공헌해 니시우에노 선방중의 필두가 되었고, 나가시노 전투에서 전사했다고 한다.",
    582: "다케다 가신. 고요 오명신 중 한 사람이다. ‘귀호’라는 별명으로 불리며 평생 36장의 감장을 받았다. 말년에는 고사카 마사노부의 부장을 맡았고, ‘제 분수를 잘 알라’는 유언으로 유명하다.",
    583: "다케다 가신. 도라마사의 아들. 분고노카미라 칭했다. 처음에는 가이즈성의 성번을 맡았으나 아버지가 죽은 뒤 이를 그만두고 하타모토 아시가루 대장으로서 기마 3기와 아시가루 10명을 이끌었다.",
    584: "다케다 가신. 노리시게의 아들. 니시우에노 선방중의 주력으로 활약했다. 주가가 멸망한 뒤에는 호조 가문을 섬겼고, 호조 가문이 멸망하자 우에다성주 사나다 마사유키를 찾아가 보호를 받았다.",
    585: "시마의 해적. 이세 기타바타케 가문에 속했다. 구키 요시타카에게 패해 시마에서 쫓겨났으나 다케다 신겐의 초빙으로 다케다 가문의 선대장이 되었다. 다케다 멸망 뒤에는 도쿠가와 가문에서 선수대장을 맡았다.",
    586: "도쿠가와 가신. 가게타카의 아들. 선두를 맡아 사가미·가즈사 두 구니에서 3천 석을 받았다. 오사카 겨울 전투에 출진해 오노 하루나가의 관선과 조선을 각각 두 척씩 빼앗는 공을 세웠다.",
    587: "다케다 가신. 군장을 붉은색으로 통일한 부대를 이끌어 ‘가이산의 맹호’라 불렸다. 신겐의 장남 요시노부의 후견을 맡았으나, 요시노부 모반 미수 사건의 책임을 지고 자해했다.",
    588: "다케다 가신. 다케다 사명신의 한 사람. 형 오부 도라마사와 마찬가지로 군장을 붉은색으로 통일했다. 내정·군사·외교 전반에서 신겐을 보좌했으며 나가시노 전투에서 온몸에 총탄을 맞고 전사했다.",
    589: "시모쓰케의 호족. 유키 마사토모의 둘째 아들로 오야마 마사나가의 양자가 되었다. 형 유키 마사카쓰의 후원을 받아 오야마 가문의 위세를 되찾았고, 호조 가문과도 손잡아 영국을 안정적으로 다스렸다.",
    590: "시모쓰케의 호족. 다카토모의 적자. 동생 유키 하루토모와 협력해 우에스기·호조 가문과 손잡고 오야마 가문의 명맥을 지켰다. 그러나 도요토미 히데요시의 오다와라 정벌 때 호조 편에 서 영지를 잃었다.",
    591: "기이의 호족. 시모쓰케 오야마 가문의 서류라고 한다. 도요토미 히데요시의 기슈 정벌군에 항복해 본령을 안도받았다. 뒤에 세키가하라 전투에서 서군에 속해 개역되었고, 오사카 겨울 전투에서 전사했다.",
    592: "다케다 가신. 데와노카미 노부아리의 아들. 투석에 능한 부대를 이끌고 여러 전투에서 활약했다. 오다 노부나가의 가이 침공군에 항복했으나, 주군 가쓰요리가 죽은 뒤 배신자로 몰려 참수되었다.",
    593: "다케다 가신. 엣추노카미 노부아리의 아들로 데와노카미라 칭했다. 시가성 공략과 우에다하라 전투 등에서 활약했다. 도이시성 공략전에서 중상을 입고 죽었으며, 장례에는 1만 명이 참석했다고 한다.",
    594: "다케다 가신. 사나다 마사유키의 맏딸 무라마쓰도노를 아내로 맞았다. 다케다 가문이 멸망한 뒤에는 사나다 가신이 되었다. 오사카 전투에서는 노부유키 대신 출진한 노부요시·노부마사를 보좌했다.",
    595: "아소 가신. 히고 미후네성주. 오토모 가문과 손잡고 류조지·시마즈 가문과 외교 교섭을 벌이며 아소 가문의 존속에 힘썼다. 시마즈에 속한 사가라 요시히로의 공격을 받았으나 이를 격퇴했다.",
    596: "아소 가신. 히고 미후네성주이며 소운의 아들이다. 시마즈군에 패해 화친했지만 오토모 가문과의 연락을 경계받아 히고 야쓰시로에 억류되었다. 국인 잇키에 가담했다가 패주하던 중 살해되었다.",
    597: "휴가의 호족. 아소 고레나가에게 쫓겨 휴가로 달아난 아소 고레토요를 보호했다. 1517년 고레나가를 물리치고 고레토요를 아소령으로 복귀시켰으며, 이후 아소 가신이 되었다.",
    598: "고노 가신. 고테가타키성주를 지냈다. 1553년 오노 도시나오 등의 공격을 받아 속성 오쿠마성으로 달아났다. 뒤에 오쿠마성도 공격받았으나 분전해 이를 물리쳤다.",
    599: "아자이 가신. 화가 가이호 유쇼의 아버지다. 도요토미 히데요시가 ‘우리 군법의 스승’이라 칭한 용장으로 무샤부교를 맡아 각지에서 활약했다. 주가가 멸망할 때 전사했으며 ‘가이·아카·아메 삼장’의 한 사람이다.",
    600: "호소카와 가신. 미쓰카게의 아들. 호소카와 가문의 가독을 두고 스미모토와 다카쿠니가 다툴 때 다카쿠니를 지지했다. 다카쿠니가 몰락한 뒤에는 스미모토의 아들 하루모토를 섬기는 등 가가와 가문의 존속에 힘썼다.",
    601: "아키 다케다 가신. 아키 야기성주. 뒤에 고이 나오유키 등과 함께 주가를 배반하고 모리 가문에 속했다. 이쓰쿠시마 전투 때는 진언사원 도린보와 함께 니호성의 성번을 맡았다.",
    602: "호소카와 가신. 아마기리성주. 주가가 몰락한 뒤 미요시 가문을 섬겼다. 뒤에 오다 노부나가와 통했으나 조소카베 모토치카의 사누키 침공군에 항복하고, 모토치카의 둘째 아들 지카카즈를 양자로 삼아 가독을 넘겼다.",
    603: "우에스기 가신. 겐신에게 ‘에치고 칠군에서 그를 당할 자는 없다’는 평을 받은 가문의 으뜸 용장이다. 간토 경략에서는 호조 가문과의 에쓰소 동맹을 성립시키는 등 외교에서도 활약했다.",
    604: "가키자키 가신. 다카히로의 아들이며 미쓰히로의 아들이라고도 한다. 아버지가 죽은 뒤 가독을 이어 가쓰야마 다테의 주인이 되었다. 뒤에 모반을 일으켜 사촌 스에히로와 싸웠으나 패해 살해되었다.",
    605: "가키자키 가문 제4대 당주. 요시히로의 아들. 선조 때부터 대립하던 아이누와 화친하고 에조 상선 왕래 제도를 정했다. 이 정책으로 에조치 영주로서의 지위를 굳혔다.",
    606: "가키자키 가문 제3대 당주. 가키자키 시조 노부히로가 아이누의 수령 고샤마인을 죽인 탓에 원한에 불타는 아이누 대군이 자주 내습했다. 평생을 전쟁 속에서 보냈다고 한다.",
    607: "스에히로의 아들. 한때 형 요시히로의 임시 양자가 되었다. 요시히로 이후 세 대에 걸쳐 번정을 보좌했다. 역대 번주의 두터운 신임을 받았고, 자손들도 중신으로서 번정에 관여했다.",
    608: "가키자키 가문 제5대 당주. 스에히로의 아들. 도요토미 히데요시에게 접근해 에조치의 교역권을 얻어 독립 영주가 되었다. 1599년 도쿠가와 이에야스에게 계보를 바치고 마쓰마에 성으로 고쳤다.",
    609: "가키자키 마쓰마에 가문 제7대 당주. 모리히로의 아들. 할아버지 요시히로의 후견으로 가독을 이었고, 뒤에 에도 막부에게 정식 후계자로 인정받았다. 요시히로가 죽은 뒤 마쓰마에번 제3대 번주가 되었다.",
    610: "마쓰마에번 가로. 스에히로의 열한째 아들로 일가를 일으켜 가신이 되었다. 제4대 번주 우지히로를 집에서 대접하던 중 우연히 불이 나자 그 죄를 짊어지고 불길 속으로 들어가 죽었다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    566: ["ochi_genealogy_and_ichio_shinsuke_readings_require_review"],
    568: ["kono_mae_proper_name_reading_requires_review"],
    582: ["koyo_five_generals_and_devil_tiger_epithet_require_glossary_review"],
    595: ["sagara_yoshihi_reading_requires_officer_catalog_review"],
    599: ["kai_aka_ame_three_generals_term_requires_glossary_review"],
    603: ["etsuso_alliance_term_requires_glossary_review"],
    604: ["kakizaki_genealogy_readings_require_review"],
}


def _selected_ids_for_batch() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != len(TRANSLATIONS):
        raise ValueError("batch6 translations must exactly cover IDs 566-610")
    return ids


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
    engine.selected_ids = _selected_ids_for_batch


def selected_ids() -> list[int]:
    return _selected_ids_for_batch()


def build(args: argparse.Namespace) -> dict[str, Any]:
    """Build batch 6 with the proven v0.5 source-free artifact engine."""
    _configure_engine()
    result = engine.build(args)

    validation_path = result["out_root"] / VALIDATION_NAME
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    validation["schema"] = "nobu16.kr.msgbre-generation-validation.v6"
    validation["scope"]["natural_boundary"] = {
        "selection_policy": "fixed_contiguous_parallel_slice",
        "previous_batch_end_id": 565,
        "next_start_id": NEXT_START_ID,
        "officer_name_ids_crosschecked": len(TRANSLATIONS) + 2,
    }
    validation["safety"]["existing_v01_to_v05_artifacts_modified"] = False
    validation["generator"] = {
        "path": SCRIPT_PATH.name,
        "sha256": engine.sha256(SCRIPT_PATH.read_bytes()),
    }
    result["artifacts"]["generation_validation"] = engine.write_json(
        validation_path, validation
    )
    return result


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
