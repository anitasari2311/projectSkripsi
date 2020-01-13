import math

def namaKolom(jmlKolom):
	char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	if jmlKolom <=25:
		for i in range(jmlKolom):
			i = i+1
			kolom = char[i:i+1]+'8'
			print(kolom)
	else:
		i1 = math.floor(jmlKolom/len(char))-1
		i2 = ((jmlKolom - (math.floor(jmlKolom/len(char)) -1))-
			(25*(math.floor(jmlKolom/len(char)))))-1

		for i in range(jmlKolom):
			i=i+1
			kolom = char[i:i+1] + char[i:i+1]+'8'
			print(kolom)
		

# namaKolom(30)



def namaKolom2(jmlKolom):
	char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	for i in range(jmlKolom):
		i = i+1
		if jmlKolom <=25:
			kolom = char[i:i+1]+'8'
			print(kolom)
		else:
			i1 = math.floor(jmlKolom/len(char))-1
			i2 = ((jmlKolom - (math.floor(jmlKolom/len(char)) -1))-
				(25*(math.floor(jmlKolom/len(char)))))-1
			print(kolom = char[i:i+1] + 
				)
namaKolom2(28)