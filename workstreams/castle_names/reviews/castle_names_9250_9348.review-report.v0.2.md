# 성 이름 ID 9250~9348 사람 검수 제안 v0.2

## 결론

ID `9250..9348` 99개를 공식 게임 EN 표시명, JP 표시명, JP 읽기 블록과 같은 ID로 대조했다. 91개는 현 초안을 유지하고, 8개는 별도 제안으로 분리했다. 기준 공개 overlay와 게임 파일은 수정하지 않았다.

- 독립 수정 4개: 장음 2개, 공식 한국어 복합 지명 2개
- 지명 `tsu` 표기 정책에 묶인 수정 4개
- 상용 원문은 이 공개 제안과 보고서에 복사하지 않았다.

JSON 제안서는 `reviews/castle_names_ko_9250_9348.review-proposal.v0.2.json`이다.

## 검수 범위와 재현 기준

- 범위: `9250..9348`, 연속 99개
- 기준 공개 overlay SHA-256: `465F0CA873E310C20FAF9DF7D247B4A5025991774E1C4F8F320BC4125A93AE13`
- 비공개 EN/JP 정렬본 SHA-256: `6169A149F4F52D368751E0EE7B802B57704E76A1E747C0A98628596C43BA7E8F`
- 공식 EN `msgdata.bin` wrapper SHA-256: `15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1`
- 공식 JP `msgdata.bin` wrapper SHA-256: `9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38`

JP 읽기에서 장음, 촉음, 탁음, `tsu`/`zu` 구별을 직접 확인하고 EN 로마자와 교차 확인했다. 따라서 `zu` 계열을 포함하는 항목은 `tsu` 정책 변경 대상에 넣지 않았다.

## 변경 제안

| ID | 현 초안 | 제안 | 판정 |
|---:|---|---|---|
| 9256 | 시이즈 | 시즈 | 별도 근거가 없는 장음 중복을 국립국어원 원칙에 맞게 축약; 희소 지명이므로 병합 전 한 번 더 확인 권장 |
| 9283 | 츠루가오카 | 쓰루가오카 | 지명 `tsu`를 표준 한국어 `쓰`로 통일하는 정책 항목 |
| 9298 | 이와츠키 | 이와쓰키 | 지명 `tsu`를 표준 한국어 `쓰`로 통일하는 정책 항목 |
| 9304 | 이이야마 | 이야마 | JNTO 한국어 페이지의 실제 표기와 일치 |
| 9316 | 마츠나미 | 마쓰나미 | 지명 `tsu`를 표준 한국어 `쓰`로 통일하는 정책 항목 |
| 9334 | 구조 하치만 | 구조하치만 | JNTO의 해당 성 및 지역 표기에 맞춰 기계적인 EN 공백 제거 |
| 9340 | 마츠가시마 | 마쓰가시마 | 지명 `tsu`를 표준 한국어 `쓰`로 통일하는 정책 항목 |
| 9346 | 야마토 고리야마 | 야마토코리야마 | JNTO와 나라현 한국어 자료의 확립된 복합 지명 사용 |

`tsu` 4건은 정확한 독음 문제라기보다 프로젝트의 지명 표기 정책 문제다. 앞 구간 제안과 동일하게 `approve_geographic_tsu_style` 결정 전에는 자동 병합하지 않는다.

## 장음과 `ii` 검수

기계적으로 모든 `ii`를 한 글자로 줄이지 않았다. 공식 한국어 용례가 있는 경우 그 표기를 우선했다.

- ID `9304`: `이야마`로 변경 제안. JNTO가 이 표기를 반복 사용한다.
- ID `9305`: `이이다` 유지. JNTO 한국어 용례가 있다.
- ID `9347`: `이이모리야마` 유지. JNTO가 `이이모리산`, `이이모리야마시타`를 사용한다.
- ID `9277`: `이이노다이라` 잠정 유지. 권위 있는 한국어 반대 용례가 없어 희소 고유명사의 음절을 임의 축약하지 않았다.
- ID `9256`: 권위 있는 한국어 관용형을 찾지 못했으므로 장음 비표기 원칙에 따라 `시즈`를 제안하되 신뢰도는 중간으로 두었다.

그 밖의 장음 포함 항목은 JP 읽기와 한국어 장음 비표기 원칙을 대조해 현 형태를 유지했다.

## 복합 지명 공백 검수

- `고리 니시야마`, `소마 나카무라`, `히다 다카야마`, `단바 가메야마`: 지역 구분자 성격의 공백 유지
- `기소 후쿠시마`: JNTO 한국어 페이지가 공백을 사용하므로 유지
- `구조하치만`: 해당 성의 공식 한국어 표기가 붙임이므로 변경 제안
- `야마토코리야마`: JNTO 제목·지역 링크와 나라현 한국어 자료에서 붙임이 확립되어 변경 제안

## 근거 링크

- 국립국어원 일본어 `tsu` 표기 설명: <https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&pageIndex=1&qna_seq=275072&searchCondition=&searchKeyword=>
- 국립국어원 일본어 장음 비표기 설명: <https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&pageIndex=1&qna_seq=329857>
- JNTO `이야마`: <https://www.japan.travel/ko/kr/japan-magazine/2309_shinrin-yoku-the-japanese-art-of-forest-bathing/>
- JNTO `이이다`: <https://www.japan.travel/ko/kr/japan-magazine/2402_sakura-and-beyond-famous-japanese-flowers-to-check-out/>
- JNTO `기소 후쿠시마`: <https://www.japan.travel/ko/destinations/hokuriku-shinetsu/nagano/kiso/>
- JNTO `구조하치만성`: <https://www.japan.travel/ko/spot/1266/>
- JNTO `야마토코리야마`: <https://www.japan.travel/ko/spot/1995/>
- 나라현 한국어 `야마토코리야마` 자료: <https://www.pref.nara.jp/secure/116801/%E5%A5%88%E3%81%AE%E8%89%AF%E3%80%80%E7%AC%AC2%E5%8F%B7%E3%80%80%E3%83%8F%E3%83%B3%E3%82%B0%E3%83%AB.pdf>
- JNTO `이이모리산`: <https://www.japan.travel/ko/spot/1760/>

## 다음 병합 단계

1. `쓰` 정책 4건을 앞 구간의 동일 정책 제안과 함께 승인하거나 보류한다.
2. 독립 수정 중 `이야마`, `구조하치만`, `야마토코리야마` 3건은 공식 한국어 용례가 명확해 우선 반영할 수 있다.
3. `시즈`는 희소 지명이므로 최종 병합 때 별도 확인한다.
4. 승인된 ID만 전체 392개 overlay에 ID별로 병합하고, 단순 문자열 일괄 치환은 하지 않는다.

이 보고서는 overlay, 설치기, 폰트, 게임 파일을 변경하지 않으며 배포 recipe도 만들지 않는다.
