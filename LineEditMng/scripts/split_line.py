from qgis.core import QgsPoint, QgsGeometry
from qgis.gui import QgsMessageBar
from geo_utils import (get_feat_bbox
                      ,get_feats_on_bbox
                      ,get_feat_byid
                      ,get_singles_part_geometries
                      ,get_intersection_points
                      ,get_rounded_points
                      ,create_feature_from_tmpl) 
from utils import (MyLog)
from settings import APP_CONFIG

#split layer feature at intersection with the added feature. Then split the added feat
def do_split_layer_by_feature(layer, id_targ, targ_geoms):
    geom_targ_new = []
    feats_int_new = []
    ids_feat_updated = []
    
    #create multigeometry from targs_geoms so all the geometry can be evaluate together
    unionGeom = QgsGeometry.unaryUnion(targ_geoms)
    
    #get the feature that are close to target geom
    feats_int = get_feats_close_to(layer, id_targ, unionGeom)
    
    if len(feats_int) > 0:
        pts_int_finded = []
        for f_int in feats_int:
            g_int = f_int.geometry()
            #get point intersection 
            geom_int_pts = get_intersection_points(unionGeom, g_int)
            
            #if interesection
            if geom_int_pts:
                #round pt geometry to a grid
                geom_int_pts_rnd = get_rounded_points(geom_int_pts, decimal=APP_CONFIG['rounding_digit'])
                pts_int_finded.extend(geom_int_pts_rnd)
            
                #split interesection layer and return new feature
                feat_int_splitted = get_splitted_feats(f_int, geom_int_pts_rnd)
                
                #if there are feat to splited rec all feats to update existing
                if len(feat_int_splitted) > 0:
                    feats_int_new.extend(feat_int_splitted)
                    ids_feat_updated.append(f_int.id())
                
        #split every target geom
        if len(pts_int_finded) > 0:
            for tgeom in targ_geoms:
              tgeom_splitted = split_geom(tgeom, pts_int_finded)
              if len(tgeom_splitted) > 0:
                  has_target_splitted = True
                  geom_targ_new.extend(tgeom_splitted)
              else:
                  geom_targ_new.append(tgeom)
                  
    return geom_targ_new, feats_int_new, ids_feat_updated  
        
  
#get all the feature the intersect the bounding box of the layer  
def get_feats_close_to(layer, id_targ, geom):
    bbox = get_feat_bbox(geom)
    feats_ids_on_bbox = get_feats_on_bbox(layer, bbox)
    feats_ids_on_bbox.remove(id_targ)
    feats_on_bbox = get_feat_byid(layer, feats_ids_on_bbox)
    
    MyLog.log_info("finded %s close to" % len(feats_ids_on_bbox))
    return feats_on_bbox
  
  
def get_splitted_feats(feat, geom_int_pts_rnd):
    feat_splitted = []
    
    #decompose feat in singles parts
    sngl_geoms = get_singles_part_geometries(feat.geometry())
    
    for sngl in sngl_geoms:
        #get point on single geoms
        try:
          MyLog.log_info("Splitting geom of feature %s part" %feat.id())
          splitted_geom = split_geom(sngl, geom_int_pts_rnd)
        
          for splt in splitted_geom: 
              f = create_feature_from_tmpl(feat, splt)
              feat_splitted.append(f)
              
        except Exception as e:
          msg = "Error spliting geometry part: %s" %e
          MyLog.log_error(msg)
          self.iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)
          continue
          
    return feat_splitted
     
      
def split_geom(geom, split_pts):
    geom_splitted = []
    
    #insert vertices in the geometry to split, and get the position index
    pts_position = densify_feature_wiht_points(geom, split_pts, tolerance=APP_CONFIG["split_tolerance"])
    
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
# find as it works
# when i split a geometry also the target geometry will be modified 
# so orig = orig(mod) + splitteds
# will leave the other methodology until it works


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
#       MyLog.log_warn("Split line", "Error on splitting lines")
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
