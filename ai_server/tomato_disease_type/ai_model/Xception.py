import tensorflow as tf


batch_normalization_momentum = 0.9

activation_function = 'swish'

img_size = 299

def Xception(classes) :
  

  # Entry Flow
  inputs = tf.keras.layers.Input(shape=(img_size, img_size, 3))

  x = tf.keras.layers.Conv2D(32, kernel_size=3, strides=2, padding='same', use_bias=False)(inputs)
  x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
  x = tf.keras.layers.Activation(activation_function)(x)
  x = tf.keras.layers.Conv2D(64, kernel_size=3, padding='same', use_bias=False)(x)
  x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
  x = tf.keras.layers.Activation(activation_function)(x)
  # (None, 150, 150, 64)
  x2 = x

  for size in [128, 256, 728]:
    if size != 128 :
      x = tf.keras.layers.Activation(activation_function)(x)
    x = tf.keras.layers.SeparableConv2D(size, kernel_size=3, padding='same', use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
    x = tf.keras.layers.Activation(activation_function)(x)
    x = tf.keras.layers.SeparableConv2D(size, kernel_size=3, padding='same', use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
    x = tf.keras.layers.MaxPooling2D(3, strides=2, padding='same')(x)
    
    residual_block = tf.keras.layers.Conv2D(size, kernel_size=1, strides=2, padding='same', use_bias=False)(x2)
    residual_block = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(residual_block)
    x = tf.keras.layers.add([x, residual_block])
    x2 = x # skip connection
    
    # (None, 75, 75, 128) -> (None, 38, 38, 256) -> (None, 19, 19, 728)

  # Middle flow
  for _ in range(8):
    for _ in range(3):
        x = tf.keras.layers.Activation(activation_function)(x)
        x = tf.keras.layers.SeparableConv2D(728, kernel_size=3, padding='same', use_bias=False)(x)
        x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
    x = tf.keras.layers.add([x, x2])
    x2 = x
    
  # (None, 19, 19, 728)

  # Exit flow
  x = tf.keras.layers.Activation(activation_function)(x)
  x = tf.keras.layers.SeparableConv2D(728, kernel_size=3, padding='same', use_bias=False)(x)
  x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
  x = tf.keras.layers.Activation(activation_function)(x)
  x = tf.keras.layers.SeparableConv2D(1024, kernel_size=3, padding='same', use_bias=False)(x)
  x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
  x = tf.keras.layers.MaxPooling2D(3, strides=2, padding='same')(x)

  residual_block = tf.keras.layers.Conv2D(1024, kernel_size=1, strides=2, padding='same', use_bias=False)(x2)
  residual_block = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(residual_block)
  x = tf.keras.layers.add([x, residual_block])

  # (None, 10, 10, 1024)

  x = tf.keras.layers.SeparableConv2D(1536, kernel_size=3, padding='same', use_bias=False)(x)
  x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
  x = tf.keras.layers.Activation(activation_function)(x)
  x = tf.keras.layers.SeparableConv2D(2048, kernel_size=3, padding='same', use_bias=False)(x)
  x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
  x = tf.keras.layers.Activation(activation_function)(x)
  x = tf.keras.layers.GlobalAveragePooling2D()(x)

  outputs = tf.keras.layers.Dense(classes, activation='softmax')(x)

  model = tf.keras.Model(inputs=inputs, outputs=outputs)

  return model, img_size