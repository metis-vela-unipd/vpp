"""
File dove raccogliere tutte le funzioni utilizzate più di una volta nel codice per
facilitarne la modifica
"""
import xfoil
import numpy as np
from scipy.interpolate import interp2d

def lift_coefficients_2D(Foil, angleOfAttack, boatSpeed, Sea):
    """
    Il modo per usare xfoil è il seguente:
    - Salvo le coordinate del profilo in due vettori numpy x,y
    - profilo = xfoil.model.Airfoil(x,y)
    - xf = xfoil.XFoil()
    - xf.airfoil = profilo
    - xf.repanel()
    - xf.Re = xxx
    - xf.n_crit = 3
    - cl, cd, cm, cp = xf.a()
    """
    # calcolo del coefficiente di lift e drag 2D:
    cllist = []
    cdlist = []
    wortmann = xfoil.model.Airfoil(x,y)
    xf = xfoil.XFoil()
    xf.airfoil = wortmann
    xf.repanel()
    for v in boatSpeed:
        xf.Re = v * Foil.chord / Sea.cinematicViscosity
        xf.n_crit = 3
        xf.max_iter = 40
        cl, cd, _, __ = xf.a(angleOfAttack)
        cllist.append(cl)
        cdlist.append(cd)
    return np.array(cllist), np.array(cdlist)

def lift_coefficients_3D(cl, cd, aspectRatio):
    cl3D = cl / (1 + 2 / aspectRatio)

    cDind = cl3D **2 / (np.pi * aspectRatio)
    cDtot = cd + cDind
    return cl3D, cDtot

def dynamic_pressure(Sea, boatSpeed):
    return 0.5 * Sea.waterDensity * boatSpeed**2

def interpolate_wing_coefficients(xf):
    Re = np.arange(1e4, 1e7, 1e6)
    alfa = np.arange(0, 5, 1)
    clalfa = []
    clre = []
    cdalfa = []
    cdre = []

    for R in Re:
        xf.Re = R
        for a in alfa:
            cl, cd, cm, cp = xf.a(a)
            clalfa.append(cl)
            cdalfa.append(cd)
        clre.append(clalfa)
        cdre.append(cdalfa)
        clalfa = []
        cdalfa = []

    x = alfa
    y = Re
    zlift = clre
    zdrag = cdre
    # Togli i nan values dalle liste che mi sfanculano l'interpolazione
    zlift = np.nan_to_num(zlift)
    zdrag = np.nan_to_num(zdrag)
    clFunction = interp2d(x,y,zlift)
    cdFunction = interp2d(x,y,zdrag)
    return clFunction, cdFunction
