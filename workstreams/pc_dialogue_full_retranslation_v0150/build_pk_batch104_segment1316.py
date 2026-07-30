#!/usr/bin/env python3
"""Build source-redacted PK B104 segment 1316 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_BASE_ASSEMBLY = COMMON.BASE.base_and_assembly_evidence
_ORIGINAL_BASE_READ_JSONL = COMMON.BASE.read_jsonl

TARGET_RECORD_IDS = (
    445, 446, 447, 451, 452, 454, 463, 464, 470, 473,
    475, 486, 487, 489, 491, 492, 493, 495, 498, 499,
)
TARGET_COORDINATES = (
    "13:445:1",
    "13:446:1",
    "13:447:1",
    "13:447:3",
    "13:451:0",
    "13:452:0",
    "13:454:0",
    "13:463:0",
    "13:464:0",
    "13:470:0",
    "13:473:0",
    "13:475:0",
    "13:486:0",
    "13:487:0",
    "13:489:0",
    "13:491:0",
    "13:492:0",
    "13:493:0",
    "13:495:0",
    "13:498:0",
    "13:499:0",
)
TRANSLATIONS = {
    "13:445:1": " ┨ ",
    "13:446:1": " ┨ ",
    "13:447:1": "┨",
    "13:447:3": "┯",
    "13:451:0": (
        "[정리: 내정]\n"
        "·\"지행\"과 \"대관\"으로 자신의 영지 내정을 가신에게 맡긴다\n"
        "·\"군 개발\"과 \"성하 시설\"로 성을 강화한다\n"
        "·\"정책\"과 \"평정중\"으로 세력 전체를 강화한다"
    ),
    "13:452:0": (
        "[정리: 외교와 군략]\n"
        "·\"친선\"으로 다른 가문과의 관계를 개선한다\n"
        "·\"출진\"해 적의 성을 제압하고 영토를 넓힌다\n"
        "\n"
        "[무엇을 해야 할지 모르겠다면]\n"
        "·화면 오른쪽 위 메뉴의 \"헌언\"에서 가신에게 묻는다"
    ),
    "13:454:0": (
        "군비 거점에는 임전 상태인 군의 수가 표시되며\n"
        "모든 군이 임전 상태가 되면 아이콘 색이 바뀝니다.\n"
        "※성대와 군다이가 맡은 군은 임전 상태가 되지 않습니다.\n"
        "\n"
        "임전 상태인 군이 많을수록 부대가 강화되어 오래 출진할 수 있지만\n"
        "모든 군이 임전 상태가 되기 전에도 출진할 수 있습니다."
    ),
    "13:463:0": (
        "[침공받기 전의 준비 예]\n"
        "·전선의 성을 방위 거점으로 설정해 방어를 강화한다\n"
        "·방위 거점 주변의 성을 지원 거점으로 설정해 "
        "방위 거점에 병력을 집결시킨다"
    ),
    "13:464:0": (
        "[침공받았을 때의 대처 예]\n"
        "·부대를 출진시켜 요격한다\n"
        "·동맹 세력에 원군을 요청한다\n"
        "·병력이나 위신이 높은 세력에 정전 중재를 부탁한다\n"
        "·외교로 정전 교섭을 한다"
    ),
    "13:470:0": "\"풍문\"",
    "13:473:0": (
        "휘하 무장이 스스로 판단해 진군로를 바꾸었습니다.\n"
        "적의 성을 포위하고 주변 가도를 봉쇄하면 공성전에서 유리하므로\n"
        "이를 노린 행동인 듯합니다.\n"
        "\n"
        "무장들은 이처럼 상황을 스스로 판단하기도 합니다.\n"
        "필요하다면 직접 지시해 효율적으로 공성전을 진행합시다."
    ),
    "13:475:0": (
        "충성이 낮은 무장은 성이 함락되기 전에 항복하기도 합니다.\n"
        "항복한 성주는 반드시 상대 세력의 등용에 응합니다.\n"
        "\n"
        "충성이 낮은 무장을 전선의 성주로 임명한다면\n"
        "가보나 관직을 내려 충성을 높게 유지합시다."
    ),
    "13:486:0": (
        "정책 \"제도 개신\"이 LV3로 오르면서\n"
        "\"성주의 지행지 교체\"를 할 수 있게 되었습니다.\n"
        "자세력의 영지를 점검해 지행지 배분을 다시 검토합시다.\n"
        "\n"
        "[해금된 내용]\n"
        "·성주의 지행지 교체\n"
        "·빈 군에 성주/영주/대관 자동 임명"
    ),
    "13:487:0": "\"위풍\"",
    "13:489:0": (
        "많은 적 부대를 상대로 합전이나 공성전에서 승리하면\n"
        "그 명성이 \"위풍\"이 되어 주변에 퍼지고 영향을 미칩니다.\n"
        "단순히 적을 격파한 것보다 큰 전과를 얻을 수 있으므로\n"
        "적 부대가 많다면 적극적으로 승리를 노립시다.\n"
        "\n"
        "또한 위풍으로 동요한 성은 한동안 설비를 건설하거나 "
        "출진할 수 없습니다.\n"
        "연달아 공격해 더 많은 성의 제압을 노릴 수도 있습니다."
    ),
    "13:491:0": (
        "정책 \"제도 개신\" LV3 발령으로 성주를 교체할 수 있게 되었습니다.\n"
        "\n"
        "성 능력에 따라 설정 가능한 성하 방침의 종류도 달라지므로\n"
        "성의 상황에 맞춰 지행지를 배분합시다.\n"
        "※설정 가능한 성하 방침은 \"능력 보정\" 탭에서 확인할 수 있습니다."
    ),
    "13:492:0": (
        "정책 \"제도 개신\" LV3 발령으로 성주를 교체하거나\n"
        "빈 군의 지행 배정/대관 자동 임명을 할 수 있게 되었습니다.\n"
        "\n"
        "성 능력에 따라 설정 가능한 성하 방침도 달라지므로\n"
        "성의 상황에 맞춰 지행지를 배분합시다.\n"
        "※설정 가능한 성하 방침은 \"보정\" 탭에서 확인할 수 있습니다."
    ),
    "13:493:0": "\"재해\"",
    "13:495:0": "\"잇키\"",
    "13:498:0": (
        "본거지를 이전할 수 있습니다.\n"
        "통치 범위 밖의 성을 얻었다면 이전을 검토합시다.\n"
        "큰 비용이 드므로 신중히 결정하는 것이 중요합니다.\n"
        "\n"
        "※통치 범위 밖의 성에서는 금전 수입이 크게 줄어듭니다\n"
        "※본거지를 옮기지 않고 성을 군단에 맡길 수도 있습니다"
    ),
    "13:499:0": (
        "본거지를 이전할 수 있습니다.\n"
        "통치 범위 밖의 성을 얻었다면 이전을 검토합시다.\n"
        "큰 비용이 드므로 신중히 결정하는 것이 중요합니다.\n"
        "\n"
        "※통치 범위 밖의 성에서는 금전 수입이 크게 줄어듭니다\n"
        "※본거지를 옮기지 않고 성을 군단에 맡길 수도 있습니다\n"
        "※정책 \"전마제\"를 발령하면 통치 범위를 넓힐 수 있습니다"
    ),
}
EXPECTED_ARITY = {
    record_id: (
        3 if record_id in {445, 446}
        else 5 if record_id == 447
        else 1
    )
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = (
    "13:445:0",
    "13:445:2",
    "13:446:0",
    "13:446:2",
    "13:447:0",
    "13:447:2",
    "13:447:4",
)
PREFILL_COMPANION_DONOR = {
    "13:445:0": "13:410:0",
    "13:445:2": "13:410:2",
    "13:446:0": "13:410:0",
    "13:446:2": "13:411:2",
    "13:447:0": "13:412:0",
    "13:447:2": "13:412:2",
    "13:447:4": "13:412:4",
}
SEMANTIC_BASE_CONTEXT = {
    445: (),
    446: (),
    447: (),
    451: ("13:415:0",),
    452: ("13:416:0",),
    454: ("13:418:0",),
    463: ("13:425:0", "13:426:0"),
    464: ("13:426:0",),
    470: (),
    473: ("13:435:0",),
    475: ("13:437:0",),
    486: ("13:447:0",),
    487: (),
    489: ("13:449:0",),
    491: ("13:451:0",),
    492: ("13:451:0", "13:447:0"),
    493: (),
    495: (),
    498: ("13:457:0",),
    499: ("13:457:0",),
}
EXPECTED_BASE_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES.update({
    445: ((13, 410),),
    446: ((13, 411),),
    447: ((13, 412),),
    470: ((13, 432),),
    487: ((13, 448),),
    493: ((13, 452),),
    495: ((13, 454),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1316,
    queue_start=0,
    queue_stop=67,
    slice_first="13:445:0",
    slice_last="13:503:0",
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
        (13, record_id) for record_id in range(443, 506)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("page attendant", "고쇼"),
        ("submission", "건의"),
        ("council officials", "평정중"),
        ("militarization base", "군비 거점"),
        ("defense base", "방위 거점"),
        ("assistance base", "지원 거점"),
        ("truce mediation", "정전 중재"),
        ("hearsay", "풍문"),
        ("marching route", "진군로"),
        ("road", "가도"),
        ("castle assault", "공성전"),
        ("system reform", "제도 개신"),
        ("fief reassignment", "지행지 교체"),
        ("authority", "위풍"),
        ("castle town plan", "성하 방침"),
        ("disaster", "재해"),
        ("uprising", "잇키"),
        ("main base", "본거지"),
        ("postal system", "전마제"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record tutorial was reviewed as auxiliary context; seven "
        "complete records use approved exact completed Base semantic "
        "assemblies, including four protected icon literals, while the "
        "remaining records adapt the nearest completed Base tutorial text "
        "for PK-only council, defense-base, siege, auto-appointment and "
        "authority additions; Base runtime and VM state are never inherited; "
        "page-attendant submission categories, military and defense bases, "
        "truce mediation, marching routes, castle assault, system reform, "
        "fief reassignment, disasters, uprisings and main-base relocation "
        "retain distinct established terms; icon color gaps, outer spaces, "
        "controller-independent literals, quote policy, headings, note "
        "markers, line counts, literal arity, terminators, seven same-record "
        "static prefill companions, all forty-six slice prefills, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=17,
    pins={
        "expected_queue_universe_sha256":
        "D4AE7DDA94614C143AE30701F35BBEAB4BA7BEF23696A8BA65086F8ACFC573DD",
        "expected_queue_slice_sha256":
        "63962D97B63897DED9588DF45813BCF6A7E86D47FDE8A5361703854E101ED0A5",
        "expected_prefilled_coordinate_sha256":
        "D78FBA1FC1A181559F3218325757A10B78B5418EE8FBFDD8950F50AFBA2BCCC2",
        "expected_prefill_slice_context_sha256":
        "958C911666FBE013B68D5F8326E5F444957152B319D2CBCFBB6E634C0CA26143",
        "expected_target_coordinate_sha256":
        "CA3C32C48891C0268AFA2B3AAADA496B7D27EA715160CBC6A272B11BEFBE6583",
        "expected_source_target_sha256":
        "217FBD89399A578A881130EBA607547EC2C47CF164AA91D90A1302E681CA5855",
        "expected_current_target_sha256":
        "3B1A4C84869565C9AC18DC28ECE452F6580E787441096A31962F1F96F1ABA7FB",
        "expected_context_corpus_sha256":
        "EF31A2EF18EADB612070AE3F8582EA2A24FBEBA2A93DAB4EED92AFA008D5A77A",
        "expected_gap_contract_sha256":
        "35FF25F2D1707DAE308553122DBF86882749B7B357072078A8F7CBC0E856E758",
        "expected_boundary_sha256":
        "7B2A73B4B0F87FC9D06F2032E008A79F8671FF770FBA7689AC1E8459C8F8BD9F",
        "expected_runtime_control_sha256":
        "464CC5DE7FE7E7F6D4FE46DC20A7480DC56C1F4C0B00F8DC2A88F1FB43907A76",
        "expected_base_search_sha256":
        "7DDC3045BEBB9DDF8A7AA428C85BE64FD88A37C308D81AF46ADBC9A1D1B88857",
        "expected_complete_assembly_sha256":
        "785870481D453229FEC641FD40DD1D839DBE2C11E942103202527BC80F713455",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "EF21F27D4074FC3987A4F2EFF8C06C86199C06FF3D101A78845FE7B7A5BC6FF2",
        "expected_terminology_policy_sha256":
        "3AF866031CB0AFCEBEE346A4DB54F5DCB2E2717F0271808EEAE93D6144CFAC56",
        "expected_translation_policy_sha256":
        "8AFE865FDE0EE957F2EBFABC6B8F689224F7ECEDC82BC941D88B5056AF96B0FE",
        "expected_candidate_sha256":
        "AF6E62AD2F488CE0D01063EF384C684AF4797A5BE69F155FB4FC7EE9652E1783",
        "expected_combined_slice_candidate_sha256":
        "838E4FE25E9386443DBAE14A80F4EEEB44A5A2C1F68362C44788D3040897E39D",
        "expected_combined_changed_literal_count": 63,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B104_S1316",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B104_S1316.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1315.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B104_S1317.private.v1.jsonl",
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
    """Accept the generated static companions without runtime promotion."""

    def compatible_read_jsonl(path: Path) -> list[dict[str, Any]]:
        rows = _ORIGINAL_BASE_READ_JSONL(path)
        if path != COMMON.PREFILL:
            return rows
        compatible: list[dict[str, Any]] = []
        for row in rows:
            copied = dict(row)
            coordinate = str(copied.get("coordinate", ""))
            if coordinate in PREFILL_COMPANION_COORDINATES:
                if copied.get("runtime_review") != "not_required":
                    raise RuntimeError(
                        "segment 1316 static prefill review drifted"
                    )
                copied["runtime_review"] = "pending"
            compatible.append(copied)
        return compatible

    original_read_jsonl = COMMON.BASE.read_jsonl
    COMMON.BASE.read_jsonl = compatible_read_jsonl
    try:
        base, assembly = _ORIGINAL_BASE_ASSEMBLY(
            prepared, records_by_label
        )
    finally:
        COMMON.BASE.read_jsonl = original_read_jsonl

    adjusted: list[tuple[Any, ...]] = []
    for evidence in assembly:
        record_id = int(evidence[0])
        owners = list(evidence[1])
        for literal_id, owner in enumerate(owners):
            coordinate = f"13:{record_id}:{literal_id}"
            if coordinate in PREFILL_COMPANION_COORDINATES:
                if owner != "base_exact_prefill_runtime_pending":
                    raise RuntimeError(
                        "segment 1316 static prefill ownership drifted"
                    )
                owners[literal_id] = (
                    "base_exact_prefill_runtime_not_required"
                )
        adjusted.append((evidence[0], tuple(owners), *evidence[2:]))
    return base, tuple(adjusted)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 13)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            445: (13, 410),
            446: (13, 411),
            447: (13, 412),
            470: (13, 432),
            487: (13, 448),
            493: (13, 452),
            495: (13, 454),
        },
    )
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        base_and_assembly_evidence,
    )


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
