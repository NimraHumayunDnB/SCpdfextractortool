import re

LOG_FILE_DIR = "C:/D_Main_Nimra/Example2/log_file_path"
pdfpath = "processed level 1"
extracted_case_text_dir = "C:\D_Main_Nimra\Example2\processed level 2"
batchcount_print = 10


pattern_mr_justice_config = re.compile(
    r"^(MR\.|MRS\.|MS\.) JUSTICE .+$", re.IGNORECASE | re.MULTILINE
)
pattern_justice_all_caps_config = re.compile(r"\bJUSTICE(?: [A-Z\.\-']+)+")
pattern_justice_title_case_config = re.compile(r"\bJustice(?: [A-Z][a-zA-Z\.\-']*)+")
pattern_versus_config = re.compile(r"(?ix)\b(?:vs\.?|versus)\b")

pattern_date_ddmmyyyy = re.compile(
    r"(?i)Date of hearing\s*[:;]?\s*(\d{2}\.\d{2}\.\d{4})"
)
pattern_date_textmonth = re.compile(
    r"(?i)Date of hearing\s*[:;]?\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})"
)
# Handling date formats like "12 and 13 January 2024"
pattern_hearing_date_3 = r"(?i)Date(?:s)? of hearing\s*[:;]?\s*((?:\d{1,2}(?:,|\s+and\s+)?\s*)+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})"


case_number_patterns = [
    r"Crl\.P\.L\.A\.[\w\-]+\/\d{4}",  # Pattern 1
    r"C\.P\.L\.A[s]?\.?\s*(?:[\w\-]+(?:,?\s*(?:and\s*)?[\w\-]+)*)(?:\s*\/\d{4}|\s*of\s*\d{4})",  # Pattern 2
    r"(?:Nos?\.?\s*(?:[\w\-]+(?:,\s*[\w\-]+)*(?:\s*(?:and|&|to|–)\s*[\w\-]+)?|[\w\-]+(?:\s*(?:and|&|to|–)\s*[\w\-]+)?))\s*(?:of|/)\s*\d{2,4}",  # Pattern 3
]


Casetitle_pattern = r"\((.*Jurisdiction\s*)\)"


respondent_pattern_config = r"""(?ix)(?:vs\.?|versus)\s*[\r\n]*  # versus variants
                            (?P<respondent>(?:["“]?)[A-Z][^\n]*?    # respondent capture group
                            (?:[\r\n]+[^\n]*?)*?)\s*                 # multiline respondent text
                            (?:\.{2,}|…+)?\s*Respondent(?:s)?(?:\(\w+\))?"""  # suffixes


Petitioner_pattern_config = re.compile(
    r"[\.\)\]]\s*\n"  # Match ., ), or ] followed by newline
    r"(?=[A-Z])"  # Next line starts with a capital letter
    r"(.*?)"  # Non-greedy match for petitioner name
    r"(?=\s*(?:\.{2,}|(?:\.\s*){2,}|…+)?\s*"  # Optional ellipsis or spaced dots
    r"\b(?:Petitioner(?:\(s\))?|Petitioners|Applicants?\(?s?\)?|Appellants?)\b)",  # Petitioner-like keywords
    re.IGNORECASE | re.DOTALL,
)


case_type_map = {
    "cma": "Civil Miscellaneous Application",
    "ca": "Civil Appeal",
    "cmappeal": "Civil Miscellaneous Appeal",
    "cp": "Civil Petition",
    "crp": "Civil Review Petition",
    "cuo": "Case Under Objection",
    "constp": "Constitution Petition",
    "crla": "Criminal Appeal",
    "crlma": "Criminal Miscellaneous Application",
    "crlmappeal": "Criminal Miscellaneous Appeal",
    "crlop": "Criminal Original Petition",
    "crlp": "Criminal Petition",
    "crlrp": "Criminal Petition",
    "ica": "Intra Court Appeals",
    "smc": "Suo Moto Case",
    "cpla": "Civil Petition for Leave to Appeal",
    "csha": "Constitutional Shariat Appeal",
    "cshp": "Constitutional Shariat Petition",
    "cshrp": "Constitutional Shariat Review Petition",
    "crlpla": "Criminal Petition for Leave to Appeal",
    "crlsmrp": "Criminal Shariat Miscellaneous Review Petition",
    "crlsmshrp": "Criminal Shariat Miscellaneous Shariat Review Petition",
    "crlsha": "Criminal Shariat Appeal",
    "crlshp": "Criminal Shariat Petition",
    "crlshrp": "Criminal Shariat Review Petition",
    "dsa": "Direct Shariat Appeal",
    "hrc": "Human Rights Case",
    "hrma": "Human Rights Miscellaneous Application",
    "jp": "Jail Petition",
    "jshp": "Jail Shariat Petition",
    "reference": "Judicial Reference (e.g., Presidential Reference)",
    "smrp": "Suo Motu Review Petition",
}


accept_keywords = [
    "company",
    "limited",
    "corporation",
    "pvt",
    "enterprise",
    "inc",
    "co",
    "ltd",
]
reject_keywords2 = ["constp", "institute"]
