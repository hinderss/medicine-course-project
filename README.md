# 🏥 Медицинская система

**Медицинская система** — это веб-приложение, обеспечивающее взаимодействие между врачами и пациентами, включая регистрацию, ведение медицинских карт, предварительную диагностику, работу с ИИ и связь с внешними медицинскими сервисами ([Ostis](https://github.com/ostis-apps/ostis-example-app) и GPT).

---

## ⚙️ Используемые технологии

* **Backend**: Flask, SQLAlchemy, Marshmallow, Flask-WTF, Flask-Login, Flask-Migrate
* **Frontend**: HTML, CSS, JavaScript, SCSS
* **AI/LLM**: OpenAI / Gemini (Langchain), Ollama (альтернатива)
* **Интеграции**:

  * **Ostis** микросервис (через `agent.py`)
  * **Langchain GPT** — генерация AI-ответов в медицинском чате

---

## 🧩 Микросервисы

### 1. 🧠 Ostis (через `AgentsClient` в `agent.py`)

* URL настраивается через `.env`: `AGENTS_URL`

### 2. 🤖 GPT (LangChain/OpenAI или Ollama)

* Конфигурация через `.env`:

  * `GPT_URL`
  * `GPT_API_KEY`
* Используется Langchain (`ChatPromptTemplate`) в `routes.py`:

  * Общение с AI ассистентом по медицинским вопросам
  * Контекстные ответы на основе истории и endpoint

---

## 🧪 Установка и запуск

### 1. 📦 Клонируйте проект

```bash
git clone https://github.com/your-username/medicine-course-project.git
cd medicine-course-project
```

### 2. 🐍 Создайте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 📄 Установите зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. ⚙️ Настройте `.env`

Создайте `.env` файл в корне со следующими переменными:

```env
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite3  # или ваша БД
UPLOAD_FOLDER=instance/
DISEASES_XML=disease_definer/diseases.xml
AGENTS_URL=http://localhost:8001
GPT_URL=https://api.gemini.google.com
GPT_API_KEY=your_openai_or_gemini_key
```

### 5. 🗄️ Инициализация БД

```bash
flask db init
flask db migrate
flask db upgrade
```

### 6. ▶️ Запуск

```bash
python run.py 
```

## 🛠️ Зависимости и версии (фрагмент)

См. `requirements.txt`, примеры:

```txt
Flask==3.0.2
Flask-SQLAlchemy==3.1.1
langchain==0.3.25
google-genai==1.14.0
openai==1.78.0
requests==2.32.3
...
```