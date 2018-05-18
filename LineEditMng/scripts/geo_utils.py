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
  
  
#get singles part geometries if geometry. If alwaysreturn if geometry is single geometry return the same geometry
def get_singles_part_geometries(geom):
    if geom.isMultipart():
        sngl_geoms = []        
        if geom.type() == QGis.Point:
            multiGeom = geom.asMultiPoint()
            for i in multiGeom:
                sngl_geoms.append(QgsGeometry().fromPoint(i))
                
        elif geom.type() == QGis.Line:
            multiGeom = geom.asMultiPolyline()
            for i in multiGeom:
                sngl_geoms.append(QgsGeometry().fromPolyline(i))
                
        elif geom.type() == QGis.Polygon:
            multiGeom = geom.asMultiPolygon()
            for i in multiGeom:
                sngl_geoms.append(QgsGeometry().fromPolygon(i))
                    
        return sngl_geoms
    
    else:
        return [geom]

        
    
#create feature from a given feat template and a list of geom
def create_feature_from_tmpl(layer, feat, geom):
    #defines attributes
    i_pks = layer.pkAttributeList()
    f_attrs = feat.attributes()
    
    #set to none all the pk field so they will setted automaticaly
    if len(i_pks):
      for i in i_pks:
        f_attrs[i] = None
    
    #create feature
    f = QgsFeature()
    f.setAttributes(f_attrs)
    f.setGeometry(geom)
    return f
  
  
#check if a point is on end or start point of a line
def point_touch_line(pt, line, tolerance=None):
    line_vrts = line.asPolyline()
    if len(line_vrts)<2: return
    
    for vrt in line_vrts[::len(line_vrts)-1]:
      vrt_geom = QgsGeometry.fromPoint(vrt)
      if tolerance is not None:
        pt = pt.buffer(tolerance, 10)
      if pt.intersects(vrt_geom): return True
  
  
#add or mouve a vertex on line at specific position (within a tolerance)
def add_close_vertex_to_linegeom(geom, pt, tolerance=0.001):
    #get the minimun distance form point to line
    dist_line_sqr, pt_on_line, next_vrt = geom.closestSegmentWithContext(pt)
    if not (0 <= dist_line_sqr <= tolerance**2) : return
      
    dist_to_vrt, vrt = geom.closestVertexWithContext(pt_on_line)
    #if the distance from the point on line and closest vertex > tolerance add new vertex else move the existing
    if dist_to_vrt > tolerance**2:
        geom.insertVertex(pt.x(), pt.y(), next_vrt)    
    else:
        geom.moveVertex(pt.x(), pt.y(), vrt)    
        
        
#return a list of linestring from geoprocessing results      
def get_geomListFromCollection(collection):
    geomList = collection.asMultiPolyline()
    collection_asLine = collection.asPolyline()
    if len(collection_asLine) > 0: geomList.append(collection_asLine)
    return geomList    
        
        
def geom_difference_to_line_list(geom_targ, geom_diff):
    geom_result = geom_targ.difference(geom_diff)
    geoms_list = get_geomListFromCollection(geom_result)
    return geoms_list
        
        
def geom_intersection_to_line_list(geom_targ, geom_diff):
    geom_result = geom_targ.intersection(geom_diff)
    geoms_list = get_geomListFromCollection(geom_result)
    return geoms_list
    
  
    