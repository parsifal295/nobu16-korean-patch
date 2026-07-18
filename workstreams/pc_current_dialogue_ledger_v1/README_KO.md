# 현재 Steam 인물 대사 좌표 장부 v1

이 workstream은 현재 Steam의 다음 두 리소스를 읽기 전용으로 대조한다.

- `MSG/JP/msggame.bin` — `83C4DF9326DB1487707FDABE9CF2A00380144D14D3AC4A4FCD02513C8E3C279E`
- `MSG_PK/JP/msggame.bin` — `31950B8213AC80C9BCB866163EE7B4B655440ADF863DED21186273E3F8A34BDB` (Wave 7 적용 후)

현재 리터럴 좌표는 Base **24,241개**, PK **29,502개**, 합계 **53,743개**다. 기존 PC 전용 coverage 장부의 53,786개와 비교하면, 과거 정적 문장 재작성에서 한국어 문장에 흡수된 이전 suffix 리터럴 좌표가 Base 21개·PK 22개 있다. 이 43개는 현재 리터럴인 척하지 않고 별도 `retired_prior_literal_coordinates` 산출물에 기록해, 이전 전수 장부와의 대응을 끊지 않는다.

각 현재 리터럴 좌표를 정확히 한 번 기록하고, 기존 PC 전용 coverage 장부의 이전 텍스트 해시와 현재 해시를 비교한다. 이전 장부와 달라진 좌표도 현재 Wave 5/6/7의 전체 파일 프로필 해시와 일치할 때에만 PC 전용 변경 이력이 확인된 것으로 표시한다.

출력에는 게임 문장이나 Switch 자료를 넣지 않는다. 순정 PC 일본어, 현재 Steam 한글, PC EN/SC/TC 파일 해시, 그리고 PC 전용 기존 장부·Wave 5/6/7 감사의 좌표/해시만 사용한다. Steam 설치 파일은 절대 쓰지 않는다.

`known_prior_pc_only_screened_unchanged`와 `known_pc_only_profile_lineage_change`는 각각 기존 정적 PC 검토 이력과 고정된 PC 전용 변경 이력을 뜻할 뿐, 의미 품질이나 실게임 줄바꿈이 완료되었다는 뜻은 아니다. `known_current_context_or_runtime_hold`와 `known_prior_review_carried_forward`는 계속 검토할 좌표다.

실행:

```powershell
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  workstreams\pc_current_dialogue_ledger_v1\build_current_pc_dialogue_ledger_v1.py --write --validate
```

산출물은 `tmp/pc_current_dialogue_ledger_v1/` 아래에만 생성된다. 현재 Wave 7의 12개 감사 레코드를 반영한다. 이 중 7개 레코드는 실제 화면에서 줄바꿈·표시를 확인해야 하는 런타임 시각 QA 보류이며, 해당 16개 리터럴 좌표는 자동 완료로 처리하지 않는다. 나머지 5개 정적 레코드의 실제 변경 리터럴 8개는 Wave 7 정적 수정으로 구분한다. 이후 파일 해시 또는 리터럴 topology가 바뀌면 이 장부는 실패하도록 되어 있으므로, 새 target hash와 좌표 변화를 명시적으로 갱신한 뒤 다시 생성해야 한다.
