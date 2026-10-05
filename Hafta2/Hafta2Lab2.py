#Gri tonlamalı bir resmi renkli hale getirme ve renkli harita uygulamak ve kaydetme

import cv2
import os

kaynak= r"C:\Users\USER\Downloads\images.jpg"
gri=cv2.imread(kaynak,cv2.IMREAD_GRAYSCALE)

renkli=cv2.cvtColor(gri,cv2.COLOR_GRAY2BGR)
renkli_harita=cv2.applyColorMap(gri,cv2.COLORMAP_JET)
cv2.imshow("GRAY2BGR",renkli)
cv2.imshow("COLORMAP",renkli_harita)

cv2.imwrite(os.path.join(r"C:\Users\USER\Desktop\Goruntu Isleme\Hafta2","gri_to_renkli.jpg"),renkli)
cv2.imwrite(os.path.join(r"C:\Users\USER\Desktop\Goruntu Isleme\Hafta2","gri_to_renkli_harita.jpg"),renkli_harita)

cv2.waitKey(0)
cv2.destroyAllWindows()