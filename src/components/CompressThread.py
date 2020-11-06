from PyQt5.QtCore import QThread, pyqtSignal
import subprocess, re, os, signal


class CompressThread(QThread):
    progress = pyqtSignal(int, int, name='progress')
    end_progress = pyqtSignal(int, name='end')
    error = pyqtSignal(name='error')

    DIRNAME = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    RE_DURATION = re.compile(
        r"Duration: (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})")
    RE_TIME = re.compile(
        r"out_time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})")

    def __init__(self, queue, parent=None, **kwargs):
        QThread.__init__(self, parent)
        self.queue = queue
        self.output = kwargs['output']
        self.bitrate = kwargs['bitrate']
        self.quality = kwargs['quality']
        self.container = kwargs['codec']['container']

    # TODO: переделать позже
    def run(self):
        while True:
            task = self.queue.get()
            out_filename = self.__format_filename_output(
                task['filename'], self.quality, self.container)
            for result in self.__ffmpeg_run_generator([self.DIRNAME+'/bin/ffmpeg',
                '-i', task['filename'],
                '-vf', 'scale=-2:{}'.format(self.quality),
                '-b', '{}K'.format(self.bitrate), '{}\\{}'.format(self.output, out_filename)]):
                self.progress.emit(task['id'], result)
                if(result == 100):
                    self.end_progress.emit(task['id'])
                    break
            self.queue.task_done()

    def __ffmpeg_run_generator(self, cmd):
        total_dur = None
        cmd_ffmpeg = [cmd[0]] + ["-progress", "-", "-nostats"] + cmd[1:]
        stderr = []

        self.process = subprocess.Popen(
            cmd_ffmpeg,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False,
        )

        while True:
            line = self.process.stdout.readline().decode("utf8", errors="replace").strip()
            if line == "" and self.process.poll() is not None:
                break
            stderr.append(line.strip())

            if not total_dur and self.RE_DURATION.search(line):
                total_dur = self.RE_DURATION.search(line).groupdict()
                total_dur = self.__convert_to_ms(**total_dur)
                continue
            if total_dur:
                result = self.RE_TIME.search(line)
                if result:
                    elapsed_time = self.__convert_to_ms(**result.groupdict())
                    yield int(elapsed_time / total_dur * 100)

        # TODO: Реализовать позже лог ошибок и обработку исключений
        if self.process.returncode != 0:
            self.error.emit()
            raise RuntimeError(
                "RunTimeError {}: {}".format(cmd, str("\n".join(stderr))))
        yield 100

    def __convert_to_ms(self, **kwargs):
        hour = int(kwargs.get("hour", 0))
        minute = int(kwargs.get("min", 0))
        sec = int(kwargs.get("sec", 0))
        ms = int(kwargs.get("ms", 0))

        result = (hour * 60 * 60 * 1000) + \
            (minute * 60 * 1000) + (sec * 1000) + ms
        return result

    def __format_filename_output(self, filename, quality, ext):
        filename = filename.split('/').pop()
        return 'compress_{}-{}.{}'.format(filename, quality, ext)

    def __del__(self):
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)