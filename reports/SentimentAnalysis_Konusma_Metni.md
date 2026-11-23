# Karşılaştırmalı Duygu Analizi — Tam Konuşma Metni

Bu metin, `SentimentAnalysis_Sunum.pptx` dosyasının 6–6–6 düzenindeki 18 slaydının tamamıyla aynı sıradadır. Başlıklar ve bu giriş okunmaz; her slaydın altındaki paragraflar okunur. Konuşmacı geçişleri ve kapanış metnin içindedir. Slaytlar 1’den 18’e sırayla ilerletilir. Sonuç 17. slaytta, kaynakça ve son teşekkür 18. slayttadır.

Konuşmacılar: **Merve: 1–6. slaytlar. Kerem: 7–12. slaytlar. Hamza: 13–18. slaytlar.**

Metin **1.169 konuşma kelimesidir**. Dakikada yaklaşık 140 kelimelik okuma ve kısa geçişlerle hedef süre **8,3 dakika civarındadır**; gerçek süre okuma hızına bağlıdır. Her kişi yaklaşık üç dakika konuşur.

## Slayt 1 — Karşılaştırmalı Duygu Analizi
**Konuşmacı: Merve Cemre Akkuş**

Merhaba hocam, ben Merve Cemre Akkuş. Kerem Kalyoncu ve Hamza Taşbay’la birlikte hazırladığımız duygu analizi projesini sunacağız.

Projede İngilizce ve Türkçe yorumlar üzerinde VADER, BERT ve Claude’u karşılaştırdık; hangisi ne kadar başarılı, nerelerde hata yapıyor, buna baktık. Ben veri setlerini ve VADER’i anlatacağım, Kerem BERT’i, Hamza da LLM tabanlı sınıflandırmayı, yani Claude’u, ve genel sonucu. Sadece doğruluğa bakmadık; pozitif, negatif ve nötr yorumlarda yanlış tahminlerin nasıl dağıldığını da inceledik.

## Slayt 2 — Veri setleri ve sınıf dağılımları
**Konuşmacı: Merve Cemre Akkuş**

İngilizce için TweetEval’in SemEval kaynaklı resmî test verisini, Türkçe için Sercan Külcü’nün tweet veri setini kullandık. İkisi de daha önceden etiketlenmiş veri setleri.

Her dilden bin pozitif, bin negatif, bin nötr olmak üzere 3.000 yorum seçtik; yani toplamda 6.000 özgün yorum var. Sınıfları eşit tuttuk ki hata sayılarını aynı örnek sayısı üzerinden rahatça karşılaştırabilelim.

Bir not: Türkçe yorumların VADER için hazırladığımız İngilizce çevirileri yeni veri sayılmıyor; özgün yorum sayısı yine 6.000.

## Slayt 3 — Veri hazırlama ve ortak değerlendirme
**Konuşmacı: Merve Cemre Akkuş**

Önce veriyi temizledik: boş kayıtları, tekrar edenleri ve aynı metne farklı etiket verilmiş çelişkili kayıtları çıkardık. Sonra sabit bir kuralla her sınıftan bin yorum seçtik. Seçim sırasında model tahminlerini kullanmadık, kaynak etiketlerine de dokunmadık.

Üç yöntemi de aynı yorumlar üzerinde değerlendirdik. Doğruluk, doğru tahminlerin tüm yorumlara oranı. Sınıf bazlı hataları ise gerçek etikete göre saydık. Mesela nötr bir yorum pozitif tahmin edilmişse, bu nötr sınıfın hatası oluyor.

Kod tarafında hazırlama, tahmin ve değerlendirme ayrı çalışıyor; karşılaştırma ve hata analizi de kaydedilmiş tahmin dosyalarından üretiliyor.

## Slayt 4 — Üç yönteme genel bakış
**Konuşmacı: Merve Cemre Akkuş**

Üç yöntemin farkı kısaca şöyle: VADER duygu sözlüğü ve dil kurallarıyla çalışıyor. BERT için her dilde hazır bir duygu sınıflandırıcısı kullandık. Claude’a ise bir istem gönderip yorumu sınıflandırmasını istedik.

İngilizce yorumlar üç yönteme de olduğu gibi verildi. Türkçede VADER İngilizce çeviriyi, BERT ve Claude ise özgün Türkçe metni gördü. O yüzden VADER’in Türkçe sonucuna bakarken çevirinin etkisini de akılda tutmak gerekiyor.

## Slayt 5 — VADER: uygulama ve sonuçlar
**Konuşmacı: Merve Cemre Akkuş**

VADER, kelimelerin duygu puanlarını olumsuzluk, vurgu ve noktalama gibi kurallarla birleştirip tek bir skor üretiyor. Bu yöntemde herhangi bir model eğitimi yapmadık.

Skor 0,05 ve üzerindeyse pozitif, eksi 0,05 ve altındaysa negatif, arası da nötr kabul ettik.

Türkçe yorumları OPUS-MT ile İngilizceye çevirdik; çeviri kodu ile VADER kodu ayrı çalışıyor. Doğruluk İngilizcede yüzde 56,47, Türkçede yüzde 48,73 oldu. Çevirinin neye yol açabildiğini de gerçek bir örnekle göstereyim.

## Slayt 6 — Çeviri, mecazi sevgiyi tersine çevirebiliyor
**Konuşmacı: Merve Cemre Akkuş**

Bu yorumda “hastayım sana, dermansızım” deniyor; kaynak etiketi pozitif. VADER ve BERT negatif tahmin etmiş, Claude pozitif.

“Hastayım sana” ifadesi İngilizceye “I’m sick of you” diye çevrilmiş; bu da “senden bıktım” gibi bir anlama gelebiliyor. Yani sevgi ifadesi çeviride ters yöne dönmüş.

VADER çeviriyi kullandığı için bundan etkileniyor. BERT ise özgün Türkçeyi okuyor, onun hatasını çeviriye bağlayamayız. Yani aynı yanlış tahmin farklı nedenlerden çıkabiliyor. Şimdi sözü BERT için Kerem’e bırakıyorum.

## Slayt 7 — BERT nasıl duygu tahmini yapıyor?
**Konuşmacı: Kerem Kalyoncu**

Teşekkürler Merve. Ben Kerem Kalyoncu.

BERT’te metin önce token denen küçük parçalara ayrılıyor; bir token her zaman tam bir kelime olmuyor. Model bu parçaları cümledeki ilişkileriyle birlikte değerlendirip bağlama göre bir temsil çıkarıyor. En sonda da bir sınıflandırma katmanı pozitif, negatif ya da nötr etiketini veriyor.

Yani amaç, tek tek kelimelerin puanına değil, bağlama bakmak. Ama bu, mecazlı ya da dolaylı anlatılan duyguları her zaman doğru anlayacağı anlamına gelmiyor.

## Slayt 8 — BERT: modeller, ayarlar ve sonuçlar
**Konuşmacı: Kerem Kalyoncu**

İngilizcede RoBERTa-large, Türkçede BERTurk tabanlı hazır duygu modellerini kullandık. Bu modeller yayıncıları tarafından duygu analizi için hazırlanmıştı; biz yeniden eğitim yapmadık.

Kod yorumları 16’şarlık gruplar halinde işliyor ve çok uzun yorumları kısaltıyor. GPU varsa onu, yoksa CPU’yu kullanıyor. Çıktılar da ortak üç etikete çevrilip CSV’ye kaydediliyor.

Doğruluk İngilizcede yüzde 66,03, Türkçede yüzde 55,10 çıktı. Ama genel doğruluk tek başına yeterli değil; asıl farkı sınıflara bakınca görüyoruz.

## Slayt 9 — BERT: Türkçe nötr sınıfında 883 hata
**Konuşmacı: Kerem Kalyoncu**

Türkçe BERT, bin nötr yorumdan sadece 117’sini doğru bildi. 483’ünü pozitif, 400’ünü negatif saymış; yani nötr sınıfta 883 hata var. Nötr duyarlılığı yüzde 11,70’te kalıyor.

Duyarlılık, gerçek nötr yorumların ne kadarının yakalandığı demek. Her sınıfta bin yorum olduğu için bunu nötr örneklerin az olmasıyla açıklayamayız. İngilizce BERT’te ise 780 nötr yorum doğru bulunmuş.

## Slayt 10 — Türkçe karışıklık matrisleri
**Konuşmacı: Kerem Kalyoncu**

Bu matrislerde satırlar gerçek sınıfı, sütunlar modelin tahminini gösteriyor. Köşegen doğru tahminler, geri kalanı hatalar. Ortadaki BERT’in matrisi.

Nötr satırındaki kaymanın yanında, BERT bin pozitif yorumun 793’ünü, bin negatif yorumun 743’ünü doğru bulmuş. Yani sorun her sınıfa eşit yayılmıyor, nötr ayrımında toplanıyor.

İki dilde farklı modeller ve farklı veri kaynakları kullandık; o yüzden bu farkı sadece Türkçenin zor olmasına bağlayamayız. Modelin veriye uyumu da incelenmesi gereken bir konu.

## Slayt 11 — BERT örneği: ağlama, beğeniyi anlatabiliyor
**Konuşmacı: Kerem Kalyoncu**

Bu İngilizce yorumda kullanıcı, Fantastik Canavarlar’ı dördüncü kez izlediği halde John Williams’ın açılış müziğiyle gözlerinin dolduğunu anlatıyor. Kaynak etiketi pozitif; VADER ve BERT negatif, Claude pozitif tahmin etmiş.

Burada ağlamak üzüntüden çok duygulanmayı ve beğeniyi anlatıyor. Filmi tekrar izlemek ve müzikten etkilenmek de bunun bağlamını oluşturuyor.

Modelin bu olumlu bağlamı yakalayamamış olması mümkün. Ama tek örnekten modelin neden öyle karar verdiğini kesin söyleyemeyiz; bu yüzden sayılarla birlikte gerçek yorumlara da baktık.

## Slayt 12 — İngilizce karışıklık matrisleri
**Konuşmacı: Kerem Kalyoncu**

İngilizce BERT’in pozitif satırına bakalım: bin yorumdan 479’u doğru bulunmuş, 463’ü nötr, 58’i negatif tahmin edilmiş.

Türkçede nötr yorumlar pozitife ve negatife kayıyordu; İngilizcede ise pozitif yorumlar nötre kayıyor. Matrisler bize sadece kaç yanlış olduğunu değil, hatanın hangi yöne gittiğini de gösteriyor.

BERT için özet şu: hazır bir model her dilde ve her sınıfta dengeli başarı vermiyor. Şimdi LLM tabanlı sınıflandırmayı, yani Claude’u, ve genel karşılaştırmayı Hamza anlatacak.

## Slayt 13 — Claude: istemle üç sınıflı duygu analizi
**Konuşmacı: Hamza Taşbay**

Teşekkürler Kerem. Ben Hamza Taşbay.

Claude için kodda “claude-haiku-5-5” olarak geçen modeli API üzerinden kullandık. Modele örnek göstermeden sınıflandırma yaptırdığımız için bu yaklaşım zero-shot sınıflandırma oluyor.

İstemde modelden yorumu pozitif, negatif ya da nötr olarak sınıflandırmasını, duygu yoksa nötr seçmesini ve yorumun içindeki ifadeleri talimat gibi görmemesini istedik. Gerçek etiket modele hiç gönderilmedi.

Yanıtı üç etiketle sınırlayan bir JSON şeması kullandık; çıktı sınırı 100 token, thinking ayarı kapalıydı. İki dilde de özgün metinler gönderildi, tahminler ve token bilgileri kaydedildi.

## Slayt 14 — Genel doğruluk ve istatistiksel karşılaştırma
**Konuşmacı: Hamza Taşbay**

Genel doğrulukta iki dilde de sıralama aynı: Claude birinci, BERT ikinci, VADER üçüncü. Claude İngilizcede yüzde 70,63, Türkçede yüzde 64,20 doğruluğa ulaştı.

Claude’un BERT’e farkı İngilizcede 4,60, Türkçede 9,10 yüzde puan. 10 bin eşleştirilmiş bootstrap tekrarıyla yüzde 95 güven aralıklarına baktık: İngilizcede 2,80 ile 6,40, Türkçede 6,97 ile 11,27. İkisi de sıfırı içermiyor.

Süreklilik düzeltmeli McNemar testinde altı karşılaştırmanın hepsinde ham p değeri 0,001’den küçük. Çoklu karşılaştırma düzeltmesi yapmadık.

## Slayt 15 — Hatalar sınıflara eşit dağılmıyor
**Konuşmacı: Hamza Taşbay**

Hatalar sınıflara eşit dağılmıyor. Hataları pozitif, negatif, nötr sırasıyla okuyorum.

İngilizcede VADER 290, 457, 559; BERT 521, 278, 220; Claude 355, 230, 296 hata yaptı.

Türkçede VADER 397, 579, 562; BERT 207, 257, 883; Claude 309, 311, 454 hata yaptı.

Yani Claude genel doğrulukta önde olsa da, Türkçe pozitif ve negatifte en az hatayı BERT yapıyor.

## Slayt 16 — Kaynak etiketiyle uyuşmazlık ayrı incelenmeli
**Konuşmacı: Hamza Taşbay**

“Bu şehri sevmek ezelden yazılmış kaderime” yorumunun kaynak etiketi nötr, ama üç model de pozitif tahmin etmiş.

“Sevmek” ifadesi etiketi sorgulatıyor. Ama üç modelin aynı fikirde olması, etiketin hatalı olduğunu kanıtlamaz. Üç modelin de yanıldığı kayıt sayısı İngilizcede 308, Türkçede 494.

Bunları doğrulanmış etiket hatası saymadık, etiketlere de dokunmadık. Kesin karar için bağımsız bir insan incelemesi gerekir. Başarı oranlarımız da kaynak etiketlere göre hesaplandı.

## Slayt 17 — Sonuç ve iyileştirme öncelikleri
**Konuşmacı: Hamza Taşbay**

Sonuç olarak Claude genel doğrulukta öne çıkıyor. BERT’in sınıflara göre değişen başarısı ve VADER’in çeviriye duyarlı olması da hata analizinin neden önemli olduğunu gösteriyor.

Bulgularımız seçtiğimiz veri setleri ve kaydedilmiş çalıştırmalar için geçerli; başka verilerde aynı sıralamanın çıkacağını garanti etmiyoruz.

İyileştirme olarak bağımsız etiket denetimi, çeviri ve alan uyumunun kontrolü, model sürümlerinin sabitlenmesi ve tekrar deneyleri öneriyoruz. Tam kaynak kodlar ve açıklamaları Word raporunda. Kaynaklarımız da son slaytta.

## Slayt 18 — Kaynakça
**Konuşmacı: Hamza Taşbay**

Veri setlerini, yöntemlerin akademik çalışmalarını, model kartlarını ve Anthropic belgelerini kaynak olarak gösterdik. Tam kaynakça ve bağlantılar raporumuzda var.

Dinlediğiniz için teşekkür ederiz hocam.
