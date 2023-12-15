# BlenderHQ Double precision float property group utility module.
# Copyright (C) 2023 Ivan Perevala (ivpe)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import math
from bpy.props import FloatProperty


__all__ = (
    "double_property",
    "double_array",
)


def double_property(attr_name, **kwargs):
    # Значення за замовчуванням (0)
    arg_default = float(kwargs.get('default', 0.0))

    # Методи отримання і встановлення значення надані як ключові аргументи. Вони надають значення з одинарною точністю.
    cb_get = kwargs.pop('get', None)
    cb_set = kwargs.pop('set', None)

    def _get_accessor_value(self):
        # Отримуємо значення з подвійною точністю, викликаючи метод отримання властивості (див. _get_prop_value нижче)
        # В такий спосіб значення з подвійною точністю буде оновлено якщо фактичні дані (отримані через метод отримання
        # наданий як ключовий аргумент) відрізняються від раніше збережених.
        #
        # Тобто тут ми звертаємося не до item['value'] а до item.value.
        return getattr(self, attr_name, arg_default)

    def _set_accessor_value(self, new_value: str | float):
        # Оновлюємо значення з подвійною точністю, викликаючи метод _set_prop_value властивості.
        setattr(self, attr_name, new_value)

    # Оновлюємо ключові аргументи для отримання і встановлення властивості блоку даних.
    kwargs['get'] = _get_accessor_value
    kwargs['set'] = _set_accessor_value

    def _get_prop_value(self) -> float:
        # Якщо значення з подвійною точністю вже встановлено раніше і присутнє в блоці даних, отримуємо його, інакше
        # беремо значення за замовчуванням.
        if attr_name in self:
            val = self.__getitem__(attr_name)
        else:
            val = arg_default

        # Якщо надано метод для отримання поточних даних з одинарною точністю:
        if cb_get is not None:
            # 1. Викликаємо його і отримуємо актуальні дані
            existing_value = cb_get(self)
            # 2. Порівнюємо їх зі збереженими раніше даними з подвійною точністю
            if not math.isclose(val, existing_value, rel_tol=1e-5, abs_tol=1e-9):
                # 3. Якщо вони відрізняються це означає що збережені дані більше не актуальні, тому оновлюємо їх до
                # актуальних.
                self.__setitem__(attr_name, existing_value)
                val = existing_value

        return val

    def _set_prop_value(self, new_value: float):
        # Якщо нове значення є рядком, конвертуємо його в дріб.
        if isinstance(new_value, str):
            try:
                new_value = float(new_value)
            except ValueError:
                pass

        # Оновлюємо значення блоку даних з подвійною точністю
        self.__setitem__(attr_name, new_value)

        # Якщо надано метод оновлення даних то викликаємо його з оновленими значеннями (оновлюємо дані Blender)
        if cb_set is not None:
            cb_set(self, new_value)

    return property(fget=_get_prop_value, fset=_set_prop_value), FloatProperty(**kwargs)


def double_array(attr_name: str, **kwargs):
    import numpy as np
    # Розміри масиву
    arg_size = kwargs.get("size")
    # Значення за замовчуванням (масив з нулів)
    arg_default = kwargs.get('default', np.zeros(shape=arg_size, dtype=np.float64, order='C'))

    # Методи отримання і встановлення значення надані як ключові аргументи. Вони надають значення з одинарною точністю.
    cb_get = kwargs.pop('get', None)
    cb_set = kwargs.pop('set', None)

    def _get_prop_value(self) -> float:
        # Якщо значення з подвійною точністю вже встановлено раніше і присутнє в блоці даних, отримуємо його, інакше
        # беремо значення за замовчуванням.
        if attr_name in self:
            val = self.__getitem__(attr_name)
        else:
            val = arg_default

        # Беремо значення як масив без копіювання
        val = np.array(val, dtype=np.float64, copy=False, order='C').reshape(arg_size)

        # Якщо надано метод для отримання поточних даних з одинарною точністю:
        if cb_get is not None:
            # 1. Викликаємо його і отримуємо актуальні дані
            existing_arr = np.array(cb_get(self), copy=False, order='C').reshape(arg_size)
            # 2. Порівнюємо їх зі збереженими раніше даними з подвійною точністю
            if not np.allclose(val, existing_arr, rtol=1e-5, atol=1e-9):
                # 3. Якщо вони відрізняються це означає що збережені дані більше не актуальні, тому оновлюємо їх до
                # актуальних.
                self.__setitem__(attr_name, existing_arr)
                val = existing_arr

        return val

    def _set_prop_value(self, new_value: tuple[str | float]):
        # Створюємо масив з наданих даних
        val = np.array(new_value, dtype=np.float64, copy=False)

        # Оновлюємо значення блоку даних з подвійною точністю
        self.__setitem__(attr_name, val)

        # Якщо надано метод оновлення даних то викликаємо його з оновленими значеннями (оновлюємо дані Blender)
        if cb_set is not None:
            cb_set(self, val)

    return property(fget=_get_prop_value, fset=_set_prop_value)
