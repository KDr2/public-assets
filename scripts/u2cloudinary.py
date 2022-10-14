#!/bin/env python

import os
import yaml

import cloudinary
import cloudinary.uploader
import cloudinary.api

BRANCH = 'main'
META_EXT = ".cloudinary"
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMG_DIR_K = "kdr2-com/images"
IMG_DIR_J = "joshinbrackets/images"
IMG_DIR = [IMG_DIR_K]

def init_cloudinary():
    config_file = os.path.join(APP_ROOT, "config/cloudinary.private.yml")
    if os.path.isfile(config_file):
        cloudinary_config = yaml.safe_load(open(config_file))
        cloudinary.config(**cloudinary_config['production'])
    else:
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            enhance_image_tag=True,
            static_image_support=True,
        )

def local_path(path=''):
    return os.path.join(APP_ROOT, IMG_DIR[0], path)

def asset_url(path):
    return "https://raw.githubusercontent.com/KDr2/public-assets/" + BRANCH + \
        "/{}/{}".format(IMG_DIR[0], path)

def public_id(path):
    if IMG_DIR[0] == IMG_DIR_K:
        return "img-kdr2-com/%s" % (os.path.splitext(path)[0])
    if IMG_DIR[0] == IMG_DIR_J:
        return "joshinbrackets/%s" % (os.path.splitext(path)[0])

def upload2cloudinary(path):
    local_img_path = local_path(path)
    if not os.path.isfile(local_img_path):
        return
    ext_name = os.path.splitext(path)[1][1:]
    if ext_name.lower() not in ("jpg", "jpeg", "gif", "png", "webp", "tiff"):
        return
    meta_path = local_img_path + META_EXT
    if os.path.isfile(meta_path):
        return  # already uploaded
    print(" ==> Uploading Image : %s" % local_img_path)
    ret = cloudinary.uploader.upload(
        asset_url(path),
        public_id=public_id(path),
        format=ext_name,
    )
    if ret.get('version'):
        with open(meta_path, "w") as m:
            m.write("%s" % ret['version'])
    else:
        print(" -- :( upload error: %s", ret['error']['message'])


def walk_fun(root, _dirs, files):
    print("=> Entering Drirectory: %s" % root)
    path = root.replace(local_path(), "")
    for f in files:
        if f.endswith(META_EXT):
            continue
        img = os.path.join(path, f)
        upload2cloudinary(img)
    print("<= Leaving Drirectory:  %s" % root)


if __name__ == '__main__':
    init_cloudinary()
    IMG_DIR[0] = IMG_DIR_K
    for root, dirs, files in os.walk(local_path()):
        walk_fun(root, dirs, files)

    IMG_DIR[0] = IMG_DIR_J
    for root, dirs, files in os.walk(local_path()):
        walk_fun(root, dirs, files)
