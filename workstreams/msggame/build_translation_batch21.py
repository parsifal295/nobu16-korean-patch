#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 21."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent


def _load_isolated_engine() -> Any:
    """Load batch 20 privately so its public import state stays untouched."""

    engine_path = WORKSTREAM_ROOT / "build_translation_batch20.py"
    spec = importlib.util.spec_from_file_location("_msggame_batch21_engine", engine_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load generator engine: {engine_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_template = _load_isolated_engine()
_engine = _template._engine

BATCH_ID = "msggame_pk_system_messages_b06r3698_3837.v0.21"
OVERLAY_NAME = "msggame_ko_system_messages_b06r3698_3837.v0.21.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.21.json"
REVIEW_NAME = "translation_review_index.v0.21.json"
VALIDATION_NAME = "translation_validation.v0.21.json"
RESOURCE = _engine.RESOURCE
LANGUAGES = _engine.LANGUAGES
SOURCE_PATHS = _engine.SOURCE_PATHS
WORKSPACE_ROOT = _engine.WORKSPACE_ROOT
previous = _engine.previous
NEXT_COORDINATE = (6, 3841, 0)


# Project-authored Korean only.  Every tuple retains the SC record's literal
# slots, including dynamic clan, officer, and territory insertions between
# literals.  The public overlay never includes original game text.
TRANSLATIONS: dict[tuple[int, int], tuple[str, ...]] = {
    (6, 3698): ("와", "의 동맹도 이제 두 달 남았습니다.\n동맹을 이어 갈지 끝낼지,\n잘 생각해 주십시오."),
    (6, 3702): ("와", "의 동맹도 이제 두 달 남았습니다.\n동맹을 이어 갈지 끝낼지,\n부디 신중히 생각해 주십시오."),
    (6, 3706): ("와", "의 동맹도 이제 두 달 남았습니다.\n동맹을 이어 갈지 끝낼지,\n부디 잘 생각해 주십시오."),
    (6, 3709): ("와", "의 동맹은 끝났습니다.\n아직 3개월간 정전은 이어지지만,\n절대 방심하지 마십시오."),
    (6, 3710): ("와", "의 동맹은 기한이 지났습니다.\n아직 3개월간 정전은 이어지지만,\n후방을 조심하십시오."),
    (6, 3711): ("와", "의 동맹은 기한이 되었다고 합니다.\n아직 3개월간 정전은 이어지지만,\n빈틈을 보이지 않도록 하십시오."),
    (6, 3715): ("와", "의 동맹은 기한이 지났습니다.\n아직 3개월간 정전은 이어지지만,\n경계를 늦추지 마십시오."),
    (6, 3721): ("와", "의 정전도 이제 두 달 남았습니다.\n정전이 끝나면 상대 영내에 머문 병력은 철수시켜야 합니다.\n이후에도 평화를 유지할지 신중히 생각해 주십시오."),
    (6, 3722): ("와", "의 정전도 이제 두 달 남았습니다.\n정전이 끝나면 상대 영내에 머문 병력은 철수시켜야 합니다.\n이후에도 평화를 지킬지 잘 생각해 주십시오."),
    (6, 3723): ("와", "의 정전도 이제 두 달 남았습니다.\n정전이 끝나면 상대 영내에 머문 병력은 철수시켜야 합니다.\n이후에도 평화를 유지할지 생각해 주십시오."),
    (6, 3727): ("와", "의 정전도 이제 두 달 남았습니다.\n정전이 끝나면 상대 영내에 머문 병력은 철수시켜야 합니다.\n평화를 지킬 수 있을지 잘 생각해 주십시오."),
    (6, 3731): ("와", "의 정전 기한이 끝났습니다.\n부디 조심하십시오."),
    (6, 3732): ("와", "의 정전 기한이 되었습니다.\n빈틈을 보이지 않도록 유의하십시오."),
    (6, 3735): ("와", "의 정전은 끝났습니다.\n만반의 준비를 하셔야 할 듯합니다."),
    (6, 3736): ("와", "의 정전은 기한이 지났습니다.\n후방을 조심하십시오."),
    (6, 3737): ("와", "의 정전은 기한이 되었다고 합니다.\n틈을 보이지 않도록 하십시오."),
    (6, 3745): ("교섭으로:", "가", "의 영지에 왔습니다."),
    (6, 3746): ("교섭으로:", "가", "의 영지에 왔습니다."),
    (6, 3747): ("정말로\n해임 대상:", "와의 연락 무장을 해임하시겠습니까?"),
    (6, 3748): ("와", "의 관계를 더욱 돈독히 하도록\n신중히 임무를 맡기십시오."),
    (6, 3749): ("와", "의 교섭을 중단했습니다."),
    (6, 3750): ("대신", ",\n상대", "와의 관계를 더욱 돈독히 하도록 힘쓰겠습니다."),
    (6, 3751): ("대신", ",\n상대", "와의 관계 유지를 위해 힘쓰겠습니다."),
    (6, 3752): ("관계를 강화하려면\n", "의 신용을 일정 수준 이상으로 올려야 합니다."),
    (6, 3753): ("와", "의 관계 유지를 위해 힘쓰겠습니다."),
    (6, 3754): ("관계 유지에는 그리 많은 비용이 들지 않습니다.",),
    (6, 3756): ("본가와", "사이를\n잘 중재해 보이겠습니다."),
    (6, 3757): ("상대", "의 신뢰를 얻기 위해,\n신중히 임하겠습니다."),
    (6, 3758): ("본가의 얼굴로서", "\n에게서 신뢰를 얻어 보이겠습니다."),
    (6, 3759): ("연락 무장이 없어\n신용이 오르지 않습니다.",),
    (6, 3760): ("연락 무장을 임명하면\n매월 신용이 오릅니다.",),
    (6, 3761): ("상대", "에 당장 원군을 요청하기는 어렵습니다.\n그것이 목적이라면 다시 생각해야 하지만,\n앞날을 내다본 일이라면 좋은 방안일 듯합니다."),
    (6, 3762): ("상대", "에 당장 원군을 요청하기는 어렵습니다.\n그것이 목적이라면 어리석은 방책이지만,\n앞날을 보고 신용을 쌓는 것도 나쁘지 않습니다."),
    (6, 3763): (",", "의\n", "가 찾아왔습니다."),
    (6, 3764): ("두 가문 사이에 굳건한 신뢰를 쌓고 싶습니다……\n훗날 동맹을 맺겠다는 약정에 동의하시겠습니까?",),
    (6, 3765): ("때가 무르익으면,\n상대", "와 손잡고 싶습니다.\n그때 만족스러운 답을 받을 수 있기를……"),
    (6, 3766): ("훗날", "에게 원군 등 군사 지원을 부탁하고 싶습니다……\n그 약속을 받아들이시겠습니까?"),
    (6, 3767): ("본가로서는,\n상대", "와의 관계를 오래 이어 가고 싶습니다.\n그대도 같은 생각이십니까?"),
    (6, 3768): ("좋은 답을 받아 더없이 기쁩니다.\n앞으로도 잘 부탁드립니다.",),
    (6, 3769): ("……알겠습니다.\n그것이 귀가의 뜻이라면,\n그대로 받아들이겠습니다.",),
    (6, 3770): ("어떤 교섭을 하시겠습니까?",),
    (6, 3771): ("상대", "에게 원군 파견을 요청합니다."),
    (6, 3772): ("상대", "에게 정전 중재를 부탁합니다."),
    (6, 3773): ("와", "의 맹약은,\n이제 쓸모가 없군요."),
    (6, 3774): ("상대", "을 종속시키도록 합시다."),
    (6, 3775): ("상대", "에게 잠시 신종하고,\n때를 기다립시다."),
    (6, 3776): ("상대", "와 관계를 맺는 겁니까?\n훌륭한 생각입니다."),
    (6, 3777): ("상대", "에게 성의 방어를 맡깁시다."),
    (6, 3780): ("그렇다면 동맹 제안을 받아들이겠소.\n당분간 우리는 동맹이오.\n그 후의 일은 그때 가서 생각하면 되오.",),
    (6, 3781): ("동맹 제안을 받아들였습니다.\n당분간 손을 잡도록 하지요.\n그 후의 일은 그때 가서 생각합시다.",),
    (6, 3782): ("맹약을 받아들이겠소.\n당분간 함께 손잡고 나아갑시다.\n그 후의 일은 그때 가서 말이지요.",),
    (6, 3786): ("동맹 제안을 받아들입니다.\n당분간 손을 잡도록 하지요.\n그 후의 일은 그때 가서 말이지요.",),
    (6, 3790): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3791): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3792): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3793): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3794): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3795): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3796): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3797): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3798): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3799): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3800): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3801): ("알겠습니다.\n", "의", "일은 제가 맡겠습니다."),
    (6, 3802): ("자세한 사정은 알겠습니다.\n상대", "와 본가의 정전에 관해,\n본가가 중재 역할을 맡겠습니다."),
    (6, 3805): ("혼인 제안을 받아들이겠소.\n두 가문이 오래도록 화목하게 지냅시다.",),
    (6, 3806): ("혼인 제안을 받아들이겠소.\n이제부터는 친척이니,\n두 가문이 화목하게 난세를 헤쳐 나갑시다.",),
    (6, 3807): ("혼인 제안을 기쁘게 받아들이겠소.\n이 인연이 두 가문을 오래도록 이어 주기를.",),
    (6, 3811): ("혼인 제안을 받아들이겠습니다.\n이제 우리는 한 가족입니다.\n무슨 일이 있으면 서로 도우며 살아갑시다.",),
    (6, 3817): ("가문을 지키기 위한 결단이오.\n부끄러워할 일은 없소……",),
    (6, 3818): ("이 또한 가문을 지키기 위한 일……\n부디 잘 부탁드리오……",),
    (6, 3819): ("이 또한 가문을 지키기 위한 일이오……\n부디 잘 부탁드리오.",),
    (6, 3823): ("이 또한 가문을 지키기 위한 일입니다……\n부디 잘 부탁드립니다……",),
    (6, 3827): ("본가의 뜻을 따르라는 말씀,\n의뢰인은 어떻게든 물리치겠습니다.",),
    (6, 3828): ("난세이기에 더욱,\n신의 없는 자는 살아남을 수 없음을 알아라!",),
    (6, 3831): ("이럴 수가…… 우리와 손을 끊다니 어리석군.",),
    (6, 3832): ("말도 안 됩니다!\n우리와 손을 끊겠다는 겁니까!",),
    (6, 3833): ("뭐라고…… 우리와 손을 끊겠다는 건가?",),
    (6, 3837): ("이렇게 갑자기 손을 끊다니……!",),
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
    if selected[0] != (6, 3698, 0) or selected[-1] != (6, 3837, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 79:
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
_engine.LAST_COORDINATE = (6, 3837, 0)
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
