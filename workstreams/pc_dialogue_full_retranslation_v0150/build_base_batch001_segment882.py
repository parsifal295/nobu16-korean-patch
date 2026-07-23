#!/usr/bin/env python3
"""Build Base authoring segment 882 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment881 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
FRAMEWORK = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S882.private.v1.jsonl"
)
SEGMENT = 882
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1283:0": "땅굴 공략이 실패하여,",
    "15:1283:1": "이(가) 부상",
    "15:1284:0": "에 대한 땅굴 공략에 실패",
    "15:1285:0": "의 내구를",
    "15:1285:1": "감소",
    "15:1286:0": "에서",
    "15:1286:1": "이(가) 벌인",
    "15:1286:2": "을(를) 저지",
    "15:1287:0": "에 병력을 보충하고 싶구먼\n",
    "15:1287:1": (
        "이(가) 여기서 병사를 이끌고\n"
        "합류하러 가는 건 어떤가?"
    ),
    "15:1288:0": "에 병력을 보충합시다\n",
    "15:1288:1": (
        "이(가) 여기서 병사를 이끌고 가면\n"
        "아마 합류할 수 있을 듯합니다"
    ),
    "15:1289:0": "에 병력을 보충해야 하오\n이제부터",
    "15:1289:1": "이(가) 병사를 모아\n합류하러 가겠사옵니다",
    "15:1290:0": (
        "에 병력을 보충합시다\n"
        "이미 출진 중이기는 하나 병력이 불안하옵니다\n"
        "성에서 병사를 이끌고 합류하겠사옵니다"
    ),
    "15:1291:0": (
        "에 병력을 보충해야 할 듯하오\n"
        "이미 출진 중이나 방도가 있소\n"
        "이제 병사를 이끌고 합류하면 어떻겠소?"
    ),
    "15:1292:0": (
        "에 병력을 보충하고자 하옵니다\n"
        "주군께서도 다소 적은 병력으로 출진했다고 여기시지 않사옵니까?\n"
        "여기서 병사를 이끌고 뒤쫓겠사옵니다"
    ),
    "15:1293:0": (
        "에 대한 병력 보충은 맡겨 주십시오\n"
        "이미 출진 중이나 병력이 불안합니다\n"
        "성에서 병사를 이끌고 합류하겠습니다"
    ),
    "15:1294:0": (
        "은(는) 병력이 불안하구나\n"
        "이미 출진 중이지만 맡겨 주시오\n"
        "이제 병사를 이끌고 합류하여 보충하겠소"
    ),
    "15:1295:0": (
        "의 병력을 보충하게 해 주십시오\n"
        "저 병력으로는 불안합니다\n"
    ),
    "15:1295:1": "이(가) 병사를 이끌고 합류시킵시다",
}
RECORD_ARITIES = {
    1283: 2,
    1284: 1,
    1285: 2,
    1286: 3,
    1287: 2,
    1288: 2,
    1289: 2,
    1290: 1,
    1291: 1,
    1292: 1,
    1293: 1,
    1294: 1,
    1295: 2,
}
EXPECTED_BASE_JP = {
    1283: ("土竜攻めが失敗、", "が負傷"),
    1284: ("への土竜攻めが失敗",),
    1285: ("の耐久を", "減少"),
    1286: ("にて", "からの", "を阻止"),
    1287: (
        "に兵を補充してえな\n",
        "がここから兵を連れて\n合流しに行くってのはどうだ？",
    ),
    1288: (
        "に兵を補充しましょう\n",
        "がここより兵を率いて向かえば\nおそらく合流できるかと",
    ),
    1289: (
        "に兵を補充すべし\nこれより",
        "が兵をまとめ\n合流に向かいまする",
    ),
    1290: (
        "に兵を補充しましょう\n"
        "すでに出陣中ではありますが兵力が不安です\n"
        "城より兵を率い、合流いたしまする",
    ),
    1291: (
        "に兵を補充いたすべきかと\n"
        "すでに出陣中にはあれど手はござる\n"
        "これより兵を率い合流いたさば如何？",
    ),
    1292: (
        "に兵を補充いたしたく\n"
        "殿もやや小勢での出陣だったとお思いでは？\n"
        "ここより兵を率い、追いかけまする",
    ),
    1293: (
        "への兵の補充をお任せください\n"
        "すでに出陣中ではありますが兵力が不安です\n"
        "城より兵を率い、合流いたしましょう",
    ),
    1294: (
        "は兵力が不安じゃ\n"
        "すでに出陣中じゃがお任せあれ\n"
        "これより兵を率いて合流し、補充つかまつる",
    ),
    1295: (
        "の兵を補充させてください\nあの兵力では不安があります\n",
        "が兵を引き連れ合流させましょう",
    ),
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    1283: ("", "024633", "050505"),
    1284: ("026432", "050505"),
    1285: ("026432", "0232", "050505"),
    1286: ("026432", "025032", "023C", "050505"),
    **{
        record_id: ("026E32", "014301000000", "050505")
        for record_id in (1287, 1288, 1289, 1295)
    },
    **{
        record_id: ("026E32", "050505")
        for record_id in range(1290, 1295)
    },
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1283): (
        ("地道攻势失败，", "负伤。"),
        ("", "024633", "050505"),
    ),
    ("TC", 1283): (
        ("地道攻勢失敗，", "負傷。"),
        ("", "024633", "050505"),
    ),
    ("SC", 1284): (
        ("对", "的地道攻势失败。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1284): (
        ("對", "的地道攻勢失敗。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1285): (
        ("的耐久减少了", "。"),
        ("026432", "0232", "050505"),
    ),
    ("TC", 1285): (
        ("的耐久減少", "。"),
        ("026432", "0232", "050505"),
    ),
    ("SC", 1286): (
        ("于", "阻止", "的", "。"),
        ("", "026432", "025032", "023C", "050505"),
    ),
    ("TC", 1286): (
        ("於", "阻止", "的", "。"),
        ("", "026432", "025032", "023C", "050505"),
    ),
    ("SC", 1289): (
        ("为了替", "补充兵力，\n接下来", "会率兵，\n前去汇合。"),
        ("", "026E32", "014301000000", "050505"),
    ),
    ("TC", 1289): (
        ("需補充兵力。\n就由", "率兵前往會合。"),
        ("026E32", "014301000000", "050505"),
    ),
    ("SC", 1290): (
        (
            "为",
            "补充兵力吧。\n那里已经出阵，但兵力堪忧。\n我会从城中率兵过去会合。",
        ),
        ("", "026E32", "050505"),
    ),
    ("TC", 1290): (
        ("出陣中的", "\n兵力堪憂，急需補充。\n就由吾人自城率兵前往會合。"),
        ("", "026E32", "050505"),
    ),
    ("SC", 1291): (
        (
            "窃以为当为",
            "补充兵力了。\n那里已经出阵，但还有办法。\n现在我去率兵会合如何？",
        ),
        ("", "026E32", "050505"),
    ),
    ("TC", 1291): (
        ("應當補充兵力。\n出陣中部隊欲補充尚有一手。\n就由在下率兵前往會合，意下如何？",),
        ("026E32", "050505"),
    ),
    ("SC", 1295): (
        (
            "请补充",
            "的兵力吧。\n现在的兵力令人担忧。\n",
            "来领兵会合吧。",
        ),
        ("", "026E32", "014301000000", "050505"),
    ),
    ("TC", 1295): (
        ("兵力堪憂，\n請讓", "領兵會合以補充兵力。"),
        ("026E32", "014301000000", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1283: (
        ("Tunneling has failed. ", " was injured."),
        ("", "024633", "050505"),
    ),
    1284: (
        ("Tunneling into ", " was a failure."),
        ("", "026432", "050505"),
    ),
    1285: (
        (" lost ", " HP."),
        ("026432", "0232", "050505"),
    ),
    1286: (
        ("The ", "Ös ", " at ", " was prevented."),
        ("", "025032", "023C", "026432", "050505"),
    ),
    1289: (
        (
            "We need to replenish ",
            "Ös ranks. IÖll gather my soldiers and head for the rendezvous.",
        ),
        ("", "026E32", "050505"),
    ),
    1290: (
        (
            "We should replenish ",
            "Ös ranks. TheyÖre already on their way, but their numbers donÖt "
            "look good. I shall command my soldiers from the castle to assemble.",
        ),
        ("", "026E32", "050505"),
    ),
    1291: (
        (
            "We should replenish ",
            "Ös ranks. TheyÖre already marching, but there may be a way. Why "
            "donÖt I lead my soldiers from the castle to join up with them?",
        ),
        ("", "026E32", "050505"),
    ),
    1295: (
        (
            "Please consider replenishing the ",
            "Ös ranks. I donÖt think they have sufficient manpower. Allow me "
            "to take some of our soldiers to join them.",
        ),
        ("", "026E32", "050505"),
    ),
}
AUXILIARY_OVERRIDES = PREVIOUS.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "tunneling_failure_results_miner_corps_runtime_token_and_marching_unit_"
    "reinforcement_proposals_with_uniform_plus_8_pk_jp_sc_tc_mapping_pk_en_"
    "auxiliary_context_tunneling_and_troop_replenishment_canonical_terms_"
    "speaker_specific_register_dynamic_person_unit_castle_action_and_value_"
    "tokens_current_layout_and_opcode_skeleton_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if EXPECTED_BASE_GAPS[1283][1] != "024633":
        raise RuntimeError("segment 882 miner-corps runtime token drifted")
    joined = "\n".join(translations.values())
    for required in (
        "땅굴 공략",
        "병력 보충",
        "병력을 보충",
        "병사를 이끌",
        "출진 중",
        "합류",
        "적은 병력",
        "불안",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 882 terminology drifted: {required}")
    if any(
        term in joined
        for term in ("두더지 공격", "갱도 공격", "금굴중", "병사의 보충")
    ):
        raise RuntimeError("segment 882 retained forbidden terminology")
    if raw_translations["15:1286:1"] != PREVIOUS.RAW_TRANSLATIONS["15:1276:2"]:
        raise RuntimeError("segment 882 agentive action canonical drifted")
    if not raw_translations["15:1289:1"].endswith("가겠사옵니다"):
        raise RuntimeError("segment 882 1289 historical register drifted")
    if "적은 병력" not in raw_translations["15:1292:0"]:
        raise RuntimeError("segment 882 1292 small-force meaning drifted")
    if "주군께서도" not in raw_translations["15:1292:0"]:
        raise RuntimeError("segment 882 1292 direct lord address drifted")
    if not raw_translations["15:1295:1"].endswith(
        "병사를 이끌고 합류시킵시다"
    ):
        raise RuntimeError("segment 882 1295 causative joining meaning drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return FRAMEWORK.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 882 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S882",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "tunneling_term": "underground_assault",
                "miner_corps_runtime_token_preserved": True,
                "troop_replenishment_term_distinction": True,
                "contextual_ellipsis_normalized_to_project_pair": 0,
                "record_count": 19152,
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
