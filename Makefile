COLLECTION := holyhope.ovh
INSTALL_DIR := $(HOME)/.ansible/collections

.PHONY:build
build: $(COLLECTION).tar.gz

$(COLLECTION).tar.gz: galaxy.yml $(shell find 'plugins')
	ansible-galaxy collection build --force '.'
	mv -f $(subst .,-,$(COLLECTION))-*.tar.gz '$(COLLECTION).tar.gz'

.PHONY:install
install: $(COLLECTION).tar.gz
	test ! -L '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))' \
		|| rm -f '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))'
	mkdir -p '$(INSTALL_DIR)/ansible_collections/$(basename $(COLLECTION))'
	ansible-galaxy collection install --force $(COLLECTION).tar.gz -p '$(INSTALL_DIR)'
	$(MAKE) congratz

.PHONY:dev
dev:
	test -L '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))' \
		|| rm -rf '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))'
	mkdir -p '$(INSTALL_DIR)/ansible_collections/$(basename $(COLLECTION))'
	test -L '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))' \
		|| ln -s '$(CURDIR)' '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))'

.PHONY:uninstall
uninstall:
	test ! -L '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))' \
		|| rm -f '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))'
	test -L '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))' \
		|| rm -rf '$(INSTALL_DIR)/ansible_collections/$(subst .,/,$(COLLECTION))'

.PHONY:update
update: update-playbook.yml
	ansible-playbook \
		-c local \
		update-playbook.yml

# https://github.com/ansible/ansible/blob/devel/test/lib/ansible_test/_data/completion/docker.txt
TEST_DOCKER_IMAGE := default

.PHONY:test
test: dep lint doctest sanity-tests

.PHONY:sanity-tests
sanity-tests:
	$(MAKE) install INSTALL_DIR=$(CURDIR)
	cd '$(CURDIR)/ansible_collections/$(subst .,/,$(COLLECTION))' ; \
		ansible-test sanity --docker $(TEST_DOCKER_IMAGE) -v
	cd '$(CURDIR)/ansible_collections/$(subst .,/,$(COLLECTION))' ; \
		test ! -d tests/unit || ansible-test units --docker $(TEST_DOCKER_IMAGE) -v
	cd '$(CURDIR)/ansible_collections/$(subst .,/,$(COLLECTION))' ; \
		test ! -d tests/integration/targets || ansible-test integration --docker $(TEST_DOCKER_IMAGE) -v
	rm $(CURDIR)/ansible_collections

define CONGRATZ
Congratulation! You can now use collections.

collections:
- name: $(COLLECTION)
endef

.PHONY:congratz
congratz:
	#######
	$(info $(CONGRATZ))

doctest:
	find plugins \
		-name '*.py' \
		-type f \
		-exec python \
		-m doctest {} +

.PHONY:lint
lint: dep
	python \
		-m flake8 \
		--config flake8.cfg \
		plugins \
		tests/plugins
	find plugins \
		-name '*.py' \
		-exec python \
			-m mypy \
			{} +
	find roles \
		-mindepth 1 \
		-maxdepth 1 \
		-type d \
		-exec python \
			-m ansiblelint \
			-p \
			-c "ansible-lint.yaml" \
			{} +

.PHONY:junit-flake8.xml
junit-flake8.xml: dep
	python \
		-m flake8 \
		--format junit-xml \
		--config flake8.cfg \
		--output-file "junit-flake8.xml" \
		"plugins" \
		"tests/plugins"

junit-mypy.xml: Makefile $(shell find 'plugins' -name '*.py')
	find "plugins" \
		-name '*.py' \
		-exec python \
			-m mypy \
			--junit-xml "junit-mypy.xml" \
			{} +
	test -f junit-mypy.xml || touch junit-mypy.xml

.PHONY:dep
dep:
	pip install \
		-r requirements-tests.txt \
		--extra-index-url https://pypi.ovh.net

.PHONY:clean
clean:
	rm -f *.tar.gz
	rm -f junit-*.xml
	rm -rf $(CURDIR)/ansible_collections
	rm -rf .ansible-test
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name __pycache__ -exec rm -rf {} +
