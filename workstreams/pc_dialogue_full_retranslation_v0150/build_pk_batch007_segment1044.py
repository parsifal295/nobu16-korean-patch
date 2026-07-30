#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1044 decisions."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch007_segment1022 as BASE_LEFT
import build_base_batch007_segment1023 as BASE_RIGHT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch006_segment1041 as COMMON

try:
    import build_pk_batch007_segment1043 as LEFT_PK
except ModuleNotFoundError:
    LEFT_PK = None


ENGINE = BASE_LEFT.ENGINE
GENERAL = BASE_LEFT.GENERAL
UTIL = BASE_LEFT.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B007_S1044.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B007_S1022.private.v1.jsonl",
        "29EEFE94FF42CEA83CB8C23D74A14CDCA45C1C70FF9AAC84444909B2D6E26DB8",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B007_S1023.private.v1.jsonl",
        "D54902B9578DE1E655B62BB6E69324226D4882B0D9B9CABAE3DE7174CA8D0B39",
    ),
)
SEGMENT = 1044
QUEUE_BATCH_ID = "pk_msggame-B007"
BLOCK_ID = 0
QUEUE_START = 134
QUEUE_STOP = 200
OWNED_RECORD_IDS = tuple(range(2607, 2677))
HIDDEN_RECORD_IDS = (2638, 2643, 2645, 2650)
RECORD_IDS = tuple(
    record_id
    for record_id in OWNED_RECORD_IDS
    if record_id not in HIDDEN_RECORD_IDS
)
BASE_RECORD_IDS = tuple(range(2539, 2609))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
OWNED_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in OWNED_RECORD_IDS
)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = (
    "0:2638:0",
    "0:2643:0",
    "0:2645:0",
    "0:2650:0",
)
PK_RECORD_COUNT = 21751

FULL_PK_GROUPS = {
    1114: tuple(range(2602, 2609)),
    1120: tuple(range(2609, 2616)),
    1126: tuple(range(2616, 2623)),
    1132: tuple(range(2623, 2630)),
    1138: tuple(range(2630, 2637)),
    1168: tuple(range(2637, 2644)),
    1174: tuple(range(2644, 2651)),
    1180: tuple(range(2651, 2658)),
    1186: tuple(range(2658, 2665)),
    1192: tuple(range(2665, 2672)),
    1198: tuple(range(2672, 2679)),
}
BASE_ROOT_BY_PK = {
    1114: 1102,
    1120: 1108,
    1126: 1114,
    1132: 1120,
    1138: 1126,
    1168: 1156,
    1174: 1162,
    1180: 1168,
    1186: 1174,
    1192: 1180,
    1198: 1187,
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id in record_ids
    if record_id in RECORD_IDS
}
EXPECTED_ROOT_CLOSURES = {
    root: tuple(range(root, root + 6)) + record_ids
    for root, record_ids in FULL_PK_GROUPS.items()
}

BASE_POLICY = {
    **BASE_LEFT.FULL_TRANSLATION_POLICY,
    **BASE_RIGHT.FULL_TRANSLATION_POLICY,
}
TRANSLATIONS_BY_RECORD = {
    record_id: BASE_POLICY[record_id - 68]
    for record_id in RECORD_IDS
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
ZERO_MORPHEME_ROOTS = {1132, 1168, 1174}
ZERO_MORPHEME_COORDINATES = {
    coordinate
    for coordinate, translation in TRANSLATIONS.items()
    if translation == ""
}
ZERO_MORPHEME_KIND_BY_ROOT = {
    1132: "japanese_sentence_final_particle",
    1168: "japanese_honorific_prefix",
    1174: "japanese_honorific_prefix",
}

EXPECTED_SOURCE_SHA256 = (
    "7A2448FBF8D5B9C9DC8CF797A7A1687489E9DC7555E60BD380A5B64F524FFFC2"
)
EXPECTED_PK_SOURCE_ANCHOR_SHA256 = (
    "9A354B6320EA0D05999721D76FF639138749F8FF4448E97155FC94FA6EC65A19"
)
EXPECTED_PK_CURRENT_ANCHOR_SHA256 = (
    "257010D7C374286E93A51BCB8FC4F4167567C4EC6B095E16EDB376F51DAF8BC6"
)
EXPECTED_POLICY_SHA256 = (
    "650BDB6D2A9E1CE34B4DA782A6B22416074E5AED1FAAB4424E70A565D03EDDD0"
)
EXPECTED_MAPPING_SHA256 = (
    "C4FEA9134CBAF3DD71268BF34C35A202A1B4D5FB150E243DDA0BDDD66344F8C3"
)
EXPECTED_HIDDEN_RAW_SHA256 = (
    "811FF85F6B47A23F4758F2875D435808683AA06A45FF36EBDF984AE4245761C0"
)
EXPECTED_CHANGED_LITERAL_COUNT = 64
EXPECTED_CANDIDATE_SHA256 = (
    "BA45A1DBBF46C3158DB2F7FE628330330EC53B6F5C5A8A892A65BE99264E9CA3"
)

PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "F18C561582E43627BC6283748D4306F81683ED76C81DEFD2F629C801FE6860D7",
    "pk_current": "D501CF41C40BCC38992D9A5255F18B7311B2FE31DD9AA1292070FF015B6C3B6F",
    "pk_sc": "A17CD3630032083C65776CC42981D1D063105EB698C6B9F68E2F16C31052128C",
    "pk_tc": "A17CD3630032083C65776CC42981D1D063105EB698C6B9F68E2F16C31052128C",
    "pk_en": "A17CD3630032083C65776CC42981D1D063105EB698C6B9F68E2F16C31052128C",
}
PK_OWNED_ARCHIVE_DIGESTS = {
    "pk_jp": "623C5070EC12809AAB9DC4A7DBF189D18EB5A25C7D98DB037D0450CBBB7CEAA4",
    "pk_current": "D05D35DC6FBF4EEAAD33E9EF25E71CC9AEC34FC6CCEF20A50C05C07CC4F075AE",
    "pk_sc": "841998589E47C7092A545BB30211D6A20A54CB74BDE84E375E14AA4CF043802C",
    "pk_tc": "841998589E47C7092A545BB30211D6A20A54CB74BDE84E375E14AA4CF043802C",
    "pk_en": "841998589E47C7092A545BB30211D6A20A54CB74BDE84E375E14AA4CF043802C",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "FDFAE3E2ECDAA5C6AA33D07912AC3DB262C302A91BC1089C75974DABE1A829B6",
    "pk_current": "F5CF215C1A51B08D5CFF677E7398A61F19990A8BD9D94E8631DD3FC1C9CB48A4",
    "pk_sc": "2A248665DED9ABEC3604B7FC14F82209CA193AA7DD84330FE987C78D8E0A1E99",
    "pk_tc": "2A248665DED9ABEC3604B7FC14F82209CA193AA7DD84330FE987C78D8E0A1E99",
    "pk_en": "2A248665DED9ABEC3604B7FC14F82209CA193AA7DD84330FE987C78D8E0A1E99",
}
PK_TARGET_EDGE = (
    66,
    "7C38C8110759E93C0DA7749A0D77F365F9405A3C74151DB87AC480A6B59BAA44",
)
PK_OWNED_EDGE = (
    70,
    "059A3D50B83528CA445D3B079099A60C04298890FE56D087C22F2B2E1300B065",
)
PK_FULL_EDGE = (
    77,
    "B054703DAE7C0D868D5A44E6D2C8E4B3F5C6FA4C072D406AB70B6D15E36A596E",
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "017347A94942973CDDEFD96BEC96B862B6ED04195727C5718E33DFBD6B5BF53C"
)
EXPECTED_ALL_CALLER_CONTEXT_COUNT = 785
EXPECTED_ALL_CALLER_CONTEXT_SHA256 = (
    "8C9600FA6F929AE39F2AF8074335DFD6003DA99D5FE8723C1C29662A9F239D0B"
)
EXPECTED_ZERO_MORPHEME_COORDINATE_SHA256 = (
    "8FCDAFCD261B335A9EC6D345A3B7586C6174CB46FF284C95A09B0A279BF7D57D"
)
EXPECTED_DIVERGENCE_EVIDENCE_SHA256 = (
    "6242B0336A9B8C4EB02A5AF964C2755CABDA1E14764ED4839B3FE7761F110F48"
)
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[1114]
LEFT_BOUNDARY_SOURCE_SHA256 = (
    "7C276D2D7DAE101732F09212433DB482D2DFB7FAD07037E27F4077351B123D3F"
)
LEFT_BOUNDARY_CURRENT = (
    "할 수 없습니다",
    "할 수 없",
    "할 수 없습니다",
    "할 수 없습니다",
    "할 수 없습니다",
    "할 수 없습니다",
    "할 수 없",
)
LEFT_BOUNDARY_POLICY = tuple(
    BASE_POLICY[record_id - 68] for record_id in LEFT_BOUNDARY_IDS
)
RIGHT_BOUNDARY_IDS = FULL_PK_GROUPS[1198]
RIGHT_BOUNDARY_SOURCE_SHA256 = (
    "287EA87A0F0A182804D2A8A72F5FFE7211589D0853D7A7E0379DDE5CA7427868"
)
RIGHT_BOUNDARY_CURRENT = (
    "받으실",
    "받아",
    "받으실",
    "받으실",
    "받으실",
    "받으실",
    "받아",
)
RIGHT_BOUNDARY_POLICY = tuple(
    BASE_POLICY[record_id - 68] for record_id in RIGHT_BOUNDARY_IDS
)
RIGHT_ROOT1198_FULL_IDS = RIGHT_BOUNDARY_IDS
RIGHT_ROOT1198_FULL_SOURCE_SHA256 = RIGHT_BOUNDARY_SOURCE_SHA256
RIGHT_ROOT1198_FULL_CURRENT = RIGHT_BOUNDARY_CURRENT
RIGHT_ROOT1198_FULL_POLICY = RIGHT_BOUNDARY_POLICY

MAPPED_DIVERGENT_IDS = {2659, *range(2672, 2677)}
EXPECTED_CURRENT_DIVERGENCES = {
    2659: ("주려무나", "다오"),
    2672: ("받으실", "받을 수 있다"),
    2673: ("받아", "받을 수 있다"),
    2674: ("받으실", "받을 수 있다"),
    2675: ("받으실", "받을 수 있다"),
    2676: ("받으실", "받을 수 있다"),
}

ROOT_ASSEMBLY_PLAN = {
    1114: (
        "ability-negative and conjectural callers share the register "
        "matrix; flatten already-complete callers and rewrite each stem by "
        "meaning before retaining a terminal"
    ),
    1120: (
        "command callers are already complete in current Korean; flatten "
        "the redundant terminal rather than duplicate an imperative"
    ),
    1126: (
        "future and first-person volition are mixed across many callers; "
        "normalize the caller stem and select intention or future by context"
    ),
    1132: (
        "sentence-final particles have no independent Korean surface form; "
        "preserve caller punctuation and emit an exact zero morpheme"
    ),
    1138: (
        "negative ending attaches without a space; complete and flattened "
        "callers require joint boundary normalization"
    ),
    1168: (
        "honorific prefix has no independent Korean surface form; preserve "
        "the verbal noun and its caller spacing as an exact zero morpheme"
    ),
    1174: (
        "honorific prefix has no independent Korean surface form; preserve "
        "the verbal noun and its caller spacing as an exact zero morpheme"
    ),
    1180: (
        "wait-request stem precedes fixed conditionals; normalize spacing "
        "and attach the fixed following text jointly"
    ),
    1186: (
        "benefactive request stem precedes fixed conditionals; normalize "
        "the caller verb and following text jointly"
    ),
    1192: (
        "apology or departure ending is source-only in PK current; restore "
        "it only while translating the flattened caller"
    ),
    1198: (
        "PK stores bound benefactive stems while Base stores complete "
        "ability semantics; flatten completed callers or rewrite both "
        "boundaries before retaining the selected register"
    ),
}

CALLER_INTEGRATION_EVIDENCE = {
    1114: (
        {
            "call_site": "6:4634:1:0",
            "observed_current_left": "그 망설임을 풀 수 있을지도 모르오",
            "observed_current_right": "\n",
            "expected_current_gap_hex": "01435A0400000143FC010000",
            "integration_mode": "flatten_complete_conjectural_caller",
            "source_free_korean_example": (
                "그 망설임을 풀 수 있을지도 모르오\n"
            ),
        },
        {
            "call_site": "9:3948:4:0",
            "observed_current_left": "방심 마",
            "observed_current_right": "듯",
            "expected_current_gap_hex": "01435A040000",
            "integration_mode": "rewrite_negative_not_ability",
            "source_free_korean_example": "방심하지 않도록",
        },
    ),
    1120: (
        {
            "call_site": "6:4735:1:0",
            "observed_current_left": "그렇다면 당장 사라지시오",
            "observed_current_right": "\n목이 달아나도 불평하지 마시오",
            "expected_current_gap_hex": "014360040000",
            "integration_mode": "flatten_complete_imperative_caller",
            "source_free_korean_example": (
                "그렇다면 당장 사라지시오\n"
                "목이 달아나도 불평하지 마시오"
            ),
        },
    ),
    1126: (
        {
            "call_site": "6:1442:2:0",
            "observed_current_left": "\n군단을 통솔하여 당가의 중심이 되",
            "observed_current_right": "",
            "expected_current_gap_hex": "014366040000050505",
            "integration_mode": "direct_future_composition",
            "source_free_korean_example": (
                "\n군단을 통솔하여 당가의 중심이 되겠습니다"
            ),
        },
        {
            "call_site": "7:2458:2:0",
            "observed_current_left": "\n힘든 싸움이 되",
            "observed_current_right": "",
            "expected_current_gap_hex": "014366040000",
            "integration_mode": "direct_future_prediction",
            "source_free_korean_example": "\n힘든 싸움이 되겠습니다",
        },
    ),
    1132: (
        {
            "call_site": "2:538:1:0",
            "observed_current_left": "고개가 높구나",
            "observed_current_right": "!\n내가 누군지 아느냐?",
            "expected_current_gap_hex": "01436C040000",
            "integration_mode": "exact_zero_morpheme_particle",
            "source_free_korean_example": (
                "고개가 높구나!\n내가 누군지 아느냐?"
            ),
        },
    ),
    1138: (
        {
            "call_site": "15:1515:5:0",
            "observed_current_left": "\n상관없",
            "observed_current_right": "일까?",
            "expected_current_gap_hex": "014372040000",
            "integration_mode": "rewrite_negative_boundary",
            "source_free_korean_example": "\n상관없을까?",
        },
    ),
    1168: (
        {
            "call_site": "6:3768:3:0",
            "observed_current_left": "협력을 청하고자…\n",
            "observed_current_right": "약속해 주시",
            "expected_current_gap_hex": "014390040000",
            "integration_mode": "exact_zero_morpheme_honorific",
            "source_free_korean_example": (
                "협력을 청하고자…\n약속해 주실 수 있습니까?"
            ),
        },
    ),
    1174: (
        {
            "call_site": "2:573:1:0",
            "observed_current_left": "의",
            "observed_current_right": "무운을\n빌어 드리",
            "expected_current_gap_hex": "014396040000",
            "integration_mode": "zero_morpheme_rewrite_boundary_space",
            "source_free_korean_example": "의 무운을\n빌어 드립니다",
        },
    ),
    1180: (
        {
            "call_site": "15:262:1:0",
            "observed_current_left": "선동의 계략, 잠시 동안",
            "observed_current_right": "면\n",
            "expected_current_gap_hex": "01439C040000",
            "integration_mode": "rewrite_wait_request_conditional",
            "source_free_korean_example": (
                "선동의 계략, 잠시 기다려 주시면\n"
            ),
        },
    ),
    1186: (
        {
            "call_site": "6:4782:1:0",
            "observed_current_left": "\n지금 영지를 안도해 주신",
            "observed_current_right": "다면\n무엇보다 기쁘겠습니",
            "expected_current_gap_hex": "0143A2040000",
            "integration_mode": "rewrite_benefactive_conditional",
            "source_free_korean_example": (
                "\n지금 영지를 안도해 주신다면\n"
                "무엇보다 기쁘겠습니다"
            ),
        },
    ),
    1198: (
        {
            "call_site": "6:3657:2:0",
            "observed_current_left": "을\n이렇게 내려주시",
            "observed_current_right": "다니…\n감사할 따름이",
            "expected_current_gap_hex": "0143AE040000",
            "integration_mode": "flatten_completed_benefactive",
            "source_free_korean_example": (
                "을\n이렇게 내려주시다니…\n감사할 따름입니다"
            ),
        },
        {
            "call_site": "6:3766:1:0",
            "observed_current_left": (
                "양가 사이에 굳건한 신뢰를 쌓고자 하오…\n"
                "훗날 동맹을 맺겠다는 약속에\n동의할 것"
            ),
            "observed_current_right": "인가?",
            "expected_current_gap_hex": "0143AE040000014348040000",
            "integration_mode": "rewrite_benefactive_ability_question",
            "source_free_korean_example": (
                "양가 사이에 굳건한 신뢰를 쌓고자 하오…\n"
                "훗날 동맹을 맺겠다는 약속에\n"
                "동의해 주실 수 있소?"
            ),
        },
        {
            "call_site": "6:4485:2:0",
            "observed_current_left": "에게 맡기",
            "observed_current_right": (
                "면\n신속히 장악을 진행하겠"
            ),
            "expected_current_gap_hex": "0143AE040000",
            "integration_mode": "rewrite_bound_benefactive_conditional",
            "source_free_korean_example": (
                "에게 맡겨 주신다면\n신속히 장악을 진행하겠습니다"
            ),
        },
        {
            "call_site": "6:4561:4:0",
            "observed_current_left": "조력하여",
            "observed_current_right": "인가?",
            "expected_current_gap_hex": (
                "0143AE0400000143EC020000"
            ),
            "integration_mode": "rewrite_bound_benefactive_request",
            "source_free_korean_example": "조력해 주실 수 있습니까?",
        },
    ),
}
SOURCE_ONLY_FLATTEN_EVIDENCE = {
    1114: (
        {
            "call_site": "15:261:3:0",
            "integration_mode": "flatten_source_only_conjecture",
            "source_free_korean_example": (
                "\n잘되면 모두 함께 돌아설지도 모릅니다"
            ),
        },
    ),
    1120: (
        {
            "call_site": "2:363:1:0",
            "integration_mode": "flatten_source_only_command",
            "source_free_korean_example": (
                "창을 겨누어라!\n기마대가 마음대로 하게 두지 않겠다"
            ),
        },
    ),
    1126: (
        {
            "call_site": "2:222:1:0",
            "integration_mode": "flatten_source_only_first_person_intention",
            "source_free_korean_example": (
                "능숙한 변설로 반드시 신용을 얻고 오겠습니다!"
            ),
        },
    ),
    1132: (
        {
            "call_site": "2:360:1:0",
            "integration_mode": "flatten_source_only_zero_particle",
            "source_free_korean_example": (
                "전선에 서는 이상 결사의 각오로 싸우겠다!"
            ),
        },
    ),
    1138: (
        {
            "call_site": "13:27:2:0",
            "integration_mode": "flatten_source_only_negative",
            "source_free_korean_example": (
                "\n돈이 없으면 세력 확대도 이루기 어렵습니다\n"
                "우선 내정을 재검토하여 수입을 늘려야겠습니다"
            ),
        },
    ),
    1168: (
        {
            "call_site": "2:574:0:0",
            "integration_mode": "flatten_source_only_zero_honorific",
            "source_free_korean_example": "배웅해 주셔서 황송합니다",
        },
    ),
    1174: (
        {
            "call_site": "2:252:2:0",
            "integration_mode": "flatten_source_only_zero_honorific",
            "source_free_korean_example": (
                "\n부디 성과를 기대해 주십시오"
            ),
        },
    ),
    1180: (
        {
            "call_site": "15:258:1:0",
            "integration_mode": "flatten_source_only_wait_conditional",
            "source_free_korean_example": (
                "파괴 계책은 잠시 기다려 주시면\n"
                "첩자를 써서 안에서부터 무너뜨리겠습니다"
            ),
        },
    ),
    1186: (
        {
            "call_site": "15:264:1:0",
            "integration_mode": "flatten_source_only_benefactive_conditional",
            "source_free_korean_example": (
                "선동 계책에 필요한 자금을 얼마간 마련해 주시면"
            ),
        },
    ),
    1192: (
        {
            "call_site": "15:265:1:0",
            "integration_mode": "flatten_source_only_apology",
            "source_free_korean_example": (
                "끼어들어 실례하겠습니다!\n"
                "이곳은 시노비가 솜씨를 보일 때이니\n"
                "더 뛰어난 술책을 건의하겠습니다"
            ),
        },
    ),
}
EXPECTED_INTEGRATION_CLASS_COUNTS = dict(
    Counter(
        str(example["integration_mode"])
        for examples in CALLER_INTEGRATION_EVIDENCE.values()
        for example in examples
    )
)
EXPECTED_SOURCE_ONLY_CLASS_COUNTS = dict(
    Counter(
        str(example["integration_mode"])
        for examples in SOURCE_ONLY_FLATTEN_EVIDENCE.values()
        for example in examples
    )
)

BASIS = (
    "pristine PK JP authoritative; PC EN SC TC and completed Base policy "
    "context-only; completed-Base explicit cross-edition map plus unique PK "
    "source/current anchor; six exact PK-specific morphology divergences; "
    "four hidden rows byte-exact; seventeen Korean zero morphemes gated; "
    "actual calls, fixed following text, flatten deltas, graph closures and "
    "incoming edges guarded; caller rewrites pending; unchanged one-line "
    "layout, reverse overlay, two-run reproduction and Steam read-only"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records
record_signature = COMMON.record_signature
sequence_starts = COMMON.sequence_starts
incoming_jump_rows = COMMON.incoming_jump_rows
caller_context_and_gap = COMMON.caller_context_and_gap


def assert_tracked_builder_source_redacted() -> None:
    if ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8")):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder contains source text"
        )


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    hidden = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if not target["visible"]
    )
    if (
        len(rows) != 204
        or len(visible) != 200
        or hidden != QUEUE_HIDDEN_COORDINATES
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or rows[0]["record_coordinate"] != "0:2473"
        or rows[-1]["record_coordinate"] != "0:2676"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[dict[int, int], int]:
    mapping = dict(zip(OWNED_RECORD_IDS, BASE_RECORD_IDS, strict=True))
    sequence = tuple(
        record_signature(records_by_label["pk_jp"], record_id)
        for record_id in OWNED_RECORD_IDS
    )
    current_sequence = tuple(
        record_signature(records_by_label["pk_current"], record_id)
        for record_id in OWNED_RECORD_IDS
    )
    if (
        HELPERS.canonical_sha256(sequence)
        != EXPECTED_PK_SOURCE_ANCHOR_SHA256
        or HELPERS.canonical_sha256(current_sequence)
        != EXPECTED_PK_CURRENT_ANCHOR_SHA256
        or sequence_starts(records_by_label["base_jp"], sequence) != ()
        or sequence_starts(records_by_label["pk_jp"], sequence) != (2607,)
        or sequence_starts(
            records_by_label["base_current"], current_sequence
        )
        != ()
        or sequence_starts(
            records_by_label["pk_current"], current_sequence
        )
        != (2607,)
        or {pk - base for pk, base in mapping.items()} != {68}
        or HELPERS.canonical_sha256(tuple(mapping.items()))
        != EXPECTED_MAPPING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK anchor or mapping drifted"
        )
    for pk_record_id, base_record_id in mapping.items():
        if base_record_id <= 2554:
            mapped = BASE_LEFT.PK_RECORD_MAP[
                (BLOCK_ID, base_record_id)
            ]
            expected = (BLOCK_ID, pk_record_id)
        else:
            mapped = BASE_RIGHT.PK_RECORD_MAP[base_record_id]
            expected = pk_record_id
        if mapped != expected:
            raise RuntimeError(
                f"segment {SEGMENT} completed Base map drifted: "
                f"{base_record_id}"
            )
    for pk_root, base_root in BASE_ROOT_BY_PK.items():
        module = BASE_LEFT if base_root <= 1114 else BASE_RIGHT
        if module.PK_ROOT_BY_BASE[base_root] != pk_root:
            raise RuntimeError(
                f"segment {SEGMENT} completed Base root map drifted: "
                f"{base_root}"
            )
    return mapping, 68


def assert_sources(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    source = records_by_label["pk_jp"]
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in RECORD_IDS
            )
        )
        != EXPECTED_SOURCE_SHA256
        or HELPERS.canonical_sha256(
            tuple(TRANSLATIONS_BY_RECORD.values())
        )
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source or policy digest drifted"
        )
    full_keys = tuple(
        (BLOCK_ID, record_id) for record_id in range(2602, 2679)
    )
    for label, expected in PK_TARGET_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], RECORD_KEYS
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} target {label} digest drifted"
            )
    for label, expected in PK_OWNED_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], OWNED_RECORD_KEYS
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} owned {label} digest drifted"
            )
    for label, expected in PK_FULL_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], full_keys
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} full {label} digest drifted"
            )
    hidden_raw = tuple(
        (
            label,
            record_id,
            records_by_label[label][
                (BLOCK_ID, record_id)
            ].data.hex().upper(),
        )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en")
        for record_id in HIDDEN_RECORD_IDS
    )
    if HELPERS.canonical_sha256(hidden_raw) != EXPECTED_HIDDEN_RAW_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} hidden raw records drifted"
        )

    source_divergences: set[int] = set()
    current_divergences: set[int] = set()
    for pk_record_id, base_record_id in mapping.items():
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        if (
            literal_texts(records_by_label["pk_jp"], pk_key)
            != literal_texts(records_by_label["base_jp"], base_key)
        ):
            source_divergences.add(pk_record_id)
        if (
            literal_texts(records_by_label["pk_current"], pk_key)
            != literal_texts(records_by_label["base_current"], base_key)
        ):
            current_divergences.add(pk_record_id)
        for language in ("jp", "current", "sc", "tc"):
            if gap_bytes(records_by_label[f"pk_{language}"][pk_key]) != (
                gap_bytes(records_by_label[f"base_{language}"][base_key])
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mapped gap drifted: "
                    f"{language}/{pk_record_id}"
                )
        for language in ("sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mapped context drifted: "
                    f"{language}/{pk_record_id}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_record_id}"
            )
        for label in PK_OWNED_ARCHIVE_DIGESTS:
            expected_literal_count = 1
            if (
                len(literal_texts(records_by_label[label], pk_key))
                != expected_literal_count
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} target skeleton drifted: "
                    f"{label}/{pk_record_id}"
                )
    if (
        source_divergences != MAPPED_DIVERGENT_IDS
        or current_divergences != MAPPED_DIVERGENT_IDS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} mapped divergence set drifted"
        )
    actual_current_divergences = {
        pk_record_id: (
            literal_texts(
                records_by_label["pk_current"],
                (BLOCK_ID, pk_record_id),
            )[0],
            literal_texts(
                records_by_label["base_current"],
                (BLOCK_ID, mapping[pk_record_id]),
            )[0],
        )
        for pk_record_id in MAPPED_DIVERGENT_IDS
    }
    if actual_current_divergences != EXPECTED_CURRENT_DIVERGENCES:
        raise RuntimeError(
            f"segment {SEGMENT} mapped current divergence drifted"
        )
    divergence_rows = tuple(
        (
            pk_record_id,
            literal_texts(
                records_by_label["pk_jp"],
                (BLOCK_ID, pk_record_id),
            )[0],
            literal_texts(
                records_by_label["base_jp"],
                (BLOCK_ID, mapping[pk_record_id]),
            )[0],
            *actual_current_divergences[pk_record_id],
        )
        for pk_record_id in sorted(MAPPED_DIVERGENT_IDS)
    )
    if (
        HELPERS.canonical_sha256(divergence_rows)
        != EXPECTED_DIVERGENCE_EVIDENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} mapped divergence evidence drifted"
        )


def collect_call_evidence(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    evidence: dict[str, tuple[tuple[int | str, ...], ...]] = {}
    for root in FULL_PK_GROUPS:
        source_calls = HELPERS.root_call_sites(source, root)
        current_calls = HELPERS.root_call_sites(current, root)
        source_fixed = HELPERS.fixed_following_blockers(source, root)
        current_fixed = HELPERS.fixed_following_blockers(current, root)
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        evidence[str(root)] = (
            (
                len(source_calls),
                HELPERS.canonical_sha256(source_calls),
                len(source_fixed),
                HELPERS.canonical_sha256(source_fixed),
            ),
            (
                len(current_calls),
                HELPERS.canonical_sha256(current_calls),
                len(current_fixed),
                HELPERS.canonical_sha256(current_fixed),
            ),
            (
                len(source_only),
                HELPERS.canonical_sha256(source_only),
                len(current_only),
                HELPERS.canonical_sha256(current_only),
            ),
        )
    return evidence


def assert_caller_evidence(
    current: dict[tuple[int, int], Any],
) -> None:
    current_calls = {
        root: set(HELPERS.root_call_sites(current, root))
        for root in FULL_PK_GROUPS
    }
    counts: Counter[str] = Counter()
    for root, examples in CALLER_INTEGRATION_EVIDENCE.items():
        for example in examples:
            call_site = str(example["call_site"])
            counts[str(example["integration_mode"])] += 1
            if call_site not in current_calls[root]:
                raise RuntimeError(
                    f"segment {SEGMENT} caller site drifted: "
                    f"{root}/{call_site}"
                )
            left, right, gap = caller_context_and_gap(current, call_site)
            if (
                left != example["observed_current_left"]
                or right != example["observed_current_right"]
                or gap != example["expected_current_gap_hex"]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller context drifted: "
                    f"{root}/{call_site}"
                )
            sample = str(example["source_free_korean_example"])
            if ENGINE.KANA_OR_HAN_RE.search(sample):
                raise RuntimeError(
                    f"segment {SEGMENT} caller example is not "
                    f"source-free Korean: {root}/{call_site}"
                )
    if dict(counts) != EXPECTED_INTEGRATION_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} caller integration classes drifted"
        )


def assert_source_only_evidence(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> None:
    counts: Counter[str] = Counter()
    for root, examples in SOURCE_ONLY_FLATTEN_EVIDENCE.items():
        source_only = (
            set(HELPERS.root_call_sites(source, root))
            - set(HELPERS.root_call_sites(current, root))
        )
        for example in examples:
            call_site = str(example["call_site"])
            counts[str(example["integration_mode"])] += 1
            if call_site not in source_only:
                raise RuntimeError(
                    f"segment {SEGMENT} source-only caller drifted: "
                    f"{root}/{call_site}"
                )
            sample = str(example["source_free_korean_example"])
            if ENGINE.KANA_OR_HAN_RE.search(sample):
                raise RuntimeError(
                    f"segment {SEGMENT} source-only example is not "
                    f"source-free Korean: {root}/{call_site}"
                )
    if dict(counts) != EXPECTED_SOURCE_ONLY_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} source-only classes drifted"
        )


def assert_all_caller_context(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> None:
    rows: list[tuple[int | str, ...]] = []
    for root in FULL_PK_GROUPS:
        for label, records in (
            ("pk_jp", source),
            ("pk_current", current),
        ):
            for call_site in HELPERS.root_call_sites(records, root):
                rows.append(
                    (
                        label,
                        root,
                        call_site,
                        *caller_context_and_gap(records, call_site),
                    )
                )
    if (
        len(rows) != EXPECTED_ALL_CALLER_CONTEXT_COUNT
        or HELPERS.canonical_sha256(tuple(rows))
        != EXPECTED_ALL_CALLER_CONTEXT_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} all caller contexts drifted"
        )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    target_ids = set(RECORD_IDS)
    owned_ids = set(OWNED_RECORD_IDS)
    full_ids = set(range(2602, 2679))
    if full_ids != {
        record_id
        for record_ids in FULL_PK_GROUPS.values()
        for record_id in record_ids
    }:
        raise RuntimeError(
            f"segment {SEGMENT} full group universe drifted"
        )
    for label in PK_TARGET_ARCHIVE_DIGESTS:
        records = records_by_label[label]
        for target_set, expected, description in (
            (target_ids, PK_TARGET_EDGE, "target"),
            (owned_ids, PK_OWNED_EDGE, "owned"),
            (full_ids, PK_FULL_EDGE, "full"),
        ):
            edges = incoming_jump_rows(records, target_set)
            if (
                len(edges) != expected[0]
                or HELPERS.canonical_sha256(edges) != expected[1]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} {description} "
                    "incoming graph drifted"
                )
    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        graph = HELPERS.graph_edges(records)
        for root, expected in EXPECTED_ROOT_CLOSURES.items():
            if tuple(sorted(HELPERS.graph_closure(graph, root))) != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} closure drifted: {root}"
                )
        valid: list[tuple[int, int, int, int, int]] = []
        overlapped: list[tuple[int, int, int, int, int]] = []
        for (block_id, record_id), record in sorted(records.items()):
            for gap_id, gap in enumerate(gap_bytes(record)):
                jump_spans = [
                    range(match.start(), match.end())
                    for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap)
                ]
                for match in MORPHOLOGY_014C_RE.finditer(gap):
                    row = (
                        block_id,
                        record_id,
                        gap_id,
                        match.start(),
                        struct.unpack("<I", match.group(1))[0],
                    )
                    if any(match.start() in span for span in jump_spans):
                        overlapped.append(row)
                    else:
                        valid.append(row)
        if valid or tuple(overlapped) != EXPECTED_014C_OVERLAP:
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014C evidence drifted"
            )
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    evidence = collect_call_evidence(source, current)
    if HELPERS.canonical_sha256(evidence) != EXPECTED_CALL_EVIDENCE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} call/fixed/flatten evidence drifted"
        )
    assert_all_caller_context(source, current)
    assert_caller_evidence(current)
    assert_source_only_evidence(source, current)
    BASE_LEFT.assert_corpora(records_by_label)
    BASE_LEFT.assert_runtime_graph(records_by_label)
    BASE_RIGHT.assert_corpora(records_by_label)
    BASE_RIGHT.assert_runtime_graph(records_by_label)
    return evidence


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in LEFT_BOUNDARY_IDS
            )
        )
        != LEFT_BOUNDARY_SOURCE_SHA256
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in LEFT_BOUNDARY_IDS
        )
        != LEFT_BOUNDARY_CURRENT
        or LEFT_BOUNDARY_POLICY
        != tuple(
            BASE_POLICY[record_id - 68]
            for record_id in LEFT_BOUNDARY_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} left root1114 boundary drifted"
        )
    if LEFT_PK is None:
        raise RuntimeError(
            f"segment {SEGMENT} left S1043 boundary module is unavailable"
        )
    if (
        LEFT_BOUNDARY_IDS != LEFT_PK.RIGHT_ROOT1114_FULL_IDS
        or LEFT_BOUNDARY_SOURCE_SHA256
        != LEFT_PK.RIGHT_ROOT1114_FULL_SOURCE_SHA256
        or LEFT_BOUNDARY_CURRENT
        != LEFT_PK.RIGHT_ROOT1114_FULL_CURRENT
        or LEFT_BOUNDARY_POLICY
        != LEFT_PK.RIGHT_ROOT1114_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1043 root1114 boundary contract drifted"
        )
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in RIGHT_BOUNDARY_IDS
            )
        )
        != RIGHT_BOUNDARY_SOURCE_SHA256
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in RIGHT_BOUNDARY_IDS
        )
        != RIGHT_BOUNDARY_CURRENT
        or RIGHT_BOUNDARY_POLICY
        != tuple(
            BASE_POLICY[record_id - 68]
            for record_id in RIGHT_BOUNDARY_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right root1198 boundary drifted"
        )


def assert_completed_base_policy(
    prepared: Any,
    mapping: dict[int, int],
) -> None:
    rows_by_coordinate: dict[str, dict[str, object]] = {}
    for path, expected_sha256 in BASE_DECISIONS:
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest().upper()
            != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base decision drifted: "
                f"{path.name}"
            )
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                rows_by_coordinate[str(row["coordinate"])] = row
    for pk_record_id in RECORD_IDS:
        base_record_id = mapping[pk_record_id]
        row = rows_by_coordinate.get(f"{BLOCK_ID}:{base_record_id}:0")
        expected_translation = TRANSLATIONS_BY_RECORD[pk_record_id]
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["semantic_review"] != "approved"
            or row["translation"] != expected_translation
            or (
                expected_translation == ""
                and row.get("empty_runtime_morpheme") is not True
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base policy drifted: "
                f"{base_record_id}"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != TRANSLATIONS
        or len(translations) != 66
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
        or len(ZERO_MORPHEME_COORDINATES) != 17
        or HELPERS.canonical_sha256(
            tuple(sorted(ZERO_MORPHEME_COORDINATES))
        )
        != EXPECTED_ZERO_MORPHEME_COORDINATE_SHA256
        or {
            RECORD_TO_ROOT[int(coordinate.split(":")[1])]
            for coordinate in ZERO_MORPHEME_COORDINATES
        }
        != ZERO_MORPHEME_ROOTS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    BASE_LEFT.assert_semantics(dict(BASE_LEFT.RAW_TRANSLATIONS))
    BASE_RIGHT.assert_semantics(dict(BASE_RIGHT.RAW_TRANSLATIONS))
    for pk_record_id, translation in TRANSLATIONS_BY_RECORD.items():
        if translation != BASE_POLICY[pk_record_id - 68]:
            raise RuntimeError(
                f"segment {SEGMENT} mapped policy drifted: {pk_record_id}"
            )
    for coordinate, translation in translations.items():
        if (
            "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    translations: dict[str, str],
) -> tuple[bytes, str]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        (BLOCK_ID, record_id, 0): translations[
            f"{BLOCK_ID}:{record_id}:0"
        ]
        for record_id in RECORD_IDS
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
            f"segment {SEGMENT} candidate record universe drifted"
        )
    target_keys = set(RECORD_KEYS)
    for key, record in current.items():
        if key not in target_keys and candidate_records[key].data != record.data:
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for record_id in RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if (
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            or literal_texts(candidate_records, key)
            != (TRANSLATIONS_BY_RECORD[record_id],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate target drifted: {key}"
            )
    for record_id in HIDDEN_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if candidate_records[key].data != current[key].data:
            raise RuntimeError(
                f"segment {SEGMENT} hidden record changed: {key}"
            )
    if ENGINE.rebuild_packed_with_literals(candidate, reverse) != (
        resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    if resource.current_path.read_bytes() != resource.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} Steam PK input changed during build"
        )
    candidate_sha256 = hashlib.sha256(candidate).hexdigest().upper()
    if candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} candidate digest drifted"
        )
    return candidate, candidate_sha256


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    bytes,
    str,
    int,
]:
    assert_tracked_builder_source_redacted()
    BASE_RIGHT.assert_empty_runtime_morpheme_gate()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    mapping, offset = discover_mapping(records_by_label)
    assert_sources(records_by_label, mapping)
    call_evidence = assert_runtime_graph(records_by_label)
    assert_boundaries(records_by_label)
    assert_completed_base_policy(prepared, mapping)
    translations = dict(TRANSLATIONS)
    assert_semantics(translations)

    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for coordinate, translation in translations.items():
        _, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            current, (BLOCK_ID, record_id)
        )[literal_id]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected line drifted: {coordinate}"
            )

    candidate, candidate_sha256 = build_candidate(
        prepared,
        records_by_label,
        translations,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        root = RECORD_TO_ROOT[record_id]
        evidence = call_evidence[str(root)]
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target[
                "source_record_raw_sha256"
            ],
            "current_ko_utf16le_sha256": target[
                "current_ko_utf16le_sha256"
            ],
            "translation": translation,
            "semantic_review": "approved",
            "scope_classification": "runtime_fragment_pending",
            "layout_review": "unchanged_from_current",
            "runtime_review": "pending",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "source_free_current_caller_evidence": list(
                CALLER_INTEGRATION_EVIDENCE.get(root, ())
            ),
            "source_free_source_only_caller_evidence": list(
                SOURCE_ONLY_FLATTEN_EVIDENCE.get(root, ())
            ),
            "runtime_assembly_evidence": {
                "root": root,
                "full_terminal_record_ids": list(FULL_PK_GROUPS[root]),
                "owned_terminal_record_ids": [
                    value
                    for value in FULL_PK_GROUPS[root]
                    if value in OWNED_RECORD_IDS
                ],
                "base_semantic_record_id":
                mapping[record_id],
                "mapping_proof":
                "completed_base_explicit_map_plus_unique_pk_anchor",
                "pk_specific_morphology_divergence":
                record_id in MAPPED_DIVERGENT_IDS,
                "source_call_count": evidence[0][0],
                "current_call_count": evidence[1][0],
                "source_fixed_following_count": evidence[0][2],
                "current_fixed_following_count": evidence[1][2],
                "source_calls_flattened_in_current": evidence[2][0],
                "current_only_call_count": evidence[2][2],
                "incoming_jump_graph_guarded": True,
                "valid_incoming_014c_count": 0,
                "automatic_space_inserted": False,
                "runtime_integration_required": True,
                "caller_rewrite_required_before_runtime_approval": True,
                "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                "source_free_caller_integration_examples": list(
                    CALLER_INTEGRATION_EVIDENCE.get(root, ())
                ),
                "source_free_source_only_integration_examples": list(
                    SOURCE_ONLY_FLATTEN_EVIDENCE.get(root, ())
                ),
            },
        }
        if coordinate in ZERO_MORPHEME_COORDINATES:
            row["empty_runtime_morpheme"] = True
            row["empty_runtime_morpheme_kind"] = (
                ZERO_MORPHEME_KIND_BY_ROOT[root]
            )
            assembly_evidence = row["runtime_assembly_evidence"]
            if not isinstance(assembly_evidence, dict):
                raise RuntimeError(
                    f"segment {SEGMENT} runtime assembly evidence drifted"
                )
            assembly_evidence["korean_zero_morpheme_caller_review"] = (
                "approved"
            )
            assembly_evidence["empty_runtime_morpheme_source_jp"] = (
                literal_texts(source, (BLOCK_ID, record_id))[literal_id]
            )
        rows.append(row)
    changed = sum(
        translations[f"{BLOCK_ID}:{record_id}:0"]
        != literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RECORD_IDS
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    return (
        prepared,
        translations,
        rows,
        candidate,
        candidate_sha256,
        offset,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, translations, rows, candidate, candidate_sha256, offset = first
    if (
        translations != second[1]
        or ENGINE.jsonl(rows) != ENGINE.jsonl(second[2])
        or candidate != second[3]
        or candidate_sha256 != second[4]
        or offset != second[5]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if (
        len(rows) != 66
        or len(validated) != 66
        or sum(
            row.get("empty_runtime_morpheme") is True
            for row in rows
        )
        != 17
        or any(
            row["scope_classification"] != "runtime_fragment_pending"
            or row["runtime_review"] != "pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision classification drifted"
        )
    current = archive_records(prepared)["pk_current"]
    changed = sum(
        translations[f"{BLOCK_ID}:{record_id}:0"]
        != literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RECORD_IDS
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B007_S1044",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [134, 199],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "owned_record_count": len(OWNED_RECORD_IDS),
                "source_literal_count": len(RECORD_IDS),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": len(HIDDEN_RECORD_IDS),
                "empty_runtime_morpheme_count":
                len(ZERO_MORPHEME_COORDINATES),
                "changed_literal_count": changed,
                "caller_integration_example_class_counts":
                EXPECTED_INTEGRATION_CLASS_COUNTS,
                "source_only_example_class_counts":
                EXPECTED_SOURCE_ONLY_CLASS_COUNTS,
                "base_mapping_method":
                "completed_base_explicit_map_plus_unique_pk_anchor",
                "mapped_pk_specific_morphology_divergence_count":
                len(MAPPED_DIVERGENT_IDS),
                "discovered_base_record_range": [2539, 2608],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256": EXPECTED_SOURCE_SHA256,
                "pk_source_anchor_sha256":
                EXPECTED_PK_SOURCE_ANCHOR_SHA256,
                "pk_current_anchor_sha256":
                EXPECTED_PK_CURRENT_ANCHOR_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "mapping_sha256": EXPECTED_MAPPING_SHA256,
                "mapped_divergence_evidence_sha256":
                EXPECTED_DIVERGENCE_EVIDENCE_SHA256,
                "hidden_raw_sha256": EXPECTED_HIDDEN_RAW_SHA256,
                "pk_target_incoming_sha256": PK_TARGET_EDGE[1],
                "pk_owned_incoming_sha256": PK_OWNED_EDGE[1],
                "pk_full_group_incoming_sha256": PK_FULL_EDGE[1],
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "all_caller_context_sha256":
                EXPECTED_ALL_CALLER_CONTEXT_SHA256,
                "zero_morpheme_coordinate_sha256":
                EXPECTED_ZERO_MORPHEME_COORDINATE_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root1114_full_policy": list(LEFT_BOUNDARY_POLICY),
                "right_root1198_full_policy": list(RIGHT_BOUNDARY_POLICY),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "hidden_non_display_raw_exact": True,
                "full_graph_closures_exact": True,
                "call_fixed_flatten_evidence_exact": True,
                "source_free_current_caller_evidence_exact": True,
                "source_free_source_only_caller_evidence_exact": True,
                "all_caller_contexts_exact": True,
                "zero_morpheme_gate_exact": True,
                "s1043_root1114_boundary_contract_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_read_only": True,
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
