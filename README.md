# Yolov3-Django-Streaming

This project is to stream an object detection module (Yolo v3) with 2 cameras (2 channels) on a web browser using Django.
The project was built and run in Ubuntu 18.04.

Link Youtube: https://www.youtube.com/watch?v=SDnpNd7xRbE&t=10s

Object detection reference: https://github.com/YunYang1994/tensorflow-yolov3

## USAGE:
1. Download folder "checkpoint" and file "yolov3_coco.pb" from the link below and locate them in the repo:
```bashrc
https://drive.google.com/drive/u/1/folders/1apB-yPIxxzC9D6_iAaQrXWuGpbWIK6Lp
```
2. Navigate terminal to the repo, then run command: 
```bashrc
$ python3 manage.py runserver
```
3. Open any web browser and go to the URL: 
```bashrc
http://127.0.0.1:8000/index
```
## NOTE:
- The 2 camera ids in the source code are "0" and "2" (for my computer). 
- You should change them for running on any other computers. Go to webcam/views.py then change "cam_id".

Hope this project useful.

July 11, 2019

Tran Le Anh
