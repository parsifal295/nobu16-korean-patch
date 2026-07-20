# PC PK 전략 조언·목표·조략 대응 정적 대사 Wave 90

Wave 90은 Wave 89 private 후보를 유일한 선행 입력으로 사용한다. PK
MSGGAME block 15의 고정 전략 조언·목표 제안·조략 대응 대사 네 행에서,
일본어 terminal static 0143 종결 명령에 의존해 한국어 문장이 미완으로 끝난
부분을 완결한다.

범위는 MSG_PK/JP/msggame.bin의 다음 record뿐이다.

- 15:2421 — 적대 세력의 위협 대응 조언
- 15:2439 — 목표 제안 뒤의 다짐
- 15:2443 — 단기 목표 제안
- 15:2448 — 조략에 대한 보복 선언

각 행은 단일 literal, terminal static 0143, terminator만 가진 고정 인물
대사다. 런타임 014301 슬롯, 다중 literal, standalone 02xx opcode는
범위에서 제외했다. complete 0143 내부 바이트는 standalone opcode로
오인하지 않는다. PK JP와 EN/SC/TC 동좌표 원문 record를 모두 해시 고정해
대조한다.

기존의 문맥상 2·3줄 개행은 그대로 보존한다. 문장 축약·의미 삭제·런타임
인명 슬롯 변경은 하지 않는다. 조언·다짐·제안·보복이라는 원문 의미를 모두
완결된 한국어 문장으로 옮긴다.

이 대상은 이벤트 MSGEV가 아니라 고정 MSGGAME 인물 대사(terminal static
0143) 경로다. 따라서 이벤트용 30px·4줄·912px 규칙은 이식하지 않는다.
원본 G1N 48px/24px advance의 raw 폭을 그대로 사용하며, 최대 세 줄·행당
888px을 기준으로 검사한다. 각 audit 행은 표시 문자열별 원본 G1N 폭·고정
인물 대사 폭·전각/반각 수·줄 수·888px 초과 여부를 기록한다.

선행 입력:

- Base: tmp/pc_dialogue_quality_wave89_pk_transfer_static_v1/candidate/MSG/JP/msggame.bin
- PK: tmp/pc_dialogue_quality_wave89_pk_transfer_static_v1/candidate/MSG_PK/JP/msggame.bin

출력은 아래 private 경로로만 생성한다.

~~~
tmp/pc_dialogue_quality_wave90_pk_counsel_static_v1/candidate/
~~~

실행:

~~~
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v workstreams\pc_dialogue_quality_wave90_pk_counsel_static_v1\test_pc_dialogue_quality_wave90_pk_counsel_static_v1.py
& $py -B workstreams\pc_dialogue_quality_wave90_pk_counsel_static_v1\build_pc_dialogue_quality_wave90_pk_counsel_static_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave90_pk_counsel_static_v1\build_pc_dialogue_quality_wave90_pk_counsel_static_v1.py verify-private
~~~

Steam 적용, Steam transaction, Git stage/commit/push, 네트워크, 릴리즈 기능은
구현하지 않는다.
