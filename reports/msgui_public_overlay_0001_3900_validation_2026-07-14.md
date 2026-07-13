# MSGUI 공개 번역 오버레이 0001–3900 검증 — 2026-07-14

## 공개 산출물

- 파일: `data/public/msgui_ko_0001_3900.v0.1.json`
- 크기: 724,153바이트
- SHA-256: `3E3FFF6ED2C3038E92D4ADB65BD7E350790972A5FF6939F46C016BA2D57575CB`
- 번역 항목: 3,692개
- 허용 필드: `id`, `source_sc_utf16le_sha256`, `ko`, 선택적 상태·우선순위·불변식 예외
- `source_en`, `source_sc`, JP/TC 원문 및 완성 리소스: 없음

개발용 배치에는 검수 문맥을 위한 공식 원문이 있으므로 Git과 공개 배포본에서 제외한다.
공개 오버레이는 각 개발 배치의 원문을 제거하고 stock SC 문자열의 UTF-16LE SHA-256과
프로젝트 소유 한국어 문자열만 보존한다.

이번 확장 배치는 다음과 같다.

- 3601–3700: 100개 엔트리, 실제 교체 98개, 배치 SHA-256
  `60D9BDE3AA6B6BAC85C4B77F4FC72286539D510BD2B7A1DFEA80BA2ACA96C981`
- 3701–3800: 100개 엔트리, 실제 교체 86개, 배치 SHA-256
  `5307D51B05BE565C6754098B4EB56D0CC344557A1D5E56E6EA1008AE82AEFE08`
- 3801–3900: 100개 엔트리, 실제 교체 98개, 배치 SHA-256
  `949C7EE2CE07B65853AA44C3D7FAFFC02C97B960C0EE594C31FE721B0AAD1035`

## 결정성·공개 산출물 감사

`--max-id 3900`과 `msgui_ko_0001_3900.v0.1`을 고정해 exporter를 서로 다른 두 출력 경로로
실행했다. 두 JSON은 크기와 SHA-256이 바이트 단위로 일치했다. 두 exporter 보고서도
동일하며 SHA-256은 다음과 같다.

`4C1B54948F99A08EC56EF1D6EE1FCD0AC7E95CFB860D5E1565FED3349EAC67C1`

ID는 1–3900 범위에서 오름차순·중복 없음으로 3,692개이며, 모든 stock SC 원문 해시는
64자리 대문자 SHA-256이다. 허용되지 않은 필드와 상용 원문 키는 0개다.

## stock 병합·빌드 검증

1. 공식 SC/EN/JP/TC stock 해시로 private 개발 카탈로그를 검증했다.
2. baseline 카탈로그에 `merge-overlay`로 공개 오버레이를 병합했다.
3. 전체 5,100행이 `valid=true`, 오류 0개, 경고 0개이며 3,692개가 buildable임을 확인했다.
4. stock `MSG_PK/SC/msgui.bin`에서 설치본과 다른 임시 출력 경로 두 곳으로 빌드했다.
5. 두 `msgui.bin`, manifest, glyph demand SHA-256이 모두 일치했다.
6. 회귀 테스트 6개가 모두 통과했다.

결과:

- target `msgui.bin` 크기: 108,156바이트
- target `msgui.bin` SHA-256:
  `0CD32F908F35DF2A852DCAC624BC04A087FF4E7850CF6576EA8FDA4F829B0C13`
- target raw table 크기: 107,708바이트
- target raw table SHA-256:
  `682D6B2748EDF1495DCED42D567B7770944CBFF388AF5EBED166624B5EB96EE5`
- 실제 변경 문자열: 3,467개
- 요구 글리프: 625개, 그중 완성형 한글 510개
- build manifest SHA-256:
  `AA8E1E010EAFA36CF44B540E50A335C596FB2D0AB6E25453821253E1362D6301`
- glyph demand SHA-256:
  `75D41DC7492722E4A8FB519BDC190641BF04C225F844CD12026E1F4D3B3A25EF`
- 설치 게임 파일 변경: 없음

ID 1–3600 공개 오버레이와 비교하면 번역 항목은 300개, 실제 변경 문자열은 282개,
요구 글리프는 27개, 완성형 한글은 21개 늘었다. 설치된 `msgui.bin`, `msgdata.bin`,
`res_lang.bin`은 모두 stock SHA-256을 유지했다.
