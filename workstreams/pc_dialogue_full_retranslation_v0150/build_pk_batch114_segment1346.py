#!/usr/bin/env python3
"""Build source-redacted PK B114 segment 1346 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    609,
    635,
    636,
    637,
    640,
    643,
    644,
)
TARGET_COORDINATES = (
    "15:609:0",
    "15:635:0",
    "15:636:0",
    "15:637:0",
    "15:640:0",
    "15:643:0",
    "15:643:1",
    "15:644:0",
)
TRANSLATIONS = {
    "15:609:0": "다시",
    "15:635:0": "·",
    "15:636:0": "·",
    "15:637:0": "·",
    "15:640:0": "이(가)",
    "15:643:0": "우리와 ",
    "15:643:1": (
        " 측은 이제\n"
        "운명을 함께하는 사이이옵니다\n"
        "속히 휘하에 들여야 할 듯하옵니다"
    ),
    "15:644:0": "우리 가문과",
}
EXPECTED_ARITY = {
    record_id: 2
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = (
    "15:609:1",
    "15:635:1",
    "15:636:1",
    "15:637:1",
    "15:640:1",
    "15:644:1",
)
PREFILL_COMPANION_DONOR = {
    "15:609:1": "15:602:1",
    "15:635:1": "15:628:1",
    "15:636:1": "15:629:1",
    "15:637:1": "15:630:1",
    "15:640:1": "15:633:1",
    "15:644:1": "15:637:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ()
BASE_CONTEXT_DONOR = {
    609: (15, 602),
    635: (15, 628),
    636: (15, 629),
    637: (15, 630),
    640: (15, 633),
    643: (15, 636),
    644: (15, 637),
}
EXACT_BASE_DONOR = {
    record_id: donor
    for record_id, donor in BASE_CONTEXT_DONOR.items()
    if record_id != 643
}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, donor in BASE_CONTEXT_DONOR.items()
}
EXPECTED_BASE_MATCHES = {
    record_id: (donor,)
    for record_id, donor in BASE_CONTEXT_DONOR.items()
}
EXPECTED_CONTROLS_BY_RECORD = {
    609: ((), ("028C32",)),
    635: ((), ("028C32",)),
    636: ((), ("028C32",)),
    637: ((), ("028C32",)),
    640: ((), ("024633", "028C32")),
    643: ((), ("028C32",)),
    644: ((), ("028C32",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1346,
    queue_start=0,
    queue_stop=67,
    slice_first="15:591:0",
    slice_last="15:644:0",
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
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(585, 651)
    ),
    speaker_style=(
        (609, "formal_completed_appeasement_report"),
        (635, "concise_vassalage_stage_status"),
        (636, "concise_vassalage_stage_status"),
        (637, "concise_vassalage_stage_status"),
        (640, "concise_failed_appeasement_report"),
        (643, "formal_courtly_subordination_proposal"),
        (644, "plain_strategic_recruitment_proposal"),
    ),
    terminology_policy=(
        ("appeasement or recruitment persuasion", "회유"),
        ("money and valuables", "금품"),
        ("battle", "전투"),
        ("vassalage stage", "종속 단계"),
        ("low stage", "낮음"),
        ("medium stage", "보통"),
        ("high stage", "높음"),
        ("highest stage", "최고"),
        ("shared fate", "운명을 함께하는 사이"),
        ("retainer command", "휘하"),
        ("our house", "우리 가문"),
        ("shared interests", "이해관계"),
        ("retainer", "가신"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B114 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record entry "
        "was reviewed as auxiliary context; six records reuse approved "
        "byte-identical Base Korean assemblies, while record 643 adapts the "
        "approved Base wording to preserve the PK dynamic group token's "
        "leading and trailing space contract; Base runtime and VM state are "
        "never inherited; appeasement, vassalage stages, shared fate, "
        "retainer command, house, shared interests and retainer terminology "
        "and the formal or plain proposal registers remain distinct; inline "
        "person, tribe and group tokens, gaps, protected outer whitespace, "
        "line counts, bullet glyphs, arrows, literal arity, terminators, all "
        "six same-record companions, all fifty-nine slice prefills, complete "
        "assemblies, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, optional neighbor decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=3,
    pins={
        "expected_queue_universe_sha256": (
            "9546FDEB560A7A0E6A75D7731A5614F817AEFBA97DE9F75154D76AD3643DD569"
        ),
        "expected_queue_slice_sha256": (
            "B3434B509DD14E670A72CF965B2468B0C3EA8C5DB8E4498E8D1F4B193935632C"
        ),
        "expected_prefilled_coordinate_sha256": (
            "E9FD0FBEF46F7C950A3BFE523CCB68F7207E8FC5EDAA8103B25FD2A48C939BEC"
        ),
        "expected_prefill_slice_context_sha256": (
            "C48A4FA1DB4189A468A6E715663293552BBD0C4DF46F014948F0276A203F938A"
        ),
        "expected_target_coordinate_sha256": (
            "6FC21F24DEE0680AD67E2F11D6CC1BB6212C72EF8D73DD0467598CBA63895B53"
        ),
        "expected_source_target_sha256": (
            "B5B9F38494ADB60B16CEE119F9711F680E23BD90B77036C3B614E5CF613F86A4"
        ),
        "expected_current_target_sha256": (
            "5DD5F1B8D7C560DCAA58D7FAABB94C5A0F73CD43B8CFD5FD742175B912DF7CDE"
        ),
        "expected_context_corpus_sha256": (
            "138F0B7C994002E05B1FB12D96F35E0EC2BC78CCCBC5230AC0E98C3750AEE912"
        ),
        "expected_gap_contract_sha256": (
            "8FDC00ACE43B37880EE92DF89D1B54423B8ADC95961920AE035AE38B908A0389"
        ),
        "expected_boundary_sha256": (
            "5813749783FD67F7FD838F63AB1C105916ABB945FE19C297BD33EAD625604E45"
        ),
        "expected_runtime_control_sha256": (
            "E1A33FCFD7338CA5BA98632E43E2F56ED7CB94D9B7EBCEE103DD0D78B8FF212A"
        ),
        "expected_base_search_sha256": (
            "85F23B30235D475C7DC7EE78E88B2BA03F340CA4EDBB3056D37CF5BD7A0F4A80"
        ),
        "expected_complete_assembly_sha256": (
            "8FDC173F165CE58E94A77A0B27013318D5ECBE78A06E46F1FC9C57A979089BA7"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "D9148B777FBEF8697457D5A8C9E1DECA1D53B0C7C95B720F5BB5BA5CCD1C8D1E"
        ),
        "expected_terminology_policy_sha256": (
            "77F92860CE5D1C38174B39890A4C226AB005A73A5DD4E0ACA019363EE13A726B"
        ),
        "expected_translation_policy_sha256": (
            "DBB969CE94249F7E736AEF964FFCE0E3519B61410ADF30919B265EB02646E5DD"
        ),
        "expected_candidate_sha256": (
            "CC961D1A308DF8D7AFA7CC5963E8041D9077C38A84A6AD4469CB5AF5A097AA98"
        ),
        "expected_combined_slice_candidate_sha256": (
            "798A26865545AD5621A3F8F6951E97B77C1A302211FA022114FF03E3F88581D4"
        ),
        "expected_combined_changed_literal_count": 56,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B114_S1346",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1346.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1347.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1348.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B114",
    "queue_row_count": 140,
    "queue_visible_count": 200,
    "queue_first": "15:591:0",
    "queue_last": "15:730:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
