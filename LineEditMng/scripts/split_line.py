from qgis.core import QgsFeature, QgsPoint, QgsGeometry
from qgis.gui import QgsMessageBar
from geo_utils import (get_feat_bbox
                      ,get_feats_on_bbox
                      ,get_feat_byid
                      ,get_singles_part_geometries
                      ,get_intersection_points
                      ,get_rounded_points) 
from utils import (log_info, log_warn, log_error)

#split layer feature at intersection with the added feature. Then split the added feat
def do_split_layer_by_feature(layer, id_targ):
    feats_int_new = []
    pts_int_finded = []
    ids_feat_updated = []

    feat_targ = get_feat_byid(layer, [id_targ])[0] 
    feats_int = get_feats_close_to(layer, feat_targ)
    if len(feats_int) > 0:
      for f_int in feats_int:
        #get point intersection 
        geom_int_pts = get_intersection_points(feat_targ, f_int)
        
        #if interesection
        if geom_int_pts:
            #round pt geometry to a grid
            geom_int_pts_rnd = get_rounded_points(geom_int_pts)
            pts_int_finded.extend(geom_int_pts_rnd)
            
            #split interesection layer and return new feature
            feat_int_splitted = get_splitted_feats(f_int, geom_int_pts_rnd)
            
            #if there are feat to splited rec all feats to update existing
            if len(feat_int_splitted) > 0:
                feats_int_new.extend(feat_int_splitted)
                ids_feat_updated.append(f_int.id())
                
      #split target feature
      if len(pts_int_finded) > 0:
        feat_targ_splitted = get_splitted_feats(feat_targ, pts_int_finded)
        
        if len(feat_targ_splitted) > 0:
          feats_int_new.extend(feat_targ_splitted)  
          ids_feat_updated.append(id_targ)
          
      #update features
      if len(feats_int_new)>0:
        apply_split_updated(layer, feats_int_new, ids_feat_updated)

  
#get all the feature the intersect the bounding box of the layer  
def get_feats_close_to(layer, feat):
    geom = feat.geometry()
    bbox = get_feat_bbox(geom)
    feats_ids_on_bbox = get_feats_on_bbox(layer, bbox)
    feats_ids_on_bbox.remove(feat.id())
    feats_on_bbox = get_feat_byid(layer, feats_ids_on_bbox)
    
    log_info("finded %s close to" % len(feats_ids_on_bbox))
    return feats_on_bbox
  
  
def get_splitted_feats(feat, geom_int_pts_rnd):
    feat_splitted = []
    feat_attrs = feat.attributes()
    
    #decompose feat in singles parts
    sngl_geoms = get_singles_part_geometries(feat.geometry())
    
    for sngl in sngl_geoms:
        #get point on single geoms
        try:
          log_info("Splitting geom of feature %s part" %feat.id())
          splitted_geom = split_geom(sngl, geom_int_pts_rnd)
        
          for splt in splitted_geom: 
              f = QgsFeature()
              f.setAttributes(feat_attrs)
              f.setGeometry(splt)
              feat_splitted.append(f)
              
        except Exception as e:
          msg = "Error spliting geometry part: %s" %e
          log_error(msg)
          self.iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)
          continue
          
    return feat_splitted
      
      
def split_geom(geom, split_pts):
    geom_splitted = []
    
    #insert vertices in the geometry to split, and get the position index
    pts_position = densify_feature_wiht_points(geom, split_pts)
    
    feat_vrt = geom.asPolyline()
    idx_ext_list = []
    idx_start = 0
    
    for idx in pts_position:
        idx_ext_list.append({"start": idx_start, "end": idx + 1})
        idx_start = idx
    idx_ext_list.append({"start": idx_start, "end": len(feat_vrt)})
      
    #create new features by splitting the vertices sequences
    for idx_ext in idx_ext_list:
        g = QgsGeometry.fromPolyline(feat_vrt[idx_ext["start"]: idx_ext["end"]])
        geom_splitted.append(g)
      
    return geom_splitted
      
      
# split geometry not seems to work
# def get_splitted_feats(feat, pts_int):
#     feat_splitted = []
#     feat_attrs = feat.attributes()
#     result, new_geoms, points = feat.constGeometry().splitGeometry(QgsGeometry.fromPolyline(pts_int).asPolyline(), True)
#     if result==0:
#       f = QgsFeature()
#       f.setAttributes(feat_attrs)
#       for g in new_geoms:
#         f.setGeometry(g)
#         
#     elif result > 1:
#       log_warn("Split line", "Error on splitting lines")
#         
#     return feat_splitted
  
  
#insert given point to the feature. If given point are a distance less than tolerance move point  
def densify_feature_wiht_points(geom, pts, tolerance=0.2):
    pts_position = []
    for pt in pts:
      #get the minimun distance form point to line
      dist_line_sqr, pt_on_line, next_vrt = geom.closestSegmentWithContext(pt)
      if dist_line_sqr < 0: break
      if dist_line_sqr > tolerance**2: continue 
      
      dist_to_vrt, vrt = geom.closestVertexWithContext(pt_on_line)
      if dist_to_vrt > tolerance**2:
        geom.insertVertex(pt.x(), pt.y(), next_vrt)
        idxpt_toadd = next_vrt
        
      else:
        geom.moveVertex(pt.x(), pt.y(), vrt)
        idxpt_toadd = vrt
      
      for i, pos in enumerate(pts_position):
        if pos >= idxpt_toadd:
          pts_position[i] = pos + 1
      pts_position.append(idxpt_toadd)
        
    pts_position.sort()
    return pts_position
  

def apply_split_updated(layer, new_feats, old_id_feats):
    try:
      log_info("Apply split update")
      
      layer.beginEditCommand("Features splitting")
      
      #delete the original features
      layer.deleteFeatures(old_id_feats)
      #add the splitted features
      layer.addFeatures(new_feats)
      
      layer.endEditCommand()
      
    except Exception as e:
      layer.destroyEditCommand()
      msg = "Error on appling split update: %s" %e   
      log_error(msg)   
      self.iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)