import os
import csv
from collections import defaultdict

def count_icon_classes(base_folder):
    # 각 폴더 내 아이콘 클래스별로 카운트를 저장할 딕셔너리 초기화
    icon_class_counts = defaultdict(lambda: defaultdict(int))
    all_icon_classes = set()

    # 폴더를 재귀적으로 탐색하는 함수
    def explore_folder(folder_path, folder_name):
        for entry in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry)
            if os.path.isdir(entry_path):
                # 하위 폴더가 있는 경우 재귀적으로 탐색
                explore_folder(entry_path, folder_name)
            elif entry.endswith(".csv") and "_" in entry:
                # 파일 이름이 지정된 형식에 맞는지 확인
                parts = entry.split('_')
                if parts[0].isdigit():  # 첫 번째 부분이 숫자인지 확인
                    count = int(parts[0])  # 파일 이름의 첫 번째 부분을 정수로 변환
                    icon_class = parts[-1].replace(".csv", "")  # 마지막 부분이 아이콘 클래스
                    icon_class_counts[icon_class][folder_name] += count  # 아이콘 클래스별로 카운트 추가
                    all_icon_classes.add(icon_class)

    # 상위 폴더 내 각 하위 폴더를 순회
    for subdir in os.listdir(base_folder):
        subdir_path = os.path.join(base_folder, subdir)

        # 하위 폴더인지 확인
        if os.path.isdir(subdir_path):
            explore_folder(subdir_path, subdir)  # 하위 폴더 탐색 시작

    # 결과를 사용자 입력 폴더 이름을 기준으로 CSV 파일로 저장
    output_csv_path = os.path.join(base_folder, f"{os.path.basename(base_folder)}_icon_class_counts.csv")
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 각 하위 폴더 이름을 헤더로 사용
        headers = ['Icon Class'] + sorted(icon_class_counts[next(iter(icon_class_counts))].keys()) + ['Total']
        writer.writerow(headers)

        # 아이콘 클래스와 Total을 포함한 데이터를 리스트에 저장
        rows = []
        for icon_class in all_icon_classes:
            row = [icon_class]
            total_count = 0
            for folder in sorted(icon_class_counts[next(iter(icon_class_counts))].keys()):
                count = icon_class_counts[icon_class].get(folder, 0)
                row.append(count)
                total_count += count
            row.append(total_count)
            rows.append(row)

        # Total을 기준으로 내림차순 정렬
        sorted_rows = sorted(rows, key=lambda x: x[-1], reverse=True)

        # 정렬된 데이터를 CSV 파일에 기록
        for row in sorted_rows:
            writer.writerow(row)

    print(f"결과가 '{output_csv_path}'에 저장되었습니다.")

if __name__ == "__main__":
    # 사용자로부터 상위 폴더 경로를 입력받습니다.
    base_folder = input("상위 폴더 경로를 입력하세요: ").strip()

    # 아이콘 클래스 수를 세는 함수 호출
    count_icon_classes(base_folder)
