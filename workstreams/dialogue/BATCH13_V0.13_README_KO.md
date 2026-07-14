# 역사 이벤트 대사 batch13 v0.13

`msgev` ID 4557~4690의 실제 표시 대사 134개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.12, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 마쓰나가 히사히데의 시기산성 축성 | 4557~4569 | 13 |
| 호조 가문과 가게토라의 간토 원정 | 4570~4591 | 22 |
| 다케다 침공과 호조·우에스기 화의 | 4592~4609 | 18 |
| 가게토라의 간토 원정 선언 | 4610~4631 | 22 |
| 소고 가즈마사의 죽음과 저주 소문 | 4632~4656 | 25 |
| 나가노 나리마사의 유언 | 4657~4690 | 34 |
| 합계 | 4557~4690 | 134 |

ID 4556은 v0.12의 마지막 대사다. ID 4690에서 나가노 나리마사의 죽음과 사나다 가문의 누마타 계승 복선이 끝나며, 다음 번역 시작점인 ID 4691부터는 가와나카지마 전투에서 다케다 노부시게가 전사하는 사건이 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 134개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 402개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 단조쇼히쓰, 조고손시지, 아리마 곤겐, 간토 마쿠추몬, 오니소고, 미요시 짓큐, 조슈의 호랑이, 사나다 단조노조, 법요 관련 독음·용어·역사적 맥락은 최종 용어집과 역사 검수가 필요하다.
- 게임 공통 용어집에 따라 `国衆`은 `국인중`으로 통일했다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.12 공개 overlay·근거·검토 인덱스·validation 48개를 개별 SHA-256으로 고정했다.
- 그 48개 경로·해시의 결정적 manifest SHA-256은 `C534CB6BF7F101A3D240A4A566F871AAB2942E59C3F47DB77041D8F397B5F472`다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.13은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_4557_4690.v0.13.json` | `DF52C23A3F94971F7B8D308DAE787C69951F08F3B879B9851A60327180E6B87E` |
| `evidence/alignment_evidence.v0.13.json` | `2BFBAF33FF4F7631AA357DA9DCB75CACEC3AE623886B2377EE3EAEFDC78364C9` |
| `review/review_index.v0.13.json` | `5493740F875F8AFED7D9FE3CAB3CF8FD389D0C805CFDB9B111783DE0D7E3493D` |
| `validation.v0.13.json` | `43E633DA4542A046123CC2F50C5206379C06DF8F8F1029FDFD765FADE79948FD` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch13.py"

foreach ($Out in @(
  "tmp\dialogue_batch13_a",
  "tmp\dialogue_batch13_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch13 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch13.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch13 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation은 각각 바이트 단위로 같아야 한다.
