# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 10:59:15 2022

@author: Ame
"""

from pathlib import Path
from pprint import pprint

import oimodeler as oim

def main():

    # NOTE: Path to a fake MATISSE-L-band binary observation (3 oifits) created with ASPRO
    #path = Path(__file__).parent.parent.parent
    path = Path(__file__).parent.parent.parent
    data_dir = path / "data" / "ASPRO_MATISSE2"

    # NOTE: Change this path if you want to save the products at another location
    save_dir = path / "images"
    if not save_dir.exists():
        save_dir.mkdir(parents=True)

    files = list(data_dir.glob("*.fits"))

    # NOTE: Building a oimodeler model with the same parameters
    ud = oim.oimUD(d=3, f=0.5)
    pt = oim.oimPt(f=1)
    model = oim.oimModel([ud, pt])

    # NOTE: Setting limits of the parameter space but also setting x,y of the UD as a
    # free parameters and f of the pt as fixed (to 1)
    ud.params["d"].set(min=0.01, max=20)
    ud.params["x"].set(min=-50, max=50, free=True)
    ud.params["y"].set(min=-50, max=50, free=True)
    ud.params["f"].set(min=0.0, max=10.0)
    pt.params["f"].free = False
    pprint(model.getFreeParameters())

    fit = oim.oimFitterEmcee(files, model, nwalkers=64)
    
    prepkwargs = {
        "init": "random",
    }
    runkwargs = {
        "progress": True,
    }
    oim.runMultiEmcee(fit, 2000, prepkwargs = prepkwargs, runkwargs = runkwargs)

    # NOTE: Get results from the fit (updates the class internal logic)
    median, err_l, err_u, err = fit.getResults(
        mode="median", discard=1000, chi2limfact=20
    )

    # %%
    sampler = fit.sampler
    chain = fit.sampler.chain
    lnprob = fit.sampler.lnprobability

    # %%
    class_name = fit.__class__.__name__
    class_name = class_name[0].upper() + class_name[1:]
    figWalkers, axeWalkers = fit.walkersPlot(
        cmap="plasma_r", savefig=save_dir / f"example{class_name}Walkers.png"
    )
    figCorner, axeCorner = fit.cornerPlot(
        discard=1000, savefig=save_dir / f"example{class_name}Corner.png"
    )

    # %%
    fig0, ax0 = fit.simulator.plot(
        ["VIS2DATA", "VISAMP", "VISPHI", "T3AMP", "T3PHI"],
        savefig=save_dir / f"Example{class_name}_fittedData.png",
    )

if __name__ == "__main__":
    main()
