import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# --- Загрузка данных ---
# Убедитесь, что файл real_salary.xlsx существует по этому пути
# и содержит необходимые колонки: 'year', 'Construction_adj', 'Строительство',
# 'Minearal_mining_adj', 'Добыча полезных ископаемых', 'Education_adj', 'Образование'
# с числовыми данными.
try:
    salary = pd.read_excel('/Users/d.mkhlnk/Downloads/real_salary.xlsx')
    # Проверка на наличие ключевых колонок
    required_cols = ['year', 'Construction_adj', 'Строительство',
                     'Minearal_mining_adj', 'Добыча полезных ископаемых',
                     'Education_adj', 'Образование']
    missing_cols = [col for col in required_cols if col not in salary.columns]
    if missing_cols:
        st.error(f"Ошибка: В файле отсутствуют следующие необходимые колонки: {', '.join(missing_cols)}")
        st.stop()  # Прерываем выполнение, если нет нужных данных
    # Преобразуем год в число, если он еще не числовой
    if not pd.api.types.is_numeric_dtype(salary['year']):
        salary['year'] = pd.to_numeric(salary['year'], errors='coerce')
        salary.dropna(subset=['year'], inplace=True)  # Удаляем строки, где год не преобразовался
        salary['year'] = salary['year'].astype(int)

except FileNotFoundError:
    st.error("Ошибка: Файл 'real_salary.xlsx' не найден. Пожалуйста, проверьте путь к файлу.")
    st.stop()  # Прерываем выполнение, если файл не найден
except Exception as e:
    st.error(f"Произошла ошибка при загрузке или обработке файла данных: {e}")
    st.stop()

# --- Заголовки и описание приложения ---
st.title('Динамика реальных заработных плат в России')
st.header('На данном сайте можно посмотреть динамику реальных заработных плат в Российской Федерации')

# --- Выбор пользователя ---
st.text('Выберите параметры для отображения:')
domain_options = ["Строительство", "Добыча полезных ископаемых", "Образование"]
dynamics_options = ['Номинальная', 'Реальная', 'Номинальная vs реальная']

# st.pills по умолчанию выбирает первый элемент, если index не указан явно как None
selection_sectors = st.multiselect(
    "Отрасль:",
    domain_options,
    default=[domain_options[0]] if domain_options else []  # По умолчанию выбираем первую, если список не пуст
)

# Для 'single' выбора st.radio или st.selectbox может быть более стандартным,
# но st.pills тоже подойдет. Убедимся, что он возвращает одно значение.
selection_dynamics = st.radio(  # st.radio удобнее для одного выбора
    "Тип зарплаты:",
    dynamics_options,
    index=2  # По умолчанию "Номинальная vs реальная"
)

# Словарь для сопоставления выбранной отрасли с колонками в DataFrame
all_domain_columns = {
    'Строительство': ['Construction_adj', 'Строительство'],
    'Добыча полезных ископаемых': ['Minearal_mining_adj', 'Добыча полезных ископаемых'],
    'Образование': ['Education_adj', 'Образование']
}

# --- Построение графика ---
if not selection_sectors:
    st.info("Пожалуйста, выберите хотя бы одну отрасль для отображения графика.")
else:
    vars_to_plot = []
    plot_titles_selected = []
    for sector_name in selection_sectors:
        if sector_name in all_domain_columns:
            vars_to_plot.append(all_domain_columns[sector_name])
            plot_titles_selected.append(sector_name)  # Название сектора будет заголовком подграфика
        else:
            st.warning(f"Отрасль '{sector_name}' не найдена в доступных данных и будет пропущена.")

    if not vars_to_plot:
        st.warning("Не выбрано ни одной валидной отрасли для построения графика.")
    else:
        num_rows = len(vars_to_plot)
        # Динамически изменяем высоту figsize в зависимости от количества графиков
        fig, axes_array = plt.subplots(nrows=num_rows, ncols=1, figsize=(12, 6 * num_rows), dpi=150, squeeze=False)
        # squeeze=False гарантирует, что axes_array всегда будет 2D (например, [[ax1], [ax2]]),
        # даже если num_rows=1 (будет [[ax1]]).
        flat_axes = axes_array.flatten()  # Превращаем в 1D массив для удобной итерации [ax1, ax2, ...]

        for i, (var_adj, var_nom) in enumerate(vars_to_plot):
            current_ax = flat_axes[i]
            sector_title = plot_titles_selected[i]

            # Проверяем, существуют ли колонки в DataFrame
            columns_exist = True
            if var_adj not in salary.columns:
                st.warning(f"Колонка для реальной зарплаты '{var_adj}' не найдена для сектора '{sector_title}'.")
                columns_exist = False
            if var_nom not in salary.columns:
                st.warning(f"Колонка для номинальной зарплаты '{var_nom}' не найдена для сектора '{sector_title}'.")
                columns_exist = False

            if not columns_exist:
                current_ax.text(0.5, 0.5, 'Данные отсутствуют', horizontalalignment='center',
                                verticalalignment='center', transform=current_ax.transAxes)
                current_ax.set_title(f"{sector_title}\n(ошибка данных)")
                continue  # Переходим к следующему сектору, если нет данных

            # Логика отрисовки в зависимости от выбора selection_dynamics
            if selection_dynamics == 'Реальная':
                sns.lineplot(data=salary, x='year', y=var_adj, ax=current_ax, label='Реальная зарплата', marker='o',
                             markersize=6)
            elif selection_dynamics == 'Номинальная':
                sns.lineplot(data=salary, x='year', y=var_nom, ax=current_ax, label='Номинальная зарплата', marker='s',
                             markersize=6, linestyle='--')
            elif selection_dynamics == 'Номинальная vs реальная':
                sns.lineplot(data=salary, x='year', y=var_adj, ax=current_ax, label='Реальная зарплата', marker='o',
                             markersize=6)
                sns.lineplot(data=salary, x='year', y=var_nom, ax=current_ax, label='Номинальная зарплата', marker='s',
                             markersize=6, linestyle='--')

            current_ax.set_ylabel('Рубль')
            current_ax.set_xlabel('Год')
            current_ax.set_title(sector_title, fontsize=14)

            # Динамические метки на оси X
            min_year = salary['year'].min()
            max_year = salary['year'].max()
            # Показываем каждый год, если их не слишком много, иначе каждый второй или более
            if (max_year - min_year + 1) <= 15:
                tick_step = 1
            elif (max_year - min_year + 1) <= 30:
                tick_step = 2
            else:
                tick_step = max(1, (max_year - min_year + 1) // 15)  # Примерно 15 меток

            current_ax.set_xticks(np.arange(min_year, max_year + 1, tick_step))
            current_ax.grid(True, linestyle=':', alpha=0.7)
            current_ax.tick_params(axis='x', rotation=45, labelsize=10)
            current_ax.tick_params(axis='y', labelsize=10)
            if 2016 >= min_year and 2016 <= max_year:  # Рисуем линию, только если 2016 год в диапазоне данных
                current_ax.axvline(2016, color='red', linestyle='--', linewidth=1.5, label='База CPI (2016)')
            current_ax.legend(fontsize=10)

        fig.suptitle('Динамика заработных плат по выбранным секторам', fontsize=18, y=1.0)  # y=1.0 чтобы было чуть выше
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # Оставляем место для suptitle

        st.subheader('Графики динамики зарплат')
        if 'Реальная' in selection_dynamics or 'Номинальная vs реальная' in selection_dynamics:
            st.caption('База сравнения для реальных зарплат - 2016 год (CPI 2016 = 1).')
        st.pyplot(fig)