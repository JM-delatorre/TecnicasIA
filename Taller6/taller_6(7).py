# -*- coding: utf-8 -*-
"""Taller 6(7).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qE7bVApVIqV3NnCU227NNzuBsMpEC5AB

# **Taller** 6

### Integrantes:

- Juliana Catalina De Castro Moreno.
- Juan Manuel De La Torre.

Enlace al Dataset: https://drive.google.com/drive/folders/1xubBP3CGdKed98VNSnP9wPeNDmmgErHJ?usp=drive_link



---

# Conceptos Base

1. **Redes Neuronales Artificiales (ANN):**
Las redes neuronales artificiales son modelos computacionales inspirados en la estructura y función del cerebro humano. Están compuestas por capas de neuronas interconectadas que procesan información para realizar tareas de aprendizaje automático, como clasificación o regresión.

2. **scikit-learn:**
Es una biblioteca de aprendizaje automático de código abierto para el lenguaje de programación Python. Proporciona herramientas simples y eficientes para análisis predictivo y minería de datos, incluyendo implementaciones de varios algoritmos de aprendizaje automático, como SVM, árboles de decisión y redes neuronales.

3. **MLPClassifier:** Es una clase dentro del módulo sklearn.neural_network de scikit-learn que implementa una red neuronal de perceptrones multicapa para clasificación. Permite entrenar un modelo de redes neuronales con diferentes parámetros de configuración, como el número de capas ocultas, el número de neuronas por capa y la función de activación.

4. **Vectores de características:** Son representaciones numéricas de las características o atributos de un conjunto de datos. Cada instancia de datos se representa como un vector, donde cada elemento del vector corresponde a una característica específica. Estos vectores se utilizan como entrada para entrenar modelos de aprendizaje automático, incluyendo redes neuronales.

5. **Desempeño del clasificador:** Se refiere a la capacidad de un modelo de aprendizaje automático para hacer predicciones precisas sobre datos no vistos. El desempeño se evalúa utilizando métricas como precisión, recall, F1-score y matriz de confusión. En el contexto de las redes neuronales, el desempeño puede verse afectado por factores como la arquitectura de la red, los parámetros de entrenamiento y la calidad de los datos.
"""

from google.colab import drive
drive.mount('/content/drive')

"""## Código
1. **Carga de Datos:**

Utiliza un generador de datos para cargar las imágenes del disco en lotes durante el entrenamiento y la validación. Se asume que las imágenes están organizadas en directorios separados para cada clase.
2. **Definición del Modelo:**

Utiliza la arquitectura de la red VGG16 pre-entrenada, pero sin incluir la capa de clasificación densa superior. Esto se hace estableciendo `include_top=False` al cargar el modelo VGG16. Luego, se agregan capas densas personalizadas para la clasificación binaria.
3. **Compilación del Modelo:**

Se compila el modelo utilizando el optimizador Adam y la función de pérdida de entropía cruzada categórica. La métrica de precisión se utiliza para evaluar el rendimiento del modelo durante el entrenamiento.
4. **Entrenamiento del Modelo:**

El modelo se entrena utilizando el método `fit_generator`, que acepta un generador de datos como entrada. Se especifica el número de épocas de entrenamiento y el tamaño del lote.
Durante el entrenamiento, se muestran las métricas de pérdida y precisión tanto para el conjunto de entrenamiento como para el conjunto de validación después de cada época.
5. **Evaluación del Modelo:**

Después del entrenamiento, se evalúa el modelo en el conjunto de prueba utilizando el método evaluate_generator. Esto proporciona la precisión del modelo en el conjunto de prueba.
6. **Análisis de Resultados:**

Se imprime la precisión del modelo en el conjunto de prueba y se muestra la matriz de confusión, así como otras métricas de clasificación como precisión, recall y f1-score para cada clase.
También se calcula el área bajo la curva ROC (AUC-ROC) como medida adicional del rendimiento del modelo.
7. **Advertencias y Observaciones:**

Se manejan advertencias como las métricas de precisión y f1-score que son indefinidas debido a la ausencia de predicciones para una de las clases.
En general, el código muestra un proceso completo de entrenamiento y evaluación de un modelo de clasificación de imágenes utilizando una arquitectura de red neuronal convolucional pre-entrenada. Sin embargo, los resultados indican un problema de sobreajuste que necesita ser abordado para mejorar el rendimiento del modelo en futuras iteraciones.
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.regularizers import l2
from tensorflow.keras.applications import VGG16

# Paths
train_dir = '/content/drive/Shareddrives/Técnicas IA/AVANCE 1/melanoma_cancer_dataset/train'
validation_dir = '/content/drive/Shareddrives/Técnicas IA/AVANCE 1/melanoma_cancer_dataset/test'

# Data Augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

validation_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)

validation_generator = validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)

# Load pre-trained VGG16 model + higher level layers
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Freeze convolutional layers
for layer in base_model.layers:
    layer.trainable = False

# Create new model on top
model = Sequential([
    base_model,
    Flatten(),
    Dense(512, activation='relu', kernel_regularizer=l2(0.01)),
    Dropout(0.7),
    Dense(256, activation='relu', kernel_regularizer=l2(0.01)),
    Dropout(0.7),
    Dense(1, activation='sigmoid', kernel_regularizer=l2(0.01))
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    train_generator,
    epochs=20,
    validation_data=validation_generator
)

# Evaluating the model
test_loss, test_acc = model.evaluate(validation_generator, verbose=2)
print(f'Test accuracy: {test_acc}')

# Predict and compute classification metrics
y_true = validation_generator.classes
y_pred = (model.predict(validation_generator) > 0.5).astype('int32')

from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

print(confusion_matrix(y_true, y_pred))
print(classification_report(y_true, y_pred))
print(f'AUC-ROC: {roc_auc_score(y_true, y_pred)}')

"""# Analisis de resultados:

1. **Regularización L2:**
   - Se agregó regularización L2 a las capas densas del modelo para penalizar los pesos grandes y reducir el sobreajuste. Esto se logró utilizando el parámetro `kernel_regularizer` en las capas densas.

2. **Reducción de Tasa de Aprendizaje:**
   - Se disminuyó la tasa de aprendizaje para ayudar al modelo a converger de manera más suave hacia un mínimo global. Esto se logró utilizando el optimizador Adam con una tasa de aprendizaje reducida.

3. **Aumento de Datos:**
   - Se aplicó aumento de datos en el generador de imágenes de entrenamiento para aumentar la cantidad de datos de entrenamiento y ayudar a prevenir el sobreajuste. Esto se realizó utilizando la clase `ImageDataGenerator` de Keras para aplicar rotación, volteo horizontal y zoom aleatorio a las imágenes durante el entrenamiento.

4. **Técnica de Early Stopping:**
   - Se utilizó la técnica de detención temprana (Early Stopping) para detener el entrenamiento del modelo si la métrica de validación dejaba de mejorar durante un número determinado de épocas. Esto se implementó utilizando la función de devolución de llamada `EarlyStopping` de Keras.

# Análisis de Resultados:

1. **Pérdida y Precisión del Modelo:**
   - Observamos que la pérdida en el conjunto de entrenamiento disminuyó con cada época, lo que indica que el modelo estaba aprendiendo de los datos de entrenamiento. Sin embargo, en el conjunto de validación, la pérdida se estancó o incluso aumentó después de un cierto número de épocas, lo que sugiere un posible sobreajuste.
   - La precisión del modelo en el conjunto de entrenamiento alcanzó el 100%, lo que indica un posible sobreajuste, ya que el modelo está aprendiendo demasiado los datos de entrenamiento y no generaliza bien a nuevos datos.

2. **Matriz de Confusión:**
   - La matriz de confusión muestra que el modelo predijo correctamente la clase negativa en todos los casos (500 de 500), pero no logró predecir correctamente la clase positiva (0 de 500). Esto indica un problema de sesgo en el modelo, donde predice consistentemente una clase sobre la otra, independientemente de las características de la imagen.

3. **Métricas de Clasificación:**
   - Las métricas de clasificación como precisión, recall y f1-score para la clase positiva son todas cero, lo que indica un rendimiento deficiente en la predicción de esta clase.
   - La precisión, el recall y el f1-score para la clase negativa son todos del 100%, lo que indica un rendimiento perfecto en la predicción de esta clase. Sin embargo, esto es engañoso, ya que el modelo simplemente predice la clase negativa para todas las instancias, lo que resulta en una precisión y un recall del 100% para esa clase.

4. **Área bajo la Curva ROC (AUC-ROC):**
   - El AUC-ROC es 0.5, lo que sugiere que el modelo esencialmente predice al azar, ya que el valor AUC-ROC para un clasificador aleatorio es 0.5.

# Conclusiones:

- El modelo sufre de un grave problema de sobreajuste, donde aprende demasiado bien los datos de entrenamiento pero no generaliza bien a nuevos datos.
- Es necesario realizar ajustes adicionales en el modelo, como una arquitectura más compleja, una optimización más cuidadosa de los hiperparámetros y una exploración más profunda del conjunto de datos para abordar este problema de sobreajuste.
- El análisis de los resultados proporciona una comprensión detallada de dónde está fallando el modelo y ofrece orientación sobre cómo mejorar su rendimiento en futuras iteraciones.

"""