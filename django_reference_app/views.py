import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
import affinidi_tdk_auth_provider
import affinidi_tdk_iota_core
from asgiref.sync import async_to_sync
import affinidi_tdk_credential_issuance_client

oauth = OAuth()

oauth.register(
    "affinidi",
    client_id=settings.PROVIDER_CLIENT_ID,
    client_secret=settings.PROVIDER_CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid offline_access',
        'token_endpoint_auth_method': 'client_secret_post',
    },
    server_metadata_url=f"{
        settings.PROVIDER_ISSUER}/.well-known/openid-configuration",
)


def login(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    return oauth.affinidi.authorize_redirect(request, redirect_uri)


def callback(request):
    token = oauth.affinidi.authorize_access_token(request)
    request.session["user"] = token['userinfo']
    return redirect(request.build_absolute_uri(reverse("index")))


def logout(request):
    request.session.pop('user', None)
    return redirect('/')


def index(request):
    user = request.session.get("user")

    if user:
        email = user.get("email") or next((item["email"] for item in user["custom"]
                                           if isinstance(item.get("email"), str)), None)
    else:
        email = None

    if email is None:
        return render(
            request,
            "index.html"
        )
    else:
        return render(
            request,
            "loggedin.html",
            context={
                "email": email,
                "user": user,
                "pretty": json.dumps(user, indent=4),
            },
        )


def iota(request):
    user = request.session.get("user")

    if user:
        email = user.get("email") or next((item["email"] for item in user["custom"]
                                           if isinstance(item.get("email"), str)), None)
    else:
        return redirect('/')

    return render(
        request,
        "iota.html",
        context={
            "iotaAddressQueryId": settings.IOTA_QUERY_ID_ADDRESS,
            "email": email,
            "user": user,
        },
    )


def iotaCredentials(request):
    try:
        user = request.session.get("user")
        if user is None:
            return JsonResponse({'error': '401 Unauthorized access'}, status=401)

        did = user["sub"]

        stats = {
            'privateKey': settings.PRIVATE_KEY,
            'passphrase': settings.PASSPHRASE,
            'keyId': settings.KEY_ID,
            'tokenId': settings.TOKEN_ID,
            'projectId': settings.PROJECT_ID,
        }

        authProvider = affinidi_tdk_auth_provider.AuthProvider(stats)
        iotaToken = authProvider.create_iota_token(
            settings.IOTA_CONFIG_ID, did)
        print(iotaToken)

        iotaAuthProvider = affinidi_tdk_iota_core.IotaAuthProvider()
        iota_credentials = iotaAuthProvider.limited_token_to_iota_credentials(
            iotaToken.iota_jwt)

        print(iota_credentials)

        return JsonResponse({
            "connectionClientId": iota_credentials.connection_client_id,
            "credentials": {
                "accessKeyId": iota_credentials.credentials.access_key_id,
                "secretKey": iota_credentials.credentials.secret_key,
                "sessionToken": iota_credentials.credentials.session_token,
                "expiration": iota_credentials.credentials.expiration,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def issueVC(request):

    params = {
        'privateKey': settings.PRIVATE_KEY,
        'passphrase': settings.PASSPHRASE,
        'keyId': settings.KEY_ID,
        'tokenId': settings.TOKEN_ID,
        'projectId': settings.PROJECT_ID,
    }

    authProvider = affinidi_tdk_auth_provider.AuthProvider(params)
    projectScopeToken = authProvider.fetch_project_scoped_token()
    print(projectScopeToken)

    configuration = affinidi_tdk_credential_issuance_client.Configuration()
    configuration.api_key['ProjectTokenAuth'] = projectScopeToken

    with affinidi_tdk_credential_issuance_client.ApiClient(configuration) as api_client:
        api_instance = affinidi_tdk_credential_issuance_client.IssuanceApi(
            api_client)

        projectId = settings.PROJECT_ID
        request_json = {
            "data": [{
                "credentialTypeId": "InsuranceRegistration",
                "credentialData": {
                    "email": "paramesh.k@afffinid.com",
                    "name": "parmaesh",
                    "phoneNumber": "998016607",
                    "dob": "22/02/2010",
                    "gender": "Male",
                    "address": "Bangalore",
                    "postcode": "560103",
                    "city": "Bangalore",
                    "country": "India",
                }
            }],
            "holderDid": "did:key:holder-did-value",
            "claimMode": "NORMAL"
        }

        start_issuance_input = affinidi_tdk_credential_issuance_client.StartIssuanceInput.from_dict(
            request_json)

        print(start_issuance_input)

        api_response = api_instance.start_issuance(
            projectId, start_issuance_input=start_issuance_input)

        print(api_response)

        return JsonResponse({
            "credential_offer_uri": api_response.credential_offer_uri,
            "tx_code": api_response.tx_code,
            "issuance_id": api_response.issuance_id,
            "expires_in": api_response.expires_in,
        })
