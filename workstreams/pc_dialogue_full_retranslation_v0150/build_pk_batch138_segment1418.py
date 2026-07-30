#!/usr/bin/env python3
"""Build source-redacted PK B138 segment 1418 residual decisions."""

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
    "17:249:0", "17:249:1",
    "17:250:0", "17:250:1", "17:250:2", "17:250:3",
    "17:251:0", "17:251:1", "17:251:2",
    "17:252:0", "17:252:1",
    "17:253:0",
    "17:254:0",
    "17:255:0", "17:255:1", "17:255:2",
    "17:256:0",
    "17:257:0",
    "17:258:0", "17:258:1",
    "17:259:0", "17:259:1", "17:259:2",
    "17:260:0", "17:260:1",
    "17:261:0", "17:261:1", "17:261:2",
    "17:262:0", "17:262:1", "17:262:2",
    "17:264:0",
    "17:265:0", "17:265:1",
    "17:266:0", "17:266:1", "17:266:2",
    "17:267:0",
    "17:268:0", "17:268:1",
    "17:269:0", "17:269:1", "17:269:2",
    "17:270:0", "17:270:1", "17:270:2",
    "17:271:0",
    "17:272:0", "17:272:1", "17:272:2",
    "17:273:0",
    "17:274:0", "17:274:1", "17:274:2",
    "17:275:0",
    "17:276:0", "17:276:1", "17:276:2", "17:276:3",
    "17:277:0", "17:277:1", "17:277:2", "17:277:3",
    "17:278:0", "17:278:1",
    "17:279:0", "17:279:1",
)

TRANSLATIONS = {
    "17:249:0": "히데요리",
    "17:249:1": "님!\n설마 정말 와 주실 줄은……",
    "17:250:0": "미쓰나리",
    "17:250:1": "가 애쓰고 있다고 들어서 말이지\n",
    "17:250:2": "적군",
    "17:250:3": "에도 낯익은 자가 있는 모양이군",
    "17:251:0": "저 깃발은",
    "17:251:1": "히데요리",
    "17:251:2": "님!? 설마 와 계신 것인가!?",
    "17:252:0": "히데요리",
    "17:252:1": (
        "님을 적으로 삼아 싸울 수는 없다!\n"
        "우리는 철수한다!"
    ),
    "17:253:0": "우리도 적당히 싸우다 서둘러 철수하자",
    "17:254:0": (
        "모두가 힘쓴 덕에 전황이 우리 쪽으로 기울었다!\n"
        "잘했다!"
    ),
    "17:255:0": "이번 싸움은,",
    "17:255:1": "도쿠가와",
    "17:255:2": (
        "의 승리로 결판났군……\n"
        "아니, 아직 모르는가……?"
    ),
    "17:256:0": (
        "군은 역시 눈치만 보는군……\n"
        "계속 밀리면 배신할지도 모른다!"
    ),
    "17:257:0": "모두, 밀리지 마라!\n지금이 버텨야 할 때다!",
    "17:258:0": "요충지 ",
    "17:258:1": "하나 정도로 전세가 기울다니……",
    "17:259:0": (
        "군사님께서 말씀하셨다!\n"
        "기세를 올려 "
    ),
    "17:259:1": "요충지",
    "17:259:2": "를 탈환하자!",
    "17:260:0": "여기까지는 순조롭지만……\n",
    "17:260:1": "는 아직 움직이지 않는가?",
    "17:261:0": "의 깃발은 아직",
    "17:261:1": "마쓰오산",
    "17:261:2": (
        "에 있습니다\n"
        "서군으로도 동군으로도 움직이지 않았습니다"
    ),
    "17:262:0": "……본대를 앞으로 내보낸다\n조금 ",
    "17:262:1": "긴고",
    "17:262:2": "를 겁줘 보자",
    "17:264:0": "아버님, 늦었지만 도착했습니다",
    "17:265:0": "히데타다",
    "17:265:1": "가 도착했나!\n든든하구나!",
    "17:266:0": "예\n하지만",
    "17:266:1": "사나다",
    "17:266:2": "도 이 싸움에 참전할 듯합니다……",
    "17:267:0": (
        "어떻게든 싸움에 늦지 않았군!\n"
        "우리가 전장을 휘젓겠다!"
    ),
    "17:268:0": "마사유키",
    "17:268:1": (
        "님! 살아 계셨습니까!\n"
        "이보다 든든한 원군은 없습니다!"
    ),
    "17:269:0": "전선의 ",
    "17:269:1": "요충지",
    "17:269:2": "를 빼앗겼나……",
    "17:270:0": "전황이",
    "17:270:1": "쪽으로 기울기 시작했군\n우리의 적은",
    "17:270:2": "이다! 진군하라!",
    "17:271:0": "가 움직였나! 우리도 호응하자!",
    "17:272:0": "녀석,",
    "17:272:1": "의 편에 서다니……\n우리 힘만으로",
    "17:272:2": "를 쓰러뜨릴 수밖에 없다……",
    "17:273:0": "이쯤이면 되겠군……\n철포대, 겨눠라!",
    "17:274:0": "주군!　",
    "17:274:1": "내대신",
    "17:274:2": "님의 진에서\n철포 사격을 받고 있습니다!",
    "17:275:0": (
        "더 지켜보는 것은\n"
        "용납하지 않겠다는 뜻인가……"
    ),
    "17:276:0": "좋다,",
    "17:276:1": "내대신",
    "17:276:2": "의 편에 서겠다!\n적은 간신",
    "17:276:3": "이다! 산을 내려가라!",
    "17:277:0": "전향이 성사됐다!\n",
    "17:277:1": "부대에 맞춰,",
    "17:277:2": "오타니 교부",
    "17:277:3": "를 쳐라!",
    "17:278:0": "전향이 성사됐다!\n전진하라!　",
    "17:278:1": "를 쳐라!",
    "17:279:0": "여기까지인가…\n미안하다",
    "17:279:1": ", 지부",
}

TARGET_RECORD_IDS = (
    249, 250, 251, 252, 253, 254, 255, 256, 257, 258,
    259, 260, 261, 262, 264, 265, 266, 267, 268, 269,
    270, 271, 272, 273, 274, 275, 276, 277, 278, 279,
)
MAIN_RECORD_IDS = TARGET_RECORD_IDS[:-1]
MAIN_TARGET_COORDINATES = TARGET_COORDINATES[:-2]
EXPECTED_ARITY = {
    249: 2, 250: 4, 251: 3, 252: 2, 253: 1, 254: 1,
    255: 3, 256: 1, 257: 1, 258: 2, 259: 3, 260: 2,
    261: 3, 262: 3, 264: 1, 265: 2, 266: 3, 267: 1,
    268: 2, 269: 3, 270: 3, 271: 1, 272: 3, 273: 1,
    274: 3, 275: 1, 276: 4, 277: 4, 278: 2, 279: 3,
}
NEIGHBOR_COMPANION_TRANSLATIONS = {
    "17:279:2": "… 네게 승리를 안겨 주지 못했구나…"
}

STRATEGIC_POINT_RECORD_IDS = (258, 259, 269)
COMMAND_RECORD_IDS = (
    253, 254, 257, 267, 270, 271, 273, 274, 276, 277, 278,
)
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ("9:2842:0",)
        for record_id in STRATEGIC_POINT_RECORD_IDS
    },
    **{record_id: ("9:3792:0",) for record_id in COMMAND_RECORD_IDS},
    **{
        record_id: ("9:1006:0",)
        for record_id in TARGET_RECORD_IDS
        if (
            record_id not in STRATEGIC_POINT_RECORD_IDS
            and record_id not in COMMAND_RECORD_IDS
        )
    },
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    256: ((), ("024834",)),
    260: ((), ("024833",)),
    261: ((), ("024834",)),
    270: ((), ("024835", "024935")),
    271: ((), ("024835",)),
    272: ((), ("024835", "024935", "024935")),
    276: ((), ("024833",)),
    277: ((), ("024834",)),
    278: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1418,
    queue_start=0,
    queue_stop=67,
    slice_first="17:249:0",
    slice_last="17:279:1",
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
        (17, record_id) for record_id in range(210, 325)
    ),
    speaker_style=(
        (249, "astonished_greeting_to_hideyori"),
        (250, "hideyori_response_about_mitsunari"),
        (251, "astonished_hideyori_banner_recognition"),
        (252, "refusal_to_fight_hideyori"),
        (253, "opportunistic_withdrawal_plan"),
        (254, "commanding_battlefield_praise"),
        (255, "cautious_tokugawa_victory_assessment"),
        (256, "warning_about_fence_sitter"),
        (257, "rousing_hold_the_line_command"),
        (258, "astonished_strategic_point_loss"),
        (259, "rousing_strategic_point_recapture"),
        (260, "impatient_fence_sitter_observation"),
        (261, "formal_matsuo_banner_report"),
        (262, "ieyasu_pressure_on_kingo"),
        (264, "formal_son_arrival_report"),
        (265, "relieved_greeting_to_hidetada"),
        (266, "formal_sanada_warning"),
        (267, "confident_battlefield_arrival"),
        (268, "relieved_greeting_to_masayuki"),
        (269, "concerned_front_strategic_point_loss"),
        (270, "commanding_alignment_advance"),
        (271, "commanding_response_to_movement"),
        (272, "angry_response_to_defection"),
        (273, "commanding_matchlock_volley"),
        (274, "urgent_naifu_gunfire_report"),
        (275, "pressured_fence_sitter_reflection"),
        (276, "decisive_defection_to_naifu"),
        (277, "commanding_otani_attack_after_defection"),
        (278, "commanding_advance_after_defection"),
        (279, "dying_apology_to_jibu"),
    ),
    terminology_policy=(
        ("Hideyori", "히데요리"),
        ("Mitsunari", "미쓰나리"),
        ("Tokugawa", "도쿠가와"),
        ("Hidetada", "히데타다"),
        ("Sanada", "사나다"),
        ("Masayuki", "마사유키"),
        ("Matsuoyama", "마쓰오산"),
        ("Kingo", "긴고"),
        ("Naifu", "내대신"),
        ("Ōtani Gyōbu", "오타니 교부"),
        ("Jibu", "지부"),
        ("strategic point", "요충지"),
        ("defection", "전향"),
        ("matchlock unit", "철포대"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B138 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context, while "
        "JP-only Hideyori and early Sekigahara dialogue was reviewed from "
        "complete assemblies and its adjacent scenario sequence; completed "
        "Base strategic-point, battle-command and officer rows are used "
        "only as independent semantic and terminology references because "
        "none of the thirty PK records has a raw, literal or operand-masked "
        "Base match; Hideyori, Mitsunari, Tokugawa, Hidetada, Sanada, "
        "Masayuki, Matsuoyama, Kingo, Naifu, Otani Gyobu and Jibu retain "
        "established historical project forms, while strategic point, "
        "defection and matchlock terminology is normalized; dialogue "
        "preserves each formal, relieved, opportunistic, cautious, rousing, "
        "impatient, pressured, decisive, angry or dying register; colour "
        "tags, inline person, force, role and location tokens, protected "
        "spaces, line breaks, particles, punctuation, terminators, complete "
        "record arity, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, reciprocal S1419 and S1420 "
        "decisions and Steam read-only state are guarded; record 279 alone "
        "uses a manually audited punctuation transfer across the Jibu "
        "runtime token so the complete Korean sentence reads naturally"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256":
        "4EDC588F91DEC58F97ACA4C16FF4150DCECBB90ED1372150DD2021A8EC01B24E",
        "expected_queue_slice_sha256":
        "51943B561BA99D294E8FF931BF8DABF17CAA9975EA219C7B810007FB70B44956",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "51943B561BA99D294E8FF931BF8DABF17CAA9975EA219C7B810007FB70B44956",
        "expected_source_target_sha256":
        "755C9877D65A237DC557BBA186BFE6B6517A106010F4263BC4E4EEAF5E37C07D",
        "expected_current_target_sha256":
        "07C153112F818F508A7C304DA76079092F175D882046CF37D08BA8078B453BDA",
        "expected_context_corpus_sha256":
        "09CA07A2EEB63A33AAFF03821C355C81D5F91E090F8817DF174B573C93FC4623",
        "expected_gap_contract_sha256":
        "CA763933E2B850CD16EC485D018E984FEF7D690AE5FF7BBD1E5EFA3F9F5A0F0A",
        "expected_boundary_sha256":
        "556CC1C537895A77458841F1F4417320B7E783D2804B28B2687413B824FE9852",
        "expected_runtime_control_sha256":
        "A5084AEC4911654EBEB8A13CA6FC6A3C9335F4272E308F70C0F8C5BEAC1AF971",
        "expected_base_search_sha256":
        "A713B9DF72C783156FF6F4DA5655986B5A9315B8F6BEC90B499FCCBC96F3B07F",
        "expected_complete_assembly_sha256":
        "B9B5D095937C86216AEA5C18E2CC5041391BAB19140393ED9A32F4A7457BF0BC",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "A10AC028E66C4B901CCF3EA1653562D7D55E7E3DE665AF1DBC212A68CC287D0F",
        "expected_terminology_policy_sha256":
        "E1BB369CFB7C5AD748B8E7AE856F3FF0EA0E8A7470DAF50BEBC5F74BD3BFFD37",
        "expected_translation_policy_sha256":
        "5680E38EB21BE8E1B7EDA6854E2680D78262F2DABBD8E017864F7A3FE9A0664F",
        "expected_candidate_sha256":
        "0DA5D9A73C5CBD6A3AED0981E3BC0B1074F8365FF89E34A56B64232A8E5E5354",
        "expected_combined_slice_candidate_sha256":
        "0DA5D9A73C5CBD6A3AED0981E3BC0B1074F8365FF89E34A56B64232A8E5E5354",
        "expected_combined_changed_literal_count": 16,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B138_S1418",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B138_S1418.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B138_S1419.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B138_S1420.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B138",
    "queue_row_count": 98,
    "queue_visible_count": 200,
    "queue_first": "17:249:0",
    "queue_last": "17:346:1",
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
    key = (17, 279)
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
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[279]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1418 Base context drifted: "
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
            f"segment 1418 neighbor companion drifted: {neighbor_coordinate}"
        )
    assembled = (
        TRANSLATIONS["17:279:0"],
        TRANSLATIONS["17:279:1"],
        expected,
    )
    if (
        len(source_literals) != EXPECTED_ARITY[279]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[279]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[279]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[279]
        or assembled != (
            "여기까지인가…\n미안하다",
            ", 지부",
            "… 네게 승리를 안겨 주지 못했구나…",
        )
    ):
        raise RuntimeError("segment 1418 boundary assembly drifted")
    return (
        tuple(base_evidence) + ((
            279,
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
            279,
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
