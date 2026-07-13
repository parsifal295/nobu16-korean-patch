# Ghidra Static Analysis Checklist (NOBU16 PK EN)

## 목표

1. 문자열 로더 함수 확정
2. 인코딩 처리 함수 확정(ANSI/UTF-16)
3. 렌더 함수 경로 확정
4. msg*.bin 레코드 구조체/포인터 테이블 확정

## 추천 분석 대상

- `NOBU16PK_EN.exe`
- 보조 비교: `NOBU16PK.exe`, `NOBU16PK_SD.exe`

## 탐색 순서

1. 문자열 기반 XREF
- Ghidra `Search -> For Strings`
- 키워드: `TIPS`, `Shift +`, `1920`, `1080`, `BGM`, `Space`
- 발견 문자열 참조 함수명을 임시로 `str_ref_*`로 명명

2. WinAPI/CRT 호출 역추적
- `MultiByteToWideChar`, `WideCharToMultiByte`
- `CreateFont`, `TextOut`, `DrawText`, DirectX text 관련 import
- 파일 로딩 계열: `CreateFile`, `ReadFile`, `fopen`, `fread`

3. msg 로더 후보 고정
- `msggame.bin`, `msgui.bin`, `msgdata.bin` 경로 문자열 유무 확인
- 없으면 상위 디렉터리 결합 함수(`MSG_PK/EN`)를 찾고 XREF 확장

4. 데이터 구조 정의
- 헤더(엔트리 수, 테이블 오프셋, 문자열 블록 오프셋) 필드 추정
- Ghidra Data Type Manager에 `msg_header_t`, `msg_entry_t` 생성
- 가설 필드마다 근거 주소/함수명을 문서화

## 명명 규칙(권장)

- 함수: `msg_load_*`, `msg_decode_*`, `ui_text_draw_*`
- 전역: `g_msg_table_*`, `g_font_*`
- 구조체: `msg_header_t`, `msg_entry_t`

## 산출물 규칙

- 함수 주소/근거를 `docs/analysis_log.md`에 기록
- 재현 명령은 `logs/`에 남김
- 포맷 확정 전에는 injector 구현 금지(오삽입 위험)
