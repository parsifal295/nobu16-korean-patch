# MSGGAME PK 병렬 번역 B10

PK `MSGGAME` 블록 17의 세 번째 병렬 번역 묶음이다. 공개 결과물에는 좌표, 원문 확인용 해시, 한국어만 들어 있으며 게임 원문과 완전한 게임 리소스는 포함하지 않는다.

- 번역 좌표: 623개
- 고유 원문 해시: 406개
- 의미 번역: 605개
- 기호·구조 검토: 17개
- 좌표 해시: `1065BE788BFB31BA6DAE65B2C25C68ACB4ACC0129166FC62A609C029BA466941`
- 개행·공백·제어 불변식 오류: 0개
- 같은 원문 해시의 번역 불일치: 0개
- 원문 문자 누출: 0개
- 자연어 표본 검수: 20개 통과
- 실제 화면 문맥 검수: 후속 통합 단계에서 필요

공개 결과물은 `public/msggame_ko_msggame_pk_parallel_b10_block17_c_623.v1.json`, 검증 결과는 `validation.v1.json`, 자연어 표본 검수 기록은 `quality_review.v1.json`이다. 재생성 및 검증 명령은 다음과 같다.

```powershell
python -X utf8 workstreams/msggame_pk_parallel_wave06/build_wave06_batch.py b10
python -X utf8 -m unittest workstreams/msggame_pk_parallel_b10/tests/test_msggame_pk_parallel_b10.py
```
