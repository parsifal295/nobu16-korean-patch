# Font-v4 전체 MSGUI 폰트 빌드

이 빌더는 설치된 SC `res_lang.bin`을 읽기 전용 입력으로 사용하고, 지정한 빈 출력
디렉터리에만 파일을 만든다. 프로세스 메모리, DLL 주입·후킹, 실행 파일, 레지스트리를
사용하지 않는다.

기본 corpus는 `corpus/msgui_0000_5099/glyph_demand.json`, P3 회귀 fixture는
`regression/p3_226.glyph_demand.json`이다. corpus는 번역 문자열의 비공백 원문자
645개를 기록하면서, G1N 글리프가 아닌 UI 제어·명령 토큰과 PUA 게임 아이콘 19개를
사유와 함께 제외한다. 실제 폰트 수요는 626개다.

```powershell
& $Python KR_PATCH_WORK\workstreams\msgui_full\font_v4\build_font_v4.py `
  --stock-archive RES_SC\res_lang.bin `
  --output-root KR_PATCH_WORK\tmp\font_v4_final
```

출력 디렉터리는 없거나 비어 있어야 한다. `public`에는 OFL 라이선스, 생성 픽셀,
metrics, file-only recipe만 들어가며 `private`의 완성 후보는 배포 금지다.
