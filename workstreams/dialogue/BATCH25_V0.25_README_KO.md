# 역사 이벤트 대사 batch25 v0.25

`msgev` ID 6142~6268의 실제 표시 대사 127개를 한국어 초벌 번역했다. 기존 v0.1~v0.24 산출물, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않았다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 미카타가하라 패전과 하마마쓰 후퇴 | 6142~6163 | 22 |
| 다케다 신겐의 죽음 | 6164~6193 | 30 |
| 도도 다카토라와 출세의 흰 떡 | 6194~6234 | 41 |
| 아자이 나가마사의 최후 | 6235~6259 | 25 |
| 에치고 우에스기 가문의 단절 | 6260~6268 | 9 |
| 합계 | 6142~6268 | 127 |

다음 번역 시작점은 ID 6269다. 이 ID부터 아시카가 요시아키와 오다 노부나가의 결별 사건이 시작된다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 번호를 가리키는 실제 표시 대사만 포함했다.

## 번역·검증 상태

- 127개 모두 사람이 세 언어의 문맥을 대조해 작성한 초벌 번역이며, 실제 게임 화면 검수는 아직 필요하다.
- 각 ID의 SC·JP·EN 참조를 대조했다. 공개 근거에는 원문 대신 381개의 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이고 최댓값은 30이다. 길이 예외는 없다.
- 인명·지명·관직·군사·시가·말장난 용어 등 판단이 필요한 항목 20개는 검수 색인에 별도로 표시했다.
- 공개 overlay·근거·검수 색인·validation에서 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.24 공개 overlay·근거·검수 색인·validation 96개를 개별 SHA-256으로 고정했다.
- 그 96개 경로·해시의 결정론적 manifest SHA-256은 `6CA1F592F375460B645456CCCB95FEA2240A5FC24CA4D1C8106735209BE00CA4`다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256이 같음을 검증했다.
- v0.25는 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_6142_6268.v0.25.json` | `D84EB96DA649971811D80DDFDB154D30E4B305FD2D5889ADB462585A9315D891` |
| `evidence/alignment_evidence.v0.25.json` | `3A1977F08593A2FFC580472E4CCC256B9D035633CC8B4693238D275F550906BF` |
| `review/review_index.v0.25.json` | `02FA3B53EE2AE08E1E6EB7A425816DBC6C8AD529CBB01BD8E0769B150D30B14A` |
| `validation.v0.25.json` | `0A7C766B415A97171ADC56E1E92999CB2DEE3D30DD96A23DC4AD8F452676C3F4` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch25.py"

foreach ($Out in @(
  "tmp\dialogue_batch25_a",
  "tmp\dialogue_batch25_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch25 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch25.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch25 tests failed" }
```

세 번의 출력에서 overlay·근거·검수 색인·validation은 각각 바이트 단위로 같아야 한다.
