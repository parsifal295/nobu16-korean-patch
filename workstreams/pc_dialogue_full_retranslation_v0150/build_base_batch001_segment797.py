#!/usr/bin/env python3
"""Build Base authoring segment 797 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S797.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s797", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
RAW_TRANSLATIONS: dict[str, str] = {
    "14:148:0": "【게임 힌트】\n◇상황에 따라 생각할 점",
    "14:148:1": (
        "\n"
        "●주변에 강한 세력이 있다\n"
        "・공격당하면 패배할 것 같은 세력이 가까이 있다면\n"
        "「외교」 명령으로 친선을 도모하고 동맹을 맺어 전쟁을 피할 수 있습니다\n"
        "・전력 차가 매우 크다면 신종도 고려해 볼 만합니다\n"
        "\n"
        "●주변에 약한 세력이 있다\n"
        "・이길 수 있을 것 같은 세력이 있다면 「출진」 명령으로 공격합시다\n"
        "・제압한 성은 아군의 것이 되어 금전 수입과 병력이 늘어납니다\n"
        "\n"
        "●무장이 부족하다\n"
        "・비어 있는 군이 많거나 명령을 실행하지 못하는 일이 잦다면\n"
        "무장 등용을 고려합시다\n"
        "・등용하려면 「영내 제책」 명령으로 「무장 탐색」을 실행하거나,\n"
        "적과의 전쟁에서 승리했을 때 등용을 선택하는 등의 방법이 필요합니다\n"
        "\n"
        "●무장은 있지만 신분이 낮다\n"
        "・훈공을 쌓으면 신분이 오릅니다\n"
        "・훈공을 쌓으려면 「성하 시설」 등의 명령에서 실행 무장으로 선택하거나\n"
        "「건의」를 승인하거나, 출진해 전쟁에서 승리하는 등의 방법이 필요합니다\n"
        "・신분 「조두」가 많다면 「정책」 명령에서 「호로슈 결성」을 발령하는 것이 좋습니다\n"
        "・신분이 오르면 영주나 성주로 임명할 수 있고\n"
        "「정책」 명령이나 「외교」 명령에서 선택할 수 있게 됩니다"
    ),
    "14:149:0": "【직명】",
    "14:149:1": (
        "\n"
        "자기 세력 안에서 맡은 위치를 「직명」이라 부릅니다.\n"
        "직명에 따라 실행 무장으로 임명될 수 있습니다. 직명은 다음과 같습니다.\n"
        "\n"
        "・다이묘  … 세력의 주인. 본거지의 성주와 다이묘 군단의 군단장을 겸임\n"
        "「인사-은거」 명령으로 일문 무장에게만 계승 가능\n"
        "・군단장 … 다이묘 군단 이외의 군단을 이끄는 무장. 소속 성의 성주도 겸임\n"
        "「군단-신설」 명령으로 신분 「가로」 이상인 무장을 임명 가능\n"
        "・성주  … 본거지 이외의 「성」을 통치하는 무장\n"
        "「지행」 명령으로 신분 「사무라이 대장」 이상인 무장을 임명 가능\n"
        "・영주  … 본거지 이외의 성 영내에 있는 「군」을 통치하는 무장\n"
        "「지행」 명령으로 신분 「아시가루 대장」 이상인 무장을 임명 가능\n"
        "・대관  … 다이묘를 대신해 본거지 영내의 군을 통치하는 무장\n"
        "「대관」 명령으로 신분과 관계없이 임명 가능\n"
        "・측근  … 위 직명에 해당하지 않는 무장\n"
        "\n"
        "※실행 무장은 TIPS【실행 무장으로 임명할 수 있는 무장】에 설명되어 있습니다"
    ),
    "14:150:0": "【무장의 영내 행동】",
    "14:150:1": (
        "\n"
        "성주/영주로 임명된 무장은 자율적으로 영내를 발전시키는 행동을 합니다.\n"
        "성주/영주가 하는 각 행동을 마치는 데는 일정한 기간이 필요합니다.\n"
        "유능한 무장일수록 행동을 마치는 데 걸리는 기간이 짧아집니다.\n"
        "기본적으로는 현재 행동을 마칠 때까지 다른 행동을 하지 않지만, 다음 경우에는 중지됩니다.\n"
        "\n"
        "・공략 목표를 설정/해제한다\n"
        "・성주/영주를 변경한다"
    ),
    "14:151:0": "◇영주/성주가 하는 행동",
    "14:151:1": (
        "\n"
        "・취락 장악 … 영지에 있는 취락을 장악한다\n"
        "・취락 건설 … 개발 용지에 취락을 건설한다\n"
        "・장악 방해 … 공략 목표 세력에 인접한 군의 영주는\n"
        "적군의 취락 장악을 방해한다(영주의 지략이 60 이상)\n"
        "・국인중 친선 … 주변 군의 국인중과 친선을 쌓아 원군을 부를 수 있게 한다\n"
        "・국인중 회유 … 국인중을 휘하에 들이기 위해 회유한다\n"
        "・군비   … 「공략 목표」에 따라 임전 준비를 한다\n"
        "・영지 순찰 … 영지의 형편을 살핀다\n"
        "\n"
    ),
    "14:151:2": "◇성주만 하는 행동",
    "14:151:3": (
        "\n"
        "・군 방위  … 적의 공격을 받으면 군을 방어하기 위해 부대를 출진시킨다\n"
        "・군 탈환  … 적에게 빼앗긴 영내의 군을 제압한다\n"
        "・잇키 진압 … 잇키가 발생한 군에 부대를 출진시켜 진압한다\n"
        "・시설 건설 … 영지의 성에 성하 시설을 건설한다\n"
        "・시설 증축 … 영지의 성에 있는 성하 시설을 증축한다\n"
        "\n"
        "※다이묘는 「군 방위」「군 탈환」「잇키 진압」만 한다\n"
        "※시설 건설/증축은 성하 방침을 설정한 경우에만 한다\n"
        "※영내 문제 「국경 분쟁」을 방치하면 독단으로 출진해 적 세력의 군을 제압하기도 한다\n"
        "※출진 중에는 작업이 멈춘다"
    ),
    "14:152:0": "【게임 시작】",
    "14:152:1": (
        "\n"
        "게임을 시작하기 위한 설정을 할 수 있습니다.\n"
        "「시나리오 선택」과 「세력 선택」을 반드시 설정해야 합니다.\n"
        "또한 「설정」 버튼에서 더 자세한 항목도 설정할 수 있습니다.\n"
        "\n"
    ),
    "14:152:2": "◇시나리오 선택",
    "14:152:3": (
        "\n"
        "게임을 시작할 연대를 선택할 수 있습니다.\n"
        "연대에 따라 세력과 그 규모가 달라집니다.\n"
        "시나리오에는 「역사적 사실에 기반한 시나리오」와 「역사와 무관한 가상 시나리오」가 있습니다.\n"
        "※「등장 전환」 버튼에서 게임에 등장시킬 「등록 무장」「추가 무장」도 설정할 수 있습니다\n"
        "\n"
    ),
    "14:152:4": "◇세력 선택",
    "14:152:5": (
        "\n"
        "선택한 연대에 등장하는 세력 중 조작할 세력을 선택할 수 있습니다.\n"
        "세력에 따라 규모와 자원 등 상황이 다릅니다.\n"
        "「세력 일람」 버튼에서 더 자세한 정보를 확인할 수 있습니다.\n"
        "※여기에 표시되는 내용은 참고용이므로 게임을 시작하면 다소 달라질 수 있습니다"
    ),
    "14:153:0": "【성하 방침】",
    "14:153:1": (
        "\n"
        "성하 방침을 설정하면 성주가 자율적으로 성하 시설을 건설합니다.\n"
        "영주도 성하 방침에 맞는 취락을 개발 용지에 건설합니다.\n"
        "\n"
        "정책 「제도 개신」 LV1을 발령하면 설정할 수 있으며 건설 비용도 들지 않습니다.\n"
        "성을 특정 용도에 특화할 수 있으므로\n"
        "원하는 성하 방침을 선택할 수 있도록 무장의 지행지를 조정해 봅시다.\n"
        "※건설 속도와 증축 가능한 LV 상한은 성 능력에 따라 다릅니다.\n"
        "\n"
    ),
    "14:153:2": "◇성하 방침의 종류",
    "14:153:3": (
        "\n"
        "・방위 … 성 능력이 「통솔 70 이상」이면 설정 가능\n"
        "망루 등 방어에 도움이 되는 시설을 우선\n"
        "・공격 … 성 능력이 「무용 70 이상」이면 설정 가능\n"
        "연병장 등 공격에 도움이 되는 시설을 우선\n"
        "・진군 … 성 능력이 「지략 70 이상」이면 설정 가능\n"
        "치중 집결소 등 원정에 도움이 되는 시설을 우선\n"
        "・내정 … 성 능력이 「정무 70 이상」이면 설정 가능\n"
        "상인 마을 등 내정에 도움이 되는 시설을 우선\n"
        "\n"
    ),
    "14:153:4": "◇성하 방침의 주의점",
    "14:153:5": (
        "\n"
        "・외교 중개나 정책 발령 등 임무 중인 무장은 건설하지 않는다\n"
        "・출진 중에는 작업이 멈춘다\n"
        "・성주를 해임하거나 소속 군단을 변경하면 중지된다\n"
        "・성하 방침을 설정한 성의 성주는 건설을 우선한다"
    ),
}
EXPECTED_ARITIES = {148: 2, 149: 2, 150: 2, 151: 4, 152: 6, 153: 6}
EXPECTED_DIVERGENCES = {
    "JP": {148, 153},
    "SC": {148, 150, 151},
    "TC": {148, 150, 151},
}
PK_ONLY_RECORD_IDS = {207, 212, 213, 214, 215, 218, 219}
PROTECTED_GLYPHS = set("◇●※①②○")
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－")
ASCII_PUNCTUATION = str.maketrans(
    {
        "【": "[",
        "】": "]",
        "「": '"',
        "」": '"',
        "／": "/",
        "，": ",",
        "。": ".",
        "・": "·",
        "…": "...",
    }
)
BASIS = (
    "pristine_base_pc_jp_authoritative_with_base_sc_tc_and_explicit_"
    "mapped_pk_jp_en_sc_tc_auxiliary_context_pk_only_expansions_excluded"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {148: 206, 149: 208, 150: 209, 151: 210, 152: 211, 153: 216}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 797 record has no PK mapping: {base_record_id}") from exc


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def expected_static_gaps(arity: int) -> tuple[bytes, ...]:
    return tuple([b"\x1b\x43\x49", b"\x1b\x43\x5a"] * (arity // 2) + [b"\x05\x05\x05"])


def line_edge(text: str) -> tuple[str, str]:
    return (
        text[: len(text) - len(text.lstrip(" \t\u3000"))],
        text[len(text.rstrip(" \t\u3000")) :],
    )


def adopt_current_layout(raw: str, current: str) -> str:
    raw_lines = raw.split("\n")
    current_lines = current.split("\n")
    if len(raw_lines) != len(current_lines):
        raise RuntimeError("raw translation LF count differs from current layout")
    rendered = []
    for raw_line, current_line in zip(raw_lines, current_lines):
        leading, trailing = line_edge(current_line)
        visible = raw_line.strip(" \t\u3000").translate(ASCII_PUNCTUATION)
        rendered.append(leading + visible + trailing)
    return "\n".join(rendered)


def layout_signature(text: str) -> tuple[object, ...]:
    lines = text.split("\n")
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line_edge(line) for line in lines),
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def resolved_translations(current_records: dict[tuple[int, int], Any]) -> dict[str, str]:
    translations = {}
    for coordinate, raw in RAW_TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        translations[coordinate] = adopt_current_layout(raw, current)
    return translations


def assert_scope(prepared: Any, translations: dict[str, str]) -> None:
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
    mapped_ids = {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITIES}
    if mapped_ids.intersection(PK_ONLY_RECORD_IDS):
        raise RuntimeError("segment 797 mapped a PK-only expansion record")
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context["SC"], pk_context["SC"]),
        ("TC", base_context["TC"], pk_context["TC"]),
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
                f"segment 797 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    expected_coordinates = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_record = source_records[(14, record_id)]
        current_record = current_records[(14, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 797 arity drifted: 14:{record_id}")
        expected_gaps = expected_static_gaps(arity)
        if record_gaps(source_record) != expected_gaps or record_gaps(current_record) != expected_gaps:
            raise RuntimeError(f"segment 797 literal/opcode skeleton drifted: 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            expected_coordinates.add(coordinate)
            translation = translations[coordinate]
            if layout_signature(translation) != layout_signature(literal.text):
                raise RuntimeError(f"segment 797 layout signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(literal.text):
                raise RuntimeError(f"segment 797 protected glyphs drifted: {coordinate}")
            if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 797 forbidden script/control drifted: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 797 retains fullwidth punctuation: {coordinate}")
    if set(translations) != expected_coordinates or len(translations) != 22:
        raise RuntimeError("segment 797 decision universe drifted")

    joined = "\n".join(translations.values())
    required_terms = (
        "영내 제책",
        "국인중 친선",
        "국인중 회유",
        "본거지",
        "사무라이 대장",
        "아시가루 대장",
        "제도 개신",
        "치중 집결소",
        "상인 마을",
        "지행지",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 797 required terminology drifted")
    if any(term in joined for term in ("호족", "본거의", "사무라이대장", "아시가루대장", "치중소", "상인마을")):
        raise RuntimeError("segment 797 retains a forbidden legacy term")


def assert_isolated_overlay_roundtrip(
    prepared: Any, translations: dict[str, str]
) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements = {}
    reverse_replacements = {}
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse_replacements[key] = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError("segment 797 record count drifted from 19152")
    target_records = {(14, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 797 changed an out-of-scope record: {key}")
    for key in target_records:
        if record_gaps(rebuilt_records[key]) != record_gaps(current_records[key]):
            raise RuntimeError(f"segment 797 target skeleton drifted: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 797 UTF-16 round-trip failed: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 797 reverse overlay is not byte-exact")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    translations = resolved_translations(current_records)
    assert_scope(prepared, translations)
    assert_isolated_overlay_roundtrip(prepared, translations)
    rows = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets[("base_msggame", block_id, record_id, literal_id)]
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
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 797 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S797",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
