# CI/CD + DevSecOps Demo

**Canlı demo:** https://coskungencay.github.io/ci-cd-sau/
**Repo:** https://github.com/coskungencay/ci-cd-sau

## Projenin Amacı

Bu demo, GitHub Actions kullanarak basit bir cloud-based CI/CD ve DevSecOps pipeline'ın nasıl çalıştığını göstermek için hazırlanmıştır. Geliştiricinin yaptığı bir commit'in nasıl otomatik olarak test edildiğini, statik kod analizinden geçirildiğini, Docker image olarak paketlendiğini, container güvenlik taramasından geçirildiğini ve son olarak **gerçek bir URL'e deploy edildiğini** uçtan uca gösterir.

## Kullanılan Teknolojiler

- **FastAPI** — Demo edilecek küçük Python web API (test ve Docker hedefi)
- **pytest** — Unit test framework
- **Docker** — Uygulamanın container olarak paketlenmesi
- **GitHub Actions** — CI/CD pipeline orchestrator
- **Semgrep** — Statik kod analizi (SAST)
- **Trivy** — Container/image güvenlik taraması
- **GitHub Pages** — Statik demo sayfasının canlı deploy hedefi

## Proje Yapısı

```
ci-cd-sau/
├── app/                  # FastAPI backend (test edilen ve Docker'a giren kod)
├── tests/                # pytest unit testleri
├── web/                  # Statik demo sayfasi (Pages'e deploy edilen)
├── .github/workflows/    # GitHub Actions pipeline tanimi
├── Dockerfile            # Backend image
├── requirements.txt      # Python bagimliliklari
└── README.md / demo-notes.md
```

## Pipeline Akışı

1. Geliştirici kodda değişiklik yapar ve GitHub'a push eder.
2. GitHub Actions otomatik olarak `CI/CD + DevSecOps Demo Pipeline` workflow'unu başlatır.
3. Unit testler `pytest` ile çalıştırılır.
4. Semgrep ile statik güvenlik analizi (SAST) yapılır.
5. Test ve SAST aşamaları başarılıysa Docker image build edilir.
6. Build edilen image, Trivy ile güvenlik taramasından geçirilir.
7. Image içinde fix'i bulunan HIGH veya CRITICAL seviye açık varsa pipeline burada durur.
8. Tüm kontroller geçerse `web/` klasörü **GitHub Pages'e canlı deploy** edilir.

## Local Çalıştırma

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tarayıcıdan test:

- http://localhost:8000
- http://localhost:8000/health
- http://localhost:8000/version

Statik sayfayı locale açmak için doğrudan `web/index.html` dosyasını tarayıcıda açabilirsin.

## Test Çalıştırma

```bash
pytest tests/
```

## Docker ile Çalıştırma

```bash
docker build -t ci-cd-demo .
docker run -p 8000:8000 ci-cd-demo
```

## GitHub Actions Demo Senaryosu

1. Repository GitHub'a yüklenir (`git push`).
2. `.github/workflows/ci-cd.yml` dosyası sayesinde pipeline GitHub tarafından otomatik tanınır.
3. `web/index.html` içindeki başlığı değiştir (görünür demo değişikliği).
4. Commit ve push atılır.
5. GitHub'da repo sayfasındaki **Actions** sekmesinden pipeline canlı izlenir.
6. Test ve güvenlik adımları başarılıysa son aşamada `deploy-pages` job'u çalışır.
7. Canlı sayfa (https://coskungencay.github.io/ci-cd-sau/) yenilenince yeni başlık görünür.

## Başarısız Pipeline Senaryosu (Fail Fast)

Demo sırasında bilerek bir testi bozarak pipeline'ın nasıl durduğunu gösterebiliriz. Örneğin `tests/test_main.py` içinde:

```python
assert response.status_code == 500
```

Bu durumda `pytest` aşaması başarısız olur, sonraki job'lar (`docker-build-and-trivy` ve `deploy-pages`) hiç çalışmaz. Canlı sayfa eski haliyle kalır. Bu, CI/CD'nin **fail fast** prensibidir: hatalı kod, boru hattının erken aşamalarında yakalanır; pahalı build/deploy adımlarına geçilmez ve üretim sayfası bozulmadan korunur.

## DevSecOps Security Gate Açıklaması

Workflow içindeki Trivy adımı `exit-code: 1` ile yapılandırılmıştır. Yani Trivy, image içinde fix'i bulunan HIGH veya CRITICAL seviye bir güvenlik açığı bulursa job'ı kasıtlı olarak başarısız bırakır. Bu durumda `deploy-pages` job'u tetiklenmez ve image deploy aşamasına ulaşamaz.

`ignore-unfixed: true` ayarı ile, henüz upstream'de fix yayınlanmamış CVE'ler pipeline'ı kırmaz; ama fix'i bulunan ciddi açık geldiğinde gate yine devreye girer. Bu, gerçek hayatta kullanılan dengeli bir yaklaşımdır.

Bu yaklaşım DevSecOps'ın temel fikrini somutlaştırır: **güvenlik kontrolleri yazılım geliştirme sürecinin sonuna eklenmez, doğrudan CI/CD pipeline'ın içine bir kapı (security gate) olarak yerleştirilir.**
