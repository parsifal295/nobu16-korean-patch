# msgui ID 4801-4900 번역 배치 검증 기록

## 결과

- 대상 범위: ID 4801-4900, 정확히 100행
- 실제 문구 및 번역 배치 엔트리: 100개
- canonical `empty` 및 구조 공백: 0개
- 병합 및 stock 대조 검증: `valid=true`, 오류 0개, 경고 0개
- invariant override: 0개
- 설치 게임 파일 변경: 없음
- 공개 overlay 및 Git 변경: 없음

배치 파일은 공식 다국어 원문을 포함하는 개발 전용 자료다. 공개 패치에는 직접 넣지 않고 추후 source-free overlay만 생성한다.

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_4801_4900.v0.1.json`
- 배치 SHA-256: `7AFB74EC7CC62B89C4105F06C959377BFA2A0C84C3A11AF2C39E679E251558A4`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 임시 단독 병합 catalog SHA-256: `671E45AC21B8BF8B8F72377F6FD947FC57F61DFE7F091B5DB7539006C95F0A79`
- 병합 보고서 SHA-256: `434939987D9E8DDA81F66541AC35CDDA65B0ED5D1D08AC4476EA33F8C3B3D14B`
- 단독 validation JSON SHA-256: `FDDAB7F88CC6A86C9E3F03658C1CD063DA11FEEF875CA568A88FFBB7275BCA3D`

## 교차검수 반영

읽기 전용 교차검수에서 확인한 수치 치환 문장의 조사를 다음과 같이 다듬었다.
printf 토큰의 종류와 순서는 바꾸지 않았다.

- ID 4825: `이전 비용으로 최소 %d가 필요합니다`
- ID 4830: `거리가 멀어 이전 비용으로 %d가 필요합니다`
- ID 4866: `금전 %d가 필요합니다`

수정 후 배치를 P3 canonical에 다시 단독 병합했으며 `batch_entries=100`,
`changed=100`, `valid=true`, 오류 0개, 경고 0개를 확인했다.

## 번역 및 용어 판단

ID 4801-4900의 EN·JP·SC·TC 원문을 모두 대조했다. 100행 모두 SC 실행 경로의 실제 문구이며 빈 슬롯은 없다.

- ID 4802-4804는 부대 이동 조작을 `합류 지점`과 `경유지`로 구분했다. ID 4803은 SC 문장이 모호하므로 JP·TC가 공통으로 명시하는 `합류 후 경유지` 의미를 따랐다.
- ID 4805/4815/4833은 `領地·所領=영지`, ID 4808은 `転封=전봉`, ID 4820은 `代官=대관`으로 기존 용어와 맞췄다.
- ID 4821-4832/4860/4877은 `本拠=본거지`와 `移転=이전`을 사용했다. 전쟁·출진·거리·비용에 따른 이전 제한을 서로 구분했다.
- ID 4834-4839/4845/4846은 `공략 목표`, `출진 준비`, `군비 거점`으로 통일했다. ID 4839는 기존 ID 3289와 같은 표현인 `%s 공략을 위한 군비 거점을 선택하십시오`를 사용했다.
- ID 4840-4859는 정책과 성하 시설의 해금·건설 조건이다. `위신`, `주의`, `실행 무장`, `상위 취락`, `노동력`, `석고`, `증축`을 누적 용어에 맞췄다.
- ID 4853/4862/4886은 직책을 `성주`, `영주`, `측근`으로 구분했다.
- ID 4867-4900은 `군단 보기`, `군단 색`, `군단 본거지`, `통치 범위`, `휘하 군단`을 사용했다. EN의 `Province`는 게임 내 조직 단위에 따라 `군단`으로 옮겼다.

동일 SC 원문 해시도 전체 개발 배치와 대조했다. 외부 중복 7쌍(ID 4813/3224, 4820/4931, 4828/3252, 4841/2958, 4864/3252, 4877/528, 4877/1415)은 모두 같은 한국어다. 내부 중복 2그룹(ID 4828/4864, 4857/4859)도 byte-equal이며 새 번역 불일치는 0개다.

## 형식 invariant

printf 토큰이 있는 항목은 19개다.

- `%d`: ID 4825, 4830, 4855-4857, 4859, 4866, 4887
- `%s`: ID 4836, 4839, 4842, 4843, 4854, 4858, 4860, 4879, 4884
- `%s`, `%d`: ID 4850
- `%s`, `%s`: ID 4885

모든 항목에서 printf 토큰의 종류와 순서가 SC 기준과 일치한다. ID 4857/4859는 각각 줄바꿈 1개를 원문과 같은 위치에 유지했다. 이 범위에는 ESC, PUA, 기타 제어문자가 없으며 invariant override도 없다.

## 단독 병합·검증

P3 canonical 복사본에 이번 배치만 병합했다.

- `batch_entries=100`
- catalog metadata 변경: 100개
- 전체 행: 5,100개
- 상태: `translated=379`, `untranslated=3683`, `empty=1038`
- buildable: 379개
- 검증: `valid=true`
- 오류: 0개
- 경고: 0개

stock 4개 언어 `MSG_PK/*/msgui.bin`의 크기·packed SHA-256·raw SHA-256도 meta와 모두 일치했다.

## 단독 빌드와 결정성

같은 단독 병합 catalog를 서로 다른 두 출력 디렉터리에 연속 빌드했다.

- 대상 `msgui.bin` 크기: 87,929바이트
- 대상 `msgui.bin` SHA-256: `BB90960B2C7891466DACD443C1472737E7331F8426DF338892F16AC80EA93082`
- 대상 raw 크기: 87,560바이트
- 대상 raw SHA-256: `F28AEB662F322156B12C0777484A56053F4D0A02FACF54551FF21F8D6273B2ED`
- 전체 실제 바이너리 변경: 379개(P3 seed 279개 + 이번 배치 100개)
- 글리프 수요: 320자
- 한글 음절 수요: 295자
- build manifest SHA-256: `830ADCC0E90FBA625798F8AB37D488961AD9F94FFFB86904826A8B6E705E161F`
- glyph demand SHA-256: `63A970DCACD4FDC4AE41604C4D413EF9666D2EF9FF24F9AC84245D331A380B63`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다.

`all_stock_hashes`, `all_source_strings`, `format_invariants`,
`table_parse_roundtrip`, `wrapper_decompress_roundtrip`은 모두 `OK`다.

검증 뒤 설치본은 다음 stock SHA-256 그대로다.

- `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `MSG_PK/SC/msgdata.bin`: `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

결정성 산출물은 무시된
`KR_PATCH_WORK/tmp/revalidate_4801_4900_crossfix/build1` 및 `build2` 아래에만
생성했다. 공개 overlay, Git, 설치본은 수정하지 않았다.
