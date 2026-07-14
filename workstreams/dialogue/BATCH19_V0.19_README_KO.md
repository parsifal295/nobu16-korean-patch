# 역사 이벤트 대사 batch19 v0.19

`msgev` ID 5359~5486의 실제 표시 대사 128개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.18, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 스노마타 축성과 하치스카 고로쿠 | 5359~5382 | 24 |
| 나가노 가문과 미노와성의 최후 | 5383~5411 | 29 |
| 오이치와 아자이 나가마사의 혼인 | 5412~5438 | 27 |
| 시카노스케의 칠난팔고 기원 | 5439~5447 | 9 |
| 미노 삼인중의 사이토 이반 | 5448~5464 | 17 |
| 노부나가의 간레이와 부쇼군직 거절 | 5465~5486 | 22 |
| 합계 | 5359~5486 | 128 |

ID 5358은 v0.18의 마지막 대사다. ID 5486에서 노부나가가 간레이와 부쇼군직을 거절한 뒤 교토와 미쓰히데를 얻은 것이 가장 큰 성과였다고 말하는 사건이 끝난다. 다음 번역 시작점인 ID 5487부터는 이른바 ‘적에게 소금을 보내다’ 일화가 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 128개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 384개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ID 5465의 SC 원문에서 색상 범위가 개행을 가로지르는 비정상 구조도 임의로 고치지 않고 그대로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 가와나미중·나가라강, 조슈의 호랑이, 코즈케 제일창 감장, 칠난팔고, 입도명 잇테쓰·보쿠젠, 미노 삼인중, 간레이·부쇼군, 막부의 아버지 일화 관련 독음·용어·역사적 맥락은 최종 용어집과 역사 검수가 필요하다.
- 기존 인명·지명 표기의 하치스카 고로쿠, 나가노 나리마사·나리모리, 가미이즈미 노부츠나, 오이치, 아자이 나가마사, 야마나카 시카노스케, 사이토 다쓰오키, 이나바 요시미치, 우지이에 나오모토, 안도 모리나리, 오다 노부나가, 아케치 미쓰히데, 스노마타·미노와·코즈케·오미·이나바야마·교토를 따랐다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.18 공개 overlay·근거·검토 인덱스·validation 72개를 개별 SHA-256으로 고정했다.
- 그 72개 경로·해시의 결정적 manifest SHA-256은 `53EF61C01DDE8FF9E0225D6F94A22C71440165ED2BDCBE71FB22F470410BE3FE`다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.19는 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_5359_5486.v0.19.json` | `9BD0043254DEDE78D9B11D1F8D7FDC66316277BB54B2964DB178F68EFDBFA88E` |
| `evidence/alignment_evidence.v0.19.json` | `C9CAC451FFC28C1BFACEA9543BD632E171311F36745F53C48D8257363B72F3AE` |
| `review/review_index.v0.19.json` | `F529FA5AEB92F4EE4037AC480DE5287278CE083ED59CB2932781E76E2827BCD5` |
| `validation.v0.19.json` | `056605D93E105ACFBAFE4391FFA69FC6B0C0A5D4788C7D279FBB4FC8C5D6A633` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch19.py"

foreach ($Out in @(
  "tmp\dialogue_batch19_a",
  "tmp\dialogue_batch19_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch19 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch19.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch19 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation은 각각 바이트 단위로 같아야 한다.
