# `msgbre` 장수 열전 Batch 6 v0.6

`MSG_PK/SC/msgbre.bin`의 ID 566~610, 연속 비공백 장수 열전 45개를 한국어 초벌 번역한 source-free 배치다. 앞선 v0.5가 끝난 ID 565 바로 다음부터 시작하며 다음 시작점은 ID 611이다.

이번 배치는 다른 세 번역 스트림과 동시 진행하는 고정 연속 슬라이스다. SC·JP·EN을 의미 대조하고 SC의 서식 불변식(제어문자·개행·공백·placeholder)을 검증한다. 공개 산출물에는 원문이나 완성 리소스를 포함하지 않는다.

재생성과 검증:

```powershell
python -B workstreams/msgbre/build_msgbre_batch6.py --out-root workstreams/msgbre
python -B -m unittest workstreams.msgbre.tests.test_msgbre_batch6
```
