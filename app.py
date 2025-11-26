# import streamlit as st
# import os
# import uuid
# from chat import response

# # ---------------------------------------
# # CREATE FOLDER
# # ---------------------------------------
# if not os.path.exists("tempImage"):
#     os.makedirs("tempImage")

# # ---------------------------------------
# # SESSION STATE INIT
# # ---------------------------------------
# if "threads" not in st.session_state:
#     st.session_state.threads = []

# if "current_thread" not in st.session_state:
#     st.session_state.current_thread = None

# if "image_uploaded" not in st.session_state:
#     st.session_state.image_uploaded = False

# # Thread → Full Chat History Store
# if "thread_data" not in st.session_state:
#     st.session_state.thread_data = {}   # { thread_id: [history objects] }



# # ---------------------------------------
# # SIDEBAR - THREAD UI
# # ---------------------------------------
# st.sidebar.title("📌 Threads")

# selected_thread = st.sidebar.radio("Select Thread", st.session_state.threads)

# if selected_thread:
#     st.session_state.current_thread = selected_thread

# # CREATE NEW THREAD
# if st.sidebar.button("➕ Create New Thread"):
#     new_id = str(uuid.uuid4())[:8]
#     st.session_state.threads.append(new_id)
#     st.session_state.current_thread = new_id
#     st.session_state.image_uploaded = False
#     st.session_state.thread_data[new_id] = []
#     st.rerun()


# # ---------------------------------------
# # NO THREAD → STOP
# # ---------------------------------------
# if not st.session_state.current_thread:
#     st.title("Fashion Recommendation Chatbot")
#     st.write("Left side se koi thread choose karo ya naya banao.")
#     st.stop()

# thread_id = st.session_state.current_thread

# if thread_id not in st.session_state.thread_data:
#     st.session_state.thread_data[thread_id] = []

# st.title(f"🧵 Thread: {thread_id}")


# # ---------------------------------------
# # IMAGE UPLOAD
# # ---------------------------------------
# st.subheader("Upload Product Image")

# uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

# if uploaded_file:
#     img_path = f"./tempImage/{thread_id}.jpg"

#     with open(img_path, "wb") as f:
#         f.write(uploaded_file.read())

#     st.session_state.image_uploaded = True
#     st.image(img_path, width=250)
#     st.success("Image saved for this thread!")


# # ---------------------------------------
# # CHAT HISTORY (Always above input)
# # ---------------------------------------
# st.subheader("📜 Chat History")

# history = st.session_state.thread_data[thread_id]

# if not history:
#     st.info("No chats yet in this thread.")
# else:
#     for h in history:

#         # USER QUERY
#         if "user_query" in h:
#             st.chat_message("user").markdown(h["user_query"])

#         # SEARCH QUERY (no JSON displayed)
#         if "llm_query" in h:
#             st.chat_message("assistant").markdown(
#                 f"### 🔍 Search Query\n`{h['llm_query']}`"
#             )

#         # RECOMMENDATIONS
#         if "db_res" in h:
#             st.chat_message("assistant").markdown("### 🎯 Recommended Products")

#             for item in h["db_res"]:
#                 meta = item.get("metadata", {})
#                 content = item.get("page_content", "")

#                 col1, col2 = st.columns([1, 2])
#                 with col1:
#                     if meta.get("image_url"):
#                         st.image(meta.get("image_url"), width=140)

#                 with col2:
#                     st.markdown(f"**{content}**")
#                     st.write(f"Brand: {meta.get('brand')}")
#                     st.write(f"Price: ₹{meta.get('price')}")
#                     st.write(f"Discounted: ₹{meta.get('discountedPrice')}")

#         # SUMMARY (BIG COLOR FIX)
#         if "summary" in h:
#             st.chat_message("assistant").markdown(
#                 f"""
#                 <div style="
#                     background:#FFE5B4;
#                     padding:14px;
#                     border-left:6px solid #FF8C00;
#                     border-radius:8px;
#                     font-size:16px;
#                     color:#000;
#                 ">
#                 <strong>📝 Final Summary:</strong><br>{h['summary']}
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )

# # END HISTORY BLOCK
# st.markdown("---")


# # ---------------------------------------
# # INPUT BOX (ALWAYS BOTTOM)
# # ---------------------------------------
# st.subheader("Ask Something")

# user_query = st.text_input("Type your query:")

# if st.button("Send Query"):

#     if not st.session_state.image_uploaded:
#         st.error("Please upload an image first.")
#     else:
#         with st.spinner("Thinking..."):
#             result = response(thread_id=thread_id, query=user_query)

#         # SAVE INTO THREAD HISTORY
#         st.session_state.thread_data[thread_id].append(result)

#         st.success("Response saved!")
#         st.rerun()









# {"variant":"standard","id":"92751","title":"Final Streamlit UI — Fully Fixed Version"}
# import streamlit as st
# import os
# import uuid
# import json
# from chat import response, get_thread_history

# # =====================================================
# #  Permanent Storage Setup (JSON based)
# # =====================================================
# DATA_FILE = "data/threads.json"
# os.makedirs("data", exist_ok=True)
# os.makedirs("tempImage", exist_ok=True)

# def load_data():
#     if not os.path.exists(DATA_FILE):
#         return {}
#     with open(DATA_FILE, "r") as f:
#         return json.load(f)

# def save_data(data):
#     with open(DATA_FILE, "w") as f:
#         json.dump(data, f, indent=4)


# # =====================================================
# #  Session State Initialization
# # =====================================================
# if "thread_data" not in st.session_state:
#     st.session_state.thread_data = load_data()

# if "threads" not in st.session_state:
#     st.session_state.threads = list(st.session_state.thread_data.keys())

# if "current_thread" not in st.session_state:
#     st.session_state.current_thread = None

# if "image_uploaded" not in st.session_state:
#     st.session_state.image_uploaded = False


# # =====================================================
# # Sidebar Thread Management
# # =====================================================
# st.sidebar.title("📌 Threads")

# if st.session_state.threads:
#     selected_thread = st.sidebar.radio("Select Thread", st.session_state.threads)
#     st.session_state.current_thread = selected_thread

# # Create New Thread
# if st.sidebar.button("➕ Create New Thread"):
#     new_id = str(uuid.uuid4())[:8]
#     st.session_state.threads.append(new_id)
#     st.session_state.thread_data[new_id] = []
#     save_data(st.session_state.thread_data)
#     st.session_state.current_thread = new_id
#     st.session_state.image_uploaded = False
#     st.rerun()


# # =====================================================
# # No Thread Selected
# # =====================================================
# if not st.session_state.current_thread:
#     st.title("Fashion Recommendation Chatbot")
#     st.write("Left side se koi thread choose karo ya naya thread banao.")
#     st.stop()

# thread_id = st.session_state.current_thread
# st.title(f"🧵 Thread: {thread_id}")


# # =====================================================
# # Image Upload
# # =====================================================
# st.subheader("Upload Product Image")

# uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

# if uploaded_file:
#     img_path = f"./tempImage/{thread_id}.jpg"

#     with open(img_path, "wb") as f:
#         f.write(uploaded_file.read())

#     st.session_state.image_uploaded = True
#     st.image(img_path, width=250)
#     st.success("Image saved for this thread!")

#     save_data(st.session_state.thread_data)


# # =====================================================
# # Chat Input (Always Bottom)
# # =====================================================
# st.markdown("---")
# st.subheader("💬 Ask Something")

# user_query = st.text_input("Type your query:")

# if st.button("Send Query"):
#     if not st.session_state.image_uploaded:
#         st.error("Please upload an image before chatting.")
#     else:
#         with st.spinner("Thinking..."):
#             result = response(thread_id=thread_id, query=user_query)

#         st.session_state.thread_data[thread_id].append(result)
#         save_data(st.session_state.thread_data)

#         st.success("Response received!")
#         st.rerun()


# # =====================================================
# # Chat History Rendering
# # =====================================================
# st.markdown("---")
# st.subheader("📜 Chat History")

# history = st.session_state.thread_data.get(thread_id, [])

# if not history:
#     st.info("No chats yet in this thread.")
# else:
#     for h in history:
#         if h.get("user_query"):
#             st.chat_message("user").markdown(h["user_query"])

#         if h.get("llm_query"):
#             st.chat_message("assistant").markdown(
#                 f"### 🔍 Search Query\n`{h['llm_query']}`"
#             )

#         if h.get("db_res"):
#             st.chat_message("assistant").markdown("### 🎯 Recommended Products")

#             for item in h["db_res"]:
#                 meta = item.get("metadata", {})
#                 content = item.get("page_content", "")

#                 with st.container():
#                     col1, col2 = st.columns([1, 2])

#                     with col1:
#                         img_url = meta.get("image_url")
#                         if img_url:
#                             st.image(img_url, width=140)

#                     with col2:
#                         st.markdown(f"**{content}**")
#                         st.write(f"Brand: {meta.get('brand')}")
#                         st.write(f"Price: ₹{meta.get('price')}")
#                         st.write(f"Discounted: ₹{meta.get('discountedPrice')}")

#         if h.get("summary"):
#             st.chat_message("assistant").markdown(
#                 f"""
#                 <div style="background:#FFF7D1;padding:14px;border-left:6px solid #FFC300;border-radius:8px;">
#                 <strong>📝 Summary:</strong><br>{h['summary']}
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )





import streamlit as st
import os
import uuid
import json
from chat import response, get_thread_history

import streamlit as st
import requests
from io import BytesIO

# =====================================================
#  Permanent Storage Setup (JSON based)
# =====================================================
DATA_FILE = "data/threads.json"
os.makedirs("data", exist_ok=True)
os.makedirs("tempImage", exist_ok=True)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =====================================================
#  Session State Initialization
# =====================================================
if "thread_data" not in st.session_state:
    st.session_state.thread_data = load_data()

if "threads" not in st.session_state:
    st.session_state.threads = list(st.session_state.thread_data.keys())

if "current_thread" not in st.session_state:
    st.session_state.current_thread = None

if "image_uploaded" not in st.session_state:
    st.session_state.image_uploaded = False


# =====================================================
# Sidebar Thread Management
# =====================================================
st.sidebar.title("📌 Threads")

if st.session_state.threads:
    selected_thread = st.sidebar.radio("Select Thread", st.session_state.threads)
    st.session_state.current_thread = selected_thread

# Create New Thread
if st.sidebar.button("➕ Create New Thread"):
    new_id = str(uuid.uuid4())[:8]
    st.session_state.threads.append(new_id)
    st.session_state.thread_data[new_id] = []
    save_data(st.session_state.thread_data)
    st.session_state.current_thread = new_id
    st.session_state.image_uploaded = False
    st.rerun()


# =====================================================
# If no thread selected
# =====================================================
if not st.session_state.current_thread:
    st.title("Fashion Recommendation Chatbot")
    st.write("Left side se koi thread choose karo ya naya thread banao.")
    st.stop()

thread_id = st.session_state.current_thread
st.title(f"🧵 Thread: {thread_id}")


# =====================================================
# Image Upload
# =====================================================
st.subheader("Upload Product Image")
uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img_path = f"./tempImage/{thread_id}.jpg"
    with open(img_path, "wb") as f:
        f.write(uploaded_file.read())

    st.session_state.image_uploaded = True
    st.image(img_path, width=250)
    st.success("Image saved for this thread!")

    save_data(st.session_state.thread_data)

    st.image(uploaded_file, caption="Selected Image", width=280, use_column_width=False)

    # -----------------------------
    # Predict Button
    # -----------------------------
    if st.button("Upload & Predict"):
        st.info("⏳ Analyzing and fetching recommendations...")

        # Simulate server request
        # Replace the URL and request as per your backend / API
        files = {"file": uploaded_file.getvalue()}
        try:
            # Example: change URL to your prediction endpoint
            response = requests.post("http://localhost:8000/predict", files={"file": uploaded_file})
            data = response.json()
            results = data.get("result", [])
            json_data = data.get("json_data", [])

            # -----------------------------
            # Show recommended products
            # -----------------------------
            cols = st.columns(3)
            for idx, img_url in enumerate(results):
                col = cols[idx % 3]
                with col:
                    st.image(img_url, width=220)
                    info_html = "<p>No metadata found</p>"
                    if idx < len(json_data):
                        try:
                            import json as js
                            parsed = js.loads(json_data[idx])
                            d = parsed.get("data", {})
                            brand = d.get("brand", "Unknown Brand")
                            desc = d.get("productName", "No Description")
                            price = f"₹{d.get('price')}" if d.get("price") else "N/A"
                            discount = f"₹{d.get('discountedPrice')}" if d.get("discountedPrice") else None

                            info_html = f"<h4>{brand}</h4><p>{desc}</p><p style='color:#007bff;font-weight:bold;'>Price: {price}</p>"
                            if discount and discount != price:
                                info_html += f"<p style='color:#28a745;font-weight:bold;'>Discounted: {discount}</p>"
                        except:
                            info_html = "<p>Invalid product metadata</p>"

                    st.markdown(info_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")



# =====================================================
# CHAT HISTORY (Always above Input Box)
# =====================================================
st.markdown("---")
st.subheader("📜 Chat History")

history = st.session_state.thread_data.get(thread_id, [])

if not history:
    st.info("No chats yet in this thread.")
else:
    for h in history:

        # USER MESSAGE
        if h.get("user_query"):
            st.chat_message("user").markdown(h["user_query"])

        # SEARCH QUERY
        if h.get("llm_query"):
            st.chat_message("assistant").markdown(
                f"### 🔍 Search Query\n`{h['llm_query']}`"
            )

        # RECOMMENDATION RESULTS
        if h.get("db_res"):
            st.chat_message("assistant").markdown("### 🎯 Recommended Products")

            for item in h["db_res"]:
                meta = item.get("metadata", {})
                content = item.get("page_content", "")

                with st.container():
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        img_url = meta.get("image_url")
                        if img_url:
                            st.image(img_url, width=140)

                    with col2:
                        st.markdown(f"**{content}**")
                        st.write(f"Brand: {meta.get('brand')}")
                        st.write(f"Price: ₹{meta.get('price')}")
                        st.write(f"Discounted: ₹{meta.get('discountedPrice')}")

        # PREMIUM SUMMARY BOX
        if h.get("summary"):
            st.chat_message("assistant").markdown(
            f"""
            <div style="
                background: #FFF7D1;
                padding: 14px;
                border-left: 6px solid #FF4C00;
                border-radius: 10px;
                font-size: 16px;
                color: black;
            ">
            <strong>📝 Final Summary:</strong><br>{h['summary']}
            </div>
            """,
            unsafe_allow_html=True
            )

        


# =====================================================
# INPUT BOX (Always Bottom)
# =====================================================
st.markdown("---")
st.subheader("💬 Ask Something")

user_query = st.text_input("Type your query:")

if st.button("Send Query"):
    if not st.session_state.image_uploaded:
        st.error("Please upload an image before chatting.")
    else:
        with st.spinner("Thinking..."):
            result = response(thread_id=thread_id, query=user_query)

        st.session_state.thread_data[thread_id].append(result)
        save_data(st.session_state.thread_data)

        st.success("Response saved!")
        st.rerun()
