# https://github.com/keras-team/keras-applications/blob/master/keras_applications/efficientnet.py

import tensorflow as tf

import os
import math

batch_normalization_momentum = 0.9
DRIVE = 'E:'

DEFAULT_BLOCKS_ARGS = [
    {'kernel_size': 3, 'repeats': 1, 'filters_in': 32, 'filters_out': 16,
     'expand_ratio': 1, 'id_skip': True, 'strides': 1, 'se_ratio': 0.25},
    {'kernel_size': 3, 'repeats': 2, 'filters_in': 16, 'filters_out': 24,
     'expand_ratio': 6, 'id_skip': True, 'strides': 2, 'se_ratio': 0.25},
    {'kernel_size': 5, 'repeats': 2, 'filters_in': 24, 'filters_out': 40,
     'expand_ratio': 6, 'id_skip': True, 'strides': 2, 'se_ratio': 0.25},
    {'kernel_size': 3, 'repeats': 3, 'filters_in': 40, 'filters_out': 80,
     'expand_ratio': 6, 'id_skip': True, 'strides': 2, 'se_ratio': 0.25},
    {'kernel_size': 5, 'repeats': 3, 'filters_in': 80, 'filters_out': 112,
     'expand_ratio': 6, 'id_skip': True, 'strides': 1, 'se_ratio': 0.25},
    {'kernel_size': 5, 'repeats': 4, 'filters_in': 112, 'filters_out': 192,
     'expand_ratio': 6, 'id_skip': True, 'strides': 2, 'se_ratio': 0.25},
    {'kernel_size': 3, 'repeats': 1, 'filters_in': 192, 'filters_out': 320,
     'expand_ratio': 6, 'id_skip': True, 'strides': 1, 'se_ratio': 0.25}
]

CONV_KERNEL_INITIALIZER = {
    'class_name': 'VarianceScaling',
    'config': {
        'scale': 2.0,
        'mode': 'fan_out',
        # EfficientNet actually uses an untruncated normal distribution for
        # initializing conv layers, but keras.initializers.VarianceScaling use
        # a truncated distribution.
        # We decided against a custom initializer for better serializability.
        'distribution': 'normal'
    }
}

DENSE_KERNEL_INITIALIZER = {
    'class_name': 'VarianceScaling',
    'config': {
        'scale': 1. / 3.,
        'mode': 'fan_out',
        'distribution': 'uniform'
    }
}


# --------------------------------------------------------------------------------------------------

def correct_pad(inputs, kernel_size):
    """Returns a tuple for zero-padding for 2D convolution with downsampling.
    # Arguments
        input_size: An integer or tuple/list of 2 integers.
        kernel_size: An integer or tuple/list of 2 integers.
    # Returns
        A tuple.
    """
    input_size = inputs.get_shape().as_list()[1:3]

    if isinstance(kernel_size, int):
        kernel_size = (kernel_size, kernel_size)

    if input_size[0] is None:
        adjust = (1, 1)
    else:
        adjust = (1 - input_size[0] % 2, 1 - input_size[1] % 2)

    correct = (kernel_size[0] // 2, kernel_size[1] // 2)

    return ((correct[0] - adjust[0], correct[0]),
            (correct[1] - adjust[1], correct[1]))


def block(inputs, activation_fn='swish', drop_rate=0., name='',
          filters_in=32, filters_out=16, kernel_size=3, strides=1,
          expand_ratio=1, se_ratio=0., id_skip=True):
    """A mobile inverted residual block.
    # Arguments
        inputs: input tensor.
        activation_fn: activation function.
        drop_rate: float between 0 and 1, fraction of the input units to drop.
        name: string, block label.
        filters_in: integer, the number of input filters.
        filters_out: integer, the number of output filters.
        kernel_size: integer, the dimension of the convolution window.
        strides: integer, the stride of the convolution.
        expand_ratio: integer, scaling coefficient for the input filters.
        se_ratio: float between 0 and 1, fraction to squeeze the input filters.
        id_skip: boolean.
    # Returns
        output tensor for the block.
    """

    # Expansion phase
    filters = filters_in * expand_ratio
    if expand_ratio != 1:
        x = tf.keras.layers.Conv2D(filters, 1, padding='same', use_bias=False, kernel_initializer=CONV_KERNEL_INITIALIZER, name=name + 'expand_conv')(inputs)
        x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum, name=name + 'expand_bn')(x)
        x = tf.keras.layers.Activation(activation_fn, name=name + 'expand_activation')(x)
    else:
        x = inputs

    # Depthwise Convolution
    if strides == 2:
        x = tf.keras.layers.ZeroPadding2D(padding=correct_pad(x, kernel_size), name=name + 'dwconv_pad')(x)
        conv_pad = 'valid'
    else:
        conv_pad = 'same'

    x = tf.keras.layers.DepthwiseConv2D(kernel_size, strides=strides, padding=conv_pad, use_bias=False, depthwise_initializer=CONV_KERNEL_INITIALIZER, name=name + 'dwconv')(x)
    x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum, name=name + 'bn')(x)
    x = tf.keras.layers.Activation(activation_fn, name=name + 'activation')(x)

    # Squeeze and Excitation phase
    if 0 < se_ratio <= 1:
        filters_se = max(1, int(filters_in * se_ratio))
        se = tf.keras.layers.GlobalAveragePooling2D(name=name + 'se_squeeze')(x)
        se = tf.keras.layers.Reshape((1, 1, filters), name=name + 'se_reshape')(se)
        se = tf.keras.layers.Conv2D(filters_se, 1, padding='same', activation=activation_fn, kernel_initializer=CONV_KERNEL_INITIALIZER, name=name + 'se_reduce')(se)
        se = tf.keras.layers.Conv2D(filters, 1, padding='same', activation='sigmoid', kernel_initializer=CONV_KERNEL_INITIALIZER, name=name + 'se_expand')(se)
        x = tf.keras.layers.multiply([x, se], name=name + 'se_excite')

    # Output phase
    x = tf.keras.layers.Conv2D(filters_out, 1, padding='same', use_bias=False, kernel_initializer=CONV_KERNEL_INITIALIZER, name=name + 'project_conv')(x)
    x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum, name=name + 'project_bn')(x)
    if (id_skip is True and strides == 1 and filters_in == filters_out):
        if drop_rate > 0:
            x = tf.keras.layers.Dropout(drop_rate, noise_shape=(None, 1, 1, 1), name=name + 'drop')(x)

        x = tf.keras.layers.add([x, inputs], name=name + 'add')

    return x


def EfficientNet(classes,
                 width_coefficient,
                 depth_coefficient,
                 default_size,
                 dropout_rate=0.2,
                 drop_connect_rate=0.2,
                 depth_divisor=8,
                 activation_fn='swish',
                 blocks_args=DEFAULT_BLOCKS_ARGS,
                 model_name='efficientnet'):
    """
    # Arguments
        width_coefficient: float, scaling coefficient for network width.
        depth_coefficient: float, scaling coefficient for network depth.
        default_size: integer, default input image size.
        dropout_rate: float, dropout rate before final classifier layer.
        drop_connect_rate: float, dropout rate at skip connections.
        depth_divisor: integer, a unit of network width.
        activation_fn: activation function.
        blocks_args: list of dicts, parameters to construct block modules.
        model_name: string, model name.
        classes: optional number of classes to classify images
            into, only to be specified if `include_top` is True, and
            if no `weights` argument is specified.
    # Returns
        A Keras model instance.
    """

    img_input = tf.keras.layers.Input(shape=(default_size, default_size, 3))

    def round_filters(filters, divisor=depth_divisor):
        """Round number of filters based on depth multiplier."""
        filters *= width_coefficient
        new_filters = max(divisor, int(filters + divisor / 2) // divisor * divisor)
        # Make sure that round down does not go down by more than 10%.
        if new_filters < 0.9 * filters:
            new_filters += divisor
        return int(new_filters)

    def round_repeats(repeats):
        """Round number of repeats based on depth multiplier."""
        return int(math.ceil(depth_coefficient * repeats))

    # Build stem
    x = img_input
    x = tf.keras.layers.ZeroPadding2D(padding=correct_pad(x, 3), name='stem_conv_pad')(x)
    x = tf.keras.layers.Conv2D(round_filters(32), 3, strides=2, padding='valid', use_bias=False, kernel_initializer=CONV_KERNEL_INITIALIZER, name='stem_conv')(x)
    x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum, name='stem_bn')(x)
    x = tf.keras.layers.Activation(activation_fn, name='stem_activation')(x)

    # Build blocks
    from copy import deepcopy
    blocks_args = deepcopy(blocks_args)

    b = 0
    blocks = float(sum(args['repeats'] for args in blocks_args))
    for (i, args) in enumerate(blocks_args):
        assert args['repeats'] > 0
        # Update block input and output filters based on depth multiplier.
        args['filters_in'] = round_filters(args['filters_in'])
        args['filters_out'] = round_filters(args['filters_out'])

        for j in range(round_repeats(args.pop('repeats'))):
            # The first block needs to take care of stride and filter size increase.
            if j > 0:
                args['strides'] = 1
                args['filters_in'] = args['filters_out']

            x = block(x, activation_fn, drop_connect_rate * b / blocks, name='block{}{}_'.format(i + 1, chr(j + 97)), **args)
            b += 1

    # Build top
    x = tf.keras.layers.Conv2D(round_filters(1280), 1, padding='same', use_bias=False, kernel_initializer=CONV_KERNEL_INITIALIZER, name='top_conv')(x)
    x = tf.keras.layers.BatchNormalization(momentum = batch_normalization_momentum, name='top_bn')(x)
    x = tf.keras.layers.Activation(activation_fn, name='top_activation')(x)

    x = tf.keras.layers.GlobalAveragePooling2D(name='avg_pool')(x)
    if dropout_rate > 0:
        x = tf.keras.layers.Dropout(dropout_rate, name='top_dropout')(x)

    output = tf.keras.layers.Dense(classes, activation='softmax', kernel_initializer=DENSE_KERNEL_INITIALIZER, name='probs')(x)

    # Create model.
    model = tf.keras.Model(img_input, output, name=model_name)

    return model


def EfficientNetB0(classes):
    img_size = 224
    return EfficientNet(classes=classes, width_coefficient = 1.0, depth_coefficient = 1.0, default_size = img_size, dropout_rate = 0.2, 
                        model_name='efficientnet-b0'), img_size


def EfficientNetB1(classes):
    img_size = 240
    return EfficientNet(classes=classes, width_coefficient = 1.0, depth_coefficient = 1.1, default_size = img_size, dropout_rate = 0.2, 
                        model_name='efficientnet-b1'), img_size


def EfficientNetB2(classes):
    img_size = 260
    return EfficientNet(classes=classes, width_coefficient = 1.1, depth_coefficient = 1.2, default_size = img_size, dropout_rate = 0.3, 
                        model_name='efficientnet-b2'), img_size


def EfficientNetB3(classes):
    img_size = 300
    return EfficientNet(classes=classes, width_coefficient = 1.2, depth_coefficient = 1.4, default_size = img_size, dropout_rate = 0.3, 
                        model_name='efficientnet-b3'), img_size


def EfficientNetB4(classes):
    img_size = 380
    return EfficientNet(classes=classes, width_coefficient = 1.4, depth_coefficient = 1.8, default_size = img_size, dropout_rate = 0.4, 
                        model_name='efficientnet-b4'), img_size


def EfficientNetB5(classes):
    img_size = 456
    return EfficientNet(classes=classes, width_coefficient = 1.6, depth_coefficient = 2.2, default_size = img_size, dropout_rate = 0.4, 
                        model_name='efficientnet-b5'), img_size


def EfficientNetB6(classes):
    img_size = 528
    return EfficientNet(classes=classes, width_coefficient = 1.8, depth_coefficient = 2.6, default_size = img_size, dropout_rate = 0.5, 
                        model_name='efficientnet-b6'), img_size


def EfficientNetB7(classes):
    img_size = 600
    return EfficientNet(classes=classes, width_coefficient = 2.0, depth_coefficient = 3.1, default_size = img_size, dropout_rate = 0.5, 
                        model_name='efficientnet-b7'), img_size

# ----------------------------------------------------------------------------------------

# setattr(EfficientNetB0, '__doc__', EfficientNet.__doc__)
# setattr(EfficientNetB1, '__doc__', EfficientNet.__doc__)
# setattr(EfficientNetB2, '__doc__', EfficientNet.__doc__)
# setattr(EfficientNetB3, '__doc__', EfficientNet.__doc__)
# setattr(EfficientNetB4, '__doc__', EfficientNet.__doc__)
# setattr(EfficientNetB5, '__doc__', EfficientNet.__doc__)
# setattr(EfficientNetB6, '__doc__', EfficientNet.__doc__)
# setattr(EfficientNetB7, '__doc__', EfficientNet.__doc__)