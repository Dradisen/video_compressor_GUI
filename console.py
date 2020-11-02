"""Интерфейс командной строки."""

import argparse
import os
from core import compression


def get_options():
    parser = argparse.ArgumentParser(
        description='Утилита для сжатия видео',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-s', dest='source', type=str, help='исходный файл')
    parser.add_argument(
        '-i', dest='input', type=str,
        help='папка для сохранения результата; по умолчанию папка исходного файла')
    parser.add_argument(
        '-q', dest='quality', type=int,
        help='желаемое качество (высота); натуральное число в диапазоне 1-1080')
    parser.add_argument(
        '-f', dest='ffmpeg', type=str, help='путь к файлу ffmpeg.exe')
    options = parser.parse_args()
    return options.source, options.input, options.quality, options.ffmpeg


def validate_options(source_file, input_dir, quality, path_to_ffmpeg):
    if not source_file:
        return False, 'Ошибка: пропущен обязательный параметр sourse (-s).'
    if not os.path.isfile(source_file):
        return False, 'Ошибка: в параметре source (-s) указан не файл.'
    if not os.path.exists(source_file):
        return False, 'Ошибка: в параметре source (-s) указан несуществующий файл.'
    if input_dir and not os.path.exists(input_dir):
        return False, 'Ошибка: в параметре input (-i) указана несуществующая директория.'
    if not quality:
        return False, 'Ошибка: пропущен обязательный параметр quality (-q).'
    if quality <= 0 or quality > 1080:
        return False, 'Ошибка: параметр quality (-q) должен находиться в диапазоне 1-1080.'
    if path_to_ffmpeg and not os.path.exists(path_to_ffmpeg):
        return False, 'Ошибка: в параметре ffmpeg (-f) указан несуществующий файл.'
    return True, None


if __name__ == '__main__':
    source_file, input_dir, quality, path_to_ffmpeg = get_options()
    is_valid, error = validate_options(
        source_file, input_dir, quality, path_to_ffmpeg)
    if not is_valid:
        print(error)
    else:
        if not input_dir:
            input_dir = os.path.dirname(source_file)
        if not path_to_ffmpeg:
            default_path = r'ffmpeg-20181102-d6d407d-win64-static\ffmpeg-20181102-d6d407d-win64-static\bin\ffmpeg.exe'
            path_to_ffmpeg = os.path.join(os.path.dirname(__file__), default_path)
        source_name, expr = os.path.split(source_file)[-1].split('.')
        input_file = os.path.join(input_dir, '%s_%s.%s' % (source_name, quality, expr))
        print('Начался процесс сжатия.')
        compression(source_file, input_file, quality, path_to_ffmpeg)
        print('Процесс сжатия завершен.')
