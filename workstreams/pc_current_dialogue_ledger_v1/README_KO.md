# 현재 Steam 인물 대사 장부 v1

이 작업물은 현재 Steam PC판의 Base/PK `msggame` 전체 리터럴 좌표를 읽기 전용으로 기록하고, 기존 PC 전용 coverage 장부 및 적용된 수정 Wave와 대조한다. 게임 문장을 복사하지 않고 좌표·해시·분류·검증 근거만 남긴다.

## 현재 기준 프로필

- Base `MSG/JP/msggame.bin`: `7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492`
- PK `MSG_PK/JP/msggame.bin`: `209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930`
- Base 이벤트 `MSG/JP/ev_strdata.bin`: `3A7BE17B7DA97B89BD82DFFF44EBC28DA2D3AA91D2E970A0F6C26DE22C657A22`
- PK 이벤트 `MSG_PK/JP/msgev.bin`: `73DEC80A85B5441AFFFA725DAB72CF02D334D29B297AD08050BC496D532CB8F3`

위 프로필은 Wave 9 적용 상태다. 장부 생성 시에는 두 `msggame` 해시뿐 아니라 Wave 9의 Base·PK 이벤트 해시도 함께 확인하므로, 일부 파일만 섞인 상태를 정상 적용본으로 표기하지 않는다.

## 범위와 현재 상태

- 현재 리터럴: Base 24,241개 + PK 29,502개 = **53,743개**
- 기존 PC 전용 coverage 장부: 53,786개. 과거 정적 문장 수정에서 suffix 리터럴 슬롯이 병합되어 43개는 별도 `retired_prior_literal_coordinates` 산출물로 보존한다.
- Wave 7: 대사 레코드 12개를 현재 해시와 대조한다. 이 중 런타임 표시 확인이 필요한 7개 레코드(16개 리터럴)는 기존 보류로 유지한다.
- Wave 8: 정적 인물 대사 48개 레코드(108개 리터럴)와 오케하자마 PK 이벤트 5항목을 현재 적용 해시와 대조한다. **정적 빌드·적용 검증만 완료되었으며, 48개 대사와 5개 이벤트 모두 실게임 화면 QA 전에는 완료로 처리하지 않는다.**
- Wave 9: PK 인물 대사 33개 레코드(59개 리터럴)와 Base 15개·PK 5개 이벤트를 현재 적용 해시와 대조한다. 긴 런타임 값이 필요한 대사 5개를 포함하며, **33개 대사와 20개 이벤트 모두 실게임 화면 QA 전에는 완료로 처리하지 않는다.**
- 명시적 보류 리터럴은 597개다. 현재 문맥·런타임·용어 보류 430개, Wave 8 실게임 QA 보류 108개, Wave 9 실게임 QA 보류 59개를 구분해 기록한다.

`known_current_wave8_static_repair_pending_real_game_qa`와 `known_current_wave9_static_repair_pending_real_game_qa`는 각각의 Wave로 바뀐 리터럴이 현재 Steam 해시와 일치하지만 실제 화면 검증을 기다리는 상태다. 이 장부의 `semantic_completion`은 항상 `false`이며, 해시·정적 근거가 번역 문맥 품질이나 실제 렌더링 완료를 증명하지는 않는다.

## 출처 제한

PC 일본어 원본, 현재 Steam 한국어, PC EN/SC/TC 해시, 기존 PC 전용 감사 산출물만 사용한다. Switch 한국어와 과거 한국어 번역본은 읽지 않으며 Steam 게임 파일도 쓰지 않는다.

## 실행

```powershell
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B `
  workstreams\pc_current_dialogue_ledger_v1\build_current_pc_dialogue_ledger_v1.py --write --validate
```

산출물은 `tmp/pc_current_dialogue_ledger_v1/` 아래에만 생성된다. 현재 Steam 프로필, Wave 감사 자료, 또는 리터럴 topology가 달라지면 장부 생성이 실패하므로 새 기준 해시와 근거를 명시적으로 갱신한 뒤 다시 생성해야 한다.
