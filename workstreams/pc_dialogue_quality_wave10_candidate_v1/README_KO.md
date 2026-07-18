# PC 인물 대사 품질 Wave 10 후보

Wave 9 비공개 후보의 PK msggame.bin을 입력으로 하는 로컬 후보다. Steam 게임
폴더를 쓰는 기능과 적용, 푸시, 릴리즈 명령은 포함하지 않는다.

## 범위

PK MSG_PK/JP/msggame.bin의 6:1454부터 6:1465까지 12개 레코드만 수정한다.
모두 같은 인물 대사이므로 논리 문장 수정은 1건이다.

현재 일본어 활용 명령 때문에 끊긴 문장을 다음과 같이 완결한다.

    알겠습니다…
    가문을 위한 일이라면, 어쩔 수 없지요.

PC 순정 일본어와 현재 PC Base의 직접 수정본 6:1450부터 6:1461까지를 함께
고정해 검증한다. Switch 한국어 파일은 읽거나 참조하지 않는다.

## 보존 및 표시 계약

- Wave 9 입력 PK 해시:
  209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930
- 대상 외 레코드는 바뀌지 않는다.
- 두 리터럴 슬롯, 마커, 050505 종단은 보존한다.
- 일본어 전용 0143 두 개만 제거한다.
- 실제 PC JP 폰트 entry 6 기준 2줄, 288px와 888px이며 912px 이하를
  강제한다. 누락 글리프와 폴백 폭은 허용하지 않는다.
- 정적 검증은 실제 게임 화면 QA를 대체하지 않는다.

## 실행

    $py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    & $py -B -m unittest -v workstreams\pc_dialogue_quality_wave10_candidate_v1\test_pc_dialogue_quality_wave10_candidate_v1.py
    & $py -B workstreams\pc_dialogue_quality_wave10_candidate_v1\build_pc_dialogue_quality_wave10_candidate_v1.py build

생성물은 tmp/pc_dialogue_quality_wave10_candidate_v1 아래에만 만들어진다.
