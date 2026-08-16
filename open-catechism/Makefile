GOML ?= .tools/goml
HUGO ?= .tools/hugo

.PHONY: tool generate validate coverage build

tool:
	mkdir -p .tools
	GOBIN=$(CURDIR)/.tools go install github.com/brain-fuel/goplus/cmd/goml@v0.145.1
	GOBIN=$(CURDIR)/.tools CGO_ENABLED=0 go install github.com/gohugoio/hugo@v0.164.0

generate: tool
	$(GOML) gen ./cmd/open-catechism

validate: generate
	go run ./cmd/open-catechism validate

coverage: generate
	go run ./cmd/open-catechism coverage

build: generate
	go run ./cmd/open-catechism build --format all
