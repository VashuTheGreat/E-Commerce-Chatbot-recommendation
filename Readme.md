{"id":"78921","variant":"standard","title":"Fashion Recommendation Chatbot README"}
# 🛍️ Fashion Recommendation Chatbot

This project is an **AI-powered chatbot** for e-commerce, designed to help customers discover products by interacting with a conversational interface. Users can upload product images, ask questions, and receive personalized product recommendations based on the uploaded image and textual queries.

---

## 🔹 Features

* Upload product images and get recommendations.
* Chat interface for asking product-related queries.
* Fetches product metadata such as brand, price, and discounts.
* Interactive display of recommended products with images.
* Stores chat history per session/thread for future reference.

---

## 🔹 Dataset

This project uses the **Fashion Product Images dataset** from Kaggle:

* Dataset 1 (Small): `paramaggarwal/fashion-product-images-small`
* Dataset 2 (Latest version): `paramaggarwal/fashion-product-images-dataset`

You can download datasets using the [`kagglehub`](https://pypi.org/project/kagglehub/) library:

```python
import kagglehub

# Download small dataset
path_small = kagglehub.dataset_download("paramaggarwal/fashion-product-images-small")
print("Path to small dataset:", path_small)

# Download latest dataset
path_latest = kagglehub.dataset_download("paramaggarwal/fashion-product-images-dataset")
print("Path to latest dataset:", path_latest)
```

* `styles.csv` contains product metadata like brand, category, and product name.
* Image files are stored in structured folders in the dataset.

---

## 🔹 Installation

1. Clone this repository:

```bash
git clone <your-repo-url>
cd <repo-folder>
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure you have `kagglehub` installed to fetch datasets:

```bash
pip install kagglehub
```

---

## 🔹 Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. Open the app in your browser:

* Upload an image of a product (e.g., glasses, shirt, shoes).
* Ask questions or describe what kind of recommendation you want.
* Chatbot will show recommended products with images, brand, price, and discount details.

---

## 🔹 Folder Structure

```
E-COMMERECECHAT/
├─ app.py                 # Streamlit app
├─ chat.py                # Chatbot logic
├─ main.py                # Optional script runner
├─ db.py                  # Database handler
├─ data/
│  ├─ styles/             # JSON files of individual products
│  ├─ images.csv           # Metadata CSV
│  ├─ db.pkl               # Serialized database
│  └─ threads.json         # Stored chat sessions
├─ tempImage/             # Uploaded product images
├─ testImage/             # Test images
├─ references/            # Reference screenshots/images
├─ requirements.txt
├─ .env                   # Environment variables
├─ .gitignore
└─ myvenv/                # Python virtual environment
```

---

## 🔹 Future Improvements

* Add **multi-image support** for batch recommendations.
* Integrate **AI-based similarity search** using embeddings.
* Add **user authentication** and persistent storage for returning customers.
* Enhance UI for better mobile responsiveness.

---

## 🔹 License

MIT License  

Made with ❤️ by VashuTheGreat
