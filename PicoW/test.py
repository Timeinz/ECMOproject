import pyads1256

ads = pyads1256.ADS1256()

#ads.ReadADC()

myid = ads.ReadID()

print(myid)