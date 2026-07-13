# MSGUI 공개 번역 오버레이 0001–3600 검증 — 2026-07-14

## 공개 산출물

- 파일: `data/public/msgui_ko_0001_3600.v0.1.json`
- 크기: 655,598바이트
- SHA-256: `194ACBD979102191A3D317C2689CC327B9F8E47E90A20CC0F605F4F63A66F7B2`
- 번역 항목: 3,392개
- 허용 필드: `id`, `source_sc_utf16le_sha256`, `ko`, 선택적 상태·우선순위·불변식 예외
- `source_en`, `source_sc`, JP/TC 원문 및 완성 리소스: 없음

개발용 배치에는 검수 문맥을 위한 공식 원문이 있으므로 Git과 공개 배포본에서 제외한다.
공개 오버레이는 각 개발 배치의 원문을 제거하고 stock SC 문자열의 UTF-16LE SHA-256과
프로젝트 소유 한국어 문자열만 보존한다.

이번 확장 배치는 다음과 같다.

- 3301–3400: 100개 엔트리, 배치 SHA-256
  `1F5728A4C0CA5F3F163D9A860C3939D32C478AD01CFEFAA6DD59BEBD7E1EFA1C`
- 3401–3500: 100개 엔트리, 배치 SHA-256
  `95B91B0A8D8EE8EFA5347BA29EF7C4CF5F70798D733E963D69D3F7E82CF7EB86`
- 3501–3600: 100개 엔트리, 배치 SHA-256
  `BD4B4B7C153AD241EDC8B9C3094728A5757B6031D624917DF2938CBE64E6B874`

## 결정성·공개 산출물 감사

`--max-id 3600`과 `msgui_ko_0001_3600.v0.1`을 고정해 exporter를 서로 다른 두 출력 경로로
실행했다. 두 JSON은 크기와 SHA-256이 바이트 단위로 일치했다. 두 exporter 보고서도
동일하며 SHA-256은 다음과 같다.

`86CF2A9A1CFE295EA06CF4FA6B9E0F3161166F5DF2D551F005A80E6A327D72E7`

ID는 1–3600 범위에서 오름차순·중복 없음으로 3,392개이며, 모든 stock SC 원문 해시는
64자리 대문자 SHA-256이다. 허용되지 않은 필드와 상용 원문 키는 0개다.

## stock 병합·빌드 검증

1. 공식 SC/EN/JP/TC stock 해시로 private 개발 카탈로그를 검증했다.
2. baseline 카탈로그에 `merge-overlay`로 공개 오버레이를 병합했다.
3. 전체 5,100행이 `valid=true`, 오류 0개, 경고 0개이며 3,392개가 buildable임을 확인했다.
4. stock `MSG_PK/SC/msgui.bin`에서 설치본과 다른 임시 출력 경로 두 곳으로 빌드했다.
5. 두 `msgui.bin`, manifest, glyph demand SHA-256이 모두 일치했다.

결과:

- target `msgui.bin` 크기: 102,594바이트
- target `msgui.bin` SHA-256:
  `1F2DCF311430860EA572D9526F44C1C5C44A3D0BF4E6AC7DFF9A2D0C06A14977`
- target raw table 크기: 102,168바이트
- target raw table SHA-256:
  `2B057D2AF98B60DE326A97BDCB3ED1D33D9CD0C5A9E7E83C2C15FBAE277BE4FE`
- 실제 변경 문자열: 3,185개
- 요구 글리프: 598개, 그중 완성형 한글 489개
- build manifest SHA-256:
  `E000DAC42E0734643FDDB2289C3809CD1133E362D35B376B0C43495404C8772D`
- glyph demand SHA-256:
  `1D94917CDB57EF071ABD619A460E289D28D74612E81ACF488A0EDEB95F6DEEC3`
- 설치 게임 파일 변경: 없음

ID 1–3300 공개 오버레이와 비교하면 번역 항목과 실제 변경 문자열은 각각 300개,
요구 글리프는 29개, 완성형 한글은 15개 늘었다. 설치된 `msgui.bin`, `msgdata.bin`,
`res_lang.bin`은 모두 stock SHA-256을 유지했다.
