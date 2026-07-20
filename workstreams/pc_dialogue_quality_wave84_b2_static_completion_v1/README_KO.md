# PC B2 정적 대사 완결 Wave 84

Wave 84는 Wave 83 private 후보를 유일한 선행 입력으로 사용한다. Base
MSCGAME B2의 9개 대사에서 한국어가 미완성 어간으로 끝난 문제를 고친다.
각 행은 PC Base/PK 일본어 원문과 PK EN/SC/TC 동좌표를 대조했고, 현재 PK의
동일 원문 번역도 의미 검토용으로 사용했다.

범위는 Base MSG/JP/msggame.bin의 다음 9개 record뿐이다.

- 2:215, 2:220, 2:225, 2:241, 2:484
- 2:485, 2:514, 2:536, 2:550

2:215만 첫 줄이 너무 길어지는 것을 막기 위해, 문장·어휘를 줄이거나 바꾸지
않고 “사람을 쓰는 일에는 제법 / 자신이 있지…… / 부하 지휘는 내게 맡겨라.”의
세 문맥 줄로 재배치한다. 나머지 8개는 기존 두 줄을 유지한다. static 0143
종결 명령만 제거하고 한국어 문장을 원문 의미대로 완결한다. 각 대상에는 runtime
0143 01 00 00 00, 02xx opcode, 인명 슬롯이 없다. PK 후보는 Wave 83 바이트와
완전히 동일하게 유지한다.

줄 폭은 static patch 007 기준으로 기록한다. 원본 G1N 폭은 48px/24px advance로
측정하고, ceil(raw_g1n_width_px × 30 / 48)로 30px 런타임 실효 폭을 산출한다.
각 audit 행은 표시 문자열별 원본 폭·실효 폭·전각/반각 수·줄 수·912px 초과 여부를
포함하며, 최대 네 줄을 허용한다.

선행 입력:

- Base: tmp/pc_dialogue_quality_wave83_difficulty_static_v1/candidate/MSG/JP/msggame.bin
- PK: tmp/pc_dialogue_quality_wave83_difficulty_static_v1/candidate/MSG_PK/JP/msggame.bin

빌더는 이 경로와 Wave 83 audit/manifest의 크기와 SHA-256을 엄격히 검사한다.
출력은 아래 private 경로로만 생성한다.

~~~
tmp/pc_dialogue_quality_wave84_b2_static_completion_v1/candidate/
~~~

실행:

~~~
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v workstreams\pc_dialogue_quality_wave84_b2_static_completion_v1\test_pc_dialogue_quality_wave84_b2_static_completion_v1.py
& $py -B workstreams\pc_dialogue_quality_wave84_b2_static_completion_v1\build_pc_dialogue_quality_wave84_b2_static_completion_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave84_b2_static_completion_v1\build_pc_dialogue_quality_wave84_b2_static_completion_v1.py verify-private
~~~

Steam 적용, Steam transaction, Git stage/commit/push, 네트워크, 릴리즈 기능은
구현하지 않는다.
