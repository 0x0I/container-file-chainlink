filepath        :=      $(PWD)
versionfile     :=      $(filepath)/version.txt
version         :=      $(shell cat $(versionfile))
image_repo      :=      0labs/chainlink

build:
	docker build -t $(image_repo):build-$(version) .

test:
	docker build --target test --build-arg chainlink_version=$(version) --tag chainlink:test . && docker run --env-file test/test.env chainlink:test

release:
	docker build --target release -t $(image_repo):$(version) .
	docker push $(image_repo):$(version)

latest:
	docker tag $(image_repo):$(version) $(image_repo):latest
	docker push $(image_repo):latest

.PHONY: build test release latest
