import streamlit as st
from PyPDF2 import PdfMerger
from io import BytesIO
from streamlit_sortables import sort_items
from PIL import Image
import img2pdf
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components
import base64
from datetime import datetime

DEBUG = False


def check_session():

    if "user_agent" not in st.session_state:
        st.session_state.user_agent = None
    
    if "mobile" not in st.session_state:
        st.session_state.mobile = None

    # checks for user_agent data
    if st.session_state.user_agent == None:
        if DEBUG: print("Getting User Agent Data")
        get_user_agent()

    # check for mobile (Depednet on user_agent)
    if st.session_state.mobile == None and st.session_state.user_agent != None:
        #print("Getting Mobile Data")
        get_mobile()

    if DEBUG: print(f"Check Session -> user_agent: {st.session_state.user_agent}")
    if DEBUG: print(f"Check Session -> mobile: {st.session_state.mobile}")

def get_mobile():

    if st.session_state.user_agent:
        if "Mobile" in st.session_state.user_agent or "Android" in st.session_state.user_agent or "iPhone" in st.session_state.user_agent:
            st.session_state.mobile = True
        else:
            st.session_state.mobile = False

def get_user_agent():
    data = st_javascript("navigator.userAgent")
    if data and data != 0:
        st.session_state.user_agent = data
        st.rerun()

def merge(sorted_names, file_name):
    if DEBUG: print("Merge was called")
    ordered = []
    for name in sorted_names:
        for file in processed_files:
            if file[0] == name:
                ordered.append(file)
                break

    merger = PdfMerger()
    for file in ordered:
        merger.append(file[1])

    out = BytesIO()
    merger.write(out)
    merger.close()
    out.seek(0)
    return out

st.set_page_config(page_title="PDF Merger", layout="centered")

tab1, tab2 = st.tabs(["Main", "Dev"])

custom_style = """
.sortable-component {
    border: 1px solid #262730;
    border-radius: 10px;
    padding: 5px;
}
.sortable-container {
    background-color: #0e1117;
    counter-reset: item;
}
.sortable-container-header {
    background-color: #0e1117;
    padding-left: 1rem;
}
.sortable-container-body {
    background-color: #0e1117;
}
.sortable-item, .sortable-item:hover {
    background-color: #262730;
    font-color: #FFFFFF;
    font-weight: bold;
}
"""

# Tab 1: Working on a single page to handle this
with tab1: 
    
    check_session()

    uploaded_files = st.file_uploader(
        "Upload Files", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("Maximum is 10 files.")
        else:
            page_size = st.selectbox("Page Size", ["A4", "Letter", "Legal", "A5", "A3", "B5", "Tabloid"])

            if page_size == "A4": # Standard International
                layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)))
            elif page_size == "Letter": # Standard US Size
                layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))
            elif page_size == "Legal": # US Legal Documents
                layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(216), img2pdf.mm_to_pt(356)))
            elif page_size == "A5": # Small Booklets, Notepads
                layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(148), img2pdf.mm_to_pt(210)))
            elif page_size == "A3": # Large Documents, Charts
                layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(297), img2pdf.mm_to_pt(420)))
            elif page_size == "B5": # Books, Journals
                layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(176), img2pdf.mm_to_pt(250)))
            elif page_size == "Tabloid": # Newsapers, Posters
                layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(279), img2pdf.mm_to_pt(432)))

            # files that may need to be converted into pdfs before doing merge operations
            processed_files = []

            # Look for none PDFs and convert using original file names provided
            for file in uploaded_files:
                if file.type != 'application/pdf':
                    image = Image.open(file).convert("RGB")
                    img_bytes = BytesIO()
                    image.save(img_bytes, format="JPEG", quality=95)  # high quality
                    img_bytes.seek(0)

                    pdf_bytes = BytesIO()
                    pdf_bytes.write(
                        img2pdf.convert(
                            img_bytes,
                            dpi=300,  # adjust as needed
                            layout_fun=layout  
                        )
                    )
                    pdf_bytes.seek(0)

                    
                    processed_files.append((file.name.split(".")[0] + ".pdf", pdf_bytes))
                else:
                    pdf_bytes = BytesIO(file.read())
                    processed_files.append((file.name, pdf_bytes))
            
            filenames = []
            for record in processed_files:
                filenames.append(record[0])

            file_name = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            if len(processed_files) > 1:
                st.subheader("Drag to Reorder PDFs")
                if filenames:
                    sort_key = f"tab_sort_{len(filenames)}_{hash(tuple(filenames))}"
                    sorted_names = sort_items(filenames, custom_style=custom_style, direction="horizontal", key=sort_key)
            else:
                sorted_names = filenames

            label = "Download PDF"

            st.download_button(
                label=label,
                data=merge(sorted_names, processed_files),
                file_name=file_name,
                mime="application/pdf"
            )

with tab2:
    '''
    Developer Information
    '''