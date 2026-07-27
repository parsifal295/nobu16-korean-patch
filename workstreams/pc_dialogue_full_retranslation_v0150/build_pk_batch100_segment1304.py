#!/usr/bin/env python3
"""Build source-redacted PK B100 segment 1304 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_BASE_ASSEMBLY = COMMON.BASE.base_and_assembly_evidence
_ORIGINAL_BASE_READ_JSONL = COMMON.BASE.read_jsonl

TARGET_RECORD_IDS = (
    4090, 4091, 4092, 4093, 4094, 4095, 4096,
    4097, 4098, 4099, 4100, 4101, 4102, 4103,
    4104, 4106, 4107, 4110, 4111, 4117, 4118,
)
EXACT_BASE_DONOR = {
    record_id: (9, record_id - 318)
    for record_id in TARGET_RECORD_IDS
}
REAL_PREFILL_COMPANION_COORDINATES = (
    "9:4095:2",
    "9:4101:1",
    "9:4102:0",
    "9:4106:1",
    "9:4107:0",
    "9:4107:2",
    "9:4110:0",
    "9:4110:2",
    "9:4111:0",
    "9:4111:2",
    "9:4117:1",
    "9:4117:5",
    "9:4118:4",
)
OUTSIDE_SLICE_BASE_COMPANION = {
    "9:4118:1": "9:3800:1",
    "9:4118:2": "9:3800:2",
    "9:4118:3": "9:3800:3",
}
PREFILL_COMPANION_COORDINATES = (
    REAL_PREFILL_COMPANION_COORDINATES
    + tuple(OUTSIDE_SLICE_BASE_COMPANION)
)
PREFILL_COMPANION_DONOR = {
    "9:4095:2": "9:3777:2",
    "9:4101:1": "9:3783:1",
    "9:4102:0": "9:3784:0",
    "9:4106:1": "9:3788:1",
    "9:4107:0": "9:3789:0",
    "9:4107:2": "9:3789:2",
    "9:4110:0": "9:3792:0",
    "9:4110:2": "9:3792:2",
    "9:4111:0": "9:3793:0",
    "9:4111:2": "9:3793:2",
    "9:4117:1": "9:3799:1",
    "9:4117:5": "9:3799:5",
    "9:4118:4": "9:3800:4",
    **OUTSIDE_SLICE_BASE_COMPANION,
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1304,
    queue_start=0,
    queue_stop=67,
    slice_first="9:4083:0",
    slice_last="9:4118:0",
    target_coordinates=(
        "9:4090:0",
        "9:4090:1",
        "9:4090:2",
        "9:4091:0",
        "9:4092:0",
        "9:4092:1",
        "9:4092:2",
        "9:4092:3",
        "9:4093:0",
        "9:4093:1",
        "9:4093:2",
        "9:4093:3",
        "9:4094:0",
        "9:4095:0",
        "9:4095:1",
        "9:4096:0",
        "9:4096:1",
        "9:4096:2",
        "9:4096:3",
        "9:4097:0",
        "9:4098:0",
        "9:4099:0",
        "9:4099:1",
        "9:4100:0",
        "9:4100:1",
        "9:4100:2",
        "9:4101:0",
        "9:4102:1",
        "9:4102:2",
        "9:4103:0",
        "9:4104:0",
        "9:4106:0",
        "9:4107:1",
        "9:4110:1",
        "9:4111:1",
        "9:4117:0",
        "9:4117:2",
        "9:4117:3",
        "9:4117:4",
        "9:4118:0",
    ),
    translations={
        "9:4090:0": "이렇게 우세한데 강화를 맺으라니…?\n",
        "9:4090:1": "쓰노쿠마",
        "9:4090:2": " 님은 지나치게 소극적이다!",
        "9:4091:0": (
            "이리된 이상, 우리가 선봉에 서서\n"
            "무리해서라도 싸움을 시작할 수밖에 없다"
        ),
        "9:4092:0": "다키타",
        "9:4092:1": "와 ",
        "9:4092:2": "사이키",
        "9:4092:3": (
            "가 멋대로 출진했다고…!?\n"
            "강화도, 오토모도 망칠 셈인가…!"
        ),
        "9:4093:0": "도시히사",
        "9:4093:1": "의 말대로다\n",
        "9:4093:2": "오토모",
        "9:4093:3": "군은 일부만 나왔구나",
        "9:4094:0": (
            "강화 사절이 효과를 냈군요\n"
            "방침을 두고 서로 반목한 모양입니다"
        ),
        "9:4095:0": "계획대로 츠리노부세를 펼친다\n",
        "9:4095:1": "오토모",
        "9:4096:0": "다다무네",
        "9:4096:1": "!\u3000",
        "9:4096:2": "도시히사",
        "9:4096:3": "!\n너희는 샛길에 병력을 매복시켜라!",
        "9:4097:0": "분부대로 하겠사옵니다……",
        "9:4098:0": (
            "맡겨 주시오!\n"
            "그런데, 정작 유인 역할은 누가 맡소?"
        ),
        "9:4099:0": "혼고",
        "9:4099:1": (
            "공, 위험한 역할이지만 맡아 주겠는가\n"
            "아군 진영 깊숙이 적을 유인해야 하네"
        ),
        "9:4100:0": "알겠소!\u3000이 몸도",
        "9:4100:1": "시마즈",
        "9:4100:2": (
            "일문의 말석\n"
            "이 중책을 훌륭히 완수해 보이겠소이다"
        ),
        "9:4101:0": "요시히로",
        "9:4102:1": "이에히사",
        "9:4102:2": "에게도 출격해 달라고 하겠다",
        "9:4103:0": (
            "이런 소수 병력이 선봉이라니 가소롭구나!\n"
            "당장 쓸어버려 주마!!"
        ),
        "9:4104:0": (
            "놈들, 미끼를 물었군……\n"
            "더 깊이 끌어들인다!\u3000퇴각을 시작하라!"
        ),
        "9:4106:0": "혼고",
        "9:4107:1": "다키타 일행",
        "9:4110:1": "오토모",
        "9:4111:1": "다카조가와",
        "9:4117:0": "오토모",
        "9:4117:2": "쓰노쿠마가",
        "9:4117:3": " 없는 ",
        "9:4117:4": "오토모",
        "9:4118:0": "이것은 ",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        4090: 3,
        4091: 1,
        4092: 4,
        4093: 4,
        4094: 1,
        4095: 3,
        4096: 4,
        4097: 1,
        4098: 1,
        4099: 2,
        4100: 3,
        4101: 2,
        4102: 3,
        4103: 1,
        4104: 1,
        4106: 2,
        4107: 3,
        4110: 3,
        4111: 3,
        4117: 6,
        4118: 5,
    },
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        record_id: tuple(
            f"9:{record_id - 318}:{literal_id}"
            for literal_id in range({
                4090: 3,
                4091: 1,
                4092: 4,
                4093: 4,
                4094: 1,
                4095: 3,
                4096: 4,
                4097: 1,
                4098: 1,
                4099: 2,
                4100: 3,
                4101: 2,
                4102: 3,
                4103: 1,
                4104: 1,
                4106: 2,
                4107: 3,
                4110: 3,
                4111: 3,
                4117: 6,
                4118: 5,
            }[record_id])
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_raw_matches={
        record_id: (
            (9, record_id - 318),
            (17, record_id - 4087),
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_literal_matches={
        record_id: (
            (9, record_id - 318),
            (17, record_id - 4087),
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_masked_matches={
        record_id: (
            (9, record_id - 318),
            (17, record_id - 4087),
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_controls_by_record={
        record_id: ((), ())
        for record_id in TARGET_RECORD_IDS
    },
    source_call_roots=(),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3771, 4120)
    ),
    speaker_style=(
        (4090, "forceful_council_opposition"),
        (4091, "forceful_unauthorized_vanguard"),
        (4092, "shocked_council_rebuke"),
        (4093, "confident_lord_confirmation"),
        (4094, "formal_strategist_report"),
        (4095, "commanding_ambush_order"),
        (4096, "commanding_lord_assignment"),
        (4097, "archaic_respectful_retainer"),
        (4098, "seasoned_retainer_question"),
        (4099, "lord_dangerous_assignment_request"),
        (4100, "proud_clan_retainer_acceptance"),
        (4101, "commanding_tactical_assignment"),
        (4102, "commanding_followup_assignment"),
        (4103, "enemy_forceful_vanguard_boast"),
        (4104, "decoy_retreat_order"),
        (4106, "calm_battlefield_monitoring"),
        (4107, "alarmed_rescue_order"),
        (4110, "decisive_general_advance"),
        (4111, "forceful_charge_order"),
        (4117, "grim_execution_order"),
        (4118, "alarmed_retreat_monologue"),
    ),
    terminology_policy=(
        ("peace settlement", "강화"),
        ("unauthorized sortie", "멋대로 출진"),
        ("decoy ambush tactic", "츠리노부세"),
        ("vanguard", "선봉"),
        ("ambush troops", "복병"),
        ("retreat", "퇴각"),
        ("historical surname", "다키타"),
        ("historical surname", "사이키"),
        ("historical surname", "혼고"),
        ("historical river", "다카조가와"),
        ("warrior epithet", "오니시마즈"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "pristine PK JP is authoritative and the available EN, SC and TC "
        "same-record fields were checked; every complete source record has "
        "byte-exact completed Base matches in two blocks, and the direct "
        "scenario mapping plus the generated exact-prefill coordinates "
        "select the block-nine Korean solely as semantic content; the "
        "alternate completed duplicate was reviewed but not mixed into a "
        "record; Base runtime and VM state are never inherited; thirteen "
        "approved static prefills and three completed-Base semantic "
        "companions beyond the slice boundary complete all twenty-one "
        "records without creating extra decisions; historical surnames, "
        "the decoy-ambush tactic, river name and warrior epithet follow the "
        "completed scenario terminology; all color gaps, full-width spaces, "
        "punctuation, line counts, literal arity and terminators are "
        "preserved; all pins, two-run reproduction, tamper rejection, "
        "reverse overlays, outside-scope identity and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=24,
    pins={
        "expected_queue_universe_sha256":
        "16465EB37A9E84E6A85010F206205CC0F89F8F62024BE6738F8C4E55821EFBC3",
        "expected_queue_slice_sha256":
        "47ABF4D27758A42484C42B67307B7A4A548F80914951D2F2C8B77DFB517ED70A",
        "expected_prefilled_coordinate_sha256":
        "FF8B597DECCFDB3D143ABCD6469B128D5031BA131C31073454F0D9C41E53A320",
        "expected_prefill_slice_context_sha256":
        "795289234E92B9886E94AA6D64340D109D265864B44548A9CB723F7C642B69DC",
        "expected_target_coordinate_sha256":
        "4EEEA1E21B10EDC75ECAE486BE3D671894A3B9B675D0E715C55478E43A5ACEC2",
        "expected_source_target_sha256":
        "BB8E633B7A266C8077C2313960F2F30502D9CC61DF5DDF931D209E5D7355EC92",
        "expected_current_target_sha256":
        "1F140A6AA0B3F3BF948B3549470F097CD09F1C6FC0FE58B1039653D72678A1C1",
        "expected_context_corpus_sha256":
        "F0C52F91A97DF577CBD26FB29DCED18C22EAB215EB4433B1FE13BA7E8BB28E82",
        "expected_gap_contract_sha256":
        "DBED40AAE3613EA08B0A59F948425A5072F6F92AF44CE529410BDC7EFC86B617",
        "expected_boundary_sha256":
        "1A1DE46D709CB075537C8170FE898222C0891F5C45C57BB9AF4C6E8284B92F44",
        "expected_runtime_control_sha256":
        "F52B2C64C64CDD52F510F8EE4C57242D3572B28CBB0306E4308C38DD8ADD5878",
        "expected_base_search_sha256":
        "63A9C437AF950ED69E70E5028355813A1FE1710F29F32FE0A82A0A8558409F85",
        "expected_complete_assembly_sha256":
        "CB26154CF81FE73B9875A4F1DB853CADB9E10D768EDAB29D1BED2B0D80DB9308",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "758FFBA049CF7A84DCDB4D84A0658A24ED2210AC1C73B490052181A3606F3E6A",
        "expected_terminology_policy_sha256":
        "EEEFE8AABB06C79DE85E2B432617B153515583664127361474CCCE3ED93C2984",
        "expected_translation_policy_sha256":
        "B7F8D3AF116AA6DAECB38E56777FEB201BE657366C7D3C4535C9D16136010230",
        "expected_candidate_sha256":
        "00EFD07AB82730E6E15483CE6468672B59B179F8278A1CC0EF786F1D042E6934",
        "expected_combined_slice_candidate_sha256":
        "E54B716766896678FFC8F7E9F2A214EA49DEFDA4797C526FA8BB854E2C2EB915",
        "expected_combined_changed_literal_count": 46,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B100_S1304",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B100_S1304.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B099_S1303.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B100_S1305.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B100",
    "queue_row_count": 106,
    "queue_visible_count": 197,
    "queue_first": "9:4083:0",
    "queue_last": "12:45:5",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Preserve static prefills and semantic companions without VM reuse."""

    base_rows = {
        str(row["coordinate"]): row
        for row in _ORIGINAL_BASE_READ_JSONL(COMMON.BASE_PROMOTED)
        if "translation" in row
    }

    def compatible_read_jsonl(path: Path) -> list[dict[str, Any]]:
        rows = _ORIGINAL_BASE_READ_JSONL(path)
        if path != COMMON.PREFILL:
            return rows
        compatible: list[dict[str, Any]] = []
        for row in rows:
            copied = dict(row)
            coordinate = str(copied.get("coordinate", ""))
            if coordinate in REAL_PREFILL_COMPANION_COORDINATES:
                if copied.get("runtime_review") != "not_required":
                    raise RuntimeError(
                        "segment 1304 static prefill review drifted"
                    )
                copied["runtime_review"] = "pending"
            compatible.append(copied)
        for coordinate, donor_coordinate in (
            OUTSIDE_SLICE_BASE_COMPANION.items()
        ):
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1304 outside-slice Base companion drifted"
                )
            compatible.append({
                "coordinate": coordinate,
                "translation": str(donor["translation"]),
                "semantic_review": "approved",
                "runtime_review": "pending",
                "base_exact_reuse_prefill": {
                    "base_coordinate": donor_coordinate,
                    "runtime_promotion_authorized": False,
                },
            })
        return compatible

    original_read_jsonl = COMMON.BASE.read_jsonl
    COMMON.BASE.read_jsonl = compatible_read_jsonl
    try:
        base, assembly = _ORIGINAL_BASE_ASSEMBLY(
            prepared, records_by_label
        )
    finally:
        COMMON.BASE.read_jsonl = original_read_jsonl

    adjusted: list[tuple[Any, ...]] = []
    for evidence in assembly:
        record_id = int(evidence[0])
        owners = list(evidence[1])
        for literal_id, owner in enumerate(owners):
            coordinate = f"9:{record_id}:{literal_id}"
            if coordinate in REAL_PREFILL_COMPANION_COORDINATES:
                if owner != "base_exact_prefill_runtime_pending":
                    raise RuntimeError(
                        "segment 1304 static prefill ownership drifted"
                    )
                owners[literal_id] = (
                    "base_exact_prefill_runtime_not_required"
                )
            elif coordinate in OUTSIDE_SLICE_BASE_COMPANION:
                if owner != "base_exact_prefill_runtime_pending":
                    raise RuntimeError(
                        "segment 1304 outside companion ownership drifted"
                    )
                owners[literal_id] = (
                    "completed_base_semantic_companion_outside_slice"
                )
        adjusted.append((evidence[0], tuple(owners), *evidence[2:]))
    return base, tuple(adjusted)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        base_and_assembly_evidence,
    )


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
