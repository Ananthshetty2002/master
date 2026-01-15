
def search_raw():
    try:
        with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
            content = f.read()
            # Start search from end to find 1329 (assuming it's Start Qty and near the beginning of the record, but lets just find all occurrences)
            start_search = 0
            while True:
                index = content.find("1329", start_search)
                if index == -1:
                    break
                print(f"Match at {index}")
                # Print 400 chars around
                s = max(0, index - 200)
                e = min(len(content), index + 200)
                print(f"Context:\n{content[s:e]}\n---")
                start_search = index + 1
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_raw()
