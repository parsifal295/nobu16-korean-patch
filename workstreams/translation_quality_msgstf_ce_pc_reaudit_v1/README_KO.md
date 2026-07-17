# `msgstf_ce` PC 원문 재감사 v1

`msgstf_ce`의 20개 슬롯을 PC 리소스만으로 확인했다. 별도 pristine backup에는
이 파일이 없었지만, 현재 Steam JP 파일은 프로젝트의 과거 파일 트랜잭션에 포함되지
않았고 일본어 전용 glyph 구성을 가진 원본 상태임을 메타데이터·해시로 확인했다.

- PC JP 원본(운영상): `27E8F296E7EA452E6AC1D6D6884084D3AB635D11281AF01E3A1F0A3696710F36`
- 기존 generic 좌표 0–7은 한글 본문을 읽지 않고 source-free 좌표로만 제외했다.
- 남은 8–19는 JP/EN/SC/TC 모두 빈 문자열인 예약 슬롯이다.
- 신규 번역 후보와 HOLD는 모두 0건이다.

Switch 한글·과거 한글·`F:\Games\NOBU16\MSG_PK\SC`·Steam 쓰기 경로는 사용하지
않았다.
