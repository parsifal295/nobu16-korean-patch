#!/usr/bin/env python3
"""Build source-redacted PK B110 segment 1335 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_COMMON_BUILD_ROWS = COMMON.build_rows

CROSS_COORDINATE = "14:245:0"
CROSS_TRANSLATION = "◇전초전"
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B110_S1334"

TARGET_COORDINATES = (
    "14:245:1",
    "14:245:2",
    "14:245:3",
    "14:245:4",
    "14:245:5",
    "14:245:6",
    "14:245:7",
    "15:220:0",
    "15:221:0",
    "15:223:2",
    "15:223:3",
    "15:233:1",
    "15:237:1",
    "15:241:1",
    "15:245:1",
    "15:247:0",
    "15:249:1",
    "15:249:2",
)
TRANSLATIONS = {
    "14:245:1": (
        "\n서로 지정한 성에서 공성전이 발생하며, 공성전과 수성전 순서로 전투가 진행됩니다.\n"
        "결전을 승인할 때 서로 공격할 성을 지정하므로,\n"
        "준비 기간에 방어 설비를 건설하는 등 대비합시다.\n"
        "전초전에서 승리하면 결전에서 유리해집니다.\n"
        "\n"
    ),
    "14:245:2": "◇규칙",
    "14:245:3": (
        "\n　·양측은 상대 세력과 인접한 성 가운데 전초전을 치를 성을 선택\n"
        " ·양측 세력을 잇는 길의 수에 따라 출진 가능한 부대 수 결정\n"
        " ·양측이 선택한 성은 방위 거점이 된다\n"
        " ·공성측 참전 부대는 시작 직전에 선택하고, 수성측은 성 소속 무장이 방어\n"
        " ·공성전은 일반 공성전과 같은 규칙\n"
        " ·공성측이 승리하면 잔여 병력이 많은 상위 4개 부대가 결전에 참가\n"
        " ·수성측이 승리하면 상대 부대의 결전 참가를 저지\n"
        "\n"
    ),
    "14:245:4": "◇결전",
    "14:245:5": (
        "\n대규모 전장에서 치르는 최종전입니다.\n"
        "승리하면 상대의 영지를 모두 제압할 수 있어,\n"
        "천하 통일의 큰 발판이 될 것입니다.\n"
        "\n"
    ),
    "14:245:6": "◇규칙",
    "14:245:7": (
        "\n　·미리 선택한 양측 12개 부대로 합전을 치른다\n"
        " ·합전은 일반 합전과 같은 규칙\n"
        " ·전초전 공성측에서 승리했다면 잔여 병력 상위 4개 부대가 추가로 참가\n"
        " ·전초전 수성측에서 패배했다면 적 세력의 부대가 최대 4개 늘어난다"
    ),
    "15:220:0": "좋은 방안",
    "15:221:0": "좋은 방안",
    "15:223:2": "\n신중히 판단하",
    "15:223:3": "십시오.",
    "15:233:1": "…",
    "15:237:1": "…",
    "15:241:1": "…",
    "15:245:1": "…",
    "15:247:0": "좋은 방안",
    "15:249:1": "\n신중히",
    "15:249:2": " 판단하십시오.",
}

# The legacy row builder is keyed by record number.  Block 14 record 245 is
# reviewed separately below; this tuple describes the block 15 records.
TARGET_RECORD_IDS = (
    220,
    221,
    223,
    233,
    237,
    241,
    245,
    247,
    249,
)
EXPECTED_ARITY = {
    220: 2,
    221: 2,
    223: 4,
    233: 2,
    237: 2,
    241: 2,
    245: 2,
    247: 2,
    249: 3,
}
TARGET_RECORD_KEYS = (
    (14, 245),
    (15, 220),
    (15, 221),
    (15, 223),
    (15, 233),
    (15, 237),
    (15, 241),
    (15, 245),
    (15, 247),
    (15, 249),
)
EXPECTED_ARITY_BY_KEY = {
    (14, 245): 8,
    **{
        (15, record_id): arity
        for record_id, arity in EXPECTED_ARITY.items()
    },
}
PREFILL_COMPANION_COORDINATES = (
    CROSS_COORDINATE,
    "15:220:1",
    "15:221:1",
    "15:223:0",
    "15:223:1",
    "15:233:0",
    "15:237:0",
    "15:241:0",
    "15:245:0",
    "15:247:1",
    "15:249:0",
)
PREFILL_COMPANION_DONOR = {
    CROSS_COORDINATE: CROSS_DONOR_LABEL,
    "15:220:1": "15:217:1",
    "15:221:1": "15:218:1",
    "15:223:0": "15:220:0",
    "15:223:1": "15:220:1",
    "15:233:0": "15:230:0",
    "15:237:0": "15:230:0",
    "15:241:0": "15:230:0",
    "15:245:0": "15:230:0",
    "15:247:1": "15:217:1",
    "15:249:0": "15:246:0",
}

# Record-number globals are used by the inherited row formatter.  The block
# 14 record with the same number is corrected to its own evidence afterwards.
EXACT_BASE_DONOR = {
    220: (15, 217),
    221: (15, 218),
    223: (15, 220),
    233: (15, 230),
    237: (15, 230),
    241: (15, 230),
    245: (15, 230),
    247: (15, 217),
    249: (15, 246),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, donor in EXACT_BASE_DONOR.items()
}
SEMANTIC_BASE_CONTEXT_BY_KEY = {
    (14, 245): (
        "14:55:0",
        "14:55:1",
        "14:59:0",
        "14:59:1",
        "14:64:0",
        "14:64:1",
    ),
    **{
        (15, record_id): SEMANTIC_BASE_CONTEXT[record_id]
        for record_id in TARGET_RECORD_IDS
    },
}
EXACT_BASE_DONOR_BY_KEY = {
    (15, record_id): donor
    for record_id, donor in EXACT_BASE_DONOR.items()
}
EXPECTED_BASE_RAW_MATCHES_BY_KEY = {
    (14, 245): (),
    (15, 220): (),
    (15, 221): (),
    (15, 223): (),
    (15, 233): ((15, 230), (15, 234), (15, 238), (15, 242)),
    (15, 237): ((15, 230), (15, 234), (15, 238), (15, 242)),
    (15, 241): ((15, 230), (15, 234), (15, 238), (15, 242)),
    (15, 245): ((15, 230), (15, 234), (15, 238), (15, 242)),
    (15, 247): (),
    (15, 249): (),
}
EXPECTED_BASE_LITERAL_MATCHES_BY_KEY = {
    (14, 245): (),
    (15, 220): ((15, 217), (15, 244)),
    (15, 221): ((15, 218),),
    (15, 223): ((15, 220),),
    (15, 233): ((15, 230), (15, 234), (15, 238), (15, 242)),
    (15, 237): ((15, 230), (15, 234), (15, 238), (15, 242)),
    (15, 241): ((15, 230), (15, 234), (15, 238), (15, 242)),
    (15, 245): ((15, 230), (15, 234), (15, 238), (15, 242)),
    (15, 247): ((15, 217), (15, 244)),
    (15, 249): ((15, 246),),
}
EXPECTED_BASE_MASKED_MATCHES_BY_KEY = (
    EXPECTED_BASE_LITERAL_MATCHES_BY_KEY
)
EXPECTED_BASE_RAW_MATCHES = {
    record_id: EXPECTED_BASE_RAW_MATCHES_BY_KEY[(15, record_id)]
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: EXPECTED_BASE_LITERAL_MATCHES_BY_KEY[(15, record_id)]
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES

EXPECTED_SOURCE_CONTROLS_BY_KEY = {
    (14, 245): ((), ()),
    (15, 220): ((550, 724, 610), ()),
    (15, 221): ((550, 724, 286), ()),
    (15, 223): ((1168, 1126, 1174, 412), ()),
    (15, 233): ((286,), ()),
    (15, 237): ((286,), ()),
    (15, 241): ((286,), ()),
    (15, 245): ((286,), ()),
    (15, 247): ((550, 724, 286), ()),
    (15, 249): ((286, 1174, 412), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_KEY = {
    **EXPECTED_SOURCE_CONTROLS_BY_KEY,
    (15, 223): ((), ()),
    (15, 249): ((), ()),
}
SOURCE_CURRENT_GAP_MISMATCH_KEYS = {
    (15, 223),
    (15, 249),
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: EXPECTED_SOURCE_CONTROLS_BY_KEY[(15, record_id)]
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1335,
    queue_start=67,
    queue_stop=134,
    slice_first="14:245:1",
    slice_last="15:255:3",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        286,
        412,
        550,
        610,
        724,
        1126,
        1168,
        1174,
    ),
    boundary_record_keys=(
        *((14, record_id) for record_id in range(240, 247)),
        *((15, record_id) for record_id in range(210, 261)),
    ),
    speaker_style=tuple(
        (record_id, "dynamic_advice_fragment")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("opening assault", "전초전"),
        ("decisive battle", "결전"),
        ("siege", "공성전"),
        ("castle defense", "수성전"),
        ("defensive equipment", "방어 설비"),
        ("defense base", "방위 거점"),
        ("field battle", "합전"),
        ("remaining soldiers", "잔여 병력"),
        ("unification", "천하 통일"),
        ("good plan", "좋은 방안"),
        ("low expected result", "그리 많은 성과는 바랄 수 없다"),
        ("even odds", "성공할 가능성은 반반입니다"),
        ("formal judgment", "신중히 판단하십시오"),
        ("project ellipsis", "…"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record entry was reviewed as auxiliary evidence; the seven PK-"
        "only opening-assault and decisive-battle help literals use completed "
        "Base siege and field-battle help only as semantic and terminology "
        "context, while all eleven block-fifteen residual fragments complete "
        "approved Base Korean donor assemblies; Base runtime and VM state are "
        "never inherited, including the two records whose PK source calls are "
        "absent from the current Korean runtime gaps; the block-fourteen and "
        "block-fifteen records that share record number 245 are keyed and "
        "guarded independently, and the opening-assault heading is assembled "
        "with the manually reviewed S1334 neighbor; opening assault, decisive "
        "battle, siege, castle defense, defensive equipment, defense base, "
        "field battle, remaining soldiers, unification, good-plan, even-odds "
        "and formal-judgment terms remain distinct; calls, tokens, leading and "
        "trailing newlines, bullets, headings, terminators, complete record "
        "arity, all forty-nine slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=5,
    pins={
        "expected_queue_universe_sha256": (
            "019BEF63ACFB2389CA11DE430278DAC12EFCD5B9CC170C4F7F37AFAF674881A8"
        ),
        "expected_queue_slice_sha256": (
            "0C68DE3376E5CA9A09BFFF3E52E270212FF8D45F21A4764C101DA0A4BBAEEEA0"
        ),
        "expected_prefilled_coordinate_sha256": (
            "3F89BD1863ECD914893D9F38FD543082C716314C6AE788F8B37BE35FD9D69FA6"
        ),
        "expected_prefill_slice_context_sha256": (
            "18A56BF913B10EB7F0031AB6630A36632A5F173204743AA853EA87B436E45843"
        ),
        "expected_target_coordinate_sha256": (
            "90DBE11913D2843D429C545E56125925D6DDC019B14E9F045DE42C739BCA3E30"
        ),
        "expected_source_target_sha256": (
            "D5E1C213703DD525F895CCC6CA10E7E145AA8DAFE1862A0BB685120E12AE9AC5"
        ),
        "expected_current_target_sha256": (
            "085F01495769FF34E94A6B80D0D4B372FEBFCC6C51AA2BE03395CB4AF9B30040"
        ),
        "expected_context_corpus_sha256": (
            "D4F48D10F0ABCEBEA9A7ABB1F1960D6BB231BC5928C35D377778E306A7C4733A"
        ),
        "expected_gap_contract_sha256": (
            "BA67D3962A22398FBA1D7D498635C806236B4F5A0B16195A31A70429FC4E7B44"
        ),
        "expected_boundary_sha256": (
            "70E0A56EF00396EF48FD255CA4AA6B30D1D6758793DCC7F885FCBF410E43B775"
        ),
        "expected_runtime_control_sha256": (
            "49987F14D5780D512C69F3C86F98C8EA18F54E0483B45C0A348058BB3864805E"
        ),
        "expected_base_search_sha256": (
            "DC551C8F683DB41D01B6891A8BFB1B84D063B4A4BD82C0EE82ED934CFCDC7CF7"
        ),
        "expected_complete_assembly_sha256": (
            "8FBDFA5381428BCBB14A4E4F593CB38751731D88C79C5B2A7B2A774C305B020A"
        ),
        "expected_call_graph_sha256": (
            "28F4D59C3C7A0DF2B87322C0AA6E99137C4755F1A5DAAF0B519A5640BDFF4032"
        ),
        "expected_speaker_style_sha256": (
            "3105D445AB13393A7CB0C858E788A2CE5CE4A00924B310C2BC30B83CFCF40E65"
        ),
        "expected_terminology_policy_sha256": (
            "6293AB3607A25A060280C1D0A8CF1F3A9054457368A9C1E3FDB24AD889DD036B"
        ),
        "expected_translation_policy_sha256": (
            "13D80D73D752C2D1735E16E56166909345C23D047BF7F6DF2EAAAA86D4ACDEF2"
        ),
        "expected_candidate_sha256": (
            "EC8C0439BE465BC9750493DCA88F2C497E85F80E1788600A295B980946D998CE"
        ),
        "expected_combined_slice_candidate_sha256": (
            "571F663AD8D327C6CF9424C8820FA390A886DED9105509A0C18DD56915A1C040"
        ),
        "expected_combined_changed_literal_count": 37,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B110_S1335",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1335.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1334.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1336.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B110",
    "queue_row_count": 79,
    "queue_visible_count": 200,
    "queue_first": "14:231:0",
    "queue_last": "15:281:0",
})


def _records_by_label(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    resource = prepared.resources["pk_msggame"]
    return {
        "jp": COMMON.ENGINE.archive_records(resource.pristine_archive),
        "current": COMMON.ENGINE.archive_records(resource.current_archive),
        **{
            label.lower(): COMMON.ENGINE.archive_records(archive)
            for label, archive in resource.context_archives.items()
        },
    }


def context_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    """Pin both sides of the block boundary and distinct runtime gaps."""
    _, _, _, _, record_keys = COMMON.queue_evidence(prepared)
    source_target = tuple(
        (
            coordinate,
            COMMON.literal_texts(
                records_by_label["jp"],
                COMMON.coordinate_key(coordinate)[:2],
            )[COMMON.coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            COMMON.literal_texts(
                records_by_label["current"],
                COMMON.coordinate_key(coordinate)[:2],
            )[COMMON.coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            key,
            COMMON.sha256_bytes(records[key].data),
            COMMON.literal_texts(records, key),
        )
        for label, records in records_by_label.items()
        for key in record_keys
    )
    gaps = tuple(
        (
            key,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(records_by_label["jp"][key])
            ),
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(
                    records_by_label["current"][key]
                )
            ),
        )
        for key in TARGET_RECORD_KEYS
    )
    boundary = tuple(
        (
            label,
            key,
            COMMON.sha256_bytes(records_by_label[label][key].data),
            COMMON.literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(
                    records_by_label[label][key]
                )
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for key in CONFIG["boundary_record_keys"]
    )
    controls = tuple(
        (
            label,
            key,
            COMMON.CORE.runtime_controls(records_by_label[label][key]),
        )
        for label in ("jp", "current")
        for key in TARGET_RECORD_KEYS
    )
    return {
        "source_target": source_target,
        "current_target": current_target,
        "corpus": corpus,
        "gaps": gaps,
        "boundary": boundary,
        "controls": controls,
    }


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = context_evidence(prepared, records_by_label)
    for label, value, expected in (
        (
            "source target",
            values["source_target"],
            COMMON.CORE.EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "current target",
            values["current_target"],
            COMMON.CORE.EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "multilingual context",
            values["corpus"],
            COMMON.CORE.EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "gap contract",
            values["gaps"],
            COMMON.CORE.EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "boundary",
            values["boundary"],
            COMMON.CORE.EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "runtime control",
            values["controls"],
            COMMON.CORE.EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        COMMON.CORE.guarded_digest(label, value, expected)
    expected_controls = tuple(
        (
            label,
            key,
            (
                EXPECTED_SOURCE_CONTROLS_BY_KEY[key]
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_KEY[key]
            ),
        )
        for label in ("jp", "current")
        for key in TARGET_RECORD_KEYS
    )
    mismatches = {
        key for key, source, current in values["gaps"]
        if source != current
    }
    if (
        values["controls"] != expected_controls
        or mismatches != SOURCE_CURRENT_GAP_MISMATCH_KEYS
        or any(
            ("pk_msggame", *COMMON.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError("segment 1335 runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard exact Base assemblies and the S1334 split-record heading."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1335 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1334.private.v1.jsonl"
    )
    if neighbor_path.is_file():
        neighbor_rows = {
            str(row["coordinate"]): row
            for row in COMMON.read_jsonl(neighbor_path)
        }
        neighbor = neighbor_rows.get(CROSS_COORDINATE)
        if (
            neighbor is None
            or neighbor.get("semantic_review") != "approved"
            or str(neighbor.get("translation")) != CROSS_TRANSLATION
        ):
            raise RuntimeError(
                "segment 1335 reciprocal S1334 heading drifted"
            )
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
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for key in TARGET_RECORD_KEYS:
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(
            records_by_label["jp"], key
        )
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
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
            )
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
            len(source_literals) != EXPECTED_ARITY_BY_KEY[key]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES_BY_KEY[key]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES_BY_KEY[key]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES_BY_KEY[key]
        ):
            raise RuntimeError(
                f"segment 1335 Base search drifted: {key}"
            )
        exact = key in EXACT_BASE_DONOR_BY_KEY
        references: list[tuple[Any, ...]] = []
        donor_coordinates = (
            tuple(
                f"{EXACT_BASE_DONOR_BY_KEY[key][0]}:"
                f"{EXACT_BASE_DONOR_BY_KEY[key][1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY_BY_KEY[key])
            )
            if exact
            else SEMANTIC_BASE_CONTEXT_BY_KEY[key]
        )
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1335 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "complete_exact_assembly" if exact else "semantic_only",
                "runtime_vm_not_inherited",
            ))
        donor_translations = (
            tuple(
                str(base_rows[coordinate]["translation"])
                for coordinate in donor_coordinates
            )
            if exact
            else None
        )
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY_BY_KEY[key]):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append(
                    "segment_manual_exact_base_semantic_reuse"
                    if exact
                    else "segment_manual_multilingual"
                )
                seen_target.add(coordinate)
            elif coordinate == CROSS_COORDINATE:
                assembled.append(CROSS_TRANSLATION)
                owners.append("neighbor_segment_manual_runtime_pending")
                seen_companion.add(coordinate)
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
                        f"segment 1335 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1335 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1335 exact assembly drifted: {key}"
            )
        base_evidence.append((
            key,
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
            key,
            tuple(owners),
            tuple(assembled),
            donor_translations,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if seen_target != target_set or seen_companion != companion_set:
        raise RuntimeError("segment 1335 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def runtime_evidence_for_key(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    key: tuple[int, int],
) -> dict[str, Any]:
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_controls = COMMON.CORE.runtime_controls(source)
    current_controls = COMMON.CORE.runtime_controls(current)
    exact = key in EXACT_BASE_DONOR_BY_KEY
    references = (
        tuple(
            f"{EXACT_BASE_DONOR_BY_KEY[key][0]}:"
            f"{EXACT_BASE_DONOR_BY_KEY[key][1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY_BY_KEY[key])
        )
        if exact
        else SEMANTIC_BASE_CONTEXT_BY_KEY[key]
    )
    return {
        "runtime_category": (
            "concise_system_help"
            if key == (14, 245)
            else "dynamic_advice_fragment"
        ),
        "source_record_gap_sha256": COMMON.CORE.canonical_sha256(
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(source)
            )
        ),
        "current_record_gap_sha256": COMMON.CORE.canonical_sha256(
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(current)
            )
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        COMMON.gap_bytes(source) == COMMON.gap_bytes(current),
        "base_complete_record_match_kind": (
            (
                "raw_literal_and_operand_exact"
                if EXPECTED_BASE_RAW_MATCHES_BY_KEY[key]
                else "literal_and_operand_exact"
            )
            if exact
            else "none_semantic_context_only"
        ),
        "base_context_reference_coordinates": references,
        "base_complete_record_match_coordinates": tuple(
            f"{match[0]}:{match[1]}"
            for match in EXPECTED_BASE_LITERAL_MATCHES_BY_KEY[key]
        ),
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed": any(
            coordinate.startswith(f"{key[0]}:{key[1]}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_donor_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    """The inherited row loop covers the block 15 records."""
    return runtime_evidence_for_key(
        records_by_label,
        (15, record_id),
    )


def unchecked_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    current = records_by_label["current"]
    replacements = {
        COMMON.coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: COMMON.literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = COMMON.ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = COMMON.ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if candidate != reverse_order:
        raise RuntimeError(
            "segment 1335 reverse-order overlay drifted"
        )
    candidate_records = COMMON.ENGINE.archive_records(
        COMMON.ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(current) != 21_751
        or len(candidate_records) != 21_751
        or set(replacements) != {
            COMMON.coordinate_key(coordinate)
            for coordinate in TARGET_COORDINATES
        }
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            COMMON.gap_bytes(candidate_records[key])
            != COMMON.gap_bytes(current[key])
            for key in touched_records
        )
        or COMMON.ENGINE.rebuild_packed_with_literals(
            candidate, reverse
        )
        != current_blob
    ):
        raise RuntimeError("segment 1335 candidate scope drifted")
    changed = sum(
        translation
        != COMMON.literal_texts(
            current,
            COMMON.coordinate_key(coordinate)[:2],
        )[COMMON.coordinate_key(coordinate)[2]]
        for coordinate, translation in TRANSLATIONS.items()
    )
    return candidate, COMMON.sha256_bytes(candidate), changed


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        base_and_assembly_evidence,
    )
    COMMON.CORE.context_evidence = context_evidence
    COMMON.CORE.assert_context_contracts = assert_context_contracts
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.runtime_evidence = runtime_evidence
    COMMON.CORE.PARENT.unchecked_candidate = unchecked_candidate


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.context_evidence = context_evidence
    COMMON.CORE.assert_context_contracts = assert_context_contracts
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.runtime_evidence = runtime_evidence
    COMMON.CORE.PARENT.unchecked_candidate = unchecked_candidate


def build_rows() -> tuple[Any, ...]:
    """Correct inherited record-number evidence for block 14 record 245."""
    result = list(_ORIGINAL_COMMON_BUILD_ROWS())
    prepared = result[0]
    rows = result[1]
    records_by_label = _records_by_label(prepared)
    references = SEMANTIC_BASE_CONTEXT_BY_KEY[(14, 245)]
    for row in rows:
        if not str(row["coordinate"]).startswith("14:245:"):
            continue
        row["base_context_reference_coordinate"] = references[0]
        row["base_context_reference_coordinates"] = references
        row["manual_complete_base_donor_translation_selected"] = False
        row["manual_multilingual_translation_selected"] = True
        row["speaker_style"] = "concise_system_help"
        row["runtime_assembly_evidence"] = runtime_evidence_for_key(
            records_by_label,
            (14, 245),
        )
    return tuple(result)


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals
COMMON.build_rows = build_rows


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
