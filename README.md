

# AgroSphere

**AgroSphere** is an intelligent agricultural insight platform designed to empower farmers, researchers, and planners with localized, data-driven recommendations. It combines environmental data sources and feeds them into a powerful Large Language Model (LLM) to generate clear, human-readable summaries tailored to specific locations.

---


## 🌐 Data Sources & API Setup

AgroSphere gathers data from multiple APIs:

### 1. **Soil Data — ISDA Africa API**
- **Endpoint**: `https://api.isda-africa.com/login`
- Authenticated via **access token** stored in `.env`
- Retrieved using an **async function** for efficiency.

#### 🔧 Setup:
- Register at [ISDA Developer Portal](https://www.isda-africa.com/isdasoil/developer/)
- Add the following to your `.env` file:
  ```env
  ISDA_USERNAME=your_email_here
  ISDA_PASSWORD=your_password_here
  ISDA_TOKEN=your_access_token_here


### 2. **Weather Data — Open-Meteo API**

* **Forecast endpoint**: `https://api.open-meteo.com/v1/forecast`
* **Historical endpoint**: `https://historical-forecast-api.open-meteo.com/v1/archive?`
* Handled via the `weather.py` module in the backend.

#### 🔧 Setup:

* No API key required.
* Data is fetched using latitude and longitude through simple GET requests.

### 3. **Elevation Data — OpenTopoData API**

* **Endpoint**: `https://api.opentopodata.org/v1/srtm90m`

#### 🔧 Setup:

* No API key needed.
* You send GET requests with lat/lon to retrieve elevation values.

### 4. **Location Data — OpenCage Geocoder API**

* **Endpoint**: `https://api.opencagedata.com/geocode/v1/json`

#### 🔧 Setup:

* Sign up at [OpenCage](https://opencagedata.com/) to obtain your API key.
* Add to your `.env` file:

  ```env
  OPENCAGE_API_KEY=your_opencage_api_key
  ```

 ### 5. **Gemini LLM Setup**:
 
 #### 🔧 Setup:

* Go to the Google AI Studio or Google Cloud Console to get your Gemini API key.
* Enable the Generative Language API in your project.
* Add the API key to your .env file:

  ```env
  GEMINI_API_KEY=your_gemini_api_key_here
  ```
---

## 💻 Running the Project

### 1. Clone and Set Up a Virtual Environment

```bash
git clone https://github.com/Leoul39/AgroSphere.git
cd AgroSphere
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
cd backend
uvicorn mainapi:app --reload
```

This will start the FastAPI server on `http://127.0.0.1:8000`.

### 3. Start the Frontend

* Navigate to the `frontend` directory.
* Open `front.html` using **Live Server** (e.g., via VS Code extension).
* Visit `http://127.0.0.1:5500/frontend/front.html`.
* Input coordinates and click **"Generate Summary"** to view the AI-generated insights.

---

## 🔒 .env File

Create a `.env` file at the root level of the project (not tracked by Git). It should include:

```env
ISDA_USERNAME=your_email
ISDA_PASSWORD=your_password
ISDA_TOKEN=your_access_token
OPENCAGE_API_KEY=your_opencage_api_key
GEMINI_API_KEY=your_gemini_api_key
```

This file is critical for authenticating to the required APIs.

---

## 📜 License

This project is licensed under the terms defined in the `LICENSE` file located at the root of this repository.

---

## 🙋‍♂️ Contributing & Feedback

Contributions, bug reports, and feature suggestions are welcome! Feel free to open issues or submit pull requests. Whether it's a bug fix or UI improvement, your input is valued.

---

## ✨ Future Improvements

* Add user authentication and login
* Deploy on cloud platforms (e.g., Render, Heroku, AWS)
* Enable support for local languages (Amharic, Afaan Oromo, etc.)
* Save and view historical query summaries
* Add a database to persist soil/weather lookup history

