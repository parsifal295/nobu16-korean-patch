#!/usr/bin/env python3
"""Build source-redacted PK B110 segment 1336 residual decisions."""

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
    "15:255:4",
    "15:259:1",
    "15:261:1",
    "15:262:1",
    "15:264:1",
    "15:265:0",
    "15:267:0",
    "15:267:1",
    "15:270:0",
    "15:272:1",
    "15:275:0",
    "15:276:0",
    "15:277:0",
    "15:278:0",
    "15:279:0",
)
TRANSLATIONS = {
    "15:255:4": "고려",
    "15:259:1": (
        "\n"
        "성을 지키는 병사를 회유해 급소를 장악한다면"
    ),
    "15:261:1": (
        "\n"
        "친족까지 함께 권유한다면"
    ),
    "15:262:1": "면\n",
    "15:264:1": "면\n",
    "15:265:0": "끼어들어 송구하옵니다",
    "15:267:0": "한 말씀",
    "15:267:1": "\n이럴 때는",
    "15:270:0": "잠시",
    "15:272:1": "인 듯합니다",
    "15:275:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:276:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:277:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:278:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:279:0": "더 성공하기 쉬운 계책이라 할 수 있습니다",
}
TARGET_RECORD_IDS = (
    255, 259, 261, 262, 264, 265, 267,
    270, 272, 275, 276, 277, 278, 279,
)
EXPECTED_ARITY = {
    255: 5,
    259: 3,
    261: 3,
    262: 3,
    264: 4,
    265: 2,
    267: 4,
    270: 4,
    272: 2,
    275: 3,
    276: 3,
    277: 3,
    278: 3,
    279: 2,
}
SELECTED_BASE_DONOR = {
    255: (15, 252),
    259: (15, 256),
    261: (15, 258),
    262: (15, 259),
    264: (15, 261),
    265: (15, 262),
    267: (15, 264),
    270: (15, 267),
    272: (15, 269),
    275: (15, 272),
    276: (15, 272),
    277: (15, 274),
    278: (15, 274),
    279: (15, 276),
}
EXACT_BASE_DONOR = {
    record_id: donor
    for record_id, donor in SELECTED_BASE_DONOR.items()
    if record_id != 255
}
PREFILL_COMPANION_DONOR = {
    "15:255:0": "15:252:0",
    "15:255:1": "15:252:1",
    "15:255:3": "15:252:3",
    "15:259:0": "15:256:0",
    "15:259:2": "15:256:2",
    "15:261:0": "15:258:0",
    "15:261:2": "15:258:2",
    "15:262:0": "15:259:0",
    "15:262:2": "15:259:2",
    "15:264:0": "15:261:0",
    "15:264:2": "15:261:2",
    "15:264:3": "15:261:3",
    "15:265:1": "15:262:1",
    "15:267:2": "15:264:2",
    "15:267:3": "15:264:3",
    "15:270:1": "15:267:1",
    "15:270:2": "15:267:2",
    "15:270:3": "15:267:3",
    "15:272:0": "15:269:0",
    "15:275:1": "15:272:1",
    "15:275:2": "15:272:2",
    "15:276:1": "15:272:1",
    "15:276:2": "15:272:2",
    "15:277:1": "15:274:1",
    "15:277:2": "15:272:2",
    "15:278:1": "15:274:1",
    "15:278:2": "15:272:2",
    "15:279:1": "15:276:1",
}
PREFILL_COMPANION_COORDINATES = tuple(PREFILL_COMPANION_DONOR)
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:255:2",)
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
        if not (
            record_id == 255 and literal_id == 2
        )
    )
    for record_id, donor in SELECTED_BASE_DONOR.items()
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    255: ((15, 252),),
    259: ((15, 256),),
    261: ((15, 258),),
    262: ((15, 259),),
    264: ((15, 261),),
    265: ((15, 262),),
    267: ((15, 264),),
    270: ((15, 267),),
    272: ((15, 269),),
    275: ((15, 272), (15, 273), (15, 280)),
    276: ((15, 272), (15, 273), (15, 280)),
    277: ((15, 274), (15, 275)),
    278: ((15, 274), (15, 275)),
    279: ((15, 276),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_SOURCE_CONTROLS = {
    255: ((1186, 1066, 1, 1174, 412), ()),
    259: ((1180, 1066, 286), ()),
    261: ((550, 700, 292, 1114), ()),
    262: ((1180, 1, 388, 1066), ()),
    264: ((1186, 1, 1036, 1126), ()),
    265: ((1192, 142), ()),
    267: ((1048, 292, 1, 322, 1126), ()),
    270: ((910, 1084, 1, 82), ()),
    272: ((616,), ()),
    275: ((1066, 940, 1096), ()),
    276: ((1066, 940, 1096), ()),
    277: ((1066, 1090, 1096), ()),
    278: ((1066, 1090, 1096), ()),
    279: ((1066, 1096), ()),
}
EXPECTED_CURRENT_CONTROLS = {
    **EXPECTED_SOURCE_CONTROLS,
    259: ((), ()),
    261: ((), ()),
    264: ((), ()),
    265: ((), ()),
    279: ((), ()),
}
EXPECTED_CONTROLS_BY_RECORD = EXPECTED_SOURCE_CONTROLS
SOURCE_CURRENT_GAP_MISMATCH_RECORDS = {
    259, 261, 264, 265, 279,
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1336,
    queue_start=134,
    queue_stop=200,
    slice_first="15:255:4",
    slice_last="15:281:0",
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
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        1, 82, 142, 286, 292, 322, 388, 412, 550, 616,
        700, 910, 940, 1036, 1048, 1066, 1084, 1090, 1096,
        1114, 1126, 1174, 1180, 1186, 1192,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(250, 283)
    ),
    speaker_style=tuple(
        (record_id, "dynamic_covert_advice_fragment")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("destroy", "파괴"),
        ("ninja", "시노비"),
        ("raze", "방화"),
        ("castle guards", "성을 지키는 병사"),
        ("weak point", "급소"),
        ("extract", "빼내기"),
        ("relatives", "친족"),
        ("incite", "선동"),
        ("revolt", "잇키"),
        ("official decree", "교서"),
        ("wit", "재지"),
        ("ingenious plan", "묘안"),
        ("noble birth", "고귀한 혈통"),
        ("chance of success", "승산"),
        ("solid progress", "착실히 진행"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record array was reviewed as auxiliary context; thirteen "
        "residual dynamic fragments and twenty-eight same-record prefill "
        "companions reproduce completed, runtime-verified Base Korean "
        "wording selected by literal and operand-masked source identity, "
        "while two fragments are adapted to the localized PK gaps that "
        "removed source calls; Base runtime and VM state are never inherited; "
        "the split "
        "record 255 assembly includes three exact prefills from the preceding "
        "slice and one source-identical hidden newline; source and current PK "
        "call operands are recorded separately for the five records whose "
        "localized Korean runtime removed source calls; destroy, ninja, "
        "raze, castle guards, weak point, extract, relatives, incite, revolt, "
        "official decree, wit, ingenious plan, noble birth, chance of "
        "success and solid-progress terms follow the completed corpus; "
        "dynamic suffix boundaries, calls, gaps, newlines, outer whitespace "
        "exceptions authorized by the verified donor assemblies, "
        "terminators, complete record arity, all fifty-one slice prefills, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbors and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=13,
    pins={
        "expected_queue_universe_sha256":
        "019BEF63ACFB2389CA11DE430278DAC12EFCD5B9CC170C4F7F37AFAF674881A8",
        "expected_queue_slice_sha256":
        "C08FACD20AB2D62DDB3FF0963C7C52DDBC037F81DD9A597E9246FA9C8EB5B816",
        "expected_prefilled_coordinate_sha256":
        "9D8D1D1E7AD1EACA274AC21AB7B76C11C36254B5BB545CB90206AEA673EFA025",
        "expected_prefill_slice_context_sha256":
        "E121666C442BBD213D4AF8F828A86878419867C3A0DA0D24A3B588AF1900D283",
        "expected_target_coordinate_sha256":
        "7AF35FB2B5CCFEB679D6C74F07783B10728B5F25EC7D59F97431D6D1D6BB9A65",
        "expected_source_target_sha256":
        "254D4DE277807C6D27A3A0A407DD2425A1493457DFD33067899B0C4CEF06095C",
        "expected_current_target_sha256":
        "ACF9040E0405B69C272DB678171508D3E4414DFFA40BB579BAC33DA01D5B0F22",
        "expected_context_corpus_sha256":
        "D4F48D10F0ABCEBEA9A7ABB1F1960D6BB231BC5928C35D377778E306A7C4733A",
        "expected_gap_contract_sha256":
        "6C65B5E3BE0E7C8B9026712B4DE56E3A65708026015C3D4E3B800A7CD98321BB",
        "expected_boundary_sha256":
        "1DF4365B14335623F6B6A59904B5FE2E3D5A8BADA6EF9392819BA7080328A737",
        "expected_runtime_control_sha256":
        "4258FFF7A94E58DCB7A0CAD04A0529A692DF0275A0A5D2CFDD81153865859483",
        "expected_base_search_sha256":
        "6BA249EDCC929F1345DE0810ACB28BBF0E891F4683187F4F23A12CE3E4142AC9",
        "expected_complete_assembly_sha256":
        "F9DF6136323E3B37A085118201723290F1F0FEB6AC0291F86A25B9DE81ED3F96",
        "expected_call_graph_sha256":
        "33507D391D347DBE3960F7A4E8BAAD994F8DA2828085A80B167CDCE16F28FF6D",
        "expected_speaker_style_sha256":
        "6097322664523E53E32BEE450073510CE8419F4D06527C05583EB157B7142C5A",
        "expected_terminology_policy_sha256":
        "20EE2ABC9F8518C224D374FB652BE1284B570D785073C3FA00DE7AF64E9F7338",
        "expected_translation_policy_sha256":
        "2CB3B5F8A7295B6856C02CB9A78CD71D83610EEB8F28F77561E70FF682852215",
        "expected_candidate_sha256":
        "C87AF52A6E0BAAAE049E31FDE46B16AF664965B242FE1475727B3BDE14B97277",
        "expected_combined_slice_candidate_sha256":
        "4CC08C9DD9474B89F8F1AB29966094EE594958B5B4029B42005F213E6AA22962",
        "expected_combined_changed_literal_count": 58,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B110_S1336",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1336.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1334.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1335.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B110",
    "queue_row_count": 79,
    "queue_visible_count": 200,
    "queue_first": "14:231:0",
    "queue_last": "15:281:0",
})


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    """Pin distinct source and localized-current runtime layouts."""
    values = COMMON.CORE.context_evidence(prepared, records_by_label)
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
            record_id,
            (
                EXPECTED_SOURCE_CONTROLS[record_id]
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS[record_id]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    mismatches = {
        record_id
        for record_id, source, current in values["gaps"]
        if source != current
    }
    if (
        values["controls"] != expected_controls
        or mismatches != SOURCE_CURRENT_GAP_MISMATCH_RECORDS
        or any(
            ("pk_msggame", *COMMON.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError("segment 1336 runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard complete verified Base wording without inheriting its VM."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1336 Base promoted input drifted")
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
        key = (15, record_id)
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
            if COMMON.literal_texts(base_source, coordinate) == source_literals
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
            or literal_matches
            != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches
            != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1336 Base search drifted: {record_id}"
            )
        donor_coordinates = SEMANTIC_BASE_CONTEXT[record_id]
        references: list[tuple[Any, ...]] = []
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1336 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "complete_verified_wording",
                "runtime_vm_not_inherited",
            ))
        donor_key = SELECTED_BASE_DONOR[record_id]
        donor_translations: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            donor_coordinate = (
                f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
            )
            if donor_coordinate in base_rows:
                donor_translations.append(
                    str(base_rows[donor_coordinate]["translation"])
                )
            elif (
                record_id == 255
                and literal_id == 2
                and source_literals[literal_id] == "\n"
                and current_literals[literal_id] == "\n"
            ):
                donor_translations.append("\n")
            else:
                raise RuntimeError(
                    "segment 1336 donor assembly drifted: "
                    f"{donor_coordinate}"
                )
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append(
                    "segment_manual_verified_base_wording"
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
                        f"segment 1336 companion drifted: {coordinate}"
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
                        f"segment 1336 hidden newline drifted: {coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1336 incomplete record: {coordinate}"
                )
        adapted_to_current_vm = record_id in {259, 261}
        if (
            not adapted_to_current_vm
            and tuple(assembled) != tuple(donor_translations)
        ):
            raise RuntimeError(
                f"segment 1336 complete assembly drifted: {record_id}"
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
                "verified_base_wording_adapted_to_pk_vm"
                if adapted_to_current_vm
                else "complete_verified_base_wording"
            ),
        ))
        assembly_evidence.append((
            record_id,
            tuple(owners),
            tuple(assembled),
            tuple(donor_translations),
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
        raise RuntimeError("segment 1336 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    """Allow only verified donor outer-whitespace boundary changes."""
    COMMON.CORE.guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        COMMON.CORE.EXPECTED_TARGET_COORDINATE_SHA256,
    )
    COMMON.CORE.guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        COMMON.CORE.EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    COMMON.CORE.guarded_digest(
        "speaker style",
        COMMON.CORE.SPEAKER_STYLE,
        COMMON.CORE.EXPECTED_SPEAKER_STYLE_SHA256,
    )
    COMMON.CORE.guarded_digest(
        "terminology policy",
        COMMON.CORE.TERMINOLOGY_POLICY,
        COMMON.CORE.EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    changed = 0
    allowed_outer_change: set[str] = set()
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or set(COMMON.CORE.DYNAMIC_COORDINATES)
        != set(TARGET_COORDINATES)
        or COMMON.CORE.STATIC_COORDINATES
        or COMMON.ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
    ):
        raise RuntimeError("segment 1336 semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = COMMON.coordinate_key(coordinate)
        current_text = COMMON.literal_texts(
            records_by_label["current"], key[:2]
        )[key[2]]
        changed += translation != current_text
        current_signature = dict(
            COMMON.ENGINE.protected_signature(current_text)
        )
        translated_signature = dict(
            COMMON.ENGINE.protected_signature(translation)
        )
        if coordinate in allowed_outer_change:
            current_signature.pop("leading_whitespace", None)
            current_signature.pop("trailing_whitespace", None)
            translated_signature.pop("leading_whitespace", None)
            translated_signature.pop("trailing_whitespace", None)
        if (
            translation.count("\n") != current_text.count("\n")
            or translated_signature != current_signature
        ):
            raise RuntimeError(
                f"segment 1336 shape drifted: {coordinate}"
            )
    if changed != CONFIG["expected_changed_literal_count"]:
        raise RuntimeError("segment 1336 changed count drifted")


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)
    COMMON.CORE.assert_context_contracts = assert_context_contracts
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.assert_semantics = assert_semantics


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.assert_context_contracts = assert_context_contracts
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.assert_semantics = assert_semantics


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
