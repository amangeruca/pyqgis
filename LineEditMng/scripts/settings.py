import os.path

PLUGIN_PATH = os.path.dirname(os.path.dirname(__file__))
APP_CONFIG = {}

with open(os.path.join(PLUGIN_PATH, 'config.ini')) as f:
    for line in f.readlines():
        if 'log_title:' in line:
            APP_CONFIG["log_title"] = line.split('log_title:')[1].strip()

        elif 'enable_print:' in line:
            APP_CONFIG["enable_print"] = eval(line.split('enable_print:')[1].strip())

        elif 'tolerance:' in line:
            APP_CONFIG["tolerance"] = float(line.split('tolerance:')[1].strip())

        elif 'rounding_digit:' in line:
            APP_CONFIG["rounding_digit"] = float(line.split('rounding_digit:')[1].strip())