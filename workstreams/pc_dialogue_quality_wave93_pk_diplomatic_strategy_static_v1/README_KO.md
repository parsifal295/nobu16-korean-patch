# PC 인물 대사 품질 Wave 93 — PK 외교·전략 static 후보

Wave 93은 **Wave 92 private candidate만** 입력으로 고정한다. Steam 설치본,
Switch 번역본, Git 원격, 릴리스 산출물에는 읽기·쓰기를 하지 않는다.

## 범위

`MSG_PK/JP/msggame.bin` block 15의 고정 인물 대사 네 건만 다룬다.

| 좌표 | 검수 내용 | 새 문안 |
| --- | --- | --- |
| 15:1850 | 비슷한 규모 세력과의 상호 이익 | 우리 가문과 규모가 크게 다르지 않아 / 서로에게 이로운 관계입니다. |
| 15:1851 | 더 큰 세력에 의지하라는 권고 | 우리 가문보다 규모가 크니 / 마음 놓고 의지하셔도 좋겠습니다. |
| 15:1860 | 공수 양립과 조기 결착 | 공격과 수비의 양립은 몹시 어렵습니다. / 어느 한쪽은 빨리 결판을 내야 합니다. |
| 15:1888 | 전쟁 시기 판단과 힘 비축 | 주변 세력을 보면 싸울 때는 아직 멀고, / 우리 가문은 지금 힘을 쌓아야 합니다. |

각 행은 동일 좌표의 PC PK 일본어·영어·간체중국어·번체중국어 레코드 SHA-256를
고정해 대조한다. 한 literal, terminal static `0143`, 종료 코드라는 기존 구조를
보존하고 static `0143`만 제거한다. 런타임 `014301`, 여러 literal, 독립 `02xx`는
범위에서 배제한다.

이 배치는 역사 지명·관직을 새로 표기하는 대상이 아니다. 그럼에도 일본어 원문과
PC EN·SC·TC를 좌표별로 교차 대조해 지명·관직·고유명사의 오독을 허용하지 않는다.

## 레이아웃 기준

이 대상은 이벤트 MSGEV 창이 아니라 고정 MSGGAME 인물 대사다. 따라서 static patch
007의 30px/4줄 규칙을 적용하지 않고, 기존 raw G1N 기준(전각 48px, 반각 24px,
한 줄 888px 이하, 최대 3줄)을 사용한다. 기존의 두 줄 의미 단위를 보존하며,
문장을 축약하거나 의미를 삭제하지 않는다.

| 좌표 | raw G1N 줄 폭(px) | 초과 |
| --- | --- | --- |
| 15:1850 | 840 / 648 | 없음 |
| 15:1851 | 600 / 768 | 없음 |
| 15:1860 | 888 / 864 | 없음 |
| 15:1888 | 888 / 864 | 없음 |

## 재현

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1\build_pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1\build_pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1.py verify-private
& $py -B -m unittest -v workstreams\pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1\test_pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1.py
```

산출물은 `tmp/pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1/candidate/`에만 쓴다.
Steam 적용, 커밋, 푸시, 릴리스는 이 작업의 범위가 아니다.
