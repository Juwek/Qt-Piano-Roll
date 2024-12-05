import io
import shutil
import os
import sys
import threading
import wave
from pydub import AudioSegment

import bd

from PyQt6 import uic, QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QLine, QUrl, QPropertyAnimation, QThread, QPoint, QRect
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QLabel, QPushButton, \
    QGroupBox, QHBoxLayout, QLineEdit, QGridLayout, QFormLayout, QMessageBox, QWidget, QFileDialog
from PyQt6.QtMultimedia import QSoundEffect

template = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>900</width>
    <height>650</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QTableWidget" name="table">
    <property name="geometry">
     <rect>
      <x>30</x>
      <y>30</y>
      <width>650</width>
      <height>400</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>1</pointsize>
     </font>
    </property>
    <property name="sizeAdjustPolicy">
     <enum>QAbstractScrollArea::AdjustToContents</enum>
    </property>
    <property name="rowCount">
     <number>15</number>
    </property>
    <property name="columnCount">
     <number>15</number>
    </property>
    <attribute name="horizontalHeaderVisible">
     <bool>false</bool>
    </attribute>
    <attribute name="verticalHeaderVisible">
     <bool>false</bool>
    </attribute>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row>
     <property name="text">
      <string/>
     </property>
    </row>
    <row/>
    <row/>
    <row/>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column>
     <property name="text">
      <string/>
     </property>
    </column>
    <column/>
    <column/>
    <column/>
    <column/>
    <column/>
   </widget>
   <widget class="Line" name="line">
    <property name="geometry">
     <rect>
      <x>20</x>
      <y>30</y>
      <width>16</width>
      <height>381</height>
     </rect>
    </property>
    <property name="orientation">
     <enum>Qt::Vertical</enum>
    </property>
   </widget>
   <widget class="Line" name="end_line">
    <property name="geometry">
     <rect>
      <x>113</x>
      <y>30</y>
      <width>20</width>
      <height>381</height>
     </rect>
    </property>
    <property name="orientation">
     <enum>Qt::Vertical</enum>
    </property>
   </widget>
   <widget class="QGroupBox" name="inspector">
    <property name="geometry">
     <rect>
      <x>690</x>
      <y>30</y>
      <width>191</width>
      <height>401</height>
     </rect>
    </property>
    <property name="title">
     <string>GroupBox</string>
    </property>
   </widget>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>
'''


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.select = False
        self.a = False
        self.select_object = False
        self.object = None
        self.notes = ['img_notes/note.png', 'img_notes/note2.png', 'img_notes/note3.png', 'img_notes/note4.png',
                      'img_notes/note5.png', 'img_notes/note6.png', 'img_notes/note7.png']
        self.sounds = ['music/do.wav', 'music/re.wav', 'music/mi.wav', 'music/fa.wav', 'music/sol.wav',
                       'music/lya.wav', 'music/si.wav',]
        self.list_notes = [None]
        self.initUI()
        t = threading.Thread(target=self.play_music, daemon=True, args=())
        t.start()

    def initUI(self):
        f = io.StringIO(template)
        uic.loadUi(f, self)

        self.table: QTableWidget = self.table
        self.table.currentItemChanged.connect(self.current_item_changed)
        self.table.setMouseTracking(True)
        self.table.setColumnCount(24)
        self.table.setRowCount(14)
        self.table.horizontalHeader().setDefaultSectionSize(25)
        self.table.verticalHeader().setDefaultSectionSize(25)

        self.clear_table()
        self.set_notes()

        self.line: QLine = self.line
        self.line.move(-5, 30)
        self.line.resize(50, 25 * 14)

        self.label_sec = QLabel(self)
        self.label_sec.resize(210, 40)
        self.label_sec.move(125, 385)

        self.end_line: QLine = self.end_line
        self.end_line.resize(50, 25 * 14)
        self.end_line.move(28, 30)
        self.set_animation()

        self.button_start_animation = QPushButton(self)
        self.button_start_animation.setIcon(QIcon('buttons/play.png'))
        self.button_start_animation.move(35, 385)
        self.button_start_animation.resize(40, 40)
        self.button_start_animation.clicked.connect(self.press_start_animation)
        self.start = True

        self.button_reset_animation = QPushButton(self)
        self.button_reset_animation.setIcon(QIcon('buttons/reset.png'))
        self.button_reset_animation.move(80, 385)
        self.button_reset_animation.resize(40, 40)
        self.button_reset_animation.clicked.connect(self.press_reset_animation)

        self.button_slider = QPushButton(self)
        self.button_slider.move(30, 5)
        self.button_slider.resize(25, 25)

        self.insp = Inspector(self.inspector, self.table)
        self.name = 'table'

        self.add = QPushButton('Сохранить', self)
        self.add.move(330, 390)
        self.add.clicked.connect(self.func_add)

        self.get = QPushButton('Выгрузить', self)
        self.get.move(430, 390)
        self.get.clicked.connect(self.func_get)

        self.get = QPushButton('Скачать', self)
        self.get.move(530, 390)
        self.get.clicked.connect(self.create_mus)

    def clear_table(self):
        rows = self.table.rowCount()
        columns = self.table.columnCount()
        for i in range(rows):
            for j in range(columns):
                item = QTableWidgetItem("")
                item.setFlags(item.flags() & ~item.flags().ItemIsEditable)
                self.table.setItem(i, j, item)
                self.table.setCellWidget(i, j, None)

    def create_mus(self):
        self.full_sound = []
        notes = []
        rows = self.table.rowCount()
        columns = self.table.columnCount()
        for i in range(columns):
            col = []
            for j in range(rows):
                item = self.table.cellWidget(j, i)
                if isinstance(item, ImgNote) and item not in notes:
                    col.append(item.sound)
                    notes.append(item)
            self.full_sound.append(col)
        self.full_sound = self.full_sound[:int(self.duration / 500)]
        self.export_sound()

    def export_sound(self):
        export = []
        shutil.rmtree('export_sound')
        os.mkdir('export_sound')
        for i in self.full_sound:
            if len(i):
                if len(i) == 1:
                    export.append(*i)
                else:
                    sound = AudioSegment.from_file(i[0])
                    for j in i[1:]:
                        sound_dop = AudioSegment.from_file(j)
                        sound = sound.overlay(sound_dop)
                    path = f'export_sound/{self.full_sound.index(i)}.wav'
                    export.append(path)
                    sound.export(path, format='wav')
            else:
                export.append('music/silent.wav')

        start = AudioSegment.from_file(export[0])
        for i in export[1:]:
            sound_dop = AudioSegment.from_file(i)
            start = start + sound_dop
        name = QFileDialog.getSaveFileName(self, 'Сохранить в...')
        if name[0] != '':
            print(name)
            path = f'{name[0]}.wav'
            start.export(path, format='wav')

    def func_add(self):
        self.user = enter.get_user()
        bd.delete_table(self.user, self.name)
        for i in self.list_notes:
            i.table(self.user, self.name)

    def func_get(self):
        self.user = enter.get_user()
        self.new_notes = []
        shutil.rmtree('music_from_table')
        os.mkdir('music_from_table')
        notes = bd.get_table(self.user, self.name)
        if notes:
            for i in notes:
                data, ampl = i
                data_table, params = tuple(data.split('|'))
                data_table = list(map(lambda x: int(x) if x[0].isdigit() else x, data_table.split('-')))
                params = tuple(map(lambda x: int(x) if x[0].isdigit() else x, params.split('-')))

                path = f'music_from_table/{notes.index(i)}.wav'
                with wave.open(path, mode='wb') as file:
                    file.setparams(params)
                    file.writeframes(ampl)
                    object = ImgNote(self, data_table[-1], path)
                    object.clicked.connect(self.move_note)
                    object.row = data_table[0]
                    object.col = data_table[1]
                    self.new_notes.append(object)

            self.reset_table()

    def reset_table(self):
        self.clear_table()

        for note in self.new_notes:
            self.table.setCellWidget(note.row, note.col, note)
        self.get_table_items()

    def set_animation(self, duration=500):
        self.animation = QPropertyAnimation(self.line, b'pos')
        self.duration = duration
        self.label_sec.setText(f'Продолжительность в секундах: {duration / 1000}')
        self.animation.setDuration(self.duration)
        self.animation.setStartValue(QPoint(-5, 30))
        self.animation.setEndValue(QPoint(int(5 + (self.duration / 20) - 2), 30))
        self.animation.finished.connect(self.animation_is_finished)

    def press_start_animation(self):
        if self.start:
            self.start = False
            self.button_start_animation.setIcon(QIcon('buttons/pause.png'))
            self.animation.start()
        elif not self.start:
            self.start = True
            self.button_start_animation.setIcon(QIcon('buttons/play.png'))
            self.animation.stop()

    def press_reset_animation(self):
        self.animation.stop()
        self.line.move(-5, 30)
        self.button_start_animation.setIcon(QIcon('buttons/play.png'))
        self.start = True

    def animation_is_finished(self):
        self.start = True
        self.button_start_animation.setIcon(QIcon('buttons/play.png'))

    def mouseMoveEvent(self, event):
        if event.pos().x() >= 30 and event.pos().x() <= 610 and \
            event.pos().y() >= 5 and event.pos().y() <= 375:
            if event.pos().x() in [i for i in range(30, 606, 25)]:
                self.button_slider.move(event.pos().x(), 5)
                self.end_line.move(self.button_slider.pos().x() - 2, self.button_slider.pos().y() + 25)
                self.set_animation(int(((self.end_line.pos().x() - 3) / 25) * 500))

    def set_notes(self):
        step = 0
        start = 100
        for i in self.notes:
            sound_file = self.sounds[self.notes.index(i)]
            self.image = ImgNote(self, i, sound_file)
            image = self.image.get_img()
            self.image.move(start + step, 500)
            image.sound_file = sound_file
            image.pic_file = i
            image.clicked.connect(self.select_note)
            step += 50

    def current_item_changed(self, current: QTableWidgetItem):
        self.row, self.column = current.row(), current.column()
        if self.select:
            if self.row != None and self.column != None:
                self.table.setCellWidget(self.row, self.column, self.select_label)
                self.select = False
                self.insp.show(self.select_label)
                self.select_label.row = self.row
                self.select_label.col = self.column
                self.get_table_items()
                self.select_label = None
        elif self.select_object:
            if self.object.row != None and self.object.col != None:
                self.table.setCellWidget(self.row, self.column, self.object)
                self.select_object = False
                self.object.row = self.row
                self.object.col = self.column
                self.object = None

    def select_note(self):
        self.select = True
        clickedLabel: ClickedLabel = self.sender()
        image: QImage = clickedLabel.pixmap().toImage()
        self.insp.hide()
        self.select_label = ImgNote(self, clickedLabel.pic_file, clickedLabel.sound_file)
        self.select_label.clicked.connect(self.move_note)

    def move_note(self):
        self.object: ImgNote = self.sender()
        self.object.row = self.row
        self.object.col = self.column
        self.select_object = True
        self.insp.show(self.object)
        self.get_table_items()

    def get_table_items(self):
        self.list_notes = []
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                item = self.table.cellWidget(i, j)
                if isinstance(item, ImgNote) and item not in self.list_notes:
                    self.list_notes.append(item)
        self.list_notes = sorted(self.list_notes, key=lambda x: x.pos().x())

    def play_music(self):
        while True:
            if self.start:
                QThread.msleep(1)
            else:
                while not self.start:
                    for i in self.list_notes:
                        i: ImgNote
                        if i != None and i.row != None and i.col != None and \
                            self.animation.currentValue().x() == i.pos().x():
                            i.play_sound()
                    QThread.msleep(1)

    def closeEvent(self, event):
        self.start = True
        self.button_start_animation.setIcon(QIcon('buttons/play.png'))
        self.animation.stop()
        dlg = QMessageBox(self)
        reply = dlg.question(self, 'Уведомление', 'Хотите выйти?', QMessageBox.StandardButton.Ok,
                             QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Ok:
            event.accept()
        else:
            event.ignore()


class Enter(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(750, 300, 300, 250)
        self.initUI()

    def initUI(self):
        self.main_group = QGroupBox(self)
        self.main_form = QFormLayout(self)
        self.button_enter = QPushButton('Войти', self)
        self.button_reg = QPushButton('Зарегистрироваться', self)
        self.main_form.addWidget(self.button_enter)
        self.main_form.addWidget(self.button_reg)
        self.main_group.setLayout(self.main_form)
        self.main_group.move(75, 80)
        self.button_enter.clicked.connect(self.enter)
        self.button_reg.clicked.connect(self.register)

    def enter(self):
        self.main_group.hide()
        self.back = QPushButton(self)
        self.back.resize(50, 30)
        self.back.move(10, 10)
        self.back.setIcon(QIcon('buttons/back.png'))
        self.back.show()
        self.back.clicked.connect(self.back_to_menu)
        self.alert = QLabel(self)
        self.alert.move(35, 180)
        self.alert.resize(200, 50)
        self.alert.hide()
        self.group = QGroupBox(self)
        self.enter_form = QFormLayout(self)
        self.login = QLineEdit(self)
        self.password = QLineEdit(self)
        self.enter_button = QPushButton('Войти', self)
        self.enter_button.clicked.connect(lambda: self.check_enter(self.login.text(), self.password.text()))
        self.enter_form.addRow('Введите логин:', self.login)
        self.enter_form.addRow('Введите пароль:', self.password)
        self.enter_form.addWidget(self.enter_button)
        self.group.setLayout(self.enter_form)
        self.group.move(35, 80)
        self.group.show()

    def back_to_menu(self):
        self.alert.hide()
        self.group.hide()
        self.back.hide()
        self.main_group.show()

    def register(self):
        self.main_group.hide()
        self.back = QPushButton(self)
        self.back.resize(50, 30)
        self.back.move(10, 10)
        self.back.setIcon(QIcon('buttons/back.png'))
        self.back.show()
        self.back.clicked.connect(self.back_to_menu)
        self.alert = QLabel(self)
        self.alert.move(22, 180)
        self.alert.resize(200, 50)
        self.alert.hide()
        self.group = QGroupBox(self)
        self.reg_form = QFormLayout(self)
        self.login = QLineEdit(self)
        self.password = QLineEdit(self)
        self.reg_button = QPushButton('Зарегистрироваться', self)
        self.reg_button.clicked.connect(lambda: self.check_register(self.login.text(), self.password.text()))
        self.reg_form.addRow('Придумайте логин:', self.login)
        self.reg_form.addRow('Придумайте пароль:', self.password)
        self.reg_form.addWidget(self.reg_button)
        self.group.setLayout(self.reg_form)
        self.group.move(22, 80)
        self.group.show()

    def check_enter(self, login, password):
        if login == '' or password == '':
            self.alert.show()
            self.alert.setText('Введите данные')
        else:
            answer = bd.check_user_for_password(login, password)
            if answer == 2:
                self.alert.show()
                self.alert.setText('Пользователя с таким логином\nне существует')
            elif answer == 3:
                self.alert.show()
                self.alert.setText('Неверный пароль')
            else:
                self.user = login
                self.hide()
                main.show()

    def check_register(self, login, password):
        if login == '' or password == '':
            self.alert.show()
            self.alert.setText('Введите данные')
        else:
            answer = bd.register_user(login, password)
            if answer == 2:
                self.alert.show()
                self.alert.setText('Пользователь с таким логтном\nуже существует')
            else:
                self.user = login
                self.hide()
                main.show()

    def get_user(self):
        return self.user


class ClickedLabel(QLabel):
    clicked = pyqtSignal()

    def files(self):
        self.sound_file = None
        self.pic_file = None

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class ImgNote(ClickedLabel):
    def __init__(self, a, pixmap: str, sound=None):
        super(ImgNote, self).__init__(a)
        self.image = ClickedLabel(self)
        self.pic = pixmap
        self.image.setPixmap(QPixmap(self.pic))
        self.sound = sound
        self.effect = QSoundEffect()
        self.effect.setSource(QUrl.fromLocalFile(self.sound))
        self.row = None
        self.col = None

    def get_img(self):
        return self.image

    def play_sound(self):
        self.effect.play()

    def set_volume(self, volume: int):
        self.effect.setVolume(volume / 10)

    def table(self, user, name):
        source = wave.open(self.sound, mode="rb")
        params = source.getparams()
        frames = source.readframes(params.nframes)
        params = tuple(params)
        frames_count = params[3]
        new_params = '-'.join(map(lambda x: str(x), list(params)))
        source.close()

        bd.add_table(user, name, f'{self.row}-{self.col}-{self.pic}|{new_params}', frames)


class Inspector:
    def __init__(self, ins, tab):
        self.inspector: QGroupBox = ins
        self.inspector.move(690, 23)
        self.inspector.resize(190, 408)
        self.inspector.setTitle('Инспектор')
        layout = QFormLayout()
        self.button_play_sound = QPushButton()
        self.button_play_sound.setIcon(QIcon('buttons/play.png'))
        self.button_play_sound.resize(40, 40)
        self.button_play_sound.clicked.connect(self.play_sound)
        self.line_volume = QLineEdit()
        self.button_del_note = QPushButton('Удалить')
        self.button_apply = QPushButton('Применить')
        self.button_apply.clicked.connect(self.set_volume)
        self.button_del_note.clicked.connect(self.delete_note)
        layout.addWidget(self.button_play_sound)
        layout.addRow('Громкость:', self.line_volume)
        layout.addWidget(self.button_apply)
        layout.addWidget(self.button_del_note)
        layout.setContentsMargins(15, 20, 15, 0)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.inspector.setLayout(layout)
        self.inspector.hide()

        self.table: QTableWidget = tab

    def show(self, note: ImgNote):
        self.inspector.show()
        self.note = note

    def hide(self):
        self.inspector.hide()

    def set_volume(self):
        if self.line_volume.text() != '' and self.line_volume.text().isdigit():
            if int(self.line_volume.text()) >= 0 and int(self.line_volume.text()) <= 10:
                self.note.set_volume(int(self.line_volume.text()))

    def play_sound(self):
        self.note.play_sound()

    def delete_note(self):
        self.table.setCellWidget(self.note.row, self.note.col, None)
        self.note.row = None
        self.note.col = None
        self.inspector.hide()
        App().get_table_items()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = App()
    enter = Enter()
    enter.show()
    sys.exit(app.exec())