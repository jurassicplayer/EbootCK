#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import time
import sys, os, shutil, subprocess, re, binascii
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QDialog
import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtCore, QtGui, uic, QtWebKit, QtWebKitWidgets

Ui_MainWindow, QtBaseClass = uic.loadUiType("main.ui")
Ui_PreviewWindow, QtBaseClass = uic.loadUiType("preview.ui")
Ui_ErrorMessage, QtBaseClass = uic.loadUiType("errormsg.ui")

class MainWindow(QWidget, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.save_toggle = 0
        self.error = None

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        # Make local modifications (settings).
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        if os.name == 'posix':
            self.resize(367, 272)
            shift=[-185,0]
        else:
            shift=[-181, 0]
        self.move(shift[0] + (resolution.width() / 2) - (self.frameSize().width() / 2), shift[1] + (resolution.height() / 2) - (self.frameSize().height() / 2))
        
        # Connect up the buttons.
        ### PBPTool
        self.Icon0Btn.clicked.connect(self.make_OpenFileDialog("Icon0"))
        self.Icon1Btn.clicked.connect(self.make_OpenFileDialog("Icon1"))
        self.Pic0Btn.clicked.connect(self.make_OpenFileDialog("Pic0"))
        self.Pic1Btn.clicked.connect(self.make_OpenFileDialog("Pic1"))
        self.Snd0Btn.clicked.connect(self.make_OpenFileDialog("Snd0"))
        self.BootBtn.clicked.connect(self.make_OpenFileDialog("Boot"))
        self.ImageEditorBtn.clicked.connect(self.make_Editor('Image'))
        self.PBPOutputBtn.clicked.connect(self.make_OpenFileDialog("PBPOutput"))
        self.PBPSaveBtn.clicked.connect(self.Archive_Eboot)
        ### AT3Tool
        self.At3InBtn.clicked.connect(self.make_OpenFileDialog("At3In"))
        self.AudioEditorBtn.clicked.connect(self.make_Editor('Audio'))
        self.At3ConvertBtn.clicked.connect(self.make_Convert("At3", self.At3InEdit.text()))
        ### PMFTool
        self.VidInBtn.clicked.connect(self.make_OpenFileDialog("VidIn"))
        self.VideoEditorBtn.clicked.connect(self.make_Editor('Video'))
        self.VidConvertBtn.clicked.connect(self.make_Convert("Vid", self.VidInEdit.text()))
        self.PmfInBtn.clicked.connect(self.make_OpenFileDialog("PmfIn"))
        self.UmdStreamComposer.clicked.connect(self.make_Editor('Umd'))
        self.PmfConvertBtn.clicked.connect(self.make_Convert("Pmf", self.PmfInEdit.text()))
        ### Settings
        self.PmfSettingsBtn.clicked.connect(self.ff_opt_defaults)
        self.AudEditorBtn.clicked.connect(self.make_OpenFileDialog("AudEditor"))
        self.ImgEditorBtn.clicked.connect(self.make_OpenFileDialog("ImgEditor"))
        self.VidEditorBtn.clicked.connect(self.make_OpenFileDialog("VidEditor"))
        self.At3EditorBtn.clicked.connect(self.make_OpenFileDialog("At3Editor"))
        self.FFEditorBtn.clicked.connect(self.make_OpenFileDialog("FFEditor"))
        self.UmdEditorBtn.clicked.connect(self.make_OpenFileDialog("UmdEditor"))
        
        self.TabContainer.currentChanged.connect(self.SaveSettings)
        self.LoadSettings()
        self.show()
        self.preview = PreviewWindow()
        
    def Archive_Eboot(self):
        func = Functions()
        out_folder = self.PBPOutputEdit.text()
        title = self.TitleEdit.text()
        if out_folder and title:
            # Copy all files to directory
            output_folder = out_folder+'/'+title
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            files = {'icon0':'/tools/tmp/icon0.png', 
                     'icon1':'/tools/tmp/icon1.pmf',
                     'pic0':'/tools/tmp/pic0.png', 
                     'pic1':'/tools/tmp/pic1.png', 
                     'snd0':'/tools/tmp/snd0.at3', 
                     'boot':'/tools/tmp/boot.png'}
            for file in files:
                filename, file_extension = os.path.splitext(files[file])
                try:
                    shutil.copy(func.config_folder+files[file], output_folder + '/' + file + file_extension)
                except Exception as e:
                    pass
                    #print(e)
            # Write metadata to readme
            with open(output_folder+'/'+'README.txt', 'w') as readme:
                readme.write("Title: %s\nVer: %s\nGame: %s\nAuthor: %s\nContact: %s\nComment: %s\n" % (self.TitleEdit.text(), self.VersionEdit.text(), self.GameEdit.text(), self.AuthorEdit.text(), self.ContactEdit.text(), self.CommentEdit.toPlainText()))
            # Archive files into a single file
            shutil.make_archive(output_folder, 'zip', output_folder)
            # Move archive and screenshot to output folder
            shutil.copy(output_folder+'.zip', output_folder)
            os.remove(output_folder+'.zip')
            func.Take_Screenshot('file:///'+func.config_folder+'/tools/preview.html', output_folder+'/screenshot.png')
        elif not title and not out_folder:
            self.make_ErrorMessage('An output folder and title have not been set.')
        elif not title:
            self.make_ErrorMessage('You are missing a title for your eboot.')
        elif not out_folder:
            self.make_ErrorMessage('An output folder has not been set.')
        
    def ff_opt_defaults(self):
        self.PmfSettingsEdit.setPlainText("-an -c:v rawvideo -y -vf scale=144:80,setsar=1/1,setdar=9/5")
    def SaveSettings(self):
        if self.TabContainer.currentIndex() != 4 and self.save_toggle == 1:
            func = Functions()
            func.SaveOpts(self.PmfSettingsEdit.toPlainText(),
                          self.AudEditorEdit.text(),
                          self.ImgEditorEdit.text(), 
                          self.VidEditorEdit.text(), 
                          self.At3EditorEdit.text(), 
                          self.FFEditorEdit.text(), 
                          self.UmdEditorEdit.text(), 
                          self.PBPOutputEdit.text(),
                          self.AuthorEdit.text(),
                          self.ContactEdit.text(),
                          self.CommentEdit.toPlainText())
            self.save_toggle = 0
        elif self.TabContainer.currentIndex() == 0 or self.TabContainer.currentIndex() == 3 or self.TabContainer.currentIndex() == 4:
            self.save_toggle = 1
    def LoadSettings(self):
        func = Functions()
        config = func.LoadOpts()
        # Set preferences on settings tab
        self.PmfSettingsEdit.setText(config['Settings']['ff_opts'])
        self.AudEditorEdit.setText(config['Settings']['audio_editor'])
        self.ImgEditorEdit.setText(config['Settings']['image_editor'])
        self.VidEditorEdit.setText(config['Settings']['video_editor'])
        self.At3EditorEdit.setText(config['Settings']['at3tool'])
        self.FFEditorEdit.setText(config['Settings']['ffmpeg'])
        self.UmdEditorEdit.setText(config['Settings']['umd_tools'])
        self.PBPOutputEdit.setText(config['Settings']['output_folder'])
        # Set possibly useful metadata on metadata tab
        self.AuthorEdit.setText(config['Metadata']['author'])
        self.ContactEdit.setText(config['Metadata']['contact'])
        self.CommentEdit.setText(config['Metadata']['comment'])
    def make_ErrorMessage(self, text):
        self.error = ErrorMessage()
        self.error.show_message(self, text)
    def make_Editor(self, editorID, InFile=None):
        def open_editor():
            func = Functions()
            if editorID == "Image":
                program = self.ImgEditorEdit.text()
            elif editorID == "Audio":
                program = self.AudEditorEdit.text()
            elif editorID == "Video":
                program = self.VidEditorEdit.text()
            elif editorID == "Umd" and os.name == 'nt':
                program = self.UmdEditorEdit.text()
            else:
                program = None
            if program:
                try:
                    subprocess.Popen('"'+program+'"')
                except:
                    subprocess.Popen(program)
            elif os.name == 'posix':
                self.make_ErrorMessage("This editor does not run under Posix operating systems.")
            else:
                self.make_ErrorMessage("This editor has not been configured in the settings.")
        return open_editor
    def make_Convert(self, convertID, InFile):
        def Convert():
            func = Functions()
            InFile = getattr(self, convertID+'InEdit').text()
            if InFile:
                dialog = QFileDialog()
                dialog.raise_()
                fileName, _ = dialog.getSaveFileName(self, "Save As...", InFile, "All Files (*.*)", options=QFileDialog.Options())
                if fileName:
                    convertBtn = getattr(self, convertID+'ConvertBtn')
                    old_text = convertBtn.text()
                    convertBtn.setText('proc...')
                    self.setEnabled(False)
                    QApplication.processEvents()
                    if fileName != InFile:
                        print("Saving file as "+ fileName)
                        if convertID == "At3":
                            if self.At3EditorEdit.text() and self.FFEditorEdit.text():
                                func.At3Convert(InFile, fileName)
                            else:
                                self.make_ErrorMessage("FFMpeg or the At3Tool has not been configured in the settings.")
                        elif convertID == "Vid":
                            if self.FFEditorEdit.text():
                                func.VidConvert(InFile, fileName)
                            else:
                                self.make_ErrorMessage("FFMpeg has not been configured in the settings.")
                        elif convertID == "Pmf":
                            func.PmfConvert(InFile, fileName)
                        convertBtn.setText(old_text)
                    else:
                        self.make_ErrorMessage("You can't save over the file you are converting!")
                    self.setEnabled(True)
            else:
                self.make_ErrorMessage('You are missing an input file.')
                
        return Convert
    def make_OpenFileDialog(self, buttonID):
        def OpenFileDialog():
            EditEntry = getattr(self, buttonID+'Edit')
            # Set Filter
            if buttonID == "At3In":
                filter = 'Audio Files (*.aac *.flac *.mp3 *.ogg *.wav);;All Files (*.*)'
                fileOut_ext = '.at3'
            elif buttonID == "VidIn":
                filter = 'Media Files (*.avi *.mkv *.mov *.mp4 *.mpg *.webm);;All Files (*.*)'
                fileOut_ext = '.avi'
            elif buttonID == "PmfIn":
                filter = 'MPS Files (*.mps)'
                fileOut_ext = '.pmf'
            elif buttonID == "Icon1":
                filter = 'PMF Files (*.pmf)'
            elif buttonID == "Snd0":
                filter = 'AT3 Files (*.at3)'
            elif "Editor" in buttonID:
                filter = 'All Files (*.*)'
            else:
                filter = 'Image Files (*.png);;All Files (*.*)'
            if buttonID == "PBPOutput":
                fileName = QFileDialog().getExistingDirectory(self, "Open directory")
            else:
                fileName, _ = QFileDialog().getOpenFileName(self, "Open file", EditEntry.text(), filter, options=QFileDialog.Options())
        
            # Update text entry and preview as necessary
            if fileName:
                func = Functions()
                self.setEnabled(False)
                QApplication.processEvents()
                if buttonID == "Icon1" and self.FFEditorEdit.text():
                    # Convert pmf files to .webm for preview
                    func.PVidConvert(fileName)
                elif buttonID == "Snd0" and self.At3EditorEdit.text():
                    # Convert at3 files to .ogg for preview
                    func.PAudConvert(fileName)
                self.setEnabled(True)
                EditEntry.setText(fileName)
                if self.TabContainer.currentIndex() == 0:
                    self.preview.update_preview(self.Icon0Edit.text(), self.Icon1Edit.text(), self.Pic0Edit.text(), self.Pic1Edit.text(),self.Snd0Edit.text(),self.BootEdit.text())
        return OpenFileDialog
    
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                self.preview.hide()
                if self.error:
                    self.error.hide()
            else:
                self.preview.show()
                if self.error:
                    self.error.show()
        elif event.type() == QtCore.QEvent.ActivationChange:
            if QtCore.QEvent.WindowActivate:
                if self.error:
                    self.error.raise_()
    def closeEvent(self, event):
        self.preview.closeEvent(event)
        if self.error:
            self.error.closeEvent(event)
        
class PreviewWindow(QWidget, Ui_PreviewWindow):
    def __init__(self, parent=None):
        super(PreviewWindow, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        func = Functions()
        
        # Make local modifications
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move(240 + (resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 2) - (self.frameSize().height() / 2))
        self.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
        self.webView.setUrl(QtCore.QUrl('file:///'+func.config_folder+'/tools/preview.html'))
        self.show()
    
    def update_preview(self, icon0, icon1, pic0, pic1, snd0, boot):
        func = Functions()
        ## Copy files to tmp folder
        tmp_folder = func.config_folder +"/tools/tmp/"
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)
        files = {'icon0':icon0, 'icon1':icon1, 'pic0':pic0, 'pic1':pic1, 'snd0':snd0, 'boot':boot}
        for file in files:
            filename, file_extension = os.path.splitext(files[file])
            try:
                shutil.copy(files[file], tmp_folder + file + file_extension)
            except Exception as e:
                pass
                #print(e)
        ## Reload webview
        self.webView.reload()
        
    def closeEvent(self, event):
        self.close()
        event.accept()

class ErrorMessage(QWidget, Ui_ErrorMessage):
    def __init__(self, parent=None):
        super(ErrorMessage, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        func = Functions()
        self.mainwindow = None
        
        # Make local modifications
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 2) - (self.frameSize().height() / 2))
        
        # Connect button
        self.pushButton.clicked.connect(self.closeEvent)
        
        
    def show_message(self, mainwindow, text):
        self.mainwindow = mainwindow
        self.mainwindow.setEnabled(False)
        self.label.setText(text)
        self.show()
        
    def closeEvent(self, event):
        self.mainwindow.setEnabled(True)
        self.hide()
        self.close()
        self.mainwindow.error = None
        
import configparser
class Functions():
    def __init__(self):
        # Get local settings
        self.config_folder = os.getcwd()
        self.tmp_folder = self.config_folder+'/tools/tmp'
        self.config = self.LoadOpts()
        
    def SaveOpts(self, ff_opts='-an -c:v rawvideo -y -vf scale=144:80,setsar=1/1,setdar=9/5', audedit='', imgedit='', videdit='', at3tool='', ffmpeg='', umdedit='', output='', author='', contact='', comment=''):
        config = configparser.ConfigParser()
        # Save default settings
        config['Settings'] = {'ff_opts': ff_opts,
                              'audio_editor': audedit,
                              'image_editor': imgedit,
                              'video_editor': videdit,
                              'at3tool': at3tool,
                              'ffmpeg': ffmpeg,
                              'umd_tools': umdedit,
                              'output_folder': output}
        config['Metadata'] = {'author': author,
                              'contact': contact,
                              'comment': comment}
        if os.name == 'posix' and config['Settings']['ffmpeg'] == "":
            # Set default linux settings
            config['Settings'].update({'audio_editor': '/usr/bin/audacity',
                                  'image_editor': '/usr/bin/gimp',
                                  'video_editor': '/usr/bin/lightworks',
                                  'ffmpeg': '/usr/bin/ffmpeg'})
        with open(self.config_folder+'/EbootCK.ini', 'w') as configfile:
            config.write(configfile)
    def LoadOpts(self):
        config = configparser.ConfigParser()
        configfile = self.config_folder+'/EbootCK.ini'
        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)
        if os.path.exists(configfile):
            config.read(configfile)
        else:
            self.SaveOpts()
            config.read(configfile)
        return config
    def Take_Screenshot(self, url, outfile):
        output = outfile
        webViewport = QtWebKitWidgets.QWebView()
        webViewport.resize(480, 272)
        webViewport.load(QtCore.QUrl(url))
        webViewport.loadFinished.connect(self._loadFinished(webViewport, output))
    def _loadFinished(self, webViewport, OutFile):
        def web_to_image():
            webViewport.show()
            frame = webViewport.page().mainFrame()
            frame.page().setViewportSize(frame.contentsSize())
            # render image
            image = QtGui.QImage(frame.page().viewportSize(), QtGui.QImage.Format_ARGB32)
            painter = QtGui.QPainter(image)
            frame.render(painter)
            painter.end()
            image.save(OutFile)
            webViewport.hide()
            webViewport.close()
            webViewport.destroy()
        return web_to_image
    def At3Convert(self, InFile, OutFile):
        TmpFile = self.tmp_folder+'/audio.wav'
        # Convert original to wav
        command = '{0} -i {1} -y -c:a pcm_s16le -vn -ar 44100 {2}'.format(self.config['Settings']['ffmpeg'], str(InFile), str(TmpFile))
        subprocess.call(command, shell=True, stdout=subprocess.PIPE)
        ## Convert wav to preview ogg
        ##command = '{0} -i {1} -y -vn -c:a libvorbis {2}'.format(self.config['Settings']['ffmpeg'], str(TmpFile), self.tmp_folder+'/audio.ogg')
        ##subprocess.call(command, shell=True, stdout=subprocess.PIPE)
        # Convert wav to at3 file
        command = '{0} -br 64 -wholeloop -e {1} {2}'.format(self.config['Settings']['at3tool'], str(TmpFile), str(OutFile))
        if os.name == 'posix':
            ## Add at3tool wine wrapper
            command = 'wine {0}'.format(command)
        print(command)
        at3convert = subprocess.call(command, shell=True)
        self.PAudConvert(OutFile)
        os.remove(TmpFile)
        
    def VidConvert(self, InFile, OutFile):
        # Convert original to avi file
        command = '{0} -i {1} -y {2} {3}'.format(self.config['Settings']['ffmpeg'], str(InFile), self.config['Settings']['ff_opts'], str(OutFile))
        ffconvert = subprocess.call(command, shell=True, stdout=subprocess.PIPE)
        # Convert avi file to preview webm
        self.PVidConvert(OutFile)
    def PmfConvert(self, InFile, OutFile):
        with open(InFile, "rb") as f:
            mps_size, height, width, video_dur = self.get_mps_info(InFile)
            pmf_header = self.build_pmf_header(mps_size, height, width, video_dur).ljust(4096,"0")
            pmf_file = open(OutFile, "w+b")
            pmf_file.write(binascii.unhexlify(pmf_header)+f.read())
    def PVidConvert(self, InFile):
        OutFile = self.tmp_folder+'/video.webm'
        command = '{0} -i {1} -y -an -qmax 25 -threads 2 {2}'.format(self.config['Settings']['ffmpeg'], str(InFile), str(OutFile))
        ffconvert = subprocess.call(command, shell=True)
    def PAudConvert(self, InFile):
        OutFile = self.tmp_folder+'/audio.ogg'
        TmpFile = self.tmp_folder+'/snd0.wav'
        # Convert At3 to wav
        command = '{0} -repeat 1 -d {1} {2}'.format(self.config['Settings']['at3tool'], str(InFile), str(TmpFile))
        if os.name == 'posix':
            ## Add at3tool wine wrapper
            command = 'wine {0}'.format(command)
        print(command)
        at3convert = subprocess.call(command, shell=True)
        # Convert wav to preview ogg
        command = '{0} -i {1} -y -c:a libvorbis {2}'.format(self.config['Settings']['ffmpeg'], str(TmpFile), str(OutFile))
        ffconvert = subprocess.call(command, shell=True)
        os.remove(TmpFile)
    def get_mps_info(self, InFile):
        mps_size = hex(os.path.getsize(InFile))[2:].rjust(8,"0")
        if os.name == 'nt':
            ffprobe_exec = '/ffprobe.exe'
        elif os.name == 'posix':
            ffprobe_exec = '/ffprobe'
        ffprobe = os.path.dirname(self.config['Settings']['ffmpeg'])+ffprobe_exec
        ffprocess = subprocess.Popen([ffprobe, '-i', InFile], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        for x in ffprocess.stdout.readlines():
            if "Stream" in str(x):
                dimension = re.search(' (\d+?x\d+?) ', str(x))
                if dimension:
                    width = dimension.group(1).split("x")[0]
                    height = dimension.group(1).split("x")[1]
                else:
                    print("Failed to get video dimensions.")
            elif "Duration" in str(x):
                video_length = str(x).split(" ")[3][:-1].split(":")
                hour = int(video_length[0])*60*60*100
                mins = int(video_length[1])*60*100
                secs = int(video_length[2].split(".")[0])*100
                centisec = int(video_length[2].split(".")[1])
                duration = hour+mins+secs+centisec
                video_dur = hex(int(duration)*1080)[2:].rjust(8,"0")
        return mps_size, height, width, video_dur
    def build_pmf_header(self, mps_size, video_height, video_width, video_dur, dev_hook_fix=0, pmf_type=14):
        pmf_id = "50534D46" ## PSMF
        pmf_ver = binascii.hexlify(str(pmf_type).rjust(4,'0').encode('utf-8')).decode() ## 0014
        
        pmf_size = "00000800" ## 2048 bytes from start of header
        mps_size = mps_size
        unk1 = "0000"
        tick_freq = "00015F90" ## 90k something
        mux_rate = "000061A8" ## Equal to program_mux_rate in mps pack_header
        height = hex(int(video_height))[2:-1].rjust(2,"0")
        width = hex(int(video_width))[2:-1].rjust(2,"0")
        if pmf_type == 12:
            table_size = "0000004E"  ## Size of the mapping table from 0x54
            table_size2 = "00000034"  ## Size of the mapping table from 0x6E
            unk2 = "0201"+table_size2+"0000"
            dh_video_dur = "00696F75"
            unk3 = "0001000000220002E00021EF"+unk1*4+width+height+"110000BD002004"+unk1*5+"0202"
        elif pmf_type == 14:
            table_size = "0000003E"
            table_size2 = "00000024"
            unk2 = "0101"+table_size2+"0000"
            dh_video_dur = "0005F49C"
            if dev_hook_fix == 1:
                unk3_byte = "16"
            else:
                unk3_byte = "14"
            unk3 = "0001000000120001E00020"+unk3_byte+unk1*4+width+height+"0000"
        if dev_hook_fix == 1:
            video_dur = dh_video_dur
        else:
            video_dur = video_dur

        ## PMF Header Ordering ##
        pmf_buffer = pmf_id+pmf_ver+pmf_size+mps_size+unk1*32+table_size+unk1+tick_freq+unk1+video_dur+mux_rate+tick_freq+unk2+tick_freq+unk1+video_dur+unk3
        return pmf_buffer
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
