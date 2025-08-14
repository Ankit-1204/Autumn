FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# Copies the requirements.txt file from your local machine into the container at /app/requirements.txt.
# The . here means "put it in the current working directory" (which is /app now).
# We copy it before other files because it allows Docker to use layer caching:
# If your dependencies don’t change, Docker reuses the old image layer without reinstalling everything.
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
COPY . .

RUN chmod +x entrypoint.sh
# To make sure that alembic migration runs after the db is initialised.
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# "main:app" means:
# main → the Python file main.py (without .py extension).
# app → the FastAPI instance inside that file.
# "--host", "0.0.0.0" makes it listen on all network interfaces inside the container, so your local machine can access it.
# "--port", "8000" makes it available on port 8000.