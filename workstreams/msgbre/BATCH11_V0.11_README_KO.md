# `msgbre` 장수 열전 Batch 11 v0.11

`MSG_PK/SC/msgbre.bin` ID 791~835의 연속 비공백 장수 열전 45개를 한국어 초벌 번역한 source-free 배치다. v0.10 뒤를 바로 잇고 다음 시작점은 ID 836이다.

SC·JP·EN의 같은 문자열 좌표를 대조하고, SC 제어문자·토큰·줄바꿈 구조를 보존한다. 기존 v0.1~v0.10 공개 오버레이의 해시와 좌표를 고정해 충돌이 없음을 확인한다. 번역 대상은 메모리에서 두 차례 재구성·압축·복원해 동일한 해시가 나오는지 검증하지만, 완성 게임 리소스는 쓰거나 배포하지 않는다.

공개 산출물에는 상용 원문이나 완성 게임 리소스를 포함하지 않는다. 모든 번역은 사람 및 실제 화면 검토 전의 초벌 상태다.

```powershell
python -B workstreams/msgbre/build_msgbre_batch11.py --out-root workstreams/msgbre
python -B -m unittest workstreams.msgbre.tests.test_msgbre_batch11
```
