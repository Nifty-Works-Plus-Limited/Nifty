# This is to help test signed urls
from django import forms
from content.models import movies

class CreateMovieForm(forms.ModelForm):

    class Meta:
        model   = movies
        fields  = ['title','desc', 'image', 'movie',  'contentTheme' ]

    '''
    image_signed_url = forms.CharField(widget=forms.HiddenInput())
    video_signed_url = forms.CharField(widget=forms.HiddenInput())
    ''' 