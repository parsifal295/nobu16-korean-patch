#!/usr/bin/env python3
"""Build source-free ev_strdata historical event batch v0.20 artifacts."""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402


BATCH_ID = "ev-strdata-historical-events-3840-4031-v0.20"
OVERLAY_NAME = "ev_strdata_ko_historical_events_3840_4031.v0.20.json"
EVIDENCE_NAME = "alignment_evidence.v0.20.json"
REVIEW_NAME = "review_index.v0.20.json"
VALIDATION_NAME = "validation.v0.20.json"

SCOPE_START = 3840
SCOPE_END = 4031
NEXT_DISPLAY_ID = 4032
TRANSLATED_COUNT = 192
INSPECTED_COUNT = 192
DEFERRED_COUNT = 0

TRANSLATED_IDS_SHA256 = "693A476D0B1166F8A4CF078781191FD22EE7D65A40CF4B1775EDDD5613A381FC"
TRANSLATION_MAP_SHA256 = "817FEABA5642575AB0292FBBAC3B83586DCCB8F66044A09093704EAB497FAA3C"
SOURCE_SC_HASHES_SHA256 = "A9295B2B2CE32F2128C7C26A4599562028DAF7F09B7F91A170C3246BDCDE7031"
ALL_REFERENCE_HASHES_SHA256 = "800EA54FF6E27C1E1D40F486B63BCB5739FF91C1CDF15B4289C844D7C536E94E"
INSPECTED_IDS_SHA256 = TRANSLATED_IDS_SHA256
DEFERRED_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
PREVIOUS_DEFERRED_UNION_COUNT = 549
PREVIOUS_DEFERRED_UNION_SHA256 = "13D87F620AE49897C10127F8FED317F99859FA89CCAF13CDAACBE0D81787F449"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "FCAA8FDD7BBE890A629F96835261EA2ACEDD251BDF7770CCAF9EB222E602DFDE",
    "JP": "E7DB5882DE2F59495E62459DC7B5619C0EEC1F79E1D802663E6F47F915DF8DC7",
    "TC": "1FDEC5A32DAB34F15633F0758446928D0B0CE3296E9CE1646AEB7BA619C7A6CD",
}

TRANSLATIONS = {
    3840: '\uadf8 \uc77c\uc740 \ub108\ubb34\ub3c4 \uac11\uc791\uc2a4\ub7ec\uc6e0\ub2e4.\n\x1bCC\ubbf8\uce74\uc640 \uc624\uce74\uc790\ud0a4\uc131\x1bCZ\uc758 \ub2e4\uc774\ubb18 \x1bCA\ub9c8\uc4f0\ub2e4\uc774\ub77c \ud788\ub85c\ud0c0\ub2e4\x1bCZ\uac00\n\uc544\ubb34\ub7f0 \uc804\uc870\ub3c4 \uc5c6\uc774 \uc138\uc0c1\uc744 \ub5a0\ub09c \uac83\uc774\ub2e4\u2026\u2026',
    3841: '\ubcd1\uc0ac\ud588\ub2e4\uac70\ub098 \ub204\uad70\uac00\uc5d0\uac8c \uc554\uc0b4\ub2f9\ud588\ub2e4\ub294 \uc774\uc57c\uae30\ub3c4 \uc788\uc9c0\ub9cc,\n\uc9c4\uc0c1\uc740 \uc804\ud600 \ubc1d\ud600\uc9c0\uc9c0 \uc54a\uc558\ub2e4.',
    3842: '\uc911\uc694\ud55c \uac83\uc740 \x1bCA\ud788\ub85c\ud0c0\ub2e4\x1bCZ\uc758 \ub4a4\ub97c \uc774\uc744 \uc801\uc790 \x1bCA\ub2e4\ucf00\uce58\uc694\x1bCZ\uac00,\n\x1bCB\uc774\ub9c8\uac00\uc640 \uac00\ubb38\x1bCZ\uc758 \uc778\uc9c8\ub85c \x1bCC\uc2a8\ud478\x1bCZ\uc5d0 \uba38\ubb3c\ub800\ub2e4\ub294 \uc0ac\uc2e4\uc774\ub2e4.',
    3843: '\x1bCC\uc2a8\ud478\x1bCZ\xb7\x1bCC\uc774\ub9c8\uac00\uc640\uad00\x1bCZ\u2015',
    3844: '\x1bCB\ub9c8\uc4f0\ub2e4\uc774\ub77c\x1bCZ \uac00\uc2e0\ub4e4\uc740 \uc6b0\ub9ac\uc5d0\uac8c\n\x1bCA\ub2e4\ucf00\uce58\uc694\x1bCZ\uc758 \ubc18\ud658\uc744 \uc694\uad6c\ud558\uaca0\uc9c0\u2026\u2026',
    3845: '\x1bCA\ub2e4\ucf00\uce58\uc694\x1bCZ\ub294 \uc9c0\uae08 \ub0b4 \uc808\uc5d0\uc11c \ud559\ubb38\uc744 \ub2e6\uace0 \uc788\uc73c\ub098,\n\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ \ub2d8\uaed8\uc11c \uba85\ud558\uc2dc\uba74\n\x1bCC\uc624\uce74\uc790\ud0a4\x1bCZ\ub85c \ub3cc\ub824\ubcf4\ub0bc \uc218\ub3c4 \uc788\uc2b5\ub2c8\ub2e4\u2026\u2026',
    3846: '\uc2a4\uc2b9\uaed8\uc11c\ub3c4 \uc9d3\uad82\uc73c\uc2dc\uad70\u2026\u2026\n\ub0b4 \ub73b\uc774 \uac70\uae30\uc5d0 \uc5c6\ub2e4\ub294 \uac83\uc744 \uc54c\uace0 \uacc4\uc2dc\uba74\uc11c.',
    3847: '\uadf8\ub7ec\uba74 \x1bCC\uc624\uce74\uc790\ud0a4\x1bCZ\uc758 \x1bCB\ub9c8\uc4f0\ub2e4\uc774\ub77c \uac00\ubb38\x1bCZ\uc740\u2026\u2026?',
    3848: '\uadf8\ub4e4\uc744 \x1bCB\uc774\ub9c8\uac00\uc640 \uac00\ubb38\x1bCZ \uc0b0\ud558\uc5d0 \ub123\ub294\ub2e4.\n\x1bCC\uc624\uce74\uc790\ud0a4\uc131\x1bCZ\uc5d0\ub294 \ub300\uad00\uacfc \ubcd1\uc0ac\ub97c \ub450\uace0,\n\uc9c1\uc811 \ub2e4\uc2a4\ub9ac\uaca0\ub2e4.',
    3849: '\uadf8\ub798\uc11c\ub294 \x1bCB\ub9c8\uc4f0\ub2e4\uc774\ub77c\x1bCZ\uc758 \uc61b \uac00\uc2e0\ub4e4\uc774 \ub0a9\ub4dd\ud558\uc9c0 \uc54a\uc744 \ud130\u2026\u2026\n\x1bCB\uc774\ub9c8\uac00\uc640 \uac00\ubb38\x1bCZ\uc740 \x1bCA\ub2e4\ucf00\uce58\uc694\x1bCZ\uac00 \uc131\ub144\uc774 \ub418\uba74 \x1bCC\uc624\uce74\uc790\ud0a4\x1bCZ\ub97c\n\x1bCB\ub9c8\uc4f0\ub2e4\uc774\ub77c \uac00\ubb38\x1bCZ\uc5d0 \ub3cc\ub824\uc8fc\uaca0\ub2e4\uace0 \uc804\ud558\uba74 \uc5b4\ub5bb\uaca0\uc2b5\ub2c8\uae4c?',
    3850: '\ud558\ud558\ud558. \ub3cc\ub824\uc904 \uc0dd\uac01\ub3c4 \uc5c6\ub294\ub370 \ub9d0\uc774\ub0d0?\n\uc88b\ub2e4\u2026\u2026 \x1bCA\ub2e4\ucf00\uce58\uc694\x1bCZ\uac00 \uc131\ub144\uc774 \ub418\ub824\uba74 \uba40\uc5c8\uc73c\ub2c8,\n\ub2f9\ubd84\uac04 \uafc8\uc744 \uafb8\uac8c \ud574 \uc8fc\uc790.',
    3851: '\x1bCA\ud788\ub85c\ud0c0\ub2e4\x1bCZ\uc758 \uc8fd\uc74c\uc73c\ub85c \x1bCB\ub9c8\uc4f0\ub2e4\uc774\ub77c \uac00\ubb38\x1bCZ\uc740 \ub2e4\uc774\ubb18\ub85c\uc11c\n\ud55c\ub54c \uba78\ub9dd\ud588\uace0, \x1bCC\uc624\uce74\uc790\ud0a4\uc131\x1bCZ\uacfc \ud568\uaed8\n\x1bCB\uc774\ub9c8\uac00\uc640 \uac00\ubb38\x1bCZ \uc0b0\ud558\uc5d0 \ud3b8\uc785\ub418\uc5c8\ub2e4.',
    3852: '\x1bCB\ub9c8\uc4f0\ub2e4\uc774\ub77c\x1bCZ \uac00\uc2e0\ub4e4\uc740 \x1bCB\uc774\ub9c8\uac00\uc640\x1bCZ\uc758 \uc9c0\ubc30\ub97c \ubc1b\uc544\ub4e4\uc774\uace0,\n\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc758 \ud5db\ub41c \uc57d\uc18d\uc5d0 \ud55c \uc904\uae30 \ud76c\ub9dd\uc744 \uac78\uc5c8\ub2e4.',
    3853: '\uba87 \ub144\ub9cc \ub354\u2026\u2026 \x1bCA\ub2e4\ucf00\uce58\uc694\x1bCZ \ub2d8\uaed8\uc11c \uc131\ub144\uc774 \ub418\uc2dc\uba74\n\x1bCC\uc624\uce74\uc790\ud0a4\x1bCZ\uc758 \uc131\ub3c4, \x1bCB\ub9c8\uc4f0\ub2e4\uc774\ub77c\x1bCZ \uac00\ubb38\ub3c4\n\uc608\uc804 \ubaa8\uc2b5\uc73c\ub85c \ub418\uc0b4\uc544\ub0a0 \uac83\uc774\ub2e4\u2026\u2026',
    3854: '\x1bCB\ub9c8\uc4f0\ub2e4\uc774\ub77c\x1bCZ\uc758 \uc61b \uac00\uc2e0\ub4e4\uc740 \uadf8 \ubbff\uc74c \ud558\ub098\ub85c,\n\x1bCB\uc774\ub9c8\uac00\uc640\x1bCZ \uc0b0\ud558\uc758 \uac00\ud639\ud55c \ub098\ub0a0\uc744 \ubb35\ubb35\ud788 \uacac\ub3a0\ub2e4.',
    3855: '\x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc740 \uac04\ud1a0 \uac04\ub808\uc774\ub97c \ub9e1\uc740\n\x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc758 \uac00\uc7ac\ub97c \ubc30\ucd9c\ud55c \uc9d1\uc548\uc774\uba70,\n\x1bCC\uc5d0\uce58\uace0\x1bCZ\uc758 \x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc740 \uadf8 \ubd84\uac00\uc5d0 \ud574\ub2f9\ud55c\ub2e4.',
    3856: '\ud558\uc9c0\ub9cc \x1bCB\ud6c4\ucd94 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uacfc \x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc740\n\uac19\uc740 \x1bCB\uc5d0\uce58\uace0 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \uc77c\uc871\uc774\uba74\uc11c\ub3c4,\n\uc608\uc804\ubd80\ud130 \uc0ac\uc774\uac00 \ud5d8\uc545\ud588\ub2e4.',
    3857: '\x1bCB\ud6c4\ucd94 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \x1bCA\ub2e4\uba54\uce74\uac8c\x1bCZ\uac00 \x1bCC\uc5d0\uce58\uace0\x1bCZ\uc5d0\uc11c \uc138\ub825\uc744 \ub113\ud788\uc790,\n\x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc740 \ubc18\uae30\ub97c \ub4e4\uc5c8\uc73c\ub098,\n\ub05d\ub0b4 \ud328\ud558\uace0 \ub9d0\uc558\ub2e4.',
    3858: '\x1bCA\ub2e4\uba54\uce74\uac8c\x1bCZ\uc758 \uc544\ub4e4 \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\ub294 \x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc744\n\ub2e4\uc2dc \uc77c\ubb38 \uc138\ub825\uc73c\ub85c \ub04c\uc5b4\ub4e4\uc774\ub824\n\uba87 \ucc28\ub840 \uad50\uc12d\ud588\uc9c0\ub9cc \uc9c4\ucc99\uc740 \ub354\ub3a0\ub2e4.',
    3859: '\ud558\uc9c0\ub9cc \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\ub97c \ub300\uc2e0\ud574 \ub2f9\uc8fc\uac00 \ub41c \x1bCA[bm1448]\x1bCZ \uacf5\uc740,\n\x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc744 \ub04c\uc5b4\ub4e4\uc774\uc9c0 \uc54a\uace0\uc11c\ub294\n\x1bCC\uc5d0\uce58\uace0\x1bCZ\ub97c \uc7a5\uc545\ud560 \uc218 \uc5c6\uc5c8\ub2e4.',
    3860: '\ud55c\ud3b8 \x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\ub3c4,\n\x1bCA[bm1448]\x1bCZ \uacf5\uc774 \ube60\ub974\uac8c \x1bCC\uc5d0\uce58\uace0\x1bCZ\uc758 \uae30\ubc18\uc744 \uad73\ud788\uc790,\n\uc790\uc2e0\uc774 \uace0\ub9bd\ub420 \uac83\uc744 \uc5fc\ub824\ud588\ub2e4.',
    3861: '\uc11c\ub85c\uc758 \ud544\uc694\ub294 \uc778\uc815\ud588\uc9c0\ub9cc \uad50\uc12d\uc774 \ub2a6\uc5b4\uc9c0\uc790,\n\ucd08\uc870\ud574\uc9c4 \x1bCA[bm1448]\x1bCZ \uacf5\uc740 \ub9c8\uce68\ub0b4 \x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\uac00 \uc788\ub294\n\x1bCC\uc0ac\uce74\ud1a0\uc131\x1bCZ\uc73c\ub85c \uad70\uc0ac\ub97c \ubcf4\ub0c8\ub2e4\u2026\u2026',
    3862: '\x1bCA[b1448]\x1bCZ \uacf5\uc740 \uc80a\uc740\ub370\ub3c4 \uc81c\ubc95\uc774\uad70.\n\ub9d0\ub2e8 \ubcd1\uc0ac\uae4c\uc9c0 \uad70\ub839\uc774 \ub2ff\uace0 \uc9c4\ud615\uc5d0 \ud750\ud2b8\ub7ec\uc9d0\uc774 \uc5c6\ub2e4.\n\ud589\uad70\uc774 \ubb34\uc5c7\uc778\uc9c0 \uc81c\ub300\ub85c \uc544\ub294 \uc790\ub2e4.',
    3863: '\ub9cc\ub9cc\ucc2e\uc740 \uc801\uc785\ub2c8\ub2e4.\n\ub18d\uc131 \uc900\ube44\ub294 \ub9c8\ucce4\uc2b5\ub2c8\ub2e4\ub9cc\u2026\u2026\n\ub098\uac00\uc11c \ub9de\uc11c\uc2dc\uaca0\uc2b5\ub2c8\uae4c?',
    3864: '\uc544\ub2c8, \uc2f8\uc6c0\uc73c\ub85c \ubc88\uc9c0\uc9c0 \uc54a\uc744 \uac83\uc774\ub2e4.\n\x1bCA[bm1448]\x1bCZ \uacf5\uc740 \uc774 \uc131\uc744 \ube7c\uc557\uc73c\ub7ec \uc628 \uac8c \uc544\ub2c8\ub2e4.\n\ub098\uc640 \uad50\uc12d\ud558\ub7ec \uc628 \uac83\uc774\ub2e4.',
    3865: '\uacfc\uc5f0 \x1bCA[bm1448]\x1bCZ \uacf5\uc740 \uc131\uc744 \ud3ec\uc704\ud558\uae30\ub9cc \ud588\uc744 \ubfd0,\n\uacf5\uaca9\ud560 \uae30\uc0c9\uc740 \ubcf4\uc774\uc9c0 \uc54a\uc558\ub2e4.\n\uadf8\ub807\ub2e4\uace0 \ubcd1\ub7c9\uc744 \ub04a\uc73c\ub824 \ud558\uc9c0\ub3c4 \uc54a\uc558\ub2e4.',
    3866: '\uc80a\uc740\uc774\uce58\uace0\ub294 \ub108\ubb34 \ub178\ub828\ud558\uc9c0\ub9cc\u2026\u2026\n\uc88b\ub2e4, \uc774\ubc88\uc5d0\ub294 \ub0b4\uac00 \ud55c\ubc1c \ubb3c\ub7ec\uc11c \uc8fc\uc9c0.\n\ub098\uc05c \uc774\uc57c\uae30\ub294 \uc544\ub2d0 \ud14c\ub2c8.',
    3867: '\x1bCC\uc0ac\uce74\ud1a0\uc131\x1bCZ \ubc16, \x1bCA[b1448]\x1bCZ \uacf5\uc758 \uc9c4\uc601\u2015',
    3868: '\uc131\uc8fc \x1bCA\ub098\uac00\uc624 \ub9c8\uc0ac\uce74\uac8c\x1bCZ \ub2d8\uaed8\uc11c \uc9c1\uc811 \uc624\uc168\uc2b5\ub2c8\ub2e4.',
    3869: '\uc2e4\ub840\ud558\uaca0\uc18c.\n\x1bCA\ub098\uac00\uc624 \ub9c8\uc0ac\uce74\uac8c\x1bCZ\uac00 \x1bCA[bm1448]\x1bCZ \uacf5\uc744 \ubd59\uace0\uc790 \uc654\uc18c.',
    3870: '\uc774\ub7f0, \uc774\ub7f0\u2026\u2026\n\x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ \ub2f9\uc8fc\uaed8\uc11c \uc9c1\uc811 \uc9c4\uc911\uc5d0 \uc624\uc2dc\ub2e4\ub2c8.\n\ucc38\uc73c\ub85c \uac10\uc0ac\ud558\uc624.',
    3871: '\uc774\uac83\uc740\u2026\u2026 \uc55e\uc73c\ub85c \x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc774\n\x1bCB\ud6c4\ucd94 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc5d0 \uc2e0\uc885\ud558\uaca0\ub2e4\ub294 \uc11c\uc57d\uc11c\uc694.\n\ubd80\ub514 \ubc1b\uc544 \uc8fc\uc2dc\uc624.',
    3872: '\uadf8\ub807\ub2e4\uba74 \uc55e\uc73c\ub85c\ub294\u2026\u2026',
    3873: '\x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\ub294 \x1bCA[bm1448]\x1bCZ \uacf5\uc758 \uac00\uc2e0\uc73c\ub85c \ud798\uc4f0\uace0\uc790 \ud558\uc624.',
    3874: '\uace0\ub9c8\uc6b4 \uc81c\uc548\uc774\ub2c8 \ucc38\uc73c\ub85c \uac10\uaca9\uc2a4\ub7fd\uc18c.\n\ub098 \ub610\ud55c \uadf8\ub300\uc758 \uc131\uc758\uc5d0 \ubcf4\ub2f5\ud574\uc57c\uaca0\uad70.\n\ub0b4 \ub204\ub2d8\uacfc \ud63c\uc778\ud558\ub294 \uac83\uc740 \uc5b4\ub5bb\uc18c?',
    3875: '\uc774\ub294 \ubc14\ub77c \ub9c8\uc9c0\uc54a\ub358 \uc77c\uc774\uc624.\n\x1bCA\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \ub9c8\uc0ac\uce74\uac8c\x1bCZ\ub294 \uc774\uc81c\ubd80\ud130 \x1bCA[bm1448]\x1bCZ \uacf5\uc758\n\uc77c\ubb38\uc73c\ub85c\uc11c \ucda9\uc131\uc744 \ub9f9\uc138\ud558\uaca0\uc18c.',
    3876: '\uacf5\uc801\uc778 \uc774\uc57c\uae30\ub97c \ub098\ub204\ub294 \ub3d9\uc548,\n\x1bCA[bm1448]\x1bCZ \uacf5\uacfc \x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\ub294 \uc11c\ub85c\uc758 \uc0ac\ub78c\ub428\uc744 \uc0b4\ud3c8\uace0,\n\ub9c8\uce68\ub0b4 \uc11c\ub85c\ub97c \uc778\uc815\ud588\ub2e4.',
    3877: '\ub2e4\ub978 \uace0\ucfe0\uc9c4\uc774 \ubcf4\ub294 \uc55e\uc5d0\uc11c \uc77c\uc871\uc774\ub77c\ub3c4 \uac00\ucc28 \uc5c6\uc774\n\uad70\uc0ac\ub97c \ubcf4\ub0b4 \uad74\ubcf5\uc2dc\ud0a4\ub294 \ubaa8\uc2b5\uc744 \ubcf4\uc784\uc73c\ub85c\uc368,\n\uac00\ubb38\uc744 \ub2e4\uc2dc \ub2e4\uc7a1\uc740 \x1bCA[bm1448]\x1bCZ \uacf5\u2015',
    3878: '\ub2f9\uc8fc\uac00 \uce5c\ud788 \uad70\uc0ac\ub97c \ub0b4\uc5b4 \uad74\ubcf5\uc2dc\ud0a8 \uc77c\uc774\uae30\uc5d0,\n\x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\ub294 \uc55e\uc73c\ub85c \x1bCB\ud6c4\ucd94 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758\n\uc911\uc9c4\uc73c\ub85c\uc11c \uc9c0\uc704\ub97c \uc790\uc5f0\uc2a4\ub808 \uc778\uc815\ubc1b\uc558\ub2e4\u2015',
    3879: '\ub450 \uc0ac\ub78c\uc740 \uc11c\ub85c \ub9cc\ub9cc\ucc2e\uc740 \uc790\ub77c \uacbd\uacc4\ud558\uba74\uc11c\ub3c4 \uc190\uc744 \uc7a1\uc558\uace0,\n\x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \uacb0\uc18d\uc740 \uad73\uc5b4\uc84c\ub2e4. \uadf8 \uad00\uacc4\uc758\n\ud575\uc2ec\uc740 \ud55c \uc5ec\uc778\uc5d0\uac8c \ub9e1\uaca8\uc84c\ub2e4\u2026\u2026',
    3880: '\x1bCC\uc544\ud0a4\x1bCZ\uc640 \x1bCC\uc774\uc640\ubbf8\x1bCZ\uc5d0 \uc138\ub825\uc744 \ub113\ud78c \x1bCB\uae43\uce74\uc640\uc528\x1bCZ.\n\ubcf8\ub798 \x1bCB\ud6c4\uc9c0\uc640\ub77c\uc528\x1bCZ \ucd9c\uc2e0\uc73c\ub85c, \uac00\ub9c8\ucfe0\ub77c \uc2dc\ub300 \uc911\uae30\uc5d0\n\x1bCC\uc0ac\uc774\uace0\ucfe0\x1bCZ\ub85c \uadfc\uac70\uc9c0\ub97c \uc62e\uae34 \ubb34\uc0ac \uc9d1\ub2e8\uc774\uc5c8\ub2e4.',
    3881: '\ud604 \ub2f9\uc8fc \x1bCA\uae43\uce74\uc640 \uc624\ud0a4\uce20\ub124\x1bCZ\ub3c4\n\ubb34\uc6a9\uc774 \ub6f0\uc5b4\ub09c \ubb34\uc7a5\uc774\uc5c8\uc9c0\ub9cc\u2026\u2026',
    3882: '\x1bCC\uac13\uc0b0\ud1a0\ub2e4\uc131\x1bCZ \uc804\ud22c\uc5d0\uc11c \ubc30\uc2e0\ud55c \ud0d3\uc5d0,\n\uc8fc\ubcc0\uc758 \uc2e0\ub8b0\ub97c \uc644\uc804\ud788 \uc783\uc5c8\ub2e4.',
    3883: '\uadf8 \uc810\uc5d0 \uc8fc\ubaa9\ud55c \x1bCA\ubaa8\ub9ac \ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294\n\ud55c \uac00\uc9c0 \uacc4\ucc45\uc744 \uc138\uc6e0\ub2e4.',
    3884: '\x1bCA\ubaa8\ud1a0\ud558\ub8e8\x1bCZ, \ub108\ub294 \uc774\uc81c\ubd80\ud130 \x1bCB\uae43\uce74\uc640 \uac00\ubb38\x1bCZ\uc73c\ub85c \ub4e4\uc5b4\uac00\ub77c.\n\x1bCA\uc624\ud0a4\uce20\ub124\x1bCZ\uc758 \uc591\uc790\uac00 \ub418\ub294 \uac83\uc774\ub2e4.',
    3885: '\x1bCA\uae43\uce74\uc640\x1bCZ\u2026\u2026?\n\uadf8 \uacbd\uc194\ud558\ub2e4\uace0 \uc18c\ubb38\ub09c \x1bCA\uc624\ud0a4\uce20\ub124\x1bCZ\uc758 \uc591\uc790 \ub9d0\uc785\ub2c8\uae4c?',
    3886: '\uadf8\ub807\uac8c \ub178\uace8\uc801\uc73c\ub85c \uc2eb\uc740 \uc5bc\uad74\uc744 \ud558\uc9c0 \ub9c8\ub77c!',
    3887: '\u2026\u2026\ub0b4 \uce5c\uc815\uc774\uae30\ub3c4 \ud558\ub2e8\ub2e4?',
    3888: '\uc774\ub7f0\u2026\u2026\n\uc5b4\uba38\ub2d8, \uc8c4\uc1a1\ud569\ub2c8\ub2e4.',
    3889: '\uc790\uc720\ubd84\ubc29\ud55c \ub108\uc5d0\uac8c \ub531 \ub9de\uc9c0 \uc54a\ub290\ub0d0.\n\u2026\u2026\ud63c\uc778 \uc0c1\ub300\uae4c\uc9c0 \uc2a4\uc2a4\ub85c \uace0\ub978 \ub140\uc11d\uc774\ub2c8.',
    3890: '\ubb34\uac00\uc758 \ud63c\uc778 \uc0c1\ub300\ub294 \ubd80\ubaa8\uac00 \uc815\ud558\ub294 \uac83\uc774 \uc0c1\uc2dd\uc774\ub358\n\ub2f9\uc2dc\uc5d0\ub3c4 \x1bCA\ubaa8\ud1a0\ud558\ub8e8\x1bCZ\ub294 \uc2a4\uc2a4\ub85c \uc6d0\ud558\uc5ec\n\x1bCA\uad6c\ub9c8\uac00\uc774 \ub178\ubd80\ub098\uc624\x1bCZ\uc758 \ub538\uc744 \uc544\ub0b4\ub85c \ub9de\uc558\ub2e4.',
    3891: '\uc81c\uac00 \uc790\uc720\ubd84\ubc29\ud558\ub2e4 \ud574\ub3c4\u2026\u2026\n\x1bCA\uc624\ud0a4\uce20\ub124\x1bCZ\uc640 \ud55c\ub370 \ubb36\uc774\ub294 \uac83\uc740 \uc5b5\uc6b8\ud569\ub2c8\ub2e4!\n\ud63c\uc778\ub3c4 \uc544\ubc84\ub2d8\uaed8\uc11c \ubc18\ub300\ud558\uc2dc\uae30 \uc804\uc5d0\u2026\u2026',
    3892: '\uc88b\uc740 \uc544\uc774\uc600\uc5b4\uc694.\n\x1bCA\ubaa8\ud1a0\ud558\ub8e8\x1bCZ\ub294 \uc5ec\uc790\ub97c \ubcf4\ub294 \ub208\uc774 \ud655\uc2e4\ud558\uad70\uc694.',
    3893: '\ub108\ub3c4 \uc0dd\uac01\uc774 \uc788\ub2e4\uba74,\n\uc774\ubc88 \uc591\uc790\uac00 \ubb34\uc5c7\uc744 \ub73b\ud558\ub294\uc9c0\n\uc54c \uc218 \uc788\uc9c0 \uc54a\uaca0\ub290\ub0d0?',
    3894: '\x1bCA\uae43\uce74\uc640 \uc624\ud0a4\uce20\ub124\x1bCZ\ub294 \uacbd\uc194\ud574\ub3c4 \uc2f8\uc6c0\uc5d0\ub294 \ub2a5\ud558\ub2e4.\n\uadf8 \uac00\uc2e0\ub4e4\ub3c4 \ub9c8\ucc2c\uac00\uc9c0\u2026\u2026\ub77c\ub294 \ub73b\uc785\ub2c8\uae4c?',
    3895: '\uadf8\ub807\ub2e4.\n\ub124\uac00 \x1bCB\uae43\uce74\uc640 \uac00\ubb38\x1bCZ\uc744 \uc774\ub04c\uc5b4,\n\uc774 \x1bCA\ubaa8\ub9ac\x1bCZ\uc758 \ud654\uc0b4\uc774 \ub418\uc5b4\ub77c, \x1bCA\ubaa8\ud1a0\ud558\ub8e8\x1bCZ.',
    3896: '\x1bCA\ubaa8\ud1a0\ud558\ub8e8\x1bCZ\ub294 \uc544\ubc84\uc9c0\uc758 \uba85\uc744 \ub530\ub77c,\n\x1bCB\uae43\uce74\uc640\x1bCZ\uc758 \uc591\uc790\uac00 \ub418\uc5b4 \x1bCA\uae43\uce74\uc640 \ubaa8\ud1a0\ud558\ub8e8\x1bCZ\ub85c \uc774\ub984\uc744 \ubc14\uafe8\ub2e4.',
    3897: '\uc774\uc73d\uace0 \x1bCB\uae43\uce74\uc640 \uac00\ubb38\x1bCZ \ub2f9\uc8fc \x1bCA\uc624\ud0a4\uce20\ub124\x1bCZ\ub294\n\uac00\uc2e0\ub4e4\uc5d0\uac8c \uac15\uc81c\ub85c \uc740\uac70\ub2f9\ud588\uace0,\n\x1bCA\ubaa8\ud1a0\ud558\ub8e8\x1bCZ\uac00 \x1bCB\uae43\uce74\uc640 \uac00\ubb38\x1bCZ\uc758 \ub2f9\uc8fc\uac00 \ub418\uc790\u2026\u2026',
    3898: '\uc591\ubd80 \x1bCA\uc624\ud0a4\uce20\ub124\x1bCZ \ubabb\uc9c0\uc54a\uc740 \uc8fc\uace0\ucfe0 \uc81c\uc77c\uc758 \ubb34\uc6a9\uc73c\ub85c,\n\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc744 \ub5a0\ubc1b\uce58\uac8c \ub418\uc5c8\ub2e4.',
    3899: '\x1bCC\ubd84\uace0\x1bCZ\uc758 \ub2e4\uc774\ubb18 \x1bCA[b473]\x1bCZ \uacf5\u2015',
    3900: '\x1bCB\uc624\ud1a0\ubaa8 \uac00\ubb38\x1bCZ \uc81c20\ub300 \ub2f9\uc8fc \x1bCA\uc624\ud1a0\ubaa8 \uc694\uc2dc\uc544\ud0a4\x1bCZ\uc758 \uc801\uc790.\n\ub2e4\uc7ac\ub2e4\ub2a5\ud588\uc9c0\ub9cc,\n\ud0dc\uc5b4\ub0a0 \ub54c\ubd80\ud130 \ubcd1\uc57d\ud55c \uc778\ubb3c\uc774\uc5c8\ub2e4.',
    3901: '\uadf8\ub7f0 \x1bCA[bm473]\x1bCZ \uacf5\uc774 \uc628\ucc9c \uc694\uc591\uc744 \ub5a0\ub09c\ub2e4\uace0 \ud574\ub3c4,\n\uc218\uc0c1\ud558\uac8c \uc5ec\uae38 \uc0ac\ub78c\uc740 \uc5c6\uc5c8\ub2e4.\n\ud558\uc9c0\ub9cc \x1bCA[bm473]\x1bCZ \uacf5\uc758 \ub178\ub9bc\uc218\ub294 \ub530\ub85c \uc788\uc5c8\ub2e4.',
    3902: '\x1bCA[bm1730]\x1bCZ \uacf5, \uc0c1\ud669\uc740 \uc5b4\ub5a0\ud55c\uac00?',
    3903: '\ubaa8\ub450 \uacc4\ud68d\ub300\ub85c \uc9c4\ud589\ub418\uace0 \uc788\uc2b5\ub2c8\ub2e4\u2026\u2026',
    3904: '\ud6c4\ud6c4\ud6c4\u2026\u2026 \uadf8\ub798, \uadf8\ub798!\n\uadf8\ub807\ub2e4\uba74 \x1bCA[bm1730]\x1bCZ \uacf5, \uadf8\ub300\ub294 \x1bCA\ub274\ud0c0\x1bCZ\ub97c \uce58\ub3c4\ub85d \ud558\ub77c.',
    3905: '\uc608!\n\uacc4\ud68d\ub300\ub85c \ud558\uaca0\uc2b5\ub2c8\ub2e4.',
    3906: '\ud6c4\ud6c4\ud6c4, \ud558\ud558\ud558!\n\uc774\uc81c \x1bCB\uc624\ud1a0\ubaa8\x1bCZ\ub294 \ub0b4 \uac83\uc774\ub2e4!',
    3907: '\uc544\ubc84\ub2d8\ub3c4 \ubb34\ub974\uc2dc\uad70!\n\ub0b4\uac00 \uc774\ub7f0 \ub54c\uc5d0\n\uc628\ucc9c \ub530\uc704\uc5d0 \uac08 \ub9ac \uc5c6\uc9c0!',
    3908: '\u2026\u2026\u2026\u2026',
    3909: '\ub098\ub97c \ud3d0\uc801\ud558\ub824 \ud558\ub2e4\ub2c8\u2026\u2026 \ub108\ubb34 \ubb34\ub974\ub2e4!\n\ub098\ub294 \uc8fd\uc9c0 \uc54a\ub294\ub2e4, \uacb0\ucf54 \uc8fd\uc9c0 \uc54a\uc544.\n\uc6d0\ud558\ub294 \ubaa8\ub4e0 \uac83\uc744 \uc190\uc5d0 \ub123\uc744 \ub54c\uae4c\uc9c0!',
    3910: '(\x1bCA[bm473]\x1bCZ \uacf5\uc774 \ub54c\ub85c \ub4dc\ub7ec\ub0b4\ub294 \uc5b4\ub450\uc6b4 \ud328\uae30\u2026\u2026\n\u3000\uc774 \ub098\uc870\ucc28 \ub20c\ub9b4 \ub9cc\ud07c \uc5c4\uccad\ub098\ub2e4.)',
    3911: '(\ud558\uc9c0\ub9cc \uae30\ubcf5\uc774 \uc2ec\ud55c \ubd84\uc774\ub2e4.\n\u3000\ucc9c\ud558\ubb34\uc30d\uc758 \uc601\uac78 \uac19\uc740 \ubaa8\uc2b5\ub3c4 \uc788\uace0,\n\u3000\uc720\ud765\uc5d0 \ube60\uc9c4 \uc6a9\ub82c\ud55c \uc7a5\uc218\uc758 \ubaa8\uc2b5\ub3c4 \uc788\ub2e4\u2026\u2026)',
    3912: '(\uace0\uc090\ub97c \ub2e8\ub2e8\ud788 \uc8c4\uc5b4\uc57c\uaca0\uad70.)',
    3913: '\x1bCA[bm473]\x1bCZ \uacf5\uc758 \uc544\ubc84\uc9c0 \x1bCA\uc624\ud1a0\ubaa8 \uc694\uc2dc\uc544\ud0a4\x1bCZ\ub294 \ud3c9\uc18c\ubd80\ud130\n\x1bCA[bm473]\x1bCZ \uacf5\uc744 \uc2eb\uc5b4\ud574, \uce21\uc2e4\uc758 \uc544\ub4e4\uc5d0\uac8c\n\x1bCB\uc624\ud1a0\ubaa8 \uac00\ubb38\x1bCZ\uc744 \uc787\uac8c \ud558\ub824 \ud588\ub2e4.',
    3914: '\x1bCA[bm473]\x1bCZ \uacf5\uc740 \uc774\ub97c \uc54c\uc544\ucc44\uace0 \uc628\ucc9c \uc694\uc591\uc744 \uad6c\uc2e4\ub85c\n\ud2c8\uc744 \ub9cc\ub4e4\uc5b4 \uc815\ubcc0\uc744 \uc720\ub3c4\ud55c \ub4a4, \ud589\ub3d9\uc744 \uc77c\uc73c\ud0a8 \x1bCA\uc694\uc2dc\uc544\ud0a4\x1bCZ\ub97c\n\uc218\ud558\ub97c \uc2dc\ucf1c \ub3c4\ub9ac\uc5b4 \uc8fd\uc600\ub2e4.',
    3915: "\x1bCB\uc624\ud1a0\ubaa8\uc528\x1bCZ\uc758 \uc800\ud0dd 2\uce35\uc5d0\uc11c \uc77c\uc5b4\ub09c \uc77c\uc774\uae30\uc5d0,\n\uc774 \uc0ac\uac74\uc740 \ubcf4\ud1b5\n'\ub2c8\uce74\uc774\ucfe0\uc988\ub808\uc758 \ubcc0'\uc774\ub77c \ubd88\ub9b0\ub2e4.",
    3916: '\ud798\uc73c\ub85c \uc544\ubc84\uc9c0\ub97c \ub118\uc5b4\uc120 \x1bCA[bm473]\x1bCZ \uacf5\uc740 \x1bCB\uc624\ud1a0\ubaa8 \uac00\ubb38\x1bCZ\uc758\n\ub2f9\uc8fc\uac00 \ub418\uc5b4 \x1bCA[b1730]\x1bCZ \ub4f1 \ub6f0\uc5b4\ub09c \ubb34\uc7a5\uc744 \uac70\ub290\ub9ac\uace0,\n\ub9c8\uce68\ub0b4 \x1bCC\uaddc\uc288\x1bCZ\ub97c \uc11d\uad8c\ud574 \uac14\ub2e4\u2026\u2026',
    3917: '\uac00\ub9c8\ucfe0\ub77c \ub9c9\ubd80 \uace0\ucf00\ub2cc\uc778 \x1bCB\ub3c4\uc774\uc528\x1bCZ\uc5d0\uc11c \ube44\ub86f\ub418\uc5b4,\n\ub6f0\uc5b4\ub09c \uc218\uad70\uc744 \uac70\ub290\ub9b0 \x1bCC\uc0b0\uc694\x1bCZ\uc758 \uba85\ubb38 \x1bCB\uace0\ubc14\uc57c\uce74\uc640 \uac00\ubb38\x1bCZ\u2015',
    3918: '\x1bCB\ub204\ud0c0\x1bCZ\uc640 \x1bCB\ub2e4\ucf00\ud558\ub77c\x1bCZ \ub450 \uac00\ubb38\uc73c\ub85c \uac08\ub77c\uc9c4 \ub4a4,\n\uc80a\uc740 \ub2f9\uc8fc\ub4e4\uc774 \uc787\ub2ec\uc544 \uc8fd\uc73c\uba70 \uc138\ub825\uc774 \uc1e0\ud588\ub2e4.\n\x1bCA\ubaa8\ub9ac \ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294 \uc774\ub97c \uae30\ud68c\ub85c \ubcf4\uc558\ub2e4.',
    3919: '\x1bCB\uace0\ubc14\uc57c\uce74\uc640 \uac00\ubb38\x1bCZ\uc758 \ubb34\ub825\uc744 \ub2e4\uc2dc \uc0b4\ub9ac\ub824\uace0,\n\x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294 \x1bCA\uc624\uc6b0\uce58 \uc694\uc2dc\ud0c0\uce74\x1bCZ\uae4c\uc9c0 \ub04c\uc5b4\ub4e4\uc5ec \uc6c0\uc9c1\uc600\ub2e4.',
    3920: '\x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\uc758 \uac15\ub825\ud55c \ud6c4\uc6d0\uc744 \ubc1b\uc544,\n\x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\uc758 \uc14b\uc9f8 \uc544\ub4e4 \x1bCA\ub2e4\uce74\uce74\uac8c\x1bCZ\uac00 \uc131\uc744 \ubc14\uafb8\uace0\n\x1bCB\ub2e4\ucf00\ud558\ub77c \uace0\ubc14\uc57c\uce74\uc640 \uac00\ubb38\x1bCZ\uc758 \ub2f9\uc8fc\uac00 \ub418\uc5c8\ub2e4.',
    3921: '\ub098\ub97c \x1bCC\uc57c\ub9c8\uad6c\uce58\x1bCZ\uc5d0 \ub9e1\uae34 \ubcf4\ub78c\uc774 \uc788\uc5c8\ub2e4\u2026\u2026\n\uc544\ubc84\ub2d8\uaed8\uc11c\ub294 \uadf8\ub807\uac8c \uc0dd\uac01\ud558\uc2dc\uaca0\uc9c0\uc694?',
    3922: '\ud6c4\ud6c4\ud6c4.\n\ubd84\uba85 \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\uac00 \ub73b\ub300\ub85c \uc6c0\uc9c1\uc778 \uac83\uc740\n\x1bCA\ub2e4\uce74\uce74\uac8c\x1bCZ, \ub124\uac00 \uc788\uc5c8\uae30 \ub54c\ubb38\uc774\ub2e4.',
    3923: '\uc774\uc81c\ubd80\ud130 \uc800\ub294 \x1bCC\uc0b0\uc694\x1bCZ\ub85c \ub098\uc544\uac00,\n\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc758 \uc804\uc9c4\uc744 \uc774\ub04c\uaca0\uc2b5\ub2c8\ub2e4.',
    3924: '\uc74c\u2026\u2026\n\ub9d0\ud558\uc9c0 \uc54a\uc544\ub3c4 \uc54c\uace0 \uc788\uad6c\ub098?',
    3925: '\x1bCB\uace0\ubc14\uc57c\uce74\uc640\x1bCZ\ub97c \ub124\uac8c \ub9e1\uae34 \uac83\uc740,\n\ub124 \uc9c0\ud61c\ub97c \ubbff\uae30 \ub54c\ubb38\uc774\ub2e4.',
    3926: '\uc81c \uc7ac\uc8fc\ub294 \ubaa8\ub450 \uc544\ubc84\ub2d8\uaed8 \ubc1b\uc740 \uac83\uc785\ub2c8\ub2e4.\n\uc544\ubc84\ub2d8\ucc98\ub7fc \uacc4\ucc45\uc744 \uc798 \ubd80\ub824,\n\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc744 \uc704\ud574 \ud798\uc4f0\uaca0\uc2b5\ub2c8\ub2e4.',
    3927: '\uadf8\ub798, \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ \ub3c4\uc57d\uc758 \ud654\uc0b4\uc774 \ub418\uc5b4\ub77c!',
    3928: '\uc5bc\ub9c8 \ub4a4 \x1bCA\ub2e4\uce74\uce74\uac8c\x1bCZ\ub294 \x1bCB\ub204\ud0c0 \uace0\ubc14\uc57c\uce74\uc640 \uac00\ubb38\x1bCZ\uc758 \ub538\uc744 \ub9de\uc544,\n\x1bCB\ub450 \uace0\ubc14\uc57c\uce74\uc640 \uac00\ubb38\x1bCZ\uc744 \ud1b5\uc77c\ud558\uace0,\n\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc744 \ub5a0\ubc1b\uce60 \uc218\uad70\ub825\uc744 \uc190\uc5d0 \ub123\uc5c8\ub2e4.',
    3929: '\uadf8\ub9ac\uace0 \uc218\uad70\ubfd0 \uc544\ub2c8\ub77c\n\x1bCA\ub2e4\uce74\uce74\uac8c\x1bCZ\ub294 \uc9c0\ub7b5\uc73c\ub85c \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc758 \uc138\ub825\uc744\n\x1bCC\uc0b0\uc694\x1bCZ \ubc29\uba74\uc73c\ub85c \ub113\ud788\ub294 \uc784\ubb34\ub3c4 \ub9e1\uc558\ub2e4\u2026\u2026',
    3930: '\x1bCC\uac00\uc774\x1bCZ\uc758 \uc804\uad6d \ub2e4\uc774\ubb18 \x1bCA[b1251]\x1bCZ \uacf5\uc774\n\ubcf8\uaca9\uc801\uc73c\ub85c \uce68\uacf5\uc744 \uc2dc\uc791\ud55c \uc9c0 \uba87 \ud574,\n\x1bCC\uc2dc\ub098\ub178\x1bCZ\ub294 \ucc28\uce30 \x1bCB\ub2e4\ucf00\ub2e4 \uac00\ubb38\x1bCZ\uc5d0 \uc7a0\uc2dd\ub418\uace0 \uc788\uc5c8\ub2e4\u2026\u2026',
    3931: '\x1bCC\uc2e0\uc288\x1bCZ\ub294 \uc6b0\ub9ac\uc758 \ub545\uc774\ub2e4.\n\x1bCA[bm1251]\x1bCZ \uacf5\uc758 \ub73b\ub300\ub85c \ub450\uc9c0\ub294 \uc54a\uaca0\ub2e4!',
    3932: '\x1bCC\uc2dc\ub098\ub178\x1bCZ\uc758 \uc5ec\ub7ec \uc138\ub825 \uac00\uc6b4\ub370,\n\ubc18\x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\uc758 \uae30\uce58\ub97c \ub4e0 \uc774\ub294 \uc608\ubd80\ud130 \x1bCC\uc2e0\uc288\x1bCZ\ub97c \ub2e4\uc2a4\ub9b0\n\x1bCB\ubb34\ub77c\uce74\ubbf8 \uac00\ubb38\x1bCZ\uc758 \x1bCA\uc694\uc2dc\ud0a4\uc694\x1bCZ\uc600\ub2e4.',
    3933: '\x1bCA\uc694\uc2dc\ud0a4\uc694\x1bCZ\ub294 \uc77c\ucc0d\uc774 \x1bCC\uc6b0\uc5d0\ub2e4\ud558\ub77c\x1bCZ\uc5d0\uc11c \x1bCA[bm1251]\x1bCZ \uacf5\uc758\n\uad70\uc744 \uaebe\uc5b4, \x1bCA[bm1251]\x1bCZ \uacf5\uc5d0 \ub9de\uc124 \ub73b\uc774\n\x1bCB\uc2dc\ub098\ub178 \ubb34\uc0ac\ub4e4\x1bCZ \uac00\uc6b4\ub370\uc11c\ub3c4 \ud2b9\ud788 \uac15\ud588\ub2e4.',
    3934: '\x1bCA\ubb34\ub77c\uce74\ubbf8 \uc694\uc2dc\ud0a4\uc694\x1bCZ\ub9cc \uc4f0\ub7ec\ub728\ub9ac\uba74,\n\x1bCC\uc2dc\ub098\ub178 \uc911\ubd80\x1bCZ\uc640 \x1bCC\uc2dc\ub098\ub178 \ubd81\ubd80\x1bCZ\uc758 \uc138\ub825\uc740 \uc800\uc808\ub85c \ub530\ub978\ub2e4.\n\x1bCA\uc694\uc2dc\ud0a4\uc694\x1bCZ\ub97c \ucca0\uc800\ud788 \uc9d3\ubc1f\uc544 \uc8fc\ub9c8!',
    3935: '\x1bCA[bm1251]\x1bCZ \uacf5\uc740 \ub300\uad70\uc744 \uc774\ub04c\uace0,\n\x1bCA\uc694\uc2dc\ud0a4\uc694\x1bCZ\uac00 \ub2e4\ub978 \ubc29\uba74\uc5d0 \ucd9c\ubcd1\ud55c \ud2c8\uc744 \ud0c0,\n\x1bCC\uce58\uc774\uc0ac\uac00\ud0c0\x1bCZ\uc758 \uc694\ucda9 \x1bCC\ub3c4\uc774\uc2dc\uc131\x1bCZ\uc5d0 \ub2e4\uac00\uac14\ub2e4.',
    3936: '\x1bCA[bm1251]\x1bCZ \uacf5\uc758 \uadf8\uac04 \uc804\uacfc\uc640\n\uc804\ub7b5\xb7\uacbd\ud5d8\uc744 \uc0dd\uac01\ud558\uba74 \x1bCC\ub3c4\uc774\uc2dc\uc131\x1bCZ\ucbe4\uc740\n\uc27d\uac8c \ud568\ub77d\ub420 \ub4ef\ud588\ub2e4. \uadf8\ub7ec\ub098\u2026\u2026',
    3937: '\x1bCA[bm1251]\x1bCZ \ub188\uc774 \uc654\uad6c\ub098!\n\uc989\uc2dc \x1bCC\ub3c4\uc774\uc2dc\uc131\x1bCZ\uc73c\ub85c \uac04\ub2e4!',
    3938: '\x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ\uc758 \ub0b4\uc2b5\uc744 \ub4e4\uc740 \x1bCA\ubb34\ub77c\uce74\ubbf8 \uc694\uc2dc\ud0a4\uc694\x1bCZ\ub294 \uc989\uc2dc\n\uad70\uc744 \ub3cc\ub824 \x1bCC\ub3c4\uc774\uc2dc\uc131\x1bCZ \uad6c\uc6d0\uc5d0 \ub098\uc130\ub2e4.',
    3939: '\x1bCA\uc694\uc2dc\ud0a4\uc694\x1bCZ \ub188, \uc0dd\uac01\ubcf4\ub2e4 \uc6c0\uc9c1\uc784\uc774 \ube60\ub974\uad70.\n\ud558\uc9c0\ub9cc \uadf8\uac00 \ub3cc\uc544\uc624\uae30 \uc804\uc5d0\n\uc131\uc744 \ub5a8\uc5b4\ub728\ub9ac\uba74 \uadf8\ub9cc\uc774\ub2e4!',
    3940: '\ud558\uc9c0\ub9cc \uc131\ubcd1\ubcf4\ub2e4 \uc5f4 \ubc30 \ub9ce\uc740 \x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ\ub3c4\n\x1bCC\ub3c4\uc774\uc2dc\uc131\x1bCZ\uc744 \uc880\ucc98\ub7fc \ud568\ub77d\ud558\uc9c0 \ubabb\ud588\ub2e4.\n\x1bCA[bm1251]\x1bCZ \uacf5\uc758 \ucd08\uc870\ud568\uc740 \ucee4\uc838\ub9cc \uac14\ub2e4\u2026\u2026',
    3941: '\x1bCC\ub3c4\uc774\uc2dc\uc131\x1bCZ\uacfc \x1bCB\ubb34\ub77c\uce74\ubbf8\x1bCZ \ubcd1\uc0ac\ub97c \uc595\ubcf4\uc558\uad6c\ub098!\n\x1bCA[b1251]\x1bCZ! \uc5ec\uae30\uc11c \ub124\ub188\uc744 \uce58\uaca0\ub2e4!',
    3942: '\ud06c\uc73d!',
    3943: '\uc608\uc0c1\ubcf4\ub2e4 \ube68\ub9ac \ub3c4\ucc29\ud55c \x1bCA\ubb34\ub77c\uce74\ubbf8 \uc694\uc2dc\ud0a4\uc694\x1bCZ\ub294\n\x1bCC\ub3c4\uc774\uc2dc\uc131\x1bCZ \ubcd1\uc0ac\ub4e4\uacfc \ud568\uaed8 \x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ\uc744 \ud611\uacf5\ud588\uace0,\n\x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ\uc740 \ud06c\uac8c \ud63c\ub780\uc5d0 \ube60\uc838 \ubb3c\ub7ec\ub0ac\ub2e4.',
    3944: '\x1bCA\ubb34\ub77c\uce74\ubbf8 \uc694\uc2dc\ud0a4\uc694\x1bCZ\u2026\u2026 \uc81c\ubc95\uc774\uad6c\ub098!\n\x1bCC\uc6b0\uc5d0\ub2e4\ud558\ub77c\x1bCZ\uc5d0 \uc774\uc5b4 \uc5ec\uae30\uc11c\ub3c4 \ub098\ub97c \uad34\ub86d\ud788\ub2e4\ub2c8.\n\ucc38\uc73c\ub85c \ub0b4 \uc219\uc801\uc774\ub2e4\u2026\u2026',
    3945: "\ubf08\uc544\ud508 \ud328\ubc30\ub97c \ub2f9\ud55c \x1bCB\ub2e4\ucf00\ub2e4 \uce21\x1bCZ\uc740\n\uc774 \uc2f8\uc6c0\uc744 '\ub3c4\uc774\uc2dc \ubd95\uad34'\ub77c \ubd88\ub800\ub2e4\uace0 \ud55c\ub2e4\u2026\u2026",
    3946: '\x1bCB\uc544\ud0a4 \ubaa8\ub9ac\uc528\x1bCZ\ub294 \uace0\ucf00\ub2cc \x1bCB\uc624\uc5d0\uc528\x1bCZ\uc758 \ud6c4\uc608. \uc804\uad6d \uc911\uae30\uae4c\uc9c0\n\uc8fc\ubcc0 \uc138\ub825\uc5d0 \ud718\ub458\ub9ac\ub358 \uc77c\uc871\uc774\uc5c8\ub2e4.',
    3947: '\uc774\uc73d\uace0 \uac19\uc740 \uc57d\uc18c \uace0\ucfe0\uc9c4\ub4e4\uc744 \ubaa8\uc544,\n\uac70\ub300 \uc138\ub825\uc5d0 \ub9de\uc11c\uac8c \ub418\uc5c8\uace0,\n\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc740 \x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ \ub300\uc5d0 \ud06c\uac8c \ub3c4\uc57d\ud588\uc9c0\ub9cc\u2026\u2026',
    3948: '\uac00\ubb38\uc5d0\ub294 \ud55c\ub54c \x1bCA\ubaa8\ub9ac\x1bCZ\uc640 \ub3d9\uaca9\uc774\ub358 \uace0\ucfe0\uc9c4\ub3c4 \uc788\uc5b4,\n\uc8fc\uad70\uc774\ub77c \ud574\ub3c4 \uadf8\ub4e4\uc744 \uac15\uad8c\uc73c\ub85c \ub2e4\uc2a4\ub9b4 \ub9cc\ud07c\n\x1bCA\ubaa8\ub9ac\x1bCZ\uc758 \uc6b0\uc704\ub294 \ud655\uace0\ud558\uc9c0 \uc54a\uc558\ub2e4.',
    3949: '\n\uadf8\uc911 \x1bCA\uc774\ub178\uc5d0 \ubaa8\ud1a0\uce74\ub124\x1bCZ \uc77c\ud30c\ub294 \x1bCA\ubaa8\ub9ac\x1bCZ\uc758 \uac00\uc2e0\uc774\uba74\uc11c\ub3c4,\n\ud6a1\ud3ec\ub97c \uc790\uc8fc \ubd80\ub838\uace0,\n\uc8fc\uac00\uc758 \uba85\ub839\ub3c4 \ub4e3\uc9c0 \uc54a\uc558\ub2e4.',
    3950: '\uadf8\ub7f0\uac00.\n\uc0ac\ucc30\uacfc \uc2e0\uc0ac \uc601\uc9c0\uc758 \ub17c\ubc2d\uc744 \uba4b\ub300\ub85c\u2026\u2026\n\uc2ec\uac01\ud55c \uc77c\uc774\ub85c\uad70.\n\n',
    3951: '\uc608!\n\x1bCB\uc774\ub178\uc5d0 \uc77c\ud30c\x1bCZ\ub294 \uc0ac\ucc30 \uc601\uc9c0\ub9cc\uc774 \uc544\ub2c8\ub77c,\n\ub2e4\ub978 \uac00\uc2e0\uc758 \uc601\uc9c0\uae4c\uc9c0 \ube7c\uc557\uace0 \uc788\uc2b5\ub2c8\ub2e4\u2026\u2026',
    3952: '\uc601\uc9c0 \uac15\ud0c8\uc744 \ub9c9\uc73c\ub824\ub358 \ubb34\uc0ac\uae4c\uc9c0\n\uc8fd\uc600\ub2e4\uace0 \ud569\ub2c8\ub2e4!',
    3953: '\uadf8 \uc9c0\uacbd\uc774\uba74 \ub354\ub294 \ub0b4\ubc84\ub824 \ub458 \uc218 \uc5c6\uad70\u2026\u2026\n\uc6b0\uc120 \x1bCA\uc774\ub178\uc5d0 \ubaa8\ud1a0\uce74\ub124\x1bCZ\ub97c \ud3c9\uc815 \uc790\ub9ac\uc5d0 \ubd80\ub974\uc790.\n\uc0ac\ub78c\ub4e4 \uc55e\uc5d0\uc11c \ub0b4\uac00 \uc9c1\uc811 \ud0c0\uc774\ub974\uaca0\ub2e4.',
    3954: '\x1bCB\uc774\ub178\uc5d0 \uc77c\ud30c\x1bCZ \ud6a1\ud3ec\ub97c \ub9c9\uc73c\ub824 \x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294 \x1bCA\ubaa8\ud1a0\uce74\ub124\x1bCZ\ub97c \ubd88\ub800\uc73c\ub098,\n\x1bCA\ubaa8\ud1a0\uce74\ub124\x1bCZ\ub294 \uac16\uc740 \ud551\uacc4\ub97c \ub300\uba70 \ub4f1\uc131\uc744 \uac70\ubd80\ud588\ub2e4\u2026\u2026',
    3955: '\uc774\ub7f0, \ub4f1\uc131 \uba85\ub839\uc870\ucc28 \ub4e3\uc9c0 \uc54a\ub294\uac00.\n\uc5b4\uca54 \uc218 \uc5c6\uad70. \uc5ec\uae30\uc11c\ub294 \uc545\uadc0\uac00 \ub418\uc5b4\uc57c\uaca0\uc5b4\u2026\u2026',
    3956: '\x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294 \ubab0\ub798 \uc790\uac1d\uc744 \ubcf4\ub0b4 \x1bCA\uc774\ub178\uc5d0 \ubaa8\ud1a0\uce74\ub124\x1bCZ\ub97c \uc554\uc0b4\ud588\ub2e4.\n\uc774\uc5b4 \ub3d9\uc694\ud55c \x1bCB\uc774\ub178\uc5d0 \uc77c\ud30c\x1bCZ\uc758 \uc800\ud0dd\uc744 \uae09\uc2b5\ud574,\n\uc77c\uc871 30\uc5ec \uba85\uc744 \ub2e8\uc228\uc5d0 \uc219\uccad\ud588\ub2e4.',
    3957: '\uadf8 \ub4a4 \x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294 \uac00\ubb38\uc5d0 \ubb38\uc11c\ub97c \ubc18\ud3ec\ud574,\n\x1bCB\uc774\ub178\uc5d0 \uc77c\ud30c\x1bCZ\uc758 \uc8c4\ubaa9\uc744 \ubb34\ub824 11\uac1c\ub098 \uc5f4\uac70\ud558\uace0,\n\uadf8\ub4e4\uc758 \uc798\ubabb\uc744 \ub300\ub300\uc801\uc73c\ub85c \uc54c\ub838\ub2e4.',
    3958: '\uc804\uad11\uc11d\ud654 \uac19\uc740 \uc219\uccad\uc5d0\n\x1bCA\ubaa8\ub9ac\x1bCZ \uac00\uc2e0\ub4e4\uc740 \ub5a8\uc5c8\uace0, 200\uba85\uc774 \ub118\ub294 \uc774\ub4e4\uc774\n\x1bCA\ubaa8\ub9ac\x1bCZ\uc5d0\uac8c \ucda9\uc131\uc744 \ub9f9\uc138\ud558\ub294 \uc11c\uc57d\uc11c\ub97c \uc62c\ub838\ub2e4.',
    3959: '\uc774\ub7f0, \uc774\ub7f0\u2026\u2026 \uc783\uc740 \uac83\ub3c4 \ub9ce\uc558\uc9c0\ub9cc,\n\uc774\uc81c \uac00\ubb38\uc774 \ub2e4\uc7a1\ud790\uc9c0 \ubaa8\ub974\uaca0\uad70.\n\ube44 \uc628 \ub4a4 \ub545\uc774 \uad73\uc73c\uba74 \uc88b\uc73c\ub828\ub9cc.',
    3960: '\uad50\ubb18\ud55c \uc218\uc600\uc9c0\ub9cc,\n\uc5b4\ub514\uae4c\uc9c0\ub098 \x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\uc758 \ube44\uc815\ud55c \uacb0\ub2e8\uc73c\ub85c,\n\x1bCB\uc774\ub178\uc5d0 \uc77c\ud30c\x1bCZ\uc758 \uc601\ud5a5\ub825\uc740 \uac00\ubb38\uc5d0\uc11c \uc0ac\ub77c\uc84c\ub2e4.',
    3961: '\uc5ec\ub7ec \uc138\ub825\uc774 \ub4a4\uc11e\uc778 \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc774\n\uc804\uad6d \ub2e4\uc774\ubb18\ub85c \uad8c\ub825\uc744 \uc9d1\uc911\ud558\ub824\uba74,\n\ud53c\ud560 \uc218 \uc5c6\ub294 \uae38\uc774\uc5c8\ub358 \uac83\uc77c\uae4c\u2026\u2026',
    3962: '\uac13\uc0b0\ud1a0\ub2e4\uc131 \uc804\ud22c\uc5d0\uc11c \ub300\ud328\ud55c \x1bCA\uc624\uc6b0\uce58 \uc694\uc2dc\ud0c0\uce74\x1bCZ\ub294\n\uc815\ubb34\uc5d0 \ud765\ubbf8\ub97c \uc783\uace0 \uc720\ud765\uc5d0 \ube60\uc84c\uc73c\uba70,\n\ubc31\uc131\uc5d0\uac8c\ub3c4 \ubb34\uac70\uc6b4 \ubd80\ub2f4\uc744 \uc9c0\uc6e0\ub2e4\u2026\u2026',
    3963: '\uc8fc\uad70, \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc740 \x1bCC\uc0ac\uc774\uace0\ucfe0\x1bCZ \uc81c\uc77c\uc758 \ub300\ub2e4\uc774\ubb18\uc785\ub2c8\ub2e4.\n\uc640\uce74\uc640 \ub2e4\ud68c\ub3c4 \uc88b\uc9c0\ub9cc,\n\ubb34\uc0ac\uc758 \ubcf8\ubd84\uc740 \ubb34\uc608\uc784\uc744 \uc78a\uc9c0 \ub9c8\uc2ed\uc2dc\uc624\u2026\u2026',
    3964: '\x1bCA\ub2e4\uce74\ud6c4\uc0ac\x1bCZ\uc778\uac00, \uc2dc\ub044\ub7fd\uad6c\ub098.\n\ub098\ub294 \uc544\ubb34\ub798\ub3c4 \uc2f8\uc6c0\uc5d0\ub294 \ub9de\uc9c0 \uc54a\ub294 \ub4ef\ud558\ub2e4.\n\uad70\ubb34\ub294 \ub124\uac8c \ub9e1\uae30\uaca0\ub2e4.',
    3965: '\uc2f8\uc6c0\ub3c4 \uc911\uc694\ud558\uc9c0\ub9cc,\n\ubb38\ud654\ub97c \ud0a4\uc6b0\uace0 \uc9c0\ud0a4\ub294 \uac83\ub3c4 \ub2e4\uc774\ubb18\uc758 \uc911\uc694\ud55c \uc5ed\ud560\uc774\uc624.\n\uadf8\ub9ac \ub208\uc744 \ubd80\ub985\ub730 \uc77c\uc740 \uc544\ub2c8\uc9c0 \uc54a\uc18c\u2026\u2026',
    3966: '(\u2026\u2026\uc8fc\uad70 \uacc1\uc758 \ubb38\uc57d\ud55c \ubb34\ub9ac\ub4e4\uc774,\n\u3000\uc8fc\uad70\uc744 \ub354\uc6b1 \ubb34\ub974\uac8c \ub9cc\ub4e4\uace0 \uc788\ub2e4.\n\u3000\uc774\ub300\ub85c\uba74 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc758 \uc55e\ub0a0\uc740 \uc5b4\ub461\ub2e4.)',
    3967: '\x1bCA\uc2a4\uc5d0 \ub2e4\uce74\ud6c4\uc0ac\x1bCZ\ub294 \x1bCB\uc624\uc6b0\uce58\x1bCZ\uc758 \uc55e\ub0a0\uc744 \uac71\uc815\ud574 \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\uc758 \uc870\uce74\n\x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\ub97c \x1bCB\uc624\ud1a0\ubaa8\x1bCZ\uc5d0\uc11c \x1bCC\uc57c\ub9c8\uad6c\uce58\x1bCZ\ub85c \ubab0\ub798 \ubd88\ub800\ub2e4\u2026\u2026',
    3968: '\x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\ub294 \x1bCA\uc694\uc2dc\uc544\ud0a4\x1bCZ\xb7\x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ \ub204\uc774\uc758 \uc544\ub4e4. \x1bCA\uadf8\x1bCZ\uc758 \uc591\uc790\uc600\ub2e4\uac00 \x1bCA\uadf8\x1bCZ\uc5d0\uac8c \uce5c\uc790\uac00 \uc0dd\uaca8 \x1bCB\uc624\ud1a0\ubaa8\x1bCZ\ub85c \ub3cc\uc544\uac14\ub2e4.',
    3969: '\ubab0\ub798 \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\uc758 \ud6c4\uacc4\uc790\ub97c \ub9c8\ub828\ud55c \x1bCA\ub2e4\uce74\ud6c4\uc0ac\x1bCZ\ub294,\n\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc744 \ub530\ub974\ub358 \x1bCA\ubaa8\ub9ac \ubaa8\ud1a0\ub098\ub9ac\x1bCZ \ub4f1\uc758 \uc9c0\uc9c0\ub3c4 \uc5bb\uc5b4,\n\ucc29\ucc29 \uc8fc\uac00 \uc804\ubcf5 \uacc4\ud68d\uc744 \ub2e4\ub4ec\uc5c8\ub2e4\u2026\u2026',
    3970: '\uadf8\ub9ac\uace0 \uc5b4\ub290 \ub0a0\u2026\u2026\n\ub9c8\uce68\ub0b4 \x1bCA\ub2e4\uce74\ud6c4\uc0ac\x1bCZ\ub294 \x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\ub97c \ubc1b\ub4e4\uc5b4 \uac70\ubcd1\ud588\ub2e4.\n\uc21c\uc2dd\uac04\uc5d0 \uc5ec\ub7ec \uc131\uc744 \ud3c9\uc815\ud558\uace0 \x1bCC\uc57c\ub9c8\uad6c\uce58\x1bCZ\ub85c \ub2e4\uac00\uac14\ub2e4.',
    3971: '\x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ \ub2d8\uaed8\uc11c\ub294 \uc740\uac70\ud558\uc2dc\uace0,\n\uc18d\ud788 \x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ \ub2d8\uaed8 \uac00\ub3c5\uc744 \ub118\uae30\uc2ed\uc2dc\uc624!\n\uc774 \ubaa8\ub450\uac00 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc744 \uc704\ud574\uc11c\uc785\ub2c8\ub2e4.',
    3972: '\uc5b4, \uc5b4\ub9ac\uc11d\uc740 \uc18c\ub9ac \ub9c8\ub77c!\n\ub124\uac00 \ubc1b\ub4dc\ub294 \x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\ub294 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ \ub2f9\uc8fc\uc758 \uadf8\ub987\uc774 \uc544\ub2c8\ub2e4!\n\x1bCB\uc624\uc6b0\uce58\x1bCZ\ub97c \uc704\ud55c \uc77c\uc774 \ub420 \ub9ac \uc5c6\ub2e4!',
    3973: '\uc801\uc5b4\ub3c4 \uc720\ud765\uc5d0\ub9cc \ube60\uc9c4 \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ \ub2d8\ubcf4\ub2e4\ub294,\n\uc81c\uac00 \ud558\ub294 \ub9d0\uc744 \ubaa8\ub450 \ubc1b\uc544\ub4e4\uc774\ub294\n\x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ \ub2d8\uc774 \x1bCB\uc624\uc6b0\uce58\x1bCZ\ub97c \uc704\ud574 \ub354 \ub0ab\uaca0\uc9c0\uc694\u2026\u2026',
    3974: '\x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\ub97c \uaf2d\ub450\uac01\uc2dc\ub85c \uc0bc\uc544,\n\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc744 \ub124 \uac83\uc73c\ub85c \ub9cc\ub4e4 \uc148\uc774\ub0d0!',
    3975: '\uc5b4\ub5bb\uac8c \uc0dd\uac01\ud558\uc2dc\ub4e0 \uc0c1\uad00\uc5c6\uc2b5\ub2c8\ub2e4.\n\uc81c\uac8c\ub294 \uc774\uac83\uc774\uc57c\ub9d0\ub85c,\n\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc5d0 \ucda9\uc131\uc744 \ub2e4\ud558\ub294 \uae38\uc785\ub2c8\ub2e4.',
    3976: '\ub124\uac00 \uc774\ub7f0 \uc0ac\ub0b4\uc600\ub2e4\ub2c8\u2026\u2026\n\ub0b4\uac00 \uc798\ubabb \ubcf4\uc558\ub358 \uac83\uc778\uac00!',
    3977: '\ud6c4\ud6c4\ud6c4\u2026\u2026 \x1bCB\uc624\uc6b0\uce58\x1bCZ\uc5d0 \ud544\uc694\ud55c \uac74 \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\uac00 \uc544\ub2cc \x1bCA\ub2e4\uce74\ud6c4\uc0ac\x1bCZ\ub2e4!\n\uc790, \uac00\ub3c5\uc744 \ub118\uae30\uc2dc\uc624!',
    3978: '\ud06c\uc73d\u2026\u2026\n\uc774\ub807\uac8c \ud3ec\uc704\ub418\uc5c8\uc73c\ub2c8 \ub2ec\uc544\ub0a0 \uc218 \uc5c6\ub098!',
    3979: '\ud3ec\uae30\ud558\uc2dc\uba74 \uc548 \ub429\ub2c8\ub2e4!\n\uc790, \uc774\ucabd\uc73c\ub85c!',
    3980: '\uc11c\ub77c!\n\ub193\uce58\uc9c0 \uc54a\uaca0\ub2e4!',
    3981: '\x1bCA\ub2e4\uce74\ud1a0\uc694\x1bCZ\uc758 \ubd84\uc804\uc73c\ub85c \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\ub294 \ud3ec\uc704\ub97c \ub6ab\uc5c8\ub2e4.\n\x1bCB\uc2a4\uc5d0\uad70\x1bCZ\uc744 \ud53c\ud574 \x1bCC\ub098\uac00\ud1a0\x1bCZ\uc758 \x1bCC\ub2e4\uc774\ub124\uc774\uc9c0\x1bCZ\ub85c \uac14\uc73c\ub098 \ub2e4\uc2dc \ud3ec\uc704\ub410\ub2e4.',
    3982: '\x1bCA\ub2e4\uce74\ud1a0\uc694\x1bCZ\u2026\u2026 \uc774\uc81c \ub410\ub2e4. \uc5ec\uae30\uae4c\uc9c0\ub2e4.\n\ub098\ub294 \uc774\uacf3\uc5d0\uc11c \ud560\ubcf5\ud558\uaca0\ub2e4\u2026\u2026 \uac00\uc774\uc0e4\ucfe0\ud574 \ub2e4\uc624.\n\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc758 \uc5ed\uc0ac\ub3c4 \uc5ec\uae30\uc11c \ub05d\uc774\ub2e4!',
    3983: "'\uce58\ub294 \uc790\uc640 \ub9de\ub294 \uc790 \ubaa8\ub450\u2026\u2026\n\u3000\uc774\uc2ac\uacfc \uac19\uace0 \ubc88\uac1c\uc640 \uac19\uc73c\ub2c8,\n\u3000\ub9c8\ub545\ud788 \uc774\uc640 \uac19\uc774 \ubcfc\uc9c0\uc5b4\ub2e4.'",
    3984: '\uc8fc\uad70\u2015!',
    3985: '\ubb50\ub77c\uace0, \uc790\uacb0\ud558\uc168\ub2e4\u2026\u2026!?\n\uadf8, \uadf8\ub7f0\uac00\u2026\u2026',
    3986: '\x1bCA\ub2e4\uce74\ud6c4\uc0ac\x1bCZ\ub294 \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\uac00 \x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\uc5d0\uac8c \uac00\ub3c5\uc744 \ub118\uae30\uace0\n\uc740\uac70\ud558\uae30\ub9cc\uc744 \ubc14\ub790\uc9c0 \ubaa9\uc228\uae4c\uc9c0 \ube7c\uc557\uc744 \uc0dd\uac01\uc740 \uc5c6\uc5c8\uae30\uc5d0,\n\uc8fc\uad70\uc758 \uc790\uacb0 \uc18c\uc2dd\uc5d0 \ub3d9\uc694\ud588\ub2e4.',
    3987: '\uadf8\ub7ec\ub098 \ub3d9\uc694\ub294 \ud55c\uc21c\uac04\ubfd0\uc774\uc5c8\ub2e4.\n\uadf8 \ub4a4\ub85c\ub294 \ub2f4\ub2f4\ud788 \uc0ac\ud6c4 \ucc98\ub9ac\ub97c \uc9c4\ud589\ud574,\n\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc744 \ud3c9\uc628\ud55c \uc0c1\ud0dc\ub85c \ub418\ub3cc\ub838\ub2e4.',
    3988: "\x1bCA\ub2e4\uce74\ud6c4\uc0ac\x1bCZ\ub294 \x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\uc5d0\uac8c \ud55c \uc790\ub97c \ubc1b\uc544 \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\ub85c \uace0\ucce4\uace0,\n\x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\ub294 \uc1fc\uad70\uc5d0\uac8c '\uc694\uc2dc'\ub97c \ubc1b\uc544,\n\x1bCA\uc694\uc2dc\ub098\uac00\x1bCZ\ub85c \uc774\ub984\uc744 \ubc14\uafe8\ub2e4.",
    3989: '\ud558\uc9c0\ub9cc \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\uc758 \uac15\uc555\uc801\uc778 \ubc29\uc2dd\uc740 \ub9c8\ucc30\uc744 \ubd88\ub800\uace0,\n\uc61b \uc8fc\uad70\uc744 \uc8fd\uc74c\uc73c\ub85c \ubab0\uc558\ub2e4\ub294 \ube44\ud310\uae4c\uc9c0 \uacb9\uccd0,\n\x1bCA\ubaa8\ub9ac \ubaa8\ud1a0\ub098\ub9ac\x1bCZ \ub4f1\uc758 \uc9c0\uc9c0\ub97c \uc783\uc5b4 \uac14\ub2e4.',
    3990: '\x1bCA\ub2e4\uce74\ud6c4\uc0ac\x1bCZ\uc5d0\uc11c \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\ub85c \uc774\ub984\uc744 \ubc14\uafbc \uadf8\uc758 \uc0dd\uac01\uacfc \ub2ec\ub9ac,\n\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc740 \uc774\ud6c4 \ub354 \uae4a\uc740 \ub3d9\ub780\uc758 \uc18c\uc6a9\ub3cc\uc774\uc5d0\n\ud718\ub9d0\ub824 \uac14\ub2e4\u2026\u2026',
    3991: '\x1bCB\ud6c4\ucd94 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uacfc \x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ \ub2f9\uc8fc\ub294\n\uc624\ub79c \ub2e4\ud23c\uc744 \ub05d\ub0c8\uace0, \ud654\ud574\uc758 \uc99d\ud45c\ub85c\n\ud63c\uc778\uc744 \ucd94\uc9c4\ud588\ub2e4.',
    3992: '\ub204\ub2d8, \uc8c4\uc1a1\ud569\ub2c8\ub2e4.\n\x1bCA[bm1448]\x1bCZ \uacf5\uc740 \ub204\ub2d8\uc744 \uc815\ub7b5\uc758 \ub3c4\uad6c\ub85c \uc0bc\uc744 \uc0dd\uac01\uc740\n\ucd94\ud638\ub3c4 \uc5c6\uc2b5\ub2c8\ub2e4\ub9cc\u2026\u2026',
    3993: '\uc54c\uace0 \uc788\ub2e8\ub2e4, \x1bCA[bm1448]\x1bCZ \uacf5.\n\ub098\ub294 \uc774\ubc88 \ud63c\uc778\uc744\n\uacb0\ucf54 \ubd80\uc815\uc801\uc73c\ub85c \uc0dd\uac01\ud558\uc9c0 \uc54a\uc544.',
    3994: '\uc624\ub77c\ubc84\ub2c8\uc640 \x1bCA[bm1448]\x1bCZ \uacf5\uc744 \ub2e4\ub904 \uc9c0\uc704\ub97c \uad73\ud78c \x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\n\ub2d8\uc774 \ub0b4 \ub0a8\ud3b8\uc774\ub77c\ub2c8\u2026\u2026 \uc720\ucf8c\ud558\uc9c0 \uc54a\uaca0\ub2c8?',
    3995: '\x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\ub294 \ubc29\uc2ec\ud560 \uc218 \uc5c6\ub294 \uc0ac\ub0b4\uc9c0\ub9cc,\n\x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc5d0 \uc5c6\uc5b4\uc11c\ub294 \uc548 \ub420 \uc778\uc7ac\uc774\uae30\ub3c4 \ud569\ub2c8\ub2e4.',
    3996: '\ub204\ub2d8\uc740 \ubb3c\ub860, \uc774\uc81c \ub9e4\ud615\uc774 \ub420 \x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ \uacf5\ub3c4\n\x1bCA[bm1448]\x1bCZ \uacf5\uc774 \uacb0\ucf54 \uc18c\ud640\ud788 \ub300\ud558\uc9c0 \uc54a\uaca0\uc2b5\ub2c8\ub2e4.\n\ub9c8\uc74c \ud3b8\ud788 \uc2dc\uc9d1\uac00 \uc8fc\uc2ed\uc2dc\uc624\u2026\u2026',
    3997: '\uadf8\ub9ac\ud558\uc5ec \x1bCA[bm1448]\x1bCZ \uacf5\uc758 \ub204\uc774 \x1bCA\uc13c\ud1a0\uc778\x1bCZ\uc740\n\x1bCB\uc6b0\uc5d0\ub2e4 \uac00\ubb38\x1bCZ \ub2f9\uc8fc \x1bCA\ub098\uac00\uc624 \ub9c8\uc0ac\uce74\uac8c\x1bCZ\uc5d0\uac8c \uc2dc\uc9d1\uac14\ub2e4\u2026\u2026',
    3998: '\ubd80\uc871\ud55c \uc0ac\ub78c\uc774\uc624\ub098,\n\uc798 \ubd80\ud0c1\ub4dc\ub9bd\ub2c8\ub2e4.',
    3999: '\uc74c. \ub098\uc57c\ub9d0\ub85c \uc798 \ubd80\ud0c1\ud558\uc624.\n\ub2f9\uc8fc\uc758 \ub204\uc774\ub97c \uc544\ub0b4\ub85c \ub9de\ub294 \uac83\uc774\ub2c8,\n\ub098\ub3c4 \uc88b\uc740 \ub0a8\ud3b8\uc774 \ub418\ub3c4\ub85d \ud798\uc4f0\uaca0\uc18c.',
    4000: '\uc5b4\uba38.\n\uadf8\ub807\ub2e4\uba74 \uc800\ub3c4 \uc88b\uc740 \uc544\ub0b4\uac00 \ub418\uaca0\uc2b5\ub2c8\ub2e4.\n\ud6c4\ud6c4\ud6c4\u2026\u2026',
    4001: '\x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\ub294 \uc815\uc2dd\uc73c\ub85c \uc8fc\uad70 \x1bCA[b1448]\x1bCZ \uacf5\uc758 \ub9e4\ud615\uc774 \ub418\uc5b4,\n\uc774\ud6c4 \uc77c\ubb38\uc911\uc758 \uc2e4\ub825\uc790\ub85c \ud65c\uc57d\ud588\ub2e4.',
    4002: '\uc815\ub7b5\uc73c\ub85c \ub9fa\uc5b4\uc84c\uc9c0\ub9cc \x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\uc640 \x1bCA\uc13c\ud1a0\uc778\x1bCZ\uc740 \uae08\uc2ac\uc774 \uc88b\uc558\uace0,\n\ub450 \uc0ac\ub78c \uc0ac\uc774\uc5d0\ub294 \ub450 \uc544\ub4e4\uacfc \ub450 \ub538\uc774 \ud0dc\uc5b4\ub0ac\ub2e4\u2026\u2026',
    4003: '\uc5d0\uad6c\uce58 \uc804\ud22c\uc5d0\uc11c \x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ\uc758 \uad70\uc138\ub97c \ubb3c\ub9ac\uccd0,\n\uac04\ub808\uc774 \x1bCB\ud638\uc18c\uce74\uc640 \uac00\ubb38\x1bCZ\uc758 \uc801\ub958\ub85c\n\uc778\uc815\ubc1b\uac8c \ub41c \x1bCA\ud638\uc18c\uce74\uc640 \uc6b0\uc9c0\uc4f0\ub098\x1bCZ\u2015',
    4004: '\ud558\uc9c0\ub9cc \ubaa8\ub450\uac00 \ubcf4\uae30\uc5d0\n\uc5d0\uad6c\uce58 \uc804\ud22c\uc758 \uc8fc\uc5ed\uc740 \x1bCA\ubbf8\uc694\uc2dc \ub098\uac00\uc694\uc2dc\x1bCZ \uc0bc\ud615\uc81c\uc600\uace0,\n\x1bCA\uc6b0\uc9c0\uc4f0\ub098\x1bCZ\uac00 \ub098\uc124 \uc77c\uc740 \uac70\uc758 \uc5c6\uc5c8\ub2e4.',
    4005: '\ubaa8\ub450 \ub098\ub97c \uaf2d\ub450\uac01\uc2dc\ub77c \ubd80\ub978\ub2e4\u2026\u2026\n\uc2e4\uad8c\uc774 \uc5c6\ub294 \uac74 \uc0ac\uc2e4\uc774\ub098 \uc5b4\uca54 \uc218 \uc5c6\uc9c0.\n\uadf8 \uc2f8\uc6c0\uc5d0\uc11c \uacf5\uc744 \uc138\uc6b4 \uac74 \x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ\uc758 \uc0ac\ub78c\ub4e4\uc774\ub2e4.',
    4006: '\uc9c0\uae08\uc740 \x1bCA\ubbf8\uc694\uc2dc \ub098\uac00\uc694\uc2dc\x1bCZ\uac00 \ub098\ub97c \uc8fc\uad70\uc73c\ub85c \ub300\ud558\uc9c0\ub9cc,\n\uc7a5\ucc28 \ub098\ub3c4 \ubc30\uc2e0\ub2f9\ud560\uc9c0 \ubaa8\ub978\ub2e4.\n\x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ\ucc98\ub7fc\u2026\u2026',
    4007: '\uc790\uc2e0\uacfc \x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ\uc758 \uc55e\ub0a0\uc744 \ubd88\uc548\ud574\ud55c\n\x1bCA\ud638\uc18c\uce74\uc640 \uc6b0\uc9c0\uc4f0\ub098\x1bCZ\ub294,\n\uc801\uadf9\uc801\uc73c\ub85c \uad8c\ud55c\uc744 \x1bCA\ubbf8\uc694\uc2dc \ub098\uac00\uc694\uc2dc\x1bCZ\uc5d0\uac8c \ub118\uacbc\ub2e4.',
    4008: '\ud558\uadf9\uc0c1\uc774 \ub2f9\uc5f0\uc2dc\ub418\ub358 \uc774 \uc2dc\ub300\uc5d0,\n\x1bCA\uc6b0\uc9c0\uc4f0\ub098\x1bCZ\ub294 \uc790\uc2e0\uc758 \ucc98\uc9c0\ub97c \ub6f0\uc5b4\ub118\uc744\n\uc5ed\ub7c9\uc744 \uc9c0\ub2cc \uc8fc\uad70\uc774 \uc544\ub2c8\uc5c8\uace0\u2026\u2026',
    4009: '\x1bCA\ub098\uac00\uc694\uc2dc\x1bCZ\uc758 \uc88b\uc740 \ud611\ub825\uc790\ub77c\ub294 \uc790\ub9ac\uc5d0 \uba38\ubb3c\ub7ec,\n\uc790\uc2e0\uc758 \uc548\ub155\uc744 \uaf80\ud588\ub2e4.',
    4010: "\x1bCA\ub098\uac00\uc694\uc2dc\x1bCZ\ub3c4 \uc774 '\uc8fc\uad70'\uc758 \uad8c\ud55c \uc774\uc591 \uc758\uc0ac\ub97c \uc874\uc911\ud574,\n\x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ\uc640 \ub2ec\ub9ac \ucd94\ubc29\ud558\uc9c0 \uc54a\uace0,\n\uadf8 \uc9c0\uc704\ub97c \ubcf4\uc804\ud574 \uc8fc\uc5c8\ub2e4.",
    4011: "\uadf8\ub9ac\ud558\uc5ec \uc138\ub825\uc73c\ub85c\uc11c\uc758 '\x1bCB\ud638\uc18c\uce74\uc640 \uac00\ubb38\x1bCZ'\uc740,\n'\x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ'\uc73c\ub85c \ud0c8\ubc14\uafc8\ud574 \uac14\ub2e4.",
    4012: '\x1bCA\uc624\ub2e4 \ub178\ubd80\ud788\ub370\x1bCZ\u2015',
    4013: '\x1bCC\uc4f0\uc2dc\ub9c8\x1bCZ\uc640 \x1bCC\uc544\uc4f0\ud0c0\x1bCZ \uac19\uc740 \uc0c1\uc5c5 \ub3c4\uc2dc\ub97c \uc9c0\ubc30\ud574,\n\ud48d\ubd80\ud55c \uacbd\uc81c\ub825\uc73c\ub85c \x1bCB\uc624\ub2e4 \uac00\ubb38\x1bCZ\uc758 \uae30\ubc18\uc744 \ub2e4\uc9c4 \uba85\uc7a5.',
    4014: '\ud558\uc9c0\ub9cc \ub300\uc678\uc801\uc73c\ub85c\ub294 \uc5b4\ub514\uae4c\uc9c0\ub098\n\uc288\uace0\ub2e4\uc774\uc758 \uac00\uc2e0\uc774\ub77c\ub294 \ucc98\uc9c0\uc5d0 \uba38\ubb3c\ub800\uace0,\n\uac00\ubb38\ub3c4 \x1bCC\uc624\uc640\ub9ac\uad6d\x1bCZ\ub3c4 \ud1b5\uc77c\ud558\uc9c0 \ubabb\ud588\ub2e4\u2026\u2026',
    4015: '\uc601\uc9c0\uac00 \uc881\uc558\uae30\uc5d0,\n\x1bCA\uc0ac\uc774\ud1a0\x1bCZ\uc640 \x1bCA\uc774\ub9c8\uac00\uc640\x1bCZ \uac19\uc740 \uad6d\uc678\uc758 \uac15\uc801\uc5d0\uac8c\n\ucc28\uce30 \ubc00\ub9ac\uae30 \uc2dc\uc791\ud588\ub2e4.',
    4016: '\uadf8\ub7ec\ub358 \uc911, \uadf8\ub294 \uc720\ud589\ubcd1\uc73c\ub85c \uc4f0\ub7ec\uc84c\ub2e4\u2026\u2026',
    4017: '\ud750, \ud558\ud558\ud558\u2026\u2026\n\uc6d0\ud1b5\ud558\uad6c\ub098!',
    4018: '\uc774\uc81c \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc758 \ucc9c\ud558\uac00 \uc2dc\uc791\ub418\ub824\ub294\ub370,\n\uac00\ub3c5\ub3c4 \ub118\uae30\uc9c0 \ubabb\ud558\uace0 \ub0b4 \uc6b4\uc774 \ub2e4\ud558\ub2e4\ub2c8!',
    4019: '\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc57c\u2026\u2026\n\uc800\uc138\uc0c1\uc758 \ub0b4\uac8c \ubcf4\uc5ec \ub2e4\uc624.\n\x1bCA\uc624\ub2e4\x1bCZ\uc758 \ucc9c\ud558\ub97c\u2026\u2026 \ub124 \uc138\uc0c1\uc744!',
    4020: "'\uc624\uc640\ub9ac\uc758 \ud638\ub791\uc774' \x1bCA\uc624\ub2e4 \ub178\ubd80\ud788\ub370\x1bCZ\uac00 \uc138\uc0c1\uc744 \ub5a0\ub0ac\ub2e4.\n\uadf8 \uc8fd\uc74c\uc740 \x1bCB\uc624\ub2e4 \uac00\ubb38\x1bCZ\uc744 \ud06c\uac8c \ub4a4\ud754\ub4e4\uc5c8\ub2e4.",
    4021: '\x1bCA\ub178\ubd80\ud788\ub370\x1bCZ\uc640 \ub2ec\ub9ac \uac00\ubb38\uc758 \ub9ce\uc740 \uc774\ub4e4\uc740,\n\ucc28\uae30 \ub2f9\uc8fc \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc5d0\uac8c\n\ud070 \ubd88\uc548\uc744 \ud488\uace0 \uc788\uc5c8\ub2e4.',
    4022: '\uadf8\ub9ac\uace0,\n\uadf8 \ubd88\uc548\uc774 \ud604\uc2e4\uc774 \ub418\ub294 \uc0ac\uac74\uc774\n\x1bCA\ub178\ubd80\ud788\ub370\x1bCZ\uc758 \uc7a5\ub840 \ub0a0 \uc77c\uc5b4\ub0ac\ub2e4.',
    4023: '\ub3c4, \ub3c4\ub828\ub2d8!\n\uadf8 \ubaa8\uc2b5\uc740\u2026\u2026!?\n\ub300\uccb4 \ubb34\uc5c7\uc744\u2026\u2026',
    4024: '\u2026\u2026\u2026\u2026',
    4025: '(\uc544\ubc84\uc9c0\uac00 \uc8fd\uc5c8\ub2e4\u2026\u2026\n\u3000\uadf8\ud1a0\ub85d \ub09c\uc138\ub97c \uaff0\ub6ab\uc5b4 \ubcf8 \uc0ac\ub78c\ub3c4,\n\u3000\uc544\ubb34\uac83\ub3c4 \ud558\uc9c0 \ubabb\ud558\uace0 \uc8fd\ub294\uad6c\ub098\u2026\u2026)',
    4026: '(\ub098\ub3c4 \uc544\ubc84\uc9c0\ucc98\ub7fc \uc8fd\ub294\uac00?\n\u3000\ub2f9\uc8fc\ub2c8 \ub2e4\uc774\ubb18\ub2c8 \ubd88\ub824\ub3c4,\n\u3000\uc544\ubb34\uac83\ub3c4 \uc774\ub8e8\uc9c0 \ubabb\ud55c \ucc44 \uc8fd\ub294\uac00?)',
    4027: '\ub098\ub294\u2026\u2026!',
    4028: '\ub3c4, \ub3c4\ub828\ub2d8\u2026\u2026\n\uc5b4\ucc0c \uadf8\ub7f0 \uc9d3\uc744\u2026\u2026',
    4029: '\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub294 \x1bCA\ub178\ubd80\ud788\ub370\x1bCZ\uc758 \uc704\ud328\uc5d0 \ud5a5\uac00\ub8e8\ub97c \ub0b4\ub358\uc9c0\uace0,\n\uadf8\ub300\ub85c \uc7a5\ub840 \uc790\ub9ac\ub97c \ub5a0\ub0ac\ub2e4\uace0 \uc804\ud55c\ub2e4.',
    4030: '\uc0c8 \ub2f9\uc8fc\uc758 \uc774\ud574\ud560 \uc218 \uc5c6\ub294 \ud589\ub3d9\uc5d0,\n\x1bCB\uc624\ub2e4\x1bCZ \uac00\uc2e0\ub4e4\uc758 \ubd88\uc548\uc740 \ub2e4\uc2dc \ucee4\uc84c\uace0,\n\ubc30\uc2e0\uacfc \uc774\ubc18\uc774 \uc787\ub530\ub790\ub2e4.',
    4031: '\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc758 \uc544\uc6b0 \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ\ub97c\n\uc0c8 \ub2f9\uc8fc\ub85c \uc138\uc6b0\ub824\ub294 \uc6c0\uc9c1\uc784\uae4c\uc9c0 \ub4dc\ub7ec\ub0ac\ub2e4\u2026\u2026',
}

CURRENT_EXCLUDED_IDS = frozenset()
PREVIOUS_DEFERRED_BATCHES = (
    {
        "version": "v0.13",
        "batch_id": "ev-strdata-event-labels-2207-2406-v0.13",
        "ids": frozenset(range(2207, 2400)),
        "count": 193,
        "ids_sha256": "B346249D6B010CCC0243DE9AE75377A7FF0E0401F8A5FDC1E74621634B9FD9BB",
    },
    {
        "version": "v0.14",
        "batch_id": "ev-strdata-event-labels-2407-2580-v0.14",
        "ids": frozenset(range(2581, 2780)),
        "count": 199,
        "ids_sha256": "A3083AED6A0EB0D670B9E3A19D50BF78D60D6325533C2D04D381993F28345373",
    },
    {
        "version": "v0.15",
        "batch_id": "ev-strdata-character-speaker-labels-2780-2971-v0.15",
        "ids": frozenset(
            {2953, 2954, 2955, 2959, 2960, 2964, 2965, 2967}
            | set(range(2972, 2998))
            | {2998, 2999}
            | set(range(3000, 3007))
        ),
        "count": 43,
        "ids_sha256": "2B95F92D5D9B8AB6E96DEB1A412CB34957B24978FFF2C089254A42C3CE265245",
    },
    {
        "version": "v0.16",
        "batch_id": "ev-strdata-labels-narration-3007-3276-v0.16",
        "ids": frozenset(
            set(range(3105, 3116))
            | {3116}
            | set(range(3118, 3201))
            | {3201}
        ),
        "count": 96,
        "ids_sha256": "06BD88F03E814D81DC107F52B4F1B1452FF8461677854C550FAB5BC1DDD94D00",
    },
    {
        "version": "v0.17",
        "batch_id": "ev-strdata-events-endings-3277-3484-v0.17",
        "ids": frozenset(
            {
                3309, 3310, 3314, 3315, 3319, 3320, 3324, 3325, 3329,
                3330, 3334, 3335, 3339, 3340, 3344, 3345, 3349, 3350,
            }
        ),
        "count": 18,
        "ids_sha256": "CBD6A8F8CB20A423BE5D38411A6AB667ACECB736DCE08404B714ABDC1882D9FA",
    },
    {
        "version": "v0.18",
        "batch_id": "ev-strdata-historical-events-3485-3661-v0.18",
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
    {
        "version": "v0.19",
        "batch_id": "ev-strdata-historical-events-3662-3839-v0.19",
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PREVIOUS_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
CLASS_COUNTS = {
    "hosokawa_ujitsuna_authority_transfer_event": 9,
    "kikkawa_motoharu_adoption_event": 19,
    "kobayakawa_takakage_succession_event": 13,
    "matsudaira_imagawa_subordination_event": 15,
    "mori_inoue_purge_event": 16,
    "nagao_masakage_submission_event": 25,
    "oda_nobuhide_death_funeral_event": 20,
    "otomo_nikaikuzure_event": 18,
    "ouchi_yoshitaka_taineiji_event": 29,
    "sentoin_masakage_marriage_event": 12,
    "toishi_castle_defeat_event": 16,
}
TERMINOLOGY_REVIEW_IDS = frozenset(
    {3846, 3855, 3857, 3861, 3877, 3881, 3882, 3899, 3902, 3904,
     3915, 3918, 3930, 3934, 3935, 3945, 3946, 3949, 3963, 3967,
     3968, 3981, 3983, 3988, 3994, 3997, 4003, 4029}
)
RELATED_MSGEV_STRUCTURE_DIFFERENCE_IDS = (3949, 3950)
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 191
REPEATED_SOURCE_ID_GROUPS: tuple[tuple[int, ...], ...] = ((3908, 4024),)
EXCLUDED_CANDIDATE_COUNTS = {
    "actor_reference": 0,
    "dummy_placeholder": 0,
    "empty_slot": 0,
    "internal_event_key": 0,
}


def classify(entry_id: int) -> str:
    if entry_id <= 3854:
        return "matsudaira_imagawa_subordination_event"
    if entry_id <= 3879:
        return "nagao_masakage_submission_event"
    if entry_id <= 3898:
        return "kikkawa_motoharu_adoption_event"
    if entry_id <= 3916:
        return "otomo_nikaikuzure_event"
    if entry_id <= 3929:
        return "kobayakawa_takakage_succession_event"
    if entry_id <= 3945:
        return "toishi_castle_defeat_event"
    if entry_id <= 3961:
        return "mori_inoue_purge_event"
    if entry_id <= 3990:
        return "ouchi_yoshitaka_taineiji_event"
    if entry_id <= 4002:
        return "sentoin_masakage_marriage_event"
    if entry_id <= 4011:
        return "hosokawa_ujitsuna_authority_transfer_event"
    return "oda_nobuhide_death_funeral_event"

def non_display_kind(text: str) -> str | None:
    if text == "":
        return "empty_slot"
    if text.isascii() and all(char.isalnum() or char == "_" for char in text):
        return "internal_event_key"
    if text.startswith("[b") and text.endswith("]") and text.count("[") == 1:
        return "actor_reference"
    if not text.strip() or text.count("?") >= 2 and text.isascii():
        return "dummy_placeholder"
    return None


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def previous_deferred_overlap_metadata() -> dict[str, Any]:
    overlap_ids = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    return {
        "previous_batches": [
            {
                "version": batch["version"],
                "batch_id": batch["batch_id"],
                "deferred_entry_count": batch["count"],
                "deferred_ids_sha256": batch["ids_sha256"],
            }
            for batch in PREVIOUS_DEFERRED_BATCHES
        ],
        "previous_deferred_union_entry_count": PREVIOUS_DEFERRED_UNION_COUNT,
        "previous_deferred_union_ids_sha256": PREVIOUS_DEFERRED_UNION_SHA256,
        "current_deferred_entry_count": DEFERRED_COUNT,
        "current_deferred_ids_sha256": DEFERRED_IDS_SHA256,
        "overlap_entry_count": len(overlap_ids),
        "overlap_ids_sha256": shared.hash_json(overlap_ids),
        "overlap_detected": bool(overlap_ids),
    }


def related_msgev_review_metadata() -> dict[str, Any]:
    return {
        "related_batches": [
            "msgev_historical_events_3819_3929.v0.7",
            "msgev_historical_events_3930_4031.v0.8",
        ],
        "same_numeric_id_semantic_reviewed_entry_count": TRANSLATED_COUNT,
        "terminology_cross_checked": True,
        "direct_translation_reuse": True,
        "source_free_reused_entry_count": 192,
        "sc_structure_adjusted_entry_count": 2,
        "ev_strdata_sc_structure_differs_at_ids": list(
            RELATED_MSGEV_STRUCTURE_DIFFERENCE_IDS
        ),
        "ev_strdata_sc_structure_is_authoritative": True,
        "commercial_source_text_included": False,
    }


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = sorted(TRANSLATIONS)
    inspected_ids = list(range(SCOPE_START, SCOPE_END + 1))
    if len(ids) != TRANSLATED_COUNT or ids != inspected_ids:
        raise shared.EvStrDataError("v0.20 translated scope changed")
    if len(inspected_ids) != INSPECTED_COUNT:
        raise shared.EvStrDataError("v0.20 inspected count changed")
    if CURRENT_EXCLUDED_IDS or DEFERRED_COUNT != 0:
        raise shared.EvStrDataError("v0.20 current exclusion set changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.20 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.20 inspected id digest changed")
    if shared.hash_json(sorted(CURRENT_EXCLUDED_IDS)) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.20 excluded id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.20 Korean translation map changed")

    for batch in PREVIOUS_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(f"{batch['version']} deferred exclusion pin changed")
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.19 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.19 deferred union digest changed")
    overlap = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.20 exclusions overlap v0.13-v0.19 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.20 event classification counts changed")

    source_sc_hashes: list[str] = []
    all_reference_hashes: list[str] = []
    ids_by_source_hash: dict[str, list[int]] = defaultdict(list)
    detected_counts = Counter()
    for entry_id in ids:
        references = [
            loaded[language]["table"].texts[entry_id]
            for language in shared.LANGUAGES
        ]
        for text in references:
            kind = non_display_kind(text)
            if kind is not None:
                detected_counts[kind] += 1
        if any(not text.strip() for text in references):
            raise shared.EvStrDataError(f"id {entry_id}: empty aligned display text")
        source_sc = references[0]
        source_hash = common.text_hash(source_sc)
        source_sc_hashes.append(source_hash)
        all_reference_hashes.extend(common.text_hash(text) for text in references)
        ids_by_source_hash[source_hash].append(entry_id)
        failures = shared.replacement_failures(source_sc, TRANSLATIONS[entry_id])
        if failures:
            raise shared.EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
    if detected_counts:
        raise shared.EvStrDataError(f"v0.20 non-display candidate found: {dict(detected_counts)}")
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.20 repeated-source groups changed")
    for group in repeated_groups:
        if len({TRANSLATIONS[entry_id] for entry_id in group}) != 1:
            raise shared.EvStrDataError(f"repeated SC source has divergent Korean text: {group}")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.20 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.20 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.20 ordered SC/JP/TC source hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if non_display_kind(next_text) is not None:
            raise shared.EvStrDataError(f"v0.20 next candidate is not display text for {language}")
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.20 next display anchor changed for {language}")
    return ids


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    ids = validate_batch_sources(loaded)
    overlap = previous_deferred_overlap_metadata()
    related_review = related_msgev_review_metadata()

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = loaded["SC"]["table"].texts[entry_id]
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": TRANSLATIONS[entry_id],
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "classification": classify(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            loaded[language]["table"].texts[entry_id]
                        ),
                        "structure": shared.text_structure(
                            loaded[language]["table"].texts[entry_id]
                        ),
                    }
                    for language in shared.LANGUAGES
                },
                "translation_origin": "source_free_related_msgev_korean_reuse_with_sc_jp_tc_revalidation",
            }
        )

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": shared.RESOURCE,
        "base_language": "SC",
        "entry_count": TRANSLATED_COUNT,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": shared.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": shared.sha256(sc_raw),
            "string_count": shared.STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
    try:
        common.validate_overlay_shape(overlay)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist

    source_files = {
        language: {
            **shared.SOURCE_PINS[language],
            "relative_path": loaded[language]["relative"],
            "string_count": shared.STRING_COUNT,
        }
        for language in shared.LANGUAGES
    }
    boundary_ids = (
        SCOPE_START - 1,
        SCOPE_START,
        3854,
        3855,
        3879,
        3880,
        3898,
        3899,
        3916,
        3917,
        3929,
        3930,
        3945,
        3946,
        3961,
        3962,
        3990,
        3991,
        4002,
        4003,
        4011,
        4012,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v20",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "inspected_entry_count": INSPECTED_COUNT,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "next_display_id": NEXT_DISPLAY_ID,
            "functional_section": "historical_event_dialogue_and_narration",
            "functional_class_counts": CLASS_COUNTS,
            "excluded_candidate_counts": EXCLUDED_CANDIDATE_COUNTS,
        },
        "translation_mapping": {
            "sha256": TRANSLATION_MAP_SHA256,
            "entry_count": TRANSLATED_COUNT,
            "embedded_in_generator": True,
            "commercial_source_text_included": False,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "sc_jp_tc_semantic_review",
            "exact_sc_hash_for_every_overlay_entry",
            "ordered_sc_jp_tc_hash_set_pin",
            "standalone_internal_placeholder_actor_and_empty_detection",
            "v013_through_v019_deferred_union_overlap_check",
            "source_free_related_msgev_korean_reuse_and_revalidation",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata resource; TC is the third "
            "reference alongside SC and JP. Official strings are represented only by hashes."
        ),
        "source_files": source_files,
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(
                        loaded[language]["table"].texts[entry_id]
                    )
                    for language in shared.LANGUAGES
                },
            }
            for entry_id in boundary_ids
        ],
        "entry_count": TRANSLATED_COUNT,
        "entries": evidence_entries,
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v20",
        "batch_id": BATCH_ID,
        "quality_state": "historical_event_translation_draft_pending_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "terminology_review_count": len(TERMINOLOGY_REVIEW_IDS),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": classify(entry_id),
                "translation_origin": "source_free_related_msgev_korean_reuse_with_sc_jp_tc_revalidation",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": ["event_text_runtime_layout"]
                + (
                    ["historical_term_or_reading_review"]
                    if entry_id in TERMINOLOGY_REVIEW_IDS
                    else []
                ),
            }
            for entry_id in ids
        ],
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in (
        (overlay_path, overlay),
        (evidence_path, evidence),
        (review_path, review),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(shared.encode_json(value))

    source_free_scan = {
        path.relative_to(out_root).as_posix(): shared.source_free_counts(path.read_bytes())
        for path in (overlay_path, evidence_path, review_path)
    }
    if any(
        counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for counts in source_free_scan.values()
    ):
        raise shared.EvStrDataError(
            "v0.20 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.20 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v20",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "translated_ids_sha256": TRANSLATED_IDS_SHA256,
            "inspected_entry_count": INSPECTED_COUNT,
            "inspected_ids_sha256": INSPECTED_IDS_SHA256,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "deferred_ids_sha256": DEFERRED_IDS_SHA256,
            "next_display_id": NEXT_DISPLAY_ID,
            "total_string_slots": shared.STRING_COUNT,
            "sc_display_translation_target_count": shared.DISPLAY_TARGET_COUNT_SC,
            "functional_class_counts": CLASS_COUNTS,
            "excluded_candidate_counts": EXCLUDED_CANDIDATE_COUNTS,
        },
        "source_alignment": {
            "languages": list(shared.LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": shared.STRING_COUNT,
            "translated_reference_hash_count": TRANSLATED_COUNT * len(shared.LANGUAGES),
            "translated_ids_nonempty_in_all_references": TRANSLATED_COUNT,
            "ordered_sc_source_hashes_sha256": SOURCE_SC_HASHES_SHA256,
            "ordered_all_reference_hashes_sha256": ALL_REFERENCE_HASHES_SHA256,
            "source_files": source_files,
        },
        "translation": {
            "translation_map_sha256": TRANSLATION_MAP_SHA256,
            "translation_map_entry_count": TRANSLATED_COUNT,
            "exact_sc_hashes_emitted": TRANSLATED_COUNT,
            "runtime_layout_review_flag_count": TRANSLATED_COUNT,
            "historical_term_or_reading_review_flag_count": len(TERMINOLOGY_REVIEW_IDS),
            "source_text_embedded": False,
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": TRANSLATED_UNIQUE_SOURCE_HASH_COUNT,
            "translated_repeated_source_group_count": len(REPEATED_SOURCE_ID_GROUPS),
            "repeated_source_id_groups": [list(group) for group in REPEATED_SOURCE_ID_GROUPS],
            "failures": 0,
        },
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "replacement_invariants": {
            "checked": TRANSLATED_COUNT,
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholders_in_order",
            ],
        },
        "raw_format": {
            "lz4_wrapper_decompression": "OK",
            "message_table_parser": "tools/nobu16_msg_table.py",
            "raw_parse_rebuild_byte_exact_languages": list(shared.LANGUAGES),
            "binary_builder_state": "enabled_offline_output_only",
        },
        "offline_binary_build": {
            **binary,
            "installed_target_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": shared.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "existing_v01_through_v019_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.20 validation is not source-free")
    return {
        "entry_count": TRANSLATED_COUNT,
        "inspected_count": INSPECTED_COUNT,
        "deferred_count": DEFERRED_COUNT,
        "next_display_id": NEXT_DISPLAY_ID,
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [
        game_root / "MSG" / language / "ev_strdata.bin"
        for language in shared.LANGUAGES
    ]
    before = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr20-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr20-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.20 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.20 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.20 build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"translated={result['entry_count']}")
    print(f"inspected={result['inspected_count']}")
    print(f"deferred_internal={result['deferred_count']}")
    print(f"next_display_id={result['next_display_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
