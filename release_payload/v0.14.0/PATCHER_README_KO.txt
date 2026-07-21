NOBU16 PK Steam JP 1.1.7 v0.14.0
순정 Steam JP 직행 통합 패처

실행할 파일은 APPLY_KOREAN_PATCH.bat 하나입니다.
리소스 15개와 정적 EXE 패치를 한 흐름으로 적용합니다. 이전 v0.13.x를 먼저
설치할 필요가 없습니다.

지원 시작 상태
- Steam 신장의 야망·신생 with 파워업키트 일본어판 Update 1.1.7
- Steam/런처 게임 언어: Japanese
- 정확한 순정 JP 리소스 15개와 원본 NOBU16PK.exe

설치 전 필수 — Steam 원본 상태
이 패처는 Steam JP 1.1.7 순정 파일에서만 설치할 수 있습니다. 이전 한글 패치,
모드 또는 수동 파일 수정 이력이 있거나 상태가 확실하지 않다면 Steam 라이브러리에서
NOBU16 → 속성 → 설치된 파일 → 게임 파일 무결성 확인을 실행해 원본 상태로
복구한 뒤 설치하십시오. 일부 파일만 바뀐 설치본에서는 안전을 위해 중단합니다.

설치
1. Steam에서 NOBU16의 게임 언어를 Japanese로 설정합니다.
2. Steam 라이브러리에서 NOBU16 → 속성 → 설치된 파일 → 게임 파일 무결성 확인을
   완료합니다.
3. 게임과 Steam 런처를 완전히 종료합니다.
4. 이 ZIP의 모든 파일을 Steam 게임 폴더 최상위에 풉니다.
   일반적인 경로: ...\SteamLibrary\steamapps\common\NOBU16
5. APPLY_KOREAN_PATCH.bat를 한 번 실행합니다.
6. `패치 완료! Steam에서 게임을 시작하세요.`가 표시되면 평소처럼 Steam에서 게임을 시작합니다.

통합 패처 동작
- 먼저 15개 리소스의 크기·SHA-256과 패키지 델타 5개의 해시를 검사합니다.
- 정적 EXE와 등록 패치 001~010의 상태를 검사한 뒤 EXE를 적용합니다.
- 이어서 텍스트 10개는 고정 레저로 재구성하고, 폰트·이미지 5개는 원본 검증형
  BSDIFF40 델타로 적용합니다.
- 각 단계는 자체 원자 교체와 해시 검증을 사용합니다. 리소스 단계가 실패하면
  이번 실행에서 순정 EXE를 바꾼 경우 EXE도 자동으로 원복합니다.
- 성공 시 EXE와 15개 리소스가 모두 v0.14.0 목표 해시에 도달했는지 다시 검사합니다.

백업 및 복원
- 리소스 원본 15개: KR_PATCH_BACKUP\v0.14.0-direct-patcher
- 통합 작업 기록: KR_PATCH_BACKUP\v0.14.0-unified-patcher\transaction.json
- 원본 EXE: NOBU16PK.exe.staticfix.original_1.1.7
- 전체를 순정 상태로 되돌리려면 게임과 런처를 종료한 뒤
  RESTORE_KOREAN_PATCH.bat를 실행합니다.

주의
- 이전 한글 패치나 다른 모드의 리소스가 남아 있거나, 일부 파일만 바꾼 설치본은
  안전을 위해 적용하지 않습니다.
- 패처가 중단되면 파일을 수동으로 덮어쓰지 말고 Steam 무결성 확인으로 원본 상태를
  복구한 뒤 다시 실행하십시오.
- 완전한 게임 리소스와 NOBU16PK.exe는 ZIP에 포함하지 않습니다.
- ZIP 안의 하위 엔진과 지원 파일을 직접 실행하지 마십시오. 적용·복원은 위 두
  통합 BAT만 사용합니다.
- 패치 후 EXE는 원본 Authenticode 서명이 제거된 NotSigned 파일입니다.
  Steam에서 게임을 시작하십시오.

포함된 Steamless 구성요소는 atom0s의 Steamless v3.1.0.5 원본이며
CC BY-NC-ND 4.0 조건으로 배포합니다. 자세한 고지는
OfficerEditorStaticFix\THIRD_PARTY_NOTICES.txt에 있습니다.
