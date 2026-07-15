# MSGGAME PK UI 우선 B03

`MSG_PK/SC/msggame.bin`의 미등록 목표 중 block 14 정적 도움말·메뉴·전투·관리 UI 220좌표를 번역한 source-free 오버레이입니다.

- Switch v1.3은 동일 좌표의 레코드 이동 때문에 좌표 직접 전사를 사용하지 않았습니다.
- 일본어 한 줄이 정확히 일치하는 경우에만 참고 번역으로 활용하고, PK의 SC/JP/EN/TC 문맥으로 검토했습니다.
- 동적 문장 조각, 이벤트 대사, 언어 중립 제어 표식 7좌표는 제외했습니다.
- 설치 게임 파일에는 쓰지 않으며, 고정 원본에서 오프라인 재구성만 검증합니다.

재생성 및 테스트:

```powershell
python workstreams/msggame_pk_ui_priority_b03/build_msggame_pk_ui_priority_b03.py
python -m unittest workstreams.msggame_pk_ui_priority_b03.tests.test_msggame_pk_ui_priority_b03
```
