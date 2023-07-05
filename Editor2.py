from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QSlider, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import sys
import pyautogui

class VideoSubclipExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.original_clip = None
        self.clips = []
        self.dark_mode = False
        self.muted_clip = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Video Subclip Extractor")
        layout = QVBoxLayout()

        self.upload_button = QPushButton("Upload Original")
        self.upload_button.clicked.connect(self.upload_original)
        layout.addWidget(self.upload_button)

        self.start_label = QLabel("Start Time (in seconds): 0")
        layout.addWidget(self.start_label)
        self.start_slider = QSlider(Qt.Horizontal)
        self.start_slider.setRange(0, 0)
        self.start_slider.valueChanged.connect(self.update_start_label)
        self.start_slider.valueChanged.connect(self.update_end_slider_range)
        layout.addWidget(self.start_slider)

        self.end_label = QLabel("End Time (in seconds): 0")
        layout.addWidget(self.end_label)
        self.end_slider = QSlider(Qt.Horizontal)
        self.end_slider.setRange(0, 0)
        self.end_slider.valueChanged.connect(self.update_end_label)
        self.end_slider.valueChanged.connect(self.update_start_slider_range)
        layout.addWidget(self.end_slider)

        extract_button = QPushButton("Extract Subclip")
        extract_button.clicked.connect(self.extract_subclip)
        layout.addWidget(extract_button)

        mix_button = QPushButton("Mix Clips")
        mix_button.clicked.connect(self.upload_clips)
        layout.addWidget(mix_button)

        mute_button = QPushButton("Mute Video")
        mute_button.clicked.connect(self.toggle_mute)
        layout.addWidget(mute_button)

        mix_audio_button = QPushButton("Mix MP3 with MP4")
        mix_audio_button.clicked.connect(self.mix_audio_video)
        layout.addWidget(mix_audio_button)

        extract_audio_button = QPushButton("Extract Audio")
        extract_audio_button.clicked.connect(self.extract_audio)
        layout.addWidget(extract_audio_button)

        self.dark_mode_button = QPushButton("Dark Mode")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_button)

        self.setLayout(layout)

        self.setGeometry(100, 100, 400, 300)  # Set a larger size for the GUI window

    def upload_original(self):
        try:
            # Open file dialog to select the original video clip
            original_path, _ = QFileDialog.getOpenFileName(self, "Select Original Video")
            if original_path:
                # Load the original video clip
                self.original_clip = VideoFileClip(original_path)
                duration = int(self.original_clip.duration)
                self.start_slider.setRange(0, duration)
                self.end_slider.setRange(0, duration)
                self.update_start_label()
                self.update_end_label()

                # Set the default value of the end slider to the maximum value
                self.end_slider.setValue(duration)
        except Exception as e:
            self.show_error_message(str(e))

    def extract_audio(self):
        try:
            if not self.original_clip:
                return

            audio_path, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "Audio Files (*.mp3)")
            if audio_path:
                audio_clip = self.original_clip.audio
                audio_clip.write_audiofile(audio_path)
        except Exception as e:
            self.show_error_message(str(e))

    def extract_subclip(self):
        try:
            if not self.original_clip:
                return

            # Get the start and end times from the sliders
            start_time = self.start_slider.value()
            end_time = self.end_slider.value()

            # Extract the subclip
            subclip = self.original_clip.subclip(start_time, end_time)

            # Save the subclip to a file
            subclip_path, _ = QFileDialog.getSaveFileName(self, "Save Subclip", "", "Video Files (*.mp4)")
            if subclip_path:
                subclip.write_videofile(subclip_path)
        except Exception as e:
            self.show_error_message(str(e))

    def upload_clips(self):
        try:
            if not self.original_clip:
                return

            clips_paths, _ = QFileDialog.getOpenFileNames(self, "Select Video Clips")
            if clips_paths:
                self.clips = []

                for path in clips_paths:
                    clip = VideoFileClip(path)
                    self.clips.append(clip)

                final_clip = concatenate_videoclips([self.original_clip] + self.clips)

                final_clip_path, _ = QFileDialog.getSaveFileName(self, "Save Final Clip", "", "Video Files (*.mp4)")
                if final_clip_path:
                    final_clip.resize(width=480).write_videofile(final_clip_path)
        except Exception as e:
            self.show_error_message(str(e))

    def toggle_mute(self):
        try:
            if self.original_clip:
                choice = QMessageBox.question(self, "Mute Video",
                                              "Do you want to save the muted clip or keep it temporarily?",
                                              QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel)
                if choice == QMessageBox.Save:
                    self.original_clip = self.original_clip.set_audio(None)
                elif choice == QMessageBox.No:
                    if not self.muted_clip:
                        self.muted_clip = self.original_clip.copy()
                    else:
                        self.original_clip = self.muted_clip.copy()
                elif choice == QMessageBox.Cancel:
                    return
        except Exception as e:
            self.show_error_message(str(e))

    def mix_audio_video(self):
        try:
            if not self.original_clip:
                return

            audio_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File")
            if audio_path:
                audio_clip = AudioFileClip(audio_path)

                final_clip = self.original_clip.set_audio(audio_clip)

                final_clip_path, _ = QFileDialog.getSaveFileName(self, "Save Mixed Clip", "", "Video Files (*.mp4)")
                if final_clip_path:
                    final_clip.write_videofile(final_clip_path)
        except Exception as e:
            self.show_error_message(str(e))

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.set_style_sheet()

    def set_style_sheet(self):
        if self.dark_mode:
            style_sheet = """
                QWidget {
                    background-color: #333333;
                    color: #ffffff;
                }

                QPushButton {
                    background-color: #666666;
                    color: #ffffff;
                }

                QLabel {
                    color: #ffffff;
                }
            """
        else:
            style_sheet = ""

        self.setStyleSheet(style_sheet)

    def update_start_label(self):
        value = self.start_slider.value()
        self.start_label.setText(f"Start Time (in seconds): {value}")

    def update_end_label(self):
        value = self.end_slider.value()
        self.end_label.setText(f"End Time (in seconds): {value}")

    def update_end_slider_range(self):
        start_time = self.start_slider.value()
        self.end_slider.setRange(start_time, self.end_slider.maximum())

    def update_start_slider_range(self):
        end_time = self.end_slider.value()
        self.start_slider.setRange(0, end_time)

    def show_error_message(self, message):
        pyautogui.alert(text=message, title="Error")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoSubclipExtractor()
    window.set_style_sheet()
    window.show()
    sys.exit(app.exec_())
