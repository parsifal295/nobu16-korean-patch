# Steam JP 제목 이미지 후보 시각 QA v1

이 작업은 `steam_jp_title_images_v1`의 후보 `RES_JP/res_lang.bin`을 게임에
복사하지 않고 PC `GT1G0600` / BC3(`0x5B`) 코덱으로 다시 풀어 보는 독립 QA다.
대상은 슬롯 `0, 24, 25, 38, 74, 107`이며, 후보 생성기를 import하지 않고 별도
변환 경로로 기준 캔버스를 재구성한다.

샘플의 의미 매핑은 다음과 같다.

| Steam JP 슬롯 | 기준 소스 | 확인 목적 |
| --- | --- | --- |
| 0 | Switch v1.3 슬롯 3 | 의도적 첫 슬롯 remap |
| 24 | Switch v1.3 슬롯 25 | 상호 remap |
| 25 | Switch v1.3 슬롯 24 | 상호 remap |
| 38 | 수정 PNG — `부대 편성` | 수정 한글 라벨 |
| 74 | 수정 PNG — `공주 정보` | 수정 한글 라벨 |
| 107 | Switch v1.3 슬롯 107 | 범위 마지막 슬롯 |

검사는 다음을 동시에 확인한다.

- candidate의 외부/내부 LINK와 각 샘플의 PC G1T(512×128, `0x5B`, mip 1) 계약
- 독립 재구성 기준과 후보 디코드본의 alpha bbox, visible-mask IoU, BC3 오차
- BC3의 4×4 alpha 양자화에서 생길 수 있는 최대 3px fringe 이동과 분리해, 기준
  잉크에서 그보다 멀리 떨어진 alpha 노이즈·비의도적 캔버스 경계 ink·배치 clip
- 좌측 파란 테두리(독립 기준)와 우측 초록 테두리(후보 디코드)를 2배 픽셀로
  나란히 보여 주는 private contact sheet의 사람 검토

실행 산출물(PNG, contact sheet, 상세 report)은 모두 무시되는 `tmp`에만 쓴다.
Git에는 이 스크립트·테스트·고정 메타데이터만 들어가며, 게임 설치 파일을 쓰지
않는다.

```powershell
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B `
  workstreams\steam_jp_title_images_visual_qa_v1\test_visual_qa_steam_jp_title_images_v1.py

# 먼저 contact sheet를 직접 열어 38=부대 편성, 74=공주 정보를 포함한 여섯 줄을 확인한다.
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B `
  workstreams\steam_jp_title_images_visual_qa_v1\visual_qa_steam_jp_title_images_v1.py qa `
  --manual-review-pass

& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B `
  workstreams\steam_jp_title_images_visual_qa_v1\visual_qa_steam_jp_title_images_v1.py verify
```

`--manual-review-pass`는 자동 OCR 판정이 아니다. private contact sheet를 실제로
열어 본 뒤에만 지정한다. 이 QA는 화면 런타임 위치까지 증명하지 않으므로, 실제
게임 화면 검증은 후보를 별도 조립·적용한 뒤에도 필요하다.

`verify`는 report뿐 아니라 기본 candidate 경로의 현재 SHA-256도 다시 고정값과
대조한다.
