#include "MuonSelectorWithID.h"

#include <DataFormats/VertexReco/interface/Vertex.h>
#include <FWCore/Framework/interface/MakerMacros.h>
#include <FWCore/Utilities/interface/EDMException.h>
#include <FWCore/Utilities/interface/InputTag.h>

#include <algorithm>
#include <limits>


MuonSelectorWithID::MuonSelectorWithID(edm::ParameterSet const &cfg):
    selector(cfg.getParameter<std::string>("cut")),
    maxRelIso(cfg.getParameter<double>("maxRelIso")),
    filterOn(cfg.getParameter<bool>("filter"))
{
    // Register input data
    srcToken = consumes<edm::View<pat::Muon>>(cfg.getParameter<edm::InputTag>("src"));
    primaryVerticesToken =
      consumes<reco::VertexCollection>(cfg.getParameter<edm::InputTag>("primaryVertices"));
    
    
    // Parse the required ID
    std::string const idTypeLabel = cfg.getParameter<std::string>("passID");
    
    if (idTypeLabel == "")
        idType = ID::None;
    else if (idTypeLabel == "tight")
        idType = ID::Tight;
    else
    {
        edm::Exception excp(edm::errors::Configuration);
        excp << "Cannot recognize ID label \"" << idTypeLabel << "\".";
        excp.raise();
    }
    
    
    // Register product
    produces<std::vector<pat::Muon>>();
}


void MuonSelectorWithID::fillDescriptions(edm::ConfigurationDescriptions &descriptions)
{
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("src")->setComment("Source collection of muons.");
    desc.add<std::string>("cut", "")->setComment("Cut-based selection.");
    desc.add<double>("maxRelIso", std::numeric_limits<double>::infinity())->
      setComment("Maximal allowed value for relative isolation.");
    desc.add<std::string>("passID", "")->setComment("ID for selection.");
    desc.add<edm::InputTag>("primaryVertices")->setComment("Collection of primary vertices.");
    desc.add<bool>("filter", true)->setComment("Enable or disable event filtering.");
    
    descriptions.add("muonSelectorWithID", desc);
}


bool MuonSelectorWithID::filter(edm::Event &event, edm::EventSetup const &)
{
    using namespace edm;
    
    // First read primary vertices
    Handle<reco::VertexCollection> vertices;
    event.getByToken(primaryVerticesToken, vertices);
    
    if (vertices->size() == 0)
    {
        Exception excp(errors::LogicError);
        excp << "Event contains zero primary vertices.\n";
        excp.raise();
    }
    
    
    // Read the muon collection
    Handle<View<pat::Muon>> srcMuons;
    event.getByToken(srcToken, srcMuons);
    
    
    // Create a collection of selected muons
    std::unique_ptr<std::vector<pat::Muon>> selectedMuons(new std::vector<pat::Muon>);
    
    for (auto const &mu: *srcMuons)
    {
        if (not selector(mu))
            continue;
        
        
        auto const &isoR04 = mu.pfIsolationR04();
        double const relIso = (isoR04.sumChargedHadronPt +
          std::max(isoR04.sumNeutralHadronEt + isoR04.sumPhotonEt - 0.5 * isoR04.sumPUPt, 0.)) /
          mu.pt();
        
        if (relIso > maxRelIso)
            continue;
        
        
        if (idType == ID::Tight)
        {
            if (not mu.isTightMuon(vertices->front()))
                continue;
        }
        
        
        selectedMuons->emplace_back(mu);
    }
    
    
    // Write the selected muons and evaluate the filter decision
    bool const filterDecision = not filterOn or not selectedMuons->empty();
    event.put(std::move(selectedMuons));
    return filterDecision;
}


DEFINE_FWK_MODULE(MuonSelectorWithID);
