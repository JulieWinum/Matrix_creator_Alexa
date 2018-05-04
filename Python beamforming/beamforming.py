import numpy as np
from math import pi, exp
import matplotlib.pyplot as plt
import scipy.io.wavfile as wave
from pylab import cos, sin
import scipy.io
from scipy.signal import lfilter, filtfilt
from time import time
from scipy.fftpack import fft

########## Constantes ##########
R = 5.2496267e-2 # ship radius value (calculated using the documentation provided by the manufacturer)
c = 343 #sound speed in air
Fc = 1000  # central frequency of the the narrow-band signals
#Fpass = 350   # low-pass filter parameter
#Fstop = 400
#Apass = 1
#Astop = 65



######## Audioread   ###########
Name=['channel_0.wav','channel_1.wav','channel_2.wav','channel_3.wav','channel_4.wav','channel_5.wav','channel_6.wav','channel_7.wav']

data=np.matrix([],dtype=complex)
for str in Name :
    Fs,data1 = wave.read(str)
    n = data1.size
    duree = 1.0*n/Fs
    
    #Remplissage des matrices
    data1=np.matrix(data1)
    data1=data1.transpose()
    if str == 'channel_0.wav' :
        data=data1
    else :
        data=np.concatenate((data,data1),1)
 
#Matrices remplis
print('Fs: {}'.format(Fs))
print('Durée: {}'.format(duree))
print('Nombre d échantillons: {}'.format(n))

#n=500
#data=data[0:n,:]



####### Affichage des signaux avant modification ##########
#for i in range(8) :
#    te = 1.0/Fs
#    t = np.zeros(n)
#    for k in range(n):
#        t[k] = te*k
#    plt.figure(figsize=(12,4))
#    plt.plot(t,data[:,i])
#    plt.xlabel("t (s)")
#    plt.ylabel("amplitude") 
#    plt.axis([0,0.1,data[:,i].min(),data[:,i].max()])
#    plt.grid()




#########   Frequency domaine visualization before real=>imag transformation ###########   
M=np.mat(np.linspace(0,(n-1)/Fs,num=n))
M=M.transpose()
datacos=np.mat(np.zeros((n,8)))
datasin=np.mat(np.zeros((n,8)))
data2=np.mat(1j*np.zeros((n,8)))

for i in range(8) :
    datacos[:,i]= np.multiply(data[:,i],cos(2*pi*Fc*M)) 
    datasin[:,i]= np.multiply(data[:,i],sin(2*pi*Fc*M))
    data2[:,i]=datacos[:,i]-1j*datasin[:,i]


#print('datacos: {}'.format(datacos))
#print('datasin: {}'.format(datasin))
#print('data2: {}'.format(data2))


###########   Low pass filter    ############# 


mat_filter = scipy.io.loadmat('speech_low_pass_filter.mat')['speech_low_pass_filter']
mat_filter = mat_filter.transpose()
mat_filter = mat_filter.reshape((mat_filter.size,))
data3=np.mat(1j*np.zeros((n,8)))
t=time()
for i in range(8) :
    data3[:,i]=lfilter(mat_filter,1, data2[:,i], axis=0)
temps=time()-t


#yf = fft(data3[:,1])
#yf = yf.reshape((yf.size,))
#xf = np.linspace(-Fs/n,Fs/2,n)
#
#plt.plot(xf, yf)
#plt.grid()
#plt.show()






###########  Delays calculation  ##########

lambda1 = c/Fc
max_score = -1000000
l_theta= 100
l_phi=100
v_theta= np.mat(np.linspace(0,pi,l_theta))
v_phi= np.mat(np.linspace(0,2*pi,l_phi))
theta_max =0
phi_max =0

score_mat = np.mat(np.zeros((l_theta,l_phi)))
N = 500 # nombre d'echantillons utilises
Tau=np.mat(np.zeros((8,1)))
r=0
var=-(1j*2*pi/lambda1)

for itheta in range(l_theta) :
    for iphi in range(l_phi) :
        theta = v_theta[0,itheta]
        phi = v_phi[0,iphi]
        for ii in range(8) :
            Tau[ii] = R*sin(theta)*(cos(phi - (pi/4)*(ii-1)) - cos(phi));
        
        mat_a=np.multiply(var,Tau)
        a = np.power(exp(1),mat_a)
        a = a.H
      
        
        echantillon=data3[3*N:4*N-1,:]
        echantillon=np.multiply(a,echantillon)
        echantillon=abs(echantillon)
        echantillon=echantillon/8
        score =  np.mean(echantillon)
     
        # maximizing the score
        if score>max_score :
            max_score = score
            #print('score_max: {}'.format(max_score)) 
            #print('i_theta: {}'.format(itheta))
            #print('i_phi: {}'.format(iphi))
            theta_max = theta
            phi_max = phi
           

        score_mat[itheta,iphi] = score

############### Radian to degres ###########
theta_max = theta_max*180/pi; 
print('theta_max: {}'.format(theta_max)) 
phi_max = phi_max*180/pi;
print('phi_max: {}'.format(phi_max)) 

