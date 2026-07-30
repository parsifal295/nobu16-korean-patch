# Steam PC MSGGAME 블록 커버리지 인벤토리 v1

이 문서는 Steam PC의 현재 한국어 `msggame.bin` 두 파일과 순정 Steam PC
일본어 원본을 **읽기 전용**으로 구조 대조한 뒤, 이미 존재하는 PC 전용
감사·후보 workstream이 각 블록을 어느 수준까지 다뤘는지 기록한다. Nintendo
Switch 파일·번역본·폴더는 읽거나 검색하지 않았다.

## 먼저 확인한 사실

- `msggame`의 실제 block ID는 **0–17**이다. Base와 PK 모두 18개 블록이며
  `B18` 좌표는 존재하지 않는다. 따라서 `block 18`이라는 이름만으로는
  감사 범위를 만들 수 없다.
- 현재 Steam 한국어 입력은 Base
  `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB`,
  PK `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092`이다.
- 원문 기준은 Base
  `EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4`,
  PK `31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210`인
  순정 Steam PC 일본어다.
- 구조 수치는 `workstreams/msggame/msggame_format.py`로 현재 Steam 한국어
  파일을 파싱해 얻었다. 모든 블록의 레코드 수는 원문과 일치한다.

여기서 **구조/좌표**는 파서로 레코드·리터럴을 전수 열거했다는 뜻일 뿐이고,
의미·문체·고유명사·수동 줄바꿈 품질을 전수 검토했다는 뜻이 아니다. **선별
후보**도 특정 고신뢰 행만 처리한 것이다. 이 문서에 있는 어떤 블록도
`전수 언어 품질 완료`로 판정하지 않는다.

## 현재 파일 구조

`표시 literal`은 공백만 있는 literal을 제외한 현재 한국어 literal 수다.
block ID는 0-base다.

| 블록 | Base 레코드 / 표시 literal | PK 레코드 / 표시 literal |
| --- | ---: | ---: |
| B00 | 2,612 / 1,388 | 2,729 / 1,451 |
| B01 | 32 / 82 | 32 / 82 |
| B02 | 653 / 846 | 681 / 883 |
| B03 | 24 / 23 | 80 / 81 |
| B04 | 52 / 59 | 155 / 163 |
| B05 | 4 / 0 | 4 / 0 |
| B06 | 4,659 / 6,426 | 4,960 / 7,411 |
| B07 | 2,807 / 3,570 | 2,887 / 3,761 |
| B08 | 1,207 / 1,627 | 1,248 / 1,764 |
| B09 | 3,802 / 3,858 | 4,149 / 4,314 |
| B10 | 9 / 8 | 9 / 8 |
| B11 | 4 / 0 | 4 / 0 |
| B12 | 69 / 143 | 71 / 143 |
| B13 | 517 / 585 | 647 / 725 |
| B14 | 157 / 633 | 247 / 1,034 |
| B15 | 2,423 / 4,360 | 2,601 / 4,888 |
| B16 | 88 / 93 | 88 / 92 |
| B17 | 33 / 64 | 1,159 / 2,238 |

## 블록별 근거와 실제 커버리지 수준

`pc_current_dialogue_ledger_v2`는 과거 Wave 14 상태의 모든 좌표 계보를
기록한 구조 원장이다. 원장 스스로 `semantic_completion: false`를 강제하고,
현재 W45 Steam SHA와도 다르므로 아래 표에서 **현재 번역 품질 근거로 사용하지
않는다**. 표의 workstream은 해당 블록에 대한 직접 PC 근거가 확인된 대표
범위이며, 나열된 후보의 존재가 블록 전체 검토를 뜻하지 않는다.

| 블록 | 확인된 PC 전용 근거 | 가장 높은 확인 수준 | 남아 있는 결론 |
| --- | --- | --- | --- |
| B00 | 현재 구조 파싱, 과거 좌표 원장 | 구조/좌표 | 블록 단위 언어 감사 근거 없음 |
| B01 | `pc_dialogue_quality_wave22_static_inflection_v1`의 선택 행 | 선별 정적 후보 | 전수 언어 품질 미완료 |
| B02 | `pc_dialogue_quality_wave6_v1`, `wave21`, `wave22`의 선택 행 | 선별 정적 후보 | 전수 언어 품질 미완료 |
| B03 | `pc_dialogue_quality_wave11_candidate_v1`의 PK 8행 | 선별 정적 후보 | Base/PK 전수 품질 미완료 |
| B04 | `pc_dialogue_quality_wave51_static_blocks13_14_v1`의 설정 UI 수동 개행 QA 보류 | 구조 + 화면 QA 보류 | 블록 단위 언어 감사 근거 없음 |
| B05 | 현재 구조 파싱(표시 literal 없음) | 구조/좌표 | 번역문은 없지만 제어/빈값 의미는 별도 확인 필요 |
| B06 | `wave4`, `wave7`, `wave9`, `wave10`, `wave14`, `wave22`, `wave37`, `wave39`의 선택 static/runtime 행 | 다수의 선별 후보 | 큰 블록 전체의 언어·줄바꿈 감사 미완료 |
| B07 | `pc_dialogue_quality_wave22_static_inflection_v1`의 선택 행 | 선별 정적 후보 | 전수 언어 품질 미완료 |
| B08 | `pc_dialogue_goodwill_runtime_wave7_v1`, `pc_dialogue_quality_wave23_static_inflection_v1`의 선택 행 | 선별 static/runtime 후보 | 전수 언어 품질 미완료 |
| B09 | `pc_dialogue_quality_wave36_static_crossfile_v1`, `wave39`, `wave50_static_blocks9_12_v1`의 선택 행 | 선별 정적 후보 | 전수 언어 품질 미완료 |
| B10 | 현재 구조 파싱 | 구조/좌표 | 8개 표시 literal의 언어 검토 근거 없음 |
| B11 | 현재 구조 파싱(표시 literal 없음) | 구조/좌표 | 번역문은 없지만 제어/빈값 의미는 별도 확인 필요 |
| B12 | `pc_dialogue_runtime_grammar_wave2_v1`, `pc_dialogue_quality_wave50_static_blocks9_12_v1`의 선택 행 | 선별 정적 후보 | 전수 언어 품질 미완료 |
| B13 | `pc_dialogue_quality_wave1_v1`, `pc_dialogue_runtime_grammar_wave2_v1`, `wave3_static_v1`, `wave6`, `wave51_static_blocks13_14_v1`의 선택 행 | 다수의 선별 static/runtime 후보 | 전수 언어 품질 미완료; LF·UI·런타임 보류 존재 |
| B14 | `pc_dialogue_quality_wave51_static_blocks13_14_v1` 및 Wave 5 잔존 품질 감사의 선택 행 | 선별 정적 후보 | 전수 언어 품질 미완료; UI/의미 보류 존재 |
| B15 | `pc_dialogue_block15_pc_audit_v1`, `pc_block15_runtime_candidate_v1`, `pc_dialogue_quality_wave23_static_inflection_v1` | Base 2,423 + PK 2,601 레코드의 PC JP 대조 감사 | 감사 문서가 명시한 대로 구조·원문 대조 범위이며, 사람의 전수 문학/문체 감사를 뜻하지 않음; 런타임·LF 보류 존재 |
| B16 | `pc_dialogue_block16_pc_audit_v1`, `pc_dialogue_runtime_grammar_wave2_v1`, `wave3_static_v1` | Base/PK 각 88 레코드의 정적 PC JP 대조 | 정적 고확신 오류는 새로 확정되지 않았으나 runtime/UI 보류가 남아 있고 전수 문학 감사 완료 근거는 없음 |
| B17 | `pc_battle_dialogue_static_quality_wave47_v1`, `pc_dialogue_quality_wave35_static_command_v1`, `wave36_static_crossfile_v1`, `pc_dialogue_quality_wave1_v1` | PK에서 65개 선택 행 검토·34개 정적 후보 | PK 1,159 레코드 전체나 Base 33 레코드 전체를 감사했다는 근거는 없음 |

## 확인 가능한 범위 근거

- `pc_dialogue_block15_pc_audit_v1`는 B15 Base 2,423, PK 2,601 레코드를
  순정 PC JP와 대조했다고 기록하지만, 문서 자체가 “완전한 문학적 전수 검토”를
  주장하지 않는다. 정적 안전 후보는 0건이고, 실제 값·화면이 필요한 항목은
  보류했다.
- `pc_dialogue_block16_pc_audit_v1`는 양쪽 88 레코드(표시 literal 87개)를
  확인하고 정적 고확신 오류를 새로 확정하지 않았으며, 명시적 runtime/UI 보류를
  남겼다.
- `pc_battle_dialogue_static_quality_wave47_v1`는 PK B17에서 65개만 검토해
  34개 정적 후보를 만들었고, README도 전수 감사 완료를 주장하지 않는다.
- `pc_dialogue_quality_wave50_static_blocks9_12_v1`은 B09 PK 35개 및
  Base 대응 19개, B12 양쪽 1개를 포함한 56개 레코드만 다룬다.
- `pc_dialogue_quality_wave51_static_blocks13_14_v1`은 B13·B14의 54개
  레코드만 다루며, 문장 재번역·UI 폭·런타임 항목을 명시적으로 보류한다.

## 다음 안전한 감사 범위

우선순위는 **B17 Base+PK 전 범위의 새 PC JP 대조 감사**다. 이유는 PK에
2,238개 표시 literal이 있으나 기존 W47 근거는 65개 선택 행뿐이고, Base B17도
블록 단위 감사 근거가 없기 때문이다. 범위는 다음처럼 고정한다.

1. 순정 Steam PC JP와 현재 Steam KO만 좌표별 대조한다.
2. B17 Base 33개와 PK 1,159개 레코드를 모두 열거하되, static·runtime·수동
   줄바꿈·불투명 제어 코드를 분리한다.
3. 고확신 정적 오류만 후보로 분리하고, runtime/LF/표시 폭 불확실 항목은
   정확한 좌표와 사유를 가진 HOLD로 남긴다.
4. 결과 감사 보고서는 전수 문학 감사 완료라고 선언하지 않는다. 후보 생성,
   Steam 적용, Git 커밋, 푸시는 이 감사와 분리한다.

B17 뒤에는 B00부터 B14까지를 같은 방식으로 블록별 진행해야 한다. 특히 B06·B07·B09는
대량의 표시 literal에 비해 선별 후보만 축적되어 있으므로, 과거 후보 합산으로
전수 검토 완료라고 간주하면 안 된다.

이 인벤토리는 Steam 파일·백업·Git·네트워크·릴리즈를 변경하지 않는다.
