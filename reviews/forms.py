from django import forms
from . import models


class ReviewForm(forms.ModelForm):

    accuracy = forms.IntegerField(min_value=1, max_value=5)
    communication = forms.IntegerField(min_value=1, max_value=5)
    cleanliness = forms.IntegerField(min_value=1, max_value=5)
    location = forms.IntegerField(min_value=1, max_value=5)
    check_in = forms.IntegerField(min_value=1, max_value=5)
    value = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = models.Review
        fields = (
            "review",
            "accuracy",
            "communication",
            "cleanliness",
            "location",
            "check_in",
            "value",
        )
        widgets = {
            "review": forms.Textarea(attrs={"placeholder": "Write your review here"}),
            "accuracy": forms.NumberInput(attrs={"placeholder": "accuracy"}),
            "communication": forms.NumberInput(attrs={"placeholder": "communication"}),
            "cleanliness": forms.NumberInput(attrs={"placeholder": "cleanliness"}),
            "location": forms.NumberInput(attrs={"placeholder": "location"}),
            "check_in": forms.NumberInput(attrs={"placeholder": "check_in"}),
            "value": forms.NumberInput(attrs={"placeholder": "value"}),
        }

    def save(self, *args, **kwargs):
        review = super().save(commit=False)
        user, room = args
        existing_review = models.Review.objects.filter(user=user, room=room)        
        if existing_review is not None:
            return None
        return review