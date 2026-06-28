import os
from datetime import datetime

def save_report(data, filename_prefix):
    if not os.path.exists('reports'):
        os.makedirs('reports')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/{filename_prefix}_{timestamp}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
        return True, f"Отчет сохранен: {filename}"
    except Exception as e:
        return False, f"Ошибка при сохранении отчета: {str(e)}"