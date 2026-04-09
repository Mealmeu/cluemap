FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONUTF8=1
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /app

RUN addgroup --system --gid 10001 runner && adduser --system --uid 10001 --ingroup runner --home /app runner

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY start.sh start.sh

RUN chmod +x /app/start.sh && chown -R runner:runner /app

USER 10001:10001

EXPOSE 9000

CMD ["/app/start.sh"]