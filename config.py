LOG_FILE_DIR = 'C:/D_Main_Nimra/Example2/log_file_path'
pdfpath = 'processed level 1'
extracted_case_text_dir = 'C:\D_Main_Nimra\Example2\processed level 2'
batchcount_print = 10


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
        "smrp": "Suo Motu Review Petition"
    }


accept_keywords = ['company', 'limited', 'corporation', 'pvt', 'enterprise', 'inc','co','ltd',]
reject_keywords2 = ['constp', 'institute']