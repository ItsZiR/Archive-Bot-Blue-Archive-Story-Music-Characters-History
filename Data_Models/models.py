from dataclasses import dataclass
from datetime import datetime

#------------ 資料表欄位相關更新 ------------
@dataclass
class Music:
    file_path: str
    name: str
    key: str
    bpm: int
    duration: str
    composer: str
    type: str
    comment1: str
    comment2: str
    style: str
    genre: str
    song_type: str
    server: str
    released_day: str
    first_use: str
    mtime: float
    last_sync_time: str

@dataclass
class SoundTrack(Music):
    number: int

    def __str__(self):
        return f"🎵 `Track No. {self.number} : {self.name}. Key: {self.key}, BPM: {self.bpm}, 長度: {self.duration}, 作者: {self.composer},\n公布日期: {self.released_day},\nComment : {self.comment1}`\n-# {self.comment2}"
    
@dataclass
class Song(Music):

    def __str__(self):
        return f"🎵 `Track : {self.name}. Key: {self.key}, BPM: {self.bpm}, 長度: {self.duration}, 作者: {self.composer},\n公布日期: {self.released_day},\nComment : {self.comment1}`\n-# {self.comment2}"

@dataclass
class Student:
    id: int
    path_name: str
    name: str
    family_name: str
    personal_Name: str
    age: str
    grade: str
    school: str
    club: str
    height: str
    birthday: str
    hobbies: str
    profile: str
    rarity: int
    voice_actress: str
    illustrator: str
    designer: str

    isDefault: int
    size: str
    memorial_lobby_track: int
    released_day: str
    type: str
    unique_item: str

@dataclass
class Story:
    number: int
    story_title: str
    story_subtitle: str
    volume: str
    chapter: int
    part: str
    main_story_part: int
    story_type: str
    episodes: int
    released_day: str