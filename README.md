# Dataset Reference Extractor

This project implements a **regex-based pipeline** for extracting dataset references from scientific articles in **PDF** and **XML** format.  

It was developed on the [Kaggle: Make Data Count – Finding Data References](https://www.kaggle.com/competitions/make-data-count-finding-data-references) dataset. The focus was on building a **robust, generalizable extraction class** that can process raw files and return structured dataset mentions for downstream analysis.  

---

## Project Highlights

- Designed and implemented a **Python class** (`DatasetReferenceExtractor`) to handle the full workflow.  
- Built a **text cleaning pipeline**: fixing encodings, normalizing Unicode, removing control characters, handling spacing issues.  
- Developed **custom regex patterns** to capture dataset identifiers such as DOIs and URLs.  
- Implemented **context windowing** to capture words around each match, making the reference more interpretable.  
- Added **deduplication logic** to merge duplicate mentions across PDF and XML sources.  
- Produced clean, tabular output (`pandas.DataFrame`) for further analysis or modeling.  

---

## Data Source

The project uses data from the Kaggle competition:  

👉 [Make Data Count – Finding Data References](https://www.kaggle.com/competitions/make-data-count-finding-data-references/data)  

The dataset contains paired **PDF** and **XML** versions of scientific articles.  
Due to licensing, the data is **not included in this repository** and must be downloaded directly from Kaggle.  

---

## Technical Stack

- **Python**  
- **pandas** – tabular processing  
- **ftfy** – text encoding fixes  
- **lxml** – XML parsing  
- **PyMuPDF (fitz)** – PDF text extraction  
- **re / regex** – dataset identifier detection  

---

## Workflow Overview

1. **Extract raw text** from PDF and XML files.  
2. **Clean and normalize** the text.  
3. **Search for dataset identifiers** using regex patterns.  
4. **Capture context windows** around each match.  
5. **Deduplicate mentions** across multiple sources.  
6. **Return results** in a DataFrame.  

This provides a structured view of where and how datasets are referenced in articles.  

---

## Known Notes

- Running on PDFs may produce harmless **PyMuPDF warnings** about annotations:  

MuPDF error: unsupported error: cannot create appearance stream for annotations


These do not affect text extraction and can be ignored.  

The current pipeline focuses purely on **regex-based extraction**.  

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.  




