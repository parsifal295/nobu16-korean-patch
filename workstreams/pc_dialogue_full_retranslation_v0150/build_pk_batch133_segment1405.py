#!/usr/bin/env python3
"""Build source-redacted PK B133 segment 1405 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE = (
    COMMON.BASE.base_and_assembly_evidence
)

TARGET_RECORD_IDS = tuple(range(2528, 2548))
MAIN_RECORD_IDS = tuple(range(2529, 2548))
TARGET_COORDINATES = (
    "15:2528:1",
    "15:2528:2",
    "15:2529:0",
    "15:2529:1",
    "15:2529:2",
    "15:2529:3",
    "15:2530:0",
    "15:2530:1",
    "15:2531:0",
    "15:2531:1",
    "15:2531:2",
    "15:2532:0",
    "15:2532:1",
    "15:2532:2",
    "15:2533:0",
    "15:2533:1",
    "15:2533:2",
    "15:2533:3",
    "15:2534:1",
    "15:2534:2",
    "15:2535:0",
    "15:2535:1",
    "15:2536:0",
    "15:2536:1",
    "15:2537:0",
    "15:2537:1",
    "15:2537:2",
    "15:2537:3",
    "15:2538:0",
    "15:2538:1",
    "15:2538:2",
    "15:2538:3",
    "15:2538:4",
    "15:2539:0",
    "15:2539:1",
    "15:2539:2",
    "15:2540:0",
    "15:2540:1",
    "15:2540:2",
    "15:2540:3",
    "15:2541:0",
    "15:2541:1",
    "15:2541:2",
    "15:2542:0",
    "15:2542:1",
    "15:2542:2",
    "15:2542:3",
    "15:2543:0",
    "15:2543:1",
    "15:2543:2",
    "15:2544:0",
    "15:2544:1",
    "15:2544:2",
    "15:2544:3",
    "15:2545:0",
    "15:2545:1",
    "15:2546:0",
    "15:2546:1",
    "15:2546:2",
    "15:2547:0",
    "15:2547:1",
    "15:2547:2",
)
MAIN_TARGET_COORDINATES = TARGET_COORDINATES[2:]
TRANSLATIONS = {
    "15:2528:1": "에 의해,",
    "15:2528:2": "의 병력이 감소",
    "15:2529:0": "의",
    "15:2529:1": "에 의해,",
    "15:2529:2": "을(를) 비롯한",
    "15:2529:3": "개 성의 병력이 감소",
    "15:2530:0": "에서 벌인",
    "15:2530:1": "에 실패",
    "15:2531:0": "에 의한",
    "15:2531:1": "에 대한",
    "15:2531:2": "을(를) 저지",
    "15:2532:0": "을(를) 비롯한",
    "15:2532:1": "개 성의",
    "15:2532:2": "에 실패",
    "15:2533:0": "에 의한",
    "15:2533:1": "을(를) 비롯한",
    "15:2533:2": "개 성에 대한",
    "15:2533:3": "을(를) 저지",
    "15:2534:1": "→",
    "15:2534:2": "으로(로)",
    "15:2535:0": "에 거짓 보고를 퍼뜨리겠습니다",
    "15:2535:1": (
        "\n우군의 이반을 의심하게 만들면\n"
        "출병할 겨를도 없어질 것입니다"
    ),
    "15:2536:0": "에 거짓 보고를 퍼뜨리겠습니다",
    "15:2536:1": (
        "\n우군의 이반을 의심하게 만들면\n"
        "출병할 겨를도 없어질 것입니다"
    ),
    "15:2537:0": "의 위보계로",
    "15:2537:1": "이(가)\n출진할 수 없게",
    "15:2537:2": "되었습니다",
    "15:2537:3": "!",
    "15:2538:0": "의 위보계로",
    "15:2538:1": "을(를) 비롯한",
    "15:2538:2": "개 성이\n출진할 수 없게",
    "15:2538:3": "되었습니다",
    "15:2538:4": "!",
    "15:2539:0": "은(는) 성공했습니다",
    "15:2539:1": "!\n",
    "15:2539:2": (
        "은(는) 크게 동요하여,\n"
        "한동안 출진할 수 없을 것입니다"
    ),
    "15:2540:0": "은(는) 성공했습니다",
    "15:2540:1": "!\n",
    "15:2540:2": "을(를) 비롯한",
    "15:2540:3": (
        "개 성은 크게 동요하여,\n"
        "한동안 출진할 수 없을 것입니다"
    ),
    "15:2541:0": "이(가)",
    "15:2541:1": "의",
    "15:2541:2": "에 성공",
    "15:2542:0": "이(가)",
    "15:2542:1": "을(를) 비롯한",
    "15:2542:2": "개 성의",
    "15:2542:3": "에 성공",
    "15:2543:0": "의",
    "15:2543:1": "에 의해,",
    "15:2543:2": "이(가) 동요",
    "15:2544:0": "의",
    "15:2544:1": "에 의해,",
    "15:2544:2": "을(를) 비롯한",
    "15:2544:3": "개 성이 동요",
    "15:2545:0": "에서 벌인",
    "15:2545:1": "에 실패",
    "15:2546:0": "에 의한",
    "15:2546:1": "에 대한",
    "15:2546:2": "을(를) 저지",
    "15:2547:0": "을(를) 비롯한",
    "15:2547:1": "개 성의",
    "15:2547:2": "에 실패",
}
EXPECTED_ARITY = {
    2528: 3,
    2529: 4,
    2530: 2,
    2531: 3,
    2532: 3,
    2533: 4,
    2534: 3,
    2535: 2,
    2536: 2,
    2537: 4,
    2538: 5,
    2539: 3,
    2540: 4,
    2541: 3,
    2542: 4,
    2543: 3,
    2544: 4,
    2545: 2,
    2546: 3,
    2547: 3,
}
PREFILL_COMPANION_COORDINATES = ("15:2534:0",)
PREFILL_COMPANION_DONOR = {"15:2534:0": "15:716:0"}
NEIGHBOR_COMPANION_TRANSLATIONS = {"15:2528:0": "의"}
EXACT_BASE_DONOR = {
    2530: (15, 1359),
    2532: (15, 1449),
    2534: (15, 716),
    2541: (15, 1357),
    2542: (15, 1446),
    2545: (15, 1359),
    2547: (15, 1449),
}
SEMANTIC_BASE_CONTEXT = {
    2528: ("6:4113:0", "6:4113:1", "6:4113:2"),
    2529: ("15:1451:0", "15:1451:1", "15:1451:2", "15:1451:3"),
    2530: (),
    2531: ("15:1454:0", "15:1454:1", "15:1454:2"),
    2532: (),
    2533: (
        "15:1449:0", "15:1449:1", "15:1449:2",
        "15:1454:0", "15:1454:1", "15:1454:2",
    ),
    2534: (),
    2535: ("9:2193:0", "15:2413:3"),
    2536: ("9:2193:0", "15:2413:3"),
    2537: ("9:2193:0",),
    2538: ("9:2193:0", "15:1449:0", "15:1449:1", "15:1449:2"),
    2539: ("9:2193:0", "9:1859:0"),
    2540: (
        "9:2193:0", "9:1859:0",
        "15:1449:0", "15:1449:1", "15:1449:2",
    ),
    2541: (),
    2542: (),
    2543: ("15:1450:0", "15:1450:1", "15:1450:2", "9:1859:0"),
    2544: (
        "15:1451:0", "15:1451:1", "15:1451:2", "15:1451:3",
        "9:1859:0",
    ),
    2545: (),
    2546: ("15:1454:0", "15:1454:1", "15:1454:2"),
    2547: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    2528: (),
    2529: (),
    2530: ((15, 1359), (15, 1448)),
    2531: (),
    2532: ((15, 1449),),
    2533: (),
    2534: ((15, 716), (15, 979), (15, 1453)),
    2535: (),
    2536: (),
    2537: (),
    2538: (),
    2539: (),
    2540: (),
    2541: ((15, 806), (15, 1357), (15, 1445)),
    2542: ((15, 1446),),
    2543: (),
    2544: (),
    2545: ((15, 1359), (15, 1448)),
    2546: (),
    2547: ((15, 1449),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    2534: (
        (15, 716), (15, 979), (15, 1337), (15, 1338), (15, 1453),
    ),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2528: ((), ("025032", "023C", "026432")),
    2529: ((), ("025032", "023C", "026432", "0232")),
    2530: ((), ("026432", "023C")),
    2531: ((), ("025032", "026432", "023C")),
    2532: ((), ("026432", "0232", "023C")),
    2533: ((), ("025032", "026432", "0232", "023C")),
    2534: ((), ("026432", "0232", "0233")),
    2535: ((442, 610, 730), ("026432",)),
    2536: ((442, 610, 730), ("025132",)),
    2537: ((760, 628), ("025032", "026432")),
    2538: ((760, 628), ("025032", "026432", "0232")),
    2539: ((538, 760, 610), ("023C", "026432")),
    2540: ((538, 760, 610), ("023C", "026432", "0232")),
    2541: ((), ("024633", "026432", "023C")),
    2542: ((), ("024633", "026432", "0232", "023C")),
    2543: ((), ("025032", "023C", "026432")),
    2544: ((), ("025032", "023C", "026432", "0232")),
    2545: ((), ("026432", "023C")),
    2546: ((), ("025032", "026432", "023C")),
    2547: ((), ("026432", "0232", "023C")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1405,
    queue_start=134,
    queue_stop=197,
    slice_first="15:2528:1",
    slice_last="15:2547:2",
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
    source_call_roots=(442, 538, 610, 628, 730, 760),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2475, 2585)
    ),
    speaker_style=(
        (2528, "concise_system_troop_reduction"),
        (2529, "concise_system_multi_troop_reduction"),
        (2530, "concise_system_scheme_failure"),
        (2531, "concise_system_scheme_prevention"),
        (2532, "concise_system_multi_scheme_failure"),
        (2533, "concise_system_multi_scheme_prevention"),
        (2534, "concise_system_troop_count_change"),
        (2535, "formal_false_report_proposal"),
        (2536, "formal_false_report_proposal"),
        (2537, "formal_misinformation_success_report"),
        (2538, "formal_multi_misinformation_success_report"),
        (2539, "formal_misinformation_completion_report"),
        (2540, "formal_multi_misinformation_completion_report"),
        (2541, "concise_system_scheme_success"),
        (2542, "concise_system_multi_scheme_success"),
        (2543, "concise_system_agitation"),
        (2544, "concise_system_multi_agitation"),
        (2545, "concise_system_scheme_failure"),
        (2546, "concise_system_scheme_prevention"),
        (2547, "concise_system_multi_scheme_failure"),
    ),
    terminology_policy=(
        ("misinformation plan", "위보계"),
        ("false report", "거짓 보고"),
        ("defection", "이반"),
        ("march", "출병"),
        ("sortie", "출진"),
        ("agitation", "동요"),
        ("prevent", "저지"),
        ("dynamic particles", "이(가), 은(는), 을(를), 으로(로)"),
        ("multiple castles", "을(를) 비롯한 수치 개 성"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B133 queue coordinates one hundred thirty-four "
        "through one hundred ninety-six and the approved Base prefill; "
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was manually reviewed as auxiliary "
        "context; seven source-identical system records reuse selected "
        "approved completed Base Korean assemblies, while PK-specific "
        "misinformation, troop-reduction, agitation and prevention records "
        "use completed Base rows only as semantic and glossary context and "
        "never inherit Base runtime or VM state; the left-boundary "
        "troop-reduction record is completed with the manually reviewed "
        "fragment owned by optional segment 1404 and any landed neighbor "
        "decision must match that assembly; misinformation plan, false "
        "report, defection, march, sortie, agitation and prevention retain "
        "established historical project wording; formal proposals and "
        "reports remain distinct from concise system notifications; calls, "
        "inline officer, castle, force, action and count tokens, protected "
        "outer whitespace, line breaks, dynamic particles, punctuation, "
        "terminators, complete record arity, the one slice prefill, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=33,
    pins={
        "expected_queue_universe_sha256": "A1FCF27A1B837763A4D3B023E5EB2F988DC4BD5C61350EC2AAAA89A92ECA6396",
        "expected_queue_slice_sha256": "99709A120A04EF2B7868BAE6B18DC9F6B765E3CBFC4596E93F9975A65618E333",
        "expected_prefilled_coordinate_sha256": "83DB2549C8BA450174ABA5FCC311B26B79774F174253076BCB6B072786999290",
        "expected_prefill_slice_context_sha256": "972E98D0925B86304BE55145DBF04569D863E0796FF3D73C8C16B74EECB66D64",
        "expected_target_coordinate_sha256": "6D4B749E2B801C9253EAB584D98B87031D69ED39FCBD45EC1054CCA35C984737",
        "expected_source_target_sha256": "3FE9586A5AFAF2FC5A32A42B9D464591C5A13B49E8A8BEDE62A8977070F647AD",
        "expected_current_target_sha256": "03582785814ACFBA9C288C342666B21B78526AD97EDA4527B1483B227914A5FE",
        "expected_context_corpus_sha256": "074BFBC4DF1748AB72681F9DF929F87C9CD07F07E8C8BC98B45338ED41867311",
        "expected_gap_contract_sha256": "AAFAFD93F7BE9BD3D299E30C314A9A0CF5E3F665FEC00369106A9C19B48E1404",
        "expected_boundary_sha256": "38E29CFEFDCC712E331CD931EFF5EE7567F66C6FBF549FC037541357A92E26F9",
        "expected_runtime_control_sha256": "610EF8E5B7381D30DF11229E13461516BDACC1BA31F7EBAF202C6C7CA2924F06",
        "expected_base_search_sha256": "284380B22A38E47965ACD485B5BF13353A9F4116E65A7C6184B870030A9EB433",
        "expected_complete_assembly_sha256": "59E4BED701AEB6CD4E29FB2E9744E47828EBDCD56C7F19A937159E4FAA2408AB",
        "expected_call_graph_sha256": "8C0ABDCAA3816C92D9E8B1014E33FC9C210B06D104CA0968C851ACA4264170CC",
        "expected_speaker_style_sha256": "4AC455B309E038561AB997675D9DC7959E8DE48A37132EDE88989A2E8A70B60F",
        "expected_terminology_policy_sha256": "45D8D7BA58EB5C5F30B6E97AFDEAA18208C6690EC9DFBD4F99AEE0ABD461FD7F",
        "expected_translation_policy_sha256": "8064A69A6C17B0F855EB9EEB3FCD4524AE8BDE53AE1DAE23D568518D4E87812A",
        "expected_candidate_sha256": "B73ECD42ED9FD4B297D1E9E9C31954ECA92C96E475321542C6D0D028ECD248B6",
        "expected_combined_slice_candidate_sha256": "B73ECD42ED9FD4B297D1E9E9C31954ECA92C96E475321542C6D0D028ECD248B6",
        "expected_combined_changed_literal_count": 33,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B133_S1405",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1405.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1403.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1404.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B133",
    "queue_row_count": 73,
    "queue_visible_count": 197,
    "queue_first": "15:2475:0",
    "queue_last": "15:2547:2",
})


def base_and_assembly_evidence_with_boundary(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard the main records plus the split left-boundary record."""
    original_globals = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved_record_ids = original_globals["TARGET_RECORD_IDS"]
    saved_coordinates = original_globals["TARGET_COORDINATES"]
    original_globals["TARGET_RECORD_IDS"] = MAIN_RECORD_IDS
    original_globals["TARGET_COORDINATES"] = MAIN_TARGET_COORDINATES
    try:
        base_evidence, assembly_evidence = (
            _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(
                prepared,
                records_by_label,
            )
        )
    finally:
        original_globals["TARGET_RECORD_IDS"] = saved_record_ids
        original_globals["TARGET_COORDINATES"] = saved_coordinates

    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    neighbor_rows = {
        str(row["coordinate"]): row
        for path in CONFIG["optional_neighbors"]
        if path.is_file()
        for row in COMMON.read_jsonl(path)
    }
    key = (15, 2528)
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
        if COMMON.literal_texts(base_source, coordinate) == source_literals
    )
    masked_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if (
            COMMON.literal_texts(base_source, coordinate) == source_literals
            and COMMON.CORE.mask_call_operands(record)
            == COMMON.CORE.mask_call_operands(source)
        )
    )
    if (
        len(source_literals) != EXPECTED_ARITY[2528]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[2528]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[2528]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[2528]
    ):
        raise RuntimeError("segment 1405 Base search drifted: 2528")

    references: list[tuple[Any, ...]] = []
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[2528]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1405 Base context drifted: "
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

    neighbor_coordinate, expected = next(
        iter(NEIGHBOR_COMPANION_TRANSLATIONS.items())
    )
    neighbor = neighbor_rows.get(neighbor_coordinate)
    if (
        neighbor is not None
        and (
            neighbor.get("translation") != expected
            or neighbor.get("semantic_review") != "approved"
            or neighbor.get("runtime_review") != "pending"
        )
    ):
        raise RuntimeError(
            "segment 1405 neighbor companion drifted: "
            f"{neighbor_coordinate}"
        )
    assembled = (
        expected,
        TRANSLATIONS["15:2528:1"],
        TRANSLATIONS["15:2528:2"],
    )
    if assembled != ("의", "에 의해,", "의 병력이 감소"):
        raise RuntimeError("segment 1405 boundary assembly drifted")
    base_tail = ((
        2528,
        COMMON.sha256_bytes(source.data),
        source_literals,
        current_literals,
        tuple(value.hex().upper() for value in COMMON.gap_bytes(source)),
        raw_matches,
        literal_matches,
        masked_matches,
        tuple(references),
        "semantic_context_only",
    ),)
    assembly_tail = ((
        2528,
        (
            "optional_previous_segment_manual_companion",
            "segment_manual_multilingual",
            "segment_manual_multilingual",
        ),
        assembled,
        None,
        COMMON.CORE.runtime_controls(source),
        COMMON.CORE.runtime_controls(current),
        "base_semantics_only",
        "base_runtime_vm_not_inherited",
    ),)
    return (
        tuple(base_evidence) + base_tail,
        tuple(assembly_evidence) + assembly_tail,
    )


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_boundary
    )
    COMMON.CORE.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_boundary
    )


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
