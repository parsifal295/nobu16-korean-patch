# Base `msggame` 런타임 VM 역설계 검증

## 결론

Base 동적 대사 15,651개를 게임에서 한 줄씩 재생할 필요는 없다. Ghidra
MCP로 Steam PK 1.1.7 JP 실행 파일의 공용 메시지 VM과 Base
`MSG/JP/msggame.bin` 로더 경로를 역설계하고, 그 규칙을 후보 레코드 전체에
정적 적용한다.

확인한 실행 경로는 다음과 같다.

```text
메시지 ID 조회
→ msggame 레코드 오프셋 선택
→ 레코드 VM 실행
→ opcode 분배
→ literal 또는 동적 값의 UTF-16LE 출력
```

핵심 규칙:

- `07 07 01 ... 07 07 02`: UTF-16LE literal을 그대로 출력한다.
- `01 43 <u32>`: 반환 주소를 저장하고 대상 레코드를 호출한다.
- `01 4A <u32>`: 대상 레코드로 점프한다.
- 호출·점프 피연산자는 `block_id * 10000 + record_id` 형식이다.
- `02 ...`: 동적 값을 구해 UTF-16 코드 단위를 출력 버퍼에 그대로 복사한다.
- `02` 처리에는 자동 공백이나 자동 구두점 삽입이 없다.
- `05`: 블록 제어 또는 호출 레코드 복귀를 처리한다.
- `1B`: 명시적 제어 태그를 처리한다.

현재 한국어 `msggame.bin`의 바이트코드를 기준으로 모든 Base 결정을
overlay한 후보를 먼저 만든다. 각 레코드에서
`literal + token/callee + literal` 순서를 source-free 템플릿으로 만들고,
레코드 해시와 행별 번역 해시를 묶은 증거를 메인 결정 validator가 다시
계산한다. 기존 번역 검토의 의미 판단은 재사용하되, 조합 순서·자동 구분자
유무·호출 대상 유효성은 실행 파일과 후보 바이트 기준으로 판정한다.

## 전수 범위

- 보류 literal: 15,651개
- 보류 레코드: 9,138개
- 레코드 실행 형태: 6개 군집
- `0143` 호출: 4,335회
- `02` 동적 값 삽입: 8,255회
- 실제 selector family: 31개
- 실제 selector/속성 형태: 56개
- 미해석 후보 gap 바이트: 0개
- 호출 루트: 160개
- 보수적으로 추출한 도달 가능 호출·점프 그래프: 1,864개 레코드
- 도달 그래프의 `014A`: 2,030회(고유 간선 1,949개)
- 도달 그래프 내부 중첩 `0143`: 2회

공개 보고서는 원문과 번역문을 싣지 않고 좌표·개수·해시·opcode 형태만
기록한다. 승격된 전체 결정본은 `tmp/` 아래에만 생성한다.

## 실행

```powershell
python -B workstreams/base_msggame_runtime_vm_audit_v1/build_base_msggame_runtime_vm_audit_v1.py
python -B workstreams/base_msggame_runtime_vm_audit_v1/build_base_msggame_runtime_vm_audit_v1.py --check
python -B workstreams/base_msggame_runtime_vm_audit_v1/test_base_msggame_runtime_vm_audit_v1.py

python -B workstreams/base_msggame_runtime_vm_audit_v1/build_base_msggame_runtime_verified_decisions_v1.py
python -B workstreams/base_msggame_runtime_vm_audit_v1/build_base_msggame_runtime_verified_decisions_v1.py --check
python -B workstreams/base_msggame_runtime_vm_audit_v1/test_base_msggame_runtime_verified_decisions_v1.py
```

이 검증은 런타임 이름의 모든 실제 문자열 값을 열거하는 작업이 아니라,
그 값이 삽입되는 모든 후보 레코드의 순서·경계·호출 대안을 전수 검증하는
작업이다. Base 23,765개 결정은 승격 후 모두 후보 빌드 가능 상태가 된다.
릴리스 직전에는 전수 재생 대신 대표 조합의 실게임 smoke test만 별도로
수행한다. 이 작업은 PK 결정 파일과 Steam 설치를 변경하지 않는다.
