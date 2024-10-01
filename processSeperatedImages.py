# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 11:28:11 2024

@author: SG
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
# import processSeperatedImagesCP as CP
import matplotlib as mpl

os.chdir("C:/Users/Laboratorio/AutoMeasureLCwithPolorizationCamera")
imName=[0] #,[0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240,255]

    
openName=str(0) #"green"+
saveName="new_"
im=plt.imread(openName+".tif")
print(openName+".tif")
im1=im[:,:,1] # green channel

mpl.rcParams['font.size'] = 15
# im_45=im_45withlabel[120:620,100:600] # adjust these arraies to make the light in the center
leftP=im1[0:2048,0:1223]
rightP=im1[0:2048,1224:2448]

im_0=leftP[0:1024,0:1223] #(611-100/612+100) (654-200/655+200)
im_45=leftP[1024:2048,0:1223] #(1636-100/1637+100) (654-200/655+200)

im_n45 = rightP[0:1024, 0:1223]
im_90 = rightP[1024:2048, 0:1223]

norm_0=im_0/255.0
norm_90=im_90/255.0
norm_45=im_45/255.0
norm_n45=im_n45/255.0

# vector=np.zeros(2)
# matrix_QWP=np.array([[1, 0], [0, 1j], ])
# print(norm_45.shape)  # Check the shape of norm_45
# print(norm_n45.shape)
# s3_cal=np.zeros_like(norm_45)
# for i in range (1024):
#     for j in range (1223): 
#         vector[0]=norm_45[i][j]/np.sqrt(2)
#         vector[1]=norm_45[i][j]/np.sqrt(2)
#         s3_1=np.dot(matrix_QWP, vector)
#         s3_2=np.dot(vector, vector)
#         s3_cal[i][j]=np.sqrt(s3_2)

# vector_i=np.zeros(2)
# matrix_QWP_i=np.array([[1, 0], [0, 1j], ])       
# s3_cal_r=np.zeros_like(norm_45)
# for i in range (1024):
#     for j in range (1223): 
#         vector_i[0]=norm_n45[i][j]/np.sqrt(2)
#         vector_i[1]=norm_n45[i][j]/np.sqrt(2)
#         s3_1=np.dot(matrix_QWP_i, vector_i)
#         s3_2=np.dot(vector_i, vector_i)
#         s3_cal_r[i][j]=np.sqrt(s3_2)
vector=np.array([[0], [0] ])
matrix_QWP=np.array([[1, -1j], [-1j, 1] ])
# # print(norm_45.shape)  # Check the shape of norm_45
# # print(norm_n45.shape)
# s3_cal=np.zeros_like(norm_45)
# for i in range (1024):
#     for j in range (1223): 
#         vector[0]=norm_90[i][j]
#         vector[1]=0
#         s3_1=np.dot(matrix_QWP, vector)
#         s3_2=np.dot(vector.conj(), vector)
#         s3_cal[i][j]=np.sqrt(s3_2)

# vector_i=np.zeros(2)
# # matrix_QWP_i=np.array([[1, 0], [0, 1j], ])       
# s3_cal_r=np.zeros_like(norm_45)
# for i in range (1024):
#     for j in range (1223): 
#         vector_i[0]=0
#         vector_i[1]=norm_0[i][j]
#         s3_11=np.dot(matrix_QWP, vector_i)
#         s3_22 = np.dot(vector_i.conj(), vector_i)
#         s3_cal_r[i][j]=np.sqrt(s3_22)

vector[0][0]=norm_90[1023][1222]
vector[1][0]=0
s3_1=np.dot(matrix_QWP, vector)
conj=s3_1.conjugate().transpose()
print(conj.shape,s3_1.shape)
s3_2=np.vdot(vector, vector)
s3_test=np.sqrt(s3_2)
        
        
s0_H_V=norm_0+norm_90
s0_D_A=norm_45+norm_n45
S0_avg=(norm_0+norm_90+norm_45+norm_n45)/2

s0=S0_avg
s1=(norm_0-norm_90)/S0_avg
s2=(norm_45-norm_n45)/S0_avg
# s3=(s3_cal-s3_cal_r)/S0_avg


# h, w, channels = im.shape
# gradient = np.linspace(1,0, 1000)
# color_image = plt.get_cmap('seismic')(gradient)
# color_bar = (color_image[:, :3] * 255).astype(np.uint8) 
# color_bar_3d = np.tile(color_bar[:, np.newaxis, :], (1, 20, 1))

# cmap = plt.get_cmap('seismic')

# # Normalize the matrix to the colormap range, where -1 corresponds to the lowest color, and 1 to the highest
# normalized_matrix = (s1 + 1) /2  # This transforms the range [-1, 1] to [0, 1]
# normalized_matrix_s3 = (s3 + 1) /2
# # Apply the colormap directly
# rgba_image = cmap(normalized_matrix)
# rgba_image_3 = cmap(normalized_matrix_s3)  # This returns RGBA values

# # Convert to RGB by discarding the alpha channel and scale to [0, 255]
# rgb_image = (rgba_image[:, :, :3] *255).astype(np.uint8)
# rgb_image_3 = (rgba_image_3[:, :, :3] *255).astype(np.uint8)

# new_matrix=np.zeros((5, 300))
# plt.figure(8)
# # plt.imshow(rgb_image_3,cmap='seismic')
# plt.imshow(s3,vmin=-1,vmax=1,cmap='seismic')

# plt.colorbar() 
# plt.title("s3")
# plt.minorticks_on()
# plt.grid(which='minor',linestyle=':', linewidth='0.1', color='gray')

# # plt.figure(9)
# # plt.imshow(s0,vmin=0,vmax=1,cmap='hot')
# # plt.colorbar() 
# # plt.title("S0")
# # plt.minorticks_on()
# # plt.grid(which='minor',linestyle=':', linewidth='0.1', color='gray')  


# plt.figure(10)
# plt.imshow(s1,vmin=-1,vmax=1,cmap='seismic')
# plt.colorbar()
# plt.title("S1")
# plt.minorticks_on()
# plt.grid(which='minor',linestyle=':', linewidth='0.1', color='gray')  


# plt.figure(11)
# plt.imshow(s2,vmin=-1,vmax=1,cmap='seismic')
# plt.colorbar()
# plt.title("S2")
# plt.minorticks_on()
# plt.grid(which='minor',linestyle=':', linewidth='0.1', color='gray')  
