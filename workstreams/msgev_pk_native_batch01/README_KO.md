# PK `msgev` 직접 번역 배치 01

현재 진행률 카탈로그와 source-free exact target 카탈로그를 교차해 아직 소유되지 않은
ID 중 오름차순 첫 100개를 고정하고, 공식 PK SC·JP·EN·TC를 읽기 전용으로 대조했다.
Switch v1.3의 일본어 해시 대응도 검사했지만 실제 번역 대상으로 선택한 8개에는 exact
대응이 없어서 공식 PK 4개 언어 문맥으로 직접 한국어를 작성했다.

## 결과

- 검토 후보: 100개
- 실제 한국어 번역: 8개
- 런타임 안전을 위해 원값 유지: 92개
- 기존 모든 `msgev` 오버레이와 겹침: 0개
- exact target 밖 번역: 0개
- 후보 ID SHA-256: `FD49D3BA09ADF8116F1ACD817C33569D93C8E952B0271CB4F79BFF1F560672BF`
- 번역 ID SHA-256: `54515802F2DE57ACA59985B84CEBFBE073F3C54403ADFDC892E21A9530197C6F`
- 오버레이 SHA-256: `049A0A885F4E02F9975D7585567F3B3066DCA05C76642A07860314AA6726964D`

번역 ID는 `2581, 3105, 3106, 3107, 3108, 6986, 7677, 7828`이다. 앞의
5개는 인명, 뒤의 3개는 사건 서술문이다.

## 제외 92개의 의미

이 92개는 번역이 어려워서 방치한 문장이 아니다. 현재 exact target 생성 규칙이
“비어 있지 않은 SC 슬롯”을 넓게 잡으면서 포함한 런타임 구조값이다.

- 동적 인물 치환 토큰만 있는 슬롯: 36개
- 내부 화자 조회 키: 7개
- 내부 지역 엔딩 이벤트 조회 키: 18개
- 동적 토큰과 비언어적 문장부호만 있는 슬롯: 2개
- 말줄임표·물음표·느낌표만 있는 비언어적 반응 슬롯: 29개

이 값을 한글로 바꾸면 동적 인물 치환이나 이벤트 조회가 깨질 수 있고, 문장부호만 있는
값을 동일 값으로 오버레이에 넣으면 번역 진행률만 부풀린다. 따라서 review/evidence에
정확한 ID와 이유를 남기되 오버레이 소유권은 만들지 않는다.

## 산출물

- `public/msgev_ko_pk_native_batch01_8.v1.json`
- `evidence/msgev_pk_native_batch01_alignment.v1.json`
- `review/msgev_pk_native_batch01_review.v1.json`
- `validation.v1.json`

공개 증거에는 공식 원문 대신 각 언어 슬롯의 UTF-16LE SHA-256만 기록한다. 완성 게임
리소스는 출력하지 않으며 8개 치환 결과는 메모리에서만 재구성·재파싱한다.

## 검증

```powershell
python -B workstreams/msgev_pk_native_batch01/build_msgev_pk_native_batch01.py
python -B -m unittest discover -s workstreams/msgev_pk_native_batch01/tests -p "test_*.py" -v
```

빌더와 테스트는 첫 100개 선택, 8/92 분할, 분류별 원문 구조, 기존 오버레이 불겹침,
exact target 소속, printf·ESC·제어문자·줄바꿈·PUA·앞뒤 공백·사용자 정의 괄호 순서,
source-free 산출물, 격리 A/B 재현, 자기 등록 전후 바이트 동일성을 모두 확인한다.

이 워크스트림은 루트 진행률·README·폰트·설치된 게임 파일을 수정하거나 배포·커밋·
푸시하지 않는다.
