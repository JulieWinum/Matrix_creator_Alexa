# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 10:50:20 2018

@author: @authors: Winum Julie and Malki Ammar
"""

import numpy as np
from math import pi, exp
from pylab import cos, sin
import scipy.io
from scipy.signal import lfilter
import scipy.io.wavfile as wave

def DOA_beamforming(data): #data is a nx8 matrix

        ########## Constantes ##########
    R = 5.2496267e-2 # ship radius value (calculated using the documentation provided by the manufacturer)
    c = 343 #sound speed in air
    Fc = 1000  # central frequency of the the narrow-band signals
    Fs = 16000 # sampling rate
    shape_data = data.shape
    n =  shape_data[0]
    
    ########   Frequency domaine visualization before real=>imag transformation ###########   
    M=np.mat(np.linspace(0,(n-1)/Fs,num=n))
    M=M.transpose()
    datacos=np.mat(np.zeros((n,8)))
    datasin=np.mat(np.zeros((n,8)))
    data2=np.mat(1j*np.zeros((n,8)))
    
    for i in range(8) :
        datacos[:,i]= np.multiply(data[:,i],cos(2*pi*Fc*M)) 
        datasin[:,i]= np.multiply(data[:,i],sin(2*pi*Fc*M))
        data2[:,i]=datacos[:,i]-1j*datasin[:,i]
 
    
    ###########   Low pass filter    ############# 
    
    
    mat_filter = scipy.io.loadmat('slpf.mat')['slpf']
    mat_filter = mat_filter.transpose()
    mat_filter = mat_filter.reshape((mat_filter.size,))
    data3=np.mat(1j*np.zeros((n,8)))
    
    for i in range(8) :
        data3[:,i]=lfilter(mat_filter,1, data2[:,i], axis=0)
    
    
    ###########  Delays calculation  ##########
    
    lambda1 = c/Fc
    max_score = -1000000
    l_theta=1# 100
    l_phi=100
   # v_theta= pi/2#np.mat(np.linspace(0,pi,l_theta))
    v_phi= np.mat(np.linspace(0,2*pi,l_phi))
    theta_max =0
    phi_max =0
    
    score_mat = np.mat(np.zeros((l_theta,l_phi)))
    Tau=np.mat(np.zeros((8,1)))
    var=-(1j*2*pi/lambda1)
    
    for itheta in range(l_theta) :
        for iphi in range(l_phi) :
            theta = pi/2#v_theta[0,itheta]
            phi = v_phi[0,iphi]
            for ii in range(8) :
                Tau[ii] = R*sin(theta)*(cos(phi ) - cos(phi+ (pi/4)*(ii)));
            
            mat_a=np.multiply(var,Tau)
            a = np.power(exp(1),mat_a)
            a = a.H
          
            
            dataprime=np.transpose(data3)
            vv=a*dataprime
           # vv=abs(vv)/8
            score =  np.var(vv)
         
            # maximizing the score
            if score>max_score :
                max_score = score
                theta_max = theta
                phi_max = phi
               
    
            score_mat[itheta,iphi] = score
    
    ############### Radian to degres ###########
    theta_max = theta_max*180/pi; 
    phi_max = phi_max*180/pi;


    
    return [phi_max]

def data_creation(): # for a duration of 0.0625s
    Name=['channel_0.wav','channel_1.wav','channel_2.wav','channel_3.wav','channel_4.wav','channel_5.wav','channel_6.wav','channel_7.wav']

    data=np.matrix([],dtype=complex)
    for str in Name :
        Fs,data1 = wave.read(str)
        
        #Remplissage des matrices
        data1=np.matrix(data1)
        data1=data1.transpose()
        if str == 'channel_0.wav' :
            data=data1
        else :
            data=np.concatenate((data,data1),1)
    return data

if __name__ == "__main__":  
    data = data_creation()      
    N = 1000
    #phi_max = DOA_beamforming(data[10*N-1:11*N-1,:])   
    phi_max = DOA_beamforming(data)   
    print(phi_max)    