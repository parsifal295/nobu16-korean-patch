# PK 이벤트 런타임 토큰 4줄 레이아웃 전수 감사

이 워크스트림은 최신 private 후보 `pc_event_kanto_quality_wave101_v1`의 PK `MSG_PK/JP/msgev.bin`에서 런타임 토큰을 포함한 **1,049행**을 전수 계측하는 읽기 전용 감사다. 이벤트 후보 바이너리, Steam 설치, Git, 네트워크, 릴리스에는 쓰지 않는다.

범위는 숫자 인명 토큰(`[prefix+ID]`) 또는 printf 런타임 토큰을 가진 행이다. 현재 W101 기준으로 인명 숫자 토큰 859행과 printf 토큰 190행은 서로 겹치지 않아 총 1,049행이다.

## 기준

- Static Patch 007 PK 이벤트 대사: 30px, 줄 간격 8, 유효폭 912px, 최대 4줄.
- 원본 G1N 기준 전각 48px / 반각 24px.
- 실효폭: `ceil(raw_g1n_width_px * 30 / 48)`; `<= 912px`가 통과다.
- 인명 토큰은 같은 숫자 ID의 strict 한국어 이름 전체 폭을 예약한다. prefix의 런타임 동작은 추론하지 않으며 모든 예약에 `runtime_proven=false`를 기록한다.
- `%s`/`%d`처럼 행별 실제 값·폭 상한이 증명되지 않은 런타임 값은 폭을 지어내지 않고 hold로 분류한다.
- JP/EN/SC/TC 직접 PC 리소스는 의미와 태그·토큰 구조 확인용 읽기 전용 증거일 뿐이다. 원문의 줄바꿈을 한국어에 이식하지 않는다.

각 행과 줄에는 표시 문자열(hold면 `null`), raw/effective 폭, 전각/반각 수, 4줄 여부, 912px 초과 여부, 인명 예약·hold 사유를 남긴다.

W101은 W100 뒤에 15행을 바꿨고, 그중 3514·3522·3526은 런타임 인명 토큰 행이다. 빌더는 W100과 W101의 런타임 1,049행 범위가 같음을 확인한 뒤, 이 3행을 W101의 새 문안과 같은 ID의 strict 한국어 인명 예약으로 다시 측정한다.

실행:

```powershell
python workstreams/pc_event_runtime_layout_inventory_v1/build_pc_event_runtime_layout_inventory_v1.py build
python workstreams/pc_event_runtime_layout_inventory_v1/build_pc_event_runtime_layout_inventory_v1.py verify
python workstreams/pc_event_runtime_layout_inventory_v1/test_pc_event_runtime_layout_inventory_v1.py
```

생성 보고서:

- `public/pc_event_runtime_layout_inventory.v1.json`: 1,049행 전체 ledger
- `REPORT_KO.md`: 요약
- `validation.v1.json`: 결정적 검증 결과
