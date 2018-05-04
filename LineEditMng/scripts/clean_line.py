from geo_utils import (get_geom_by_id,
                       get_singles_part_geometries)
from settings import APP_CONFIG
                       
def do_clean_geom(feat, check_self_int, check_simplify):
    #get target geom
    targ_geom = feat.geometry()
    cleaned_geoms = [targ_geom]
    
    #do resolve self intersection and return geometry
    if check_self_int:
        validateResults = targ_geom.validateGeometry()
        if len(validateResults):
            cleaned_geoms = do_resolve_self_int(targ_geom)
    
    #get singlePartGeom
    singl_geoms = []
    for cgeom in cleaned_geoms:
        sgeom = get_singles_part_geometries(cgeom)
        singl_geoms.append(sgeom)
    
    cleaned_geoms = singl_geoms
    
    #do perform simplify
    if check_simplify:
        simpl_geoms = []
        for cgeom in cleaned_geoms:
            simpgeom = do_simplify_geom(cgeom)
            simpl_geoms.append(simpgeom)
        
        cleaned_geoms = simpl_geoms 
    
    return cleaned_geoms


def do_resolve_self_int(geom):
    resolved_geoms = []
    
    #intersect geom with its self gives segments every vertices splitted at intersection with other segments ordered from starting point
    segsint = geom.intersection(geom).asMultiPolyline
    
    #if return just a segments return or none return
    if len(segsint)==0: return [geom]
    if len(segsint)<4: return segsint #min segments it should be five we write 4 just to be sure 
    
    #Cicle on segments and combine adjacent geometry without intersect
    targ_geom = None
    for seg in segsint:
        if targ_geom is None:
            targ_geom = seg
                
        #check if end point of the current geom intersects more than one segments
        ref_geoms = list(segsint).remove(seg)
        result = isSegAtIntersection(seg, refs_geom)
        
        #if it did i save the targ_geom and reset it
        #when i have an intersection a can not combine the geometry with other so i save it  
        if result:
            resolved_geoms.append(targ_geom)
            targ_geom = None
            
        #otherwise i combine with the seg geometry 
        else:
            targ_geom.combine(seg)
            
    return resolved_geoms
        
        
def isSegAtIntersection(seg, refs_geom):
    endPt = seg.asPolyline[-1]
    endPtBuff = QgsGeometry.fromPoint(endPt).buffer(APP_CONFIG["split_tolerance"], 10)
    
    #loop throught refs and test if are more than 1
    tot_ints = 0
    for rgeom in refs_geom:
        if (endPtBuff.intersects(rgeom)):
            tot_ints += 1
        if tot_ints>1: break
        
    return (tot_ints > 1)


def do_simplify_geom(geom):
    simpl_geom = geom.simplify(APP_CONFIG["simpl_tolerance"])
    return simpl_geom
            
    
    
    
    