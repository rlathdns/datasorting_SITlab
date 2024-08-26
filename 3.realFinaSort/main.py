import csv
import re
import os
import chardet  # 파일 인코딩을 감지하기 위해 chardet 사용


def extract_data_from_csv(file_path):
    # 파일의 인코딩을 감지
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']

    with open(file_path, mode='r', encoding=encoding, errors='replace') as file:
        csv_reader = csv.reader(file)
        resource_id_pattern = re.compile(r'resource-id:.*:id/(.*)')
        app_name_pattern = re.compile(r'App Name:(.*)')

        resource_id = None
        app_name = None

        extracted_data = []

        for row in csv_reader:
            if not row:
                continue
            line = row[0]

            resource_id_match = resource_id_pattern.match(line)
            if resource_id_match:
                resource_id = resource_id_match.group(1).strip()
                app_name = None  # Reset app_name whenever a new resource-id is found

            app_name_match = app_name_pattern.match(line)
            if app_name_match:
                app_name = app_name_match.group(1).strip()
                if resource_id and app_name:
                    extracted_data.append((resource_id, app_name))
                    resource_id = None  # Reset resource_id after storing the pair
                    app_name = None  # Reset app_name after storing the pair

    return extracted_data


def process_csv_files(root_folder, icon_class):
    all_extracted_data = {}

    # 최상위 폴더 내부의 모든 하위 폴더 탐색
    for folder in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder)

        if os.path.isdir(folder_path):  # 폴더인지 확인
            print(f"Processing folder: {folder}")
            all_extracted_data[folder] = []

            # 국가 코드 이름으로 된 하위 폴더 탐색
            for country_folder in os.listdir(folder_path):
                country_folder_path = os.path.join(folder_path, country_folder)

                if os.path.isdir(country_folder_path):  # 국가 코드 폴더인지 확인
                    print(f"  Found country folder: {country_folder}")

                    # 해당 국가 코드 폴더 내의 CSV 파일 탐색
                    for file in os.listdir(country_folder_path):
                        if file.endswith('.csv'):
                            file_base_name = file.lower()

                            # 사용자 입력 아이콘 클래스와 파일 이름에서 'ca_' 이후의 부분 비교
                            icon_part = file_base_name.split(f'{country_folder.lower()}_')[1].replace('.csv', '')
                            if icon_part == icon_class.lower():
                                file_path = os.path.join(country_folder_path, file)

                                # CSV 파일에서 데이터 추출
                                data = extract_data_from_csv(file_path)
                                all_extracted_data[folder].extend(
                                    [(country_folder, resource_id, app_name) for resource_id, app_name in data])

                                # 아이콘 클래스 파일 경로 및 내용 출력
                                print(f'    아이콘 클래스 파일 경로: {file_path}')

    return all_extracted_data


def save_to_csv(file_path, data):
    with open(file_path, mode='w', encoding='ANSI', newline='') as file:
        writer = csv.writer(file)

        for folder, entries in data.items():
            # 메인 폴더 이름을 제목으로 기록
            writer.writerow([f'Main Folder: {folder}'])
            writer.writerow(['Country', 'Resource ID', 'App Name'])

            for entry in entries:
                writer.writerow(entry)

            # 메인 폴더별로 구분을 위해 빈 줄 추가
            writer.writerow([])


def main():
    # 아이콘 클래스 입력 받기
    icon_class = input("비교할 아이콘 클래스를 입력하세요: ")

    # 사용자로부터 폴더 이름 입력 받기
    folder_name = input("폴더 이름을 입력하세요: ")

    # 최상위 폴더 경로 설정 (Desktop 내의 폴더)
    root_folder = os.path.join(os.path.expanduser("~/Desktop"), folder_name)

    # CSV 파일에서 데이터 추출 및 아이콘 클래스 파일 내용 읽기
    all_data = process_csv_files(root_folder, icon_class)

    # 결과를 하나의 CSV 파일로 저장
    output_file_path = os.path.join(os.path.expanduser("~/Desktop"), f"{folder_name}_output_grouped_{icon_class}.csv")
    save_to_csv(output_file_path, all_data)
    print(f"결과가 {output_file_path}에 저장되었습니다.")


if __name__ == '__main__':
    main()
