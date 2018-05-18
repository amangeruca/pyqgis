from qgis.gui import QgsMessageBar
from split_line import do_split_layer_by_feature
from clean_line import (do_makeGeometryValid
                        ,do_clean_multipart
                        ,do_clean_simplify)
from settings import APP_CONFIG
from utils import (MyLog)
from geo_utils import (get_feat_byid,
                       create_feature_from_tmpl)


class LineLayer:
  
  def __init__(self, lineEditor, layer):
    self.iface = lineEditor.iface
    self.layer_state = {
        "is_action_split_checked": APP_CONFIG['check_split_button'],
        "is_action_selfint_checked": APP_CONFIG['check_selfint_button'],
        "is_action_simpl_checked": APP_CONFIG['check_simpl_button']
    }
    self.props_switch = {
      "split": {"auth": APP_CONFIG['allow_split_button'], "prop": "is_action_split_checked"},
      "selfint": {"auth": APP_CONFIG['allow_selfint_button'], "prop": "is_action_selfint_checked"},
      "simpl": {"auth": APP_CONFIG['allow_simpl_button'], "prop": "is_action_simpl_checked"}
    }
    self.layer = layer
    self.isCommittedFeatureAdded = False
    self.current_fids = None
    self.handle_lineEditProcessResult = None
    self.on_layerEditStared = lineEditor.on_layerEditStarted
    self.on_layerEditStoped = lineEditor.on_layerEditStoped
    self.attach_event()
    
    
  def __del__(self):
    self.detach_event() 
  
  
  def attach_event(self):
    self.layer.selectionChanged.connect(self.on_selectionChanged)
    self.layer.editingStarted.connect(self.on_editingStarted)
    self.layer.editingStopped.connect(self.on_editingStoped)
    self.layer.editCommandStarted.connect(self.on_editCommandStarted)
    self.layer.editCommandDestroyed.connect(self.on_editCommandDestroyed)
    self.layer.editCommandEnded.connect(self.on_editCommandEnded)
    self.layer.beforeCommitChanges.connect(self.on_beforeCommitChanges)
    self.layer.committedFeaturesAdded.connect(self.on_committedFeaturesAdded)
  
  
  def detach_event(self):
    self.layer.committedFeaturesAdded.connect(self.on_committedFeaturesAdded)
    self.layer.beforeCommitChanges.connect(self.on_beforeCommitChanges)
    self.layer.editCommandEnded.disconnect(self.on_editCommandEnded)
    self.layer.editCommandDestroyed.disconnect(self.on_editCommandDestroyed)
    self.layer.editCommandStarted.disconnect(self.on_editCommandStarted)
    self.layer.editingStopped.disconnect(self.on_editingStoped)
    self.layer.editingStarted.disconnect(self.on_editingStarted)
    self.layer.selectionChanged.disconnect(self.on_selectionChanged)
  
  
  def attach_lineedit_event(self):
    self.layer.featureAdded.connect(self.on_featureAdded)
    self.layer.featuresDeleted.connect(self.on_featuresDeleted)
    self.layer.geometryChanged.connect(self.on_geometryChanged)
#     self.layer.editCommandStarted.connect(self.on_editCommandStarted)
#     self.layer.editCommandEnded.connect(self.on_editCommandEnded)

          
  def detach_lineedit_event(self):
#     self.layer.editCommandEnded.disconnect(self.on_editCommandEnded)
#     self.layer.editCommandStarted.disconnect(self.on_editCommandStarted)
    self.layer.geometryChanged.disconnect(self.on_geometryChanged)
    self.layer.featuresDeleted.disconnect(self.on_featuresDeleted)
    self.layer.featureAdded.disconnect(self.on_featureAdded)
    
      
  def on_selectionChanged(self, sel_fids, desel_fids, new_sel):
    print "on selection changed", sel_fids
    self.current_fids = sel_fids
  
  
  def on_editingStarted(self):
    print "on_editingStarted"
    self.isCommittedFeatureAdded = False
    self.attach_lineedit_event()
    self.on_layerEditStared(self.layer_state)
  
  
  def on_editingStoped(self):
    print "on_editingStoped"
    self.on_layerEditStoped()
    self.detach_lineedit_event()

    
  def on_featureAdded(self, fid):   
    print "on feature added: feat added %s" %fid   

    '''
      Andrea Mangeruca 18-05-10
      review of where the lineedit update is performs.
      try process on feature add
      
    '''
#     #     self.current_fids = [fid]
    #detach featureadd signal
    
    #process line if feature add is not from committed signal (when press save button)
    if not self.isCommittedFeatureAdded: self.set_lineEditProcess(fid)
    
    
  def on_featuresDeleted(self, fids):
    print "on features deleted", fids
    self.current_fids = None
    
    
  def on_geometryChanged(self, fid, geom):
    print "on geometryChanged", fid, geom.exportToWkt()
    if not self.isCommittedFeatureAdded: self.set_lineEditProcess(fid)
    
    
  def on_editCommandStarted(self, txt):
    print "on editCommandStarted %s" %txt
#     MyLog.log_info("Edit command started: %s" %txt)
    
    
  def on_editCommandDestroyed(self):
    print "on editCommandDestroyed"
    
    self.handle_lineEditProcessResult = None

    
    
  def on_editCommandEnded(self):
    print "on editCommandEnded"
    
    if not (self.handle_lineEditProcessResult is None): 
      self.do_lineEditProcess()
#     if self.current_fids is None: return
#     
#     #detach featureadd signal
#     self.layer.editCommandEnded.disconnect(self.on_editCommandEnded)
#     
#     #perform the process
#     self.do_lineEditProcess()
#     
#     #attach featureadd signal      
#     self.layer.removeSelection()
#     self.current_fids=None
#     self.layer.editCommandEnded.connect(self.on_editCommandEnded)
    
       
  def on_beforeCommitChanges(self):
#     layer = self.iface.activeLayer()
#     #detach featureadd signal
#     self._featureAdded_management(layer, conn=False)
     
    print "on beforeCommitChanges"
       
   
  def on_committedFeaturesAdded(self, lid, fids):
#     layer = self.iface.activeLayer()
#     #detach featureadd signal
#     self._featureAdded_management(layer, conn=False)
    print "on committedFeaturesAdded %s, %s" %(lid, ','.join([str(f.id()) for f in fids]))
    self.isCommittedFeatureAdded = True

     
  def set_state(self, prop_name, value):
    prop = self.props_switch[prop_name]
    self.layer_state[prop["prop"]] = prop["auth"] and value
    
    
  def reset_buttons_state(self):
    for p in self.layer_state:
      self.layer_state[p] = False    
    
    
  def set_lineEditProcess(self, fid):
    
    try:
        MyLog.log_info("LINEDITPROCESS STARTED - Feat: %s" %fid)
        
        #feature ids update from the process
        feats_targ_new = [] #new feature after change
        feats_int_new = []
        geom_targ_new = []
        targ_updated = False
                 
        #get feat and init variable
        feat_targ = get_feat_byid(self.layer, [fid])[0] 
        geom_targ = feat_targ.geometry()
        geom_targ_new = [geom_targ]
        feat_updated_ids = [fid]
        self.handle_lineEditProcessResult = LineEditProcessResult(self, fid)
        
        #Validate geometry
        if self.layer_state["is_action_selfint_checked"]:
            validateResults = geom_targ.validateGeometry()
            if len(validateResults) > 0:
                MyLog.log_info("Do make geometry valid")
                geom_targ_new = do_makeGeometryValid(geom_targ)
                targ_updated = True
                
        #Remove Multipart
        sngl_geoms = do_clean_multipart(geom_targ_new)
        if len(sngl_geoms) > 1:
            geom_targ_new = sngl_geoms
            targ_updated = True
            
        #Simplify geometries
        if self.layer_state["is_action_simpl_checked"]:
            MyLog.log_info("Do simplify geometry")
            simpl_geoms = do_clean_simplify(geom_targ_new)
            geom_targ_new = simpl_geoms
            targ_updated = True
            
        #Check if geometries intersects other features and split them 
        if self.layer_state["is_action_split_checked"]:
            geom_targ_splited, feats_int_new, ids_feat_updated = do_split_layer_by_feature(self.layer, fid, geom_targ_new)
            if geom_targ_splited is not None:
                feat_updated_ids.extend(ids_feat_updated)
                geom_targ_new = geom_targ_splited
                targ_updated = True
                
        if targ_updated:
            #Create feature from the modified geometry and apply update
            for tgeom in geom_targ_new:
                f = create_feature_from_tmpl(self.layer, feat_targ, tgeom)
                feats_targ_new.append(f)
                
            self.handle_lineEditProcessResult.set_Result(feats_int_new, feats_targ_new, feat_updated_ids)
            
        MyLog.log_info("LINEDITPROCESS FINISCHED - Feat: %s" %fid)
        
    except Exception as e:
        msg = "Do_lineeditonfeatureadd error: %s" %e
        MyLog.log_error(msg)
        self.iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)
        self.layer.deleteFeature(fid)
            
            
  def do_lineEditProcess(self):
      #apply all the updates to target geom
      try:
          feats_int_new = [] if self.handle_lineEditProcessResult.feats_int_new is None else self.handle_lineEditProcessResult.feats_int_new
          feats_targ_new = [] if self.handle_lineEditProcessResult.feats_targ_new is None else self.handle_lineEditProcessResult.feats_targ_new
          feat_updated_ids = [] if self.handle_lineEditProcessResult.feat_updated_ids is None else self.handle_lineEditProcessResult.feat_updated_ids
          self.handle_lineEditProcessResult = None
          
          self.detach_lineedit_event()
          self.layer.beginEditCommand("processResult")
          
          #add the feature intersects news and then the target new so just the target remain selected
          if len(feats_int_new) > 0: self.layer.addFeatures(feats_int_new)
          if len(feats_targ_new) > 0: self.layer.addFeatures(feats_targ_new)
          if len(feat_updated_ids) > 0: self.layer.deleteFeatures(feat_updated_ids)           
              
          MyLog.log_info("%s features added; %s features delected" %(len(feats_targ_new) + len(feats_int_new), len(feat_updated_ids)))
        
      except Exception as e:
          self.layer.destroyEditCommand()
          raise e
          
      finally:
          self.layer.endEditCommand() 
          self.attach_lineedit_event()
            
                
#             #apply all the updates to target geom
#             try:
#                 self.detach_lineedit_event()
#                 self.layer.endEditCommand() 
#                 self.layer.beginEditCommand("Line edit after feature added")
#                 
#                 #add the feature intersects news and then the target new so just the target remain selected
#                 if len(feats_int_new) > 0: self.layer.addFeatures(feats_int_new)
#                 if len(feats_targ_new) > 0: self.layer.addFeatures(feats_targ_new)
#                 self.layer.deleteFeatures(targ_ids)
#                 
#                 MyLog.log_info("%s features added; %s features delected" %(len(feats_targ_new) + len(feats_int_new), len(targ_ids)))
#           
#             except Exception as e:
#                 self.layer.destroyEditCommand()
#                 raise e
#                 
#             finally:
# #                 self.layer.endEditCommand() 
#                 self.attach_lineedit_event()
                     
    
        
#         #clean line and get cleaned geometry. (Remove multipolyline, remove selfintersects, simplify line)
#         cleaned_geoms = do_clean_geom(feat_targ, self.layer_state["is_action_selfint_checked"], self.layer_state["is_action_simpl_checked"]) 
#         targ_geoms = cleaned_geoms 
         
#         #perform splitting on every geometry from cleaned geoms
#         #split line at intersection with other feature of the same layer
#         if self.layer_state["is_action_split_checked"]:
#             geom_targ_new, feats_int_new, ids_feat_updated = do_split_layer_by_feature(self.layer, fid, cleaned_geoms)
#             targ_ids.extend(ids_feat_updated)
#             ''' 
#               Andrea Mangeruca 18-05-09
#               review how to consider geom_targ_new
#               the method above create overlaps beteewn feat_int and feat_targ when feat_targ completely overlaps all feat_int so is geom_targ_new remain empty and
#               it will take the orignal feature without consider feat_in 
#               
#               if len(geom_targ_new) > 0:  targ_geoms = geom_targ_new
#             '''
# 
#             #if any splitting operation has done it meens that also geom_targ has been modified
#             #in this way we consider cases when all feat_targ overlap feat int and the features int will be splitted but not geom target is returned
#             if len(feats_int_new) > 0:  targ_geoms = geom_targ_new
#          
#         #Create feature from the modified geometry and apply update
#         if len(targ_geoms)>0:
#           for tgeom in targ_geoms:
#               f = create_feature_from_tmpl(self.layer, feat_targ, tgeom)
#               feats_targ_new.append(f)
# #           
#           #apply all the updates to target geom
#           try:
#               self.detach_lineedit_event()
#               self.layer.beginEditCommand("Line edit after feature added")
#               
#               #add the feature intersects news and then the target new so just the target remain selected
#               self.layer.addFeatures(feats_int_new)
#               self.layer.addFeatures(feats_targ_new)
#               self.layer.deleteFeatures(targ_ids)
#               
#               MyLog.log_info("%s features added; %s features delected" %(len(feats_targ_new) + len(feats_int_new), len(targ_ids)))
#         
#           except Exception as e:
#               self.layer.destroyEditCommand()
#               raise e
#               
#           finally:
#               self.layer.endEditCommand() 
#               self.attach_lineedit_event()
              



class LineEditProcessResult:
  
    def __init__(self, lineLayer, feat_targ_id):
        self.lineLayer = lineLayer
        self.feat_targ_id = feat_targ_id
        self.feats_int_new = None
        self.feats_targ_new = None
        self.feat_updated_ids = None
        
        
    def set_Result(self, feats_int_new=None, feats_targ_new=None, feat_updated_ids=None):
        self.feats_int_new = feats_int_new
        self.feats_targ_new = feats_targ_new
        self.feat_updated_ids = feat_updated_ids
        
            
#   def do_lineEditProcess(self):
#     try:      
#         #beign a buffer on editing
#         self.layer.beginEditCommand("Line management edit update")
#         
#         #create feature from the udpated geom
#         feat_targ = get_feat_byid(self.layer, self.current_fids)[0] 
#         
#         #clean line and get cleaned geometry. 
#         cleaned_geoms = do_clean_geom(feat_targ, self.layer_state["is_action_selfint_checked"], self.layer_state["is_action_simpl_checked"]) 
#         targ_geoms = cleaned_geoms #new goemetries for the commited feature
#         targ_ids = self.current_fids #feature ids update from the process
#         feats_new = [] #new feature after change
#     
#         #perform splitting on every geometry from cleaned geoms
#         #split line at intersection with other feature of the same layer
#         if self.layer_state["is_action_split_checked"]:
#             geom_targ_new, feats_int_new, ids_feat_updated = do_split_layer_by_feature(self.layer, self.current_fids[0], cleaned_geoms)
#             feats_new.extend(feats_int_new)
#             targ_ids.extend(ids_feat_updated)
#             if len(geom_targ_new) > 0:  targ_geoms = geom_targ_new
#         
#         #Create feature from the modified geometry
#         if len(targ_geoms)>0:
#           for tgeom in targ_geoms:
#               f = create_feature_from_tmpl(feat_targ, tgeom)
#               feats_new.append(f)
#           
#           #apply all the updates to target geom
#           self.layer.deleteFeatures(targ_ids)
#           self.layer.addFeatures(feats_new)
#         
#     except Exception as e:
#         msg = "Line editor management error on edit command ended: %s" %e
#         MyLog.log_error(msg)
#         self.layer.destroyEditCommand()
#         self.iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)
#         self.layer.deleteFeature(self.current_fids[0])
#         
#     finally:
#         self.layer.endEditCommand()  
        
  