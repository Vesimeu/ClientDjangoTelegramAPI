from graphviz import Digraph

dot = Digraph(comment='Более Подробная Блок-Схема Сайта для Фриланс Заказов')

# Добавление узлов
dot.node('A', 'Пользовательский Ввод')
dot.node('B', 'Проверка Данных (JS)')
dot.node('C', 'Отправка Формы (AJAX)')
dot.node('D', 'Обработка Запроса (Django)')
dot.node('E1', 'Извлечение Данных')
dot.node('E2', 'Формирование Сообщения')
dot.node('F', 'Связь с Telegram Bot')
dot.node('G', 'Ответ Пользователю')
dot.node('H', 'Уведомление Фрилансера')
dot.node('I', 'Фрилансер Принимает Заказ')
dot.node('J', 'Фрилансер Отклоняет Заказ')

# Добавление связей
dot.edges(['AB', 'BC', 'CD'])
dot.edge('D', 'E1')
dot.edge('D', 'E2')
dot.edge('E1', 'F')
dot.edge('E2', 'F')
dot.edges(['FG', 'FH', 'HI', 'HJ'])

# Опциональные связи для расширенных сценариев
dot.edge('I', 'A', style='dashed')
dot.edge('J', 'A', style='dashed')

print(dot.source)
dot.render('detailed_block_diagram', view=True)
