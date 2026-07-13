# msgui ID 4101-4200 canonical empty 검증 기록

## 결과

- 대상 범위: ID 4101-4200, 정확히 100행
- EN/JP/SC/TC가 모두 빈 행: 100개
- catalog 상태 `empty`: 100개
- printf, ESC, PUA, 기타 제어문자: 없음
- 번역 배치 엔트리: 0개
- 설치 게임 파일 변경: 없음

이 범위는 네 언어에서 모두 canonical empty이므로 한국어 문자열을 임의로 추가하지 않는다.
`export-batch --id-range 4101:4200`도 `exported_entries=0`을 반환했다. 공개 overlay와
빌드에서는 기존 빈 슬롯을 그대로 유지한다.
