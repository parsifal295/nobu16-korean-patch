# PK `msggame` Base 재사용 런타임 VM 감사

## 결론

Base 완료 번역을 그대로 재사용한 PK private prefill 17,652개 중
`runtime_review=pending`인 9,770개를 Steam PK 1.1.7 실행 파일의 실제
`MSG_PK/JP/msggame.bin` 경로와 공용 메시지 VM 규칙으로 전수 검사했다.

- 별도 승격기에 넘길 수 있는 보수적 안전 집합: 4,717개
- 현재 차단 집합: 5,053개
- 실제 디코드한 PK 폐포 레코드: 8,651개
- 실제 `0143` operand: 4,203개
- 실제 `014A` operand: 1,974개
- 미해석 gap byte: 0개
- regex operand masking에 의한 검증: 0개

이 감사기는 판단만 기록한다. private decision을 승격하지 않았고 Steam에도
아무 파일도 쓰지 않았다.

## PK 로더 경로

Ghidra MCP로 확인한 경로는 다음과 같다.

```text
0x1409F7A70
  -> locale별 MSG_PK/JP, TC, SC, EN 선택
0x1409F8710
  -> "/" + *(0x141C01CE0: "msggame") + ".bin"
  -> MSG_PK/JP/msggame.bin을 object+0x30/+0x38에 결박
vtable 0x14154C538
  -> +0x08 loader 0x1409F8710
  -> +0x18 evaluator 0x1409F7490
0x1409F7490
  -> selector 0x140A00FC0
  -> record VM 0x1409F7610
```

따라서 `0x1409F8710`은 이 실행 파일에서 PK locale path builder를 호출하는
PK `msggame` 로더다. 기존 Base 감사 계약의 함수 별칭을 그대로 재사용하지
않고, PK 경로를 별도 계약
[`ghidra_pk_vm_contract.v1.json`](ghidra_pk_vm_contract.v1.json)에 고정했다.

## 검증 경계

각 prefill 행은 다음 증거를 모두 다시 계산한다.

1. PK pristine/current/exact-prefill candidate의 레코드·literal 해시
2. prefill의 Base donor 좌표와 Base 완료 decision 해시
3. Base 완료 candidate의 donor 번역과 PK prefill 번역의 일치
4. Base reversed-VM coverage의 donor row proof 존재 여부
5. Base donor record와 PK target record의 VM 구성요소 순서
6. literal slot 경계와 모든 형제 literal의 source/candidate 일치
7. selector group·slot·optional property와 식 연산자
8. 실제 `0143`/`014A` operand 범위, target 존재, edge 종류와 occurrence 순서
9. 각 edge target을 좌표 delta 없이 다시 짝지은 synchronized closure

하위 record가 다르면 그 오염은 루트 행으로 역전파된다.

- `novel_taint`: 루트 VM 구조가 다름
- `sibling_taint`: 같은 루트의 형제 source 또는 candidate literal이 다름
- `closure_taint`: 실제 call/jump 폐포의 구조·literal·pairing이 다름
- `donor_taint`: Base reversed-VM donor row proof가 없음
- `layout_taint`: prefill 단계에서 줄 수 변경 검토가 남음

차단 행 하나가 여러 taint를 동시에 가질 수 있으므로 taint별 개수의 합은
5,053보다 클 수 있다.

## 실행

```powershell
python -B workstreams/pk_msggame_runtime_vm_audit_v1/build_pk_msggame_runtime_vm_audit_v1.py
python -B workstreams/pk_msggame_runtime_vm_audit_v1/build_pk_msggame_runtime_vm_audit_v1.py --check
python -B workstreams/pk_msggame_runtime_vm_audit_v1/test_pk_msggame_runtime_vm_audit_v1.py
```

회귀 테스트는 다음 변조를 모두 거부한다.

- call operand 순서 바꾸기
- `0143`을 `014A`로 바꾸기
- selector property 바꾸기
- literal 경계 앞뒤로 selector 옮기기
- PK 번역 또는 Base donor 바꾸기
- public report payload hash 바꾸기
- novel-tainted 행을 강제로 승격 가능 상태로 바꾸기

공개 보고서
[`public/pk_msggame_runtime_vm_coverage.v1.json`](public/pk_msggame_runtime_vm_coverage.v1.json)은
상용 원문이나 번역문을 담지 않고 좌표·해시·개수·opcode form·taint만 담는다.
4,717개를 실제 decision으로 승격하려면 이 보고서의 row/pair proof를 묶는
별도 private decision builder와 shared engine의 PK evidence validator가
필요하다.
