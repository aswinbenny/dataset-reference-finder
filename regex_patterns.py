import re

# Dictionary of regex patterns for identifying common dataset/database references in text
patterns = {
    # DOI formats
    'doi_short': r'https?\s*:\s*/\s*/\s*(?:doi\.org|dx\.doi\.org)\s*/\s*10\.\d{4,9}/[A-Za-z0-9._\-()/]+\b',  # Standard DOI link (with optional spacing)
    'doi_long': r'\bhttps?://(?:doi\.org|dx\.doi\.org)/10\.\d{4,9}/[A-Za-z0-9._\-()/]+(?: [A-Za-z0-9._\-()/]+)\b',  # Longer DOI with potential trailing text
    'doi_xml': r'\bdoi:\s*10\.\d{4,9}/[A-Za-z0-9._\-()/]+\b',  # DOI prefixed with "doi:"

    # BioSample / BioProject identifiers
    'SAMN BioSample':  r'\bSAMN\d{8,}\b',         # NCBI BioSample IDs
    'PRJNA (BioProject)': r'\bPRJNA\d+\b',        # NCBI BioProject IDs

    # Virus / Sequence databases
    'EPI_ISL (GISAID)': r'\bEPI_ISL_\d+',         # GISAID EPI_ISL IDs
    'EPI Short (Legacy)': r'\bEPI\d{6,}\b',       # Short legacy GISAID IDs
    'SRX/SRR/SRP': r'\bSR[PXR]\d{6,}\b',          # NCBI Sequence Read Archive (Run/Project/Experiment)

    # Protein & enzyme databases
    'UniProt ID': r'\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b',   # UniProt protein accession IDs
    'EC Numbers': r'\b\d+\.\d+\.\d+\.\d+\b',          # Enzyme Commission numbers
    'ENSEMBL Gene ENSMMUT': r'\bENSMMUT\d{11,}\b',    # Ensembl gene ID (Macaca mulatta)
    'ENSEMBL Gene ENSBTAG': r'\bENSBTAG\d{11,}\b',    # Ensembl gene ID (Bos taurus)
    'ENSEMBL Gene ENSOARG': r'\bENSOARG\d{11,}\b',    # Ensembl gene ID (Ovis aries)

    # Chemical / drug / structure databases
    'CHEMBL': r'\bCHEMBL\d+\b',       # ChEMBL chemical compound IDs
    'IPR': r'\bIPR\d{6,}\b',          # InterPro protein families
    'PF': r'\bPF\d{5,}\b',            # Pfam protein families
    'KEGG K Numbers': r'\bK\d{5,}\b', # KEGG orthology IDs
    'PDB ID': r'\b[1-9](?:[a-z]{2}[a-z0-9]|[a-z][a-z0-9][a-z]|[a-z0-9][a-z]{2})\b',  # Protein Data Bank IDs
    'Short Alphanumeric ID (PDB-like)': r'\b[0-9](?:[A-Z]{2}[A-Z0-9]|[A-Z][A-Z0-9][A-Z]|[A-Z0-9][A-Z]{2})\b',  # Short structural IDs

    # Expression & proteomics
    'E-GEOD (GEO)': r'\bE-GEOD-\d{5,}\b',   # GEO microarray datasets
    'GSE': r'\bGSE\d{5,}\b',                # GEO study IDs
    'E-PROT (Expression Atlas)': r'\bE-PROT-\d{2,}\b',  # Expression Atlas IDs
    'PXD (ProteomeXchange)': r'\bPXD\d{6,}\b',          # ProteomeXchange dataset IDs

    # Imaging databases
    'EMPIAR': r'\bEMPIAR-\d{5,}\b',         # Electron Microscopy Public Image Archive
    'HPA ID': r'\bHPA\d{6,}\b',             # Human Protein Atlas

    # GenBank / RefSeq
    'CP GenBank/RefSeq': r'\bCP\d{6,}\b',   # GenBank complete genome IDs
    'NC_ RefSeq': r'\bNC_\d+\.\d+\b',       # RefSeq accession numbers
    'NM_ RefSeq': r'\bNM_\d+\b',            # RefSeq mRNA IDs

    # Cell lines
    'CVCL (Cellosaurus)': r'\bCVCL_\w{4,}\b',  # Cellosaurus cell line IDs

    # Other identifiers
    'rs ID': r'\brs\d{6,}\b',          # dbSNP reference SNP IDs
    'CAB ID': r'\bCAB\d{6,}\b',        # CAB sequence IDs
    'KX ID': r'\bKX\d{6,}\b',          # GenBank sequence IDs
    'BX ID': r'\bBX\d+\b',             # GenBank BAC clone IDs
    'STH ID': r'\bSTH\d+\b',           # Custom/unknown reference IDs
    'F ID': r'\bF(?=[A-Z0-9]{5,})(?=(?:.*\d){2,})(?=(?:.*[A-Z]){2,})[A-Z0-9]+\b',  # Patterned IDs starting with F
    'D ID': r'\bD\d{5,}\b',            # Dataset IDs starting with D
    'ERR ID (ENA Run)': r'\bERR\d+\b', # ENA sequence run IDs
    'MODEL ID': r'\bMODEL\d+\b'        # Structural model IDs
}
