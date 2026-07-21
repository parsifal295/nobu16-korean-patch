# PC 인물 대사 품질 Wave 95 — PK 조정·부임 static 후보

Wave 95는 **Wave 94 private candidate만** 입력으로 고정한다. Steam 설치본,
Switch 번역본, Git 원격, 릴리스 산출물에는 읽기·쓰기를 하지 않는다.

## 범위

MSG_PK/JP/msggame.bin block 06의 고정 인물 대사 네 건만 다룬다.

| 좌표 | 검수 내용 | 새 문안 |
| --- | --- | --- |
| 6:4253 | 조정의 후원 확보를 위한 교섭 | 조정의 후원을 얻기 위해 / 빈틈없이 교섭하겠습니다. |
| 6:4441 | 상황에 맞는 대응의 종결 복원 | 그렇군요… / 상황에 맞춰 적절히 처리하겠습니다. |
| 6:4507 | 当家와 手腕의 자연스러운 한국어화 | 오랜 세월 이 가문에서 갈고닦은 역량을 / 마음껏 발휘하겠습니다. |
| 6:4511 | 가까운 영지로의 즉시 부임 가능 | 그곳은 가까운 곳이니 / 당장이라도 부임할 수 있습니다. |

각 행은 동일 좌표의 PC PK 일본어·영어·간체중국어·번체중국어 레코드 SHA-256를
고정해 대조한다. 한 literal, terminal static 0143, 종료 코드라는 기존 구조를
보존하고 static 0143만 제거한다. 런타임 014301, 여러 literal, 독립 02xx는
범위에서 배제한다.

문장 축약이나 의미 삭제는 하지 않는다. 朝廷(조정), 後ろ盾(후원),
抜かりなく働きかけ(빈틈없는 교섭), 適宜良きように対応,
長年当家にて鍛えた手腕, すぐにでも赴任でき의 의미를 각각 유지한 채,
한국어 문장 종결만 완결형으로 바로잡는다.

## 레이아웃 기준

이 대상은 이벤트 MSGEV 창이 아니라 고정 MSGGAME 인물 대사다. 따라서 static patch
007의 30px/4줄 규칙을 적용하지 않고, 기존 raw G1N 기준(전각 48px, 반각 24px,
한 줄 888px 이하, 최대 3줄)을 사용한다. 기존 2줄의 의미 단위를 보존하며
문장을 축약하거나 의미를 삭제하지 않는다.

| 좌표 | raw G1N 줄 폭(px) | 초과 |
| --- | --- | --- |
| 6:4253 | 552 / 576 | 없음 |
| 6:4441 | 240 / 816 | 없음 |
| 6:4507 | 888 / 528 | 없음 |
| 6:4511 | 480 / 720 | 없음 |

## 재현

    $py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    & $py -B workstreams\pc_dialogue_quality_wave95_pk_court_assignment_static_v1\build_pc_dialogue_quality_wave95_pk_court_assignment_static_v1.py build
    & $py -B workstreams\pc_dialogue_quality_wave95_pk_court_assignment_static_v1\build_pc_dialogue_quality_wave95_pk_court_assignment_static_v1.py verify-private
    & $py -B -m unittest -v workstreams\pc_dialogue_quality_wave95_pk_court_assignment_static_v1\test_pc_dialogue_quality_wave95_pk_court_assignment_static_v1.py

산출물은 tmp/pc_dialogue_quality_wave95_pk_court_assignment_static_v1/candidate/에만 쓴다.
Steam 적용, 커밋, 푸시, 릴리스는 이 작업의 범위가 아니다.
