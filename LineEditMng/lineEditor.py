from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# initialize Qt resources from file resources.py
import resources

from ui.settings_dialog import SettingsDialog
from scripts.lineLayer import LineLayer
from scripts.utils import (MyLog)
from scripts.geo_utils import (get_lyrs_line_on_map
                               ,is_lyr_a_line
                               ,lines_on_map_are_editable
                               ,get_lyrs_line_editable)
from scripts.settings import APP_CONFIG

class LineEditor:

  def __init__(self, iface):
    print "__init__"
    
    # save reference to the QGIS interface
    self.iface = iface
    self.actions = []
    self.plugin_name = u"LineEditor"
    
    #TOOLBAR
    self.toolbar = self.iface.addToolBar(self.plugin_name)
    self.toolbar.setObjectName(self.plugin_name)
    
    #PLUGIN INIT
    self.maplayerregistry = QgsMapLayerRegistry.instance()
    self.stop_currentEditingSession() #CHECK IF SOMES LAYER ARE ON EDIT AND STOP IT. It may cause conflict with signal
    self.currentLayer = self.iface.activeLayer()  
    self.linelayer_list = self.set_linelayer_list()
    self.dialogSettings = SettingsDialog()
    
    #attach event
    self._attach_events()
  
  
  def initGui(self):
    print "initGui"
    
    #add action button to menu
    icon_split = ":/plugins/lineeditor/icons/split.png"
    self.action_split = self.add_action(icon_split, "Split at intersection", self.active_deactive_action_split, enabled_flag=False)
    
    #add action button to menu
    icon_selfint = ":/plugins/lineeditor/icons/selfint.png"
    self.action_selfint = self.add_action(icon_selfint, "Resolve self-intersection", self.active_deactive_action_selfint, enabled_flag=False)
    
    #add action button to menu
    icon_simpl = ":/plugins/lineeditor/icons/simpl.png"
    self.action_simpl = self.add_action(icon_simpl, "Split at intersection", self.active_deactive_action_simpl, enabled_flag=False)
    
    #add action button to menu
    icon_settings = ":/plugins/lineeditor/icons/settings.png"
    self.action_settings = self.add_action(icon_settings, "Split at intersection", self.on_clickSettings, checkable_flag=False, enabled_flag=APP_CONFIG["allow_settings"])

    # connect to signal renderComplete which is emitted when canvas
    # rendering is done
    #QObject.connect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)
    

  #lanciata quando il plugin viene rimosso
  def unload(self):
    print "unload"

    #check if any layer is editable and switch off editing
    self.stop_currentEditingSession()
    
    #remove all the istance of LineLayer
    self.linelayer_list.clear()
    
    
    """Removes the plugin menu item and icon from QGIS GUI."""
    for action in self.actions:
        self.iface.removeToolBarIcon(action)
        

    #detach events on map
    self._detach_events()
    
    # remove the toolbar
    del self.toolbar

    
  def add_action(
      self,
      icon_path,
      text,
      callback,
      checkable_flag=True,
      enabled_flag=True,
      add_to_menu=False,
      add_to_toolbar=True,
      status_tip=None,
      whats_this=None,
      parent=None):
      """Add a toolbar icon to the toolbar.

      :param icon_path: Path to the icon for this action. Can be a resource
          path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
      :type icon_path: str

      :param text: Text that should be shown in menu items for this action.
      :type text: str

      :param callback: Function to be called when the action is triggered.
      :type callback: function

      :param checkable_flag: Indicate toogle options enabled
      :type checkable_flag: bool

      :param enabled_flag: A flag indicating if the action should be enabled
          by default. Defaults to True.
      :type enabled_flag: bool

      :param add_to_menu: Flag indicating whether the action should also
          be added to the menu. Defaults to True.
      :type add_to_menu: bool

      :param add_to_toolbar: Flag indicating whether the action should also
          be added to the toolbar. Defaults to True.
      :type add_to_toolbar: bool

      :param status_tip: Optional text to show in a popup when mouse pointer
          hovers over the action.
      :type status_tip: str

      :param parent: Parent widget for the new action. Defaults None.
      :type parent: QWidget

      :param whats_this: Optional text to show in the status bar when the
          mouse pointer hovers over the action.

      :returns: The action that was created. Note that the action is also
          added to self.actions list.
      :rtype: QAction
      """

      icon = QIcon(icon_path)
      action = QAction(icon, text, parent)
      action.triggered.connect(callback)
      action.setEnabled(enabled_flag)
      action.setCheckable(checkable_flag)

      if status_tip is not None:
          action.setStatusTip(status_tip)

      if whats_this is not None:
          action.setWhatsThis(whats_this)

      if add_to_toolbar:
          self.toolbar.addAction(action)

      if add_to_menu:
          self.iface.addPluginToDatabaseMenu(
              self.menu,
              action)

      self.actions.append(action)

      return action

  
  '''
  active/deactivate enable/disable plugins buttons
  '''
  def active_deactive_action_split(self):
    action_is_checked = self.action_split.isChecked()
    print "active_deactive_action_split %s" % action_is_checked 
    self.set_is_action_active_on_layer(action_is_checked, "split")
    
    
  def active_deactive_action_selfint(self):
    action_is_checked = self.action_selfint.isChecked()
    print "active_deactive_action_selfint %s" % action_is_checked 
    self.set_is_action_active_on_layer(action_is_checked, "selfint")
    
    
  def active_deactive_action_simpl(self):
    action_is_checked = self.action_simpl.isChecked()
    print "active_deactive_action_simpl %s" % action_is_checked 
    self.set_is_action_active_on_layer(action_is_checked, "simpl")
    
    
  def enable_disable_buttons(self, enable):
    if APP_CONFIG["allow_split_button"]: self.action_split.setEnabled(enable)
    if APP_CONFIG["allow_selfint_button"]: self.action_selfint.setEnabled(enable)
    if APP_CONFIG["allow_simpl_button"]: self.action_simpl.setEnabled(enable)
    
    
  def uncheck_buttons(self):    
    self.action_split.setChecked(False)
    self.action_selfint.setChecked(False)
    self.action_simpl.setChecked(False)
    
    
  def set_buttons(self, lstate):
    self.action_split.setChecked(lstate["is_action_split_checked"])
    self.action_selfint.setChecked(lstate["is_action_selfint_checked"])
    self.action_simpl.setChecked(lstate["is_action_simpl_checked"])
    
    
  '''
  set layer buttons state
  '''
  def set_is_action_active_on_layer(self, is_active, prop_name):
    print "set action"
    l_id = self.currentLayer.id()
    if l_id in self.linelayer_list:
        self.linelayer_list[l_id].set_state(prop_name, is_active)
           
      
  def _attach_events(self):    
    self.iface.currentLayerChanged.connect(self.on_currentLayerChanged)
    self.maplayerregistry.layersAdded.connect(self.on_layersAdded)
    self.maplayerregistry.layersWillBeRemoved.connect(self.on_layerWillRemoved)
    
  
  def _detach_events(self):
    self.maplayerregistry.layersWillBeRemoved.disconnect(self.on_layerWillRemoved)
    self.maplayerregistry.layersAdded.disconnect(self.on_layersAdded)
    self.iface.currentLayerChanged.disconnect(self.on_currentLayerChanged)
          
      
  def set_linelayer_list(self):
    linelayer_list = {}
    lyrs = get_lyrs_line_on_map(self.maplayerregistry)
    for l in lyrs:
      lc = LineLayer(self, l)
      linelayer_list[l.id()] = lc
    return linelayer_list
      
      
  def stop_currentEditingSession(self):
    #check if any layer is editable and switch off editing
    editable_layers = get_lyrs_line_editable(self.maplayerregistry)
    for l in editable_layers:
#       self.iface.setActiveLayer(l)
#       l.rollBack()
      l.commitChanges()
#     
#     for l_id in self.linelayer_list:
#       l = self.linelayer_list[l_id].layer
#       if l.isEditable(): l.commitChanges()
      
      
  def on_clickSettings(self):
    print "on_click_settings"
    self.dialogSettings.show()
    
      
  def on_currentLayerChanged(self, layer):
    if not layer: return #it may happens when we close the project
    MyLog.log_info("on current layer changed")
    self.currentLayer = layer
    l_id = layer.id()
    
    #configure slit button
    if l_id in self.linelayer_list:
      l_isEditable = layer.isEditable()
      #enable buttons if layer is editable
      self.enable_disable_buttons(l_isEditable)
      
      #if layer is editable set buttons else reset it
      if l_isEditable: 
        self.set_buttons(self.linelayer_list[l_id].layer_state)
      else:
        self.uncheck_buttons()
        
    else:
      self.enable_disable_buttons(False)
      self.uncheck_buttons()
      
        
  def on_layersAdded(self, layers):
    MyLog.log_info("on layer added")
    for l in layers:
      print l  
      if is_lyr_a_line(l):
        lc = LineLayer(self, l)
        self.linelayer_list[l.id()] = lc
    
    
  def on_layerWillRemoved(self, layer_id):
    MyLog.log_info("on layer removed")
    for l_id in layer_id:
      self.linelayer_list.pop(l_id, None)
      
      
  def on_layerEditStarted(self, lstate):
    print "on layerEditStarted"

#     MyLog.log_info("on edit started")
#     l_id = self.currentLayer.id()
#     if not l_id in self.linelayer_list: return #if is not a line layer
#     l_cfg = self.linelayer_list[l_id]
    
    #enable buttons on plugins
    self.enable_disable_buttons(True)
    #set the split button based on the last configured for the layer
    self.set_buttons(lstate)
#     
    #attach event for edit line
#     l_cfg.on_layerStartEditing() 
    
      
  def on_layerEditStoped(self):
    print "on layerEditStoped"
    
    #manage buttons
    self.uncheck_buttons()
    self.enable_disable_buttons(False)
    
#     l_id = self.currentLayer.id()
#     if not l_id in self.linelayer_list: return #if is not a line layer
#     l_cfg = self.linelayer_list[l_id]
#       
#     #attach event for edit line and set split setting
#     #l_cfg.reset_buttons_state()
#     l_cfg.on_layerStopEditing() 