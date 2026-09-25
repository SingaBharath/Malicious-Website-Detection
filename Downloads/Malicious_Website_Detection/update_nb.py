import json
with open('Malicious_website_Detection.ipynb', 'r', encoding='utf-8') as f:
    data = json.load(f)

for cell in data.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        for i, line in enumerate(source):
            if 'pd.read_csv("malicious_phish.csv")' in line:
                source[i] = line.replace('pd.read_csv("malicious_phish.csv")', 'pd.read_csv("malicious_phish.csv").sample(10000, random_state=42)')

with open('Malicious_website_Detection.ipynb', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=1)
