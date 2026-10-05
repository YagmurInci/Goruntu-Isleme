#Renkli bir resmi fonksiyon kullanmadan gri tonlamalı hale getirme ve kaydetme 

import cv2
import os
import numpy as np
from pathlib import Path

yol= r"C:\Users\USER\Downloads\Original-image-512-512-3-RGB-colors-Color-figure-online.webp"

renkli=cv2.imdecode(np.fromfile(yol,dtype=np.uint8),cv2.IMREAD_COLOR)

if renkli is None:
    print("Görüntü yüklenemedi. Lütfen dosya yolunu kontrol edin.", yol)
    raise SystemExit

#renkli gorutntunun shape'i (yukseklik,genislik,kanal sayisi) olur, yani 3 boyutlu
#bu yuzden 3 degisken 3 deger var. kanal sayisina ihtiyacimiz yok, _ ile atadik

yukseklik,genislik, _ =renkli.shape

#bos bir gri goruntu olusturma 8 bit tek kanal 
gri_ortalama=np.zeros((yukseklik,genislik),dtype=np.uint8)
gri_agirlik=np.zeros((yukseklik,genislik),dtype=np.uint8)

#her pikseli tek tek dolas
# int() ile ceviriyoruz piksel degerleri unit8 dir
# uc degeri toplarken 255 i asarsa tasar (basa sarar) ve yanlis sonuc cikar
for y in range(yukseklik):  # satirlar yukardan asagiya
    for x in range(genislik): # sutunlar soldan saga
        b = int(renkli[y,x,0]) #renkli kanal sirasi BGR oldugu icin 0. kanal mavi, 1. kanal yesil, 2. kanal kirmizi
        g = int(renkli[y,x,1])
        r = int(renkli[y,x,2])
        #yontem: basit ortalama
        gri_ortalama[y,x]=(b+g+r)//3

        #yontem2: agirlikli ortalama (standart formul: 0.299*R + 0.587*G + 0.114*B)
        gri_agirlik[y,x]=int(0.299*r + 0.587*g + 0.114*b)

        #kaydetme
kayit_yolu_ortalama=os.path.join(r"C:\Users\USER\Desktop\Goruntu Isleme\Hafta2","gri_ortalama.jpg")
kayit_yolu_agirlik=os.path.join(r"C:\Users\USER\Desktop\Goruntu Isleme\Hafta2","gri_agirlik.jpg")

print("Kaydedildi:",kayit_yolu_ortalama)
print("Kaydedildi:",kayit_yolu_agirlik)
print("renkli shape:",renkli.shape) # (y,x,3) 3 kanal oldugu icin 3 boyutlu
print("gri_ortalama shape:",gri_ortalama.shape) # (y,x) 2 boyutlu tek kanal
print("gri_agirlik shape:",gri_agirlik.shape)
print("gri ortalama veri tipi:",gri_ortalama.dtype)
print("gri agirlik veri tipi:",gri_agirlik.dtype)


cv2.imshow("orjinal Renkli",renkli)
cv2.imshow("Gri_ortalama",gri_ortalama)
cv2.imshow("Gri_agirlik",gri_agirlik)
cv2.waitKey(0) #bir tusa basana kadar bekle
cv2.destroyAllWindows() #tum pencereleri kapat