#!/usr/bin/env python3
"""Build source-redacted PK B143 segment 1434 residual decisions."""

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
    "17:772:0", "17:773:0", "17:774:0", "17:774:1",
    "17:775:0", "17:776:0", "17:776:1",
    "17:777:0", "17:777:1", "17:777:2", "17:777:3",
    "17:778:0", "17:778:1", "17:779:0", "17:779:1",
    "17:780:0", "17:781:0", "17:781:1", "17:781:2",
    "17:782:0", "17:782:1", "17:783:0", "17:784:0",
    "17:785:0", "17:785:1", "17:786:0", "17:786:1",
    "17:787:0", "17:787:1", "17:788:0", "17:789:0",
    "17:790:0", "17:790:1", "17:791:0", "17:791:1",
    "17:792:0", "17:792:1",
    "17:793:0", "17:793:1", "17:793:2",
    "17:794:0", "17:794:1", "17:794:2", "17:794:3",
    "17:795:0", "17:795:1", "17:795:2", "17:795:3",
    "17:796:0", "17:796:1",
    "17:797:0", "17:797:1", "17:797:2",
    "17:798:0", "17:798:1", "17:798:2",
    "17:799:1", "17:799:2", "17:799:3", "17:799:4", "17:799:5",
    "17:800:0", "17:801:0", "17:802:0", "17:803:0", "17:804:0",
)
TRANSLATIONS = {
    "17:772:0": "님께서 출진하시도록\n이길 싸움이라 여기게 만든다… 그렇지?",
    "17:773:0": (
        "마지막 싸움이라며 기세를 올린 자도 있겠지\n"
        "우선 적의 칼끝을 끌어당겨… 꺾는다"
    ),
    "17:774:0": "덴노지",
    "17:774:1": "에서 적을 끌어들여 친다\n그것이 내 역할이라는 말이군요",
    "17:775:0": (
        "선봉이 무너지면 달아날 병사도 있겠지\n"
        "특히 이번에는 전쟁을 모르는 자가 많다"
    ),
    "17:776:0": "적의 진형은 무너지고 본진까지 길이 열린다\n그곳을",
    "17:776:1": "님과 함께 찌른다",
    "17:777:0": "그리하면",
    "17:777:1": "도 허락할 터\n",
    "17:777:2": "님과",
    "17:777:3": "에게도 전갈을 부탁해 두었다",
    "17:778:0": "(죽더라도",
    "17:778:1": "의 피를 남기기 위해서… 인가\n 어디까지 내다본 것인지…)",
    "17:779:0": "자—",
    "17:779:1": "놓치지 않으려면\n기습하라는 말이군……",
    "17:780:0": (
        "적에게 들키지 않고 도착할 수 있을지는\n"
        "신의 가호를 믿을 수밖에 없겠군"
    ),
    "17:781:0": "하지만 “",
    "17:781:1": "는 움직이지 않는다”는 건가……\n",
    "17:781:2": "님, 그 말씀을 믿겠습니다……",
    "17:782:0": "뭐라고? 승산을 찾으면\n",
    "17:782:1": "님께 출진을 청하라고…?",
    "17:783:0": "저 낭인들, 이길 수 있다고 생각하나……\n후, 후후후……하하하!",
    "17:784:0": (
        "좋다, 마지막까지 발버둥 쳐 보자\n"
        "어차피 달리 의지할 것도 없으니"
    ),
    "17:785:0": "이번 싸움에서는 반드시 선봉의 역할을 다하고\n술로 저지른 실수를 만회해",
    "17:785:1": "라는 오명을 씻어야 한다!",
    "17:786:0": "흥, 시시한 싸움이군…\n",
    "17:786:1": ", 모두에게 자리를 지키라고 전하라",
    "17:787:0": "성에 틀어박힐 수도, 해자와 강을 이용할 수도 없다\n아무리",
    "17:787:1": "라도 손쓸 도리가 없겠지",
    "17:788:0": (
        "병력이 우세한 대장이 움직이는 건 하책이다\n"
        "움직이지 말고 결말을 지켜보자"
    ),
    "17:789:0": "적의 선봉을 격퇴하라",
    "17:790:0": "적의 선봉을 격퇴하라 (",
    "17:790:1": "/2)",
    "17:791:0": "적의 선봉을 격퇴하라",
    "17:791:1": " 성공",
    "17:792:0": "적의 선봉을 격퇴하라",
    "17:792:1": " 실패",
    "17:793:0": "부대를 기습할 때까지",
    "17:793:1": "덴노지",
    "17:793:2": "를 지켜라",
    "17:794:0": "부대를 기습할 때까지",
    "17:794:1": "덴노지",
    "17:794:2": "를 지켜라",
    "17:794:3": " 성공",
    "17:795:0": "부대를 기습할 때까지",
    "17:795:1": "덴노지",
    "17:795:2": "를 지켜라",
    "17:795:3": " 실패",
    "17:796:0": "부대로",
    "17:796:1": "부대를 기습하라",
    "17:797:0": "부대로",
    "17:797:1": "부대를 기습하라",
    "17:797:2": " 성공",
    "17:798:0": "부대로",
    "17:798:1": "부대를 기습하라",
    "17:798:2": " 실패",
    "17:799:1": "혼다 헤이하치로 다다카쓰",
    "17:799:2": "의 아들,",
    "17:799:3": "!\n",
    "17:799:4": "의,",
    "17:799:5": "의 무용을 똑똑히 보아라!",
    "17:800:0": (
        "이 대전투에 어울리는 훌륭한 기백이군\n"
        "선봉에 걸맞은 용장이지만……"
    ),
    "17:801:0": "적은 우리를 두려워해 물러나고 있다!\n이대로 밀어붙여 무너뜨려라!",
    "17:802:0": "주변을 살피지 못하는 모양이군\n철포대, 일제히 쏴라!",
    "17:803:0": "뭐라고, 복병이라고!\n이깟 철포 따위에… 으악!",
    "17:804:0": "이런 유인책에 넘어가서는\n이",
}
TARGET_RECORD_IDS = tuple(range(772, 805))
EXPECTED_ARITY = {
    772: 1, 773: 1, 774: 2, 775: 1, 776: 2, 777: 4,
    778: 2, 779: 2, 780: 1, 781: 3, 782: 2, 783: 1,
    784: 1, 785: 2, 786: 2, 787: 2, 788: 1, 789: 1,
    790: 2, 791: 2, 792: 2, 793: 3, 794: 4, 795: 4,
    796: 2, 797: 3, 798: 3, 799: 6, 800: 1, 801: 1,
    802: 1, 803: 1, 804: 2,
}
PREFILL_COMPANION_COORDINATES = ("17:799:0", "17:804:1")
PREFILL_COMPANION_DONOR = {
    "17:799:0": "9:2022:0",
    "17:804:1": "neighbor:S1435",
}
SPLIT_TRANSLATIONS = {"17:804:1": "의 목을 벨 수 없다!"}
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
    772: ((), ("024835",)),
    776: ((), ("024834",)),
    777: ((), ("024833", "024935", "024A35")),
    778: ((), ("024834",)),
    779: ((), ("024835",)),
    781: ((), ("024834", "024735")),
    782: ((), ("024835",)),
    785: ((), ("024634",)),
    786: ((), ("024835",)),
    787: ((), ("024834",)),
    790: ((), ("0232",)),
    799: ((), ("024635", "024834", "024634")),
    804: ((), ("024635",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1434, queue_start=67, queue_stop=134,
    slice_first="17:772:0", slice_last="17:804:0",
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
    boundary_record_keys=tuple((17, record_id) for record_id in range(734, 846)),
    speaker_style=tuple(
        (record_id, "historical_osaka_battle_dialogue_or_objective")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Tennōji", "덴노지"),
        ("Honda Heihachirō Tadakatsu", "혼다 헤이하치로 다다카쓰"),
        ("main camp", "본진"),
        ("moat", "해자"),
        ("firearm unit", "철포대"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "all sixty-seven visible B143 middle-slice coordinates are manually "
        "reviewed against pristine PK JP and complete PK EN SC TC context; "
        "one exact completed-Base fragment is reused and the split lure "
        "dialogue in record 804 is completed with the reciprocally reviewed "
        "segment-1435 fragment; historical names, battle objectives, dynamic "
        "call operands, controls, protected whitespace, line breaks, complete "
        "arity, pins, reverse overlays, tamper rejection, outside-scope "
        "identity, optional neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=13,
    pins={
        "expected_queue_universe_sha256": "97034B72BF1A59D3B88B58402638522D02F813FE7A6E9F9EA591CD300B8578A2",
        "expected_queue_slice_sha256": "904163682EF1BF6FEB280B6BA52EF084B6BBAE756BE84BFF9062D91944364B03",
        "expected_prefilled_coordinate_sha256": "43CE1018FE80CA1F9E61FC704B70BDF880C831DD2041DE4FC36C26DE692E92E7",
        "expected_prefill_slice_context_sha256": "888456DF99A19D40B1BCD4BC865C7A2BBC828AB224070A2AD0F4D9FBF2DE2FE9",
        "expected_target_coordinate_sha256": "B84E1C48DA6347E0FBB97FADE795CA77AB2AD14CB4B7EB78E6698C072C22A873",
        "expected_source_target_sha256": "154F3871E55AF163737713EDDC510AFE959556EF3D048EF31AAD9641C7E3538F",
        "expected_current_target_sha256": "3060AE858EACA27C34DAD9A28428D50ECC365419514E29E2D9B514C63DB032E0",
        "expected_context_corpus_sha256": "94CA6DAE2694DA146AB4181314A55D1E06AE366CE75F3A4FB7C3871DCD5679E9",
        "expected_gap_contract_sha256": "5BEB5F19F8BC91EF88BD8DD931A8B0373050A201A18CBB8B0ECFDA30DF85DA01",
        "expected_boundary_sha256": "76E0B181706E5F4143FC8CA6AEA3E5937EADBAEAF717B69E5D3C23CB20D56361",
        "expected_runtime_control_sha256": "DD2AA651C40C3D7AD0C79BC4616825F68DF94B110322B7AEC37D48EC488B19EF",
        "expected_base_search_sha256": "CCD7233CA3088352F5FCF6BC28769C6CC3D7F1732466B78BFE3E632CCBEE5FBB",
        "expected_complete_assembly_sha256": "0303FE65D2D6AF0A922FA05CA7A591A424DC9B6C581949C13485CC9BCD0CDBCE",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "1B7FC57B585ACCEABD46BCB1BDE84FA2A73A566D17213D0C5496B8CFAE1FB4A7",
        "expected_terminology_policy_sha256": "D73BCEC306B21BA5E69514A54DD32E68A768D4DA5F8D4692E99F9A5CF7A30A36",
        "expected_translation_policy_sha256": "1423619F9F12351C0DD8CBCB4ADFCF5554DABFDFDAB9CACECD2F8174FD8E8153",
        "expected_candidate_sha256": "DFF4EA8C5E004A46552C486AF31E9B4F6B72EA42227CEC1D69C25E54FBEBEBC3",
        "expected_combined_slice_candidate_sha256": "7F70174E283E19D79FD72171DAF6CF82B0078DB6CFD578627FBD5B8ED9A464A3",
        "expected_combined_changed_literal_count": 14,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B143_S1434",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B143_S1434.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B143_S1433.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B143_S1435.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B143", "queue_row_count": 112,
    "queue_visible_count": 200, "queue_first": "17:734:0",
    "queue_last": "17:845:0",
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
                f"segment 1434 split neighbor drifted: {coordinate}"
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
