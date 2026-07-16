# Steam JP 시스템 버튼 다음 배치 카탈로그

이 작업물은 Steam 1.1.7 일본어 경로의 `RES_JP/res_lang.bin` 내부 시스템 버튼 아틀라스(`/5/0`, texture 1)를 위한 **좌표 카탈로그만** 담습니다. 후보 리소스, 게임 파일, Switch 원본 이미지·컨테이너·페이로드는 만들거나 저장하지 않습니다.

현재 donor 검증 계약에서는 안전한 PC-native 후보 생성을 승인할 수 없으므로 `candidate_generation_blocked=true`입니다. 이 카탈로그는 확정된 의미·셀 좌표·PC 네이티브 보존 조건만 후속 재구성 경로에 전달합니다.

## 범위

- 기존 `steam_jp_system_buttons_v1`의 8개 라벨(닫기, 중지, 결정, 거부, 뒤로, 아니오, 건너뛰기, 예)은 의도적으로 제외했습니다.
- Switch v2.1→v2.2의 읽기 전용 private 시각 대조로, 신규 12개 라벨 중 11개의 canonical 상태 셀을 확정했습니다.
- `개시`는 장식형 전투 개시 버튼이므로 후보 생성 전 실제 화면과 글리프 대역을 재확인해야 하는 deferred 행입니다.

## 카탈로그 사용법

`catalog.v1.json`의 사각형은 글리프 대역이 아니라 **셀 전체 좌표**입니다. 후속 구현자는 다음을 모두 지켜야 합니다.

1. 확정 행의 같은 상태 canonical 셀만 출발점으로 삼습니다.
2. PC 대상 셀의 한국어 글리프 대역만 새로 그립니다.
3. PC 네이티브 아이콘, 화살표, 장식, 배경은 보존합니다.
4. 같은 라벨의 다른 상태는 자동으로 복제하지 않고 상태별 private atlas와 실제 화면으로 다시 확인합니다.
5. `개시`는 실제 화면 QA가 끝날 때까지 후보에 포함하지 않습니다.

## 검증

```powershell
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B -m unittest `
  KR_PATCH_WORK\workstreams\steam_jp_system_buttons_catalog_v1\test_steam_jp_system_buttons_catalog_v1.py -v
```

테스트는 좌표 범위, core v1 중복 배제, canonical 행의 중복 좌표 금지, deferred 제약, source-free 파일 규칙을 확인합니다.
