# Stage 1: Base Image
FROM python:3.9-slim-buster as base
RUN apt-get update && \
    apt-get install --no-install-recommends --yes curl netcat libpq-dev
RUN pip install --upgrade pip pip-tools
RUN mkdir /app

# Stage 2: Builder
FROM base as builder
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN apt-get update && apt-get install --yes --no-install-recommends \
    build-essential autoconf automake libtool pkg-config libc++-dev git libffi-dev

COPY requirements /app/requirements
COPY setup.py /app
RUN cd /app && pip install -r requirements/requirements.txt .;

# Stage 3: App Image
FROM base
COPY --from=builder /usr/local /usr/local
COPY . /app
RUN chmod +x /app/run.sh
WORKDIR /app
EXPOSE 3000
CMD ["/app/run.sh"]
