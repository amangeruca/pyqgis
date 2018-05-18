import os

from PyQt4 import QtGui, uic
from ..scripts.settings import APP_CONFIG, get_parameter, set_parameter, removeProjSettings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'SettingsDialog.ui'))

class SettingsDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(SettingsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        
    def showEvent(self, t):
        print "showEvent"
        self.splitTolerance.setValue(get_parameter("split_tolerance"))
        self.simplTolerance.setValue(get_parameter("simpl_tolerance"))
        
        
    def accept(self):
        set_parameter("split_tolerance", self.splitTolerance.value(), "float")
        set_parameter("simpl_tolerance", self.simplTolerance.value(), "float")
        self.close()
        
        
    def on_restoreButtonClicked(self):
        print "on_restoreButtonClicked"
        self.splitTolerance.setValue(APP_CONFIG["split_tolerance"])
        self.simplTolerance.setValue(APP_CONFIG["simpl_tolerance"])
        removeProjSettings("split_tolerance")
        removeProjSettings("simpl_tolerance")
        

        
    
    