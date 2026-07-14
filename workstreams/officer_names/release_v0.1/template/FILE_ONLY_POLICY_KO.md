# 파일 전용 배포 정책

허용 범위는 네 고정 리소스의 검증, 로컬 stock 백업, 공개 레시피 재생성, 같은 볼륨의 임시
파일을 이용한 거래적 교체와 복원뿐이다.

금지 사항:

- 실행 중인 프로세스 조회·연결·메모리 읽기·쓰기
- DLL 주입, API 후킹, 프록시 DLL, 런타임 로더
- 게임 EXE 또는 런처 수정·교체·패치
- 레지스트리 읽기·쓰기
- Steam 경로·클라이언트·manifest 의존
- 공식 상용 리소스 완성본이나 공식 원문 전체의 배포

경로는 네 고정 상대 경로만 허용한다. 패키지와 게임 경로의 `..` 탈출, 절대경로 삽입,
대소문자 충돌, 중복 JSON 키, 심볼릭 링크·junction·mount point 등 reparse point를 거부한다.
stock·target·허용 predecessor는 크기와 SHA-256으로 고정한다.

허용 상태는 `stock`, 최종 네 파일, 검토된 predecessor 네 파일이라는 완전한 벡터 단위로만
판정한다. 리소스별 허용 해시의 임의 조합은 거부한다. Font-v5 라이선스·metrics·pixel payload도
고정된 다섯 상대 경로와 크기·SHA-256 외에는 패키지에 흡수하지 않는다.

`Development`와 `ReleaseCandidate` 승격을 분리한다. 후자는 최종 네 리소스 recipe E2E와 runtime
QA 통과 증명 및 그 증명의 크기·SHA-256을 모두 검증한 패키지만 허용한다.

운영체제는 네 파일을 한 번에 교체하는 단일 syscall을 제공하지 않으므로, 설치기는 각 파일의
동일 디렉터리에서 durable stage와 rollback 파일을 만들고 저널을 갱신한다. 부분 실패 시 이미
교체한 파일을 역순으로 복원하고 네 해시 벡터를 다시 검증해야 거래가 실패 종료된다.
predecessor→stock→final의 두 거래를 잇는 상위 migration 저널은 네 시작 snapshot의 경로·크기·
SHA-256을 고정한다. 복구는 내부 거래 저널을 먼저 처리한 뒤에만 이 snapshot을 사용하며,
snapshot은 고정 backup 디렉터리의 직계 자식 네 파일 외에는 허용하지 않는다.
