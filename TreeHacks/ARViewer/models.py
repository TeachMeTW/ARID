from django.db import models
import uuid
import os
import cv2 as cv
# Create your models here.
def load_images(dir):
    images = []
    files = os.listdir(dir)
    for f in files:
        image_path = os.path.join(dir, f)
        image = cv.imread(image_path)
        images.append(image)
        
    return images  


def p_and_r(instance, fname):
    img_list = load_images('../TreeHacks/media/images')
    upload_to = 'media/images/'
    ext = fname.split('.')[-1]
    
    if instance.pk:
        fname = '{}.{}'.format(instance.pk, ext)
    
    else:
        fname = '{}.{}'.format(len(img_list), ext)
    
    return os.path.join(upload_to, fname)

class IDModel(models.Model):

    image = models.ImageField(upload_to=p_and_r, default="", blank=True, null=True)
    #image_url = models.CharField(max_length = 200, default="", blank=True)
    patient_name = models.CharField(max_length = 200, default="", blank=True)
    
    
