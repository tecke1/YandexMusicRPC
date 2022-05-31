import logging
import time
import os

from pypresence import Presence
from yandex_music import Client
from configparser import ConfigParser

logger = logging.getLogger(__name__)

config = ConfigParser()

class User:
    def __init__(self, client):
        self.client = client

    @property
    def get_track(self): # Получение информации о треке
        try:
            queues = self.client.queues_list()
            last_queue = self.client.queue(queues[0].id)
            track_id = last_queue.get_current_track()
            track = track_id.fetch_track()
            return track
        except Exception:
            None

    @property
    def get_image(self): # Получение ссылки на обложку
        try:
            return self.get_track['og_image'][:-2] + '100x100'
        except Exception:
            return None 

    @property
    def get_label(self): # Получение название трека
        try:
            return self.get_track.title
        except Exception:
            return None
    
    @property
    def get_artist(self): # Получение исполнителей трека
        try:
            return ', '.join(self.get_track.artists_name())
        except Exception:
            return None

    @property
    def get_link(self):
        try:
            track = self.get_track
            return f"https://music.yandex.ru/album/{track['albums'][0]['id']}/track/{track['id']}/"
        except Exception:
            return 'https://music.yandex.ru/'

def loop(user: Client, discord: Presence):
    while True:
        try:
            os.system('cls')
        except Exception:
            os.system('clear')

        if user.get_label is None:
            logger.info('♫ Ничего не играет...')
            print("*'Мой вайб' на данный момент не поддерживается")
        else:
            logger.info(f'♫ {user.get_artist} - {user.get_label}')
        
        discord.update(
            details=user.get_label,
            state=user.get_artist,
            large_image='icon',
            large_text='Яндекс.Музыка',
            buttons=[{'label': 'Слушать', 'url': user.get_link}]
            )
        
        time.sleep(15)

def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='[YandexMusicRPC] - %(message)s')

    # Настройка конфига
    if not os.path.exists('config.ini'):
        with open('config.ini', 'w+', encoding='utf-8') as f:
            logger.info('Необходимо ввести токен!')
            token = input('=> ')
            example = [
                '[config]\n',
               f'YTOKEN = {token}\n',
                'CLIENT_ID = 981235164988465223']
            for element in example:
                f.write(element)
    try:
        config.read('config.ini')
    except Exception:
        logger.error('Не удалось прочитать файл конфигурации!')
        exit()

    # Объявление переменных
    try:
        yclient = User(Client(config.get('config', 'YTOKEN')).init())
        logger.error('Успешная инициализация API')
    except Exception:
        logger.info('Не удалось подключится к API!')
    try:
        rpc = Presence(config.get('config', 'CLIENT_ID'))
        rpc.connect()
        logger.error('Успешная инициализация Discord')
    except Exception:
        logger.error('Не удалось подключится к Discord!')
    
    time.sleep(1)
    
    # Запуск цикла
    loop(yclient, rpc)


if __name__ == '__main__':
    main()