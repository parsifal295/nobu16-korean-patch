#!/usr/bin/env python3
"""Build source-redacted PK B087 segment 1265 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1828, 1829, 1830, 1848, 1851, 1853, 1857, 1861, 1869,
)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1265,
    queue_start=0,
    queue_stop=67,
    slice_first="9:1817:0",
    slice_last="9:1871:0",
    target_coordinates=(
        "9:1828:0",
        "9:1828:1",
        "9:1829:0",
        "9:1829:1",
        "9:1830:0",
        "9:1830:1",
        "9:1848:0",
        "9:1848:1",
        "9:1851:0",
        "9:1851:1",
        "9:1853:0",
        "9:1857:0",
        "9:1861:1",
        "9:1869:0",
    ),
    translations={
        "9:1828:0": "\n무운을 기원",
        "9:1828:1": "……",
        "9:1829:0": "\n꼭 무사",
        "9:1829:1": "하기를!",
        "9:1830:0": "무사하기를 기원",
        "9:1830:1": "……",
        "9:1848:0": "말도 안 돼……\n",
        "9:1848:1": "이(가)……!",
        "9:1851:0": "그럴 수가……!?\n",
        "9:1851:1": "이(가)……",
        "9:1853:0": "설마―",
        "9:1857:0": "의 한은……\n",
        "9:1861:1": "이(가) 반드시 갚으리라",
        "9:1869:0": "이 몸―",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={record_id: 2 for record_id in TARGET_RECORD_IDS},
    prefill_companion_coordinates=(
        "9:1853:1",
        "9:1857:1",
        "9:1861:0",
        "9:1869:1",
    ),
    prefill_companion_donor={
        "9:1853:1": "9:1779:1",
        "9:1857:1": "9:1783:1",
        "9:1861:0": "9:1787:0",
        "9:1869:1": "9:1795:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        1828: ("9:1754:0", "9:862:0", "9:2424:0"),
        1829: ("9:1755:0", "9:1849:0"),
        1830: ("9:1756:0", "9:741:0"),
        1848: ("9:1774:0", "9:1774:1"),
        1851: ("9:1777:0", "9:1777:1"),
        1853: ("9:1779:0", "9:1779:1"),
        1857: ("9:1783:0", "9:1783:1"),
        1861: ("9:1787:0", "9:1787:1"),
        1869: ("9:1795:0", "9:1795:1"),
    },
    expected_base_raw_matches={
        1828: (),
        1829: (),
        1830: (),
        1848: ((9, 1774),),
        1851: ((9, 1777),),
        1853: ((9, 1779),),
        1857: ((9, 1783),),
        1861: ((9, 1787),),
        1869: ((9, 1795),),
    },
    expected_base_literal_matches={
        1828: (),
        1829: (),
        1830: (),
        1848: ((9, 1774),),
        1851: ((9, 1777),),
        1853: ((9, 1779),),
        1857: ((9, 1783),),
        1861: ((9, 1787),),
        1869: ((9, 1795),),
    },
    expected_base_masked_matches={
        1828: (),
        1829: (),
        1830: (),
        1848: ((9, 1774),),
        1851: ((9, 1777),),
        1853: ((9, 1779),),
        1857: ((9, 1783),),
        1861: ((9, 1787),),
        1869: ((9, 1795),),
    },
    expected_controls_by_record={
        1828: ((29, 1090), ()),
        1829: ((29, 1174), ()),
        1830: ((1090,), ()),
        1848: ((29,), ()),
        1851: ((29,), ()),
        1853: ((29,), ()),
        1857: ((29, 1), ()),
        1861: ((29, 4), ()),
        1869: ((4,), ()),
    },
    source_call_roots=(1, 4, 29, 1090, 1174),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(1753, 1873)
    ),
    speaker_style=(
        (1828, "dynamic_warrior_fortune_prayer"),
        (1829, "earnest_dynamic_safety_wish"),
        (1830, "solemn_register_sensitive_safety_prayer"),
        (1848, "stunned_dynamic_death_reaction"),
        (1851, "disbelieving_dynamic_death_reaction"),
        (1853, "grieving_dynamic_death_reaction"),
        (1857, "resolute_dynamic_vengeance_vow"),
        (1861, "solemn_dynamic_vengeance_oath"),
        (1869, "defiant_first_person_retribution_vow"),
    ),
    terminology_policy=(
        ("military fortune", "무운"),
        ("pray or wish", "기원하다"),
        ("safety wish", "무사하기를"),
        ("dynamic subject particle", "이(가)"),
        ("grievance", "한"),
        ("avenge", "갚다"),
        ("historic first person", "이 몸"),
        ("project ellipsis", "……"),
        ("project em dash", "―"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "context was manually reviewed; six exact completed Base records and "
        "three related completed Base prayer records supply semantic, "
        "terminology, punctuation and speaker-register evidence only, with no "
        "Base runtime or VM state inherited; the PK-only fortune and safety "
        "prayers were rebuilt around terminal 1090's 합니다/한다 register "
        "matrix and Korean-zero honorific terminal 1174 so every runtime "
        "assembly remains grammatical; all nine complete records preserve "
        "dynamic names, subject particles, historical 무운 and 이 몸 wording, "
        "calls, protected newlines, gaps and same-record prefills; all pins, "
        "two-run reproduction, tamper rejection, mutual neighbors, reverse "
        "overlays, outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=14,
    pins={
        "expected_queue_universe_sha256":
        "D8911A720BB76E5F8078D1609E2402F49B21AF37413EA43E6745510025A3D940",
        "expected_queue_slice_sha256":
        "EE91B42624B6DD27F32256E4C239FF3EC7235F9F54E58B8F6AB4E483E58EBE5A",
        "expected_prefilled_coordinate_sha256":
        "C61ED70806CF4FD340E16BFDE8932669CF4EA4D169038F2B687E590F6E04641E",
        "expected_prefill_slice_context_sha256":
        "A22DBE5CBEC0ED8A9EB05A4139EBA0C71FA48D8B4EAD0FEF17C032916EDDCE2F",
        "expected_target_coordinate_sha256":
        "0724B3F45833ACBC658DB272B46C79E62880387E53251419BD4F81E1823FD732",
        "expected_source_target_sha256":
        "65BC74B127A362382B6C68ED36BC35196D21C73CE9A4F8E2A413ACF98AA9649E",
        "expected_current_target_sha256":
        "CA9B5A78706FD457CD53D369933A8CFEA541F12EF8D22010F19D38DB77B287EC",
        "expected_context_corpus_sha256":
        "E47ECB529E51331A1CD7011A444CD17A01793B7483F47970BC6C78162F8881E6",
        "expected_gap_contract_sha256":
        "568C63B1578B584D284E5EC6D9B5572166B151834CEF133AA71E293C38BD8574",
        "expected_boundary_sha256":
        "BB19BE61AEE9DBBC541CE73CBAEB1678FCEED5BC312CF18093DF115F6ABF3F63",
        "expected_runtime_control_sha256":
        "04D034FD6E28350FB377D9DFAC28B3DAE4E5A49173DE3C976898E7CAC5AC596C",
        "expected_base_search_sha256":
        "9FCE229D10637C82A585C82B5501BE7340D44E725796C6BAB54999BD702F313D",
        "expected_complete_assembly_sha256":
        "2C4E5203B240728513B44AB0B66B363B33C3A9B954EC83C9C7436CCB825F1466",
        "expected_call_graph_sha256":
        "1C4D7667B4A355A78C982F6D4CCC873F783CE96D3CEBE17A47587BF949B67C8B",
        "expected_speaker_style_sha256":
        "9DCFF920525543E336186B522333C9055BC4200E4923030864FCA1D129E9A4E1",
        "expected_terminology_policy_sha256":
        "B7B8A60C0FFB09068C8D5BF5661630C460F46C91E17EB06D03E4B0BD59158CBD",
        "expected_translation_policy_sha256":
        "900823E0BE401763B4301629CA218F002850C6F2F27B7F2046F2651626A60207",
        "expected_candidate_sha256":
        "3AAA3834FBA6E404B9DB27D3CA36281F48E5E713859EF81551181D010035865C",
        "expected_combined_slice_candidate_sha256":
        "46CECA91396554A20007C21E336C0A176A85C4866DF5845FE7410A2BCBB7BC23",
        "expected_combined_changed_literal_count": 65,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B087_S1265",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B087_S1265.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B087_S{segment}.private.v1.jsonl"
        for segment in (1266, 1267)
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
