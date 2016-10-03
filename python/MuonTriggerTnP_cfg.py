"""A cmsRun configuration to produce muon tag-and-probe tuples.

The tuples are intended to be used to measure trigger efficiencies.
"""


# Create the process and set up logging
import FWCore.ParameterSet.Config as cms
process = cms.Process('Analysis')

process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True),
    allowUnscheduled = cms.untracked.bool(True)
)

process.p = cms.Path()


# Parse command-line options
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('analysis')

options.register(
    'runOnData', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool,
    'Indicates whether the job processes data or simulation'
)
options.register(
    'triggerProcessName', '', VarParsing.multiplicity.singleton,
    VarParsing.varType.string, 'Name of the process that evaluated trigger decisions'
)

options.setDefault('maxEvents', 100)
options.parseArguments()

if not options.triggerProcessName:
    if options.runOnData:
        options.triggerProcessName = 'HLT'
    else:
        options.triggerProcessName = 'HLT2'


# Set the global tag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag

if options.runOnData:
    process.GlobalTag = GlobalTag(process.GlobalTag, '80X_dataRun2_Prompt_ICHEP16JEC_v0')
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, '80X_mcRun2_asymptotic_2016_miniAODv2_v1')


# Input files for testing
process.source = cms.Source('PoolSource')

if options.runOnData:
    process.source.fileNames = cms.untracked.vstring('/store/data/Run2016D/SingleMuon/MINIAOD/PromptReco-v2/000/276/315/00000/168C3DE5-F444-E611-A012-02163E014230.root')
else:
    process.source.fileNames = cms.untracked.vstring('/store/mc/RunIISpring16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/40000/009BDF9B-FE5C-E611-B71A-0CC47A4D76B6.root')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.maxEvents))


process.triggerFilter = cms.EDFilter('HLTHighLevel',
    HLTPaths = cms.vstring('HLT_IsoMu24_v*', 'HLT_IsoTkMu24_v*'),
    TriggerResultsTag = cms.InputTag('TriggerResults', '', options.triggerProcessName),
    andOr = cms.bool(False),  # at least one of the triggers
    throw = cms.bool(True)
)
process.p += process.triggerFilter

