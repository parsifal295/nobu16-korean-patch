# 역사 이벤트 대사 batch10 v0.10

`msgev` ID 4161~4279의 실제 표시 대사 119개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.9, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 아마고 신구토 숙청 | 4161~4179 | 19 |
| 이쓰쿠시마 결전 준비 | 4180~4209 | 30 |
| 다이겐 셋사이의 죽음 | 4210~4230 | 21 |
| 노부나가의 기요스 천거 | 4231~4235 | 5 |
| 사이토 부자의 불화 격화 | 4236~4249 | 14 |
| 데루토라, 후시키안 겐신으로 개명 | 4250~4257 | 8 |
| 나가라강 전투 | 4258~4279 | 22 |
| 합계 | 4161~4279 | 119 |

ID 4160은 v0.9의 마지막 대사다. ID 4279에서 나가라강 전투와 도산의 유언이 끝나며, 다음 번역 시작점인 ID 4280부터는 별도의 ‘가게토라 출가 소동’ 사건이 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 119개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 357개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- 순정 SC ID 4245·4246에 있는 `[[bm921]`, `[[bm924]`의 여분 여는 대괄호도 원문 구조대로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 신구토, 요시다 고리야마성, 규에이 쇼기쿠, 고소슨 삼국동맹, 교토·가마쿠라 왕환로, 야쿠오 소켄, 후시키안 겐신 관련 독음·용어는 최종 용어집 검수가 필요하다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.9 공개 overlay·근거·검토 인덱스·validation 36개를 개별 SHA-256으로 고정했다.
- 그 36개 경로·해시의 결정적 manifest SHA-256은 `52E9461FF70C5B4C9F7FC460AB7B0657207160D476B32383C2BA1D89749D2A80`이다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.10은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_4161_4279.v0.10.json` | `30C843032B2C8B7F8204840E02BEED3D67935F3E46770BF9C1EA889B5EEB763A` |
| `evidence/alignment_evidence.v0.10.json` | `A1D8BE1BDF0CD801E5FBBEA2E99BB6B1D00957E792FD32C7637E0799981EF089` |
| `review/review_index.v0.10.json` | `5D5C7CD307C88DCB4E54262C178094261E7319C1FE8AFFAD5C15C598D9ABD927` |
| `validation.v0.10.json` | `D62BF8D021C6993523083C99CC83EA9E68699320FA79A038992D8FCF45D996C8` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch10.py"

foreach ($Out in @(
  "tmp\dialogue_batch10_a",
  "tmp\dialogue_batch10_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch10 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch10.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch10 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation이 각각 바이트 단위로 같아야 한다.
