#!/usr/bin/env python3
"""Build a private Wave 92 PK regional/policy static-dialogue candidate.

Wave 92 accepts only Wave 91's private candidate.  It completes four
self-contained, fixed PK MSGGAME lines after pinning direct PC Japanese,
English, Simplified Chinese, and Traditional Chinese records at matching
coordinates.  It writes only a private candidate; Steam, Git, network, and
release operations are absent.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

W91_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave91_pk_regional_static_v1" / "candidate"
)
W91_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave91_pk_regional_static_v1"
    / "build_pc_dialogue_quality_wave91_pk_regional_static_v1.py"
)
W91_BUILDER_SHA256 = "177DF383325AA170D379F22271F934C8A44F661094BD2F0047ADC2D558E8C1B7"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave92-pk-regional-policy-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave92-pk-regional-policy-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave92-pk-regional-policy-static-manifest.v1"

# Fixed MSGGAME person-dialogue / terminal-static-0143 route; not the 30px/4-line
# MSGEV event widget.  Preserve the existing raw-G1N layout gate for this route.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave91_private_candidate_byte_identical_from_wave90",
        "path": W91_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave91_private_candidate",
        "path": W91_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_679,
        "sha256": "0153A4DDAB3A5DA43557D373920DC3312693F485EDF24867CE2D075B9167A4CC",
        "raw_size": 1_799_596,
        "raw_sha256": "FE1CA4B937EE4A4B86E6945544316072A9A0B9E919EA04128758E69C87F99F12",
    },
}

W91_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W91_CANDIDATE_ROOT / "audit.v1.json",
        "size": 21_331,
        "sha256": "968CBC6C09ED79933283DAF2B0E7919B17F5B2201D86F6D9A1FAA2F6410F683D",
    },
    "build_manifest.v1.json": {
        "path": W91_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_710,
        "sha256": "D06C8E39319CDB3FA9DB0A8C128915A30658CA7A4EBC304C128F9A563F0FB8A4",
    },
}

TARGET_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "size": 1_806_610,
        "sha256": "DB2F6DD20F72F7490B0F3FC2874CA480571F82F2B7637A54C6959F7FBF26F0AA",
        "raw_size": 1_799_528,
        "raw_sha256": "8B17328C40A788F004E600220ADDA4A0727CA6657248CD9A95C829F815296986",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave92Error(RuntimeError):
    """Raised when a Wave 92 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave92Error(label)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_w91() -> Any:
    require(W91_BUILDER.is_file(), "pinned Wave 91 builder is absent")
    require(sha256_path(W91_BUILDER) == W91_BUILDER_SHA256, "pinned Wave 91 builder differs")
    spec = importlib.util.spec_from_file_location("wave92_imported_wave91", W91_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave92Error("cannot load pinned Wave 91 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W91 = load_w91()
W86 = W91.W86
Change = W91.Change
CandidateBundle = W91.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "musashi_bando_significance",
        (15, 1619),
        "武蔵は坂東の中心にして、隣接国も多い地\n他国に進出する上でも、武蔵一円を支配した\n意味は大きいかと",
        "무사시는 간토의 중심이며\n인접국도 많은 땅입니다.\n일대 장악은 타국 진출의 발판입니다.",
        "167759E690564927FA97D40DEBD49B933E2127BCE86B7113593C99C3D0A548DB",
        137,
        "F296D8847D2F998564F7C5AC01DB3F3931B28DE72B272C811F867FEA921648CE",
        105,
        (576, 552, 840),
        ("", "0143E2000000050505"),
        ("0143E2000000",),
        source_hashes(
            "02555BFE1992DDEE48A7E96BD92016C9067F97B5053E23DCEB4465C2D133A93F",
            "0A6B620C77AE8795427EF2DC058A7C406F65EC4C5B09578DF1E2B97691CBE8E9",
            "08953B308A818A72DB489D5B103CBC43163637D28EFEC5AC36764C8E0B737DCD",
            "96E088802EDF93A8E5A9A56C3F0121E8EE457F9DB8929DAF6321AF222AD5C329",
        ),
    ),
    Change(
        "owari_kinai_significance",
        (15, 1622),
        "尾張は東国と西国の境に当たり、\n畿内もうかがえる枢要の地\nこの国を制した意義は大きいかと",
        "오와리는 동국과 서국의 경계에 있고,\n기나이까지 시야에 두는 요충지입니다.\n이 지역을 제압한 의의는 매우 큽니다.",
        "DCA2F48E5817E5D6C1C45E6A8FA89BF7C7AEAE01FF35E930B5CF754AD9BDEDA5",
        139,
        "F8255E8C2F0DADDE1ED8711A1C4B9F9E534297936D0DC85A52950FF3C9250496",
        135,
        (840, 864, 864),
        ("", "0143E2000000050505"),
        ("0143E2000000",),
        source_hashes(
            "453B6C76AB5DEF221A935D76A9FEE451D4401C9A97A197328BCEBBC6D8F2A27B",
            "156F52E6F1E140A21BF833B22E06F89CC57E4FCBA5503D71A7911B39D12BF4DB",
            "4CE3A10D00756FFD141C9012706C7620D17FD1CD02050B18B873F7CA78F50D7A",
            "F9EE2BFFA750BB66CABB1F10AC3D52C024D1B73AA70548FB35DA9B7E7B58FC0E",
        ),
    ),
    Change(
        "banshu_harima_rank",
        (15, 1627),
        "この播州は西国と京を結ぶ枢要の地\n諸国の国司の中でも播磨守は、伊予守と並び\n最も格上といわれて",
        "반슈는 서국과 교토를 잇는 요지입니다.\n하리마노카미와 이요노카미는\n각국 국사 중 가장 격이 높습니다.",
        "4D89D09616BBF7BD4D669D6CAB91744AD4AEBB9337F2DFE8C2BB12AE6A0A0017",
        151,
        "3F9FE63EDEDFEAF55A24F06702B40D2BB9FCC3C601B2B745CDA272CDAE2F4A77",
        121,
        (888, 648, 768),
        ("", "0143B2000000050505"),
        ("0143B2000000",),
        source_hashes(
            "D5F4C801CA3FD501452DE9C6B0610AE840CE1105F916FFE88B2F92FA6BD49C8A",
            "2818719654AD83498AF5150AEDEDD9D37A4AB244264638035548BDA9B759F3E2",
            "0B10C2E288C8D5CB81ECCD3970CFABE5960ABC9C6C31482EDA2CC435D53E99AC",
            "BA10845F7CDAC92035884DB7A7769AF24F6FE5D2101C17293F4253E2ECB91220",
        ),
    ),
    Change(
        "strong_enemy_castle_town_advice",
        (15, 1665),
        "強敵に打ち勝つには国力増強が肝心\nもし余剰の金銭があるならば\n城下施設の増築を提案",
        "강적을 이기려면 국력을 키워야 합니다.\n여유 자금이 있다면\n성하 시설 증축을 제안합니다.",
        "390180613D187F60BF35D0904ED730CD3C75248897CD9EA4AFFF301DFFFC94B5",
        107,
        "7AA756BB09D9AB4ACFB75D49796FCA18F7D6E65220334231EA8A47A4C59900D7",
        107,
        (888, 432, 672),
        ("", "01438E000000050505"),
        ("01438E000000",),
        source_hashes(
            "793CCB8EA7503957E512293EA836793D29E6373766D14AA629C54330CCD7BABA",
            "EBC0477834341F77C9594E30BF27F6EB620F1D154ECF6B61B7EA89C132CEC5DD",
            "9903EA76273C333A76234334B2AF084D9C2A921FD06642351E19192ED542A01E",
            "56EED58C64F6A9FF585A19AE8B41B4D224BACB653F435350FC6F774BCC2BDC24",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (15, 1619): "坂東를 역사적 간토 권역으로 정확히 표기했다. 무사시가 간토의 중심이자 인접국이 많은 땅이며, 일대 장악이 타국 진출의 발판이라는 네 언어 원문의 의미를 모두 보존해 문장을 완결했다.",
    (15, 1622): "오와리가 동국·서국의 경계이자 기나이를 시야에 둘 수 있는 요충지이며 제압의 의의가 크다는 네 언어 원문을 보존해 자연스러운 서술문으로 완결했다.",
    (15, 1627): "京를 교토로 정확히 표기했다. 반슈가 서국과 교토를 잇는 요지이고 하리마노카미와 이요노카미가 각국 국사 중 높은 격이라는 네 언어 원문의 의미를 모두 보존해 문장을 완결했다.",
    (15, 1665): "강적을 이기기 위한 국력 증강, 여유 자금, 성하 시설 증축 제안이라는 네 언어 원문의 조건과 권고를 모두 보존해 문장을 완결했다.",
}


def configure_w91() -> None:
    """Reuse only Wave 91's pinned parser, rebuilder, and source guards."""

    require(W91.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W91.Wave91Error = Wave92Error
    W91.require = require
    W91.TMP_ROOT = TMP_ROOT
    W91.W90_CANDIDATE_ROOT = W91_CANDIDATE_ROOT
    W91.INPUT_PROFILES = INPUT_PROFILES
    W91.W90_EVIDENCE = W91_EVIDENCE
    W91.TARGET_PROFILES = TARGET_PROFILES
    W91.CHANGES = CHANGES
    W91.CHANGE_RATIONALES = CHANGE_RATIONALES
    W91.SCHEMA = SCHEMA
    W91.AUDIT_SCHEMA = AUDIT_SCHEMA
    W91.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W91.configure_w90()


def w92_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave90_evidence")
    predecessor["wave91_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w91()
    base = W91.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w92_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 91 private candidate"
    audit["source_policy"]["manual_line_break_topology"] = "semantic three-line layout preserved or rebalanced without shortening"
    audit["source_policy"]["layout_baseline"] = {
        "widget": "fixed MSGGAME person dialogue / terminal static 0143",
        "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
        "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
        "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
        "max_lines": MAX_PERSON_DIALOGUE_LINES,
        "event_msgev_30px_4line_rule": "not applied",
    }
    audit["scope"] = {
        "kind": "fixed PK regional-commentary and policy-advice person dialogue",
        "block_id": 15,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "runtime_0143_entries": "forbidden",
        "multi_literal_entries": "forbidden",
        "standalone_02xx_entries": "forbidden; bytes inside a complete 0143 are not standalone opcodes",
    }
    for row in audit["records"]:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["semantic_repair"] = CHANGE_RATIONALES[coordinate]
        row["manual_line_break_policy"] = "semantic three-line layout without sentence shortening"

    manifest = copy.deepcopy(base.manifest)
    manifest["schema"] = MANIFEST_SCHEMA
    manifest["predecessor"] = copy.deepcopy(audit["predecessor"])
    manifest["audit_sha256"] = sha256_bytes(canonical_json(audit))
    manifest["scope"] = {
        "block_id": 15,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "candidate_only": True,
    }
    return CandidateBundle(base.packed, base.raw, audit, manifest)


def write_candidate(bundle: Any) -> Path:
    configure_w91()
    return W91.write_candidate(bundle)


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = TMP_ROOT / "candidate"
    for resource, packed in bundle.packed.items():
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require(
        (output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "private manifest differs",
    )
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "base_byte_identical_from_wave91": True,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": len(CHANGES),
            "base_byte_identical_from_wave91": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
