#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 22."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent


def _load_isolated_engine() -> Any:
    """Load batch 21 privately so its public import state stays untouched."""

    engine_path = WORKSTREAM_ROOT / "build_translation_batch21.py"
    spec = importlib.util.spec_from_file_location("_msggame_batch22_engine", engine_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load generator engine: {engine_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_template = _load_isolated_engine()
_engine = _template._engine

BATCH_ID = "msggame_pk_system_messages_b06r3841_3930.v0.22"
OVERLAY_NAME = "msggame_ko_system_messages_b06r3841_3930.v0.22.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.22.json"
REVIEW_NAME = "translation_review_index.v0.22.json"
VALIDATION_NAME = "translation_validation.v0.22.json"
RESOURCE = _engine.RESOURCE
LANGUAGES = _engine.LANGUAGES
SOURCE_PATHS = _engine.SOURCE_PATHS
WORKSPACE_ROOT = _engine.WORKSPACE_ROOT
previous = _engine.previous
NEXT_COORDINATE = (6, 3930, 1)


# Project-authored Korean only.  Tuples retain every SC literal slot in each
# record; the two trailing slots in record 3930 intentionally stay ``None``
# because this fixed-size batch ends at its first visible literal.
TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 3841): ("의 소속이 바뀌어,", "의 건설을 중단했습니다."),
    (6, 3842): ("근거지 이전으로,", "건설 중단:", "."),
    (6, 3843): ("가 교전 상태가 되어,", "의 건설을 중단했습니다."),
    (6, 3844): ("무장이 없어,", "건설 중단:", "."),
    (6, 3845): ("상황이 악화되어,", "건설 중단:", "."),
    (6, 3846): ("건설 완료:", "의 건설이 완료되었습니다."),
    (6, 3847): ("의 당주", "\n가 면회를 요청해 찾아왔습니다."),
    (6, 3848): ("이번에는", "의 체면을 보아,\n상대", "와의 전쟁을,\n멈춰 주실 수 있겠습니까?"),
    (6, 3849): ("……알겠습니다.\n이번에는", "의 체면을 보아,\n상대", "와 정전하겠습니다. "),
    (6, 3850): ("에게는", "와의 동맹이 있어,\n섣불리 공격하는 것은 위험합니다."),
    (6, 3851): ("와", "의 동맹을", "개월 연장했습니다."),
    (6, 3852): ("와", "의 정전을", "개월 연장했습니다."),
    (6, 3853): ("상대", "의 영내에 병력이 남아 있어,\n동맹이 연장되었지만,\n주변 세력은 불신을 품고 있습니다……"),
    (6, 3854): ("상대", "의 영내에 병력이 남아 있어,\n정전이 연장되었지만,\n주변 세력은 불신을 품고 있습니다……"),
    (6, 3855): ("다음 관직:", "이지만,\n본가의 위신이 부족해\n추천을 받기 어려울 듯합니다."),
    (6, 3856): ("다음으로,\n상대", "의 관직 추천을 추진해 봅시다."),
    (6, 3857): ("다음 관직:", "이지만,\n본가의 위신과 가문 격이 다소 부족해\n상당한 금전이 들 듯합니다."),
    (6, 3858): ("연락 무장이 없어,\n조정의 신용이 오르지 않습니다.",),
    (6, 3859): ("조정의 신용을 충분히 얻었지만,\n관직에 빈자리가 없다고 합니다……\n헌금을 중단하고 기다릴 수밖에 없습니다.",),
    (6, 3860): ("그대의 근왕의 뜻은 잘 알겠다.\n천자의 명으로", "을 내리겠다."),
    (6, 3861): ("비용이 들더라도,\n상대", ",\n상대", "에 잘 청원합시다."),
    (6, 3862): ("그대가", "에 임명되었다는 소식을 들으면,\n분명 기뻐 춤출 것입니다."),
    (6, 3863): ("그대가", "에 임명되어,\n기뻐하지 않을 다이묘가 어디 있겠는가."),
    (6, 3864): ("께서,\n", "가 막부 사자로 찾아왔습니다."),
    (6, 3865): ("의", "활약이 주목받아,\n관직", "의 중책을 맡게 되었습니다……\n더없는 영광입니다."),
    (6, 3866): ("그대가", "에 임명되면,\n임지 국중에 대한 영향력도 높아질 것입니다."),
    (6, 3867): ("그대가", "에 임명되면,\n본가의 위신도 더욱 높아질 것입니다."),
    (6, 3868): ("뭐라고?관직", "취임을 거절하다니……!"),
    (6, 3869): ("취임은,\n대단히 죄송하지만 사양하겠습니다.",),
    (6, 3870): ("동의:", "가", "의", "요청을 수락했습니다."),
    (6, 3871): ("동의:", "의", "요청을 수락했습니다."),
    (6, 3872): ("동의로", "와", "의 동맹이 연장되었습니다."),
    (6, 3873): ("정책「", "」의 발전이 완료되었습니다."),
    (6, 3874): ("정책「", "」의 발전을 중단했습니다."),
    (6, 3875): ("발전 한도에 도달해 정책「", "」의 발전을 중단했습니다."),
    (6, 3876): ("무장이 없어 정책「", "」의 작업을 중단했습니다."),
    (6, 3877): ("이대로면 금전 수지가 적자가 됩니다.\n계속하시겠습니까?",),
    (6, 3878): ("봉행 변경으로 정책“", "”의 발전을 중단했습니다."),
    (6, 3879): ("봉행 변경으로 정책“", "”을 철회했습니다."),
    (6, 3880): ("철거 대상:", "을 철거하시겠습니까?"),
    (6, 3881): ("건설의 임무, 알겠습니다.\n이번에", "을 완성하면,\n반드시 본가에 이로울 것입니다."),
    (6, 3882): ("알겠습니다,\n그대가", "나서면,\n", "의 건설쯤은 식은 죽 먹기입니다."),
    (6, 3883): ("의 건설은 훌륭한 계책이니,\n즉시 시행하겠습니다.",),
    (6, 3884): ("건설 시작:", "의 건설을 시작하겠습니다.\n부지런히 일한 자에게는 큰 상을 내릴 테니,\n모두 힘써 주십시오."),
    (6, 3885): ("건설 시작:", "의 건설에 힘써,\n우리 성하를 더욱 훌륭하게 만들겠습니다."),
    (6, 3886): ("우리 성하에", "을 건설하겠습니다.\n손을 빼지 말고 후세에 남길 만한 것으로 합시다."),
    (6, 3887): ("이제 시간을 진행하면 시설 건설이 시작됩니다.\n이번은 튜토리얼이므로 금전과 노동력은 들지 않습니다.\n건설 결과도 곧바로 확인할 수 있습니다.",),
    (6, 3889): ("직위를 내려 준 것에 감사하고 있습니다.",),
    (6, 3890): ("선물을 준 것에 감사하고 있습니다.",),
    (6, 3891): ("본가의 세력에 일목을 두고 있습니다.",),
    (6, 3892): ("혼인 관계에 있어\n신뢰할 수 있습니다.",),
    (6, 3893): ("동맹으로서 신뢰하고 있습니다.",),
    (6, 3894): ("주종 관계에 있는 세력으로서\n신뢰하고 있습니다.",),
    (6, 3895): ("본가를 매우 신뢰하고 있습니다.",),
    (6, 3896): ("에", "\n호감을 품고 있습니다."),
    (6, 3897): ("와", "\n마음이 잘 맞습니다."),
    (6, 3898): ("선물로 경계를 풀었습니다.",),
    (6, 3899): ("본가의 기세를 주시하고 있습니다.",),
    (6, 3900): ("원군 요청은 거절했지만\n납득하고 있습니다.",),
    (6, 3901): ("불의를 저지른\n본가를 의심하고 있습니다.",),
    (6, 3902): ("동맹으로서 경계를 풀고 있습니다.",),
    (6, 3903): ("주종 관계에 있어\n경계를 풀고 있습니다.",),
    (6, 3904): ("특별히 관심을 두지 않습니다.",),
    (6, 3905): ("칼을 맞댄 지 얼마 되지 않았지만\n원한은 없습니다.",),
    (6, 3906): ("본가를 방패로 삼아\n중재한 지 얼마 되지 않았습니다.",),
    (6, 3907): ("불구대천의 원수로 여기고 있습니다.",),
    (6, 3908): ("배신자를 원망하고 있습니다.",),
    (6, 3909): ("동맹 제안을 거절당해\n원망하고 있습니다.",),
    (6, 3910): ("원군 요청을 거절당해\n당황하고 있습니다.",),
    (6, 3911): ("본가와의\n전투에서 크게 패했습니다.",),
    (6, 3912): ("불의를 저지른\n본가를 경계하고 있습니다.",),
    (6, 3913): ("주종 관계이지만\n신뢰하지 않고 있습니다.",),
    (6, 3914): ("본가를 경계하고 있습니다.",),
    (6, 3915): ("아버지의 원수로 원망하고 있습니다.",),
    (6, 3916): ("자식의 원수로 원망하고 있습니다.",),
    (6, 3917): ("형의 원수로 원망하고 있습니다.",),
    (6, 3918): ("아우의 원수로 원망하고 있습니다.",),
    (6, 3919): ("친족의 원수로 원망하고 있습니다.",),
    (6, 3920): ("현재 교전 중인 적입니다.",),
    (6, 3921): ("칼을 맞댄 지 얼마 되지 않아\n경계하고 있습니다.",),
    (6, 3922): ("계략을 당해\n강하게 경계하고 있습니다.",),
    (6, 3923): ("혐오:", "."),
    (6, 3924): ("동맹국이 있는\n본가를 경계하고 있습니다.",),
    (6, 3925): ("와", "\n마음이 맞지 않습니다."),
    (6, 3926): ("본가를 방패로 삼아\n중재한 지 얼마 되지 않았습니다.",),
    (6, 3927): ("장군가를 멸망시킨\n본가를 경계하고 있습니다.",),
    (6, 3928): ("어느 직위를 내리시겠습니까?",),
    (6, 3929): ("좋습니다.\n그렇다면", "을", "에게 내리겠습니다.\n막부를 위한 충성과 근면을 기대하겠습니다."),
    (6, 3930): ("에", None, None),
}

SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {}
EXPECTED_RECORD_KEYS = tuple(TRANSLATIONS)


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
    if keys != sorted(EXPECTED_RECORD_KEYS):
        raise ValueError("translation scan record set changed")
    if selected[0] != (6, 3841, 0) or selected[-1] != (6, 3930, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 89:
        raise ValueError("translation batch scope changed")
    if SKIPPED_CANDIDATES:
        raise ValueError("translation batch unexpectedly contains skips")


_engine.SCRIPT_PATH = SCRIPT_PATH
_engine.BATCH_ID = BATCH_ID
_engine.OVERLAY_NAME = OVERLAY_NAME
_engine.EVIDENCE_NAME = EVIDENCE_NAME
_engine.REVIEW_NAME = REVIEW_NAME
_engine.VALIDATION_NAME = VALIDATION_NAME
_engine.NEXT_COORDINATE = NEXT_COORDINATE
_engine.LAST_COORDINATE = (6, 3930, 0)
_engine.TRANSLATIONS = TRANSLATIONS
_engine.SKIPPED_CANDIDATES = SKIPPED_CANDIDATES
_engine.EXPECTED_RECORD_KEYS = EXPECTED_RECORD_KEYS
_engine.validate_static_scope = validate_static_scope
build = _engine.build


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
