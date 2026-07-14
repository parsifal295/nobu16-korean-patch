# 역사 이벤트 대사 batch22 v0.22

`msgev` ID 5749~5873의 실제 표시 대사 125개를 한국어 초벌 번역했다. 입력 배치는 기존 v0.1~v0.21, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일을 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 오토모의 모리 포위망 | 5749~5776 | 28 |
| 아네가와 전투 전야 | 5777~5802 | 26 |
| 하마마쓰 입성과 오카자키의 불씨 | 5803~5816 | 14 |
| 모가미 요시아키의 가독 계승 | 5817~5838 | 22 |
| 모가미 요시아키의 힘돌 | 5839~5855 | 17 |
| 이마야마 전투 전야 | 5856~5873 | 18 |
| 합계 | 5749~5873 | 125 |

ID 5748은 v0.21의 마지막 대사다. 다음 번역 시작점은 ID 5874이며, 다테 가문의 덴분의 난이 화의로 끝나는 새 사건이 시작된다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 의미를 가리키는 실제 표시 대사만 포함했다.

## 번역·검증 상태

- 125개 모두 자동 초벌 뒤 사람이 문체를 대조했으며 실제 게임 화면 검수는 아직 필요하다.
- 같은 ID의 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 375개의 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 오토모 동적 이름, 무라카미 수군, 스오 차우스산, 아네가와 전투, 히쿠마·하마마쓰성, 쓰키야마도노·세나히메, 모가미 요시아키, 우슈의 여우, 우슈·자오온천, 요시아키 공의 힘돌, 규슈 탐제, 쇼니 가문, 게이긴니, 이마야마 전투는 최종 용어집과 실제 화면 검수가 필요하다.
- 공개 overlay·근거·검수 인덱스·validation에서 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.21 공개 overlay·근거·검수 인덱스·validation 84개를 개별 SHA-256으로 고정했다.
- 그 84개 경로·해시의 결정론적 manifest SHA-256은 `92CDC4C6BA43B8D28F6FD48B3C20AE86525450C47E8A7318CFE162F9968A5355`다.
- 빌드 전후 설치별 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교했으며 빌더는 게임 파일에 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치별 불변만 증명한다. v0.22는 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_5749_5873.v0.22.json` | `AF82BB146540FBD72A14149BD93F8CA37F0F27C080A80E42502803284BBA3029` |
| `evidence/alignment_evidence.v0.22.json` | `8BFE5C891A6497529B1440512488719446F7FA08E940A7BD117554D4D1788B32` |
| `review/review_index.v0.22.json` | `FA44B01EFCE5E565D5BDAB875A20CA8633D58D0B44661EE18D7F17C662FB2B76` |
| `validation.v0.22.json` | `F76C2B29E9356EEEFDF99356A6451547DD480F55B4C930EF552F943D87F8645C` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch22.py"

foreach ($Out in @(
  "tmp\dialogue_batch22_a",
  "tmp\dialogue_batch22_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch22 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch22.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch22 tests failed" }
```

세 번의 출력에서 overlay·근거·검수 인덱스·validation은 각각 바이트 단위로 같아야 한다.
