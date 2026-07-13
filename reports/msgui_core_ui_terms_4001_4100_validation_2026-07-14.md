# msgui ID 4001-4100 번역 배치 검증 기록

## 결과

- 대상 범위: ID 4001-4100, 정확히 100행
- 번역 배치 엔트리: 60개
- canonical `empty` 제외: ID 4061-4100, 40개
- 교차 검수 반영: 5개(ID 4002, 4010, 4038, 4042, 4055)
- 병합 및 stock 대조 검증: `valid=true`, 오류 0개, 경고 0개
- invariant override: 0개
- 설치 게임 파일 변경: 없음

이 배치는 공식 다국어 원문을 포함하는 개발 전용 파일이다. 공개 패치에는 직접 넣지
않고 source-free overlay로만 내보낸다.

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_4001_4100.v0.1.json`
- 배치 SHA-256: `80D7C27112AE745DF43511105C232326A317734B7A60BBD3E258B2E159A5B304`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 재검증 기준 P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 배치 내부 생성 시점 catalog SHA-256: `3A0FE9B37584AC7BC82B86E56831C26B8D42B1FAC512EF728581485F7B6E3160`
- 임시 단독 병합 catalog SHA-256:
  `BB3838C3DDBFBD567457E14FFBD351D4C0207BE7CF712A1ED15793552AB7F7C9`
- batch merge report SHA-256:
  `E58262061CE410184C746992E94F8F9B5F2794BE18AAE2295306CBD0AC471C1C`
- 단독 validation JSON SHA-256:
  `DA320BEF37860B8221DB904911988CA73041E3B23A3D06D9F2FBD2727CF303BE`

배치의 entry별 `source_en`과 SC UTF-16LE SHA-256은 현재 P3에서도 모두 일치했다. 따라서 생성 시점 catalog 해시는 provenance로 남기고, 이번 재검증 결과는 현재 P3를 기준으로 기록한다.

## 교차 검수 반영 내역

- ID 4002: `상대가 보유한 %s 등급보다 높은 가보는 줄 수 없습니다.` → `상대가 보유한 %s 가보보다 상위 등급의 가보는 줄 수 없습니다.`
- ID 4010: `특정 무장의 휘하로 임명할 것을 약속합니다.` → `특정 무장의 휘하에 배속할 것을 약속합니다.`
- ID 4038: `시나리오에 반영할 사실 무장의 편집 데이터를 선택합니다.` → `시나리오에 반영할 실존 무장의 편집 데이터를 선택합니다.`
- ID 4042: `편집한 사실 무장 데이터가 없습니다.` → `편집한 실존 무장 데이터가 없습니다.`
- ID 4055: `친아버지·혈연·친애 무장·혐오 무장으로 다른 등록 무장이 설정되어 있으면\n해당 관계가 삭제됩니다.` → `생부·혈연·친애 무장·혐오 무장에 다른 등록 무장이 설정된 경우\n해당 관계를 삭제했습니다.`

ID 4002의 `%s`와 ID 4055의 줄바꿈 1개를 포함해 모든 형식 불변식을 보존했다.

## 주요 번역 판단

- `Promise`, `Land Holder`, `Lord`, `Conservator Emigre`는 누적 용어 `약정`,
  `영주`, `성주`, `외양 가재`로 통일했다.
- `Commendation`, `Covert`, `Defensive Base`, `Resupply Base`는 각각 `감장`,
  `조략`, `방위 거점`, `보급 거점`으로 유지했다.
- ID 4030-4035는 EN 슬롯이 반각 공백이지만 SC/JP에 실제 문구가 있는 언어별 비대칭
  항목이다. SC 실행 경로의 게임 계승 안내를 기준으로 번역했다.
- ID 4056-4057은 JP의 실제 편집 조건을 따라 얼굴 CG와 음성 이외를 변경하면
  업적 또는 트로피를 얻을 수 없다고 번역했다.
- ID 4058은 SC의 임시 문구보다 EN의 실제 기능 설명을 우선해 이름 폭 초과 안내로
  옮겼다.

## 형식 invariant

printf 토큰이 있는 항목은 24개이며 종류와 순서를 SC 기준으로 보존했다. ID 4014-4016,
4048-4050의 전각 퍼센트와 다중 `%d`, ID 4026의 네 `%d`, ID 4029의 `%s` 뒤
`%d` 순서를 유지했다.

SC 줄바꿈이 있는 6개 항목도 개수를 그대로 보존했다. ID 4052와 4053의
`ESC CP Σ ESC CZ` 색상 코드 및 ID 4052의 전각 공백·전각 퍼센트·전각 괄호를
유지했다. PUA와 기타 제어문자는 없고 invariant override도 사용하지 않았다.

## 단독 병합·검증

기준 카탈로그 복사본에 이번 배치만 병합했다.

- `batch_entries=60`
- 전체 행: 5,100개
- 상태: `translated=339`, `untranslated=3723`, `empty=1038`
- buildable: 339개
- 검증: `valid=true`
- 오류: 0개
- 경고: 0개

stock 4개 언어 `MSG_PK/*/msgui.bin`의 packed/raw SHA-256도 meta와 모두 일치했다.

## 단독 빌드와 결정성

같은 단독 병합 catalog를 서로 다른 두 출력 디렉터리에 빌드했다.

- 대상 `msgui.bin` 크기: 87,596바이트
- 대상 `msgui.bin` SHA-256:
  `3048A277F4E4F3C6AFA2E135306B89326DC6B728EB75C1CFB678483EDBBCFE08`
- 대상 raw 크기: 87,228바이트
- 대상 raw SHA-256:
  `399589CECF82CB1486A3C1FC4D8D6F047CA94EB7736CF52135AD01DFE946F16F`
- 전체 실제 바이너리 변경: 339개(현재 P3 seed 279개와 이번 번역 60개)
- 글리프 수요: 332자
- 한글 음절 수요: 298자
- build manifest SHA-256:
  `3DFE2A21AF6B227E7495EA1023D38430227789210423DDC7120428A4486CCB24`
- glyph demand SHA-256:
  `8D3D868F0258F84E8A697D5C3FBFA9CCD7E6FC64B8F15F1FB4FE0273EB9DE670`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다.
검증 뒤 설치본 `MSG_PK/SC/msgui.bin`은 stock SHA-256
`C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82` 그대로다.
`RES_SC/res_lang.bin`도 stock SHA-256
`916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99` 그대로다.
결정성 산출물은 무시된 `KR_PATCH_WORK/tmp/revalidate_3901_4100/4001_4100/build_a` 및 `build_b` 아래에만 생성했다.
