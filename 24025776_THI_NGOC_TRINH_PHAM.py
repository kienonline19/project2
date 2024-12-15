# Name: THI NGOC TRINH PHAM
# Student ID: 24025776

def read_txt(file_path):
    """ Function to read and parse the disease data from a text file """
    diseases = []

    with open(file_path) as fo:
        for line in fo:
            line = line.strip()

            if len(line) != 0:
                record = {}
                values = line.split(',')

                # Parse each key-value pair in the line
                for value in values:
                    key, val = value.split(':')
                    key = key.strip().lower()
                    val = val.strip()
                    # Try to convert value to integer if possible
                    try:
                        val = int(val)
                    except:
                        pass

                    record[key] = val

                diseases.append(record)

    return diseases


def read_csv(file_path):
    """ Function to read and parse the hospital data from a CSV file """
    hospitals = []

    with open(file_path) as fo:
        # Read and process the header
        header_list = [
            header_name.lower()
            for header_name in fo.readline().strip().split(',')
        ]

        # Read and process each data row
        for line in fo:
            values = line.strip().split(',')

            # Try to convert each value to integer if possible
            for i in range(len(values)):
                try:
                    values[i] = int(values[i])
                except:
                    pass

            # Create a dictionary for each hospital
            record = dict(zip(header_list, values))
            hospitals.append(record)

    return hospitals


def generate_country_specific_hospital_data(hospitals: list[dict], diseases: list[dict]):
    """ Function to generate country-specific hospital data """
    country_to_hospitals = {}
    country_to_death = {}
    country_to_covid_stroke = {}

    # Process hospital data
    for hospital in hospitals:
        country_name = hospital["country"]
        hospital_id = hospital["hospital_id"]
        no_of_deaths_in_2022 = hospital["no_of_deaths_in_2022"]

        # Populate country_to_hospitals and country_to_death dictionaries
        if country_name not in country_to_hospitals:
            country_to_hospitals[country_name] = [hospital_id]
            country_to_death[country_name] = [no_of_deaths_in_2022]
        else:
            country_to_hospitals[country_name].append(hospital_id)
            country_to_death[country_name].append(no_of_deaths_in_2022)

    # Process disease data
    for disease in diseases:
        country_name = disease["country"]
        hospital_id = disease["hospital_id"]
        total = disease["covid"] + disease["stroke"]

        # Populate country_to_covid_stroke dictionary
        if country_name not in country_to_covid_stroke:
            country_to_covid_stroke[country_name] = {hospital_id: total}
        else:
            country_to_covid_stroke[country_name].update({hospital_id: total})

    # Align covid & stroke data with hospital IDs
    ans = {}
    for country_name, disease_dict in country_to_covid_stroke.items():
        if country_name in country_to_hospitals:
            hospital_ids = country_to_hospitals[country_name]

            ans[country_name] = [
                disease_dict[id]
                for id in hospital_ids
                if id in disease_dict
            ]

    return [country_to_hospitals, country_to_death, ans]


def calculate_cosine_similarity(country_death, country_stroke_covid):
    """ Function to calculate cosine similarity """
    cosine_dict = {}

    for country in country_death:
        x = country_death[country]
        y = country_stroke_covid[country]

        if len(x) != len(y):
            continue

        # Calculate cosine similarity
        numerator = sum(a*b for a, b in zip(x, y))
        denominator = (sum(i*i for i in x) ** 0.5) * \
            (sum(j*j for j in y) ** 0.5)

        if denominator != 0:
            cosine_dict[country] = round(numerator / denominator, 4)
        else:
            cosine_dict[country] = 0

    return cosine_dict


def analyze_variance_in_cancer_admissions(hospitals, diseases, category):
    """ Function to analyze variance in cancer admissions """
    variance_dict = {}
    country_category_cancer = {}

    # Find eligible hospitals based on category
    eligible_hospitals = {
        hospital["hospital_id"]
        for hospital in hospitals
        if hospital["hospital_category"].lower() == category.lower()
    }

    # Collect cancer data for eligible hospitals
    for disease in diseases:
        country = disease["country"]
        hospital_id = disease["hospital_id"]

        if hospital_id in eligible_hospitals:
            if country not in country_category_cancer:
                country_category_cancer[country] = [disease["cancer"]]
            else:
                country_category_cancer[country].append(disease["cancer"])

    # Calculate variance for each country
    for country, cancer_data in country_category_cancer.items():
        num = len(cancer_data)
        if num > 1:
            mean = sum(cancer_data) / num
            variance = sum((x - mean)**2 for x in cancer_data) / (num - 1)
            variance_dict[country] = variance
        else:
            variance_dict[country] = 0

    return variance_dict


def generate_hospital_category_statistics(hospitals):
    """ Function to generate hospital category statistics """
    category_country_dict = {}

    # Collect data for each hospital
    for hospital in hospitals:
        category = hospital["hospital_category"]
        country = hospital["country"]
        female_patients = hospital["female_patients"]
        staff = hospital["no_of_staff"]
        deaths_2022 = hospital["no_of_deaths_in_2022"]
        deaths_2023 = hospital["no_of_deaths_in_2023"]

        # Organize data by category and country
        if category not in category_country_dict:
            category_country_dict[category] = {}

        if country not in category_country_dict[category]:
            category_country_dict[category][country] = {
                "female_patients": [],
                "staff": [],
                "deaths_2022": [],
                "deaths_2023": []
            }

        category_country_dict[category][country]["female_patients"].append(
            female_patients)
        category_country_dict[category][country]["staff"].append(staff)
        category_country_dict[category][country]["deaths_2022"].append(
            deaths_2022)
        category_country_dict[category][country]["deaths_2023"].append(
            deaths_2023)

    # Calculate statistics for each category and country
    for category in category_country_dict:
        for country, data in category_country_dict[category].items():
            avg_female = sum(data["female_patients"]) / \
                len(data["female_patients"])
            max_staff = max(data["staff"])
            avg_deaths_2022 = sum(data["deaths_2022"]) / \
                len(data["deaths_2022"])
            avg_deaths_2023 = sum(data["deaths_2023"]) / \
                len(data["deaths_2023"])

            percent_change = (
                (avg_deaths_2023 - avg_deaths_2022) / avg_deaths_2022) * 100

            category_country_dict[category][country] = [
                round(avg_female, 4),
                max_staff,
                round(percent_change, 4)
            ]

    return category_country_dict


def main(csv_file="hospital_data.csv", txt_file="disease.txt", category="children"):
    """ Main function to execute all tasks """
    hospital_data = read_csv(csv_file)
    disease_data = read_txt(txt_file)
    op1 = generate_country_specific_hospital_data(hospital_data, disease_data)
    _, country_death_dict, country_stroke_covid_dict = op1
    op2 = calculate_cosine_similarity(
        country_death_dict, country_stroke_covid_dict)
    op3 = analyze_variance_in_cancer_admissions(
        hospital_data, disease_data, category)
    op4 = generate_hospital_category_statistics(hospital_data)
    print(op1)
    return op1, op2, op3, op4
