# ClueMap 서버 배포 빠른 가이드 (HTTP/IP 직결)

이 번들은 `http://183.96.149.8/` 로 바로 접속되도록 맞춰져 있습니다.
현재 설정은 **도메인 없이 IP + HTTP** 기준입니다.

## 1) 서버에 복사

```bash
sudo mkdir -p /srv/cluemap
sudo chown -R $USER:$USER /srv/cluemap
cd /srv/cluemap
```

이 폴더에 번들 내용을 풀어 둡니다.

## 2) 필수 확인

- `.env` 는 이미 `183.96.149.8` 기준으로 조정되어 있습니다.
- 현재 번들은 즉시 기동을 위해 `LLM_PROVIDER=disabled` 로 조정되어 있습니다.
- 따라서 GGUF 모델 파일 없이도 페이지는 먼저 뜹니다.
- 나중에 로컬 LLM을 붙이려면 `.env` 에서 `LLM_PROVIDER=local` 로 바꾸고 `backend/models/` 아래에 모델 파일을 넣으면 됩니다.
- UFW를 쓴다면 80/tcp 를 허용해야 합니다.

```bash
sudo ufw allow 80/tcp
```

## 3) 실행

```bash
cd /srv/cluemap
docker compose --env-file .env up -d --build
sh scripts/migrate.sh
sh scripts/seed.sh
```

## 4) 확인

```bash
docker compose --env-file .env ps
docker compose --env-file .env logs nginx --tail=100
docker compose --env-file .env logs backend --tail=100
curl -I http://127.0.0.1/
curl -I http://127.0.0.1/healthz
curl -I http://127.0.0.1/api/auth/me
```

브라우저에서는 아래 주소로 접속합니다.

```text
http://183.96.149.8/
```

## 5) 재빌드

```bash
cd /srv/cluemap
docker compose --env-file .env down
docker compose --env-file .env up -d --build
```

## 6) 나중에 도메인/TLS 붙일 때

아래 값만 바꾸면 됩니다.

- `FRONTEND_ORIGIN`
- `CORS_ORIGINS_RAW`
- `TRUSTED_HOSTS_RAW`
- `CSRF_TRUSTED_ORIGINS_RAW`
- `COOKIE_SECURE=true`
- `ENABLE_TLS=true`
- `NGINX_SERVER_NAME=<도메인>`
