# Wave 18: 이벤트 정적 라벨 8건 private 후보

이 워크스트림은 현재 Steam PC의 PK 이벤트 문자열에서, 의미 검수로 확정한 정적 라벨 8건만 고친 private 후보를 만든다. 후보는 메모리에서 모든 입력을 검증한 뒤 이 워크스트림 전용 tmp 경로에만 생성된다.

Steam 게임 파일 적용, Steam 트랜잭션, Git 작업, 네트워크 접근, 릴리스 생성 기능은 구현하지 않았다. Switch 한국어와 과거 한국어 번역 산출물도 읽지 않는다.

## 수정 범위

| ID | 현재 | 후보 |
| ---: | --- | --- |
| 11007 | 하하! | 하핫! |
| 14040 | 뎃포덴라이 | 철포전래 |
| 14386 | 야보오츠구모노 | 야망을잇는자 |
| 14391 | 덴쇼진고노란 | 덴쇼진고의난 |
| 14403 | 고마키가쿠테노타타카이 | 고마키나가쿠테전투 |
| 14623 | 야마자키전투아케치승리 | 야마자키 전투·아케치 승리 |
| 14648 | 시대개요덴쇼10년 | 시대 개요(덴쇼 10년) |
| 14651 | 시대개요덴쇼10년 | 시대 개요(덴쇼 10년) |

각 행은 pristine PC JP와 현 PC EN/SC/TC의 동일 ID 원문을 고정한다. 중복 원문이 있는 행은 현재 Steam 한국어의 중복 앵커 ID와 JP/한국어 UTF-16LE SHA-256도 함께 고정한다. 14648·14651은 서로의 원문/현재값을 대칭 중복 앵커로 고정하고, 같은 테이블의 정상 형식 시대 개요 행 14642·14643도 고정한다.

## fail-closed 입력과 출력

| 항목 | SHA-256 |
| --- | --- |
| 현재 Steam PK MSG_PK/JP/msgev.bin | CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3 |
| pristine PC JP MSG_PK/JP/msgev.bin | A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84 |
| PC EN MSG_PK/EN/msgev.bin | BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E |
| PC SC MSG_PK/SC/msgev.bin | 7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA |
| PC TC MSG_PK/TC/msgev.bin | 89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6 |
| 활성 이벤트 글꼴 RES_JP/res_lang.bin | 3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7 |
| 후보 MSG_PK/JP/msgev.bin | D922E7C2B0BD4078A5DB14C87973ECB7BB1A62A4CA2EA30A03A231AB40C1E86B |

현재 Steam 입력은 994,711 bytes이고 후보는 994,727 bytes다. raw 크기와 SHA-256, 메시지 테이블 재구성, LZ4 재압축 표현, 변경 ID 정확히 8개, 모든 원문/중복 앵커도 함께 검증한다. 하나라도 다르면 후보 생성을 중단한다.

## 구조 및 글꼴 폭

8건 모두 수동 줄바꿈, 런타임 대괄호 토큰, printf 토큰, ESC 토큰, 기타 제어문자가 없다. 현재와 후보의 이 구조 서명은 정확히 같아야 한다.

활성 글꼴 기준 현재→후보 한 줄 폭은 다음과 같고, 모두 912px 및 3줄 한도 안이다.

| ID | 현재 폭 | 후보 폭 |
| ---: | ---: | ---: |
| 11007 | 120px | 120px |
| 14040 | 240px | 192px |
| 14386 | 336px | 288px |
| 14391 | 288px | 288px |
| 14403 | 528px | 432px |
| 14623 | 528px | 624px |
| 14648 | 384px | 480px |
| 14651 | 384px | 480px |

## 검증과 private 후보 생성

~~~powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_static_labels_wave18_v1\build_pc_event_static_labels_wave18_v1.py hash
& $py -B -m unittest workstreams\pc_event_static_labels_wave18_v1\test_pc_event_static_labels_wave18_v1.py
& $py -B workstreams\pc_event_static_labels_wave18_v1\build_pc_event_static_labels_wave18_v1.py build
~~~

마지막 명령은 tmp/pc_event_static_labels_wave18_v1/candidate-v1 아래에만 후보 파일, audit.v1.json, candidate_manifest.v1.json을 만든다. 이미 존재하는 후보 디렉터리를 덮어쓰지 않으며, Steam 경로나 tmp 밖 경로는 거부한다.
