# PK 공용 `strdata` 수동 UI B01

PK 실행이 함께 읽는 `MSG/SC/strdata.bin`의 비공백 대상 26,690개를 기준으로,
기존 공개 오버레이 24,425개와 겹치지 않는 잔여 2,265개를 다시 조사했다.
충돌 방지를 위해 블록 0의 슬롯 0~99는 제외했으며, Switch v1.3 직접 이식에서
`manual`로 분류됐던 블록 0·1의 UI·메뉴·라벨·설명 206개를 전부 회수했다.

구성은 UI 자산 라벨 85개, 메뉴·시스템 확인문 42개, 정책 효과·도움말 27개,
이벤트 자막 21개, HUD·상태 도움말 18개, 전투·운영 UI 8개, 시나리오 설명
5개다. PC SC/JP와 Switch v1.3의 동일 좌표를 함께 검토했고, Switch 문자열의
줄바꿈·제어코드·서식 인수가 PC SC와 다른 경우에는 한국어 문장을 수동으로
재배치하거나 다시 번역했다.

공개 오버레이·근거·검토표에는 상용 원문이나 전체 게임 리소스가 없다. 순정 SC
트랜잭션 백업에서만 후보를 만들며 기존 24,425개와 이번 206개, 합계 24,631개
외의 좌표 7,680개가 그대로 유지되는지 재파싱으로 검증한다. 설치본, 전역 진행률,
루트 README, 폰트, 사용자 소유 `workstreams/strdata/`는 읽거나 수정하지 않는다.

```powershell
python -B workstreams\strdata_pk_shared_manual_b01\build_strdata_pk_shared_manual_b01.py
python -B -m unittest discover -s workstreams\strdata_pk_shared_manual_b01\tests -p "test_*.py" -v
```

기본 후보 출력은
`tmp/strdata_pk_shared_manual_b01/candidate/MSG/SC/strdata.bin`이며 실제 게임에는
자동 적용하지 않는다.
