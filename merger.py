from PyPDF2 import PdfMerger
from tkinter import Tk, filedialog, messagebox

def select_pdf(title):
    root = Tk()
    root.withdraw()
    file = filedialog.askopenfilename(
        title=title,
        filetypes=[("PDF files", "*.pdf")]
    )
    root.destroy()
    return file

def main():
    pdf_files = []

    # Ask how many files to merge
    root = Tk()
    root.withdraw()
    num = messagebox.askquestion("Merge 2 PDFs", "Do you want to merge exactly 2 PDFs?")
    root.destroy()

    # Select files one at a time
    pdf_files.append(select_pdf("Select the first PDF"))
    pdf_files.append(select_pdf("Select the second PDF"))

    if None in pdf_files or "" in pdf_files:
        print("Cancelled.")
        return

    # Ask where to save the merged PDF
    root = Tk()
    root.withdraw()
    output_file = filedialog.asksaveasfilename(
        title="Save merged PDF as...",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    root.destroy()

    if output_file:
        merger = PdfMerger()
        for f in pdf_files:
            merger.append(f)
        merger.write(output_file)
        merger.close()
        print(f"Merged PDF saved to: {output_file}")
    else:
        print("Cancelled.")

if __name__ == "__main__":
    main()
