# Interdependent Tool Usage (Tool-Calling Agent)

## Project Summary
This project involves the development of an LLM-based autonomous agent capable of analyzing user requests, calling necessary external data sources (APIs) in the correct sequence, taking initiative when parameters are missing, and successfully executing interdependent functions (chaining).

The system is built on a decoupled architecture. The data layer, service layer (Flask REST API), and intelligence layer (Llama 3.3 powered Groq Agent) operate independently of each other.

## System Components
* **Data Layer (db.json):** A mock database that stores user information, transaction histories, and error logs.
* **Service Layer (server.py):** A Flask-based REST API that exposes the database information, featuring error management (e.g., 404 Not Found) and data sanitization (case-insensitive queries) capabilities.
* **Agent Layer (groq_agent.py):** An LLM module that processes natural language user queries, determines the necessary API endpoints, and synthesizes the returned JSON data to present the final report.

## Setup and Execution Steps

### 1. Installing Requirements
Before running the project, ensure that Python 3.8+ is installed on your system. Then, install the required libraries:
```bash
pip install flask requests groq
```

### 2. Environment Variables (API Key)
Ensure that a valid Groq API key is entered in the `client = Groq(api_key="...")` line within the `groq_agent.py` file. (Integrated into the code for the development phase).

### 3. Starting the API Server
First, bring up the Flask data server that will run in the background. Navigate to the project directory in your terminal and run the following command:
```bash
python server.py
```
The server will start running at `http://127.0.0.1:5000`. Do not close this terminal.

### 4. Starting the Agent
Open a new terminal window and start the Agent interface:
```bash
python groq_agent.py
```
Once the Agent is started, you can ask your questions in natural language via the terminal. You can type "exit" or "quit" to exit.

## Architectural Decisions and State Management
Critical architectural and design decisions taken in line with the evaluation criteria are summarized below:

### 1. State Management in the Agent System
State management within the system is dynamically structured through an "Agentic Loop" and "Message Payload" rather than global variables.

* **Temporary Memory (Context Window):** When a user asks a question, the `run_agent` function initiates an empty `messages` array. The model's tool call requests (`tool_calls`) and the JSON responses returned from the API (`tool_responses`) are appended to this array.
* **Interdependent Requests (Chaining):** The system features a loop structured as `for step in range(10)`. The agent repeatedly sends requests to the API until it reaches a conclusion (e.g., finding the ID, fetching the transactions, and determining the rejection reason). The memory (state) grows cumulatively within the `messages` array throughout this loop. Once the agent reaches a final decision, the loop breaks, and the answer is presented to the user. This structure prevents infinite loops while allowing for in-depth analysis.

### 2. Route and Limit Optimization (Why Groq & Llama 3.3?)
During the development process, it was identified that sequential tool calls created a bottleneck (Rate Limit / 429 Errors) on standard free API tiers. To overcome this problem and reduce the inference speed to milliseconds, the system was migrated to the Groq LPU infrastructure and the `Llama-3.3-70b-versatile` model.

### 3. Testability and Dynamic Data Reading
Considering the "unexpected situation (Chaos/Edge Case) tests" during the evaluation process, the `load_db()` function in the Flask server is designed to read the `db.json` file from scratch on every HTTP GET request, rather than keeping the data in memory (RAM). This ensures that new scenarios added to the database can be processed by the Agent instantly without restarting the server.

## Expected Features and Test Scenarios
The system successfully fulfills the following mandatory scenarios:

* **Interdependent Requests (Chaining):** When asked "What are the reasons for the rejected transactions in my account at ali@sirket.com?", the `get_user_details` -> `get_recent_transactions` -> `check_fraud_reason` tools are triggered automatically in sequence.
* **Missing Parameter Management:** When a user asks directly "Why was my payment rejected?", the system takes the initiative thanks to the LLM's natural language processing capability and completes the missing parameter by asking, "Please provide your email address so I can check."
* **Error Handling:** When an unregistered email is queried (e.g., olmayan@sirket.com), the Flask API returns a 404 Not Found. The Agent catches this exception without crashing and provides a professional response to the user, stating, "No user registered with this email address was found in our system." Similarly, it does not unnecessarily perform fraud checks for successful transactions that have no rejection reason.

---

# Birbirine Bağımlı Araç Kullanımı (Tool-Calling Agent)

## Proje Özeti
Bu proje, kullanıcı taleplerini analiz ederek gerekli dış veri kaynaklarını (API) doğru sırayla çağıran, eksik parametre durumunda inisiyatif alabilen ve birbirine bağımlı fonksiyonları (chaining) başarıyla çalıştırabilen LLM tabanlı bir otonom ajanın (Agent) geliştirilmesini içermektedir.

Sistem, ayrıştırılmış (decoupled) bir mimari üzerine inşa edilmiştir. Veri katmanı, servis katmanı (Flask REST API) ve zeka katmanı (Llama 3.3 destekli Groq Agent) birbirinden bağımsız olarak çalışmaktadır.

## Sistem Bileşenleri
* **Veri Katmanı (db.json):** Kullanıcı bilgilerini, işlem geçmişlerini ve hata loglarını tutan mock veritabanı.
* **Servis Katmanı (server.py):** Veritabanındaki bilgileri dışarıya açan, hata yönetimi (404 Not Found vb.) ve veri temizleme (case-insensitive sorgular) yeteneklerine sahip Flask tabanlı REST API.
* **Agent Katmanı (groq_agent.py):** Kullanıcının doğal dildeki sorularını işleyen, gerekli API uç noktalarına karar veren ve dönen JSON verilerini sentezleyerek nihai raporu sunan LLM modülü.

## Kurulum ve Çalıştırma Adımları

### 1. Gereksinimlerin Yüklenmesi
Projeyi çalıştırmadan önce sisteminizde Python 3.8+ kurulu olduğundan emin olun. Ardından gerekli kütüphaneleri yükleyin:
```bash
pip install flask requests groq
```

### 2. Ortam Değişkenleri (API Key)
`groq_agent.py` dosyası içerisinde yer alan `client = Groq(api_key="...")` satırına geçerli bir Groq API anahtarı girildiğinden emin olun. (Geliştirme aşamasında kod içerisine entegre edilmiştir).

### 3. API Sunucusunun Başlatılması
İlk olarak arka planda çalışacak olan Flask veri sunucusunu ayağa kaldırın. Terminalde proje dizinine giderek şu komutu çalıştırın:
```bash
python server.py
```
Sunucu `http://127.0.0.1:5000` adresinde çalışmaya başlayacaktır. Bu terminali kapatmayın.

### 4. Agent'ın Çalıştırılması
Yeni bir terminal penceresi açın ve Agent arayüzünü başlatın:
```bash
python groq_agent.py
```
Agent başlatıldıktan sonra terminal üzerinden doğal dille sorularınızı yöneltebilirsiniz. Çıkış yapmak için "exit" veya "quit" yazabilirsiniz.

## Mimari Kararlar ve State (Durum) Yönetimi
Değerlendirme kriterleri kapsamında alınan kritik mimari ve tasarımsal kararlar aşağıda özetlenmiştir:

### 1. Agent Sisteminde State (Durum) Yönetimi
Sistemde State yönetimi, global değişkenler yerine "Agentic Loop" (Ajan Döngüsü) ve "Message Payload" (Mesaj Yükü) üzerinden dinamik olarak kurgulanmıştır.

* **Geçici Hafıza (Context Window):** Kullanıcı bir soru sorduğunda, `run_agent` fonksiyonu boş bir `messages` dizisi başlatır. Modelin araç çağırma talepleri (`tool_calls`) ve API'den dönen JSON yanıtları (`tool_responses`) bu diziye append edilerek eklenir.
* **Bağımlı İstekler (Chaining):** Sistem `for step in range(10)` şeklinde bir döngüye sahiptir. Ajan, sonuca ulaşana kadar (örneğin ID'yi bulup, işlemleri çekip, red sebebini bulana dek) API'ye tekrar tekrar istek atar. Hafıza (state) bu döngü boyunca `messages` dizisi içinde kümülatif olarak büyür. Ajan nihai karara vardığında döngü kırılır ve cevap kullanıcıya sunulur. Bu yapı, sonsuz döngüleri engellerken derinlemesine analize olanak tanır.

### 2. Rota ve Limit Optimizasyonu (Neden Groq & Llama 3.3?)
Geliştirme sürecinde birbirine bağımlı ve ardışık araç çağrılarının (Sequential Tool Calling) standart ücretsiz API katmanlarında (Rate Limit / 429 Hataları) darboğaz yarattığı tespit edilmiştir. Bu problemi aşmak ve çıkarım (inference) hızını milisaniyeler seviyesine indirmek amacıyla sistem Groq LPU altyapısına ve `Llama-3.3-70b-versatile` modeline taşınmıştır.

### 3. Test Edilebilirlik ve Dinamik Veri Okuma
Değerlendirme sürecindeki "beklenmedik durum (Chaos/Edge Case) testleri" göz önüne alınarak, Flask sunucusundaki `load_db()` fonksiyonu veriyi bellekte (RAM) tutmak yerine, her HTTP GET isteğinde `db.json` dosyasını baştan okuyacak şekilde tasarlanmıştır. Bu sayede sunucu yeniden başlatılmadan veritabanına eklenen yeni senaryolar anında Agent tarafından işlenebilmektedir.

## Beklenen İşlevler ve Test Senaryoları
Sistem aşağıdaki zorunlu senaryoları başarıyla yerine getirmektedir:

* **Bağımlı İstekler (Chaining):** "ali@sirket.com adresli hesabımdaki reddedilen işlemlerin sebepleri nelerdir?" sorusunda sırasıyla `get_user_details` -> `get_recent_transactions` -> `check_fraud_reason` araçları otomatik olarak tetiklenir.
* **Eksik Parametre Yönetimi:** Kullanıcı doğrudan "Ödemem neden reddedildi?" diye sorduğunda, sistem LLM'in doğal dil işleme yeteneği sayesinde "Lütfen kontrol edebilmem için e-posta adresinizi belirtin" şeklinde inisiyatif alarak eksik parametreyi tamamlatır.
* **Hata Yönetimi (Error Handling):** Veritabanında olmayan bir e-posta sorgulandığında (Örn: olmayan@sirket.com), Flask API 404 Not Found döner. Agent bu hatayı (Exception) yakalayarak çökmez ve kullanıcıya "Sistemimizde bu e-posta adresiyle kayıtlı bir kullanıcı bulunamadı" şeklinde profesyonel bir dönüş yapar. Aynı şekilde red sebebi bulunmayan başarılı işlemler için gereksiz yere fraud (dolandırıcılık) kontrolü yapmaz.

---
---
