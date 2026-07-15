#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 10 (IDs 746-790)."""

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

import build_msgbre_batch9 as engine  # noqa: E402


BATCH_ID = "msgbre_biographies_0746_0790.v0.10"
OVERLAY_NAME = "msgbre_ko_biographies_0746_0790.v0.10.json"
EVIDENCE_NAME = "alignment_evidence.v0.10.json"
REVIEW_NAME = "review_index.v0.10.json"
VALIDATION_NAME = "validation.v0.10.json"
STRING_COUNT = engine.STRING_COUNT
SOURCE_PINS = engine.SOURCE_PINS
SCOPE_START = 746
SCOPE_END = 790
NEXT_START_ID = 791
base = engine.base
shared = engine.shared


PREVIOUS_OVERLAY_PINS: dict[str, tuple[int, int, str]] = {
    **engine.PREVIOUS_OVERLAY_PINS,
    "msgbre_ko_biographies_0701_0745.v0.9.json": (
        701,
        745,
        "3D8D2EE48F42ED9F2F580DA4AB0004A131198DC692FC8DEE44F6B201814ADA91",
    ),
}


TRANSLATIONS: dict[int, str] = {
    746: "아키의 유력 호족. 아마고와 오우치 가문을 거듭 배반해 집안의 분열을 불렀다. 모리 모토나리에게 아들 모토하루를 후계자로 맞도록 강요받은 뒤 살해되었다.",
    747: "모리 가신. 모리 가문이 이와미를 평정한 뒤 모노이와즈성을 쌓았다. 뒤에 후쿠야 다카카네의 공격을 받았으나 아들 쓰네이에와 함께 이를 물리쳤다.",
    748: "모리 가신. 쓰네야스의 아들이다. 야마나 도요쿠니에게 추방되어 이나바 돗토리성에 들어가 하시바 히데요시와 싸웠다. 병사들을 살리기 위해 자결했다.",
    749: "깃카와 가신. 조카 오키쓰네의 시종이 횡포를 부리자 그를 죽이고 오키쓰네를 은퇴시켰다. 뒤에 모리 모토나리의 아들 모토하루를 후계자로 맞았다.",
    750: "모토하루의 장남. 도요토미 히데요시의 규슈 정벌에 참가해 한 번도 패하지 않았다. 아버지가 죽은 뒤 가독을 이었으나 얼마 지나지 않아 죽었다.",
    751: "모토하루의 셋째 아들. 세키가하라 전투에서 서군의 패배를 예견해 모리 가문에 남게 해 달라고 교섭했다. 뒤에 배신자로 낙인찍혔다.",
    752: "벳쇼 가신, 구니구사성주. 한때 미요시 나가요시와 함께 싸웠고, 뒤에는 하시바 히데요시의 침공군과 맞섰으나 패했다. 전투 중 죽은 것으로 여겨진다.",
    753: "도요토미 가신. 이에사다의 둘째 아들이다. 세키가하라 전투 때 히메지성 유수로서 서군의 동생 고바야카와 히데아키가 입성하는 것을 거부했다. 1613년 한 해 동안 쓴 일기가 사료로 남아 있다.",
    754: "오다 노부나가를 섬겼다. 혼노지의 변 뒤 아케치 미쓰히데와 시바타 가쓰이에를 물리치고 일본 최초의 통일을 이끌었다.",
    755: "도요토미 가신. 세키가하라 전투에서 동군으로 돌아서 승리에 기여했다. 그러나 불과 2년 뒤 갑작스럽게 죽었다.",
    756: "히데요시의 이복동생. 히데요시의 오른팔로서 그를 도왔고 특히 외교에 뛰어났다. 형보다 먼저 죽었다.",
    757: "히데요시의 둘째 아들. 오사카성 포위전에서 어머니와 함께 자결했다.",
    758: "아라키 가신이자 무라시게의 측근. 주가가 몰락한 뒤 도요토미 가문을 섬겨 기노시타 성을 받고 이나바 와카사에 영지를 받았다. 세키가하라 전투 뒤 자결했다.",
    759: "도요토미 가신, 와카사 오바마성주. 세키가하라 전투 때 후시미성으로 파견되었으나 탈영해 영지를 잃었다. 훗날 현대 와카의 아버지로 불렸다.",
    760: "류조지 가신, 류조지 사천왕의 한 사람. 오키타나와테 전투에서 주군이 쓰러졌다는 소식을 듣고 적진에 돌입했다. 그의 죽음은 끝내 확인되지 않았다.",
    761: "도요토미 가신. 사다미쓰의 아들이다. 화친 교섭에서 도쿠가와와 도요토미 가문 사이의 사자를 맡았다. 오사카 여름 전투에서 싸우다 죽었다.",
    762: "도요토미 가신. 시즈가타케 전투에서 싸웠고 에치젠에 영지를 받았다. 도요토미 히데쓰구 사건에 연루되어 자결을 명받았다.",
    763: "가토 기요마사 가신, 가토 십육장의 한 사람. 처음에는 롯카쿠 요시카타를 섬겼고 겁쟁이로 알려졌으나 하치만의 가호를 받아 무적의 무사가 되었다. 기요마사의 명으로 오사카 전투에서 도요토미 편에 섰다.",
    764: "오스미 기모쓰키 가문의 서류 출신. 양가가 다투던 때 시마즈 다다요시의 도움으로 가지키성주가 되었다. 뒤에 다다요시에게 항복해 다시 가신으로 돌아갔다.",
    765: "오스미의 다이묘, 다카야마성주. 가네쓰구의 아들이다. 형 가네스케가 추방된 뒤 가독을 이었고 세키가하라 전투에서 죽었다.",
    766: "시마즈 가문의 중신. 아버지 가네히로에게서 가지키성을 이어받아 시마즈 다카히사와 요시히사를 섬겼다. 특히 가모·이토 가문과의 전투에서 활약했다.",
    767: "오스미의 다이묘, 다카야마성주. 기모쓰키 가문 최대의 전성기를 이뤘다. 시마즈 다다요시의 딸과 혼인했으나, 그의 아들 다카히사와 싸웠다.",
    768: "시마즈 가신. 기모쓰키 가네모리의 아들이다. 이주인 다다무네가 죽자 시마즈 가문은 그에게 기모쓰키 가문의 재흥을 맡겼다. 뒤에 쇼나이 반란을 진압하고 류큐에서도 싸웠다.",
    769: "시마즈 가신. 가네아쓰의 아들이다. 아버지가 죽은 뒤 기이레초 기모쓰키 가문의 제2대 당주가 되었다. 오사카 겨울 전투에 참가하려 사쓰마를 떠났으나, 양군의 화친 소식을 듣고 돌아갔다.",
    770: "오스미의 다이묘, 다카야마성주. 가네쓰구의 아들이다. 형 요시가네가 죽은 뒤 가독을 이었다. 이토 가문과 손잡고 시마즈 가문과 싸웠다.",
    771: "오스미의 다이묘, 다카야마성주. 가네쓰구의 아들이다. 이토 가문과 손잡고 휴가 오비성을 공격해 시마즈 다다치카를 추격했다.",
    772: "아시카가 가신. 요시테루의 측근으로 섬겼다. 요시아키가 쇼군이 된 뒤 노부나가에게 맞서 숨어 지냈다.",
    773: "오미 북부의 수호. 아버지 다카키요가 양동생 다카요시를 후계자로 세우려 하자 아자이 쓰케마사와 함께 그들을 몰아냈다. 당주가 된 뒤에도 쓰케마사가 실권을 쥐었다.",
    774: "도요토미 가신. 다카요시의 아들이다. 세키가하라 전투에서 동군에 속해 서군이 오쓰로 진출하는 것을 막았다.",
    775: "도요토미 가신. 다카요시의 아들이다. 시나노 이이다에 영지를 두고 세키가하라 전투에서 동군을 위해 싸웠다. 전후 형을 설득해 도쿠가와 가문을 섬기게 했다.",
    776: "다카쓰구의 아들. 오사카 겨울 전투의 화친 협정은 장모의 중재 아래 다다타카의 진영에서 맺어졌다. 도쿠가와 히데타다의 딸과 혼인했고, 모리 가문을 견제하기 위해 이즈모에 봉해졌다.",
    777: "무라카미 가신. 요시키요에게 충성을 다해 사나다 유키타카 등 반항적인 가신들과 싸웠고, 뒤에는 그와 함께 시나노를 떠났다. 아들 구니키요까지 길러 주었다.",
    778: "우에스기 가신. 아시나 사천왕 히라타 기요노리의 아들이다. 인질로 우에스기 가문에 들어가 재능을 인정받아 가게카쓰의 측근이 되었다. 가게카쓰와 사다카쓰의 신임을 받아 요네자와 총감이 되었다.",
    779: "미카와 기라 가문 제13대 당주. 형 요시사토의 뒤를 이었다. 곧 이마가와 가문에 패해 스루가 후추로 끌려갔다. 마쓰다이라 모토야스가 성인이 될 때 머리를 올려 주었다.",
    780: "미카와 기라 가문 제11대 당주. 요시모토의 아들이다. 세력이 커지던 중 이마가와의 침공으로 대관 오코치 사다쓰나가 죽어 도토미 하마마쓰의 영지에서 쫓겨났다.",
    781: "조소카베 가신. 지카사다의 후계자다. 숙부 모토치카가 모리치카를 가문의 후계자로 정한 데 불만을 품어 자결을 명받았다.",
    782: "조소카베 구니치카의 둘째 아들. 뛰어난 무장과 책사로서 형 모토치카의 오른팔이 되어 도사를 통일했다. 뒤에 병으로 죽었다.",
    783: "이토 가신, 오니가성주. 한때 시마즈군을 기습해 물리쳤다. 그러나 시마즈 가문이 주군을 분고에서 공격하자 자결을 강요받았다.",
    784: "오다 가신이자 시마의 해적. 기즈가와구치 전투 경험을 살려 철갑선을 만들고 모리 수군을 격파했다. 이 공으로 해적 다이묘라 불렸다.",
    785: "오다 가신. 어머니의 오빠 구키 요시타카의 양자가 되어 성을 이었다. 처음에는 오다 노부타카를 섬겼고, 뒤에 가토 기요마사에게서 달아났다. 이후 구로다·고바야카와·도도 가문을 섬겼다.",
    786: "시마 도바의 다이묘. 세키가하라 전투에서 아버지 요시타카와 맞서 동군에 속했다. 전후 아버지의 사면을 청했으나 이미 늦었다.",
    787: "소마 가신. 아키타네를 섬겨 나카무라성 유수를 지냈다. 나카무라성은 801년 사카노우에노 다무라마로가 스가와라 사네타카를 위해 쌓았다고 전해지며, 그곳에 거주한 첫 나카무라였다.",
    788: "아카마쓰 가신, 시카타성주. 16세의 구로다 간베이에게 재능을 인정해 주홍색 투구와 갑옷을 보내고 딸 미쓰도 시집보냈다. 성이 포위되었을 때 오다군에게 쓰러졌다.",
    789: "구로다 간베이가 15세에 맞은 아내. 구로다 나가마사의 어머니다. 정토종 신자로 법명은 쇼후쿠인이었다.",
    790: "호조 가신. 구시마 마사시게의 아들이다. 아버지가 죽은 뒤 호조 우지쓰나에게 의지했고, 우지쓰나의 딸과 혼인했다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    746: ["aki_powerful_family_and_forced_adoption_context_requires_review"],
    747: ["monoiwazu_castle_and_fukuya_name_readings_require_review"],
    749: ["okitsune_attendant_name_and_succession_context_require_review"],
    753: ["himeji_castle_chamberlain_and_1613_diary_title_require_review"],
    759: ["modern_waka_father_epithet_requires_review"],
    763: ["kato_sixteen_and_hachiman_blessing_account_require_review"],
    764: ["kimotsuki_branch_and_kajiki_castle_succession_require_review"],
    768: ["kimotsuki_revival_and_shonai_uprising_readings_require_review"],
    769: ["kiirecho_kimotsuki_branch_reading_requires_review"],
    773: ["northern_omi_governorship_and_azai_succession_context_require_review"],
    776: ["izumo_grant_and_osaka_winter_truce_context_require_review"],
    778: ["ashina_elite_four_and_yonezawa_overseer_title_require_review"],
    779: ["matsudaira_coming_of_age_haircut_term_requires_review"],
    787: ["nakamura_castle_founding_tradition_and_proper_names_require_review"],
    788: ["red_bowl_helmet_and_armor_term_requires_review"],
}


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != len(TRANSLATIONS):
        raise ValueError("batch10 translations must exactly cover IDs 746-790")
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
    """Build batch 10 through the proven v0.9 source-free artifact engine."""
    _configure_engine()
    result = engine.build(args)
    validation_path = result["out_root"] / VALIDATION_NAME
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    validation["schema"] = "nobu16.kr.msgbre-generation-validation.v10"
    validation["scope"]["natural_boundary"] = {
        "selection_policy": "fixed_contiguous_parallel_slice",
        "previous_batch_end_id": 745,
        "next_start_id": NEXT_START_ID,
        "officer_name_ids_crosschecked": len(TRANSLATIONS) + 2,
    }
    validation["safety"]["existing_v01_to_v09_artifacts_modified"] = False
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
