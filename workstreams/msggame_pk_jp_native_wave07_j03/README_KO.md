# Steam JP msggame wave07 j03

스팀판 1.1.7의 `MSG_PK/JP/msggame.bin` 전용 추가 번역 묶음이다.

- 대상: 블록 6의 j03 좌표 761개
- 번역 상태: 761/761 완료
- 메시지 불변조건: 761/761 통과
- 같은 원문 해시의 번역 일관성: 통과
- 실제 게임 화면 검수: 대기

공개 오버레이에는 좌표, 원문 해시, 한국어 번역만 들어 있다. 게임 원문이나 완성된 게임 리소스는 포함하지 않는다.

재현 명령:

```powershell
python -B workstreams/msggame_pk_jp_native_wave07_j03/build_j03.py build
python -B workstreams/msggame_pk_jp_native_wave07_j03/build_j03.py verify
python -B workstreams/msggame_pk_jp_native_wave07_j03/test_j03.py
```

스팀판 1.1.7 원본 파일이 있으면 테스트가 실제 JP 로더로 761개 항목의 좌표와 원문 해시까지 확인한다. 원본 파일이 없거나 이미 패치된 파일만 있으면 해당 검사만 건너뛴다.
