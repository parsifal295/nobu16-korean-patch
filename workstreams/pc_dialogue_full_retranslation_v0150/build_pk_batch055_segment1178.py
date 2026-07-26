#!/usr/bin/env python3
"""Build source-redacted PK B055 segment 1178 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch055_segment1176.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B055_S1178.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = REPO / "tmp" / WORKSTREAM.name / "base_msggame_runtime_vm_verified.private.v1.jsonl"
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B055_S1176.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B055_S1177.private.v1.jsonl",
)
STEAM_PK = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin")
SEGMENT = 1178
QUEUE_BATCH_ID = "pk_msggame-B055"
QUEUE_START, QUEUE_STOP = 134, 199
BLOCK_ID, PK_RECORD_COUNT = 7, 21_751
TARGET_COORDINATES = (
    "7:765:1","7:767:0","7:767:1","7:768:0","7:768:1","7:769:0","7:769:1",
    "7:770:0","7:770:1","7:771:0","7:771:1","7:772:0","7:772:1","7:773:0",
    "7:773:1","7:774:0","7:775:0","7:775:1","7:776:0","7:776:1","7:777:1",
    "7:778:0","7:779:0","7:779:1","7:780:0","7:780:1","7:781:0","7:781:1",
    "7:782:0","7:782:1","7:783:0","7:783:1","7:784:0","7:784:1","7:785:0",
    "7:785:1","7:786:0","7:786:1","7:787:0","7:787:1","7:789:0","7:790:0",
    "7:790:1","7:791:0","7:791:1","7:792:0","7:793:0","7:793:1","7:794:0",
    "7:794:1","7:795:0","7:795:1","7:797:0","7:797:1",
)
TRANSLATIONS = {
    "7:765:1":"」은(는) 차지했다!","7:767:0":"적 본거지 「","7:767:1":"」을(를) 빼앗았도다!",
    "7:768:0":"적 본거지 「","7:768:1":"」은(는) 내 손안에 있다","7:769:0":"적 본거지 「",
    "7:769:1":"」을(를) 함락시켰도다!","7:770:0":"적 본거지 「","7:770:1":"」을(를) 손에 넣었다!",
    "7:771:0":"적 본거지 「","7:771:1":"」은(는) 차지하겠다!","7:772:0":"적 본거지 「",
    "7:772:1":"」을(를) 제압한 것은 우리다!","7:773:0":"적 본거지 「","7:773:1":"」은(는) 차지했사옵니다",
    "7:774:0":"적 본거지","7:775:0":"적 본거지 「","7:775:1":"」은(는) 우리가 차지했다!",
    "7:776:0":"적 본거지 「","7:776:1":"」을(를) 함락시켰다!","7:777:1":"」을(를) 함락시켰다!",
    "7:778:0":"적 본거지","7:779:0":"적 본거지 「","7:779:1":"」은(는) 우리가 차지했다",
    "7:780:0":"적 본거지 「","7:780:1":"」을(를) 함락시켰노라!","7:781:0":"적 본거지 「",
    "7:781:1":"」은(는) 넘겨받았습니다","7:782:0":"적 본거지 「","7:782:1":"」을(를) 제압했습니다",
    "7:783:0":"적 본거지 「","7:783:1":"」을(를) 제압했다!","7:784:0":"적 본거지 「",
    "7:784:1":"」은(는) 기어코 함락시켰노라!","7:785:0":"적 본거지 「","7:785:1":"」을(를) 함락시켰사옵니다",
    "7:786:0":"적 본거지 「","7:786:1":"」을(를) 기어코 제압했소이다","7:787:0":"적 본거지 「",
    "7:787:1":"」은(는) 우리 것이로다!","7:789:0":"적 본거지","7:790:0":"적 본거지 「",
    "7:790:1":"」을(를) 제압한 것은 우리다!","7:791:0":"적 본거지 「","7:791:1":"」은(는) 제가 차지했습니다",
    "7:792:0":"적 본거지","7:793:0":"적 본거지 「","7:793:1":"」을(를) 내 것으로 삼았노라!",
    "7:794:0":"적 본거지 「","7:794:1":"」을(를) 우리가 공략해 빼앗았다!","7:795:0":"적 본거지 「",
    "7:795:1":"」을(를) 손에 넣었습니다","7:797:0":"적 본거지 「","7:797:1":"」은(는) 우리 것이다!",
}
TARGET_RECORD_IDS = tuple(dict.fromkeys(int(c.split(":")[1]) for c in TARGET_COORDINATES))
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {record_id: 2 for record_id in TARGET_RECORD_IDS}
PREFILL_COMPANION_COORDINATES = ("7:765:0","7:774:1","7:777:0","7:778:1","7:789:1","7:792:1")
PREFILL_BASE_COORDINATE_OVERRIDES: dict[str, str] = {}
PRIMARY_BASE_DONOR = {record_id: (7, record_id - 8) for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_RAW_MATCHES = {r: (PRIMARY_BASE_DONOR[r],) for r in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple((7, r) for r in (673,674,763,764,765,766,767,796,797))
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {r: ((), ("026432",)) for r in TARGET_RECORD_IDS}
SPEAKER_STYLE = tuple((r, "enemy_home_castle_capture_register") for r in TARGET_RECORD_IDS)
TERMINOLOGY_POLICY = (("enemy headquarters","적 본거지"),("capture","공략"),("fall","함락"),("control","제압"))
EXPECTED_STEAM_PK_SHA256 = "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
EXPECTED_PRISTINE_PK_SHA256 = "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
EXPECTED_PREFILL_SHA256 = "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
EXPECTED_BASE_PROMOTED_SHA256 = "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
EXPECTED_QUEUE_UNIVERSE_SHA256 = "C550CDBFE345196261A77C7AFBC41A329E3BB13A71AA02C12ABE23A14504F87D"
EXPECTED_QUEUE_SLICE_SHA256 = "DDCBE8428FBCDD3199E2CFD703DEE5F35DA1BD35F3B2CAB5E3F1B5AED453477E"
EXPECTED_PREFILLED_COORDINATE_SHA256 = "31A06121953FD3CAC5E6FB53DEF388F8D2BD06268E8DF006E76B8792814F23C7"
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = "4606022ACF3D707894C74FDA4536CC110AB315B192C57F66618A6A87E9254D33"
EXPECTED_TARGET_COORDINATE_SHA256 = "8242B6ABABB265017CD1BDF8BE21AE0F46DB0484AD2C270BA468FD308A01145C"
EXPECTED_SOURCE_TARGET_SHA256 = "5C4E8A9DCE7B9522F90520F85E4E1CFDD21DB2187404B1894FB90B75B843C304"
EXPECTED_CURRENT_TARGET_SHA256 = "3FEA6397CD91B6B74BAC23109D62575B1C80ED5C09CFCCB705827EC76AB657D2"
EXPECTED_CONTEXT_CORPUS_SHA256 = "1946A7E28F71E53BA7325FDAE4E34E425CA5FF9A12A70074C1A5BB2605FB1CB3"
EXPECTED_GAP_CONTRACT_SHA256 = "C3813D252D26406F15027B64631C09D978C5EDA62588F8E221AF6C865EB5F8AE"
EXPECTED_BOUNDARY_SHA256 = "333F737FAC287BD57C874DA0CB784DA77BAE52C9E1B3AC060EEA0715C5549C6D"
EXPECTED_RUNTIME_CONTROL_SHA256 = "3E84668F978797CEAAF988B93C9F7090E976B6CE705993D5E702D2C4AD1C476A"
EXPECTED_BASE_SEARCH_SHA256 = "1F1DEDE913BDAFA89049FBB27548847D8EF2BEB8F160F3D066DFF9D913F784F3"
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = "93589A21CF1CE4B4A42A7082277F11D01AE072F905C96CA08CAE399968153E61"
EXPECTED_CALL_GRAPH_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
EXPECTED_SPEAKER_STYLE_SHA256 = "01CD2719963FC1D8EBABB7F308F43095B6BE7DF01CB120086503C6E6FF5D51B9"
EXPECTED_TERMINOLOGY_POLICY_SHA256 = "CAC0C1B2517771B5411336A98DEB8257FD686C2F1C55017732834523CEA38912"
EXPECTED_TRANSLATION_POLICY_SHA256 = "0740FF289FC070A92D7042DDB576FD705E08E8AA941A08BEDDB9B5D6CC88BAB3"
EXPECTED_CANDIDATE_SHA256 = "0BDA77D93F1459E8927E384BCC26710FB5C183B5B0F8006B3D8866EDAD0A824A"
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = "79B9EF6120707132344C562D40336924D9270DEBDEFE356CF2C79F1D317E8CAA"
EXPECTED_CHANGED_LITERAL_COUNT = 54
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 65
BASE_DONOR_TRAILING_SPACE_COORDINATES = {
    "7:774:0", "7:778:0", "7:789:0", "7:792:0",
}
DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete EN SC TC records reviewed; all thirty complete "
    "PK records have byte-exact completed Base donors whose Korean is manually selected for semantic "
    "consistency only; Base runtime and VM state are never inherited; eleven slice prefills and five "
    "same-record companions, dynamic castle tokens, paired quotes, particles, gaps, absence of calls, "
    "boundaries, reverse overlays, two-run reproduction, tamper rejection, outside-scope identity and "
    "Steam read-only state are guarded"
)

def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_s1178_base", BASE_PATH)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return module

BASE = load_base()
CORE, ENGINE = BASE.CORE, BASE.ENGINE
sha256_bytes, coordinate_key = BASE.sha256_bytes, BASE.coordinate_key
literal_texts, gap_bytes, read_jsonl, context_records = BASE.literal_texts, BASE.gap_bytes, BASE.read_jsonl, BASE.context_records

def read_jsonl_with_neighbor(path: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    if path.resolve(strict=False) == BASE_PROMOTED.resolve(strict=False):
        strip_coordinates = {"7:766:0", "7:770:0", "7:781:0", "7:784:0"}
        adapted = []
        for row in rows:
            copy = dict(row)
            if copy.get("coordinate") in strip_coordinates:
                copy["translation"] = str(copy["translation"]).rstrip(" ")
            adapted.append(copy)
        return adapted
    if path.resolve(strict=False) != PREFILL.resolve(strict=False):
        return rows
    neighbor_path = DECISIONS_ROOT / "pk_msggame_B055_S1177.private.v1.jsonl"
    neighbor = next(
        (
            dict(row)
            for row in read_jsonl(neighbor_path)
            if row.get("coordinate") == "7:765:0"
        ),
        None,
    )
    if (
        neighbor is None
        or neighbor.get("semantic_review") != "approved"
        or neighbor.get("runtime_review") != "pending"
        or neighbor.get("base_context_reference_coordinate") != "7:757:0"
        or neighbor.get("base_runtime_state_inherited") is not False
        or neighbor["runtime_assembly_evidence"]["runtime_promotion_authorized"]
        is not False
    ):
        raise RuntimeError("S1177 cross-slice companion drifted")
    neighbor["base_exact_reuse_prefill"] = {
        "base_coordinate": "7:757:0",
        "runtime_promotion_authorized": False,
    }
    return [*rows, neighbor]

def patch_globals() -> None:
    names = (
        "SCRIPT","OUTPUT","PREFILL","BASE_PROMOTED","SEGMENT","QUEUE_BATCH_ID","QUEUE_START","QUEUE_STOP",
        "BLOCK_ID","PK_RECORD_COUNT","TARGET_COORDINATES","TRANSLATIONS","STATIC_RECORD_IDS","TARGET_RECORD_IDS",
        "DYNAMIC_RECORD_IDS","STATIC_COORDINATES","DYNAMIC_COORDINATES","EXPECTED_ARITY",
        "PREFILL_COMPANION_COORDINATES","PREFILL_BASE_COORDINATE_OVERRIDES","PRIMARY_BASE_DONOR",
        "EXPECTED_BASE_RAW_MATCHES","EXPECTED_BASE_LITERAL_MATCHES","EXPECTED_BASE_MASKED_MATCHES",
        "BOUNDARY_RECORD_KEYS","SOURCE_CALL_ROOTS","CURRENT_CALL_ROOTS","EXPECTED_CONTROLS_BY_RECORD",
        "SPEAKER_STYLE","TERMINOLOGY_POLICY","EXPECTED_QUEUE_UNIVERSE_SHA256","EXPECTED_QUEUE_SLICE_SHA256",
        "EXPECTED_PREFILLED_COORDINATE_SHA256","EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
        "EXPECTED_TARGET_COORDINATE_SHA256","EXPECTED_SOURCE_TARGET_SHA256","EXPECTED_CURRENT_TARGET_SHA256",
        "EXPECTED_CONTEXT_CORPUS_SHA256","EXPECTED_GAP_CONTRACT_SHA256","EXPECTED_BOUNDARY_SHA256",
        "EXPECTED_RUNTIME_CONTROL_SHA256","EXPECTED_BASE_SEARCH_SHA256","EXPECTED_COMPLETE_ASSEMBLY_SHA256",
        "EXPECTED_CALL_GRAPH_SHA256","EXPECTED_SPEAKER_STYLE_SHA256","EXPECTED_TERMINOLOGY_POLICY_SHA256",
        "EXPECTED_TRANSLATION_POLICY_SHA256","EXPECTED_CANDIDATE_SHA256",
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256","EXPECTED_CHANGED_LITERAL_COUNT",
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT","DISCOVERED_PINS","BASIS",
    )
    for name in names: setattr(BASE, name, globals()[name])
    BASE.queue_evidence = queue_evidence
    BASE.assert_queue_and_residual_contract = assert_queue_and_residual_contract
    BASE.build_combined_slice_candidate = build_combined_slice_candidate
    BASE.read_jsonl = read_jsonl_with_neighbor
    BASE.patch_parent_globals()
    CORE.assert_semantics = assert_semantics

def assert_semantics(records: dict[str, dict[tuple[int, int], Any]]) -> None:
    for label,value,expected in (
        ("target coordinate",TARGET_COORDINATES,EXPECTED_TARGET_COORDINATE_SHA256),
        ("translation policy",tuple(TRANSLATIONS.items()),EXPECTED_TRANSLATION_POLICY_SHA256),
        ("speaker style",SPEAKER_STYLE,EXPECTED_SPEAKER_STYLE_SHA256),
        ("terminology policy",TERMINOLOGY_POLICY,EXPECTED_TERMINOLOGY_POLICY_SHA256),
    ): CORE.guarded_digest(label,value,expected)
    if tuple(TRANSLATIONS)!=TARGET_COORDINATES or DYNAMIC_COORDINATES!=set(TARGET_COORDINATES) or STATIC_COORDINATES or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8")): raise RuntimeError("semantic policy drifted")
    changed=0
    for coordinate,translation in TRANSLATIONS.items():
        key=coordinate_key(coordinate); current=literal_texts(records["current"],key[:2])[key[2]]
        changed += translation != current
        if coordinate in BASE_DONOR_TRAILING_SPACE_COORDINATES:
            if translation!="적 본거지" or current.strip()!=current: raise RuntimeError("donor trailing-space adaptation drifted")
            ENGINE.validate_translation_shape(current,translation,"runtime_pending",coordinate)
            continue
        ENGINE.validate_translation_shape(current,translation,"runtime_pending",coordinate)
        if translation.count("\n")!=current.count("\n") or ENGINE.protected_signature(translation)!=ENGINE.protected_signature(current): raise RuntimeError("shape drifted")
    if changed!=EXPECTED_CHANGED_LITERAL_COUNT: raise RuntimeError("changed count drifted")

def build_rows() -> tuple[Any, ...]:
    result=list(BASE.build_rows())
    for row in result[1]:
        if row["coordinate"] in BASE_DONOR_TRAILING_SPACE_COORDINATES:
            row["base_wording_contextually_adapted"]=True
            row["base_donor_trailing_space_omitted_for_pk_shape"]=True
            row["runtime_assembly_evidence"]["base_donor_trailing_space_omitted_for_pk_shape"]=True
    return tuple(result)

def queue_evidence(prepared: Any) -> tuple[Any, ...]:
    rows = [json.loads(line) for line in prepared.queue.splitlines() if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID]
    visible = tuple(str(t["coordinate"]) for row in rows for t in row["target_literals"] if t["visible"])
    if len(rows)!=124 or len(visible)!=199 or visible[0]!="7:674:0" or visible[-1]!="7:797:1": raise RuntimeError("B055 universe drifted")
    queue_slice=visible[QUEUE_START:QUEUE_STOP]
    if len(queue_slice)!=65 or queue_slice[0]!="7:765:1" or queue_slice[-1]!="7:797:1": raise RuntimeError("slice drifted")
    pref={str(r["coordinate"]):r for r in read_jsonl(PREFILL)}
    prefilled=tuple(c for c in queue_slice if c in pref)
    if len(prefilled)!=11 or tuple(c for c in queue_slice if c not in pref)!=TARGET_COORDINATES: raise RuntimeError("prefill drifted")
    context=tuple((c,str(pref[c]["translation"]),str(pref[c]["source_record_raw_sha256"]),str(pref[c]["current_ko_utf16le_sha256"]),str(pref[c]["semantic_review"]),str(pref[c]["runtime_review"]),str(pref[c]["layout_review"]),str(pref[c]["base_exact_reuse_prefill"]["base_coordinate"]),str(pref[c]["base_exact_reuse_prefill"]["translation_utf16le_sha256"]),bool(pref[c]["base_exact_reuse_prefill"]["runtime_promotion_authorized"])) for c in prefilled)
    keys=tuple(tuple(map(int,str(r["record_coordinate"]).split(":"))) for r in rows)
    if len(keys)!=len(set(keys)): raise RuntimeError("duplicate records")
    return visible,queue_slice,prefilled,context,keys

def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if sha256_bytes(PREFILL.read_bytes())!=EXPECTED_PREFILL_SHA256 or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())!=EXPECTED_PRISTINE_PK_SHA256: raise RuntimeError("input drifted")
    ENGINE.validate_decisions(prepared,PREFILL,require_complete=False)
    visible,sl,pref,ctx,_=queue_evidence(prepared)
    for label,value,expected in (("queue universe",visible,EXPECTED_QUEUE_UNIVERSE_SHA256),("queue slice",sl,EXPECTED_QUEUE_SLICE_SHA256),("prefilled coordinate",pref,EXPECTED_PREFILLED_COORDINATE_SHA256),("prefill slice context",ctx,EXPECTED_PREFILL_SLICE_CONTEXT_SHA256)): CORE.guarded_digest(label,value,expected)
    existing={}
    for path in sorted(DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")):
        if path.resolve(strict=False)==OUTPUT.resolve(strict=False): continue
        ENGINE.validate_decisions(prepared,path,require_complete=False)
        for row in read_jsonl(path):
            c=row.get("coordinate"); prev=existing.setdefault(c,path.name)
            if row.get("resource")!="pk_msggame" or not isinstance(c,str) or prev!=path.name: raise RuntimeError("predecessor drifted")
    if tuple(c for c in sl if c not in existing)!=TARGET_COORDINATES: raise RuntimeError("residual drifted")
    present = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            present.append(path.name)
    return tuple(present)

def build_combined_slice_candidate(prepared: Any, records: dict[str,dict[tuple[int,int],Any]]) -> tuple[str,int]:
    _,sl,pref,_,_=queue_evidence(prepared); pr={str(r["coordinate"]):r for r in read_jsonl(PREFILL)}
    repl={coordinate_key(c):(TRANSLATIONS[c] if c in TRANSLATIONS else str(pr[c]["translation"])) for c in sl}
    cur=records["current"]; rev={k:literal_texts(cur,k[:2])[k[2]] for k in repl}; blob=prepared.resources["pk_msggame"].current_blob
    cand=ENGINE.rebuild_packed_with_literals(blob,repl); order=ENGINE.rebuild_packed_with_literals(blob,dict(reversed(tuple(repl.items()))))
    if cand!=order or ENGINE.rebuild_packed_with_literals(cand,rev)!=blob: raise RuntimeError("combined reverse drifted")
    cr=ENGINE.archive_records(ENGINE.parse_packed_msggame(cand).archive); touched={k[:2] for k in repl}
    if len(repl)!=65 or len(pref)!=11 or any(cr[k].data!=v.data for k,v in cur.items() if k not in touched) or any(gap_bytes(cr[k])!=gap_bytes(cur[k]) for k in touched): raise RuntimeError("combined scope drifted")
    changed=sum(v!=literal_texts(cur,k[:2])[k[2]] for k,v in repl.items()); digest=sha256_bytes(cand)
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256!="TO_PIN" and digest!=EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256: raise RuntimeError("combined hash drifted")
    if EXPECTED_COMBINED_CHANGED_LITERAL_COUNT>=0 and changed!=EXPECTED_COMBINED_CHANGED_LITERAL_COUNT: raise RuntimeError("combined count drifted")
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256=="TO_PIN": DISCOVERED_PINS.update({"combined slice candidate":digest,"combined slice changed count":str(changed)})
    return digest,changed

def main() -> int:
    patch_globals(); first=build_rows(); second=build_rows()
    prepared,rows,candidate,csha,changed,combo,cchanged,neighbors=first
    if ENGINE.jsonl(rows)!=ENGINE.jsonl(second[1]) or candidate!=second[2] or first[3:]!=second[3:]: raise RuntimeError("second-run drifted")
    if DISCOVERED_PINS: print(json.dumps(DISCOVERED_PINS,sort_keys=True,separators=(",",":"))); return 2
    before=sha256_bytes(STEAM_PK.read_bytes())
    if before!=EXPECTED_STEAM_PK_SHA256: raise RuntimeError("Steam drifted")
    ENGINE.atomic_write(OUTPUT,ENGINE.jsonl(rows)); validated=ENGINE.validate_decisions(prepared,OUTPUT,require_complete=False)
    counts=Counter(str(r["scope_classification"]) for r in rows)
    if len(rows)!=54 or len(validated)!=54 or counts!=Counter({"runtime_fragment_pending":54}) or any(r["semantic_review"]!="approved" or r["runtime_review"]!="pending" or r["base_runtime_state_inherited"] is not False or r["runtime_assembly_evidence"]["runtime_promotion_authorized"] is not False for r in rows): raise RuntimeError("decision validation drifted")
    patch_globals(); CORE.assert_tamper_rejection(prepared,rows,candidate)
    after=sha256_bytes(STEAM_PK.read_bytes())
    if after!=before: raise RuntimeError("Steam written")
    print(json.dumps({"status":"ok","segment":"pk_msggame_B055_S1178","approved":54,"changed_literal_count":changed,"combined_slice_changed_literal_count":cchanged,"candidate_sha256":csha,"combined_slice_candidate_sha256":combo,"decision_sha256":sha256_bytes(OUTPUT.read_bytes()),"builder_sha256":sha256_bytes(SCRIPT.read_bytes()),"optional_neighbors_present":list(neighbors),"steam_sha256_before":before,"steam_sha256_after":after,"second_run_reproduced":True,"tamper_rejection_passed":True,"outside_scope_identity_guarded":True,"base_runtime_state_inherited":False},sort_keys=True,separators=(",",":")))
    return 0

if __name__ == "__main__": raise SystemExit(main())
