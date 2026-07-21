# Wave 102 — 다케다 노부시게·히코쓰루 이벤트 품질 후보

이 workstream은 `pc_event_takeda_hikotsuru_audit_v1`의
`static_high_confidence_ids` 20행만 Wave 101 private 후보 위에 적용한다.
문안을 다시 작성하지 않고 감사 JSON의 `proposed_ko`를 그대로 이식한다.

## 입력과 적용 범위

- strict 입력: `tmp/pc_event_kanto_quality_wave101_v1/candidate-final/MSG_PK/JP/msgev.bin`
- 감사 근거: `workstreams/pc_event_takeda_hikotsuru_audit_v1/public/pc_event_takeda_hikotsuru_audit.v1.json`
- 적용 ID: `3529, 3530, 3532, 3533, 3536, 3539, 3540, 3541, 3542, 3546, 3547, 3548, 3550, 3551, 3554, 3555, 3559, 3561, 3563, 3564`
- 출력: `tmp/pc_event_takeda_hikotsuru_quality_wave102_v1/candidate-final/MSG_PK/JP/msgev.bin`

W101의 모든 파일 프로필과 private audit/manifest, 그리고 원 감사 builder/public JSON의
SHA-256을 고정한다. 빌드는 audit의 적용 ID·현재 문안·제안 문안·제어 서명·레이아웃
기록이 모두 일치할 때만 진행한다.

## 검증 조건

- Wave 101 대비 정확히 위 20행만 변경
- 문장 축약·삭제 금지, 색상 태그·런타임 토큰·제어 구조·UTF-16 종료 구조 보존
- PK Static Patch 007: 30px, 줄 간격 8, 유효폭 912px, 최대 4줄
- `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`
- 런타임 토큰 `[bm1251]`(ID `3548`)은 strict 전체 이름 예약 폭을 그대로 쓰며
  `runtime_proven=false`를 유지
- `diff-guard`가 W101 외 변경 0건을 검증

## 실행

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_takeda_hikotsuru_quality_wave102_v1\build_pc_event_takeda_hikotsuru_quality_wave102_v1.py build
& $py -B workstreams\pc_event_takeda_hikotsuru_quality_wave102_v1\build_pc_event_takeda_hikotsuru_quality_wave102_v1.py verify-private
& $py -B workstreams\pc_event_takeda_hikotsuru_quality_wave102_v1\build_pc_event_takeda_hikotsuru_quality_wave102_v1.py diff-guard
& $py -B -m unittest -v workstreams\pc_event_takeda_hikotsuru_quality_wave102_v1\test_pc_event_takeda_hikotsuru_quality_wave102_v1.py
```

출력은 private `tmp/` 후보와 이 workstream의 public audit/validation에만 만든다.
Steam 적용, Git 조작, 푸시, 릴리즈, 네트워크 작업은 이 workstream의 범위가 아니다.
