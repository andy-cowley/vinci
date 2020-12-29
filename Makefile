#vars
IMAGENAME=vinci
REPO=andycowley
VERSION = $(shell cat VERSION)
DEV_VERSION = dev-$(shell git rev-parse HEAD)
IMAGEFULLNAME=${REPO}/${IMAGENAME}:${VERSION}
BUILD_DATE=$(shell date +"%Y%m%d%H%M")

DEV_NOTES_DIR=/home/ac/src/ac/vinci/zk

.PHONY: help build build_local push all

help:
	    @echo "Makefile arguments:"
	    @echo ""
	    @echo "alpver - Alpine Version"
	    @echo "kctlver - kubectl version"
	    @echo ""
	    @echo "Makefile commands:"
	    @echo "build"
	    @echo "push"
	    @echo "all"

.DEFAULT_GOAL := all

build:
	    @docker build --pull --build-arg VERSION=${VERSION} --build-arg BUILD_DATE=${BUILD_DATE} -t ${IMAGEFULLNAME} .

build_local:
	@docker build --build-arg VERSION=${DEV_VERSION} --build-arg BUILD_DATE=${BUILD_DATE} -t local/vinci:dev .

dev_run:
	@docker run --rm --name=vinci-dev -it -p 5099:5000 -v ${DEV_NOTES_DIR}:/app/notes local/vinci:dev --debug=True

push:
	    @docker push ${IMAGEFULLNAME}

all: build push

dev: build_local dev_run
