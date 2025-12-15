import streamlit as st
import pandas as pd
import os
from PIL import Image
from datetime import datetime

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Inventory Management App", layout="wide")

DATA_FILE = "inventory.csv"
IMAGE_FOLDER = "images"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# =============================
# LOAD / SAVE DATA
# =============================
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Item ID",
            "Item Name",
            "Category",
            "Quantity",
            "Price",
            "Image",
            "Added On"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# =============================
# UI
# =============================
st.title("📦 Inventory Management App")

tabs = st.tabs(["➕ Add Item", "📋 Inventory List", "🗑 Delete Item"])

# =============================
# ADD ITEM
# =============================
with tabs[0]:
    st.subheader("Add New Item")

    col1, col2 = st.columns(2)

    with col1:
        item_name = st.text_input("Item Name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        price = st.number_input("Price", min_value=0.0, step=0.01)

    with col2:
        image_file = st.file_uploader(
            "Upload Item Image (High Quality)",
            type=["jpg", "jpeg", "png"]
        )

    if st.button("Add Item"):
        if item_name.strip() == "":
            st.error("Item name is required")
        else:
            item_id = f"ITEM-{len(df)+1}"
            image_name = ""

            if image_file:
                image_name = f"{item_id}.png"

                # 🔥 BLUR FIX STARTS HERE 🔥
                image = Image.open(image_file)
                image = image.convert("RGB")  # remove compression artifacts

                image.save(
                    os.path.join(IMAGE_FOLDER, image_name),
                    format="PNG",
                    optimize=False,   # NO compression
                    compress_level=0  # MAX quality
                )
                # 🔥 BLUR FIX ENDS HERE 🔥

            new_row = {
                "Item ID": item_id,
                "Item Name": item_name,
                "Category": category,
                "Quantity": quantity,
                "Price": price,
                "Image": image_name,
                "Added On": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)

            st.success("Item added successfully ✅")

# =============================
# INVENTORY LIST
# =============================
with tabs[1]:
    st.subheader("Inventory Items")

    if df.empty:
        st.info("No items added yet.")
    else:
        for _, row in df.iterrows():
            col1, col2 = st.columns([1.2, 3])

            with col1:
                if row["Image"] and os.path.exists(f"{IMAGE_FOLDER}/{row['Image']}"):
                    st.image(
                        f"{IMAGE_FOLDER}/{row['Image']}",
                        caption=row["Item Name"],
                        use_container_width=False  # IMPORTANT: prevents blur
                    )
                else:
                    st.text("No Image")

            with col2:
                st.markdown(f"""
                **Item ID:** {row['Item ID']}  
                **Name:** {row['Item Name']}  
                **Category:** {row['Category']}  
                **Quantity:** {row['Quantity']}  
                **Price:** ₹{row['Price']}  
                **Added On:** {row['Added On']}
                """)
                st.divider()

# =============================
# DELETE ITEM
# =============================
with tabs[2]:
    st.subheader("Delete Item")

    if df.empty:
        st.info("No items to delete.")
    else:
        item_to_delete = st.selectbox(
            "Select Item ID",
            df["Item ID"].tolist()
        )

        if st.button("Delete"):
            row = df[df["Item ID"] == item_to_delete].iloc[0]

            if row["Image"]:
                img_path = f"{IMAGE_FOLDER}/{row['Image']}"
                if os.path.exists(img_path):
                    os.remove(img_path)

            df = df[df["Item ID"] != item_to_delete]
            save_data(df)

            st.success("Item deleted successfully 🗑")
