#!/usr/bin/env python3
"""Build Base authoring segment 766 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S766.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s766", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:446:0": '"제도 개신 LV3"',
    "13:447:0": '정책 "제도 개신"이 LV3로 오르면서\n"성주의 지행지 교체"를 할 수 있게 되었습니다.\n자세력의 영지를 점검해 지행지 배분을 다시 검토합시다.\n\n[해금된 내용]\n·성주의 지행지 교체',
    "13:448:0": '"위풍"',
    "13:449:0": '많은 적 부대를 상대로 합전에서 승리하면\n그 명성이 "위풍"이 되어 주변에 퍼지고 영향을 미칩니다.\n\n단순히 적을 격파한 것 이상의 전과를 얻을 수 있으므로\n적 부대가 많다면 적극적으로 합전 승리를 노립시다.',
    "13:450:0": '"지행지 변경"',
    "13:451:0": '정책 "제도 개신" LV3 발령으로 성주를 교체할 수 있게 되었습니다.\n\n성 능력에 따라 설정 가능한 성하 방침의 종류도 달라지므로\n내정을 유리하게 진행하려면 성의 상황에 맞춰 지행지를 배분합시다.\n※설정 가능한 성하 방침은 "능력 보정" 탭에서 확인할 수 있습니다.',
    "13:452:0": '"재해"',
    "13:453:0": '달 초에는 여러 자연재해가 일어나기도 합니다.\n재해가 발생한 군은 피해를 입을 뿐 아니라 영내 문제도 생깁니다.\n영내 문제를 빨리 해결하지 않으면 잇키가 일어나기도 합니다.\n\n[재해 피해를 피하려면]\n·정책 "관개 정비"를 발령한다\n·성하 시설 "관개 수로"를 건설한다',
    "13:454:0": '"잇키"',
    "13:455:0": "영내 문제나 적대 세력의 조략으로 잇키가 일어나기도 합니다.\n잇키가 발생하면 여러 불이익이 있고 방치할수록 다른 군까지 번지므로\n일찍 진압하는 것이 중요합니다.\n\n잇키가 일어난 군에 부대를 주둔시키면 진압할 수 있습니다.\n출진할 수 있다면 성주가 판단해 부대를 보내 진압에 나섭니다.",
    "13:456:0": '"본거지 이전"',
    "13:457:0": "큰 비용이 들지만 본거지를 이전할 수 있습니다.\n통치 범위 밖의 성을 얻었다면 이전을 검토합시다.\n\n※통치 범위 밖의 성에서는 금전 수입이 크게 줄어듭니다.\n※본거지를 옮기지 않고 성을 군단에 맡길 수도 있습니다.",
    "13:458:0": '"도움말"',
    "13:459:0": '도움말에는 게임에 관한 다양한 정보가 실려 있습니다.\n모르는 것이 있다면 확인해 봅시다.\n\n각 명령에서 화면 왼쪽 위의 "?" 버튼을 누르면\n해당 도움말을 확인할 수 있습니다.',
    "13:460:0": '[도움말의 종류]\n·화면 설명 ... 각 명령 등의 표시 내용을 설명\n각 화면 왼쪽 위의 "?" 버튼에서도 확인 가능\n·용어 ... 다양한 용어를 설명\n·TIPS ... 공략 도움말\n·튜토리얼 다시 보기 ... 한 번 표시된 튜토리얼을 다시 확인\n·이력 ... 과거에 본 도움말의 이력을 확인하고 선택 가능',
    "13:461:0": '"군을 완전히 개발하면"',
    "13:462:0": "한 군을 완전히 개발해 석고가 더 올랐습니다.\n이 기세로 군을 적극적으로 개발해 세력을 발전시킵시다.\n\n[군을 완전히 개발하려면]\n·모든 농촌과 시장을 장악한다\n·모든 개발 용지에 건설한다\n·모든 상위 취락을 건설한다",
    "13:463:0": '[군의 성장을 앞당기려면]\n·통솔이 높은 무장을 대관이나 영주로 임명한다\n·"군 개발", "영내 제책" 명령을 실행한다\n\n[추가 발전]\n·성의 지배하에 있는 모든 군을 개발하면 상업이 더 오른다',
    "13:464:0": '"성의 모든 군을 완전히 개발하면"',
    "13:465:0": "성의 모든 군을 완전히 개발해 각 군의 상업이 더 올랐습니다.\n이 기세로 다른 성의 군도 개발해 세력을 발전시킵시다.\n\n[성의 군을 완전히 개발하려면]\n·각 군의 모든 농촌과 시장을 장악한다\n·각 군의 모든 개발 용지에 건설한다\n·각 군에 건설 가능한 모든 상위 취락을 건설한다",
    "13:466:0": '"여러 부대 선택"',
    "13:467:0": "출진 중인 부대가 많아졌습니다.\nShift + 드래그로 여러 부대를 선택할 수 있으니\n목표를 한꺼번에 변경할 때 활용합시다.",
    "13:468:0": "출진 중인 부대가 많아졌군요.\n㍉㎝㍑㎝㌣로 여러 부대를 선택할 수 있으니\n목표를 한꺼번에 변경할 때 활용해 주십시오.",
    "13:469:0": '"협격"',
}

BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）【】")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if 446 <= base_record_id <= 447:
        return base_record_id + 38
    if 448 <= base_record_id <= 449:
        return base_record_id + 39
    if 450 <= base_record_id <= 451:
        return base_record_id + 40
    if 452 <= base_record_id <= 457:
        return base_record_id + 41
    if 458 <= base_record_id <= 469:
        return base_record_id + 42
    raise RuntimeError(f"segment 766 record has no configured PK mapping: {base_record_id}")


def assert_scope(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }
    expected_divergences = {
        "JP": {451, 457, 468},
        "SC": {451, 457, 463},
        "TC": {451, 457, 463},
    }
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(446, 470)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(13, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(13, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != expected_divergences[language]:
            raise RuntimeError(
                f"segment 766 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id in range(446, 470):
        source_literals = ENGINE.parse_record_literals(source_records[(13, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(13, record_id)])
        if len(source_literals) != 1 or len(current_literals) != 1:
            raise RuntimeError(f"segment 766 record must remain a single static literal: 13:{record_id}")
    for coordinate, translation in TRANSLATIONS.items():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError(f"segment 766 must not add U+3000 or CR: {coordinate}")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"segment 766 retains banned fullwidth punctuation: {coordinate}")
    if "내정을 유리하게" not in TRANSLATIONS["13:451:0"] or '"능력 보정" 탭' not in TRANSLATIONS["13:451:0"]:
        raise RuntimeError("13:451 must follow Base JP and retain the internal-affairs purpose/tab")
    if "본거지" not in TRANSLATIONS["13:456:0"] or "본거지" not in TRANSLATIONS["13:457:0"]:
        raise RuntimeError("13:456/457 must retain 本拠=본거지")
    if "신중" in TRANSLATIONS["13:457:0"]:
        raise RuntimeError("13:457 imported a PK-only caution sentence")
    if not all(
        term in TRANSLATIONS["13:459:0"]
        for term in ("도움말", "명령", "왼쪽 위")
    ):
        raise RuntimeError("13:459 must use the fixed Help/command/location terminology")
    if not all(
        term in TRANSLATIONS["13:468:0"]
        for term in ("많아졌군요", "활용해 주십시오")
    ):
        raise RuntimeError("13:468 must preserve the Base-specific conversational voice")
    if any(term in "\n".join(TRANSLATIONS.values()) for term in ("자동 임명", "전마제")):
        raise RuntimeError("segment 766 imported a PK-only explanation")
    if len(TRANSLATIONS) != 24:
        raise RuntimeError("segment 766 decision count drifted")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S766",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": 0,
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
