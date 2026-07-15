# `msgbre` 장수 열전 Batch 8 v0.8

`MSG_PK/SC/msgbre.bin` ID 656~700의 연속 비공백 장수 열전 45개를 한국어 초벌 번역한 source-free 배치다. v0.7 뒤를 바로 잇고 다음 시작점은 ID 701이다.

SC·JP·EN 정렬과 SC 형식 불변식을 검증한다. 공개 산출물에는 상용 원문이나 완성 게임 리소스를 포함하지 않는다.

```powershell
python -B workstreams/msgbre/build_msgbre_batch8.py --out-root workstreams/msgbre
python -B -m unittest workstreams.msgbre.tests.test_msgbre_batch8
```
