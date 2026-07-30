#!/usr/bin/env python3
"""Build Base authoring segment 939 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment938 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
MORPHOLOGY = PREVIOUS.MORPHOLOGY
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S939.private.v1.jsonl"
)
SEGMENT = 939
TRANSLATIONS_BY_RECORD = {
    1838: (
        "의",
        "은(는) 틈만 나면\n우리 가문의 성을 노리는 모양…",
    ),
    1839: (
        "우리 가문은 여러 세력의 표적이 되어 있으며\n그중에서도",
        "의",
        "은(는)\n가장 위험한 상대라 할",
    ),
    1840: (
        "은(는) 우리 가문보다 규모가 작지만\n결코 방심해서는",
        ", 경계해야 할 상대",
    ),
    1841: (
        "의 규모는 우리 가문과 비슷합니다\n배후를 찔리지 않도록\n"
        "병력을 온존해 두어야 하겠습니다",
    ),
    1842: (
        "은(는) 우리 가문보다 한 수 위인 적\n"
        "아무런 계책 없이 맞서서는 승산이 없으니\n무언가 대책을 마련",
    ),
    1843: (
        "에는 이름난 장수가",
        "만\n결코 경계를 늦춰서는",
    ),
    1844: (
        "에는 명장·",
        "이(가) 있으며\n그 인물의 동향 또한\n승패를 크게 좌우할 것",
    ),
    1845: (
        "에는 이름난 장수가",
        "만\n",
        "등 주력 장수들에 대해서는\n결코 경계를 늦춰서는",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1838: ("の", "は隙あらば、と\n当家の城を狙っている様子…"),
    1839: (
        "当家は複数の勢力から狙われており\n中でも",
        "の",
        "は\nその最たるものと言え",
    ),
    1840: ("は当家より小規模なれど\n決して油断はでき", "相手"),
    1841: (
        "の規模は当家と同程度\n後背を突かれぬよう\n兵力を温存しておくべきかと",
    ),
    1842: (
        "は当家からすれば格上の敵\n無策ではおよそ太刀打ち敵わず\n"
        "何か対応を講じる必要があ",
    ),
    1843: ("には高名な将こそ", "が\n決して警戒を怠っては"),
    1844: ("には名将・", "がおり\nかの者の動向もまた\n勝敗を大きく左右する"),
    1845: (
        "には高名な将こそ",
        "が\n",
        "など主力の将らに対しては\n決して警戒を怠っては",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1838: ("023C", "025132", "050505"),
    1839: ("", "023C", "025132", "01431E040000050505"),
    1840: ("025132", "0143E0020000", "01432C020000050505"),
    1841: ("025132", "050505"),
    1842: ("025132", "01435A040000050505"),
    1843: ("025132", "0143A0000000", "01431C030000050505"),
    1844: ("025132", "024933", "014356020000050505"),
    1845: ("025132", "0143A0000000", "024933", "01431C030000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1838: ("023C", "025132", "050505"),
    1839: ("", "023C", "025132", "01432A040000050505"),
    1840: ("025132", "0143EC020000", "014338020000050505"),
    1841: ("025132", "050505"),
    1842: ("025132", "014366040000050505"),
    1843: ("025132", "0143A0000000", "014328030000050505"),
    1844: ("025132", "024933", "014362020000050505"),
    1845: ("025132", "0143A0000000", "024933", "014328030000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:1838:1"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1838): (
        ("的", "似乎正趁隙\n觊觎我方的城……"),
        ("023C", "025132", "050505"),
    ),
    ("SC", 1839): (
        ("众多势力正觊觎本家，\n其中", "的", "\n最该当心吧。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1840): (
        ("的规模虽在本家之下，\n但依旧大意不得。",),
        ("025132", "050505"),
    ),
    ("SC", 1841): (
        ("需密切关注\n", "的动向……"),
        ("", "025132", "050505"),
    ),
    ("SC", 1842): (
        ("的势力在本家之上，\n未采取任何对策的话，绝对无法迎击。\n需要拟定计策才行。",),
        ("025132", "050505"),
    ),
    ("SC", 1843): (("当中虽无高名的武将，\n但务必提防。",), ("025132", "050505")),
    ("SC", 1844): (
        ("中有名将", "，\n其动向亦将\n大大地影响胜负吧。"),
        ("025132", "024933", "050505"),
    ),
    ("SC", 1845): (
        ("中虽无高明的武将，\n但务必提防\n", "等主将。"),
        ("025132", "024933", "050505"),
    ),
    ("TC", 1838): (
        ("的", "似乎正趁隙\n覬覦我方的城……"),
        ("023C", "025132", "050505"),
    ),
    ("TC", 1839): (
        ("眾多勢力正覬覦本家，\n其中", "的", "\n最該當心吧。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1840): (
        ("的規模雖在本家之下，\n但依舊大意不得。",),
        ("025132", "050505"),
    ),
    ("TC", 1841): (
        ("需密切關注\n", "的動向……"),
        ("", "025132", "050505"),
    ),
    ("TC", 1842): (
        ("的勢力在本家之上，\n未採取任何對策的話，絕對無法迎擊。\n非得擬定計策才行。",),
        ("025132", "050505"),
    ),
    ("TC", 1843): (("當中雖無高名的武將，\n但務必提防。",), ("025132", "050505")),
    ("TC", 1844): (
        ("中有名將", "，\n其動向亦將\n大大地影響勝負吧。"),
        ("025132", "024933", "050505"),
    ),
    ("TC", 1845): (
        ("中雖無高明的武將，\n但務必提防\n", "等主將。"),
        ("025132", "024933", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1838: (
        (
            "It would seem that the ",
            " of ",
            " are scouting our castles for signs of weakness.",
        ),
        ("", "025132", "023C", "050505"),
    ),
    1839: (
        (
            "There are numerous clans with their eyes set on us, but the one that stands out most are the ",
            " of ",
            ".",
        ),
        ("", "025132", "023C", "050505"),
    ),
    1840: (
        ("The ", " may be smaller than our clan, but we must not underestimate them."),
        ("", "025132", "050505"),
    ),
    1841: (
        (
            "The ",
            " are of an equal scale to us. We ought to keep a sufficient number of soldiers in reserve to stave off flanking maneuvers.",
        ),
        ("", "025132", "050505"),
    ),
    1842: (
        (
            "The ",
            " have us outmatched. We cannot expect to compete with them if we do not adopt a suitable plan of action.",
        ),
        ("", "025132", "050505"),
    ),
}
AUXILIARY_OVERRIDES = MORPHOLOGY.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B113_A_pristine_base_pc_jp_authoritative_"
    "enemy_threat_scale_reserve_force_countermeasure_and_notable_general_"
    "assessment_with_explicit_base1838_1845_to_pk1868_1875_mapping_exact_"
    "base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_project_uri_gamun_"
    "amureon_gyechaek_eopsi_term_dynamic_house_force_and_officer_tokens_"
    "direction_current_korean_morphology_terminal_corpora_and_cross_"
    "resource_opcode_divergences_recorded_project_ellipsis_pair_current_"
    "line_counts_and_protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    160: ("없사옵니다", "없다", "없습니다"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    736: ("않습니다", "않는다"),
    796: ("안 됩니다", "안 된다", "아니 되옵니다"),
    1054: ("합시다", "듯"),
    1114: ("합시다", "하리라"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    160: EXPECTED_BASE_MORPHOLOGY_TERMINALS[160],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    748: EXPECTED_BASE_MORPHOLOGY_TERMINALS[736],
    808: EXPECTED_BASE_MORPHOLOGY_TERMINALS[796],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1126: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 939 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {1839, 1840, 1842, 1843, 1844, 1845}:
        raise RuntimeError("segment 939 Base-to-PK gap divergence drifted")
    if any(
        EXPECTED_BASE_JP[record_id] != EXPECTED_PK_JP[record_id]
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 939 Base-to-PK literal divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "아무런 계책 없이",
        "온존",
        "명장",
        "주력 장수",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 939 required terminology drifted: {required}")
    for forbidden in ("당가", "무책", "격이 높은 적", "그자"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 939 forbidden phrasing retained: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 939 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(translations) != 16:
        raise RuntimeError("segment 939 visible decision count drifted")


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
    MORPHOLOGY.annotate_morphology_evidence(
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
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 16 or len(validated) != len(translations):
        raise RuntimeError("segment 939 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 939 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S939",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1839,
                    1840,
                    1842,
                    1843,
                    1844,
                    1845,
                ],
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
