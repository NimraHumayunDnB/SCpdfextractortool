from utilis import *
from datetime import datetime
import os
from config import *


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# LOG_FILE_DIR = 'C:/D_Main_Nimra/Example2/log_file_path'
# extracted_case_text_dir = 'processed level 2'
log_file_path = os.path.join(LOG_FILE_DIR, f"data_extraction_TimeStamp_{timestamp}.log")
logging.basicConfig(
    filename=log_file_path,  # Full absolute path
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    force=True,
)

logging.info("Logging initialized successfully.")


if __name__ == "__main__":
    extract_texts_from_pdfs(pdfpath)
    (
        df_casetype,
        df_case_number,
        df_casetitle,
        df_hearingdate,
        df_judgesname,
        df_respondent,
        df_petitioner,
    ) = extracting_df_from_textfiles(extracted_case_text_dir)
    combined_df1 = combine_df_into_excel(
        df_casetype,
        df_case_number,
        df_casetitle,
        df_hearingdate,
        df_judgesname,
        df_respondent,
        df_petitioner,
    )

    filtered_df = filter_cases_by_keywords(
        combined_df1, accept_keywords, reject_keywords2
    )
    filtered_df.to_excel("filterexcel5.xlsx", index=False)
