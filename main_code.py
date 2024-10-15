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
        self.setGeometry(100, 100, 700, 500)

        self.setStyleSheet("background-color: black;")

        title_label = QtWidgets.QLabel("MÛSİKİ", self)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(title_label)
        
        self.setWindowIcon(QtGui.QIcon('icon.ico'))

        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit(self)
        self.search_input.setPlaceholderText("Search for song...")
        self.search_input.setStyleSheet("background-color: #1c1c1c; color: white; border: 1px solid #494949;")  
        search_layout.addWidget(self.search_input)

        self.search_button = QtWidgets.QPushButton("Search", self)
        self.search_button.setStyleSheet("background-color: #1c1c1c; color: white;") 
        self.search_button.clicked.connect(self.search_songs)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        self.results_list = QtWidgets.QListWidget(self)
        self.results_list.setStyleSheet("background-color: #1c1c1c; color: white;")  
        self.layout.addWidget(self.results_list)

        self.add_button = QtWidgets.QPushButton("Add", self)
        self.add_button.setStyleSheet("background-color: #1c1c1c; color: white;")  #
        self.add_button.clicked.connect(self.add_song)
        self.layout.addWidget(self.add_button)

        self.library_list = QtWidgets.QListWidget(self)
        self.library_list.setStyleSheet("background-color: #1c1c1c; color: white;") 
        self.layout.addWidget(self.library_list)

        control_layout = QtWidgets.QHBoxLayout()
        self.play_button = QtWidgets.QPushButton("Play", self)
        self.play_button.setStyleSheet("background-color: #1c1c1c; color: white;")  
        self.play_button.clicked.connect(self.play_song)
        control_layout.addWidget(self.play_button)

        self.stop_button = QtWidgets.QPushButton("Stop", self)
        self.stop_button.setStyleSheet("background-color: #1c1c1c; color: white;") 
        self.stop_button.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.stop_button)

        self.delete_button = QtWidgets.QPushButton("Delete", self)
        self.delete_button.setStyleSheet("background-color: #1c1c1c; color: white;")  
        self.delete_button.clicked.connect(self.delete_song)
        self.layout.addWidget(self.delete_button)

        self.layout.addLayout(control_layout)

        self.progress_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.progress_slider.setRange(0, 100)  
        self.progress_slider.setStyleSheet("background-color: #1c1c1c; color: white;")
        self.progress_slider.sliderReleased.connect(self.seek_song)  
        self.layout.addWidget(self.progress_slider)

        self.progress_label = QtWidgets.QLabel("00:00 / 00:00", self)
        self.progress_label.setStyleSheet("color: white;")  
        self.layout.addWidget(self.progress_label)


        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)  
        self.volume_slider.setValue(50) 
        self.volume_slider.setStyleSheet("background-color: #1c1c1c; color: white;") 
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.layout.addWidget(self.volume_slider)

        self.volume_label = QtWidgets.QLabel("Volume: 50%", self)
        self.volume_label.setStyleSheet("color: white;")
        self.layout.addWidget(self.volume_label)

        self.setLayout(self.layout)

        if not os.path.exists('music'):
            os.makedirs('music')

        self.update_library()

        pygame.mixer.init()
        self.is_playing = False  #
        self.timer = QtCore.QTimer(self) 
        self.timer.timeout.connect(self.update_progress)
        self.current_song_length = 0 
        self.current_position = 0  

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
            if os.path.exists(song_path):
                os.remove(song_path)
                self.update_library() 

    def play_song(self):
        selected_item = self.library_list.currentItem()
        if selected_item:
            song_name = selected_item.text()
            song_path = os.path.join('music', song_name)
            if os.path.exists(song_path):
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.is_playing = True
                self.current_song_length = self.get_song_length(song_path)  
                self.update_progress_label(0)  
                self.progress_slider.setRange(0, int(self.current_song_length)) 
                self.progress_slider.setEnabled(True) 
                self.stop_button.setText("Stop")  
                self.timer.start(1000) 
                self.current_position = 0  

    def get_song_length(self, song_path):
        sound = pygame.mixer.Sound(song_path)  
        return sound.get_length()

    def toggle_playback(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.stop_button.setText("Continue")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.stop_button.setText("Stop")

    def update_progress(self):
        if self.is_playing:
            self.current_position += 1
            self.progress_slider.setValue(self.current_position)
            self.update_progress_label(self.current_position)
            if self.current_position >= self.current_song_length:
                self.timer.stop() 

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
        seek_time = self.progress_slider.value()
        pygame.mixer.music.play(start=seek_time)
        self.current_position = seek_time
        self.update_progress_label(seek_time)

    def change_volume(self):
        volume = self.volume_slider.value() / 100  
        pygame.mixer.music.set_volume(volume)
        self.volume_label.setText(f"Volume: {self.volume_slider.value()}%")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MusikiApp()
    window.show()
    sys.exit(app.exec_())