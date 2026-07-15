# PK `msgbre` 직접 번역 완료 워크스트림

Switch판에서 안전하게 복구할 수 없었던 PK 열전 마지막 11개를 공식 PK SC·JP·EN·TC
테이블의 동일 ID로 읽기 전용 정렬한 뒤 한국어로 직접 번역한다. 대상은 ID `1749`와
`2207..2216`이며, 정확한 PK SC 번역 대상 키 2,217개 안에 모두 포함된다.

## 결과

- 새 번역: 11개
- 기존 오버레이와 겹침: 0개
- 등록 전 기존 번역: 2,206 / 2,217
- 이 오버레이 등록 후: 2,217 / 2,217
- 의미 확정 불가로 제외한 항목: 0개
- 원문 공개: 없음. 공개 증거에는 UTF-16LE SHA-256만 기록한다.
- 완성 게임 리소스 출력: 없음. 재구성 결과는 메모리에서만 검증한다.
- 게임·진행률·루트 README·폰트 수정: 없음

공개 오버레이는
`public/msgbre_ko_pk_native_completion_11.v0.1.json`이다. 증거·검토 인덱스·검증서는
각각 `evidence/`, `review/`, 워크스트림 루트에 생성된다.

## 검증 범위

빌더는 다음을 실패 시 즉시 중단한다.

1. 공식 4개 언어 파일의 packed/raw 크기와 SHA-256 및 3,000개 슬롯 고정
2. 정확한 PK SC 대상 키 `0..2216`과 대상 키 해시 고정
3. 자기 오버레이를 제외한 기존 2,206개 ID의 완전 일치와 11개 ID 불겹침
4. 자기 오버레이가 진행률에 등록되기 전·후 모두 같은 기존 집합을 얻는지 검증
5. printf·ESC·제어문자·줄바꿈·PUA·앞뒤 공백·사용자 정의 괄호 순서 보존
6. 공개 JSON의 CJK 통합 한자·가나 0개 및 한국어 의미 문자열 존재
7. 격리 2회와 최종 1회의 바이트 동일 산출물 및 메모리 재구성 해시 동일성

## 실행

```powershell
python -B workstreams/msgbre_pk_native_completion/build_msgbre_pk_native_completion.py
python -B -m unittest workstreams.msgbre_pk_native_completion.tests.test_msgbre_pk_native_completion -v
```

빌더 기본 SC 입력은 최초 파일 전용 트랜잭션이 보존한 pristine 백업이다. JP·EN·TC는
설치 폴더에서 읽기만 하며 파일 핀이 맞지 않으면 산출물을 만들지 않는다. 어떤 경우에도
설치된 `msgbre.bin`을 출력 경로로 사용하지 않는다.
