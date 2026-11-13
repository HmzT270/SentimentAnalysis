# Veri setleri ve kaynakça

Hazırlama tarihi: 12 Kasım 2026. Her dilde 3.000 metin; pozitif, negatif ve nötr sınıflarında 1.000'er özgün örnek vardır. Çıktı şeması mevcut analiz kodlarıyla uyumlu `text,label` biçimindedir.

Türkçe ham veri `raw/turkish/positive.csv`, `negative.csv` ve `notr.csv` dosyalarından okunur. Birleşik `raw/turkish/turkce_tum.csv` dosyası, temizleme ve örnekleme öncesindeki 6.001 kaydı içerir. Yerel Türkçe TXT kopyaları kaldırılmıştır. Eksik CSV'ler `--download` ile hazırlanırken özgün TXT kaynağı bellekte SHA256 ile doğrulanır, ardından CSV'ye dönüştürülür; diske TXT yazılmaz. Özgün kaynak ve yerel CSV özetleri manifestte ayrı ayrı tutulur. Kaynak satır numaraları ve özgün dosya adları izlenebilirlik kayıtlarında korunur. Model analizlerinde kullanılan dosya `Turkce_3000.csv` olmaya devam eder.

## Değiştirme gerekçesi

Önceki Türkçe veride açık anlam-etiket uyuşmazlıkları gözlendi. Önceki iki CSV'nin kaynakları ve etiket dönüşümleri proje dosyalarından doğrulanamadı. Bu nedenle kaynağı ve seçim süreci izlenebilen yeni değerlendirme örneklemleri hazırlandı. Önceki etiketlerin kaçta kaçının yanlış olduğu ölçülmedi; model uzlaşması gerçek etiket olarak kabul edilmedi. Yeni setlerin daha yüksek doğruluk vereceği veya hatasız olduğu iddia edilmiyor.

## İngilizce: TweetEval / Sentiment

Yerel ?ngilizce ham veriler `raw/english/ingilizce_tum.csv` ve s?n?f bazl? `positive.csv`, `negative.csv`, `notr.csv` dosyalar?ndad?r. ?ngilizce TXT kopyalar? kald?r?lm??t?r; ?zg?n kaynak dosya adlar? ve SHA256 ?zetleri manifestte korunur.

Kaynak: [CardiffNLP resmî deposu](https://github.com/cardiffnlp/tweeteval/tree/4fbd22cd78421f05b1ecdb4fc5725bc7a7bd8f66/datasets/sentiment).

TweetEval, çeşitli Twitter sınıflandırma görevlerini sabit veri bölümleriyle birleştiren bir değerlendirme çerçevesidir. Duygu görevi SemEval-2017 Task 4 kaynağına dayanır. Bu projede yalnızca yayımlanan **test** bölümündeki 12.284 metin kullanıldı. Kaynağın `mapping.txt` dosyasındaki `0=negative`, `1=neutral`, `2=positive` eşlemesi uygulandı. Eğitim ve doğrulama bölümleri eklenmedi. Kullanılan dosyalar, sürüm ve SHA256 değerleri `dataset_manifest.json` içindedir.

## Türkçe: Türkçe tweet duygu verisi

Kaynak: [Sercan Külcü'nün yayımladığı veri dosyaları](https://github.com/sercankulcu/sentiment-analysis-of-tweets-in-Turkish/tree/9647a08a9f0f6ac117d6f79a65578315b27682d9/training%20data).

`positive.txt`, `negative.txt` ve `notr.txt` dosyalarındaki önceden verilmiş sınıflar korundu; `notr` adı `neutral` olarak standartlaştırıldı. Yıldız puanı dönüşümü, yeniden etiketleme veya LLM ile etiket üretimi yapılmadı. Kaynakta ayrı bir test bölümü yayımlanmadığından bu projede ayrılan 3.000 metin yalnızca değerlendirme amacıyla kullanılmalıdır.

Kaynağın README dosyası 6.000 metin bildirse de sabit sürümdeki dosyalarda toplam **6.001 satır** bulundu: 1.552 pozitif, 3.001 negatif, 1.448 nötr. Dosyaların gerçek içeriği esas alındı. Bu kaynak, etiketleyici sayısı, uzlaşma ölçüsü ve ayrıntılı etiketleme yönergesi sunmuyor. Bu yüzden veri setini "etiketleri uzmanlarca doğrulanmış hatasız altın standart" olarak tanımlamayın. Görsel veya bağlantı bağlamına ihtiyaç duyan, karma duygu içeren, farklı dilde parçalar barındıran ve eski emoji kodlamaları bozulmuş metinler bulunabilir. Bu sınırlamalar sonuçların yorumunda açıkça belirtilmelidir.

## Temizleme ve örnekleme

Model çıktıları veya duygu kelimeleri seçim ölçütü olarak kullanılmadı. Metinlerin başındaki ve sonundaki boşluklar temizlendi; içerideki yazım, emoji, URL, kullanıcı adı ve noktalama korundu. Tekrar denetiminde NFKC normalizasyonu, `casefold` ve boşluk birleştirme kullanıldı; bu işlem model girdisini değiştirmez. Aynı normalize metin farklı sınıflarda bulunuyorsa grubun bütün satırları çıkarıldı; aynı sınıftaki tekrarların ilki korundu.

İngilizcede 7 çelişkili etiketli satır çıkarıldı. Türkçede 24 çelişkili etiketli satır ve 44 tekrar çıkarıldı. Sonrasında İngilizcede 2.375 pozitif, 3.968 negatif, 5.934 nötr; Türkçede 1.545 pozitif, 2.954 negatif, 1.434 nötr aday kaldı. Çıkarma sayıları, normalize edilmiş birebir metin gruplarını ifade eder; anlamsal etiket hatası oranı değildir.

Her sınıftaki adaylar `42|select|dil|normalize_metin` SHA256 değerine göre sıralanıp ilk 1.000 satır seçildi. Son sıra ayrı bir `42|order|dil|normalize_metin` SHA256 sıralamasıyla karıştırıldı. Bu yöntem sabittir ve Python'un rastgele sayı üretecinin sürümüne bağlı değildir. Her satırın kaynak dosyası, sıfır tabanlı kaynak satır numarası ve metin özeti `provenance/` altında bulunur.

## Değerlendirme sınırlamaları

İki set de sosyal medya metinleridir; ürün yorumu deneyleriyle doğrudan aynı deney değildir. Farklı konular ve etiketleme süreçleri nedeniyle iki dil arasındaki başarı farkını yalnızca dilin zorluğuna bağlamayın. Türkçe kaynakta bölünme bilgisi yoktur. Hazır modellerin eğitim verileriyle veya LLM ön eğitimiyle örtüşme bütünüyle dışlanmış değildir. Eğitim verisi erişilebiliyorsa eşleşme ayrıca kontrol edilmelidir.

Kaynak etiketleri korunmuştur; metinlerin tamamı insan tarafından yeniden denetlenmemiştir. Grup üyelerinin her sınıftan rastgele örnekleri bağımsız inceleyip etiket tanımını tartışması önerilir. Ana deney sonuçlarını iyileştirmek amacıyla örnek silmeyin veya model uzlaşmasına göre etiket değiştirmeyin. Varsa insan denetimini ayrı bir analiz olarak raporlayın.

THY-SA da incelendi ancak 23.300 satırının yalnızca 745'i pozitifti; tekrar/çelişki denetiminden sonra 460 özgün pozitif kaldı. Bu nedenle sınıf başına 1.000 koşulunu sağlayamadığından seçilmedi. Kaynak: https://huggingface.co/datasets/trmteb/thy_sa

## Yeniden üretme ve analiz durumu

Proje kökünden `python src/prepare_datasets.py` komutu yerel sabit kaynakları doğrulayıp aynı CSV'leri üretir. Kaynaklar yoksa `--download` eklenir. Farklı eski CSV'ler varsa `--replace`, önce ZIP yedeğini doğrular, sonra eski verileri ve sonuçları aktif konumdan kaldırır. Mevcut verilerle aynı veri üretilirse sonuç dosyaları kaldırılmaz. Hazırlama kodu yalnızca Python standart kütüphanesini kullanır.

Önceki veri, çeviri ve sonuç dosyaları kullanıcının isteğiyle silinmiştir. BERT, VADER ve Claude güncel veriler üzerinde yeniden çalıştırılmalıdır. Güncel Türkçe setin İngilizce çevirisi `data/Turkce_3000_translated.csv` dosyasındadır. Çeviri modeli ve parametreleri `translation_manifest.json` dosyasında kayıtlıdır. Veri hazırlama ve yerel çeviri sırasında ücretli API çağrısı yapılmadı.

## Rapora aktarılabilecek kaynakça

Türkçe VADER çevirisi `src/translate_tr.py` ile [Helsinki-NLP/opus-mt-tr-en](https://huggingface.co/Helsinki-NLP/opus-mt-tr-en) modelinin `19c65427cc2af5f191337d4899e0348c4af25902` sürümü kullanılarak yerel üretilir. Çıktı `Turkce_3000_translated.csv` dosyasıdır. Kaynak metin ve etiketler korunur; yalnızca `text_en` eklenir. Ayarlar: `num_beams=4`, `do_sample=False`, `max_new_tokens=256`, batch büyüklüğü 32. Girdiler kesilmez; model sınırını aşan girdide veya tamamlanmayan çıktıda işlem durur. Kaynak/çıktı SHA256 değerleri `translation_manifest.json` dosyasına yazılır. Bu bir makine çevirisidir; duygu, ironi, argo ve emoji aktarımında hatalar olabilir. Etiketler çeviriden yeniden türetilmez.

1. Barbieri, F., Camacho-Collados, J., Espinosa Anke, L. ve Neves, L. (2020). *TweetEval: Unified Benchmark and Comparative Evaluation for Tweet Classification*. Findings of EMNLP 2020, 1644–1650. https://doi.org/10.18653/v1/2020.findings-emnlp.148
2. Rosenthal, S., Farra, N. ve Nakov, P. (2017). *SemEval-2017 Task 4: Sentiment Analysis in Twitter*. Proceedings of the 11th International Workshop on Semantic Evaluation, 502–518. https://doi.org/10.18653/v1/S17-2088
3. Külcü, S. (t.y.). *sentiment-analysis-of-tweets-in-Turkish: training data* [Veri dosyaları]. GitHub. https://github.com/sercankulcu/sentiment-analysis-of-tweets-in-Turkish/tree/9647a08a9f0f6ac117d6f79a65578315b27682d9/training%20data (Erişim: 12 Kasım 2026).

BibTeX kayıtları `sources.bib` dosyasındadır. Türkçe kaynak için doğrulanmamış makale künyesi veya etiketleme ayrıntısı eklenmedi.
