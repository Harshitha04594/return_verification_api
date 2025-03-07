import streamlit as st
import requests

# Replace this with your Render API URL
API_URL = "https://return-verification-api-1.onrender.com"

st.title("Return Verification App")

# --- Upload Product Images ---
st.header("Upload Product Images")
product_id = st.text_input("Enter Product ID", value="prod1")
uploaded_files = st.file_uploader("Choose Product Image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("Upload Images"):
    if not product_id:
        st.error("Please enter a product ID.")
    elif not uploaded_files:
        st.error("Please select at least one image file.")
    else:
        files = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
        response = requests.post(f"{API_URL}/upload_product_images", params={"product_id": product_id}, files=files)
        if response.status_code == 200:
            st.success("Images uploaded successfully!")
            st.json(response.json())
        else:
            st.error(f"Error: {response.status_code}")
            st.text(response.text)

# --- Verify a Return Image ---
st.header("Verify Return")
return_file = st.file_uploader("Choose Return Image", type=["jpg", "jpeg", "png"], key="return")
if st.button("Verify Return"):
    if not product_id:
        st.error("Please enter a product ID.")
    elif not return_file:
        st.error("Please select a return image.")
    else:
        files = {"file": (return_file.name, return_file.getvalue(), return_file.type)}
        response = requests.post(f"{API_URL}/verify_return", params={"product_id": product_id}, files=files)
        if response.status_code == 200:
            st.success("Return verified!")
            st.json(response.json())
        else:
            st.error(f"Error: {response.status_code}")
            st.text(response.text)

# --- View All Products ---
st.header("View All Products")
if st.button("Get Products"):
    response = requests.get(f"{API_URL}/products/")
    if response.status_code == 200:
        st.json(response.json())
    else:
        st.error(f"Error: {response.status_code}")
        st.text(response.text)
