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
8. Tüm kalite ve güvenlik kapılarından geçen build, deploy simülasyonu job'una ulaşır.

## Sunumda Söylenecek Kısa Açıklama

> "Bu örnekte küçük bir FastAPI uygulaması kullandık. Geliştirici kodu GitHub'a gönderdiği anda GitHub Actions pipeline otomatik olarak çalışıyor. İlk olarak unit testler çalıştırılıyor. Testler başarısız olursa pipeline burada duruyor. Daha sonra Semgrep ile statik güvenlik analizi yapılıyor. Sonrasında Docker image oluşturuluyor ve Trivy ile image içerisindeki güvenlik açıkları taranıyor. Eğer yüksek veya kritik seviyede açık bulunursa deploy aşamasına geçilmiyor. Böylece güvenlik kontrolü yazılım geliştirme sürecinin sonuna değil, doğrudan CI/CD pipeline içine alınmış oluyor."

## Başarılı Demo

Pipeline tamamen yeşil olduğunda öğrencilere şunları gösteriyoruz:

- Tüm unit testler geçti.
- Semgrep statik kod analizi temiz.
- Docker image başarıyla build edildi.
- Trivy taramasında HIGH/CRITICAL açık bulunmadı.
- Deploy simülasyonu çalıştı ve "Deploy simulation completed successfully." mesajı yazdı.

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
- Deploy simülasyonu çalışmaz.

Bu **fail fast** prensibidir: hatalı kod, pipeline'ın en erken ve en ucuz adımında yakalanır; daha pahalı build ve deploy adımlarına hiç geçilmez.

## Başarısız Demo — Security Gate

Eğer Docker image içinde Trivy HIGH veya CRITICAL seviyede bir CVE bulursa:

- Trivy adımı kırmızıya döner (çünkü `exit-code: 1` ayarlı).
- `deploy-simulation` job'u çalışmaz.

Bu **security gate** mantığıdır: testler geçmiş olsa bile, içinde kritik açık olan bir image üretime gidemez. Güvenlik, geliştirme sürecinin sonuna eklenen bir adım değil, pipeline'ın doğal bir parçasıdır — bu da DevSecOps yaklaşımının özüdür.

## Sunum Sırasında Yapılacak Komutlar

Repo zaten oluşturuldu: https://github.com/coskungencay/ci-cd-sau

### 1. "Değişiklik nasıl yansıyor?" demosu (HAPPY PATH)

Bu, hocanın en çok merak edeceği şey: "Tamam pipeline çalışıyor da, ben bir şey değiştirdiğimde bunu nereden göreceğim?"

Açıklama: Geliştirici küçük bir kod değişikliği yapar (versiyon yükseltir gibi). Bu değişiklik commit'lenip push edildiğinde GitHub iki yerde anında gösterir:

1. **Code / Commits sekmesi** → diff görünür: hangi satır değişmiş, ne eklenmiş ne silinmiş.
2. **Actions sekmesi** → o commit için yeni bir pipeline run'ı otomatik başlar.

Somut örnek — versiyon `1.0.0` → `1.0.1`:

`app/main.py` içinde:

```python
@app.get("/version")
def version():
    return {"version": "1.0.1", "environment": "demo"}  # 1.0.0 -> 1.0.1
```

`tests/test_main.py` içinde aynı değeri güncelle (yoksa test düşer ve fail-fast tetiklenir — onu sonra göstereceğiz):

```python
def test_version_value():
    response = client.get("/version")
    assert response.json()["version"] == "1.0.1"
```

Sonra:

```bash
git add app/main.py tests/test_main.py
git commit -m "Bump version to 1.0.1"
git push
```

Sunumda yapılacak gösterim:

1. Repo sayfasında **Commits** sekmesini aç → en üstteki commit'e tıkla → "2 dosya değişti" diff'i göster. Bu, "ne değişti?" sorusunun doğrudan cevabı.
2. **Actions** sekmesine geç → yeni run başlamış, üç job sırayla yeşile dönüyor:
   - `Test & SAST` ✓
   - `Docker Build & Trivy Scan` ✓
   - `Deploy Simulation` ✓

Bu, pipeline'ın değişikliği uçtan uca takip ettiğinin kanıtıdır.

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

Sonuç: `Test & SAST` job'u kırmızıya döner. Sonraki iki job (Docker build, deploy) **hiç çalışmaz**. Hocaya: "Hatalı kod, pipeline'ın en erken adımında yakalandı; pahalı build/deploy adımlarına geçilmedi. Bu fail-fast prensibidir." denir.

### 3. Düzeltme — pipeline tekrar yeşile döner

```bash
# tests/test_main.py'deki assert'i 200'e geri al
git add tests/test_main.py
git commit -m "Fix failing test"
git push
```

Pipeline yeşile döner; üç job da geçer.

### 4. (Opsiyonel) Security Gate demosu

Daha cesursan, Trivy gate'inin gerçekten çalıştığını canlı göstermek için workflow'da `ignore-unfixed: true` satırını sil ve push at. Trivy, base image'daki HIGH CVE'leri yakalar, **deploy simülasyonu çalışmaz**. Sonra `ignore-unfixed: true`'yu geri koy ve yeşile döndür.

Bu, "testler geçmiş olsa bile, içinde HIGH/CRITICAL açık olan image deploy'a gitmez" mesajının canlı kanıtıdır.
