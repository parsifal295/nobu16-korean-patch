# PK 간토·가와고에 이벤트 전수 감사

범위는 PK `MSG_PK/JP/msgev.bin` ID `3485–3526`의 호조·이마가와 전개,
가와고에 위기, 다케다 노부시게 도입까지 42행이다. 한국어 입력은 오직
`tmp/pc_event_ending_regions_quality_wave100_v1/candidate-final/MSG_PK/JP/msgev.bin`만 사용했다.
Wave 100의 변경 ID는 `3331/3413/3446/3475/3477/3479`이므로, 이 감사 범위
`3485–3526`의 모든 문자열이 직전 Wave 98 후보와 동일한지도 별도로 검증한다.
순정 Steam PC JP와 설치된 PC EN/SC/TC는 뜻과 보호 구조를 대조하는 읽기 전용
근거이며, Switch 한국어는 열거나 기준으로 사용하지 않았다.

## 감사 결과

- 42행 전부 재검토했다.
- 15행은 고확신 정적 후보다. 이 workstream은 **후보 바이너리를 만들지 않으며**,
  제안 문안과 근거만 public JSON에 기록한다.
- 의미·문맥 보정: `3489`, `3491`, `3500`, `3502`, `3505`, `3506`, `3508`.
- 문맥 개행만 재배치: `3490`, `3493`, `3497`, `3510`, `3514`, `3516`, `3522`,
  `3526`.
- `3514`, `3522`, `3526`의 런타임 인명 토큰은 prefix 의미를 추측하지 않고
  strict 이름표의 전체 이름 예약 폭으로만 측정했다. `runtime_proven`은 모두
  `false`로 기록한다.
- 나머지 27행은 원문과 PC 다국어를 대조한 뒤 현재 문안·개행을 유지한다.

대표적인 정정은 다음과 같다.

- `3506`: 원문 `河越城`을 `가와고에성`으로 복원한다.
- `3505`, `3508`: `両上杉`·`古河公方`을 `양 우에스기`·`고가 공방`으로
  표기하고, 조사와 문장 경계를 한국어에 맞춘다.
- `3491`, `3510`, `3516`: `가독을/이어`, `맡아/주겠느냐`, `듣고/싶지`처럼
  의미 단위가 갈라진 개행을 다시 배치한다.

## Static Patch 007 레이아웃 기준

- 글자 크기 30px, 줄 간격 설정 8, 유효폭 912px, 최대 4줄
- 원본 G1N 폭: 전각 48px, 반각 24px
- `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`
- 원본 G1N 상한 1440px / 환산 실효 상한 912px

각 행의 현재·제안 문안에는 표시 문자열, 원본 G1N 폭, 환산 실효 폭,
전각/반각 수, 줄 수, 912px 초과 여부와 런타임 예약 폭을 모두 기록한다.
JP 원문 LF는 레이아웃 권위로 사용하지 않았고, 태그 내부에 LF를 넣지 않았다.
문장 축약·삭제도 하지 않는다.

## 실행

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_kanto_audit_v1\build_pc_event_kanto_audit_v1.py build
& $py -B workstreams\pc_event_kanto_audit_v1\build_pc_event_kanto_audit_v1.py verify
& $py -B -m unittest -v workstreams\pc_event_kanto_audit_v1\test_pc_event_kanto_audit_v1.py
```

산출물은 `public/pc_event_kanto_audit.v1.json`과 `validation.v1.json`뿐이다.
Steam 파일, 후보 바이너리, Git, 푸시, 릴리즈, 네트워크 상태는 변경하지 않는다.
