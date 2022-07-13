from django import template

register = template.Library()

@register.filter(name="sexy_capitals") # 이부분이 태그 이름 지정함. 아니면 함수명을 그대로 태그명으로 사용하게 됨. 
def sexy_capitals(value):
    return value.capitalize()