SSH_CONNECTION=51bb5930500446923f000201@geography-conqueror.rhcloud.com

target/download:
	mkdir -p target/download; \
	cd target/download; \
	git clone git@github.com:kartograph/kartograph.py.git; \
	cd kartograph.py; \
	python setup.py build; \
	cd ..; \
	wget https://github.com/mapnik/mapnik/wiki/data/110m-admin-0-countries.zip -O geoshapes.zip; \
	mkdir geoshapes; \
	unzip geoshapes.zip -d geoshapes; \
	ssh $(SSH_CONNECTION) -t '/var/lib/openshift/51bb5930500446923f000201/app-root/runtime/repo/wsgi/openshift/manage.py dumpdata questions.answer > /tmp/data.answers.json' && \
	scp $(SSH_CONNECTION):/tmp/data.answers.json answers.json; \
	ssh $(SSH_CONNECTION) -t '/var/lib/openshift/51bb5930500446923f000201/app-root/runtime/repo/wsgi/openshift/manage.py dumpdata core.place > /tmp/data.places.json' && \
	scp $(SSH_CONNECTION):/tmp/data.places.json places.json;

target/external-libs: target/download
	rm -rf target/external-libs; \
	mkdir -p target/external-libs; \
	cp -r target/download/kartograph.py/build/*/kartograph target/external-libs

target/data: target/download
	rm -rf target/data; \
	echo $(SSH_CONNECTION); \
	mkdir -p target/data; \
	python prepare-data.py; \
	for EXT in shp dbf prj shx; do \
		cp "target/download/geoshapes/ne_110m_admin_0_countries.$$EXT" "target/data/world.$$EXT"; \
	done

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
