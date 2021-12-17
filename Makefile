filepath        :=      $(PWD)
versionfile     :=      $(filepath)/version.txt
version         :=      $(shell cat $(versionfile))
image_repo      :=      0labs/chainlink

build:
	docker build -t $(image_repo):build-$(version) --build-arg chainlink_version=$(version) .

test:
	docker build --target test --build-arg chainlink_version=$(version) --tag chainlink:test . && docker run --env-file test/test.env chainlink:test

test-compose:
	echo "image=${image_repo}:${version}" > compose/.env-test
	export POSTGRES_PASSWORD=test && cd compose && docker-compose --env-file .env-test config && docker-compose --env-file .env-test up -d && \
	sleep 10 && docker-compose logs 2>&1 | grep "Listening and serving HTTP on port" && docker-compose logs 2>&1 | grep "Postgres event broadcaster: connected" && \
	docker-compose down && rm .env-test

release:
	docker build --target release -t $(image_repo):$(version) --build-arg chainlink_version=$(version) .
	docker push $(image_repo):$(version)

latest:
	docker tag $(image_repo):$(version) $(image_repo):latest
	docker push $(image_repo):latest

tools:
	docker build --target tools --tag $(image_repo):$(version)-tools --build-arg chainlink_version=$(version) .
	docker push ${image_repo}:$(version)-tools

.PHONY: build test release latest
