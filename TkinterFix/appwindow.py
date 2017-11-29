
from Tkinter import *
import bouncediagram
import tkFileDialog
import glob
import logparser
import logparserutil
import re
import subprocess
import os.path
from logentryviewer import LogEntryViewer
from logentrytreeviewer import LogEntryTreeViewer
import logstats
from tkColorChooser import askcolor 
from reglogparser import SequenceBuilder
import platform
# Add control frame
'''1'''
    def on_configure(event):
        # update scrollregion after starting 'mainloop'
        # when all widgets are in canvas
        canvas1.configure(scrollregion=canvas1.bbox('all'))
canvas1 = Canvas(self.top_frame,bd=4,width=230)
canvas1.grid(row=0, rowspan=5,sticky=N+S+W)
##Uncomment lower part if mouse scrolling is required
    '''def _on_mousewheel(event):
        canvas1.yview_scroll(-1*(event.delta/120), "units")
        canvas1.bind_all("<MouseWheel>", _on_mousewheel)'''
scrollbar = Scrollbar(self.top_frame, orient=VERTICAL, command=canvas1.yview, takefocus=0)
scrollbar.grid(row=0,rowspan=5,sticky=N+S+E)
canvas1.configure(yscrollcommand = scrollbar.set)
canvas1.bind('<Configure>', on_configure)
control_frame = Frame(canvas1, bd=2)
canvas1.create_window((0,0), window=control_frame, anchor='nw')
'''/1'''
