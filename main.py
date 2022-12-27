import sqlite3
import sys
import time
import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QLabel
from PyQt5.uic import loadUi


def gotoshow():
    showing = showData()
    widget.addWidget(showing)
    widget.setCurrentIndex(widget.currentIndex() + 1)


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.loginbutton.clicked.connect(self.loginfunction)
        self.loginbuttonseri.clicked.connect(self.start_timer)
        self.showdatabutton.clicked.connect(gotoshow)
        self.setFixedSize(1463, 900)
        self.label = self.findChild(QLabel, 'resimlabel')  # UI dosyasındaki label'ı bul
        pixmap = QPixmap('yt.png')
        self.label.setPixmap(pixmap)

    def start_timer(self):
        timef = self.freqline.text()
        timef = int(timef)
        timef = timef * 86400000
        self.timer = QTimer()
        self.timer.timeout.connect(self.loginfunctionseri)
        self.timer.setInterval(timef)  # 6000 ms = 6 saniye
        self.timer.start()
        self.run_count = 1

    def loginfunctionseri(self):
        frequency = self.freqline_2.text()
        frequency = int(frequency)

        if self.run_count == (frequency + 1):
            self.timer.stop()
        else:
            channel_name_input = self.channellnameline.text()
            api_key = self.apikeyline.text()

            url = "https://www.googleapis.com/youtube/v3/search"

            parameters = {
                "part": "snippet",
                "q": channel_name_input,
                "key": api_key,
                "type": "channel",
                "maxResults": 1,  # Only need one result
                "order": "videoCount"
            }

            try:
                # Send GET request to YouTube API and get response
                channel_resp = requests.get(url, params=parameters)

                # Get channel ID from response
                channel_id = channel_resp.json()["items"][0]["id"]["channelId"]

            except (KeyError, IndexError):
                from PyQt5.QtWidgets import QMessageBox

                error_message = QMessageBox()
                error_message.setIcon(QMessageBox.Warning)
                error_message.setText("Incorrect entry made. Please try again.")
                error_message.setWindowTitle("ERROR!")
                error_message.setStandardButtons(QMessageBox.Ok)
                error_message.exec_()
                self.channellnameline.setText("")
                self.apikeyline.setText("")
                return

            # Now that we have the channel ID, we can use it to get the videos
            videos_url = "https://www.googleapis.com/youtube/v3/search"
            videos_params = {
                "part": "id,snippet",  # We want the video IDs and basic information
                "channelId": channel_id,
                "key": api_key,
                "type": "video",
                "order": "date",  # Get the most recent videos first
                "maxResults": 50  # Get up to 50 videos
            }
            videos_resp = requests.get(videos_url, params=videos_params)
            videos = videos_resp.json()["items"]

            video_ids = []
            durations = []
            publish_dates = []
            titles = []
            video_views = []
            likes = []
            favs = []
            descs = []

            # Make a single API request to get all the video information
            video_info_url = "https://www.googleapis.com/youtube/v3/videos"
            video_ids_string = ",".join(video["id"]["videoId"] for video in videos)
            video_info_params = {
                "part": "id,snippet,contentDetails,statistics",
                "id": video_ids_string,
                "key": api_key
            }
            video_info_resp = requests.get(video_info_url, params=video_info_params)
            video_info = video_info_resp.json()["items"]

            for info in video_info:
                video_id = info["id"]
                video_ids.append(video_id)

                duration = info["contentDetails"]["duration"]
                durations.append(duration)

                publish_date = info["snippet"]["publishedAt"]
                publish_dates.append(publish_date)

                title = info["snippet"]["title"]
                titles.append(title)

                stats = info["statistics"]
                video_views.append(stats["viewCount"])
                likes.append(stats["likeCount"])
                favs.append(stats["favoriteCount"])

                desc = info["snippet"]["description"]
                descs.append(desc)

            # Now we have all the information for each video in separate lists
            #            print(f"Video IDs: {len(video_ids)}")
            #            print(f"Durations: {len(durations)}")
            #            print(f"Publish dates: {len(publish_dates)}")
            #            print(f"Titles: {len(titles)}")
            #            print(f"Views: {len(video_views)}")
            #            print(f"Likes: {len(likes)}")
            #            print(f"Favorites: {len(favs)}")
            #            print(f"Descriptions: {len(descs)}")
            #
            import sqlite3
            sqlinpt = self.databasenameline.text() + ".db"
            # Connect to the database
            conn = sqlite3.connect(sqlinpt)

            # Create a cursor
            cursor = conn.cursor()

            from datetime import datetime
            now = datetime.now()
            a = self.run_count
            a = str(a)
            formatted_date = now.strftime("x%Yx%mx%d" + "X" + a)

            cursor.execute(
                f'CREATE TABLE IF NOT EXISTS {formatted_date}'
                f' (id INTEGER PRIMARY KEY, video_id TEXT,duration TEXT, publish_date TEXT, '
                f'title TEXT, video_views INTEGER, likes INTEGER,favs INTEGER, desc TEXT)')
            # Loop through the list of videos and insert the data into the table

            for i in range(len(video_ids)):
                cursor.execute(
                    f'INSERT INTO {formatted_date} (video_id , duration , publish_date, title, video_views, likes,favs, desc) VALUES(?,?,?,?,?,?,?,?)',
                    (video_ids[i], durations[i], publish_dates[i], titles[i], video_views[i], likes[i], favs[i],
                     descs[i]))
                time.sleep(0.01)

            # Commit the changes
            conn.commit()

            # Close the connection
            conn.close()
        self.run_count += 1

    def loginfunction(self):
        channel_name_input = self.channellnameline.text()
        api_key = self.apikeyline.text()

        url = "https://www.googleapis.com/youtube/v3/search"

        parameters = {
            "part": "snippet",
            "q": channel_name_input,
            "key": api_key,
            "type": "channel",
            "maxResults": 1,  # Only need one result
            "order": "videoCount"
        }

        try:
            # Send GET request to YouTube API and get response
            channel_resp = requests.get(url, params=parameters)

            # Get channel ID from response
            channel_id = channel_resp.json()["items"][0]["id"]["channelId"]

        except (KeyError, IndexError):
            from PyQt5.QtWidgets import QMessageBox

            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Warning)
            error_message.setText("Incorrect entry made.")
            error_message.setWindowTitle("ERROR!")
            error_message.setStandardButtons(QMessageBox.Ok)
            error_message.exec_()
            self.channellnameline.setText("")
            self.apikeyline.setText("")
            return

        # Now that we have the channel ID, we can use it to get the videos
        videos_url = "https://www.googleapis.com/youtube/v3/search"
        videos_params = {
            "part": "id,snippet",  # We want the video IDs and basic information
            "channelId": channel_id,
            "key": api_key,
            "type": "video",
            "order": "date",  # Get the most recent videos first
            "maxResults": 50  # Get up to 50 videos
        }
        videos_resp = requests.get(videos_url, params=videos_params)
        videos = videos_resp.json()["items"]

        video_ids = []
        durations = []
        publish_dates = []
        titles = []
        video_views = []
        likes = []
        favs = []
        descs = []

        # Make a single API request to get all the video information
        video_info_url = "https://www.googleapis.com/youtube/v3/videos"
        video_ids_string = ",".join(video["id"]["videoId"] for video in videos)
        video_info_params = {
            "part": "id,snippet,contentDetails,statistics",
            "id": video_ids_string,
            "key": api_key
        }
        video_info_resp = requests.get(video_info_url, params=video_info_params)
        video_info = video_info_resp.json()["items"]

        for info in video_info:
            video_id = info["id"]
            video_ids.append(video_id)

            duration = info["contentDetails"]["duration"]
            durations.append(duration)

            publish_date = info["snippet"]["publishedAt"]
            publish_dates.append(publish_date)

            title = info["snippet"]["title"]
            titles.append(title)

            stats = info["statistics"]
            video_views.append(stats["viewCount"])
            likes.append(stats["likeCount"])
            favs.append(stats["favoriteCount"])

            desc = info["snippet"]["description"]
            descs.append(desc)

        # Now we have all the information for each video in separate lists
        #      print(f"Video IDs: {len(video_ids)}")
        #     print(f"Durations: {len(durations)}")
        #    print(f"Publish dates: {len(publish_dates)}")
        #   print(f"Titles: {len(titles)}")
        #   print(f"Views: {len(video_views)}")
        #   print(f"Likes: {len(likes)}")
        #    print(f"Favorites: {len(favs)}")
        #   print(f"Descriptions: {len(descs)}")

        def sqlaktarma():
            try:
                sqlinpt = self.databasenameline.text() + ".db"
                # Connect to the database
                conn = sqlite3.connect(sqlinpt)

                # Create a cursor
                cursor = conn.cursor()

                from datetime import datetime
                now = datetime.now()
                formatted_date = now.strftime("x%Yx%mx%d")

                cursor.execute(
                    f'CREATE TABLE IF NOT EXISTS {formatted_date} (id INTEGER PRIMARY KEY, video_id TEXT,duration TEXT, publish_date TEXT, '
                    f'title TEXT, video_views INTEGER, likes INTEGER,favs INTEGER, desc TEXT)')
                # Loop through the list of videos and insert the data into the table

                for i in range(len(video_ids)):
                    cursor.execute(
                        f'INSERT INTO {formatted_date} (video_id , duration , publish_date, title, video_views, likes,favs, desc) VALUES(?,?,?,?,?,?,?,?)',
                        (video_ids[i], durations[i], publish_dates[i], titles[i], video_views[i], likes[i], favs[i],
                         descs[i]))
                    time.sleep(0.01)
                conn.commit()
                conn.close()

                # Show success message
                from PyQt5.QtWidgets import QMessageBox

                success_message = QMessageBox()
                success_message.setIcon(QMessageBox.Information)
                success_message.setText("Data has been successfully saved to the database.")
                success_message.setWindowTitle("SUCCES")
                success_message.setStandardButtons(QMessageBox.Ok)
                success_message.exec_()

            except sqlite3.OperationalError:
                # If there is an error, show error message and clear
                from PyQt5.QtWidgets import QMessageBox

                error_message = QMessageBox()
                error_message.setIcon(QMessageBox.Warning)
                error_message.setText("The database name is incorrect. Please try again.")
                error_message.setWindowTitle("ERROR")
                error_message.setStandardButtons(QMessageBox.Ok)
                error_message.exec_()

                # Clear database name input field
                self.databaseinputline.setText("")
                return

        sqlaktarma()


class showData(QDialog):
    def __init__(self):
        super(showData, self).__init__()
        loadUi("datashow.ui", self)
        self.databasenameline = self.findChild(QtWidgets.QLineEdit, "databasenameline")
        self.okbutton = self.findChild(QtWidgets.QPushButton, "okbutton")
        self.tablewidget = self.findChild(QtWidgets.QTableWidget, "tablewidget")
        self.retturnbutton = self.findChild(QtWidgets.QPushButton, "retturnbutton")
        self.retturnbutton.clicked.connect(self.returnfunction)
        self.okbutton.clicked.connect(self.load_data)

    def returnfunction(self):

        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def load_data(self):
        try:
            # Veritabanı adını ayarlayın
            database_name = self.databasenameline.text() + ".db"

            # Veritabanı bağlantısını oluşturun
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()

            from datetime import datetime

            now = datetime.now()
            formatted_date = now.strftime("x%Yx%mx%d")

            # Verileri çekin
            cursor.execute("SELECT * FROM {}".format(formatted_date))
            rows = cursor.fetchall()

            # Tabloyu temizleyin ve sütunları ayarlayın
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(len(rows[0]))
            self.tableWidget.setHorizontalHeaderLabels(
                ["id", "video_id", "duration", "publish_date", "Title", "video_views", "likes", "favs", "description"])

            # Verileri tablo içine ekleyin
            for row_index, row_data in enumerate(rows):
                self.tableWidget.insertRow(row_index)
                for col_index, col_data in enumerate(row_data):
                    self.tableWidget.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(col_data)))

            # Veritabanı bağlantısını kapatın
            cursor.close()
            conn.close()
            from PyQt5.QtWidgets import QMessageBox

            success_message = QMessageBox()
            success_message.setIcon(QMessageBox.Information)
            success_message.setText("The request was successfully fulfilled.")
            success_message.setWindowTitle("SUCCES")
            success_message.setStandardButtons(QMessageBox.Ok)
            success_message.exec_()
        except sqlite3.OperationalError:
            from PyQt5.QtWidgets import QMessageBox
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Warning)
            error_message.setText("The database name was entered incorrectly. Please try again.")
            error_message.setWindowTitle("ERROR")
            error_message.exec_()
            self.databasenameline.clear()


app = QApplication(sys.argv)
mainwindow = Login()

widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)

widget.show()
app.exec_()
