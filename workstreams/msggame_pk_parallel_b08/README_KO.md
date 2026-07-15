# MSGGAME PK 병렬 번역 B08

PK `MSGGAME` 블록 17의 첫 병렬 묶음이다. 공개 오버레이는 한글과 좌표, 원문 확인용 해시만 담으며 상용 원문은 포함하지 않는다.

- 번역 좌표: 625개
- 고유 원문 해시: 383개
- 의미 번역: 594개
- 기호·구조 검토: 31개
- 좌표 해시: `10033A34BA958C0788E3A33DEC9DF0337172A0347F1C4F508E262DE594DEC802`
- 개행·공백·제어 불변식 오류: 0개
- 동일 원문 해시의 번역 불일치: 0개
- 화면 문맥 검토: 아직 필요

공개 산출물은 `public/msggame_ko_msggame_pk_parallel_b08_block17_a_625.v1.json`, 검증 결과는 `validation.v1.json`이다. 재생성은 저장소 루트에서 다음 명령으로 수행한다.

```powershell
python -X utf8 workstreams/msggame_pk_parallel_wave06/build_wave06_batch.py b08
python -X utf8 -m unittest workstreams/msggame_pk_parallel_b08/tests/test_msggame_pk_parallel_b08.py
```
