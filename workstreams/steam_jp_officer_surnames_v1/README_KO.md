# Steam JP 장수 성씨 980건 복구

Steam PK 1.1.7 일본어 `MSG_PK/JP/msgdata.bin`은 장수 이름을 성씨 조각과
이름 조각으로 합친다. v0.7 후보는 이름 조각은 한국어로 바꿨지만, 결합용 끝
공백이 필요한 성씨 조각을 형식 불일치로 제외했다. 그 결과 `織田` + `노부나가`
처럼 모든 장수의 성씨만 한자로 남았다.

기존 source-free 장수 이름 카탈로그의 성씨 1,050건을 현행 Steam JP 좌표와
다시 대조했다. 다른 지명 번역이 이미 소유한 충돌 좌표 70건은 그대로 보존하고,
누락된 980건만 JP 원문 해시로 고정해 적용한다. 기본 성씨 영역 859건이 모두
포함되며 ID 84 `오다 `와 ID 1266 `노부나가`의 결합 결과는
`오다 노부나가`로 검증한다. 성씨 뒤 ASCII 공백은 이름 결합 구분자이므로
의도적으로 유지한다.

이 복구로 공통 메시지의 형식 계약 대기 1,710건 중 980건이 해소되고 730건이
남는다. SC 게임 파일은 읽지 않으며 완성 바이너리는 저장소에 추적하지 않는다.

```powershell
python workstreams/steam_jp_officer_surnames_v1/build_steam_jp_officer_surnames_v1.py verify
python workstreams/steam_jp_officer_surnames_v1/test_steam_jp_officer_surnames_v1.py
```
