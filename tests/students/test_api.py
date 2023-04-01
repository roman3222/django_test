import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user('admin')


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory



@pytest.mark.django_db
def test_get_first_course(client, user, course_factory):
    course = course_factory(_quantity=10)
    first_course = course[0]
    response = client.get('/courses/?id=1')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == first_course.name


@pytest.mark.django_db
def test_get_all_courses(client, user, course_factory):
    course_all = course_factory(_quantity=10)
    response = client.get('/courses/')
    assert response.status_code == 200
    data = response.json()
    courses = Course.objects.all()
    assert len(data) == len(courses)
    for i, course in enumerate(courses):
        assert data[i]['name'] == course.name


@pytest.mark.django_db
def test_check_filter_id(client, user, course_factory):
    course = course_factory(_quantity=12)
    filter_id = course[10].id
    response = client.get(f'/courses/?id={filter_id}')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == filter_id


@pytest.mark.django_db
def test_check_filter_name(client, user, course_factory):
    course_create = course_factory(_quantity=20)
    course_name = course_create[15].name
    count = Course.objects.filter(name=course_name).count()
    response = client.get(f'/courses/?name={course_name}')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == count
    for course in data:
        assert course_name == course['name']


@pytest.mark.django_db
def test_create_course(client, user):
    count = Course.objects.count()
    response = client.post('/courses/', data={'user': user.id, 'name': 'postgres'})
    assert response.status_code == 201
    data = response.json()
    assert Course.objects.count() == count + 1
    assert data['name'] == 'postgres'


@pytest.mark.django_db
def test_update_course(client, user, course_factory):
    course = course_factory(_quantity=30)
    id_course = course[2].pk
    response = client.put(f'/courses/{id_course}/', data={'user': user.id, 'name': 'django_db'})
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'django_db'


@pytest.mark.django_db
def test_delete_course(client, user, course_factory):
    courses = course_factory(_quantity=5)
    courses_id = courses[4].pk
    response = client.delete(f'/courses/{courses_id}/')
    assert response.status_code == 204
    assert not Course.objects.filter(id=courses_id).exists()


@pytest.mark.django_db
def test_add_student_to_course(client, course_factory, student_factory):
    course = course_factory()
    student = student_factory()

    response = client.post(f'/courses/{course.pk}/', data={'student_id': student.pk})

    assert response.status_code == 200
    assert course.students.filter(pk=student.pk).exists()
