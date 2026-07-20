# 수동 압축 한국어 이벤트 레이아웃 전수 인벤토리

## 결론

`manual_compact_korean_layout` + 수동 개행 작업 대상은 **1,553행** (ID 3210–11008)이며, 연속 ID 기준 장면 배치는 **1,049개**입니다.
현재 한국어는 `pc_event_manual_compact_static007_batch02_v1`을 읽기 전용 기준으로 사용합니다. 이 기준은 5777의 검증된 Static 007 3줄 상태, 3210·3231–3234·3239의 batch01 복원, 3254·3260의 batch02 복원을 포함하며, W97은 역사적 엄격 전임으로 보존합니다. Steam 게임 파일·트랜잭션·Git·네트워크·릴리스에는 쓰지 않습니다.

모든 행은 사람의 의미 검토를 거친 **축약 없는 재번역 및 수동 재개행** 대상입니다. 일괄 줄바꿈 삭제나 자동 decompact는 금지합니다.

## 측정 원칙

- 원본 G1N 기준 전각 48px / 반각 24px를 기록하고, 유효 표시폭은 `ceil(raw_g1n_width_px * 30 / 48)`로 계산합니다.
- Static patch 007의 실제 런타임 판단은 유효폭 912px 이하(원본 G1N 동등값 1440px)/최대 4줄입니다.
- 동적 이름 토큰은 일치하는 장면 전용 후보 감사 근거가 있으면 그 행에만 적용하고, 그 외에는 v2 전체 이름 상한을 사용했습니다. `[bu]`류 비수치 토큰은 폭을 추정하지 않고 hold로 남깁니다.

## 현재 결과

- W90–W97, Static 007 3줄 전임, batch01, 현재 batch02 또는 완료된 strict 후속 후보가 이미 바꾼 보호 행: **30행** (덮어쓰기 금지)
- 런타임 토큰 폭 근거 hold 행: **11행**
- Static patch 007 유효폭 912px 주의 행: **0행**
- v2 역사적 수동 압축 오버레이와 현재 batch02 기준 문구가 다른 행: **205행**
- 별도 legacy static preflight(원본-font-rollback, 비권위적) reflow 행: **33행**

보호 행도 재검토 대상이지만, 이 인벤토리의 후속 작업이 기존 엄격 후보 변경을 덮어써서는 안 됩니다. 새 후보에서 다루려면 명시적인 사람 승인과 행 단위 차이 검사가 필요합니다.

## 우선 추천 배치

아래 순서는 기계 번역 순서가 아니라, 사람 검토를 위한 위험 우선 순위입니다. 각 배치의 모든 문장은 축약 없이 의미를 다시 대조하고, 태그·토큰·종결자·의미 단위를 보존해야 합니다.

| 순위 | 배치 | ID 범위 | 분류 | 주의 |
| ---: | --- | --- | --- | --- |
| 1 | MC-0026 | 3438–3439 | P2_runtime_reservation_evidence_attention | token hold 3438,3439 |
| 2 | MC-0013 | 3327 | P2_runtime_reservation_evidence_attention | token hold 3327 |
| 3 | MC-0018 | 3386 | P2_runtime_reservation_evidence_attention | token hold 3386 |
| 4 | MC-0019 | 3394 | P2_runtime_reservation_evidence_attention | token hold 3394 |
| 5 | MC-0020 | 3396 | P2_runtime_reservation_evidence_attention | token hold 3396 |
| 6 | MC-0021 | 3398 | P2_runtime_reservation_evidence_attention | token hold 3398 |
| 7 | MC-0022 | 3402 | P2_runtime_reservation_evidence_attention | token hold 3402 |
| 8 | MC-0023 | 3411 | P2_runtime_reservation_evidence_attention | token hold 3411 |
| 9 | MC-0024 | 3421 | P2_runtime_reservation_evidence_attention | token hold 3421 |
| 10 | MC-0025 | 3429 | P2_runtime_reservation_evidence_attention | token hold 3429 |
| 11 | MC-0816 | 9324–9338 | P3_standard_human_semantic_retranslation_reflow | 사람 의미·수동 reflow |
| 12 | MC-0668 | 8239–8244 | P3_standard_human_semantic_retranslation_reflow | 사람 의미·수동 reflow |

## 안전한 후보 체인

1. 이 인벤토리에서 보호되지 않은 한 배치만 선택하고, JP/EN/SC/TC 직접 PC 문맥과 현재 batch02 한국어 기준을 사람이 대조합니다.
2. 한국어 문장을 삭제·축약하지 말고 태그, 색상 span, 런타임 토큰, printf, 종결자를 그대로 보존한 새 문안과 수동 줄바꿈을 만듭니다.
3. 새 빌더는 현재 batch02 후보(또는 바로 앞에서 검증된 사설 후속 후보)를 엄격한 읽기 전용 입력으로 pin하고, 자기 `tmp/<새_워크스트림>/candidate-final`에만 씁니다.
4. 빌더 감사에는 행별 직접 PC 4언어 문맥, raw/effective 폭, 동적 토큰 예약, 정확한 diff ID, 전임/출력 프로필을 기록합니다.
5. 다음 후보는 직전 검증 후보만 전임으로 삼고, 이 인벤토리의 보호 ID와 기존 변경 ID의 교집합이 비어 있음을 검사합니다. Steam 적용·트랜잭션·릴리스는 명시 승인 전까지 하지 않습니다.

세부 행별 원문, 직접 PC 4언어 문맥, 태그/토큰, 줄별 폭, 보호 근거는 `public/msgev_manual_compact_korean_layout_inventory.v1.json`에 있습니다. 연속 장면 배치와 전체 우선순위는 `public/msgev_manual_compact_korean_layout_batches.v1.json`에 있습니다.
