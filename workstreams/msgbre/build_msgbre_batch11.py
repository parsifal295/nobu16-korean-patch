#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 11 (IDs 791-835)."""

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

import build_msgbre_batch10 as engine  # noqa: E402


BATCH_ID = "msgbre_biographies_0791_0835.v0.11"
OVERLAY_NAME = "msgbre_ko_biographies_0791_0835.v0.11.json"
EVIDENCE_NAME = "alignment_evidence.v0.11.json"
REVIEW_NAME = "review_index.v0.11.json"
VALIDATION_NAME = "validation.v0.11.json"
STRING_COUNT = engine.STRING_COUNT
SOURCE_PINS = engine.SOURCE_PINS
SCOPE_START = 791
SCOPE_END = 835
NEXT_START_ID = 836
base = engine.base
shared = engine.shared


PREVIOUS_OVERLAY_PINS: dict[str, tuple[int, int, str]] = {
    **engine.PREVIOUS_OVERLAY_PINS,
    "msgbre_ko_biographies_0746_0790.v0.10.json": (
        746,
        790,
        "6D74AE6E3D86F09C0A1356B0D25D97B1B2BEBC319A288544D31714039BAA2430",
    ),
}


TRANSLATIONS: dict[int, str] = {
    791: "호조 가신. 우지시게의 아들이다. 도요토미 히데요시의 오다와라 정벌 때 야마나카성을 지켰으나 성이 함락된 뒤 도쿠가와 가문을 섬겼다.",
    792: "호조 가신. 쓰나시게의 아들이다. 아버지를 닮은 맹장으로 다마나와성주를 지냈다. 우에스기 겐신의 간토 침공군을 물리쳤다.",
    793: "이마가와 가신, 다카텐진성주. 후쿠시마 가문의 제일 용장이라 불렸다. 이이다가와라에서 다케다 노부토라에게 죽었다는 설과 하나쿠라의 난에서 달아나다 죽었다는 설이 있다.",
    794: "아시카가 가신이자 비할 데 없는 서예가. 주군 요시테루가 죽은 뒤 마쓰나가 히사히데를 섬겼고, 뒤에 오다 노부나가와 도요토미 히데요시의 비서가 되었다.",
    795: "모리 가신. 시지 히로요시의 둘째 아들이다. 산인 지방에서 깃카와 모토하루를 섬겼다. 모리 모토나리가 죽은 뒤 가문의 사장 중 한 사람이 되었다.",
    796: "오미의 유력 호족. 에치젠에서 오다 노부나가의 길잡이를 맡았다. 혼노지의 변 뒤 도요토미 히데요시를 섬겼으나 세키가하라 전투에서 배반했다.",
    797: "오미의 유력 호족. 다네쓰나의 후계자다. 아시카가 요시하루에게서 편휘를 받기 전에는 사다쓰나라고 했다. 다카시마·엣추 방어전에서 싸우다 죽었다.",
    798: "도쿠가와 가신. 모토쓰나의 장남이다. 하타모토였으나 오미의 명문 출신이라 다이묘에 준하는 대우를 받았다. 간분 대지진으로 죽었다.",
    799: "오미의 유력 호족. 미요시 모토나가를 피해 상경에서 달아난 쇼군 아시카가 요시하루를 숨겨 주었다. 그 공으로 요시하루의 칠봉행 중 한 사람이 되었다.",
    800: "고노 가신, 수군 지휘관. 구루시마 미치후사와 무라카미 다케요시와 함께 오토모 소린의 이요 침공을 막았다. 뒤에는 오다 가문과 싸우는 모리 가문에 수군 지원을 했다.",
    801: "모리 가신. 고리야마 전투에서 34명을 베었다. 가문의 오대 행정관 중 한 사람이 되었고, 뒤에는 아시카가 요시테루에게 용맹을 칭찬받았다.",
    802: "이마가와 가신, 구노성주. 주가가 멸망한 뒤 도쿠가와 가문에 속했다. 한때 사쿠라성을 다스렸으나 뒤에 다시 구노성으로 돌아왔다.",
    803: "난부 가신. 구노헤 노부나카의 아들이다. 시바 아키자네의 딸과 혼인했으나 곧 옛 주군에게 반란을 일으켰다. 뒤에 형에게 살해되었다.",
    804: "난부 가신, 노부나카의 아들. 난부 하루마사의 둘째 딸과 혼인해 후계자가 되었다. 뒤에 형 마사자네의 반란을 도운 죄로 참수되었다.",
    805: "난부 가신. 노부자네의 장남이자 구노헤성주다. 구노헤 가문은 난부 가문의 서출 후예로 여겨졌다. 하치노헤 노부나가의 딸과 혼인했다.",
    806: "난부 가신, 노부나카의 아들. 난부 하루마사가 죽은 뒤 반란을 일으켰으나 노부나오와 도요토미 군에 맞서지 못하고 참수되었다.",
    807: "도사 이치조 가신, 구시야마성주. 조소카베 모토치카를 섬겼다. 뒤에 히사타케 지카나오의 이요 남부 원정에 따랐다가 전사했다.",
    808: "가가의 유력 호족, 야스키치성주. 처음에는 야스키치 이에나가를 섬겼으나 1550년 이에나가에게서 야스키치성을 받았다. 가가 소동 때 가가슈를 이끌었다.",
    809: "모리 가신. 노부나오의 손자다. 구로다 요시타카의 영향으로 기독교도가 되었다. 뒤에 종교에 관한 데루모토의 명령을 어기고 처형되었다.",
    810: "아키 다케다 가신. 주가와 불화해 모리 가문에 들어갔다. 딸은 모토나리의 아들 깃카와 모토하루와 혼인했다. 깃카와 군의 선봉으로 활약했다.",
    811: "쇼니 가신. 류조지 가신 오다 마사미쓰와의 싸움 등에서 여러 차례 승리했다. 뒤에 류조지 가문에 반란을 일으켰다.",
    812: "쇼니 가신. 가쓰토시의 후계자다. 아버지가 죽은 뒤 류조지 가문과 화친하고 그 가신이 되었다. 뒤에 나베시마 나오시게의 조카를 양자로 맞았다.",
    813: "기쿠치 가신, 히고 나가노성주. 뒤에 류조지 가문을 섬겼다. 도요토미 히데요시의 규슈 정벌에서 패했고, 훗날 히고 소동 때 죽었다.",
    814: "벳쇼 가신. 미키 전투에서 성을 포위했다. 패색이 짙어지자 하시바 히데요시 진영에 잠입해 그를 습격했으나 붙잡혀 죽었다.",
    815: "도사의 유력 호족, 도쿠젠성주. 처음에는 조소카베 구니치카와 싸웠으나 뒤에 그 가신이 되었다. 용맹한 무장으로 전해지지만 매우 가난했다고 한다.",
    816: "구로다 가신이자 구로다 팔호의 한 사람. 간베이의 신임을 받았고 세키가하라 전투 때 매부 모리 다헤이와 함께 분고 오토모군과 싸웠다.",
    817: "구로다 가문의 중신. 도시야스의 아들이며 이름은 도시아키라다. 평화로운 시대에 군비를 늘린 주군 다다유키에게 맞서 막부에 역모로 고발해 구로다 소동을 일으켰으나, 받아들여지지 않고 유배되었다.",
    818: "구루시마 미치후사의 손자. 오사카성과 에도성 축성에 종사하는 한편 새 가신을 발탁하고 오사카에 창고를 설치해 재정을 개선했다.",
    819: "도요토미 가신. 미치야스의 아들이다. 동생 도쿠이 미치토시와 함께 고노 가문을 떠나 히데요시의 시코쿠 정벌에 참가했다.",
    820: "사타케 가신. 전 중신 와다 아키타메를 모함한 뒤 요시시게의 측근이 되었다. 세키가하라 전투에서는 우에스기 가문을 섬겨 싸우다 죽었다.",
    821: "아키 가신. 아버지는 죽은 주군 구니토라의 시신을 고향으로 모시고 가 무덤에서 자결했다. 다네나오는 나카토미가와 전투에서 죽었다.",
    822: "오사키 가신. 구로카와 가문은 오사키 가문의 서출 후예로 다테 가문을 섬겼다. 1588년 다테 가문이 침공하자 오사키 가문 편에 섰다.",
    823: "우에스기 가신. 간바라군 북부 오쿠야마쇼의 구로카와를 다스렸다. 조조 사다노리가 반란을 일으킨 뒤 나가오 다메카게를 떠나 조조 가문으로 갔으나, 훗날 용서받고 돌아왔다.",
    824: "오노데라 가신, 구로사와성주. 아리야토게 전투에서 싸웠다. 주군이 개역된 뒤에는 사타케 가문을 섬겨 반란을 진압하고 농지 개발에 힘썼다.",
    825: "구로다 팔호의 한 사람. 아라키 무라시게에게서 구로다 간베이를 구했다. 세키가하라 전투에서 이시다 미쓰나리의 수석 가신을 물리쳤다.",
    826: "도요토미 가신. 히데요시를 책사로 섬겼고 천하 통일에 크게 공헌했다.",
    827: "우에스기 가신, 구로타키성주. 주군 하루카게에게 반란을 일으켰다가 사면받았으나 다시 반란을 일으켜 에치고 슈고에게 자결을 명받았다.",
    828: "하리마의 유력 호족. 본래 비젠 출신으로 안약을 팔아 재산을 모았다. 아들 모토타카를 고데라 가문에 출사시켜 마침내 구로다 가문의 기초를 세웠다.",
    829: "고데라 가신, 히메지성주. 하리마의 유력 호족 출신이다. 주군 마사모토의 딸과 혼인해 중신이 되었다.",
    830: "나가마사의 후계자. 나가마사는 다다유키의 능력을 의심해 다른 후계자를 세우려 했다고 한다. 뒤에 중신 구리야마 다이젠에게 맞서 구로다 소동을 일으켰으나 개역은 피했다.",
    831: "도요토미 가신. 규슈 정벌에서 싸웠다. 세키가하라 전투에서는 동군에 속했고, 전후 지쿠젠에 영지를 받았다.",
    832: "조소카베 가신, 도사 나카무라성주. 헤쓰기가와 전투에서 싸우고 우라토 소동을 진압했다. 뒤에 도도 가문을 섬겼으며 오사카 전투에서 싸우다 죽었다.",
    833: "도요토미 가신. 조부 시게하루의 뒤를 이었다. 세키가하라 전투에서 동군을 도와 호리노우치 우지요시의 성을 빼앗았다. 뒤에 야마토에 영지를 받았다.",
    834: "도쿠가와 가신. 가즈하루의 동생이다. 세키가하라 전투에서 혼다 다다카쓰 휘하로 오타니 요시쓰구와 싸웠다. 오사카 전투에서도 공을 세워 증봉을 약속받았으나, 하타모토끼리의 다툼에 휘말려 근신 처분을 받았다.",
    835: "도쿠가와 가신. 시게하루의 아들이다. 처음에는 도요토미 히데요시를 섬겼으나 세키가하라 전투에서 동군에 속했다. 전후 야마토 고세에 영지를 받았다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    793: ["fukushima_general_death_accounts_and_iidagawara_reading_require_review"],
    794: ["calligrapher_identity_and_secretary_titles_require_review"],
    797: ["takashima_ecchu_defense_context_requires_review"],
    799: ["yoshiharu_seven_intermediaries_title_requires_glossary_review"],
    801: ["koryama_battle_and_five_administrators_title_require_review"],
    803: ["shiba_marriage_and_mutiny_context_require_review"],
    808: ["yasukichi_castle_and_kaga_band_terms_require_review"],
    814: ["miki_battle_infiltration_account_requires_review"],
    816: ["kuroda_eight_tigers_and_tahei_mori_readings_require_review"],
    817: ["kuroda_unrest_and_tadayuki_context_require_review"],
    823: ["okuyamasho_kurokawa_and_jojo_rebellion_readings_require_review"],
    825: ["ishida_chief_retainer_identity_requires_review"],
    830: ["kuroda_unrest_succession_context_requires_review"],
    833: ["horinouchi_ujiyoshi_castle_reading_requires_review"],
    834: ["sekigahara_opponent_and_bannerman_dispute_context_require_review"],
}


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != len(TRANSLATIONS):
        raise ValueError("batch11 translations must exactly cover IDs 791-835")
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
    engine.PREVIOUS_OVERLAY_PINS = PREVIOUS_OVERLAY_PINS
    engine.selected_ids = selected_ids


def verify_previous_overlays() -> dict[str, dict[str, Any]]:
    _configure_engine()
    return engine.verify_previous_overlays()


def reconstruct_sc_target(sc_packed: bytes, sc_table: Any) -> dict[str, Any]:
    _configure_engine()
    return engine.reconstruct_sc_target(sc_packed, sc_table)


def build(args: argparse.Namespace) -> dict[str, Any]:
    """Build batch 11 through the proven v0.10 source-free artifact engine."""
    _configure_engine()
    result = engine.build(args)
    validation_path = result["out_root"] / VALIDATION_NAME
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    validation["schema"] = "nobu16.kr.msgbre-generation-validation.v11"
    validation["scope"]["natural_boundary"] = {
        "selection_policy": "fixed_contiguous_parallel_slice",
        "previous_batch_end_id": 790,
        "next_start_id": NEXT_START_ID,
        "officer_name_ids_crosschecked": len(TRANSLATIONS) + 2,
    }
    validation["safety"]["existing_v01_to_v10_artifacts_modified"] = False
    validation["generator"] = {
        "path": SCRIPT_PATH.name,
        "sha256": base.sha256(SCRIPT_PATH.read_bytes()),
    }
    validation["source_free_scan"]["generation_validation"] = base.script_counts(
        base.encode_json(validation).decode("utf-8")
    )
    if validation["source_free_scan"]["generation_validation"] != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError("generation validation contains source-script text")
    result["artifacts"]["generation_validation"] = base.write_json(validation_path, validation)
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
