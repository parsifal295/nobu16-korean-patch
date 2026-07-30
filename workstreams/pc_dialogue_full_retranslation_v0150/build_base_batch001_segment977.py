#!/usr/bin/env python3
"""Build Base authoring segment 977 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment976 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S977.private.v1.jsonl"
)
SEGMENT = 977
CASTLE_TOKEN = PREVIOUS.CASTLE_TOKEN
FORCE_TOKEN = "025032"
UNIT_GROUP_TOKEN = "026E32"
VALUE_TOKEN = "0232"
TRANSLATIONS_BY_RECORD: dict[int, tuple[str | None, ...]] = {
    2230: (
        "을(를) 공략해 차지하는 것이 어떻겠소\n우리 병력은",
        "보다 우세하니\n대군을 동원해 쳐부수",
    ),
    2231: (
        "을(를) 공략할 절호의 기회",
        None,
        "은(는) 장수들이 하나같이 허약하니\n정예병으로 맞서면 쓸어 버릴 수 있",
    ),
    2232: (
        "을(를) 공격하던 부대를 철수시키겠습니다\n괜찮으시겠습니까?",
    ),
    2233: (
        "출진 중인 부대는 아직 여력이 충분하니\n",
        "등의 새 목표를\n공략하도록 지시해 보는 건",
        "가?",
    ),
    2234: (
        "여력이 남은 부대를 모아\n",
        "등의 성을 공격해 보는 건 어떻겠소?\n승산은 충분하다고 판단",
    ),
    2235: (
        "연전할 수 있는 부대가 남아",
        "\n집결시키면",
        "등의\n다른 성도 함락시킬 수 있",
    ),
    2236: (
        "들에게\n",
        "을(를) 공략하라고 명하시겠습니까?",
    ),
    2237: (
        "알겠",
        None,
        "들을 성으로 돌아오게 하",
    ),
    2238: (
        "지금은 움직일 때가 아닙니다. ",
        "\n잠시 호기를 기다리는 편이 ",
        "상책이라 사료됩니다.",
    ),
    2239: (
        "우리 가문은 지금 바로",
        "와\n교전 중이며, 그 병력은",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if translation is not None
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2230: ("を攻め取ってはいかが\n我らの兵力は", "より上\n大軍を用いて攻め潰"),
    2231: ("攻めの好機", "\n", "は弱将揃い\n精鋭で当たれば蹴散らせ"),
    2232: ("攻めから部隊を撤退させます\nよろしいでしょうか？",),
    2233: ("出陣中の部隊は余力十分\n", "など、新たな目標を\n指示しては", "か"),
    2234: ("余力の残る部隊を集め\n", "などを攻めてみては？\n勝算は十分にあると見"),
    2235: ("連戦可能な部隊が", "\n集結させれば", "など\n別の城も落とせ"),
    2236: ("らに\n", "攻略を命じますか？"),
    2237: ("承知し", "\n", "らを帰城させ"),
    2238: ("今は動く時では", "\nしばし機を待つのが", "かと"),
    2239: ("当家は今まさに", "と\n刃を交えており、その兵力は"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2230: (CASTLE_TOKEN, FORCE_TOKEN, "01437E0400000143FC010000050505"),
    2231: (
        CASTLE_TOKEN,
        "01432C020000",
        FORCE_TOKEN,
        "01431E040000050505",
    ),
    2232: (CASTLE_TOKEN, "050505"),
    2233: ("", CASTLE_TOKEN, "0143B0020000014356020000", "050505"),
    2234: ("", CASTLE_TOKEN, "01433C040000050505"),
    2235: ("", "0143B2000000", CASTLE_TOKEN, "01431E040000050505"),
    2236: (UNIT_GROUP_TOKEN, CASTLE_TOKEN, "050505"),
    2237: ("", "014314020000", UNIT_GROUP_TOKEN, "01433C040000050505"),
    2238: ("", "0143DA020000", "01430C040000", "050505"),
    2239: ("", FORCE_TOKEN, "023C050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    2238: ("", "", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2230: (CASTLE_TOKEN, FORCE_TOKEN, "01438A040000014302020000050505"),
    2231: (
        CASTLE_TOKEN,
        "014338020000",
        FORCE_TOKEN,
        "01432A040000050505",
    ),
    2233: ("", CASTLE_TOKEN, "0143BC020000014362020000", "050505"),
    2234: ("", CASTLE_TOKEN, "014348040000050505"),
    2235: ("", "0143B2000000", CASTLE_TOKEN, "01432A040000050505"),
    2237: ("", "01431A020000", UNIT_GROUP_TOKEN, "014348040000050505"),
    2238: ("", "0143E6020000", "014318040000", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:2231:1": "\n",
    "15:2237:1": "\n",
}
SHARED_AUXILIARY = {
    ("SC", 2230): (
        ("攻占", "如何？\n我等之兵力较", "为上，\n靠大军将其击溃吧。"),
        ("", CASTLE_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("TC", 2230): (
        ("攻取", "如何？\n我等之兵力較", "為上，\n以大軍予以擊潰吧。"),
        ("", CASTLE_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("SC", 2231): (
        ("如今是攻打", "的大好时机。\n", "的武将全都弱不禁风。\n若以精锐发动攻势则必胜。"),
        ("", CASTLE_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("TC", 2231): (
        ("現為攻擊", "的好時機。\n", "一群弱將，\n以精銳發動攻勢，定能擊潰。"),
        ("", CASTLE_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("SC", 2232): (
        ("是否确定放弃攻打", "，\n让部队撤退吗？"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2232): (
        ("是否允許停止進攻", "，\n率領部隊撤退？"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2233): (
        ("出阵中的部队余力十足。\n指示", "等新目标，\n如何？"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2233): (
        ("出陣中的部隊餘力十足。\n指示", "等新目標，\n如何？"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2234): (
        ("聚集有余力的部队，\n攻打", "等如何？\n应相当有胜算。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2234): (
        ("聚集有餘力的部隊，\n攻打", "等如何？\n應相當有勝算。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2235): (
        ("看来有能进行连战的部队，\n聚集起来的话，", "等\n其他城应该也能拿下吧。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2235): (
        ("看來有能進行連戰的部隊，\n聚集起來的話，", "等\n其他城應該也能拿下吧。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2236): (
        ("是否向", "等\n下达攻略", "的命令？"),
        ("", UNIT_GROUP_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2236): (
        ("是否命令", "\n進攻", "？"),
        ("", UNIT_GROUP_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2237): (
        ("明白了。\n让", "等人回城。"),
        ("", UNIT_GROUP_TOKEN, "050505"),
    ),
    ("TC", 2237): (
        ("明白了。\n會讓", "等回城的。"),
        ("", UNIT_GROUP_TOKEN, "050505"),
    ),
    ("SC", 2238): (
        ("现在尚且不是出手的时机。\n应该稍安勿躁，等待时机。",),
        ("", "050505"),
    ),
    ("TC", 2238): (
        ("此時並非移動的時機。\n暫且按兵不動方為上策。",),
        ("", "050505"),
    ),
    ("SC", 2239): (
        ("在周边势力中，与", "目前\n正处于交战状态，\n其兵力为", "。"),
        ("", FORCE_TOKEN, "023C", "050505"),
    ),
    ("TC", 2239): (
        ("在周邊勢力中與", "目前\n正處於交戰狀態，其兵力為"),
        ("", FORCE_TOKEN, "023C050505"),
    ),
}
PK_EN_AUXILIARY = {
    2230: (
        ("What do you think of attacking ", "? We could send a force larger than the ", "Ös and crush them."),
        ("", CASTLE_TOKEN, FORCE_TOKEN, "050505"),
    ),
    2231: (
        ("This is an excellent opportunity to attack ", ". The ", "Ös officers are weak; our troops will shatter them."),
        ("", CASTLE_TOKEN, FORCE_TOKEN, "050505"),
    ),
    2232: (
        ("Shall we order the units to retreat from the attack on ", "?"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2233: (
        ("The marching units have enough remaining strength. Why not assign them a new target, such as ", "?"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2234: (
        ("Should we gather the units with strength remaining to attack ", "? We retain enough power for victory."),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2235: (
        ("There are units capable of fighting on. LetÖs gather them together to capture ", " or some other castle."),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2236: (
        ("Will you command ", " to attack ", "?"),
        ("", UNIT_GROUP_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2237: (
        ("Acknowledged. IÖll order ", " to return."),
        ("", UNIT_GROUP_TOKEN, "050505"),
    ),
    2238: (
        ("Now is not the time to move. We should wait for a better opportunity.",),
        ("", "050505"),
    ),
    2239: (
        ("We are battling ", " troops of ", " at this very moment."),
        ("", "023C", FORCE_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B117_B_pristine_base_pc_jp_authoritative_"
    "castle_capture_attack_withdrawal_follow_on_targets_return_to_castle_"
    "and_war_assessment_with_explicit_base2230_2239_to_pk2260_2269_mapping_"
    "exact_sc_tc_and_actual_pk_en_context_dynamic_castle_force_unit_group_"
    "token_direction_base_pk_morphology_opcode_divergences_and_current2238_"
    "flattened_skeleton_recorded_attack_capture_distinction_weak_commanders_"
    "without_literal_yakjang_simple_examples_as_deung_our_house_as_uri_gamun_"
    "current_line_counts_outer_whitespace_and_hidden_lf_preserved_runtime_"
    "fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    178: ("있습니다", "있다", "있사옵니다"),
    508: ("", "다"),
    532: ("했습니다", "다"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    1054: ("합시다", "듯"),
    1084: ("합니다", "다", "하옵니다"),
    1150: ("합시다", "그렇군"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    514: EXPECTED_BASE_MORPHOLOGY_TERMINALS[508],
    538: EXPECTED_BASE_MORPHOLOGY_TERMINALS[532],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    742: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
    1048: ("좋다",),
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
    1162: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1150],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 977 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 977 Base-to-PK JP literal drifted")
    pk_gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if pk_gap_divergences != {2230, 2231, 2233, 2234, 2235, 2237, 2238}:
        raise RuntimeError("segment 977 Base-to-PK gap divergence drifted")
    current_gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_CURRENT_GAPS[record_id]
    }
    if current_gap_divergences != {2238}:
        raise RuntimeError("segment 977 pristine/current gap divergence drifted")
    if set(EXCLUDED_NONVISIBLE_COORDINATES) != {"15:2231:1", "15:2237:1"}:
        raise RuntimeError("segment 977 hidden LF coordinate drifted")
    joined = "\n".join(translations.values())
    for required in ("공략해 차지", "철수", "등", "성으로 돌아오", "우리 가문"):
        if required not in joined:
            raise RuntimeError(f"segment 977 required meaning drifted: {required}")
    for forbidden in ("약장", "따위", "귀성", "당가", "。"):
        if forbidden in joined:
            raise RuntimeError(f"segment 977 forbidden wording retained: {forbidden}")
    available_unit_variants = {
        f"{TRANSLATIONS_BY_RECORD[2235][0]}{ending}"
        for ending in EXPECTED_BASE_MORPHOLOGY_TERMINALS[178]
    }
    if available_unit_variants != {
        "연전할 수 있는 부대가 남아있습니다",
        "연전할 수 있는 부대가 남아있다",
        "연전할 수 있는 부대가 남아있사옵니다",
    }:
        raise RuntimeError("segment 977 available-unit morphology drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 977 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 977 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 977 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S977",
                "source_literal_count": 24,
                "decision_count": len(rows),
                "hidden_non_display_count": 2,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2230,
                    2231,
                    2233,
                    2234,
                    2235,
                    2237,
                    2238,
                ],
                "pristine_current_gap_divergence_records": [2238],
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
                "reverse_overlay_exact": True,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
