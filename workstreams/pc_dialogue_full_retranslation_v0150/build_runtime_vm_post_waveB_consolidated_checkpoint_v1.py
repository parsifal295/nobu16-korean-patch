#!/usr/bin/env python3
"""Build the official post-WaveB dialogue checkpoint.

This wrapper reuses the frozen post-WaveA checkpoint engine while rebinding
it to the independently closed WaveB union.  Dialogue-bearing outputs stay
below ``tmp/``; the tracked checkpoint report is source-free.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import types


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (parent / "workstreams" / "pc_dialogue_full_retranslation_v0150").is_dir()
)
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
BASE_BUILDER = (
    DIALOGUE / "build_runtime_vm_post_waveA_consolidated_checkpoint_v1.py"
)
EXPECTED_BASE_BUILDER_SHA256 = (
    "94E3E95FDB06824A4ADEF64CEAEB9E2A8026691FFC25428EB70CF35EC2437590"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


if sha256_file(BASE_BUILDER) != EXPECTED_BASE_BUILDER_SHA256:
    raise ValueError("frozen post-WaveA checkpoint engine drift")

source = BASE_BUILDER.read_text(encoding="utf-8")
source = (
    source.replace("post_waveA", "post_waveB")
    .replace("WaveA", "WaveB")
    .replace("waveA", "waveB")
)

engine = types.ModuleType("post_waveB_checkpoint_frozen_engine")
engine.__file__ = str(SCRIPT)
engine.__name__ = "post_waveB_checkpoint_frozen_engine"
sys.modules[engine.__name__] = engine
exec(compile(source, str(BASE_BUILDER), "exec"), engine.__dict__)

engine.PREDECESSOR = (
    TMP / "runtime_vm_integrated.post_waveA_consolidated_checkpoint.private.v1.jsonl"
)
engine.UNION_BUILDER = (
    AUDIT / "build_pk_msggame_waveB_consolidated_closure_v1.py"
)
engine.UNION_DECISIONS = (
    TMP / "pk_msggame_waveB_union_decisions.private.v1.jsonl"
)
engine.UNION_EVIDENCE = TMP / "pk_msggame_waveB_union_evidence.private.v1.json"
engine.UNION_CANDIDATE = TMP / "pk_msggame_waveB_union_candidate.private.v1.bin"
engine.UNION_PUBLIC = (
    AUDIT
    / "public"
    / "pk_msggame_waveB_consolidated_closure.source_free.v1.json"
)
engine.DEFAULT_PRIVATE = (
    TMP / "runtime_vm_integrated.post_waveB_consolidated_checkpoint.private.v1.jsonl"
)
engine.DEFAULT_PUBLIC = (
    DIALOGUE
    / "runtime_vm_integration.post_waveB_consolidated_checkpoint.source_free.v1.json"
)
engine.EXPECTED_PREDECESSOR_SHA256 = (
    "F7B2AA9642E6FDC80920B091991C41F7EC08590E5DE778326EB72E3C8BA67E1A"
)
engine.EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "A2811CA8B9A53C84678727737FDA1729520FB4AB16F19AAB537C51292D1EEE78"
)
engine.EXPECTED_INPUT_SHA256 = {
    "predecessor":
        "F7B2AA9642E6FDC80920B091991C41F7EC08590E5DE778326EB72E3C8BA67E1A",
    "union_builder":
        "D17D3C6078CC4FDDC16E37DBF2523F139B165C84E5E3E16E2F1ADE0AC2D61B26",
    "union_decisions":
        "FC0EDD1AF8F4EA67E98C16724526503BA1DCED18D69347DC9DFB1E74DF931E44",
    "union_evidence":
        "E0991999F909AC7630C510118241D204385ABBD08B096E31BF0EB58DB9783430",
    "union_candidate":
        "8EB28B349E704643B633CAF69640F4BAA1BC90B4E3F3505035069B9301C6008B",
    "union_public":
        "8A4856502B3743CB72E716BC40CDE1DA14F8AEC1A23842AAD7FB0AFD3D2B4267",
    "engine_builder":
        "CF32112EB7B0BA578DF9EF2E9D2A5C92818E25AC2217FE867BE7968F92D8372E",
    "shadow_current":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
}
engine.EXPECTED_OUTPUT_SHA256 = {
    "private": "C0E4F1CEEE7FA2C62DB58DD53BEE926F1AD30DFF25F50F05DC41E924439A9243",
    "public": "7E86117D0F63F22B2CEB0A337412483511E797110B19CB151EDD57BE7401CBD1",
}


if __name__ == "__main__":
    raise SystemExit(engine.main())
