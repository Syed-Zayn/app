import streamlit as st
import os
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="🎃 AI Horror Image Generator", layout="wide")
st.title("🎃 AI Horror Image Generator")
st.write("Gemini 2.0 Image Model se cinematic horror images generate karo.")

# API key input
api_key = st.text_input("Enter your Google API Key", type="password")

SAVE_DIR = "horror_imagesss"
os.makedirs(SAVE_DIR, exist_ok=True)

# Upload or manual prompt input
uploaded_file = st.file_uploader("Upload a .txt file with prompts (one per line)", type=["txt"])
manual_prompts = st.text_area("Or enter prompts manually (one per line)")

if st.button("Generate Images"):
    if not api_key:
        st.error("Google API key dalna zaroori hai.")
    else:
        # Configure API key and create client
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)
        client = genai.Client()

        # Prepare prompts list
        prompts = []
        if uploaded_file is not None:
            try:
                prompts = [line.strip() for line in uploaded_file.read().decode("utf-8").splitlines() if line.strip()]
            except Exception as e:
                st.error(f"File read error: {e}")
        elif manual_prompts.strip():
            prompts = [line.strip() for line in manual_prompts.splitlines() if line.strip()]
        else:
            st.error("Please upload a prompt file or enter prompts manually.")
            st.stop()

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Generate images for prompts
        for idx, prompt in enumerate(prompts, start=1):
            status_text.text(f"Generating image {idx}/{len(prompts)} ...")
            contents = f"Cinematic horror illustration, dark and atmospheric, {prompt}"
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )

                # Extract and show images and text notes
                for part in response.candidates[0].content.parts:
                    if part.text is not None:
                        st.info(f"Model note: {part.text}")
                    elif part.inline_data is not None:
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
                progress_bar.progress(idx / len(prompts))
            except Exception as e:
                st.error(f"Error generating image {idx}: {e}")
                continue

        status_text.text("🎉 All horror images generated successfully!")
        progress_bar.empty()
