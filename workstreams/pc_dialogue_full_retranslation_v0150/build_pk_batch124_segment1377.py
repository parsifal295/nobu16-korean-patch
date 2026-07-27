#!/usr/bin/env python3
"""Build source-redacted PK B124 segment 1377 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1658:2",
    "15:1659:1",
    "15:1660:0",
    "15:1661:1",
    "15:1661:2",
    "15:1662:1",
    "15:1662:3",
    "15:1663:1",
    "15:1666:0",
    "15:1667:0",
    "15:1668:0",
    "15:1669:0",
    "15:1670:1",
    "15:1670:2",
    "15:1673:1",
    "15:1675:2",
    "15:1676:0",
    "15:1677:2",
    "15:1679:1",
    "15:1684:0",
)
TRANSLATIONS = {
    "15:1658:2": "대관",
    "15:1659:1": "대관",
    "15:1660:0": "대관",
    "15:1661:1": "\n새로이",
    "15:1661:2": "군단",
    "15:1662:1": "군단",
    "15:1662:3": "검토해 주시옵소서……",
    "15:1663:1": "군단",
    "15:1666:0": '성하 시설 "',
    "15:1667:0": '정책 "',
    "15:1668:0": '정책 "',
    "15:1669:0": '정책 "',
    "15:1670:1": '\n가신단에 "',
    "15:1670:2": '"을(를) 발령해 보는 것은 어떻겠습니까?',
    "15:1673:1": '"을(를) 발령해 보시는 것은 어떻겠습니까?',
    "15:1675:2": "까닭에",
    "15:1676:0": "본거지인",
    "15:1677:2": "인가",
    "15:1679:1": "에게……",
    "15:1684:0": "주군 가문인",
}
TARGET_RECORD_IDS = (
    1658,
    1659,
    1660,
    1661,
    1662,
    1663,
    1666,
    1667,
    1668,
    1669,
    1670,
    1673,
    1675,
    1676,
    1677,
    1679,
    1684,
)
EXPECTED_ARITY = {
    1658: 4,
    1659: 3,
    1660: 3,
    1661: 4,
    1662: 4,
    1663: 3,
    1666: 2,
    1667: 2,
    1668: 2,
    1669: 2,
    1670: 3,
    1673: 2,
    1675: 3,
    1676: 2,
    1677: 3,
    1679: 2,
    1684: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1658:0",
    "15:1658:1",
    "15:1658:3",
    "15:1659:0",
    "15:1659:2",
    "15:1660:1",
    "15:1660:2",
    "15:1661:0",
    "15:1661:3",
    "15:1662:0",
    "15:1662:2",
    "15:1663:0",
    "15:1663:2",
    "15:1666:1",
    "15:1667:1",
    "15:1668:1",
    "15:1669:1",
    "15:1670:0",
    "15:1673:0",
    "15:1675:0",
    "15:1675:1",
    "15:1676:1",
    "15:1677:0",
    "15:1677:1",
    "15:1679:0",
    "15:1684:1",
    "15:1684:2",
)
PREFILL_COMPANION_DONOR = {
    "15:1658:0": "15:1628:0",
    "15:1658:1": "15:1628:1",
    "15:1658:3": "15:1628:3",
    "15:1659:0": "15:1629:0",
    "15:1659:2": "15:1629:2",
    "15:1660:1": "15:1630:1",
    "15:1660:2": "15:1630:2",
    "15:1661:0": "15:1631:0",
    "15:1661:3": "15:1631:3",
    "15:1662:0": "15:1632:0",
    "15:1662:2": "15:1632:2",
    "15:1663:0": "15:1633:0",
    "15:1663:2": "15:1633:2",
    "15:1666:1": "15:1636:1",
    "15:1667:1": "15:1637:1",
    "15:1668:1": "15:1638:1",
    "15:1669:1": "15:1639:1",
    "15:1670:0": "15:1640:0",
    "15:1673:0": "15:1643:0",
    "15:1675:0": "15:1645:0",
    "15:1675:1": "15:1645:1",
    "15:1676:1": "15:1646:1",
    "15:1677:0": "15:1647:0",
    "15:1677:1": "15:1647:1",
    "15:1679:0": "15:1649:0",
    "15:1684:1": "15:1654:1",
    "15:1684:2": "15:1654:2",
}
EXACT_BASE_DONOR = {
    1658: (15, 1628),
    1659: (15, 1629),
    1660: (15, 1630),
    1661: (15, 1631),
    1662: (15, 1632),
    1663: (15, 1633),
    1666: (15, 1636),
    1667: (15, 1637),
    1668: (15, 1638),
    1669: (15, 1639),
    1670: (15, 1640),
    1673: (15, 1643),
    1675: (15, 1645),
    1676: (15, 1646),
    1677: (15, 1647),
    1679: (15, 1649),
    1684: (15, 1654),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    1658: (),
    1659: (),
    1660: (),
    1661: ((15, 1631),),
    1662: (),
    1663: (),
    1666: (),
    1667: ((15, 1637),),
    1668: (),
    1669: (),
    1670: (),
    1673: ((15, 1643),),
    1675: (),
    1676: (),
    1677: (),
    1679: ((15, 1649),),
    1684: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1658: ((562,), ()),
    1659: ((1126,), ()),
    1660: ((634, 1066), ()),
    1661: ((226,), ()),
    1662: ((1174,), ()),
    1663: ((1066,), ()),
    1666: ((700, 610), ("023C",)),
    1667: ((), ("023C",)),
    1668: ((1066,), ("023C",)),
    1669: ((700, 610), ("023C",)),
    1670: ((1066,), ("023C",)),
    1673: ((), ("023C",)),
    1675: ((1114, 724, 628), ("02473F",)),
    1676: ((568,), ("02473F",)),
    1677: ((82, 700, 610), ()),
    1679: ((1,), ()),
    1684: ((1066,), ("025032",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1377,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1658:0",
    slice_last="15:1686:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        562,
        1126,
        634,
        1066,
        226,
        1174,
        700,
        610,
        1114,
        724,
        628,
        568,
        82,
        1,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1620, 1720)
    ),
    speaker_style=(
        (1658, "formal_governor_assignment_proposal"),
        (1659, "formal_home_county_governor_proposal"),
        (1660, "formal_vacant_governor_report"),
        (1661, "formal_new_corps_proposal"),
        (1662, "formal_corps_establishment_request"),
        (1663, "formal_corps_governance_proposal"),
        (1666, "concise_facility_construction_proposal"),
        (1667, "formal_policy_necessity_advice"),
        (1668, "concise_policy_research_proposal"),
        (1669, "concise_policy_issue_proposal"),
        (1670, "formal_retainer_corps_policy_proposal"),
        (1673, "formal_merit_opportunity_policy_proposal"),
        (1675, "formal_distant_main_base_assessment"),
        (1676, "formal_main_base_relocation_proposal"),
        (1677, "formal_castle_lord_assignment_proposal"),
        (1679, "formal_chamberlain_risk_assignment_request"),
        (1684, "formal_lord_clan_courtesy_visit_proposal"),
    ),
    terminology_policy=(
        ("substitute governor", "대관"),
        ("county", "군"),
        ("army corps", "군단"),
        ("castle-town facility", "성하 시설"),
        ("policy", "정책"),
        ("retainer corps", "가신단"),
        ("main base", "본거지"),
        ("castle lord", "성주"),
        ("chamberlain", "성대"),
        ("lord clan", "주군 가문"),
        ("courtesy visit", "문안"),
        ("merit", "공"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B124 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all seventeen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by literal and operand-masked source identity with "
        "explicit exact donors; Base runtime and VM state are never "
        "inherited; substitute governors, counties, army corps, castle-town "
        "facilities, policies, the retainer corps, the main base, castle "
        "lords, chamberlains, the lord clan, courtesy visits and merit "
        "retain established historical project wording and formal advisory "
        "registers; calls, speaker, county, person, policy and value tokens, "
        "protected outer whitespace, line breaks, ellipses, terminators, "
        "complete record arity, all forty-seven slice prefills, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256": (
            "63E6B1C672AAC22BB0D388E2D42C4798C3438D1E7596F9AC5206BAC0B65D92D6"
        ),
        "expected_queue_slice_sha256": (
            "C29BDCF7A2892F7800199395561A88FA187D0D7E203666B6C6A331CAC28A1989"
        ),
        "expected_prefilled_coordinate_sha256": (
            "A30696028C025139AF81182E16D18C551CCFA6FA27A19B9EDB2124C42FD85E4F"
        ),
        "expected_prefill_slice_context_sha256": (
            "51DE3A5E06FBA2B37B0BD4382D5A8A65B8EFE83D7932C454DC7823B17281883A"
        ),
        "expected_target_coordinate_sha256": (
            "18063032DF051C569326026D83B0DAC97CB3226D6162BEC4EF6CA75B3EDE2207"
        ),
        "expected_source_target_sha256": (
            "4C69E26992E30CB75A96604C71935957501778D1C647FC89EF10F3754953E2BA"
        ),
        "expected_current_target_sha256": (
            "941FAF4DBF548E270C1082030D0F012A7D60074F78CAFF9A81778A567342B08E"
        ),
        "expected_context_corpus_sha256": (
            "33B7FDBFBD37767D8A0BBE73026893FECDF65D1AC3D40DB9FF560AC8BB98D667"
        ),
        "expected_gap_contract_sha256": (
            "F3ECA109A1E1C55A269034DF6123AB4063142BB55CC9E91C4F10A037D3B85684"
        ),
        "expected_boundary_sha256": (
            "0380901595EC1C70DB1E86E2E1C27F70C70426F90214D449BEB9E3CE6CEAAE5C"
        ),
        "expected_runtime_control_sha256": (
            "0EA112D6DCFED78985D8207BD37861DFCCE793B84A1B1F346A044F60E0BF1CEB"
        ),
        "expected_base_search_sha256": (
            "9CE8456EB62491F021D2940F789CDEFD72D4905AF5F89B18A9568BEBF110B24B"
        ),
        "expected_complete_assembly_sha256": (
            "1918ED662A9FD3D3801622139A2D740A1691729FBAFEE2E6B8491D44A50227C5"
        ),
        "expected_call_graph_sha256": (
            "C0BAB483064321E27DEF24FF5EA3EDF73A21ACFEEABE319EBE2F027CB3D38EF6"
        ),
        "expected_speaker_style_sha256": (
            "D9E91E0103A67979449DC86B6FBFED70929884F4A703C18F77EDED3D8683A10D"
        ),
        "expected_terminology_policy_sha256": (
            "60ACB39C0940708FF23B693A6B5B1C1EB811F339C53799E2A197B3992DCA9F3B"
        ),
        "expected_translation_policy_sha256": (
            "03139BCB50D7EB4A0388E1B059254B6B4876AB097499B00EA14A45DABB308EBE"
        ),
        "expected_candidate_sha256": (
            "D1A30D3E25674928C56938B54DA805FE97C49E02E0F02A3DA3981CA03F18A44A"
        ),
        "expected_combined_slice_candidate_sha256": (
            "A93ECEFF2E4D217CC15E1DD3352C13E1CE76D3C138436028B128B2FFC02F99E9"
        ),
        "expected_combined_changed_literal_count": 53,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B124_S1377",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1377.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1376.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1378.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B124",
    "queue_row_count": 101,
    "queue_visible_count": 200,
    "queue_first": "15:1614:0",
    "queue_last": "15:1714:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
