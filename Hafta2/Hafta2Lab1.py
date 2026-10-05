#Gri goruntu okuma ve kaydetme

import cv2
import os

giris_yolu= r"C:\Users\USER\Downloads\images.jpg"
klasor=r"C:\Users\USER\Desktop\Goruntu Isleme\Hafta2"

os.makedirs(klasor, exist_ok=True)
gri=cv2.imread(giris_yolu,0)


if gri is None:
    print("Görüntü yüklenemedi. Lütfen dosya yolunu kontrol edin.")
    raise SystemExit

print("Boyut:",gri.shape, "|Tip:", gri.dtype)

kayit_yolu=os.path.join(klasor,"gri_goruntu.jpg")

basarili, tampon=cv2.imencode(".jpg",gri)
if basarili:
    tampon.tofile(kayit_yolu)
    print("Görüntü başarıyla kaydedildi:",kayit_yolu)
    print("dosya var mi:",os.path.exists(kayit_yolu))
else:
    print("Görüntü kaydedilemedi.")

cv2.imshow("Gri Goruntu",gri)
cv2.waitKey(0)
cv2.destroyAllWindows()

