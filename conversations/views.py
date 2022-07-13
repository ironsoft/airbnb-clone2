from django.contrib import messages
from django.views.generic import View
from django.http import Http404
from django.db.models import Q
from django.shortcuts import render, reverse, redirect
from users import models as user_models
from . import models, forms

def go_conversation(request, a_pk, b_pk):
    
    try: 
        user_one = user_models.User.objects.get(pk=a_pk)
        user_two = user_models.User.objects.get(pk=b_pk)
        # 이 두사람이 대화를 한적이 있는지 Conversations에서 찾기.
        result = models.Conversation.objects.filter(participants=user_one).filter(participants=user_two)
        # result 는 QuerySet, 즉 객체 리스트로 반환함으로 언팩해 줘야 함.
        # 기존에 없다면 새롭게 생성하기 (QuerySet 이 비어있는 경우) 
        if not result: 
            conversation = models.Conversation.objects.create()
            conversation.participants.add(user_one, user_two)
        # 기존에 하던 대화가 있다면,
        else:
            conversation = result[0]
        return redirect(reverse("conversations:detail", kwargs={"pk":conversation.pk}))

    # user가 호스트나 게스트가 아닌 경우.
    except user_models.User.DoesNotExist:
        messages.error(request, "Something's wrong!")
        return redirect(reverse("core:home"))


class ConversationDetailView(View):
    
    def get(self, *args, **kwargs):

        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()

        form = forms.AddCommentForm()
        return render(self.request, "conversations/conversation_detail.html", context={
            "conversation":conversation,
            "form":form,
        })

    def post(self, *args, **kwargs):
        
        message = self.request.POST.get("message", None)
        conversation_pk = kwargs.get("conversation_pk")
        conversation = models.Conversation.objects.get_or_none(pk=conversation_pk)
        if not conversation:
            raise Http404()
        if message is not None:
            models.Message.objects.create(
                message=message,
                user=self.request.user,
                conversation=conversation, 
            )
        return redirect(reverse("conversations:detail", kwargs={"pk":conversation_pk}))




        



    
            