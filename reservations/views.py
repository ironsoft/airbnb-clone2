import datetime
from django.shortcuts import redirect, reverse, render
from django.http import Http404
from django.contrib import messages
from django.views.generic import View, ListView
from rooms import models as room_models
from reviews import forms as review_forms
from . import models


class CreateError(Exception):

    pass


def create_reservation(request, room_pk, year, month, date):

    try:
        # 먼저 datetime()을 통해 예약을 원하는 날짜의 객체(date_obj)를 만든다. 
        date_obj = datetime.datetime(year=year, month=month, day=date)
        # room_pk 를 통해 해당 룸의 객체를 생성한다. 
        room = room_models.Room.objects.get(pk=room_pk)
        try:
            # BookedDay 에서 이미 예약이 되어 있는 객체가 있는지 조회해 본다. 
            models.BookedDay.objects.get(day=date_obj, reservation__room=room)
            # 만약에 있다면 예약이 불가함으로 메세지를 전달하고 에러를 발생시킨다.
            messages.error(request, "Room already booked, sorry!")
            # 에러를 발생시켜야 하는데 딱 맞는 에러가 없으므로 위에 CreateError 클래스를 만들어 써먹는다. 
            raise CreateError()

        # 만약에 BookedDay 객체에서 맞는걸 찾을 수 없다면 예약이 가능하다는 의미이므로 예약을 생성한다. 
        except models.BookedDay.DoesNotExist:

            reservation = models.Reservation.objects.create(
                check_in=date_obj,
                # 자바스크립트를 사용할 수 없으므로 체크인에서 하루를 더한 날짜만 예약이 가능하도록 한다. 
                check_out=date_obj + datetime.timedelta(days=1),
                guest=request.user,
                room=room
            )
            messages.success(request, "Reservation Created!")
        # 일단 예약상세페이지 생성전까지 룸 디테일 페이지로 이동시킨다.  
        return redirect(reverse('reservations:detail', kwargs={"pk":reservation.pk}))

    # 만약 예약하려는 룸 자체가 존재하지 않는다면 예약이 불가능함으로 에러 메세지를 전달하고 에러를 발생시킨다. 
    except room_models.Room.DoesNotExist:
        messages.error(request, "Room doesn't exist")
        raise CreateError() 


class ReservationListView(View):

    def get(self, *agrs, **kwargs):
        room_pk = kwargs.get("room_pk")
        room = room_models.Room.objects.get(pk=room_pk)
        print(room.first_photo)
        reservations = models.Reservation.objects.filter(room=room)
        return render(self.request, "reservations/reservation_list.html", context={
            "reservations":reservations,
            "room":room,
        })
        

class ReservationDetailView(View):

    def get(self, *args, **kwargs):

        pk = kwargs.get("pk")
        reservation = models.Reservation.objects.get_or_none(pk=pk)
        # 만약 reservation이 존재하지 않으면 None인 경우이고 = not reservation 과 같은 말임.
        # 로그인한 사람이 예약을 한 사람이거나 또는 룸의 주인이어야만 상세페이지를 볼 수 있어야 함.     
        if not reservation or (reservation.guest != self.request.user and reservation.room.host != self.request.user):
            raise Http404()
        form = review_forms.ReviewForm
        return render(self.request, "reservations/reservation_detail.html", context={
            "reservation":reservation,
            "form":form,
        })


def edit_reservation(request, pk, verb):

    # confirm 버큰을 클릭 후, reservation 의 status 가 confirmed 으로 되어야 한다. 
    # confirm 버튼 클릭시, reservation.pk 와 'confirm' 2개의 인자를 받아 온다. 

    # 해당 예약을 가져온다. 
    # 만약 해당 예약의 상태를 confirmed 로 변경해 준다. 
    # 예약을 DB에 저장해 준다. 

    # 만들어 놓은 get_or_none 커스텀 매니저를 활용한다. 
    reservation = models.Reservation.objects.get_or_none(pk=pk)
    # 일단 예약이 DB 에 없으면 안되고, 또한 로그인한 사람이 게스트도 아니고 집주인도 아니면 404 를 발생시킨다. 
    if not reservation or (reservation.guest != request.user and reservation.room.host != request.user):
        raise Http404

    else:

        if verb == 'confirm':
            reservation.status = reservation.STATUS_CONFIRMED
            messages.success(request, "Your reservation has been confirmed!")

        # 이번에는 cancel 버튼 클릭시, 
        # reservation 의 status 가 canceled 로 변경되고,
        # 해당 reservation 의 예약일들을 BookedDay 에서 찾아서 삭제해 준다. 

        elif verb == 'cancel':
            reservation.status = reservation.STATUS_CANCELED
            models.BookedDay.objects.filter(reservation=reservation).delete()
            messages.success(request, "Successfuly Your Reservation Canceled!")

    reservation.save()
    return redirect(reverse("reservations:detail", kwargs={'pk':pk}))







