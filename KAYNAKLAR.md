# Veri setleri ve çeviri

- `Ingilizce_3000.csv`: [TweetEval / Sentiment](https://github.com/cardiffnlp/tweeteval/tree/4fbd22cd78421f05b1ecdb4fc5725bc7a7bd8f66/datasets/sentiment) resmî test bölümünden 1.000 pozitif, 1.000 negatif, 1.000 nötr metin.
- `Turkce_3000.csv`: [Sercan Külcü'nün Türkçe tweet verileri](https://github.com/sercankulcu/sentiment-analysis-of-tweets-in-Turkish/tree/9647a08a9f0f6ac117d6f79a65578315b27682d9/training%20data) içinden 1.000 pozitif, 1.000 negatif, 1.000 nötr metin.
- `Turkce_3000_translated.csv`: Aynı Türkçe metinler ve etiketler korunarak `text_en` sütunu eklendi. [Helsinki-NLP/opus-mt-tr-en](https://huggingface.co/Helsinki-NLP/opus-mt-tr-en) modelinin `19c65427cc2af5f191337d4899e0348c4af25902` sürümüyle yerel makine çevirisi yapıldı. Ayarlar: beam=4, örnekleme kapalı, batch=32, en fazla 256 yeni token. Girdiler kesilmedi.

Kaynak etiketleri korunmuştur. Tekrarlar ve aynı metne farklı etiket verilmiş kayıtlar ayıklandıktan sonra sabit SHA256 sıralamasıyla örnekleme yapıldı. Model tahminleri seçimde kullanılmadı. Türkçe kaynağın etiketleme protokolü sınırlı belgelidir; makine çevirisi de anlam ve duygu aktarımında hata yapabilir. Veriler tamamen hatasız olarak sunulmamalıdır.

## Raporda kullanılabilecek kaynakça

1. Barbieri, F., Camacho-Collados, J., Espinosa Anke, L. ve Neves, L. (2020). *TweetEval: Unified Benchmark and Comparative Evaluation for Tweet Classification*. Findings of EMNLP 2020, 1644–1650. https://doi.org/10.18653/v1/2020.findings-emnlp.148
2. Rosenthal, S., Farra, N. ve Nakov, P. (2017). *SemEval-2017 Task 4: Sentiment Analysis in Twitter*. SemEval 2017, 502–518. https://doi.org/10.18653/v1/S17-2088
3. Külcü, S. (t.y.). *sentiment-analysis-of-tweets-in-Turkish: training data* [Veri dosyaları]. GitHub. Yukarıdaki sabit sürüm bağlantısı. Erişim: 12 Kasım 2026.
4. Helsinki-NLP. (t.y.). *OPUS-MT Turkish-English translation model* [Çeviri modeli]. Hugging Face. Yukarıdaki model bağlantısı. Erişim: 12 Kasım 2026.

Ayrıntılı hazırlama kayıtları `archive/source_records/` altında saklanır. Önceki veri setleri ve model sonuçları silinmiştir.
