# MSGUI 공개 번역 오버레이 0001–2400 검증 — 2026-07-14

## 공개 산출물

- 파일: `data/public/msgui_ko_0001_2400.v0.1.json`
- 크기: 418,400바이트
- SHA-256: `193523EA249BE8A404CB3F92DD991DCF6F384629D0FE32ADEADBDA7EA0BB6A02`
- 번역 항목: 2,266
- 허용 필드: `id`, `source_sc_utf16le_sha256`, `ko`, 선택적 상태·우선순위·불변성 예외
- `source_en`, `source_sc`, JP/TC 원문, 완성 리소스: 없음

개발용 배치에는 검수 편의를 위한 상용 영문 원문이 있으므로 Git과 공개 배포본에서
제외했다. 공개 오버레이는 각 개발 배치의 원문을 private 카탈로그와 먼저 대조한 뒤
SC 원문의 UTF-16LE SHA-256과 한국어만 내보낸다. 마지막 개발 배치는
`msgui_core_ui_terms_2301_2400.v0.1.json`이며 배치 SHA-256은
`A7FA4311B2B7BDDBDB525424663BE94069719C23B8101498719279168C83A68F`다.

## 결정성·공개 산출물 감사

`--max-id 2400`과 `msgui_ko_0001_2400.v0.1`을 고정해
`tools/export_public_translation_overlay.py`를 서로 다른 출력 경로로 두 번 실행했다.
두 파일의 크기와 SHA-256이 모두 418,400바이트 및 다음 값으로 일치했다.

`193523EA249BE8A404CB3F92DD991DCF6F384629D0FE32ADEADBDA7EA0BB6A02`

내보내기 보고서도 두 실행에서 바이트 단위로 같았고 SHA-256은
`71E296A694B08F0878C0658E84E7626E7AB6B93924A7D0E932EF031EF80DE575`였다.
공개 JSON을 별도로 검사한 결과 항목 ID는 1–2400 사이에서 오름차순·중복 없이
2,266개이며, 모든 SC 원문 해시는 대문자 64자리 SHA-256이다. 각 항목에는 허용 필드만
있고 상용 원문 필드·완성 게임 리소스는 없다. 저장소 `unittest discover` 회귀 테스트
6개도 모두 통과했다.

## stock 병합·빌드 검증

1. 공식 SC/EN/JP/TC stock 해시로 private 개발 카탈로그를 검증했다.
2. baseline 카탈로그에 `merge-overlay`로 공개 오버레이를 병합했다.
3. 5,100행 전체가 `valid=true`, 오류 0개, 경고 0개이며 2,266개가 buildable임을 확인했다.
4. stock `MSG_PK/SC/msgui.bin`에서 설치본과 다른 임시 출력 경로로 빌드했다.

결과:

- target `msgui.bin` 크기: 89,515바이트
- target `msgui.bin` SHA-256:
  `F66096CBE8F6CBDB5F30862487E28B2DD46312D529F6BAB08FC40619DB107E14`
- target raw table 크기: 89,140바이트
- target raw table SHA-256:
  `5FC956F8E438A21A0AFFB4C67C43DE21AE49D21CFA983D4A3CC88E2CEA84DCDF`
- 실제 변경 문자열: 2,147
- 요구 글리프: 493자, 그중 완성형 한글 414자
- build manifest SHA-256:
  `7E2BB643F1547A84E2D6FB0C539058743A99154BE9C19B9D0B0C42FA87B8EC5D`
- glyph demand SHA-256:
  `F1B2E49A2A595AA245719ACCD78FFAF89F94EF131309CF3FA994642C94C38CC8`
- 설치 게임 파일 변경: 없음

target과 raw 해시는 개발용 ID 401–2400 누적 독립 검증 결과와 바이트 단위로 일치한다.
ID 1–2300 공개 오버레이와 비교하면 번역 항목은 100개, 실제 변경 문자열은 78개,
요구 글리프는 4자, 완성형 한글은 4자 늘었다.
