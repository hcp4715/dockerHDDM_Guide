# Wiener First Passage Time
# This was from Narravo & Fuss (2009)

def wfpt(t, v, a, z, err):
    import math
    import numpy as np

    tt = t/(a**2)   # use normalized time
    w = z/a         # convert to relative start point

    # calculate number of terms needed for large t
    if math.pi * tt * err < 1:  #  if error threshold is set low enough
        kl = math.sqrt(-2 * math.log(math.pi * tt * err)/(math.pi ** 2 * tt)) # bound
        kl = max(kl, 1/(math.pi * math.sqrt(tt))) # ensure boundary conditions met
    else:                                # if error threshold set too high
        kl=1/(math.pi * math.sqrt(tt))  # set to boundary condition

    # calculate number of terms needed for small t
    if 2 * math.sqrt(2*math.pi*tt)*err < 1: # if error threshold is set low enough
        ks = 2 + math.sqrt(-2 * np.multiply( tt, math.log(2 * math.sqrt(2 * math.pi *tt) *err)))  # bound
        ks = max(ks, math.sqrt(tt) + 1)  # ensure boundary conditions are met
    else:      #  if error threshold was set too high
        ks = 2   #  Minimal kappa for that case

    # compute f(tt|0,1,w)
    p = 0 # initialize density
    if ks < kl: # small t is better...
        K = math.ceil(ks) # round to smallest integer meeting error
    
        for k in range(-math.floor((K-1)/2), math.ceil((K-1)/2), 1):     # loop over k
            p = p+(w+2*k) * math.exp(-((w+2*k)**2)/2/tt)      # increment sum
    
        p = p/math.sqrt(2*math.pi*tt**3) # add constant term

    else: # if large t is better...
        K = math.ceil(kl) # round to smallest integer meeting error
        for k in range(0, K, 1):
            p = p+k*math.exp(-(k**2)*(math.pi**2)*tt/2)*math.sin(k*math.pi*w) # increment sum
        
        p=p*math.pi # add constant term

    # convert to f(t|v,a,w)
    p = p*math.exp(-v * a * w -(v**2) * t/2)/(a**2)
    return p


v = 1.0
a = 2.0 
z = .5

err = 0.0001

#import numpy as np
#mu, sigma = 2, 0.5
#t = np.random.normal(mu, sigma, 1000)
t = 1.5
p = wfpt(t, v, a, z, err)