#!/usr/bin/env python3
"""Build source-redacted PK B058 segment 1185 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch057_segment1182.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B058_S1185.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B058_S1186.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1185
QUEUE_BATCH_ID = "pk_msggame-B058"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:1005:0", "7:1007:0", "7:1009:0", "7:1018:0",
    "7:1024:0", "7:1025:0", "7:1026:0", "7:1027:0",
    "7:1028:0", "7:1029:0", "7:1030:0", "7:1031:0",
    "7:1032:0", "7:1033:0", "7:1034:0", "7:1035:0",
    "7:1036:0",
    "7:1037:0", "7:1037:1",
    "7:1038:0", "7:1038:1",
    "7:1039:0", "7:1040:0", "7:1041:0", "7:1042:0",
    "7:1043:0", "7:1044:0", "7:1045:0", "7:1046:0",
    "7:1047:0",
)
DEFEAT_RECOVERY = (
    "상대에게 이토록 패하다니……\n"
    "우리 가문이 싸울 때를 잘못 헤아렸는지도 모르겠군\n"
    "이 피해로는 당분간 싸우기 어렵겠군……"
)
ELDER_SELF_PRESERVATION = (
    "대패로다……! 이제 싸울 때가 아니다!\n"
    "배반자가 나오지 않도록 서둘러 영내를 안정시켜야 한다\n"
    "……아니, 내 거취부터 숙고해야 하나?"
)
ELDER_STABILIZATION = (
    "대패로다……! 이제 싸울 때가 아니다!\n"
    "배반자가 나오지 않도록 서둘러 영내를 안정시켜야 한다"
)
INTERNAL_GOVERNANCE = (
    "이번 패배는 제법 뼈아프군……\n"
    "여기서 중요한 것은 이반을 막는 일\n"
    "우선 성하 통제에 힘쓰도록 하지"
)
POLITE_DISADVANTAGE_CONTROL = (
    "에게 패하고 말았군요……\n"
    "중요한 것은 열세를 틈탄 배신자가 나오지 않게 하는 일\n"
    "우선 성하 통제에 힘쓰도록 하지요"
)
POLITE_WEAKNESS_CONTROL = (
    "에게 패하고 말았군요……\n"
    "중요한 것은 약점을 틈탄 배신자가 나오지 않게 하는 일\n"
    "우선 성하 통제에 힘쓰도록 하지요"
)
TRANSLATIONS = {
    "7:1005:0": (
        "에게 패한 것을 이러쿵저러쿵 말하지는 않겠으나\n"
        "하나를 보면 열을 안다고 하지\n"
        "앞으로의"
    ),
    "7:1007:0": "이(가) 「",
    "7:1009:0": "에게 진 것입니까……\n",
    "7:1018:0": "을(를) 굴복시키다니\n",
    "7:1024:0": (
        "대패다……! 이제 싸울 때가 아니다!\n"
        "배반자가 나오지 않도록 서둘러 영내를 안정시켜야 한다\n"
        "……아니, 내 거취부터 생각해야 하나?"
    ),
    "7:1025:0": DEFEAT_RECOVERY,
    "7:1026:0": DEFEAT_RECOVERY,
    "7:1027:0": (
        "에게 패했는가……\n"
        "이를 틈타 영민이 이반하면 곤란하니\n"
        "당분간 내치에 전념해야겠군"
    ),
    "7:1028:0": ELDER_SELF_PRESERVATION,
    "7:1029:0": ELDER_SELF_PRESERVATION,
    "7:1030:0": INTERNAL_GOVERNANCE,
    "7:1031:0": ELDER_SELF_PRESERVATION,
    "7:1032:0": POLITE_DISADVANTAGE_CONTROL,
    "7:1033:0": DEFEAT_RECOVERY,
    "7:1034:0": POLITE_DISADVANTAGE_CONTROL,
    "7:1035:0": DEFEAT_RECOVERY,
    "7:1036:0": (
        "대패다……! 이제 싸울 때가 아니다!\n"
        "배반자가 나오지 않도록 서둘러 영내를 안정시켜야 한다"
    ),
    "7:1037:0": "상대에게 이토록 패하다니……\n",
    "7:1037:1": (
        "은(는) 싸울 때를 잘못 헤아렸는지도 모르겠군\n"
        "이 피해로는 당분간 싸우기 어렵겠군……"
    ),
    "7:1038:0": "상대에게 이토록 패하다니……\n",
    "7:1038:1": (
        "은(는) 싸울 때를 잘못 헤아렸는지도 모르겠군\n"
        "이 피해로는 당분간 싸우기 어렵겠군……"
    ),
    "7:1039:0": (
        "에게 패했는가……\n"
        "이를 틈타 영민이 이반하면 곤란하니\n"
        "당분간 내치에 전념해야겠군"
    ),
    "7:1040:0": ELDER_STABILIZATION,
    "7:1041:0": ELDER_STABILIZATION,
    "7:1042:0": INTERNAL_GOVERNANCE,
    "7:1043:0": ELDER_SELF_PRESERVATION,
    "7:1044:0": POLITE_WEAKNESS_CONTROL,
    "7:1045:0": DEFEAT_RECOVERY,
    "7:1046:0": POLITE_WEAKNESS_CONTROL,
    "7:1047:0": "상대에게 이토록 패하다니……\n",
}
TARGET_RECORD_IDS = tuple(
    dict.fromkeys(
        int(coordinate.split(":")[1])
        for coordinate in TARGET_COORDINATES
    )
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    1005: 2,
    1007: 2,
    1009: 2,
    1018: 2,
    **{record_id: 1 for record_id in range(1024, 1037)},
    1037: 2,
    1038: 2,
    **{record_id: 1 for record_id in range(1039, 1047)},
    1047: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:1005:1",
    "7:1007:1",
    "7:1009:1",
    "7:1018:1",
)
PREFILL_COMPANION_DONOR = {
    "7:1005:1": "7:989:1",
    "7:1007:1": "7:991:1",
    "7:1009:1": "7:993:1",
    "7:1018:1": "7:1002:1",
}
OUTSIDE_SLICE_COMPANION_COORDINATES = ("7:1047:1",)
EXACT_BASE_DONOR = {
    1007: (7, 991),
    1009: (7, 993),
    1018: (7, 1002),
}
SELF_PRESERVATION_CONTEXT = (
    "6:3904:0", "6:2759:0", "7:993:1", "15:1458:1",
)
RECOVERY_CONTEXT = (
    "6:2759:0", "6:1531:0", "9:2911:0",
)
GOVERNANCE_CONTEXT = (
    "15:1458:1", "6:2760:0", "8:699:0",
)
SEMANTIC_BASE_CONTEXT = {
    1005: ("7:989:0", "7:989:1"),
    1024: SELF_PRESERVATION_CONTEXT,
    1025: RECOVERY_CONTEXT,
    1026: RECOVERY_CONTEXT,
    1027: GOVERNANCE_CONTEXT,
    1028: SELF_PRESERVATION_CONTEXT,
    1029: SELF_PRESERVATION_CONTEXT,
    1030: GOVERNANCE_CONTEXT,
    1031: SELF_PRESERVATION_CONTEXT,
    1032: GOVERNANCE_CONTEXT,
    1033: RECOVERY_CONTEXT,
    1034: GOVERNANCE_CONTEXT,
    1035: RECOVERY_CONTEXT,
    1036: SELF_PRESERVATION_CONTEXT,
    1037: RECOVERY_CONTEXT,
    1038: RECOVERY_CONTEXT,
    1039: GOVERNANCE_CONTEXT,
    1040: SELF_PRESERVATION_CONTEXT,
    1041: SELF_PRESERVATION_CONTEXT,
    1042: GOVERNANCE_CONTEXT,
    1043: SELF_PRESERVATION_CONTEXT,
    1044: GOVERNANCE_CONTEXT,
    1045: RECOVERY_CONTEXT,
    1046: GOVERNANCE_CONTEXT,
    1047: RECOVERY_CONTEXT,
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (
        (EXACT_BASE_DONOR[record_id],)
        if record_id in EXACT_BASE_DONOR
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
        1017, 1018, 1019, 1023, 1024, 1036, 1037, 1038,
        1046, 1047, 1048, 1175, 1176,
    )
)
SOURCE_CALL_ROOTS = (1,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
NO_CONTROL_RECORDS = {
    1024, 1028, 1029, 1030, 1031, 1036, 1040, 1041, 1042, 1043,
}
TOKEN_025032_RECORDS = {
    1025, 1026, 1027, 1032, 1033, 1034, 1035, 1037, 1038,
    1039, 1044, 1045, 1046, 1047,
}
EXPECTED_CONTROLS_BY_RECORD = {
    **{
        record_id: ((), ())
        for record_id in NO_CONTROL_RECORDS
    },
    **{
        record_id: (
            (1,) if record_id in {1037, 1038, 1047} else (),
            ("025032",),
        )
        for record_id in TOKEN_025032_RECORDS
    },
    1005: ((), ("025132", "025032")),
    1007: ((), ("025032", "025132")),
    1009: ((), ("025132", "025032")),
    1018: ((), ("025132", "025032")),
}
SPEAKER_STYLE = (
    (1005, "critical_vassal_judgment"),
    (1007, "polite_defeat_loyalty_reaction"),
    (1009, "polite_defeat_survival_reaction"),
    (1018, "formal_victory_diplomatic_reaction"),
    (1024, "rough_self_preservation_reaction"),
    (1025, "measured_defeat_recovery"),
    (1026, "measured_defeat_recovery"),
    (1027, "civil_governance_defeat_reaction"),
    (1028, "elder_self_preservation_reaction"),
    (1029, "elder_self_preservation_reaction"),
    (1030, "castle_town_control_reaction"),
    (1031, "elder_self_preservation_reaction"),
    (1032, "polite_disadvantage_control_reaction"),
    (1033, "measured_defeat_recovery"),
    (1034, "polite_disadvantage_control_reaction"),
    (1035, "measured_defeat_recovery"),
    (1036, "rough_stabilization_reaction"),
    (1037, "faction_token_defeat_recovery"),
    (1038, "faction_token_defeat_recovery"),
    (1039, "civil_governance_defeat_reaction"),
    (1040, "elder_stabilization_reaction"),
    (1041, "elder_stabilization_reaction"),
    (1042, "castle_town_control_reaction"),
    (1043, "elder_self_preservation_reaction"),
    (1044, "polite_weakness_control_reaction"),
    (1045, "measured_defeat_recovery"),
    (1046, "polite_weakness_control_reaction"),
    (1047, "faction_token_defeat_recovery_boundary"),
)
TERMINOLOGY_POLICY = (
    ("our house", "우리 가문"),
    ("battle opportunity", "싸울 때"),
    ("defection", "이반"),
    ("betrayer", "배신자"),
    ("domain", "영내"),
    ("castle town", "성하"),
    ("civil governance", "내치"),
    ("future allegiance", "거취"),
    ("submission", "굴복"),
    ("temporary recovery period", "당분간"),
)

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
    "4AAA68453D0B5ADA984EDB3ADC13CAF7BD57952640B15351135138705612A808"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "2D5421AB27380C2456C99F514E0924ED5BE503784947922EFD017AB6A8F05B7F"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "A90A53619E0C565E875455A14F4E5F4C65CBC20FBE7F04BB52E1B19BF3E31322"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "A8EBCCB546A2BD6004D640C2ED86D734C4C4F5EAAC467E25787E72E8FEF38A4B"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "969712D9EF5B954EC5C6027DA81BFABEBBFC82908D37A5C0447EDC1979F941E8"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "0EC3DDFAD9B28DDEF1BC4208BDCCBB94C6AC7B19A973B087CDCDED41D24A8D44"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "A115B8AF47236740A638DAA995AAD688885440690DA7737D179D63E7C12D4686"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "CCE35AB5EA30617D091F2A53FF9FA3435E12AC24C9A8B4EB46F9D9DC894EBEC4"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "AF938AA6F4E393D5FD8BB1BB0F7BC7CDA975FDED2AFC26667723B3AF739970CA"
)
EXPECTED_BOUNDARY_SHA256 = (
    "CD07CDD557A66638E1A181BBF1F3B9D88CB74B42EECB4CBC10114234E8B6A5AE"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "CBB900929DACC805903028D2A2500E350A4BEAD3F21E6FD6A7418A895F190925"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "DFBBD9ED8BF2913021F6EEC4221E232C3C28BE645F78B976D8F4A9E5646F096C"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "8111021BF374F082F456358F74BAD05F8C71AB6FB1B24C99201C45142C679644"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "36886B00D3D91DB339357E88EA221EF07E55B0035116C9227647695ADD6B883F"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "638887AC7F4B0F379666C8955C74A6F58B3735FAA1BA1A0CD84583B91B79B2C6"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "B2C359F731D10CF42067E1B517910A542F5990C93BB1118E918BE9DA6A1DB188"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F64999C783A12E76DAC817FC63E675E9CFE0C9FE17D719B22F9AE733BFC1A125"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "34A74C9E213BBC24DD5745BB0BBC6382412A98554069005B6751ED833D6BA768"
)
EXPECTED_CHANGED_LITERAL_COUNT = 30
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 60

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; three complete records use completed Base "
    "literal donors, one near-identical record uses the completed Base "
    "wording as manual semantic context, and twenty-four PK-only defeat, "
    "defection, domain stabilization, castle-town control, recovery and "
    "future-allegiance records use manually selected completed Base semantic "
    "context only; Base runtime and VM state are never inherited; all "
    "thirty-seven queue prefills, four same-record prefill companions and "
    "one outside-slice current companion are guarded; complete records, "
    "direct calls, faction tokens, protected outer whitespace, queue and "
    "segment boundaries, two-run reproduction, tamper rejection, reverse "
    "overlays, outside-scope identity, and Steam read-only state are guarded"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1185_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
CORE = PARENT.CORE
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 174
        or len(visible) != 200
        or visible[0] != "7:1003:0"
        or visible[-1] != "7:1176:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B058 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:1003:0"
        or queue_slice[-1] != "7:1047:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in prefill_rows
    )
    if len(prefilled) != 37 or residual != TARGET_COORDINATES:
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_outside: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and CORE.mask_call_operands(record)
                == CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
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
        donor_rows: list[dict[str, Any]] = []
        for donor_coordinate in donor_coordinates:
            row = base_rows.get(donor_coordinate)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(row)
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual")
                seen_target.add(coordinate)
                continue
            if coordinate in PREFILL_COMPANION_COORDINATES:
                prefill = prefill_rows.get(coordinate)
                if (
                    prefill is None
                    or prefill.get("semantic_review") != "approved"
                    or prefill.get("runtime_review") != "pending"
                    or prefill["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append("base_exact_prefill_runtime_pending")
                seen_prefill.add(coordinate)
                continue
            if coordinate in OUTSIDE_SLICE_COMPANION_COORDINATES:
                assembled.append(current_literals[literal_id])
                owners.append("current_outside_slice")
                seen_outside.add(coordinate)
                continue
            raise RuntimeError(
                f"segment {SEGMENT} assembly ownership missing: {coordinate}"
            )
        donor_translations = tuple(
            str(row["translation"]) for row in donor_rows
        )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment {SEGMENT} exact donor assembly drifted: "
                f"{record_id}"
            )
        if (
            record_id == 1005
            and tuple(assembled) != donor_translations
        ):
            raise RuntimeError(
                f"segment {SEGMENT} near-exact donor assembly drifted"
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                donor_coordinates,
                tuple(
                    (
                        coordinate,
                        str(row["translation"]),
                        str(row["runtime_review"]),
                    )
                    for coordinate, row in zip(
                        donor_coordinates,
                        donor_rows,
                    )
                ),
                "complete_exact" if exact else "semantic_context_only",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                donor_translations,
                CORE.runtime_controls(source),
                CORE.runtime_controls(records_by_label["current"][key]),
                (
                    "complete_translation_equals_completed_base_donor"
                    if exact
                    else "near_exact_completed_base_semantic_reuse"
                    if record_id == 1005
                    else "manual_pk_semantic_adaptation"
                ),
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_outside != set(OUTSIDE_SLICE_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 67
        or len(prefilled) != 37
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if (
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_COMBINED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined changed count drifted: {changed}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = CORE.runtime_controls(source)
    current_controls = CORE.runtime_controls(current)
    exact = record_id in EXACT_BASE_DONOR
    references = (
        tuple(
            f"{EXACT_BASE_DONOR[record_id][0]}:"
            f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        if exact
        else SEMANTIC_BASE_CONTEXT[record_id]
    )
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": CORE.canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": CORE.canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_complete_record_match_kind": (
            "raw_literal_and_operand_exact"
            if exact
            else "none_semantic_context_only"
        ),
        "base_context_reference_coordinates": references,
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "outside_slice_current_companion_reviewed":
        any(
            coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
            for coordinate in OUTSIDE_SLICE_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_donor_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
        "EXACT_BASE_DONOR": EXACT_BASE_DONOR,
        "SEMANTIC_BASE_CONTEXT": SEMANTIC_BASE_CONTEXT,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT":
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.base_and_assembly_evidence = base_and_assembly_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    PARENT.runtime_evidence = runtime_evidence
    PARENT.patch_parent_globals()
    grandparent = PARENT.PARENT
    grandparent.queue_evidence = queue_evidence
    grandparent.base_and_assembly_evidence = base_and_assembly_evidence
    grandparent.build_combined_slice_candidate = (
        build_combined_slice_candidate
    )
    grandparent.runtime_evidence = runtime_evidence
    CORE.queue_evidence = queue_evidence
    CORE.base_and_assembly_evidence = base_and_assembly_evidence


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    str,
    int,
    tuple[str, ...],
]:
    patch_parent_globals()
    result = PARENT.build_rows()
    for row in result[1]:
        record_id = int(str(row["coordinate"]).split(":")[1])
        row["outside_slice_current_companion_reviewed"] = (
            record_id == 1047
        )
    return result


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    if DISCOVERED_PINS:
        print(json.dumps(
            DISCOVERED_PINS,
            sort_keys=True,
            separators=(",", ":"),
        ))
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
        len(rows) != 30
        or len(validated) != 30
        or counts != Counter({"runtime_fragment_pending": 30})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["base_runtime_state_inherited"] is not False
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    patch_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B058_S1185",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 37,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "outside_slice_current_companion_count":
        len(OUTSIDE_SLICE_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count":
        len(EXACT_BASE_DONOR),
        "masked_complete_base_donor_record_count": 0,
        "semantic_base_context_record_count":
        len(SEMANTIC_BASE_CONTEXT),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
        "candidate_sha256": candidate_sha256,
        "combined_slice_candidate_sha256": combined_sha256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "steam_sha256_before": steam_before,
        "steam_sha256_after": steam_after,
        "base_runtime_state_inherited": False,
        "source_current_gap_equality_guarded": True,
        "inline_token_controls_guarded": True,
        "direct_call_graphs_guarded": True,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
