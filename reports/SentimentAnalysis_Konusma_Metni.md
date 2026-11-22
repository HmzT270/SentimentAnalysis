# Karşılaştırmalı Duygu Analizi — Tam Konuşma Metni

Bu metin, `SentimentAnalysis_Sunum.pptx` dosyasının 6–6–6 düzenindeki 18 slaydının tamamıyla aynı sıradadır. Başlıklar ve bu giriş okunmaz; her slaydın altındaki paragraflar aynen okunur. Konuşmacı geçişleri ve kapanış metnin içindedir. Slaytlar 1’den 18’e sırayla ilerletilir. Sonuç 17. slaytta, kaynakça ve son teşekkür 18. slayttadır.

Konuşmacılar: **Kerem: 1–6. slaytlar. Merve: 7–12. slaytlar. Hamza: 13–18. slaytlar.**

Metin **1.242 konuşma kelimesidir**. Dakikada yaklaşık 140 kelimelik okuma ve kısa geçişlerle hedef süre **9,5 dakika civarındadır**; gerçek süre okuma hızına bağlıdır. Her kişi yaklaşık üç dakika konuşur. Hiçbir bölümde ek cümle kurmak veya doğaçlama yapmak gerekmez.

## Slayt 1 — Karşılaştırmalı Duygu Analizi
**Konuşmacı: Kerem Kalyoncu**

Merhaba hocam. Ben Kerem Kalyoncu. Merve Cemre Akkuş ve Hamza Taşbay ile hazırladığımız karşılaştırmalı duygu analizi projesini sunacağız.

İngilizce ve Türkçe yorumlarda VADER, BERT ve Claude’un başarısını ve hatalarını karşılaştırdık. Ben veri setlerini ve VADER’i, Merve BERT’i, Hamza Claude’u ve genel değerlendirmeyi anlatacak. Her yöntem için genel doğruluğun yanında pozitif, negatif ve nötr sınıflardaki yanlış tahminleri de inceledik.

## Slayt 2 — Veri setleri ve sınıf dağılımları
**Konuşmacı: Kerem Kalyoncu**

İngilizcede TweetEval’in SemEval kaynaklı resmî test verilerini, Türkçede Sercan Külcü’nün tweet veri setini kullandık. Bunlar önceden etiketlenmiş kaynaklardır.

Her dilde bin pozitif, bin negatif ve bin nötr olmak üzere üç bin yorum seçtik. Toplam altı bin özgün yorum değerlendirdik. Sınıfların eşit büyüklükte olması, hata sayılarını aynı örnek sayısı üzerinden karşılaştırmamızı sağladı.

Türkçe yorumların VADER için hazırlanan İngilizce çevirileri yeni gözlemler değildir; özgün yorum sayısını artırmaz.

## Slayt 3 — Veri hazırlama ve ortak değerlendirme
**Konuşmacı: Kerem Kalyoncu**

Veri hazırlama kodu önce boş kayıtları, tekrarları ve aynı metne farklı etiket verilmiş çelişkili kayıtları ayıklıyor. Ardından sabit bir seçim kuralıyla her sınıftan bin yorum seçiyor. Model tahminleri veri seçiminde kullanılmadı ve kaynak etiketleri değiştirilmedi.

Her dilde yöntemleri aynı yorumlar üzerinde değerlendirdik. Doğruluk, doğru tahminlerin toplam yorumlara oranıdır. Sınıf bazlı hatayı ise gerçek etikete göre saydık. Örneğin nötr bir yorum pozitif tahmin edilmişse bu, nötr sınıfın hatasıdır.

Hazırlama, tahmin ve değerlendirme kodları ayrıdır; karşılaştırma ve hata analizi, kaydedilen tahmin dosyalarından üretilir.

## Slayt 4 — Üç yönteme genel bakış
**Konuşmacı: Kerem Kalyoncu**

Üç yaklaşımın temel farkı burada görülüyor. VADER, duygu sözlüğünü ve dil kurallarını kullanıyor. BERT grubunda, her dil için hazır bir duygu sınıflandırıcısı çalıştırıyoruz. Claude’da ise modele bir sınıflandırma istemi gönderiyoruz.

İngilizce yorumlar üç yönteme de özgün biçimiyle verildi. Türkçede VADER İngilizce çeviriyi, BERT ve Claude özgün Türkçe metni kullandı. Dolayısıyla VADER’in Türkçe sonucunu yorumlarken çeviri etkisini de dikkate almak gerekiyor.

## Slayt 5 — VADER: uygulama ve sonuçlar
**Konuşmacı: Kerem Kalyoncu**

VADER, sözcük puanlarını olumsuzluk, vurgu ve noktalama gibi kurallarla birleştirerek birleşik bir duygu skoru üretir. Bu yöntemde model eğitimi yapmadık.

Skor sıfır virgül sıfır beş ve üzerindeyse pozitif, eksi sıfır virgül sıfır beş ve altındaysa negatif, aradaki değerlerde nötr kabul ettik.

Türkçe yorumları OPUS-MT modeliyle İngilizceye çevirdik. Çeviri kodu ile VADER tahmin kodu ayrı çalışıyor. Doğruluk İngilizcede yüzde elli altı virgül kırk yedi, Türkçede yüzde kırk sekiz virgül yetmiş üç oldu. Şimdi çeviri sorununa gerçek bir örnek göstereceğim.

## Slayt 6 — Çeviri, mecazi sevgiyi tersine çevirebiliyor
**Konuşmacı: Kerem Kalyoncu**

Yorumdaki “hastayım sana, dermansızım” ifadesinin kaynak etiketi pozitif. VADER ve BERT negatif, Claude pozitif tahmin etmiş.

“Hastayım sana” ifadesi, İngilizcede “senden bıktım” anlamına gelebilen “I’m sick of you” biçimine çevrilmiş. Böylece mecazi sevgi ifadesinin duygu yönü değişmiş.

VADER bu çeviriyi kullandığından girdisi etkileniyor. BERT özgün Türkçeyi okuduğu için onun hatasını çeviriye bağlayamayız. Bu ayrım, aynı yanlış tahminin farklı nedenlerle oluşabileceğini gösteriyor. Şimdi BERT’i Merve anlatacak.

## Slayt 7 — BERT nasıl duygu tahmini yapıyor?
**Konuşmacı: Merve Cemre Akkuş**

Teşekkür ederim Kerem. Ben Merve Cemre Akkuş.

BERT tabanlı yaklaşımda metin önce token adı verilen parçalara ayrılır. Token her zaman tam bir kelime değildir. Model, parçaları cümle içindeki ilişkileriyle değerlendirerek bağlamsal bir temsil oluşturur. Duygu sınıflandırma katmanı bu temsilden pozitif, negatif veya nötr etiketi üretir.

Amaç, tek bir sözcüğün puanından daha geniş bağlamı değerlendirmektir. Ancak bu özellik, mecazların veya örtük duyguların her zaman doğru anlaşılacağını garanti etmez.

## Slayt 8 — BERT: modeller, ayarlar ve sonuçlar
**Konuşmacı: Merve Cemre Akkuş**

İngilizcede RoBERTa-large, Türkçede BERTurk tabanlı hazır duygu modellerini kullandık. Bunlar yayıncıları tarafından duygu analizi için hazırlanmıştı; proje kapsamında yeniden eğitim yapmadık.

Kod, yorumları on altılık gruplarla işler. İki yüz elli altı tokenı aşan girdiler kesilir. Grup büyüklüğüyle metnin uzunluk sınırı farklı ayarlardır. GPU varsa GPU, yoksa CPU kullanılır. Çıktılar ortak üç etikete dönüştürülüp CSV’ye kaydedilir.

Doğruluk İngilizcede yüzde altmış altı virgül sıfır üç, Türkçede yüzde elli beş virgül on oldu. Ancak genel doğruluk tek başına yeterli değil.

## Slayt 9 — BERT: Türkçe nötr sınıfında 883 hata
**Konuşmacı: Merve Cemre Akkuş**

Türkçe BERT, bin nötr yorumun yalnızca yüz on yedisini doğru sınıflandırdı. Dört yüz seksen üçünü pozitif, dört yüzünü negatif tahmin etti. Böylece nötr sınıfta sekiz yüz seksen üç hata oluştu; nötr duyarlılığı yüzde on bir virgül yetmişte kaldı.

Duyarlılık, gerçek nötr yorumların ne kadarının yakalandığını ifade ediyor. Değerlendirme verisinde her sınıfta bin yorum bulunduğundan bu sonuç, nötr örneklerin azlığıyla açıklanamaz. İngilizce BERT’te ise yedi yüz seksen nötr doğru tahmini var.

## Slayt 10 — Türkçe karışıklık matrisleri
**Konuşmacı: Merve Cemre Akkuş**

Matrislerde satırlar gerçek sınıfı, sütunlar tahmini gösteriyor. Köşegendeki sayılar doğru, diğer hücreler yanlış tahminlerdir. BERT ortadaki matristir.

Nötr satırındaki kaymanın yanında BERT’in bin pozitif yorumun yedi yüz doksan üçünü, bin negatif yorumun yedi yüz kırk üçünü doğru bulduğunu görüyoruz. Sorun bütün sınıflara eşit yayılmıyor; nötr ayrımında yoğunlaşıyor.

İki dilde farklı modeller ve veri kaynakları kullandık. Bu nedenle farkı yalnızca Türkçenin zorluğuna bağlayamayız. Modelin alan uyumu da incelenmeli.

## Slayt 11 — BERT örneği: ağlama, beğeniyi anlatabiliyor
**Konuşmacı: Merve Cemre Akkuş**

Bu İngilizce yorumda kullanıcı, Fantastik Canavarlar filmini dördüncü izleyişinde bile John Williams’ın açılış müziğiyle gözlerinin dolduğunu anlatıyor. Kaynak etiketi pozitif; VADER ve BERT negatif, Claude pozitif tahmin etmiş.

Ağlama burada üzüntüden çok beğeni ve duygulanmayı anlatıyor. Tekrar izleme ve müzikten etkilenme, bu ifadenin bağlamını oluşturuyor.

Olası açıklama, modelin bu olumlu bağlamı yorumlamadaki güçlüğü. Ancak tek örnekten modelin iç karar nedenini kesin çıkaramayız. Bu yüzden sayısal sonuçlarla birlikte gerçek yorumları da inceledik.

## Slayt 12 — İngilizce karışıklık matrisleri
**Konuşmacı: Merve Cemre Akkuş**

İngilizce BERT’in pozitif satırında bin yorumun dört yüz yetmiş dokuzu doğru bulunmuş, dört yüz altmış üçü nötr, elli sekizi negatif tahmin edilmiş.

Türkçede nötr yorumların pozitif ve negatif sınıflara kayması, İngilizcede ise pozitif yorumların nötr tahmin edilmesi dikkat çekiyor. Matrisler, yanlış sayısının yanında hatanın yönünü de gösteriyor.

BERT bölümünün sonucu şu: Hazır bir model her dilde ve sınıfta dengeli başarı sağlamıyor. Şimdi Claude’u ve genel karşılaştırmayı Hamza anlatacak.

## Slayt 13 — Claude: istemle üç sınıflı duygu analizi
**Konuşmacı: Hamza Taşbay**

Teşekkür ederim Merve. Ben Hamza Taşbay.

Claude için kodda “claude-haiku-5-5” olarak belirtilen modeli API üzerinden kullandık. Örnek göstermeden sınıflandırma istediğimiz için yaklaşımımız zero-shot sınıflandırmadır.

İstemde yorumu pozitif, negatif veya nötr sınıflandırmasını, duygu yoksa nötr seçmesini ve yorum içeriğini talimat olarak değerlendirmemesini söyledik. Gerçek etiket modele gönderilmedi.

Yanıtı üç etiketle sınırlayan JSON şeması kullandık. Çıktı sınırı yüz token, thinking ayarı kapalıydı. İki dilde de özgün metinler gönderildi; tahminler ve token bilgileri kaydedildi.

## Slayt 14 — Genel doğruluk ve istatistiksel karşılaştırma
**Konuşmacı: Hamza Taşbay**

Genel doğrulukta iki dilde de Claude birinci, BERT ikinci, VADER üçüncü oldu. Claude İngilizcede yüzde yetmiş virgül altmış üç, Türkçede yüzde altmış dört virgül yirmi doğruluğa ulaştı.

Claude’un BERT’e farkı İngilizcede dört virgül altmış, Türkçede dokuz virgül on yüzde puan. On bin eşleştirilmiş bootstrap tekrarında yüzde doksan beş güven aralıkları İngilizcede iki virgül seksen ile altı virgül kırk, Türkçede altı virgül doksan yedi ile on bir virgül yirmi yedi. İkisi de sıfırı içermiyor.

Süreklilik düzeltmeli McNemar testinde altı karşılaştırmanın ham p değeri sıfır virgül sıfır sıfır birden küçük. Çoklu karşılaştırma düzeltmesi yapılmadı.

## Slayt 15 — Hatalar sınıflara eşit dağılmıyor
**Konuşmacı: Hamza Taşbay**

Hataları pozitif, negatif ve nötr sırasıyla okuyacağım.

İngilizcede VADER iki yüz doksan, dört yüz elli yedi, beş yüz elli dokuz; BERT beş yüz yirmi bir, iki yüz yetmiş sekiz, iki yüz yirmi; Claude üç yüz elli beş, iki yüz otuz, iki yüz doksan altı hata yaptı.

Türkçede VADER üç yüz doksan yedi, beş yüz yetmiş dokuz, beş yüz altmış iki; BERT iki yüz yedi, iki yüz elli yedi, sekiz yüz seksen üç; Claude üç yüz dokuz, üç yüz on bir, dört yüz elli dört hata yaptı.

Claude genel doğrulukta önde olsa da Türkçe pozitif ve negatifte en az hata BERT’te.

## Slayt 16 — Kaynak etiketiyle uyuşmazlık ayrı incelenmeli
**Konuşmacı: Hamza Taşbay**

“Bu şehri sevmek ezelden yazılmış kaderime” yorumunun kaynak etiketi nötr, üç modelin tahmini pozitif.

Sevmek ifadesi etiketi sorgulatıyor; ancak model uzlaşması, etiket hatasını kanıtlamaz. Üç modelin birlikte kaynakla uyuşmadığı kayıt sayısı İngilizcede üç yüz sekiz, Türkçede dört yüz doksan dört.

Bunları doğrulanmış etiket hatası saymadık ve etiketleri değiştirmedik. Kesin karar için bağımsız insan incelemesi gerekir. Başarı oranlarımız da kaynak etiketlerine göre hesaplanmıştır.

## Slayt 17 — Sonuç ve iyileştirme öncelikleri
**Konuşmacı: Hamza Taşbay**

Sonuç olarak Claude genel doğrulukta öne çıkıyor. BERT’in sınıflara göre değişen başarısı ve VADER’in çeviriye duyarlılığı ise hata analizinin önemini gösteriyor.

Bulgularımız seçilen veri setleri ve kayıtlı çalıştırmalar için geçerlidir; farklı verilerde aynı sıralamayı garanti etmez.

İyileştirme önceliklerimiz bağımsız etiket denetimi, çeviri ve alan uyumunun kontrolü, model sürümlerinin sabitlenmesi ve tekrar deneyleridir. Tam kaynak kodlar ve açıklamaları Word raporunda bulunuyor. Kaynaklarımız son slaytta yer alıyor.

## Slayt 18 — Kaynakça
**Konuşmacı: Hamza Taşbay**

Veri setlerini, yöntemlerin akademik çalışmalarını, kullanılan model kartlarını ve Anthropic belgelerini kaynak gösterdik. Tam kaynakça ve erişim bağlantıları raporumuzda bulunuyor.

Dinlediğiniz için teşekkür ederiz hocam.
