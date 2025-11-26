from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import pickle
import os
from jsonFileDataExtreactor import extract_product_info_with_image
import json
from tqdm import tqdm
# Example products
# products = [
#     {
#         "main_product": {
#             "name": "Nike Sahara Team India Fanwear Round Neck Jersey",
#             "color": "Blue",
#             "pattern": "",
#             "type_style": "",
#             "category_or_gender": "Men",
#         },
#         "additional_info": {
#             "brand": "Nike",
#             "price": 895,
#             "discountedPrice": 795,
#             "image_url": "http://assets.myntassets.com/v1/images/style/properties/Nike-Sahara-Team-India-Fanwear-Round-Neck-Jersey_2d27392cc7d7730e8fee0755fd41d30c_images.jpg",
#         },
#     },
#     {
#         "main_product": {
#             "name": "Adidas Essentials 3-Stripes T-Shirt",
#             "color": "Black",
#             "pattern": "Plain",
#             "type_style": "Round Neck",
#             "category_or_gender": "Men",
#         },
#         "additional_info": {
#             "brand": "Adidas",
#             "price": 1200,
#             "discountedPrice": 999,
#             "image_url": "http://assets.myntassets.com/v1/images/style/properties/Adidas-Essentials-3-Stripes-T-Shirt_abc123_images.jpg",
#         },
#     },
#     {
#         "main_product": {
#             "name": "Puma Women's Running Shoes",
#             "color": "Pink",
#             "pattern": "Plain",
#             "type_style": "Lace-up",
#             "category_or_gender": "Women",
#         },
#         "additional_info": {
#             "brand": "Puma",
#             "price": 2999,
#             "discountedPrice": 2599,
#             "image_url": "http://assets.myntassets.com/v1/images/style/properties/Puma-Womens-Running-Shoes_xyz456_images.jpg",
#         },
#     },
# ]


products=[]


for i in  tqdm(os.listdir("./styles")):
    if i.endswith(".json"):
        
        with open(f"./styles/{i}","rb") as f:
            data=json.load(f)
            data=extract_product_info_with_image(data)
            products.append(data)




# Prepare texts and metadata
texts = []
metadatas = []

for product in tqdm(products):
    # Flatten main_product to string
    doc_text = " | ".join([f"{k}: {v}" for k, v in product["main_product"].items()])
    texts.append(doc_text)
    # Metadata from additional_info
    metadatas.append(product["additional_info"])

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Convert into FAISS vector DB
vector_db = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

# Save DB
with open("db.pkl", "wb") as f:
    pickle.dump(vector_db, f)
    print("Vector Db Saved")

# Query example
query = "Blue men's jersey"
results = vector_db.similarity_search(query, k=3)

for r in results:
    print("Text:", r.page_content)
    print("Metadata:", r.metadata)
