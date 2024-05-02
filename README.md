Quick bit of code to give quick and dirty CBC cell type counts by counting pixels in the scatterplot.

The Sysmex machine will not report actual numbers for cell type counts or cell type percentages if the concentration
of cells in the sample is too low. At low concentrations, the sampling error becomes large (and what's going on 
with your patient's blood in this case anyway???) This was the right decision, clinically...

However, __for research use only__, we want to get quick and dirty estimations of the diff percents on minute and 
diluted samples. No, we aren't Theranos LOL, this is *for resesarch use only*!!!! Fortunately, the Sysmex machine 
produces various scatterplots, no matter how few cells there were. We can get a *quick* and *dirty* estimation of the
numbers of cells of each type by counting pixels of various colors. The script reports numbers of pixels, roughly [1], 
rather than percentages; we know that when the numbers of pixels are on the small side, the sampling error can become
rather large.

Yes, Elizabeth, there is such a thing as sampling error. No basing clinical decisions on this.

[1] Each brightly-colored pixel is given more weight than a normal-colored pixel. We don't know just how much 
overplotting the brightly-colored pixels represent. The current script has these weighted at 2X, but this is a
parameter that's settable in the code.
