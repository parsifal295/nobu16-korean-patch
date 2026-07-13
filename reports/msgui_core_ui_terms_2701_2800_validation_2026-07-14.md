# msgui ID 2701-2800 번역 배치 검증 기록

## 결과

- 조사 범위: ID 2701-2800, 정확히 100행
- 번역 배치 엔트리: 49개
- SC 구조용 반각 공백 보존: 46개(ID 2701-2746)
- canonical `empty` 유지: 51개(ID 2749-2799)
- 실제 번역 문자열: 3개(ID 2747, 2748, 2800)
- 원문 및 해시 대조: 49개 모두 일치
- 검증: `valid=true`, 오류 0개, 경고 0개
- printf·ESC·PUA·기타 제어문자·줄바꿈 invariant override: 0개
- 설치 게임 파일 변경: 없음

이 배치는 상용 다국어 원문을 포함하는 개발 전용 파일이다. 공개 배포에는 직접 넣지 않고 추후 source-free overlay만 생성한다.

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_2701_2800.v0.1.json`
- 배치 SHA-256: `A6D902A3ABFB9776C91BB363C17F9763E95A4C9AD2CDFB79FAC905C5B351F8D5`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 임시 단독 병합 catalog SHA-256: `B4BBB68F8C1E01C7D5764BDCB1A24F36E02ADD8178A44BFAECA2FE0FC8DE16DD`
- merge 보고서 SHA-256: `B79E62A3B582D2048BABD26474307443843035160E4D1A50CD42BFB139E10A77`
- validation JSON SHA-256: `E08BBE007C5569DEDDF233EFF4490A52D7CE98867F44A89D8C34C767FCA9A75B`

## 구조 슬롯 처리

ID 2701-2746은 EN과 JP에 전투 효과 문구가 있으나 SC와 TC에는 모두 `U+0020` 한 글자만 있다. 간체중문판 경로에서 비활성화된 기능 슬롯으로 판단해 EN/JP 전용 문구를 한국어로 되살리지 않고 반각 공백을 바이트 단위로 유지했다.

- ID 2701-2704: 아군/적군 부대 공격 상승·저하 계열
- ID 2705-2712: 이동 상승·저하 계열
- ID 2713-2720: 방어 상승·저하 계열
- ID 2721-2730: 체력·병력 회복/저하 계열
- ID 2731-2738: 혼란 무효·부여 계열
- ID 2739-2742: 철퇴 무효 계열
- ID 2743-2746: 전법 회복 상승 계열

이 46개는 모두 배치 metadata만 `translated`로 갱신되고 SC 문자열은 원문과 동일하다.

ID 2749-2799는 EN·JP·SC·TC가 모두 빈 문자열이며 catalog 상태도 `empty`다. 빈 번역을 buildable 상태로 바꾸지 않고 배치에서 제외해 51개 모두 canonical `empty`를 유지했다.

따라서 범위 100행은 다음처럼 완전히 분류된다.

- SC 한 칸 공백 유지 46개
- 실제 번역 3개
- 완전 빈 canonical 슬롯 51개

## 실제 번역 판단

- ID 2747 `補給兵糧増加` / `补给军粮增加`: 기존 `補給兵糧=보급 군량` 계열과 맞춰 `보급 군량 증가`로 번역했다.
- ID 2748 `混乱無効` / `混乱无效`: 상태 효과를 짧게 나타내는 항목이므로 `혼란 무효`로 번역했다.
- ID 2800 `UI文章ダミー` / `UI文本dummy`: 내부 자리표시자 성격을 보존하면서 읽을 수 있게 `UI 텍스트 더미`로 번역했다.

세 항목 모두 printf, ESC, PUA, 기타 제어문자, 줄바꿈을 포함하지 않는다. ID 2701-2746의 구조용 공백 외에 byte-equal 엔트리는 없다.

## 단독 병합·검증

P3 canonical 복사본에 이번 배치만 병합했다.

- `batch_entries=49`
- catalog metadata 변경: 49개
- 전체 행: 5,100개
- 상태: `translated=328`, `untranslated=3734`, `empty=1038`
- buildable: 328개
- 검증: `valid=true`
- 오류: 0개
- 경고: 0개
- 이번 범위 실제 SC 문자열 변경: 3개
- 이번 범위 byte-equal: 46개

stock 네 언어 원문 해시와 형식 invariant를 모두 대조했고 허용 예외는 사용하지 않았다.

## 단독 빌드와 재현성

같은 단독 병합 catalog를 서로 다른 두 출력 디렉터리에 연속 빌드했다.

- 대상 `msgui.bin` 크기: 86,306바이트
- 대상 `msgui.bin` SHA-256: `1BC2BDFDB19C03DCDDCA75E35CC925CBB2F25F38D1B2A9D392D384476DD7A41C`
- 대상 raw 크기: 85,944바이트
- 대상 raw SHA-256: `5A9E4A72448DA7EA315D9DED7F1F74E8CB8AE71262BE1B3D052C4AC6A982DCE4`
- 전체 실제 바이너리 변경: 282개(P3 seed 279개 + 이번 배치 3개)
- 글리프 수요: 246자
- 한글 음절 수요: 232자
- build manifest SHA-256: `1FA92E9A20626031B2DF755BD65C9F1D229E7615FE59EB8C869A80A7146047F6`
- glyph demand SHA-256: `CDEDB211F68175040F70E765F27221490ECDBA33B8CB004340388E6E2437757D`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다. 모든 빌드 manifest에 `installed_game_files_modified=false`가 기록되었다.

## 원본·설치본 무변경

- 설치본 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 설치본 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- P3/P4 canonical, 공개 overlay, Font-v4, 성 이름 workstream, 배포 경로를 수정하지 않았다.
- 실제 쓰기 범위는 이번 번역 배치, 이 보고서, 무시된 `KR_PATCH_WORK/tmp/translate_2701_2800_validation` 아래 임시 검증 산출물뿐이다.
