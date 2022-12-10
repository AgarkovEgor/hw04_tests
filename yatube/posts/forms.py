from django import forms
from .models import Post, Comments


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
        label = {
            'text': 'Комментарий'
        }
        help_text = {
            'text': 'Напишите комментарий'
        }




