#!/usr/bin/env python3
"""Prepare high-confidence PC ``msgui`` semantic corrections.

This generator only covers rows where the live Korean text is demonstrably
unrelated to the same-coordinate pristine PC Japanese text, or where a short
Japanese UI label has a single unambiguous Korean rendering.  It deliberately
excludes the 3625--3670 slice prepared separately, all IME component labels,
and every uncertain wording review.

Evidence is limited to the pristine PC Japanese ``msgui`` source and the live
PC EN/SC/TC context embedded in the private inventory.  It never reads Switch
Korean or historic Korean backups.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
INPUT = REPO / "tmp" / "translation_quality_audit_v1" / "semantic_inventory_v3" / "private_full_pairs.jsonl"
OUTPUT = REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "msgui_findings.v1.jsonl"

# The 3625--3670 interval belongs to its own independently reviewed file.
# Do not add IDs from that interval here.
FIXES = {
    # Short, directly translatable UI labels.
    2757: "명",
    2758: "전체",
    # Verified coordinate drift: 3527--3560.
    3527: "당가의 다이묘입니다",
    3528: "이미 다른 군단의 군단장이 되어 있습니다",
    3529: "군단장이 될 수 있는 신분이 아닙니다",
    3533: "스킵하시겠습니까?",
    3534: "병량이 부족합니다",
    3535: "출진 가능한 병력이 부족합니다",
    3537: "군단장의 소속 성이 교전 중입니다",
    3538: "군단장이 군단 본거지에 없습니다",
    3540: "군단장이 이동할 수 있는 성이 없습니다",
    3541: "군단장의 소속 성을 변경합니다",
    3542: "타 세력의 성입니다",
    3543: "교전 중인 성입니다",
    3544: "군단 본거지입니다",
    3546: "공물을 보낼 세력을 선택하십시오",
    3547: "다이묘가 직접 다스리고 있어 건설할 수 없습니다",
    3548: "성하 방침을 설정할 수 있는 성이 없습니다",
    3549: "성주가 없어 선택할 수 없습니다",
    3550: "성주가 개발할 수 있는 최대치에 도달했습니다",
    3551: "성하 방침을 설정할 수 없는 상황이라 선택할 수 없습니다",
    3552: "정책 “제도 개신” LV1을 발령하면 가능해집니다",
    3553: "발휘되지 않은 성향이라 선택할 수 없습니다",
    3554: "본거지는 선택할 수 없습니다",
    3555: "수여할 수 있는 군이 없습니다",
    3556: "실행할 수 있는 성이 없습니다",
    3557: "성주를 임명해야 합니다",
    3558: "자군단의 성에서만 실행할 수 있습니다",
    3559: "모든 농촌을 장악했습니다",
    3560: "모든 시장을 장악했습니다",
    # Verified coordinate drift: 3561--3624.
    3561: "타 세력 영내의 국인중입니다",
    3562: "이미 원군을 요청할 수 있는 상태입니다",
    3563: "더 이상 회유할 수 없습니다",
    3564: "편입에 응할 가망이 없습니다",
    3565: "적대 세력 이외는 선택할 수 없습니다",
    3566: "인접 세력 이외는 선택할 수 없습니다",
    3567: "표적이 될 무장이 없습니다",
    3568: "이미 봉기가 발생해 선동 효과를 기대할 수 없습니다",
    3569: "인접하지 않은 성은 선택할 수 없습니다",
    3570: "내구와 병력 모두 파괴 효과를 기대할 수 없습니다",
    3571: "병량과 병력 모두 방화 효과를 기대할 수 없습니다",
    3572: "단교 중인 세력에는 효과를 기대할 수 없습니다",
    3573: "이미 우호적인 관계입니다",
    3574: "회유할 국인중을 선택하십시오",
    3575: "편입할 국인중을 선택하십시오",
    3576: "충성심이 높은 무장에게는 효과를 기대할 수 없습니다",
    3577: "이미 충성심이 낮아 실행할 필요가 없습니다",
    3579: "당가를 혐오하는 무장입니다",
    3580: "당가와 인연이 있는 무장입니다",
    3581: "영지 수여",
    3582: "적 영지 탈취",
    3585: "지난번에 보낸 것보다 좋은 가보가 없습니다",
    3586: "이미 공물을 준비했습니다",
    3587: "보낼 수 있는 가보가 없습니다",
    3588: "교체할 수 있는 무장이 없습니다",
    3589: "현재 선택한 성입니다",
    3590: "다이묘에게는 실행할 수 없습니다",
    3591: "성주의 지행 군 수를 설정하십시오",
    3592: "지행하지 않음",
    3593: "이동 목적지를 선택하십시오",
    3594: "성주에게 임명할 수 있는 영지 수가 이미 최대입니다",
    3595: "성주에게 임명할 수 있는 영지 수가 이미 최소입니다",
    3596: "소집할 무장을 선택하십시오",
    3597: "이동할 군을 선택하십시오",
    3598: "선택 가능한 군을 선택하십시오",
    3599: "선택 중인 목록을 해제하십시오",
    3601: "공격에 도움이 되는 연병장 등을 우선 건설합니다",
    3602: "원정과 포위에 도움이 되는 보급소 등을 우선 건설합니다",
    3603: "금전 수입을 늘리는 상인 마을 등을 우선 건설합니다",
    3604: "타 군단 영내의 국인중입니다",
    3607: "성주가 될 수 있는 신분이 아닙니다",
    3608: "출진할 부대가 없습니다",
    3609: "이 안은 제안되지 않았습니다",
    3614: "군단 내 무장의 영지를 편성합니다",
    3615: "타 세력에 대한 조략을 명령합니다",
    3620: "무장을 파견하면 기간이 단축됩니다",
    3621: "무장을 파견하면 건설을 시작합니다",
    3622: "타 세력이 제압한 군은 선택할 수 없습니다",
    3623: "성하 방침 완료",
    3624: "모든 이벤트 발생이 활성화되어 있습니다",
    # Verified coordinate drift: 3671--3746 (3625--3670 excluded).
    3671: "병력 회복 중이라 회유할 수 없습니다",
    3672: "이 땅의 취락에 관한 명령을 내립니다",
    3673: "군단장이 소속된 성이 교전 중이라 해산할 수 없습니다",
    3674: "군단장이 소속된 성에서 부대가 출진 중이라 해산할 수 없습니다",
    3675: "군단장이 소속된 성이 교전 중이라 이동할 수 없습니다",
    3676: "군단장이 소속된 성에서 부대가 출진 중이라 이동할 수 없습니다",
    3677: "타 세력의 군단은 해산할 수 없습니다",
    3679: "다른 군단의 부대는 편성할 수 없습니다",
    3680: "무장을 파견하면 분쟁을 중재합니다",
    3681: "이미 포섭하려는 국인중입니다",
    3682: "이 항목에서는 선택할 수 없습니다",
    3686: "병량고 효과로 휴대 병량 소비량이 감소 중입니다",
    3687: "본거지 이외의 성에는 군 개발을 명령할 수 없습니다",
    3688: "카메라를 확대하면 이용할 수 있습니다",
    3692: "공성 중이므로 병력이 귀환할 수 없습니다",
    3693: "선택 중인 적 성을 향해 출진합니다",
    3694: "내구가 최대입니다",
    3695: "원군을 요청할 수 있도록 국인중을 회유합니다",
    3696: "국인중을 세력 산하로 편입합니다",
    3697: "선택 중인 부대를 출진 중인 부대의 목표로 삼습니다",
    3698: "교전 중인 성을 포위합니다",
    3699: "교전 중인 성을 강공합니다",
    3700: "대관이 장악 중입니다",
    3701: "대관이 건설 중입니다",
    3702: "먼 성은 출진 목표로 지정할 수 없습니다",
    3703: "명령 숨기기",
    3704: "막부 또는 인접 세력 이외는 선택할 수 없습니다",
    3705: "원군으로 출진 중인 부대에는 명령할 수 없습니다",
    3706: "이 부대는 독단으로 행동해 다이묘의 명령을 따르지 않습니다",
    3709: "『노부나가의 야망·대지 파워업키트』의 등록 무장 데이터를 이어받습니다",
    3726: "%s 등의 양도",
    3729: "%s 안도 %d년",
    3734: "%s의 해고",
    3736: "%s와의 동맹 파기",
    3738: "항복하고 성주 이외는 석방",
}

# Further findings from the same all-coordinate comparison.  These include
# two established-term corrections, format-critical fullwidth percentages,
# and the independently verified post-3750 misalignment clusters.
FIXES.update(
    {
        687: "겐푸쿠",
        1420: "겐푸쿠 전",
        2139: "석고 %d％ 상승",
        2140: "상업 %d％ 상승",
        2154: "완전 개발 완료\n석고 %d％ 상승",
        2155: "모든 군 완전 개발 완료\n상업 %d％ 상승",
        2278: "건설 조건 “%s 개발률 %d％ 이상(현재 %d％)”",
        2524: "교섭치 %s％",
        2651: "개발률 25％ 이상인 성",
        2914: "무장이 %d％ 확률로 부상",
        3102: "비용 %d％",
        3110: "획득 군량 +%d％",
        3113: "획득 물자 +%d％",
        3164: "영향에 따른 민충 감소를 %d％ 경감",
        3168: "획득 금전 +%d％",
        3187: "기간 -%d％",
        3750: "현재 영지를 다시 지행으로 수여할 수 없습니다",
        3751: "지행으로 수여할 영지를 지도에서 선택합니다",
        3752: "양도할 영지를 지도에서 선택합니다",
        3753: "소령 안도할 영지를 지도에서 확인합니다",
        3754: "소속되기를 희망하는 성을 지도에서 확인합니다",
        3759: "특수 양동 작전 건의 가능",
        3760: "다른 군단에 원군을 파견",
        3766: "이 항목은 변경할 수 없습니다",
        3774: "시나리오 “%s” 시작 시 이 무장은 등장 전입니다\n설정한 신분은 겐푸쿠할 때 반영됩니다",
        3785: "가재 특성을 설정합니다",
        3786: "봉행 특성을 설정합니다",
        3787: "출신을 설정합니다",
        3788: "%s 탭의 편집 내용을 초기화합니다",
        3791: "정책 “제도 개신 2” LV2를 발령하면 이용할 수 있습니다",
        3792: "가재와 봉행을 임명해 세력을 강화합니다",
        3793: "가로 이상의 무장이 없어 임명할 수 없습니다",
        3797: "본가에 종속된 세력이 있으면 도자마 가재를 임명할 수 있습니다",
        3798: "봉행으로 임명할 수 있는 무장이 없습니다",
        3799: "가재를 겸임할 수 없습니다",
        3800: "다이묘가 바뀌면 봉행으로 다시 임명할 수 있습니다",
        3805: "이미 봉행으로 임명한 무장입니다",
        3817: "결전의 방위전을 치르는 성이라 해제할 수 없습니다",
        3819: "소속 세력을 변경합니다",
        3824: "도자마 가재를 임명할 수 있습니다",
        3834: "추가 효과 설명 6",
        3839: "등용을 거부한 포획 무장을 설득합니다",
        3840: "등용한 무장에게 가르침을 청합니다",
        3841: "성주의 항복을 받아들이고 영주를 석방합니다",
        3845: "가보 등을 건네 외교 자세를 개선합니다",
        3846: "공적을 인정받아 감장을 받았습니다",
        3847: "동요 상태인 성에서는 출진할 수 없습니다",
        3848: "성 역할 해제",
        3852: "BGM 설정을 초기화했습니다",
        3854: "정전 제안을 준비합니다",
        3856: "대상 방위 거점 또는 그 지원 거점과 인접하지 않습니다",
        3859: "·봉행 증설 불가",
        3861: "선택 중인 방위 거점입니다",
        3863: "새 군단을 맡길 수 있는 무장이 없습니다",
        3866: "성주가 될 만큼 공훈을 얻지 못해 임명할 수 없습니다",
        3867: "성주가 될 만큼 공훈을 얻지 못해 확약할 수 없습니다",
        3868: "금전을 건넵니다",
        3871: "상대 성이 본래 보유한 영지를 건넵니다",
        3872: "성을 건넵니다",
        3873: "현재 지행을 수년간 보장합니다",
        3874: "새 지행을 주고 수년간 보장합니다",
        3875: "지금까지의 공훈을 치하하고 신분을 보장합니다",
        3878: "건넬 수 있는 충분한 금전이 없습니다",
        3879: "건넬 수 있는 가보가 없습니다",
        3880: "수여할 수 있는 관직이 없습니다",
        3881: "상대에게 돌려줄 영지가 없습니다",
        3882: "상대와 인접한 영지 중 건넬 수 있는 영지가 없습니다",
        3899: "정책 “제도 개신 2” LV2를 발령하면 증설할 수 있습니다",
        3900: "낙성 직후 혼란 상태라 지행을 임명할 수 없습니다",
        3905: "가재로 임명 중이라 변경할 수 없습니다",
        3906: "봉행으로 임명 중이라 변경할 수 없습니다",
        3907: "선택한 얼굴로 변경합니다",
        3908: "선택한 음성으로 변경합니다",
        3909: "군단장의 제안이 없어 %s을(를) 실행할 수 없습니다",
        3912: "원군을 보낼 수 있는 부대가 없습니다",
        3923: "조언의 공훈을 치하하고 무장으로 발탁합니다",
        3927: "튜토리얼에서는 선택할 수 없습니다",
        3928: "선택에 따라 이후 전개에 영향을 미칩니다",
        3929: "성에 특정 역할을 명령합니다",
        3930: "방위를 강화하고 적의 침공에 대비할 성을 설정합니다",
        3941: "전선에 있는 %s",
        3942: "후방에 있는 %s",
        3951: "선택한 이명을 사용합니다",
        3952: "관리할 명소가 없습니다",
        3953: "파기를 요구할 수 있는 동맹 세력이 없습니다",
        3955: "반환될 영지를 지도에서 확인합니다",
        3956: "본가와의 외교가 금지될 세력을 지도에서 확인합니다",
        3957: "본가가 동맹을 파기할 세력을 지도에서 확인합니다",
        3958: "신종한 세력을 지도에서 확인합니다",
        3959: "요구할 영지를 지도에서 선택합니다",
        3962: "외교 금지를 요구할 수 있는 세력이 없습니다",
        3963: "이 세력과의 외교를 금지합니다",
        3964: "교섭 상대는 선택할 수 없습니다",
        3965: "외교 가능한 거리가 아닙니다",
        3966: "혼인 동맹 파기는 요구할 수 없습니다",
        3968: "성주에서 강등되는 것은 받아들이지 않습니다",
        3970: "금전을 요구합니다",
        3971: "본가가 요구할 수 있는 영지가 없습니다",
        3973: "본가의 성이 원래 보유한 영지의 반환을 요구합니다",
        3974: "요구할 수 있는 가보가 없습니다",
        3977: "더 이상 요구할 수 없습니다",
        3978: "주요 안건은 철회할 수 없습니다",
        3980: "본거지는 양도할 수 없습니다",
        3981: "이 영지를 요구합니다",
        3983: "본가의 영지입니다",
        3985: "상대가 종속 세력이 아니므로 요구할 수 없습니다",
        3988: "적 부대에 주는 피해 증가",
        3989: "전법·요충지·설비 게이지 회복 속도 상승",
        3990: "소속 성의 병량 수입 상승",
        3991: "%d개월간 지정 세력과의 외교를 금지합니다(정전 제외)",
        3993: "본가에 종속하도록 변경합니다",
        4003: "%s에 신종",
        4012: "군단장이 있는 성은 수여할 수 없습니다",
        4013: "요청한 쪽이므로 변경할 수 없습니다",
        4017: "특정 무장의 가신이 되기로 약속합니다",
        4018: "이미 도자마 가재로 임명했습니다",
        4019: "다음부터 표시하지 않기",
        4021: "재건 조건 “%s의 개발률 %d％ 이상(현재 %d％)”",
        4022: "발전 조건 “%s의 성 %d곳의 개발률 %d％ 이상(현재 %d/%d)”",
        4024: "감장을 수여하거나 공훈을 확인합니다",
        4031: "확약 완료 무장",
        4037: "『노부나가의 야망·대지 파워업키트』에서 이어받을 등록 무장을 선택합니다",
        4038: "『노부나가의 야망·신생』에서 이어받을 등록 무장을 선택합니다",
        4039: "등록 무장 선택 중에는 목록을 전환할 수 없습니다",
        4040: "『노부나가의 야망·신생』의 등록 무장 데이터가 없습니다",
        4041: "이어받을 수 있는 등록 무장 데이터가 없습니다",
        4042: "『노부나가의 야망·신생』 및 『노부나가의 야망·대지 파워업키트』의 등록 무장 데이터를 이어받습니다",
        4044: "시나리오에 등장할 추가 무장을 선택합니다",
        4045: "시나리오에 반영할 실존 무장의 편집 데이터를 선택합니다",
        4046: "신앙을 설정합니다",
        4055: "%s의 개발률 %d％ 이상(현재 %d％)",
        4056: "%s의 성 %d곳의 개발률 %d％ 이상(현재 %d/%d)",
        4059: "\x1bCPΣ\x1bCZ공성전 불가 최대 병력의 %d％(%d) 필요",
    }
)

RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
SHORT_UI_IDS = {2757, 2758}
TERM_IDS = {687, 1420, 3774}
FULLWIDTH_PERCENT_IDS = {
    2139, 2140, 2154, 2155, 2278, 2524, 2651, 2914, 3102, 3110,
    3113, 3164, 3168, 3187, 4021, 4022, 4055, 4056, 4059,
}


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def format_profile(text: str) -> dict[str, object]:
    return {
        "runtime": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "esc": ESC_RE.findall(text),
        "linebreaks": re.findall(r"\r\n|\n|\r", text),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "private_use": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "fullwidth_percent_count": text.count("％"),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    tmp_root = (REPO / "tmp").resolve()
    output = args.output.resolve()
    if output == tmp_root or tmp_root not in output.parents:
        raise SystemExit("output must remain below tmp")
    if any(3625 <= entry_id <= 3670 for entry_id in FIXES):
        raise SystemExit("3625--3670 belongs to the separately reviewed slice")

    rows = {
        int(row["coordinate"]): row
        for row in map(json.loads, args.input.read_text(encoding="utf-8").splitlines())
        if row["resource"] == "msgui"
    }
    if set(FIXES) - set(rows):
        raise SystemExit("review coordinate is absent from msgui inventory")

    output_rows: list[dict[str, object]] = []
    for entry_id, ko in sorted(FIXES.items()):
        row = rows[entry_id]
        profile = format_profile(row["jp"])
        if profile != format_profile(ko):
            raise SystemExit(f"format mismatch against pristine JP at msgui:{entry_id}")
        if KANA_OR_HAN_RE.search(ko):
            raise SystemExit(f"Korean proposal retains Japanese/CJK at msgui:{entry_id}")
        if not re.search(r"[가-힣]", ko):
            raise SystemExit(f"Korean proposal has no Hangul at msgui:{entry_id}")
        if "?" in ko and not ko.rstrip().endswith("?"):
            raise SystemExit(f"suspicious question-mark replacement at msgui:{entry_id}")
        if ko == row["ko"]:
            raise SystemExit(f"proposal is not an effective correction at msgui:{entry_id}")
        issue = "coordinate_semantic_misalignment"
        if entry_id in SHORT_UI_IDS:
            issue = "short_ui_translation"
        elif entry_id in TERM_IDS:
            issue = "terminology_correction"
        elif entry_id in FULLWIDTH_PERCENT_IDS:
            issue = "format_fullwidth_percent"
        output_rows.append(
            {
                "id": entry_id,
                "issue": issue,
                "ko": ko,
                "current_hash": text_hash(row["ko"]),
                "format": profile,
            }
        )

    expected_count = 248
    if len(output_rows) != expected_count:
        raise SystemExit(f"unexpected proposal count: {len(output_rows)} != {expected_count}")
    atomic_write(output, "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in output_rows))
    print(
        json.dumps(
            {
                "entry_count": len(output_rows),
                "output": str(output),
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
                "game_files_written": False,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
