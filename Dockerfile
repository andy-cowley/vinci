FROM python:3.7.5-alpine AS base

FROM base AS build

WORKDIR /build
COPY src/requirements.txt .
RUN pip install --no-cache-dir --install-option="--prefix=/build" -r ./requirements.txt

FROM base

# enable edge repos
RUN sed -i -e 's/v3\.4/edge/g' /etc/apk/repositories
# enable testing
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories

#RUN apk update\
#    && apk add texlive-full\
#    texlive-xetex\
#    biber\
#    make\
#    rsync\
RUN apk update && apk add tar\
    libarchive-tools\
    gmp\
    curl

# install Ripgrep

RUN curl -Lsf https://github.com/BurntSushi/ripgrep/releases/download/11.0.2/ripgrep-11.0.2-x86_64-unknown-linux-musl.tar.gz \
    | tar xvz --strip-components=1 ripgrep-11.0.2-x86_64-unknown-linux-musl/rg && mv rg /usr/local/bin 

# install pandoc
RUN curl -Lsf https://github.com/jgm/pandoc/releases/download/2.9.1.1/pandoc-2.9.1.1-linux-amd64.tar.gz \
    | tar xvz --strip-components 2 -C /usr/local/bin

ARG BUILD_DATE
ARG VERSION

LABEL name="Vinci" \
  version=$VERSION \
  org.label-schema.schema-version="1.0" \
  org.label-schema.build-date=$BUILD_DATE \
  org.label-schema.name="Vinci" \
  org.label-schema.vendor="Andy Cowley" \
  org.label-schema.description="A lightweight markdown indexer and viewer" \
  org.label-schema.version=$VERSION

COPY --from=build /build /usr/local
COPY ./src /app

WORKDIR /app

ENTRYPOINT [ "python", "/app/main.py" ]

