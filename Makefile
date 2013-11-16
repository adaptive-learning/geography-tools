SSH_CONNECTION=51bb5930500446923f000201@geography-conqueror.rhcloud.com

.PHONY: target/reports target/maps

target/download:
	mkdir -p target/download; \
	cd target/download; \
	git clone git@github.com:kartograph/kartograph.py.git; \
	cd kartograph.py; \
	python setup.py build; \
	cd ..; \
	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip -O geoshapes.zip; \
	mkdir geoshapes; \
	unzip geoshapes.zip -d geoshapes; \
	ssh $(SSH_CONNECTION) -t '/var/lib/openshift/51bb5930500446923f000201/app-root/runtime/repo/wsgi/openshift/manage.py dumpdata questions.answer > /tmp/data.answers.json' && \
	scp $(SSH_CONNECTION):/tmp/data.answers.json answers.json; \
	ssh $(SSH_CONNECTION) -t '/var/lib/openshift/51bb5930500446923f000201/app-root/runtime/repo/wsgi/openshift/manage.py dumpdata core.place > /tmp/data.places.json' && \
	scp $(SSH_CONNECTION):/tmp/data.places.json places.json;

target/external-libs: target/download
	mkdir -p target/external-libs; \
	cp -r target/download/kartograph.py/build/*/kartograph target/external-libs

target/data: target/download
	mkdir -p target/data; \
	python prepare-data.py; \
	for EXT in shp dbf prj shx; do \
		cp "target/download/geoshapes/ne_110m_admin_0_countries.$$EXT" "target/data/world.$$EXT"; \
	done

target/reports: target/data notebooks/* libs/geodata/*
	mkdir -p target/reports; \
	cd notebooks; for NOTEBOOK in *.ipynb; do \
		BASENAME=`basename $$NOTEBOOK .ipynb`; \
		echo "$$BASENAME"; \
		runipy $$NOTEBOOK -q --pylab --html ../target/reports/$$BASENAME.html; \
	done;\

target/maps: scripts/maps_*.py target/data
	mkdir -p target/maps; \
	cd scripts; for SCRIPT in maps_*.py; do \
		BASENAME=`basename $$SCRIPT .py`; \
		echo "$$BASENAME"; \
		python "$$SCRIPT"; \
	done;

target/optimized: scripts/optimize_*.py target/data
	mkdir -p target/optimized; \
	cd scripts; for SCRIPT in optimize_*.py; do \
		BASENAME=`basename $$SCRIPT .py`; \
		echo "$$BASENAME"; \
		(python "$$SCRIPT") > "../target/optimized/$$BASENAME.txt"; \
	done;

target/video: target/maps
	mkdir -p target/video; \
	for DIR in target/maps/dynamic/*; do \
		VIDEO_NAME=`basename $$DIR`; \
		mkdir -p "target/video/$$VIDEO_NAME"; \
		for FILE in $$DIR/*.svg; do \
			echo "converting $$FILE"; \
			FILE_BASE=`basename "$$FILE" .svg`; \
			convert -density 1200 -resize 1600x900 "$$FILE" "target/video/$$VIDEO_NAME/$$FILE_BASE.png"; \
		done; \
	done

publish: target/reports target/maps target/optimized target/video
	ssh jpapouse@zimodej.cz -t "rm -rf /var/www/zimodej.cz/subdomeny/geodata/ && mkdir /var/www/zimodej.cz/subdomeny/geodata/ && (echo 'Options All +Indexes' > /var/www/zimodej.cz/subdomeny/geodata/.htaccess)"; \
	scp -r target/reports/ jpapouse@zimodej.cz:/var/www/zimodej.cz/subdomeny/geodata;
	scp -r target/maps/ jpapouse@zimodej.cz:/var/www/zimodej.cz/subdomeny/geodata;
	scp -r target/optimized/ jpapouse@zimodej.cz:/var/www/zimodej.cz/subdomeny/geodata;
	scp -r target/video jpapouse@zimodej.cz:/var/www/zimodej.cz/subdomeny/geodata;
