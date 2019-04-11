# -*- coding: utf-8 -*-

import tensorflow as tf
import keras
import numpy as np
import os

from cartoon import PKG_ROOT
from cartoon import USE_TF_KERAS
from cartoon.layers import SpatialReflectionPadding, InstanceNormalization
from cartoon.utils import load_net_in
from cartoon.utils import run_by_torch


if USE_TF_KERAS:
    Input = tf.keras.layers.Input
    Conv2D = tf.keras.layers.Conv2D
    DepthwiseConv2D = tf.keras.layers.DepthwiseConv2D
    BatchNormalization = tf.keras.layers.BatchNormalization
    Activation = tf.keras.layers.Activation
    MaxPooling2D = tf.keras.layers.MaxPooling2D
    Layer = tf.keras.layers.Layer
    Model = tf.keras.models.Model
    VGG19 = tf.keras.applications.vgg19.VGG19
else:
    Input = keras.layers.Input
    Conv2D = keras.layers.Conv2D
    DepthwiseConv2D = keras.layers.DepthwiseConv2D
    BatchNormalization = keras.layers.BatchNormalization
    Activation = keras.layers.Activation
    MaxPooling2D = keras.layers.MaxPooling2D
    Layer = keras.layers.Layer
    Model = keras.models.Model
    VGG19 = keras.applications.vgg19.VGG19

def cartoon_generator(input_size=256):

    input_shape=[input_size,input_size,3]
    
    x = Input(shape=input_shape, name="input")
    img_input = x

    # Block 1 : (256,256,3) -> (256,256,64)
    x = SpatialReflectionPadding(3)(x)
    x = Conv2D(64, (7, 7), strides=1, use_bias=True, padding='valid', name="conv1")(x)
    x = InstanceNormalization(name="in1")(x)
    x = Activation("relu")(x)

    # Block 2 : (256,256,64) -> (128,128,128)
    # Todo : strides (1->2)
    x = Conv2D(128, (3, 3), strides=1, use_bias=True, padding='same', name="conv2_1")(x)
    x = Conv2D(128, (3, 3), strides=1, use_bias=True, padding='same', name="conv2_2")(x)
    x = InstanceNormalization(name="in2")(x)
    x = Activation("relu")(x)

    # Block 3 : (128,128,128) -> (64,64,256)
    # Todo : strides (1->2)
    x = Conv2D(256, (3, 3), strides=1, use_bias=True, padding='same', name="conv3_1")(x)
    x = Conv2D(256, (3, 3), strides=1, use_bias=True, padding='same', name="conv3_2")(x)
    x = InstanceNormalization(name="in3")(x)
    x = Activation("relu")(x)
    res_in = x

    # Block 4 : (64,64,256) -> (64,64,256)
    x = SpatialReflectionPadding(1)(x)
    x = Conv2D(256, (3, 3), strides=1, use_bias=True, padding='valid', name="conv4_1")(x)
    x = InstanceNormalization(name="in4_1")(x)
    x = Activation("relu")(x)

    x = SpatialReflectionPadding(1)(x)
    x = Conv2D(256, (3, 3), strides=1, use_bias=True, padding='valid', name="conv4_2")(x)
    x = InstanceNormalization(name="in4_2")(x)
    x = tf.keras.layers.Add()([x, res_in])
    res_in = x

    # Block 5 : (64,64,256) -> (64,64,256)
    x = SpatialReflectionPadding(1)(x)
    x = Conv2D(256, (3, 3), strides=1, use_bias=True, padding='valid', name="conv5_1")(x)
    x = InstanceNormalization(name="in5_1")(x)
    x = Activation("relu")(x)

    x = SpatialReflectionPadding(1)(x)
    x = Conv2D(256, (3, 3), strides=1, use_bias=True, padding='valid', name="conv5_2")(x)
    x = InstanceNormalization(name="in5_2")(x)
    x = tf.keras.layers.Add()([x, res_in])
    
    model = Model(img_input, x, name='cartoon_generator')
    # model.load_weights(h5_fname)
    return model


if __name__ == '__main__':
    model = cartoon_generator(input_size=256)
    model.summary()

    ys_torch = run_by_torch(load_net_in())
    print(ys_torch.shape)

    # 1st conv layer
    w1 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "0.npy")), [2,3,1,0])
    b1 = np.load(os.path.join(PKG_ROOT, "Hayao", "1.npy"))
    model.get_layer(name="conv1").set_weights([w1, b1])

    # 1st in layer
    in1_a = np.load(os.path.join(PKG_ROOT, "Hayao", "2.npy"))
    in1_b = np.load(os.path.join(PKG_ROOT, "Hayao", "3.npy"))
    model.get_layer(name="in1").set_weights([in1_a, in1_b])
    
    w2_1 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "4.npy")), [2,3,1,0])
    b2_1 = np.load(os.path.join(PKG_ROOT, "Hayao", "5.npy"))
    model.get_layer(name="conv2_1").set_weights([w2_1, b2_1])

    w2_2 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "6.npy")), [2,3,1,0])
    b2_2 = np.load(os.path.join(PKG_ROOT, "Hayao", "7.npy"))
    model.get_layer(name="conv2_2").set_weights([w2_2, b2_2])

    # 2nd in layer
    in2_a = np.load(os.path.join(PKG_ROOT, "Hayao", "8.npy"))
    in2_b = np.load(os.path.join(PKG_ROOT, "Hayao", "9.npy"))
    model.get_layer(name="in2").set_weights([in2_a, in2_b])

    # Block3
    w3_1 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "10.npy")), [2,3,1,0])
    b3_1 = np.load(os.path.join(PKG_ROOT, "Hayao", "11.npy"))
    model.get_layer(name="conv3_1").set_weights([w3_1, b3_1])
    w3_2 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "12.npy")), [2,3,1,0])
    b3_2 = np.load(os.path.join(PKG_ROOT, "Hayao", "13.npy"))
    model.get_layer(name="conv3_2").set_weights([w3_2, b3_2])
    in3_a = np.load(os.path.join(PKG_ROOT, "Hayao", "14.npy"))
    in3_b = np.load(os.path.join(PKG_ROOT, "Hayao", "15.npy"))
    model.get_layer(name="in3").set_weights([in3_a, in3_b])

    # Block4
    w4_1 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "16.npy")), [2,3,1,0])
    b4_1 = np.load(os.path.join(PKG_ROOT, "Hayao", "17.npy"))
    model.get_layer(name="conv4_1").set_weights([w4_1, b4_1])
    in4_1a = np.load(os.path.join(PKG_ROOT, "Hayao", "18.npy"))
    in4_1b = np.load(os.path.join(PKG_ROOT, "Hayao", "19.npy"))
    model.get_layer(name="in4_1").set_weights([in4_1a, in4_1b])

    w4_2 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "20.npy")), [2,3,1,0])
    b4_2 = np.load(os.path.join(PKG_ROOT, "Hayao", "21.npy"))
    model.get_layer(name="conv4_2").set_weights([w4_2, b4_2])
    in4_2a = np.load(os.path.join(PKG_ROOT, "Hayao", "22.npy"))
    in4_2b = np.load(os.path.join(PKG_ROOT, "Hayao", "23.npy"))
    model.get_layer(name="in4_2").set_weights([in4_2a, in4_2b])

    # Block5
    w5_1 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "24.npy")), [2,3,1,0])
    b5_1 = np.load(os.path.join(PKG_ROOT, "Hayao", "25.npy"))
    model.get_layer(name="conv5_1").set_weights([w5_1, b5_1])
    in5_1a = np.load(os.path.join(PKG_ROOT, "Hayao", "26.npy"))
    in5_1b = np.load(os.path.join(PKG_ROOT, "Hayao", "27.npy"))
    model.get_layer(name="in5_1").set_weights([in5_1a, in5_1b])

    w5_2 = np.transpose(np.load(os.path.join(PKG_ROOT, "Hayao", "28.npy")), [2,3,1,0])
    b5_2 = np.load(os.path.join(PKG_ROOT, "Hayao", "29.npy"))
    model.get_layer(name="conv5_2").set_weights([w5_2, b5_2])
    in5_2a = np.load(os.path.join(PKG_ROOT, "Hayao", "30.npy"))
    in5_2b = np.load(os.path.join(PKG_ROOT, "Hayao", "31.npy"))
    model.get_layer(name="in5_2").set_weights([in5_2a, in5_2b])


    imgs = np.expand_dims(load_net_in(), axis=0)
    ys = model.predict(imgs)
    print(ys.shape)
    print(np.allclose(ys, ys_torch, rtol=1e-3, atol=1e-3))



