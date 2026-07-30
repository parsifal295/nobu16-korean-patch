#!/usr/bin/env python3
"""Build source-redacted PK B109 segment 1331 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    182, 183, 184, 185, 186, 188, 189,
    190, 191, 192, 193, 196, 197, 198,
)
TARGET_COORDINATES = (
    "14:182:0",
    "14:182:1",
    "14:182:2",
    "14:182:3",
    "14:183:0",
    "14:184:3",
    "14:185:0",
    "14:185:3",
    "14:186:0",
    "14:186:1",
    "14:186:3",
    "14:188:1",
    "14:189:1",
    "14:189:3",
    "14:190:1",
    "14:191:1",
    "14:191:2",
    "14:191:3",
    "14:192:1",
    "14:192:3",
    "14:193:1",
    "14:193:3",
    "14:196:0",
    "14:197:0",
    "14:197:2",
    "14:198:0",
)
TRANSLATIONS = {
    "14:182:0": "◇명승에 관한 사항",
    "14:182:1": (
        "\n　·명승을 장악하면 세력 전체에 혜택을 준다\n"
        " ·이미 장악한 명승이라면 LV가 올라 효과가 커진다\n"
        "\n"
    ),
    "14:182:2": "◇발생 조건",
    "14:182:3": (
        "\n　·재건(LV1) ... 명승이 있는 성의 개발률이 높아지면 발생한다\n"
        " ·발전(LV2) ... 명승이 있는 국의 모든 성의 개발률이 높아지면 발생한다\n"
        " ·번영(LV3) ... 명승이 있는 지방의 모든 성을 소유하면 발생한다"
    ),
    "14:183:0": "[전봉]",
    "14:184:3": (
        "\n　·출분하여 세력을 떠난다\n"
        " ·성주라면 적의 공격을 받을 때 성이 함락되기 전에 항복한다\n"
        "  ※항복한 성주는 상대 세력의 등용에 반드시 응한다\n"
        " ·불리한 상황이 되면 독단으로 철수한다"
    ),
    "14:185:0": "[위풍]",
    "14:185:3": (
        "\n　·패배한 세력의 군이나 성이 승리한 쪽으로 돌아선다\n"
        " ·주변 세력의 외교 자세가 변동한다\n"
        " ·주변 국인중의 종속도가 변동한다\n"
        " ·양쪽 세력에 속한 무장의 충성이 변동한다"
    ),
    "14:186:0": "[위풍]",
    "14:186:1": (
        "\n다수의 적 부대를 상대로 한 합전이나 공성전에서 승리하면\n"
        "그 명성은 \"위풍\"이 되어 주변까지 퍼지며 영향을 미칩니다.\n"
        "\n"
    ),
    "14:186:3": (
        "\n　·패배한 세력의 군이나 성이 승리한 쪽으로 돌아선다\n"
        "  ※공성전에서 수성 측이 승리한 경우에는 발생하지 않는다\n"
        " ·패배한 세력 주변의 성이 동요하여 출진이나 설비 건설을 할 수 없게 된다\n"
        "  ※영내가 침공당하면 해제된다\n"
        " ·주변 세력의 외교 자세가 변동한다\n"
        " ·주변 국인중의 종속도가 변동한다\n"
        " ·양쪽 세력에 속한 무장의 충성이 변동한다"
    ),
    "14:188:1": (
        "\n전투나 내정 등에서 무장이 능력을 사용하면 경험치를 얻으며,\n"
        "경험치가 일정량 쌓이면 해당 능력이 성장합니다.\n"
        "\n"
    ),
    "14:189:1": (
        "\n전투나 내정 등에서 무장이 능력을 사용하면 경험치를 얻으며,\n"
        "경험치가 일정량 쌓이면 해당 능력이 성장합니다.\n"
        "\n"
    ),
    "14:189:3": (
        "\n　·적 부대를 격파하거나 적 성을 제압한다\n"
        " ·군단장으로서 군단을 지휘한다\n"
        " ·영주나 대관으로서 군을 통치한다\n"
        " ·성하 시설을 건설하거나 정책을 발령한다\n"
        " ·건의나 영내 제책, 조략을 실행한다\n"
        " ·영내 문제를 해결한다\n"
        " ·외교 중개를 맡는다\n"
        " ·감장을 수여하여 별호를 얻게 한다\n"
        "  ※경험치가 아니라 능력이 직접 상승한다\n"
        " ·직담 \"교련\"에 성공한다(무장 등용 시 발생하기도 한다)"
    ),
    "14:190:1": (
        "\n세력 목표로\n"
        "성하 시설 건설이나 영지 확장 등이 제안되기도 합니다.\n"
        "\n"
        "제안된 내용을 기한 안에 달성하면 보상을 얻을 수 있으므로\n"
        "달성을 노려 보는 것도 좋습니다.\n"
        "※달성하지 못해도 불이익은 없습니다\n"
        "※설정>시나리오에서 OFF로 바꿀 수도 있습니다"
    ),
    "14:191:1": (
        "\n세력을 발전시켜 \"세력 목표\"를 달성하면 보상을 받을 수 있습니다.\n"
        "현재 목표를 달성하면 다음 LV의 목표가 표시됩니다.\n"
        "달성할 수 있을 만한 목표가 있다면 플레이 방향을 정할 때 참고합시다.\n"
        "※시나리오 시작 시 이미 달성한 목표의 보상은 획득한 상태로 시작합니다\n"
        "\n"
    ),
    "14:191:2": "◇보상 내용",
    "14:191:3": (
        "\n　·감장      ... 공적을 세운 무장에게 \"은상\" 명령으로 수여할 수 있다\n"
        "         감장을 받은 무장은 충성과 능력 등이 오른다\n"
        " ·특별 보상 ... 특정 목표 달성 시 획득할 수 있으며 세력 전체에 혜택을 준다\n"
        "         ※획득할 수 있는 목표와 LV는 세력 목표 목록에서 확인할 수 있다"
    ),
    "14:192:1": (
        "\n다이묘나 군단장이 있는 성에서 멀리 떨어진 성은\n"
        "통치 범위 밖이 되어 금전 수입이 크게 줄어듭니다.\n"
        "\n"
        "본거지 이전이나 군단 신설을 통해\n"
        "성이 통치 범위 밖이 되지 않도록 주의합시다.\n"
        "\n"
    ),
    "14:192:3": (
        "\n통치 범위는 다음 화면과 명령에서 확인할 수 있습니다.\n"
        " ·군단 뷰\n"
        " ·\"지행\" 명령\n"
        " ·\"본거지 이전\" 명령\n"
        " ·\"군단\" 명령"
    ),
    "14:193:1": (
        "\n다이묘나 군단장이 있는 성에서 멀리 떨어진 성은\n"
        "통치 범위 밖이 되어 금전 수입이 크게 줄어듭니다.\n"
        "\n"
        "본거지 이전이나 군단 신설을 통해\n"
        "성이 통치 범위 밖이 되지 않도록 주의합시다.\n"
        "※정책 \"전마제\"를 발령하면 통치 범위를 넓힐 수 있습니다\n"
        "\n"
    ),
    "14:193:3": (
        "\n통치 범위는 다음 화면과 명령에서 확인할 수 있습니다.\n"
        " ·군단 뷰\n"
        " ·\"지행\" 명령\n"
        " ·\"본거지 이전\" 명령\n"
        " ·\"군단\" 명령"
    ),
    "14:196:0": "[본거지]",
    "14:197:0": "[본거지의 군]",
    "14:197:2": "◇특징",
    "14:198:0": "[성]",
}
EXPECTED_ARITY = {
    182: 4,
    183: 4,
    184: 4,
    185: 4,
    186: 4,
    188: 4,
    189: 4,
    190: 2,
    191: 4,
    192: 4,
    193: 4,
    196: 4,
    197: 4,
    198: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "14:183:1",
    "14:183:2",
    "14:183:3",
    "14:184:0",
    "14:184:1",
    "14:184:2",
    "14:185:1",
    "14:185:2",
    "14:186:2",
    "14:188:0",
    "14:188:2",
    "14:188:3",
    "14:189:0",
    "14:189:2",
    "14:190:0",
    "14:191:0",
    "14:192:0",
    "14:192:2",
    "14:193:0",
    "14:193:2",
    "14:196:1",
    "14:196:2",
    "14:196:3",
    "14:197:1",
    "14:197:3",
    "14:198:1",
    "14:198:2",
    "14:198:3",
)
PREFILL_COMPANION_DONOR = {
    **{
        f"14:183:{literal_id}": f"14:131:{literal_id}"
        for literal_id in (1, 2, 3)
    },
    **{
        f"14:184:{literal_id}": f"14:132:{literal_id}"
        for literal_id in (0, 1, 2)
    },
    "14:185:1": "14:133:1",
    "14:185:2": "14:133:2",
    "14:186:2": "14:133:2",
    "14:188:0": "14:135:0",
    "14:188:2": "14:135:2",
    "14:188:3": "14:135:3",
    "14:189:0": "14:135:0",
    "14:189:2": "14:135:2",
    "14:190:0": "14:136:0",
    "14:191:0": "14:136:0",
    "14:192:0": "14:137:0",
    "14:192:2": "14:137:2",
    "14:193:0": "14:137:0",
    "14:193:2": "14:137:2",
    **{
        f"14:196:{literal_id}": f"14:140:{literal_id}"
        for literal_id in (1, 2, 3)
    },
    "14:197:1": "14:141:1",
    "14:197:3": "14:141:3",
    **{
        f"14:198:{literal_id}": f"14:142:{literal_id}"
        for literal_id in (1, 2, 3)
    },
}
SEMANTIC_BASE_CONTEXT = {
    182: ("14:129:1", "14:130:2", "14:130:3"),
    183: (),
    184: ("14:132:3",),
    185: ("14:133:0", "14:133:3"),
    186: ("14:133:0", "14:133:1", "14:133:3"),
    188: ("14:135:1",),
    189: ("14:135:1", "14:135:3"),
    190: ("14:136:1",),
    191: ("14:136:0", "14:136:1"),
    192: ("14:137:1", "14:137:3"),
    193: ("14:137:1", "14:137:3"),
    196: (),
    197: ("14:141:0", "14:141:2"),
    198: (),
}
EXPECTED_BASE_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES.update({
    183: ((14, 131),),
    196: ((14, 140),),
    198: ((14, 142),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1331,
    queue_start=0,
    queue_stop=67,
    slice_first="14:182:0",
    slice_last="14:198:0",
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
        (14, record_id) for record_id in range(180, 201)
    ),
    speaker_style=tuple(
        (record_id, "static_colored_help_fragment")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("landmark", "명승"),
        ("country", "국"),
        ("region", "지방"),
        ("relocation", "전봉"),
        ("fief", "지행지"),
        ("desertion", "출분"),
        ("authority", "위풍"),
        ("local faction", "국인중"),
        ("siege", "공성전"),
        ("letter of commendation", "감장"),
        ("alias", "별호"),
        ("direct negotiation", "직담"),
        ("drill", "교련"),
        ("clan target", "세력 목표"),
        ("accolade", "은상"),
        ("governance range", "통치 범위"),
        ("postal system", "전마제"),
        ("main base", "본거지"),
        ("governor", "대관"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary context; three "
        "byte-identical complete records reuse approved completed Base "
        "Korean assemblies, including the split final castle record, while "
        "the remaining records adapt completed Base tutorial wording for "
        "PK-only landmark levels, surrender consequences, siege authority, "
        "commendations, aliases, direct-negotiation drills, tiered clan "
        "targets, special rewards and Postal System range expansion; Base "
        "runtime and VM state are never inherited; landmarks, countries, "
        "regions, relocations, fiefs, desertion, authority, local factions, "
        "sieges, commendations, aliases, direct negotiations, drills, clan "
        "targets, accolades, governance range, the Postal System, main "
        "bases and governors retain established project terms; all gaps, "
        "outer whitespace, headings, line counts, literal arity, "
        "terminators, twenty-eight same-record prefill companions, all "
        "forty-one slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=23,
    pins={
        "expected_queue_universe_sha256":
        "45725189FDBA833067CF645AEC7CB28B6F89EA536635E577CB94F8B8567290F8",
        "expected_queue_slice_sha256":
        "AF14536BA2740A2992BD59A52B3C9D116E5AFEA53314F5E7CD5B8A1927D2E534",
        "expected_prefilled_coordinate_sha256":
        "2C59B0F835AE1C92DE8DED6C5DA3A33C341169AF4076127E517EB9AD9B35A10B",
        "expected_prefill_slice_context_sha256":
        "00D8C959C89475A282D9276341C55E27D6EBA361AFA059D37010217D64CB7351",
        "expected_target_coordinate_sha256":
        "9A3428631A0FCE18E25F653BF0A10A9ED697C423EB8E7123D90EF1B799307F21",
        "expected_source_target_sha256":
        "D1288154C39AAC50E0A4F045E1BDFB75648F6A82823F15C1BD54C3266B443B71",
        "expected_current_target_sha256":
        "0584C343106A3167BF6E621B2BAD098667FECA90B9AB2864831A412B8CFBA699",
        "expected_context_corpus_sha256":
        "A8B4C0F0A377AC68608327123565CF521B16D0A1AB9400163A62722D4EC1CFD4",
        "expected_gap_contract_sha256":
        "97C0B5716DB188B8E8886292E2A11F708FB1A6F5C27C8804BB61B27075CFFA6F",
        "expected_boundary_sha256":
        "4A2F2DE1B78BBDE8CA7052C228B8F2C358027A2486D7DC76F9A8DF991BABC456",
        "expected_runtime_control_sha256":
        "99AD21EF12EDCBD39F8498C85B3DF929B7790D50D91514F5523DBE364B3E58FE",
        "expected_base_search_sha256":
        "8D5746330A6DDA9DAC985476ED490DF98B1A6603F07B922B6E995152E0A87BD3",
        "expected_complete_assembly_sha256":
        "2E352C960B85369A3E99F489FB5DCFA0F9B7C9CF80F9D13E8C173835C9B31E3B",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "6EAAA960DD3EF0B6608C8F30C82B1F16DC750239778A6F9E1B1BD151244679FE",
        "expected_terminology_policy_sha256":
        "13D5D7E0BAAA6F020288C2790378DC4D1D463E940308DA41152BCC46E999E265",
        "expected_translation_policy_sha256":
        "9867CC78077B068DA5A66BE7B11550F1E3A352EEBC7A4F73E3D13AC6423AE182",
        "expected_candidate_sha256":
        "32754328D18643066450743EC4BC26C396387445BB645FF44A97F819E099F18C",
        "expected_combined_slice_candidate_sha256":
        "1A39AC92A40BF11AE42335167566F8CFB0840BACF9CEB7B834217CD2124C2B46",
        "expected_combined_changed_literal_count": 54,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B109_S1331",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1331.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1332.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1333.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B109",
    "queue_row_count": 49,
    "queue_visible_count": 194,
    "queue_first": "14:182:0",
    "queue_last": "14:230:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            183: (14, 131),
            196: (14, 140),
            198: (14, 142),
        },
    )
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
