#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import wx, gettext, os, sys, ConfigParser, subprocess, webbrowser, re
import wx.lib.scrolledpanel as scrolled
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

home = os.path.expanduser('~')
pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, 102))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MainFrame(wx.Frame):
####layout###################
	def __init__(self):
		wx.Frame.__init__(self, None, title="OpenPlotter", size=(700,420))

		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

########reading configuration###################
		self.read_conf()
###########################reading configuration
########language###################
		gettext.install('openplotter', currentpath+'/locale', unicode=False)
		self.presLan_en = gettext.translation('openplotter', currentpath+'/locale', languages=['en'])
		self.presLan_ca = gettext.translation('openplotter', currentpath+'/locale', languages=['ca'])
		self.presLan_es = gettext.translation('openplotter', currentpath+'/locale', languages=['es'])
		self.presLan_fr = gettext.translation('openplotter', currentpath+'/locale', languages=['fr'])
		self.language=self.data_conf.get('GENERAL', 'lang')
		if self.language=='en':self.presLan_en.install()
		if self.language=='ca':self.presLan_ca.install()
		if self.language=='es':self.presLan_es.install()
		if self.language=='fr':self.presLan_fr.install()
##########################language
		self.p = scrolled.ScrolledPanel(self, -1, style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
		self.p.SetAutoLayout(1)
		self.p.SetupScrolling()
		self.nb = wx.Notebook(self.p)

		self.page1 = wx.Panel(self.nb)
		self.page2 = wx.Panel(self.nb)
		self.page3 = wx.Panel(self.nb)
		self.page4 = wx.Panel(self.nb)
		self.page5 = wx.Panel(self.nb)
		self.page6 = wx.Panel(self.nb)
		self.page7 = wx.Panel(self.nb)

		self.nb.AddPage(self.page5, _('NMEA 0183'))
		self.nb.AddPage(self.page7, _('Signal K (beta)'))
		self.nb.AddPage(self.page3, _('WiFi access point'))
		self.nb.AddPage(self.page4, _('SDR-AIS'))
		self.nb.AddPage(self.page2, _('Calculate'))
		self.nb.AddPage(self.page6, _('Sensors'))
		self.nb.AddPage(self.page1, _('Startup'))

		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.p.SetSizer(sizer)

		self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.CreateStatusBar()
		self.Centre()
########menu###################
		self.menubar = wx.MenuBar()

		self.settings = wx.Menu()
		self.time_item1 = self.settings.Append(wx.ID_ANY, _('Set time zone'), _('Set time zone in the new window'))
		self.Bind(wx.EVT_MENU, self.time_zone, self.time_item1)
		self.time_item2 = self.settings.Append(wx.ID_ANY, _('Set time from NMEA'), _('Set system time from NMEA data'))
		self.Bind(wx.EVT_MENU, self.time_gps, self.time_item2)
		self.settings.AppendSeparator()
		self.gpsd_item1 = self.settings.Append(wx.ID_ANY, _('Set GPSD'), _('Set GPSD in the new window'))
		self.Bind(wx.EVT_MENU, self.reconfigure_gpsd, self.gpsd_item1)
		self.menubar.Append(self.settings, _('Settings'))

		self.lang = wx.Menu()
		self.lang_item1 = self.lang.Append(wx.ID_ANY, _('English'), _('Set English language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_en, self.lang_item1)
		self.lang_item2 = self.lang.Append(wx.ID_ANY, _('Catalan'), _('Set Catalan language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_ca, self.lang_item2)
		self.lang_item3 = self.lang.Append(wx.ID_ANY, _('Spanish'), _('Set Spanish language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_es, self.lang_item3)
		self.lang_item4 = self.lang.Append(wx.ID_ANY, _('French'), _('Set French language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_fr, self.lang_item4)
		self.menubar.Append(self.lang, _('Language'))

		self.helpm = wx.Menu()
		self.helpm_item1=self.helpm.Append(wx.ID_ANY, _('&About'), _('About OpenPlotter'))
		self.Bind(wx.EVT_MENU, self.OnAboutBox, self.helpm_item1)
		self.helpm_item2=self.helpm.Append(wx.ID_ANY, _('OpenPlotter online documentation'), _('OpenPlotter online documentation'))
		self.Bind(wx.EVT_MENU, self.op_doc, self.helpm_item2)
		self.helpm_item3=self.helpm.Append(wx.ID_ANY, _('OpenPlotter online guides'), _('OpenPlotter online guides'))
		self.Bind(wx.EVT_MENU, self.op_guides, self.helpm_item3)
		self.menubar.Append(self.helpm, _('&Help'))

		self.SetMenuBar(self.menubar)
###########################menu
########page1###################
		wx.StaticBox(self.page1, size=(670, 50), pos=(10, 10))
		wx.StaticText(self.page1, label=_('Delay (seconds)'), pos=(20, 30))
		self.delay = wx.TextCtrl(self.page1, -1, size=(55, 32), pos=(170, 23))
		self.button_ok_delay =wx.Button(self.page1, label=_('Ok'),size=(70, 32), pos=(250, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_delay, self.button_ok_delay)

		wx.StaticBox(self.page1, size=(330, 230), pos=(10, 70))
		self.startup_opencpn = wx.CheckBox(self.page1, label=_('OpenCPN'), pos=(20, 85))
		self.startup_opencpn.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_opencpn_nopengl = wx.CheckBox(self.page1, label=_('no OpenGL'), pos=(40, 110))
		self.startup_opencpn_nopengl.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_opencpn_fullscreen = wx.CheckBox(self.page1, label=_('fullscreen'), pos=(40, 135))
		self.startup_opencpn_fullscreen.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_multiplexer = wx.CheckBox(self.page1, label=_('NMEA 0183 multiplexer'), pos=(20, 170))
		self.startup_multiplexer.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_nmea_time = wx.CheckBox(self.page1, label=_('Set time from NMEA'), pos=(40, 195))
		self.startup_nmea_time.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_remote_desktop = wx.CheckBox(self.page1, label=_('Remote desktop'), pos=(20, 230))
		self.startup_remote_desktop.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_signalk = wx.CheckBox(self.page1, label=_('Signal K server (beta)'), pos=(20, 265))
		self.startup_signalk.Bind(wx.EVT_CHECKBOX, self.startup)

###########################page1
########page2###################
		wx.StaticBox(self.page2, size=(670, 50), pos=(10, 10))
		wx.StaticText(self.page2, label=_('NMEA generation rate (seconds)'), pos=(20, 30))
		self.rate_list = ['0.1', '0.25', '0.5', '0.75', '1', '1.5', '2']
		self.rate2= wx.ComboBox(self.page2, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(260, 23))
		self.button_ok_rate2 =wx.Button(self.page2, label=_('Ok'),size=(70, 32), pos=(350, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_rate2, self.button_ok_rate2)

		wx.StaticBox(self.page2, size=(330, 65), pos=(10, 70))
		self.mag_var = wx.CheckBox(self.page2, label=_('Magnetic variation'), pos=(20, 85))
		self.mag_var.Bind(wx.EVT_CHECKBOX, self.nmea_mag_var)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OPHDG'), pos=(20, 110))

		wx.StaticBox(self.page2, size=(330, 65), pos=(10, 135))
		self.heading_t = wx.CheckBox(self.page2, label=_('True heading'), pos=(20, 150))
		self.heading_t.Bind(wx.EVT_CHECKBOX, self.nmea_hdt)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OPHDT'), pos=(20, 175))

		wx.StaticBox(self.page2, label=_(' True wind '), size=(330, 130), pos=(350, 70))
		self.TW_STW = wx.CheckBox(self.page2, label=_('Use speed log'), pos=(360, 95))
		self.TW_STW.Bind(wx.EVT_CHECKBOX, self.TW)
		self.TW_SOG = wx.CheckBox(self.page2, label=_('Use GPS'), pos=(360, 125))
		self.TW_SOG.Bind(wx.EVT_CHECKBOX, self.TW)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OPMWV, $OPMWD'), pos=(360, 155))
###########################page2
########page3###################
		wx.StaticBox(self.page3, size=(400, 45), pos=(10, 10))
		self.wifi_enable = wx.CheckBox(self.page3, label=_('Enable WiFi access point'), pos=(20, 25))
		self.wifi_enable.Bind(wx.EVT_CHECKBOX, self.onwifi_enable)

		wx.StaticBox(self.page3, label=_(' Settings '), size=(400, 125), pos=(10, 60))

		self.available_wireless = []
		output=subprocess.check_output('iwconfig')
		for i in range (0, 10):
			ii=str(i)
			if 'wlan'+ii in output: self.available_wireless.append('wlan'+ii)
		self.wlan = wx.ComboBox(self.page3, choices=self.available_wireless, style=wx.CB_READONLY, size=(100, 32), pos=(20, 85))
		self.wlan_label=wx.StaticText(self.page3, label=_('WiFi device'), pos=(140, 90))

		self.passw = wx.TextCtrl(self.page3, -1, size=(100, 32), pos=(20, 120))
		self.passw_label=wx.StaticText(self.page3, label=_('Password \nminimum 8 characters required'), pos=(140, 120))

#Agregado----sin acceso a lenguaje (texto puesto en espanol)
		self.wifiap = wx.TextCtrl(self.page3, -1, size=(100, 32), pos=(20, 155))
		self.wifiap_label=wx.StaticText(self.page3, label=_('Dejar vacio o escribir un numero\npara el nombre del punto de acceso'), pos=(140, 155))
#============================================

		wx.StaticBox(self.page3, label=_(' Addresses '), size=(270, 265), pos=(415, 10))
		#self.ip_info=wx.StaticText(self.page3, label='', pos=(430, 35))
		self.ip_info = wx.TextCtrl(self.page3, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(260, 245), pos=(420, 25))
		self.ip_info.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		self.button_refresh_ip =wx.Button(self.page3, label=_('Refresh'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.show_ip_info, self.button_refresh_ip)
		
#Agregado----sin acceso a lenguaje (texto puesto en espanol)
		self.button_wifiap =wx.Button(self.page3, label=_('Grabar Nombre'), pos=(20, 285))
		self.Bind(wx.EVT_BUTTON, self.cambia_wifiap, self.button_wifiap)
#============================================

###########################page3
########page4###################
		wx.StaticBox(self.page4, size=(400, 45), pos=(10, 10))
		self.ais_sdr_enable = wx.CheckBox(self.page4, label=_('Enable AIS NMEA generation'), pos=(20, 25))
		self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

		wx.StaticBox(self.page4, label=_(' Settings '), size=(400, 150), pos=(10, 60))

		self.gain = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(150, 80))
		self.gain_label=wx.StaticText(self.page4, label=_('Gain'), pos=(20, 85))
		self.ppm = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(150, 115))
		self.correction_label=wx.StaticText(self.page4, label=_('Correction (ppm)'), pos=(20, 120))

		self.ais_frequencies1 = wx.CheckBox(self.page4, label=_('Channel A 161.975Mhz'), pos=(220, 80))
		self.ais_frequencies1.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)
		self.ais_frequencies2 = wx.CheckBox(self.page4, label=_('Channel B 162.025Mhz'), pos=(220, 115))
		self.ais_frequencies2.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)

		self.button_test_gain =wx.Button(self.page4, label=_('Calibration'), pos=(275, 165))
		self.Bind(wx.EVT_BUTTON, self.test_gain, self.button_test_gain)
		self.button_test_ppm =wx.Button(self.page4, label=_('Take a look'), pos=(150, 165))
		self.Bind(wx.EVT_BUTTON, self.test_ppm, self.button_test_ppm)

		wx.StaticBox(self.page4, label=_(' Fine calibration using GSM base stations '), size=(400, 100), pos=(10, 215))
		self.bands_label=wx.StaticText(self.page4, label=_('Band'), pos=(20, 245))
		self.bands_list = ['GSM850', 'GSM-R', 'GSM900', 'EGSM', 'DCS', 'PCS']
		self.band= wx.ComboBox(self.page4, choices=self.bands_list, style=wx.CB_READONLY, size=(100, 32), pos=(150, 240))
		self.band.SetValue('GSM900')
		self.check_bands =wx.Button(self.page4, label=_('Check band'), pos=(275, 240))
		self.Bind(wx.EVT_BUTTON, self.check_band, self.check_bands)
		self.channel_label=wx.StaticText(self.page4, label=_('Channel'), pos=(20, 280))
		self.channel = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(150, 275))
		self.check_channels =wx.Button(self.page4, label=_('Fine calibration'), pos=(275, 275))
		self.Bind(wx.EVT_BUTTON, self.check_channel, self.check_channels)
###########################page4
########page5###################
		wx.StaticBox(self.page5, label=_(' Inputs '), size=(670, 130), pos=(10, 10))
		self.list_input = CheckListCtrl(self.page5)
		self.list_input.SetPosition((15, 30))
		self.list_input.InsertColumn(0, _('Name'), width=130)
		self.list_input.InsertColumn(1, _('Type'), width=45)
		self.list_input.InsertColumn(2, _('Port/Address'), width=110)
		self.list_input.InsertColumn(3, _('Bauds/Port'))
		self.list_input.InsertColumn(4, _('Filter'))
		self.list_input.InsertColumn(5, _('Filtering'))
		self.add_serial_in =wx.Button(self.page5, label=_('+ serial'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_serial_input, self.add_serial_in)

		self.add_network_in =wx.Button(self.page5, label=_('+ network'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.add_network_input, self.add_network_in)

		self.button_delete_input =wx.Button(self.page5, label=_('delete'), pos=(585, 100))
		self.Bind(wx.EVT_BUTTON, self.delete_input, self.button_delete_input)

		wx.StaticBox(self.page5, label=_(' Outputs '), size=(670, 130), pos=(10, 145))
		self.list_output = CheckListCtrl(self.page5)
		self.list_output.SetPosition((15, 165))
		self.list_output.InsertColumn(0, _('Name'), width=130)
		self.list_output.InsertColumn(1, _('Type'), width=45)
		self.list_output.InsertColumn(2, _('Port/Address'), width=110)
		self.list_output.InsertColumn(3, _('Bauds/Port'))
		self.list_output.InsertColumn(4, _('Filter'))
		self.list_output.InsertColumn(5, _('Filtering'))
		self.add_serial_out =wx.Button(self.page5, label=_('+ serial'), pos=(585, 165))
		self.Bind(wx.EVT_BUTTON, self.add_serial_output, self.add_serial_out)

		self.add_network_out =wx.Button(self.page5, label=_('+ network'), pos=(585, 200))
		self.Bind(wx.EVT_BUTTON, self.add_network_output, self.add_network_out)

		self.button_delete_output =wx.Button(self.page5, label=_('delete'), pos=(585, 235))
		self.Bind(wx.EVT_BUTTON, self.delete_output, self.button_delete_output)

		self.show_output =wx.Button(self.page5, label=_('Show output'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output)
		self.restart =wx.Button(self.page5, label=_('Restart'), pos=(130, 285))
		self.Bind(wx.EVT_BUTTON, self.restart_multiplex, self.restart)
		self.button_apply =wx.Button(self.page5, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes, self.button_apply)
		self.button_cancel =wx.Button(self.page5, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes, self.button_cancel)
###########################page5
########page7###################
		wx.StaticBox(self.page7, label=_(' Inputs '), size=(670, 130), pos=(10, 10))
		self.inSK = wx.TextCtrl(self.page7, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(565, 102), pos=(15, 30))
		self.inSK.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
		self.inSK.SetValue(' NMEA 0183 - system_output  TCP  localhost  10110')

		wx.StaticBox(self.page7, label=_(' Outputs '), size=(670, 130), pos=(10, 145))
		self.outSK = wx.TextCtrl(self.page7, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(565, 102), pos=(15, 165))
		self.outSK.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
		self.outSK.SetValue(' http://localhost:3000/instrumentpanel\n http://localhost:3000/sailgauge\n http://localhost:3000/signalk/stream/v1?stream=delta')
		self.showpanels =wx.Button(self.page7, label=_('Panel'), pos=(585, 165))
		self.Bind(wx.EVT_BUTTON, self.signalKpanels, self.showpanels)
		self.showgauge =wx.Button(self.page7, label=_('Gauge'), pos=(585, 200))
		self.Bind(wx.EVT_BUTTON, self.signalKsailgauge, self.showgauge)

		self.show_outputSK =wx.Button(self.page7, label=_('Show output'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.signalKout, self.show_outputSK)
		self.button_restartSK =wx.Button(self.page7, label=_('Restart'), pos=(130, 285))
		self.Bind(wx.EVT_BUTTON, self.restartSK, self.button_restartSK)
###########################page7
########page6###################
		wx.StaticBox(self.page6, size=(670, 50), pos=(10, 10))
		wx.StaticText(self.page6, label=_('NMEA generation rate (seconds)'), pos=(20, 30))
		self.rate= wx.ComboBox(self.page6, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(260, 23))
		self.button_ok_rate =wx.Button(self.page6, label=_('Ok'),size=(70, 32), pos=(350, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_rate, self.button_ok_rate)

		wx.StaticBox(self.page6, size=(330, 90), pos=(10, 70))
		self.imu_tag=wx.StaticText(self.page6, label=_('Sensor detected: ')+_('none'), pos=(20, 90))
		self.button_calibrate_imu =wx.Button(self.page6, label=_('Calibrate'), pos=(240, 120))
		self.Bind(wx.EVT_BUTTON, self.calibrate_imu, self.button_calibrate_imu)
		self.heading = wx.CheckBox(self.page6, label=_('Heading'), pos=(20, 110))
		self.heading.Bind(wx.EVT_CHECKBOX, self.nmea_hdg)
		self.heading_nmea=wx.StaticText(self.page6, label=_('Generated NMEA: $OPHDG'), pos=(20, 135))

		wx.StaticBox(self.page6, size=(330, 90), pos=(10, 160))
		self.press_tag=wx.StaticText(self.page6, label=_('Sensor detected: ')+_('none'), pos=(20, 180))
		self.press_temp = wx.CheckBox(self.page6, label=_('Pressure'), pos=(20, 200))
		self.press_temp.Bind(wx.EVT_CHECKBOX, self.nmea_mda)
		self.press_nmea=wx.StaticText(self.page6, label=_('Generated NMEA: $OPMDA'), pos=(20, 225))

		wx.StaticBox(self.page6, size=(330, 90), pos=(350, 70))
		self.press_temp_log = wx.CheckBox(self.page6, label=_('Weather data logging'), pos=(360, 90))
		self.press_temp_log.Bind(wx.EVT_CHECKBOX, self.enable_press_temp_log)
		self.button_reset =wx.Button(self.page6, label=_('Reset'), pos=(470, 120))
		self.Bind(wx.EVT_BUTTON, self.reset_graph, self.button_reset)
		self.button_graph =wx.Button(self.page6, label=_('Show'), pos=(585, 120))
		self.Bind(wx.EVT_BUTTON, self.show_graph, self.button_graph)
###########################page6
		self.read_kplex_conf()
		self.set_layout_conf()
###########################layout



####definitions###################
	def read_conf(self):
		self.data_conf = ConfigParser.SafeConfigParser()
		self.data_conf.read(currentpath+'/openplotter.conf')

	def set_layout_conf(self):
		language=self.data_conf.get('GENERAL', 'lang')
		if language=='en': self.lang.Check(self.lang_item1.GetId(), True)
		if language=='ca': self.lang.Check(self.lang_item2.GetId(), True)
		if language=='es': self.lang.Check(self.lang_item3.GetId(), True)

		self.delay.SetValue(self.data_conf.get('STARTUP', 'delay'))

		if self.data_conf.get('STARTUP', 'opencpn')=='1': 
			self.startup_opencpn.SetValue(True)
		else:
			self.startup_opencpn_nopengl.Disable()
			self.startup_opencpn_fullscreen.Disable()
		if self.data_conf.get('STARTUP', 'opencpn_no_opengl')=='1': self.startup_opencpn_nopengl.SetValue(True)
		if self.data_conf.get('STARTUP', 'opencpn_fullscreen')=='1': self.startup_opencpn_fullscreen.SetValue(True)
		if self.data_conf.get('STARTUP', 'kplex')=='1': 
			self.startup_multiplexer.SetValue(True)
		else:
			self.startup_nmea_time.Disable()
		if self.data_conf.get('STARTUP', 'gps_time')=='1': self.startup_nmea_time.SetValue(True)
		if self.data_conf.get('STARTUP', 'x11vnc')=='1': self.startup_remote_desktop.SetValue(True)
		if self.data_conf.get('STARTUP', 'signalk')=='1': self.startup_signalk.SetValue(True)

#Agregado----- -------------------------------------
		archivo = '/home/pi/.config/openplotter/WiFiAP.conf' 
		if os.path.exists(archivo): 
			wifiarc=open(archivo,'r')
			wfap=wifiarc.readline()
			wifiarc.close()
			self.wifiap.SetValue(wfap.strip())
#===================================================

		if len(self.available_wireless)>0:
			self.wlan.SetValue(self.data_conf.get('WIFI', 'device'))
			self.passw.SetValue(self.data_conf.get('WIFI', 'password'))
			if self.data_conf.get('WIFI', 'enable')=='1':
				self.wifi_enable.SetValue(True)
				self.wlan.Disable()
				self.passw.Disable()
				self.wlan_label.Disable()
				self.passw_label.Disable()
		else:
			self.wifi_enable.Disable()
			self.wlan.Disable()
			self.passw.Disable()
			self.wlan_label.Disable()
			self.passw_label.Disable()			
		self.show_ip_info('')
		
		output=subprocess.check_output('lsusb')
		if 'DVB-T' in output:
			self.gain.SetValue(self.data_conf.get('AIS-SDR', 'gain'))
			self.ppm.SetValue(self.data_conf.get('AIS-SDR', 'ppm'))
			self.channel.SetValue(self.data_conf.get('AIS-SDR', 'gsm_channel'))
			if self.data_conf.get('AIS-SDR', 'enable')=='1': 
				self.ais_sdr_enable.SetValue(True)
				self.disable_sdr_controls()
			if self.data_conf.get('AIS-SDR', 'channel')=='a': self.ais_frequencies1.SetValue(True)
			if self.data_conf.get('AIS-SDR', 'channel')=='b': self.ais_frequencies2.SetValue(True)
		else:
			self.ais_sdr_enable.Disable()
			self.disable_sdr_controls()
			self.button_test_gain.Disable()
			self.button_test_ppm.Disable()
			self.bands_label.Disable()
			self.channel_label.Disable()
			self.band.Disable()
			self.channel.Disable()
			self.check_channels.Disable()
			self.check_bands.Disable()

		self.rate.SetValue(self.data_conf.get('STARTUP', 'nmea_rate_sen'))
		self.rate2.SetValue(self.data_conf.get('STARTUP', 'nmea_rate_cal'))

		if self.data_conf.get('STARTUP', 'nmea_mag_var')=='1': self.mag_var.SetValue(True)

		if self.data_conf.get('STARTUP', 'nmea_hdt')=='1': self.heading_t.SetValue(True)

		detected=subprocess.check_output(['python', currentpath+'/imu/check_sensors.py'], cwd=currentpath+'/imu')
		l_detected=detected.split('\n')
		imu_sensor=l_detected[0]
		press_sensor=l_detected[1]

		if 'none' in imu_sensor:
			self.heading.Disable()
			self.button_calibrate_imu.Disable()
			self.heading_nmea.Disable()
			if self.data_conf.get('STARTUP', 'nmea_hdg')=='1': 
				self.data_conf.set('STARTUP', 'nmea_hdg', '0')
				self.write_conf()
		else:
			self.imu_tag.SetLabel(_('Sensor detected: ')+imu_sensor)
			if self.data_conf.get('STARTUP', 'nmea_hdg')=='1': self.heading.SetValue(True)

		if 'none' in press_sensor:
			self.press_temp.Disable()
			self.press_nmea.Disable()
			self.press_temp_log.Disable()
			if self.data_conf.get('STARTUP', 'nmea_mda')=='1' or self.data_conf.get('STARTUP', 'press_temp_log')=='1': 
				self.data_conf.set('STARTUP', 'nmea_mda', '0')
				self.data_conf.set('STARTUP', 'press_temp_log', '0')
				self.write_conf()
		else:
			self.press_tag.SetLabel(_('Sensor detected: ')+press_sensor)
			if self.data_conf.get('STARTUP', 'nmea_mda')=='1': self.press_temp.SetValue(True)
			else: self.press_temp_log.Disable()
			if self.data_conf.get('STARTUP', 'press_temp_log')=='1': self.press_temp_log.SetValue(True)

		if self.data_conf.get('STARTUP', 'tw_stw')=='1': self.TW_STW.SetValue(True)
		if self.data_conf.get('STARTUP', 'tw_sog')=='1': self.TW_SOG.SetValue(True)

########MENU###################################	

	def time_zone(self,event):
		subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure tzdata'])
		self.SetStatusText(_('Set time zone in the new window'))

	def time_gps(self,event):
		self.SetStatusText(_('Waiting for NMEA time data in localhost:10110 ...'))
		time_gps_result=subprocess.check_output(['sudo', 'python', currentpath+'/time_gps.py'])
		msg=''
		re=time_gps_result.splitlines()
		for current in re:
			if 'Failed to connect with localhost:10110.' in current: msg+=_('Failed to connect with localhost:10110.\n')
			if 'Error: ' in current: msg+=current+'\n'
			if 'Unable to retrieve date or time from NMEA data.' in current: msg+=_('Unable to retrieve date or time from NMEA data.\n')
			if 'UTC' in current:
				if not '00:00:00' in current: msg+=current+'\n'
			if 'Date and time retrieved from NMEA data successfully.' in current: msg+=_('Date and time retrieved from NMEA data successfully.')

		self.SetStatusText('')
		self.ShowMessage(msg)

	def reconfigure_gpsd(self,event):
		subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure gpsd'])
		self.SetStatusText(_('Set GPSD in the new window'))
	
	def clear_lang(self):
		self.lang.Check(self.lang_item1.GetId(), False)
		self.lang.Check(self.lang_item2.GetId(), False)
		self.lang.Check(self.lang_item3.GetId(), False)
		self.lang.Check(self.lang_item4.GetId(), False)
		self.ShowMessage(_('The selected language will be enabled when you restart'))
	
	def lang_en(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item1.GetId(), True)
		self.data_conf.set('GENERAL', 'lang', 'en')
		self.write_conf()
	def lang_ca(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item2.GetId(), True)
		self.data_conf.set('GENERAL', 'lang', 'ca')
		self.write_conf()
	def lang_es(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item3.GetId(), True)
		self.data_conf.set('GENERAL', 'lang', 'es')
		self.write_conf()
	def lang_fr(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item4.GetId(), True)
		self.data_conf.set('GENERAL', 'lang', 'fr')
		self.write_conf()

	def OnAboutBox(self, e):
		description = _("OpenPlotter is a DIY, open-source, low-cost, low-consumption, modular and scalable sailing platform to run on ARM boards.")			
		licence = """This program is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 2 of 
the License, or any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program.  If not, see http://www.gnu.org/licenses/"""

		info = wx.AboutDialogInfo()
		info.SetName('OpenPlotter')
		info.SetVersion(self.data_conf.get('GENERAL', 'version'))
		info.SetDescription(description)
		info.SetCopyright('2013 - 2015 Sailoog')
		info.SetWebSite('http://www.sailoog.com')
		info.SetLicence(licence)
		info.AddDeveloper('Sailoog\nhttp://github.com/sailoog/openplotter\n-------------------\nOpenCPN: http://opencpn.org/ocpn/\nzyGrib: http://www.zygrib.org/\nMultiplexer: http://www.stripydog.com/kplex/index.html\nrtl-sdr: http://sdr.osmocom.org/trac/wiki/rtl-sdr\naisdecoder: http://www.aishub.net/aisdecoder-via-sound-card.html\ngeomag: http://github.com/cmweiss/geomag\nIMU sensor: http://github.com/richards-tech/RTIMULib\nNMEA parser: http://github.com/Knio/pynmea2\n\n')
		info.AddDocWriter('Sailoog\n\nDocumentation: http://sailoog.gitbooks.io/openplotter-documentation/\nGuides: http://sailoog.dozuki.com/c/OpenPlotter')
		info.AddArtist('Sailoog')
		info.AddTranslator('Catalan, English and Spanish by Sailoog\nFrench by Nicolas Janvier.')
		wx.AboutBox(info)

	def op_doc(self, e):
		url = "http://sailoog.gitbooks.io/openplotter-documentation/"
		webbrowser.open(url,new=2)

	def op_guides(self, e):
		url = "http://sailoog.dozuki.com/c/OpenPlotter"
		webbrowser.open(url,new=2)

########startup###################################	
	def ok_delay(self, e):
		delay=self.delay.GetValue()
		if not re.match('^[0-9]*$', delay):
				self.ShowMessage(_('You can enter only numbers.'))
				return
		else:
			if delay != '0': delay = delay.lstrip('0')
			self.data_conf.set('STARTUP', 'delay', delay)
			self.ShowMessage(_('Startup delay set to ')+delay+_(' seconds'))
			self.write_conf()

	def startup(self, e):

		if self.startup_opencpn.GetValue():
			self.startup_opencpn_nopengl.Enable()
			self.startup_opencpn_fullscreen.Enable()
			self.data_conf.set('STARTUP', 'opencpn', '1')
		else:
			self.startup_opencpn_nopengl.Disable()
			self.startup_opencpn_fullscreen.Disable()
			self.data_conf.set('STARTUP', 'opencpn', '0')

		if self.startup_opencpn_nopengl.GetValue():
			self.data_conf.set('STARTUP', 'opencpn_no_opengl', '1')
		else:
			self.data_conf.set('STARTUP', 'opencpn_no_opengl', '0')

		if self.startup_opencpn_fullscreen.GetValue():
			self.data_conf.set('STARTUP', 'opencpn_fullscreen', '1')
		else:
			self.data_conf.set('STARTUP', 'opencpn_fullscreen', '0')

		if self.startup_multiplexer.GetValue():
			self.startup_nmea_time.Enable()
			self.data_conf.set('STARTUP', 'kplex', '1')
		else:
			self.startup_nmea_time.Disable()
			self.data_conf.set('STARTUP', 'kplex', '0')

		if self.startup_nmea_time.GetValue():
			self.data_conf.set('STARTUP', 'gps_time', '1')
		else:
			self.data_conf.set('STARTUP', 'gps_time', '0')

		if self.startup_remote_desktop.GetValue():
			self.data_conf.set('STARTUP', 'x11vnc', '1')
		else:
			self.data_conf.set('STARTUP', 'x11vnc', '0')

		if self.startup_signalk.GetValue():
			self.data_conf.set('STARTUP', 'signalk', '1')
		else:
			self.data_conf.set('STARTUP', 'signalk', '0')

		self.write_conf()

########WIFI###################################	


	def onwifi_enable (self, e):
		self.SetStatusText(_('Configuring NMEA WiFi server, wait please...'))
		isChecked = self.wifi_enable.GetValue()
		wlan=self.wlan.GetValue()
		passw=self.passw.GetValue()
		if isChecked:
			self.enable_disable_wifi(1)
			if len(passw)>=8:
				wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '1', wlan, passw])
			else:
				wifi_result=_('Your password must have a minimum of 8 characters.')
				self.enable_disable_wifi(0)
		else: 
			self.enable_disable_wifi(0)
			wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '0', wlan, passw])
			
		msg=wifi_result
		if 'WiFi access point failed.' in msg:
			self.enable_disable_wifi(0)
			self.data_conf.set('WIFI', 'device', '')
			self.data_conf.set('WIFI', 'password', '')
		if'WiFi access point started.' in msg:
			wlan=self.wlan.GetValue()
			passw=self.passw.GetValue()
			self.data_conf.set('WIFI', 'device', wlan)
			self.data_conf.set('WIFI', 'password', passw)
		msg=msg.replace('WiFi access point failed.', _('WiFi access point failed.'))
		msg=msg.replace('WiFi access point started.', _('WiFi access point started.'))
		msg=msg.replace('WiFi access point stopped.', _('WiFi access point stopped.'))
		self.SetStatusText('')
		self.ShowMessage(msg)
		self.write_conf()
		self.show_ip_info('')

	def show_ip_info(self, e):
#Agregado y Modificado--------------------
		archivo = '/home/pi/.config/openplotter/WiFiAP.conf'
		wfap=''
		if os.path.exists(archivo): 
			wifiarc=open(archivo,'r')
			wfap=wifiarc.readline()
			wifiarc.close()
		out=_('OpenPlotter'+wfap+'\n')
		out+=_('____________________\n')
#========================================
		ip_info=subprocess.check_output(['hostname', '-I'])
		out=_(' NMEA 0183:\n')
		ips=ip_info.split()
		for ip in ips:
			out+=ip+':10110\n'
		out+=_('\n Remote desktop:\n')
		for ip in ips:
			out+=ip+':5900\n'
		out+=_('\n Signal K panel:\n')
		for ip in ips:
			out+=ip+':3000/instrumentpanel\n'
		out+=_('\n Signal K gauge:\n')
		for ip in ips:
			out+=ip+':3000/sailgauge\n'
		out+=_('\n Signal K WebSocket:\n')
		for ip in ips:
			out+=ip+':3000/signalk/stream/v1?stream=delta\n'
		self.ip_info.SetValue(out)

	def enable_disable_wifi(self, s):
		if s==1:
			self.wlan.Disable()
			self.passw.Disable()
			self.wlan_label.Disable()
			self.passw_label.Disable()
			self.wifi_enable.SetValue(True)
			self.data_conf.set('WIFI', 'enable', '1')
		else:
			self.wlan.Enable()
			self.passw.Enable()
			self.wlan_label.Enable()
			self.passw_label.Enable()
			self.wifi_enable.SetValue(False)
			self.data_conf.set('WIFI', 'enable', '0')

#Agregado----sin acceso a lenguaje (texto puesto en espanol)
	def cambia_wifiap(self,event):
		wfapi=self.wifiap.GetValue()
		wifiarc=open('/home/pi/.config/openplotter/WiFiAP.conf','w')
		wifiarc.write(wfapi)
		wifiarc.close()
		msg=_('Fue grabado el nombre del punto de acceso WiFi como:   OpenPlotter'+wfapi)
		self.ShowMessage(msg)
# =======================================

########SDR-AIS###################################	


	def kill_sdr(self):
		subprocess.call(['pkill', '-9', 'aisdecoder'])
		subprocess.call(['pkill', '-9', 'rtl_fm'])
		subprocess.call(['pkill', '-f', 'waterfall.py'])
		subprocess.call(['pkill', '-9', 'rtl_test'])
		subprocess.call(['pkill', '-9', 'kal'])

	def enable_sdr_controls(self):
		self.gain.Enable()
		self.ppm.Enable()
		self.ais_frequencies1.Enable()
		self.ais_frequencies2.Enable()
		self.gain_label.Enable()
		self.correction_label.Enable()
		self.ais_sdr_enable.SetValue(False)
		self.data_conf.set('AIS-SDR', 'enable', '0')
		self.write_conf()

	def disable_sdr_controls(self):
		self.gain.Disable()
		self.ppm.Disable()
		self.ais_frequencies1.Disable()
		self.ais_frequencies2.Disable()
		self.gain_label.Disable()
		self.correction_label.Disable()
	
	def ais_frequencies(self, e):
		sender = e.GetEventObject()
		self.ais_frequencies1.SetValue(False)
		self.ais_frequencies2.SetValue(False)
		sender.SetValue(True)

	def OnOffAIS(self, e):
		self.kill_sdr()
		isChecked = self.ais_sdr_enable.GetValue()
		if isChecked:
			self.disable_sdr_controls() 
			gain=self.gain.GetValue()
			ppm=self.ppm.GetValue()
			frecuency='161975000'
			channel='a'
			if self.ais_frequencies2.GetValue(): 
				frecuency='162025000'
				channel='b'
			rtl_fm=subprocess.Popen(['rtl_fm', '-f', frecuency, '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
			aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
			self.data_conf.set('AIS-SDR', 'enable', '1')
			self.data_conf.set('AIS-SDR', 'gain', gain)
			self.data_conf.set('AIS-SDR', 'ppm', ppm)
			self.data_conf.set('AIS-SDR', 'channel', channel)
			msg=_('SDR-AIS reception enabled')
		else: 
			self.enable_sdr_controls()
			self.data_conf.set('AIS-SDR', 'enable', '0')
			msg=_('SDR-AIS reception disabled')
		self.write_conf()
		self.SetStatusText('')
		self.ShowMessage(msg)

	def test_ppm(self,event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain='25'
		if self.gain.GetValue():
			gain=self.gain.GetValue()
			gain=gain.replace(',', '.')
		ppm='0'
		if self.ppm.GetValue():
			ppm=self.ppm.GetValue()
			ppm=ppm.replace(',', '.')
		channel='a'
		if self.ais_frequencies2.GetValue(): channel='b'
		w_open=subprocess.Popen(['python', currentpath+'/waterfall.py', gain, ppm, channel])
		msg=_('SDR-AIS reception disabled.\nAfter checking the new window enable SDR-AIS reception again.')
		self.ShowMessage(msg)

	def test_gain(self,event):
		self.kill_sdr()
		self.enable_sdr_controls()
		subprocess.Popen(['lxterminal', '-e', 'rtl_test', '-p'])
		msg=_('SDR-AIS reception disabled.\nCheck the new window. Copy the maximum supported gain value. Wait for ppm value to stabilize and copy it too.')
		self.ShowMessage(msg)

	def check_band(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain=self.gain.GetValue()
		ppm=self.ppm.GetValue()
		band=self.band.GetValue()
		subprocess.Popen(("lxterminal -e 'bash -c \"kal -s "+band+" -g "+gain+" -e "+ppm+"; echo 'Press [ENTER] to close the window'; read -p ---------------------------------; exit 0; exec bash\"'"), shell=True)
		msg=_('Wait for the system to check the band and select the strongest channel (power). If you do not find any channel try another band.')
		self.ShowMessage(msg)

	def check_channel(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain=self.gain.GetValue()
		ppm=self.ppm.GetValue()
		channel=self.channel.GetValue()
		if channel:
			subprocess.Popen(("lxterminal -e 'bash -c \"kal -c "+channel+" -g "+gain+" -e "+ppm+"; echo 'Press [ENTER] to close the window'; read -p ---------------------------------; exit 0; exec bash\"'"), shell=True)
			msg=_('Wait for the system to calculate the ppm value with the selected channel. Put the obtained value in "Correction (ppm)" field and enable SDR-AIS reception again.')
			self.data_conf.set('AIS-SDR', 'gsm_channel', channel)
			self.write_conf()
			self.ShowMessage(msg)

########multimpexer###################################	

	def show_output_window(self,event):
		close=subprocess.call(['pkill', '-f', 'output.py'])
		show_output=subprocess.Popen(['python', currentpath+'/output.py', self.language])

	def restart_multiplex(self,event):
		self.restart_kplex()
		self.read_kplex_conf()

	def restart_kplex(self):
		self.SetStatusText(_('Closing Kplex'))
		subprocess.call(["pkill", '-9', "kplex"])
		subprocess.Popen('kplex')
		self.SetStatusText(_('Kplex restarted'))

	def cancel_changes(self,event):
		self.read_kplex_conf()

	def read_kplex_conf(self):
		self.inputs = []
		self.outputs = []
		try:
			file=open(home+'/.kplex.conf', 'r')
			data=file.readlines()
			file.close()

			l_tmp=[None]*8
			for index, item in enumerate(data):
				if re.search('\[*\]', item):
					if l_tmp[0]=='in': self.inputs.append(l_tmp)
					if l_tmp[0]=='out': self.outputs.append(l_tmp)
					l_tmp=[None]*8
					l_tmp[5]='none'
					l_tmp[6]='nothing'
					if '[serial]' in item: l_tmp[2]='Serial'
					if '[tcp]' in item: l_tmp[2]='TCP'
					if '[udp]' in item: l_tmp[2]='UDP'
					if '#[' in item: l_tmp[7]='0'
					else: l_tmp[7]='1'
				if 'direction=in' in item:
					l_tmp[0]='in'
				if 'direction=out' in item:
					l_tmp[0]='out'
				if 'name=' in item and 'filename=' not in item:
					l_tmp[1]=self.extract_value(item)
				if 'address=' in item or 'filename=' in item:
					l_tmp[3]=self.extract_value(item)
				if 'port=' in item or 'baud=' in item:
					l_tmp[4]=self.extract_value(item)
				if 'filter=' in item and '-all' in item:
					l_tmp[5]='accept'
					l_tmp[6]=self.extract_value(item)
				if 'filter=' in item and '-all' not in item:
					l_tmp[5]='ignore'
					l_tmp[6]=self.extract_value(item)

			if l_tmp[0]=='in': self.inputs.append(l_tmp)
			if l_tmp[0]=='out': self.outputs.append(l_tmp)
			self.write_inputs()
			self.write_outputs()

		except IOError:
			self.ShowMessage(_('Multiplexer configuration file does not exist. Add inputs and apply changes.'))

	def extract_value(self,data):
		option, value =data.split('=')
		value=value.strip()
		return value

	def write_inputs(self):
		self.list_input.DeleteAllItems()
		for i in self.inputs:
			if i[1]: index = self.list_input.InsertStringItem(sys.maxint, i[1])
			if i[2]: self.list_input.SetStringItem(index, 1, i[2])
			if i[3]: self.list_input.SetStringItem(index, 2, i[3])
			else: self.list_input.SetStringItem(index, 2, 'localhost')
			if i[4]: self.list_input.SetStringItem(index, 3, i[4])
			if i[5]:
				if i[5]=='none': self.list_input.SetStringItem(index, 4, _('none'))
				if i[5]=='accept': self.list_input.SetStringItem(index, 4, _('accept'))
				if i[5]=='ignore': self.list_input.SetStringItem(index, 4, _('ignore'))
			if i[6]=='nothing':
				self.list_input.SetStringItem(index, 5, _('nothing'))
			else:
				filters=i[6].replace(':-all', '')
				filters=filters.replace('+', '')
				filters=filters.replace('-', '')
				filters=filters.replace(':', ',')
				self.list_input.SetStringItem(index, 5, filters)
			if i[7]=='1': self.list_input.CheckItem(index)
	
	def write_outputs(self):
		self.list_output.DeleteAllItems()
		for i in self.outputs:
			if i[1]: index = self.list_output.InsertStringItem(sys.maxint, i[1])
			if i[2]: self.list_output.SetStringItem(index, 1, i[2])
			if i[3]: self.list_output.SetStringItem(index, 2, i[3])
			else: self.list_output.SetStringItem(index, 2, 'localhost')
			if i[4]: self.list_output.SetStringItem(index, 3, i[4])
			if i[5]:
				if i[5]=='none': self.list_output.SetStringItem(index, 4, _('none'))
				if i[5]=='accept': self.list_output.SetStringItem(index, 4, _('accept'))
				if i[5]=='ignore': self.list_output.SetStringItem(index, 4, _('ignore'))
			if i[6]=='nothing':
				self.list_output.SetStringItem(index, 5, _('nothing'))
			else:
				filters=i[6].replace(':-all', '')
				filters=filters.replace('+', '')
				filters=filters.replace('-', '')
				filters=filters.replace(':', ',')
				self.list_output.SetStringItem(index, 5, filters)
			if i[7]=='1': self.list_output.CheckItem(index)

	def apply_changes(self,event):
		data='# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Editing this file by openplotter GUI, can eliminate manual settings.\n# You should not modify defaults.\n\n'

		data=data+'###defaults\n\n[udp]\nname=system_input\ndirection=in\noptional=yes\nport=10110\n\n'
		data=data+'[tcp]\nname=system_output\ndirection=out\nmode=server\nport=10110\n\n###end defaults\n\n'

		for index,item in enumerate(self.inputs):
			if 'system_input' not in item[1]:
				if self.list_input.IsChecked(index): state=''
				else: state='#'
				if 'Serial' in item[2]:
					data=data+state+'[serial]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'filename='+item[3]+'\n'+state+'baud='+item[4]+'\n\n'
				if 'TCP' in item[2]:
					data=data+state+'[tcp]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'mode=client\n'+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n'
					data=data+state+'persist=yes\n'+state+'retry=10\n\n'				
				if 'UDP' in item[2]:
					data=data+state+'[udp]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'
		

		for index,item in enumerate(self.outputs):
			if 'system_output' not in item[1]:
				if self.list_output.IsChecked(index): state=''
				else: state='#'
				if 'Serial' in item[2]:
					data=data+state+'[serial]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'filename='+item[3]+'\n'+state+'baud='+item[4]+'\n\n'
				if 'TCP' in item[2]:
					data=data+state+'[tcp]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'mode=server\n'+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'				
				if 'UDP' in item[2]:
					data=data+state+'[udp]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'
		
		
		file = open(home+'/.kplex.conf', 'w')
		file.write(data)
		file.close()
		self.restart_kplex()
		self.read_kplex_conf()

	def delete_input(self,event):
		num = len(self.inputs)
		for i in range(num):
			if self.list_input.IsSelected(i):
				del self.inputs[i]
		self.write_inputs()

	def delete_output(self,event):
		num = len(self.outputs)
		for i in range(num):
			if self.list_output.IsSelected(i):
				del self.outputs[i]
		self.write_outputs()

	def process_name(self,r):
		list_tmp=[]
		l=r.split(',')
		for item in l:
			item=item.strip()
			list_tmp.append(item)
		name=list_tmp[1]
		found=False
		for sublist in self.inputs:
			if sublist[1] == name:
				found=True
		for sublist in self.outputs:
			if sublist[1] == name:
				found=True
		if found==True:
			self.ShowMessage(_('This name already exists.'))
			return False
		else:
			return list_tmp
	
	def add_serial_input(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', self.language, 'in', 'serial'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_port=list_tmp[3]
				for sublist in self.inputs:
					if sublist[3] == new_port: 
						self.ShowMessage(_('This input is already in use.'))
						return
				self.inputs.append(list_tmp)
				self.write_inputs()


	def add_serial_output(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', self.language, 'out', 'serial'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_port=list_tmp[3]
				for sublist in self.outputs:
					if sublist[3] == new_port: 
						self.ShowMessage(_('This output is already in use.'))
						return
				self.outputs.append(list_tmp)
				self.write_outputs()

	
	def add_network_input(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', self.language, 'in', 'network'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_address_port=str(list_tmp[2])+str(list_tmp[3])+str(list_tmp[4])
				for sublist in self.inputs:					
					old_address_port=str(sublist[2])+str(sublist[3])+str(sublist[4])
					if old_address_port == new_address_port: 
						self.ShowMessage(_('This input is already in use.'))
						return
				self.inputs.append(list_tmp)
				self.write_inputs()


	def add_network_output(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', self.language, 'out', 'network'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_address_port=str(list_tmp[2])+str(list_tmp[3])+str(list_tmp[4])
				for sublist in self.outputs:					
					old_address_port=str(sublist[2])+str(sublist[3])+str(sublist[4])
					if old_address_port == new_address_port: 
						self.ShowMessage(_('This output is already in use.'))
						return
				self.outputs.append(list_tmp)
				self.write_outputs()


######################################multiplexer


	def write_conf(self):
		with open(currentpath+'/openplotter.conf', 'wb') as configfile:
			self.data_conf.write(configfile)

	def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)

######################################sensors
	def start_sensors(self):
		self.write_conf()
		subprocess.call(['pkill', '-f', 'sensors.py'])
		if self.heading.GetValue() or self.press_temp.GetValue():
			subprocess.Popen(['python', currentpath+'/sensors.py'], cwd=currentpath+'/imu')

	def ok_rate(self, e):
		rate=self.rate.GetValue()
		self.data_conf.set('STARTUP', 'nmea_rate_sen', rate)
		self.start_sensors()
		self.ShowMessage(_('Generation rate set to ')+rate+_(' seconds'))

	def ok_rate2(self, e):
		rate=self.rate2.GetValue()
		self.data_conf.set('STARTUP', 'nmea_rate_cal', rate)
		self.start_calculate()
		self.ShowMessage(_('Generation rate set to ')+rate+_(' seconds'))
		
	def nmea_hdg(self, e):
		subprocess.call(['pkill', 'RTIMULibDemoGL'])
		sender = e.GetEventObject()
		if sender.GetValue(): self.data_conf.set('STARTUP', 'nmea_hdg', '1')
		else: self.data_conf.set('STARTUP', 'nmea_hdg', '0')
		self.start_sensors()
	
	def calibrate_imu(self, e):
		self.heading.SetValue(False)
		self.press_temp.SetValue(False)
		self.press_temp_log.SetValue(False)
		self.press_temp_log.Disable()
		self.data_conf.set('STARTUP', 'nmea_hdg', '0')
		self.data_conf.set('STARTUP', 'nmea_mda', '0')
		self.data_conf.set('STARTUP', 'press_temp_log', '0')
		self.start_sensors()
		subprocess.call(['pkill', 'RTIMULibDemoGL'])
		subprocess.Popen('RTIMULibDemoGL', cwd=currentpath+'/imu')
		msg=_('Heading, temperature and pressure generation disabled.\nAfter calibrating, enable heading, temperature and pressure generation again.')
		self.ShowMessage(msg)
	
	def nmea_mda(self, e):
		subprocess.call(['pkill', 'RTIMULibDemoGL'])
		sender = e.GetEventObject()
		if sender.GetValue():     
			self.press_temp_log.Enable()
			self.data_conf.set('STARTUP', 'nmea_mda', '1')
		else:
			self.press_temp_log.SetValue(False)
			self.press_temp_log.Disable()
			self.data_conf.set('STARTUP', 'nmea_mda', '0')
			self.data_conf.set('STARTUP', 'press_temp_log', '0')
		self.start_sensors()

	def enable_press_temp_log(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.data_conf.set('STARTUP', 'press_temp_log', '1')
		else: self.data_conf.set('STARTUP', 'press_temp_log', '0')
		self.start_sensors()

	def show_graph(self, e):
		subprocess.call(['pkill', '-f', 'graph.py'])
		subprocess.Popen(['python', currentpath+'/graph.py'])

	def	reset_graph(self, e):
		data=''
		file = open(currentpath+'/weather_log.csv', 'w')
		file.write(data)
		file.close()
		self.start_sensors()
		self.ShowMessage(_('Weather log restarted'))
######################################calculate
	def start_calculate(self):
		self.write_conf()
		subprocess.call(['pkill', '-f', 'calculate.py'])
		if self.mag_var.GetValue() or self.heading_t.GetValue() or self.TW_STW.GetValue() or self.TW_SOG.GetValue():
			subprocess.Popen(['python', currentpath+'/calculate.py'])

	def nmea_mag_var(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.data_conf.set('STARTUP', 'nmea_mag_var', '1')
		else: self.data_conf.set('STARTUP', 'nmea_mag_var', '0')
		self.start_calculate()

	def nmea_hdt(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.data_conf.set('STARTUP', 'nmea_hdt', '1')
		else: self.data_conf.set('STARTUP', 'nmea_hdt', '0')
		self.start_calculate()

	def	TW(self, e):
		sender = e.GetEventObject()
		state=sender.GetValue()
		self.TW_STW.SetValue(False)
		self.TW_SOG.SetValue(False)
		self.data_conf.set('STARTUP', 'tw_stw', '0')
		self.data_conf.set('STARTUP', 'tw_sog', '0')
		if state: sender.SetValue(True)
		if self.TW_STW.GetValue(): self.data_conf.set('STARTUP', 'tw_stw', '1')
		if self.TW_SOG.GetValue(): self.data_conf.set('STARTUP', 'tw_sog', '1')
		self.start_calculate()
######################################Signal K
	def signalKpanels(self, e):
		url = 'http://localhost:3000/instrumentpanel'
		webbrowser.open(url,new=2)

	def signalKsailgauge(self, e):
		url = 'http://localhost:3000/sailgauge'
		webbrowser.open(url,new=2)

	def signalKout(self, e):
		url = 'http://localhost:3000/examples/consumer-example.html'
		webbrowser.open(url,new=2)

	def restartSK(self, e):
		self.SetStatusText(_('Closing Signal K server'))
		subprocess.call(["pkill", '-9', "node"])
		subprocess.Popen(home+'/.config/signalk-server-node/bin/nmea-from-10110', cwd=home+'/.config/signalk-server-node')
		self.SetStatusText(_('Signal K server restarted'))
#######################definitions



#Main#############################
if __name__ == "__main__":
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()
