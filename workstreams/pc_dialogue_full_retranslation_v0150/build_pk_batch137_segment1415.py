#!/usr/bin/env python3
"""Build source-redacted PK B137 segment 1415 residual decisions."""

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

TARGET_COORDINATES = (
    "17:154:0", "17:154:1", "17:154:2", "17:154:3",
    "17:155:0", "17:155:1",
    "17:156:0",
    "17:157:0", "17:157:1",
    "17:158:0", "17:158:1",
    "17:159:0", "17:159:1", "17:159:2",
    "17:160:0", "17:160:1",
    "17:161:0", "17:161:1",
    "17:162:0", "17:162:1", "17:162:2",
    "17:163:0", "17:163:1",
    "17:164:0",
    "17:165:0", "17:165:1", "17:165:2", "17:165:3", "17:165:4",
    "17:166:0", "17:166:1",
    "17:167:0", "17:167:1",
    "17:168:0", "17:168:1", "17:168:2",
    "17:169:0", "17:169:1", "17:169:2", "17:169:3", "17:169:4",
    "17:170:0", "17:170:1", "17:170:2",
    "17:171:0",
    "17:172:0", "17:172:1",
    "17:173:0", "17:173:1", "17:173:2", "17:173:3",
    "17:174:0",
    "17:175:0", "17:175:1", "17:175:2",
    "17:176:0",
    "17:177:0", "17:177:1",
    "17:178:0", "17:178:1",
    "17:179:0", "17:179:1",
    "17:180:0", "17:180:1", "17:180:2",
    "17:181:0", "17:181:1",
)

TRANSLATIONS = {
    "17:154:0": "설마",
    "17:154:1": "가 당하다니!\n큭,",
    "17:154:2": "미쓰히데",
    "17:154:3": "의 군략이 이 정도일 줄이야!",
    "17:155:0": "전 부대는 원군에 맞춰 진격하라!\n",
    "17:155:1": "를 쓰러뜨리면 우리의 승리다!",
    "17:156:0": "격파하라",
    "17:157:0": "격파하라",
    "17:157:1": " 성공",
    "17:158:0": "격파하라",
    "17:158:1": " 실패",
    "17:159:0": "에",
    "17:159:1": "덴노잔",
    "17:159:2": (
        "을 빼앗겼다고……?\n"
        "내 계책은 실패한 것인가……"
    ),
    "17:160:0": "적어도,",
    "17:160:1": (
        "와 동귀어진해서라도 일격을 갚겠다\n"
        "전군, 전진하라!"
    ),
    "17:161:0": "의 본대가 저곳이다!\n전군 전진!",
    "17:161:1": "의 목을 베어라!",
    "17:162:0": "내 그릇으로는 천하에 닿지 못하는가……\n",
    "17:162:1": ", ",
    "17:162:2": ", 미안하다……",
    "17:163:0": (
        "우리의 승리다!\n"
        "다음으로 천하를 다스릴 자는"
    ),
    "17:163:1": "로다!",
    "17:164:0": (
        "때는 지금이 아니었던가……?\n"
        "아무것도 이루지 못하고 역적으로 끝나는가……"
    ),
    "17:165:0": "강행군을 한 보람이 있어\n",
    "17:165:1": "아케치",
    "17:165:2": "와의 싸움은",
    "17:165:3": "하시바 가문",
    "17:165:4": (
        "이 주도하게 됐습니다\n"
        "자, 역적 토벌의 공을 차지하러 갑시다"
    ),
    "17:166:0": "아케치",
    "17:166:1": (
        "군은 생각보다 적은 병력이군\n"
        "서둘러 군을 돌린 것이 효과를 봤나……"
    ),
    "17:167:0": "자……\n이번에는 어떻게 이길까,",
    "17:167:1": "?",
    "17:168:0": "모반을 일으킨 ",
    "17:168:1": "아케치",
    "17:168:2": (
        "군은 지면 끝이다……\n"
        "죽기를 각오하고 정면 돌파를 노리겠지"
    ),
    "17:169:0": "이곳에서는,",
    "17:169:1": "덴노잔",
    "17:169:2": "와",
    "17:169:3": "숲가의 요충지",
    "17:169:4": (
        "를 제압해\n"
        "양쪽 측면에서 적진을 공격해야 할 듯합니다"
    ),
    "17:170:0": (
        "포위해 기세를 꺾어 버리면\n"
        "병력이 적은"
    ),
    "17:170:1": "아케치",
    "17:170:2": "에게 승산은 없습니다",
    "17:171:0": "잘 알겠다!\n나머지는 내게 맡겨라!",
    "17:172:0": "이곳에서 반드시",
    "17:172:1": "님의 원수를 갚자!\n모두, 분발하라!",
    "17:173:0": "우선",
    "17:173:1": "덴노잔",
    "17:173:2": "을 제압하는 것부터지?\n",
    "17:173:3": ", 네게 맡기겠다!",
    "17:174:0": (
        "중앙 부대는 정면을 지켜라\n"
        "계책이 성사될 때까지 적의 공세를 견뎌라"
    ),
    "17:175:0": (
        "승리해 천하를 우리 것으로 만들겠다!\n"
        "무슨 수를 써서라도"
    ),
    "17:175:1": "히데요시",
    "17:175:2": "를 쳐라!",
    "17:176:0": "격파하라",
    "17:177:0": "격파하라",
    "17:177:1": " 성공",
    "17:178:0": "격파하라",
    "17:178:1": " 실패",
    "17:179:0": "덴노잔",
    "17:179:1": "을 탈취하라",
    "17:180:0": "덴노잔",
    "17:180:1": "을 탈취하라",
    "17:180:2": " 성공",
    "17:181:0": "덴노잔",
    "17:181:1": "을 탈취하라",
}

TARGET_RECORD_IDS = tuple(range(154, 182))
MAIN_RECORD_IDS = TARGET_RECORD_IDS[:-1]
MAIN_TARGET_COORDINATES = TARGET_COORDINATES[:-2]
EXPECTED_ARITY = {
    154: 4, 155: 2, 156: 1, 157: 2, 158: 2, 159: 3,
    160: 2, 161: 2, 162: 3, 163: 2, 164: 1, 165: 5,
    166: 2, 167: 2, 168: 3, 169: 5, 170: 3, 171: 1,
    172: 2, 173: 4, 174: 1, 175: 3, 176: 1, 177: 2,
    178: 2, 179: 2, 180: 3, 181: 3,
}
NEIGHBOR_COMPANION_TRANSLATIONS = {"17:181:2": " 실패"}

DEFEAT_RECORD_IDS = (156, 157, 158, 176, 177, 178)
TENNOZAN_OBJECTIVE_RECORD_IDS = (179, 180, 181)
REFLECTIVE_RECORD_IDS = (154, 159, 160, 162, 164)
COMMAND_RECORD_IDS = (
    155, 161, 163, 165, 166, 167, 168, 169, 170, 171,
    172, 173, 174, 175,
)
SEMANTIC_BASE_CONTEXT = {
    **{record_id: ("7:1974:1",) for record_id in DEFEAT_RECORD_IDS},
    **{
        record_id: ("9:2842:0",)
        for record_id in TENNOZAN_OBJECTIVE_RECORD_IDS
    },
    **{record_id: ("7:1040:0",) for record_id in REFLECTIVE_RECORD_IDS},
    **{record_id: ("9:3792:0",) for record_id in COMMAND_RECORD_IDS},
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    154: ((), ("024835",)),
    155: ((), ("024835",)),
    159: ((), ("024835",)),
    160: ((), ("024835",)),
    161: ((), ("024835", "024833")),
    162: ((), ("024835", "024935")),
    163: ((), ("024833",)),
    167: ((), ("024835",)),
    172: ((), ("024835",)),
    173: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1415,
    queue_start=0,
    queue_stop=67,
    slice_first="17:154:0",
    slice_last="17:181:1",
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
        (17, record_id) for record_id in range(120, 220)
    ),
    speaker_style=(
        (154, "astonished_at_mitsuhide_strategy"),
        (155, "commanding_reinforcement_advance"),
        (156, "scenario_defeat_objective"),
        (157, "scenario_defeat_objective_success"),
        (158, "scenario_defeat_objective_failure"),
        (159, "despairing_tennozan_loss"),
        (160, "desperate_final_advance"),
        (161, "commanding_enemy_main_force_attack"),
        (162, "dying_regret_and_apology"),
        (163, "triumphant_unification_declaration"),
        (164, "mitsuhide_dying_reflection"),
        (165, "confident_hashiba_initiative_report"),
        (166, "confident_akechi_force_assessment"),
        (167, "confident_strategy_consultation"),
        (168, "formal_akechi_breakthrough_prediction"),
        (169, "formal_two_flank_strategy"),
        (170, "formal_encirclement_assessment"),
        (171, "confident_acceptance"),
        (172, "rousing_avenging_command"),
        (173, "commanding_tennozan_assignment"),
        (174, "commanding_center_defense"),
        (175, "desperate_hideyoshi_attack"),
        (176, "scenario_defeat_objective"),
        (177, "scenario_defeat_objective_success"),
        (178, "scenario_defeat_objective_failure"),
        (179, "scenario_tennozan_capture_objective"),
        (180, "scenario_tennozan_capture_success"),
        (181, "scenario_tennozan_capture_failure"),
    ),
    terminology_policy=(
        ("Mitsuhide", "미쓰히데"),
        ("Akechi", "아케치"),
        ("Hashiba Clan", "하시바 가문"),
        ("Hideyoshi", "히데요시"),
        ("Tennōzan", "덴노잔"),
        ("rebellion", "모반"),
        ("traitor", "역적"),
        ("forced march", "강행군"),
        ("main force", "본대"),
        ("front breakthrough", "정면 돌파"),
        ("key point", "요충지"),
        ("capture", "탈취"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B137 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context, while "
        "the opening JP-only Akechi dialogue was reviewed from its complete "
        "assembly and adjacent Yamazaki sequence; completed Base defeat, "
        "strategic-point, battle-command and reflective rows are used only "
        "as independent semantic and terminology references because none "
        "of the twenty-eight PK records has a raw, literal or operand-"
        "masked Base match; Mitsuhide, Akechi, Hashiba, Hideyoshi and "
        "Tennōzan retain established historical project forms, while "
        "forced march, rebellion, traitor, main force, frontal "
        "breakthrough, key point and capture terminology is normalized; "
        "objective labels remain concise while dialogue preserves each "
        "commanding, formal, confident, despairing, triumphant, desperate "
        "or reflective register; colour tags, inline person, force and "
        "location tokens, protected spaces, line breaks, particles, "
        "punctuation, terminators, complete record arity, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1416 and S1417 decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=12,
    pins={
        "expected_queue_universe_sha256":
        "AA6B64E39166A50CF7D456140DFC053DCB88E80C33120BAFFADE06C49C921E0D",
        "expected_queue_slice_sha256":
        "385F785BCF561FF366897FF1B0A6E15679422EDE0D028C6B5374E73C35BEA19A",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "385F785BCF561FF366897FF1B0A6E15679422EDE0D028C6B5374E73C35BEA19A",
        "expected_source_target_sha256":
        "0E7C0AA2D69796858426C377F4A703F99A87FDC936F9296CB60EA95D52541FEA",
        "expected_current_target_sha256":
        "912949DAAC7D12322B87C3DC41EFBB6393CCD2511867228F519E78258CA51545",
        "expected_context_corpus_sha256":
        "B542EDCA0F2044E694BE2A20C0C8015569380470245117D24C4B915CE072C772",
        "expected_gap_contract_sha256":
        "80DA5932942E335CA7C873EA696BF71C9D5E7414950957BAE667CA4942EA9ACA",
        "expected_boundary_sha256":
        "C7D248F83847EAF624251B7375101E15853817941358FAB5021898A563A88C60",
        "expected_runtime_control_sha256":
        "00E9829FEC0CCD107B1558AF0A9C6DD6C9A025FEA25DDD958E918B779D77450E",
        "expected_base_search_sha256":
        "E3C26E8A95B8007F46011DF511AAD64F842E7BA6E6569155E49A40A52AB8450C",
        "expected_complete_assembly_sha256":
        "B7969683996FDF9027D6DF1F9363205F6128125F218E7D325B95A514F2DC32F2",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "20DCEFF52693007DD5CBA9C219D5DB0701937E96F2B75D08862CBEB123B4AFCC",
        "expected_terminology_policy_sha256":
        "36353E80C3B3BE48342DC435A8B623297643841E2D5C444CE1E9B1841F7F6C61",
        "expected_translation_policy_sha256":
        "46C6C0E00BDC5DA5451B53B3B6C704CD1A0964E1C3C9828AF3ACE94B1077FCFB",
        "expected_candidate_sha256":
        "5733C68FC67F0B07E508EECFE592440A1CABABD8DF6EECC4174DAA249918C2EC",
        "expected_combined_slice_candidate_sha256":
        "5733C68FC67F0B07E508EECFE592440A1CABABD8DF6EECC4174DAA249918C2EC",
        "expected_combined_changed_literal_count": 12,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B137_S1415",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B137_S1415.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B137_S1416.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B137_S1417.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B137",
    "queue_row_count": 95,
    "queue_visible_count": 199,
    "queue_first": "17:154:0",
    "queue_last": "17:248:2",
})


def base_and_assembly_evidence_with_boundary(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard the main records plus the split right-boundary record."""
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
    key = (17, 181)
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
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[181]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1415 Base context drifted: "
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
            f"segment 1415 neighbor companion drifted: {neighbor_coordinate}"
        )
    assembled = (
        TRANSLATIONS["17:181:0"],
        TRANSLATIONS["17:181:1"],
        expected,
    )
    if (
        len(source_literals) != EXPECTED_ARITY[181]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[181]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[181]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[181]
        or assembled != ("덴노잔", "을 탈취하라", " 실패")
    ):
        raise RuntimeError("segment 1415 boundary assembly drifted")
    return (
        tuple(base_evidence) + ((
            181,
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
            181,
            (
                "segment_manual_multilingual",
                "segment_manual_multilingual",
                "optional_next_segment_manual_companion",
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
