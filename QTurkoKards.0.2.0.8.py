import os
import random
import sys
import pygame
import webbrowser
import configparser
from functools import partial
from PyQt5 import QtWidgets, QtGui, QtCore

class TarotApp(QtWidgets.QMainWindow):
    positions = [
        "Resolution", "Counterforce", "Force", "Outcome", "Hopes and Fears",
        "External Influences", "Self-Perception", "Immediate Future", "Past Influence",
        "Conscious Influences", "Subconscious Influences", "Challenges/Obstacles", "Present Situation"
    ]

    deck_folders = {
        'iNOVA': 'iNOVA', 'turkokards': 'turkokards', 'Rider_Waite': 'Rider_Waite',
        'playing_dark_extended': 'playing_dark_extended',
        'playing_dark': 'playing_dark', 'deviant_dark': 'deviant_dark',
    }

    CONFIG_FILE = ".tarot_config"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTurkoKards")
        self.resize(666, 45)
        self.current_deck = 'iNOVA'
        self.card_width = self.load_card_width()
        self.dark_mode = self.load_dark_mode()
        self.card_windows = []
        self.play_music = False
        self.music = None
        self.current_music_file = None
        self.music_files = ['background.flac', 'background_01.flac', 'background_02.flac']
        self.init_ui()
        self.select_music(self.music_files[0])

    def load_card_width(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.CONFIG_FILE):
            config.read(self.CONFIG_FILE)
            try:
                return config.getint('Settings', 'card_width', fallback=333)
            except Exception:
                return 333
        return 333

    def load_dark_mode(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.CONFIG_FILE):
            config.read(self.CONFIG_FILE)
            try:
                return config.getboolean('Settings', 'dark_mode', fallback=False)
            except Exception:
                return False
        return False

    def save_card_width(self, width):
        config = configparser.ConfigParser()
        if os.path.exists(self.CONFIG_FILE):
            config.read(self.CONFIG_FILE)
        if 'Settings' not in config:
            config['Settings'] = {}
        config['Settings']['card_width'] = str(width)
        with open(self.CONFIG_FILE, 'w') as f:
            config.write(f)

    def save_dark_mode(self, dark_mode):
        config = configparser.ConfigParser()
        if os.path.exists(self.CONFIG_FILE):
            config.read(self.CONFIG_FILE)
        if 'Settings' not in config:
            config['Settings'] = {}
        config['Settings']['dark_mode'] = str(dark_mode)
        with open(self.CONFIG_FILE, 'w') as f:
            config.write(f)

    def init_ui(self):
        self.setup_music()
        self.setup_menus()
        self.apply_theme()
        self.show()

    def setup_menus(self):
        # File menu
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction('Open Reading', self.open_reading_file)
        file_menu.addAction('Save Reading', self.save_reading)
        file_menu.addAction('Clear Log', self.clear_log)
        file_menu.addAction('Exit', QtWidgets.qApp.quit)

        # Main menu
        main_menu = self.menuBar().addMenu('Main')
        deck_submenu = main_menu.addMenu('Deck')
        for deck in ['iNOVA', 'turkokards', 'Rider_Waite', 'deviant_dark']:
            deck_submenu.addAction(deck, partial(self.select_deck, deck))
        playing_cards = deck_submenu.addMenu('Playing Cards')
        for deck in ['playing_dark', 'playing_dark_extended']:
            playing_cards.addAction(deck.replace('_', ' ').title(), partial(self.select_deck, deck))
        
        # Music menu
        music_menu = main_menu.addMenu('Music')
        music_menu.addAction('Toggle Music', self.toggle_music)
        for music_file in self.music_files:
            music_menu.addAction(music_file, partial(self.select_music, music_file))

        # Size menu
        size_menu = main_menu.addMenu('Size')
        for label, width in [('XS', 200), ('Small', 300), ('Medium', 400), ('Large', 500),
                             ('XL', 600), ('700', 700), ('XXL', 800), ('900', 900), ('XXX', 1000)]:
            size_menu.addAction(label, partial(self.set_card_size, width))

        main_menu.addAction('Clear', self.clear_card_windows)
        
        # Dark mode toggle
        main_menu.addSeparator()
        main_menu.addAction('Toggle Dark Mode', self.toggle_dark_mode)

        # Info menu
        info_menu = self.menuBar().addMenu('Info')
        info_menu.addAction('About', self.show_about_dialog)
        info_menu.addAction('Help', self.show_help_dialog)
        info_menu.addAction('Contact Me', self.show_contact_info)
        info_menu.addAction('Buy Cards', lambda: webbrowser.open('https://turkokards.com'))

    def setup_music(self):
        pygame.init()
        pygame.mixer.init()

    def select_music(self, music_file):
        if self.play_music:
            self.toggle_music()
        self.current_music_file = music_file
        music_path = os.path.join('music', music_file)
        self.music = pygame.mixer.Sound(music_path)
        if self.play_music:
            self.toggle_music()

    def toggle_music(self):
        self.play_music = not self.play_music
        if self.play_music and self.music:
            self.music.play(-1)
        elif self.music:
            self.music.stop()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.save_dark_mode(self.dark_mode)
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            # Dark mode styling
            dark_style = """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #363636;
                color: #ffffff;
                border-bottom: 1px solid #555555;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #0078d7;
            }
            QMenu {
                background-color: #363636;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item {
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #0078d7;
            }
            QLabel {
                color: #ffffff;
                background-color: #2b2b2b;
            }
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QMessageBox QPushButton:hover {
                background-color: #505050;
            }
            QFileDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            """
            self.setStyleSheet(dark_style)
        else:
            # Light mode (default)
            self.setStyleSheet("")
        
        # Update existing card windows with new theme
        for window in self.card_windows:
            if self.dark_mode:
                window.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                    background-color: #2b2b2b;
                }
                """)
            else:
                window.setStyleSheet("")

    def clear_log(self):
        log_file_path = os.path.join('logs', 'tarot_log.txt')
        try:
            if os.path.exists(log_file_path):
                os.remove(log_file_path)
                QtWidgets.QMessageBox.information(self, "Log Cleared", "Log file cleared successfully.")
            else:
                QtWidgets.QMessageBox.information(self, "Log Cleared", "Log file is already clear.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while clearing log: {str(e)}")

    def generate_tarot_reading(self):
        try:
            deck_folder = self.current_deck_folder()
            with open(os.path.join(deck_folder, 'cardslist.txt'), 'r') as f:
                tarot_cards = [card.strip() for card in f.readlines()]
            self.random_cards = random.sample(tarot_cards, 13)
            reversed_count = int(0.26 * 13)
            reversed_positions = set(random.sample(range(13), reversed_count))
            self.clear_card_windows()
            for i, position in enumerate(self.positions):
                card_name = self.random_cards[i]
                is_reversed = i in reversed_positions
                display_name = card_name + (" reversed" if is_reversed else "")
                self.show_card_window(position, display_name, is_reversed)
                self.write_to_log(position, display_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def show_card_window(self, position, card_name, is_reversed):
        card_window = QtWidgets.QWidget()
        card_window.setWindowTitle(position)
        card_window.setGeometry(100, 100, self.card_width, 400)
        layout = QtWidgets.QVBoxLayout(card_window)
        layout.addWidget(QtWidgets.QLabel(position))
        card_image = self.get_card_image(card_name)
        if card_image:
            label = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(card_image).scaledToWidth(self.card_width)
            label.setPixmap(pixmap)
            layout.addWidget(label)
            label.mousePressEvent = partial(self.show_card_definition, card_name)
        else:
            layout.addWidget(QtWidgets.QLabel(card_name))
        
        # Apply theme to card window
        if self.dark_mode:
            card_window.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background-color: #2b2b2b;
            }
            """)
        
        card_window.show()
        self.card_windows.append(card_window)

    def write_to_log(self, position, card_name):
        os.makedirs('logs', exist_ok=True)
        try:
            with open(os.path.join('logs', 'tarot_log.txt'), 'a') as log_file:
                log_file.write(f"{position}: {card_name}\n")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while writing to log: {str(e)}")

    def set_card_size(self, width):
        self.card_width = width
        self.save_card_width(width)
        self.clear_card_windows()
        try:
            with open(os.path.join('logs', 'tarot_log.txt'), 'r') as log_file:
                lines = log_file.readlines()[-13:]
            for line in lines:
                position, card_name = line.strip().split(': ')
                is_reversed = "reversed" in card_name
                self.show_card_window(position, card_name, is_reversed)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while loading reading: {str(e)}")

    def show_about_dialog(self):
        QtWidgets.QMessageBox.about(self, "About", "TurkoKards App\nVersion 0.2.0.8\n© 2017 - 2025 G. Robert Turcotte (Gary R. Tucotte)")

    def show_help_dialog(self):
        QtWidgets.QMessageBox.information(self, "Help", "WASSSUP? This is the help message. You can use this app to generate Tarot card readings and customize various settings.")

    def show_contact_info(self):
        QtWidgets.QMessageBox.information(
            self,
            "Contact Me",
            '<a href="mailto:gary@turkokards.com">gary@turkokards.com</a>'
        )

    def select_custom_deck(self, index):
        self.select_deck(f'custom_{index}')

    def get_card_image(self, card_name):
        try:
            deck_folder = self.current_deck_folder()
            image_folder = os.path.join(deck_folder, 'card_images')
            file_name = card_name.lower().replace(' ', '_') + '.jpg'
            file_path = os.path.join(image_folder, file_name)
            for _ in range(7):
                if os.path.exists(file_path):
                    return file_path
                QtCore.QThread.msleep(150)
            QtWidgets.QMessageBox.critical(self, "Error", f"Image not found: {card_name}")
            return None
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while loading image: {str(e)}")
            return None

    def show_card_definition(self, card_name, event=None):
        try:
            deck_folder = self.current_deck_folder()
            definition_file = os.path.join(deck_folder, 'card_definitions', card_name.lower().replace(' ', '_') + '.txt')
            if os.path.exists(definition_file):
                with open(definition_file, 'r') as f:
                    card_definition = f.read()
                QtWidgets.QMessageBox.information(self, card_name, card_definition)
            else:
                QtWidgets.QMessageBox.information(self, "Card Definition", "Definition not found.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while loading card definition: {str(e)}")

    def current_deck_folder(self):
        deck = self.current_deck
        if deck in self.deck_folders:
            return os.path.join('decks', self.deck_folders[deck])
        raise ValueError('Invalid deck selected')

    def select_deck(self, deck_name):
        self.current_deck = deck_name
        self.generate_tarot_reading()

    def save_reading(self):
        try:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Reading", "saves", "Text Files (*.txt)")
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(f"Deck: {self.current_deck}\n")
                with open(os.path.join('logs', 'tarot_log.txt'), 'r') as log_file:
                    lines = log_file.readlines()[-13:]
                with open(file_path, 'a') as file:
                    file.writelines(lines)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while saving reading: {str(e)}")

    def open_reading_file(self):
        try:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Reading", "saves", "Text Files (*.txt)")
            if file_path:
                with open(file_path, 'r') as file:
                    readings = file.readlines()
                deck_name = readings[0].strip().split(': ')[1]
                if deck_name != self.current_deck:
                    self.select_deck(deck_name)
                else:
                    self.clear_card_windows()
                with open(os.path.join('logs', 'tarot_log.txt'), 'a') as log_file:
                    log_file.writelines(readings[-13:])
                for line in readings[1:14]:
                    position, card_name = line.strip().split(': ')
                    is_reversed = "reversed" in card_name
                    self.show_card_window(position, card_name, is_reversed)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while opening reading: {str(e)}")

    def closeEvent(self, event):
        self.clear_card_windows()
        event.accept()

    def clear_card_windows(self):
        for window in getattr(self, 'card_windows', []):
            window.close()
        self.card_windows = []

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TarotApp()
    sys.exit(app.exec_())