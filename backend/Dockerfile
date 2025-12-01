FROM python:3.14-slim-bookworm

# Setup UV
# Using a distroless image which only contains uv binaries
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /expenses

WORKDIR /expenses
RUN uv sync --locked # Uses uv.lock for packages resolution

CMD [ "uv", "run", "fastapi", "run", "app/main.py" ]
