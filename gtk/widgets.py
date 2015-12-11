# - coding: utf-8 -
#
# Copyright (C) 2009 Alejandro Ayuso
#
# This file is part of the Monocaffe Connection Manager
#
# Monocaffe Connection Manager is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Monocaffe Connection Manager is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the Monocaffe Connection Manager. If not, see
# <http://www.gnu.org/licenses/>.
#

import gtk
import pygtk
pygtk.require("2.0")

from mcm.common.connections import *
from mcm.common.utils import *
from mcm.common.configurations import McmConfig
import mcm.common.constants

'''
Dialogs for Monocaffe Connections Manager
'''

class UtilityDialogs(object):
    """
    Class that defines the methods used to display MessageDialog dialogs
    to the user
    """

    def __init__(self):
        pass

    def show_question_dialog(self, title, message):
        """Display a Warning Dialog and return the response to the caller"""
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, title)
        dialog.format_secondary_text(message)
        response = dialog.run()
        dialog.destroy()
        return response

    def show_error_dialog(self, title, message):
        """Display an error dialog to the user"""
        self.show_common_dialog(title, message, gtk.MESSAGE_ERROR)

    def show_info_dialog(self, title, message):
        """Display an error dialog to the user"""
        self.show_common_dialog(title, message, gtk.MESSAGE_INFO)

    def show_common_dialog(self, title, message, icon):
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, icon, gtk.BUTTONS_OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


class AddConnectionDialog(object):

    def __init__(self, id, aliases, groups, types, cx=None):
        #I need a list with the aliases so I can validate the name
        self.response = gtk.RESPONSE_CANCEL
        self.default_color = DefaultColorSettings().base_color
        self.new_connection = None
        self.error = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_new_cx)
        self.aliases = aliases
        self.id = id
        self.widgets = {
                        'dlg': self.builder.get_object('dialog_add'),
                        'types_combobox': self.builder.get_object('types_combobox'),
                        'group_combobox': self.builder.get_object('group_combobox'),
                        'user_entry1': self.builder.get_object('user_entry1'),
                        'host_entry1': self.builder.get_object('host_entry1'),
                        'port_entry1': self.builder.get_object('port_entry1'),
                        'options_entry1': self.builder.get_object('options_entry1'),
                        'description_entry1': self.builder.get_object('description_entry1'),
                        'password_entry1': self.builder.get_object('password_entry1'),
                        'alias_entry1': self.builder.get_object('alias_entry1'),
                        'title_label': self.builder.get_object('title_label'),
                        }
        events = {
                        'response': self.cancel_event,
                        'on_button_cancel_clicked': self.cancel_event,
                        'on_button_save_clicked': self.save_event,
                        'on_alias_entry1_changed': self.validate_alias,
                        'on_types_combobox_changed': self.insert_default_options,
                }
        self.builder.connect_signals(events)

        # Glade3 changes the behaviour of the comboboxentry widget.

        g_entry = self.widgets['group_combobox'].get_child()
        self.widgets['group_entry1'] = g_entry

        if cx:
            self.aliases.remove(cx.alias)
            self.init_combos(groups, types, cx.group, cx.get_type())
            self.fill_fields(cx)
        else:
            self.init_combos(groups, types)

    def run(self):
        dlg = self.widgets['dlg']
        dlg.run()
        dlg.destroy()

    def init_combos(self, groups, types, active_grp=None, active_type=None):
        cb_groups = self.widgets['group_combobox']
        cb_types = self.widgets['types_combobox']
        grp_index = self.set_model_from_list(cb_groups, groups)
        types_index = self.set_model_from_list(cb_types, types)
        if active_grp and active_type:
            active = grp_index[active_grp]
            cb_groups.set_active(active)
            active = types_index[active_type]
            cb_types.set_active(active)


    def set_model_from_list(self, cb, items):
        """Setup a ComboBox or ComboBoxEntry based on a list of strings."""           
        model = gtk.ListStore(str)
        index = {}
        j = 0
        for i in items:
            model.append([i])
            index[i] = j 
            j += 1
        cb.set_model(model)
        if type(cb) == gtk.ComboBoxEntry:
            cb.set_text_column(0)
        elif type(cb) == gtk.ComboBox:
            cell = gtk.CellRendererText()
            cb.pack_start(cell, True)
            cb.add_attribute(cell, 'text', 0)
        return index

    def insert_default_options(self, widget):
        type = widget.get_active_text()
        conf = McmConfig()
        config = ""
        if type == 'SSH':
            not_used, config = conf.get_ssh_conf()
        elif type == 'VNC':
            not_used, config = conf.get_vnc_conf()
        elif type == 'RDP':
            not_used, config = conf.get_rdp_conf()
        elif type == 'TELNET':
            not_used, config = conf.get_telnet_conf()
        elif type == 'FTP':
            not_used, config = conf.get_ftp_conf()

        opts_entry = self.widgets['options_entry1']
        opts_entry.set_text(config)

    def cancel_event(self, widget):
        pass

    def save_event(self, widget):
        if self.error == None:
            self.response = gtk.RESPONSE_OK
            cx_type = self.widgets['types_combobox'].get_active_text()
            cx_group = self.widgets['group_entry1'].get_text()
            cx_user = self.widgets['user_entry1'].get_text()
            cx_host = self.widgets['host_entry1'].get_text()
            cx_alias = self.widgets['alias_entry1'].get_text()
            cx_port = self.widgets['port_entry1'].get_text()
            cx_desc = self.widgets['description_entry1'].get_text()
            cx_pass = self.widgets['password_entry1'].get_text()
            cx_options = self.widgets['options_entry1'].get_text()
            self.new_connection = connections_factory(self.id, cx_type, cx_user, cx_host, cx_alias, cx_pass, cx_port, cx_group, cx_options, cx_desc)

    def validate_alias(self, widget):
        alias = widget.get_text()
        entry = self.widgets['alias_entry1']
        if alias in self.aliases:
            self.error = constants.alias_error
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFADAD"))
            widget.set_tooltip_text(self.error)
        else:
            self.error = None
            widget.modify_base(gtk.STATE_NORMAL, self.default_color)
            widget.set_tooltip_text(constants.alias_tooltip)

    def validate_port(self, widget):
        pass

    def fill_fields(self, cx):
        """Fill the dialog fields so we can use it to edit a connection"""
        user = self.widgets['user_entry1']
        host = self.widgets['host_entry1']
        alias = self.widgets['alias_entry1']
        port = self.widgets['port_entry1']
        desc = self.widgets['description_entry1']
        fpass = self.widgets['password_entry1']
        options = self.widgets['options_entry1']

        user.set_text(cx.user)
        host.set_text(cx.host) 
        alias.set_text(cx.alias)
        port.set_text(cx.port)
        desc.set_text(cx.description)
        fpass.set_text(cx.password)
        options.set_text(cx.options)

class FileSelectDialog(object):
    CSV = 1
    HTML = 2
    DIR = 3

    def __init__(self, model=0):
        self.response = gtk.RESPONSE_CANCEL
        self.error = None
        self.uri = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_file_utils)
        self.dlg = self.builder.get_object('select_file_dialog')

        events = {
                  'on_open_button7_clicked': self.open_event,
                  'on_cancel_button6_clicked': self.cancel_event,
                }
        self.builder.connect_signals(events)
        self.attach_filter(model)

    def attach_filter(self, model):
        _filter = gtk.FileFilter()
        if model is FileSelectDialog.CSV:
            _filter.set_name("CSV")
            _filter.add_pattern("*.csv")
        elif model is FileSelectDialog.HTML:
            _filter.set_name("HTML")
            _filter.add_mime_type("text/html")
            _filter.add_pattern("*.html")
            _filter.add_pattern("*.htm")
        self.dlg.add_filter(_filter)

        _filter = gtk.FileFilter()
        _filter.set_name(constants.all_connections_filter_name)
        _filter.add_pattern("*")
        self.dlg.add_filter(_filter)
                

    def get_response(self):
        return self.response

    def open_event(self, widget):
        self.uri = self.dlg.get_filename()
        self.response = gtk.RESPONSE_OK

    def cancel_event(self, widget):
        self.response = gtk.RESPONSE_CANCEL

    def get_filename(self):
        return self.uri

    def run(self):
        self.dlg.run()
        self.dlg.destroy()

class ImportProgressDialog(object):

    def __init__(self, cxs, connections):
        self.connections = connections
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_import)
        self.dlg = self.builder.get_object('import_progress')
        self.results = self.builder.get_object('import_result')
        events = {
                    'on_ok_button6_clicked': self.close_event,
                    'on_import_progress_destroy': self.close_event,
                }
        self.builder.connect_signals(events)
        for d in cxs:
            alias = d['alias'].strip()
            if len(d) != 10 or alias in self.connections:
                self.write_result(constants.import_not_saving % alias)
                continue
            cx = connections_factory(get_last_id(self.connections), d['type'], d['user'],
                                    d['host'], alias, d['password'], d['port'],
                                    d['group'], d['options'], d['description'])
            self.connections[alias] = cx
            self.write_result(constants.import_saving % cx)

    def run(self):
        self.dlg.run()

    def close_event(self, widget=None):
        self.dlg.destroy()

    def write_result(self, text):
        buffer = self.results.get_buffer()
        if buffer == None:
            buffer = gtk.TextBuffer()
            self.results.set_buffer(buffer)
        buffer.insert_at_cursor(text)


class PreferencesDialog(object):

    def __init__(self):
        self.response = gtk.RESPONSE_CANCEL
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_preferences)
        self.dlg = self.builder.get_object('dialog_preferences')
        self.widgets = {
            # Consoles
            'fg_colorbutton': self.builder.get_object('font-colorbutton'),
            'fontbutton': self.builder.get_object('fontbutton'),
            'buffer_hscale': self.builder.get_object('buffer-hscale'),
            'chk_bg_transparent': self.builder.get_object('chk_bg_transparent'),
            'transparency_hscale': self.builder.get_object('transparency-hscale'),
            'bgimage_filechooserbutton': self.builder.get_object('bgimage-filechooserbutton'),
            'bg_colorbutton': self.builder.get_object('bg-colorbutton'),
            'clear_bg': self.builder.get_object('clear_image_button'),
            # Connections
            'ssh_options_entry': self.builder.get_object('ssh_default_options_entry'),
            'vnc_options_entry': self.builder.get_object('vnc_default_options_entry'),
            'rdp_options_entry': self.builder.get_object('rdp_default_options_entry'),
            'telnet_options_entry': self.builder.get_object('telnet_default_options_entry'),
            'ftp_options_entry': self.builder.get_object('ftp_default_options_entry'),
            'ssh_entry': self.builder.get_object('ssh_client_entry'),
            'vnc_entry': self.builder.get_object('vnc_client_entry'),
            'rdp_entry': self.builder.get_object('rdp_client_entry'),
            'telnet_entry': self.builder.get_object('telnet_client_entry'),
            'ftp_entry': self.builder.get_object('ftp_client_entry'),
            'console_char_entry': self.builder.get_object('console_char_entry'),
            'vnc_embedded_chkbutton': self.builder.get_object('vnc_embedded_chkbutton')}

        events = {
            'on_dialog_preferences_close': self.close_event,
            'on_pref_cancel_button_clicked': self.close_event,
            'on_pref_appy_button_clicked': self.apply_event,
            'on_clear_image_button_clicked': self.clear_event,
            'on_vnc_embedded_chkbutton_toggled': self.toggle_vnc_embeded,
            'on_chk_bg_transparent_toggled': self.toggle_transparency_event}
        self.builder.connect_signals(events)
        self.fill_entries()
        self.fill_console()

    def close_event(self, widget):
        self.dlg.destroy()

    def apply_event(self, widget):
        self.save_connections_config()
        self.save_console_config()
        self.close_event(None)
        self.response = gtk.RESPONSE_OK

    def clear_event(self, widget):
        '''Set the bg image to None'''
        bg_but = self.widgets['bgimage_filechooserbutton']
        bg_but.set_filename("None")

    def toggle_transparency_event(self, widget):
        bg_button = self.widgets['bgimage_filechooserbutton']
        bg_clear = self.widgets['clear_bg']
        bg_color = self.widgets['bg_colorbutton']
        if widget.get_active():
            bg_button.set_sensitive(False)
            bg_clear.set_sensitive(False)
            bg_color.set_sensitive(False)
        else:
            bg_button.set_sensitive(True)
            bg_clear.set_sensitive(True)
            bg_color.set_sensitive(True)

    def toggle_vnc_embeded(self, widget):
        vnc_client = self.widgets['vnc_entry']
        vnc_options = self.widgets['vnc_options_entry']
        if widget.get_active():
            vnc_client.set_sensitive(False)
            vnc_options.set_sensitive(False)
        else:
            vnc_client.set_sensitive(True)
            vnc_options.set_sensitive(True)
            
    def fill_entries(self):
        conf = McmConfig()
        #SSH
        client, options = conf.get_ssh_conf()
        e1 = self.widgets['ssh_entry']
        e2 = self.widgets['ssh_options_entry']
        e1.set_text(client)
        e2.set_text(options)
        #VNC
        client, options, embedded = conf.get_vnc_conf()
        e1 = self.widgets['vnc_entry']
        e2 = self.widgets['vnc_options_entry']
        e3 = self.widgets['vnc_embedded_chkbutton']
        e1.set_text(client)
        e2.set_text(options)
        e3.set_active(embedded)
        #Telnet
        client, options = conf.get_telnet_conf()
        e1 = self.widgets['telnet_entry']
        e2 = self.widgets['telnet_options_entry']
        e1.set_text(client)
        e2.set_text(options)
        #FTP
        client, options = conf.get_ftp_conf()
        e1 = self.widgets['ftp_entry']
        e2 = self.widgets['ftp_options_entry']
        e1.set_text(client)
        e2.set_text(options)
        #RDP
        client, options = conf.get_rdp_conf()
        e1 = self.widgets['rdp_entry']
        e2 = self.widgets['rdp_options_entry']
        e1.set_text(client)
        e2.set_text(options)

    def fill_console(self):
        conf = McmConfig()
        widget = self.widgets['fg_colorbutton']
        widget.set_color(gtk.gdk.color_parse(conf.get_fg_color()))
        widget = self.widgets['fontbutton']
        pango_font = conf.get_font()
        widget.set_font_name(pango_font.to_string())
        widget = self.widgets['chk_bg_transparent']
        widget.set_active(conf.get_bg_transparent())
        widget.toggled()
        widget = self.widgets['transparency_hscale']
        widget.set_value(conf.get_bg_transparency())
        widget = self.widgets['bgimage_filechooserbutton']
        widget.set_filename(conf.get_bg_image())
        widget = self.widgets['bg_colorbutton']
        widget.set_color(gtk.gdk.color_parse(conf.get_bg_color()))
        widget = self.widgets['console_char_entry']
        widget.set_text(conf.get_word_chars())
        widget = self.widgets['buffer_hscale']
        widget.set_value(conf.get_buffer_size())

    def save_connections_config(self):
        conf = McmConfig()
        cfg = conf.get_connections_config()
        #SSH
        cfg['ssh.client'] = self.widgets['ssh_entry'].get_text()
        cfg['ssh.default'] = self.widgets['ssh_options_entry'].get_text()
        #VNC
        cfg['vnc.client'] = self.widgets['vnc_entry'].get_text()
        cfg['vnc.default'] = self.widgets['vnc_options_entry'].get_text()
        cfg['vnc.embedded'] = str(self.widgets['vnc_embedded_chkbutton'].get_active())
        #RDP
        cfg['rdp.client'] = self.widgets['rdp_entry'].get_text()
        cfg['rdp.default'] = self.widgets['rdp_options_entry'].get_text()
        #TELNET
        cfg['telnet.client'] = self.widgets['telnet_entry'].get_text()
        cfg['telnet.default'] = self.widgets['telnet_options_entry'].get_text()
        #FTP
        cfg['ftp.client'] = self.widgets['ftp_entry'].get_text()
        cfg['ftp.default'] = self.widgets['ftp_options_entry'].get_text()
        conf.save_connections_config(cfg)

    def save_console_config(self):
        conf = McmConfig()
        cfg = conf.get_console_config()

        color = self.widgets['fg_colorbutton'].get_color()
        cfg['fg.color'] = color.to_string().strip("#")
        color = self.widgets['bg_colorbutton'].get_color()
        cfg['bg.color'] = color.to_string().strip("#")

        fname = self.widgets['bgimage_filechooserbutton'].get_filename()
        if fname == None:
            fname = "None"
        cfg['bg.image'] = fname

        active = self.widgets['chk_bg_transparent'].get_active()
        cfg['bg.transparent'] = str(active)

        value = self.widgets['transparency_hscale'].get_value()
        value = int(value)
        cfg['bg.transparency'] = str(value)

        value = self.widgets['buffer_hscale'].get_value()
        value = int(value)
        cfg['buffer.size'] = str(value)

        font = self.widgets['fontbutton'].get_font_name()
        cfg['font.type'] = font

        cfg['word.chars'] = self.widgets['console_char_entry'].get_text()
        conf.save_console_config(cfg)

    def get_font(self):
        return self.widgets['fontbutton'].get_font_name()

    def get_fg_color(self):
        return self.widgets['fg_colorbutton'].get_color()

    def get_bg_color(self):
        return self.widgets['bg_colorbutton'].get_color()

    def get_transparency(self):
        return (self.widgets['chk_bg_transparent'].get_active(), self.widgets['transparency_hscale'].get_value())

    def get_bg_image(self):
        return self.widgets['bgimage_filechooserbutton'].get_filename()

    def run(self):
        self.dlg.run()


class McmCheckbox(gtk.HBox):

    def __init__(self, title):
        gtk.HBox.__init__(self, False)
        self._label = gtk.Label(title)
        self._current_alias = title
        self.pack_start(self._label, True, True, 0)
        self._button = gtk.CheckButton()
        self._button.set_name("%s_button" % title)
        self._button.set_tooltip_text(constants.cluster_checkbox_tooltip)
        self.pack_start(self._button, False, False, 0)
        #self._button1 = gtk.Button()
        #self._button1.set_relief(gtk.RELIEF_NONE)
        #self._button1.set_image(gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_BUTTON))
        #self._button1.set_tooltip_text(constants.cluster_checkbox_tooltip)
        #self.pack_start(self._button1, False, False, 0)
        self.show_all()

    def get_active(self):
        return self._button.get_active()

    def set_title(self, title):
        self._label.set_text(title)

    def get_title(self):
        return self._label.get_text()

    def get_current_alias(self):
        return self._current_alias


class McmNewTipDialog(object):

    def __init__(self):
        self.response = gtk.RESPONSE_CANCEL
        self.new_tip = None
        self.error = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_tips)
        self.widgets = {
                        'dlg': self.builder.get_object('new_tips_dialog'),
                        'section_entry': self.builder.get_object('section_entry'),
                        'subsection_entry': self.builder.get_object('subsection_entry'),
                        'name_entry': self.builder.get_object('name_entry'),
                        'value_entry': self.builder.get_object('value_entry'),
                        'send_checkbox': self.builder.get_object('send_checkbox'),
                        }
        events = {
                        'response': self.cancel_event,
                        'on_cancel_button_clicked': self.cancel_event,
                        'on_save_button_clicked': self.save_event,
                        'on_help_button_clicked': self.help_event,
                }
        self.builder.connect_signals(events)
        self.dlg = self.widgets['dlg']

    def run(self):
        self.dlg.run()

    def cancel_event(self, widget):
        self.response = gtk.RESPONSE_CANCEL
        self.dlg.destroy()
        return True

    def save_event(self, widget):
        self.response = gtk.RESPONSE_OK
        section = self.widgets['section_entry'].get_text()
        subsection = self.widgets['subsection_entry'].get_text()
        name = self.widgets['name_entry'].get_text()
        value = self.widgets['value_entry'].get_text()
        send = self.widgets['send_checkbox'].get_active()

        # Shall I add a "Are you sure" dialog when sending to google docs?

        self.new_tip = Tip(0, section, subsection, name, value)
        if send:
            gform = GoogleForm()
            gform.send(self.new_tip)

        self.dlg.destroy()
        return True

    def help_event(self, widget):
        dlg = UtilityDialogs()
        response = dlg.show_info_dialog(constants.send_world, constants.google_docs_disclaimer)


class McmMenu(gtk.Menu):

    def __init__(self, label):
        gtk.Menu.__init__(self)
        self.label = label


class TipGtkMenuItem(gtk.MenuItem):

    def __init__(self, label, tip):
        gtk.MenuItem.__init__(self, label)
        self.tip = tip


class McmTipsWidget(object):

    def __init__(self, hbox):
        self.tips = Tips()
        self.tips_list = self.tips.read()
        self.hbox = hbox
        self.menu_bar = self.hbox.get_children()[0]
        self.tips_entry = self.hbox.get_children()[1]
        self.tips_entry.connect("icon-press", self.entry_icon_event)
        self.draw_menu_bar()

    def draw_menu_bar(self):
        root_menu_item = self.menu_bar.get_children()[0]
        sections_menu = gtk.Menu()
        root_menu_item.set_submenu(sections_menu)
        for sect in self.draw_sections():
            menu = sect.get_submenu()
            for subsect in self.draw_subsections(menu):
                menu.append(subsect)
                sub_menu = subsect.get_submenu()
                for tips in self.draw_tips_menu(menu, sub_menu):
                    sub_menu.append(tips)
            sections_menu.append(sect)

    def entry_icon_event(self, widget, icon, event):
        # Using 'event.button' I can know which mouse button was used
        if icon.value_name == "GTK_ENTRY_ICON_PRIMARY":
            print "To Console"
        elif icon.value_name == "GTK_ENTRY_ICON_SECONDARY":
            new_tip_dialog = McmNewTipDialog()
            new_tip_dialog.run()
            if new_tip_dialog.response == gtk.RESPONSE_OK:
                self.tips_list.append(new_tip_dialog.new_tip)
                self.draw_menu_bar()
                self.tips.save(self.tips_list)
        return True

    def draw_sections(self):
        sections = []
        menu_items = []
        for tip in self.tips_list:
            sections.append(tip.section)
        sections = set(sections)
        for section in sections:
            mi = gtk.MenuItem(section)
            me = McmMenu(section)
            mi.set_submenu(me)
            mi.show()
            menu_items.append(mi)
        return menu_items

    def draw_subsections(self, sections_menu):
        subsections = []
        menu_items = []
        label = sections_menu.label
        for tip in self.tips_list:
            if label == tip.section:
                subsections.append(tip.subsection)
        subsections = set(subsections)
        for subsection in subsections:
            mi = gtk.MenuItem(subsection)
            me = McmMenu(subsection)
            mi.set_submenu(me)
            mi.show()
            menu_items.append(mi)
        return menu_items

    def draw_tips_menu(self, sections_menu, subsections_menu):
        tips = []
        menu_items = []
        sect_label = sections_menu.label
        subsect_label = subsections_menu.label
        for tip in self.tips_list:
            if subsect_label == tip.subsection and sect_label == tip.section:
                tips.append(tip)
        for tip in tips:
            mi = TipGtkMenuItem(tip.name, tip)
            mi.connect("activate", self.item_event)
            mi.show()
            menu_items.append(mi)
        return menu_items

    def draw_breadcrumb(self, tip):
        items = self.menu_bar.get_children()
        if len(items) > 1:
            self.menu_bar.remove(items[1])
            self.menu_bar.remove(items[2])
            self.menu_bar.remove(items[3])

        mi_section = gtk.MenuItem(tip.section)
        mi_subsection = gtk.MenuItem(tip.subsection)
        mi_name = gtk.MenuItem(tip.name)

        mi_section.show()
        mi_subsection.show()
        mi_name.show()

        sect_menu = McmMenu(tip.section)
        subsect_menu = McmMenu(tip.subsection)
        name_menu = McmMenu(tip.name)

        for sect in self.draw_sections():
            menu = sect.get_submenu()
            for subsect in self.draw_subsections(menu):
                menu.append(subsect)
                sub_menu = subsect.get_submenu()
                for tips in self.draw_tips_menu(menu, sub_menu):
                    sub_menu.append(tips)
            sect_menu.append(sect)

        for subsect in self.draw_subsections(sect_menu):
            subsect_menu.append(subsect)
            sub_menu = subsect.get_submenu()
            for tips in self.draw_tips_menu(sect_menu, sub_menu):
                sub_menu.append(tips)

        for tips in self.draw_tips_menu(sect_menu, subsect_menu):
            name_menu.append(tips)

        mi_section.set_submenu(sect_menu)
        mi_subsection.set_submenu(subsect_menu)
        mi_name.set_submenu(name_menu)

        self.menu_bar.append(mi_section)
        self.menu_bar.append(mi_subsection)
        self.menu_bar.append(mi_name)

    def item_event(self, widget):
        self.draw_breadcrumb(widget.tip)
        self.tips_entry.set_text(widget.tip.value)

    def update(self, filename=None):
        response = self.tips.update(filename)
        self.tips_list = self.tips.read()
        self.draw_menu_bar()
        return response

class ManageConnectionsDialog(object):
    def __init__(self, connections):
        self.response = gtk.RESPONSE_CANCEL
        self.connections = connections
        builder = gtk.Builder()
        builder.add_from_file(constants.glade_edit_cx)
        self.dialog = builder.get_object("edit_connections_dialog")
        self.tree_container = builder.get_object("tree_scroll")
        events = {
                        'response': self.cancel_event,
                        'on_cancel_button_clicked': self.cancel_event,
                        'on_save_button_clicked': self.save_event,
                        'on_exp_csv_button_clicked': self.export_csv_event,
                        'on_exp_html_button_clicked': self.export_html_event,
                }
        builder.connect_signals(events)
        self.view = self.connections_view()
        self.tree_container.add(self.view)
        self.tree_container.show_all()

    def run(self):
        self.dialog.run()
    
    def cancel_event(self, widget):
        self.dialog.destroy()

    def save_event(self, widget):
        self.dialog.destroy()

    def export_csv_event(self, widget):
        pass

    def export_html_event(self, widget):
        pass

    def cell_edited_event(self, widget, path, new_text, store):
        pass

    def connections_view(self):
        store = self.connections_model()
        view = gtk.TreeView(store)

        for column in self.generate_columns(store):
            view.append_column(column)

        return view

    def generate_columns(self, store):
        columns = []

        renderer0 = gtk.CellRendererText()
        renderer0.set_property( 'editable', True)
        renderer0.connect('edited', self.cell_edited_event, store )
        img_renderer = gtk.CellRendererPixbuf()
        
        columns.append(gtk.TreeViewColumn("Alias", renderer0, text=0))
        columns.append(gtk.TreeViewColumn("Type", renderer0, text=1))
        columns.append(gtk.TreeViewColumn("Group", renderer0, text=8))
        columns.append(gtk.TreeViewColumn("Username", renderer0, text=5))
        columns.append(gtk.TreeViewColumn("Host", renderer0, text=3))
        columns.append(gtk.TreeViewColumn("Port", renderer0, text=4))
        columns.append(gtk.TreeViewColumn("Options", renderer0, text=7))
        columns.append(gtk.TreeViewColumn("Description", renderer0, text=9))
        columns.append(gtk.TreeViewColumn("Password", renderer0, text=6))
        columns.append(gtk.TreeViewColumn("Delete", img_renderer, pixbuf=10))

        return columns

    def connections_model(self):
        """Creates a ListStore with the Connections data"""
        store = gtk.ListStore(str, str, str, str, str, str, str, str, str, str, gtk.gdk.Pixbuf)
        img = self.dialog.render_icon(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON)

        for cx in self.connections.values():
            cx_list = cx.to_list()
            cx_list.append(img)
            store.append(cx_list)
        return store

class HttpServerDialog(object):
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file(constants.glade_http)
        self.dialog = builder.get_object("http_server_dialog")
        self.dialog.connect('on_http_server_connect_toggled', self.start_server)
        self.dialog.connect('on_http_server_disconnect_toggled', self.stop_server)
        #self.http_server = McmHttpServerThread

    def run(self):
        self.dialog.run()
        self.dialog.destroy()

    def start_server(self):
        pass

    def stop_server(self):
        pass

class DefaultColorSettings(object):
    def __init__(self):
        def_settings = gtk.settings_get_default()
        color_scheme = def_settings.get_property("gtk-color-scheme").strip()
        color_scheme = color_scheme.split("\n")

        settings = {}
        for property in color_scheme:
            # property is of the type key: value
            property = property.split(": ")
            settings[property[0]] = property[1]
            
        self.tooltip_fg_color = gtk.gdk.color_parse(settings["tooltip_fg_color"])
        self.selected_bg_color = gtk.gdk.color_parse(settings["selected_bg_color"])
        self.tooltip_bg_color = gtk.gdk.color_parse(settings["tooltip_bg_color"])
        self.base_color = gtk.gdk.color_parse(settings["base_color"])
        self.fg_color = gtk.gdk.color_parse(settings["fg_color"])
        self.text_color = gtk.gdk.color_parse(settings["text_color"])
        self.selected_fg_color = gtk.gdk.color_parse(settings["selected_fg_color"])
        self.bg_color = gtk.gdk.color_parse(settings["bg_color"])
