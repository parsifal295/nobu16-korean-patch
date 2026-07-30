#!/usr/bin/env python3
"""Build source-redacted PK B030 segment 1103 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch014_segment1063.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B030_S1103.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B030_S1101.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B030_S1102.private.v1.jsonl",
)

SEGMENT = 1103
QUEUE_BATCH_ID = "pk_msggame-B030"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 2615
QUEUE_LAST_RECORD = 2758

TARGET_COORDINATES = (
    "6:2725:0",
    "6:2731:0",
    "6:2737:0",
    "6:2746:0",
    "6:2750:0",
    "6:2751:0",
    "6:2753:0",
    "6:2756:0",
    "6:2758:0",
    "6:2758:1",
)
TRANSLATIONS = {
    "6:2725:0": "우리 가문이 약한 탓이다, ",
    "6:2731:0": "지금은,",
    "6:2737:0": "지금은,",
    "6:2746:0": "눈앞을 가로막는 것은, ",
    "6:2750:0": "무위로 쓰러뜨리는 것이 최선이지만,\n",
    "6:2751:0": "적은,",
    "6:2753:0": "우리 가문을,",
    "6:2756:0": "우리 가문이,",
    "6:2758:0": "앞으로,",
    "6:2758:1": (
        " 와(과) 다툴 때를 대비해\n"
        "외교에서 활로를 찾고자 하옵니다"
    ),
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    2725,
    2731,
    2737,
    2746,
    2750,
    2751,
    2753,
    2756,
    2758,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
COMPLETE_SEGMENT_RECORD_IDS = (2758,)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:1"
    for record_id in TARGET_RECORD_IDS
    if record_id not in COMPLETE_SEGMENT_RECORD_IDS
)
HIDDEN_COORDINATES: tuple[str, ...] = ()
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in TARGET_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
BOUNDARY_RECORD_IDS = (
    2719,
    2724,
    2726,
    2730,
    2732,
    2736,
    2738,
    2745,
    2747,
    2749,
    2752,
    2754,
    2755,
    2757,
    2759,
)
EXPECTED_GAPS_BY_RECORD = {
    record_id: ("", "025032", "050505")
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_DIRECT_CALLS = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_INLINE_TOKENS = {
    record_id: ("025032",)
    for record_id in TARGET_RECORD_IDS
}
RUNTIME_CATEGORY = {
    record_id: "dynamic_clan_name_025032_between_literals"
    for record_id in TARGET_RECORD_IDS
}
SPEAKER_STYLE = {
    2725: "stern_pragmatic_house_head",
    2731: "patient_rustic_elder",
    2737: "restrained_self_reliant_retainer",
    2746: "assertive_long_view_strategist",
    2750: "reluctant_martial_realist",
    2751: "confident_senior_commander",
    2753: "wily_confident_diplomat",
    2756: "plainspoken_house_strategist",
    2758: "polite_formal_diplomatic_strategist",
}
TERMINOLOGY_SCOPE = {
    "house": ("우리 가문", "segment_required"),
    "protection": ("비호", "prefill_required"),
    "martial_prestige": ("무위", "segment_required"),
    "strategic_move": ("포석", "prefill_required"),
    "negotiation": ("교섭", "prefill_required"),
    "diplomacy": ("외교", "complete_record_required"),
    "verbal_skill": ("언변", "prefill_required"),
    "way_forward": ("활로", "complete_record_required"),
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

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "3FE2194976FF1B3A028573C27BD7F58B270D0D733187DD7A7F2E51E8443C8286"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "F3FEA7B417E527F8519D1BBDFCE75A3838C303C506A6E9BFFC5775887A617908"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "3D891114BE7BEA646C931D3D13785CFFC329CD691A1F676CE232C14B497479CF"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "FB747CC24E6730D368D4FB756A87B158982B7B65E28A57916DF96AF4300F1B85"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "716A0422FF714A85AB29D7C1A09A8A888AD3F64E2AC7FE0D020A38764B44EF91"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "11D07E8627868458E122CB82BB76C82D4928115CC5C14A129B5E0AB594F7AED4"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "4EEBC0445310E1E30F3E24442B8B78C89A31CF9B70129B9DD7630E5386920DCB"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "76546E3B1DD3AE81CBD26AA33C04821A60DC02B9C491C8D7B0FE041F8D65DAE7"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "23C89B2EAFD68AAB191CFA93F62585DE833F7238E1FCAF84AB8B03699F5E8698"
)
EXPECTED_BOUNDARY_SHA256 = (
    "8BB54BDA429DF8E4DA6C4785BA29271D6389D69569177F0853054CE437357C02"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "BC06A98BD701DBB2AC9C4AE1C2BCBC65FF3A12696F01BD50224A4B675953F7D3"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "0F8F8A674B6A9D800D319EB50DB23E1446EE11C1277A4BA97792BEAD2AD6BC69"
)
EXPECTED_VISIBILITY_SHA256 = (
    "D666E203D3315E0938E927ECA9331DDE216EF8E426C7A1B477EE67CDBF0C048B"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "961FC395972A640C56D9C09FEAC36552B3328BF98C6C78B7174C4B6DA2186385"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "565C49040EA811340CAD3A968667B2665135749B7AA450825972E25396248B5D"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "2F0137226836B48595816F1186E369A45F228BFF2861F34B084E234D3D50CC1B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "CDC83C7F725EBE97F13FF16D11177FFB22E00D06CE5646320F4CB6AE4E5FDC40"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "3B57204557372BFBC89E7A521AD183265579F854028952021CE238B4336B7A93"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "3F3DA54487986B44E19142E336816C83F7A4F480E5ECFDBEAAABD33383867C31"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3BEBC7A9984BA114D40F787D43CDB31C140042AF4E69D28EADC7B51F98AEF8D5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "26C7558838EB442BB20BD870243D4006037FEC985910CCE5D0260F5D4C289C8C"
)
EXPECTED_CHANGED_LITERAL_COUNT = 10

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "full-record donors pin nine strategic meanings, speaker registers "
    "and historical diplomacy terminology while Base runtime state and "
    "VM verification are not inherited; the complete B030 universe, "
    "assigned 66-visible slice, 56 exact-reuse prefill rows, eight "
    "prefilled same-record companions and the complete two-literal final "
    "record are guarded; clan-name token placement, protected trailing "
    "spaces, trailing newline and leading space, hidden-literal absence, "
    "full record assembly, line counts, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are reviewed; "
    "all ten residual literals remain PK runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1103_common",
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


def patch_common_globals() -> None:
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
        setattr(COMMON, name, value)
    COMMON.patch_common_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


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
                result[coordinate] = row
    return result


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    direct_calls = tuple(
        int.from_bytes(value[2:6], "little")
        for value in gap_bytes(record)
        if value.startswith(b"\x01\x43")
    )
    inline_tokens = tuple(
        value.hex().upper()
        for value in gap_bytes(record)
        if value.startswith(b"\x02")
    )
    return direct_calls, inline_tokens


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
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
    queue_universe = tuple(
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
        queue_universe,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    if (
        len(queue_rows) != 144
        or len(visible) != 200
        or visible[0] != "6:2615:0"
        or visible[-1] != "6:2758:1"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B030 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:2720:0"
        or queue_slice[-1] != "6:2758:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice boundary drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    expected_prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in TARGET_COORDINATES
    )
    if (
        len(prefilled) != 56
        or prefilled != expected_prefilled
        or any(
            coordinate not in prefilled
            for coordinate in PREFILL_COMPANION_COORDINATES
        )
        or any(
            coordinate in prefilled
            for coordinate in ("6:2758:0", "6:2758:1")
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_slice_context = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("scope_classification"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate].get(
                "current_ko_utf16le_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("translation_utf16le_sha256"),
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
            _,
            runtime,
            _,
            _,
            _,
            _,
            promotion,
        ) in prefill_slice_context
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill policy drifted"
        )
    guarded_digest(
        "prefill slice context",
        prefill_slice_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
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
    if residual != TARGET_COORDINATES or len(residual) != 10:
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
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records[(BLOCK_ID, record_id)]
                )
            ),
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
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
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
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    runtime_control = tuple(
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
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if any(
            runtime_controls(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
    )
    visibility = tuple(
        (
            record_id,
            len(
                literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )
            ),
            tuple(
                (
                    literal_id,
                    (
                        "pk_msggame",
                        BLOCK_ID,
                        record_id,
                        literal_id,
                    )
                    in prepared.visible_targets,
                )
                for literal_id in (0, 1)
            ),
        )
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
            runtime_control,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
        (
            "dynamic record",
            actual_dynamic,
            EXPECTED_DYNAMIC_RECORD_SHA256,
        ),
        (
            "visibility",
            visibility,
            EXPECTED_VISIBILITY_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
            for record_id, source, current in gaps
        )
        or any(
            controls
            != (
                EXPECTED_DIRECT_CALLS[record_id],
                EXPECTED_INLINE_TOKENS[record_id],
            )
            for _, record_id, controls in runtime_control
        )
        or any(
            arity != 2
            or literal_visibility
            != ((0, True), (1, True))
            for _, arity, literal_visibility in visibility
        )
        or HIDDEN_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime layout drifted"
        )


def assert_base_prefill_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame")
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }

    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    assembled_texts: dict[int, str] = {}
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        base_source_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current_records,
            (BLOCK_ID, base_record_id),
        )
        if record_id in COMPLETE_SEGMENT_RECORD_IDS:
            translated_literals = (
                TRANSLATIONS[f"6:{record_id}:0"],
                TRANSLATIONS[f"6:{record_id}:1"],
            )
            ownership = ("segment", "segment")
        else:
            translated_literals = (
                TRANSLATIONS[f"6:{record_id}:0"],
                str(
                    prefill_rows[f"6:{record_id}:1"][
                        "translation"
                    ]
                ),
            )
            ownership = ("segment", "prefill")
        expected_literals: list[str] = []
        for literal_id in (0, 1):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{base_record_id}:{literal_id}"
            )
            base_row = base_rows[base_coordinate]
            verification = base_row.get(
                "runtime_vm_verification",
                {},
            )
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                current_literals[literal_id],
            )
            expected_literals.append(adapted)
            base_evidence.append(
                (
                    coordinate,
                    base_coordinate,
                    source_literals[literal_id],
                    base_source_literals[literal_id],
                    current_literals[literal_id],
                    base_current_literals[literal_id],
                    base_row.get("translation"),
                    adapted,
                    translated_literals[literal_id],
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                    verification.get("method"),
                    verification.get("result"),
                    verification.get(
                        "row_verification_sha256"
                    ),
                )
            )
            if (
                source_literals[literal_id]
                != base_source_literals[literal_id]
                or translated_literals[literal_id] != adapted
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or verification.get("method")
                != "reversed_vm_static_analysis"
                or verification.get("result") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base donor drifted: "
                    f"{coordinate}"
                )
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        current_record = records_by_label["current"][
            (BLOCK_ID, record_id)
        ]
        base_source_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(source_record)
        )
        current_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(current_record)
        )
        base_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(base_source_record)
        )
        assembled = (
            translated_literals[0]
            + "<dynamic_clan_name_025032>"
            + translated_literals[1]
        )
        assembled_texts[record_id] = assembled
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                ownership,
                source_literals,
                current_literals,
                base_source_literals,
                tuple(expected_literals),
                translated_literals,
                source_gaps,
                current_gaps,
                base_gaps,
                runtime_controls(source_record),
                runtime_controls(current_record),
                runtime_controls(base_source_record),
                assembled,
            )
        )
        if (
            source_literals != base_source_literals
            or tuple(expected_literals) != translated_literals
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or current_gaps != source_gaps
            or base_gaps != source_gaps
            or runtime_controls(source_record)
            != (
                EXPECTED_DIRECT_CALLS[record_id],
                EXPECTED_INLINE_TOKENS[record_id],
            )
            or runtime_controls(current_record)
            != runtime_controls(source_record)
            or runtime_controls(base_source_record)
            != runtime_controls(source_record)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )

    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("scope_classification"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in PREFILL_COMPANION_COORDINATES
    )
    if (
        len(companion_evidence) != 8
        or any(
            semantic != "approved"
            or scope != "runtime_fragment_pending"
            or runtime != "pending"
            or promotion is not False
            for (
                _,
                _,
                semantic,
                scope,
                runtime,
                _,
                _,
                promotion,
            ) in companion_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} companion prefill drifted"
        )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )

    joined = "\n".join(assembled_texts.values())
    if any(
        term not in joined
        for term, _ in TERMINOLOGY_SCOPE.values()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology drifted"
        )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_SCOPE,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    guarded_digest(
        "runtime category",
        RUNTIME_CATEGORY,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
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
        or set(SPEAKER_STYLE) != set(TARGET_RECORD_IDS)
        or set(RUNTIME_CATEGORY) != set(TARGET_RECORD_IDS)
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
    current = records_by_label["current"]
    changed = 0
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            current,
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
        changed += translation != current_text
    if (
        EXPECTED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} changed policy drifted: {changed}"
        )
    if (
        TRANSLATIONS["6:2725:0"]
        != "우리 가문이 약한 탓이다, "
        or TRANSLATIONS["6:2731:0"] != "지금은,"
        or TRANSLATIONS["6:2737:0"] != "지금은,"
        or TRANSLATIONS["6:2746:0"]
        != "눈앞을 가로막는 것은, "
        or TRANSLATIONS["6:2750:0"]
        != "무위로 쓰러뜨리는 것이 최선이지만,\n"
        or TRANSLATIONS["6:2751:0"] != "적은,"
        or TRANSLATIONS["6:2753:0"] != "우리 가문을,"
        or TRANSLATIONS["6:2756:0"] != "우리 가문이,"
        or TRANSLATIONS["6:2758:0"] != "앞으로,"
        or TRANSLATIONS["6:2758:1"]
        != (
            " 와(과) 다툴 때를 대비해\n"
            "외교에서 활로를 찾고자 하옵니다"
        )
        or not TRANSLATIONS["6:2725:0"].endswith(" ")
        or not TRANSLATIONS["6:2746:0"].endswith(" ")
        or not TRANSLATIONS["6:2750:0"].endswith("\n")
        or not TRANSLATIONS["6:2758:1"].startswith(" ")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} speaker wording drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_record = base_source_records[
        (BLOCK_ID, BASE_RECORD_MAPPING[record_id])
    ]
    source_gaps = tuple(
        value.hex().upper() for value in gap_bytes(source_record)
    )
    current_gaps = tuple(
        value.hex().upper() for value in gap_bytes(current_record)
    )
    base_gaps = tuple(
        value.hex().upper() for value in gap_bytes(base_record)
    )
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    base_controls = runtime_controls(base_record)
    if (
        source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gaps != source_gaps
        or base_gaps != source_gaps
        or source_controls
        != (
            EXPECTED_DIRECT_CALLS[record_id],
            EXPECTED_INLINE_TOKENS[record_id],
        )
        or current_controls != source_controls
        or base_controls != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} controls drifted: {record_id}"
        )
    ownership = (
        ("segment_literal_0", "segment_literal_1")
        if record_id in COMPLETE_SEGMENT_RECORD_IDS
        else ("segment_literal_0", "prefill_literal_1")
    )
    return {
        "assembly_mode": RUNTIME_CATEGORY[record_id],
        "runtime_order": (
            ownership[0],
            "dynamic_clan_name_025032",
            ownership[1],
        ),
        "source_record_gap_sha256": canonical_sha256(
            source_gaps
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gaps
        ),
        "base_source_record_gap_sha256": canonical_sha256(
            base_gaps
        ),
        "source_runtime_gap_hex": source_gaps,
        "current_runtime_gap_hex": current_gaps,
        "base_source_runtime_gap_hex": base_gaps,
        "source_current_runtime_gap_equal": True,
        "base_source_opcode_gap_equal": True,
        "direct_call_operands": source_controls[0],
        "inline_runtime_tokens": source_controls[1],
        "complete_record_assembly_reviewed": True,
        "complete_record_owned_by_segment":
        record_id in COMPLETE_SEGMENT_RECORD_IDS,
        "all_record_literals_reviewed": True,
        "prefill_companion_reviewed":
        record_id not in COMPLETE_SEGMENT_RECORD_IDS,
        "hidden_companions_absent_and_guarded": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "dynamic_clan_direction_reviewed": True,
        "dynamic_numeric_token_present": False,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "outer_whitespace_preserved": True,
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
    patch_common_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_prefill_and_assembly(prepared, records_by_label)
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
        companion_id = 1 - literal_id
        companion_coordinate = (
            f"6:{record_id}:{companion_id}"
        )
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
                "historical_term_review": True,
                "terminology_scope_review": TERMINOLOGY_SCOPE,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "record_variant":
                "subordination_or_diplomatic_strategy",
                "speaker_register_variant":
                SPEAKER_STYLE[record_id],
                "runtime_category":
                RUNTIME_CATEGORY[record_id],
                "companion_coordinates": (
                    companion_coordinate,
                ),
                "companion_source": (
                    "segment"
                    if record_id in COMPLETE_SEGMENT_RECORD_IDS
                    else "prefill"
                ),
                "hidden_companion_coordinates": (),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_kind":
                "exact_source_exact_opcode_semantic_only",
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
                    prepared,
                    records_by_label,
                    record_id,
                ),
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
    patch_common_globals()
    COMMON.assert_tamper_rejection(
        prepared,
        rows,
        candidate,
    )


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
        or optional_present != second[5]
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
        len(rows) != 10
        or len(validated) != 10
        or counts != Counter({"runtime_fragment_pending": 10})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
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
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B030_S1103",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 144,
                "queue_visible_count": 200,
                "slice_visible_count": 66,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 56,
                "residual_count": 10,
                "base_semantic_reference_count": 10,
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "clan_token_record_count":
                len(TARGET_RECORD_IDS),
                "complete_segment_record_count":
                len(COMPLETE_SEGMENT_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_companion_count": 0,
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "runtime_category_sha256":
                EXPECTED_RUNTIME_CATEGORY_SHA256,
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
                "prefill_companions_guarded": True,
                "complete_two_literal_record_guarded": True,
                "hidden_companions_absent_and_guarded": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "complete_record_assembly_guarded": True,
                "inline_clan_tokens_guarded": True,
                "direct_call_operands": [],
                "source_current_opcode_gap_divergence_records": [],
                "base_source_opcode_gap_divergence_records": [],
                "speaker_registers_reviewed": True,
                "terminology_scope_review": TERMINOLOGY_SCOPE,
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
