# Production of tag-and-probe tuples

This is a simple [CMSSW](https://github.com/cms-sw/cmssw) package to produce [ROOT](http://root.cern.ch) tuples with tag-probe pairs, which are intended to measure efficiencies of lepton identification and triggers.
The package is kept simple and minimalistic, and as such is supposed to be clearer then central packages for [electrons](https://twiki.cern.ch/twiki/bin/view/CMSPublic/ElectronTagAndProbe) and [muons](https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonTagAndProbe).


## Installation

This package exploits some classes from the central electron tag-and-probe package and thus needs to be installed on top of it.
Commands for installation:
```bash
cmsrel CMSSW_8_0_10
cd CMSSW_8_0_10/src
cmsenv
git cms-init
git cms-merge-topic fcouderc:tnp_egm_80X

mkdir Analysis
cd Analysis
git clone git@github.com:andrey-popov/tag-and-probe-tuples.git TagAndProbe
cd ..

scram b -j 8
```
The last commit in the branch `tnp-egm_80X` is [cf0ffb](https://github.com/fcouderc/cmssw/tree/cf0ffb668fb97048aff5e6016f7589fa75844726/PhysicsTools/TagAndProbe).
