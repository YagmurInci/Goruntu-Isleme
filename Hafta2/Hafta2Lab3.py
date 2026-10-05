#Renkili bir resmi gri tonlamaya çevirme ve kaydetme

import cv2
import os

kaynak= r"C:\Users\USER\Downloads\Original-image-512-512-3-RGB-colors-Color-figure-online.webp"

renkli=cv2.imread(kaynak,cv2.IMREAD_COLOR)
gri=cv2.cvtColor(renkli,cv2.COLOR_BGR2GRAY)

print("Boyut:",gri.shape, "|Tip:", gri.dtype)
cv2.imshow("Renkli",renkli)
cv2.imshow("Gri",gri)
kaydet=os.path.join(r"C:\Users\USER\Desktop\Goruntu Isleme\Hafta2","gri_goruntu.jpg")
cv2.waitKey(0)
cv2.destroyAllWindows()