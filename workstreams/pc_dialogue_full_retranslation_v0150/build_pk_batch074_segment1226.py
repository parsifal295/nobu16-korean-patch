#!/usr/bin/env python3
"""Build source-redacted PK B074 segment 1226 residual decisions."""

from pathlib import Path

from build_pk_batch074_common import make_config, run


SCRIPT = Path(__file__).resolve()
CONFIG = make_config(
    script=SCRIPT,
    segment=1226,
    queue_start=0,
    queue_stop=67,
    slice_first="8:567:0",
    slice_last="8:622:0",
    target_coordinates=(
        "8:590:0",
        "8:590:1",
        "8:606:0",
        "8:610:0",
        "8:614:0",
    ),
    translations={
        "8:590:0": "역시 「",
        "8:590:1": "」!\n",
        "8:606:0": "돌이켜 보니 이 땅에 머문 지도 어언 제",
        "8:610:0": "이곳을 다스린 지도 제",
        "8:614:0": "이 땅을 다스린 지도 제",
    },
    target_record_ids=(590, 606, 610, 614),
    expected_arity={
        590: 3,
        606: 2,
        610: 2,
        614: 2,
    },
    prefill_companion_coordinates=(
        "8:590:2",
        "8:606:1",
        "8:610:1",
        "8:614:1",
    ),
    prefill_companion_donor={
        "8:590:2": "8:578:2",
        "8:606:1": "8:594:1",
        "8:610:1": "8:598:1",
        "8:614:1": "8:602:1",
    },
    semantic_base_context={
        590: ("8:578:0", "8:578:1", "8:578:2"),
        606: ("8:594:0", "8:594:1"),
        610: ("8:598:0", "8:598:1"),
        614: ("8:602:0", "8:602:1"),
    },
    expected_base_raw_matches={
        590: ((8, 578),),
        606: ((8, 594),),
        610: ((8, 598),),
        614: ((8, 602),),
    },
    expected_controls_by_record={
        590: ((8, 1), ()),
        606: ((), ("0232",)),
        610: ((), ("0232",)),
        614: ((), ("0232",)),
    },
    source_call_roots=(1, 8),
    boundary_record_keys=tuple(
        (8, record_id)
        for record_id in (
            566, 567, 577, 578, 579, 589, 590, 591,
            593, 594, 595, 597, 598, 599, 601, 602, 603,
            605, 606, 607, 609, 610, 611, 613, 614, 615,
            621, 622, 623,
        )
    ),
    speaker_style=(
        (590, "loyal_retainer_recognition_gratitude"),
        (606, "long_tenure_reflection_polite"),
        (610, "long_tenure_handover_decision"),
        (614, "long_tenure_attachment_to_people"),
    ),
    terminology_policy=(
        ("governance tenure", "다스린 지도"),
        ("long passage of time", "어언"),
        ("land", "이 땅/이곳"),
        ("people", "백성"),
        ("dynamic person or lord", "「」"),
        ("year counter", "제…년"),
    ),
    basis=(
        "pristine PK Japanese is authoritative and all available PK English, "
        "Simplified Chinese and Traditional Chinese context was reviewed; "
        "four raw-identical completed Base records supply manually selected "
        "semantic wording only, while PK runtime and VM state are never "
        "inherited; five residuals and four exact-prefill companions form four "
        "complete records; tenure, governance, people, honorific register, "
        "dynamic persons, year tokens, calls, protected whitespace, gaps, "
        "boundaries, two-run reproduction, tamper rejection, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    pins={
        "expected_queue_universe_sha256":
        "AD7463BFB5BF319B21F2E4B813FD175CEF956C86397E29689D48156AD1726FC7",
        "expected_queue_slice_sha256":
        "A887EF25C6028D4249564B83408089F4A0DF717803597F2D973DE6EC0F404551",
        "expected_prefilled_coordinate_sha256":
        "4902BE6009E3B0EBAB4BFD866AC07EA7161DBF60A0D330111D6D16973687B0BD",
        "expected_prefill_slice_context_sha256":
        "567767E13BE92201F5936E3F8E4F617488A50ED985308E2605337AF267D41C5B",
        "expected_target_coordinate_sha256":
        "CAF6E20464629233E7A7DFD1C8EA9BB43579F754C4647A3C07E05FADC8539B75",
        "expected_source_target_sha256":
        "072DE8F04B1377DB5994489693D125756FF1357663298660CBAC39C5A6003B15",
        "expected_current_target_sha256":
        "DC7333B409DFD634AEECE95E2A177C6F0A7637654F992BA3FF5F0002016C14F1",
        "expected_context_corpus_sha256":
        "E7F745C4E880B90BF50A1B66340CFB2DF04CCF441ECDDDB6EB033BD08BC4147F",
        "expected_gap_contract_sha256":
        "52C553E4891B79F7C3D749DC1466E69312E35FE80D27C6FD1B4C8A893FD0AB78",
        "expected_boundary_sha256":
        "6ABCE73B7A2212FB34E9CC8273AE4FED2C551E2488DA0DC55DE5CF7EA6CD9AFE",
        "expected_runtime_control_sha256":
        "762A4471D393FD8C285418794BE59D07C47B8C1300842BEBA4DD6D167EBC90B4",
        "expected_base_search_sha256":
        "1839E5209CF7BCB8615B2315EC85E311D2F9DDA3B61B5776D7275905E0FEC405",
        "expected_complete_assembly_sha256":
        "E0B9DEE8ABC4C797DC2B767A82C7E94D4315F3750312095AADC8A5804488CA78",
        "expected_call_graph_sha256":
        "B7FEFC0E69503FD7AC6DCB557D7714DA2EC745739A13C3E806D541BE9BF5BC14",
        "expected_speaker_style_sha256":
        "171B161E0877734997E097C676BCEFF4D36A239C9EB6D49A0D9ABE59CFCC0BD0",
        "expected_terminology_policy_sha256":
        "1B3E69774EF86FD1F674918B9C5155390679BC180885C7C27FC3638682017402",
        "expected_translation_policy_sha256":
        "C4406E723FED20D1A69EF72DFF85E47BA4A7341A192D48E328A71AD8CAF72F7B",
        "expected_candidate_sha256":
        "66D8ABF190161BA0858AD46406A9ECCC375E68C50260990B4FD5197EFA206894",
        "expected_combined_slice_candidate_sha256":
        "6215956E0049D8074855719C250BBA2BF775F11F6218C527C8C8634BE4EBE41F",
        "expected_combined_changed_literal_count": 65,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
