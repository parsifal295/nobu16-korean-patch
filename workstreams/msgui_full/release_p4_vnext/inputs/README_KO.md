# v0.3 배포 빌드 입력

이 폴더는 `Build-ReleaseP4VNext.ps1`이 기본으로 사용하는 소스 프리 공개 입력만 보관합니다. 완성된 원본 또는 수정 게임 리소스는 포함하지 않습니다.

- `message/msgui_sc.recipe.json`: 원본 `msgui.bin`에 적용할 3,819개 번역 작업 레시피
- `font/recipe.json`: 원본 `res_lang.bin`의 G1N 엔트리를 재구성하는 레시피
- `font/payload/*.bin`: OFL 글꼴에서 프로젝트가 생성한 글리프 픽셀
- `font/metrics/glyphs.jsonl`: 생성 글리프의 메트릭
- `font/licenses/*`: 사용한 Noto 글꼴의 OFL 라이선스

고정 SHA-256:

- 메시지 레시피: `3F5CAC974C95B19B78319DBF97C2289FFF82B4ED23A4950013DB94C19A6948AB`
- 폰트 레시피: `561477D6312FF02DDD18C09CBF4A2802E00BFA42015B325CFE6F04BDED04C109`
- 엔트리 6 픽셀: `53898FD6039F8CAD63BC85D50791DD3451D9EDCB69EB6F15EE08550EF50A91ED`
- 엔트리 7 픽셀: `CD34058F3C85554900314394AB3C1CFD92DF6CA7007068F44F2D12968DCA168D`
- 글리프 메트릭: `1AF2EF974E0E6E3670F2FF3AAC127C28717128C86573DF759EBCFF73C01A9074`
