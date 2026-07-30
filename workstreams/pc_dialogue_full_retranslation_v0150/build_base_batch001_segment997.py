#!/usr/bin/env python3
"""Build Base authoring segment 997 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment995 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S997.private.v1.jsonl"
)
SEGMENT = 997
TRANSLATIONS_BY_RECORD = {
    32: ("이 가문을 계속 섬겨도\n정말 괜찮은 것일까…",),
    33: (
        "지금의",
        "으로는\n적의 습격을 견뎌 낼 수 있을까…",
    ),
    34: ("군단의 지침을 일임받다니…\n기쁘지만 한편으로는 긴장",),
    35: ("의 성은 멀구나\n군단만 있다면…",),
    36: ("공략 목표가 정해지면\n군비를 갖추자",),
    37: ("군비만 갖춘다면\n웬만한 전력 차이쯤은…",),
    38: ("일손이 모자라는군…\n군 개발에 쓸 노동력을 더…",),
    39: ("대관 자리가 비었군…\n과연 누가 발탁될까",),
    40: ("의 정책으로\n지행지를 자유롭게 바꿀 수 있군…",),
    41: (
        "성주가 없는 성인가?\n그렇다면",
        "에게 기회가 오려나…",
    ),
    42: ("금전을 쌓아 두기만 하는 것은 악수\n정책이야말로 난세의 요체다",),
    43: ("위신을 좌우하는 것은\n주로 지배한 성의 수다",),
    44: ("일국일성의 주인이\n되는 것이 내 바람",),
    45: ("군다이로서는 역시…\n배속된 부하가 있어야 하는데",),
    46: ("콜록, 쿨럭…\n어서 병을 고쳐야 하는데",),
    47: ("큭… 이 정도 상처쯤은\n아무것도 아니지…",),
    48: ("성의 수리는 영내 제책으로\n실행",),
    49: ("자, 슬슬 때가 되었군…\n어떻게 해 줄까",),
    50: ("모성이라니, 과한 칭호로군…\n그저 해야 할 일을 할 뿐이다",),
    51: ("품격을 잃지 않으면\n백성 또한 따르리라",),
    52: ("야망은 아직 이루지 못했건만\n…흥, 어쩔 수 없군",),
}
RAW_TRANSLATIONS = {
    f"16:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_KEYS = tuple((16, record_id) for record_id in range(32, 53))
PK_RECORD_MAP = {key: key for key in RECORD_KEYS}
EXPECTED_SOURCE_ARITIES = {
    **{(16, record_id): 1 for record_id in range(32, 53)},
    (16, 32): 2,
    (16, 33): 2,
    (16, 38): 2,
    (16, 41): 2,
}
EXPECTED_CURRENT_ARITIES = {
    **EXPECTED_SOURCE_ARITIES,
    (16, 32): 1,
    (16, 38): 1,
}
STATIC_RECORD_IDS = {
    32,
    36,
    37,
    38,
    39,
    42,
    43,
    45,
    46,
    47,
    49,
    50,
    51,
    52,
}
STATIC_COORDINATES = {
    f"16:{record_id}:0" for record_id in STATIC_RECORD_IDS
}
ELLIPSIS_COORDINATES = {
    "16:32:0",
    "16:33:1",
    "16:34:0",
    "16:35:0",
    "16:37:0",
    "16:38:0",
    "16:39:0",
    "16:40:0",
    "16:41:1",
    "16:45:0",
    "16:46:0",
    "16:47:0",
    "16:49:0",
    "16:50:0",
    "16:52:0",
}
EXPECTED_LITERAL_DIVERGENCES = {
    "JP": {
        (16, 40),
        (16, 42),
        (16, 43),
        (16, 44),
        (16, 45),
        (16, 48),
        (16, 50),
    },
    "SC": set(),
    "TC": set(),
}
EXPECTED_GAP_DIVERGENCES = {
    "JP": {
        (16, 32),
        (16, 34),
        (16, 36),
        (16, 38),
        (16, 42),
        (16, 43),
        (16, 44),
        (16, 45),
        (16, 46),
        (16, 48),
    },
    "SC": set(),
    "TC": set(),
}
EXPECTED_PRISTINE_CURRENT_GAP_DIVERGENCES = {
    (16, 32),
    (16, 36),
    (16, 38),
    (16, 43),
    (16, 46),
}
CASTLE_TOKEN = "02463F"
POLICY_TOKEN = "023C"
TOKEN_CONTRACTS = (
    ((16, 33), 1, 1, CASTLE_TOKEN),
    ((16, 40), 0, 0, POLICY_TOKEN),
)
EXPECTED_BASE_MORPHOLOGY = {
    1: ("소승", "나", "저", "소인", "이 몸"),
    29: (
        "아버님",
        "어머님",
        "할아버님",
        "할머님",
        "숙부님",
        "숙모님",
        "님",
        "주군님",
        "주군",
        "도련님",
        "공주님",
        "그분",
        "그자",
        "쇼군님",
        "스님",
        "원숭이",
        "놈",
        "누님",
        "형님",
    ),
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
    556: ("입니다", "다", "이오"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY = {
    1: EXPECTED_BASE_MORPHOLOGY[1],
    29: EXPECTED_BASE_MORPHOLOGY[29],
    466: EXPECTED_BASE_MORPHOLOGY[460],
    568: EXPECTED_BASE_MORPHOLOGY[556],
    1096: EXPECTED_BASE_MORPHOLOGY[1084],
}
UNRESOLVED_RUNTIME_BRANCHES = (
    "16:41:0/root1_line_edge_spacing",
    "16:44:0/root556",
    "16:48:0/root1084_plain_da",
)
ARCHIVE_DIGESTS = {
    "base_jp": "FBEB52E2744DEA1B686FC474A9BD3BE672A77C4AA54374121AA3A903A03C5696",
    "base_current": "1F8968C2FFA8A3FA2DD9039575EA5792E06C9D3AEA817030F91BB408B20FFBB8",
    "base_sc": "EA5317299587A026CCCFCF8A7112332B2B0480DCFC5E75490132DC264A91BEC5",
    "base_tc": "90B1772603AF0DFAA915789FA0C362CA1F612CCD6088250F026CA1B9FFB9B3DB",
    "pk_jp": "B06D1CC1D172CE804BDE3D7BB1A8E43DF4BA3FAA9284A983B0501706C9CB7C39",
    "pk_current": "A4CC15099FC9C61C31838E3247DAAE007C83BD64B2F97A79E3DEA5F23C032D03",
    "pk_sc": "EA5317299587A026CCCFCF8A7112332B2B0480DCFC5E75490132DC264A91BEC5",
    "pk_tc": "90B1772603AF0DFAA915789FA0C362CA1F612CCD6088250F026CA1B9FFB9B3DB",
    "pk_en": "237BD577F99921EC7096DC671CC4AAFD5240FE6AE0F1DC3CEDCA27E0E16646F7",
}
EVIDENCE_URLS = {
    "郡代": "https://kotobank.jp/word/%E9%83%A1%E4%BB%A3-58399",
    "知行替": "https://kotobank.jp/word/%E7%9F%A5%E8%A1%8C%E6%9B%BF-324857",
}
BASIS = (
    "review_queue_base_msggame_B119_B_pristine_base_pc_jp_authoritative_"
    "service_anxiety_corps_readiness_county_development_daikan_castle_lord_"
    "policy_prestige_gundai_health_domain_measures_and_bosei_monologues_"
    "with_exact_base16_same_coordinate_pk_mapping_pc_sc_tc_and_contextual_"
    "pk_en_郡代_as_gundai_知行替_as_jihang_reallocation_領内諸策_as_"
    "yeongnae_jechaek_謀聖_as_moseong_dynamic_castle_relation_pronoun_"
    "policy_and_morphology_terminals_current_line_counts_and_project_"
    "ellipsis_preserved_no_korean_build_authority"
)


def assert_semantics(translations: dict[str, str]) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "군단",
        "군 개발",
        "노동력",
        "대관",
        "지행",
        "일국일성",
        "군다이",
        "영내 제책",
        "모성",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 997 required meaning drifted: {required}")
    for forbidden in (
        "지행 교체",
        "영내 정책",
        "모략의 성인",
        "을(를)",
        "、",
        "。",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 997 forbidden wording retained: {forbidden}"
            )
    if (
        translations["16:40:0"].splitlines()[-1]
        != "지행지를 자유롭게 바꿀 수 있군……"
    ):
        raise RuntimeError("segment 997 chigyo reassignment meaning drifted")
    tension_variants = {
        f"{translations['16:34:0']}{ending}".splitlines()[-1]
        for ending in EXPECTED_BASE_MORPHOLOGY[460]
    }
    if tension_variants != {
        "기쁘지만 한편으로는 긴장합니다",
        "기쁘지만 한편으로는 긴장하다",
        "기쁘지만 한편으로는 긴장하겠습니다",
        "기쁘지만 한편으로는 긴장하겠사옵니다",
    }:
        raise RuntimeError("segment 997 tension morphology drifted")
    repair_variants = {
        f"{translations['16:48:0']}{ending}".splitlines()[-1]
        for ending in EXPECTED_BASE_MORPHOLOGY[1084]
    }
    if repair_variants != {
        "실행합니다",
        "실행다",
        "실행하옵니다",
    }:
        raise RuntimeError("segment 997 repair morphology drifted")
    aspiration_variants = {
        f"{translations['16:44:0']}{ending}".splitlines()[-1]
        for ending in EXPECTED_BASE_MORPHOLOGY[556]
    }
    if aspiration_variants != {
        "되는 것이 내 바람입니다",
        "되는 것이 내 바람다",
        "되는 것이 내 바람이오",
    }:
        raise RuntimeError("segment 997 aspiration morphology drifted")
    pronoun_variants = {
        (
            f"{translations['16:41:0']}{pronoun}"
            f"{translations['16:41:1']}"
        ).splitlines()[-1]
        for pronoun in EXPECTED_BASE_MORPHOLOGY[1]
    }
    if pronoun_variants != {
        "그렇다면소승에게 기회가 오려나……",
        "그렇다면나에게 기회가 오려나……",
        "그렇다면저에게 기회가 오려나……",
        "그렇다면소인에게 기회가 오려나……",
        "그렇다면이 몸에게 기회가 오려나……",
    }:
        raise RuntimeError("segment 997 pronoun line-edge assembly drifted")
    if not all(url.startswith("https://kotobank.jp/") for url in EVIDENCE_URLS.values()):
        raise RuntimeError("segment 997 historical evidence drifted")


def main() -> int:
    prepared, translations, rows, candidate_sha256 = COMMON.build_segment_rows(
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
    COMMON.assert_dynamic_runtime_contracts(
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
        raise RuntimeError("segment 997 decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S997",
                "source_literal_count": 25,
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
