# PK 이벤트 6000–7999 manual compact 복원 후보

이 후보는 batch06 strict 한국어 이벤트 파일 하나를 입력으로 사용한다. 한국어 본문은 완료된 6000 및 7000 review artifact의 proposed_ko만 적용한다.

- 6000 review는 batch05 기준이므로 192행 전부가 batch06 strict 입력과 동일한지 행별로 먼저 확인한다.
- proposed_ko가 strict 현재문과 같은 보존 행은 실제 바이너리 diff와 변경행 audit에서 제외한다.
- 실제 변경행은 review 참조, 직접 PC 4언어 원문, 제어 코드, Static Patch 007 줄별 raw/실효 폭, 전각/반각 수, 토큰 예약 폭, 912px 및 4줄 판정을 기록한다.
- 후보 출력은 이 workstream의 tmp 경로에만 생성한다. Steam, Git, 릴리스, 네트워크 작업은 없다.

고정 검증값:

- review 범위 393행(6000 review 192행, 7000 review 201행) 모두가 batch06 strict 입력과 행별로 일치해야 한다.
- 실제 변경은 338행(6000대 191행, 7000대 147행)이며 ID 목록 SHA-256은 `07E14E2342A395494470D520D36872D167A3B76F14FA97AD84543CC52F6F3ADA`다.
- 보존 review 행은 55행이며 ID 목록 SHA-256은 `7B3C7141669C7DD975378791DF347C79FA1ED04812248FA6DB9E1D8E3306674C`다.
- 후보 `MSG_PK/JP/msgev.bin` packed SHA-256은 `D99390D4F2D7D469C105439A11476B01830F5E96287B278C164045CBC7BA3547`, raw SHA-256은 `567C8C3C2F371E27CBE6FFEAB9F8F3EE7F6D6F13A2C179682A5A7F7D3F35780F`로 고정한다.

실행 명령:

    python workstreams/pc_event_manual_compact_static007_6000_7999_restore_v1/build_pc_event_manual_compact_static007_6000_7999_restore_v1.py profile
    python workstreams/pc_event_manual_compact_static007_6000_7999_restore_v1/build_pc_event_manual_compact_static007_6000_7999_restore_v1.py build
    python workstreams/pc_event_manual_compact_static007_6000_7999_restore_v1/build_pc_event_manual_compact_static007_6000_7999_restore_v1.py verify-private
