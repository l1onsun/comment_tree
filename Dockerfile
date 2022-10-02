FROM python:3.10-slim AS python-base

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code/

ENV PIP_CACHE_DIR /root/.cache/pip
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

ENV BUILDER_INSTALL_PREFIX=/install

WORKDIR /code/


FROM python-base as builder

COPY requirements.txt ./
RUN --mount=type=cache,target=${PIP_CACHE_DIR} pip install \
    --prefix=${BUILDER_INSTALL_PREFIX} -r requirements.txt

FROM python-base as app

COPY --from=builder ${BUILDER_INSTALL_PREFIX} /usr/local

COPY happy_predictions ./happy_predictions

CMD ["uvicorn", "happy_predictions.asgi:app", "--host", "0.0.0.0", "--port", "8443"]

# ToDo: split core and test dependencies, add testing layers
#FROM app as app-dev
#COPY requirements-dev.txt ./