#!/usr/bin/env python3
"""Build source-redacted PK B136 segment 1414 residual decisions."""

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

TARGET_RECORD_IDS = tuple(range(128, 154))
MAIN_RECORD_IDS = tuple(range(129, 154))
TARGET_COORDINATES = (
    "17:128:1",
    "17:129:0",
    "17:129:1",
    "17:129:2",
    "17:130:0",
    "17:130:1",
    "17:130:2",
    "17:131:0",
    "17:131:1",
    "17:132:0",
    "17:132:1",
    "17:133:0",
    "17:133:1",
    "17:133:2",
    "17:134:0",
    "17:134:1",
    "17:135:0",
    "17:135:1",
    "17:135:2",
    "17:136:0",
    "17:136:1",
    "17:136:2",
    "17:136:3",
    "17:137:0",
    "17:137:1",
    "17:137:2",
    "17:137:3",
    "17:138:0",
    "17:139:0",
    "17:139:1",
    "17:139:2",
    "17:140:0",
    "17:140:1",
    "17:140:2",
    "17:141:0",
    "17:141:1",
    "17:141:2",
    "17:142:0",
    "17:142:1",
    "17:142:2",
    "17:143:0",
    "17:144:0",
    "17:144:1",
    "17:144:2",
    "17:144:3",
    "17:144:4",
    "17:145:0",
    "17:145:1",
    "17:145:2",
    "17:146:0",
    "17:146:1",
    "17:146:2",
    "17:147:0",
    "17:147:1",
    "17:148:0",
    "17:148:1",
    "17:149:0",
    "17:149:1",
    "17:150:0",
    "17:151:0",
    "17:152:0",
    "17:152:1",
    "17:152:2",
    "17:153:0",
)
MAIN_TARGET_COORDINATES = TARGET_COORDINATES[1:]
TRANSLATIONS = {
    "17:128:1": "을 탈취하라",
    "17:129:0": "덴노잔",
    "17:129:1": "을 탈취하라",
    "17:129:2": " 성공",
    "17:130:0": "덴노잔",
    "17:130:1": "을 탈취하라",
    "17:130:2": " 실패",
    "17:131:0": "덴노잔",
    "17:131:1": ", 제압했다!",
    "17:132:0": "잘했다,",
    "17:132:1": "!",
    "17:133:0": (
        "이제 산꼭대기로 예비 군기를 옮기겠다……\n"
        "준비가 끝날 때까지,"
    ),
    "17:133:1": "덴노잔",
    "17:133:2": "을 적에게 넘기지 마라!",
    "17:134:0": "덴노잔",
    "17:134:1": "을 끝까지 지켜 내면\n내 계책은 성공한다!",
    "17:135:0": "요충지 효과「",
    "17:135:1": "고무",
    "17:135:2": "」를 발동하라",
    "17:136:0": "요충지 효과「",
    "17:136:1": "고무",
    "17:136:2": "」를 발동하라",
    "17:136:3": " 성공",
    "17:137:0": "요충지 효과「",
    "17:137:1": "고무",
    "17:137:2": "」를 발동하라",
    "17:137:3": " 실패",
    "17:138:0": (
        "산기슭 주전장을 비우면서까지\n"
        "산꼭대기로 부대를 올려 보낸다고……?"
    ),
    "17:139:0": "목표는 주군의 본진인가?\n진로를 바꿔라!\u3000",
    "17:139:1": "덴노잔",
    "17:139:2": "을 탈환하라!",
    "17:140:0": "예비 군기를 모두 가져왔습니다\n주군께서는",
    "17:140:1": " 아카이",
    "17:140:2": "를 흉내 내면 된다고만 하셨습니다……",
    "17:141:0": "……",
    "17:141:1": "단바",
    "17:141:2": "를 공략했을 때 쓴 그 수법인가!\n당장 모든 군기를 이곳에 세워라!",
    "17:142:0": "아케치",
    "17:142:1": "군이 어마어마한 대군이라고\n",
    "17:142:2": "주군이 생각하면 우리의 승리다",
    "17:143:0": "준비는 모두 끝났다!\n모두 함성을 올려라!",
    "17:144:0": "야마자키",
    "17:144:1": "에서 승리의 함성이 들리는군……\n",
    "17:144:2": "하시바",
    "17:144:3": "군의 함성이겠지,",
    "17:144:4": "?",
    "17:145:0": "아니, 저것을……\n",
    "17:145:1": "덴노잔",
    "17:145:2": "을 보십시오",
    "17:146:0": (
        "산꼭대기에만 도라지 문양 군기가 저토록 많다니……?\n"
    ),
    "17:146:1": "아케치",
    "17:146:2": "군은 어찌 저리 대군이란 말인가……!",
    "17:147:0": (
        "에게 돌아서기로 한 약조는 무효다!\n서둘러"
    ),
    "17:147:1": "주군을 도우러 간다!",
    "17:148:0": "쓰쓰이",
    "17:148:1": (
        "의 원군……!\n산꼭대기 위장이 제대로 통했나 봅니다"
    ),
    "17:149:0": "전 부대, 원군과 함께 진격하라!\n",
    "17:149:1": "을(를) 쓰러뜨리면 우리의 승리다!",
    "17:150:0": "그 정도는 예상했다! 전군, 이 정도 일로 당황하지 마라!",
    "17:151:0": (
        "주군께서 내다보고 계셨다니……\n"
        "저 군사님만 있으면 두려울 것이 없다!"
    ),
    "17:152:0": "성가신 군사가 있군",
    "17:152:1": "보다 먼저\n",
    "17:152:2": "을(를) 쳐서 적의 사기를 떨어뜨려라!",
    "17:153:0": "군사인 나부터 쓰러뜨리다니\n싸움을 아는 자로군……",
}
EXPECTED_ARITY = {
    128: 2,
    129: 3,
    130: 3,
    131: 2,
    132: 2,
    133: 3,
    134: 2,
    135: 3,
    136: 4,
    137: 4,
    138: 1,
    139: 3,
    140: 3,
    141: 3,
    142: 3,
    143: 1,
    144: 5,
    145: 3,
    146: 3,
    147: 2,
    148: 2,
    149: 2,
    150: 1,
    151: 1,
    152: 3,
    153: 1,
}
NEIGHBOR_COMPANION_TRANSLATIONS = {"17:128:0": "덴노잔"}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ("9:2842:0", "9:3031:0")
        for record_id in range(128, 132)
    },
    132: ("7:1974:1",),
    133: ("9:1006:0", "9:2750:0"),
    134: ("9:2750:0", "9:3031:0"),
    135: ("14:95:3",),
    136: ("14:95:3",),
    137: ("14:95:3",),
    138: ("9:3031:0",),
    139: ("9:3031:0",),
    140: ("9:1006:0",),
    141: ("9:1006:0",),
    142: ("9:1006:0",),
    143: ("9:1006:0",),
    144: ("7:748:0",),
    145: ("9:3031:0",),
    146: ("9:1006:0",),
    147: ("9:3792:0",),
    148: ("9:3792:0",),
    149: ("9:3792:0",),
    150: ("9:3792:0",),
    151: ("7:1040:0",),
    152: ("9:2787:0",),
    153: ("7:1040:0",),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    132: ((), ("024835",)),
    142: ((), ("024834",)),
    144: ((), ("024835",)),
    147: ((), ("024835", "024934")),
    149: ((), ("024835",)),
    151: ((), ("024835",)),
    152: ((), ("024835", "024935")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1414,
    queue_start=134,
    queue_stop=198,
    slice_first="17:128:1",
    slice_last="17:153:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (17, record_id) for record_id in range(90, 180)
    ),
    speaker_style=(
        (128, "scenario_objective"),
        (129, "scenario_objective_success"),
        (130, "scenario_objective_failure"),
        (131, "commanding_strategic_point_capture"),
        (132, "commanding_officer_praise"),
        (133, "commanding_banner_transport_defense"),
        (134, "resolute_strategic_point_defense"),
        (135, "scenario_objective"),
        (136, "scenario_objective_success"),
        (137, "scenario_objective_failure"),
        (138, "astonished_summit_advance"),
        (139, "commanding_recapture_order"),
        (140, "formal_reserve_banner_report"),
        (141, "commanding_historical_ruse_recognition"),
        (142, "confident_deception_plan"),
        (143, "commanding_war_cry_order"),
        (144, "reflective_distant_victory_cry"),
        (145, "formal_summit_attention"),
        (146, "astonished_apparent_large_army"),
        (147, "commanding_defection_reversal"),
        (148, "formal_reinforcement_and_deception_report"),
        (149, "commanding_reinforcement_advance"),
        (150, "commanding_unshaken_response"),
        (151, "rough_confident_strategist_praise"),
        (152, "commanding_enemy_strategist_target"),
        (153, "impressed_defeated_strategist"),
    ),
    terminology_policy=(
        ("strategic mountain", "덴노잔"),
        ("strategic point effect", "요충지 효과"),
        ("inspire", "고무"),
        ("reserve banners", "예비 군기"),
        ("bellflower crest banners", "도라지 문양 군기"),
        ("main camp", "본진"),
        ("defection", "돌아서다"),
        ("all units", "전 부대"),
        ("strategist", "군사"),
        ("dynamic particle", "을(를)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire B136 queue slice from zero-based ordinals one hundred "
        "thirty-four through one hundred ninety-seven because no approved "
        "Base prefill exists in the slice; pristine PK JP is authoritative, "
        "every available EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context, and records without auxiliary "
        "translations were reviewed from their complete JP assemblies, "
        "colour controls and adjacent scenario sequence; completed Base "
        "battle, strategic-point, banner and command rows are used only as "
        "semantic and glossary context and never contribute runtime or VM "
        "state; the left-boundary mountain-capture record is completed with "
        "the manually reviewed fragment owned by optional segment 1413 and "
        "any landed neighbor decision must match that assembly; the "
        "strategic mountain, strategic-point effect, inspire effect, reserve "
        "banners, bellflower crest banners, main camp, defection and "
        "strategists retain established historical project wording; "
        "objective labels remain concise while dialogue preserves each "
        "commanding, resolute, formal, reflective, astonished or rough "
        "register; colour tags, inline person and role tokens, protected "
        "full-width spaces, outer whitespace, line breaks, dynamic "
        "particles, punctuation, terminators, complete record arity, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=24,
    pins={
        "expected_queue_universe_sha256": "9875C5BDFC630EE0ACB5EB425F8ADE458E850FCAF249DD388A37E7336B631D1B",
        "expected_queue_slice_sha256": "606B7C7A99D359DAD668A2A0CA751086286E9D068CF4C6D99358F429E2DF6A1F",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "606B7C7A99D359DAD668A2A0CA751086286E9D068CF4C6D99358F429E2DF6A1F",
        "expected_source_target_sha256": "69ED2890BBB53F014F87E4FB2E809673340BBD448588DF01C462D9776DA5F719",
        "expected_current_target_sha256": "8B0C13A8785D56ED1BE356C6663B7FCA4D05135812D9DB5078ECBC487B5186A4",
        "expected_context_corpus_sha256": "02EB336E27DC8BD87228E49E57CB46F10056DE13C4F4FFCC4BDFE71D3A645836",
        "expected_gap_contract_sha256": "766F9FE16BDAF6689741F032EA457AEC449656FB4C95F8EC283AE54B8C010BDB",
        "expected_boundary_sha256": "50E802592F62D18832CE4015D06E518C733A8146A3D8DE65708A54A6188751CB",
        "expected_runtime_control_sha256": "BADDCEA2DDB424D17E09702DB04998FC4675119F5BE64D9B4B6302D25B6F721D",
        "expected_base_search_sha256": "2D13D713B3F39310DF7FCF84E2EC8F6B5C4058DAAD5220E1074ED9E80130EF0B",
        "expected_complete_assembly_sha256": "4CA5A16CF0DDB6A00513E4A245F92D039F0815FCADC9F01A9F2C2DB119FAEE73",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "554DC3D72A6F20C90E66AFDFCBCD9139879D2B13541B1EF21BA4B4DD2BBD636C",
        "expected_terminology_policy_sha256": "3E40FB7BBF61C29080726923488F5A8C21268287F1C1CC7BEA25DA9E0A2A1A93",
        "expected_translation_policy_sha256": "632F31B6CEEFF184E934B13FB07102E84894B9EEB2FEC0045D2D8220E4FF7E20",
        "expected_candidate_sha256": "8534381FC5577BBCFD3667A7F33BE4C8F81BF37106F495BAC53BA26F063F6DB9",
        "expected_combined_slice_candidate_sha256": "8534381FC5577BBCFD3667A7F33BE4C8F81BF37106F495BAC53BA26F063F6DB9",
        "expected_combined_changed_literal_count": 24,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B136_S1414",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B136_S1414.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B136_S1412.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B136_S1413.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B136",
    "queue_row_count": 96,
    "queue_visible_count": 198,
    "queue_first": "17:58:0",
    "queue_last": "17:153:0",
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
    key = (17, 128)
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
    references: list[tuple[Any, ...]] = []
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[128]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1414 Base context drifted: "
                f"{donor_coordinate}"
            )
        references.append((
            donor_coordinate,
            str(donor["translation"]),
            str(donor["runtime_review"]),
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
            f"segment 1414 neighbor companion drifted: {neighbor_coordinate}"
        )
    assembled = (expected, TRANSLATIONS["17:128:1"])
    if (
        len(source_literals) != EXPECTED_ARITY[128]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[128]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[128]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[128]
        or assembled != ("덴노잔", "을 탈취하라")
    ):
        raise RuntimeError("segment 1414 boundary assembly drifted")
    return (
        tuple(base_evidence) + ((
            128,
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
            "semantic_context_only",
        ),),
        tuple(assembly_evidence) + ((
            128,
            (
                "optional_previous_segment_manual_companion",
                "segment_manual_multilingual",
            ),
            assembled,
            None,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ),),
    )


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


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
