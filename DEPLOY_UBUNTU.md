# ClueMap Ubuntu 배포 가이드

## 1. 서버 준비

```sh
cd /tmp
sh /opt/cluemap/scripts/bootstrap-ubuntu.sh
```

다시 로그인한 뒤 작업합니다.

## 2. 소스 업로드

```sh
sudo mkdir -p /opt/cluemap
sudo chown -R $USER:$USER /opt/cluemap
cd /opt/cluemap
```

Git 사용 시:

```sh
git clone <REPO_URL> /opt/cluemap
cd /opt/cluemap
```

WinSCP 또는 PSCP 사용 시:

```powershell
pscp -i C:\path\key.ppk -r C:\path\repo\* ubuntu@SERVER_IP:/opt/cluemap/
```

## 3. 환경변수 준비

```sh
cd /opt/cluemap
cp .env.example .env
mkdir -p backend/models infra/nginx/certs backups
```

`.env`에서 최소 수정:

```dotenv
ENVIRONMENT=production
POSTGRES_PASSWORD=강한비밀번호
DATABASE_URL=postgresql+psycopg://cluemap:강한비밀번호@postgres:5432/cluemap
ACCESS_TOKEN_SECRET=32자이상강한값
REFRESH_TOKEN_SECRET=32자이상강한값
SANDBOX_RUNNER_SHARED_SECRET=32자이상강한값
FRONTEND_ORIGIN=https://도메인
CORS_ORIGINS_RAW=https://도메인
TRUSTED_HOSTS_RAW=도메인,서버IP
CSRF_TRUSTED_ORIGINS_RAW=https://도메인
COOKIE_SECURE=true
ENABLE_TLS=true
NGINX_SERVER_NAME=도메인
LOCAL_LLM_PROFILE_NAME=ClueMap KR Analyzer
LOCAL_LLM_MODEL_FILE=cluemap-kr-analyzer-qwen3-4b-q4_k_m.gguf
```

## 4. 로컬 LLM 모델 업로드

서버 배치 경로:

```text
/opt/cluemap/backend/models/cluemap-kr-analyzer-qwen3-4b-q4_k_m.gguf
```

업로드 예시:

```powershell
pscp -i C:\path\key.ppk C:\path\cluemap-kr-analyzer-qwen3-4b-q4_k_m.gguf ubuntu@SERVER_IP:/opt/cluemap/backend/models/
```

## 5. TLS 준비

셀프사인 인증서:

```sh
cd /opt/cluemap
sh scripts/prepare-ssl.sh infra/nginx/certs localhost
```

실인증서 발급:

```sh
cd /opt/cluemap
sh scripts/issue-certbot.sh example.com admin@example.com
```

## 6. 서비스 기동

```sh
cd /opt/cluemap
docker compose up --build -d
sh scripts/migrate.sh
sh scripts/seed.sh
sh scripts/verify-flow.sh
```

확인:

```sh
docker compose ps
docker compose logs -f backend
docker compose logs -f runner
curl http://localhost/healthz
curl -k https://localhost/healthz
```

## 7. 백업과 복구

DB 백업:

```sh
cd /opt/cluemap
sh scripts/backup-postgres.sh
```

DB 복구:

```sh
cd /opt/cluemap
sh scripts/restore-postgres.sh backups/cluemap-YYYYMMDD-HHMMSS.dump
```

## 8. 배포 번들 생성

```sh
cd /opt/cluemap
sh scripts/create-release-bundle.sh cluemap-release.zip
```

번들에 포함되지 않는 것:

- `.env`
- `backend/models/*.gguf`
- `frontend/node_modules`
- `frontend/dist`
- `__pycache__`
- `*.pyc`
- 인증서 `.pem`
- 백업 파일
- 로그와 기존 zip

## 9. Ubuntu 운영 체크

- `ufw status`
- `sudo fail2ban-client status sshd`
- `timedatectl status`
- `sudo journalctl -u docker --since today`
- `docker compose logs --tail=200 backend`
- `docker compose logs --tail=200 runner`
- `sh scripts/verify-flow.sh`
