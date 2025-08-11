import streamlit as st
import os
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from google.generativeai import types

st.title("🎃 AI Horror Image Generator")

api_key = st.text_input("Enter your Google API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)

prompts_text = st.text_area("Enter prompts (one per line)")

SAVE_DIR = "generated_horror_images"
os.makedirs(SAVE_DIR, exist_ok=True)

if st.button("Generate Images"):
    if not api_key:
        st.error("Please enter your API key.")
    elif not prompts_text.strip():
        st.error("Please enter some prompts.")
    else:
        prompts = [p.strip() for p in prompts_text.splitlines() if p.strip()]
        for idx, prompt in enumerate(prompts, 1):
            st.write(f"🖌️ Generating image {idx}/{len(prompts)}...")
            contents = f"Cinematic horror illustration, dark and atmospheric, {prompt}"

            try:
                response = genai.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=contents,
                    generation_config=types.GenerationConfig(
                        response_modalities=["IMAGE", "TEXT"]
                    )
                )

                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        image = Image.open(BytesIO(part.inline_data.data))
                        save_path = os.path.join(SAVE_DIR, f"horror_image_{idx}.png")
                        image.save(save_path)
                        st.image(image, caption=f"Image {idx}: {prompt}", use_container_width=True)
                    elif part.text:
                        st.info(f"Note: {part.text}")

            except Exception as e:
                st.error(f"❌ Error generating image {idx}: {e}")
