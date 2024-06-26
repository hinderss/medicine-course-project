import xml.etree.ElementTree
from collections import defaultdict


class DiseaseDefiner:
    def __init__(self, xml_file_path):
        self.diseases = []
        tree = xml.etree.ElementTree.parse(xml_file_path)
        root = tree.getroot()
        for disease in root.findall('disease'):
            name = disease.find('name').text
            symptoms = [symptom.text for symptom in disease.find('symptoms').findall('symptom')]
            doctor = disease.find('doctor').text
            self.diseases.append({
                'name': name,
                'symptoms': symptoms,
                'doctor': doctor
            })

    def get_possible_disease(self, symptoms):
        possible_diseases = []

        for disease in self.diseases:
            if all(symptom in symptoms for symptom in disease['symptoms']):
                possible_diseases.append({
                    'name': disease['name'],
                    'doctor': disease['doctor']
                })

        if possible_diseases:
            return possible_diseases
        else:
            return self.get_most_matching_disease(symptoms)

    def get_most_matching_disease(self, symptoms):
        matching_counts = defaultdict(list)

        for disease in self.diseases:
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

    def get_unique_symptoms(self):
        symptoms = set()
        for disease in self.diseases:
            symptoms.update(disease['symptoms'])
        return sorted(symptoms)
