import data from "./data.json" assert { type: "json" };
//document.getElementById('main').innerHTML = JSON.stringify(data);
//console.log(data)
/*
const payload = {
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
};
 */
//console.log(payload);
const apikey = "zRtetzWK3KnRe7MD";
const nonce = "oqbnpshpb9g520ly38386y";
const timestamp = "1635759189540";
const secret = "wZVQKuYITGzKCPAAtdsHJ120pDixNL93";

// calculate the signature
var reqObj = JSON.stringify(data);
var signatureString = "/verify/" +
                      "data=" + reqObj + ";" +
                      "key=" + apikey + ";" +
                      "nonce=" + nonce + ";" +
                      "timestamp=" + timestamp + ";";

var hash = CryptoJS.HmacSHA256(signatureString, secret);
var hashInBase64 = CryptoJS.enc.Hex.stringify(hash);
//pm.environment.set("signature", hashInBase64);

console.log(signatureString,hash);
document.getElementById('main').innerHTML = hash + "<br>" + signatureString
//document.getElementById('main').innerHTML = signatureString