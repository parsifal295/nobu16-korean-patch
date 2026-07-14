# 역사 이벤트 대사 batch3 v0.3

한글화 속도를 우선해 `msgev` ID 3309~3440 구간의 실제 표시 대사 114개를 한국어 초벌로 옮긴 독립 배치다. 기존 v0.1·v0.2, 현재 Font-v6, 설치기와 설치된 게임 파일은 수정하지 않았다.

## 범위

| 묶음 | ID 범위 | 번역 수 |
|---|---:|---:|
| 지역 통일 엔딩 9종 | 3311~3353 | 27 |
| 조정 관직 선택 | 3354~3384 | 31 |
| 천하통일 선언 | 3385~3394 | 10 |
| 관직별 통일 결과 | 3395~3402 | 8 |
| 장기 정권 결말 | 3403~3440 | 38 |
| 합계 | 3309~3440 | 114 |

ID 3309~3350 사이의 다음 18개는 SC·JP·EN에 똑같이 들어 있는 비표시 내부 지역 키이므로 번역하지 않았다.

`3309, 3310, 3314, 3315, 3319, 3320, 3324, 3325, 3329, 3330, 3334, 3335, 3339, 3340, 3344, 3345, 3349, 3350`

ID 3308은 v0.2의 마지막 대사이며, ID 3441부터 아시카가·미요시의 별도 역사 사건이 시작된다.

## 번역·검수 상태

- 114개 모두 `translated` 초벌이며 사람 문체 검수와 런타임 검수가 필요하다.
- SC·JP·EN 같은 ID의 의미를 대조했으며, 공개 근거에는 원문 대신 342개 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 줄바꿈, 앞뒤 공백, 제어문자, PUA, printf 토큰을 114개 모두 보존했다.
- `[bus]`, `[bu]`, `[bum]`, `[bis]`, `[bt]`, `[bk]`, `[cuh]` 같은 게임 고유 자리표시자의 종류와 순서를 별도로 114회 검사했다.
- ESC 코드를 뺀 작성 줄의 최대 길이는 32코드포인트이며, 30자를 넘는 항목은 ID 3358 하나다.
- 지역명, 관백·정이대장군·태정대신, 장군·관백 선하, 후지와라 북가·섭관가, 소부지령, 정무청, 잇키, 공가 사회 용어는 사람 용어집 검수가 필요하다.
- 가변 이름 뒤 조사가 깨지지 않도록 가능한 곳은 `가문`, `공`, `정권`, `시대` 같은 고정 명사를 사이에 두었다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_event_endings_3311_3440.v0.3.json` | `482239403E31932E9FD735C4C6F08228F650147B0A9D523431B5F4D17CBBF1FF` |
| `evidence/alignment_evidence.v0.3.json` | `730FD461C3FD01AAC98DA548F462090261245A001296D8D36FCF57F22E9974F3` |
| `review/review_index.v0.3.json` | `5C834F7C2D130E3AC1A246CFDFC73A7248C3078F122FA7AEB60230AB3E5B7AAD` |
| `validation.v0.3.json` | `2734D895A0D224ECE9BC7BB31DF16BB57534F83BF0219BFF4B046C1EF2710B4B` |

위 네 파일은 A/B 생성과 최종 경로에서 바이트 단위로 같았다. 공개 산출물의 통합 한자 영역 문자와 히라가나·가타카나는 모두 0개다.

## 통합 제한

이번 배치는 번역량 확보를 위한 다음 릴리스 입력이다. 현재 Font-v6와 설치기에는 포함하지 않는다. 실제 배포 전에는 v0.1·v0.2·v0.3 및 장수명 오버레이를 순정 SC 기준으로 병합하고, 새 글리프 수요를 계산한 뒤 후속 글꼴을 만들어야 한다.

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = 'workstreams\dialogue\build_event_dialogue_batch3.py'

foreach ($Out in @(
  'tmp\dialogue_batch3_a',
  'tmp\dialogue_batch3_b',
  'workstreams\dialogue'
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch3 build failed: $Out" }
}

& $Python -B -m unittest 'workstreams\dialogue\tests\test_event_dialogue_batch3.py'
if ($LASTEXITCODE -ne 0) { throw 'dialogue batch3 tests failed' }
```
