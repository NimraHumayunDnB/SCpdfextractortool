
from datetime import datetime
import os
import pdfplumber
import logging
import re
import pandas as pd
import pytesseract
import pdfplumber
from config import *
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\HumayunN\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

#extracting text from pdfs that are images
def extract_text_from_pdf_pytesseract(pdf_path):
    output_text = ""
    try:
        logging.info(f"Starting OCR for: {pdf_path}")
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                try:
                    image = page.to_image(resolution=300)
                    img_bytes = image.original.convert("RGB")
                    ocr_text = pytesseract.image_to_string(img_bytes)
                    output_text += f"--- OCR Page {i} ---\n{ocr_text}\n"
                except Exception as page_err:
                    logging.error(f"OCR failed on page {i} of {pdf_path}: {page_err}")
                    logging.exception(page_err)
        logging.info(f"OCR complete for: {pdf_path}")
    except Exception as e:
        logging.error(f"Error during OCR processing of {pdf_path}: {e}")
        logging.exception(e)

    return output_text


#extracting texts via pdfplumber
def extract_texts_from_pdfs(all_pdf_folder):
    output_dir = extracted_case_text_dir
    os.makedirs(output_dir, exist_ok=True)

    
    already_processed = {
        os.path.splitext(f)[0]
        for f in os.listdir(output_dir)
        if f.lower().endswith(".txt")
    }

    for filename in os.listdir(all_pdf_folder):
        if filename.lower().endswith(".pdf"):
            pdf_name = os.path.splitext(filename)[0]
            if pdf_name in already_processed:
                logging.info(f"Skipping already processed file: {filename}")
                continue 

            pdf_path = os.path.join(all_pdf_folder, filename)
            txt_filename = pdf_name + ".txt"
            txt_path = os.path.join(output_dir, txt_filename)

            logging.info(f"Starting text extraction for: {filename}")
            extracted_text = ""

            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for i, page in enumerate(pdf.pages, start=1):
                        try:
                            text = page.extract_text()
                            if text:
                                extracted_text += f"--- Page {i} ---\n{text}\n"
                        except Exception as page_err:
                            logging.error(f"Text extraction failed on page {i} of {filename}: {page_err}")
                            logging.exception(page_err)

                if not extracted_text.strip():
                    logging.info(f"No text found in {filename}, falling back to OCR.")
                    extracted_text = extract_text_from_pdf_pytesseract(pdf_path)

                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)

                logging.info(f"Successfully saved extracted text to: {txt_path}")

            except Exception as e:
                logging.error(f"Error processing {filename}: {e}")
                logging.exception(e)

    logging.info(f"All new PDFs processed. Text files saved in: {output_dir}")



#extracting casetypes
def extract_case_type_from_folder(folder_path):
    logging.info(f"Starting case type extraction from folder: {folder_path}")
    results = []
    successcount = 0
    batchcount = 0
    # Mapping of case types to full forms
    

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                logging.info(f"Extracting case type from filename: {filename}")
                parts = filename.split('_')

                if len(parts) < 2:
                    logging.warning(f"Filename format unexpected: {filename}")
                    results.append({
                        "filename": filename,
                        "case_type": None,
                        "full_form": "Unknown Case Type"
                    })
                    continue

                case_type1 = parts[1]
                # logging.info(f"Extracted case type part: {case_type1}")
                batchcount += 1
                successcount += 1

                # Normalize
                normalized = re.sub(r'[^a-zA-Z]', '', case_type1).lower()
                full_form = case_type_map.get(normalized, "Unknown Case Type")

                results.append({
                    "filename": filename,
                    "case_type": normalized,
                    "full_form": full_form
                })
                

                if batchcount == batchcount_print:
                    logging.info(f"Case type extracted for {successcount} no of files")
                    batchcount = 0
        logging.info(f"Completed case type extraction for folder: {folder_path}")
    except Exception as e:
        logging.error(f"Error processing folder {folder_path}: {e}")
        logging.exception(e)

    return results




#extracting judges
def extract_judges_from_folder(folder_path):
    logging.info(f"Starting judge extraction from folder: {folder_path}")
    results = []
    successcount = 0
    batchcount = 0
    # Regex patterns
    pattern_mr_justice = re.compile(r'^(MR\.|MRS\.|MS\.) JUSTICE .+$', re.IGNORECASE | re.MULTILINE)
    pattern_justice_all_caps = re.compile(r"\bJUSTICE(?: [A-Z\.\-']+)+")
    pattern_justice_title_case = re.compile(r"\bJustice(?: [A-Z][a-zA-Z\.\-']*)+")
    pattern_versus = re.compile(r"(?ix)\b(?:vs\.?|versus)\b")

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                filepath = os.path.join(folder_path, filename)
                logging.info(f"Processing file: {filename}")

                try:
                    collected_lines = []
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            if pattern_versus.search(line):
                                break
                            collected_lines.append(line)

                    text = "".join(collected_lines)

                    matches = []
                    mr_justice_matches = [match.group(0).strip() for match in pattern_mr_justice.finditer(text)]
                    
                    if mr_justice_matches:
                        matches = mr_justice_matches
                        # logging.info(f"Found MR./MRS./MS. JUSTICE matches in {filename}")
                        successcount += 1
                        batchcount += 1
                    else:
                        matches += pattern_justice_all_caps.findall(text)
                        matches += pattern_justice_title_case.findall(text)
                        # logging.info(f"Found JUSTICE matches in {filename}")
                        successcount += 1
                        batchcount += 1

                    unique_judges = sorted(set(matches))
                    

                    results.append({
                        "filename": filename,
                        "judges": ", ".join(unique_judges) if unique_judges else "No match"
                    })
                    
                    if batchcount == batchcount_print: 
                        logging.info(f"Successfully extracted judges for {successcount} no of files")
                        batchcount = 0
                except Exception as e:
                    logging.error(f"Error processing file {filename}: {e}")
                    logging.exception(e)

        logging.info(f"Completed judge extraction for folder: {folder_path}")
    except Exception as e:
        logging.error(f"Error accessing folder {folder_path}: {e}")
        logging.exception(e)

    return results




#extracting hearing date
def extract_hearingdate_from_folder(folder_path):
    results = []
    batch_count = 0
    success_count = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read() 

            # Normalize spaces and line breaks for initial regex matching
            text = re.sub(r'\s+', ' ', raw_text)

            # First: single-date patterns
            match1 = re.search(r'(?i)Date of hearing\s*[:;]?\s*(\d{2}\.\d{2}\.\d{4})', text)
            match2 = re.search(r'(?i)Date of hearing\s*[:;]?\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})', text)

            hearing_date = "No date found"
            
            try:
                if match1:
                    date_str = match1.group(1).strip()
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                    hearing_date = date_obj.strftime("%d-%m-%Y")
                    batch_count += 1
                    success_count += 1

                elif match2:
                    date_str = match2.group(1).strip()
                    date_obj = datetime.strptime(date_str, "%d %B %Y")
                    hearing_date = date_obj.strftime("%d-%m-%Y")
                    batch_count += 1
                    success_count += 1

                else:
                    # Handling date formats like "12 and 13 January 2024"
                    pattern = r'(?i)Date(?:s)? of hearing\s*[:;]?\s*((?:\d{1,2}(?:,|\s+and\s+)?\s*)+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})'
                    match_multi = re.search(pattern, text)

                    hearing_dates = []
                    if match_multi:
                        date_segment = match_multi.group(1)
                        month = match_multi.group(2)
                        year_match = re.search(rf'{month}\s+(\d{{4}})', date_segment, re.IGNORECASE)
                        year = year_match.group(1) if year_match else None

                        if year:
                            days = re.findall(r'\d{1,2}', date_segment.split(month)[0])
                            for day in days:
                                try:
                                    date_obj = datetime.strptime(f"{int(day)} {month} {year}", "%d %B %Y")
                                    hearing_dates.append(date_obj.strftime("%d-%m-%Y"))
                                except ValueError:
                                    continue

                    if not hearing_dates:
                        fallback_pattern = r'(?i)Date(?:s)? of hearing\s*[:;]?\s*((?:\d{2}\.\d{2}\.\d{4}[,\sand]*)+)'
                        match_fallback = re.search(fallback_pattern, text)
                        if match_fallback:
                            date_strs = re.findall(r'\d{2}\.\d{2}\.\d{4}', match_fallback.group(1))
                            for ds in date_strs:
                                try:
                                    date_obj = datetime.strptime(ds, "%d.%m.%Y")
                                    hearing_dates.append(date_obj.strftime("%d-%m-%Y"))
                                except ValueError:
                                    continue

                    if not hearing_dates:
                        hearing_date = "No date found"
                    elif len(hearing_dates) == 1:
                        hearing_date = hearing_dates[0]
                        batch_count += 1
                        success_count += 1
                    else:
                        hearing_date = hearing_dates
                        batch_count += 1
                        success_count += 1
            except ValueError:
                hearing_date = "Invalid date format"

            #Final fallback: look for "Islamabad" followed by date on the next line
            if hearing_date == "No date found":
                fallback_match = re.search(
                    r'(?i)Islamabad\s*[:.,]?\s*\n\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})',
                    raw_text
                )
                if fallback_match:
                    date_str = fallback_match.group(1).strip()
                    try:
                        date_obj = datetime.strptime(date_str, "%d %B %Y")
                        hearing_date = date_obj.strftime("%d-%m-%Y")
                        batch_count += 1
                        success_count += 1
                    except ValueError:
                        hearing_date = "Invalid date format"
            
            if batch_count == batchcount_print:
                logging.info(f"Successfuly extracted hearing dates from {success_count} no of files" )
            results.append({
                "filename": filename,
                "hearing_date": hearing_date
            })

    return results



#extracting case numbers
def extract_casenumber_from_folder(folder_path):
    results = []
    successcount = 0
    batchcount = 0
    patterns = [
        r"Crl\.P\.L\.A\.[\w\-]+\/\d{4}",  # Pattern 1
        r"C\.P\.L\.A[s]?\.?\s*(?:[\w\-]+(?:,?\s*(?:and\s*)?[\w\-]+)*)(?:\s*\/\d{4}|\s*of\s*\d{4})",  # Pattern 2
        r"(?:Nos?\.?\s*(?:[\w\-]+(?:,\s*[\w\-]+)*(?:\s*(?:and|&|to|–)\s*[\w\-]+)?|[\w\-]+(?:\s*(?:and|&|to|–)\s*[\w\-]+)?))\s*(?:of|/)\s*\d{2,4}"  # Pattern 3
    ]

    logging.info(f"Starting case number extraction from folder: {folder_path}")

    try:
        filenames = os.listdir(folder_path)
    except Exception as e:
        logging.error(f"Failed to list directory '{folder_path}': {e}")
        return results  # Return empty list if folder can't be read

    for filename in filenames:
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                logging.error(f"Error reading file '{filepath}': {e}")
                continue
            logging.info(f"processing'{filename}' for case number extraction")
            case_number = " "
            try:
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        case_number = match.group()
                        successcount += 1
                        batchcount += 1
                        # logging.info(f"Match found in file '{filename}': {case_number}")
                        break
            except Exception as e:
                logging.error(f"Regex error in file '{filename}': {e}")

            results.append({
                "filename": filename,
                "case_number": case_number
            })

            if batchcount == 10:
                logging.info(f"Successfully extracted case_number from {successcount} files")
                batchcount = 0
    logging.info("Case number extraction completed.")
    return results




#extracting case title
def extract_casetitle_from_folder(folder_path):
    results = []
    pattern = r'\((.*Jurisdiction\s*)\)'
    successcount = 0
    batchcount = 0
    logging.info(f"Starting case title extraction from folder: {folder_path}")

    try:
        filenames = os.listdir(folder_path)
    except Exception as e:
        logging.error(f"Failed to list directory '{folder_path}': {e}")
        return results
         
    for filename in filenames:
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                logging.error(f"Error reading file '{filepath}': {e}")
                continue
            logging.info(f"Processing file {filename} for case title extraction")
            case_title = ""
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    case_title = match.group(1).strip()
                    successcount += 1
                    batchcount += 1
                    # logging.info(f"Match found in '{filename}': {case_title}")
                else:
                    logging.warning(f"No match found in '{filename}'")
            except Exception as e:
                logging.error(f"Regex error in file '{filename}': {e}")

            results.append({
                "filename": filename,
                "case_title": case_title
            })

            # Log file completion
            if batchcount == batchcount_print: 
                logging.info(f"Extraction of case title completed for {successcount} No of files")
                batchcount = 0
    logging.info("Case title extraction completed for all files.")
    return results



#extracting respondent name
def extract_respondentname_from_folder(folder_path):
    results = []
    successcount = 0
    batchcount = 0
    respondent_pattern = r"""(?ix)(?:vs\.?|versus)\s*[\r\n]*  # versus variants
                            (?P<respondent>(?:["“]?)[A-Z][^\n]*?    # respondent capture group
                            (?:[\r\n]+[^\n]*?)*?)\s*                 # multiline respondent text
                            (?:\.{2,}|…+)?\s*Respondent(?:s)?(?:\(\w+\))?"""  # suffixes

    logging.info(f"Starting respondent name extraction from folder: {folder_path}")

    try:
        filenames = os.listdir(folder_path)
    except Exception as e:
        logging.error(f"Failed to list directory '{folder_path}': {e}")
        return results

    for filename in filenames:
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                logging.error(f"Error reading file '{filepath}': {e}")
                continue
            logging.info(f"Processing file {filename} for respondent name extraction")
            respondent = ""
            try:
                match = re.search(respondent_pattern, text, flags=re.IGNORECASE | re.VERBOSE)
                if match:
                    respondent = match.group('respondent')
                    respondent = re.sub(r'(\.{2,}|…+|\.)', '', respondent).strip()
                    successcount += 1
                    batchcount += 1
                    # logging.info(f"Match found in '{filename}")
                else:
                    logging.warning(f"No respondent match found in '{filename}'")
            except Exception as e:
                logging.error(f"Regex error in file '{filename}': {e}")

            results.append({
                "filename": filename,
                "respondent": respondent
            })

            if batchcount == batchcount_print:
                logging.info(f"Extraction of respondent name completed for {successcount} no of files")
                batchcount = 0
    logging.info("Respondent name extraction completed for all files.")
    return results




#extracting petitioner name
def extract_petitionername_from_folder(folder_path):
    results = []
    successcount = 0
    batchcount = 0
    pattern2 = re.compile(
        r'[\.\)\]]\s*\n'                   # Match ., ), or ] followed by newline
        r'(?=[A-Z])'                      # Next line starts with a capital letter
        r'(.*?)'                         # Non-greedy match for petitioner name
        r'(?=\s*(?:\.{2,}|(?:\.\s*){2,}|…+)?\s*'  # Optional ellipsis or spaced dots
        r'\b(?:Petitioner(?:\(s\))?|Petitioners|Applicants?\(?s?\)?|Appellants?)\b)',  # Petitioner-like keywords
        re.IGNORECASE | re.DOTALL
    )

    logging.info(f"Starting petitioner name extraction from folder: {folder_path}")

    try:
        filenames = os.listdir(folder_path)
    except Exception as e:
        logging.error(f"Failed to list directory '{folder_path}': {e}")
        return results

    for filename in filenames:
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            logging.info(f"Processing file: {filename}")

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                logging.error(f"Error reading file '{filepath}': {e}")
                continue

            # Remove jurisdiction parentheticals before searching
            cleaned_text = re.sub(r'\(.*?jurisdiction.*?\)', '', text, flags=re.IGNORECASE)

            petitionername = ""
            try:
                match2 = pattern2.search(cleaned_text)
                if match2:
                    petitionername = match2.group(1).strip()
                    petitionername = re.sub(r'\s*\([^)]*\)\s*$', '', petitionername)  # Remove trailing parentheses
                    petitionername = re.sub(r'(\.{2,}|…+|\.)', '', petitionername).strip()
                    successcount += 1
                    batchcount += 1
                    # logging.info(f"Match found in '{filename}'")
                else:
                    logging.warning(f"No petitioner name match found in '{filename}'")
            except Exception as e:
                logging.error(f"Regex error in file '{filename}': {e}")

            results.append({
                "filename": filename,
                "petitionername": petitionername if petitionername else " "
            })
            if batchcount == batchcount_print:
                logging.info(f"Extraction of prtitioner name completed for {successcount} no of files")
                batchcount = 0

    logging.info("Petitioner name extraction completed for all files.")
    return results




#extracting citations
def extract_citations_from_folder(folder_path):
    results = []
    successcount = 0
    batchcount = 0
    # Citation pattern allowing multiline and variations
    citation_pattern = r'\((?:[^()]*?\b(?:SCMR|PLD|MLD|CLC|CLD|AIR|PTD)\b[^()]*)\)'

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            # Extract all citations with multiline support
            matches = re.findall(citation_pattern, text, flags=re.DOTALL)

            # Clean each match (remove line breaks, leading/trailing spaces)
            cleaned_matches = [match.strip().replace('\n', ' ') for match in matches]

            results.append({
                "filename": filename,
                "citations": cleaned_matches
            })

    return results




#converting extracted texts to df
def extracting_df_from_textfiles(extracted_case_text_dir):
    logging.info("pipline started")
    judgesname_data = extract_judges_from_folder(extracted_case_text_dir)
    df_judgesname = pd.DataFrame(judgesname_data)
    case_type_data = extract_case_type_from_folder(extracted_case_text_dir)
    df_casetype = pd.DataFrame(case_type_data)
    hearing_date_data = extract_hearingdate_from_folder(extracted_case_text_dir)
    df_hearingdate = pd.DataFrame(hearing_date_data)
    case_number_data = extract_casenumber_from_folder(extracted_case_text_dir)
    df_case_number = pd.DataFrame(case_number_data)
    case_title_data = extract_casetitle_from_folder(extracted_case_text_dir)
    df_casetitle = pd.DataFrame(case_title_data)
    case_respondent_data = extract_respondentname_from_folder(extracted_case_text_dir)
    df_respondent = pd.DataFrame(case_respondent_data)
    case_petitioner_data = extract_petitionername_from_folder(extracted_case_text_dir)
    df_petitioner = pd.DataFrame(case_petitioner_data)

    return df_casetype,df_case_number,df_casetitle,df_hearingdate,df_judgesname,df_respondent,df_petitioner    



#coverting the extracted df to xlsx
def combine_df_into_excel(df_casetype,df_case_number,df_casetitle,df_hearingdate,df_judgesname,df_respondent,df_petitioner  ):
    combined_df = df_case_number.merge(df_casetitle, on="filename", how="outer")\
                 .merge(df_casetype, on="filename", how="outer")\
                 .merge(df_hearingdate, on="filename", how="outer")\
                 .merge(df_judgesname, on="filename", how="outer")\
                 .merge(df_respondent, on="filename", how="outer")\
                 .merge(df_petitioner, on="filename", how="outer")
    


    combined_df.to_excel("combine_data_final5.xlsx", index=False)
    return combined_df





def filter_cases_by_keywords(df, accept_keywords, reject_keywords2):
    if not accept_keywords:
        return pd.DataFrame(columns=df.columns) 

    
    pattern = r'\b(?:' + '|'.join([re.escape(word) for word in accept_keywords]) + r')\b'
    pattern2 = r'\b(?:' + '|'.join([re.escape(word) for word in reject_keywords2]) + r')\b'

    #Filter rows where petitionername or respondent contains any keyword
    filtered = df['petitionername'].str.contains(pattern, case=False, na=False) | \
           df['respondent'].str.contains(pattern, case=False, na=False)
    filtered_df = df[filtered]
    filtered_df = filtered_df[~filtered_df['petitionername'].str.contains(pattern2, case=False, na=False)]
    
    if reject_keywords2:
        filtered_df = filtered_df[~filtered_df['case_type'].str.lower().isin([word.lower() for word in reject_keywords2])]
        
    return filtered_df
