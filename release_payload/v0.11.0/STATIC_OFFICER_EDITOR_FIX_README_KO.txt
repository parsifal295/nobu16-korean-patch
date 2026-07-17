NOBU16 PK Steam JP 1.1.7 v0.11.0
무장 에디트 한글 성명 검증 — 영구 정적 EXE 패치

이 ZIP에는 NOBU16PK.exe가 들어 있지 않습니다. 사용자의 Steam JP 1.1.7
원본 EXE를 PC 안에서 한 번 언팩하고, 검증된 다섯 분기를 수정한 뒤 영구
교체합니다. 설치 뒤에는 매번 실행할 helper나 메모리 패치가 없습니다.

대상
- Steam판 NOBU16 PK 일본어판, Update 1.1.7 (Steam build 18823764)
- 원본 NOBU16PK.exe SHA-256:
  29BC1ED66D27B9AEF5EB6CE3D126BA2BDBF86099E12B09615FE9F988F41E2246

설치
1. 게임 언어를 Japanese로 선택합니다.
2. 게임과 런처를 완전히 종료합니다.
3. 이 ZIP의 모든 파일을 게임 폴더에 풀고, 리소스 덮어쓰기를 허용합니다.
   일반적인 폴더 예: ...\SteamLibrary\steamapps\common\NOBU16
4. 게임 폴더 최상단의 APPLY_STATIC_OFFICER_EDITOR_FIX.bat를 실행합니다.
5. "적용 완료"가 표시되면 평소처럼 Steam -> 런처 -> 게임으로 실행합니다.

설치기는 원본 EXE 해시, Steamless 언팩 결과, 다섯 개 패치 전 바이트와
최종 결과 SHA-256을 모두 확인합니다. 하나라도 맞지 않으면 EXE를 교체하지
않습니다. 성공하면 같은 게임 폴더에 다음 원본 백업을 만듭니다.

  NOBU16PK.exe.staticfix.original_1.1.7

설치 후 최종 EXE SHA-256:
  2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C

원복
- 게임과 런처를 종료한 뒤 RESTORE_ORIGINAL_NOBU16PK_EXE.bat를 실행합니다.
- Steam 파일 무결성 검사나 게임 업데이트도 EXE를 원본으로 되돌릴 수
  있습니다. 이후에는 정확히 같은 1.1.7 원본일 때만 설치기를 다시 실행할
  수 있습니다.

무엇이 바뀌나
- 무장 에디트가 기존 한글 성/이름 및 읽기 필드를 "사용할 수 없는 문자"로
  거부하지 않도록 문자 검사 네 곳을 우회합니다.
- 기존 한글 성명의 합산 6자 제한도 기존 계속 경로로 보냅니다.
- 빈 이름, 열전 문자, 실제 변경 여부 등의 다른 검사는 그대로 남습니다.

제한
- 이것은 기존 한글 리소스 성명을 저장할 수 있게 하는 패치입니다. 한글 IME
  입력이나 새 한글 이름 생성 기능을 추가하지 않습니다.
- 무장 에디트에서는 성명/읽기 필드를 바꾸지 말고 능력치 등 다른 항목만
  수정하는 용도를 권장합니다.
- 최종 EXE는 Steam 보호 래퍼와 원본 Authenticode 서명이 제거된 NotSigned
  파일입니다. 반드시 Steam 또는 1.1.7 런처에서 게임을 시작하십시오.
- Windows의 .NET Framework 4.5.2 이상이 필요합니다.

포함된 Steamless 구성요소는 atom0s의 Steamless v3.1.0.5 원본 그대로이며,
CC BY-NC-ND 4.0 조건으로 배포됩니다. 상세 고지는
OfficerEditorStaticFix\THIRD_PARTY_NOTICES.txt에 있습니다.
