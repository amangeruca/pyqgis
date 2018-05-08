from qgis.gui import QgsMessageBar
from split_line import do_split_layer_by_feature
from clean_line import do_clean_geom
from settings import APP_CONFIG
from utils import (MyLog)
from geo_utils import (get_feat_byid,
                       create_feature_from_tmpl)

class LineLayer:
  
  def __init__(self, iface, layer):
    self.iface = iface
    self.layer_state = {
        "is_action_split_checked": APP_CONFIG['check_split_button'] and APP_CONFIG['check_split_button'],
        "is_action_selfint_checked": APP_CONFIG['check_selfint_button'] and APP_CONFIG['allow_selfint_button'],
        "is_action_simpl_checked": APP_CONFIG['check_simpl_button'] and APP_CONFIG['allow_simpl_button']
    }
    self.props_switch = {
      "split": {"auth": APP_CONFIG['allow_split_button'], "prop": "is_action_split_checked"},
      "selfint": {"auth": APP_CONFIG['allow_selfint_button'], "prop": "is_action_selfint_checked"},
      "simpl": {"auth": APP_CONFIG['allow_simpl_button'], "prop": "is_action_simpl_checked"}
    }
    self.current_fid = None
    self.layer = layer
    
    
  #return the layer map id
  def get_layer_id(self):
    return self.layer.id()
  
  
  def attach_editor_event(self):
    self.layer.featureAdded.connect(self.on_featureAdded)
    self.layer.editCommandEnded.connect(self.on_editCommandEnded)
    self.layer.beforeCommitChanges.connect(self.on_beforeCommitChanges)
    self.layer.committedFeaturesAdded.connect(self.on_committedFeaturesAdded)
    

  def detach_editor_event(self):
    self.layer.committedFeaturesAdded.disconnect(self.on_committedFeaturesAdded)
    self.layer.beforeCommitChanges.disconnect(self.on_beforeCommitChanges)
    self.layer.editCommandEnded.disconnect(self.on_editCommandEnded)
    self.layer.featureAdded.disconnect(self.on_featureAdded)
    
    
  def set_state(self, prop_name, value):
    prop = self.props_switch[prop_name]
    self.layer_state[prop["prop"]] = prop["auth"] and value
    
    
  def reset_buttons_state(self):
    for p in self.layer_state:
      self.layer_state[p] = False    

    
  def on_featureAdded(self, fid):   
    print "on feature: feat added %s" %fid
    self.current_fid = fid
    
    
  def on_editCommandEnded(self):
#     layer = self.iface.activeLayer()
#     #detach featureadd signal
#     self._featureAdded_management(layer, conn=False)
    print "editCommandEnded"
# 
#     layer = self.featureAdded["layer"]
#     fid = self.featureAdded["id_feat"]
    
    #detach featureadd signal
    self.layer.editCommandEnded.disconnect(self.on_editCommandEnded)
    
    #perform the process
    self.do_update_onEditCommandEnded()
    
    #attach featureadd signal      
    self.layer.removeSelection()
    self.layer.editCommandEnded.connect(self.on_editCommandEnded)
    
       
  def on_beforeCommitChanges(self):
#     layer = self.iface.activeLayer()
#     #detach featureadd signal
#     self._featureAdded_management(layer, conn=False)
     
    print "beforeCommitChanges"
       
   
  def on_committedFeaturesAdded(self, lid, fids):
#     layer = self.iface.activeLayer()
#     #detach featureadd signal
#     self._featureAdded_management(layer, conn=False)
     
    print "committedFeaturesAdded %s, %s" %(lid, ','.join([str(f.id()) for f in fids]))
    
    
  def do_update_onEditCommandEnded(self):
    try:
        #create feature from the udpated geom
        feat_targ = get_feat_byid(self.layer, self.current_fid)[0] 
        
        #clean line and get cleaned geometry. 
        cleaned_geoms = do_clean_geom(feat_targ, self.layer_state["is_action_selfint_active"], self.layer_state["is_action_simpl_active"]) #self.is_action_selfint_active, self.is_action_simplify_active)
        targ_geoms = cleaned_geoms
    
        #perform splitting on every geometry from cleaned geoms
        #split line at intersection with other feature of the same layer
        if self.layer_state["is_action_split_active"]:
            splitted_geoms = do_split_layer_by_feature(self.layer, self.current_fid, cleaned_geoms)
            targ_geoms = splitted_geoms
        
        #Create feature from the modified geometry
        feats_new = []
        for tgeom in targ_geoms:
            f = create_feature_from_tmpl(feat_targ, tgeom)
            feats_new.append(f)
        
        #apply all the updates to target geom
        self.apply_update_on_editCommandEnded(feats_new)
        
    except Exception as e:
        msg = "Line editor management error on edit command ended: %s" %e
        MyLog.log_error(msg)
        self.iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)
        self.layer.deleteFeature(self.current_fid)
        
        
  def apply_update_on_editCommandEnded(self, feats):
      try:
          self.layer.beginEditCommand("Split Feature Target")
          MyLog.log_info("Apply after edit ended update")
      
          #delete the original features
          self.layer.deleteFeatures(self.current_fid)
          #add the splitted features
          self.layer.addFeatures(feats)
    
      except e as Exception:
          layer.destroyEditCommand()
          msg = "Error on after edit ended update: %s" %e 
          raise Exception(msg)
    
      finally:
          self.layer.endEditCommand()
  