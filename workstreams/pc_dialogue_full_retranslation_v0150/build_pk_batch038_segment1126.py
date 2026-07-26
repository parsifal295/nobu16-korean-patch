#!/usr/bin/env python3
"""Build source-redacted PK B038 segment 1126 residual decisions."""

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
    WORKSTREAM / "build_pk_batch037_segment1123.py"
)
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B038_S1126.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B037_S1124.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B038_S1125.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B038_S1127.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1126
QUEUE_BATCH_ID = "pk_msggame-B038"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 3644
QUEUE_LAST_RECORD = 3751

TARGET_COORDINATES = (
    "6:3681:0",
    "6:3682:0",
    "6:3683:0",
    "6:3684:0",
    "6:3685:0",
    "6:3685:1",
    "6:3686:0",
    "6:3687:0",
    "6:3688:0",
    "6:3688:1",
    "6:3689:0",
    "6:3690:0",
    "6:3692:0",
    "6:3694:0",
    "6:3695:0",
)
TRANSLATIONS = {
    "6:3681:0": "의",
    "6:3682:0": "의",
    "6:3683:0": "의",
    "6:3684:0": "을(를)",
    "6:3685:0": ",",
    "6:3685:1": "이(가)",
    "6:3686:0": "을(를)",
    "6:3687:0": "을(를)",
    "6:3688:0": ",",
    "6:3688:1": "을(를)",
    "6:3689:0": "을(를)",
    "6:3690:0": "을(를)",
    "6:3692:0": "을(를)",
    "6:3694:0": "을(를)",
    "6:3695:0": "을(를)",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3681,
    3682,
    3683,
    3684,
    3685,
    3686,
    3687,
    3688,
    3689,
    3690,
    3692,
    3694,
    3695,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BASE_RECORD_MAPPING = {
    3681: 3674,
    3682: 3675,
    3683: 3676,
    3684: 3677,
    3685: 3678,
    3686: 3679,
    3687: 3680,
    3688: 3681,
    3689: 3682,
    3690: 3683,
    3692: 3685,
    3694: 3687,
    3695: 3688,
}
RAW_EXACT_BASE_RECORD_IDS = (3681, 3682, 3687, 3689)
OPERAND_MASKED_BASE_RECORD_IDS = (
    3683,
    3684,
    3685,
    3686,
    3688,
    3690,
    3692,
    3694,
    3695,
)
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
EXPECTED_ARITY = {
    3681: 2,
    3682: 2,
    3683: 3,
    3684: 2,
    3685: 3,
    3686: 2,
    3687: 2,
    3688: 3,
    3689: 2,
    3690: 2,
    3692: 2,
    3694: 2,
    3695: 2,
}
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
)
LEFT_BOUNDARY_RECORD_ID = 3680
LEFT_BOUNDARY_BASE_RECORD_ID = 3673
LEFT_BOUNDARY_COORDINATES = (
    "6:3680:0",
    "6:3680:1",
    "6:3680:2",
)
BOUNDARY_RECORD_IDS = (
    3679,
    3680,
    3691,
    3693,
    3696,
    3715,
    3716,
    3717,
)
EXPECTED_GAPS_BY_RECORD = {
    3681: ("014301000000", "023C", "050505"),
    3682: ("014301000000", "023C", "050505"),
    3683: (
        "014301000000",
        "023C",
        "014301000000",
        "01430A030000050505",
    ),
    3684: (
        "014301000000",
        "023C",
        "014326020000050505",
    ),
    3685: (
        "0143D6000000",
        "014301000000",
        "023C",
        "014326020000050505",
    ),
    3686: (
        "014301000000",
        "023C",
        "0143E6020000050505",
    ),
    3687: (
        "014301000000",
        "023C",
        "014318010000050505",
    ),
    3688: (
        "0143D6000000",
        "014301000000",
        "023C",
        "0143E6020000050505",
    ),
    3689: (
        "014301000000",
        "023C",
        "014352000000050505",
    ),
    3690: (
        "014301000000",
        "023C",
        "014326020000050505",
    ),
    3692: (
        "014301000000",
        "023C",
        "014326020000050505",
    ),
    3694: (
        "014301000000",
        "023C",
        "0143E6020000050505",
    ),
    3695: (
        "014301000000",
        "023C",
        "014326020000050505",
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3681: ((1,), ("023C",)),
    3682: ((1,), ("023C",)),
    3683: ((1, 1, 778), ("023C",)),
    3684: ((1, 550), ("023C",)),
    3685: ((214, 1, 550), ("023C",)),
    3686: ((1, 742), ("023C",)),
    3687: ((1, 280), ("023C",)),
    3688: ((214, 1, 742), ("023C",)),
    3689: ((1, 82), ("023C",)),
    3690: ((1, 550), ("023C",)),
    3692: ((1, 550), ("023C",)),
    3694: ((1, 742), ("023C",)),
    3695: ((1, 550), ("023C",)),
}
EXPECTED_LEFT_BOUNDARY_GAPS = (
    "01438E030000",
    "014301000000",
    "023C",
    "014342010000050505",
)
EXPECTED_LEFT_BOUNDARY_CONTROLS = (
    (910, 1, 322),
    ("023C",),
)
EXPECTED_CALL_ROOTS = (
    1,
    82,
    214,
    280,
    322,
    550,
    742,
    778,
    910,
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
    "90A0C0FC8686409234C2F7DEA89E00D72A4DD0DD509C14CF4FA831E880A82B10"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "57550669A250340C5A941BD6E00166FE1F6E0DA94C12E2191970F47A857B07C0"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "51628EC42EC3DC68EDDFFD5552C22AF3109EE06A670A3A5F20AC832CDF7826BF"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "D30201B9FD02A04FF6990D5ECCCF1E56A9E1269AE6D60C183D8D90595645658A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7B917B619FE1A5CE506D678E684B0C9D91F0E23B1CECFA112669F51D2F33E9A5"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "F9940AEDDB3B26A3E9E0636D65C761FFD02F9EDB3DD2D30FBA3491C8A73AE3D0"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "C4EB66E3F9A5DC6F76C4644CC47C0FB04C06E631F87B20A1A7492A1ADED10843"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1E42A2DFC8D5E1DFA691D6293AC37104D08F4F2AFF48559E586B7960C4F07754"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D8FC52D65AD89DF52A7935C00793276E07D645D4E86CB0E3D22AF0F623F80504"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1DF4E7DFB0F3233E24B5E424821B51EC174F1337A93249828BD2CB0996AC68C1"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "90288E8F8E30E6E8779058BDD68895C293F9FC1B8C36408AEE30C7A643F545BF"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "C0972EC747613D39BB980C8FCE8FC21518637FD15E8F12A6F5A75E35B25C45ED"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "7F4A9D5154B45931EACA8A285997F373D752F04DEAEE04DABB7C7AD66280A269"
)
EXPECTED_LEFT_BOUNDARY_SHA256 = (
    "AC791850BB812B48FB06DBEB5230C286BAA4674145C7F4EF82BC49BF16AD11CF"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "33032B1B95DD4D9C080D17C75B0DEAFC7A407A65D0974106B7613D1691C71A49"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "998BE15618BB1CC968EA1565324C0CA734F69E12C92E3D339806F726F47D92C5"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "BE6E491B045668BD7A51ACEC07B43A424D33B71209DFA85A6ED926374274E021"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "D997053A3CE91C24204CB7A2A04D48D36D22CF46A051834D9BC4D7362E9F8C74"
)
EXPECTED_CANDIDATE_SHA256 = (
    "0F90FB8366FC36BD66ECEA20ED3CD0842DBF8F637B2A34060C528AE14DE32CDD"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12

DISCOVERED_PINS: dict[str, str] = {}

SPEAKER_STYLE = {
    3681: "shocked_informal_rhetorical_confiscation_protest",
    3682: "resigned_formal_retainer_accepting_lords_decision",
    3683: "protective_formal_objection_to_confiscation",
    3684: "humble_delight_at_office_nomination",
    3685: "surprised_delight_at_office_nomination",
    3686: "formal_gratitude_at_office_nomination",
    3687: "high_formal_gratitude_at_office_nomination",
    3688: "surprised_formal_gratitude_at_office_nomination",
    3689: "confident_colloquial_response_to_nomination",
    3690: "formal_honor_response_to_nomination",
    3692: "formal_unexpected_joy_at_nomination",
    3694: "formal_gratitude_at_nomination",
    3695: "formal_high_honor_at_nomination",
}
TERMINOLOGY_POLICY = {
    "confiscation_feudal_register": "거두어 가다",
    "office_nomination": "천거",
    "office_token": "023C",
    "unexpected_joy": "뜻밖의 기쁨",
    "highest_honor": "더없는 영광",
    "genitive_particle": "의",
    "object_particle": "을(를)",
    "subject_particle": "이(가)",
    "runtime_punctuation": ",",
}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; all fifteen residual fragments "
    "use completed Base semantic donors with identical Japanese literal "
    "sequences; four records are byte-exact Base matches and nine retain "
    "the same operand-masked runtime layout with PK-specific call "
    "operands; fourteen same-record prefill companions complete all "
    "thirteen target records; split boundary record 3680 is assembled "
    "from its hidden leading line-feed literal, optional prior-segment "
    "genitive fragment and in-slice prefill fragment, with optional "
    "neighbor presence excluded from pinned evidence; live PK call graphs "
    "and terminal text for all nine referenced roots include both 0143 "
    "and 014A traversal; the direct-call scanner uses DOTALL so operand "
    "778 containing byte 0A is not lost; confiscation and office "
    "nomination feudal register, Korean particle placeholders, office "
    "token 023C, punctuation, protected spaces, line counts, bytecode "
    "gaps, reverse overlay, two-run reproduction, tamper rejection, "
    "outside-scope records and read-only inputs are guarded; Base runtime "
    "verification is not inherited and every PK fragment remains runtime "
    "pending"
)


def load_base_builder() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1126_base",
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
        len(queue_rows) != 108
        or len(visible) != 199
        or queue_rows[0]["record_coordinate"] != "6:3644"
        or queue_rows[-1]["record_coordinate"] != "6:3751"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
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
        or queue_slice[0] != "6:3680:2"
        or queue_slice[-1] != "6:3716:0"
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
        len(prefilled) != 52
        or residual != TARGET_COORDINATES
        or len(PREFILL_COMPANION_COORDINATES) != 14
        or any(
            coordinate not in prefilled
            for coordinate in PREFILL_COMPANION_COORDINATES
        )
        or "6:3680:2" not in prefilled
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
    ):
        raise RuntimeError(
            f"segment {SEGMENT} visibility drifted"
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
    neighbor_rows = decision_map("pk_msggame")
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
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or source_literals != base_source_literals
        ):
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
            base_row = base_rows[base_coordinate]
            verification = base_row.get(
                "runtime_vm_verification",
                {},
            )
            translated = (
                TRANSLATIONS[coordinate]
                if coordinate in TRANSLATIONS
                else str(prefill_rows[coordinate]["translation"])
            )
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                current_literals[literal_id],
            )
            translated_literals.append(translated)
            base_context.append(
                (
                    coordinate,
                    base_coordinate,
                    source_literals[literal_id],
                    base_source_literals[literal_id],
                    current_literals[literal_id],
                    base_current_literals[literal_id],
                    base_row.get("translation"),
                    adapted,
                    translated,
                    (
                        "segment"
                        if coordinate in TRANSLATIONS
                        else "prefill_companion"
                    ),
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                    verification.get("method"),
                    verification.get("result"),
                    verification.get("row_verification_sha256"),
                )
            )
            if (
                translated != adapted
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or verification.get("method")
                != "reversed_vm_static_analysis"
                or verification.get("result") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base wording drifted: "
                    f"{coordinate}"
                )
        assemblies.append(
            (
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
                (
                    "raw_exact"
                    if record_id in RAW_EXACT_BASE_RECORD_IDS
                    else "operand_masked"
                ),
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

    left_source_record = pk_source[
        (BLOCK_ID, LEFT_BOUNDARY_RECORD_ID)
    ]
    left_current_record = pk_current[
        (BLOCK_ID, LEFT_BOUNDARY_RECORD_ID)
    ]
    left_base_source_record = base_source[
        (BLOCK_ID, LEFT_BOUNDARY_BASE_RECORD_ID)
    ]
    left_source_literals = literal_texts(
        pk_source,
        (BLOCK_ID, LEFT_BOUNDARY_RECORD_ID),
    )
    left_current_literals = literal_texts(
        pk_current,
        (BLOCK_ID, LEFT_BOUNDARY_RECORD_ID),
    )
    left_base_source_literals = literal_texts(
        base_source,
        (BLOCK_ID, LEFT_BOUNDARY_BASE_RECORD_ID),
    )
    left_translated: list[str] = []
    left_rows: list[tuple[Any, ...]] = []
    for literal_id, coordinate in enumerate(
        LEFT_BOUNDARY_COORDINATES
    ):
        base_coordinate = (
            f"6:{LEFT_BOUNDARY_BASE_RECORD_ID}:{literal_id}"
        )
        if literal_id == 0:
            if base_coordinate in base_rows:
                raise RuntimeError(
                    f"segment {SEGMENT} hidden Base row appeared"
                )
            translated = left_current_literals[literal_id]
            adapted = translated
            owner = "hidden_current_literal"
            optional_translation = None
        else:
            base_row = base_rows[base_coordinate]
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                left_current_literals[literal_id],
            )
            optional_translation = (
                neighbor_rows.get(coordinate, {}).get("translation")
            )
            if literal_id == 1:
                translated = adapted
                owner = "optional_prior_segment_base_companion"
            else:
                translated = str(
                    prefill_rows[coordinate]["translation"]
                )
                owner = "in_slice_prefill_companion"
            if (
                translated != adapted
                or (
                    optional_translation is not None
                    and optional_translation != adapted
                )
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} left boundary drifted: "
                    f"{coordinate}"
                )
        left_translated.append(translated)
        left_rows.append(
            (
                coordinate,
                base_coordinate,
                left_source_literals[literal_id],
                left_base_source_literals[literal_id],
                left_current_literals[literal_id],
                adapted,
                translated,
                owner,
                (
                    "optional_neighbor_matches_when_present"
                    if literal_id == 1
                    else "not_optional"
                ),
            )
        )
    left_evidence = (
        tuple(left_rows),
        tuple(left_translated),
        tuple(
            value.hex().upper()
            for value in gap_bytes(left_source_record)
        ),
        tuple(
            value.hex().upper()
            for value in gap_bytes(left_current_record)
        ),
        tuple(
            value.hex().upper()
            for value in gap_bytes(left_base_source_record)
        ),
        runtime_controls(left_source_record),
        runtime_controls(left_current_record),
        mask_call_operands(gap_bytes(left_source_record)),
        mask_call_operands(gap_bytes(left_base_source_record)),
    )
    if (
        left_source_literals != left_base_source_literals
        or tuple(
            value.hex().upper()
            for value in gap_bytes(left_source_record)
        )
        != EXPECTED_LEFT_BOUNDARY_GAPS
        or gap_bytes(left_current_record)
        != gap_bytes(left_source_record)
        or runtime_controls(left_source_record)
        != EXPECTED_LEFT_BOUNDARY_CONTROLS
        or mask_call_operands(gap_bytes(left_source_record))
        != mask_call_operands(gap_bytes(left_base_source_record))
        or (
            "pk_msggame",
            BLOCK_ID,
            LEFT_BOUNDARY_RECORD_ID,
            0,
        )
        in prepared.visible_targets
        or (
            "pk_msggame",
            BLOCK_ID,
            LEFT_BOUNDARY_RECORD_ID,
            1,
        )
        not in prepared.visible_targets
        or (
            "pk_msggame",
            BLOCK_ID,
            LEFT_BOUNDARY_RECORD_ID,
            2,
        )
        not in prepared.visible_targets
    ):
        raise RuntimeError(
            f"segment {SEGMENT} left boundary layout drifted"
        )
    guarded_digest(
        "left boundary",
        left_evidence,
        EXPECTED_LEFT_BOUNDARY_SHA256,
    )


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = BASE.BASE.reachable_call_graph(
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
        evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
    guarded_digest(
        "call graph",
        tuple(evidence),
        EXPECTED_CALL_GRAPH_SHA256,
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
        or any(
            TRANSLATIONS[coordinate] != "의"
            for coordinate in (
                "6:3681:0",
                "6:3682:0",
                "6:3683:0",
            )
        )
        or TRANSLATIONS["6:3685:0"] != ","
        or TRANSLATIONS["6:3685:1"] != "이(가)"
        or TRANSLATIONS["6:3688:0"] != ","
        or any(
            TRANSLATIONS[coordinate] != "을(를)"
            for coordinate in (
                "6:3684:0",
                "6:3686:0",
                "6:3687:0",
                "6:3688:1",
                "6:3689:0",
                "6:3690:0",
                "6:3692:0",
                "6:3694:0",
                "6:3695:0",
            )
        )
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
    return {
        "runtime_category":
        "pk_direct_calls_and_office_token_base_semantic_donor",
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
            else "operand_masked"
        ),
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "split_left_boundary_record_reviewed": True,
        "live_pk_call_graphs_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
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
                "scope_classification":
                "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
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
                "left_boundary_record_reviewed": True,
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
        len(rows) != 15
        or len(validated) != 15
        or counts != Counter({"runtime_fragment_pending": 15})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            or row["runtime_assembly_evidence"][
                "dotall_operand_scan_used"
            ]
            is not True
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
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
                "segment": "pk_msggame_B038_S1126",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 108,
                "queue_visible_count": 199,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 52,
                "residual_count": 15,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "left_boundary_companion_count":
                len(LEFT_BOUNDARY_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
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
                "canonical_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "split_left_boundary_3680_guarded": True,
                "dotall_call_operand_scanner_guarded": True,
                "live_pk_call_graphs_guarded": True,
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
