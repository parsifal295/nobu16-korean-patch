#!/usr/bin/env python3
"""Independently revalidate the priority PC ``msgbre`` omission block.

This is an evidence-only companion to the already active private candidate
file ``msgbre_findings.v1.jsonl``.  It does not add duplicate builder inputs.
Each included recommendation is independently composed from pristine PC
Japanese plus current PC EN/SC/TC context, then compared against the active
candidate only after that review.  Switch Korean, historic Korean backups,
and game-resource writes are excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_ROOT = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
TMP_ROOT = REPO / "tmp"
AUDIT_ROOT = TMP_ROOT / "translation_quality_audit_v1"
ACTIVE_CANDIDATES = AUDIT_ROOT / "semantic" / "msgbre_findings.v1.jsonl"
DEFAULT_OUTPUT = AUDIT_ROOT / "semantic" / "msgbre_priority_omission_revalidation.v1.jsonl"
DEFAULT_HOLD_OUTPUT = AUDIT_ROOT / "semantic" / "msgbre_priority_omission_holds.v1.jsonl"

PATHS = {
    "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgbre.bin",
    "ko": STEAM / "MSG_PK" / "JP" / "msgbre.bin",
    "en": STEAM / "MSG_PK" / "EN" / "msgbre.bin",
    "sc": STEAM / "MSG_PK" / "SC" / "msgbre.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msgbre.bin",
}

sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff"
    r"\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


@dataclass(frozen=True)
class Candidate:
    identifier: int
    source_hash: str
    current_hash: str
    independent_recommendation: str
    omitted_semantics: tuple[str, ...]


# The recommendations below were authored from the PC JP/EN/SC/TC reading
# before loading the active candidate artifact.  Hashes freeze complete
# source/current records, not just an abbreviated clause.
CANDIDATES = (
    Candidate(
        748,
        "F5D1367060779F53755BB0231ED9222DADC84F3BFDFA5E87BF25F0447D9E132F",
        "DA18A26190B64820524130CD03DD37F69CDD0219BCAD2D819FE85CA3F09CE399",
        "모리 가신. 쓰네요시의 아들. 야마나 도요쿠니에게 추방되어 이나바 돗토리성에 들어가 하시바 히데요시군과 싸웠다. 그러나 히데요시의 「굶겨 죽이기」 전법에 패했고, 성 안 병사의 목숨을 살려주는 것을 조건으로 자결했다.",
        ("Hideyoshi's starvation tactic", "defeat", "condition protecting the castle garrison"),
    ),
    Candidate(
        752,
        "21E9EDC33F0682001B6DDB612BCCE59DDCC699DC1BDD3B246A550DF38CC0D2A2",
        "AB94717B0BC972264AADA82945792E874C185DC7B3A2D7842ED168AFE9720F92",
        "벳쇼 가신. 기누가사성주. 기누가사 가문은 아카마쓰 가문의 서류다. 한때 미요시 나가요시에게 속해 각지를 전전했다. 하시바 히데요시의 주고쿠 침공군과 싸워 패배했으며, 낙향했다는 설과 전사했다는 설이 있다.",
        ("Kinugasa lineage", "roving service under Miyoshi", "two alternative outcomes rather than battle death alone"),
    ),
    Candidate(
        754,
        "FAD048E8E8EAAE0E682AA0B7BC09362AD2E4D0DE0BFA470A60AF83F468EBC597",
        "2EA7DB1D2FF0D94EBBB747A973731E1C011450588BDC9734CDE2B8C49AF8A72E",
        "전국시대 최고의 입신출세가. 오다 노부나가를 섬기며 뛰어난 인망과 지략을 무기로 활약해 두각을 드러냈다. 혼노지의 변 후 아케치 미쓰히데와 시바타 가쓰이에 등을 차례로 물리치고 천하의 패권을 떨쳤다.",
        ("rise through popularity and strategy", "emergence as a leader", "claim to national hegemony"),
    ),
    Candidate(
        755,
        "B4ED6D25896A00B4CB71CFA8E2D6BA36478748694761B8FA1B6A3181FA0973B2",
        "5E37A146ACD16632A1CB215AE19B4920AF2081B2436B11FCE230F93DDEADCCCC",
        "도요토미 가신. 기노시타 이에사다의 아들. 도요토미 히데요시의 명으로 고바야카와 다카카게의 양자가 되었다. 세키가하라 합전에서 동군으로 돌아서 동군의 승리에 크게 공헌했지만, 2년 뒤 급사했다.",
        ("parentage", "adoption by Kobayakawa Takakage", "Hideyoshi's order"),
    ),
    Candidate(
        756,
        "28B2820E64A3011E97DA08F89E762DEEBEC87A44E0840CE1018F939853E6BDD1",
        "586B5231FCDD4050E8F1B5351273A9C55E453F055A28886A521A0E28EDD6AE16",
        "히데요시의 이복동생. 형의 오른팔로서 그의 패업에 공헌했다. 온화하고 인망이 높아 히데요시와 다른 다이묘의 절충 역할을 맡았다. 히데요시보다 먼저 세상을 떠났고, 여러 장수가 그의 죽음을 애석해했다.",
        ("gentle character and popularity", "negotiation role", "mourning by other generals"),
    ),
    Candidate(
        757,
        "6B105985CA56F0982BB13A370377B4280332D66A036F0D9E0BF4F7B45F42AB51",
        "0724E8EBB4A1C0D8FF27E192CDB0C9F428F820736D10D4435F801DB265FEECF8",
        "히데요시의 차남. 세키가하라 합전 후 셋쓰·가와치·이즈미 65만 석의 일개 다이묘로 전락했다. 오사카 전투에서 어머니 요도도노 등의 과도한 비호를 받아 한 번도 출진하지 못한 채 자결했다.",
        ("post-Sekigahara demotion", "specified 650,000-koku domain", "never deployed because of overprotection"),
    ),
    Candidate(
        758,
        "B068BE92E74B56EAC4D4772ABA4DABE3CF5F002A9B36D72D3CD83866ACB8AD54",
        "4C584B65111476880806214CE54FD69C2B3E276E24E502CA477ECBB54CD8B857",
        "아라키 가신. 주군 무라시게의 소성을 지냈다. 주가가 몰락한 뒤 도요토미 히데요시를 섬겼고, 훗날 기노시타 성을 하사받아 이나바 와카사 2만 석을 영유했다. 세키가하라 합전에서 서군에 속했으며 전후 자결했다.",
        ("page role", "2万石 grant", "Western Army affiliation"),
    ),
    Candidate(
        759,
        "58D8DE33EB1E1F7FD1A06B5F0907AF7F29F5F34BC3EFE4861C6CE9D3F51A7715",
        "2A5A99A3569BFBB99E9E501B3CA2E4334C5D7EC45A4E59E9D42B1E4B0A1DD146",
        "도요토미 가신. 이에사다의 장남. 와카사 오바마성주. 세키가하라 합전에서 동군에 속해 후시미성을 맡았으나 임무 방기의 죄로 개역되어 교토에 은거했다. 근세 와카의 시조로 일컬어진다.",
        ("eldest-son relationship", "Fushimi Castle duty", "disposition and Kyoto retirement"),
    ),
    Candidate(
        760,
        "6B6A8566BDBADA8E9A07A3460A1BD93FFF6958214708E78E9568A90D1827DB13",
        "7E43CF52528F79021ECD8ECB28E25772062C2CECD73E17DC49734BB70302D47B",
        "류조지 가신. 류조지 사천왕 중 한 사람으로 일컬어진다. 오키타나와테 합전에서 주군 다카노부의 전사 소식을 듣자 나베시마 나오시게를 탈출시킨 뒤 적진에 돌입했다. 생사는 여러 설이 있어 분명하지 않다.",
        ("allowing Nabeshima Naoshige to escape", "multiple accounts of his fate"),
    ),
    Candidate(
        761,
        "B77EAABD7A2C4A9C793D5D814124C6FBD9B7EF74A5B9F66B21A85E26BB900558",
        "2128EC0453D704D36F6D744379B0D88DBC235231077A97C4BC46B2BF23C1D3FA",
        "도요토미 가신. 사다미쓰의 아들이라 한다. 주군 히데요리의 유형제로서 소성을 지냈다. 도쿠가와가와 화목할 때 도요토미가의 사자를 맡았다. 오사카 여름의 진에서 이이 나오타카군과 싸워 전사했다.",
        ("foster-sibling and page relationship", "specific Ii Naotaka force", "battle death"),
    ),
    Candidate(
        762,
        "A3CB622B6CCE529A1BE1B5E731DB07B356A9B45F54FD318B4306E1770643E966",
        "029502FB71924B7C6CFB11044C083ADF060651E9ABB68334242BAC6AB6C868A7",
        "도요토미 가신. 히타치노스케라 칭했다. 시즈가타케 합전 등에 종군해 에치젠 후추 10만 석을 영유했다. 데와의 검지 봉행 등을 맡았다. 훗날 도요토미 히데쓰구 사건에 연좌되어 자결을 강요받았다.",
        ("Hitachinosuke title", "Echizen Fuchu 100,000-koku holding", "Dewa land-survey magistracy", "forced suicide"),
    ),
    Candidate(
        764,
        "77C61BAE59C83829288BA9D2DCEBF19281EBDC0CB3F297304F3B6F7BF3A5AEDC",
        "B4F551EAA99CDFB2A94768E217D2778947A4573F09B70E4A717663F95305D3E6",
        "오스미 기모쓰키가의 서류. 가네모리의 아버지. 본가가 시마즈가에 맞서는 가운데 시마즈 다다요시와 내통해 가지키성주가 되었다. 훗날 다다요시와 다카히사에 맞섰으나 패해 항복하고 다시 신하가 되었다.",
        ("Kanemori's parentage", "secret contact with Tadayoshi", "later defeat and renewed submission"),
    ),
    Candidate(
        765,
        "7C02B11BA34FEEE8EB1FD62EE50EB62C8443D5FF9616E3BBE9AD6918C5F618C3",
        "3A4796E4A2F3B86451A46F83D554E45BCD3AB6C4DD81418942891D77B644D61C",
        "오스미의 센고쿠 다이묘. 다카야마성주. 가네쓰구의 아들. 둘째 형 가네스케가 추방된 뒤 가독을 이었으나, 시마즈군의 공격에 패해 영지를 내놓고 항복했다. 세키가하라 합전에서 전사했다.",
        ("second-elder-brother relationship", "Shimazu attack", "surrender of the domain"),
    ),
    Candidate(
        766,
        "8871299B47E9269B347773CFF70962B6DFB4646A0D9EB884E1DE0BED0EE25C45",
        "30A324A0AFD30FF186550A4A8838626E21529578E80AA0BE8846AE9A28AF07EB",
        "시마즈 가신. 기모쓰키가의 서류. 부친 가네히로에게서 가지키성주 자리를 이었다. 시마즈 다카히사와 요시히사의 가로를 맡았다. 가모가와 이토가를 공격한 전투에서 특히 군공을 세웠다.",
        ("Kimotsuki branch", "castle succession", "councillor role", "military merit"),
    ),
    Candidate(
        767,
        "0978E8AB954EB68487F11A1856C20D977F3AA0107DE7930D4E35D938608E124F",
        "95B50B66F4CF8519682AE2AF728D406B385BA8202E13BECE92364228EE903795",
        "오스미의 센고쿠 다이묘. 다카야마성주. 기모쓰키가 최대의 판도를 구축했다. 시마즈 다다요시의 딸과 혼인했으나, 훗날 그의 아들 다카히사와 적대했다. 거성이 시마즈군에게 빼앗겼다는 소식을 듣고 자결했다.",
        ("greatest territorial extent", "loss of the residence", "suicide outcome"),
    ),
    Candidate(
        770,
        "9B4319FA48473C34A2555EC99DC8953B0A957B73349A24CDE0F56CFB670119A9",
        "BFCFFDF066D91A6225237927C16DE03B196AA0AE25BB8B5B318EF71743BECA57",
        "오스미의 센고쿠 다이묘. 다카야마성주. 가네쓰구의 아들. 형 요시가네가 죽은 뒤 가독을 이었다. 이토가 등과 손잡고 시마즈가에 맞섰기에, 시마즈 다다요시의 딸인 어머니와 가신들에게 추방당했다.",
        ("cause of exile", "exile by mother and retainers"),
    ),
    Candidate(
        771,
        "A173FC8CE5DB6458AD225C795EC29FBFD8B8927D8CC04A68C35C7619EC3D7BC6",
        "425D8A1B2CDFDA3AB54F4F1AFB0C264ED236C2161A8EA8D72A09ACC432A2D95A",
        "오스미의 센고쿠 다이묘. 다카야마성주. 가네쓰구의 아들. 이토가와 손잡고 휴가 오비성을 공격해 성주 시마즈 다다치카를 쫓아냈다. 또한 이지치 시게오키를 도우는 등 평생 시마즈가와 항쟁했다.",
        ("aid to Ijichi Shigeoki", "lifelong conflict with the Shimazu"),
    ),
    Candidate(
        772,
        "FB7C4F4A75EDDA439CACEBFC74EE3BE0D9E46C2916570EF2DE6DE8354862BBD7",
        "1E9CA4E568122CB4D9CD56EAA5D82A5740FC5482EBF4072F16DBCD1A755761AD",
        "아시카가 가신. 주군 요시테루의 근습을 지냈다. 요시테루가 죽은 뒤 오미로 달아난 그의 동생 요시아키를 위해 분주히 뛰었다. 요시아키가 쇼군이 된 뒤 오다 노부나가와 대립해 조헤이지에 은거했다.",
        ("service to the fleeing Yoshiaki after Yoshiteru's death", "specific retirement at Joheiji"),
    ),
    Candidate(
        774,
        "144BC2350A0D704BD1987498BFB739F02995334F7228E34FFB91BB9A2E75B8A7",
        "204643E6805E5184300D5B6E35D8F5AD85A22316C39A7BBB983B2AD886713908",
        "도요토미 가신. 다카요시의 아들. 아내와 여동생의 인연으로 도요토미 히데요시를 섬겨 오미 오쓰 6만 석을 영유했다. 세키가하라 합전에서 동군에 속해 거성에 농성하며 서군 일부를 오쓰에 묶어 두었다.",
        ("family connection to Hideyoshi", "60,000-koku holding", "castle defence holding Western forces at Otsu"),
    ),
    Candidate(
        775,
        "FAA05A692C5AE75EE85E284FCE6C904FF0AEA149EE54E6D59E07E21BFF312287",
        "F9362F8C7D3B1877C13CFA5064EB9E5462AB7E04F48409FBB06CC9861FF57F59",
        "도요토미 가신. 다카요시의 차남. 시나노 이이다 10만 석을 영유하며 성하 마을 정비에 힘썼다. 세키가하라 합전에서 동군에 속했고, 전후 고야산으로 달아난 형에게 도쿠가와가에 사관하라고 설득했다.",
        ("second-son relationship", "castle-town development", "brother's flight to Mount Koya"),
    ),
)


@dataclass(frozen=True)
class Hold:
    identifier: int
    source_hash: str
    current_hash: str
    reason: str


HOLDS = (
    Hold(703, "192014059422319F7A3894C34A547D5AA9897D4CE309B313B0A313981095D8E0", "ED79970776EE0987C1D70BB9D2DA5C684AA6E664B570109A3C28EB4B62E158FC", "The current biography retains the source's central recruitment, campaign, castle lordship, and battle facts; only compression remains."),
    Hold(763, "A74BC27DA428C8014D2337E715FED8180C0B362EEB326C7627A86590DD055A8B", "4779DD8A24E370768402AD0C6EF850A900220F40F6B1174C5849F146596487F0", "The current text retains the core affiliation, nickname, divine blessing, and Toyotomi-side action; no high-confidence material omission remains."),
    Hold(768, "BE4173E58FC84F5FA0CD00151A840057BFA1BB8CB782A67693B7582201EE5145", "927F1B3A2F2B47B4D9AE5F6D37DB1C0C33BA9EDF6F5598DE6F65FD98E0BB547A", "The live text preserves the name restoration, Shonai suppression, and Ryukyu expedition; wording is compressed but not a high-confidence omission."),
    Hold(769, "584C215BFE9F6E7A15781B76863BDC287A8AAE1DEE807E0DD11D7C3C61EEA850", "2881FE24C052EDD36E15E55FD441FD1C34A3627456D7353219C77A60575326D4", "The source's succession and aborted Osaka-winter deployment are retained; only the Higo location is absent, below the omission threshold."),
    Hold(773, "F766F2D9A17D177289B1B0722DFD3CDF4AADF890F81C74560941301C95745A4F", "6AA5A848420605CE33817BB40E972F2D8076FE693E66C8AA5989B702FAF363C3", "Potential relationship wording deserves a separate relationship review, not an omission-only candidate."),
    Hold(776, "4E8920CEF3DDEDFD77CD7F79FE1102D8E19524F3FD24FFA5694A28303A77AC9A", "EED786DDE254BB52C86040A08E99584FDECEE0408D7C030F7965322A2436A839", "The visible problem is a relationship mistranslation (義母), plus proper-name/territory detail, rather than an omission-only repair."),
    Hold(777, "80D90BBE7999AD52E1E9171540E139E21D6202C47EC973E37E50D25C8B6A0C08", "CC169EA5C2DE17CE6FF7203F75E1B815B66E67424ECB532A2C3585916D72DF52", "The current text retains the actions, Shinano departure, and education of Kunikiyo; its wording is compressed but not materially omitted."),
)

PRIORITY_IDS = {703, 748, 752, *range(754, 778)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load_common(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def profile(text: str) -> dict[str, object]:
    return {
        "escape_tags": ESC_RE.findall(text),
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "newlines": re.findall(r"\r\n|\n|\r", text),
        "outer_ascii_whitespace": (
            text[: len(text) - len(text.lstrip(" \t"))],
            text[len(text.rstrip(" \t")) :],
        ),
        "private_use": [f"U+{ord(character):04X}" for character in PRIVATE_USE_RE.findall(text)],
        "fullwidth_percent_count": text.count("\uff05"),
        "question_mark_count": text.count("?"),
    }


def profile_match(left: dict[str, object], right: dict[str, object]) -> dict[str, bool]:
    return {
        "escape_tags_match": left["escape_tags"] == right["escape_tags"],
        "runtime_tokens_match": left["runtime_tokens"] == right["runtime_tokens"],
        "printf_match": left["printf"] == right["printf"],
        "newlines_match": left["newlines"] == right["newlines"],
        "outer_ascii_whitespace_match": left["outer_ascii_whitespace"] == right["outer_ascii_whitespace"],
        "private_use_match": left["private_use"] == right["private_use"],
        "fullwidth_percent_count_match": left["fullwidth_percent_count"] == right["fullwidth_percent_count"],
        "question_mark_count_match": left["question_mark_count"] == right["question_mark_count"],
    }


def integrity(text: str) -> dict[str, bool]:
    return {
        "hangul_present": bool(HANGUL_RE.search(text)),
        "no_japanese_or_cjk_residue": not bool(CJK_OR_KANA_RE.search(text)),
        "no_replacement_glyph": "\ufffd" not in text,
        "no_repeated_question_marks": "??" not in text,
    }


def safe_under(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=False)
    allowed = root.resolve(strict=False)
    if resolved != allowed and allowed not in resolved.parents:
        raise ValueError(f"output must remain below {allowed}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_active_rows() -> dict[int, dict[str, Any]]:
    if not ACTIVE_CANDIDATES.is_file():
        raise ValueError(f"active candidate artifact is absent: {ACTIVE_CANDIDATES}")
    rows: dict[int, dict[str, Any]] = {}
    for line_number, line in enumerate(ACTIVE_CANDIDATES.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        identifier = row.get("id")
        if isinstance(identifier, int):
            if identifier in rows:
                raise ValueError(f"duplicate active msgbre candidate id {identifier} at line {line_number}")
            rows[identifier] = row
    return rows


def source_and_current_gate(identifier: int, expected_source_hash: str, expected_current_hash: str, tables: dict[str, list[str]]) -> tuple[str, str]:
    source = tables["jp"][identifier]
    current = tables["ko"][identifier]
    if text_hash(source) != expected_source_hash:
        raise ValueError(f"pristine JP source hash gate failed at msgbre:{identifier}")
    if text_hash(current) != expected_current_hash:
        raise ValueError(f"current KO hash gate failed at msgbre:{identifier}")
    return source, current


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    candidate_ids = {candidate.identifier for candidate in CANDIDATES}
    hold_ids = {hold.identifier for hold in HOLDS}
    if candidate_ids.intersection(hold_ids) or candidate_ids.union(hold_ids) != PRIORITY_IDS:
        raise ValueError("priority IDs are not partitioned into candidates and holds")
    if len(CANDIDATES) != len(candidate_ids) or len(HOLDS) != len(hold_ids):
        raise ValueError("duplicate candidate or hold ID")

    tables = {language: load_common(path) for language, path in PATHS.items()}
    if any(len(table) != len(tables["jp"]) for table in tables.values()):
        raise ValueError("PC msgbre cardinalities differ")
    file_hashes = {language: sha256_file(path) for language, path in PATHS.items()}
    active = load_active_rows()

    evidence_rows: list[dict[str, Any]] = []
    for candidate in CANDIDATES:
        source, current = source_and_current_gate(candidate.identifier, candidate.source_hash, candidate.current_hash, tables)
        active_row = active.get(candidate.identifier)
        if active_row is None:
            raise ValueError(f"active msgbre candidate is absent at {candidate.identifier}")
        active_replacement = active_row.get("ko")
        if not isinstance(active_replacement, str) or not active_replacement:
            raise ValueError(f"active msgbre candidate has no replacement at {candidate.identifier}")
        if active_row.get("current_hash") != candidate.current_hash:
            raise ValueError(f"active msgbre candidate current hash differs at {candidate.identifier}")

        source_profile = profile(source)
        current_profile = profile(current)
        independent_profile = profile(candidate.independent_recommendation)
        active_profile = profile(active_replacement)
        independent_current = profile_match(current_profile, independent_profile)
        independent_source = profile_match(source_profile, independent_profile)
        active_current = profile_match(current_profile, active_profile)
        active_source = profile_match(source_profile, active_profile)
        independent_integrity = integrity(candidate.independent_recommendation)
        active_integrity = integrity(active_replacement)
        if not (
            all(independent_current.values())
            and all(independent_source.values())
            and all(active_current.values())
            and all(active_source.values())
            and all(independent_integrity.values())
            and all(active_integrity.values())
        ):
            raise ValueError(f"format or Korean-integrity validation failed at msgbre:{candidate.identifier}")
        evidence_rows.append(
            {
                "resource": "msgbre",
                "coordinate": str(candidate.identifier),
                "id": candidate.identifier,
                "current_ko": current,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "source_file_sha256": file_hashes["ko"],
                "pristine_jp_file_sha256": file_hashes["jp"],
                "reference_file_sha256": {language: file_hashes[language] for language in ("en", "sc", "tc")},
                "pc_target_contexts": {language: tables[language][candidate.identifier] for language in ("en", "sc", "tc")},
                "issue_type": "high_confidence_biography_semantic_omission_revalidation",
                "omitted_semantics": list(candidate.omitted_semantics),
                "independent_recommendation_ko": candidate.independent_recommendation,
                "independent_recommendation_hash": text_hash(candidate.independent_recommendation),
                "active_candidate_comparison": {
                    "artifact": ACTIVE_CANDIDATES.name,
                    "id": candidate.identifier,
                    "active_replacement_hash": text_hash(active_replacement),
                    "active_current_hash_matches": True,
                    "semantic_alignment": "aligned",
                    "material_replacement_recommendation": None,
                },
                "source_gate_validation": "exact_utf16le_hash_match",
                "current_ko_gate_validation": "exact_utf16le_hash_match",
                "format_profile": {
                    "pristine_jp": source_profile,
                    "current_ko": current_profile,
                    "independent_recommendation": independent_profile,
                    "active_candidate": active_profile,
                },
                "format_validation": {
                    "independent_to_current": independent_current,
                    "independent_to_pristine_jp": independent_source,
                    "active_to_current": active_current,
                    "active_to_pristine_jp": active_source,
                    "independent_integrity": independent_integrity,
                    "active_integrity": active_integrity,
                    "all_required_checks_pass": True,
                },
                "candidate_integration_policy": "evidence_only_existing_active_candidate_no_duplicate_application",
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
                "game_files_written": False,
            }
        )

    hold_rows: list[dict[str, Any]] = []
    for hold in HOLDS:
        source, current = source_and_current_gate(hold.identifier, hold.source_hash, hold.current_hash, tables)
        hold_rows.append(
            {
                "resource": "msgbre",
                "coordinate": str(hold.identifier),
                "id": hold.identifier,
                "current_ko": current,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "source_file_sha256": file_hashes["ko"],
                "pristine_jp_file_sha256": file_hashes["jp"],
                "reference_file_sha256": {language: file_hashes[language] for language in ("en", "sc", "tc")},
                "pc_target_contexts": {language: tables[language][hold.identifier] for language in ("en", "sc", "tc")},
                "status": "hold_not_high_confidence_semantic_omission",
                "reason": hold.reason,
                "source_gate_validation": "exact_utf16le_hash_match",
                "current_ko_gate_validation": "exact_utf16le_hash_match",
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
                "game_files_written": False,
            }
        )

    evidence_payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in evidence_rows)
    hold_payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in hold_rows)
    if any(byte > 0x7F for byte in evidence_payload.encode("utf-8")) or any(byte > 0x7F for byte in hold_payload.encode("utf-8")):
        raise ValueError("JSONL output must be ASCII-only")
    summary = {
        "priority_coordinate_count": len(PRIORITY_IDS),
        "revalidated_existing_active_candidate_count": len(evidence_rows),
        "hold_count": len(hold_rows),
        "candidate_ids": [row["id"] for row in evidence_rows],
        "hold_ids": [row["id"] for row in hold_rows],
        "active_candidate_artifact": ACTIVE_CANDIDATES.name,
        "semantic_alignment": "all_revalidated_rows_aligned_no_material_replacement_recommendation",
        "source_gates": "all_exact_utf16le_hash_match",
        "current_ko_gates": "all_exact_utf16le_hash_match",
        "format_validation": "active_and_independent_recommendations_match_runtime_printf_esc_newline_whitespace_profiles",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return evidence_rows, hold_rows, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="validate only; write no files")
    parser.add_argument("--write", action="store_true", help="write evidence and hold JSONL files")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--hold-output", type=Path, default=DEFAULT_HOLD_OUTPUT)
    args = parser.parse_args()
    if args.validate and args.write:
        parser.error("choose either --validate or --write")
    evidence_rows, hold_rows, summary = build_rows()
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        output = safe_under(args.output, TMP_ROOT)
        hold_output = safe_under(args.hold_output, TMP_ROOT)
        if output.resolve(strict=False) == hold_output.resolve(strict=False):
            raise ValueError("evidence and hold outputs must differ")
        evidence_payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in evidence_rows)
        hold_payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in hold_rows)
        atomic_write(output, evidence_payload)
        atomic_write(hold_output, hold_payload)
        print(json.dumps({**summary, "output": str(output), "output_bytes": output.stat().st_size, "hold_output": str(hold_output), "hold_output_bytes": hold_output.stat().st_size}, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    for row in evidence_rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
