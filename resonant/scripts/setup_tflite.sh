#!/bin/bash
# Pre-compiled tflite for arm: https://github.com/iCorv/tflite-runtime
pip3 install https://github.com/iCorv/tflite-runtime/raw/master/tflite_runtime-2.4.0-cp37-cp37m-linux_armv7l.whl
wget https://tfhub.dev/google/lite-model/yamnet/tflite/1?lite-format=tflite -O assets/model.tflite