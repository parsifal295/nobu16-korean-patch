#!/usr/bin/env python3
"""Build Base authoring segment 876 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment863 as COMMON


ENGINE = COMMON.ENGINE
CORE = COMMON.CORE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S876.private.v1.jsonl"
SEGMENT = 876
TUNNEL_SIEGE_TERM = "땅굴 공략"
MINER_CORPS_TERM = "광부대"
TUNNEL_SUCCESS_RECORD_IDS = tuple(range(1230, 1239))
TUNNEL_SUCCESS_SOURCE = (
    "金堀衆による土竜攻めで\n",
    "を攻め落とし",
    "ぞ！",
)
TUNNEL_SUCCESS_REPORT = (
    "광부대가 펼친 땅굴 공략으로\n",
    "을(를) 함락시키",
    "다!",
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1223:0": (
        "을(를) 공격할 때는 땅굴 공략을 쓰자\n"
        "재빨리 성을 함락시킬 수 있을 것이다"
    ),
    "15:1224:0": (
        "땅굴 공략을 펼칩시다\n"
        "준비가 필요하지만\n"
        "아군 피해를 줄이면서"
    ),
    "15:1224:1": "을(를) 함락시킬 수 있습니다",
    "15:1225:0": (
        "을(를) 함락할 방책이\n"
        "내게 있사옵니다\n"
        "땅굴 공략을 펼칩시다"
    ),
    "15:1226:0": "요해인",
    "15:1226:1": (
        "을(를) 함락하려면\n"
        "땅굴 공략을 쓰는 것이\n"
    ),
    "15:1227:0": (
        "은(는) 꽤나 견고하오니\n"
        "이곳은 땅굴 공략을 시도해 보시는 것이\n"
    ),
    "15:1227:1": "인가",
    "15:1228:0": (
        "의 방비를 무너뜨리고자\n"
        "땅굴 공략을 시도하여\n"
        "적의 간담을 서늘하게 만들고자"
    ),
    "15:1229:0": "에",
    "15:1229:1": "을(를) 걸어\n방비를 깎는 데 성공하",
    "15:1229:2": "!",
    **{
        f"15:{record_id}:{literal_id}": text
        for record_id in range(1230, 1233)
        for literal_id, text in enumerate(TUNNEL_SUCCESS_REPORT)
    },
}
RECORD_ARITIES = {
    1223: 1,
    1224: 2,
    1225: 1,
    1226: 2,
    1227: 2,
    1228: 1,
    1229: 3,
    1230: 3,
    1231: 3,
    1232: 3,
}
EXPECTED_JP = {
    1223: ("攻めに土竜攻めを使おう\n手早く城を落とせるはずだ",),
    1224: (
        "土竜攻めをいたしましょう\n準備が必要ですが\n被害を抑えて",
        "を落とせます",
    ),
    1225: (
        "を攻め落とすに\n考えがございます\n土竜攻めを行いましょう",
    ),
    1226: (
        "要害たる",
        "を攻め落とすには\n土竜攻めを用いるのが\n",
    ),
    1227: (
        "はなかなかに堅牢\nここは土竜攻めを仕掛けては\n",
        "か",
    ),
    1228: (
        "の防備を崩すべく\n"
        "土竜攻めを試みて\n"
        "敵の度肝を抜きたく",
    ),
    1229: ("へ", "を仕掛け\n防備を削ることに成功し", "！"),
    1230: TUNNEL_SUCCESS_SOURCE,
    1231: TUNNEL_SUCCESS_SOURCE,
    1232: TUNNEL_SUCCESS_SOURCE,
}
EXPECTED_BASE_GAPS = {
    1223: ("026432", "050505"),
    1224: ("", "026432", "050505"),
    1225: ("026432", "050505"),
    1226: ("", "026432", "01430c04000001431e010000050505"),
    1227: ("026432", "0143b002000001435c020000", "050505"),
    1228: ("026432", "0143e2000000050505"),
    1229: ("026432", "023c", "014314020000", "050505"),
    **{
        record_id: ("", "026432", "014314020000", "050505")
        for record_id in range(1230, 1233)
    },
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1226: ("", "026432", "01431804000001431e010000050505"),
    1227: ("026432", "0143bc020000014368020000", "050505"),
    1229: ("026432", "023c", "01431a020000", "050505"),
    **{
        record_id: ("", "026432", "01431a020000", "050505")
        for record_id in range(1230, 1233)
    },
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1226): (
            ("的城墙十分坚固，\n我看可以用地道攻势进攻。",),
            ("026432", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1226): (
            ("城牆堅固無比，\n不妨使用地道攻勢。",),
            ("026432", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1226): (
        (" has strategic importance. We should try attacking it by tunneling.",),
        ("026432", "050505"),
    ),
    **{
        (side, "SC", 1227): (
            ("坚不可摧，\n不如使用地道攻势如何？",),
            ("026432", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1227): (
            ("的戒備森嚴，\n是否發動地道攻勢？",),
            ("026432", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1227): (
        (" is practically a fortress. Why donÖt we try tunneling in?",),
        ("026432", "050505"),
    ),
    **{
        (side, "SC", 1228): (
            (
                "为了瓦解",
                "的防御，\n在下欲尝试地道攻势，\n给敌人一个出其不意。",
            ),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1228): (
            (
                "為攻潰",
                "的防衛，\n建議不妨發動地道攻勢，\n痛擊敵人。",
            ),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1228): (
        (
            "We could try tunneling to break down ",
            "Ös defenses. IÖm certain it will take the enemy off guard.",
        ),
        ("", "026432", "050505"),
    ),
    **{
        (side, "SC", 1229): (
            ("对", "发动", "，\n成功削弱了防备！"),
            ("", "026432", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1229): (
            ("對", "發動", "，\n成功削弱了防備！"),
            ("", "026432", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1229): (
        ("Thanks to ", ", we managed to crumble ", "Ös defenses!"),
        ("", "023c", "026432", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "historical_tunnel_siege_proposals_effect_success_and_gold_miner_corps_"
    "reports_with_uniform_plus_8_pk_jp_sc_tc_exact_mapping_pk_en_auxiliary_"
    "context_dynamic_castle_action_and_speaker_tokens_shirobito_mining_"
    "engineer_tunnel_wall_water_source_and_siege_context_project_tunnel_"
    "siege_miner_corps_fortification_and_strategic_stronghold_terminology_"
    "shared_success_report_canonical_current_layout_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(1223, 1229):
        if TUNNEL_SIEGE_TERM not in "\n".join(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        ):
            raise RuntimeError(
                f"segment 876 tunnel-siege canonical drifted: {record_id}"
            )
    if "요해" not in raw_translations["15:1226:0"]:
        raise RuntimeError("segment 876 1226 要害 semantics drifted")
    if "아군 피해를 줄이면서" not in raw_translations["15:1224:0"]:
        raise RuntimeError("segment 876 1224 friendly-damage meaning drifted")
    if not raw_translations["15:1228:0"].endswith("만들고자"):
        raise RuntimeError("segment 876 1228 live 0143 stem drifted")
    if tuple(raw_translations[f"15:1229:{i}"] for i in range(3)) != (
        "에",
        "을(를) 걸어\n방비를 깎는 데 성공하",
        "!",
    ):
        raise RuntimeError("segment 876 1229 dynamic action/castle report drifted")
    if not raw_translations["15:1229:1"].endswith("성공하"):
        raise RuntimeError("segment 876 1229 live 0143 stem drifted")

    for record_id in range(1230, 1233):
        if CORE.source_literals(source_records, record_id) != TUNNEL_SUCCESS_SOURCE:
            raise RuntimeError(
                f"segment 876 tunnel success source canonical drifted: {record_id}"
            )
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(3)
        )
        if actual != TUNNEL_SUCCESS_REPORT:
            raise RuntimeError(
                f"segment 876 tunnel success translation drifted: {record_id}"
            )

    joined = "\n".join(translations.values())
    for required in ("땅굴 공략", "광부대", "요해", "견고"):
        if required not in joined:
            raise RuntimeError(f"segment 876 siege terminology drifted: {required}")
    if any(term in joined for term in ("두더지", "땅굴 공격", "광부 부대")):
        raise RuntimeError("segment 876 retained forbidden terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
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
        raise RuntimeError("segment 876 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S876",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "exact_tunnel_success_records": 3,
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
