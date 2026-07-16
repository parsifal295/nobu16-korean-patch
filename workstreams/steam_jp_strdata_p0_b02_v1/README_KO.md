# Steam JP `strdata` P0-02 (350좌표) 번역 후보

이것은 P0-01과 별개의 스트림이다. 활성 Steam 1.1.7 일본어 경로 `MSG/JP/strdata.bin`의 잔여 감사 계약 중 `p0-MSG_JP_strdata-02` 350좌표만 대상으로 하며, 좌표 SHA-256은 `8083C00E140022FD59D6BDCF3CE100DE6BA96C6070237CB3BFEA9D641C73EC6B`이다.

형식 엔진은 P0-01에서 재사용하지만, 다음은 이 스트림에서 분리되어 고정된다.

- 번들 ID·좌표·원문 해시·한국어 오버레이
- `workstreams/steam_jp_strdata_p0_b02_v1/public/`의 배포 가능한 source-free 카탈로그
- `tmp/steam_jp_strdata_p0_b02_v1/` 아래의 임시 후보·결정성 검증 출력

채택 전에는 활성 Steam JP v6 파일의 packed/raw 해시를 확인하고, 350개 각각이 핀된 공식 JP 백업과 동일한 원문인지 대조한다. 그 뒤에만 Switch v1.3의 대응 한글을 참고한다. 원문 텍스트·완전 게임 리소스는 공개 오버레이에 넣지 않는다.

```powershell
$py='C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py workstreams\steam_jp_strdata_p0_b02_v1\build_steam_jp_strdata_p0_b02_v1.py derive-overlay
& $py workstreams\steam_jp_strdata_p0_b02_v1\build_steam_jp_strdata_p0_b02_v1.py build --output-dir tmp\steam_jp_strdata_p0_b02_v1\candidate
& $py workstreams\steam_jp_strdata_p0_b02_v1\build_steam_jp_strdata_p0_b02_v1.py determinism --output-dir tmp\steam_jp_strdata_p0_b02_v1\determinism
```

게임 설치·릴리즈·GitHub는 이 스트림이 절대 수정하지 않는다. 로고·타이틀·브랜드 아트(`/3`, `/24` 포함)와도 무관하다.
