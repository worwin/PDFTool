import streamlit as st
from PyPDF2 import PdfMerger
from io import BytesIO
from streamlit_sortables import sort_items
from PIL import Image

st.set_page_config(page_title="PDF Merger", layout="centered")

tab1, tab2, tab3, tab4 = st.tabs(["Merge PDFs", "Image to PDF", "Main", "Dev/Bugs"])

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

# Tab 1: Merge PDFs
with tab1: 
    #st.header("PDF Merger — Drag to Reorder Uploads")

    uploaded_files = st.file_uploader(
        "Upload up to 10 PDFs", type="pdf", accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("Maximum is 10 files.")
        else:
            # Append list of filenames 
            filenames = [f.name for f in uploaded_files]

            st.subheader("Drag to reorder PDFs")
            sorted_names = sort_items(filenames, custom_style=custom_style, direction="horizontal")
            
            # Ordere the files
            ordered = []

            for name in sorted_names:
                for file in uploaded_files:
                    if file.name == name:
                        ordered.append(file)
                        break

            if st.button("Merge"):
                merger = PdfMerger()
                for f in ordered:
                    merger.append(f)
                out = BytesIO()
                merger.write(out)
                merger.close()
                out.seek(0)
                st.success("Merged!")
                st.download_button("Download Merged PDF", out, "merged.pdf", "application/pdf")

# Tab 2: Image to PDF
with tab2:
    #st.header("Convert Images to PDF")

    images = st.file_uploader(
        "Upload PNG or JPEG files", type=["png", "jpg", "jpeg"], accept_multiple_files=True
    )

    if images:
        image_objs = []
        for img in images:
            image = Image.open(img)
            if image.mode != "RGB":
                image = image.convert("RGB")
            image_objs.append(image)

        if st.button("Convert to PDF"):
            output = BytesIO()
            image_objs[0].save(output, format="PDF", save_all=True, append_images=image_objs[1:])
            output.seek(0)
            st.success("Images converted to PDF!")
            st.download_button("Download PDF", output, "converted.pdf", "application/pdf")

# Tab 3: Working on a single page to handle this
with tab3: 

    files = st.file_uploader(
        "Upload Files", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True
    )

    # Get the file uploaded order (store names)
    uploaded_files = []
    for file in files:
        uploaded_files.append(file.name)

    # Look for none PDFs and convert using original file names provided
    for file in files:
        if file.type != 'application/pdf':
            col1, col2 = st.columns([4,1])
            with col1: 
                st.write(file.name)
            with col2:
                if st.button(f"Convert {file.name}", key=f"convert_{file.name}"):
                    image = Image.open(file).convert("RGB")
                    pdf_bytes = BytesIO()
                    image.save(pdf_bytes, format="PDF")
                    pdf_bytes.seek(0)
                    st.download_button("Download PDF", pdf_bytes, file.name + ".pdf", mime="application/pdf")    
            

    # If a single file is provided
        # give download option for file

    # If multiple files are provided
        # Maintain original upload order and provide a sorting mechanism

        # Allow for merging into a single pdf (if a single pdf is provided)

    #for file in files:
    #    print(file)

        # file.type == 'image/png' or 'image/jpg' or 'image/jpeg'
        # file.type == 'application/pdf'




with tab4:
    ##=== Bugs to fix ===##
    """
    Bug Issues

    1. uploading multiple of the same file results in a duplicate name issue,
    they will need different key values, not sure how to handle this issue. 

    2. 
    """