#!/usr/bin/env python3
"""Build source-redacted PK B142 segment 1431 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_READ_JSONL = COMMON.BASE.read_jsonl
_ORIGINAL_BASE_EVIDENCE = COMMON.BASE.base_and_assembly_evidence

TARGET_COORDINATES = (
    "17:661:1", "17:661:2", "17:662:0", "17:662:1",
    "17:663:0", "17:664:0", "17:664:1", "17:664:2",
    "17:664:3", "17:665:0", "17:666:0", "17:667:1",
    "17:667:2", "17:667:3", "17:667:4", "17:667:5",
    "17:668:0", "17:669:0", "17:670:0",
    "17:670:1", "17:671:0", "17:672:0", "17:673:0",
    "17:673:1", "17:674:0", "17:676:0", "17:677:0",
    "17:678:0", "17:678:1", "17:679:0", "17:680:0",
    "17:680:1", "17:680:2", "17:680:3", "17:680:4",
    "17:681:0", "17:682:0", "17:682:1", "17:682:2",
    "17:682:3", "17:683:0", "17:683:1", "17:684:0",
    "17:684:1", "17:685:0", "17:685:1", "17:685:2",
    "17:685:3", "17:686:0", "17:687:0", "17:688:0",
    "17:689:0", "17:690:0", "17:691:0", "17:691:1",
    "17:691:2", "17:692:0", "17:692:1", "17:693:0",
    "17:693:1", "17:693:2", "17:694:0", "17:694:1",
    "17:695:0", "17:695:1", "17:696:0",
)
TRANSLATIONS = {
    "17:661:1": "의 요충지를 확보하라",
    "17:661:2": " 실패",
    "17:662:0": "예상대로—",
    "17:662:1": "는 움직일 태세가 아니다\n이제 우리 손에 달렸다…",
    "17:663:0": "님께서 출진하시도록\n이길 싸움이라 여기게 만든다… 그렇지?",
    "17:664:0": "그리하면",
    "17:664:1": "도 허락할 터\n",
    "17:664:2": "님과",
    "17:664:3": "에게도 전갈을 부탁해 두었다",
    "17:665:0": "적은 많지만 전쟁을 모르는 자들뿐…\n우리의 승기는 거기에 있다",
    "17:666:0": "마지막 싸움이라며 기세를 올린 자도 있겠지\n우선 적의 칼끝을 끌어당겨… 꺾는다",
    "17:667:1": "혼다 헤이하치로 다다카쓰",
    "17:667:2": "의 아들,",
    "17:667:3": "!\n",
    "17:667:4": "의,",
    "17:667:5": "의 무용을 똑똑히 보아라!",
    "17:668:0": "훌륭한 기백이로군\n선봉에 어울리는 용장이지만…",
    "17:669:0": "적은 우리를 두려워해 물러나고 있다!\n이대로 밀어붙여 무너뜨려라!",
    "17:670:0": "기다려라—",
    "17:670:1": "!\n대장이 너무 앞서 나갔다!",
    "17:671:0": "주위를 살피는 힘은 부족한 모양이군\n…철포대, 쏴라!",
    "17:672:0": "뭐라고, 복병!?\n이깟 철포 따위에… 으악!",
    "17:673:0": "이런 유인책에 넘어가서는\n이",
    "17:673:1": "의 목을 벨 수 없다!",
    "17:674:0": "이 상처로는… 이제 술도 못 마시겠군…\n하하… 역시 술은… 삼가야… 했나…",
    "17:676:0": "부대의 아군이 무너져 진형이…!\n깊이 들어가지 마라, 일단 물러나라!",
    "17:677:0": "이미 늦었다!\n좌우에서도 공격하라!",
    "17:678:0": "주군! 설마",
    "17:678:1": "에 이어…\n큭, 병사들의 혼란을 막을 수 없다…!",
    "17:679:0": "일행의 선봉이 쓰러졌나…\n하지만 이 정도로 대세는 바뀌지 않는다!",
    "17:680:0": "주군, 큰일입니다!\n적의",
    "17:680:1": "사나다",
    "17:680:2": "부대와",
    "17:680:3": "오타니",
    "17:680:4": "부대가 보이지 않습니다",
    "17:681:0": "뭐라고…! 설마 배후에서…\n에잇, 무슨 수를 써서라도 찾아내라",
    "17:682:0": "그럴 필요는 없습니다—",
    "17:682:1": "대어소",
    "17:682:2": "님!\n우리",
    "17:682:3": ", 여기 있소!",
    "17:683:0": "우리는 결사대가 되어 돌격한다!\n노리는 것은 오직 하나—",
    "17:683:1": "의 목이다!",
    "17:684:0": "큭—",
    "17:684:1": "는 무엇을 하는 게냐!\n모두 진정하라! 어서 맞서 싸워라!",
    "17:685:0": "음—",
    "17:685:1": "놈은 어디로 갔지?\n설마",
    "17:685:2": "오사카성",
    "17:685:3": "으로 도망쳤나!",
    "17:686:0": "그저 놓친 것뿐인가…\n…음…?",
    "17:687:0": "저건… 아군이 아니군",
    "17:688:0": "흥, 그 인원으로는 아무것도 못 할 테지\n여기서는 전진해 퇴로를 끊어야 한다!",
    "17:689:0": "그럴지도 모르나… 불길한 예감이 든다\n여기서 추격해야 할까?",
    "17:690:0": "부대와는 따로 움직이겠다!\n마지막 싸움에서 후회를 남기고 싶지 않으니",
    "17:691:0": "좋아, ",
    "17:691:1": "덴노지",
    "17:691:2": "를 확보했군\n이제 적은 뜻대로 움직이지 못하겠지",
    "17:692:0": "큭, 이 무슨 실책인가…\n",
    "17:692:1": "님을 뵐 면목이 없습니다…",
    "17:693:0": "덴노지",
    "17:693:1": "를 빼앗기다니…\n이래서는",
    "17:693:2": "님의 출진이 어렵나…",
    "17:694:0": "부대와",
    "17:694:1": "부대를 격파하라",
    "17:695:0": "부대와",
    "17:695:1": "부대를 교전시키지 마라",
    "17:696:0": "사나다 유키무라",
}
TARGET_RECORD_IDS = (
    *range(661, 675),
    *range(676, 697),
)
EXPECTED_ARITY = {
    661: 3, 662: 2, 663: 1, 664: 4, 665: 1, 666: 1,
    667: 6, 668: 1, 669: 1, 670: 2, 671: 1, 672: 1,
    673: 2, 674: 1, 676: 1, 677: 1, 678: 2, 679: 1,
    680: 5, 681: 1, 682: 4, 683: 2, 684: 2, 685: 4,
    686: 1, 687: 1, 688: 1, 689: 1, 690: 1, 691: 3,
    692: 2, 693: 3, 694: 2, 695: 2, 696: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "17:661:0", "17:667:0",
    "17:696:1", "17:696:2", "17:696:3", "17:696:4",
)
PREFILL_COMPANION_DONOR = {
    "17:661:0": "neighbor:S1430",
    "17:667:0": "9:2022:0",
    "17:696:1": "neighbor:S1432",
    "17:696:2": "neighbor:S1432",
    "17:696:3": "neighbor:S1432",
    "17:696:4": "neighbor:S1432",
}
SPLIT_TRANSLATIONS = {
    "17:661:0": "덴노지",
    "17:696:1": "부대와",
    "17:696:2": "오타니 요시하루",
    "17:696:3": "부대를 격파하라(",
    "17:696:4": "/2)",
}
SYNTHETIC_ROWS = tuple({
    "coordinate": coordinate,
    "translation": translation,
    "semantic_review": "approved",
    "runtime_review": "pending",
    "base_exact_reuse_prefill": {
        "base_coordinate": PREFILL_COMPANION_DONOR[coordinate],
        "runtime_promotion_authorized": False,
    },
} for coordinate, translation in SPLIT_TRANSLATIONS.items())
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    record_id: ("9:400:0", "9:401:0", "8:465:0")
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD.update({
    662: ((), ("024835",)),
    663: ((), ("024835",)),
    664: ((), ("024833", "024935", "024A35")),
    667: ((), ("024635", "024834", "024634")),
    670: ((), ("024735",)),
    673: ((), ("024635",)),
    676: ((), ("024735",)),
    678: ((), ("024735", "024835")),
    679: ((), ("024735",)),
    682: ((), ("024634",)),
    683: ((), ("024735",)),
    684: ((), ("024735",)),
    685: ((), ("024735",)),
    690: ((), ("024735",)),
    692: ((), ("024735",)),
    693: ((), ("024735",)),
    696: ((), ("0232",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1431, queue_start=67, queue_stop=134,
    slice_first="17:661:1", slice_last="17:696:0",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple((17, i) for i in range(628, 734)),
    speaker_style=tuple(
        (i, "historical_osaka_battle_dialogue_or_objective")
        for i in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Tennōji", "덴노지"),
        ("Sanada Yukimura", "사나다 유키무라"),
        ("Ōtani Yoshiharu", "오타니 요시하루"),
        ("Ōgosho", "대어소"),
        ("Osaka Castle", "오사카성"),
        ("firearm unit", "철포대"),
        ("project long ellipsis", "…"),
    ),
    basis=(
        "all sixty-seven visible B142 middle-slice coordinates are manually "
        "reviewed against pristine PK JP and complete PK EN SC TC context; "
        "completed Base battle, objective and defeat rows provide semantic "
        "register context only; the split Tennōji objective failure and "
        "Sanada-Yukimura/Otani-Yoshiharu counter objective are completed "
        "with reviewed optional-neighbor fragments and ASCII closing "
        "parenthesis; historical titles and names, dynamic call operands, "
        "controls, protected outer whitespace, line breaks, complete arity, "
        "pins, reverse overlays, tamper rejection, outside-scope identity, "
        "optional neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=7,
    pins={
        "expected_queue_universe_sha256": "9ADC9B4DD0A084887292B974B664291A50102FAC706F3F8FD9A07A4FD782C767",
        "expected_queue_slice_sha256": "3B914E0B6AE509E0B8BA54EDF22E94D30FC2B0EAB8DB7869E9B84747208EF2C0",
        "expected_prefilled_coordinate_sha256": "B22D0B724D8F2B59138840DFF0F0013CE451D1B28A5C3962ACBEF205974B5531",
        "expected_prefill_slice_context_sha256": "90D662C0FB1D86F918E9F55DEA845D6CD8A2FCF139A9732E1A77BE9EE386DED6",
        "expected_target_coordinate_sha256": "D3FD27C4F44B51A825DF251F51AB168BFD027A4EFBEFD7C36E46DCB5A1C02FD1",
        "expected_source_target_sha256": "64304F19E2AB6EFF18FF79668AE3547BC3B81F7ED225A6431E60CECB9069B3D8",
        "expected_current_target_sha256": "FC80A1610A11221D0BA5A925ADE0660B2B7E359C55A8EA44D563343E3B657CF1",
        "expected_context_corpus_sha256": "D37D0147B94C15EFAD70A3E9F8EC94A9D06CC6FCB3575430EE470F5EAC990A7C",
        "expected_gap_contract_sha256": "87E3DCB063884FAA51D09FB2982D9C6AACE4EDE6EF6AD5EE0FBF55CF05160B2A",
        "expected_boundary_sha256": "9A577397C8D95F6B8C0F0CE6E8B21E7496AC8E5D8D0DFFF3066EF45C89FF7122",
        "expected_runtime_control_sha256": "3654DA9F8338D80CBC8E1B0E2294D3C0C5E424EDA9F621FFFD33336544D6F76F",
        "expected_base_search_sha256": "1C936E0A7D0FE5F225BAE5AFF1CBD2E24B166517310BE805B4DCFBC6EE440C2A",
        "expected_complete_assembly_sha256": "1938EA28D239DCA3D5AAA37D73EE30D90742D014B0A60AD5B2F391A3CCF8C60A",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "F0385EA731EA5A88615BEBA1624127AA370E04F36A4D6462CE5D63B80D5BA5AC",
        "expected_terminology_policy_sha256": "0EFD27B7A3637973D1B7F082C0F3519502E31503FBC9D0DEC0CA1DED042012F7",
        "expected_translation_policy_sha256": "875C802B1A14B7BD54307A6879BC7E5BDDA473C2FC6857F028706100533957B3",
        "expected_candidate_sha256": "37006F19A1ECE80CA55F55052EBD885DD7487853303055B3EEBCA418F864D741",
        "expected_combined_slice_candidate_sha256": "0D6EC7424F4168424B19B7D4A7C4F715E550EFE76FEBBE45BE6A3390660A4C89",
        "expected_combined_changed_literal_count": 8,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B142_S1431",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B142_S1431.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B142_S1430.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B142_S1432.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B142", "queue_row_count": 106,
    "queue_visible_count": 200, "queue_first": "17:628:0",
    "queue_last": "17:733:1",
})


def read_jsonl_with_splits(path: Path) -> tuple[dict[str, Any], ...]:
    rows = tuple(_ORIGINAL_READ_JSONL(path))
    if path.resolve(strict=False) == COMMON.PREFILL.resolve(strict=False):
        return rows + SYNTHETIC_ROWS
    return rows


def base_evidence_with_splits(
    prepared: Any,
    records: dict[str, Any],
) -> Any:
    neighbors = {
        str(row["coordinate"]): row
        for path in CONFIG["optional_neighbors"] if path.is_file()
        for row in _ORIGINAL_READ_JSONL(path)
    }
    for coordinate, expected in SPLIT_TRANSLATIONS.items():
        row = neighbors.get(coordinate)
        if row is not None and (
            row.get("translation") != expected
            or row.get("semantic_review") != "approved"
        ):
            raise RuntimeError(
                f"segment 1431 split neighbor drifted: {coordinate}"
            )
    return _ORIGINAL_BASE_EVIDENCE(prepared, records)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "read_jsonl", read_jsonl_with_splits)
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_evidence_with_splits
    COMMON.CORE.base_and_assembly_evidence = base_evidence_with_splits


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
