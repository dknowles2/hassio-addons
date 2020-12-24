ARG BUILD_FROM
FROM $BUILD_FROM
ENV LANG C.UTF-8
LABEL maintainer="dknowles2@gmail.com"
LABEL description="Moves files to Google Drive"
RUN apk add --no-cache go && go get github.com/dknowles2/gdrive_sync
COPY run.sh /
ENTRYPOINT ["/run.sh"]
