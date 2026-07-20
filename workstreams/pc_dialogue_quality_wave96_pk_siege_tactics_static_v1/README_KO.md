# PC 인물 대사 품질 Wave 96 — PK 공성 전술 static 후보

Wave 96은 **Wave 95 private candidate만** 입력으로 고정한다. Steam 설치본,
Switch 번역본, Git 원격, 릴리스 산출물에는 읽기·쓰기를 하지 않는다.

## 범위

MSG_PK/JP/msggame.bin block 09의 고정 공성 전술 인물 대사 다섯 건만 다룬다.

| 좌표 | 검수 내용 | 새 문안 |
| --- | --- | --- |
| 9:3987 | 퇴로 파괴와 승리의 인과 복원 | 퇴로를 파괴하는 것이야말로 / 승리로 가는 지름길입니다. |
| 9:3989 | 요충지 제압과 지리의 이점 | 요충지를 많이 제압하여 / 지리의 이점을 얻도록 합시다. |
| 9:3990 | 수비 중시의 견실한 전투 방침 | 수비를 중시하여 / 견실하게 싸웁시다. |
| 9:3991 | 좋은 적수와의 싸움을 기다리지 못하는 기대감 | 맞설 만한 적수와 싸울 날을 / 벌써부터 기다릴 수 없군. |
| 9:3992 | 고전하는 아군의 즉시 지원 | 고전 중인 아군이 있으면 / 즉시 지원하겠습니다. |

각 행은 동일 좌표의 PC PK 일본어·영어·간체중국어·번체중국어 레코드 SHA-256를
고정해 대조한다. 한 literal, terminal static 0143, 종료 코드라는 기존 구조를
보존하고 static 0143만 제거한다. 런타임 014301, 여러 literal, 독립 02xx는
범위에서 배제한다.

문장 축약이나 의미 삭제는 하지 않는다. 退き口는 게임 내 용어인 퇴로로,
要所는 요충지로, 地の利는 기존 용어인 지리의 이점으로 유지했다. 良き敵은
맞설 만한 적수로 옮겨, 우수한 상대와 싸우고 싶다는 화자의 기대감을 보존한다.

## 레이아웃 기준

이 대상은 이벤트 MSGEV 창이 아니라 고정 MSGGAME 인물 대사다. 따라서 static patch
007의 30px/4줄 규칙을 적용하지 않고, 기존 raw G1N 기준(전각 48px, 반각 24px,
한 줄 888px 이하, 최대 3줄)을 사용한다. 기존 2줄의 의미 단위를 보존하며
문장을 축약하거나 의미를 삭제하지 않는다.

| 좌표 | raw G1N 줄 폭(px) | 초과 |
| --- | --- | --- |
| 9:3987 | 624 / 600 | 없음 |
| 9:3989 | 528 / 672 | 없음 |
| 9:3990 | 360 / 432 | 없음 |
| 9:3991 | 624 / 576 | 없음 |
| 9:3992 | 552 / 480 | 없음 |

## 재현

    $py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    & $py -B workstreams\pc_dialogue_quality_wave96_pk_siege_tactics_static_v1\build_pc_dialogue_quality_wave96_pk_siege_tactics_static_v1.py build
    & $py -B workstreams\pc_dialogue_quality_wave96_pk_siege_tactics_static_v1\build_pc_dialogue_quality_wave96_pk_siege_tactics_static_v1.py verify-private
    & $py -B -m unittest -v workstreams\pc_dialogue_quality_wave96_pk_siege_tactics_static_v1\test_pc_dialogue_quality_wave96_pk_siege_tactics_static_v1.py

산출물은 tmp/pc_dialogue_quality_wave96_pk_siege_tactics_static_v1/candidate/에만 쓴다.
Steam 적용, 커밋, 푸시, 릴리스는 이 작업의 범위가 아니다.
