# Karşılaştırmalı Duygu Analizi

## Kurulum

Doğrulanan ortam Windows x64, Python 3.14 ve CUDA 13.0 destekli PyTorch `2.14.1+cu130` sürümüdür. `requirements.txt` çalışan ortamın sürümlerini sabitler ve CUDA derlemesi için [resmî PyTorch paket kaynağını](https://download.pytorch.org/whl/cu130/torch/) içerir.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

GPU yoksa mevcut kurulu PyTorch CPU üzerinde çalışabilir; farklı işletim sistemi veya Python sürümünde aynı CUDA paketinin kurulumu ayrıca doğrulanmalıdır. Kurulum talimatı yukarıdaki çalışma ortamını yeniden kurmayı hedefler. Mevcut ortamda sürüm eşleşmesi, çevrimdışı pip kurulum önizlemesi ve `pip check` doğrulandı; ayrı, boş bir ortama yeniden kurulum yapılmadı.

## Nitel hata incelemesi

`results/comparison/hata_ornekleri.csv` içindeki 103 örneğin `manuel_inceleme` ve `aciklama` alanları Codex tarafından metin bazında doldurulmuştur. `inceleme_kaynagi` sütunu bunun LLM incelemesi olduğunu belirtir; grup üyelerinin veya bağımsız insan etiketleyicilerin anotasyonu olarak sunulmamalıdır. `manuel_inceleme`, kaynak etiketi değiştiren bir alan değildir: `positive`, `negative`, `neutral`, `karma` veya `belirsiz` yorumunu içerir. `karma` birden çok duygu/hedefi; `belirsiz` ise görünür metinle kesinleştirilemeyen kutbu ifade eder. Açıklamalar olası nedenlerdir, modelin iç karar sürecinin kanıtı değildir.

Ana başarı hesapları kaynak etiketleriyle yapılır; bu inceleme etiketleri sonuçları veya tahminleri değiştirmez. Örnekler hatalardan seçildiği ve Türkçe nötr sınıfı ayrıca örneklendiği için buradan tüm veri setinin etiket hata oranı çıkarılamaz. `error_analysis.py` yeniden çalıştırıldığında aynı metin, kaynak etiket ve üç tahmin için incelemeleri korur; bunlardan biri değişirse o satırın eski incelemesini taşımaz.

Kullanılacak dosyalar `data/` klasöründedir:

- `Ingilizce_3000.csv`: 3.000 İngilizce metin ve duygu etiketi.
- `Turkce_3000.csv`: 3.000 Türkçe metin ve duygu etiketi.
- `Turkce_3000_translated.csv`: Aynı Türkçe metinlerin İngilizce çevirisi; Türkçe VADER için kullanılır.
- `KAYNAKLAR.md`: Veri kaynakları, çeviri yöntemi ve rapora aktarılabilecek kaynakça.

Her dilde sınıf başına 1.000 örnek vardır. Güncel hazırlama kayıtları `archive/source_records/` altındadır; eski veriler silinmiştir.

## Çalıştırma

Sanal ortamı etkinleştirip sırasıyla:

```powershell
python src/vader_analysis.py
python src/bert_analysis.py
python src/claude_analysis.py
python src/compare_results.py
python src/statistical_comparison.py
python src/error_analysis.py
```

`statistical_comparison.py`, kayıtlı tahminlerden McNemar testi ve bootstrap güven aralıklarını (Tablo 5), Macro F1 değerlerini (Tablo 30) ve ortak doğru/hata sayılarını (Tablo 12) üretir; çıktılar `results/comparison/` altındaki `istatistiksel_karsilastirma.csv` ve `ek_olcumler.csv` dosyalarıdır.

Claude adımı `.env` içinde Anthropic API anahtarı gerektirir ve ücretli API çağrısı yapar.

Verileri yeniden hazırlamak için `python src/prepare_datasets.py`; çeviriyi yeniden üretmek için `python src/translate_tr.py` kullanılır. Eksik kaynak/model indirmek için ilgili komuta `--download` eklenir.
