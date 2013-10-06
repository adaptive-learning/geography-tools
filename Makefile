SSH_CONNECTION=51bb5930500446923f000201@geography-conqueror.rhcloud.com

reports: data notebooks
	rm -rf reports;
	mkdir reports;
	cd notebooks; for NOTEBOOK in *.ipynb; do \
		BASENAME=`basename $$NOTEBOOK`; \
		echo "$$BASENAME"; \
		./recompute-notebook.py "$$NOTEBOOK" "../reports/$$BASENAME"; \
		cd ../reports; \
		ipython nbconvert --to html "$$NOTEBOOK"; \
		cd -; \
		rm -rf ../reports/$$BASENAME; \
	done;\

data:
	echo $(SSH_CONNECTION); \
	mkdir data; \
	ssh $(SSH_CONNECTION) -t '/var/lib/openshift/51bb5930500446923f000201/app-root/runtime/repo/wsgi/openshift/manage.py dumpdata questions.answer > /tmp/data.answers.json' && \
	scp $(SSH_CONNECTION):/tmp/data.answers.json data/answers.json;
