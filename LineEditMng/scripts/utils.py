from qgis.core import QgsMessageLog
from settings import APP_CONFIG

def logonqgis(msg, enable_print=False, level=QgsMessageLog.CRITICAL):
    QgsMessageLog.logMessage(msg, APP_CONFIG['log_title'], level=level)
    if enable_print:
      print_msg(msg)

    
def log_info(msg, enable_print = APP_CONFIG['enable_print']):
    logonqgis(msg, enable_print, level=QgsMessageLog.INFO)

    
def log_warn(msg, enable_print = APP_CONFIG['enable_print']):
    logonqgis(msg, enable_print, level=QgsMessageLog.WARNING)


def log_error(msg, enable_print = APP_CONFIG['enable_print']):
    logonqgis(msg, enable_print)
    
    
def print_msg(msg):
    try:
      print msg
      
    except Exception as e:
      logonqgis("Error on print: %s" % str(e))