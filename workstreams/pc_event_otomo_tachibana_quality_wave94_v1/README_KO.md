# PC 이벤트 품질 Wave 94 — 오토모 계승과 다치바나산 장면

PK `MSG_PK/JP/msgev.bin`의 ID 8383–8391을 W93 후보 위에서 검수한다. 다카하시 무네토라가 벳키 아키츠라의 유해를 다치바나산으로 옮기고 오토모를 지키겠다고 맹세하는 완결 대화 장면이다.

- 엄격한 입력: W93 private 후보의 검증된 `msgev.bin`
- 번역 대조: 직접 PC JP 원문 및 직접 PC EN/SC/TC 문맥만 사용
- 검수 결과: 9행 전체, 7행 수정·2행 유지
- 일본어 원문 줄바꿈은 따르지 않고 한국어 의미 단위로 수동 개행
- static patch 007 레이아웃: 최대 4줄, 원본 G1N raw 48/24 advance 기준 각 줄 960px 이하
- `ceil(raw * 30 / 48)`의 30px 실효 폭은 보고용이며 두 번째 차단 기준으로 쓰지 않음
- `[bm1222]`는 `다카하시 무네토라` raw 408px, `[bm1730]`은 `벳키 아키츠라` raw 312px으로 이 장면에서만 보수 예약한다. 두 예약 모두 `scene_limited: true`, `runtime_proven: false`이다.
- 9행 전부를 예약 적용 뒤의 표시 문자열과 폭으로 감사한다. 토큰을 제거한 폭으로 통과시키지 않는다.

후보 출력은 `tmp/pc_event_otomo_tachibana_quality_wave94_v1/candidate-final/`만 사용한다. Steam 적용, 커밋, 푸시, 릴리스는 이 작업에 포함하지 않는다.
