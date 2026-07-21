# Wave 101 — 간토·가와고에 이벤트 품질 후보

이 작업물은 `pc_event_kanto_audit_v1`에서 검증한 15개 `static_high_confidence`
제안을 실제 private 후보에만 적용한다. 입력은 Wave 100의
`tmp/pc_event_ending_regions_quality_wave100_v1/candidate-final/MSG_PK/JP/msgev.bin`이며,
감사 보고서의 `proposed_ko`를 다시 쓰지 않고 그대로 이식한다.

## 적용 범위

`3489, 3490, 3491, 3493, 3497, 3500, 3502, 3505, 3506, 3508, 3510, 3514, 3516, 3522, 3526`

- 의미·용어 보정: `3489`, `3491`, `3500`, `3502`, `3505`, `3506`, `3508`
- 한국어 문맥 개행: `3490`, `3493`, `3497`, `3510`, `3514`, `3516`, `3522`, `3526`
- 런타임 인명 토큰: `3514`, `3522`, `3526`
  - strict 이름표 전체 이름 예약 폭을 적용한다.
  - `runtime_proven=false`를 유지하며 접두사 렌더링을 추측하지 않는다.

## 검증 조건

- PK Static Patch 007: 30px, 줄 간격 8, 유효폭 912px, 최대 4줄
- `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`
- raw G1N 1440px / 실효 912px 이하
- 색상 태그·런타임 토큰·제어 구조·UTF-16 종료 구조 보존
- JP 원문 LF는 복사하지 않고, 문장 축약·삭제는 하지 않음
- 순정 PC JP 및 PC EN/SC/TC를 다시 대조
- Wave 100 대비 정확히 15행만 변경

## 실행

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_kanto_quality_wave101_v1\build_pc_event_kanto_quality_wave101_v1.py build
& $py -B workstreams\pc_event_kanto_quality_wave101_v1\build_pc_event_kanto_quality_wave101_v1.py verify-private
& $py -B -m unittest -v workstreams\pc_event_kanto_quality_wave101_v1\test_pc_event_kanto_quality_wave101_v1.py
```

출력은 `tmp/pc_event_kanto_quality_wave101_v1/candidate-final/`에만 만든다.
Steam 적용, Git 조작, 푸시, 릴리즈, 네트워크 작업은 이 workstream의 범위가 아니다.
