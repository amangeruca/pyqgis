import os.path

PLUGIN_PATH = os.path.dirname(os.path.dirname(__file__))
APP_CONFIG = {}

with open(os.path.join(PLUGIN_PATH, 'config.ini')) as f:
    for line in f.readlines():
        if 'log_title:' in line:
            APP_CONFIG["log_title"] = line.split('log_title:')[1].strip()

        elif 'enable_print:' in line:
            APP_CONFIG["enable_print"] = eval(line.split('enable_print:')[1].strip())

# line editor permissions
        elif 'allow_settings:' in line:
            APP_CONFIG["allow_settings"] = eval(line.split('allow_settings:')[1].strip())
            
        elif 'allow_split_button:' in line:
            APP_CONFIG["allow_split_button"] = eval(line.split('allow_split_button:')[1].strip())
            
        elif 'allow_selfint_button:' in line:
            APP_CONFIG["allow_selfint_button"] = eval(line.split('allow_selfint_button:')[1].strip())
            
        elif 'allow_simpl_button:' in line:
            APP_CONFIG["allow_simpl_button"] = eval(line.split('allow_simpl_button:')[1].strip())
            
# line editor default
        elif 'enable_split_button:' in line:
            APP_CONFIG["enable_split_button"] = eval(line.split('enable_split_button:')[1].strip())
            
        elif 'enable_selfint_button:' in line:
            APP_CONFIG["enable_selfint_button"] = eval(line.split('enable_selfint_button:')[1].strip())
            
        elif 'enable_simplify:' in line:
            APP_CONFIG["enable_simplify"] = eval(line.split('enable_simplify:')[1].strip())
            
# function settings
        elif 'split_tolerance:' in line:
            APP_CONFIG["split_tolerance"] = float(line.split('split_tolerance:')[1].strip())

        elif 'simpl_tolerance:' in line:
            APP_CONFIG["simpl_tolerance"] = float(line.split('simpl_tolerance:')[1].strip())

        elif 'rounding_digit:' in line:
            APP_CONFIG["rounding_digit"] = float(line.split('rounding_digit:')[1].strip())