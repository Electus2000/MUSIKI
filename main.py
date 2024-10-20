import os
import sys
import yt_dlp
import pygame
from PyQt5 import QtWidgets, QtCore, QtGui
from googleapiclient.discovery import build

API_KEY = 'API' 

class MusikiApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MÛSİKİ")
        self.setGeometry(100, 100, 900, 500)
        self.setStyleSheet("background-color: black; color: white; font-family: Arial;")

        main_layout = QtWidgets.QGridLayout(self)
        self.setWindowIcon(QtGui.QIcon('icon.ico'))

        title_label = QtWidgets.QLabel("MÛSİKİ", self)
        title_label.setAlignment(QtCore.Qt.AlignRight)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        main_layout.addWidget(title_label, 0, 1)

        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit(self)
        self.search_input.setPlaceholderText("Search for song...")
        self.search_input.setStyleSheet("background-color: #333; color: white; border-radius: 15px; padding: 10px;")
        search_layout.addWidget(self.search_input)
        
        self.search_button = QtWidgets.QPushButton("Search", self)
        self.search_button.setStyleSheet("background-color: #333; color: white; border-radius: 15px; padding: 10px 20px; height: 15px;")
        self.search_button.clicked.connect(self.search_songs)
        search_layout.addWidget(self.search_button)
        
        main_layout.addLayout(search_layout, 0, 0)

        results_groupbox = QtWidgets.QGroupBox("Search Results", self)
        results_groupbox.setStyleSheet("color: white;")
        results_layout = QtWidgets.QVBoxLayout()
        
        self.results_list = QtWidgets.QListWidget(self)
        self.results_list.setStyleSheet("background-color: #1c1c1c; color: white;")
        results_layout.addWidget(self.results_list)

        self.add_button = QtWidgets.QPushButton("Add", self)
        self.add_button.setStyleSheet("background-color: #333; color: white; border-radius: 10px; padding: 5px;")
        self.add_button.clicked.connect(self.add_song)
        results_layout.addWidget(self.add_button)
        
        results_groupbox.setLayout(results_layout)
        results_groupbox.setMinimumWidth(600)  
        main_layout.addWidget(results_groupbox, 1, 0)

        library_groupbox = QtWidgets.QGroupBox("Library", self)
        library_groupbox.setStyleSheet("color: white;")
        library_layout = QtWidgets.QVBoxLayout()
        
        self.library_search_input = QtWidgets.QLineEdit(self)
        self.library_search_input.setPlaceholderText("Search in library...")
        self.library_search_input.setStyleSheet("background-color: #333; color: white; border-radius: 15px; padding: 10px;")
        self.library_search_input.textChanged.connect(self.search_library)
        library_layout.addWidget(self.library_search_input)
        self.library_list = QtWidgets.QListWidget(self)
        self.library_list.setStyleSheet("background-color: #1c1c1c; color: white;")
        library_layout.addWidget(self.library_list)
        
        main_layout.setColumnStretch(0, 2) 
        main_layout.setColumnStretch(1, 1)

        self.delete_button = QtWidgets.QPushButton("Delete", self)
        self.delete_button.setStyleSheet("background-color: #333; color: white; border-radius: 10px; padding: 5px;")
        self.delete_button.clicked.connect(self.delete_song)
        library_layout.addWidget(self.delete_button)
        
        library_groupbox.setLayout(library_layout)
        main_layout.addWidget(library_groupbox, 1, 1)
        
        music_controls_layout = QtWidgets.QVBoxLayout()

        control_layout = QtWidgets.QHBoxLayout()

        self.play_button = QtWidgets.QPushButton("Play", self)
        self.play_button.setStyleSheet("font-size: 12px; background-color: #333; border-radius: 15px; padding: 10px;")
        self.play_button.setFixedSize(70, 35) 
        self.play_button.clicked.connect(self.play_song)

        control_layout.addStretch(1) 
        control_layout.addWidget(self.play_button) 
        control_layout.addStretch(1)

        music_controls_layout.addLayout(control_layout)

        self.progress_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setStyleSheet("background-color: #1c1c1c;")
        self.progress_slider.sliderReleased.connect(self.seek_song)
        music_controls_layout.addWidget(self.progress_slider)

        self.progress_label = QtWidgets.QLabel("00:00 / 00:00", self)
        self.progress_label.setStyleSheet("color: white;")
        music_controls_layout.addWidget(self.progress_label)

        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("background-color: #1c1c1c;")
        self.volume_slider.valueChanged.connect(self.change_volume)
        music_controls_layout.addWidget(self.volume_slider)

        self.volume_label = QtWidgets.QLabel(f"Volume: {self.volume_slider.value()}%", self)
        self.volume_label.setStyleSheet("color: white;")
        music_controls_layout.addWidget(self.volume_label)
        
        self.library_list.itemClicked.connect(self.play_selected_song)

        main_layout.addLayout(music_controls_layout, 2, 0, 1, 2)
        
        self.setLayout(main_layout)

        if not os.path.exists('music'):
            os.makedirs('music')

        self.update_library()

        pygame.mixer.init()
        self.is_playing = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.current_song_length = 0
        self.current_position = 0
        pygame.mixer.music.set_volume(50)

    def search_songs(self):
        query = self.search_input.text()
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        request = youtube.search().list(q=query, part='snippet', type='video', maxResults=10)
        response = request.execute()

        self.results_list.clear()
        for item in response['items']:
            title = item['snippet']['title']
            video_id = item['id']['videoId']
            self.results_list.addItem(f"{title}  /  https://www.youtube.com/watch?v={video_id}")

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
            options = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'outtmpl': 'music/%(title)s.%(ext)s',
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
        for filename in os.listdir('music'):
            if filename.endswith('.mp3'):
                self.library_list.addItem(filename)

    def delete_song(self):
        selected_item = self.library_list.currentItem()
        if selected_item:
            song_name = selected_item.text()
            song_path = os.path.join('music', song_name)
            
            
            pygame.mixer.music.stop() 
            pygame.quit() 
            self.is_playing = False  

            if os.path.exists(song_path):
                os.remove(song_path)
                self.update_library()
                
    def play_selected_song(self):
        import pygame
        pygame.mixer.init()
        selected_item = self.library_list.currentItem()
        song_name = selected_item.text()
        song_path = os.path.join('music', song_name)
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

    def play_song(self):
        import pygame
        pygame.mixer.init()
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_button.setText("Play")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.play_button.setText("Stop")

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
