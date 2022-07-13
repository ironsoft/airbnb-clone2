from django.forms import forms
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from rooms import models as room_models
from . import forms

def review_create(request, reservation_pk, room_pk):

    if request.method == 'POST':

        form = forms.ReviewForm(request.POST)
        room = room_models.Room.objects.get_or_none(pk=room_pk)

        if not room:
            raise Http404()
        if form.is_valid():
            # 해당 리뷰가 모델에서 이미 존재하는지 안하는지 폼에서 필터링 하도록 인자를 전달해줌. 
            review = form.save(request.user, room)
            # 접속자가 한번도 이 룸에 대해 리뷰를 작성하지 않았다면 작성한 리뷰 저장
            if review is not None:
                user = request.user
                review.user = user
                review.room = room
                review.save()
                messages.success(request, "Review Saved!")
                return redirect(reverse("rooms:detail", kwargs={
                    "pk":room_pk,
                }))
            # 이미 해당룸에 접속자가 작성한 리뷰가 있을 때 리뷰 저장하지 않고 메세지만 전달. 페이지는 계속 해당 페이에 남아 있기. 
            else:
                messages.warning(request, "Sorry! You've already submitted your reviews.")
                return redirect(reverse("reservations:detail", kwargs={
                    "pk":reservation_pk,
                }))
        else:
            messages.error(request, "Something's wrong!")
            return redirect(reverse("core:home"))


