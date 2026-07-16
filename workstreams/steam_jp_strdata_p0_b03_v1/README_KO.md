# Steam JP `strdata` P0-03 (350좌표) 번역 후보

이 스트림은 `p0-MSG_JP_strdata-03`의 350좌표만 다룬다. P0-01/P0-02와 좌표·오버레이·후보 출력 경로가 분리되어 있으며, 좌표 SHA-256은 `E93B58820385F38A01F4DD54E6D3EA28B2771E19E05E589BBF56DC469FFC7815`이다.

활성 Steam JP v6 원문과 핀된 공식 JP 백업의 좌표별 동일성을 먼저 확인한 뒤에만 Switch v1.3 한글 참조를 사용한다. 이 묶음에는 Switch 참조의 타이포그래피 문제 세 건이 있어 아래처럼 source-free 한국어 문구로 보정한다.

- 두 UI 수치 문구: 원문의 리터럴 전각 퍼센트를 보존해 printf 뒤의 퍼센트가 서식 토큰으로 오인되지 않게 함
- 시설 비용 문구: 잔존 일본식 중점 대신 한국어 중점 사용

보정 후에도 모든 제어 코드·줄바꿈·printf 토큰은 원문과 일치해야 한다. `public/` 오버레이에는 원문이나 완전한 게임 리소스가 없다. 후보는 `tmp/steam_jp_strdata_p0_b03_v1/` 밖에 생성할 수 없다.

```powershell
$py='C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py workstreams\steam_jp_strdata_p0_b03_v1\build_steam_jp_strdata_p0_b03_v1.py derive-overlay
& $py workstreams\steam_jp_strdata_p0_b03_v1\build_steam_jp_strdata_p0_b03_v1.py build --output-dir tmp\steam_jp_strdata_p0_b03_v1\candidate
& $py workstreams\steam_jp_strdata_p0_b03_v1\build_steam_jp_strdata_p0_b03_v1.py determinism --output-dir tmp\steam_jp_strdata_p0_b03_v1\determinism
```

게임 설치·릴리즈·GitHub와 로고·타이틀·브랜드 아트(`/3`, `/24` 포함)는 이 스트림의 작업 범위가 아니다.
