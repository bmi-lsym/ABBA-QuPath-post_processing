from javax.swing import JTabbedPane, JPanel, JFrame, JLabel, JSpinner, JSlider, JCheckBox, JColorChooser, JComboBox, SpinnerNumberModel, SpringLayout
from javax.swing.event import ChangeListener
from javax.swing import JMenuBar, JMenu, JMenuItem, JFileChooser, JDialog, JButton
from javax.swing.filechooser import FileFilter, FileNameExtensionFilter
from java.awt import Color, GridLayout, Container, Graphics, FlowLayout, Dimension
from java.awt.event import ActionListener
from string import *
from ij import IJ, WindowManager, ImagePlus, ImageStack, Prefs, ImageListener
from ij.plugin.frame import RoiManager
from ij.plugin import ChannelSplitter
from ij.gui import Roi, PolygonRoi, Overlay
from ij.process import FloatPolygon
from ij.measure import ResultsTable
from java.io import *
from ij.measure import Calibration
from Jama import Matrix
import math
import java
import jarray
import json
import random
import os
import sys

class OpenImageListener(ImageListener):
  def imageClosed(self, imp):
    global current_stack
    imp.removeImageListener(self)
    if (imp==current_stack.image_plus):
      current_stack.close(1)
  def imageUpdated(self, imp):
    global current_stack
    if (current_stack):
      current_stack.set_current_slice(imp.getCurrentSlice())
  def imageOpened(self, imp):
    pass


def text_and_spinner(txt, spin_list):
  lbl=JLabel(txt)
  #lbl.setBounds(20,20,0,0)
  lbl.setHorizontalAlignment(0)
  spin_model=SpinnerNumberModel(spin_list[0], spin_list[1], spin_list[2], spin_list[3])
  spinner=JSpinner(spin_model)
  #spinner.setBounds(20,50,20,0)
  spring_layout=SpringLayout()
  contentPane=Container()#fiber1_panel.getContentPane()
  contentPane.add(lbl)
  contentPane.add(spinner)
  contentPane.setLayout(spring_layout)
  #spring_layout.putConstraint(SpringLayout.WEST,lbl,5,SpringLayout.WEST,contentPane)
  spring_layout.putConstraint(SpringLayout.NORTH,lbl,4,SpringLayout.NORTH,contentPane)
  spring_layout.putConstraint(SpringLayout.WEST,spinner,3,SpringLayout.EAST,lbl)
  spring_layout.putConstraint(SpringLayout.NORTH,spinner,3,SpringLayout.NORTH,contentPane)
  spring_layout.putConstraint(SpringLayout.EAST,contentPane,10,SpringLayout.EAST,spinner)
  spring_layout.putConstraint(SpringLayout.SOUTH,contentPane,6,SpringLayout.SOUTH,spinner)
  return spinner, contentPane

def make_checkbox(txt, state):
  checkbox=JCheckBox(txt, state)
  spring_layout=SpringLayout()
  contentPane=Container()#fiber1_panel.getContentPane()
  contentPane.add(checkbox)
  contentPane.setLayout(spring_layout)
  spring_layout.putConstraint(SpringLayout.NORTH,checkbox,0,SpringLayout.NORTH,contentPane)
  spring_layout.putConstraint(SpringLayout.WEST,checkbox,75,SpringLayout.WEST,contentPane)
  spring_layout.putConstraint(SpringLayout.EAST,checkbox,10,SpringLayout.EAST,contentPane)
  spring_layout.putConstraint(SpringLayout.SOUTH,checkbox,20,SpringLayout.NORTH,contentPane)
  return checkbox, contentPane

class make_combo_button_dialog():
  global GUIframe
  def __init__(self, title, item_list, button_txt):
    d=JDialog(GUIframe , title, True)
    cb=JComboBox(item_list)
    self.combobox=cb
    self.item_index=-1
    self.dialog=d
    cb.setBounds(20,20,90,20)
    b=JButton(button_txt)
    b.setBounds(130,20,130,20)
    b.addActionListener(Listener_combo_button(self.dialog, self))
    d.add(cb)
    d.add(b)
    d.setLayout(None)
    d.setSize(320,110)
    d.setMinimumSize(Dimension(320,110))
    d.pack()
    self.dialog.setVisible(False)
  def button_pressed(self):
    self.item_index=self.combobox.getSelectedIndex()
  def reset(self):
    self.item_index=-1
    self.dialog.setVisible(True)
  def close(self):
    del self

class Listener_combo_button(ActionListener):
  def __init__(self, dialog, dialog_obj):
    self.dialog = dialog
    self.dialog_obj=dialog_obj
  def actionPerformed(self, event):
    self.dialog_obj.button_pressed()
    self.dialog.setVisible(False)




class make_thresholding_dialog():
  global GUIframe
  def __init__(self, imp, title, slider1_txt, slider1_values, slider2_txt, slider2_values, slider3_txt, slider3_values, button_txt):
    self.imp=imp
    d=JDialog(GUIframe , title, True)
    self.dialog=d
    self.slider1_init=slider1_values
    self.slider2_init=slider2_values
    self.slider3_init=slider3_values
    self.slider1_val=slider1_values[2]
    self.slider2_val=slider2_values[2]
    self.slider3_val=slider3_values[2]
    self.slider1=JSlider(slider1_values[0],slider1_values[1],slider1_values[2])
    self.slider2=JSlider(slider2_values[0],slider2_values[1],slider2_values[2])
    self.slider3=JSlider(slider3_values[0],slider3_values[1],slider3_values[2])
    spin_model1=SpinnerNumberModel(slider1_values[2], slider1_values[0], slider1_values[1], (slider1_values[1]-slider1_values[0])/20)
    spin_model2=SpinnerNumberModel(slider2_values[2], slider2_values[0], slider2_values[1], (slider1_values[1]-slider1_values[0])/20)
    spin_model3=SpinnerNumberModel(slider3_values[2], slider3_values[0], slider3_values[1], 1)
    self.spinner1=JSpinner(spin_model1)
    self.spinner2=JSpinner(spin_model2)
    self.spinner3=JSpinner(spin_model3)

    slider_list=[self.slider1, self.slider2, self.slider3, self.spinner1, self.spinner2, self.spinner3]
    self.slider1.addChangeListener(Listener_thresholding(self, slider_list, 0))
    self.slider2.addChangeListener(Listener_thresholding(self, slider_list, 1))
    self.slider3.addChangeListener(Listener_thresholding(self, slider_list, 2))
    self.spinner1.addChangeListener(Listener_thresholding(self, slider_list, 3))
    self.spinner2.addChangeListener(Listener_thresholding(self, slider_list, 4))
    self.spinner3.addChangeListener(Listener_thresholding(self, slider_list, 5))

    self.slider1.setBounds(20,20,350,20)
    self.slider2.setBounds(20,20,350,20)
    self.slider3.setBounds(20,20,350,20)
    self.spinner1.setBounds(20,20,150,20)
    self.spinner2.setBounds(20,20,150,20)
    self.spinner3.setBounds(20,20,150,20)

    txt1 = JLabel(slider1_txt)
    txt2 = JLabel(slider2_txt)
    txt3 = JLabel(slider3_txt)
    txt4 = JLabel("          ")
    self.slider1_val_txt = JLabel(str(self.slider1_val))
    self.slider2_val_txt = JLabel(str(self.slider2_val))
    b_reset=JButton("Reset")
    b_reset.setBounds(20,20,130,20)
    b_reset.addActionListener(Listener_thresholding_reset(self.dialog, self))
    b=JButton(button_txt)
    b.setBounds(20,20,130,20)
    b.addActionListener(Listener_combo_button(self.dialog, self))
    layout = FlowLayout(FlowLayout.CENTER)
    d.setLayout(layout)
    d.setSize(480,200)
    #d.setMinimumSize(Dimension(450,150))

    d.add(txt1)
    d.add(self.slider1)
    d.add(self.spinner1)
    d.add(txt2)
    d.add(self.slider2)
    d.add(self.spinner2)
    d.add(txt3)
    d.add(self.slider3)
    d.add(self.spinner3)
    d.add(txt4)
    d.add(b_reset)
    d.add(b)
    self.status=-1
    self.imp.setSlice(self.slider3_init[2])
    #self.dialog.pack()
    self.dialog.setVisible(False)
  def button_pressed(self):
    self.status=1
  def reset_pressed(self):
    self.status=-1
    self.slider1.setValue(self.slider1_init[2])
    self.slider2.setValue(self.slider2_init[2])
    IJ.setRawThreshold(self.imp, self.slider1_val, self.slider2_val,"Red")
    self.dialog.setVisible(True)
    self.imp.setSlice(self.slider3_init[2])
  def update(self, slider, value):
    if (slider==0 or slider==3):
      self.slider1_val=value
      self.slider1_val_txt.setText(str(self.slider1_val))
    elif (slider==1 or slider==4):
      self.slider2_val=value
    elif (slider==2 or slider==5):
      self.slider3_val=value
    if (slider==0 or slider==1 or slider==3 or slider==4):
      IJ.setRawThreshold(self.imp, self.slider1_val, self.slider2_val,"Red")
  def close(self):
    del self

class Listener_thresholding_reset(ActionListener):
  def __init__(self, dialog, dialog_obj):
    self.dialog = dialog
    self.dialog_obj=dialog_obj
  def actionPerformed(self, event):
    self.dialog_obj.reset_pressed()

class Listener_thresholding(ChangeListener):
  def __init__(self, dialog_obj, sliders_list, order):
    self.group = sliders_list
    self.order = order
    self.dialog_obj=dialog_obj
  def stateChanged(self, event):
    if (self.order==0 or self.order==3):
      new_val=min(self.group[self.order].getValue(),self.dialog_obj.slider2_val)
      self.group[0].setValue(new_val)
      self.group[3].setValue(new_val)
    elif (self.order==1 or self.order==4):
      new_val=max(self.group[self.order].getValue(),self.dialog_obj.slider1_val)
      self.group[1].setValue(new_val)
      self.group[4].setValue(new_val)
    elif (self.order==2 or self.order==5):
      new_val=self.group[self.order].getValue()
      self.dialog_obj.imp.setSlice(new_val)
      self.group[2].setValue(new_val)
      self.group[5].setValue(new_val)
    self.dialog_obj.update(self.order,new_val)


class erode_dilate_dialog():
  global GUIframe
  def __init__(self, imp, ori_stack, title, slider1_txt, slider1_values, button_txt):
    self.imp=imp
    self.n_slices=self.imp.getNSlices()
    self.ori_stack=ori_stack
    self.slider_prefix=slider1_txt
    self.output_ROIs=[]
    d=JDialog(GUIframe , title, True)
    self.dialog=d
    self.slider1_init=slider1_values
    self.slider1_val=self.slider1_init[2]
    self.slider1=JSlider(slider1_values[0],slider1_values[1],slider1_values[2])
    self.slider1.addChangeListener(Listener_erode_dilate_slider(self))
    self.slider1.setBounds(20,20,350,20)

    self.txt1 = JLabel(self.slider_prefix+" " +str(self.slider1_val))

    b_reset=JButton("Reset")
    b_reset.setBounds(20,20,130,20)
    b_reset.addActionListener(Listener_thresholding_reset(self.dialog, self))
    b=JButton(button_txt)
    b.setBounds(20,20,130,20)
    b.addActionListener(Listener_combo_button(self.dialog, self))

    b_erode=JButton("Erode mask")
    b_erode.setBounds(20,20,130,20)
    b_erode.addActionListener(Listener_erode_dilate_buttons(self, "erode"))
    b_dilate=JButton("Dilate mask")
    b_dilate.setBounds(20,20,130,20)
    b_dilate.addActionListener(Listener_erode_dilate_buttons(self, "dilate"))

    layout = FlowLayout(FlowLayout.CENTER)
    d.setLayout(layout)
    d.setSize(380,160)
    #d.setMinimumSize(Dimension(450,150))

    d.add(self.txt1)
    d.add(self.slider1)
    d.add(b_erode)
    d.add(b_dilate)
    d.add(b_reset)
    d.add(b)
    self.status=-1
    #self.dialog.pack()
    self.imp.setSlice(self.slider1_init[2])
    self.dialog.setVisible(False)

  def button_pressed(self):
    for i in range(self.n_slices):
      self.imp.setSlice(i+1)
      IJ.run(self.imp, "Create Selection", "")
      #IJ.run(self.imp, "Make Inverse", "")
      roi = self.imp.getRoi().getInverse(self.imp)
      if (roi is None):
        roi=PolygonRoi([[0.0,0.0,0.0],[0.0,0.0,0.0]],Roi.FREEROI)
      roi.setPosition(i+1)
      self.output_ROIs.append(roi)
    self.status=1
  def reset_pressed(self):
    self.status=-1
    self.slider1.setValue(self.slider1_init[2])
    self.imp.setStack("Refining mask", self.ori_stack)
    self.imp.show()
    self.imp.setSlice(self.slider1_init[2])
    self.output_ROIs=[]
    self.dialog.setVisible(True)
  def update(self, value):
    self.slider1_val=value
    self.txt1.setText(self.slider_prefix+" " +str(self.slider1_val))
  def close(self):
    del self

class Listener_erode_dilate_buttons(ActionListener):
  def __init__(self, dialog_obj, op):
    self.op=op
    self.dialog_obj=dialog_obj
  def actionPerformed(self, event):
    current_slice=self.dialog_obj.imp.getCurrentSlice()
    for i in range(self.dialog_obj.n_slices):
      self.dialog_obj.imp.setSlice(i+1)
      if (self.op=="dilate"):
        self.dialog_obj.imp.getProcessor().erode()
      elif (self.op=="erode"):
        self.dialog_obj.imp.getProcessor().dilate()
    self.dialog_obj.imp.setSlice(current_slice)

class Listener_erode_dilate_slider(ChangeListener):
  def __init__(self, dialog_obj):
    self.dialog_obj=dialog_obj
  def stateChanged(self, event):
    new_val=self.dialog_obj.slider1.getValue()
    self.dialog_obj.imp.setSlice(new_val)
    self.dialog_obj.update(new_val)


class One_button_dialog():
  global GUIframe
  def __init__(self, title, message_text, button_text, dialog):
    self.title = title
    self.mesage_text=message_text
    self.button_text = button_text
    d = JDialog(GUIframe , title, True)
    layout = FlowLayout(FlowLayout.CENTER)
    d.setLayout(layout)
    d.setSize(300,150)
    b = JButton(button_text)
    b.addActionListener(Listener_dialog_one_button(d))
    txt = JLabel(message_text)
    d.add(txt)
    d.add(b)
    d.setVisible(False)
    self.dialog=d


class One_spinner_dialog():
  global GUIframe
  def __init__(self, title, spinner_text, button_text, value, min_val, max_val, incr_val, int_flag, dialog):
    self.title = title
    self.spinner_text=spinner_text
    self.button_text = button_text
    self.value=value
    self.min_val=min_val
    self.max_val=max_val
    self.increment=incr_val
    self.int_flag=int_flag
    spin_model=SpinnerNumberModel(value, min_val, max_val, incr_val)
    spinner=JSpinner(spin_model)
    self.spinner=spinner
    if self.int_flag:
      self.spinner.setValue(int( min(max(round(self.value),self.min_val),self.max_val) ))
      self.value=self.spinner.getValue()
    d = JDialog(GUIframe , title, True);
    layout = FlowLayout(FlowLayout.CENTER)
    d.setLayout(layout)
    d.setSize(300,150)
    txt = JLabel(spinner_text)
    d.add(txt)
    d.add(spinner)
    b = JButton(button_text)
    b.addActionListener(Listener_dialog_one_spinner(d, self))
    d.add(b)
    d.setVisible(False)
    self.dialog=d
  def button_pressed(self):
    self.value=self.spinner.getValue()
    if self.int_flag:
      self.spinner.setValue(int( min(max(round(self.value),self.min_val),self.max_val) ))
      self.value=self.spinner.getValue()


class Listener_dialog_one_spinner(ActionListener):
  def __init__(self, dialog, dialog_obj):
    self.dialog = dialog
    self.obj = dialog_obj
  def actionPerformed(self, event):
    self.obj.button_pressed()
    self.dialog.setVisible(False)


class Listener_dialog_one_button(ActionListener):
  def __init__(self, dialog):
    self.dialog = dialog
  def actionPerformed(self, event):
    self.dialog.setVisible(False)


class Two_buttons_dialog():
  global GUIframe
  def __init__(self, title, message_text, buttonYes_text, buttonNo_text, flag, dialog):
    self.title = title
    self.mesage_text=message_text
    self.buttonYes_text = buttonYes_text
    self.buttonNo_text = buttonNo_text
    self.flag = flag
    d = JDialog(GUIframe , title, True);
    layout = FlowLayout(FlowLayout.CENTER)
    d.setLayout(layout)
    d.setSize(300,150)
    b1 = JButton(buttonYes_text)
    b2 = JButton(buttonNo_text)
    b1.addActionListener(Listener_dialog_two_buttons(self, True))
    b2.addActionListener(Listener_dialog_two_buttons(self, False))
    txt = JLabel(message_text)
    d.add(txt)
    d.add(b1)
    d.add(b2)
    d.setVisible(False)
    self.dialog=d
  def yesPressed(self):
    self.flag=True
  def noPressed(self):
    self.flag=False

class Listener_dialog_two_buttons(ActionListener):
  def __init__(self, dialog, flag):
    self.dialog = dialog
    self.flag = flag
  def actionPerformed(self, event):
    if (self.flag):
      self.dialog.yesPressed()      
    else:
      self.dialog.noPressed()
    self.dialog.dialog.setVisible(False)


class Listener_checkboxes(ActionListener):
  def __init__(self, checkbox, order, fiber):
    self.checkbox = checkbox
    self.order = order
    self.fiber = fiber
  def actionPerformed(self, event):
    global GUIframe
    global current_stack

    chk = event.getSource()
    if self.order == 3 or self.order == 4:
      c = JColorChooser.showDialog(GUIframe,"Select a color",chk.getBackground())
      chk.setBackground(c)
      chk.setSelected(False)
      if current_stack is not None:
	      if self.order == 3:
	        current_stack.change_fiber_color(self.fiber,c)
	      elif self.order == 4:
	        current_stack.change_cone_color(self.fiber,c)
    elif current_stack is not None:
	    if self.order == 0:
	      current_stack.fill_cone(self.fiber,chk.isSelected())
	    elif self.order == 1:
	      current_stack.hide_fiber(self.fiber,chk.isSelected())
	    elif self.order == 2:
	      current_stack.hide_cone(self.fiber,chk.isSelected())


class Listener_spinners(ChangeListener):
  def __init__(self, spinners_list, order, fiber):
    self.group = spinners_list
    self.order = order
    self.fiber = fiber
  def stateChanged(self, event):
    global current_stack
    if current_stack is not None:
      if (self.order <= 5):
        vector = [self.group[i].getValue() for i in range(6)]
        current_stack.update_fiber_location(self.fiber, vector)
      elif (self.order==6):
        current_stack.update_fiber_shape(self.fiber, self.group[6].getValue(), self.group[11].getValue(), self.group[12].getValue())
      elif (self.order==10):
        current_stack.change_line_thickness(self.fiber,self.group[10].getValue())
      elif (self.order==7 or self.order==8 or self.order==9):
        current_stack.update_cone_shape(self.fiber, self.group[7].getValue(), self.group[8].getValue(), self.group[9].getValue(), self.group[11].getValue(), self.group[12].getValue())
      elif (self.order==11  or self.order==12):
        current_stack.update_fiber_shape(self.fiber, self.group[6].getValue(), self.group[11].getValue(), self.group[12].getValue())
        current_stack.update_cone_shape(self.fiber, self.group[7].getValue(), self.group[8].getValue(), self.group[9].getValue(), self.group[11].getValue(), self.group[12].getValue())


class Listener_menu(ActionListener):

  def __init__(self, menu_item, order):
    self.menu_item = menu_item
    self.order = order

  def actionPerformed(self, event):
    global GUIframe, rm
    global spinners, labels, pntrs
    global current_filepath, current_filename, fibers
    global current_stack
    global nofile_dialog, openanyways_dialog, closeanyways_dialog, overwriteanyways_dialog, exit_dialog, setNfibers_dialog

    item = event.getSource()

    if (self.order == 0): #Create new project
        if (current_stack):
          if (current_stack.unsaved):
            openanyways_dialog.dialog.setVisible(True)
            if (not openanyways_dialog.flag):
              proceed=False
        else:
          proceed=True
        if (proceed):
	      setNfibers_dialog.dialog.setVisible(True)
	      fibers=setNfibers_dialog.value
	      fc = JFileChooser()
	      ffilter = FileNameExtensionFilter("TIFF image stacks", ["tif", "tiff"])
	      fc.setFileFilter(ffilter)
	      i = fc.showDialog(GUIframe,"Open image stack")
	      if (i==JFileChooser.APPROVE_OPTION):
	        f = fc.getSelectedFile()
	        path = f.getPath()
	        fname = f.getName()
	        if (f.canRead() and f.isFile()):
	          if (current_stack):
	            current_stack.close(-1)
	          create_fiber_panes(fibers, spinners, labels, pntrs)
	          current_stack = stack_processing(GUIframe, fibers, path, fname)
	          current_filepath=path
	          current_filename=fname
	        else:
	          nofile_dialog.dialog.setVisible(True)

    if (self.order == 11): #Load project
        if (current_stack):
          if (current_stack.unsaved):
            openanyways_dialog.dialog.setVisible(True)
            if (not openanyways_dialog.flag):
              proceed=False
        else:
          proceed=True
        if (proceed):
	      fc = JFileChooser()
	      ffilter = FileNameExtensionFilter("Project files .json", ["json"])
	      fc.setFileFilter(ffilter)
	      i = fc.showDialog(GUIframe,"Open project")
	      if (i==JFileChooser.APPROVE_OPTION):
	        f = fc.getSelectedFile()
	        path = f.getPath()
	        fname = f.getName()
	        if (f.canRead() and f.isFile()):
	          if (current_stack):
	            current_stack.close(-1)
	          with open(path, 'r') as fp:
	            load_dict = json.load(fp)
	          fibers=int(load_dict["N_fibers"])
	          create_fiber_panes(fibers, spinners, labels, pntrs)
	          path, fname = apply_proj_dict(load_dict, fibers)
	          current_stack = stack_processing(GUIframe, fibers, path, fname)
	          current_filepath=path
	          current_filename=fname
	          if (("isThresholded" in load_dict) and ("Threshold_ROIs" in load_dict)):
	            if (load_dict["isThresholded"].lower() in ["true", "1", "yes"]):
	              current_stack.load_Threshold_ROIs(load_dict["Threshold_ROIs"])
	          current_stack.setSaved()
	        else:
	          nofile_dialog.dialog.setVisible(True)

    elif (self.order == 33 and current_stack): # Save project
      fc = JFileChooser()
      ffilter = FileNameExtensionFilter("Project files (.json)", ["json"])
      fc.setFileFilter(ffilter)
      i = fc.showDialog(GUIframe, "Save project")
      if (i==JFileChooser.APPROVE_OPTION):
        f = fc.getSelectedFile()
        path = f.getPath()
        fname = f.getName()
        if (f.canWrite() and f.isFile()):
          overwriteanyways_dialog.dialog.setVisible(True)
          if (overwriteanyways_dialog.flag):
            current_stack.save_project(path, fname)
        elif (f.createNewFile()):
          current_stack.save_project(path, fname)
        else:
          #IJ.showMessage("File can not be written!")
          nofile_dialog.dialog.setVisible(True)

    elif self.order == 99 and current_stack: #Close project
      current_stack.close(-1)

    elif self.order == 22 and current_stack: #Thresholding
        if (current_stack.threshold_channel is None):
          current_stack.Make_th_channel_dialog()
        current_stack.threshold_channel.reset()
        if (current_stack.threshold_channel.item_index>=0):
          th_channel=current_stack.threshold_channel.item_index
          if (current_stack.image_plus.getType()==ImagePlus.COLOR_RGB):
            imp_chX=ChannelSplitter.splitRGB(current_stack.image_plus.getImageStack(),True)[th_channel]
          else:
            imp_chX=ChannelSplitter.getChannel(current_stack.image_plus,th_channel+1)
          imp_chX_plus=ImagePlus("Thresholding channel "+str(th_channel+1), imp_chX)
          imp_chX=None
          imp_chX_plus.show()
          IJ.resetMinAndMax(imp_chX_plus)
          stats=imp_chX_plus.getRawStatistics()
          min_value=stats.min
          max_value=stats.max
          for i in range(1,current_stack.slices):
            imp_chX_plus.setSlice(i+1)
            stats=imp_chX_plus.getRawStatistics()
            min_value=min(stats.min,min_value)
            max_value=max(stats.max,max_value)
          range_value=max_value-min_value
          slider1_values=[int(round(min_value)),int(round(max_value)),int(round(min_value+range_value/3))]
          slider2_values=[int(round(min_value)),int(round(max_value)),int(round(max_value))]
          slider3_values=[1,current_stack.slices,1]
          th_sliders_dialog=make_thresholding_dialog(imp_chX_plus, "Set threshold", "Lower threshold", slider1_values, "Higher threshold", slider2_values, "Scroll stack", slider3_values, "Continue")
          th_sliders_dialog.reset_pressed()
          if (th_sliders_dialog.status>0):
            mask_stack=ImageStack()
            for i in range(current_stack.slices):
              imp_chX_plus.setSlice(i+1)
              mask_stack.addSlice(imp_chX_plus.createThresholdMask())
            mask=ImagePlus("Thresholding channel",mask_stack)
            imp_chX_plus.close()
            imp_chX_plus.flush()
            ed_dialog=erode_dilate_dialog(mask, mask_stack, "Refine binary mask", "Scroll stack", slider3_values, "Generate ROIs")
            ed_dialog.reset_pressed()
            if (ed_dialog.status>0):
              mask_stack=None
              mask.changes=False
              mask.close()
              mask.flush()
              th_roi_idx=[]
              th_roi_list=[]
              for i, th_roi in enumerate(ed_dialog.output_ROIs):
                th_roi_name="th_ch"+str(th_channel+1)+"_z"+str(i+1)
                th_roi.setName(th_roi_name)
                if (current_stack.hyperstack):
                  th_roi.setPosition(0,i+1,1)
                th_roi_list.append(th_roi)
              roi_fname=current_stack.save_ROIs_list(th_roi_list, "_th_ch"+str(th_channel+1)+"_ROIs")
              current_stack.addThresholdOverlay(th_roi_list, roi_fname)
              current_stack.setUnsaved()

    elif self.order == 44 and current_stack and current_stack.isThresholded(): #Toggle Thresholding view
      current_stack.toggle_Threshold_visible()

    elif self.order == 66 and current_stack and current_stack.isThresholded(): #Overlay Threshold and ROIs
      IJ.log("\nStarting threshold x ROIs overlay...")
      sys.stdout.flush()
      current_stack.th_x_ROIs()
      IJ.log("...done.\n")

    elif self.order == 88 and current_stack and current_stack.isThresholded(): #Overlay Cones and Threshold
      IJ.log("Starting cones x threshold overlay...")
      sys.stdout.flush()
      current_stack.cones_x_th()
      IJ.log("...done.\n")

    elif self.order == 222 and current_stack: # Overlay Cones and ROIs
      IJ.log("Starting cones x ROIs overlay...")
      sys.stdout.flush()
      current_stack.cones_x_ROIs()
      IJ.log("...done.\n")

    elif self.order == 444 and current_stack: # Overlay Cones and Threshold and ROIs
      IJ.log("Starting cones x threshold x ROIs overlay...")
      sys.stdout.flush()
      current_stack.cones_x_th_x_ROIs()
      IJ.log("...done.\n")

    elif self.order == 888 and current_stack: # Overlay Cones and Threshold and ROIs
      IJ.log("Starting batch overlay...")
      if (current_stack.isThresholded()):
        IJ.log("...doing threshold x ROIs overlay...")
        sys.stdout.flush()
        current_stack.th_x_ROIs()
        IJ.log("...doing cones x threshold overlay...")
        sys.stdout.flush()
        current_stack.cones_x_th()
        IJ.log("...doing cones x ROIs overlay...")
        sys.stdout.flush()
        current_stack.cones_x_ROIs()
        IJ.log("...doing cones x threshold x ROIs overlay...")
        sys.stdout.flush()
        current_stack.cones_x_th_x_ROIs()
      else:
        IJ.log("...doing only cones x ROIs (no thresholding found)")
        sys.stdout.flush()
        current_stack.cones_x_ROIs()
      IJ.log("...done.\n")

    elif self.order == 999: #Exit program
      exit_dialog.dialog.setVisible(True)
      if (exit_dialog.flag):
        if (current_stack):
          current_stack.close(-1)
        IJ.log("Bye-bye")
        GUIframe.dispose()

def bool_from_str(string):
    if (string in ["True", "true"]):
      return True
    else:
      return False

def apply_proj_dict(load_dict, fibers):
    global spinners_fiber, checkbox_fiber

    fpath=load_dict["Stack_path"]
    fname=load_dict["Stack_filename"]

    for i in range(fibers):
      s_fiber="fiber"+str(int(i+1))+"_"
      s_cone="cone"+str(int(i+1))+"_"
      spinners_fiber[i][0].setValue(float(load_dict[s_fiber+"X"]))
      spinners_fiber[i][1].setValue(float(load_dict[s_fiber+"Xangle"]))
      spinners_fiber[i][2].setValue(float(load_dict[s_fiber+"Y"]))
      spinners_fiber[i][3].setValue(float(load_dict[s_fiber+"Yangle"]))
      spinners_fiber[i][4].setValue(float(load_dict[s_fiber+"Z"]))
      spinners_fiber[i][5].setValue(float(load_dict[s_fiber+"Zangle"]))
      spinners_fiber[i][6].setValue(float(load_dict[s_fiber+"od"]))
      spinners_fiber[i][7].setValue(float(load_dict[s_fiber+"id"]))
      spinners_fiber[i][8].setValue(float(load_dict[s_fiber+"NA"]))
      spinners_fiber[i][9].setValue(float(load_dict[s_cone+"Length"]))
      spinners_fiber[i][10].setValue(float(load_dict[s_fiber+"LineWidth"]))
      spinners_fiber[i][11].setValue(float(load_dict[s_fiber+"Smooth"]))
      spinners_fiber[i][12].setValue(float(load_dict[s_fiber+"Tolerance"]))
      checkbox_fiber[i][0].setSelected(bool_from_str(load_dict[s_cone+"Fill"]))
      checkbox_fiber[i][1].setSelected(bool_from_str(load_dict[s_fiber+"Hide"]))
      checkbox_fiber[i][2].setSelected(bool_from_str(load_dict[s_cone+"Hide"]))
      checkbox_fiber[i][3].setBackground(Color(int(load_dict[s_fiber+"Color"])))
      checkbox_fiber[i][4].setBackground(Color(int(load_dict[s_cone+"Color"])))

    return fpath, fname


class TransformMatrix():
  def __init__(self, vector, fiber):
    self.fiber=fiber
    self.matrix=Matrix(4,4)
    self.torad=math.pi/180.0
    self.transfX=Matrix([1.0,0,0,0,0,0,0,0,0],3)
    self.transfY=Matrix([0,0,0,0,1.0,0,0,0,0],3)
    self.transfZ=Matrix([0,0,0,0,0,0,0,0,1.0],3)
      #Make/N=(3,3)/O temp_x, temp_y, temp_z, temp_M
    self.transfXYZ=Matrix(3,3)
    self.transl=Matrix(4,1)
    self.update(vector)
  def update(self,vector):
    self.transfX.set(1,1,math.cos(vector[5]*self.torad))
    self.transfX.set(2,1,-math.sin(vector[5]*self.torad))
    self.transfX.set(1,2,math.sin(vector[5]*self.torad))
    self.transfX.set(2,2,math.cos(vector[5]*self.torad))
      #temp_x={{1, 0, 0},{0, cos(transf_vector[3]*deg), -sin(transf_vector[3]*deg)},{0,sin(transf_vector[3]*deg), cos(transf_vector[3]*deg)}}
    self.transfY.set(0,0,math.cos(vector[1]*self.torad))
    self.transfY.set(2,0,-math.sin(vector[1]*self.torad))
    self.transfY.set(0,2,math.sin(vector[1]*self.torad))
    self.transfY.set(2,2,math.cos(vector[1]*self.torad))
      #temp_y={{cos(transf_vector[4]*deg), 0, -sin(transf_vector[4]*deg)},{0, 1, 0},{sin(transf_vector[4]*deg),0, cos(transf_vector[4]*deg)}}
    self.transfZ.set(0,0,math.cos(vector[3]*self.torad))
    self.transfZ.set(1,0,-math.sin(vector[3]*self.torad))
    self.transfZ.set(0,1,math.sin(vector[3]*self.torad))
    self.transfZ.set(1,1,math.cos(vector[3]*self.torad))
      #temp_z={{cos(transf_vector[5]*deg), -sin(transf_vector[5]*deg), 0},{sin(transf_vector[5]*deg), cos(transf_vector[5]*deg), 0},{0,0, 1}}
    self.transfXYZ=self.transfZ.times(self.transfY).times(self.transfX)
      #MatrixOp/O temp_M = temp_z x temp_y x temp_x
    self.matrix.setMatrix(0,2,0,2,self.transfXYZ)
      #res=(p<3 && q <3) ? temp_M[p][q] : 0
    self.matrix.set(0,3,vector[4])
    self.matrix.set(1,3,vector[0])
    self.matrix.set(2,3,vector[2])
    self.matrix.set(3,3,1.0)
      #res[0][3]=transf_vector[0]
      #res[1][3]=transf_vector[1]
      #res[2][3]=transf_vector[2]
      #res[3][3]=1

def to_um(unit_name): #returns coefficient for converting the input units (string) to microns
  unit=unit_name.lower()
  if (unit=="mm"):
    return 1e3
  elif (unit=="um" or unit=="micron" or unit=="pixel" or unit=="u" or unit==u'\xb5m'):
     return 1.0
  elif (unit=="cm"):
     return 1e4
  elif (unit=="m"):
    return 1e6
  elif (unit=="nm"):
    return 1e-3
  elif (unit=="inch"):
    return 2.54e4


def return_pos(roi):
  if (roi.hasHyperStackPosition()):
    return roi.getZPosition()
  else:
    return roi.getPosition()

class stack_processing(object):
  global spinners_fiber
  global checkbox_fiber
  global current_stack
  def __init__(self, main_frame, fibers, path, fname):
    self.fibers=fibers
    self.main_frame = main_frame
    self.filepath = path
    self.filename = fname
    self.just_path=os.sep.join(self.filepath.split(os.sep)[:-1])+os.sep
    self.image_plus=IJ.openImage(path)
    self.stack=self.image_plus.getStack()
    self.hyperstack=self.image_plus.isHyperStack()
    self.channels=self.image_plus.getNChannels()
    self.slices=self.image_plus.getNSlices()
    frms=self.image_plus.getNFrames()
    if (frms>1):
      if (self.slices==1): #swap frames and slices to get Z-stack, in case Z-steps were along time axis
        IJ.run(self.image_plus, "Properties...", "slices="+str(frms)+" frames=1")
        self.slices=self.image_plus.getNSlices()
      elif (self.slices>1):
        IJ.error("Warning", "Hyperstack dimensions too large. May not work properly.")
    self.image_plus.show()
    self.image_plus.setSlice(1)
    self.currentZ=1
    self.currentC=1
    self.image_listener=OpenImageListener()
    self.image_plus.addImageListener(self.image_listener)
    self.imageWindow=fname
    self.stackname=fname
    self.width=self.image_plus.width
    self.height=self.image_plus.height
    self.im_type=self.image_plus.getType()
    cal = self.image_plus.getCalibration()
    self.units=u'\xb5m'
    self.Xscale=cal.pixelWidth*to_um(cal.getXUnit())
    self.Yscale=cal.pixelHeight*to_um(cal.getYUnit())
    self.Zscale=cal.pixelDepth*to_um(cal.getZUnit())
    self.area_to_um2=to_um(cal.getXUnit())*to_um(cal.getYUnit())
    self.Xsize=self.Xscale*self.width
    self.Ysize=self.Yscale*self.height
    self.Zsize=self.Zscale*self.slices
    self.X_ori=cal.xOrigin*self.Xscale#*to_um(cal.getXUnit())
    self.Y_ori=cal.yOrigin*self.Yscale#*to_um(cal.getYUnit())
    self.Z_ori=cal.zOrigin*self.Zscale#*to_um(cal.getZUnit())
    self.unsaved=True
    self.status_line1=JLabel("Image path: '"+path+"'")
    self.status_line2=JLabel("Stack dimensions: "+str(self.width)+" x "+str(self.height)+" x "+str(self.slices)+" pixels ("+str(self.Xsize)+" x "+str(self.Ysize)+" x "+str(self.Zsize)+" "+self.units+")")
    self.status_line3=JLabel("Pixel dimensions: "+str(self.Xscale)+" x "+str(self.Yscale)+" x "+str(self.Zscale)+" "+self.units+"; "+str(self.channels)+" channels" )
    self.status_line4=JLabel("Zero-offset pixel coordinates ([X,Y,Z]): ["+str(cal.xOrigin)+" ; "+str(cal.yOrigin)+" ; "+str(cal.zOrigin)+"]" )
    self.status_line1.setBounds(20,Menu_height+GUI_height-210,GUI_width-50,30)
    self.status_line2.setBounds(20,Menu_height+GUI_height-190,GUI_width-50,30)
    self.status_line3.setBounds(20,Menu_height+GUI_height-170,GUI_width-50,30)
    self.status_line4.setBounds(20,Menu_height+GUI_height-150,GUI_width-50,30)
    main_frame.add(self.status_line1)
    main_frame.add(self.status_line2)
    main_frame.add(self.status_line3)
    main_frame.add(self.status_line4)
    main_frame.repaint(50, 20, Menu_height+GUI_height-210, GUI_width-20, 200)
    self.thresholded=False
    self.threshold_ROIs_path=""
    self.threshold_visible=False

    self.od=[]
    self.finess=[]
    self.tolerance=[]
    self.strokeWidth=[]
    self.fiber_color=[]
    self.fiber_hide=[]

    self.intd=[]
    self.NA=[]
    self.cone_length=[]
    self.cone_color=[]
    self.cone_fill=[]
    self.cone_hide=[]

    self.transform_matrix=[]

    self.fiber_shape=[]
    self.fiber_ROIs_coords=[]
    self.fiber_ROIs=[]

    self.cone_shape=[]
    self.cone_ROIs_coords=[]
    self.cone_ROIs=[]

    self.threshold_ROIs=[]

    rm = RoiManager.getInstance()
    if (rm==None):
      rm = RoiManager()
    rm.reset()

    self.previous_rois=[]
    previous_overlay=self.image_plus.getOverlay()
    if (previous_overlay):
      IJ.run("To ROI Manager", "")
      self.previous_rois=list(previous_overlay.toArray())
      previous_overlay.clear()
      previous_overlay=None
      IJ.log("Image contained overlay which was converted to ROI(s).")
    
    self.overlay=Overlay()
    self.overlay.clear()
    self.image_plus.setOverlay(self.overlay)

    self.fiber_vector=[]
    

    for i in range(fibers): #generating prototype rois
      self.od.append(spinners_fiber[i][6].getValue())
      self.intd.append(spinners_fiber[i][7].getValue())
      self.cone_length.append(spinners_fiber[i][9].getValue())
      self.tolerance.append(spinners_fiber[i][12].getValue())
      self.NA.append(spinners_fiber[i][8].getValue())
      self.finess.append(spinners_fiber[i][11].getValue())
      self.strokeWidth.append(spinners_fiber[i][10].getValue())
      self.fiber_color.append(checkbox_fiber[i][3].getBackground())
      self.fiber_hide.append(checkbox_fiber[i][1].isSelected())
      self.cone_color.append(checkbox_fiber[i][4].getBackground())
      self.cone_fill.append(checkbox_fiber[i][0].isSelected())
      self.cone_hide.append(checkbox_fiber[i][2].isSelected())
      self.fiber_shape.append(FiberShape(self.od[i], self.Xsize, self.Ysize, self.Zsize, self.finess[i]))
      self.cone_shape.append(ConeShape(self.intd[i], self.NA[i], self.cone_length[i], self.finess[i], self.fiber_shape[i]))
      temp_ROIs=[]
      for j in range(self.slices):
        temp_ROIs.append([[0.0,0.0],[0.0,0.0],[0.0,0.0]]) #assigning initial ROI lists, one point each at the initial step
      self.fiber_ROIs_coords.append(temp_ROIs)
      self.cone_ROIs_coords.append(temp_ROIs)
      for j in range(self.slices): #adding ROIs for the fibers and the cones at the initial step
        poly=FloatPolygon([(t[0]+self.X_ori)/self.Xscale for t in self.fiber_ROIs_coords[i][j]],[(t[1]+self.Y_ori)/self.Yscale for t in self.fiber_ROIs_coords[i][j]])
        pROI = PolygonRoi(poly,Roi.FREEROI)
        if (self.hyperstack):
          pROI.setPosition(0,j+1,1)
        else:
          pROI.setPosition(j+1)
        pROI.setName("fiber"+str(i+1)+"_z"+str(j+1))
        pROI.setStrokeWidth(self.strokeWidth[i])
        pROI.setStrokeColor(self.fiber_color[i])
        self.fiber_ROIs.append(pROI)
        self.overlay.add(pROI)

        #rm.addRoi(pROI)
      for j in range(self.slices): #adding ROIs for the fibers and the cones at the initial step
        poly=FloatPolygon([(t[0]+self.X_ori)/self.Xscale for t in self.cone_ROIs_coords[i][j]],[(t[1]+self.Y_ori)/self.Yscale for t in self.cone_ROIs_coords[i][j]])
        pROI = PolygonRoi(poly,Roi.FREEROI)
        if (self.hyperstack):
          pROI.setPosition(0,j+1,1)
        else:
          pROI.setPosition(j+1)
        pROI.setName("cone"+str(i+1)+"_z"+str(j+1))
        pROI.setStrokeWidth(self.strokeWidth[i])
        pROI.setStrokeColor(self.cone_color[i])
        self.cone_ROIs.append(pROI)
        self.overlay.add(pROI)

      vector=[spinners_fiber[i][j].getValue() for j in range(6)]
      self.fiber_vector.append(vector)
      self.transform_matrix.append(TransformMatrix(self.fiber_vector[i],i+1))
      self.update_fiber_location(i+1, self.fiber_vector[i])

      self.threshold_channel=None


  def Make_th_channel_dialog(self):    #creating the dialogs for thresholding menu
      if (self.im_type==ImagePlus.COLOR_RGB):
        self.channels_list=["Red", "Green", "Blue"]
      else:
        self.channels_list=["Ch "+str(i+1) for i in range(self.channels)]
      self.threshold_channel=make_combo_button_dialog("Set channel", self.channels_list, "Continue")

  def set_current_slice(self, slc):
    if (self.hyperstack):
      self.currentZ=1+(slc-1)//self.channels
      self.currentC=slc % self.channels
    else:
      self.currentZ=slc

  def setSaved(self):
    self.unsaved=False
  def setUnsaved(self):
    self.unsaved=True

  def isThresholded(self):
    return self.thresholded

  def isThresholded(self):
    return self.thresholded

  def addThresholdOverlay(self, th_roi_list, fpath):
    self.thresholded=True
    self.threshold_ROIs_path=fpath
    self.threshold_ROIs=[]
    self.threshold_ROIs=list(th_roi_list)
    self.threshold_visible=False
    self.toggle_Threshold_visible()


  def load_Threshold_ROIs(self, fpath):
    rm = RoiManager.getInstance()
    if (rm==None):
      rm = RoiManager()
    #temporarily store previous ROIs, those converted from TIFF overlays
#    previous_rois_names=[x.getName() for x in self.previous_rois]
#   previous_roi_idx=[rm.getIndex(x) for x in previous_rois_names]
#    rm.setSelectedIndexes(previous_roi_idx)
#    rm.runCommand(self.image_plus,"Delete")
    rm.reset()

    if (rm.open(fpath)):
      self.threshold_ROIs=list(rm.getRoisAsArray())
      if (len(self.threshold_ROIs)!=self.slices):
        self.threshold_ROIs=[]
        self.thresholded=False
        IJ.log("Wrong number of ROIs found. Please check the corresponding file or re-do thresholding.")
      else:
        self.threshold_ROIs.sort(key=return_pos) #just in case, sort by Z position o guarantee match with the cones ROIs order
        roi_idx=[rm.getRoiIndex(roi) for roi in self.threshold_ROIs]
        rm.setSelectedIndexes(roi_idx)
        rm.runCommand(self.image_plus,"Delete")
        self.thresholded=True
        self.threshold_ROIs_path=fpath
        self.threshold_visible=False
        self.toggle_Threshold_visible()
    #recover previous ROIs, those converted from TIFF overlays
    for roi in self.previous_rois:
      rm.addRoi(roi)
#

  def toggle_Threshold_visible(self):
    self.threshold_visible = not self.threshold_visible
#    for j in range(self.fibers):
#      self.hide_fiber(j+1, True)
#      self.hide_fiber(j+1, True)
    for i in range(self.slices):
      th_roi=self.threshold_ROIs[i]
      th_roi_name=th_roi.getName()
      th_roi.setStrokeWidth(1)
      th_roi.setStrokeColor(Color.WHITE)
      th_roi.setFillColor(Color.WHITE)
      self.threshold_ROIs[i]=th_roi
      if (self.threshold_visible):
        self.overlay.add(th_roi)
      else:
        self.overlay.remove(th_roi_name)
#    for j in range(self.fibers):
#      self.hide_fiber(j+1, False)
#      self.hide_fiber(j+1, False)
    self.image_plus.updateAndDraw()

  def save_ROIs_list(self, roi_list, file_suffix):
    if (len(roi_list)>0):
      rm = RoiManager.getInstance()
      if (rm==None):
        rm = RoiManager()
      roi_idx=[]
      for i, roi in enumerate(roi_list):
        rm.addRoi(roi)
        roi_name=roi.getName()
        roi_idx.append(rm.getIndex(roi_name))
      rm.setSelectedIndexes(roi_idx)
      roi_fname=self.just_path+"".join(current_stack.filename.split(".")[:-1])+file_suffix#"_th_ch"+str(th_channel+1)+"_ROIs"
      if (len(roi_idx)>1):
        roi_fname=roi_fname+".zip"
      elif (len(roi_idx)==1):
        roi_fname=roi_fname+".roi"
      rm.save(roi_fname)
      IJ.log("Saved ROIs in the file "+ roi_fname)
      rm.runCommand(self.image_plus,"Deselect")
      rm.setSelectedIndexes(roi_idx)
      rm.runCommand(self.image_plus,"Delete")
      return roi_fname

  def update_and_save_Table(self, table_name, row_offset, labels_list, file_suffix):
    if (len(labels_list)>0):
        if (row_offset==0):
          res_Tab=ResultsTable.getResultsTable(table_name)
        areas=res_Tab.getColumn("Area")
        scaled_area="Area ("+u'\xb5m'+"^2)"
        if (row_offset==0):
          res_Tab.setValues(scaled_area,areas)
        for i in range(len(labels_list)):
          res_Tab.setValue(scaled_area,i+row_offset,res_Tab.getValue("Area",i+row_offset)*self.area_to_um2)
          res_Tab.setLabel(labels_list[i], i+row_offset)
        res_Tab.show(table_name)
        roi_fname=self.just_path+"".join(current_stack.filename.split(".")[:-1])+file_suffix+".csv"
        res_Tab.save(roi_fname)
        IJ.log("Saved measurements results in the file "+ roi_fname)

  def th_x_ROIs(self):
    rm = RoiManager.getInstance()
    if (rm):
      current_Z=self.currentZ
      current_C=self.currentC
      manager_rois=list(rm.getRoisAsArray())
      list_of_crossing=[]
      list_of_crossing_names=[]
      IJ.run("Set Measurements...", "area stack display redirect=None decimal=5")
      res_Tab=ResultsTable.getResultsTable("Results")
      if (res_Tab):
        res_Tab.deleteRows(0,res_Tab.size()-1)
      for j, temp_ROI in enumerate(self.threshold_ROIs):
        if (len(temp_ROI.getContainedPoints())>0):
          name=temp_ROI.getName()
          rm.addRoi(temp_ROI)
          temp_index=rm.getIndex(name)
          if (self.hyperstack):
            ovl_pos=temp_ROI.getZPosition()
          else:
            ovl_pos=temp_ROI.getPosition()
          for roj in manager_rois:
            roj_idx=rm.getRoiIndex(roj)
            roj_name=roj.getName()
            if (roj.hasHyperStackPosition()):
              roj_Z=roj.getZPosition()
            else:
              roj_Z=roj.getPosition()
            if (roj_Z==ovl_pos):
              rm.setSelectedIndexes([temp_index, roj_idx])
              rm.runCommand(self.image_plus,"AND")
              and_roi=self.image_plus.getRoi()
              if (and_roi is not None):
                and_roi_name=name+" x "+roj_name
                and_roi.setName(and_roi_name)
                rm.addRoi(and_roi)
                if (self.hyperstack):
                  and_roi.setPosition(0,ovl_pos,1)
                else:
                  and_roi.setPosition(ovl_pos)
                list_of_crossing.append(and_roi)
                list_of_crossing_names.append(and_roi_name)
                and_idx=rm.getIndex(and_roi_name)
                rm.select(and_idx)
                rm.runCommand("Measure")
                rm.runCommand("Delete")
          rm.deselect()
          rm.select(temp_index)
          rm.runCommand(self.image_plus,"Delete")

      file_suffix="_th_x_ROIs"
      self.save_ROIs_list(list_of_crossing, file_suffix)
      self.update_and_save_Table("Results", 0, list_of_crossing_names, file_suffix)


      if (self.hyperstack):
        self.image_plus.setZ(current_Z)
        self.image_plus.setC(current_C)
      else:
        self.image_plus.setSlice(current_Z)



  def cones_x_ROIs(self):
    rm = RoiManager.getInstance()
    if (rm):
      current_Z=self.currentZ
      current_C=self.currentC
      manager_rois=list(rm.getRoisAsArray())
      list_of_crossing=[]
      list_of_crossing_names=[]
      IJ.run("Set Measurements...", "area stack display redirect=None decimal=5")
      res_Tab=ResultsTable.getResultsTable("Results")
      if (res_Tab):
        res_Tab.deleteRows(0,res_Tab.size()-1)
      for i in range(self.fibers):
        for j in range(self.slices):
          temp_ROI=self.cone_ROIs[int((i-1)*self.slices+j)]
          if (len(temp_ROI.getContainedPoints())>0):
            name=temp_ROI.getName()
            rm.addRoi(temp_ROI)
            temp_index=rm.getIndex(name)
            if (self.hyperstack):
              ovl_pos=temp_ROI.getZPosition()
            else:
              ovl_pos=temp_ROI.getPosition()
            for roj in manager_rois:
              roj_idx=rm.getRoiIndex(roj)
              roj_name=roj.getName()
              if (roj.hasHyperStackPosition()):
                roj_Z=roj.getZPosition()
              else:
                roj_Z=roj.getPosition()
              if (roj_Z==ovl_pos):
                rm.setSelectedIndexes([temp_index, roj_idx])
                rm.runCommand(self.image_plus,"AND")
                and_roi=self.image_plus.getRoi()
                if (and_roi is not None):
                  and_roi_name=name+" x "+roj_name
                  and_roi.setName(and_roi_name)
                  rm.addRoi(and_roi)
                  if (self.hyperstack):
                    and_roi.setPosition(0,ovl_pos,1)
                  else:
                    and_roi.setPosition(ovl_pos)
                  list_of_crossing.append(and_roi)
                  list_of_crossing_names.append(and_roi_name)
                  and_idx=rm.getIndex(and_roi_name)
                  rm.select(and_idx)
                  rm.runCommand("Measure")
                  rm.runCommand("Delete")

            rm.deselect()
            rm.select(temp_index)
            rm.runCommand(self.image_plus,"Delete")

      file_suffix="_cones_x_ROIs"
      self.save_ROIs_list(list_of_crossing, file_suffix)
      self.update_and_save_Table("Results", 0, list_of_crossing_names, file_suffix)


      if (self.hyperstack):
        self.image_plus.setZ(current_Z)
        self.image_plus.setC(current_C)
      else:
        self.image_plus.setSlice(current_Z)


  def cones_x_th(self):
    rm = RoiManager.getInstance()
    if (rm==None):
      rm = RoiManager()

    current_Z=self.currentZ
    current_C=self.currentC
    list_of_crossing=[]
    list_of_crossing_names=[]
    IJ.run("Set Measurements...", "area stack display redirect=None decimal=5")
    res_Tab=ResultsTable.getResultsTable("Results")
    if (res_Tab):
      res_Tab.deleteRows(0,res_Tab.size()-1)
    for i in range(self.fibers):
      for j in range(self.slices):
        temp_ROI=self.cone_ROIs[int((i-1)*self.slices+j)]
        temp_ROI_th=self.threshold_ROIs[j]
        if (len(temp_ROI.getContainedPoints())>0):
          name=temp_ROI.getName()
          name_th=temp_ROI_th.getName()
          rm.addRoi(temp_ROI)
          rm.addRoi(temp_ROI_th)
          temp_index=rm.getIndex(name)
          temp_index_th=rm.getIndex(name_th)

          if (self.hyperstack):
            temp_ROI.setPosition(0,j+1,1)
            temp_ROI_th.setPosition(0,j+1,1)
          else:
            temp_ROI.setPosition(j+1)
            temp_ROI_th.setPosition(j+1)

          rm.setSelectedIndexes([temp_index, temp_index_th])
          rm.runCommand(self.image_plus,"AND")
          and_roi=self.image_plus.getRoi()
          if (and_roi is not None):
            and_roi_name=name+" x "+name_th
            and_roi.setName(and_roi_name)
            rm.addRoi(and_roi)
            if (self.hyperstack):
              and_roi.setPosition(0,j+1,1)
            else:
              and_roi.setPosition(j+1)
            list_of_crossing.append(and_roi)
            list_of_crossing_names.append(and_roi_name)
            and_idx=rm.getIndex(and_roi_name)
            rm.select(and_idx)
            rm.runCommand("Measure")
            rm.runCommand("Delete")

          rm.deselect()
          rm.setSelectedIndexes([temp_index, temp_index_th])
          rm.runCommand(self.image_plus,"Delete")

    file_suffix="_cones_x_th"
    self.save_ROIs_list(list_of_crossing, "_cones_x_th")
    self.update_and_save_Table("Results", 0, list_of_crossing_names, file_suffix)


    if (self.hyperstack):
      self.image_plus.setZ(current_Z)
      self.image_plus.setC(current_C)
    else:
      self.image_plus.setSlice(current_Z)



  def cones_x_th_x_ROIs(self):
    rm = RoiManager.getInstance()
    if (rm):
      current_Z=self.currentZ
      current_C=self.currentC
      manager_rois=list(rm.getRoisAsArray())
      list_of_crossing=[]
      list_of_crossing_names=[]
      IJ.run("Set Measurements...", "area stack display redirect=None decimal=5")
      res_Tab=ResultsTable.getResultsTable("Results")
      if (res_Tab):
        res_Tab.deleteRows(0,res_Tab.size()-1)
      for i in range(self.fibers):
        for j in range(self.slices):
          temp_ROI=self.cone_ROIs[int((i-1)*self.slices+j)]
          temp_ROI_th=self.threshold_ROIs[j]
          if (len(temp_ROI.getContainedPoints())>0 and len(temp_ROI_th.getContainedPoints())>0):
            name=temp_ROI.getName()
            rm.addRoi(temp_ROI)
            name_th=temp_ROI_th.getName()
            rm.addRoi(temp_ROI_th)
            temp_index=rm.getIndex(name)
            temp_index_th=rm.getIndex(name_th)
            if (self.hyperstack):
              ovl_pos=temp_ROI.getZPosition()
            else:
              ovl_pos=temp_ROI.getPosition()
            for roj in manager_rois:
              roj_idx=rm.getRoiIndex(roj)
              roj_name=roj.getName()
              if (roj.hasHyperStackPosition()):
                roj_Z=roj.getZPosition()
              else:
                roj_Z=roj.getPosition()
              if (roj_Z==ovl_pos):
                rm.setSelectedIndexes([temp_index, temp_index_th, roj_idx])
                rm.runCommand(self.image_plus,"AND")
                and_roi=self.image_plus.getRoi()
                if (and_roi is not None):
                  and_roi_name=name+" x "+name_th+" x "+roj_name
                  and_roi.setName(and_roi_name)
                  rm.addRoi(and_roi)
                  if (self.hyperstack):
                    and_roi.setPosition(0,ovl_pos,1)
                  else:
                    and_roi.setPosition(ovl_pos)
                  list_of_crossing.append(and_roi)
                  list_of_crossing_names.append(and_roi_name)
                  and_idx=rm.getIndex(and_roi_name)
                  rm.select(and_idx)
                  rm.runCommand("Measure")
                  rm.runCommand("Delete")

            rm.deselect()
            rm.setSelectedIndexes([temp_index, temp_index_th])
            rm.runCommand(self.image_plus,"Delete")

      file_suffix="_cones_x_th_x_ROIs"
      self.save_ROIs_list(list_of_crossing, file_suffix)
      self.update_and_save_Table("Results", 0, list_of_crossing_names, file_suffix)


      if (self.hyperstack):
        self.image_plus.setZ(current_Z)
        self.image_plus.setC(current_C)
      else:
        self.image_plus.setSlice(current_Z)



  def save_project(self, pathname, fname):
    save_dict={}
    save_dict["N_fibers"]=str(int(self.fibers))
    save_dict["Stack_path"]=self.filepath
    save_dict["Stack_filename"]=self.filename

    if (self.thresholded):
      save_dict["isThresholded"]="True"
      save_dict["Threshold_ROIs"]=self.threshold_ROIs_path
    else:
      save_dict["isThresholded"]="False"
      save_dict["Threshold_ROIs"]=""

    for i in range(self.fibers):
      s_fiber="fiber"+str(int(i+1))+"_"
      s_cone="cone"+str(int(i+1))+"_"
      save_dict[s_fiber+"X"]=str(spinners_fiber[i][0].getValue())
      save_dict[s_fiber+"Xangle"]=str(spinners_fiber[i][1].getValue())
      save_dict[s_fiber+"Y"]=str(spinners_fiber[i][2].getValue())
      save_dict[s_fiber+"Yangle"]=str(spinners_fiber[i][3].getValue())
      save_dict[s_fiber+"Z"]=str(spinners_fiber[i][4].getValue())
      save_dict[s_fiber+"Zangle"]=str(spinners_fiber[i][5].getValue())
      save_dict[s_fiber+"od"]=str(self.od[i])
      save_dict[s_fiber+"id"]=str(self.intd[i])
      save_dict[s_fiber+"NA"]=str(self.NA[i])
      save_dict[s_fiber+"LineWidth"]=str(self.strokeWidth[i])
      save_dict[s_fiber+"Smooth"]=str(self.finess[i])
      save_dict[s_fiber+"Tolerance"]=str(self.tolerance[i])
      save_dict[s_fiber+"Hide"]=str(self.fiber_hide[i])
      save_dict[s_fiber+"Color"]=str(self.fiber_color[i].getRGB())
      save_dict[s_cone+"Length"]=str(self.cone_length[i])
      save_dict[s_cone+"Hide"]=str(self.cone_hide[i])
      save_dict[s_cone+"Color"]=str(self.cone_color[i].getRGB())
      save_dict[s_cone+"Fill"]=str(self.cone_fill[i])

    with open(pathname, 'w') as fp:
      json.dump(save_dict, fp, sort_keys=False, indent=4)
    self.setSaved()
    IJ.log("Saved the project '"+self.stackname+"' in the file " + pathname)



  def update_fiber_location(self, fiber, vector):
    transform_matrix=self.transform_matrix[fiber-1]
    transform_matrix.update(vector)
    self.update_ROIs_fiber(fiber, self.tolerance[fiber-1])
    self.update_ROIs_cone(fiber, self.tolerance[fiber-1])
    self.setUnsaved()

  def update_fiber_shape(self, fiber, od, finess, tolerance):
    self.od[fiber-1]=od
    self.finess[fiber-1]=finess
    self.tolerance[fiber-1]=tolerance
    active_fiber=self.fiber_shape[fiber-1]
    active_fiber.update_surface(od, finess)
    self.update_ROIs_fiber(fiber, self.tolerance[fiber-1])
    self.setUnsaved()

  def update_cone_shape(self, fiber, int_d, NA, cone_length, finess, tolerance):
    self.intd[fiber-1]=int_d
    self.NA[fiber-1]=NA
    self.cone_length[fiber-1]=cone_length
    self.finess[fiber-1]=finess
    self.tolerance[fiber-1]=tolerance
    active_fiber=self.fiber_shape[fiber-1]
    active_cone=self.cone_shape[fiber-1]
    active_cone.update_surface(int_d, NA, cone_length, finess, active_fiber)
    self.update_ROIs_cone(fiber, self.tolerance[fiber-1])
    self.setUnsaved()

  def update_ROIs_fiber(self, fiber, tolerance):
    # fibers
    active_fiber_ROIs=self.fiber_ROIs_coords[fiber-1]
    transform_matrix=self.transform_matrix[fiber-1]
    th=tolerance/100

    active_fiber=self.fiber_shape[fiber-1]
    M_fiber=Matrix(jarray.array(active_fiber.points_list,java.lang.Class.forName("[D"))).transpose()
    M_fiber_transf=transform_matrix.matrix.times(M_fiber)
    transf_points_fiber=list(M_fiber_transf.transpose().getArray())

   #just_test=[]

    for j in range(self.slices):
      active_fiber_ROIs[j]=[]

    for pnt in transf_points_fiber: #searching for cross-sections of the fiber by the image planes
      i_plane=(pnt[0]+self.Z_ori)/self.Zscale
      i=int(round(i_plane))
      if (abs(i_plane-i)<=th and i<self.slices and i>=0):
        active_fiber_ROIs[i].append(pnt[1:3])


      #active_fiber_ROIs[j]=[pnt[1:3] for pnt in transf_points_fiber if abs(pnt[0]-current_Z)<=th]
    for j in range(self.slices):
      if (len(active_fiber_ROIs[j])==0):
        active_fiber_ROIs[j]=[[0.0,0.0],[0.0,0.0],[0.0,0.0]]
      #just_test.append(len(active_fiber_ROIs[j]))
      active_fiber_ROIs[j]=Sort_ROI_coords(active_fiber_ROIs[j])
      poly=FloatPolygon([(t[0]+self.X_ori)/self.Xscale for t in active_fiber_ROIs[j]],[(t[1]+self.Y_ori)/self.Yscale for t in active_fiber_ROIs[j]])
      pROI = PolygonRoi(poly,Roi.FREEROI)
      self.fiber_ROIs[int((fiber-1)*self.slices+j)]=pROI

    self.DrawFiber(fiber)


  def DrawFiber(self, fiber):
    for j in range(self.slices):
      pROI=self.fiber_ROIs[int((fiber-1)*self.slices+j)]
      roi_name="fiber"+str(fiber)+"_z"+str(j+1)
      pROI.setName(roi_name)
      if (self.hyperstack):
        pROI.setPosition(0,j+1,1)
      else:
        pROI.setPosition(j+1)
      pROI.setStrokeWidth(self.strokeWidth[fiber-1])
      pROI.setStrokeColor(self.fiber_color[fiber-1])
      #rm.setRoi(pROI, int(2*(fiber-1)*self.slices+j))
      if (self.fiber_hide[fiber-1]==False):
        self.overlay.set(pROI, self.overlay.getIndex(roi_name))#int(2*(fiber-1)*self.slices+j))#
    self.image_plus.updateAndDraw()


  def update_ROIs_cone(self, fiber, tolerance):

    active_cone_ROIs=self.cone_ROIs_coords[fiber-1]
    transform_matrix=self.transform_matrix[fiber-1]
    th=tolerance/100

    active_cone=self.cone_shape[fiber-1]
    M_cone=Matrix(jarray.array(active_cone.points_list,java.lang.Class.forName("[D"))).transpose()
    M_cone_transf=transform_matrix.matrix.times(M_cone)
    transf_points_cone=list(M_cone_transf.transpose().getArray())
    #just_test=[]

    for j in range(self.slices):
      active_cone_ROIs[j]=[]


    for pnt in transf_points_cone: #searching for cross-sections of the cone by the image planes
      i_plane=(pnt[0]+self.Z_ori)/self.Zscale
      i=int(round(i_plane))
      if (abs(i_plane-i)<=th and i<self.slices and i>=0):
        active_cone_ROIs[i].append(pnt[1:3])

      #active_fiber_ROIs[j]=[pnt[1:3] for pnt in transf_points_fiber if abs(pnt[0]-current_Z)<=th]
    for j in range(self.slices):
      if (len(active_cone_ROIs[j])==0):
        active_cone_ROIs[j]=[[0.0,0.0],[0.0,0.0],[0.0,0.0]]
      #just_test.append(len(active_fiber_ROIs[j]))
      active_cone_ROIs[j]=Sort_ROI_coords(active_cone_ROIs[j])
      poly=FloatPolygon([(t[0]+self.X_ori)/self.Xscale for t in active_cone_ROIs[j]],[(t[1]+self.Y_ori)/self.Yscale for t in active_cone_ROIs[j]])
      pROI = PolygonRoi(poly,Roi.FREEROI)
      self.cone_ROIs[int((fiber-1)*self.slices+j)]=pROI

    self.DrawCone(fiber)

  def DrawCone(self, fiber):
    for j in range(self.slices):
      pROI=self.cone_ROIs[int((fiber-1)*self.slices+j)]
      roi_name="cone"+str(fiber)+"_z"+str(j+1)
      pROI.setName(roi_name)
      if (self.hyperstack):
        pROI.setPosition(0,j+1,1)
      else:
        pROI.setPosition(j+1)
      pROI.setStrokeWidth(self.strokeWidth[fiber-1])
      pROI.setStrokeColor(self.cone_color[fiber-1])
      #rm.setRoi(pROI, int(2*(fiber-1)*self.slices+j))
      if (self.cone_fill[fiber-1]):
        pROI.setFillColor(self.cone_color[fiber-1])
      if (self.cone_hide[fiber-1]==False):
        self.overlay.set(pROI, self.overlay.getIndex(roi_name))#int(2*(fiber-1)*self.slices+j))#
    self.image_plus.updateAndDraw()

  def change_fiber_color(self, fiber, fiber_color):
    self.fiber_color[fiber-1]=fiber_color
    self.update_appearance(fiber)

  def change_cone_color(self, fiber, cone_color):
    self.cone_color[fiber-1]=cone_color
    self.update_appearance(fiber)

  def change_line_thickness(self, fiber, line_thick):
    self.strokeWidth[fiber-1]=line_thick
    self.update_appearance(fiber)

  def fill_cone(self, fiber, fill_flag):
    self.cone_fill[fiber-1]=fill_flag
    self.update_appearance(fiber)

  def hide_cone(self, fiber, hide_flag):
    overlay=self.overlay
    for j in range(self.slices):
      cone_idx=int((fiber-1)*self.slices+j)
      cROI = self.cone_ROIs[cone_idx]
      cone_ROI_name=cROI.getName()
      if (hide_flag):
        overlay.remove(cone_ROI_name)
      else:
        overlay.add(cROI)
    self.cone_hide[fiber-1]=hide_flag
    self.update_appearance(fiber)


  def hide_fiber(self, fiber, hide_flag):
    overlay=self.overlay
    for j in range(self.slices):
      fiber_idx=int((fiber-1)*self.slices+j)
      fROI = self.fiber_ROIs[fiber_idx]
      fiber_ROI_name=fROI.getName()
      if (hide_flag):
        overlay.remove(fiber_ROI_name)
      else:
        overlay.add(fROI)
    self.fiber_hide[fiber-1]=hide_flag
    self.update_appearance(fiber)


  def update_appearance(self, fiber):
    overlay=self.overlay
    for j in range(self.slices):
      fiber_idx=int((fiber-1)*self.slices+j)
      fROI = self.fiber_ROIs[fiber_idx]#overlay.get(fiber_ROI_name)
      fiber_ROI_name=fROI.getName()#"fiber"+str(fiber)+"_z"+str(j+1)
      #poly=FloatPolygon([t[0]/self.Xscale for t in active_fiber_ROIs[j]],[t[1]/self.Yscale for t in active_fiber_ROIs[j]])
      #fROI.setPosition(j+1)
      fROI.setStrokeWidth(self.strokeWidth[fiber-1])
      fROI.setStrokeColor(self.fiber_color[fiber-1])
      #rm.setRoi(pROI, int(2*(fiber-1)*self.slices+j))
      self.fiber_ROIs[fiber_idx] = fROI
      if (self.fiber_hide[fiber-1]==False):
        overlay.set(fROI, overlay.getIndex(fiber_ROI_name))

      cone_idx=int((fiber-1)*self.slices+j)
      cROI = self.cone_ROIs[cone_idx]#overlay.get(fiber_ROI_name)
      cone_ROI_name=cROI.getName()#"fiber"+str(fiber)+"_z"+str(j+1)
      cROI.setStrokeWidth(self.strokeWidth[fiber-1])
      cROI.setStrokeColor(self.cone_color[fiber-1])
      if (self.cone_fill[fiber-1]):
        cROI.setFillColor(self.cone_color[fiber-1])
      else:
        cROI.setFillColor(None)
      #rm.setRoi(pROI, int(2*(fiber-1)*self.slices+j))
      self.cone_ROIs[cone_idx] = cROI
      if (self.cone_hide[fiber-1]==False):
        overlay.set(cROI, overlay.getIndex(cone_ROI_name))

    self.image_plus.updateAndDraw()
    self.setUnsaved()



  def close(self, isWindowClosed):
    global tabs
    global closeanyways_dialog
    global current_stack
    proceed=True
    if (current_stack.unsaved):
      closeanyways_dialog.dialog.setVisible(True)
      proceed=closeanyways_dialog.flag
    if (proceed):
      tabs.removeAll()
      fiber_panels=[]
      spinners_fiber=[]
      checkbox_fiber=[]
      self.status_line1.setText("")
      self.status_line2.setText("")
      self.status_line3.setText("")
      self.status_line4.setText("")
      self.overlay.clear()
      if (isWindowClosed<0):
        self.image_plus.removeImageListener(self.image_listener)
        self.image_plus.close()
    #IJ.selectWindow(self.imageWindow)
    #IJ.run("Close")
    #self.image_plus.killStack()
    #self.imp.flush()
    #rm.runCommand('reset')
      if (self.threshold_channel is not None):
        self.threshold_channel.close()
      IJ.log("Closed project '"+self.stackname+"' and associated data.")
      current_stack = None
      del self
    else:
      if (isWindowClosed>0):
        self.image_plus=ImagePlus(self.filename, self.stack)
        self.image_plus.show()
        self.image_plus.addImageListener(self.image_listener)
        self.image_plus.setOverlay(self.overlay)
        for j in range(self.fibers):
          self.DrawFiber(j+1)
          self.DrawCone(j+1)
        self.image_plus.setSlice(self.currentSlice)





def dist(p1, p2):
    return math.sqrt(math.pow(p1[0]-p2[0],2)+math.pow(p1[1]-p2[1],2))

def Sort_ROI_coords(unsorted_list):
    buf_list=[item for item in unsorted_list]
    N=len(unsorted_list)
    for i in range(1,N):
        idx=i
        min_dist=dist(buf_list[i-1],buf_list[idx])
        for j in range(i+1,N):
            try_dist=dist(buf_list[i-1],buf_list[j])
            if (min_dist > try_dist):
                min_dist = try_dist
                idx=j
        if (idx!=i):
            buf_list[i], buf_list[idx] = buf_list[idx], buf_list[i]
    return buf_list




class FiberShape(object):
    def __init__(self, od, im_Xsize, im_Ysize, im_Zsize, fine_factor):
        #self.im_total_pnts = im_width*im_height # in points
        self.image_Y=im_Ysize
        self.length=math.sqrt(im_Xsize*im_Xsize+im_Ysize*im_Ysize+im_Zsize*im_Zsize) # in microns
        self.fiber_side_s=self.length*math.pi*od
        self.fiber_tip_s=math.pi*od*od/4.0
        self.fiber_pnts=int(round(fine_factor*(self.fiber_side_s+self.fiber_tip_s)))#int(round(fine_factor*self.im_total_pnts))
        self.fiber_side_pnts=int(round(self.fiber_pnts*self.fiber_side_s/(self.fiber_side_s+self.fiber_tip_s)))
        self.points_list=[]
        self.Z0=0 #self.image_Y*0.5
        #self.matrix=Matrix(jarray.array(self.points_list,java.lang.Class.forName("[D")))
        self.update_surface(od, fine_factor)



    def update_surface(self, od, fine_factor):
        Y0_coord=0 #self.image_Y*0.5
        self.Z0=Y0_coord
        self.fiber_side_s=self.length*math.pi*od
        self.fiber_tip_s=math.pi*od*od/4.0
        radius=od*0.5
        self.fiber_pnts=int(round(fine_factor*(self.fiber_side_s+self.fiber_tip_s)))#int(round(fine_factor*self.im_total_pnts))
        self.fiber_side_pnts=int(round(self.fiber_pnts*self.fiber_side_s/(self.fiber_side_s+self.fiber_tip_s)))
        self.fiber_tip_pnts=max(self.fiber_pnts-self.fiber_side_pnts, 1)
        self.points_list=[[0.0,0.0,Y0_coord,1.0]] # center of the fiber tip in the fiber coordinate system
        for i in range(self.fiber_side_pnts):
            fi=random.uniform(0, 2.0*math.pi)
            self.points_list.append([-radius*math.sin(fi), radius*math.cos(fi), Y0_coord-random.uniform(0, self.length), 1.0])
        for i in range(self.fiber_tip_pnts-1):
            fi=random.uniform(0, 2.0*math.pi)
            r_i=random.uniform(0, radius)
            self.points_list.append([-r_i*math.sin(fi),r_i*math.cos(fi),Y0_coord,1.0])
        for i in range(36): #making the solid rim of the fiber tip
            fi=math.pi/18.0*i
            self.points_list.append([-radius*math.sin(fi),radius*math.cos(fi),Y0_coord,1.0])
        self.fiber_pnts=self.fiber_side_pnts+self.fiber_tip_pnts+36



class ConeShape(object):
    def __init__(self, int_d, NA, cone_length, finess, its_fiber_obj):
        #self.im_total_pnts = im_width*im_height # in points
        #self.image_Y=im_Ysize
        self.core_radius=int_d*0.5
        self.depth=cone_length # in microns
        self.brain_n=1.35
        self.NA_angle=math.asin(NA/self.brain_n)
        self.cone_area_top=0
        self.cone_area_side=0
        self.cone_area_sphere=0
        self.cone_pnts=0
        self.cone_pnts_top=0
        self.cone_pnts_side=0
        self.cone_pnts_shpere=0
        self.points_list=[]
        self.update_surface(int_d, NA, cone_length, finess, its_fiber_obj)
        self.Z0=its_fiber_obj.Z0


    def update_surface(self, int_d, NA, length, fine_factor, its_fiber_obj):
        self.core_radius=int_d*0.5
        self.depth=length # in microns
        self.NA_angle=math.asin(NA/self.brain_n)
        radius=self.core_radius
        cone_R=self.depth+radius/math.tan(self.NA_angle)
        self.cone_area_top=math.pi*radius**2
        self.cone_area_side=math.pi*(math.sin(self.NA_angle)*cone_R**2-1.0/math.sin(self.NA_angle)*radius**2)
        self.cone_area_sphere=math.pi*(2-2*math.cos(self.NA_angle))*cone_R**2
        self.cone_pnts_top=int(round(fine_factor*self.cone_area_top))+1 #int(round(fine_factor*self.im_total_pnts))
        self.cone_pnts_sphere=int(round(fine_factor*self.cone_area_sphere))+1
        self.cone_pnts_side=int(round(fine_factor*self.cone_area_side))
        self.Z0=its_fiber_obj.Z0
        self.points_list=[[0.0,0.0,self.Z0,1.0]] # center of the fiber tip in the fiber coordinate system
        self.points_list.append([0.0,0.0,self.Z0+self.depth,1.0]) # center of the spherical cone

        big_radius=(self.depth*math.sin(self.NA_angle)+radius*math.cos(self.NA_angle))
        h=self.depth-(1-math.cos(self.NA_angle))*cone_R

        for i in range(36): #making the solid rim at the fiber tip
            fi=math.pi/18.0*i
            self.points_list.append([-radius*math.sin(fi),radius*math.cos(fi),self.Z0,1.0])
            self.points_list.append([-big_radius*math.sin(fi),big_radius*math.cos(fi),self.Z0+h,1.0])

        for i in range(self.cone_pnts_top):
            fi=random.uniform(0, 2.0*math.pi)
            r_i=random.uniform(0, radius)
            self.points_list.append([-r_i*math.sin(fi), r_i*math.cos(fi), self.Z0, 1.0])

        for i in range(self.cone_pnts_side):
            fi=random.uniform(0, 2.0*math.pi)
            h_i=random.uniform(0, h)
            r_i=radius+h_i*math.tan(self.NA_angle)
            self.points_list.append([-r_i*math.sin(fi), r_i*math.cos(fi), self.Z0+h_i, 1.0])

        for i in range(self.cone_pnts_sphere):
            fi=random.uniform(0, 2.0*math.pi)
            alfa_i=random.uniform(0, self.NA_angle)
            r_i=cone_R*math.sin(alfa_i)
            self.points_list.append([-r_i*math.sin(fi), r_i*math.cos(fi), self.Z0+(cone_R*math.cos(alfa_i)-radius/math.tan(self.NA_angle)), 1.0])


        self.cone_pnts=self.cone_pnts_top+self.cone_pnts_side+self.cone_pnts_sphere+72



def create_fiber_panes(fibers, spinners, labels, pntrs):
  global fiber_panels, spinners_fiber, checkbox_fiber
  global tabs
  fiber_panels=[]
  spinners_fiber=[]
  checkbox_fiber=[]

  pane_layout=GridLayout(9,2,0,20)
  for i in range(fibers):
	  fiber_panels.append(JPanel())
	  fiber_panels[i].setBackground(Color(230-int(i*20),230-int(i*20),230-int(i*20)))
	  tabs.add(" fiber #"+str(i+1)+" ",fiber_panels[i])

	  spinners_fiber.append([])
	  checkbox_fiber.append([])
	  for j in range(13):
	    spin_j, contentPane = text_and_spinner(rjust(labels[j],30), spinners[pntrs[j]])
	    spinners_fiber[i].append(spin_j)
	    fiber_panels[i].add(contentPane)
	    spinners_fiber[i][j].addChangeListener(Listener_spinners(spinners_fiber[i], j, i+1))
	  for j in range(5):
	    checkbox, contentPane = make_checkbox(labels[j+13], False)
	    checkbox_fiber[i].append(checkbox)
	    checkbox.addActionListener(Listener_checkboxes(checkbox, j, i+1))
	    fiber_panels[i].add(contentPane)
	  fiber_panels[i].setLayout(pane_layout)



spinners = [[-4200, -150000, 150000, 10],[0, -90, 90, 0.2],[0, -150000, 150000, 10],[0, -90, 90, 0.2],[0, -150000, 150000, 10],[0, -90, 90, 0.2],
            [230, 10, 1500, 5],[200, 1, 1500, 5],[0.39, 0.01, 1.35, 0.1],[500, 10, 5000, 10],[2, 0, 20.0, 1],[0.02, 0.001, 1, 0.02],[0.5, 0.1, 20.0, 0.1]]
labels =  ['Position along X (um):', 'Rotation around X (deg):','Position along Y (um):', 'Rotation around Y (deg):','Position along Z (um):', 'Rotation around Z (deg):',
          'Fiber o.d. (um):', 'Fiber i.d. (um):','Fiber N.A.:', 'Light cone length (um):', 'Line thickness (pix):', 'Fiber rendering dpi (1/mm2):', 'Tolerance along Z (%):',
          'Fill the light cone', 'Hide the fiber', 'Hide the light cone', 'Change the fiber color', 'Change the cone color']
pntrs = [0,1,2,3,4,5,6,7,8,9,10,11,12]

#set_check_boxes = [False, False, False, False, False]
selected_flag=False

fiber_panels=[]
spinners_fiber=[]
checkbox_fiber=[]

GUI_width=700
GUI_height=750

Menu_height=40
Menu_width=300

current_filepath = ""
current_filename = ""
current_stack=None #IJ.createImage("", "8-bit", 10, 10, 1).getStack()

GUIframe = JFrame("Fiber Light Cone")
GUIframe.setSize(GUI_width,GUI_height)
GUIframe.setLayout(None)
GUIframe.setBackground(Color.WHITE)

tabs = JTabbedPane()
tabs.setBounds(20,Menu_height,GUI_width-50,GUI_height-240)
GUIframe.add(tabs)


setNfibers_dialog=One_spinner_dialog("Please specify","The number of fibers:","OK", 2,1,10,1, True, None)
nofile_dialog=One_button_dialog("Alert","Can not open the file!","OK", None)
openanyways_dialog=Two_buttons_dialog("Warning","Current unsaved data will be lost!","Proceed","Cancel",True,None)
overwriteanyways_dialog=Two_buttons_dialog("Warning","Existing project will be overwritten!","Proceed","Cancel",True,None)
closeanyways_dialog=Two_buttons_dialog("Warning","Unsaved data will be lost!","Proceed","Cancel",True,None)
exit_dialog=Two_buttons_dialog("Exit","Sure to exit the program now?","Yes","No",True,None)


fibers=2 #total number of fibers

menu_bar=JMenuBar()
menu_bar.setBounds(0,0,Menu_width,Menu_height)
menu_file=JMenu("File")

menu_file_create=JMenuItem("Create project")
menu_file_create.addActionListener(Listener_menu(menu_file_create, 0))
menu_file.add(menu_file_create)

menu_file_load=JMenuItem("Load project")
menu_file_load.addActionListener(Listener_menu(menu_file_load, 11))
menu_file.add(menu_file_load)

menu_prj_save=JMenuItem("Save project")
menu_prj_save.addActionListener(Listener_menu(menu_prj_save, 33))
menu_file.add(menu_prj_save)

menu_file_close=JMenuItem("Close project")
menu_file_close.addActionListener(Listener_menu(menu_file_close, 99))
menu_file.add(menu_file_close)

menu_file_exit=JMenuItem("Exit")
menu_file_exit.addActionListener(Listener_menu(menu_file_exit, 999))
menu_file.add(menu_file_exit)

menu_analysis=JMenu("Analysis")

menu_threshold=JMenuItem("Threshold channel")
menu_threshold.addActionListener(Listener_menu(menu_threshold, 22))
menu_analysis.add(menu_threshold)

menu_toggle_th=JMenuItem("Toggle Threshold visible")
menu_toggle_th.addActionListener(Listener_menu(menu_toggle_th, 44))
menu_analysis.add(menu_toggle_th)

menu_th_x_ROIs=JMenuItem("Overlay Threshold&ROIs")
menu_th_x_ROIs.addActionListener(Listener_menu(menu_th_x_ROIs, 66))
menu_analysis.add(menu_th_x_ROIs)

menu_cones_x_th=JMenuItem("Overlay Cones&Threshold")
menu_cones_x_th.addActionListener(Listener_menu(menu_cones_x_th, 88))
menu_analysis.add(menu_cones_x_th)

menu_cones_x_ROIs=JMenuItem("Overlay Cones&ROIs")
menu_cones_x_ROIs.addActionListener(Listener_menu(menu_cones_x_ROIs, 222))
menu_analysis.add(menu_cones_x_ROIs)

menu_cones_x_Th_x_ROIs=JMenuItem("Overlay Cones&Threshold&ROIs")
menu_cones_x_Th_x_ROIs.addActionListener(Listener_menu(menu_cones_x_Th_x_ROIs, 444))
menu_analysis.add(menu_cones_x_Th_x_ROIs)

menu_batch_x=JMenuItem("Batch all possible overlays")
menu_batch_x.addActionListener(Listener_menu(menu_batch_x, 888))
menu_analysis.add(menu_batch_x)



menu_bar.add(menu_file)
menu_bar.add(menu_analysis)

GUIframe.add(menu_bar)


#GUIframe.pack()


GUIframe.setVisible(True)

IJ.log("Hello!")






