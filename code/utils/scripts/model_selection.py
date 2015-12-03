from __future__ import absolute_import, division, print_function
import numpy as np
import numpy.linalg as npl
import matplotlib.pyplot as plt
import nibabel as nib
import pandas as pd # new
import sys # instead of os
import scipy.stats
from scipy.stats import gamma
import os
import scipy.stats as stats

# Relative path to subject 1 data

project_path          = "../../../"
path_to_data          = project_path+"data/ds009/"
location_of_images    = project_path+"images/"
location_of_functions = project_path+"code/utils/functions/" 
final_data            = "../../../final/data/"
smooth_data           =  final_data + 'smooth/'
hrf_data              = final_data + 'hrf/'
behav_suffix           = "/behav/task001_run001/behavdata.txt"


sys.path.append(location_of_functions)

sub_list = os.listdir(path_to_data)[1:]

from event_related_fMRI_functions import hrf_single, np_convolve_30_cuts
from time_shift import time_shift, make_shift_matrix, time_correct
from glm import glm_multiple, glm_diagnostics
from noise_correction import mean_underlying_noise, fourier_predict_underlying_noise,fourier_creation
from hypothesis import t_stat_mult_regression, t_stat
from Image_Visualizing import present_3d, make_mask
from mask_phase_2_dimension_change import masking_reshape_start, masking_reshape_end


################
# Adjusted R^2 #
################

def adjR2(MRSS,y_1d,df):
	n=y_1d.shape[0]
	RSS= MRSS*df
	TSS= np.sum((y_1d-np.mean(y_1d))**2)
	adjR2 = 1- ((RSS/TSS)  * (df/(n-1))  )

	return adjR2


#LOAD THE DATA In
i = 'sub001'
img = nib.load(smooth_data+ i +"_bold_smoothed.nii")
data = img.get_data() 

behav=pd.read_table(path_to_data+i+behav_suffix,sep=" ")
num_TR = float(behav["NumTRs"])
    

#CREATE THE CONVOLVE STUFF
cond1=np.loadtxt(path_to_data+ i+ "/model/model001/onsets/task001_run001/cond001.txt")
cond2=np.loadtxt(path_to_data+ i+ "/model/model001/onsets/task001_run001/cond002.txt")
cond3=np.loadtxt(path_to_data+ i+ "/model/model001/onsets/task001_run001/cond003.txt")
    
TR = 2
tr_times = np.arange(0, 30, TR)
hrf_at_trs = np.array([hrf_single(x) for x in tr_times])

# creating the .txt file for the events2neural function
cond_all=np.row_stack((cond1,cond2,cond3))
cond_all=sorted(cond_all,key= lambda x:x[0])

cond_all=np.array(cond_all)[:,0]
    
delta_y=2*(np.arange(34))/34


shifted=make_shift_matrix(cond_all,delta_y)
    
def make_convolve_lambda(hrf_function,TR,num_TRs):
    convolve_lambda=lambda x: np_convolve_30_cuts(x,np.ones(x.shape[0]),hrf_function,TR,np.linspace(0,(num_TRs-1)*TR,num_TRs),15)[0]
        
    return convolve_lambda
        
convolve_lambda=make_convolve_lambda(hrf_single,TR,num_TR)
    
convolve=time_correct(convolve_lambda,shifted,num_TR)   
n_vols = data.shape[-1]    
    

mask = nib.load(path_to_data+i+'/anatomy/inplane001_brain_mask.nii.gz')
mask_data = mask.get_data()
mask_data = make_mask(np.ones(data.shape[:-1]), mask_data, fit=True)
mask_data = mask_data!=0
mask_data = mask_data.astype(int)

###PCA SHIT###

to_2d= masking_reshape_start(data,mask)
# double_centered_2d
X_pca= to_2d - np.mean(to_2d,0) - np.mean(to_2d,1)[:,None]

cov = X_pca.T.dot(X_pca)

U, S, V = npl.svd(cov)
pca_addition= U[:,:6] # ~40% coverage



model1=[]
model2=[]
model3=[]
model4=[]
model5=[]
model6=[]
model7=[]
model8=[]
model9=[]
model10=[]

#START DOING GLM
for j in range(data.shape[2]):
    
    data_slice = data[:,:,j,:]
    mask_slice = mask_data[:,:,j]
    data_slice = data_slice.reshape((-1,239))
    mask_slice = np.ravel(mask_slice)
    
    data_slice = data_slice[mask_slice==1]
    
    X = np.ones((n_vols,13))
    X[:,1] = convolve[:,j] # 1 more
    X[:,2] = np.linspace(-1,1,num=X.shape[0]) #drift # one 
    X[:,3:7] = fourier_creation(X.shape[0],2)[:,1:] # four more
    X[:,7:] = pca_addition
    

#START CREATING MODELS

    ###################
    #   MODEL 1       #
    ###################
    # 1.1 hrf (simple)

    beta1,t,df1,p = t_stat_mult_regression(data_slice, X[:,0:2])
                
    MRSS1, fitted, residuals = glm_diagnostics(beta1, X[:,0:2], data_slice)
    
    adj1_slice = np.zeros(len(MRSS1))
    count = 0
    
    for value in MRSS1:
        adj1_slice[count] = adjR2(value, np.array(data_slice[count,:]) ,df1)  
        count+=1
    
    model1=model1+adj1_slice.tolist()
    
    ###################
    #   MODEL 2       #
    ###################

    # 1.2 hrf + drift
    
    beta2,t,df2,p = t_stat_mult_regression(data_slice, X[:,0:3])
                
    MRSS2, fitted, residuals = glm_diagnostics(beta2, X[:,0:3], data_slice)
    
    adj2_slice = np.zeros(len(MRSS2))
    count = 0
    
    for value in MRSS2:
        adj2_slice[count] = adjR2(value, np.array(data_slice[count,:]) ,df2)  
        count+=1
    
    model2=model2+adj2_slice.tolist()
    
    ###################
    #   MODEL 3       #
    ###################
    
    # 1.3 hrf + drift + fourier

    beta3,t,df3,p = t_stat_mult_regression(data_slice, X[:,0:7])
                
    MRSS3, fitted, residuals = glm_diagnostics(beta3, X[:,0:7], data_slice)
    
    adj3_slice = np.zeros(len(MRSS3))
    count = 0
    
    for value in MRSS3:
        adj3_slice[count] = adjR2(value, np.array(data_slice[count,:]) ,df3)  
        count+=1
    
    model3=model3+adj3_slice.tolist()
    
    ###################
    #   MODEL 4       #
    ###################
    
    # 1.4 hrf + drift + pca

    beta4,t,df4,p = t_stat_mult_regression(data_slice, X[:,[0,1,2,7,8,9,10,11,12]])
                
    MRSS4, fitted, residuals = glm_diagnostics(beta4, X[:,[0,1,2,7,8,9,10,11,12]], data_slice)
    
    adj4_slice = np.zeros(len(MRSS4))
    count = 0
    
    for value in MRSS4:
        adj4_slice[count] = adjR2(value, np.array(data_slice[count,:]) ,df4)  
        count+=1
    
    model4=model4+adj4_slice.tolist()
    
    ###################
    #   MODEL 5       #
    ###################
    
    # 1.5 hrf + drift + pca + fourier
    
    beta5,t,df5,p = t_stat_mult_regression(data_slice, X)
                
    MRSS5, fitted, residuals = glm_diagnostics(beta5, X, data_slice)
    
    adj5_slice = np.zeros(len(MRSS5))
    count = 0
    
    for value in MRSS5:
        adj5_slice[count] = adjR2(value, np.array(data_slice[count,:]) ,df5)  
        count+=1
    
    model5=model5+adj5_slice.tolist()
    
    # ###################
    # #   MODEL 6       #
    # ###################
    #
    # beta6,t,df6,p = t_stat_mult_regression(data_slice, X)
    #
    # MRSS6, fitted, residuals = glm_diagnostics(beta6, X, data_slice)
    #
    # adj6_slice = np.zeros(len(MRSS6))
    # count = 0
    #
    # for value in MRSS6:
    #     adj6_slice[count] = adjR2(value, np.array(data_slice[count,:]) ,df6)
    #     count+=1
    #
    # model6=model6+adj6_slice.tolist()
    #
    # ###################
    # #   MODEL 7       #
    # ###################
    #
    # beta7,t,df7,p = t_stat_mult_regression(data_slice, X)
    #
    # MRSS7, fitted, residuals = glm_diagnostics(beta7, X, data_slice)
    #
    # adj7_slice = np.zeros(len(MRSS7))
    # count = 0
    #
    # for value in MRSS7:
    #     adj7_slice[count] = adjR2(value, np.array(data_slice[count,:]) ,df7)
    #     count+=1
    #
    # model7=model7+adj7_slice.tolist()
    #

###################
# Desired Models: #
###################

### subcategory 1:
# with only cond_all hrf run

# 1.1 hrf (simple)
# 1.2 hrf + drift
# 1.3 hrf + drift + fourier
# 1.4 hrf + drift + pca
# 1.5 hrf + drift + pca + fourier




### subcategory 1:
# with all 3 different hrfs for each type of condition

# 2.1 hrf
# 2.2 hrf + drift
# 2.3 hrf + drift + fourier
# 2.4 hrf + drift + pca
# 2.5 hrf + drift + pca + fourier



# need to correct fourier in noise correction function file