# `msgbre` 장수 열전 Batch 7 v0.7

`MSG_PK/SC/msgbre.bin` ID 611~655의 연속 비공백 장수 열전 45개를 한국어 초벌 번역한 source-free 배치다. v0.6 다음에서 바로 이어지며, 다음 시작점은 ID 656이다.

SC·JP·EN 의미 대조와 SC 형식 불변식 검사를 적용한다. 공개 산출물에는 원문이나 완성된 게임 리소스를 포함하지 않는다.

```powershell
python -B workstreams/msgbre/build_msgbre_batch7.py --out-root workstreams/msgbre
python -B -m unittest workstreams.msgbre.tests.test_msgbre_batch7
```
