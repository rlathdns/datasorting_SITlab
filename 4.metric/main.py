import re
import csv
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial.distance import cosine

# 파일 경로 (로컬 경로로 수정)
file_path = r"C:\Users\USER\Desktop\GROUP_B_output_grouped_more.csv"

# 데이터 읽기
with open(file_path, 'r', encoding='ANSI') as file:
    lines = file.readlines()

# 초기 변수 설정
folder_groups = {}
current_group = None
reading_resource_ids = False

# 특수문자 및 언더바를 공백으로 대체하는 함수
def clean_resource_id(resource_id):
    return re.sub(r'[\W_]+', ' ', resource_id).strip()

# 파일을 한 줄씩 읽으면서 처리
for line in lines:
    line = line.strip()

    # Main Folder: 로 시작하는 줄을 찾음
    if line.startswith("Main Folder:"):
        # res_ 이후의 이름으로 그룹 이름 설정
        group_name = line.split('res_')[-1].strip()
        current_group = group_name
        folder_groups[current_group] = []
        reading_resource_ids = False  # 새로운 그룹이 시작될 때, 리소스 ID 읽기 플래그 초기화

    # Country, Resource 열이 있는 줄을 찾아 리소스 ID 읽기 시작
    elif line.startswith("Country") and "Resource" in line:
        reading_resource_ids = True

    # 리소스 ID를 읽어와 그룹화
    elif reading_resource_ids and current_group:
        parts = line.split(',')
        if len(parts) > 1:
            resource_id = parts[1].strip()  # 두 번째 열이 리소스 ID
            cleaned_id = clean_resource_id(resource_id)
            folder_groups[current_group].append(cleaned_id)

# Jaccard 유사도 계산 함수
def calculate_jaccard(set1, set2):
    set1, set2 = set(set1), set(set2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

# Cosine 유사도 계산 함수
def calculate_cosine(set1, set2):
    # 각 리스트를 하나의 문자열로 변환
    text1 = " ".join(set1)
    text2 = " ".join(set2)

    if not text1 or not text2:
        return 0.0  # 텍스트가 비어 있는 경우 0 반환

    # CountVectorizer 객체 생성 (토큰 패턴을 단어 전체로 지정)
    vectorizer = CountVectorizer(token_pattern=r'(?u)\b\w+\b')
    vectors = vectorizer.fit_transform([text1, text2]).toarray()

    if vectors.shape[1] == 0:
        return 0.0  # 단어가 없는 경우 0 반환

    return 1 - cosine(vectors[0], vectors[1])

# 메인 폴더 그룹 간 유사도 계산
all_results = []

folder_names = list(folder_groups.keys())
for i in range(len(folder_names)):
    for j in range(i + 1, len(folder_names)):
        folder1 = folder_names[i]
        folder2 = folder_names[j]

        jaccard_sim = calculate_jaccard(folder_groups[folder1], folder_groups[folder2])
        cosine_sim = calculate_cosine(folder_groups[folder1], folder_groups[folder2])

        result = {
            'Folder Group 1': folder1,
            'Folder Group 2': folder2,
            'Jaccard Similarity': jaccard_sim,
            'Cosine Similarity': cosine_sim,
        }

        all_results.append(result)

# 유사도 결과를 CSV 파일로 저장
output_file_path = r'C:\Users\USER\Desktop\similarity_results_arrow_more.csv'
with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Folder Group 1', 'Folder Group 2', 'Jaccard Similarity', 'Cosine Similarity']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for result in all_results:
        writer.writerow(result)

print(f"Results have been saved to {output_file_path}")
