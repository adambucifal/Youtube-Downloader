# to install pytube go to command prompt and type "pip install pytube"
# Docs https://pytube.io/en/latest/
# Download ffmpeg - https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z
# Instruction for installing ffmpeg - https://phoenixnap.com/kb/ffmpeg-windows

import os
import tkinter as tk
from tkinter import filedialog

try:
    import ffmpeg
except ModuleNotFoundError:
    print(
        "ffmpeg not found, please install ffmpeg into your environment\n"
        "Download ffmpeg - https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z\n"
        "Instruction for installing ffmpeg - https://phoenixnap.com/kb/ffmpeg-windows"
    )
try:
    from pytube import YouTube, Playlist
    import pytube as pt
except ModuleNotFoundError:
    print("pytube not found, please install pytube (pip install pytube)")

class YoutubeDownloader:
    def __init__(self):
        # UI Info
        self.ui_font = "Arial"
        self.user_interface()

    def user_interface(self):
        # Main window
        window_root = tk.Tk()
        window_root.title("Adam's Youtube Downloader")

        title_label = tk.Label(
            window_root, text="Enter a YouTube link: "
            "\n(starting with 'https://www.youtube.com/watch'"
            "\nor 'https://www.youtube.com/playlist')", font=(self.ui_font, 9)
        )
        title_label.grid(row=0, column=0, padx=10, pady=5, columnspan=2)
        # Enter a youtube link field
        self.check_youtube_link = tk.StringVar()  # self.check_youtube_link.get()
        youtube_link_textbox = tk.Entry(
            window_root,
            font=(self.ui_font, 9),
            textvariable=self.check_youtube_link,
            width=60,
            bd=3,
        )
        youtube_link_textbox.grid(row=1, column=0, padx=10, pady=5, columnspan=2)
        # Choose directory to save files to
        self.check_download_directory_textbox = tk.StringVar()
        download_directory_textbox = tk.Entry(
            window_root,
            font=(self.ui_font, 9),
            textvariable=self.check_download_directory_textbox,
            width=40,
            bd=3,
            state="readonly",
        )
        download_directory_textbox.grid(
            row=2, column=0, columnspan=1, padx=5, pady=5
        )
        browse_directory_button = tk.Button(
            window_root, text="Browse", command=self.browse_directory
        )
        browse_directory_button.grid(
            row=2, column=1, padx=5, pady=5, sticky=tk.E + tk.W
        )
        # Enable only audio download
        self.check_audio_only = tk.IntVar()
        audio_only_checkbox = tk.Checkbutton(
            window_root,
            text="Export Audio Only",
            font=(self.ui_font, 9),
            variable=self.check_audio_only,
        )
        audio_only_checkbox.grid(row=3, column=0)
        # Choose an audio format for audio only downloads
        self.audio_format_selected_option = tk.StringVar()
        audio_format_list = ["mp3", "wav", "flac"]
        self.audio_format_selected_option.set(audio_format_list[0])
        audio_format_option = tk.OptionMenu(
            window_root, self.audio_format_selected_option, *audio_format_list
        )
        audio_format_option.grid(row=3, column=1, sticky=tk.E + tk.W, columnspan=1)

        # Limit video quality sections
        self.limit_video_output_selected_option = tk.StringVar()
        limit_video_output_list = ["4K", "1080p"]
        self.limit_video_output_selected_option.set(limit_video_output_list[0])
        limit_video_output_option = tk.OptionMenu(
            window_root,
            self.limit_video_output_selected_option,
            *limit_video_output_list,
        )
        limit_video_output_option.grid(row=4, column=0, columnspan=4, pady=10)

        download_button = tk.Button(
            window_root,
            text="Download",
            font=(self.ui_font, 15),
            command=self.run_downloads,
        )
        download_button.grid(row=5, column=0, columnspan=4, pady=10)

        # Show main window
        window_root.mainloop()

    def browse_directory(self):
        """
        Pops open a file dialog and gets the selected directory.
        """
        selected_directory = filedialog.askdirectory()
        self.check_download_directory_textbox.set(selected_directory)

    def download_video(self, url, directory, download_audio_only=False, audio_format="mp3"):
        """
        Downloads video as mp4 or mp3.
        :param url: string, link to the video (Should be copied from the search
            bar at the top of your browser)
        :param directory: string, directory to download the file to
        :param download_audio_only: bool, downloads a mp3 if True
        :param audio_format: string, format to download the audio if download_audio_only
        :return video_title: string, title of the video
        """
        # Defines video information and printing status update
        youtube_object = YouTube(url)
        video_title = youtube_object.title
        print(f"Starting download for {video_title}")

        # Runs this section if the user only wants to download the audio
        if download_audio_only:
            audio_stream = youtube_object.streams.get_audio_only()
            audio_stream.download(output_path=directory)
            # Converts audio file into specified format
            try:
                file_name = audio_stream.default_filename
                source = f"{directory}\\{file_name}"

                # Gets rid of any white space in the file name
                file_name = self.underscore_file(
                    file=file_name, source=source
                )

                # Strips away the extension of the file
                stripped_file = os.path.splitext(file_name)[0]
                os.system(f"ffmpeg -i {file_name} {stripped_file}.{audio_format}")
                os.remove(file_name)
            except:
                pass

            print(
                f"Successfully downloaded the audio from {video_title} to {directory}"
            )
            return video_title

        # Downloads video separately from audio to maximize quality
        # Creates 4K and HD variables
        video_stream_4k = youtube_object.streams.filter(
            res="2160p", file_extension=None
        ).first()
        video_stream_hd = youtube_object.streams.filter(
            res="1080p", file_extension=None
        ).first()
        # Runs checks to determine the highest quality available to download
        if video_stream_4k or video_stream_hd:
            if video_stream_4k:
                if self.limit_video_output_selected_option.get() == "4K":
                    self.get_audio_and_video(
                        directory=directory, stream=video_stream_4k, object=youtube_object
                    )
                    print(f"Successfully downloaded '{video_title}' in 4K to {directory}")
            if video_stream_hd:
                if self.limit_video_output_selected_option.get() == "1080p":
                    self.get_audio_and_video(
                        directory=directory, stream=video_stream_hd, object=youtube_object
                    )
                    print(f"Successfully downloaded '{video_title}' in HD to {directory}")
        else:
            youtube_object.streams.get_highest_resolution().download(output_path=directory)
            print(
                f"Couldn't find a 4K or HD version, downloaded '{video_title}' to {directory}"
            )

        return video_title

    def underscore_file(self, file, source):
        """
        Underscores a file and returns the name
        :param file: string name of the file
        :param source: string name of the source
        :return source: string new name of the source
        """
        if " " in file:
            os.rename(source, source.replace(" ", "_"))
            return source.replace(" ", "_")
        else:
            return source
    def get_audio_and_video(self, directory, stream, object):
        """
        Downloads the audio and video as separate files so the quality
            is as high as possible and then combines them.
        :param directory: string, directory to download the video to
        :param stream: YouTube object stream of the video
        """
        # Downloads video file
        old_video_file_path = os.path.normpath(
            os.path.join(directory, stream.default_filename)
        )
        stream.download(output_path=directory)

        video_file_path = os.path.normpath(
            os.path.join(directory, f"temp_video_{stream.default_filename}")
        )
        os.rename(old_video_file_path, video_file_path)

        # Downloads audio file
        video_audio_stream = object.streams.get_audio_only()
        old_video_audio_file_path = os.path.normpath(
            os.path.join(directory, video_audio_stream.default_filename)
        )
        video_audio_stream.download(output_path=directory)

        video_audio_file_path = os.path.normpath(
            os.path.join(directory, f"temp_audio_{stream.default_filename}")
        )
        os.rename(old_video_audio_file_path, video_audio_file_path)

        output_video_path = os.path.normpath(
            os.path.join(directory, stream.default_filename)
        )
        # Defines input variables for the ffmpeg function
        audio_input = ffmpeg.input(video_audio_file_path)
        video_input = ffmpeg.input(video_file_path)

        # Combines the audio and video files into a single mp4
        ffmpeg.output(
            audio_input,
            video_input,
            output_video_path
        ).overwrite_output().run(quiet=True)
        # Removes extra files
        os.remove(video_audio_file_path)
        os.remove(video_file_path)

    def batch_download(
            self,
            playlist,
            download_directory,
            download_audio_only=False,
            audio_format="mp3",
    ):
        """
        Takes a playlist link and downloads each video within the playlist.
        :param playlist: string, playlist link (Should be copied from the
            search bar at the top of your browser)
        :param download_directory: string, directory to download the videos to
        :param download_audio_only: bool, downloads only audio if True
        :param audio_format: string, audio format to download if download_audio_only
        """
        youtube_playlist_object = Playlist(playlist)
        playlist_video_urls = youtube_playlist_object.video_urls

        downloaded_videos = [
            self.download_video(
                url=video_url,
                directory=download_directory,
                download_audio_only=download_audio_only,
                audio_format=audio_format,
            )
            for index, video_url in enumerate(playlist_video_urls)
        ]

        print(
            f"Exported {len(downloaded_videos)}/{len(playlist_video_urls)} "
            f"videos from {youtube_playlist_object.title}"
        )

    def run_downloads(self):
        """
        Function that runs when the button is clicked on the UI.
            Identifies the type of link as a video or playlist and
        runs the appropriate function.
        """
        link = self.check_youtube_link.get()
        directory = self.check_download_directory_textbox.get()

        if not os.path.isdir(directory):
            print("Invalid directory")
            return

        audio_only = self.check_audio_only.get()
        audio_format = self.audio_format_selected_option.get()

        if "https://www.youtube.com/playlist" in link:
            self.batch_download(
                playlist=link,
                download_directory=directory,
                download_audio_only=audio_only,
                audio_format=audio_format,
            )

        elif "https://www.youtube.com/watch" in link:
            self.download_video(
                url=link,
                directory=directory,
                download_audio_only=audio_only,
                audio_format=audio_format,
            )
        else:
            print("Invalid link, please provide a YouTube link to a playlist or video")

if __name__ == "__main__":
    ytDownload = YoutubeDownloader()