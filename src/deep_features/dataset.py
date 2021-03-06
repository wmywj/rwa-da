# The datasets
import matplotlib.pyplot as plt
import urllib.request
import io
import glob
import numpy as np
import scipy.io
import scipy.ndimage
import re
from network import resize

def load_image(filename):
  return scipy.ndimage.imread(filename, mode='RGB')

def load_image_url(url):
  ext = url.split('.')[-1]
  return plt.imread(io.BytesIO(urllib.request.urlopen(url).read()), ext)

def load_office31_domain(domain):
  dirs = sorted(glob.glob('~/data/office31/{}/images/*'.format(domain)))
  x = []
  y = []
  for i,dir in enumerate(dirs):
    for file in sorted(glob.glob(dir+'/*.jpg')):
      x.append(load_image(file))
      y.append(i)
  return x,y

def load_and_preprocess_office31(network):
  domains = ['amazon','dslr','webcam']
  x = {}
  y = {}
  for domain in domains:
    xd, yd = load_office31_domain(domain)
    yd = np.array(yd, dtype=np.int32)
    xd = network.preprocess_many(xd)
    x[domain] = xd
    y[domain] = yd
  return domains, x, y

def load_and_resize_office31():
  domains = ['amazon','dslr','webcam']
  x = {}
  y = {}
  for domain in domains:
    xd, yd = load_office31_domain(domain)
    yd = np.array(yd, dtype=np.int32)
    xd = np.array([resize(x) for x in xd], dtype=np.float32)
    x[domain] = xd
    y[domain] = yd
  return domains, x, y

def load_office_caltech_domain(domain):
  # Load matlab files
  mat_suffix = 'Caltech10' if domain == 'Caltech' else domain
  # labels
  surf_file  = '../data/office10/{}_SURF_L10.mat'.format(mat_suffix)
  y = scipy.io.loadmat(surf_file)['labels'] # 1..10
  y = y[:,0] - 1
  # caltech uses different category names
  caltech_cat_names = {'003':'backpack', '041':'coffee-mug', '045':'computer-keyboard',
                       '046':'computer-monitor', '047':'computer-mouse', '101':'head-phones',
                       '127':'laptop-101', '224':'touring-bike', '238':'video-projector'}
  # images
  index_file = '../data/office10/{}_SURF_L10_imgs.mat'.format(mat_suffix)
  img_names = scipy.io.loadmat(index_file)['imgNames'][:,0]
  x = []
  for img_name in img_names:
    img_name = img_name[0]
    # map names:
    if domain == 'Caltech':
      # example: Caltech256_projector_238_0089
      #      --> data/caltech256/256_ObjectCategories/238.video-projector/238_0089.jpg
      cat_name, cat_id, img_id = re.match(r'Caltech256_(.*)_([^_]*)_([^_]*)$', img_name).groups()
      if cat_id in caltech_cat_names:
        cat_name = caltech_cat_names[cat_id]
      file = '~/data/caltech256/256_ObjectCategories/{}.{}/{}_{}.jpg'.format(cat_id, cat_name, cat_id, img_id)
    else:
      # example: amazon_projector_frame_0076 --> data/office31/amazon/projector/frame_0076.jpg
      dom_name, cat_name, img_id = re.match(r'([^_]*)_(.*)_(frame_[^_]*)', img_name).groups()
      file = '~/data/office31/{}/images/{}/{}.jpg'.format(domain, cat_name, img_id)
    x.append(load_image(file))
  return x,y

