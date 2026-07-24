#!/usr/bin/env python3
"""Build Base authoring segment 1000 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment999 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B119_S1000.private.v1.jsonl"
)
SEGMENT = 1000
RecordKey = tuple[int, int]

TRANSLATIONS_BY_RECORD: dict[RecordKey, tuple[str, ...]] = {
    (17, 7): (
        "강화 사절이 효과를 보았군요\n"
        "방침을 두고 서로 갈라선 모양입니다",
    ),
    (17, 8): (
        "작전대로 쓰리노부세를 쓴다\n",
        "오토모",
        "의 선봉을 유인해 복병으로 친다",
    ),
    (17, 9): (
        "다다무네",
        "! ",
        "도시히사",
        "!\n너희는 샛길에 병사를 매복시켜라!",
    ),
    (17, 10): ("명을 받들겠소…",),
    (17, 11): ("맡겨 주시오!\n그런데 정작 미끼는 누가 맡소?",),
    (17, 12): (
        "혼고",
        " 공, 위험한 역할이지만 맡아 주겠소?\n"
        "아군 진 깊숙이 적을 유인해야 하오",
    ),
    (17, 13): (
        "알겠소! 소인도 ",
        "시마즈",
        " 일문의 말석\n대임을 훌륭히 완수해 보이겠소이다",
    ),
    (17, 14): (
        "요시히로",
        "는 강가에 진을 치고\n복병을 들키지 않도록 하라",
    ),
    (17, 15): (
        "계책이 무사히 성공하면\n",
        "이에히사",
        "에게도 공세에 나서 달라고 하겠다",
    ),
    (17, 16): (
        "이런 소수 병력이 선봉이라니 우습구나!\n"
        "당장 쓸어버려 주마!!",
    ),
    (17, 17): (
        "놈들이 미끼를 물었군…\n"
        "깊이 끌어들인다! 철수를 시작하라!",
    ),
}
RAW_TRANSLATIONS = {
    f"{block_id}:{record_id}:{literal_id}": translation
    for (block_id, record_id), translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    key: len(translations)
    for key, translations in TRANSLATIONS_BY_RECORD.items()
}
PK_RECORD_MAP = {key: key for key in RECORD_ARITIES}
EXPECTED_BASE_JP = {
    (17, 7): (
        "講和の使者が効きましたな\n"
        "方針を巡って仲違いしたのでしょう",
    ),
    (17, 8): (
        "手筈通り、釣り野伏を使うぞ\n",
        "大友",
        "の先陣を誘引し、伏兵にて叩くのだ",
    ),
    (17, 9): (
        "忠棟",
        "！　",
        "歳久",
        "！\nぬしらは側道に兵を伏せよ！",
    ),
    (17, 10): ("御意にござる…",),
    (17, 11): ("お任せくだされ！\nして、肝心の釣り役は？",),
    (17, 12): (
        "北郷",
        "殿、危うい役だが受けてくれるか\n"
        "自陣深くまで敵を釣らねばならぬ",
    ),
    (17, 13): (
        "承知！　それがしも",
        "島津",
        "一門の端くれ\n大役、見事に果たしてみせましょうぞ",
    ),
    (17, 14): (
        "義弘",
        "は河畔に陣を敷き\n伏兵を察知されぬようにせよ",
    ),
    (17, 15): (
        "無事に策が成ったならば\n",
        "家久",
        "にも打って出てもらうぞ",
    ),
    (17, 16): (
        "この寡兵が先鋒とは笑わせる！\n"
        "すぐさま蹴散らしてくれるわ！！",
    ),
    (17, 17): (
        "奴ら、食いついたな…\n"
        "誘い込むぞ！　撤退を始めよ！",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    (17, 8): (
        "手筈通り、釣り野伏を使う\n",
        "大友",
        "の先陣を誘引し、伏兵にて叩くぞ",
    ),
    (17, 9): (
        "まず伏兵の為に敵を釣る必要がある\n"
        "北郷殿、受けてくれるか？",
    ),
    (17, 10): (
        "承知！　それがしも島津一門の端くれ\n"
        "大役、見事に果たしてみせましょうぞ",
    ),
    (17, 11): ("お任せくだされ！",),
    (17, 12): (
        "さて肝心の釣り役だが\n",
        "北郷",
        " 殿、受けてくれるか？",
    ),
}
EXPECTED_BASE_GAPS = {
    (17, 7): ("", "050505"),
    (17, 8): ("", "1B4333", "1B435A", "050505"),
    (17, 9): (
        "1B4331",
        "1B435A",
        "1B4331",
        "1B435A",
        "050505",
    ),
    (17, 10): ("", "050505"),
    (17, 11): ("", "050505"),
    (17, 12): ("1B4331", "1B435A", "050505"),
    (17, 13): ("", "1B4333", "1B435A", "050505"),
    (17, 14): ("1B4331", "1B435A", "050505"),
    (17, 15): ("", "1B4331", "1B435A", "050505"),
    (17, 16): ("", "050505"),
    (17, 17): ("", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    (17, 9): ("", "050505"),
    (17, 12): ("", "1B4331", "1B435A", "050505"),
}
ARCHIVE_DIGESTS = {
    "base_jp": "A7BB5C2AC3598EA81085091D6998E1FF21E621F09378A1B40BFDDA64E767DC88",
    "base_current": "A8A0B0F1BA34DDC8FC2D5338787E9AE3BBF5BC03FB60614A0F5AE2206B906EA4",
    "base_sc": "332AA1033C3008D64A19625DF74F4BE0572EEC757EC2A77C6231322A9CF2655D",
    "base_tc": "332AA1033C3008D64A19625DF74F4BE0572EEC757EC2A77C6231322A9CF2655D",
    "pk_jp": "77F5ED9B7E4F7EA262774CCF2ECE17935E2ED2B85115A48DABF25E28AD8925FE",
    "pk_current": "F19D9D0F48F804A1D0F4996928098C56E9907E5358AE3E0D561C2FD598F19193",
    "pk_sc": "332AA1033C3008D64A19625DF74F4BE0572EEC757EC2A77C6231322A9CF2655D",
    "pk_tc": "332AA1033C3008D64A19625DF74F4BE0572EEC757EC2A77C6231322A9CF2655D",
    "pk_en": "332AA1033C3008D64A19625DF74F4BE0572EEC757EC2A77C6231322A9CF2655D",
}
PK_EN_VISIBLE_KEYS: set[RecordKey] = set()
CURRENT_ELLIPSIS_COORDINATES = {
    "17:10:0",
    "17:17:0",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_COORDINATES = set(RAW_TRANSLATIONS)
HISTORICAL_EVIDENCE_URLS = {
    "北郷_reading": (
        "https://www.city.miyakonojo.miyazaki.jp/site/"
        "jidaibunkazai/3791.html"
    ),
    "北郷_history": (
        "https://www.city.miyakonojo.miyazaki.jp/site/kanko/10419.html"
    ),
    "釣り野伏": (
        "https://crd.ndl.go.jp/reference/entry/index.php?"
        "id=1000098821&page=ref_view"
    ),
}
BASIS = (
    "review_queue_base_msggame_B119_C_pristine_local_pc_jp_authoritative_"
    "shimazu_tsurinobuse_event_with_identity_base_pk_block17_mapping_"
    "exact_base_pk_jp_sc_tc_and_empty_pk_en_subset_digests_explicit_pk_"
    "scene_recomposition_17_8_through_17_12_and_gap_divergences_17_9_"
    "17_12_fixed_colour_tags_current_line_counts_protected_signatures_"
    "project_ellipsis_hongo_name_reading_and_tsurinobuse_historical_"
    "evidence_static_retranslated_only_no_korean_build_authority"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if any(key != mapped for key, mapped in PK_RECORD_MAP.items()):
        raise RuntimeError("segment 1000 identity Base-to-PK mapping drifted")
    divergences = {
        key
        for key in RECORD_ARITIES
        if EXPECTED_BASE_JP[key] != EXPECTED_PK_JP[key]
    }
    if divergences != {
        (17, 8),
        (17, 9),
        (17, 10),
        (17, 11),
        (17, 12),
    }:
        raise RuntimeError("segment 1000 PK wording divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "쓰리노부세",
        "오토모",
        "다다무네",
        "도시히사",
        "혼고",
        "시마즈",
        "요시히로",
        "이에히사",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 1000 required terminology drifted: {required}"
            )
    if "호고" in joined:
        raise RuntimeError("segment 1000 forbidden name retained: 호고")
    if PK_EN_VISIBLE_KEYS:
        raise RuntimeError("segment 1000 block 17 PK EN visibility drifted")
    if "".join(TRANSLATIONS_BY_RECORD[(17, 8)]) != (
        "작전대로 쓰리노부세를 쓴다\n"
        "오토모의 선봉을 유인해 복병으로 친다"
    ):
        raise RuntimeError("segment 1000 tsurinobuse context drifted")
    if "".join(TRANSLATIONS_BY_RECORD[(17, 9)]) != (
        "다다무네! 도시히사!\n"
        "너희는 샛길에 병사를 매복시켜라!"
    ):
        raise RuntimeError("segment 1000 coloured-name spacing drifted")
    if TRANSLATIONS_BY_RECORD[(17, 12)][0] != "혼고":
        raise RuntimeError("segment 1000 Hongo reading drifted")
    if len(HISTORICAL_EVIDENCE_URLS) != 3:
        raise RuntimeError("segment 1000 evidence registry drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 1000 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows, _records = PREVIOUS.build_general_rows(
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
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 1000 validated count drifted")
    if any(
        row["scope_classification"] != "retranslated"
        or row["runtime_review"] != "not_required"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 1000 classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B119_S1000",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": len(rows),
                "runtime_fragment_pending": 0,
                "explicit_pk_mapping": {
                    f"{key[0]}:{key[1]}": (
                        f"{mapped[0]}:{mapped[1]}"
                    )
                    for key, mapped in PK_RECORD_MAP.items()
                },
                "base_pk_jp_literal_divergence_records": [
                    "17:8",
                    "17:9",
                    "17:10",
                    "17:11",
                    "17:12",
                ],
                "base_pk_jp_gap_divergence_records": [
                    "17:9",
                    "17:12",
                ],
                "pristine_current_gap_divergence_records": [],
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
