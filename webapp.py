import streamlit as st
from PyPDF2 import PdfMerger
from io import BytesIO
from streamlit_sortables import sort_items
from PIL import Image
from PIL import ImageOps
import img2pdf

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

            st.subheader("Drag to reorder PDFs")
            if filenames:
                sort_key = f"tab3_sort_{len(filenames)}_{hash(tuple(filenames))}"
                sorted_names_t3 = sort_items(filenames, custom_style=custom_style, direction="horizontal", key=sort_key)

            ordered = []

            for name in sorted_names_t3:
                for file in processed_files:
                    if file[0] == name:
                        ordered.append(file)
                        break
                        
            if st.button("Merge1"):
                merger = PdfMerger()
                for f in ordered:
                    merger.append(f[1])
                out = BytesIO()
                merger.write(out)
                merger.close()
                out.seek(0)
                st.success("Merged!")
                st.download_button("Download Merged PDF", out, "merged.pdf", "application/pdf")

            

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

    3. how to deal with different paper sizes being uploaded?

    4. [resolved] drag to reorder is hiden until files are uploaded.

    5. Fix issue where it does everything as A4. Maybe a selection of page size?
       Or it recognizes other page sizes? idk.
    """