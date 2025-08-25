# from datetime import datetime
#
# import requests
# from jose import jwt
# from jose.exceptions import JWTError, ExpiredSignatureError
# from jwcrypto import jwk
#
# url = "https://firebaseappcheck.googleapis.com/v1/jwks"
# project_number = "135259686055"
#
#
# def fetch_jwks():
#     response = requests.get(url)
#     response.raise_for_status()
#     return response.json()
#
#
# jwks = None
#
#
# def get_public_key(kid):
#     global jwks
#     if jwks is None:
#         jwks = fetch_jwks()
#
#     for key in jwks['keys']:
#         if key['kid'] == kid:
#             return jwk.JWK(**key)
#     return None
#
#
# def token_verify(token: str) -> bool:
#     try:
#         decoded_jwt = jwt.get_unverified_header(token)
#         kid = decoded_jwt.get('kid')
#         public_key = get_public_key(kid)
#
#         if not public_key:
#             return False
#
#         verified_jwt = jwt.decode(token, public_key.export_to_pem(), algorithms=['RS256'], audience=f"projects/{project_number}")
#
#         # Ensure the token's header uses the algorithm RS256
#         if decoded_jwt.get('alg') != 'RS256':
#             return False
#
#         # Ensure the token's header has type JWT
#         if decoded_jwt.get('typ') != 'JWT':
#             return False
#
#         # Ensure the token is issued by App Check
#         if verified_jwt.get('iss') != f"https://firebaseappcheck.googleapis.com/{project_number}":
#             return False
#
#         # Ensure the token is not expired
#         if verified_jwt.get('exp') <= datetime.utcnow().timestamp():
#             return False
#
#         # Ensure the token's audience matches your project
#         if f"projects/{project_number}" not in verified_jwt.get('aud', []):
#             return False
#
#         return True
#
#     except (JWTError, ExpiredSignatureError):
#         return False
