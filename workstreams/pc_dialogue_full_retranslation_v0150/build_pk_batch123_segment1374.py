#!/usr/bin/env python3
"""Build source-redacted PK B123 segment 1374 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

TARGET_COORDINATES = (
    "15:1560:1",
    "15:1560:3",
    "15:1561:0",
    "15:1562:0",
    "15:1562:2",
    "15:1563:0",
    "15:1564:2",
    "15:1565:1",
    "15:1566:3",
    "15:1567:2",
    "15:1568:3",
    "15:1569:0",
    "15:1569:1",
    "15:1570:0",
    "15:1570:3",
    "15:1571:3",
    "15:1572:0",
    "15:1572:2",
    "15:1573:1",
    "15:1574:2",
    "15:1576:1",
    "15:1578:1",
    "15:1579:1",
    "15:1579:2",
    "15:1582:2",
)
TRANSLATIONS = {
    "15:1560:1": "성",
    "15:1560:3": "성은 우리 가문을 따르고 있",
    "15:1561:0": (
        "지방 통일에 필요한 성을 동맹 세력이\n"
        "제압하고 있다면, 외교 관계를\n"
        "해소한 뒤 공략해야 하"
    ),
    "15:1562:0": "기나이는 모두 우리 가문을 따르고 있",
    "15:1562:2": "성",
    "15:1563:0": (
        "천하 평정에 필요한 성을 동맹 세력이\n"
        "제압하고 있다면, 외교 관계를\n"
        "해소한 뒤 공략해야 하"
    ),
    "15:1564:2": "성",
    "15:1565:1": "성",
    "15:1566:3": "성",
    "15:1567:2": "성",
    "15:1568:3": "인가",
    "15:1569:0": (
        "우리 가문이야말로 이 나라에 둘도 없는 무가\n"
        "천하에 패권을 떨쳐\n"
        "천하 평정을 이루"
    ),
    "15:1569:1": "다",
    "15:1570:0": "이제",
    "15:1570:3": "다",
    "15:1571:3": "다",
    "15:1572:0": "우선",
    "15:1572:2": "확인",
    "15:1573:1": "은(는)\n",
    "15:1574:2": "확인",
    "15:1576:1": "확인",
    "15:1578:1": "은(는)\n",
    "15:1579:1": "\n은상의",
    "15:1579:2": "검토를",
    "15:1582:2": "이……",
}
TARGET_RECORD_IDS = (
    1560,
    1561,
    1562,
    1563,
    1564,
    1565,
    1566,
    1567,
    1568,
    1569,
    1570,
    1571,
    1572,
    1573,
    1574,
    1576,
    1578,
    1579,
    1582,
)
EXPECTED_ARITY = {
    1560: 4,
    1561: 1,
    1562: 5,
    1563: 1,
    1564: 5,
    1565: 4,
    1566: 4,
    1567: 4,
    1568: 4,
    1569: 2,
    1570: 4,
    1571: 4,
    1572: 5,
    1573: 4,
    1574: 3,
    1576: 2,
    1578: 4,
    1579: 3,
    1582: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1560:0",
    "15:1562:1",
    "15:1562:4",
    "15:1564:0",
    "15:1564:1",
    "15:1564:4",
    "15:1565:0",
    "15:1565:3",
    "15:1566:0",
    "15:1566:1",
    "15:1566:2",
    "15:1567:0",
    "15:1567:1",
    "15:1567:3",
    "15:1568:0",
    "15:1568:1",
    "15:1568:2",
    "15:1570:1",
    "15:1570:2",
    "15:1571:0",
    "15:1571:1",
    "15:1571:2",
    "15:1572:1",
    "15:1572:4",
    "15:1573:0",
    "15:1573:2",
    "15:1573:3",
    "15:1574:0",
    "15:1574:1",
    "15:1576:0",
    "15:1578:0",
    "15:1578:2",
    "15:1578:3",
    "15:1579:0",
    "15:1582:0",
    "15:1582:1",
)
PREFILL_COMPANION_DONOR = {
    "15:1560:0": "15:1530:0",
    "15:1562:1": "15:1532:1",
    "15:1562:4": "15:1532:4",
    "15:1564:0": "15:1534:0",
    "15:1564:1": "15:1534:1",
    "15:1564:4": "15:1532:4",
    "15:1565:0": "15:1535:0",
    "15:1565:3": "15:1535:3",
    "15:1566:0": "15:1536:0",
    "15:1566:1": "15:1536:1",
    "15:1566:2": "15:1536:2",
    "15:1567:0": "15:1537:0",
    "15:1567:1": "15:1537:1",
    "15:1567:3": "15:1537:3",
    "15:1568:0": "15:1538:0",
    "15:1568:1": "15:1538:1",
    "15:1568:2": "15:1538:2",
    "15:1570:1": "15:1540:1",
    "15:1570:2": "15:1540:2",
    "15:1571:0": "15:1541:0",
    "15:1571:1": "15:1541:1",
    "15:1571:2": "15:1541:2",
    "15:1572:1": "15:1542:1",
    "15:1572:4": "15:1542:4",
    "15:1573:0": "15:1543:0",
    "15:1573:2": "15:1543:2",
    "15:1573:3": "15:1543:3",
    "15:1574:0": "15:1544:0",
    "15:1574:1": "15:1544:1",
    "15:1576:0": "15:1546:0",
    "15:1578:0": "15:1548:0",
    "15:1578:2": "15:1543:2",
    "15:1578:3": "15:1543:3",
    "15:1579:0": "15:1549:0",
    "15:1582:0": "15:1552:0",
    "15:1582:1": "15:1552:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:1560:2",
    "15:1562:3",
    "15:1564:3",
    "15:1565:2",
    "15:1572:3",
)
EXACT_BASE_DONOR = {
    1564: (15, 1534),
    1565: (15, 1535),
    1566: (15, 1536),
    1567: (15, 1537),
    1568: (15, 1538),
    1570: (15, 1540),
    1571: (15, 1541),
    1572: (15, 1542),
    1573: (15, 1543),
    1574: (15, 1544),
    1576: (15, 1546),
    1578: (15, 1548),
    1579: (15, 1549),
    1582: (15, 1552),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id in EXACT_BASE_DONOR
    },
    1560: ("15:1530:0", "15:1530:1", "15:1530:3"),
    1561: ("15:1531:0",),
    1562: (
        "15:1532:0",
        "15:1532:1",
        "15:1532:2",
        "15:1532:4",
    ),
    1563: ("15:1533:0",),
    1569: ("15:1539:0", "15:1539:1"),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{
        record_id: ()
        for record_id in (1560, 1561, 1562, 1563, 1569)
    },
    1564: ((15, 1534),),
    1565: ((15, 1535),),
    1566: ((15, 1536),),
    1567: ((15, 1537),),
    1568: ((15, 1538),),
    1570: ((15, 1540),),
    1571: ((15, 1541),),
    1572: ((15, 1542),),
    1573: ((15, 1543),),
    1574: ((15, 1544),),
    1576: ((15, 1546),),
    1578: ((15, 1548),),
    1579: ((15, 1549),),
    1582: ((15, 1552),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    1560: ((568, 1090), ("023C", "0232", "0233")),
    1561: ((82,), ()),
    1562: ((1090, 568, 1090), ("0232", "0233")),
    1563: ((82,), ()),
    1564: ((1090, 568, 1090), ("0232", "0233")),
    1565: ((568, 1090), ("0232", "0233")),
    1566: ((82, 568), ("0232", "0233")),
    1567: ((1090, 568, 394), ("0232",)),
    1568: ((586, 700, 610), ("023C",)),
    1569: ((1066,), ()),
    1570: ((1286, 1162), ("025032",)),
    1571: ((550, 1162), ("023C", "025032")),
    1572: ((1174, 412, 808), ("023C", "023C")),
    1573: ((1090,), ("026432", "023C", "0232")),
    1574: ((1126, 1174, 412), ()),
    1576: ((1174, 412), ()),
    1578: ((1090,), ("026432", "023C", "0232")),
    1579: ((550, 1174), ()),
    1582: ((538, 1096), ("026432",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1374,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1560:0",
    slice_last="15:1582:2",
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
        568,
        1090,
        82,
        394,
        586,
        700,
        610,
        1066,
        1286,
        1162,
        550,
        1174,
        412,
        808,
        1126,
        538,
        1096,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1525, 1625)
    ),
    speaker_style=(
        (1560, "system_unification_progress"),
        (1561, "tutorial_regional_unification_alliance_warning"),
        (1562, "system_national_pacification_progress"),
        (1563, "tutorial_national_pacification_alliance_warning"),
        (1564, "system_kinai_conquest_progress"),
        (1565, "system_all_castles_conquest_progress"),
        (1566, "system_national_pacification_kinai_requirement"),
        (1567, "system_kinai_conquest_no_castle_progress"),
        (1568, "formal_regional_unification_proposal"),
        (1569, "emphatic_national_pacification_declaration"),
        (1570, "emphatic_national_unification_ambition"),
        (1571, "emphatic_appointment_unification_ambition"),
        (1572, "formal_regional_situation_review"),
        (1573, "formal_home_base_region_report"),
        (1574, "confident_governance_review"),
        (1576, "formal_remaining_factions_review"),
        (1578, "formal_former_base_region_report"),
        (1579, "formal_reward_review"),
        (1582, "formal_spy_interception_proposal"),
    ),
    terminology_policy=(
        ("regional unification", "지방 통일"),
        ("national pacification", "천하 평정"),
        ("Kinai", "기나이"),
        ("domination", "제패"),
        ("allied faction", "동맹 세력"),
        ("diplomatic relations", "외교 관계"),
        ("clan", "우리 가문"),
        ("castle", "성"),
        ("ruler of the realm", "천하인"),
        ("military prestige", "무위"),
        ("reward", "은상"),
        ("spy", "간자"),
        ("county", "군"),
        ("review", "확인, 검토"),
        ("subjugate", "제압, 복속"),
        ("hegemony", "패권"),
        ("dynamic object particle", "을(를)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B123 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; fourteen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by literal and operand-masked source identity, while five "
        "PK-specific unification records use adjacent completed Base records "
        "as semantic context and preserve the authoritative allied-faction "
        "and clan-submission distinctions; five source-identical hidden "
        "newline companions remain non-translatable while participating in "
        "complete-record assembly; Base runtime and VM state are never "
        "inherited; regional unification, national pacification, Kinai, "
        "domination, diplomatic relations, castles, the clan, military "
        "prestige, rewards, spies and counties retain established historical "
        "project wording and tutorial, system, formal, confident or emphatic "
        "registers; calls, inline castle, faction, count and review tokens, "
        "protected outer whitespace, line breaks, ellipses, terminators, "
        "complete record arity, all forty-two slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=6,
    pins={
        "expected_queue_universe_sha256": (
            "01F2F01C3BD54B4E74BA77C265BF140CBDBA1DF4238130C4E562422C72CE4662"
        ),
        "expected_queue_slice_sha256": (
            "B589BE99798C067AB966F20125B10C3D5213D47F61A3224FB06D46FA39606176"
        ),
        "expected_prefilled_coordinate_sha256": (
            "39417DACD18D3EBAF9BEA2FCA665D64B038F2D4142AF169DA88CABFE590EACD1"
        ),
        "expected_prefill_slice_context_sha256": (
            "C2C272442D5C9786B249CB2D04F582126630544E43475668EF10BCB272203F59"
        ),
        "expected_target_coordinate_sha256": (
            "2AE881C403D41F1B3B8C7AC79205EF720FF3983DF647FC131444F86B92390A24"
        ),
        "expected_source_target_sha256": (
            "B08F801049BE86F1A0F4C61EC3041CE7404D46342DF1E7A2F553FE68CB64C743"
        ),
        "expected_current_target_sha256": (
            "895833B67C1423B32E47195D95B01B9D5C2A1B5EB7E511E533586E022A99328E"
        ),
        "expected_context_corpus_sha256": (
            "8FB2668DFD7BA3E9C26775EB7540AF41F109D9406FA938F876F803E2392DDAC9"
        ),
        "expected_gap_contract_sha256": (
            "A133E2AD81F58F1422D9C5C6506153D949D40B413F763B15A16EAC5A0771E8A4"
        ),
        "expected_boundary_sha256": (
            "E01894673600ACF7719006F41DACF97B8A1BDB91B852E47F384AD90C5B93DE3B"
        ),
        "expected_runtime_control_sha256": (
            "6DCF3AAC5CE08ACE68CB301665905B071AC007D7B95CDBD53C599B05F0C70CB3"
        ),
        "expected_base_search_sha256": (
            "19CD0706642004F1A183183C9350ABDB009CAD3248DDA1522FAE90E150C31103"
        ),
        "expected_complete_assembly_sha256": (
            "960887FC6CA64C921D0A103F8AA4E72AE6BAED3A9615CD41E183A9570267B28C"
        ),
        "expected_call_graph_sha256": (
            "9F370C3E8C9E27A069AABF66F968593FCF85FC6E011492E76AD222676DBCD872"
        ),
        "expected_speaker_style_sha256": (
            "70D9DF56508260AD08625481A7548068158E735BFD57A66CC0170F96AB79A183"
        ),
        "expected_terminology_policy_sha256": (
            "BACAE2D17504472CD9200DF5C777929CD2904398EF18BB85A1AE81BAE7E019AD"
        ),
        "expected_translation_policy_sha256": (
            "EDD2AEDB8BD629E5A0B7DA47EFB37B76CBB932204BFB36BC4C41E63FAE4CD7FC"
        ),
        "expected_candidate_sha256": (
            "AF3BE47917EE1146F18730747184680AF9F3D6D8C69774F2AD4E2B4DA69D67D9"
        ),
        "expected_combined_slice_candidate_sha256": (
            "87BBD50990E92B35C3B964AA7356014FA5AF6CF0D86BEBB8BDCA6608B613CE5D"
        ),
        "expected_combined_changed_literal_count": 31,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B123_S1374",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1374.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1373.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1375.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B123",
    "queue_row_count": 78,
    "queue_visible_count": 199,
    "queue_first": "15:1536:0",
    "queue_last": "15:1613:1",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard exact Base assemblies and PK-specific semantic adaptations."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1374 Base promoted input drifted")
    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (15, record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(
            records_by_label["jp"], key
        )
        current_literals = COMMON.literal_texts(
            records_by_label["current"], key
        )
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
            )
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
                and COMMON.CORE.mask_call_operands(record)
                == COMMON.CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches
            != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches
            != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1374 Base search drifted: {record_id}"
            )
        exact = record_id in EXACT_BASE_DONOR
        donor_coordinates = (
            tuple(
                f"{EXACT_BASE_DONOR[record_id][0]}:"
                f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
            if exact
            else SEMANTIC_BASE_CONTEXT[record_id]
        )
        references: list[tuple[Any, ...]] = []
        donor_translations: list[str] = []
        for literal_id, donor_coordinate in enumerate(donor_coordinates):
            donor = base_rows.get(donor_coordinate)
            target_coordinate = f"15:{record_id}:{literal_id}"
            if (
                exact
                and donor is None
                and target_coordinate in hidden_set
            ):
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment 1374 hidden donor drifted: "
                        f"{target_coordinate}"
                    )
                donor_translations.append("\n")
                references.append((
                    donor_coordinate,
                    "\n",
                    "source_identical_hidden_newline",
                    "not_translatable_blank",
                    "complete_exact_assembly",
                    "runtime_vm_not_inherited",
                ))
                continue
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1374 Base context drifted: "
                    f"{donor_coordinate}"
                )
            donor_translation = str(donor["translation"])
            if exact:
                donor_translations.append(donor_translation)
            references.append((
                donor_coordinate,
                donor_translation,
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                (
                    "complete_exact_assembly"
                    if exact
                    else "semantic_only"
                ),
                "runtime_vm_not_inherited",
            ))
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append(
                    "segment_manual_exact_base_semantic_reuse"
                    if exact
                    else "segment_manual_multilingual"
                )
                seen_target.add(coordinate)
            elif coordinate in companion_set:
                prefill = prefill_rows.get(coordinate)
                if (
                    prefill is None
                    or prefill.get("semantic_review") != "approved"
                    or prefill.get("runtime_review")
                    not in {"pending", "not_required"}
                    or prefill["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or prefill["base_exact_reuse_prefill"][
                        "base_coordinate"
                    ]
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment 1374 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment 1374 hidden newline drifted: {coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1374 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != tuple(donor_translations):
            raise RuntimeError(
                f"segment 1374 exact assembly drifted: {record_id}"
            )
        base_evidence.append((
            record_id,
            COMMON.sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(source)
            ),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(references),
            (
                "complete_exact_semantic_review"
                if exact
                else "semantic_context_only"
            ),
        ))
        assembly_evidence.append((
            record_id,
            tuple(owners),
            tuple(assembled),
            tuple(donor_translations) if exact else None,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError("segment 1374 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
