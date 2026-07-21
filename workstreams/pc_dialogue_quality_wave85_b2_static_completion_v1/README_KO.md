# PC B2 정적 대사 완결 Wave 85

Wave 85는 Wave 84 private 후보를 유일한 선행 입력으로 사용한다. Base
MSGGAME B2에서 정적 0143 종결 명령만 남아 한국어 문장이 미완성으로 끝난
여섯 행을 고친다.

범위는 Base MSG/JP/msggame.bin의 다음 여섯 record뿐이다.

- 2:315, 2:331, 2:335
- 2:340, 2:343, 2:538

모든 대사는 기존 두 줄의 문맥 개행을 보존한다. 문장 축약·의미 삭제·런타임
인명 슬롯 변경은 하지 않으며, 각 행의 terminal static 0143만 제거하고 완결된
한국어 종결형을 기록한다. PK 후보는 Wave 83부터 바이트 동일 상태를 유지한다.

이 여섯 행은 Base 전용이다. Base SC/TC 동좌표는 빈 record이고, 원본 PK JP에는
정확히 같은 일본어 literal이 없으므로 Base JP 원문을 근거로 검수한다.

줄 폭은 static patch 007 기준으로 기록한다. 원본 G1N 폭은 48px/24px advance로
측정하고, ceil(raw_g1n_width_px × 30 / 48)로 30px 런타임 실효 폭을 산출한다.
각 audit 행은 표시 문자열별 원본 폭·실효 폭·전각/반각 수·줄 수·912px 초과 여부를
포함하며, 최대 네 줄을 허용한다.

선행 입력:

- Base: tmp/pc_dialogue_quality_wave84_b2_static_completion_v1/candidate/MSG/JP/msggame.bin
- PK: tmp/pc_dialogue_quality_wave84_b2_static_completion_v1/candidate/MSG_PK/JP/msggame.bin

출력은 아래 private 경로로만 생성한다.

~~~
tmp/pc_dialogue_quality_wave85_b2_static_completion_v1/candidate/
~~~

실행:

~~~
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v workstreams\pc_dialogue_quality_wave85_b2_static_completion_v1\test_pc_dialogue_quality_wave85_b2_static_completion_v1.py
& $py -B workstreams\pc_dialogue_quality_wave85_b2_static_completion_v1\build_pc_dialogue_quality_wave85_b2_static_completion_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave85_b2_static_completion_v1\build_pc_dialogue_quality_wave85_b2_static_completion_v1.py verify-private
~~~

Steam 적용, Steam transaction, Git stage/commit/push, 네트워크, 릴리즈 기능은
구현하지 않는다.
