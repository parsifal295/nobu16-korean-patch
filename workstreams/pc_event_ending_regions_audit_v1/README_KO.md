# PC PK 엔딩 지역·초기 엔딩 이벤트 3309–3484 재검수

이 작업물은 `MSG_PK/JP/msgev.bin`의 3309–3484번을 **현재 한국어 후보본 자체**로 다시 읽은, 읽기 전용 전수 ledger다. 과거 `manual_compact_korean_layout` 이력은 품질 판정 근거로 사용하지 않았다. 후보 바이너리를 만들지 않았고 Steam·Git·릴리스·네트워크에는 쓰지 않는다.

## 기준 입력과 원문 대조

- 현재 한국어 strict 입력: `tmp/pc_event_gifu_quality_wave98_v1/candidate-final/MSG_PK/JP/msgev.bin`
  - packed SHA-256: `62C7F55506DB59A43761DDCE07FB5DA4175AD0AC4B68C03507B37AD52E2AEBD3`
  - raw SHA-256: `D0FAB9C303F8F456184DCDD89AC929C675D6528080F8C29E419E1249BD9B7408`
- 재베이스 비중첩 검증: 직전 `pc_event_manual_compact_static007_3xxx_runtime_restore_v1` 후보와 전수 비교했다. W98의 변화 ID는 3288, 3293, 3295, 3298–3300, 3302–3307이며, 허용 창 3287–3307 밖의 변화와 이 감사 범위 3309–3484의 변화는 없음을 빌더가 검증한다.
- 비교 원문: pristine PC JP 및 PC EN/SC/TC `msgev.bin`
- 범위: ID 3309–3484, 총 176행

JP 원문의 LF·들여쓰기는 한국어 레이아웃의 권위로 쓰지 않았다. 한국어 LF는 문맥 단위로만 판단하며, 태그 내부 LF·문장 축약·의미 삭제는 금지한다.

## 분류 결과

| 분류 | 행 수 | 처리 |
| --- | ---: | --- |
| `reviewed_preserve` | 81 | 정적 표시 문구를 원문·한국어 흐름·Static Patch 007 폭 기준으로 재검토하고 보존 |
| `static_high_confidence_correction` | 6 | 동적 토큰이 없는 행에서만 확인한 의미/품질 수정 후보 |
| `runtime_or_ui_hold` | 89 | 이벤트 키 18행 또는 동적 토큰 71행. 실제 표시 문자열·예약 폭이 이 범위에서 미입증이라 수정 보류 |

고확신 후보는 3331, 3413, 3446, 3475, 3477, 3479이다.

- 3331: `先進的な大名`의 뜻을 살리면서 직역투 서술을 자연화
- 3413: `諸外国との交易`을 국내 여러 나라가 아닌 여러 **외국**과의 교역으로 명확화
- 3446: `晴元は切ろう`의 정치적 결별을 살해처럼도 읽히는 표현 대신 `하루모토와 결별하자`로 수정
- 3475: 양보·대조 문장을 한국어로 완결
- 3477: `天下だ`라는 야망을 `내가 노리는 것`으로 정확히 표현
- 3479: 일본어 원문의 행두 들여쓰기만 제거하고 괄호 독백·태그·의미를 보존

## 레이아웃 기준

PK 이벤트 대사는 Static Patch 007 기준으로 측정했다.

- 30px, 유효폭 912px, 최대 4줄
- 원본 G1N 폭: 전각 48px / 반각 24px
- `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`
- 통과 한계: raw 1440px / 실효 912px

정적 보존행과 6개 고확신 후보의 최대 raw 폭은 1152px, 최대 실효 폭은 720px, 최대 줄 수는 4줄이다. 912px 초과 행은 없다. 각 고확신 후보에는 표시 문자열, raw 폭, 환산 실효 폭, 전각/반각 수, 줄 수와 초과 여부를 [공개 JSON 보고서](public/pc_event_ending_regions_audit.v1.json)에 기록했다.

동적 토큰 행은 토큰의 런타임 표시 형태 및 30/48 배율 예약 폭이 이 범위에서 직접 입증되지 않았으므로, 리터럴만 재어 통과라고 주장하지 않는다. 별도 런타임 토큰 근거가 확보된 뒤에만 수정·후보 생성 대상으로 올린다.

## 재현·검증

```powershell
python workstreams/pc_event_ending_regions_audit_v1/build_pc_event_ending_regions_audit_v1.py build
python workstreams/pc_event_ending_regions_audit_v1/build_pc_event_ending_regions_audit_v1.py verify
python workstreams/pc_event_ending_regions_audit_v1/test_pc_event_ending_regions_audit_v1.py
```
