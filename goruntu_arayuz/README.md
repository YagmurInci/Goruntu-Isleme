# Görsel Programlama - Görüntü İşleme Laboratuvarı Uygulaması

Bu proje, Python, OpenCV ve NumPy kullanılarak geliştirilmiş, Tkinter tabanlı modüler bir masaüstü görüntü işleme uygulamasıdır. Ders kapsamında her hafta yeni butonlar ve filtreler eklenerek genişletilebilecek sade bir mimariye sahiptir.

---

## 🛠️ Kurulum

Uygulamanın çalışması için sisteminizde **Python 3.10+** kurulu olmalıdır.

Terminal veya komut satırından proje dizinine gidip gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

*(Not: `requirements.txt` içerisinde yalnızca `opencv-python` ve `numpy` bulunur. Tkinter, Python ile birlikte kurulu gelen standart bir kütüphanedir. Harici Pillow/PIL kütüphanesi **kullanılmamıştır**.)*

---

## 🚀 Çalıştırma

Uygulamayı başlatmak için terminalde şu komutu çalıştırın:

```bash
python gorsel_arayuz.py
```

Uygulama açıldığında sol paneldeki **"Görüntü Aç"** butonuna basarak projenin ana dizininde hazır bulunan `ornek_resim.png` dosyasını veya bilgisayarınızdaki herhangi bir resmi seçebilirsiniz.

---

## 🧩 Mevcut Butonlar ve İşlevleri

1. **Görüntü Aç:** `png`, `jpg`, `jpeg`, `bmp` formatlarındaki görüntüleri BGR formatında okur. Orijinal kopyayı (`self.original_image`) saklarken çalışma kopyası (`self.current_image`) üzerinde işlem yapar.
2. **Renkli → Gri:** Görüntüyü `cv2.COLOR_BGR2GRAY` ile griye çevirir. Ardından kanal uyuşmazlığını önlemek için tekrar 3 kanala (`cv2.COLOR_GRAY2BGR`) genişletir.
3. **Gri → Renkli (Orijinal):** Orijinal saklanan renkli görüntüyü geri yükler.
4. **10x10 Rastgele Blok Ekle:** Görüntünün rastgele koordinatlarına 10x10 boyutunda siyah (değeri 0) bloklar yerleştirir. Dizi sınırları dışına taşmaması için `[0, h - 10]` ve `[0, w - 10]` aralıklarında sınır kontrolü yapılır.
5. **Kaydet (PNG):** Mevcut çalışma görüntüsünü kayıpsız PNG formatında diske kaydeder (böylece siyah piksel değerleri kesinlikle 0 olarak kalır).

---

## ➕ Yeni Buton / Özellik Nasıl Eklenir? (Haftalık Ödevler İçin)

Kod, nesne yönelimli ve liste döngülü tasarlandığı için yeni bir özellik eklemek sadece **iki basit adım** gerektirir:

### Örnek: "Görüntü Negatifi Alma" Butonu Ekleme

#### 1. Adım: Yeni İşlem Metodunu Tanımlayın
[gorsel_arayuz.py](file:///c:/Users/USER/Desktop/Goruntu%20Isleme/goruntu_arayuz/gorsel_arayuz.py) dosyası içerisindeki `App` sınıfına aşağıdaki metodu ekleyin:

```python
    def negatif_al(self):
        """Görüntünün renk negatifini alır (255 - piksel_değeri)."""
        # 1. Görüntü yüklü mü kontrol et
        if not self.goruntu_kontrol():
            return

        # 2. NumPy vektörel çıkarma işlemi ile tüm kanallardaki pikselleri tersine çevir
        self.current_image = 255 - self.current_image

        # 3. Sonucu ekrana yansıt
        self.goruntuyu_goster()
```

#### 2. Adım: `self.BUTONLAR` Listesine Ekleyin
`__init__` fonksiyonu içindeki `self.BUTONLAR` listesine tek satır ekleyin:

```python
        self.BUTONLAR = [
            ("Görüntü Aç", self.goruntu_ac),
            ("Renkli → Gri", self.renkli_to_gri),
            ("Gri → Renkli (Orijinal)", self.gri_to_renkli),
            ("Negatif Al", self.negatif_al),  # <-- YENİ EKLENEN BUTON
            (f"{BLOK_BOYUTU}x{BLOK_BOYUTU} Blok Ekle", self.blok_ekle),
            ("Kaydet (PNG)", self.goruntu_kaydet),
        ]
```

Arayüz bu listeyi otomatik okur ve butonu sol panelde oluşturarak fonksiyonunuza bağlar!

---

## 🔍 Önemli Teknik Detaylar (Hocaya Anlatım Notları)

- **Türkçe Karakter Güvenliği:** Windows'ta `cv2.imread` ve `cv2.imwrite` dosya yolunda Türkçe karakter (ş, ç, ğ, ı, ö, ü) olduğunda hata verir. Bu sorunu aşmak için dosyayı `np.fromfile` ile bayt olarak okuyup `cv2.imdecode` ile açıyor; kaydederken `cv2.imencode` sonrası `.tofile()` ile diske yazıyoruz.
- **Pillow Kullanmadan Gösterim:** Görüntü matrisi bellekte `cv2.imencode('.png', ...)` ile PNG baytlarına, oradan `base64` string'e çevrilerek doğrudan Tkinter'ın `tk.PhotoImage(data=b64)` nesnesine aktarılır.
- **Piksel Matris Düzeni:** NumPy'da indeksleme Kartezyen `(x, y)` değil; matris `[satır(y), sütun(x), kanal(c)]` biçimindedir.
- **Renk Sırası:** OpenCV renkleri RGB değil **BGR** (Mavi, Yeşil, Kırmızı) sırasında saklar.
- **Ekran Ölçekleme:** Büyük resimler ekrana sığması için sadece gösterim aşamasında küçültülür; filtreler ve pikseller üzerindeki tüm işlemler orijinal tam çözünürlüklü görüntü (`self.current_image`) üzerinde gerçekleştirilir.
