.PHONY: install data index dev test eval warm deploy

install:
	uv pip install -r requirements.txt || pip install -r requirements.txt

data:
	PYTHONPATH=. python3 scripts/01_download_data.py
	PYTHONPATH=. python3 scripts/02_normalize_catalog.py
	PYTHONPATH=. python3 scripts/03_normalize_shades.py
	PYTHONPATH=. python3 scripts/04_index_products.py
	PYTHONPATH=. python3 scripts/05_build_cooccurrence.py

index:
	PYTHONPATH=. python3 scripts/04_index_products.py

dev:
	PYTHONPATH=. uvicorn app.main:app --reload

test:
	pytest -v

eval:
	PYTHONPATH=. python3 scripts/run_eval.py

warm:
	PYTHONPATH=. python3 scripts/07_warm_cache.py

deploy:
	gcloud run deploy glowmatch \
		--source . \
		--region asia-south1 \
		--allow-unauthenticated \
		--memory 4Gi \
		--cpu 2 \
		--concurrency 8 \
		--timeout 60 \
		--max-instances 3 \
		--min-instances 0 \
		--set-env-vars "ENV=production,QDRANT_MODE=cloud" \
		--set-secrets "GEMINI_API_KEY=gemini-key:latest,MONGO_URI=mongo-uri:latest"
