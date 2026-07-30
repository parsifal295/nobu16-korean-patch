#!/usr/bin/env python3
"""Build Base authoring segment 986 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment982 as STABLE


ENGINE = STABLE.ENGINE
COMMON = STABLE.COMMON
SUPPORT = STABLE.SUPPORT
UTIL = COMMON.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S986.private.v1.jsonl"
)
SEGMENT = 986
TRANSLATIONS_BY_RECORD = {
    2331: (
        "영내의 각 성을 부유하게 하려면\n"
        "성하를 번성시키는 것이 긴요하니\n"
        "시설 확충을 검토해 보는 것이 어떻겠습니까?",
    ),
    2332: (
        "각지의 개간을 추진해 석고를 높이고\n"
        "백성을 윤택하게 하면 병사도 군량도\n"
        "절로 갖춰질 것",
    ),
    2333: (
        "각지의 상업을 장려해\n"
        "금전 수입을 늘려서\n"
        "우리 가문의 힘으로 삼고",
    ),
    2334: (
        "우리 가문의 무위를 천하에 보이고자\n"
        "공략 목표로 정한 적의 성을\n"
        "확실히 함락해 보는 것이 어떻겠습니까?",
    ),
    2335: (
        "의 힘을 보이고자\n"
        "직접 칼을 들어 합전에서 승리해\n"
        "천하에 이름을 떨치고",
    ),
    2336: (
        "거부하면 다시 선택할 수 없습니다\n"
        "정말 괜찮으시겠습니까?",
    ),
    2337: (
        ", 이번 목표를…\n"
        "가신들에게 확실히 알려, 실현을 위해\n"
        "모두 진력",
    ),
    2338: (
        "표적은 상당히 영악한 자이니\n"
        "아마 이번 계략은 성공할 듯합니다",
    ),
    2339: (
        "목표로 삼은 영주는 특수한 기량의 소유자\n"
        "이번 일도 쉽사리 풀리지는 않겠군요…",
    ),
    2340: (
        "목표로 삼은 성에는 특수한 기량을 지닌 자가 있어\n"
        "이번 일도 쉽사리 풀리지는 않겠군요…",
    ),
    2341: (
        "목표로 삼은 성에는 지혜로운 자가 많아\n"
        "계략을 성공시키기는 지극히 어려울 듯합니다",
    ),
    2342: (
        "적의 다이묘는 상당한 지략가이니\n"
        "이번 일은 어렵다고",
    ),
    2343: (
        "목표로 삼은 영주는 상당한 지략가이니\n"
        "이번 일은 어렵다고",
    ),
    2344: (
        "그 자가 충성심이 약하다고는 하나\n"
        "주군 가문을 배신하도록 결심시키는 일은\n"
        "상당한 난제로 판단",
    ),
    2345: (
        "의 임무에 실패하였습니다\n"
        "면목이 없습니다",
    ),
    2346: (
        "의 임무는 실패로 끝나",
        "인가…\n어쩔 수",
    ),
    2347: (
        "의 임무에 실패하였습니다\n"
        "소인도 부상을 입어…\n"
        "면목이 없습니다",
    ),
    2348: (
        "우선 가신들이 건의를 올릴 수 있도록\n"
        "공략할 세력을 정해",
    ),
    2349: (
        "공략 방침에서 공략 대상을 정해 두",
        "\n그러면 공략을 실현하기 위한 여러 준비를\n"
        "가신들이 제안",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
JP_GAP_DIVERGENCES = {2332, 2333, 2335, 2337, 2344, 2346, 2349}
STATIC_RECORD_IDS = {2331, 2334, 2336, 2338, 2339, 2340, 2341}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2337:0",
    "15:2339:0",
    "15:2340:0",
    "15:2346:1",
    "15:2347:0",
}
ARCHIVE_DIGESTS = {
    "base_jp": "D5015EBABEBE5453C220FF7801CF84CA08D175CC1D0FCE4BA88A207CF752A22A",
    "base_current": "FE3D55297203BCD70E18F9089C4B690436F0BBDA6D5BD46604A5897EB2585F0D",
    "base_sc": "7890537BDC690B3728A81808C2D236E81571B1D5CC0651898A1ED0339AED7590",
    "base_tc": "25FD4E944D24D15D92C69DE18383A456CFA166644D33FC357A97A82E0F2899F1",
    "pk_jp": "6D96B3F586B1C052957DF0FF0BA801EE89033BA556916AEA77CCC667558FB0E6",
    "pk_current": "4362AC0867E3A2040868C93EB0722C1ED1E686D3734D568351B611C24EBE4A66",
    "pk_sc": "7890537BDC690B3728A81808C2D236E81571B1D5CC0651898A1ED0339AED7590",
    "pk_tc": "25FD4E944D24D15D92C69DE18383A456CFA166644D33FC357A97A82E0F2899F1",
    "pk_en": "70D0B6A9A365FEDFFF6F987D0D4376449ABFE3195069FC8976B3C69FE84A7A05",
}
BASIS = (
    "review_queue_base_msggame_B118_B_pristine_base_pc_jp_authoritative_"
    "territory_development_war_goal_strategy_assessment_mission_failure_"
    "and_invasion_policy_guidance_with_exact_plus31_pk_mapping_aggregate_"
    "pc_jp_en_sc_tc_record_digests_dynamic_morphology_samples_current_line_"
    "counts_and_project_ellipsis_preserved_no_korean_build_authority"
)


def subset_digest(
    records: dict[tuple[int, int], Any],
    record_ids: tuple[int, ...],
    offset: int,
) -> str:
    digest = hashlib.sha256()
    for record_id in record_ids:
        record = records[(15, record_id + offset)]
        digest.update(struct.pack("<II", record_id, len(record.data)))
        digest.update(record.data)
    return digest.hexdigest().upper()


def literal_texts(
    records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(records[(15, record_id)])
    )


def gap_bytes(
    records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[bytes, ...]:
    return UTIL.record_gaps(records[(15, record_id)])


def build_compact_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    pk_record_map: dict[int, int],
    archive_digests: dict[str, str],
    jp_gap_divergences: set[int],
    static_record_ids: set[int],
    ellipsis_coordinates: set[str],
    basis: str,
    semantic_assertions: Callable[[dict[str, str]], None],
) -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    archives = {
        "base_jp": (base.pristine_archive, 0),
        "base_current": (base.current_archive, 0),
        "base_sc": (base.context_archives["SC"], 0),
        "base_tc": (base.context_archives["TC"], 0),
        "pk_jp": (pk.pristine_archive, 31),
        "pk_current": (pk.current_archive, 31),
        "pk_sc": (pk.context_archives["SC"], 31),
        "pk_tc": (pk.context_archives["TC"], 31),
        "pk_en": (pk.context_archives["EN"], 31),
    }
    records_by_label = {
        label: ENGINE.archive_records(archive)
        for label, (archive, _offset) in archives.items()
    }
    record_ids = tuple(record_arities)
    if set(pk_record_map) != set(record_ids) or {
        pk_record_map[record_id] - record_id for record_id in record_ids
    } != {31}:
        raise RuntimeError(f"segment {segment} Base-to-PK mapping drifted")
    if set(archive_digests) != set(archives):
        raise RuntimeError(f"segment {segment} archive digest universe drifted")
    for label, (_archive, offset) in archives.items():
        actual = subset_digest(records_by_label[label], record_ids, offset)
        if actual != archive_digests[label]:
            raise RuntimeError(f"segment {segment} {label} corpus drifted")

    base_jp = records_by_label["base_jp"]
    current = records_by_label["base_current"]
    pk_jp = records_by_label["pk_jp"]
    actual_gap_divergences: set[int] = set()
    for record_id, arity in record_arities.items():
        mapped_id = pk_record_map[record_id]
        if (
            len(literal_texts(base_jp, record_id)) != arity
            or len(literal_texts(current, record_id)) != arity
            or literal_texts(base_jp, record_id)
            != literal_texts(pk_jp, mapped_id)
        ):
            raise RuntimeError(
                f"segment {segment} JP literal mapping drifted: {record_id}"
            )
        if gap_bytes(base_jp, record_id) != gap_bytes(current, record_id):
            raise RuntimeError(
                f"segment {segment} pristine/current gap drifted: {record_id}"
            )
        if gap_bytes(base_jp, record_id) != gap_bytes(pk_jp, mapped_id):
            actual_gap_divergences.add(record_id)
        for language in ("sc", "tc"):
            base_context = records_by_label[f"base_{language}"]
            pk_context = records_by_label[f"pk_{language}"]
            if (
                literal_texts(base_context, record_id)
                != literal_texts(pk_context, mapped_id)
                or gap_bytes(base_context, record_id)
                != gap_bytes(pk_context, mapped_id)
            ):
                raise RuntimeError(
                    f"segment {segment} {language.upper()} mapping drifted: "
                    f"{record_id}"
                )
        if not any(
            text.strip()
            for text in literal_texts(records_by_label["pk_en"], mapped_id)
        ):
            raise RuntimeError(
                f"segment {segment} PK EN context became empty: {record_id}"
            )
    if actual_gap_divergences != jp_gap_divergences:
        raise RuntimeError(f"segment {segment} JP gap divergence drifted")

    translations = UTIL.resolved_translations(current, raw_translations)
    expected_coordinates = {
        f"15:{record_id}:{literal_id}"
        for record_id, arity in record_arities.items()
        for literal_id in range(arity)
    }
    if set(translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} coordinate universe drifted")
    actual_ellipsis = {
        coordinate
        for coordinate in expected_coordinates
        if "…" in literal_texts(
            current,
            int(coordinate.split(":")[1]),
        )[int(coordinate.split(":")[2])]
    }
    if actual_ellipsis != ellipsis_coordinates:
        raise RuntimeError(f"segment {segment} ellipsis universe drifted")
    for coordinate, translation in translations.items():
        _block, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(current, record_id)[literal_id]
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {segment} layout signature drifted: {coordinate}"
            )
        if (
            "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
            or "…" in translation.replace("……", "")
        ):
            raise RuntimeError(
                f"segment {segment} text residue drifted: {coordinate}"
            )
    semantic_assertions(translations)
    UTIL.assert_isolated_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        record_arities=record_arities,
    )

    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        _block, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", 15, record_id, literal_id)
        ]
        is_static = record_id in static_record_ids
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target[
                "current_ko_utf16le_sha256"
            ],
            "translation": translation,
            "semantic_review": "approved",
            "scope_classification": (
                "retranslated" if is_static else "runtime_fragment_pending"
            ),
            "layout_review": "unchanged_from_current",
            "runtime_review": "not_required" if is_static else "pending",
            "basis": basis,
            "historic_korean_used": False,
            "switch_korean_used": False,
        }
        base_operands = SUPPORT.morphology_operands(
            gap_bytes(current, record_id)[literal_id + 1].hex()
        )
        mapped_id = pk_record_map[record_id]
        pk_operands = SUPPORT.morphology_operands(
            gap_bytes(pk_jp, mapped_id)[literal_id + 1].hex()
        )
        if base_operands or pk_operands:
            row["runtime_morphology_samples"] = {
                "base": [
                    {
                        "opcode": (
                            b"\x01\x43" + struct.pack("<I", operand)
                        ).hex().upper(),
                        "terminal_literals": list(
                            SUPPORT.morphology_terminal_literals(
                                current,
                                operand,
                            )
                        ),
                    }
                    for operand in base_operands
                ],
                "pk": [
                    {
                        "mapped_record_id": mapped_id,
                        "opcode": (
                            b"\x01\x43" + struct.pack("<I", operand)
                        ).hex().upper(),
                        "terminal_literals": list(
                            SUPPORT.morphology_terminal_literals(
                                records_by_label["pk_current"],
                                operand,
                            )
                        ),
                    }
                    for operand in pk_operands
                ],
            }
        rows.append(row)
    return prepared, translations, rows


def assert_semantics(translations: dict[str, str]) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "영내",
        "석고",
        "시설 확충",
        "합전",
        "다이묘",
        "주군 가문",
        "건의",
        "공략 방침",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 986 required meaning drifted: {required}")
    for forbidden in (
        "당가",
        "주가",
        "영지의 각 성",
        "부인하면",
        "똑똑히",
        "、",
        "。",
    ):
        if forbidden in joined:
            raise RuntimeError(f"segment 986 forbidden wording retained: {forbidden}")
    if not TRANSLATIONS_BY_RECORD[2332][0].endswith("갖춰질 것"):
        raise RuntimeError("segment 986 self-sufficiency morphology stem drifted")
    self_sufficiency = {
        f"{TRANSLATIONS_BY_RECORD[2332][0]}{ending}".splitlines()[-1]
        for ending in ("이겠지요", "이리라", "이겠지")
    }
    if self_sufficiency != {
        "절로 갖춰질 것이겠지요",
        "절로 갖춰질 것이리라",
        "절로 갖춰질 것이겠지",
    }:
        raise RuntimeError("segment 986 self-sufficiency assembly drifted")
    if not TRANSLATIONS_BY_RECORD[2348][0].endswith("정해"):
        raise RuntimeError("segment 986 invasion-target request stem drifted")


def main() -> int:
    prepared, translations, rows = build_compact_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        archive_digests=ARCHIVE_DIGESTS,
        jp_gap_divergences=JP_GAP_DIVERGENCES,
        static_record_ids=STATIC_RECORD_IDS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 986 decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S986",
                "source_literal_count": 21,
                "decision_count": len(rows),
                "retranslated": len(STATIC_RECORD_IDS),
                "runtime_fragment_pending": len(rows) - len(STATIC_RECORD_IDS),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": sorted(
                    JP_GAP_DIVERGENCES
                ),
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "lf_count": sum(
                    text.count("\n") for text in translations.values()
                ),
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
