#!/usr/bin/env python3
"""Build source-redacted PK B104 segment 1317 residual decisions."""

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
    "13:510:0",
    "13:511:0",
    "13:513:0",
    "13:520:0",
    "13:523:0",
    "13:524:0",
    "13:540:0",
    "13:545:0",
    "13:547:2",
    "13:547:3",
    "13:552:1",
    "13:552:3",
    "13:555:0",
    "13:559:0",
    "13:560:0",
    "13:561:0",
    "13:562:0",
)
TRANSLATIONS = {
    "13:510:0": (
        "출진 중인 부대가 많아졌습니다.\n"
        "㍉㎝㍑㎝㌣로 여러 부대를 선택할 수 있으니\n"
        "목표를 한꺼번에 변경할 때 활용합시다."
    ),
    "13:511:0": "\"협격\"",
    "13:513:0": "\"조략\"",
    "13:520:0": (
        "영내의 군에서는 무장을 파견하지 않으면 해결하기 어려운 문제가 생기기도 합니다.\n"
        "더 빨리 해결하려면 무장을 파견합시다.\n"
        "\n"
        "【문제의 종류】\n"
        "◇영내 황폐\n"
        "◇국경 분쟁\n"
        "◇상위 취락 건설\n"
        "◇명소 관련 항목"
    ),
    "13:523:0": (
        "【명소 관련 항목】\n"
        "·명소를 장악하여 세력 전체에 혜택을 준다\n"
        "·이미 장악한 명소라면 LV가 올라 효과가 커진다\n"
        "\n"
        "◇발생 조건\n"
        "·재건(LV1) … 명소가 있는 성의 개발률이 높아지면 발생\n"
        "·발전(LV2) … 명소가 있는 국의 모든 성의 개발률이 높아지면 발생\n"
        "·번영(LV3) … 명소가 있는 지방의 모든 성을 보유하면 발생"
    ),
    "13:524:0": "\"전봉\"",
    "13:540:0": (
        "완전 제패에는 두 가지 방법이 있습니다.\n"
        "달성 방법에 따라 각각의 엔딩을 맞이합니다.\n"
        "\n"
        "◇전국 통일\n"
        " 모든 성을 자세력만으로 지배하면 달성한다\n"
        "◇종속 통일\n"
        " 전국 과반수의 성을 지배하고,\n"
        " 남은 모든 적 세력을 종속시키면 달성한다"
    ),
    "13:545:0": (
        "출진 중인 부대가 적 부대와 접촉했습니다.\n"
        "\n"
        "【교전 규칙】\n"
        "·적 부대와 접촉하면 교전이 시작된다\n"
        "·교전 중에는 부대 능력에 따라 병력이 감소한다\n"
        "·병력이 0이 되면 부대가 괴멸한다\n"
        "·부대가 괴멸할 때 부대를 이끄는 무장이 사망할 수도 있다\n"
        "·교전이 끝날 때까지 부대는 그 자리에 머문다"
    ),
    "13:547:2": "\"의 \"",
    "13:547:3": "오다 가문",
    "13:552:1": "㈹노동력",
    "13:552:3": "㈹노동력",
    "13:555:0": (
        "영내의 군을 적에게 빼앗겼습니다.\n"
        "군을 빼앗기면 다음과 같은 악영향이 발생합니다.\n"
        "부대를 출진시켜 서둘러 탈환합시다.\n"
        "\n"
        "【군을 빼앗기면】\n"
        "·취락 장악이 해제된다(공성전이 발생하지 않는 성의 경우)\n"
        "·개발 용지의 취락이 파괴된다\n"
        "·영주가 일시적으로 해임된다"
    ),
    "13:559:0": (
        "포진 변경에서는 합전 시작 시 부대 배치를 바꿀 수 있습니다.\n"
        "강력한 부대는 특수 요충지나 방비가 약한 경로의 전선에 두는 것이 좋습니다.\n"
        "◇전방 부대의 주요 역할\n"
        "·초반 적과 접촉하고 전선을 구축한다\n"
        "·퇴각로와 요충지를 공략한다\n"
        "◇후방 부대의 주요 역할\n"
        "·퇴각로와 요충지를 방어한다\n"
        "·체력이 줄어든 전방 부대와 교대한다"
    ),
    "13:560:0": "\"공성전\"",
    "13:561:0": (
        "공성전에서는 성을 두고 두 진영이 싸웁니다.\n"
        "\n"
        "수성 측은 성하에 배치된 설비를 활용해 성을 지킵니다.\n"
        "\n"
        "공성 측은 시간이 지나면 \"총사기\"가 감소합니다.\n"
        "0이 되면 공성 측의 패배이므로 설비를 파괴하거나 적 부대를 격파해\n"
        "총사기를 유지하면서 적의 \"본성\"을 파괴해야 합니다."
    ),
    "13:562:0": (
        "【공성 측의 승리 조건】\n"
        "①적의 \"본성\"을 파괴한다\n"
        "②적 부대를 모두 격파한다\n"
        "③적의 다이묘를 쓰러뜨린다\n"
        "【수성 측의 승리 조건】\n"
        "①적의 \"총사기\"를 0으로 만든다\n"
        "②적 부대를 모두 격파한다\n"
        "③적의 다이묘를 쓰러뜨린다"
    ),
}
TARGET_RECORD_IDS = (
    510, 511, 513, 520, 523, 524, 540, 545, 547, 552, 555, 559, 560,
    561, 562,
)
EXPECTED_ARITY = {
    547: 5,
    552: 5,
    **{
        record_id: 1
        for record_id in TARGET_RECORD_IDS
        if record_id not in {547, 552}
    },
}
PREFILL_COMPANION_COORDINATES = (
    "13:547:0",
    "13:547:1",
    "13:547:4",
    "13:552:0",
    "13:552:2",
    "13:552:4",
)
PREFILL_COMPANION_DONOR = {
    "13:547:0": "13:503:0",
    "13:547:1": "13:503:1",
    "13:547:4": "13:503:4",
    "13:552:0": "13:508:0",
    "13:552:2": "13:508:2",
    "13:552:4": "13:508:4",
}
SEMANTIC_BASE_CONTEXT = {
    510: ("13:468:0",),
    511: (),
    513: (),
    520: ("13:477:0",),
    523: ("13:477:0", "13:479:0"),
    524: (),
    540: ("13:496:0",),
    545: ("13:501:0", "13:316:0"),
    547: (),
    552: (),
    555: ("13:510:0",),
    559: ("13:514:0",),
    560: (),
    561: ("13:325:0", "14:65:1"),
    562: ("13:325:0", "14:65:1"),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES.update({
    511: ((13, 469),),
    513: ((13, 262), (13, 471)),
    524: ((13, 480),),
    547: ((13, 503),),
    552: ((13, 508),),
    560: ((13, 331),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1317,
    queue_start=67,
    queue_stop=134,
    slice_first="13:504:0",
    slice_last="13:562:0",
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
        (13, record_id) for record_id in range(502, 565)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("pincer attack", "협격"),
        ("covert action", "조략"),
        ("landmark", "명소"),
        ("higher settlement", "상위 취락"),
        ("relocation of fief", "전봉"),
        ("complete supremacy", "완전 제패"),
        ("national unification", "전국 통일"),
        ("vassal unification", "종속 통일"),
        ("engagement", "교전"),
        ("labor", "노동력"),
        ("formation change", "포진 변경"),
        ("disengagement point", "퇴각로"),
        ("key point", "요충지"),
        ("castle assault", "공성전"),
        ("defending side", "수성 측"),
        ("attacking side", "공성 측"),
        ("total morale", "총사기"),
        ("citadel", "본성"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record tutorial was reviewed as auxiliary evidence; six "
        "complete records reuse approved exact Base Korean assemblies, "
        "including all six same-record prefill companions, while nine "
        "PK-specific records use closely corresponding completed Base "
        "tutorials only as semantic and register context and never inherit "
        "Base runtime or VM state; landmark terminology follows the native "
        "PK data corpus, and pincer attack, covert action, fief relocation, "
        "complete supremacy, engagement, labor, formation, disengagement "
        "point, castle assault, defending and attacking sides, total morale "
        "and citadel labels remain distinct; Okehazama and Oda names, "
        "platform button strings, line counts, bullet hierarchy, note "
        "indentation, terminators, complete record arity, all fifty slice "
        "prefills, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, optional neighbor decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256": (
            "D4AE7DDA94614C143AE30701F35BBEAB4BA7BEF23696A8BA65086F8ACFC573DD"
        ),
        "expected_queue_slice_sha256": (
            "B3AF6B928692BD56A777D74D60A17300F7C71770457FCBCF02A0E51F0E55D51B"
        ),
        "expected_prefilled_coordinate_sha256": (
            "6265179E9D1102E81562E5D851E693ECD82C6AAAB5E629565A860AADF7BC5189"
        ),
        "expected_prefill_slice_context_sha256": (
            "82E68519B65117CD1C5E1CA37F155399E5B8884B25C95AACCBC70D47591A8D0B"
        ),
        "expected_target_coordinate_sha256": (
            "91237BB11D8321CD8E400515374024220CD65634AE5D4182E9571915B6B328D5"
        ),
        "expected_source_target_sha256": (
            "3721C69251312324A4D9327E43E18D2E64409497682BFE36979FBE05341152F8"
        ),
        "expected_current_target_sha256": (
            "5E2F0AE21F499CBABE9906B07A24059CDE72C5AF044024C161416EDB97DF6610"
        ),
        "expected_context_corpus_sha256": (
            "EF31A2EF18EADB612070AE3F8582EA2A24FBEBA2A93DAB4EED92AFA008D5A77A"
        ),
        "expected_gap_contract_sha256": (
            "297751AB505C5208CB0BBA3371C100978B44D0468C94FDD0A5D2A021EAB7FE9A"
        ),
        "expected_boundary_sha256": (
            "A6676F9B68BE90FCE5E71C760B7902763CFA7130A073E5158D03EC13441C2FC5"
        ),
        "expected_runtime_control_sha256": (
            "01B9C5810EED345B803D29F9B8F46E9DBA6BA237444307FD311A69AC1FA4CE18"
        ),
        "expected_base_search_sha256": (
            "1F2B28146325B8389B4F519A16B878DB7BBDF1B58A27C163EA0A681A076949FF"
        ),
        "expected_complete_assembly_sha256": (
            "C43E4DFCAF94563DEA591F640747BC38BDDBA59519F3E4FD99EB7B2B2E8904CE"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "489CB7AD4607D2B0BA90FBD40CBD486CCE4E44F01CA41121E6365ACC4015A296"
        ),
        "expected_terminology_policy_sha256": (
            "E0870BA08196458B655FC7D1E16A364E82E93F6DB727A546FC74900A047902F9"
        ),
        "expected_translation_policy_sha256": (
            "8CBF398229053D22DEA36485C25DEAFC519412655D75B380D39966F688D7AFCF"
        ),
        "expected_candidate_sha256": (
            "4F39E4CFAB340ED0FB7ABEA6CAB89E20891F8BAC488FF903DEC02C517CEA6463"
        ),
        "expected_combined_slice_candidate_sha256": (
            "7C4E27566634081EBA88F8A1829886520A3B4D40B1C19E75BE7418B95D85928F"
        ),
        "expected_combined_changed_literal_count": 65,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B104_S1317",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B104_S1317.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B104_S1316.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B104_S1318.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B104",
    "queue_row_count": 176,
    "queue_visible_count": 200,
    "queue_first": "13:445:0",
    "queue_last": "13:620:0",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Review complete records while retaining static prefill provenance."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1317 Base promoted input drifted")
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
    exact_donor = {
        511: (13, 469),
        513: (13, 471),
        524: (13, 480),
        547: (13, 503),
        552: (13, 508),
        560: (13, 331),
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (13, record_id)
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
                f"segment 1317 Base search drifted: {record_id}"
            )
        exact = record_id in exact_donor
        donor_coordinates = (
            tuple(
                f"{exact_donor[record_id][0]}:"
                f"{exact_donor[record_id][1]}:{literal_id}"
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
                    "segment 1317 Base context drifted: "
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
            coordinate = f"13:{record_id}:{literal_id}"
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
                        f"segment 1317 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1317 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1317 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1317 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 13)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            511: (13, 469),
            513: (13, 471),
            524: (13, 480),
            547: (13, 503),
            552: (13, 508),
            560: (13, 331),
        },
    )


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
