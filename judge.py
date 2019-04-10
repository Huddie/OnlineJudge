import os, sys, filecmp, re, subprocess, os.path, uuid, argparse, smtplib, glob
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
        files = list(glob.iglob('./**/{0}.problem'.format(program_name), recursive=True))
        if len(files) > 0:
            return files[0]

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
        output_file = f'{self.attempt.uid}.solution'
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
                    with open(f'{self.attempt.uid}.solution', 'r') as file2:
                        f1, f2 = file1.read(), file2.read()
                f1, f2 = f1.strip(), f2.strip()
                return 200, f1, f2
        except TimeoutExpired as tle:
            return 408, tle
        except CalledProcessError as e:
            print(e.output)

    


def email(status):
    return """<!doctype html>
<html>
    <head>
    <meta charset="UTF-8">
    <!-- utf-8 works for most cases -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Forcing initial-scale shouldn't be necessary -->
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <!-- Use the latest (edge) version of IE rendering engine -->
    <title>EmailTemplate-Responsive</title>
    <!-- The title tag shows in email notifications, like Android 4.4. -->
    <!-- Please use an inliner tool to convert all CSS to inline as inpage or external CSS is removed by email clients -->
    <!-- important in CSS is used to prevent the styles of currently inline CSS from overriding the ones mentioned in media queries when corresponding screen sizes are encountered -->

    <!-- CSS Reset -->
    <style type="text/css">
/* What it does: Remove spaces around the email design added by some email clients. */
      /* Beware: It can remove the padding / margin and add a background color to the compose a reply window. */
html,  body {
	margin: 0 !important;
	padding: 0 !important;
	height: 100% !important;
	width: 100% !important;
}
/* What it does: Stops email clients resizing small text. */
* {
	-ms-text-size-adjust: 100%;
	-webkit-text-size-adjust: 100%;
}
/* What it does: Forces Outlook.com to display emails full width. */
.ExternalClass {
	width: 100%;
}
/* What is does: Centers email on Android 4.4 */
div[style*="margin: 16px 0"] {
	margin: 0 !important;
}
/* What it does: Stops Outlook from adding extra spacing to tables. */
table,  td {
	mso-table-lspace: 0pt !important;
	mso-table-rspace: 0pt !important;
}
/* What it does: Fixes webkit padding issue. Fix for Yahoo mail table alignment bug. Applies table-layout to the first 2 tables then removes for anything nested deeper. */
table {
	border-spacing: 0 !important;
	border-collapse: collapse !important;
	table-layout: fixed !important;
	margin: 0 auto !important;
}
table table table {
	table-layout: auto;
}
/* What it does: Uses a better rendering method when resizing images in IE. */
img {
	-ms-interpolation-mode: bicubic;
}
/* What it does: Overrides styles added when Yahoo's auto-senses a link. */
.yshortcuts a {
	border-bottom: none !important;
}
/* What it does: Another work-around for iOS meddling in triggered links. */
a[x-apple-data-detectors] {
	color: inherit !important;
}
</style>

    <!-- Progressive Enhancements -->
    <style type="text/css">
        
        /* What it does: Hover styles for buttons */
        .button-td,
        .button-a {
            transition: all 100ms ease-in;
        }
        .button-td:hover,
        .button-a:hover {
            background: #555555 !important;
            border-color: #555555 !important;
        }

        /* Media Queries */
        @media screen and (max-width: 600px) {

            .email-container {
                width: 100% !important;
            }

            /* What it does: Forces elements to resize to the full width of their container. Useful for resizing images beyond their max-width. */
            .fluid,
            .fluid-centered {
                max-width: 100% !important;
                height: auto !important;
                margin-left: auto !important;
                margin-right: auto !important;
            }
            /* And center justify these ones. */
            .fluid-centered {
                margin-left: auto !important;
                margin-right: auto !important;
            }

            /* What it does: Forces table cells into full-width rows. */
            .stack-column,
            .stack-column-center {
                display: block !important;
                width: 100% !important;
                max-width: 100% !important;
                direction: ltr !important;
            }
            /* And center justify these ones. */
            .stack-column-center {
                text-align: center !important;
            }
        
            /* What it does: Generic utility class for centering. Useful for images, buttons, and nested tables. */
            .center-on-narrow {
                text-align: center !important;
                display: block !important;
                margin-left: auto !important;
                margin-right: auto !important;
                float: none !important;
            }
            table.center-on-narrow {
                display: inline-block !important;
            }
                
        }

    </style>
    </head>
    <body bgcolor="#e0e0e0" width="100%" style="margin: 0;" yahoo="yahoo">
    <table bgcolor="#e0e0e0" cellpadding="0" cellspacing="0" border="0" height="100%" width="100%" style="border-collapse:collapse;">
      <tr>
        <td><center style="width: 100%;">
            
            <!-- Visually Hidden Preheader Text : BEGIN -->
            <div style="display:none;font-size:1px;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;mso-hide:all;font-family: sans-serif;"> (Optional) This text will appear in the inbox preview, but not the email body. </div>
            <!-- Visually Hidden Preheader Text : END --> 
            
            <!-- Email Header : BEGIN -->
            <table align="center" width="600" class="email-container">
            <tr>
                <td style="padding: 20px 0; text-align: center">&nbsp;</td>
              </tr>
          </table>
            <!-- Email Header : END --> 
            
            <!-- Email Body : BEGIN -->
            <table cellspacing="0" cellpadding="0" border="0" align="center" bgcolor="#ffffff" width="600" class="email-container">
            
            <!-- Hero Image, Flush : BEGIN -->
            <tr>
                <td class="full-width-image">&nbsp;</td>
              </tr>
            <!-- Hero Image, Flush : END --> 
            
            <!-- 1 Column Text : BEGIN -->
            <tr>
                <td style="padding: 40px; text-align: center; font-family: sans-serif; font-size: 15px; mso-height-rule: exactly; line-height: 20px; color: #555555;">Your attempt at CSAC has processed and a result is not available.<br>
                  <br>
                  Result below:<br>
                  <br>
                  {0} &nbsp; <br>
                  <br>
                  <!-- Button : Begin -->
                
                <table cellspacing="0" cellpadding="0" border="0" align="center" style="margin: auto">
                    <tr>
                    <td style="border-radius: 3px; background: #222222; text-align: center;" class="button-td"><a href="https://venus.cs.qc.cuny.edu/~adeh6562/csac/OnlineJudge/csac.php" style="background: #222222; border: 15px solid #222222; padding: 0 10px;color: #ffffff; font-family: sans-serif; font-size: 13px; line-height: 1.1; text-align: center; text-decoration: none; display: block; border-radius: 3px; font-weight: bold;" class="button-a"> 
                      <!--[if mso]>&nbsp;&nbsp;&nbsp;&nbsp;<![endif]-->CSAC 2019<!--[if mso]>&nbsp;&nbsp;&nbsp;&nbsp;<![endif]--> 
                      </a></td>
                  </tr>
                  </table>
                
                <!-- Button : END --></td>
              </tr>
            <!-- 1 Column Text : BEGIN --> 
            
            <!-- Background Image with Text : BEGIN -->
            <tr>
                <td background="" bgcolor="#222222" valign="middle" style="text-align: center; background-position: center center !important; background-size: cover !important;"><!--[if gte mso 9]>
                    <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width:600px;height:175px; background-position: center center !important;">
                    <v:fill type="tile" src="assets/Responsive/Image_600x230.png" color="#222222" />
                    <v:textbox inset="0,0,0,0">
                    <![endif]-->
                
                <div>
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                        <td valign="middle" style="text-align: center; padding: 40px; font-family: sans-serif; font-size: 15px; mso-height-rule: exactly; line-height: 20px; color: #ffffff;"> This contest is sponsored by ... surprise.<br>
                        If you feel that a mistake was made, please reach out to Ehud Adler.<br></td>
                      </tr>
                  </table>
                  </div>
                
                <!--[if gte mso 9]>
                    </v:textbox>
                    </v:rect>
                    <![endif]--></td>
              </tr>
            <!-- Background Image with Text : END --> 
            
            <!-- Two Even Columns : BEGIN -->
            <tr>
                <td align="center" valign="top" style="padding: 10px;"><table cellspacing="0" cellpadding="0" border="0" width="100%">
                    <tr> </tr>
                  </table></td>
              </tr>
            <!-- Two Even Columns : END --> 
            
            <!-- Three Even Columns : BEGIN -->
            <tr>
                <td align="center" valign="top" style="padding: 10px;"><table cellspacing="0" cellpadding="0" border="0" width="100%">
                    <tr>
                    <td width="33.33%" class="stack-column-center"><table cellspacing="0" cellpadding="0" border="0">
                        <tr> </tr>
                        <tr> </tr>
                      </table></td>
                    <td width="33.33%" class="stack-column-center"><table cellspacing="0" cellpadding="0" border="0">
                        <tr> </tr>
                        <tr> </tr>
                      </table></td>
                    <td width="33.33%" class="stack-column-center"><table cellspacing="0" cellpadding="0" border="0">
                        <tr> </tr>
                        <tr> </tr>
                      </table></td>
                  </tr>
                  </table></td>
              </tr>
            <!-- Three Even Columns : END --> 
            
            <!-- Thumbnail Left, Text Right : BEGIN -->
            <tr> </tr>
            <!-- Thumbnail Left, Text Right : END --> 
            
            <!-- Thumbnail Right, Text Left : BEGIN -->
            <tr>
                <td dir="rtl" align="center" valign="top" width="100%" style="padding: 10px;"><table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                    <td width="33.33%" class="stack-column-center"><table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr> </tr>
                      </table></td>
                    <td width="66.66%" class="stack-column-center"><table align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr> </tr>
                      </table></td>
                  </tr>
                  </table></td>
              </tr>
            <!-- Thumbnail Right, Text Left : END -->
            
          </table>
            <!-- Email Body : END --> 
            
            <!-- Email Footer : BEGIN -->
            <table align="center" width="600" class="email-container">
            <tr>
                <td style="padding: 40px 10px;width: 100%;font-size: 12px; font-family: sans-serif; mso-height-rule: exactly; line-height:18px; text-align: center; color: #888888;"><webversion style="color:#cccccc; text-decoration:underline; font-weight: bold;">View as a Web Page</webversion>
                  <br>
                CSAC 2019<br>                  <unsubscribe style="color:#888888; text-decoration:underline;">unsubscribe</unsubscribe></td>
              </tr>
          </table>
            <!-- Email Footer : END -->
            
          </center></td>
      </tr>
    </table>
</body>
</html>
""".format(status)


def send_email(status, email):
    message = Mail(
        from_email='ehud.adler62@qmail.cuny.edu',
        to_emails=email,
        subject='CSAC 2019 Results',
        html_content=email(status))
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e)

def parse():
    parser = argparse.ArgumentParser(
        description='Specify commands for CSAC v1.0')
    parser.add_argument('--filepath')
    parser.add_argument('--problem_code')
    parser.add_argument('--email')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse()
    try:
        print(args.filepath)
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





