# Steam JP `strdata` P0-04 (350좌표) 번역 후보

`p0-MSG_JP_strdata-04`의 350좌표만 대상으로 하는 독립 스트림이다. 좌표 SHA-256은 `E676D17E1541F9F6B94887F8C1EF4502F54B3BCE2A0A4F2254FB1491FBD4C510`이며 P0-01~03과 오버랩하지 않는다.

활성 Steam JP v6 파일과 raw 데이터 해시를 게이트하고, 각 원문이 공식 JP 백업과 동일한지 확인한 뒤에만 Switch v1.3 번역 참조를 쓴다. B04 참조본에는 일본식 글머리표·장음 기호, 한자 괄호 표기, 한 좌표의 누락된 끝 공백이 남아 있어 별도 allowlist로만 보정한다.

- 7개 안내문: 일본식 글머리표를 한국어 중점으로 치환
- 2개 비단어 UI 값: 구분선과 한국어 중점만 지정 좌표에서 허용
- 6개 전기/설명: 한자 괄호 표기를 한글 어휘로 정리
- 1개 전기: 활성 원문의 끝 공백을 보존

보정 후 모든 제어 코드·줄바꿈·printf 토큰과 선택 외 31,961개 텍스트 좌표가 보존되어야 한다. 공개 오버레이에는 원문이나 완전 게임 리소스가 없고 후보는 `tmp/steam_jp_strdata_p0_b04_v1/` 밖에 쓸 수 없다.

```powershell
$py='C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py workstreams\steam_jp_strdata_p0_b04_v1\build_steam_jp_strdata_p0_b04_v1.py derive-overlay
& $py workstreams\steam_jp_strdata_p0_b04_v1\build_steam_jp_strdata_p0_b04_v1.py build --output-dir tmp\steam_jp_strdata_p0_b04_v1\candidate
& $py workstreams\steam_jp_strdata_p0_b04_v1\build_steam_jp_strdata_p0_b04_v1.py determinism --output-dir tmp\steam_jp_strdata_p0_b04_v1\determinism
```

게임 설치·릴리즈·GitHub와 로고·타이틀·브랜드 아트(`/3`, `/24` 포함)는 절대 수정하지 않는다.
