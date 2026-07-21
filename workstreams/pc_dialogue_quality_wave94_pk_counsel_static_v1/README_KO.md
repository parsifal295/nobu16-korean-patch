# PC 인물 대사 품질 Wave 94 — PK 헌언 static 후보

Wave 94는 **Wave 93 private candidate만** 입력으로 고정한다. Steam 설치본,
Switch 번역본, Git 원격, 릴리스 산출물에는 읽기·쓰기를 하지 않는다.

## 범위

`MSG_PK/JP/msggame.bin` block 15의 고정 인물 대사 네 건만 다룬다.

| 좌표 | 검수 내용 | 새 문안 |
| --- | --- | --- |
| 15:2281 | 본거지·군 개발과 호기 | 본거지 개발도 아직 진행 중이니 / 군 개발을 추진하면서 / 호기를 놓치지 않도록 하십시오. |
| 15:2364 | 상업 장려와 금전 수입 | 각지의 상업을 장려해 / 금전 수입을 늘리면 / 우리 가문의 힘이 될 것입니다. |
| 15:2373 | 적 다이묘의 지략 평가 | 적 다이묘는 뛰어난 지략가이니 / 이번 일은 쉽지 않을 듯합니다. |
| 15:2374 | 목표 영주의 지략 평가 | 목표한 영주는 뛰어난 지략가이니 / 이번 일은 쉽지 않을 듯하옵니다. |

각 행은 동일 좌표의 PC PK 일본어·영어·간체중국어·번체중국어 레코드 SHA-256를
고정해 대조한다. 한 literal, terminal static `0143`, 종료 코드라는 기존 구조를
보존하고 static `0143`만 제거한다. 런타임 `014301`, 여러 literal, 독립 `02xx`는
범위에서 배제한다. 지명·관직·고유명사가 새로 등장하지 않는 대상도 원문 네 언어를
교차 확인해 오독을 허용하지 않는다.

## 레이아웃 기준

이 대상은 이벤트 MSGEV 창이 아니라 고정 MSGGAME 인물 대사다. 따라서 static patch
007의 30px/4줄 규칙을 적용하지 않고, 기존 raw G1N 기준(전각 48px, 반각 24px,
한 줄 888px 이하, 최대 3줄)을 사용한다. 기존 2/3줄 의미 단위를 보존하며 문장을
축약하거나 의미를 삭제하지 않는다.

| 좌표 | raw G1N 줄 폭(px) | 초과 |
| --- | --- | --- |
| 15:2281 | 720 / 480 / 720 | 없음 |
| 15:2364 | 480 / 432 / 696 | 없음 |
| 15:2373 | 696 / 696 | 없음 |
| 15:2374 | 744 / 744 | 없음 |

## 재현

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_dialogue_quality_wave94_pk_counsel_static_v1\build_pc_dialogue_quality_wave94_pk_counsel_static_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave94_pk_counsel_static_v1\build_pc_dialogue_quality_wave94_pk_counsel_static_v1.py verify-private
& $py -B -m unittest -v workstreams\pc_dialogue_quality_wave94_pk_counsel_static_v1\test_pc_dialogue_quality_wave94_pk_counsel_static_v1.py
```

산출물은 `tmp/pc_dialogue_quality_wave94_pk_counsel_static_v1/candidate/`에만 쓴다.
Steam 적용, 커밋, 푸시, 릴리스는 이 작업의 범위가 아니다.
