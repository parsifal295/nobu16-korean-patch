#!/usr/bin/env python3
"""Build source-redacted PK B044 segment 1145 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch043_segment1142.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B044_S1145.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B044_S1143.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B044_S1144.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1145
QUEUE_BATCH_ID = "pk_msggame-B044"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_FIRST_RECORD = 4263
QUEUE_LAST_RECORD = 4369
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4340:0 6:4340:1
    6:4341:0 6:4341:1
    6:4342:0 6:4342:1
    6:4343:0 6:4343:1
    6:4344:0 6:4344:1
    6:4345:0 6:4345:1
    6:4346:0 6:4346:1
    6:4347:0 6:4347:1 6:4347:2
    6:4348:0 6:4348:1 6:4348:2
    6:4349:0 6:4349:1
    6:4350:0 6:4350:1
    6:4351:0 6:4351:1
    6:4352:0 6:4352:1 6:4352:2
    6:4353:0 6:4353:1
    6:4354:0 6:4354:1
    6:4355:0 6:4355:1
    6:4356:0 6:4356:1
    6:4357:0
    6:4358:0
    6:4359:0 6:4359:1
    6:4360:0
    6:4361:0
    6:4362:0
    6:4363:0 6:4363:1 6:4363:2
    6:4364:0
    6:4365:0
    6:4366:0 6:4366:1
    6:4367:0 6:4367:1
    6:4368:0 6:4368:1 6:4368:2
    """.split()
)
TRANSLATIONS = {
    "6:4340:0": "우리의",
    "6:4340:1": "을 본가에 도입해\n한층 더 큰 발전을 이루리라!",
    "6:4341:0": "주군께서 내리신 땅을\n끝까지 지켜 내는 것이야말로 무사의 영예다",
    "6:4341:1": "!",
    "6:4342:0": "예로부터 이어 온 우리 가문의 이름을\n온 천하에 떨치리라",
    "6:4342:1": "!",
    "6:4343:0": "신불의 가르침으로\n나라의 정사를 바로잡으리라",
    "6:4343:1": "!",
    "6:4344:0": "아미타불도 돈으로 빛나는 법!\n내 장사 수완으로 이익을 가져오리라",
    "6:4344:1": "!",
    "6:4345:0": "본가의 무예를 갈고닦도록\n내 유파의 검술을 전수하리라",
    "6:4345:1": "!",
    "6:4346:0": "백성은 나라보다 귀한 법…\n백성의 힘으로 나라를 풍요롭게 하리라",
    "6:4346:1": "!",
    "6:4347:0": "전장에서 쓰일 병법을\n병졸들에게까지 가르칠 이는:",
    "6:4347:1": ", 직접 훈련",
    "6:4347:2": "！",
    "6:4348:0": "관료로 나설 이는:",
    "6:4348:1": "!\n그 역량으로 정사를 더욱 훌륭하게 개선",
    "6:4348:2": "！",
    "6:4349:0": "고향의 닌자 무리를 포섭해 본진까지—",
    "6:4349:1": "\n모략을 펼칠 때 도움이 될 것이오…",
    "6:4350:0": "항구에 해적의 성채를 마련",
    "6:4350:1": "!\n유사시에는 힘이 되어 드리겠소",
    "6:4351:0": "의 이름 아래 사람에 귀천은 없다!\n재능 있는 자는 모두 차별 없이 등용",
    "6:4351:1": "！",
    "6:4352:0": "너희는 모두 나의 심복이다",
    "6:4352:1": "!\n각자의 장기를 마음껏 살려 보아라",
    "6:4352:2": "!",
    "6:4353:0": "어찌 되었든 좋은 일은 속전속결",
    "6:4353:1": "!\n모든 일은 위타천처럼 재빨리 끝내라!",
    "6:4354:0": "한마음으로 뭉친 군세는 강하다!\n아무리 병력 차가 커도 결코 지지 않으리라",
    "6:4354:1": "!",
    "6:4355:0": "무사도란 죽음을 무릅쓰고 미친 듯 싸우는 것!\n궁지에서야말로 온 힘을 다하리라",
    "6:4355:1": "!",
    "6:4356:0": "히타치의 기두란 바로 ‘",
    "6:4356:1": "’을 이른다!\n월환선 깃발 아래 모두 모여라!",
    "6:4357:0": "백성이 있기에 이 몸도 있다!\n지·인·용의 삼덕으로 정사에 임하리라!",
    "6:4358:0": "의 길은 늘 신의와 함께하리라!\n어떤 때에도 정도를 걸으리라!",
    "6:4359:0": "이 땅의 백성을 향사로 등용하리라!\n모두 함께 이 땅을 일으켜 세우자",
    "6:4359:1": "!",
    "6:4360:0": "사가라 가문의 힘을 보여 주자!",
    "6:4361:0": "막대한 부를 거머쥐기 위해\n지금이야말로 바닷길을 열 때다!",
    "6:4362:0": "고귀한 본가의 이름을 천하에 떨쳐라!\n주변 다이묘들이 우러러볼 대상",
    "6:4363:0": "일족의 힘으로 천하를 다스리리라!\n",
    "6:4363:1": "의 이름을 온 세상에 널리 알릴 때",
    "6:4363:2": "！",
    "6:4364:0": "의 위광으로 일본을 밝히리라!\n차오르는 달을 가로막는 자는 용서하지 않으리라!",
    "6:4365:0": "의 나라라면 강해야 한다\n수호로서 백성과 가신을 지탱하리라!",
    "6:4366:0": "상업을 지배하는 자가 천하를 지배한다!\n한 푼의 돈도 결코 소홀히 하지 않으리라",
    "6:4366:1": "!",
    "6:4367:0": "우리는 진수대장군의 후예다!\n병사들이여, 두려워 말고 나아가라",
    "6:4367:1": "!",
    "6:4368:0": "망설임 없이 질풍처럼 몰아치는 것이 ‘",
    "6:4368:1": "’의 전법",
    "6:4368:2": "!\n겁먹은 적은 모조리 삼켜 버려라!",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = tuple(range(4340, 4369))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4340: 2, 4341: 2, 4342: 2, 4343: 2, 4344: 2,
    4345: 2, 4346: 2, 4347: 3, 4348: 3, 4349: 2,
    4350: 2, 4351: 2, 4352: 3, 4353: 2, 4354: 2,
    4355: 2, 4356: 2, 4357: 1, 4358: 1, 4359: 2,
    4360: 1, 4361: 1, 4362: 1, 4363: 3, 4364: 1,
    4365: 1, 4366: 2, 4367: 2, 4368: 3,
}
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = (
    4262, 4263, 4299, 4332, 4333, 4339, 4340, 4368, 4369, 4370,
)
SOURCE_CALL_ROOTS = (
    1, 82, 148, 424, 508, 514, 526, 538, 550, 568,
    610, 748, 814, 850, 1066, 1162,
)
CURRENT_CALL_ROOTS = (1, 148, 508, 526, 538, 568, 610, 850, 1066)

SPEAKER_STYLE = tuple(
    (record_id, "clan_policy_adoption_declaration")
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("main_house", "본가"),
    ("lord", "주군"),
    ("samurai_honor", "무사의 영예"),
    ("gods_and_buddha", "신불"),
    ("martial_arts", "무예"),
    ("military_strategy", "병법"),
    ("official", "관료"),
    ("ninja", "닌자"),
    ("pirate_fortress", "해적의 성채"),
    ("retainer", "심복"),
    ("swift_deity", "위타천"),
    ("warrior_way", "무사도"),
    ("hitachi_banner_chief", "히타치의 기두"),
    ("three_virtues", "지·인·용의 삼덕"),
    ("country_samurai", "향사"),
    ("regional_lord", "다이묘"),
    ("military_governor", "수호"),
    ("pacification_general", "진수대장군"),
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "A8F5DAA3CC50D65FAAF50AAB7AEEA95EACC6A2A58B720A1D3EAA4157A37E5179"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "AA485B60DED39CE848219435E49646F230C42244B55DA9DD5DBB43FE1FEF0887"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "952A8577AA3364DD6A525DD2F12B818F51AA07FA563BCDB8093C6B26C8D7815C"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "235A1FB759C5F9084C9AF1A098993422F439E095AC2584997D2EB6CE818871CF"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "4500630C61D084E79B851391D26FCE1EA28B75971A3710839449CF0B8676A164"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "E8B98C50891B6B005098380D095CF08EA24DCAE1C0F6BDE1362DEEB1ACF945C6"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "774DB0ABB89441E4E31182CB9CFE4148050FA61CA3B66A44D14C2E208F3117A2"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "DA5CCA52F00B06F1B10A1E4336275D29ECC9C9CC03728F2B20BC3D6B92E80270"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "1E70117FD27E7AA31B7FBE894C654D887290D242A5C6BFA41934A874C1355DEA"
)
EXPECTED_BOUNDARY_SHA256 = (
    "4EAD7C37BADAAA57D1E7F5BAE24E2C527D116C87BA788ADF9634CA2D1E1875D9"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "C41DDD947595B6A7D60AA7CBE2F6F9B9F172031362351F42DBA115B4012F78A7"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "ED10F5D2D9802BB501D0E18AF95F4B4EE31DD445ED2D92A78FE41F6D35FC2BA7"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "B9438B79EE7577E62BD39F3DB83EAE036685CA73C4CF9E21D6A72E73AE222898"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "6290A73E0CF10C9DC651B5452D33F903091208A40F220A35C54A2C8D6D1BAB5E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "3BE004611FCC68FB7DDD08E0811293F2AD12959588C5633A311F218C224CD4D4"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "FD232049730933C8214369060C1B7FE95AF62F3D8D81F0701971A90E33154479"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "FE83304F9A3F731C496A0D22D6255C63D2990A93F9AEC3C992791CCB3A423C1F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "6B334B0B99340263909D1203EBAF0C3EC60A6C9D69458708215E5B78940F0ED7"
)
EXPECTED_CHANGED_LITERAL_COUNT = 31

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete PC "
    "EN SC TC records across the full B044 queue are context only; all "
    "twenty-nine complete target records are PK-only policy-adoption "
    "declarations with no raw-exact, literal-exact or operand-masked "
    "complete Base source record; the completed Base corpus was searched "
    "and pinned as semantic comparison context, never as inherited runtime "
    "state; all fifty-six residual fragments form twenty-nine complete "
    "records; thirty-one wording, register, grammar and dynamic-assembly "
    "fragments are corrected while twenty-five reviewed fragments stay "
    "unchanged; period clan institutions, offices, warrior ethics, "
    "religion, commerce, martial training and regional-title terminology "
    "are reviewed; dynamic names, register calls, particles, punctuation, "
    "protected outer whitespace, line counts, both pristine and current "
    "call graphs, inline runtime tokens, deliberate source-current runtime "
    "gap differences, reverse-order overlay, reverse restoration, two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; Base runtime verification is not "
    "inherited and every PK fragment remains runtime pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
ALL_CALL_RE = re.compile(b"\x01([\x43\x4A])(.{4})", re.DOTALL)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1145_template",
        TEMPLATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {TEMPLATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_template()
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records


def patch_template_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    calls = tuple(
        int.from_bytes(match.group(1), "little")
        for value in gaps
        for match in DIRECT_CALL_RE.finditer(value)
    )
    tokens = tuple(
        value.hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )
    return calls, tokens


def mask_call_operands(record: Any) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01([\x43\x4A]).{4}",
            lambda match: b"\x01" + match.group(1) + b"\xFF" * 4,
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gap_bytes(record)
    )


def queue_evidence(
    prepared: Any,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[Any, ...]]:
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 104
        or len(visible) != 200
        or visible[0] != "6:4263:0"
        or visible[-1] != "6:4369:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B044 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:4333:0"
        or queue_slice[-1] != "6:4369:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 10
        or prefilled[:2] != ("6:4333:0", "6:4333:1")
        or prefilled[-2:] != ("6:4369:0", "6:4369:1")
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
        )
        for coordinate in prefilled
    )
    return visible, queue_slice, prefill_context


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice, prefill_context = queue_evidence(prepared)
    prefilled = tuple(row[0] for row in prefill_context)
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def context_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in CONTEXT_RECORD_IDS
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    return {
        "source_target": source_target,
        "current_target": current_target,
        "corpus": corpus,
        "gaps": gaps,
        "boundary": boundary,
        "controls": controls,
    }


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = context_evidence(records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        all(source == current for _, source, current in values["gaps"])
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    if not base_rows or any(
        row.get("semantic_review") != "approved"
        or row.get("runtime_review") not in {"verified", "not_required"}
        for row in base_rows.values()
    ):
        raise RuntimeError(f"segment {SEGMENT} Base completion drifted")
    raw_index: dict[bytes, list[tuple[int, int]]] = {}
    literal_index: dict[tuple[str, ...], list[tuple[int, int]]] = {}
    masked_index: dict[
        tuple[tuple[str, ...], tuple[str, ...]],
        list[tuple[int, int]],
    ] = {}
    for key, record in base_source.items():
        literals = literal_texts(base_source, key)
        raw_index.setdefault(record.data, []).append(key)
        literal_index.setdefault(literals, []).append(key)
        masked_index.setdefault(
            (literals, mask_call_operands(record)),
            [],
        ).append(key)
    search_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or tuple(
                f"6:{record_id}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
            != tuple(
                coordinate
                for coordinate in TARGET_COORDINATES
                if coordinate_key(coordinate)[1] == record_id
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} complete record drifted: {record_id}"
            )
        raw_matches = tuple(raw_index.get(source.data, ()))
        literal_matches = tuple(literal_index.get(source_literals, ()))
        masked_matches = tuple(
            masked_index.get(
                (source_literals, mask_call_operands(source)),
                (),
            )
        )
        if raw_matches or literal_matches or masked_matches:
            raise RuntimeError(
                f"segment {SEGMENT} unexpected complete Base donor: "
                f"{record_id}"
            )
        search_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                tuple(
                    value.hex().upper() for value in gap_bytes(source)
                ),
                raw_matches,
                literal_matches,
                masked_matches,
                len(base_rows),
            )
        )
        translations = tuple(
            TRANSLATIONS[f"6:{record_id}:{literal_id}"]
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        assembly_evidence.append(
            (
                record_id,
                source_literals,
                current_literals,
                tuple(
                    literal_texts(records_by_label[label], key)
                    for label in ("en", "sc", "tc")
                ),
                translations,
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "manual_multilingual_pk_only",
            )
        )
    return tuple(search_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    search, assembly = base_and_assembly_evidence(prepared, records_by_label)
    guarded_digest("Base search", search, EXPECTED_BASE_SEARCH_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[tuple[Any, ...], tuple[tuple[int, int], ...]]:
    pending: deque[tuple[int, int]] = deque([root])
    visited: set[tuple[int, int]] = set()
    edges: list[tuple[Any, ...]] = []
    terminals: list[tuple[int, int]] = []
    while pending:
        coordinate = pending.popleft()
        if coordinate in visited:
            continue
        if coordinate not in records:
            raise RuntimeError(
                f"segment {SEGMENT} missing call target: {coordinate}"
            )
        visited.add(coordinate)
        joined = b"".join(gap_bytes(records[coordinate]))
        next_coordinates: list[tuple[int, int]] = []
        for match in ALL_CALL_RE.finditer(joined):
            operand = int.from_bytes(match.group(2), "little")
            target = (operand // 10_000, operand % 10_000)
            edges.append(
                (
                    coordinate,
                    ("01" + match.group(1).hex()).upper(),
                    operand,
                    target,
                )
            )
            next_coordinates.append(target)
            pending.append(target)
        if not next_coordinates:
            terminals.append(coordinate)
    graph = tuple(
        (
            coordinate,
            sha256_bytes(records[coordinate].data),
            literal_texts(records, coordinate),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[coordinate])
            ),
        )
        for coordinate in sorted(visited)
    ) + (("edges", tuple(sorted(edges))),)
    return graph, tuple(sorted(terminals))


def call_graph_evidence(prepared: Any) -> tuple[Any, ...]:
    evidence: list[tuple[Any, ...]] = []
    for label, archive, roots in (
        (
            "jp",
            prepared.resources["pk_msggame"].pristine_archive,
            SOURCE_CALL_ROOTS,
        ),
        (
            "current",
            prepared.resources["pk_msggame"].current_archive,
            CURRENT_CALL_ROOTS,
        ),
    ):
        records = ENGINE.archive_records(archive)
        for operand in roots:
            graph, terminals = reachable_call_graph(records, (0, operand))
            terminal_literals = tuple(
                literal_texts(records, coordinate)
                for coordinate in terminals
            )
            if (
                not graph
                or not terminals
                or any(len(values) > 1 for values in terminal_literals)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} call graph drifted: "
                    f"{label}:{operand}"
                )
            evidence.append(
                (label, operand, graph, terminals, terminal_literals)
            )
    return tuple(evidence)


def assert_call_graphs(prepared: Any) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(prepared),
        EXPECTED_CALL_GRAPH_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            key[:2],
        )[key[2]]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def unchecked_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    pk = prepared.resources["pk_msggame"]
    current = records_by_label["current"]
    replacements = {
        coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        pk.current_blob,
        replacements,
    )
    reverse_order_candidate = ENGINE.rebuild_packed_with_literals(
        pk.current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if candidate != reverse_order_candidate:
        raise RuntimeError(
            f"segment {SEGMENT} reverse-order overlay drifted"
        )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    target_record_keys = {
        (BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS
    }
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
        or set(replacements) != {
            coordinate_key(coordinate)
            for coordinate in TARGET_COORDINATES
        }
    ):
        raise RuntimeError(f"segment {SEGMENT} candidate universe drifted")
    for key, current_record in current.items():
        if (
            key not in target_record_keys
            and candidate_records[key].data != current_record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        expected = tuple(
            TRANSLATIONS[f"6:{record_id}:{literal_id}"]
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        if (
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            or literal_texts(candidate_records, key) != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target record drifted: {key}"
            )
    reversed_blob = ENGINE.rebuild_packed_with_literals(candidate, reverse)
    if reversed_blob != pk.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    changed = sum(
        translation
        != literal_texts(current, coordinate_key(coordinate)[:2])[
            coordinate_key(coordinate)[2]
        ]
        for coordinate, translation in TRANSLATIONS.items()
    )
    return candidate, sha256_bytes(candidate), changed


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "all_same_record_fragments_reviewed": True,
        "manual_multilingual_context_reviewed": True,
        "completed_base_corpus_searched": True,
        "base_complete_record_match_kind": "none",
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(prepared, records)
    assert_base_and_complete_assembly(prepared, records)
    assert_call_graphs(prepared)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_same_record_fragments_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinates": [],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "speaker_style": style_map[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records, record_id),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 56
        or len(validated) != 56
        or counts != Counter({"runtime_fragment_pending": 56})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B044_S1145",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 10,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "manual_pk_only_record_count":
                len(TARGET_RECORD_IDS),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "completed_base_corpus_searched": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "all_ten_prefills_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "manual_multilingual_context_guarded": True,
                "source_and_current_call_graphs_guarded": True,
                "source_current_runtime_gap_differences_guarded": True,
                "inline_runtime_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "current_runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
