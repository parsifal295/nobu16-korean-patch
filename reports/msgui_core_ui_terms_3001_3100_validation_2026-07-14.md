# msgui ID 3001-3100 번역 배치 검증 기록

## 결과

- 조사 범위: ID 3001-3100, 정확히 100행
- 번역 배치 엔트리: 100개
- 실제 번역 문자열: 100개
- 원문 및 SC UTF-16LE 해시 대조: 100개 모두 일치
- 검증: `valid=true`, 오류 0개, 경고 0개
- printf·ESC·PUA·기타 제어문자·줄바꿈 invariant override: 0개
- canonical `empty` 및 공백-only 구조 슬롯: 없음
- 설치 게임 파일 변경: 없음

이 배치는 상용 다국어 원문을 포함하는 개발 전용 파일이다. 공개 배포에는 직접 넣지 않고 추후 source-free overlay만 생성한다.

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_3001_3100.v0.1.json`
- 배치 SHA-256: `4559E29F8C2686519B1E28D97AF5A4FC222D74B205EEA69A82B679889BCE630F`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 임시 단독 병합 catalog SHA-256: `48FD471D8DE6FF974EBB6004CD1704538BE2F36F7725B60C90B8FFE79CD402D3`
- merge 보고서 SHA-256: `89BD69242DE2DB09CF86E20E5D4063DA8CFF403E2C1F75C79B07BF1115ECA3A8`
- validation JSON SHA-256: `755BDB608118CF8CC3E9B992ECC3D37FD47B305C3CDCF0E93E37D34382A2AC83`

## 번역 범위와 용어 판단

- ID 3001-3031: 지행 무장 임명·해임, 미지행 군 일괄 임명, 정책 효과, 군 정보와 선택 안내
- ID 3032-3054: 전투·저장·등록 무장·군단·전봉·도움말·거래 관련 안내와 오류 메시지
- ID 3055-3084: 세력·출진·교섭·부대·성·국인중 명령, 포로 처우, 데모 플레이 안내
- ID 3085-3100: 다이묘 선택, 인물 설명, 설정 초기화, 이벤트·맹약·공략 조건과 수치 표시

누적 배치의 용어를 우선해 `知行武将=지행 무장`, `未知行郡=미지행 군`, `転封=전봉`, `具申=건의`, `主命=주명`, `威風=위풍`, `威信=위신`, `国衆=국인중`, `家宝=가보`, `官職=관직`, `登録武将=등록 무장`, `デモプレイ=데모 플레이`, `朝廷=조정`, `領主=영주`로 통일했다.

동일 SC 원문은 기존 번역과 정확히 맞췄다.

- ID 3011 `金钱不足`: ID 1954와 동일하게 `금전 부족`
- ID 3019 `未选择武将`: ID 2882·2889와 동일하게 `선택한 무장이 없습니다.`

## 형식 invariant와 공백 처리

SC 기준 printf 순서와 종류를 모두 그대로 유지했다.

- ID 3021: `%d`, `%d`
- ID 3038: `%s`
- ID 3051: `%s`, `%d`
- ID 3060: `%s`
- ID 3073: `%s`
- ID 3092: `%d`
- ID 3098: `%d`
- ID 3099: `%s`, `%s`, `%d`
- ID 3100: `%d`, `%d`

ID 3038의 `ESC CB`와 `ESC CZ` 색상 제어 시퀀스를 `%s` 양쪽에 원문 순서대로 유지했다. EN·JP에는 줄바꿈이 있지만 실제 기준인 SC에는 줄바꿈이 없으므로 한국어도 한 줄로 유지했다.

SC 줄바꿈 수를 다음과 같이 보존했다.

- ID 3021: 2개
- ID 3037, 3046, 3060, 3067, 3088: 각 1개
- ID 3074, 3083, 3084: 각 4개
- ID 3089: 6개

PUA와 기타 제어문자는 이 범위에 없다. 원문과 번역 모두 선두·후미 공백이 없으며, 공백-only 구조 슬롯도 없다. ID 3089의 목록 줄 시작 전각 공백 `U+3000`은 SC 배열대로 보존했다. 형식 예외는 사용하지 않았다.

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
- 이번 범위 실제 SC 문자열 변경: 100개
- 이번 범위 byte-equal: 0개

stock 네 언어 원문 해시와 형식 invariant를 모두 대조했고 허용 예외는 사용하지 않았다.

## 단독 빌드와 재현성

같은 단독 병합 catalog를 서로 다른 두 출력 디렉터리에 연속 빌드했다.

- 대상 `msgui.bin` 크기: 88,174바이트
- 대상 `msgui.bin` SHA-256: `2514140B859586DE8C81937658C3DB3FD68E8CA6E6C68EEFD5B1A899D5E5D32E`
- 대상 raw 크기: 87,804바이트
- 대상 raw SHA-256: `6E50E34D2D99D342227C1772C83973186E1450C0262B5290E2DAA5CA8CC840EC`
- 전체 실제 바이너리 변경: 379개(P3 seed 279개 + 이번 배치 100개)
- 글리프 수요: 328자
- 한글 음절 수요: 301자
- build manifest SHA-256: `59EF682CEE6B0FB27853FF1B07D656882CD82B760CAA44A0FFF6708569272C2A`
- glyph demand SHA-256: `3CB324104CC0BC10561EF43D0CF96B3FF5B63297A77E3DF7532A2C0C5A893123`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다. 모든 빌드 manifest에 `installed_game_files_modified=false`가 기록되었다.

## 원본·설치본 무변경

- 설치본 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 설치본 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- P3/P4 canonical, 공개 overlay, Font-v4, 성 이름 workstream, 배포 경로를 수정하지 않았다.
- 실제 쓰기 범위는 이번 번역 배치, 이 보고서, 무시된 `KR_PATCH_WORK/tmp/translate_3001_3100_validation` 아래 임시 검증 산출물뿐이다.
