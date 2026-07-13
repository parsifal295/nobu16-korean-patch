# MSGUI 공개 번역 오버레이 0001–2700 검증 — 2026-07-14

## 공개 산출물

- 파일: `data/public/msgui_ko_0001_2700.v0.1.json`
- 크기: 470,082바이트
- SHA-256: `5D471B05A0AC3BED6AF81C613C88630D98697F66A0A3AB8611D18D1AD3999A06`
- 번역 항목: 2,544
- 허용 필드: `id`, `source_sc_utf16le_sha256`, `ko`, 선택적 상태·우선순위·불변성 예외
- `source_en`, `source_sc`, JP/TC 원문, 완성 리소스: 없음

개발용 배치에는 검수 편의를 위한 상용 영문 원문이 있으므로 Git과 공개 배포본에서
제외했다. 공개 오버레이는 각 개발 배치의 원문을 private 카탈로그와 먼저 대조한 뒤
SC 원문의 UTF-16LE SHA-256과 한국어만 내보낸다.

이번 확장 배치는 다음과 같다.

- 2401–2500: 100개, 배치 SHA-256
  `84B4748BBA070531CCE84202072F4FB4A4C1E1A7B7006655C15948A7023A72F4`
- 2501–2600: 100개, 배치 SHA-256
  `64CB32EB5CB13DEBF3B16CDA3446571481241D11A91BB82339A12AE85890B18F`
- 2601–2700: 유효 78개, 정식 빈 슬롯 22개 유지, 배치 SHA-256
  `EFF9DDC41BBFF817D93E3E8F46B8FB5657F9935A172B3A7118686C373B268EED`

## 결정성·공개 산출물 감사

`--max-id 2700`과 `msgui_ko_0001_2700.v0.1`을 고정해
`tools/export_public_translation_overlay.py`를 서로 다른 출력 경로로 두 번 실행했다.
두 파일의 크기와 SHA-256이 모두 일치했다. 내보내기 보고서도 바이트 단위로 같았고
SHA-256은 다음과 같다.

`B6867488CCA78ED9C02C93DD11644DBBA889308B3ABA72FF6C0CEE92ED9FF612`

공개 JSON을 별도로 검사한 결과 ID는 1–2700 사이에서 오름차순·중복 없이 2,544개이며,
모든 SC 원문 해시는 대문자 64자리 SHA-256이다. 허용하지 않은 필드와 상용 원문 키는
0개다. 저장소 회귀 테스트 6개도 모두 통과했다.

## stock 병합·빌드 검증

1. 공식 SC/EN/JP/TC stock 해시로 private 개발 카탈로그를 검증했다.
2. baseline 카탈로그에 `merge-overlay`로 공개 오버레이를 병합했다.
3. 5,100행 전체가 `valid=true`, 오류 0개, 경고 0개이며 2,544개가 buildable임을 확인했다.
4. stock `MSG_PK/SC/msgui.bin`에서 설치본과 다른 임시 출력 경로로 빌드했다.

결과:

- target `msgui.bin` 크기: 89,856바이트
- target `msgui.bin` SHA-256:
  `E78B21CA59D3C068D2C62B707754076F94D34955FA6FAA2B140FA95516DC8E1E`
- target raw table 크기: 89,480바이트
- target raw table SHA-256:
  `38A9E5EA56AD3A112CF0482C94D1355ABBE78FEA01525C27B55CCE1B9AB56639`
- 실제 변경 문자열: 2,384
- 요구 글리프: 507자, 그중 완성형 한글 420자
- build manifest SHA-256:
  `DD42C2AB70860A9FE3F3E2A969120088C251DE8FB94562C5705F09FA7A43D7C6`
- glyph demand SHA-256:
  `EAA566C4DA497D23C488C01F972D46DE91AFB478E496365752CC7E649C043BC1`
- 설치 게임 파일 변경: 없음

ID 1–2400 공개 오버레이와 비교하면 번역 항목은 278개, 실제 변경 문자열은 237개,
요구 글리프는 14자, 완성형 한글은 6자 늘었다. 설치된 `msgui.bin`, `msgdata.bin`,
`res_lang.bin`은 모두 stock SHA-256을 유지했다.
