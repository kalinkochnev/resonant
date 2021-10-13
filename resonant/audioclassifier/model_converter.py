import tensorflow as tf

model = tf.keras.models.load_model('model/')
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model= converter.convert()

with open('algo_tflite.tflite', 'wb') as f:
    f.write(tflite_model)