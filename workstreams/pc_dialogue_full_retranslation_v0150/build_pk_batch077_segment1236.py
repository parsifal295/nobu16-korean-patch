#!/usr/bin/env python3
"""Build source-redacted PK B077 segment 1236 residual decisions."""

from pathlib import Path

from build_pk_batch077_common import make_config, run


SCRIPT = Path(__file__).resolve()
TARGET_RECORD_IDS = (
    1028, 1029, 1030, 1031, 1032, 1039, 1040, 1041, 1042,
)
BASE_DONORS = {
    1028: 1016,
    1029: 1017,
    1030: 1018,
    1031: 1019,
    1032: 1020,
    1039: 1027,
    1040: 1028,
    1041: 1029,
    1042: 1030,
}
CONFIG = make_config(
    script=SCRIPT,
    segment=1236,
    queue_start=67,
    queue_stop=134,
    slice_first="8:1020:0",
    slice_last="8:1054:1",
    target_coordinates=(
        "8:1028:2",
        "8:1029:0",
        "8:1030:1",
        "8:1031:3",
        "8:1032:4",
        "8:1039:0",
        "8:1040:1",
        "8:1041:0",
        "8:1042:1",
    ),
    translations={
        "8:1028:2": "는가…",
        "8:1029:0": "알겠",
        "8:1030:1": "…",
        "8:1031:3": "시간을…",
        "8:1032:4": "…",
        "8:1039:0": "의",
        "8:1040:1": "의",
        "8:1041:0": "의",
        "8:1042:1": "의",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        1028: 3,
        1029: 3,
        1030: 2,
        1031: 4,
        1032: 5,
        1039: 2,
        1040: 3,
        1041: 2,
        1042: 3,
    },
    prefill_companion_coordinates=(
        "8:1028:0",
        "8:1028:1",
        "8:1029:1",
        "8:1029:2",
        "8:1030:0",
        "8:1031:0",
        "8:1031:1",
        "8:1031:2",
        "8:1032:0",
        "8:1032:1",
        "8:1032:3",
        "8:1039:1",
        "8:1040:2",
        "8:1041:1",
        "8:1042:2",
    ),
    prefill_companion_donor={
        "8:1028:0": "8:1016:0",
        "8:1028:1": "8:1016:1",
        "8:1029:1": "8:1017:1",
        "8:1029:2": "8:1017:2",
        "8:1030:0": "8:1018:0",
        "8:1031:0": "8:1019:0",
        "8:1031:1": "8:1019:1",
        "8:1031:2": "8:1019:2",
        "8:1032:0": "8:1020:0",
        "8:1032:1": "8:1020:1",
        "8:1032:3": "8:1020:3",
        "8:1039:1": "8:1027:1",
        "8:1040:2": "8:1028:2",
        "8:1041:1": "8:1029:1",
        "8:1042:2": "8:1030:2",
    },
    hidden_current_companion_coordinates=(
        "8:1032:2",
        "8:1040:0",
        "8:1042:0",
    ),
    semantic_base_context={
        1028: ("8:1016:0", "8:1016:1", "8:1016:2"),
        1029: ("8:1017:0", "8:1017:1", "8:1017:2"),
        1030: ("8:1018:0", "8:1018:1"),
        1031: ("8:1019:0", "8:1019:1", "8:1019:2", "8:1019:3"),
        1032: ("8:1020:0", "8:1020:1", "8:1020:3", "8:1020:4"),
        1039: ("8:1027:0", "8:1027:1"),
        1040: ("8:1028:1", "8:1028:2"),
        1041: ("8:1029:0", "8:1029:1"),
        1042: ("8:1030:1", "8:1030:2"),
    },
    expected_base_raw_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_base_literal_matches={
        record_id: ((8, BASE_DONORS[record_id]),)
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_masked_matches={
        record_id: ((8, BASE_DONORS[record_id]),)
        for record_id in TARGET_RECORD_IDS
    },
    expected_controls_by_record={
        1028: ((1090, 976), ()),
        1029: ((538, 1, 1066), ()),
        1030: ((568,), ()),
        1031: ((568, 442, 1168), ()),
        1032: ((1, 748, 1174, 460), ()),
        1039: ((268, 1066), ("029632", "023C01430C010000")),
        1040: ((904, 1090), ("029632", "023C")),
        1041: ((268, 1066), ("029632", "023C01430C010000")),
        1042: ((904, 1066), ("029632", "023C")),
    },
    source_call_roots=(
        1, 268, 442, 460, 538, 568, 748,
        904, 976, 1066, 1090, 1168, 1174,
    ),
    boundary_record_keys=tuple(
        (8, record_id)
        for record_id in (
            1015, 1016, 1017, 1018, 1019, 1020, 1021,
            1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033,
            1038, 1039, 1040, 1041, 1042, 1043,
            1053, 1054, 1055,
        )
    ),
    speaker_style=(
        (1028, "strategic_domain_policy_deliberation"),
        (1029, "castle_lord_governance_acceptance"),
        (1030, "ailing_retainer_self_reproach"),
        (1031, "ailing_retainer_recovery_request"),
        (1032, "ailing_retainer_apology"),
        (1039, "urgent_task_response"),
        (1040, "formal_task_acceptance"),
        (1041, "urgent_task_response"),
        (1042, "formal_task_completion_pledge"),
    ),
    terminology_policy=(
        ("civil administration", "내정"),
        ("castle lord", "성주"),
        ("illness", "병"),
        ("recovery", "낫다"),
        ("urgent response", "서둘러 대처"),
        ("task completion", "완수"),
        ("dynamic task and person tokens", "runtime token"),
    ),
    basis=(
        "pristine PK Japanese is authoritative and all available PK English, "
        "Simplified Chinese and Traditional Chinese context was manually "
        "reviewed; nine completed Base records with identical literal and "
        "operand-masked templates supply semantic wording only, while Base "
        "runtime and VM state are never inherited; nine residuals, fifteen "
        "exact-prefill companions and three source-identical hidden newlines "
        "form nine complete records; policy, castle-lord, illness and urgent "
        "task registers, dynamic task and person fragments, inline tokens, "
        "calls, protected whitespace, gaps, boundaries, two-run reproduction, "
        "tamper rejection, reverse overlays, outside-scope identity and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=2,
    pins={
        "expected_queue_universe_sha256":
        "A773BC2A346A94EF11442275CC15B7EC79729ABC130B1FB137130468C8D5B917",
        "expected_queue_slice_sha256":
        "6F219D95B4D11BE2DA4FD3C0375A489B22890CA4AA038D3C7D624CF50ABAEB29",
        "expected_prefilled_coordinate_sha256":
        "AF4AB35F29F8802EDFAE35937789C1AEB16658125747E147D9A410DA3A2E96A8",
        "expected_prefill_slice_context_sha256":
        "C5A6EA99C0C4F3523423B8100DD663FA1A73EC27B3F0C05D26842CBD724DC4AB",
        "expected_target_coordinate_sha256":
        "0FAEE050EE4CFDDA0DF6E131E29CAA315E0C0BA01C1A83EA986FE035AB1F483C",
        "expected_source_target_sha256":
        "0B5797E1DA6F9939F37972B08E17A5F06E9EB77A509CAFCB49086F33F15C7B93",
        "expected_current_target_sha256":
        "89EE73283DCF9D35DFABA7B349F6016BB3BCB6749D321B12A434D23AD7248CEB",
        "expected_context_corpus_sha256":
        "BC6AD64CCD8C2F358FF09BB1BF406A04308A1A9B4F3BBA75A80BEDE5FCC75621",
        "expected_gap_contract_sha256":
        "7CAF01A5798A10153834AC2146EA57F88D325BA8433AFFBBEE6BD2F860FE626E",
        "expected_boundary_sha256":
        "BB7D1DF8943D8C1A5C5F49C99F0CA7D4227AFE213F952F2FDCB0C5612B2AF8FD",
        "expected_runtime_control_sha256":
        "46CA20B51444DC9353F1621850DFDED18E137F1913712E748CA43CBA30C48AFE",
        "expected_base_search_sha256":
        "A25B8A1E0C73DC6D61F1926C1837F46A45CF23FEF20C0360FD2900FFE1EBE6C0",
        "expected_complete_assembly_sha256":
        "1B24C22011550F70B26C2F37577643014A6A7065763B802C178689CB77C4C7CB",
        "expected_call_graph_sha256":
        "64041B93F876F090F89E992BEFB88BBEBFBE9D36BB841D443A337BFCDDA30528",
        "expected_speaker_style_sha256":
        "D71F728CBEC9B312DD99C3D1DD46BF3FEDF15FB41FECC27BAFE194AB29E2AD72",
        "expected_terminology_policy_sha256":
        "14DFD9856BE6D4721DDB424E2EF680A582048F3ADCC9E6F0EC1C05B84222036F",
        "expected_translation_policy_sha256":
        "6BD8E3ED58A8A7DA15091E0AAF05A663051F9B7FEB748B8DA770F2D0FB11DEA5",
        "expected_candidate_sha256":
        "E488D03EC33812718F083503EE7BA444FB4710B6318AD8F7AE0FA2A56D3EAF0D",
        "expected_combined_slice_candidate_sha256":
        "1366682CFB34C7D1FD84FA8711CE0B52898F3FB1243D3B44000B8829EC0EBB50",
        "expected_combined_changed_literal_count": 49,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
