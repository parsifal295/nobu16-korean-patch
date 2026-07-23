#!/usr/bin/env python3
"""Build the PC-only static third repair wave for Korean dialogue grammar.

This wave deliberately rebuilds only fully static records: after their
literal spans are removed, the original record may contain only explicitly
pinned ``01 43 <u32>`` fragments and the normal ``05 05 05`` terminator.
Records carrying a runtime name, target, colour, or other opcode are excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME = REPO / "workstreams" / "msggame"
sys.path[:0] = [str(TOOLS), str(MSGGAME)]

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
)


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"
TERMINATOR = b"\x05\x05\x05"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-runtime-grammar-wave3-static.v1"

# Exact installed state after wave two.  All eleven PC text resources form one
# transaction profile; this builder may change only the two msggame resources.
BASELINE_SHA256 = {
    "MSG/JP/ev_strdata.bin": "25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834",
    "MSG/JP/msggame.bin": "663EB8100A40AF5DE86810C0836EDCEF0A23C3AC2F01D461F9254BC73AA14900",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "9572873D2BBFF3C62581F09BE2CD54225CCDD2C400D3ACC895675E2C0A2780DD",
    "MSG_PK/JP/msggame.bin": "B3B541A86E882BA89FBC46B32FF129E269E7EDE09B17D9CC2DA6F7ED82112E6A",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
PROFILE_PATHS = tuple(BASELINE_SHA256)
CHANGED_PATHS = ("MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin")

# These values were generated from the source-gated candidate contract below.
# The normal build and installed-state verifier require this exact output.
TARGET_SHA256 = {
    **BASELINE_SHA256,
    "MSG/JP/msggame.bin": "C61B7157A957C43B797743203A9F2F8E80775C543871CAE76C3C53354D0B1DD8",
    "MSG_PK/JP/msggame.bin": "BE349DADD267AF608BC7BABD38A2FCDADEC69EC6C154A6229620FC451C718FEA",
}

PRISTINE_SOURCES = {
    "MSG/JP/msggame.bin": (
        Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "MSG_PK/JP/msggame.bin": (
        Path(
            r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
            r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin"
        ),
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
}


class WaveError(ValueError):
    """A source, record, or transaction contract did not match."""


@dataclass(frozen=True)
class StaticPlan:
    block_id: int
    record_id: int
    expected_sha256: str
    expected_commands: tuple[bytes, ...]
    text: str

    @property
    def coordinate(self) -> tuple[int, int]:
        return self.block_id, self.record_id


def plan(
    block_id: int,
    record_id: int,
    expected_sha256: str,
    commands: tuple[str, ...],
    text: str,
) -> StaticPlan:
    decoded = tuple(bytes.fromhex(value) for value in commands)
    if not decoded or any(len(value) != 6 or value[:2] != b"\x01\x43" for value in decoded):
        raise ValueError(f"invalid 0143 contract for {block_id}:{record_id}")
    return StaticPlan(block_id, record_id, expected_sha256, decoded, text)


# Each planned Korean string is a full sentence.  No plan carries a runtime
# token; names, targets, colours, and records that were already complete are
# intentionally deferred to separate runtime/visual QA work.
BASE_PLANS = (
    plan(13, 9, "EF16BD15A1EFEF0C455312B8EEA8A6B6DD94B6D897B4526CDF69FF5DC15F9787", ("01433C040000",), "일동 수고했다!\n지금부터 평정을 시작한다!\n고개를 들라!"),
    plan(13, 28, "3FA8A6644CC9AF3056F07DD23FC2C4898BA5D662A79013F7255847A9A0D63172", ("01435A040000",), "당가가 우선 이루어야 할 일은 타국을 공략할\n국력을 기르는 것입니다.\n당분간은 내정에 힘쓰는 것이 좋겠습니다."),
    plan(13, 33, "2607C85B5FCA6B714CB3454C45294F29D00B1F9D80C2A14E7093106FB5C0C926", ("01433C040000",), "각 군은 가신에게 맡길 수 있으며, 각 무장은\n독자적인 판단으로 자신의 영지를 다스린다."),
    plan(13, 36, "ED29C165BB0A477C3B341BE2A73D0A75E4AE70B2B8B5FCB9993FC9943AD3D406", ("01431A020000",), "그렇게 군의 개발이 차츰 진행되면\n생산성이 오르고 재정도 윤택해진다는\n뜻입니다."),
    plan(13, 40, "EA712B3006D1262515A2361FC1C54EA19B9FC1823A5325745AD428C300982CD1", ("01431E040000",), "분부대로!\n그럼 무엇부터 시작할까요?"),
    plan(13, 49, "C920B666D551F0DC6BADAF0E913CE34827846E2A454DD72B504C2A73B3633699", ("01431A020000",), "외교로 타국과 좋은 관계를 맺고\n동맹을 맺어 원군을 청하는 일도\n천하로 나아가는 중요한 수단입니다."),
    plan(13, 55, "25C0CFA3C7CCF149644B02EB19C8D91C31B10EE0AA7AB6FE58597B4F100F1496", ("014352000000", "01433C040000"), "그 밖에도 당가와 동맹을 맺은\n세력이 있습니다. 평정의\n「외교」에서 확인할 수 있습니다."),
    plan(13, 85, "7C4271E290F81EFF39E79BD363614AC8F41C4D724647B75F1924987C9C00A5AC", ("01434A020000",), "합전에서 활약하거나 군을 다스려\n공훈을 인정받으면 출세의 길이\n열리는 셈이지."),
    plan(13, 87, "84777214F5DA624BB9747FB41F0DB57B670FD02BB32522E589BA1F8D8B25EE32", ("014324040000",), "우선 본거지에 속한 군의 대관으로서\n공훈을 세우게 하고 신분을 올린 뒤,\n지행지를 맡기는 것이 좋겠습니다."),
    plan(13, 106, "307EFBA09A5C0EA987375A5CE77CB35243D68A5ABF0205757B546B77CD68B5DB", ("014336040000", "0143C8020000"), "또한 통솔력이 뛰어나므로\n군의 발전과 전투 때에도 큰 도움이 될 것입니다."),
    plan(13, 108, "AED874395219809ABE0E737773C0BAAFA3F48FA2947D12B2A1D54F21620BB150", ("0143B2000000", "014356020000"), "또한 지략가로도 이름나 있어,\n조략이나 외교 같은 분야에서 그 재능을\n발휘할 수 있을 것입니다."),
    plan(13, 116, "3BD26A5BF445C1A2FA3EE0F191CAB429AF259C918BCD7ABC0F92070E91B97CD7", ("014384010000", "01431E040000"), "다만… 각 분야의 능력에는 딱히\n내세울 만한 것이 없으나,\n특성의 힘으로 활약해 보이겠습니다."),
    plan(13, 122, "86DE606A016ED72F8B8374E8BF8D81A2F16EC4AAB91E4FAC0A3DEBB4871CF9B0", ("0143DA020000", "01431E040000"), "특별한 특성은 없지만,\n능력을 살릴 수 있는 곳에서 일하게 하면\n반드시 활약할 수 있습니다."),
    plan(13, 127, "5E0386D27637027A0EC7012B0609148A78BABFFE9D162CD5CD02FEBFBA570049", ("0143B2000000", "014342010000"), "게다가 남만큼 특성도 갖추고 있으니,\n부디 능력을 잘 발휘할 자리를\n마련해 주십시오."),
    plan(13, 128, "8CCBC7A05BCE1D289B5444573FFF230DFDF5EF76DEF8C4A6F869BE69AEBD02D7", ("0143DA020000",), "부끄럽지만, 특성은 없으니\n지닌 능력을 살릴 자리를 마련해 주신다면\n더없이 감사하겠습니다…"),
    plan(13, 136, "EF16BD15A1EFEF0C455312B8EEA8A6B6DD94B6D897B4526CDF69FF5DC15F9787", ("01433C040000",), "일동 수고했다!\n지금부터 평정을 시작한다!\n고개를 들라!"),
    plan(13, 176, "7C4271E290F81EFF39E79BD363614AC8F41C4D724647B75F1924987C9C00A5AC", ("01434A020000",), "합전에서 활약하거나 군을 다스려\n공훈을 인정받으면 출세의 길이\n열리는 셈이지."),
    plan(13, 178, "84777214F5DA624BB9747FB41F0DB57B670FD02BB32522E589BA1F8D8B25EE32", ("014324040000",), "우선 본거지에 속한 군의 대관으로서\n공훈을 세우게 하고 신분을 올린 뒤,\n지행지를 맡기는 것이 좋겠습니다."),
    plan(16, 15, "FA6B85D02E80F65D205893D5277BE202692C8AEDD8CF273944E0465A0CC69532", ("01431E040000",), "자, 개발 용지에\n무엇을 지을까?"),
    plan(16, 29, "7BE443F5ECF36AEEC5D9FF976BD1B6F6240E2185A64DBDC93599FC7AD9654B54", ("01432C020000",), "우리 영지는 더할 나위 없이\n번영하고 있는 듯하군."),
    plan(16, 32, "8C1D40B52D3A840AD7FBD7B3DE54CF04FF8DEDE58A9535A8B405D4A5861ABC46", ("014356020000",), "이 가문을 계속 섬겨도\n괜찮은 걸까…"),
    plan(16, 36, "B7CF9FC6A8A745E9121E723F149A49BF5F65B4219D0014BFB753934F29C489A8", ("01431E040000",), "공략 목표가 정해지면\n군비를 갖추자."),
    plan(16, 43, "A2C8B142F8B422C0F3154FCEAB0399A5B1D05037081BD458D9D64ECDC9479836", ("01432C020000",), "위신을 좌우하는 것은\n주로 지배하는 성의 수다."),
    plan(16, 46, "838D48FF60BDCA217E8FB99AC7981E1C14D188BD00D77ACE7C993E5B32F1F42C", ("014304030000",), "콜록, 쿨럭…\n어서 나아야 하는데…"),
)

PK_PLANS = (
    plan(13, 9, "246CE2CC75E779FB7BDF49AF2A9D74B0BBC2A11289F1625E8EE960DF9F15318E", ("014348040000",), "일동 수고했다!\n지금부터 평정을 시작한다!\n고개를 들라!"),
    plan(13, 28, "DE4556531302C8721A35F0D917164279EB57F91AF5605AC420F451D5785895BF", ("014366040000",), "당가가 우선 이루어야 할 일은 타국을 공략할\n국력을 기르는 것입니다.\n당분간은 내정에 힘쓰는 것이 좋겠습니다."),
    plan(13, 33, "843CB024B9DF2A6838F4C6993D448D078457EADEDB6DCD903DD8D7D68EDED620", ("014348040000",), "각 군은 가신에게 맡길 수 있으며,\n무장마다 스스로의 판단으로 영지를 다스립니다."),
    plan(13, 36, "97E588CDD65C7637AC5AEDB195446F204A8657E20C5E8E4ED27013D07BAD098B", ("014326020000",), "그리하여 군 개발이 차츰 진행되면\n생산성이 오르고 재정도 넉넉해집니다."),
    plan(13, 40, "63F3E7ED65A24705354BDEDB6E7AF7765CFB29BC6E7340E448E7FDCDED922DFE", ("01432A040000",), "분부대로!\n그럼 무엇부터 시작할까요?"),
    plan(13, 49, "54AFCC1A46925D61CB118852DFFC13E85949606325DDD99979ADE234F813C2C7", ("014326020000",), "외교로 타국과 우호 관계를 맺고\n동맹을 맺어 원군을 청하는 일도…\n천하로 나아가는 중요한 수단입니다."),
    plan(13, 55, "72C96C3215DA020337C6D6C1598B1A7BC157712871E65932D8A28A4DBE31DBB4", ("014352000000", "014348040000"), "그 밖에도 당가와 동맹 중인\n세력이 있습니다. 평정의\n「외교」에서 확인할 수 있습니다."),
    plan(13, 85, "38981BCECFA3D8CC27FE0BBC5133D80ACF235442FE49BFF42509279959E343C7", ("014356020000",), "전투에서 활약하거나 군을 다스려\n공훈을 인정받으면 출세의 길이\n열립니다."),
    plan(13, 87, "0B23DD3BE757DDF5E5EAFC37BE9409596DCE8598F84ACE0979AABF61ED683F10", ("014330040000",), "우선 본거지에 속한 군의 대관으로서\n공훈을 세워 신분을 올린 뒤\n지행지를 맡기는 것이 좋겠습니다."),
    plan(13, 106, "6F4994A7043391F3DBE670C13BAFB4FEF19E7F335E1194720F661BC6D55739F1", ("014342040000", "0143D4020000"), "또한 통솔력이 뛰어나므로\n군의 발전과 전쟁에서도 든든한 도움이 될 것입니다."),
    plan(13, 108, "15AF993B925F4D0408645821EC322F50D8305920A372797DCBD0E8C459F8B183", ("0143B2000000", "014362020000"), "또한 지혜로운 인물로 알려져 있으며,\n조략과 외교 같은 분야에서\n그 재능을 발휘할 것입니다."),
    plan(13, 116, "A37B8A85BA43B8F930C370F67B234D960CF3DDE5BB4D2EABC292E524998F5CEE", ("01438A010000", "01432A040000"), "다만 각 분야의 능력에는\n내세울 만한 것이 없습니다.\n특성의 힘으로 활약해 보이겠습니다."),
    plan(13, 122, "39AB8FDBDDCFB95020781FBF080D4543A0DF43CB4BB4FF59180D7D02E3874101", ("0143E6020000", "01432A040000"), "특별한 특성은 없으나,\n그 능력을 살릴 수 있는 곳에서 일하게 하면\n반드시 활약할 수 있습니다."),
    plan(13, 127, "5E0386D27637027A0EC7012B0609148A78BABFFE9D162CD5CD02FEBFBA570049", ("0143B2000000", "014342010000"), "게다가 남만큼 특성도 갖추고 있으니,\n부디 능력을 잘 발휘할 자리를\n마련해 주십시오."),
    plan(13, 128, "6BD6A8B8E0B39326CC35B05B865C4224237463414A7AD7991DFE79BD8D4EB87B", ("0143E6020000",), "부끄럽지만, 특별한 특성은 없습니다.\n지닌 능력을 살릴 자리를 주신다면\n더없이 감사하겠습니다…"),
    plan(13, 136, "246CE2CC75E779FB7BDF49AF2A9D74B0BBC2A11289F1625E8EE960DF9F15318E", ("014348040000",), "일동 수고했다!\n지금부터 평정을 시작한다!\n고개를 들라!"),
    plan(13, 176, "38981BCECFA3D8CC27FE0BBC5133D80ACF235442FE49BFF42509279959E343C7", ("014356020000",), "전투에서 활약하거나 군을 다스려\n공훈을 인정받으면 출세의 길이\n열립니다."),
    plan(13, 178, "0B23DD3BE757DDF5E5EAFC37BE9409596DCE8598F84ACE0979AABF61ED683F10", ("014330040000",), "우선 본거지에 속한 군의 대관으로서\n공훈을 세워 신분을 올린 뒤\n지행지를 맡기는 것이 좋겠습니다."),
    plan(16, 15, "4336BB7CFBAF4BCF815CBF2477C53587A4F4DB80EE24676E5ADB0824C619F85F", ("01432A040000",), "자, 개발 용지에\n무엇을 지을 것인가?"),
    plan(16, 32, "706CF01C773F94CDCA497C62FA078EE3B0DE3D1C66050A6073B04181BEEEC596", ("014362020000",), "이 가문을 계속 섬겨도\n괜찮을까…"),
    plan(16, 36, "1B1B2B4A85EB321707D379F812E5E07C55161606C83F49E05D84CB13FC8D4302", ("01432A040000",), "공략 목표가 정해지면\n군비를 갖춰야겠지."),
    plan(16, 42, "3C072963BDAA9AD1B232A0AD309D0E620B7DB89BF5A06D6EFF560ED47C7BE57E", ("014338020000",), "금전은 정책에 써야\n나라를 부유하게 하는 왕도다."),
    plan(16, 43, "124001F3D023B41F926F69BD957D9FC1D319E640A303E41B7199B92BEA26FE81", ("014342040000",), "다스리는 성이 많을수록\n나라의 위신도 높아집니다."),
    plan(16, 45, "4CAF25A20A3ABE3ADCCCFADEF512C4EFE3F22D81CD07FD339276644A15C786D2", ("014338020000",), "군에 영주가 있다면\n개발도 더욱 진척될 텐데…"),
    plan(16, 46, "9955AFE4B5ACC44ED41B52B14F6EF7F83087E8966521A9128BAE4BF12AD678A8", ("014310030000",), "콜록, 쿨럭…\n어서 나아야 할 텐데."),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise WaveError(f"{label} escapes allowed root: {resolved_path}") from exc
    return resolved_path


def profile_hashes(root: Path) -> dict[str, str]:
    return {
        relative: sha256_path(require_under(root, root / relative, "profile file"))
        for relative in PROFILE_PATHS
    }


def assert_profile(root: Path, expected: dict[str, str], label: str) -> None:
    actual = profile_hashes(root)
    if actual == expected:
        return
    mismatch = {
        path: {"expected": expected[path], "actual": actual[path]}
        for path in PROFILE_PATHS
        if actual[path] != expected[path]
    }
    raise WaveError(f"{label} SHA-256 profile mismatch: {json.dumps(mismatch, ensure_ascii=False)}")


def plans_for(relative: str) -> tuple[StaticPlan, ...]:
    if relative == "MSG/JP/msggame.bin":
        return BASE_PLANS
    if relative == "MSG_PK/JP/msggame.bin":
        return PK_PLANS
    raise WaveError(f"unsupported message resource: {relative}")


def validate_plan_set(plans: tuple[StaticPlan, ...], relative: str) -> None:
    coordinates = [item.coordinate for item in plans]
    if len(coordinates) != len(set(coordinates)):
        raise WaveError(f"duplicate plan coordinate in {relative}")
    for item in plans:
        lines = item.text.split("\n")
        if not 1 <= len(lines) <= 3 or any(not line for line in lines):
            raise WaveError(f"{relative} {item.block_id}:{item.record_id} is not a 1–3 line sentence")
        if any(character in item.text for character in "、。！？"):
            raise WaveError(f"{relative} {item.block_id}:{item.record_id} contains Japanese punctuation")


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(packed).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def opaque_bytes(record: MsgGameRecord) -> bytes:
    literals = parse_record_literals(record)
    if not literals:
        raise WaveError(f"{record.block_id}:{record.record_id} has no literal span")
    output = bytearray()
    cursor = 0
    for literal in literals:
        output.extend(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


def expected_record_data(item: StaticPlan) -> bytes:
    encoded = item.text.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise WaveError(f"reserved literal marker in replacement {item.coordinate}")
    return LITERAL_START + encoded + LITERAL_END + TERMINATOR


def validate_current_record(record: MsgGameRecord, item: StaticPlan, relative: str) -> None:
    actual_hash = sha256_bytes(record.data)
    if actual_hash != item.expected_sha256:
        raise WaveError(
            f"{relative} {item.block_id}:{item.record_id} SHA-256 mismatch: "
            f"expected {item.expected_sha256}, got {actual_hash}"
        )
    expected_opaque = b"".join(item.expected_commands) + TERMINATOR
    actual_opaque = opaque_bytes(record)
    if actual_opaque != expected_opaque:
        raise WaveError(
            f"{relative} {item.block_id}:{item.record_id} opaque bytecode mismatch: "
            f"expected {expected_opaque.hex().upper()}, got {actual_opaque.hex().upper()}"
        )


def rebuild_static_resource(packed: bytes, plans: tuple[StaticPlan, ...], relative: str) -> bytes:
    validate_plan_set(plans, relative)
    before = records_by_coordinate(packed)
    replacements: dict[tuple[int, int], bytes] = {}
    for item in plans:
        try:
            record = before[item.coordinate]
        except KeyError as exc:
            raise WaveError(f"{relative} missing record {item.coordinate}") from exc
        validate_current_record(record, item, relative)
        replacements[item.coordinate] = expected_record_data(item)

    rebuilt = rebuild_packed_msggame(packed, replacements)
    after = records_by_coordinate(rebuilt)
    if set(after) != set(before):
        raise WaveError(f"{relative} record topology changed")
    for coordinate, original in before.items():
        expected = replacements.get(coordinate, original.data)
        if after[coordinate].data != expected:
            raise WaveError(f"{relative} {coordinate} rebuilt record does not match its contract")
    for item in plans:
        if b"\x01\x43" in after[item.coordinate].data:
            raise WaveError(f"{relative} {item.coordinate} retained a 0143 command")
        literals = parse_record_literals(after[item.coordinate])
        if len(literals) != 1 or literals[0].text != item.text:
            raise WaveError(f"{relative} {item.coordinate} literal reconstruction mismatch")
    return rebuilt


def assert_pristine_sources() -> dict[str, str]:
    actual: dict[str, str] = {}
    for relative, (path, expected_hash) in PRISTINE_SOURCES.items():
        if not path.is_file():
            raise WaveError(f"missing PC JP pristine source: {path}")
        actual_hash = sha256_path(path)
        if actual_hash != expected_hash:
            raise WaveError(
                f"PC JP pristine source mismatch for {relative}: "
                f"expected {expected_hash}, got {actual_hash}"
            )
        source_records = records_by_coordinate(path.read_bytes())
        for item in plans_for(relative):
            if item.coordinate not in source_records:
                raise WaveError(f"PC JP source lacks {relative} {item.coordinate}")
        actual[relative] = actual_hash
    return actual


def assert_pristine_layout_matches_steam(steam_root: Path) -> None:
    """Require the PC-JP source to have the exact current PC record layout.

    A whole-file hash proves identity, but not that a previously selected
    pristine file belongs to the installed PC release.  Compare every message
    block's record count with the actual PC profile before using it as a
    translation source; a mismatched release can otherwise make valid-looking
    coordinates refer to different dialogue.
    """
    steam_root = steam_root.resolve()
    for relative, (source_path, _expected_hash) in PRISTINE_SOURCES.items():
        source_archive = parse_packed_msggame(source_path.read_bytes()).archive
        steam_path = require_under(steam_root, steam_root / relative, "Steam input")
        steam_archive = parse_packed_msggame(steam_path.read_bytes()).archive
        source_counts = tuple(len(block.records) for block in source_archive.blocks)
        steam_counts = tuple(len(block.records) for block in steam_archive.blocks)
        if source_counts != steam_counts:
            raise WaveError(
                f"PC JP source layout mismatch for {relative}: "
                f"source={source_counts}, steam={steam_counts}"
            )


def target_is_pinned() -> bool:
    return all(TARGET_SHA256[path] for path in CHANGED_PATHS)


def candidate_manifest(
    input_hashes: dict[str, str],
    output_hashes: dict[str, str],
    source_hashes: dict[str, str],
) -> dict[str, object]:
    def render(item: StaticPlan) -> dict[str, object]:
        data = asdict(item)
        data["expected_commands"] = [value.hex().upper() for value in item.expected_commands]
        data["coordinate"] = f"{item.block_id}:{item.record_id}"
        return data

    return {
        "schema": MANIFEST_SCHEMA,
        "transaction_id": "pc-dialogue-runtime-grammar-wave3-static-v1",
        "input_sha256": input_hashes,
        "output_sha256": output_hashes,
        "pinned_output_sha256": TARGET_SHA256 if target_is_pinned() else None,
        "pristine_pc_jp_sha256": source_hashes,
        "changed_paths": list(CHANGED_PATHS),
        "base_plan_count": len(BASE_PLANS),
        "pk_plan_count": len(PK_PLANS),
        "base_plans": [render(item) for item in BASE_PLANS],
        "pk_plans": [render(item) for item in PK_PLANS],
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_candidate(
    steam_root: Path,
    output_root: Path,
    manifest_path: Path,
    allow_unpinned_output: bool,
) -> dict[str, object]:
    steam_root = steam_root.resolve()
    output_root = require_under(REPO, output_root, "candidate output")
    manifest_path = require_under(REPO, manifest_path, "manifest output")
    if output_root.exists():
        raise WaveError(f"candidate output already exists: {output_root}")
    input_hashes = profile_hashes(steam_root)
    if input_hashes != BASELINE_SHA256:
        assert_profile(steam_root, BASELINE_SHA256, "installed input")
        raise AssertionError("unreachable")
    source_hashes = assert_pristine_sources()
    assert_pristine_layout_matches_steam(steam_root)

    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(require_under(steam_root, steam_root / relative, "Steam input"), target)
        for relative in CHANGED_PATHS:
            source = require_under(steam_root, steam_root / relative, "Steam input")
            repaired = rebuild_static_resource(source.read_bytes(), plans_for(relative), relative)
            (stage / relative).write_bytes(repaired)
        output_hashes = profile_hashes(stage)
        if target_is_pinned():
            if output_hashes != TARGET_SHA256:
                mismatch = {
                    path: {"expected": TARGET_SHA256[path], "actual": output_hashes[path]}
                    for path in PROFILE_PATHS
                    if TARGET_SHA256[path] != output_hashes[path]
                }
                raise WaveError(f"candidate target SHA-256 mismatch: {json.dumps(mismatch)}")
        elif not allow_unpinned_output:
            raise WaveError("target SHA-256 is not pinned; use only --allow-unpinned-output to bootstrap it")
        manifest = candidate_manifest(input_hashes, output_hashes, source_hashes)
        os.replace(stage, output_root)
        write_json(manifest_path, manifest)
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def verify_installed(steam_root: Path) -> None:
    if not target_is_pinned():
        raise WaveError("target SHA-256 is not pinned in this source revision")
    steam_root = steam_root.resolve()
    assert_pristine_sources()
    assert_pristine_layout_matches_steam(steam_root)
    assert_profile(steam_root, TARGET_SHA256, "installed target")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Build a source-gated candidate without changing Steam")
    build.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    build.add_argument("--allow-unpinned-output", action="store_true")
    build.set_defaults(func=lambda args: build_candidate(
        args.steam_root, args.output_root, args.manifest, args.allow_unpinned_output
    ))
    verify = sub.add_parser("verify-installed", help="Require the exact pinned Wave 3 state")
    verify.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    verify.set_defaults(func=lambda args: verify_installed(args.steam_root))
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        outcome = args.func(args)
        if outcome is not None:
            print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
        else:
            print("OK")
        return 0
    except (OSError, ValueError, WaveError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
