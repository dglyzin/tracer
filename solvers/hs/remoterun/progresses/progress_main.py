import re
from solvers.hs.remoterun.progresses.progress_cmd import ProgressCmd


class StdoutProgresses():
    def __init__(self, re_pattern="[\d]+\s?%", STEPS=100, notebook=None):
        self.re_pattern = re_pattern
        self.prefix = "solving"

        self.progresses = []

        if notebook is not None:
            # from solvers.hs.remoterun.progresses.progress_notebook import ProgressNotebook
            self.progresses.append(notebook)
            # self.progresses.append(ProgressNotebook(STEPS,
            #                                         prefix=self.prefix))
        else:
            self.progresses.append(ProgressCmd(STEPS,
                                               prefix=self.prefix))
            
    def show_stdout_progresses(self, line):
        res = re.search(self.re_pattern, line)
        if res is not None:
            res_str = res.group()
            value = int(res_str[:-1])
            for progress in self.progresses:
                progress.succ(value)
    

def test():
    lines = ["there is 11% complited"]
    lines.append("there is 1 % complited")
    lines.append("there is 100 % complited")
    
    progress = StdoutProgresses()
    for line in lines:
        progress.show_stdout_progresses(line)


if __name__ == '__main__':
    test()
