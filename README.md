# Tamil-Arwi Transliterator API

This is a Flask-based service that transliterates Tamil text to Arwi script using the Gemini API and optional Google Sheets data.

## 🚀 Deployment (Render)

1. Push this repo to GitHub
2. Go to https://render.com
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Fill in:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `./start.sh`
   - Add an environment variable:
     - Key: `API_KEY`
     - Value: your Gemini API key from https://makersuite.google.com/app/apikey
6. Deploy and use the URL like:

```http
POST /transliterate
{
  "tamil_input": "வணக்கம்",
  "data_source": "google_sheet"
}
```
