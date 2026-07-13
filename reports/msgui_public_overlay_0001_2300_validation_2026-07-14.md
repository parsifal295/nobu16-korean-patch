# MSGUI 공개 번역 오버레이 0001–2300 검증 — 2026-07-14

## 공개 산출물

- 파일: `data/public/msgui_ko_0001_2300.v0.1.json`
- SHA-256: `A0905E87686320301510EA914FFBD102F1306212CB846326BEB3710ADE03145C`
- 번역 항목: 2,166
- 허용 필드: `id`, `source_sc_utf16le_sha256`, `ko`, 선택적 상태·우선순위·불변성 예외
- `source_en`, `source_sc`, JP/TC 원문, 완성 리소스: 없음

개발용 배치에는 검수 편의를 위한 상용 영문 원문이 있으므로 Git과 공개 배포본에서
제외했다. 공개 오버레이는 각 개발 배치의 원문을 private 카탈로그와 먼저 대조한 뒤
SC 원문의 UTF-16LE SHA-256과 한국어만 내보낸다.

## 결정성

동일 입력으로 `tools/export_public_translation_overlay.py`를 두 번 실행한 결과 두 파일의
SHA-256이 모두 다음 값으로 일치했다.

`A0905E87686320301510EA914FFBD102F1306212CB846326BEB3710ADE03145C`

## stock 병합·빌드 검증

1. 공식 SC/EN/JP/TC stock 해시로 private 개발 카탈로그를 검증했다.
2. baseline 카탈로그에 `merge-overlay`로 공개 오버레이를 병합했다.
3. 병합 결과 2,166개가 buildable이고 validation 오류·경고가 없음을 확인했다.
4. stock `MSG_PK/SC/msgui.bin`에서 별도 출력 경로로 빌드했다.

결과:

- target `msgui.bin` SHA-256:
  `E4C8FE20B010B0A6688C9BB528CD4BD523FE8D2B004F4A8274E966959C06C8E8`
- target raw table SHA-256:
  `2DDE12B3503FBAB519E9D4F88BBDAF19F4B47414BD3ABAF4223E980CA8D4EF0F`
- 실제 변경 문자열: 2,069
- 요구 글리프: 489자, 그중 완성형 한글 410자
- 설치 게임 파일 변경: 없음

target 해시는 개발용 누적 401–2300 독립 검증 결과와 바이트 단위로 일치한다.
