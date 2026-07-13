# msgui ID 4901-5000 번역 배치 검증 기록

## 결과

- 대상 범위: ID 4901-5000, 정확히 100행
- 실제 문구: ID 4901-4986, 86개
- canonical `empty`: ID 4987-5000, 14개
- 번역 배치 병합: 86개 입력, 86개 변경
- 병합 및 stock 대조 검증: `valid=true`, 오류 0개, 경고 0개
- 설치 게임 파일 변경: 없음

실제 문구 86개는 EN·JP·SC·TC를 대조하고 기존 용어집의 `군단`, `군`, `성주`, `영주`, `성하 방침`, `봉행`, `소령 안도`, `교섭 재료` 표기를 적용했다. 네 언어와 한국어 필드가 모두 빈 ID 4987-5000은 번역 배치에서 제외하고 canonical `empty` 상태를 유지했다.

## 산출물과 기준

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_4901_5000.v0.1.json`
- 배치 SHA-256: `91BC14278C5A16B829F76B79AB2E776EBA637E2ADF11375EF36DA132F09176CD`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 임시 병합 catalog SHA-256: `CF64D3A68049D791E087C4C4DA82389162A5DA2D4B8693F9A951CF6CA134D5DA`
- batch merge report SHA-256: `09786C3A8907387D48C48E9F9B98A0B7FEAE04F8D1C4127B6F9E4915E4E88A0B`
- validation JSON SHA-256: `B1359554CECACD1AA78E934FBE8E20ED278905C53C889FA05CB6AAC5A221EB30`

배치는 `development_only=true`, `contains_commercial_source_text=true`, `include_in_public_patch=false`로 선언했다. 공개 overlay에는 원문을 복제하거나 병합하지 않았다.

## 교차검수 반영

기존 누적 용어와 원문을 재대조해 다음 두 문구를 교정했다.

- ID 4906: `増築=증축`에 맞춰 `교전 중에는 증축할 수 없습니다.`로 수정
- ID 4954: 프로젝트 용어 `調略=조략`에 맞춰 `실행할 조략을 선택하십시오.`로 수정

수정 후 배치를 P3 canonical에 다시 단독 병합했으며 `batch_entries=86`,
`changed=86`, `valid=true`, 오류 0개, 경고 0개를 확인했다.

## 범위 및 불변식 검증

- 병합 후 전체 행: 5,100개
- 상태: `translated=365`, `untranslated=3697`, `empty=1038`
- buildable: 365개
- 필수 글리프: 315개
- printf 행 12개: ID 4901, 4903, 4904, 4907, 4908, 4911, 4912, 4952, 4963, 4974, 4976, 4980
- PUA 행 1개: ID 4920, `U+E008 U+E015 U+E00D` 순서 보존
- 줄바꿈 행 1개: ID 4924, 줄바꿈 1개 보존
- ESC: 없음
- 기타 제어문자: 없음
- unknown percent: 없음

해시 게이트가 각 entry의 `source_en`과 SC UTF-16LE SHA-256을 canonical 원문과 대조했다. 병합 뒤 validator가 printf 순서, PUA 순서, 줄바꿈 수, ESC 및 기타 제어문자 계약을 다시 검사했으며 오류와 경고는 모두 0개였다.

## 단독 빌드와 결정성

동일한 임시 병합 catalog를 서로 다른 두 출력 디렉터리에 연속 빌드했다.

- 대상 `msgui.bin` 크기: 87,941바이트
- 대상 `msgui.bin` SHA-256: `1A3C1626DAA708ED482DCC1BE30A97A9FA443F7E8A6BB30A3215E5CF1BC08C35`
- 대상 raw 크기: 87,572바이트
- 대상 raw SHA-256: `308BD95DF89E8DADBAFED1F86FC9B755FB0AC07F5701870C349293C2066016F9`
- 전체 실제 바이너리 변경: 365개(P3 seed 279개와 이 배치 86개)
- 글리프 수요: 315개
- 한글 음절 수요: 292개
- build manifest SHA-256: `D320BEF075290D83C962347D122EE2406588E5AE79F493E757414D75E34C770E`
- glyph demand SHA-256: `1A799732142C8C52B9592D505895942F278C05282061C164E1CC38BE8F9680F9`

두 빌드의 `msgui.bin`, build manifest, glyph demand가 모두 바이트 단위로 일치했다. 두 build manifest 모두 `installed_game_files_modified=false`를 기록한다.

`all_stock_hashes`, `all_source_strings`, `format_invariants`,
`table_parse_roundtrip`, `wrapper_decompress_roundtrip`은 모두 `OK`다.

## 원본·설치본 무변경

- 설치본 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 설치본 `MSG_PK/SC/msgdata.bin`: `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- 설치본 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- P3/P4 canonical, 공개 overlay, Font-v4, 성 이름 workstream, 배포 경로를 수정하지 않음
- Git 조작이나 커밋을 수행하지 않음
- 이번 재검증 산출물은 무시된
  `KR_PATCH_WORK/tmp/revalidate_4901_5000_crossfix` 아래에만 생성했다.
