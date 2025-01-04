FROM python:3-slim AS builder
ADD . /app
WORKDIR /app

# Install any requirements.txt
RUN pip install --target=/app -r requirements.txt

# https://github.com/GoogleContainerTools/distroless
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]
