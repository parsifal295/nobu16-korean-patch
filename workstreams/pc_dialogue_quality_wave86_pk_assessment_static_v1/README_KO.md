# PC PK 성과 예측 정적 대사 Wave 86

Wave 86은 Wave 85 private 후보를 유일한 선행 입력으로 사용한다. PK
MSGGAME block 15의 고정 성과 예측 대사 여덟 행에서, 한국어가 정적 0143
종결 명령 앞에서 끊긴 문제를 고친다.

범위는 MSG_PK/JP/msggame.bin의 다음 record뿐이다.

- 긍정 예측: 15:231, 15:235, 15:239, 15:243
- 보통 예측: 15:232, 15:236, 15:240, 15:244

원문 PK JP와 EN/SC/TC 동좌표를 모두 대조했다. 긍정 예측은 “좋은 성과를
얻을 수 있습니다.”, 보통 예측은 “그럭저럭의 성과는 거둘 수 있습니다.”로
완결한다. 기존 두 줄의 의미 단위 개행을 유지하며, 문장 축약·의미 삭제·런타임
인명 슬롯 변경은 하지 않는다.

각 record는 단일 literal, terminal static 0143, terminator만 가진 고정 대사다.
014301 런타임 슬롯, 02xx opcode, 다중 literal record는 범위에서 제외했다.
Base MSG/JP/msggame.bin은 Wave 85 바이트와 완전히 동일하게 유지한다.

이 대상은 이벤트 msgev가 아니라 고정 MSGGAME 인물 대사(terminal static 0143)
경로다. 따라서 이벤트용 static patch 007의 30px·4줄·912px 규칙은 이식하지
않는다. 원본 G1N 48px/24px advance로 측정한 raw 폭을 그대로 사용하며, 최대
세 줄·행당 888px을 기준으로 검사한다. 각 audit 행은 표시 문자열별 원본 G1N
폭·고정 인물 대사 폭·전각/반각 수·줄 수·888px 초과 여부를 기록한다.

선행 입력:

- Base: tmp/pc_dialogue_quality_wave85_b2_static_completion_v1/candidate/MSG/JP/msggame.bin
- PK: tmp/pc_dialogue_quality_wave85_b2_static_completion_v1/candidate/MSG_PK/JP/msggame.bin

출력은 아래 private 경로로만 생성한다.

~~~
tmp/pc_dialogue_quality_wave86_pk_assessment_static_v1/candidate/
~~~

실행:

~~~
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v workstreams\pc_dialogue_quality_wave86_pk_assessment_static_v1\test_pc_dialogue_quality_wave86_pk_assessment_static_v1.py
& $py -B workstreams\pc_dialogue_quality_wave86_pk_assessment_static_v1\build_pc_dialogue_quality_wave86_pk_assessment_static_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave86_pk_assessment_static_v1\build_pc_dialogue_quality_wave86_pk_assessment_static_v1.py verify-private
~~~

Steam 적용, Steam transaction, Git stage/commit/push, 네트워크, 릴리즈 기능은
구현하지 않는다.
