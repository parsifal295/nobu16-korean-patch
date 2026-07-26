#!/usr/bin/env python3
"""Build source-redacted PK B077 segment 1237 residual decisions."""

from pathlib import Path

from build_pk_batch077_common import make_config, run


SCRIPT = Path(__file__).resolve()
TARGET_RECORD_IDS = tuple(range(1095, 1102))
CONFIG = make_config(
    script=SCRIPT,
    segment=1237,
    queue_start=134,
    queue_stop=199,
    slice_first="8:1055:0",
    slice_last="8:1101:3",
    target_coordinates=(
        "8:1095:0",
        "8:1095:1",
        "8:1095:2",
        "8:1096:0",
        "8:1096:1",
        "8:1096:2",
        "8:1097:0",
        "8:1097:1",
        "8:1097:2",
        "8:1098:0",
        "8:1098:1",
        "8:1099:0",
        "8:1099:1",
        "8:1099:2",
        "8:1099:3",
        "8:1100:0",
        "8:1100:1",
        "8:1100:2",
        "8:1100:3",
        "8:1100:4",
        "8:1101:0",
        "8:1101:1",
        "8:1101:2",
        "8:1101:3",
    ),
    translations={
        "8:1095:0": "주손지",
        "8:1095:1": (
            "를 수리하며 예로부터 전해진 공법을\n"
            "목수들이 익혔습니다"
        ),
        "8:1095:2": "\n이 공법을 성하 보수에도 활용하라",
        "8:1096:0": "고토쿠인",
        "8:1096:1": (
            "이 옛 광채를 되찾아\n"
            "본가의 위광도 널리 퍼지고 있습니다"
        ),
        "8:1096:2": "\n분명 국인중도 우리 편으로 기울 것입니다",
        "8:1097:0": "도다이지",
        "8:1097:1": (
            "를 재건하자\n"
            "백성들의 눈빛도 전보다 한층 밝아졌습니다"
        ),
        "8:1097:2": "!\n일하는 모습도 놀라울 정도입니다",
        "8:1098:0": "이세 신궁",
        "8:1098:1": (
            "에 기진한 일로\n"
            "조정에서도 감사를 표한 덕인지\n"
            "본가의 위세가 널리 퍼지고 있습니다"
        ),
        "8:1099:0": "이즈모 대사",
        "8:1099:1": "의 가호 덕분",
        "8:1099:2": "인지\n병사들의 기세가 좋아졌습니다",
        "8:1099:3": "\n그 힘을 전장에서 크게 발휘할 것입니다",
        "8:1100:0": "이쓰쿠시마 신사",
        "8:1100:1": (
            "를 재흥한 뒤로\n"
            "가신들의 책략이 한층 날카로워졌습니다"
        ),
        "8:1100:2": "\n이 또한 무나카타 대신의 가호",
        "8:1100:3": "일지도 모릅니다",
        "8:1100:4": "!",
        "8:1101:0": "다자이후 덴만구",
        "8:1101:1": "의 영험 덕분",
        "8:1101:2": (
            "인지\n"
            "가신들이 영지를 다스리는 솜씨도\n"
            "더욱 놀라워졌습니다"
        ),
        "8:1101:3": "!",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        1095: 3,
        1096: 3,
        1097: 3,
        1098: 2,
        1099: 4,
        1100: 5,
        1101: 4,
    },
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        1095: ("8:1083:0",),
        1096: ("8:1084:0",),
        1097: ("8:1085:0",),
        1098: ("8:1086:0",),
        1099: ("8:1087:0",),
        1100: ("8:1088:0",),
        1101: ("8:1089:0",),
    },
    expected_base_raw_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_base_literal_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_base_masked_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_controls_by_record={
        1095: ((712, 1066), ()),
        1096: ((712, 514), ()),
        1097: ((178, 520), ()),
        1098: ((712,), ()),
        1099: ((1174, 628, 286), ()),
        1100: ((178, 1174, 1114), ()),
        1101: ((1174, 628), ()),
    },
    source_call_roots=(178, 286, 514, 520, 628, 712, 1066, 1114, 1174),
    boundary_record_keys=tuple(
        (8, record_id)
        for record_id in (
            1054, 1055, 1082, 1083, 1084, 1085, 1086, 1087,
            1088, 1089, 1090, 1094, 1095, 1096, 1097, 1098,
            1099, 1100, 1101, 1102,
        )
    ),
    speaker_style=(
        (1095, "temple_repair_technique_imperative_report"),
        (1096, "temple_restoration_authority_report"),
        (1097, "temple_reconstruction_popular_morale_report"),
        (1098, "shrine_donation_clan_prestige_report"),
        (1099, "shrine_blessing_soldier_morale_report"),
        (1100, "shrine_restoration_stratagem_blessing_report"),
        (1101, "shrine_blessing_domain_governance_report"),
    ),
    terminology_policy=(
        ("Chusonji", "주손지"),
        ("Kotokuin", "고토쿠인"),
        ("Todaiji", "도다이지"),
        ("Ise Jingu", "이세 신궁"),
        ("Izumo Taisha", "이즈모 대사"),
        ("Itsukushima Jinja", "이쓰쿠시마 신사"),
        ("Dazaifu Tenmangu", "다자이후 덴만구"),
        ("donation to shrine", "기진"),
        ("provincial warriors", "국인중"),
        ("Munakata deity", "무나카타 대신"),
        ("divine blessing and efficacy", "가호/영험"),
        ("castle-town works", "성하 보수"),
    ),
    basis=(
        "pristine PK Japanese is authoritative and complete PK English, "
        "Simplified Chinese and Traditional Chinese context was manually "
        "reviewed; seven PK-only shrine and temple achievement records have "
        "no raw, literal or operand-masked Base match, so seven completed Base "
        "achievement records supply terminology and semantic wording only "
        "while Base runtime and VM state are never inherited; all twenty-four "
        "residuals form seven complete records without prefill or hidden "
        "companions; historically specific temple and shrine names, shrine "
        "donation, provincial-warrior, deity, blessing and castle-town terms, "
        "imperative and formal report registers, dynamic fragments, calls, "
        "protected whitespace, gaps, boundaries, two-run reproduction, "
        "tamper rejection, reverse overlays, outside-scope identity and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=14,
    pins={
        "expected_queue_universe_sha256":
        "A773BC2A346A94EF11442275CC15B7EC79729ABC130B1FB137130468C8D5B917",
        "expected_queue_slice_sha256":
        "C1C9CA081AD6061165060E41B88EAA42C6E38BC8EC3D8B83672A8939F16E6935",
        "expected_prefilled_coordinate_sha256":
        "71DD6D9FF8408FB016851ECE3848C571255D758063854DCCE4943E2D9A4599B8",
        "expected_prefill_slice_context_sha256":
        "B236E8C06062C5BE481DE6DC5EC7D30A539CD1C1BAD5EAD5552CC09A2B5B7A5D",
        "expected_target_coordinate_sha256":
        "4CC2C584F1D935BBB254514525CFBC340C757741611DF0BD62456A7404995AF6",
        "expected_source_target_sha256":
        "7A2EDFA547AF19FADE71B72B08C69DDB409A74F6C30830113BAEA7012C31C4EF",
        "expected_current_target_sha256":
        "5C4E24F6071648FB6F2B3868B8A103325B610F53728FCF4344EECB95174863B1",
        "expected_context_corpus_sha256":
        "BC6AD64CCD8C2F358FF09BB1BF406A04308A1A9B4F3BBA75A80BEDE5FCC75621",
        "expected_gap_contract_sha256":
        "CB9C63630E3CC472F841E2AE47D1BA96E470BA2A2E0F40416FDF1DC0F8736C8E",
        "expected_boundary_sha256":
        "4CF5BF7EB8233E5BED8714F6B9F41AD2932AA8B5406FE1553911D9066536813B",
        "expected_runtime_control_sha256":
        "4ABADE1872C815A3D67CB52A4A5ABBC331F38DA60B0EE629CAAEBB663A9B86E6",
        "expected_base_search_sha256":
        "8367114540F2A5537B4FDCA0BFA14602378B39EE402FEBB7A4B423E44AFFB359",
        "expected_complete_assembly_sha256":
        "3918FD27A829372F61EBB5C3467F67F335531E7AEC0DFD985DC31D74134A5B60",
        "expected_call_graph_sha256":
        "33CFE074FD8D88F21071C4EA6CCE1853BDBF72F72B56218B4B4E6C934DD57090",
        "expected_speaker_style_sha256":
        "B27205F376B7FFD175CBBE126CEEB52F4EB7C7CC65737E297212DBC881D747ED",
        "expected_terminology_policy_sha256":
        "A772973DD2F06C872DC61AC61685D2C901781982EC76F2B66D7E15A653DF8900",
        "expected_translation_policy_sha256":
        "351211EBAEDF44CBD457B8F41A687491F7E922E6526DC93D157D816AAF74C2E0",
        "expected_candidate_sha256":
        "218B1A7AFF568649607E056B4AE9B7397188406679994AE1C405AC3CA3EF9807",
        "expected_combined_slice_candidate_sha256":
        "84BA3C9D7BDA17DA754570E1644C731E88E6624E644512EA7C668D74B7F3E68E",
        "expected_combined_changed_literal_count": 54,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
