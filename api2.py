import base64
from datetime import datetime
import requests
import hmac
import hashlib
import struct
import time


def getEncodedString(string):
    string = str(string)
    base64_bytes = base64.b64encode(string.encode("ascii"))
    return base64_bytes.decode("ascii")


def get_totp(secret, digits=6, interval=30):
    secret = secret.replace(" ", "").upper()
    secret += "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(secret)
    counter = struct.pack(">Q", int(time.time()) // interval)
    hmac_hash = hmac.new(key, counter, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 0x0F
    code = (struct.unpack(">I", hmac_hash[offset:offset + 4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)

URL_SEND_LOGIN_OTP="https://api-t2.fyers.in/vagator/v2/send_login_otp_v2"
res = requests.post(url=URL_SEND_LOGIN_OTP, json={"fy_id":getEncodedString(FY_ID),"app_id":"2"}).json()
print(res)

if datetime.now().second % 30 > 27 : 
    time.sleep(5)
    URL_VERIFY_OTP="https://api-t2.fyers.in/vagator/v2/verify_otp"
    res2 = requests.post(url=URL_VERIFY_OTP, json= {"request_key":res["request_key"],"otp":get_totp(TOTP_KEY)}).json()
    print(res2)

ses = requests.Session()
URL_VERIFY_OTP2="https://api-t2.fyers.in/vagator/v2/verify_pin_v2"
payload2 = {"request_key": res2["request_key"],"identity_type":"pin","identifier":getEncodedString(PIN)}
res3 = ses.post(url=URL_VERIFY_OTP2, json= payload2).json()
print(res3)


ses.headers.update({
'authorization': f"Bearer {res3['data']['access_token']}"})