#!/usr/bin/env python3
"""Build source-redacted PK B014 segment 1063 residual decisions."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch012_segment1059.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B014_S1063.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B013_S1060.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B013_S1061.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B013_S1062.private.v1.jsonl",
)

SEGMENT = 1063
QUEUE_BATCH_ID = "pk_msggame-B014"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 4
PK_RECORD_COUNT = 21_751

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1063_common",
        COMMON_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {COMMON_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_common()
ENGINE = COMMON.ENGINE

TARGET_COORDINATES = (
    "4:94:0",
    "4:95:0",
    "4:96:0",
    "4:97:0",
    "4:98:0",
    "4:99:0",
    "4:100:0",
    "4:101:0",
    "4:102:0",
    "4:103:0",
    "4:103:1",
    "4:104:0",
    "4:105:0",
    "4:106:0",
    "4:108:0",
    "4:109:0",
    "4:110:0",
    "4:111:0",
    "4:112:0",
    "4:113:0",
    "4:114:0",
    "4:115:0",
    "4:116:0",
    "4:117:0",
    "4:118:0",
    "4:119:0",
    "4:120:0",
    "4:121:0",
    "4:122:0",
    "4:123:0",
    "4:124:0",
    "4:125:0",
    "4:126:0",
    "4:127:0",
    "4:128:0",
    "4:129:0",
    "4:130:0",
    "4:131:0",
    "4:132:0",
    "4:133:0",
    "4:134:0",
    "4:135:0",
    "4:136:0",
    "4:137:0",
    "4:138:0",
    "4:139:0",
    "4:140:0",
    "4:141:0",
    "4:142:0",
    "4:143:0",
    "4:144:0",
    "4:145:0",
    "4:146:0",
    "4:147:0",
    "4:148:0",
    "4:149:0",
    "4:150:0",
    "4:151:0",
    "4:152:0",
    "4:153:0",
)

TRANSLATIONS = {
    "4:94:0": "이미 소지한 무장이 있어 선택할 수 없습니다",
    "4:95:0": "철포가 전래되기 전이므로 선택할 수 없습니다",
    "4:96:0": "외교할 세력을 선택하십시오",
    "4:97:0": (
        "종속 중에는 종주 세력 외에는 외교할 수 없습니다"
    ),
    "4:98:0": "타 가문에 종속된 세력과는 외교할 수 없습니다",
    "4:99:0": "신용을 설정합니다",
    "4:100:0": "외교 관계를 동맹으로 설정합니다",
    "4:101:0": "이미 동맹을 맺었습니다",
    "4:102:0": (
        "멀리 떨어진 세력과는 동맹을 맺을 수 없습니다"
    ),
    "4:103:0": "을(를)",
    "4:103:1": "에 종속시킵니다",
    "4:104:0": (
        "대상 세력 및 그 종속 세력과 인접하지 않습니다"
    ),
    "4:105:0": "이미 종속되어 있습니다",
    "4:106:0": "외교 관계를 정전으로 설정합니다",
    "4:108:0": "파기할 외교 관계가 없습니다",
    "4:109:0": "편집할 성을 선택하십시오",
    "4:110:0": "병력을 설정합니다",
    "4:111:0": "내구도를 설정합니다",
    "4:112:0": "성하 시설을 설정합니다",
    "4:113:0": "군내 취락 장악 수를 설정합니다",
    "4:114:0": "병량을 설정합니다",
    "4:115:0": "병력을 설정합니다",
    "4:116:0": "기마 LV를 설정합니다",
    "4:117:0": "철포 LV를 설정합니다",
    "4:118:0": (
        "철포가 전래되기 전이므로 설정할 수 없습니다"
    ),
    "4:119:0": "휴대 군량을 설정합니다",
    "4:120:0": "얼굴 CG를 설정합니다",
    "4:121:0": "음성을 설정합니다",
    "4:122:0": "소속 세력을 설정합니다",
    "4:123:0": (
        "신분을 올립니다\n"
        "아시가루 대장은 영주, 사무라이 대장은 성주, "
        "가로는 군단장으로 임명할 수 있습니다"
    ),
    "4:124:0": "더 이상 신분을 올릴 수 없습니다",
    "4:125:0": "다이묘는 변경할 수 없습니다",
    "4:126:0": "무장의 소속 세력을 변경합니다",
    "4:127:0": "직위 취임 조건을 충족하지 못했습니다",
    "4:128:0": "의 장악 현황을 변경합니다",
    "4:129:0": "상위 취락을 장악합니다",
    "4:130:0": "장악할 수 있는 상위 취락이 없습니다",
    "4:131:0": "이미 장악했습니다",
    "4:132:0": "출진 중인 부대가 없습니다",
    "4:133:0": (
        "게임 중 편집하면 업적을 획득할 수 없습니다\n"
        "계속하시겠습니까?"
    ),
    "4:134:0": (
        "게임 중 편집하면 트로피를 획득할 수 없습니다\n"
        "계속하시겠습니까?"
    ),
    "4:135:0": "더 이상 외교 관계를 맺을 수 없습니다",
    "4:136:0": "멀리 떨어진 세력과는 외교할 수 없습니다",
    "4:137:0": "보급 군량을 설정합니다",
    "4:138:0": "방위 병력을 설정합니다",
    "4:139:0": "각종 데이터를 편집합니다",
    "4:140:0": (
        "각종 데이터를 편집합니다\n"
        "게임 중 편집하면 업적을 획득할 수 없습니다"
    ),
    "4:141:0": (
        "각종 데이터를 편집합니다\n"
        "게임 중 편집하면 트로피를 획득할 수 없습니다"
    ),
    "4:142:0": "세력 고유 정책을 설정합니다",
    "4:143:0": "정책의 발령 상태를 설정합니다",
    "4:144:0": (
        "【성명 표시】\n"
        "무장 성명의 표시 순서를 전환합니다\n"
        "\n"
        "[성-이름]\n"
        "성-이름 순으로 표시합니다\n"
        "\n"
        "[이름-성]\n"
        "이름-성 순으로 표시합니다"
    ),
    "4:145:0": (
        "【확인 메시지】\n"
        "각종 명령에서 표시되는 확인 메시지를 설정합니다\n"
        "\n"
        "[사용자 설정]\n"
        "‘다음부터 표시하지 않음’을 선택한 메시지를 제외하고 표시합니다\n"
        "\n"
        "[모두 표시]\n"
        "모든 확인 메시지를 표시합니다"
    ),
    "4:146:0": (
        "【난이도】\n"
        "게임의 난이도를 설정합니다\n"
        "\n"
        "[매우 쉬움]\n"
        "느긋하게 즐기고 싶은 사람에게 추천\n"
        "[쉬움]\n"
        "적당한 난이도를 즐기고 싶은 사람에게 추천\n"
        "[보통]\n"
        "게임에 익숙한 사람에게 추천\n"
        "[어려움]\n"
        "도전적인 난이도를 원하는 사람에게 추천\n"
        "[매우 어려움]\n"
        "더 높은 경지를 목표로 하는 사람에게 추천\n"
        "[사용자 지정]\n"
        "취향에 맞는 난이도로 즐기고 싶은 사람에게 추천"
    ),
    "4:147:0": "《노부나가의 야망·신생 파워업키트》",
    "4:148:0": (
        "《노부나가의 야망·신생 파워업키트》가 발매되었습니다!\n"
        "다양한 추가 요소 중 일부를 소개합니다!\n"
        "더욱 진화한 “군신일체의 전국 체험”을 즐겨 보십시오.\n"
        "\n"
        "·모든 성이 전용 전장이 되는 시리즈 최대 규모의 “공성전”\n"
        "·“군단 전략”과 “평정중”이 선보이는 새로운 전략, "
        "무장의 교섭 제안 “직담”\n"
        "·휴대 군량을 보급할 수 있는 거점 등 성에 역할을 "
        "부여하는 “성 역할”\n"
        "·자유롭게 즐기는 편집 기능 “영지 변경”“신규 세력 생성”"
        "“실존 무장 편집”\n"
        "·“자동 지행”“이벤트 전투”를 비롯해 새로운 시나리오와 "
        "정책도 충실"
    ),
    "4:149:0": (
        "마우스 조작으로 전환되었습니다\n"
        "μ 또는 ν로 조작 방식을 전환할 수 있습니다"
    ),
    "4:150:0": "컨트롤러 조작으로 전환되었습니다",
    "4:151:0": "마우스가 연결되었습니다",
    "4:152:0": (
        "마우스가 연결되었습니다\n"
        "Joy-Con 2의 마우스 조작이 비활성화되었습니다"
    ),
    "4:153:0": (
        "Joy-Con 2 마우스 조작은\n"
        "Joy-Con 2를 양손에 하나씩 들고 사용할 때\n"
        "활성화됩니다"
    ),
}

DYNAMIC_COORDINATES = {
    "4:103:0",
    "4:103:1",
    "4:128:0",
}
STATIC_COORDINATES = set(TARGET_COORDINATES) - DYNAMIC_COORDINATES
TARGET_RECORD_IDS = tuple(
    sorted({int(value.split(":")[1]) for value in TARGET_COORDINATES})
)
DYNAMIC_RECORD_IDS = (103, 128)
BOUNDARY_RECORD_IDS = (93, 154)

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0C896D40AEF1CA90CC670EECD9818B41FD1F26DFF00F7386C69DF774566425C6"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "3282F46FA096054E517FADE6D53CDB9077C6082412C72A94B9569AD736B37075"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "3AADB42F444D30EF67F12C2F2050F8033EC4CF76A59BE7C908093E6D3D342346"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "84BD06FE6F5C13C54387384D55939D824C8AE22CA0723106949ED104C4A71D83"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "1D153510EE8DCE7D9AA2BED98B7F0E2BE8D9F3C8482775C81CEDAC37BB933C6F"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "BF0D5CB2298BAE9F67D436A0F5BB0D06DE98C72C9637890710125B6D3C578BBE"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "74460210E60BA8ED3D433C4F0B8F4E3E83FD38B9EC7433C4EA482C52E9F2312F"
)
EXPECTED_BOUNDARY_SHA256 = (
    "978E0B8849CCE26B65AB9A7FE52D275DD7C4E22C09DDA1848F67DD5E44E65FFA"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "11BA72F844E3248BC27DDB32C31889AA97AF08D183FD60B697CB253A06F22A68"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "9ECB2A4CFB10B97F53365E3CE97BFFF0896C2D7F7F719B2840B72AC2A47FE9C4"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F8D398F4087AB136FCA7BBA6B8D57B4998CE04C0FC1F4D4C9D6EA842E9A87A95"
)
EXPECTED_CHANGED_LITERAL_COUNT = 42

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; Base exact reuse prefill and "
    "all available decisions through optional S1062 are validated and "
    "excluded; adjacent records, complete dynamic assemblies, historical "
    "ranks, game terminology, UI register, protected signatures, line "
    "counts, bytecode gaps, reverse overlay, two-run reproduction, "
    "tamper rejection and read-only inputs are guarded; dynamic fragments "
    "remain runtime pending without automatic promotion"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def coordinate_key(value: str) -> tuple[int, int, int]:
    return COMMON.coordinate_key(value)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return COMMON.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return COMMON.gap_bytes(record)


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return COMMON.read_jsonl(path)


def patch_common_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
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
        "DYNAMIC_RECORD_IDS": set(DYNAMIC_RECORD_IDS),
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(COMMON, name, value)


def context_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return COMMON.context_records(prepared)


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
    )

    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 202
        or len(visible) != 200
        or visible[0] != "4:94:0"
        or visible[-1] != "6:416:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B014 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )

    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 7:
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice count drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )

    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
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
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )

    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
        )

    optional_present: list[str] = []
    for path in OPTIONAL_PREDECESSORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
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
        for record_id in TARGET_RECORD_IDS
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
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
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
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    guarded_digest(
        "source target",
        source_target,
        EXPECTED_SOURCE_TARGET_SHA256,
    )
    guarded_digest(
        "current target",
        current_target,
        EXPECTED_CURRENT_TARGET_SHA256,
    )
    guarded_digest(
        "multilingual context",
        corpus,
        EXPECTED_CONTEXT_CORPUS_SHA256,
    )
    guarded_digest(
        "gap contract",
        gaps,
        EXPECTED_GAP_CONTRACT_SHA256,
    )
    guarded_digest(
        "boundary",
        boundary,
        EXPECTED_BOUNDARY_SHA256,
    )

    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if (
            b"\x01\x43"
            in b"".join(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            )
            or b"\x02"
            in b"".join(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            )
        )
    )
    guarded_digest(
        "dynamic record",
        actual_dynamic,
        EXPECTED_DYNAMIC_RECORD_SHA256,
    )
    if actual_dynamic != DYNAMIC_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
        or len(DYNAMIC_COORDINATES) != 3
        or len(STATIC_COORDINATES) != 57
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation ordering drifted"
        )
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
    if (
        ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source-redaction policy drifted"
        )

    current = records_by_label["current"]
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
        dynamic = coordinate in DYNAMIC_COORDINATES
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending" if dynamic else "unchanged_from_current",
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

    if (
        TRANSLATIONS["4:103:0"] != "을(를)"
        or TRANSLATIONS["4:103:1"] != "에 종속시킵니다"
        or TRANSLATIONS["4:123:0"].splitlines()[1].count(
            "대장"
        )
        != 2
        or "가로는 군단장" not in TRANSLATIONS["4:123:0"]
        or "다이묘" not in TRANSLATIONS["4:125:0"]
        or "군신일체" not in TRANSLATIONS["4:148:0"]
        or "평정중" not in TRANSLATIONS["4:148:0"]
        or "직담" not in TRANSLATIONS["4:148:0"]
        or "자동 지행" not in TRANSLATIONS["4:148:0"]
        or "Joy-Con 2" not in TRANSLATIONS["4:153:0"]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology or assembly drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_gaps = gap_bytes(
        records_by_label["jp"][(BLOCK_ID, record_id)]
    )
    current_gaps = gap_bytes(
        records_by_label["current"][(BLOCK_ID, record_id)]
    )
    source_runtime = tuple(
        value.hex().upper()
        for value in source_gaps
        if b"\x01\x43" in value or b"\x02" in value
    )
    current_runtime = tuple(
        value.hex().upper()
        for value in current_gaps
        if b"\x01\x43" in value or b"\x02" in value
    )
    if not source_runtime or not current_runtime:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic record lost controls: "
            f"{record_id}"
        )
    return {
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in source_gaps)
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in current_gaps)
        ),
        "source_runtime_gap_hex": source_runtime,
        "current_runtime_gap_hex": current_runtime,
        "complete_record_assembly_reviewed": True,
        "prefill_companion_reviewed": True,
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
    patch_common_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )

    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        dynamic = coordinate in DYNAMIC_COORDINATES
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
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
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending"
                if dynamic
                else "retranslated"
            ),
            "layout_review": (
                "runtime_pending"
                if dynamic
                else "unchanged_from_current"
            ),
            "runtime_review": (
                "pending" if dynamic else "not_required"
            ),
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "optional_s1062_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "historical_term_review": True,
            "ui_register_review": True,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
        }
        if dynamic:
            row["runtime_assembly_evidence"] = (
                runtime_control_evidence(
                    records_by_label,
                    record_id,
                )
            )
        rows.append(row)
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
    patch_common_globals()
    COMMON.assert_tamper_rejection(
        prepared,
        rows,
        candidate,
    )


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
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )

    steam_path = prepared.resources["pk_msggame"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
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
        len(rows) != 60
        or len(validated) != 60
        or counts
        != Counter(
            {
                "retranslated": 57,
                "runtime_fragment_pending": 3,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
            if row["scope_classification"]
            == "runtime_fragment_pending"
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
            if row["scope_classification"] == "retranslated"
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B014_S1063",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "target_record_count": len(TARGET_RECORD_IDS),
                "block_ids": [BLOCK_ID],
                "exact_reuse_prefill_count": 7,
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_s1062_validated_if_present": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_terms_reviewed": [
                    "ashigaru_taisho",
                    "samurai_taisho",
                    "karo",
                    "daimyo",
                    "gunshin_ittai",
                    "hyōjōshū",
                    "jikidan",
                    "chigyō",
                ],
                "historic_korean_used": False,
                "switch_korean_used": False,
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
