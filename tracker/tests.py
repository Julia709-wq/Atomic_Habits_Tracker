from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User
from .models import Habit


class HabitTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            email='test@mail.com',
            password='test'
        )
        self.user.set_password('test')
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_create_habit(self):
        """Тест создания привычки"""
        data = {
            "action": "Сделать зарядку",
            "place": "Дома",
            "time_of_day": "08:00:00"
        }

        response = self.client.post('/api/tracker/habits/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_data = response.json()

        self.assertEqual(response_data['action'], 'Сделать зарядку')
        self.assertEqual(response_data['place'], 'Дома')
        self.assertEqual(response_data['time_of_day'], '08:00:00')
        self.assertEqual(response_data['is_pleasant'], False)
        self.assertEqual(response_data['related_habit'], None)
        self.assertEqual(response_data['reward'], '')
        self.assertEqual(response_data['period_days'], 1)
        self.assertEqual(response_data['duration_seconds'], 60)
        self.assertEqual(response_data['is_public'], False)
        self.assertEqual(response_data['owner'], 'test@mail.com')

        self.assertIn('created_at', response_data)
        self.assertIn('updated_at', response_data)
        self.assertIn('id', response_data)

        self.assertTrue(Habit.objects.filter(action='Сделать зарядку').exists())
        self.assertEqual(Habit.objects.count(), 1)


    def test_list_habits(self):
        """Тест вывода списка привычек"""
        habit = Habit.objects.create(
            owner=self.user,
            action="Сделать зарядку",
            place="Дома",
            time_of_day="08:00:00"
        )

        response = self.client.get("/api/tracker/habits/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertIn('count', response_data)
        self.assertIn('next', response_data)
        self.assertIn('previous', response_data)
        self.assertIn('results', response_data)

        self.assertEqual(response_data['count'], 1)
        self.assertEqual(len(response_data['results']), 1)
        
        habit_data = response_data['results'][0]
        self.assertEqual(habit_data['id'], habit.id)
        self.assertEqual(habit_data['action'], 'Сделать зарядку')
        self.assertEqual(habit_data['place'], 'Дома')
        self.assertEqual(habit_data['time_of_day'], '08:00:00')
        self.assertEqual(habit_data['is_pleasant'], False)
        self.assertEqual(habit_data['related_habit'], None)
        self.assertEqual(habit_data['reward'], '')
        self.assertEqual(habit_data['period_days'], 1)
        self.assertEqual(habit_data['duration_seconds'], 60)
        self.assertEqual(habit_data['is_public'], False)
        self.assertEqual(habit_data['owner'], 'test@mail.com')
        self.assertIn('created_at', habit_data)
        self.assertIn('updated_at', habit_data)


    def test_update_habit(self):
        """Тест частичного обновления привычки"""
        habit = Habit.objects.create(
            owner=self.user,
            action="Сделать зарядку",
            place="Дома",
            time_of_day="08:00:00",
            is_public=False
        )

        update_data = {
            "action": "Пробежка",
            "is_public": True
        }

        response = self.client.patch(f'/api/tracker/habits/{habit.id}/', data=update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data['action'], 'Пробежка')
        self.assertEqual(response_data['is_public'], True)
        self.assertEqual(response_data['place'], 'Дома')
        self.assertEqual(response_data['time_of_day'], '08:00:00')

        habit.refresh_from_db()
        self.assertEqual(habit.action, 'Пробежка')
        self.assertEqual(habit.is_public, True)
        self.assertEqual(habit.place, 'Дома')


    def test_delete_habit(self):
        """Тест удаления привычки"""
        habit = Habit.objects.create(
            owner=self.user,
            action="Сделать зарядку",
            place="Дома",
            time_of_day="08:00:00"
        )

        habit_id = habit.id

        response = self.client.delete(f'/api/tracker/habits/{habit.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Habit.objects.filter(id=habit_id).exists())
        self.assertEqual(Habit.objects.count(), 0)


