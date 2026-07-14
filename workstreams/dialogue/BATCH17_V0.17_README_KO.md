# 역사 이벤트 대사 batch17 v0.17

`msgev` ID 5109~5237의 실제 표시 대사 129개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.16, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 흰 원숭이와 히라유 온천 | 5109~5136 | 28 |
| 다케나카 한베에의 이나바야마성 탈취 | 5137~5160 | 24 |
| 요시히메와 다테 데루무네의 혼인 | 5161~5183 | 23 |
| 나가오 마사카게와 우사미 사다미츠의 죽음 | 5184~5217 | 34 |
| 미요시 나가요시의 죽음 | 5218~5237 | 20 |
| 합계 | 5109~5237 | 129 |

ID 5108은 v0.16의 마지막 대사다. ID 5237에서 미요시 나가요시가 죽은 뒤 마쓰나가 히사히데가 자신의 앞날을 자문하는 사건이 끝난다. 다음 번역 시작점인 ID 5238부터는 이마가와 요시모토의 죽음이 간토·고신의 외교 관계에 끼친 영향을 설명하는 새 사건이 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 129개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 387개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 31이다. 길이 예외와 원문 고정 개행 예외는 없다.
- 고슈 병사, 독안개·유황 가스, 히라유 온천 유래, 고쿠진, 미노 반국 제안, 덴분의 난, 독안룡, 노지리호·우사미 사다미츠, 마사카게 익사설, 우노마쓰, 일본의 부왕, 최초의 천하인 관련 독음·용어·역사적 맥락은 최종 용어집과 역사 검수가 필요하다.
- 기존 인명·지명 표기의 다케나카 한베에, 사이토 요시타쓰·다쓰오키, 안도 모리나리, 모가미 요시아키, 요시히메, 다테 데루무네, 나가오 마사카게·아키카게, 센토인, 우사미 사다미츠, 우에스기 가게카쓰, 미요시 나가요시·요시쓰구, 이나바야마·기나이·세토우치를 따랐다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.16 공개 overlay·근거·검토 인덱스·validation 64개를 개별 SHA-256으로 고정했다.
- 그 64개 경로·해시의 결정적 manifest SHA-256은 `150476CE86FCDA26DA0819395FAC8B913CDB01E9D9FBFF9B3D9A0876C7B7487C`다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.17은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_5109_5237.v0.17.json` | `3DDBDFDE91384B344A6E93946E3216C1444DD05689E6D92E5CF4E3D2F51A9406` |
| `evidence/alignment_evidence.v0.17.json` | `544640CB547BE5AA8A8DE00286A0D365E79EB2BD842561C245F8720F086AE725` |
| `review/review_index.v0.17.json` | `97E31C05E632B34C9C308EF0DC4B850DE02A20018CA155DE18CE42F27F30E3BA` |
| `validation.v0.17.json` | `1F674B7E31A0ED067B714DB5D9BB7A2AB6592F86E04799E33D0163C0865192EA` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch17.py"

foreach ($Out in @(
  "tmp\dialogue_batch17_a",
  "tmp\dialogue_batch17_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch17 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch17.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch17 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation은 각각 바이트 단위로 같아야 한다.
