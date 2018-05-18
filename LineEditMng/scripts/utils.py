from qgis.core import QgsMessageLog
from settings import APP_CONFIG

class MyLog():
    @staticmethod
    def logonqgis(msg, enable_print=False, level=QgsMessageLog.CRITICAL):
        QgsMessageLog.logMessage(msg, APP_CONFIG['app_name'], level=level)
        if enable_print:
          MyLog.print_msg(msg)
    
    
    @staticmethod    
    def log_info(msg, enable_print = APP_CONFIG['enable_print']):
        MyLog.logonqgis(msg, enable_print, level=QgsMessageLog.INFO)
    
    
    @staticmethod    
    def log_warn(msg, enable_print = APP_CONFIG['enable_print']):
        MyLog.logonqgis(msg, enable_print, level=QgsMessageLog.WARNING)
    
    
    @staticmethod
    def log_error(msg, enable_print = APP_CONFIG['enable_print']):
        MyLog.logonqgis(msg, enable_print)
        
        
    @staticmethod    
    def print_msg(msg):
        try:
          print msg
          
        except Exception as e:
          MyLog.logonqgis("Error on print: %s" % str(e))