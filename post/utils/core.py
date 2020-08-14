import os
import random 
from .folder_profile import folder_name as profile_folder_name
from .folder_post import folder_name as post_folder_name
import string
from random import choice

def get_file_extension(filename):
    basename = os.path.basename(filename)
    base, ext = os.path.splitext(basename)
    return base, ext

def upload_image_path(instance,filename):    
    new_file = random.randint(1, 39515623)        
    basename, ext = get_file_extension(filename)
    filename = "{new_file_name}{ext}".format(new_file_name=new_file,ext=ext)

    try:        
        folder_name = profile_folder_name
    except AttributeError:
        try:
            folder_name = post_folder_name
        except AttributeError:
            pass

    return "{folder_name}/{username}/{new_filename}/{filename}".format(
        folder_name=folder_name, username = instance.user, new_filename=new_file, filename=filename
    )
    
def generate_slug():    
    random = string.ascii_uppercase + string.ascii_lowercase + string.digits  
    return ''.join(choice(random) for _ in range(15))

def get_absolute_uri(self,post):
    request = self.context.get('request')
    attribute_url = post.image.url    
    return request.build_absolute_uri(attribute_url)