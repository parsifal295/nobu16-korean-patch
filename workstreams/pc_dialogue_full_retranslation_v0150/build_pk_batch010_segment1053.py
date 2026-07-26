#!/usr/bin/env python3
"""Build source-redacted PK batch 010 segment 1053 decisions."""

from __future__ import annotations

import difflib
import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_pk_batch009_segment1050 as COMMON


ENGINE = COMMON.ENGINE
UTIL = COMMON.UTIL
HELPERS = COMMON.HELPERS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B010_S1053.private.v1.jsonl"
)
PREFILL = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)

SEGMENT = 1053
QUEUE_BATCH_ID = "pk_msggame-B010"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 2
PK_RECORD_COUNT = 21751

TRANSLATIONS = {
    "2:328:0": "이 땅에 모략이 일어나면 즉시\n이를 막아 다오",
    "2:329:0": (
        "적의 성을 제압했다!\n"
        "이 승전보를 천하에 널리 알려\n"
        "천하의 부왕이 지닌 위세를 두루 떨쳐라!"
    ),
    "2:330:0": "님도 무척 든든하시겠지……\n이 「",
    "2:330:1": "」와(과) 뜻을 함께할 수 있으니 말이야!",
    "2:331:0": "설마 이 ",
    "2:331:1": "이(가) 협격을\n눈치채지 못할 줄 알았느냐?",
    "2:332:0": (
        "이(가) 자랑하는 기마대의 위용을,\n"
        "천하에 보일 때는 지금이다!"
    ),
    "2:333:0": (
        "이 성을 내 죽을 곳으로 삼으리라!\n"
        "이 목숨을 걸고 끝까지 지켜 내겠다!"
    ),
    "2:334:0": (
        "신뢰를 얻는 것이야말로 처세의 한 방편.\n"
        "분쟁이 끊이지 않는 세상이기에\n"
    ),
    "2:334:1": "은(는) 인연을 요체로 삼는다!",
    "2:338:0": (
        "고금전수의 비의를 집대성한 문재와\n"
        "온갖 무예를 닦은 무재를\n"
        "이 땅에서 남김없이 펼쳐 보이겠다"
    ),
    "2:339:0": (
        "춤추어라, 나의 용기병이여!\n"
        "천하를 향해 날아오르라!"
    ),
    "2:341:0": "만사는 소인에게 맡겨 주십시오.\n이 ",
    "2:341:1": "이(가) 주군의 오른눈이 되겠습니다!",
    "2:342:0": (
        "만민을 위해 힘쓰면 만민 또한 나를 위해 힘쓴다.\n"
        "이것이야말로 땅을 부유하게 하는 비결이니……"
    ),
    "2:349:0": (
        "무슨 일이든 앞서는 것은 금전……\n"
        "여기서는 낭비를 줄이고 재물을 비축하겠다"
    ),
    "2:350:0": (
        "나의 벗, 타로타치여!\n"
        "이 역경을 이겨 낼 힘을 다오!"
    ),
    "2:353:0": (
        "춤추어라, 나의 용기병이여!\n"
        "천하를 향해 날아오르라!"
    ),
    "2:356:0": "빈틈투성이로구나",
    "2:356:1": "!\n내 맹공에 떨도록 하라!",
    "2:357:0": (
        "내 개를 전령으로 삼아\n"
        "훌륭히 이끌어 보이겠다"
    ),
    "2:358:0": (
        "지혜와 재능은 몸에 익혀도 짐이 되지 않으니……\n"
        '"이로하 노래"의 가르침을 널리 전파하겠다'
    ),
    "2:359:0": "상대의 마음을 파고드는 법은 익혀 두었다",
    "2:359:1": "\n우리에게 유리하도록\n일을 이끌어 보이겠다",
    "2:360:0": "전선에 선 이상\n결사의 각오로 ",
    "2:360:1": "싸우겠다!",
    "2:361:0": (
        "방울 소리 울리는 곳에 내가 있다!\n"
        "덤벼들 자는 "
    ),
    "2:361:1": "없느냐!",
    "2:362:0": (
        "시작부터 기선을 제압당한 기분이 어떠냐?\n"
        "싸움은 지혜를 더욱 짜내야 하는 법이지"
    ),
    "2:363:0": "창을 겨누어라!",
    "2:363:1": "\n기마대가 제멋대로 날뛰게 두지 ",
    "2:363:2": "않겠다!",
    "2:364:0": "아직…… 아직 포기하지 않겠다!",
    "2:364:1": "\n몇 번이고 되찾아 ",
    "2:364:2": "보이겠다!",
    "2:366:0": (
        "서로의 가문을 지키고자\n"
        "우리가 손을 잡는 것은 좋은 일이겠지.\n"
    ),
    "2:366:1": "잠시 함께 싸우도록 하지.",
}
TARGET_COORDINATES = tuple(TRANSLATIONS)
TARGET_RECORD_IDS = tuple(
    sorted(
        {
            int(coordinate.split(":")[1])
            for coordinate in TARGET_COORDINATES
        }
    )
)
TARGET_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS
)

RUNTIME_PENDING_COORDINATES = {
    "2:328:0",
    "2:330:0",
    "2:330:1",
    "2:331:0",
    "2:331:1",
    "2:332:0",
    "2:334:0",
    "2:334:1",
    "2:338:0",
    "2:341:0",
    "2:341:1",
    "2:349:0",
    "2:356:0",
    "2:356:1",
    "2:357:0",
    "2:358:0",
    "2:359:0",
    "2:359:1",
    "2:360:0",
    "2:360:1",
    "2:361:0",
    "2:361:1",
    "2:363:0",
    "2:363:1",
    "2:363:2",
    "2:364:0",
    "2:364:1",
    "2:364:2",
    "2:366:0",
    "2:366:1",
}
STATIC_COORDINATES = (
    set(TARGET_COORDINATES) - RUNTIME_PENDING_COORDINATES
)
RUNTIME_INTEGRATION_MODES = {
    "2:328:0": "scheme_suppression_completion",
    "2:330:0": "lord_name_then_quoted_ally_name_prefix",
    "2:330:1": "quoted_ally_name_comitative_completion",
    "2:331:0": "speaker_name_prefix",
    "2:331:1": "speaker_name_subject_completion",
    "2:332:0": "force_name_subject_fragment",
    "2:334:0": "relationship_maxim_record_prefix",
    "2:334:1": "runtime_subject_maxim_completion",
    "2:338:0": "talent_boast_completion",
    "2:341:0": "speaker_name_prefix",
    "2:341:1": "speaker_name_subject_completion",
    "2:349:0": "wealth_policy_completion",
    "2:356:0": "taunt_prefix",
    "2:356:1": "taunt_completion",
    "2:357:0": "dog_messenger_boast_completion",
    "2:358:0": "literary_teaching_boast_completion",
    "2:359:0": "favor_strategy_prefix",
    "2:359:1": "favor_strategy_completion",
    "2:360:0": "resolve_prefix",
    "2:360:1": "resolve_completion",
    "2:361:0": "bell_challenge_prefix",
    "2:361:1": "bell_challenge_completion",
    "2:363:0": "spear_command_prefix",
    "2:363:1": "anti_cavalry_prefix",
    "2:363:2": "anti_cavalry_completion",
    "2:364:0": "recapture_vow_prefix",
    "2:364:1": "recapture_vow_continuation",
    "2:364:2": "recapture_vow_completion",
    "2:366:0": "alliance_maxim_prefix",
    "2:366:1": "alliance_maxim_completion",
}

# These are contextual analogues, not direct-reuse donors.  Their promoted
# Korean policy and source similarity are pinned to make that distinction
# explicit.
BASE_CONTEXT_REFERENCES = {
    "2:331:1": ("9:2161:1", "이(가)\n혼란에 빠질 줄 알았나?"),
    "2:332:0": (
        "6:4296:1",
        "의 기마대가 지닌 위세를 세상에 떨치리라!",
    ),
    "2:339:0": (
        "6:4305:0",
        "말 위에서 불을 뿜는 용기병이여!\n"
        "천하를 향해 날아올라라!",
    ),
    "2:341:0": ("2:120:0", "뒷일은 맡겨 주시오\n이"),
    "2:349:0": (
        "15:1870:0",
        "무슨 일을 하든 먼저 필요한 것은 금전……\n",
    ),
    "2:353:0": (
        "6:4305:0",
        "말 위에서 불을 뿜는 용기병이여!\n"
        "천하를 향해 날아올라라!",
    ),
    "2:363:1": (
        "2:519:0",
        "포위군이 마음대로 하게 두지 ",
    ),
}
HISTORICAL_TERM_COORDINATES = {
    "2:338:0": "kokindenju_literary_transmission",
    "2:350:0": "taro_tachi_proper_name",
    "2:358:0": "iroha_poem_title",
}

BASIS = (
    "pristine PK JP authoritative; current Korean and full-record PC EN "
    "SC TC used for context; completed Base policy used only as pinned "
    "contextual analogues after exact-reuse prefill exclusion; adjacent "
    "records, speaker register, historical proper nouns, duplicate PK "
    "literals, protected layout, runtime gaps, candidate reverse overlay, "
    "two-run reproduction, tamper rejection and read-only input guarded"
)

EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "F6CB4EC6323F4AE2B3140F87CF091C871760430E43FC5003FA9BD149BD065D3B"
)
EXPECTED_QUEUE_SOURCE_SHA256 = (
    "771C91931343A3DA2666F0F8EE24CB27FC748E1F415BD00E50269DD318C8F666"
)
EXPECTED_QUEUE_CURRENT_SHA256 = (
    "DBDF7ABE9F18A8DE2A336440D4653F88647F1462834C7278834A1DCAC62B10EA"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "FF9C3534BC311358CD35731637924EBF0C3C0AA9627CCF564B9B84DC25FD366D"
)
EXPECTED_SOURCE_LITERAL_SHA256 = (
    "58D35E66F6D07A4CFDD8DAB5128032B5DB1A6FD8620A784BBDD169660B0655FD"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "02EBAC8EA815967099BF0777B46A49BA3A625D586790BEC96A924EBEC2EE8F73"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "EADA2104702730379116A10D8C53674A98B44DB864192C663DF4412151D71E09"
)
EXPECTED_SOURCE_RECORD_SHA256 = (
    "F95662F7C5688E73A5C331662A0DAF5285E38219C20C30663658F483C898EB54"
)
EXPECTED_CURRENT_RECORD_SHA256 = (
    "75658333E507E65335BF347518D4C1B53EA002812E089EF4FF57D2002D95D3A0"
)
EXPECTED_CONTEXT_RECORD_SHA256 = (
    "16A0EB12276D32630A6741EC0E3030F93FB983C41F08906E4180EB26B618656C"
)
EXPECTED_GAP_SHA256 = (
    "7167C7EC220E99A44F1551187142EBB91DA65519B8C16C6F90D3FF1191210450"
)
EXPECTED_PENDING_SHA256 = (
    "2BE1FEB32C91AF9E124D6CBB073679D894193180DDCFDDE18038AAFD6EE31A8A"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "4E8FBA3E8E9F61E0F0BBEA6A6B61FD7B54AA052CD2AE81A01416165A60A96DD1"
)
EXPECTED_CANDIDATE_SHA256 = (
    "C71E0AD21CC8DDA0E2F85A3682260FBFFE90FB8436D6F5626BA41D5E19B6EC10"
)
EXPECTED_CHANGED_LITERAL_COUNT = 31
EXPECTED_CURRENT_PACKED_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records


def canonical_sha256(value: object) -> str:
    return HELPERS.canonical_sha256(value)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_rows(
    path: Path,
    expected_sha256: str | None = None,
) -> list[dict[str, Any]]:
    if (
        not path.is_file()
        or (
            expected_sha256 is not None
            and file_sha256(path) != expected_sha256
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision input drifted: {path.name}"
        )
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            value = json.loads(line)
            if not isinstance(value, dict):
                raise RuntimeError(
                    f"segment {SEGMENT} invalid decision row"
                )
            rows.append(value)
    return rows


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in prepared.queue.splitlines():
        if not line:
            continue
        row = json.loads(line)
        if row.get("batch_id") == QUEUE_BATCH_ID:
            rows.append(row)
    return rows


def visible_queue(
    prepared: Any,
) -> tuple[tuple[str, str, str], ...]:
    visible: list[tuple[str, str, str]] = []
    for row in queue_rows(prepared):
        for literal_id, target in enumerate(row["target_literals"]):
            if target["visible"]:
                visible.append(
                    (
                        str(target["coordinate"]),
                        str(row["source_jp_literals"][literal_id]),
                        str(row["current_ko_literals"][literal_id]),
                    )
                )
    return tuple(visible)


def assert_queue_contract(prepared: Any) -> None:
    rows = queue_rows(prepared)
    visible = visible_queue(prepared)
    owned = visible[QUEUE_START:QUEUE_STOP]
    owned_coordinates = tuple(row[0] for row in owned)
    if (
        len(rows) != 139
        or rows[0]["record_coordinate"] != "2:242"
        or rows[-1]["record_coordinate"] != "2:380"
        or len(visible) != 200
        or len(owned) != 66
        or owned_coordinates[0] != "2:328:0"
        or owned_coordinates[-1] != "2:380:0"
        or canonical_sha256(
            tuple((coordinate, source) for coordinate, source, _ in owned)
        )
        != EXPECTED_QUEUE_SOURCE_SHA256
        or canonical_sha256(
            tuple((coordinate, current) for coordinate, _, current in owned)
        )
        != EXPECTED_QUEUE_CURRENT_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue contract drifted"
        )

    prefill_rows = read_rows(PREFILL, EXPECTED_PREFILL_SHA256)
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
    )
    prefill_coordinates = {
        str(row["coordinate"]) for row in prefill_rows
    }
    prefilled_owned = tuple(
        coordinate
        for coordinate in owned_coordinates
        if coordinate in prefill_coordinates
    )
    if (
        len(prefilled_owned) != 29
        or canonical_sha256(prefilled_owned)
        != EXPECTED_PREFILLED_COORDINATE_SHA256
        or set(owned_coordinates) - prefill_coordinates
        != set(TARGET_COORDINATES)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} exact-reuse prefill split drifted"
        )

    other_coordinates: dict[str, str] = {}
    for path in sorted(
        OUTPUT.parent.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_rows(path):
            coordinate = str(row["coordinate"])
            provider = other_coordinates.setdefault(
                coordinate,
                path.name,
            )
            if provider != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate PK decision: "
                    f"{coordinate}"
                )
    if any(
        coordinate in other_coordinates
        for coordinate in TARGET_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target already has a decision"
        )


def record_contract(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, str], ...]:
    return tuple(
        (
            record_id,
            hashlib.sha256(
                records[(BLOCK_ID, record_id)].data
            ).hexdigest().upper(),
        )
        for record_id in TARGET_RECORD_IDS
    )


def gap_contract(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            record_id,
            tuple(
                gap.hex().upper()
                for gap in gap_bytes(source[(BLOCK_ID, record_id)])
            ),
            tuple(
                gap.hex().upper()
                for gap in gap_bytes(current[(BLOCK_ID, record_id)])
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )


def rough_dynamic(record: Any) -> bool:
    joined = b"".join(gap_bytes(record))
    return b"\x01\x43" in joined or b"\x02" in joined


def assert_archive_contracts(
    prepared: Any,
    records_by_label: dict[
        str,
        dict[tuple[int, int], Any],
    ],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    contexts = tuple(
        (
            label,
            record_contract(ENGINE.archive_records(archive)),
        )
        for label, archive in sorted(
            prepared.resources[
                "pk_msggame"
            ].context_archives.items()
        )
    )
    source_literals = tuple(
        literal_texts(
            source,
            (
                BLOCK_ID,
                int(coordinate.split(":")[1]),
            ),
        )[int(coordinate.split(":")[2])]
        for coordinate in TARGET_COORDINATES
    )
    current_literals = tuple(
        literal_texts(
            current,
            (
                BLOCK_ID,
                int(coordinate.split(":")[1]),
            ),
        )[int(coordinate.split(":")[2])]
        for coordinate in TARGET_COORDINATES
    )
    detected_pending = tuple(
        coordinate
        for coordinate in TARGET_COORDINATES
        if rough_dynamic(
            source[
                (
                    BLOCK_ID,
                    int(coordinate.split(":")[1]),
                )
            ]
        )
    )
    if (
        canonical_sha256(record_contract(source))
        != EXPECTED_SOURCE_RECORD_SHA256
        or canonical_sha256(record_contract(current))
        != EXPECTED_CURRENT_RECORD_SHA256
        or canonical_sha256(contexts)
        != EXPECTED_CONTEXT_RECORD_SHA256
        or canonical_sha256(source_literals)
        != EXPECTED_SOURCE_LITERAL_SHA256
        or canonical_sha256(current_literals)
        != EXPECTED_CURRENT_LITERAL_SHA256
        or canonical_sha256(gap_contract(source, current))
        != EXPECTED_GAP_SHA256
        or detected_pending
        != tuple(
            coordinate
            for coordinate in TARGET_COORDINATES
            if coordinate in RUNTIME_PENDING_COORDINATES
        )
        or canonical_sha256(detected_pending)
        != EXPECTED_PENDING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} archive contract drifted"
        )


def assert_base_context_references(
    records_by_label: dict[
        str,
        dict[tuple[int, int], Any],
    ],
) -> None:
    base_rows = read_rows(
        BASE_PROMOTED,
        EXPECTED_BASE_PROMOTED_SHA256,
    )
    by_coordinate = {
        str(row["coordinate"]): row
        for row in base_rows
        if "translation" in row
    }
    pk_source = records_by_label["pk_jp"]
    base_source = records_by_label["base_jp"]
    evidence: list[tuple[object, ...]] = []
    for pk_coordinate, (
        base_coordinate,
        expected_translation,
    ) in BASE_CONTEXT_REFERENCES.items():
        pk_block, pk_record, pk_literal = (
            int(part) for part in pk_coordinate.split(":")
        )
        base_block, base_record, base_literal = (
            int(part) for part in base_coordinate.split(":")
        )
        row = by_coordinate.get(base_coordinate)
        pk_text = literal_texts(
            pk_source,
            (pk_block, pk_record),
        )[pk_literal]
        base_text = literal_texts(
            base_source,
            (base_block, base_record),
        )[base_literal]
        ratio = difflib.SequenceMatcher(
            None,
            pk_text,
            base_text,
        ).ratio()
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["translation"] != expected_translation
            or row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or pk_text == base_text
            or ratio < 0.45
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base context drifted: "
                f"{pk_coordinate}"
            )
        evidence.append(
            (
                pk_coordinate,
                base_coordinate,
                round(ratio, 12),
                expected_translation,
            )
        )
    if canonical_sha256(tuple(evidence)) != EXPECTED_BASE_CONTEXT_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Base context digest drifted"
        )


def assert_semantics() -> None:
    if (
        len(TARGET_COORDINATES) != 37
        or len(TARGET_RECORD_IDS) != 24
        or len(RUNTIME_PENDING_COORDINATES) != 30
        or len(STATIC_COORDINATES) != 7
        or set(RUNTIME_INTEGRATION_MODES)
        != RUNTIME_PENDING_COORDINATES
        or set(HISTORICAL_TERM_COORDINATES)
        != {"2:338:0", "2:350:0", "2:358:0"}
        or TRANSLATIONS["2:339:0"]
        != TRANSLATIONS["2:353:0"]
        or canonical_sha256(TARGET_COORDINATES)
        != EXPECTED_TARGET_COORDINATE_SHA256
        or canonical_sha256(
            tuple(
                TRANSLATIONS[coordinate]
                for coordinate in TARGET_COORDINATES
            )
        )
        != EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic universe drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        allowed_fullwidth = (
            {"「"} if coordinate == "2:330:0"
            else {"」"} if coordinate == "2:330:1"
            else set()
        )
        if (
            "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or (
                UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                    translation
                )
                - allowed_fullwidth
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} translation policy drifted: "
                f"{coordinate}"
            )
    if ENGINE.KANA_OR_HAN_RE.search(
        SCRIPT.read_text(encoding="utf-8")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder is not source-redacted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[
        str,
        dict[tuple[int, int], Any],
    ],
) -> tuple[bytes, str, int]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        tuple(
            int(part) for part in coordinate.split(":")
        ): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )
    target_keys = set(TARGET_RECORD_KEYS)
    for key, record in current.items():
        if (
            key not in target_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed outside scope: {key}"
            )
    for key in TARGET_RECORD_KEYS:
        if gap_bytes(candidate_records[key]) != gap_bytes(current[key]):
            raise RuntimeError(
                f"segment {SEGMENT} changed target gaps: {key}"
            )
    for coordinate, translation in TRANSLATIONS.items():
        key = tuple(
            int(part) for part in coordinate.split(":")
        )
        if (
            literal_texts(candidate_records, key[:2])[key[2]]
            != translation
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate literal drifted: "
                f"{coordinate}"
            )
    if (
        ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay drifted"
        )
    changed = sum(
        translation != reverse[key]
        for key, translation in replacements.items()
    )
    candidate_sha256 = hashlib.sha256(
        candidate
    ).hexdigest().upper()
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate digest drifted"
        )
    tampered = candidate[:-1] + bytes([candidate[-1] ^ 0x01])
    if hashlib.sha256(tampered).hexdigest().upper() in {
        EXPECTED_CANDIDATE_SHA256,
        EXPECTED_CURRENT_PACKED_SHA256,
    }:
        raise RuntimeError(
            f"segment {SEGMENT} candidate tamper was not detected"
        )
    return candidate, candidate_sha256, changed


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    assert_archive_contracts(prepared, records_by_label)
    assert_base_context_references(records_by_label)
    assert_semantics()

    current = records_by_label["pk_current"]
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = (
            int(part) for part in coordinate.split(":")
        )
        translation = TRANSLATIONS[coordinate]
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected layout drifted: "
                f"{coordinate}"
            )
        pending = coordinate in RUNTIME_PENDING_COORDINATES
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        row: dict[str, Any] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
            "translation": translation,
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending"
                if pending
                else "retranslated"
            ),
            "layout_review": "unchanged_from_current",
            "runtime_review": (
                "pending" if pending else "not_required"
            ),
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "exact_reuse_prefill_companions_guarded": True,
            "pc_multilingual_record_context_reviewed": True,
            "adjacent_record_context_reviewed": True,
            "manual_translation_reviewed": True,
            "base_context_reference_coordinate": (
                BASE_CONTEXT_REFERENCES[coordinate][0]
                if coordinate in BASE_CONTEXT_REFERENCES
                else None
            ),
            "historical_term_check": (
                HISTORICAL_TERM_COORDINATES.get(coordinate)
            ),
        }
        if pending:
            row["runtime_assembly_evidence"] = {
                "integration_mode":
                RUNTIME_INTEGRATION_MODES[coordinate],
                "pk_gap_template_guarded": True,
                "runtime_review_required": True,
                "automatic_runtime_promotion_authorized": False,
            }
        rows.append(row)

    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    return prepared, rows, candidate, candidate_sha256, changed


def assert_decision_tamper_rejected(
    prepared: Any,
    rows: list[dict[str, Any]],
) -> None:
    tampered = [dict(row) for row in rows]
    tampered[0]["current_ko_utf16le_sha256"] = "0" * 64
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="pk-s1053-tamper-",
        dir=OUTPUT.parent,
    ) as temporary:
        path = Path(temporary) / "tampered.private.v1.jsonl"
        ENGINE.atomic_write(path, ENGINE.jsonl(tampered))
        try:
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
        except ENGINE.RetranslationError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} decision tamper was not rejected"
            )


def main() -> int:
    input_path = (
        ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    )
    input_before = file_sha256(input_path)
    first = build_rows()
    second = build_rows()
    prepared, rows, candidate, candidate_sha256, changed = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )

    assert_decision_tamper_rejected(prepared, rows)
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    input_after = file_sha256(input_path)
    if (
        len(rows) != 37
        or len(validated) != 37
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 30,
                "retranslated": 7,
            }
        )
        or input_before != input_after
        or input_after != EXPECTED_CURRENT_PACKED_SHA256
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["semantic_review"] != "approved"
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B010_S1053",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "queue_coordinate_envelope": [
                    "2:328:0",
                    "2:380:0",
                ],
                "first_decision_coordinate":
                TARGET_COORDINATES[0],
                "last_decision_coordinate":
                TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "exact_reuse_prefill_count": 29,
                "base_context_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "historical_term_check_count":
                len(HISTORICAL_TERM_COORDINATES),
                "scope_classification_counts": dict(counts),
                "changed_literal_count": changed,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": file_sha256(OUTPUT),
                "builder_sha256": file_sha256(SCRIPT),
                "exact_reuse_prefill_split_guarded": True,
                "base_context_is_non_direct_reuse": True,
                "pc_multilingual_context_guarded": True,
                "historical_terms_checked": True,
                "runtime_fragments_left_pending": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "decision_tamper_rejected": True,
                "candidate_tamper_rejected": True,
                "second_run_reproduction_exact": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
