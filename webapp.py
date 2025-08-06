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

def check_session():

    if "user_agent" not in st.session_state:
        st.session_state.user_agent = None
    
    if "mobile" not in st.session_state:
        st.session_state.mobile = None

    # checks for user_agent data
    if st.session_state.user_agent == None:
        print("Getting User Agent Data")
        get_user_agent()

    # check for mobile (Depednet on user_agent)
    if st.session_state.mobile == None and st.session_state.user_agent != None:
        print("Getting Mobile Data")
        get_mobile()

    print(f"Check Session -> user_agent: {st.session_state.user_agent}")
    print(f"Check Session -> mobile: {st.session_state.mobile}")

def get_user_agent():
    data = st_javascript("navigator.userAgent")
    if data and data != 0:
        st.session_state.user_agent = data
        st.rerun()
    

def get_mobile():

    if st.session_state.user_agent:
        if "Mobile" in st.session_state.user_agent or "Android" in st.session_state.user_agent or "iPhone" in st.session_state.user_agent:
            st.session_state.mobile = True
        else:
            st.session_state.mobile = False

def js_download_button(buffer, filename):
    b64 = base64.b64encode(buffer.getvalue()).decode()
    payload = f"data:application/pdf;base64,{b64}"
    custom_html = f"""
    <html>
        <body>
            <a download="{filename}" id="download-link" href="{payload}" style="display:none;"></a>
            <script>
                document.getElementById("download-link").click();
            </script>
        </body>
    </html>
    """
    components.html(custom_html, height=0, width=0)

def merge(sorted_names, file_name):
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

tab1, tab2, = st.tabs(["Main", "Dev/Bugs"])

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
            page_size = st.selectbox("Page Size", ["A4", "Letter"])

            if page_size == "A4":
                layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)))
            elif page_size == "Letter":
                layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))

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

            if st.session_state.mobile:
                file_name = st.text_input("Save as", value="merged")
            else:
                file_name = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            if not file_name.lower().endswith(".pdf"):
                file_name += ".pdf"

            if len(processed_files) > 1:
                st.subheader("Drag to Reorder PDFs")
                if filenames:
                    sort_key = f"tab_sort_{len(filenames)}_{hash(tuple(filenames))}"
                    sorted_names = sort_items(filenames, custom_style=custom_style, direction="horizontal", key=sort_key)
            else:
                sorted_names = filenames

            if st.button("Download PDF"):
                merged_pdf = merge(sorted_names, processed_files)
                js_download_button(merged_pdf, file_name)

    # If a single file is provided
        # give download option for file

    # If multiple files are provided
        # Maintain original upload order and provide a sorting mechanism

        # Allow for merging into a single pdf (if a single pdf is provided)

    #for file in files:
    #    print(file)

        # file.type == 'image/png' or 'image/jpg' or 'image/jpeg'
        # file.type == 'application/pdf'


with tab2:
    ##=== Bugs to fix ===##
    """
    Bug Issues

    1. [resolved] uploading multiple of the same file results in a duplicate name issue,
    they will need different key values, not sure how to handle this issue. 

    2. [resolved] image quality of upload is not great

    3. [resolved] how to deal with different paper sizes being uploaded?

    4. [resolved] drag to reorder is hiden until files are uploaded.

    5. [resolged] Fix issue where it does everything as A4. Maybe a selection of page size?
       Or it recognizes other page sizes? idk.
    
    6. [resolved] If only a single file is upload, have button say Download. Right now, if a single file
       needs to be uploaded and converted it still shows merge and reordering. Maybe
       figure out how to activate this once two files have been done.

    7. Look at how to rotate images if needed, but this also implies that we need to 
       be able to see them. This is where streamlit might have limitations.
    
    8. Some issue where a rotated image will still show in it's original format.
       Not sure thats a big on my end but kinda interesting it is happening.
    
    9. [resolved] Have Merge Button simply just download. No Merge then seperate download.
       Keep this streamlined. 

    10. [resolved] From (9) check and see when resolving (6) if this causes issues. 

    11. Detect what device they are connecting from. If phone, give the option to 
        name the file before downloading. Otherwise, return as merged.pdf.

    12. Over modularization of merge is causing issues with everything. A bit of a paradox.
        I want the ability to select the name it will be saved as once they click the download 
        button. However, because this is in merge, it doesn't work. it has to be moved outside
        of merge (chatgpt says at least) 

    """