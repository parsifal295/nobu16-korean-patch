# PC 텍스트 품질 Wave 34 — 엄격 후보 번들

Wave 31 이벤트 8셀, Wave 32 PK 인물 대사 16레코드, Wave 33 이벤트 26셀을
하나의 private 후보로 합성한다. 총 변경은 이벤트 34셀과 인물 대사 16레코드,
합계 50개다.

각 구성 워크스트림이 PC JP/EN/SC/TC 원문, 현재 Steam 입력, 글꼴 폭과 바이트
구조를 먼저 검증한다. 이 번들은 그 결과를 현재 Steam 기준으로 합성하고 정확한
3개 파일 해시를 다시 고정한다.

- Switch 파일·Switch 한국어·과거 한국어 산출물은 입력에 없다.
- 빌더는 `tmp/pc_text_quality_wave34_strict_bundle_v1/`에만 쓴다.
- Steam 적용·Git·네트워크·릴리즈 기능은 없다.
- Base 이벤트 ID `6772`, `6941`, `8776`, `8803`, `8947`, `9292`는 실제 장면
  QA가 끝날 때까지 Steam 적용 대상으로 취급하지 않는다. 재현 경로 조사 결과는
  [BASE_EVENT_QA_STATUS_KO.md](BASE_EVENT_QA_STATUS_KO.md)에 기록한다.

이 번들은 전수 감사 완료를 뜻하지 않는다. 의미·런타임·UI 문맥 보류군은 계속
별도로 추적한다.
