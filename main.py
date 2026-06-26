import os
from collections import defaultdict
from tqdm import tqdm
from send2trash import send2trash
from file_hasher import calculate_sha256

class FileNode:
    def __init__(self, filepath, size):
        self.filepath = filepath
        self.size = size
        self.hash_val = None 

class DuplicateScanner:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.size_dict = defaultdict(list)
        self.hash_dict = defaultdict(list)
        self.duplicate_groups = []

    def scan(self):
        print(f"\n[階段一] 執行深度優先搜尋 (DFS) 走訪目錄樹...")
        all_files = []
        
        for root, _, files in os.walk(self.target_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                all_files.append(filepath)

        for filepath in tqdm(all_files, desc="讀取檔案大小"):
            try:
                size = os.path.getsize(filepath)
                if size > 0: 
                    node = FileNode(filepath, size)
                    self.size_dict[size].append(node)
            except OSError:
                continue

        potential_duplicates = [nodes for nodes in self.size_dict.values() if len(nodes) > 1]
        
        print(f"\n[階段二]  SHA-256 雜湊值比對...")
        
        files_to_hash = [node for group in potential_duplicates for node in group]
        
        for node in tqdm(files_to_hash, desc="計算數位指紋"):
            node.hash_val = calculate_sha256(node.filepath)
            if node.hash_val:
                self.hash_dict[node.hash_val].append(node)

        for hash_val, nodes in self.hash_dict.items():
            if len(nodes) > 1:
                self.duplicate_groups.append(nodes)

    def report_and_clean(self):
        if not self.duplicate_groups:
            print("\n 掃描完成！您的系統很乾淨，沒有發現重複檔案。")
            return

        print(f"\n=== 掃描完成！發現 {len(self.duplicate_groups)} 組重複檔案 ===")
        wasted_space = 0

        for i, group in enumerate(self.duplicate_groups, 1):
            original = group[0]
            duplicates = group[1:] 
            
            wasted_space += original.size * len(duplicates)
            
            print(f"\n群組 {i} (大小: {original.size / (1024*1024):.2f} MB, 共有指紋: {original.hash_val[:8]}...)")
            print(f"  🟢 [保留] {original.filepath}")
            for dup in duplicates:
                print(f"  🔴 [重複] {dup.filepath}")

        print(f"\n總共浪費了約 {wasted_space / (1024*1024):.2f} MB 的空間。")
        
        choice = input("\n是否要將所有標示為 [重複] 的檔案移至資源回收桶？(Y/N): ")
        if choice.lower() == 'y':
            cleaned_count = 0
            for group in self.duplicate_groups:
                for dup in group[1:]:
                    try:
                        send2trash(dup.filepath)
                        cleaned_count += 1
                    except Exception as e:
                        print(f"無法移動檔案 {dup.filepath}: {e}")
            print(f" 清理完成！已將 {cleaned_count} 個檔案移至資源回收桶。")
        else:
            print("已取消清理操作。您的檔案未被更動。")

if __name__ == "__main__":
    print("=== 電腦空間優化與重複檔案掃描器 ===")
    target_directory = input("請輸入要掃描的資料夾絕對路徑 (例如 D:\\Downloads): ")
    
    if os.path.isdir(target_directory):
        app = DuplicateScanner(target_directory)
        app.scan()
        app.report_and_clean()
    else:
        print(" 錯誤：找不到該資料夾，請確認路徑是否正確！")
