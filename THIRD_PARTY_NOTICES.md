# 외부 번역 원천 고지

아래의 선별 한국어 번역은 Switch용 비공식 패치 배포본을 호환성 검증을 거쳐
PK PC판의 대응 문자열에 이식한 것입니다.

- 원천 저장소·계정: [`snake7594/nobunaga-shinsei-korean-patch`](https://github.com/snake7594/nobunaga-shinsei-korean-patch)
- 원천 릴리스: [v1.1](https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1), 2026-07-14
- 검증한 파일: `NobunagaShinsei_KoreanPatch_v1.1.zip`
- SHA-256: `931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6`
- 이식 후보 리소스: `msgev.bin`, `msgdata.bin`, `msggame.bin`

원천 ZIP과 게임 원문은 이 저장소에 포함하지 않습니다. 각 이식 항목은 다음을
모두 만족할 때만 공개 오버레이에 들어갑니다.

1. 대응 JP 원문이 해시 기준으로 완전히 일치한다.
2. PK SC 원본의 printf·ESC·제어문자·줄바꿈 구조가 보존된다.
3. 기존 공개 오버레이의 ID 또는 literal 좌표와 겹치지 않는다.
4. PC 한글 글꼴 범위 밖의 CJK 통합한자·Kana를 포함하지 않는다.

외부 번역의 원 저작권과 출처 표시는 원 저작자에게 귀속됩니다. 이 프로젝트는
원천 배포물을 재배포하지 않으며, 이식 근거와 출처를 보존합니다.
