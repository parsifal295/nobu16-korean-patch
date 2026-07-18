# PC 대사 런타임 Wave 9 후보

이 작업 스트림은 Steam 게임 폴더에 쓰지 않는 비공개 후보 빌드다. 입력은
Wave 8 비공개 후보의 고정 해시 11개 리소스이며, Switch 한국어 파일은 읽거나
참조하지 않는다.

변경 대상은 MSG_PK/JP/msggame.bin 하나다.

- 런타임 줄바꿈 및 문맥 정리: 25개 레코드
- 고확신 용어 정리: 8개 레코드
- 총 변경 레코드: 33개

## 고확신 용어 그룹

별도 그룹 high_confidence_gusin_to_geonui는 다음 PK 레코드만 다룬다.

- 6:563, 6:572, 6:1195, 6:1396–6:1399, 6:1472

각 행은 pristine PC 일본어가 具申인 것을 확인하고, PC EN/SC/TC 리소스의
해시와 좌표도 고정해 검증한다. 원칙적으로 구신을 건의로만 바꾼다.
6:1195, 6:1396, 6:1472만 한국어 조사 결합상 필요한 을→를,
이→가 조정을 명시적으로 허용한다. 누구신은 이 그룹과 전체 후보의
명시적 제외어이며, 변경하지 않는다.

## 보존 계약

모든 33개 레코드는 빌드 전에 Wave 8의 레코드 해시, 리터럴 슬롯 수,
opaque span, 리터럴 marker, 05 05 05 종단을 확인한다. 빌드 후에도 다음을
재검증한다.

- opaque 바이트와 런타임 토큰이 완전히 동일함
- 리터럴 marker topology와 종단이 동일함
- 33개 대상 외의 레코드가 바뀌지 않음
- 현재 PC 폰트 RES_JP/res_lang.bin entry 6으로 정적 글리프와 줄 폭을 확인함

감사 파일은 문자열 원문을 넣지 않는 source-free JSON이다. 좌표, 해시,
토폴로지, 글리프, 폭, QA 플래그만 기록한다.

## 실행

    $py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    & $py -m unittest -v workstreams\pc_dialogue_runtime_wave9_candidate_v1\test_pc_dialogue_runtime_wave9_candidate_v1.py
    & $py workstreams\pc_dialogue_runtime_wave9_candidate_v1\build_pc_dialogue_runtime_wave9_candidate_v1.py build

성공 시 아래에만 산출물을 만든다.

- tmp/pc_dialogue_runtime_wave9_candidate_v1/candidate-build-1
- tmp/pc_dialogue_runtime_wave9_candidate_v1/audit_pc_dialogue_runtime_wave9.v1.json
- tmp/pc_dialogue_runtime_wave9_candidate_v1/build_manifest.v1.json

이 작업 스트림에는 Steam 적용 명령이나 apply 스크립트가 없다. 후보 생성은
실게임 적용이나 릴리스 승인이 아니다.

## 실게임 QA 필수 항목

모든 대상은 실제 게임에서 런타임 값으로 확인해야 한다. 특히 긴 런타임 값
검증이 필요한 행은 2:96, 2:97, 2:126, 6:2328, 6:2750이다.
해상도를 바꿨다면 게임 프로세스를 완전히 종료한 뒤 다시 실행하고 검증한다.
