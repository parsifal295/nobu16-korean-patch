#!/usr/bin/env python3
"""Build source-redacted PK B095 segment 1291 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (3400, 3405)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1291,
    queue_start=134,
    queue_stop=200,
    slice_first="9:3397:0",
    slice_last="9:3455:1",
    target_coordinates=(
        "9:3400:0",
        "9:3405:0",
    ),
    translations={
        "9:3400:0": (
            "본성을 빼앗겼습니까……\n"
            "만회할 방도를 강구해야 합니다……"
        ),
        "9:3405:0": "본성을 잃다니……\n",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        3400: 1,
        3405: 2,
    },
    prefill_companion_coordinates=("9:3405:1",),
    prefill_companion_donor={
        "9:3405:1": "9:3176:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        3400: ("9:3172:0",),
        3405: ("9:3176:0", "9:3176:1"),
    },
    expected_base_raw_matches={
        3400: (),
        3405: (),
    },
    expected_base_literal_matches={
        3400: (),
        3405: (),
    },
    expected_base_masked_matches={
        3400: (),
        3405: (),
    },
    expected_controls_by_record={
        3400: ((), ()),
        3405: ((1,), ()),
    },
    source_call_roots=(1,),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3395, 3457)
    ),
    speaker_style=(
        (3400, "polite_citadel_loss_recovery_assessment"),
        (3405, "dynamic_citadel_loss_final_lament"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("recover the situation", "만회하다"),
        ("devise a measure", "방도를 강구하다"),
        ("dynamic house call", "direct call 1"),
        ("final lament", "이제 끝인가"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record arrays were manually reviewed; both PK-only citadel-loss "
        "records have no Base raw, literal or operand-masked match, while two "
        "completed parallel Base retreat-route-loss records supply semantic "
        "structure, recovery vocabulary, polite and lamenting registers and "
        "the approved same-record dynamic companion only; Base runtime and VM "
        "state are never inherited; 본성, 만회할 방도를 강구하다 and the "
        "dynamic final-lament assembly retain the loss and recovery meanings; "
        "both two-line records preserve literal arity, direct call 1, empty "
        "inline-token set, protected trailing newline, gap and terminator; all "
        "sixty-four slice prefills, pins, two-run reproduction, tamper "
        "rejection, mutual neighbor, reverse overlays, outside-scope identity "
        "and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=2,
    pins={
        "expected_queue_universe_sha256":
        "7B3B9B0B06E04011E8B4BBAC53D62B2F68AC2E1D12BD0D834CB019A578EB8533",
        "expected_queue_slice_sha256":
        "DD153C6BCA4A483C4C531696B05EE769F822151AAD54F921724A53741776BB8F",
        "expected_prefilled_coordinate_sha256":
        "A6E39B9D0A31DF9DF72EFA436714467898DDCD245CF115445B821047CF9196A8",
        "expected_prefill_slice_context_sha256":
        "56DE64A59E1CD7A873052B23BD83444C75479C6AB6A8DC77DCA50A5EA9C5D529",
        "expected_target_coordinate_sha256":
        "A26F05A85BB45A80B8AAFF341F9F25CDEF6842791B837AB10FD03C87E0F52061",
        "expected_source_target_sha256":
        "26F814774D6D9CDA965D4672F2885FC652B54A0C4EFA5477307EAD730DE8CF84",
        "expected_current_target_sha256":
        "D3632B6E0B2FEFB093DEEF46E8E64B38EDD85D9F658CC6AC85FF82ABE035B775",
        "expected_context_corpus_sha256":
        "6276BBF2CEF6E50D3E16C284CAB351F31C60FF5CF389E12558568085E0CDA33F",
        "expected_gap_contract_sha256":
        "AC4ECA29BFF4C4C32F678F663B2FE636524F808F26DB96295F661344EC7F5B7D",
        "expected_boundary_sha256":
        "5A404241DB1004B15B6D4B8CD425FC932D9580872AF9D3172364827FCCFF3080",
        "expected_runtime_control_sha256":
        "739A1B33EDCF73074249600955B5339904F6E25B6B5CC84C3E243262ADBE5CD2",
        "expected_base_search_sha256":
        "E128A0E54AC2ADCA7348752441D4FC91F2FABAD0F783EAF39B4942CCBF7DCB40",
        "expected_complete_assembly_sha256":
        "FEA80616E8592ED03856DF9F3C8D92421AF41D2C7CB139DFC22C7DE04DF159AD",
        "expected_call_graph_sha256":
        "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD",
        "expected_speaker_style_sha256":
        "8E51DEF8B8D0CDE22863CD34A2C0EE1AA17958D9B1D35211BA189CFB9E0561A6",
        "expected_terminology_policy_sha256":
        "BA9C2E75A880A26EE0F3C6EBC3671E3C1E9FD80E033AE72AE2B7999685EEA904",
        "expected_translation_policy_sha256":
        "A3AAA7DCA50DFB2962F059FA1E6CD85C3FF85AD3C735AE0101778A593564600A",
        "expected_candidate_sha256":
        "018BE58F3AFB8743BFA3F4182872B95071647E5D477CD34D5FEB2E31D00BE9CF",
        "expected_combined_slice_candidate_sha256":
        "C11B65730E13CF8BE95F8F36B08416BFF47C4F1C0DCC1A5895717947DA69480C",
        "expected_combined_changed_literal_count": 64,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B095_S1291",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B095_S1291.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B095_S1290.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B095",
    "queue_row_count": 192,
    "queue_visible_count": 200,
    "queue_first": "9:3264:0",
    "queue_last": "9:3455:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
