import os
import sys
import yt_dlp
import shutil
import pygame
import requests
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QIcon
from googleapiclient.discovery import build

API_KEY = 'API'

class MusikiApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MÛSİKİ")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: black; color: white; font-family: Arial;")

        main_layout = QtWidgets.QGridLayout(self)
        self.setWindowIcon(QtGui.QIcon('icon.ico'))

        title_label = QtWidgets.QLabel("MÛSİKİ", self)
        title_label.setAlignment(QtCore.Qt.AlignRight)
        title_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white;")
        main_layout.addWidget(title_label, 0, 1)

        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit(self)
        self.search_input.setPlaceholderText("Search for song...")
        self.search_input.setStyleSheet("font-size: 13px; background-color: #333; color: white; border-radius: 15px; padding: 10px;")
        search_layout.addWidget(self.search_input)
        
        self.search_button = QtWidgets.QPushButton("Search", self)
        self.search_button.setStyleSheet("font-size: 12px; background-color: #333; color: white; border-radius: 15px; padding: 10px 20px; height: 15px;")
        self.search_button.clicked.connect(self.search_songs)
        search_layout.addWidget(self.search_button)
        
        main_layout.addLayout(search_layout, 0, 0)

        results_groupbox = QtWidgets.QGroupBox("Search Results", self)
        results_groupbox.setStyleSheet("color: white;")
        results_layout = QtWidgets.QVBoxLayout()
        
        self.results_list = QtWidgets.QListWidget(self)
        self.results_list.setStyleSheet("font-size: 13px; background-color: #1c1c1c; color: white;")
        results_layout.addWidget(self.results_list)

        self.add_button = QtWidgets.QPushButton("Add", self)
        self.add_button.setStyleSheet("font-size: 12px; background-color: #333; color: white; border-radius: 10px; padding: 5px;")
        self.add_button.clicked.connect(self.add_song)
        results_layout.addWidget(self.add_button)
        
        results_groupbox.setLayout(results_layout)
        results_groupbox.setMinimumWidth(600)  
        main_layout.addWidget(results_groupbox, 1, 0)

        library_groupbox = QtWidgets.QGroupBox("Library", self)
        library_groupbox.setStyleSheet("color: white;")
        library_layout = QtWidgets.QVBoxLayout()
        
        self.current_directory = os.path.join(os.getcwd(), 'music')
        
        self.library_search_input = QtWidgets.QLineEdit(self)
        self.library_search_input.setPlaceholderText("Search in library...")
        self.library_search_input.setStyleSheet("font-size: 13px; background-color: #333; color: white; border-radius: 15px; padding: 10px;")
        self.library_search_input.textChanged.connect(self.search_library)
        library_layout.addWidget(self.library_search_input)
        self.library_list = QtWidgets.QListWidget(self)
        self.library_list.setStyleSheet("font-size: 12px; background-color: #1c1c1c; color: white;")
        library_layout.addWidget(self.library_list)
        
        main_layout.setColumnStretch(0, 2) 
        main_layout.setColumnStretch(1, 1)
        
        self.add_playlist_button = QtWidgets.QPushButton("Create Playlist", self)
        self.add_playlist_button.setStyleSheet("font-size: 12px; background-color: #333; color: white; border-radius: 10px; padding: 5px;")
        library_layout.addWidget(self.add_playlist_button)
        self.add_playlist_button.clicked.connect(self.add_playlist)

        self.delete_button = QtWidgets.QPushButton("Delete", self)
        self.delete_button.setStyleSheet("font-size: 12px; background-color: #333; color: white; border-radius: 10px; padding: 5px;")
        self.delete_button.clicked.connect(self.delete_song)
        library_layout.addWidget(self.delete_button)
        
        library_groupbox.setLayout(library_layout)
        main_layout.addWidget(library_groupbox, 1, 1)
        
        music_controls_layout = QtWidgets.QVBoxLayout()

        control_layout = QtWidgets.QHBoxLayout()
        
        self.song_title_label = QtWidgets.QLabel("Currently Playing: None  ", self)
        self.song_title_label.setStyleSheet("font-size: 16px; color: white;")
        control_layout.addWidget(self.song_title_label)

        self.play_button = QtWidgets.QPushButton("Play", self)
        self.play_button.setStyleSheet("font-size: 12px; background-color: #333; border-radius: 15px; padding: 10px;")
        self.play_button.setFixedSize(70, 35) 
        self.play_button.clicked.connect(self.play_song)
        
        self.loop_button = QtWidgets.QPushButton("Loop: False", self)
        self.loop_button.setStyleSheet("font-size: 12px; background-color: #333; border-radius: 15px; padding: 10px;")
        self.loop_button.setFixedSize(100, 35) 
        self.loop_button.clicked.connect(self.loop)
        
        self.next_button = QtWidgets.QPushButton("Play next: False", self)
        self.next_button.setStyleSheet("font-size: 12px; background-color: #333; border-radius: 15px; padding: 10px;")
        self.next_button.setFixedSize(120, 35) 
        self.next_button.clicked.connect(self.next)

        control_layout.addWidget(self.play_button) 
        control_layout.addStretch(1)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.loop_button)
        
        music_controls_layout.addLayout(control_layout)

        music_controls_layout.addLayout(control_layout)

        self.progress_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setStyleSheet("background-color: #1c1c1c;")
        self.progress_slider.sliderReleased.connect(self.seek_song)
        music_controls_layout.addWidget(self.progress_slider)

        self.progress_label = QtWidgets.QLabel("00:00 / 00:00", self)
        self.progress_label.setStyleSheet("font-size: 12px; color: white;")
        music_controls_layout.addWidget(self.progress_label)

        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("background-color: #1c1c1c;")
        self.volume_slider.valueChanged.connect(self.change_volume)
        music_controls_layout.addWidget(self.volume_slider)

        self.volume_label = QtWidgets.QLabel(f"Volume: {self.volume_slider.value()}%", self)
        self.volume_label.setStyleSheet("font-size: 12px; color: white;")
        music_controls_layout.addWidget(self.volume_label)
        
        self.library_list.itemClicked.connect(self.play_selected_song)

        main_layout.addLayout(music_controls_layout, 2, 0, 1, 2)
        
        self.setLayout(main_layout)

        if not os.path.exists('music'):
            os.makedirs('music')

        self.update_library()

        pygame.mixer.init()
        self.is_playing = False
        self.loop_mode = False
        self.next_mode = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.current_song_length = 0
        self.current_position = 0
        pygame.mixer.music.set_volume(50)
        self.library_list.itemDoubleClicked.connect(self.on_library_item_double_clicked)
        
    def loop(self):
        if self.loop_mode:
            self.loop_mode = False
            self.loop_button.setText("Loop: False")
        else:
            self.loop_mode = True
            self.loop_button.setText("Loop: True")
            
    def next(self):
        if self.next_mode:
            self.next_mode = False
            self.next_button.setText("Play next: False")
        else:
            self.next_mode = True
            self.next_button.setText("Play next: True")
            
    def add_playlist(self):
        folder_name, ok = QtWidgets.QInputDialog.getText(self, "New Playlist", "Playlist name:")
        
        if ok and folder_name:
            folder_name_with_tag = f"{folder_name} [Playlist]"
            new_folder_path = os.path.join('music', folder_name_with_tag)

            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                
                self.update_library()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", f"'{folder_name}' playlist is already available.")
                print(f"{folder_name}' playlist is already available.")

    def search_songs(self):
        query = self.search_input.text()
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        request = youtube.search().list(q=query, part='snippet', type='video', maxResults=20)
        response = request.execute()

        self.results_list.clear()
        
        for item in response['items']:
            title = item['snippet']['title']
            video_id = item['id']['videoId']
            thumbnail_url = item['snippet']['thumbnails']['default']['url'] 
            
            list_item =QtWidgets.QListWidgetItem(f"{title}  /  [https://www.youtube.com/watch?v={video_id}]")
            
            thumbnail_data = requests.get(thumbnail_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(thumbnail_data)
            
            icon = QIcon(pixmap)
            list_item.setIcon(icon)
            
            list_item.setSizeHint(QtCore.QSize(0, 30))
            
            self.results_list.addItem(list_item)

    def add_song(self):
        selected_item = self.results_list.currentItem()
        if selected_item:
            video_url = selected_item.text().split("  /  ")[1].strip()
            self.setWindowTitle("MÛSİKİ (Song is Downloading, Do Not Close the Application)")  
            self.download_song(video_url)
            self.update_library() 
            self.setWindowTitle("MÛSİKİ") 
            self.library_list.clear()  
            self.update_library()  

    def download_song(self, url):
        try:
            search_url = f"ytsearch:{url}"
            output_directory = os.path.join(self.current_directory, '%(title)s.%(ext)s')
            options = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'outtmpl':  output_directory,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([search_url])
        except Exception as e:
            error_msg = QtWidgets.QMessageBox(self)
            error_msg.setWindowTitle("Error")
            error_msg.setText(f"Error: {str(e)}")
            error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    border: none;
                    padding: 5px;
                }
            """)
            print(f"Error: {str(e)}")
            error_msg.exec_()
            
    def search_library(self):
        search_term = self.library_search_input.text().lower()
        self.library_list.clear()
        for filename in os.listdir('music'):
            if filename.endswith('.mp3') and search_term in filename.lower():
                self.library_list.addItem(filename)

    def update_library(self):
        self.library_list.clear()
        
        if self.current_directory != os.path.join(os.getcwd(), 'music'):
            self.library_list.addItem("...")

        for item in os.listdir(self.current_directory):
            item_path = os.path.join(self.current_directory, item)
            if os.path.isdir(item_path) or item.endswith('.mp3'):
                self.library_list.addItem(item)
                
    def on_library_item_double_clicked(self, item):
        if item.text() == "...":
            self.current_directory = os.path.dirname(self.current_directory)
        else:
            selected_path = os.path.join(self.current_directory, item.text())
            if os.path.isdir(selected_path):
                self.current_directory = selected_path
            elif selected_path.endswith('.mp3'):

                self.play_music(selected_path)

        self.update_library()

    def delete_song(self):
        selected_item = self.library_list.currentItem()
        if selected_item:
            song_name = selected_item.text()
            song_path = os.path.join('music', song_name)

            print(f"Deleting: {song_name}")
            
            pygame.quit()
            self.is_playing = False
            self.play_button.setText("Play")

            if os.path.isfile(song_path):
                if os.path.exists(song_path):
                    os.remove(song_path)
                    self.song_title_label.setText("Currently Playing: None  ")
                    print(f"Deleted file: {song_name}")
                    
            elif os.path.isdir(song_path):
                if os.path.exists(song_path):
                    shutil.rmtree(song_path)
                    print(f"Deleted folder: {song_name}")

            self.update_library()
                
    def play_selected_song(self):
        selected_item = self.library_list.currentItem()
        if not selected_item:
            return

        song_name = selected_item.text()
        song_path = os.path.join(self.current_directory, song_name)
        
        if os.path.isfile(song_path) and song_path.endswith('.mp3'):
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.is_playing = True
                self.timer.start(1000)
                self.current_song_length = self.get_song_length(song_path)
                self.update_progress_label(0)
                self.progress_slider.setRange(0, int(self.current_song_length))
                self.progress_slider.setEnabled(True)
                self.play_button.setText("Stop")
                self.current_position = 0
                self.song_title_label.setText(f"Currently Playing: {song_name}   ")
                print(f"Playing : {song_name}")
            except pygame.error as e:
                print(f"Pygame Error: {e}")

    def play_song(self):
        import pygame
        pygame.mixer.init()
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_button.setText("Play")
            print("Stopped")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.play_button.setText("Stop")
            print("Playing")

    def get_song_length(self, song_path):
        import pygame
        pygame.mixer.init()
        sound = pygame.mixer.Sound(song_path)  
        return sound.get_length()

    def update_progress(self):
        if self.is_playing:
            self.current_position += 1
            self.progress_slider.setValue(self.current_position)
            self.update_progress_label(self.current_position)

            if self.current_position >= self.current_song_length:
                self.current_position -= 1 
                
                if not self.loop_mode and self.next_mode:
                    self.play_next_song()

                if self.loop_mode:
                    self.play_current_song()

    def play_next_song(self):
        selected_item = self.library_list.currentItem()
        song_name = selected_item.text()
        current_directory = self.current_directory
        song_list = os.listdir(current_directory)
        song_list = [f for f in song_list if f.endswith('.mp3')]  

        current_index = song_list.index(song_name)
        
        if current_index + 1 < len(song_list):
            next_song_name = song_list[current_index + 1]
        else:
            next_song_name = song_list[0]

        song_path = os.path.join(current_directory, next_song_name)
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()

        self.is_playing = True
        self.play_button.setText("Stop")
        self.current_song_length = self.get_song_length(song_path)
        self.update_progress_label(0)
        self.progress_slider.setRange(0, int(self.current_song_length))
        self.progress_slider.setEnabled(True)
        self.current_position = 0
        
        self.song_title_label.setText(f"Currently Playing: {next_song_name}   ")

    def play_current_song(self):
        selected_item = self.library_list.currentItem()
        song_name = selected_item.text()
        song_path = os.path.join(self.current_directory, song_name)
        
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        
        self.is_playing = True
        self.play_button.setText("Stop")
        self.current_song_length = self.get_song_length(song_path)
        self.update_progress_label(0)
        self.progress_slider.setRange(0, int(self.current_song_length))
        self.progress_slider.setEnabled(True)
        self.current_position = 0

    def update_progress_label(self, current_time):
        total_time = self.current_song_length
        current_time_str = self.format_time(current_time)
        total_time_str = self.format_time(total_time)
        self.progress_label.setText(f"{current_time_str} / {total_time_str}")

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

    def seek_song(self):
        import pygame
        pygame.mixer.init()
        self.is_playing = True
        self.play_button.setText("Stop")
        seek_time = self.progress_slider.value()
        pygame.mixer.music.play(start=seek_time)
        self.current_position = seek_time
        self.update_progress_label(seek_time)

    def change_volume(self):
        import pygame
        pygame.mixer.init()
        volume = self.volume_slider.value() / 100  
        pygame.mixer.music.set_volume(volume)
        self.volume_label.setText(f"Volume: {self.volume_slider.value()}%")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MusikiApp()
    window.show()
    sys.exit(app.exec_())
