# 텍스트 → LaTeX (Overleaf) 변환기

일반 텍스트를 Overleaf에서 사용할 수 있는 완전한 LaTeX 문서로 변환하는 로컬 웹앱입니다. 제목, 문단, Markdown 스타일 제목과 순서/비순서 목록을 인식하고 LaTeX 특수문자를 이스케이프합니다.

## 요구 사항

- Python 3.11 이상
- PowerShell

## 설치 및 실행

PowerShell에서 이 폴더로 이동한 뒤 실행합니다.

```powershell
cd C:\path\to\upload
.\start.ps1
```

`start.ps1`가 `requirements.txt`의 패키지를 설치하고 `127.0.0.1:8000`에서 서버를 시작합니다. 브라우저에서 <http://127.0.0.1:8000>을 엽니다.

직접 실행하려면 다음과 같습니다.

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 사용법

입력창에 텍스트를 넣고 **LaTeX로 변환**을 누릅니다. 다음 구조를 지원합니다.

- 첫 줄 제목 → `\\title` 및 `\\maketitle`
- `#`, `##`, `###` 제목 → `\\section`, `\\subsection`, `\\subsubsection`
- `-`, `*`, `•` 목록 → `itemize`
- `1.`, `2)` 형식 목록 → `enumerate`

## 검증 상태

소스와 정적 UI는 준비되었지만, 이 작업 환경에서는 `python` 명령이 인식되지 않아 서버/API/실제 브라우저 검증을 완료하지 못했습니다. Python이 정상 동작하는 환경에서 위 실행 명령으로 확인할 수 있습니다.
