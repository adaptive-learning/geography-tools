SSH_CONNECTION?=51bb5930500446923f000201@geography-conqueror.rhcloud.com
APP_ROOT?=/var/lib/openshift/51bb5930500446923f000201/app-root
MANAGE_ROOT?=${APP_ROOT}/runtime/repo/wsgi/openshift
DATA_ROOT?=${APP_ROOT}/data
GEOGRAPHY_MODEL?=answer place placerelation
EXTERNAL_LIBS?=kartograph


###############################################################################
# Preparation targets
###############################################################################

prepare.data: target/data/geoshapes $(foreach MODEL, $(GEOGRAPHY_MODEL), target/data/geography.$(MODEL).csv)

prepare.external-libs: $(foreach LIB, $(EXTERNAL_LIBS), target/external-libs/$(LIB))


###############################################################################
# Download data from third parties
###############################################################################

target/download:
	mkdir -p target/download; \

target/download/answers_csv.zip: | target/download
	cd target/download; \
	scp $(SSH_CONNECTION):${DATA_ROOT}/export_csv.zip ./answers_csv.zip;

target/download/geography.%.json: | target/download
	cd target/download; \
	ssh $(SSH_CONNECTION) -t '${MANAGE_ROOT}/manage.py dumpdata geography.$* > /tmp/geography.$*.json' && \
	scp $(SSH_CONNECTION):/tmp/geography.$*.json geography.$*.json;

target/download/geoshapes: | target/download
	cd target/download; \
	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip -O geoshapes.zip; \
	mkdir geoshapes; \
	unzip geoshapes.zip -d geoshapes;

target/download/kartograph.py: | target/download
	cd target/download; \
	git clone git@github.com:kartograph/kartograph.py.git; \
	cd kartograph.py; \
	python setup.py build;


###############################################################################
# External libraries
###############################################################################

target/external-libs:
	mkdir -p target/external-libs;

target/external-libs/kartograph: target/download/kartograph.py | target/external-libs
	cp -r target/download/kartograph.py/build/*/kartograph target/external-libs;


###############################################################################
# Data for analysis
###############################################################################

target/data:
	mkdir -p target/data;

target/data/geography.answer.csv: target/download/answers_csv.zip | target/data
	unzip target/download/answers_csv.zip -d target/data; \
	mv target/data/export.csv target/data/geography.answer.csv;

target/data/geography.%.csv: target/download/geography.%.json | target/data
	python json2csv.py geography.$* target/download/geography.$*.json target/data/geography.$*.csv;

target/data/geoshapes: target/download/geoshapes | target/data
	mkdir -p target/data/geoshapes; \
	for EXT in shp dbf prj shx; do \
		cp target/download/geoshapes/ne_110m_admin_0_countries.$$EXT target/data/geoshapes/world.$$EXT; \
	done;
