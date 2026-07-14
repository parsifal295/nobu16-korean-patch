# 역사 이벤트 대사 batch7 v0.7

번역 속도를 우선해 msgev ID 3819~3929의 실제 표시 대사 111개를 한국어 초벌로 옮긴 독립 배치다. 기존 v0.1~v0.6, 루트 README와 진행률 파일, 다른 작업선, 현재 글꼴, 설치기와 설치된 게임 파일은 수정하지 않았다.

## 범위

| 묶음 | ID 범위 | 번역 수 |
|---|---:|---:|
| 미요시 나가요시의 진영 교체 | 3819~3839 | 21 |
| 마쓰다이라 가문의 이마가와 종속 | 3840~3854 | 15 |
| 나가오 마사카게의 신종 | 3855~3879 | 25 |
| 깃카와 모토하루의 입양 | 3880~3898 | 19 |
| 오토모 가문의 니카이쿠즈레의 변 | 3899~3916 | 18 |
| 고바야카와 다카카게의 가독 계승 | 3917~3929 | 13 |
| 합계 | 3819~3929 | 111 |

이 범위에는 SC·JP·EN에 공통으로 들어 있는 내부 키가 없다. ID 3818은 v0.6의 마지막 대사이며, ID 3930부터 다케다·무라카미의 도이시성 사건이 시작된다.

## 번역·검수 상태

- 111개 모두 translated 초벌이며 사람 문체 검수와 런타임 검수가 필요하다.
- SC·JP·EN의 같은 ID를 대조했다. 공개 근거에는 원문 대신 333개 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 줄바꿈, 앞뒤 공백, 제어문자, PUA, printf 토큰을 모두 보존했다.
- [bm1448], [b1448], [b473], [bm473], [bm1730], [b1730] 자리표시자의 종류와 순서를 111회 별도로 검사했다.
- 가변 이름 뒤에는 공, 님 같은 고정 명사를 두어 한국어 조사 충돌을 피했다.
- ESC 코드를 뺀 작성 줄의 최대 길이는 32코드포인트이며 32자를 넘는 항목은 없다.
- 미요시 유키나가, 호소카와 게이초, 가재·간토 간레이, 사카토성, 고쿠진, 깃카와 오키츠네, 갓산토다성, 뉴타, 니카이쿠즈레의 변, 누타 고바야카와 관련 용어와 독음은 용어집 검수가 필요하다.
- 동적 장수명 [bm1448], [b1448], [b473], [bm473], [bm1730], [b1730]의 실제 표시는 장수명 오버레이와 함께 런타임에서 확인해야 한다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| public/msgev_ko_historical_events_3819_3929.v0.7.json | 8B121FE9A3D78EC0C936732A801F1710FE4D4334AC322F9954066C10B097D392 |
| evidence/alignment_evidence.v0.7.json | E4AE64791A6130C7E2D556A9C9C4394646C7D0E07D824BCC9F26A745FB9E8559 |
| review/review_index.v0.7.json | 74F9F475F31819A087D8C2E86F1564DEAE390197B8616E4CCE17A60F5E0D037B |
| validation.v0.7.json | 3EE51745A00EBDB234E9F98DED40C6C5CE6D8395E6A93EAB181E310F9E09400C |

위 네 파일은 독립 A/B 생성과 최종 경로에서 바이트 단위로 같았다. 공개 오버레이·정렬 근거·검수 인덱스의 통합 한자 영역 문자와 히라가나·가타카나는 모두 0개다.

## 통합 제한

이번 배치는 번역량 확보를 위한 후속 릴리스 입력이다. 현재 글꼴과 설치기에는 포함하지 않는다. 실제 배포 전에는 v0.1~v0.7과 장수명 오버레이를 순정 SC 기준으로 병합하고, 새 글리프 수요를 계산한 뒤 후속 글꼴을 만들어야 한다.

## 재생성

    $Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    $Script = "workstreams\dialogue\build_event_dialogue_batch7.py"

    foreach ($Out in @(
      "tmp\dialogue_batch7_a",
      "tmp\dialogue_batch7_b",
      "workstreams\dialogue"
    )) {
      & $Python -B $Script --out-root $Out
      if ($LASTEXITCODE -ne 0) { throw "dialogue batch7 build failed: $Out" }
    }

    & $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch7.py"
    if ($LASTEXITCODE -ne 0) { throw "dialogue batch7 tests failed" }
