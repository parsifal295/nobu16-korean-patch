#!/usr/bin/env python3
"""Build Base authoring segment 771 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S771.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s771",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:14:0": "[임시 로그]",
    "14:14:1": (
        "\n자세력 가신의 행동 등을 알리는 로그가 일시적으로 표시됩니다.\n"
        "화면 오른쪽 아래의 로그 상세 버튼에서 지난 이력을 확인할 수 있습니다."
    ),
    "14:15:0": "[평정 명령]",
    "14:15:1": (
        "\n　·정책     ... 세력 전체를 강화하는 정책을 발령한다\n"
        " ·거래     ... 본거지의 병량과 가보를 매매한다\n"
        " ·인사-상벌  ... 가보나 관직을 가신에게 수여하거나 박탈한다\n"
        " ·인사-결연  ... 다이묘나 가신의 혼인을 주선한다\n"
        " ·인사-은거  ... 다이묘 자리에서 물러나 일문 무장에게 뒤를 잇게 한다\n"
        " ·인사-해고  ... 가신을 세력에서 추방한다\n"
        " ·본거지 이전 ... 자세력의 본거지를 다른 성으로 옮긴다\n"
        " ·군단     ... 무장에게 성과 가신 일부를 맡겨 일임한다\n"
        " ·논공행상   ... 가신의 활약과 신분 상승을 확인한다"
    ),
    "14:16:0": "[정책]",
    "14:16:1": (
        "\n유지비를 지불해 정책을 발령합니다.\n"
        "발령하려면 실행 무장을 임명해야 하며 일정 기간이 걸립니다.\n"
        "발령되면 세력 전체에 영향을 주는 효과를 얻습니다.\n"
        "정책 중에는 명령을 해금하거나 세력 고유인 것도 있습니다.\n"
        "또한 발령한 정책은 유지비가 늘어나는 대신\n"
        '"정책 LV"를 올릴 수 있습니다.\n\n'
    ),
    "14:16:2": "◇실행 무장",
    "14:16:3": (
        "\n정책의 실행 무장으로 임명할 수 있는 무장은\n"
        '세력 내 신분이 "부장" 이상인 "성주"와 "측근"입니다.\n'
        '실행 무장의 "정무"가 높을수록 발령까지의 기간이 단축됩니다.\n\n'
    ),
    "14:16:4": "◇특수 발령 조건",
    "14:16:5": (
        "\n일부 정책은 특수 조건을 충족해야 발령할 수 있습니다.\n"
        '조건에는 "일정 이상의 위신", "특정 주의를 지닌 실행 무장", "상위 취락 건설"이 있습니다.\n'
        "또한 다음 정책은 기독교가 전래되면 해금됩니다.\n"
        "·남만 교역\n"
        "·은 교역\n"
        "·기리시탄 포교(오토모 가문)"
    ),
    "14:17:0": "◇위신을 높이려면",
    "14:17:1": (
        "\n　·세력의 성을 늘린다\n"
        " ·조정에서 관직을 받거나 막부 세력과 교섭해 역직을 얻는다\n\n"
    ),
    "14:17:2": '◇"주의"를 지닌 무장',
    "14:17:3": (
        "\n　·주의에는 혁신/보수/중도 세 가지가 있다\n"
        " ·특정 주의를 지닌 무장이 있어야 발령할 수 있는 정책이 있다\n\n"
    ),
    "14:17:4": '◇"상위 취락"에 대하여',
    "14:17:5": (
        '\n　·취락 중 건설 조건이나 효과가 특수한 것을 "상위 취락"이라 한다\n'
        " ·일부 정책은 특정 상위 취락을 필요한 수만큼 건설해야 한다\n"
        " ·상위 취락별로 건설할 수 있는 군이 한정되어 있으며\n"
        '  "영내 문제"를 해결하면 상위 취락을 건설할 수 있다\n'
        " ·정책 발령에 필요한 상위 취락은 여섯 종류다\n"
        '  "온천향", "교역항", "금산 마을", "은산 마을", "절", "남만사"'
    ),
    "14:18:0": "◇정책 LV",
    "14:18:1": (
        "\n발령한 정책은 유지비가 늘어나는 대신 LV를 올릴 수 있습니다.\n"
        "정책 LV를 올리면 정책 효과가 더욱 강화됩니다.\n"
        "또한 LV마다 발령까지 걸리는 기간과 실행 무장 수도 늘어납니다.\n"
        "※금전이 없어 유지비를 낼 수 없게 되면\n"
        " 발령 중인 모든 정책이 중지되므로 LV를 지나치게 올리지 않도록 주의합시다\n\n"
    ),
    "14:18:2": "◇정책 중지",
    "14:18:3": (
        "\n정책이 중지되면 모든 정책 효과가 무효화됩니다.\n"
        "중지된 정책은 하루치 유지비를 지불하면 다시 발령할 수 있습니다.\n"
        "다시 발령한 정책은 중지 전 LV로 발령됩니다.\n\n"
    ),
    "14:18:4": "◇정책 주의점",
    "14:18:5": (
        "\n　·유지비는 월초에 지불한다\n"
        " ·발령 중이거나 발령 준비 중이어도 유지비를 지불한다\n"
        " ·한번 발령하면 취소할 수 없다\n"
        " ·금전 수지가 적자여도 발령할 수 있다\n"
        " ·유지비를 지불할 수 없으면 발령 중인 모든 정책이 중지된다\n"
        " ·중지된 정책은 하루치 유지비를 지불하면 다시 발령할 수 있다"
    ),
}

EXPECTED_ARITIES = {14: 2, 15: 2, 16: 6, 17: 6, 18: 6}
EXPECTED_DIVERGENCES = {"JP": {16}, "SC": set(), "TC": set()}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_exact_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_semantics_priority"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {14: 19, 15: 21, 16: 23, 17: 25, 18: 26}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 771 record has no configured PK mapping: {base_record_id}"
        ) from exc


def line_layout_signature(text: str) -> tuple[object, ...]:
    lines = text.split("\n")
    leading = tuple(
        line[: len(line) - len(line.lstrip(" \t\u3000"))]
        for line in lines
    )
    trailing = tuple(
        line[len(line.rstrip(" \t\u3000")) :]
        for line in lines
    )
    return (
        text.count("\n"),
        leading,
        trailing,
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
    )


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

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(14, 19)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(14, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(14, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != EXPECTED_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 771 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 771 arity drifted at 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 771 unexpectedly contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 771 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 771 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 771 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 771 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 771 retains banned fullwidth punctuation: {coordinate}")

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 22:
        raise RuntimeError("segment 771 decision universe drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "평정",
        "병량",
        "관직",
        "역직",
        "기리시탄",
        "상위 취락",
        "본거지",
        "해금",
        "결연",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 771 required terminology drifted")
    if any(term in joined for term in ("커맨드", "해방", "고급 취락", "호족")):
        raise RuntimeError("segment 771 retains a forbidden or PK-priority term")
    if "기리시탄 포교(오토모 가문)" not in TRANSLATIONS["14:16:5"]:
        raise RuntimeError("14:16:5 must retain the Base Christianity policy attribution")
    if (
        "다이묘 자리에서 물러나" not in TRANSLATIONS["14:15:1"]
        or "다이묘에서 물러나" in TRANSLATIONS["14:15:1"]
    ):
        raise RuntimeError("14:15:1 must describe retirement from the daimyo position")


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
        target = prepared.visible_targets.get(
            ("base_msggame", block_id, record_id, literal_id)
        )
        if target is None:
            raise RuntimeError(
                f"decision target is absent from the current Base universe: {coordinate}"
            )
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
        raise RuntimeError(
            "validated decision count differs from the segment translation count"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S771",
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
