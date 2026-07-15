#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 9 (IDs 701-745)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
TOOLS_DIR = SCRIPT_PATH.parents[2] / "tools"
sys.path.insert(0, str(WORKSTREAM_DIR))
sys.path.insert(0, str(TOOLS_DIR))

import build_msgbre_batch1 as base  # noqa: E402
import build_msgbre_batch8 as engine  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "msgbre_biographies_0701_0745.v0.9"
OVERLAY_NAME = "msgbre_ko_biographies_0701_0745.v0.9.json"
EVIDENCE_NAME = "alignment_evidence.v0.9.json"
REVIEW_NAME = "review_index.v0.9.json"
VALIDATION_NAME = "validation.v0.9.json"
STRING_COUNT = base.STRING_COUNT
SOURCE_PINS = base.SOURCE_PINS
SCOPE_START = 701
SCOPE_END = 745
NEXT_START_ID = 746
shared = base


# The prior overlays are pinned so this batch cannot silently overlap or alter
# an already translated coordinate.  They are source-free public artifacts.
PREVIOUS_OVERLAY_PINS: dict[str, tuple[int, int, str]] = {
    "msgbre_ko_biographies_0000_0128.v0.1.json": (
        0,
        128,
        "DDD87FDF972F4EE907D310387074D0879E620C61B15C26B7F8A7FBA40BE52E00",
    ),
    "msgbre_ko_biographies_0129_0250.v0.2.json": (
        129,
        250,
        "FDB2511970F1E8CEF194E661CBCE3F8D912B372382BCFD89129FD1F8B309A4D3",
    ),
    "msgbre_ko_biographies_0251_0350.v0.3.json": (
        251,
        350,
        "1253609BC246DB4A63D1A5658476756AB89A0660FA683262CFFA444E3678132B",
    ),
    "msgbre_ko_biographies_0351_0457.v0.4.json": (
        351,
        457,
        "30E38BE8C8F0D0E48FAFB828A88765AFF52BF607F1D8D22985E88CD0B810109E",
    ),
    "msgbre_ko_biographies_0458_0565.v0.5.json": (
        458,
        565,
        "941D6B235708E4E8247CD0E4508DBDADBBA5D46A6A7F5406F047C4187B19A8F0",
    ),
    "msgbre_ko_biographies_0566_0610.v0.6.json": (
        566,
        610,
        "0FB3F6F777E5110507EB4782C5B7C5E2B61EC50FBF9E8314E5FF2491C9D6ACD2",
    ),
    "msgbre_ko_biographies_0611_0655.v0.7.json": (
        611,
        655,
        "82FCFE650D8AA0EBDC70AFEEFEDE2EE14049AB0EB1979464ACBDD10B69F9B72C",
    ),
    "msgbre_ko_biographies_0656_0700.v0.8.json": (
        656,
        700,
        "6791F39371E7C34F2792AE03EB88CD3CEB0FA0980D21178EFF4A86B7793063BA",
    ),
}


TRANSLATIONS: dict[int, str] = {
    701: "오다 가신. 흑모의중의 수장을 지냈다. 노부나가의 적자 노부타다를 보좌했다. 가이 평정전에서 활약해 가이 일국을 받았으나, 혼노지의 변 뒤 가이의 국인 잇키에 살해되었다.",
    702: "아마고 가신. 쓰네히사 때부터 활약했고 하야시노성 성대로서 미마사카 방면군을 지휘했다. 주가가 멸망한 뒤 다치하라 히사쓰나와 재흥군을 일으켰으나, 갓산토다성 공략 중 병으로 쓰러져 죽었다.",
    703: "오미 출신의 우에스기 가신. 겐신이 상경할 때 초빙되어 따랐다. 호쿠리쿠 공략에서 활약했고 마쓰쿠라성주가 되어 노부나가군과 싸웠다.",
    704: "사나다 가신. 마사유키의 사촌이다. 나가시노 전투에서 형을 잃고 가독을 이었다. 세키가하라 전투 때 사나다 부자의 회담을 엿보다가 마사유키가 던진 게타에 맞아 앞니가 부러졌다고 한다.",
    705: "나미오카 기타바타케 가신. 도모나가의 아들이다. 단절되었던 가와라 고쇼를 이었고 《쓰가루 군추 묘지》를 편찬했다. 뒤에 조카와 대립해 그를 죽였으나, 조카의 동생에게 살해되었다.",
    706: "다테 가신. 산술과 수리에 정통했다. 기타카미강 개수 공사를 비롯한 여러 토목 사업을 맡아, 실질 200만 석이라 불린 센다이번의 경제 기반을 닦았다.",
    707: "구로다 가신이자 구로다 이십사기의 한 사람. 시즈가타케 전투에서 첫 출전했고 규슈 정벌과 기이 나가후사와의 전투에서 활약했다. 세키가하라에서 시마 사콘을 토벌하는 등 무공이 뛰어나 주홍 갑옷을 허락받았다.",
    708: "도요토미 가신. 본래 아와지의 국인이었다. 모리·조소카베 가문을 따르며 오다·도요토미 가문과 싸웠으나, 시코쿠 정벌 뒤 도요토미에 귀순했다. 규슈와 오다와라 원정에서 수군으로 활약했다.",
    709: "벳쇼 가신, 간키성주. 간키 가문은 아카마쓰 가문의 서류다. 하시바 히데요시의 주고쿠 정벌군에 완강히 저항했으나 패전해 전사했고, 거성은 불타 장병 대부분이 불에 타 죽었다고 한다.",
    710: "나가시마 간쇼지의 승려. 부친 쇼케이의 뒤를 이어 사찰의 수장이 되었다. 혼간지 겐뇨의 격문에 호응해 노부나가와 맞서 문도를 이끌었으나, 의문의 급사를 맞았다.",
    711: "렌준의 손자이며 이세 나가시마 간쇼지의 주지다. 일향종 문도를 이끌고 노부나가의 토벌군에 격렬히 저항했으나, 초토화 작전에 패해 기소강에 몸을 던졌다.",
    712: "혼간지 제8대 법주 렌뇨의 여섯째 아들. 오쓰 겐쇼지를 거쳐 문도들의 요청으로 가와치 겐쇼지의 주지가 되었다. 이세 나가시마에 간쇼지를 세우는 등 혼간지 발전에 기여했다.",
    713: "사나다 유키타카의 동생이자 마사유키의 숙부. 우미노 가문의 지족인 간바라 가문에 양자로 들어갔다. 일찍부터 다케다 가문에 신종해 유키타카와 함께 선방중의 한 부대를 맡아 신겐의 시나노 진출에 공헌했다.",
    714: "이세의 호족, 간베성주. 오다 노부타카를 양자로 삼았다. 뒤에 노부나가에게 히노성에 유폐되었으나, 노부타카가 시코쿠로 출진할 때 용서받아 유수역을 맡았다.",
    715: "사이토 도산의 딸 노히메. 부친과 오다 가문이 화친했을 때 노부나가에게 시집갔다. 혼노지의 변 뒤에는 노부카쓰를 의지해 오와리에 화장령을 받고 아즈치도노라 불렸다고 한다.",
    716: "기이 우쓰노미야 가문 제14대 당주. 오우치 가문을 섬겼다. 쇼니·오토모 가문과 손잡고 주군에 맞섰으나, 일족 사다 도시카게의 공격을 받아 패배해 항복했다. 이후 다시 오우치 가문을 따랐다.",
    717: "기이 우쓰노미야 가문 제15대 당주. 마사후사의 아들이다. 일찍 아들 시게후사에게 가독을 넘겼다. 시모쓰케 우쓰노미야 가문의 후계 문제에 두 차례 관여했고, 훗날 시게후사와 함께 구로다 나가마사에게 살해되었다.",
    718: "기이 우쓰노미야 가문 제16대 당주. 나가후사의 아들로 오토모·시마즈 가문을 섬겼다. 뒤에 도요토미에 굴복했으나 이요 전봉을 거부하고 반란을 일으켜 구로다 나가마사에게 살해되었다.",
    719: "다케다 신겐의 다섯째 딸. 다케다·우에스기 동맹에 따라 우에스기 가게카쓰에게 시집갔다. 미모와 총명을 겸비해 가이 고젠이라 불리며 귀하게 여겨졌다고 한다.",
    720: "오토모 요시나가의 둘째 아들. 명문 히고 기쿠치 가문을 이었다. 오우치 가문과 함께 형 요시아키에게 맞섰으나 패했고, 뒤에 조카 소린에게 살해되었다.",
    721: "호소카와 가신, 시기산성주. 주군 하루모토를 따라 옛 주군 하타케야마 요시노부를 자해하게 하고 미요시 모토나가를 죽였다. 뒤에 하루모토와 대립해 가와치 다이헤이지 전투에서 패사했다.",
    722: "쓰쓰이 가신. 쓰쓰이 준케이를 따라 마쓰나가 히사히데와 공방전을 벌였다. 뒤에 도요토미 가문을 섬겼고, 세키가하라 때는 시마 사콘 등과 함께 서군에 참가했다. 목숨을 건져 난부 가문에 맡겨졌다.",
    723: "데와의 호족. 도키히데의 아들로 다이호지 가문과 모가미 가문 사이에서 거취를 망설였다. 주고리가하라 전투 뒤 우에스기 가문을 따랐고, 1601년 거성 간논지성을 버리고 요네자와로 갔다고 한다.",
    724: "데와의 호족. 16세기 후반 아쿠미군에 간논지성을 쌓아 거성으로 삼았다. 오우라성주 다이호지 가문을 섬겨 약 2천5백 석을 지행했다고 한다.",
    725: "시나노 기소다니의 호족. 요시아리의 적장자다. 무라카미 요시키요·오가사와라 나가토키·스와 요리시게와 함께 시나노 사대장이라 불렸다. 신겐의 공격에 완강히 저항했으나 패해 항복했다.",
    726: "시나노 기소 계곡의 국인. 온화한 성품으로 알려졌다. 부친 요시모토 때부터 적대하던 히다 미키 가문과의 관계를 고쳐 영지를 안정시켰고, 풍류 태수라 불렸다.",
    727: "시나노 기소다니의 호족. 요시야스의 적장자다. 신겐의 딸을 아내로 맞았으나 뒤에 노부나가와 내통해 다케다 가문 멸망의 원인을 만들었다. 혼노지의 변 뒤에는 이에야스를 섬겨 시모사로 전봉되었다.",
    728: "도쿠가와 가신. 요시마사의 적장자다. 아버지 사후 가독을 이었으나 난폭한 행동이 잦아 숙부 요시토요를 살해한 죄로 개역되었다. 뒤에 교토에서 삭발하고 각지를 떠돌았다.",
    729: "난부 가신. 노부치카의 아들이다. 구노헤 마사자네의 난 뒤 무쓰 데라다성주가 되어 데라다 기타 가문을 세웠다. 아버지의 하나마키 기타 가문이 단절됐을 때도 뒤를 잇지 않았으며, 오사카 전투에 종군했다.",
    730: "난부 가신, 겐요시성주. 하루마사 사후의 가문 소동에서 노부나오를 지지해 노부나오의 필두 가로로 활약했다. 전투에 나설 때는 반드시 작은 관음상을 상투 속에 넣었다고 한다.",
    731: "난부 가신. 노부치카의 양자다. 주군 도시나오와 불화해 출분했다. 오사카 전투에서는 도요토미 편에 서 화려한 갑옷을 입고 활약해 난부의 빛나는 무사라 불렸다.",
    732: "난부 가신. 노부치카의 아버지다. 난부 가문 제21대 당주 노부요시의 적자였으나, 노부요시가 죽은 다음 날 태어나 가독을 이을 수 없었고 어머니 쪽의 기타 가문으로 내몰렸다고 한다.",
    733: "아소 가신, 히고 이시비쓰성주. 오토모 가문과 친교를 맺고 부젠에 군사를 보냈다. 시마즈의 히고 침공 때 항복했으나 오토모파인 아들 시게요시와 다투었고, 뒤에 가토 기요마사를 섬겼다.",
    734: "우에스기 가신. 다카히로의 아들이다. 부친과 함께 우마야바시성에 머물며 겐신의 간토 경략을 도왔다. 오타테의 난 때 가게토라 편의 핵심을 맡았으나, 뒤에 가게카쓰에게 암살되었다.",
    735: "우에스기 가신. 우마야바시성주를 지내며 간토 경략을 담당했다. 다케다 신겐·호조 우지야스 등의 권유에 넘어가 여러 차례 모반했으나, 그때마다 용서받아 복귀했다.",
    736: "모가미 가신으로 다이가쿠라 불렸다. 치수 공사로 쇼나이 평야의 물 부족을 해소했고, 이 보는 다이가쿠보라 불렸다. 요시아키에게 쇼나이 후세의 보배라며 극찬받았다.",
    737: "사이온지 가신, 가부토노모리성주. 사이온지 십오장의 한 사람이다. 기씨의 후예로 기 쓰네야스라고도 했으며, 그의 치세에 기타노카와노쇼가 번성해 두 마을로 나뉘었다고 한다.",
    738: "사이온지 가신, 미타키성주. 사이온지 십오장의 한 사람이다. 조소카베 가신 하카와 겐바의 딸을 아내로 맞았으나, 뒤에 겐바가 모반을 꾀해 모토치카의 공격을 받고 패사했다.",
    739: "이세 국사 기타바타케 가문 제8대 당주. 하루토모의 아들이다. 노부나가에게 패해 그의 둘째 아들 노부카쓰를 양자로 삼았으나, 뒤에 살해되었다. 쓰카하라 보쿠덴에게 비전 이치노타치를 전수받았다.",
    740: "나가노 구도 가문 제16대 당주. 기타바타케 도모노리의 아들이다. 화친에 따라 나가노 가문에 양자로 들어갔다. 아버지와 함께 노부나가의 이세 침공에 맞섰으나 노부카쓰에게 살해되었다.",
    741: "이세 국사 기타바타케 가문 제9대 당주. 도모노리의 아들이다. 아버지가 노부카쓰에게 살해된 뒤 다키가와 가즈마스에게 맡겨져 아노군 가와치에 3년간 유폐되었다. 뒤에 풀려났으나 이내 병사했다.",
    742: "도모후사의 적장자. 노부카쓰가 기타바타케 일족을 모살했을 때 화를 피한 어머니가 도피처에서 낳았다. 각지를 떠돌다 쓰가루 가문의 객분이 되어 가문 재흥을 꾀했으나 이루지 못했다.",
    743: "이세 국사 기타바타케 가문 제7대 당주. 이세 신궁의 문전 마을 우지야마다의 사람들, 이른바 야마다 삼방과 대립해 오랫동안 항쟁을 이어 갔다. 궁마의 달인이자 와카와 서예에 능했다.",
    744: "휴가의 호족. 이토 가문과 손잡고 혼고 가문 등과 싸웠다. 그러나 후계자 문제를 둘러싼 분쟁에서 기타하라 가문이 이토 가문에 탈취당했고, 자신도 이토 가신의 흉기에 쓰러졌다.",
    745: "노부나가의 측실. 이코마 이에무네의 딸로 노부타다·노부카쓰·도쿠히메를 낳았으나 산후 회복이 나빠 세상을 떠났다. 노부나가의 실질적인 정실이었다고도 한다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    701: ["black_mother_cloak_corps_title_requires_glossary_review"],
    702: ["rinya_castle_and_gassantoda_campaign_readings_require_review"],
    705: ["tsugaru_genealogy_title_and_kinship_readings_require_review"],
    707: ["kuroda_twenty_four_and_nagafusa_castle_readings_require_review"],
    710: ["ganshoji_monzaki_office_and_death_account_require_review"],
    712: ["ganshoji_and_kenshoji_institutional_titles_require_review"],
    713: ["kanbara_branch_and_unno_lineage_readings_require_review"],
    715: ["nohime_later_life_and_cosmetic_fief_wording_require_review"],
    723: ["jugorigahara_and_kannonji_castle_readings_require_review"],
    729: ["terada_northern_branch_and_hanamaki_branch_wording_require_review"],
    736: ["daigaku_weir_epithet_requires_glossary_review"],
    737: ["saionji_fifteen_commanders_and_kitano_kawa_estate_readings_require_review"],
    739: ["one_sword_secret_transmission_term_requires_review"],
    741: ["ano_district_kawachi_detention_location_requires_review"],
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
        raise ValueError("batch9 translations must exactly cover IDs 701-745")
    return ids


def verify_previous_overlays() -> dict[str, dict[str, Any]]:
    """Pin prior public overlays and prove their coordinates do not overlap this slice."""
    selected = set(selected_ids())
    observed_ids: set[int] = set()
    records: dict[str, dict[str, Any]] = {}
    for name, (start_id, end_id, expected_hash) in PREVIOUS_OVERLAY_PINS.items():
        path = WORKSTREAM_DIR / "public" / name
        if not path.is_file():
            raise ValueError(f"missing prior msgbre overlay: {name}")
        actual_hash = base.sha256(path.read_bytes())
        if actual_hash != expected_hash:
            raise ValueError(f"prior msgbre overlay hash differs: {name}")
        overlay = json.loads(path.read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in overlay.get("entries", [])]
        expected_ids = list(range(start_id, end_id + 1))
        if ids != expected_ids:
            raise ValueError(f"prior msgbre overlay scope differs: {name}")
        if selected.intersection(ids) or observed_ids.intersection(ids):
            raise ValueError(f"msgbre overlay coordinate collision: {name}")
        observed_ids.update(ids)
        records[name] = {
            "start_id": start_id,
            "end_id": end_id,
            "sha256": actual_hash,
        }
    return records


def _check_replacement_invariants(sc_table: Any) -> None:
    failures: list[dict[str, Any]] = []
    for entry_id in selected_ids():
        source = sc_table.texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        problems = base.common.invariant_mismatches(source, replacement)
        if base.BRACKET_TOKEN_RE.findall(source) != base.BRACKET_TOKEN_RE.findall(replacement):
            problems.append("custom_bracket_placeholders differ")
        if problems:
            failures.append({"id": entry_id, "problems": problems})
    if failures:
        raise ValueError(f"batch9 replacement invariants failed: {failures}")


def reconstruct_sc_target(sc_packed: bytes, sc_table: Any) -> dict[str, Any]:
    """Rebuild the Korean target entirely in memory; never write a game resource."""
    texts = list(sc_table.texts)
    for entry_id in selected_ids():
        texts[entry_id] = TRANSLATIONS[entry_id]
    rebuilt_raw = rebuild_message_table(sc_table, texts)
    rebuilt_table = parse_message_table(rebuilt_raw)
    if rebuilt_table.texts != tuple(texts):
        raise ValueError("translated SC msgbre parse/rebuild round-trip differs")
    rebuilt_packed = recompress_wrapper(rebuilt_raw, sc_packed)
    _, decompressed = decompress_wrapper(rebuilt_packed)
    if decompressed != rebuilt_raw:
        raise ValueError("translated SC msgbre wrapper round-trip differs")
    return {
        "resource": "MSG_PK/SC/msgbre.bin",
        "entry_count": len(selected_ids()),
        "complete_target_included": False,
        "packed_size": len(rebuilt_packed),
        "packed_sha256": base.sha256(rebuilt_packed),
        "raw_size": len(rebuilt_raw),
        "raw_sha256": base.sha256(rebuilt_raw),
        "parse_rebuild_round_trip": True,
        "wrapper_round_trip": True,
    }


def _load_sources(args: argparse.Namespace) -> dict[str, tuple[bytes, bytes, Any]]:
    paths = {"SC": args.stock_sc, "JP": args.stock_jp, "EN": args.stock_en}
    loaded = {language: base.load_source(path, language) for language, path in paths.items()}
    tables = {language: value[2] for language, value in loaded.items()}
    empty_ids = [
        entry_id
        for entry_id in selected_ids()
        if any(not tables[language].texts[entry_id] for language in ("SC", "JP", "EN"))
    ]
    if empty_ids:
        raise ValueError(f"selected aligned range contains empty entries: {empty_ids}")
    if not all(tables[language].texts[NEXT_START_ID] for language in ("SC", "JP", "EN")):
        raise ValueError(f"next-start boundary ID {NEXT_START_ID} must be non-empty in all languages")
    _check_replacement_invariants(tables["SC"])
    return loaded


def _source_file_snapshot(args: argparse.Namespace) -> dict[str, str]:
    return {
        language: base.sha256(path.read_bytes())
        for language, path in {
            "SC": args.stock_sc,
            "JP": args.stock_jp,
            "EN": args.stock_en,
        }.items()
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    """Build the source-free catalog and independently validate its target transform."""
    previous_before = verify_previous_overlays()
    source_before = _source_file_snapshot(args)
    loaded = _load_sources(args)
    target_a = reconstruct_sc_target(loaded["SC"][0], loaded["SC"][2])
    target_b = reconstruct_sc_target(loaded["SC"][0], loaded["SC"][2])
    if target_a != target_b:
        raise ValueError("translated SC target reconstruction is not deterministic")

    _configure_engine()
    result = engine.build(args)

    if previous_before != verify_previous_overlays():
        raise ValueError("existing msgbre public overlays changed during batch9 build")
    if source_before != _source_file_snapshot(args):
        raise ValueError("installed msgbre source resources changed during batch9 build")

    validation_path = result["out_root"] / VALIDATION_NAME
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    validation["schema"] = "nobu16.kr.msgbre-generation-validation.v9"
    validation["scope"]["natural_boundary"] = {
        "selection_policy": "fixed_contiguous_parallel_slice",
        "previous_batch_end_id": 700,
        "next_start_id": NEXT_START_ID,
        "officer_name_ids_crosschecked": len(TRANSLATIONS) + 2,
    }
    validation["target_reconstruction"] = target_a
    validation["prior_overlay_coordination"] = {
        "checked_overlay_count": len(previous_before),
        "coordinate_collisions": 0,
        "all_prior_hashes_unchanged": True,
        "overlays": previous_before,
    }
    validation["safety"].update(
        {
            "installed_game_files_modified": False,
            "existing_v01_to_v08_artifacts_modified": False,
            "complete_translated_target_written": False,
        }
    )
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
