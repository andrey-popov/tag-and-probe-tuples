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
    # process.source.fileNames = cms.untracked.vstring('/store/mc/RunIISpring16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/40000/009BDF9B-FE5C-E611-B71A-0CC47A4D76B6.root')
    process.source.fileNames = cms.untracked.vstring('file:DY.root')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.maxEvents))


# Trigger selection
process.triggerFilter = cms.EDFilter('HLTHighLevel',
    HLTPaths = cms.vstring('HLT_IsoMu24_v*', 'HLT_IsoTkMu24_v*'),
    TriggerResultsTag = cms.InputTag('TriggerResults', '', options.triggerProcessName),
    andOr = cms.bool(False),  # at least one of the triggers
    throw = cms.bool(True)
)
process.p += process.triggerFilter


# Create collection of good muons and select events with exactly two
# such muons.  They will be used as probes.
process.pvFilter = cms.EDFilter('PrimaryVertexObjectFilter',
    src = cms.InputTag('offlineSlimmedPrimaryVertices'),
    filterParams = cms.PSet(
        minNdof = cms.double(4.),
        maxZ = cms.double(24.),
        maxRho = cms.double(2.)
    )
)
process.goodMuons = cms.EDFilter('MuonSelectorWithID',
    src = cms.InputTag('slimmedMuons'),
    cut = cms.string('pt > 20. & abs(eta) < 2.4'),
    maxRelIso = cms.double(0.15),
    passID = cms.string('tight'),
    primaryVertices = cms.InputTag('offlineSlimmedPrimaryVertices')
)
process.countGoodMuons = cms.EDFilter('PATCandViewCountFilter',
    src = cms.InputTag('goodMuons'),
    minNumber = cms.uint32(2),
    maxNumber = cms.uint32(2)
)
process.p += process.pvFilter + process.goodMuons + process.countGoodMuons


# Define probes and tags.  Probes are just a copy of good muons, which
# is needed as subsequent modules expect a collection of references
# rather than actual muons.
process.probes = cms.EDFilter('PATMuonRefSelector',
    src = cms.InputTag('goodMuons'),
    cut = cms.string('')
)
process.tagsNoTrigger = cms.EDFilter('PATMuonRefSelector',
    src = cms.InputTag('goodMuons'),
    cut = cms.string('pt > 26.')
)
process.tags = cms.EDProducer('PatMuonTriggerCandProducer',
    bits = cms.InputTag('TriggerResults', '', options.triggerProcessName),
    dR = cms.double(0.3),
    filterNames = cms.vstring(
        'hltL3crIsoL1sMu22L1f0L2f10QL3f24QL3trkIsoFiltered0p09',
        'hltL3fL1sMu22L1f0Tkf24QL3trkIsoFiltered0p09'
    ),
    inputs = cms.InputTag('tagsNoTrigger'),
    isAND = cms.bool(False),  # at least one of the filters
    objects = cms.InputTag('selectedPatTrigger')
)
process.p += process.probes + process.tagsNoTrigger


# Define passing probes
process.passingProbes = cms.EDProducer('PatMuonTriggerCandProducer',
    bits = cms.InputTag('TriggerResults', '', options.triggerProcessName),
    dR = cms.double(0.3),
    filterNames = cms.vstring(
        'hltL3crIsoL1sMu22L1f0L2f10QL3f24QL3trkIsoFiltered0p09',
        'hltL3fL1sMu22L1f0Tkf24QL3trkIsoFiltered0p09'
    ),
    inputs = cms.InputTag('probes'),
    isAND = cms.bool(False),  # at least one of the filters
    objects = cms.InputTag('selectedPatTrigger')
)


# Build tag-probe pairs
process.tagProbePairs = cms.EDProducer('CandViewShallowCloneCombiner',
    checkCharge = cms.bool(True),
    cut = cms.string('60. < mass < 120.'),
    decay = cms.string('tags@+ probes@-')
)


# Reweighting for pileup
process.pileupWeightProducer = cms.EDProducer('PileupWeightProducer',
    pileupInfoTag = cms.InputTag('slimmedAddPileupInfo'),
    PileupData = cms.vdouble(
        2089.62956914, 159955.708702, 614013.655512, 1245342.74124, 1942400.09885, 2634038.86143,
        3539700.24252, 8460726.01703, 29245438.5629, 69800658.1416, 136505863.254, 229956106.945,
        352174867.954, 483323203.195, 604181515.838, 718692337.781, 822519970.332, 902598131.862,
        952455066.298, 971642614.916, 961652388.576, 923801999.387, 862498597.538, 784523657.308,
        694724435.502, 595744388.019, 491342816.752, 388126610.98, 293543737.799, 212808587.929,
        147869960.019, 98256026.3173, 62252327.2582, 37548131.7717, 21567454.2577, 11811072.9432,
        6174466.91928, 3086382.70548, 1479290.611, 682903.221284, 305786.192123, 134412.550535,
        59351.5375969, 27540.3171446, 14454.9144601, 9219.61100027, 7180.34048733, 6406.24224784,
        6116.8611278, 6002.57775894
    ),
    PileupMC = cms.vdouble(
        0.000829312873542, 0.00124276120498, 0.00339329181587, 0.00408224735376, 0.00383036590008,
        0.00659159288946, 0.00816022734493, 0.00943640833116, 0.0137777376066, 0.017059392038,
        0.0213193035468, 0.0247343174676, 0.0280848773878, 0.0323308476564, 0.0370394341409,
        0.0456917721191, 0.0558762890594, 0.0576956187107, 0.0625325287017, 0.0591603758776,
        0.0656650815128, 0.0678329011676, 0.0625142146389, 0.0548068448797, 0.0503893295063,
        0.040209818868, 0.0374446988111, 0.0299661572042, 0.0272024759921, 0.0219328403791,
        0.0179586571619, 0.0142926728247, 0.00839941654725, 0.00522366397213, 0.00224457976761,
        0.000779274977993, 0.000197066585944, 7.16031761328e-05, 0., 0., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 0.
    )
)


# Count jets not overlapping with electrons and associated this number
# with the electrons so it can be accessed as a property of a probe
process.goodJets = cms.EDProducer('PATJetCleaner',
    src = cms.InputTag('slimmedJets'),
    preselection = cms.string(''),
    finalCut = cms.string('pt > 30. & abs(eta) < 5.'),
    checkOverlaps = cms.PSet(
        electrons = cms.PSet(
            algorithm = cms.string('byDeltaR'),
            checkRecoComponents = cms.bool(False),
            deltaR = cms.double(0.4),
            pairCut = cms.string(''),
            preselection = cms.string(''),
            requireNoOverlaps = cms.bool(True),
            src = cms.InputTag('probes')
        )
    )
)
process.jetCounter = cms.EDProducer('CandMultiplicityCounter',
    objects = cms.InputTag('goodJets'),
    probes = process.probes.src
)


# Save tag-probe pairs
process.muonTriggerTnP = cms.EDAnalyzer('TagProbeFitTreeProducer',
    allProbes = cms.InputTag('probes'),
    tagProbePairs = cms.InputTag('tagProbePairs'),
    variables = cms.PSet(
        probe_pt = cms.string('pt'),
        probe_eta = cms.string('eta'),
        probe_nJet30 = cms.InputTag('jetCounter')
    ),
    tagVariables = cms.PSet(
        pt = cms.string('pt'),
        eta = cms.string('eta')
    ),
    pairVariables = cms.PSet(),
    mcVariables = cms.PSet(),
    flags = cms.PSet(
        passingHLT = cms.InputTag('passingProbes')
    ),
    tagFlags = cms.PSet(),
    pairFlags = cms.PSet(),
    mcFlags = cms.PSet(),
    addEventVariablesInfo = cms.bool(True),
    isMC = cms.bool(not options.runOnData),
    genParticles = cms.InputTag('prunedGenParticles'),
    pdgId = cms.int32(13),
    motherPdgId = cms.vint32(),
    useTauDecays = cms.bool(False),
    arbitration = cms.string('None'),
    checkCharge = cms.bool(False),
    pileupInfoTag = cms.InputTag('slimmedAddPileupInfo'),
    vertexCollection = cms.InputTag('offlineSlimmedPrimaryVertices'),
    eventWeight = cms.InputTag('generator'),
    PUWeightSrc = cms.InputTag('pileupWeightProducer', 'pileupWeights')
)
process.p += process.muonTriggerTnP

if options.runOnData:
    del(process.muonTriggerTnP.genParticles)
    del(process.muonTriggerTnP.eventWeight)
    del(process.muonTriggerTnP.PUWeightSrc)


process.TFileService = cms.Service('TFileService',
    fileName = cms.string('TnPTree.root')
)
