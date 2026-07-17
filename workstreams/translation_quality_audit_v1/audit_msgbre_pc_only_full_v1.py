#!/usr/bin/env python3
"""Audit all PC ``msgbre`` biographies without using Switch Korean text.

The audit reads the pristine PC Japanese biographies, the currently installed
PC Korean table, and the installed PC EN/SC/TC tables.  Matching PC ``strdata``
descriptions are used only as same-source Korean corroboration.  It deliberately
does not inspect a Switch Korean resource or historical Korean output.

Every one of the 3,000 table slots is classified.  The six replacements below
are limited to independently reproducible, high-confidence errors: a lost
actor/name, an untranslated geographic construction, a cross-resource proper
name mismatch, a lost battle/death predicate, and concrete omitted biography
facts.  The script writes private JSONL evidence under ``tmp`` only and never
writes a Steam game file.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_ROOT = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
BUILDER = REPO / "workstreams" / "translation_quality_corrections_v1" / "build_translation_quality_corrections_v1.py"
DEFAULT_AUDIT_OUTPUT = AUDIT_ROOT / "semantic" / "msgbre_pc_only_full_audit.v1.jsonl"
DEFAULT_CANDIDATE_OUTPUT = AUDIT_ROOT / "semantic" / "msgbre_pc_only_quality_addendum.v1.jsonl"
DEFAULT_HOLD_OUTPUT = AUDIT_ROOT / "semantic" / "msgbre_pc_only_ambiguous_holds.v1.jsonl"

PATHS = {
    "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgbre.bin",
    # The Korean patch is intentionally mounted on the Steam JP route.
    "ko": STEAM / "MSG_PK" / "JP" / "msgbre.bin",
    "en": STEAM / "MSG_PK" / "EN" / "msgbre.bin",
    "sc": STEAM / "MSG_PK" / "SC" / "msgbre.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msgbre.bin",
}
STRDATA_PATHS = {
    "jp": PRISTINE_ROOT / "MSG" / "JP" / "strdata.bin",
    "ko": STEAM / "MSG" / "JP" / "strdata.bin",
}
SUPPORT_PATHS = {
    "msgdata": {
        "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
        "ko": STEAM / "MSG_PK" / "JP" / "msgdata.bin",
        "en": STEAM / "MSG_PK" / "EN" / "msgdata.bin",
    },
    "msgev": {
        "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgev.bin",
        "ko": STEAM / "MSG_PK" / "JP" / "msgev.bin",
        "en": STEAM / "MSG_PK" / "EN" / "msgev.bin",
    },
}

EXPECTED_FILE_SHA256 = {
    "jp": "945A0E9157E2DBD12781FFA5A986D93681325F40B6486348B1AB311D3BEE1D6D",
    "ko": "C545CD2251E61AEB0A68E10A08ADFFCD3B150C32B5D15236D90727A305B03BAE",
    "en": "97AF6A9CCB7D49C1325A92F6C83B88AA26511B7AE2CB0ABB7C6E0B38AB368945",
    "sc": "D0DDE32C6BE9C81BA91D210BC62BC3E552121A9D7E493D53B461641FABAA499E",
    "tc": "F4A39E2FFD0DB4FBDE416E20B387DA629D87905E127C4421166751E3650D4A11",
}
EXPECTED_STRDATA_SHA256 = {
    "jp": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "ko": "D518A91E36B9A59EAD0B5ED1FDD067941E4BF72E43AFCB19C296C8AD77C8C128",
}
EXPECTED_SUPPORT_SHA256 = {
    "msgdata": {
        "jp": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
        "ko": "7EAA33BC80C021A028660DF1A7934886591A1DA36DB7BC53146749C3A4AEF040",
        "en": "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033",
    },
    "msgev": {
        "jp": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "ko": "B8B3B1C5A635419E590DB866C240A1B6609799E0FEA0E69F86D6208F27E5C52B",
        "en": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
    },
}

ENTRY_COUNT = 3000
POPULATED_ENTRY_COUNT = 2217
NEW_CANDIDATE_IDS = frozenset({112, 241, 276, 710, 800, 835})

# The remaining source/current divergences below are real editorial variants,
# but PC-only material does not identify one uniquely safe Korean rewrite.  We
# retain them in a separate hold file instead of silently changing them.
AMBIGUOUS_HOLDS = {
    703: "shorter wording retains the source events; exact degree-of-contribution wording is editorial",
    720: "the source's plot/house-succession detail is compressed, but death, actor, and outcome are retained",
    734: "the PC Korean corpus contains both '우마야바시' and '마야바시' for 厩橋; needs a resource-wide place-name decision",
    746: "the source's adoption mechanism is compressed to succession; a terminology policy is needed before rewriting",
    768: "permission, merit, and late-life nuance are compressed but the restoration, suppression, and Ryukyu participation remain",
}

# Exact current-text gates keep the private proposal from applying after an
# unrelated Korean edit.  Candidate wording is intentionally minimal except
# where several concrete source facts were lost in one biography.
CANDIDATES: dict[int, dict[str, Any]] = {
    112: {
        "issue_type": "named_actor_lost_from_execution_account",
        "source_cues": ("隆資", "刺客", "殺害"),
        "expected_current": "오노데라 가신. 당주 데루미치가 주색에 빠져 간언한 가신들을 가차 없이 처벌했으나 뜻을 굽히지 않고 쓴소리를 올렸다. 결국 데루미치가 보낸 자객에게 살해되었다.",
        "proposed": "오노데라 가신. 당주 데루미치가 주색에 빠져 간언한 가신들을 가차 없이 처벌했으나, 다카스케도 뜻을 굳히고 쓴소리를 올렸다. 결국 데루미치가 보낸 자객에게 습격당해 살해되었다.",
        "strdata_terms": ("다카스케", "습격당해 살해되었다"),
        "rationale": "원문은 고언을 올린 인물이 隆資(다카스케)라고 명시한다. 현재 문장은 그 주어와 이름을 잃어 당주가 쓴소리를 한 것처럼 읽힐 수 있으므로, 이름과 자객의 습격을 복원한다.",
        "support": (
            ("msgdata", 2792, "隆資", "다카스케", "Takasuke"),
            ("msgev", 112, "姉崎隆資", "아네자키 다카스케", "Takasuke Anezaki"),
        ),
    },
    241: {
        "issue_type": "japanese_geographic_construction_left_untranslated",
        "source_cues": ("防長両国", "山口奉行"),
        "expected_current": "깃카와 가신. 아버지 깃카와 쓰네요와 함께 모리 모토나리의 둘째 아들 모토하루가 깃카와 가문을 잇도록 힘썼다. 뒤에 모리 가문에 속했고, 오우치 가문 멸망 뒤 야마구치 부교로 보초 두 구니의 여러 정무를 맡았다.",
        "proposed": "깃카와 가신. 아버지 깃카와 쓰네요와 함께 모리 모토나리의 둘째 아들 모토하루가 깃카와 가문을 잇도록 힘썼다. 뒤에 모리 가문에 속했고, 오우치 가문 멸망 뒤 야마구치 부교로 스오와 나가토 두 지방의 여러 정무를 맡았다.",
        "strdata_terms": ("스오와 나가토 두 지방",),
        "rationale": "防長両国은 스오·나가토 두 지방을 가리킨다. 현재 '보초 두 구니'에는 일본어 행정 단위가 그대로 남아 있어, PC 같은 원문의 한국어 지명 확장을 사용한다.",
        "support": (),
    },
    276: {
        "issue_type": "proper_name_reading_conflicts_with_pc_name_labels",
        "source_cues": ("祐慶", "自害命令"),
        "expected_current": "이토 가신. 기요타케성주. 세키가하라 전투 때 서군 측 미야자키성을 함락했다. 전후 막부의 반환 명령과 주군 스케요시의 자결 명령을 모두 거부한 채 거성에 농성하다 패사했다.",
        "proposed": "이토 가신. 기요타케성주. 세키가하라 전투 때 서군 측 미야자키성을 함락했다. 전후 막부의 반환 명령과 주군 스케노리의 자결 명령을 모두 거부한 채 거성에 농성하다 패사했다.",
        "strdata_terms": ("스케노리",),
        "rationale": "祐慶의 PC EN 표기는 Sukenori이며, PC msgdata와 PC msgev의 같은 인물 표기도 스케노리다. 현재 전기 한 곳의 스케요시를 교정한다.",
        "support": (
            ("msgdata", 1803, "祐慶", "스케노리", "Sukenori"),
            ("msgev", 269, "伊東祐慶", "이토 스케노리", "Sukenori Itª"),
        ),
    },
    710: {
        "issue_type": "fierce_battle_context_omitted_before_mysterious_death",
        "source_cues": ("壮絶な死闘", "謎の急死"),
        "expected_current": "나가시마 간쇼지의 승려. 부친 쇼케이의 뒤를 이어 사찰의 수장이 되었다. 혼간지 겐뇨의 격문에 호응해 노부나가와 맞서 문도를 이끌었으나, 의문의 급사를 맞았다.",
        "proposed": "나가시마 간쇼지의 승려. 부친 쇼케이의 뒤를 이어 사찰의 수장이 되었다. 혼간지 겐뇨의 격문에 호응해 노부나가와 맞서 문도를 이끌고 처절한 사투를 벌이던 중, 의문의 급사를 맞았다.",
        "strdata_terms": ("처절한 사투",),
        "rationale": "원문은 문도를 이끌어 처절한 사투를 계속하던 중의 급사라고 서술한다. 현재 번역의 대조·급사 연결만으로는 전투 맥락이 빠지므로 그 술어를 복원한다.",
        "support": (
            ("msgdata", 1534, "証恵", "쇼케이", "Shªkei"),
            ("msgev", 711, "願証寺証恵", "간쇼지 쇼케이", "Shªkei Ganshªji"),
        ),
    },
    800: {
        "issue_type": "proper_name_reading_michifusa_to_michiyasu",
        "source_cues": ("来島通康", "村上武吉"),
        "expected_current": "고노 가신, 수군 지휘관. 구루시마 미치후사와 무라카미 다케요시와 함께 오토모 소린의 이요 침공을 막았다. 뒤에는 오다 가문과 싸우는 모리 가문에 수군 지원을 했다.",
        "proposed": "고노 가신, 수군 지휘관. 구루시마 미치야스와 무라카미 다케요시와 함께 오토모 소린의 이요 침공을 막았다. 뒤에는 오다 가문과 싸우는 모리 가문에 수군 지원을 했다.",
        "strdata_terms": ("구루시마 미치야스",),
        "rationale": "来島通康은 PC EN에서 Michiyasu Kurishima이며, 같은 PC 전기의 다른 항목들도 미치야스로 표기한다. 미치후사는 다른 인물명으로 잘못 읽힌 표기다.",
        "support": (),
    },
    835: {
        "issue_type": "three_concrete_biography_facts_omitted",
        "source_cues": ("次男", "朝鮮派兵", "２万６千石余"),
        "expected_current": "도쿠가와 가신. 시게하루의 아들이다. 처음에는 도요토미 히데요시를 섬겼으나 세키가하라 전투에서 동군에 속했다. 전후 야마토 고세에 영지를 받았다.",
        "proposed": "도쿠가와 가신. 시게하루의 차남이다. 처음에는 도요토미 히데요시를 섬겨 조선 파병 등에 종군했다. 세키가하라 전투에서는 동군에 속했고, 전후 야마토 고세 2만 6천여 석을 영유했다.",
        "strdata_terms": ("차남", "조선 파병", "2만 6천여 석"),
        "rationale": "원문의 차남 여부, 조선 파병 종군, 전후 2만 6천여 석 영유라는 세 가지 구체 사실이 빠져 있다. PC 같은 원문의 한국어 전기와 EN/중문 문맥으로 이를 모두 복원한다.",
        "support": (),
    },
}

RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")

# Broad semantic gates are evidence screens, not automatic rewriting rules.
# They intentionally cover the user-prioritized high-risk conditions.
SOURCE_GATES = {
    # Do not match bare 死 or 子: those characters occur in names and in
    # neutral phrases such as 死後/妻女山.  These are event/relation phrases.
    "death": re.compile(r"(?:死亡|死去|戦死|病死|急死|溺死|自害|自刃|殺害|暗殺|斬首|処刑|討たれ|討ち取ら|敗死|横死|刑死|毒殺|殉死|果てた)"),
    "exile": re.compile(r"(?:追放|流罪|追われ|逐電|逃亡|退去|出奔|隠棲|隠居|放浪|退隠|脱出|出家)"),
    "defeat_or_fall": re.compile(r"(?:敗北|敗れ|敗死|降伏|落城|滅亡|改易|没落|大敗|撃破され|壊滅|劣勢)"),
    "victory_or_recovery": re.compile(r"(?:勝利|撃退|撃破|打ち破|奪還|制圧|討ち取|落とす|攻め落と|撃滅|大勝|勝つ)"),
    "relationship": re.compile(r"(?:父[・の親]|母[・の親]|兄[・の]|弟[・の]|姉[・の]|妹[・の]|祖父[・の]|祖母[・の]|長男|次男|三男|四男|五男|六男|嫡男|庶子|子[・のを]|娘[・のを]|孫[・の]|養子|養嗣子|妻[・の]|夫[・の]|婿)"),
    "status": re.compile(r"(?:家臣|当主|城主|守護|奉行|大名|旗本|僧|将軍|主君|城代|家老|国人|豪族)"),
}
TARGET_GATES = {
    "death": re.compile(r"(?:죽|사망|전사|병사|급사|익사|자결|참수|살해|암살|처형|모살|패사|절명|독살|순사|몰살|사형|토벌되|죽임|목숨)"),
    "exile": re.compile(r"(?:추방|유배|쫓겨|도주|도망|달아나|퇴거|출분|은거|은둔|방랑|물러|피신|탈출|출가)"),
    "defeat_or_fall": re.compile(r"(?:패[해배]|항복|함락|멸망|개역|몰락|대패|격파|괴멸|무너|패사|성 잃|몰수)"),
    "victory_or_recovery": re.compile(r"(?:승리|격퇴|격파|물리|탈환|제압|토벌|함락|무찌르|쳐 죽|공략|대승|이겼|이기)"),
    "relationship": re.compile(r"(?:아버지|부친|모친|어머니|형|동생|누나|여동생|형제|조부|조모|장남|차남|삼남|넷째 아들|다섯째|적남|서자|아들|딸|손자|양자|양사자|아내|부인|남편|사위|조카)"),
    "status": re.compile(r"(?:가신|당주|성주|슈고|수호|부교|봉행|다이묘|하타모토|승려|쇼군|주군|성대|가로|고쿠진|호족)"),
}

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata  # noqa: E402


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def load_table(path: Path) -> tuple[str, ...]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def load_strdata(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


def format_profile(value: str) -> dict[str, Any]:
    return {
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "escape_tags": ESC_RE.findall(value),
        "line_breaks": re.findall(r"\r\n|\n|\r", value),
        "outer_ascii_whitespace": [
            value[: len(value) - len(value.lstrip(" \t"))],
            value[len(value.rstrip(" \t")) :],
        ],
        "private_use": [f"U+{ord(char):04X}" for char in PRIVATE_USE_RE.findall(value)],
        "fullwidth_percent_count": value.count("％"),
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


def deterministic_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def active_builder_ids() -> set[int]:
    """Read current builder inputs only; do not invoke a game-file build."""
    if not BUILDER.is_file():
        raise ValueError(f"translation-quality builder is absent: {BUILDER}")
    for dependency in (REPO / "tools", REPO / "workstreams" / "strdata", REPO / "workstreams" / "msggame"):
        dependency_text = str(dependency)
        if dependency_text not in sys.path:
            sys.path.insert(0, dependency_text)
    module_name = "_msgbre_pc_only_full_audit_builder"
    module_spec = importlib.util.spec_from_file_location(module_name, BUILDER)
    if module_spec is None or module_spec.loader is None:
        raise ValueError(f"unable to load builder: {BUILDER}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    result: set[int] = set()
    try:
        spec = next(resource for resource in module.SPECS if resource.name == "msgbre")
        for path in spec.proposal_paths:
            path = Path(path)
            # Once this review addendum is wired into the generic builder, it
            # must not diagnose its own six rows as a pre-existing conflict.
            # All other artifact IDs remain active overlap gates.
            if path.resolve() == DEFAULT_CANDIDATE_OUTPUT.resolve():
                continue
            if path == module.AUTONOMOUS_WORDING_OVERLAY:
                continue
            if not path.is_file():
                raise ValueError(f"active msgbre builder artifact is absent: {path}")
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"active msgbre artifact row is not an object: {path}:{line_number}")
                declared_resource = row.get("resource")
                if declared_resource is not None and declared_resource != "msgbre":
                    continue
                identifier = row.get("id")
                if isinstance(identifier, bool) or not isinstance(identifier, int) or identifier < 0:
                    raise ValueError(f"active msgbre artifact has invalid id: {path}:{line_number}")
                if identifier in result:
                    raise ValueError(f"duplicate active msgbre coordinate: {identifier}")
                result.add(identifier)
    finally:
        sys.modules.pop(module_name, None)
    return result


def gate_result(source: str, current: str) -> dict[str, bool]:
    """Report whether each high-risk source condition has a Korean counterpart."""
    return {
        name: not SOURCE_GATES[name].search(source) or bool(TARGET_GATES[name].search(current))
        for name in SOURCE_GATES
    }


def exact_same_source_coordinate(
    identifier: int,
    source: str,
    strdata_jp: Mapping[tuple[int, int], str],
    source_to_strdata: Mapping[str, list[tuple[int, int]]],
) -> tuple[int, int] | None:
    preferred = (2, identifier)
    if strdata_jp.get(preferred) == source:
        return preferred
    matches = source_to_strdata.get(source, [])
    return matches[0] if matches else None


def support_rows_for_candidate(
    identifier: int,
    support_tables: Mapping[str, Mapping[str, tuple[str, ...]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for resource, resource_id, expected_jp, expected_ko, expected_en in CANDIDATES[identifier]["support"]:
        tables = support_tables[resource]
        if (
            tables["jp"][resource_id] != expected_jp
            or tables["ko"][resource_id] != expected_ko
            or tables["en"][resource_id] != expected_en
        ):
            raise ValueError(f"PC {resource}:{resource_id} support evidence changed for msgbre:{identifier}")
        rows.append(
            {
                "resource": resource,
                "id": resource_id,
                "source_jp": expected_jp,
                "current_ko": expected_ko,
                "pc_en": expected_en,
            }
        )
    return rows


def candidate_for(
    identifier: int,
    source: str,
    current: str,
    references: Mapping[str, str],
    msgbre_hashes: Mapping[str, str],
    strdata_jp: Mapping[tuple[int, int], str],
    strdata_ko: Mapping[tuple[int, int], str],
    strdata_hashes: Mapping[str, str],
    support_tables: Mapping[str, Mapping[str, tuple[str, ...]]],
    support_hashes: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    config = CANDIDATES[identifier]
    if current != config["expected_current"]:
        raise ValueError(f"msgbre:{identifier} current Korean baseline changed")
    if any(cue not in source for cue in config["source_cues"]):
        raise ValueError(f"msgbre:{identifier} pristine source no longer has its correction cues")
    coordinate = (2, identifier)
    if strdata_jp.get(coordinate) != source:
        raise ValueError(f"msgbre:{identifier} no longer has same-source PC strdata evidence at 2:{identifier}")
    strdata_current = strdata_ko.get(coordinate)
    if not isinstance(strdata_current, str) or any(term not in strdata_current for term in config["strdata_terms"]):
        raise ValueError(f"msgbre:{identifier} PC strdata evidence no longer supports the required Korean facts")
    proposed = config["proposed"]
    before = format_profile(current)
    after = format_profile(proposed)
    if before != after or format_profile(source) != after:
        raise ValueError(f"msgbre:{identifier} replacement changes a protected format field")
    if KANA_OR_HAN_RE.search(proposed) or not HANGUL_RE.search(proposed) or "\0" in proposed or "�" in proposed:
        raise ValueError(f"msgbre:{identifier} proposal fails Korean text safety checks")
    support_rows = support_rows_for_candidate(identifier, support_tables)
    return {
        "resource": "msgbre",
        "id": identifier,
        "ko": current,
        "proposed_ko": proposed,
        "current_hash": text_hash(current),
        "source_text": source,
        "source_text_hash": text_hash(source),
        "live_ko_file_sha256": msgbre_hashes["ko"],
        "pristine_jp_file_sha256": msgbre_hashes["jp"],
        "reference_contexts": dict(references),
        "issue_type": config["issue_type"],
        "rationale": config["rationale"],
        "pc_cross_resource_evidence": {
            "strdata_same_source_coordinate": f"2:{identifier}",
            "strdata_current_ko": strdata_current,
            "strdata_pristine_jp_file_sha256": strdata_hashes["jp"],
            "strdata_current_ko_file_sha256": strdata_hashes["ko"],
            "same_person_or_name_label_evidence": support_rows,
            "support_file_sha256": {resource: dict(hashes) for resource, hashes in support_hashes.items()},
            "switch_korean_translation_used": False,
            "historic_korean_translation_used": False,
        },
        "format_validation": {
            "current_to_proposed": "runtime_printf_escape_newline_outer_whitespace_private_use_and_percent_match",
            "pristine_jp_to_proposed": "runtime_printf_escape_newline_outer_whitespace_private_use_and_percent_match",
            "all_required_checks_pass": True,
        },
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    msgbre_hashes = {language: file_hash(path) for language, path in PATHS.items()}
    if msgbre_hashes != EXPECTED_FILE_SHA256:
        raise ValueError("PC msgbre file baseline changed; rebase the PC-only audit before reuse")
    tables = {language: load_table(path) for language, path in PATHS.items()}
    if any(len(table) != ENTRY_COUNT for table in tables.values()):
        raise ValueError("PC msgbre table cardinality differs from 3,000")
    if sum(bool(value) for value in tables["jp"]) != POPULATED_ENTRY_COUNT:
        raise ValueError("PC msgbre populated-slot count differs from 2,217")
    if any(any(tables[language][POPULATED_ENTRY_COUNT:]) for language in tables):
        raise ValueError("expected msgbre internal blank-slot tail changed")

    strdata_hashes = {language: file_hash(path) for language, path in STRDATA_PATHS.items()}
    if strdata_hashes != EXPECTED_STRDATA_SHA256:
        raise ValueError("PC strdata evidence baseline changed; rebase msgbre audit before reuse")
    strdata_tables = {language: load_strdata(path) for language, path in STRDATA_PATHS.items()}
    source_to_strdata: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for coordinate, source in strdata_tables["jp"].items():
        if source:
            source_to_strdata[source].append(coordinate)
    for matches in source_to_strdata.values():
        matches.sort()

    support_hashes = {
        resource: {language: file_hash(path) for language, path in paths.items()}
        for resource, paths in SUPPORT_PATHS.items()
    }
    if support_hashes != EXPECTED_SUPPORT_SHA256:
        raise ValueError("PC name-label evidence baseline changed; rebase msgbre audit before reuse")
    support_tables = {
        resource: {language: load_table(path) for language, path in paths.items()}
        for resource, paths in SUPPORT_PATHS.items()
    }

    active_ids = active_builder_ids()
    unexpected_overlap = NEW_CANDIDATE_IDS.intersection(active_ids)
    if unexpected_overlap:
        raise ValueError(f"new msgbre PC-only candidates overlap existing builder coordinates: {sorted(unexpected_overlap)}")
    candidate_already_active = False

    candidate_rows = [
        candidate_for(
            identifier,
            tables["jp"][identifier],
            tables["ko"][identifier],
            {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")},
            msgbre_hashes,
            strdata_tables["jp"],
            strdata_tables["ko"],
            strdata_hashes,
            support_tables,
            support_hashes,
        )
        for identifier in sorted(NEW_CANDIDATE_IDS)
    ]
    candidates_by_id = {row["id"]: row for row in candidate_rows}
    if set(candidates_by_id) != NEW_CANDIDATE_IDS:
        raise ValueError("msgbre candidate rows differ from the reviewed high-confidence set")

    audit_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    for identifier in range(ENTRY_COUNT):
        source = tables["jp"][identifier]
        current = tables["ko"][identifier]
        references = {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")}
        if not source:
            disposition = "internal_blank_slot"
            detail = "unused internal table slot; all PC language tables are blank"
            same_source_coordinate = None
            cross_resource_text = None
            gates = {name: True for name in SOURCE_GATES}
        else:
            same_source_coordinate = exact_same_source_coordinate(identifier, source, strdata_tables["jp"], source_to_strdata)
            cross_resource_text = strdata_tables["ko"].get(same_source_coordinate) if same_source_coordinate is not None else None
            gates = gate_result(source, current)
            if identifier in active_ids and identifier not in NEW_CANDIDATE_IDS:
                disposition = "active_existing_candidate"
                detail = "already present in current msgbre builder inputs; excluded from duplicate proposal"
            elif identifier in candidates_by_id:
                disposition = "active_new_candidate" if identifier in active_ids else "candidate_high_confidence"
                detail = candidates_by_id[identifier]["issue_type"]
            elif identifier in AMBIGUOUS_HOLDS:
                disposition = "hold_ambiguous_pc_only"
                detail = AMBIGUOUS_HOLDS[identifier]
            else:
                disposition = "retained_after_pc_only_gates"
                detail = "no high-confidence meaning, proper-name, quantity, relation, status, death, exile, or outcome error found from PC-only evidence"
        row = {
            "schema": "nobu16.kr.msgbre-pc-only-full-audit.v1",
            "resource": "msgbre",
            "id": identifier,
            "disposition": disposition,
            "disposition_detail": detail,
            "source_jp": source,
            "source_jp_utf16le_sha256": text_hash(source),
            "current_ko": current,
            "current_ko_utf16le_sha256": text_hash(current),
            "reference_contexts": references,
            "source_file_sha256": msgbre_hashes["jp"],
            "current_file_sha256": msgbre_hashes["ko"],
            "reference_file_sha256": {language.upper(): msgbre_hashes[language] for language in ("en", "sc", "tc")},
            "semantic_gate_pass": gates,
            "same_source_pc_strdata_coordinate": None if same_source_coordinate is None else f"{same_source_coordinate[0]}:{same_source_coordinate[1]}",
            "same_source_pc_strdata_current_ko": cross_resource_text,
            "same_source_pc_strdata_diverges": None if cross_resource_text is None else cross_resource_text != current,
            "audit_scope": {
                "pristine_pc_japanese": True,
                "current_pc_korean": True,
                "pc_en_sc_tc_references": True,
                "current_pc_strdata_same_source_only": True,
                "switch_korean_read": False,
                "historic_korean_read": False,
                "steam_game_resource_written": False,
            },
        }
        audit_rows.append(row)
        if disposition == "hold_ambiguous_pc_only":
            hold_rows.append(row)

    # This is a conservative lexical screen: a nonzero count means that the
    # exact wording did not expose a matching marker, not that an error was
    # automatically asserted.  Each row retains the PC source, Korean, and
    # EN/SC/TC context so those signals stay auditable without changing text.
    semantic_marker_parity_signal_counts = {
        name: sum(not row["semantic_gate_pass"][name] for row in audit_rows if row["source_jp"])
        for name in SOURCE_GATES
    }
    summary = {
        "schema": "nobu16.kr.msgbre-pc-only-full-audit-summary.v1",
        "entry_count": len(audit_rows),
        "populated_entry_count": POPULATED_ENTRY_COUNT,
        "internal_blank_slot_count": ENTRY_COUNT - POPULATED_ENTRY_COUNT,
        "active_builder_candidate_count": len(active_ids),
        "new_candidate_already_active": candidate_already_active,
        "new_high_confidence_candidate_count": len(candidate_rows),
        "ambiguous_hold_count": len(hold_rows),
        "same_source_pc_strdata_match_count": sum(row["same_source_pc_strdata_coordinate"] is not None for row in audit_rows if row["source_jp"]),
        "same_source_pc_strdata_divergence_count": sum(bool(row["same_source_pc_strdata_diverges"]) for row in audit_rows),
        "semantic_marker_parity_signal_counts": semantic_marker_parity_signal_counts,
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in audit_rows).items())),
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }
    return audit_rows, candidate_rows, hold_rows, summary


def validate_rows(
    audit_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    if len(audit_rows) != ENTRY_COUNT or {row["id"] for row in audit_rows} != set(range(ENTRY_COUNT)):
        raise ValueError("full msgbre audit does not cover every 0..2999 coordinate exactly once")
    if {row["id"] for row in candidate_rows} != NEW_CANDIDATE_IDS:
        raise ValueError("high-confidence msgbre candidate set differs from reviewed set")
    if {row["id"] for row in hold_rows} != set(AMBIGUOUS_HOLDS):
        raise ValueError("ambiguous msgbre hold set differs from reviewed set")
    if any(row["id"] in AMBIGUOUS_HOLDS for row in candidate_rows):
        raise ValueError("candidate/hold partitions overlap")
    for row in candidate_rows:
        if row["ko"] == row["proposed_ko"] or text_hash(row["ko"]) != row["current_hash"]:
            raise ValueError(f"msgbre:{row['id']} candidate text/hash gate is invalid")
        if format_profile(row["ko"]) != format_profile(row["proposed_ko"]):
            raise ValueError(f"msgbre:{row['id']} proposal changes its format profile")
        if KANA_OR_HAN_RE.search(row["proposed_ko"]) or not HANGUL_RE.search(row["proposed_ko"]):
            raise ValueError(f"msgbre:{row['id']} proposal contains CJK or lacks Hangul")
    for row in audit_rows:
        scope = row["audit_scope"]
        if scope["switch_korean_read"] or scope["historic_korean_read"] or scope["steam_game_resource_written"]:
            raise ValueError("audit scope must remain PC-only and read-only")
    if summary.get("entry_count") != ENTRY_COUNT or summary.get("new_high_confidence_candidate_count") != len(NEW_CANDIDATE_IDS):
        raise ValueError("msgbre audit summary is inconsistent")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE_OUTPUT)
    parser.add_argument("--hold-output", type=Path, default=DEFAULT_HOLD_OUTPUT)
    parser.add_argument("--write", action="store_true", help="write private PC-only audit, candidate, and hold JSONL files")
    parser.add_argument("--validate", action="store_true", help="validate generated data and any existing deterministic outputs")
    args = parser.parse_args()

    outputs = {
        "audit": safe_under(args.audit_output, AUDIT_ROOT),
        "candidate": safe_under(args.candidate_output, AUDIT_ROOT),
        "hold": safe_under(args.hold_output, AUDIT_ROOT),
    }
    audit_rows, candidate_rows, hold_rows, summary = build_rows()
    validate_rows(audit_rows, candidate_rows, hold_rows, summary)
    payloads = {
        "audit": deterministic_jsonl(audit_rows),
        "candidate": deterministic_jsonl(candidate_rows),
        "hold": deterministic_jsonl(hold_rows),
    }
    if args.write:
        for key in ("audit", "candidate", "hold"):
            atomic_write(outputs[key], payloads[key])
    if args.validate:
        for key in ("audit", "candidate", "hold"):
            if outputs[key].exists() and outputs[key].read_text(encoding="utf-8") != payloads[key]:
                raise ValueError(f"existing {key} output differs from deterministic PC-only evidence")
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
