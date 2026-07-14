# MSGUI 전체 한글화 작업선

공식 간체중문(SC) 가로쓰기 경로의 `MSG_PK/SC/msgui.bin` 5,100개 ID를 다룬다.
이 작업선은 파일 전용이며 프로세스 메모리, DLL 주입, 후킹, EXE, 레지스트리를
사용하지 않는다.

## 권위 있는 현재 상태

과거 P3/P4 개발 카탈로그와 `4,062개·미번역 0` 보고서는 역사 기록이다. 현재 기준은
날짜 오역 QA 뒤 생성한 v0.1 overlay와 비대칭 슬롯을 재분류한 v0.2 후보이다.

| 분류 | v0.1 안정 기준 | v0.2 후보 |
|---|---:|---:|
| 번역·검수 엔트리 | 3,951 | 4,037 |
| 실제 SC 교체 operation | 3,836 | 3,922 |
| canonical empty | 1,038 | 1,041 |
| 일반 SC 비공백 미번역 | 0 | 0 |
| 의도적 언어 전용 공백 | 미분류 22+구조 3 | 22 |
| SC 공백 비대칭 번역 대기 | 86 | 0 |

v0.2 개발 카탈로그의 정확한 상태는 `empty=1,041`, `untranslated=22`,
`translated=4,019`, `reviewed=18`이다. `untranslated` 22개는 일본어 읽기·IME 전용이라
SC 공백을 의도적으로 유지하며 번역 누락으로 취급하지 않는다.

## 현재 공개 산출물

- 안정 overlay: `data/public/msgui_ko_0000_5099.v0.1.json`
  - 3,951개, SHA-256
    `65994E73624B90951D64369D20097CE46ACAFCDBD0C2EFA18B40975126F3F8C6`
  - 장수명 v0.1 RC에 포함된 메시지 기준
- v0.2 번역 후보: `data/public/msgui_ko_0000_5099.v0.2.json`
  - 4,037개, SHA-256
    `5DC3C0E14E2131FC2BB4252DF3B25E1F10E462205EAB715E2923298A714B8C14`
  - 원래 SC 공백이던 언어 중립·내부 효과명 86개 추가
  - 일본어 전용 22개와 구조 공백 3개는 적용하지 않음
- v0.2 recipe: `asymmetric_v02/public/msgui_sc.recipe.json`
  - 3,922 operation
  - SHA-256 `88094B17FC90E892020B8301476D1F7899B60389C9E805929C618DFC5EA517BF`
  - target SHA-256
    `C683AE9355A43F9A2104E49A6179363727CE0A550682F906C224A44F506826AC`

개발 카탈로그와 `data/translations/`에는 상용 다국어 원문이 있으므로 Git·공개 패치에
넣지 않는다. 공개 overlay와 recipe에는 numeric ID, stock SC 문자열의 UTF-16LE 해시,
프로젝트 소유 한국어와 검수 메타데이터만 둔다.

## 비대칭 슬롯 결정

SC가 공백이고 EN/JP에만 문구가 있는 108개를 독립 검토했다.

- 번역 86개: `2329–2348, 2408–2409, 2419–2420, 2457, 2459, 2558,
  2650, 2657, 2661, 2691–2746`
- 공백 보존 22개: `513, 689, 691, 1302, 1350, 1352, 1694, 1921–1932,
  2570–2572`
- 구조 empty 3개: `733, 734, 1607`

ID 2657만 공식 EN의 printf 토큰을 근거로 `printf:EN` override를 사용한다. ID 2729와
2730은 EN과 JP의 의미가 충돌해 효과 배열 구조와 EN을 따라 병력 회복으로 번역했으며
런타임 확인 대상으로 남긴다.

## 안전 장치

- 네 언어 원본 파일과 모든 원문 UTF-16LE 해시 고정
- printf 순서, ESC 색상 코드, PUA 아이콘, 개행 수 보존
- 공개 overlay의 정확한 root/nested/entry 필드 허용 목록 검증
- 중복 키와 대소문자 충돌 키 거부
- 비-MSGUI `msgdata`·`msgev` 개발 batch 자동 제외
- 출력은 별도 경로에만 생성하고 설치 파일을 직접 덮어쓰지 않음
- 공개 recipe를 순정 fixture에 적용해 고정 target을 바이트 단위로 재현

v0.2 overlay export, public replay, 빌드, recipe export는 서로 다른 두 경로에서 모두
byte-exact였다. 요구 글리프 파일은 장수명 Font-v5의 MSGUI corpus와 SHA-256까지 같아
UI v0.2만으로는 폰트 재빌드가 필요 없다.

## 다음 게이트

1. 새로 활성화하는 86개 SC 공백 슬롯의 실제 화면·전투 효과 문맥을 확인한다.
2. 성 이름·대사 초벌을 합친 Font-vNext를 별도로 생성·검증한다.
3. 장수명 RC를 정확한 predecessor로 받는 새 4리소스 설치기를 versioned workstream으로
   만든다. 과거 P4 2파일 설치기는 Font-v5와 장수명 상태를 안전하게 다루지 못하므로
   재사용하지 않는다.
4. stock fixture와 현재 장수명 RC fixture 양쪽에서 적용, 중단 복구, 완전 원복을 검증한다.
5. 실제 게임 화면 QA와 외부 독립 감사를 통과하기 전에는
   `release_eligible=false`를 유지한다.

자세한 v0.2 분류·해시·승격 상태는 `asymmetric_v02/README_KO.md`와
`asymmetric_v02/validation.json`에 있다.
