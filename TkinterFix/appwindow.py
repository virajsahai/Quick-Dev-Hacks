#
# @file
# @brief log viewer appliation GUI classes
#
# Copyright (c) 2007 by Spirent Communications Inc.
# All Rights Reserved.
#
# This software is confidential and proprietary to Spirent Communications Inc.
# No part of this software may be reproduced, transmitted, disclosed or used
# in violation of the Software License Agreement without the expressed
# written consent of Spirent Communications Inc.
#

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
class AppWindow(object):
    class EndpointEnable(object):
        def __init__(self):
            self.var = IntVar()
            self.var.set(1)
            self.checkbutton = None
        
        def enabled(self):
            if self.var.get():
                return True
            else:
                return False
            
    class RegexEntry(object):
        def __init__(self):
            self.re = None
            self.var = StringVar()
            self.entry = None

    def __init__(self, master, ar='1024x768', xy='+20+20'):
        # Make control variables
        self.entry_type_enables = { }
        for type_, name, value in logparserutil.get_msg_types():
            var = self.entry_type_enables[type_] = IntVar()
            var.set(value)

        self.endpoint_group_enables = { }
        self.endpoint_enables = { }
        self.msg_regex = self.RegexEntry()
        self.endpoint_regex = self.RegexEntry()
        self.msg_content_regex = self.RegexEntry()
        self.status_line = StringVar()
        self.enable_uniform_y_axis = IntVar()
        self.enable_uniform_y_axis.set(0)

        self.log_file_spec = []
        self.log_files = []
        
        # Make top level window        
        self.top_frame = Toplevel(bd=2, relief=RIDGE)
        self.top_frame.geometry(ar+xy)
        self.top_frame.protocol('WM_DELETE_WINDOW', self.quit)
        self.top_frame.rowconfigure(0, weight=9)
        self.top_frame.columnconfigure(1, weight=1)

        # Add log text
        self.log_text = Text(self.top_frame, height=10, wrap=WORD, state=DISABLED, bd=2, relief=SUNKEN, takefocus=1, highlightthickness=1)
        self.log_text.grid(row=1, column=1, sticky=W+E)
        
        self.log_scroll_y = Scrollbar(self.top_frame, orient=VERTICAL, command=self.log_text.yview, takefocus=0)
        self.log_scroll_y.grid(row=1, column=2, sticky=N+S)
        self.log_text['yscrollcommand'] = self.log_scroll_y.set

        # Add bounce diagram
        self.diagram = bouncediagram.BounceDiagram(self.top_frame, self)
        self.diagram.grid(row=0, column=1, columnspan=2, sticky=N+S+W+E)
        
        # Add control frame
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
        
        # Add status line
        status_label = Label(self.top_frame, textvariable=self.status_line, bd=2, relief=SUNKEN, anchor=NW)
        status_label.grid(row=2, column=1, sticky=W+E)
        
        # Populate control frame
        control_frame.rowconfigure(17, weight=1)
        control_frame.columnconfigure(0, weight=1)

        Label(control_frame, text='Actions:').grid(sticky=W)
        Button(control_frame, text='Add log files...', command=self.loadDialog).grid(sticky=W+E)
        Button(control_frame, text='Reset diagram', command=self.resetCommand).grid(sticky=W+E)
        Button(control_frame, text='Show statistics', command=self.showStats).grid(sticky=W+E)
        Button(control_frame, text='Message Graph', command=self.launchMessageGraph).grid(sticky=W+E)
        Button(control_frame, text='Highlight Color', command=self.selectHighlightColor).grid(sticky=W+E)
        Button(control_frame, text='Show Sequence (Regression Log Only)', command=self.showSequence).grid(sticky=W+E)
        Button(control_frame, text='Quit', command=self.quit).grid(sticky=W+E)

        #Label(control_frame).grid()
        
        Label(control_frame, text='Log entry types:').grid(sticky=W)
        type_frame = Frame(control_frame, bd=2, relief=RIDGE)
        type_frame.grid(sticky=W+E)
        type_frame.columnconfigure(0, weight=1)
        for type, name, value in logparserutil.get_msg_types():
            view_enable = self.entry_type_enables[type]
            button = Checkbutton(type_frame, text=name, command=self.diagram.redraw, variable=view_enable)
            button.grid(sticky=W)

        #Label(control_frame).grid()

        button = Checkbutton(control_frame, text='TODO: Uniform time-axis', command=self.diagram.redraw, variable=self.enable_uniform_y_axis)
        button.grid(sticky=W)

        #Label(control_frame).grid()

        Label(control_frame, text='Endpoint Groups:').grid(sticky=W)
        self.endpoint_frame = Frame(control_frame, bd=2, relief=RIDGE)
        self.endpoint_frame.grid(sticky=N+S+W+E)
        self.endpoint_frame.rowconfigure(100, weight=1)
        self.endpoint_frame.columnconfigure(0, weight=1)
        #bll_endpoint = Checkbutton(self.endpoint_frame, text='BLL', state=DISABLED)
        #bll_endpoint.grid(sticky=NW)
        #bll_endpoint.select()

        #Label(control_frame).grid()

        Label(control_frame, text='Message names (regex):').grid(sticky=W)
        self.msg_regex.entry = Entry(control_frame, textvariable=self.msg_regex.var, bd=2, relief=RIDGE)
        self.msg_regex.entry.grid(sticky=W+E)
        self.msg_regex.entry.bind('<Return>', func=self.msgRegexConfigureEvent)

        Label(control_frame, text='Message content (regex):').grid(sticky=W)
        self.msg_content_regex.entry = Entry(control_frame, textvariable=self.msg_content_regex.var, bd=2, relief=RIDGE)
        self.msg_content_regex.entry.grid(sticky=W+E)
        self.msg_content_regex.entry.bind('<Return>', func=self.msgContentRegexConfigureEvent)
        
        
        Label(control_frame, text='Endpoint (regex):').grid(sticky=W)
        self.endpoint_regex.entry = Entry(control_frame, textvariable=self.endpoint_regex.var, bd=2, relief=RIDGE)
        self.endpoint_regex.entry.grid(sticky=W+E)
        self.endpoint_regex.entry.bind('<Return>', func=self.endpointRegexConfigureEvent)

        Label(control_frame, text='Zoom step:').grid(sticky=W)
        self.last_zoom_step = bouncediagram.DEFAULT_ZOOM_STEP
        zoom_step = IntVar()
        zoom_step.set(self.last_zoom_step)
        Scale(control_frame, from_=1, to=bouncediagram.ZOOM_STEPS, resolution=1.0, showvalue=0,
              command=self.zoomCommand, variable=zoom_step, orient=HORIZONTAL).grid(sticky=W+E)
    
        # Dummy label
        Label(control_frame).grid()
        # File open dialog box
        if platform.system().startswith("Darwin") :
            _filetypes= []
        else :
            _filetypes = filetypes=[('Log files', '*.log*'), ('All files', '*')]
        self.log_open = tkFileDialog.Open(filetypes=_filetypes,
                                          parent=self.top_frame,
                                          title='Add log files',
                                          multiple=True)

        self.top_frame.bind('<Button-1>', func=self.mouseButtonEvent)
        self.log_text.bind('<Double-Button-1>', func=self.doubleMouseButtonEvent)
    
    def loadDialog(self):
        log_files = self.log_open.show()
        if log_files:
            self.loadCommand(log_files)
        
    def loadCommand(self, log_file_spec):
        self.log_file_spec = log_file_spec
        log_files = [ ]
        if isinstance(log_file_spec, (list, tuple)):
            for spec in log_file_spec:
                log_files += glob.glob(spec)
        elif isinstance(log_file_spec, unicode):
            if log_file_spec.startswith("{"):
                log_file_spec = log_file_spec.split("}")
                for spec in log_file_spec:
                    spec = spec.lstrip(" {")
                    log_files += glob.glob(spec)
            else:
                log_file_spec = log_file_spec.split(" ")
                for spec in log_file_spec:
                    log_files += glob.glob(spec)
        else:
            log_files += glob.glob(log_file_spec)

        log_files = list(set(log_files).difference(set(self.log_files)))
        self.log_files.extend(log_files)

        for log in logparserutil.parse_logs(log_files):
            if not self.endpoint_group_enables.has_key(log.endpoint_group):
            	self.top_frame.geometry(str(self.top_frame.winfo_width())+"x"+str(self.top_frame.winfo_height()+1));
                enable = self.endpoint_group_enables[log.endpoint_group] = self.EndpointEnable()
                enable.checkbutton = Checkbutton(self.endpoint_frame,
                                                 text=log.endpoint_group,
                                                 command=self.diagram.redraw,
                                                 variable=enable.var)
                enable.checkbutton.grid(sticky=NW)
            self.diagram.insert(log)
        self.diagram.redraw()

    def resetCommand(self):
        for enable in self.endpoint_group_enables.values():
            enable.checkbutton.destroy()
        self.endpoint_group_enables.clear()
        self.diagram.reset()
        self.diagram.redraw()
        self.log_files = []

    def showStats(self):
        viewer = LogEntryViewer()
        if len(self.diagram.selectedEntries) > 0:
            viewer.viewText(logstats.get_log_stats_text(self.log_files, [self.diagram.selectedEntries[0].timestamp, self.diagram.selectedEntries[1].timestamp]))
        else:
            viewer.viewText(logstats.get_log_stats_text(self.log_files, None))

    def launchMessageGraph(self):
        cmd = ['python ', os.path.join(os.path.dirname(__file__), '../chmsggraph/chmsggraph.py')]
        cmd.extend(self.log_file_spec)
        subprocess.Popen(cmd)
        
    def msgRegexConfigureEvent(self, event):
        regex = self.msg_regex.var.get().strip()
        if len(regex):
            try:
                self.msg_regex.re = re.compile(regex, re.IGNORECASE | re.VERBOSE)
                self.msg_regex.entry['bg'] = 'green'
            except:
                self.msg_regex.re = None
                self.msg_regex.entry['bg'] = 'red'
        else:
            self.msg_regex.re = None
            self.msg_regex.entry['bg'] = 'white'
        self.diagram.redraw()

    def endpointRegexConfigureEvent(self, event):
        regex = self.endpoint_regex.var.get().strip()
        if len(regex):
            try:
                self.endpoint_regex.re = re.compile(regex, re.IGNORECASE | re.VERBOSE)
                self.endpoint_regex.entry['bg'] = 'green'
            except:
                self.endpoint_regex.re = None
                self.endpoint_regex.entry['bg'] = 'red'
        else:
            self.endpoint_regex.re = None
            self.endpoint_regex.entry['bg'] = 'white'
        self.diagram.redraw()
    
    def msgContentRegexConfigureEvent(self, event):
        regex = self.msg_content_regex.var.get()
        if len(regex):
            try:
                self.msg_content_regex.re = re.compile(regex, re.IGNORECASE | re.VERBOSE)
                self.msg_content_regex.entry['bg'] = 'green'
            except:
                self.msg_content_regex.re = None
                self.msg_content_regex.entry['bg'] = 'red'
        else:
            self.msg_content_regex.re = None
            self.msg_content_regex.entry['bg'] = 'white'
        self.diagram.redraw()

    def zoomCommand(self, zoom_step):
        zoom_step = int(zoom_step)
        if zoom_step != self.last_zoom_step:
            self.diagram.zoomStep(zoom_step)
            self.last_zoom_step = zoom_step
    
    def quit(self):
        self.top_frame.quit()

    def mouseButtonEvent(self, event):
        if event.widget.winfo_parent() == str(self.diagram):
            self.diagram.focus_set()
        elif event.widget == self.log_scroll_y:
            self.log_text.focus_set()
        else:
            event.widget.focus_set()
            
    def doubleMouseButtonEvent(self, event):
        if event.widget == self.log_text:
            viewer = LogEntryTreeViewer()
            viewer.viewText(self.log_text.get('1.0', END))

    def selectHighlightColor(self):
        (rgb, highlightColor) = askcolor()
        self.diagram.highlightColor = highlightColor

    def showSequence(self):
        viewer = LogEntryViewer()
        s = SequenceBuilder()
        viewer.viewText(s.process(self.log_files))


# Testing only...
if __name__ == '__main__':
    root = Tk()
    root.withdraw()
    app = AppWindow(root)
    app.loadCommand(r'c:\working\TestCenter\p2_core\bin\debug\10_100_19_239.log')
    root.mainloop()
