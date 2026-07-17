# PC 인물 대사 런타임 문법 보정 2차

Steam PC의 순정 일본어 원문과 현재 한국어만 대조해, 한국어 어간 뒤에 일본어 활용 바이트코드가 붙는 인물 대사를 보정한다. Switch 한국어는 읽거나 번역 근거로 사용하지 않는다.

`01 43 <u32>`는 모두 같은 종결어미가 아니다. 인물·대상 참조도 섞여 있으므로 일괄 삭제하지 않는다.

- 블록 12의 정적 23개는 기존 리터럴/지역 색상 태그를 보존한 채, 좌표별로 검증한 종결 바이트만 제거한다.
- 블록 13·16의 정적 10개는 남는 opaque 바이트가 종료 코드뿐인 것을 확인한 뒤 완결 한국어 한 문장으로 재구성한다.
- Base와 PK는 같은 원문·현재 리터럴을 각각 확인했지만 런타임 operand가 달라, 파일별 레코드 해시와 바이트 오프셋을 별도 고정한다.
- 총 33개 레코드를 Base와 PK에 각각 적용하는 후보(66개 재구성)를 만든다. 동적 인물/가문 참조가 있는 행은 이 작업에서 제외한다.

후보 생성과 적용 전 검증:

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams/pc_dialogue_runtime_grammar_wave2_v1/build_pc_dialogue_runtime_grammar_wave2_v1.py
& $py -B workstreams/pc_dialogue_runtime_grammar_wave2_v1/build_pc_dialogue_runtime_grammar_wave2_v1.py --verify-only
```

적용 뒤 설치본 확인:

```powershell
& $py -B workstreams/pc_dialogue_runtime_grammar_wave2_v1/build_pc_dialogue_runtime_grammar_wave2_v1.py --verify-installed
```

빌더는 적용 전 Steam PC 11파일 해시, 각 레코드 전체 해시, 그리고 제거할 `0143`의 정확한 오프셋·operand를 모두 확인한다. 지정하지 않은 레코드와 opaque 바이트가 달라지면 후보 검증을 거부한다. 적용 뒤에는 두 `msggame` 대상 해시와 66개 재구성 레코드도 다시 확인한다.
