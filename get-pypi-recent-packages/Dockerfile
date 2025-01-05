FROM alpine/git AS repo

ARG REPO_NAME=threatpatrols-workflows/github-actions
ARG REPO_BRANCH=dev

WORKDIR /repo
ADD "https://api.github.com/repos/${REPO_NAME}/commits/${REPO_BRANCH}?per_page=1" /last-commit.json
RUN git clone -b ${REPO_BRANCH} --single-branch --depth 1 https://github.com/${REPO_NAME}/github-actions.git .


FROM python:3-slim AS builder
ADD . /app
WORKDIR /app
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --target=/app -r requirements.txt


FROM python:3-slim
COPY --from=builder /app /app
COPY --from=repo /repo/shared/app/threatpatrols /app/threatpatrols

WORKDIR /app
ENV PYTHONPATH=/app
CMD ["python3", "/app/main.py"]
