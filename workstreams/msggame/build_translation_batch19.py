#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 19."""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys
from types import SimpleNamespace
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent


def _load_isolated_engine() -> Any:
    """Load batch 18's verified generator in a private module namespace.

    Batch generators intentionally keep their complete scope and pinned-artifact
    logic together.  Loading the immediately preceding generator privately lets
    this batch retain that byte-for-byte validation path without mutating the
    public ``build_translation_batch18`` module used by its own regression test.
    """

    engine_path = WORKSTREAM_ROOT / "build_translation_batch18.py"
    spec = importlib.util.spec_from_file_location("_msggame_batch19_engine", engine_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load generator engine: {engine_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_engine = _load_isolated_engine()

BATCH_ID = "msggame_pk_system_messages_b06r3302_3477.v0.19"
OVERLAY_NAME = "msggame_ko_system_messages_b06r3302_3477.v0.19.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.19.json"
REVIEW_NAME = "translation_review_index.v0.19.json"
VALIDATION_NAME = "translation_validation.v0.19.json"
RESOURCE = _engine.RESOURCE
LANGUAGES = _engine.LANGUAGES
SOURCE_PATHS = _engine.SOURCE_PATHS
WORKSPACE_ROOT = _engine.WORKSPACE_ROOT
previous = _engine.previous
NEXT_COORDINATE = (6, 3478, 0)


# Project-authored Korean only.  Values retain the SC literal-slot layout;
# ``None`` preserves a non-visible empty slot without publishing source text.
TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 3302): ("잃어선 안 될 대상:", "\n어떻게든 지켜 주십시오."),
    (6, 3306): ("금전이 부족하여 조정과 교섭할 수 없습니다.",),
    (6, 3307): ("본가는 방금 조정과의 교섭을 마쳤습니다.",),
    (6, 3308): ("금전이 부족하여 조정에 주청할 수 없습니다.",),
    (6, 3309): ("위신이 부족하여 조정에 주청할 수 없습니다.",),
    (6, 3310): ("조정에 주청할 내용이 없습니다.",),
    (6, 3311): ("다른 항목과 동시에 주청할 수 없습니다.",),
    (6, 3312): ("본가의 악명이 높아 관직을 받을 수 없습니다.",),
    (6, 3313): ("본가는 관직을 주청할 만한 규모가 아닙니다.",),
    (6, 3314): ("주청할 수 있는 관직이 없습니다.",),
    (6, 3315): ("다른 항목과 동시에 주청할 수 없습니다.",),
    (6, 3316): ("다른 가문에 종속되어 있어 칙명 강화를 요청할 수 없습니다.",),
    (6, 3317): ("본가의 악명이 높아 칙명 강화를 주청할 수 없습니다.",),
    (6, 3318): ("다른 항목과 동시에 주청할 수 없습니다.",),
    (6, 3319): ("악명을 낮출 필요가 없습니다.",),
    (6, 3320): ("다른 항목과 동시에 주청할 수 없습니다.",),
    (6, 3321): ("본가는 조정에 충분히 공헌하고 있습니다.",),
    (6, 3322): ("금전이 부족합니다.",),
    (6, 3323): ("필요 금전:", "이상입니다."),
    (6, 3324): ("조정에 금전을 헌상합니다.",),
    (6, 3325): ("조정에 관직을 주청합니다.",),
    (6, 3326): (
        "두 세력을 선택하여 6개월간 정전을 주청합니다.\n"
        "본가와 우군, 그리고 그 적대 세력을 선택할 수 있습니다.",
    ),
    (6, 3327): ("조정에 금전을 헌상하여 본가의 악명을 낮춥니다.",),
    (6, 3328): ("다음 관직을 얻기 위해 공헌도 상승을 주청합니다.",),
    (6, 3329): ("이 세력을 칙명 강화 주청의 첫 번째 세력으로 선택합니다.",),
    (6, 3330): ("독립하지 않은 세력과는 칙명 강화를 주청할 수 없습니다.",),
    (6, 3331): ("본가보다 관위가 높은 세력은 선택할 수 없습니다.",),
    (6, 3332): ("세력의 악명이 40 이상이므로 칙명 강화를 주청할 수 없습니다.",),
    (6, 3333): ("본가나 우군과 칙명 강화를 맺을 필요가 없습니다.",),
    (6, 3334): ("이 세력과의 칙명 강화를 주청할 금전이 부족합니다.",),
    (6, 3335): ("이 세력과의 상대:", "와 칙명 강화를 주청합니다."),
    (6, 3336): ("독립하지 않은 세력과는 칙명 강화를 주청할 수 없습니다.",),
    (6, 3337): ("본가보다 관위가 높은 세력은 선택할 수 없습니다.",),
    (6, 3338): ("세력의 악명이 40 이상이므로 칙명 강화를 주청할 수 없습니다.",),
    (6, 3339): ("이 세력과의 상대:", "와 칙명 강화를 맺을 필요가 없습니다."),
    (6, 3340): ("이 세력과의 상대:", "와 칙명 강화를 주청할 금전이 부족합니다."),
    (6, 3341): ("이미 선택한 세력입니다.",),
    (6, 3342): ("참으로 훌륭한 마음가짐이로다.\n앞으로도 근왕의 뜻을 잊지 말거라.",),
    (6, 3343): ("께서 찾아오시다니 드문 일이군.\n무슨 용건인가?",),
    (6, 3344): ("\n자주 찾아오는군.",),
    (6, 3345): ("오,", "\n오랜만이구나."),
    (6, 3346): ("오,", "대감!\n폐하께서도 기다리고 계십니다."),
    (6, 3347): ("칙명 강화의 대상이 될 세력이 없습니다.",),
    (6, 3348): ("의 임명 직위:", "입니다."),
    (6, 3349): ("의 악명:", "입니다."),
    (6, 3350): ("의 조정 공헌도:", "입니다."),
    (6, 3351): ("이 해임을 실행하면\n군단이 해산되고 혼인 동맹도 파기됩니다.\n계속하시겠습니까?",),
    (6, 3352): ("이 해임을 실행하면\n군단이 해산됩니다.\n계속하시겠습니까?",),
    (6, 3353): ("이 해임을 실행하면\n혼인 동맹이 파기됩니다.\n계속하시겠습니까?",),
    (6, 3356): ("이 추방을 실행하면\n상대 세력:", "와의 혼인 동맹이 파기됩니다.\n계속하시겠습니까?"),
    (6, 3357): ("안 됩니다…… 이렇게 되면\n상대 세력:", "와의 혼인 동맹이\n파기됩니다……"),
    (6, 3358): ("추방이라니……\n상대 세력:", "와의 혼인 동맹이 무너집니다!"),
    (6, 3362): ("추방 대상:", "을 내쫓으면,\n상대 세력:", "와의 혼인 동맹이\n사라집니다……"),
    (6, 3366): ("추방 대상:", "을 내쫓으면,\n상대 세력:", "와의 혼인 동맹이\n사라집니다……"),
    (6, 3369): ("군단을 이끌면서도 쓸모없다니……\n나 자신도 한심하군.",),
    (6, 3370): ("군단을 이끄는 이 몸마저\n쓸모없다는 겁니까!",),
    (6, 3371): ("이래 봬도 군단을 이끄는 몸인데\n그래도 쓸모없단 말인가?",),
    (6, 3375): ("군단장:", "을 추방하다니,\n몹시 미움받았나 보군요……"),
    (6, 3381): ("필요 없다면\n어리석은 당주에게 미련 따위 없습니다.",),
    (6, 3382): ("필요하지 않으시다면\n미련은 없습니다……",),
    (6, 3383): ("필요 없다면\n미련 따위 없습니다……",),
    (6, 3387): ("나를 필요로 하는\n세력:", "을 찾아 떠나겠습니다……"),
    (6, 3391): ("이, 이건 받아들일 수 없습니다!\n어째서", "이 이런 일을……"),
    (6, 3392): ("어, 어째서 이런 일이……\n섬길 주군을 잘못 고른 모양이군.",),
    (6, 3393): ("이, 이게 무슨……!?\n……언젠가 반드시 후회할 것이다.",),
    (6, 3394): ("후계자가 군단장이므로\n군단을 해산하고 다이묘 직할로 편입합니다.\n계속하시겠습니까?",),
    (6, 3395): ("선택한 후계자는 혈족이 아닌 무장입니다.\n혈족 무장의 충성이 낮아집니다.\n계속하시겠습니까?",),
    (6, 3400): ("이 판단이 옳았음을\n증명하기 위해 가문:", "을 평생을 걸고 번영시켜\n증명하겠습니다."),
    (6, 3401): ("의 이름은 무겁지만 자랑스럽기도 하여,\n절로 마음이 다잡힙니다.\n이후는 제게 맡겨 주십시오.",),
    (6, 3402): (
        "계승할 대상:",
        "의 자리를 잇게 되어 영광입니다.\n충성을 바칠 자:",
        "는 목숨을 걸고,\n지킬 대상:",
        "을 지키겠습니다.",
    ),
    (6, 3403): (
        "안심하십시오.",
        "께서 지켜 온 가문:",
        "을 제 지략과 무용으로\n이어가겠습니다……\n아니, 더욱 번성시키겠다고 맹세합니다.",
    ),
    (6, 3404): ("더없는 영광입니다!\n은혜를 베풀어 주신 분:", "께 반드시 보답하여,\n본가를 번영시키겠습니다!"),
    (6, 3405): ("님, 지금까지 본가의 주인으로서\n정말 수고 많으셨습니다.\n후임:", "에게 맡겨 주십시오."),
    (6, 3412): ("님, 안심하십시오.\n저", "는 목숨을 걸고,\n지킬 가문:", "을 지키겠습니다."),
    (6, 3417): ("후임:", "는\n선대를 대신해 본가를 지키겠습니다!"),
    (6, 3418): ("후임:", "에게 맡겨 주십시오.\n본가를 번영으로 이끌겠습니다."),
    (6, 3419): ("당주의 막중한 임무를 맡겠습니다……\n앞으로도 사명을 다하겠습니다.",),
    (6, 3420): ("미지행 군 중 군량 생산 효과가 있는 군에\n정무 능력이 높은 무장을 우선 임명합니다. 계속하시겠습니까?",),
    (6, 3421): ("미지행 군 중 금전 수입 효과가 있는 군에\n정무 능력이 높은 무장을 우선 임명합니다. 계속하시겠습니까?",),
    (6, 3422): ("미지행 군 중 병력 상승 효과가 있는 군에\n정무 능력이 높은 무장을 우선 임명합니다. 계속하시겠습니까?",),
    (6, 3423): ("미지행 군 중 군마 생산 효과가 있는 군에\n정무 능력이 높은 무장을 우선 임명합니다. 계속하시겠습니까?",),
    (6, 3424): ("미지행 군 중 철포 생산 효과가 있는 군에\n정무 능력이 높은 무장을 우선 임명합니다. 계속하시겠습니까?",),
    (6, 3425): ("모든 군의 지행 무장을 해임합니다.\n계속하시겠습니까?",),
    (6, 3426): ("의 임기:", "동안 충성 보정을 잃습니다.\n계속하시겠습니까?"),
    (6, 3429): ("의 공훈:", "이 1위인가요……\n부끄럽지만 매우 영광입니다.\n올해도", "을 위해 최선을 다하겠습니다."),
    (6, 3430): ("제가 공훈 1위라니\n정말 기쁩니다.\n상으로", "을 주시면 더없이 좋겠습니다."),
    (6, 3431): ("제가 공훈 1위라니\n정말 기쁩니다.\n상으로", "을 주시면 더없이 좋겠습니다."),
    (6, 3435): ("제가 공훈 1위라니\n정말 기쁩니다.\n상으로", "을 주시면 더없이 좋겠습니다."),
    (6, 3441): ("공훈 1위라니,\n아직 부족하지만\n차근차근 노력하여\n본가에 공헌하겠습니다.",),
    (6, 3442): ("대인께서 이끌어 주신 덕에\n저도 꾸준히 나아가고 있습니다.\n앞으로도 중용해 주십시오.",),
    (6, 3443): ("대인께서 이끌어 주신 덕에\n저도 꾸준히 나아가고 있습니다.\n앞으로도 중용해 주십시오.",),
    (6, 3447): ("대인께서 이끌어 주신 덕에\n저도 꾸준히 나아가고 있습니다.\n앞으로도 중용해 주십시오.",),
    (6, 3453): ("공훈 1위는 기쁘지만,\n이 자리는 아직 제게 과분합니다.\n더욱 노력하겠습니다.",),
    (6, 3454): ("대인께서 중용해 주신 덕에\n제 능력을 더욱 발휘하게 되었습니다.\n앞으로도 잘 부탁드립니다.",),
    (6, 3455): ("오, 공훈 1위라……\n직위:", "이 되면 할 일이 많으니,\n당연히 열심히 해야지."),
    (6, 3459): ("대인께서 중용해 주신 덕에\n제 능력을 더욱 발휘하게 되었습니다.\n앞으로도 잘 부탁드립니다.",),
    (6, 3465): ("로서", "공훈 1위는 당연하지만,\n아직 정상과는 멀었습니다.\n올해는 더 크게 도약하겠습니다."),
    (6, 3466): ("마침내", "에 이르렀습니다……\n", "칭찬해 주십시오!\n참고로", "은 좋아하는 것:", None),
    (6, 3467): ("마침내", "에 이르렀습니다……\n", "칭찬해 주십시오!\n참고로", "은 좋아하는 것:", None),
    (6, 3471): ("마침내", "에 이르렀습니다……\n", "칭찬해 주십시오!\n참고로", "은 좋아하는 것:", None),
    (6, 3477): ("공훈 수석이 되다니\n더없이 영광입니다.\n앞으로도 가문의 번영을 위해 힘쓰겠습니다.",),
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
    if selected[0] != (6, 3302, 0) or selected[-1] != (6, 3477, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 101:
        raise ValueError("translation batch scope changed")
    if SKIPPED_CANDIDATES:
        raise ValueError("translation batch unexpectedly contains skips")


# Keep the established generator fully isolated from v0.18's import namespace.
# Three selected records have a trailing empty literal slot.  It is deliberately
# represented by ``None`` above, while the surrounding non-empty literals remain
# the exact next SC candidates.  The private engine accepts that inert slot only;
# the public ``previous`` alias remains unmodified for scan regression tests.
_engine_previous = _engine.previous
_engine.previous = SimpleNamespace(**vars(_engine_previous))
_engine.previous.is_visible_translation_candidate = (
    lambda text: _engine_previous.is_visible_translation_candidate(text) or text == ""
)
_engine.SCRIPT_PATH = SCRIPT_PATH
_engine.BATCH_ID = BATCH_ID
_engine.OVERLAY_NAME = OVERLAY_NAME
_engine.EVIDENCE_NAME = EVIDENCE_NAME
_engine.REVIEW_NAME = REVIEW_NAME
_engine.VALIDATION_NAME = VALIDATION_NAME
_engine.NEXT_COORDINATE = NEXT_COORDINATE
_engine.TRANSLATIONS = TRANSLATIONS
_engine.SKIPPED_CANDIDATES = SKIPPED_CANDIDATES
_engine.EXPECTED_RECORD_KEYS = EXPECTED_RECORD_KEYS
_engine.validate_static_scope = validate_static_scope

# The shared build body has one scope-boundary assertion in addition to its
# static validator.  Rebind only that assertion inside the private engine so
# v0.18 remains independently importable and testable.
_engine.LAST_COORDINATE = (6, 3477, 0)
_engine_build_source = inspect.getsource(_engine.build)
_old_boundary_assertion = (
    "if selected[-1] != (6, 3298, 0) or NEXT_COORDINATE not in sc_literals:"
)
if _old_boundary_assertion not in _engine_build_source:
    raise RuntimeError("batch 18 engine boundary assertion changed")
exec(
    compile(
        _engine_build_source.replace(
            _old_boundary_assertion,
            "if selected[-1] != LAST_COORDINATE or NEXT_COORDINATE not in sc_literals:",
        ),
        str(SCRIPT_PATH),
        "exec",
    ),
    _engine.__dict__,
)
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
