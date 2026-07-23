# PORT3 화면 제목 음식디미방체 통일 시안

`res_lang_pk_port3.bin`의 1024x256 화면 제목을 하나의 결정적 렌더링 규칙으로
통일하기 위한 검토 및 후보 제작 단계다. Steam 설치본이나 배포 파일은 변경하지
않으며, PORT3 화면 제목 슬롯 `000~109` 전체를 같은 규칙으로 렌더링한다.

- 기준 폰트: 영양군 음식디미방체 TTF (`Yydimibang Bold`)
- 공통: 4배 렌더 후 1024x256 축소, 고정 기준선, 고정 색상과 외곽선
- 첫 글자: 항상 `136px` 유지
- 나머지 글자: 기본 `112px`, 긴 문구만 `102/92/84px` 고정 단계로 축소
- 첫 글자와 나머지 글자의 잉크 하단을 맞춰 일본어 원본의 머리글자 구성을 재현
- 가로 배치: 블러를 포함한 실제 잉크 시작점을 원본처럼 `x=24px`로 좌측 정렬
- 외곽선: 노란 기를 줄인 중성 아이보리 회색 `RGB(222, 222, 214)`을
  `18px/alpha 52`, `13px/alpha 112`, `8px/alpha 225` 세 층으로 겹쳐
  원본처럼 바깥 가장자리가 부드럽게 퍼지도록 처리
- 신규 번역: `108 목표 무장 선택`, `109 국인중 선택`

문구마다 연속 비율로 확대·축소하지 않는다. 첫 글자 136px, 나머지 112px를
우선 사용하고 920px 안전 폭을 넘을 때만 나머지 글자를 다음 고정 단계로 낮춘다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  workstreams\steam_jp_port3_title_consistency_v1\render_port3_title_ab.ps1
```

승인 렌더를 BC3로 변환하고 PORT3 후보를 만드는 명령은 다음과 같다. texconv는
Microsoft DirectXTex `may2026` 릴리스의 고정 해시 실행 파일만 허용한다.

```powershell
python -X utf8 -B `
  workstreams\steam_jp_port3_title_consistency_v1\build_port3_title_candidate.py build `
  --base tmp\steam_jp_port_imagegen_v1\apply_backup_001\res_lang_pk_port3.bin `
  --render-root tmp\atlas_dashboard\port3_title_consistency_dimibang_v1 `
  --output-root tmp\port3_title_consistency_dimibang_full_v1 `
  --texconv tmp\toolchain\directxtex_may2026\texconv.exe
```

후보 검증 및 실제 BC3 역변환을 포함한 3열 대시보드 생성:

```powershell
python -X utf8 -B `
  workstreams\steam_jp_port3_title_consistency_v1\build_port3_title_candidate.py verify `
  --report tmp\port3_title_consistency_dimibang_full_v1\build_report.json

python -X utf8 -B `
  workstreams\steam_jp_port3_title_consistency_v1\build_port3_title_review_dashboard.py `
  --render-root tmp\atlas_dashboard\port3_title_consistency_dimibang_v1 `
  --candidate-report tmp\port3_title_consistency_dimibang_full_v1\build_report.json `
  --output-root tmp\atlas_dashboard\port3_title_consistency_dimibang_full_v1
```

후보 아카이브는
`tmp/port3_title_consistency_dimibang_full_v1/candidate/RES_JP_PK_PORT/res_lang_pk_port3.bin`에만
생성된다. 배포 또는 Steam 적용은 별도 승인 단계다.

명시적으로 승인된 로컬 Steam 적용은 게임이 종료된 상태에서 다음 스크립트로
수행한다. 현재 설치본과 후보 해시를 고정 검증하고, 기존 PORT3을 `tmp` 아래에
백업한 후 적용한다. 실패하면 백업본으로 롤백한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  workstreams\steam_jp_port3_title_consistency_v1\apply_steam_port3_title_consistency.ps1
```
