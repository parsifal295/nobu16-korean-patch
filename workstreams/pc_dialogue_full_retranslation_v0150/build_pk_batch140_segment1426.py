#!/usr/bin/env python3
"""Build source-redacted PK B140 segment 1426 residual decisions."""

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

TARGET_RECORD_IDS = tuple(range(502, 534))
MAIN_RECORD_IDS = tuple(
    record_id for record_id in TARGET_RECORD_IDS if record_id != 510
)
TARGET_COORDINATES = (
    "17:502:0", "17:502:1", "17:502:2",
    "17:503:0", "17:503:1",
    "17:504:0", "17:505:0", "17:506:0",
    "17:507:0", "17:507:1", "17:507:2", "17:507:3",
    "17:508:0", "17:509:0", "17:510:1",
    "17:511:0", "17:511:1",
    "17:512:0", "17:512:1", "17:512:2",
    "17:513:0", "17:513:1", "17:513:2",
    "17:514:0", "17:515:0", "17:516:0",
    "17:517:0", "17:517:1",
    "17:518:0", "17:518:1",
    "17:519:0", "17:519:1",
    "17:520:0", "17:520:1", "17:520:2",
    "17:521:0", "17:521:1",
    "17:522:0", "17:522:1", "17:522:2",
    "17:523:0",
    "17:524:0", "17:524:1",
    "17:525:0", "17:525:1", "17:525:2", "17:525:3",
    "17:526:0", "17:526:1", "17:526:2",
    "17:527:0", "17:527:1",
    "17:528:0", "17:528:1",
    "17:529:0", "17:529:1",
    "17:530:0", "17:530:1",
    "17:531:0", "17:531:1", "17:531:2",
    "17:532:0", "17:532:1", "17:532:2",
    "17:533:0",
)
MAIN_TARGET_COORDINATES = tuple(
    coordinate
    for coordinate in TARGET_COORDINATES
    if not coordinate.startswith("17:510:")
)
TRANSLATIONS = {
    "17:502:0": "누가 간신이라는 것이냐……!\n네가 바라는 것은 ",
    "17:502:1": "도쿠가와",
    "17:502:2": "의 천하일 터!",
    "17:503:0": "아와노카미",
    "17:503:1": "여……\n끝까지 방해하는구나?",
    "17:504:0": (
        "우리가 오히려 너구리 사냥에 질렸다……\n"
        "뭐, 이번에도 사냥감이 되어 줘야겠지만"
    ),
    "17:505:0": "!\n약속과 다르지 않느냐!!",
    "17:506:0": (
        "글쎄, 약속이라니 무슨 말인가?\n"
        "약한 군의 편이 되겠다는 말은 한 적이 없다"
    ),
    "17:507:0": "불전의 약정은 어찌한 것이냐!\u3000",
    "17:507:1": "!\n",
    "17:507:2": "모리",
    "17:507:3": "가문이 무너져도 좋다는 것이냐!?",
    "17:508:0": (
        "약정……? 무슨 말인지……\n"
        "근거도 없는 말을 하시니 곤란하군요……"
    ),
    "17:509:0": (
        "약정……? 무슨 말인지……\n"
        "근거도 없는 말을 하시니 곤란하군요……"
    ),
    "17:510:1": "\u3000동군",
    "17:511:0": "이 앞을 지나가고 싶다면\n이",
    "17:511:1": "의 진을 뚫어 보아라!",
    "17:512:0": "덤벼라!\n이 ",
    "17:512:1": "비젠 재상",
    "17:512:2": "이 단숨에 쓸어 주마!",
    "17:513:0": "이 ",
    "17:513:1": "고니시 셋쓰노카미",
    "17:513:2": "가\n무예도 뒤지지 않음을 천하에 보여 주마!",
    "17:514:0": "역시 적 본진의 수비는 견고한가……\n먼저 평지의 적부터 처리하라!",
    "17:515:0": "움직이지 않을 생각이었지만……\n도전한다면 받아 주마!",
    "17:516:0": "대군이 무슨 대수냐!\n모두 돌격하라!",
    "17:517:0": "적은 그",
    "17:517:1": "인가!\n상대로 부족함이 없다!",
    "17:518:0": "전진하라! 전진하라!\n이",
    "17:518:1": "에게 뒤처지지 마라!",
    "17:519:0": "도쿠가와",
    "17:519:1": "의 아카조나에인가……\n내가 이곳에서 막겠다!",
    "17:520:0": "그",
    "17:520:1": "사콘",
    "17:520:2": (
        "님과 겨루게 되어 송구하나……\n"
        "아내의 원수와 그 신하들을 살려 둘 수는 없다"
    ),
    "17:521:0": "호소카와",
    "17:521:1": (
        "의 장남은 성질이 급하다고 들었는데\n"
        "제법 침착한 용병술이군"
    ),
    "17:522:0": "주군, 왜 오사카를 떠나셨습니까……\n이제 와서",
    "17:522:1": "모리",
    "17:522:2": "가 천하를 바라는 겁니까?",
    "17:523:0": "그래도 총대장이니까\n모두를 격려해야겠다고 생각했을 뿐이다",
    "17:524:0": (
        "소나기……실로 하늘의 도움이다\n"
        "비가 그치기 전에 적 본진을 습격해\n내 손으로"
    ),
    "17:524:1": "를 쓰러뜨리겠다",
    "17:525:0": "오케하자마산",
    "17:525:1": "에서 쉬고 있는 적군을 확인했습니다!\n……",
    "17:525:2": "이마가와",
    "17:525:3": "군의 본진인 듯합니다!",
    "17:526:0": "앞선 보고대로입니다\n적은 날이 개기를 기다려",
    "17:526:1": "나루미",
    "17:526:2": "로 진군할 생각인 듯합니다",
    "17:527:0": "가소롭구나,",
    "17:527:1": "……\n기회만 기다리는 자에게 하늘은 편들지 않는다",
    "17:528:0": "이제 비바람을 틈타 적 본진을 습격한다\n노릴 것은",
    "17:528:1": "의 목뿐이다!",
    "17:529:0": "부대로",
    "17:529:1": "부대를 기습하라",
    "17:530:0": "부대로",
    "17:530:1": "부대를 기습하라",
    "17:531:0": "부대로",
    "17:531:1": "부대를 기습하라",
    "17:531:2": " 성공",
    "17:532:0": "부대로",
    "17:532:1": "부대를 기습하라",
    "17:532:2": " 실패",
    "17:533:0": "과연 세 나라를 거느리는 수장이군……\n수비도 소홀히 하지 않았나",
}
EXPECTED_ARITY = {
    502: 3, 503: 2, 504: 1, 505: 1, 506: 1, 507: 4,
    508: 1, 509: 1, 510: 3, 511: 2, 512: 3, 513: 3,
    514: 1, 515: 1, 516: 1, 517: 2, 518: 2, 519: 2,
    520: 3, 521: 2, 522: 3, 523: 1, 524: 2, 525: 4,
    526: 3, 527: 2, 528: 2, 529: 2, 530: 2, 531: 3,
    532: 3, 533: 1,
}
SEMANTIC_BASE_CONTEXT = {
    **{record_id: ("9:1006:0",) for record_id in range(502, 524)},
    **{record_id: ("9:3031:0",) for record_id in range(524, 534)},
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    505: ((), ("024735",)),
    507: ((), ("024735",)),
    510: ((), ("024633", "0247331B4333")),
    511: ((), ("024635",)),
    517: ((), ("024733",)),
    518: ((), ("024635",)),
    522: ((), ("024735",)),
    524: ((), ("024833",)),
    527: ((), ("024835",)),
    528: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1426,
    queue_start=134,
    queue_stop=200,
    slice_first="17:502:0",
    slice_last="17:533:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=("17:510:2",),
    prefill_companion_donor={"17:510:2": "15:482:1"},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple((17, record_id) for record_id in range(470, 570)),
    speaker_style=tuple(
        (record_id, "historical_battle_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Tokugawa", "도쿠가와"),
        ("Mori", "모리"),
        ("nonaggression pact", "불전의 약정"),
        ("eastern army", "동군"),
        ("main camp", "본진"),
        ("red cavalry", "아카조나에"),
        ("Okehazama mountain", "오케하자마산"),
        ("matchlock unit", "철포대"),
        ("ambush", "기습"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B140 queue coordinates one hundred thirty-four "
        "through one hundred ninety-nine and the single approved Base "
        "prefill; pristine PK source is authoritative, all available "
        "multilingual same-record fragments were reviewed as auxiliary "
        "context, and source-only records were reviewed from complete "
        "assemblies and adjacent historical battle sequence; completed Base "
        "battle and command rows are semantic context only and never "
        "contribute runtime or VM state; the split defection record is "
        "assembled from one hidden current companion, this segment's eastern-"
        "army fragment and the approved Base-prefilled defection fragment; "
        "Tokugawa, Mori, the nonaggression pact, eastern army, main camp, red "
        "cavalry, Okehazama mountain, matchlock unit and ambush terminology "
        "retain established project wording; tags, tokens, protected "
        "whitespace, line breaks, punctuation, terminators, arity, pins, "
        "reverse overlays, reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256": "46AC009F2442000B77B8824FDBBB676398B300A99602408336C2C6021E105D13",
        "expected_queue_slice_sha256": "647C21DA57304D893FAEA159D7FC063A558DF1FCE5F8D0856F5A914E15F72534",
        "expected_prefilled_coordinate_sha256": "42B38844A6A889525E551D88031437864123CADF2F5AFD545C649A8B965E2210",
        "expected_prefill_slice_context_sha256": "3EC2306800A35151310247C645E64BC22567E7C0F63D3C6AA537CAF6FC2E916E",
        "expected_target_coordinate_sha256": "F2940775D527BF60633B88CF24420874E7E10223C090DBD2C658F35C0BB37653",
        "expected_source_target_sha256": "A30E0B18101250972193163566804B39CDF9C744D0EE098BF43B2BC38AE445A6",
        "expected_current_target_sha256": "EFC08847643E4712A677E248C3E7777AE912869619F24F47215B1E7F02776A3F",
        "expected_context_corpus_sha256": "89E1A9C78704BA431F3E6FD4BAB11F6EA787C631BC35BC474D081F79EE23DBB2",
        "expected_gap_contract_sha256": "2FFD8979B5EB891EA209004C7B255CFDCBB448EDDEF39DD2CBC49B9FAD975C44",
        "expected_boundary_sha256": "E52F1498CA9C49F0B56A51DCFA3892D0EA60AA39DE5DE5D302137BD7E393D938",
        "expected_runtime_control_sha256": "6AC5F597F6C023C99200894DFA2637CAA079343B674B8BA1936DACA3F497531D",
        "expected_base_search_sha256": "D26BF03543EA1C8DF1ACAD7298AB048F0D28DBAD6B9FE3AFFF899984A493E99C",
        "expected_complete_assembly_sha256": "4D43E0A036B80FFB18AE72522AE581C26A64467921FC87BADC5F1EC9C2894C1D",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "22202036B902BB086FB54481838981B0F02463BB856D081172E61C61E33F46C3",
        "expected_terminology_policy_sha256": "55388B1929159E18C558F0574EC024BC8EA2B8285412E65FCD58E4E9AC6C76C6",
        "expected_translation_policy_sha256": "FB17F9B1C713A9DDE5677D6A06C7401C1938087A5BCC3C3169D4448241DE00D7",
        "expected_candidate_sha256": "2A91DDBA06B2322EE7FB29D137A9BCB7EEFC42F47817A07F539B40D7423EACC8",
        "expected_combined_slice_candidate_sha256": "1166BAEB0579799557F228D9E06CC2B968D8DA737168B54908292F8B00883B55",
        "expected_combined_changed_literal_count": 17,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B140_S1426",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B140_S1426.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B140_S1424.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B140_S1425.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B140",
    "queue_row_count": 97,
    "queue_visible_count": 200,
    "queue_first": "17:437:0",
    "queue_last": "17:533:0",
})


def base_and_assembly_evidence_with_space_companion(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard ordinary records plus record 510's hidden ideographic space."""
    original_globals = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved = {
        name: original_globals[name]
        for name in (
            "TARGET_RECORD_IDS",
            "TARGET_COORDINATES",
            "PREFILL_COMPANION_COORDINATES",
            "PREFILL_COMPANION_DONOR",
            "HIDDEN_CURRENT_COMPANION_COORDINATES",
        )
    }
    original_globals["TARGET_RECORD_IDS"] = MAIN_RECORD_IDS
    original_globals["TARGET_COORDINATES"] = MAIN_TARGET_COORDINATES
    original_globals["PREFILL_COMPANION_COORDINATES"] = ()
    original_globals["PREFILL_COMPANION_DONOR"] = {}
    original_globals["HIDDEN_CURRENT_COMPANION_COORDINATES"] = ()
    try:
        base_evidence, assembly_evidence = (
            _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(
                prepared,
                records_by_label,
            )
        )
    finally:
        for name, value in saved.items():
            original_globals[name] = value

    key = (17, 510)
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_literals = COMMON.literal_texts(records_by_label["jp"], key)
    current_literals = COMMON.literal_texts(records_by_label["current"], key)
    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
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
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    references: list[tuple[Any, ...]] = []
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[510]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                f"segment 1426 Base context drifted: {donor_coordinate}"
            )
        references.append((
            donor_coordinate,
            str(donor["translation"]),
            str(donor["runtime_review"]),
        ))
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    prefill = prefill_rows.get("17:510:2")
    if (
        prefill is None
        or prefill.get("translation") != "에 귀순"
        or prefill.get("semantic_review") != "approved"
        or prefill.get("runtime_review") != "pending"
        or prefill["base_exact_reuse_prefill"]["base_coordinate"]
        != "15:482:1"
        or prefill["base_exact_reuse_prefill"][
            "runtime_promotion_authorized"
        ]
        is not False
    ):
        raise RuntimeError("segment 1426 prefill companion drifted")
    assembled = (
        source_literals[0],
        TRANSLATIONS["17:510:1"],
        str(prefill["translation"]),
    )
    if (
        len(source_literals) != EXPECTED_ARITY[510]
        or source_literals[0] != "\u3000"
        or current_literals[0] != source_literals[0]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[510]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[510]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[510]
        or assembled != ("\u3000", "\u3000동군", "에 귀순")
    ):
        raise RuntimeError("segment 1426 record 510 assembly drifted")
    return (
        tuple(base_evidence) + ((
            510,
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
            510,
            (
                "source_identical_hidden_ideographic_space",
                "segment_manual_multilingual",
                "base_exact_prefill_runtime_pending",
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
        base_and_assembly_evidence_with_space_companion
    )
    COMMON.CORE.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_space_companion
    )


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
