from qgis.core import QgsPoint, QgsGeometry
from qgis.gui import QgsMessageBar
from geo_utils import (get_feat_bbox
                      ,get_feats_on_bbox
                      ,get_feat_byid
                      ,get_singles_part_geometries
                      ,get_intersection_points
                      ,get_rounded_points
                      ,create_feature_from_tmpl
                      ,add_close_vertex_to_linegeom
                      ,geom_difference_to_line_list
                      ,geom_intersection_to_line_list) 
from utils import (MyLog)
from settings import APP_CONFIG

#split layer feature at intersection with the added feature. Then split the added feat
def do_split_layer_by_feature(layer, id_targ, geoms_targ):
    geoms_targ_new = []
    feats_int_new = []
    ids_feat_updated = []
    geoms_int_snapped = []
    
    #create multigeometry from targs_geoms so all the geometry can be evaluate together
    uniong_targ = QgsGeometry.unaryUnion(geoms_targ)
    
    #get the feature that are close to target geom
    feats_int = get_feats_close_to(layer, id_targ, uniong_targ)
    
    if len(feats_int) > 0:
      
        for f_int in feats_int:
            geoms_int_splitted = []
            g_int = f_int.geometry()
            
            #if not intersection between g_int e u_geom skip
            if not g_int.intersects(uniong_targ): continue                                
          
            #add vertices from target_geom close to the g_geom
            for g_targ in geoms_targ:
              add_vertices_to_geom(g_int, g_targ)
            
            #save the update geometry to use for split the union of target geom
            geoms_int_snapped.append(g_int)
              
            #split intersected geometry first with difference and intersection
            geoms_int_diff = geom_difference_to_line_list(g_int, uniong_targ)
            geoms_int_inters = geom_intersection_to_line_list(g_int, uniong_targ)
                
            for g in geoms_int_diff + geoms_int_inters:
                geoms_int_splitted.append(QgsGeometry().fromPolyline(g))
                
            if len(geoms_int_splitted) > 0:
                #create new feature and save it in feats_int_new
                for g in geoms_int_splitted:
                    f = create_feature_from_tmpl(f_int, g)
                    feats_int_new.append(f)
                    
                #save the original id of the feature
                ids_feat_updated.append(f_int.id())
                
        #split union target geom otherwise noone intersect the target
        if len(geoms_int_snapped) > 0:
            uniong_int = QgsGeometry.unaryUnion(geoms_int_snapped)
            geoms_targ_diff = geom_difference_to_line_list(uniong_targ, uniong_int)
            
            for g_targ in geoms_targ_diff:
                geoms_targ_new.append(QgsGeometry().fromPolyline(g_targ))

    return geoms_targ_new, feats_int_new, ids_feat_updated  
        
  
#get all the feature the intersect the bounding box of the layer  
def get_feats_close_to(layer, id_targ, geom):
    bbox = get_feat_bbox(geom)
    feats_ids_on_bbox = get_feats_on_bbox(layer, bbox)
    feats_ids_on_bbox.remove(id_targ)
    feats_on_bbox = get_feat_byid(layer, feats_ids_on_bbox)
    
    MyLog.log_info("finded %s close to" % len(feats_ids_on_bbox))
    return feats_on_bbox
  
  
def add_vertices_to_geom(geom, t_geom):
    pts = t_geom.asPolyline()
    for pt in pts:
      add_close_vertex_to_linegeom(geom, pt, tolerance=APP_CONFIG['split_tolerance'])
      

''' 
  Andrea Mangeruca 18-05-09
  review of metodology for splitting geometry.
  the method above were substitute form difference and intersect native function
'''
'''
  
  
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
      
      #add to list of position if is before of already added pt move it forward
      for i, pos in enumerate(pts_position):
        if pos >= idxpt_toadd:
          pts_position[i] = pos + 1
      pts_position.append(idxpt_toadd)
        
    pts_position.sort()
    return pts_position

'''


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