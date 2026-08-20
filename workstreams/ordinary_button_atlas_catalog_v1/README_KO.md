# 일반 버튼 아틀라스 위치 감사 v1

## 결론

일반 버튼의 확인된 런타임 텍스처 5개와 배치 **266개 전부**를 좌표화했다.

- 공용 표준 버튼: 20그룹 × 6상태 × 저·고해상도 = 240개
- 공용 전투 `개전`: 7상태 × 저·고해상도 = 14개
- PK 전용 저·고해상도 `전체승인`: 6상태 × 2경로 = 12개
- 합계: 22개 논리 그룹, 266개 배치

산출물은 다음과 같다.

- `ordinary_button_catalog_v1.json`: 경로, 입력 해시, 레이블, 266개 전체 레코드
- `ordinary_button_placements_v1.csv`: 필터 가능한 아트워크·처리·BC 블록 좌표표
- `ORDINARY_BUTTON_POSITIONS_KO.md`: 44개 경로/그룹 행의 사람이 읽는 전체 위치표
- `REWORK_PIPELINE_KO.md`: 휠과 같은 비생성형 원본 레이어 재구축 파이프라인

## 런타임 경로

| 경로 ID | 범위 | 아카이브 | 바깥/중첩 | 리소스/텍스처 | 형식·크기 | 배치 |
|---|---|---|---|---|---|---:|
| `common_low` | 기본판·PK 공용 저해상도 | `RES_JP/res_lang.bin` | `/5` → `/0` | `3856` / `1` | 4096×2048 BC3 | 127 |
| `pk_low_approve_all` | PK 전용 저해상도 `전체승인` | `RES_JP_PK/res_lang_exp_pk.bin` | `/4` → `/0` | `870` / `1` | 2048×512 BC7 | 6 |
| `common_high_standard` | 기본판·PK 공용 고해상도 | `RES_JP_PK_PORT/res_lang_pk_port1.bin` | `/2` → `/0` | `3860` / `1` | 4096×4096 BC3 | 120 |
| `common_high_battle` | 기본판·PK 공용 고해상도 | `RES_JP_PK_PORT/res_lang_pk_port1.bin` | `/2` → `/0` | `3860` / `2` | 4096×2048 BC3 | 7 |
| `pk_high_approve_all` | PK 전용 고해상도 | `RES_JP_PK_PORT/res_lang_pk_port2.bin` | `/2` → `/0` | `870` / `1` | 4096×1024 BC7 | 6 |

PK 저해상도의 표준 버튼은 `RES_JP/res_lang.bin` 공용 아틀라스를 사용한다.
다만 `전체승인`은 예외로 `RES_JP_PK/res_lang_exp_pk.bin`에 192×88
네이티브 셀 6개가 있고, 고해상도 대응은
`RES_JP_PK_PORT/res_lang_pk_port2.bin`의 368×160 셀 6개다.

## 좌표 계약

모든 인덱스는 0부터 시작한다. `state`만 사람이 읽기 쉽게 1부터 시작한다. 사각형은 `[left, top, right, bottom]`이며 오른쪽과 아래쪽은 포함하지 않는다.

- `artwork_rect`: 순정 원본에서 알파 8 이상인 실제 연결요소 경계. BC7 `전체승인`은 교차 언어판으로 검증한 논리 셀이다.
- `processing_rect`: 기존 검증 빌더가 한 상태를 추출·합성한 네이티브 작업 캔버스다.
- `atlas_clip_rect`: `processing_rect`를 실제 아틀라스 경계로 자른 접근 범위다.
- `artwork_bc_block_rect`: 원본 아트워크와 교차하는 4×4 압축 블록 범위다.
- `bc_block_rect`: 실제 변경을 허용할 `atlas_clip_rect`의 4×4 압축 블록 범위다.
- `bc_pixel_rect`: 위 블록 범위를 픽셀 좌표로 환산한 값이다.

저해상도 `개전` 7상태의 264×88 처리 캔버스는 중심 정렬 결과 위쪽이 1~3px 아틀라스 밖으로 나간다. 따라서 논리 `processing_rect`와 실제 `atlas_clip_rect`를 모두 보존했다. 이 7건을 음수 좌표 오류로 고쳐 쓰면 기존 합성 정렬이 달라진다.

## 해상도별 기하 차이

표준 버튼 원본 아트워크는 저해상도 180×79, 고해상도 360×158로 정확히 2배다. 그러나 처리 캔버스는 각각 192×88과 376×168이다.

- 처리 캔버스 배율: 폭 1.9583, 높이 1.9091
- 따라서 저해상도 192×88 결과를 단순 2배 한 384×176으로 고해상도에 넣으면 안 된다.
- 고해상도에서는 순정 360×158 몸체를 그대로 유지하고, 376×168 네이티브 캔버스에서 글자만 별도로 렌더링해야 한다.

`개전`도 단순 2배 계약이 아니다.

- 저해상도: 상태마다 264×88 처리 캔버스
- 고해상도 상태 1: 508×154
- 고해상도 상태 2~7: 493×146

`전체승인`은 저해상도 192×88, 고해상도 368×160 BC7 셀을 각각
네이티브 아틀라스에서 독립 확인했다. 저해상도 좌표는 고해상도 좌표를
절반으로 나누어 만들지 않았다.

## 상태 매핑

고해상도 표준 버튼은 아틀라스의 연속 6개 패킹 순서가 상태 1→6이다. 저해상도는 같은 레이블의 6개가 패킹상 흩어진 사례가 있어 다음 방식으로 복원했다.

1. 알파 연결요소 120개를 검출한다.
2. 레이블별 구성요소 소속을 고정한다.
3. 글자와 아이콘이 닿지 않는 상·하단 배경 띠를 비교한다.
4. 4개 배경 계열과 각 계열 내 반복 순서로 상태 1→6을 확정한다.

이 때문에 저해상도에서는 `component_index`와 `state`가 항상 같은 순서가 아니다. 재작업은 CSV의 상태 매핑을 사용해야 한다.

## 재현

NumPy가 설치된 Python 환경에서 실행한다.

```powershell
python workstreams/ordinary_button_atlas_catalog_v1/build_ordinary_button_atlas_catalog_v1.py `
  --source-root I:\Workspaces\NOBU16-Korean\scratch\release-v0940-approve-all-layered-20260820-01\resource-input\source `
  --target-root I:\Workspaces\NOBU16-Korean\scratch\release-v0940-approve-all-layered-20260820-01\resource-input\target `
  --output workstreams/ordinary_button_atlas_catalog_v1
```

빌더는 순정 4개와 v0.94.0 최종 후보 4개의 크기·SHA-256을 검사하고,
LINK 재구축 동일성, 중첩 슬롯, 리소스 ID, 텍스처 번호, 형식과 크기를
확인한다. 입력 아카이브와 게임 설치는 읽기만 한다.

## 현재 Steam 확인 상태

이번 위치 감사 자체는 리소스를 바꾸지 않는다. 이 문서에 고정한
`전체승인` 최종 후보는 패처 통합과 정적 검증을 마친 뒤에만 Steam에
적용하고, 선택 해상도와 프로세스 완전 재시작 여부를 별도 QA 기록에 남긴다.
