#!/usr/bin/env python3
"""Build Base authoring segment 998 decisions for the v0.15.0 retranslation."""

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

import build_base_batch001_segment991 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
UTIL = COMMON.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B119_S998.private.v1.jsonl"
)
SEGMENT = 998
RecordKey = tuple[int, int]

TRANSLATIONS_BY_RECORD: dict[RecordKey, tuple[str, ...]] = {
    (16, 53): (
        "준비가 갖춰지면 이미 이긴 것이나 다름없다\n"
        "황색 부대여, 이제 승리하자",
    ),
    (16, 54): ("군사로서의 지략을\n세상에 보이리라",),
    (16, 55): (
        "오래 궁리하고 더디게 결단한다\n"
        "매사에 빈틈이 없어야 하리라",
    ),
    (16, 56): (
        "주군 가문에 힘이 없으면\n"
        "통째로 삼켜지는 것이 세상 이치지",
    ),
    (16, 57): (
        "목숨을 아끼지 않을 각오는\n"
        "언제나 내 마음속에 있다",
    ),
    (16, 58): ("체스토, 서둘러라!\n싸움이 코앞이다!",),
    (16, 59): ("사쓰마의 방식을\n내가 세상에 보이리라",),
    (16, 60): (
        "사람이 곧 성이요, 사람이 곧 돌담이다…\n"
        "사람과 정으로 세상은 돌아간다",
    ),
    (16, 61): ("당대 공명의 지략을\n보여 드리겠습니다",),
    (16, 62): ("이 외눈은\n어떠한 기회도 놓치지 않는다",),
    (16, 63): ("도사의 군법이다!\n어서 갑옷을 가져오라!",),
    (16, 64): ("운은 하늘에, 갑옷은 가슴에\n공훈은 발에 달려 있다",),
    (16, 65): (
        "길 위의 눈은 녹을 때까지\n"
        "자리를 옮기지 않는 법",
    ),
    (16, 66): (
        "녹수응온, 백성을 지키기 위해\n"
        "우리가 존재하는 것이다",
    ),
    (16, 67): ("큰 염주를 들어라!\n싸움을 앞두고 피를 끓여라!",),
    (16, 68): (
        "인생은 무거운 짐을 지고\n"
        "먼 길을 가는 것과 같도다…",
    ),
    (16, 69): ("계책이 많으면 이기고\n적으면 질 뿐이다",),
    (16, 70): ("계책으로 승패를 가르는 것은\n오히려 쉬운 일이다",),
    (16, 71): (
        "마음 위에 칼날을 얹고\n"
        "주군을 위해 진력할 뿐",
    ),
    (16, 72): ("어떤 주군을 섬기든\n내 신조는 변하지 않는다",),
    (16, 73): (
        "마음 가는 대로, 파격적으로 산다\n"
        "그래야 인생이지",
    ),
    (16, 74): (
        "지행과 정은 수레의 두 바퀴\n"
        "그만큼 다루기 어려운 법",
    ),
    (16, 75): ("하늘이여, 내게 칠난팔고를\n내려 주소서…",),
}
RAW_TRANSLATIONS = {
    f"{block_id}:{record_id}:{literal_id}": translation
    for (block_id, record_id), translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    key: len(translations)
    for key, translations in TRANSLATIONS_BY_RECORD.items()
}
PK_RECORD_MAP = {key: key for key in RECORD_ARITIES}
EXPECTED_BASE_JP = {
    (16, 53): ("備え整えば勝利も同然\n黄備え、いざ勝たん",),
    (16, 54): ("軍師たるの謀才\n世に示すべし",),
    (16, 55): ("長く思案し遅く決断す\n万事、疎漏なかるべし",),
    (16, 56): ("主家に力なくば\n丸呑みされるが道理よ",),
    (16, 57): ("不惜身命の思い\n常に我が心中に",),
    (16, 58): ("チェスト、急げ！\n戦は近いぞ！",),
    (16, 59): ("薩摩が流儀\n我が世に示さん",),
    (16, 60): ("人は城、人は石垣…\n人と情とで世は回る",),
    (16, 61): ("今孔明の知略\nご覧に入れましょう",),
    (16, 62): ("我が独眼は\nいかな機も見逃さぬ",),
    (16, 63): ("土佐の軍法である！\n急ぎ鎧を持参せい！",),
    (16, 64): ("運は天に、鎧は胸に\n手柄は足にあり",),
    (16, 65): ("道の雪は消えるまで\n居場所を変えぬもの",),
    (16, 66): ("禄寿応穏、民を守りて\n我らが在るのだ",),
    (16, 67): ("大数珠を持て！\n戦に血をたぎらせい！",),
    (16, 68): ("人生は重荷を負いて\n遠き道を行くが如し…",),
    (16, 69): ("謀多きは勝ち\n少なきは負けるのみ",),
    (16, 70): ("謀にて勝敗を決すは\nむしろ容易きこと",),
    (16, 71): ("心の上に刃を置きて\n主がために尽くすのみ",),
    (16, 72): ("いかな主に仕えようと\n己が在り方は不変なり",),
    (16, 73): ("好きに生き、傾く\nそれでこそ人生よ",),
    (16, 74): ("知行と情とは車の両輪\n難しきものにて",),
    (16, 75): ("天よ、我に七難八苦を\n与えたまえ…",),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    (16, 53): ("備え整わば勝利も同然\n黄備え、いざ勝たん",),
    (16, 75): ("天よ、どうか我に\n七難八苦を与えたまえ",),
}
STATIC_GAPS = ("", "050505")
EXPECTED_BASE_GAPS = {key: STATIC_GAPS for key in RECORD_ARITIES}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
ARCHIVE_DIGESTS = {
    "base_jp": "5316E1D9B05145C29E2A1A3D3DC12E2B31C75081F96BB8795F1097EFB980E2AD",
    "base_current": "2A6129E053135F115A9A0450333E18066BF35B3CFE14ED011E430E41C935AFA2",
    "base_sc": "55A573727169B3621913228A3270DF07404C2E0129BE29E780FA97AD6043D1C5",
    "base_tc": "7A25696CDE3439625D2049F605AC9EA81C487F98B3138A63AE4A396EFFF77A2F",
    "pk_jp": "7E2BAA514C971E3DD419CFEA39BF9B8845C7D9574DF95D31BE14109B4F1E4327",
    "pk_current": "AFEAEA6C8D1D49DE93D8076BD06BB427CED895B23664AB15E33A4334CB037AA7",
    "pk_sc": "55A573727169B3621913228A3270DF07404C2E0129BE29E780FA97AD6043D1C5",
    "pk_tc": "7A25696CDE3439625D2049F605AC9EA81C487F98B3138A63AE4A396EFFF77A2F",
    "pk_en": "7D633B7204BCE70BDC5D8544846850E35A85C62174AAD7DA245CB520318A05F8",
}
PK_EN_VISIBLE_KEYS = set(RECORD_ARITIES)
CURRENT_ELLIPSIS_COORDINATES = {
    "16:60:0",
    "16:68:0",
    "16:75:0",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_COORDINATES = set(RAW_TRANSLATIONS)
HISTORICAL_EVIDENCE_URLS = {
    "チェスト": (
        "https://www.bunka.go.jp/seisaku/bunkazai/joseishien/"
        "syokubunka_story/pdf/94054901_23.pdf"
    ),
    "禄寿応穏": (
        "https://ch.kanagawa-museum.jp/uploads/caption-20160502.pdf"
    ),
    "傾く": (
        "https://www.touken-world.jp/history/history-important-word/"
        "izumo-no-okuni/"
    ),
    "知行": "https://kotobank.jp/word/%E7%9F%A5%E8%A1%8C-95952",
    "七難八苦": (
        "https://crd.ndl.go.jp/reference/entry/index.php?"
        "id=1000011880&page=ref_view"
    ),
}
BASIS = (
    "review_queue_base_msggame_B119_C_pristine_local_pc_jp_authoritative_"
    "fixed_officer_maxims_satsuma_chesto_rokujuoon_historical_clan_"
    "service_kabuku_chigyo_and_shichinan_hakku_with_identity_base_pk_"
    "block16_mapping_exact_base_pk_jp_sc_tc_and_pk_en_subset_digests_"
    "explicit_pk_wording_divergence_16_53_16_75_current_line_counts_"
    "protected_signatures_project_ellipsis_and_static_retranslated_only_"
    "dictionary_museum_cultural_agency_and_ndl_evidence_no_korean_build_"
    "authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: RecordKey,
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_hexes(
    records: dict[tuple[int, int], Any],
    key: RecordKey,
) -> tuple[str, ...]:
    if not ENGINE.parse_record_literals(records[key]):
        return ()
    return tuple(gap.hex().upper() for gap in UTIL.record_gaps(records[key]))


def subset_digest(
    records: dict[tuple[int, int], Any],
    keys: tuple[RecordKey, ...],
) -> str:
    digest = hashlib.sha256()
    for block_id, record_id in keys:
        data = records[(block_id, record_id)].data
        digest.update(struct.pack("<III", block_id, record_id, len(data)))
        digest.update(data)
    return digest.hexdigest().upper()


def assert_general_overlay_roundtrip(
    prepared: Any,
    *,
    segment: int,
    translations: dict[str, str],
    record_arities: dict[RecordKey, int],
) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements: dict[tuple[int, int, int], str] = {}
    reverse: dict[tuple[int, int, int], str] = {}
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse[key] = ENGINE.parse_record_literals(
            current_records[key[:2]]
        )[literal_id].text
    rebuilt = ENGINE.rebuild_packed_with_literals(
        base.current_blob,
        replacements,
    )
    rebuilt_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(rebuilt).archive
    )
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError(f"segment {segment} Base record count drifted")
    targets = set(record_arities)
    for key, current_record in current_records.items():
        if key not in targets and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(
                f"segment {segment} changed an out-of-scope record: {key}"
            )
    for key in targets:
        if UTIL.record_gaps(rebuilt_records[key]) != UTIL.record_gaps(
            current_records[key]
        ):
            raise RuntimeError(
                f"segment {segment} changed target skeleton: {key}"
            )
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(
            rebuilt_records[key[:2]]
        )[key[2]].text
        if actual != translation:
            raise RuntimeError(
                f"segment {segment} UTF-16 round-trip failed: {key}"
            )
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse)
    if reversed_blob != base.current_blob:
        raise RuntimeError(
            f"segment {segment} reverse overlay is not byte-exact"
        )


def build_general_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[RecordKey, int],
    pk_record_map: dict[RecordKey, RecordKey],
    expected_base_jp: dict[RecordKey, tuple[str, ...]],
    expected_pk_jp: dict[RecordKey, tuple[str, ...]],
    base_gaps: dict[RecordKey, tuple[str, ...]],
    current_gaps: dict[RecordKey, tuple[str, ...]],
    pk_jp_gaps: dict[RecordKey, tuple[str, ...]],
    archive_digests: dict[str, str],
    pk_en_visible_keys: set[RecordKey],
    ellipsis_coordinates: set[str],
    excluded_nonvisible_coordinates: dict[str, str],
    static_coordinates: set[str],
    basis: str,
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]],
        None,
    ],
) -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    dict[str, dict[tuple[int, int], Any]],
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    archives = {
        "base_jp": base.pristine_archive,
        "base_current": base.current_archive,
        "base_sc": base.context_archives["SC"],
        "base_tc": base.context_archives["TC"],
        "pk_jp": pk.pristine_archive,
        "pk_current": pk.current_archive,
        "pk_sc": pk.context_archives["SC"],
        "pk_tc": pk.context_archives["TC"],
        "pk_en": pk.context_archives["EN"],
    }
    records_by_label = {
        label: ENGINE.archive_records(archive)
        for label, archive in archives.items()
    }
    base_keys = tuple(record_arities)
    pk_keys = tuple(pk_record_map[key] for key in base_keys)
    expected_universe = set(record_arities)
    for label, values in (
        ("pk map", pk_record_map),
        ("Base JP", expected_base_jp),
        ("PK JP", expected_pk_jp),
        ("Base gaps", base_gaps),
        ("current gaps", current_gaps),
        ("PK gaps", pk_jp_gaps),
    ):
        if set(values) != expected_universe:
            raise RuntimeError(f"segment {segment} {label} universe drifted")
    if set(archive_digests) != set(archives):
        raise RuntimeError(f"segment {segment} archive universe drifted")
    for label, records in records_by_label.items():
        keys = pk_keys if label.startswith("pk_") else base_keys
        actual = subset_digest(records, keys)
        if actual != archive_digests[label]:
            raise RuntimeError(f"segment {segment} {label} corpus drifted")

    source_records = records_by_label["base_jp"]
    current_records = records_by_label["base_current"]
    pk_source_records = records_by_label["pk_jp"]
    expected_coordinates: set[str] = set()
    actual_ellipsis: set[str] = set()
    for key, arity in record_arities.items():
        mapped = pk_record_map[key]
        if literal_texts(source_records, key) != expected_base_jp[key]:
            raise RuntimeError(
                f"segment {segment} Base JP literal drifted: {key}"
            )
        if literal_texts(pk_source_records, mapped) != expected_pk_jp[key]:
            raise RuntimeError(
                f"segment {segment} PK JP literal drifted: {key}/{mapped}"
            )
        source_literals = ENGINE.parse_record_literals(source_records[key])
        current_literals = ENGINE.parse_record_literals(current_records[key])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(
                f"segment {segment} source/current arity drifted: {key}"
            )
        if gap_hexes(source_records, key) != base_gaps[key]:
            raise RuntimeError(
                f"segment {segment} Base pristine skeleton drifted: {key}"
            )
        if gap_hexes(current_records, key) != current_gaps[key]:
            raise RuntimeError(
                f"segment {segment} Base current skeleton drifted: {key}"
            )
        if gap_hexes(pk_source_records, mapped) != pk_jp_gaps[key]:
            raise RuntimeError(
                f"segment {segment} PK pristine skeleton drifted: "
                f"{key}/{mapped}"
            )
        for language in ("sc", "tc"):
            base_context = records_by_label[f"base_{language}"]
            pk_context = records_by_label[f"pk_{language}"]
            if (
                literal_texts(base_context, key)
                != literal_texts(pk_context, mapped)
                or gap_hexes(base_context, key)
                != gap_hexes(pk_context, mapped)
            ):
                raise RuntimeError(
                    f"segment {segment} {language.upper()} mapping drifted: "
                    f"{key}/{mapped}"
                )
        pk_en_texts = literal_texts(records_by_label["pk_en"], mapped)
        pk_en_visible = any(
            ENGINE.is_visible_translation_candidate(text)
            for text in pk_en_texts
        )
        if pk_en_visible != (key in pk_en_visible_keys):
            raise RuntimeError(
                f"segment {segment} PK EN visibility drifted: {key}/{mapped}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in excluded_nonvisible_coordinates:
                expected = excluded_nonvisible_coordinates[coordinate]
                if (
                    source_literal.text != expected
                    or current_literal.text != expected
                    or ENGINE.is_visible_translation_candidate(
                        source_literal.text
                    )
                    or ENGINE.is_visible_translation_candidate(
                        current_literal.text
                    )
                    or coordinate in raw_translations
                ):
                    raise RuntimeError(
                        f"segment {segment} nonvisible literal drifted: "
                        f"{coordinate}"
                    )
                continue
            if not ENGINE.is_visible_translation_candidate(
                source_literal.text
            ) or not ENGINE.is_visible_translation_candidate(
                current_literal.text
            ):
                raise RuntimeError(
                    f"segment {segment} unexpected blank target: {coordinate}"
                )
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_ellipsis.add(coordinate)
    if set(raw_translations) != expected_coordinates:
        raise RuntimeError(
            f"segment {segment} raw coordinate universe drifted"
        )
    translations = UTIL.resolved_translations(
        current_records,
        raw_translations,
    )
    if set(translations) != expected_coordinates:
        raise RuntimeError(
            f"segment {segment} resolved coordinate universe drifted"
        )
    if actual_ellipsis != ellipsis_coordinates:
        raise RuntimeError(
            f"segment {segment} ellipsis universe drifted"
        )
    if not static_coordinates.issubset(expected_coordinates):
        raise RuntimeError(
            f"segment {segment} static coordinate universe drifted"
        )
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
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
        raw = raw_translations[coordinate]
        if coordinate in ellipsis_coordinates and (
            not raw.count("…")
            or translation.count("…") != raw.count("…") * 2
        ):
            raise RuntimeError(
                f"segment {segment} ellipsis pair drifted: {coordinate}"
            )
    semantic_assertions(source_records, raw_translations, translations)
    assert_general_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        record_arities=record_arities,
    )

    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        is_static = coordinate in static_coordinates
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": (
                    "retranslated"
                    if is_static
                    else "runtime_fragment_pending"
                ),
                "layout_review": "unchanged_from_current",
                "runtime_review": (
                    "not_required" if is_static else "pending"
                ),
                "basis": basis,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows, records_by_label


def annotate_general_morphology(
    rows: list[dict[str, object]],
    *,
    record_arities: dict[RecordKey, int],
    pk_record_map: dict[RecordKey, RecordKey],
    base_gaps: dict[RecordKey, tuple[str, ...]],
    pk_gaps: dict[RecordKey, tuple[str, ...]],
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    expected_base: dict[int, tuple[str, ...]],
    expected_pk: dict[int, tuple[str, ...]],
) -> None:
    observed_base = {
        operand
        for key in record_arities
        for gap in base_gaps[key]
        for operand in SUPPORT.morphology_operands(gap)
    }
    observed_pk = {
        operand
        for key in record_arities
        for gap in pk_gaps[key]
        for operand in SUPPORT.morphology_operands(gap)
    }
    if observed_base != set(expected_base) or observed_pk != set(expected_pk):
        raise RuntimeError("general morphology operand universe drifted")
    for records, expected, side in (
        (records_by_label["base_current"], expected_base, "Base"),
        (records_by_label["pk_current"], expected_pk, "PK"),
    ):
        for operand, terminals in expected.items():
            actual = SUPPORT.morphology_terminal_literals(records, operand)
            if actual != terminals:
                raise RuntimeError(
                    f"{side} morphology terminal corpus drifted: {operand}"
                )
    rows_by_coordinate = {
        str(row["coordinate"]): row for row in rows
    }
    for key, arity in record_arities.items():
        for literal_id in range(arity):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate not in rows_by_coordinate:
                continue
            base_operands = SUPPORT.morphology_operands(
                base_gaps[key][literal_id + 1]
            )
            mapped = pk_record_map[key]
            pk_operands: tuple[int, ...] = ()
            if literal_id + 1 < len(pk_gaps[key]):
                pk_operands = SUPPORT.morphology_operands(
                    pk_gaps[key][literal_id + 1]
                )
            if not base_operands and not pk_operands:
                continue
            rows_by_coordinate[coordinate]["runtime_morphology_samples"] = {
                "base": [
                    {
                        "opcode": (
                            b"\x01\x43" + struct.pack("<I", operand)
                        ).hex().upper(),
                        "terminal_literals": list(expected_base[operand]),
                    }
                    for operand in base_operands
                ],
                "pk": [
                    {
                        "mapped_coordinate": f"{mapped[0]}:{mapped[1]}",
                        "opcode": (
                            b"\x01\x43" + struct.pack("<I", operand)
                        ).hex().upper(),
                        "terminal_literals": list(expected_pk[operand]),
                    }
                    for operand in pk_operands
                ],
            }


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if any(key != mapped for key, mapped in PK_RECORD_MAP.items()):
        raise RuntimeError("segment 998 identity Base-to-PK mapping drifted")
    divergences = {
        key
        for key in RECORD_ARITIES
        if EXPECTED_BASE_JP[key] != EXPECTED_PK_JP[key]
    }
    if divergences != {(16, 53), (16, 75)}:
        raise RuntimeError("segment 998 PK wording divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "황색 부대",
        "주군 가문",
        "체스토",
        "사쓰마",
        "녹수응온",
        "지행",
        "칠난팔고",
        "파격적으로",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 998 required terminology drifted: {required}"
            )
    for forbidden in ("주가", "어서, 서둘러라", "지행과 인정"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 998 forbidden wording retained: {forbidden}"
            )
    if len(HISTORICAL_EVIDENCE_URLS) != 5:
        raise RuntimeError("segment 998 evidence registry drifted")
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 998 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows, _records = build_general_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        archive_digests=ARCHIVE_DIGESTS,
        pk_en_visible_keys=PK_EN_VISIBLE_KEYS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        static_coordinates=STATIC_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 998 validated count drifted")
    if any(
        row["scope_classification"] != "retranslated"
        or row["runtime_review"] != "not_required"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 998 classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B119_S998",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": len(rows),
                "runtime_fragment_pending": 0,
                "explicit_pk_mapping": {
                    f"{key[0]}:{key[1]}": (
                        f"{mapped[0]}:{mapped[1]}"
                    )
                    for key, mapped in PK_RECORD_MAP.items()
                },
                "base_pk_jp_literal_divergence_records": [
                    "16:53",
                    "16:75",
                ],
                "base_pk_jp_gap_divergence_records": [],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(
                    CURRENT_ELLIPSIS_COORDINATES
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
