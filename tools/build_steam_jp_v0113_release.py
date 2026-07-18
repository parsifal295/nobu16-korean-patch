#!/usr/bin/env python3
"""Build the public Steam JP 1.1.7 v0.11.3 release from pinned inputs.

The archive layout, installer support payload, and safety gates are inherited
from the audited v0.11.2 builder.  This wrapper only advances the release
identity and pins the six text resources changed by the NPC and dialogue/event
quality work; all other game and installer members remain byte-identical.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any, Mapping


VERSION = "v0.11.3"
ZIP_NAME = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.11.3.zip"
ZIP_TIMESTAMP = (2026, 7, 18, 9, 0, 0)
SCHEMA = "nobu16.kr.steam-jp-1.1.7-release.v0.11.3"
MANIFEST_NAME = "release_manifest.v0.11.3.json"

SCRIPT = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT.parents[1]
DEFAULT_PAYLOAD_ROOT = PROJECT_ROOT / "release_payload" / "v0.11.1"
UPSTREAM_PATH = PROJECT_ROOT / "tools" / "build_steam_jp_v0112_release.py"


# Current Steam profile after the NPC component repair and the unified text
# quality transaction.  The remaining nine game resources are intentionally
# pinned unchanged from v0.11.2.
GAME_TARGETS: Mapping[str, tuple[int, str]] = {
    "MSG/JP/ev_strdata.bin": (928_123, "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80"),
    "MSG/JP/msggame.bin": (1_504_643, "C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347"),
    "MSG/JP/strdata.bin": (957_204, "5F308F416378976C1AB0B50D4A91C9DA38C637A0A842BAB04FB48256B2103E28"),
    "MSG_PK/JP/msgbre.bin": (484_068, "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939"),
    "MSG_PK/JP/msgdata.bin": (496_995, "69090EC9EEE1DF9EAFB64BB35CEFD285A5089FDE78E9A4A855EAA0AE5991C168"),
    "MSG_PK/JP/msgev.bin": (994_707, "3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5"),
    "MSG_PK/JP/msggame.bin": (1_806_787, "3924ADABF69C9BA72EEBA95E4CE07A3CB8FCD716A31D8F6217ECC5FFAA7B96C5"),
    "MSG_PK/JP/msgire.bin": (23_128, "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB"),
    "MSG_PK/JP/msgstf.bin": (17_341, "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B"),
    "MSG_PK/JP/msgui.bin": (122_733, "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7"),
    "RES_JP/res_lang.bin": (161_428_458, "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"),
    "RES_JP/res_lang_exp.bin": (13_796_051, "AC55622FC5C78ECA4ECFE37D1D890D5B26F6200ED7BAF1506B784541E158B7B7"),
    "RES_JP_PK/res_lang_pk.bin": (141_893_576, "9019582ABBF88B08562B366E7D5A4283C6507455F86A801946AC32CCC25C2C2F"),
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": (83_878_438, "F65383C72291D08B71EBA7E2EF504A8C674E7C4678445045868D98FCA5B0730D"),
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": (67_623_137, "09531F21FA3BD56E2554C47942E47B5ACB61A7F279EFBF4AF85E4CAB963E4FAA"),
}


def load_upstream() -> Any:
    spec = importlib.util.spec_from_file_location("steam_jp_v0112_release", UPSTREAM_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load release builder: {UPSTREAM_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(game_root: Path, output: Path, payload_root: Path = DEFAULT_PAYLOAD_ROOT) -> dict[str, object]:
    upstream = load_upstream()
    upstream.VERSION = VERSION
    upstream.ZIP_NAME = ZIP_NAME
    upstream.ZIP_TIMESTAMP = ZIP_TIMESTAMP
    upstream.SCHEMA = SCHEMA
    upstream.MANIFEST_NAME = MANIFEST_NAME
    upstream.GAME_TARGETS = dict(GAME_TARGETS)
    return upstream.build(
        game_root,
        output,
        payload_root,
        game_targets=GAME_TARGETS,
        support_targets=upstream.SUPPORT_TARGETS,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", required=True, type=Path)
    parser.add_argument("--payload-root", type=Path, default=DEFAULT_PAYLOAD_ROOT)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = build(args.game_root, args.output, args.payload_root)
    print(manifest["release_zip"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
