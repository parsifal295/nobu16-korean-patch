# PC 인물 대사·표기 품질 보정 1차

현재 Steam PC 한글 파일과 순정 PC 일본어 원문을 대조해 확정한 1차 보정이다. Switch 파일은 읽거나 근거로 사용하지 않는다.

- `고쇼`·`소성`의 일반 `小姓` 표기를 `시동`으로, `小姓頭`를 `시동장`으로 바로잡는다.
- 사용자 보고 대사 `당가는 아직 힘이 부족하오`와 `일이를 다투는`을 자연스러운 한국어로 고친다.
- 오케하자마 전투 대사의 일본식 쉼표·붙어쓴 문장과 PK 동적 인명 나열의 `、`를 한국식 표기로 바꾼다.
- 모든 `msggame` 변경은 리터럴 한 칸만 바꾸며, 런타임 이름·조사 바이트코드와 ESC 색상 태그를 보존한다.
- 11개 텍스트 파일 프로필을 모두 만들되 실제 변경은 8개 파일로 제한한다.
- `01 43` 런타임 종결어미 바이트코드가 있는 인물 대사는 이 1차 수정에서 건드리지 않는다. 해당 항목은 바이트코드 해석·재구성 검증 후 별도 작업으로 처리한다.

실행:

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams/pc_dialogue_quality_wave1_v1/build_pc_dialogue_quality_wave1_v1.py
& $py -B workstreams/pc_dialogue_quality_wave1_v1/build_pc_dialogue_quality_wave1_v1.py --verify-only
```

적용 뒤 설치본 확인:

```powershell
& $py -B workstreams/pc_dialogue_quality_wave1_v1/build_pc_dialogue_quality_wave1_v1.py --verify-installed
```

빌더는 적용 전 기준 설치본의 11개 SHA-256을 먼저 확인한다. 다른 설치 상태에서는 후보를 만들지 않는다. `--verify-installed`는 적용 뒤의 11개 파일 SHA-256과 모든 수정 좌표를 다시 확인한다.
