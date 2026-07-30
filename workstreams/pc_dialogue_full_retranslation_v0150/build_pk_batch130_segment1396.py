#!/usr/bin/env python3
"""Build source-redacted PK B130 segment 1396 residual decisions."""

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
    "15:2263:2",
    "15:2266:0",
    "15:2267:0",
    "15:2268:2",
    "15:2273:0",
    "15:2273:1",
    "15:2274:0",
    "15:2274:1",
    "15:2274:2",
    "15:2274:4",
    "15:2275:0",
    "15:2275:1",
    "15:2275:2",
    "15:2275:3",
    "15:2275:5",
    "15:2277:0",
    "15:2280:1",
    "15:2282:0",
    "15:2284:0",
    "15:2285:0",
    "15:2285:1",
    "15:2286:2",
    "15:2289:0",
)
TRANSLATIONS = {
    "15:2263:2": "가?",
    "15:2266:0": "들에게\n",
    "15:2267:0": "알겠",
    "15:2268:2": "상책이라 사료됩니다.",
    "15:2273:0": "또한,",
    "15:2273:1": (
        "에게는 우호 세력이 없으니\n"
        "원군을 부를 걱정도 없습니다"
    ),
    "15:2274:0": "또한,",
    "15:2274:1": "은(는)\n",
    "15:2274:2": "을(를) 우호 세력으로 두고 있",
    "15:2274:4": "주의해",
    "15:2275:0": "또한,",
    "15:2275:1": "은(는)\n",
    "15:2275:2": "을(를) 비롯한",
    "15:2275:3": "개 세력을 우호 세력으로 두고 있",
    "15:2275:5": "주의해",
    "15:2277:0": "아직 개발할 성이 남아 있습니다. ",
    "15:2280:1": "의",
    "15:2282:0": "아직 개발할 수 있는 성이 남아",
    "15:2284:0": (
        "적군은 침공에 만반의 대비를 갖춘 듯합니다……\n"
        "수비를 굳힌 성을 함락하려면\n"
        "대규모 공성전을 각오해야 합니다."
    ),
    "15:2285:0": "헌언을 허락해 주시",
    "15:2285:1": "니,",
    "15:2286:2": "참조해",
    "15:2289:0": "……알겠",
}
TARGET_RECORD_IDS = (
    2263,
    2266,
    2267,
    2268,
    2273,
    2274,
    2275,
    2277,
    2280,
    2282,
    2284,
    2285,
    2286,
    2289,
)
EXPECTED_ARITY = {
    2263: 3,
    2266: 2,
    2267: 3,
    2268: 3,
    2273: 2,
    2274: 5,
    2275: 6,
    2277: 2,
    2280: 3,
    2282: 2,
    2284: 1,
    2285: 4,
    2286: 3,
    2289: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2263:0",
    "15:2263:1",
    "15:2266:1",
    "15:2267:2",
    "15:2268:0",
    "15:2268:1",
    "15:2274:3",
    "15:2275:4",
    "15:2277:1",
    "15:2280:0",
    "15:2280:2",
    "15:2282:1",
    "15:2285:2",
    "15:2285:3",
    "15:2286:0",
    "15:2286:1",
    "15:2289:1",
)
PREFILL_COMPANION_DONOR = {
    "15:2263:0": "15:2233:0",
    "15:2263:1": "15:2233:1",
    "15:2266:1": "15:2236:1",
    "15:2267:2": "15:2237:2",
    "15:2268:0": "15:2238:0",
    "15:2268:1": "15:2238:1",
    "15:2274:3": "15:2244:1",
    "15:2275:4": "15:2244:1",
    "15:2277:1": "15:2247:1",
    "15:2280:0": "15:2250:0",
    "15:2280:2": "15:2250:2",
    "15:2282:1": "15:2252:1",
    "15:2285:2": "15:2254:2",
    "15:2285:3": "15:2254:3",
    "15:2286:0": "15:2255:0",
    "15:2286:1": "15:2255:1",
    "15:2289:1": "15:2258:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:2267:1",)
EXACT_BASE_DONOR = {
    2263: (15, 2233),
    2266: (15, 2236),
    2268: (15, 2238),
    2277: (15, 2247),
    2280: (15, 2250),
    2282: (15, 2252),
    2285: (15, 2254),
    2286: (15, 2255),
    2289: (15, 2258),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id in EXACT_BASE_DONOR
    },
    2267: (
        "15:2237:0",
        "15:2237:2",
    ),
    2273: ("15:2243:0",),
    2274: (
        "15:2244:0",
        "15:2244:1",
        "15:2244:2",
    ),
    2275: (
        "15:2245:0",
        "15:2245:1",
        "15:2245:2",
        "15:2245:3",
    ),
    2284: (
        "7:1342:0",
        "7:1345:0",
        "15:2221:0",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    2263: (),
    2266: ((15, 2236),),
    2267: (),
    2268: (),
    2273: (),
    2274: (),
    2275: (),
    2277: (),
    2280: ((15, 2250),),
    2282: ((15, 2252),),
    2284: (),
    2285: (),
    2286: (),
    2289: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    2263: ((15, 2233),),
    2266: ((15, 2236),),
    2267: ((15, 2237),),
    2268: ((15, 2238),),
    2273: (),
    2274: (),
    2275: (),
    2277: ((15, 2247),),
    2280: ((15, 2250),),
    2282: ((15, 2252),),
    2284: (),
    2285: ((15, 2254),),
    2286: ((15, 2255),),
    2289: ((15, 2258),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2263: ((700, 610), ("026432",)),
    2266: ((), ("026E32", "026432")),
    2267: ((538, 1096), ("026E32",)),
    2268: ((742, 1048), ()),
    2273: ((754,), ("025032",)),
    2274: ((178, 1174, 412), ("025032", "025132")),
    2275: (
        (178, 1174, 412),
        ("025032", "025132", "0232"),
    ),
    2277: ((82, 700, 610), ()),
    2280: ((), ("023C", "025032")),
    2282: ((82, 148), ()),
    2284: ((286,), ()),
    2285: ((1168, 280, 1, 1162, 514), ()),
    2286: ((568, 1174, 412), ()),
    2289: ((628,), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    2268: ((), ()),
    2277: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1396,
    queue_start=134,
    queue_stop=199,
    slice_first="15:2262:0",
    slice_last="15:2289:1",
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
        1,
        82,
        148,
        178,
        280,
        286,
        412,
        514,
        538,
        568,
        610,
        628,
        700,
        742,
        754,
        1048,
        1096,
        1162,
        1168,
        1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2193, 2290)
    ),
    speaker_style=(
        (2263, "formal_marching_unit_target_proposal"),
        (2266, "formal_siege_order_confirmation"),
        (2267, "formal_return_to_castle_acknowledgement"),
        (2268, "humble_wait_for_opportunity_advice"),
        (2273, "formal_no_enemy_allies_assessment"),
        (2274, "formal_single_enemy_ally_warning"),
        (2275, "formal_multiple_enemy_allies_warning"),
        (2277, "formal_castle_development_proposal"),
        (2280, "formal_future_diplomatic_target_advice"),
        (2282, "formal_castle_development_and_opportunity_advice"),
        (2284, "formal_large_scale_siege_warning"),
        (2285, "humble_counsel_introduction"),
        (2286, "humble_written_proposal_reference"),
        (2289, "solemn_lord_and_people_warning"),
    ),
    terminology_policy=(
        ("marching unit", "출진 중인 부대"),
        ("siege target", "공략 목표"),
        ("return to castle", "성으로 돌아오다"),
        ("best policy", "상책"),
        ("friendly force", "우호 세력"),
        ("reinforcements", "원군"),
        ("castle development", "성 개발"),
        ("crop yield", "석고"),
        ("opportunity", "호기"),
        ("invasion preparation", "침공 대비"),
        ("fortified castle", "수비를 굳힌 성"),
        ("large-scale siege", "대규모 공성전"),
        ("counsel", "헌언"),
        ("lord", "영주"),
        ("commoners", "백성"),
        ("project ellipsis", "……"),
        ("particle compatibility", "을(를)\u00b7은(는)"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B130 queue ordinals one hundred "
        "thirty-four through one hundred ninety-eight and the approved Base "
        "prefill; pristine PK JP is authoritative and every populated EN, "
        "SC and TC same-record fragment array was reviewed as auxiliary "
        "context; nine complete records reuse approved completed Base "
        "Korean assemblies selected by raw, literal and operand-masked "
        "source identity with explicit exact donors, one return-to-castle "
        "record reuses the matching Base visible assembly through semantic "
        "references because its newline-only fragment has no promoted "
        "decision row, three enemy-alliance warning records adapt the "
        "adjacent completed Base warning assemblies to their additional "
        "force and count tokens, and the siege warning is manually "
        "translated from authoritative JP with completed Base fortification "
        "and siege terminology as semantic context; Base runtime and VM "
        "state are never inherited; marching units, siege targets, castle "
        "returns, opportunities, friendly forces, reinforcements, castle "
        "development, crop yield, invasion preparation, fortified castles, "
        "large-scale sieges, counsel, lords and commoners retain established "
        "historical project wording and each formal, humble or solemn "
        "speaker register; direct calls, inline officer, force and count "
        "tokens, colour tags, protected outer whitespace, newlines, gaps, "
        "literal arity, particles, ellipses, terminators, all seventeen "
        "same-record prefills, the hidden newline, all forty-two slice "
        "prefills, complete assemblies, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, reciprocal "
        "S1394 and S1395 decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=15,
    pins={
        "expected_queue_universe_sha256": (
            "71C7EBC3AABF0AAB3370592930BE4C339E6E63D3343A8F498ED5901F3682AB2F"
        ),
        "expected_queue_slice_sha256": (
            "5F8C14DCCBE554437679D3274600C48BED483C0EBEB5896EEA69EF9191B2C9F9"
        ),
        "expected_prefilled_coordinate_sha256": (
            "CEA32A4225C86EE124E48E2594E87ED690930AC84DE2F5C019FC8827D8EBE831"
        ),
        "expected_prefill_slice_context_sha256": (
            "BF3219E0BBECB79ED47D237D001BECBCA3D2DA3E2B3147127681D9B012EAE16E"
        ),
        "expected_target_coordinate_sha256": (
            "5EC36DC6D39A3F41AAF43057F3068199AAADA818D2A01A29EFBEB7785DAF8A7C"
        ),
        "expected_source_target_sha256": (
            "558E7DE45C2EE3AE26A0AAAAD7AEAC07913BC555DA8336C1284D208D7B013385"
        ),
        "expected_current_target_sha256": (
            "204472C83F9DE2037D71C7DA59FC326BE6AB47CA2D9CEF47D941BEB9EF061C58"
        ),
        "expected_context_corpus_sha256": (
            "03DC62C7A0C8C3AC07AF97A148F0BBDD47026D2571EEED897A543B68CCA58C0C"
        ),
        "expected_gap_contract_sha256": (
            "7EBEAF9DB1ADD43404E03E16E73BF5400D93E9D97D96FD16D4118E4E56CF88AC"
        ),
        "expected_boundary_sha256": (
            "7467DB14080A7E4376057EA9ADE6309322C12E5E445D91626D21F1E30DAC5890"
        ),
        "expected_runtime_control_sha256": (
            "213E2A257AF5E6EA11A097A2089F14A084DEEA5FF5BF99A12B6644D4729FBE8C"
        ),
        "expected_base_search_sha256": (
            "52DD877585BC76DB36B71387F6F8256F8A07634905AE2B24C0FFD302869F45FE"
        ),
        "expected_complete_assembly_sha256": (
            "FD34507B28F0FF13E69C741A2F553D01B0BB1BF779580D65CE6AC95667E4E68D"
        ),
        "expected_call_graph_sha256": (
            "49CB841ACE026AEC20FC8AFBC4D2340DAC1979D3110E0767B7CFF44F7C7AFFB7"
        ),
        "expected_speaker_style_sha256": (
            "4A36D788777C2FB9108C26198FA97692AE0BC11EB8013EC429701CB8A7245236"
        ),
        "expected_terminology_policy_sha256": (
            "1C86B26B150D7F2FC7DCF3EFC0B9D7BF35938757A55F0891F95C7516B74A9238"
        ),
        "expected_translation_policy_sha256": (
            "453987C1C94A3AF8428F80C89B2341A038F3DB6870539D7F13977CDD134ABC55"
        ),
        "expected_candidate_sha256": (
            "C6E7A62F3109DDF5719021635D0F0C227D6340AF60707633385BC7F53145B2BA"
        ),
        "expected_combined_slice_candidate_sha256": (
            "470B343CEDABA61F52EEC0515CD5C72DB1D0D0A4110AC9318ABEF2267B066BBB"
        ),
        "expected_combined_changed_literal_count": 52,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B130_S1396",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1396.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1394.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1395.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B130",
    "queue_row_count": 97,
    "queue_visible_count": 199,
    "queue_first": "15:2193:0",
    "queue_last": "15:2289:1",
})


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    """Guard the two known current records whose legacy calls are absent."""
    values = COMMON.CORE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        (
            "source target",
            values["source_target"],
            CONFIG["expected_source_target_sha256"],
        ),
        (
            "current target",
            values["current_target"],
            CONFIG["expected_current_target_sha256"],
        ),
        (
            "multilingual context",
            values["corpus"],
            CONFIG["expected_context_corpus_sha256"],
        ),
        (
            "gap contract",
            values["gaps"],
            CONFIG["expected_gap_contract_sha256"],
        ),
        (
            "boundary",
            values["boundary"],
            CONFIG["expected_boundary_sha256"],
        ),
        (
            "runtime control",
            values["controls"],
            CONFIG["expected_runtime_control_sha256"],
        ),
    ):
        COMMON.CORE.guarded_digest(label, value, expected)
    expected_controls = tuple(
        (
            label,
            record_id,
            (
                EXPECTED_CONTROLS_BY_RECORD[record_id]
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    mismatched_gap_records = {
        record_id
        for record_id, source, current in values["gaps"]
        if source != current
    }
    if (
        values["controls"] != expected_controls
        or mismatched_gap_records != {2268, 2277}
        or any(
            ("pk_msggame", *COMMON.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError("segment 1396 runtime layout drifted")


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.assert_context_contracts = assert_context_contracts
    COMMON.CORE.assert_context_contracts = assert_context_contracts


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
