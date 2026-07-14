# 역사 이벤트 대사 batch15 v0.15

`msgev` ID 4839~4976의 실제 표시 대사 138개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.14, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 아키쓰라의 연회와 요시시게의 개심 | 4839~4873 | 35 |
| 미요시 짓큐의 죽음 | 4874~4887 | 14 |
| 스와 시로 가쓰요리의 원복 | 4888~4910 | 23 |
| 사나다 마사유키의 원복 | 4911~4914 | 4 |
| 모리 다카모토의 죽음 | 4915~4939 | 25 |
| 모토야스의 오카자키 독립 | 4940~4976 | 37 |
| 합계 | 4839~4976 | 138 |

ID 4838은 v0.14의 마지막 대사다. ID 4976에서 모토야스의 오카자키 독립과 `염리예토 흔구정토` 깃발의 유래가 끝나며, 다음 번역 시작점인 ID 4977부터는 야마나카 시카노스케의 녹각 투구와 용맹을 소개하는 사건이 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 138개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 414개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 삼박자·쓰루사키오도리, 아키쓰라의 도세쓰 개명과 법호 유래, 네고로슈·미요시 짓큐, 다케다·스와 가문의 통자, 기헤에 마사유키·표리비흥의 자, 다카모토 독살설·고쓰루마루, 쇼닌·도요 쇼닌, `염리예토 흔구정토` 관련 독음·용어·역사적 맥락은 최종 용어집과 역사 검수가 필요하다.
- 기존 장수명·지명 표기의 오토모 요시시게, 아타기 후유야스, 스와히메, 모리 다카모토·데루모토, 오카자키·스루가를 따랐고, 게임 공통 용어집에 따라 `国衆`은 `국인중`, `城代`는 `성대`로 통일했다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.14 공개 overlay·근거·검토 인덱스·validation 56개를 개별 SHA-256으로 고정했다.
- 그 56개 경로·해시의 결정적 manifest SHA-256은 `CEC31430C4920744C39B9B62F5CCDBD173A89D0EA2A35950D5C5C3FA38578F2C`다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.15는 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_4839_4976.v0.15.json` | `81568BBD13BF61F4CAE83E9F893ECA7DA723ADB76200F25D1D38011FFE3A831A` |
| `evidence/alignment_evidence.v0.15.json` | `4BA6A777EE108B84E8FE9723A97AF75CD6A8FDDEE9BC9B9908A24D0BAFB5DA6B` |
| `review/review_index.v0.15.json` | `957C55863EEEBB23E0D36FCBACB2BB630E195F2A2A3039D852D97BFF4B0B1C71` |
| `validation.v0.15.json` | `C2298D40384B680FF482DCD63B7E13BFC9FD1236FD83B434A1DBA3DAE09A0BF4` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch15.py"

foreach ($Out in @(
  "tmp\dialogue_batch15_a",
  "tmp\dialogue_batch15_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch15 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch15.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch15 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation은 각각 바이트 단위로 같아야 한다.
