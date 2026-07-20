# PC 인물 대사 품질 Wave 97 — PK 치안·지역 발전 static 후보

Wave 97은 **Wave 96 private candidate만** 입력으로 고정한다. Steam 설치본,
Switch 번역본, Git 원격, 릴리스 산출물에는 읽기·쓰기를 하지 않는다.

## 범위

MSG_PK/JP/msggame.bin block 08의 고정 치안·지역 발전 인물 대사 네 건만 다룬다.

| 좌표 | 검수 내용 | 새 문안 |
| --- | --- | --- |
| 8:982 | 간자 소탕을 위한 출병 명령 | 필요하다면 간자 놈들을 쫓아내도록 / 출병 명령을 내리십시오. |
| 8:983 | 간자 소탕으로 조략을 미연에 방지 | 병사를 내어 간자를 몰아내면 / 조략을 미연에 막을 수 있습니다. |
| 8:1012 | 땅을 풍요롭게 하려는 미력의 다짐 | 이 땅을 풍요롭게 하기 위해 / 미력하나마 진력하겠습니다. |
| 8:1036 | 안정된 군과 석고 증가의 인과 | 군이 안정되었으니 / 석고도 늘어날 것입니다. |

각 행은 동일 좌표의 PC PK 일본어·영어·간체중국어·번체중국어 레코드 SHA-256를
고정해 대조한다. 한 literal, terminal static 0143, 종료 코드라는 기존 구조를
보존하고 static 0143만 제거한다. 런타임 014301, 여러 literal, 독립 02xx는
범위에서 배제한다.

문장 축약이나 의미 삭제는 하지 않는다. 間者의 게임 내 용어인 간자, 調略의
조략, 郡의 행정 단위 군, 石高의 석고를 유지했다. 특히 간자 소탕과 조략 방지의
원인·결과, 군 안정과 석고 증가의 인과를 모두 보존한다.

## 레이아웃 기준

이 대상은 이벤트 MSGEV 창이 아니라 고정 MSGGAME 인물 대사다. 따라서 static patch
007의 30px/4줄 규칙을 적용하지 않고, 기존 raw G1N 기준(전각 48px, 반각 24px,
한 줄 888px 이하, 최대 3줄)을 사용한다. 기존 2줄의 의미 단위를 보존하며
문장을 축약하거나 의미를 삭제하지 않는다.

| 좌표 | raw G1N 줄 폭(px) | 초과 |
| --- | --- | --- |
| 8:982 | 792 / 552 | 없음 |
| 8:983 | 648 / 744 | 없음 |
| 8:1012 | 624 / 624 | 없음 |
| 8:1036 | 408 / 552 | 없음 |

## 재현

    $py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    & $py -B workstreams\pc_dialogue_quality_wave97_pk_security_development_static_v1\build_pc_dialogue_quality_wave97_pk_security_development_static_v1.py build
    & $py -B workstreams\pc_dialogue_quality_wave97_pk_security_development_static_v1\build_pc_dialogue_quality_wave97_pk_security_development_static_v1.py verify-private
    & $py -B -m unittest -v workstreams\pc_dialogue_quality_wave97_pk_security_development_static_v1\test_pc_dialogue_quality_wave97_pk_security_development_static_v1.py

산출물은 tmp/pc_dialogue_quality_wave97_pk_security_development_static_v1/candidate/에만 쓴다.
Steam 적용, 커밋, 푸시, 릴리스는 이 작업의 범위가 아니다.
