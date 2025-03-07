import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from typing import List

app = FastAPI()

# Directories for image storage
PRODUCT_IMAGES_DIR = "product_images/"
RETURNED_IMAGES_DIR = "returned_images/"
os.makedirs(PRODUCT_IMAGES_DIR, exist_ok=True)
os.makedirs(RETURNED_IMAGES_DIR, exist_ok=True)

# Function to compute Structural Similarity Index (SSIM)
def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        return 0.0  # Error case
    img1 = cv2.resize(img1, (300, 300))
    img2 = cv2.resize(img2, (300, 300))
    score, _ = ssim(img1, img2, full=True)
    return score

# ✅ Upload multiple images for a product (Stored Locally)
@app.post("/upload_product_images")
async def upload_product_images(product_id: str, files: List[UploadFile] = File(...)):
    saved_files = []
    
    for idx, file in enumerate(files):
        file_path = os.path.join(PRODUCT_IMAGES_DIR, f"{product_id}_{idx}.jpg")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file_path)
    
    return {"message": "Product images uploaded successfully!", "files": saved_files}

# ✅ Verify return image by comparing with stored product images
@app.post("/verify_return")
async def verify_return(product_id: str, file: UploadFile = File(...)):
    returned_path = os.path.join(RETURNED_IMAGES_DIR, f"{product_id}_returned.jpg")
    
    with open(returned_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Find all stored images for this product
    product_images = [f for f in os.listdir(PRODUCT_IMAGES_DIR) if f.startswith(f"{product_id}_")]
    
    if not product_images:
        raise HTTPException(status_code=404, detail="No product images found!")

    best_similarity = 0.0
    for img in product_images:
        product_img_path = os.path.join(PRODUCT_IMAGES_DIR, img)
        similarity_score = compare_images(product_img_path, returned_path)
        if similarity_score > best_similarity:
            best_similarity = similarity_score

    status = "Approved" if best_similarity > 0.8 else "Rejected"

    return {"status": status, "best_similarity": best_similarity, "product_id": product_id}
