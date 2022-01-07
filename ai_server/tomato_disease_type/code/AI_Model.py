import tensorflow as tf
import numpy as np
import PIL.Image

from pathlib import Path
PROJECT_DIR = str(Path(__file__).resolve().parent.parent.parent) + '/'

g_model_path = PROJECT_DIR + 'tomato_disease_type/ai_model/'
g_model_name = 'tomato_disease_type_model.h5'

class AI_Model():
    m_ai_model_image_size = 256
    m_ai_model_disease_types = ['D01', 'D04', 'D05', 'H', 'P03']
    m_ai_model = tf.keras.models.load_model(g_model_path + g_model_name)

    def predict_image(self, image):
        assert image is not None
        assert isinstance(image, PIL.Image.Image)

        image = tf.keras.preprocessing.image.img_to_array(image)

        image = image[ : , : , :3]
        image = np.expand_dims(image, axis=0)
        
        predict = self.m_ai_model.predict(image/255.)
        
        # 퍼센트 거름망 추가
        predict_index = int(np.argmax(predict, axis=-1))
        predict = list(predict[0].round(2))
        
        print("predict : ", predict)
        print("predict : ", predict[predict_index])
        print("predict_index : ", predict_index)
        
        if predict[predict_index] < 0.9:
            return 'etc'

        return self.m_ai_model_disease_types[predict_index]

    def get_resize_image_list(self, image_list):
        assert image_list is not None
        assert isinstance(image_list, list)
        assert isinstance(image_list[0], PIL.Image.Image)

        resize_image_list = list()

        for image in image_list:
            if image.size != (self.m_ai_model_image_size, self.m_ai_model_image_size):
                image = image.resize((self.m_ai_model_image_size, self.m_ai_model_image_size))
            resize_image_list.append(image)

        return resize_image_list

    
    def predict_image_list(self, image_list):
        assert image_list is not None
        assert isinstance(image_list, list)
        assert isinstance(image_list[0], PIL.Image.Image)

        resize_image_list = self.get_resize_image_list(image_list)
        
        image_list.clear()
        image_list = None

        predict_list = list()
        for resize_image in resize_image_list:
            temp_predict = self.predict_image(resize_image)
            predict_list.append(temp_predict)

        resize_image_list.clear()
        resize_image_list = None

        return predict_list