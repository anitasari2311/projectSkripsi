import base64

data = "7f2rFS*2018"

# Standard Base64 Encoding
encodedBytes = base64.b64encode(data.encode("utf-8"))
encodedStr = str(encodedBytes, "utf-8")

encodedBytes2 = base64.b64encode(encodedStr.encode("utf-8"))
encodedStr2 = str(encodedBytes2, "utf-8")

decoded2=base64.b64decode(encodedStr2)
decodedStr=str(decoded2,'utf-8')

decoded=base64.b64decode(decodedStr)
decodedSt2r=str(decoded,'utf-8')

print(decodedStr)
print(encodedStr)
print('========')
print(encodedStr2)

print(decodedSt2r)
