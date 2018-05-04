from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# initialize Qt resources from file resources.py
import resources

from scripts.lineLayer import LineLayer
from scripts.utils import (MyLog)
from scripts.geo_utils import (get_lyrs_line_on_map
                               ,is_lyr_a_line
                               ,lines_on_map_are_editable
                               ,get_lyrs_line_editable)
from scripts.settings import APP_CONFIG

class LineEditor:

  def __init__(self, iface):
    # save reference to the QGIS interface
    self.iface = iface
    self.actions = []
    self.plugin_name = u"LineEditor"
    
    #TOOLBAR
    self.toolbar = self.iface.addToolBar(self.plugin_name)
    self.toolbar.setObjectName(self.plugin_name)
    
    #PLUGIN INIT
    self.maplayerregistry = QgsMapLayerRegistry.instance()
    self.currentLayer = None
    self.linelayer_list = {}
  
  
  def initGui(self):
    print "init"
    
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
    self.set_linelayer_list()
    
    self._attach_events()
    

  #lanciata quando il plugin viene rimosso
  def unload(self):
    print "unload"
    
    #check if any layer is editable and switch off editing
    editable_layers = get_lyrs_line_editable(self.maplayerregistry)
    for l in editable_layers:
      self.iface.setActiveLayer(l)
      l.rollBack()
    
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
    
    
  def attach_lines_lyrid_to_toolevent(self):
    for id, lc in self.linelayer_list.iteritems():
      #connect to layer startediting and stopediting
      lc.layer.editingStarted.connect(self.on_editingStarted)
      lc.layer.editingStopped.connect(self.on_editingStoped)
    
    
  def detach_lines_lyrid_to_toolevent(self):
    for id, lc in self.linelayer_list.iteritems():
      #connect to layer startediting and stopediting
      lc.layer.editingStarted.disconnect(self.on_editingStarted)
      lc.layer.editingStopped.disconnect(self.on_editingStoped)
  
  '''
  active/disactive enable/disable plugins buttons
  '''
  def active_deactive_action_split(self):
    action_is_checked = self.action_split.isChecked()
    print "active_deactive_action_split %s" % action_is_checked 
    self.set_is_action_active_on_layer(action_is_checked, "action_split")
    
    
  def active_deactive_action_selfint(self):
    action_is_checked = self.action_selfint.isChecked()
    print "active_deactive_action_selfint %s" % action_is_checked 
    self.set_is_action_active_on_layer(action_is_checked, "action_selfint")
    
    
  def active_deactive_action_simpl(self):
    action_is_checked = self.action_simpl.isChecked()
    print "active_deactive_action_simpl %s" % action_is_checked 
    self.set_is_action_active_on_layer(action_is_checked, "action_simpl")
    
    
  def enable_disable_buttons(self, enable):
    if APP_CONFIG["allow_split_button"]: self.action_split.setEnabled(enable)
    if APP_CONFIG["allow_selfint_button"]: self.action_selfint.setEnabled(enable)
    if APP_CONFIG["allow_simpl_button"]: self.action_simpl.setEnabled(enable)
    
    
  def uncheck_buttons(self):    
    self.action_split.setChecked(False)
    self.action_selfint.setChecked(False)
    self.action_simpl.setChecked(False)
    
    
  def set_buttons(self, l_cfg):
    self.action_split.setChecked(l_cfg.is_action_split_active)
    self.action_selfint.setChecked(l_cfg.is_action_selfint_active)
    self.action_simpl.setChecked(l_cfg.is_action_simpl_active)
    
    
  '''
  set layer buttons state
  '''
  def set_is_action_active_on_layer(self, is_active, prop_name):
    l_id = self.currentLayer.id()
    if l_id in self.linelayer_list:
      properties = {
        "action_split": self.linelayer_list[l_id].is_action_split_active,
        "action_selfint": self.linelayer_list[l_id].is_action_selfint_active,
        "action_simpl": self.linelayer_list[l_id].is_action_simpl_active
      }
      prop = properties.get(prop_name)
      prop = is_active
           
      
  def _attach_events(self):    
    self.iface.currentLayerChanged.connect(self.on_currentLayerChanged)
    self.attach_lines_lyrid_to_toolevent()
    self.maplayerregistry.layersAdded.connect(self.on_layersAdded)
    self.maplayerregistry.layersWillBeRemoved.connect(self.on_layerWillRemoved)
    
  
  def _detach_events(self):
    self.maplayerregistry.layersWillBeRemoved.disconnect(self.on_layerWillRemoved)
    self.maplayerregistry.layersAdded.disconnect(self.on_layersAdded)
    self.detach_lines_lyrid_to_toolevent()
    self.iface.currentLayerChanged.disconnect(self.on_currentLayerChanged)
          
      
  def set_linelayer_list(self):
    lyrs = get_lyrs_line_on_map(self.maplayerregistry)
    for l in lyrs:
      lc = LineLayer(self.iface, l)
      self.linelayer_list[l.id()] = lc
      
      
  def on_clickSettings(self):
    print "on_click_settings"
    
      
  def on_currentLayerChanged(self, layer):
    if not layer: return #it may happens when we close the project
    MyLog.log_info("on current layer changed")
    self.currentLayer = layer
    l_id = layer.id()
    
    #configure slit button
    if l_id in self.linelayer_list:
      self.action_split.setChecked(self.linelayer_list[l_id].is_action_split_active)
      self.action_split.setEnabled(layer.isEditable())
      
        
  def on_layersAdded(self, layers):
    MyLog.log_info("on layer added")
    for l in layers:
      print l  
      if is_lyr_a_line(l):
        lc = LineLayer(self.iface, l)
        self.linelayer_list[l.id()] = lc
        l.editingStarted.connect(self.on_editingStarted)
        l.editingStopped.connect(self.on_editingStoped)
    
    
  def on_layerWillRemoved(self, layer_id):
    MyLog.log_info("on layer removed")
    for l_id in layer_id:
      self.linelayer_list.pop(l_id, None)
      
      
  def on_editingStarted(self):
    MyLog.log_info("edit started")
    l_id = self.currentLayer.id()
    if not l_id in self.linelayer_list: return #if is not a line layer
    l_cfg = self.linelayer_list[l_id]
    
    #enable buttons on plugins
    self.enable_disable_buttons(True)
    #set the split button based on the last configured for the layer
    self.set_buttons(l_cfg)
    
    #attach event for edit line
    l_cfg.attach_editor_event() 
    
      
  def on_editingStoped(self):
    MyLog.log_info("edit stoped")
    #manage buttons
    self.uncheck_buttons()
    self.enable_disable_buttons(False)
    
    l_id = self.currentLayer.id()
    if not l_id in self.linelayer_list: return #if is not a line layer
    l_cfg = self.linelayer_list[l_id]
      
    #attach event for edit line and set split setting
    l_cfg.reset_buttons_state()
    l_cfg.detach_editor_event() 