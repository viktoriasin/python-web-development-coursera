from datetime import datetime

from django.db.models import Q, Count, Avg
from pytz import UTC

from db.models import User, Blog, Topic


# 1. Создание (функция create):
# Создать пользователя first_name = u1, last_name = u1.
# Создать пользователя first_name = u2, last_name = u2.
# Создать пользователя first_name = u3, last_name = u3.
# Создать блог title = blog1, author = u1.
# Создать блог title = blog2, author = u1.
# Подписать пользователей u1 u2 на blog1, u2 на blog2.
# Создать топик title = topic1, blog = blog1, author = u1.
# Создать топик title = topic2_content, blog = blog1, author = u3, created = 2017-01-01.
# Лайкнуть topic1 пользователями u1, u2, u3.
# 2. Редактирование:
#
# Поменять first_name на uu1 у всех пользователей (функция edit_all).
# Поменять first_name на uu1 у пользователей, у которых first_name u1 или u2 (функция edit_u1_u2).
# 3. Удаление:
#
# удалить пользователя с first_name u1 (функция delete_u1).
# отписать пользователя с first_name u2 от блогов (функция unsubscribe_u2_from_blogs).
# 4. Найти топики у которых дата создания больше 2018-01-01 (функция get_topic_created_grated).
#
# 5. Найти топик у которого title заканчивается на content (функция get_topic_title_ended).
#
# 6. Получить 2х первых пользователей (сортировка в обратном порядке по id) (функция get_user_with_limit).
#
# 7. Получить количество топиков в каждом блоге, назвать поле topic_count, отсортировать по topic_count по возрастанию (функция get_topic_count).
#
# 8. Получить среднее количество топиков в блоге (функция get_avg_topic_count).
#
# 9. Найти блоги, в которых топиков больше одного (функция get_blog_that_have_more_than_one_topic).
#
# 10. Получить все топики автора с first_name u1 (функция get_topic_by_u1).
#
# 11. Найти пользователей, у которых нет блогов, отсортировать по возрастанию id (функция get_user_that_dont_have_blog).
#
# 12. Найти топик, который лайкнули все пользователи (функция get_topic_that_like_all_users).
#
# 13. Найти топики, у которы нет лайков (функция get_topic_that_dont_have_like).

def create():
    u1 = User.objects.create(first_name="u1", last_name="u1")
    u2 = User.objects.create(first_name="u2", last_name="u2")
    u3 = User.objects.create(first_name="u3", last_name="u3")
    blog1 = Blog.objects.create(title='blog1', author=u1)
    blog2 = Blog.objects.create(title='blog2', author=u1)
    blog1.subscribers.add(u1, u2)
    blog2.subscribers.add(u2)

    topic1 = Topic.objects.create(title='topic1', blog=blog1, author=u1)
    topic2_content = Topic.objects.create(
        title='topic2_content', blog=blog1, author=u3,
        created=datetime(year=2017, month=1, day=1, tzinfo=UTC))
    topic1.likes.add(u1, u2, u3)


def edit_all():
    User.objects.all().update(first_name='uu1')


def edit_u1_u2():
    User.objects.filter(
        Q(first_name='u1') | Q(first_name='u2')
    ).update(first_name='uu1')


def delete_u1():
    User.objects.get(first_name='u1').delete()


def unsubscribe_u2_from_blogs():
    User.objects.get(first_name='u2').subscriptions.clear()


def get_topic_created_grated():
    return Topic.objects.filter(created__gt=datetime(year=2018, month=1, day=1,
                                                     tzinfo=UTC))


def get_topic_title_ended():
    return Topic.objects.filter(title__endswith='content')


def get_user_with_limit():
    return User.objects.all().order_by('-pk')[:2]


def get_topic_count():
    return Blog.objects.annotate(
        topic_count=Count('topic', distinct=True)).order_by('topic_count')


def get_avg_topic_count():
    return Blog.objects.annotate(topic_count=Count('topic', distinct=True)).aggregate(
        avg=Avg('topic_count')
    )


def get_blog_that_have_more_than_one_topic():
    return Blog.objects.annotate(
        topic_count=Count('topic', distinct=True)).filter(topic_count__gt=1)


def get_topic_by_u1():
    return User.objects.get(first_name='u1').topic_set.all()
    # Topic.objects.filter(author__first_name='u1')


def get_user_that_dont_have_blog():
    return User.objects.filter(blog__isnull=True).order_by('pk')


def get_topic_that_like_all_users():
    user_cnt = User.objects.count()
    return Topic.objects.annotate(users_cnt=Count('likes', distinct=True)).filter(users_cnt__exact=user_cnt)


def get_topic_that_dont_have_like():
    return Topic.objects.filter(likes__isnull=True)
