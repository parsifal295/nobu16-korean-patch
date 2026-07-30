#!/usr/bin/env python3
"""Build source-redacted PK B120 segment 1365 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

CROSS_TRANSLATIONS = {
    "15:1386:4": "의 인망",
}
CROSS_DONOR_LABEL = {
    "15:1386:4": "manual-neighbor:pk_msggame_B120_S1366",
}

TARGET_RECORD_IDS = (
    1366,
    1367,
    1368,
    1369,
    1370,
    1371,
    1372,
    1373,
    1374,
    1375,
    1376,
    1377,
    1379,
    1380,
    1381,
    1385,
    1386,
)
TARGET_COORDINATES = (
    "15:1366:0",
    "15:1367:0",
    "15:1367:1",
    "15:1367:2",
    "15:1368:0",
    "15:1368:2",
    "15:1369:0",
    "15:1369:1",
    "15:1370:0",
    "15:1370:1",
    "15:1371:0",
    "15:1371:1",
    "15:1372:0",
    "15:1372:1",
    "15:1372:2",
    "15:1373:0",
    "15:1373:1",
    "15:1374:0",
    "15:1374:1",
    "15:1374:2",
    "15:1375:0",
    "15:1375:1",
    "15:1375:2",
    "15:1376:0",
    "15:1376:1",
    "15:1376:2",
    "15:1377:0",
    "15:1377:1",
    "15:1379:2",
    "15:1380:0",
    "15:1380:1",
    "15:1380:2",
    "15:1380:3",
    "15:1380:4",
    "15:1381:3",
    "15:1385:0",
    "15:1385:4",
    "15:1386:0",
)
TRANSLATIONS = {
    "15:1366:0": "·",
    "15:1367:0": "이(가)",
    "15:1367:1": "의",
    "15:1367:2": "에 성공",
    "15:1368:0": "에서 벌인",
    "15:1368:2": "이(가) 부상",
    "15:1369:0": "에서 벌인",
    "15:1369:1": "에 실패",
    "15:1370:0": "이(가)",
    "15:1370:1": "의",
    "15:1371:0": "의 성주",
    "15:1371:1": "이(가) 부상",
    "15:1372:0": "을(를) 비롯한",
    "15:1372:1": "명에게 벌인",
    "15:1372:2": "에 성공",
    "15:1373:0": "을(를) 비롯한",
    "15:1373:1": "명이 부상",
    "15:1374:0": "을(를) 비롯한",
    "15:1374:1": "명에게 벌인",
    "15:1374:2": "에 실패",
    "15:1375:0": "을(를) 비롯한",
    "15:1375:1": "명 대상의",
    "15:1375:2": "을(를) 저지",
    "15:1376:0": "에서",
    "15:1376:1": "이(가) 벌인",
    "15:1376:2": "을(를) 저지",
    "15:1377:0": "성주·",
    "15:1377:1": "님께서\n",
    "15:1379:2": "이(가) 벌인",
    "15:1380:0": "성주·",
    "15:1380:1": "님을 비롯한\n",
    "15:1380:2": "명이",
    "15:1380:3": "의 간자에게\n",
    "15:1380:4": "을(를) 받아 부상했습니다!",
    "15:1381:3": "……!",
    "15:1385:0": "에서",
    "15:1385:4": "의 인망",
    "15:1386:0": "에서",
}
EXPECTED_ARITY = {
    1366: 2,
    1367: 3,
    1368: 3,
    1369: 2,
    1370: 3,
    1371: 2,
    1372: 3,
    1373: 2,
    1374: 3,
    1375: 3,
    1376: 3,
    1377: 4,
    1379: 4,
    1380: 5,
    1381: 4,
    1385: 5,
    1386: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1366:1",
    "15:1368:1",
    "15:1370:2",
    "15:1377:2",
    "15:1377:3",
    "15:1379:0",
    "15:1379:3",
    "15:1381:0",
    "15:1381:1",
    "15:1381:2",
    "15:1385:1",
    "15:1385:2",
    "15:1385:3",
    "15:1386:1",
    "15:1386:2",
    "15:1386:3",
    *tuple(CROSS_TRANSLATIONS),
)
PREFILL_COMPANION_DONOR = {
    "15:1366:1": "15:1356:1",
    "15:1368:1": "15:810:1",
    "15:1370:2": "15:1360:2",
    "15:1377:2": "15:1363:2",
    "15:1377:3": "15:1363:3",
    "15:1379:0": "15:973:0",
    "15:1379:3": "15:973:3",
    "15:1381:0": "15:1366:0",
    "15:1381:1": "15:1366:1",
    "15:1381:2": "15:1366:2",
    "15:1385:1": "15:1370:1",
    "15:1385:2": "15:1370:2",
    "15:1385:3": "15:1370:3",
    "15:1386:1": "15:1370:1",
    "15:1386:2": "15:1370:2",
    "15:1386:3": "15:1370:3",
    **CROSS_DONOR_LABEL,
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:1379:1",)
EXACT_BASE_DONOR = {
    1366: (15, 1356),
    1367: (15, 1357),
    1368: (15, 1358),
    1369: (15, 1359),
    1370: (15, 1360),
    1371: (15, 1361),
    1372: (15, 1480),
    1374: (15, 1476),
    1376: (15, 1362),
    1377: (15, 1363),
    1381: (15, 1366),
    1385: (15, 1370),
    1386: (15, 1370),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in (1373, 1375, 1379, 1380)
    },
    1373: (
        "15:1477:1",
        "2:621:2",
        "15:1361:1",
    ),
    1375: (
        "15:1477:1",
        "15:1477:2",
        "15:1477:3",
    ),
    1379: (
        "15:973:0",
        "15:973:2",
        "15:973:3",
    ),
    1380: (
        "15:1363:0",
        "2:621:1",
        "2:621:2",
        "15:1363:2",
        "15:1363:3",
    ),
}
OPERATION_SUCCESS_MATCHES = (
    (15, 806),
    (15, 1357),
    (15, 1445),
)
OPERATION_FAILURE_INJURY_MATCHES = (
    (15, 810),
    (15, 1358),
    (15, 1447),
)
OPERATION_PREVENTED_MATCHES = (
    (15, 811),
    (15, 980),
    (15, 1286),
    (15, 1362),
    (15, 1454),
)
COUNTERINTELLIGENCE_LITERAL_MATCHES = (
    (15, 907),
    (15, 973),
    (15, 1276),
    (15, 1365),
    (15, 1444),
    (15, 1485),
)
COUNTERINTELLIGENCE_MASKED_MATCHES = (
    (15, 973),
    (15, 1276),
    (15, 1365),
    (15, 1444),
    (15, 1485),
)
COUNTY_DEVELOPMENT_MATCHES = tuple(
    (15, record_id)
    for record_id in range(1370, 1394)
)
EXPECTED_BASE_RAW_MATCHES = {
    1366: ((15, 1356),),
    1367: OPERATION_SUCCESS_MATCHES,
    1368: OPERATION_FAILURE_INJURY_MATCHES,
    1369: ((15, 1359), (15, 1448)),
    1370: ((15, 1360),),
    1371: ((15, 1361),),
    1372: ((15, 1480),),
    1373: (),
    1374: ((15, 1476),),
    1375: (),
    1376: OPERATION_PREVENTED_MATCHES,
    1377: ((15, 1363),),
    1379: (),
    1380: (),
    1381: (),
    1385: (),
    1386: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1379: COUNTERINTELLIGENCE_LITERAL_MATCHES,
    1381: ((15, 1366),),
    1385: COUNTY_DEVELOPMENT_MATCHES,
    1386: COUNTY_DEVELOPMENT_MATCHES,
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    1379: COUNTERINTELLIGENCE_MASKED_MATCHES,
}
EXPECTED_CONTROLS_BY_RECORD = {
    1366: ((), ("024633",)),
    1367: ((), ("024633", "026432", "023C")),
    1368: ((), ("026432", "023C", "024633")),
    1369: ((), ("026432", "023C")),
    1370: ((), ("026432", "025032", "023C")),
    1371: ((), ("026432", "024833")),
    1372: ((), ("024833", "0232", "023C")),
    1373: ((), ("024833", "0232")),
    1374: ((), ("024833", "0232", "023C")),
    1375: ((), ("024833", "0232", "023C")),
    1376: ((), ("026432", "025032", "023C")),
    1377: ((), ("026432", "024833", "025032", "023C")),
    1379: ((538, 592), ("026432", "025032", "023C")),
    1380: (
        (),
        ("026432", "024833", "0232", "025032", "023C"),
    ),
    1381: ((1042,), ("024833", "02483E")),
    1385: ((538, 628, 1, 610), ("029632", "02BE32")),
    1386: ((538, 628, 1, 610), ("029632", "02BE32")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1365,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1360:0",
    slice_last="15:1386:3",
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
    source_call_roots=(1, 538, 592, 610, 628, 1042),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(1350, 1400)
    ),
    speaker_style=(
        (1366, "system_recovery_summary"),
        (1367, "system_operation_success"),
        (1368, "system_operation_failure_injury"),
        (1369, "system_operation_failure"),
        (1370, "system_operation_damage"),
        (1371, "system_castle_lord_injury"),
        (1372, "system_multi_officer_operation_success"),
        (1373, "system_multi_officer_injury"),
        (1374, "system_multi_officer_operation_failure"),
        (1375, "system_multi_officer_operation_prevented"),
        (1376, "system_operation_prevented"),
        (1377, "formal_castle_lord_spy_injury_report"),
        (1379, "informal_counterintelligence_report"),
        (1380, "formal_multi_officer_spy_injury_report"),
        (1381, "defiant_injury_reflection"),
        (1385, "confident_county_development_report"),
        (1386, "confident_county_development_report"),
    ),
    terminology_policy=(
        ("operation success", "성공"),
        ("operation failure", "실패"),
        ("injury", "부상"),
        ("spy", "간자"),
        ("castle lord", "성주"),
        ("operation prevention", "저지"),
        ("county development", "개척"),
        ("local popularity", "인망"),
        ("people", "백성"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic grouped person", "을(를) 비롯한"),
        ("project ellipsis", "……"),
        ("project exclamation mark", "!"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B120 queue ordinals 67 through 133 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; thirteen complete records reuse "
        "approved completed Base Korean assemblies selected by raw, literal "
        "and operand-masked source identity; multi-officer injury, "
        "multi-officer operation prevention and multi-officer spy injury "
        "records are contextually adapted from approved completed Base group, "
        "injury, spy and prevention assemblies, while the "
        "counterintelligence record preserves its source-identical hidden "
        "newline through visible Base semantic references; Base runtime and "
        "VM state are never inherited; operation outcomes, injury, spy, "
        "castle lord, prevention, county development, local popularity, "
        "people, dynamic particles, grouped-person wording, ellipsis and "
        "each speaker register retain established project and historical "
        "terminology; direct calls, inline person, castle, faction, count, "
        "operation, county and development tokens, protected outer "
        "whitespace, newlines, gaps, literal arity, terminators, all sixteen "
        "Base-prefilled same-record companions, the hidden newline and the "
        "reciprocal S1366 closing fragment, all twenty-nine slice prefills, "
        "complete assemblies, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=21,
    pins={
        "expected_queue_universe_sha256": (
            "F31FED1CD112AA0ADB2BFBEEC7F459040B9E5892A5E59BE751060D0B8D50E138"
        ),
        "expected_queue_slice_sha256": (
            "1919D9D51F945E2AF87BA18FF153E3FFC047FF8DF9E76D90BB7EA23F116C8088"
        ),
        "expected_prefilled_coordinate_sha256": (
            "5FA64127E3CE643378E9CE0BAEEBBB15747A9610EF2BD5AE5E8790F8FBFC78BD"
        ),
        "expected_prefill_slice_context_sha256": (
            "562ED35EFCFC74FA8C9B59EBB3F211D32A4450196636B346FBE0523188F17F96"
        ),
        "expected_target_coordinate_sha256": (
            "5756ABC1E067338C74ECBFB35AB4018392931CAE8F3712F979D5378824D5AF4B"
        ),
        "expected_source_target_sha256": (
            "9C4E20FA19763D9053D75A4AF10F1487B7D733E7E35A0719C17F014C9086767A"
        ),
        "expected_current_target_sha256": (
            "5F7AC1265AE65FF5F6EB453F6FA86EF178FAE33BC165BBF57EF95398D6A887C2"
        ),
        "expected_context_corpus_sha256": (
            "BC631B3C918EB592932A4ACEA0AFB6AA32A42B3FD7E4BDA644E3B6AA6F607FA1"
        ),
        "expected_gap_contract_sha256": (
            "1FE5EB68980A77E0569C12BEE4B5594EB50E0358E651E7505A980DBC32BFAAA2"
        ),
        "expected_boundary_sha256": (
            "E752CC0B615086D1FB85EA95E2E17137E521D9DFB2069C4F0555617D12632FD5"
        ),
        "expected_runtime_control_sha256": (
            "965AA7C8108AD47E3A175B310A1712E9B1C2D745E81D6435C4326927092E1754"
        ),
        "expected_base_search_sha256": (
            "D47601FB8949B0B026CB032874F0E8F48D3A217CBAA7D3CCAB92D4EDDFE470DC"
        ),
        "expected_complete_assembly_sha256": (
            "59EB1AA7317D3FEA36C5E25876904972F32EE366B3C184AD3E1E6BB7E781BC9B"
        ),
        "expected_call_graph_sha256": (
            "80B9DE59284F4CB6224AD90A05CDCC5F8DA5B0BADF951C60EB19D25E72C131D9"
        ),
        "expected_speaker_style_sha256": (
            "60810FF6798630FBB74D522A5A8ABFE3905BE21691033B0D7B49AE61ADE1F277"
        ),
        "expected_terminology_policy_sha256": (
            "84BC3BA5AEE3FB362609C68DB1FE692958B04E2EEC0994F7CCD672C8B2AF2E2F"
        ),
        "expected_translation_policy_sha256": (
            "B92FC63357700026BD059E7C56D9F9AC24EA81C58A3406F8241CB1ACE9F113B9"
        ),
        "expected_candidate_sha256": (
            "3AFFADEF084C018AA0AABE086ABA40DC691F3F03E1D7F6D42D04ED7C1E92D1E0"
        ),
        "expected_combined_slice_candidate_sha256": (
            "8F13CA82D8EC3293010303715208EF948B47F25AD1A18CA63899D8ECC22FD606"
        ),
        "expected_combined_changed_literal_count": 46,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B120_S1365",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1365.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1364.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1366.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B120",
    "queue_row_count": 72,
    "queue_visible_count": 200,
    "queue_first": "15:1326:0",
    "queue_last": "15:1399:4",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard Base evidence, hidden newline and the split S1366 record."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1365 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1366.private.v1.jsonl"
    )
    if neighbor_path.is_file():
        neighbor_rows = {
            str(row["coordinate"]): row
            for row in COMMON.read_jsonl(neighbor_path)
        }
        for coordinate, translation in CROSS_TRANSLATIONS.items():
            neighbor = neighbor_rows.get(coordinate)
            if (
                neighbor is None
                or neighbor.get("resource") != "pk_msggame"
                or neighbor.get("semantic_review") != "approved"
                or neighbor.get("runtime_review") != "pending"
                or str(neighbor.get("translation")) != translation
            ):
                raise RuntimeError(
                    "segment 1365 reciprocal S1366 fragment drifted"
                )
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
                f"segment 1365 Base search drifted: {record_id}"
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
                    "segment 1365 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                (
                    "complete_exact_assembly"
                    if exact
                    else "semantic_only"
                ),
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
            elif coordinate in CROSS_TRANSLATIONS:
                assembled.append(CROSS_TRANSLATIONS[coordinate])
                owners.append(
                    "neighbor_segment_manual_runtime_pending"
                )
                seen_companion.add(coordinate)
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
                        f"segment 1365 companion drifted: {coordinate}"
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
                        "segment 1365 hidden newline drifted: "
                        f"{coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1365 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1365 exact assembly drifted: {record_id}"
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
        or seen_hidden != hidden_set
    ):
        raise RuntimeError("segment 1365 assembly ownership drifted")
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
