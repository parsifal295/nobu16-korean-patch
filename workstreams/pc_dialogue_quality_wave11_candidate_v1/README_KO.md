# PC 인물 대사 품질 Wave 11 후보

Wave 11은 Steam PC PK msggame의 시나리오 편집 기능 국替 8개를
영지 변경으로 통일하는 비공개 후보입니다. 국가 변경과 국체는 국가 자체를
바꾸는 기능처럼 보이지만, 원문과 PC 영어 설명은 지정 세력의 배치를 바꾸는
기능임을 명시합니다.

## 범위와 근거

- 대상 literal 좌표: 3:57:0, 3:58:0, 3:59:0, 3:60:0, 3:61:0,
  4:148:0, 14:213:1, 14:214:1
- 실제 변경 레코드: 8개, 모두 MSG_PK/JP/msggame.bin 안이다.
- 원문 앵커: pristine Steam PC PK 일본어의 国替
- 영어 앵커: 같은 Steam PC PK 좌표의 Switch Countries
- Nintendo Switch 한국어 파일은 읽거나 참조하지 않는다.

14:213과 14:214에는 기존 ESC 스타일 태그가 있다. 이 후보는 그 태그,
literal marker, 종단 050505를 바이트 단위로 그대로 보존하며, 일본어 활용
런타임 명령 0143은 대상에 존재하지 않음을 확인한다.

## 입력과 표시 계약

- Wave 9 PK 입력 SHA-256:
  209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930
- Wave 11 PK 출력 SHA-256:
  F4605CB25F7AEF97BFC9CB5444249E2420AD0639D44E7B903373C9B8B61D84A5
- 모든 수동 개행은 유지하고, 각 줄의 실제 PC JP 폰트 폭은 입력보다
  넓어지지 않아야 하며 fallback glyph은 허용하지 않는다.
- v0.11.2 글꼴과 현재 별도 UI 이미지/HUD 자산 프로필만 허용하며, 대상
  글리프 advance가 같은지 대조한 뒤 실제 글꼴 폭을 다시 검증한다.

이것은 정적 후보 검증일 뿐 실제 게임 화면 QA를 대체하지 않는다. Steam
적용, 푸시, 릴리즈 기능은 포함하지 않는다.

## 실행

    $py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    & $py -B -m unittest -v workstreams\pc_dialogue_quality_wave11_candidate_v1\test_pc_dialogue_quality_wave11_candidate_v1.py
    & $py -B workstreams\pc_dialogue_quality_wave11_candidate_v1\build_pc_dialogue_quality_wave11_candidate_v1.py build

산출물은 tmp/pc_dialogue_quality_wave11_candidate_v1 아래에만 생성된다.
