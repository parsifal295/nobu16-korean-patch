#!/usr/bin/env python3
"""Build source-redacted PK B106 segment 1323 residual decisions."""

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
    "14:57:1",
    "14:57:3",
    "14:58:0",
    "14:58:1",
    "14:59:0",
    "14:59:1",
    "14:59:3",
    "14:60:0",
    "14:60:1",
    "14:60:3",
    "14:60:4",
    "14:60:5",
    "14:61:2",
    "14:61:4",
    "14:64:2",
    "14:65:2",
    "14:66:2",
    "14:67:0",
    "14:67:2",
    "14:68:2",
    "14:69:2",
    "14:69:4",
    "14:70:1",
)
TRANSLATIONS = {
    "14:57:1": (
        "\n정책 \"제도 개신\" LV1을 발령하면 각 성에 성하 방침을 설정할 수 있습니다.\n"
        "성하 방침을 설정하면 성주와 영주가 각각 성하 시설과 개발 용지를 자율적으로 건설합니다.\n"
        "\n"
    ),
    "14:57:3": (
        "\n　·설정할 수 있는 성하 방침\n"
        "　·성하 시설과 개발 용지의 건설 속도\n"
        "　·성하 시설을 증축할 수 있는 최대 LV\n"
        "\n"
        "성을 특정 용도에 특화할 수 있으므로,\n"
        "원하는 성하 방침을 선택할 수 있도록 무장의 지행지를 조정해 봅시다."
    ),
    "14:58:0": "◇설비 건설",
    "14:58:1": (
        "\n정책 \"제도 개신·이\" LV1을 발령하면 본거지와 방위 거점에 설비가 건설됩니다.\n"
        "\n"
        "설비는 공성전에서 사용되어 적의 침공을 막는 데 큰 도움이 됩니다.\n"
        "설비의 종류는 무장에 따라 다르므로 지행과 대관을 적절히 배치하면\n"
        "공성전을 유리하게 치를 수 있습니다.\n"
        "※건설 속도는 무장에 따라 다릅니다"
    ),
    "14:59:0": "[지행]",
    "14:59:1": (
        "\n본거지 이외의 군이나 성을 무장에게 내려 통치를 맡깁니다.\n"
        "군을 받은 무장은 \"영주\"로서 받은 군의 발전에 종사합니다.\n"
        "성을 받은 무장은 \"성주\"로서 받은 성의 발전에 종사합니다.\n"
        "\n"
        "본거지 이외의 군이나 성은 영주/성주가 없으면 발전하지 않으므로\n"
        "측근을 몇 명 남기되, 적극적으로 영주/성주로 임명하기를 권합니다.\n"
        "\n"
    ),
    "14:59:3": (
        "어느 무장에게도 지행지로 주어지지 않은 군에는 \"┫\"가 표시됩니다.\n"
        "특히 노란색 \"┫\"가 표시된 군은 농촌이나 시장을 장악해 나가면\n"
        "상위 취락인 \"대농촌\"이나 \"대시장\"을 건설할 수 있게 되므로\n"
        "우선하여 무장에게 내리는 것이 좋습니다."
    ),
    "14:60:0": "[지행]",
    "14:60:1": (
        "\n본거지 이외의 군이나 성을 무장에게 내려 통치를 맡깁니다.\n"
        "군을 받은 무장은 \"영주\"로서 받은 군의 발전에 종사합니다.\n"
        "성을 받은 무장은 \"성주\"로서 받은 성의 발전에 종사합니다.\n"
        "\n"
        "본거지 이외의 군이나 성은 영주/성주가 없으면 발전하지 않으므로\n"
        "측근을 몇 명 남기되, 적극적으로 영주/성주로 임명하기를 권합니다.\n"
        "\n"
    ),
    "14:60:3": (
        "어느 무장에게도 지행지로 주어지지 않은 군에는 \"┫\"가 표시됩니다.\n"
        "특히 노란색 \"┫\"가 표시된 군은 농촌이나 시장을 장악해 나가면\n"
        "상위 취락인 \"대농촌\"이나 \"대시장\"을 건설할 수 있게 되므로\n"
        "우선하여 무장에게 내리는 것이 좋습니다.\n"
        "\n"
    ),
    "14:60:4": "◇명소에 대하여\n",
    "14:60:5": (
        "명소가 있는 성이나 국의 개발률을 높이면 명소를 장악하거나 LV를 높일 수 있습니다.\n"
        "세력 내에 명소가 있다면 우선하여 무장에게 내립시다."
    ),
    "14:61:2": "◇장악",
    "14:61:4": "◇건설",
    "14:64:2": "◇조건",
    "14:65:2": "◇조건",
    "14:66:2": "◇조건",
    "14:67:0": "[수복]",
    "14:67:2": "◇조건",
    "14:68:2": "◇조건",
    "14:69:2": "◇조건",
    "14:69:4": "◇보충",
    "14:70:1": (
        "\n본거지와 직할령을 변경할 수 있습니다.\n"
        "현재 성에서 멀수록 비용이 늘어납니다.\n"
        "\n"
    ),
}
CROSS_SEGMENT_COMPANION_COORDINATES = (
    "14:70:2",
    "14:70:5",
)
MANUAL_CROSS_SEGMENT_TRANSLATIONS = {
    "14:70:2": "◇본거지",
    "14:70:5": (
        "\n다이묘와 군단장의 본거지를 중심으로 지시가 닿는 성의 범위입니다.\n"
        "범위 밖의 성에는 지시가 닿지 않아 금전 수입이 크게 줄어듭니다.\n"
        "통치 범위 밖에 성이 있다면 본거지를 이전하여\n"
        "되도록 통치 범위 안에 두도록 합시다.\n"
        "그래도 범위 밖에 성이 남는다면 군단 편제를 권합니다."
    ),
}
TARGET_RECORD_IDS = (57, 58, 59, 60, 61, 64, 65, 66, 67, 68, 69, 70)
EXPECTED_ARITY = {
    57: 4,
    58: 2,
    59: 4,
    60: 6,
    61: 6,
    64: 6,
    65: 6,
    66: 6,
    67: 6,
    68: 6,
    69: 6,
    70: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "14:57:0",
    "14:57:2",
    "14:59:2",
    "14:60:2",
    "14:61:0",
    "14:61:1",
    "14:61:3",
    "14:61:5",
    "14:64:0",
    "14:64:1",
    "14:64:3",
    "14:64:4",
    "14:64:5",
    "14:65:0",
    "14:65:1",
    "14:65:3",
    "14:65:4",
    "14:65:5",
    "14:66:0",
    "14:66:1",
    "14:66:3",
    "14:66:4",
    "14:66:5",
    "14:67:1",
    "14:67:3",
    "14:67:4",
    "14:67:5",
    "14:68:0",
    "14:68:1",
    "14:68:3",
    "14:68:4",
    "14:68:5",
    "14:69:0",
    "14:69:1",
    "14:69:3",
    "14:69:5",
    "14:70:0",
    "14:70:3",
    "14:70:4",
)
PREFILL_COMPANION_DONOR = {
    "14:57:0": "14:37:0",
    "14:57:2": "14:36:2",
    "14:59:2": "14:38:2",
    "14:60:2": "14:38:2",
    **{
        f"14:61:{literal_id}": f"14:39:{literal_id}"
        for literal_id in (0, 1, 3, 5)
    },
    **{
        f"14:64:{literal_id}": f"14:42:{literal_id}"
        for literal_id in (0, 1, 3, 4, 5)
    },
    **{
        f"14:65:{literal_id}": f"14:43:{literal_id}"
        for literal_id in (0, 1, 3, 5)
    },
    "14:65:4": "14:42:4",
    **{
        f"14:66:{literal_id}": f"14:44:{literal_id}"
        for literal_id in (0, 1, 3, 5)
    },
    "14:66:4": "14:42:4",
    **{
        f"14:67:{literal_id}": f"14:45:{literal_id}"
        for literal_id in (1, 3, 5)
    },
    "14:67:4": "14:42:4",
    **{
        f"14:68:{literal_id}": f"14:46:{literal_id}"
        for literal_id in (0, 1, 3)
    },
    "14:68:4": "14:42:4",
    "14:68:5": "14:42:5",
    **{
        f"14:69:{literal_id}": f"14:47:{literal_id}"
        for literal_id in (0, 1, 3, 5)
    },
    "14:70:0": "14:48:0",
    "14:70:3": "14:48:3",
    "14:70:4": "14:48:4",
}
SEMANTIC_BASE_CONTEXT = {
    57: ("14:37:0", "14:37:1", "14:36:2", "14:36:3"),
    58: ("13:338:0", "13:332:0"),
    59: tuple(f"14:38:{literal_id}" for literal_id in range(4)),
    60: (
        *(f"14:38:{literal_id}" for literal_id in range(4)),
        "13:477:0",
        "13:479:0",
    ),
    61: (),
    64: (),
    65: (),
    66: (),
    67: (),
    68: (),
    69: (),
    70: tuple(f"14:48:{literal_id}" for literal_id in range(6)),
}
EXACT_BASE_DONOR = {
    61: (14, 39),
    64: (14, 42),
    65: (14, 43),
    66: (14, 44),
    67: (14, 45),
    68: (14, 46),
    69: (14, 47),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (
        (EXACT_BASE_DONOR[record_id],)
        if record_id in EXACT_BASE_DONOR
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1323,
    queue_start=67,
    queue_stop=134,
    slice_first="14:57:1",
    slice_last="14:70:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (14, record_id) for record_id in range(55, 74)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_help")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("castle town plan", "성하 방침"),
        ("castle town facility", "성하 시설"),
        ("development site", "개발 용지"),
        ("system reform", "제도 개신"),
        ("system reform two", "제도 개신·이"),
        ("main base", "본거지"),
        ("defensive base", "방위 거점"),
        ("siege", "공성전"),
        ("dominion", "지행"),
        ("land holder", "영주"),
        ("castle lord", "성주"),
        ("farm", "농촌"),
        ("market", "시장"),
        ("large farm", "대농촌"),
        ("large market", "대시장"),
        ("landmark", "명소"),
        ("local faction", "국인중"),
        ("governance range", "통치 범위"),
        ("province organization", "군단 편제"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary evidence; seven "
        "complete records reuse approved exact Base Korean assemblies, "
        "including every same-record exact companion, while five PK-specific "
        "records use completed Base help entries only as semantic and "
        "register context and never inherit Base runtime or VM state; castle "
        "town plan, development site, system reform, defensive base, siege, "
        "dominion, land holder, castle lord, farm, market, large settlement, "
        "landmark, local faction, governance range and province-organization "
        "terms remain distinct; split record 70 is fully assembled with two "
        "S1324 companions and any present neighbor decision must agree "
        "exactly; token separators, leading and trailing newlines, bullets, "
        "spacing, terminators, complete record arity, all forty-four slice "
        "prefills, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, optional neighbor decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=12,
    pins={
        "expected_queue_universe_sha256": (
            "45DD8230808466378440F383E693E5424552C4381E4B8880C5CC5D20467BC3A1"
        ),
        "expected_queue_slice_sha256": (
            "8BE3C7F12ED7DF105ED853CE101CE96CDD564B06B50C5836AE515BA2D5EB6C5D"
        ),
        "expected_prefilled_coordinate_sha256": (
            "5CE4CA1D515F99E9E07B5F9DDEC5932721A5998EE7175F34E17B24910033A3A9"
        ),
        "expected_prefill_slice_context_sha256": (
            "8DD0FE909070A53CD937F646883A6B3AAB56093959FB653CF3591160680F14F2"
        ),
        "expected_target_coordinate_sha256": (
            "821718444325A6D37A4EA7481B6313B2A04EC9BB0D7D0498BD20A3C6F613CAC1"
        ),
        "expected_source_target_sha256": (
            "DEF277F30BD4EB0DD6790FE1DA91DCF1AE59A5558578B9A55F3661597F241F2C"
        ),
        "expected_current_target_sha256": (
            "C631A9606C75754EC3D0F70E5CDEE4CD0F6D9DF8773B1978A100D1B180CC6654"
        ),
        "expected_context_corpus_sha256": (
            "8E64D9C008771F5B2CB60963BD38753D17EE6ADDAB0BDFDF17FFBD6D291F199E"
        ),
        "expected_gap_contract_sha256": (
            "E8BB376675153804B0B78F079AD6CC45BF6A37A8F6A84F74A89B95B6F232A479"
        ),
        "expected_boundary_sha256": (
            "2436B36D109E2A89DCCE0FAC7B8C34B89E7300E66334B8D3C971745C8C41FC19"
        ),
        "expected_runtime_control_sha256": (
            "4390DECB765C963D6139D2C3D47654FA24EACDCAB42F9E259BB0FC14DEDCA558"
        ),
        "expected_base_search_sha256": (
            "F87D21202962FA3930EA4CA519FFA3C8FD6A98CC8DDEB1D84E3A789868128D95"
        ),
        "expected_complete_assembly_sha256": (
            "0DBFA70E548A0CE12B9CE844E5A4B5A3AFEABCBDC2CEB6DB67AD4EFA878D69C7"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "AFE6D619FE04C41409A39B8B1D0928419AEAB69F0931CD4D4490E794CE5900E6"
        ),
        "expected_terminology_policy_sha256": (
            "C7A731A540ADEA524C1457E3B501E766C63D2B6D1184E7F854769BF686F48C9B"
        ),
        "expected_translation_policy_sha256": (
            "D93EE3E01BF7028F866828395613F7357274C37A11C7D955E06BCD5FA3C7E2CE"
        ),
        "expected_candidate_sha256": (
            "AFDB751CDB3CEB3CCB1BDF53F34ADC7235CFBA7026BBB335FAEEAB6512A394AB"
        ),
        "expected_combined_slice_candidate_sha256": (
            "97B4F4EA6747670BED830C2381E02F4839C8A6C4B7EE382A5B6435E03D22AF22"
        ),
        "expected_combined_changed_literal_count": 45,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B106_S1323",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1323.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1322.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1324.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B106",
    "queue_row_count": 41,
    "queue_visible_count": 198,
    "queue_first": "14:45:0",
    "queue_last": "14:85:3",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Review complete records while retaining all companion provenance."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1323 Base promoted input drifted")
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
    neighbor_rows: dict[str, dict[str, Any]] = {}
    for path in CONFIG["optional_neighbors"]:
        if path.is_file():
            for row in COMMON.read_jsonl(path):
                neighbor_rows[str(row["coordinate"])] = row
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    cross_set = set(CROSS_SEGMENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_cross: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (14, record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(records_by_label["jp"], key)
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
            if COMMON.literal_texts(base_source, coordinate)
            == source_literals
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
            or literal_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1323 Base search drifted: {record_id}"
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
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1323 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "semantic_only",
                "runtime_vm_not_inherited",
            ))
        donor_translations = (
            tuple(
                str(base_rows[coordinate]["translation"])
                for coordinate in donor_coordinates
            )
            if exact
            else None
        )
        owners: list[str] = []
        assembled: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"14:{record_id}:{literal_id}"
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
                        f"segment 1323 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in cross_set:
                translation = MANUAL_CROSS_SEGMENT_TRANSLATIONS[coordinate]
                neighbor = neighbor_rows.get(coordinate)
                if neighbor is not None and (
                    neighbor.get("semantic_review") != "approved"
                    or neighbor.get("runtime_review") != "pending"
                    or str(neighbor.get("translation")) != translation
                ):
                    raise RuntimeError(
                        "segment 1323 neighbor companion drifted: "
                        f"{coordinate}"
                    )
                assembled.append(translation)
                owners.append("s1324_manual_companion")
                seen_cross.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1323 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1323 exact assembly drifted: {record_id}"
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
            donor_translations,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_cross != cross_set
    ):
        raise RuntimeError("segment 1323 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
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
