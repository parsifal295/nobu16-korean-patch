#!/usr/bin/env python3
"""Build source-redacted PK B087 segment 1267 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1940, 1943, 1944, 1945, 1946, 1952, 1957, 1959, 1983, 1986,
)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1267,
    queue_start=134,
    queue_stop=200,
    slice_first="9:1936:0",
    slice_last="9:1995:0",
    target_coordinates=(
        "9:1940:0",
        "9:1943:0",
        "9:1944:0",
        "9:1945:0",
        "9:1946:0",
        "9:1952:0",
        "9:1957:0",
        "9:1959:0",
        "9:1983:0",
        "9:1986:0",
        "9:1986:1",
    ),
    translations={
        "9:1940:0": "끄으윽……",
        "9:1943:0": "끄으윽……",
        "9:1944:0": "끄으윽……",
        "9:1945:0": "끄으윽……",
        "9:1946:0": "끄으윽……",
        "9:1952:0": "이놈……!",
        "9:1957:0": "이럴 수가……\n",
        "9:1959:0": "그럴 수가……!\n",
        "9:1983:0": "설마―",
        "9:1986:0": "!?\n설마―",
        "9:1986:1": "마저!?",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        1940: 1,
        1943: 1,
        1944: 1,
        1945: 1,
        1946: 1,
        1952: 1,
        1957: 2,
        1959: 2,
        1983: 2,
        1986: 2,
    },
    prefill_companion_coordinates=(
        "9:1957:1",
        "9:1959:1",
        "9:1983:1",
    ),
    prefill_companion_donor={
        "9:1957:1": "9:1883:1",
        "9:1959:1": "9:1885:1",
        "9:1983:1": "9:1909:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        1940: ("9:1866:0",),
        1943: ("9:1866:0",),
        1944: ("9:1866:0",),
        1945: ("9:1866:0",),
        1946: ("9:1866:0",),
        1952: ("9:1878:0",),
        1957: ("9:1883:0", "9:1883:1"),
        1959: ("9:1885:0", "9:1885:1"),
        1983: ("9:1909:0", "9:1909:1"),
        1986: ("9:1912:0", "9:1912:1"),
    },
    expected_base_raw_matches={
        1940: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1943: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1944: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1945: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1946: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1952: ((9, 1878),),
        1957: ((9, 1883),),
        1959: ((9, 1885),),
        1983: ((9, 1909),),
        1986: ((9, 1912),),
    },
    expected_base_literal_matches={
        1940: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1943: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1944: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1945: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1946: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1952: ((9, 1878),),
        1957: ((9, 1883),),
        1959: ((9, 1885),),
        1983: ((9, 1909),),
        1986: ((9, 1912),),
    },
    expected_base_masked_matches={
        1940: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1943: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1944: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1945: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1946: ((9, 1866), (9, 1869), (9, 1870), (9, 1871), (9, 1872)),
        1952: ((9, 1878),),
        1957: ((9, 1883),),
        1959: ((9, 1885),),
        1983: ((9, 1909),),
        1986: ((9, 1912),),
    },
    expected_controls_by_record={
        1940: ((), ()),
        1943: ((), ()),
        1944: ((), ()),
        1945: ((), ()),
        1946: ((), ()),
        1952: ((), ()),
        1957: ((17,), ()),
        1959: ((17,), ()),
        1983: ((29,), ()),
        1986: ((29,), ("024833",)),
    },
    source_call_roots=(17, 29),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(1865, 1997)
    ),
    speaker_style=(
        (1940, "frustrated_defeat_groan"),
        (1943, "frustrated_defeat_groan"),
        (1944, "frustrated_defeat_groan"),
        (1945, "frustrated_defeat_groan"),
        (1946, "frustrated_defeat_groan"),
        (1952, "angry_defeat_exclamation"),
        (1957, "disbelieving_dynamic_general_defeat_reaction"),
        (1959, "shocked_dynamic_renowned_general_reaction"),
        (1983, "astonished_dynamic_enemy_defeat_praise"),
        (1986, "astonished_dynamic_enemy_defeat_exclamation"),
    ),
    terminology_policy=(
        ("defeat groan", "끄으윽"),
        ("angry address", "이놈"),
        ("general", "장수"),
        ("dynamic inclusive particle", "마저"),
        ("defeat", "패하다·쓰러뜨리다"),
        ("project ellipsis", "……"),
        ("project em dash", "―"),
        ("ASCII exclamation and question", "!·?"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "context was manually reviewed; every target has one or more exact "
        "completed Base records supplying semantic, terminology, punctuation "
        "and speaker-register evidence only, with no Base runtime or VM state "
        "inherited; repeated defeat groans deliberately share one approved "
        "rendering, while the dynamic general and enemy-defeat reactions "
        "preserve inclusive particles, names, inline 024833, calls, protected "
        "newlines, gaps and all complete-record companions; all pins, two-run "
        "reproduction, tamper rejection, mutual neighbors, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256":
        "D8911A720BB76E5F8078D1609E2402F49B21AF37413EA43E6745510025A3D940",
        "expected_queue_slice_sha256":
        "D543972B13B377E7DB4D79AD3004C235319E351DD2CC8EAE3AEA7D83D4327F18",
        "expected_prefilled_coordinate_sha256":
        "290920EA4F4FB352A237BAB80B286723DA7FCC52792B8F0A6576A923C3709683",
        "expected_prefill_slice_context_sha256":
        "7BD4F4F96DE9101546F88CE08BB49DB4793EAFDB473F38C68ADBE944788DE74E",
        "expected_target_coordinate_sha256":
        "C194537A606C79556C8CB4E7FA03BBE9DEC6F4BBFCB2C4266CD3EF1240CFB3FB",
        "expected_source_target_sha256":
        "5DC3B0E9CD1F3DA2FF2ADDD9298E800B03958E00BFC39BD07280F9776B63CCC2",
        "expected_current_target_sha256":
        "4CCF64F5FDA2B00391669500FA02B31292B1B187EC6492D795B478E783F09DCD",
        "expected_context_corpus_sha256":
        "E47ECB529E51331A1CD7011A444CD17A01793B7483F47970BC6C78162F8881E6",
        "expected_gap_contract_sha256":
        "9CE56AE82E10862CF03277178D9923A6F18AF113862BE9D82840A80A46793E7C",
        "expected_boundary_sha256":
        "9AF729CD0E7385ED972DA1DAD21FCD0424DFBE773B829B6676FB688B69916954",
        "expected_runtime_control_sha256":
        "CA7BC8947BA07922F8472A24B686DC4E4A737BE33C308410B8612498AD687153",
        "expected_base_search_sha256":
        "66DA03CFCFE9A0614FB52CCCE5FE897A507CCA6CB601843AFBF07578B2079CA8",
        "expected_complete_assembly_sha256":
        "6826246FEADD10A8EE598C4EABB7B0D2E24B30402BBCDCA36C0D471DADDF5354",
        "expected_call_graph_sha256":
        "D68942668EDB6AEFC2B408194FD38F1A5CC2C0F8CF9C36F0B3E416775AF451E0",
        "expected_speaker_style_sha256":
        "AD4B7258D09F8AA4555DE64B92EE26EAB1F04F1DAEEFB7EBA6FEFEBDB5E188CC",
        "expected_terminology_policy_sha256":
        "ED7AD64589A5CE8E8E9BF273E9E581DFDF2273089274DE387EB7BF40875F152C",
        "expected_translation_policy_sha256":
        "637C5D27722F04DCAB4B3AE234FE176D672177F36D6ED8E2F7F238E7B0C4FF9C",
        "expected_candidate_sha256":
        "F08CDCABE342CACD1144633352383080EEBFA116B638A16419FBC7DDE343FF8F",
        "expected_combined_slice_candidate_sha256":
        "88D6769C38D9179F3C4DC03B3DD2C39CC6B241C0D7A136E248C7CD64B07814F0",
        "expected_combined_changed_literal_count": 64,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B087_S1267",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B087_S1267.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B087_S{segment}.private.v1.jsonl"
        for segment in (1265, 1266)
    ),
    "queue_batch_id": "pk_msggame-B087",
    "queue_row_count": 179,
    "queue_visible_count": 200,
    "queue_first": "9:1817:0",
    "queue_last": "9:1995:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
