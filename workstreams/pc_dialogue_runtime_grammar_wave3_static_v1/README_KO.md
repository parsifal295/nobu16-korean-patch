# PC 인물 대사 문법 정리 3차 — 정적 레코드

이 작업은 Steam PC판의 현재 한국어 `msggame.bin`을 대상으로 한다. Switch 번역 파일은 읽거나 번역 근거로 사용하지 않는다.

## 범위

- Base `MSG/JP/msggame.bin`: 24개 레코드
- PK `MSG_PK/JP/msggame.bin`: 25개 레코드
- 합계 49개 정적 레코드

대상은 리터럴 바깥 바이트가 정확히 고정된 `01 43 <u32>` 조각과 레코드 종결 바이트뿐인 경우로 한정한다. 각 레코드는 현재 Steam SHA-256, 모든 `01 43` 바이트열, PC JP 순정 원본 SHA-256을 함께 확인한다. 또한 원본의 모든 블록별 레코드 수가 현재 Steam PC 설치본과 정확히 같은지 확인해, 다른 PC 릴리스의 같은 좌표를 번역 근거로 쓰지 못하게 한다.

## 제외

인물명·대상·색상·특성 등 런타임 토큰이 섞인 레코드, 이미 한국어 문장으로 완결된 레코드, 실제 대화창 QA가 필요한 조건부 서식은 이 작업에서 수정하지 않는다. `01 43` 전체 삭제는 하지 않는다.

## 후보 생성과 검증

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B .\build_pc_dialogue_runtime_grammar_wave3_static_v1.py build
& $py -B .\test_pc_dialogue_runtime_grammar_wave3_static_v1.py
```

빌드는 Steam 설치본을 읽기만 하고 `KR_PATCH_WORK\tmp` 아래 후보를 만든다. 출력 해시가 이 소스에 고정된 뒤에만 설치본 상태 검증을 허용한다.

```powershell
& $py -B .\build_pc_dialogue_runtime_grammar_wave3_static_v1.py verify-installed
```

`verify-installed`는 Steam에 실제 적용된 뒤에만 성공해야 한다.
