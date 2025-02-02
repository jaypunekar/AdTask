# 📢 Google Ads Campaign Chatbot

🚀 A simple **Flask chatbot** that helps you create **Google Ads campaigns** step by step.  
It asks you **questions** and sets up a campaign **automatically**! 🎯  
Demo Video: https://www.youtube.com/watch?v=vb9FDPiK8WE

---

## 📌 Features

✅ **Talk to the chatbot** to set up a Google Ads campaign  
✅ **No need to enter Customer ID** (It takes it from `google-ads.yaml`)  
✅ **Validates campaign details** (Budget, Dates, etc.)  
✅ **Creates Google Ads campaign using API**  
✅ **Clears chat after campaign is made**  

---

## 🛠️ How It Works

1️⃣ **Start the chatbot**  
2️⃣ **Answer simple questions** (Campaign name, budget, type, etc.)  
3️⃣ **Review campaign details**  
4️⃣ **Say "Yes" to publish or "No" to clear chat**  
5️⃣ **Campaign is created automatically!** 🎉  

---

## 🔧 Set Up Google Ads API
Google Ads API Docs: https://developers.google.com/google-ads/api/docs/start

### 1️⃣ Enable Google Ads API
1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**  
2. Create a **new project** (or select an existing one)  
3. Enable **Google Ads API**  

### 2️⃣ Create API Credentials
1. Go to **[Google Ads API Credentials](https://console.cloud.google.com/apis/credentials)**  
2. Click **Create Credentials** → Select **OAuth Client ID**  
3. Download the `google-ads.yaml` file  

### 3️⃣ Set Up `google-ads.yaml`
Create a file **`google-ads.yaml`** in your project folder and add:

```yaml
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_CLIENT_ID
client_secret: YOUR_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
login_customer_id: YOUR_CUSTOMER_ID
```


```
## 📂 Project Structure
📂 adTask/
 ├── 📄 app.py           # Flask chatbot & campaign creation logic
 ├── 📄 google-ads.yaml  # Stores API credentials (Customer ID)
 ├── 📂 static/          # CSS and assets
 ├── 📂 templates/       # HTML files
     ├── 📄 chat.html    # Chatbot UI (front-end)
 └── 📄 requirements.txt # Python dependencies
```
## 💻 Installation

### 1️⃣ Install Dependencies
```sh
pip install -r requirements.txt

python app.py
```
Make sure you have Google Ads API properly setup or this won't work.
