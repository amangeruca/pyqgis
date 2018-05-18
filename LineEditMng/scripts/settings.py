import os.path
from qgis.core import QgsProject

PLUGIN_PATH = os.path.dirname(os.path.dirname(__file__))
APP_CONFIG = {}
    

with open(os.path.join(PLUGIN_PATH, 'config.ini')) as f:
    for line in f.readlines():
        if 'author:' in line:
            APP_CONFIG["author"] = line.split('author:')[1].strip()
            
        elif 'app_name:' in line:
            APP_CONFIG["app_name"] = line.split('app_name:')[1].strip()

        elif 'enable_print:' in line:
            APP_CONFIG["enable_print"] = eval(line.split('enable_print:')[1].strip())
# 
#         elif 'system_settings:' in line:
#             APP_CONFIG["system_settings"] = eval(line.split('system_settings:')[1].strip())

# line editor permissions
        elif 'allow_settings:' in line:
            APP_CONFIG["allow_settings"] = eval(line.split('allow_settings:')[1].strip())
            
        elif 'allow_split_button:' in line:
            APP_CONFIG["allow_split_button"] = eval(line.split('allow_split_button:')[1].strip())
            
        elif 'allow_selfint_button:' in line:
            APP_CONFIG["allow_selfint_button"] = eval(line.split('allow_selfint_button:')[1].strip())
            
        elif 'allow_simpl_button:' in line:
            APP_CONFIG["allow_simpl_button"] = eval(line.split('allow_simpl_button:')[1].strip())
            
# line editor default
        elif 'check_split_button:' in line:
            APP_CONFIG["check_split_button"] = eval(line.split('check_split_button:')[1].strip())
            
        elif 'check_selfint_button:' in line:
            APP_CONFIG["check_selfint_button"] = eval(line.split('check_selfint_button:')[1].strip())
            
        elif 'check_simpl_button:' in line:
            APP_CONFIG["check_simpl_button"] = eval(line.split('check_simpl_button:')[1].strip())
            
# function settings
        elif 'split_tolerance:' in line:
            APP_CONFIG["split_tolerance"] = float(line.split('split_tolerance:')[1].strip())

        elif 'simpl_tolerance:' in line:
            APP_CONFIG["simpl_tolerance"] = float(line.split('simpl_tolerance:')[1].strip())

        elif 'rounding_digit:' in line:
            APP_CONFIG["rounding_digit"] = int(line.split('rounding_digit:')[1].strip())
            
            
def readProjSettings(k, def_value):
    proj = QgsProject.instance()
    value = proj.readEntry(APP_CONFIG["app_name"], k, def_value)[0]
    return value
            
            
def readBoolProjSettings(k, def_value):
    proj = QgsProject.instance()
    value = proj.readBoolEntry(APP_CONFIG["app_name"], k, def_value)[0]
    return value
            
            
def readreadNumProjSettings(k, def_value):
    proj = QgsProject.instance()
    value = proj.readNumEntry(APP_CONFIG["app_name"], k, def_value)[0]
    return value
            
            
def readDoubleProjSettings(k, def_value):
    proj = QgsProject.instance()
    value = proj.readDoubleEntry(APP_CONFIG["app_name"], k, def_value)[0]
    return value
  
  
def storeProjSettings(k, value):
    proj = QgsProject.instance()
    proj.writeEntry(APP_CONFIG["app_name"], k, value)
    
    
def removeProjSettings(k):
    proj = QgsProject.instance()
    proj.removeEntry(APP_CONFIG["app_name"], k)
    

def set_parameter(par_name, par_value, par_type=None):
#     #cast the value
#     if par_type=="bool":
#       value = eval(par_value)
#     elif par_type=="int":
#       value = int(par_value)
#     elif par_type=="float":
#       value = float(par_value)
#     else:
#       value=par_value
      
    storeProjSettings(par_name, unicode(par_value))
#     APP_CONFIG[par_name] = value
      
      
def get_parameter(key):
    def_value = APP_CONFIG[key]
    
    if isinstance(def_value, bool):
      proj_value = eval(readDoubleProjSettings(key, def_value))
    elif isinstance(def_value, float):
      proj_value = float(readDoubleProjSettings(key, def_value))
    elif isinstance(def_value, int):
      proj_value = int(readreadNumProjSettings(key, def_value))
    else:
      proj_value = readProjSettings(key, def_value)
      
    return proj_value
        
      