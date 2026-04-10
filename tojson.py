import fitz  # PyMuPDF
import re
import json
import os

def extract_words_from_pdf(pdf_path, output_json_path):
    if not os.path.exists(pdf_path):
        print(f"找不到檔案：{pdf_path}，請確認檔名和路徑是否正確。")
        return

    print("正在讀取 PDF 檔案...")
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
        
    print("正在解析單字與解釋...")
    full_text = re.sub(r'\n[A-Z]\n', '\n', full_text)
    
    # 抓取規則
    pattern = re.compile(r'(\d+)\.\s*([a-zA-Z\-]+(?:\s+[a-zA-Z\-]+)*)\s*(.*?)(?=\n\d+\.\s*[a-zA-Z\-]+|\Z)', re.DOTALL)
    matches = pattern.finditer(full_text)
    
    vocab_list = []
    
    # 定義常見的英文詞性標籤
    valid_pos = {'n', 'v', 'a', 'ad', 'prep', 'con', 'pron', 'aux'}
    
    for match in matches:
        word_id = int(match.group(1))
        raw_word = match.group(2).strip()
        meaning = match.group(3).replace('\n', '').strip()
        
        word = raw_word
        pos = ""
        
        # 情況 1: 詞性黏在單字後面 (例如: "assert v")
        parts = raw_word.split()
        if len(parts) > 1 and parts[-1] in valid_pos:
            word = " ".join(parts[:-1]) # 把最後的詞性切掉，留下純單字
            pos = parts[-1]             # 抓取最後的詞性
            
        # 情況 2: 詞性不小心掉到中文解釋那邊了 (例如: "v斷言" 或 "ad 在國外")
        if not pos:
            # 檢查 meaning 開頭是否為已知詞性，並且後面接空白或中文符號
            pos_match = re.match(r'^(' + '|'.join(valid_pos) + r')(?:\s+|(?=[^\w\s]))(.*)', meaning)
            if pos_match:
                pos = pos_match.group(1)
                meaning = pos_match.group(2).strip()
                
        if word and meaning:
            vocab_list.append({
                "id": word_id,
                "word": word,
                "詞性": pos,
                "meaning": meaning
            })
            
    # 寫入 JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(vocab_list, f, ensure_ascii=False, indent=2)
        
    print(f"轉換大功告成！共成功提取了 {len(vocab_list)} 個單字，已存檔至 {output_json_path}")

if __name__ == "__main__":
    pdf_file = "TOEIC3000.pdf"  # 確保與資料夾中的 PDF 檔名一致
    json_file = "words.json"
    extract_words_from_pdf(pdf_file, json_file)