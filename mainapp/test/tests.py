from django.test import TestCase
import hmac
import hashlib
import re
import json
import time
import requests

# Create your tests here.

# The API call path.
path = "/verify/"

# Test data
"""
data = {"details":{},"reference":"1"}
key = 'lj5YozlG6cv7mm6c'
test_timestamp = "1353987581461"
secret = "Ur7znqOTM1KuQw2gXBt0ShDqQcHVGsAq"
secret_byte = b'Ur7znqOTM1KuQw2gXBt0ShDqQcHVGsAq'
nonce ="1"
"""
# Access data

#data = {"details": {"address": {"suburb": "St Johns","street": "5 Strong Street","postcode": "1072","city": "Auckland","countryCode": "NZ"},"name": {"given": "Arnold","middle": "","family": "Schwarzenegger"},"dateofbirth": "1947-07-30","driverslicence": {"number": "AB123456","version": "111"}},"reference": "myref1","consent": "Yes"}
#key = "FnMpGxbIwl2bCOuZ"

f = open('data.json',)
data = json.load(f)
#data = {"details":{"address":{"suburb":"Hillsborough","street":"27 Indira Lane","postcode":"8022","city":"Christchurch"},"name":{"given":"Cooper","middle":"John","family":"Down"},"dateofbirth":"1978-01-10"},"consent":"Yes"}

key = "zRtetzWK3KnRe7MD"

#key = "lj5YozlG6cv7mm6c"
nonce ="1"
current_timestamp = int(time.time() * 1000)
print(current_timestamp)
test_timestamp = str(current_timestamp)
#secret = "gvcpAKfkuT48DGKS0fuc9KKHSMIKr44z"
#secret = "wZVQKuYITGzKCPAAtdsHJ120pDixNL93"

secret = "Ur7znqOTM1KuQw2gXBt0ShDqQcHVGsAq"

secret_byte = bytes(secret, 'utf-8')
return_url = "chaining-dev.cloudcheck.com.au"

# use json dumps to create the string from data obj
json_obj = json.dumps(data)
#print(json_obj)

# concaternate the string to create the super string ro signing
sign_str = path + "data=" + json_obj + ";" + "key=" + key + ";" + "nonce=" + nonce + ";" + "timestamp=" + test_timestamp + ";"

#sign_str = '/verify/data={"details":{"address":{"suburb":"St Johns","street":"5 Strong Street","postcode":"1072","city":"Auckland","countryCode":"NZ"},"name":{"given":"Arnold","middle":"","family":"Schwarzenegger"},"dateofbirth":"1947-07-30","driverslicence":{"number":"AB123456","version":"111"}},"reference":"myref1","consent":"Yes"};key=zRtetzWK3KnRe7MD;nonce=oqbnpshpb9g520ly38386y;timestamp=1635759189540;'


#sign_str = '/verify/data={"details":{},"reference":"1"};key=lj5YozlG6cv7mm6c;nonce=1;timestamp=1353987581461;'
sign_str = re.sub(": ",":",sign_str)
sign_str = re.sub(", ",",",sign_str)

print(sign_str)

encoded_sign_str = bytes(sign_str, 'utf-8')

# Create the HMAC SHA-256 Hash from the signature string.
signature = hmac.new(secret_byte, encoded_sign_str, hashlib.sha256).hexdigest()
print("signature = {0}".format(signature))

# Setup url and headers for API post request
url = "https://api.cloudcheck.co.nz/verify/"
headers = {
  'Content': 'application/x-www-form-urlencoded',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Cookie': 'com.xk72.webparts.csrf=sJ8aNdkPgMPAPMuk'
}

#final_str = "data=" + json_obj + "\nkey=" + key + "\nnonce=" + nonce + "\ntimestamp=" + test_timestamp + "\nsignature=" + signature
#print(final_str)
#final_data = json.loads(final_str)
#print(final_str)


final_data = {}
final_data["data"] = data
final_data["key"] = key
final_data["nonce"] = nonce
final_data["timestamp"] = test_timestamp
final_data["signature"] = signature
#final_data = sorted(final_data)
print(final_data)


post_call = requests.request("Post", url, headers=headers, data=final_data)
print(post_call.status_code,post_call.reason)
print(post_call.text)
print(post_call.content)


"""
curl --location --request POST 'https://api.cloudcheck.co.nz/verify/' \
--header 'Content: application/x-www-form-urlencoded' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'data={
    "details": {
        "address": {
            "suburb": "St Johns",
            "street": "5 Strong Street",
            "postcode": "1072",
            "city": "Auckland",
            "countryCode": "NZ"
        },
        "name": {
            "given": "Arnold",
            "middle": "",
            "family": "Schwarzenegger"
        },
        "dateofbirth": "1947-07-30",
        "driverslicence": {
            "number": "AB123456",
            "version": "111"
        }
    },
    "reference": "myref1",
    "consent": "Yes"
}' \
--data-urlencode 'key=zRtetzWK3KnRe7MD' \
--data-urlencode 'nonce={{nonce}}' \
--data-urlencode 'timestamp={{timestamp}}' \
--data-urlencode 'signature={{signature}}'
"""