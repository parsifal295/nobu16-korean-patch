#!/usr/bin/env python3
"""Build Base authoring segment 883 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment882 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
FRAMEWORK = PREVIOUS.FRAMEWORK
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S883.private.v1.jsonl"
)
SEGMENT = 883
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1296:0": (
        "의 병력을 보충하고 싶다\n"
        "저 정도 수로는 불안할 터\n"
        "병사를 이끌고 가 합류시키겠다"
    ),
    "15:1297:0": (
        "의 병력을 보충하고 오겠습니다\n"
        "저 병력으로는 불안합니다\n"
    ),
    "15:1297:1": "이(가) 병사를 합류시키겠습니다",
    "15:1298:0": (
        "에 병력을 보충하고 오겠습니다\n"
        "이미 출진 중이나 병력이 불안합니다\n"
        "성에서 병사를 이끌고 합류하겠습니다"
    ),
    "15:1299:0": "출진 중인 군의 병력이 불안한가?\n그렇다면",
    "15:1299:1": (
        "이(가) 여기서 한달음에 달려가\n"
        "병력을 보충해 주지"
    ),
    "15:1300:0": (
        "출진 중인 군에 병력이 다소 부족하다고…\n"
        "그렇다면"
    ),
    "15:1300:1": (
        "이(가) 서둘러 병사를 이끌고\n"
        "병력 보충을 하러 가겠사옵니다"
    ),
    "15:1301:0": (
        "출진 중인 군에 병력을 보충하려면 맡겨 주시옵소서\n"
        "이 성에서 병사를 이끌고 가면\n"
        "문제없이 합류할 수 있사옵니다"
    ),
    "15:1302:0": (
        "출진 중인 부대에 병력을 보충할 좋은 방도가 있사옵니다\n"
        "비록 성에 없더라도\n"
        "이 성에서 병사를 이끌고 뒤쫓으면 될 듯하옵니다"
    ),
    "15:1303:0": (
        "출진 중인 부대의 병력 보충이오?\n"
        "병력이 다소 불안하다고 여기셨소?\n"
        "맡겨 주시오, 병사를 이끌고 합류하겠소"
    ),
    "15:1304:0": (
        "출진 중인 부대의 병력이 불안하시다면 맡겨 주시옵소서\n"
        "이 성에서 병사를 이끌고\n"
        "뒤쫓아 합류하면 보충할 수 있사옵니다"
    ),
    "15:1305:0": (
        "출진 중인 부대에 병력을 보충하시려면 맡겨 주십시오\n"
        "비록 성을 나가 있더라도\n"
        "성에서 병사를 이끌고 합류하겠습니다"
    ),
    "15:1306:0": (
        "출진 중인 부대의 병력이\n"
        "다소 불안하다고 여기셨는가\n"
        "맡겨 주시오, 병사를 이끌고 합류하겠소"
    ),
    "15:1307:0": "병력 보충이군요\n곧바로 다녀오겠습니다!",
    "15:1308:0": "병력 보충이로군\n곧바로 마치겠다!",
    "15:1309:0": "병력 보충이라면 맡겨 주십시오\n곧 출발하겠습니다",
    "15:1310:0": "출진 중인 부대에 병력을 보충하는 것이구려!\n",
    "15:1310:1": "이(가) 다녀오겠습니다!",
    "15:1311:0": (
        "의 병력 보충을 마치고 왔다\n"
        "병사 수는 이제 충분하군!"
    ),
    "15:1312:0": (
        "에 병력을 보충하였사옵니다\n"
        "그들도 병력이 다소 적었던 터라,\n"
        "병사 수가 늘어 안심했을 것입니다"
    ),
    "15:1313:0": (
        "에 병력 보충을 마치고 왔사옵니다\n"
        "이제 병력은 걱정하지 않으셔도 될 것입니다"
    ),
    "15:1314:0": (
        "의 병력 보충을 완료했습니다\n"
        "무사히 따라잡아 병사를 합류시켜\n"
        "성에 들르게 하지 않고 보충을 마쳤습니다"
    ),
    "15:1315:0": (
        "의 병력은 만전이옵니다\n"
        "무사히 따라잡아 합류하여\n"
        "진군을 멈추지 않고 병력을 보충하였사옵니다"
    ),
    "15:1316:0": (
        "에 합류하여\n"
        "병력 보충을 마치고 돌아왔습니다\n"
        "부디 마음 놓으십시오"
    ),
    "15:1317:0": (
        "에 부대를 합류시켜\n"
        "이동을 멈추지 않고 병력을 보충하였사옵니다\n"
        "이제 병력은 염려하지 않으셔도 되옵니다"
    ),
}
RECORD_ARITIES = {
    1296: 1,
    1297: 2,
    1298: 1,
    1299: 2,
    1300: 2,
    **{record_id: 1 for record_id in range(1301, 1310)},
    1310: 2,
    **{record_id: 1 for record_id in range(1311, 1318)},
}
EXPECTED_BASE_JP = {
    1296: (
        "の兵を補充したい\n"
        "あの数では不安であろう\n"
        "兵を連れ合流させてこよう",
    ),
    1297: (
        "の兵を補充してきます\nあの兵力では不安があります\n",
        "が兵を合流させましょう",
    ),
    1298: (
        "に兵を補充してきます\n"
        "すでに出陣中ですが兵力が不安です\n"
        "城より兵を率い、合流いたします",
    ),
    1299: (
        "出陣中の軍に不安があるのか？\nなら",
        "がここからひとっ走りして\n兵を補充してきてやるよ",
    ),
    1300: (
        "出陣中の軍、些か数が足りぬと…\nならば",
        "が急ぎ兵を率いて\n補充に参りましょうぞ",
    ),
    1301: (
        "出陣中の軍に兵を補充するならばお任せを\n"
        "この城より兵を率いてゆけば\n"
        "問題なく合流できまする",
    ),
    1302: (
        "出陣中の部隊に兵を補充するなら良い案が\n"
        "たとえ城にいなくても\n"
        "この城より兵を率い追いかければよいかと",
    ),
    1303: (
        "出陣中の部隊への兵の補充？\n"
        "いささか兵力が心許なく思われたか\n"
        "お任せあれ、兵を率いて合流いたそう",
    ),
    1304: (
        "出陣中の部隊の兵力が不安ならお任せを\n"
        "この城より兵を率い\n"
        "追いかけて合流すれば、補充できまする",
    ),
    1305: (
        "出陣中の部隊に兵を補充なさるならお任せを\n"
        "たとえ城を出ておりましても\n"
        "城より兵を率い合流いたしましょう",
    ),
    1306: (
        "出ておる部隊の兵力が\n"
        "いささか心許のう思われたか\n"
        "任せられい、兵を率いて合流しようぞ",
    ),
    1307: ("兵を補充するのですね\nすぐに行ってまいります！",),
    1308: ("兵の補充だな\nすぐに済ませよう！",),
    1309: ("兵の補充ならばお任せを\nすぐに出立いたします",),
    1310: (
        "出陣中の部隊に兵を補充するのですな！\n",
        "が行ってきましょう！",
    ),
    1311: ("への補充を終えてきたぞ\n兵の数はこれで十分だな！",),
    1312: (
        "へ兵の補充をいたしました\n"
        "彼らも些か少数であったゆえ、\n"
        "兵の数が増え、安心したでしょう",
    ),
    1313: (
        "に兵の補充をしてまいりましたぞ\n"
        "これにて兵力については心配いらぬでしょう",
    ),
    1314: (
        "への兵の補充は完了です\n"
        "無事追いつき、兵を合流させることで\n"
        "城に寄らせることなく補充を終えました",
    ),
    1315: (
        "の兵力は万全にござる\n"
        "無事追いつきて合流し\n"
        "進軍を止めることなく、兵を補充いたした",
    ),
    1316: (
        "に合流いたし\n"
        "兵の補充を終えて戻りました\n"
        "どうぞお心安く",
    ),
    1317: (
        "に部隊を合流させ\n"
        "進行を止めることなく兵を補充いたしました\n"
        "これで兵力の心配はご無用かと",
    ),
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    1296: ("026E32", "050505"),
    1297: ("026E32", "014301000000", "050505"),
    1298: ("026E32", "050505"),
    **{
        record_id: ("", "014301000000", "050505")
        for record_id in (1299, 1300)
    },
    **{
        record_id: ("", "050505")
        for record_id in range(1301, 1310)
    },
    1310: ("", "014301000000", "050505"),
    **{
        record_id: ("026E32", "050505")
        for record_id in range(1311, 1318)
    },
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES = {"15:1300:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1301): (
        (
            "若要为出阵的军队补充兵力便交给我吧。\n"
            "从此城率兵出发的话，\n"
            "应该可以顺利汇合。",
        ),
        ("", "050505"),
    ),
    ("TC", 1301): (
        (
            "派兵增援出陣中部隊的任務，\n"
            "請讓我為您效勞。若從這座城\n"
            "率兵前往，應可順利會合。 ",
        ),
        ("", "050505"),
    ),
    ("SC", 1302): (
        (
            "有个好方法能为出阵的军队补充兵力。\n"
            "即使不在城内，\n"
            "从此城率兵追赶便可。",
        ),
        ("", "050505"),
    ),
    ("TC", 1302): (
        (
            "欲向出陣中軍隊派兵增援之事，\n"
            "我有一計。縱使不在城內，\n"
            "亦可從此城率兵趕往。 ",
        ),
        ("", "050505"),
    ),
    ("SC", 1303): (
        (
            "出阵中的部队补充兵力？\n"
            "对兵力抱有不安吗？\n"
            "交给我率兵去汇合吧。",
        ),
        ("", "050505"),
    ),
    ("TC", 1303): (
        (
            "派兵增援出陣中的部隊？\n"
            "對薄弱的兵力感到憂心嗎。\n"
            "請讓我為您效勞，立刻率兵前往會合。 ",
        ),
        ("", "050505"),
    ),
    ("SC", 1307): (
        ("是要补充兵力吧。\n那便立即出发！",),
        ("", "050505"),
    ),
    ("TC", 1307): (
        ("想派兵增援是嗎。\n這就立刻率兵前往！ ",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1301: (
        (
            "If you need to replenish troops on the move, then you can count "
            "on me. IÖll march some fresh soldiers from the castle and join "
            "up with them.",
        ),
        ("", "050505"),
    ),
    1302: (
        (
            "ItÖd be smart to replenish our marching troops. Even when they "
            "arenÖt stationed at a castle, I could lead soldiers from this "
            "castle to link up with them.",
        ),
        ("", "050505"),
    ),
    1303: (
        (
            "Should we replenish the troops that have marched out? IÖm "
            "worried that their manpower will come up short. Perhaps I could "
            "lead some soldiers their way?",
        ),
        ("", "050505"),
    ),
    1307: (
        ("Replenish the soldiers? IÖll see to it immediately!",),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = PREVIOUS.PREVIOUS.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "marching_unit_reinforcement_proposals_acceptances_and_completion_reports_"
    "with_uniform_plus_8_pk_jp_sc_tc_mapping_pk_en_auxiliary_context_exact_"
    "troop_replenishment_command_versus_leading_soldiers_action_distinction_"
    "marching_joining_small_force_and_uncertainty_meanings_speaker_specific_"
    "register_dynamic_person_unit_and_castle_tokens_current_layout_and_opcode_"
    "skeleton_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "병력 보충",
        "병력을 보충",
        "병사를 이끌",
        "출진 중",
        "합류",
        "불안",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 883 terminology drifted: {required}")
    if any(term in joined for term in ("병사의 보충", "미덥지 않", "군용 인원")):
        raise RuntimeError("segment 883 retained forbidden terminology")
    for record_id in range(1307, 1311):
        group = "\n".join(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        )
        if "보충" not in group:
            raise RuntimeError(
                f"segment 883 reinforcement acceptance meaning drifted: {record_id}"
            )
    for record_id in range(1311, 1318):
        group = "\n".join(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        )
        if not any(
            term in group for term in ("마치고", "완료", "만전", "보충하였")
        ):
            raise RuntimeError(
                f"segment 883 reinforcement completion meaning drifted: "
                f"{record_id}"
            )
    if not raw_translations["15:1297:1"].endswith("병사를 합류시키겠습니다"):
        raise RuntimeError("segment 883 1297 causative joining meaning drifted")
    if not raw_translations["15:1299:0"].startswith(
        "출진 중인 군의 병력이 불안한가?"
    ):
        raise RuntimeError("segment 883 1299 uncertainty subject drifted")
    for record_id in (1303, 1306):
        if "불안하다고 여기셨" not in raw_translations[f"15:{record_id}:0"]:
            raise RuntimeError(
                f"segment 883 uncertainty experiencer drifted: {record_id}"
            )
    if (
        not raw_translations["15:1310:0"].endswith("것이구려!\n")
        or not raw_translations["15:1310:1"].endswith("다녀오겠습니다!")
    ):
        raise RuntimeError("segment 883 1310 confirmation register drifted")
    if "병력이 다소 적었던" not in raw_translations["15:1312:0"]:
        raise RuntimeError("segment 883 1312 small-number meaning drifted")
    if not raw_translations["15:1316:0"].endswith("부디 마음 놓으십시오"):
        raise RuntimeError("segment 883 1316 reassurance meaning drifted")
    if (
        "진군을 멈추지 않고" not in raw_translations["15:1315:0"]
        or "이동을 멈추지 않고" not in raw_translations["15:1317:0"]
    ):
        raise RuntimeError("segment 883 進軍/進行 distinction drifted")


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
        raise RuntimeError("segment 883 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S883",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "reinforcement_proposals": 11,
                "reinforcement_acceptances": 4,
                "reinforcement_completion_reports": 7,
                "troop_replenishment_term_distinction": True,
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
