#!/usr/bin/env python3
"""Build source-redacted PK B035 segment 1118 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch035_segment1116.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B035_S1118.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B034_S1113.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B034_S1114.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B034_S1115.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B035_S1116.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B035_S1117.private.v1.jsonl",
)

SEGMENT = 1118
QUEUE_BATCH_ID = "pk_msggame-B035"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:3409:3",
    "6:3410:0",
    "6:3410:2",
    "6:3410:3",
    "6:3411:0",
    "6:3411:1",
    "6:3413:0",
    "6:3413:1",
    "6:3413:2",
    "6:3414:0",
    "6:3414:1",
    "6:3414:2",
    "6:3415:1",
    "6:3416:0",
    "6:3416:2",
    "6:3417:0",
    "6:3417:1",
    "6:3417:2",
    "6:3418:0",
    "6:3418:1",
    "6:3418:2",
    "6:3420:0",
    "6:3420:1",
    "6:3428:0",
    "6:3429:0",
    "6:3431:0",
    "6:3436:1",
    "6:3440:0",
)
TRANSLATIONS = {
    "6:3409:3": (
        "인 이상, 어떤 수를\n"
        "써서라도 가문을 번영시켜 보이겠"
    ),
    "6:3410:0": ", 반드시",
    "6:3410:2": ".\n",
    "6:3410:3": "은(는) 나에게",
    "6:3411:0": (
        "우리 가문을 이끄는 일을 일임받다니\n"
        "더없는 기쁨과 함께,"
    ),
    "6:3411:1": (
        "책임의 무게에\n"
        "마음이 절로 다잡히는 기분"
    ),
    "6:3413:0": (
        "이런, 이런. 살날이 얼마 남지 않은 몸으로 무거운 짐을\n"
        "지게 될 줄이야… 허나\n"
    ),
    "6:3413:1": "의",
    "6:3413:2": "기대에는 부응해 보이",
    "6:3414:0": ", 안심하고",
    "6:3414:1": ".\n",
    "6:3414:2": "은(는) 이",
    "6:3415:1": ".\n반드시",
    "6:3416:0": "조금만 더",
    "6:3416:2": "만…\n알겠",
    "6:3417:0": ", 안심하고",
    "6:3417:1": ".\n이",
    "6:3417:2": ",",
    "6:3418:0": ", 이",
    "6:3418:1": ", 목숨을 걸고\n반드시",
    "6:3418:2": "의 존속과 번영을\n이루어 보이",
    "6:3420:0": "뒷일은",
    "6:3420:1": "에게",
    "6:3428:0": "이(가)",
    "6:3429:0": "의",
    "6:3431:0": "의",
    "6:3436:1": "의 눈에 든 것이야말로 망외의 기쁨",
    "6:3440:0": "이럴 수가,",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3409,
    3410,
    3411,
    3413,
    3414,
    3415,
    3416,
    3417,
    3418,
    3420,
    3428,
    3429,
    3431,
    3436,
    3440,
)
SLICE_RECORD_IDS = tuple(range(3409, 3441))
BOUNDARY_RECORD_IDS = (3408, 3441)
CURRENT_GAP_DIVERGENT_RECORD_IDS = (3421,)
BOUNDARY_COMPANION_COORDINATES = (
    "6:3409:0",
    "6:3409:1",
    "6:3409:2",
)
BASE_RECORD_MAPPING = {
    record_id: record_id - 7 for record_id in SLICE_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{int(coordinate.split(':')[1]) - 7}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
DIVERGENT_CALL_RECORD_IDS = (
    *range(3409, 3419),
    3420,
    3421,
)
EXACT_BASE_RECORD_IDS = (
    3419,
    *range(3422, 3441),
)

EXPECTED_TARGET_ASSEMBLIES = {
    3409: (
        "안심하고",
        ", 이",
        "이(가)\n당주라니",
        "인 이상, 어떤 수를\n써서라도 가문을 번영시켜 보이겠",
    ),
    3410: (
        ", 반드시",
        "기대에\n부응할 것을 이 자리에서 맹세하",
        ".\n",
        "은(는) 나에게",
    ),
    3411: (
        "우리 가문을 이끄는 일을 일임받다니\n더없는 기쁨과 함께,",
        "책임의 무게에\n마음이 절로 다잡히는 기분",
    ),
    3413: (
        "이런, 이런. 살날이 얼마 남지 않은 몸으로 무거운 짐을\n"
        "지게 될 줄이야… 허나\n",
        "의",
        "기대에는 부응해 보이",
    ),
    3414: (
        ", 안심하고",
        ".\n",
        "은(는) 이",
        "이(가)\n목숨을 바쳐서라도 지켜 보이",
    ),
    3415: (
        "뒷일은",
        ".\n반드시",
        "의 기대에 부응하여\n",
        "을(를) 강대하게 키워 보이",
    ),
    3416: (
        "조금만 더",
        "을(를) 주군으로\n받들고 싶었",
        "만…\n알겠",
        ", 힘이 닿는 데까지 다하",
    ),
    3417: (
        ", 안심하고",
        ".\n이",
        ",",
        "을(를)\n목숨을 걸고서라도 지켜 보이",
    ),
    3418: (
        ", 이",
        ", 목숨을 걸고\n반드시",
        "의 존속과 번영을\n이루어 보이",
    ),
    3420: (
        "뒷일은",
        "에게",
        "\n우리 가문을 번영으로 이끌",
    ),
    3428: (
        "이(가)",
        "의 임기에 따른\n충성 보정을 잃습니다. 계속하시겠습니까?",
    ),
    3429: (
        "의",
        "이(가) 제일이라고!?\n",
        "의 은혜가 뼛속까지 사무치는군…\n"
        "좋아, 올해도 죽어라 일해 주마!",
    ),
    3431: (
        "의",
        "이(가) 제일인가…\n"
        "쑥스럽기는 하나 기쁜 일이로군\n"
        "올해도 힘써,",
        "의 힘이 되어 드리겠소이다",
    ),
    3436: (
        "이(가) 훈공 1위입니까, 감사드립니다\n"
        "낭중지추라 하듯 낮은 자리에 있으면서도\n",
        "의 눈에 든 것이야말로 망외의 기쁨",
    ),
    3440: (
        "이럴 수가,",
        "이(가) 제일이라니…\n"
        "아직도 실감이 나지 않으나\n"
        "기대를 받는 것은 기쁜 일이로군",
    ),
}
BOUNDARY_COMPANION_TRANSLATIONS = {
    coordinate: EXPECTED_TARGET_ASSEMBLIES[3409][
        int(coordinate.split(":")[2])
    ]
    for coordinate in BOUNDARY_COMPANION_COORDINATES
}
EXPECTED_TARGET_RUNTIME = {
    3409: (
        (
            "",
            "014342010000014308000000",
            "024635",
            "014374020000",
            "01432A040000050505",
        ),
        (322, 628, 1066),
        ("024635",),
    ),
    3410: (
        (
            "014308000000",
            "014396040000",
            "0143CA000000",
            "02473E",
            "014388030000050505",
        ),
        (8, 1174, 202, 904),
        ("02473E",),
    ),
    3411: (
        ("", "014390040000", "014326020000050505"),
        (1168, 550),
        (),
    ),
    3413: (
        (
            "",
            "014308000000",
            "014396040000",
            "01432A0400000143FC010000050505",
        ),
        (8, 1174, 1066),
        (),
    ),
    3414: (
        (
            "014308000000",
            "014342010000",
            "02473E",
            "024633",
            "014348040000050505",
        ),
        (8, 322, 1096),
        ("02473E", "024633"),
    ),
    3415: (
        (
            "",
            "014388030000",
            "014308000000",
            "02473E",
            "014348040000050505",
        ),
        (904, 8, 1096),
        ("02473E",),
    ),
    3416: (
        (
            "",
            "014308000000",
            "01431A020000",
            "014374020000",
            "01438A040000050505",
        ),
        (8, 538, 628, 1162),
        (),
    ),
    3417: (
        (
            "014308000000",
            "014342010000",
            "024633",
            "02473E",
            "014348040000050505",
        ),
        (8, 322, 1096),
        ("024633", "02473E"),
    ),
    3418: (
        (
            "0143D0000000",
            "024635",
            "02473E",
            "014348040000050505",
        ),
        (208, 1096),
        ("024635", "02473E"),
    ),
    3420: (
        (
            "",
            "014301000000",
            "014388030000",
            "01436C010000050505",
        ),
        (1, 904, 364),
        (),
    ),
    3428: (
        ("024633", "029632", "050505"),
        (),
        ("024633", "029632"),
    ),
    3429: (
        ("023C", "014301000000", "014311000000", "050505"),
        (1, 17),
        ("023C",),
    ),
    3431: (
        ("023C", "014301000000", "014311000000", "050505"),
        (1, 17),
        ("023C",),
    ),
    3436: (
        ("014301000000", "014311000000", "050505"),
        (1, 17),
        (),
    ),
    3440: (
        ("", "014301000000", "050505"),
        (1,),
        (),
    ),
}
RECORD_VARIANTS = {
    3409: "house_head_succession_assurance",
    3410: "house_head_oath",
    3411: "house_stewardship_acceptance",
    3413: "elder_house_stewardship_acceptance",
    3414: "life_pledged_house_protection",
    3415: "house_strengthening_vow",
    3416: "reluctant_house_head_acceptance",
    3417: "life_pledged_house_protection",
    3418: "house_survival_and_prosperity_vow",
    3420: "house_prosperity_charge",
    3428: "term_loyalty_modifier_warning",
    3429: "rough_merit_rank_reaction",
    3431: "formal_merit_rank_reaction",
    3436: "humble_merit_rank_reaction",
    3440: "reserved_merit_rank_reaction",
}
REGISTER_POLICY = {
    3409: "assertive_house_head",
    3410: "formal_oath",
    3411: "formal_stewardship",
    3413: "elder_resigned_stewardship",
    3414: "protective_vow",
    3415: "confident_strengthening_vow",
    3416: "reluctant_but_loyal",
    3417: "protective_vow",
    3418: "solemn_prosperity_vow",
    3420: "confident_house_charge",
    3428: "neutral_system_warning",
    3429: "rough_grateful_merit",
    3431: "formal_humble_merit",
    3436: "deferential_humble_merit",
    3440: "reserved_humble_merit",
}
TERMINOLOGY_SCOPE = {
    "house": ("당주", "가문", "주군", "존속", "번영"),
    "office": ("일임", "책임", "임기", "충성 보정"),
    "merit": ("훈공", "낭중지추", "망외의 기쁨"),
    "runtime_particles": (
        "이(가)",
        "은(는)",
        "을(를)",
        "에게",
        "의",
    ),
}
KNOWN_CURRENT_GAP_ANOMALY = {
    "coordinate": "6:3421:0",
    "record_id": 3421,
    "base_coordinate": "6:3414:0",
    "pk_source_gap_hex": ("", "01432A040000050505"),
    "pk_current_gap_hex": ("", "050505"),
    "base_source_gap_hex": ("", "01431E040000050505"),
    "pk_source_direct_call_operands": (1066,),
    "pk_current_direct_call_operands": (),
    "base_source_direct_call_operands": (1054,),
    "prefill_runtime_review": "not_required",
    "prefill_scope_classification": "retranslated",
    "prefill_runtime_classification_incorrect": True,
    "repair_in_current_segment_authorized": False,
}
EXPECTED_CHANGED_COORDINATES = (
    "6:3410:2",
    "6:3411:0",
    "6:3411:1",
    "6:3413:0",
    "6:3414:1",
    "6:3415:1",
    "6:3416:2",
    "6:3417:1",
    "6:3417:2",
    "6:3418:1",
    "6:3420:0",
    "6:3420:1",
    "6:3428:0",
    "6:3429:0",
)
EXPECTED_CHANGED_LITERAL_COUNT = len(EXPECTED_CHANGED_COORDINATES)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_BASE_PRISTINE_SHA256 = (
    "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "C35F948B73B95390D3235E7C6FC56ABC84172BADC5CBFE9DB063BA74554AE100"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "F371A45023580B071ED96F0C99093C9E929D7DE4834CE217BF912DD40773BE91"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4E61E0776DDFE1EE87B5CF87EFE1B78EAD673266917E7FFC40A52B1FBC397988"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C75A746A37312137D63E284118B568098D1BA069B4224F9137C79C1D9CE804E2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "8F39FC870CDC013DD1B594584B589102B6A12C2A2C1E33B3AC62EB020E0D1C4B"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "DC6D0C5B34374319599688D0C7D13CA1204F613103EE956DF1BE1CEAA44F4FE8"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "383DE8AC68F138302D9C50DC9341C7FF11943B4C02F56B0C15B68349EF1E0A8E"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "DD4B2BCE9A70202905801D92DE64C179E17FCD0F109A238D554BB4F7D7E86109"
)
EXPECTED_BOUNDARY_SHA256 = (
    "FD19F41D9B2E2CCE6DF0010CEE2A269A375A7147814A1A657EB8C27B821FD2C6"
)
EXPECTED_RUNTIME_RECORD_SHA256 = (
    "93675FF1DA8F4396C34C6C2128FAEE7D97C11059ABEE77E8C940FF81A1BCD932"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "80BB9724D4533C76CC6A832EAA7B92E4973D4CC920C9051B6D68DBA43A6FB161"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "0C459C98D4EA055720DAADEDEE490FCAFFFC0CE4D9FA4465FD2EB6BA67600613"
)
EXPECTED_KNOWN_CURRENT_GAP_ANOMALY_SHA256 = (
    "95196C64D683636E17E54E0B67646302E1B088D8F81E4653B794E6FA2E0C8BD4"
)
EXPECTED_BOUNDARY_COMPANION_SHA256 = (
    "00BA7E50AA0B469D0AD96165F93B72908F95362597A45CDF5767579BFFA16A2A"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "E9EE1FB9534035AB6D3162A0C55636E88B5D278423E7FDCAD0FE223CCD115F10"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "EDADA6F15C8B9FACD20DC672B968D9F4A6B939130D0CB474006FD8EDB48D020E"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "9392558858D06D28F6631A6C1104F8978312A36D6B986F1B19DE2645A64A51B1"
)
EXPECTED_REGISTER_POLICY_SHA256 = (
    "C8700E3691E8C110C5E6807974CDD086F7DB9E83E38086D0C5C6237E36DE5CB4"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "30DA742954D3301637DFF9A19E34E80D0D29A0902105FA46732B7764D5FC3F77"
)
EXPECTED_CANDIDATE_SHA256 = (
    "2EE3F2AC1BE9830D013E2D2477D532C65F3FDF914081980DC19D6DB63FB23BAC"
)

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; thirty-eight Base exact-"
    "reuse prefill rows and twenty-eight residual rows cover the "
    "assigned sixty-six visible literals, while three independently "
    "guarded predecessor companions complete boundary record 3409; "
    "all thirty-two complete records and sixty-nine literals are "
    "assembled without current-text fallback; the semantic Base donor "
    "sequence is PK record minus seven, under which all source literals "
    "and operand-masked runtime templates are identical; twenty records "
    "are byte-exact and twelve records contain reviewed direct-call "
    "operand remapping only; Base semantic translations are reused "
    "exactly while Base runtime review and call-operand state are not "
    "inherited; house-head succession, stewardship, term loyalty and "
    "merit terminology and assertive, formal, elder, protective, "
    "reluctant, rough, humble and reserved registers are reviewed; "
    "person, clan, house, numeric and title tokens, direct-call "
    "operands, particles, spacing, protected signatures, line counts, "
    "the out-of-scope record 3421 missing-current-call anomaly and its "
    "incorrect not-required prefill classification, "
    "reverse overlay, two-run reproduction, tamper rejection, outside-"
    "scope records and read-only inputs are guarded; all twenty-eight "
    "dynamic fragments remain runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1118_common",
        COMMON_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {COMMON_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_common()
ENGINE = COMMON.ENGINE
sha256_bytes = COMMON.sha256_bytes
canonical_sha256 = COMMON.canonical_sha256
coordinate_key = COMMON.coordinate_key
literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
read_jsonl = COMMON.read_jsonl
context_records = COMMON.context_records
direct_calls = COMMON.direct_calls
inline_controls = COMMON.inline_controls


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def mask_call_operands(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01\x43.{4}",
            b"\x01\x43\xFF\xFF\xFF\xFF",
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gaps
    )


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,)
        if resource == "base_msggame"
        else tuple(
            sorted(
                DECISIONS_ROOT.glob(
                    "pk_msggame_*.private.v1.jsonl"
                )
            )
        )
    )
    result: dict[str, dict[str, Any]] = {}
    for path in paths:
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") == resource
                and isinstance(coordinate, str)
            ):
                previous = result.setdefault(coordinate, row)
                if previous is not row:
                    raise RuntimeError(
                        f"segment {SEGMENT} duplicate decision: "
                        f"{coordinate}"
                    )
    return result


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
        or sha256_bytes(ENGINE.DEFAULT_BASE_PRISTINE.read_bytes())
        != EXPECTED_BASE_PRISTINE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
    )
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 109
        or len(visible) != 200
        or visible[0] != "6:3332:0"
        or visible[-1] != "6:3440:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B035 queue universe drifted"
        )
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:3409:3"
        or queue_slice[-1] != "6:3440:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice boundary drifted"
        )
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 38:
        raise RuntimeError(
            f"segment {SEGMENT} prefill count drifted: "
            f"{len(prefilled)}"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )

    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES or len(residual) != 28:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
        )
    guarded_digest(
        "target coordinate",
        residual,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )

    optional_present: list[str] = []
    for path in OPTIONAL_PREDECESSORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
            optional_present.append(path.name)
    return queue_slice, tuple(optional_present)


def assert_context_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    context_ids = tuple(range(3408, 3442))
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in context_ids
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in SLICE_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    runtime_records = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            direct_calls(
                gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            inline_controls(
                gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in SLICE_RECORD_IDS
    )
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        (
            "multilingual context",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        (
            "runtime record",
            runtime_records,
            EXPECTED_RUNTIME_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if any(
        (source == current)
        != (record_id not in CURRENT_GAP_DIVERGENT_RECORD_IDS)
        for record_id, source, current in gaps
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source/current gap drifted"
        )
    divergent_gap_map = {
        record_id: (source, current)
        for record_id, source, current in gaps
        if record_id in CURRENT_GAP_DIVERGENT_RECORD_IDS
    }
    if divergent_gap_map != {
        3421: (
            ("", "01432A040000050505"),
            ("", "050505"),
        )
    }:
        raise RuntimeError(
            f"segment {SEGMENT} known current gap anomaly drifted"
        )
    runtime_map = {
        record_id: (gaps_hex, calls, inline)
        for record_id, gaps_hex, calls, inline in runtime_records
    }
    if any(
        runtime_map[record_id] != expected
        for record_id, expected in EXPECTED_TARGET_RUNTIME.items()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target runtime structure drifted"
        )


def assert_base_boundary_and_assembly(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    queue_slice: tuple[str, ...],
) -> dict[int, tuple[str, ...]]:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame")
    pk_rows = decision_map("pk_msggame")
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }

    base_record_evidence: list[tuple[Any, ...]] = []
    for pk_record_id in SLICE_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[pk_record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, pk_record_id)]
        base_record = base_source_records[(BLOCK_ID, base_record_id)]
        pk_gaps = gap_bytes(pk_record)
        base_gaps = gap_bytes(base_record)
        source_equal = (
            literal_texts(
                records_by_label["jp"],
                (BLOCK_ID, pk_record_id),
            )
            == literal_texts(
                base_source_records,
                (BLOCK_ID, base_record_id),
            )
        )
        data_equal = pk_record.data == base_record.data
        gaps_equal = pk_gaps == base_gaps
        masked_equal = (
            mask_call_operands(pk_gaps)
            == mask_call_operands(base_gaps)
        )
        inline_equal = (
            inline_controls(pk_gaps)
            == inline_controls(base_gaps)
        )
        base_record_evidence.append(
            (
                pk_record_id,
                base_record_id,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                source_equal,
                data_equal,
                gaps_equal,
                masked_equal,
                inline_equal,
                direct_calls(pk_gaps),
                direct_calls(base_gaps),
                mask_call_operands(pk_gaps),
                mask_call_operands(base_gaps),
            )
        )
        expected_exact = pk_record_id in EXACT_BASE_RECORD_IDS
        expected_divergent = (
            pk_record_id in DIVERGENT_CALL_RECORD_IDS
        )
        if (
            not source_equal
            or not masked_equal
            or not inline_equal
            or expected_exact == expected_divergent
            or data_equal != expected_exact
            or gaps_equal != expected_exact
            or (
                expected_divergent
                and direct_calls(pk_gaps)
                == direct_calls(base_gaps)
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base record mapping drifted: "
                f"{pk_record_id}"
            )
    guarded_digest(
        "Base record",
        tuple(base_record_evidence),
        EXPECTED_BASE_RECORD_SHA256,
    )

    full_coordinates = tuple(
        f"6:{record_id}:{literal_id}"
        for record_id in SLICE_RECORD_IDS
        for literal_id in range(
            len(
                literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )
            )
        )
    )
    prefill_coordinates = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if (
        len(full_coordinates) != 69
        or len(queue_slice) != 66
        or full_coordinates[:3] != BOUNDARY_COMPANION_COORDINATES
        or full_coordinates[3:] != queue_slice
        or len(prefill_coordinates) != 38
        or any(
            coordinate in prefill_coordinates
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full coordinate drifted"
        )
    prefill_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
        )
        for coordinate in prefill_coordinates
    )
    if any(
        semantic != "approved"
        or runtime not in ("pending", "not_required")
        for _, _, semantic, runtime, _, _ in prefill_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill context drifted"
        )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )
    anomaly_coordinate = str(
        KNOWN_CURRENT_GAP_ANOMALY["coordinate"]
    )
    anomaly_record_id = int(
        KNOWN_CURRENT_GAP_ANOMALY["record_id"]
    )
    anomaly_base_coordinate = str(
        KNOWN_CURRENT_GAP_ANOMALY["base_coordinate"]
    )
    anomaly_base_record_id = int(
        anomaly_base_coordinate.split(":")[1]
    )
    anomaly_source_gaps = gap_bytes(
        records_by_label["jp"][(BLOCK_ID, anomaly_record_id)]
    )
    anomaly_current_gaps = gap_bytes(
        records_by_label["current"][(BLOCK_ID, anomaly_record_id)]
    )
    anomaly_base_gaps = gap_bytes(
        base_source_records[
            (BLOCK_ID, anomaly_base_record_id)
        ]
    )
    anomaly_prefill = prefill_rows[anomaly_coordinate]
    anomaly_actual = {
        "coordinate": anomaly_coordinate,
        "record_id": anomaly_record_id,
        "base_coordinate": anomaly_base_coordinate,
        "pk_source_gap_hex": tuple(
            value.hex().upper() for value in anomaly_source_gaps
        ),
        "pk_current_gap_hex": tuple(
            value.hex().upper() for value in anomaly_current_gaps
        ),
        "base_source_gap_hex": tuple(
            value.hex().upper() for value in anomaly_base_gaps
        ),
        "pk_source_direct_call_operands":
        direct_calls(anomaly_source_gaps),
        "pk_current_direct_call_operands":
        direct_calls(anomaly_current_gaps),
        "base_source_direct_call_operands":
        direct_calls(anomaly_base_gaps),
        "prefill_runtime_review":
        anomaly_prefill.get("runtime_review"),
        "prefill_scope_classification":
        anomaly_prefill.get("scope_classification"),
        "prefill_runtime_classification_incorrect": True,
        "repair_in_current_segment_authorized": False,
    }
    if anomaly_actual != KNOWN_CURRENT_GAP_ANOMALY:
        raise RuntimeError(
            f"segment {SEGMENT} known current gap anomaly "
            "evidence drifted"
        )
    guarded_digest(
        "known current gap anomaly",
        anomaly_actual,
        EXPECTED_KNOWN_CURRENT_GAP_ANOMALY_SHA256,
    )

    boundary_evidence: list[tuple[Any, ...]] = []
    for coordinate, translation in (
        BOUNDARY_COMPANION_TRANSLATIONS.items()
    ):
        donor = (
            f"6:{int(coordinate.split(':')[1]) - 7}:"
            f"{coordinate.split(':')[2]}"
        )
        base_row = base_rows[donor]
        predecessor = pk_rows.get(coordinate)
        if (
            translation != base_row.get("translation")
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
            or (
                predecessor is not None
                and (
                    predecessor.get("translation") != translation
                    or predecessor.get("semantic_review") != "approved"
                    or predecessor.get("runtime_review") != "pending"
                )
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} boundary companion drifted: "
                f"{coordinate}"
            )
        boundary_evidence.append(
            (
                coordinate,
                donor,
                translation,
                (
                    predecessor.get("translation")
                    if predecessor is not None
                    else None
                ),
                (
                    predecessor.get("runtime_review")
                    if predecessor is not None
                    else None
                ),
            )
        )
    guarded_digest(
        "boundary companion",
        tuple(boundary_evidence),
        EXPECTED_BOUNDARY_COMPANION_SHA256,
    )

    assembly_evidence: list[tuple[Any, ...]] = []
    base_evidence: list[tuple[Any, ...]] = []
    assembly_map: dict[int, tuple[str, ...]] = {}
    for record_id in SLICE_RECORD_IDS:
        translations: list[str] = []
        owners: list[str] = []
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        for literal_id, _current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{BASE_RECORD_MAPPING[record_id]}:{literal_id}"
            )
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owner = "segment"
            elif coordinate in prefill_rows:
                translation = str(
                    prefill_rows[coordinate]["translation"]
                )
                owner = "prefill"
            elif coordinate in BOUNDARY_COMPANION_TRANSLATIONS:
                translation = BOUNDARY_COMPANION_TRANSLATIONS[
                    coordinate
                ]
                owner = "boundary_base_donor"
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} current fallback forbidden: "
                    f"{coordinate}"
                )
            base_row = base_rows[base_coordinate]
            if (
                base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review")
                not in ("verified", "not_required")
                or translation != base_row.get("translation")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base semantic donor drifted: "
                    f"{coordinate}"
                )
            translations.append(translation)
            owners.append(owner)
            base_evidence.append(
                (
                    coordinate,
                    base_coordinate,
                    translation,
                    base_row.get("translation"),
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                )
            )
        assembly_map[record_id] = tuple(translations)
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(source_record)
                ),
                direct_calls(gap_bytes(source_record)),
                inline_controls(gap_bytes(source_record)),
            )
        )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )
    if (
        any(
            assembly_map[record_id] != expected
            for record_id, expected
            in EXPECTED_TARGET_ASSEMBLIES.items()
        )
        or any(
            base_rows[BASE_CONTEXT_REFERENCES[coordinate]].get(
                "runtime_review"
            )
            != "verified"
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete assembly drifted"
        )
    return assembly_map


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_SCOPE,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    guarded_digest(
        "register policy",
        REGISTER_POLICY,
        EXPECTED_REGISTER_POLICY_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    changed_coordinates: list[str] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )
        if translation != current_text:
            changed_coordinates.append(coordinate)
    if tuple(changed_coordinates) != EXPECTED_CHANGED_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} changed coordinate drifted"
        )


def patch_common_globals() -> None:
    values = {
        "SEGMENT": SEGMENT,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "DECISIONS_ROOT": DECISIONS_ROOT,
    }
    for name, value in values.items():
        setattr(COMMON, name, value)


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_sequence(
    source_gap_hex: tuple[str, ...],
    record_id: int,
) -> tuple[str, ...]:
    steps: list[str] = []
    for literal_id in range(len(source_gap_hex) - 1):
        if source_gap_hex[literal_id]:
            steps.append(
                f"gap:{literal_id}:{source_gap_hex[literal_id]}"
            )
        steps.append(f"literal:6:{record_id}:{literal_id}")
    if source_gap_hex[-1]:
        steps.append(f"terminal_gap:{source_gap_hex[-1]}")
    return tuple(steps)


def control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    base_source_records: dict[tuple[int, int], Any],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][(BLOCK_ID, record_id)]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    base_record = base_source_records[
        (BLOCK_ID, BASE_RECORD_MAPPING[record_id])
    ]
    source_gaps = gap_bytes(source_record)
    current_gaps = gap_bytes(current_record)
    base_gaps = gap_bytes(base_record)
    source_gap_hex = tuple(
        value.hex().upper() for value in source_gaps
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in current_gaps
    )
    base_gap_hex = tuple(
        value.hex().upper() for value in base_gaps
    )
    source_calls = direct_calls(source_gaps)
    current_calls = direct_calls(current_gaps)
    base_calls = direct_calls(base_gaps)
    source_inline = inline_controls(source_gaps)
    current_inline = inline_controls(current_gaps)
    base_inline = inline_controls(base_gaps)
    expected_gap, expected_calls, expected_inline = (
        EXPECTED_TARGET_RUNTIME[record_id]
    )
    base_exact = record_id in EXACT_BASE_RECORD_IDS
    call_remapped = record_id in DIVERGENT_CALL_RECORD_IDS
    if (
        source_gap_hex != expected_gap
        or current_gap_hex != source_gap_hex
        or source_calls != expected_calls
        or current_calls != source_calls
        or source_inline != expected_inline
        or current_inline != source_inline
        or base_inline != source_inline
        or mask_call_operands(source_gaps)
        != mask_call_operands(base_gaps)
        or base_exact == call_remapped
        or (base_gap_hex == source_gap_hex) != base_exact
        or (
            call_remapped
            and base_calls == source_calls
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    return {
        "source_record_gap_sha256":
        canonical_sha256(source_gap_hex),
        "current_record_gap_sha256":
        canonical_sha256(current_gap_hex),
        "base_record_gap_sha256":
        canonical_sha256(base_gap_hex),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "base_runtime_gap_hex": base_gap_hex,
        "source_current_runtime_gap_equal": True,
        "source_direct_call_operands": source_calls,
        "current_direct_call_operands": current_calls,
        "base_direct_call_operands": base_calls,
        "source_inline_runtime_controls": source_inline,
        "current_inline_runtime_controls": current_inline,
        "base_inline_runtime_controls": base_inline,
        "operand_masked_runtime_gap_equal": True,
        "base_record_byte_exact": base_exact,
        "base_call_operand_remap_reviewed": call_remapped,
        "base_call_operand_state_inherited": False,
        "runtime_sequence":
        runtime_sequence(source_gap_hex, record_id),
        "record_variant": RECORD_VARIANTS[record_id],
        "speaker_register_variant": REGISTER_POLICY[record_id],
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_companions_reviewed": True,
        "boundary_predecessor_companions_reviewed":
        record_id == 3409,
        "protected_token_spacing_reviewed": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    queue_slice, optional_present = (
        assert_queue_and_residual_contract(prepared)
    )
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_boundary_and_assembly(
        records_by_label,
        queue_slice,
    )
    assert_semantics(records_by_label)
    if DISCOVERED_PINS:
        return prepared, [], b"", "", -1, optional_present

    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        companion_coordinates = tuple(
            f"6:{record_id}:{companion_id}"
            for companion_id in range(
                len(
                    literal_texts(
                        records_by_label["current"],
                        (block_id, record_id),
                    )
                )
            )
            if companion_id != literal_id
        )
        base_exact = record_id in EXACT_BASE_RECORD_IDS
        row = {
            "schema":
            "nobu16.kr.pc-dialogue-full-retranslation.v1."
            "private-decision",
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "runtime_review": "pending",
            "layout_review": "runtime_pending",
            "scope_classification": "runtime_fragment_pending",
            "basis": BASIS,
            "source_record_raw_sha256":
            prepared.visible_targets[
                ("pk_msggame", block_id, record_id, literal_id)
            ]["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            sha256_bytes(current_text.encode("utf-16le")),
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "protected_signature_review": True,
            "historical_term_review": True,
            "speaker_register_review": True,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_context_reference_kind":
            (
                "exact_source_exact_record"
                if base_exact
                else "exact_source_operand_masked_runtime_template"
            ),
            "base_source_literal_exact": True,
            "base_record_opcode_exact": True,
            "base_record_byte_exact": base_exact,
            "base_call_operand_remap_reviewed":
            not base_exact,
            "base_call_operand_state_inherited": False,
            "base_semantic_translation_reused": True,
            "base_translation_contextually_adapted": False,
            "base_exact_reuse_prefill_excluded": True,
            "base_runtime_state_inherited": False,
            "same_record_companion_coordinates":
            companion_coordinates,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "record_variant": RECORD_VARIANTS[record_id],
            "speaker_register_variant":
            REGISTER_POLICY[record_id],
            "runtime_assembly_evidence":
            control_evidence(
                records_by_label,
                base_source_records,
                record_id,
            ),
        }
        rows.append(row)
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_common_globals()
    COMMON.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    if DISCOVERED_PINS:
        print(
            json.dumps(
                DISCOVERED_PINS,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )

    steam_path = prepared.resources["pk_msggame"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 28
        or len(validated) != 28
        or counts != Counter({"runtime_fragment_pending": 28})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["base_runtime_state_inherited"] is not False
            or row["base_call_operand_state_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["protected_signature_review"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B035_S1118",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 38,
                "residual_count": 28,
                "boundary_companion_count":
                len(BOUNDARY_COMPANION_COORDINATES),
                "reviewed_complete_record_count":
                len(SLICE_RECORD_IDS),
                "reviewed_complete_literal_count": 69,
                "target_runtime_record_count":
                len(TARGET_RECORD_IDS),
                "direct_call_target_record_count": 14,
                "exact_base_record_count":
                len(EXACT_BASE_RECORD_IDS),
                "operand_remapped_base_record_count":
                len(DIVERGENT_CALL_RECORD_IDS),
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "base_record_mapping_offset": -7,
                "base_source_literals_exact": True,
                "base_operand_masked_templates_exact": True,
                "base_call_operand_remaps_reviewed": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "base_call_operand_state_inherited": False,
                "known_current_gap_divergence_records":
                list(CURRENT_GAP_DIVERGENT_RECORD_IDS),
                "known_current_gap_divergence_guarded": True,
                "prefill_runtime_anomaly_detected": True,
                "known_current_gap_anomaly":
                KNOWN_CURRENT_GAP_ANOMALY,
                "prefill_companions_guarded": True,
                "boundary_companions_guarded": True,
                "complete_record_assembly_guarded": True,
                "historical_terms_reviewed": True,
                "speaker_registers_reviewed": True,
                "runtime_controls_guarded": True,
                "direct_call_operands_guarded": True,
                "protected_token_spacing_guarded": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "outside_scope_records_exact": True,
                "target_runtime_gaps_exact": True,
                "source_current_runtime_gaps_exact": False,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
