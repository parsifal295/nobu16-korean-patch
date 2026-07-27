#!/usr/bin/env python3
"""Build source-redacted PK B108 segment 1329 residual decisions."""

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
    "14:153:2",
    "14:154:2",
    "14:154:4",
    "14:154:6",
    "14:154:8",
    "14:155:2",
    "14:155:3",
    "14:155:4",
    "14:155:5",
    "14:155:6",
    "14:155:7",
    "14:155:8",
    "14:155:9",
    "14:156:0",
    "14:157:0",
    "14:157:1",
    "14:159:3",
    "14:160:1",
    "14:161:1",
    "14:162:1",
    "14:163:1",
    "14:164:0",
    "14:164:1",
    "14:164:2",
    "14:164:3",
    "14:164:4",
    "14:164:6",
    "14:164:7",
    "14:165:0",
    "14:165:1",
    "14:165:2",
    "14:165:3",
    "14:165:4",
    "14:165:6",
    "14:165:7",
    "14:165:8",
    "14:165:9",
    "14:166:1",
)
TRANSLATIONS = {
    "14:153:2": "[성 능력]",
    "14:154:2": "◇통솔",
    "14:154:4": "◇무용",
    "14:154:6": "◇지략",
    "14:154:8": "◇정무",
    "14:155:2": "◇통솔",
    "14:155:3": (
        "\n　·부대와 성의 방어\n"
        "·취락 장악 속도\n"
        "·통솔 70 이상이면 성하 방침 \"방위\"를 선택할 수 있다\n"
        "·본인의 통솔이 70 이상이면 군단 전략 \"광역\"을 제안할 수 있다"
        "(성 능력으로는 불가)\n"
    ),
    "14:155:4": "◇무용",
    "14:155:5": (
        "\n　·부대와 성의 공격\n"
        "·무용 70 이상이면 성하 방침 \"공격\"을 선택할 수 있다\n"
        "·본인의 무용이 70 이상이면 군단 전략 \"양동\"을 건의할 수 있다"
        "(성 능력으로는 불가)\n"
    ),
    "14:155:6": "◇지략",
    "14:155:7": (
        "\n　·부대의 포위와 성의 대포위\n"
        "·조략 성공률\n"
        "·지략 60 이상이면 영주가 인접 군을 조략하기도 한다\n"
        "·지략 70 이상이면 성하 방침 \"진군\"을 선택할 수 있다\n"
        "·본인의 지략이 70 이상이면 군단 전략 \"증원\"을 제안할 수 있다"
        "(성 능력으로는 불가)\n"
    ),
    "14:155:8": "◇정무",
    "14:155:9": (
        "\n　·성하 시설과 취락의 건설 속도\n"
        "·정책 발령 속도\n"
        "·외교 친선에 따른 신용 상승량\n"
        "·보급 병량 수입량\n"
        "·정무 70 이상이면 성하 방침 \"내정\"을 선택할 수 있다"
    ),
    "14:156:0": "[신분]",
    "14:157:0": "[신분]",
    "14:157:1": (
        "\n자세력 내의 지위를 \"신분\"이라고 합니다.\n"
        "신분이 높을수록 다양한 \"직명\"에 임명될 수 있지만\n"
        "승진하려면 더 많은 훈공이 필요합니다.\n"
        "신분에는 다음 단계가 있습니다.\n"
        "\n"
        "　·숙로 ... 가장 높은 신분\n"
        "         \"군단장\", \"성주\", \"영주\", \"대관\"에 임명 가능\n"
        "         평정중 \"가재\", \"봉행\"에 임명 가능\n"
        "·가로 ... 숙로와 같은 직명/평정중에 임명 가능\n"
        "·부장 ... \"성주\", \"영주\", \"대관\"에 임명 가능\n"
        "         평정중 \"봉행\"에 임명 가능\n"
        "·사무라이 대장 ... 부장과 같은 직명에 임명 가능\n"
        "·아시가루 대장 ... \"영주\", \"대관\"에 임명 가능\n"
        "·조두 ... \"대관\"에 임명 가능 \n"
        "\n"
        "※신분에 걸맞은 직명을 주지 않으면 가신이 불만을 품고 충성이 내려갑니다"
    ),
    "14:159:3": (
        "\n　·충의가 두터운 성격이다\n"
        "·다이묘의 일문이나 배우자이거나 다이묘와 상성이 좋다\n"
        "·오랫동안 다이묘 가문을 섬겼거나 신분이 높다\n"
        "·관직이나 가보를 받았다\n"
        "·감장을 받았다\n"
        "·직담의 영향\n"
        "·합전이나 공성전에서 승리하여 위풍이 발생했다\n"
        "·특성이나 정책의 영향"
    ),
    "14:160:1": (
        "\n　·야심이 강한 성격이다\n"
        "·다이묘에게 원한이 있거나 상성이 나쁘다\n"
        "·새로운 다이묘를 받아들이지 못한다\n"
        "·신분에 걸맞은 지행지를 받지 못했다\n"
        "·자신의 영지가 공격받고 있거나 이미 빼앗겼다\n"
        "·원래 가지고 있던 가보를 다이묘에게 몰수당했다\n"
        "·직담으로 받은 대우에 만족하지 못한다\n"
        "·직담으로 맺은 약정이 깨졌다\n"
        "·다이묘가 외교 상대와의 약속을 깨는 등 불명예스러운 행동을 했다\n"
        "·합전이나 공성전에서 패배하여 상대의 위풍이 발생했다\n"
        "·정책이나 조략 \"유언비어\"의 영향"
    ),
    "14:161:1": (
        "\n　·조략 \"공물\"을 실행한다\n"
        "·동맹이나 종속 관계를 맺는다\n"
        "·역직을 부여한다(자세력이 막부 세력일 때만)\n"
        "·동맹 세력을 줄인다\n"
        "　※AI 레벨 \"표준\" 이상에서는 동맹 상대가 많은 세력이 경계받기 때문"
    ),
    "14:162:1": (
        "\n　·외교 교섭 \"공물\"을 실행한다\n"
        "·동맹이나 종속 관계를 맺는다\n"
        "·역직을 부여한다(자세력이 막부 세력일 때만)\n"
        "·동맹 세력을 줄인다\n"
        "　※AI 레벨 \"표준\" 이상에서는 동맹 상대가 많은 세력이 경계받기 때문"
    ),
    "14:163:1": (
        "\n　·적 세력을 멸망시키고 포박한 무장을 등용한다\n"
        "·영내 제책 \"무장 탐색\"을 실행한다\n"
        "·\"○○중 두령\" 이외의 무장이 있는 국인중을 대상으로 "
        "영내 제책 \"국인중 편입\"을 실행한다"
    ),
    "14:164:0": "[훈공]",
    "14:164:1": (
        "\n무장이 세력에 공헌하여 훈공을 얻으면 \"신분\"이 오릅니다.\n"
        "신분이 오르면 더 책임 있는 자리에 임명할 수 있으므로\n"
        "눈여겨보는 무장이 훈공을 얻도록 명령을 내립시다.\n"
        "다음과 같은 행동으로 훈공을 얻을 수 있습니다.\n"
        "\n"
    ),
    "14:164:2": "◇내정",
    "14:164:3": (
        "\n　·\"성주\", \"영주\", \"대관\"으로서 군이나 성을 개발한다\n"
        "·\"조두\"로서 하급 업무를 맡는다\n"
        "　(정책 \"호로슈 결성\" 발령 필요)\n"
        "·실행 무장으로 명령을 수행한다\n"
        "　(성하 시설, 정책, 조략, 영내 제책, 외교)\n"
        "\n"
    ),
    "14:164:4": "◇건의",
    "14:164:6": "◇군사",
    "14:164:7": (
        "\n　·적 부대를 격파하거나 적 성을 제압한다\n"
        "·합전에서 공헌한다"
    ),
    "14:165:0": "[훈공]",
    "14:165:1": (
        "\n무장이 세력에 공헌하여 훈공을 얻으면 \"신분\"이 오릅니다.\n"
        "신분이 오르면 더 책임 있는 자리에 임명할 수 있으므로\n"
        "눈여겨보는 무장이 훈공을 얻도록 명령을 내립시다.\n"
        "다음과 같은 행동으로 훈공을 얻을 수 있습니다.\n"
        "\n"
    ),
    "14:165:2": "◇내정",
    "14:165:3": (
        "\n　·\"성주\", \"영주\", \"대관\"으로서 군이나 성을 개발한다\n"
        "·\"조두\"로서 하급 업무를 맡는다\n"
        "　(정책 \"호로슈 결성\" 발령 필요)\n"
        "·실행 무장으로 명령을 수행한다\n"
        "　(성하 시설, 정책, 조략, 영내 제책, 외교)\n"
        "\n"
    ),
    "14:165:4": "◇건의",
    "14:165:6": "◇군사",
    "14:165:7": (
        "\n　·적 부대를 격파하거나 적 성을 제압한다\n"
        "·합전이나 공성전에서 공헌한다\n"
        "\n"
    ),
    "14:165:8": "◇기타",
    "14:165:9": "\n　·은상으로 감장을 수여한다",
    "14:166:1": (
        "\n　·성의 저장 병량이 출진 병력 이상 쌓인 뒤 출진한다\n"
        "·성하 시설 \"치중 집결소\"를 건설한다\n"
        "·정책 \"치중대 배치\"를 발령한다\n"
        "·공략 목표를 설정해 임전 상태로 만든다\n"
        "·자세력의 성 위에서 대기한다\n"
        "　※출진한 성의 병량을 사용할 수 있기 때문"
    ),
}
TARGET_RECORD_IDS = (
    153,
    154,
    155,
    156,
    157,
    159,
    160,
    161,
    162,
    163,
    164,
    165,
    166,
)
EXPECTED_ARITY = {
    153: 4,
    154: 10,
    155: 10,
    156: 2,
    157: 2,
    159: 4,
    160: 2,
    161: 2,
    162: 2,
    163: 2,
    164: 8,
    165: 10,
    166: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "14:153:0",
    "14:153:1",
    "14:153:3",
    "14:154:0",
    "14:154:3",
    "14:154:5",
    "14:154:7",
    "14:154:9",
    "14:155:0",
    "14:156:1",
    "14:159:0",
    "14:159:1",
    "14:159:2",
    "14:160:0",
    "14:161:0",
    "14:162:0",
    "14:163:0",
    "14:164:5",
    "14:165:5",
    "14:166:0",
)
PREFILL_COMPANION_DONOR = {
    **{
        f"14:153:{literal_id}": f"14:111:{literal_id}"
        for literal_id in (0, 1, 3)
    },
    **{
        f"14:154:{literal_id}": f"14:112:{literal_id}"
        for literal_id in (0, 3, 5, 7, 9)
    },
    "14:155:0": "14:112:0",
    "14:156:1": "14:113:1",
    **{
        f"14:159:{literal_id}": f"14:114:{literal_id}"
        for literal_id in (0, 1, 2)
    },
    "14:160:0": "14:114:4",
    "14:161:0": "14:115:0",
    "14:162:0": "14:115:0",
    "14:163:0": "14:116:0",
    "14:164:5": "14:117:5",
    "14:165:5": "14:117:5",
    "14:166:0": "14:118:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "14:154:1",
    "14:155:1",
)
HIDDEN_BASE_DONOR_COORDINATES = {"14:112:1"}
SEMANTIC_BASE_CONTEXT = {
    153: (),
    154: (),
    155: tuple(
        f"14:112:{literal_id}"
        for literal_id in (0, 2, 3, 4, 5, 6, 7, 8, 9)
    ),
    156: (),
    157: tuple(f"14:113:{literal_id}" for literal_id in range(2)),
    159: tuple(f"14:114:{literal_id}" for literal_id in range(6)),
    160: ("14:114:4", "14:114:5"),
    161: tuple(f"14:115:{literal_id}" for literal_id in range(2)),
    162: tuple(f"14:115:{literal_id}" for literal_id in range(2)),
    163: tuple(f"14:116:{literal_id}" for literal_id in range(2)),
    164: tuple(f"14:117:{literal_id}" for literal_id in range(8)),
    165: tuple(f"14:117:{literal_id}" for literal_id in range(8)),
    166: tuple(f"14:118:{literal_id}" for literal_id in range(2)),
}
EXACT_BASE_DONOR = {
    153: (14, 111),
    154: (14, 112),
    156: (14, 113),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (
        (EXACT_BASE_DONOR[record_id],)
        if record_id in EXACT_BASE_DONOR
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1329,
    queue_start=67,
    queue_stop=134,
    slice_first="14:152:4",
    slice_last="14:167:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(
        HIDDEN_CURRENT_COMPANION_COORDINATES
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (14, record_id) for record_id in range(150, 170)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_help")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("castle ability", "성 능력"),
        ("leadership", "통솔"),
        ("valor", "무용"),
        ("intelligence", "지략"),
        ("political affairs", "정무"),
        ("castle town plan", "성하 방침"),
        ("province strategy", "군단 전략"),
        ("wide area", "광역"),
        ("feint", "양동"),
        ("reinforcement", "증원"),
        ("station", "신분"),
        ("role name", "직명"),
        ("council officials", "평정중"),
        ("conservator", "가재"),
        ("overseer", "봉행"),
        ("commendation letter", "감장"),
        ("direct talk", "직담"),
        ("direct-talk agreement", "약정"),
        ("rumor", "유언비어"),
        ("honor", "훈공"),
        ("bodyguard formation", "호로슈 결성"),
        ("supply station", "치중 집결소"),
        ("small supply unit deployment", "치중대 배치"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary evidence; three "
        "complete records reuse approved exact Base Korean assemblies, "
        "including one source-identical hidden newline, while ten PK-specific "
        "or extended records use completed Base entries only as semantic and "
        "register context and never inherit Base runtime or VM state; the "
        "political-affairs threshold in the civil castle-town-plan line follows "
        "the SC and TC rules text and the completed Base translation rather "
        "than propagating the isolated source label typo; castle ability, "
        "leadership, valor, intelligence, political affairs, province "
        "strategy, wide-area, feint, reinforcement, station, council official, "
        "conservator, overseer, commendation letter, direct talk, agreement, "
        "rumor, honor, bodyguard and supply terms remain distinct; token "
        "separators, hidden newlines, leading and trailing whitespace, bullets, "
        "terminators, complete record arity, all twenty-nine slice prefills, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=24,
    pins={
        "expected_queue_universe_sha256": (
            "FFA1827A890DE1A6FA6B7FF4AAD76E2E4D9A2C00796F508C5DCAF204DC4D80B8"
        ),
        "expected_queue_slice_sha256": (
            "9AA2995989EB30407C2E2BD8ECBEA7175DCD0BE22738C8CDA203D004EDFE55C6"
        ),
        "expected_prefilled_coordinate_sha256": (
            "2D28F6845DC2805FEF18CEB154F75E21D28EE128F9B1A646E5F700BB7B2C7B1A"
        ),
        "expected_prefill_slice_context_sha256": (
            "D66824C27EC46BFC7587E3A61AC0D1CDDFFB73D886A570C8F796F8B750138991"
        ),
        "expected_target_coordinate_sha256": (
            "5BA1F62F0B760028096210A24B121C69F56A81A333EF7587ABDF01934C1FF5A1"
        ),
        "expected_source_target_sha256": (
            "03D85DB13962EFD69219FB4AB357D8D9E3BB22DB1E6ABC866393EA2E6F2A7D1F"
        ),
        "expected_current_target_sha256": (
            "F20E874DC631FA8B2BA74613C27406184F193424AD8D5E5A83D487A8E0EF3E36"
        ),
        "expected_context_corpus_sha256": (
            "2A1DB1981FE75894EA30E7A92F2D17C258968FCB1A30F69A9E6C8DF15964DACB"
        ),
        "expected_gap_contract_sha256": (
            "55C95E2DF4D63A38CAF6FD9D34905A8F5216EA634D833042BD1B1DF4DCD58AE3"
        ),
        "expected_boundary_sha256": (
            "FCFE95EB8BE879E074FB68FDB2471676A1291B1454F989393F7312F5241C58A7"
        ),
        "expected_runtime_control_sha256": (
            "5F87ACE0C05CDE106AAD900991BC2EFD7DEC9F4BA64E1162189C3E265F3E8BA8"
        ),
        "expected_base_search_sha256": (
            "9CB31134A01C161F29CB6DFB555CE3F7AFA27BBCEFA82DE32ED36B71495EC361"
        ),
        "expected_complete_assembly_sha256": (
            "9CC45B2B1EC31F09DA0358F822CB2152C4333A6FB00A9679B24870F0B87876A9"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "E7B8EC00159FECCCE7CD1E7F6BA7C3752B27421979349793E85A68EA57CF0F89"
        ),
        "expected_terminology_policy_sha256": (
            "9E5A19EDA2933509080E01FE922EB77848F94DB4095C807C10187F2D670702EA"
        ),
        "expected_translation_policy_sha256": (
            "C1C100703855EB8FD78741B0A29F3634A397B5C2F4E204E304027F5B77E93D80"
        ),
        "expected_candidate_sha256": (
            "6529BE1FE32C5C644BB08BAF1EEB2108219C45044E064B8386D97E78FBA1EA3A"
        ),
        "expected_combined_slice_candidate_sha256": (
            "F77E22CE3870F5FAFCCE8526DABFE3EE5949EC68D29FC721CBB1C6DEF5232E5A"
        ),
        "expected_combined_changed_literal_count": 50,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B108_S1329",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1329.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1328.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1330.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B108",
    "queue_row_count": 43,
    "queue_visible_count": 197,
    "queue_first": "14:139:0",
    "queue_last": "14:181:3",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Review complete records, including source-identical hidden newlines."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1329 Base promoted input drifted")
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
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_hidden: set[str] = set()
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
                f"segment 1329 Base search drifted: {record_id}"
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
            if donor_coordinate in HIDDEN_BASE_DONOR_COORDINATES:
                references.append((
                    donor_coordinate,
                    "\n",
                    "source_identical_hidden_newline",
                    "not_required",
                    "exact_hidden_literal",
                    "runtime_vm_not_inherited",
                ))
                continue
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1329 Base context drifted: "
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
                "\n"
                if coordinate in HIDDEN_BASE_DONOR_COORDINATES
                else str(base_rows[coordinate]["translation"])
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
                        f"segment 1329 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment 1329 hidden newline drifted: {coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1329 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1329 exact assembly drifted: {record_id}"
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
        or seen_hidden != hidden_set
    ):
        raise RuntimeError("segment 1329 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
