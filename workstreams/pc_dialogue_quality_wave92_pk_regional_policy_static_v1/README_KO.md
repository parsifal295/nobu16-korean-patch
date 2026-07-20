# PC 인물 대사 품질 Wave 92 — PK 지역·정책 static 후보

Wave 92는 **Wave 91 private candidate만** 입력으로 고정한다. Steam 설치본,
Switch 번역본, Git 원격, 릴리스 산출물에는 읽기·쓰기를 하지 않는다.

## 범위

`MSG_PK/JP/msggame.bin` block 15의 고정 인물 대사 네 건만 다룬다.

| 좌표 | 검수 내용 | 새 문안 |
| --- | --- | --- |
| 15:1619 | 무사시 장악의 전략적 의의 (`坂東`는 간토 권역) | 무사시는 간토의 중심이며 / 인접국도 많은 땅입니다. / 일대 장악은 타국 진출의 발판입니다. |
| 15:1622 | 오와리·기나이 접근의 전략적 의의 | 오와리는 동국과 서국의 경계에 있고, / 기나이까지 시야에 두는 요충지입니다. / 이 지역을 제압한 의의는 매우 큽니다. |
| 15:1627 | 반슈 및 하리마노카미·이요노카미의 격 (`京`은 교토) | 반슈는 서국과 교토를 잇는 요지입니다. / 하리마노카미와 이요노카미는 / 각국 국사 중 가장 격이 높습니다. |
| 15:1665 | 강적 대응을 위한 성하 시설 증축 제안 | 강적을 이기려면 국력을 키워야 합니다. / 여유 자금이 있다면 / 성하 시설 증축을 제안합니다. |

각 행은 동일 좌표의 PC PK 일본어·영어·간체중국어·번체중국어 레코드 SHA-256를
고정해 대조한다. 한 literal, terminal static `0143`, 종료 코드라는 기존 구조를
보존하고 static `0143`만 제거한다. 런타임 `014301`, 여러 literal, 독립 `02xx`는
범위에서 배제한다.

15:1619의 `坂東`는 일반명사 ‘반도’가 아니라 역사적 간토 권역을 가리키므로,
문안과 검수 근거에서 `간토`로 바로잡았다.

15:1627의 `京`는 교토를 가리킨다. `교토` 표기 후에도 3줄 상한을 지키기 위해
동일한 의미의 `요충지`를 `요지`로 정리했으며, 지명·관직·격의 의미는 삭제하지 않았다.

## 레이아웃 기준

이 대상은 이벤트 MSGEV 창이 아니라 고정 MSGGAME 인물 대사다. 따라서 static patch
007의 30px/4줄 규칙을 적용하지 않고, 기존 raw G1N 기준(전각 48px, 반각 24px,
한 줄 888px 이하, 최대 3줄)을 사용한다. 문장을 축약하거나 의미를 삭제하지 않고,
의미 단위로 수동 개행한다.

| 좌표 | raw G1N 줄 폭(px) | 초과 |
| --- | --- | --- |
| 15:1619 | 576 / 552 / 840 | 없음 |
| 15:1622 | 840 / 864 / 864 | 없음 |
| 15:1627 | 888 / 648 / 768 | 없음 |
| 15:1665 | 888 / 432 / 672 | 없음 |

## 재현

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_dialogue_quality_wave92_pk_regional_policy_static_v1\build_pc_dialogue_quality_wave92_pk_regional_policy_static_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave92_pk_regional_policy_static_v1\build_pc_dialogue_quality_wave92_pk_regional_policy_static_v1.py verify-private
& $py -B -m unittest -v workstreams\pc_dialogue_quality_wave92_pk_regional_policy_static_v1\test_pc_dialogue_quality_wave92_pk_regional_policy_static_v1.py
```

산출물은 `tmp/pc_dialogue_quality_wave92_pk_regional_policy_static_v1/candidate/`에만 쓴다.
Steam 적용, 커밋, 푸시, 릴리스는 이 작업의 범위가 아니다.
