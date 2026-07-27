#!/usr/bin/env python3
"""Build source-redacted PK B106 segment 1324 residual decisions."""

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
    "14:70:2",
    "14:70:5",
    "14:71:1",
    "14:71:2",
    "14:71:5",
    "14:72:2",
    "14:73:0",
    "14:73:2",
    "14:74:1",
    "14:74:2",
    "14:74:6",
    "14:75:0",
    "14:75:3",
    "14:78:0",
    "14:78:1",
    "14:79:0",
    "14:79:1",
    "14:83:0",
    "14:84:1",
    "14:84:2",
    "14:84:3",
    "14:84:4",
    "14:84:5",
    "14:84:6",
    "14:84:7",
)
TRANSLATIONS = {
    "14:70:2": "◇본거지",
    "14:70:5": (
        "\n"
        "다이묘와 군단장의 본거지를 중심으로 지시가 닿는 성의 범위입니다.\n"
        "범위 밖의 성에는 지시가 닿지 않아 금전 수입이 크게 줄어듭니다.\n"
        "통치 범위 밖에 성이 있다면 본거지를 이전하여\n"
        "되도록 통치 범위 안에 두도록 합시다.\n"
        "그래도 범위 밖에 성이 남는다면 군단 편제를 권합니다."
    ),
    "14:71:1": (
        "\n"
        "본거지와 직할령을 변경할 수 있습니다.\n"
        "현재 성에서 멀수록 비용이 늘어납니다.\n"
        "※직담에서 소령 안도를 약속한 성은 이전할 수 없습니다.\n"
        "\n"
    ),
    "14:71:2": "◇본거지",
    "14:71:5": (
        "\n"
        "다이묘와 군단장의 본거지를 중심으로 지시가 닿는 성의 범위입니다.\n"
        "범위 밖의 성에는 지시가 닿지 않아 금전 수입이 크게 줄어듭니다.\n"
        "통치 범위 밖에 성이 있다면 본거지를 이전해 범위 안에 두도록 합시다.\n"
        "그래도 범위 밖에 성이 남는다면 군단 편제나 정책 \"전마제\" 발령을 권합니다."
    ),
    "14:72:2": "◇구획",
    "14:73:0": "◇증축",
    "14:73:2": "◇철거",
    "14:74:1": (
        "\n"
        "\"공략 목표\"를 설정하면 선정된 성의 가신들이\n"
        "공략 목표로 지정된 성을 공격하고자 군비를 갖춥니다.\n"
        "\n"
    ),
    "14:74:2": "◇군비",
    "14:74:6": "╋",
    "14:75:0": "【출진】",
    "14:75:3": (
        "\n"
        "　·행군 중에는 휴대 군량(부대가 휴대하는 식량)을 소비한다\n"
        "　　병량이 떨어지면 병력이 조금씩 감소한다\n"
        "　·적의 군에 도달하면 군을 제압할 때까지 발이 묶이며\n"
        "　　취락 \"요새\"가 있으면 영주의 무용에 따라 피해를 받는다\n"
        "　·적 부대나 성과 접촉하면 전투가 시작된다\n"
        "　·병력이 0이 되면 부대가 괴멸하며, 무장이 전사할 수도 있다"
    ),
    "14:78:0": "◇성 공격",
    "14:78:1": (
        "\n"
        "적의 성과 접촉하면 \"포위\"가 시작됩니다.\n"
        "\"강공\"으로 변경할 수도 있습니다.\n"
        "\n"
        "　·성의 내구를 0으로 만들면 성을 제압한다\n"
        "　·여러 길에서 성을 포위하면 유리해진다\n"
        "　·\"포위\"는 시간이 걸리지만 반격을 받지 않는다\n"
        "　·포위 중 피해는 부대 측의 포위와 성 측의 대포위로 결정된다\n"
        "　·\"강공\"은 성에 큰 피해를 주지만 반격을 받는다\n"
        "　·강공 중 피해는 부대 측의 공격과 성 측의 방어로 결정된다\n"
        "　·성에 \"낙석\"이나 \"투배락\"이 있으면 포위 중에도 강력한 반격을 받는다\n"
        "　·\"낙석\"과 \"투배락\"은 성내 병사가 출진 중이어도 발동할 수 있다\n"
        "　·적 부대와 교전 중에는 공성전을 할 수 없다"
    ),
    "14:79:0": "◇성 공격",
    "14:79:1": (
        "\n"
        "공성전이 발생하지 않는 적의 성과 접촉하면 \"포위\"가 시작됩니다.\n"
        "\"강공\"으로 변경할 수도 있습니다.\n"
        "\n"
        "　·성의 내구를 0으로 만들면 성을 제압한다\n"
        "　·여러 길에서 성을 포위하면 유리해진다\n"
        "　·\"포위\"는 시간이 걸리지만 반격을 받지 않는다\n"
        "　·포위 중 피해는 부대 측의 포위와 성 측의 대포위로 결정된다\n"
        "　·\"강공\"은 성에 큰 피해를 주지만 반격을 받는다\n"
        "　·강공 중 피해는 부대 측의 공격과 성 측의 방어로 결정된다\n"
        "　·성에 \"낙석\"이나 \"투배락\"이 있으면 포위 중에도 강력한 반격을 받는다\n"
        "　·\"낙석\"과 \"투배락\"은 성내 병사가 출진 중이어도 발동할 수 있다\n"
        "　·적 부대와 교전 중에는 성 공격을 할 수 없다"
    ),
    "14:83:0": "◇합전",
    "14:84:1": "\n방위 준비를 마친(",
    "14:84:2": "Σ",
    "14:84:3": (
        ") 적의 성과 접촉하면 \"공성전\"을 벌일 수 있습니다.\n"
        "방위 준비는 \"성 역할\"에서 \"방위 거점\"으로 설정한 성이나 본거지에서 이루어집니다.\n"
        "각 성이 전용 전장이 되며, 성을 포위한 공성 측 부대와\n"
        "그 성의 영지를 맡은 수성 측 부대가 전투를 벌입니다.\n"
        "\n"
    ),
    "14:84:4": "◇공성전에 참가하는 부대",
    "14:84:5": (
        "\n"
        "　·공성 측　…　성에서 일정 범위 안에 있는 부대\n"
        "　　　　　　　　가도를 봉쇄할수록 참가 가능한 부대 수가 늘어난다(최대 16개)\n"
        "　·수성 측　…　그 성에 지행지가 있는 무장 또는 대관\n"
        "\n"
    ),
    "14:84:6": "◇공성전 결과",
    "14:84:7": (
        "\n"
        "공성전의 승패가 가려지면 위풍이 발생하여\n"
        "주변 성과 군, 국인중이 동요하거나 돌아서는 등의 일이 일어납니다.\n"
        "동요한 성은 일정 기간 출진하거나 설비를 건설할 수 없습니다.\n"
        "※동요 상태인 성의 영내로 쳐들어가면 해제됩니다\n"
        "※위풍의 규모는 공성 측의 부대 수와 수성 측의 세력 규모, 내구, 병력으로 정해집니다\n"
        "※수성 측의 위풍으로는 성과 군이 돌아서지 않습니다\n"
        "\n"
        "또한 공성 측이 승리하면 방위용으로 비축한 군량을 접수하여\n"
        "휴대 군량을 보충할 수 있으므로 계속 행군하기 쉬워집니다."
    ),
}
CROSS_SEGMENT_COMPANION_COORDINATES = ("14:70:1",)
MANUAL_CROSS_SEGMENT_TRANSLATIONS = {
    "14:70:1": (
        "\n"
        "본거지와 직할령을 변경할 수 있습니다.\n"
        "현재 성에서 멀수록 비용이 늘어납니다.\n"
        "\n"
    ),
}
TARGET_RECORD_IDS = (70, 71, 72, 73, 74, 75, 78, 79, 83, 84)
EXPECTED_ARITY = {
    70: 6,
    71: 6,
    72: 6,
    73: 6,
    74: 8,
    75: 4,
    78: 2,
    79: 2,
    83: 4,
    84: 8,
}
PREFILL_COMPANION_COORDINATES = (
    "14:70:0",
    "14:70:3",
    "14:70:4",
    "14:71:0",
    "14:71:3",
    "14:71:4",
    "14:72:0",
    "14:72:1",
    "14:72:3",
    "14:72:4",
    "14:72:5",
    "14:73:1",
    "14:73:3",
    "14:73:4",
    "14:73:5",
    "14:74:0",
    "14:74:3",
    "14:74:4",
    "14:74:5",
    "14:74:7",
    "14:75:1",
    "14:75:2",
    "14:83:1",
    "14:83:2",
    "14:83:3",
    "14:84:0",
)
PREFILL_COMPANION_DONOR = {
    "14:70:0": "14:48:0",
    "14:70:3": "14:48:3",
    "14:70:4": "14:48:4",
    "14:71:0": "14:48:0",
    "14:71:3": "14:48:3",
    "14:71:4": "14:48:4",
    "14:72:0": "14:49:0",
    "14:72:1": "14:49:1",
    "14:72:3": "14:49:3",
    "14:72:4": "14:49:4",
    "14:72:5": "14:49:5",
    "14:73:1": "14:50:1",
    "14:73:3": "14:50:3",
    "14:73:4": "14:50:4",
    "14:73:5": "14:50:5",
    "14:74:0": "14:51:0",
    "14:74:3": "14:51:3",
    "14:74:4": "14:51:4",
    "14:74:5": "14:51:5",
    "14:74:7": "14:51:7",
    "14:75:1": "14:52:1",
    "14:75:2": "14:52:2",
    "14:83:1": "14:59:1",
    "14:83:2": "14:59:2",
    "14:83:3": "14:59:3",
    "14:84:0": "14:55:0",
}
SEMANTIC_BASE_CONTEXT = {
    70: tuple(f"14:48:{literal_id}" for literal_id in range(6)),
    71: tuple(f"14:48:{literal_id}" for literal_id in range(6)),
    72: (),
    73: (),
    74: tuple(f"14:51:{literal_id}" for literal_id in range(8)),
    75: ("14:52:0", "14:52:3"),
    78: ("14:55:0", "14:55:1"),
    79: ("14:55:0", "14:55:1"),
    83: (),
    84: ("14:55:0", "14:55:1", "7:939:1"),
}
EXACT_BASE_DONOR = {
    72: (14, 49),
    73: (14, 50),
    83: (14, 59),
}
EXPECTED_BASE_MATCHES = {
    record_id: (
        ((14, 49),) if record_id == 72
        else ((14, 50),) if record_id == 73
        else ((14, 59),) if record_id == 83
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1324,
    queue_start=134,
    queue_stop=198,
    slice_first="14:70:2",
    slice_last="14:85:3",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (14, record_id) for record_id in range(68, 88)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("main base", "본거지"),
        ("direct domain", "직할령"),
        ("domain assurance", "소령 안도"),
        ("direct talks", "직담"),
        ("governance range", "통치 범위"),
        ("province organization", "군단 편제"),
        ("postal system", "전마제"),
        ("attack target", "공략 목표"),
        ("mobilization", "군비"),
        ("unit provisions", "휴대 군량"),
        ("castle assault", "성 공격"),
        ("blockade", "포위"),
        ("storm", "강공"),
        ("counter-blockade", "대포위"),
        ("rock drop", "낙석"),
        ("firepot", "투배락"),
        ("field battle", "합전"),
        ("siege battle", "공성전"),
        ("attacking side", "공성 측"),
        ("defending side", "수성 측"),
        ("castle role", "성 역할"),
        ("defensive base", "방위 거점"),
        ("county faction", "국인중"),
        ("magistrate", "대관"),
    ),
    basis=(
        "pristine PK JP is authoritative and every available EN, SC and TC "
        "same-record tutorial was reviewed as auxiliary evidence; approved "
        "completed Base tutorials supply exact completed assemblies or "
        "semantic terminology only, without Base runtime or VM inheritance; "
        "all twenty-five residual literals across ten complete records were "
        "reviewed with twenty-six exact-reuse companions and one predecessor "
        "decision companion; the split record seventy assembly is explicitly "
        "identical to the preceding segment, including the approved main-base "
        "layout break; project terms for main base, domain assurance, direct "
        "talks, province organization, unit provisions, blockade, storm, "
        "counter-blockade, rock drop, firepot, field battle, siege battle, "
        "castle role, defensive base and county factions are preserved; "
        "icon fragments, full-width bullet hierarchy, outer whitespace, "
        "gaps, terminators, complete arity, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=14,
    pins={
        "expected_queue_universe_sha256":
        "45DD8230808466378440F383E693E5424552C4381E4B8880C5CC5D20467BC3A1",
        "expected_queue_slice_sha256":
        "CA0FF0C2A7C270D31B4C2F362D0FB23541160D42FAA088C44ED28CF4AAA728FA",
        "expected_prefilled_coordinate_sha256":
        "730D9E8D1A9F99A07D41ECD531C4292C8C6496ADB99D8907BE3A780B29E855BF",
        "expected_prefill_slice_context_sha256":
        "E14160FE4E6826B0877D2650B17FC88461540DAA5168F51E0FCCBF7B0B44CB4F",
        "expected_target_coordinate_sha256":
        "838492EF683BA6A038A1441F0BCEAE4D3369DDEBE78862F4DEB435EAED54DA22",
        "expected_source_target_sha256":
        "31FE1E14A2F63664C14F066CE5C3413EA8C2CB21EA24DB2215D4223C48B27347",
        "expected_current_target_sha256":
        "29E4A638A94747B5C2950539368B7BCFCCCBF85C383AC8515386D2A4391956DD",
        "expected_context_corpus_sha256":
        "8E64D9C008771F5B2CB60963BD38753D17EE6ADDAB0BDFDF17FFBD6D291F199E",
        "expected_gap_contract_sha256":
        "2212A3D4A6127A2B2370FC368897AA8FA509E93163637618428A8A39D5F60B71",
        "expected_boundary_sha256":
        "DF82600F753A39ADC0E18C24CC5B916A3319D151907A5EBB80A98FDFD59F8CC8",
        "expected_runtime_control_sha256":
        "CE32655DC46120E7800FB989527EFBC70ED93B8A6DAE92DFDCF47ED941DEB0B3",
        "expected_base_search_sha256":
        "1505F227541AE271B21A546254D39647627EA90A95BB297006AE379109044653",
        "expected_complete_assembly_sha256":
        "33B3D6D2F879648324AD134ECD25BBBBFFCE57941DC6BD0AE6019B6D50A6749B",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "459B9CE6AC968FDC67B54EF1CA2E7E708F356F1508420B99DF72F6343A497971",
        "expected_terminology_policy_sha256":
        "7D8D42E01F44EA643F4D7DAB43BCB9B3AB35CBBFB8D6B391F8BC2F37880C6E32",
        "expected_translation_policy_sha256":
        "6AADB59D0BCAE171BD625D6BF5B69B4271FB3CB44BC713465B1BEAADA4B71C03",
        "expected_candidate_sha256":
        "4019DA3D3F76CD95DB1E9139C6ABFC34FD5760E4B31723F3B3DA15344A903198",
        "expected_combined_slice_candidate_sha256":
        "7B7782624C0E1F84C00969083A50417F533C8E7D8536F1C0C889E1E36BCA6431",
        "expected_combined_changed_literal_count": 40,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B106_S1324",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1324.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1322.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1323.private.v1.jsonl",
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
    """Review complete records, including the predecessor-owned boundary."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1324 Base promoted input drifted")
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
    predecessor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1323.private.v1.jsonl"
    )
    predecessor_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(predecessor_path)
    }
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
            or raw_matches != EXPECTED_BASE_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1324 Base search drifted: {record_id}"
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
                    "segment 1324 Base context drifted: "
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
                        f"segment 1324 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in cross_set:
                predecessor = predecessor_rows.get(coordinate)
                translation = MANUAL_CROSS_SEGMENT_TRANSLATIONS[coordinate]
                if (
                    predecessor is None
                    or predecessor.get("semantic_review") != "approved"
                    or predecessor.get("runtime_review") != "pending"
                    or predecessor.get("translation") != translation
                ):
                    raise RuntimeError(
                        f"segment 1324 predecessor drifted: {coordinate}"
                    )
                assembled.append(translation)
                owners.append("preceding_segment_manual_multilingual")
                seen_cross.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1324 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1324 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1324 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    """Allow only the reviewed extra layout break at the split boundary."""
    COMMON.CORE.guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        COMMON.CORE.EXPECTED_TARGET_COORDINATE_SHA256,
    )
    COMMON.CORE.guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        COMMON.CORE.EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    COMMON.CORE.guarded_digest(
        "speaker style",
        COMMON.CORE.SPEAKER_STYLE,
        COMMON.CORE.EXPECTED_SPEAKER_STYLE_SHA256,
    )
    COMMON.CORE.guarded_digest(
        "terminology policy",
        COMMON.CORE.TERMINOLOGY_POLICY,
        COMMON.CORE.EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    changed_coordinates = tuple(
        coordinate
        for coordinate, translation in TRANSLATIONS.items()
        if translation
        != COMMON.literal_texts(
            records_by_label["current"],
            COMMON.coordinate_key(coordinate)[:2],
        )[COMMON.coordinate_key(coordinate)[2]]
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or set(COMMON.CORE.DYNAMIC_COORDINATES)
        != set(TARGET_COORDINATES)
        or COMMON.CORE.STATIC_COORDINATES
        or len(changed_coordinates)
        != CONFIG["expected_changed_literal_count"]
        or COMMON.ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
    ):
        raise RuntimeError("segment 1324 semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = COMMON.coordinate_key(coordinate)
        current_text = COMMON.literal_texts(
            records_by_label["current"], key[:2]
        )[key[2]]
        COMMON.ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        expected_line_delta = 1 if coordinate == "14:70:5" else 0
        if (
            translation.count("\n")
            != current_text.count("\n") + expected_line_delta
            or COMMON.ENGINE.protected_signature(translation)
            != COMMON.ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment 1324 shape drifted: {coordinate}"
            )


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)
    setattr(COMMON.CORE, "assert_semantics", assert_semantics)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
