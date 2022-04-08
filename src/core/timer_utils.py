import time

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

class Timer():
    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type,exc_value, exc_traceback):
        end_time = time.time()
        duration = convert((end_time-self.start_time))
        print("Elapsed {} [days:hours:min:seconds]".format(duration))