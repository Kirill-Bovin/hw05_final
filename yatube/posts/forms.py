from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Картинка'
        }
        help_texts = {
            'text': 'Текст',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Добавтье картинку'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

        def clean_subject(self):
            data = self.cleaned_data['text']
            if '' in data:
                raise forms.ValidationError('Поле должно быть заполнено')
            return data
