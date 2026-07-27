#!/usr/bin/env python3
"""Build source-redacted PK B108 segment 1330 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    167, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 180,
)
TARGET_COORDINATES = (
    "14:167:1",
    "14:169:1",
    "14:170:1",
    "14:171:0",
    "14:171:1",
    "14:171:2",
    "14:171:3",
    "14:172:0",
    "14:172:1",
    "14:172:2",
    "14:172:3",
    "14:173:0",
    "14:173:2",
    "14:173:3",
    "14:174:0",
    "14:174:2",
    "14:174:3",
    "14:175:0",
    "14:175:2",
    "14:175:3",
    "14:176:0",
    "14:176:2",
    "14:176:3",
    "14:177:0",
    "14:177:2",
    "14:177:3",
    "14:178:0",
    "14:178:2",
    "14:180:1",
)
TRANSLATIONS = {
    "14:167:1": (
        "\n"
        "　·성의 저장 병량이 출진 병력 이상 쌓인 뒤 출진한다\n"
        " ·성하 시설 \"치중 집결소\"를 건설한다\n"
        " ·정책 \"치중대 배치\"를 발령한다\n"
        " ·공략 목표를 설정해 임전 상태로 만든다\n"
        " ·자세력의 성 위에서 대기한다\n"
        "  ※출진지의 병량을 사용할 수 있기 때문\n"
        " ·행군 경로상의 성을 보급 거점으로 설정한다"
    ),
    "14:169:1": (
        "\n"
        "주변에 자신보다 약한 세력이 있다면\n"
        "공격하여 영토와 무장을 빼앗읍시다.\n"
        "\n"
        "자리를 비운 사이 다른 세력의 공격을 받지 않도록\n"
        "내정으로 영지를 지킬 병력을 늘리거나\n"
        "미리 위험한 상대와 동맹을 맺으면 더욱 안전합니다.\n"
        "\n"
        "전쟁이 길어질 듯하면 합전을 벌여\n"
        "단숨에 결판을 내는 것도 효과적입니다."
    ),
    "14:170:1": (
        "\n"
        "지나치게 넓은 영토를 다이묘 혼자 다스리기는 어려우므로\n"
        "군단을 만들어 휘하 무장에게 맡기는 것이 중요합니다.\n"
        "\n"
        "약소 세력은 외교로 종속시킬 수 있는 경우가 있습니다.\n"
        "불필요한 전쟁을 피하는 것도 천하통일의 지름길이 될 것입니다."
    ),
    "14:171:0": "[조략]",
    "14:171:1": (
        "\n"
        "다른 세력에 약화나 공격 등의 공작을 벌입니다.\n"
        "\"다이묘\", \"성주\", \"측근\"이 실행할 수 있습니다.\n"
        "\n"
        "·유언비어 ... 대상 무장의 충성을 낮춘다\n"
        "·빼내기 ... 충성이 낮은 무장을 자세력으로 빼낸다\n"
        "·선동 ... 대상 성의 군에서 잇키를 일으킨다\n"
        "·파괴 ... 대상 성의 내구와 병력을 줄인다\n"
        "·방화 ... 대상 성의 병량과 병력을 줄인다\n"
        "·공물 ... 대상 세력에 가보를 보내 외교 자세를 개선한다\n"
        "\n"
    ),
    "14:171:2": "◇주의",
    "14:171:3": (
        "\n"
        "\"조략\" 명령은 원하는 때에 실행할 수 있는 대신\n"
        "가신의 건의보다 금전과 노동력, 효과와 기간 면에서 효율이 낮습니다."
    ),
    "14:172:0": "[조략]",
    "14:172:1": (
        "\n"
        "다른 세력에 약화나 공격 등의 공작을 벌입니다.\n"
        "\"다이묘\", \"성주\", \"측근\"이 실행할 수 있습니다.\n"
        "\n"
        "·유언비어 ... 대상 무장의 충성을 낮춘다\n"
        "·빼내기 ... 충성이 낮은 무장을 자세력으로 빼낸다\n"
        "·선동 ... 대상 성의 군에서 잇키를 일으킨다\n"
        "·파괴 ... 대상 성의 내구와 병력을 줄인다\n"
        "·방화 ... 대상 성의 병량과 병력을 줄인다\n"
        "\n"
    ),
    "14:172:2": "◇주의",
    "14:172:3": (
        "\n"
        "\"조략\" 명령은 원하는 때에 실행할 수 있는 대신\n"
        "가신의 건의보다 금전과 노동력, 효과와 기간 면에서 효율이 낮습니다."
    ),
    "14:173:0": "[유언비어]",
    "14:173:2": "◇조건",
    "14:173:3": (
        "\n"
        "·동맹, 종속, 정전 관계가 아니며 동맹 상대의 종속 세력도 아님\n"
        "·자세력과 인접한 성임\n"
        "·충성이 노란색인 무장이 있음\n"
        "\n"
    ),
    "14:174:0": "[빼내기]",
    "14:174:2": "◇조건",
    "14:174:3": (
        "\n"
        "·동맹, 종속, 정전 관계가 아니며 동맹 상대의 종속 세력도 아님\n"
        "·자세력과 인접한 성임\n"
        "·충성이 빨간색인 무장이 있음\n"
        "\n"
    ),
    "14:175:0": "[선동]",
    "14:175:2": "◇조건",
    "14:175:3": (
        "\n"
        "·동맹, 종속, 정전 관계가 아니며 동맹 상대의 종속 세력도 아님\n"
        "·자세력과 인접한 성임\n"
        "·잇키를 일으킬 수 있는 군이 있음\n"
        "\n"
    ),
    "14:176:0": "[파괴]",
    "14:176:2": "◇조건",
    "14:176:3": (
        "\n"
        "·동맹, 종속, 정전 관계가 아니며 동맹 상대의 종속 세력도 아님\n"
        "·자세력과 인접한 성임\n"
        "\n"
    ),
    "14:177:0": "[방화]",
    "14:177:2": "◇조건",
    "14:177:3": (
        "\n"
        "·동맹, 종속, 정전 관계가 아니며 동맹 상대의 종속 세력도 아님\n"
        "·자세력과 인접한 성임\n"
        "\n"
    ),
    "14:178:0": "[공물]",
    "14:178:2": "◇조건",
    "14:180:1": (
        "\n"
        "영내의 군에서는 무장을 파견하지 않으면 해결하기 어려운 문제가 생기기도 합니다.\n"
        "그럴 때는 \"성주\"나 \"측근\"을 지명하여 해결하게 합시다.\n"
        "영내 문제에는 \"영내 황폐\", \"국경 분쟁\", \"상위 취락 건설\", \"명승 관련 문제\"가 있습니다.\n"
        "\n"
    ),
}
EXPECTED_ARITY = {
    167: 2,
    169: 2,
    170: 2,
    171: 4,
    172: 4,
    173: 6,
    174: 6,
    175: 6,
    176: 6,
    177: 6,
    178: 6,
    180: 4,
}
PREFILL_COMPANION_DONOR = {
    "14:167:0": "14:118:0",
    "14:169:0": "14:120:0",
    "14:170:0": "14:121:0",
    "14:173:1": "14:123:1",
    "14:173:4": "14:42:4",
    "14:173:5": "14:123:5",
    "14:174:1": "14:124:1",
    "14:174:4": "14:42:4",
    "14:174:5": "14:123:5",
    "14:175:1": "14:125:1",
    "14:175:4": "14:42:4",
    "14:175:5": "14:125:5",
    "14:176:1": "14:126:1",
    "14:176:4": "14:42:4",
    "14:176:5": "14:123:5",
    "14:177:1": "14:127:1",
    "14:177:4": "14:42:4",
    "14:177:5": "14:123:5",
    "14:178:1": "14:128:1",
    "14:178:3": "14:128:3",
    "14:178:4": "14:42:4",
    "14:178:5": "14:128:5",
    "14:180:0": "14:129:0",
    "14:180:2": "14:129:2",
    "14:180:3": "14:129:3",
}
PREFILL_COMPANION_COORDINATES = tuple(PREFILL_COMPANION_DONOR)
SEMANTIC_BASE_CONTEXT = {
    167: tuple(f"14:118:{literal_id}" for literal_id in range(2)),
    169: tuple(f"14:120:{literal_id}" for literal_id in range(2)),
    170: tuple(f"14:121:{literal_id}" for literal_id in range(2)),
    171: tuple(f"14:122:{literal_id}" for literal_id in range(4)),
    172: tuple(f"14:122:{literal_id}" for literal_id in range(4)),
    173: tuple(f"14:123:{literal_id}" for literal_id in range(6)),
    174: tuple(f"14:124:{literal_id}" for literal_id in range(6)),
    175: tuple(f"14:125:{literal_id}" for literal_id in range(6)),
    176: tuple(f"14:126:{literal_id}" for literal_id in range(6)),
    177: tuple(f"14:127:{literal_id}" for literal_id in range(6)),
    178: tuple(f"14:128:{literal_id}" for literal_id in range(6)),
    180: tuple(f"14:129:{literal_id}" for literal_id in range(4)),
}
EXPECTED_BASE_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES[178] = ((14, 128),)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1330,
    queue_start=134,
    queue_stop=197,
    slice_first="14:167:1",
    slice_last="14:181:3",
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
        (14, record_id) for record_id in range(165, 183)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("storage provisions", "저장 병량"),
        ("supply station", "치중 집결소"),
        ("baggage train deployment", "치중대 배치"),
        ("battle readiness", "임전"),
        ("resupply base", "보급 거점"),
        ("province", "군단"),
        ("covert action", "조략"),
        ("rumor", "유언비어"),
        ("extract", "빼내기"),
        ("incite", "선동"),
        ("destroy", "파괴"),
        ("raze", "방화"),
        ("tribute", "공물"),
        ("revolt", "잇키"),
        ("labor", "노동력"),
        ("major settlement", "상위 취락"),
        ("landmark", "명승"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record tutorial was reviewed as auxiliary evidence; one "
        "byte-identical complete record reuses its approved completed Base "
        "Korean assembly, while eleven PK-specific or extended records use "
        "completed Base entries as complete semantic and register context "
        "without inheriting Base runtime or VM state; the split record 167 "
        "assembly includes its exact Base-prefill heading from the preceding "
        "slice and the PK-only resupply-base rule; medium and major daimyo "
        "advice retains the completed Base register; covert-action names "
        "remain distinct as rumor, extract, incite, destroy, raze and "
        "tribute, with yellow and red loyalty conditions preserved exactly; "
        "the extended domain-problem record adds landmark-related matters "
        "without changing the other completed Base categories; storage "
        "provisions, supply stations, baggage trains, battle readiness, "
        "resupply bases, provinces, labor, major settlements and landmarks "
        "follow the project glossary; outer whitespace, line counts, "
        "full-width bullets, complete record arity, terminators, all "
        "thirty-four slice prefills, twenty-five same-record companions, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbors and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=21,
    pins={
        "expected_queue_universe_sha256":
        "FFA1827A890DE1A6FA6B7FF4AAD76E2E4D9A2C00796F508C5DCAF204DC4D80B8",
        "expected_queue_slice_sha256":
        "4BE446C5EAD07470E145FB36084A812051FD134BC9968764B97E136ACC5368C0",
        "expected_prefilled_coordinate_sha256":
        "AFB4DDD97AB29925E0B2D21F8249D507AA56D9D8E4283B74329C41DECEC70FC9",
        "expected_prefill_slice_context_sha256":
        "52C16C33FBE18867E412B9426764E2E986004B5D9492192D7026D15884AED9BE",
        "expected_target_coordinate_sha256":
        "0FCA6D6230A9C4206DA135F928D00C32F503A1C4775E2295075103234F9E569C",
        "expected_source_target_sha256":
        "3202576458C80CBA72272B9C0C6F4B470BE67503C842F23FB022B23D68C3479E",
        "expected_current_target_sha256":
        "3D3C519DC85C3CF44309BBD098F787C6BB2C1FA8793093570AA2759EB9B274E6",
        "expected_context_corpus_sha256":
        "2A1DB1981FE75894EA30E7A92F2D17C258968FCB1A30F69A9E6C8DF15964DACB",
        "expected_gap_contract_sha256":
        "A30C4E0720BA5DE15FB6F6C454284F1E3A6751561F5384199E1A3A483AEF75A0",
        "expected_boundary_sha256":
        "3A5161D9BD9A8618CEFD99FB40591815B34E4FEB278D2D7F4CFB0486DDFC537F",
        "expected_runtime_control_sha256":
        "05024C1759F9B76FB1951CDCFE61E321009FBEF3E14C5163EA893A0CC7C14429",
        "expected_base_search_sha256":
        "6ED0460DFEE08536D74DAF3C8215BEF85C521A69460C6634BB844E6BB62C233B",
        "expected_complete_assembly_sha256":
        "E04E12A198858DEF4570F39BC19DBC66833E807EB7B5FD5D6A696E2084B25F7F",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "017B02BF261C4308B2574AEE7AB8271D5E0AB45931FEB8930B92682B59B81E4B",
        "expected_terminology_policy_sha256":
        "10F2E9B3A79DA0D00555C74594FF3EA418CA1A895CE1DA29BCA99B50034DFCAD",
        "expected_translation_policy_sha256":
        "642FF04A0B6FDB72AB3D37625A4B1BAB8E28164C7F72E7DEE9317C595F4067D4",
        "expected_candidate_sha256":
        "5E1093D8F1261F6DC0A21B91933BB3DA36672E3B804DF5AB97D8D0A0AFE47887",
        "expected_combined_slice_candidate_sha256":
        "AEAB8D04015879B6D069770EDBF899074497FD7EBD144AFF2995A19CEF0D128B",
        "expected_combined_changed_literal_count": 42,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B108_S1330",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1330.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1328.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1329.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B108",
    "queue_row_count": 43,
    "queue_visible_count": 197,
    "queue_first": "14:139:0",
    "queue_last": "14:181:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {178: (14, 128)})
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
