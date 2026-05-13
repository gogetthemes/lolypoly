# Contributing Guide

## Как внести вклад в LolyPoly

Спасибо за интерес к проекту! Вот как вы можете помочь:

## Процесс внесения изменений

1. **Fork репозиторий**
   ```bash
   git clone https://github.com/YOUR_USERNAME/lolypoly.git
   cd lolypoly
   ```

2. **Создайте ветку для вашей функции**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Внесите изменения**
   - Следуйте существующему стилю кода
   - Добавьте тесты для новых функций
   - Обновите документацию если необходимо

4. **Запустите тесты**
   ```bash
   python -m pytest tests/
   ```

5. **Закоммитьте изменения**
   ```bash
   git commit -am 'Add new feature'
   ```

6. **Запушьте в вашу ветку**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Создайте Pull Request**
   - Опишите изменения
   - Ссылайтесь на связанные issues

## Стиль кода

- Следуйте PEP 8
- Используйте type hints
- Добавляйте docstrings для всех функций
- Максимум 100 символов в строке

## Тестирование

Все новые функции должны иметь тесты:

```python
def test_my_feature(db_session):
    """Test my new feature"""
    # Arrange
    # Act
    # Assert
```

## Reporting Issues

При создании issue:

1. Используйте понятный заголовок
2. Опишите ожидаемое и фактическое поведение
3. Добавьте шаги для воспроизведения
4. Укажите версию Python и OS

## Questions?

Основной контакт: themesmonsterscom@gmail.com
