#!/usr/bin/env python3
"""Build source-redacted PK B079 segment 1241 residual decisions."""

from pathlib import Path

from build_pk_batch079_common import make_config, run


SCRIPT = Path(__file__).resolve()
TARGET_RECORD_IDS = (
    1234, 1236, 1237, 1238, 1239, 1240,
    1241, 1243, 1244, 1245, 1246, 368,
)
CONFIG = make_config(
    script=SCRIPT,
    segment=1241,
    queue_start=0,
    queue_stop=67,
    slice_first="8:1233:0",
    slice_last="9:396:0",
    target_coordinates=(
        "8:1234:0",
        "8:1234:1",
        "8:1234:2",
        "8:1234:3",
        "8:1236:0",
        "8:1236:1",
        "8:1236:2",
        "8:1237:1",
        "8:1238:2",
        "8:1239:2",
        "8:1239:3",
        "8:1240:0",
        "8:1240:1",
        "8:1241:0",
        "8:1243:0",
        "8:1244:2",
        "8:1245:1",
        "8:1246:0",
        "9:368:1",
    ),
    translations={
        "8:1234:0": "대관·",
        "8:1234:1": "을(를)",
        "8:1234:2": "에서",
        "8:1234:3": "(으)로 이동",
        "8:1236:0": "그렇",
        "8:1236:1": "…\n유감",
        "8:1236:2": "지만, 어쩔 수",
        "8:1237:1": "지만\n",
        "8:1238:2": "확인해 주",
        "8:1239:2": "지만\n",
        "8:1239:3": "습니까?",
        "8:1240:0": "알겠",
        "8:1240:1": "\n또한",
        "8:1241:0": "알겠",
        "8:1243:0": "의 성하 방침 해제",
        "8:1244:2": "(으)로",
        "8:1245:1": "의 성하 방침을 해제",
        "8:1246:0": (
            "아직 영지를 받지 못한 고위 가신에게\n"
            "이러한 처분을 내려도 되겠습니까?"
        ),
        "9:368:1": "이다!",
    },
    target_record_ids=TARGET_RECORD_IDS,
    target_record_blocks={
        **{record_id: 8 for record_id in TARGET_RECORD_IDS[:-1]},
        368: 9,
    },
    expected_arity={
        1234: 4,
        1236: 3,
        1237: 3,
        1238: 3,
        1239: 4,
        1240: 3,
        1241: 1,
        1243: 1,
        1244: 3,
        1245: 2,
        1246: 1,
        368: 2,
    },
    prefill_companion_coordinates=(
        "8:1237:0",
        "8:1237:2",
        "8:1238:0",
        "8:1239:0",
        "8:1239:1",
        "8:1240:2",
        "8:1244:0",
        "8:1244:1",
        "8:1245:0",
        "9:368:0",
    ),
    prefill_companion_donor={
        "8:1237:0": "8:1197:0",
        "8:1237:2": "8:1197:2",
        "8:1238:0": "8:1198:0",
        "8:1239:0": "8:1199:0",
        "8:1239:1": "8:1199:1",
        "8:1240:2": "8:1200:2",
        "8:1244:0": "8:1204:0",
        "8:1244:1": "8:1204:1",
        "8:1245:0": "8:1205:0",
        "9:368:0": "9:324:0",
    },
    hidden_current_companion_coordinates=("8:1238:1",),
    semantic_base_context={
        1234: tuple(f"8:1194:{literal_id}" for literal_id in range(4)),
        1236: tuple(f"8:1196:{literal_id}" for literal_id in range(3)),
        1237: tuple(f"8:1197:{literal_id}" for literal_id in range(3)),
        1238: ("8:1198:0", "8:1198:1"),
        1239: tuple(f"8:1199:{literal_id}" for literal_id in range(4)),
        1240: tuple(f"8:1200:{literal_id}" for literal_id in range(3)),
        1241: ("8:1201:0",),
        1243: ("8:1203:0",),
        1244: tuple(f"8:1204:{literal_id}" for literal_id in range(3)),
        1245: ("8:1205:0", "8:1205:1"),
        1246: ("13:239:0", "13:383:0", "6:501:0"),
        368: ("9:324:0", "9:324:1"),
    },
    expected_base_raw_matches={
        1234: ((8, 1194),),
        1236: (),
        1237: (),
        1238: (),
        1239: (),
        1240: (),
        1241: (),
        1243: ((8, 1203),),
        1244: ((8, 1204),),
        1245: ((8, 1205),),
        1246: (),
        368: ((9, 324),),
    },
    expected_base_literal_matches={
        1234: ((8, 1194),),
        1236: ((8, 1196),),
        1237: ((8, 1197),),
        1238: (),
        1239: ((8, 1199),),
        1240: ((8, 1200),),
        1241: ((8, 1201),),
        1243: ((8, 1203),),
        1244: ((8, 1204),),
        1245: ((8, 1205),),
        1246: (),
        368: ((9, 324),),
    },
    expected_base_masked_matches={
        1234: ((8, 1194),),
        1236: ((8, 1196),),
        1237: ((8, 1197),),
        1238: (),
        1239: ((8, 1199),),
        1240: ((8, 1200),),
        1241: ((8, 1201),),
        1243: ((8, 1203),),
        1244: ((8, 1204),),
        1245: ((8, 1205),),
        1246: (),
        368: ((9, 324),),
    },
    expected_controls_by_record={
        1234: ((), ("024633", "029632", "029732")),
        1236: ((268, 568, 742), ()),
        1237: ((1096, 1168), ()),
        1238: ((538, 1174, 412), ("02463F",)),
        1239: ((1, 550, 226, 1048, 610), ()),
        1240: ((538, 1, 958), ()),
        1241: ((538,), ()),
        1243: ((), ("026432",)),
        1244: ((), ("026432", "023D")),
        1245: ((), ("026432",)),
        1246: ((), ()),
        368: ((7,), ()),
    },
    source_call_roots=(
        1, 7, 226, 268, 412, 538, 550, 568, 610,
        742, 958, 1048, 1096, 1168, 1174,
    ),
    boundary_record_keys=(
        tuple((8, record_id) for record_id in range(1232, 1248))
        + tuple((9, record_id) for record_id in range(367, 398))
    ),
    speaker_style=(
        (1234, "governor_transfer_command_ui"),
        (1236, "reluctant_policy_response_fragment"),
        (1237, "formal_policy_objection_fragment"),
        (1238, "development_completion_report_fragment"),
        (1239, "formal_delegation_report_fragment"),
        (1240, "formal_castle_policy_reassignment_fragment"),
        (1241, "formal_acknowledgement_fragment"),
        (1243, "castle_policy_release_ui"),
        (1244, "castle_policy_change_reason_ui"),
        (1245, "castle_policy_release_reason_ui"),
        (1246, "formal_high_rank_retainer_discipline_warning"),
        (368, "battle_dominance_declaration_fragment"),
    ),
    terminology_policy=(
        ("governor", "대관"),
        ("castle policy", "성하 방침"),
        ("territory grant", "영지"),
        ("high-rank retainer", "고위 가신"),
        ("disciplinary measure", "처분"),
        ("development completion", "개발 완료"),
        ("battle dominance", "싸움을 지배하다"),
        ("dynamic particles", "을(를)·이(가)·(으)로"),
    ),
    basis=(
        "pristine PK JP is authoritative and complete EN, SC and TC context "
        "was manually reviewed; completed Base records provide semantic, "
        "terminology and register references only, while the PK-only high-rank "
        "retainer warning is aligned with completed Base rank, landholding and "
        "discipline wording; all twelve complete records preserve historically "
        "appropriate governor, territory and retainer terminology, speaker "
        "register, dynamic particles, one hidden newline, inline tokens, calls, "
        "protected whitespace, gaps and block-eight to block-nine boundaries; "
        "two-run reproduction, tamper rejection, mutual neighbors, reverse "
        "overlays, outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=15,
    pins={
        "expected_queue_universe_sha256":
        "BE5A0E8B4C4FB397A096B8EDBA465B2CDFA0AB180AD5BF66EE0743C15693F2A2",
        "expected_queue_slice_sha256":
        "79A618251F7939CD98A2C7BAA643B1164D7F975D1B6437B210398C7A5C2BA814",
        "expected_prefilled_coordinate_sha256":
        "9C92814ED18B9884BA634E37155BE2B609A240EEC9B46859851CDC5983FA885A",
        "expected_prefill_slice_context_sha256":
        "B307BA8539A3F753CE5FB3992B89BD9A52C135C1193C11BA4AC97B660D83298F",
        "expected_target_coordinate_sha256":
        "C8A59113D22026D417D4DD44D94F23F864B6793991ADF3CECB04CCB5AE1C8C2A",
        "expected_source_target_sha256":
        "2A3AC2C4E80556DAF64D14CF42561ED3231CEE90756AD4CEA65D96C84DA29C2E",
        "expected_current_target_sha256":
        "FF90DB85E21FB0010C08813A264E58A326D73FA070E70626DEA6761E6F5E336D",
        "expected_context_corpus_sha256":
        "6BC0EDB140EBB450CBC2BCD06C8E80405AA66981052E4521B38197A643291A60",
        "expected_gap_contract_sha256":
        "4B5FB26A5DC3E937193B2D6A4BB9943A3757CC18CC32AB91DEEBCBC9C78A9275",
        "expected_boundary_sha256":
        "B6B3F49A72C100A3110CB257E787F4383470CD9A146F8512A931AF83CE036546",
        "expected_runtime_control_sha256":
        "4450788CFED4DD8A91D9A5EB574E9A7EBC456E5E8952F7B1692D49A590F958A6",
        "expected_base_search_sha256":
        "BDDAFBF507930E7B01D03121CEDF791AB34A5A5C3F80B54EDE63403CE409EC43",
        "expected_complete_assembly_sha256":
        "74AE21B7C8F30A7B49EE688795D4704407DA8BE9DB6F172D931682FFB4523AE0",
        "expected_call_graph_sha256":
        "86E3FC01D38E63DCC6DB3940FCC2F9795A2F212036E0EBFE2A984462CDA88FD3",
        "expected_speaker_style_sha256":
        "909BE39E703D947D1CCCDC1591B7010D19FABFF377B18F203B189B35D414F052",
        "expected_terminology_policy_sha256":
        "29C9C647544CD221752AF29F5E607BAA77A5CADAE5BDE1D8DA4E848E0F4B1F21",
        "expected_translation_policy_sha256":
        "C0D89FCB90569668A1C487FC321E61C13E8066C95D602CB22B78DCF56C23625F",
        "expected_candidate_sha256":
        "E69D48EF5D12EE9355C4B5E0A711C083D84D7315D45EC0AFF6D8B32634974A50",
        "expected_combined_slice_candidate_sha256":
        "B5E108E4251ADD38EE2350D74E87D77F7D06D8815133DEA4ED83F40989604A39",
        "expected_combined_changed_literal_count": 57,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
