import os
import xml.etree.ElementTree as ET
from collections import defaultdict


class DiseaseDefiner:
    @staticmethod
    def parse_diseases():
        xml_file_path = os.path.join(os.path.dirname(__file__), 'static/diseases.xml')
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        diseases = []
        for disease in root.findall('disease'):
            name = disease.find('name').text
            symptoms = [symptom.text for symptom in disease.find('symptoms').findall('symptom')]
            doctor = disease.find('doctor').text
            diseases.append({
                'name': name,
                'symptoms': symptoms,
                'doctor': doctor
            })
        return diseases

    @staticmethod
    def get_possible_disease(symptoms):
        diseases = DiseaseDefiner.parse_diseases()
        possible_diseases = []

        for disease in diseases:
            if all(symptom in symptoms for symptom in disease['symptoms']):
                possible_diseases.append({
                    'name': disease['name'],
                    'doctor': disease['doctor']
                })

        if possible_diseases:
            return possible_diseases
        else:
            return DiseaseDefiner.get_most_matching_disease(symptoms)

    @staticmethod
    def get_most_matching_disease(symptoms):
        diseases = DiseaseDefiner.parse_diseases()
        matching_counts = defaultdict(list)

        for disease in diseases:
            matching_symptoms = set(symptoms) & set(disease['symptoms'])
            matching_counts[len(matching_symptoms)].append({
                'name': disease['name'],
                'doctor': disease['doctor'],
                'matching_symptoms_count': len(matching_symptoms)
            })

        if matching_counts:
            max_matching_count = max(matching_counts.keys())
            return matching_counts[max_matching_count]
        else:
            return []

    @staticmethod
    def get_unique_symptoms():
        diseases = DiseaseDefiner.parse_diseases()
        symptoms = set()
        for disease in diseases:
            symptoms.update(disease['symptoms'])
        return sorted(symptoms)