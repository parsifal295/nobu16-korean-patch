# Steam JP msgui wave07 복구

스팀판 1.1.7의 `MSG_PK/JP/msgui.bin`에서 v1이 보류한 344개 슬롯을 다시 검토한 보충 오버레이다.

- 복구: 343개
- 실제 문자열 변경: 341개
- JP 기능 글리프를 그대로 유지하는 무변경 복구: 2개
- 제외: 1개
- JP 원문 해시 및 형식 불변조건: 343/343 통과
- v1 기반 오버레이와 좌표 중복: 없음
- 실제 게임 화면 검수: 대기

기존 한국어가 SC 슬롯 배열을 전제로 하여 의미가 밀린 구간은 재사용하지 않았다. 스팀판 1.1.7의 고정된 JP 슬롯을 기준으로 JP·EN·SC·TC 문맥을 함께 확인하고, JP의 줄바꿈·서식 인자·색상 코드·기능 글리프·앞뒤 공백에 맞춰 새로 번역했다.

제외한 ID 2657은 JP 슬롯 자체가 공백 한 글자뿐인 비의미 슬롯이다. 한국어를 넣는 것보다 원본 공백을 유지하는 편이 안전하다.

공개 파일에는 슬롯 ID, JP 원문 해시, 한국어 번역과 검증 상태만 들어 있다. 게임 원문이나 완성된 게임 리소스는 포함하지 않는다.

재현 명령:

```powershell
python -B workstreams/steam_jp_msgui_wave07_recovery/build_recovery.py build
python -B workstreams/steam_jp_msgui_wave07_recovery/build_recovery.py verify
python -B workstreams/steam_jp_msgui_wave07_recovery/test_recovery.py
```

빌더는 JP 입력으로 `steam-jp-1.1.7-v0.6.0` 트랜잭션 백업의 원본을 사용한다. 현재 설치된 JP 파일은 입력으로 사용하거나 수정하지 않는다.
