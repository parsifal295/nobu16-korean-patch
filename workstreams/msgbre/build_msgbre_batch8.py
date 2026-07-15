#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 8 (IDs 656-700)."""

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

import build_msgbre_batch7 as engine  # noqa: E402


BATCH_ID = "msgbre_biographies_0656_0700.v0.8"
OVERLAY_NAME = "msgbre_ko_biographies_0656_0700.v0.8.json"
EVIDENCE_NAME = "alignment_evidence.v0.8.json"
REVIEW_NAME = "review_index.v0.8.json"
VALIDATION_NAME = "validation.v0.8.json"
STRING_COUNT = engine.STRING_COUNT
SOURCE_PINS = engine.SOURCE_PINS
SCOPE_START = 656
SCOPE_END = 700
NEXT_START_ID = 701
shared = engine.shared


TRANSLATIONS: dict[int, str] = {
    656: "안도 가신. 요나이자와 성주. 안도 가의 가즈노 공격에서 공을 세워 아니 군대가가 되었다. 난부 가의 공격을 격퇴하고 오다테 성 탈환에도 성공했으나, 그 전투에서 전사했다.",
    657: "후쿠시마 가신으로 시다이쇼를 지냈다. 호조인 인에이에게 창술을 배웠다. 세키가하라 전투에서 벤 적장 17명의 목에 모두 조릿대 잎을 꽂아 표식으로 삼아 ‘사사의 사이조’라는 이명을 얻었다.",
    658: "이요의 호족, 가네코 성주. 조소카베 모토치카의 시코쿠 통일에 공헌했다. 인품과 식견이 모두 뛰어난 용장으로 평가받았다. 도요토미 히데요시의 시코쿠 정벌군에 맞섰으나 패해 자결했다.",
    659: "미우라 가신으로 가가노카미라 불렸다. 주군 사다카쓰의 다카다 성 탈환 작전에 후나쓰 사다이에, 마키 나오하루 등과 함께 따랐다. 아마고 가신 우야마 히사노부가 지키는 다카다 성을 공격해 탈환에 성공했다.",
    660: "쓰가루 가신. 주군 다메노부의 창업기를 지탱한 오우라 삼로 중 한 명이다. 가네히라 가문은 오우라 일족으로, 다네사토 모리즈미가 가네히라 촌을 영유할 때 지명을 성으로 삼았다고 전해진다.",
    661: "아사쿠라 가신. 가가 잇코잇키 공격에서 아사쿠라 소테키가 병으로 쓰러지자 아사쿠라 가게타카를 보좌했다. 1560년까지 후추 부교직을 맡아 아사쿠라 가의 기반을 지탱했다.",
    662: "오다 가신. 에치젠 도네야마 전투에서 분전해 주군 노부나가에게 아시나카를 하사받았다. 혼노지의 변 뒤 오와리로 돌아가 오다 노부카쓰와 마쓰다이라 다다요시 등 역대 영주를 섬겼다.",
    663: "우에스기 가신. 아버지 히데모토는 진보 가신이었다. 오타테의 난에서 가게카쓰 측으로 활약했다. 우에스기 가의 내정과 외교를 맡아 나오에 가네쓰구와 양두 체제를 구축했고, 훗날 사누키노카미를 받았다.",
    664: "호조 가신. 우지야스 때부터 섬겨 우마마와리슈로 활약했다. 오다와라 정벌 때 하치오지 성에서 마에다·우에스기 군과 싸우다 죽은 가노 이치안 소엔과 동일 인물이라는 설도 있다.",
    665: "에도 가신. 오부 성(고우칸)의 성주이자 가로를 지냈다. 같은 가로인 에도 미치즈미와 대립해 반란을 일으켰으나 패사했다. 이 사건 뒤 에도 가는 쇠퇴의 길을 걸었다.",
    666: "기쿠치 가신. 히고 구마모토 성주. 오토모 요시나가의 차남 요시타케가 기쿠치 가에 들어간 뒤에는 요시타케의 가로가 되었다. 산조니시 사네타카에게서 《겐지 이야기》를 사들이는 등 문예에도 관심이 깊었다.",
    667: "시마즈 가신으로 가로를 지냈다. 도요토미 히데요시의 조선 파병에 종군해 이순신이 이끄는 거북선 수군을 격파했다. 류큐 원정에서는 총대장을 맡아 슈리를 점령하고 왕자를 포로로 잡았다.",
    668: "시마즈 가의 서류. 다카히사를 섬겨 여러 차례 무공을 세웠다. 가인으로도 알려졌으며, 성 안에 노래를 써 두고 도망친 적을 추격하며 화답시를 화살에 묶어 쏘았다는 일화가 전한다.",
    669: "시마즈 가신. 요시히사의 아들이며 히사타카의 아버지다. 다카히사와 요시히사를 중신으로 섬겨 사쓰마·휴가·오스미 삼주 통일에 공헌했다. 가인으로 알려진 아버지를 닮아 자신도 와카를 좋아했다.",
    670: "이세의 호족, 가부토 성주. 가부토 가는 세키 가의 서류다. 노부나가의 삼남 노부타카가 간베 가의 양자가 된 뒤부터 오다 가를 따랐으나, 아네가와 전투에서는 아자이 가에 속해 싸웠다.",
    671: "시마즈 가신. 히고 야자키 성 공격 등에서 활약했다. 사쓰마 마고시 성 공격에서 큰 공을 세워 주군 다다요시에게 포상받고, 시마즈 가의 간쿄쇼에 이름을 남긴 네 사람 중 한 명이 되었다.",
    672: "지쿠고의 호족, 가마치 성주로 무사시노카미라 불렸다. 가마치 가 적류인 시모가마치 가의 시조가 되었다. 야나가와 성을 쌓아 거성으로 삼고 오토모 가에 속해 24성주 다이묘의 기수를 맡았다.",
    673: "지쿠고의 호족, 야나가와 성주. 아키히사의 적남으로 오토모 가에 속했다. 멸망 위기에 놓인 류조지 가를 두 차례 보호했다. 미미가와 전투에 참전해 일족과 함께 전사했다.",
    674: "지쿠고의 호족, 야나가와 성주. 아키모리의 적남이다. 아버지가 죽은 뒤 가독을 이었다. 류조지 다카노부의 지쿠고 경략을 도왔으나 훗날 대립했고, 다카노부의 거성인 히젠 사가 성에 불려가 살해됐다.",
    675: "검술가. 처음에는 나가노 가를 섬겼다. 주가가 멸망한 뒤 잠시 다케다 신겐을 섬겼으나, 곧 무예 수련을 위해 낭인으로 떠돌며 신카게류를 창시했다. 제자로는 야규 무네토시 등이 있다.",
    676: "신카게류 창시자 가미이즈미 노부쓰나의 손자. 세키가하라 전투 직전 우에스기 가게카쓰의 낭인 모집에 응해 나오에 가네쓰구 휘하에 들었다. 데와 하세도 성에서 모가미 군과 싸우다 전사했다.",
    677: "아마고 가신. 1511년 후나오카야마 전투에 주군 쓰네히사와 함께 종군했다. 모리 모토나리의 이복동생 아이아이 모토쓰나를 회유해 모리 가의 분열을 꾀했으나 실패로 끝났다.",
    678: "도쿠가와 가신. 고레노리의 차남으로 도쿠가와 히데타다의 측근을 지냈다. 아버지가 죽자 이나바 시카노의 2대 번주가 되었다. 네네와 친해 그녀를 찾아가던 길에 낙마해 젊은 나이로 죽었다.",
    679: "아마고 가신. 주가가 멸망한 뒤 도요토미 가를 섬겨 시카노 성주가 되었다. 간척과 용수로 건설 등 영지 산업 진흥에 힘썼다. 주인장을 받아 시암에 무역선을 파견하기도 했다.",
    680: "히에누키 가신으로 즈쇼라 불렸다. 1540년 야소자와 씨를 대신해 가메가모리 성주가 됐다. 훗날 주가를 배반해 공격받았으나 격퇴했다. 자손은 난부 가를 섬겼다고 한다.",
    681: "아사노 가신. 세키가하라 전투 등에서 무공을 많이 세웠다. 오사카 여름의 진 가시이 전투에서 반 단우에몬을 베었으나 공은 다른 사람의 것이 됐다. 훗날 우에다 시게야스와 다투고 낭인이 되었다.",
    682: "오스미의 호족. 시마즈 가와 다투던 중 요시히사·요시히로·도시히사 삼형제가 이와쓰루기 성을 공격하자, 일본 최초의 철포끼리 맞선 전투를 벌였다. 이후 시마즈 가에 항복했다.",
    683: "롯카쿠 가신, 사다히데의 아들. 노부나가가 상경할 때 노부나가의 삼남 노부타카가 매부 간베 도모모리의 양자가 된 인연으로 오다 가에 속했다. 혼노지의 변 때에는 노부나가의 처자를 보호했다.",
    684: "오다 가신. 아버지 시게쓰나가 죽은 뒤 가독을 이어 영지를 보장받았다. 사쿠마 노부모리의 요리키로 각지에 종군했다. 혼노지의 변 뒤 오다 노부타카를 따랐고, 훗날 마에다 가를 섬겼다.",
    685: "오다 가신, 가타히데의 아들. 주군 노부나가의 딸을 아내로 맞았다. 혼노지의 변 뒤 도요토미 히데요시를 섬겨 활약하고 무쓰 아이즈 92만 석을 다스렸다. 문무에 뛰어난 재능을 히데요시도 두려워했다고 한다.",
    686: "도요토미 가신, 우지사토의 적남. 무쓰 아이즈 92만 석을 이었으나 가문 내분으로 시모쓰케 우쓰노미야 18만 석으로 감봉됐다. 세키가하라 전투에서 동군에 속해 무쓰 아이즈 60만 석으로 돌아왔다.",
    687: "히데유키의 적남. 아버지가 죽은 뒤 가독을 이었다. 증조부가 오다 노부나가, 외조부가 도쿠가와 이에야스라는 빼어난 혈통으로 태어났으나 요절했다. 적자가 없던 가모 가는 단절됐다.",
    688: "히데유키의 차남. 형 다다사토가 요절해 단절된 가모 가를 막부의 배려로 재흥하고 이요 마쓰야마 24만 석을 받았다. 그러나 다다토모도 일찍 죽고 후사가 없어 가모 가는 다시 단절됐다.",
    689: "롯카쿠 가신. 롯카쿠 군의 선봉으로 각지에 출전해 용명을 떨쳤다. 주군 요시하루가 고토 가타토요를 모살해 간논지 소동이 일어났을 때에는 요시하루와 가신단 사이의 조정역을 맡았다.",
    690: "오다 가신. 가모 사다히데의 아들로 아오치 가의 양자가 됐다. 기타바타케 가 공격 등에 종군했다. 훗날 모리 요시나리 등과 함께 사카모토 성을 지키다 아자이·아사쿠라 연합군의 공격을 받아 전사했다.",
    691: "다테 가신 다테 시게자네의 부하. 철포를 능숙하게 다뤘다. 시게자네가 여러 번 상을 내렸지만 그때마다 사양했다. 계속 사양하기 미안했는지 한 푼만 받았다고 한다.",
    692: "아케치 미쓰히데의 셋째 딸. 이름은 다마코라고도 전해진다. 호소카와 다다오키의 아내이자 독실한 기독교도였다. 세키가하라 전투 직전 서군의 인질이 되기를 거부하고 가신의 손에 최후를 맞았다.",
    693: "아사쿠라 가신. 이치조다니 사부교 중 한 명으로 국정에 참여했고, 아자이 가를 구원하려 오미에 출전하는 등 활약했다. 도네자카 전투에서 오다 군에게 죽었다고 전해진다.",
    694: "시마즈 가신, 다다카쓰의 아들. 시마즈 가의 간쿄쇼에 이름을 남긴 네 사람 중 한 명이다. 18세 때 주군 요시히사에게 슈고다이로 천거됐다고 한다. 사쓰마 오쿠치 성 공격전에서 전사했다.",
    695: "시마즈 가신, 구시키노 성주. 처음에는 삿슈 시마즈 가에 속했으나 훗날 시마즈 다다요시에게 항복해 고시키 섬에 3년간 유배됐다. 이후 가로가 되어 하쿠산 곤겐의 재흥에 힘쓰는 등 활약했다.",
    696: "시마즈 가신. 시마즈 이에히사 휘하에 속했다. 오키타나와테 전투에서 류조지 이에나리를 베어 공을 세웠다. 조선 출병에서는 이에히사의 아들 아키히사를 보좌했고, 아키히사가 병사하자 군대를 대신 지휘했다.",
    697: "오다 가신. 혼노지의 변 뒤 노부카쓰를 섬기고 그가 몰락한 뒤에는 히데요시를 따랐다. 세키가하라 전투에서는 서군에 속했으며, 패전 뒤 다테 마사무네에게 맡겨졌다가 훗날 사면되어 도쿠가와 가에 출사했다.",
    698: "이토 가신, 메이 성주로 스루가노카미라 불렸다. 주군 요시스케의 분고 퇴거를 따랐다. 가난한 이를 구제하려 술과 직물을 만들어 팔았다고 전한다. 주가가 옛 영지를 되찾자 사카타니 성주가 됐다.",
    699: "니카이도 가신. 주가가 멸망한 뒤 다테 가를 섬겼다. 가사이·오사키 잇키 때 만신창이가 되면서도 물러서지 않았다고 한다. 훗날 센다이 성과 에도 성 외호 공사를 맡았다.",
    700: "도요토미 가신, 나오에기 성주. 히데타카의 아들이다. 고마키·나가쿠테 전투와 오다와라 정벌 등에 종군했다. 조선 출병 때는 히젠 나고야 성에 주둔했고, 세키가하라 전투에서 서군에 속해 전사했다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    657: ["sasano_saizo_epithet_and_hozo_in_school_readings_require_review"],
    660: ["oura_three_elders_and_kanehira_genealogy_readings_require_review"],
    661: ["fuchu_magistrate_and_asakura_proper_name_readings_require_review"],
    663: ["uesugi_dual_leadership_and_sanuki_title_require_review"],
    666: ["kumamoto_castle_and_sanjyonishi_name_readings_require_review"],
    667: ["historical_korean_expedition_claim_requires_context_review"],
    671: ["shimazu_kankyosho_term_requires_glossary_review"],
    678: ["korenori_and_shikano_domain_readings_require_review"],
    682: ["first_matchlock_battle_claim_and_iwatsurugi_reading_require_review"],
    692: ["tamako_identity_and_hostage_event_wording_require_review"],
    694: ["shimazu_kankyosho_and_shugodai_title_require_review"],
    696: ["iehis a_and_akihisa_name_readings_require_review"],
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
        raise ValueError("batch8 translations must exactly cover IDs 656-700")
    return ids


def build(args: argparse.Namespace) -> dict[str, Any]:
    _configure_engine()
    result = engine.build(args)
    validation_path = result["out_root"] / VALIDATION_NAME
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    validation["schema"] = "nobu16.kr.msgbre-generation-validation.v8"
    validation["scope"]["natural_boundary"] = {
        "selection_policy": "fixed_contiguous_parallel_slice",
        "previous_batch_end_id": 655,
        "next_start_id": NEXT_START_ID,
        "officer_name_ids_crosschecked": len(TRANSLATIONS) + 2,
    }
    validation["safety"]["existing_v01_to_v07_artifacts_modified"] = False
    validation["generator"] = {
        "path": SCRIPT_PATH.name,
        "sha256": engine.engine.engine.sha256(SCRIPT_PATH.read_bytes()),
    }
    result["artifacts"]["generation_validation"] = engine.engine.engine.write_json(
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
