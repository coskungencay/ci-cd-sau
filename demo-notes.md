# Sunum Notları

## Demo Amacı

Bu demo ile GitHub Actions üzerinde çalışan basit bir CI/CD + DevSecOps pipeline gösteriyoruz. Amacımız; küçük bir FastAPI uygulaması üzerinden, kodun commit anından deploy aşamasına kadar otomatik olarak nasıl test edildiğini, güvenlik kontrollerinden nasıl geçirildiğini ve hangi noktalarda durdurulabileceğini somut olarak göstermektir.

## Demo Akışı

1. Kodda küçük bir değişiklik yapılır.
2. `git commit` ve `git push` atılır.
3. GitHub Actions pipeline'ı otomatik olarak başlar.
4. Önce unit testler (`pytest`) çalışır.
5. Ardından Semgrep ile SAST (statik güvenlik analizi) yapılır.
6. Sonra Docker image build edilir.
7. Build edilen image Trivy ile güvenlik taramasından geçer.
8. Tüm kalite ve güvenlik kapılarından geçen build, **GitHub Pages'e gerçek deploy** olur ve canlı URL'de görünür.

## Sunumda Söylenecek Kısa Açıklama

> "Bu örnekte küçük bir FastAPI uygulaması ve onun yanında basit bir HTML sayfası kullandık. Geliştirici kodu GitHub'a gönderdiği anda GitHub Actions pipeline otomatik olarak çalışıyor. İlk olarak unit testler çalıştırılıyor. Testler başarısız olursa pipeline burada duruyor. Daha sonra Semgrep ile statik güvenlik analizi yapılıyor. Sonrasında Docker image oluşturuluyor ve Trivy ile image içerisindeki güvenlik açıkları taranıyor. Eğer yüksek veya kritik seviyede açık bulunursa deploy aşamasına geçilmiyor. Bütün kontroller geçerse statik sayfa GitHub Pages'e otomatik deploy oluyor; canlı URL'i yenilediğimizde değişikliği görebiliyoruz. Böylece güvenlik kontrolü yazılım geliştirme sürecinin sonuna değil, doğrudan CI/CD pipeline içine alınmış oluyor."

## Başarılı Demo

Pipeline tamamen yeşil olduğunda öğrencilere şunları gösteriyoruz:

- Tüm unit testler geçti.
- Semgrep statik kod analizi temiz.
- Docker image başarıyla build edildi.
- Trivy taramasında HIGH/CRITICAL açık bulunmadı.
- `web/` klasörü GitHub Pages'e deploy edildi → canlı sayfa güncel.

Bu, **happy path** senaryosudur: kod kaliteli, güvenli ve dağıtıma hazırdır.

## Başarısız Demo — Fail Fast

Bir testi bilerek bozalım. Örneğin `tests/test_main.py` içinde:

```python
assert response.status_code == 500
```

Bu değişikliği commit'leyip push attığımızda:

- `pytest` adımı kırmızıya döner.
- Docker build job'u hiç tetiklenmez.
- Trivy taraması yapılmaz.
- Pages deploy çalışmaz; **canlı sayfa eski haliyle kalır**.

Bu **fail fast** prensibidir: hatalı kod, pipeline'ın en erken ve en ucuz adımında yakalanır; daha pahalı build ve deploy adımlarına hiç geçilmez. Üretim sayfası bozulmadan korunur.

## Başarısız Demo — Security Gate

Eğer Docker image içinde Trivy HIGH veya CRITICAL seviyede bir CVE bulursa:

- Trivy adımı kırmızıya döner (`exit-code: 1` ayarlı).
- Pages deploy job'u çalışmaz; canlı sayfa güncellenmez.

Bu **security gate** mantığıdır: testler geçmiş olsa bile, içinde kritik açık olan bir image üretime gidemez. Güvenlik, geliştirme sürecinin sonuna eklenen bir adım değil, pipeline'ın doğal bir parçasıdır — bu da DevSecOps yaklaşımının özüdür.

## Sunum Sırasında Yapılacak Komutlar

**Repo:** https://github.com/coskungencay/ci-cd-sau
**Canlı Demo Sayfası:** https://coskungencay.github.io/ci-cd-sau/

> Sunum sırasında bu iki sekmeyi açık tut: GitHub Actions sekmesi + canlı demo sayfası. Push'tan sonra Actions yeşile döndüğünde sayfayı yenile, değişiklik canlı görünür.

### 1. "Değişiklik nasıl görünür?" demosu (HAPPY PATH)

Bu, hocanın en çok merak edeceği şey: "Tamam pipeline çalışıyor da, ben bir yazıyı değiştirdiğimde bunu gözle nasıl göreceğim?"

Cevap: `web/index.html` içindeki herhangi bir metni değiştir, push at, pipeline yeşile döndüğünde **canlı sayfayı yenile** — değişiklik görünür.

Somut örnek — başlığı ve versiyon badge'ini değiştir:

`web/index.html` içinde:

```html
<span class="badge">v1.0.1</span>

<h1>Yazılım Mühendisliği — CI/CD Sunumu</h1>
```

Sonra:

```bash
git add web/index.html
git commit -m "Update demo page title and version"
git push
```

Sunumda yapılacak gösterim:

1. Hocaya canlı sayfayı göster — eski başlık görünüyor: https://coskungencay.github.io/ci-cd-sau/
2. IDE'de değişikliği yap, commit + push at.
3. **GitHub Actions sekmesini** aç → yeni run başlamış, 3 job sırayla yeşile dönüyor:
   - `Test & SAST` ✓
   - `Docker Build & Trivy Scan` ✓
   - `Deploy to GitHub Pages` ✓ (yaklaşık 1-2 dk)
4. Pipeline yeşile döndükten sonra **canlı sayfayı yenile** → yeni başlık görünür. Hocaya: "Bakın, kodda yaptığım değişiklik tüm güvenlik kontrollerinden geçtikten sonra otomatik olarak canlı URL'e yansıdı. Hiçbir manuel deploy adımı yok."

### 2. Fail Fast demosu

`tests/test_main.py` içinde bir assert'i kasıtlı olarak boz:

```python
def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 500   # bilerek yanlis
```

```bash
git add tests/test_main.py
git commit -m "Break test to demonstrate fail fast"
git push
```

Sonuç: `Test & SAST` job'u kırmızıya döner. Sonraki iki job (Docker build, deploy) **hiç çalışmaz**. Canlı sayfa eski haliyle kalır. Hocaya: "Hatalı kod, pipeline'ın en erken adımında yakalandı; pahalı build/deploy adımlarına geçilmedi. Bu fail-fast prensibidir. Üretim canlı sayfası bozulmadan korundu."

### 3. Düzeltme — pipeline tekrar yeşile döner

```bash
# tests/test_main.py'deki assert'i 200'e geri al
git add tests/test_main.py
git commit -m "Fix failing test"
git push
```

Pipeline yeşile döner; üç job da geçer; canlı sayfa güncellenir.

### 4. (Opsiyonel) Security Gate demosu

Daha cesursan, Trivy gate'inin gerçekten çalıştığını canlı göstermek için `.github/workflows/ci-cd.yml` dosyasındaki `ignore-unfixed: true` satırını sil ve push at. Trivy, base image'daki HIGH CVE'leri yakalar, **deploy adımı çalışmaz**, canlı sayfa güncellenmez. Sonra `ignore-unfixed: true`'yu geri koy → yeşile dön, sayfa güncellenir.

Bu, "testler geçmiş olsa bile, içinde HIGH/CRITICAL açık olan image deploy'a gitmez" mesajının canlı kanıtıdır.
