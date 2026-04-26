import pandas as pd
import json
import os

def preprocess_excel(file_path, output_path):
    print(f"Processing {file_path}...")
    xl = pd.ExcelFile(file_path)
    all_data = []

    for sheet_name in xl.sheet_names:
        print(f"Reading sheet: {sheet_name}")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # We need to find rows that have translations.
        # Based on the preview, translations are usually in columns 1, 2, 3, 4 (0-indexed: B, C, D, E)
        # after the header row (which contains "국문", "영문", etc.)
        
        # Let's try to find the row index where "국문" is located
        header_row_idx = -1
        for i, row in df.iterrows():
            if any("국문" in str(val) for val in row.values):
                header_row_idx = i
                break
        
        if header_row_idx == -1:
            continue
            
        # The data starts from header_row_idx + 1
        data_df = df.iloc[header_row_idx+1:]
        
        for _, row in data_df.iterrows():
            # Column 1: Korean, 2: English, 3: Japanese, 4: Chinese
            # Ensure we have at least Korean and one other language
            ko = str(row.iloc[2]) if len(row) > 2 else ""
            en = str(row.iloc[3]) if len(row) > 3 else ""
            ja = str(row.iloc[4]) if len(row) > 4 else ""
            zh = str(row.iloc[5]) if len(row) > 5 else ""
            
            # Clean up strings (remove NaN, etc.)
            ko = ko.strip() if ko and ko != "nan" else ""
            en = en.strip() if en and en != "nan" else ""
            ja = ja.strip() if ja and ja != "nan" else ""
            zh = zh.strip() if zh and zh != "nan" else ""
            
            if ko and (en or ja or zh):
                all_data.append({
                    "ko": ko,
                    "en": en,
                    "ja": ja,
                    "zh": zh,
                    "source": sheet_name
                })

    # Save to JSON for caching
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(all_data)} translation pairs to {output_path}")

if __name__ == "__main__":
    input_file = "Weverse Global_공지문 (2026 ver.).xlsx"
    output_file = ".tmp/kb_data.json"
    
    if not os.path.exists(".tmp"):
        os.makedirs(".tmp")
        
    preprocess_excel(input_file, output_file)
