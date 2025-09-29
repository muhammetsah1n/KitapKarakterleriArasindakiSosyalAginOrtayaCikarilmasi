# Proje
- Social Network Analysis Yöntemi ile Kitap Karakterleri Arasındaki Sosyal Ağın Ortaya Çıkarılması

## Amaç/Motivasyon
- Sosyal Ağ Analizi konusunu gerçek bir metin üzerinden uygulayarak pratikle pekiştirmek.
  
- Bu motivasyonla, seçtiğimiz bir kitabın (Harry Potter ve Felsefe Taşı) karakterleri ve karakterler arasındaki etkileşimleri veri olarak işleyip, bu karakterlerin sosyal yapısını ağ teorisiyle ortaya çıkarmayı hedefledik.

## Yöntem
- İlk olarak, seçilen kitap PDF formatında PyMuPDF (fitz) kütüphanesi kullanılarak okunmuş ve sayfalardan düz metin halinde içerik elde edilmiştir.

- Ardından, spaCy adlı doğal dil işleme kütüphanesi kullanılarak kitap içerisindeki kişi isimleri (PERSON etiketli varlıklar) otomatik olarak tespit edilmiştir.

- Bu aşamada çıkarılan isimler, re modülü (regular expressions) yardımıyla temizleme işlemine tabi tutulmuştur. İsimlerin başındaki unvanlar (örneğin Mr., Professor) kaldırılmış;'s gibi ekler ve özel karakterler metinden ayıklanmıştır.

- Ayrıca, aynı kişiyi temsil eden ancak farklı uzunlukta geçen isimlerin (örneğin Harry ve Harry Potter) çakışmasını önlemek amacıyla alt küme çıkarımı uygulanmıştır.

- Kalan isimler, kullanıcıya interaktif bir onay süreciyle tek tek gösterilmiş, onaylanan isimler “characters.txt” dosyasına kaydedilmiştir.

- Karakterler arası ilişkilerin çıkarılmasında, kitap paragraflar bazında analiz edilmiş ve aynı paragraf içinde birlikte geçen karakterler birbiriyle bağlantılı kabul edilmiştir. Bu bağlantılar üzerinden bir co-occurrence (birlikte geçme) ağı oluşturulmuş ve bağlantıların sıklığına göre kenar ağırlıkları hesaplanmıştır.

## Özellikler
- Herhangi bir kitap ile çalışma. (Bunun için kodlardaki kitap isimlerinin güncellenmesi yeterlidir.)

- Ayrıca ele alınan kitap ile ilgili olacak şekilde "titles" dizisi de güncellenebilir.
  
## Yorumlama
- Ağ grafiği, karakterler arasındaki sıkı ve yoğun etkileşimleri net şekilde ortaya koydu.
- Harry Potter gibi merkezilik değerleri yüksek karakterler, hikayede kritik rol oynuyor.
- Derece merkeziliği, en çok doğrudan bağlantıya sahip karakterleri gösterdi.
- Aracılık merkeziliği, etkileşimlerin yayılmasında köprü konumundaki karakterleri belirledi.
- Yakınlık merkeziliği, karakterlerin ağdaki hızlı erişim noktalarını ortaya koydu.
- Ağ yoğunluğu, karakterler arasındaki sosyal bağların sıkı olduğunu gösterdi

  
