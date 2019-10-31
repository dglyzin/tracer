import unittest
import sys


# what print for each error
# (unused see OVERRIDE tag)
STDOUT_LINE = '   FAIL%s'
STDERR_LINE = '   ERROR%s'


class SimpleTextResult(unittest._TextTestResult):
    '''
    DESCRIPTION:
    For nice result out in stream.
    if buffer=True in runner.
    '''
    
    def _restoreStdout(self):
        """
        DESCRIPTION:
        This methond differ from original by output
        during errors.
        For nice silent output in stdout.
        See OVERRIDE tags.
        """

        if self.buffer:
            if self._mirrorOutput:
                '''
                OVERRIDE:

                output = sys.stdout.getvalue()
                error = sys.stderr.getvalue()
                
                if output:
                    if not output.endswith('\n'):
                        output += '\n'
                    self._original_stdout.write(STDOUT_LINE % output)
                    
                if error:
                    error = '\n'  # OVERRIDE
                    if not error.endswith('\n'):
                        error += '\n'
                    self._original_stderr.write(STDERR_LINE % error)
                '''
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self._stdout_buffer.seek(0)
            self._stdout_buffer.truncate()
            self._stderr_buffer.seek(0)
            self._stderr_buffer.truncate()

    def printErrorList(self, flavour, errors):
        '''
        DESCRIPTION:
        All Errors in TestCases.core is cpp generation
        fail.
        All Failures in TestCases.core is gcc fail.
        '''
        if len(errors) != 0:
            if flavour == 'ERROR':
                self.stream.writeln(self.separator1)
                self.stream.writeln("%s tester errors occurred" % str(len(errors)))
            elif flavour == 'FAIL':
                self.stream.writeln(self.separator1)
                self.stream.writeln("%s tests fail see details in %s"
                                    % (str(len(errors)), "log file"))


class SimpleTextRunner(unittest.TextTestRunner):
    '''
    DESCRIPTION:
    Runner for SimpleTextResult.
    '''
    def _makeResult(self):
        return(SimpleTextResult(self.stream, self.descriptions, self.verbosity))

