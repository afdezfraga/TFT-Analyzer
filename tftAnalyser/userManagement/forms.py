from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from tftAnalyser.settings import MAX_LENGTH_USERNAME, MIN_LENGTH_USERNAME, MAX_LENGTH_PASSWORD, MIN_LENGTH_PASSWORD

class SignupForm(forms.Form):

   username = forms.CharField(
      label = "Nombre de usuario:",
      max_length = MAX_LENGTH_USERNAME,
      min_length = MIN_LENGTH_USERNAME,
      required = True,
   )
   password = forms.CharField(
      label = "Contraseña:",
      max_length = MAX_LENGTH_PASSWORD,
      min_length = MIN_LENGTH_PASSWORD,
      required = True,
      widget=forms.PasswordInput()
   )

   def __init__(self, *args, **kwargs):
       super(SignupForm, self).__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.form_id = 'id-signupForm'
       self.helper.form_class = 'px-4 py-3'
       self.helper.form_method = 'post'
       self.helper.form_action = 'signup'
       self.helper.add_input(Submit('submit', 'Entrar'))
       self.helper.add_input(Submit('submit', 'Registrarse'))

