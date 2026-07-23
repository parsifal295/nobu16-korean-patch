#!/usr/bin/env python3
"""Build Base authoring segment 786 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S786.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s786", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:94:0": "[기마와 철포]",
    "14:94:1": (
        "\n"
        "부대의 기마 LV와 철포 LV를 높이면 전투에서 유리해집니다.\n"
        "일반적인 LV 상한은 9이지만 특정 세력은\n"
        "고유 정책을 발령하여 LV 상한을 높일 수 있습니다.\n"
        "\n"
    ),
    "14:94:2": "◇LV를 높이려면",
    "14:94:3": (
        "\n\u3000"
        "·성하 시설을 건설한다\n"
        " ·정책을 발령한다\n"
        " ·LV를 높이는 특성을 지닌 무장을 부대에 편성한다\n"
        ' ·영내 문제를 해결하여 "목마장"과 "대장간 마을"을 건설한다\n'
        "\n"
    ),
    "14:94:4": "◇기마와 철포의 효과",
    "14:94:5": (
        "\n\u3000"
        "·(합전 중에만) 적 부대와 접촉할 때 반드시 강력한 공격을 한다\n"
        " ·(합전 이외) 적 부대와 교전 중 일정 확률로 강력한 공격을 한다\n"
        " ·(공통) LV가 높을수록 위력이 오른다\n"
        " ·(공통) LV가 5와 10이 되면 각각 위력이 크게 오른다"
    ),
    "14:95:0": "[특수 요충지]",
    "14:95:1": (
        "\n"
        "합전의 특수 요충지는 종류에 따라 발동 효과가 다릅니다.\n"
        "\n"
    ),
    "14:95:2": "◇효과 종류",
    "14:95:3": (
        "\n\u3000"
        "·낙석: 범위 안 부대에 피해를 주고 혼란시킨다\n"
        " ·고무: 범위 안 부대의 체력 회복\n"
        " ·다리 무너뜨리기: 다리를 파괴하여 경로 차단 "
    ),
    "14:96:0": "[여러 부대의 진군]",
    "14:96:1": (
        "\n"
        "여러 부대가 한데 모여 진군할 수 있습니다.\n"
        "함께 진군할 수 있는 부대 수는 가도 종류에 따라 제한됩니다.\n"
        "군과 군을 잇는 가도 종류는 길 뷰에서 확인할 수 있습니다.\n"
        "좁은 길에서는 대군도 병력을 살리기 어려우므로\n"
        "험한 지형의 성은 공격하기 어렵고 방어하기 쉬운 경우가 많습니다.\n"
        "\n"
    ),
    "14:96:2": "◇함께 진군할 수 있는 부대 수",
    "14:96:3": (
        "\n\u3000"
        "·군의 중심     ... 4부대\n"
        " ·넓은 길(노란색) ... 4부대\n"
        " ·좁은 길(초록색) ... 2부대"
    ),
    "14:97:0": "[잇키]",
    "14:97:1": (
        "\n"
        "영내 문제나 적대 세력의 조략으로 잇키가 일어나기도 합니다.\n"
        "영내에서 잇키가 발생하면 서둘러 진압하는 것이 중요합니다.\n"
        "\n"
    ),
    "14:97:2": "◇특징",
    "14:97:3": (
        "\n\u3000"
        "·잇키가 일어난 군에서는 출진할 수 없다\n"
        " ·잇키가 일어난 군에서는 취락 장악이 서서히 해제된다\n"
        ' ·잇키가 일어난 군에서는 영내 행동인 "취락 장악"과 "취락 건설"을 할 수 없다\n'
        " ·잇키가 일어난 군에서는 병량 수입과 금전 수입을 얻을 수 없다\n"
        " ·잇키를 방치하면 주변 군으로 퍼진다\n"
        " ·부대를 일정 시간 주둔시키면 잇키를 진압할 수 있다\n"
        " ·출진할 수 있다면 성주가 판단해 부대를 보내 진압하러 나선다\n"
        " ·잇키가 일어난 군은 공격받으면 금세 제압당한다"
    ),
    "14:98:0": "[위신]",
    "14:98:1": (
        "\n"
        "위신은 세력의 격을 나타내는 수치입니다.\n"
        "\n"
    ),
    "14:98:2": "◇위신을 높이면",
    "14:98:3": (
        "\n\u3000"
        "·정책을 발령할 수 있다\n"
        " ·상대보다 위신이 높으면 쳐들어온 적병이 위축되어 유리하게 싸울 수 있다\n"
        " ·자신보다 위신이 낮은 세력과의 외교가 유리해진다\n"
        "\n"
    ),
    "14:98:4": "◇위신을 높이려면",
    "14:98:5": (
        "\n\u3000"
        "·세력의 성을 늘린다\n"
        " ·외교를 통해 조정에서 관직을, 막부에서 역직을 얻는다"
    ),
}

EXPECTED_ARITIES = {94: 6, 95: 4, 96: 4, 97: 4, 98: 6}
EXPECTED_DIVERGENCES = {
    "JP": {97},
    "SC": {97},
    "TC": set(),
}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－＆"
)
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘㌃㌔㌢㌧㌫㌶㍉┨┯")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {94: 128, 95: 131, 96: 132, 97: 133, 98: 135}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 786 record has no configured PK mapping: {base_record_id}"
        ) from exc


def expected_gaps(arity: int) -> tuple[bytes, ...]:
    return tuple(
        part
        for _ in range(arity // 2)
        for part in (b"\x1b\x43\x49", b"\x1b\x43\x5a")
    ) + (b"\x05\x05\x05",)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def prior_translation(coordinate: str) -> str:
    for decision_path in sorted(
        OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl")
    ):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate:
                return str(row["translation"])
    raise RuntimeError(f"prior exact translation is absent: {coordinate}")


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    lines = text.split("\n")
    leading = tuple(line[: len(line) - len(line.lstrip(" \t\u3000"))] for line in lines)
    trailing = tuple(line[len(line.rstrip(" \t\u3000")) :] for line in lines)
    return (
        text.count("\n"),
        leading,
        trailing,
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
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
            for record_id in EXPECTED_ARITIES
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
                f"segment 786 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 786 literal arity drifted: 14:{record_id}")
        expected = expected_gaps(arity)
        if record_gaps(source_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 786 pristine opcode gaps drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected:
            raise RuntimeError(f"segment 786 current opcode gaps drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(
                    f"segment 786 unexpectedly contains a blank target: {coordinate}"
                )
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 786 decision is missing: {coordinate}")
            if layout_signature(translation) != layout_signature(literal.text):
                raise RuntimeError(f"segment 786 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 786 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 786 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(
                    f"segment 786 retains banned fullwidth punctuation: {coordinate}"
                )
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(
                    f"segment 786 controller-glyph skeleton drifted: {coordinate}"
                )

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 24:
        raise RuntimeError("segment 786 decision universe drifted")

    source_98 = ENGINE.parse_record_literals(source_records[(14, 98)])[4].text
    current_98 = ENGINE.parse_record_literals(current_records[(14, 98)])[4].text
    source_17 = ENGINE.parse_record_literals(source_records[(14, 17)])[0].text
    current_17 = ENGINE.parse_record_literals(current_records[(14, 17)])[0].text
    if source_98 != source_17 or current_98 != current_17:
        raise RuntimeError("14:98:4/14:17:0 exact source/current reuse drifted")
    if TRANSLATIONS["14:98:4"] != prior_translation("14:17:0"):
        raise RuntimeError("14:98:4 must exactly reuse the approved 14:17:0 translation")

    pk_extra_129 = ENGINE.parse_record_literals(pk_source_records[(14, 129)])
    pk_extra_130 = ENGINE.parse_record_literals(pk_source_records[(14, 130)])
    pk_extra_134 = ENGINE.parse_record_literals(pk_source_records[(14, 134)])
    if len(pk_extra_129) != 6 or "家宰特性" not in pk_extra_129[3].text:
        raise RuntimeError("PK-only 14:129 house-steward extension drifted")
    if len(pk_extra_130) != 2 or pk_extra_130[0].text != "◇鉄砲伝来":
        raise RuntimeError("PK-only 14:130 firearm-arrival page drifted")
    if len(pk_extra_134) != 4 or "名所" not in pk_extra_134[3].text:
        raise RuntimeError("PK-only 14:134 landmark-uprising extension drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "기마",
        "철포",
        "목마장",
        "대장간 마을",
        "특수 요충지",
        "다리 무너뜨리기",
        "길 뷰",
        "잇키",
        "위신",
        "관직",
        "역직",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 786 required terminology drifted")
    if any(
        term in joined
        for term in ("말 목장", "마목장", "가재 특성", "철포 전래", "명소 LV")
    ):
        raise RuntimeError("segment 786 retains a legacy term or imports a PK-only rule")
    if "공격받으면" not in TRANSLATIONS["14:97:3"]:
        raise RuntimeError("14:97:3 lost the Base SC/TC attack-condition clarification")
    if "짧은 기간에 적에게 제압" in TRANSLATIONS["14:97:3"]:
        raise RuntimeError("14:97:3 imported the PK-only clarified final rule")


def assert_isolated_overlay_roundtrip(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements: dict[tuple[int, int, int], str] = {}
    reverse_replacements: dict[tuple[int, int, int], str] = {}
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse_replacements[key] = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text

    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError("segment 786 Base record count drifted from 19152")

    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 786 changed an out-of-scope record: {key}")
    for record_key in target_records:
        if record_gaps(rebuilt_records[record_key]) != record_gaps(current_records[record_key]):
            raise RuntimeError(f"segment 786 changed a target nonstring skeleton: {record_key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment 786 literal failed UTF-16 round-trip: {key}")

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 786 reverse overlay is not byte-exact")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
    assert_isolated_overlay_roundtrip(prepared)
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
                "segment": "base_msggame_B001_S786",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": 0,
                "steam_write_performed": False,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
