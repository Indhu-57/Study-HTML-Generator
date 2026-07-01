
import streamlit as st
from gemini import generate_learning_material

st.title("Gemini Test")

text = st.text_area(
    "Paste extracted text here",
    height=300
)

if st.button("Generate"):

    if text.strip() == "":
        st.warning("Please paste some text.")
    else:

        with st.spinner("Generating..."):

            result = generate_learning_material(text)

        st.subheader("Gemini Response")

        st.text_area(
            "",
            result,
            height=500
        )
