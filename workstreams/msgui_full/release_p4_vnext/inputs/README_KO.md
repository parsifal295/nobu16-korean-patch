# v0.3 배포 빌드 입력

이 폴더는 `Build-ReleaseP4VNext.ps1`이 기본으로 사용하는 소스 프리 공개 입력만 보관합니다. 완성된 원본 또는 수정 게임 리소스는 포함하지 않습니다.

- `message/msgui_sc.recipe.json`: 원본 `msgui.bin`에 적용할 3,836개 번역 작업 레시피
- `font/recipe.json`: 원본 `res_lang.bin`의 G1N 엔트리를 재구성하는 레시피
- `font/payload/*.bin`: OFL 글꼴에서 프로젝트가 생성한 글리프 픽셀
- `font/metrics/glyphs.jsonl`: 생성 글리프의 메트릭
- `font/licenses/*`: 사용한 Noto 글꼴의 OFL 라이선스

고정 SHA-256:

- 메시지 레시피: `397EA229DD601EC11C89285BE1ABF3BEC7DA17C7ADE723300B0B37A98B6EB648`
- 폰트 레시피: `6E88317D4A48EF38EDE015E8D61FE48625D8CC2B758B2B2760374021511BC7DE`
- 엔트리 6 픽셀: `96AEB284CA78BB78977F75F5B9944443A61E063BD2132797416921F2A68CECA1`
- 엔트리 7 픽셀: `2811C30E0CBFEA3BBBA895296F7EC4A5FCCBC7E4ADA29C61DFDF222E8FE862D2`
- 글리프 메트릭: `B82DB6950D0AD2DC119AEEFC748EE999E6A3D0B6BD9CA92FA41D3CAAC84966AD`
