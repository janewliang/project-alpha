"""
Parameter selection for Benjamini Hochberg Analysis and T analysis.

"""

from __future__ import absolute_import, division, print_function
import numpy as np
import matplotlib.pyplot as plt
import sys
import itertools
import nibabel as nib
import os


name="sub001"

#set up paths
project_path          = "../../"
path_to_data          = project_path+"data/ds009/"+name
location_of_images    = project_path+"images/"
location_of_functions = project_path+"code/utils/functions/" 
final_data            = "../data/"
behav_suffix           = "/behav/task001_run001/behavdata.txt"
smooth_data           =  final_data + 'smooth/'
hrf_data              = final_data + 'hrf/'


sys.path.append(location_of_functions)

#Import functions
from tgrouping import t_grouping_neighbor
from mask_phase_2_dimension_change import masking_reshape_end, neighbor_smoothing_binary
from Image_Visualizing import make_mask
from benjamini_hochberg import bh_procedure


#load data from regression

p_3d = np.load("../data/p-values/"+name+"_pvalue.npy")
t_3d = np.load("../data/t_stat/"+name+"_tstat.npy")
beta_3d = np.load("../data/betas/"+name+"_beta.npy")

#create mask
mask = nib.load(path_to_data + '/anatomy/inplane001_brain_mask.nii.gz')
mask_data = mask.get_data()
rachels_ones = np.ones((64, 64, 34))
fitted_mask = make_mask(rachels_ones, mask_data, fit = True)
fitted_mask[fitted_mask>0]=1


#set up parameters to test
q1         = [.3,.25,.2,.15,.1]
neighbors1 = [1,3,5,12,20]
prod2      = [.25,.2,.15,.1,.05]
neighbors2 = [1,3,5,12,20]
prod3      = [.25,.2,.15,.1,.05]
neighbors3 = [1,3,5,12,20]



mask = fitted_mask
mask_1d = np.ravel(mask)


p_1d = np.ravel(p_3d)
p_bh = p_1d[mask_1d==1]


sys.stdout.write("*-----------------------------------------------* \n")
sys.stdout.write("Running different Clustering Tasks on "+ name + "\n more than needed for visuals: \n")

###############################
# Benjamini Hochberg Analysis #
###############################

toolbar_width=len(q1)
sys.stdout.write("Benjamini Hochberg: ")
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['
    


bh=[] # values a*6 + b - 1
count_a=0
for a,b in itertools.product(range(len(q1)),range(5)):
	bh_first = bh_procedure(p_bh,q1[a])
	bh_3d    = masking_reshape_end(bh_first,mask,off_value=.5)
	bh_3d[bh_3d<.5]=0

	

	bh_3d_1_good = 1-bh_3d	
	first  = neighbor_smoothing_binary(bh_3d_1_good,neighbors1[b])

	bh.append(first)


	if count_a==a and b==4:
		sys.stdout.write("-")
		sys.stdout.flush()
		count_a+=1
	

sys.stdout.write("\n")


#------------------#
# Image comparison #
#------------------#


present_bh = np.ones((len(q1)*64,5*64))
behind= np.ones((len(q1)*64,5*64))

behind_p=masking_reshape_end(p_bh,mask,off_value=.5)

for a,b in itertools.product(range(len(q1)),range(5)):
	present_bh[(a*64):((a+1)*64),(b*64):((b+1)*64)]= bh[a*5+b][...,15]
	behind[(a*64):((a+1)*64),(b*64):((b+1)*64)]=behind_p[...,15]
present_bh[present_bh<.5]=0



plt.contour(present_bh,interpolation="nearest",colors="k",alpha=1)
plt.imshow(behind,interpolation="nearest",cmap="Blues_r")
plt.title("Benjamini Hochberg on slice 15 and contours *"+name+"* \n (with varying Q and # neighbors)")
x=32+64*np.arange(5)
labels = neighbors1
plt.xticks(x, labels)
plt.clim(0,np.max(abs(behind)))
plt.xlabel("Number of Neighbors")
labels2 = q1
y=32+64*np.arange(len(q1))
plt.yticks(y, labels2)
plt.ylabel("Q")
plt.colorbar()
plt.savefig(location_of_images+name+"_"+"bh_compare_15_plus_contours.png")
plt.close()


plt.imshow(present_bh,interpolation="nearest",cmap="bwr")
plt.title("Benjamini Hochberg on slice 15 *"+name+"* \n (with varying Q and # neighbors)")
x=32+64*np.arange(5)
labels = neighbors1
plt.xticks(x, labels)
plt.xlabel("Number of Neighbors")
labels2 = q1

y=32+64*np.arange(len(q1))
plt.yticks(y, labels2)
plt.ylabel("Q")
plt.savefig(location_of_images+name+"_"+"bh_compare_15.png")
plt.close()

##############
# T Analysis #
##############

toolbar_width=len(prod2)
sys.stdout.write("T - Analysis:       ")
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['
    




t_val=[] #values c*5 + d - 1
count_c=0
for c,d in itertools.product(range(5),range(5)):
	second=t_grouping_neighbor(t_3d, mask, prod2[c], neighbors= neighbors2[d],
					prop=True,abs_on=True, binary=True ,off_value=0,masked_value=.5)[0]
	t_val.append(second)

	if count_c==c and d==4:
		sys.stdout.write("-")
		sys.stdout.flush()
		count_c+=1
sys.stdout.write("\n")


#------------------#
# Image comparison #
#------------------#


present_t = np.ones((5*64,5*64))
behind2= np.ones((5*64,5*64))
behind_t=t_3d*mask

for c,d in itertools.product(range(5),range(5)):
	present_t[(c*64):((c+1)*64),(d*64):((d+1)*64)]= t_val[c*5+d][...,15]
	behind2[(c*64):((c+1)*64),(d*64):((d+1)*64)]=behind_t[...,15]


#---------------------#
#   T-analysis Plot   #
#---------------------#

plt.contour(present_t,interpolation="nearest",colors="k",alpha=1)
plt.imshow(behind2,interpolation="nearest",cmap="seismic")
plt.clim(-4.2,4.2)
plt.colorbar()
plt.title("T- Analysis on slice 15 and contours *"+name+"* \n (with varying proportions and # neighbors)")
x=32+64*np.arange(5)
labels = neighbors2
plt.xticks(x, labels)
plt.xlabel("Number of Neighbors")
labels2 = prod2 
plt.clim(-np.max(abs(behind2)),np.max(abs(behind2)))
plt.yticks(x, labels2)
plt.ylabel("Proportion")
plt.savefig(location_of_images+name+"_"+"t_compare_15_plus_contours.png")
plt.close()

#---------------------------------------#
#   Absolute value of T-analysis Plot   #
#---------------------------------------#
plt.contour(present_t,interpolation="nearest",colors="k",alpha=1)
plt.imshow(np.abs(behind2),interpolation="nearest",cmap="Blues")
plt.clim(0,np.max(abs(behind)))
plt.colorbar()
plt.title(name+", slice 15: abs(T-statistic) and contours \n (with varying proportions and # neighbors)")
x=32+64*np.arange(5)
labels = neighbors2
plt.xticks(x, labels)
plt.xlabel("Number of Neighbors")
labels2 = prod2 
plt.yticks(x, labels2)
plt.ylabel("Proportion")
plt.savefig(location_of_images+name+"_"+"t_compare_15_abs_plus_contours.png")
plt.close()




plt.imshow(present_t,interpolation="nearest",cmap="bwr")
plt.title("T- Analysis on slice 15 *"+name+"* \n (with varying proportions and # neighbors)")
x=32+64*np.arange(5)
labels = neighbors2
plt.xticks(x, labels)
plt.xlabel("Number of Neighbors")
labels2 = prod2 
plt.yticks(x, labels2)
plt.ylabel("Proportion")
plt.savefig(location_of_images+name+"_"+"t_compare_15.png")
plt.close()



#################
# Beta Analysis #
#################


toolbar_width=len(prod2)
sys.stdout.write("Beta - Analysis:    ")
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['
    



beta_val=[] # values e*5 + f -1
count_e=0
for e,f in itertools.product(range(5),range(5)):
	third=t_grouping_neighbor(beta_3d, mask, prod3[e], neighbors= neighbors3[f],
						prop=True,abs_on=True, binary=True ,off_value=0,masked_value=.5)[0]
	beta_val.append(third)

	if count_e==e and f==4:
		sys.stdout.write("-")
		sys.stdout.flush()
		count_e+=1
sys.stdout.write("\n")


#------------------#
# Image comparison #
#------------------#

present_beta = np.ones((5*64,5*64))
behind3= np.ones((5*64,5*64))
behind_beta=beta_3d*mask

for e,f in itertools.product(range(5),range(5)):
	present_beta[(e*64):((e+1)*64),(f*64):((f+1)*64)]= beta_val[e*5+f][...,15]
	behind3[(e*64):((e+1)*64),(f*64):((f+1)*64)]=behind_beta[...,15]


#------------------------#
#     Beta-value Plot    #
#------------------------#

plt.contour(present_beta,interpolation="nearest",colors="k",alpha=1)
plt.imshow(behind3,interpolation="nearest",cmap="seismic")
plt.clim(-np.max(abs(behind3)),np.max(abs(behind3)))
plt.title("Beta- Analysis on slice 15 and contours *"+name+"* \n (with varying proportions and # neighbors)")
plt.colorbar()
x=32+64*np.arange(5)
labels = neighbors3
plt.xticks(x, labels)
plt.xlabel("Number of Neighbors")
labels2 = prod3 
plt.yticks(x, labels2)
plt.ylabel("Proportion")
plt.savefig(location_of_images+name+"_"+"beta_compare_15_plus_contours.png")
plt.close()

#---------------------------------------#
#   Absolute value of beta-value Plot   #
#---------------------------------------#
plt.contour(present_beta,interpolation="nearest",colors="k",alpha=1)
plt.imshow(np.abs(behind3),interpolation="nearest",cmap="Blues")
plt.title("abs(Beta- values) on slice 15 and contours *"+name+"* \n (with varying proportions and # neighbors)")
plt.colorbar()
plt.clim(0,np.max(abs(behind3)))
x=32+64*np.arange(5)
labels = neighbors3
plt.xticks(x, labels)
plt.xlabel("Number of Neighbors")
labels2 = prod3 
plt.yticks(x, labels2)
plt.ylabel("Proportion")
plt.savefig(location_of_images+name+"_"+"beta_compare_15_abs_plus_contours.png")
plt.close()




plt.imshow(present_beta,interpolation="nearest",cmap="bwr")
plt.title("Beta- Analysis on slice 15 *"+name+"* \n (with varying proportions and # neighbors)")
plt.colorbar()
x=32+64*np.arange(5)
labels = neighbors3
plt.xticks(x, labels)
plt.xlabel("Number of Neighbors")
labels2 = prod3 
plt.yticks(x, labels2)
plt.ylabel("Proportion")
plt.savefig(location_of_images+name+"_"+"beta_compare_15.png")
plt.close()



