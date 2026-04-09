FROM nginxinc/nginx-unprivileged:1.27-alpine

USER root

COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
COPY templates /etc/nginx/templates

RUN mkdir -p /etc/nginx/certs /etc/nginx/conf.d /tmp/nginx /var/cache/nginx \
    && chmod +x /entrypoint.sh \
    && chown -R 101:101 /etc/nginx /tmp/nginx /var/cache/nginx /entrypoint.sh

USER 101

EXPOSE 8080 8443

CMD ["/entrypoint.sh"]
