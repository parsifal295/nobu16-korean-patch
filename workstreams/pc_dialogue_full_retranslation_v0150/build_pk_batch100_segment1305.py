#!/usr/bin/env python3
"""Build source-redacted PK B100 segment 1305 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_BASE_ASSEMBLY = COMMON.BASE.base_and_assembly_evidence
_ORIGINAL_BASE_READ_JSONL = COMMON.BASE.read_jsonl

LEFT_CROSS_COORDINATE = "9:4118:0"
LEFT_CROSS_TRANSLATION = "이것은 "
LEFT_CROSS_DONOR = "manual-neighbor:pk_msggame_B100_S1304"
STATIC_COMPANION_COORDINATE = "9:4118:4"
STATIC_COMPANION_DONOR = "9:3800:4"
RIGHT_CROSS_COORDINATE = "9:4144:5"
RIGHT_CROSS_TRANSLATION = "!"
RIGHT_CROSS_DONOR = "manual-neighbor:pk_msggame_B100_S1306"

TARGET_RECORD_IDS = tuple(range(4118, 4145))
TARGET_COORDINATES = (
    "9:4118:1",
    "9:4118:2",
    "9:4118:3",
    "9:4119:0",
    "9:4120:0",
    "9:4121:0",
    "9:4121:1",
    "9:4121:2",
    "9:4121:3",
    "9:4121:4",
    "9:4122:0",
    "9:4122:1",
    "9:4123:0",
    "9:4123:1",
    "9:4123:2",
    "9:4123:3",
    "9:4124:0",
    "9:4125:0",
    "9:4126:0",
    "9:4126:1",
    "9:4127:0",
    "9:4127:1",
    "9:4128:0",
    "9:4128:1",
    "9:4129:0",
    "9:4129:1",
    "9:4130:0",
    "9:4130:1",
    "9:4131:0",
    "9:4131:1",
    "9:4132:0",
    "9:4132:1",
    "9:4133:0",
    "9:4133:1",
    "9:4133:2",
    "9:4134:0",
    "9:4134:1",
    "9:4135:0",
    "9:4135:1",
    "9:4136:0",
    "9:4136:1",
    "9:4137:0",
    "9:4138:0",
    "9:4138:1",
    "9:4139:0",
    "9:4139:1",
    "9:4139:2",
    "9:4139:3",
    "9:4140:0",
    "9:4140:1",
    "9:4140:2",
    "9:4140:3",
    "9:4141:0",
    "9:4141:1",
    "9:4141:3",
    "9:4142:0",
    "9:4142:2",
    "9:4142:4",
    "9:4143:0",
    "9:4143:1",
    "9:4143:2",
    "9:4144:0",
    "9:4144:1",
    "9:4144:2",
    "9:4144:3",
    "9:4144:4",
)
TRANSLATIONS = {
    "9:4118:1": "오니시마즈",
    "9:4118:2": "의 부대인가……!\n",
    "9:4118:3": "오토모",
    "9:4119:0": "을(를) 격파하라",
    "9:4120:0": "을(를) 파괴하라",
    "9:4121:0": "총사기를",
    "9:4121:1": "이상으로 유지하며",
    "9:4121:2": "개의 목표를 달성하라(",
    "9:4121:3": " / ",
    "9:4121:4": ")",
    "9:4122:0": "총사기를",
    "9:4122:1": "이상으로 유지하며 모든 목표를 달성하라",
    "9:4123:0": "아군 부대를 괴멸시키지 말고",
    "9:4123:1": "개의 목표를 달성하라(",
    "9:4123:2": " / ",
    "9:4123:3": ")",
    "9:4124:0": (
        "아군 부대를 괴멸시키지 말고 모든 목표를 달성하라"
    ),
    "9:4125:0": "을(를) 협격하여 격파하라",
    "9:4126:0": "총사기를",
    "9:4126:1": "이상으로 끌어올려라",
    "9:4127:0": "이번 공성에는 한 가지 계책이 있사옵니다",
    "9:4127:1": (
        "\n일이 뜻대로 풀린다면\n"
        "큰 피해 없이 성을 함락할 수도 있사옵니다……"
    ),
    "9:4128:0": (
        "저 성주는 방어를 휘하에만 의지하는 모양입니다…\n"
    ),
    "9:4128:1": (
        "부터 격파한다면\n"
        "수성 측은 전의를 잃고 틀림없이 항복할 것입니다"
    ),
    "9:4129:0": "성주 「",
    "9:4129:1": (
        "」은(는) 충신이라 하기는 어렵습니다…\n"
        "전의가 높은 충의지사부터 격파한다면\n"
        "남은 장수들은 싸움보다 굴복을 택할 것입니다"
    ),
    "9:4130:0": "수성 측의 노림수는 「",
    "9:4130:1": (
        "」 등을 이용한 반격입니다…\n"
        "이들을 파괴해 적의 승산을 없앤다면\n"
        "수성 측에는 항복밖에 남지 않을 것입니다"
    ),
    "9:4131:0": (
        "수성 측도 자신들이 불리하다는 것을 알고 있습니다"
    ),
    "9:4131:1": (
        "\n성안 최고의 맹장을 쓰러뜨려 적의 사기를 꺾는다면\n"
        "수성 측도 서둘러 항복을 택할 것입니다"
    ),
    "9:4132:0": "수성 측은 「",
    "9:4132:1": (
        "」 등으로 방비를 굳히려는 모양입니다…\n"
        "준비가 끝나기 전에 이들을 파괴한다면\n"
        "성안 사람들도 항복을 고려할 것입니다"
    ),
    "9:4133:0": "보고드립니다!\n계획대로 성주 「",
    "9:4133:1": "」이(가)\n항복을 청해 왔습니다",
    "9:4133:2": "!",
    "9:4134:0": (
        "(이)가 격파되어\n"
        "우리는 수비의 핵심을 잃었습니다"
    ),
    "9:4134:1": (
        "…\n"
        "이 성도 이제 끝이라고 판단했습니다"
    ),
    "9:4135:0": (
        "우리는 애초에 이 가문에 충성을 다할 의리도 없습니다…\n"
        "사수를 주장하던 자들도 이미"
    ),
    "9:4135:1": (
        "했고\n"
        "이런 싸움에서 목숨을 버리고 싶지는 않습니다"
    ),
    "9:4136:0": "반격의 핵심이던 「",
    "9:4136:1": (
        "」이(가)\n"
        "이토록 쉽게 파괴되다니…\n"
        "아무래도 귀가의 힘을 잘못 판단한 듯합니다"
    ),
    "9:4137:0": (
        "의 방비가 완전히 갖춰지기도 전에\n"
        "돌파를 허용하고 말다니…\n"
        "아무래도 귀가의 힘을 잘못 판단한 듯합니다"
    ),
    "9:4138:0": (
        "이 전력 차를 뒤집기는 이제 어렵습니다…\n"
        "마지막으로 의지하던 「"
    ),
    "9:4138:1": (
        "」마저 물러난 지금\n"
        "더 버텨도 아무 소용이 없습니다"
    ),
    "9:4139:0": "분하지만, ",
    "9:4139:1": "의 성문을 열겠습니다",
    "9:4139:2": (
        "…\n"
        "저희의 항복을 받아 주시겠습니까"
    ),
    "9:4139:3": "?",
    "9:4140:0": "을(를) 넘겨드리고,\n성주 「",
    "9:4140:1": "」도 포박에 응하겠습니다",
    "9:4140:2": (
        "…\n"
        "부디 제 부하들이 물러나는 것만은"
    ),
    "9:4140:3": "허락해 주십시오…",
    "9:4141:0": "부디 귀순을 허락해 주십시오!\n이 「",
    "9:4141:1": "」, 성심성의껏 모시겠습니다",
    "9:4141:3": "도 원하시는 대로 처분하십시오…",
    "9:4142:0": "현명한 판단이로군",
    "9:4142:2": "의 항복을 받아들이겠다",
    "9:4142:4": "은(는) 이 자리에서 포박에 응하라",
    "9:4143:0": "…\n",
    "9:4143:1": "의 항복을 허락한다",
    "9:4143:2": "\n그대 부하들의 안전도 보장하겠다",
    "9:4144:0": "물론, 기꺼이 환영한다",
    "9:4144:1": "!\n",
    "9:4144:2": "와(과)",
    "9:4144:3": "이(가) 항복해 준다면\n",
    "9:4144:4": "도 한층 더 번영할 것이다",
}
EXPECTED_ARITY = {
    4118: 5,
    4119: 1,
    4120: 1,
    4121: 5,
    4122: 2,
    4123: 4,
    4124: 1,
    4125: 1,
    4126: 2,
    4127: 2,
    4128: 2,
    4129: 2,
    4130: 2,
    4131: 2,
    4132: 2,
    4133: 3,
    4134: 2,
    4135: 2,
    4136: 2,
    4137: 1,
    4138: 2,
    4139: 4,
    4140: 4,
    4141: 4,
    4142: 5,
    4143: 3,
    4144: 6,
}
SEMANTIC_BASE_CONTEXT = {
    4118: tuple(f"9:3800:{literal_id}" for literal_id in range(5)),
    4119: ("9:448:0",),
    4120: ("9:446:0",),
    4121: ("13:325:0",),
    4122: ("13:325:0",),
    4123: ("9:449:0",),
    4124: ("9:449:0",),
    4125: ("9:3638:0", "9:448:0"),
    4126: ("9:444:0",),
    4127: ("15:896:0",),
    4128: ("7:1367:0",),
    4129: ("7:1369:0",),
    4130: ("7:1586:1",),
    4131: ("7:1367:0",),
    4132: ("7:1458:0",),
    4133: ("13:436:0", "13:437:0"),
    4134: ("9:1191:0", "13:437:0"),
    4135: ("9:1191:0", "13:437:0"),
    4136: ("9:1191:0", "13:437:0"),
    4137: ("9:1191:0", "13:437:0"),
    4138: ("9:1191:0", "13:437:0"),
    4139: ("6:4650:0", "7:748:1"),
    4140: ("6:4650:0", "7:748:1"),
    4141: ("6:4650:0", "7:748:1"),
    4142: ("13:436:0", "6:1591:0"),
    4143: ("13:436:0", "6:1591:0"),
    4144: ("13:436:0", "6:1591:0"),
}
EMPTY_BASE_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES = {
    **EMPTY_BASE_MATCHES,
    4118: ((9, 3800), (17, 31)),
}
EXPECTED_CONTROLS_BY_RECORD = {
    4118: ((), ()),
    4119: ((), ("02AA32",)),
    4120: ((), ()),
    4121: ((), ("0234", "0233", "0232", "0233")),
    4122: ((), ("0234",)),
    4123: ((), ("0233", "0232", "0233")),
    4124: ((), ()),
    4125: ((), ("02AA32",)),
    4126: ((), ("0232",)),
    4127: ((376,), ()),
    4128: ((754,), ("024833",)),
    4129: ((610, 730), ("024833",)),
    4130: ((778,), ()),
    4131: ((610, 226), ()),
    4132: ((610, 730), ()),
    4133: ((628,), ("024833",)),
    4134: ((634,), ("024833",)),
    4135: ((160, 754), ()),
    4136: ((568,), ()),
    4137: ((568,), ()),
    4138: ((556, 730), ("024833",)),
    4139: ((142, 1066), ("026432",)),
    4140: ((1, 310, 1168), ("026432",)),
    4141: ((310,), ("024635", "026432")),
    4142: (
        (568, 730, 1066, 514, 8, 1048),
        ("026432",),
    ),
    4143: ((1072, 1162, 514, 148), ("026432",)),
    4144: ((148, 8, 610), ("026432", "025032")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1305,
    queue_start=67,
    queue_stop=134,
    slice_first="9:4118:1",
    slice_last="9:4144:4",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(
        LEFT_CROSS_COORDINATE,
        STATIC_COMPANION_COORDINATE,
        RIGHT_CROSS_COORDINATE,
    ),
    prefill_companion_donor={
        LEFT_CROSS_COORDINATE: LEFT_CROSS_DONOR,
        STATIC_COMPANION_COORDINATE: STATIC_COMPANION_DONOR,
        RIGHT_CROSS_COORDINATE: RIGHT_CROSS_DONOR,
    },
    hidden_current_companion_coordinates=(
        "9:4141:2",
        "9:4142:1",
        "9:4142:3",
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        1, 8, 142, 148, 160, 226, 310, 376, 514, 556, 568,
        610, 628, 634, 730, 754, 778, 1048, 1066, 1072,
        1162, 1168,
    ),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3798, 4147)
    ),
    speaker_style=(
        (4118, "fearful_historical_force_recognition"),
        (4119, "system_dynamic_unit_defeat_objective"),
        (4120, "system_dynamic_facility_destroy_objective"),
        (4121, "system_morale_partial_target_objective"),
        (4122, "system_morale_all_target_objective"),
        (4123, "system_no_loss_partial_target_objective"),
        (4124, "system_no_loss_all_target_objective"),
        (4125, "system_dynamic_pincer_defeat_objective"),
        (4126, "system_total_morale_objective"),
        (4127, "archaic_respectful_siege_plan"),
        (4128, "formal_retainer_first_surrender_plan"),
        (4129, "formal_disloyal_castellan_surrender_plan"),
        (4130, "formal_counterattack_denial_surrender_plan"),
        (4131, "formal_champion_defeat_surrender_plan"),
        (4132, "formal_defense_denial_surrender_plan"),
        (4133, "formal_castellan_surrender_report"),
        (4134, "weary_defensive_pillar_loss_surrender"),
        (4135, "weary_disloyal_retainer_surrender"),
        (4136, "weary_counterattack_facility_loss_surrender"),
        (4137, "weary_defense_facility_loss_surrender"),
        (4138, "weary_champion_loss_surrender"),
        (4139, "reluctant_castle_opening_plea"),
        (4140, "formal_castellan_capture_plea"),
        (4141, "earnest_defection_plea"),
        (4142, "lordly_strict_surrender_acceptance"),
        (4143, "lordly_protective_surrender_acceptance"),
        (4144, "lordly_welcoming_surrender_acceptance"),
    ),
    terminology_policy=(
        ("historical sobriquet", "오니시마즈"),
        ("historical force", "오토모"),
        ("battle-wide morale", "총사기"),
        ("two-sided attack", "협격"),
        ("castle attack", "공성"),
        ("castle defenders", "수성 측"),
        ("castle preparedness", "방비"),
        ("castle surrender", "항복"),
        ("opening a castle", "성문을 열다"),
        ("submit to binding", "포박에 응하다"),
        ("defection", "귀순"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record arrays were manually reviewed as auxiliary evidence; "
        "the exact completed Base record supplies the complete historical "
        "force-recognition assembly only, while every other completed Base "
        "reference supplies semantic wording and terminology without "
        "inheriting Base runtime or VM state; 오니시마즈, 오토모, 총사기, "
        "협격, 공성, 수성 측, 방비, 항복, 귀순 and 포박 terminology follows "
        "the project glossary and completed corpus; system objectives, "
        "archaic proposals, formal reports, weary surrender pleas and "
        "lordly acceptance registers remain distinct; dynamic counts, "
        "officers, forces, castles and facilities, color spans, calls 1, 8, "
        "142, 148, 160, 226, 310, 376, 514, 556, 568, 610, 628, 634, 730, "
        "754, 778, 1048, 1066, 1072, 1162 and 1168, protected outer "
        "whitespace, hidden newline literals, line shapes, gaps, terminators, "
        "the static Base companion and both split-record neighbor companions "
        "are guarded; all pins, two-run reproduction, tamper rejection, "
        "mutual neighbors, reverse overlays, outside-scope identity and "
        "Steam read-only state are also guarded"
    ),
    expected_changed_literal_count=49,
    pins={
        "expected_queue_universe_sha256":
        "16465EB37A9E84E6A85010F206205CC0F89F8F62024BE6738F8C4E55821EFBC3",
        "expected_queue_slice_sha256":
        "139A001F480935FFA1F93016F5514C50F6962A1659BBCA3FF5C0AEC251B70B81",
        "expected_prefilled_coordinate_sha256":
        "42955C0EE72F41BB904519CBAC53033B054A35CA1586F6A4D88698FB13BE1465",
        "expected_prefill_slice_context_sha256":
        "5FFEF2853244EDB6623F4E3D4BC238D46B796E83BAC8222F6FDBA1ED1C571B39",
        "expected_target_coordinate_sha256":
        "D7F511F0FB7B57DC597839F6152C6EEDAD8FA098C169FCAC1B545CA231D2351F",
        "expected_source_target_sha256":
        "8AA2E529BBE7D45011C7EFEFFF8BA2A588269370CBC2B1FF25F044EEF56BA071",
        "expected_current_target_sha256":
        "08477ABD64EBD2D3893B91B82AC6D7289278F84602F973058677EE6A72A1D281",
        "expected_context_corpus_sha256":
        "F0C52F91A97DF577CBD26FB29DCED18C22EAB215EB4433B1FE13BA7E8BB28E82",
        "expected_gap_contract_sha256":
        "9B14060A4526843599A262164CD210D78DADEC9715C8D405433A600938A1A0B0",
        "expected_boundary_sha256":
        "C3AFC340FEB93D937D6C671C7E9827588A00E9428E8C8A835C5EA45FB6277BF7",
        "expected_runtime_control_sha256":
        "BA14AF6017C8E8402B6E84539FA7E08CE8C98CA39A6F18C176EA3C7497229177",
        "expected_base_search_sha256":
        "8A7C5AD90D7FCE642E2183346D9298E24134E3A8935124BB156B2A0517A0FD27",
        "expected_complete_assembly_sha256":
        "CC119231959B182E8DC4237B7E87FA5B985112AF08E209F182F66751880D3D6C",
        "expected_call_graph_sha256":
        "6F96BAB4EB9CD1F2CFF853D74055799D459AEB949221C34BCCEE3697A2A6467A",
        "expected_speaker_style_sha256":
        "F3E6ED72C391BC0E3BC33157582F79FF2D21D5FEFC8E4F5AE38265519DD4AECA",
        "expected_terminology_policy_sha256":
        "A45E8CFEADB65D1F41FFCFA614AD9A745056164D885F05CC375E2E08F78691AD",
        "expected_translation_policy_sha256":
        "AAE8CDF3F9B7806F6DCF7559856CDC5EF5313C85C1CC21E9FD5234C5094D0CFB",
        "expected_candidate_sha256":
        "FCE60684C2FFE86C40A839F23B0823FD23FA172B52D3DABA02C0955DE660C3DC",
        "expected_combined_slice_candidate_sha256":
        "D4FC2097C8B9144C231659FF44562DE5C406E4D8A73C358B30B1E90EB18B46D5",
        "expected_combined_changed_literal_count": 50,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B100_S1305",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B100_S1305.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B100_S{segment}.private.v1.jsonl"
        for segment in (1304, 1306)
    ),
    "queue_batch_id": "pk_msggame-B100",
    "queue_row_count": 106,
    "queue_visible_count": 197,
    "queue_first": "9:4083:0",
    "queue_last": "12:45:5",
})


def base_and_assembly_evidence(
    prepared: object,
    records_by_label: dict[tuple[str, str], object],
) -> tuple[tuple[object, ...], tuple[object, ...]]:
    """Model split neighbors and one static prefill in full assemblies."""

    neighbor_contracts = (
        (
            COMMON.DECISIONS_ROOT
            / "pk_msggame_B100_S1304.private.v1.jsonl",
            LEFT_CROSS_COORDINATE,
            LEFT_CROSS_TRANSLATION,
            "S1304",
        ),
        (
            COMMON.DECISIONS_ROOT
            / "pk_msggame_B100_S1306.private.v1.jsonl",
            RIGHT_CROSS_COORDINATE,
            RIGHT_CROSS_TRANSLATION,
            "S1306",
        ),
    )
    for path, coordinate, translation, label in neighbor_contracts:
        if not path.is_file():
            continue
        rows = {
            str(row["coordinate"]): row
            for row in _ORIGINAL_BASE_READ_JSONL(path)
        }
        neighbor = rows.get(coordinate)
        if (
            neighbor is None
            or neighbor.get("semantic_review") != "approved"
            or neighbor.get("runtime_review") != "pending"
            or str(neighbor.get("translation")) != translation
        ):
            raise RuntimeError(
                f"segment 1305 reciprocal {label} translation drifted"
            )

    synthetic_neighbors = (
        {
            "coordinate": LEFT_CROSS_COORDINATE,
            "translation": LEFT_CROSS_TRANSLATION,
            "semantic_review": "approved",
            "runtime_review": "pending",
            "base_exact_reuse_prefill": {
                "base_coordinate": LEFT_CROSS_DONOR,
                "runtime_promotion_authorized": False,
            },
        },
        {
            "coordinate": RIGHT_CROSS_COORDINATE,
            "translation": RIGHT_CROSS_TRANSLATION,
            "semantic_review": "approved",
            "runtime_review": "pending",
            "base_exact_reuse_prefill": {
                "base_coordinate": RIGHT_CROSS_DONOR,
                "runtime_promotion_authorized": False,
            },
        },
    )

    def compatible_read_jsonl(path: Path) -> list[dict[str, object]]:
        rows = _ORIGINAL_BASE_READ_JSONL(path)
        if path != COMMON.PREFILL:
            return rows
        cross_coordinates = {
            LEFT_CROSS_COORDINATE,
            RIGHT_CROSS_COORDINATE,
        }
        if any(
            str(row["coordinate"]) in cross_coordinates for row in rows
        ):
            raise RuntimeError(
                "segment 1305 cross coordinate became prefilled"
            )
        compatible: list[dict[str, object]] = []
        for row in rows:
            copied = dict(row)
            if copied.get("coordinate") == STATIC_COMPANION_COORDINATE:
                if copied.get("runtime_review") != "not_required":
                    raise RuntimeError(
                        "segment 1305 static companion review drifted"
                    )
                copied["runtime_review"] = "pending"
            compatible.append(copied)
        return [*compatible, *synthetic_neighbors]

    original_read_jsonl = COMMON.BASE.read_jsonl
    COMMON.BASE.read_jsonl = compatible_read_jsonl
    try:
        base, assembly = _ORIGINAL_BASE_ASSEMBLY(
            prepared, records_by_label
        )
    finally:
        COMMON.BASE.read_jsonl = original_read_jsonl

    adjusted: list[tuple[object, ...]] = []
    for evidence in assembly:
        owners = list(evidence[1])
        if evidence[0] == 4118:
            if (
                owners[0] != "base_exact_prefill_runtime_pending"
                or owners[4] != "base_exact_prefill_runtime_pending"
            ):
                raise RuntimeError(
                    "segment 1305 left split ownership drifted"
                )
            owners[0] = "neighbor_segment_manual_runtime_pending"
            owners[4] = "base_exact_prefill_runtime_not_required"
        elif evidence[0] == 4144:
            if owners[5] != "base_exact_prefill_runtime_pending":
                raise RuntimeError(
                    "segment 1305 right split ownership drifted"
                )
            owners[5] = "neighbor_segment_manual_runtime_pending"
        adjusted.append((evidence[0], tuple(owners), *evidence[2:]))
    return base, tuple(adjusted)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {4118: (9, 3800)})
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        base_and_assembly_evidence,
    )


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
