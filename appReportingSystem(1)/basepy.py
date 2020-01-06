import base64

data = "7f2rFS*2018"

# Standard Base64 Encoding
encodedBytes = base64.b64encode(data.encode("utf-8"))
encodedStr = str(encodedBytes, "utf-8")

encodedBytes2 = base64.b64encode(encodedStr.encode("utf-8"))
encodedStr2 = str(encodedBytes2, "utf-8")

decoded1=base64.b64decode(encodedStr2)
decodedStr1=str(decoded1,'utf-8')

decoded2=base64.b64decode(decodedStr1)
decodedStr2=str(decoded2,'utf-8')


print(encodedStr)
print(encodedStr2)

print(decodedStr1)
print(decodedStr2)