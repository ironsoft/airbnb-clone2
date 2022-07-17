from django import template
from lists import models as list_models

register = template.Library()


@register.simple_tag(takes_context=True)
def on_favs(context, room):
    user = context.request.user
    # # List DB에 이 사용자가 클릭한 즐겨찾기가 있는지 없는지 확인
    # the_list = list_models.List.objects.get_or_none(
    #     user=user,
    #     name="My Favorites Houses",
    # )
    # # 해당 즐겨찾기 리스트가 있으면 해당 룸이 있는지 없는지 확인. 
    # return room in the_list.rooms.all()

    # 에러난 부분 새로운 코드로 작성
    try:
        the_list = list_models.List.objects.get_or_none(
        user=user,
        name="My Favorites Houses",
        )
        return room in the_list.rooms.all()
    except list_models.List.DoesNotExist:
        return False