from split_line import do_split_layer_by_feature

class Line_layer_cfg:
  
  def __init__(self, iface, layer):
    self.iface = iface
    self.is_action_split_active = False
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
    self.layer.featureAdded.disconnect(self.on_featureAdded)
    self.layer.editCommandEnded.disconnect(self.on_editCommandEnded)
    self.layer.beforeCommitChanges.disconnect(self.on_beforeCommitChanges)
    self.layer.committedFeaturesAdded.disconnect(self.on_committedFeaturesAdded)

    
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
    
    #split line at intersection with other feature of the same layer
    if self.is_action_split_active:
      do_split_layer_by_feature(self.layer, self.current_fid)

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