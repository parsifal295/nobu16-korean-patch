# msgui ID 2601-2700 번역 배치 검증 기록

## 결과

- 대상 범위: ID 2601-2700, 정확히 100행 조사
- 번역 배치 엔트리: 78개
- canonical `empty` 유지: 22개(ID 2665-2686)
- 병합 및 stock 대조 검증: `valid=true`, 오류 0개, 경고 0개
- printf·ESC·PUA·제어문자·줄바꿈 invariant override: 0개
- 설치 게임 파일 변경: 없음

배치 파일은 개발 전용이다. 공식 다국어 원문을 포함하므로 공개 패치에는 이 파일을 직접 넣지 않고, 추후 source-free overlay만 생성한다.

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_2601_2700.v0.1.json`
- 배치 SHA-256: `EFF9DDC41BBFF817D93E3E8F46B8FB5657F9935A172B3A7118686C373B268EED`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 임시 단독 병합 catalog SHA-256: `0F0CB16F938E54E4D5E115F248A8545D371863AA1B8E363AF24C0DAF0CEDB2DF`
- 단독 validation JSON SHA-256: `0B85B837AC8B9CDE88796B2E1C8852E0609E597A2219976170901B0351DAE675`

## 범위와 구조 슬롯 처리

ID 2601-2700의 네 언어 원문을 모두 확인했다. ID 2665-2686은 EN·JP·SC·TC가 전부 빈 문자열이고 catalog 상태도 `empty`다. `merge-batch`는 빈 번역을 buildable 상태로 바꾸는 것을 금지하므로, 이 22개는 배치에 넣지 않고 canonical `empty` 상태를 그대로 유지했다.

SC판에서 반각 공백 하나로 비활성화된 슬롯도 임의로 EN/JP 문구를 되살리지 않았다. 다음 13개는 `U+0020` 한 글자를 그대로 보존했다.

- ID 2650, 2657, 2661, 2691-2700

그 밖의 byte-equal 엔트리는 다음과 같다.

- ID 2662-2664: SC/JP가 명시한 내부 미사용 표식 `不要` 보존
- ID 2690: SC 형식 조각 `%s%s` 보존

따라서 배치 엔트리 78개 중 catalog 상태·검토 정보가 갱신된 수는 78개이며, 실제 SC 문자열 바이트가 달라지는 항목은 61개다. byte-equal 엔트리는 모두 의도된 구조/미사용/형식 슬롯이다.

## 주요 번역 판단

- ID 2601 `（自勢力）`: 앞 범위 ID 2600 `(타세력)`과 맞춰 `(자세력)`으로 통일했다.
- ID 2602-2605: `병력 회복 속도`, `건의·내정 속도`, `계략 성공률`, `전투/공성전 AI 레벨`로 기존 용어집과 누적 배치에 맞췄다.
- ID 2616 `卒年`: 동일 SC 원문의 기존 ID 1285와 같은 `사망년`을 사용했다.
- ID 2618 `安堵年数選択`: 기존 `소령 안도` 계열과 연결해 `안도 연수 선택`으로 옮겼다.
- ID 2619/2620 `掌握状態`/`未掌握`: 누적 용어 `장악`에 맞춰 `장악 상태`/`미장악`으로 옮겼다.
- ID 2624 `主城`: 동일 SC 원문의 기존 ID 1667과 같은 `본성`을 사용했다.
- ID 2630-2637: 괄호 안 세력 표기를 `(타세력)`/`(자세력)`으로 통일했다.
- ID 2642/2643: 고유 직책 `奉行`/`家宰`를 누적 용어 `봉행`/`가재`로 유지했다.
- ID 2654/2658: 같은 SC 원문 `婚姻/调停`을 모두 `혼인/중재`로 통일했다.
- ID 2687/2688: 동일 SC 원문의 기존 ID 658/659와 같은 `증가`/`감소`를 사용했다.

현재 존재하는 개발 배치와 SC 원문 해시가 겹치는 항목을 대조한 결과, 이번 범위와의 중복 쌍 576개는 모두 같은 번역이었다. 이 수에는 반복된 구조용 공백 쌍이 포함된다. 이번 배치가 새로 만든 불일치 쌍은 0개다.

## 형식 invariant

printf 토큰이 있는 항목은 8개다.

- ID 2609: `%+d`
- ID 2610: `%d`, `%d`; SC의 전각 퍼센트 기호를 유지해 `%d％(LV%d)`로 구성
- ID 2613: `%s`
- ID 2622: `%s`
- ID 2638: `%s`, `%s`
- ID 2641: `%s`, `%d`, `%d`
- ID 2648: `%d`
- ID 2690: `%s`, `%s`

모든 항목에서 토큰 종류와 순서가 SC 기준과 일치한다. ESC 색상 코드, PUA, 기타 제어문자, 줄바꿈이 있는 항목은 없으며 invariant override도 없다.

## 단독 병합·검증

P3 canonical 복사본에 이번 배치만 병합했다.

- `batch_entries=78`
- catalog metadata 변경: 78개
- 전체 행: 5,100개
- 상태: `translated=357`, `untranslated=3705`, `empty=1038`
- buildable: 357개
- 검증: `valid=true`
- 오류: 0개
- 경고: 0개

stock 4개 언어 `MSG_PK/*/msgui.bin`의 크기·packed SHA-256·raw SHA-256도 meta와 모두 일치했다.

## 단독 빌드와 재현성

같은 단독 병합 catalog를 서로 다른 두 출력 디렉터리에 연속 빌드했다.

- 대상 `msgui.bin` 크기: 86,371바이트
- 대상 `msgui.bin` SHA-256: `568B3AEDDE1FD19B6AAA441FF23EFDCAB5F8A4C5F0FD1BBFF16BCFC5DA236477`
- 대상 raw 크기: 86,008바이트
- 대상 raw SHA-256: `0876900DB841955894FD9D7FF46E5B5B398313FB7D9F0CFDC3DF5E6BFF1F9787`
- 전체 실제 바이너리 변경: 340개(P3 seed 포함)
- 글리프 수요: 276자
- 한글 음절 수요: 249자
- build manifest SHA-256: `CACC61A1E91B2F8FA8E786D850729DDD0E1A35EEC1DBC34BE9C34CF1A4882F5A`
- glyph demand SHA-256: `DC7CA022EAC32AB9C224A8692FEEDD319F3D93D39F76531F6F7F6FB449634131`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다.

검증 뒤 설치본 `MSG_PK/SC/msgui.bin`은 stock SHA-256 `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82` 그대로다. 모든 산출물은 무시된 `KR_PATCH_WORK/tmp/translation_2601_2700` 아래에서만 생성했다.
