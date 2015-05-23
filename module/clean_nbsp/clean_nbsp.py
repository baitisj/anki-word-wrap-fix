# -*- coding: utf-8 -*-
# Copyright 2014 Jeff Baitis <jeff@baitis.net>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Version: 1.0, 2014/10/24

import os
from anki.hooks import addHook
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QIcon, QAction
from anki.hooks import wrap
from aqt.editor import Editor
from anki.utils import json
from BeautifulSoup import BeautifulSoup
from aqt import mw
from aqt.utils import showInfo
from aqt import browser

def removeNBSP(str):
	return str.replace('&nbsp;', ' ')

def cleanNBSP(self):
	""" Utility function that removes non-breaking spaces from the field of the note that is currently being edited. """
	self.saveNow();
	self.mw.checkpoint(_("Fix word wrap (remove non-breaking space)"))
	text = self.note.fields[self.currentField]
	self.note.fields[self.currentField] = removeNBSP(text)
	self.stealFocus = True;
	self.loadNote();

def setupButtons(self):
	""" Adds word wrap keyboard shortcut and button to the note editor. """
	icons_dir = os.path.join(mw.pm.addonFolder(), 'clean_nbsp', 'icons')
	b = self._addButton("cleanButton", lambda s=self: cleanNBSP(self),
		    text=" ", tip="Fix word wrap by removing non-breaking spaces (Ctrl+Shift+W)", key="Ctrl+Shift+w")
	b.setIcon(QIcon(os.path.join(icons_dir, 'word_wrap.png')))

def bulkReplace(self):
	""" Performs search-and-replace on selected notes """
	nids = self.selectedNotes()
	if not nids:
		return
	# Allow undo
	self.mw.checkpoint(_("Fix word wrap on selected cards (remove non-breaking space)"))
	self.mw.progress.start()
	# Not sure if beginReset is required
	self.model.beginReset()
	changed = self.col.findReplace(nids, # Selected note IDs
		'&nbsp;', # from
		' ',  # to whitespace
		True, # treat as regular expression
		None, # all note fields
		True) # case insensitivity
	self.model.endReset()
	self.mw.progress.finish()
	# Display a progress meter
	showInfo(ngettext(
            "%(a)d of %(b)d note updated",
            "%(a)d of %(b)d notes updated", len(nids)) % {
                'a': changed,
                'b': len(nids),
            })

def addMenuItem(self):
	""" Adds hook to the Edit menu in the note browser """
	action = QAction("Fix word-wrap, currently selected notes", self)
	self.bulkReplace = bulkReplace
	self.connect(action, SIGNAL("triggered()"), lambda s=self: bulkReplace(self))
	self.form.menuEdit.addAction(action)
	
# Add-in hook; called by the AQT Browser object when it is ready for the add-on to modify the menus
addHook('browser.setupMenus', addMenuItem)

Editor.cleanNBSP = cleanNBSP
Editor.setupButtons = wrap(Editor.setupButtons, setupButtons)
