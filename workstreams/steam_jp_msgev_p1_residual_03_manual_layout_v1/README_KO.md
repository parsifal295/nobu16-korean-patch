# Steam JP v0.9 msgev P1-03 수동 레이아웃 오버레이

이 작업선은 p1-MSG_PK_JP_msgev-03 감사 좌표 중 자동 이식에서 의도적으로 보류한 23개만 다룬다. 공개 산출물에는 한글 텍스트, 해시, 제어 토큰 계약, 고정된 도너 출처만 포함하며, 완전한 게임 리소스는 KR_PATCH_WORK/tmp 아래에서만 재구성한다.

- 고정 기준: Steam JP v0.9 MSG_PK/JP/msgev.bin, packed SHA-256 A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5
- 21개: 이미 검증된 공개 한글 도너의 의미 payload는 그대로 두고, JP 기준의 줄바꿈과 ESC lexeme stream만 수동 배치한다.
- 2개 (10421, 10475): 도너의 ESC 쌍 수가 JP skeleton과 달라 한글 전용 엔티티 템플릿으로 재조립한다. 원문 token profile의 ESC 정확한 순서·개수, 줄바꿈, 대괄호, printf, PUA, 공백·제어 문자는 모두 일치해야 한다.
- 도너는 고정된 기존 공개 한글 catalog와 그 alignment evidence만 사용한다. Switch 같은 인덱스의 텍스트는 읽거나 복사하지 않는다.
- 10837, 10840, 10905의 runtime custom bracket 항목은 선택하지 않으며, 비선택 UTF-16LE payload 보존 검사로 그대로 유지됨을 확인한다.

검증은 항목별 JP source hash, 전체 token profile, parser round-trip, 비선택 payload 보존, raw·packed 결정론적 재구성을 함께 강제한다.

실행 명령:

    & C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_residual_03_manual_layout_v1\build_steam_jp_msgev_p1_residual_03_manual_layout_v1.py freeze
    & C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_residual_03_manual_layout_v1\build_steam_jp_msgev_p1_residual_03_manual_layout_v1.py verify
    & C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_residual_03_manual_layout_v1\build_steam_jp_msgev_p1_residual_03_manual_layout_v1.py build

게임 설치 파일, 실행 파일, 릴리스 자산, GitHub에는 쓰지 않는다.
