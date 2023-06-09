import os
os.environ['PYOPENGL_PLATFORM'] = 'egl'
# os.environ['PYOPENGL_PLATFORM'] = 'osmesa'
# sudo apt-get install llvm-6.0 freeglut3 freeglut3-dev
from pyrender import Mesh, Scene, Viewer
import pyrender

from pyrender import PerspectiveCamera,\
                     DirectionalLight, SpotLight, PointLight,\
                     MetallicRoughnessMaterial,\
                     Primitive, Mesh, Node, Scene,\
                     Viewer, OffscreenRenderer, RenderFlags
from io import BytesIO
import numpy as np
import trimesh
import requests
import time


duck_source = "https://github.com/KhronosGroup/glTF-Sample-Models/raw/master/2.0/Duck/glTF-Binary/Duck.glb"

# duck = trimesh.load("./models/stress80k.glb")
# duck = trimesh.load(BytesIO(requests.get(duck_source).content), file_type='glb')
# duckmesh = Mesh.from_trimesh(list(duck.geometry.values())[0])
duckmesh = Mesh.from_trimesh(trimesh.load("./models/suzanne.stl"))
scene = Scene(ambient_light=np.array([1.0, 1.0, 1.0, 1.0]), bg_color=[0.0, 0.0, 0.0])

duckmesh_pose = np.array([
    [0.0, 0.0, -1.0, 0.0],
    [1.0, 0.0,  0.0, 0.0],
    [0.0, 1.0,  0.0, 0.0],
    [0.0, 0.0,  0.0, 1.0],
])

scene.add(duckmesh, pose=duckmesh_pose)


cam = PerspectiveCamera(yfov=(np.pi / 3.0))
# cam_pose = np.array([
#     [0.0,  -np.sqrt(2)/2, np.sqrt(2)/2, 1.5],
#     [1.0, 0.0,           0.0,           0.0],
#     [0.0,  np.sqrt(2)/2,  np.sqrt(2)/2, 1.4],
#     [0.0,  0.0,           0.0,          1.0]
# ])
# cam_pose = np.array([
#     [1.0, 0.0, 0.0, 0.0],
#     [0.0, 1.0, 0.0, 100.0],
#     [0.0, 0.0, -1.0, -300.0],
#     [0.0, 0.0, 0.0, 1.0]
# ])
import random

# random betwee -1 and 1
randval = random.uniform(-1, 1)

cam_pose = np.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, randval],
    [0.0, 0.0, -1.0, -5.0],
    [0.0, 0.0, 0.0, 1.0]
])

scene.add(cam, pose=cam_pose)

r = pyrender.OffscreenRenderer(viewport_width=640,
                                viewport_height=480,
                                point_size=1.0)
color, depth = r.render(scene)


N=1000
start_time = time.perf_counter()
for i in range(N):
    color, depth = r.render(scene)

print("FPS: ", N / (time.perf_counter() - start_time))

r.delete()

# set all values less than 0 to 0
# color[color < 0] = 0

print(f"{color.shape=} {color.dtype=}")

print(f"{np.amin(color)=} {np.amax(color)=}")
print(f"{np.unique(color, return_counts=True)=}")

# save to file
import cv2
remapped = np.interp(color[:,:,::-1], (0, 1), (0, 255)).astype(np.uint8)
# remapped = np.interp(color[:,:,::-1], (np.amin(color), np.amax(color)), (0, 255)).astype(np.uint8)
print(f"{np.amin(remapped)=} {np.amax(remapped)=}")
cv2.imwrite('duck.png', remapped)
cv2.imwrite('duck_depth.png', depth)
