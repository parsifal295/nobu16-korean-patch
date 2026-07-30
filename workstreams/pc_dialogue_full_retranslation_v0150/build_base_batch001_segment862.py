#!/usr/bin/env python3
"""Build Base authoring segment 862 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment860 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S862.private.v1.jsonl"
SEGMENT = 862
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1045:0": "가보·",
    "15:1045:1": "을(를) 접수",
    "15:1046:0": (
        "을(를) 수복해야겠어\n"
        "지난 싸움에서 꽤 손상됐으니\n"
        "지금 고쳐 두자고!"
    ),
    "15:1047:0": (
        "을(를) 서둘러 수복해야 할 듯하옵니다\n"
        "지난 싸움에서 손상된 듯하오니\n"
        "무너지기 전에 고쳐야 하옵니다"
    ),
    "15:1048:0": (
        "을(를) 수복해도 되겠습니까\n"
        "다음 싸움까지 방비를 온전히 갖추고 싶습니다"
    ),
    "15:1049:0": (
        "을(를) 서둘러 수복합시다\n"
        "싸움이 없는 지금이야말로 호기… 다음 싸움에 대비해\n"
        "단숨에 고쳐 두어야 합니다"
    ),
    "15:1050:0": (
        "은(는) 서둘러 수복해야 하옵니다\n"
        "싸움이 없음을 다행으로 여겨, 어서 수복을!"
    ),
    "15:1051:0": (
        "은(는) 수복하셔야 하옵니다\n"
        "그렇지 않으면 약한 성으로 여겨져 적의 표적이 될 것이옵니다"
    ),
    "15:1052:0": (
        "은(는) 수복이 필요하옵니다\n"
        "지난 싸움에서 손상되어 염려되오니\n"
        "적이 쳐들어오기 전에 서둘러 고쳐야 할 줄로 아뢰옵니다"
    ),
    "15:1053:0": (
        "은(는), 어서 고쳐 주어야겠구려\n"
        "다음 싸움이 벌어진 뒤에는 늦소이다"
    ),
    "15:1054:0": (
        "의 수복을 서두릅시다\n"
        "지난 싸움에서 크게 손상된 듯합니다"
    ),
    "15:1055:0": (
        "에는 수복이 필요하군\n"
        "이 상태로 공격받으면\n"
        "이길 싸움도 이기지 못한다"
    ),
    "15:1056:0": (
        "의 수복을 서두릅시다\n"
        "지난 싸움에서 상당한 피해를 입었습니다\n"
        "지금 적의 습격을 받으면 버티지 못할 듯…"
    ),
    "15:1057:0": (
        "의 수복을 명해 주시옵소서\n"
        "지난 싸움에서 크게 무너졌사오니\n"
        "벽이 무너져 내릴까 염려되옵니다"
    ),
    "15:1058:0": (
        "을(를) 서둘러 수복해야 할 듯하옵니다\n"
        "이곳은 적지와 가까우니\n"
        "빈틈을 보여서는"
    ),
    "15:1059:0": "은(는) 손상되어",
    "15:1059:1": (
        "\n이웃 나라에 틈을 내주지 않기 위해서라도\n"
        "서둘러 수복해 버리"
    ),
    "15:1059:2": "인가",
    "15:1060:0": "을(를) 수복하고자",
    "15:1060:1": "\n지키기에 다소 지장이 있",
    "15:1060:2": "그러하오니\n공을 들여 수복하고자 하옵니다",
}
RECORD_ARITIES = {
    1045: 2,
    **{record_id: 1 for record_id in range(1046, 1059)},
    1059: 3,
    1060: 3,
}
EXPECTED_JP = {
    1045: ("家宝・", "を接収"),
    1046: (
        "を修復しねえとな\n先の戦で、かなり傷んじまってる\n今のうちに直しとこうぜ！",
    ),
    1047: (
        "を急ぎ修復すべきかと\n先の戦にて傷んでしまっている様子\n崩れる前に直さねば",
    ),
    1048: (
        "を修復してもよろしいですか\n次の戦までに防備を完全にしたいのです",
    ),
    1049: (
        "を急ぎ修復しましょう\n戦なき今こそ好機…次の戦に備え\n一気に直してしまわねば",
    ),
    1050: (
        "は急ぎ直さねばなりますまい\n戦なきを幸い、いざ修復を！",
    ),
    1051: (
        "は修復なさるべきです\nさもなくば弱城よと敵に狙われましょう",
    ),
    1052: (
        "は修復が必要でございます\n先の戦で傷つき心許なく存じまする\n敵の襲来前に、急ぎ直すべきかと",
    ),
    1053: (
        "は、早う直してやらねばのう\n次の戦が起きてからでは遅うござる",
    ),
    1054: (
        "の修復を急ぎましょう\n先の戦でずいぶん傷んでいる様子にて",
    ),
    1055: (
        "には修復がいるな\nこの状態で攻められては\n勝てる戦も勝てぬ",
    ),
    1056: (
        "の修復を急ぎましょう\n先の戦でだいぶ被害が出ています\n今、敵の襲撃を受ければ耐えきれぬかと…",
    ),
    1057: (
        "の修復をお命じくだされ\n先の戦でかなり崩れておりますゆえ\n壁が倒れてくるのではと不安なのです",
    ),
    1058: (
        "を急ぎ修復すべきかと\nここは敵地に近いゆえ\n隙を見せては",
    ),
    1059: (
        "は傷んで",
        "\n隣国に付け入られぬためにも\n急ぎ直してしま",
        "か",
    ),
    1060: (
        "を修復したく",
        "\n守るに少々支障があ",
        "ゆえ\n手をかけて直してしまおうかと",
    ),
}
EXPECTED_BASE_GAPS = {
    1045: ("", "028232", "050505"),
    **{record_id: ("026432", "050505") for record_id in range(1046, 1058)},
    1058: ("026432", "01434c000000050505"),
    1059: (
        "026432",
        "0143b2000000",
        "014366040000",
        "050505",
    ),
    1060: (
        "026432",
        "0143e2000000",
        "014336040000",
        "050505",
    ),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1059: (
        "026432",
        "0143b2000000",
        "014372040000",
        "050505",
    ),
    1060: (
        "026432",
        "0143e2000000",
        "014342040000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + (7 if record_id <= 1045 else 8)
    for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1049:0",
    "15:1056:0",
}
SC_AUXILIARY = {
    1045: (
        ("接收了家宝", "。"),
        ("", "028232", "050505"),
    ),
    1048: (
        ("可以修复", "吗？\n我想在下一战之前，做好万全的防备。"),
        ("", "026432", "050505"),
    ),
    1049: (
        (
            "火速修复",
            "吧。\n如今没有战事，正是大好时机……\n必须一口气修好它，为下一战做准备。",
        ),
        ("", "026432", "050505"),
    ),
    1050: (
        ("必须火速修好", "。\n幸好如今没有开战，快修复吧！"),
        ("", "026432", "050505"),
    ),
    1054: (
        ("加紧修复", "吧。\n它在上一战中损坏不小。"),
        ("", "026432", "050505"),
    ),
    1058: (
        ("应该立即对", "进行修复。\n此处离敌方很近，\n不能让敌人有可乘之机。"),
        ("", "026432", "050505"),
    ),
    1059: (
        ("已经受损，\n为了不被邻国乘人之危，\n应该立即着手修复。",),
        ("026432", "050505"),
    ),
    1060: (
        ("要修复", "。\n多少有点妨碍防御，\n所以应该尽快着手修理。"),
        ("", "026432", "050505"),
    ),
}
TC_AUXILIARY = {
    1045: (
        ("接收家寶", "。"),
        ("", "028232", "050505"),
    ),
    1048: (
        ("可否修復", "？\n希望能在下次臨戰前做好防備。"),
        ("", "026432", "050505"),
    ),
    1049: (
        (
            "趕緊修復",
            "吧！\n目前無戰火乃天賜良機……\n必須迅速修復，為下次備戰。",
        ),
        ("", "026432", "050505"),
    ),
    1050: (
        ("非得火速修復才行。\n所幸當前無戰事，趕緊修復吧！",),
        ("026432", "050505"),
    ),
    1054: (
        ("趕緊修復", "吧！\n乃因上一戰似乎導致嚴重損壞。"),
        ("", "026432", "050505"),
    ),
    1058: (
        ("離敵境不遠，\n應立即修復以防露出破綻。",),
        ("026432", "050505"),
    ),
    1059: (
        ("已經受損。\n為免鄰國趁虛而入，\n務必儘速修復。",),
        ("026432", "050505"),
    ),
    1060: (
        ("有必要對", "進行修復。\n由於會對防務造成些許影響，\n還是趕快投入人手修復吧。"),
        ("", "026432", "050505"),
    ),
}
EN_AUXILIARY = {
    1045: (
        ("Seized the treasure ", "."),
        ("", "028232", "050505"),
    ),
    1048: (
        (
            "Shall we repair ",
            "? IÖd like to shore up our defenses before the next battle.",
        ),
        ("", "026432", "050505"),
    ),
    1049: (
        (
            "LetÖs repair ",
            " quickly! We should take advantage of this momentary peace to fix it up.",
        ),
        ("", "026432", "050505"),
    ),
    1050: (
        (
            "We must repair ",
            " quickly! This blessed reprieve from battle shouldnÖt be wasted!",
        ),
        ("", "026432", "050505"),
    ),
    1054: (
        (
            "We ought to hurry with the repairs to ",
            ". We incurred a lot of damage during the last battle.",
        ),
        ("", "026432", "050505"),
    ),
    1058: (
        (
            "We must hurry and repair ",
            ". We canÖt afford to appear weak this close to enemy territory.",
        ),
        ("", "026432", "050505"),
    ),
    1059: (
        (
            "We canÖt let our neighbors take advantage of ",
            " being damaged. ShouldnÖt we hurry and repair it?",
        ),
        ("", "026432", "050505"),
    ),
    1060: (
        (
            "IÖd like to repair ",
            ". ItÖll be difficult to defend it the way it is, so we should repair it right away.",
        ),
        ("", "026432", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): value
        for side in ("base", "pk")
        for record_id, value in SC_AUXILIARY.items()
    },
    **{
        (side, "TC", record_id): value
        for side in ("base", "pk")
        for record_id, value in TC_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
DYNAMIC_STEM_REFERENCE_CASES = {
    (6, 3081): (
        "0143b2000000",
        0,
        "은(는) 충분한 힘을 길러",
    ),
    (6, 3545): (
        "014366040000",
        0,
        "사람을 이끄는 자로서\n주어진 일을 해낼 뿐\n더 맡겨도 상관없",
    ),
}
BASIS = (
    "pristine_base_pc_jp_authoritative_treasure_receipt_and_castle_repair_"
    "proposals_with_explicit_plus_7_then_plus_8_pk_insertion_corrected_map_"
    "exact_pc_sc_tc_mapping_pk_en_auxiliary_context_dynamic_castle_and_"
    "speaker_conjugation_tokens_historical_hierarchical_register_weak_castle_"
    "meaning_current_layout_opcode_skeleton_reference_stem_assemblies_and_"
    "isolated_reverse_overlay_verified_runtime_assembly_pending"
)


def assert_dynamic_stem_references() -> None:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    for key, (opcode_hex, literal_id, expected_korean) in (
        DYNAMIC_STEM_REFERENCE_CASES.items()
    ):
        record = current_records[key]
        gaps = tuple(gap.hex() for gap in COMMON.UTIL.record_gaps(record))
        if gaps[literal_id + 1] != opcode_hex:
            raise RuntimeError(
                f"segment 862 reference conjugation opcode drifted: {key}"
            )
        actual_korean = ENGINE.parse_record_literals(record)[literal_id].text
        if actual_korean != expected_korean:
            raise RuntimeError(
                f"segment 862 reference Korean stem assembly drifted: {key}"
            )


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    assert_dynamic_stem_references()
    if COMMON.CORE.source_literals(source_records, 1045) != EXPECTED_JP[1045]:
        raise RuntimeError("segment 862 1045 treasure receipt source drifted")
    if set(PK_RECORD_MAP.values()) & {1053}:
        raise RuntimeError("segment 862 PK-only insertion entered mapped scope")
    if not translations["15:1057:0"].startswith(
        "의 수복을 명해 주시옵소서\n"
    ):
        raise RuntimeError("segment 862 1057 lord/subordinate hierarchy drifted")
    if not translations["15:1058:0"].endswith("빈틈을 보여서는"):
        raise RuntimeError("segment 862 1058 post-gap conjugation stem drifted")
    stem_expectations = {
        "15:1059:0": "손상되어",
        "15:1059:1": "서둘러 수복해 버리",
        "15:1060:0": "수복하고자",
        "15:1060:1": "지장이 있",
    }
    for coordinate, suffix in stem_expectations.items():
        if not raw_translations[coordinate].endswith(suffix):
            raise RuntimeError(
                f"segment 862 dynamic conjugation stem drifted: {coordinate}"
            )
    if raw_translations["15:1059:2"] != "인가":
        raise RuntimeError("segment 862 1059 source question particle drifted")
    if raw_translations["15:1060:2"] != (
        "그러하오니\n공을 들여 수복하고자 하옵니다"
    ):
        raise RuntimeError("segment 862 1060 post-opcode completion drifted")
    if EXPECTED_BASE_GAPS[1059][1:3] != (
        "0143b2000000",
        "014366040000",
    ):
        raise RuntimeError("segment 862 1059 Base conjugation opcode order drifted")
    if EXPECTED_BASE_GAPS[1060][1:3] != (
        "0143e2000000",
        "014336040000",
    ):
        raise RuntimeError("segment 862 1060 Base conjugation opcode order drifted")
    joined = "\n".join(translations.values())
    for required in ("접수", "수복", "방비", "약한 성", "손상"):
        if required not in joined:
            raise RuntimeError(
                f"segment 862 repair/receipt terminology drifted: {required}"
            )
    if any(term in joined for term in ("보수", "복구", "약성", "산하")):
        raise RuntimeError("segment 862 retained forbidden legacy terminology")
    if any(coordinate.startswith("15:1095:") for coordinate in translations):
        raise RuntimeError("segment 862 hidden 1095 entered visible decision scope")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_record_map=PK_RECORD_MAP,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 862 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S862",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "record_count": 19152,
                "explicit_pk_record_mapping_verified": True,
                "dynamic_stem_reference_cases_verified": len(
                    DYNAMIC_STEM_REFERENCE_CASES
                ),
                "outside_scope_records_exact": True,
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
