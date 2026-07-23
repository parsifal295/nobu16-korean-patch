# BASE LOW 화면 제목 통일 후보

확정된 PORT3 HIGH 화면 제목 110개를 BASE LOW의 정확한 대응 슬롯으로 내리는
작업선이다. Steam 설치본이나 배포 파일은 직접 변경하지 않고 후보와 QA 결과를
`tmp` 아래에만 만든다.

- HIGH: `RES_JP_PK_PORT/res_lang_pk_port3.bin`, outer `000`, slot `000~109`, `1024x256`
- LOW: `RES_JP/res_lang.bin`, outer `003`, slot `000~109`, `512x128`
- 대응: 같은 slot 번호끼리 1:1
- 축소: 전체 캔버스를 PArgb 상태에서 고품질 Bicubic으로 정확히 50% 축소
- 압축: Microsoft DirectXTex `texconv may2026`, BC3/DXT5, mip 1개
- 보존: BASE LOW outer `003` 외 모든 outer 항목을 바이트 단위로 보존

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  workstreams\steam_jp_base_low_title_consistency_v1\render_base_low_titles.ps1

python -X utf8 -B `
  workstreams\steam_jp_base_low_title_consistency_v1\build_base_low_title_candidate.py build `
  --base F:\SteamLibrary\steamapps\common\NOBU16\RES_JP\res_lang.bin `
  --render-root tmp\atlas_dashboard\base_low_title_consistency_dimibang_v1 `
  --output-root tmp\base_low_title_consistency_dimibang_full_v1 `
  --texconv tmp\toolchain\directxtex_may2026\texconv.exe

python -X utf8 -B `
  workstreams\steam_jp_base_low_title_consistency_v1\build_base_low_title_candidate.py verify `
  --report tmp\base_low_title_consistency_dimibang_full_v1\build_report.json

python -X utf8 -B `
  workstreams\steam_jp_base_low_title_consistency_v1\build_base_low_title_review_dashboard.py `
  --render-root tmp\atlas_dashboard\base_low_title_consistency_dimibang_v1 `
  --candidate-report tmp\base_low_title_consistency_dimibang_full_v1\build_report.json `
  --output-root tmp\atlas_dashboard\base_low_title_consistency_dimibang_full_v1
```

Steam 적용은 대시보드 승인 뒤 게임이 종료된 상태에서 다음 명령으로 수행한다.
현재 설치본과 후보 해시를 고정 검증하고, `tmp` 아래에 기존 파일을 백업하며,
적용 실패 시 백업본으로 롤백한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  workstreams\steam_jp_base_low_title_consistency_v1\apply_steam_base_low_titles.ps1
```
