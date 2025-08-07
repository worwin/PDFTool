import streamlit as st
from PyPDF2 import PdfMerger
from io import BytesIO
from streamlit_sortables import sort_items
from PIL import Image
from PIL import ImageOps
import img2pdf

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
            sort_key = f"tab1_sort_{len(filenames)}_{hash(tuple(filenames))}"
            sorted_names_t1 = sort_items(filenames, custom_style=custom_style, direction="horizontal", key=sort_key)

            
            # Ordere the files
            ordered = []

            for name in sorted_names_t1:
                for file in uploaded_files:
                    if file.name == name:
                        ordered.append(file)
                        break

            print(ordered)

            if st.button("Merge0"):
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

    uploaded_files = st.file_uploader(
        "Upload Files", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("Maximum is 10 files.")
        else:

            # files that may need to be converted into pdfs before doing merge operations
            processed_files = []
            A4_WIDTH = 2480
            A4_HEIGHT = 3508

            # Look for none PDFs and convert using original file names provided
            for file in uploaded_files:
                if file.type != 'application/pdf':
                    #print(f"Converted {file.name}")
                    image = Image.open(file).convert("RGB")
                    img_bytes = BytesIO()
                    image.save(img_bytes, format="JPEG", quality=95)  # high quality
                    img_bytes.seek(0)

                    pdf_bytes = BytesIO()
                    pdf_bytes.write(
                        img2pdf.convert(
                            img_bytes,
                            dpi=300,  # adjust as needed
                            layout_fun=img2pdf.get_layout_fun((img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)))  # A4
                        )
                    )
                    pdf_bytes.seek(0)

                    
                    processed_files.append((file.name.split(".")[0] + ".pdf", pdf_bytes))
                else:
                    #print(f"Didn't need to convert {file.name}")
                    pdf_bytes = BytesIO(file.read())
                    processed_files.append((file.name, pdf_bytes))
            
            #print(processed_files)

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