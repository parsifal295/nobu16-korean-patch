# 역사 이벤트 대사 batch11 v0.11

`msgev` ID 4280~4417의 실제 표시 대사 138개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.10, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 가게토라 출가 소동 | 4280~4314 | 35 |
| 이노 전투와 노부카쓰의 사면 | 4315~4357 | 43 |
| 오우치 가문의 멸망 | 4358~4376 | 19 |
| 도시이에와 마쓰의 혼인 | 4377~4386 | 10 |
| 아카마쓰 하루마사의 추방 | 4387~4400 | 14 |
| 우키타 나오이에의 죽음 | 4401~4411 | 11 |
| 하루노부, 신겐으로 개명 | 4412~4417 | 6 |
| 합계 | 4280~4417 | 138 |

ID 4279는 v0.10의 마지막 대사다. ID 4417에서 다케다 하루노부의 출가와 신겐 개명 사건이 끝나며, 다음 번역 시작점인 ID 4418부터는 별도의 히다국 미키 가문 사건이 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 138개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 414개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 덴시쓰 고이쿠, 노부카쓰의 이명, 미마사카노카미, 오우치 요시나가의 사세구, ‘창의 마타자’, 혼인 관용구, 도쿠에이켄 신겐 관련 독음·용어·문체는 최종 용어집과 문학 검수가 필요하다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.10 공개 overlay·근거·검토 인덱스·validation 40개를 개별 SHA-256으로 고정했다.
- 그 40개 경로·해시의 결정적 manifest SHA-256은 `7EB28BC2CE8BF3138F8F6F431A9AA5C70B2B49FFDC1F963CC9FF5A58174F3C3D`이다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.11은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_4280_4417.v0.11.json` | `E6A366499D89317F78C1E96BA546D10AB9ABE3FF9B49E49C299F6B69C38E3C23` |
| `evidence/alignment_evidence.v0.11.json` | `759E031F61D525B6B895CBB4258F135A06B83AA7D93744D53365F13F91245BD7` |
| `review/review_index.v0.11.json` | `3D9DF5E03F6F5F29C64E6B31EFCAF4E4C998A5F69B01825583002B76603923BA` |
| `validation.v0.11.json` | `5A2E6BEF1798C8BACB11F6D032C046277C2296A12C27DED7124C5639443BF6C8` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch11.py"

foreach ($Out in @(
  "tmp\dialogue_batch11_a",
  "tmp\dialogue_batch11_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch11 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch11.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch11 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation이 각각 바이트 단위로 같아야 한다.
