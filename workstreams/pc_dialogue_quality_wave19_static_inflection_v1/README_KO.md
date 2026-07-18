# Wave 19: 정적 인물 대사 12건 후보

Wave 19는 검증을 마친 Wave 17의 11파일 private candidate만 입력으로 사용한다. Steam 게임 파일, Git, 릴리즈, Switch 한국어는 건드리지 않으며, 출력은 tmp/pc_dialogue_quality_wave19_static_inflection_v1 아래의 private candidate로만 쓴다.

## 대상과 최종 문장

| 구분 | Base | PK | 최종 한국어 |
| --- | --- | --- | --- |
| 조정 교섭 | 6:4224 | 6:4254 | 조정에 대한 교섭을<br>중단했습니다. |
| 당가 봉사 | 6:4446 | 6:4505 | 당가를 섬긴 지 얼마 안 된 몸이나<br>분골쇄신하여 일에 임하겠습니다. |
| 마을 부흥 | 8:1043 | 8:1055 | 싸움으로 황폐해진 마을의<br>부흥을 지원했습니다.<br>백성들도 무척 감사하고 있습니다. |
| 낭인 등용 | 15:1523 | 15:1538 | 성하의 낭인에게 등용을 권했으나<br>제 힘이 미치지 못하여…<br>성과는 얻지 못했습니다. |
| 계책 결의 | 15:2202 | 15:2232 | 미약한 이 몸의 목숨을 걸고<br>가진 계책을 모두 동원하겠습니다. |

위 다섯 쌍은 Base/PK 합계 10레코드다. 각 레코드를 리터럴과 05 05 05 종결자만으로 완전 재구성하고, 남아 있던 일본어 01 43 활용 명령을 전부 없앤다. 특히 마을 부흥 8:1043/8:1055는 각 레코드의 01 43 세 개를 모두 제거한다.

Wave 17 Base 보정에 대응하는 PK 두 건도 함께 포함한다.

| PK 좌표·리터럴 | 이전 | 수정 | opaque layout |
| --- | --- | --- | --- |
| 2:503, 리터럴 1 | 내리겠다! | 주겠다! | 빈 span, 빈 span, 05 05 05 |
| 2:533, 리터럴 0 | 포위병 마음대로 하게 두지 | 포위병들이 마음대로 하게 두지 | 빈 span 3개, 05 05 05 |

이 두 대응 보정은 01 43 제거 대상이 아니다. 리터럴 마커·opaque layout·종결자를 그대로 보존하며, 실제 PC 일본어 폰트 폭으로 각각 480/624px, 888/528px를 검증한다.

## PC 근거와 고정 검증

각 가족은 순정 PC Base/PK 일본어와 PK EN/SC/TC 레코드를 모두 whole-record SHA-256, 레코드 크기, opaque span, 01 43 명령 상태로 고정한다. Base에는 설치된 EN msggame이 없으므로, 같은 일본어 리터럴을 가진 PK 대응 좌표의 EN/SC/TC로 의미를 확인한다.

빌드가 통과하면 audit.v1.json에 각 대상의 PC JP/EN/SC/TC 전체 리터럴을 기록한다. 따라서 문장 근거와 인코딩된 바이트 상태를 함께 재현할 수 있다. Switch 한국어 또는 과거 한국어 번역본은 읽지 않는다.

정적 10레코드는 다음을 모두 검증한다.

- Wave 17 입력 레코드 SHA-256·크기·opaque span·01 43 명령
- 완전 재구성 후 정확한 target record SHA-256·크기
- 모든 01 43 제거, 리터럴 마커 토폴로지와 05 05 05 종결자 보존
- 수동 줄바꿈 수 보존, 명시 줄 수 최대 3줄, 보수적 폭 상한 최대 912px
- Base와 PK에서 예상한 5개 레코드 외에는 바이트가 바뀌지 않음

PK 대응 2레코드는 whole-record 해시와 실제 폰트 폭까지 별도로 검증하며, 01 43이 원래 없었다는 사실도 고정한다.

## 11파일 프로필

| 파일 | Wave 17 입력 SHA-256 | Wave 19 후보 SHA-256 |
| --- | --- | --- |
| MSG/JP/msggame.bin | C1B39C7344F8A095E179942A26FB4EBDECEAABC2D6A8966A0DB134B7EBE600AC | C00B78165B06A5A9D2BFBE134E847E4B00EC3E5243EE9A1981BA1BB68CFA79C6 |
| MSG_PK/JP/msggame.bin | 9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC | 7D7826A575E4BA80FEE1E4FE920CBD7E16A48F0DA529D06514EDB59B11422FBC |

다른 9파일은 Wave 17 candidate 해시와 바이트 단위로 동일해야 한다. 이 11파일 profile 중 하나라도 달라지면 빌더는 재베이스하지 않고 실패한다.

## 검증과 후보 생성

PowerShell에서 다음을 실행한다.

    $py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    & $py -B workstreams\pc_dialogue_quality_wave19_static_inflection_v1\build_pc_dialogue_quality_wave19_static_inflection_v1.py hash
    & $py -B -m unittest workstreams\pc_dialogue_quality_wave19_static_inflection_v1\test_pc_dialogue_quality_wave19_static_inflection_v1.py
    & $py -B workstreams\pc_dialogue_quality_wave19_static_inflection_v1\build_pc_dialogue_quality_wave19_static_inflection_v1.py build
    & $py -B workstreams\pc_dialogue_quality_wave19_static_inflection_v1\build_pc_dialogue_quality_wave19_static_inflection_v1.py verify-private --candidate-root tmp\pc_dialogue_quality_wave19_static_inflection_v1\candidate

build는 해당 tmp 디렉터리 아래에서만 11파일 후보, audit, manifest를 만든다. Steam 적용·Git 변경·푸시·릴리즈 명령은 이 워크스트림에 존재하지 않는다.
