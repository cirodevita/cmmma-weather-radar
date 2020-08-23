# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 12:06:01 2014

@author: Vincenzo
"""
import numpy as np
from scipy import signal


def StatisticalFilter(Mappe, Etn_Th, Txt_Th, Z_Th):
    Ny = len(Mappe[1, :, 1])
    Nx = len(Mappe[1, 1, :])
    Nt = len(Mappe[:, 1, 1])

    min_val = np.nanmin(Mappe)

    Map_filt = np.ones([Nt, Ny, Nx])
    Map_filt[:, :, :] = min_val
    ind32 = np.where(Mappe[:, :, :] > min_val) and np.where(Mappe[:, :, :] < -30.0)
    Map_filt[ind32] = min_val
    Map_filt1_bool = np.zeros([Ny, Nx])
    Th = 5.0
    Map_final = np.empty((Nt, Ny, Nx))

    for k in range(Nt):
        Map = Mappe[k, :, :]
        ind1 = np.where(Map > Th)
        # ind0=np.where(Map<=Th)
        Map_filt1_bool[ind1] = 1.0
        vector = np.concatenate(Map_filt1_bool)
        Et = f_entropy(vector)
        Htx = f_texture(Map, min_val)
        ind = np.where(Htx > Txt_Th)
        NH = len(ind[0]) / float(Nx * Ny) * 100.0
        if Et > Etn_Th and NH <= 70.0:
            Map_filt = f_Median_declutter(Map, Th)
            Htx = f_texture(Map_filt, min_val)
            ind = np.where(Htx[:, :] > Txt_Th)
            Map_filt[ind] = min_val
            ind = np.where(Map_filt > 70.0)
            Map_filt[ind] = min_val
            Map_filt = f_Median_declutter(Map_filt, Th)
            ind = np.where(Map_filt <= Z_Th)
            Map_filt[ind] = min_val
            Map_final[k, :, :] = Map_filt
    return Map_final


def f_entropy(x):
    minimum = np.nanmin(x)
    if minimum < 0:
        histogram = np.histogram(x - minimum)
    else:
        histogram = np.histogram(x)
        rows = np.size(x)
        # trovo primo elemento diverso da zero
        # index=np.where(histogram>0)
        P = histogram[0][0] / float(rows)
        H = -P * np.log2(P);
    return H


def f_texture(Map, min_val):
    Text = np.zeros((len(Map[:, 0]), len(Map[0, :])))
    Sum_weight = np.zeros((len(Map[:, 0]), len(Map[0, :])))
    Weight = np.ones((len(Map[:, 0]), len(Map[0, :])))
    ind_nan = np.isnan(Map[:, :])
    Weight[ind_nan] = 0.0  
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i * i + j * j > 0:
                parz = np.roll(Weight, i, axis=0)
                parz = np.roll(parz, j, axis=1)
                parz2 = np.roll(Map, i, axis=0)
                parz2 = np.roll(parz2, j, axis=1)
                Text = Text + Weight * parz * (parz2 - Map) ** 2
                parz3 = np.roll(Weight, i, axis=0)
                parz3 = np.roll(parz3, j, axis=1)
                Sum_weight = Sum_weight + (Weight * parz3)
    ngood = np.where(Sum_weight >= 3.0)
    Text[ngood] = np.divide(np.sqrt(Text[ngood]), Sum_weight[ngood])
    indflag = np.where(Sum_weight < 3.0)
    Text[indflag] = min_val  # flag
    return Text


def f_Median_declutter(Map, Th):
    minVal = np.nanmin(Map)
    ind32 = np.where(Map[:, :] > minVal) and np.where(Map[:, :] < -30.0)
    Maschera = np.copy(Map) 
    Ny = len(Map[:, 1])
    Nx = len(Map[1, :])
    indTh0 = np.where(Map <= Th)  # Maschera
    indTh1 = np.where(Map > Th)  # Maschera
    Maschera[indTh0] = 0.0
    Maschera[indTh1] = 1.0
    if len(indTh0[0]) < (Nx * Ny):
        Maschera = signal.medfilt2d(Maschera, 3)  # 3*3

    Mappa1 = Map * Maschera
    index0 = np.where(Maschera[:, :] == 0.0)
    Mappa1[index0] = minVal
    Mappa1[ind32] = minVal
    return Mappa1
