#!/usr/bin/env python3
"""Build source-redacted PK B123 segment 1373 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1537:0",
    "15:1537:1",
    "15:1537:3",
    "15:1540:0",
    "15:1540:3",
    "15:1540:5",
    "15:1542:0",
    "15:1542:1",
    "15:1545:0",
    "15:1545:2",
    "15:1546:0",
    "15:1546:1",
    "15:1546:2",
    "15:1546:3",
    "15:1546:4",
    "15:1546:5",
    "15:1547:0",
    "15:1547:1",
    "15:1547:2",
    "15:1548:0",
    "15:1548:1",
    "15:1548:2",
    "15:1549:0",
    "15:1549:1",
    "15:1549:2",
    "15:1549:3",
    "15:1550:0",
    "15:1550:1",
    "15:1551:0",
    "15:1551:2",
    "15:1552:0",
    "15:1552:1",
    "15:1553:0",
    "15:1553:1",
    "15:1554:0",
    "15:1554:1",
    "15:1554:2",
    "15:1555:0",
    "15:1555:1",
    "15:1555:2",
    "15:1555:3",
    "15:1556:0",
    "15:1556:1",
    "15:1556:2",
    "15:1557:0",
    "15:1557:1",
    "15:1557:2",
    "15:1558:0",
    "15:1558:1",
    "15:1559:0",
    "15:1559:1",
    "15:1559:2",
    "15:1559:3",
)
TRANSLATIONS = {
    "15:1537:0": "성하를 샅샅이 뒤진 결과\n",
    "15:1537:1": "이(가) 우리 가문에 사관해도 좋다고 하옵니다",
    "15:1537:3": "인가?",
    "15:1540:0": "……",
    "15:1540:3": "의",
    "15:1540:5": "만",
    "15:1542:0": "이(가)",
    "15:1542:1": "을(를) 등용",
    "15:1545:0": "을(를) 공략할 계책이 있사옵니다",
    "15:1545:2": (
        "로 적병을 유인하면\n"
        "방비가 허술해진 성을 공략할 수 있사옵니다"
    ),
    "15:1546:0": "적병을",
    "15:1546:1": "로 유인했습니다",
    "15:1546:2": "!\n이제",
    "15:1546:3": "의 다른 성은 방비가 허술할 터……\n지금",
    "15:1546:4": "출진",
    "15:1546:5": "!",
    "15:1547:0": "그럼 잠시 더 적병을 유인하겠습니다",
    "15:1547:1": "\n준비가 갖춰지는 대로",
    "15:1547:2": "출진하십시오!",
    "15:1548:0": "아무래도 이 양동책이\n",
    "15:1548:1": "에게 간파당한 모양……\n",
    "15:1548:2": "은(는) 철수시키겠습니다",
    "15:1549:0": "이(가) 양동임을 눈치챘",
    "15:1549:1": "군요\n조금이라도 적의 발을 묶으려면\n",
    "15:1549:2": "을(를) 공격하게 할 생각",
    "15:1549:3": "인가?",
    "15:1550:0": "그럼",
    "15:1550:1": "은(는) 철수시키겠습니다",
    "15:1551:0": "에 다른 세력이 쳐들어와\n양동의 의미도 없어졌습니다",
    "15:1551:2": "은(는) 철수시키겠습니다",
    "15:1552:0": "양동을 맡은",
    "15:1552:1": "의\n휴대 병량이 바닥나 가므로\n철수시키겠습니다",
    "15:1553:0": "양동을 맡았던",
    "15:1553:1": "이(가)\n철수할 수밖에 없게 되었습니다",
    "15:1554:0": "이(가)",
    "15:1554:1": "의 소유가\n아니게 되었으므로 이 성의 양동을 맡았던\n",
    "15:1554:2": "은(는) 철수시키겠습니다",
    "15:1555:0": "의 양동책에 걸려\n",
    "15:1555:1": "개 부대가 출진했습니다",
    "15:1555:2": "\n한동안 명령이 닿지 않을 것",
    "15:1555:3": "……",
    "15:1556:0": "적의 양동에 걸렸던",
    "15:1556:1": "개 부대가\n이제야 냉정을 되찾은 듯합니다",
    "15:1556:2": "\n지금이라면 명령도 닿을 것",
    "15:1557:0": (
        "의 움직임이 어딘가 부자연스럽습니다……\n"
        "이는 아마 양동일 것입니다"
    ),
    "15:1557:1": "\n이 \u300c",
    "15:1557:2": "\u300d은 쉽게 속지 않습니다",
    "15:1558:0": "적의 장단에 맞춰 줄 필요는 없습니다",
    "15:1558:1": "\n요격 부대를 철수시키겠습니다",
    "15:1559:0": "우리에게 찾아온 낭인은",
    "15:1559:1": "명\n그들을 우리 가문에 받아들일지\n부디",
    "15:1559:2": "의 눈으로",
    "15:1559:3": "판단해",
}
TARGET_RECORD_IDS = (
    1537,
    1540,
    1542,
    1545,
    1546,
    1547,
    1548,
    1549,
    1550,
    1551,
    1552,
    1553,
    1554,
    1555,
    1556,
    1557,
    1558,
    1559,
)
EXPECTED_ARITY = {
    1537: 4,
    1540: 6,
    1542: 2,
    1545: 3,
    1546: 6,
    1547: 3,
    1548: 3,
    1549: 4,
    1550: 2,
    1551: 3,
    1552: 2,
    1553: 2,
    1554: 3,
    1555: 4,
    1556: 3,
    1557: 3,
    1558: 2,
    1559: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1540:1",
    "15:1540:4",
)
PREFILL_COMPANION_DONOR = {
    "15:1540:1": "15:1525:1",
    "15:1540:4": "15:1525:4",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:1537:2",
    "15:1540:2",
    "15:1545:1",
    "15:1551:1",
)
EXACT_BASE_DONOR = {
    1542: (15, 1527),
}
SEMANTIC_BASE_CONTEXT = {
    1537: ("15:1522:0", "15:1522:1", "15:1522:2"),
    1540: (
        "15:1525:0",
        "15:1525:1",
        "15:1525:3",
        "15:1525:4",
        "15:1525:5",
    ),
    1542: (),
    1545: ("7:1471:0",),
    1546: ("7:1471:0", "2:283:0"),
    1547: ("2:283:0",),
    1548: ("9:953:0", "6:2495:0"),
    1549: ("9:953:0", "7:1471:0"),
    1550: ("6:2495:0",),
    1551: ("6:2495:0",),
    1552: ("7:2416:0", "6:2495:0"),
    1553: ("6:2495:0",),
    1554: ("6:2495:0",),
    1555: ("9:3400:0",),
    1556: ("9:3400:0",),
    1557: ("9:953:0",),
    1558: ("9:3400:0", "6:2495:0"),
    1559: ("6:2331:0", "15:1396:2"),
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    1542: ((15, 373), (15, 1411), (15, 1429), (15, 1527)),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1540: ((15, 1525),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1537: ((37, 568, 700, 424), ()),
    1540: ((574, 538, 514, 29, 226), ("026432",)),
    1542: ((), ("024633", "024733")),
    1545: ((376, 610), ("025032", "026432")),
    1546: ((538, 508, 1174, 412), ("026432", "025032")),
    1547: ((310, 1174), ()),
    1548: ((1096,), ("024833", "026E32")),
    1549: ((538, 1066), ("026E32", "026432")),
    1550: ((1096,), ("026E32",)),
    1551: ((628, 1096), ("025032", "026E32")),
    1552: ((568, 1096), ("026E32014338020000",)),
    1553: ((568, 634), ("026E32014338020000",)),
    1554: ((1096,), ("026432", "025032", "026E32")),
    1555: ((634, 286), ("025032", "023D")),
    1556: ((568, 610), ("023D",)),
    1557: ((610, 730, 1114, 508), ("026E32", "024633")),
    1558: ((754, 1096), ()),
    1559: ((8, 1174, 412), ("0232",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1373,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1536:0",
    slice_last="15:1559:3",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(
        HIDDEN_CURRENT_COMPANION_COORDINATES
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        37,
        568,
        700,
        424,
        574,
        538,
        514,
        29,
        226,
        376,
        610,
        508,
        1174,
        412,
        310,
        1096,
        1066,
        628,
        634,
        286,
        730,
        1114,
        754,
        8,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1525, 1572)
    ),
    speaker_style=(
        (1537, "formal_officer_search_recruitment_result"),
        (1540, "formal_extraction_intelligence_proposal"),
        (1542, "system_officer_employment_result"),
        (1545, "formal_feint_strategy_proposal"),
        (1546, "formal_feint_success_sortie_prompt"),
        (1547, "formal_feint_continuation_sortie_prompt"),
        (1548, "formal_feint_detected_retreat_report"),
        (1549, "strategic_feint_detected_counterproposal"),
        (1550, "formal_retreat_order"),
        (1551, "formal_feint_invalidated_retreat_report"),
        (1552, "formal_provisions_depleted_retreat_report"),
        (1553, "formal_forced_retreat_report"),
        (1554, "formal_target_ownership_retreat_report"),
        (1555, "system_enemy_feint_uncontrolled_units"),
        (1556, "system_units_regain_control"),
        (1557, "confident_officer_detects_feint"),
        (1558, "formal_disengagement_retreat_report"),
        (1559, "formal_ronin_intake_decision_request"),
    ),
    terminology_policy=(
        ("castle town", "성하"),
        ("enter service", "사관"),
        ("our clan", "우리 가문"),
        ("employ", "등용"),
        ("extraction negotiation", "빼내기 교섭"),
        ("feint", "양동"),
        ("mobile provisions", "휴대 병량"),
        ("sortie", "출진"),
        ("interception unit", "요격 부대"),
        ("ronin", "낭인"),
        ("dynamic subject particle", "이(가), 은(는)"),
        ("dynamic object particle", "을(를)"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B123 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; one complete "
        "record reuses an approved completed Base Korean assembly selected "
        "by raw, literal and operand-masked source identity; a second "
        "source-matched record reuses every visible completed Base fragment "
        "and its source-identical hidden newline, while sixteen PK-only or "
        "structurally divergent records use reviewed Base wording "
        "for officer searches, siege proposals, sorties, detection, retreat, "
        "provisions and ronin intake as semantic context only; Base runtime "
        "and VM state are never inherited; castle towns, service, our clan, "
        "employment, extraction negotiation, feints, mobile provisions, "
        "sorties, interception units and ronin retain established historical "
        "project wording and formal, strategic, confident or system "
        "registers; calls, inline officer, castle, faction, unit, count and "
        "speaker tokens, four source-identical hidden newlines, protected "
        "outer whitespace, line breaks, ellipses, terminators, complete "
        "record arity, all fourteen slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=32,
    pins={
        "expected_queue_universe_sha256": (
            "01F2F01C3BD54B4E74BA77C265BF140CBDBA1DF4238130C4E562422C72CE4662"
        ),
        "expected_queue_slice_sha256": (
            "D3F06C6D14C0136AD7DD682C8759FA177D77BF59739171C9FB63EAC8FB51AA29"
        ),
        "expected_prefilled_coordinate_sha256": (
            "6D7339767A902852D5567562BAC51EAA68668E6FD7A98E338C968B08C1E95995"
        ),
        "expected_prefill_slice_context_sha256": (
            "6D20D7D49518B681F331819738D792021AD8EF426BDD3B319A32657D97FBFECD"
        ),
        "expected_target_coordinate_sha256": (
            "B670F8FCBEF759234B1ACCC6C7EFA78E1EF9C7E0DBA9698C1BFF4B422DB1E663"
        ),
        "expected_source_target_sha256": (
            "603AA71ED5ED39663E3B0EE4D9EEF6D5A863AD24959E248D21EED97AC3629B8E"
        ),
        "expected_current_target_sha256": (
            "CA9918DE0C8D5AC903293E0D4EF73139680EEDB815AA424E1312B4C84CB8CFB7"
        ),
        "expected_context_corpus_sha256": (
            "8FB2668DFD7BA3E9C26775EB7540AF41F109D9406FA938F876F803E2392DDAC9"
        ),
        "expected_gap_contract_sha256": (
            "58E8CAC32E2C2F03065F91F09CAA94EBADDF1ABFB005D4DE6D9CBA87550A6E0B"
        ),
        "expected_boundary_sha256": (
            "6BF23FB68106B155A2DA2BEA33A5C88E969618741E9403730EB817E1C06AF56F"
        ),
        "expected_runtime_control_sha256": (
            "3E3609AD53782622E7066DFC60C46173AF20DEE2EF63C34884616F71D2B719DB"
        ),
        "expected_base_search_sha256": (
            "3F42735AB34CAFC800D96BB4AF42A881B7273377AB3AFBA2520003CC3F7ED933"
        ),
        "expected_complete_assembly_sha256": (
            "853A8543784C37B757955DADC4EB1F4758A8FD278EAB79363191B26FE2123212"
        ),
        "expected_call_graph_sha256": (
            "0FA33238F34C2DCC1392366448342EBCDC7389D0DD15B6262D48098095D151A3"
        ),
        "expected_speaker_style_sha256": (
            "217A372D4E7F28FFCE2D4A233398276FF76FA18FE6CAB7EB590ED3081E48672D"
        ),
        "expected_terminology_policy_sha256": (
            "D6AE9C58AA232F2C73B6094CFF65037176AD40844FE7C1BECCC0CBA47E51E7A5"
        ),
        "expected_translation_policy_sha256": (
            "7266C6DD57CB1F04F95ADAAAF2DEC45DDEF8CB9158AE340650FC7E02BE20D98B"
        ),
        "expected_candidate_sha256": (
            "8A4FD4EA28C3E5343EDED6EA084E4DAE4F1F2B60932AEC33C357209A84E5EC7F"
        ),
        "expected_combined_slice_candidate_sha256": (
            "1D2D9E34EDB6B07ACCCED645E9CC57F1FA4C5A18A4753D8D934B0C83CC91C4E5"
        ),
        "expected_combined_changed_literal_count": 43,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B123_S1373",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1373.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1374.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1375.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B123",
    "queue_row_count": 78,
    "queue_visible_count": 199,
    "queue_first": "15:1536:0",
    "queue_last": "15:1613:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
