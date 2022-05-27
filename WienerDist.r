dat1 <- RWiener::rwiener(1000, alpha = 2, tau = .3, beta = .5, delta = 1)
dat2 <- RWiener::rwiener(1000, alpha = 2, tau = .3, beta = .5, delta = 2)
plot(dat1)

# A nice video introduce Wiener process: https://www.youtube.com/watch?v=ld0rxwAJpkM

# Simulate a single trial 
library(tidyverse)
# Time
rm(list=ls())

T <- c(1:2000)
w <- data.frame(Time = T, w = NA)

t0 = 0
w0 = 0
cur_w <- data.frame(Time = NA, w = NA, trial = NA)
n_trial <- 10
v_trial <- rnorm(10, 0, 1)

for (jj in 1:length(v_trial)) {
        cur_v <- v_trial[jj]
        for (i in 1:2000){
                cur_w[i, ] < NA
                t <- t0 + T[i]
                w_delta <- rnorm(1, cur_v, 1)
                w_delta <- w_delta
             
                cur_w[i, 'Time'] <- i
                cur_w[i, 'trial'] <- jj
             
                if (i <= 1){
                        cur_w[i, 'w'] <- w0 + w_delta
                } else {
                        cur_w[i, 'w'] <- cur_w$w[i-1] +  w_delta
                }
             
                if (abs(cur_w$w[i]) >= 20){
                        break
                }
        }
}

w %>% tidyr::drop_na() %>% 
        ggplot2::ggplot(., aes(x = Time, y = w)) +
        geom_line() + 
        geom_hline(yintercept=20, linetype="dashed", 
                   color = 'black', size=1) + 
        geom_hline(yintercept=-20, linetype="dashed", 
                   color = 'black', size=1) +
        geom_hline(yintercept=0, # linetype="dashed", 
                   color = 'black', size=1) +
        geom_vline(xintercept=0, # linetype="dashed", 
                   color = 'black', size=1) +
        theme_classic()
