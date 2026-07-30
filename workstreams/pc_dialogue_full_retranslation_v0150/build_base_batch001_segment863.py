#!/usr/bin/env python3
"""Build Base authoring segment 863 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment821 as CORE


ENGINE = CORE.ENGINE
COMMON = CORE.COMMON
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S863.private.v1.jsonl"
SEGMENT = 863

REPAIR_BRISK = (
    "을(를) 단숨에 수복했다!\n"
    "어떠냐, 훼손되기 전보다\n"
    "더 견고하게 마무리됐지!"
)
REPAIR_RELIEF = (
    "의 수복을 마쳤소이다\n"
    "적이 공격해 오기 전에\n"
    "작업을 마쳐 한시름 놓이는구려"
)
REPAIR_DURABLE = (
    "을(를) 단숨에 수복했소이다\n"
    "이제 성의 내구는 충분하니\n"
    "어지간한 공격으로는 함락되지 않을 것이오"
)
REPAIR_HURRIED = (
    ", 서둘러 수복하였습니다\n"
    "그 상처 입은 모습이 거짓말처럼 말끔해졌습니다\n"
    "언제 싸움이 벌어져도 안심이겠군요"
)
REPAIR_GALLANT = (
    ", 단숨에 수복하였소이다\n"
    "보시옵소서, 이 성의 늠름한 모습을\n"
    "이로써 아직 한참은 싸울 수 있사옵니다"
)
REPAIR_RUMOR = (
    "의 수복을 단숨에 마쳤습니다\n"
    "이 성이 훼손되었다는 소문에 넘어가\n"
    "적이 쳐들어와도 도리어 무찔러 줄 수 있사옵니다"
)
REPAIR_ALWAYS_READY = (
    "을(를) 수복하였사옵니다\n"
    "성은 언제든 싸울 수 있어야 하옵기에"
)
REPAIR_RESTORED_VOCATIVE = (
    "수복하여 저 황폐했던 성이 벌써 본모습을 되찾았소이다\n",
    "여, 다시 한번 힘껏 싸워다오",
)
REPAIR_BATTLE_READY = (
    "을(를) 수복했습니다\n"
    "이제 언제 전투가 벌어져도 안심이군요"
)
REPAIR_THOUGHTS = (
    "수복이 완료되었다\n"
    "작업에 힘쓴 이들의 마음이 깃들었으니\n"
    "어떤 공격도 견뎌 주리라"
)
REPAIR_FEMININE = (
    "을(를) 수복하였사옵니다\n"
    "이제 언제 공격받더라도\n"
    "근심할 것 없사옵니다"
)
REPAIR_SLEEP = (
    "을(를) 수복하였소이다\n"
    "이로써 내구는 충분할 것이오\n"
    "이제 안심하고 잠들 수 있겠구려!"
)

RAW_TRANSLATIONS: dict[str, str] = {
    "15:1061:0": "의 내구를",
    "15:1061:1": "회복(",
    "15:1061:2": "→",
    "15:1061:3": ")",
    "15:1062:0": REPAIR_BRISK,
    "15:1063:0": REPAIR_RELIEF,
    "15:1064:0": REPAIR_DURABLE,
    "15:1065:0": REPAIR_HURRIED,
    "15:1066:0": REPAIR_GALLANT,
    "15:1067:0": REPAIR_RUMOR,
    "15:1068:0": REPAIR_ALWAYS_READY,
    "15:1069:0": REPAIR_RESTORED_VOCATIVE[0],
    "15:1069:1": REPAIR_RESTORED_VOCATIVE[1],
    "15:1070:0": REPAIR_BATTLE_READY,
    "15:1071:0": REPAIR_THOUGHTS,
    "15:1072:0": REPAIR_FEMININE,
    "15:1073:0": REPAIR_SLEEP,
    "15:1074:0": REPAIR_BRISK,
    "15:1075:0": REPAIR_RELIEF,
    "15:1076:0": REPAIR_DURABLE,
    "15:1077:0": REPAIR_HURRIED,
}
RECORD_ARITIES = {
    1061: 4,
    **{record_id: 1 for record_id in range(1062, 1069)},
    1069: 2,
    **{record_id: 1 for record_id in range(1070, 1078)},
}
EXPECTED_JP = {
    1061: ("の耐久を", "回復(", "→", ")"),
    1062: (
        "を一気に修復したぞ！\n"
        "どうだ、傷つく前よりも\n"
        "頑丈そうに仕上がっただろ！",
    ),
    1063: (
        "の修復、完了いたした\n"
        "敵に攻め込まれる前に\n"
        "作業が済んで一安心ですな",
    ),
    1064: (
        "を一気に修復しましたぞ\n"
        "これにて城の耐久は十分\n"
        "生半可な攻めでは落ちますまい",
    ),
    1065: (
        "、急ぎ修復いたしました\n"
        "あの傷ついた姿が嘘のように直っています\n"
        "いつ戦となっても安心ですね",
    ),
    1066: (
        "、一気に修復いたしてござる\n"
        "ご覧あれ、この城の勇姿\n"
        "これでまだまだ戦えまするぞ",
    ),
    1067: (
        "の修復、一気に完了させました\n"
        "この城が傷ついたとの噂に釣られて\n"
        "敵が参っても、返り討ちにしてやれまする",
    ),
    1068: (
        "を修復いたしてございまする\n"
        "城は、いつでも戦えねばなりませぬゆえ",
    ),
    1069: (
        "修復で、あの荒れ城が早や元通りでござるわ\n",
        "よ、またよう戦ってくれい",
    ),
    1070: ("を修復しました\nこれでいつ合戦になっても安心ですね",),
    1071: (
        "修復が完了した\n"
        "携わった者の思いがこもっている\n"
        "どんな攻撃にも耐えてくれよう",
    ),
    1072: (
        "を修復しましたわ\n"
        "これでいつ攻められようと\n"
        "憂いはありません",
    ),
    1073: (
        "を修復いたしましたぞ\n"
        "これで耐久は十分でしょう\n"
        "安心して眠れますな！",
    ),
    1074: (
        "を一気に修復したぞ！\n"
        "どうだ、傷つく前よりも\n"
        "頑丈そうに仕上がっただろ！",
    ),
    1075: (
        "の修復、完了いたした\n"
        "敵に攻め込まれる前に\n"
        "作業が済んで一安心ですな",
    ),
    1076: (
        "を一気に修復しましたぞ\n"
        "これにて城の耐久は十分\n"
        "生半可な攻めでは落ちますまい",
    ),
    1077: (
        "、急ぎ修復いたしました\n"
        "あの傷ついた姿が嘘のように直っています\n"
        "いつ戦となっても安心ですね",
    ),
}
EXPECTED_BASE_GAPS = {
    1061: ("026432", "0232", "0233", "0234", "050505"),
    **{record_id: ("026432", "050505") for record_id in range(1062, 1069)},
    1069: ("", "026432", "050505"),
    **{record_id: ("026432", "050505") for record_id in range(1070, 1078)},
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1061): (
            ("的耐久恢复了", "(", "→", ")。"),
            ("026432", "0232", "0233", "0234", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1061): (
            ("的耐久恢復", "(", "→", ")。"),
            ("026432", "0232", "0233", "0234", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1061): (
        (" restored ", " HP (", " Ð ", ")."),
        ("026432", "0232", "0233", "0234", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B104_pristine_base_pc_jp_authoritative_castle_"
    "durability_recovery_and_repair_completion_reports_with_uniform_plus_8_"
    "pk_jp_sc_tc_exact_mapping_pk_en_auxiliary_context_exact_repeated_source_"
    "pairs_historical_speaker_register_siege_fall_semantics_dynamic_castle_"
    "tokens_current_layout_and_opcode_skeleton_runtime_fragment_pending"
)


def expected_auxiliary(
    side: str,
    language: str,
    record_id: int,
    overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return overrides.get((side, language, record_id), CORE.DEFAULT_AUXILIARY)


def assert_context_mapping(
    *,
    segment: int,
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    mapped_ids = {record_id + 8 for record_id in record_arities}
    expected_mapped_ids = set(range(min(record_arities) + 8, max(record_arities) + 9))
    if mapped_ids != expected_mapped_ids or mapped_ids & COMMON.PK_ONLY_RECORD_IDS:
        raise RuntimeError(f"segment {segment} uniform +8 mapping drifted")

    for record_id in record_arities:
        base_record = source_records[(15, record_id)]
        pk_record = pk_source_records[(15, record_id + 8)]
        base_literals = tuple(
            literal.text for literal in ENGINE.parse_record_literals(base_record)
        )
        pk_literals = tuple(
            literal.text for literal in ENGINE.parse_record_literals(pk_record)
        )
        if base_literals != expected_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} Base JP literal array drifted: {record_id}"
            )
        if pk_literals != expected_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} mapped PK JP literal array drifted: {record_id + 8}"
            )
        if COMMON.record_gaps(base_record) != COMMON.gaps_from_hex(
            base_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} Base JP token skeleton drifted: {record_id}"
            )
        if COMMON.record_gaps(pk_record) != COMMON.gaps_from_hex(
            pk_jp_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} PK JP token skeleton drifted: {record_id + 8}"
            )

        for side, languages, mapped_id in (
            ("base", ("SC", "TC"), record_id),
            ("pk", ("SC", "TC", "EN"), record_id + 8),
        ):
            records_by_language = base_context if side == "base" else pk_context
            for language in languages:
                expected_literals, expected_gaps = expected_auxiliary(
                    side, language, record_id, auxiliary_overrides
                )
                record = records_by_language[language][(15, mapped_id)]
                actual_literals = tuple(
                    literal.text for literal in ENGINE.parse_record_literals(record)
                )
                if actual_literals != expected_literals:
                    raise RuntimeError(
                        f"segment {segment} {side} {language} literal array drifted: "
                        f"{mapped_id}"
                    )
                if COMMON.record_gaps(record) != COMMON.gaps_from_hex(expected_gaps):
                    raise RuntimeError(
                        f"segment {segment} {side} {language} token skeleton drifted: "
                        f"{mapped_id}"
                    )


def assert_scope(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    excluded_nonvisible_coordinates: dict[str, str],
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]], None
    ],
) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }
    assert_context_mapping(
        segment=segment,
        record_arities=record_arities,
        expected_jp=expected_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        auxiliary_overrides=auxiliary_overrides,
        source_records=source_records,
        pk_source_records=pk_source_records,
        base_context=base_context,
        pk_context=pk_context,
    )

    expected_coordinates = set()
    actual_current_ellipsis = set()
    for record_id, arity in record_arities.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(
                f"segment {segment} source/current arity drifted: 15:{record_id}"
            )
        expected_gaps = COMMON.gaps_from_hex(base_gaps[record_id])
        if (
            COMMON.record_gaps(source_record) != expected_gaps
            or COMMON.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(
                f"segment {segment} Base dynamic skeleton drifted: 15:{record_id}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in excluded_nonvisible_coordinates:
                expected_text = excluded_nonvisible_coordinates[coordinate]
                if (
                    source_literal.text != expected_text
                    or current_literal.text != expected_text
                    or ENGINE.is_visible_translation_candidate(source_literal.text)
                    or ENGINE.is_visible_translation_candidate(current_literal.text)
                    or coordinate in raw_translations
                    or coordinate in translations
                ):
                    raise RuntimeError(
                        f"segment {segment} excluded nonvisible literal drifted: "
                        f"{coordinate}"
                    )
                continue
            if not ENGINE.is_visible_translation_candidate(source_literal.text):
                raise RuntimeError(
                    f"segment {segment} unexpected blank source literal: {coordinate}"
                )
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(
                    f"segment {segment} unexpected blank current literal: {coordinate}"
                )
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(raw_translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} raw decision coordinate universe drifted")
    if set(translations) != expected_coordinates:
        raise RuntimeError(
            f"segment {segment} resolved decision coordinate universe drifted"
        )
    expected_count = sum(record_arities.values()) - len(
        excluded_nonvisible_coordinates
    )
    if len(translations) != expected_count:
        raise RuntimeError(f"segment {segment} visible decision count drifted")
    if actual_current_ellipsis != ellipsis_coordinates:
        raise RuntimeError(f"segment {segment} current ellipsis coordinates drifted")

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if COMMON.layout_signature(translation) != COMMON.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {segment} layout/outer signature drifted: {coordinate}"
            )
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(
                f"segment {segment} forbidden script/control drifted: {coordinate}"
            )
        if COMMON.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(
                f"segment {segment} retains banned fullwidth punctuation: {coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(
                f"segment {segment} retains an unpaired ellipsis: {coordinate}"
            )

    semantic_assertions(source_records, raw_translations, translations)


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    excluded_nonvisible_coordinates: dict[str, str],
    basis: str,
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]], None
    ],
) -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    translations = COMMON.resolved_translations(current_records, raw_translations)
    assert_scope(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        expected_jp=expected_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        ellipsis_coordinates=ellipsis_coordinates,
        auxiliary_overrides=auxiliary_overrides,
        excluded_nonvisible_coordinates=excluded_nonvisible_coordinates,
        semantic_assertions=semantic_assertions,
    )
    COMMON.assert_isolated_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        record_arities=record_arities,
    )
    rows = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": basis,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    exact_pairs = {
        1062: 1074,
        1063: 1075,
        1064: 1076,
        1065: 1077,
    }
    for left, right in exact_pairs.items():
        if CORE.source_literals(source_records, left) != CORE.source_literals(
            source_records, right
        ):
            raise RuntimeError(
                f"segment 863 exact repair source pair drifted: {left}/{right}"
            )
        if raw_translations[f"15:{left}:0"] != raw_translations[f"15:{right}:0"]:
            raise RuntimeError(
                f"segment 863 exact repair translation pair drifted: {left}/{right}"
            )

    exact_expectations = {
        "15:1063:0": REPAIR_RELIEF,
        "15:1064:0": REPAIR_DURABLE,
        "15:1065:0": REPAIR_HURRIED,
        "15:1066:0": REPAIR_GALLANT,
        "15:1067:0": REPAIR_RUMOR,
        "15:1072:0": REPAIR_FEMININE,
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 863 repair canonical drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in ("수복", "내구", "함락", "소문", "무찔러"):
        if required not in joined:
            raise RuntimeError(f"segment 863 repair terminology drifted: {required}")
    if "、" in joined or "합전" in joined or "떨어지지" in joined:
        raise RuntimeError("segment 863 retained forbidden repair phrasing")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 863 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S863",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "excluded_nonvisible_decisions": len(
                    EXCLUDED_NONVISIBLE_COORDINATES
                ),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
