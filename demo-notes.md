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

İlk yükleme:

```bash
git init
git add .
git commit -m "Initial CI/CD DevSecOps demo"
git branch -M main
git remote add origin <GITHUB_REPO_URL>
git push -u origin main
```

Fail fast demosu:

```bash
# tests/test_main.py icindeki bir assert'i 500 yap
git add .
git commit -m "Break test to demonstrate fail fast"
git push
```

Düzeltme:

```bash
# Test'i eski haline geri getir
git add .
git commit -m "Fix failing test"
git push
```
