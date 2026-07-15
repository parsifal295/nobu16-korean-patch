# Switch v1.1 `msgdata` 엄격 이식 v0.1

Switch용 비공식 한글 패치의 `strdata.bin`에서, PC 기본판 JP 문자열과 완전히 일치하는 문자열만 해시 역색인하여 PK `MSG_PK/SC/msgdata.bin`에 이식하는 source-free 카탈로그다.

출처는 GitHub 사용자 [`snake7594`](https://github.com/snake7594), 저장소 [`nobunaga-shinsei-korean-patch`](https://github.com/snake7594/nobunaga-shinsei-korean-patch), 릴리스 [`v1.1`](https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1)이다. 공개 시각은 `2026-07-14T14:13:23Z`이며, 제공된 `NobunagaShinsei_KoreanPatch_v1.1.zip`의 SHA-256은 `931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6`이다. ZIP 내부 README에는 저자 표기가 없으므로 위 GitHub 계정명을 출처 표기로 사용한다.

적격 조건은 다음과 같다.

- PC 기본 JP `MSG/JP/strdata.bin`의 다섯 블록(25,069 / 4,100 / 3,000 / 122 / 20) 전체에서 UTF-16LE SHA-256으로 역색인한 JP 문자열과 PK JP가 완전히 일치한다.
- 같은 JP 해시의 Switch 한국어 후보가 한 값으로 수렴하고, 각 후보는 원 JP와 다르며 의미 있는 한글을 포함한다.
- `translation_progress.v0.1.json`의 PK `msgdata` 오버레이가 이미 점유한 ID와 겹치지 않는다.
- PK SC의 printf·ESC·제어문자·줄바꿈·PUA·양끝 공백 불변식을 지킨다.
- CJK 통합한자나 Kana가 하나라도 있는 Switch 한국어 결과는 제외한다.

이 조건으로 16,176개의 새 ID만 남는다. ZIP, 게임 원문, 완성된 게임 리소스는 산출물에 포함하거나 기록하지 않는다. 번역은 외부 이식본이며 사람·실행 화면 검토 전 상태다.

```powershell
python -B workstreams/switch_msgdata_v11/build_switch_msgdata_v11.py --out-root workstreams/switch_msgdata_v11
python -B -m unittest workstreams.switch_msgdata_v11.tests.test_switch_msgdata_v11
```
