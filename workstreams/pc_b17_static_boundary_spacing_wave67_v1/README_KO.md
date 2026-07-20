# PC 원문 기반 W67: PK B17 정적 경계·조사 보정

W67은 W66 사설 후보와 순정 Steam PC 일본어만 읽어 PK `msggame.bin` B17의
정적 literal **20개 / 레코드 19개**를 보정한다. Switch 자료, Steam 게임 파일,
폰트, Git, 네트워크, 공개 릴리즈는 건드리지 않는다.

## 포함 범위

- 정적 인명·관직명·가문명·수량 앞의 누락 공백을 복원한다.
- `모리 가문는`은 앞 정적 literal의 받침을 기준으로 `모리 가문은`으로 고친다.
- 수동 줄바꿈 수와 literal 제어 바이트는 모든 대상에서 유지한다.
- 완성된 레코드의 각 줄은 실제 활성 글꼴 기준 최대 `912px` 이하로 고정한다.

`17:520`의 `그사콘님`은 같은 종류의 누락 공백이지만, 이미 둘째 줄이
`1032px`여서 이번 정적 묶음에는 넣지 않았다. 이는 별도 표시·줄바꿈 QA 보류다.

## 재현과 검증

후보 산출물은 `tmp/pc_b17_static_boundary_spacing_wave67_v1/candidate-final/`
아래에만 생성된다. Steam 적용 명령은 제공하지 않는다.

```powershell
python -B -X utf8 workstreams\pc_b17_static_boundary_spacing_wave67_v1\build_pc_b17_static_boundary_spacing_wave67_v1.py profile
# profile 결과를 EXPECTED_FINAL_* 상수에 먼저 고정한다.
python -B -X utf8 workstreams\pc_b17_static_boundary_spacing_wave67_v1\test_pc_b17_static_boundary_spacing_wave67_v1.py
python -B -X utf8 workstreams\pc_b17_static_boundary_spacing_wave67_v1\build_pc_b17_static_boundary_spacing_wave67_v1.py build
python -B -X utf8 workstreams\pc_b17_static_boundary_spacing_wave67_v1\build_pc_b17_static_boundary_spacing_wave67_v1.py diff-check
```
