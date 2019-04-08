import os, sys, filecmp, re, subprocess, os.path, uuid, argparse, smtplib
from subprocess import CalledProcessError, TimeoutExpired
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
status_codes = {
    200: 'OK',
    201: 'ACCEPTED',
    400: 'WRONG ANSWER',
    401: 'COMPILATION ERROR',
    402: 'RUNTIME ERROR',
    403: 'INVALID FILE',
    404: 'FILE NOT FOUND',
    405: 'INPUT FILE ERROR',
    408: 'TIME LIMIT EXCEEDED'
}

filetypes = {
    'c': "C",
    'cpp': "CPP",
    'java': "JAVA"
}

files_to_delete = []

class ErrorHandler:
    @staticmethod
    def process_status(error_num):
        if error_num != 200:
            print(status_codes[error_num])
            exit(1)

class FileManager:
    @staticmethod
    def file_exists(filepath):
        return os.path.isfile(filepath)

    @staticmethod
    def is_valid_file(filepath):
        # Exists
        if not FileManager.file_exists(filepath):
            return False

        # Valid filetype
        print(FileManager.filetype(filepath))
        return FileManager.filetype(filepath) in filetypes

    @staticmethod
    def is_valid_program(prg_name):
        pass

    @staticmethod
    def filetype(filepath):
        return (os.path.splitext(filepath)[1])[1:]

    @staticmethod
    def filename(filepath):
        return (os.path.splitext(filepath)[0])
        
    @staticmethod
    def delete_file(filepath):
        os.remove(filepath)


class ProgramManager:
    @staticmethod
    def dirpath_for_program_name(program_name):
        return f'./{program_name}'

    @staticmethod
    def expected_output_filepath(dirpath):
        return f'{dirpath}/output.txt'

    @staticmethod
    def test_input_filepath(dirpath):  
        return f'{dirpath}/input.txt'

    @staticmethod
    def rules(dirpath):
        with open(f'{dirpath}/rules.txt', 'r') as rules:
            return rules.read()

    @staticmethod
    def timeout(rules):
        return 10

    @staticmethod
    def generateUID():
        return str(uuid.uuid4().hex)

    @staticmethod
    def getLang(ext):
        return filetypes[ext]


class ResultManager:
    def __init__(self, f1, f2):
        self.f1 = f1
        self.f2 = f2
    
    def compare(self):
        if(self.f1 == self.f2):
            return 201, None
        else:
            return 400, "Results do not match"

class Attempt:
    def __init__(self, filepath, program_name):
        self.filepath = filepath
        self.program_name = program_name
        self.lang = ProgramManager.getLang(FileManager.filetype(filepath))
        self.uid = ProgramManager.generateUID()
        self.timeout = ProgramManager.timeout(ProgramManager.rules)

        dir_for_prg = ProgramManager.dirpath_for_program_name(program_name)
        self.inputfile = ProgramManager.test_input_filepath(dir_for_prg)
        self.expectedOutput = ProgramManager.expected_output_filepath(dir_for_prg)

    def compelationCommand(self, filepath, uid):
        if self.lang == 'C':
            return f"gcc {os.path.abspath(filepath)} -o {uid}"
        elif self.lang == 'CPP':
            return f"g++ {os.path.abspath(filepath)} -o {uid}"
        elif self.lang == 'JAVA':
            return f"javac {filepath}"

    def runCommand(self, filename, uid):
        if self.lang == 'C':
            return os.path.abspath(uid)
        elif self.lang == 'CPP':
            return os.path.abspath(uid)
        elif self.lang == 'JAVA':
            return fos.path.abspath(f"java {filename}")

class Program:
    def __init__(self, filepath, program_name):
        self.attempt = Attempt(filepath, program_name)

    def compile(self):

        compile_command = self.attempt.compelationCommand(
            self.attempt.filepath, 
            self.attempt.uid
        )

        try:
            result = subprocess.run(
                compile_command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            if result.returncode != 0:
                return 401, result.stderr
            else:
                return 200, None
                
        except CalledProcessError as e:
            print(e.output)

    def run_and_test(self):
        run_command = self.attempt.runCommand(self.attempt.filepath, self.attempt.uid)
        output_file = f'{self.attempt.uid}.txt'
        try:
            with open(output_file, 'w+') as fout:
                fin = None
                if self.attempt.inputfile and os.path.isfile(self.attempt.inputfile):
                    fin = open(self.attempt.inputfile, 'r')
                    result = subprocess.run(
                        run_command.split(),
                        stdin=fin,
                        stdout=fout,
                        stderr=subprocess.PIPE,
                        timeout=self.attempt.timeout
                    )
                else:
                    return 405, None

            # Append the newly created files to files_to_delte
            # this way they are cleaned up post program
            files_to_delete.append(run_command)
            files_to_delete.append(output_file)

            # close the file
            fin.close()

            # Check for errors
            if result.returncode != 0:
                return 402, result.stderr
            else:
                f1, f2 = None, None
                with open(self.attempt.expectedOutput, 'r') as file1:
                    with open(f'{self.attempt.uid}.txt', 'r') as file2:
                        f1, f2 = file1.read(), file2.read()
                f1, f2 = f1.strip(), f2.strip()
                return 200, f1, f2
        except TimeoutExpired as tle:
            return 408, tle
        except CalledProcessError as e:
            print(e.output)


def send_email(status, email):
    message = Mail(
        from_email='easports96@gmail.com',
        to_emails='adlerehud@gmail.com',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

if __name__ == "__main__":
    args = parse()
    try:
        filepath = input("filepath: ") if not args.filepath else args.filepath
        email = input("email: ") if not args.filepath else args.email
        prg = Program(filepath, "100")

        com_res = prg.compile()
        ErrorHandler.process_status(com_res[0])

        result = prg.run_and_test()
        ErrorHandler.process_status(result[0])

        result_mng = ResultManager(result[1], result[2])
        comp_res = result_mng.compare()

        send_email(status_codes[comp_res[0]], email)
        print(status_codes[comp_res[0]])

        for file in files_to_delete:
            FileManager.delete_file(file)

    except Exception as e:
        print(str(e))





