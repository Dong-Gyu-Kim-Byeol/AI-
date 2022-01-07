import tensorflow as tf

bottleneck_Width = 4
theta = 0.5
batch_normalization_momentum = 0.9
activation_function = 'swish'

def SEBlock(pre_layer, r):
    ch = int(pre_layer.get_shape().as_list()[-1])

    se = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(pre_layer)
    se = tf.keras.layers.Activation(activation_function)(se)
    se = tf.keras.layers.GlobalAveragePooling2D()(se)

    se = tf.keras.layers.Dense(int(ch // r), use_bias=False)(se)
    se = tf.keras.layers.Activation(activation_function)(se)
    se = tf.keras.layers.Dense(ch, use_bias=False)(se)
    se = tf.keras.layers.Activation('sigmoid')(se)
    
    se = tf.keras.layers.Reshape((1, 1, ch))(se)
    x = tf.keras.layers.multiply([pre_layer, se])
    return x

def DenseBlock(x, num, growth_rate):
    layer_list = [x]
    for i in range(num): # layer 수가 늘어날수록 layer_list에 있는 x에 대해 새로운 x가 concatenate 된다
      x1 = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
      x1 = tf.keras.layers.Activation(activation_function)(x1)
      x1 = tf.keras.layers.Conv2D(growth_rate * bottleneck_Width, kernel_size=1, padding='same', use_bias=False)(x1)
      
      x1 = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x1)
      x1 = tf.keras.layers.Activation(activation_function)(x1)
      x1 = tf.keras.layers.Conv2D(growth_rate, kernel_size=3, padding='same', use_bias=False)(x1)
      layer_list.append(x1)
      x = tf.keras.layers.concatenate(layer_list, axis=-1) # channel에 대해 layer들을 concatenate
    
    return x

def TransitionLayer(x):
    num_ch = int(x.get_shape().as_list()[-1] * theta) # theta 비율만큼 channel 수를 줄임
    x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
    x = tf.keras.layers.Activation(activation_function)(x)
    x = tf.keras.layers.Conv2D(num_ch, kernel_size=3, padding='same', use_bias=False)(x)
    x = tf.keras.layers.AveragePooling2D(pool_size=2, strides=2, padding='same')(x)
    
    return x

def SE_DenseNet(classes, width_coefficient = 1.0, depth_coefficient = 1.0, img_size = 224, dropout_rate = 0.2) :
  growth_rate = 16
  growth_rate = int(growth_rate * width_coefficient)

  assert (img_size % 32) == 0
  
  inputs = tf.keras.layers.Input(shape=(img_size, img_size, 3))
  x = tf.keras.layers.Conv2D(growth_rate * bottleneck_Width, kernel_size=7, strides=2, padding='same', use_bias=False)(inputs)
  
  x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum)(x)
  x = tf.keras.layers.Activation(activation_function)(x)
  x = tf.keras.layers.MaxPooling2D(pool_size=3, strides=2, padding='same')(x)

  x = DenseBlock(x, int(6 * depth_coefficient), growth_rate)
  x = SEBlock(x, growth_rate)
  x = TransitionLayer(x)
  x = SEBlock(x, growth_rate)

  x = DenseBlock(x, int(12 * depth_coefficient), growth_rate)
  x = SEBlock(x, growth_rate)
  x = TransitionLayer(x)
  x = SEBlock(x, growth_rate)

  x = DenseBlock(x, int(24 * depth_coefficient), growth_rate)
  x = SEBlock(x, growth_rate)
  x = TransitionLayer(x)
  x = SEBlock(x, growth_rate)

  x = DenseBlock(x, int(16 * depth_coefficient), growth_rate)
  x = SEBlock(x, growth_rate)

  x = tf.keras.layers.GlobalAveragePooling2D()(x)
  x = tf.keras.layers.Dropout(dropout_rate)(x)

  outputs = tf.keras.layers.Dense(classes, activation='softmax')(x)

  model = tf.keras.Model(inputs=inputs, outputs=outputs)

  return model, img_size

def SE_DenseEfficientNetB2(classes):
  return SE_DenseNet(classes, width_coefficient = 1.1, depth_coefficient = 1.2, img_size = 256, dropout_rate = 0.3)

def SE_DenseEfficientNetB3(classes):
  return SE_DenseNet(classes, width_coefficient = 1.2, depth_coefficient = 1.4, img_size = 320, dropout_rate = 0.3)