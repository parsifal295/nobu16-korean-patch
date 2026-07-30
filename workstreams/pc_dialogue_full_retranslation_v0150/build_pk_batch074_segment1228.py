#!/usr/bin/env python3
"""Build source-redacted PK B074 segment 1228 residual decisions."""

from pathlib import Path

from build_pk_batch074_common import make_config, run


SCRIPT = Path(__file__).resolve()
CONFIG = make_config(
    script=SCRIPT,
    segment=1228,
    queue_start=134,
    queue_stop=200,
    slice_first="8:683:0",
    slice_last="8:742:0",
    target_coordinates=("8:696:0",),
    translations={
        "8:696:0": "의 가신:",
    },
    target_record_ids=(696,),
    expected_arity={696: 2},
    prefill_companion_coordinates=("8:696:1",),
    prefill_companion_donor={
        "8:696:1": "8:684:1",
    },
    semantic_base_context={
        696: ("8:684:0", "8:684:1"),
    },
    expected_base_raw_matches={
        696: ((8, 684),),
    },
    expected_controls_by_record={
        696: ((), ("025032", "0232")),
    },
    source_call_roots=(),
    boundary_record_keys=tuple(
        (8, record_id)
        for record_id in (
            682, 683, 684, 685, 695, 696, 697, 741, 742, 743,
        )
    ),
    speaker_style=((696, "retainer_promotion_status_notice"),),
    terminology_policy=(
        ("retainer", "가신"),
        ("promotion", "승진"),
        ("count", "명"),
        ("dynamic clan or lord", "runtime token"),
    ),
    basis=(
        "pristine PK Japanese is authoritative and complete PK English, "
        "Simplified Chinese and Traditional Chinese context was manually "
        "reviewed; one raw-identical completed Base record supplies manually "
        "selected semantic wording only, while PK runtime and VM state are "
        "never inherited; one residual and one exact-prefill companion form a "
        "complete promotion notice; retainer and promotion terminology, "
        "dynamic clan and count tokens, punctuation, gaps, boundaries, "
        "two-run reproduction, tamper rejection, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    pins={
        "expected_queue_universe_sha256":
        "AD7463BFB5BF319B21F2E4B813FD175CEF956C86397E29689D48156AD1726FC7",
        "expected_queue_slice_sha256":
        "9F6EDE8196B3D5D562AE01F5022D9422B4CD00B5326646457B86F2B4BD6BC104",
        "expected_prefilled_coordinate_sha256":
        "E6C84AB6749B0CBAD1BAE8391622F5ABE98BBFBE82D1E5C848541E3992382D25",
        "expected_prefill_slice_context_sha256":
        "15E212770C9436B03D336A9144C1B1EEB5FA928F3E892E733126F316D33BD77F",
        "expected_target_coordinate_sha256":
        "E78CCD162D9D4EF6760AE2CA691A7960FD48708CDD0A52CA9C0B2DD696007A3F",
        "expected_source_target_sha256":
        "8C30D79B1369F5F2923A9FB1537D125BFB7A76B80679963B47088E0D7C3CAACC",
        "expected_current_target_sha256":
        "D2D10613BCEC6C1BEC7B4D40A727CFDCB1AB2F678AF706BD1A7D6FC27D36898C",
        "expected_context_corpus_sha256":
        "E7F745C4E880B90BF50A1B66340CFB2DF04CCF441ECDDDB6EB033BD08BC4147F",
        "expected_gap_contract_sha256":
        "394B9F9FA8E5DB98CB5146218E6906D0CE3791ED45A521070B438E52B5AC9F89",
        "expected_boundary_sha256":
        "5A4D3FC38C1E44D1C86CECA7F4B165669EDDED2A7DCCA6BDEF18ED03047095B8",
        "expected_runtime_control_sha256":
        "15D63756484CA304FD881F68EC9FF8ABF5361355347390A1162904EAFCEB702D",
        "expected_base_search_sha256":
        "C96C9BE1FA5635BE2207CDFBDA95F4FC5F801613980A38422C98765B415C97C3",
        "expected_complete_assembly_sha256":
        "DBF84C75E7721075703DA269CF61D577C865BA8A5EDDE2201190E06DDF416EB8",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "402B8D793F1816CEC8C3EB332D26C29C79F7A1B6E33018A59892CC449801FB16",
        "expected_terminology_policy_sha256":
        "E7143C57B029A5A9988BEEB06FA58F8C1DDD22DB82F67F9F7E37BA123D4B9378",
        "expected_translation_policy_sha256":
        "CEE048FA2FDD5A9D8A0D4D6F825E91249B13BD14842231FA6E5AE3FD5755BD4C",
        "expected_candidate_sha256":
        "0364899A0FC034AB4929A73E8797147D3D5FE91D2627EB99DD23485E4B801E0D",
        "expected_combined_slice_candidate_sha256":
        "6BE75E1939C8BED6E3F1A55A7A876206FF05FED2CF2BB9E82510F11848DA0E46",
        "expected_combined_changed_literal_count": 58,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
