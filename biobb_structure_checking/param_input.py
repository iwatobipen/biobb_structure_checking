"""
  Module to manage command line for simple parameter input
"""
import argparse

def _get_input(value, prompt_text):
    """ Get input data """
    while value is None or value == '':
        value = input(prompt_text)
    if isinstance(value, str):
        value = value.replace(' ', '')
    return value

class ParamInput():
    """ Class to generate and manage interactive parameter dialogs"""
    def __init__(self, prefix, non_interactive=True):
        self.options = []
        self.non_interactive = non_interactive
        self.prefix = prefix


    def add_option_all(self):
        """ Add 'All' option to dialog"""
        self.add_option_list('all', ['All'])

    def add_option_none(self):
        """ Add 'None' option to dialog"""
        self.add_option_list('none', ['None'])

    def add_option_yes_no(self):
        """Add 'Yes/No' option to dialog"""
        self.add_option_list('yes', ['Yes'])
        self.add_option_list('no', ['No'])

    def add_option_list(self, label, opt_list, case=False, opt_type='list', \
            multiple=False, list2=None):
        """ Add a list based option to dialog """
        self.options.append({
            'label':label,
            'opt_list':opt_list,
            'case':case,
            'type':opt_type,
            'multiple':multiple,
            'list2':list2
        })

    def add_option_numeric(self, label, opt_list, opt_type, min_val, max_val):
        """ Add a numeric option to dialog """
        self.options.append({
            'label':label,
            'opt_list':opt_list,
            'type':opt_type,
            'min':min_val,
            'max':max_val,
        })

    def _build_dialog(self):
        if not self.options:
            return self.prefix + ': '
        opt_strs = []
        for opt in self.options:
            if opt['type'] == 'list':
                opt_strs.append(','.join(opt['opt_list']))
            elif opt['type'] in ('int', 'float'):
                if opt['min'] != 0 or opt['max'] != 0:
                    opt_strs.append('{} - {}'.format(opt['min'], opt['max']))
            elif opt['type'] == 'input':
                opt_strs.append('')
            elif opt['type'] == 'pair_list':
                str_opt = []
                for oper in opt['opt_list']:
                    str_opt.append('{}:[{}]'.format(oper, '|'.join(opt['list2'])))
                opt_strs.append(','.join(str_opt))
            else:
                opt_strs.append('?')
        return self.prefix + ' (' + ' | '.join(opt_strs) + '): '

    def _check_dialog_value(self, opt_value):
        if opt_value is None:
            return [False, -1, None]
        iopt = 0
        input_ok = False
        while not input_ok and iopt < len(self.options):
            opt = self.options[iopt]
            if opt['type'] in ('list', 'pair_list') and isinstance(opt_value, str):
                if opt['multiple']:
                    values = opt_value.split(',')
                else:
                    values = [opt_value]
                for val in values:
                    # To support both 'list' and 'pair_list':
                    val_sp = val.split(':')
                    val = val_sp[0]

                    input_ok =\
                        (opt['case'] == 'sensitive' and val in opt['opt_list'])\
                        or (opt['case'] == 'upper' and val.upper() in opt['opt_list'])\
                        or (opt['case'] == 'lower' and val.lower() in opt['opt_list'])\
                        or (not opt['case'] and val.lower() in\
                        list(map(lambda x: x.lower(), opt['opt_list'])))

                    if opt['type'] == 'pair_list':
                        input_ok = input_ok and val_sp[1] in opt['list2']

            elif opt['type'] in ('int', 'float'):
                opt_value = float(opt_value)
                if opt['type'] == "int":
                    opt_value = int(opt_value)
                input_ok = opt_value >= opt['min'] and opt_value <= opt['max']
            if not input_ok:
                iopt += 1

        return [input_ok, iopt, opt_value]

    def run(self, opt_value):
        """ Build and execute dialog"""

        # Non interactive enviroment, check available input only
        if self.non_interactive:
            # No options, nothing to do, return original value
            if not self.options:
                return opt_value
            # Check input
            (input_ok, iopt, opt_value) = self._check_dialog_value(opt_value)
            if not input_ok:
                print('Input not valid ({})'.format(opt_value))
                self.options.append({'label':'error'})
            return [self.options[iopt]['label'], opt_value]

        # Interactive input case
        prompt_str = self._build_dialog()
        # No options, simple input
        if not self.options:
            return _get_input(opt_value, prompt_str)
        # Prompt repeats until valid
        input_ok = False
        while not input_ok:
            opt_value = _get_input(opt_value, prompt_str)
            (input_ok, iopt, opt_value) = self._check_dialog_value(opt_value)
            if not input_ok:
                print('Input not valid ({})'.format(opt_value))
                opt_value = ''
        return [self.options[iopt]['label'], opt_value]

class Dialog():
    """Dialog to complete command options"""
    def __init__(self):
        self.options = {}

    def add_option(self, command, opt_prompt, opt_dest, opt_help, opt_type=str):
        """add Dialog option"""
        self.options[command] = {
            'command':command,
            'prompt': opt_prompt,
            'dest':   opt_dest,
            'help':   opt_help,
            'type':   opt_type
        }

    def get_parameter(self, command, opts):
        """Generate Dialog"""
        dialog = self.options[command]
        if not dialog:
            raise NoDialogAvailableError(command)
            return None
        opts_parser = argparse.ArgumentParser(prog=dialog['command'])
        opts_parser.add_argument(
            dialog['prompt'],
            dest=dialog['dest'],
            help=dialog['help'],
            type=dialog['type']
        )
        return vars(opts_parser.parse_args(opts))

    def get_dialog(self, command):
        """Get Dialog data"""
        return self.options[command]

    def exists(self, command):
        """Checks whether a Dialog for **command** is defined"""
        return command in self.options

#===============================================================================
class Error(Exception):
    """ Base class """
    pass

class NoDialogAvailableError(Error):
    def __init__(self, command):
        self.message = 'ERROR: no dialog available for {}'.format(command)