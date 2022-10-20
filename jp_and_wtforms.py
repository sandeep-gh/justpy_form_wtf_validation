import pickle
from starlette_wtf import CSRFProtectMiddleware, csrf_protect
from wtforms.validators	import DataRequired
from wtforms.fields.core import UnboundField
from wtforms import StringField as wtStringField
from wtforms import Form as wtForm, ValidationError
from wtforms.validators	import StopValidation, ValidationError
from collections import OrderedDict
from dataclasses import dataclass

button_classes = 'bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded m-2'
input_classes = 'border m-2 p-2'

import justpy as jp
with open("form_data.pickle", "rb") as fh:
    form_data = pickle.load(fh)


class Field:
    pass

class StringField(Field):
    def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        self.jp_hcref = None
        self.validators = [] # TODO: bring validators in 
        self.errors = [] #fTOOD
    def __call__(self, **kwargs):
        #print ("hijacked wt render filed -- ")
        if not self.jp_hcref:
            self.jp_hcref = jp.Input(**kwargs)
        return self.jp_hcref

    def validate(self, data, extra):
        # we have omitted extra validators
        chain = self.validators
        stop_validation = self._run_validation_chain(data, chain)

        # Call post_validate
        try:
            self.post_validate(data, stop_validation)
        except ValidationError as e:
            self.errors.append(e.args[0])
        return len(self.errors) == 0


    def _run_validation_chain(self, form, validators):
        """
        Run a validation chain, stopping if any validator raises StopValidation.

        :param form: The Form instance this field belongs to.
        :param validators: a sequence or iterable of validator callables.
        :return: True if validation was stopped, False otherwise.
        """
        #print ("running validataion chain")
        for validator in validators:
            try:
                #print ("trying validator = ", validator)
                validator(form, self)
            except StopValidation as e:
                if e.args and e.args[0]:
                    self.errors.append(e.args[0])
                return True
            except ValidationError as e:
                self.errors.append(e.args[0])

        return False


    def post_validate(self, *args):
        #print ("do post validate things")
        pass


class OrderedMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases): 
        return OrderedDict()

    def __new__(cls, name, bases, clsdict):
        c = type.__new__(cls, name, bases, clsdict)
        c._orderedKeys = clsdict.keys()
        return c
    
@dataclass    
class jpValidateForm(metaclass=OrderedMeta):
    
    @classmethod
    def setFields(cls):
        cls.fields = OrderedDict()
        for attr in cls._orderedKeys:
            
            if not attr.startswith('__'):
                #print (type(getattr(self.wtFormType, attr)))
                if isinstance(getattr(cls, attr), Field):
                    cls.fields[attr] = getattr(cls, attr)
        #print ("set fields called")
        #print (cls.fields)
        pass
    
    # def process(self, msg):
    #     """
    #     mimics wtf.Form process function. 
    #     Assigns values to each of the form 
    #     components. 
    #     """
        
    #     print ("i should process incoming message")
    #     print (msg)
        
    #     assert False

    @classmethod
    def validate(cls, msg):
        for item_data in form_data:
            item_data.id

        data  = None
        success = True
        for name, field in cls.fields.items():
            # if extra_validators is not None and name in extra_validators:
            #     extra = extra_validators[name]
            # else:
            #     extra = tuple()
            extra = tuple()
            if not field.validate(data, extra):
                success = False
        return success
    

    

             
class JPForm(jp.Form):
    # we will do interesting things here
    def __init__(self, wtFormType, **kwargs):
        """
        wtFormType maintains form definition. Its also the validator
        """
        super().__init__(**kwargs)
        self.wtFormType = wtFormType
        self.build_components()
    def build_components(self):
        """
        build child and submit buttons
        components
        """
        self.form_components =  OrderedDict()
        self.component_id_to_name  = {}
        for fn, fd in self.wtFormType.fields.items():
            print (fn, " ", fd)
            self.form_components[fn] = fd(a=self, id=fn)
            self.form_components[fn].name = fn
            #self.component_id_to_name[self.form_components[fn].id] = fn

        # for name, field in self.wtFormType.():
        #     print (name, " ", field)
        print ("components = ", self.form_components)
        #print ("ids = ", self.component_id_to_name)
    def validate(self, msg, extra_validators=None):
        
        #wtForm = self.wtFormType(msg)
        #TODO: from msg get data from each form component
        #print ()
        for item_data in msg.form_data:
            print ('visiting = ', item_data)
            print ('visiting = ', item_data['value'])
            

        return self.wtFormType.validate(msg)
        # data = None
        # success = True
        # for name, field in wtForm._fields.items():
        #     if extra_validators is not None and name in extra_validators:
        #         extra = extra_validators[name]
        #     else:
        #         extra = tuple()
                
        #     if not field.validate(self, data, extra):
        #         success = False
                
        
        # return success 

@dataclass    
class MyFormValidator(jpValidateForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])


class MyFormValidator2(jpValidateForm):
    name2 = StringField('name', validators=[DataRequired()])
    email2 = StringField('email', validators=[DataRequired()])
         

#validate the form    
#myjpForm.validate(form_data)



#myjpForm.build_components()

def runonce():
    MyFormValidator.setFields()
    MyFormValidator2.setFields()


runonce()
# myjpForm = JPForm(MyFormValidator)
# myjpForm.build_components()

# msg = None 
# myjpForm.validate(msg)


app = jp.build_app()
def form_build_and_validate():
    wp = jp.WebPage(use_websockets = False)
    
    myjpForm = JPForm(MyFormValidator, a = wp)
    submit_button = jp.Input(value='Submit Form', type='submit', a=myjpForm, classes=button_classes)
    def submit_form(self, msg):
        # traceback.print_stack(file=sys.stdout)
        print("on_submit click = ", msg.form_data)
        myjpForm.validate(msg)
        with open("form_data.pickle", "wb") as fh:
            pickle.dump(msg.form_data, fh)

    myjpForm.on('submit', submit_form)
    return wp

app.add_jproute("/", form_build_and_validate)

wp  = form_build_and_validate()
form = wp.components[0]
# inp1, inp2, submit = form.components
# print (submit)
from addict import Dict
msg = Dict()
msg.form_data = form_data = [{'html_tag': 'input', 'id': '11', 'type': 'text', 'value': 'sdsf', 'checked': False}, {'html_tag': 'input', 'id': '12', 'type': 'text', 'value': 'sdsd', 'checked': False}, {'html_tag': 'input', 'id': '13', 'type': 'submit', 'value': 'Submit Form', 'class': 'bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded m-2', 'checked': False}]

form.on_submit(msg)

