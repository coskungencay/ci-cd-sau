# CI/CD + DevSecOps Demo

## Projenin Amacı

Bu demo, GitHub Actions kullanarak basit bir cloud-based CI/CD ve DevSecOps pipeline'ın nasıl çalıştığını göstermek için hazırlanmıştır. Geliştiricinin yaptığı bir commit'in nasıl otomatik olarak test edildiğini, statik kod analizinden geçirildiğini, Docker image olarak paketlendiğini, container güvenlik taramasından geçirildiğini ve son olarak deploy aşamasına ulaştığını uçtan uca gösterir.

## Kullanılan Teknolojiler

- **FastAPI** — Demo edilecek küçük Python web API
- **pytest** — Unit test framework
- **Docker** — Uygulamanın container olarak paketlenmesi
- **GitHub Actions** — CI/CD pipeline orchestrator
- **Semgrep** — Statik kod analizi (SAST)
- **Trivy** — Container/image güvenlik taraması (SCA + image scan)

## Pipeline Akışı

1. Geliştirici kodda değişiklik yapar ve GitHub'a push eder.
2. GitHub Actions otomatik olarak `CI/CD + DevSecOps Demo Pipeline` workflow'unu başlatır.
3. Unit testler `pytest` ile çalıştırılır.
4. Semgrep ile statik güvenlik analizi (SAST) yapılır.
5. Test ve SAST aşamaları başarılıysa Docker image build edilir.
6. Build edilen image, Trivy ile güvenlik taramasından geçirilir.
7. Image içinde HIGH veya CRITICAL seviye açık varsa pipeline burada durur.
8. Tüm kontroller geçerse deploy simülasyonu çalışır.

## Local Çalıştırma

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tarayıcıdan test:

- http://localhost:8000
- http://localhost:8000/health
- http://localhost:8000/version

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
3. Kodda küçük bir değişiklik yapılır.
4. Commit ve push atılır.
5. GitHub'da repo sayfasındaki **Actions** sekmesinden pipeline canlı izlenir.
6. Test ve güvenlik adımları başarılıysa son aşamada `deploy-simulation` job'u çalışır ve pipeline yeşile döner.

## Başarısız Pipeline Senaryosu (Fail Fast)

Demo sırasında bilerek bir testi bozarak pipeline'ın nasıl durduğunu gösterebiliriz. Örneğin `tests/test_main.py` içinde:

```python
assert response.status_code == 500
```

Bu durumda `pytest` aşaması başarısız olur, sonraki job'lar (`docker-build-and-trivy` ve `deploy-simulation`) hiç çalışmaz. Bu, CI/CD'nin **fail fast** prensibidir: hatalı kod, boru hattının erken aşamalarında yakalanır ve daha pahalı/yavaş olan adımlara geçilmez.

## DevSecOps Security Gate Açıklaması

Workflow içindeki Trivy adımı `exit-code: 1` ile yapılandırılmıştır. Yani Trivy, image içinde HIGH veya CRITICAL seviye bir güvenlik açığı bulursa job'ı kasıtlı olarak başarısız bırakır. Bu durumda `deploy-simulation` job'u tetiklenmez ve image deploy aşamasına ulaşamaz.

Bu yaklaşım DevSecOps'ın temel fikrini somutlaştırır: **güvenlik kontrolleri yazılım geliştirme sürecinin sonuna eklenmez, doğrudan CI/CD pipeline'ın içine bir kapı (security gate) olarak yerleştirilir.**
