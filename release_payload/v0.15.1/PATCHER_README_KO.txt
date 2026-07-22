NOBU16 PK Steam JP 1.1.7 v0.15.1
순정 Steam JP 직접 통합 패처

v0.15.1 핫픽스
- v0.15.0에서 PORT3 이미지 아틀라스의 작업 중간본을 순정 원본으로 잘못
  판정해 실제 순정 설치본이 Resource stage Preflight에서 중단되던 문제를 수정했습니다.
- 순정 RES_JP_PK_PORT\res_lang_pk_port3.bin SHA-256
  BE1361E17341D433931EB5740B228EF1842BF6DF2F01D4F582CE790A9A57A154

실행할 파일은 APPLY_KOREAN_PATCH.bat 하나입니다.
기존 v0.14.0의 본문 번역, 새로 검수한 이미지, 보유 중인 DLC의 번역, 정적 EXE 패치를
한 번에 적용합니다. 이전 한국어 패치를 먼저 설치할 필요는 없습니다.

지원 시작 상태
- Steam판 신장의 야망·신생 with 파워업키트 일본어판 Update 1.1.7
- Steam/런처 게임 언어: Japanese
- 필수 순정 JP 리소스 16개와 순정 NOBU16PK.exe
- DLC 파일은 선택 사항입니다. 보유하지 않은 DLC 파일은 오류 없이 건너뜁니다.

설치 전 필수 작업
1. Steam에서 NOBU16의 게임 언어를 Japanese로 설정합니다.
2. Steam 라이브러리에서 NOBU16 → 속성 → 설치된 파일 → 게임 파일 무결성 확인을 완료합니다.
3. 게임과 Steam 런처를 완전히 종료합니다.
4. ZIP의 모든 파일을 Steam 게임 폴더 최상위에 풉니다.
   일반적인 경로: ...\SteamLibrary\steamapps\common\NOBU16
5. APPLY_KOREAN_PATCH.bat를 두 번 클릭합니다.
6. 성 이름 표시 방식을 선택합니다.
   - 1: 세로쓰기. 가로쓰기와 관련 지도 아이콘 이동 패치(004, 005, 006, 008)를 제외합니다.
   - 2: 가로쓰기. 가로 라벨과 관련 지도 아이콘 이동 패치를 모두 적용합니다.

DLC 처리
- 지원하는 DLC 번역 파일은 105개입니다.
- 실제로 설치되어 있는 파일만 순정 해시를 확인한 뒤 번역합니다.
- 없는 DLC 파일은 정상적으로 건너뜁니다.
- 나중에 DLC를 추가 설치했다면 APPLY_KOREAN_PATCH.bat를 다시 실행하십시오.
  이미 적용된 필수 파일은 유지하고 새로 생긴 순정 DLC 파일만 추가 번역합니다.

리소스와 이미지
- 본문 텍스트 리소스 10개는 고정 작업 원장으로 재구성합니다.
- 이미지 아틀라스 6개는 원본 검증형 BSDIFF40 델타로 적용합니다.
- 이번 이미지 갱신 대상은 BASE LOW, PORT1 HIGH, PORT3 HIGH입니다.
- 전체 게임 리소스와 NOBU16PK.exe 원본은 ZIP에 포함하지 않습니다.

성이름 표시 방식 전환
- APPLY_KOREAN_PATCH.bat를 다시 실행하고 1 또는 2를 선택하면 안전하게 전환됩니다.
- 1번 세로쓰기는 001, 002, 003, 007, 009, 010만 적용합니다.
- 2번 가로쓰기는 001~010을 모두 적용합니다.
- 매번 보호된 순정 EXE 백업에서 선택한 프로필을 다시 만들기 때문에 이전 방식의 잔여 패치가 남지 않습니다.

백업과 복원
- 리소스 원본: KR_PATCH_BACKUP\v0.15.1-direct-patcher
- 통합 작업 기록: KR_PATCH_BACKUP\v0.15.1-unified-patcher\transaction.json
- 원본 EXE: NOBU16PK.exe.staticfix.original_1.1.7
- 순정 상태로 되돌리려면 게임과 런처를 종료한 뒤 RESTORE_KOREAN_PATCH.bat를 실행합니다.
- 복원 시에도 현재 없는 DLC 파일은 건너뜁니다.

주의
- 순정 해시가 아닌 파일은 안전을 위해 적용하지 않습니다.
- 설치 중 파일을 수동으로 옮기거나 바꾸지 마십시오.
- ZIP 내부의 하위 엔진 파일은 직접 실행하지 말고 통합 BAT만 사용하십시오.
- 패치된 EXE는 원본 Authenticode 서명이 제거된 NotSigned 파일입니다. Steam에서 게임을 시작하십시오.

포함된 Steamless 구성요소는 atom0s의 Steamless v3.1.0.5 원본이며
CC BY-NC-ND 4.0 조건으로 배포됩니다. 자세한 고지는
OfficerEditorStaticFix\THIRD_PARTY_NOTICES.txt에 있습니다.
