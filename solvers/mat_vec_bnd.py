"""
Matrix-vector product, including booundary values, for PyNS matrix format.
"""

# Standard Python modules
from pyns.standard import *

# Specific Python modules
import time

# PyNS modules
from pyns.constants import W, E, S, N, B, T
from pyns.operators import cat_x, cat_y, cat_z

# =============================================================================
def mat_vec_bnd(a, phi, gpu=False):
# -----------------------------------------------------------------------------
    """
    Args:
      a:   Object of the type "Matrix", holding the matrix for multiplication.
      phi: Three-dimensional array holding a vector for multiplication.

    Returns:
      r: Result of the matrix-vector product, which is a vector stored
         in a three-dimensional array.
    """

    if gpu:

        import pycuda.driver as cuda
        import pycuda.autoinit
        import pycuda.gpuarray as gpuarray
        from numpy import shape
        from numpy import pad
        
        #start_gpu=time.time()
    
        # initialize and push data to gpu
        a_gpu = a
        phi_gpu = phi

        r_gpu = gpuarray.zeros_like(phi_gpu.val)
        x_gpu = gpuarray.zeros_like(phi_gpu.val)
      
        r_gpu = a_gpu.C * phi_gpu.val
    
        x_gpu[:1,:,:]  = phi_gpu.bnd[W].val[ :1,:,:] 
        x_gpu[1:,:,:]  = phi_gpu.val       [:-1,:,:]
        r_gpu = r_gpu - a_gpu.W * x_gpu

        # print(type(phi_gpu.val[1:,:,:]), type(x_gpu[:-1,:,:]))    
        # print(shape(phi_gpu.val[1:,:,:]), shape(x_gpu[:-1,:,:]))    
        x_gpu[:-1,:,:] = phi_gpu.val[ 1:,:,:]
        x_gpu[-1:,:,:] = phi_gpu.bnd[E].val[ :1,:,:]
        r_gpu = r_gpu - a_gpu.E * x_gpu
    
        x_gpu[:,:1,:]  = phi_gpu.bnd[S].val[:, :1,:] 
        x_gpu[:,1:,:]  = phi_gpu.val[:,:-1,:]
        r_gpu = r_gpu - a_gpu.S * x_gpu
        
        x_gpu[:,:-1,:] = phi_gpu.val[:, 1:,:] 
        x_gpu[:,-1:,:] = phi_gpu.bnd[N].val[:, :1,:]
        r_gpu = r_gpu - a_gpu.N * x_gpu
        
        x_gpu[:,:,:1]  = phi_gpu.bnd[B].val[:,:, :1]
        x_gpu[:,:,1:]  = phi_gpu.val[:,:,:-1]
        r_gpu = r_gpu - a_gpu.B * x_gpu
    
        x_gpu[:,:,:-1] = phi_gpu.val[:,:, 1:] 
        x_gpu[:,:,-1:] = phi_gpu.bnd[T].val[:,:, :1]
        r_gpu = r_gpu - a_gpu.T * x_gpu
    
        #stop_gpu=time.time()
        #print("GPU time: %2.3e s" %(stop_gpu-start_gpu))
       
        #print("from mat_vec_bnd.py gpu: ")
        #print(gpuarray.dot(r_gpu,r_gpu))
        return r_gpu
   
   
    phi.exchange()
    
    #start_cpu = time.time()

    r = zeros(phi.val.shape)
    
    r[:]  = a.C[:] * phi.val[:]

    r[:] -= a.W[:] * cat_x( (phi.bnd[W].val[ :1,:,:], 
                             phi.val       [:-1,:,:]) )

    r[:] -= a.E[:] * cat_x( (phi.val       [ 1:,:,:], 
                             phi.bnd[E].val[ :1,:,:]) )
    
    r[:] -= a.S[:] * cat_y( (phi.bnd[S].val[:, :1,:], 
                             phi.val       [:,:-1,:]) )

    r[:] -= a.N[:] * cat_y( (phi.val       [:, 1:,:], 
                             phi.bnd[N].val[:, :1,:]) )
    
    r[:] -= a.B[:] * cat_z( (phi.bnd[B].val[:,:, :1], 
                             phi.val       [:,:,:-1]) )

    r[:] -= a.T[:] * cat_z( (phi.val       [:,:, 1:], 
                             phi.bnd[T].val[:,:, :1]) )

    # import numpy as np
    # print("from mat_vec_bnd.py cpu: ")
    # print(np.sum(np.sum(np.sum(np.multiply(r,r)))))

    #stop_cpu=time.time()
    #print("CPU time: %2.3e s" %(stop_cpu-start_cpu))
        
    return r  # end of function
