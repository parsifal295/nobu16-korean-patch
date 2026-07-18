# Wave 50 — 블록 9·12 정적 대사 품질 비공개 후보

이 작업물은 Steam PC `msggame.bin`의 검토 완료된 정적 대사만 후보로
만듭니다. 번역 판단은 pristine Steam-PC 일본어 원문을 기준으로 했고,
PC EN/SC/TC는 검토 문맥으로만 사용했습니다. Switch 한국어는 읽거나
참조하지 않습니다.

- PK 블록 9의 고신뢰 정적 수정: 35개
- Base에는 현재 한국어·PC 일본어 원문·literal marker·opaque 바이트가
  PK 대상과 **완전히 동일한** 19개 대응 레코드만 포함
- block 12:51은 Base/PK 각 1개를 포함하며, 강조된 `고신` literal과
  style marker를 그대로 보존
- 합계 56개: Base 20개, PK 36개

모든 대상은 `02xx` 런타임 슬롯과 `0143` 명령이 없는 레코드입니다.
literal marker, opaque 바이트, 수동 줄바꿈 수, 레코드 종료 코드가
바뀌지 않으며, 활성 폰트 기준으로 3줄·줄당 912px 이내와 fallback
glyph 없음까지 확인합니다.

`9:2135`와 같은 Base 대응 `9:2061`은 초안의 `무턱대고`에 포함된
`턱` 글리프가 활성 폰트에 없어, 일본어 `闇雲に`의 뜻을 보존하는
`함부로 덤비기만 한다고`로 고정했습니다. 이 대체문은 2줄(528px,
672px)이고 fallback glyph가 없습니다.

문체 다듬기 보류 6개(`9:707`, `9:797`, `9:993`, `9:1051`,
`9:1692`, `9:1908`)와 별도 보류 `9:3867`, `9:3926`은 포함하지
않습니다. 그 밖의 `02xx`/`0143` 레코드도 모두 제외합니다.

스크립트는 오직 아래 private 후보 경로에만 결과를 씁니다.

`tmp/pc_dialogue_quality_wave50_static_blocks9_12_v1/candidate`

Steam 게임 파일 쓰기, 백업 거래, Git 조작, 네트워크, 푸시, 릴리즈
기능은 구현되어 있지 않습니다.

```powershell
py -3 -X utf8 workstreams\pc_dialogue_quality_wave50_static_blocks9_12_v1\build_pc_dialogue_quality_wave50_static_blocks9_12_v1.py build
py -3 -X utf8 workstreams\pc_dialogue_quality_wave50_static_blocks9_12_v1\build_pc_dialogue_quality_wave50_static_blocks9_12_v1.py verify-private
py -3 -X utf8 -m unittest workstreams\pc_dialogue_quality_wave50_static_blocks9_12_v1\test_pc_dialogue_quality_wave50_static_blocks9_12_v1.py -v
```
