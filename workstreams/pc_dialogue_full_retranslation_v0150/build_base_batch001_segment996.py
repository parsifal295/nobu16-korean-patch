#!/usr/bin/env python3
"""Build Base authoring segment 996 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment995 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S996.private.v1.jsonl"
)
SEGMENT = 996
TRANSLATIONS_BY_RECORD = {
    13: ("의 금전 수입은\n더 늘릴 여지가 있군…",),
    14: ("서둘러 전쟁에 대비해\n휘하 병력을 정비해야겠군",),
    15: ("자, 개발 용지에는\n무엇을 지을까",),
    16: ("의 회유로\n우리 가문에 보탬이 되게",),
    17: ("에 선동을 벌여\n기회가 닿으면 잇키를…",),
    18: ("에 위협을 가해\n적의 지배력을 약화하리라",),
    19: ("때는 지금… 아니,\n아직은 아니겠군",),
    20: ("쳐라, 몰아쳐라!\n판도를 넓혀라",),
    21: ("아카조나에 정예들이여\n이제 전투를 준비하라!",),
    22: ("큭큭, 다음엔 무엇을\n꾸며 볼까",),
    23: (
        "가보가 남는다면\n",
        "에게 줄 수도… 이런",
    ),
    24: (
        "지금이라면",
        "에\n시설을 건설할 수 있는데",
    ),
    25: (
        "의 성하 시설은\n증축할 좋은 기회라 생각",
        "만",
    ),
    26: ("지금 우리 가문이라면\n정책을 더 충실히 펼칠 수 있겠군",),
    27: ("의 기세는\n날로 더해지는군…",),
    28: ("의 성하는\n더없이 번화하군",),
    29: ("우리 영지는 더없이\n번영한 듯하군",),
    30: ("대관이 된 이상\n그에 걸맞은 활약을 해야겠군…",),
    31: (
        "본거지로 삼은",
        "에서\n전선까지 너무 멀어 불편",
    ),
}
RAW_TRANSLATIONS = {
    f"16:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_KEYS = tuple((16, record_id) for record_id in range(13, 32))
PK_RECORD_MAP = {key: key for key in RECORD_KEYS}
EXPECTED_SOURCE_ARITIES = {
    **{(16, record_id): 1 for record_id in range(13, 32)},
    (16, 15): 2,
    (16, 23): 2,
    (16, 24): 2,
    (16, 25): 2,
    (16, 31): 2,
}
EXPECTED_CURRENT_ARITIES = {
    **EXPECTED_SOURCE_ARITIES,
    (16, 15): 1,
}
STATIC_RECORD_IDS = {14, 15, 19, 20, 21, 22, 26, 29, 30}
STATIC_COORDINATES = {
    f"16:{record_id}:0" for record_id in STATIC_RECORD_IDS
}
ELLIPSIS_COORDINATES = {
    "16:13:0",
    "16:17:0",
    "16:19:0",
    "16:23:1",
    "16:27:0",
    "16:30:0",
}
EXPECTED_LITERAL_DIVERGENCES = {
    "JP": {
        (16, 23),
        (16, 24),
        (16, 25),
        (16, 26),
        (16, 29),
        (16, 30),
    },
    "SC": set(),
    "TC": set(),
}
EXPECTED_GAP_DIVERGENCES = {
    "JP": {
        (16, 15),
        (16, 16),
        (16, 24),
        (16, 25),
        (16, 29),
        (16, 31),
    },
    "SC": set(),
    "TC": set(),
}
EXPECTED_PRISTINE_CURRENT_GAP_DIVERGENCES = {(16, 15), (16, 29)}
CASTLE_TOKEN = "02463F"
FACILITY_TOKEN = "023C"
SETTLEMENT_TOKEN = "029632"
FORCE_TOKEN = "025032"
TOKEN_CONTRACTS = (
    ((16, 13), 0, 0, CASTLE_TOKEN),
    ((16, 16), 0, 0, FACILITY_TOKEN),
    ((16, 17), 0, 0, SETTLEMENT_TOKEN),
    ((16, 18), 0, 0, SETTLEMENT_TOKEN),
    ((16, 24), 1, 0, CASTLE_TOKEN),
    ((16, 25), 0, 0, CASTLE_TOKEN),
    ((16, 27), 0, 0, FORCE_TOKEN),
    ((16, 28), 0, 0, CASTLE_TOKEN),
    ((16, 31), 1, 1, CASTLE_TOKEN),
)
EXPECTED_BASE_MORPHOLOGY = {
    1: ("소승", "나", "저", "소인", "이 몸"),
    556: ("입니다", "다", "이오"),
    1054: ("합시다", "듯"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY = {
    1: EXPECTED_BASE_MORPHOLOGY[1],
    568: EXPECTED_BASE_MORPHOLOGY[556],
    1066: EXPECTED_BASE_MORPHOLOGY[1054],
    1096: EXPECTED_BASE_MORPHOLOGY[1084],
}
UNRESOLVED_RUNTIME_BRANCHES = (
    "16:16:0/root1054",
    "16:25:0/root1084_plain_da",
    "16:31:1/root556",
)
ARCHIVE_DIGESTS = {
    "base_jp": "9CAACA26B5DA3A9690DA29542C32D24B54D56A83BADDF0C4A97D76DA07DD50AA",
    "base_current": "804E87FB0722BEDD55AB359A81F5E240FEDDEE284A628A98A6C3011759912CD9",
    "base_sc": "A985ADB3328721588542C9E47D5BD0763AB94F47036D73FDC2743A8B81842A3C",
    "base_tc": "A85310F86975E3F3AFFFA202731BE3DFB99BA7A01EEDABE0F4242AF72AD355D9",
    "pk_jp": "25331B90438714D4B77CF4EC041966C35C6373A59EE9761EE960CF73D6E179D4",
    "pk_current": "5C56BA4BEA42D10EA4468113EA45250D768D9ADDA26B4015830A9B632AA2F825",
    "pk_sc": "A985ADB3328721588542C9E47D5BD0763AB94F47036D73FDC2743A8B81842A3C",
    "pk_tc": "A85310F86975E3F3AFFFA202731BE3DFB99BA7A01EEDABE0F4242AF72AD355D9",
    "pk_en": "8577E5AC134696F89662B8A37CD0636D2C36D98B7F8E8812649FFE4B07E9781C",
}
EVIDENCE_URLS = {
    "赤備": "https://kotobank.jp/word/%E8%B5%A4%E5%82%99-1260683",
    "代官": "https://kotobank.jp/word/%E4%BB%A3%E5%AE%98-90927",
}
BASIS = (
    "review_queue_base_msggame_B119_B_pristine_base_pc_jp_authoritative_"
    "castle_income_war_readiness_development_plotting_treasure_policy_"
    "prosperity_and_daikan_monologues_with_exact_base16_same_coordinate_"
    "pk_mapping_pc_sc_tc_and_contextual_pk_en_赤備_as_akajonae_when_"
    "formation_name_foregrounded_一揆_as_ikki_当家_as_uri_gamun_代官_as_"
    "daegwan_版図_as_pando_dynamic_castle_settlement_pronoun_and_"
    "morphology_terminals_current_line_counts_and_project_ellipsis_"
    "preserved_no_korean_build_authority"
)


def assert_semantics(translations: dict[str, str]) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "잇키",
        "판도",
        "아카조나에",
        "대관",
        "성하 시설",
        "본거지",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 996 required meaning drifted: {required}")
    for forbidden in (
        "당가",
        "일국일성",
        "군다이",
        "아카조나에의",
        "을(를)",
        "、",
        "。",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 996 forbidden wording retained: {forbidden}"
            )
    if translations["16:25:0"].splitlines()[-1] != "증축할 좋은 기회라 생각":
        raise RuntimeError("segment 996 facility-opportunity stem drifted")
    facility_variants = {
        f"{translations['16:25:0']}{ending}{translations['16:25:1']}".splitlines()[-1]
        for ending in EXPECTED_BASE_MORPHOLOGY[1084]
    }
    if facility_variants != {
        "증축할 좋은 기회라 생각합니다만",
        "증축할 좋은 기회라 생각다만",
        "증축할 좋은 기회라 생각하옵니다만",
    }:
        raise RuntimeError("segment 996 facility-opportunity assembly drifted")
    appeasement_variants = {
        f"{translations['16:16:0']}{ending}".splitlines()[-1]
        for ending in EXPECTED_BASE_MORPHOLOGY[1054]
    }
    if appeasement_variants != {
        "우리 가문에 보탬이 되게합시다",
        "우리 가문에 보탬이 되게듯",
    }:
        raise RuntimeError("segment 996 appeasement morphology drifted")
    distance_variants = {
        f"{translations['16:31:1']}{ending}".splitlines()[-1]
        for ending in EXPECTED_BASE_MORPHOLOGY[556]
    }
    if distance_variants != {
        "전선까지 너무 멀어 불편입니다",
        "전선까지 너무 멀어 불편다",
        "전선까지 너무 멀어 불편이오",
    }:
        raise RuntimeError("segment 996 distance morphology drifted")
    if not all(url.startswith("https://kotobank.jp/") for url in EVIDENCE_URLS.values()):
        raise RuntimeError("segment 996 historical evidence drifted")


def main() -> int:
    prepared, translations, rows, candidate_sha256 = (
        PREVIOUS.build_segment_rows(
            output=OUTPUT,
            segment=SEGMENT,
            record_keys=RECORD_KEYS,
            pk_record_map=PK_RECORD_MAP,
            raw_translations=RAW_TRANSLATIONS,
            source_arities=EXPECTED_SOURCE_ARITIES,
            current_arities=EXPECTED_CURRENT_ARITIES,
            hidden_coordinates=set(),
            static_coordinates=STATIC_COORDINATES,
            ellipsis_coordinates=ELLIPSIS_COORDINATES,
            literal_divergences=EXPECTED_LITERAL_DIVERGENCES,
            gap_divergences=EXPECTED_GAP_DIVERGENCES,
            pristine_current_gap_divergences=(
                EXPECTED_PRISTINE_CURRENT_GAP_DIVERGENCES
            ),
            archive_digests=ARCHIVE_DIGESTS,
            basis=BASIS,
            semantic_assertions=assert_semantics,
        )
    )
    PREVIOUS.assert_dynamic_runtime_contracts(
        prepared,
        segment=SEGMENT,
        record_keys=RECORD_KEYS,
        pk_record_map=PK_RECORD_MAP,
        token_contracts=TOKEN_CONTRACTS,
        expected_base_morphology=EXPECTED_BASE_MORPHOLOGY,
        expected_pk_morphology=EXPECTED_PK_MORPHOLOGY,
        translations=translations,
        static_coordinates=STATIC_COORDINATES,
        rows=rows,
    )
    if len(rows) != 23 or len(translations) != 23:
        raise RuntimeError("segment 996 decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S996",
                "source_literal_count": 24,
                "current_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": len(STATIC_COORDINATES),
                "runtime_fragment_pending": (
                    len(rows) - len(STATIC_COORDINATES)
                ),
                "explicit_pk_mapping": "base16_same_coordinate",
                "base_pk_literal_divergences": {
                    language: [
                        f"{key[0]}:{key[1]}"
                        for key in sorted(divergences)
                    ]
                    for language, divergences in (
                        EXPECTED_LITERAL_DIVERGENCES.items()
                    )
                },
                "base_pk_gap_divergences": {
                    language: [
                        f"{key[0]}:{key[1]}"
                        for key in sorted(divergences)
                    ]
                    for language, divergences in (
                        EXPECTED_GAP_DIVERGENCES.items()
                    )
                },
                "pristine_current_gap_divergences": [
                    f"{key[0]}:{key[1]}"
                    for key in sorted(
                        EXPECTED_PRISTINE_CURRENT_GAP_DIVERGENCES
                    )
                ],
                "runtime_unresolved_branches": list(
                    UNRESOLVED_RUNTIME_BRANCHES
                ),
                "ellipsis_coordinates": sorted(ELLIPSIS_COORDINATES),
                "evidence_urls": EVIDENCE_URLS,
                "lf_count": sum(
                    text.count("\n") for text in translations.values()
                ),
                "candidate_sha256": candidate_sha256,
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
