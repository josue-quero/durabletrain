import math
from pydub import AudioSegment
class SplitWavAudioMubin():
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = filename
        self.output_folder = folder + '\\' + 'splitted'
        self.audio = AudioSegment.from_mp3(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        filepath = self.output_folder + '\\' + split_filename
        
        split_audio.export(filepath, format="wav")
        return filepath

    def multiple_split(self, min_per_split):
        files = []
        total_mins = math.ceil(self.get_duration() / 60)
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + self.filename
            files.append(self.single_split(i, i+min_per_split, split_fn))
            print(str(i) + ' Done')
            if i == total_mins - min_per_split:
                print('All splited successfully')
        return files