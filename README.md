# Affinidi login demo with Django

This is a python Application that showcases how to integrate Affinidi Login & Iota.


First, copy `.env.example` to `.env`:

```
cp .env.example .env
```

## Install

Install the required dependencies:

```
pip install -r requirements.txt
```

Add Affinidi TDK packages from local reference

*Note*: Stay tuned once we publish Affinidi TDK Python modules to the Python Package Index (PyPI) repository.

```
pip install affinidi-tdk-dist/python/affinidi_tdk_auth_provider-1.12.0-py3-none-any.whl affinidi-tdk-dist/python/affinidi_tdk_iota_core-1.2.0-py3-none-any.whl affinidi-tdk-dist/python/affinidi_tdk_credential_issuance_client-1.0.0-py3-none-any.whl  pydantic==1.10.5 --force-reinstall

```


## Create Login Configuration and update .env

1. Follow [this guide](./docs/setup-login-config.md) to set up your login configuration with callback URL as `http://localhost:8000/callback`

2. Copy your **Client ID**, **Client Secret** and **Issuer** from your login configuration and paste them into your `.env` file:

```ini
PROVIDER_CLIENT_ID="<CLIENT_ID>"
PROVIDER_CLIENT_SECRET="<CLIENT_SECRET>"
PROVIDER_ISSUER="<ISSUER>"
```

## Setup Personal Access Token

Affinidi API's expects an authorization token, Follow [this guide](./docs/create-pat.md) to set up your Personnel Access Token


## Set up your Affinidi Iota configuration

1. Follow [this guide](./docs/setup-iota-config.md) to set up your iota configuration

2. Copy your **Configuration ID** and **Query ID** for relevant iota queries and paste them into your `.env` file:

```ini
IOTA_CONFIG_ID="Iota Configuration ID"
IOTA_QUERY_ID_ADDRESS=""
```

## Run

```
python manage.py migrate
```

Start server with:

```
python manage.py runserver
```

Then visit: http://localhost:8000




