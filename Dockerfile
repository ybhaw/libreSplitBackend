FROM python:3.12-slim-bookworm
WORKDIR /tmp
COPY requirements.txt /tmp
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt \
    && rm -rf /root/.cache/pip \
    && rm -rf /tmp/requirements.txt

COPY src /app
WORKDIR /app
EXPOSE 80
CMD ["litestar", "run", "--host", "0.0.0.0", "--port", "80"]
