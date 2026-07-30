#!/usr/bin/env python3
"""Build Base authoring segment 999 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment998 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B119_S999.private.v1.jsonl"
)
SEGMENT = 999
RecordKey = tuple[int, int]

FRONTLINE_TALENT = (
    "이 최전선의 성이야말로\n내 재능이 빛날 곳이다",
)
TRANSLATIONS_BY_RECORD: dict[RecordKey, tuple[str, ...]] = {
    (16, 76): ("자, 고메고로자도\n한바탕 일해 볼까",),
    (16, 77): ("화승총을 만지지 않으면\n솜씨가 무뎌질 듯하군",),
    (16, 78): ("…잠시 쉬어 가는 건 어떤가",),
    (16, 79): FRONTLINE_TALENT,
    (16, 80): FRONTLINE_TALENT,
    (16, 81): ("후방 성에서 정무에 힘써\n내 진면목을 보여야 한다",),
    (16, 82): ("에서라면\n내 지략을 살릴 수 있으리라",),
    (16, 83): ("의 건설은\n내 특기다",),
    (16, 84): ("성하 시설의 증축 상한은\n시설마다 다르다던데",),
    (16, 85): ("전선의 성에서\n무용을 떨치고자 하는 바",),
    (16, 86): ("후방 성에서 정무에\n전념해 보고 싶군…",),
    (17, 3): (
        "이처럼 우세한 상황에서 강화라니…?\n",
        "쓰노쿠마",
        " 공은 지나치게 소극적이오!",
    ),
    (17, 4): (
        "이리된 이상 우리가 선봉에 서서\n"
        "강제로라도 전쟁을 시작할 수밖에 없다",
    ),
    (17, 5): (
        "다키타",
        "와 ",
        "사에키",
        "이(가) 멋대로 출진했다고…!?\n"
        "강화를 깨고 오토모를 무너뜨릴 셈인가…!",
    ),
    (17, 6): (
        "도시히사",
        "의 말대로군\n",
        "오토모",
        "군이 일부만 나왔구나",
    ),
}
RAW_TRANSLATIONS = {
    f"{block_id}:{record_id}:{literal_id}": translation
    for (block_id, record_id), translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES: dict[RecordKey, int] = {
    **{
        (16, record_id): 1
        for record_id in range(76, 87)
    },
    (17, 2): 1,
    (17, 3): 3,
    (17, 4): 1,
    (17, 5): 4,
    (17, 6): 4,
}
PK_RECORD_MAP = {key: key for key in RECORD_ARITIES}
EXPECTED_BASE_JP = {
    (16, 76): ("さてさて、米五郎左\nひと働き致そうか",),
    (16, 77): ("火縄に触れておらぬと\n腕が鈍りそうだ",),
    (16, 78): ("……一服、いかがかな",),
    (16, 79): ("ここ前線の城こそ\n我が才の輝く場所",),
    (16, 80): ("ここ前線の城こそ\n我が才の輝く場所",),
    (16, 81): ("後方城で政務に励む\n我が本領を見せねば",),
    (16, 82): ("ならば\n我が知を活かせよう",),
    (16, 83): ("の建設は\n我が得手とするところ",),
    (16, 84): ("城下施設の増築上限は\n施設によって違うとか",),
    (16, 85): ("前線の城にて\n武を振るいたいもの",),
    (16, 86): ("後方城にて政務に\n専念してみたい…",),
    (17, 2): ("",),
    (17, 3): (
        "この優勢な状況で講和せよとな…？\n",
        "角隈",
        "殿は弱腰が過ぎる！",
    ),
    (17, 4): (
        "こうなれば、我らが先陣を切って\n"
        "強引にでも開戦するしかあるまい",
    ),
    (17, 5): (
        "田北",
        "と",
        "佐伯",
        "が抜け駆けじゃと…！？\n講和を、大友を潰す気か…！",
    ),
    (17, 6): (
        "歳久",
        "の言うた通りじゃ\n",
        "大友",
        "軍が一部だけ出てきたぞ",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    (16, 79): ("ここ前線の城での\n武働きこそ我が本領",),
    (16, 81): ("後方の城での政務…\n我が本領の見せ所",),
    (16, 86): ("後方の城にて政務に\n専念してみたい…",),
    (17, 5): (
        "田北",
        "と",
        "佐伯",
        "が抜け駆けじゃと…！？\n講和を、",
        "大友",
        "を潰す気か…！",
    ),
}
EXPECTED_BASE_GAPS = {
    **{
        (16, record_id): ("", "050505")
        for record_id in range(76, 82)
    },
    (16, 82): ("02463F", "050505"),
    (16, 83): ("023C", "050505"),
    (16, 84): ("", "050505"),
    (16, 85): ("", "01432C020000050505"),
    (16, 86): ("", "050505"),
    (17, 2): ("", "050505"),
    (17, 3): ("", "1B4331", "1B435A", "050505"),
    (17, 4): ("", "050505"),
    (17, 5): (
        "1B4331",
        "1B435A",
        "1B4331",
        "1B435A",
        "050505",
    ),
    (17, 6): (
        "1B4331",
        "1B435A",
        "1B4333",
        "1B435A",
        "050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    (16, 81): ("", "014312040000050505"),
    (16, 85): ("", "014338020000050505"),
    (17, 5): (
        "1B4331",
        "1B435A",
        "1B4331",
        "1B435A",
        "1B4333",
        "1B435A",
        "050505",
    ),
}
ARCHIVE_DIGESTS = {
    "base_jp": "D9A3FD2102FF3A4EEE16CCA8636536FC41CE8D6D5C552AFF97FAB0E2373DABC3",
    "base_current": "9FE3ED6CE5FCA0710DD2470BFAB9B320DA5EAD06B846037C3CADA812B4929FA2",
    "base_sc": "6D0AB7B18FFA349ED5DDD137B6EDA92207B4513A8BF27797D81DFAE8E3B8AEC7",
    "base_tc": "968261A7DB3108B7053697B05E047BDEE19F693FD3AB9E5DB291304F58802369",
    "pk_jp": "D3B214F11D966FFA41DC7B3821BCCEC0204EF593984926AD9044749A5E34C746",
    "pk_current": "B3C616CAB18467C2F65DDF6A978701F021ED9D46D705A00BC8D9A52A703ED884",
    "pk_sc": "6D0AB7B18FFA349ED5DDD137B6EDA92207B4513A8BF27797D81DFAE8E3B8AEC7",
    "pk_tc": "968261A7DB3108B7053697B05E047BDEE19F693FD3AB9E5DB291304F58802369",
    "pk_en": "8D1F18E3E8913A133B529D7E69B9AE50747A0B55FD205B81F7CA2F63A00721D6",
}
PK_EN_VISIBLE_KEYS = {
    (16, record_id)
    for record_id in range(76, 87)
}
CURRENT_ELLIPSIS_COORDINATES = {
    "16:78:0",
    "16:86:0",
    "17:3:0",
    "17:5:3",
}
EXCLUDED_NONVISIBLE_COORDINATES = {"17:2:0": ""}
DYNAMIC_COORDINATES = {
    "16:82:0",
    "16:83:0",
    "16:85:0",
}
STATIC_COORDINATES = set(RAW_TRANSLATIONS) - DYNAMIC_COORDINATES
EXPECTED_BASE_MORPHOLOGY = {
    556: ("입니다", "다", "이오"),
}
EXPECTED_PK_MORPHOLOGY = {
    568: ("입니다", "다", "이오"),
    1042: ("군", "여"),
}
HISTORICAL_EVIDENCE_URLS = {
    "角隈": (
        "https://tree-novel.com/article/"
        "ee9810b86a157c14754eeb4315ced5e1.html"
    ),
    "田北": (
        "https://www.city.taketa.oita.jp/material/files/group/23/"
        "1syou2.pdf"
    ),
}
BASIS = (
    "review_queue_base_msggame_B119_C_pristine_local_pc_jp_authoritative_"
    "officer_assignment_maxims_and_otomo_siege_dialogue_with_identity_"
    "base_pk_block16_17_mapping_exact_base_pk_jp_sc_tc_and_pk_en_subset_"
    "digests_explicit_pk_wording_and_gap_divergences_hidden_empty_17_2_"
    "excluded_fixed_colour_tags_castle_and_facility_runtime_prefixes_"
    "morphology_roots_556_568_1042_current_line_counts_protected_"
    "signatures_project_ellipsis_name_reading_evidence_and_shared_exact_"
    "repeat_object_16_79_16_80_no_korean_build_authority"
)

build_general_rows = PREVIOUS.build_general_rows
annotate_general_morphology = PREVIOUS.annotate_general_morphology


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if any(key != mapped for key, mapped in PK_RECORD_MAP.items()):
        raise RuntimeError("segment 999 identity Base-to-PK mapping drifted")
    divergences = {
        key
        for key in RECORD_ARITIES
        if EXPECTED_BASE_JP[key] != EXPECTED_PK_JP[key]
    }
    if divergences != {(16, 79), (16, 81), (16, 86), (17, 5)}:
        raise RuntimeError("segment 999 PK wording divergence drifted")
    if (
        TRANSLATIONS_BY_RECORD[(16, 79)] is not FRONTLINE_TALENT
        or TRANSLATIONS_BY_RECORD[(16, 80)] is not FRONTLINE_TALENT
        or EXPECTED_BASE_JP[(16, 79)] != EXPECTED_BASE_JP[(16, 80)]
        or EXPECTED_BASE_GAPS[(16, 79)] != EXPECTED_BASE_GAPS[(16, 80)]
    ):
        raise RuntimeError(
            "segment 999 repeated source/gap/Korean tuple identity drifted"
        )
    if (
        EXPECTED_BASE_GAPS[(16, 82)][0] != "02463F"
        or not raw_translations["16:82:0"].startswith("에서라면")
    ):
        raise RuntimeError("segment 999 castle-prefix direction drifted")
    if (
        EXPECTED_BASE_GAPS[(16, 83)][0] != "023C"
        or not raw_translations["16:83:0"].startswith("의 건설은")
    ):
        raise RuntimeError("segment 999 facility-prefix direction drifted")
    morphology_stem = raw_translations["16:85:0"]
    if {
        morphology_stem + terminal
        for terminal in EXPECTED_BASE_MORPHOLOGY[556]
    } != {
        "전선의 성에서\n무용을 떨치고자 하는 바입니다",
        "전선의 성에서\n무용을 떨치고자 하는 바다",
        "전선의 성에서\n무용을 떨치고자 하는 바이오",
    }:
        raise RuntimeError("segment 999 root 556 composition drifted")
    if "".join(TRANSLATIONS_BY_RECORD[(17, 5)]) != (
        "다키타와 사에키이(가) 멋대로 출진했다고…!?\n"
        "강화를 깨고 오토모를 무너뜨릴 셈인가…!"
    ):
        raise RuntimeError("segment 999 coloured-name spacing drifted")
    joined = "\n".join(translations.values())
    for required in (
        "고메고로자",
        "화승총",
        "쓰노쿠마",
        "다키타",
        "사에키",
        "도시히사",
        "오토모",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 999 required terminology drifted: {required}"
            )
    for forbidden in ("기타키타", "다바루"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 999 forbidden name retained: {forbidden}"
            )
    if len(HISTORICAL_EVIDENCE_URLS) != 2:
        raise RuntimeError("segment 999 evidence registry drifted")
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 999 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows, records = build_general_rows(
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
        archive_digests=ARCHIVE_DIGESTS,
        pk_en_visible_keys=PK_EN_VISIBLE_KEYS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        static_coordinates=STATIC_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    annotate_general_morphology(
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        records_by_label=records,
        expected_base=EXPECTED_BASE_MORPHOLOGY,
        expected_pk=EXPECTED_PK_MORPHOLOGY,
    )
    rows_by_coordinate = {
        str(row["coordinate"]): row
        for row in rows
    }
    rows_by_coordinate["16:82:0"]["runtime_token_prefix"] = "02463F"
    rows_by_coordinate["16:82:0"]["runtime_token_role"] = "castle_name"
    rows_by_coordinate["16:83:0"]["runtime_token_prefix"] = "023C"
    rows_by_coordinate["16:83:0"]["runtime_token_role"] = (
        "facility_or_value_name"
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
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 999 validated count drifted")
    if sum(
        row["scope_classification"] == "retranslated"
        for row in rows
    ) != 20 or sum(
        row["scope_classification"] == "runtime_fragment_pending"
        for row in rows
    ) != 3:
        raise RuntimeError("segment 999 classification count drifted")
    if any(
        row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 999 Korean authority flag drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B119_S999",
                "source_literal_count": 24,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "retranslated": 20,
                "runtime_fragment_pending": 3,
                "explicit_pk_mapping": {
                    f"{key[0]}:{key[1]}": (
                        f"{mapped[0]}:{mapped[1]}"
                    )
                    for key, mapped in PK_RECORD_MAP.items()
                },
                "base_pk_jp_literal_divergence_records": [
                    "16:79",
                    "16:81",
                    "16:86",
                    "17:5",
                ],
                "base_pk_jp_gap_divergence_records": [
                    "16:81",
                    "16:85",
                    "17:5",
                ],
                "pristine_current_gap_divergence_records": [],
                "excluded_nonvisible_coordinates": ["17:2:0"],
                "runtime_fragment_pending_coordinates": sorted(
                    DYNAMIC_COORDINATES
                ),
                "ellipsis_coordinates": sorted(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
