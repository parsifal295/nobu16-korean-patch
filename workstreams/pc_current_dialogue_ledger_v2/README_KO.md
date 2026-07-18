# 현재 Steam PC 인물 대사 원장 v2

이 작업공간은 Wave 14 적용 뒤의 Steam PC `msggame` 두 파일을 읽기 전용으로
대조한다. 목적은 모든 현재 리터럴 좌표의 PC 전용 coverage 계보, Wave 7--14의
현재 레코드 적용 상태, 그리고 명시적 보류 근거를 **원문을 복사하지 않고**
기록하는 것이다.

## 고정된 현재 상태

| 리소스 | 현재 SHA-256 | 리터럴 좌표 |
| --- | --- | ---: |
| `MSG/JP/msggame.bin` | `4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8` | 24,241 |
| `MSG_PK/JP/msggame.bin` | `BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860` | 29,502 |
| 합계 | - | **53,743** |

Wave 14의 11개 Steam 텍스트 파일 프로필 전체도 함께 고정한다. 따라서 두
`msggame` 파일만 맞고 주변 이벤트·NPC 텍스트 파일이 섞인 상태는 통과하지
않는다.

## v1과 다른 점

v1은 Wave 9 시점의 whole-file 해시를 현재성 근거로 사용했다. 후속 Wave가
같은 packed 파일에 정상적으로 합성되므로, 이 방식은 현재 Steam에서 의도적으로
실패한다.

v2는 다음을 분리한다.

- Wave 7--14: audit에 고정된 **대상 레코드 SHA-256**가 현재 Steam 레코드와
  일치하는지 대조한다. 138개 레코드와 266개 변경 리터럴을 모두 fail-closed로
  검증한다.
- 기존 PC-only coverage: 이전 53,786좌표와 현재 53,743좌표를 대조한다. 정적
  재작성으로 retired 된 좌표는 Base 21개와 PK 22개, 총 43개다.
- 기존 보류 근거: 현재 레코드와 여전히 결속되는 597개 리터럴 근거와, 예전
  preimage가 더는 일치하지 않아 재분류가 필요한 31개 레코드를 별도 산출물로
  분리한다.

현재 prior coverage 해시와 같은 리터럴은 52,192개, 다른 리터럴은 1,551개다.
후자 중 Wave 7--14의 검증된 변경은 266개이고, 나머지 1,285개는 이 원장이
자동으로 의미 품질 완료라고 판정하지 않는 기존 프로필 계보다.

## 보류 근거의 의미

`current_explicit_hold_evidence`는 해당 근거가 현재 레코드와 여전히 연결됨을
뜻한다. 특히 Wave 8/9의 `real_game_qa_required_before_release`는 과거 audit의
요구사항이며, 이 source-free 원장만으로 실제 게임 화면 QA의 완료 여부를
추론하지 않는다.

따라서 이 원장은 언제나 다음을 유지한다.

- `semantic_completion: false`
- Switch 한국어와 과거 한국어 번역본을 읽지 않음
- Steam 설치 파일을 쓰지 않음
- 출력에 한국어·일본어 게임 본문을 넣지 않음

## 입력 범위

- 현재 Steam PC JP 파일
- 순정 Steam PC 일본어 Base/PK 원본
- Steam PC EN/SC/TC 컨텍스트 파일
- 기존 PC-only source-free coverage 원장
- Wave 7--14의 PC-only audit 메타데이터

Nintendo Switch 한국어 파일과 과거 한국어 번역본은 허용 입력이 아니다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

& $py -B -m unittest -v `
  workstreams\pc_current_dialogue_ledger_v2\test_pc_current_dialogue_ledger_v2.py

& $py -B workstreams\pc_current_dialogue_ledger_v2\build_current_pc_dialogue_ledger_v2.py `
  --write --validate
```

산출물은 `tmp/pc_current_dialogue_ledger_v2/` 아래에만 생성된다.

- `current_pc_dialogue_coordinate_ledger.source_free.v2.jsonl`
- `retired_prior_literal_coordinates.source_free.v2.jsonl`
- `current_explicit_hold_evidence.source_free.v2.jsonl`
- `stale_legacy_hold_records.source_free.v2.jsonl`
- `summary.source_free.v2.json`

이 빌더에는 Steam 적용, Git 스테이지·커밋·푸시, 릴리즈, 네트워크 기능이 없다.
