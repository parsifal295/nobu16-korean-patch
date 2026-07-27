#!/usr/bin/env python3
"""Build source-redacted PK B111 segment 1338 residual decisions."""

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
    "15:321:1",
    "15:321:3",
    "15:322:1",
    "15:323:0",
    "15:324:0",
    "15:326:2",
    "15:328:0",
    "15:329:0",
    "15:337:0",
    "15:353:0",
    "15:353:1",
    "15:354:0",
    "15:354:1",
    "15:356:1",
    "15:357:0",
    "15:359:0",
)
TRANSLATIONS = {
    "15:321:1": "인",
    "15:321:3": "인견",
    "15:322:1": "까 하옵니다",
    "15:323:0": "(이)라는 자가",
    "15:324:0": "등이,",
    "15:326:2": (
        "(이)라는 자들이 출분하여\n"
        "우리 가문에 사관하기를 바라며"
    ),
    "15:328:0": "성하에서",
    "15:329:0": "낭인·",
    "15:337:0": "낭인·",
    "15:353:0": "은(는)",
    "15:353:1": "(이)라 하오\n",
    "15:354:0": "은(는)",
    "15:354:1": "(이)라 하오\n",
    "15:356:1": "놈을\n",
    "15:357:0": "불초,",
    "15:359:0": "은(는)",
}
TARGET_RECORD_IDS = (
    321,
    322,
    323,
    324,
    326,
    328,
    329,
    337,
    353,
    354,
    356,
    357,
    359,
)
EXPECTED_ARITY = {
    321: 5,
    322: 2,
    323: 2,
    324: 2,
    326: 3,
    328: 2,
    329: 2,
    337: 2,
    353: 3,
    354: 3,
    356: 3,
    357: 3,
    359: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:321:0",
    "15:321:2",
    "15:321:4",
    "15:322:0",
    "15:323:1",
    "15:324:1",
    "15:326:0",
    "15:326:1",
    "15:328:1",
    "15:329:1",
    "15:337:1",
    "15:353:2",
    "15:354:2",
    "15:356:0",
    "15:356:2",
    "15:357:1",
    "15:357:2",
    "15:359:1",
    "15:359:2",
)
PREFILL_COMPANION_DONOR = {
    "15:321:0": "15:315:0",
    "15:321:2": "15:315:2",
    "15:321:4": "15:315:4",
    "15:322:0": "15:317:0",
    "15:323:1": "15:318:1",
    "15:324:1": "15:318:1",
    "15:326:0": "15:319:0",
    "15:326:1": "15:319:1",
    "15:328:1": "15:321:1",
    "15:329:1": "15:322:1",
    "15:337:1": "15:330:1",
    "15:353:2": "15:346:2",
    "15:354:2": "15:347:2",
    "15:356:0": "15:349:0",
    "15:356:2": "15:349:2",
    "15:357:1": "15:350:1",
    "15:357:2": "15:350:2",
    "15:359:1": "15:352:1",
    "15:359:2": "15:352:2",
}
EXACT_BASE_DONOR = {
    321: (15, 315),
    322: (15, 317),
    323: (15, 318),
    328: (15, 321),
    329: (15, 322),
    337: (15, 330),
    353: (15, 346),
    354: (15, 347),
    356: (15, 349),
    357: (15, 350),
    359: (15, 352),
}
SEMANTIC_BASE_CONTEXT = {
    321: (),
    322: (),
    323: (),
    324: tuple(f"15:318:{literal_id}" for literal_id in range(2)),
    326: tuple(f"15:319:{literal_id}" for literal_id in range(3)),
    328: (),
    329: (),
    337: (),
    353: (),
    354: (),
    356: (),
    357: (),
    359: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    321: (),
    322: (),
    323: ((15, 318),),
    324: (),
    326: (),
    328: ((15, 321),),
    329: ((15, 322),),
    337: ((15, 330),),
    353: ((15, 346), (15, 1399), (15, 1417)),
    354: ((15, 347), (15, 1400), (15, 1418)),
    356: ((15, 349), (15, 1402), (15, 1420)),
    357: ((15, 350), (15, 1403), (15, 1421)),
    359: ((15, 352), (15, 1405), (15, 1423)),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    321: ((15, 315), (15, 316)),
    322: ((15, 317),),
    323: ((15, 318),),
    324: (),
    326: (),
    328: ((15, 321),),
    329: ((15, 322),),
    337: ((15, 330),),
    353: ((15, 346), (15, 1399), (15, 1417)),
    354: ((15, 347), (15, 1400), (15, 1418)),
    356: ((15, 349), (15, 1402), (15, 1420)),
    357: ((15, 350), (15, 1403), (15, 1421)),
    359: ((15, 352), (15, 1405), (15, 1423)),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    321: ((8, 1174, 796), ("024833", "023C")),
    322: ((1048,), ("024833",)),
    323: ((178,), ("024833", "025032")),
    324: ((178,), ("024833", "025032")),
    326: ((178,), ("025032", "024833")),
    328: ((), ("024833",)),
    329: ((), ("024833",)),
    337: ((), ("024833",)),
    353: ((1, 8), ("024633",)),
    354: ((1, 8), ("024633",)),
    356: ((8,), ("024635",)),
    357: ((8,), ("024633",)),
    359: ((1, 8), ("024633",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1338,
    queue_start=67,
    queue_stop=134,
    slice_first="15:321:1",
    slice_last="15:360:0",
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
    source_call_roots=(1, 8, 178, 796, 1048, 1174),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(310, 371)
    ),
    speaker_style=(
        (321, "formal_recruitment_report"),
        (322, "formal_recruitment_report"),
        (323, "formal_recruitment_report"),
        (324, "formal_plural_recruitment_report"),
        (326, "formal_plural_recruitment_report"),
        (328, "retainer_recruitment_report"),
        (329, "retainer_recruitment_proposal"),
        (337, "female_recruitment_proposal"),
        (353, "male_archaic_service_pledge"),
        (354, "male_archaic_service_pledge"),
        (356, "male_humble_service_pledge"),
        (357, "male_formal_service_pledge"),
        (359, "male_forceful_service_pledge"),
    ),
    terminology_policy=(
        ("castle town", "성하"),
        ("audience", "인견"),
        ("ronin", "낭인"),
        ("clan", "우리 가문"),
        ("leave one's lord", "출분"),
        ("enter service", "사관"),
        ("employ", "등용"),
        ("warrior honor", "무사의 영예"),
        ("supremacy", "패업"),
        ("humble first person", "불초"),
        ("dynamic subject particle", "은(는)"),
        ("dynamic copula", "(이)라"),
        ("project middle dot", "·"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; eleven "
        "complete records reuse approved completed Base Korean assemblies, "
        "including duplicated Base source records with identical final Korean, "
        "while two PK plural recruitment records adapt the completed Base "
        "departure and service wording only as semantic context; Base runtime "
        "and VM state are never inherited; dynamic person, clan and speaker "
        "calls retain their source ordering, subject and object particles "
        "remain explicit, audience, ronin, departure, service, employment, "
        "warrior honor, supremacy and humble first-person terms retain the "
        "completed Base register; calls, inline name and faction tokens, "
        "leading and trailing newlines, punctuation fragments, terminators, "
        "complete record arity, all fifty-one slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=9,
    pins={
        "expected_queue_universe_sha256": (
            "B7EEC6BF26F798B3C3B00BAC72A3E07BF5A68F3F242518911158017CD99BD584"
        ),
        "expected_queue_slice_sha256": (
            "5A0FAC6F54DB106DBF19646C74025465EE122BDAAE38F87AC269311A54571EB8"
        ),
        "expected_prefilled_coordinate_sha256": (
            "468D25E5856B066DC99BBEB92EE6C4A1441B8AF050037B398CA62696BD67A62A"
        ),
        "expected_prefill_slice_context_sha256": (
            "DDA366E1DA226B4F514E8F55185B7719DAAA2152A86ABD902F216AE6020AE0CD"
        ),
        "expected_target_coordinate_sha256": (
            "ABA59FF4F7DE80461FBBB5702784CEB93752D1527E155042A9FC0F4A07300BED"
        ),
        "expected_source_target_sha256": (
            "725732E3091D99840F92C01D375B40099BF5281987F9610F12089C653AFC5D1C"
        ),
        "expected_current_target_sha256": (
            "C01030123CEE6B396198ECE8A443219CD8FCA511B6C3A5C8253E4B19AC7F0311"
        ),
        "expected_context_corpus_sha256": (
            "5E7230FB3D0D4FF3D4E8B19E8604363C4653FB44D52095DA5027BE70B00FB41D"
        ),
        "expected_gap_contract_sha256": (
            "6CB947D0FA26289E5C74FE1EE43C966B47EFC763EDAB73A7BA9747147D00C76C"
        ),
        "expected_boundary_sha256": (
            "8A43C8FFBAD4218DE82A752BA6F1023B8E255FACD3D8477F27AB51BD14B956C7"
        ),
        "expected_runtime_control_sha256": (
            "B57BFA8B85EBEFFD1E745348ECA03CC0291EF98B0CA92AB6392D8A2F12D943A7"
        ),
        "expected_base_search_sha256": (
            "752913EED4DA7AE6BC89AB7CF522C670F99C531440411FDF13482817E6DBFC1B"
        ),
        "expected_complete_assembly_sha256": (
            "D4241A37385D8D1E28454E0820BF1223E7F6B1376E825C3FC2F825772179E2F5"
        ),
        "expected_call_graph_sha256": (
            "61500042D59E98D0C3CB671D6897B2FCEE1F7F3DF66B29E4A271068DFE814F94"
        ),
        "expected_speaker_style_sha256": (
            "9424E4A010CF88C8289B9DAD9DB12CBA495EE04E235AA3AE14C9B467E1E45A5B"
        ),
        "expected_terminology_policy_sha256": (
            "638555E3E1AC546224937D74BB4914B155EE93E13BF2F7D85527425AC6355990"
        ),
        "expected_translation_policy_sha256": (
            "90ADD8B9B2C593DF0023FC65474D366CFF9077759414E19FDE079B73B63FFFFF"
        ),
        "expected_candidate_sha256": (
            "F90E7D5F184AC5C9137EF4B791A341605F024C0694859C22CDFC79CE84C9DFCA"
        ),
        "expected_combined_slice_candidate_sha256": (
            "95597512BDAD900AF1B792E3BB01BE885C15B07970F6B841F40FC3ACC0A72353"
        ),
        "expected_combined_changed_literal_count": 53,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B111_S1338",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1338.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1337.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1339.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B111",
    "queue_row_count": 113,
    "queue_visible_count": 199,
    "queue_first": "15:282:0",
    "queue_last": "15:394:1",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Review exact Base assemblies and the two PK plural extensions."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1338 Base promoted input drifted")
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
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
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
                f"segment 1338 Base search drifted: {record_id}"
            )
        exact = record_id in EXACT_BASE_DONOR
        references: list[tuple[Any, ...]] = []
        donor_coordinates = (
            tuple(
                f"{EXACT_BASE_DONOR[record_id][0]}:"
                f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
            if exact
            else SEMANTIC_BASE_CONTEXT[record_id]
        )
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1338 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "complete_exact_assembly" if exact else "semantic_only",
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
                        f"segment 1338 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1338 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1338 exact assembly drifted: {record_id}"
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
    if seen_target != target_set or seen_companion != companion_set:
        raise RuntimeError("segment 1338 assembly ownership drifted")
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
