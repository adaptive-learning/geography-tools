SSH_CONNECTION=51bb5930500446923f000201@geography-conqueror.rhcloud.com

target/download:
	rm -rf target/download; \
	mkdir -p target/download; \
	cd target/download; \
	git clone git@github.com:kartograph/kartograph.py.git; \
	cd kartograph.py; \
	python setup.py build; \
	cd ..; \
	wget https://github.com/mapnik/mapnik/wiki/data/110m-admin-0-countries.zip -O geoshapes.zip; \
	mkdir geoshapes; \
	unzip geoshapes.zip -d geoshapes; \

target/external-libs: target/download
	rm -rf target/external-libs; \
	mkdir -p target/external-libs; \
	cp -r target/download/kartograph.py/build/*/kartograph target/external-libs

target/data: target/download
	rm -rf target/data; \
	echo $(SSH_CONNECTION); \
	mkdir -p target/data; \
	ssh $(SSH_CONNECTION) -t '/var/lib/openshift/51bb5930500446923f000201/app-root/runtime/repo/wsgi/openshift/manage.py dumpdata questions.answer > /tmp/data.answers.json' && \
	scp $(SSH_CONNECTION):/tmp/data.answers.json target/data/answers.json; \
	ssh $(SSH_CONNECTION) -t '/var/lib/openshift/51bb5930500446923f000201/app-root/runtime/repo/wsgi/openshift/manage.py dumpdata core.Place > /tmp/data.places.json' && \
	scp $(SSH_CONNECTION):/tmp/data.places.json target/data/places.json; \
	python prepare-data.py; \
	cp target/download/geoshapes/ne_110m_admin_0_countries.shp target/data/world.shp;

target/reports: target/data notebooks/* libs/geodata/*
	rm -rf target/reports;
	mkdir -p target/reports;
	cd notebooks; for NOTEBOOK in *.ipynb; do \
		BASENAME=`basename $$NOTEBOOK .ipynb`; \
		echo "$$BASENAME"; \
		runipy $$NOTEBOOK -q --pylab --html ../target/reports/$$BASENAME.html; \
	done;\

publish: reports
	ssh jpapouse@zimodej.cz -t "rm -rf /var/www/zimodej.cz/subdomeny/geodata/ && mkdir /var/www/zimodej.cz/subdomeny/geodata/ && (echo 'Options +Indexes' > /var/www/zimodej.cz/subdomeny/geodata/.htaccess)"; \
	scp reports/*.html jpapouse@zimodej.cz:/var/www/zimodej.cz/subdomeny/geodata
