
# Copyright (C) 2009 Alejandro Ayuso 
#
# This file is part of the Monocaffe Connection Manager
#
# Monocaffe Connection Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Monocaffe Connection Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the Monocaffe Connection Manager.  If not, see <http://www.gnu.org/licenses/>.
#
# Introduction
#
# The Monocaffe Connection Manager is created to ease the management of connections to different
# servers a sysadmin usuarlly connect to. I'm aiming to provide support for:
# -ssh
# -telnet
# -vnc
# -rdesktop
# -ICA (Citrix) TO DO
#
# This basically depends on which of this programs can be called from the command line without
# too much trouble. Also, very basic options will be used, so if you want more complex options
# like mount usb drives for rdesktop, or sound for VNC, use the proper utilities for this or
# modify mcm.
#
# Configuration
# mcm comes configured for Ubuntu (my platform) but basically, all you need to modify in case one
# of the commands isn't found, is the file connections.py. There you'll find the global tuples where
# the paths to the clients are specified. You can change them freely.
#
# Also, if you preffer to change any of them to be the first, do so modifying the tuples mentioned
# before.
#
