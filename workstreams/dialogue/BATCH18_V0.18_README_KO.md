# 역사 이벤트 대사 batch18 v0.18

`msgev` ID 5238~5358의 실제 표시 대사 121개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.17, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 이마가와의 몰락과 다케다의 방침 전환 | 5238~5255 | 18 |
| 에이로쿠의 변과 요시아키 구출 | 5256~5293 | 38 |
| 난부 노부나오의 후계자 입양 | 5294~5299 | 6 |
| 요시아키의 상경 요청과 아케치 미쓰히데 | 5300~5337 | 38 |
| 우키타 나오이에의 미무라 이에치카 암살 | 5338~5349 | 12 |
| 마쓰다이라 이에야스의 도쿠가와 개성 | 5350~5358 | 9 |
| 합계 | 5238~5358 | 121 |

ID 5237은 v0.17의 마지막 대사다. ID 5358에서 마쓰다이라 이에야스가 도쿠가와 성을 택한 사건이 끝난다. 다음 번역 시작점인 ID 5359부터는 새 사건인 스노마타 축성 대사가 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 121개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 363개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ID 5315의 SC 원문에 있는 비정상 동적 토큰 배열도 임의로 고치지 않고 바이트 구조를 그대로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 고소슨 삼국 동맹, 이치노타치, 난토·고후쿠지·이치조인 가쿠케이, 에이로쿠의 변, 미카와슈·미카와노카미, 도쿠가와 계보 관련 독음·용어·역사적 맥락은 최종 용어집과 역사 검수가 필요하다.
- 기존 인명·지명 표기의 이마가와 요시모토, 다케다·호조, 미요시 나가요시, 마쓰나가 히사히데·히사미치, 아시카가 요시테루·요시아키, 호소카와 후지타카, 난부 하루마사·노부나오, 이시카와 다카노부, 오다 노부나가, 아케치 미쓰히데, 우키타 나오이에, 미무라 이에치카, 마쓰다이라·도쿠가와 이에야스, 기나이·교토·미노·미카와를 따랐다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.17 공개 overlay·근거·검토 인덱스·validation 68개를 개별 SHA-256으로 고정했다.
- 그 68개 경로·해시의 결정적 manifest SHA-256은 `EF7473AE37B1E4F6BE0B95629F6CF5021D07FBC7BB09344A195FE2B7029D4CBB`다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.18은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_5238_5358.v0.18.json` | `B6E9F58EBC968B89D6B8765F22E3353F234B3418CE441A6DDE7442B70F164EE1` |
| `evidence/alignment_evidence.v0.18.json` | `E1D40FC55AF570DC9298F87EC720435366AA55DEDAE5F54956C9C49E770145A4` |
| `review/review_index.v0.18.json` | `1EB13DC83C2A2F49CC1532D299FD8FFC1B5F5242FE4F259CA67E9AE7F51801C7` |
| `validation.v0.18.json` | `279A28FEC4B400CAF027D84441CCBBCD948B1A7759C403833E5FE289B8BD546B` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch18.py"

foreach ($Out in @(
  "tmp\dialogue_batch18_a",
  "tmp\dialogue_batch18_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch18 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch18.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch18 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation은 각각 바이트 단위로 같아야 한다.
