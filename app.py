import streamlit as st
import os
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from google.generativeai import types


# ========== Streamlit UI ==========
st.set_page_config(page_title="Horror Image Generator", layout="wide")
st.title("🎃 AI Horror Image Generator")
st.write("Gemini 2.0 Image Model ka use karke cinematic horror illustrations banao.")

# API Key input
api_key = st.text_input("Enter your Google API Key", type="password")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)

# Prompt input options
st.subheader("Prompts Input")
uploaded_file = st.file_uploader("Upload a .txt file with prompts (one per line)", type=["txt"])
manual_prompts = st.text_area("Or enter prompts manually (one per line)")

# Output folder
SAVE_DIR = "generated_horror_images"
os.makedirs(SAVE_DIR, exist_ok=True)

if st.button("Generate Images"):
    if not api_key:
        st.error("Please enter your Google API Key.")
    else:
        # Prepare prompt list
        prompts = []
        if uploaded_file is not None:
            prompts = [line.strip() for line in uploaded_file.read().decode("utf-8").splitlines() if line.strip()]
        elif manual_prompts.strip():
            prompts = [line.strip() for line in manual_prompts.splitlines() if line.strip()]
        else:
            st.error("Please upload a prompt file or enter prompts manually.")
        
        if prompts:
            client = genai.Client()
            for idx, prompt in enumerate(prompts, start=1):
                st.write(f"🖌️ Generating image {idx}/{len(prompts)}...")
                contents = f"Cinematic horror illustration, dark and atmospheric, {prompt}"

                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-preview-image-generation",
                        contents=contents,
                        config=types.GenerateContentConfig(
                            response_modalities=['TEXT', 'IMAGE']
                        )
                    )

                    for part in response.candidates[0].content.parts:
                        if part.inline_data is not None:
                            image = Image.open(BytesIO(part.inline_data.data))
                            save_path = os.path.join(SAVE_DIR, f"horror_image_{idx}.png")
                            image.save(save_path)
                            st.image(image, caption=f"Image {idx}: {prompt}", use_container_width=True)
                            with open(save_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download Image",
                                    data=f,
                                    file_name=f"horror_image_{idx}.png",
                                    mime="image/png"
                                )
                        elif part.text:
                            st.info(f"Note from model: {part.text}")
                except Exception as e:
                    st.error(f"❌ Error generating image {idx}: {e}")
        else:
            st.error("No prompts found.")

