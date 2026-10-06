"""
Görsel Programlama Dersi - Görüntü İşleme Masaüstü Uygulaması
-------------------------------------------------------------
Bu uygulama; Python, OpenCV (cv2), NumPy ve Tkinter kullanılarak geliştirilmiştir.
Dış bir GUI kütüphanesi veya Pillow (PIL) kullanılmamıştır. Görüntüler, bellek
üzerinde doğrudan PNG formatına kodlanıp base64 verisi üzerinden Tkinter PhotoImage 
nesnesine aktarılarak ekranda görüntülenir.

Önemli Temel Kavramlar:
1. Renk Uzayı Sırası (BGR):
   OpenCV, görüntüleri standart RGB yerine BGR (Blue-Green-Red / Mavi-Yeşil-Kırmızı)
   sırasıyla okur ve işler.
2. NumPy Matris İndeksleme Mantığı:
   Görüntüler bellekte 2 veya 3 boyutlu NumPy dizileri (ndarrays) olarak tutulur.
   İndeksleme sırası Kartezyen koordinat sistemindeki (x, y) gibi değil,
   matris gösterimi olan [satır(y), sütun(x), kanal(c)] sırasındadır:
     - 1. indeks: Yükseklik / Satır (y koordinatı)
     - 2. indeks: Genişlik / Sütun (x koordinatı)
     - 3. indeks: Renk Kanalı (0: Mavi/B, 1: Yeşil/G, 2: Kırmızı/R)
"""

import os
import random
import base64
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np

# ==============================================================================
# UYGULAMA SABİTLERİ (CONSTANTS)
# ==============================================================================
# Ekranda gösterilecek görüntünün en-boy oranı korunarak sığdırılacağı maksimum boyutlar:
MAKS_GOSTERIM_GENISLIK = 900
MAKS_GOSTERIM_YUKSEKLIK = 800

# Eklenecek siyah blokların piksel cinsinden kenar uzunluğu ve adedi:
BLOK_BOYUTU = 10
BLOK_ADEDI = 2  # Her tıklamada görüntünün rastgele konumlarına eklenecek blok sayısı


class App:
    """
    Ana Masaüstü Görüntü İşleme Uygulaması Sınıfı.
    Arayüz elemanlarını, görüntü işleme metotlarını ve olay yönetimini barındırır.
    """

    def __init__(self, root: tk.Tk):
        """Uygulama penceresini ve bileşenlerini başlatır."""
        self.root = root
        self.root.title("Görsel Programlama - Görüntü İşleme Laboratuvarı")
        self.root.geometry("1050x700")
        self.root.minsize(850, 550)
        self.root.configure(bg="#f4f5f7")

        # ----------------------------------------------------------------------
        # GÖRÜNTÜ DEĞİŞKENLERİ
        # ----------------------------------------------------------------------
        # self.original_image: Dosyadan ilk okunan renkli ham görüntü (referans kopya).
        #                      Filtre ve dönüşümler bu görüntüyü doğrudan bozmaz.
        self.original_image = None

        # self.current_image: Üzerinde filtreler ve işlemler yapılan çalışma görüntüsü.
        #                     Tüm işlemler her zaman tam çözünürlüklü bu veri üzerinde yapılır.
        # self.bloksuz_goruntu: Blok eklenmeden önceki temiz görüntüyü saklar.
        #                       Butona tekrar tekrar basıldığında blokların üst üste birikmesini (2->4->6)
        #                       önler ve daima tam olarak 2 blok kalmasını sağlar.
        self.bloksuz_goruntu = None

        # self.tk_image: Tkinter Label üzerinde gösterilen PhotoImage nesnesinin referansı.
        #                Python Garbage Collector'ın (çöp toplayıcı) görseli bellekten
        #                silmesini önlemek için sınıf niteliği olarak saklanmalıdır.
        self.tk_image = None

        # ----------------------------------------------------------------------
        # BUTON LİSTESİ (GENİŞLETİLEBİLİR YAPI)
        # ----------------------------------------------------------------------
        # Projeye her hafta yeni bir özellik eklemek için:
        # 1. Yeni bir metot tanımlayın (örn. def negatif_al(self): ...).
        # 2. Aşağıdaki listeye ("Buton Başlığı", self.yeni_metot) şeklinde ekleyin.
        self.BUTONLAR = [
            ("Görüntü Aç", self.goruntu_ac),
            ("Renkli → Gri", self.renkli_to_gri),
            ("Gri → Renkli (Orijinal)", self.gri_to_renkli),
            (f"{BLOK_BOYUTU}x{BLOK_BOYUTU} Rastgele Blok Ekle", self.blok_ekle),
            ("Kaydet (PNG)", self.goruntu_kaydet),
        ]

        # Arayüzü oluştur
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Pencere düzenini (sol panel, sağ görüntüleme alanı, durum çubuğu) kurar."""
        # 1. Sol Buton Paneli
        self.sol_panel = tk.Frame(self.root, width=220, bg="#2c3e50", padx=15, pady=15)
        self.sol_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.sol_panel.pack_propagate(False)  # Sabit genişliği koru

        panel_baslik = tk.Label(
            self.sol_panel,
            text="İŞLEMLER",
            font=("Helvetica", 13, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50",
            pady=10
        )
        panel_baslik.pack(fill=tk.X, pady=(0, 10))

        # Butonları dinamik olarak listeden oluştur
        for yazi, komut in self.BUTONLAR:
            btn = tk.Button(
                self.sol_panel,
                text=yazi,
                command=komut,
                font=("Helvetica", 10),
                bg="#34495e",
                fg="#ffffff",
                activebackground="#1abc9c",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                pady=8,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=4)

        # 2. Alt Durum Çubuğu (Status Bar)
        self.durum_cubugu = tk.Label(
            self.root,
            text="Hazır. Lütfen 'Görüntü Aç' butonuna tıklayarak bir görüntü seçin.",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#e2e8f0",
            fg="#2d3748",
            font=("Helvetica", 9),
            padx=10,
            pady=4
        )
        self.durum_cubugu.pack(side=tk.BOTTOM, fill=tk.X)

        # 3. Sağ Görüntü Alanı
        self.sag_alan = tk.Frame(self.root, bg="#1e293b")
        self.sag_alan.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Görüntünün yerleşeceği etiket (Label)
        self.resim_etiketi = tk.Label(
            self.sag_alan,
            text="Görüntü yüklenmedi\nLütfen sol panelden bir resim seçin",
            font=("Helvetica", 12),
            fg="#94a3b8",
            bg="#1e293b"
        )
        self.resim_etiketi.pack(expand=True)

    # ==========================================================================
    # YARDIMCI METOTLAR (COMMON HELPERS)
    # ==========================================================================

    def goruntu_kontrol(self) -> bool:
        """
        Herhangi bir görüntü işleme adımı çağrıldığında bellekte görüntü olup
        olmadığını kontrol eder. Görüntü yoksa kullanıcıya uyarı penceresi gösterir.
        """
        if self.current_image is None:
            messagebox.showwarning(
                "Görüntü Bulunamadı",
                "Bu işlemi gerçekleştirmek için önce 'Görüntü Aç' butonu ile bir resim seçmelisiniz!"
            )
            return False
        return True

    def goruntuyu_goster(self):
        """
        Mevcut çalışma görüntüsünü (self.current_image) ekrana çizer.
        - İşlemler orijinal çözünürlükteki 'self.current_image' üzerinde kalır.
        - Yalnızca ekranda gösterim için görüntü MAKS_GOSTERIM boyutlarına sığacak şekilde küçültülür.
        - Pillow KULLANILMAZ: cv2.imencode ile PNG baytlarına dönüştürülüp
          base64 formatı üzerinden tk.PhotoImage'a aktarılır.
        """
        if self.current_image is None:
            return

        h, w = self.current_image.shape[:2]
        kanal_sayisi = self.current_image.shape[2] if len(self.current_image.shape) == 3 else 1

        # Görüntü ekrana sığacak şekilde küçültme oranını hesapla (en-boy oranını koru)
        oran = min(MAKS_GOSTERIM_GENISLIK / w, MAKS_GOSTERIM_YUKSEKLIK / h, 1.0)
        yeni_w = int(w * oran)
        yeni_h = int(h * oran)

        if oran < 1.0:
            # INTER_AREA: Görüntü küçültmede en kaliteli ve pürüzsüz sonucu veren enterpolasyon
            gosterim_resmi = cv2.resize(self.current_image, (yeni_w, yeni_h), interpolation=cv2.INTER_AREA)
        else:
            gosterim_resmi = self.current_image

        # ----------------------------------------------------------------------
        # PILLOW KULLANMADAN TKINTER'A AKTARIM:
        # 1. cv2.imencode ile bellekteki NumPy matrisi PNG bayt dizisine kodlanır.
        # 2. Elde edilen baytlar base64 formatına çevrilir.
        # 3. tk.PhotoImage(data=base64_str) ile doğrudan GUI nesnesine dönüştürülür.
        # ----------------------------------------------------------------------
        basarili, tampon = cv2.imencode(".png", gosterim_resmi)
        if not basarili:
            messagebox.showerror("Hata", "Görüntü arayüz için kodlanırken bir sorun oluştu.")
            return

        b64_veri = base64.b64encode(tampon).decode("utf-8")
        self.tk_image = tk.PhotoImage(data=b64_veri)

        # Label bileşenine görseli bas ve metni temizle
        self.resim_etiketi.config(image=self.tk_image, text="")

        # Durum çubuğuna teknik detayları yaz
        self.durum_cubugu.config(
            text=f"Gerçek Çözünürlük: {w}x{h} px | Kanal: {kanal_sayisi} (BGR) | "
                 f"Ekran Gösterimi: {yeni_w}x{yeni_h} px (Ölçek: %{int(oran*100)})"
        )

    # ==========================================================================
    # BUTON İŞLEM METOTLARI
    # ==========================================================================

    def goruntu_ac(self):
        """
        Dosya seçme penceresi açar ve seçilen resmi renkli (BGR) olarak okur.
        Orijinal görüntüyü 'self.original_image' içinde saklar,
        tüm işlemler için 'self.current_image' kopyasını oluşturur.
        """
        dosya_yolu = filedialog.askopenfilename(
            title="Bir Görüntü Dosyası Seçin",
            filetypes=[
                ("Görüntü Dosyaları", "*.png *.jpg *.jpeg *.bmp"),
                ("PNG Dosyaları (*.png)", "*.png"),
                ("JPEG Dosyaları (*.jpg;*.jpeg)", "*.jpg;*.jpeg"),
                ("Bitmap Dosyaları (*.bmp)", "*.bmp"),
                ("Tüm Dosyalar", "*.*")
            ]
        )

        if not dosya_yolu:
            return  # Kullanıcı seçim yapmadan iptal etti

        # ----------------------------------------------------------------------
        # KRİTİK TEKNİK NOKTA (WINDOWS TÜRKÇE KARAKTER DESTEĞİ):
        # Standart cv2.imread(dosya_yolu) fonksiyonu Windows işletim sisteminde
        # dosya yolunda 'ç, ğ, ı, ö, ş, ü' gibi karakterler olduğunda hata vermeden
        # sessizce 'None' döndürür.
        # Çözüm: Dosyayı önce Python ve NumPy ile ikili bayt (binary byte) olarak okuyup,
        # ardından cv2.imdecode ile bellekte çözmektir.
        # ----------------------------------------------------------------------
        try:
            veri = np.fromfile(dosya_yolu, dtype=np.uint8)
            resim = cv2.imdecode(veri, cv2.IMREAD_COLOR)

            if resim is None:
                messagebox.showerror("Hata", "Seçilen dosya geçerli bir görüntü olarak okunamadı.")
                return

            # Orijinal renkli görüntüyü koru ve çalışma kopyasını hazırla
            self.original_image = resim
            self.current_image = resim.copy()
            self.bloksuz_goruntu = None

            # Ekranda göster
            self.goruntuyu_goster()

        except Exception as e:
            messagebox.showerror("Okuma Hatası", f"Dosya okunurken bir hata oluştu:\n{e}")

    def renkli_to_gri(self):
        """
        Renkli BGR görüntüyü gri tonlamalıya (Grayscale) dönüştürür.
        Dönüşüm sonrası veri tipi ve kanal tutarlılığı için tekrar 3 kanallı
        GRAY2BGR formatına çevrilir.
        """
        if not self.goruntu_kontrol():
            return

        # 1. Adım: cv2.COLOR_BGR2GRAY ile 3 kanallı renkli matris, tek kanallı gri matrise çevrilir.
        #    Matematiksel Formül (Standart Parlaklık / Luminance):
        #    Gri = 0.114 * Blue + 0.587 * Green + 0.299 * Red
        gri = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)

        # 2. Adım: Gri görüntüyü tekrar 3 kanala (GRAY2BGR) çoğaltıyoruz.
        #    NEDENİ: Blok ekleme gibi işlemlerde matrisin [y, x, c] 3 kanal yapısını
        #    korumak, boyut uyuşmazlığı hatalarını önlemek ve pipeline tutarlılığı sağlamaktır.
        #    Burada 3 kanala da aynı gri değer kopyalanır (R=G=B=Gri).
        self.current_image = cv2.cvtColor(gri, cv2.COLOR_GRAY2BGR)
        self.bloksuz_goruntu = None

        self.goruntuyu_goster()

    def gri_to_renkli(self):
        """
        Griye dönüştürülmüş görüntüyü ilk açılan orijinal renkli haline geri getirir.
        
        TEORİK AÇIKLAMA (HOCAYA SUNUM İÇİN):
        -----------------------------------
        Renkli bir görüntü griye (grayscale) dönüştürüldüğünde, 3 kanaldaki
        (Mavi, Yeşil, Kırmızı) bağımsız renk bilgisi tek bir parlaklık değerine
        indirgenir. Bu işlem matematiksel olarak 'Geri Döndürülemez Bilgi Kaybı'
        (Lossy / Many-to-One mapping) içerir.
        Yani tek bir gri değer (örneğin 128), sonsuz farklı (B, G, R) kombinasyonunun
        ağırlıklı toplamından oluşmuş olabilir. Hangi pikselin gerçekte hangi renkte
        olduğunu salt gri değerden geri hesaplamak matematiksel olarak İMKÂNSIZDIR.
        Bu nedenle gerçek renkleri geri yüklemenin tek yolu, dosya ilk açıldığında
        sakladığımız 'self.original_image' referans kopyasını tekrar geri yüklemektir.
        """
        if not self.goruntu_kontrol():
            return

        # Saklanan orijinal görüntüyü kopyalayarak çalışma alanına aktar
        self.current_image = self.original_image.copy()
        self.bloksuz_goruntu = None

        self.goruntuyu_goster()

    def blok_ekle(self):
        """
        Görüntünün rastgele konumlarına BLOK_ADEDI adet BLOK_BOYUTUxBLOK_BOYUTU (10x10)
        boyutunda siyah (değeri 0) blok yerleştirir.
        
        Sınır Kontrolü:
        Rastgele seçilen (x, y) başlangıç noktalarına blok boyutu eklendiğinde
        görüntü sınırları dışına taşma (IndexError / out of bounds) olmaması için
        koordinatlar [0, h - bh] ve [0, w - bw] aralığında sınırlandırılır.
        """
        if not self.goruntu_kontrol():
            return

        # Blokların üst üste birikmesini (2 -> 4 -> 6) önleme mantığı:
        # Eğer butona ilk kez basılıyorsa o anki görüntünün temiz halini sakla.
        # Eğer butona tekrar basılıyorsa önce görüntüyü temiz haline döndür,
        # böylece ekranda her zaman tam olarak BLOK_ADEDI (2) blok kalır.
        if self.bloksuz_goruntu is None:
            self.bloksuz_goruntu = self.current_image.copy()
        else:
            self.current_image = self.bloksuz_goruntu.copy()

        # Görüntünün yükseklik (satır sayısı) ve genişlik (sütun sayısı) değerlerini al
        # shape[0] = yükseklik (y ekseni), shape[1] = genişlik (x ekseni)
        h, w = self.current_image.shape[:2]

        # Sınır kontrolü: Eğer görüntü blok boyutundan küçükse taşmayı önlemek için sınırla
        bh = min(BLOK_BOYUTU, h)
        bw = min(BLOK_BOYUTU, w)

        # Bloğun görüntünün dışına taşmaması için seçilebilecek maksimum başlangıç koordinatları:
        maks_y = max(0, h - bh)
        maks_x = max(0, w - bw)

        # Belirlenen sayıda (BLOK_ADEDI) rastgele blok yerleştir
        for i in range(BLOK_ADEDI):
            # Rastgele sol-üst köşe başlangıç koordinatları üret
            rastgele_y = random.randint(0, maks_y)
            rastgele_x = random.randint(0, maks_x)

            # ------------------------------------------------------------------
            # YÖNTEM 1: DİLİMLEME (NUMPY SLICING) - [HIZLI VE VEKTÖREL YÖNTEM]
            # NumPy indeksleme: [satır_aralığı, sütun_aralığı] -> [y:y+bh, x:x+bw]
            # BGR renk kanallarının tamamına 0 atanarak blok siyaha boyanır.
            # ------------------------------------------------------------------
            self.current_image[rastgele_y:rastgele_y + bh, rastgele_x:rastgele_x + bw] = 0

            # ------------------------------------------------------------------
            # YÖNTEM 2: İÇ İÇE DÖNGÜ (FOR LOOP) İLE PİKSEL PİKSEL DEĞER ATAMA
            # (Hocaya piksel adresleme ve Kartezyen uzay mantığını anlatmak için alternatif):
            # ------------------------------------------------------------------
            # for py in range(rastgele_y, rastgele_y + bh):     # y koordinatı (satırlar)
            #     for px in range(rastgele_x, rastgele_x + bw): # x koordinatı (sütunlar)
            #         # NumPy matrisinde [y, x] adresindeki pikselin tüm kanalları 0 (siyah) yapılır:
            #         self.current_image[py, px] = [0, 0, 0]
            # ------------------------------------------------------------------

        self.goruntuyu_goster()

    def goruntu_kaydet(self):
        """
        Üzerinde işlem yapılan mevcut görüntüyü PNG formatında kaydeder.
        
        TEKNİK NOT (NEDEN PNG?):
        PNG, kayıpsız (lossless) bir sıkıştırma formatıdır. JPEG gibi kayıplı
        formatlar köşelere eklediğimiz bloklardaki tam 0 olan siyah piksel
        değerlerini DCT (Ayrık Kosinüs Dönüşümü) sıkıştırması sebebiyle
        1, 2 veya 3 gibi değerlere bozabilir. PNG formatında ise 0 pikselleri
        kesinlikle tam 0 olarak korunur.
        """
        if not self.goruntu_kontrol():
            return

        dosya_yolu = filedialog.asksaveasfilename(
            title="Görüntüyü Kaydet",
            defaultextension=".png",
            filetypes=[("PNG Dosyası (*.png)", "*.png")]
        )

        if not dosya_yolu:
            return  # Kullanıcı kaydetmekten vazgeçti

        # ----------------------------------------------------------------------
        # KRİTİK TEKNİK NOKTA (TÜRKÇE KARAKTERLİ DOSYA YOLUNA KAYDETME):
        # cv2.imwrite doğrudan Türkçe karakterli Windows yollarında hata verebilir.
        # Bu yüzden önce cv2.imencode ile PNG baytlarına çevirip, ardından
        # tofile() ile diske güvenle yazıyoruz.
        # ----------------------------------------------------------------------
        try:
            basarili, kodlanmis_veri = cv2.imencode(".png", self.current_image)
            if basarili:
                kodlanmis_veri.tofile(dosya_yolu)
                messagebox.showinfo("Başarılı", "Görüntü kayıpsız PNG formatında başarıyla kaydedildi!")
            else:
                messagebox.showerror("Hata", "Görüntü PNG formatında kodlanamadı.")
        except Exception as e:
            messagebox.showerror("Kaydetme Hatası", f"Dosya kaydedilirken bir hata oluştu:\n{e}")


# ==============================================================================
# PROGRAM GİRİŞ NOKTASI (MAIN)
# ==============================================================================
if __name__ == "__main__":
    pencere = tk.Tk()
    uygulama = App(pencere)
    pencere.mainloop()
