# JP G1N table 1 그리운 경찰감성체 교체 v1

0.94 일본어 리소스의 각 G1N에서 **0부터 세는 table 1(두 번째 테이블)**만
`그리운 경찰감성체 Regular` 래스터로 교체한다. table 0과 table 2는 글리프
픽셀까지 입력과 바이트 단위로 동일하게 유지한다.

## 대상

| 리소스 | G1N outer entry | table 1 cell / raster |
|---|---|---:|
| `RES_JP/res_lang.bin` | 6, 7 | 48 / 46 |
| `RES_JP_PK/res_lang_pk.bin` | 16, 17 | 48 / 46 |
| `RES_JP_PK_PORT/res_lang_pk_port1.bin` | 1 | 96 / 92 |
| `RES_JP_PK_PORT/res_lang_pk_port2.bin` | 0, 1 | 96 / 92 |

G1N 맵, 12바이트 레코드, 폭·셀·포인터, 팔레트, LINK 비대상 entry는
수정하지 않는다. table 1의 기존 한글 슬롯 중 공식 TTF cmap이 제공하는
글리프의 픽셀 span만 같은 크기로 덮어쓴다.

## 폰트 입력과 예외

- 공식 페이지: `https://www.griun.co.kr/fonts/polsensibility`
- 입력 파일: `Griun_PolSensibility-Rg.ttf`
- 크기: `1,936,424 bytes`
- SHA-256: `057472E1B8E4528421A5B30953A33992FFCE06F2BF9546993C364E264CD1887F`
- TTF는 수정하거나 패처 결과물에 포함하지 않는다. 오프라인 4bpp 래스터
  입력으로만 사용한다.
- `U+CE4C`은 사용되지 않는 기존 매핑이며 TTF cmap에 없으므로 기존 table 1
  픽셀을 유지한다.
- `U+D07F` `큿`은 번역 수요에 있으나 TTF cmap에 없으며, 사용자 지시에 따라
  기존 table 1 픽셀을 유지한다. 합성·대체 폰트 fallback을 사용하지 않는다.

기존 서울한강체 TTF 3종은 G1N 안에 혼합 보존하지 않고 다음 별도 백업에
원본 파일 그대로 보존한다.

`I:/Workspaces/NOBU16-Korean/scratch/font-backups/seoulhangang-before-griun-20260820`

## 빌드

```powershell
python -B workstreams/font_jp_griun_polsensibility_v1/build_font_jp_griun_polsensibility_v1.py `
  --input-root I:/Workspaces/NOBU16-Korean/scratch/release-v0940-approve-all-layered-20260820-01/resource-input/target `
  --font I:/Workspaces/NOBU16-Korean/scratch/font-griun-polsensibility-v1/source/Griun_PolSensibility-Rg.ttf `
  --output-root I:/Workspaces/NOBU16-Korean/worktrees/V0905_RELEASE/tmp/font_jp_griun_polsensibility_v1/run_a
```

출력 경로는 이 worktree 아래의 비어 있는 디렉터리만 허용한다. 빌더는 Steam
설치 파일에 쓰지 않는다. 후보는 독립 A/B 빌드 일치와 table 0/2 보존 검증을
통과한 뒤에만 0.94 패처 입력으로 승격한다.

## 회귀 검사

```powershell
python -B -m unittest workstreams/font_jp_griun_polsensibility_v1/tests/test_font_jp_griun_polsensibility_v1.py -v
```

테스트 fixture는 table 1의 대상 span 하나만 바뀌는지, `큿` 예외와 table 0/2
픽셀이 유지되는지, table 간 atlas pointer alias가 거부되는지를 확인한다.

## 설치 선택 통합

패처 0.2.8의 설치 화면에서는 다음 두 후보를 고른다. 여기의 A/B는 재현 빌드
run A/B와 별개인 사용자 선택 코드다.

- `A`: `SeoulHangang ExtraBold`를 유지한 기존 0.94 리소스
- `B`: 이 파이프라인으로 table 1만 교체한 `그리운 경찰감성체`

각 후보는 동일한 Steam JP 1.1.7 순정 프로필을 입력으로 하는 독립 서명 번들이다.
선택한 번들 하나만 적용하며 글꼴을 바꿀 때는 전체 원본 복구 후 다시 적용한다.

CLI 미리보기는 두 후보의 `RES_JP_PK_PORT/res_lang_pk_port1.bin` table 1에서
96px 글리프를 직접 추출해 만든 무손실 PNG다. JPEG는 사용하지 않는다.

```powershell
& workstreams/font_jp_griun_polsensibility_v1/New-FontChoicePreviews.ps1 `
  -SeoulHangangCandidateRoot I:/Workspaces/NOBU16-Korean/scratch/release-v0940-approve-all-layered-20260820-01/resource-input/target `
  -GriunCandidateRoot I:/Workspaces/NOBU16-Korean/worktrees/V0905_RELEASE/tmp/font_jp_griun_polsensibility_v1/run_rc8_a/candidate `
  -OutputRoot I:/Workspaces/NOBU16-Korean/worktrees/V0905_RELEASE/workstreams/rust_patcher_v1/rust/crates/n16patch-cli/assets
```

PNG는 패처 실행 파일에 내장된다. ANSI 색상을 지원하면 상·하 픽셀을 전경·배경색으로
합친 반블록으로 표시하고, 지원하지 않으면 `▀▄█` 단색 조합으로 자동 폴백한다.
