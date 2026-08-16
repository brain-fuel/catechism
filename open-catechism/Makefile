GOML ?= .tools/goml

.PHONY: tool generate validate coverage build

tool:
	mkdir -p .tools
	GOBIN=$(CURDIR)/.tools go install github.com/brain-fuel/goplus/cmd/goml@v0.145.1

generate: tool
	$(GOML) gen ./cmd/open-catechism

validate: generate
	go run ./cmd/open-catechism validate

coverage: generate
	go run ./cmd/open-catechism coverage

build: generate
	go run ./cmd/open-catechism build --format all

