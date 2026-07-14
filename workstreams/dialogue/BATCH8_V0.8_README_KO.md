# 역사 이벤트 대사 batch8 v0.8

번역 속도를 우선해 `msgev` ID 3930~4031의 실제 표시 대사 102개를 한국어 초벌로 작성한 독립 배치다. 기존 v0.1~v0.7, 루트 README와 진행률 파일, 폰트·설치기·게임 파일은 수정하지 않았다.

## 범위

| 묶음 | ID 범위 | 번역 수 |
|---|---:|---:|
| 다케다 가문의 도이시성 패전 | 3930~3945 | 16 |
| 모리 모토나리의 이노우에 일파 숙청 | 3946~3961 | 16 |
| 오우치 요시타카의 다이네이지 최후 | 3962~3990 | 29 |
| 센토인과 나가오 마사카게의 혼인 | 3991~4002 | 12 |
| 호소카와 우지쓰나의 권한 이양 | 4003~4011 | 9 |
| 오다 노부히데의 죽음과 장례 | 4012~4031 | 20 |
| 합계 | 3930~4031 | 102 |

ID 3929는 v0.7의 마지막 대사다. 다음 번역 시작점은 새 이벤트가 시작되는 ID 4032다. 이번 범위에는 SC·JP·EN에서 공통으로 비표시 처리되는 내부 항목이 없다.

## 번역·검증 상태

- 102개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 SC·JP·EN을 대조했고, 공개 근거에는 원문 대신 306개의 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 줄바꿈, 앞뒤 공백, 제어문자, PUA, printf 토큰을 원문 구조대로 보존했다.
- `[b1251]`, `[bm1251]`, `[bm1448]`, `[b1448]` 같은 동적 장수명 자리표시자의 종류와 순서를 각 항목별로 검사했다.
- 공개 오버레이·근거·검수 인덱스·검증 JSON의 한자 및 가나 수는 모두 0이다.
- 3968번을 제외한 모든 작성 줄은 ESC 코드를 뺀 32코드포인트 이하다.
- 3968번은 원문에 수동 줄바꿈이 없고 색상 지정 인명이 여섯 번 들어가는 관계 설명문이라 자연스러운 번역을 유지했다. 작성 줄 길이는 54코드포인트이며 게임의 자동 줄바꿈 동작을 반드시 확인해야 한다.
- 두 개의 격리 출력과 최종 출력에서 아래 네 파일이 바이트 단위로 동일했다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_3930_4031.v0.8.json` | `3CE22CFC77829BD1A627FB0ABE80FC387196AED74DA3B79A29EDB5FAC2D77534` |
| `evidence/alignment_evidence.v0.8.json` | `739CC3631F35788B684755EA8BDEDC9C8AECC1C45C42630C9E797264C3E73665` |
| `review/review_index.v0.8.json` | `8CC9DDC3FCEF5D7A370BE4B6E8BB5AB325F5096DFE1E2719B80E410C971D032A` |
| `validation.v0.8.json` | `996727176B973D14451C65EB5AF0661BC50B40DFE53C8FAC01D26305E4751935` |

## 통합 제한

이 배치는 번역 검수용 독립 공개 입력이다. 현재 글꼴이나 설치기에 포함되지 않으며 게임 파일에도 적용되지 않았다. 배포본에 넣기 전에 v0.1~v0.8과 장수명 오버레이를 확정 SC 기준으로 병합하고, 재패킹·글리프 수요 계산·게임 내 UI 검수를 거쳐야 한다.

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch8.py"

foreach ($Out in @(
  "tmp\dialogue_batch8_a",
  "tmp\dialogue_batch8_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch8 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch8.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch8 tests failed" }
```
