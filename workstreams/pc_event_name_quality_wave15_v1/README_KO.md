# Wave 15: PK 이벤트 인물명 3건 private 후보

이 작업물은 현재 Steam PC의 PK 이벤트 문자열에서 확인된 정적 인물명 3건만
고치는 private 후보 생성기다. 후보 생성은 메모리에서 모든 입력을 검증한 뒤,
이 작업물 전용 tmp 아래에만 결과를 쓴다.

## 대상

| ID | 현재 | 후보 |
| ---: | --- | --- |
| 3015 | 미키 요시요리 | 미츠키 요시요리 |
| 3016 | 미키 요리쓰나 | 미츠키 요리츠나 |
| 3084 | 오토모 지카이에 | 오토모 치카이에 |

각 행은 pristine PC JP 원문과 PC EN 앵커를 모두 고정한다. 행별 JP/EN
앵커 UTF-16LE SHA-256, 현재/후보 한국어 UTF-16LE SHA-256도 빌더에 고정돼
있다.

## fail-closed 입력과 출력

| 입력 또는 출력 | SHA-256 |
| --- | --- |
| 현재 Steam PK MSG_PK/JP/msgev.bin | 3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5 |
| pristine PC JP MSG_PK/JP/msgev.bin | A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84 |
| 현재 PC EN MSG_PK/EN/msgev.bin | BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E |
| 활성 이벤트 글꼴 RES_JP/res_lang.bin | 3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7 |
| 후보 MSG_PK/JP/msgev.bin | CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3 |

현재 Steam PK 파일은 994,707 bytes, 후보는 994,711 bytes다. 입력 파일,
JP/EN 앵커, 현재/후보 텍스트, 활성 폰트 메트릭, 압축 전 raw 해시 또는
후보 출력 해시 중 하나라도 다르면 후보 생성을 중단한다.

Switch 한국어, 기존 한국어 번역 산출물은 읽지 않는다. Steam 게임 파일을
쓰는 코드, Steam 적용 코드, 트랜잭션 생성 코드, Git 커밋 코드, 네트워크
코드는 포함하지 않는다.

## 형식과 레이아웃 불변량

세 항목 모두 다음 값을 현재와 후보 사이에서 동일하게 요구한다.

- 수동 줄바꿈 벡터
- 런타임 대괄호 토큰
- printf 토큰 및 미확인 퍼센트 기호 수
- ESC 색상 토큰과 기타 제어 문자

세 항목은 모두 제어 토큰 없는 한 줄 정적 이름이다. 현재 활성 이벤트 폰트와
912px 한 줄 한도 기준 폭은 다음과 같다.

| ID | 현재 폭 | 후보 폭 |
| ---: | ---: | ---: |
| 3015 | 312px | 360px |
| 3016 | 312px | 360px |
| 3084 | 360px | 360px |

따라서 후보는 모두 1줄이며 3줄/912px 제한 안에 있다.

## 검증과 private 후보 생성

~~~powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_name_quality_wave15_v1\build_pc_event_name_quality_wave15_v1.py hash
& $py -B -m unittest workstreams\pc_event_name_quality_wave15_v1\test_pc_event_name_quality_wave15_v1.py
& $py -B workstreams\pc_event_name_quality_wave15_v1\build_pc_event_name_quality_wave15_v1.py build
~~~

마지막 명령은 tmp/pc_event_name_quality_wave15_v1/candidate-v1 아래에만
후보 파일, audit.v1.json, candidate_manifest.v1.json을 새로 만든다. 이미
존재하는 후보 디렉터리는 덮어쓰지 않으며, tmp 밖 경로는 거부한다.
