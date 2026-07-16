# Steam JP `msgstf_ce` 엔딩 크레디트 감사

## 결론

`MSG_PK/JP/msgstf_ce.bin`은 PK 엔딩 크레디트 페이지용으로 강하게 분류되지만, 현재 단계에서는 **다음 후보에 넣지 않는다**. Steam 파일 열기 추적과 엔딩 화면에서의 JP 파일 선택 증거가 아직 없기 때문이다. 따라서 번역 모듈이나 완성 후보 바이너리는 만들지 않았다.

이 작업선은 Steam 1.1.7 설치본을 읽기 전용으로 분석하고, 원문 없이 해시·건수·슬롯·정적 결론만 `audit.v1.json`에 기록한다. Steam 설치본, v5 후보, 릴리스 압축 파일, 루트 README, Git 커밋은 바꾸지 않는다.

## 확인된 구조

| 언어 | 문자열 슬롯 | 실제 크레디트 페이지 | 빈 구조 슬롯 | 결과 |
| --- | ---: | ---: | ---: | --- |
| JP | 20 | 8 (`0..7`) | 12 (`8..19`) | 일본어 원문, 한글 없음 |
| EN | 20 | 8 (`0..7`) | 12 (`8..19`) | 별도 영어 페이지 |
| SC | 20 | 8 (`0..7`) | 12 (`8..19`) | TC와 원시 테이블 동일, 한글 아님 |
| TC | 20 | 8 (`0..7`) | 12 (`8..19`) | SC와 원시 테이블 동일, 한글 아님 |

네 파일은 모두 raw-LZ4 단일 메시지 테이블이며, 테이블 머리말과 슬롯 수는 호환된다. 하지만 JP와 다른 언어의 일부 페이지는 줄바꿈 또는 끝 공백 불변식이 다르며, SC·TC는 동일한 비한글 콘텐츠다. 다른 언어 파일이나 wrapper를 그대로 복사하는 방식은 안전하지 않다.

현재 v5 exact-14 대상에는 이 파일이 없다. 기존 `msgstf.bin`과도 독립 리소스이며, 실제 페이지 대부분이 달라 기존 크레디트 번역을 재사용할 수 없다.

## 로딩 근거의 등급

정적 조사에서 PK 실행 파일에 `MSG_PK`와 네 언어 코드가 존재하고, PK 엔딩 flow 파일도 확인했다. 그러나 실행 파일과 flow 파일 모두에서 `msgstf_ce.bin`의 명시 문자열은 찾지 못했다. 일반 로더가 이름을 조합할 수 있으므로 이 부재는 미로드 증거가 아니다.

따라서 현재 근거는 **언어별 리소스 구조와 엔딩 문맥의 정적 증거**까지이며, 실제 파일 열기·JP 선택은 미확인이다.

## 다음 단계

1. PK 엔딩 크레디트를 재생하는 동안 읽기 전용 파일 열기 추적을 캡처한다.
2. `MSG_PK/JP/msgstf_ce.bin`이 실제로 선택됨을 확인한다.
3. 확인된 경우에만 8개 페이지를 별도 수동 한국어 오버레이로 만들고, 인명·회사명·줄바꿈을 페이지 단위로 화면 검증한다.
4. 그 결과를 별도 후보 조립 단계에서만 추가한다.

## 재현

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\steam_jp_msgstf_ce_credits_audit_v1\build_msgstf_ce_credits_audit.py verify
& $py -B -m unittest workstreams\steam_jp_msgstf_ce_credits_audit_v1\test_msgstf_ce_credits_audit.py -q
```

`generate`도 이 작업선의 source-free JSON만 다시 만들며 게임 파일에는 쓰지 않는다.
