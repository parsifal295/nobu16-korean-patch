#!/usr/bin/env python3
"""Build source-redacted PK B039 segment 1128 residual decisions."""

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
BASE_BUILDER_PATH = (
    WORKSTREAM / "build_pk_batch038_segment1126.py"
)
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B039_S1128.private.v1.jsonl"
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
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B038_S1127.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B039_S1129.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1128
QUEUE_BATCH_ID = "pk_msggame-B039"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 3752
QUEUE_LAST_RECORD = 3866

TARGET_COORDINATES = (
    "6:3752:0",
    "6:3753:0",
    "6:3758:0",
    "6:3765:0",
    "6:3765:1",
    "6:3766:0",
    "6:3766:1",
    "6:3768:1",
    "6:3768:4",
    "6:3769:4",
    "6:3771:0",
    "6:3777:0",
    "6:3778:1",
    "6:3780:0",
    "6:3781:0",
    "6:3783:0",
    "6:3784:0",
    "6:3785:0",
    "6:3786:0",
    "6:3787:0",
    "6:3788:0",
    "6:3789:0",
    "6:3790:0",
    "6:3791:0",
    "6:3792:2",
    "6:3793:2",
)
TRANSLATIONS = {
    "6:3752:0": "을(를) 대신해\n",
    "6:3753:0": "을(를) 대신해\n",
    "6:3758:0": "우리 가문과",
    "6:3765:0": ",",
    "6:3765:1": "의",
    "6:3766:0": (
        "두 가문 사이에 굳건한 신뢰를 쌓고자…\n"
        "훗날 동맹을 맺겠다는 약정에\n"
        "동의해 주시"
    ),
    "6:3766:1": "까?",
    "6:3768:1": "에게 원군 등\n군사적",
    "6:3768:4": "까?",
    "6:3769:4": "까?",
    "6:3771:0": "…알겠",
    "6:3777:0": "지금은",
    "6:3778:1": "\n좋은 방안",
    "6:3780:0": (
        "재미있군, 손잡아 주지\n"
        "단, 당분간뿐이다\n"
        "그다음 일은 그때의 내가 알아서 하겠지"
    ),
    "6:3781:0": (
        "동맹 제의는 받아들였다\n"
        "당분간은 손을 잡도록 하지\n"
        "그 뒤 일은 그때 다시 이야기하자꾸나"
    ),
    "6:3783:0": (
        "동맹 제의는 알겠습니다\n"
        "당분간은 손을 잡도록 하지요\n"
        "그 뒤 일은 때가 되면 다시 이야기하지요"
    ),
    "6:3784:0": (
        "맹약은 받아들이겠다\n"
        "당분간은 손을 잡도록 하자\n"
        "그 뒤 일은 때가 되면 논하면 된다"
    ),
    "6:3785:0": (
        "동맹 제의는 받아들이겠다\n"
        "당분간 서로 손을 잡도록 하지\n"
        "그 뒤 일은 그때 생각하면 된다"
    ),
    "6:3786:0": (
        "동맹 제의는 받아들이겠다\n"
        "당분간은 손을 잡도록 하지\n"
        "그 뒤 일은 때가 되면 다시 논하자"
    ),
    "6:3787:0": (
        "동맹 제의는 승낙했다\n"
        "당분간은 손을 잡도록 하지\n"
        "그 뒤 일은 때가 되면 다시 논하면 되겠지"
    ),
    "6:3788:0": (
        "동맹 제의는 받아들이겠습니다\n"
        "당분간은 손을 잡도록 하지요\n"
        "그 뒤 일은 그때 다시 의논하지요"
    ),
    "6:3789:0": (
        "동맹 제의는 받아들이겠다\n"
        "당분간은 벗이 되자\n"
        "그 뒤 일은 때가 되면 다시 생각하면 된다"
    ),
    "6:3790:0": (
        "동맹 제의, 삼가 받아들이겠습니다\n"
        "당분간 손을 잡고…\n"
        "그 뒤 일은 훗날 다시…"
    ),
    "6:3791:0": (
        "동맹 제의는 받아들이겠다\n"
        "당분간은 손을 잡도록 하지\n"
        "그 뒤 일은 때가 되면 다시 논하자"
    ),
    "6:3792:2": "의",
    "6:3793:2": "의",
}
STATIC_RECORD_IDS = (
    3780,
    3781,
    3783,
    3784,
    3785,
    3786,
    3787,
    3788,
    3789,
    3790,
    3791,
)
STATIC_COORDINATES = {
    f"6:{record_id}:0" for record_id in STATIC_RECORD_IDS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
TARGET_RECORD_IDS = (
    3752,
    3753,
    3758,
    3765,
    3766,
    3768,
    3769,
    3771,
    3777,
    3778,
    *STATIC_RECORD_IDS,
    3792,
    3793,
)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
BASE_RECORD_MAPPING = {
    record_id: record_id - 7 for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (
    3777,
    *STATIC_RECORD_IDS,
)
OPERAND_MASKED_BASE_RECORD_IDS = (
    3752,
    3753,
    3758,
    3765,
    3769,
    3771,
    3778,
    3792,
    3793,
)
PK_EXCLUSIVE_SEMANTIC_RECORD_IDS = (3766, 3768)
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = (3766, 3768)
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
EXPECTED_ARITY = {
    3752: 2,
    3753: 2,
    3758: 2,
    3765: 3,
    3766: 2,
    3768: 5,
    3769: 5,
    3771: 2,
    3777: 2,
    3778: 2,
    **{record_id: 1 for record_id in STATIC_RECORD_IDS},
    3792: 4,
    3793: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "6:3752:1",
    "6:3753:1",
    "6:3758:1",
    "6:3765:2",
    "6:3768:0",
    "6:3768:2",
    "6:3768:3",
    "6:3769:0",
    "6:3769:1",
    "6:3769:3",
    "6:3771:1",
    "6:3777:1",
    "6:3778:0",
    "6:3792:0",
    "6:3792:3",
    "6:3793:0",
    "6:3793:3",
)
HIDDEN_COMPANION_COORDINATES = (
    "6:3769:2",
    "6:3792:1",
    "6:3793:1",
)
BOUNDARY_RECORD_IDS = (
    3751,
    3754,
    3757,
    3779,
    3782,
    3794,
)
EXPECTED_GAPS_BY_RECORD = {
    3752: (
        "01431D000000",
        "025032",
        "014366040000050505",
    ),
    3753: (
        "01431D000000",
        "025032",
        "01432A040000050505",
    ),
    3758: ("", "025032", "01432A040000050505"),
    3765: (
        "014308000000",
        "025032",
        "014322000000",
        "014326020000050505",
    ),
    3766: (
        "",
        "0143AE040000014348040000",
        "050505",
    ),
    3768: (
        "",
        "025032",
        "014396040000",
        "014390040000",
        "0143EC020000",
        "050505",
    ),
    3769: (
        "",
        "025032",
        "0143B2000000",
        "014396040000",
        "014348040000",
        "050505",
    ),
    3771: (
        "",
        "014374020000",
        "0143DC030000050505",
    ),
    3777: ("", "025032", "050505"),
    3778: (
        "023C",
        "0143EE000000",
        "014326020000050505",
    ),
    **{
        record_id: ("", "050505")
        for record_id in STATIC_RECORD_IDS
    },
    3792: (
        "",
        "014374020000",
        "026432",
        "023C",
        "01432A040000050505",
    ),
    3793: (
        "",
        "014374020000",
        "026432",
        "023C",
        "01432A040000050505",
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3752: ((29, 1126), ("025032",)),
    3753: ((29, 1066), ("025032",)),
    3758: ((1066,), ("025032",)),
    3765: ((8, 34, 550), ("025032",)),
    3766: ((1198, 1096), ()),
    3768: ((1174, 1168, 748), ("025032",)),
    3769: ((178, 1174, 1096), ("025032",)),
    3771: ((628, 988), ()),
    3777: ((), ("025032",)),
    3778: ((238, 550), ("023C",)),
    **{
        record_id: ((), ())
        for record_id in STATIC_RECORD_IDS
    },
    3792: ((628, 1066), ("026432", "023C")),
    3793: ((628, 1066), ("026432", "023C")),
}
EXPECTED_CALL_ROOTS = (
    8,
    29,
    34,
    178,
    238,
    550,
    628,
    748,
    988,
    1066,
    1096,
    1126,
    1168,
    1174,
    1198,
)
EXPECTED_CONFLICT_TERMINAL_SETS = {
    748: {"않습니다", "않는다"},
    1096: {"합니다", "다", "하옵니다"},
    1168: {"오", ""},
    1174: {"고", ""},
    1198: {"받으실", "받아"},
}

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "46FCAC941D0FA0530066C89B6E293C186F1813C94CEAB511A7E2676262023423"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "10EE8B0EF62A2AD61312432A51E9FA0DD52AE48A7615C3D6E4EBACFE3E3F5800"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C47F716B3764E47C667233E14C113A9A52392FB8964CA4BF7A16DDB66BCAF5F8"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "AD5A4F864A29AA15AB56561B849B63BA95207696CE208AEA4DE62FA468016371"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "B219D662D6772844302D66F60976CC768019EA52F4609E2956FACE4AE71B2289"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "FA8CC0295746CBF6C9814E03336223C95F7A594EB61BA439CCF7067A4CADC22A"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "FDFA97EF1073CD2B626AA7A27D046B3C3DED2B5B2D377CE15485371387A78564"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "4A61B4164E4FADF24E99CEC1E5F5EAB783D00586A4BAB883B680389B0FBC0825"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "16D0451807472C8B39B7A5E2EF2BF5743D0F966EE87BF71155AAC689B96F2F70"
)
EXPECTED_BOUNDARY_SHA256 = (
    "4D1233653DCB6E237C3D5D826BDB4BAFA9FDD8276261BE99A660CA09C04EF96D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "34627E21A3DC8CE0EEAF001E7785B9F1F8F34BBDE307AC4F97870F06D2FF0DD0"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "42D0E01EC671D110DFC38163E4AC6EBD5B8FBC2EE1DDB19A1D80E79F95900B51"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "56F4E8CF2E8176C8187A78FE61FCD19D33C140C16BC497A4F8C201E38A2D1128"
)
EXPECTED_PK_EXCLUSIVE_SHA256 = (
    "46C54A7C598476D8A9A3B82C64702153B80E2C38E41C0C8FCB03F0AA1E7D4277"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "D5C8416AF2EB573D7181E30F0BB97C361DEB81356BEC1B9CB0BEC04D2AA9AE5A"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "C8EA788245C48C6E67A110894A0F590184EBDAF9539E1193A716BA32E3A5DEC8"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "2ED2AD7F57EB0D591EA9BEE7782D9217598C006C35CC51CBC2CE579067782B89"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "90B523602C2849C9B74E0DD3FC25A029C574A324615C63450DB7E81C4C9D5892"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "ACBB2D3203FCE5BE208732EC5F18644DF52E36B313C82F1BB491DA87F40066FA"
)
EXPECTED_CANDIDATE_SHA256 = (
    "876BC26305840751D0E8B12B9BF3FE5553A49A2BC9A4B1544D678C5FD42C2D0D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 22

DISCOVERED_PINS: dict[str, str] = {}

SPEAKER_STYLE = {
    3752: "formal_envoy_strengthening_interclan_relations",
    3753: "formal_envoy_maintaining_interclan_relations",
    3758: "confident_house_envoy_brokering_relations",
    3765: "formal_attendant_announcing_visiting_envoy",
    3766: "formal_interclan_alliance_overture",
    3768: "formal_request_for_future_military_cooperation",
    3769: "formal_request_for_enduring_interclan_relations",
    3771: "formal_resigned_acceptance_of_other_house_intent",
    3777: "strategic_temporary_submission_to_another_clan",
    3778: "positive_response_to_forming_relations",
    3780: "rough_masculine_temporary_alliance_acceptance",
    3781: "authoritative_elder_temporary_alliance_acceptance",
    3783: "polite_temporary_alliance_acceptance",
    3784: "archaic_authoritative_pact_acceptance",
    3785: "calm_authoritative_alliance_acceptance",
    3786: "measured_authoritative_alliance_acceptance",
    3787: "confident_authoritative_alliance_acceptance",
    3788: "polite_feminine_alliance_acceptance",
    3789: "bold_friendly_alliance_acceptance",
    3790: "high_formal_humble_alliance_acceptance",
    3791: "calm_authoritative_alliance_acceptance",
    3792: "formal_mission_acceptance_fragment",
    3793: "formal_mission_acceptance_fragment",
}
TERMINOLOGY_POLICY = {
    "house": "우리 가문",
    "other_house": "귀 가문",
    "clan_token": "025032",
    "castle_token": "026432",
    "office_or_mission_token": "023C",
    "submission": "신종",
    "alliance": "동맹",
    "pact": "맹약",
    "agreement": "약정",
    "reinforcements": "원군",
    "military_cooperation": "군사적 협력",
    "relationship_brokerage": "중개",
    "object_particle": "을(를)",
    "subject_particle": "이(가)",
    "conjunction_particle": "와(과)",
}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; twenty-one records use the "
    "canonical local Base donor at PK minus seven, including twelve "
    "byte-exact records and nine operand-masked records; PK-exclusive "
    "records 3766 and 3768 use the corresponding Base records only as "
    "semantic and register donors because their Japanese literals or "
    "runtime call layouts differ; all seventeen prefilled and three "
    "hidden same-record companions complete all twenty-three target "
    "records; eleven static alliance-acceptance records preserve distinct "
    "speaker voices and require no runtime review; live PK call graphs "
    "and terminal text for all fifteen roots include 0143 and 014A "
    "traversal; roots 1198 plus 1096 and roots 1174 plus 1168 plus 748 "
    "cannot form grammatical Korean across every speaker branch with "
    "the current block-zero terminal translations, so records 3766 and "
    "3768 retain explicit runtime morphology conflicts and cannot be "
    "promoted; interclan diplomacy, submission, alliance and pact "
    "terminology, clan, castle and mission tokens, protected whitespace, "
    "line counts, bytecode gaps, reverse overlay, two-run reproduction, "
    "tamper rejection, outside-scope records and read-only inputs are "
    "guarded; Base runtime verification is not inherited"
)


def load_base_builder() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1128_base",
        BASE_BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base_builder()
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
context_records = BASE.context_records


def patch_base_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.patch_base_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    calls: list[int] = []
    for gap in gaps:
        for match in re.finditer(
            b"\x01\x43(.{4})",
            gap,
            re.DOTALL,
        ):
            calls.append(
                int.from_bytes(match.group(1), "little")
            )
    return (
        tuple(calls),
        tuple(
            value.hex().upper()
            for value in gaps
            if value.startswith(b"\x02")
        ),
    )


def mask_call_operands(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01([\x43\x4A]).{4}",
            lambda match: b"\x01" + match.group(1) + b"\xFF" * 4,
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gaps
    )


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,)
        if resource == "base_msggame"
        else tuple(
            sorted(
                DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
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


def assert_queue_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
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
    universe = tuple(
        (
            str(row["record_coordinate"]),
            str(row["source_record_raw_sha256"]),
            str(row["current_record_raw_sha256"]),
            tuple(
                str(target["coordinate"])
                for target in row["target_literals"]
                if target["visible"]
            ),
        )
        for row in queue_rows
    )
    guarded_digest(
        "queue universe",
        universe,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    if (
        len(queue_rows) != 114
        or len(visible) != 198
        or queue_rows[0]["record_coordinate"] != "6:3752"
        or queue_rows[-1]["record_coordinate"] != "6:3866"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(
            record_id
            for record_id in range(
                QUEUE_FIRST_RECORD,
                QUEUE_LAST_RECORD + 1,
            )
            if record_id != 3757
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3752:0"
        or queue_slice[-1] != "6:3793:3"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue boundary drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != 41
        or residual != TARGET_COORDINATES
        or len(PREFILL_COMPANION_COORDINATES) != 17
        or any(
            coordinate not in prefilled
            for coordinate in PREFILL_COMPANION_COORDINATES
        )
        or any(
            coordinate in queue_slice
            for coordinate in HIDDEN_COMPANION_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill/residual drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    guarded_digest(
        "target coordinate",
        residual,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    prefill_context = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get("source_record_raw_sha256"),
            prefill_rows[coordinate].get("current_ko_utf16le_sha256"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in prefilled
    )
    if any(
        semantic != "approved"
        or runtime not in ("pending", "not_required")
        or promotion is not False
        for (
            _,
            _,
            semantic,
            runtime,
            _,
            _,
            _,
            promotion,
        ) in prefill_context
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill policy drifted"
        )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )

    optional_present: list[str] = []
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
        if path in OPTIONAL_NEIGHBORS:
            optional_present.append(path.name)
        coordinates = {
            str(row["coordinate"])
            for row in read_jsonl(path)
            if row.get("resource") == "pk_msggame"
        }
        if coordinates.intersection(TARGET_COORDINATES):
            raise RuntimeError(
                f"segment {SEGMENT} predecessor overlap: {path}"
            )
    return tuple(optional_present)


def assert_context_contracts(
    prepared: Any,
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
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in range(
            QUEUE_FIRST_RECORD,
            QUEUE_LAST_RECORD + 1,
        )
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
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        (
            "source target",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "current target",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "multilingual context",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "gap contract",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "boundary",
            boundary,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "runtime control",
            controls,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if any(
        source != EXPECTED_GAPS_BY_RECORD[record_id]
        or current != source
        for record_id, source, current in gaps
    ) or any(
        runtime != EXPECTED_CONTROLS_BY_RECORD[record_id]
        for _, record_id, runtime in controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime layout drifted"
        )
    if any(
        ("pk_msggame", *coordinate_key(coordinate))
        not in prepared.visible_targets
        for coordinate in TARGET_COORDINATES
    ) or any(
        ("pk_msggame", *coordinate_key(coordinate))
        in prepared.visible_targets
        for coordinate in HIDDEN_COMPANION_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} visibility drifted"
        )


def base_row_is_approved(row: dict[str, Any]) -> bool:
    runtime = row.get("runtime_review")
    verification = row.get("runtime_vm_verification", {})
    return (
        row.get("semantic_review") == "approved"
        and runtime in ("verified", "not_required")
        and (
            runtime == "not_required"
            or (
                verification.get("method")
                == "reversed_vm_static_analysis"
                and verification.get("result") == "verified"
            )
        )
    )


def assert_base_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted input drifted"
        )
    base_rows = decision_map("base_msggame")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    pk_source = records_by_label["jp"]
    pk_current = records_by_label["current"]
    base_context: list[tuple[Any, ...]] = []
    assemblies: list[tuple[Any, ...]] = []
    exclusive_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        source_record = pk_source[(BLOCK_ID, record_id)]
        current_record = pk_current[(BLOCK_ID, record_id)]
        base_source_record = base_source[(BLOCK_ID, base_record_id)]
        source_literals = literal_texts(
            pk_source,
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            pk_current,
            (BLOCK_ID, record_id),
        )
        base_source_literals = literal_texts(
            base_source,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current,
            (BLOCK_ID, base_record_id),
        )
        if len(source_literals) != EXPECTED_ARITY[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} arity drifted: {record_id}"
            )
        exact_semantic = (
            record_id not in PK_EXCLUSIVE_SEMANTIC_RECORD_IDS
        )
        if exact_semantic and source_literals != base_source_literals:
            raise RuntimeError(
                f"segment {SEGMENT} Base literal donor drifted: "
                f"{record_id}"
            )
        if (
            record_id in RAW_EXACT_BASE_RECORD_IDS
            and source_record.data != base_source_record.data
        ) or (
            record_id in OPERAND_MASKED_BASE_RECORD_IDS
            and mask_call_operands(gap_bytes(source_record))
            != mask_call_operands(gap_bytes(base_source_record))
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base layout donor drifted: "
                f"{record_id}"
            )
        translated_literals: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = f"6:{base_record_id}:{literal_id}"
            if coordinate in HIDDEN_COMPANION_COORDINATES:
                if base_coordinate in base_rows:
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden Base row appeared: "
                        f"{base_coordinate}"
                    )
                translated = current_literals[literal_id]
                adapted = translated
                owner = "hidden_current_companion"
                base_row = None
            else:
                base_row = base_rows[base_coordinate]
                translated = (
                    TRANSLATIONS[coordinate]
                    if coordinate in TRANSLATIONS
                    else str(prefill_rows[coordinate]["translation"])
                )
                adapted = adapt_outer_whitespace(
                    str(base_row["translation"]),
                    current_literals[literal_id],
                )
                owner = (
                    "segment"
                    if coordinate in TRANSLATIONS
                    else "prefill_companion"
                )
                expected_translation = adapted
                if coordinate == "6:3768:1":
                    expected_translation = "에게 원군 등\n군사적"
                if (
                    translated != expected_translation
                    or not base_row_is_approved(base_row)
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base wording drifted: "
                        f"{coordinate}"
                    )
            translated_literals.append(translated)
            verification = (
                {}
                if base_row is None
                else base_row.get("runtime_vm_verification", {})
            )
            base_context.append(
                (
                    coordinate,
                    base_coordinate,
                    source_literals[literal_id],
                    base_source_literals[literal_id],
                    current_literals[literal_id],
                    base_current_literals[literal_id],
                    (
                        None
                        if base_row is None
                        else base_row.get("translation")
                    ),
                    adapted,
                    translated,
                    owner,
                    (
                        None
                        if base_row is None
                        else base_row.get("semantic_review")
                    ),
                    (
                        None
                        if base_row is None
                        else base_row.get("runtime_review")
                    ),
                    verification.get("method"),
                    verification.get("result"),
                    verification.get("row_verification_sha256"),
                )
            )
        assembly_kind = (
            "raw_exact"
            if record_id in RAW_EXACT_BASE_RECORD_IDS
            else (
                "operand_masked"
                if record_id in OPERAND_MASKED_BASE_RECORD_IDS
                else "pk_exclusive_semantic_donor"
            )
        )
        assembly = (
            record_id,
            base_record_id,
            tuple(translated_literals),
            tuple(
                value.hex().upper()
                for value in gap_bytes(source_record)
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(base_source_record)
            ),
            runtime_controls(source_record),
            runtime_controls(base_source_record),
            assembly_kind,
        )
        assemblies.append(assembly)
        if record_id in PK_EXCLUSIVE_SEMANTIC_RECORD_IDS:
            exclusive_evidence.append(
                (
                    assembly,
                    source_literals,
                    base_source_literals,
                    source_literals != base_source_literals,
                    gap_bytes(source_record)
                    != gap_bytes(base_source_record),
                    SPEAKER_STYLE[record_id],
                )
            )
    guarded_digest(
        "Base context",
        tuple(base_context),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "complete assembly",
        tuple(assemblies),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )
    if (
        tuple(row[0][0] for row in exclusive_evidence)
        != PK_EXCLUSIVE_SEMANTIC_RECORD_IDS
        or any(
            not source_diff or not gap_diff
            for (
                _,
                _,
                _,
                source_diff,
                gap_diff,
                _,
            ) in exclusive_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK-exclusive donor drifted"
        )
    guarded_digest(
        "PK-exclusive semantic donor",
        tuple(exclusive_evidence),
        EXPECTED_PK_EXCLUSIVE_SHA256,
    )


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    conflict_evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = BASE.BASE.BASE.reachable_call_graph(
            current_records,
            (0, operand),
        )
        terminal_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in terminals
        )
        if (
            not graph
            or not terminals
            or any(len(values) > 1 for values in terminal_literals)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        terminal_set = {
            values[0]
            for values in terminal_literals
            if values
        }
        evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
        if operand in EXPECTED_CONFLICT_TERMINAL_SETS:
            expected_set = EXPECTED_CONFLICT_TERMINAL_SETS[operand]
            if terminal_set != expected_set:
                raise RuntimeError(
                    f"segment {SEGMENT} conflict terminal drifted: "
                    f"{operand}"
                )
            conflict_evidence.append(
                (
                    operand,
                    tuple(sorted(terminal_set)),
                    "all_branch_korean_morphology_conflict",
                )
            )
    guarded_digest(
        "call graph",
        tuple(evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    conflict_summary = (
        tuple(conflict_evidence),
        RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        (
            3766,
            (1198, 1096),
            "two_live_suffix_calls_cannot_compose_grammatically",
        ),
        (
            3768,
            (1174, 1168, 748),
            "literal_honorific_prefix_calls_and_negative_suffix_conflict",
        ),
        False,
    )
    guarded_digest(
        "runtime conflict",
        conflict_summary,
        EXPECTED_RUNTIME_CONFLICT_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        tuple(TERMINOLOGY_POLICY.items()),
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or TRANSLATIONS["6:3765:0"] != ","
        or TRANSLATIONS["6:3766:1"] != "까?"
        or TRANSLATIONS["6:3768:1"] != "에게 원군 등\n군사적"
        or TRANSLATIONS["6:3768:4"] != "까?"
        or TRANSLATIONS["6:3769:4"] != "까?"
        or TRANSLATIONS["6:3778:1"] != "\n좋은 방안"
        or len(STATIC_COORDINATES) != 11
        or len(DYNAMIC_COORDINATES) != 15
        or "귀가" in "\n".join(TRANSLATIONS.values())
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        layout = (
            "unchanged_from_current"
            if coordinate in STATIC_COORDINATES
            else "runtime_pending"
        )
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            layout,
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


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_base_globals()
    return BASE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted"
        )
    static = record_id in STATIC_RECORD_IDS
    conflict = (
        record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    )
    return {
        "runtime_category": (
            "static_alliance_acceptance"
            if static
            else (
                "pk_exclusive_live_morphology_conflict"
                if conflict
                else "pk_calls_and_dynamic_tokens_base_semantic_donor"
            )
        ),
        "speaker_style": SPEAKER_STYLE[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(source_record)
            )
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(current_record)
            )
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source_record) == gap_bytes(current_record),
        "dotall_operand_scan_used": True,
        "base_record_coordinate":
        f"6:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": (
            "raw_exact"
            if record_id in RAW_EXACT_BASE_RECORD_IDS
            else (
                "operand_masked"
                if record_id in OPERAND_MASKED_BASE_RECORD_IDS
                else "pk_exclusive_semantic_donor"
            )
        ),
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "hidden_companions_reviewed": True,
        "live_pk_call_graphs_reviewed": not static,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": not conflict,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "runtime_review_required": not static,
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
    patch_base_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_and_assembly(prepared, records_by_label)
    assert_call_graphs(prepared)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification": (
                    "retranslated"
                    if static
                    else "runtime_fragment_pending"
                ),
                "layout_review": (
                    "unchanged_from_current"
                    if static
                    else "runtime_pending"
                ),
                "runtime_review": (
                    "not_required"
                    if static
                    else "pending"
                ),
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "hidden_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records_by_label, record_id),
            }
        )
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
    patch_base_globals()
    BASE.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
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
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    if DISCOVERED_PINS:
        print(
            json.dumps(
                {
                    **DISCOVERED_PINS,
                    "candidate": candidate_sha256,
                    "changed literal count": changed,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2

    steam_before = sha256_bytes(STEAM_PK.read_bytes())
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
        len(rows) != 26
        or len(validated) != 26
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 15,
                "retranslated": 11,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
            if row["coordinate"] in STATIC_COORDINATES
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            for row in rows
            if row["coordinate"] in DYNAMIC_COORDINATES
        )
        or any(
            row["runtime_assembly_evidence"][
                "runtime_morphology_conflict_detected"
            ]
            is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
            if coordinate_key(str(row["coordinate"]))[1]
            in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B039_S1128",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 114,
                "queue_visible_count": 198,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 41,
                "residual_count": 26,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "static_record_count": len(STATIC_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "pk_exclusive_semantic_record_count":
                len(PK_EXCLUSIVE_SEMANTIC_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_companion_count":
                len(HIDDEN_COMPANION_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
                "runtime_morphology_conflict_record_count":
                len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
                "optional_neighbors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "call_graph_sha256":
                EXPECTED_CALL_GRAPH_SHA256,
                "runtime_conflict_sha256":
                EXPECTED_RUNTIME_CONFLICT_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "canonical_local_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "hidden_companions_guarded": True,
                "dotall_call_operand_scanner_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "runtime_morphology_conflicts_guarded": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
                "speaker_registers_reviewed": True,
                "historical_terminology_reviewed": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
