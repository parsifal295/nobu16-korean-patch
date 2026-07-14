#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 5."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
WORKSPACE_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_translation_batch1 as previous  # noqa: E402


BATCH_ID = "msggame_pk_system_messages_b02r0666_b04r0075.v0.5"
OVERLAY_NAME = "msggame_ko_system_messages_b02r0666_b04r0075.v0.5.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.5.json"
REVIEW_NAME = "translation_review_index.v0.5.json"
VALIDATION_NAME = "translation_validation.v0.5.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (4, 76, 0)


# A tuple covers every SC literal slot in the record. None retains a stock
# literal without publishing it. Visible non-linguistic fragments additionally
# have a pinned public skip reason below; invisible whitespace is simply kept.
TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (2, 666): ("조정과의 친선은\n약", "개월 후 완료될 예정입니다."),
    (2, 667): ("담당 구획을 변경할 무장을 선택하십시오.",),
    (2, 668): ("군대는 설비를 건설할 수 없습니다",),
    (2, 669): ("“군사제”에 따라 군대가 건설합니다",),
    (2, 670): ("여러 영지를 보유한 성주가 건설합니다",),
    (2, 671): ("성주는 변경할 수 없습니다",),
    (2, 672): ("달성",),
    (2, 673): ("세력 목표 “", "”을 달성했습니다.\n본가도 더욱 발전하겠군요."),
    (2, 674): ("특별 보상 획득",),
    (2, 676): ("획득", None, None),
    (2, 677): ("양도", None),
    (3, 3): ("이 저장 데이터를 덮어쓰시겠습니까?",),
    (3, 4): ("저장에 실패했습니다.",),
    (3, 5): ("저장을 완료했습니다.",),
    (3, 6): (
        "이 저장 데이터를 불러올 수 없습니다.\n"
        "데이터와 게임의 버전이 일치하지 않습니다.\n"
        "게임을 최신 버전으로 업데이트하십시오.",
    ),
    (3, 7): ("플레이 중인 시나리오를 중단하고\n불러오시겠습니까?",),
    (3, 8): ("이 저장 데이터를 불러오시겠습니까?",),
    (3, 9): ("데이터 불러오기에 실패했습니다(", ")입니다."),
    (3, 10): ("새 저장 파일 생성에 실패했습니다.",),
    (3, 11): ("보유하지 않은 DLC가 포함되어 있습니다.",),
    (3, 12): ("게임을 최신 버전으로 업데이트하십시오.",),
    (3, 13): ("변경 사항을 버리고 돌아가시겠습니까?",),
    (3, 14): ("데이터가 손상되었습니다.",),
    (3, 15): ("등록 무장", "명을 불러왔습니다."),
    (3, 16): (
        "등록 무장이 생부나 혈연으로 설정되어 있으면,\n"
        "해당 생부·혈연 설정을 삭제했습니다.",
    ),
    (3, 17): ("생년을 변경하면 생부 설정이 무효가 됩니다.\n계속하시겠습니까?",),
    (3, 18): ("수명 변경으로", "의\n생부 설정이 무효가 됩니다.\n계속하시겠습니까?"),
    (3, 19): ("수명 변경으로", "등의\n생부 설정이 무효가 됩니다.\n계속하시겠습니까?"),
    (3, 20): ("성별을 변경하면 생부 설정이 무효가 됩니다.\n계속하시겠습니까?",),
    (3, 21): ("시나리오 「군웅쟁패」가 개방되었습니다.",),
    (3, 22): (
        "추가 콘텐츠 데이터를 찾을 수 없어,\n"
        "일부 무장이 등장하지 않습니다.\n"
        "※다시 다운로드한 후\n"
        "　게임을 시작하면 등장합니다.",
    ),
    (3, 23): ("세력 배치 편집",),
    (3, 24): ("신규 세력 생성",),
    (3, 25): ("다이묘 변경",),
    (3, 26): ("편집 내용을 초기화",),
    (3, 27): ("이전 화면으로 돌아가기",),
    (3, 28): ("시나리오 편집",),
    (3, 29): (
        "다음 조건을 충족하여\n"
        "신규 세력의 다이묘가 될 등록 무장이 없습니다.\n"
        "신규 세력을 생성할 수 없습니다.\n"
        "●등록 무장 편집 화면에서 “등장”으로 설정\n"
        "●시나리오 시작 시 16세 이상이며 생존",
    ),
    (3, 31): ("편집한 시나리오를 초기화합니다.\n계속하시겠습니까?",),
    (3, 32): ("시나리오를 초기화했습니다",),
    (3, 33): ("편집할 신규 세력을 선택하십시오",),
    (3, 34): ("편집할 항목을 선택하십시오",),
    (3, 35): ("설정 내용을 폐기합니다.\n계속하시겠습니까?",),
    (3, 36): ("본거지로 삼을 성 1개를 선택하십시오",),
    (3, 37): ("신규 세력의 성을 선택하십시오（최대 2개）",),
    (3, 38): ("본거지로 선택할 수 없습니다",),
    (3, 39): ("성은 최대 2개까지 선택할 수 있습니다",),
    (3, 40): ("설정 내용을 폐기하고 본거지 선택으로 돌아갑니다.\n계속하시겠습니까?",),
    (3, 41): ("다이묘가 될 수 있는 무장이 없습니다",),
    (3, 42): ("다이묘를 선택하십시오",),
    (3, 43): ("본거지로 변경할 수 있는 성이 없습니다",),
    (3, 44): ("세력에 소속시킬 수 있는 무장이 없습니다",),
    (3, 45): ("현재 다이묘입니다",),
    (3, 46): ("신규 세력의 다이묘입니다",),
    (3, 47): ("생성됨",),
    (3, 48): ("삭제됨",),
    (3, 49): ("편집됨",),
    (3, 50): ("다른 세력의 성은 선택할 수 없습니다",),
    (3, 51): ("다이묘가 변경되지 않았습니다",),
    (3, 54): ("다이묘를 변경할 세력을 선택하십시오",),
    (3, 55): ("세력 배치를 편집하십시오",),
    (3, 56): ("세력이 지배하는 성을 무작위로 교체",),
    (3, 57): ("국가 변경 대상이 될 세력이 없습니다",),
    (3, 58): ("모든 세력을 국가 변경 대상에서 제외",),
    (3, 59): ("모든 세력을 국가 변경 대상으로 선택",),
    (3, 60): ("이 세력을 국가 변경 대상에서 제외",),
    (3, 61): ("이 세력을 국가 변경 대상으로 선택",),
    (4, 3): ("α 버전의 튜토리얼을 표시하시겠습니까?",),
    (4, 4): ("게임을 종료하시겠습니까?",),
    (4, 5): ("데이터", "을 불러오시겠습니까?"),
    (4, 6): ("오카자키성이 함락되었습니다.\n축하합니다!\nα 버전은 여기까지입니다.",),
    (4, 7): ("이나바야마성이 함락되었지만,\nα 버전의 목표는 오카자키성 공략입니다.",),
    (4, 8): ("다음에는 오카자키성을 목표로 하십시오.\nα 버전은 여기까지입니다.",),
    (4, 9): ("기요스성이 함락되었습니다.\nα 버전은 여기까지입니다.",),
    (4, 10): ("마우스 오른쪽 버튼을 클릭하면 세력 메뉴가 열립니다.",),
    (4, 11): (
        "【표시 모드】\n"
        "게임 화면의 표시 모드를 설정합니다.\n\n"
        "[창 모드]\n창으로 표시\n\n"
        "[전체 화면 모드]\n전체 화면으로 표시\n\n"
        "[테두리 없음]\n테두리 없는 창으로 표시",
    ),
    (4, 12): (
        "【화면 크기(해상도)】\n"
        "화면 해상도를 변경합니다.\n\n"
        "[권장 해상도]\n"
        "1920×1080 픽셀\n"
        "1600×900 픽셀\n",
    ),
    (4, 13): (
        "【CG 품질】\nCG 품질을 설정합니다.\n※전투 중에는 변경할 수 없습니다.\n\n"
        "[속도 우선]\n속도를 우선하여 CG를 간략히 표시\n\n"
        "[표준]\n표준 품질로 CG 표시\n\n"
        "[품질 우선]\n품질을 우선하여 CG를 자세히 표시",
    ),
    (4, 14): (
        "【음향 설정】\n게임 내 음량을 조절합니다.\n\n"
        "[전체 음량]\n게임의 전체 음량 설정\n\n"
        "[BGM 음량] / [효과음 음량] /\n"
        "[음성·동영상 음량]\n각 항목의 음량 설정",
    ),
    (4, 15): ("【음향 출력】\n음향 방식을 설정합니다.\n\n[스테레오] / [서라운드]",),
    (4, 17): (
        "【자동 저장】\n자동 저장 간격을 설정합니다.\n\n"
        "[매월]\n달이 바뀔 때\n\n"
        "[분기마다]\n1월, 4월, 7월, 10월\n\n"
        "[매년]\n매년 1월\n\n"
        "[사용 안 함]\n자동 저장하지 않음",
    ),
    (4, 18): (
        "【시나리오 자동 재생】\n시나리오 자동 재생을 설정합니다.\n\n"
        "[저속] / [중속] / [고속] / [최고속]\n자동 재생 속도 설정\n\n"
        "[사용 안 함]\n조작하지 않으면 진행하지 않음",
    ),
    (4, 19): (
        "【개요 표시 속도】\n성이나 부대에 마우스를 올렸을 때,\n"
        "정보가 표시되기까지의 시간을 설정합니다.\n\n"
        "[저속] / [중속]\n일정 시간이 지난 뒤 표시\n\n"
        "[고속]\n즉시 표시",
    ),
    (4, 20): (
        "【자동 스크롤】\n마우스를 화면 가장자리로 옮겼을 때,\n"
        "지도를 스크롤할지 설정합니다.\n\n"
        "[저속] / [중속] / [고속]\n스크롤 속도 설정\n\n"
        "[사용 안 함]\n자동 스크롤하지 않음",
    ),
    (4, 21): (
        "【명령 시 카메라 이동】\n성·부대 메뉴를 선택하거나 명령을 실행할\n"
        "때 카메라가 이동할지 설정합니다.\n\n[사용] / [사용 안 함]",
    ),
    (4, 22): (
        "【이벤트 시 카메라 이동】\n지도에서 발생한 이벤트를 따라 카메라가\n"
        "이동할지 설정합니다.\n\n"
        "[사용]\n이벤트 보고 시 카메라 이동\n\n"
        "[사용 안 함]\n일부 예외를 제외하고 이벤트 보고 시\n카메라를 이동하지 않음",
    ),
    (4, 23): (
        "【난이도】\n게임 난이도를 설정합니다.\n\n"
        "[입문]\n느긋하게 즐기려는 플레이어에게 권장\n\n"
        "[초급]\n적당한 난이도를 즐기려는 플레이어에게 권장\n\n"
        "[중급]\n게임에 익숙한 플레이어에게 권장\n\n"
        "[상급]\n도전을 원하는 플레이어에게 권장",
    ),
    (4, 24): (
        "【군량 수입(자세력)】\n자세력의 군량 수입량을 설정합니다.\n"
        "수치를 높일수록 성의 군량 수입이 늘어납니다.",
    ),
    (4, 25): (
        "【군량 수입(타세력)】\n타세력의 군량 수입량을 설정합니다.\n"
        "수치를 높일수록 성의 군량 수입이 늘어납니다.",
    ),
    (4, 26): (
        "【금전 수입(자세력)】\n자세력의 금전 수입량을 설정합니다.\n"
        "수치를 높일수록 성의 금전 수입이 늘어납니다.",
    ),
    (4, 27): (
        "【금전 수입(타세력)】\n타세력의 금전 수입량을 설정합니다.\n"
        "수치를 높일수록 성의 금전 수입이 늘어납니다.",
    ),
    (4, 28): (
        "【AI 레벨】\n타세력의 사고 능력을 설정합니다.\n"
        "레벨이 높을수록 여러 전략을 효율적으로 실행합니다.",
    ),
    (4, 29): (
        "【AI 호전도】\n타세력의 호전성을 설정합니다.\n"
        "레벨이 높을수록 적국을 침략하기 쉬워집니다.",
    ),
    (4, 30): (
        "【전투/공성전 AI 레벨】\n전투/공성전에서 타세력의 사고 능력을\n"
        "설정합니다. 높을수록 어려워집니다.",
    ),
    (4, 31): (
        "【재해】\n재해 발생 빈도를 설정합니다.\n"
        "높을수록 태풍이나 흉작 같은 재해가 자주 발생합니다.",
    ),
    (4, 32): (
        "【병력 회복 속도(자세력)】\n자세력의 병력 회복 속도를 설정합니다.\n"
        "성의 병력이 최대치까지 회복되는 데\n걸리는 속도에 영향을 줍니다.",
    ),
    (4, 33): (
        "【병력 회복 속도(타세력)】\n타세력의 병력 회복 속도를 설정합니다.\n"
        "성의 병력이 최대치까지 회복되는 데\n걸리는 속도에 영향을 줍니다.",
    ),
    (4, 34): (
        "【건의·내정 속도(자세력)】\n자세력의 건의 및 내정 속도를 설정합니다.\n"
        "빠르게 설정할수록 건의와 내정의 실행\n기간이 짧아집니다.",
    ),
    (4, 35): (
        "【건의·내정 속도(타세력)】\n타세력의 건의 및 내정 속도를 설정합니다.\n"
        "빠르게 설정할수록 건의와 내정의 실행\n기간이 짧아집니다.",
    ),
    (4, 36): (
        "【노동력(자세력)】\n자세력의 최대 노동력을 설정합니다.\n"
        "수치를 높일수록 석고로 얻는 노동력이\n늘어납니다.",
    ),
    (4, 37): (
        "【노동력(타세력)】\n타세력의 최대 노동력을 설정합니다.\n"
        "수치를 높일수록 석고로 얻는 노동력이\n늘어납니다.",
    ),
    (4, 38): (
        "【수명】\n무장의 수명을 설정합니다.\n",
        "※시나리오 시작 후에는 변경할 수 없습니다",
        "\n\n[사실]\n사실에 따른 수명\n\n"
        "[장수]\n사실보다 긴 수명\n\n"
        "[없음]\n수명이 다하지 않으며 이벤트나 전사로만 사망",
    ),
    (4, 39): ("【전사】\n무장이 전투에서 사망하는 빈도를 설정합니다.\n\n[적음] / [보통] / [많음] / [없음]",),
    (4, 40): (
        "【무장명】\n무장명 표시 방식을 전환합니다.\n\n"
        "[통칭]\n통상적으로 쓰인 이름을 우선 표시\n\n"
        "[사실]\n역사상의 이름을 우선 표시\n\n"
        "예: (통칭) 사나다 유키무라\n　　(사실) 사나다 노부시게",
    ),
    (4, 41): (
        "【역사 이벤트】\n무장 대화 등으로 발생하는 역사\n이벤트를 설정합니다.\n\n"
        "[있음] / [없음]\n\n"
        "※이벤트는 사실에 기반한 이벤트와\n"
        "　《노부나가의 야망·신생》 오리지널 이벤트로 나뉩니다.\n"
        "※게임 내 이벤트 목록에서도\n　개별 설정할 수 있습니다",
    ),
    (4, 42): (
        "【공주 무장】\n공주를 무장으로 등장시킬지 설정합니다.\n"
        "　공주　　…혼인·화친 혼인이 가능\n"
        "　공주 무장…공주와 무장 신분을 함께 보유\n",
        "※시나리오 선택 전까지만 변경할 수 있습니다",
        "\n\n[있음]\n모든 공주가 공주 무장으로 등장\n\n"
        "[없음]\n모든 공주가 공주로 등장",
    ),
    (4, 43): (
        "【가상 공주 출생】\n가상 공주의 출생 여부를 설정합니다.\n"
        "※공주가 있어야 혼인이나 혼인 동맹을 맺을 수 있습니다\n\n"
        "[있음] / [없음]",
    ),
    (4, 44): (
        "【진언】\n가신이 건의로 현재 취해야 할 행동을\n"
        "안내할지 설정합니다\n"
        "※처음 플레이하는 분에게 권장\n\n[있음] / [없음]",
    ),
    (4, 45): (
        "【자율 행동】\n부대 출진 시 모든 자율 행동을 허용할지\n설정합니다.\n"
        "※부대별로 따로 설정할 수 있습니다\n\n"
        "[허가]\n다음 행동은 무장에게 확인\n"
        "·목표 달성 후 가까운 성으로 귀환\n"
        "·적이 양쪽으로 나뉘면 한쪽을 공격\n"
        "·승산 없는 상대에게서 도주\n\n"
        "[금지]\n내린 명령만 실행",
    ),
    (4, 46): ("【버튼 안내】\n버튼 안내 표시 여부를 설정합니다\n\n[표시] / [표시 안 함]",),
    (4, 47): ("【카메라 조작】\n카메라 조작 방식을 설정합니다\n\n[정방향] / [역방향]",),
    (4, 48): (
        "【초기 외교 상태】\n동맹·종속 등 사실에 따른 외교 관계를\n"
        "맺은 상태로 시작할지 선택합니다.\n",
        "※시나리오 시작 후에는 변경할 수 없습니다.",
        "\n\n[사실]\n사실에 따른 외교 관계가 있음\n\n"
        "[없음]\n모든 세력이 외교 관계를 맺지 않은\n상태로 설정",
    ),
    (4, 49): (
        "【튜토리얼 표시】\n게임 진행 중 튜토리얼 표시를 설정합니다.\n",
        "※시나리오 시작 후에는 [있음]으로 변경할 수 없습니다.",
        "\n\n[있음] / [없음]",
    ),
    (4, 50): (
        "【실시간 로그 표시】\n화면 중앙에 실시간으로 표시할 로그를 설정합니다.\n\n"
        "[모두 표시]\n모든 종류의 로그 표시\n\n"
        "[모두 표시 안 함]\n모든 종류의 로그를 표시하지 않음\n\n"
        "[사용자 설정]\n지정한 종류만 표시",
    ),
    (4, 51): (
        "[내정]\n정무와 건설 관련 로그\n\n"
        "[군사]\n행군 관련 로그\n\n"
        "[외교]\n다른 세력과의 신용 관련 로그\n\n"
        "[모략]\n다른 세력에 대한 공작 관련 로그\n\n"
        "[무장]\n무장의 상태와 지위 관련 로그",
    ),
    (4, 52): (
        "【3D 커서 이동 속도】\n지도 위 3D 커서의 이동 속도를 조절합니다.\n\n"
        "[저속] / [중속] / [고속]\n3D 커서 이동 속도 설정",
    ),
    (4, 53): (
        "【세력 목표】\n게임 중 가신이 목표를 건의할지 설정합니다.\n\n"
        "[있음]\n상황에 따라 목표를 건의\n달성하면 공훈 획득\n\n"
        "[없음]\n세력 목표를 건의하지 않음",
    ),
    (4, 54): (
        "【소목표 건의】\n게임 중 가신이 목표를 건의할지 설정합니다.\n\n"
        "[있음]\n상황에 따라 목표를 건의합니다.\n달성하면 공훈을 획득합니다.\n\n"
        "[없음]\n소목표를 건의하지 않습니다.",
    ),
    (4, 55): (
        "【회전 연출 표시】\n회전 연출을 표시할지 설정합니다.\n\n"
        "[모두 표시]\n모든 연출 표시\n\n"
        "[일부 표시]\n퇴각이나 궤주 등 일부 연출만 표시",
    ),
    (4, 56): ("【군단 상황 표시】\n행동 목록에 군단 상황 보고를 표시할지\n설정합니다.\n\n[표시] / [표시 안 함]",),
    (4, 57): ("다음 가보가 입고되었습니다:\n·", None, None),
    (4, 58): ("정책으로 인해 금전 수지가 적자입니다.",),
    (4, 59): ("정책「", "」을 실행할 수 있게 되었습니다."),
    (4, 60): ("영주를 교체할 수 있게 되었습니다.",),
    (4, 61): ("성주를 교체할 수 있게 되었습니다.",),
    (4, 62): ("의 시설 건설 슬롯이 확장되었습니다.",),
    (4, 68): ("편집할 세력을 선택하십시오",),
    (4, 69): ("다이묘의 관직 설정",),
    (4, 70): ("직위 설정",),
    (4, 71): ("다이묘의 가보 설정",),
    (4, 72): ("금전 설정",),
    (4, 73): ("재임 중인 무장이 있어 선택할 수 없습니다",),
    (4, 74): ("재임 중인 세력이 있어 선택할 수 없습니다",),
    (4, 75): ("소유한 무장이 있어 선택할 수 없습니다",),
}


SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {
    (2, 676, 2): "nonlinguistic_numeric_bonus_prefix",
    (4, 57, 1): "nonlinguistic_repeated_bullet_separator",
    (4, 57, 2): "nonlinguistic_repeated_bullet_separator",
}
EXPECTED_RECORD_KEYS = (
    tuple((2, item) for item in (666, 667, 668, 669, 670, 671, 672, 673, 674, 676, 677))
    + tuple((3, item) for item in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 54, 55, 56, 57, 58, 59, 60, 61))
    + tuple((4, item) for item in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 68, 69, 70, 71, 72, 73, 74, 75))
)


def selected_record_keys() -> list[tuple[int, int]]:
    return sorted(TRANSLATIONS)


def selected_coordinates() -> list[tuple[int, int, int]]:
    return [
        (block_id, record_id, literal_id)
        for (block_id, record_id), replacements in sorted(TRANSLATIONS.items())
        for literal_id, replacement in enumerate(replacements)
        if replacement is not None
    ]


def validate_static_scope() -> None:
    keys = selected_record_keys()
    selected = selected_coordinates()
    if keys != list(EXPECTED_RECORD_KEYS):
        raise ValueError("translation scan record set changed")
    if selected[0] != (2, 666, 0) or selected[-1] != (4, 75, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 134:
        raise ValueError("translation batch scope changed")
    if set(SKIPPED_CANDIDATES) != {
        (2, 676, 2),
        (4, 57, 1),
        (4, 57, 2),
    }:
        raise ValueError("translation batch skip set changed")
    if set(selected) & set(SKIPPED_CANDIDATES):
        raise ValueError("a skipped coordinate is also selected")


def _uncertainty_flags(
    coordinate: tuple[int, int, int],
    record_counts: dict[str, int],
    sc_literal_count: int,
) -> list[str]:
    flags = ["runtime_line_wrap_review"]
    if len(set(record_counts.values())) != 1:
        flags.append("cross_language_literal_shape_diff")
    if sc_literal_count > 1:
        flags.append("runtime_dynamic_join_review")
    if coordinate[1] in {38, 42, 48, 49, 57, 59}:
        flags.append("runtime_fragment_join_review")
    return flags


def _assert_public_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    scans: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = previous.script_counts(path.read_text(encoding="utf-8"))
        scans[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise ValueError(f"source-script text leaked into {path}")
    return scans


def build(args: argparse.Namespace) -> dict[str, Any]:
    validate_static_scope()
    paths = {
        language: Path(getattr(args, f"stock_{language.lower()}")).resolve()
        for language in LANGUAGES
    }
    installed_before = {
        language: previous.sha256(path.read_bytes()) for language, path in paths.items()
    }
    loaded = previous.load_sources(paths)
    archives = {
        language: loaded[language]["parsed"].archive for language in LANGUAGES
    }
    records = {
        language: previous._record_map(archive)
        for language, archive in archives.items()
    }
    sc_literals = previous._literal_map(archives["SC"])

    overlay_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    invariant_failures: list[dict[str, Any]] = []
    record_evidence: list[dict[str, Any]] = []
    replacement_map: dict[tuple[int, int, int], str] = {}
    observed_skips: set[tuple[int, int, int]] = set()

    for block_id, record_id in selected_record_keys():
        key = (block_id, record_id)
        source_record_literals = previous.parse_record_literals(records["SC"][key])
        replacements = TRANSLATIONS[key]
        if len(source_record_literals) != len(replacements):
            raise ValueError(
                f"translation literal count mismatch at {key}: "
                f"source={len(source_record_literals)}, ko={len(replacements)}"
            )
        candidate_ids = {
            literal.literal_id
            for literal in source_record_literals
            if previous.is_visible_translation_candidate(literal.text)
        }
        language_references = {
            language: previous.record_reference(records[language][key])
            for language in LANGUAGES
        }
        literal_counts = {
            language: language_references[language]["literal_count"]
            for language in LANGUAGES
        }
        selected_ids = [
            literal_id
            for literal_id, replacement in enumerate(replacements)
            if replacement is not None
        ]
        skipped_ids = [
            literal_id
            for literal_id, replacement in enumerate(replacements)
            if replacement is None and literal_id in candidate_ids
        ]
        retained_nonvisible_ids = [
            literal_id
            for literal_id, replacement in enumerate(replacements)
            if replacement is None and literal_id not in candidate_ids
        ]
        if not set(selected_ids).issubset(candidate_ids):
            raise ValueError(f"non-visible literal selected at {key}")
        record_evidence.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "selected_sc_literal_ids": selected_ids,
                "skipped_sc_literal_ids": skipped_ids,
                "retained_nonvisible_sc_literal_ids": retained_nonvisible_ids,
                "references": language_references,
                "literal_shape_aligned_across_languages": len(set(literal_counts.values()))
                == 1,
                "cross_language_literal_id_alignment_used": False,
                "manual_same_record_semantic_crosscheck": True,
            }
        )

        for literal, replacement in zip(
            source_record_literals, replacements, strict=True
        ):
            coordinate = (block_id, record_id, literal.literal_id)
            if replacement is None:
                if literal.literal_id in candidate_ids:
                    if coordinate not in SKIPPED_CANDIDATES:
                        raise ValueError(f"unexplained visible skip: {coordinate}")
                    observed_skips.add(coordinate)
                elif coordinate in SKIPPED_CANDIDATES:
                    raise ValueError(f"declared skip is not visible: {coordinate}")
                continue
            problems = previous.common.invariant_mismatches(literal.text, replacement)
            if previous.bracket_sequence(literal.text) != previous.bracket_sequence(
                replacement
            ):
                problems.append(
                    "bracket_sequence: "
                    f"source={previous.bracket_sequence(literal.text)!r}, "
                    f"ko={previous.bracket_sequence(replacement)!r}"
                )
            if problems:
                invariant_failures.append(
                    {"coordinate": list(coordinate), "problems": problems}
                )
            replacement_map[coordinate] = replacement
            overlay_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "source_sc_utf16le_sha256": previous.text_hash(literal.text),
                    "ko": replacement,
                }
            )
            review_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "status": "translated",
                    "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en_tc_record_context",
                    "automated_draft": True,
                    "human_review_required": True,
                    "runtime_reviewed": False,
                    "uncertainty_flags": _uncertainty_flags(
                        coordinate, literal_counts, len(source_record_literals)
                    ),
                }
            )
    if observed_skips != set(SKIPPED_CANDIDATES):
        raise ValueError("declared skipped coordinates were not observed")
    if invariant_failures:
        raise ValueError(f"replacement invariants failed: {invariant_failures}")

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": previous.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "packed_size": len(sc_packed),
            "packed_sha256": previous.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": previous.sha256(sc_raw),
            "record_count": archives["SC"].record_count,
            "literal_slot_count": len(sc_literals),
        },
        "entries": overlay_entries,
    }

    rebuilt, binary_manifest = previous.apply_overlay_blob(sc_packed, overlay)
    _target_header, target_raw = previous.decompress_wrapper(rebuilt)
    target = previous.parse_packed_msggame(rebuilt)
    target_literals = previous._literal_map(target.archive)
    target_records = previous._record_map(target.archive)
    if set(target_literals) != set(sc_literals):
        raise ValueError("literal coordinates changed after rebuild")
    for coordinate, source_literal in sc_literals.items():
        expected = replacement_map.get(coordinate, source_literal.text)
        if target_literals[coordinate].text != expected:
            raise ValueError(f"rebuilt literal mismatch at {coordinate}")
    if set(target_records) != set(records["SC"]):
        raise ValueError("record coordinates changed after rebuild")
    if any(
        previous.record_skeleton(records["SC"][key])
        != previous.record_skeleton(target_records[key])
        for key in target_records
    ):
        raise ValueError("opaque record bytecode changed outside literal text")
    if previous.rebuild_raw_msggame(target.archive) != target_raw:
        raise ValueError("rebuilt target raw parse/rebuild is not byte-identical")
    if [len(block.records) for block in archives["SC"].blocks] != [
        len(block.records) for block in target.archive.blocks
    ]:
        raise ValueError("top-level block record counts changed")
    if any(block.offset % 4 for block in target.archive.blocks):
        raise ValueError("rebuilt top-level block offset is not four-byte aligned")

    selected = selected_coordinates()
    actual_coordinates = [
        tuple(entry[key] for key in ("block_id", "record_id", "literal_id"))
        for entry in overlay_entries
    ]
    if actual_coordinates != selected:
        raise ValueError("overlay coordinate order is not deterministic")
    if selected[-1] != (4, 75, 0) or NEXT_COORDINATE not in sc_literals:
        raise ValueError("batch continuation boundary changed")

    record_keys = selected_record_keys()
    skipped = [
        {"coordinate": list(coordinate), "reason": reason}
        for coordinate, reason in sorted(SKIPPED_CANDIDATES.items())
    ]
    evidence = {
        "schema": "nobu16.kr.msggame-translation-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "scanned_visible_candidate_count": len(selected) + len(skipped),
            "skipped_candidates": skipped,
        },
        "alignment_basis": [
            "same_pk_resource_role",
            "same_18_block_shape",
            "same_block_and_record_coordinates",
            "manual_same_record_semantic_crosscheck",
            "language_literal_shapes_may_differ",
            "cross_language_literal_id_alignment_not_used",
        ],
        "source_files": {
            language: {
                "logical_path": SOURCE_PATHS[language],
                **previous.SOURCE_PINS[SOURCE_PATHS[language]],
            }
            for language in LANGUAGES
        },
        "record_count": len(record_evidence),
        "records": record_evidence,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msggame-translation-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(review_entries),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts["overlay"] = previous.write_json(overlay_path, overlay)
    artifacts["alignment_evidence"] = previous.write_json(evidence_path, evidence)
    artifacts["review_index"] = previous.write_json(review_path, review)
    source_free_scan = _assert_public_source_free(
        (overlay_path, evidence_path, review_path)
    )

    installed_after = {
        language: previous.sha256(path.read_bytes()) for language, path in paths.items()
    }
    if installed_before != installed_after:
        raise ValueError("installed game source changed during read-only batch build")

    validation = {
        "schema": "nobu16.kr.msggame-translation-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "selected_coordinates_sha256": previous.sha256(
                json.dumps(selected, separators=(",", ":")).encode("utf-8")
            ),
        },
        "selection": {
            "stable_sc_coordinate_order": True,
            "natural_scan_record_boundaries": True,
            "all_linguistic_literals_in_scanned_records_selected": True,
            "scanned_visible_candidate_count": len(selected) + len(skipped),
            "nonlinguistic_visible_candidate_skips": len(skipped),
            "skipped_candidates": skipped,
            "retained_nonvisible_literal_count": sum(
                replacement is None
                for replacements in TRANSLATIONS.values()
                for replacement in replacements
            )
            - len(skipped),
        },
        "source_alignment": {
            "languages": list(LANGUAGES),
            "record_coordinates_aligned": True,
            "literal_shapes_assumed_aligned": False,
            "manual_same_record_semantic_crosschecks": len(record_keys),
            "record_reference_count": len(record_keys) * len(LANGUAGES),
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "escape_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_sequence_in_order",
            ],
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": previous.sha256(rebuilt),
            "target_raw_size": len(target_raw),
            "target_raw_sha256": previous.sha256(target_raw),
            "literal_coordinates_preserved": True,
            "record_coordinates_preserved": True,
            "opaque_record_bytecode_preserved": True,
            "top_level_offsets_recomputed_and_aligned": True,
            "raw_parse_rebuild_byte_exact": True,
            "skipped_candidates_unchanged": all(
                target_literals[coordinate].text == sc_literals[coordinate].text
                for coordinate in SKIPPED_CANDIDATES
            ),
            "retained_nonvisible_literals_unchanged": all(
                target_literals[(block_id, record_id, literal_id)].text
                == sc_literals[(block_id, record_id, literal_id)].text
                for (block_id, record_id), replacements in TRANSLATIONS.items()
                for literal_id, replacement in enumerate(replacements)
                if replacement is None
                and (block_id, record_id, literal_id) not in SKIPPED_CANDIDATES
            ),
            "installed_game_file_written": False,
        },
        "translation_status": {
            "translated_draft": len(selected),
            "human_review_required": len(selected),
            "runtime_reviewed": 0,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": previous.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "byte_identical_offline_binary_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_modified": False,
            "progress_manifest_modified": False,
            "other_workstreams_modified": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    artifacts["generation_validation"] = previous.write_json(
        validation_path, validation
    )
    if previous.script_counts(validation_path.read_text(encoding="utf-8")) != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError("source-script text leaked into validation artifact")
    return {
        "out_root": out_root,
        "entry_count": len(selected),
        "record_count": len(record_keys),
        "skipped_count": len(skipped),
        "next_coordinate": NEXT_COORDINATE,
        "target_packed_sha256": previous.sha256(rebuilt),
        "artifacts": artifacts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for language in LANGUAGES:
        parser.add_argument(
            f"--stock-{language.lower()}",
            type=Path,
            default=WORKSPACE_ROOT / Path(SOURCE_PATHS[language]),
        )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"records={result['record_count']}")
    print(f"entries={result['entry_count']}")
    print(f"skipped={result['skipped_count']}")
    print("next_coordinate=" + ",".join(map(str, result["next_coordinate"])))
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
