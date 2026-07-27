#!/usr/bin/env python3
"""Build source-redacted PK B105 segment 1320 residual decisions."""

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
    "14:13:3",
    "14:14:3",
    "14:16:0",
    "14:17:0",
    "14:17:2",
    "14:18:0",
    "14:18:1",
    "14:20:0",
    "14:20:1",
    "14:20:2",
    "14:20:3",
    "14:22:1",
    "14:23:0",
    "14:23:5",
    "14:24:0",
    "14:24:1",
    "14:24:5",
    "14:28:3",
    "14:29:0",
)
TRANSLATIONS = {
    "14:13:3": (
        "\n　·가신의 건의\n"
        " ·내린 명령의 진행 상황(군 개발, 정책 발령 등)\n"
        " ·영내 문제\n"
        " ·군단 상황"
    ),
    "14:14:3": (
        "\n　·가신의 건의\n"
        " ·내린 명령의 진행 상황(군 개발, 정책 발령 등)\n"
        " ·영내 문제\n"
        " ·직담으로 맺은 약정\n"
        " ·군단 상황"
    ),
    "14:16:0": "[로그]",
    "14:17:0": "[국인중]",
    "14:17:2": "┥",
    "14:18:0": "[부대]",
    "14:18:1": (
        "\n출진 중인 부대입니다.\n"
        "자세력은 청색, 적 세력은 적색, 동맹 세력은 녹색으로 표시됩니다."
    ),
    "14:20:0": "[명소]",
    "14:20:1": (
        "\n일부 군에는 \"명소\"라는 특별한 시설이 있습니다.\n"
        "모두 높은 효과를 지니며 세력의 발전을 돕습니다.\n"
        "명소는 해당 명소가 있는 성을 지배하는 세력에 속하며,\n"
        "LV를 높이거나 다른 세력에서 빼앗은 명소를 장악하려면\n"
        "영내 문제를 해결해야 합니다.\n"
        "\n"
    ),
    "14:20:2": "◇영내 문제의 발생 조건",
    "14:20:3": (
        "\n　·재건(LV1) … 명소가 있는 성의 개발률이 높아지면 발생\n"
        " ·발전(LV2) … 명소가 있는 국의 모든 성의 개발률이 높아지면 발생\n"
        " ·번영(LV3) … 명소가 있는 지방의 모든 성을 보유하면 발생"
    ),
    "14:22:1": (
        "\n　·정책     ... 세력 전체를 강화하는 정책을 발령한다\n"
        " ·평정중    ... 가재나 봉행을 임명해 세력 전체를 강화한다\n"
        " ·논공행상   ... 가신에게 은상을 준다. 활약과 승진을 확인한다\n"
        " ·거래     ... 본거지의 병량과 가보를 매매한다\n"
        " ·인사-상벌  ... 가보나 관직을 가신에게 수여하거나 박탈한다\n"
        " ·인사-혼인  ... 다이묘나 가신의 혼인을 주선한다\n"
        " ·인사-은거  ... 다이묘 자리에서 물러나 일문 무장에게 뒤를 잇게 한다\n"
        " ·인사-해고  ... 가신을 세력에서 추방한다\n"
        " ·군단     ... 무장에게 성과 가신 일부를 맡겨 일임한다\n"
        " ·본거지 이전 ... 자세력의 본거지를 다른 성으로 옮긴다"
    ),
    "14:23:0": "[정책]",
    "14:23:5": (
        "\n일부 정책은 특수 조건을 충족해야 발령할 수 있습니다.\n"
        "조건에는 \"일정 이상의 위신\", \"특정 주의를 지닌 실행 무장\", "
        "\"상위 취락 건설\"이 있습니다.\n"
        "또한 다음 정책은 기독교가 전래되면 해금됩니다.\n"
        "·남만 교역\n"
        "·은 교역\n"
        "·기리시탄 포교(오토모 가문)"
    ),
    "14:24:0": "[정책]",
    "14:24:1": (
        "\n세력 전체에 효과를 주는 정책을 발령합니다.\n"
        "발령에는 준비 기간이 걸리며 실행 무장을 임명해야 합니다.\n"
        "정책을 발령하면 매달 유지비가 들며, 봉행 특성으로 줄일 수도 있습니다.\n"
        "발령할 수 있는 정책에는 세력 고유 정책과 봉행 임명으로 해금되는 정책 등이 있습니다.\n"
        "또한 발령한 정책은 \"LV\"를 올릴 수 있습니다.\n"
        "LV를 올리면 효과가 강화되지만 유지비도 증가합니다.\n"
        "\n"
    ),
    "14:24:5": (
        "\n일부 정책은 특수 조건을 충족해야 발령할 수 있습니다.\n"
        "조건에는 \"일정 이상의 위신\", \"특정 주의를 지닌 실행 무장\",\n"
        "\"상위 취락 건설\", \"세력 목표 달성\"이 있습니다.\n"
        "\n"
        "다음 정책은 철포가 전래되면 해금됩니다.\n"
        "\"포술 지남\", \"용기병 편제(다테 가문)\", \"사이가 총규(스즈키 가문)\"\n"
        "또한 다음 정책은 기독교가 전래되면 해금됩니다.\n"
        "\"남만 교역\", \"은 교역\", \"기리시탄 포교(오토모 가문)\""
    ),
    "14:28:3": (
        "\n　·병량 거래 가능량에는 상한이 있으며 계절마다 갱신된다\n"
        "  (1월, 4월, 7월, 10월)\n"
        " ·계절과 풍작 등의 요인에 따라 병량 시세가 변한다\n"
        " ·본거지의 병량만 거래에 사용된다\n"
        " ·구입할 수 있는 가보는 계절마다 바뀐다\n"
        " ·등급이 높은 가보를 구입하려면 세력 목표 \"총상업\"을 달성해야 한다\n"
        " ·가보를 가신에게 주면 가신의 충성을 높일 수 있다\n"
        " ·가보는 여러 직담에서 교섭 재료로 사용할 수 있다"
    ),
    "14:29:0": "[친선]",
}
TARGET_RECORD_IDS = (13, 14, 16, 17, 18, 20, 22, 23, 24, 28, 29)
EXPECTED_ARITY = {
    13: 4,
    14: 4,
    16: 2,
    17: 6,
    18: 2,
    20: 4,
    22: 2,
    23: 6,
    24: 6,
    28: 4,
    29: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "14:13:0",
    "14:13:1",
    "14:13:2",
    "14:14:0",
    "14:14:1",
    "14:14:2",
    "14:16:1",
    "14:17:1",
    "14:17:3",
    "14:17:4",
    "14:17:5",
    "14:22:0",
    "14:23:1",
    "14:23:2",
    "14:23:3",
    "14:23:4",
    "14:24:2",
    "14:24:3",
    "14:24:4",
    "14:28:0",
    "14:28:1",
    "14:28:2",
    "14:29:1",
    "14:29:2",
    "14:29:3",
    "14:29:4",
    "14:29:5",
)
PREFILL_COMPANION_DONOR = {
    **{
        f"14:13:{literal_id}": f"14:8:{literal_id}"
        for literal_id in (0, 1, 2)
    },
    **{
        f"14:14:{literal_id}": f"14:8:{literal_id}"
        for literal_id in (0, 1, 2)
    },
    "14:16:1": "14:11:1",
    **{
        f"14:17:{literal_id}": f"14:12:{literal_id}"
        for literal_id in (1, 3, 4, 5)
    },
    "14:22:0": "14:15:0",
    **{
        f"14:23:{literal_id}": f"14:16:{literal_id}"
        for literal_id in (1, 2, 3, 4)
    },
    **{
        f"14:24:{literal_id}": f"14:16:{literal_id}"
        for literal_id in (2, 3, 4)
    },
    **{
        f"14:28:{literal_id}": f"14:19:{literal_id}"
        for literal_id in (0, 1, 2)
    },
    **{
        f"14:29:{literal_id}": f"14:20:{literal_id}"
        for literal_id in (1, 2, 3, 4, 5)
    },
}
SEMANTIC_BASE_CONTEXT = {
    13: ("14:9:3",),
    14: ("14:9:3",),
    16: (),
    17: (),
    18: ("14:13:0", "14:13:1"),
    20: ("13:477:0", "13:479:0"),
    22: ("14:15:1",),
    23: tuple(f"14:16:{literal_id}" for literal_id in range(6)),
    24: ("14:16:0", "14:16:5", "13:338:0"),
    28: ("14:19:3",),
    29: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES.update({
    16: ((14, 11),),
    17: ((14, 12),),
    29: ((14, 20),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1320,
    queue_start=67,
    queue_stop=134,
    slice_first="14:13:2",
    slice_last="14:30:0",
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
        (14, record_id) for record_id in range(11, 33)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_help")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("action list", "행동 목록"),
        ("submission", "건의"),
        ("direct talk", "직담"),
        ("province condition", "군단 상황"),
        ("local faction", "국인중"),
        ("allied clan", "동맹 세력"),
        ("landmark", "명소"),
        ("council officials", "평정중"),
        ("conservator", "가재"),
        ("overseer", "봉행"),
        ("honor commendation", "논공행상"),
        ("main base", "본거지"),
        ("troop provisions", "병량"),
        ("tenet", "주의"),
        ("major settlement", "상위 취락"),
        ("total commerce", "총상업"),
        ("emissary", "중개자"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary evidence; three "
        "complete records reuse approved exact Base Korean assemblies, "
        "including all ten exact same-record companions, while eight "
        "PK-specific records use completed Base help entries only as "
        "semantic and register context and never inherit Base runtime or VM "
        "state; all seventeen non-exact prefill companions retain their actual "
        "approved provenance; action-list, direct-talk agreement, local "
        "faction, allied clan, landmark, council official, conservator, "
        "overseer, honor commendation, main base, provisions, policy tenet, "
        "major settlement, firearm-era policy, total commerce and emissary "
        "terms remain distinct; token separators, leading and trailing "
        "newlines, bullets, spacing, terminators, complete record arity, all "
        "forty-eight slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=18,
    pins={
        "expected_queue_universe_sha256": (
            "160AEEE06DBD94C8DBE04555BD1DC6D0C1238B46248E2C38AD615997A364C395"
        ),
        "expected_queue_slice_sha256": (
            "69A0B0D30567A0F3D95AA49A8A0A7C84AA044D80707498F0CFCB786C005DEB5D"
        ),
        "expected_prefilled_coordinate_sha256": (
            "AB960337D9BFEC67386F1205E9FC9929A0BCC129DB9EEB611367FB4EE2C55E20"
        ),
        "expected_prefill_slice_context_sha256": (
            "306A8F88D2BC6BB88BF9F8F6D206ECEADCC52253BA80AA6AB25E7F901DC726B5"
        ),
        "expected_target_coordinate_sha256": (
            "4F214F8631B0FD49C79BA4E61C5540A4350875F232EFD1599E525ED15E00B06B"
        ),
        "expected_source_target_sha256": (
            "EE5BFBD7FAC5DFE9B48E13F04909371CB19B21DCCB055A67AAA2DE1551ECF24E"
        ),
        "expected_current_target_sha256": (
            "74A697FC02C7A8218C7911F124B12FBEB92733FFB40C3D19B6954CC252768532"
        ),
        "expected_context_corpus_sha256": (
            "EDEB29FA8ECCF1E6602A3E1D9A9F643E1D0A827CBB2BAA6BA5F1A360F1899F1A"
        ),
        "expected_gap_contract_sha256": (
            "41BDE3A0E06511BB502A5488984D19B9E9D680692D24739B84015D1974FCDE43"
        ),
        "expected_boundary_sha256": (
            "575EFAF43EC6F06EF79095D09DE863CC68B73B664BCBD18DD2D3680131E96AC1"
        ),
        "expected_runtime_control_sha256": (
            "F0E28FA7A268B8641D8EB083CDF76C476EB5011AF0E53E5B163BC864FBE322AC"
        ),
        "expected_base_search_sha256": (
            "721072E1DDD91B7B10DF452C27C0C58A247D240D4500983159E7D8688F04E955"
        ),
        "expected_complete_assembly_sha256": (
            "69FF65B349046B518BA35D11BFE7B1960711F38C60595442869C927F0295A902"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "D354A589261A902B28883405309005BEA6FE5E6A0E74F271B973714E59280D76"
        ),
        "expected_terminology_policy_sha256": (
            "FB2C964164FF80D108DFD342ED77F0B912E87EE8D0298CCB2C859AE5C67F3CBB"
        ),
        "expected_translation_policy_sha256": (
            "EB3AA7DFFDAA68D76B145790E83A56B478B86696C17D3D0B4014A83E94FA267F"
        ),
        "expected_candidate_sha256": (
            "2442CA65AC6F8B795D6FC3AAD15833025D6B7BD25C1D31703FE010DF0E50542C"
        ),
        "expected_combined_slice_candidate_sha256": (
            "B14DB3E67E33323F9BE9031E8345635137378500D28DBEA03A7EAFEE63C89952"
        ),
        "expected_combined_changed_literal_count": 52,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B105_S1320",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B105_S1320.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B105_S1319.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B105_S1321.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B105",
    "queue_row_count": 69,
    "queue_visible_count": 199,
    "queue_first": "13:621:0",
    "queue_last": "14:44:5",
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
        raise RuntimeError("segment 1320 Base promoted input drifted")
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
        16: (14, 11),
        17: (14, 12),
        29: (14, 20),
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
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
                f"segment 1320 Base search drifted: {record_id}"
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
                    "segment 1320 Base context drifted: "
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
                        f"segment 1320 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1320 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1320 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1320 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            16: (14, 11),
            17: (14, 12),
            29: (14, 20),
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
