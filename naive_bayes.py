# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class NaiveBayes:
    def __init__(self):
        self.prior_probs = {}
        self.conditional_probs = {}

    def fit(self, X_train, y_train):
        classes, counts = np.unique(y_train, return_counts=True)
        total_samples = len(y_train)
        for i in range(len(classes)):
            self.prior_probs[classes[i]] = counts[i] / total_samples

        for feature in X_train.columns:
            self.conditional_probs[feature] = {}
            for cls in classes:
                cls_data = X_train[y_train == cls][feature]
                # Calcular la frecuencia de cada valor
                if cls_data.dtype == 'object':
                    frequency = cls_data.value_counts().to_dict()
                else:
                    frequency = cls_data.unique()
                self.conditional_probs[feature][cls] = {
                    'frequency': frequency,
                    'mean': cls_data.mean() if cls_data.dtype != 'object' else None,
                    'std': cls_data.std() if cls_data.dtype != 'object' else None
                }

        # Imprimir tablas de frecuencias y de verosimilitud
        self.print_tables(X_train, y_train)

    def print_tables(self, X, y):
        print("Tabla de frecuencias:")
        for feature in self.conditional_probs:
            print(f"\nAtributo: {feature}")
            for cls in self.conditional_probs[feature]:
                print(f"Clase: {cls}")
                if isinstance(self.conditional_probs[feature][cls]['frequency'], dict):
                    print(pd.DataFrame(self.conditional_probs[feature][cls]['frequency'].items(), columns=['Valor', 'Frecuencia']))
                else:
                    print(self.conditional_probs[feature][cls]['frequency'])

        print("\nTabla de verosimilitud:")
        for feature in self.conditional_probs:
            print(f"\nAtributo: {feature}")
            for cls in self.conditional_probs[feature]:
                print(f"Clase: {cls}")
                print("Media:", self.conditional_probs[feature][cls]['mean'])
                print("Desviación estándar:", self.conditional_probs[feature][cls]['std'])

    def predict(self, X_test):
        predictions = []
        for _, sample in X_test.iterrows():
            posterior_probs = {}
            for cls in self.prior_probs:
                posterior_prob = self.prior_probs[cls]
                for feature in X_test.columns:
                    if self.conditional_probs[feature][cls]['mean'] is None:
                        # Manejar caso de atributo categórico
                        frequency = self.conditional_probs[feature][cls]['frequency']
                        likelihood = frequency.get(sample[feature], 0) / (sum(frequency.values()) + 1e-6)  # Corrección para evitar división por cero
                    else:
                        # Manejar caso de atributo continuo
                        mean = self.conditional_probs[feature][cls]['mean']
                        std = self.conditional_probs[feature][cls]['std']
                        likelihood = self.calculate_likelihood(sample[feature], mean, std)
                    posterior_prob *= likelihood
                posterior_probs[cls] = posterior_prob
            predictions.append(max(posterior_probs, key=posterior_probs.get))
        return predictions

    def calculate_likelihood(self, x, mean, std):
        exponent = np.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (np.sqrt(2 * np.pi) * std)) * exponent

#Leer csv
data = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/iris_mixed - iris_mixed.csv')

X = data.drop(columns=['iris'])
y = data['iris']

n_iteraciones = int(input("Ingrese el número de iteraciones (por defecto es 10): ") or 10)

# almacenar las exactitudes de cada iteración
exactitudes = []

for i in range(n_iteraciones):
    # Dividir datos en conjunto de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=i)

    # Inicializar y entrenar el clasificador
    classifier = NaiveBayes()
    classifier.fit(X_train, y_train)

    # Realizar predicciones
    predictions = classifier.predict(X_test)

    # Calcular y almacenar la exactitud de esta iteración
    accuracy = accuracy_score(y_test, predictions)
    exactitudes.append(accuracy)

    # Imprimir la exactitud de esta iteración
    print(f"Exactitud en la iteración {i + 1}: {accuracy}")

# Calcular y mostrar la exactitud promedio
exactitud_promedio = sum(exactitudes) / len(exactitudes)
print(f"Exactitud promedio:{exactitud_promedio}")
