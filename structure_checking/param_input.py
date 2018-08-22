"""
  Module to manage command line for simple parameter input
"""

class ParamInput():
    def __init__(self, prefix, opt_value, non_interactive=True):
        self.options=[]        
        self.opt_value=opt_value
        self.non_interactive = non_interactive
        self.prefix = prefix
        
    def add_option(self, label, opt_list, case=False, type='list', multiple=False, min=0, max=0):
        self.options.append({'label':label,'opt_list':opt_list,'case':case,'type':type, 'min':min, 'max':max, 'multiple':multiple})
    
    def add_option_all(self):
        self.add_option('all', ['All'])

    def add_option_none(self):
        self.add_option('none', ['None'])
        
    def add_option_yes_no(self):
        self.add_option('yes', ['Yes'])
        self.add_option('nos', ['No'])
        
    def run(self):
        prompt_str = self.prefix
        if len(self.options):
            opt_strs=[]
            for opt in self.options:
                if opt['type'] == 'list':
                    opt_strs.append(','.join(opt['opt_list']))
                elif opt['type'] == 'int' or opt['type'] == 'float':
                    if opt['min'] != 0 or opt['max'] != 0:
                        opt_strs.append('{} - {}'.format(opt['min'], opt['max']))
                elif opt['type'] == 'input':
                    opt_strs.append('')
                else: 
                    opt_strs.append('?')
                
            prompt_str += ' ('+' | '.join(opt_strs)+')'
        prompt_str += ': ' 
# No options, simple input
        if not len(self.options):
            if not self.non_interactive:
                self.opt_value = _get_input(self.opt_value, prompt_str)
            return ['input', self.opt_value]
# Check alternative options        
        input_ok = False
        while not input_ok:
            if not self.non_interactive:
                self.opt_value = _get_input(self.opt_value, prompt_str)
            iopt=0
            if self.opt_value is None:
                return ['error','']
            else:
                while not input_ok and iopt < len(self.options):
                    opt = self.options[iopt]
                    if opt['type'] == 'list' and isinstance(self.opt_value, str):
                        if not opt['multiple']:
                            values = [self.opt_value]
                        else:
                            values = self.opt_value.split(',')
                        group_ok = True
                        for val in values:
                            if opt['case'] == 'upper':
                                val=val.upper()
                                group_ok = group_ok and val in opt['opt_list']
                            elif opt['case'] == 'lower':
                                val=val.lower()
                                group_ok = group_ok and val in opt['opt_list']
                            elif opt['case'] == 'sensitive':
                                group_ok = group_ok and val in opt['opt_list']
                            else:
                                group_ok = group_ok and val.lower() in list(map(lambda x: x.lower(),opt['opt_list']))
                        input_ok = group_ok
                    elif opt['type'] == 'int': 
                        self.opt_value = int(self.opt_value)
                        input_ok = self.opt_value >= opt['min'] and self.opt_value <= opt['max']
                    if not input_ok:
                        iopt +=1
                if not input_ok:
                    print ("Input not valid")
                    if self.non_interactive:
                        self.options.append({'label':'error'})
                        input_ok=True
                    else:
                        self.opt_value = ''

        return [self.options[iopt]['label'],self.opt_value]
    
def _get_input (value, prompt_text):
    while value is None or value == '':
        value = input (prompt_text)
    if isinstance(value, str):
        value = value.replace(' ', '')
    return value