#!/usr/bin/env python3
"""Build PK-loaded shared ``strdata`` manual UI batch B01.

The batch starts from the exact pristine PC SC transaction backup.  It uses
the pinned PC JP table and Switch v1.3 table only as review inputs, applies
the two already-published shared-runtime overlays first, then adds 206
disjoint block/slot translations.  No installed game file is written.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
STRDATA_ROOT = REPO_ROOT / "workstreams" / "switch_msgbre_v11"
for import_root in (TOOLS_ROOT, STRDATA_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from strdata_container import parse_strdata, rebuild_strdata  # noqa: E402


def _load_direct_builder() -> Any:
    path = (
        REPO_ROOT
        / "workstreams"
        / "switch_strdata_v13_direct_transfer"
        / "build_switch_strdata_v13_direct_transfer.py"
    )
    spec = importlib.util.spec_from_file_location(
        "strdata_direct_upstream_for_manual_b01", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load direct-transfer builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


direct = _load_direct_builder()

RESOURCE = "MSG/SC/strdata.bin"
BATCH_ID = "strdata-pk-shared-manual-b01-206-v1"
OVERLAY_ID = BATCH_ID
OVERLAY_NAME = "strdata_ko_pk_shared_manual_b01_206.v1.json"
EVIDENCE_NAME = "strdata_pk_shared_manual_b01_evidence.v1.json"
REVIEW_NAME = "strdata_pk_shared_manual_b01_review.v1.json"
VALIDATION_NAME = "translation_validation.v1.json"
OVERLAY_SCHEMA = "nobu16.kr.strdata-block-overlay.v1"
SELF_LOGICAL_PATH = (
    "workstreams/strdata_pk_shared_manual_b01/public/"
    + OVERLAY_NAME
)
TARGET_CATALOG = REPO_ROOT / "data" / "public" / "translation_target_keys.v0.1.json"
PROGRESS = REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json"
DEFAULT_SWITCH_ZIP = direct.DEFAULT_SWITCH_ZIP

TARGET_CATALOG_PIN = {
    "size": 2_985_420,
    "sha256": "E4207003341C214C7C124A9BC9A82E475851FF44D3B4C84A941F5E76F42DF142",
    "target_count": 26_690,
    "target_coordinates_sha256": "45DEA7C11E0369AA628B592FEEE375334B60BC493932601516E169689923BBC5",
}
PREDECESSORS = (
    {
        "path": (
            "workstreams/switch_strdata_v13_direct_transfer/public/"
            "strdata_ko_switch_v13_direct_transfer_24424.v1.json"
        ),
        "entry_count": 24_424,
        "size": 5_169_221,
        "sha256": "2C4B1F7C52D5B04EE915693C20D4662011E18A3B6535212905609B3ABBA9FE98",
    },
    {
        "path": (
            "workstreams/strdata_pk_shared_ui/public/"
            "strdata_ko_pk_shared_ui_b01_1.v1.json"
        ),
        "entry_count": 1,
        "size": 1_142,
        "sha256": "DF58FD55FF17F5AA39F73DF4445360BA9BE18AC9C87E3B7E245F07C359EC5A4D",
    },
)
EXPECTED = {
    "total_slots": 32_311,
    "target_count": 26_690,
    "published_predecessor_coverage": 24_425,
    "remaining_before_b00_exclusion": 2_265,
    "b00_excluded_count": 100,
    "eligible_remaining": 2_165,
    "selected_count": 206,
    "selected_per_block": {"0": 146, "1": 60, "2": 0, "3": 0, "4": 0},
    "selected_coordinates_sha256": "1DCC321EEA9B82376EF5BAD41510091EA7C4B99A0DDCADEACF70E6F57EEBCAD5",
    "coverage_after": 24_631,
    "remaining_after": 2_059,
}

HAN_OR_KANA_RE = re.compile(
    r"[\u2e80-\u2fff\u3040-\u30ff\u31f0-\u31ff"
    r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")


class ManualBatchError(ValueError):
    """Raised when an input, translation, or rebuild proof changes."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def canonical_hash(value: Any) -> str:
    return sha256(
        json.dumps(
            value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.relative_to(WORKSTREAM_ROOT).as_posix()
        if path.is_relative_to(WORKSTREAM_ROOT)
        else str(path),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=common.strict_object
    )
    if not isinstance(value, dict):
        raise ManualBatchError(f"JSON root is not an object: {path}")
    return value


def coordinate_texts(archive: Any) -> dict[tuple[int, int], str]:
    return {
        (block.block_id, slot_id): value
        for block in archive.blocks
        for slot_id, value in enumerate(block.texts)
    }


def _scenario_overrides() -> dict[tuple[int, int], str]:
    return {
        (0, 15047): (
            "아시카가 쇼군가와 간레이가 호소카와 하루모토의 권위는 실추하고,\n"
            "중앙에는 권력의 공백이 생겨났다. 수많은 군웅이 할거하며\n"
            "전국의 세상이 새 국면을 맞는 가운데, 오와리 땅에서\n"
            "오다 노부히데의 적자 깃포시가 겐푸쿠를 치른다. 이로써\n"
            "한 영웅의 기나긴 이야기가 시작되려 하고 있었다."
        ),
        (0, 15050): (
            "쇼군 아시카가 요시아키는 미노를 공략한 노부나가와 함께\n"
            "상경하여 숙원인 쇼군가 재흥을 이루었다. 노부나가의 패권을\n"
            "막으려 여러 다이묘가 일어서는 가운데, 두 사람 사이에는\n"
            "점차 알력이 생기기 시작한다. 천하포무를 이루려는 노부나가 앞에\n"
            "생애 최대의 위기가 기다리고 있었다."
        ),
        (0, 15053): (
            "벳쇼·아라키·마쓰나가 등의 잇따른 반란으로 고립된\n"
            "하시바 히데요시는 이 궁지를 기회로 삼아 마침내 오다 가문에서\n"
            "독립하기로 결심했다. 도모의 아시카가 요시아키, 친아버지를\n"
            "은거시킨 도쿠가와 노부야스 등과 뜻을 모은 히데요시는\n"
            "만반의 준비를 갖추고 옛 주군 오다 노부나가와 직접 맞선다."
        ),
        (0, 15054): (
            "여러 다이묘의 포위망을 깨고 쇼군 아시카가 요시아키를\n"
            "추방한 노부나가는 기나이를 손에 넣었다. 휘하에 이반자를\n"
            "안은 가운데, 신겐 사후 다케다 가문을 이은 다케다 가쓰요리와\n"
            "결전을 벌인다. 노부나가의 천하 통일 사업은 마침내\n"
            "절정으로 치달으려 하고 있었다."
        ),
        (0, 15055): (
            "노부나가가 죽은 뒤 아케치와 시바타를 굴복시킨\n"
            "하시바 히데요시는 실질적인 오다 가문의 계승자가 되었다.\n"
            "명목상 당주 오다 노부카쓰는 그와 맞서 다섯 나라를 다스리는\n"
            "도쿠가와 이에야스와 손을 잡는다. 원숭이와 너구리라 불린\n"
            "전국의 두 영걸이 결전에 나서려 하고 있었다."
        ),
    }


def _asset_label_overrides() -> dict[tuple[int, int], str]:
    """Translate the 85 label keys and retain SC's U+E003 delimiter."""
    rows: list[tuple[int, str, int]] = []

    def add(start: int, label: str, levels: Iterable[int]) -> None:
        for offset, level in enumerate(levels):
            rows.append((start + offset, label, level))

    add(17802, "호화 평성", [3])
    add(17803, "호화 산성", [1, 2, 3])
    add(17806, "병력 소", [1, 2, 3])
    add(17809, "병력 군마", [2, 3])
    add(17811, "병력 철포", [3])
    add(17812, "금전 소", [1, 2, 3])
    add(17815, "금전 군량", [2, 3])
    add(17817, "금전 병력 회복", [3])
    add(17818, "금전 중", [1, 2, 3])
    add(17821, "금전 정무", [3])
    add(17822, "광산", [1, 2, 3])
    add(17825, "은산", [1, 2, 3])
    add(17828, "금산", [1, 2, 3])
    add(17831, "군량 소", [1, 2, 3])
    add(17834, "군량 민충", [2, 3])
    add(17836, "군량 대", [1, 2, 3])
    add(17839, "군량 금전", [2, 3])
    add(17841, "군량 치수", [3])
    add(17842, "군마 소", [1, 2, 3])
    add(17845, "군마 금전", [2, 3])
    add(17847, "군마 통솔", [3])
    add(17848, "군마 대", [1, 2, 3])
    add(17851, "철포 대", [1, 2, 3])
    add(17854, "민충 소", [1, 2, 3])
    add(17857, "민충 병력", [2, 3])
    add(17859, "병력 회복", [1, 2, 3])
    add(17862, "병과 철포", [2, 3])
    add(17864, "병과 무용", [3])
    add(17865, "민충 대", [1, 2, 3])
    add(17868, "민충 지략", [3])
    add(17869, "토호", [1, 2, 3])
    add(17872, "장원", [1, 2, 3])
    add(17875, "대호족", [1, 2, 3])
    add(17878, "소촌", [1, 2, 3])
    add(17881, "명주", [1, 2, 3])
    add(17884, "촌장", [1, 2, 3])
    if len(rows) != 85 or [slot for slot, _label, _level in rows] != list(
        range(17802, 17887)
    ):
        raise ManualBatchError("asset-label coordinate construction changed")
    return {
        (0, slot): f"{label}\ue003{level}" for slot, label, level in rows
    }


def _semantic_overrides() -> dict[tuple[int, int], str]:
    return {
        (0, 17892): "정면으로 맞설 적은 어디에도 없었다.",
        (0, 17893): "이마가와군 선봉대는 잇달아 성을 함락시켰다.",
        (0, 17898): "폭우가 모든 소리를 삼키고,",
        (0, 17900): "요시모토는 더위를 식힐 술 한 잔을 들이켰고,",
        (0, 17907): "자신이 베인 줄조차 몰랐을지도 모른다.",
        (0, 17944): "노부나가의 유해는 끝내 발견되지 않았다.",
        (0, 17945): "죽은 주군의 너털웃음이 귓가에서 떠나지 않았다…",
        (0, 17946): "그 목소리는 속마음을 모두 꿰뚫어 본 듯했다.",
        (0, 17953): (
            "여기에는\n소문대로 노부나가가 「멍청이」라면,\n"
            "그 칼로 죽이겠다는 뜻도 담겨 있었다."
        ),
        (0, 17957): "그녀는 장차 남편이 될\n그 남자를 처음 보고 충격을 받았다.",
        (0, 17961): "이 난세를 과감히 바꾸려는 충동.",
        (0, 17963): (
            "하지만 노부나가가 천하를 거머쥘 때 가장 잘 이해해 준 "
            "사람이기도 했다."
        ),
        (0, 17968): (
            "도쿠가와 편으로 돌아선 오쿠다이라 가문을\n"
            "본보기로 삼아 경고해야 한다."
        ),
        (0, 17969): "그러지 않으면 다른 호족들의 신뢰마저 잃게 된다.",
        (0, 17974): (
            "설욕할 기회를 노리던 이에야스는\n"
            "나가시노를 구하려 맹우에게 원군을 청했다."
        ),
        (0, 17982): "마치 철옹성과도 같았다.",
        (0, 17995): (
            "\n그러나 다케다군은 별동대를 보내\n"
            "우에스기군이 지키는 사이조산으로 향하게 했다."
        ),
        (0, 17997): "…\n이 전법을 「딱따구리 전법」이라 불렀다.",
        (0, 17999): "딱따구리 전법이 실패한 것인가……\n초조해진 신겐의 눈에,",
        (0, 18002): "한편 마사토라는 한밤중에 적의 우회를 간파했다.",
        (0, 18008): (
            "\n호위의 창벽을 헤치고\n"
            "마사토라는 말 위에서 칼을 내리쳤다."
        ),
        (0, 19549): "호족을 자세력에 편입",
        (0, 19566): "성의\n무장 충성 감소",
        (0, 20842): "피해 / 「혼란」 부여",
        (0, 20859): "요지 주변 아군 부대가 절벽을 타고 내려가 적 부대를 밀어냄",
        (0, 20863): "강물을 범람시켜 통행 불가. 휩쓸린 적 부대에 피해를 주고 혼란 부여",
        (0, 20942): "피해 / 「혼란」 부여",
        (0, 20959): "아군 강제 이동 / 적 밀어냄",
        (0, 20963): "여러 길 봉쇄 / 피해",
        (0, 22256): "전 가신 무장의 충성 +%d",
        (0, 22282): "호족 종속도 증가량 %+d％",
        (0, 22292): "금산정·은산정의 금전 수입 %+d％",
        (0, 22293): "휘하 무장의 지휘 가능 병력 +%d",
        (0, 22301): "건의 비용 %+d%",
        (0, 22302): "대장간정 효과량 %+d％",
        (0, 22311): "철포 공격 발생률 %+d％",
        (0, 22350): "성하 시설 \x1bC3%s\x1bCZ의 상업 %+d",
        (0, 23194): "특수 영향력 +%d, 상업 +%d",
        (0, 24859): "무장을 파견하지 않으면 매월 %d% 확률로 잇키가 발생",
        (0, 24863): "무장을 파견하지 않으면 매월 %d% 확률로 여러 군에서 잇키가 발생",
        (1, 1665): "부장",
        (1, 2139): "석고 %d％ 상승",
        (1, 2823): "시작 메뉴로 돌아가시겠습니까?",
        (1, 2826): "세이브 데이터를 덮어쓰시겠습니까?",
        (1, 2829): (
            "지금 불러오면 저장하지 않은 진행 내용이 사라집니다.\n"
            "계속하시겠습니까?"
        ),
        (1, 2840): "수행 중인 임무가 없습니다.\n\n지도에서 출진지를 선택해 주십시오.",
        (1, 2895): "저장하지 않고 게임을 계속하시겠습니까?",
        (1, 2898): (
            "자동 저장 데이터가 손상되었습니다.\n"
            "자동 저장 데이터를 삭제한 뒤 다시 시도해 주십시오."
        ),
        (1, 2934): "종료하고 게임을 시작하시겠습니까?",
        (1, 2952): (
            "이 화면 크기로 변경하시겠습니까? 15초 후 원래 크기로 돌아갑니다."
        ),
        (1, 3035): "난이도 변경과 기타 설정은 여기에서 변경할 수 있습니다.",
        (1, 3038): "\x1bCB%s\x1bCZ(으)로 계속하시겠습니까?",
        (1, 3084): (
            "자세력을 컴퓨터에 맡깁니다.\n"
            "데모 플레이를 시작하면\n"
            "도중에 해제할 수 없습니다.\n\n"
            "데모 플레이를 시작하시겠습니까?"
        ),
        (1, 3110): "획득 병량 +%d",
        (1, 3113): "획득 물자 +%d",
        (1, 3120): "병량 %d을(를) %s에 양도(%d→%d)",
        (1, 3124): "설정 내용을 취소하시겠습니까?",
        (1, 3168): "획득 금전 +%d％",
        (1, 3175): "게임을 종료하시겠습니까?",
        (1, 3206): "선택한 등록 무장을 삭제하시겠습니까?",
        (1, 3207): (
            "선택한 등록 무장과의 모든 인간관계가 무효가 됩니다.\n"
            "계속하시겠습니까?"
        ),
        (1, 3223): "%s의 취락 「%s」을(를) 철거하시겠습니까?",
        (1, 3235): (
            "%s은(는) 출진 중인 무장입니다. %s의 지행을 해임하면 "
            "부대에서 이탈합니다. 계속하시겠습니까?"
        ),
        (1, 3238): (
            "%s은(는) 출진 중인 무장입니다. %s의 대관을 해임하면 "
            "부대에서 이탈합니다. 계속하시겠습니까?"
        ),
        (1, 3239): (
            "%s은(는) 출진 중인 무장입니다. %s의 성주를 해임하면 "
            "부대에서 이탈합니다. 계속하시겠습니까?"
        ),
        (1, 3249): "변경하지 않고 돌아가시겠습니까?",
        (1, 3272): "모든 대관을 해임하고 다이묘와 동행시키겠습니까?",
        (1, 3273): "맡긴 군을 지행으로 주어 %s에 남길 무장을 선택하십시오",
        (1, 3281): "%s을(를) 거부하시겠습니까?",
        (1, 3291): "취락 「%s」은(는) 특수 시설이므로 철거할 수 없습니다.",
        (1, 3294): "취락 「%s」을(를) 건설하시겠습니까?",
        (1, 3306): "%s을(를) %s의 영주로 임명하시겠습니까?",
        (1, 3307): "%s을(를) %s의 대관으로 임명하시겠습니까?",
        (1, 3308): "%s을(를) %s %s의 성주로 임명하시겠습니까?",
        (1, 3372): (
            "대상 무장은 이미 가보를 보유하고 있어 교체하게 됩니다.\n"
            "계속하시겠습니까?"
        ),
        (1, 3396): (
            "%s은(는) %s의 영주이므로 해임하게 됩니다.\n"
            "계속하시겠습니까?\n※충성이 낮아질 수 있습니다."
        ),
        (1, 3397): (
            "%s은(는) %s의 성주이므로 해임하게 됩니다.\n"
            "계속하시겠습니까?\n※충성이 낮아질 수 있습니다."
        ),
        (1, 3400): "평정 튜토리얼을 종료하시겠습니까?",
        (1, 3405): (
            "%s은(는) 임무 「%s」 및 건의 「%s」을(를) 수행 중입니다.\n"
            "중지하시겠습니까?"
        ),
        (1, 3439): (
            "추가 콘텐츠 데이터를 찾을 수 없습니다.\n"
            "추가 콘텐츠가 적용된 세이브 데이터는 불러올 수 없습니다."
        ),
        (1, 3462): "\x1bCQ\ue020\x1bCZ공성전 중(강공)",
        (1, 3463): "\x1bCQ\ue021\x1bCZ공성전 중(포위)",
        (1, 3464): (
            "\x1bCQ\ue022\x1bCZ통치 범위 밖의 성\n"
            "어느 군단의 통치하에 들어갈 때까지 수입 감소"
        ),
        (1, 3465): "\x1bCQ\ue023\x1bCZ공략 목표 성",
        (1, 3466): (
            "\x1bCP\ue024\x1bCZ군비 중(%d/%d)　모든 군의 군비 완료까지 %d일\n"
            "　임전 상태인 군 수에 따라 부대 능력 상승, 휴대 병량 일수 증가"
        ),
        (1, 3467): (
            "\x1bCP\ue024\x1bCZ군비(%d/%d)　무장이 출진 중/부상/질병으로 군비 중지\n"
            "　임전 상태인 군 수에 따라 부대 능력 상승, 휴대 병량 일수 증가"
        ),
        (1, 3468): (
            "\x1bCQ\ue024\x1bCZ성주/영주/대관이 있는 모든 군의 군비 완료\n"
            "　임전 상태가 되어 부대 능력 상승, 휴대 병량 일수 증가"
        ),
        (1, 3469): "\x1bCQ\ue028\x1bCZ잇키 발생 중\n　해당 군은 수입 없음, 출진 불가",
        (1, 3470): (
            "\x1bCQ\ue025\x1bCZ병력에 비해 병량 부족\n"
            "　출진 시 휴대 병량은 현재 %d일분"
        ),
        (1, 3471): (
            "\x1bCQ\ue025\x1bCZ병력에 비해 병량이 크게 부족\n"
            "　출진 시 휴대 병량은 현재 %d일분"
        ),
        (1, 3525): "전투 계열 특성이 없습니다.",
        (1, 3612): "\x1bCQ\ue029\x1bCZ성주에게 영지를 추가할 수 있습니다.",
        (1, 3613): "\x1bCQ\ue022\x1bCZ성주가 임명되지 않았습니다.",
        (1, 3663): "\x1bCP\ue024\x1bCZ성대와 군대만 있어 군비할 수 없습니다.",
        (1, 3920): "\ue008\ue015\ue00d으로 명령을 철회합니다.",
    }


def _msgui_terminology_overrides() -> dict[tuple[int, int], str]:
    """Reuse the reviewed PK msgui wording for byte-identical UI messages."""

    return {
        (1, 2307): "\ue00f명령",
        (1, 2308): "\ue00e전투",
        (1, 2826): "저장 데이터를 덮어쓰시겠습니까?",
        (1, 2829): "불러오면 저장하지 않은 진행 상황이 사라집니다.\n계속하시겠습니까?",
        (1, 2840): "수행 중인 임무가 없습니다.\n\n지도에서 출진 목적지를 선택하십시오.",
        (1, 2898): "자동 저장 데이터가 손상되었습니다.\n자동 저장 데이터를 삭제한 뒤 다시 시도하십시오.",
        (1, 2934): "종료 후 게임을 시작하시겠습니까?",
        (1, 2952): "이 화면 크기를 적용하시겠습니까? 15초 후 원래대로 돌아갑니다.",
        (1, 3035): "난이도 변경과 기타 설정은 여기서 할 수 있습니다.",
        (1, 3038): "\x1bCB%s\x1bCZ 세력으로 계속하시겠습니까?",
        (1, 3084): (
            "자세력을 컴퓨터에 맡깁니다.\n데모 플레이를 시작하면\n"
            "중간에 해제할 수 없습니다.\n\n데모 플레이를 시작하시겠습니까?"
        ),
        (1, 3110): "획득 군량 +%d％",
        (1, 3113): "획득 물자 +%d％",
        (1, 3120): "군량 %d, %s에 양도(%d→%d)",
        (1, 3124): "설정 내용을 폐기하시겠습니까?",
        (1, 3235): (
            "%s은(는) 출진 중인 무장입니다. %s의 지행을 해제하면 "
            "부대에서 이탈합니다. 계속하시겠습니까?"
        ),
        (1, 3238): (
            "%s은(는) 출진 중인 무장입니다. %s을(를) 대관직에서 해임하면 "
            "부대에서 이탈합니다. 계속하시겠습니까?"
        ),
        (1, 3239): (
            "%s은(는) 출진 중인 무장입니다. %s을(를) 성주직에서 해임하면 "
            "부대에서 이탈합니다. 계속하시겠습니까?"
        ),
        (1, 3272): "모든 대관을 해임해 다이묘와 동행시키시겠습니까?",
        (1, 3273): "맡은 군을 지행으로 주어 %s에 남길 무장을 선택하십시오",
        (1, 3308): "%s을(를) %s의 %s 성주로 임명하시겠습니까?",
        (1, 3372): "대상 무장은 이미 가보를 보유 중이므로 교체됩니다.\n계속하시겠습니까?",
        (1, 3396): (
            "%s은(는) %s의 영주이므로 해임됩니다.\n계속하시겠습니까?\n"
            "※충성도가 내려갈 수 있습니다."
        ),
        (1, 3397): (
            "%s은(는) %s의 성주이므로 해임됩니다.\n계속하시겠습니까?\n"
            "※충성도가 내려갈 수 있습니다."
        ),
        (1, 3439): (
            "추가 콘텐츠 데이터가 없습니다.\n"
            "추가 콘텐츠가 적용된 저장 데이터는 불러올 수 없습니다."
        ),
        (1, 3462): "\x1bCQ\ue020\x1bCZ공성 중(강공)",
        (1, 3463): "\x1bCQ\ue021\x1bCZ공성 중(포위)",
        (1, 3464): (
            "\x1bCQ\ue022\x1bCZ통치 범위 밖의 성\n"
            "어느 군단의 통치를 받기 전까지 수입이 감소합니다."
        ),
        (1, 3465): "\x1bCQ\ue023\x1bCZ공략 목표 성",
        (1, 3466): (
            "\x1bCP\ue024\x1bCZ군비 중(%d/%d), 모든 군의 군비 완료까지 %d일\n"
            "　임전 상태인 군 수에 따라 부대 능력과 휴대 군량 일수가 증가합니다."
        ),
        (1, 3467): (
            "\x1bCP\ue024\x1bCZ군비 중(%d/%d), 무장이 출진/부상/질병 중이므로 "
            "군비가 중단된 상태입니다.\n"
            "　임전 상태인 군 수에 따라 부대 능력과 휴대 군량 일수가 증가합니다."
        ),
        (1, 3468): (
            "\x1bCQ\ue024\x1bCZ성주/영주/대관이 있는 모든 군의 군비 완료\n"
            "　임전 상태가 되어 부대 능력과 휴대 군량 일수가 증가합니다."
        ),
        (1, 3469): "\x1bCQ\ue028\x1bCZ봉기 발생 중\n　해당 군은 수입이 없고 출진할 수 없습니다.",
        (1, 3470): (
            "\x1bCQ\ue025\x1bCZ병력에 비해 군량이 부족합니다.\n"
            "　현재 출진 시 휴대 군량은 %d일분입니다."
        ),
        (1, 3471): (
            "\x1bCQ\ue025\x1bCZ병력에 비해 군량이 크게 부족합니다.\n"
            "　현재 출진 시 휴대 군량은 %d일분입니다."
        ),
        (1, 3525): "전투 계열 특성이 없습니다",
        (1, 3612): "\x1bCQ\ue029\x1bCZ성주에게 영지를 추가할 수 있습니다.",
        (1, 3613): "\x1bCQ\ue022\x1bCZ성주가 임명되지 않았습니다.",
        (1, 3654): "·설정된 성하 방침을 모두 “위임”으로 변경",
        (1, 3663): "\x1bCP\ue024\x1bCZ성대와 군대만 있어 군비를 진행할 수 없습니다.",
        (1, 3920): "\ue008\ue015\ue00d으로 명령을 철회합니다.",
    }


TRANSLATION_OVERRIDES = {
    **_scenario_overrides(),
    **_asset_label_overrides(),
    **_semantic_overrides(),
    **_msgui_terminology_overrides(),
}


def _replace_source_pua(source_sc: str, source_jp: str, replacement: str) -> str:
    source_pua = [character for character in source_sc if 0xE000 <= ord(character) <= 0xF8FF]
    if not source_pua:
        return replacement
    replacement_pua = [
        character for character in replacement if 0xE000 <= ord(character) <= 0xF8FF
    ]
    if replacement_pua == source_pua:
        return replacement
    if replacement_pua:
        raise ManualBatchError("replacement begins with an unexpected PUA sequence")
    display_glyphs = {
        "\ue008": "㌘",
        "\ue00d": "㍗",
        "\ue00e": "㌍",
        "\ue00f": "㌦",
        "\ue015": "㎝",
        "\ue018": "㊤",
        "\ue019": "㊥",
        "\ue01c": "㊨",
        "\ue020": "┣",
        "\ue021": "┳",
        "\ue022": "┫",
        "\ue023": "┻",
        "\ue024": "╋",
        "\ue025": "┠",
        "\ue028": "┷",
        "\ue029": "┿",
    }
    result = replacement
    for index, pua in enumerate(source_sc):
        if not (0xE000 <= ord(pua) <= 0xF8FF):
            continue
        jp_glyph = source_jp[index] if index < len(source_jp) else ""
        if display_glyphs.get(pua, "") in result:
            result = result.replace(display_glyphs[pua], pua, 1)
        elif jp_glyph and jp_glyph in result:
            result = result.replace(jp_glyph, pua, 1)
        elif "·" in result:
            result = result.replace("·", pua, 1)
        else:
            raise ManualBatchError("cannot reconcile a Switch display glyph with SC PUA")
    if [character for character in result if 0xE000 <= ord(character) <= 0xF8FF] != source_pua:
        raise ManualBatchError("SC PUA sequence did not survive translation repair")
    return result


def _balanced_lines(text: str, count: int) -> list[str]:
    if count <= 1:
        return [text]
    words = text.split()
    if len(words) < count:
        characters = list(text)
        if len(characters) < count:
            raise ManualBatchError("translation is too short for source line structure")
        cuts = [round(len(characters) * index / count) for index in range(count + 1)]
        return ["".join(characters[cuts[index] : cuts[index + 1]]) for index in range(count)]
    result: list[str] = []
    cursor = 0
    for line_index in range(count - 1):
        remaining_lines = count - line_index
        remaining_words = words[cursor:]
        target_width = sum(len(word) for word in remaining_words) + len(remaining_words) - 1
        target_width /= remaining_lines
        end = cursor + 1
        while end < len(words) - (remaining_lines - 1):
            candidate = " ".join(words[cursor : end + 1])
            if len(candidate) > target_width and end > cursor:
                break
            end += 1
        result.append(" ".join(words[cursor:end]))
        cursor = end
    result.append(" ".join(words[cursor:]))
    if any(not line for line in result):
        raise ManualBatchError("line reconciliation produced an empty semantic line")
    return result


def _reconcile_line_and_edge_structure(source_sc: str, replacement: str) -> str:
    before = common.message_invariants(source_sc)
    after = common.message_invariants(replacement)
    if (
        before["line_breaks"] == after["line_breaks"]
        and before["leading_whitespace"] == after["leading_whitespace"]
        and before["trailing_whitespace"] == after["trailing_whitespace"]
    ):
        return replacement
    source_leading = before["leading_whitespace"]
    source_trailing = before["trailing_whitespace"]
    leading_breaks = len(common.LINE_BREAK_RE.findall(source_leading))
    trailing_breaks = len(common.LINE_BREAK_RE.findall(source_trailing))
    internal_breaks = len(before["line_breaks"]) - leading_breaks - trailing_breaks
    core = common.LINE_BREAK_RE.sub(" ", replacement).strip()
    core = re.sub(r"[ \t]+", " ", core)
    lines = _balanced_lines(core, internal_breaks + 1)
    return source_leading + "\n".join(lines) + source_trailing


def make_translation(
    coordinate: tuple[int, int], source_sc: str, source_jp: str, switch_ko: str
) -> tuple[str, str]:
    if coordinate in TRANSLATION_OVERRIDES:
        replacement = TRANSLATION_OVERRIDES[coordinate]
        method = "manual-translation-override"
    else:
        replacement = switch_ko
        method = "manual-switch-semantic-acceptance"
    # U+30FB is classified as Katakana.  Korean typography uses U+00B7.
    replacement = replacement.replace("\u30fb", "·")
    try:
        replacement = _replace_source_pua(source_sc, source_jp, replacement)
    except ManualBatchError as exc:
        raise ManualBatchError(f"{coordinate}: {exc}") from exc
    replacement = _reconcile_line_and_edge_structure(source_sc, replacement)
    mismatches = common.invariant_mismatches(source_sc, replacement)
    if mismatches:
        raise ManualBatchError(f"{coordinate}: format invariant mismatch: {mismatches}")
    if HAN_OR_KANA_RE.search(replacement):
        raise ManualBatchError(f"{coordinate}: replacement still contains Han or Kana")
    if not any(0xAC00 <= ord(character) <= 0xD7A3 for character in replacement):
        raise ManualBatchError(f"{coordinate}: replacement has no Hangul syllable")
    return replacement, method


def load_target_catalog(path: Path) -> tuple[set[tuple[int, int]], dict[str, Any]]:
    blob = path.read_bytes()
    if {
        "size": len(blob),
        "sha256": sha256(blob),
    } != {key: TARGET_CATALOG_PIN[key] for key in ("size", "sha256")}:
        raise ManualBatchError("translation target catalog pin changed")
    catalog = read_json(path)
    resources = [row for row in catalog.get("resources", []) if row.get("path") == RESOURCE]
    if len(resources) != 1:
        raise ManualBatchError("shared strdata target resource is not unique")
    resource = resources[0]
    coordinates = [tuple(value) for value in resource.get("target_coordinates", [])]
    if (
        resource.get("key_kind") != "block_slot_coordinate"
        or resource.get("target_count") != TARGET_CATALOG_PIN["target_count"]
        or resource.get("target_keys_sha256")
        != TARGET_CATALOG_PIN["target_coordinates_sha256"]
        or len(coordinates) != len(set(coordinates))
        or canonical_hash([list(value) for value in coordinates])
        != TARGET_CATALOG_PIN["target_coordinates_sha256"]
    ):
        raise ManualBatchError("shared strdata target coordinate contract changed")
    return set(coordinates), {
        "path": path.relative_to(REPO_ROOT).as_posix(),
        **TARGET_CATALOG_PIN,
    }


def _validate_overlay_entries(
    overlay: dict[str, Any], pc_sc: dict[tuple[int, int], str], label: str
) -> dict[tuple[int, int], str]:
    if overlay.get("schema") != OVERLAY_SCHEMA or overlay.get("resource") != RESOURCE:
        raise ManualBatchError(f"{label}: overlay identity changed")
    entries = overlay.get("entries")
    if not isinstance(entries, list) or overlay.get("entry_count") != len(entries):
        raise ManualBatchError(f"{label}: overlay entry count changed")
    values: dict[tuple[int, int], str] = {}
    for entry in entries:
        coordinate = (entry.get("block_id"), entry.get("slot_id"))
        if not all(type(part) is int for part in coordinate) or coordinate in values:
            raise ManualBatchError(f"{label}: invalid or duplicate coordinate")
        if coordinate not in pc_sc:
            raise ManualBatchError(f"{label}: coordinate is outside strdata")
        replacement = entry.get("ko")
        if (
            not isinstance(replacement, str)
            or entry.get("source_sc_utf16le_sha256") != text_hash(pc_sc[coordinate])
            or common.invariant_mismatches(pc_sc[coordinate], replacement)
        ):
            raise ManualBatchError(f"{label}: source hash or format invariant changed")
        values[coordinate] = replacement
    if sorted(values) != list(values):
        raise ManualBatchError(f"{label}: coordinates are not sorted")
    return values


def load_predecessors(
    repo_root: Path, pc_sc: dict[tuple[int, int], str]
) -> tuple[dict[tuple[int, int], str], list[dict[str, Any]]]:
    values: dict[tuple[int, int], str] = {}
    snapshots: list[dict[str, Any]] = []
    for descriptor in PREDECESSORS:
        path = repo_root / descriptor["path"]
        blob = path.read_bytes()
        if (
            len(blob) != descriptor["size"]
            or sha256(blob) != descriptor["sha256"]
        ):
            raise ManualBatchError(f"predecessor pin changed: {descriptor['path']}")
        overlay = read_json(path)
        current = _validate_overlay_entries(overlay, pc_sc, descriptor["path"])
        if len(current) != descriptor["entry_count"]:
            raise ManualBatchError(f"predecessor entry count changed: {descriptor['path']}")
        overlap = set(values).intersection(current)
        if overlap:
            raise ManualBatchError(f"predecessors overlap at {min(overlap)}")
        values.update(current)
        snapshots.append(dict(descriptor))
    if len(values) != EXPECTED["published_predecessor_coverage"]:
        raise ManualBatchError("published predecessor coordinate union changed")
    return values, snapshots


def select_coordinates(
    targets: set[tuple[int, int]],
    predecessor_values: dict[tuple[int, int], str],
    classified: dict[str, Any],
) -> tuple[list[tuple[int, int]], dict[str, Any]]:
    remaining = targets - set(predecessor_values)
    b00 = {(0, slot_id) for slot_id in range(100)}
    if len(remaining) != EXPECTED["remaining_before_b00_exclusion"] or not b00.issubset(remaining):
        raise ManualBatchError("remaining shared strdata target set changed")
    eligible = remaining - b00
    selected = sorted(
        coordinate
        for coordinate in eligible
        if classified["details"][coordinate]["classification"] == "manual"
        and coordinate[0] in (0, 1)
    )
    per_block = Counter(str(block_id) for block_id, _slot_id in selected)
    actual_per_block = {str(block_id): per_block[str(block_id)] for block_id in range(5)}
    if (
        len(eligible) != EXPECTED["eligible_remaining"]
        or len(selected) != EXPECTED["selected_count"]
        or actual_per_block != EXPECTED["selected_per_block"]
        or canonical_hash([list(value) for value in selected])
        != EXPECTED["selected_coordinates_sha256"]
    ):
        raise ManualBatchError("manual UI selection changed")
    if any(coordinate[0] == 0 and coordinate[1] < 100 for coordinate in selected):
        raise ManualBatchError("B00 exclusion failed")
    return selected, {
        "published_predecessor_coverage": len(predecessor_values),
        "remaining_before_b00_exclusion": len(remaining),
        "b00_excluded_count": len(b00),
        "eligible_remaining": len(eligible),
        "selected_count": len(selected),
        "selected_per_block": actual_per_block,
        "selected_coordinates_sha256": EXPECTED["selected_coordinates_sha256"],
    }


def category_for(coordinate: tuple[int, int]) -> str:
    block_id, slot_id = coordinate
    if block_id == 1:
        if slot_id in (2307, 2308, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470, 3471, 3477, 3478, 3612, 3613, 3663, 3920):
            return "hud_label_or_status_help"
        return "menu_dialog_or_system_prompt"
    if 15047 <= slot_id <= 15055:
        return "scenario_description"
    if 17802 <= slot_id <= 17886:
        return "ui_asset_label"
    if 17892 <= slot_id <= 18008:
        return "event_caption"
    if 19549 <= slot_id <= 20963:
        return "battle_or_management_ui"
    return "policy_effect_or_help"


def make_models(
    inputs: dict[str, Any], classified: dict[str, Any], repo_root: Path
) -> dict[str, Any]:
    pc_sc = classified["pc_sc"]
    targets, target_snapshot = load_target_catalog(repo_root / TARGET_CATALOG.relative_to(REPO_ROOT))
    predecessor_values, predecessor_snapshots = load_predecessors(repo_root, pc_sc)
    selected, selection = select_coordinates(targets, predecessor_values, classified)
    entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    values: dict[tuple[int, int], str] = {}
    category_counts: Counter[str] = Counter()
    method_counts: Counter[str] = Counter()
    for coordinate in selected:
        source_sc = pc_sc[coordinate]
        source_jp = classified["pc_jp"][coordinate]
        switch_ko = classified["switch"][coordinate]
        replacement, method = make_translation(coordinate, source_sc, source_jp, switch_ko)
        category = category_for(coordinate)
        category_counts[category] += 1
        method_counts[method] += 1
        values[coordinate] = replacement
        entries.append(
            {
                "block_id": coordinate[0],
                "slot_id": coordinate[1],
                "source_sc_utf16le_sha256": text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "block_id": coordinate[0],
                "slot_id": coordinate[1],
                "category": category,
                "selection_classification": "manual",
                "translation_method": method,
                "pc_sc_utf16le_sha256": text_hash(source_sc),
                "pc_jp_utf16le_sha256": text_hash(source_jp),
                "switch_v13_utf16le_sha256": text_hash(switch_ko),
                "ko_utf16le_sha256": text_hash(replacement),
                "format_invariants_equal": True,
                "source_free_han_or_kana": True,
            }
        )
        review_entries.append(
            {
                "block_id": coordinate[0],
                "slot_id": coordinate[1],
                "category": category,
                "status": "reviewed",
                "translation_method": method,
                "same_coordinate_switch_reviewed": True,
                "pc_sc_and_jp_context_reviewed": True,
                "format_invariants_equal": True,
                "source_free": True,
            }
        )
    if len(values) != EXPECTED["selected_count"] or set(values) & set(predecessor_values):
        raise ManualBatchError("manual overlay count or predecessor disjointness changed")
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": OVERLAY_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "defaults": {"status": "reviewed"},
        "entries": entries,
    }
    evidence = {
        "schema": "nobu16.kr.strdata-pk-shared-manual-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "entry_count": len(evidence_entries),
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "target_catalog": target_snapshot,
        "predecessors": predecessor_snapshots,
        "selection": selection,
        "category_counts": dict(sorted(category_counts.items())),
        "translation_method_counts": dict(sorted(method_counts.items())),
        "entries": evidence_entries,
    }
    review = {
        "schema": "nobu16.kr.strdata-pk-shared-manual-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "entry_count": len(review_entries),
        "review_policy": {
            "pc_sc_and_jp_context_checked": True,
            "switch_v13_same_coordinate_checked_first": True,
            "ui_menu_label_description_priority": True,
            "block0_slots_0_99_excluded": True,
            "source_free_public_artifacts": True,
        },
        "entries": review_entries,
    }
    return {
        "overlay": overlay,
        "evidence": evidence,
        "review": review,
        "values": values,
        "predecessor_values": predecessor_values,
        "selection": selection,
        "target_snapshot": target_snapshot,
        "category_counts": dict(sorted(category_counts.items())),
        "translation_method_counts": dict(sorted(method_counts.items())),
    }


def audit_progress_registration(
    progress_path: Path,
    repo_root: Path,
    pc_sc: dict[tuple[int, int], str],
    target_coordinates: set[tuple[int, int]],
    predecessor_coordinates: set[tuple[int, int]],
    self_overlay: dict[str, Any],
) -> dict[str, Any]:
    progress = read_json(progress_path)
    resources = [row for row in progress.get("shared_strings", []) if row.get("path") == RESOURCE]
    if len(resources) != 1:
        raise ManualBatchError("progress shared strdata resource is not unique")
    patterns = resources[0].get("overlay_globs")
    if not isinstance(patterns, list) or patterns[: len(PREDECESSORS)] != [
        row["path"] for row in PREDECESSORS
    ]:
        raise ManualBatchError("pinned predecessor registration boundary changed")
    self_blob = encode_json(self_overlay)
    self_coordinates = {
        (entry["block_id"], entry["slot_id"]) for entry in self_overlay["entries"]
    }
    self_count = 0
    successor_coordinates: set[tuple[int, int]] = set()
    successor_paths: list[str] = []
    for pattern in patterns[len(PREDECESSORS) :]:
        if not isinstance(pattern, str) or ".." in Path(pattern).parts:
            raise ManualBatchError("progress overlay path is unsafe")
        matches = sorted(repo_root.glob(pattern))
        if len(matches) != 1:
            raise ManualBatchError(f"progress path must resolve exactly once: {pattern}")
        overlay = read_json(matches[0])
        current = _validate_overlay_entries(overlay, pc_sc, pattern)
        if pattern == SELF_LOGICAL_PATH:
            if matches[0].read_bytes() != self_blob or current != {
                (entry["block_id"], entry["slot_id"]): entry["ko"]
                for entry in self_overlay["entries"]
            }:
                raise ManualBatchError("self registration is not the exact deterministic overlay")
            self_count += 1
            continue
        coordinates = set(current)
        if not coordinates.issubset(target_coordinates):
            raise ManualBatchError(f"successor escaped target catalog: {pattern}")
        if coordinates & predecessor_coordinates or coordinates & self_coordinates:
            raise ManualBatchError(f"successor overlaps predecessor or self: {pattern}")
        if coordinates & successor_coordinates:
            raise ManualBatchError(f"successors overlap each other: {pattern}")
        text = matches[0].read_text(encoding="utf-8")
        if HAN_OR_KANA_RE.search(text):
            raise ManualBatchError(f"successor is not source-free: {pattern}")
        successor_coordinates.update(coordinates)
        successor_paths.append(pattern)
    if self_count > 1:
        raise ManualBatchError("self overlay is registered more than once")
    return {
        "predecessor_registration_count": len(PREDECESSORS),
        "self_registration_count": self_count,
        "self_registration_states_supported": [0, 1],
        "self_excluded_from_predecessor_selection": True,
        "successor_registration_tolerant": True,
        "successor_overlay_count": len(successor_paths),
        "successor_coordinate_count": len(successor_coordinates),
        "successor_paths": successor_paths,
        "successors_excluded_from_predecessor_selection": True,
    }


def build_candidate(
    inputs: dict[str, Any], integrated_values: dict[tuple[int, int], str]
) -> tuple[bytes, dict[str, Any]]:
    archive = inputs["pc_sc_archive"]
    replacements: dict[int, list[str]] = {
        block.block_id: list(block.texts) for block in archive.blocks
    }
    for (block_id, slot_id), replacement in integrated_values.items():
        source = archive.blocks[block_id].texts[slot_id]
        if common.invariant_mismatches(source, replacement):
            raise ManualBatchError(f"candidate invariant mismatch at {(block_id, slot_id)}")
        replacements[block_id][slot_id] = replacement
    target_raw = rebuild_strdata(archive, replacements)
    target_packed = recompress_wrapper(target_raw, inputs["pc_sc_wrapper"])
    _check_wrapper, check_raw = decompress_wrapper(target_packed)
    if check_raw != target_raw:
        raise ManualBatchError("candidate wrapper round-trip changed")
    check = parse_strdata(check_raw)
    before = coordinate_texts(archive)
    after = coordinate_texts(check)
    changed = sorted(coordinate for coordinate in before if before[coordinate] != after[coordinate])
    if changed != sorted(integrated_values):
        raise ManualBatchError("candidate changed an unexpected coordinate")
    if any(after[coordinate] != value for coordinate, value in integrated_values.items()):
        raise ManualBatchError("candidate replacement did not survive reparse")
    return target_packed, {
        "target_packed_size": len(target_packed),
        "target_packed_sha256": sha256(target_packed),
        "target_raw_size": len(target_raw),
        "target_raw_sha256": sha256(target_raw),
        "changed_coordinate_count": len(changed),
        "changed_coordinates_sha256": canonical_hash([list(value) for value in changed]),
        "unchanged_coordinate_count": EXPECTED["total_slots"] - len(changed),
        "block_slot_counts_preserved": [block.slot_count for block in check.blocks]
        == direct.BLOCK_SLOT_COUNTS,
        "target_outside_preserved": True,
        "offline_reparse_verified": True,
    }


def build(
    game_root: Path,
    switch_zip: Path,
    repo_root: Path,
    out_root: Path,
    candidate_out: Path,
    progress_path: Path,
) -> dict[str, Any]:
    inputs = direct.load_inputs(game_root, switch_zip)
    classified = direct.classify_direct(inputs)
    models = make_models(inputs, classified, repo_root)
    targets, _target_snapshot = load_target_catalog(
        repo_root / TARGET_CATALOG.relative_to(REPO_ROOT)
    )
    progress_audit = audit_progress_registration(
        progress_path,
        repo_root,
        classified["pc_sc"],
        targets,
        set(models["predecessor_values"]),
        models["overlay"],
    )
    integrated = {**models["predecessor_values"], **models["values"]}
    first, first_stats = build_candidate(inputs, integrated)
    second, second_stats = build_candidate(inputs, integrated)
    if first != second or first_stats != second_stats:
        raise ManualBatchError("candidate A/B builds differ")

    overlay_info = write_json(out_root / "public" / OVERLAY_NAME, models["overlay"])
    evidence_info = write_json(out_root / "evidence" / EVIDENCE_NAME, models["evidence"])
    review_info = write_json(out_root / "review" / REVIEW_NAME, models["review"])
    for path in (
        out_root / "public" / OVERLAY_NAME,
        out_root / "evidence" / EVIDENCE_NAME,
        out_root / "review" / REVIEW_NAME,
    ):
        if HAN_OR_KANA_RE.search(path.read_text(encoding="utf-8")):
            raise ManualBatchError(f"public artifact contains Han or Kana: {path}")

    candidate_out.parent.mkdir(parents=True, exist_ok=True)
    candidate_out.write_bytes(first)
    validation = {
        "schema": "nobu16.kr.strdata-pk-shared-manual-validation.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "passed": True,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "input_pins": {
            "pc_sc": direct.PC_SC_PIN,
            "pc_jp": direct.PC_JP_PIN,
            "switch_v13": direct.SWITCH_PIN,
            "switch_zip": direct.ZIP_PIN,
            "target_catalog": models["target_snapshot"],
        },
        "predecessors": {
            "entry_count": len(models["predecessor_values"]),
            "overlays": list(PREDECESSORS),
            "disjoint": True,
        },
        "selection": models["selection"],
        "category_counts": models["category_counts"],
        "translation_method_counts": models["translation_method_counts"],
        "coverage": {
            "target_count": EXPECTED["target_count"],
            "before": EXPECTED["published_predecessor_coverage"],
            "added": EXPECTED["selected_count"],
            "after": EXPECTED["coverage_after"],
            "remaining": EXPECTED["remaining_after"],
        },
        "format_contract": {
            "all_selected_invariants_equal": True,
            "han_or_kana_in_public_artifacts": 0,
            "block_slot_counts_preserved": True,
            "all_nonselected_coordinates_preserved": True,
        },
        "progress_registration_audit": progress_audit,
        "candidate": first_stats,
        "reproducibility": {
            "in_memory_candidate_a_b_equal": True,
            "artifact_json_canonical": True,
        },
        "artifacts": {
            "overlay": overlay_info,
            "evidence": evidence_info,
            "review": review_info,
        },
        "safety": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "user_untracked_strdata_workstream_read": False,
            "user_untracked_strdata_workstream_modified": False,
            "progress_modified": False,
            "root_readme_modified": False,
            "font_modified": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "commit_or_push_performed": False,
        },
    }
    write_json(out_root / VALIDATION_NAME, validation)
    return validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    parser.add_argument("--progress", type=Path, default=PROGRESS)
    parser.add_argument(
        "--candidate-out",
        type=Path,
        default=(
            REPO_ROOT
            / "tmp"
            / "strdata_pk_shared_manual_b01"
            / "candidate"
            / RESOURCE
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validation = build(
        args.game_root.resolve(),
        args.switch_zip.resolve(),
        args.repo_root.resolve(),
        args.out_root.resolve(),
        args.candidate_out.resolve(),
        args.progress.resolve(),
    )
    print(f"overlay_entries={validation['selection']['selected_count']}")
    print(f"coverage_after={validation['coverage']['after']}")
    print(f"remaining={validation['coverage']['remaining']}")
    print(f"target_sha256={validation['candidate']['target_packed_sha256']}")
    print(f"candidate={args.candidate_out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
