from qgis.core import QGis, QgsMapLayerRegistry, QgsSpatialIndex, QgsFeatureRequest, QgsPoint, QgsGeometry, QgsFeature

#get the ids of lines feature on map
def get_lyrs_line_id_on_map(maplayerregistry):
    lyrs = get_lyrs_line_on_map(maplayerregistry)
    lyrs_line_id = [lyr.id() for lyr in lyrs]
    return lyrs_line_id


#get the ids of lines feature on map
def get_lyrs_line_on_map(maplayerregistry):
    lyrs_vect = get_lyrs_vect_on_map(maplayerregistry)
    lyrs_line = [lyr for lyr in lyrs_vect if is_lyr_a_line(lyr)]
    return lyrs_line
  
  
#     lyr_list = []
#     for id, lyr in maplayerregistry.mapLayers().iteritems():
#         if lyr.type() == 0:
#           if is_layer_a_linestring:
#               lyr_list.append(lyr)
#     
#     return lyr_list

#get all layer on map
def get_lyrs_on_map(maplayerregistry):
    lyrs = [lyr for id, lyr in maplayerregistry.mapLayers().iteritems()]
    return lyrs
  
  
#get all vector layer on map  
def get_lyrs_vect_on_map(maplayerregistry):
    lyrs = get_lyrs_on_map(maplayerregistry)
    lyrs_vect = [lyr for lyr in lyrs if lyr.type() == 0]
    return lyrs_vect
  
  
#check if layer is a linestring
def is_lyr_a_line(lyr):
    try:
      return lyr.geometryType() == 1
    
    except:
      return False 


#find layer by its id on map
def get_lyr_by_id(maplayerregistry, id):
    return maplayerregistry.mapLayer(id)


#get layer geom by feature id
def get_geom_by_id(layer, fid):
    feats = get_feat_byid(layer, [fid])
    if len(feats)>0:
      return feats[0].geometry()
    
    
#find features for list of id    
def get_feat_byid(layer, ids):
    feats = []
    for id in ids:
      request = QgsFeatureRequest(id)
      feats.append(layer.getFeatures(request).next())
    return feats   
  

#check if any lines feature in map are editable  
def lines_on_map_are_editable(maplayerregistry):
    if len(get_lyrs_line_editable(maplayerregistry)) > 0:
      return True
    
    else:
      return False
  
  
#get the lines editable layer in maps  
def get_lyrs_line_editable(maplayerregistry):
    lyrs_line = get_lyrs_line_on_map(maplayerregistry)
    lyrs_line_editable = [lyr for lyr in lyrs_line if lyr.isEditable()]
    return lyrs_line_editable
    
#     lines_editable_lyr = []
#     for id in lyrid_list:
#       layer = get_lyr_by_id(maplayerregistry, id)
#       if layer.isEditable():
#         lines_editable_lyr.append(layer)
#     
#     return lines_editable_lyr
    
    
#get feature intesecting a given bbox (is a feature bounding box)    
def get_feats_on_bbox(layer, bbox):
    index = QgsSpatialIndex(layer.getFeatures())
    feats_int = index.intersects(bbox)
    return feats_int
  
  
#get feature bounding box 
def get_feat_bbox(geom, tolerance=0):
    bbox = geom.boundingBox()
    if tolerance > 0:
      pass
    return bbox
  

#get the intersection point of two feature
def get_intersection_points(targ_geom, ref_geom):
    int_geom = targ_geom.intersection(ref_geom)
    if int_geom.isMultipart():
      return int_geom.asMultiPoint()
    return [int_geom.asPoint()]
  
  
#it round the coordinate to a given decimals       
def get_rounded_points(pts, decimal=3):
    pts_rounded =  []
    for p in pts:
      px_r = round(p.x(), decimal)
      py_r = round(p.y(), decimal)
      pr = QgsPoint(px_r, py_r)
      pts_rounded.append(pr)
      
    return pts_rounded
  
  
#get singles part geometries
def get_singles_part_geometries(geom):
    multiGeom = QgsGeometry()
    sngl_geoms = []
    if geom.type() == QGis.Point:
        if geom.isMultipart():
            multiGeom = geom.asMultiPoint()
            for i in multiGeom:
                sngl_geoms.append(QgsGeometry().fromPoint(i))
        else:
            sngl_geoms.append(geom)
    elif geom.type() == QGis.Line:
        if geom.isMultipart():
            multiGeom = geom.asMultiPolyline()
            for i in multiGeom:
                sngl_geoms.append(QgsGeometry().fromPolyline(i))
        else:
            sngl_geoms.append(geom)
    elif geom.type() == QGis.Polygon:
        if geom.isMultipart():
            multiGeom = geom.asMultiPolygon()
            for i in multiGeom:
                sngl_geoms.append(QgsGeometry().fromPolygon(i))
        else:
            sngl_geoms.append(geom)
    return sngl_geoms
    
    
#create feature from a given feat template and a list of geom
def create_feature_from_tmpl(feat, geom):
    f_attrs = feat.attributes()
    f = QgsFeature()
    f.setAttributes(f_attrs)
    f.setGeometry(geom)
    return f
    