#!/usr/bin/env python3
"""Build the exact PK bound-terminal caller closure above 7777aa7.

The predecessor is the independently reproducible
``pk_bound_terminal_family_exact_closure`` layer, not an unfrozen shared
integration file.  This layer applies the complete 261-coordinate caller
repair, renews every affected pre-existing verified row, and promotes only
the 41 manually approved rows.  Public reports contain no dialogue bodies;
private decision/evidence deltas remain below ``tmp``.  Steam is read only.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import importlib.util
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PREDECESSOR_BUILDER_PATH = (
    WORKSTREAM / "build_pk_bound_terminal_family_exact_closure_v1.py"
)
DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_caller_full_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_caller_full_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_bound_terminal_caller_full_closure_integrated_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_bound_terminal_caller_full_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-caller-full-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-caller-full-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-caller-full-closure-evidence-row.v1"
)
METHOD = "reversed_vm_pk_bound_terminal_caller_full_closure_analysis"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER_PATH,
    "pk_bound_terminal_family_exact_closure_predecessor_v1",
)
HONORIFIC = PREDECESSOR.HONORIFIC
CROSS = PREDECESSOR.CROSS
BASE_AUDIT = PREDECESSOR.BASE_AUDIT
ENGINE = PREDECESSOR.ENGINE

LIVE_STEAM_BASE = PREDECESSOR.LIVE_STEAM_BASE
LIVE_STEAM_PK = PREDECESSOR.LIVE_STEAM_PK
PREDECESSOR_PUBLIC_PATHS = (
    PREDECESSOR.DEFAULT_AUDIT_OUTPUT,
    PREDECESSOR.DEFAULT_PROMOTION_OUTPUT,
)
PREDECESSOR_PRIVATE_PATHS = (
    PREDECESSOR.DEFAULT_DECISION_OUTPUT,
    PREDECESSOR.DEFAULT_EVIDENCE_OUTPUT,
)

EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING_ROWS = 8_641
EXPECTED_PREDECESSOR_PK_CANDIDATE_SHA256 = (
    "902CD3A1372BC19ABCA846C6A9F43195085C0782994ECFCE8A8353B2F9E0A628"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "306A95F90E98A1DDF4BF5BE010CB213B169E8F72B05A8D7828F3512C1143908B"
)
EXPECTED_OVERRIDE_ROWS = 261
EXPECTED_OVERRIDE_RECORDS = 150
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "C55E31E551208FEA5EF6FA3B0F95B52024AA5AC6A2155C38818DD29080883D0E"
)
EXPECTED_OVERRIDE_MAP_COMPACT_JSON_SHA256 = (
    "BAA8980704D1B1F090F81D43722BB10FBF077445FF97F9258878315ADBA671B8"
)
EXPECTED_OVERRIDE_RECORD_SHA256 = (
    "0639B879A4BF3BBD68376046A475EB5BEBA3324FF85CFC3D5F16B9EA5C609528"
)
EXPECTED_AFFECTED_RECORDS = 204
EXPECTED_AFFECTED_RECORD_SHA256 = (
    "3AA704B42027ABA8BD2D7DB5BF1D66A6E9320F1C56A6CC9189A38C167FAC0011"
)
EXPECTED_AFFECTED_PENDING_ROWS = 321
EXPECTED_AFFECTED_PENDING_ROOTS = 130
EXPECTED_AFFECTED_PENDING_COORDINATE_SHA256 = (
    "41DADF264235EB02E2F61A51A9846A1DC32313F7DC5DE915E968293FCA715CB6"
)
EXPECTED_AFFECTED_PENDING_ROOT_SHA256 = (
    "98423C83E20DBE95F49CB5552426E30A30023AA7601E37157F24E73E203C99A6"
)
EXPECTED_VERIFIED_RENEWAL_ROWS = 120
EXPECTED_VERIFIED_RENEWAL_ROOTS = 56
EXPECTED_VERIFIED_RENEWAL_COORDINATE_SHA256 = (
    "37B23A707D5049924CF7585A9144C18FDB61B172ABE858ABB5224076F44BB45E"
)
EXPECTED_VERIFIED_RENEWAL_ROOT_SHA256 = (
    "66BF312A98DF1066B3CB6A498C0BD37F9968476A465422E590B07D355D150B96"
)
EXPECTED_MACHINE_ELIGIBLE_ROWS = 42
EXPECTED_MACHINE_ELIGIBLE_ROOTS = 24
EXPECTED_MACHINE_ELIGIBLE_COORDINATE_SHA256 = (
    "5D2839727FBD5622CC639A130916800888EC3F26B7670E404DC04B61F4079CF0"
)
EXPECTED_MACHINE_ELIGIBLE_ROOT_SHA256 = (
    "8D28691FB9DDB035DA7356FCCF26255F32BB3B683BC571F9A218E5C666B7E2F9"
)
EXPECTED_ELIGIBLE_ROWS = 41
EXPECTED_ELIGIBLE_ROOTS = 23
EXPECTED_ELIGIBLE_COORDINATE_SHA256 = (
    "FD8D45E6B7193A2C6832D57A024FA693CEAA7F2A95825B7000CCA5B623A028C7"
)
EXPECTED_ELIGIBLE_ROOT_SHA256 = (
    "53149C3F973A4F19A20401C0D236A0A31508212A12C29F073FEF7A7A47B8DDD1"
)
EXPECTED_REJECTED_ROWS = 280
EXPECTED_REJECTED_ROOTS = 107
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "43B2B3B2F04A38AFFE5CD06A679C99BAD7EA15B223F4F22EFAA90E86CAAF6E86"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "6D62CC7CF7BAE833D9B48B40B90894F6E73CB9E9994F435DAC15F61F6EA58583"
)
EXPECTED_PENDING_AFTER = 8_600
EXPECTED_LEDGER_OVERRIDE_ROWS = 257
EXPECTED_UNTRACKED_LITERAL_OVERRIDE_ROWS = 4
EXPECTED_DECISION_DELTA_ROWS = 313
EXPECTED_EVIDENCE_ROWS = 313
EXPECTED_RISK_REPAIRS = 152
EXPECTED_CALL_SITES = {1090: 96, 1198: 46}
EXPECTED_CALL_SITE_SHA256 = {
    1090: "DA165DF96B4DEACE4F8FCE97B30FCEA456B81C1866B47D69397AAB12F66621FB",
    1198: "5F5737A990013C5019F7EBF83DC6826711A389FAF9C9B9F285D71F9F20F5362F",
}
EXPECTED_ASSEMBLY_COMBINATIONS = 994
EXPECTED_ASSEMBLY_HASH_MANIFEST_SHA256 = (
    "0B0A9FD6DB8FC102D6871D7E5A520A7F1AB0A623EC504BCA369928D9DDC7850A"
)
EXPECTED_AUDIT_FILE_SHA256 = (
    "E666495EC34DE65AD40C3846D73A37784EC734514B6ECEBBE4B96BCE43D9F3C6"
)
EXPECTED_PROMOTION_FILE_SHA256 = (
    "B92C8099CFB6CC3AEE1C7BD09D1940F0CD53380749A43AC01F39BF20E9925E33"
)
EXPECTED_DECISION_FILE_SHA256 = (
    "5AD71717E0C92EA895C8589678D72ED665096B9D9A655CE9739301C11E230CBB"
)
EXPECTED_EVIDENCE_FILE_SHA256 = (
    "7B26CF5464079A3AE6CCC8B2321DBFBE1F74F97A4293E6A45B887BB0CD66A089"
)
PRIOR_MULTILINGUAL_ASSEMBLY_CONTEXT_SHA256 = (
    "7F06E9B0A8F50C678E70DE92E17C728CA75D6137BA4568F7E925D3A267C2263E"
)
PRIOR_FULL_ASSEMBLY_ANALYSIS_SHA256 = (
    "62F8F09EFEBD26E062CB78FE5BA835670646C54D849C022FF62A8477690D4829"
)

FAMILY_TARGETS = {
    "predicate_hao_hada_2574_2580": {
        (0, record_id) for record_id in range(2574, 2581)
    },
    "benefactive_jusin_jun_2672_2678": {
        (0, record_id) for record_id in range(2672, 2679)
    },
}
FAMILY_SELECTORS = {
    "predicate_hao_hada_2574_2580": 1090,
    "benefactive_jusin_jun_2672_2678": 1198,
}
ACTUAL_ELIGIBLE_ROOTS = (
    {(0, record_id) for record_id in range(2574, 2581)}
    | {(6, 4445), (6, 4666)}
    | {
        (15, 1560),
        (15, 1562),
        (15, 2565),
        (15, 2567),
        (15, 2569),
    }
    | {(0, record_id) for record_id in range(2672, 2679)}
    | {(6, 4893), (6, 4902)}
)
MANUAL_REJECT_REASONS = {
    (6, 3941): "plain_dictionary_form_interrogative_register_not_approved",
}

# Exact escaped map.  This is deliberately source-owned: no compressed blob,
# generated sidecar, shared integration file, or network artifact is required.
TRANSLATION_OVERRIDES = {
    "0:2574:0": "\uc624",
    "0:2575:0": "\ub2e4",
    "0:2576:0": "\uc624",
    "0:2577:0": "\uc624",
    "0:2578:0": "\uc624",
    "0:2579:0": "\uc624",
    "0:2580:0": "\ub2e4",
    "0:2672:0": "\uc8fc\uc2e0",
    "0:2673:0": "\uc900",
    "0:2674:0": "\uc8fc\uc2e0",
    "0:2675:0": "\uc8fc\uc2e0",
    "0:2676:0": "\uc8fc\uc2e0",
    "0:2677:0": "\uc8fc\uc2e0",
    "0:2678:0": "\uc900",
    "15:1068:1": "\n\uc218\ube44\uc5d0 \ub2e4\uc18c \uc9c0\uc7a5\uc774 \uc874\uc7ac\ud558",
    "15:1068:2": ". \uadf8\ub7ec\ud558\uc624\ub2c8\n\uacf5\uc744 \ub4e4\uc5ec \uc218\ubcf5\ud558\uace0\uc790 \ud558\uc635\ub2c8\ub2e4",
    "15:1448:1": "\uacf5\ub7b5\uc758 \uc9c0\ub984\uae38\n\uc131\uc5d0 \ubcf5\uc18d\ub41c \ub9c8\uc744\ub9c8\ub2e4 \ubd88\uc744 \uc9c8\ub7ec\n\ucd9c\ubcd1 \ubc29\ud574\ub97c \ub3c4\ubaa8\ud558",
    "15:1480:0": "\uc740(\ub294) \ud2c0\ub9bc\uc5c6\ub294 \uc778\uc7ac\uc774\ub2c8\n\uc6b0\ub9ac \uac00\ubb38\uc758 \ubc88\uc601\uc744 \uc704\ud574\uc11c\ub77c\ub3c4 \ub9de\uc544\ub4e4\uc774\uace0\uc790\n\ub2e4\uc18c \uc0ac\uc804 \uacf5\uc791\uc774 \ud544\uc694\ud558",
    "15:1480:1": "\u2026\u2026",
    "15:1560:3": "\uc131\uc758 \ubcf5\uc885\uc744 \ud655\uc778\ud558",
    "15:1562:0": "\uae30\ub098\uc774\uc758 \ubcf5\uc18d\uc744 \ud655\uc778\ud558",
    "15:1562:1": "\n\ucc9c\ud558 \ud3c9\uc815\uae4c\uc9c0 \ub0a8\uc740",
    "15:1562:4": "\uc131\uc758 \ud1b5\uce58\ub97c \ud655\uc778\ud558",
    "15:1564:0": "\uc804\uad6d \uacfc\ubc18\uc218 \uc81c\uc555\uc744 \uc644\ub8cc\ud558",
    "15:1564:1": "\n\uae30\ub098\uc774 \uc81c\ud328\uae4c\uc9c0 \ub0a8\uc740",
    "15:1564:4": "\uc131\uc758 \ud1b5\uce58\ub97c \ud655\uc778\ud558",
    "15:1565:3": "\uc131\uc758 \ud1b5\uce58\ub97c \ud655\uc778\ud558",
    "15:1567:0": "\uc804\uad6d \uacfc\ubc18\uc218 \uc81c\uc555\uc744 \uc644\ub8cc\ud558",
    "15:1567:1": "\n\uae30\ub098\uc774 \uc81c\ud328\uae4c\uc9c0 \ub0a8\uc740",
    "15:1573:3": "\uac1c\uc758 \uc131\uc744 \ud655\uc778\ud558",
    "15:1578:3": "\uac1c\uc758 \uc131\uc744 \ud655\uc778\ud558",
    "15:1611:0": "\u2026\u2026\ubcf8\uc758\uac00 \uc544\ub2c8\ub77c\uace0 \ud1a0\ub85c\ud558",
    "15:1611:1": ". \uadf8\ub7ec\ub098\n\uc774\ubc88",
    "15:1887:2": "\ub4f1\uc758 \uc6c0\uc9c1\uc784\uc744 \uacbd\uacc4\ud558",
    "15:1889:0": "\uc8fc\ubcc0\uc5d0\ub294 \uc6b0\ub9ac \uac00\ubb38\ubcf4\ub2e4 \uc18c\uaddc\ubaa8 \uc138\ub825\uc758 \uc874\uc7ac\ub97c \ud655\uc778\ud558",
    "15:1889:1": "\n\ud310\ub3c4\ub97c \ub113\ud788\ub824\uba74 \uadf8\ub7f0 \uc791\uc740 \uc138\ub825\ubd80\ud130\n\uc131\uc744 \ube7c\uc557\ub294 \uac83\uc774 \uc21c\ub9ac",
    "15:1985:1": "\uc77c \uc815\ub3c4\uc758 \ucd94\uac00 \uc18c\uc694\ub97c \uc608\uc0c1\ud558",
    "15:1985:2": ". \uadf8\ub7ec\ub2c8\n\uc7a0\uc2dc,",
    "15:2176:1": "\uc5d0\uac8c\ub3c4 \uacbd\uc704\ub97c \uc9c8\ubb38\ud558",
    "15:2176:2": "?",
    "15:2180:1": "\ub9cc\n\uadf8 \ub0b4\uc6a9\ub3c4 \uc9c8\ubb38\ud558",
    "15:2180:2": "?",
    "15:2186:0": "\ubcf4\ubb3c \uc0c1\uc778\uc758 \ub0b4\ubc29\uc744 \ubcf4\uace0\ud558",
    "15:2186:1": "\n\uc7a5\uc218\ub4e4\uc758 \ucda9\uadfc\uc744 \ud3ec\uc0c1\ud558\ub294 \ub370\n\uba85\ud488\uc744 \uc4f0\ub294 \uac83\uc774 \uc0c1\ucc45",
    "15:2187:0": "\uc77c\ud488 \uc0c1\uc778\uc758 \ub0b4\ubc29\uc744 \ubcf4\uace0\ud558",
    "15:2187:1": "\n\uc218\uc9d1\ud574\ub3c4 \uc88b\uace0, \ud558\uc0ac\ud574\ub3c4 \uc88b\uc73c\ub2c8\n",
    "15:2188:0": "\ucc3e\uc544\uc628 \uc0c1\uc778\uc774 \uc77c\ud488\uc744 \ud310\ub2e4\ub294 \uc18c\uc2dd\uc5d0\n\uc7a5\uc218\ub4e4\uc758 \uae30\ub300 \uace0\uc870\ub97c \ubcf4\uace0\ud558",
    "15:2188:1": "\n",
    "15:2218:1": "\uc5d0\uac8c\uc11c \ud53c\ud574 \ubc1c\uc0dd\uc744 \ubcf4\uace0\ud558",
    "15:2218:2": "\n\ubd80\ub514 \uacb0\ub2e8\uc744",
    "15:2472:2": "?\n\ubc31\uc131\uc758 \ub9c8\uc74c\uc744 \uc798 \uc548\ub2e4\uace0 \uc790\ubd80\ud558",
    "15:2485:2": "\uc774 \ud718\ud558 \uad00\ub9ac\ub4e4\uacfc \ud568\uaed8\n\uc601\ub0b4 \uc789\uc5ec \uc300 \uc9d5\uc218\ub97c \uc57d\uc18d\ud558",
    "15:2494:0": "\uc758 \ud328\uc804 \ub3d9\uc694\ub97c \ubcf4\uace0\ud558",
    "15:2494:1": "\n\uc124\ub4dd\uc5d0\ub294 \uc790\uc2e0 \uc788\uc73c\ub2c8,",
    "15:2497:3": "\u2026\u2026\n\uc774\ub807\uac8c \ub41c \uc774\uc0c1 \uacf5\uaca9 \uc810\ub839 \uc678\uc5d0\ub294 \ubc29\ub3c4\uac00 \uc5c6\ub2e4\uace0 \ud310\ub2e8\ud558",
    "15:2497:4": "!",
    "15:254:1": "\uc5d0\uac8c\ub3c4 \uc88b\uc740 \ubc29\uc548\uc774\ub77c \ud310\ub2e8\ud558",
    "15:2565:3": "\uc131\uc758 \ud1b5\uce58\ub97c \ud655\uc778\ud558",
    "15:2567:0": "\uae30\ub098\uc774\uc758 \uc9c0\ubc30\ub97c \ud655\uc778\ud558",
    "15:2567:1": "\n\ucc9c\ud558 \ud3c9\uc815\uae4c\uc9c0 \ub0a8\uc740",
    "15:2567:4": "\uc131\uc758 \ud1b5\uce58\ub97c \ud655\uc778\ud558",
    "15:2569:0": "\uc804\uad6d \uacfc\ubc18\uc218 \ubcf5\uc18d\uc744 \ud655\uc778\ud558",
    "15:2569:1": "\n\uae30\ub098\uc774 \uc81c\ud328\uae4c\uc9c0 \ub0a8\uc740",
    "15:2569:4": "\uc131\uc758 \ud1b5\uce58\ub97c \ud655\uc778\ud558",
    "15:2570:3": "\uc131\uc758 \ud1b5\uce58\ub97c \ud655\uc778\ud558",
    "15:2572:0": "\uc804\uad6d \uacfc\ubc18\uc218 \uc81c\uc555\uc744 \uc644\ub8cc\ud558",
    "15:2572:1": "\n\uae30\ub098\uc774 \uc81c\ud328\uae4c\uc9c0 \ub0a8\uc740",
    "15:2595:0": "\uc5d0\uac8c \ud328\ud558\ub2e4\ub2c8\u2026\u2026\n\uc774\ub807\uac8c \ub41c \uc774\uc0c1 \ud56d\ubcf5 \uc678\uc5d0\ub294 \ubc29\ub3c4\uac00 \uc5c6\ub2e4\uace0 \ud310\ub2e8\ud558",
    "15:2595:1": ".\n\uc6b0\ub9ac\uc758 \uc219\uc6d0\ub3c4 \uc5ec\uae30\uae4c\uc9c0\uad70\uc694,",
    "15:277:1": "\n\uc2dc\uac04 \uc18c\uc694\ub97c \uc608\uc0c1\ud558",
    "15:277:2": ". \uadf8\ub7ec\ub098\n\ucc29\uc2e4\ud55c \uc9c4\ud589\uc740 \uac00\ub2a5\ud558",
    "15:278:1": "\n\uc2dc\uac04 \uc18c\uc694\ub97c \uc608\uc0c1\ud558",
    "15:278:2": ". \uadf8\ub7ec\ub098\n\ucc29\uc2e4\ud55c \uc9c4\ud589\uc740 \uac00\ub2a5\ud558",
    "15:518:1": "\uc758 \ub3d9\ud5a5\uc744 \uc6b0\ub824\ud558",
    "15:518:2": "\n\uae08\ud488\uc73c\ub85c \ud658\uc2ec\uc744 \uc0ac \ub450\ub294 \uac83\uc774 \uc88b\uc744 \ub4ef\ud558\uc635\ub2c8\ub2e4",
    "15:703:2": "\ub2d8\uc758 \uac00\uc2e0\ub2e8 \ud569\ub958\ub97c \uae30\ub300\ud558",
    "15:756:2": "\uc5d0 \uc801\uc774 \uc811\uadfc \uc911\uc774\ub77c \ubcf4\uace0\ud558",
    "15:756:3": ".\n\ubb34\ub9ac\ub97c \ubb34\ub985\uc4f0\uace0\ub77c\ub3c4 \uc131\uc744 \uc9c0\ucf1c\uc57c \ud558\uc635\ub2c8\ub2e4\u2026\u2026",
    "15:763:0": "\ubbfc\uc2ec \uc77c\ubd80 \uc0c1\uc2e4\uc744 \uc608\uc0c1\ud558",
    "15:763:1": ". \uadf8\ub7ec\ub098\n",
    "2:223:2": "\uc744(\ub97c) \ubcf4\uc88c\ud558\uc5ec\n\ubc18\ub4dc\uc2dc \uc2e0\uc6a9 \ud655\ubcf4\ub97c \uc7a5\ub2f4\ud558",
    "6:1136:0": "\ubc30\ud6c4\ub97c \uae30\uc2b5\ub2f9\ud558\uba74\n\uace4\ub780\ud558",
    "6:1136:1": ". \uc774\uc5d0",
    "6:2173:0": "\uc744(\ub97c) \ud568\ub77d\ud558\uae30\ub3c4 \uc804\uc5d0 \uada4\uba78\ud558\ub2e4\ub2c8\u2026\n\uba74\ubaa9 \uc5c6\uc9c0\ub9cc \uc6d0\uad70\uc740 \uc5ec\uae30\uae4c\uc9c0\uc694\u2026\n\ub0a8\uc740 \uc2f8\uc6c0\uc758 \ubb34\uc6b4\uc744 \uae30\uc6d0\ud558",
    "6:2174:0": "\uc744(\ub97c) \ub05d\uae4c\uc9c0 \uc9c0\ud0a4\uae30\ub3c4 \uc804\uc5d0 \uada4\uba78\ud558\ub2e4\ub2c8\u2026\n\uba74\ubaa9 \uc5c6\uc9c0\ub9cc \uc6d0\uad70\uc740 \uc5ec\uae30\uae4c\uc9c0\uc694\u2026\n\ub0a8\uc740 \uc2f8\uc6c0\uc758 \ubb34\uc6b4\uc744 \uae30\uc6d0\ud558",
    "6:2175:2": "\uc9c0\ub9cc \uc6d0\uad70\uc740 \uc5ec\uae30\uae4c\uc9c0\uc694\u2026\n\ub0a8\uc740 \uc2f8\uc6c0\uc758 \ubb34\uc6b4\uc744 \uae30\uc6d0\ud558",
    "6:3515:0": "\ud6c8\uacf5 1\uc704, \uac10\uc0ac\ud788 \uc218\ub839\ud558",
    "6:3515:1": "!\n",
    "6:3657:1": "\uc744(\ub97c)\n\uc774\ub807\uac8c \ub0b4\ub824",
    "6:3657:2": "\ub2e4\ub2c8\u2026\n\uac10\uc0ac\uc758 \ub9d0\uc500\ub3c4",
    "6:3766:0": "\ub450 \uac00\ubb38 \uc0ac\uc774\uc5d0 \uad73\uac74\ud55c \uc2e0\ub8b0\ub97c \uc313\uace0\uc790\u2026\n\ud6d7\ub0a0 \ub3d9\ub9f9\uc744 \ub9fa\uaca0\ub2e4\ub294 \uc57d\uc815\uc5d0\n\ub3d9\uc758\ud574",
    "6:3766:1": "\uac00?",
    "6:3855:1": "\uc640(\uacfc)\ub294 \uc801\ub300\ud558",
    "6:3855:2": "\n\ubd80\ub514 \uac01\ubcc4\ud788 \uc870\uc2ec\ud558\uc2ed\uc2dc\uc624\u2026",
    "6:3863:0": "\ube44\uc6a9\uc774 \ubc1c\uc0dd\ud558",
    "6:3863:1": ". \uadf8\ub7ec\ub098\n",
    "6:3941:2": "\n\uc989\uc2dc \uad50\uc12d\uc744 \uac1c\uc2dc\ud558",
    "6:3941:3": "?",
    "6:3952:2": "\uc758 \uc9c0\ubc30\ud558\uc5d0 \ud3b8\uc785\ud558",
    "6:3952:3": "\n\ubd80\ub514 \uac01\ubcc4\ud788 \uc8fc\uc758\ud574 \uc8fc",
    "6:4420:4": "\ub2d8\uaed8 \ud558\uc0ac\ud558",
    "6:4420:5": "?",
    "6:4423:2": "\uac1c\uc785\ub2c8\ub2e4\n\uc0c8 \uc601\uc9c0\ub97c \ud558\uc0ac\ud558",
    "6:4423:3": "?",
    "6:4445:1": "\ub3c4\n\uac74\ucd95\uc774 \uac00\ub2a5\ud558",
    "6:4462:1": ", \ucd9c\uc804\uc744 \uac08\ub9dd\ud558",
    "6:4462:2": "\n",
    "6:4485:1": "\uc5d0\uac8c \ub9e1\uaca8",
    "6:4485:2": "\ub2e4\uba74\n\uc2e0\uc18d\ud788 \uc7a5\uc545\uc744 \uc9c4\ud589",
    "6:4561:3": "\ub3c4\uc640",
    "6:4561:4": "\uac00?",
    "6:4564:3": "\uaed8\uc11c\ub3c4 \uc124\ub4dd\ud574",
    "6:4564:4": "\uac00?",
    "6:4565:4": ", \uc124\ub4dd\ud574",
    "6:4565:5": "\uac00?",
    "6:4566:4": "\uaed8\uc11c \uc124\ub4dd\ud574",
    "6:4566:5": "\uac00?",
    "6:4577:3": "\ub3c4\uc640",
    "6:4577:4": "\uac00?",
    "6:4578:3": "\ub3c4\uc640",
    "6:4578:4": "\uac00?",
    "6:4579:0": "\uc758 \ube7c\ub0b4\uae30 \ub09c\ud56d\uc744 \ubcf4\uace0\ud558",
    "6:4579:1": "\u2026\n\uc694\uad6c\ub97c \ubc1b\uc544\ub4e4\uc774\uc9c0 \uc54a\uc73c\uba74 \uc751\ud558\uc9c0 \uc54a\uc744 \ubaa8\uc591\uc785\ub2c8\ub2e4\n",
    "6:4579:3": "\ub3c4\uc640",
    "6:4579:4": "\uac00?",
    "6:4580:4": "\ub3c4\uc640",
    "6:4580:5": "\uac00?",
    "6:4581:4": "\ub3c4\uc640",
    "6:4581:5": "\uac00?",
    "6:4585:0": "\uc5d0\uc11c \ud734\uc804 \uc0ac\uc790 \ub3c4\ucc29\uc744 \ubcf4\uace0\ud558",
    "6:4585:1": ".\n\ub354 \ub098\uc740 \uc870\uac74\ub3c4 \ub3c4\ucd9c \uac00\ub2a5\ud558",
    "6:4598:0": "\u2026?\n\ub9cc\ub098\uae30\ub85c \uc57d\uc18d\ud558\uc9c0 \uc54a\uc558\uc744 \ud150\ub370\uc694\u2026\n\uac11\uc791\uc2a4\ub7ec\uc6b4 \ubc29\ubb38\uc740 \uace4\ub780\ud558",
    "6:4599:2": "\uaed8\uc11c \ubab8\uc18c \ucc3e\uc544\uc640",
    "6:4599:3": "\ub2e4\ub2c8\u2026\n",
    "6:4606:2": "\ub3c4\uc6c0\uc744 \ubd80\ud0c1\ud558",
    "6:4606:3": ",",
    "6:4608:2": "\uc740\ud61c\uc5d0 \uac10\uc0ac\ud558",
    "6:4608:3": ",",
    "6:4624:0": "\ud734\uc804\uc744 \ub17c\uc758\ud560 \uc790\ub9ac\ub97c\n\ub9c8\ub828\ud574",
    "6:4624:1": "\ub2e4\ub2c8\u2026\n",
    "6:4651:1": "\n\uc120\ubb3c\uc744 \ubc1b\uc544",
    "6:4651:2": "\uac00?",
    "6:4652:2": "\n\uc6b0\ub9ac\uc758 \uc131\uc758\ub97c \ubc1b\uc544",
    "6:4652:3": "\uac00?",
    "6:4655:0": "\uc194\uc9c1\ud788 \ubd88\ub9cc\uc740 \uc5ec\ub7ff \uc788\uc9c0\ub9cc\n\uac11\uc791\uc2a4\ub7ec\uc6b4 \uc9c8\ubb38\uc740 \uace4\ub780\ud558",
    "6:4655:1": "\u2026",
    "6:4661:2": "\uc57d\uc18d\ud574",
    "6:4661:3": "\ub2e4\uba74\n\uadf8\uac83\uc744 \ud798\uc0bc\uc544 \ub178\ub825\ud558\uaca0\uc2b5\ub2c8",
    "6:4663:1": "\ub9cc\n\ubb34\uc5b8\uac00\ub97c \uc81c\uc2dc\ud574",
    "6:4663:2": "\ub2e4\uba74",
    "6:4664:1": "\ub9cc\n\ubb34\uc5b8\uac00\ub97c \uc81c\uc2dc\ud574",
    "6:4664:2": "\ub2e4\uba74",
    "6:4665:1": "\ub9cc\n\uc131\uacf5\ud55c \ub4a4 \ud3ec\uc0c1\uc744 \uc57d\uc18d\ud574",
    "6:4665:2": "\ub2e4\uba74\u2026",
    "6:4666:0": ", \ube60\ub978 \ud569\uc758\ub97c \ub2e4\ud589\uc774\ub77c \uc0dd\uac01\ud558",
    "6:4676:1": "\ub9cc\n\uc5b4\ub5a4 \uac83\uc744 \ub0b4\uc5b4",
    "6:4676:2": "\ub2e4\ub294 \uac83",
    "6:4690:0": "\ubc14\ub78c\uc744 \uc774\ub8e8\uc5b4",
    "6:4690:1": "\uac00\u2026",
    "6:4691:0": "\ub300\uccb4 \ubb34\uc5c7\uc744 \ub0b4\uc5b4",
    "6:4691:1": "\ub2e4\ub294 \uac83",
    "6:4696:0": "\uc870\uae08\ub9cc \ub354 \uace0\ub824\ud574",
    "6:4696:1": "\uac00",
    "6:4706:0": "\uc124\ub9c8\u2026\n\uacfc\uc5f0 \ub300\ub2e8\ud55c \ub9d0\uc500\uc774\ub77c \uac10\ud0c4\ud558",
    "6:4706:1": "!",
    "6:4707:0": "\uc774 \uc815\ub3c4\ub85c \uc6a9\uc11c\ud574 \n",
    "6:4707:1": "\uac00",
    "6:4712:0": ", \uc57d\uc810\uc744 \uc7a1\ud788\ub2e4\ub2c8\u2026\n\uae30\uac04\uc744 \uc5f0\uc7a5\ud574",
    "6:4712:1": "\ub2e4\ub294 \ub9d0\uc774",
    "6:4713:0": "\uc6b0\ub9ac\uc5d0\uac8c\ub3c4 \ubc18\uac00\uc6b4 \uc81c\uc548\uc774\ub77c \uc0dd\uac01\ud558",
    "6:4713:1": "\n\uc774\ubc88\uc5d0\ub294 \uc21c\uc21c\ud788 \ubc1b\uc544\ub4e4\uc774\uaca0\uc18c",
    "6:4725:1": "\u2026\n\uc0ac\uc815\uc744 \ub4e4\uc5b4",
    "6:4725:2": "\ub2e4\ub294 \uc810\uc740\n\uc720\uac10",
    "6:4743:1": "\ub9cc \ub2e4\ub978 \ubc29\ub3c4\ub294 \uc5c6\ub2e4\uace0 \ud310\ub2e8\ud558",
    "6:4743:2": ".\n\uc6b0\ub9ac\uc5d0\uac8c\ub3c4 \uc9c0\ucf1c\uc57c \ud560 \uc758\uc9c0\uac00 \uc788\uc2b5\ub2c8",
    "6:4746:0": "\uc81c \ubc14\ub78c\uc744 \uc774\ub8e8\uc5b4",
    "6:4746:1": "\ub2e4\ub2c8\u2026\n",
    "6:4747:1": "\n\uc774\ud1a0\ub85d \ubc30\ub824\ud574",
    "6:4747:2": "\ub2e4\uba74\n\uae30\uaebc\uc774 \ucd9c\uc0ac",
    "6:4752:0": "\uc81c \ubc14\ub78c\uc744 \ub4e4\uc5b4",
    "6:4752:1": "\ub2e4\ub2c8\u2026!\n",
    "6:4753:0": "\ud56d\ubcf5\uc744 \ubc1b\uc544",
    "6:4753:1": "\ub2e4\ub2c8\n\ub354\uc5c6\uc774 \uac10\uc0ac\ud55c \uc77c\uc785\ub2c8\ub2e4",
    "6:4754:0": "\uc774\ud1a0\ub85d \ubc30\ub824\ud574",
    "6:4754:1": "\ub2e4\ub2c8\u2026!\n\ubc18\ub4dc\uc2dc \uc601\ubbfc \uc124\ub4dd\uc744 \ub2e4\uc9d0\ud558",
    "6:4754:2": "\n",
    "6:4756:0": "\uc81c \ubc14\ub78c\uc744 \ub4e4\uc5b4",
    "6:4756:1": "\ub2e4\ub2c8!\n\uc9c0\uae08 \uc131\uc73c\ub85c \ub3cc\uc544\uac00 \ucc45\ub7b5\uc744 \ub9c8\ub828",
    "6:4757:0": "\uc774\ud1a0\ub85d \ud6c4\ud558\uac8c \ub300\uc6b0\ud574",
    "6:4757:1": "\ub2e4\ub2c8\n",
    "6:4758:0": "\uc81c \ubc14\ub78c\uc744 \ub4e4\uc5b4",
    "6:4758:1": "\ub2e4\ub2c8\u2026\n\uae30\uaebc\uc774 \ucd9c\uc0ac",
    "6:4781:1": "\uc5d0\uac8c \ubb18\ud55c \uc778\uc5f0\uc744 \ub290\ub07c\uace0 \uc788\uc5b4\n\uaf2d \uac74\ub124",
    "6:4781:2": "\ub2e4\uba74\u2026",
    "6:4790:1": "\u2026\n\ub2e4\ub9cc \uc808\uacfc \uc778\uc5f0\uc774 \uc788\ub294 \ub545\uc744 \ub9e1\uaca8",
    "6:4790:2": "\ub2e4\uba74",
    "6:4794:1": "\u300d\uc758 \uac00\ubcf4\uc5d0 \ub208\ub3c5\uc744 \ub4e4\uc774\uace0 \uc788\uc5b4\n\uaf2d \uac74\ub124",
    "6:4794:2": "\ub2e4\uba74\u2026",
    "6:4799:0": "\n\ubcd1\uc0ac\ub97c \ub0bc \uc218 \uc788\ub294 \uc601\uc9c0\ub97c \ub9e1\uaca8",
    "6:4799:1": "\ub2e4\uba74\n\ubcf8\ub839\uc744 \ubc1c\ud718",
    "6:4801:1": "\n\uadf8 \uc77c\uc744 \ub9e1\uaca8",
    "6:4801:2": "\ub2e4\uba74 \ub9e1\uae38 \ub9cc\ud55c \uc9c0\uc704\ub97c\u2026",
    "6:4816:2": "\n\uc801\uc5b4\ub3c4 \ud65c\uc57d\ud560 \uc790\ub9ac\ub97c \ub9c8\ub828\ud574",
    "6:4816:3": "\uac00",
    "6:4890:2": "\uc758 \ub545\uc744 \ub9e1\uaca8",
    "6:4890:3": "\ub2e4\ub294 \uc57d\uc18d\uc774 \uc5c6\ub2e4\uba74\u2026",
    "6:4893:0": "\uc758 \uc601\uc9c0\ub97c \ub9e1\uaca8",
    "6:4893:1": "\ub2e4\ub294\n\uadf8\ub7f0 \uc57d\uc18d\uc774\uc5c8\uc744 \ud150\ub370\uc694",
    "6:4894:0": "\uc758 \ud718\ud558\uc5d0 \ub450\uc5b4",
    "6:4894:1": "\ub2e4\ub294 \uac83\uc774 \uc57d\uc18d\uc774\uc5c8\uc744 \ud150\ub370",
    "6:4896:1": "\ub9cc\n\uc5b8\uc820\uac00 \uc57d\uc18d\uc744 \uc9c0\ucf1c",
    "6:4896:2": "\ub2e4\uba74\n\uadf8\ub54c\uae4c\uc9c0 \uc5f4\uc2ec\ud788 \ub2e4\uc2a4\ub9ac\uaca0\uc2b5\ub2c8",
    "6:4902:0": "\uc5d0 \uc784\uba85\ud574",
    "6:4902:1": "\ub2e4\ub2c8 \uacfc\ubd84\ud55c \uc601\uad11\uc785\ub2c8\ub2e4!\n\uc774\uc81c\ubd80\ud130 \uc774",
    "7:2458:0": "\uc744(\ub97c) \uc0c1\ub300\ud558\uae30\uc5d0\ub294\n\ubcd1\ub825 \ubd80\uc871\uc744 \uc6b0\ub824\ud558",
    "7:2458:1": "\n\ud798\uaca8\uc6b4 \uc2f8\uc6c0\uc774 \ub418",
    "7:2462:1": "\n\ub2e4\ub9cc \ubcd1\ub7c9 \ubd80\uc871\uc744 \uc6b0\ub824\ud558",
    "7:2462:2": ", \uc720\uc758\ud558\uc2dc\uc624",
    "7:2465:2": "\n\uac8c\ub2e4\uac00 \ubcd1\ub7c9 \ubd80\uc871\uc744 \uc6b0\ub824\ud558",
    "7:2465:3": ", \uc720\uc758\ud558\uc2dc\uc624",
    "7:2469:1": "\n\ub2e4\ub9cc \ubcd1\ub7c9 \ubd80\uc871\uc744 \uc6b0\ub824\ud558",
    "7:2469:2": ", \uc720\uc758\ud558\uc2dc\uc624",
    "7:2491:0": "\uc744(\ub97c) \uacf5\uaca9\ud558\uc2e0\ub2e4\uba74\n\uc9c1\uc9c4 \uc678\uc5d0\ub3c4 \ub300\uc548\uc774 \uc788\ub2e4\uace0 \ud310\ub2e8\ud558",
    "7:2491:1": "\n",
    "7:277:1": "\n\uc774\ub807\uac8c \ub2e4\uc2dc \ubd88\ub7ec \uc8fc\uc2e0 \uc774\uc0c1\n\ubcf5\uc885\uc744 \uacb0\uc2ec\ud558",
    "7:277:2": ".",
    "7:2830:1": "\n\uc77c\ub2e8 \uc131\uc73c\ub85c \uadc0\ud658\ud558",
    "7:2874:2": "\uc744(\ub97c) \uaca9\ud30c \ud6c4 \uadc0\ud658\ud558",
    "7:2877:0": "\uc758 \ubc29\ube44\uac00 \ud5c8\uc220\ud574\uc84c\ub2e4\uace0 \ud558\uc635\ub2c8\ub2e4\n\uc774 \uae30\ud68c\uc5d0 \uc6b0\ub9ac \uad70\ub2e8\uc758 \uc810\ub839\uc744 \ub2e4\uc9d0\ud558",
    "7:2878:1": "\uc774(\uac00) \uc6b0\ub9ac \uac00\ubb38\uc758 \uc704\ud611\uc774 \ub418\uae30 \uc804\uc5d0\n\uc6b0\ub9ac \uad70\ub2e8\uc758 \ucc98\ub2e8\uc744 \ub2e4\uc9d0\ud558",
    "7:2879:2": "\n\uc6b0\ub9ac \uad70\ub2e8\uc774 \ud1a0\ubc8c \ud6c4 \uadc0\ud658\ud558",
    "7:2880:2": "\n\uc6b0\ub9ac \uad70\ub2e8\uc774 \ud669\ucc9c\ud589\uc744 \uc7a5\ub2f4\ud558",
    "7:332:0": "\uc5d0\uac8c\ub3c4 \uae0d\uc9c0\ub97c \uc911\uc2dc\ud558",
    "7:332:1": "\n\ubc29\uae08 \uc804\uae4c\uc9c0 \uc801\uc774\ub358 \uc0c1\ub300\ub97c\n\uace7\ubc14\ub85c \uc8fc\uad70\uc73c\ub85c \ubc1b\ub4e4 \uc218\ub294 \uc5c6",
    "7:334:0": "\u2026\u2026\uadf8 \uc628\uc815\uc5d0 \uae4a\uc774 \uac10\uc0ac\ud558",
    "7:334:1": ". \uadf8\ub7ec\ub098\n\uc774\ubc88\uc5d0\ub294 \uac70\uc808\ud558\uaca0",
    "8:1028:0": "\uc801\uc758 \ud45c\uc801\uc774 \ub418\uae30 \uc26c\uc6b4 \uacf3\uc784\uc744 \uc0dd\uac01\ud558\uba74\n\ub290\uae0b\ud558\uac8c \ub0b4\uc815\uc744 \uc815\ube44\ud560 \uc5ec\uc720\uac00 \uc5c6\ub2e4\uace0 \ud310\ub2e8\ud558",
    "8:1028:1": ".\n\uc790, \uc5b4\ub5a4 \ubc29\uce68\uc73c\ub85c \uc784\ud558",
    "8:1040:2": "\uc5d0\n\ub300\ucc98 \ud6c4 \uadc0\ud658\ud558",
    "8:1107:1": "\n\uc774 \ub610\ud55c \uad6c\ub9c8\ub178 \uc7ac\ud765\uc758 \ub355\uc774\ub77c \ud310\ub2e8\ud558",
    "8:274:1": "\uac1c \uad70\uc5d0\uc11c\n\uc5f0\uacf5\ubbf8\uac00 \uac10\uc18c\ud558",
    "8:274:2": ", \ub17c\uc758 \ud669\ud3d0\ud654\ub294 \uc5b5\uc81c\ub418\uc5b4\n\ubbfc\ucda9\ub3c4 \uadf8\ub2e4\uc9c0 \ub5a8\uc5b4\uc9c0\uc9c0 \uc54a\uc744 \uc804\ub9dd",
    "8:275:1": "\uac1c \uad70\uc5d0\uc11c\n\uc5f0\uacf5\ubbf8\uac00 \uac10\uc18c\ud558",
    "8:275:2": ", \ub17c\uc758 \ud669\ud3d0\ud654\ub294 \uc5b5\uc81c\ub418\uc5b4\n\ubbfc\ucda9\ub3c4 \uadf8\ub2e4\uc9c0 \ub5a8\uc5b4\uc9c0\uc9c0 \uc54a\uc744 \uc804\ub9dd",
    "8:276:1": "\uac1c \uad70\uc5d0\uc11c\n\uc5f0\uacf5\ubbf8\uac00 \uac10\uc18c\ud558",
    "8:276:2": ", \ub17c\uc758 \ud669\ud3d0\ud654\ub294 \uc5b5\uc81c\ub418\uc5b4\n\ubbfc\ucda9\ub3c4 \uadf8\ub2e4\uc9c0 \ub5a8\uc5b4\uc9c0\uc9c0 \uc54a\uc744 \uc804\ub9dd",
    "8:277:1": "\uac1c \uad70\uc5d0\uc11c\n\uc5f0\uacf5\ubbf8\uac00 \uac10\uc18c\ud558",
    "8:277:2": ", \ub17c\uc758 \ud669\ud3d0\ud654\ub294 \uc5b5\uc81c\ub418\uc5b4\n\ubbfc\ucda9\ub3c4 \uadf8\ub2e4\uc9c0 \ub5a8\uc5b4\uc9c0\uc9c0 \uc54a\uc744 \uc804\ub9dd",
    "8:278:1": "\uac1c \uad70\uc5d0\uc11c\n\uc5f0\uacf5\ubbf8\uac00 \uac10\uc18c\ud558",
    "8:278:2": ", \ub17c\uc758 \ud669\ud3d0\ud654\ub294 \uc5b5\uc81c\ub418\uc5b4\n\ubbfc\ucda9\ub3c4 \uadf8\ub2e4\uc9c0 \ub5a8\uc5b4\uc9c0\uc9c0 \uc54a\uc744 \uc804\ub9dd",
    "8:332:1": "\uac1c\ub85c,\n\ucde8\ub77d\uc774 \uc77c\uc2dc\uc801\uc73c\ub85c \uae30\ub2a5\uc744 \uc783\uc5b4\n\uc0c1\ud669\uc774 \uc2ec\uac01\ud558",
    "8:333:1": "\uac1c\ub85c,\n\ucde8\ub77d\uc774 \uc77c\uc2dc\uc801\uc73c\ub85c \uae30\ub2a5\uc744 \uc783\uc5b4\n\uc0c1\ud669\uc774 \uc2ec\uac01\ud558",
    "8:334:1": "\uac1c\ub85c,\n\ucde8\ub77d\uc774 \uc77c\uc2dc\uc801\uc73c\ub85c \uae30\ub2a5\uc744 \uc783\uc5b4\n\uc0c1\ud669\uc774 \uc2ec\uac01\ud558",
    "8:335:1": "\uac1c\ub85c,\n\ucde8\ub77d\uc774 \uc77c\uc2dc\uc801\uc73c\ub85c \uae30\ub2a5\uc744 \uc783\uc5b4\n\uc0c1\ud669\uc774 \uc2ec\uac01\ud558",
    "8:336:1": "\uac1c\ub85c,\n\ucde8\ub77d\uc774 \uc77c\uc2dc\uc801\uc73c\ub85c \uae30\ub2a5\uc744 \uc783\uc5b4\n\uc0c1\ud669\uc774 \uc2ec\uac01\ud558",
    "9:1828:0": "\n\ubb34\uc6b4\uc744 \uae30\uc6d0\ud558",
    "9:1828:1": "\u2026\u2026",
    "9:1830:0": "\ubb34\uc0ac \uadc0\ud658\uc744 \uae30\uc6d0\ud558",
    "9:1830:1": "\u2026\u2026",
    "9:4146:2": "\uc758 \ud718\ud558 \uc7a5\uc218\ub4e4\uc774 \ud544\uc694\ud558\ub2e4\uace0 \ud310\ub2e8\ud558",
    "9:4146:3": "\u2026\n\uc790, \ub3cc\uc544\uac00 \uc791\ubcc4\uc758 \ubb3c\uc794\uc774\ub77c\ub3c4 \ub098\ub204\uac70\ub77c",
}

EXPECTED_UNTRACKED_LITERAL_OVERRIDES = {
    "6:4462:2",
    "6:4754:2",
    "7:2491:1",
    "15:2188:1",
}
CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    return HONORIFIC.canonical_sha256(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return HONORIFIC.canonical_json(value)


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return HONORIFIC.canonical_jsonl(rows)


def coordinate_digest(values: Iterable[str]) -> str:
    return HONORIFIC.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return HONORIFIC.record_digest(values)


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return HONORIFIC.row_sort_key(row)


def parse_coordinate(coordinate: str) -> tuple[int, int, int]:
    return BASE_AUDIT.parse_literal_coordinate(coordinate)


def member_coordinates(
    roots: Iterable[tuple[int, int]],
    by_root: Mapping[tuple[int, int], Sequence[str]],
) -> list[str]:
    return [
        coordinate
        for root in sorted(roots)
        for coordinate in by_root[root]
    ]


def digest_summary(
    roots: set[tuple[int, int]],
    by_root: Mapping[tuple[int, int], Sequence[str]],
) -> dict[str, Any]:
    coordinates = member_coordinates(roots, by_root)
    return {
        "rows": len(coordinates),
        "roots": len(roots),
        "coordinate_sha256": coordinate_digest(coordinates),
        "record_sha256": record_digest(roots),
    }


def load_predecessor() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = PREDECESSOR.build_outputs()
    PREDECESSOR.validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    expected_files = {
        PREDECESSOR.DEFAULT_AUDIT_OUTPUT: audit_content,
        PREDECESSOR.DEFAULT_PROMOTION_OUTPUT: promotion_content,
        PREDECESSOR.DEFAULT_DECISION_OUTPUT: decision_content,
        PREDECESSOR.DEFAULT_EVIDENCE_OUTPUT: evidence_content,
    }
    for path, expected_content in expected_files.items():
        require(path.is_file(), f"predecessor output missing: {path}")
        require(
            path.read_text(encoding="utf-8") == expected_content,
            f"predecessor output drifted: {path}",
        )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["checkpoint_rows"].items()
    }
    for row in bundle["updated_rows"]:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(key in merged, f"predecessor delta outside ledger: {key}")
        merged[key] = copy.deepcopy(dict(row))
    pending = [
        coordinate
        for (_, coordinate), row in merged.items()
        if row.get("runtime_review") == "pending"
    ]
    require(
        len(merged) == EXPECTED_PREDECESSOR_ROWS
        and len(pending) == EXPECTED_PREDECESSOR_PENDING_ROWS,
        "direct predecessor ledger drifted",
    )
    bindings = {
        "predecessor_builder_sha256": sha256_file(
            PREDECESSOR_BUILDER_PATH
        ),
        "predecessor_audit_file_sha256": sha256_file(
            PREDECESSOR.DEFAULT_AUDIT_OUTPUT
        ),
        "predecessor_promotion_file_sha256": sha256_file(
            PREDECESSOR.DEFAULT_PROMOTION_OUTPUT
        ),
        "predecessor_decision_delta_file_sha256": sha256_file(
            PREDECESSOR.DEFAULT_DECISION_OUTPUT
        ),
        "predecessor_evidence_file_sha256": sha256_file(
            PREDECESSOR.DEFAULT_EVIDENCE_OUTPUT
        ),
        "ghidra_vm_contract_file_sha256": audit["guards"][
            "ghidra_vm_contract_file_sha256"
        ],
        "ghidra_layout_contract_file_sha256": audit["guards"][
            "ghidra_layout_contract_file_sha256"
        ],
    }
    return merged, bindings


def build_candidate(
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[
    bytes,
    dict[tuple[int, int], Any],
    bytes,
    dict[tuple[int, int], Any],
]:
    predecessor_replacements: dict[tuple[int, int, int], str] = {}
    for (resource, coordinate), row in predecessor_rows.items():
        if resource != "pk_msggame" or not isinstance(
            row.get("translation"), str
        ):
            continue
        predecessor_replacements[parse_coordinate(coordinate)] = str(
            row["translation"]
        )
    predecessor_blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        predecessor_replacements,
    )
    predecessor_records = BASE_AUDIT.records_from_blob(predecessor_blob)
    candidate_replacements = dict(predecessor_replacements)
    candidate_replacements.update(
        {
            parse_coordinate(coordinate): text
            for coordinate, text in TRANSLATION_OVERRIDES.items()
        }
    )
    candidate_blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        candidate_replacements,
    )
    candidate_records = BASE_AUDIT.records_from_blob(candidate_blob)
    require(
        sha256_bytes(predecessor_blob)
        == EXPECTED_PREDECESSOR_PK_CANDIDATE_SHA256
        and sha256_bytes(candidate_blob) == EXPECTED_PK_CANDIDATE_SHA256,
        "direct predecessor/candidate packed hash drifted",
    )
    return (
        predecessor_blob,
        predecessor_records,
        candidate_blob,
        candidate_records,
    )


def call_sites(
    records: Mapping[tuple[int, int], Any],
    selector: int,
) -> tuple[str, ...]:
    return tuple(
        f"{root[0]}:{root[1]}:{gap_id}:{match.start()}"
        for root in sorted(records)
        for gap_id, gap in enumerate(
            BASE_AUDIT.literal_gaps(records[root])
        )
        for match in CALL_RE.finditer(gap)
        if struct.unpack("<I", match.group(1))[0] == selector
    )


def adjacent_literals(
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> tuple[str, str]:
    block_id, record_id, gap_id, _ = map(int, site.split(":"))
    literals = BASE_AUDIT.parse_record_literals(
        records[(block_id, record_id)]
    )
    return (
        literals[gap_id - 1].text if gap_id else "",
        literals[gap_id].text if gap_id < len(literals) else "",
    )


def assembly_manifest(
    candidate_records: Mapping[tuple[int, int], Any],
) -> tuple[list[list[Any]], dict[int, dict[str, Any]]]:
    manifest: list[list[Any]] = []
    selectors: dict[int, dict[str, Any]] = {}
    for family, selector in FAMILY_SELECTORS.items():
        sites = call_sites(candidate_records, selector)
        site_sha256 = sha256_bytes("\n".join(sites).encode("ascii"))
        require(
            len(sites) == EXPECTED_CALL_SITES[selector]
            and site_sha256 == EXPECTED_CALL_SITE_SHA256[selector],
            f"selector caller universe drifted: {selector}",
        )
        selectors[selector] = {
            "family": family,
            "call_sites": len(sites),
            "call_site_sha256": site_sha256,
        }
        for site in sites:
            left, right = adjacent_literals(candidate_records, site)
            for terminal in sorted(FAMILY_TARGETS[family]):
                ending = BASE_AUDIT.parse_record_literals(
                    candidate_records[terminal]
                )[0].text
                manifest.append(
                    [
                        site,
                        terminal[1],
                        ENGINE.sha256_text(left + ending + right),
                    ]
                )
    require(
        len(manifest) == EXPECTED_ASSEMBLY_COMBINATIONS
        and canonical_sha256(manifest)
        == EXPECTED_ASSEMBLY_HASH_MANIFEST_SHA256,
        "full caller branch assembly manifest drifted",
    )
    return manifest, selectors


def target_delta_manifest(
    *,
    predecessor_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for coordinate in sorted(
        TRANSLATION_OVERRIDES,
        key=parse_coordinate,
    ):
        parsed = parse_coordinate(coordinate)
        root = parsed[:2]
        predecessor = predecessor_records[root]
        candidate = candidate_records[root]
        require(
            HONORIFIC.component_signatures(predecessor)
            == HONORIFIC.component_signatures(candidate),
            f"override changed control signature: {coordinate}",
        )
        predecessor_literals = BASE_AUDIT.parse_record_literals(
            predecessor
        )
        candidate_literals = BASE_AUDIT.parse_record_literals(candidate)
        require(
            candidate_literals[parsed[2]].text
            == TRANSLATION_OVERRIDES[coordinate],
            f"candidate literal mismatch: {coordinate}",
        )
        manifest.append(
            {
                "coordinate": coordinate,
                "record": list(root),
                "predecessor_record_sha256": sha256_bytes(
                    predecessor.data
                ),
                "candidate_record_sha256": sha256_bytes(candidate.data),
                "predecessor_literal_utf16le_sha256": ENGINE.sha256_text(
                    predecessor_literals[parsed[2]].text
                ),
                "candidate_literal_utf16le_sha256": ENGINE.sha256_text(
                    candidate_literals[parsed[2]].text
                ),
            }
        )
    return manifest


def repaired_pk_decisions(
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[
    dict[tuple[int, int], list[dict[str, Any]]],
    dict[str, dict[str, Any]],
    int,
]:
    by_root: defaultdict[tuple[int, int], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    by_coordinate: dict[str, dict[str, Any]] = {}
    repaired_risks = 0
    for (resource, coordinate), predecessor in predecessor_rows.items():
        if resource != "pk_msggame":
            continue
        row = copy.deepcopy(dict(predecessor))
        if coordinate in TRANSLATION_OVERRIDES:
            row["translation"] = TRANSLATION_OVERRIDES[coordinate]
            repaired_risks += PREDECESSOR.repair_hard_risks(row)
            row["bound_terminal_caller_override_evidence"] = {
                "schema":
                "nobu16.kr.pk-bound-terminal-caller-exact-override.v1",
                "exact_source_owned_override": True,
                "translation_utf16le_sha256": ENGINE.sha256_text(
                    str(row["translation"])
                ),
                "control_bytes_preserved": True,
                "automatic_space_inserted": False,
            }
        root = parse_coordinate(coordinate)[:2]
        by_root[root].append(row)
        by_coordinate[coordinate] = row
    require(
        repaired_risks == EXPECTED_RISK_REPAIRS,
        "override hard-risk repair count drifted",
    )
    return dict(by_root), by_coordinate, repaired_risks


def build_analysis(
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    compact_map = json.dumps(
        TRANSLATION_OVERRIDES,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    targets = {
        parse_coordinate(coordinate)[:2]
        for coordinate in TRANSLATION_OVERRIDES
    }
    ledger_override_coordinates = {
        coordinate
        for coordinate in TRANSLATION_OVERRIDES
        if ("pk_msggame", coordinate) in predecessor_rows
    }
    untracked_literal_overrides = (
        set(TRANSLATION_OVERRIDES) - ledger_override_coordinates
    )
    require(
        len(TRANSLATION_OVERRIDES) == EXPECTED_OVERRIDE_ROWS
        and len(targets) == EXPECTED_OVERRIDE_RECORDS
        and coordinate_digest(TRANSLATION_OVERRIDES)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and sha256_bytes(compact_map)
        == EXPECTED_OVERRIDE_MAP_COMPACT_JSON_SHA256
        and record_digest(targets) == EXPECTED_OVERRIDE_RECORD_SHA256
        and len(ledger_override_coordinates)
        == EXPECTED_LEDGER_OVERRIDE_ROWS
        and len(untracked_literal_overrides)
        == EXPECTED_UNTRACKED_LITERAL_OVERRIDE_ROWS
        and untracked_literal_overrides
        == EXPECTED_UNTRACKED_LITERAL_OVERRIDES,
        "exact 261-coordinate source map drifted",
    )
    (
        predecessor_blob,
        predecessor_records,
        candidate_blob,
        candidate_records,
    ) = build_candidate(predecessor_rows)
    changed = HONORIFIC.changed_record_guard(
        predecessor_records=predecessor_records,
        candidate_records=candidate_records,
        expected_changed=targets,
    )
    target_delta = target_delta_manifest(
        predecessor_records=predecessor_records,
        candidate_records=candidate_records,
    )
    target_delta_sha256 = canonical_sha256(target_delta)
    assembly, selector_summary = assembly_manifest(candidate_records)
    source_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_PRISTINE
    )[0]
    current_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_CURRENT
    )[0]
    candidate_inputs = dataclasses.make_dataclass(
        "BoundTerminalCallerCandidateInputs",
        [
            ("pk_source_records", object),
            ("pk_current_records", object),
            ("pk_candidate_records", object),
        ],
    )(source_records, current_records, candidate_records)
    profiles, candidate_edges = (
        CROSS.RESIDUAL_AUDIT.build_record_profiles(
            inputs=candidate_inputs
        )
    )
    source_edges = HONORIFIC.graph_edges(
        source_records,
        conservative_operand_scan=True,
    )
    candidate_affected = HONORIFIC.reverse_ancestors(
        edges=candidate_edges,
        targets=tuple(targets),
    )
    source_affected = HONORIFIC.reverse_ancestors(
        edges=source_edges,
        targets=tuple(targets),
    )
    affected = candidate_affected | source_affected
    require(
        candidate_affected <= source_affected
        and len(affected) == EXPECTED_AFFECTED_RECORDS
        and record_digest(affected) == EXPECTED_AFFECTED_RECORD_SHA256,
        "source/candidate affected record universe drifted",
    )
    root_proofs = HONORIFIC.root_delta_proofs(
        resource="pk_msggame",
        affected_records=affected,
        edges=source_edges,
        target_records=targets,
        predecessor_records=predecessor_records,
        candidate_records=candidate_records,
        target_delta_sha256=target_delta_sha256,
    )
    root_proof_manifest_sha256 = canonical_sha256(
        {
            f"{root[0]}:{root[1]}": proof
            for root, proof in sorted(root_proofs.items())
        }
    )
    (
        decisions_by_root,
        repaired_by_coordinate,
        repaired_risks,
    ) = repaired_pk_decisions(predecessor_rows)
    pending_by_root: defaultdict[tuple[int, int], list[str]] = (
        defaultdict(list)
    )
    verified_by_root: defaultdict[tuple[int, int], list[str]] = (
        defaultdict(list)
    )
    for (resource, coordinate), row in predecessor_rows.items():
        if resource != "pk_msggame":
            continue
        root = parse_coordinate(coordinate)[:2]
        if row.get("runtime_review") == "pending":
            pending_by_root[root].append(coordinate)
        elif row.get("runtime_review") == "verified":
            verified_by_root[root].append(coordinate)
    for mapping in (pending_by_root, verified_by_root):
        for coordinates in mapping.values():
            coordinates.sort(key=parse_coordinate)
    affected_pending_roots = set(pending_by_root) & affected
    affected_verified_roots = set(verified_by_root) & affected
    pending_summary = digest_summary(
        affected_pending_roots,
        pending_by_root,
    )
    verified_summary = digest_summary(
        affected_verified_roots,
        verified_by_root,
    )
    require(
        pending_summary
        == {
            "rows": EXPECTED_AFFECTED_PENDING_ROWS,
            "roots": EXPECTED_AFFECTED_PENDING_ROOTS,
            "coordinate_sha256":
            EXPECTED_AFFECTED_PENDING_COORDINATE_SHA256,
            "record_sha256": EXPECTED_AFFECTED_PENDING_ROOT_SHA256,
        }
        and verified_summary
        == {
            "rows": EXPECTED_VERIFIED_RENEWAL_ROWS,
            "roots": EXPECTED_VERIFIED_RENEWAL_ROOTS,
            "coordinate_sha256":
            EXPECTED_VERIFIED_RENEWAL_COORDINATE_SHA256,
            "record_sha256": EXPECTED_VERIFIED_RENEWAL_ROOT_SHA256,
        },
        "affected pending/verified universe drifted",
    )
    machine_entries: dict[tuple[int, int], dict[str, Any]] = {}
    for root in sorted(affected_pending_roots):
        closure = CROSS.PK_ONLY.closure_guard(
            root,
            inputs=candidate_inputs,
            decisions_by_record=decisions_by_root,
        )
        layout = CROSS.relative_layout_closure_guard(
            root,
            profiles=profiles,
            edges=candidate_edges,
        )
        machine_entries[root] = {
            "root": list(root),
            "member_coordinates": pending_by_root[root],
            "member_coordinate_sha256": coordinate_digest(
                pending_by_root[root]
            ),
            "closure_guard": closure,
            "relative_layout_guard": layout,
            "root_delta_proof_sha256": root_proofs[root]["proof_sha256"],
        }
    machine_roots = {
        root
        for root, entry in machine_entries.items()
        if CROSS.target_guard_passes(entry["closure_guard"])
        and entry["relative_layout_guard"]["status"] == "verified"
    }
    machine_summary = digest_summary(machine_roots, pending_by_root)
    require(
        machine_summary
        == {
            "rows": EXPECTED_MACHINE_ELIGIBLE_ROWS,
            "roots": EXPECTED_MACHINE_ELIGIBLE_ROOTS,
            "coordinate_sha256":
            EXPECTED_MACHINE_ELIGIBLE_COORDINATE_SHA256,
            "record_sha256": EXPECTED_MACHINE_ELIGIBLE_ROOT_SHA256,
        }
        and ACTUAL_ELIGIBLE_ROOTS <= machine_roots
        and machine_roots - ACTUAL_ELIGIBLE_ROOTS
        == set(MANUAL_REJECT_REASONS),
        "machine/manual caller adjudication drifted",
    )
    rejected_roots = affected_pending_roots - ACTUAL_ELIGIBLE_ROOTS
    eligible_summary = digest_summary(
        ACTUAL_ELIGIBLE_ROOTS,
        pending_by_root,
    )
    rejected_summary = digest_summary(rejected_roots, pending_by_root)
    require(
        eligible_summary
        == {
            "rows": EXPECTED_ELIGIBLE_ROWS,
            "roots": EXPECTED_ELIGIBLE_ROOTS,
            "coordinate_sha256": EXPECTED_ELIGIBLE_COORDINATE_SHA256,
            "record_sha256": EXPECTED_ELIGIBLE_ROOT_SHA256,
        }
        and rejected_summary
        == {
            "rows": EXPECTED_REJECTED_ROWS,
            "roots": EXPECTED_REJECTED_ROOTS,
            "coordinate_sha256": EXPECTED_REJECTED_COORDINATE_SHA256,
            "record_sha256": EXPECTED_REJECTED_ROOT_SHA256,
        },
        "actual eligible/rejected caller universe drifted",
    )
    family_summaries: dict[str, dict[str, Any]] = {}
    for family, family_targets in FAMILY_TARGETS.items():
        family_affected = HONORIFIC.reverse_ancestors(
            edges=source_edges,
            targets=tuple(family_targets),
        )
        family_pending = affected_pending_roots & family_affected
        family_verified = affected_verified_roots & family_affected
        family_eligible = ACTUAL_ELIGIBLE_ROOTS & family_pending
        family_summaries[family] = {
            "selector": FAMILY_SELECTORS[family],
            "terminal_records": len(family_targets),
            "affected_records": len(family_affected),
            "pending": digest_summary(
                family_pending,
                pending_by_root,
            ),
            "verified_renewal": digest_summary(
                family_verified,
                verified_by_root,
            ),
            "eligible": digest_summary(
                family_eligible,
                pending_by_root,
            ),
            "rejected": digest_summary(
                family_pending - family_eligible,
                pending_by_root,
            ),
        }
    rejection_reason_rows: Counter[str] = Counter()
    rejection_reason_roots: Counter[str] = Counter()
    for root in sorted(rejected_roots):
        entry = machine_entries[root]
        reasons = set(entry["closure_guard"]["failure_codes"])
        reasons.update(entry["relative_layout_guard"]["reason_codes"])
        manual_reason = MANUAL_REJECT_REASONS.get(root)
        if manual_reason is not None:
            reasons.add(manual_reason)
        for reason in reasons:
            rejection_reason_roots[reason] += 1
            rejection_reason_rows[reason] += len(pending_by_root[root])
    return {
        "predecessor_blob": predecessor_blob,
        "predecessor_records": predecessor_records,
        "candidate_blob": candidate_blob,
        "candidate_records": candidate_records,
        "changed": changed,
        "targets": targets,
        "target_delta": target_delta,
        "target_delta_sha256": target_delta_sha256,
        "assembly_manifest_sha256": canonical_sha256(assembly),
        "selector_summary": selector_summary,
        "candidate_inputs": candidate_inputs,
        "profiles": profiles,
        "candidate_edges": candidate_edges,
        "source_edges": source_edges,
        "candidate_affected": candidate_affected,
        "source_affected": source_affected,
        "affected": affected,
        "root_proofs": root_proofs,
        "root_proof_manifest_sha256": root_proof_manifest_sha256,
        "repaired_by_coordinate": repaired_by_coordinate,
        "repaired_risks": repaired_risks,
        "ledger_override_coordinates": ledger_override_coordinates,
        "untracked_literal_overrides": untracked_literal_overrides,
        "pending_by_root": dict(pending_by_root),
        "verified_by_root": dict(verified_by_root),
        "affected_pending_roots": affected_pending_roots,
        "affected_verified_roots": affected_verified_roots,
        "pending_summary": pending_summary,
        "verified_summary": verified_summary,
        "machine_entries": machine_entries,
        "machine_roots": machine_roots,
        "machine_summary": machine_summary,
        "eligible_roots": ACTUAL_ELIGIBLE_ROOTS,
        "eligible_summary": eligible_summary,
        "rejected_roots": rejected_roots,
        "rejected_summary": rejected_summary,
        "family_summaries": family_summaries,
        "rejection_reason_rows": dict(
            sorted(rejection_reason_rows.items())
        ),
        "rejection_reason_roots": dict(
            sorted(rejection_reason_roots.items())
        ),
    }


def public_machine_manifest(
    analysis: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for root in sorted(analysis["affected_pending_roots"]):
        entry = analysis["machine_entries"][root]
        base = {
            "root": list(root),
            "member_coordinate_sha256": entry[
                "member_coordinate_sha256"
            ],
            "closure_guard_sha256": entry["closure_guard"][
                "proof_sha256"
            ],
            "relative_layout_guard_sha256": entry[
                "relative_layout_guard"
            ]["proof_sha256"],
            "root_delta_proof_sha256": entry[
                "root_delta_proof_sha256"
            ],
        }
        if root in analysis["eligible_roots"]:
            eligible.append(base)
            continue
        reasons = set(entry["closure_guard"]["failure_codes"])
        reasons.update(entry["relative_layout_guard"]["reason_codes"])
        manual_reason = MANUAL_REJECT_REASONS.get(root)
        if manual_reason is not None:
            reasons.add(manual_reason)
        rejected.append(
            {
                **base,
                "reason_codes": sorted(reasons),
                "manual_full_assembly_rejected":
                manual_reason is not None,
            }
        )
    return eligible, rejected


def build_audit(
    *,
    analysis: Mapping[str, Any],
    predecessor_bindings: Mapping[str, str],
) -> dict[str, Any]:
    eligible_manifest, rejected_manifest = public_machine_manifest(
        analysis
    )
    source_only = (
        analysis["source_affected"] - analysis["candidate_affected"]
    )
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "scope": {
            "predecessor_rows": EXPECTED_PREDECESSOR_ROWS,
            "predecessor_pending_rows": EXPECTED_PREDECESSOR_PENDING_ROWS,
            "translation_override_coordinates": EXPECTED_OVERRIDE_ROWS,
            "translation_override_records": EXPECTED_OVERRIDE_RECORDS,
            "ledger_backed_override_coordinates":
            EXPECTED_LEDGER_OVERRIDE_ROWS,
            "literal_only_override_coordinates":
            EXPECTED_UNTRACKED_LITERAL_OVERRIDE_ROWS,
            "affected_pk_records": EXPECTED_AFFECTED_RECORDS,
            "source_only_affected_pk_records": len(source_only),
            "affected_existing_verified_pk_rows":
            EXPECTED_VERIFIED_RENEWAL_ROWS,
            "affected_existing_verified_pk_roots":
            EXPECTED_VERIFIED_RENEWAL_ROOTS,
            "affected_existing_verified_base_rows": 0,
            "affected_pending_pk_rows": EXPECTED_AFFECTED_PENDING_ROWS,
            "affected_pending_pk_roots": EXPECTED_AFFECTED_PENDING_ROOTS,
            "machine_eligible_rows": EXPECTED_MACHINE_ELIGIBLE_ROWS,
            "machine_eligible_roots": EXPECTED_MACHINE_ELIGIBLE_ROOTS,
            "actual_eligible_rows": EXPECTED_ELIGIBLE_ROWS,
            "actual_eligible_roots": EXPECTED_ELIGIBLE_ROOTS,
            "actual_rejected_rows": EXPECTED_REJECTED_ROWS,
            "actual_rejected_roots": EXPECTED_REJECTED_ROOTS,
            "post_layer_pending_rows": EXPECTED_PENDING_AFTER,
        },
        "adjudication": {
            "exact_override_map_owned_by_builder_source": True,
            "compressed_blob_runtime_dependency": False,
            "direct_predecessor_layer_rebuilt_and_validated": True,
            "candidate_and_source_graphs_both_audited": True,
            "all_affected_preexisting_verified_rows_renewed": True,
            "full_caller_branch_assembly_combinations":
            EXPECTED_ASSEMBLY_COMBINATIONS,
            "automatic_space_inserted": False,
            "control_bytes_preserved": True,
            "current_relative_raw_g1n_full_closure_gate": True,
            "manual_full_assembly_review_after_machine_gate": True,
            "uncertain_roots_remain_rejected": True,
            "base_resource_changed": False,
        },
        "families": analysis["family_summaries"],
        "selectors": {
            str(selector): summary
            for selector, summary in sorted(
                analysis["selector_summary"].items()
            )
        },
        "eligible_coordinates": member_coordinates(
            analysis["eligible_roots"],
            analysis["pending_by_root"],
        ),
        "literal_only_override_coordinates": sorted(
            analysis["untracked_literal_overrides"],
            key=parse_coordinate,
        ),
        "manual_rejected_roots": [
            {
                "root": list(root),
                "reason_code": MANUAL_REJECT_REASONS[root],
            }
            for root in sorted(MANUAL_REJECT_REASONS)
        ],
        "rejection_reason_rows": analysis["rejection_reason_rows"],
        "rejection_reason_roots": analysis["rejection_reason_roots"],
        "eligible_manifest_sha256": canonical_sha256(
            eligible_manifest
        ),
        "rejected_manifest_sha256": canonical_sha256(
            rejected_manifest
        ),
        "guards": {
            **dict(predecessor_bindings),
            "predecessor_pk_candidate_packed_sha256":
            EXPECTED_PREDECESSOR_PK_CANDIDATE_SHA256,
            "pk_candidate_packed_sha256":
            EXPECTED_PK_CANDIDATE_SHA256,
            "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "override_map_compact_json_sha256":
            EXPECTED_OVERRIDE_MAP_COMPACT_JSON_SHA256,
            "override_record_sha256": EXPECTED_OVERRIDE_RECORD_SHA256,
            "target_delta_manifest_sha256":
            analysis["target_delta_sha256"],
            "affected_record_sha256":
            EXPECTED_AFFECTED_RECORD_SHA256,
            "affected_pending_coordinate_sha256":
            EXPECTED_AFFECTED_PENDING_COORDINATE_SHA256,
            "affected_pending_root_sha256":
            EXPECTED_AFFECTED_PENDING_ROOT_SHA256,
            "verified_renewal_coordinate_sha256":
            EXPECTED_VERIFIED_RENEWAL_COORDINATE_SHA256,
            "verified_renewal_root_sha256":
            EXPECTED_VERIFIED_RENEWAL_ROOT_SHA256,
            "machine_eligible_coordinate_sha256":
            EXPECTED_MACHINE_ELIGIBLE_COORDINATE_SHA256,
            "machine_eligible_root_sha256":
            EXPECTED_MACHINE_ELIGIBLE_ROOT_SHA256,
            "actual_eligible_coordinate_sha256":
            EXPECTED_ELIGIBLE_COORDINATE_SHA256,
            "actual_eligible_root_sha256":
            EXPECTED_ELIGIBLE_ROOT_SHA256,
            "actual_rejected_coordinate_sha256":
            EXPECTED_REJECTED_COORDINATE_SHA256,
            "actual_rejected_root_sha256":
            EXPECTED_REJECTED_ROOT_SHA256,
            "root_delta_proof_manifest_sha256":
            analysis["root_proof_manifest_sha256"],
            "assembly_hash_manifest_sha256":
            EXPECTED_ASSEMBLY_HASH_MANIFEST_SHA256,
            "prior_multilingual_assembly_context_sha256":
            PRIOR_MULTILINGUAL_ASSEMBLY_CONTEXT_SHA256,
            "prior_full_assembly_analysis_sha256":
            PRIOR_FULL_ASSEMBLY_ANALYSIS_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_overlay_contains_translation_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


def evidence_row(
    *,
    coordinate: str,
    predecessor: Mapping[str, Any],
    updated_translation: str,
    action: str,
    status: str,
    root_proof: Mapping[str, Any],
    root_entry: Mapping[str, Any] | None,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "resource": "pk_msggame",
        "coordinate": coordinate,
        "status": status,
        "method": METHOD,
        "action": action,
        "translation_utf16le_sha256": ENGINE.sha256_text(
            updated_translation
        ),
        "predecessor_binding": {
            "row_sha256": canonical_sha256(predecessor),
            "predecessor_builder_sha256": audit["guards"][
                "predecessor_builder_sha256"
            ],
            "predecessor_audit_file_sha256": audit["guards"][
                "predecessor_audit_file_sha256"
            ],
            "predecessor_decision_delta_file_sha256": audit["guards"][
                "predecessor_decision_delta_file_sha256"
            ],
            "previous_runtime_vm_verification_sha256": (
                canonical_sha256(predecessor["runtime_vm_verification"])
                if isinstance(
                    predecessor.get("runtime_vm_verification"),
                    dict,
                )
                else None
            ),
        },
        "caller_delta_binding": {
            "root": root_proof["root"],
            "reachable_repaired_targets": root_proof[
                "reachable_repaired_targets"
            ],
            "root_delta_proof_sha256": root_proof["proof_sha256"],
            "target_delta_manifest_sha256": audit["guards"][
                "target_delta_manifest_sha256"
            ],
            "pk_candidate_packed_sha256": audit["guards"][
                "pk_candidate_packed_sha256"
            ],
            "assembly_hash_manifest_sha256": audit["guards"][
                "assembly_hash_manifest_sha256"
            ],
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
        },
        "preexisting_verified_evidence_renewed": (
            predecessor.get("runtime_review") == "verified"
        ),
        "per_row_game_playback_required": False,
    }
    if root_entry is not None:
        evidence["actual_promotion_binding"] = {
            "member_coordinate_sha256": root_entry[
                "member_coordinate_sha256"
            ],
            "closure_guard_sha256": root_entry["closure_guard"][
                "proof_sha256"
            ],
            "relative_layout_guard_sha256": root_entry[
                "relative_layout_guard"
            ]["proof_sha256"],
            "source_current_control_equal": root_entry["closure_guard"][
                "source_current_control_equal"
            ],
            "source_final_control_equal": root_entry["closure_guard"][
                "source_final_control_equal"
            ],
            "current_final_control_equal": root_entry["closure_guard"][
                "current_final_control_equal"
            ],
            "hard_grammar_risk_absent": root_entry["closure_guard"][
                "hard_grammar_risk_absent"
            ],
            "relative_full_closure_line_envelope_nonexpanding":
            root_entry["relative_layout_guard"][
                "relative_full_closure_line_envelope_nonexpanding"
            ],
            "manual_full_assembly_verified": True,
        }
    return evidence


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    verified_coordinates = set(
        member_coordinates(
            analysis["affected_verified_roots"],
            analysis["verified_by_root"],
        )
    )
    eligible_coordinates = set(
        member_coordinates(
            analysis["eligible_roots"],
            analysis["pending_by_root"],
        )
    )
    update_coordinates = (
        set(analysis["ledger_override_coordinates"])
        | verified_coordinates
        | eligible_coordinates
    )
    require(
        len(update_coordinates) == EXPECTED_DECISION_DELTA_ROWS,
        "decision delta coordinate count drifted",
    )
    updated_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    for coordinate in sorted(update_coordinates, key=parse_coordinate):
        key = ("pk_msggame", coordinate)
        predecessor = predecessor_rows[key]
        updated = copy.deepcopy(
            analysis["repaired_by_coordinate"][coordinate]
        )
        root = parse_coordinate(coordinate)[:2]
        is_override = coordinate in TRANSLATION_OVERRIDES
        is_promotion = coordinate in eligible_coordinates
        is_renewal = coordinate in verified_coordinates
        if is_override and is_promotion:
            action = "translation_override_and_runtime_promotion"
        elif is_override and is_renewal:
            action = "translation_override_and_verification_renewal"
        elif is_override:
            action = "translation_override_pending"
        elif is_promotion:
            action = "runtime_promotion"
        else:
            action = "verification_renewal"
        if is_promotion:
            require(
                predecessor.get("runtime_review") == "pending"
                and predecessor.get("scope_classification")
                == "runtime_fragment_pending",
                f"promotion predecessor drifted: {coordinate}",
            )
            updated["runtime_review"] = "verified"
            updated["scope_classification"] = "retranslated"
            updated["layout_review"] = "runtime_verified"
        elif is_renewal:
            require(
                predecessor.get("runtime_review") == "verified"
                and updated.get("runtime_review") == "verified",
                f"verified renewal state drifted: {coordinate}",
            )
        else:
            require(
                is_override
                and predecessor.get("runtime_review") == "pending",
                f"unexpected pending override: {coordinate}",
            )
        status = str(updated["runtime_review"])
        root_entry = (
            analysis["machine_entries"][root] if is_promotion else None
        )
        evidence = evidence_row(
            coordinate=coordinate,
            predecessor=predecessor,
            updated_translation=str(updated["translation"]),
            action=action,
            status=status,
            root_proof=analysis["root_proofs"][root],
            root_entry=root_entry,
            audit=audit,
            audit_file_sha256=audit_file_sha256,
        )
        updated["bound_terminal_caller_update_action"] = action
        if status == "verified":
            updated["runtime_vm_verification"] = evidence
        else:
            updated["bound_terminal_caller_runtime_evidence"] = evidence
        updated_rows.append(updated)
        evidence_rows.append(evidence)
    updated_rows.sort(key=row_sort_key)
    evidence_rows.sort(
        key=lambda row: parse_coordinate(str(row["coordinate"]))
    )
    return updated_rows, evidence_rows


def build_promotion_report(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
    evidence_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    actions = Counter(str(row["action"]) for row in evidence_rows)
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "result": {
            "translation_override_coordinates": EXPECTED_OVERRIDE_ROWS,
            "ledger_backed_override_coordinates":
            EXPECTED_LEDGER_OVERRIDE_ROWS,
            "literal_only_override_coordinates":
            EXPECTED_UNTRACKED_LITERAL_OVERRIDE_ROWS,
            "existing_verified_pk_evidence_renewal_rows":
            EXPECTED_VERIFIED_RENEWAL_ROWS,
            "existing_verified_base_evidence_renewal_rows": 0,
            "runtime_promotion_rows": EXPECTED_ELIGIBLE_ROWS,
            "runtime_promotion_roots": EXPECTED_ELIGIBLE_ROOTS,
            "rejected_pending_rows": EXPECTED_REJECTED_ROWS,
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "decision_delta_rows": EXPECTED_DECISION_DELTA_ROWS,
            "private_evidence_rows": EXPECTED_EVIDENCE_ROWS,
            "private_decision_delta_sha256": sha256_bytes(
                decision_content.encode("utf-8")
            ),
            "private_evidence_sha256": sha256_bytes(
                evidence_content.encode("utf-8")
            ),
            "translation_body_copied_to_evidence_overlay": False,
        },
        "action_counts": dict(sorted(actions.items())),
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "predecessor_builder_sha256": audit["guards"][
                "predecessor_builder_sha256"
            ],
            "predecessor_pk_candidate_packed_sha256": audit["guards"][
                "predecessor_pk_candidate_packed_sha256"
            ],
            "pk_candidate_packed_sha256": audit["guards"][
                "pk_candidate_packed_sha256"
            ],
            "override_map_compact_json_sha256":
            EXPECTED_OVERRIDE_MAP_COMPACT_JSON_SHA256,
            "actual_eligible_coordinate_sha256":
            EXPECTED_ELIGIBLE_COORDINATE_SHA256,
            "actual_eligible_root_sha256":
            EXPECTED_ELIGIBLE_ROOT_SHA256,
            "verified_renewal_coordinate_sha256":
            EXPECTED_VERIFIED_RENEWAL_COORDINATE_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_overlay_contains_translation_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


def build_outputs() -> tuple[
    str,
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    steam_before = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    predecessor_rows, predecessor_bindings = load_predecessor()
    analysis = build_analysis(predecessor_rows)
    audit = build_audit(
        analysis=analysis,
        predecessor_bindings=predecessor_bindings,
    )
    HONORIFIC.validate_seal(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updated_rows, evidence_rows = build_updated_rows(
        predecessor_rows=predecessor_rows,
        analysis=analysis,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updated_rows)
    evidence_content = canonical_jsonl(evidence_rows)
    promotion = build_promotion_report(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
        evidence_rows=evidence_rows,
    )
    HONORIFIC.validate_seal(promotion)
    promotion_content = canonical_json(promotion)
    steam_after = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during caller closure build",
    )
    return (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        {
            "predecessor_rows": predecessor_rows,
            "updated_rows": updated_rows,
            "evidence_rows": evidence_rows,
            "analysis": analysis,
            "promotion": promotion,
        },
    )


SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
    r"\uac00-\ud7a3]"
)


def assert_source_free_report(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            require(
                key not in {
                    "translation",
                    "source_text",
                    "current_text",
                    "candidate_text",
                    "assembly",
                },
                f"tracked report contains a dialogue body key: {key}",
            )
            assert_source_free_report(child)
    elif isinstance(value, list):
        for child in value:
            assert_source_free_report(child)
    elif isinstance(value, str):
        require(
            SOURCE_TEXT_RE.search(value) is None,
            "tracked report contains source/translated dialogue text",
        )


def contains_body_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            key
            in {
                "translation",
                "source_text",
                "current_text",
                "candidate_text",
                "assembly",
            }
            or contains_body_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(contains_body_key(child) for child in value)
    return False


def validate_outputs(
    *,
    decision_content: str,
    evidence_content: str,
    audit_content: str,
    promotion_content: str,
    audit: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> None:
    analysis = bundle["analysis"]
    promotion = bundle["promotion"]
    require(
        decision_content == canonical_jsonl(bundle["updated_rows"])
        and evidence_content == canonical_jsonl(bundle["evidence_rows"])
        and audit_content == canonical_json(audit)
        and promotion_content == canonical_json(promotion),
        "serialized output drifted",
    )
    require(
        sha256_bytes(audit_content.encode("utf-8"))
        == EXPECTED_AUDIT_FILE_SHA256
        and sha256_bytes(promotion_content.encode("utf-8"))
        == EXPECTED_PROMOTION_FILE_SHA256
        and sha256_bytes(decision_content.encode("utf-8"))
        == EXPECTED_DECISION_FILE_SHA256
        and sha256_bytes(evidence_content.encode("utf-8"))
        == EXPECTED_EVIDENCE_FILE_SHA256,
        "frozen output file hash drifted",
    )
    HONORIFIC.validate_seal(audit)
    HONORIFIC.validate_seal(promotion)
    assert_source_free_report(audit)
    assert_source_free_report(promotion)
    require(
        not any(
            contains_body_key(row) for row in bundle["evidence_rows"]
        ),
        "private evidence overlay contains dialogue bodies",
    )
    updated_by_key = {
        (str(row["resource"]), str(row["coordinate"])): row
        for row in bundle["updated_rows"]
    }
    require(
        len(updated_by_key) == EXPECTED_DECISION_DELTA_ROWS
        and len(bundle["evidence_rows"]) == EXPECTED_EVIDENCE_ROWS
        and all(resource == "pk_msggame" for resource, _ in updated_by_key),
        "private delta row universe drifted",
    )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["predecessor_rows"].items()
    }
    merged.update(
        {
            key: copy.deepcopy(dict(row))
            for key, row in updated_by_key.items()
        }
    )
    pending_after = [
        coordinate
        for (_, coordinate), row in merged.items()
        if row.get("runtime_review") == "pending"
    ]
    promoted = [
        row
        for row in bundle["updated_rows"]
        if str(row.get("bound_terminal_caller_update_action"))
        in {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }
    ]
    promoted_coordinates = [
        str(row["coordinate"]) for row in promoted
    ]
    renewed_coordinates = {
        str(row["coordinate"])
        for row in bundle["updated_rows"]
        if bool(
            row.get("runtime_vm_verification", {}).get(
                "preexisting_verified_evidence_renewed"
            )
        )
    }
    expected_renewed_coordinates = set(
        member_coordinates(
            analysis["affected_verified_roots"],
            analysis["verified_by_root"],
        )
    )
    require(
        len(merged) == EXPECTED_PREDECESSOR_ROWS
        and len(pending_after) == EXPECTED_PENDING_AFTER
        and len(promoted) == EXPECTED_ELIGIBLE_ROWS
        and coordinate_digest(promoted_coordinates)
        == EXPECTED_ELIGIBLE_COORDINATE_SHA256
        and renewed_coordinates == expected_renewed_coordinates
        and len(renewed_coordinates) == EXPECTED_VERIFIED_RENEWAL_ROWS,
        "promotion/renewal result drifted",
    )
    for coordinate, expected_translation in TRANSLATION_OVERRIDES.items():
        if coordinate in analysis["untracked_literal_overrides"]:
            continue
        require(
            merged[("pk_msggame", coordinate)].get("translation")
            == expected_translation,
            f"merged override drifted: {coordinate}",
        )
    require(
        audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_PENDING_AFTER
        and promotion["result"]["pending_rows_after"]
        == EXPECTED_PENDING_AFTER
        and audit["scope"]["actual_eligible_rows"]
        == EXPECTED_ELIGIBLE_ROWS
        and promotion["result"]["runtime_promotion_rows"]
        == EXPECTED_ELIGIBLE_ROWS
        and audit.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False,
        "sealed result assertions drifted",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=DEFAULT_AUDIT_OUTPUT,
    )
    parser.add_argument(
        "--promotion-output",
        type=Path,
        default=DEFAULT_PROMOTION_OUTPUT,
    )
    parser.add_argument(
        "--decision-output",
        type=Path,
        default=DEFAULT_DECISION_OUTPUT,
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=DEFAULT_EVIDENCE_OUTPUT,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify all four outputs without writing",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = build_outputs()
    validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    outputs = {
        args.audit_output: audit_content,
        args.promotion_output: promotion_content,
        args.decision_output: decision_content,
        args.evidence_output: evidence_content,
    }
    if args.check:
        for path, expected_content in outputs.items():
            require(path.is_file(), f"output missing: {path}")
            require(
                path.read_text(encoding="utf-8") == expected_content,
                f"output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(
        "PASS "
        f"overrides={EXPECTED_OVERRIDE_ROWS} "
        f"verified_renewed={EXPECTED_VERIFIED_RENEWAL_ROWS} "
        f"promoted={EXPECTED_ELIGIBLE_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        "base_renewed=0 steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
