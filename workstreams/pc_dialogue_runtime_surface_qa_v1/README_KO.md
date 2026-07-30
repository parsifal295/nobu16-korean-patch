# PC 동적 대사 완성문장 표면 감사

기존 Base/PK 런타임 VM 감사는 호출·분기 폐포와 바이트 구조를
검증했지만, 조립된 한국어 문장의 조사·어미를 완료 조건으로 삼지 않았다.
이 감사기는 Ghidra로 확인한 다음 계약을 사용자 화면 검증에 연결한다.

- 리터럴과 동적 셀렉터 출력은 UTF-16 코드 단위 그대로 복사된다.
- 자동 띄어쓰기와 자동 문장부호 삽입은 없다.
- `0143`은 대상 레코드를 호출하고 반환한다.

검사 항목:

1. `이(가)`, `은(는)`, `을(를)`, `와(과)`, `(으)로`, `으로(로)`
2. 동적 셀렉터 직후의 고정 조사
3. `0143` 호출로 조립된 동적 문구 직후의 고정 조사
4. 줄바꿈·닫는 괄호·닫는 인용부호 뒤에 숨은 고정 조사
5. 동적 호칭 뒤에 기계적으로 붙인 `분/무장/장수/주군/대상` carrier
6. 동적 셀렉터 뒤에 기계적으로 붙인
   `분/무장/장수/주군/사자/당주/인물/대상/항목/본인/자신` carrier
   및 성·군 지역값을 세력처럼 바꾸는 `측` carrier
7. `너/놈/저희/우리` 등 서로 다른 높임 등급을 내는 호출 뒤의
   고정 `께/께서/께서는`
8. 리터럴의 마지막 단어·문장부호와 동적 이름·지역·수치 selector가
   공백 없이 붙는 왼쪽 경계. 수치 selector의 `LV3`, `제2`,
   `통/무/지/정` 축약 표기와 부호 결합, 이름 변경의 `옛이름→새이름`
   화살표만 별도 compact 계약으로 허용
9. predecessor에는 없었으나 재번역 과정에서 동적 값 직후 새로 생긴
   첨가조사 `도`와 접속어 `및`
10. 외국 상인 말투를 기계적으로 옮겨 오타처럼 보이는 중복 어미 `요오`
11. 완결 어미 직후 VM 종결어미 중복

기본 입력은 0.15.0의 52,803행 최종 후보이다.

```powershell
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/audit_runtime_surface_v1.py
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/audit_runtime_surface_v1.py `
  --strict `
  --output tmp/pc_dialogue_runtime_surface_qa_v1/report.source_free.v1.json
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/test_runtime_surface_v1.py
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/terminal_boundary_detector_v1.py `
  --output tmp/pc_dialogue_runtime_surface_qa_v1/terminal-boundary.source-free.v1.json
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/test_terminal_boundary_detector_v1.py
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/audit_candidate_structure_v1.py `
  --strict `
  --output tmp/pc_dialogue_runtime_surface_qa_v1/candidate-structure.source-free.v1.json
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/audit_candidate_relative_width_v1.py `
  --strict `
  --output tmp/pc_dialogue_runtime_surface_qa_v1/candidate-relative-width.source-free.v1.json
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/test_candidate_guardrails_v1.py
```

`--include-text` 출력에는 번역문이 포함되므로 `tmp/` 아래에서만 사용한다.
최종 후보 승격은 `--strict`가 0으로 종료할 때만 허용해야 한다.

구조 감사는 모든 레코드·리터럴 슬롯·VM 구성요소를 predecessor와
비교한다. PK의 검토된 종결어미 family retarget 14건만 정확 좌표와
전후 opcode로 허용하며 다른 selector/call/jump/control 변경은 거부한다.
또한 predecessor의 검토된 첨가 의미는 유지하되 후보에서 새로 도입된
동적 경계 `도/및`만 의미 불변식 위반으로 거부한다.

상대폭 감사는 `msggame.bin`에 이벤트 대사용 `912px` 절대 gate를
잘못 적용하지 않는다. 대신 predecessor 대비 표시 줄 증가를 금지하고,
일반 변경 줄은 raw G1N 폭 증가를 `24px` 이하로 제한한다. 증가한 줄은
같은 block의 predecessor 최대폭도 넘을 수 없다. 사용자 제보 exact
회귀문 때문에 더 길어진 문장은 좌표·줄·전후폭·번역문 SHA-256이 모두
일치하는 개별 예외만 허용한다.

기존 52,803행 후보의 최초 실패 기준선은
`baseline_failure.source_free.v1.json`에 고정했다. 이 보고서는 번역문을
포함하지 않으며, 후보 해시와 유형별 건수만 기록한다.

## 최종 후보 릴리스 게이트

최종 Base/PK 후보는 다음 래퍼로 source-free 증거를 생성한다. 두 파일의
표면 감사와 확장 종결어미 경계 감사의 합산 `issue_count`가 0이 아니면
종료 코드가 1이며
`runtime_completion=PASS`가 생성되지 않는다.

```powershell
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/gate_final_candidate_v1.py `
  --base tmp/candidate/MSG/JP/msggame.bin `
  --pk tmp/candidate/MSG_PK/JP/msggame.bin `
  --output tmp/pc_dialogue_runtime_surface_qa_v1/final-candidate-gate.source-free.v1.json
python -B workstreams/pc_dialogue_runtime_surface_qa_v1/test_release_gate_v1.py
```

`New-V090ResourceTarget.ps1`은 위 PASS 증거를
`-DialogueRuntimeSurfaceEvidence`로 요구한다. 증거에 바인딩된 Base/PK
크기와 SHA-256이 실제 입력 후보와 일치하지 않거나, 어느 한 리소스라도
issue가 남아 있으면 0.90.0 target 디렉터리를 만들기 전에 실패한다.
