#pragma once

#include <FWCore/Framework/interface/EDFilter.h>
#include <FWCore/Framework/interface/Event.h>
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/ParameterSet/interface/ConfigurationDescriptions.h>
#include <FWCore/ParameterSet/interface/ParameterSetDescription.h>

#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/VertexReco/interface/VertexFwd.h>
#include <CommonTools/Utils/interface/StringCutObjectSelector.h>


/**
 * \class MuonSelectorWithID
 * \brief A PAT muon selector that can take into consideration muon ID
 * 
 * This plugin performs filtering of a collection of instances of pat::Muon, similar to
 * PATMuonSelector. In addition to a string-based selection, however, it allows to apply a
 * selection on muon ID (which requires access to primary vertices). Although a cut on isolation
 * can be described in the string, it is cumbersome. This plugin allows to cut on it directly.
 */
class MuonSelectorWithID: public edm::EDFilter
{
private:
    /// Supported identification criteria
    enum class ID
    {
        None,
        Tight
    };
    
public:
    /// Constructor from a configuration
    MuonSelectorWithID(edm::ParameterSet const &cfg);
    
public:
    /// Verifies configuration of the plugin
    static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);
    
private:
    /// Performs event filtering
    virtual bool filter(edm::Event &event, edm::EventSetup const &) override;
    
private:
    /// Source collection of muons
    edm::EDGetTokenT<edm::View<pat::Muon>> srcToken;
    
    /// String-based cut
    StringCutObjectSelector<pat::Muon> selector;
    
    /// Maximal allowed value for relative isolation
    double maxRelIso;
    
    /// Type of identification to be required
    ID idType;
    
    /// Collection of reconstructed primary vertices
    edm::EDGetTokenT<reco::VertexCollection> primaryVerticesToken;
    
    /// Indicates whether event filtering is enabled
    bool filterOn;
};
