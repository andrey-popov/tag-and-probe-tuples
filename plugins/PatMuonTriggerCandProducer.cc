#include <PhysicsTools/TagAndProbe/plugins/MiniAODTriggerCandProducer.h>

#include <DataFormats/PatCandidates/interface/Muon.h>


template<>
bool MiniAODTriggerCandProducer<pat::Muon, pat::TriggerObjectStandAlone>::
onlineOfflineMatching(pat::MuonRef ref,
  std::vector<pat::TriggerObjectStandAlone> const *triggerObjects, 
  std::string filterLabel, float dRmin)
{
    for (pat::TriggerObjectStandAlone const &obj: *triggerObjects) 
    { 
        if (obj.hasFilterLabel(filterLabel))
        {
            float const dR = deltaR(ref->p4(), obj.p4());
            
            if (dR < dRmin)
                return true;
        }
    }
    
    return false;
}


typedef MiniAODTriggerCandProducer<pat::Muon, pat::TriggerObjectStandAlone>
  PatMuonTriggerCandProducer;
DEFINE_FWK_MODULE(PatMuonTriggerCandProducer);
